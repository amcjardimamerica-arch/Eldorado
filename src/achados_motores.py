"""AS OPORTUNIDADES DE CADA MOTOR, SEM REPETIÇÃO (titular, 27/09).

Cada motor da Bússola mostra quantas oportunidades DIFERENTES encontrou e as 5 mais recentes, com a DATA DE
PUBLICAÇÃO ORIGINAL. A mesma oportunidade chega em registros diferentes (a divulgação e a página oficial, o
"continue lendo" da ABCR, o título com e sem acento, o endereço com e sem parâmetros): aqui ela conta uma vez.
Edição de diário oficial não é oportunidade e não entra.
Saída: docs/dados/achados_motores.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MESTRE = ROOT / "dados/oportunidades/oportunidades.jsonl"
SAIDA = ROOT / "docs/dados/achados_motores.json"
ALIAS = {   # motor da Bússola → identificadores de fonte gravados nos registros
    "pncp-api": {"pncp"}, "plat-observatorio-3setor": {"observatorio-3setor", "observatorio-terceiro-setor"},
    "plat-secult-go": {"secult-go", "goyazes-programa"}, "piloto-aberto": {"plat-piloto-aberto", "piloto-aberto"},
    "plat-piloto-aberto": {"plat-piloto-aberto", "piloto-aberto"}, "plat-abcr": {"abcr"},
}


def _norm_tit(t: str) -> str:
    t = re.sub(r"(?i)^continue lendo\s+", "", str(t or ""))
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t)[:70]


def _norm_url(u: str) -> str:
    p = urlsplit(str(u or "")); return ((p.hostname or "").replace("www.", "") + p.path.rstrip("/")).lower()


def _data(*v) -> str | None:
    for x in v:
        s = str(x or "")[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}$", s):
            return s
    return None


def montar() -> dict:
    D = json.loads((ROOT / "docs/dados/descricao_motores.json").read_text(encoding="utf-8"))
    motores = list((D.get("motores") or D).keys())
    regs = [json.loads(l) for l in MESTRE.open(encoding="utf-8") if l.strip()] if MESTRE.exists() else []
    # a data de publicação de muitas fontes (ABCR, Diário de Goiás) está na ficha da Biblioteca, não no registro
    pub_ficha = {}
    for f in (ROOT / "biblioteca_alexandria/oportunidades").glob("*/*/ficha.json"):
        try:
            fi = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if fi.get("id") and _data(fi.get("data_publicacao"), fi.get("publicado_em")):
            pub_ficha[fi["id"]] = _data(fi.get("data_publicacao"), fi.get("publicado_em"))
    ext = ROOT / "dados/editais/extraidos"
    out = {}
    for mid in motores:
        ids = {mid, mid.replace("plat-", "")} | ALIAS.get(mid, set())
        xs = [r for r in regs if r.get("fonte_id") in ids]
        if mid == "do-goiania":
            xs = [r for r in regs if r.get("fonte_id") == "querido-diario" and "goiânia" in str(r.get("titulo", "")).lower()]
        vistos_t, vistos_u, unicas = set(), set(), []
        for r in xs:
            r["_pub"] = _data(r.get("data_publicacao")) or pub_ficha.get(r.get("id"))
        for r in sorted(xs, key=lambda r: str(r["_pub"] or _data(r.get("descoberto_em"), r.get("coletado_em")) or ""), reverse=True):
            tit = str(r.get("titulo") or "")
            if not tit or re.match(r"(?i)di[aá]rio oficial d[eo] ", tit) or r.get("estado_export") in ("arquivado", "excluido"):
                continue
            kt, ku = _norm_tit(tit), _norm_url(r.get("url"))
            if (kt and kt in vistos_t) or (ku and ku in vistos_u):
                continue
            vistos_t.add(kt); vistos_u.add(ku)
            e = {}
            try:
                e = json.loads((ext / f"{r.get('id')}.json").read_text(encoding="utf-8"))
            except Exception:
                pass
            ve = e.get("verificacao_externa") if isinstance(e.get("verificacao_externa"), dict) else {}
            unicas.append({"id": r.get("id"), "titulo": re.sub(r"(?i)^continue lendo\s+", "", tit)[:160],
                           "url": ve.get("pagina_oficial") or e.get("pagina_oficial") or r.get("url"),
                           "publicado_em": r["_pub"], "visto_em": None if r["_pub"] else _data(r.get("descoberto_em"), r.get("coletado_em")),
                           "prazo": _data(r.get("fim"), ve.get("prazo"), e.get("fim")), "uf": r.get("uf")})
        out[mid] = {"total_registros": len(xs), "total_unicas": len(unicas), "ultimas": unicas[:5]}
    res = {"regra": "oportunidades diferentes por motor, sem repetição; as 5 mais recentes pela data de publicação original", "motores": out}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {m: (v["total_registros"], v["total_unicas"]) for m, v in out.items() if v["total_registros"]}


if __name__ == "__main__":
    print(montar())
