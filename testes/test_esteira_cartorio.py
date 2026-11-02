"""R37 (titular, 02/11/2026): a esteira do Cartório — o livro completo (ou sem nada a buscar) não fica parado na preparação."""
import sqlite3
from pathlib import Path

from eldorado.base.cartorio import esteira


def test_a_esteira_esta_na_passagem():
    t = Path("workflows/passagem.toml").read_text(encoding="utf-8")
    assert 'tipo = "eldorado.base.cartorio.esteira:no_organizar_esteira"' in t


def test_o_completo_sai_da_preparacao(monkeypatch):
    b = sqlite3.connect(":memory:")
    b.executescript("""
    CREATE TABLE livro(id TEXT, situacao TEXT); CREATE TABLE livro_dados(livro_id TEXT, inscricao_fim TEXT, validacao TEXT);
    CREATE TABLE passaporte(livro_id TEXT, fase TEXT); CREATE TABLE uniao(livro_que_fica TEXT, livro_unido TEXT);
    CREATE TABLE certidao(livro_id TEXT, item TEXT, situacao TEXT);
    INSERT INTO livro VALUES ('L-completo','em trabalho'),('L-falta','em trabalho'),('L-velho','em trabalho');
    INSERT INTO livro_dados VALUES ('L-completo','2099-01-01','aprovado'),('L-falta','2099-01-01','aprovado'),('L-velho','2000-01-01','aprovado');
    INSERT INTO passaporte VALUES ('L-completo','preparacao'),('L-falta','preparacao'),('L-velho','preparacao');
    """)
    from eldorado.base.missao import itens as I
    b.executemany("INSERT INTO certidao VALUES ('L-completo',?, 'comprovado')", [(k,) for k in I.DOZE])

    class F:   # o Interceptador ainda tem o que buscar no L-falta
        id = "L-falta"
    monkeypatch.setattr("eldorado.motores.pilotos.interceptador.fila", lambda con, hoje: [F()])
    c = esteira.candidatos(b, "2026-11-02")
    assert c == {"encerrados": ["L-velho"], "completos": ["L-completo"], "sem_o_que_buscar": []}


def test_o_interceptador_grava_o_degrau_da_escada():
    t = Path("eldorado/motores/pilotos/interceptador.py").read_text(encoding="utf-8")
    assert '"escada": {"motor": "interceptador", "fonte": ABORDAGENS[n],' in t
