"""Busca ativa — a cada 3 dias, atrás do edital que o indício anuncia.

Regra do titular: a base do Eldorado é levantamento MÍNIMO. Quando existe
indício de edital em aberto (publicado) ou provável (modo preditivo), o
sistema apura ONDE esse edital é publicado — secretaria, ministério ou fundo
especializado — analisando o nível (municipal, estadual, federal) e a área, e
vai buscá-lo ativamente **a cada 3 dias** enquanto durar a janela.

Duas frentes por rodada, na ordem do mais barato para o mais caro:
  1. determinística — abre as páginas dos órgãos mapeados em
     `config/locais_publicacao.json` e procura links que casem com o indício;
  2. IA — só quando a busca determinística não acha: UMA chamada ao modelo
     mais barato com busca na web (haiku), pedindo apenas a URL oficial do
     edital. Sem credencial, registra a pendência.

Achou → o indício ganha `url_edital` e entra na campanha de completude (que
extrai texto, datas e anexos). Não achou → tentativa registrada; a próxima é
em 3 dias. Nada é inventado: URL só entra depois de aberta e confirmada.
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from .nucleo import ROOT, load_json, now_iso, sha256, validate_public_https, write_json

CFG = ROOT / "config/locais_publicacao.json"
ESTADO = ROOT / "estado/busca_ativa.json"
CFG_IA = ROOT / "config/ia.json"


def _cfg() -> dict:
    return load_json(CFG)


def _urls_de_fontes(ids: list[str]) -> list[str]:
    urls = []
    for arq, chave in (("config/fontes.json", "fontes"), ("config/conselhos.json", "conselhos")):
        p = ROOT / arq
        if not p.exists():
            continue
        for f in load_json(p).get(chave, []):
            if f.get("id") in ids and f.get("url"):
                urls.append(f["url"])
    return urls


_F260 = ROOT / "config/fontes_captacao_260.json"
_AREA_260 = {"cultura": r"cultura", "esporte": r"esporte", "educacao": r"educa",
             "saude": r"sa[úu]de", "assistencia_social": r"assist|seguran[çc]a alimentar",
             "crianca_adolescente": r"crian|adolesc", "pessoa_idosa": r"idos",
             "meio_ambiente": r"ambiente|difus|cidadania", "emendas_parlamentares": r"emenda"}


def sites_das_260(area: str | None, nivel: str | None, uf: str | None = None) -> list[dict]:
    """Fontes do relatório de 260 que casam com área e nível — Goiás primeiro."""
    if not _F260.exists():
        return []
    fontes = load_json(_F260).get("fontes", [])
    rx = re.compile(_AREA_260.get(area or "", "$^"), re.I)
    sel = [f for f in fontes if f["sites"] and (f["nivel"] == nivel or nivel is None)
           and (rx.search(f["area"]) or rx.search(f["programa"]))]
    if uf == "GO" or nivel in ("municipal", "estadual"):
        sel.sort(key=lambda f: not f["goias"])
    return [{"id": f["id"], "programa": f["programa"], "orgao": f["orgao"],
             "sites": f["sites"], "confianca": f["confianca_site"]} for f in sel[:12]]


_SITES_HIST = ROOT / "biblioteca_alexandria/fontes/sites_historicos.json"


def paginas_historicas(uf: str | None, area: str | None, limite: int = 6) -> list[str]:
    """Páginas de onde editais históricos vieram — Goiás primeiro, sem agregadores."""
    if not _SITES_HIST.exists():
        return []
    d = load_json(_SITES_HIST)
    agreg = re.compile(r"queridodiario|pncp\.gov|compras|licitanet", re.I)
    urls = []
    for pg in d.get("paginas_goias", []) if uf == "GO" else []:
        if not agreg.search(pg["url"]):
            urls.append(pg["url"])
    for s in d.get("sites", []):
        if agreg.search(s["dominio"]):
            continue
        if (uf and s["ufs"].get(uf)) or (area and area in s["areas"]):
            urls.append(s["exemplo"])
    return list(dict.fromkeys(urls))[:limite]


def local_de_publicacao(area: str | None, nivel: str | None, uf: str | None = None) -> dict:
    """ONDE procurar: órgão (secretaria/ministério/fundo) e URLs, por área e nível.
    Combina o mapa por área, as fontes do relatório de 260 (Goiás primeiro) e as
    páginas históricas de onde editais semelhantes vieram."""
    cfg = _cfg()
    nivel = nivel if nivel in ("municipal", "estadual", "federal") else (
        "federal" if not uf else "estadual")
    das260 = sites_das_260(area, nivel, uf)
    extra = [u for f in das260 for u in f["sites"]] + paginas_historicas(uf, area)
    regra = (cfg["por_area"].get(area or "") or {}).get(nivel)
    if regra:
        urls = list(dict.fromkeys(_urls_de_fontes(regra.get("fontes", [])) + regra.get("urls", []) + extra))
        return {"orgao": regra["orgao"], "nivel": nivel, "area": area,
                "tipo": ("fundo" if "fundo" in regra["orgao"].lower() else
                         "ministerio" if "minist" in regra["orgao"].lower() else
                         "gabinete" if "gabinete" in regra["orgao"].lower() else "secretaria"),
                "urls": urls, "mapeado": True, "fontes_260": das260}
    g = cfg["generico"][nivel]
    return {"orgao": g["orgao"], "nivel": nivel, "area": area, "tipo": "generico",
            "urls": list(dict.fromkeys(g["urls"] + extra)), "mapeado": bool(extra),
            "fontes_260": das260}


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self._h = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag == "a": self._h = dict(attrs).get("href"); self._t = []
    def handle_data(self, data):
        if self._h is not None: self._t.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.links.append((self._h, " ".join(self._t).strip())); self._h = None


def _abrir(url: str, timeout: int = 25) -> tuple[str, str]:
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Eldorado-OSC/1.0 busca-ativa"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(2_500_000).decode("utf-8", "replace"), r.geturl()


def _tokens(texto: str) -> list[str]:
    return [t for t in re.findall(r"[a-zà-ú0-9]{4,}", (texto or "").lower())
            if t not in {"edital", "chamamento", "publico", "público", "chamada", "para",
                         "projetos", "projeto", "sociedade", "civil", "organizações",
                         "secretaria", "municipal", "estadual", "federal", "diário", "oficial"}]


def busca_deterministica(indicio: dict, local: dict) -> dict:
    """Abre as páginas do órgão e procura link que case com o indício."""
    tokens = _tokens(indicio.get("titulo", "") + " " + (indicio.get("objeto") or ""))[:6]
    visitadas, achados, falhas = [], [], []
    for url in local["urls"][:8]:
        try:
            html, final = _abrir(url)
        except Exception as exc:
            falhas.append({"url": url, "erro": type(exc).__name__}); continue
        visitadas.append(final)
        p = _Links(); p.feed(html)
        for href, rot in p.links:
            r = (rot or "").lower()
            if not re.search(r"edital|chamamento|chamada|sele[çc][ãa]o", r):
                continue
            casa = sum(1 for t in tokens if t in r)
            if casa >= max(1, min(2, len(tokens) - 1)):
                achados.append({"url": urljoin(final, href), "rotulo": rot[:200],
                                "aderencia": casa, "em": final})
    achados.sort(key=lambda a: -a["aderencia"])
    return {"visitadas": visitadas, "achados": achados[:5], "falhas": falhas}


def busca_ia_escalada(indicio: dict, local: dict, alvo: list[str] | None = None) -> dict:
    """Escalada modelo a modelo: só sobe o degrau se o anterior não atingiu a
    finalidade. Registra cada degrau, seu modelo e o que rendeu."""
    import os
    if not os.environ.get("FAROL_AI_API_KEY"):
        return {"status": "aguardando credencial FAROL_AI_API_KEY", "url": None, "degraus": []}
    cfg = load_json(CFG_IA) if CFG_IA.exists() else {}
    cadeia = (cfg.get("escalada_busca") or {}).get("cadeia") or []
    degraus, url, itens = [], None, {}
    for d in cadeia:
        r = _chamar_modelo(d, indicio, local, alvo or [])
        degraus.append({"papel": d["papel"], "modelo": d["modelo"], "resultado": r.get("status"),
                        "uso": r.get("uso")})
        url = url or r.get("url")
        itens.update({k: v for k, v in (r.get("itens") or {}).items() if v})
        atingiu = bool(url) and (not alvo or all(itens.get(a) for a in alvo))
        if atingiu or d["papel"] == "analise_profunda":
            break
    return {"status": "consultado", "url": url, "itens": itens, "degraus": degraus}


def _chamar_modelo(d: dict, indicio: dict, local: dict, alvo: list[str]) -> dict:
    import os, urllib.request
    prompt = (f"Fonte: {local['orgao']} ({local['nivel']}). Finalidade: {d['finalidade']}.\n"
              f"Edital/indício: {indicio.get('titulo')}\nÁrea: {indicio.get('area')} · "
              f"Território: {indicio.get('territorio') or indicio.get('uf')}\n"
              f"Itens ainda sem dado: {', '.join(alvo) or 'URL oficial'}\n"
              "Responda SOMENTE em JSON: {\"url\": <URL oficial ou null>, \"itens\": {<item>: <valor ou null>}}. "
              "Nunca invente: sem fonte oficial, use null.")
    corpo = {"model": d["modelo"], "max_tokens": d["max_tokens"],
             "messages": [{"role": "user", "content": prompt}]}
    if d.get("web_search"):
        corpo["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(),
                                 headers={"content-type": "application/json",
                                          "x-api-key": os.environ["FAROL_AI_API_KEY"],
                                          "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dados = json.loads(r.read())
    except Exception as exc:
        return {"status": f"falha: {type(exc).__name__}"}
    texto = " ".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
    with (ROOT / "estado/ia_uso.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps({"em": now_iso(), "modelo": d["modelo"], "tarefa": d["papel"],
                            "uso": dados.get("usage", {})}, ensure_ascii=False) + "\n")
    try:
        js = json.loads(re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip())
        return {"status": "respondeu", "url": js.get("url"), "itens": js.get("itens") or {},
                "uso": dados.get("usage", {})}
    except Exception:
        m = re.search(r"https?://\S+", texto)
        return {"status": "resposta livre", "url": m.group(0).rstrip(".,)") if m else None,
                "uso": dados.get("usage", {})}


def busca_ia(indicio: dict, local: dict) -> dict:
    """Compatibilidade: primeiro degrau da escalada."""
    r = busca_ia_escalada(indicio, local)
    return {"status": r["status"], "url": r.get("url"), "degraus": r.get("degraus", [])}


def _busca_ia_antiga(indicio: dict, local: dict) -> dict:
    """Uma chamada ao modelo MAIS BARATO com busca na web — só a URL oficial."""
    import os, urllib.request
    chave = os.environ.get("FAROL_AI_API_KEY")
    if not chave:
        return {"status": "aguardando credencial FAROL_AI_API_KEY", "url": None}
    cfg = load_json(CFG_IA) if CFG_IA.exists() else {}
    spec = (cfg.get("modelos") or {}).get("busca") or {}
    modelo = (os.environ.get(spec.get("env", ""), "") if isinstance(spec, dict) else "") \
        or (spec.get("padrao") if isinstance(spec, dict) else spec) or "claude-haiku-4-5"
    prompt = (f"Localize a URL OFICIAL do edital descrito abaixo, publicado por "
              f"{local['orgao']} ({local['nivel']}). Responda SOMENTE com a URL, ou "
              f"com a palavra NENHUMA se não encontrar em fonte oficial.\n\n"
              f"Título: {indicio.get('titulo')}\nÁrea: {indicio.get('area')}\n"
              f"Território: {indicio.get('territorio') or indicio.get('uf')}\n"
              f"Janela: {indicio.get('inicio')} a {indicio.get('fim')}")
    corpo = json.dumps({"model": modelo, "max_tokens": 200,
                        "tools": [{"type": "web_search_20250305", "name": "web_search",
                                   "max_uses": 3}],
                        "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=corpo,
                                 headers={"content-type": "application/json", "x-api-key": chave,
                                          "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            dados = json.loads(r.read())
    except Exception as exc:
        return {"status": f"falha: {type(exc).__name__}", "url": None, "modelo": modelo}
    texto = " ".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
    m = re.search(r"https?://\S+", texto)
    with (ROOT / "estado/ia_uso.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps({"em": now_iso(), "modelo": modelo, "tarefa": "busca_ativa",
                            "uso": dados.get("usage", {})}, ensure_ascii=False) + "\n")
    return {"status": "consultado", "url": m.group(0).rstrip(".,)") if m else None,
            "modelo": modelo, "resposta": texto[:200]}


def _pendentes_da_fase2(limite: int = 200) -> list[dict]:
    """Editais que já têm sensor e URL mas ainda não alcançaram a totalidade.

    Ordem de ataque: quem está a UM item do mínimo (prazo+objeto) primeiro —
    é o degrau que transforma registro em decisão. Depois, quem já tem o
    mínimo e falta detalhe."""
    try:
        from .banco import conectar
        con = conectar()
        linhas = con.execute(
            "SELECT chave, ano, id, ficha FROM historico "
            "WHERE url IS NOT NULL ORDER BY (uf='GO') DESC, data_publicacao DESC "
            "LIMIT 4000").fetchall()
        con.close()
    except Exception:
        return []
    fila = []
    for chave, ano, cid, fj in linhas:
        f = json.loads(fj)
        c = f.get("confirmacao") or {}
        if not c or c.get("nivel_confirmacao") == "completo":
            continue
        peso = {"minimo_util": 1, "confirmado_documental": 2,
                "parcial": 0, "pendente": 3}.get(c.get("nivel_confirmacao"), 3)
        fila.append({"id": cid, "titulo": f.get("titulo"), "area": f.get("area"),
                     "nivel": f.get("nivel"), "uf": f.get("uf"),
                     "territorio": f.get("territorio"), "inicio": f.get("inicio"),
                     "fim": f.get("fim"), "objeto": f.get("objeto"), "url": f.get("url"),
                     "origem": "fase2_incompleta", "peso": peso,
                     "alvo": c.get("proximo_alvo") or [],
                     "chave": chave, "ano_ref": ano})
    fila.sort(key=lambda x: (x["peso"], not (x["uf"] == "GO")))
    return fila[:limite]


def _indicios(hoje: date) -> list[dict]:
    """Editais em aberto/por abrir ainda incompletos + previsões a até 60 dias."""
    saida = []
    dj = ROOT / "docs/dashboard-dados.json"
    if dj.exists():
        d = load_json(dj)
        for e in d.get("editais", []):
            if e.get("sem_edital") or e.get("acervo") == "historico":
                continue
            if e.get("estado_export") in ("aberto", "a_abrir") and (e.get("etapa") or 1) < 2:
                saida.append({**{k: e.get(k) for k in ("id", "titulo", "area", "nivel", "uf",
                                                       "territorio", "inicio", "fim", "objeto", "url")},
                              "origem": "indicio_publicado"})
    saida += _pendentes_da_fase2()
    pj = ROOT / "biblioteca_alexandria/previsoes/previsoes.json"
    if pj.exists():
        lim = (hoje + timedelta(days=60)).isoformat()
        for p in load_json(pj).get("itens", []):
            if p["inicio"] <= lim and p["fim"] >= hoje.isoformat():
                saida.append({**{k: p.get(k) for k in ("id", "titulo", "area", "nivel", "uf",
                                                       "inicio", "fim")},
                              "territorio": p.get("uf"), "objeto": None, "url": None,
                              "origem": "previsao"})
    return saida


def run(hoje: date | None = None, limite: int = 60, usar_ia: bool = True) -> dict:
    hoje = hoje or date.today()
    cad = _cfg().get("cadencia_dias", 3)
    est = load_json(ESTADO) if ESTADO.exists() else {"itens": {}}
    itens = est["itens"]
    processados, achados, pend_ia = 0, 0, 0
    for ind in _indicios(hoje)[:limite * 3]:
        reg = itens.setdefault(ind["id"], {"criado_em": hoje.isoformat(), "tentativas": []})
        if reg.get("url_edital") or reg.get("parado"):
            continue
        ultima = reg["tentativas"][-1]["data"] if reg["tentativas"] else None
        if ultima and (hoje - date.fromisoformat(ultima)).days < cad:
            continue
        if processados >= limite:
            break
        local = local_de_publicacao(ind.get("area"), ind.get("nivel"), ind.get("uf"))
        det = busca_deterministica(ind, local)
        tentativa = {"data": hoje.isoformat(), "local": {k: local[k] for k in
                     ("orgao", "nivel", "tipo", "mapeado")}, "urls_visitadas": det["visitadas"],
                     "achados": det["achados"], "falhas": det["falhas"]}
        url = det["achados"][0]["url"] if det["achados"] else None
        if not url and usar_ia:
            ia = busca_ia_escalada(ind, local, ind.get("alvo"))
            tentativa["ia"] = {k: ia.get(k) for k in ("status", "url", "degraus")}
            url = ia.get("url")
            if ia.get("itens"):
                reg["itens_obtidos_por_ia"] = {**reg.get("itens_obtidos_por_ia", {}), **ia["itens"]}
            if "credencial" in (ia.get("status") or ""):
                pend_ia += 1
        # PARADA: três leituras seguidas dos locais oficiais sem nenhum dado novo
        sem_novo = not det["achados"] and not (tentativa.get("ia") or {}).get("url")
        reg["sem_novidade_seguidas"] = (reg.get("sem_novidade_seguidas", 0) + 1) if sem_novo else 0
        if reg["sem_novidade_seguidas"] >= 3 and not reg.get("url_edital"):
            reg["parado"] = {"em": now_iso(), "motivo": "três leituras seguidas sem dado novo nos locais oficiais",
                             "retomar_quando": "a previsão apontar nova janela ou o titular pedir"}
        if url:
            reg["url_edital"] = url
            reg["encontrado_em"] = now_iso()
            reg["proximo_passo"] = "campanha de completude (texto, datas, anexos)"
            achados += 1
        reg["origem"] = ind["origem"]; reg["titulo"] = ind.get("titulo")
        reg["local_publicacao"] = local["orgao"]
        reg["tentativas"].append(tentativa)
        processados += 1
    est["atualizado_em"] = now_iso()
    write_json(ESTADO, est)
    return {"executado_em": now_iso(), "cadencia_dias": cad, "processados": processados,
            "encontrados": achados, "aguardando_credencial_ia": pend_ia,
            "em_acompanhamento": sum(1 for r in itens.values() if not r.get("url_edital")),
            "nota": ("busca determinística primeiro; IA (modelo mais barato, busca na web) "
                     "só quando necessário; URL só entra depois de aberta e confirmada")}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
