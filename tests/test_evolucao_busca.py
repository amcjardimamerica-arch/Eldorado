"""Evolução da busca (20/09): empresas→rotas, descoberta×recorrência, léxico que aprende, acervo compacto."""
import datetime, json, os, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteEmpresasRotas(unittest.TestCase):
    def test_toda_empresa_mapeada_vira_rotas(self):
        d = json.loads((ROOT / "config/rotas_empresas.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(d["total_empresas"], 50)
        for e in d["empresas"][:20]:
            tipos = {r["tipo"] for r in e["rotas"]}
            self.assertTrue(tipos & {"site_institucional", "descobrir_site"}, e["empresa"])   # sempre há um caminho para o site
            self.assertIn("vetor_terceiro_setor", tipos)
            self.assertTrue(all(r.get("prioridade") for r in e["rotas"]))
        from src.empresas_rotas import rotas_para_sensor, _slug
        self.assertGreaterEqual(len(rotas_para_sensor(24)), 10)
        self.assertTrue(_slug("GRUPO CASAS BAHIA S.A.").startswith("grupocasasbahia"))

    def test_motor_de_editais_de_empresas_le_as_rotas(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        from src.sensores import registro, _paginas
        s = [x for x in registro() if x["id"] == "plat-empresas-editais-incentivados"][0]
        self.assertGreaterEqual(len(_paginas(s)), 15)


class TesteDescobertaERecorrencia(unittest.TestCase):
    def test_finalidade_declarada_para_todo_motor(self):
        f = json.loads((ROOT / "config/finalidade_motores.json").read_text(encoding="utf-8"))
        from src.sensores import registro
        for s in [x for x in registro() if not x.get("fontes_260") and x["id"] != "recorrencia"]:
            self.assertIn(f["motores"][s["id"]]["finalidade"], ("descoberta", "insumo"), s["id"])
        self.assertEqual(f["motores"]["recorrencia"]["finalidade"], "recorrencia")
        self.assertEqual(f["motores"]["alego-pl"]["finalidade"], "insumo")

    def test_recorrencia_uma_rota_por_validada_com_cadencia_por_estado(self):
        from src.finalidade_motores import _cadencia_recorrencia
        hoje = datetime.date(2026, 9, 20)
        self.assertEqual(_cadencia_recorrencia({"fim": "2026-10-30"}, hoje)[0], 2)          # aberta
        self.assertEqual(_cadencia_recorrencia({"fim": "2026-03-01"}, hoje)[0], 30)         # encerrada, longe da época
        self.assertEqual(_cadencia_recorrencia({"fim": "2025-09-25"}, hoje)[0], 1)          # época de reabertura
        self.assertEqual(_cadencia_recorrencia({}, hoje)[0], 7)
        r = json.loads((ROOT / "estado/rotas_recorrencia.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(r["total"], 50)
        self.assertTrue(all(x["url"] and x["cadencia_dias"] and x["proxima_leitura"] for x in r["rotas"]))

    def test_recorrencia_e_sensor_regular_e_reprograma(self):
        os.environ["GITHUB_ACTIONS"] = "true"
        from src.sensores import registro, escala_do_dia, reprogramar_recorrencia
        rec = [s for s in registro() if s["id"] == "recorrencia"]
        self.assertTrue(rec); self.assertLessEqual(len(rec[0]["urls"]), 40)
        e = escala_do_dia(datetime.date.today())
        self.assertIn("recorrencia", {s["id"] for s in e["saem"]})
        self.assertTrue(callable(reprogramar_recorrencia))

    def test_espalhamento_alimenta_a_curadoria(self):
        f = json.loads((ROOT / "config/finalidade_motores.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(f["espalhamento"]["total_novos"], 5)
        cur = json.loads((ROOT / "config/curadoria_fontes.json").read_text(encoding="utf-8"))
        self.assertTrue(any(str(x.get("id", "")).startswith("espalhado-") for x in cur["fontes_novas"]))


class TesteLexicoQueAprende(unittest.TestCase):
    def test_promocao_so_sem_falso_positivo(self):
        d = json.loads((ROOT / "config/lexico_aprendido.json").read_text(encoding="utf-8"))
        for t, v in d["positivos"].items():
            self.assertEqual(v["em_reprovados"], 0, t); self.assertGreaterEqual(v["em_aprovados"], 3); self.assertTrue(v["ids"])
        for t, v in d["vetos"].items():
            self.assertEqual(v["em_aprovados"], 0, t); self.assertGreaterEqual(v["em_reprovados"], 5)
        for ruido in ("continue lendo", "continue", "lendo", "selecionadas"):
            self.assertNotIn(ruido, d["positivos"]); self.assertNotIn(ruido, d["vetos"])
        self.assertLessEqual(len(d["positivos"]), 80); self.assertLessEqual(len(d["vetos"]), 80)

    def test_lexico_aprendido_entra_na_camada_1(self):
        from src.sensores import registro, lexico_camada1
        from src.aprendizado_lexico import termos_aprendidos
        pos, veto = termos_aprendidos()
        s = [x for x in registro() if x["id"] == "plat-ovg"][0]
        t, v = lexico_camada1(s)
        self.assertTrue(set(pos[:10]) <= set(t)); self.assertTrue(set(veto[:10]) <= set(v))
        self.assertGreaterEqual(len(t), 80)


class TesteAcervoCompacto(unittest.TestCase):
    def test_acervo_fts5_zstd(self):
        from src.acervo_compacto import buscar, ficha, ACERVO
        self.assertTrue(ACERVO.exists())
        m = json.loads((ROOT / "estado/acervo_compacto.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(m["docs"], 10000); self.assertLess(m["bytes_acervo"], 40 * 1024 * 1024)
        self.assertTrue(m["dicionario_zstd"]); self.assertGreaterEqual(m["compressao"], 1.2)
        r = buscar("termo de fomento cultura", 5); self.assertTrue(r)
        f = ficha(r[0]["id"]); self.assertTrue(f and f["ficha"])
        self.assertTrue(buscar("chamamento público", 3, uf="GO") is not None)
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8"); self.assertIn("acervo.sqlite", gi)   # regenerado no CI, não versionado
        req = (ROOT / "requirements.txt").read_text(encoding="utf-8"); self.assertIn("zstandard", req); self.assertIn("rapidfuzz", req)


if __name__ == "__main__":
    unittest.main()
