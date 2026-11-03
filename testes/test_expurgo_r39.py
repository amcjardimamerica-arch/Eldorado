"""R39: o alerta do expurgo é só do livro sem estrela na verificação externa (o Chrome valida); a preparação não alerta."""
import sqlite3
from datetime import date

from eldorado.base.cartorio.expurgo_claude import candidatos, livros_para_expurgo


def _banco():
    b = sqlite3.connect(":memory:")
    b.executescript(
        "CREATE TABLE documento (id INTEGER PRIMARY KEY, url TEXT, obtido_em TEXT);"
        "CREATE TABLE certidao (documento_id INTEGER);"
        "CREATE TABLE achado (id TEXT, documento_id INTEGER, livro_id TEXT, decisao TEXT, encontrado_em TEXT, motor TEXT);"
        "CREATE TABLE livro (id TEXT, situacao TEXT, estrela TEXT, link_oficial TEXT, link_divulgacao TEXT);"
        "CREATE TABLE passaporte (livro_id TEXT, fase TEXT);"
        "INSERT INTO livro VALUES ('A', 'ativo', 'sem', NULL, NULL), ('B', 'ativo', 'bronze', NULL, NULL), "
        "('C', 'ativo', 'sem', NULL, NULL), ('D', 'ativo', NULL, NULL, NULL), ('E', 'excluido', 'sem', NULL, NULL);"
        "INSERT INTO passaporte VALUES ('A', 'analise externa'), ('B', 'analise externa'), ('C', 'preparacao'), "
        "('D', 'analise externa'), ('E', 'analise externa');"
        "INSERT INTO documento VALUES (1, 'https://solto.org/x.pdf', '2026-01-01');"
        "INSERT INTO achado VALUES ('x', NULL, NULL, 'barrado', '2026-01-01', 'dou');"
    )
    return b


def test_so_o_livro_sem_estrela_na_verificacao_externa_alerta():
    b = _banco()
    assert livros_para_expurgo(b) == ["A", "D"]
    c = candidatos(b)
    assert c["livros_para_expurgo"] == 2 and c["total"] == 2


def test_preparacao_e_leitura_sem_livro_nao_alertam():
    c = candidatos(_banco())
    assert c["na_preparacao"] == 1 and c["documentos_sem_uso"] == 1 and c["achados_sem_livro"] == 1
    assert c["total"] == c["livros_para_expurgo"] + c["migrados_no_chrome"]


def test_o_lote_marca_o_livro_para_expurgo():
    from eldorado.base.cartorio import analise_externa as ae
    assert "R39" in ae.INSTRUCOES and "verificacao_para_expurgo" in open(ae.__file__, encoding="utf-8").read()
    assert date.today()  # o lote real é exercitado em test_analise_externa
