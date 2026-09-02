"""Alternativas quando o portal oficial bloqueia.

Regra do titular: site bloqueado ou inacessível (gov.br, mpgo.mp.br,
tjgo.jus.br…) não é fim de linha — é sinal para descer uma escada de
alternativas, cada degrau mais caro que o anterior, até alimentar o
repositório. A finalidade é ENTENDER ONDE A FONTE ESTÁ e como funciona:

  · judicial  → quais varas e juízes fazem a destinação (Res. CNJ 154/2012:
                cada vara publica edital de cadastramento de entidades);
  · permanente→ linha de captação o ano inteiro no calendário;
  · sazonal   → época prevista pelo regramento/histórico, e a data real
                assim que o edital sair.

A escada, por URL bloqueada:
  0. registrar o bloqueio (HTTP, DNS, timeout) com data — vira estatística;
  1. espelho institucional: variante da mesma casa que costuma ser pública
     (ex.: DJE em vez da home; API de dados abertos; RSS);
  2. cópia arquivada: Wayback Machine (web.archive.org) — texto histórico
     da mesma URL, suficiente para regra, calendário e requisitos;
  3. agregador público que republica a fonte (Querido Diário para diários;
     PNCP para chamamentos; Transferegov para convênios; SALIC para Rouanet);
  4. IA com busca na web — pergunta fechada, modelo barato: "onde esta fonte
     publica, quais varas/setores, qual a época" — resposta só com URL oficial;
  5. pedido de acesso à informação (LAI): gera o texto do pedido ao órgão,
     pronto para o titular protocolar — última alternativa, e a mais lenta.

Cada degrau grava o que rendeu; a fonte fica com o mapa do que foi obtido e
de onde. Nada presumido: degrau sem resultado é declarado.
"""
from __future__ import annotations

import json
import re
from datetime import date
from urllib.parse import quote, urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

ESTADO = ROOT / "estado/bloqueios.json"
ALTERNATIVAS = ROOT / "config/alternativas_acesso.json"

# Espelhos institucionais conhecidos: onde a mesma casa costuma estar aberta
_ESPELHOS = {
    "www.tjgo.jus.br": ["https://www.tjgo.jus.br/index.php/diario-da-justica",
                        "https://projudi.tjgo.jus.br/", "https://www.tjgo.jus.br/index.php/transparencia"],
    "www.mpgo.mp.br": ["https://www.mpgo.mp.br/portal/transparencia",
                       "https://www.mpgo.mp.br/portal/diario-oficial-eletronico"],
    "www.trf1.jus.br": ["https://portal.trf1.jus.br/sjgo/", "https://www.trf1.jus.br/dspace/"],
    "www.gov.br": ["https://www.in.gov.br/consulta/-/buscar/dou?q={termo}&s=todos",
                   "https://dados.gov.br/dados/busca?termo={termo}"],
    "goias.gov.br": ["https://diariooficial.abc.go.gov.br/", "https://legisla.casacivil.go.gov.br/"],
    "www.goiania.go.gov.br": ["https://diariooficial.goiania.go.gov.br/",
                              "https://www.goiania.go.gov.br/transparencia/"],
    "portal.al.go.leg.br": ["https://portal.al.go.leg.br/noticias", "https://portal.al.go.leg.br/legislacao"],
    "www.goiania.go.leg.br": ["https://www.goiania.go.leg.br/transparencia"],
}
_AGREGADORES = {
    "diario_oficial": "https://queridodiario.ok.org.br/api/gazettes?querystring={termo}&territory_ids={ibge}",
    "chamamento": "https://pncp.gov.br/api/search/?q={termo}&tipos_documento=edital",
    "convenio": "https://api.transferegov.gov.br/",
    "rouanet": "https://salic.cultura.gov.br/",
}
_JUDICIAL = re.compile(r"tjgo|trf1|jus\.br|vara|juiz|prestação pecuniária|execução penal|cnj", re.I)


def registrar_bloqueio(url: str, erro: str, contexto: str = "") -> dict:
    est = load_json(ESTADO) if ESTADO.exists() else {"dominios": {}}
    dom = urlsplit(url).hostname or url
    d = est["dominios"].setdefault(dom, {"bloqueios": 0, "erros": {}, "ultimo": None, "urls": []})
    d["bloqueios"] += 1
    d["erros"][erro] = d["erros"].get(erro, 0) + 1
    d["ultimo"] = now_iso()
    if url not in d["urls"] and len(d["urls"]) < 20:
        d["urls"].append(url)
    if contexto:
        d["contexto"] = contexto
    est["atualizado_em"] = now_iso()
    write_json(ESTADO, est)
    return d


