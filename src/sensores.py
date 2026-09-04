"""Esquadra de sensores — um por fonte, independentes e coordenados.

Doutrina do titular: cada fonte de recurso tem seu próprio sensor, que sabe
tudo sobre ela — passado (dossiê), presente (última leitura) e futuro
(previsão). Diários oficiais, Diário da Justiça, legislativos e APIs rodam
todos os dias; sites de fonte rodam em rodízio por dia da semana; quando há
previsão de edital para a fonte no mês, o sensor passa a rodar diariamente.

Como fica leve:
  · um único arquivo de estado para toda a esquadra (`estado/esquadra.json`),
    compacto; nenhum sensor cria arquivo próprio;
  · o léxico é compilado uma vez e compartilhado; zero IA na triagem;
  · cada sensor lê no máximo 3 páginas e 60 links por página, com pausa;
  · achados entram na base JSONL deduplicados por URL canônica; o restante
    é contagem.
  · a IA (modelo mais barato) só é chamada pela busca ativa, e só quando a
    leitura determinística não acha.

Executar: `python -m src.sensores` (o coordenador decide quem sai hoje).
"""
from __future__ import annotations

import json
import re
import time
import zlib
from datetime import date, timedelta
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, urlsplit

from .destinacao import avaliar_destinacao
from .lexico import casar
from .nucleo import (ROOT, append_jsonl, canonical_url, carregar_oportunidades, load_json,
                     now_iso, sha256, validate_public_https, write_json)

CFG = ROOT / "config/sensores.json"
F260 = ROOT / "config/fontes_captacao_260.json"
INVEST = ROOT / "config/investigacao.json"
PREV = ROOT / "biblioteca_alexandria/previsoes/previsoes.json"
ESTADO = ROOT / "estado/esquadra.json"
DIARIO = ROOT / "estado/esquadra_diario.json"        # 30 dias por sensor: cor + trecho
ATIVACAO = ROOT / "estado/ativacao_fontes.json"      # fontes específicas ativas hoje (época/menção)


def cor_do_dia(r: dict) -> str:
    """cinza: não executado · vermelho: falha/inoperante · azul: funcionou sem
    oportunidade · amarelo: achou, mas faltam camadas · verde: 11 camadas."""
    if r.get("falhas") and not r.get("saude"):
        return "vermelho"
    if not r.get("achados"):
        return "azul"
    if any((a.get("confirmacao") or {}).get("nivel_confirmacao") == "completo" for a in r["achados"]):
        return "verde"
    return "amarelo"


def registrar_dia(sensor_id: str, hoje: date, r: dict) -> None:
    d = load_json(DIARIO) if DIARIO.exists() else {"sensores": {}}
    s = d["sensores"].setdefault(sensor_id, {})
    melhor = max(r.get("achados") or [], key=lambda a: a.get("forca_lexica", 0), default=None)
    s[hoje.isoformat()] = {
        "cor": cor_do_dia(r), "achados": len(r.get("achados") or []),
        "falhas": len(r.get("falhas") or []),
        "http": ((r.get("saude") or [{}])[0]).get("http"),
        "trecho": ((melhor or {}).get("titulo") or "")[:160] if melhor else None,
        "url": (melhor or {}).get("url"),
    }
    # janela móvel: só os últimos 45 dias ficam
    corte = (hoje - timedelta(days=45)).isoformat()
    for k in [k for k in s if k < corte]:
        del s[k]
    d["atualizado_em"] = now_iso()
    write_json(DIARIO, d)
DB = ROOT / "dados/oportunidades/oportunidades.jsonl"

_FIM = re.compile(r"(?:at[ée]|prazo|encerra\w*|inscri[çc][õo]es[^.]{0,30}?at[ée])\D{0,25}(\d{1,2}/\d{1,2}/20\d{2})", re.I)
_VALOR = re.compile(r"R\$\s?[\d.]{1,12},\d{2}|R\$\s?[\d.]{3,12}", re.I)
_AGREG = re.compile(r"queridodiario|pncp\.gov|compras|licitanet", re.I)


