"""08/11/2026 (parecer individual dos motores, piloto Espião): o aprendizado premiava o barulho — a família mais usada recebia
recompensa por qualquer missão dela desde a decisão (o internacional_espanhol chegou a 77% das missões). Agora a decisão é
avaliada pela missão que ela autorizou, nenhuma família passa de 20% das últimas 100 missões e o fracasso pesa como o acerto."""
import sqlite3
from datetime import datetime, timedelta, timezone

from eldorado.base.comandante.pilotos import _teto_por_familia


def _cer(tmp_path, missoes):
    c = sqlite3.connect(tmp_path / "c.db")
    c.execute("CREATE TABLE espiao_missao(em TEXT, familia TEXT, achados INTEGER)")
    c.executemany("INSERT INTO espiao_missao VALUES (?,?,?)", missoes)
    return c


def test_o_teto_de_20_por_cento_por_familia(tmp_path):
    agora = datetime.now(timezone.utc)
    missoes = [((agora - timedelta(minutes=i)).isoformat(), "internacional_espanhol" if i % 10 < 8 else "nao_financeiro", 0) for i in range(100)]
    c = _cer(tmp_path, missoes)
    lista = [("internacional_espanhol", 0.9), ("nao_financeiro", 0.3), ("setor_apoio_regiao", 0.3)]
    pesos = _teto_por_familia(c, lista, [0.9, 0.3, 0.3])
    assert pesos[0] < 0.05 and pesos[1:] == [0.3, 0.3]           # 80% das missões: fica com 5% do peso


def test_sem_historico_o_teto_nao_vale(tmp_path):
    c = _cer(tmp_path, [(datetime.now(timezone.utc).isoformat(), "internacional_espanhol", 0)] * 10)
    assert _teto_por_familia(c, [("internacional_espanhol", 0.9), ("x", 0.1)], [0.9, 0.1]) == [0.9, 0.1]


def test_a_decisao_vale_pela_missao_que_autorizou(tmp_path):
    """A família que voou de novo depois (com achado) não premia a decisão cuja missão voltou vazia."""
    from eldorado.base.aprendizado import avaliar as A

    em = datetime.now(timezone.utc) - timedelta(hours=30)
    cer = sqlite3.connect(tmp_path / "cerebro.db")
    cer.executescript("CREATE TABLE comandante_decisao(id TEXT, etapa TEXT, alvo TEXT, em TEXT, avaliada_em TEXT, recompensa REAL, resultado TEXT);"
                      "CREATE TABLE espiao_missao(em TEXT, familia TEXT, achados INTEGER);")
    cer.execute("INSERT INTO comandante_decisao VALUES ('d1', 'espiao', 'fam', ?, NULL, NULL, NULL)", (em.isoformat(),))
    cer.executemany("INSERT INTO espiao_missao VALUES (?,?,?)", [((em + timedelta(minutes=1)).isoformat(), "fam", 0),
                                                                 ((em + timedelta(hours=5)).isoformat(), "fam", 3)])
    cer.commit()
    sqlite3.connect(tmp_path / "biblioteca.db").close()

    class Diario:
        def __init__(self):
            self.ev = []

        def emitir(self, tipo, origem, dados):
            self.ev.append(dados)

    d = Diario()
    A.avaliar(tmp_path, d)
    assert d.ev and d.ev[0]["recompensa"] == 0.0 and "0 achado" in d.ev[0]["resultado"]


def test_o_interceptador_deixa_para_o_fim_o_que_nao_e_oportunidade():
    """08/11/2026 (parecer, piloto Interceptador): resultado, estudo e o edital que só cita anos vencidos vão para o fim da
    fila (continuam nela: a fila é do Comandante, R43)."""
    from eldorado.motores.pilotos.interceptador import _fim_da_fila
    assert _fim_da_fila("Governo de Pernambuco divulga resultado definitivo do edital", None, "2026-11-08")
    assert _fim_da_fila("Estudo BISC 2026", None, "2026-11-08")
    assert _fim_da_fila("edital selecao publica 2023012 empoderamento", None, "2026-11-08")
    assert not _fim_da_fila("Edital 05/2026 de chamamento público", None, "2026-11-08")
    assert not _fim_da_fila("Edital 2024 reaberto", "2026-12-01", "2026-11-08")       # com prazo aberto, a data manda
