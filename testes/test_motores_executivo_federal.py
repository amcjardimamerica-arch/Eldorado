"""CNPq, Funarte e bancos públicos nas páginas reais gravadas (23/10/2026)."""
import pytest
from paginas_servidor import motor, servir

CASOS = {"cnpq-extensao": ["https://www.gov.br"], "site-funarte": ["https://www.gov.br"],
         "novo-bancos-publicos": ["https://www.bnb.gov.br", "https://www.bndes.gov.br", "https://sebraego.com.br"]}


def titulos(m, tmp_path):
    srv, base = servir(m, CASOS[m])
    try:
        return [a.titulo for a in motor(m, base, CASOS[m], tmp_path).buscar(None)]
    finally:
        srv.shutdown()


def test_cnpq_so_o_que_tem_extensao_ou_osc(tmp_path):
    assert titulos("cnpq-extensao", tmp_path) == []                     # as 4 abertas são para pesquisadores (eventos, bolsas, MAI/DAI, ANR)
    m = motor("cnpq-extensao", "http://x", [], tmp_path)
    assert m._passa_lexico("Chamada CNPq/MCTI Nº 15/2026 - Tecnologias Sociais e Extensão Inovadora", "")
    assert m._passa_lexico("Edital de chamada pública para projetos de divulgação científica em comunidades", "")
    assert not m._passa_lexico("Chamada CNPq nº 33/2026 - Bolsas de Produtividade do CNPq", "")
    assert not m._passa_lexico("Compartilhe por WhatsApp", "")


def test_funarte_os_editais_abertos(tmp_path):
    t = titulos("site-funarte", tmp_path)
    for esperado in ("Programa Funarte Aberta", "2ª edição - Edital de Seleção Cultura Viva - Fomento à Rede de Pontões Cultura Viva",
                     "Programa Ibercena - Convocatória 2026-2027", "Laç(z)os Artísticos – Chamada Especial CPLP"):
        assert esperado in t, esperado


def test_bancos_publicos_os_editais_sociais(tmp_path):
    t = titulos("novo-bancos-publicos", tmp_path)
    assert any(x.startswith("21/08/2025 - Chamada Pública para Apoio a Projetos Sociais com Amparo em Incentivos Fiscais") for x in t)
    assert any("6º ciclo do BNDES Periferias" in x for x in t)
    assert not [x for x in t if x.lower().startswith(("ler mais", "bolsa família")) or "Resultado" in x]


@pytest.mark.parametrize("m", list(CASOS))
def test_sem_mudanca_na_segunda_leitura(m, tmp_path):
    srv, base = servir(m, CASOS[m])
    try:
        mo = motor(m, base, CASOS[m], tmp_path)
        list(mo.buscar(None))
        assert list(mo.buscar(None)) == []
    finally:
        srv.shutdown()
