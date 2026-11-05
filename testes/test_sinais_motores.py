"""05/11/2026 (titular): os sinais de cada motor, além de «leu sem erro»."""
import sqlite3
from datetime import datetime, timezone

from eldorado.base.cerebro.sinais_motores import sinais

AGORA = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)


def _cer():
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE motor_fonte(motor TEXT, nome TEXT, leituras INT, sem_mudanca INT, achados INT, falhas INT, ultimo_erro TEXT, ultima TEXT, situacao TEXT);"
                    "CREATE TABLE motor_entregue(motor TEXT, chave TEXT, em TEXT, achado TEXT, fonte TEXT);")
    return c


def test_verde_so_sem_sinal():
    c = _cer()
    c.execute("INSERT INTO motor_fonte VALUES ('m','A',10,3,1,0,NULL,'2026-11-05T10:00:00+00:00','sem mudança')")
    c.execute("INSERT INTO motor_entregue VALUES ('m','k','2026-11-04T10:00:00+00:00','a','A')")
    assert sinais(c, "m", ["A"], False, AGORA)["luz"] == "verde"


def test_pendente_abandonada_e_sem_novidade_acendem():
    c = _cer()
    c.executemany("INSERT INTO motor_fonte VALUES (?,?,?,?,?,?,?,?,?)", [
        ("m", "A", 40, 38, 2, 0, None, "2026-11-05T10:00:00+00:00", "sem mudança"),
        ("m", "B", 40, 0, 0, 2, "pendente no computador local", "2026-11-05T10:00:00+00:00", "lida"),
        ("m", "C", 7, 0, 0, 7, "bloqueado", "2026-10-22T10:00:00+00:00", None)])
    c.execute("INSERT INTO motor_entregue VALUES ('m','k','2026-10-24T10:00:00+00:00','a','A')")
    s = sinais(c, "m", ["A", "B", "C"], False, AGORA)
    assert s["luz"] == "amarelo" and s["pendentes_local"] == ["B"] and s["abandonadas"] == ["C"]
    assert any("sem oportunidade nova há 12 dias" in x for x in s["sinais"])


def test_nunca_entregou_e_vermelho_e_o_especial_nao():
    c = _cer()
    c.execute("INSERT INTO motor_fonte VALUES ('m','A',31,28,0,0,NULL,'2026-11-05T10:00:00+00:00','sem mudança')")
    assert sinais(c, "m", ["A"], False, AGORA)["luz"] == "vermelho"
    assert sinais(c, "m", ["A"], True, AGORA)["luz"] == "verde"
