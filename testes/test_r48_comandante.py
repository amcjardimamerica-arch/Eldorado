"""R48 (titular, 08/11/2026 — as decisões do parecer da etapa 8 «Comandante e Aprendizado»): as travas."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from eldorado.base.comandante.politica import Thompson, contagens_coleta


class _Diario:
    def __init__(self):
        self.ev = []

    def emitir(self, tipo, modulo, dados):
        self.ev.append((tipo, dados))


def test_thompson_pela_taxa_real_e_a_probabilidade_de_inclusao():
    pol = Thompson("coleta", {"bom": (40, 10), "medio": (10, 40), "ruim": (0, 50), "novo": (0, 0)}, semente=7)
    esc = pol.escolher(2)
    assert len(esc) == 2 and esc[0][0] in ("bom", "novo")
    assert all(0 < p <= 1 for _o, p in esc)
    assert pol.media("bom") > pol.media("medio") > pol.media("ruim")


def test_contagens_da_coleta_ate_a_vespera():
    b, c = sqlite3.connect(":memory:"), sqlite3.connect(":memory:")
    b.execute("CREATE TABLE achado(motor TEXT, encontrado_em TEXT, decisao TEXT)")
    c.execute("CREATE TABLE execucao_motor(motor TEXT, inicio TEXT)")
    for d in ("2026-11-05", "2026-11-06", "2026-11-07", "2026-11-08"):
        c.execute("INSERT INTO execucao_motor VALUES ('a', ?)", (d + "T03:00:00+00:00",))
    b.executemany("INSERT INTO achado VALUES ('a', ?, 'aceito')", [("2026-11-05",), ("2026-11-08",)])
    assert contagens_coleta(b, c, ["a"], "2026-11-08") == {"a": (1, 2)}   # o dia de hoje não entra


def test_a_coleta_decide_uma_vez_por_motor_por_dia_e_sem_o_vw():
    src = Path("eldorado/base/comandante/decidir.py").read_text(encoding="utf-8")
    assert "Thompson(" in src and "substr(em, 1, 10) = ?" in src and "Politica(" not in src
    assert "Thompson(" in Path("eldorado/base/comandante/pilotos.py").read_text(encoding="utf-8")


def test_a_recompensa_do_espiao_e_o_achado_aceito_em_24h(tmp_path):
    from eldorado.base.aprendizado.avaliar import avaliar
    em = (datetime.now(timezone.utc) - timedelta(hours=30)).replace(microsecond=0)
    b = sqlite3.connect(tmp_path / "biblioteca.db")
    b.execute("CREATE TABLE achado(motor TEXT, encontrado_em TEXT, decisao TEXT, dados TEXT)")
    b.execute("INSERT INTO achado VALUES ('espiao', ?, 'aceito', ?)", (em.date().isoformat(), json.dumps({"familia": "empresa_semente"})))
    b.commit()
    b.close()
    c = sqlite3.connect(tmp_path / "cerebro.db")
    c.executescript("CREATE TABLE comandante_decisao(id INTEGER PRIMARY KEY, etapa TEXT, alvo TEXT, em TEXT, avaliada_em TEXT, contexto TEXT);"
                    "CREATE TABLE espiao_missao(familia TEXT, em TEXT, achados INT)")
    c.executemany("INSERT INTO comandante_decisao(etapa, alvo, em) VALUES ('espiao', ?, ?)",
                  [("empresa_semente", em.isoformat()), ("internacional_espanhol", em.isoformat())])
    c.executemany("INSERT INTO espiao_missao VALUES (?, ?, 5)", [("empresa_semente", (em + timedelta(hours=1)).isoformat()),
                                                                 ("internacional_espanhol", (em + timedelta(hours=1)).isoformat())])
    c.commit()
    c.close()
    d = _Diario()
    avaliar(tmp_path, d)
    rec = {x["id"]: x["recompensa"] for t, x in d.ev if t == "comandante.avaliada"}
    assert rec == {1: 1.0, 2: 0.0}      # a espanhol «achou» 5 na missão, mas nada aceito: antes contava como acerto


def test_o_comandante_pula_o_originais_de_verdade(tmp_path):
    from eldorado.base.comandante.escolher import no_comandante_escolher
    c = sqlite3.connect(tmp_path / "cerebro.db")
    c.executescript("CREATE TABLE comandante_decisao(id INTEGER); CREATE TABLE execucao_passo(no TEXT, estado TEXT, saida TEXT, em TEXT);"
                    "CREATE TABLE parametro(etapa TEXT, chave TEXT, versao INT, valor TEXT)")
    for no in ("originais", "farol"):
        c.executemany("INSERT INTO execucao_passo VALUES (?, 'concluido', '[]', ?)", [(no, f"2026-11-08T0{i}:00:00+00:00") for i in range(6)])
    c.commit()
    c.close()
    d = _Diario()
    r = no_comandante_escolher([], {"dados": str(tmp_path)}, SimpleNamespace(diario=d, execucao="x"))[0]
    assert r["__pular__"] == ["originais"] and set(r["pular"]) == {"originais", "farol"}   # o farol, só em sombra
    acoes = {x["alvo"]: x["acao"] for _t, x in d.ev}
    assert acoes == {"originais": "pular a etapa", "farol": "pularia a etapa (em sombra)"}


def test_a_rede_sem_o_link_oficial_com_a_pergunta_aberta_e_a_janela():
    from eldorado.base.cerebro.rede import RedeNeural, caracteristicas_livro, metricas_janela
    f = caracteristicas_livro({"titulo": "Edital de chamamento", "link_oficial": "https://x.gov.br", "link_oficial_tipo": "gov", "uf": "GO"})
    assert "tem_link_oficial" not in f and not any(k.startswith("link_oficial_tipo") for k in f) and "uf=go" in f
    assert "aberta" in RedeNeural.PERGUNTAS and "encerrada" not in RedeNeural.ABERTA_SIM
    h = [("2026-10-01T00:00:00", True, 0.1)] + [(f"2026-11-0{i}T00:00:00", i % 2 == 0, 0.9 if i % 2 == 0 else 0.1) for i in range(1, 9)]
    j = metricas_janela(h, 0.5)
    assert j["amostras"] == 8 and j["precisao"] == 1.0          # o caso de outubro fica fora da janela


def test_a_sala_mostra_todos_os_alarmes_e_a_janela_da_rede():
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    assert "FROM alarme WHERE fechado_em IS NULL ORDER BY aberto_em" in s and "aberto desde" in s
    assert "rede:oportunidade:7d" in s and "_faixa(pre, 0.65, 0.5)" in s


def test_a_fonte_esporadica_nao_acende_sem_novidade():
    from eldorado.base.cerebro.sinais_motores import esporadica, sinais
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE motor_fonte(motor TEXT, nome TEXT, leituras INT, sem_mudanca INT, achados INT, falhas INT, ultimo_erro TEXT, "
                    "ultima TEXT, situacao TEXT); CREATE TABLE motor_entregue(motor TEXT, chave TEXT, em TEXT, achado TEXT, fonte TEXT);")
    agora = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)
    c.execute("INSERT INTO motor_fonte VALUES ('m','A',30,30,0,0,NULL,'2026-11-08T03:00:00+00:00','sem mudança')")
    c.execute("INSERT INTO motor_entregue VALUES ('m','k','2026-10-24T10:00:00+00:00','a','A')")
    assert sinais(c, "m", ["A"], False, agora, rara=True)["luz"] == "verde"
    assert sinais(c, "m", ["A"], False, agora, rara=False)["luz"] == "amarelo"
    assert all(esporadica(m) for m in ("dj-trf1-go", "judiciario-cnj", "judiciario-tjgo", "mptgo-destinacao", "mpgo-destinacao", "mpu-destinacao"))
