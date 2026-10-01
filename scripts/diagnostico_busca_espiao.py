#!/usr/bin/env python3
"""Diagnóstico da busca do Espião (01/10): resultados, trecho do buscador e leitura das páginas — no servidor."""
import json, sys, time
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
from src.piloto_busca import buscar, ler_pagina
CONS = ["edital assistência social organizações da sociedade civil Goiás 2026", "grupo empresarial instituto social chamada de projetos 2026",
        "patrocinadores festival goiânia 2026", "edital pessoa idosa organizações da sociedade civil inscrições", "fundação empresarial goiás edital projetos 2026"]
out = []
for c in CONS:
    t0 = time.time(); rs = buscar(c, 8) or []
    item = {"consulta": c, "resultados": len(rs), "com_trecho": sum(1 for r in rs if (r.get("trecho") or "").strip()),
            "buscador": sorted({str(r.get("buscador") or "") for r in rs}), "segundos_busca": round(time.time() - t0, 1), "paginas": []}
    for r in rs[:3]:
        t1 = time.time(); tx = ler_pagina(r["url"])
        item["paginas"].append({"url": r["url"][:120], "caracteres": len(tx or ""), "segundos": round(time.time() - t1, 1), "trecho_busca": (r.get("trecho") or "")[:80]})
    out.append(item)
(R / "biblioteca_alexandria/base/diagnostico_busca_espiao.json").write_text(json.dumps({"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "itens": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:3000])
