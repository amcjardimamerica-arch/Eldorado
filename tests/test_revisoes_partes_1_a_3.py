"""10/10/2026 (implantação das Partes 1, 2 e 3): um mecanismo só para a revisão humana — vereditos no saneamento,
certidões num arquivo próprio que o Cartório incorpora, oportunidades novas (derivadas) no fluxo; e o gabarito da
Parte 3 como regressão: nenhuma regra automática atinge um útil."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))


class TesteGabaritoP3(unittest.TestCase):
    def test_nenhum_util_da_parte_3_atingido(self):
        from src import saneamento_motores as S
        S.limpar_cache()
        g = json.loads((ROOT / "tests/fixtures/gabarito_abertas_p3_br_privadas_2026_10_10.json").read_text(encoding="utf-8"))["registros"]
        uteis = [r for r in g if r["veredito"] in ("ouro", "prata", "bronze", "pendente", "nao_disponivel")]
        atingidos = [(r["id"], S.nao_oportunidade(r)) for r in uteis if S.nao_oportunidade(r)]
        self.assertEqual(atingidos, [], "regra M3 atingiu útil da Parte 3")
        self.assertGreaterEqual(sum(1 for r in g if r["veredito"] == "ruido" and S.nao_oportunidade(r)), 70)

    def test_pagina_catalogo_nao_e_oportunidade(self):
        from src import saneamento_motores as S
        S.limpar_cache()
        self.assertTrue(S.nao_oportunidade({"url": "https://capitaai.com.br/editais-abertos/", "titulo": "Editais abertos"}))
        self.assertTrue(S.nao_oportunidade({"url": "https://blog.org/tag/editais", "titulo": "23 editais abertos para ONGs"}))


class TesteImportador(unittest.TestCase):
    def test_pagina_exigida_so_de_pdf(self):
        import importar_revisao_abertas as I
        base = {"valor": "x", "trecho": "y"}
        self.assertTrue(I._item_ok({**base, "documento": "https://orgao.org.br/edital", "pagina": None}), "HTML não tem página")
        self.assertFalse(I._item_ok({**base, "documento": "https://orgao.org.br/edital.pdf", "pagina": None}), "PDF exige página")
        self.assertTrue(I._item_ok({**base, "documento": "https://orgao.org.br/edital.pdf", "pagina": 3}))
        self.assertTrue(I.CERTIDOES.name == "certidoes_manuais.json", "certidões da revisão em arquivo próprio")

    def test_le_formato_da_parte_2_e_derivadas_da_parte_3(self):
        import importar_revisao_abertas as I
        with tempfile.TemporaryDirectory() as t:
            T = Path(t)
            (T / "resultado_ABERTAS_P2-X.json").write_text(json.dumps({"resultado": {"a1": {"veredito": "ruido"}}}))
            (T / "resultado_ABERTAS_P3-X.json").write_text(json.dumps({"der-1": {"veredito": "ouro", "novo": True, "derivada_de": "b2"}}))
            regs = I.ler_lotes(T)
            self.assertEqual(set(regs), {"a1", "der-1"})


class TesteCartorioEFluxo(unittest.TestCase):
    def test_cartorio_incorpora_e_fluxo_recebe(self):
        c = (ROOT / "src/cartorio.py").read_text(encoding="utf-8")
        self.assertIn('PASTA / "certidoes_manuais.json"', c); self.assertIn('"revisao_humana": True', c)
        f = (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8")
        self.assertIn("biblioteca_alexandria/livros/_acervo/editais/derivadas_revisao.json", f)
        d = json.loads((ROOT / "biblioteca_alexandria/livros/_acervo/editais/derivadas_revisao.json").read_text(encoding="utf-8"))["derivadas"]
        self.assertGreaterEqual(len(d), 25)
        v = json.loads((ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json").read_text(encoding="utf-8"))["vereditos"]
        # as três partes presentes; revisões posteriores (ex.: verificação pelo Chrome de 11/10) acrescentam origens
        self.assertLessEqual({"P1-GO-2026-10-10", "P2-BR-PUBLICAS-2026-10-10", "P3-BR-PRIVADAS-2026-10-10"}, {x["origem"] for x in v.values()})


if __name__ == "__main__":
    unittest.main()
