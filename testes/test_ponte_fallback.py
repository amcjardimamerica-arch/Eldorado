"""08/11/2026 (parecer dos motores): a ponte BR com falha passageira não encerra o degrau — o pedido direto é tentado uma
vez; e a ponte pede até 15 MB (o arquivo de programas do Transferegov tem 11 MB e era cortado em 6 MB)."""
from servidor_local import criar_servidor

from eldorado.motores.acesso import ponte_br
from eldorado.motores.acesso.api import DegrauAPI
from eldorado.motores.acesso.escada import Passageiro


def test_a_ponte_que_falha_cai_no_pedido_direto(monkeypatch):
    srv, estado = criar_servidor({"/dados.json": (200, b'{"ok": 1}', "application/json")})
    try:
        monkeypatch.setattr(ponte_br, "usar", lambda url: True)

        def falha(url, tempo_limite=40, max_bytes=ponte_br.MAX_BYTES):
            raise Passageiro("a ponte BR: falha de rede na ponte: Callback aborted")
        monkeypatch.setattr(ponte_br, "buscar", falha)
        r = DegrauAPI().buscar(f"http://127.0.0.1:{estado.porta}/dados.json", 10)
        assert r.status == 200 and r.conteudo == b'{"ok": 1}'
    finally:
        srv.shutdown()


def test_a_ponte_pede_ate_15_mb():
    import inspect
    assert ponte_br.MAX_BYTES == 15_000_000 and inspect.signature(ponte_br.buscar).parameters["max_bytes"].default == ponte_br.MAX_BYTES
