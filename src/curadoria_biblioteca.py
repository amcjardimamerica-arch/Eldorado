"""CONFERÊNCIA DA BIBLIOTECA (titular, 01/10) — cada livro conferido a cada ciclo, pelos parâmetros de
config/parametros_biblioteca.json:
  1. ABRANGÊNCIA  livro público MUNICIPAL só de Goiás; de outros estados, só estaduais ou regionais. O que sai vai para
                  biblioteca_alexandria/livros/arquivo_fora_da_abrangencia.jsonl.xz (nada se perde).
  2. EMPRESAS     empresa só entra como EDITAL (programa por concorrência). A empresa em si vira FONTE DE BUSCA:
                  continua vigiada pelos motores, com a pesquisa preservada, mas não é livro.
  3. DUPLICIDADE  livros que são a mesma oportunidade são juntados num só (histórico, checklist e ids).
Relatório: docs/dados/conferencia_livros.json
"""
from __future__ import annotations

import json
import lzma
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LIG = ROOT / "estado/opressores.json"
PAR = ROOT / "config/parametros_biblioteca.json"
ARQ = ROOT / "biblioteca_alexandria/livros/arquivo_fora_da_abrangencia.jsonl.xz"
REL = ROOT / "docs/dados/conferencia_livros.json"

sem = lambda t: "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))
MUN = re.compile(r"munic[ií]p|prefeitura|secretaria municipal|camara municipal|conselho municipal|fundo municipal|\bfmdca\b|\bcmdca\b|\bcmas\b|\bfmas\b|\bcomdica\b|\bsemas\b|\bsmas\b|\bsemasdh\b|\bsejuc\b|\bsemed\b|\bsme\b|\bsemus\b|\bsms\b|\bsmc\b|\bsecult municipal\b|\bfundac municipal\b")
PUB = re.compile(r"ministerio publico|\bmpt\b|\bmpf\b|procuradoria|justica|munic[ií]p|prefeitura|secretaria|governo|minist|fundo |conselho|camara|assembleia|tribunal|uniao|federal|estadual|\bseds\b|secult|pnab|aldir|chamamento publico|emenda")
PRIV = re.compile(r"institut|fundac|\bs\.?a\.?\b|ltda|empresa|banco|grupo |cooperativa|foundation|fondation|corporat|seguros|natura|ambev|\bvale\b|itau|bradesco|santander|petrobras|equatorial|unimed")
SEL = re.compile(r"edital|editais|chamada|chamamento|sele[cç]|selecao|premio|inscri|concurso de projetos|convocat|programa de apoio|grant|call for|candidat|residenc|bolsa|fellowship|award|open call|apply|destinac")
GEN = set(("aviso chamamento chamada publico publica publicado diario oficial edital editais selecao credenciamento organizacoes organizacao sociedade "
           "civil projetos projeto termo parceria parcerias ref presente objetivo tem por objeto para de da do das dos e a o em com no na nos nas pela "
           "pelo municipio municipal prefeitura secretaria fomento colaboracao celebracao propostas proposta oscs osc entidades sem fins lucrativos").split())


def _txt(x: dict) -> str:
    return sem(f"{x.get('programa') or ''} {x.get('orgao') or ''} " + " ".join(str(h.get("titulo") or "") for h in (x.get("historico") or [])[-3:]))


def natureza(x: dict) -> str:
    if x.get("natureza") in ("publica", "privada"):
        return x["natureza"]
    t = _txt(x)
    if x.get("geo") == "INT":
        return "privada"
    if PUB.search(t) and not re.search(r"institut|fundac|empresa|s\.a\.|ltda", sem(x.get("orgao"))):
        return "publica"
    return "privada" if PRIV.search(t) else ("publica" if PUB.search(t) else "indefinida")


def municipal(x: dict) -> bool:
    from .livros_opressores import uf_do_dominio
    return bool(MUN.search(_txt(x)) or x.get("abrangencia") == "municipal" or uf_do_dominio(x.get("pagina"))[1] == "municipal")


