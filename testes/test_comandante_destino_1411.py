"""R57 (titular, 14/11/2026): o Comandante medido pelo destino final, a finalidade em cada decisão e o motivo do descarte."""
import json
import sqlite3

from eldorado.base.comandante.descartes import classificar, medir
from eldorado.base.comandante.destino import RECOMPENSA, destinos
from eldorado.base.comandante.finalidade import anotar
from eldorado.base.comandante.politica import contagens_espiao


def _bib():
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE livro(id TEXT, situacao TEXT, justificativa_exclusao TEXT, link_divulgacao TEXT);"
                    "CREATE TABLE passaporte(livro_id TEXT, fase TEXT); CREATE TABLE previsao(livro_id TEXT, datas_encontrado TEXT);"
                    "CREATE TABLE achado(livro_id TEXT, motor TEXT, dados TEXT, decisao TEXT, encontrado_em TEXT);")
    for lid, sit, fase, _mot in (("F", "transferido ao farol", "farol", "x"), ("A", "finalizado", "arquivo", "x"), ("E", "finalizado", "arquivo", "x"),
                                ("U", "unido", None, "x"), ("D", "excluido", None, "x")):
        b.execute("INSERT INTO livro VALUES (?, ?, ?, ?)", (lid, sit, "notícia, não é oportunidade" if sit == "excluido" else None, "https://outro.org/x"))
        b.execute("INSERT INTO passaporte VALUES (?, ?)", (lid, fase))
    b.execute("INSERT INTO previsao VALUES ('E', '[\"2025-03-01\"]')")
    return b


def test_a_recompensa_de_um_livro_descartado_e_zero():
    d = destinos(_bib())
    assert d == {"F": 1.0, "A": 0.5, "E": 0.7, "U": 0.2, "D": 0.0} and RECOMPENSA["descartado"] == 0


def test_a_familia_do_espiao_e_medida_pelo_destino_e_nao_pelo_aceite():
    b, c = _bib(), sqlite3.connect(":memory:")
    c.execute("CREATE TABLE espiao_missao(familia TEXT)")
    c.executemany("INSERT INTO espiao_missao VALUES (?)", [("f1",)] * 4)
    b.executemany("INSERT INTO achado VALUES (?, 'espiao', ?, 'aceito', '2026-11-10')", [("F", json.dumps({"familia": "f1"})), ("D", json.dumps({"familia": "f1"}))])
    a, e = contagens_espiao(b, c, ["f1"])["f1"]
    assert a == 1.0 and e == 3.0                              # o aceite descartado (D) não conta como acerto


def test_toda_decisao_leva_a_finalidade_e_a_medida():
    ctx = json.loads(anotar({"x": 1}, "coleta"))
    assert ctx["finalidade"] == "descobrir" and ctx["medida"] and json.loads(anotar("", "interceptador"))["finalidade"] == "completar"
    from pathlib import Path
    for arq in ("decidir.py", "escolher.py", "pilotos.py"):
        assert "anotar(" in Path(f"eldorado/base/comandante/{arq}").read_text(encoding="utf-8"), arq


def test_o_motivo_do_descarte_volta_e_o_ruido_vai_ao_crivo():
    assert classificar("licitação: pregão eletrônico") == "licitação ou compra" and classificar("xyz") == "outros"
    b = _bib()
    for i in range(20):
        b.execute("INSERT INTO livro VALUES (?, 'excluido', 'notícia', 'https://ruido.org/n')", (f"R{i}",))
    m = medir(b)
    assert "ruido.org" in m["ruido"] and m["classes"]["notícia ou página genérica"] >= 20
    from pathlib import Path
    assert "self.ruido" in Path("eldorado/motores/pilotos/espiao.py").read_text(encoding="utf-8")
