"""01/10 (titular): status dos motores a cada 6 horas — data da última leitura e UMA de três luzes:
verde (coletou hoje, com ou sem dados) · vermelho (erro ou falha na coleta) · cinza (não rodou). Sem verde claro."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TesteStatusMotores(unittest.TestCase):
    def setUp(self):
        import src.status_motores as S
        self.S = S; S._DIARIO = {}

    def test_tres_luzes(self):
        h = "2026-10-01"
        self.assertEqual(self.S.status_de({"id": "a", "ultima_leitura": "2026-10-01T14:00:00+00:00", "dias": [{"d": h, "cor": "azul"}]}, h)["luz"], "verde")
        self.assertEqual(self.S.status_de({"id": "b", "ultima_leitura": "2026-10-01T14:00:00+00:00", "dias": [{"d": h, "cor": "amarelo", "n": 3}]}, h)["luz"], "verde")
        self.assertEqual(self.S.status_de({"id": "c", "ultima_leitura": "2026-10-01T14:00:00+00:00", "dias": [{"d": h, "cor": "vermelho"}]}, h)["luz"], "vermelho")
        self.assertEqual(self.S.status_de({"id": "d", "ultima_leitura": "2026-09-30T14:00:00+00:00", "dias": [{"d": h, "cor": "cinza"}]}, h)["luz"], "cinza")

    def test_falha_parcial_e_vermelho(self):
        h = "2026-10-01"; self.S._DIARIO = {"plat-x": {h: {"cor": "amarelo", "falhas": 2, "achados": 5}}}
        r = self.S.status_de({"id": "x", "ultima_leitura": "2026-10-01T14:00:00+00:00"}, h)
        self.assertEqual(r["luz"], "vermelho"); self.assertIn("2 página(s) com falha", r["resultado"])

    def test_calendario_so_tres_cores(self):
        from src.motores import _trinta_dias
        from datetime import date
        dias = _trinta_dias({"2026-10-01": {"cor": "amarelo", "achados": 2}, "2026-09-30": {"cor": "azul"}, "2026-09-29": {"cor": "verde", "falhas": 1}}, date(2026, 10, 1))
        self.assertTrue({d["cor"] for d in dias} <= {"verde", "vermelho", "cinza", "futuro"})
        self.assertEqual({d["d"]: d["cor"] for d in dias}["2026-09-29"], "vermelho")

    def test_painel_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("status_motores.json", h); self.assertNotIn("semaforoTres", h)   # a cor fica só na lateral direita
        for c in ("verde", "vermelho", "cinza"):
            self.assertIn(f".mt-item.oficial.sem-{c}{{border-right:10px solid", h)
        self.assertNotIn("sem-lendo", h.split("ofRows.map(o=>{")[1].split("join(\"\")")[0])
        w = (ROOT / ".github/workflows/status-motores.yml").read_text(encoding="utf-8")
        self.assertIn("17 0,6,12,18 * * *", w); self.assertIn("src.status_motores", w)


if __name__ == "__main__":
    unittest.main()
