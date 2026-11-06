"""R47 (titular, 06/11/2026): o ciclo dos pilotos a cada 100, pelo resultado REAL (o Chrome e o Farol), e o Comandante usa."""
import json
import sqlite3
from pathlib import Path

from eldorado.base.cerebro import ciclo_pilotos as C


class D:
    def __init__(self):
        self.ev = []

    def emitir(self, t, m, d):
        self.ev.append((t, d))


def _bancos(n_missoes=120):
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE achado(dados TEXT, livro_id TEXT, motor TEXT);"
                    "CREATE TABLE livro(id TEXT, situacao TEXT); CREATE TABLE passaporte(livro_id TEXT, fase TEXT);"
                    "CREATE TABLE tentativa(ferramenta TEXT, resultado TEXT);")
    for i in range(6):
        boa = i < 3
        b.execute("INSERT INTO achado VALUES (?,?,'espiao')", (json.dumps({"familia": "boa" if boa else "ruim", "consulta": f"q{i % 2}{boa}"}), f"L{i}"))
        b.execute("INSERT INTO livro VALUES (?,?)", (f"L{i}", "aguardando" if boa else "excluido"))
        b.execute("INSERT INTO passaporte VALUES (?,?)", (f"L{i}", "farol" if boa else "arquivo"))
    c = sqlite3.connect(":memory:")
    c.executescript("CREATE TABLE espiao_missao(id INT); CREATE TABLE espiao_familia(nome TEXT, usos INT, achados INT);"
                    "CREATE TABLE medicao(marcador TEXT, em TEXT, valor REAL, motivo TEXT);")
    c.executemany("INSERT INTO espiao_missao VALUES (?)", [(i,) for i in range(n_missoes)])
    c.executemany("INSERT INTO espiao_familia VALUES (?,?,?)", [("boa", 10, 2), ("ruim", 90, 80)])
    return b, c


def test_o_fator_real_inverte_a_familia_dos_candidatos(tmp_path):
    b, c = _bancos()
    av = C.avaliar_espiao(b, c, tmp_path)
    assert av["familias"]["boa"]["fator_real"] > 1 > av["familias"]["ruim"]["fator_real"]   # a «ruim» tem mais candidatos


def test_o_ciclo_roda_a_cada_100_e_o_comandante_usa(tmp_path):
    b, c = _bancos(120)
    d = D()
    feito = C.ciclo(b, c, d, tmp_path)
    assert "espiao" in feito and any(t == "medicao.registrada" and x["marcador"] == "ciclo:espiao" for t, x in d.ev)
    c.execute("INSERT INTO medicao VALUES ('ciclo:espiao', '2026-11-06', 120, ?)", (json.dumps(feito["espiao"]),))
    assert C.fator_familia(c, "boa") > 1 > C.fator_familia(c, "ruim")
    assert C.ciclo(b, c, D(), tmp_path).get("espiao") is None                 # menos de 100 desde o último: não roda
    s = Path("eldorado/base/comandante/pilotos.py").read_text(encoding="utf-8")
    assert "fator_familia(cer, a)" in s and "_fator_real(self.con, f)" in Path("eldorado/motores/pilotos/espiao.py").read_text(encoding="utf-8")
