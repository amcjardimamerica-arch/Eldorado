"""O cargo de Piloto (22/09): ocupante trocável, escopo de sniper, memória de erros."""
import json, pathlib, unittest
from src.cargo_piloto import cargo, ocupante, criterio, aprovado_no_criterio, registrar_erro, licoes_para_o_prompt, estatistica, MEM
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteCargo(unittest.TestCase):
    def test_ocupante_eleito_cumpre_o_criterio_do_titular(self):
        """O cargo pode estar VAGO — é estado legítimo desde 23/09, quando o ocupante caiu
        abaixo do critério e nenhum substituto havia sido medido. Vago não é falha: é a
        recusa de manter um reprovado por inércia."""
        o = ocupante(); c = criterio()
        if o.get("vago"):
            self.assertIsNone(o["nome"]); self.assertTrue(o["motivo"])
            self.assertIn("rede determinística", o["como_o_piloto_voa"])
            return
        self.assertEqual(o["id"], "llama-3.2-3b")
        self.assertGreaterEqual(o["desempenho"]["acerto"], c["assertividade_minima"])   # ≥ 50%
        self.assertEqual(o["desempenho"]["prazos_inventados"], 0)
        self.assertLessEqual(o["gb"], c["tamanho_maximo_gb"])                            # leve
        self.assertGreaterEqual(o["desempenho"]["tokens_por_s"], c["velocidade_minima_tokens_s"])
        self.assertTrue(o["por_que"] and o["fraqueza_conhecida"])
        cfg = json.loads((ROOT / "config/piloto.json").read_text(encoding="utf-8"))
        from src.piloto import cfg as cfg_op
        self.assertEqual(cfg_op()["modelo_vencedor"], "llama-3.2-3b")                    # o cargo manda no operacional

    def test_escopo_de_sniper_sem_projetos_nem_documentos(self):
        e = cargo()["escopo"]
        self.assertTrue(any("encontrar oportunidades" in x for x in e["faz"]))
        self.assertTrue(any("assertividade dos motores" in x for x in e["faz"]))
        for proibido in ("elaborar projeto", "preencher documentos", "plano de trabalho", "decidir inscrição"):
            self.assertTrue(any(proibido.split()[0] in x for x in e["nao_faz"]), proibido)
        src = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
        self.assertIn("def nivel2_classificar", src); self.assertNotIn("def nivel2_enquadrar", src)
        self.assertIn("projeto e documentos não são do cargo", src)

    def test_troca_do_ocupante_e_uma_linha(self):
        c = cargo()
        self.assertGreaterEqual(len(c["banco_de_reserva"]), 4)
        for r in c["banco_de_reserva"]:
            self.assertTrue(r["url"].startswith("https://") and r["gb"] <= 3.0 and r["porque"])
        self.assertIn("ex_ocupantes", c); self.assertEqual(len(c["como_trocar_o_piloto"]), 3)
        ok, _ = aprovado_no_criterio({"acerto": 0.62, "prazos_inventados": 0, "falso_positivo": 0.2, "gb": 1.1, "tokens_por_s": 25})
        self.assertTrue(ok)
        for ruim in ({"acerto": 0.62, "prazos_inventados": 1, "gb": 1.1, "tokens_por_s": 25},
                     {"acerto": 0.40, "prazos_inventados": 0, "gb": 1.1, "tokens_por_s": 25},
                     {"acerto": 0.62, "prazos_inventados": 0, "falso_positivo": 0.5, "gb": 1.1, "tokens_por_s": 25},
                     {"acerto": 0.62, "prazos_inventados": 0, "gb": 4.7, "tokens_por_s": 25},
                     {"acerto": 0.62, "prazos_inventados": 0, "gb": 1.1, "tokens_por_s": 4}):
            self.assertFalse(aprovado_no_criterio(ruim)[0], ruim)

    def test_memoria_de_erros_vira_licao_no_prompt(self):
        # com o cargo vago o prompt não traz nome de ocupante, mas as lições continuam
        antes = MEM.read_text(encoding="utf-8") if MEM.exists() else None
        try:
            # parte do zero: o prompt só carrega as lições mais recentes, e com a memória
            # acumulada de muitos voos a lição recém-registrada não entrava no corte
            MEM.write_text(json.dumps({"erros": {}, "total": 0}, ensure_ascii=False), encoding="utf-8")
            registrar_erro("falso_positivo", "CREDENCIAMENTO DE EMPRESAS para exames", "reprovado", "aprovado", "é contratação de serviço")
            registrar_erro("falso_positivo", "CREDENCIAMENTO DE EMPRESAS para exames", "reprovado", "aprovado", "é contratação de serviço")
            registrar_erro("falso_negativo", "Chamamento 05/2026 termo de fomento", "aprovado", "reprovado")
            L = licoes_para_o_prompt()
            self.assertIn("ERROS A NÃO REPETIR", L); self.assertIn("você já errou 2x", L); self.assertIn("NÃO é fomento", L); self.assertIn("É fomento", L)
            self.assertEqual(estatistica()["por_tipo"]["falso_positivo"], 2)
            ia = (ROOT / "src/ia_local.py").read_text(encoding="utf-8")
            self.assertIn("licoes_para_o_prompt", ia)                                    # entra no prompt da classificação
            sd = (ROOT / "src/piloto.py").read_text(encoding="utf-8")
            self.assertIn('registrar_erro("falso_positivo"', sd)                          # e o erro medido volta para a memória
        finally:
            if antes is None: MEM.unlink(missing_ok=True)
            else: MEM.write_text(antes, encoding="utf-8")

    def test_workflow_roda_so_o_ocupante_no_dia_a_dia(self):
        w = (ROOT / ".github/workflows/piloto.yml").read_text(encoding="utf-8")
        self.assertIn("alvo = [oc]", w); self.assertIn("modo == \"avaliar\"", w)
        self.assertIn("upload-artifact", w); self.assertIn("reset -q --hard origin/main", w)
        self.assertIn("src.cargo_piloto avaliar", w)


if __name__ == "__main__":
    unittest.main()
