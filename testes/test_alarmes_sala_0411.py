"""04/11/2026 (titular): o mostrador do servidor desenha (o escape do bloco), a fila do Chrome segue a regra dos 50 itens e
168 h, e o motor que volta a rodar fecha os seus alarmes de adiamento."""
import sqlite3
from pathlib import Path

from eldorado.base.cerebro.regencia import _fechar_adiamentos


def test_o_mostrador_do_servidor_tem_o_seu_escape():
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    bloco = h[h.index("/* O servidor do sistema (titular, 24/10/2026)"):h.index("function procs(M)")]
    assert "const e=s=>String(" in bloco


def test_a_fila_do_chrome_segue_a_regra_dos_50_e_168h():
    s = Path("eldorado/base/painel/sala.py").read_text(encoding="utf-8")
    i = s.index('"ve_para_o_chrome",\n        "Livros na fila do Chrome')
    assert "_alerta_claude(ext, _idade_ext)" in s[i:i + 300]


def test_o_motor_que_voltou_fecha_os_adiamentos(tmp_path):
    c = sqlite3.connect(tmp_path / "cerebro.db")
    c.executescript("CREATE TABLE alarme(id INTEGER, modulo TEXT, mensagem TEXT, fechado_em TEXT);"
                    "INSERT INTO alarme VALUES (1,'dou','motor adiado pelo governador: carga 82%',NULL),"
                    "(2,'pncp','motor adiado pelo governador: carga 82%',NULL),(3,'dou','outro alarme',NULL);")
    c.commit()
    c.close()
    ev = []

    class D:
        def emitir(self, t, m, d):
            ev.append((t, d["id"]))
    _fechar_adiamentos(tmp_path, {"dou"}, D())
    assert ev == [("alarme.fechado", 1)]
