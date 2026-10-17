"""Trava de isolamento da bateria (17/10/2026).

Os testes gravam em livros, estado/ e docs/dados. Por isso só rodam numa cópia:
  - a cópia temporária criada por scripts/testar.py (tem o arquivo .copia_de_teste na raiz); ou
  - um git worktree separado (.git é arquivo, não pasta), como no fluxo monitoramento-diario.
No repositório principal (.git é pasta) a bateria recusa e explica o comando certo.
"""
import os
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
_NA_COPIA = (_RAIZ / ".copia_de_teste").exists() or os.environ.get("ELDORADO_COPIA_DE_TESTE") == "1"
_REPO_PRINCIPAL = (_RAIZ / ".git").is_dir()

if _REPO_PRINCIPAL and not _NA_COPIA and os.environ.get("ELDORADO_PERMITIR_REPO_REAL") != "1":
    raise RuntimeError(
        "A bateria não roda no repositório real: os testes gravam nos dados. "
        "Use:  python3 scripts/testar.py   (roda numa cópia temporária e confere que nada mudou)."
    )
