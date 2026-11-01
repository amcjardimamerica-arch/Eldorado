"""01/11/2026 (titular): as melhorias do Interceptador (o diagnóstico: 70% do material sem leitura da IA)."""

from types import SimpleNamespace

from eldorado.motores.pilotos import interceptador as M
from eldorado.motores.pilotos.extratores import extrair

EDITAL = """PREFEITURA MUNICIPAL DE COLINAS DO SUL
SECRETARIA MUNICIPAL DE CULTURA
EDITAL DE CHAMAMENTO PÚBLICO Nº 01/2026
1. DO OBJETO
1.1 O presente edital tem como objeto a seleção de 30 agentes culturais para premiação pela trajetória na cultura local.
2.1 O valor total do edital é de R$ 43.866,00, distribuídos em 30 prêmios.
3.1 As inscrições ficam abertas de 07/10/2026 a 01/11/2026, pelo formulário online.
4.1 Poderão participar pessoas físicas residentes em Colinas do Sul há pelo menos dois anos.
ANEXO I - Formulário de inscrição
ANEXO II - Declaração de residência"""


def test_os_extratores_trazem_o_trecho_literal():
    itens = ["Prazo de inscrição", "Valor", "Anexos", "Objeto", "Requisitos", "Órgão / financiador", "Território", "Esfera", "Modalidade"]
    r = extrair([EDITAL], itens, "Secretaria Municipal de Cultura", "Colinas do Sul", "GO")
    assert set(r) == set(itens)
    assert (
        r["Prazo de inscrição"]["valor"] == "07/10/2026 a 01/11/2026"
        and r["Valor"]["valor"] == "R$ 43.866,00"
        and r["Esfera"]["valor"] == "municipal"
    )
    assert all(v["trecho"] in EDITAL and v["origem"] == "extrator" for v in r.values())
    assert extrair(["texto sem nada disso"], ["Valor", "Prazo de inscrição"]) == {}


def _livro(certs=None, fim=None):
    return M.Livro("L-1", "Edital 01/2026", "Secretaria", "https://x.go.gov.br/edital", None, "sem", fim, certs or {}, set(), "Colinas do Sul", "GO")


def test_posteriores_fora_e_suficiente_sai_da_fila():
    lv = _livro()
    assert "Resultado" not in lv.faltam and "Prazo de recurso" not in lv.faltam
    ok = {"situacao": "comprovado", "valor": "Secretaria Municipal de Cultura, 07/10/2026", "trecho": "trecho literal do edital", "item": "x"}
    lv2 = _livro({"Prazo de inscrição": ok, "Objeto": ok, "Órgão / financiador": ok, "Território": ok})
    assert lv2.suficiente and not _livro({"Prazo de inscrição": ok, "Objeto": ok}).suficiente


def test_a_verificacao_previa_primeiro_e_as_aposentadas_fora():
    it = M.Interceptador.__new__(M.Interceptador)
    it.ponte = None
    plano = [n for n, _ in it.plano_de_voo(_livro())]
    assert plano[0] == 12 and not (set(plano) & M.APOSENTADAS)
    assert all(v[0] == 12 for v in M.PLANO_POR_ITEM.values()) and M.ORDEM["sem estrela"][0] == 12


def test_o_achado_sem_ia_pelos_extratores(tmp_path):
    """A página do edital lida pelo Interceptador, sem IA: o achado sai com os itens comprovados pelos extratores."""
    it = M.Interceptador.__new__(M.Interceptador)
    it.ia = None
    leitura = SimpleNamespace(paginas=[SimpleNamespace(texto=EDITAL)], alertas=[], dados={}, tipo="pdf", links=[])
    it._ler = lambda u, profunda=False, escada=None: (u, leitura, b"")
    a = it._achado(_livro(), 12, ["https://x.go.gov.br/edital.pdf"])
    assert {"Prazo de inscrição", "Valor", "Objeto", "Anexos"} <= set(a.dados["itens"]) and a.dados["ia"]["extratores"]
