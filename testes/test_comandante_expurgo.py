"""A regra do expurgo (titular, 26/10/2026): o livro público sem selo, sem estrela e sem prazo aberto é excluído; o
município de outro estado fora das capitais também; os de mesmo código e nome se unem; as empresas ficam todas; o
recém-criado tem 3 dias; o Farol nunca é tocado."""

from datetime import datetime, timedelta, timezone

from eldorado.base.comandante.biblioteca import expurgar
from eldorado.base.nucleo.eventos import Diario, ler


def _l(b, i, titulo, orgao, link, selo="sem", estrela="sem", prazo="sem prazo", dias=10, fase="preparacao", uf="BR"):
    c = (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat()
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, orgao, uf, link_oficial, estrela, selo_livro, informacoes_validadas, situacao, criado_em, "
        "atualizado_em) VALUES (?, 'oportunidades', ?, ?, ?, ?, ?, ?, ?, 0, 'em trabalho', ?, ?)",
        (i, i, titulo, orgao, uf, link, estrela, selo, c, c),
    )
    b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES (?, ?, ?)", (i, fase, c))
    b.execute("INSERT INTO livro_dados(livro_id, validacao, validado_em, situacao_prazo) VALUES (?, 'aprovado', ?, ?)", (i, c, prazo))


def test_a_regra_do_expurgo(bancos, gravador, tmp_path):
    b = bancos["biblioteca"]
    _l(b, "P", "Edital de Cultura do Ministério", "Ministério da Cultura", "https://www.gov.br/cultura/e")  # público sem dados: sai
    _l(b, "E", "Programa Social da Empresa Alfa", "Instituto Empresa Alfa", "https://institutoalfa.org.br/p")  # empresa: fica
    _l(b, "A", "Chamada da Secretaria de Cultura", "Secretaria de Cultura", "https://www.gov.br/x", prazo="aberta")  # aberta: fica
    _l(b, "B", "Edital do Fundo Estadual", "Secretaria Estadual", "https://www.go.gov.br/b", selo="bronze")  # com selo: fica
    _l(b, "N", "Edital Novo da Secretaria", "Secretaria", "https://www.gov.br/n", dias=1)  # recém-criado: fica
    _l(b, "F", "Edital no Farol", "Ministério", "https://www.gov.br/f", fase="farol")  # Farol: fica
    _l(
        b,
        "M",
        "Prefeitura Municipal de Campinas/SP — Chamamento cultural",
        "Prefeitura de Campinas",
        "https://campinas.sp.gov.br/x",
        uf="SP",
        selo="bronze",
    )
    _l(b, "U1", "Chamada Pública CNPq nº 29/2026 Inteligência Artificial", "CNPq", "https://www.gov.br/cnpq/a", selo="bronze")
    _l(b, "U2", "Chamada Pública CNPq nº 29/2026 Inteligência Artificial", "CNPq", "https://www.gov.br/cnpq/b")
    b.commit()
    r = expurgar(b, Diario(tmp_path / "ev", "c"))
    assert gravador.aplicar(list(ler(tmp_path / "ev"))).ok
    situ = dict(b.execute("SELECT id, situacao FROM livro").fetchall())
    assert situ["P"] == "excluido" and situ["M"] == "excluido"
    assert all(situ[i] != "excluido" for i in ("E", "A", "B", "N", "F", "U1"))
    assert situ["U2"] == "unido" and r["unidos"] == 1  # fica o de melhor selo (U1)
