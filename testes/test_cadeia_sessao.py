"""A cadeia com sessão (canivete, 23/10/2026): a página abre a sessão (cookie e código) e a tabela só responde por POST,
na mesma sessão e com o código, como a PRT 18ª Região."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from eldorado.motores.canal.motor import MotorCanal

CODIGO = "1eee8a72d63e4a39fbf3969c3da8a771"
PAGINA = Path("testes/paginas/ministerios-publicos")


@pytest.fixture
def prt():
    real = PAGINA / next(x["arquivo"] for u, x in json.loads((PAGINA / "indice.json").read_text()).items() if "editais-de-destinacao" in u)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Set-Cookie", "sessao=abc; Path=/")
            self.end_headers()
            self.wfile.write(real.read_bytes())

        def do_POST(self):
            corpo = parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
            ok = "sessao=abc" in (self.headers.get("Cookie") or "") and corpo.get(CODIGO) == ["1"] and corpo.get("task") == ["editaisdestinacaorecursosoubens"]
            dados = {"aaData": [["Goiânia", "21/10/2026", "123/2026", "Procedimento 000456.2025.18.000/7", "edital123.pdf"]]} if ok else {"aaData": []}
            self.send_response(200 if ok else 403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(dados).encode())
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_a_tabela_por_post_na_sessao_da_pagina(prt, tmp_path):
    texto = Path("eldorado/motores/canal/config/mptgo-destinacao.toml").read_text(encoding="utf-8").replace("https://www.prt18.mpt.mp.br", prt)
    texto = texto.replace("https://mpt.mp.br", prt).replace("documentos = true", "documentos = false").replace("paginas_dos_achados = true", "paginas_dos_achados = false")
    texto = texto.replace('degraus = ["api", "leve", "local"]', 'degraus = ["api"]').replace('degraus = ["api", "leve"]', 'degraus = ["api"]')
    (tmp_path / "m.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "d", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    a = [x for x in m.buscar(None) if "123/2026" in x.titulo]
    assert a and a[0].titulo == "Edital de destinação de recursos ou bens nº 123/2026 — Procedimento 000456.2025.18.000/7"
    assert a[0].link_divulgacao.endswith("task=baixa&format=raw&arq=edital123.pdf")
