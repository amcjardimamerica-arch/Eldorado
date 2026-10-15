"""15/10/2026 (titular): erro de acesso volta em 30 min; 5 erros iguais = fora da fila; leitura parcial volta à fila;
dois links por oportunidade com curadoria objetiva do link oficial."""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from src import fila_retentativa as FR


class Retentativa(unittest.TestCase):
    def setUp(self):
        self.p = mock.patch.object(FR, "ARQ", Path(tempfile.mkdtemp()) / "f.json"); self.p.start()
        FR._CACHE = None
        self.t0 = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.p.stop(); FR._CACHE = None

    def test_volta_em_30_minutos(self):
        u = "https://x.go.gov.br/editais"
        FR.falhou(u, "m1", "tempo esgotado", agora=self.t0)
        self.assertTrue(FR.aguardando(u, self.t0 + timedelta(minutes=29)))
        self.assertFalse(FR.aguardando(u, self.t0 + timedelta(minutes=30)))
        self.assertEqual(FR.devidas("m1", self.t0 + timedelta(minutes=31)), [u])
        self.assertEqual(FR.devidas("outro", self.t0 + timedelta(minutes=31)), [])

    def test_cinco_erros_iguais_sai_da_fila_e_erro_diferente_recomeca(self):
        u = "https://y.go.gov.br/"
        for k in range(4):
            r = FR.falhou(u, "m1", "HTTP 503", agora=self.t0 + timedelta(minutes=30 * k))
        self.assertEqual((r["estado"], r["tentativas"]), ("aguardando", 4))
        r = FR.falhou(u, "m1", "tempo esgotado", agora=self.t0 + timedelta(minutes=150))
        self.assertEqual(r["tentativas"], 1)                                   # erro diferente recomeça
        for k in range(4):
            r = FR.falhou(u, "m1", "tempo esgotado", agora=self.t0 + timedelta(minutes=180 + 30 * k))
        self.assertEqual(r["estado"], "fora_da_fila")
        self.assertTrue(FR.fora_da_fila(u))
        self.assertEqual(FR.resumo()["fora_da_fila"], 1)
        self.assertTrue(FR.reabrir(u)); self.assertFalse(FR.fora_da_fila(u))

    def test_sucesso_tira_da_fila(self):
        u = "https://z.go.gov.br/"
        FR.falhou(u, "m1", "HTTP 403", agora=self.t0); FR.sucesso(u)
        self.assertFalse(FR.aguardando(u, self.t0)); self.assertEqual(FR.resumo()["aguardando_retentativa"], 0)

    def test_rotulo_do_erro(self):
        import socket
        self.assertEqual(FR.tipo_erro(socket.timeout("timed out")), "tempo esgotado")
        self.assertEqual(FR.tipo_erro(None, 403), "HTTP 403")


class Curadoria(unittest.TestCase):
    def setUp(self):
        FR._CACHE = {"fila": {}, "fora_da_fila": {}}

    def tearDown(self):
        FR._CACHE = None

    def test_classes(self):
        from src import curadoria_links as C
        self.assertEqual(C.classe("https://editaisdobrasil.com/x"), "agregador ou replicador")
        self.assertEqual(C.classe("https://anapolis.go.gov.br/edital.pdf"), "órgão público")
        self.assertEqual(C.classe("https://pncp.gov.br/pncp-api/v1/orgaos/1/compras/2026/5/arquivos/1"), "arquivo do órgão no PNCP")
        self.assertEqual(C.classe("https://pncp.gov.br/app/editais/1/2026/5"), "página do PNCP (não é o documento)")
        self.assertEqual(C.classe("https://www.fundacaoboticario.org.br/edital", "Fundação Grupo Boticário"), "site do financiador")

    def test_dois_links_e_curadoria(self):
        from src import curadoria_links as C
        agora = datetime(2026, 10, 15, tzinfo=timezone.utc)
        r = {"id": "a", "titulo": "Chamamento 3/2026", "orgao": "Prefeitura de Anápolis", "url": "https://editaisdobrasil.com/x",
             "link_oficial": "https://editaisdobrasil.com/x", "itens": {"Objeto": {"valor": "seleção de OSC"}}}
        x = C.curar(r, None, agora)
        self.assertEqual(x["curadoria"], "reprovado"); self.assertIsNone(x["link_oficial"])     # agregador não vale como oficial
        cert = {"link_oficial": "https://anapolis.go.gov.br/edital.pdf", "ainda_faltam": [], "em": "2026-10-14T10:00:00+00:00",
                "itens": {"Objeto": {"trecho": "1.1 Seleção de OSC para Termo de Colaboração", "documento": "https://anapolis.go.gov.br/edital.pdf", "pagina": 1}}}
        y = C.curar(r, cert, agora)
        self.assertEqual((y["curadoria"], y["link_acesso"], y["link_oficial"]), ("aprovado", "https://editaisdobrasil.com/x", "https://anapolis.go.gov.br/edital.pdf"))
        self.assertFalse(y["mesmo_link"])
        self.assertEqual((y["trecho"]["fonte"], y["trecho"]["pagina"]), ("documento oficial", 1))
        z = C.curar({**r, "url": "https://anapolis.go.gov.br/edital.pdf", "link_oficial": None}, cert, agora)
        self.assertTrue(z["captada_direto_na_fonte_oficial"])                                     # mesmo link só na fonte oficial
        w = C.curar({**r, "link_oficial": None}, {**cert, "ainda_faltam": ["Valor"]}, agora)
        self.assertEqual(w["curadoria"], "em curadoria")


if __name__ == "__main__":
    unittest.main()
