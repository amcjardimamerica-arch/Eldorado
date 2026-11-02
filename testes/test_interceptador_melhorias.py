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


def test_os_12_itens_ate_o_fim_e_a_verificacao_previa_em_duas_rodadas():
    """01/11/2026 (titular): a fila é perseguida até os 12 itens (ou a dispensa); a verificação prévia vem antes, em duas
    rodadas por livro, com 30 minutos ou mais entre elas; nenhuma abordagem aposentada."""
    from datetime import datetime, timedelta, timezone

    lv = _livro()
    assert "Resultado" in lv.faltam and "Prazo de recurso" in lv.faltam and not hasattr(M, "POSTERIORES")
    assert not hasattr(M.Livro, "suficiente") and not M.APOSENTADAS
    it = M.Interceptador.__new__(M.Interceptador)
    it.ponte = None
    assert [n for n, _ in it.plano_de_voo(lv)][0] == 12 and M.ORDEM["sem estrela"][0] == 12
    lv.vp_rodadas, lv.vp_ultima = 1, (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    assert not lv.vp_devida and 12 not in [n for n, _ in it.plano_de_voo(lv)]  # a segunda rodada só depois de 30 min
    lv.vp_ultima = (datetime.now(timezone.utc) - timedelta(minutes=31)).isoformat()
    assert lv.vp_devida and [n for n, _ in it.plano_de_voo(lv)][0] == 12
    lv.vp_rodadas = 2
    assert not lv.vp_devida  # no máximo duas rodadas


def test_o_achado_sem_ia_pelos_extratores(tmp_path):
    """A página do edital lida pelo Interceptador, sem IA: o achado sai com os itens comprovados pelos extratores."""
    it = M.Interceptador.__new__(M.Interceptador)
    it.ia = None
    leitura = SimpleNamespace(paginas=[SimpleNamespace(texto=EDITAL)], alertas=[], dados={}, tipo="pdf", links=[])
    it._ler = lambda u, profunda=False, escada=None: (u, leitura, b"")
    a = it._achado(_livro(), 12, ["https://x.go.gov.br/edital.pdf"])
    assert {"Prazo de inscrição", "Valor", "Objeto", "Anexos"} <= set(a.dados["itens"]) and a.dados["ia"]["extratores"]
