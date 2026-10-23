"""Servidor local das páginas reais gravadas (testes/paginas/<motor>/): o mesmo caminho, e o domínio da fonte trocado pelo
do servidor dentro das páginas (a extração só aceita links do mesmo domínio)."""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def servir(motor: str, dominios: list[str]):
    pasta = Path("testes/paginas") / motor
    indice = json.loads((pasta / "indice.json").read_text(encoding="utf-8"))
    gravadas = {urlsplit(u).path.rstrip("/"): (pasta / x["arquivo"], x.get("tipo") or "text/html") for u, x in indice.items() if x.get("arquivo")}
    base = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            g = gravadas.get(urlsplit(self.path).path.rstrip("/"))
            corpo = g[0].read_bytes() if g else b""
            for d in dominios:
                corpo = corpo.replace(d.encode(), base["url"].encode())
            self.send_response(200 if g else 404)
            self.send_header("Content-Type", g[1] if g else "text/plain")
            self.end_headers()
            self.wfile.write(corpo)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    base["url"] = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, base["url"]


def motor(motor: str, base: str, dominios: list[str], tmp_path):
    from eldorado.motores.canal.motor import MotorCanal
    texto = (Path("eldorado/motores/canal/config") / f"{motor}.toml").read_text(encoding="utf-8")
    for d in dominios:
        texto = texto.replace(d, base)
    texto = texto.replace("paginas_dos_achados = true", "paginas_dos_achados = false").replace("seguir_oficial = true", "seguir_oficial = false")
    texto = re.sub(r'degraus = \[[^\]]*\]', 'degraus = ["api"]', texto)
    (tmp_path / f"{motor}.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / f"{motor}.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m
