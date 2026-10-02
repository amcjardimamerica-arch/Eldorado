"""ARMAZENAMENTO LEVE (titular, 02/10/2026) — compacta a base de oportunidades sem perder informação.

- campo qualidade: listas só com os códigos (rótulos voltam do catálogo na leitura — qualidade.expandir);
- JSON sem espaços supérfluos.
Medido em 02/10: 66,4 MB → 52,4 MB (−21%). Idempotente: rodar de novo não muda nada. Grava num arquivo temporário e troca
de uma vez (uma falha no meio não corrompe a base). Relatórios do maestro guardam só 30 dias; o livro-razão é mensal e gz.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dados/oportunidades/oportunidades.jsonl"


def run(base: Path | None = None) -> dict:
    from .qualidade import compactar
    base = base or BASE
    if not base.exists():
        return {"registros": 0}
    antes = base.stat().st_size; n = 0; tmp = base.with_suffix(".jsonl.tmp")
    with base.open(encoding="utf-8") as ent, tmp.open("w", encoding="utf-8") as sai:
        for l in ent:
            if not l.strip():
                continue
            try:
                r = json.loads(l)
            except ValueError:
                sai.write(l if l.endswith("\n") else l + "\n"); continue        # linha estranha: preservada como está
            if "qualidade" in r:
                r["qualidade"] = compactar(r["qualidade"])
            sai.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"); n += 1
    os.replace(tmp, base)
    depois = base.stat().st_size
    return {"registros": n, "antes_mb": round(antes / 1e6, 1), "depois_mb": round(depois / 1e6, 1), "economia_pct": round(100 * (1 - depois / max(1, antes)))}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
