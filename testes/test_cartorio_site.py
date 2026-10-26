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
    assert [e["degrau"] for e in m["escada"]][:8] == ["1", "2", "P", "3", "4", "5", "6", "7"]   # a ponte BR depois da nuvem
    assert c["certidoes"] and len(fichas) == len(c["certidoes"])                     # uma ficha por livro
    f = next(iter(fichas.values()))
    assert {"relatorio", "parecer", "repasse", "orientacao", "itens", "etapa", "degrau"} <= set(f)
    assert Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8").count("car-m-etapas") >= 2


def test_o_classificador_do_cartorio_e_a_janela_da_decisao():
    """26/10/2026 (titular): os dois medidores do Cartório (a escada e as 5 etapas com a classificação em dois ramos, no
    modo coletivo ou individual) e o 'Para a sua decisão' só numa janela da tela inicial, não inserido nas páginas."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'id="cls-escada"' in p and 'id="cls-etapas"' in p and 'id="cls-q"' in p                  # os dois medidores e a busca
    assert "Fica no Eldorado" in p and "Vai ao Farol" in p and "6. A classificação" in p            # a etapa 6 com dois ramos
    assert 'id="v-relatorio-titular"' not in p and 'id="dec-janela"' in p                          # a janela, não uma seção
    assert 'sessionStorage.getItem("eldorado-decisao")' in p and "naInicial()" in p                  # só na inicial, uma vez por visita
