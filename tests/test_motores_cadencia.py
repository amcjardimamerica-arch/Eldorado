"""12/10/2026 (conselho, motores sem funcionamento): status pela cadência do motor; leitura parcial é atenção;
SALIC conta editais e janela; fluxo 34 próprio para os motores de empresas, com recuperação diária."""
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import status_motores as S


class TesteCadencia(unittest.TestCase):
    def test_janela_pela_cadencia(self):
        self.assertEqual(S.janela_do_motor({"id": "x"}, {"dias": "todos"}), 26)
        self.assertEqual(S.janela_do_motor({"id": "motor-gife"}, {"dias": "dom"}), 7 * 24 + 26)
        self.assertEqual(S.janela_do_motor({"id": "y"}, {"dias": "seg,qui"}), 4 * 24 + 26)
        self.assertGreaterEqual(S.janela_do_motor({"id": "site-undef"}, {}), 168)

    def test_leitura_parcial_e_atencao(self):
        src = (ROOT / "src/status_motores.py").read_text(encoding="utf-8")
        self.assertIn('leitura parcial = verde com atenção', src)

    def test_salic_conta_editais_e_tenta_de_novo(self):
        src = (ROOT / "src/rouanet_salic.py").read_text(encoding="utf-8")
        self.assertIn('diag["paginas_lidas"] = int(diag.get("paginas_lidas") or 0) + 1 + len(editais)', src)
        self.assertIn("def _get_json_uma_vez", src); self.assertIn("for espera in (0, 8, 20)", src)

    def test_fluxo_34_proprio_com_recuperacao(self):
        w = (ROOT / ".github/workflows/motores-empresas.yml").read_text(encoding="utf-8")
        self.assertIn("group: motores-empresas", w); self.assertIn("7 * 24 - 6", w); self.assertIn("python -m src.empresas semanal GO", w)
        self.assertNotIn('cron: "0 6 * * 0"', (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8"))

    def test_fontes_monitoradas_so_numeros(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertNotIn("com edital aberto · ${OP.monitorados_prestes} prestes a abrir", h)


if __name__ == "__main__":
    unittest.main()
