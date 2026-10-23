"""O motor do Diário Oficial de Goiás nas páginas reais gravadas (23/10/2026): o critério de pronto da orientação."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from eldorado.motores.canal.motor import MotorCanal

PASTA = Path("testes/paginas/do-goias")
INDICE = json.loads((PASTA / "indice.json").read_text(encoding="utf-8"))


def _gravada(caminho: str) -> tuple[bytes, str] | None:
    if "/edicoes_from_data/" in caminho:                            # todo dia serve a edição gravada de 22/10
        caminho = "/apifront/portal/edicoes/edicoes_from_data/2026-10-22.json"
    for url, x in INDICE.items():
        if urlsplit(url).path == caminho and x.get("arquivo"):
            return (PASTA / x["arquivo"]).read_bytes(), x["tipo"]
    return None


@pytest.fixture(scope="module")
def diario():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            g = _gravada(urlsplit(self.path).path.rstrip("/") or "/")
            self.send_response(200 if g else 404)
            self.send_header("Content-Type", g[1] if g else "text/plain")
            self.end_headers()
            self.wfile.write(g[0] if g else b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def motor(base, tmp_path):
    texto = Path("eldorado/motores/canal/config/do-goias.toml").read_text(encoding="utf-8")
    texto = texto.replace("https://diariooficial.abc.go.gov.br", base).replace("https://goias.gov.br", base).replace("https://www.goias.gov.br", base)
    (tmp_path / "do-goias.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "do-goias.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_entrega_o_chamamento_com_o_texto_integral_e_veta_o_ruido(diario, tmp_path):
    achados = list(motor(diario, tmp_path).buscar(None))
    titulos = [a.titulo for a in achados]
    assert "Aviso de Chamamento Público Nº 02-2025 – SGG 3ª Retificação" in titulos
    a = next(a for a in achados if a.titulo.startswith("Aviso de Chamamento Público Nº 02-2025"))
    assert "Credenciamento nº 02/2025-SGG" in a.documento["paginas"][0] and a.link_oficial.endswith("/publicacoes_ver_conteudo/752542")
    assert not [t for t in titulos if any(x in t.lower() for x in ("citação", "intimação", "convocação", "extrato", "portaria"))]
    assert len(titulos) == len(set(titulos))                                                        # hoje e ontem não duplicam


def test_sem_mudanca_na_segunda_leitura(diario, tmp_path):
    m = motor(diario, tmp_path)
    list(m.buscar(None))
    assert list(m.buscar(None)) == [] and any("sem mudança" in r for r in m.relatorio)
