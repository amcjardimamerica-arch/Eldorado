"""PARECERES INDIVIDUAIS NOS LIVROS + MARCADOR DE INICIATIVA (titular, 02/10/2026).

Cada oportunidade aberta recebe um PARECER individual (12 itens, decisão, conselho de 7 lentes, histórico de 3 anos)
gravado em dados/oportunidades/pareceres_livros/pareceres_AAAA-MM-DD*.json. Este módulo leva os pareceres para os
LIVROS da Biblioteca (biblioteca_alexandria/fontes/motores.json → livro.pareceres[]), de forma ACUMULATIVA: quando a
oportunidade for aberta de novo, o livro já traz o histórico de pareceres anteriores.

Marcador NOVO — iniciativa: poder_publico · iniciativa_privada · mista (recurso público operado por privado: leis de
incentivo, parcerias). Vai para livro.iniciativa e para o cartão do painel (campo `iniciativa`).

Oportunidade sem livro (fora da abrangência ou não seleção de associações): o parecer fica em
biblioteca_alexandria/pareceres/sem_livro.json, com o motivo da dispensa do livro.

Idempotente: o mesmo parecer (mesma data + mesma oportunidade) nunca é gravado duas vezes.
"""
from __future__ import annotations

import json
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

PASTA = ROOT / "dados/oportunidades/pareceres_livros"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
SEM_LIVRO = ROOT / "biblioteca_alexandria/pareceres/sem_livro.json"
INICIATIVAS = ("poder_publico", "iniciativa_privada", "mista")
MAX_PARECERES = 12          # por livro: os mais recentes (o resto continua no arquivo de pareceres)


def carregar() -> dict[str, dict]:
    """id da oportunidade → parecer mais recente (arquivos em ordem de nome; o mais novo prevalece)."""
    out: dict[str, dict] = {}
    for arq in sorted(PASTA.glob("pareceres_*.json")) if PASTA.exists() else []:
        for p in (load_json(arq).get("pareceres") or []):
            if p.get("id"):
                out[p["id"]] = {**p, "_arquivo": arq.name}
    return out


def iniciativa_por_id(P: dict[str, dict] | None = None) -> dict[str, str]:
    P = carregar() if P is None else P
    return {k: (v.get("iniciativa") or {}).get("valor") for k, v in P.items() if (v.get("iniciativa") or {}).get("valor") in INICIATIVAS}


def _resumo(p: dict) -> dict:
    dz = p.get("doze_itens") or {}
    return {"data": p.get("data"), "oportunidade": p.get("id"), "titulo": str(p.get("titulo") or "")[:160], "estudo": p.get("estudo"),
            "decisao": p.get("decisao"), "abrangencia": p.get("abrangencia"), "prazo": p.get("prazo"), "fonte_oficial": p.get("fonte_oficial"),
            "regime": p.get("regime"), "iniciativa": p.get("iniciativa"),
            "doze": {k: {"status": (v or {}).get("status"), "valor": (v or {}).get("valor")} for k, v in dz.items()},
            "resolvidos": p.get("resolvidos"), "historico_3_anos": p.get("historico_3_anos"), "conselho": p.get("conselho"),
            "aplica_amc": p.get("aplica_amc"), "parecer": p.get("parecer"), "falta": p.get("falta")}


def aplicar() -> dict:
    P = carregar(); res = {"pareceres": len(P), "livros_atualizados": 0, "sem_livro": 0, "iniciativas": {}}
    if not P or not CAT.exists():
        return res
    C = json.loads(CAT.read_text(encoding="utf-8")); cat = {x.get("id"): x for x in C.get("motores") or []}
    por_op: dict[str, list] = {}
    for x in cat.values():                                 # oportunidade → livro (atual ou nas edições)
        for h in x.get("historico") or []:
            if h.get("id"):
                por_op.setdefault(h["id"], []).append(x["id"])
        if x.get("atual"):
            por_op.setdefault(x["atual"], []).append(x["id"])
    sem = load_json(SEM_LIVRO) if SEM_LIVRO.exists() else {"regra": __doc__.split("Idempotente")[0].strip(), "itens": {}}
    for oid, p in P.items():
        livros = [l for l in dict.fromkeys(([p.get("livro")] if p.get("livro") else []) + por_op.get(oid, [])) if l in cat]
        r = _resumo(p)
        ini = (p.get("iniciativa") or {}).get("valor")
        if ini:
            res["iniciativas"][ini] = res["iniciativas"].get(ini, 0) + 1
        if not livros:
            sem.setdefault("itens", {})[oid] = {**r, "motivo_sem_livro": p.get("sem_livro_motivo")}
            res["sem_livro"] += 1
            continue
        for lid in livros:
            lv = cat[lid].setdefault("livro", {}); ps = lv.setdefault("pareceres", [])
            if any(q.get("data") == r["data"] and q.get("oportunidade") == oid for q in ps):
                continue
            ps.append(r); lv["pareceres"] = ps[-MAX_PARECERES:]
            if ini in INICIATIVAS:
                lv["iniciativa"] = {"valor": ini, "fundamento": (p.get("iniciativa") or {}).get("fundamento"), "em": p.get("data")}
            if p.get("historico_3_anos"):
                lv["historico_3_anos"] = {**p["historico_3_anos"], "em": p.get("data")}
            at = lv.setdefault("atualizacoes", [])
            at.append({"em": now_iso(), "o_que": f"parecer individual de {p.get('data')} ({p.get('decisao')}, {p.get('resolvidos')}/12)"}); lv["atualizacoes"] = at[-20:]
            res["livros_atualizados"] += 1
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    sem["em"] = now_iso(); SEM_LIVRO.parent.mkdir(parents=True, exist_ok=True); write_json(SEM_LIVRO, sem)
    return res


def run() -> dict:
    return aplicar()


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
