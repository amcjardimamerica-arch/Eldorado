"""13/10/2026 (titular): alimentação diária externa — só os campos permitidos, certificação SHA-256 e assinatura HMAC;
o destino fica nos segredos (nada no código)."""
import hashlib, hmac, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import exportar_editais_osc as X


class TesteAlimentacao(unittest.TestCase):
    def test_so_campos_permitidos(self):
        L = X.itens()
        self.assertGreater(len(L), 0)
        for i in L:
            self.assertEqual(set(i), {"nome", "link", "objeto", "abrangencia", "uf", "prazo", "continuo"})
            self.assertIn(i["abrangencia"], ("federal", "estadual")); self.assertTrue(i["link"].startswith("http"))
            self.assertFalse(any(a in i["link"] for a in X.AGREGADORES))

    def test_certificacao(self):
        corpo, h = X.pacote([{"nome": "x", "link": "https://a.gov.br", "objeto": "Cultura", "abrangencia": "federal", "uf": "", "prazo": None, "continuo": False}])
        p = json.loads(corpo); self.assertEqual(hashlib.sha256(p["itens_json"].encode()).hexdigest(), h); self.assertEqual(p["sha256"], h)
        for proibido in ("eldorado", "livro", "motor", "opressor", "github"):
            self.assertNotIn(proibido, corpo.decode().lower())

    def test_destino_so_nos_segredos(self):
        w = (ROOT / ".github/workflows/alimentacao-externa.yml").read_text(encoding="utf-8")
        self.assertIn("secrets.OSC_URL", w); self.assertNotIn("advogadogoiano", w)
        self.assertNotIn("advogadogoiano", (ROOT / "src/exportar_editais_osc.py").read_text(encoding="utf-8"))
        self.assertFalse(X.enviar.__code__.co_consts is None)


if __name__ == "__main__":
    unittest.main()
