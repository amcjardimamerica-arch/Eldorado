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


def test_os_resultados_do_chrome_da_fila_foram_aplicados():
    """01/11/2026 (titular): as partes 1 a 3 do Chrome sobre a fila do Interceptador: 475 certidões, 12 dispensas (as 4 de
    'não verificável' ficam para o Interceptador), 323 exclusões (não é oportunidade, inacessível, encerrada sem data),
    220 encerradas com as datas arquivadas, 70 abertas na fila."""
    import json
    from pathlib import Path

    ev = [json.loads(linha) for linha in Path("eventos/2026/11/02/claude-interceptador-chrome-01-11.jsonl").read_text(encoding="utf-8").splitlines()]
    tipos = [e["tipo"] for e in ev]
    assert tipos.count("livro.excluido_logicamente") == 323 and tipos.count("livro.passagem") <= 220
    disp = [e for e in ev if e["tipo"] == "certidao.gravada" and e["dados"]["situacao"] == "dispensado"]
    assert len(disp) == 12 and all(e["dados"]["item"] not in ("Objeto", "Prazo de inscrição", "Território") for e in disp)
    assert Path("expurgos/2026-11-02T002405.json").exists()
