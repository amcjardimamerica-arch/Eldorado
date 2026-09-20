"""ACHADOS DO DIA — o que cada motor encontrou em cada dia, SEM REPETIÇÃO.

Regra do titular (20/09): uma oportunidade aparece no calendário só na PRIMEIRA data em
que foi encontrada. Se um motor a captura de novo em outro dia (o portal repete a notícia,
o diário republica), aquele dia conta como "sem oportunidade nova" para aquele motor.
Assim o mapa vira um resumo honesto do achado do dia, e não um eco.

Saída: docs/dados/achados_dia.json
  { "dias": { "AAAA-MM-DD": { "total": n, "motores": {motor: [ {id, titulo, url, area, uf} ]},
                              "reapresentados": k } },
    "primeira_data": { edital_id: "AAAA-MM-DD" } }
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

VETOR = re.compile(r"pncp\.gov|queridodiario|in\.gov\.br|diariooficial|observatorio3setor|captadores\.org|bussolasocial|prosas\.com", re.I)


def _chave_dedup(e: dict) -> str:
    """Duas capturas do mesmo edital em fontes diferentes viram uma só: título normalizado
    + órgão. (As duplicatas já consolidadas em dados/editais/duplicatas.json também caem aqui.)"""
    t = re.sub(r"\s+", " ", (e.get("titulo") or "").lower())
    t = re.sub(r"^(continue lendo|leia mais)\s*", "", t)
    t = re.sub(r"[^a-z0-9à-ú ]", "", t)[:90]
    return f"{t}|{(e.get('orgao') or e.get('fonte_nome') or '').lower()[:40]}"


def _motor_de(e: dict, mapa_fontes: dict) -> str:
    fid = e.get("fonte_id") or ""
    nome = e.get("fonte_nome") or ""
    if fid in mapa_fontes:
        return mapa_fontes[fid]
    for k, v in mapa_fontes.items():
        if k and (k in nome.lower() or k in fid.lower()):
            return v
    if re.search(r"pncp", f"{fid} {nome}", re.I): return "pncp-api"
    if re.search(r"querido|di[áa]rio oficial de", f"{fid} {nome}", re.I): return "diarios-municipais"
    if re.search(r"observat", f"{fid} {nome}", re.I): return "plat-observatorio-3setor"
    if re.search(r"abcr|captadores", f"{fid} {nome}", re.I): return "plat-abcr"
    if re.search(r"gife", f"{fid} {nome}", re.I): return "plat-gife"
    if re.search(r"prosas", f"{fid} {nome}", re.I): return "plat-prosas"
    if re.search(r"in\.gov|di[áa]rio oficial da uni[ãa]o|dou", f"{fid} {nome}", re.I): return "dou"
    if re.search(r"alego|assembleia", f"{fid} {nome}", re.I): return "alego-pl"
    if re.search(r"empresa|incentiv", f"{fid} {nome}", re.I): return "empresas-incentivadas"
    return fid or nome or "desconhecido"


def montar() -> dict:
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = list(dados.get("editais") or [])
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        from .compacto import expandir
        vistos = {x["id"] for x in universo}
        universo += [o for o in expandir(load_json(ab)) if o.get("id") not in vistos]
    op = [e for e in universo if e.get("tipo_registro") in ("edital", "regra_anual")]
    dups = load_json(ROOT / "dados/editais/duplicatas.json") if (ROOT / "dados/editais/duplicatas.json").exists() else {}
    fora = {d for g in dups.get("grupos", []) for d in g.get("duplicatas", [])}
    op = [e for e in op if e["id"] not in fora]
    mapa_fontes = {"observatorio-terceiro-setor": "plat-observatorio-3setor", "abcr": "plat-abcr", "gife": "plat-gife",
                   "prosas": "plat-prosas", "pncp": "pncp-api", "querido-diario": "diarios-municipais", "dou": "dou"}
    # primeira data de cada edital (deduplicado por chave)
    primeira: dict = {}
    por_chave: dict = {}
    for e in sorted(op, key=lambda x: (x.get("coletado_em") or x.get("publicado_em") or "9999")):
        data = (e.get("coletado_em") or e.get("publicado_em") or "")[:10]
        if not data:
            continue
        ch = _chave_dedup(e)
        if ch in por_chave:
            por_chave[ch]["reapresentacoes"].append({"id": e["id"], "data": data, "motor": _motor_de(e, mapa_fontes)})
            continue
        por_chave[ch] = {"id": e["id"], "data": data, "reapresentacoes": []}
        primeira[e["id"]] = data
    dias: dict = {}
    reap: dict = {}
    for ch, reg in por_chave.items():
        e = next(x for x in op if x["id"] == reg["id"])
        motor = _motor_de(e, mapa_fontes)
        url = e.get("pagina_divulgacao") if e.get("pagina_divulgacao") and not VETOR.search(str(e.get("pagina_divulgacao"))) else e.get("url")
        dias.setdefault(reg["data"], {"total": 0, "motores": {}, "reapresentados": 0})
        dias[reg["data"]]["motores"].setdefault(motor, []).append(
            {"id": e["id"], "titulo": (e.get("titulo") or "")[:110], "url": url, "area": e.get("area"), "uf": e.get("uf"),
             "fim": e.get("fim"), "validada": e.get("selo_validacao") == "validada"})
        dias[reg["data"]]["total"] += 1
        for r in reg["reapresentacoes"]:
            dias.setdefault(r["data"], {"total": 0, "motores": {}, "reapresentados": 0})
            dias[r["data"]]["reapresentados"] += 1
            reap.setdefault(r["id"], {"primeira_vez": reg["data"], "canonico": reg["id"]})
    res = {"em": now_iso(), "regra": "cada oportunidade aparece só na PRIMEIRA data em que foi encontrada; reapresentações contam como 'sem oportunidade nova'",
           "dias": dict(sorted(dias.items())), "primeira_data": primeira, "reapresentados": reap,
           "total_unicos": len(por_chave), "total_reapresentacoes": sum(len(v["reapresentacoes"]) for v in por_chave.values())}
    write_json(ROOT / "docs/dados/achados_dia.json", res)
    return {k: v for k, v in res.items() if k not in ("dias", "primeira_data", "reapresentados")} | {"dias_com_achado": len([d for d, v in dias.items() if v["total"]])}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
