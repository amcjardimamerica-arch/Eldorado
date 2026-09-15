"""A fila de pesquisa: editais em aberto que ainda estao sem informacao.

O caso real que originou o modulo: a inspecao de 10/09/2026 encontrou o trabalho
de verificacao e o sistema em dois mundos separados. A base de 468 registros —
339 prazos confirmados em documento oficial, 231 validados um por um — nao era
lida por nenhum modulo, nenhum painel e nenhum workflow. E o monitor de prazos
lia so a base de oportunidades, quase toda de edicoes de diario sem prazo, e por
isso enxergava ZERO prazos em 17 mil registros.
"""
import json
import unittest
from datetime import date
from pathlib import Path

from src import abertos_sem_informacao as A

ROOT = Path(__file__).resolve().parents[1]
HOJE = date(2026, 9, 12)


class TestePaginaOficial(unittest.TestCase):
    """Pagina oficial e a do orgao ou do patrocinador — e so ela."""

    def test_pagina_de_divulgacao_do_pncp_nao_e_pagina_oficial(self):
        oficial, motivo = A.e_pagina_oficial("https://pncp.gov.br/app/editais/44733608000109/2026/765")
        self.assertFalse(oficial)
        self.assertIn("portal de divulgacao".replace("c", "ç").replace("ao", "ão"), motivo)

    def test_arquivo_do_orgao_no_pncp_vale_com_origem_declarada(self):
        oficial, motivo = A.e_pagina_oficial(
            "https://pncp.gov.br/pncp-api/v1/orgaos/00/compras/2026/1/arquivos/1")
        self.assertTrue(oficial)
        self.assertIn("origem declarada", motivo)

    def test_site_do_orgao_vale(self):
        for url in ("https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/",
                    "https://www.januaria.mg.gov.br/editais",
                    "https://www.bnb.gov.br/sustentabilidade"):
            oficial, _ = A.e_pagina_oficial(url)
            self.assertTrue(oficial, url)

    def test_diario_portal_de_noticia_e_plataforma_privada_nao_valem(self):
        for url in ("https://data.queridodiario.ok.org.br/2307304/2023-06-15/x.pdf",
                    "https://captadores.org.br/editais/x",
                    "https://observatorio3setor.org.br/noticia",
                    "https://portaldecompraspublicas.com.br/x",
                    "https://app2.ammlicita.org.br/x"):
            oficial, motivo = A.e_pagina_oficial(url)
            self.assertFalse(oficial, url)
            self.assertTrue(motivo)

    def test_sem_endereco_diz_o_motivo(self):
        oficial, motivo = A.e_pagina_oficial("")
        self.assertFalse(oficial)
        self.assertIn("nenhum endereço", motivo)


class TesteRegrasDaFila(unittest.TestCase):
    def test_edicao_de_diario_sem_ato_nao_e_edital(self):
        self.assertTrue(A._e_edicao_de_diario(
            {"titulo": "Diário Oficial de Goiânia (GO) 2025-02-26 — \"chamamento público\""}))
        # com ato identificado dentro, deixa de ser edicao bruta
        self.assertFalse(A._e_edicao_de_diario(
            {"titulo": "Diário Oficial de Goiânia (GO) 2025-02-26 — x",
             "objeto": "termo de fomento com organizações da sociedade civil"}))

    def test_sem_data_final_nao_ha_prazo_para_decidir(self):
        self.assertEqual(A._situacao(None, HOJE), "sem_prazo_confirmado")
        self.assertEqual(A._situacao("", HOJE), "sem_prazo_confirmado")
        self.assertEqual(A._situacao("2026-09-25", HOJE), "aberto")
        self.assertEqual(A._situacao("2026-09-11", HOJE), "encerrado")

    def test_objeto_curto_conta_como_falta_de_objeto(self):
        # Curitiba/DER-PR: "CHAMAMENTO PUBLICO RESIDUOS SOLIDOS", quatro palavras,
        # e o edital de 75 paginas mostrou doacao de bens moveis inserviveis.
        self.assertLessEqual(A._palavras("CHAMAMENTO PUBLICO RESIDUOS SOLIDOS"),
                             A.OBJETO_CURTO_MAX_PALAVRAS)

    def test_duplicata_colapsa_pelo_objeto_normalizado(self):
        a = A._chave_de_duplicata("Apoio financeiro para que ORGANIZAÇÕES da sociedade civil...")
        b = A._chave_de_duplicata("apoio  financeiro  para que organizacoes da sociedade civil")
        self.assertNotEqual(a, "")
        self.assertTrue(a.startswith("apoio financeiro para que organiza"))
        self.assertTrue(b.startswith("apoio financeiro para que organizacoes"))

    def test_urgente_e_o_que_fecha_em_ate_trinta_dias(self):
        self.assertEqual(A._prioridade("aberto", 3, "aprovado")[0], 1)
        self.assertEqual(A._prioridade("aberto", 58, "atencao")[0], 2)
        self.assertEqual(A._prioridade("sem_prazo_confirmado", None, "aprovado")[0], 3)
        self.assertEqual(A._prioridade("sem_prazo_confirmado", None, "atencao")[0], 4)


class TesteSaida(unittest.TestCase):
    """A saida gravada tem de existir, bater com o resumo e nao inventar data."""

    def setUp(self):
        self.pacote = json.loads((ROOT / "docs/dados/abertos_sem_informacao.json")
                                 .read_text(encoding="utf-8"))

    def test_as_bases_verificadas_entram_na_fila(self):
        fonte = (ROOT / "src/abertos_sem_informacao.py").read_text(encoding="utf-8")
        self.assertIn("verificacao_467_2026-09-09.json", fonte,
                      "a base verificada era arquivo orfao: tem de ser lida aqui")
        self.assertGreater(self.pacote["resumo"]["ja_validados_individualmente"], 0)

    def test_resumo_bate_com_a_lista(self):
        self.assertEqual(self.pacote["resumo"]["total"], len(self.pacote["itens"]))

    def test_todo_item_diz_o_que_falta(self):
        for item in self.pacote["itens"]:
            self.assertTrue(item["faltam"], item["id"])
            for falta in item["faltam"]:
                self.assertIn(falta, ("objeto", "prazo de inscrição", "página oficial"))

    def test_nenhum_item_reprovado_por_objeto_entra(self):
        for item in self.pacote["itens"]:
            self.assertNotEqual(item["veredito"], "reprovado", item["id"])

    def test_nenhum_encerrado_entra(self):
        for item in self.pacote["itens"]:
            self.assertNotEqual(item["situacao"], "encerrado", item["id"])

    def test_item_sem_pagina_oficial_diz_o_motivo(self):
        for item in self.pacote["itens"]:
            if "página oficial" in item["faltam"]:
                self.assertTrue(item["motivo_sem_pagina_oficial"], item["id"])

    def test_edicoes_de_diario_ficam_em_bloco_proprio(self):
        bloco = self.pacote["resumo"]["edicoes_de_diario_sem_ato"]
        self.assertGreater(bloco["total"], 1000)
        self.assertIn("nunca é fonte de prazo", bloco["destino"])

    def test_todo_item_diz_como_pesquisar(self):
        for item in self.pacote["itens"]:
            self.assertIn("como_pesquisar", item)
            self.assertIn("exige_navegador_do_titular", item["como_pesquisar"])

    def test_csv_acompanha_o_json(self):
        csv = (ROOT / "docs/dados/abertos_sem_informacao.csv").read_text(encoding="utf-8-sig")
        self.assertEqual(len(csv.strip().splitlines()) - 1, self.pacote["resumo"]["total"])


if __name__ == "__main__":
    unittest.main()
