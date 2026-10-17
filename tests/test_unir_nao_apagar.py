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


class UnirComTiposDiferentes(unittest.TestCase):
    def test_edicoes_numerico_nao_quebra(self):
        """17/10: 'edicoes' é um NÚMERO em muitos livros — a união quebrava a leitura dos motores e a montagem do fluxo
        (TypeError: 'int' object is not iterable) e a Bússola ficava com o número velho."""
        fica = {"id": "a", "edicoes": 3, "coleta": {"x": 1}}
        sai = {"id": "b", "edicoes": 2, "coleta": "texto", "historico": [{"id": "e1"}]}
        B.juntar_em(fica, sai)
        self.assertEqual(fica["edicoes"], 3); self.assertEqual(fica["coleta"], {"x": 1})
        self.assertEqual(fica["historico"], [{"id": "e1"}])


class ContratoDaBussola(unittest.TestCase):
    def test_bussola_mostra_os_livros_do_catalogo(self):
        """17/10 (titular): a Bússola mostra os livros do sistema — o número publicado é o do catálogo gravado."""
        import json
        from pathlib import Path
        R = Path(__file__).resolve().parents[1]
        cat = len(json.loads((R / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"])
        flx = json.loads((R / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        self.assertEqual(flx["opressores"]["catalogo"], cat)
        self.assertEqual(flx["etapas"]["opressores_total"], cat)
