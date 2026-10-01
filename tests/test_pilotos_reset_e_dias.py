"""01/10: reset dos Pilotos com os achados guardados nos livros; oportunidades por dia; ciclo criativo a cada 100
pesquisas; restrições fixas só negativas."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePilotos(unittest.TestCase):
    def test_historico_preservado_e_por_dia(self):
        for f in ("estado/pilotos/historico/espiao_missoes_ate_2026-10-01.jsonl.xz", "estado/pilotos/historico/interceptador_voos_ate_2026-10-01.jsonl.xz"):
            self.assertTrue((ROOT / f).exists(), f)
        d = json.loads((ROOT / "docs/dados/achados_pilotos.json").read_text(encoding="utf-8"))
        self.assertIn("espiao", d); self.assertIn("interceptador", d)
        for p in ("espiao", "interceptador"):
            for dia, L in d[p].items():
                for o in L:
                    self.assertIn("titulo", o); self.assertNotIn("consulta", o)   # só oportunidades, sem as buscas

    def test_ciclo_criativo_e_restricoes(self):
        from src.skills.aprendizado import ciclo_criativo, parametros, _proibido
        ciclo_criativo(); P = parametros()
        e = P["espiao"]["estrategia_criativa"]; self.assertGreaterEqual(len(e["pool"]), 8)
        rf = P["espiao"]["restricoes_fixas"]
        self.assertTrue(all(not _proibido(q, rf) for q in e["pool"]), "a estratégia criativa nunca usa o que é proibido")
        self.assertIn("alvos_proibidos", P["interceptador"]["restricoes_fixas"])
        self.assertEqual(ciclo_criativo(), {"sem_troca": True}, "só troca a cada 100 pesquisas")

    def test_painel_dias(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertEqual(h.count("data-dias-piloto="), 2); self.assertIn("window.abreDiaPiloto=", h)


if __name__ == "__main__":
    unittest.main()
