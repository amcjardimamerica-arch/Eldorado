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
sys.exit(0 if r.wasSuccessful() else 1)
