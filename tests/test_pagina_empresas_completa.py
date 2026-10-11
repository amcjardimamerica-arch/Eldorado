"""11/10/2026 (titular): página de empresas com todos os programas do catálogo; lista de doação e patrocínio com as
empresas observadas, do Espião e de chamamentos privados, sem teto e sem duplicatas; só doadora privada."""
import json, re, sys, unittest
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePagina(unittest.TestCase):
    def test_programas_e_sem_duplicata(self):
        A = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))["empresas"]
        pr = Counter(p["chave"] for e in A for p in (e.get("programas") or []))
        for k in ("pronon", "pronas", "esporte", "rouanet"):
            self.assertGreater(pr[k], 0, k)
        for orig in ("destinação tributária", "doação e patrocínio"):
            nomes = Counter(re.sub(r"[^a-z0-9]", "", e["nome"].lower())[:40] for e in A if e.get("origem") == orig)
            self.assertEqual([k for k, v in nomes.items() if v > 1], [], orig)

    def test_doadora_privada(self):
        from src.biblioteca_empresas import doadora_privada
        for n in ("Fundação Grupo Boticário", "Zurich Seguros", "Instituto Genésio A. Mendes", "Inter-American Foundation"):
            self.assertTrue(doadora_privada(n), n)
        for n in ("Agência Nacional de Águas", "FAPESP", "Extranewsgo", "Associação Nacional dos Catadores", "Social Grant 2026: Applications open", "Prefeitura de Aparecida", "Grantstation"):
            self.assertFalse(doadora_privada(n), n)
        self.assertIn("novas_de_patrocinio()", (ROOT / "src/biblioteca_empresas.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
