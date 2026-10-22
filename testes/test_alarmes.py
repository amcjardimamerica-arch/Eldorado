import pytest

from eldorado.base.nucleo.alarmes import Alarmes
from eldorado.base.nucleo.eventos import ler


def test_erro_vira_alarme_e_continua_subindo(diario, gravador, bancos, tmp_path):
    alarmes = Alarmes(diario)
    with pytest.raises(ZeroDivisionError):
        with alarmes.vigiar("motor-teste"):
            resultado = 1 / 0  # noqa: F841 — erro provocado de propósito
    r = gravador.aplicar(ler(tmp_path / "eventos"))
    assert r.ok, r.recusados
    linha = bancos["cerebro"].execute("SELECT gravidade, modulo, mensagem, rastro FROM alarme").fetchone()
    assert linha["modulo"] == "motor-teste" and "ZeroDivisionError" in linha["mensagem"] and "1 / 0" in linha["rastro"]


def test_gravidade_desconhecida_e_recusada(diario):
    with pytest.raises(ValueError):
        Alarmes(diario).abrir("urgentissima", "x", "y")
