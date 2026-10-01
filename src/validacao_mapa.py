"""VALIDAÇÃO INDIVIDUAL DO MAPA (titular, 27/09/2026) — nada de dado podre ou inútil no mapa.

Cada oportunidade do mapa recebe UMA decisão, registrada em dados/oportunidades/validacao_mapa/validacao_AAAA-MM-DD.json
(o arquivo mais recente prevalece, item a item):

    valida_aberta             aberta, dentro da abrangência aprovada (nacional + Goiás + Goiânia), com os 12 dados
                              do edital (ou a dispensa declarada pelo próprio edital) tirados do site oficial
    valida_fora_abrangencia   aberta ou possivelmente aberta, mas de outro estado/município: fica no mapa com o mínimo
    arquivada_encerrada       oportunidade verdadeira, porém fora do prazo: sai do mapa, vai para o arquivo e alimenta
                              o cadastro preditivo (próxima edição)
    descartada                não é oportunidade (notícia, vaga, blog, inexigibilidade, licitação, ato de pessoal…): sai
    pendente                  não foi possível confirmar na fonte oficial agora: fica no mapa, com o motivo

aplicar()   leva as decisões ao sistema — arquivo (dados/editais/arquivados.json), cadastro preditivo, estudo de cada
            oportunidade válida (dados/editais/extraidos/<id>.json → verificacao_externa) e livros de oportunidades (cria o
            opressor individual da válida que ainda não tinha; desliga o opressor criado para item descartado/encerrado).
dispensa()  o APRENDIZADO: regras de config/filtros_motores.json que dispensam na origem o que a validação mostrou
            ser lixo (usada pelo fluxo das oportunidades antes de o item chegar ao mapa).
relatorio() um relatório por motor de busca: o que ele achou, o que valeu, o site original a monitorar e a regra que
            o dispensa quando a oportunidade não presta — docs/dados/validacao_motores.json.

Regras invioláveis: a fonte é o site oficial do órgão ou do patrocinador (diário, PNCP, portais e agregadores só
servem para descobrir); nenhuma data é inventada ou estimada — campo sem confirmação fica null com o motivo.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

PASTA = ROOT / "dados/oportunidades/validacao_mapa"
FILTROS = ROOT / "config/filtros_motores.json"
ARQUIVADOS = ROOT / "dados/editais/arquivados.json"
EXT = ROOT / "dados/editais/extraidos"
CAT_OPR = ROOT / "biblioteca_alexandria/fontes/motores.json"
EST_OPR = ROOT / "estado/opressores.json"
PRED = ROOT / "biblioteca_alexandria/base/preditivo/oportunidades.jsonl"
SAIDA_REL = ROOT / "docs/dados/validacao_motores.json"
DECISOES = ("valida_aberta", "valida_fora_abrangencia", "arquivada_encerrada", "descartada", "pendente")
SAEM_DO_MAPA = ("arquivada_encerrada", "descartada")
ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower())


def _nu(u: str) -> str:
    p = urlsplit(str(u or "")); return ((p.hostname or "").replace("www.", "") + p.path.rstrip("/")).lower()


# ───────────────────────── decisões registradas ─────────────────────────
def carregar() -> dict[str, dict]:
    """id → registro de validação (arquivos em ordem de data; o mais recente prevalece)."""
    out: dict[str, dict] = {}
    for arq in sorted(PASTA.glob("validacao_*.json")) if PASTA.exists() else []:
        for r in (load_json(arq).get("itens") or []):
            if r.get("id") and r.get("decisao") in DECISOES:
                out[r["id"]] = {**r, "_arquivo": arq.name}
    return out


def _nt(t: str) -> str:
    t = re.sub(r"(?i)^continue lendo\s+", "", str(t or "")); return re.sub(r"[^a-z0-9]+", "", _norm(t))[:70]


def indice_heranca(V: dict[str, dict] | None = None) -> dict[str, dict]:
    """Mesma página ou mesmo título de item já validado (fora de diário) herda a decisão: a validação vale para as
    cópias que o fluxo escondia atrás da deduplicação e para as recoletas do mesmo endereço."""
    V = carregar() if V is None else V; idx: dict[str, dict] = {}
    for r in V.values():
        if str(r.get("tipo") or "").startswith("menção"):
            continue
        for k in ("u:" + _nu(r.get("url")), "u:" + _nu(r.get("fonte_oficial")) if r.get("decisao", "").startswith("valida") else "", "t:" + _nt(r.get("titulo"))):
            if len(k) > 4:
                idx.setdefault(k, r)
    return idx


def herdada(m: dict, idx: dict[str, dict]) -> dict | None:
    tit = str(m.get("titulo") or "")
    if re.match(r"(?i)di[aá]rio oficial de .+\d{4}-\d{2}-\d{2}", tit):
        return None                                    # a mesma edição de diário traz atos diferentes: nunca herda
    return idx.get("u:" + _nu(m.get("url"))) or idx.get("t:" + _nt(tit))


# ───────────────────────── aprendizado: regras de dispensa ─────────────────────────
_CACHE: dict = {}


def _filtros() -> dict:
    if "f" not in _CACHE:
        _CACHE["f"] = load_json(FILTROS) if FILTROS.exists() else {"regras": [], "diario": {"regras": []}}
    return _CACHE["f"]


def classificar_trecho_diario(trecho: str) -> tuple[str, str, str]:
    """(decisao, regra, motivo) para o trecho de uma edição de diário oficial."""
    t = _norm(trecho); cfg = _filtros().get("diario") or {}
    for r in cfg.get("regras") or []:
        if re.search(r["rx"], t):
            return r["decisao"], r["id"], r["motivo"]
    s = cfg.get("sem_regra") or {}
    if s.get("exceto_rx") and re.search(s["exceto_rx"], t):
        return s.get("senao", "revisar"), "sem_regra", "menciona chamamento/edital sem padrão reconhecido — revisar"
    return s.get("decisao", "descartada"), "sem_regra", s.get("motivo", "trecho sem edital")


def _motor(origem: str, m: dict) -> str:
    o = str(origem or "")
    return str(m.get("fonte_id") or (o[6:] if o.startswith("motor ") else o) or "?")


def dispensa(origem: str, m: dict, tipo: str | None = None) -> dict | None:
    """Regra aprendida que dispensa o registro antes do mapa. None = segue para o mapa."""
    motor = _motor(origem, m)
    tit = re.sub(r"\s+", " ", str(m.get("titulo") or "")).strip(); url = str(m.get("url") or "")
    if "duckduckgo.com/l/" in url and "uddg=" in url:          # link embrulhado pelo buscador: decide pelo endereço real
        from urllib.parse import parse_qs, unquote
        url = unquote((parse_qs(urlsplit(url).query).get("uddg") or [url])[0])
    if motor == "querido-diario" or re.match(r"(?i)di[aá]rio oficial de .+\d{4}-\d{2}-\d{2}", tit):
        if not m.get("evidencia"):
            return None
        dec, regra, motivo = classificar_trecho_diario(m.get("evidencia"))
        return {"decisao": dec, "regra": f"diario:{regra}", "motivo": motivo} if dec in ("descartada", "arquivada") else None
    for r in _filtros().get("regras") or []:
        if r.get("motores") and motor not in r["motores"]:
            continue
        if r.get("exceto_motores") and motor in r["exceto_motores"]:
            continue
        if r.get("exceto_tipo") and tipo == r["exceto_tipo"]:
            continue
        ok = False
        if r.get("url") and re.search(r["url"], url, re.I):
            ok = True
        if r.get("titulo") and re.search(r["titulo"], tit, re.I) and not (r.get("exceto_titulo") and re.search(r["exceto_titulo"], tit, re.I)):
            ok = True
        if r.get("url_raiz") and url.startswith("http") and urlsplit(url).path.strip("/") == "" and not urlsplit(url).query:
            ok = True
        if ok:
            return {"decisao": r["decisao"], "regra": r["id"], "motivo": r["motivo"]}
    return None


# ───────────────────────── aplicação ao sistema ─────────────────────────
def _oid(pagina: str) -> str:
    return "nova-" + hashlib.sha1(_nu(pagina).encode()).hexdigest()[:12]


def _itens_confirmados(r: dict) -> dict:
    """Itens já confirmados na validação entram prontos no opressor (a IA não gasta tokens com o que já se sabe)."""
    out = {}
    for k, v in (r.get("doze_itens") or {}).items():
        if not isinstance(v, dict):
            continue
        if v.get("status") == "confirmado" and v.get("valor"):
            out[k] = v["valor"]
        elif v.get("status") == "dispensado pelo edital":
            out[k] = "dispensado pelo edital" + (f": {v['valor']}" if v.get("valor") else "")
    return out


def aplicar(hoje: date | None = None) -> dict:
    """Idempotente: rodar de novo não duplica nada."""
    hoje = hoje or date.today(); V = carregar()
    res = {"arquivados_novos": 0, "estudos_gravados": 0, "preditivo_atualizado": 0, "preditivo_novo": 0,
           "opressores_criados": 0, "opressores_desligados": 0}
    if not V:
        return res
    # 1. ARQUIVO: descartadas e encerradas saem do sistema inteiro (mapa, enquadramento, análises)
    arq = load_json(ARQUIVADOS) if ARQUIVADOS.exists() else {}
    for eid, r in V.items():
        if r["decisao"] in SAEM_DO_MAPA and eid not in arq:
            arq[eid] = {"estado": "descartado" if r["decisao"] == "descartada" else "encerrado", "em": r.get("validado_em") or hoje.isoformat(),
                        "por": "validação individual do mapa", "motivo": str(r.get("motivo") or "")[:240]}
            res["arquivados_novos"] += 1
    write_json(ARQUIVADOS, arq)
    # 2. ESTUDO de cada oportunidade verdadeira com fonte oficial (válida ou encerrada)
    EXT.mkdir(parents=True, exist_ok=True)
    for eid, r in V.items():
        if r["decisao"] in ("valida_aberta", "valida_fora_abrangencia", "arquivada_encerrada") and r.get("fonte_oficial"):
            fp = EXT / f"{eid}.json"; e = load_json(fp) if fp.exists() else {"id": eid, "titulo": r.get("titulo"), "url": r.get("url")}
            ve = {"prazo": r.get("prazo"), "inicio": r.get("inicio"), "pagina_oficial": r.get("fonte_oficial"),
                  "origem_fonte": r.get("origem_fonte"), "decisao": r["decisao"], "motivo": r.get("motivo"),
                  "doze_itens": r.get("doze_itens"), "verificado_em": r.get("validado_em"), "via": "validação individual do mapa"}
            if e.get("verificacao_externa") != ve:
                e["verificacao_externa"] = ve
                if r.get("objeto") and not e.get("objeto"):
                    e["objeto"] = r["objeto"]
                write_json(fp, e); res["estudos_gravados"] += 1
    # 3. PREDITIVO: toda oportunidade verdadeira compõe a previsão (encerradas principalmente)
    linhas = [json.loads(l) for l in PRED.read_text(encoding="utf-8").splitlines() if l.strip()] if PRED.exists() else []
    por_id = {x.get("id"): x for x in linhas}
    for eid, r in V.items():
        if r["decisao"] not in ("valida_aberta", "valida_fora_abrangencia", "arquivada_encerrada"):
            continue
        estudo = {k: v for k, v in {"validado_em": r.get("validado_em"), "decisao": r["decisao"], "prazo": r.get("prazo"),
                                    "pagina_oficial": r.get("fonte_oficial"), "motivo": r.get("motivo")}.items() if v is not None}
        x = por_id.get(eid)
        if x is None:
            prazo = r.get("prazo")
            x = {"id": eid, "titulo": r.get("titulo"), "orgao": r.get("orgao"), "uf": r.get("uf"), "origem": r.get("origem"),
                 "tipo": r.get("tipo"), "ciclo": r.get("ciclo") or "indefinido", "publicado_em": r.get("publicado_em"), "prazo": prazo,
                 # janela só a partir de data CONFIRMADA na fonte oficial; sem data confirmada fica null (nada estimado do nada)
                 "proxima_janela_estimada": (date.fromisoformat(prazo) + timedelta(days=365)).isoformat()[:7] if prazo else None,
                 "confianca": "alta" if (prazo and r.get("fonte_oficial")) else "baixa", "confirmada": r["decisao"] == "valida_aberta",
                 "cadastrado_em": hoje.isoformat(), "estudos": []}
            linhas.append(x); por_id[eid] = x; res["preditivo_novo"] += 1
        if not any(s.get("validado_em") == estudo.get("validado_em") and s.get("decisao") == estudo.get("decisao") for s in x.get("estudos") or []):
            x.setdefault("estudos", []).append(estudo); x["estudos"] = x["estudos"][-5:]
            if r.get("prazo") and r.get("fonte_oficial"):
                x["prazo"] = r["prazo"]; x["confianca"] = "alta"
            x["situacao"] = {"valida_aberta": "aberta", "valida_fora_abrangencia": "aberta (fora da abrangência)", "arquivada_encerrada": "encerrada — arquivada"}[r["decisao"]]
            res["preditivo_atualizado"] += 1
    if linhas:
        PRED.parent.mkdir(parents=True, exist_ok=True)
        PRED.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")
    # 4. MOTORES OPRESSORES: apresentação individual de cada válida; nada de opressor gastando IA com lixo
    C = load_json(CAT_OPR) if CAT_OPR.exists() else {"motores": []}; L = load_json(EST_OPR) if EST_OPR.exists() else {"ligados": {}}
    L.setdefault("ligados", {}); cat = {x["id"]: x for x in C.get("motores") or []}
    usados_por_validas = {(r.get("opressor") or {}).get("id") for r in V.values() if r["decisao"] in ("valida_aberta", "valida_fora_abrangencia", "pendente")}
    for eid, r in V.items():
        op = (r.get("opressor") or {}).get("id")
        if r["decisao"] in ("valida_aberta", "valida_fora_abrangencia") and op and op in cat:
            # já tinha apresentação individual: garante que está ligado, com os dados confirmados (a IA só busca o que falta)
            if not cat[op].get("ativa", True):
                cat[op]["ativa"] = True; cat[op]["motivo_status"] = f"religado pela validação do mapa: oportunidade aberta confirmada no site oficial ({r.get('validado_em')})"
                res["opressores_religados"] = res.get("opressores_religados", 0) + 1
            reg = L["ligados"].get(op)
            if reg is None:
                L["ligados"][op] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=30)).isoformat(),
                                    "origem": "automática: oportunidade validada no site oficial", "dias": 0, "ia": [], "itens": _itens_confirmados(r)}
            else:
                for k, v in _itens_confirmados(r).items():
                    reg.setdefault("itens", {}).setdefault(k, v)
        if r["decisao"] in ("valida_aberta", "valida_fora_abrangencia") and r.get("fonte_oficial") and not op and not r.get("mesma_de"):
            oid = _oid(r["fonte_oficial"])
            # já existe opressor com o mesmo programa (título) — reaproveita em vez de duplicar (o fluxo funde duplicados)
            mesmo = [k for k, x in cat.items() if _nt(x.get("programa")) == _nt(str(r.get("titulo") or "")[:160]) or _nu(x.get("pagina")) == _nu(r["fonte_oficial"])]
            if mesmo and oid not in cat:
                oid = mesmo[0]
            if oid not in cat:
                x = {"id": oid, "programa": str(r.get("titulo") or "")[:160], "orgao": r.get("orgao") or "", "motor": "f260-" + oid,
                     "familia": "Outros programas", "esfera": "Estado" if r.get("uf") else "Brasil", "uf": r.get("uf") or "BR", "ativa": True,
                     "tipo": "oportunidade_mapeada", "pagina": r["fonte_oficial"], "paginas": [r["fonte_oficial"]], "validacao": "validada no site oficial",
                     "motivo_status": f"criado pela validação individual do mapa ({r.get('validado_em')})", "criado_em": hoje.isoformat(),
                     "proxima_data": {"inicio": r.get("inicio"), "fim": r.get("prazo")} if r.get("prazo") else None,
                     "mencoes": [{"titulo": str(r.get("titulo") or "")[:120], "url": r.get("url")}], "oportunidade_id": eid}
                C.setdefault("motores", []).append(x); cat[oid] = x; res["opressores_criados"] += 1
            if oid not in L["ligados"]:
                L["ligados"][oid] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=30)).isoformat(),
                                     "origem": "automática: oportunidade validada no site oficial", "dias": 0, "ia": [], "itens": _itens_confirmados(r)}
        if r["decisao"] in SAEM_DO_MAPA and op and op in cat and op not in usados_por_validas and cat[op].get("tipo") == "oportunidade_mapeada" and cat[op].get("ativa", True) \
                and cat[op].get("atual") in (None, eid):      # 29/09: opressor que hoje serve outra oportunidade aberta não é desligado
            # só desliga opressor criado para ESTA oportunidade (fontes permanentes nunca são desligadas aqui)
            cat[op]["ativa"] = False; cat[op]["motivo_status"] = f"desligado pela validação do mapa: {str(r.get('motivo') or '')[:160]}"
            if op in L["ligados"]:
                L.setdefault("historico", []).append({**L["ligados"].pop(op), "id": op, "desligado_em": hoje.isoformat(), "motivo": "validação do mapa"})
            res["opressores_desligados"] += 1
    # mesmo formato que o fluxo e o repositório usam (indent=1): evita reescrever o catálogo inteiro a cada execução
    CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # 01/10: compacto
    EST_OPR.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


# ───────────────────────── relatório por motor de busca ─────────────────────────
def relatorio() -> dict:
    V = carregar(); mot: dict[str, dict] = {}
    for eid, r in V.items():
        k = r.get("motor") or "?"
        m = mot.setdefault(k, {"motor": k, "total": 0, "por_decisao": {d: 0 for d in DECISOES}, "validas": [], "encerradas": [],
                               "motivos_descarte": {}, "regras_que_dispensam": {}, "sites_originais": {}, "recomendacoes": {}})
        m["total"] += 1; m["por_decisao"][r["decisao"]] += 1
        if r["decisao"].startswith("valida"):
            m["validas"].append({"id": eid, "titulo": r.get("titulo"), "prazo": r.get("prazo"), "fonte_oficial": r.get("fonte_oficial"), "abrangencia": r.get("abrangencia")})
        elif r["decisao"] == "arquivada_encerrada":
            m["encerradas"].append({"id": eid, "titulo": r.get("titulo"), "prazo": r.get("prazo"), "fonte_oficial": r.get("fonte_oficial")})
        if r["decisao"] == "descartada":
            mt = str(r.get("motivo") or "").split(" — ")[0][:80]; m["motivos_descarte"][mt] = m["motivos_descarte"].get(mt, 0) + 1
        if r.get("regra_aprendida"):
            m["regras_que_dispensam"][r["regra_aprendida"]] = m["regras_que_dispensam"].get(r["regra_aprendida"], 0) + 1
        if r.get("fonte_oficial"):
            h = urlsplit(r["fonte_oficial"]).hostname or ""; m["sites_originais"][h] = m["sites_originais"].get(h, 0) + 1
        if r.get("recomendacao_motor"):
            m["recomendacoes"][r["recomendacao_motor"]] = m["recomendacoes"].get(r["recomendacao_motor"], 0) + 1
    for m in mot.values():
        uteis = m["por_decisao"]["valida_aberta"] + m["por_decisao"]["valida_fora_abrangencia"] + m["por_decisao"]["arquivada_encerrada"]
        m["aproveitamento_pct"] = round(100 * uteis / m["total"], 1) if m["total"] else 0.0
        m["dispensaveis_pela_regra"] = sum(m["regras_que_dispensam"].values())
        m["motivos_descarte"] = dict(sorted(m["motivos_descarte"].items(), key=lambda kv: -kv[1])[:8])
        m["recomendacoes"] = [k for k, _ in sorted(m["recomendacoes"].items(), key=lambda kv: -kv[1])[:10]]
    out = {"gerado_em": now_iso(), "total": len(V), "por_decisao": {d: sum(1 for r in V.values() if r["decisao"] == d) for d in DECISOES},
           "motores": sorted(mot.values(), key=lambda m: -m["total"])}
    write_json(SAIDA_REL, out)
    return out


def run() -> dict:
    r = aplicar(); rel = relatorio()
    return {**r, "motores_no_relatorio": len(rel["motores"]), "por_decisao": rel["por_decisao"]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
