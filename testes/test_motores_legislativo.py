"""Os motores do Legislativo nas páginas reais gravadas (23/10/2026)."""
from paginas_servidor import motor, servir

DOMS = ["https://www.congressonacional.leg.br", "https://legis.senado.leg.br", "https://www12.senado.leg.br", "https://www.camara.leg.br"]


def test_congresso_o_prazo_das_emendas_e_as_materias_para_entidades(tmp_path):
    srv, base = servir("legislativo-sondagem", DOMS)
    try:
        t = [a.titulo for a in motor("congresso-nacional", base, DOMS, tmp_path).buscar(None)]
    finally:
        srv.shutdown()
    assert "21/10/2026 09:30Matérias Novas/Relatórios Entregues e prazo de emendas" in t
    assert "Apresentação de emendas" in t and "Cronograma da tramitação" in t
    assert any(x.startswith("PL 427/2026 — Dispõe sobre o Fundo Nacional de Apoio ao Terceiro Setor") for x in t)
    assert not [x for x in t if "Nota Técnica" in x or "Raio X" in x or "admissibilidade" in x]


def test_lexico_estrito_do_terceiro_setor_nos_atos_municipais_e_estaduais(tmp_path):
    """Titular, 23/10/2026: todo ato do terceiro setor; nos atos dos diários, o léxico estrito (sem decretos de crédito)."""
    for pasta in ("camara-goiania-pl", "alego-pl"):
        (tmp_path / pasta).mkdir()
    casos = {"CCJ mantém autorização para Município doar materiais esportivos a associações": True,
             "LEI Nº 11.300 · Declara de utilidade pública a Associação Moradores X": True,
             "Projeto da emenda impositiva destina recursos a entidades assistenciais": True,
             "DECRETO ORÇAMENTÁRIO Nº 233, DE 2026 · Abre ao Orçamento crédito suplementar ao Fundo Municipal": False,
             "TERMO DE SERVIDÃO ADMINISTRATIVA Nº 08/2026": False,
             "DECRETO Nº 202, DE 2026 · Declara de utilidade pública, para fins de desapropriação, o imóvel": False,
             "EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - ARTE E MÍDIAS INTERATIVAS": True,
             "EXTRATO DO TERMO DE FOMENTO N.º 001/2026": True}
    for m in ("camara-goiania-pl", "alego-pl"):
        mo = motor(m, "http://x", [], tmp_path / m)
        assert {k: mo._passa_lexico(k, "") for k in casos} == casos, m
