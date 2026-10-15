"""15/10/2026 (titular): releitura padrão em todos os motores — a mesma oportunidade relida não é nova."""
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from src import vistos as V


class Releitura(unittest.TestCase):
    def setUp(self):
        self.p = mock.patch.object(V, "ARQ", Path(tempfile.mkdtemp()) / "v.json"); self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_mesma_compra_por_enderecos_diferentes(self):
        a = V.chave({"url": "https://pncp.gov.br/app/editais/18557561000151/2026/136"})
        b = V.chave({"url": "https://pncp.gov.br/pncp-api/v1/orgaos/18557561000151/compras/2026/136/arquivos/1"})
        self.assertEqual(a, b)
        self.assertEqual(V.chave({"url": "https://WWW.x.gov.br/edital/?utm_source=a#t"}), V.chave({"url": "https://x.gov.br/edital"}))

    def test_novas_e_relidas(self):
        lote = [{"url": "https://pncp.gov.br/app/editais/11111111000111/2026/1"}, {"url": "https://x.gov.br/a"},
                {"url": "https://x.gov.br/a"}]                                          # repetida na mesma leitura
        r1 = V.registrar("pncp-api", lote, date(2026, 10, 14))
        r2 = V.registrar("pncp-api", lote + [{"url": "https://x.gov.br/b"}], date(2026, 10, 15))
        self.assertEqual((r1["novas"], r1["relidas"]), (2, 0))
        self.assertEqual((r2["novas"], r2["relidas"]), (1, 2))
        self.assertEqual(V.distintas("pncp-api"), 3)
        self.assertEqual(V.distintas("outro-motor"), 0)                               # cada motor com o seu registro

    def test_corrigir_totais_uma_vez(self):
        V.registrar("m1", [{"url": "https://x.gov.br/a"}, {"url": "https://x.gov.br/b"}], date(2026, 10, 15))
        sens = {"m1": {"achados_total": 50}}
        V.corrigir_totais(sens)
        self.assertEqual((sens["m1"]["achados_total"], sens["m1"]["relidas_total"]), (2, 48))
        V.corrigir_totais(sens)
        self.assertEqual(sens["m1"]["relidas_total"], 48)


class PortaoPncp15_10b(unittest.TestCase):
    def test_ilpi_goias_e_capitais(self):
        from src import pncp_osc as P
        h = date(2026, 10, 15)
        base = {"titulo": "Credenciamento de ILPI para acolhimento de idosos", "objeto": "credenciamento de entidades filantrópicas para acolhimento",
                "modalidade": "Credenciamento", "encerramento": "2026-11-30", "esfera": "M"}
        self.assertEqual(P.classificar_item({**base, "orgao": "MUNICIPIO DE ANAPOLIS", "uf": "GO"}, h, P.TODAS_UFS)["veredito"], "OPORTUNIDADE")
        self.assertEqual(P.classificar_item({**base, "orgao": "MUNICIPIO DE CURITIBA", "uf": "PR", "municipio": "Curitiba"}, h, P.TODAS_UFS)["veredito"], "OPORTUNIDADE")
        self.assertEqual(P.classificar_item({**base, "orgao": "MUNICIPIO DE NOVA SANTA RITA", "uf": "RS"}, h, P.TODAS_UFS)["veredito"], "RUIDO")

    def test_portao_nos_registros_antigos(self):
        from src import pncp_osc as P
        self.assertIn("fora de Goiás", P.veredito_por_titulo("MUNICIPIO DE ANCHIETA — VISA CONTRATAÇÃO DE VAGAS EM ILPI", uf="ES"))
        self.assertIn("agricultura familiar", P.veredito_por_titulo("MUNICIPIO DE CURITIBA — Credenciamento de agricultores familiares"))
        self.assertIn("pessoas físicas", P.veredito_por_titulo("UNIVERSIDADE FEDERAL — seleção de ensaios fotográficos inéditos"))
        self.assertIsNone(P.veredito_por_titulo("TRIBUNAL SUPERIOR DO TRABALHO — Seleção de associações e cooperativas de catadores"))
