"""01/11/2026 (titular): a mesma oportunidade não pode ter dois livros, mesmo com títulos diferentes (outro canal); e o
que só se parece (categorias, números de edital diferentes) nunca se une, nem em cadeia."""

import sqlite3

from eldorado.base.cartorio.identidade import conflito, grupos, mesma_por_caracteristicas
from eldorado.base.comandante.escolher import CANDIDATAS


def lv(i, titulo, ini="2026-10-07", fim="2026-11-01", site="https://colinasdosul.go.gov.br/", objeto="", valor="", municipio=None):
    return {
        "id": i,
        "titulo": titulo,
        "ini": ini,
        "fim": fim,
        "oficial": site,
        "divulgacao": site,
        "objeto": objeto,
        "valor": valor,
        "municipio": municipio,
    }


OBJ = "premiação de agentes culturais com trajetória cultural no município, recursos da política nacional aldir blanc"


def test_a_mesma_oportunidade_com_titulos_diferentes_se_une():
    a = lv("op-690f9928042c", "Chamamento publico para credenciamento de agentes culturais pnab ciclo 2. — fundo municipal", objeto=OBJ)
    b = lv("op-6e1743f5d723", "Edital de Premiação Cultural 01/2026 (PNAB) de Colinas do Sul-GO: 30 prêmios, R$ 43.866,00", objeto=OBJ)
    assert mesma_por_caracteristicas(a, b)


def test_o_que_so_se_parece_nunca_se_une():
    teatro = lv("c15", "PNAB Goiás - Teatro — Goiás", site="https://goias.gov.br/x", objeto=OBJ)
    circo = lv("c16", "PNAB Goiás - Circo — Goiás", site="https://goias.gov.br/x", objeto=OBJ)
    assert conflito(teatro, circo) and not mesma_por_caracteristicas(teatro, circo)
    e09 = lv("g9", "Edital 09 – Fomento Cultural II – Ações Formativas (PDF)", site="https://goiania.go.gov.br/a", objeto=OBJ)
    e10 = lv("g10", "Edital 10 – Fomento Cultural III – Patrimônio Cultural (PDF)", site="https://goiania.go.gov.br/a", objeto=OBJ)
    assert conflito(e09, e10)
    s2 = lv("s2", "Chamamento SEJUS-PI 02/2026 (APEC em Parnaíba)", site="https://sigrp.pi.gov.br/", objeto=OBJ, valor="R$ 700,9 mil")
    s3 = lv("s3", "Chamamento SEJUS-PI 03/2026 (CIAP de Altos/PI)", site="https://sigrp.pi.gov.br/", objeto=OBJ, valor="R$ 700,9 mil")
    assert conflito(s2, s3) and not mesma_por_caracteristicas(s2, s3)
    assert not mesma_por_caracteristicas(lv("x", "A", fim="2026-11-02", objeto=OBJ), lv("y", "A", objeto=OBJ))  # outro prazo


def test_a_uniao_nunca_se_encadeia_sobre_um_conflito(tmp_path):
    con = sqlite3.connect(tmp_path / "b.db")
    con.executescript("""CREATE TABLE livro(id, titulo, uf, link_oficial, link_divulgacao, estrela, criado_em, situacao);
      CREATE TABLE livro_dados(livro_id, inscricao_fim, inscricao_inicio, municipio, esfera, abrangencia, area, codigo);
      CREATE TABLE certidao(id INTEGER PRIMARY KEY, livro_id, item, valor, situacao);""")
    for i, t in (("s2", "Chamamento SEJUS-PI 02/2026 (APEC)"), ("s3", "Chamamento SEJUS-PI 03/2026 (CIAP)"), ("lixo", "Quem pode aplicar?")):
        con.execute("INSERT INTO livro VALUES (?,?,NULL,'https://sigrp.pi.gov.br/',NULL,'sem','2026-10-01','em trabalho')", (i, t))
        con.execute("INSERT INTO livro_dados VALUES (?,'2026-11-10','2026-10-07',NULL,NULL,NULL,NULL,NULL)", (i,))
        con.execute("INSERT INTO certidao(livro_id,item,valor,situacao) VALUES (?,'Objeto',?,'comprovado')", (i, OBJ))
    con.commit()
    juntos = [{f, *(u for u, _ in us)} for f, us in grupos(con)]
    assert not any({"s2", "s3"} <= g for g in juntos)


def test_a_uniao_de_repetidos_nunca_e_pulada():
    assert "unir_repetidos" not in CANDIDATAS
