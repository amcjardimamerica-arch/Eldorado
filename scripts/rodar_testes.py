#!/usr/bin/env python3
"""Bateria de testes SEM os módulos em quarentena (config/testes_quarentena.json) — portão dos fluxos 00 e 01."""
import json, sys, unittest
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
Q = set((json.loads((RAIZ / "config/testes_quarentena.json").read_text(encoding="utf-8")).get("modulos") or {}).keys())
nomes = sorted(p.stem for p in (RAIZ / "tests").glob("test_*.py") if p.stem not in Q)
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(f"tests.{n}") for n in nomes)
print(f"{len(nomes)} módulos (quarentena: {len(Q)})", flush=True)
r = unittest.TextTestRunner(verbosity=1).run(suite)
# no GitHub, cada falha vira ANOTAÇÃO da execução (legível pela API e pela análise do sistema, sem baixar o registro)
for caso, tb in (r.failures + r.errors)[:15]:
    ult = [l for l in tb.strip().splitlines() if l.strip()][-1][:180].replace("\n", " ")
    print(f"::error title=teste falhou::{caso.id()} — {ult}", flush=True)
sys.exit(0 if r.wasSuccessful() else 1)
