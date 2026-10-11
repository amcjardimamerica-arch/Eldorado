"""11/10/2026 (titular): repositório único — um registro por oportunidade, todas as origens, prova na fonte, estante
como classificador, próximo passo pela rede neural e pela skill; todos os painéis no mesmo universo."""
import json, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import repositorio_unico as R


class TesteRepositorio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); T = Path(cls.tmp.name)
        cls.o = (R.SAIDA, R.RESUMO); R.SAIDA = T / "r.json"; R.RESUMO = T / "s.json"
        cls.res = R.construir(gravar=True); cls.regs = json.loads(R.SAIDA.read_text())["registros"]

    @classmethod
    def tearDownClass(cls):
        R.SAIDA, R.RESUMO = cls.o; cls.tmp.cleanup()

    def test_um_registro_por_oportunidade_e_soma(self):
        ids = [x["id"] for x in self.regs]; self.assertEqual(len(ids), len(set(ids)))
        orig = [i for x in self.regs for i in x["ids_origem"]]; self.assertEqual(len(orig), len(set(orig)), "nenhum id de origem em dois registros")
        r = self.res; self.assertEqual(r["abertas"], r["validadas"] + r["em_verificacao"] + r["validacao_manual"])

    def test_todo_registro_tem_proximo_passo_estante_e_prova(self):
        for x in self.regs:
            self.assertTrue(x["proximo_passo"]); self.assertIn(x["estante"], ("sem_livro", "bronze", "prata", "ouro"))
            self.assertEqual(set(x["itens"]), set(R.DOZE))
            for it in x["itens"].values():
                self.assertIn(it["estado"], ("comprovado", "dispensado", "nao_comprovado", "falta"))
                if it["estado"] == "comprovado":
                    self.assertTrue(it.get("trecho") or it.get("valor"))

    def test_validada_so_com_prova(self):
        for x in self.regs:
            if x["estado"] == "validada" and x["motivo_estado"].startswith("objeto e prazo"):
                self.assertEqual(x["itens"]["Objeto"]["estado"], "comprovado"); self.assertEqual(x["itens"]["Prazo de inscrição"]["estado"], "comprovado")

    def test_chrome_e_excecao_e_skills(self):
        for x in self.regs:
            if x["proximo_passo"].startswith("Chrome"):
                self.assertTrue(x["cartorio"]["tentativas"] >= 10 or x["cartorio"]["esgotada"])
        self.assertEqual(R._skill("motor agregadores · farolcultura"), "agregador"); self.assertEqual(R._skill("motor pncp-api"), "pncp")
        sk = json.loads((ROOT / "config/skills_extracao_origem.json").read_text(encoding="utf-8"))["skills"]
        for k, v in sk.items():
            self.assertEqual(sorted(v["ordem"]), list(range(1, 11)), k)

    def test_auditoria_e_integracoes(self):
        self.assertIn("auditoria", self.res)
        self.assertIn("from .repositorio_unico import construir as _repo", (ROOT / "src/fluxo_oportunidades.py").read_text(encoding="utf-8"))
        c = (ROOT / "src/cartorio.py").read_text(encoding="utf-8"); self.assertIn("_repositorio()", c); self.assertIn("_ordem_da_skill(op)", c)
        self.assertIn("RECUSADO", (ROOT / "scripts/gerar_lote_chrome.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
