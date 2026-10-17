"""Unir, nunca apagar (titular, 17/10/2026): duplicata de livro é UNIDA ao que fica, com registro em 'juntados'."""
import unittest

from src import banco_livros as B
from src import trava_livros as T


class Unir(unittest.TestCase):
    def test_conteudo_do_que_sai_vai_para_o_que_fica(self):
        fica = {"id": "a", "programa": "PNAB", "historico": [{"id": "e1"}], "coleta": {"x": 1}}
        sai = {"id": "b", "programa": "PNAB", "historico": [{"id": "e1"}, {"id": "e2"}], "coleta": {"y": 2},
               "pagina": "https://goias.gov.br/pnab"}
        B.juntar_em(fica, sai)
        self.assertEqual([h["id"] for h in fica["historico"]], ["e1", "e2"])
        self.assertEqual(fica["coleta"], {"x": 1, "y": 2})
        self.assertEqual(fica["pagina"], "https://goias.gov.br/pnab", "campo que só o que sai tinha passa para o que fica")
        self.assertEqual(fica["juntados"][0]["id"], "b")

    def test_a_trava_reconhece_a_uniao(self):
        fica = {"id": "a", "programa": "PNAB"}
        B.juntar_em(fica, {"id": "b", "programa": "PNAB"})
        self.assertIn("b", T._juntados([fica]), "com o registro, a trava arquiva em vez de devolver ao catálogo")
