"""08/11/2026 (parecer da etapa 8): o Comandante contra a ordem fixa na MESMA unidade (o motor-dia distinto). Antes,
a média das decisões repetidas (até 484 do mesmo motor num dia) mostrava +25,5 pontos que não existiam."""
import sqlite3
from datetime import datetime, timedelta, timezone

from eldorado.base.aprendizado.avaliar import comparacao


def test_decisoes_repetidas_nao_inflam_o_comandante():
    d = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    b, c = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    b.execute("CREATE TABLE achado(motor TEXT, encontrado_em TEXT, decisao TEXT)")
    c.executescript("CREATE TABLE comandante_decisao(etapa TEXT, alvo TEXT, em TEXT, recompensa REAL);"
                    "CREATE TABLE execucao_motor(motor TEXT, inicio TEXT)")
    for m in ("a", "b", "c", "d"):
        c.execute("INSERT INTO execucao_motor VALUES (?, ?)", (m, d + "T03:00:00+00:00"))
    b.execute("INSERT INTO achado VALUES ('a', ?, 'aceito')", (d,))
    c.executemany("INSERT INTO comandante_decisao VALUES ('coleta', ?, ?, ?)",
                  [("a", d + "T10:00:00+00:00", 1.0)] * 50 + [("b", d + "T10:00:00+00:00", 0.0)])
    r = comparacao(b, c)
    assert r["unidade"] == "motor-dia" and r["decisoes"] == 2
    assert r["comandante"] == 0.5 and r["ordem_fixa"] == 0.25 and r["sorteio"] == 0.25   # antes: 50/51 = 0,98
