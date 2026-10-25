"""A identidade das oportunidades (titular, 24/10/2026): a mesma oportunidade num só livro; o que já tem livro agrega."""
from types import SimpleNamespace

from eldorado.base.cartorio import identidade as I
from eldorado.base.nucleo.eventos import criar, ler

AGORA = "2026-10-24T12:00:00+00:00"


def _livro(id_, titulo, link, estrela="sem"):
    return [criar("livro.criado", "t", {"id": id_, "missao": "oportunidades", "chave": id_, "titulo": titulo, "link_divulgacao": link,
                                         "link_oficial": None, "estrela": estrela, "selo_livro": "sem", "informacoes_validadas": 0,
                                         "situacao": "em trabalho", "criado_em": AGORA, "atualizado_em": AGORA})]


def test_a_mesma_oportunidade_vira_um_livro(bancos, gravador, diario, tmp_path):
    for evs in (_livro("A", "Chamada CNPq nº 33/2026 — Bolsas de Produtividade — Brasil", "https://cnpq.br/chamada-33", "prata"),
                _livro("B", "Chamada CNPq Nº 33/2026: Bolsas de Produtividade", "https://www.cnpq.br/chamada-33/"),
                _livro("C", "Edital 2026", "https://cidade-a.gov.br/edital"), _livro("D", "Edital 2026", "https://cidade-b.gov.br/edital")):
        assert gravador.aplicar(evs).ok
    assert gravador.aplicar([criar("achado.entregue", "m", {"id": "ach-b", "motor": "m", "encontrado_em": "2026-10-24", "titulo": "x",
                                                             "link_divulgacao": "https://cnpq.br/chamada-33", "dados": "{}", "livro_id": "B"}),
                             criar("certidao.gravada", "t", {"livro_id": "B", "item": "Valor", "valor": "R$ 10 mil", "pagina": 1, "trecho": "R$ 10 mil",
                                                             "fase": "certificacao", "situacao": "comprovado", "em": AGORA})]).ok
    r = I.no_unir_repetidos([], {"dados": str(tmp_path)}, SimpleNamespace(diario=diario))
    assert r == [{"unidos": 1}]                                                       # A e B; C e D (genéricos, links diferentes) não
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    b = bancos["biblioteca"]
    assert b.execute("SELECT situacao FROM livro WHERE id = 'B'").fetchone()[0] == "unido"            # não se apaga
    assert b.execute("SELECT livro_que_fica FROM uniao WHERE livro_unido = 'B'").fetchone()[0] == "A"
    assert b.execute("SELECT livro_id FROM achado WHERE id = 'ach-b'").fetchone()[0] == "A"            # o achado passou
    assert b.execute("SELECT COUNT(*) FROM certidao WHERE livro_id = 'A' AND item = 'Valor'").fetchone()[0] == 1   # a certidão passou
    assert {x[0] for x in b.execute("SELECT situacao FROM livro WHERE id IN ('C', 'D')")} == {"em trabalho"}


def test_o_achado_da_oportunidade_que_ja_tem_livro_agrega(bancos, gravador, diario):
    from eldorado.base.cartorio.indice import Indice
    from eldorado.base.missao.oportunidades import MissaoOportunidades
    from eldorado.base.nucleo.contratos import Achado
    assert gravador.aplicar(_livro("A", "Prêmio Cultura Viva 2026 — Goiás", "https://cultura.gov.br/premio-cultura-viva-2026")).ok
    ind = Indice(bancos["biblioteca"], MissaoOportunidades(), diario)
    a = Achado(id="novo-1", motor="outro", titulo="PRÊMIO CULTURA VIVA 2026", link_divulgacao="https://www.cultura.gov.br/premio-cultura-viva-2026/",
               encontrado_em="2026-10-24", dados={})
    livro, novo, como = ind.resolver(a)
    assert (livro, novo) == ("A", False) and "mesma oportunidade" in como
