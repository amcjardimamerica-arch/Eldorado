"""O Cartório no site ligado aos dados (titular, 25/10/2026: a página estava estática)."""
import shutil
import sqlite3
from pathlib import Path

from eldorado.base.painel.cartorio import montar


def test_o_cartorio_tem_os_mostradores_e_a_ficha_de_cada_livro(tmp_path):
    shutil.copy("dados/biblioteca.db", tmp_path / "b.db")
    from eldorado.banco.biblioteca.esquema import abrir
    abrir(tmp_path / "b.db").close()
    c, fichas = montar(sqlite3.connect(tmp_path / "b.db"), None)
    m = c["mostradores"]
    assert [e["id"] for e in m["etapas"]] == ["recepcao", "certificacao", "preparacao", "validacao", "analise externa"]
    assert [e["degrau"] for e in m["escada"]][:7] == [str(i) for i in range(1, 8)]
    assert c["certidoes"] and len(fichas) == len(c["certidoes"])                     # uma ficha por livro
    f = next(iter(fichas.values()))
    assert {"relatorio", "parecer", "repasse", "orientacao", "itens", "etapa", "degrau"} <= set(f)
    assert Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8").count("car-m-etapas") >= 2
