"""A decisão do Cérebro: sem horário fixo; aciona conforme a necessidade e aprende as horas de cada fonte."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from eldorado.base.cerebro.decisao import Execucao, decidir, horas_produtivas

BR = ZoneInfo("America/Sao_Paulo")


def em(dia, hora):
    return datetime(2026, 10, dia, hora, 5, tzinfo=BR).astimezone(timezone.utc)


def test_primeira_leitura_do_dia_pelo_rendimento():
    hist = [Execucao("dou", em(21, 7), 40), Execucao("pncp", em(21, 9), 2)]
    d = decidir(em(22, 6), ["pncp", "dou", "novo"], hist, {})
    assert [x.motor for x in d] == ["dou", "pncp", "novo"] and all(x.motivo == "primeira leitura do dia" for x in d)   # novo: prioridade média (1)


def test_falha_tenta_de_novo_ate_3_vezes():
    hist = [Execucao("dou", em(22, 6), 0, falhou=True)]
    assert decidir(em(22, 7), ["dou"], hist, {})[0].motivo.startswith("nova tentativa (2ª do dia)")
    hist += [Execucao("dou", em(22, 7), 0, falhou=True), Execucao("dou", em(22, 8), 0, falhou=True)]
    assert decidir(em(22, 9), ["dou"], hist, {}) == []                                                # esgotou as 3


def test_volta_na_hora_aprendida_e_nao_roda_sem_necessidade():
    hist = [Execucao("dou", em(d, 20), 9) for d in range(10, 16)] + [Execucao("dou", em(22, 6), 3)]   # publica às 20h
    assert decidir(em(22, 14), ["dou"], hist, {"dou": {12}}) == []                                    # aprendido: 12h não vale mais
    d = decidir(em(22, 20), ["dou"], hist, {"dou": {12}})
    assert d and "20h" in d[0].motivo


def test_ponto_de_partida_so_com_historico_curto():
    agora = em(22, 12)
    assert horas_produtivas("x", [Execucao("x", em(21, 7), 1)], {9, 12}, agora) == {7, 9, 12}
    longo = [Execucao("x", em(d, 7), 1) for d in range(15, 21)]
    assert horas_produtivas("x", longo, {9, 12}, agora) == {7}
    assert horas_produtivas("x", [Execucao("x", em(22, 7) - timedelta(days=40), 5)], {9}, agora) == {9}  # velho demais


def test_proxima_acao_prevista():
    from eldorado.base.cerebro.decisao import proxima
    hist = [Execucao("dou", em(d, 20), 9) for d in range(10, 16)]
    assert proxima(em(22, 14), ["dou"], hist, {}).astimezone(BR).hour == 20                        # a hora aprendida
    assert proxima(em(22, 21), ["dou"], hist, {}).astimezone(BR).date().day == 23                   # passou: amanhã cedo