# ------------------------------------------------------------------ registro
def registro() -> list[dict]:
    """Toda a esquadra: especiais + um sensor por fonte das 260 + portais."""
    cfg = load_json(CFG)
    sens = [dict(s, origem="especial") for s in cfg["sensores_especiais"]]
    vistos = {u for s in sens for u in s["urls"]}
    por_url: dict[str, dict] = {}
    if F260.exists():
        for f in load_json(F260).get("fontes", []):
            if f["confianca_site"] == "pendente":
                continue
            urls = [u for u in f["sites"] if u not in vistos and not _AGREG.search(u)]
            if not urls:
                # site já coberto por outro motor: este ponto passa a ser atendido por ele
                for u in f["sites"]:
                    if u in por_url:
                        por_url[u].setdefault("fontes_260", []).append(f["id"])
                        break
                continue
            vistos.update(urls)
            tipo = {"internacional": "internacional", "privada": "privada"}.get(
                f["nivel"], "site_oficial")
            s = {"id": f"f260-{f['id']}", "nome": f["programa"], "tipo": tipo,
                 "nivel": f["nivel"], "uf": f.get("uf"), "territorio": f.get("uf") or "BR",
                 "urls": urls[:2], "busca": None, "confianca": f["confianca_site"],
                 "orgao": f.get("orgao"), "area": f.get("area"), "goias": f.get("goias"),
                 "fonte_260": f["id"], "fontes_260": [f["id"]], "origem": "fontes_260"}
            sens.append(s)
            for u in urls:
                por_url[u] = s
    if INVEST.exists():
        for p in load_json(INVEST).get("fontes", []):
            if p.get("url") in vistos or not p.get("ativa", True):
                continue
            vistos.add(p["url"])
            sens.append({"id": f"plat-{p['id']}", "nome": p["nome"], "tipo": "plataforma",
                         "nivel": "privada", "uf": None, "territorio": p.get("territorio", "BR"),
                         "urls": [p["url"]], "busca": None, "confianca": "confirmada",
                         "origem": "investigacao"})
    return sens


def _previsoes_ativas(hoje: date) -> set[str]:
    """Órgãos com previsão de edital no mês corrente → sensor escala para diário."""
    if not PREV.exists():
        return set()
    mes = hoje.isoformat()[:7]
    ativos = set()
    for p in load_json(PREV).get("itens", []):
        if p["inicio"][:7] <= mes <= p["fim"][:7]:
            ativos.add(re.sub(r"\W+", " ", (p.get("orgao") or "").lower()).strip())
    return ativos


def _casa_previsao(sensor: dict, ativos: set[str]) -> bool:
    alvo = re.sub(r"\W+", " ", f'{sensor.get("orgao") or ""} {sensor["nome"]}'.lower())
    toks = [t for t in alvo.split() if len(t) > 4]
    return any(sum(1 for t in toks if t in a) >= 2 for a in ativos) if toks else False


def escala_do_dia(hoje: date | None = None) -> dict:
    """Quem sai hoje: diários/justiça/legislativo/API sempre; sites em rodízio
    por dia da semana; escalada para diário quando há previsão no mês."""
    hoje = hoje or date.today()
    cfg = load_json(CFG)
    diarios = set(cfg["cadencia"]["diaria"])
    ativos = _previsoes_ativas(hoje)
    # motores desligados pelo titular no painel (tonel azul) não saem
    ma = ROOT / "config/motores_ativos.json"
    desligados = set(load_json(ma).get("inativos", [])) if ma.exists() else set()
    dia = hoje.weekday()
    saem, ficam = [], []
    ativas = set((load_json(ATIVACAO).get("ativas") or {}).keys()) if ATIVACAO.exists() else set()
    for s in registro():
        motivo = None
        if s["id"] in desligados or desligados & set(s.get("fontes_260") or []):
            ficam.append(dict(s, desligado_pelo_titular=True)); continue
        if s["tipo"] in diarios or s["tipo"] == "plataforma":
            motivo = "motor regular e geral — todo dia"
        elif s.get("fontes_260") and (set(s["fontes_260"]) & ativas):
            motivo = "fonte específica ATIVA: época prevista ou menção em local oficial"
        elif cfg["cadencia"].get("escalada_por_previsao") and _casa_previsao(s, ativos):
            motivo = "escalada: previsão de edital neste mês"
        elif not s.get("fontes_260") and zlib.crc32(s["id"].encode()) % 7 == dia:
            motivo = f"rodízio semanal (dia {dia})"
        (saem if motivo else ficam).append({**s, "motivo": motivo} if motivo else s)
    lim = cfg["limites"]["sensores_por_execucao"]
    saem.sort(key=lambda s: (s["tipo"] not in diarios, not s.get("goias"), s["id"]))   # diários e Goiás primeiro
    return {"data": hoje.isoformat(), "saem": saem[:lim], "ficam": len(ficam) + max(0, len(saem) - lim),
            "total": len(saem) + len(ficam), "previsoes_ativas": len(ativos)}


