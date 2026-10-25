"""A fase 1 do Comandante e do Aprendizado (titular, 25/10/2026): o Arquivo do Cérebro preparado, a memória FTS5 e a IA
única por cargos (cada cargo na sua vaga, sem interromper os outros)."""

import json
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

from eldorado.base.aprendizado.memoria import buscar, no_memorizar
from eldorado.base.nucleo.eventos import criar, ler


def test_a_memoria_alimenta_busca_e_expira(bancos, gravador, diario, tmp_path):
    agora = datetime.now(timezone.utc)
    velho = (agora - timedelta(days=40)).isoformat()
    assert gravador.aplicar(
        [
            criar(
                "alarme.aberto",
                "t",
                {
                    "gravidade": "alta",
                    "modulo": "piloto:espiao",
                    "aberto_em": agora.isoformat(),
                    "mensagem": "o voo permanente do Espião falhou: a ponte BR recusou o domínio da CESE",
                },
            )
        ]
    ).ok
    no_memorizar([], {"dados": str(tmp_path)}, SimpleNamespace(diario=diario))
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    c = bancos["cerebro"]
    linhas, ms = buscar(c, "recusou cese")
    assert linhas and linhas[0]["tabela"] == "alarme" and "CESE" in linhas[0]["trecho"] and ms < 50
    c.execute("INSERT INTO memoria(tabela, ref, texto, em) VALUES ('alarme', 'antigo', 'um registro de 40 dias', ?)", (velho,))
    c.commit()
    n0 = c.execute("SELECT COUNT(*) FROM memoria").fetchone()[0]
    for f in (tmp_path / "eventos").rglob("*.jsonl"):
        f.unlink()
    no_memorizar([], {"dados": str(tmp_path)}, SimpleNamespace(diario=diario))  # a segunda passagem: só o novo, e expira o velho
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert c.execute("SELECT COUNT(*) FROM memoria").fetchone()[0] == n0 - 1  # os 30 dias do temporário


def test_a_ia_unica_por_cargos_sem_interromper(monkeypatch, tmp_path):
    vistos, inicio = [], {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        def do_POST(self):
            d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            inicio[d.get("id_slot")] = time.monotonic()
            vistos.append(d)
            time.sleep(0.6)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"choices": [{"message": {"content": '{"ok": 1}'}}], "usage": {}}).encode())

    s = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        from eldorado.base.nucleo.ia import IA

        monkeypatch.setattr(IA, "disponivel", lambda self: True)  # o servidor de ensaio (os testes desligam a IA)
        url = f"http://127.0.0.1:{s.server_address[1]}"
        ias = [IA(url, cargo_nome=n) for n in ("comandante", "espiao", "interceptador")]
        t0 = time.monotonic()
        fios = [threading.Thread(target=ia.pedir, args=("teste", "um pedido")) for ia in ias]
        [f.start() for f in fios]
        [f.join() for f in fios]
        assert time.monotonic() - t0 < 1.5  # os três juntos: nenhum esperou o outro
    finally:
        s.shutdown()
    assert sorted(d["id_slot"] for d in vistos) == [0, 1, 2]  # cada cargo na sua vaga
    assert all(d["cache_prompt"] for d in vistos) and any("Comandante" in d["messages"][0]["content"] for d in vistos)
