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
    assert [e["degrau"] for e in m["escada"]][:8] == ["1", "2", "P", "3", "4", "5", "6", "7"]  # a ponte BR depois da nuvem
    assert c["certidoes"] and len(fichas) == len(c["certidoes"])  # uma ficha por livro
    f = next(iter(fichas.values()))
    assert {"relatorio", "parecer", "repasse", "orientacao", "itens", "etapa", "degrau"} <= set(f)
    assert Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8").count("car-m-etapas") >= 2


def test_o_classificador_do_cartorio_e_a_janela_da_decisao():
    """26/10/2026 (titular): os dois medidores do Cartório (a escada e as 5 etapas com a classificação em dois ramos, no
    modo coletivo ou individual) e o 'Para a sua decisão' só numa janela da tela inicial, não inserido nas páginas."""
    from pathlib import Path

    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'id="c2-escada"' in p and 'id="c2-fluxo"' in p and 'id="c2-q"' in p  # os dois medidores e a busca
    assert "Fica no Eldorado" in p and "Vai ao Farol" in p and "6. A classificação" in p  # a etapa 6 com dois ramos
    assert "width:100vw;margin-left:calc(50% - 50vw)" in p  # de margem a margem
    assert 'id="c2-gaveta"' in p and "function dica(" in p and "function particulas(" in p  # a gaveta, a dica e o fluxo vivo
    assert 'fetch("dados/cartorio/"+encodeURIComponent(id)' in p  # a trajetória do livro
    assert 'id="v-relatorio-titular"' not in p and 'id="dec-janela"' in p  # a janela, não uma seção
    assert 'sessionStorage.getItem("eldorado-decisao")' in p and "naInicial()" in p  # só na inicial, uma vez por visita


def test_os_fluxos_e_o_tempo_na_etapa_no_cartorio():
    from eldorado.base.painel.cartorio import _fluxos

    ps = {
        "L1": [
            {"de": None, "para": "recepcao", "em": "2026-10-26T10:00:00+00:00"},
            {"de": "recepcao", "para": "certificacao", "em": "2026-10-20T10:00:00+00:00"},
        ]
    }
    f = _fluxos(ps, "2026-10-26T12:00:00+00:00")
    assert {"de": "chegada", "para": "recepcao", "sete_dias": 1, "um_dia": 1} in f and {
        "de": "recepcao",
        "para": "certificacao",
        "sete_dias": 1,
        "um_dia": 0,
    } in f
