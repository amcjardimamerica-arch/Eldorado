"""Testes da regra de Goiás e do aprimoramento das fontes goianas.

Regra do titular, 08/09/2026: todo edital que se aplique a Goiás tem de estar
arquivado no acervo de Editais Históricos do Google Drive.
"""
import json
import unittest
from pathlib import Path

from src.acervo_drive import (ARMADILHA_TERMOS_GO, FONTES_GOIAS, aplica_se_a_goias,
                              arquivados, banco, conferir, pendencias)

ROOT = Path(__file__).resolve().parents[1]


class TesteRegraDeGoias(unittest.TestCase):

    def test_municipio_goiano_entra_na_regra(self):
        ok, motivo = aplica_se_a_goias({"uf": "GO", "orgao": "MUNICIPIO DE FORMOSA"})
        self.assertTrue(ok)
        self.assertIn("Goiás", motivo)

    def test_orgao_com_dominio_go_gov_br_entra_mesmo_sem_uf(self):
        """O caso real: registros do PNCP chegam com uf nula."""
        ok, _ = aplica_se_a_goias({"uf": None,
                                   "link_capturado": "https://porangatu.go.gov.br/editais"})
        self.assertTrue(ok)

    def test_tjgo_entra_pela_mencao_a_goiania(self):
        ok, _ = aplica_se_a_goias({"uf": None,
                                   "orgao": "TJGO - 1ª Vara de Execução Penal de Goiânia"})
        self.assertTrue(ok)

    def test_edital_nacional_entra_porque_admite_proponente_de_goias(self):
        ok, motivo = aplica_se_a_goias({"uf": None, "nivel": "federal",
                                        "titulo": "Prêmio nacional de cultura"})
        self.assertTrue(ok)
        self.assertIn("nacional", motivo)

    def test_edital_de_outro_estado_fica_fora(self):
        ok, _ = aplica_se_a_goias({"uf": "RS", "orgao": "MUNICIPIO DE LAGOA VERMELHA",
                                   "titulo": "Chamamento público 13/2026"})
        self.assertFalse(ok)

    def test_banco_local_espelha_o_drive_e_tem_os_editais_de_goias(self):
        b = banco()
        self.assertGreaterEqual(len(b["itens"]), 6)
        for item in b["itens"]:
            self.assertEqual(item["uf"], "GO")
            self.assertIn("edital", item)
            # nenhuma data estimada: quando falta, é null com o motivo escrito
            if item.get("fim") is None:
                self.assertTrue(item.get("prazo_nao_confirmado_porque")
                                or item.get("situacao") == "encerrado",
                                f'{item["id"]} sem prazo e sem motivo registrado')

    def test_itens_reprovados_por_objeto_nao_geram_pendencia(self):
        """Qualificação de OS e incentivo a empresas não são edital de fomento:
        não há o que arquivar, e o relatório não pode acusar pendência."""
        entrada = [
            {"id": "22ca6714", "uf": "GO",
             "titulo": "CHAMAMENTO PÚBLICO PARA QUALIFICAÇÃO DE PESSOAS JURÍDICAS DE DIREITO "
                       "PRIVADO, SEM FINS LUCRATIVOS, COMO ORGANIZAÇÃO SOCIAL DE SAÚDE"},
            {"id": "3f5feb59", "uf": "GO",
             "titulo": "SELEÇÃO PÚBLICA, MEDIANTE CHAMAMENTO PÚBLICO, DE EMPRESAS PARA "
                       "CONCESSÃO DE INCENTIVO ECONÔMICO"},
        ]
        self.assertEqual(pendencias(entrada), [])

    def test_edital_de_fomento_goiano_nao_arquivado_gera_pendencia(self):
        entrada = [{"id": "zzzzzzzz", "uf": "GO",
                    "titulo": "Edital de chamamento público para seleção de projetos culturais "
                              "de organizações da sociedade civil"}]
        pend = pendencias(entrada)
        self.assertEqual(len(pend), 1)
        self.assertEqual(pend[0]["id"], "zzzzzzzz")

    def test_editais_de_goias_ja_verificados_estao_arquivados(self):
        """Os 6 registros de Goiás que são edital de fomento têm de estar no acervo."""
        for oid in ("5456e0e0", "77be3a1f", "f55515b0", "5b991f65", "db310a0f", "ba62bfc2"):
            self.assertIn(oid, arquivados(), f"{oid} não está no acervo de Goiás")

    def test_relatorio_de_conferencia_grava_estado(self):
        rel = conferir([])
        self.assertIn("regra", rel)
        self.assertEqual(rel["arquivados"], len(banco()["itens"]))
        self.assertTrue((ROOT / "estado/acervo_goias.json").exists())


class TesteFontesDeGoias(unittest.TestCase):

    def setUp(self):
        self.fontes = json.loads(
            (ROOT / "config/fontes_captacao_260.json").read_text(encoding="utf-8"))["fontes"]

    def _estaduais_cultura(self):
        return [f for f in self.fontes
                if f.get("uf") == "GO" and f.get("area") == "cultura"
                and f.get("nivel") == "estadual"]

    def test_fontes_pnab_de_goias_apontam_para_a_pagina_dos_editais(self):
        """Antes de 08/09/2026 apontavam só para o índice da secretaria, e por isso
        os 18 editais do Ciclo 2 de 2026 não entraram na base."""
        pnab = [f for f in self._estaduais_cultura() if "pnab" in f["programa"].lower()]
        self.assertGreaterEqual(len(pnab), 16)
        for f in pnab:
            self.assertIn("https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/", f["sites"])
            self.assertIn("https://pnab.cultura.go.gov.br", f["sites"])

    def test_fonte_do_fica_aponta_para_a_plataforma_das_chamadas(self):
        fica = [f for f in self._estaduais_cultura() if "fica" in f["programa"].lower()]
        self.assertTrue(fica)
        for f in fica:
            self.assertIn("https://web.ufg.br/plateia-editais/", f["sites"])

    def test_fontes_municipais_de_goiania_nao_foram_contaminadas(self):
        """Goiânia publica no portal próprio: não pode receber URL do Estado."""
        goiania = [f for f in self.fontes
                   if f.get("uf") == "GO" and f.get("nivel") == "municipal"
                   and "goiânia" in (f.get("programa") or "").lower()]
        self.assertTrue(goiania)
        for f in goiania:
            self.assertNotIn("https://pnab.cultura.go.gov.br", f.get("sites") or [])

    def test_armadilha_dos_termos_de_fomento_esta_registrada(self):
        cfg = json.loads((ROOT / "config/fontes_captacao_260.json").read_text(encoding="utf-8"))
        urls = [a["url"] for a in cfg.get("armadilhas", [])]
        self.assertTrue(any(ARMADILHA_TERMOS_GO in u for u in urls),
                        "a página de termos já celebrados precisa ficar registrada como armadilha")

    def test_fontes_goias_do_modulo_sao_as_verificadas(self):
        self.assertIn("https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/", FONTES_GOIAS)
        self.assertIn("https://web.ufg.br/plateia-editais/", FONTES_GOIAS)


if __name__ == "__main__":
    unittest.main()
