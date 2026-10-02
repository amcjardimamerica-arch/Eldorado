"""02/10 (titular): decisões sobre o parecer 238 — três públicos são OSC, identificar antes de qualificar, preparação."""
import json, sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import regras_restricao as R


class TesteDecisoes238(unittest.TestCase):
    def test_veto_duvidoso_fica_em_revisao(self):
        q = R.qualificacao_do_veto("NA-06", "Edital de premiação de pontos de cultura — Mestra Francisca Rodrigues")
        self.assertEqual(q["veredito"], "EM REVISÃO")
        self.assertEqual(R.qualificacao_do_veto("NA-02", "Pregão para aquisição de material")["veredito"], "NÃO APLICA")

    def test_livro_existente_em_veto_e_mantido_e_marcado(self):
        x = {"id": "t", "programa": "Pregão eletrônico para aquisição de merenda escolar", "pagina": "https://x.go.gov.br/p", "geo": "GO"}
        R._qualificar(x, "2026-10-02")
        self.assertEqual(x["qualificacao"]["veredito"], "NÃO APLICA"); self.assertIn("arquivar manualmente", x["qualificacao"]["acao"])
        x["qualificacao"]["manual"] = True; x["programa"] = "Chamamento de OSC — termo de fomento"
        R._qualificar(x, "2026-10-02"); self.assertTrue(x["qualificacao"]["manual"], "a qualificação manual nunca é sobrescrita")

    def test_preparacao_dos_fluxos_permanentes(self):
        c = json.loads((ROOT / "config/preparacao_fluxos.json").read_text(encoding="utf-8"))
        self.assertEqual(set(c["livros"]), {"nova-9c02d7750df1", "nova-01619b77b6f8", "nova-ac18334f53bb"})
        self.assertIn("13.019", c["documentos_base_mrosc"]["fundamento"])
        self.assertIn("preparacao_livros", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))

    def test_pncp_tres_publicos_sao_oportunidade(self):
        from src import pncp_osc as P
        for t in ("Credenciamento de Instituições de Longa Permanência para Idosos (ILPI) sem fins lucrativos",
                  "Chamamento Público de Associações Estudantis para apoio a projetos"):
            c = P.classificar_item({"titulo": t, "objeto": t, "orgao": "MUNICIPIO X", "uf": "SP", "esfera": "M", "encerramento": "2026-12-01"},
                                   date(2026, 10, 2), P.TODAS_UFS)
            self.assertEqual(c["veredito"], "OPORTUNIDADE", t)


if __name__ == "__main__":
    unittest.main()
