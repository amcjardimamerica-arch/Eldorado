import json
import unittest

from src import dispensas_itens, livros_opressores, pareceres_livros


class TestPareceresLivros(unittest.TestCase):
    def test_livro_preserva_pareceres_e_iniciativa(self):
        x = {"id": "op-teste", "programa": "Edital PNAB Ciclo 2", "orgao": "Prefeitura", "uf": "GO", "historico": [],
             "livro": {"pareceres": [{"data": "2026-10-02", "oportunidade": "a"}], "iniciativa": {"valor": "poder_publico"},
                       "historico_3_anos": {"situacao": "recorrente"}}}
        livros_opressores.classificar(x)
        self.assertEqual(x["livro"]["pareceres"][0]["oportunidade"], "a")
        self.assertEqual(x["livro"]["iniciativa"]["valor"], "poder_publico")
        self.assertEqual(x["livro"]["historico_3_anos"]["situacao"], "recorrente")

    def test_regime_credenciamento(self):
        r, _ = dispensas_itens.regime_por_texto("Credenciamento de artistas locais")
        self.assertEqual(r, "credenciamento")
        a = dispensas_itens.analisar("credenciamento")
        self.assertIn("Prazo de inscrição", a["provaveis"])

    def test_pareceres_tem_iniciativa_valida(self):
        P = pareceres_livros.carregar()
        for p in P.values():
            self.assertIn((p.get("iniciativa") or {}).get("valor"), pareceres_livros.INICIATIVAS)
            self.assertEqual(len(p.get("doze_itens") or {}), 12)


if __name__ == "__main__":
    unittest.main()
