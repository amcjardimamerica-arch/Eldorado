"""Teste do motor 07 (TJ-GO) em 03/10/2026: prazo do edital de Itaberaí (2020), data sem ano e cobertura no maestro."""
import unittest
from datetime import date

from src import judiciario_go as J
from src import maestro


class TesteMotor07(unittest.TestCase):
    def test_periodo_com_ano_manda(self):
        self.assertEqual(J.prazo("protocolar o pedido no período de 20/07 a 18/08/2020.", "2026-09-11")[0], "2020-08-18")

    def test_data_sem_ano_nao_vai_para_o_ano_seguinte(self):
        self.assertIsNone(J.prazo("Edital seleciona projetos de Itaberaí (GO). Inscrições de 20/07 a 18/08.", "2026-09-11")[0])

    def test_prazo_normal_continua(self):
        self.assertEqual(J.prazo("Comarca de Goiânia: inscrições até 30/10/2026", "2026-10-02")[0], "2026-10-30")

    def test_edital_de_2020_nao_e_oportunidade(self):
        a = J.classificar_item({"titulo": "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária",
                                "texto": "As instituições deverão protocolar o pedido de destinação no período de 20/07 a 18/08/2020.",
                                "data_publicacao": "2026-09-11", "fonte": "C", "url": "https://www.cnj.jus.br/x"}, date(2026, 10, 3))
        self.assertNotEqual(a.get("veredito"), "OPORTUNIDADE")

    def test_editais_de_magistratura_sao_ruido(self):
        for t in ("TJGO publica edital para preenchimento de vaga de juiz-membro substituto no TRE-GO",
                  "Divulgado edital de remoção para vaga na 7ª Câmara Cível do TJGO"):
            a = J.classificar_item({"titulo": t, "texto": t, "data_publicacao": "2026-10-02", "fonte": "A", "url": "https://www.tjgo.jus.br/x"}, date(2026, 10, 3))
            self.assertEqual(a.get("veredito"), "RUIDO")

    def test_maestro_fonte_local_pulada_nao_e_completa(self):
        diag = {"fontes": {"A": {"pulado": "na nuvem o TJGO recusa IP estrangeiro: lidos no computador do titular"}}}
        self.assertEqual(maestro.cobertura("judiciario-tjgo", {"cor": "azul", "falhas": 0}, {}, diag), "pendente_local")


if __name__ == "__main__":
    unittest.main()
