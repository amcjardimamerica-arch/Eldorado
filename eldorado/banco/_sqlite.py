"""Abertura padronizada dos bancos SQLite: configurações medidas, criação do esquema, versão e integridade."""
from __future__ import annotations

import sqlite3
from pathlib import Path


class EsquemaIncompativel(Exception):
    pass


def abrir(caminho: str | Path, ddl: str, versao: int) -> sqlite3.Connection:
    """Abre (ou cria) o banco. Na criação, aplica o esquema e grava a versão; depois, exige a versão esperada."""
    p = str(caminho)
    if p != ":memory:":
        Path(p).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p, isolation_level=None, check_same_thread=False)
    con.row_factory = sqlite3.Row
    for pragma in ("journal_mode=WAL", "synchronous=NORMAL", "foreign_keys=ON", "mmap_size=268435456", "temp_store=MEMORY"):
        con.execute(f"PRAGMA {pragma}")
    atual = con.execute("PRAGMA user_version").fetchone()[0]
    if atual == 0:
        con.executescript(ddl)
        con.execute(f"PRAGMA user_version={versao}")
        con.execute("PRAGMA foreign_keys=ON")
    elif atual != versao:
        con.close()
        raise EsquemaIncompativel(f"{p}: esquema na versão {atual}, esperada {versao} (rode a migração)")
    return con


def integridade(con: sqlite3.Connection) -> bool:
    return con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def colunas(con: sqlite3.Connection, tabela: str) -> set[str]:
    return {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}
