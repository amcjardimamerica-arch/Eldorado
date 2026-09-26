"""PARA O CLAUDE — a cada 3 dias (titular, 26/09).

Os dois Pilotos levantam o MÍNIMO: link original da oportunidade e dados de partida. Quem finaliza — analisa,
valida ou descarta — é o Claude, na sessão de análise a cada 3 dias. Este módulo monta a fila dele:
    docs/dados/para_claude.json  ·  estado/para_claude/fila.json
Cada item: origem (Espião/Interceptador), tipo (edital/empresa/fonte), link original, página oficial (se
mapeada), dados mínimos, qualidade apurada pelo Interceptador, o parecer "como serve como fonte", e o
status: a_analisar | validada | descartada (os dois últimos só o Claude marca).
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from .nucleo import load_json, now_iso, write_json

ROOT = Path(__file__).resolve().parents[1]
FILA = ROOT / "estado/para_claude/fila.json"
PUB = ROOT / "docs/dados/para_claude.json"
INTERVALO_DIAS = 3


def montar() -> dict:
    fila = load_json(FILA) if FILA.exists() else {"itens": {}, "analises_do_claude": []}
    itens = fila.setdefault("itens", {})
    # 1) indícios do Espião (candidatas), com o que o Interceptador comprovou
    cand = (load_json(ROOT / "estado/piloto/candidatas_do_catalogo.json") or {}).get("candidatas") or []
    for c in cand:
        k = "cand:" + c["url"]
        it = itens.setdefault(k, {"origem": "Piloto - Espião", "tipo": "edital", "status": "a_analisar", "descoberto_em": c.get("descoberto_em")})
        it.update({"titulo": c.get("titulo"), "link_original": c.get("url"), "enquadramento": c.get("enquadramento"), "visto_em": c.get("visto_em")})
    # 2) o que o Interceptador estudou (registros com investigacao_ia)
    for arq in (ROOT / "dados/editais/extraidos").glob("*.json"):
        e = load_json(arq) or {}
        inv = e.get("investigacao_ia") or {}
        if not inv or not inv.get("em") or inv["em"] < "2026-09-26":
            continue
        chave = next((k for k, v in itens.items() if v.get("link_original") and v["link_original"] == e.get("url")), "edital:" + arq.stem)
        it = itens.setdefault(chave, {"origem": "Piloto - Interceptador", "tipo": "edital", "status": "a_analisar", "descoberto_em": inv["em"][:10]})
        campos = inv.get("campos") or {}
        it.update({"titulo": e.get("titulo") or it.get("titulo"), "link_original": e.get("url") or it.get("link_original"), "pagina_oficial": e.get("pagina_oficial"),
                   "dados_minimos": {k: v.get("valor") for k, v in campos.items() if v.get("comprovado") or v.get("dispensado")},
                   "faltou": [k for k, v in campos.items() if not (v.get("comprovado") or v.get("dispensado"))],
                   "qualidade": inv.get("qualidade"), "parecer_fonte": inv.get("parecer_fonte"), "estudado_em": inv["em"][:10]})
    # 3) empresas sem edital (fichas do Interceptador)
    fe = ROOT / "estado/interceptador/fontes_empresas.json"
    F = (load_json(fe) or {}) if fe.exists() else {}
    for nome, f in (F.get("fichas") or {}).items():
        it = itens.setdefault("empresa:" + nome, {"origem": "Piloto - Interceptador", "tipo": "empresa", "status": "a_analisar", "descoberto_em": str(f.get("em", ""))[:10]})
        it.update({"titulo": nome, "link_original": f.get("site_oficial"), "qualidade": f.get("qualidade"),
                   "dados_minimos": {k: v.get("valor") for k, v in (f.get("itens") or {}).items() if v.get("comprovado")}, "erro": f.get("erro")})
    ult = (fila.get("analises_do_claude") or [None])[-1]
    proxima = (date.fromisoformat(ult["em"][:10]) + timedelta(days=INTERVALO_DIAS)).isoformat() if ult else date.today().isoformat()
    fila["em"] = now_iso(); fila["proxima_analise_do_claude"] = proxima
    write_json(FILA, fila)
    pend = {k: v for k, v in itens.items() if v.get("status") == "a_analisar"}
    write_json(PUB, {"em": fila["em"], "regra": f"os Pilotos levantam o mínimo (link original + dados de partida); o Claude analisa, valida ou descarta a cada {INTERVALO_DIAS} dias",
                     "proxima_analise_do_claude": proxima, "a_analisar": len(pend),
                     "validadas": sum(1 for v in itens.values() if v.get("status") == "validada"), "descartadas": sum(1 for v in itens.values() if v.get("status") == "descartada"),
                     "itens": sorted(pend.values(), key=lambda x: (x.get("qualidade") != "validada", str(x.get("descoberto_em"))), reverse=False)[:200]})
    return {"a_analisar": len(pend), "proxima": proxima}
