"""04/10/2026: o executor documental extrai os 12 pontos com valor, trecho literal, documento e página — só o que o texto diz."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.executor_skills import extrair_pontos

PAG1 = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 07/2026 — Secretaria Municipal de Cultura de Goiânia. 1. DO OBJETO: seleção de projetos "
        "culturais de organizações da sociedade civil para o Natal no Parque. As inscrições estarão abertas de 01/10/2026 a 30/10/2026. "
        "O valor total é de R$ 150.000,00 (cento e cinquenta mil reais). Poderão participar organizações da sociedade civil com sede no "
        "Município de Goiânia há pelo menos dois anos.")
PAG2 = "O resultado será publicado em 20/11/2026. Caberá recurso no prazo de 5 (cinco) dias úteis. ANEXO I - Plano de trabalho ANEXO II - Declarações"


class Teste(unittest.TestCase):
    def test_pontos_com_trecho_e_pagina(self):
        p = extrair_pontos([PAG1, PAG2], "https://www.goiania.go.gov.br/edital-07-2026.pdf")
        self.assertEqual(p["Prazo de inscrição"]["valor"], "01/10/2026 a 30/10/2026")
        self.assertTrue(p["Valor"]["valor"].startswith("R$ 150.000,00"))
        self.assertIn("Natal no Parque", p["Objeto"]["valor"])
        self.assertEqual((p["Resultado"]["valor"], p["Resultado"]["pagina"]), ("20/11/2026", 2))
        self.assertIn("5 (cinco) dias", p["Prazo de recurso"]["valor"])
        self.assertIn("Secretaria Municipal de Cultura", p["Órgão / financiador"]["valor"])
        self.assertIn("ANEXO I", p["Anexos"]["valor"])
        self.assertEqual(p["Esfera"]["valor"], "municipal")
        for v in p.values():
            self.assertTrue(v["trecho"] and v["documento"] and v["pagina"])

    def test_nao_inventa(self):
        self.assertEqual(extrair_pontos(["Notícia sem nenhum dado do edital."], "https://exemplo.org/n"), {})


if __name__ == "__main__":
    unittest.main()