GO_CIDADES = re.compile(r"goias|goiania|aparecida de goiania|anapolis|rio verde|senador canedo|trindade|catalao|itumbiara|jatai|luziania|formosa|"
                        r"valparaiso|aguas lindas|novo gama|caldas novas|goianesia|inhumas|cristalina|quirinopolis|niquelandia|porangatu|mineiros|"
                        r"pirenopolis|alvorada do norte|goiatuba|morrinhos|ceres|uruacu|planaltina de goias|cidade ocidental|santo antonio do descoberto")


def fora_da_abrangencia(x: dict) -> bool:
    """Público MUNICIPAL só de Goiás — inclusive quando o estado não foi identificado (geo nacional)."""
    from .livros_opressores import uf_do_dominio
    _uf, _niv = uf_do_dominio(x.get("pagina"))
    if _niv == "municipal" and _uf != "GO":
        return True                                    # site oficial de prefeitura/câmara de outro estado
    forte = bool(MUN.search(_txt(x)))                  # texto com órgão municipal: é público municipal, mesmo em blog
    if (natureza(x) != "publica" and not forte) or not municipal(x) or x.get("geo") in ("GO", "INT"):
        return False
    if x.get("geo") in ("BR", None):
        return not GO_CIDADES.search(_txt(x))          # municipal sem estado: fica só se for de cidade goiana
    return True


def empresa_sem_edital(x: dict) -> bool:
    return natureza(x) == "privada" and x.get("geo") != "INT" and not SEL.search(_txt(x))


def _base(x: dict) -> str:
    n = str(x.get("nome_classificado") or x.get("programa") or "").split(" — ")[0]
    return re.sub(r"\s+", " ", re.sub(r"\b(19|20)\d\d\b|\bn[ºo°]?\s*\d+[\w/.-]*|\b\d+\b|[^a-z ]", " ", sem(n))).strip()


def _host(u) -> str:
    return re.sub(r"^www\.", "", (re.sub(r"^https?://", "", str(u or "")).split("/")[0]).lower())


def mesma_oportunidade(a: dict, b: dict, p: dict) -> bool:
    from rapidfuzz import fuzz
    if (a.get("geo"), a.get("municipio") or "") != (b.get("geo"), b.get("municipio") or ""):
        return False
    da = [w for w in _base(a).split() if w not in GEN and len(w) > 2]
    db = [w for w in _base(b).split() if w not in GEN and len(w) > 2]
    m = p.get("palavras_distintivas_minimas", 2)
    if len(da) < m and len(db) < m:                    # os DOIS genéricos: só com a mesma página
        return bool(a.get("pagina") and a.get("pagina") == b.get("pagina"))
    if len(da) < m or len(db) < m:                     # um genérico e outro não: programas diferentes na mesma página
        return False
    ja, jb = " ".join(da), " ".join(db)
    if fuzz.token_sort_ratio(ja, jb) < p.get("nome_parecido_minimo", 90) or fuzz.token_set_ratio(ja, jb) < p.get("nome_contido_minimo", 95):
        return False
    return fuzz.ratio(sem(a.get("orgao")), sem(b.get("orgao"))) >= p.get("financiador_parecido_minimo", 80) or \
        (_host(a.get("pagina")) and _host(a.get("pagina")) == _host(b.get("pagina")))


