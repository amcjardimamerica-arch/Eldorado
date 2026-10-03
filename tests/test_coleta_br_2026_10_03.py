"""Coleta dos 3 anos (livros do Brasil) — regras do selo estimado e da expansão por programa. Sem rede."""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import expandir_coleta_br as X


def ed(ano, ab, en, prova="literal", prog="P", tit="T"):
    return {"ano": ano, "abertura": ab, "encerramento": en, "pagina_oficial": "https://x.gov.br/a", "trecho": "literal da página", "prova": prova,
            "programa": prog, "titulo": tit}


class Selo(unittest.TestCase):
    def test_ouro_dois_anos_prova_literal(self):
        s, _, _ = X.selo("x", [ed("2024", "2024-03-01", "2024-04-01"), ed("2026", "2026-03-01", "2026-04-01")])
        self.assertEqual(s, "ouro")

    def test_prata_quando_so_resumo(self):
        s, m, _ = X.selo("x", [ed("2024", "2024-03-01", "2024-04-01", prova="resumo_webfetch"), ed("2026", "2026-03-01", "2026-04-01")])
        self.assertEqual(s, "prata"); self.assertIn("resumo", m)

    def test_bronze_so_2026(self):
        self.assertEqual(X.selo("x", [ed("2026", "2026-03-01", "2026-04-01")])[0], "bronze")

    def test_fora_da_janela_nao_conta(self):
        self.assertEqual(X.selo("x", [ed("2023", "2023-09-01", "2023-10-02"), ed("2026", "2026-03-01", "2026-04-01")])[0], "bronze")

    def test_programa_que_nao_e_para_osc_nao_conta(self):
        s, _, _ = X.selo("x", [ed("2025", "2025-03-01", "2025-04-01", prog="Prêmio Cooperar para Transformar"),
                              ed("2026", "2026-03-01", "2026-04-01", prog="Prêmio Cooperar para Transformar")])
        self.assertEqual(s, "bronze")

    def test_programas_diferentes_nao_somam(self):
        s, _, _ = X.selo("x", [ed("2024", "2024-03-01", "2024-04-01", prog="A"), ed("2026", "2026-03-01", "2026-04-01", prog="B")])
        self.assertEqual(s, "prata")

    def test_edicao_sem_pagina_ou_trecho_nao_vale(self):
        e = ed("2025", "2025-03-01", "2025-04-01"); e["trecho"] = None
        self.assertFalse(X.valida(e))


class Expansao(unittest.TestCase):
    def test_livro_so_recebe_edicoes_do_proprio_programa(self):
        pron = {"nome": "Pronon - assistência oncológica", "orgao": "Ministério da Saúde"}
        pronas = {"nome": "Pronas/PCD - pesquisa sobre deficiência", "orgao": "Ministério da Saúde"}
        e_on, e_as = ed("2025", "2025-10-07", "2025-11-12", prog="PRONON"), ed("2025", "2025-10-07", "2025-11-05", prog="PRONAS/PCD")
        self.assertTrue(X.casa("pronon-pronas", pron, e_on)); self.assertFalse(X.casa("pronon-pronas", pron, e_as))
        self.assertTrue(X.casa("pronon-pronas", pronas, e_as))

    def test_ancora_unica_vale_para_todos_os_livros(self):
        self.assertTrue(X.casa("lie", {"nome": "qualquer"}, ed("2025", "2025-01-01", "2025-02-01")))


if __name__ == "__main__":
    unittest.main()
