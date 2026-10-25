"""A manutenção dos bancos e a busca por texto (plano C: sqlite-utils).

A busca por texto lê direto a Biblioteca no momento da busca (os títulos, os órgãos e os valores certificados): nenhum
índice nem cópia fora do banco relacional dos livros.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def otimizar(dados: Path = Path("dados")) -> dict[str, Any]:
    """ANALYZE e otimização de cada banco (o tamanho antes e depois)."""
    import sqlite_utils
    r = {}
    for p in sorted(dados.glob("*.db")):
        antes = p.stat().st_size
        db = sqlite_utils.Database(p)
        db.analyze()
        db.execute("PRAGMA optimize")
        db.vacuum()
        db.conn.close()
        r[p.name] = {"antes_kb": antes // 1024, "depois_kb": p.stat().st_size // 1024}
    return r


def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", (t or "").lower()) if unicodedata.category(c) != "Mn")


def buscar(texto: str, dados: Path = Path("dados"), limite: int = 50) -> list[dict[str, Any]]:
    """A busca por texto (sem acento, sem maiúsculas) lida DIRETO na Biblioteca, no momento da busca: nenhum índice ou
    cópia fora do banco relacional dos livros (a regra da titular, 24/10/2026)."""
    p = dados / "biblioteca.db"
    if not p.exists() or not texto.strip():
        return []
    palavras = _sem_acento(texto).split()
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        certs: dict[str, list[str]] = {}
        for lid, valor in con.execute("SELECT livro_id, valor FROM certidao WHERE situacao = 'comprovado' AND valor IS NOT NULL"):
            certs.setdefault(lid, []).append(valor)
        saida = []
        for lid, t, o in con.execute("SELECT id, titulo, orgao FROM livro WHERE situacao NOT IN ('excluido', 'unido') ORDER BY atualizado_em DESC"):
            alvo = _sem_acento(f"{t} {o} {' '.join(certs.get(lid, []))}")
            if all(w in alvo for w in palavras):
                saida.append({"id": lid, "titulo": t, "orgao": o})
                if len(saida) >= limite:
                    break
        return saida
    finally:
        con.close()