def escada(url: str, termo: str, fonte: dict | None = None) -> list[dict]:
    """A escada de alternativas para uma URL bloqueada — em ordem de custo."""
    dom = urlsplit(url).hostname or ""
    fonte = fonte or {}
    passos = [{"degrau": 0, "acao": "registrar bloqueio", "custo": "zero"}]
    for esp in _ESPELHOS.get(dom, []):
        passos.append({"degrau": 1, "acao": "espelho institucional", "url": esp.replace("{termo}", quote(termo)),
                       "custo": "zero"})
    passos.append({"degrau": 2, "acao": "cópia arquivada (Wayback Machine)",
                   "url": f"https://archive.org/wayback/available?url={quote(url, safe='')}", "custo": "zero",
                   "nota": "texto histórico da mesma URL: serve para regra, calendário e requisitos"})
    tipo = str(fonte.get("tipo_recurso") or fonte.get("tipo") or "")
    if "diario" in dom or "diario" in tipo:
        passos.append({"degrau": 3, "acao": "agregador (Querido Diário)", "url": _AGREGADORES["diario_oficial"], "custo": "zero"})
    if any(k in tipo for k in ("edital", "fundo", "chamamento")):
        passos.append({"degrau": 3, "acao": "agregador (PNCP)", "url": _AGREGADORES["chamamento"].replace("{termo}", quote(termo)), "custo": "zero"})
    if "rouanet" in (fonte.get("id") or "").lower():
        passos.append({"degrau": 3, "acao": "sistema da própria política (SALIC)", "url": _AGREGADORES["rouanet"], "custo": "zero"})
    pergunta = (f"Onde {fonte.get('fonte') or termo} publica seus editais/atos de destinação, "
                + ("quais varas e juízes fazem a destinação, " if _JUDICIAL.search(url + termo) else "")
                + "qual a época do ano e qual a norma que rege? Responda só com URLs oficiais e artigos.")
    passos.append({"degrau": 4, "acao": "IA com busca na web (modelo barato, pergunta fechada)",
                   "pergunta": pergunta, "custo": "baixo", "modelo": "haiku → sonnet se falhar"})
    passos.append({"degrau": 5, "acao": "pedido LAI ao órgão", "custo": "tempo",
                   "texto": texto_lai(fonte, termo, url)})
    return passos


def texto_lai(fonte: dict, termo: str, url: str) -> str:
    """Pedido de acesso à informação pronto para o titular protocolar."""
    orgao = fonte.get("orgao") or urlsplit(url).hostname or "órgão"
    return (f"Com fundamento na Lei 12.527/2011, solicito a {orgao}: (1) a norma vigente que "
            f"rege {fonte.get('fonte') or termo}; (2) o calendário/periodicidade de abertura para "
            f"entidades sem fins lucrativos; (3) a relação de editais/atos de destinação dos últimos "
            f"3 anos, com valores e beneficiários; (4) o endereço eletrônico onde tais atos são "
            f"publicados. A página {url} não respondeu às consultas automatizadas em {date.today():%d/%m/%Y}.")


def destinacao_judicial(fonte: dict) -> dict:
    """Para fontes judiciais: o que o Eldorado precisa mapear — varas e juízes.

    Resolução CNJ 154/2012, art. 2º-3º: cada vara com competência de execução
    penal publica edital anual de cadastramento de entidades e destina as
    prestações pecuniárias por decisão do juiz. Logo o alvo não é 'o TJGO': são
    as VEPs e Juizados de Goiânia e as comarcas com maior movimento.
    """
    return {
        "o_que_mapear": ["varas de execução penal e juizados especiais criminais de Goiânia e comarcas",
                         "juiz(a) titular de cada vara (assina o edital de cadastramento e a destinação)",
                         "edital anual de cadastramento de entidades (Res. CNJ 154/2012)",
                         "conta única de prestações pecuniárias e o cronograma de destinação",
                         "valores destinados nos últimos 3 anos e entidades beneficiadas"],
        "onde": ["DJE-GO (edital de cadastramento aparece com o nome da vara e do juiz)",
                 "Projudi / consulta de expedientes da vara",
                 "portal da transparência do TJGO (prestações pecuniárias)",
                 "Diário Oficial Eletrônico do MPGO (Programa Destina: Ato PGJ 58/2025)"],
        "lexico": ["Vara de Execução Penal", "VEP", "Juizado Especial Criminal", "cadastramento de entidades",
                   "prestação pecuniária", "Resolução 154", "juiz(a) de direito", "Destina", "Promotoria"],
        "apresentacao_no_calendario": ("permanente com edital anual: linha o ano inteiro, com a "
                                       "estrela no mês em que a vara costuma publicar o cadastramento"),
    }


