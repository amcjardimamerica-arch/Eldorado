"""O motor dos mecanismos de incentivo nas páginas reais gravadas do gov.br (23/10/2026)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/empresas-editais-incentivados")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))
GRAVADAS = {urlsplit(u).path: PASTA / x["arquivo"] for u, x in INDICE.items() if x.get("arquivo")}


@pytest.fixture(scope="module")
def govbr():
    base = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            g = GRAVADAS.get(urlsplit(self.path).path)
            self.send_response(200 if g else 404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(g.read_bytes().replace(b"https://www.gov.br", base["url"].encode()) if g else b"")   # o mesmo domínio, como na fonte
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    base["url"] = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield base["url"]
    srv.shutdown()


def test_os_chamamentos_do_pronas_e_do_pronon(govbr, tmp_path):
    texto = Path("eldorado/motores/canal/config/empresas-editais-incentivados.toml").read_text(encoding="utf-8").replace("https://www.gov.br", govbr)
    texto = texto.replace("paginas_dos_achados = true", "paginas_dos_achados = false").replace("seguir_oficial = true", "seguir_oficial = false")
    texto = texto.replace('degraus = ["api", "leve"]', 'degraus = ["api"]').replace('degraus = ["api", "leve", "local"]', 'degraus = ["api"]')
    (tmp_path / "e.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "e.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    titulos = [a.titulo for a in m.buscar(None)]
    assert "Chamamento Público nº 07/2026 - Secretaria Executiva (SE) | PRONAS/PCD" in titulos
    assert "Chamamento Público nº 06/2026 - Secretaria Executiva (SE) | PRONON" in titulos
    assert any(t.startswith("Credenciamento") for t in titulos) and any(t.startswith("Apresentação de Projetos") for t in titulos)
    assert not [t for t in titulos if any(x in t for x in ("Ouvidoria", "Contatos", "Documentação", "Marcos legais", "Vacinação", "Campanhas"))]
