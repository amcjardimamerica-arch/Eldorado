"""A organização dos livros pelo Comandante (titular, 25/10/2026): o código LOCAL·ÁREA·NATUREZA·OBJETO, a identidade do
edital (o nome próprio, o número e o ano), o desempate pelo site, as edições, a eliminação do município de outro estado
e a contagem única dos livros no site inteiro."""

import re
from datetime import datetime, timezone
from pathlib import Path

from eldorado.base.comandante.organizar import classificar, organizar


def _livro(b, i, titulo, link, uf="BR", orgao=""):
    agora = datetime.now(timezone.utc).isoformat()
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, orgao, uf, link_oficial, estrela, selo_livro, informacoes_validadas, situacao, criado_em, "
        "atualizado_em) VALUES (?, 'oportunidades', ?, ?, ?, ?, ?, 'sem', 'sem', 0, 'em trabalho', ?, ?)",
        (i, i, titulo, orgao, uf, link, agora, agora),
    )
    b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES (?, 'preparacao', ?)", (i, agora))
    b.execute("INSERT INTO livro_dados(livro_id, validacao, validado_em) VALUES (?, 'aprovado', ?)", (i, agora))


def test_a_formula_e_as_unioes(bancos):
    b = bancos["biblioteca"]
    _livro(b, "A1", "Prêmio Cultura Viva Comunitária 2026", "https://www.gov.br/cultura/premio")
    _livro(b, "A2", "Prêmio Cultura Viva Comunitária 2026", "https://www.gov.br/cultura/premio-2")  # o mesmo site: une
    _livro(b, "A3", "Prêmio Cultura Viva Comunitária 2026", "https://observatorio3setor.org.br/x")  # o republicador: une
    _livro(b, "B1", "Edital Raízes da Terra nº 3/2026", "https://www.fundacaoa.org.br/e")
    _livro(b, "B2", "Edital Raízes da Terra nº 3/2026", "https://www.institutob.org.br/e")  # dois oficiais diferentes: não une
    _livro(b, "C1", "Emendas Parlamentares - RP8", "https://www.gov.br/emendas")
    _livro(b, "C2", "Emendas Parlamentares - RP9", "https://www.gov.br/emendas")  # RP8 e RP9: diferentes
    _livro(b, "D1", "Glocal Aceleradora – 11º edital", "https://aceleradora.glocal.org/e")
    _livro(b, "D2", "Glocal Aceleradora – 12º edital", "https://aceleradora.glocal.org/e")  # a edição mais nova fica
    _livro(b, "E1", "Prefeitura Municipal de Campinas/SP — Chamamento de projetos culturais", "https://campinas.sp.gov.br/x", uf="SP")
    _livro(b, "E2", "Prefeitura Municipal de Salvador/BA — Chamamento de projetos culturais", "https://salvador.ba.gov.br/x", uf="BA")
    b.commit()
    livros = classificar(b)
    cod = {x["id"]: x["codigo"] for x in livros}
    assert all(re.fullmatch(r"[A-Z?\-]+·[A-Z]{3}·(PUB|PRI)·[A-Z]{3}", c) for i, c in cod.items() if i != "E1")
    assert cod["A1"].split("·")[1] == "CUL" and cod["A1"].split("·")[3] == "PRE"
    assert cod["E1"] is None and cod["E2"].startswith("BA-CAP")  # fora das capitais: eliminado
    d = organizar(livros)
    unioes = {(f, u) for f, u, _m in d["unir"]}
    assert {u for _f, u in unioes} >= {"A2", "A3"} and ("D2", "D1") in unioes
    assert not {u for _f, u in unioes} & {"B1", "B2", "C1", "C2"}
    assert [x["id"] for x in d["eliminar"]] == ["E1"]


def test_uma_unica_contagem_dos_livros_no_site():
    """Nenhuma tela conta o passaporte inteiro (com os unidos e os excluídos): só os livros vivos."""
    for p in list(Path("eldorado/base/painel").glob("*.py")) + list(Path("eldorado/base/comandante").glob("*.py")):
        for m in re.finditer(r"COUNT\(\*\)\s*(?:FROM passaporte\b[^\"]*)", p.read_text(encoding="utf-8")):
            assert "JOIN livro" in m.group(0) or "situacao" in m.group(0), f"{p}: {m.group(0)[:80]}"
