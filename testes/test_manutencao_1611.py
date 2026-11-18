"""As correções da manutenção de 16/11/2026 (o relatório de correções, fichas C-01 a C-25)."""
from eldorado.base.cerebro.encaminhamento import Encaminhamento
from eldorado.base.nucleo.contratos import Achado


class _D:
    def __init__(self):
        self.ev = []

    def emitir(self, t, m, d, **k):
        self.ev.append(t)


def test_o_no_originais_nao_falha_com_achado_sem_documento_e_entrega_o_achado():
    """C-01: a página do mapa do site que não abriu vira achado sem documento — antes, KeyError: 'url' derrubava a passagem."""
    enc = Encaminhamento.__new__(Encaminhamento)
    enc.diario = _D()
    a = Achado(id="m-mapa-1", motor="m", encontrado_em="2026-11-16", link_divulgacao="https://x.org/edital", link_oficial="https://x.org/edital",
               titulo="Edital", dados={"livro_id": "L1"}, documento=None)
    enc._entregar(a, "m")
    assert enc.diario.ev == ["achado.entregue"]
    from pathlib import Path
    m = Path("eldorado/motores/canal/motor.py").read_text(encoding="utf-8")
    assert "if p.link not in relevantes or p.link in nesta_rodada" in m   # a relevante além do limite não se perde


def test_o_posto_do_espiao_nao_mostra_missao_undefined():
    """C-19: o painel publica motor, título e desde — a página usa o título quando não há número da missão."""
    from pathlib import Path
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert "Missão ${MA.n}/${MA.total} — ${esc(MA.missao)}</b>" not in p and 'esc(MA.missao||MA.titulo||"")' in p


def test_livro_devolvido_do_arquivo_com_prazo_aberto_usa_uma_regua_so():
    """C-02 (R46): a devolução do arquivo e a saída do Farol usam a mesma condição de prazo aberto (o livro ia e voltava)."""
    import inspect

    from eldorado.base.cartorio import auditoria
    from eldorado.base.cartorio.regua import PRAZO_ABERTO
    assert "inscricao_fim" in PRAZO_ABERTO and "situacao_prazo" in PRAZO_ABERTO
    assert "PRAZO_ABERTO" in inspect.getsource(auditoria.devolver_abertas_do_arquivo)
    assert "PRAZO_ABERTO" in inspect.getsource(auditoria.farol_so_com_prazo_aberto)
    assert '("certificacao", "farol")' in inspect.getsource(auditoria.devolver_abertas_do_arquivo)


def test_aviso_de_licitacao_nao_entra_e_o_ato_vizinho_nao_contamina():
    """C-03: o aviso de contratação direta ou de anulação é barrado; a dispensa vizinha fica fora do edital."""
    from eldorado.base.missao.regras_portao import portao_associacao
    from eldorado.motores.leitura.atos import recortar
    assert "aviso de licitação" in (portao_associacao({}, "AVISO DE CONTRATACAO DIRETA N 12/2026 SECRETARIA") or "")
    texto = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026\nSeleção de organizações da sociedade civil para projetos culturais no município.\n"
             "DISPENSA DE LICITAÇÃO Nº 44/2026\nRequisito: apresentar certidão negativa de débitos trabalhistas e atestado de capacidade.\n")
    atos = recortar(texto)
    assert len(atos) == 2 and "certidão negativa" not in atos[0]["texto"]


def test_os_que_fecham_em_7_dias_sao_contados_antes_do_corte():
    """C-18: a lista mostra 15; o total é o do banco (eram 45 e o relatório dizia 15)."""
    from eldorado.base.comandante.apresentar import _n7
    assert _n7({"fecham_em_7_dias": [1] * 15, "fecham_em_7_dias_total": 45}) == 45


def test_o_ocr_que_demora_nao_prende_a_leitura():
    """17/11/2026: o OCR passou a levar minutos por página e prendeu a Qualidade — agora tem tempo limite por página."""
    import time

    import pytest

    from eldorado.motores.leitura.ocr import OCR, OCRDemorou
    o = OCR.__new__(OCR)
    o._motor, o._tess, o.nome = (lambda img: time.sleep(5)), None, "lento"
    t0 = time.monotonic()
    with pytest.raises(OCRDemorou):
        o.texto(b"x", limite_s=0.5)
    assert time.monotonic() - t0 < 2


def test_o_prazo_da_api_vale_antes_do_texto():
    """17/11/2026: o Agente Cultural tinha 2 chamamentos de Goiás abertos e não entregava — o prazo vinha num campo da API."""
    from datetime import timedelta

    from eldorado.motores.canal.motor import _prazo_estruturado_vigente, hoje_local
    from eldorado.motores.descoberta.pistas import Pista
    futuro = (hoje_local() + timedelta(days=5)).isoformat()
    assert _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": {"date": futuro + " 23:59:00"}}))
    assert _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": futuro}))
    assert not _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api", extra={"fim": "2020-01-01"}))
    assert not _prazo_estruturado_vigente(Pista(titulo="x", link="https://x", origem="api"))
