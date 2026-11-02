"""02/11/2026 (titular): cada livro com a história completa — ele e, em cadeia, os livros unidos a ele, em todas as tabelas."""
import sqlite3

from eldorado.base.cartorio.historia import familia, historia_completa


def _banco():
    b = sqlite3.connect(":memory:")
    b.executescript("""
    CREATE TABLE livro(id TEXT, titulo TEXT, situacao TEXT); CREATE TABLE livro_dados(livro_id TEXT, codigo TEXT);
    CREATE TABLE passaporte(livro_id TEXT, fase TEXT, entrou_em TEXT); CREATE TABLE uniao(livro_que_fica TEXT, livro_unido TEXT, em TEXT, motivo TEXT);
    CREATE TABLE certidao(livro_id TEXT, item TEXT, valor TEXT, situacao TEXT, fase TEXT, trecho TEXT, pagina INT, documento_id INT, justificativa TEXT, em TEXT);
    CREATE TABLE veredito(livro_id TEXT, origem TEXT, decisao TEXT, motivo TEXT, como_encontrou TEXT, em TEXT);
    CREATE TABLE documento(id INT, url TEXT, tipo TEXT, paginas INT, oficial INT, drive_id TEXT, leitor TEXT, obtido_em TEXT);
    INSERT INTO livro VALUES ('A','a','em trabalho'),('B','b','unido'),('C','c','unido');
    INSERT INTO uniao VALUES ('A','B','1','x'),('B','C','2','y');
    INSERT INTO certidao VALUES ('A','Objeto','o','comprovado','f','t',1,NULL,NULL,'1'),('B','Objeto','o','comprovado','f','t',1,NULL,NULL,'1'),
                                ('C','Valor','R$ 1','comprovado','f','t',1,NULL,NULL,'1');
    INSERT INTO veredito VALUES ('C','chrome','verificado_prata','m','c','3');
    """)
    return b


def test_a_familia_segue_a_cadeia_das_unioes():
    assert familia(_banco(), "A") == ["A", "B", "C"]


def test_a_historia_traz_o_que_ficou_nos_unidos_sem_repetir():
    h = historia_completa(_banco(), "A")
    assert [v["decisao"] for v in h["vereditos"]] == ["verificado_prata"] and h["vereditos"][0]["de_livro"] == "C"
    assert sorted(c["item"] for c in h["certidoes"]) == ["Objeto", "Valor"]


def test_a_conexao_volta_ao_formato_de_antes():
    b = _banco()
    b.row_factory = sqlite3.Row
    historia_completa(b, "A")
    assert b.row_factory is sqlite3.Row
