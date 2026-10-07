"""04/10/2026 — REGRA PERMANENTE: nenhuma qualificação sem o critério (src/criterio_selos.py)."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.criterio_selos import auditar_estrelas, dispensa_valida, nivel, ORDEM


class TesteRegra(unittest.TestCase):
    def test_auditoria_rebaixa(self):
        it = [{"id": "x", "selo": "ouro", "checklist": {"Objeto": {"s": "ok", "v": "Seleção de projetos"}}}]
        casos = auditar_estrelas(it)
        self.assertEqual((it[0]["selo"], casos[0]["tinha"]), (None, "ouro"))

    def test_dispensa_precisa_de_justificativa(self):
        self.assertFalse(dispensa_valida("não informado no edital"))
        self.assertTrue(dispensa_valida("dispensado pelo edital: não há fase de recurso"))

    def test_mapa_publicado_respeita_o_criterio(self):
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        its = [i for v in F.get("itens_por_uf", {}).values() for i in v]
        if not any("selo_faltando" in i for i in its):
            self.skipTest("mapa gerado antes da regra de 04/10")
        fora = [i["id"] for i in its if ORDEM.get(i.get("selo"), 0) > ORDEM.get(nivel(i.get("checklist") or {}), 0)]
        self.assertFalse(fora, f"{len(fora)} oportunidade(s) com estrela acima do critério")


if __name__ == "__main__":
    unittest.main()
