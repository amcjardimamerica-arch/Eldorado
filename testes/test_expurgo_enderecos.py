"""O documento que é o endereço de um livro ativo não é candidato ao expurgo (R35: os endereços ficam)."""
import sqlite3

from eldorado.base.cartorio.expurgo_claude import candidatos


def test_endereco_de_livro_ativo_nao_e_candidato():
    b = sqlite3.connect(":memory:")
    b.executescript(
        "CREATE TABLE documento (id INTEGER PRIMARY KEY, url TEXT, obtido_em TEXT);"
        "CREATE TABLE certidao (documento_id INTEGER);"
        "CREATE TABLE achado (id TEXT, documento_id INTEGER, livro_id TEXT, decisao TEXT, encontrado_em TEXT, motor TEXT);"
        "CREATE TABLE livro (id TEXT, situacao TEXT, link_oficial TEXT, link_divulgacao TEXT);"
        "INSERT INTO livro VALUES ('L1', 'ativo', 'https://a.gov.br/edital', 'https://noticia.com/x');"
        "INSERT INTO livro VALUES ('L2', 'excluido', 'https://b.gov.br/velho', NULL);"
        "INSERT INTO documento VALUES (1, 'https://a.gov.br/edital', '2026-01-01');"
        "INSERT INTO documento VALUES (2, 'https://noticia.com/x', '2026-01-01');"
        "INSERT INTO documento VALUES (3, 'https://b.gov.br/velho', '2026-01-01');"
        "INSERT INTO documento VALUES (4, 'https://solto.org/anexo.pdf', '2026-01-01');"
    )
    assert candidatos(b)["documentos_sem_uso"] == 2   # o do livro excluído e o solto; os dois endereços do livro ativo ficam
