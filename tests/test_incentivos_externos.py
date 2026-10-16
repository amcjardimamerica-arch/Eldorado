"""11/10/2026 (titular): empresas de incentivo da busca do Chrome no catálogo único (uma empresa por raiz de CNPJ)."""
import gzip, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteCatalogo(unittest.TestCase):
    def test_esporte_e_goyazes_no_catalogo(self):
        r = json.loads((ROOT / "biblioteca_alexandria/livros/especiais/empresas/catalogo_incentivos_resumo.json").read_text(encoding="utf-8"))
        self.assertGreater(r["por_incentivo"]["Esporte"], 9000); self.assertGreaterEqual(r["por_incentivo"]["Goyazes"], 100)
        self.assertGreater(r["por_incentivo"]["PRONON"], 1500); self.assertGreater(r["por_incentivo"]["PRONAS"], 700)   # 11/10: Transferegov
        raizes, cpf = set(), 0
        with gzip.open(ROOT / "biblioteca_alexandria/livros/especiais/empresas/catalogo_incentivos.jsonl.gz", "rt", encoding="utf-8") as fh:
            for l in fh:
                e = json.loads(l)
                self.assertNotIn(e["raiz"], raizes, "uma empresa por raiz"); raizes.add(e["raiz"])
                if e.get("cnpj") and len(str(e["cnpj"])) == 11:
                    cpf += 1
        self.assertEqual(cpf, 0, "pessoa física não entra")

    def test_gerador_le_as_bases_externas(self):
        s = (ROOT / "src/catalogo_incentivos.py").read_text(encoding="utf-8")
        self.assertIn('(BASE / "externos").glob("incentivos_*.jsonl.gz")', s)
        self.assertIn("ano já vindo da planilha da Secult: não duplica", s)
        d = json.loads((ROOT / "dados/editais/derivadas_revisao.json").read_text(encoding="utf-8"))["derivadas"]
        self.assertEqual(sum(1 for x in d.values() if x.get("origem") == "CHROME-INCENTIVOS-2026-10-11"), 3)


if __name__ == "__main__":
    unittest.main()
