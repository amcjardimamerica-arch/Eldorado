"""Teste do motor 09 (MPT-GO) em 03/10/2026: PDF do edital, exigência de cadastro e tabela em toda passagem."""
import json
import unittest
from datetime import date

from src import ministerios_publicos as M
from src.nucleo import ROOT

TEXTO_9220 = ("EDITAL PARA INDICAÇÃO DE DESTINAÇÃO DE RECURSOS OU BENS PA-INTER 000037.2019.18.003/6 ... torna público o presente Edital "
              "facultando a terceiros juridicamente interessados, pelo prazo de 5 (cinco) dias , a indicação de destinatários(as) de bens ou "
              "valores decorrentes no importe correspondente a até R$ 94.428,74 (noventa e quatro mil). Quem pode indicar . Poderão indicar "
              "destinações qualquer pessoa jurídica de direito privado, órgãos públicos ... Como indicar . A indicação deverá ocorrer nos autos "
              "do Procedimento Administrativo (PA-INTER) 000037.2019.18.003/6.")


class TesteMotor09(unittest.TestCase):
    def test_pdf_do_9220_nao_exige_cadastro_e_traz_valor(self):
        x = M.extrair_pdf_mpt(TEXTO_9220)
        self.assertEqual((x["valor"], x["prazo_dias"], x["exige_cadastro"]), ("R$ 94.428,74", 5, False))

    def test_sem_pdf_nao_presume_cadastro(self):
        it = {"tipo": "edital_mpt", "titulo": "Edital 009220.2026 — PTM Anápolis", "data_publicacao": "2026-10-01", "orgao": "MPT-GO"}
        r = M.classificar(it, date(2026, 10, 3), M._cfg())
        self.assertEqual(r["classificacao"], "OPORTUNIDADE")
        self.assertIsNone(r["exige_cadastro"])
        self.assertIn("conferir no PDF", r["motivo"])

    def test_com_pdf_sem_exigencia(self):
        it = {"tipo": "edital_mpt", "titulo": "Edital 009220.2026", "data_publicacao": "2026-10-01", "orgao": "MPT-GO", "exige_cadastro": False}
        self.assertIn("não exige cadastro", M.classificar(it, date(2026, 10, 3), M._cfg())["motivo"])

    def test_resposta_que_nao_e_pdf(self):
        self.assertEqual(M._texto_pdf(b"<html>sessao expirada</html>"), "")
        self.assertIn(M._PDF_ERRO["motivo"], ("resposta_nao_e_pdf", "sem_leitor_pdf"))

    def test_tabela_lida_em_toda_passagem(self):
        cfg = json.loads((ROOT / "config/ministerios_publicos.json").read_text(encoding="utf-8"))
        f = {"id": "f02", "modo": "tabela_mpt"}
        self.assertTrue(M._devido(f, {"ultima_por_fonte": {"f02": "2026-10-03"}}, cfg, date(2026, 10, 3)))


if __name__ == "__main__":
    unittest.main()
