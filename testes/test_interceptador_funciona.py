"""O Interceptador funcionando (24/10/2026): ele não produzia nada (37 min, nenhuma tentativa registrada)."""
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from eldorado.motores.acesso.api import DegrauAPI
from eldorado.motores.acesso.escada import Escada
from eldorado.motores.pilotos.interceptador import Interceptador, Livro
from eldorado.base.nucleo.eventos import ler

TEXTO = ("Edital de chamamento público nº 7/2026. Objeto: fomento a projetos culturais de organizações da sociedade civil. "
         "Inscrições de 01/11/2026 a 30/11/2026. Valor total de R$ 300.000,00. ") * 4


def _servidor():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if self.path.startswith("/noticia"):
                corpo = f"<main><p>{TEXTO}</p><a href='/edital-7-2026.html'>Edital de chamamento 7/2026 (íntegra)</a></main>"
            else:
                corpo = f"<main><h1>Edital nº 7/2026</h1><p>{TEXTO}</p></main>"
            self.wfile.write(f"<html><body>{corpo}</body></html>".encode())
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def test_o_livro_so_com_o_link_de_divulgacao_tem_material(bancos, diario, tmp_path):
    srv, base = _servidor()
    try:
        it = Interceptador(bancos["biblioteca"], diario, Escada([DegrauAPI()], intervalo_padrao=0, tentativas=1, tempo_limite=10))
        lv = Livro("L1", "Edital de chamamento público nº 7/2026", None, None, f"{base}/noticia-edital", "sem", None, {}, set())
        r = it.investigar(lv, [1])
    finally:
        srv.shutdown()
    assert r["achado"] is not None and r["abordagem"] == 1                       # antes: sem link oficial, nenhuma abordagem
    assert [e for e in ler(tmp_path / "eventos") if e.tipo == "tentativa.registrada"]


def test_toda_abordagem_fica_registrada_e_o_prazo_adia(bancos, diario, tmp_path):
    it = Interceptador(bancos["biblioteca"], diario, Escada([], intervalo_padrao=0))
    lv = Livro("L2", "Um edital sem nenhum link", None, None, None, "sem", None, {}, set())
    r = it.investigar(lv, [1, 3, 9])
    assert r["esgotado"] and lv.tentadas == {1, 3, 9}                             # tentadas e registradas (sem material)
    regs = [e for e in ler(tmp_path / "eventos") if e.tipo == "tentativa.registrada" and e.dados["livro_id"] == "L2"]
    assert len(regs) == 3 and all('"sem material": true' in e.dados["resultado"] for e in regs)
    lv3 = Livro("L3", "Outro edital", None, None, None, "sem", None, {}, set())
    assert it.investigar(lv3, [1, 3], ate=time.monotonic() - 1) == {"livro": "L3", "abordagem": None, "achado": None, "esgotado": False,
                                                                    "adiado": True}   # o prazo: continua na próxima passagem


def test_o_canivete_nos_achados_dos_pilotos():
    """25/10/2026: o canivete suíço dos motores também nos achados do Espião e do Interceptador."""
    from eldorado.base.cerebro.encaminhamento import _canivete
    from eldorado.base.nucleo.contratos import Achado
    a = Achado(id="x", motor="interceptador", titulo="Edital 7/2026", link_divulgacao="https://exemplo.org/edital", encontrado_em="2026-10-25",
               dados={}, documento={"url": "https://exemplo.org/edital", "sha256": "s", "paginas": [TEXTO]})
    c = _canivete(a).dados["canivete"]
    assert c.get("valores") and c.get("datas")                                        # o valor e as datas do edital


def test_o_canivete_de_busca_soma_as_rotas():
    """25/10/2026: a metabusca não depende de uma rota só; os resultados de várias rotas se somam, e a que falha descansa."""
    from eldorado.motores.descoberta.metabusca import Metabusca
    from eldorado.motores.descoberta.pistas import Pista
    mb = Metabusca(buscar=lambda u: None)
    chamadas = []

    def rota(nome, links, falha=False):
        def fn(t, lim):
            chamadas.append(nome)
            if falha:
                raise RuntimeError("bloqueado")
            return [Pista(titulo=x, link=x, origem=nome) for x in links]
        return (nome, fn)
    mb.rotas = lambda termos: [rota("a", ["https://1", "https://2"]), rota("b", [], falha=True), rota("c", ["https://2/", "https://3"])]
    pistas, relato = mb.consultar("edital cultura", limite=10)
    assert [p.link for p in pistas] == ["https://1", "https://2", "https://3"] and chamadas == ["a", "b", "c"]
    assert any(r.startswith("b: falhou") for r in relato) and not mb._livre("b") and mb._livre("c")
