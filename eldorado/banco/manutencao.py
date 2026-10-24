"""A manutenção dos bancos e a busca por texto (plano C: sqlite-utils).

A busca por texto é um ÍNDICE DERIVADO (FTS5) em biblioteca_busca.db, refeito a partir da Biblioteca: os títulos, os
órgãos e os valores certificados. Os dados continuam vindo só dos eventos; o índice nunca é fonte de verdade.
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


def indexar(dados: Path = Path("dados")) -> int:
    """Refaz o índice de busca por texto da Biblioteca (biblioteca_busca.db)."""
    import sqlite_utils
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    certs: dict[str, list[str]] = {}
    for lid, item, valor in bib.execute("SELECT livro_id, item, valor FROM certidao WHERE situacao = 'comprovado' AND valor IS NOT NULL"):
        certs.setdefault(lid, []).append(f"{item}: {valor}")
    linhas = [{"id": lid, "titulo": t or "", "orgao": o or "", "certidoes": " | ".join(certs.get(lid, []))}
              for lid, t, o in bib.execute("SELECT id, titulo, orgao FROM livro WHERE situacao <> 'excluido'")]
    bib.close()
    destino = dados / "biblioteca_busca.db"
    destino.unlink(missing_ok=True)
    db = sqlite_utils.Database(destino)
    db["livro"].insert_all(linhas, pk="id")
    db["livro"].enable_fts(["titulo", "orgao", "certidoes"], tokenize="unicode61 remove_diacritics 2")
    db.conn.close()
    return len(linhas)


def buscar(texto: str, dados: Path = Path("dados"), limite: int = 50) -> list[dict[str, Any]]:
    """A busca por texto (sem acento, sem maiúsculas); [] sem o índice."""
    p = dados / "biblioteca_busca.db"
    if not p.exists():
        return []
    import sqlite_utils
    db = sqlite_utils.Database(p)
    try:
        return [dict(r) for r in db["livro"].search(texto, limit=limite, columns=["id", "titulo", "orgao"])]
    finally:
        db.conn.close()
