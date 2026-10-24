"""As análises sobre os bancos (plano C: DuckDB): o rendimento de cada motor, o funil do Cartório, os achados por dia.
O DuckDB lê os bancos SQLite direto (só leitura), sem copiar nada."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _con(dados: Path):
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    for nome in ("biblioteca", "cerebro", "especial"):
        p = dados / f"{nome}.db"
        if p.exists():
            con.execute(f"ATTACH '{p}' AS {nome} (TYPE sqlite, READ_ONLY)")
    return con


def relatorio(dados: Path = Path("dados"), dias: int = 7) -> dict[str, Any]:
    """Pelo DuckDB; sem a extensão de leitura de SQLite (ela é baixada no primeiro uso), as mesmas consultas no SQLite."""
    try:
        con = _con(dados)
    except Exception:  # noqa: BLE001 — sem a extensão: a reserva no SQLite
        return _relatorio_sqlite(dados, dias)
    try:
        def q(sql: str) -> list[dict[str, Any]]:
            cur = con.execute(sql)
            nomes = [c[0] for c in cur.description]
            return [dict(zip(nomes, r, strict=True)) for r in cur.fetchall()]
        return {
            "rendimento_por_motor": q(f"""SELECT motor, COUNT(*) AS execucoes, SUM(COALESCE(achados, 0)) AS achados,
                SUM(CASE WHEN erro IS NOT NULL THEN 1 ELSE 0 END) AS erros FROM cerebro.execucao_motor
                WHERE inicio >= strftime(now() - INTERVAL {int(dias)} DAY, '%Y-%m-%d') GROUP BY motor ORDER BY achados DESC"""),
            "funil_do_cartorio": q("SELECT fase, COUNT(*) AS livros FROM biblioteca.passaporte GROUP BY fase ORDER BY livros DESC"),
            "achados_por_dia": q(f"""SELECT encontrado_em AS dia, COUNT(*) AS achados, SUM(CASE WHEN decisao = 'aceito' THEN 1 ELSE 0 END) AS aceitos
                FROM biblioteca.achado WHERE encontrado_em >= strftime(now() - INTERVAL {int(dias)} DAY, '%Y-%m-%d') GROUP BY 1 ORDER BY 1"""),
            "origem_dos_livros": q("SELECT COALESCE(origem, 'sem') AS origem, COUNT(*) AS livros FROM biblioteca.livro_dados GROUP BY 1 ORDER BY 2 DESC"),
        }
    finally:
        con.close()


def _relatorio_sqlite(dados: Path, dias: int) -> dict[str, Any]:
    import sqlite3
    con = sqlite3.connect(":memory:")
    for nome in ("biblioteca", "cerebro", "especial"):
        if (dados / f"{nome}.db").exists():
            con.execute(f"ATTACH 'file:{dados / (nome + '.db')}?mode=ro' AS {nome}")
    desde = f"date('now', '-{int(dias)} day')"

    def q(sql: str) -> list[dict[str, Any]]:
        cur = con.execute(sql)
        nomes = [c[0] for c in cur.description]
        return [dict(zip(nomes, r, strict=True)) for r in cur.fetchall()]
    try:
        return {
            "rendimento_por_motor": q(f"""SELECT motor, COUNT(*) AS execucoes, SUM(COALESCE(achados, 0)) AS achados,
                SUM(CASE WHEN erro IS NOT NULL THEN 1 ELSE 0 END) AS erros FROM cerebro.execucao_motor WHERE inicio >= {desde}
                GROUP BY motor ORDER BY achados DESC"""),
            "funil_do_cartorio": q("SELECT fase, COUNT(*) AS livros FROM biblioteca.passaporte GROUP BY fase ORDER BY livros DESC"),
            "achados_por_dia": q(f"""SELECT encontrado_em AS dia, COUNT(*) AS achados, SUM(CASE WHEN decisao = 'aceito' THEN 1 ELSE 0 END) AS aceitos
                FROM biblioteca.achado WHERE encontrado_em >= {desde} GROUP BY 1 ORDER BY 1"""),
            "origem_dos_livros": q("SELECT COALESCE(origem, 'sem') AS origem, COUNT(*) AS livros FROM biblioteca.livro_dados GROUP BY 1 ORDER BY 2 DESC"),
        }
    finally:
        con.close()
