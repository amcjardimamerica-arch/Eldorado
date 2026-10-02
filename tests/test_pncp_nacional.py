"""02/10 (titular): o PNCP recebe TODAS as oportunidades do Brasil e cada uma ganha livro na Biblioteca."""
import json, sys, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestePncpNacional(unittest.TestCase):
    def test_config_sem_restricao_a_goias(self):
        c = json.loads((ROOT / "config/pncp_osc.json").read_text(encoding="utf-8"))
        self.assertEqual(c["fonte_a"]["ufs"], ["*"]); self.assertIn({}, c["fonte_b"]["escopos"]); self.assertTrue(c["abrangencia"]["nacional"])

    def test_outro_estado_nao_e_ruido_por_territorio(self):
        from src import pncp_osc as P
        m = {"titulo": "Chamamento público para organizações da sociedade civil — termo de colaboração", "objeto": "seleção de OSC",
             "orgao": "MUNICIPIO DE CAMPINAS", "uf": "SP", "municipio": "Campinas", "esfera": "M", "encerramento": "2026-12-01"}
        c = P.classificar_item(m, date(2026, 10, 2), P.TODAS_UFS)
        self.assertNotIn("fora do território", " ".join(c.get("motivos") or []))
        self.assertEqual(c["territorio"], "SP/Campinas")

    def test_livro_para_pncp_em_qualquer_estado(self):
        from src.curadoria_biblioteca import fora_da_abrangencia
        from src.opressores_repositorio import dispensa
        self.assertFalse(fora_da_abrangencia({"programa": "Chamamento", "orgao": "Prefeitura de Campinas", "geo": "SP", "pagina": "https://pncp.gov.br/app/editais/1/2026/3"}))
        self.assertIsNone(dispensa({"titulo": "Chamamento público OSC", "orgao": "Prefeitura de Campinas", "uf": "SP", "origem": "motor pncp"}))
        self.assertIsNotNone(dispensa({"titulo": "Chamamento público OSC", "orgao": "Prefeitura de Campinas", "uf": "SP", "origem": "motor x"}))   # outros motores: regra mantida


if __name__ == "__main__":
    unittest.main()
