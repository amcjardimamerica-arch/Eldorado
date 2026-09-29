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

    def test_pat_incentivo_indicio_so_de_empresa_existente(self):
        """29/09: PAT é incentivo fiscal da empresa (indício), só matriz; nunca inclui empresa nem é fonte para associação."""
        self.assertTrue(all(("Rouanet" in e["incentivos"] or "Goyazes" in e["incentivos"] or e.get("no_sistema")) for e in self.cat),
                        "empresa que só está no PAT não pode entrar")
        pat = [e["incentivos"]["PAT"] for e in self.cat if "PAT" in e["incentivos"]]
        self.assertGreater(len(pat), 1000)
        self.assertTrue(all("não destina" in p.get("papel", "") or "não associações" in p.get("papel", "") or "trabalhadores" in p.get("papel", "") for p in pat[:500]))
        self.assertFalse((ROOT / "biblioteca_alexandria/base/incentivos/pat_beneficiarias_ativas_2026-03-31.jsonl.gz").exists())

    def test_icone_do_pat_aceso_no_painel(self):
        R = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))
        acesos = sum(1 for e in R["empresas"] for p in (e.get("programas") or []) if p.get("chave") == "pat" and p.get("verificado"))
        self.assertGreater(acesos, 1000, "ícone do PAT precisa acender para as empresas com adesão")

    def test_leitura_de_valor_brasileiro(self):
        from src.catalogo_incentivos import valor_br
        self.assertEqual(valor_br("R$ 1.373.032,92"), 1373032.92); self.assertEqual(valor_br(290000), 290000.0)


if __name__ == "__main__":
    unittest.main()
