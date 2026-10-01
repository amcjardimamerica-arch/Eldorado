"""02/10 (titular): o motor encontra a oportunidade → o livro existente recebe os dados atuais e guarda o HISTÓRICO
dos parâmetros; a previsão da próxima abertura ATIVA o livro 30 dias antes."""
import json, sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.previsao_livros import prever, janelas, PADRAO


class TestePrevisaoLivros(unittest.TestCase):
    def test_historico_dos_parametros(self):
        from src.livros_regra import anotar_checklist
        x = {"programa": "Edital X", "historico": [{"id": "a", "titulo": "Edital X 2025"}, {"id": "b", "titulo": "Edital X 2026"}]}
        anotar_checklist(x, {"Valor": "R$ 10 mil"}, "motor A", edicao={"id": "a"})
        anotar_checklist(x, {"Valor": "R$ 15 mil"}, "motor B", edicao={"id": "b"})
        self.assertEqual(x["historico"][0]["parametros"]["Valor"], "R$ 10 mil")
        self.assertEqual(x["livro"]["historico_parametros"][-1]["mudou"]["Valor"], {"antes": "R$ 10 mil", "agora": "R$ 15 mil"})

    def test_previsao_e_ativacao_30_dias_antes(self):
        x = {"historico": [{"inicio": "2024-03-01", "fim": "2024-04-15"}, {"inicio": "2025-03-03", "fim": "2025-04-18"}]}
        pv = prever(x, date(2026, 1, 10), PADRAO)
        self.assertEqual(pv["situacao"], "prevista"); self.assertEqual(pv["confianca"], "media")
        self.assertTrue(pv["abertura"].startswith("2026-03")); self.assertEqual((date.fromisoformat(pv["abertura"]) - date.fromisoformat(pv["ativar_em"])).days, 30)

    def test_aberta_agora_e_continua(self):
        self.assertEqual(prever({"historico": [{"inicio": "2026-09-20", "fim": "2026-10-20"}]}, date(2026, 10, 1), PADRAO)["situacao"], "aberta agora")
        self.assertIsNone(prever({"regime_inscricao": "contínuo", "historico": [{"fim": "2025-05-01"}]}, date(2026, 10, 1), PADRAO))

    def test_datas_do_historico_de_parametros_contam(self):
        x = {"livro": {"historico_parametros": [{"mudou": {"Prazo de inscrição": {"antes": "01/03/2025 a 30/04/2025", "agora": "02/03/2026 a 30/04/2026"}}}]}}
        self.assertEqual(len(janelas(x)), 2)

    def test_no_ciclo_e_no_painel(self):
        f = (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8")
        self.assertGreater(f.index("_prev()"), f.index("aplicar_motores()"))
        P = json.loads((ROOT / "config/parametros_biblioteca.json").read_text(encoding="utf-8"))["previsao"]
        self.assertEqual(P["ativar_dias_antes"], 30)
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("ativa em ${br(m.previsao.ativar_em)}", h); self.assertIn("Histórico dos parâmetros", h)


if __name__ == "__main__":
    unittest.main()
