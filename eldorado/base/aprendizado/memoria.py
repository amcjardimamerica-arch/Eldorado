"""A memória do Aprendizado (a etapa A6): tudo o que o sistema viveu, pesquisável no Arquivo do Cérebro (titular, 25/10/2026).

O conceito do Hermes (a memória SQLite com busca FTS5), com o índice trigram eleito no estudo (5 de 5 no top-5, 1,3 ms;
acha partes de palavra, importante em português). A cada passagem, o que é novo no Cérebro entra na memória (por eventos);
o que passou de 30 dias expira (o temporário do Cérebro). A busca ordena por relevância (bm25)."""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# (a tabela, a referência, o texto, a data): o que o Cérebro registra em texto
# (a tabela, a referência, o texto, a data), das mais valiosas para a IA às menos; cada uma com a sua cota por passagem
FONTES = [
    (
        "comandante_decisao",
        "id",
        "coalesce(etapa,'')||' · '||coalesce(acao,'')||' · '||coalesce(alvo,'')||' · '||coalesce(motivo,'')||' · '||coalesce(resultado,'')",
        "em",
    ),
    ("aprendizado_permanente", "id", "coalesce(modulo,'')||' · '||coalesce(o_que,'')", "promovido_em"),
    ("regra", "id", "coalesce(tema,'')||' · '||coalesce(regra,'')", "data"),
    ("espiao_missao", "id", "coalesce(familia,'')||' · '||coalesce(consulta,'')||' · '||coalesce(motivos,'')", "em"),
    ("decisao_pertinencia", "id", "coalesce(etapa,'')||' · '||coalesce(decisao,'')||' · '||coalesce(motivo,'')||' · '||coalesce(regra,'')", "em"),
    ("alarme", "id", "coalesce(modulo,'')||' · '||coalesce(mensagem,'')", "aberto_em"),
    ("medicao", "marcador||'@'||em", "coalesce(marcador,'')||' · '||coalesce(motivo,'')", "em"),
    ("execucao_passo", "execucao||':'||passo", "coalesce(no,'')||' · '||coalesce(estado,'')||' · '||coalesce(saida,'')", "em"),
]
DIAS = 30
POR_PASSAGEM = 20000


def _existe(con: sqlite3.Connection, tabela: str, coluna: str | None = None) -> bool:
    cols = {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}
    return bool(cols) and (coluna is None or coluna in cols)


def novos(con: sqlite3.Connection, limite: int = POR_PASSAGEM) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """O que é novo no Cérebro desde a última passagem (pelo ponteiro de cada tabela)."""
    ponteiro = dict(con.execute("SELECT tabela, ultimo FROM memoria_ponteiro")) if _existe(con, "memoria_ponteiro") else {}
    corte = (datetime.now(timezone.utc) - timedelta(days=DIAS)).isoformat()
    saida, novos_ponteiros = [], {}
    for tabela, ref, texto, em in FONTES:
        if len(saida) >= limite or not _existe(con, tabela, em):
            continue
        desde = max(ponteiro.get(tabela, ""), corte)
        cota = min(limite - len(saida), max(limite // len(FONTES), 1000))
        for r, t, e in con.execute(f"SELECT {ref}, {texto}, {em} FROM {tabela} WHERE {em} > ? ORDER BY {em} LIMIT ?", (desde, cota)):
            if t and t.strip(" ·"):
                saida.append({"tabela": tabela, "ref": str(r), "texto": t[:4000], "em": e})
            novos_ponteiros[tabela] = e
    return saida, novos_ponteiros


def expirados(con: sqlite3.Connection, limite: int = POR_PASSAGEM) -> list[dict[str, str]]:
    corte = (datetime.now(timezone.utc) - timedelta(days=DIAS)).isoformat()
    return [{"tabela": t, "ref": r} for t, r in con.execute("SELECT tabela, ref FROM memoria WHERE em < ? LIMIT ?", (corte, limite))]


def buscar(con: sqlite3.Connection, consulta: str, limite: int = 10) -> tuple[list[dict[str, Any]], float]:
    """A busca por relevância (bm25): os termos de 3 letras ou mais, em qualquer parte da palavra (trigram)."""
    termos = [w.replace('"', "") for w in consulta.split() if len(w) >= 3]
    if not termos:
        return [], 0.0
    t0 = time.perf_counter()
    linhas = con.execute(
        "SELECT tabela, ref, snippet(memoria, 2, '[', ']', '…', 40), em, substr(texto, 1, 400) FROM memoria "
        "WHERE memoria MATCH ? ORDER BY bm25(memoria) LIMIT ?",
        (" OR ".join(f'"{t}"' for t in termos), limite),
    ).fetchall()
    return [{"tabela": a, "ref": b, "trecho": c, "em": d, "texto": t} for a, b, c, d, t in linhas], round((time.perf_counter() - t0) * 1000, 2)


def no_memorizar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Aprendizado, A6): o que é novo entra na memória; o que passou de 30 dias expira."""
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if not p.exists():
        return [{"memorizados": 0}]
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        if not _existe(con, "memoria"):
            return [{"memorizados": 0, "motivo": "o Cérebro ainda não está na versão 10"}]
        docs, ponteiros = novos(con)
        velhos = expirados(con)
    finally:
        con.close()
    for d in docs:
        contexto.diario.emitir("memoria.registrada", "aprendizado", d)
    for v in velhos:
        contexto.diario.emitir("memoria.expirada", "aprendizado", v)
    for tabela, ultimo in ponteiros.items():
        contexto.diario.emitir("memoria.ponteiro", "aprendizado", {"tabela": tabela, "ultimo": ultimo})
    return [{"memorizados": len(docs), "expirados": len(velhos)}]
