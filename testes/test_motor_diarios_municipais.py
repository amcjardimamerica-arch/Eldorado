"""O motor dos diários municipais de Goiás nas páginas reais gravadas: a edição nº 3730 da AGM (23/10/2026)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/novo-diarios-municipais-go")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
HOME = PASTA / next(x["arquivo"] for u, x in INDICE.items() if u.endswith("/agm/") and x.get("arquivo"))
PDF = PASTA / next(x["arquivo"] for u, x in INDICE.items() if u.endswith("c569.pdf") and x.get("arquivo"))


@pytest.fixture(scope="module")
def agm():
    base = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            caminho = urlsplit(self.path).path
            if caminho.startswith("/agm"):
                corpo, tipo = HOME.read_bytes().replace(b"https://www-storage.voxtecnologia.com.br/", f"{base['url']}/storage/".encode()), "text/html"
            elif caminho.startswith("/storage"):
                corpo, tipo = PDF.read_bytes(), "application/pdf"
            else:
                corpo, tipo = None, None
            self.send_response(200 if corpo else 404)
            self.send_header("Content-Type", tipo or "text/plain")
            self.end_headers()
            self.wfile.write(corpo or b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    base["url"] = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield base["url"]
    srv.shutdown()


def motor(base, tmp_path):
    texto = Path("eldorado/motores/canal/config/novo-diarios-municipais-go.toml").read_text(encoding="utf-8")
    texto = texto.replace("https://www.diariomunicipal.com.br", base).replace("https://queridodiario.ok.org.br", base)
    texto = texto.replace('degraus = ["api", "leve"]', 'degraus = ["api"]')
    (tmp_path / "d.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "d.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_entrega_com_o_municipio_e_veta_o_ruido(agm, tmp_path):
    achados = list(motor(agm, tmp_path).buscar(None))
    cred = [a for a in achados if a.dados.get("localidade") == "Buriti De Goiás" and "CREDENCIAMENTO" in a.documento["paginas"][0][:200].upper()]
    assert cred and cred[0].documento["tipo"] == "ato"
    textos = [(a.titulo + " " + a.documento["paginas"][0][:400]).lower() for a in achados]
    for vetado in ("licença prêmio", "rescisão", "pregão eletrônico", "extrato"):
        assert not [t for t in textos if vetado in t], vetado
    assert len({a.dados.get("localidade") for a in achados}) >= 1 and all(a.dados.get("localidade") for a in achados)
