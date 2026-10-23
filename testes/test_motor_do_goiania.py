"""O motor do Diário Oficial de Goiânia nas páginas reais gravadas (23/10/2026): o critério de pronto da orientação."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/do-goiania")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
PDFS = {urlsplit(u).path: PASTA / x["arquivo"] for u, x in INDICE.items() if u.endswith(".pdf") and x.get("arquivo")}
# a lista REAL gravada; só a segunda edição (8888, não gravada) aponta para a 8740 gravada, que tem um chamamento
_REAL = next(PASTA / x["arquivo"] for u, x in INDICE.items() if "lista_diarios" in u and x.get("arquivo"))
LISTA = _REAL.read_bytes().replace(b"do_20261021_000008888.pdf", b"do_20260313_000008740.pdf", 1)


@pytest.fixture(scope="module")
def prefeitura():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            caminho = urlsplit(self.path).path
            corpo, tipo = (LISTA, "text/html") if "lista_diarios" in caminho else ((PDFS[caminho].read_bytes(), "application/pdf") if caminho in PDFS else (None, None))
            self.send_response(200 if corpo else 404)
            self.send_header("Content-Type", tipo or "text/plain")
            self.end_headers()
            self.wfile.write(corpo or b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def motor(base, tmp_path):
    texto = Path("eldorado/motores/canal/config/do-goiania.toml").read_text(encoding="utf-8")
    for d in ("https://www.goiania.go.gov.br", "https://queridodiario.ok.org.br", "https://diariooficial.goiania.go.gov.br", "https://goiania.go.gov.br"):
        texto = texto.replace(d, base)
    (tmp_path / "do-goiania.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "do-goiania.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_entrega_os_atos_de_chamamento_e_veta_o_ruido(prefeitura, tmp_path):
    achados = list(motor(prefeitura, tmp_path).buscar(None))              # o Querido Diário fora do ar no teste: a principal basta
    titulos = [a.titulo for a in achados]
    assert "CHAMAMENTO PÚBLICO Nº 001/2026" in titulos
    a = next(a for a in achados if a.titulo == "CHAMAMENTO PÚBLICO Nº 001/2026")
    assert "Secretaria Municipal de Administração" in a.dados["orgao"] and a.documento["tipo"] == "ato"
    assert a.documento["paginas"][0].startswith("CHAMAMENTO PÚBLICO Nº 001/2026") and a.link_oficial.endswith("8740.pdf#ato-53")
    assert not [t for t in titulos if t.startswith(("EXTRATO", "PORTARIA", "DECRETO", "TERMO DE HOMOLOGA"))]
    assert not [a for a in achados if "requereu" in a.documento["paginas"][0][:600]]             # as licenças ambientais
    assert len(titulos) == len(set(a.link_oficial for a in achados))


def test_sem_mudanca_na_segunda_leitura(prefeitura, tmp_path):
    m = motor(prefeitura, tmp_path)
    list(m.buscar(None))
    assert list(m.buscar(None)) == []
