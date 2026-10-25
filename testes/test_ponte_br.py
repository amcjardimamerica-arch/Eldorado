"""A ponte da HostGator (25/10/2026): o mesmo protocolo do ponte.php do Eldorado0 (o pedido assinado com HMAC-SHA256)."""
import base64
import hashlib
import hmac
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from eldorado.motores.acesso import ponte_br
from eldorado.motores.acesso.escada import Indisponivel

CHAVE = "uma frase longa de teste para a ponte"


def _ponte_de_ensaio():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):                                     # como o ponte.php: confere a idade e a assinatura
            p = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            ok = abs(time.time() - p["ts"]) <= 300 and hmac.compare_digest(
                hmac.new(CHAVE.encode(), f"{p['ts']}\n{p['url']}".encode(), hashlib.sha256).hexdigest(), p["assinatura"])
            r = {"ok": True, "status": 200, "url_final": p["url"], "cabecalhos": {"Content-Type": "application/json"},
                 "corpo_b64": base64.b64encode(b'[{"title":"Edital CESE 2026"}]').decode()} if ok else {"ok": False, "erro": "assinatura invalida"}
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(r).encode())
    s = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def test_a_ponte_le_os_dominios_da_lista_com_o_pedido_assinado(monkeypatch):
    s = _ponte_de_ensaio()
    try:
        monkeypatch.setenv("ELDORADO_PONTE_URL", f"http://127.0.0.1:{s.server_address[1]}/ponte.php")
        monkeypatch.setenv("ELDORADO_PONTE_CHAVE", CHAVE)
        assert ponte_br.usar("https://cese.org.br/wp-json/wp/v2/edital") and not ponte_br.usar("https://exemplo.org/x")
        r = ponte_br.buscar("https://cese.org.br/wp-json/wp/v2/edital")
        assert r.status == 200 and b"Edital CESE" in r.conteudo and "ponte BR" in r.alertas[0]
        monkeypatch.setenv("ELDORADO_PONTE_CHAVE", "a chave errada")
        with pytest.raises(Indisponivel):
            ponte_br.buscar("https://cese.org.br/wp-json/wp/v2/edital")
    finally:
        s.shutdown()


def test_sem_os_segredos_a_ponte_fica_de_fora(monkeypatch):
    monkeypatch.delenv("ELDORADO_PONTE_URL", raising=False)
    assert not ponte_br.usar("https://cese.org.br/")


def test_a_ponte_esta_no_canivete_de_todos_os_motores(tmp_path):
    """25/10/2026 (a titular): a ponte como ferramenta do canivete de todo motor, na escada depois dos degraus da nuvem."""
    from pathlib import Path

    from eldorado.motores.canal.motor import MotorCanal
    for cfg in sorted(Path("eldorado/motores/canal/config").glob("*.toml")):
        m = MotorCanal(cfg, tmp_path / "dados")
        nomes = [d.nome for d in m.escada.degraus]
        if m.cfg.canivete.ponte_br:
            i = next(k for k, n in enumerate(nomes) if n.startswith("P ·"))
            assert all(not n.startswith(("4 ", "5 ", "6 ", "7 ")) for n in nomes[:i]), f"{cfg.stem}: a ponte antes dos degraus pesados"