def _juntar(s: dict, o: dict) -> None:
    ids = {h.get("id") or h.get("titulo") for h in s.get("historico") or []}
    s.setdefault("historico", []).extend(h for h in o.get("historico") or [] if (h.get("id") or h.get("titulo")) not in ids)
    ck_s = s.setdefault("livro", {}).setdefault("checklist", {})
    for k, v in ((o.get("livro") or {}).get("checklist") or {}).items():
        ck_s.setdefault(k, v)
    if not ck_s:
        s["livro"].pop("checklist", None)
    s.setdefault("ids_juntados", []).extend([o["id"]] + (o.get("ids_juntados") or []))
    at = s["livro"].setdefault("atualizacoes", [])
    at.append({"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "o_que": f"juntado com {o['id']} (mesma oportunidade)"}); s["livro"]["atualizacoes"] = at[-8:]


def conferir() -> dict:
    P = json.loads(PAR.read_text(encoding="utf-8")); pd = P.get("duplicidade") or {}
    C = json.loads(CAT.read_text(encoding="utf-8")); L = json.loads(LIG.read_text(encoding="utf-8")) if LIG.exists() else {"ligados": {}}
    lig = L.get("ligados") or {}; ms = C.get("motores") or []
    # 1) abrangência
    fora = [x for x in ms if fora_da_abrangencia(x)]
    if fora:
        ant = lzma.decompress(ARQ.read_bytes()).decode().splitlines() if ARQ.exists() else []
        ja = {json.loads(l).get("id") for l in ant if l.strip()}
        ARQ.parent.mkdir(parents=True, exist_ok=True)
        ARQ.write_bytes(lzma.compress(("\n".join(ant + [json.dumps({**x, "arquivado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                                                    "motivo": "público municipal de outro estado (só Goiás tem livros municipais)"}, ensure_ascii=False)
                                                       for x in fora if x["id"] not in ja]) + "\n").encode()))
        ids_fora = {x["id"] for x in fora}
        ms = [x for x in ms if x["id"] not in ids_fora]
        for i in ids_fora:
            lig.pop(i, None)
    # 2) empresas sem edital → fonte de busca
    fontes = 0
    for x in ms:
        if empresa_sem_edital(x):
            if x.get("papel") != "fonte_de_busca":
                x["papel"] = "fonte_de_busca"; x["motivo_papel"] = "empresa sem edital por concorrência: vigiada como fonte, não é livro"; fontes += 1
        elif x.get("papel") == "fonte_de_busca":
            x.pop("papel", None)
    # 3) duplicidade (só entre livros; mesmo lugar)
    livros = [x for x in ms if x.get("papel") != "fonte_de_busca"]
    por_lugar = defaultdict(list)
    for x in livros:
        por_lugar[(x.get("geo"), x.get("municipio") or "")].append(x)
    pai = {}
    def raiz(i):
        while pai.get(i, i) != i:
            i = pai[i]
        return i
    for L_ in por_lugar.values():
        for i in range(len(L_)):
            for j in range(i + 1, len(L_)):
                if mesma_oportunidade(L_[i], L_[j], pd):
                    pai[raiz(L_[j]["id"])] = raiz(L_[i]["id"])
    grupos = defaultdict(list)
    por_id = {x["id"]: x for x in ms}
    for x in livros:
        grupos[raiz(x["id"])].append(x)
    sai, juntados = set(), []
    for g in grupos.values():
        if len(g) < 2:
            continue
        g.sort(key=lambda x: (not x.get("parametros"), x["id"] not in lig, x.get("tipo") == "repositorio_de_oportunidade",   # original do catálogo sobrevive (o gerador o recria)
                              -len(x.get("historico") or []), str(x.get("criado_em") or "0")))
        s = g[0]
        for o in g[1:]:
            _juntar(s, o); sai.add(o["id"])
            if o["id"] in lig and s["id"] not in lig:
                lig[s["id"]] = lig[o["id"]]
            lig.pop(o["id"], None)
        juntados.append({"fica": s["id"], "nome": s.get("nome_classificado"), "juntou": [o["id"] for o in g[1:]]})
    ms = [x for x in ms if x["id"] not in sai]
    C["motores"] = ms
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    L["ligados"] = lig; LIG.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    rel = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Relatório")[0].strip(),
           "livros": sum(1 for x in ms if x.get("papel") != "fonte_de_busca"), "fontes_de_busca": sum(1 for x in ms if x.get("papel") == "fonte_de_busca"),
           "arquivados_fora_da_abrangencia": len(fora), "por_estado_arquivados": dict(Counter(x.get("geo") for x in fora).most_common()),
           "empresas_viraram_fonte": fontes, "duplicatas_juntadas": len(sai), "grupos": juntados[:200]}
    REL.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: rel[k] for k in ("livros", "fontes_de_busca", "arquivados_fora_da_abrangencia", "empresas_viraram_fonte", "duplicatas_juntadas")}


if __name__ == "__main__":
    print(json.dumps(conferir(), ensure_ascii=False, indent=1))
