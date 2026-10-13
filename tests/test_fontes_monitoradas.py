"""11/10/2026 (titular): fontes monitoradas = livros com edital aberto, prestes a abrir (previsão) ou de fluxo contínuo;
cada livro monitorado tem pesquisa focada no edital (aberto ou esperado)."""
import sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import opressores as O


class TesteAlvo(unittest.TestCase):
    def test_prestes_continuo_e_fora(self):
        f = {"p1": {"id": "p1", "previsao": {"abertura": "2026-10-20", "ativar_em": "2026-09-20", "encerramento": "2026-11-30", "confianca": "media"},
                    "pagina": "https://orgao.go.gov.br/editais", "historico": [{"id": "h1", "pagina_oficial": "https://orgao.go.gov.br/edital-2025"}]},
             "p2": {"id": "p2", "previsao": {"abertura": "2027-08-03", "ativar_em": "2027-07-04", "encerramento": "2027-09-23"}},
             "c1": {"id": "c1", "regime_inscricao": "contínuo", "pagina": "https://fundo.org.br"},
             "x1": {"id": "x1"}}
        a = O.alvo_de_monitoramento(f, date(2026, 10, 11))
        self.assertEqual(a["p1"]["tipo"], "prestes"); self.assertEqual(a["c1"]["tipo"], "contínuo")
        self.assertNotIn("p2", a, "previsão distante não é monitorada"); self.assertNotIn("x1", a, "sem edital aberto nem previsão: não monitora")
        self.assertIn("https://orgao.go.gov.br/edital-2025", a["p1"]["foco"]["onde_publicou_antes"])

    def test_prompt_focado(self):
        f = {"programa": "Prêmio X", "_foco": {"tipo": "edital esperado", "abertura_prevista": "2026-10-20", "confianca": "media", "onde_publicou_antes": ["https://orgao.go.gov.br/editais"]}}
        p = O.prompt_para_fonte(f, None, ["Valor"], [])
        self.assertIn("deve ABRIR por volta de 2026-10-20", p); self.assertIn("Não reaproveite dados da edição anterior", p)

    def test_regra_no_ciclo_e_cartao(self):
        s = (ROOT / "src/opressores.py").read_text(encoding="utf-8")
        self.assertIn('if o.startswith("automática") and fid not in alvo:', s); self.assertIn('"monitoramento"', s)
        self.assertNotIn("prestes a abrir (previsão)", (ROOT / "docs/dashboard.html").read_text(encoding="utf-8"), "12/10 (titular): o mostrador mostra só os números")


if __name__ == "__main__":
    unittest.main()