# ------------------------------------------------------------------- leitura
class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.texto = []; self._h = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag == "a": self._h = dict(attrs).get("href"); self._t = []
    def handle_data(self, data):
        self.texto.append(data)
        if self._h is not None: self._t.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None:
            self.links.append((self._h, " ".join(self._t).strip())); self._h = None


def _abrir(url: str, timeout: int = 12, max_bytes: int = 2_500_000) -> tuple[str, str, int]:
    from urllib.request import Request, urlopen
    if not url.startswith("file://"):
        validate_public_https(url, urlsplit(url).hostname)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0", "From": "contato-via-repositorio", "Accept-Language": "pt-BR,pt;q=0.9",
                                "Accept": "text/html,application/rss+xml,application/json;q=0.9,*/*;q=0.5"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(max_bytes).decode("utf-8", "replace"), r.geturl(), getattr(r, "status", 200) or 200


def _paginas(sensor: dict, hoje: date | None = None) -> list[str]:
    """URLs a ler: fixas; por termo quando o portal tem busca; por DATA do dia
    quando o diário publica por edição (DOU: leiturajornal?data=DD-MM-AAAA)."""
    hoje = hoje or date.today()
    saida = []
    for u in sensor["urls"]:
        if "{data8}" in u:
            saida.append(u.replace("{data8}", hoje.strftime("%Y%m%d")))
        elif "{data}" in u:
            saida.append(u.replace("{data}", hoje.strftime("%d-%m-%Y")))
        elif "{termo}" in u:
            saida += [u.replace("{termo}", quote(t)) for t in sensor.get("termos_busca", [])[:4]]
        else:
            saida.append(u)
    return saida


_LEX_ESP: dict = {}
def lexico_especifico(sensor: dict) -> list[str]:
    """2ª etapa (Motores Opressores): termos ESPECÍFICOS do recurso — o léxico
    próprio do regramento quando existe, senão os termos distintivos do
    programa. Casam de forma cirúrgica, onde o léxico geral seria vago."""
    if not sensor.get("fontes_260"):
        return []
    genericos = {"edital", "editais", "projeto", "projetos", "apoio", "cultura", "cultural", "esporte", "fomento",
                 "programa", "municipal", "estadual", "federal", "goiás", "goiania", "goiânia", "secretaria",
                 "destinação", "destinacao", "doação", "doacao", "incentivo", "fiscal", "nacional", "estado",
                 "recursos", "captação", "entidades", "social", "sociais", "pessoa", "física", "fisica", "jurídica"}
    if not _LEX_ESP:
        rg = ROOT / "config/regramentos.json"
        if rg.exists():
            for r in load_json(rg).get("regramentos", []):
                toks = {t for t in re.findall(r"[a-zà-ú]{5,}", r["fonte"].lower()) if t not in genericos}
                _LEX_ESP[r["id"]] = {"toks": toks, "lex": r.get("lexico_proprio", [])}
    nome = (sensor.get("nome") or "").lower()
    ntoks = {t for t in re.findall(r"[a-zà-ú]{5,}", nome) if t not in genericos}
    # UM regramento só: o de maior sobreposição de termos distintivos (mín. 1 termo forte)
    melhor, nota = None, 0
    for rid, r in _LEX_ESP.items():
        n = len(ntoks & r["toks"])
        if n > nota:
            melhor, nota = r, n
    termos = list(melhor["lex"]) if melhor else []
    termos += sorted(ntoks)
    return sorted(set(termos))[:24]


def casa_especifico(texto: str, termos: list[str]) -> list[str]:
    tl = texto.lower()
    return [t for t in termos if t.lower() in tl]


