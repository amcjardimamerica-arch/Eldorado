"""Motores opressores como LIVROS (29/09): classificação, nome "GO - Cultura", curadoria sem mistura, filtros e dossiê."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteLivros(unittest.TestCase):
    def test_classificacao_e_nome(self):
        from src.livros_opressores import classificar
        x = classificar({"programa": "Programa Goyazes - projetos até R$ 20 mil", "uf": "GO"})
        self.assertTrue(x["rotulo"].startswith("GO - Cultura · Incentivo fiscal"))
        self.assertTrue(x["nome_classificado"].startswith("Programa Goyazes") and x["nome_classificado"].endswith("— Goiás"))   # 01/10: nome da oportunidade — Estado / Cidade
        y = classificar({"programa": "Fundo Municipal do Idoso de Goiânia", "uf": "GO", "familia": "Fundos da Infância e do Idoso"})
        self.assertEqual(y["objeto_area"], "Pessoa idosa")
        z = classificar({"programa": "Ford Foundation", "esfera": "Internacional"})
        self.assertTrue(z["rotulo"].startswith("INT - ")); self.assertTrue(z["nome_classificado"].endswith("— Internacional"))

    def test_nenhum_livro_mistura_estados(self):
        C = json.loads((ROOT / "biblioteca_alexandria/fontes/motores.json").read_text(encoding="utf-8"))["motores"]
        mix = [x["id"] for x in C if len({h.get("uf") for h in (x.get("historico") or []) if h.get("uf")}) > 1]
        self.assertEqual(mix, [])
        self.assertTrue(all(x.get("nome_classificado") for x in C))

    def test_painel_filtros_livro_e_dossie(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for id_ in ("mo-tipo", "mo-periodo", "mo-publico"):
            self.assertIn(f'id="{id_}"', h)
        self.assertIn("Livro da oportunidade", h); self.assertIn("${dossHtml}", h)


if __name__ == "__main__":
    unittest.main()
