"""Selo ouro/prata/bronze do LIVRO pelo histórico de 3 anos (titular, 03/10/2026)."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from src import selo_livros as S

H = date(2026, 10, 3)


class TesteSeloLivros(unittest.TestCase):
    def test_ouro_com_dois_anos_e_prova(self):
        x = {"geo": "GO", "historico": [
            {"publicado_em": "2025-04-10", "fim": "2025-05-10", "pagina_oficial": "https://www.itaberai.go.gov.br/edital-cmdca-2025"},
            {"publicado_em": "2026-04-12", "fim": "2026-05-12", "pagina_oficial": "https://www.itaberai.go.gov.br/edital-cmdca-2026"}]}
        s = S.avaliar(x, H)
        self.assertEqual((s["selo"], s["bloco"], s["anos_com_edicao"]), ("ouro", "GO", [2025, 2026]))
        self.assertEqual(s["preditivo"]["mes_tipico"], 4)
        self.assertEqual(s["preditivo"]["proxima_janela"], "2027-04")

    def test_prata_sem_pagina_oficial(self):
        x = {"geo": "BR", "historico": [
            {"publicado_em": "2024-09-01", "pagina_oficial": "https://capitaai.com.br/captacao/x"},
            {"publicado_em": "2026-09-01", "pagina_oficial": "https://capitaai.com.br/captacao/y"}]}
        self.assertEqual(S.avaliar(x, H)["selo"], "prata")

    def test_bronze_so_edicao_atual_e_vigencia_longa_nao_conta(self):
        x = {"geo": "SP", "historico": [{"publicado_em": "2026-09-20", "fim": "2031-07-22", "ano": "2031", "pagina_oficial": "https://pncp.gov.br/app/editais/1/2026/2"}]}
        s = S.avaliar(x, H)
        self.assertEqual((s["selo"], s["bloco"]), ("bronze", "UF"))
        self.assertIsNone(s["edicoes"][0]["encerramento"])
        self.assertFalse(s["teve_edital_3_anos"])

    def test_internacional_e_mesma_edicao_conta_uma_vez(self):
        x = {"internacional": True, "historico": [{"publicado_em": "2025-03-01", "pagina_oficial": "https://a.org/e"},
                                                 {"publicado_em": "2025-03-15", "pagina_oficial": "https://b.org/e"}]}
        s = S.avaliar(x, H)
        self.assertEqual((s["bloco"], s["edicoes_3_anos"]), ("INT", 1))

    def test_coleta_entra_no_historico_com_prova(self):
        livros = [{"id": "op-1", "programa": "Edital X", "historico": []}]
        with tempfile.TemporaryDirectory() as t:
            ent = Path(t); (ent / "go_2026-10-04.json").write_text(json.dumps({"op-1": {"edicoes": [
                {"ano": "2024", "abertura": "2024-05-02", "encerramento": "2024-06-01", "pagina_oficial": "https://goias.gov.br/x"},
                {"ano": "2023", "abertura": "2023-05-02"}]}}), encoding="utf-8")
            with mock.patch.object(S, "ENTRADA", ent):
                self.assertEqual(S.incorporar(livros), 1)
                S.incorporar(livros)                               # idempotente: o histórico não cresce
                self.assertEqual(len(livros[0]["historico"]), 1)
        self.assertEqual(livros[0]["historico"][0]["ano"], "2024")


if __name__ == "__main__":
    unittest.main()
