"""16/10/2026 (titular): o índice encontra o livro da nova edição pelo programa, órgão, local, modalidade, tipo e área."""
import unittest

from src.indice_livros import Indice, entrada

LIVROS = [{"id": "lv-premio", "programa": "Prêmio Goiás de Cultura Popular 2025", "orgao": "Secretaria de Estado da Cultura de Goiás",
           "uf": "GO", "esfera": "Estado", "tipo_objeto": "Prêmio", "objeto_area": "Cultura", "pagina": "https://goias.gov.br/cultura/premio"},
          {"id": "lv-saude", "programa": "Secretaria de Estado da Saúde — Edital de chamamento", "orgao": "Secretaria de Estado da Saúde", "uf": "GO"},
          {"id": "lv-fia", "programa": "FIA Anápolis — Fundo da Infância e Adolescência", "orgao": "Prefeitura de Anápolis", "uf": "GO",
           "municipio": "Anápolis"}]


class Indice16_10(unittest.TestCase):
    def setUp(self):
        self.I = Indice([entrada(lv) for lv in LIVROS])

    def test_nova_edicao_cai_no_livro_do_programa(self):
        lid, s, mot = self.I.encontrar({"titulo": "Prêmio Goiás de Cultura Popular 2026 — inscrições abertas",
                                        "orgao": "Secretaria de Estado da Cultura de Goiás", "uf": "GO", "url": "https://goias.gov.br/cultura/premio-2026"})
        self.assertEqual(lid, "lv-premio")

    def test_orgao_diferente_nao_liga(self):
        self.assertIsNone(self.I.encontrar({"titulo": "Ministério da Saúde — Edital de chamamento nº 6/2026", "orgao": "Ministério da Saúde"})[0])

    def test_conflito_de_local_impede(self):
        self.assertIsNone(self.I.encontrar({"titulo": "FIA — Fundo da Infância e Adolescência", "orgao": "Prefeitura de Anápolis",
                                            "uf": "GO", "municipio": "Goiânia"})[0])
