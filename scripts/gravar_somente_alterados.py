#!/usr/bin/env python3
"""GRAVAR SOMENTE O QUE ESTE FLUXO ALTEROU (titular, 15/10/2026 — análise do sistema, ciclo 5).

Defeito medido: a análise das 14:43 reaplicou a ÁRVORE INTEIRA que tinha copiado às 14:03 e apagou a coleta que o
comando único gravou às 14:37 (docs/dados/maestro.json e comando.json voltaram às 12:46). O mesmo mecanismo existia no
fluxo 22. Regra nova: cada fluxo grava só os arquivos que ELE mudou, sempre por cima do main MAIS RECENTE.

    python scripts/gravar_somente_alterados.py salvar              # ao fim do trabalho: guarda os arquivos alterados
    python scripts/gravar_somente_alterados.py aplicar "mensagem"   # parte do main atual e grava só esses arquivos
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDA = Path("/tmp/alterados_pelo_fluxo")
AREAS = ["biblioteca_alexandria", "dados", "estado", "docs/dados", "docs/dashboard-dados.js", "docs/relatorios"]


def _git(*a, ok=False) -> str:
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    if r.returncode and not ok:
        raise RuntimeError(f"git {' '.join(a)}: {r.stderr.strip()[:300]}")
    return r.stdout


def salvar() -> dict:
    mud = [l for l in _git("status", "--porcelain", "--untracked-files=all", "--", *AREAS).splitlines() if l.strip()]
    alterados, apagados = [], []
    for l in mud:
        caminho = l[3:].split(" -> ")[-1].strip().strip('"')
        (apagados if l[:2].strip() == "D" else alterados).append(caminho)
    if GUARDA.exists():
        shutil.rmtree(GUARDA)
    for c in alterados:
        d = GUARDA / "arquivos" / c
        d.parent.mkdir(parents=True, exist_ok=True)
        if (ROOT / c).is_file():
            shutil.copy2(ROOT / c, d)
    m = {"alterados": alterados, "apagados": apagados}
    GUARDA.mkdir(parents=True, exist_ok=True)
    (GUARDA / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"guardados {len(alterados)} alterado(s) e {len(apagados)} apagado(s)")
    return m


def aplicar(msg: str, tentativas: int = 6) -> bool:
    m = json.loads((GUARDA / "manifesto.json").read_text(encoding="utf-8"))
    if not m["alterados"] and not m["apagados"]:
        print("nada a gravar"); return True
    for i in range(1, tentativas + 1):
        _git("fetch", "-q", "origin", "main")
        _git("reset", "-q", "--hard", "origin/main")                 # sempre o main MAIS RECENTE
        for c in m["alterados"]:
            o = GUARDA / "arquivos" / c
            if o.is_file():
                (ROOT / c).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(o, ROOT / c)
        for c in m["apagados"]:
            if (ROOT / c).exists():
                _git("rm", "-q", "--", c, ok=True)
        _git("add", "--", *[c for c in m["alterados"] if (ROOT / c).exists()], ok=True)
        if not _git("diff", "--cached", "--name-only"):
            print("nada mudou em relação ao main"); return True
        _git("commit", "-q", "-m", msg)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=ROOT).returncode == 0:
            print(f"gravado na tentativa {i}: só os {len(m['alterados'])} arquivo(s) deste fluxo"); return True
        time.sleep(5 * i)
    print("REGISTRO FALHOU — nenhum arquivo de outro fluxo foi sobrescrito"); return False


if __name__ == "__main__":
    if sys.argv[1:2] == ["salvar"]:
        salvar()
    elif sys.argv[1:2] == ["aplicar"]:
        sys.exit(0 if aplicar(sys.argv[2] if len(sys.argv) > 2 else "dados") else 1)
    else:
        print(__doc__)
