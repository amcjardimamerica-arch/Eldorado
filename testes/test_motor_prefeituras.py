"""O motor das prefeituras nas respostas reais gravadas das 25 cidades (sondagem de 23/10/2026)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/prefeituras-50-go")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
GRAVADAS = {(urlsplit(u).hostname, "wp" if "wp-json" in u else urlsplit(u).path): PASTA / x["arquivo"] for u, x in INDICE.items() if x.get("arquivo")}


@pytest.fixture(scope="module")
def cidades():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):                                            # /<domínio da cidade>/<caminho>
            partes = urlsplit(self.path).path.split("/", 2)
            host, caminho = partes[1], "/" + (partes[2] if len(partes) > 2 else "")
            g = GRAVADAS.get((host, "wp" if "wp-json" in caminho else caminho))
            self.send_response(200 if g else 404)
            self.send_header("Content-Type", "application/json" if g and g.suffix == ".json" else "text/html")
            self.end_headers()
            self.wfile.write(g.read_bytes() if g else b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def motor(base, tmp_path):
    import re
    texto = Path("eldorado/motores/canal/config/prefeituras-50-go.toml").read_text(encoding="utf-8")
    texto = re.sub(r"https://([a-z0-9.-]+\.go\.gov\.br)", lambda m: f"{base}/{m.group(1)}", texto)
    texto = texto.replace("paginas_dos_achados = true", "paginas_dos_achados = false").replace("seguir_oficial = true ", "seguir_oficial = false ")
    texto = texto.replace('degraus = ["api", "leve", "local"]', 'degraus = ["api"]').replace('degraus = ["api", "leve"]', 'degraus = ["api"]')
    (tmp_path / "p.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "p.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_pre_filtro_dos_portais_municipais(cidades, tmp_path):
    titulos = [a.titulo for a in motor(cidades, tmp_path).buscar(None)]
    for esperado in ("EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 – PROGRAMA ORGULHO RIO-VERDENSE (BOLSA ATLETA)", "Prefeitura de Senador Canedo lança Edital Aldir Blanc 2026",
                     "EDITAL DE CHAMAMENTO PÚBLICO N° 001-CMDCA-2026", "EDITAL DE CHAMAMENTO PÚBLICO N. 002/2026"):
        assert esperado in titulos, esperado
    assert not [t for t in titulos if "<mark>" in t]                                                     # o título limpo
    for vetado in ("RESULTADO", "INEXIGIBILIDADE", "CONCURSO PÚBLICO", "vacinação", "atividades comerciais", "REGULARIZAÇÃO FUNDIÁRIA", "moradias", "notificação de lançamento"):
        assert not [t for t in titulos if vetado.lower() in t.lower()], vetado
