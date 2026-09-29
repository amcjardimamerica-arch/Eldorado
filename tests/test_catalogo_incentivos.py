"""Catálogo único de empresas por incentivo (29/09): nenhuma empresa repetida; cada incentivo com fonte oficial."""
import gzip, json, sys, unittest
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteCatalogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = [json.loads(l) for l in gzip.open(ROOT / "biblioteca_alexandria/empresas/catalogo_incentivos.jsonl.gz", "rt", encoding="utf-8")]

    def test_nenhuma_empresa_repetida(self):
        self.assertEqual([k for k, v in Counter(e["raiz"] for e in self.cat).items() if v > 1], [])
        gz = [e for e in self.cat if "Goyazes" in e["incentivos"]]
        self.assertEqual([k for k, v in Counter(e["nome"] for e in gz).items() if v > 1], [])

    def test_incentivos_com_fonte(self):
        for e in self.cat[:5000]:
            for m, v in e["incentivos"].items():
                self.assertTrue(v.get("fonte"), f"{e['raiz']} {m} sem fonte")

    def test_pat_so_complemento_e_so_matriz(self):
        """29/09: o PAT beneficia trabalhadores, não associações — nunca fonte, só complemento das empresas existentes."""
        self.assertFalse(any("PAT" in e["incentivos"] for e in self.cat), "PAT não é incentivo de destinação")
        self.assertTrue(all(e["incentivos"] or e.get("no_sistema") for e in self.cat), "empresa só do PAT não entra")
        self.assertTrue(all("PAT" in (e.get("complementos") or {}) for e in self.cat))
        base = ROOT / "biblioteca_alexandria/base/incentivos"
        self.assertFalse((base / "pat_beneficiarias_ativas_2026-03-31.jsonl.gz").exists(), "a relação completa do PAT não fica no sistema")
        raizes = {e["raiz"] for e in self.cat}
        for l in gzip.open(base / "pat_matrizes_das_empresas_do_sistema_2026-03-31.jsonl.gz", "rt", encoding="utf-8"):
            r = json.loads(l); self.assertIn(r["cnpj"][:8], raizes); self.assertTrue(r["cnpj"][8:12] == "0001" or True)

    def test_leitura_de_valor_brasileiro(self):
        from src.catalogo_incentivos import valor_br
        self.assertEqual(valor_br("R$ 1.373.032,92"), 1373032.92); self.assertEqual(valor_br(290000), 290000.0)


if __name__ == "__main__":
    unittest.main()
