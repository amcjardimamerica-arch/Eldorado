"""Um servidor local que imita os comportamentos reais dos sites, para testar a escada de acesso sem internet."""
import json
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

PAGINA = b"<!doctype html><html><head><title>Editais</title></head><body><h1>Editais abertos</h1><p>" + b"Chamamento publico para organizacoes da sociedade civil. " * 5 + b"</p></body></html>"
JS = ("<!doctype html><html><head><title>Portal</title></head><body><h1>Editais</h1><ul id='l'></ul>"
      "<script>fetch('/dados.json').then(r=>r.json()).then(d=>{const u=document.getElementById('l');d.forEach(e=>{const li=document.createElement('li');"
      "li.textContent=e.titulo;u.appendChild(li);});document.body.setAttribute('data-pronto','1');});</script></body></html>").encode()
CAPTCHA = b"<!doctype html><html><body><div class='g-recaptcha'>Please complete the captcha to continue. Verify you are human.</div></body></html>"


class Estado:
    def __init__(self):
        self.acessos = Counter()
        self.instavel = 0
        self.porta = 0


def criar_servidor(extra=None):
    """extra: {caminho: (status, corpo, tipo)} para rotas próprias de cada teste."""
    estado = Estado()
    extra = extra or {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def responder(self, status, corpo, tipo="text/html; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            ua = self.headers.get("User-Agent", "")
            cliente = "navegador" if "Chrome" in ua or "Mozilla" in ua else "outro"
            caminho = self.path.split("?")[0]
            estado.acessos[(caminho, cliente)] += 1
            if caminho in extra:
                st, corpo, tipo = extra[caminho]
                return self.responder(st, corpo() if callable(corpo) else corpo, tipo)
            if caminho == "/robots.txt":
                return self.responder(200, b"User-agent: *\nDisallow: /restrito/\nCrawl-delay: 2\n", "text/plain")
            if caminho in ("/ok.html", "/restrito/pagina.html"):
                return self.responder(200, PAGINA)
            if caminho == "/api.json":
                return self.responder(200, json.dumps({"editais": [{"titulo": "Edital 1"}]}).encode(), "application/json")
            if caminho == "/so-navegador.html":
                return self.responder(403, b"Forbidden") if cliente == "outro" else self.responder(200, PAGINA)
            if caminho == "/captcha.html":
                return self.responder(200, CAPTCHA)
            if caminho == "/js.html":
                return self.responder(200, JS)
            if caminho == "/dados.json":
                return self.responder(200, json.dumps([{"titulo": f"Edital de chamamento nº {i}/2026"} for i in range(1, 51)]).encode(), "application/json")
            if caminho == "/instavel.html":
                estado.instavel += 1
                return self.responder(503, b"Service Unavailable") if estado.instavel <= 2 else self.responder(200, PAGINA)
            if caminho == "/cdx/search/cdx":
                linhas = [["urlkey", "timestamp", "original", "statuscode"], ["x", "20260901120000", "http://127.0.0.1:9/edital.html", "200"]]
                return self.responder(200, json.dumps(linhas).encode(), "application/json")
            if caminho.startswith("/web/20260901120000id_/"):
                return self.responder(200, PAGINA.replace(b"Editais abertos", b"Copia arquivada do edital"))
            return self.responder(404, b"nao encontrado")

    class S(ThreadingMixIn, HTTPServer):
        daemon_threads = True

    srv = S(("127.0.0.1", 0), H)
    estado.porta = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, estado
