"""Atalho: python scripts/unificar_livros.py [--verificar] → src/unificar_livros.py (uma oportunidade = um livro)."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.unificar_livros import unificar  # noqa: E402

if __name__ == "__main__":
    print(json.dumps(unificar(gravar="--verificar" not in sys.argv)["resumo"], ensure_ascii=False, indent=1))
