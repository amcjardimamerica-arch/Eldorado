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
        self.assertEqual(self.S.status_de({"id": "d", "ultima_leitura": "2026-09-30T14:00:00+00:00", "dias": [{"d": h, "cor": "cinza"}]}, h)["luz"], "vermelho")
        # 10/10 (titular): cinza agora é só INATIVO; motor ativo há mais de 26 h sem ler é FALHA

    def test_falha_parcial_e_vermelho(self):
        h = "2026-10-01"; self.S._DIARIO = {"plat-x": {h: {"cor": "amarelo", "falhas": 2, "achados": 5}}}
        r = self.S.status_de({"id": "x", "ultima_leitura": "2026-10-01T14:00:00+00:00"}, h)
        self.assertEqual(r["luz"], "vermelho"); self.assertIn("2 página(s) com falha", r["resultado"])

    def test_calendario_segue_o_indice_original(self):
        """02/10 (titular): o calendário mantém as cinco cores do índice; as três cores de status são só da lateral."""
        from src.motores import _trinta_dias
        from datetime import date
        dias = {d["d"]: d["cor"] for d in _trinta_dias({"2026-10-01": {"cor": "amarelo", "achados": 2}, "2026-09-30": {"cor": "azul"},
                                                         "2026-09-29": {"cor": "verde"}, "2026-09-28": {"cor": "vermelho"}}, date(2026, 10, 1))}
        self.assertEqual([dias[k] for k in ("2026-10-01", "2026-09-30", "2026-09-29", "2026-09-28", "2026-09-27")], ["amarelo", "azul", "verde", "vermelho", "cinza"])
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for c in ("cinza", "azul", "amarelo", "verde", "vermelho"):
            self.assertIn(f".mt-cal .mtd-{c}{{", h)
        self.assertNotIn(".mt-item .mt-cal .bdia.mtd-verde{", h)

    def test_painel_e_fluxo(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("status_motores.json", h); self.assertNotIn("semaforoTres", h)   # a cor fica só na lateral direita
        self.assertIn(".mt-item.sem-verde{border-right:6px solid var(--ok)}", h)          # cores suaves de antes
        self.assertIn(".mt-item.sem-vermelho{border-right:6px solid var(--urgente)}", h)
        self.assertIn(".mt-item.oficial.sem-cinza{border-right:6px solid #C9CED6}", h)
        self.assertNotIn("sem-lendo", h.split("ofRows.map(o=>{")[1].split("join(\"\")")[0])
        w = (ROOT / ".github/workflows/status-motores.yml").read_text(encoding="utf-8")
        self.assertIn("47 10,14,19 * * *", w); self.assertIn("17 1 * * *", w); self.assertIn("src.status_motores", w)   # 02/10: itinerário do maestro


if __name__ == "__main__":
    unittest.main()
