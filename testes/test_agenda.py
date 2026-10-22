from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from eldorado.base.fluxo.agenda import Agenda, AgendaInvalida, Regra

SP = ZoneInfo("America/Sao_Paulo")
SEG = datetime(2026, 10, 19, 6, 30, tzinfo=SP)          # segunda-feira


def ag(**kw):
    return Agenda([Regra(modulo="do-goias", horarios=("06:23", "12:53"), dias=("seg", "ter", "qua", "qui", "sex", "sab"), **kw)])


def test_devido_dentro_da_janela_e_nao_fora():
    assert [d.modulo for d in ag().devidos(SEG)] == ["do-goias"]
    assert ag().devidos(SEG.replace(hour=7, minute=30)) == []


def test_dia_nao_permitido():
    assert ag().devidos(datetime(2026, 10, 25, 6, 30, tzinfo=SP)) == []        # domingo


def test_uma_passagem_por_janela():
    a = ag()
    d = a.devidos(SEG)[0]
    assert a.devidos(SEG.replace(minute=40), acionadas={(d.modulo, d.janela_inicio)}) == []


def test_cadencia_semanal():
    a = ag(cadencia_dias=7)
    assert a.devidos(SEG, ultima_execucao={"do-goias": SEG.replace(day=16)}) == []
    assert len(a.devidos(SEG, ultima_execucao={"do-goias": SEG.replace(day=12)})) == 1


def test_janela_prevista_pela_analise():
    a = Agenda([Regra(modulo="mpgo", janelas_previstas=(("2026-10-20T00:00:00-03:00", "2026-10-21T00:00:00-03:00"),))])
    assert a.devidos(datetime(2026, 10, 20, 15, 0, tzinfo=SP))[0].motivo == "janela prevista pela análise"


def test_hora_sem_fuso_e_regras_invalidas():
    with pytest.raises(ValueError):
        ag().devidos(datetime(2026, 10, 19, 6, 30))
    with pytest.raises(AgendaInvalida):
        Regra(modulo="x", horarios=("25:00",))
    with pytest.raises(AgendaInvalida):
        Regra(modulo="x", dias=("segunda",))
    with pytest.raises(AgendaInvalida):
        Agenda([Regra(modulo="x"), Regra(modulo="x")])
