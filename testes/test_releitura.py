"""A releitura dos documentos herdados sem texto (24/10/2026): o texto vai para o próprio documento herdado; a tentativa,
para o aprendizado do Cérebro."""
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from eldorado.base.cartorio.releitura import reler
from eldorado.base.nucleo.eventos import criar, ler

PAGINA = "<html><body><main><h1>Edital de Fomento 2026</h1><p>As inscrições vão até 30/11/2026. Valor total de R$ 500 mil.</p></main></body></html>"


def test_o_documento_herdado_ganha_o_texto(bancos, gravador, diario, tmp_path):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGINA.encode())
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/edital.html"
    try:
        assert gravador.aplicar([criar("documento.registrado", "migracao", {"url": url, "sha256": "herdado-1", "tipo": None, "paginas": None,
                                                                            "obtido_em": "2026-10-22T18:58:36+00:00"})]).ok
        r = reler(tmp_path, diario, limite=5, orcamento_s=30)
    finally:
        srv.shutdown()
    assert r["relidos"] == 1 and r["paginas"] >= 1
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    b, c = bancos["biblioteca"], bancos["cerebro"]
    did = b.execute("SELECT id FROM documento WHERE sha256 = 'herdado-1'").fetchone()[0]
    assert b.execute("SELECT COUNT(*) FROM pagina WHERE documento_id = ?", (did,)).fetchone()[0] >= 1          # no próprio documento
    assert b.execute("SELECT COUNT(*) FROM documento").fetchone()[0] == 1                                       # nenhum documento novo
    assert c.execute("SELECT resultado FROM releitura WHERE documento_id = ?", (did,)).fetchone()[0].startswith("relido")
    assert reler(tmp_path, diario, limite=5)["escolhidos"] == 0                                                  # não relê o que já tem texto
