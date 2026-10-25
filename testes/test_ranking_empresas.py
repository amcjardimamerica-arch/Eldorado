"""O ranking de empresas (titular, 25/10/2026: a aba estava zerada)."""
import sqlite3

from eldorado.base.painel.dados import _molde
from eldorado.base.painel.ranking import montar


def test_o_ranking_tem_todas_as_empresas_da_biblioteca():
    con = sqlite3.connect("file:dados/biblioteca.db?mode=ro", uri=True)
    r = montar(con, _molde)
    n = con.execute("SELECT COUNT(*) FROM empresa").fetchone()[0]
    assert r["total"] == n == len(r["empresas"]) > 0                                       # todas as empresas, nenhuma de fora
    assert r["listas"]["destinacao_tributaria"]["total"] + r["listas"]["patrocinio_privado"]["total"] == n
    trib = [e for e in r["empresas"] if e["origem"] == "destinação tributária"]
    assert [e["n_na_lista"] for e in trib] == list(range(1, len(trib) + 1))                 # as posições em ordem
    assert all(trib[i]["pontos_lista"] >= trib[i + 1]["pontos_lista"] for i in range(len(trib) - 1))
    assert all(e["pontuacao"]["porque"] for e in r["empresas"]) and r["catalogo_de_leis"]
