"""O Piloto (21/09): gabarito, benchmark eliminatório, mineração sem ociosidade e memória curta."""
import json, pathlib, unittest
from src.piloto import gabarito, CANDIDATOS, MAPA_VEREDITO, PROMPTS_MINERACAO, minerar, entender
from src.ia_local import IALocal
ROOT = pathlib.Path(__file__).resolve().parents[1]


def falso(resp): return lambda payload: {"model": "sim", "choices": [{"message": {"content": json.dumps(resp, ensure_ascii=False)}}]}


class TestePiloto(unittest.TestCase):
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
        wf = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("actions/cache@v4", wf); self.assertIn("ia_local/modelos", wf); self.assertIn("benchmark", wf)
        self.assertIn("Pousar 3 segundos e decolar de novo", wf)                         # ciclo contínuo: um voo chama o seguinte
        self.assertIn("prazo inventado", (ROOT / "src/piloto.py").read_text(encoding="utf-8").lower().replace("prazos inventados", "prazo inventado"))

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
        self.assertTrue((ROOT / "estado/piloto/catalogo_entendimento.json").exists())
        cfg = json.loads((ROOT / "config/piloto.json").read_text(encoding="utf-8"))
        self.assertIn("orcamento", cfg); self.assertIn("prazo inventado", cfg["regra"])


if __name__ == "__main__":
    unittest.main()


class TesteConstituicaoEConselho(unittest.TestCase):
    def test_constituicao_tres_niveis_e_regra(self):
        c = json.loads((ROOT / "config/constituicao_piloto.json").read_text(encoding="utf-8"))
        self.assertEqual([p["nivel"] for p in c["prioridades"]], [1, 2, 3])
        self.assertIn("trecho literal", c["regra_inegociavel"])
        self.assertIn("ocioso", c["premissa"].lower())
        self.assertIn("Lucro Real", " ".join(" ".join(p["tarefas"]) for p in c["prioridades"]))
        self.assertIn("claude_a_cada_3_dias", c["divisao_de_trabalho"]); self.assertIn("claude_desktop_diario", c["divisao_de_trabalho"])

    def test_acionamento_automatico_e_pacote_do_conselho(self):
        wf = (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8")
        self.assertIn("Acionar o Piloto quando houver edital novo", wf); self.assertIn("actions: write", wf)
        wc = (ROOT / ".github/workflows/conselho.yml").read_text(encoding="utf-8"); self.assertIn("*/3", wc)
        from src.pacote_conselho import montar
        r = montar(3); self.assertIn("bloqueios", r)
        t = (ROOT / "estado/pacote_conselho.md").read_text(encoding="utf-8")
        for x in ("Relatório de aprendizado e bloqueios", "Perguntas para o conselho", "anota o modelo"): self.assertIn(x, t)

    def test_relatorio_aponta_o_modelo(self):
        an = json.loads((ROOT / "dados/editais/analises.json").read_text(encoding="utf-8"))
        self.assertTrue(all(v.get("modelo") for v in an.values()))
        self.assertTrue(any(v["modelo"] == "Claude Fable 5.1" for v in an.values()))
        html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("com o modelo <b>${esc(R.modelo)}</b>", html); self.assertIn("Constituição:", html)
        from src.piloto import aprender, fila_nivel1
        self.assertTrue(callable(aprender)); self.assertIsInstance(fila_nivel1(), list)
