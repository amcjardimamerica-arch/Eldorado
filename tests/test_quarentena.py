"""14/10/2026: quarentena de testes com motivo; portão dos fluxos 00 e 01 sem ela; a análise do sistema a lista."""
import json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteQuarentena(unittest.TestCase):
    def test_cada_um_com_categoria_e_motivo(self):
        Q = json.loads((ROOT / "config/testes_quarentena.json").read_text(encoding="utf-8"))["modulos"]
        for k, v in Q.items():
            self.assertTrue((ROOT / "tests" / f"{k}.py").exists(), k)
            self.assertIn(v["categoria"], ("fotografia de data", "tela retirada ou redesenhada", "configuração mudou", "defeito real a corrigir", "lento"))
            self.assertTrue(v["motivo"])

    def test_portao_e_diagnostico(self):
        self.assertIn("python scripts/rodar_testes.py", (ROOT / ".github/workflows/00-prontidao.yml").read_text(encoding="utf-8"))
        self.assertIn("python scripts/rodar_testes.py", (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8"))
        self.assertIn("teste_em_quarentena_defeito", (ROOT / "src/diagnostico_sistema.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
