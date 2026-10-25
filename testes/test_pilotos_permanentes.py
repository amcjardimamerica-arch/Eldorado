"""Os pilotos de forma permanente (titular, 25/10/2026): voam em segundo plano; os nós entregam o que eles trouxeram."""
from pathlib import Path
from types import SimpleNamespace

from eldorado.base.cerebro import pilotos_permanentes as P
from eldorado.base.cerebro.encaminhamento import no_encaminhar, no_espiao


def test_com_os_voos_ligados_os_nos_entregam_o_que_eles_trouxeram():
    P.ATIVO.set()
    try:
        P.ENTREGAS["interceptador"].put({"id": "a1"})
        P.ENTREGAS["espiao"].put({"id": "e1"})
        ctx = SimpleNamespace(diario=None)
        assert no_encaminhar([], {"dados": "dados"}, ctx) == [{"id": "a1"}]
        assert no_espiao([], {"dados": "dados"}, ctx) == [{"id": "e1"}]
        assert no_encaminhar([], {"dados": "dados"}, ctx) == []                      # entregue uma vez só
    finally:
        P.ATIVO.clear()


def test_o_funcionamento_permanente_liga_os_voos():
    fonte = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "from ..cerebro.pilotos_permanentes import ligar" in fonte and "ligar(dados, eventos, parar)" in fonte
