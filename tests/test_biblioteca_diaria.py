"""11/10/2026 (titular): a tarefa do botão 'Atualizar a Biblioteca (completa)' roda uma vez por dia no fluxo da rede
neural (22 · motores da vez); o catálogo de livros tem um formato único (compacto) em todas as gravações."""
import re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteBibliotecaDiaria(unittest.TestCase):
    def test_leitor_documental_diario_antes_do_recalculo(self):
        w = (ROOT / ".github/workflows/motores-da-vez.yml").read_text(encoding="utf-8")
        i = w.index("from src.leitor_documental import aplicar"); j = w.index("python -m src.fluxo_oportunidades --completo")
        self.assertLess(i, j, "o leitor roda antes do recálculo da mesma passagem")
        self.assertIn("estado/biblioteca_diaria.txt", w)

    def test_catalogo_formato_unico(self):
        ruins = []
        for f in (ROOT / "src").glob("*.py"):
            t = f.read_text(encoding="utf-8")
            for v in re.findall(r"^(\w+) = ROOT / \"biblioteca_alexandria/fontes/motores\.json\"", t, re.M):
                for m in re.finditer(rf"{v}\.write_text\(json\.dumps\(([^\n]*)", t):
                    if 'separators=(",", ":")' not in m.group(1):
                        ruins.append(f"{f.name}: {m.group(0)[:80]}")
                if re.search(rf"write_json\({v}\b", t):
                    ruins.append(f"{f.name}: write_json({v})")
        self.assertEqual(ruins, [], "toda gravação do catálogo é compacta — formatos alternados regravam 24 MB a cada vez")
        self.assertNotIn("write_json(cat, C)", (ROOT / "src/interceptador.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
