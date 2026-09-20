"""Rotas duplas, léxico em duas camadas, alerta diário, validação do mês e pacote do Desktop (20/09)."""
import datetime, json, os, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteRotasELexico(unittest.TestCase):
    def test_todo_motor_regular_tem_duas_rotas_e_lexico_em_duas_camadas(self):
        from src.sensores import registro, lexico_camada1, lexico_camada2, rotas_alternativas
        cfg = json.loads((ROOT / "config/rotas_motores.json").read_text(encoding="utf-8"))
        for s in [x for x in registro() if not x.get("fontes_260")]:
            m = cfg["motores"].get(s["id"]); self.assertIsNotNone(m, s["id"])
            self.assertGreaterEqual(len(m["rotas"]), 2, f"{s['id']} precisa de 2 rotas")
            self.assertTrue(m.get("perfil"))
            t1, v1 = lexico_camada1(s); self.assertGreaterEqual(len(t1), 8); self.assertGreaterEqual(len(v1), 5)
            self.assertTrue(lexico_camada2(s))
            self.assertTrue(rotas_alternativas(s))

    def test_camada1_direciona_e_veta(self):
        from src.sensores import casa_camada1
        t = ["chamamento público", "termo de fomento", "edital"]; v = ["pregão", "aquisição de"]
        self.assertTrue(casa_camada1("Edital de chamamento público 05/2026", t, v)["passa"])
        r = casa_camada1("Pregão eletrônico — aquisição de merenda", t, v)
        self.assertFalse(r["passa"]); self.assertIn("pregão", r["veto"])
        self.assertFalse(casa_camada1("Portaria de nomeação", t, v)["passa"])

    def test_diario_que_exige_brasil_le_as_rotas_alternativas_no_github(self):
        os.environ["GITHUB_ACTIONS"] = "true"; os.environ.pop("ELDORADO_LOCAL_BR", None)
        from src.sensores import registro, _paginas
        s = [x for x in registro() if x["id"] == "do-goias"][0]
        pags = _paginas(s)
        self.assertTrue(any("goias.gov.br/cultura" in u or "goias.gov.br/social" in u or "ovg.org.br" in u for u in pags))

    def test_armadilhas_declaradas(self):
        cfg = json.loads((ROOT / "config/rotas_motores.json").read_text(encoding="utf-8"))
        self.assertIn("jusbrasil", cfg["motores"]["dje-tjgo"]["armadilha"])
        self.assertIn("termos-de-fomento", cfg["motores"]["plat-secult-go"]["armadilha"])


class TesteAlertaEValidacao(unittest.TestCase):
    def test_alerta_diario_nomeia_problema_e_acao(self):
        a = json.loads((ROOT / "estado/alerta_motores.json").read_text(encoding="utf-8"))
        self.assertEqual(a["total"], a["funcionando"] + a["em_alerta"])
        for x in a["alertas"]:
            self.assertIn(x["gravidade"], ("alta", "media")); self.assertTrue(x["problema"] and x["acao"])
        self.assertTrue((ROOT / "docs/dados/alerta_motores.json").exists())

    def test_rotulo_aguardando_coleta_local_nao_e_bloqueado(self):
        from src.motores import _aguarda_local
        self.assertTrue(_aguarda_local({"pulado_exige_brasil": True}))
        self.assertTrue(_aguarda_local({"saude": [], "diagnostico": {"motivo_zero": "aguardando coleta local (Brasil): ..."}}))
        self.assertFalse(_aguarda_local({"saude": [{"erro": "HTTPError"}], "diagnostico": {"motivo_zero": "x"}}))
        m = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8"))
        goiania = [o for o in m["oficiais"] if o["id"] == "do-goiania"][0]
        self.assertEqual(goiania["situacao"], "aguardando coleta local")

    def test_validacao_do_mes_dia_a_dia(self):
        v = json.loads((ROOT / "estado/validacao_motores_mes.json").read_text(encoding="utf-8"))
        self.assertEqual(v["mes"], "2026-09"); self.assertGreaterEqual(v["dias_no_periodo"], 20)
        r = v["resumo"]; self.assertEqual(r["integros"] + r["com_lacunas"] + r["nao_executaram"], len(v["motores"]))
        for k, g in v["motores"].items():
            self.assertIn(g["veredito"], ("íntegro", "lacunas", "não executou"))
            self.assertEqual(len(g["dias"]), v["dias_no_periodo"])
        self.assertGreaterEqual(v["motores"]["dou"]["dias_executados"], 15)      # o DOU leu quase todo dia

    def test_pacote_do_desktop_cobre_o_que_falta(self):
        t = (ROOT / "estado/pacote_desktop.md").read_text(encoding="utf-8")
        for x in ("Etapa 1", "Etapa 2", "Etapa 3", "Etapa 4", "Etapa 5", "Opus 5", "coleta_brasil.py", "ingerir_navegador", "Nunca estime datas"):
            self.assertIn(x, t, x)
        j = json.loads((ROOT / "estado/pacote_desktop.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(j["motores_coleta_local"] + j["motores_em_alerta"], 1)
        self.assertIn("pacote_desktop.md", (ROOT / "docs/claude/ARRANQUE-CLAUDE-DESKTOP.md").read_text(encoding="utf-8"))
        html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("ALERTA DIÁRIO DOS MOTORES", html); self.assertIn("Validação dia a dia", html)


if __name__ == "__main__":
    unittest.main()
