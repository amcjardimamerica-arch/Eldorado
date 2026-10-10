"""11/10/2026 (titular): 'não consta' é dispensa justificada só com documentos lidos e nunca no núcleo; 'não lido'
nunca conta para ouro; veredito vermelho (validação manual); 30 dias sem validação → arquivada."""
import sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))


class TesteDispensaNaoConsta(unittest.TestCase):
    def test_regras(self):
        import importar_revisao_abertas as I
        doc = "https://orgao.go.gov.br/edital.pdf"
        x = {"id": "t1", "veredito": "ouro", "itens": {}, "dispensas": {
            "Prazo de recurso": {"tipo": "nao_consta", "motivo": "edital não prevê fase recursal", "documentos_lidos": [doc]},
            "Resultado": {"tipo": "nao_consta", "motivo": "sem data", "documentos_lidos": []},
            "Objeto": {"tipo": "nao_consta", "motivo": "x", "documentos_lidos": [doc]}}}
        cert, av = I.certidao_de(x, "teste")
        self.assertIn("Prazo de recurso", cert["dispensas"]); self.assertEqual(cert["dispensas"]["Prazo de recurso"]["tipo"], "nao_consta")
        self.assertNotIn("Resultado", cert["dispensas"], "sem documentos lidos não é dispensa")
        self.assertNotIn("Objeto", cert["dispensas"], "núcleo nunca é dispensado")
        self.assertIn("validacao_manual", I.VIGENTES)


class TesteSaneamento(unittest.TestCase):
    def setUp(self):
        from src import saneamento_motores as S
        self.S = S; S.limpar_cache()

    def test_vermelho_por_revisao(self):
        S = self.S
        S._VER = None
        orig = S.vereditos
        S.vereditos = lambda: {"zz1": {"veredito": "validacao_manual", "motivo": "site exige login", "origem": "CHROME"}}
        try:
            out = S.sanear_registro({"id": "zz1", "titulo": "Edital de chamamento", "url": "https://x.go.gov.br/e"}, date(2026, 10, 11))
        finally:
            S.vereditos = orig
        self.assertEqual(out["ajustes"]["selo_validacao"], "validacao_manual"); self.assertIn("VALIDAÇÃO MANUAL", out["ajustes"]["motivo_tipo"])
        self.assertIsNone(out["descartar"], "vermelho fica na caixa até a decisão manual")

    def test_30_dias_sem_validacao(self):
        S = self.S
        r = {"id": "m15", "titulo": "Edital de chamamento público para OSC", "url": "https://x.go.gov.br/edital", "descoberto_em": "2026-08-20"}
        self.assertIn("M15", S.sanear_registro(r, date(2026, 10, 11))["regras"])
        self.assertNotIn("M15", S.sanear_registro({**r, "descoberto_em": "2026-10-01"}, date(2026, 10, 11))["regras"])
        self.assertNotIn("M15", S.sanear_registro({**r, "fim": "2026-11-30"}, date(2026, 10, 11))["regras"], "prazo vigente: o prazo decide")
        self.assertNotIn("M15", S.sanear_registro({**r, "fim": "2026-09-01"}, date(2026, 10, 11))["regras"], "prazo vencido também: o prazo decide (encerrada)")
        self.assertNotIn("M15", S.sanear_registro({**r, "prazo_texto": "inscrições até 30/11/2026"}, date(2026, 10, 11))["regras"], "prazo só no texto também")

    def test_painel_vermelho(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn('e.selo_validacao==="validacao_manual"', h); self.assertIn(".selo-val.val-manual", h)


if __name__ == "__main__":
    unittest.main()