def run() -> dict:
    """Consolida bloqueios registrados e a escada de cada domínio bloqueado."""
    est = load_json(ESTADO) if ESTADO.exists() else {"dominios": {}}
    f260 = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", []) \
        if (ROOT / "config/fontes_captacao_260.json").exists() else []
    por_dom: dict[str, dict] = {}
    for f in f260:
        for u in f["sites"]:
            por_dom.setdefault(urlsplit(u).hostname or "", f)
    saida = {}
    for dom, d in est["dominios"].items():
        fonte = por_dom.get(dom, {})
        saida[dom] = {"bloqueios": d["bloqueios"], "erros": d["erros"], "ultimo": d["ultimo"],
                      "escada": escada(d["urls"][0] if d["urls"] else f"https://{dom}/",
                                       fonte.get("programa") or dom, fonte),
                      "judicial": destinacao_judicial(fonte) if _JUDICIAL.search(dom) else None}
    write_json(ALTERNATIVAS, {"gerado_em": now_iso(), "dominios_bloqueados": len(saida),
                              "alternativas": saida,
                              "regra": "bloqueio nao encerra a busca: desce a escada ate alimentar o repositorio"})
    return {"dominios_bloqueados": len(saida), "gerado_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))


# ------------------------------------------------- degrau 4: IA para localizar
def localizar_com_ia(fonte: dict, hoje: date | None = None) -> dict:
    """Pergunta fechada ao modelo barato com busca na web: ONDE a fonte publica,
    QUAIS varas/setores destinam (se judicial), QUAL a época e QUAL a norma.
    Só URLs oficiais; sem credencial, declara. Escala para o intermediário se a
    resposta não trouxer URL oficial."""
    import os, urllib.request
    hoje = hoje or date.today()
    if not os.environ.get("FAROL_AI_API_KEY"):
        return {"status": "aguardando credencial FAROL_AI_API_KEY"}
    cfg = load_json(ROOT / "config/ia.json") if (ROOT / "config/ia.json").exists() else {}
    cadeia = (cfg.get("escalada_busca") or {}).get("cadeia") or []
    judicial = bool(_JUDICIAL.search(json.dumps(fonte, ensure_ascii=False)))
    prompt = (f"Fonte de recurso: {fonte.get('fonte') or fonte.get('programa')} — órgão: {fonte.get('orgao')} "
              f"({fonte.get('nivel')}). Hoje é {hoje:%d/%m/%Y}.\n"
              "Responda SOMENTE em JSON com as chaves: onde_publica (lista de URLs oficiais), "
              "norma (referência e URL), epoca (texto curto ou null), permanente (true/false)"
              + (", varas (lista de {vara, comarca, juiz, url}) " if judicial else "")
              + ". Se não encontrar em fonte oficial, use null. Nunca invente.")
    saida = {"degraus": []}
    for d in cadeia[:2]:
        corpo = {"model": d["modelo"], "max_tokens": max(d["max_tokens"], 700),
                 "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
                 "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(),
                                     headers={"content-type": "application/json",
                                              "x-api-key": os.environ["FAROL_AI_API_KEY"],
                                              "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                dados = json.loads(r.read())
        except Exception as exc:
            saida["degraus"].append({"modelo": d["modelo"], "status": f"falha: {type(exc).__name__}"})
            continue
        texto = " ".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
        with (ROOT / "estado/ia_uso.jsonl").open("a", encoding="utf-8") as h:
            h.write(json.dumps({"em": now_iso(), "modelo": d["modelo"], "tarefa": "localizar_fonte",
                                "uso": dados.get("usage", {})}, ensure_ascii=False) + "\n")
        try:
            js = json.loads(re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip())
        except Exception:
            saida["degraus"].append({"modelo": d["modelo"], "status": "resposta não estruturada"})
            continue
        urls = [u for u in (js.get("onde_publica") or []) if isinstance(u, str) and u.startswith("http")]
        saida["degraus"].append({"modelo": d["modelo"], "status": "respondeu", "urls": len(urls)})
        if urls:
            saida.update({"status": "localizada", "onde_publica": urls, "norma": js.get("norma"),
                          "epoca": js.get("epoca"), "permanente": js.get("permanente"),
                          "varas": js.get("varas") if judicial else None,
                          "modelo": d["modelo"], "em": now_iso(),
                          "nota": "URLs devolvidas pela IA precisam ser abertas pelo sensor antes de valer"})
            return saida
    saida["status"] = "não localizada"
    return saida


def run_localizacao(limite: int = 10) -> dict:
    """Para cada domínio bloqueado com fonte associada, desce até o degrau 4."""
    est = load_json(ESTADO) if ESTADO.exists() else {"dominios": {}}
    f260 = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", []) \
        if (ROOT / "config/fontes_captacao_260.json").exists() else []
    por_dom = {}
    for f in f260:
        for u in f["sites"]:
            por_dom.setdefault(urlsplit(u).hostname or "", f)
    feitos = []
    for dom, d in list(est["dominios"].items())[:limite]:
        if d.get("localizacao_ia") and d["localizacao_ia"].get("status") == "localizada":
            continue
        fonte = por_dom.get(dom)
        if not fonte:
            continue
        d["localizacao_ia"] = localizar_com_ia(fonte)
        feitos.append({"dominio": dom, "status": d["localizacao_ia"].get("status")})
    write_json(ESTADO, est)
    return {"localizacoes": feitos, "executado_em": now_iso()}
