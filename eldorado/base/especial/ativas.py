"""R61 (titular, 18/11 e 25/11/2026): a pessoa física sai do cadastro de empresas por EXCLUSÃO LÓGICA — a linha fica no
banco (R35: as empresas ficam na Biblioteca) e nenhuma tela, ranking, busca do Espião ou vínculo a lê."""
from __future__ import annotations

import sqlite3


def tem_exclusao(con: sqlite3.Connection) -> bool:
    try:
        return "excluida_em" in {r[1] for r in con.execute("PRAGMA table_info(empresa)")}
    except sqlite3.Error:
        return False


def ativas(con: sqlite3.Connection, alias: str = "") -> str:
    """A condição das empresas ativas (para depois de um WHERE); «1=1» no banco antigo, sem a coluna."""
    return f"{alias + '.' if alias else ''}excluida_em IS NULL" if tem_exclusao(con) else "1=1"
