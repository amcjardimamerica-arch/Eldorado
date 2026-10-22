"""O expurgo físico pela análise externa (titular, 22/10/2026): "o sistema não apaga nada, mas o Claude pode apagar e
fazer tudo. A automação é travada; a análise externa pode fazer o que precisar."

A automação (o gravador e todos os módulos) continua sem poder apagar: as travas do banco ficam. Este expurgo é uma
ferramenta da análise externa, chamada por comando: numa transação única, guarda as travas, desliga, apaga os livros e
tudo o que depende deles, recria as travas exatamente como eram e registra o expurgo (que nada altera depois). Se
qualquer passo falhar, nada muda.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

LIGACOES_LIVRO = ("livro_id", "livro_que_fica", "livro_unido")


def _tabelas_dependentes(con: sqlite3.Connection) -> list[tuple[str, str]]:
    """(tabela, coluna) que guardam o identificador de um livro, descobertas pelo próprio esquema."""
    saida = []
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'busca%'"):
        for col in con.execute(f"PRAGMA table_info({t})"):
            if col[1] in LIGACOES_LIVRO:
                saida.append((t, col[1]))
    return saida


def _sem_travas(con: sqlite3.Connection, tabelas: set[str]) -> list[str]:
    filtro = ",".join("?" * len(tabelas))
    linhas = con.execute(f"SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name IN ({filtro})", tuple(tabelas)).fetchall()
    for nome, _ in linhas:
        con.execute(f'DROP TRIGGER "{nome}"')
    return [sql for _, sql in linhas]


def expurgar(biblioteca: sqlite3.Connection, cerebro: sqlite3.Connection | None, ids: list[str], motivo: str, por: str = "análise externa (Claude)") -> dict:
    if not ids:
        return {"livros": 0, "linhas": 0, "por_tabela": {}}
    if len(motivo.strip()) < 10:
        raise ValueError("o expurgo exige o motivo")
    dependentes = _tabelas_dependentes(biblioteca)
    tabelas = {t for t, _ in dependentes} | {"livro"}
    marca = ",".join("?" * len(ids))
    por_tabela: dict[str, int] = {}
    biblioteca.execute("BEGIN IMMEDIATE")
    try:
        travas = _sem_travas(biblioteca, tabelas)
        for t, col in dependentes:
            if t == "livro":
                continue
            n = biblioteca.execute(f"DELETE FROM {t} WHERE {col} IN ({marca})", ids).rowcount
            if n:
                por_tabela[f"{t}.{col}"] = por_tabela.get(f"{t}.{col}", 0) + n
        por_tabela["livro"] = biblioteca.execute(f"DELETE FROM livro WHERE id IN ({marca})", ids).rowcount
        for sql in travas:
            biblioteca.execute(sql)
        linhas = sum(por_tabela.values())
        biblioteca.execute("INSERT INTO expurgo_externo(em, por, motivo, livros, linhas, ids) VALUES (?,?,?,?,?,?)",
                           (datetime.now(timezone.utc).isoformat(timespec="seconds"), por, motivo, por_tabela["livro"], linhas, json.dumps(ids)))
        biblioteca.execute("COMMIT")
    except Exception:
        biblioteca.execute("ROLLBACK")
        raise
    if cerebro is not None:                                  # os rótulos da rede neural sobre esses livros
        cerebro.execute("BEGIN IMMEDIATE")
        try:
            travas = _sem_travas(cerebro, {"rotulo"})
            por_tabela["cerebro.rotulo"] = cerebro.execute(f"DELETE FROM rotulo WHERE referencia IN ({marca})", ids).rowcount
            for sql in travas:
                cerebro.execute(sql)
            cerebro.execute("COMMIT")
        except Exception:
            cerebro.execute("ROLLBACK")
            raise
    return {"livros": por_tabela["livro"], "linhas": sum(por_tabela.values()), "por_tabela": por_tabela}
