"""A IA dos pilotos: a IA propõe; o sistema valida (o trecho tem de existir); sem o modelo, erro claro, nunca simulação."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from eldorado.base.missao import itens as I
from eldorado.base.nucleo.ia import IA, SemIA, _json, comprovar, trecho_existe

DOC = ["Edital nº 3/2026. O prazo para recurso é de 5 (cinco) dias úteis a contar da publicação do resultado.\n\n"
       "Anexo I — Plano de trabalho. Anexo II — Declaração.\n\nO valor total é de R$ 300.000,00."]
RESPOSTA = {"itens": [{"item": "Prazo de recurso", "valor": "5 dias úteis", "trecho": "O prazo para recurso é de 5 (cinco) dias úteis", "pagina": 1},
                      {"item": "Anexos", "valor": "Anexo III", "trecho": "Anexo III — Orçamento detalhado", "pagina": 1},
                      {"item": "Objeto", "valor": "x", "trecho": "Edital nº 3/2026", "pagina": 1}]}


@pytest.fixture(scope="module")
def modelo():
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200 if self.path == "/health" else 404)
            self.end_headers()

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            corpo = json.dumps({"choices": [{"message": {"content": "<think>pensando</think>```json\n" + json.dumps(RESPOSTA) + "\n```"}}],
                                "usage": {"prompt_tokens": 300, "completion_tokens": 80}}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(corpo)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_a_ia_propoe_e_o_sistema_valida(modelo):
    aceitos, uso = comprovar(IA(modelo), ["Prazo de recurso", "Anexos"], DOC, "Edital nº 3/2026", I.DOZE)
    assert set(aceitos) == {"Prazo de recurso"} and aceitos["Prazo de recurso"]["pagina"] == 1                     # só o que tem prova
    assert uso.propostas == 3 and uso.aceitas == 1 and uso.tokens_entrada == 300
    assert any("não existe no documento" in r for r in uso.recusas) and any("fora dos itens que faltam" in r for r in uso.recusas)


def test_sem_o_modelo_erro_claro_nunca_simulacao():
    with pytest.raises(SemIA):
        IA("http://127.0.0.1:9").pedir("comprovar", "x")


def test_trecho_normalizado_e_resposta_com_pensamento():
    assert trecho_existe("prazo para RECURSO é de 5 (cinco)", DOC[0]) and not trecho_existe("prazo de 30 dias", DOC[0])
    assert _json("<think>a</think>```json\n{\"itens\": []}\n```") == {"itens": []}


def test_interceptador_entrega_o_item_da_ia_ao_cartorio(modelo, gravador, bancos, diario, tmp_path):
    import msgspec
    from conftest import AGORA, ev

    from eldorado.base.cartorio.cartorio import Cartorio
    from eldorado.base.missao.oportunidades import MissaoOportunidades
    from eldorado.base.nucleo.eventos import ler
    from eldorado.motores.pilotos.interceptador import Interceptador, Livro
    assert gravador.aplicar([ev("livro.criado", id="L", missao="oportunidades", chave="k", titulo="Edital nº 3/2026", orgao="Secult", uf="GO",
                                estrela="sem", selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
                             ev("livro.passagem", livro_id="L", de=None, para="recepcao", em=AGORA, autorizado_por="regencia"),
                             ev("livro.passagem", livro_id="L", de="recepcao", para="certificacao", em=AGORA, autorizado_por="regencia"),
                             ev("livro.passagem", livro_id="L", de="certificacao", para="preparacao", em=AGORA, autorizado_por="regencia")]).ok
    lv = Livro("L", "Edital nº 3/2026", "Secult", "https://goias.gov.br/e.pdf", None, "sem", None, {}, set())
    lv_falta = ["Prazo de recurso", "Anexos"]
    lv.__class__ = type("LivroTeste", (Livro,), {"faltam": property(lambda self: lv_falta)})
    inter = Interceptador(bancos["biblioteca"], diario, None, ia=IA(modelo))
    a = inter._achado(lv, 1, [])                                                                         # sem documentos: sem achado
    assert a is None
    inter._ler = lambda u, profunda=False, escada=None: (u, type("L", (), {"paginas": [type("P", (), {"texto": DOC[0]})()], "alertas": [],
                                                                           "dados": {}, "tipo": "pdf"})(), b"")
    a = inter._achado(lv, 1, ["https://goias.gov.br/e.pdf"])
    assert a.dados["itens"]["Prazo de recurso"]["trecho"].startswith("O prazo para recurso") and a.dados["ia"]["aceitas"] == 1
    from eldorado.base.cerebro.encaminhamento import Encaminhamento
    from eldorado.base.nucleo.registro import Registro
    entregue = Encaminhamento(bancos["biblioteca"], diario, Registro(), inter)._entregar(a, "interceptador")
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([entregue])                   # etapa 4: valida e armazena
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok
    assert bancos["biblioteca"].execute("SELECT valor FROM certidao WHERE livro_id='L' AND item='Prazo de recurso'").fetchone()[0] == "5 dias úteis"
    assert msgspec  # noqa
