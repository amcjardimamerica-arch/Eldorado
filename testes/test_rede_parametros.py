"""02/11/2026 (titular): os parâmetros da rede pelo benchmark prequencial (estudos/bench_rede_2026_11_02.py) — a taxa e o
limiar de cada pergunta, o contexto da tentativa na ação e o histórico recente do motor."""
from eldorado.base.cerebro.rede import RedeNeural, car_acao, car_motor


def test_a_taxa_e_o_limiar_de_cada_pergunta():
    assert RedeNeural.CONFIG == {"oportunidade": (0.2, 0.5), "acao": (0.1, 0.45), "motor": (0.1, 0.35)}
    r = RedeNeural()
    assert r.p["motor"].limiar == 0.35 and r.p["acao"].limiar == 0.45 and r.motor_recentes == {}


def test_a_acao_ve_o_contexto_e_o_motor_ve_o_historico():
    x = car_acao("abordagem 3", {"faltam": ["Valor"], "tentativas_n": 9, "titulo": "Edital Lei Rouanet", "fim": "2099-01-01", "em": "2026-11-02"})
    assert x["tentativa_n=6"] and x["regime=incentivo_fiscal"] and x["prazo=aberto"] and x["nfaltam=1"]
    m = car_motor("dou", 9, 1, [True, False, True])
    assert m["ultimo=1"] and m["motor_ultimo=dou|1"] and "taxa5=0.7" in m
    assert "sem_historico" in car_motor("dou", 9, 1, []) and "sem_historico" not in car_motor("dou", 9, 1)


def test_a_comparacao_r01_por_dia_e_com_base_minima():
    """02/11/2026: o histórico migrado do Eldorado0 é um retrato de um dia; sem 3 dias de origem não há comparação (antes
    5 motores apareciam como «pior» comparando 11 dias de execuções com o acumulado de um dia)."""
    import sqlite3
    import tomllib
    from datetime import datetime, timezone
    from pathlib import Path

    from eldorado.base.painel.sala import _comparacao_r01
    cfg = tomllib.loads(Path("config/comparacao.toml").read_text(encoding="utf-8"))
    assert cfg["minimo_dias_origem"] == 3 and cfg["motores"]["novo-diarios-municipais-go"] == ["querido-diario"]
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE execucao_motor (motor TEXT, inicio TEXT, fim TEXT, achados INTEGER)")
    c.executemany("INSERT INTO execucao_motor VALUES (?, ?, ?, ?)", [("dou", "2026-10-22T10:00:00+00:00", None, 600)]
                  + [("dou", f"2026-10-{d}T{h:02d}:00:00+00:00", None, 20) for d in range(23, 30) for h in (6, 12, 18)])
    r = _comparacao_r01(c, datetime(2026, 10, 30, tzinfo=timezone.utc))
    assert r["motores"]["dou"]["novo_por_dia"] == 60 and "sem base" in r["motores"]["dou"]["situacao"] and r["piores"] == []
