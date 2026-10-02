"""02/10 (titular): linha de produção, rede neural, planos de correção e skills dos motores."""
import json, sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import linha_producao as L, rede_neural as N, planos_correcao as P


class TesteLinha(unittest.TestCase):
    def test_canal_canonico_e_familia(self):
        self.assertEqual(L.canal_canonico("pncp"), "pncp-api"); self.assertEqual(L.canal_canonico("plat-abcr"), "abcr")
        self.assertEqual(L.familia("querido-diario"), "diario_oficial"); self.assertEqual(L.familia("pncp-api"), "portal_chamamentos")

    def test_contrato_manda_para_reprocessar_nao_para_o_lixo(self):
        cfg = json.loads((ROOT / "config/linha_producao.json").read_text(encoding="utf-8"))
        self.assertIn("buscador", L.contrato({"titulo": "Edital de chamamento X", "url": "https://duckduckgo.com/l?x", "fonte_id": "a"}, cfg))
        self.assertIsNone(L.contrato({"titulo": "Edital de chamamento X", "url": "https://goias.gov.br/x", "fonte_id": "a"}, cfg))
        o = L.run([{"id": "1", "titulo": "Edital de chamamento X", "url": "https://duckduckgo.com/l?x", "fonte_id": "a"}], gravar=False)
        self.assertEqual(o["funil"]["etapas"].get("REPROCESSAR"), 1)

    def test_mesma_oportunidade_em_dois_canais_e_corroboracao(self):
        cfg = json.loads((ROOT / "config/linha_producao.json").read_text(encoding="utf-8"))
        regs = [{"id": "a", "titulo": "Edital Goyazes de incentivo cultural 2026", "url": "https://x/1", "uf": "GO", "fonte_id": "abcr"},
                {"id": "b", "titulo": "Edital Goyazes de incentivo cultural 2026", "url": "https://y/2", "uf": "GO", "fonte_id": "observatorio-3setor"},
                {"id": "c", "titulo": "Chamamento do Fundo da Criança de Anápolis", "url": "https://z/3", "uf": "GO", "fonte_id": "do-goias"}]
        e = L.resolver_entidades(regs, cfg)
        self.assertEqual(e["a"], e["b"]); self.assertNotEqual(e["a"], e["c"])


class TesteRede(unittest.TestCase):
    def test_aprende_e_e_calibravel(self):
        X = [[1, 2, 3]] * 30 + [[4, 5, 6]] * 30; y = [1] * 30 + [0] * 30
        r = N.Rede().treinar(X, y, epocas=10)
        self.assertGreater(r.prever([1, 2, 3]), 0.8); self.assertLess(r.prever([4, 5, 6]), 0.2)
        r.T = 5.0; self.assertLess(r.prever([1, 2, 3]), 0.99)        # temperatura amacia a confiança
        self.assertEqual(N.auc([1, 0, 1, 0], [0.9, 0.1, 0.8, 0.2]), 1.0)

    def test_copia_de_oportunidade_real_e_positivo(self):
        self.assertTrue(N.COPIA.search("link do edital zurich 2026 — cópia do item principal"))
        self.assertTrue(N.AUC_MINIMA >= 0.8)


class TestePlanosESkills(unittest.TestCase):
    def test_diagnostico(self):
        self.assertEqual(P.diagnosticar("x", {"leituras": 9, "achados_total": 0}, {}, {}, date(2026, 10, 2))[0], "sem_rendimento")
        self.assertIsNone(P.diagnosticar("x", {"leituras": 9, "achados_total": 0}, {}, {}, date(2026, 10, 2), "insumo")[0])
        self.assertEqual(P.diagnosticar("x", {}, {}, {"motivo": "exige IP Brasil"}, date(2026, 10, 2))[0], "exige_brasil")

    def test_skills_dos_motores(self):
        M = json.loads((ROOT / "config/skills_motores.json").read_text(encoding="utf-8"))["motores"]
        for v in M.values():
            for s in v["skills"]:
                self.assertTrue((ROOT / "skills" / s / "SKILL.md").exists(), s)
        f = (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8")
        for m in ("linha_producao", "rede_neural", "planos_correcao"):
            self.assertIn(m, f)


if __name__ == "__main__":
    unittest.main()
