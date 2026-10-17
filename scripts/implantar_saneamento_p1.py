#!/usr/bin/env python3
"""IMPLANTAÇÃO do saneamento dos motores (revisão da Parte 1 · Goiás · 10/10/2026). Um comando, idempotente.

    python scripts/implantar_saneamento_p1.py              # importa a revisão, testa e mostra o efeito na base
    python scripts/implantar_saneamento_p1.py --verificar  # só testa e mostra o efeito, sem gravar nada

Passos:
  1. importa os 340 vereditos e as 12 certidões da revisão (scripts/importar_revisao_abertas.py);
  2. roda tests/test_saneamento_motores.py (gabarito de 338 registros: nenhum útil pode ser atingido);
  3. simula o saneamento na base inteira (dados/oportunidades/oportunidades.jsonl) e imprime o que mudaria.
A caixa de abertas (docs/dados/abertas.json) passa a sair saneada na próxima geração do painel do ciclo normal.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv: list[str]) -> int:
    verificar = "--verificar" in argv
    import importlib.util
    spec = importlib.util.spec_from_file_location("importar_revisao_abertas", ROOT / "scripts/importar_revisao_abertas.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    importar = mod.importar
    rel = importar(ROOT / "biblioteca_alexandria/livros/_acervo/revisoes/abertas_p1_go_2026_10_10", "P1-GO-2026-10-10", gravar=not verificar)
    print("1) revisão importada:" if not verificar else "1) revisão conferida (nada gravado):",
          json.dumps({k: rel[k] for k in ("lidos", "vereditos", "certidoes", "derivadas", "selos_das_certidoes")}, ensure_ascii=False))
    t = subprocess.run([sys.executable, "scripts/testar.py", "--comando", f"{sys.executable} -m unittest tests.test_saneamento_motores"], cwd=ROOT, capture_output=True, text=True)
    print("2) testes do saneamento:", "OK" if t.returncode == 0 else "FALHOU\n" + t.stderr[-2000:])
    if t.returncode:
        return 1
    from src.nucleo import carregar_oportunidades
    from src import saneamento_motores as S
    S.limpar_cache()
    ops = list(carregar_oportunidades().values())
    dups = S.agrupar_duplicatas(ops)
    regras, desc = Counter(), Counter()
    for o in ops:
        s = S.sanear_registro(o, date.today(), dups)
        regras.update(s["regras"])
        if s["descartar"]:
            desc[s["descartar"].split(":")[0]] += 1
    print("3) efeito na base:", json.dumps({"registros": len(ops), "duplicatas": len(dups), "regras": dict(regras),
                                             "descartes_da_caixa": dict(desc)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
