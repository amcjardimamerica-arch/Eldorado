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
    _l(b, "MP", "Itajaí em Traços: concurso cultural livre", "Associação Cultural Itajaí", "https://itajaiemtracos.org.br/x", uf="SC", selo="bronze")
    _l(b, "U1", "Chamada Pública CNPq nº 29/2026 Inteligência Artificial", "CNPq", "https://www.gov.br/cnpq/a", selo="bronze")
    _l(b, "U2", "Chamada Pública CNPq nº 29/2026 Inteligência Artificial", "CNPq", "https://www.gov.br/cnpq/b")
    b.commit()
    r = expurgar(b, Diario(tmp_path / "ev", "c"))
    assert gravador.aplicar(list(ler(tmp_path / "ev"))).ok
    situ = dict(b.execute("SELECT id, situacao FROM livro").fetchall())
    assert situ["P"] == "excluido" and situ["M"] == "excluido"
    assert all(situ[i] != "excluido" for i in ("E", "A", "B", "N", "F", "U1", "MP"))  # a privada de outra cidade fica
    assert situ["U2"] == "unido" and r["unidos"] == 1  # fica o de melhor selo (U1)


def test_a_regra_territorial_no_portao_vale_so_para_as_publicas():
    from eldorado.base.missao.portao import motivo

    publica = {
        "titulo": "Prefeitura Municipal de Campinas/SP — Chamamento de projetos culturais",
        "orgao": "Prefeitura de Campinas",
        "url": "https://campinas.sp.gov.br/x",
        "uf": "SP",
    }
    privada = {
        "titulo": "Concurso cultural da Associação Cultural de Campinas/SP",
        "orgao": "Associação Cultural de Campinas",
        "url": "https://acultural.org.br/x",
        "uf": "SP",
        "nivel": "municipal",
    }
    assert "município de outro estado" in (motivo(publica) or "")
    assert "município de outro estado" not in (motivo(privada) or "")


def test_a_clausula_de_quem_pode_participar_decide_o_territorio():
    """27/10/2026 (titular, o caso de Mauriti/CE): a cláusula do edital ('resida no Município de Mauriti/CE') é prova do
    município, tão forte quanto o título; a descrição solta do território não vale (os editais nacionais que citam cidades)."""
    from eldorado.base.cartorio.auditoria import restricao_de_participacao as r
    from eldorado.base.cartorio.auditoria import territorio

    c = {
        "Requisitos": {
            "valor": "Pode se inscrever no Edital qualquer agente cultural que resida no Município de Mauriti/CE há pelo menos 02 (dois) anos"
        }
    }
    livro = {
        "titulo": "EDITAL DE CHAMAMENTO PÚBLICO Nº 03/2026 - MOSTRA CULTURAL MAURITI DE ARTES E CULTURAS",
        "uf": "BR",
        "link_oficial": "https://mapacultural.secult.ce.gov.br/files/opportunity/8448/edital-mostra-cultural-mauriti-2.pdf",
    }
    assert territorio(livro, c) == ("municipal_fora_go", "Mauriti")
    assert r({"Objeto": {"valor": "apoiar projetos dos agentes culturais do Município de Mauriti, Estado do Ceará"}}) == ("Mauriti", "CE")
    assert r({"Requisitos": {"valor": "organizações da sociedade civil com sede no Município de Goiânia há 1 ano"}}) == ("Goiânia", "GO")
    assert r({"Requisitos": {"valor": "organizações de todo o Brasil, inclusive de Goiânia e Anápolis"}}) is None
    from pathlib import Path

    src = Path("eldorado/base/comandante/biblioteca.py").read_text(encoding="utf-8")
    assert 'x["fase"] == "farol" and x["abrangencia"] != "municipal_fora_go"' in src  # a regra territorial vale no Farol
    assert "QUEM_PODE" in src  # a cláusula é dado obrigatório
