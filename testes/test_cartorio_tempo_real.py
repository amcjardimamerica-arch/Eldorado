"""R40 (titular, 03/11/2026): nenhum dado desatualizado nem decorativo — o Cartório conta no banco e toda gravação de dados
republica o painel, que importa os vereditos pendentes antes de aplicar os eventos."""
import sqlite3
from pathlib import Path


def test_toda_gravacao_de_dados_republica_e_importa_os_vereditos():
    y = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    assert '"eventos/**", "verificacao/**", "expurgos/**"' in y
    assert y.index("eldorado vereditos") < y.index("run: eldorado aplicar")


def test_o_cartorio_conta_no_banco_sem_decoracao():
    from eldorado.base.missao import itens as I
    from eldorado.base.painel.cartorio import montar
    b = sqlite3.connect(":memory:")
    b.executescript("""
    CREATE TABLE livro(id TEXT, titulo TEXT, orgao TEXT, uf TEXT, estrela TEXT, selo_livro TEXT, link_oficial TEXT, link_divulgacao TEXT,
                       criado_em TEXT, situacao TEXT);
    CREATE TABLE passaporte(livro_id TEXT, fase TEXT, entrou_em TEXT);
    CREATE TABLE livro_dados(livro_id TEXT, inscricao_fim TEXT, situacao_prazo TEXT, escada TEXT, origem TEXT, validacao TEXT, codigo TEXT);
    CREATE TABLE certidao(id INTEGER, livro_id TEXT, item TEXT, valor TEXT, situacao TEXT, fase TEXT, justificativa TEXT, trecho TEXT,
                          pagina INTEGER, documento_id INTEGER, em TEXT);
    CREATE TABLE passagem(id INTEGER, livro_id TEXT, de TEXT, para TEXT, em TEXT, autorizado_por TEXT, motivo TEXT);
    CREATE TABLE tentativa(livro_id TEXT, ferramenta TEXT, em TEXT, resultado TEXT);
    CREATE TABLE achado(livro_id TEXT, motor TEXT);
    CREATE TABLE documento(id INTEGER, url TEXT, tipo TEXT, paginas INTEGER, oficial INTEGER);
    INSERT INTO livro VALUES ('A','a',NULL,'GO','bronze','sem','https://o',NULL,'2026-11-01','em trabalho'),
                             ('B','b',NULL,'GO','sem','sem',NULL,NULL,'2026-11-01','excluido');
    INSERT INTO passaporte VALUES ('A','analise externa','2026-11-01'),('B','preparacao','2026-11-01');
    INSERT INTO livro_dados VALUES ('A',NULL,NULL,NULL,NULL,NULL,NULL),('B',NULL,NULL,NULL,NULL,NULL,NULL);
    """)
    b.executemany("INSERT INTO certidao (livro_id, item, situacao, em) VALUES ('A', ?, 'comprovado', '2026-11-03T00:00:00+00:00')",
                  [(k,) for k in I.DOZE[:3]])
    b.execute("INSERT INTO certidao (livro_id, item, situacao, em) VALUES ('A', 'Valor', 'contestado', '2026-11-03T00:00:00+00:00')")
    d, _ = montar(b, None, agora="2026-11-03T12:00:00+00:00")
    assert {e["id"]: e["livros"] for e in d["mostradores"]["etapas"]}["analise externa"] == 1      # a etapa do passaporte
    assert d["resumo"]["livros"] == 1 and d["resumo"]["certidoes"] == 3 and d["resumo"]["certidoes_24h"] == 3
    assert d["contestadas"] == {"certidoes": 1, "livros": 1}
    assert "por_versao" not in d and "cinza_conferidos" not in d and "itens_achados_pelo_gabarito" not in d["gabarito"]
