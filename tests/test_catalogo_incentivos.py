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
        self.assertTrue(all(e["incentivos"]["PAT"].get("nota") for e in self.cat[:2000] if "PAT" in e["incentivos"]))

    def test_leitura_de_valor_brasileiro(self):
        from src.catalogo_incentivos import valor_br
        self.assertEqual(valor_br("R$ 1.373.032,92"), 1373032.92); self.assertEqual(valor_br(290000), 290000.0)


if __name__ == "__main__":
    unittest.main()
