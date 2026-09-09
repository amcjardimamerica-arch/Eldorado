"""A rota importa mais que o endereço.

Estes testes guardam o que custou duas rodadas para aprender: o coletor conclui
"não há edital" quando o que houve foi rota errada, e a regra do titular sobre
fonte só se sustenta se o sistema souber, antes de gastar a requisição, o que
cada domínio pode e não pode alimentar na base.
"""
import unittest

from src.rotas_coleta import (diagnostico, exige_navegador, pode_da_nuvem, rota_de,
                              ritmo_de, serve_como_fonte)


class TesteCasamentoPorCaminho(unittest.TestCase):
    def test_caminho_vence_dominio(self):
        # bndes.gov.br responde a requisição simples; bndes.gov.br/wps/portal não.
        self.assertEqual(rota_de("https://www.bndes.gov.br/periferias")["familia"],
                         "portal_municipal_que_responde_a_requisicao")
        self.assertEqual(
            rota_de("https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios")["familia"],
            "portal_em_javascript")

    def test_www_nao_atrapalha(self):
        self.assertIsNotNone(rota_de("https://www.januaria.mg.gov.br/portal/editais/5"))

    def test_subdominio_casa(self):
        self.assertEqual(rota_de("https://chamadas.funbio.org.br/usopublico-rppn")["rota"],
                         "requisicao_simples")


class TesteRegraDeFonte(unittest.TestCase):
    def test_portal_de_noticia_nunca_e_fonte_de_prazo(self):
        serve, motivo = serve_como_fonte("https://captadores.org.br/editais/qualquer-coisa")
        self.assertFalse(serve)
        self.assertIn("prazo", motivo)

    def test_plataforma_privada_nao_e_fonte_e_aponta_a_saida(self):
        serve, motivo = serve_como_fonte("https://bllcompras.com/Process/ProcessView?param1=x")
        self.assertFalse(serve)
        self.assertIn("PNCP", motivo)

    def test_dominio_com_ssl_invalido_e_bloqueado(self):
        serve, _ = serve_como_fonte("https://fundacaomariaemilia.org.br/")
        self.assertFalse(serve)

    def test_site_do_patrocinador_serve(self):
        serve, _ = serve_como_fonte("https://www.institutolojasrenner.org.br/edital-encantando-comunidades/")
        self.assertTrue(serve)

    def test_dominio_novo_e_tratado_como_fonte(self):
        # Tentar é barato, e o resultado ensina a rota. Bloquear o desconhecido
        # faria o sistema deixar de descobrir fonte nova.
        serve, motivo = serve_como_fonte("https://institutoqualquer.org.br/editais")
        self.assertTrue(serve)
        self.assertIn("não catalogado", motivo)


class TesteAlcance(unittest.TestCase):
    def test_pncp_so_pelo_navegador_do_titular(self):
        url = "https://pncp.gov.br/api/consulta/v1/orgaos/1/compras/2026/1"
        self.assertFalse(pode_da_nuvem(url))
        self.assertTrue(exige_navegador(url))

    def test_portal_municipal_pode_da_nuvem(self):
        self.assertTrue(pode_da_nuvem("https://www.januaria.mg.gov.br/portal/editais/5"))

    def test_ritmo_do_pncp_esta_declarado(self):
        self.assertIn("2,5", ritmo_de("https://pncp.gov.br/api/consulta/v1/x"))


class TesteDiagnostico(unittest.TestCase):
    def test_diagnostico_traz_erro_conhecido(self):
        d = diagnostico("https://bnccompras.com/Process/ProcessView?param1=x")
        self.assertIn("403", d["erro_conhecido"])
        self.assertFalse(d["serve_como_fonte"])

    def test_diario_agregado_marcado_como_precisando_recorte(self):
        d = diagnostico("https://data.queridodiario.ok.org.br/2307304/2023-06-15/x.pdf")
        self.assertEqual(d["rota"], "edicao_inteira_precisa_de_recorte")


if __name__ == "__main__":
    unittest.main()
