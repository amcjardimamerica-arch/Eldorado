"""O Síndico (21/09): gabarito, benchmark eliminatório, mineração sem ociosidade e memória curta."""
import json, pathlib, unittest
from src.sindico import gabarito, CANDIDATOS, MAPA_VEREDITO, PROMPTS_MINERACAO, minerar, entender
from src.ia_local import IALocal
ROOT = pathlib.Path(__file__).resolve().parents[1]


def falso(resp): return lambda payload: {"model": "sim", "choices": [{"message": {"content": json.dumps(resp, ensure_ascii=False)}}]}


class TesteSindico(unittest.TestCase):
    def test_gabarito_vem_das_validacoes_do_titular(self):
        g = gabarito()
        self.assertGreaterEqual(len(g), 400)
        self.assertTrue(all(x["veredito"] in ("aprovado", "atencao", "reprovado") for x in g))
        self.assertGreaterEqual(sum(1 for x in g if len(x["texto"]) > 200), 300)

    def test_quatro_candidatos_um_por_vez_e_eliminatorio(self):
        self.assertEqual(len(CANDIDATOS), 4)
        self.assertEqual({c["id"] for c in CANDIDATOS}, {"qwen2.5-3b", "qwen2.5-7b", "gemma-2-2b", "llama-3.2-3b"})
        self.assertTrue(all(c["gb"] <= 5 and c["url"].startswith("https://huggingface.co/") for c in CANDIDATOS))
        self.assertEqual(MAPA_VEREDITO["fomento_osc"], "aprovado")
        wf = (ROOT / ".github/workflows/sindico.yml").read_text(encoding="utf-8")
        self.assertIn("actions/cache@v4", wf); self.assertIn("ia_local/modelos", wf); self.assertIn("benchmark", wf)
        self.assertIn("4,10,16,22", wf)                                     # 4 ciclos por dia
        self.assertIn("prazo inventado", (ROOT / "src/sindico.py").read_text(encoding="utf-8").lower().replace("prazos inventados", "prazo inventado"))

    def test_mineracao_gera_prompt_diferente_e_registra_negativo(self):
        self.assertGreaterEqual(len(PROMPTS_MINERACAO), 5)
        self.assertTrue(any("lucro real" in p.lower() and "goiás" in p.lower() for _, p in PROMPTS_MINERACAO))
        self.assertTrue(any("patrocinar eventos" in p.lower() for _, p in PROMPTS_MINERACAO))
        ia = IALocal(transporte=falso([{"empresa": "X S.A.", "pista": "instituto", "onde_procurar": "https://x.com.br/instituto"}, {"empresa": "Y", "onde_procurar": ""}]))
        m = minerar(ia, set())
        self.assertEqual(m["prompt"], "empresas_lucro_real_go"); self.assertEqual(len(m["pistas"]), 1); self.assertFalse(m["negativo"])
        m2 = minerar(IALocal(transporte=falso([])), {"empresas_lucro_real_go"})
        self.assertEqual(m2["prompt"], "patrocinadores_eventos_go"); self.assertTrue(m2["negativo"]); self.assertIn("não repetir", m2["aprendizado"])
        m3 = minerar(ia, {k for k, _ in PROMPTS_MINERACAO}); self.assertIsNone(m3["prompt"])

    def test_entendimento_cobre_a_biblioteca_inteira(self):
        e = entender()
        for k in ("editais", "analises", "fontes", "leis", "motores", "empresas"):
            self.assertIn(k, e); self.assertTrue(e[k].get("total") is not None)
        self.assertTrue((ROOT / "estado/sindico/catalogo_entendimento.json").exists())
        cfg = json.loads((ROOT / "config/sindico.json").read_text(encoding="utf-8"))
        self.assertIn("orcamento", cfg); self.assertIn("prazo inventado", cfg["regra"])


if __name__ == "__main__":
    unittest.main()
