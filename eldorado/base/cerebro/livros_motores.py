"""Os motores de cada livro e as pesquisas já feitas (comum ao encaminhamento e à vigilância dos sites originais; antes,
os dois se importavam um ao outro: o parecer do conselho, item 6)."""
from __future__ import annotations

import sqlite3


def motores_do_livro(con: sqlite3.Connection, livro: str) -> list[str]:
    """Os motores que trouxeram o livro, pelo nome de hoje (o nome anterior aponta para o motor que o reúne)."""
    from ...motores.canal.motor import apelidos
    ap = apelidos()
    nomes = [ap.get(r[0], r[0]) for r in con.execute("SELECT DISTINCT motor FROM achado WHERE livro_id=? AND motor NOT IN ('interceptador', 'espiao') "
                                                     "ORDER BY motor", (livro,))]
    return list(dict.fromkeys(nomes))


def ja_pesquisado(con: sqlite3.Connection, livro: str, motor: str) -> bool:  # noqa: D103
    return con.execute("SELECT 1 FROM tentativa WHERE livro_id=? AND fase='preparacao' AND ferramenta=?", (livro, f"motor {motor}")).fetchone() is not None