def ler(sensor: dict, limites: dict | None = None, pausa: float | None = None) -> dict:
    """Uma leitura do sensor: páginas → links → léxico → destinação → achados.
    Motores Opressores (fontes_260) também casam pelo léxico ESPECÍFICO."""
    lim = limites or load_json(CFG)["limites"]
    pausa = lim["pausa_segundos"] if pausa is None else pausa
    achados, falhas, saude = [], [], []
    especifico = lexico_especifico(sensor)
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None}
    fila = list(_paginas(sensor)[:lim["paginas_por_sensor"]])
    lidas: set = set()
    while fila and diag["paginas_lidas"] < lim["paginas_por_sensor"] + 4:
        url = fila.pop(0)
        if url in lidas:
            continue
        lidas.add(url)
        try:
            tmo = lim.get("timeout_segundos", 12) if sensor.get("tipo") != "api" else max(30, lim.get("timeout_segundos", 12))
            html, final, status = _abrir(url, timeout=tmo, max_bytes=lim["bytes_por_pagina"])
            saude.append({"url": url, "http": status, "bytes": len(html)}); diag["paginas_lidas"] += 1
        except Exception as exc:
            falhas.append({"url": url, "erro": type(exc).__name__})
            try:
                from .alternativas import registrar_bloqueio
                registrar_bloqueio(url, type(exc).__name__, sensor.get("nome", ""))
            except Exception:
                pass
            continue
        p = _Links()
        # API JSON (PNCP): itens viram links para a página pública do edital
        if html.lstrip().startswith(("{", "[")) and "pncp" in url:
            try:
                js = json.loads(html); itens = js.get("data") if isinstance(js, dict) else js
                for it in (itens or [])[:200]:
                    org = (it.get("orgaoEntidade") or {}); cnpj = re.sub(r"\D", "", str(org.get("cnpj") or ""))
                    ano = it.get("anoCompra"); seq = it.get("sequencialCompra")
                    rot = f"{it.get('modalidadeNome') or 'Chamamento'} — {org.get('razaoSocial') or ''} — {(it.get('objetoCompra') or '')[:220]}"
                    link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if cnpj and ano and seq else it.get("linkSistemaOrigem") or url
                    p.links.append((link, rot)); p.texto.append(" " + rot + f" · encerramento {it.get('dataEncerramentoProposta') or ''} · UF {((it.get('unidadeOrgao') or {}).get('ufSigla') or '')} ")
            except Exception:
                pass
        else:
            p.feed(html)
        # DOU (leiturajornal): as matérias do dia vêm num JSON embutido, não em <a>;
        # cada matéria vira um link para a íntegra em /web/dou/-/<urlTitle>
        mj = re.search(r'<script[^>]*id="params"[^>]*>(.*?)</script>', html, re.S)
        if "in.gov.br" in url:
            diag["dou_json_encontrado"] = bool(mj)
        if mj and "in.gov.br" in url:
            try:
                dados_dou = json.loads(mj.group(1))
                diag["dou_json_materias"] = len(dados_dou.get("jsonArray") or [])
                for mat in (dados_dou.get("jsonArray") or [])[:600]:
                    tit = (mat.get("title") or "").strip(); slug_ = mat.get("urlTitle")
                    if tit and slug_:
                        p.links.append((f"https://www.in.gov.br/web/dou/-/{slug_}", tit))
                        p.texto.append(" " + tit + " " + (mat.get("content") or "")[:300] + " ")
            except Exception:
                pass
        corpo = re.sub(r"\s+", " ", " ".join(p.texto))
        diag["links_total"] += len(p.links)
        diag["pdf_links"] += sum(1 for h, _ in p.links if h and h.lower().endswith(".pdf"))
        # DESCOBERTA DA LISTAGEM: se a página não traz editais mas aponta para
        # 'editais / licitações / chamamentos / edições / diário / publicações',
        # segue esses links (até 4) — a home costuma ser só institucional
        if url in _paginas(sensor)[:lim["paginas_por_sensor"]] and len(diag["descobertas"]) < 4:
            for h, r in p.links:
                rl = (r or "").lower(); hl = (h or "").lower()
                if h and re.search(r"edita|licita|chamament|credenciament|edi[çc][õo]es|di[áa]rio|publica[çc][õo]es|transpar[êe]ncia|jornal|ver todas|mais not", rl + " " + hl) \
                        and not re.search(r"\.(jpg|png|css|js)$|mailto:|javascript:|#$", hl):
                    u2 = canonical_url(urljoin(final, h))
                    if urlsplit(u2).scheme in ("https", "file") and u2 not in lidas and u2 not in fila and len(diag["descobertas"]) < 4:
                        fila.append(u2); diag["descobertas"].append({"de": url, "para": u2, "rotulo": (r or "")[:60]})
        for href, rot in p.links[:lim["links_por_pagina"] * 3]:
            if not rot or len(rot) < 10:
                continue
            diag["links_candidatos"] += 1
            lx = casar(rot)
            esp = casa_especifico(rot, especifico) if especifico else []
            if not lx["candidato"] and not esp:
                continue
            lx["termos"]["especificos"] = esp
            u = canonical_url(urljoin(final, href))
            if urlsplit(u).scheme not in ("https", "file"):
                continue
            # contexto: o rótulo e o que vem DEPOIS dele, até o próximo item —
            # olhar para trás fazia um item herdar prazo/valor do vizinho
            i = corpo.find(rot[:40])
            ctx = corpo[i: i + 320] if i >= 0 else rot
            prox = ctx.find(" ", len(rot) + 1)
            nxt = re.search(r"(?:Resolu[çc][ãa]o|Edital|Projeto de Lei|Preg[ãa]o|Aviso|Portaria)\s+(?:n[ºo]|d[ao])",
                            ctx[len(rot):])
            if nxt:
                ctx = ctx[: len(rot) + nxt.start()]
            dest = avaliar_destinacao({"titulo": rot, "evidencia": ctx, "fonte_id": sensor["id"]})
            if not dest["elegivel"]:
                continue
            from .pertinencia import pertinente as _pert
            if not _pert({"titulo": rot, "evidencia": ctx})["ok"]:
                continue
            fim = _FIM.search(ctx); val = _VALOR.search(ctx)
            achados.append({
                "id": sha256(("sens|" + u).encode())[:20], "status": "capturada",
                "titulo": rot[:300], "url": u, "fonte_id": sensor["id"],
                "fonte_nome": sensor["nome"], "territorio": sensor.get("territorio") or "BR",
                "uf": sensor.get("uf"), "nivel": sensor.get("nivel"),
                "tipo_fonte": f"sensor_{sensor['tipo']}", "confianca": "primaria"
                if sensor["tipo"] in ("diario_oficial", "api", "site_oficial") else "secundaria",
                "coletado_em": now_iso(), "prazo_texto": fim.group(1) if fim else None,
                "valor_texto": val.group(0) if val else None,
                "evidencia": ctx[:500], "hash_evidencia": sha256(ctx.encode()),
                "lexico": lx["termos"], "forca_lexica": lx["forca"],
                "destinacao": dest, "sensor": sensor["id"],
            })
            if len(achados) >= lim["links_por_pagina"]:
                break
        if pausa: time.sleep(pausa)
    unicos = {a["id"]: a for a in achados}
    # DIAGNÓSTICO INDIVIDUAL — por que este motor rendeu (ou não)
    if not unicos:
        if saude and not falhas:
            if diag["links_total"] == 0 and diag["pdf_links"] == 0:
                diag["motivo_zero"] = "página respondeu mas não tem links (conteúdo carregado por script ou vazio) — precisa de API/RSS ou leitura do HTML renderizado"
            elif diag["pdf_links"] and diag["links_candidatos"] < 5:
                diag["motivo_zero"] = "os editais estão dentro de PDFs (edições inteiras) — a leitura do rótulo não alcança; entra a extração de edição"
            elif diag["descobertas"]:
                diag["motivo_zero"] = f"página institucional; seguiu {len(diag['descobertas'])} listagem(ns) e nenhum rótulo casou com o léxico do terceiro setor hoje"
            else:
                diag["motivo_zero"] = "página respondeu com links, mas nenhum rótulo casou com o léxico do terceiro setor hoje — pode não haver edital publicado"
        elif falhas and not saude:
            erros = {f["erro"] for f in falhas}
            diag["motivo_zero"] = ("endereço não resolve (DNS) — URL errada" if "gaierror" in erros else
                                   "o portal recusa acesso automatizado (HTTP 403/404) — escada de alternativas" if "HTTPError" in erros else
                                   "tempo esgotado / conexão recusada" if erros & {"timeout", "URLError", "TimeoutError"} else f"falha: {', '.join(sorted(erros))}")
        elif falhas and saude:
            diag["motivo_zero"] = "parte das páginas respondeu e parte falhou; nenhum edital reconhecido nas que responderam"
    return {"sensor": sensor["id"], "achados": list(unicos.values()),
            "falhas": falhas, "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


# --------------------------------------------------------------- coordenador
def run(hoje: date | None = None, limite: int | None = None, pausa: float | None = None) -> dict:
    hoje = hoje or date.today()
    escala = escala_do_dia(hoje)
    # ATIVAÇÃO MANUAL: o titular seleciona pontos no painel e o workflow recebe
    # os ids em MOTORES_FONTES — só esses motores saem, fora da escala
    import os
    pedidos = {x.strip() for x in os.environ.get("MOTORES_FONTES", "").split(",") if x.strip()}
    # BLOCO DA HORA (config/horarios.json): 00h diários · 01h justiça/legislativo ·
    # 02h plataformas/API · 04h Motores Opressores ativos. Fora do bloco, o motor
    # espera a sua hora — nada de sobrecarga.
    bloco = os.environ.get("MOTORES_BLOCO", "completo")
    hz = ROOT / "config/horarios.json"
    tipos_bloco = None
    if bloco == "regulares":
        escala["saem"] = [s for s in escala["saem"] if not s.get("fontes_260")] + \
            [s for s in registro() if not s.get("fontes_260") and s["id"] not in {x["id"] for x in escala["saem"]}]
        escala["bloco"] = bloco
    elif bloco not in ("completo", "manual") and hz.exists():
        for b in load_json(hz).get("blocos", []):
            if b["bloco"] == bloco:
                tipos_bloco = set(b["tipos"])
        if tipos_bloco is not None:
            escala["saem"] = [s for s in escala["saem"] if s["tipo"] in tipos_bloco]
            escala["bloco"] = bloco
    if pedidos:
        todos = registro()
        saem = [dict(s, motivo="ativação manual pelo titular") for s in todos
                if s["id"] in pedidos or pedidos & set(s.get("fontes_260") or [])]
        escala = {"data": hoje.isoformat(), "saem": saem, "ficam": len(todos) - len(saem),
                  "total": len(todos), "previsoes_ativas": escala["previsoes_ativas"],
                  "manual": sorted(pedidos)}
    est = load_json(ESTADO) if ESTADO.exists() else {"sensores": {}}
    sens = est["sensores"]
    existentes = carregar_oportunidades()
    novos = total_ach = 0
    por_tipo: dict[str, dict] = {}
    for s in escala["saem"][: (limite or len(escala["saem"]))]:
        r = ler(s, pausa=pausa)
        reg = sens.setdefault(s["id"], {"nome": s["nome"], "tipo": s["tipo"], "leituras": 0,
                                        "achados_total": 0, "vazias_seguidas": 0})
        reg.update({"ultima": r["lido_em"], "motivo": s["motivo"],
                    "leituras": reg["leituras"] + 1,
                    "achados_ultima": len(r["achados"]),
                    "achados_total": reg["achados_total"] + len(r["achados"]),
                    "falhas_ultima": len(r["falhas"]),
                    "saude": (r["saude"] or r["falhas"])[:2],
                    "vazias_seguidas": 0 if r["achados"] else reg["vazias_seguidas"] + 1})
        # três leituras vazias com página respondendo = URL provavelmente é home, não listagem
        reg["alerta"] = ("trocar URL: 3 leituras sem achados com página respondendo"
                         if reg["vazias_seguidas"] >= 3 and r["saude"] and not r["falhas"] else None)
        registrar_dia(s["id"], hoje, r)
        est["sensores"].setdefault(s["id"], {})["diagnostico"] = r.get("diagnostico")
        for a in r["achados"]:
            total_ach += 1
            if a["id"] not in existentes:
                append_jsonl(DB, a); existentes[a["id"]] = a; novos += 1
        t = por_tipo.setdefault(s["tipo"], {"sensores": 0, "achados": 0, "falhas": 0})
        t["sensores"] += 1; t["achados"] += len(r["achados"]); t["falhas"] += len(r["falhas"])
    est["ultima_execucao"] = {"data": hoje.isoformat(), "em": now_iso(),
                              "manual": escala.get("manual"), "bloco": escala.get("bloco", bloco),
                              "sensores_executados": min(len(escala["saem"]), limite or 10**6),
                              "em_espera": escala["ficam"], "total_esquadra": escala["total"],
                              "previsoes_ativas": escala["previsoes_ativas"],
                              "achados": total_ach, "novos_na_base": novos, "por_tipo": por_tipo}
    write_json(ESTADO, est)
    return est["ultima_execucao"]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
