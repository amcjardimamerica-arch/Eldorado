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
