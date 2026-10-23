"""Os modelos em lote do Cérebro: medidos em ordem cronológica e usados só onde discernem melhor que o contínuo."""
import random

import pytest

from eldorado.base.cerebro import lote


def casos(n, sinal=True):
    r = random.Random(3)
    saida = []
    for i in range(n):
        v = r.random() < 0.5
        x = {"motor=a": 1.0 if (v if sinal else r.random() < 0.5) else 0.0, "ruido": r.random()}
        saida.append((f"2026-{i:05d}", "acao", x, v))
    return saida


def test_lote_aprende_o_sinal_e_recusa_poucos_casos():
    pytest.importorskip("sklearn")
    c = casos(200)
    m = lote.treinar([x for *_, x, _ in c], [v for *_, v in c])
    assert m is not None and m.discernimento > 0.9 and m.nota({"motor=a": 1.0, "ruido": 0.5}) > 0.5
    assert lote.treinar([x for *_, x, _ in c[:10]], [v for *_, v in c[:10]]) is None              # poucos casos: fica o contínuo


def test_compara_e_liga_so_onde_discerne_melhor():
    pytest.importorskip("sklearn")
    from eldorado.base.cerebro.rede import RedeNeural
    rede = RedeNeural()
    c = casos(200)
    for _, p, x, v in c:
        rede.p[p].aprender_de(x, v)
    relato = lote.comparar_e_ligar(rede, c)
    assert relato["acao"]["usa"] in ("lote", "contínuo") and relato["oportunidade"]["lote"] == "poucos casos"
    assert (rede.p["acao"].lote is not None) == (relato["acao"]["usa"] == "lote")
