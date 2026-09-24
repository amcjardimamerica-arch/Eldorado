"""Achados do dia sem repetição, motores de empresas honestos, varredura retroativa (20/09)."""
import datetime, json, os, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteAchadosDoDia(unittest.TestCase):
    def test_cada_oportunidade_so_na_primeira_data(self):
        a = json.loads((ROOT / "docs/dados/achados_dia.json").read_text(encoding="utf-8"))
        vistos = set()
        for d, v in a["dias"].items():
            for m, l in v["motores"].items():
                for x in l:
                    self.assertNotIn(x["id"], vistos, f"{x['id']} apareceu em mais de um dia")
                    vistos.add(x["id"])
        self.assertEqual(len(vistos), a["total_unicos"])
        self.assertGreaterEqual(a["total_reapresentacoes"], 1)          # houve eco, e ele foi contado à parte
        for eid, r in a["reapresentados"].items():
            self.assertNotIn(eid, vistos)                               # a reapresentação não conta como novo
            self.assertIn(r["primeira_vez"], a["dias"])

    def test_dia_traz_motor_e_link(self):
        a = json.loads((ROOT / "docs/dados/achados_dia.json").read_text(encoding="utf-8"))
        # o dia mais recente com achado, não uma data fixa: com '2026-09-20' o teste apodreceu
        # quando o dia saiu da janela, e sua falha impedia TODOS os motores de rodar
        dia = a["dias"][max(k for k, v in a["dias"].items() if (v or {}).get("total", 0) >= 1)]
        self.assertGreaterEqual(dia["total"], 1)
        for m, l in dia["motores"].items():
            self.assertTrue(m)
            for x in l:
                self.assertTrue(x["titulo"]); self.assertIn("url", x)
        html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for s in ("carregaAchadosDia", "MOTOR_ROTULO", "oportunidade(s) nova(s)", "reapresentada(s)", "Achado do dia"):
            self.assertIn(s, html, s)

    def test_dedup_por_chave_normalizada(self):
        from src.achados_dia import _chave_dedup
        a = _chave_dedup({"titulo": "Continue lendo Instituto Lojas Renner abre edital com até R$ 10 mil", "orgao": "Renner"})
        b = _chave_dedup({"titulo": "Instituto Lojas Renner abre edital com até R$ 10 mil", "orgao": "Renner"})
        self.assertEqual(a, b)


class TesteMotoresDeEmpresasERetroativo(unittest.TestCase):
    def test_motor_de_empresas_nao_chama_empresa_de_edital(self):
        m = json.loads((ROOT / "docs/dados/motores.json").read_text(encoding="utf-8"))
        g = [o for o in m["oficiais"] if o["id"] == "motor-gife"][0]
        self.assertEqual(g["produto"], "empresas"); self.assertGreaterEqual(len(g["empresas"]), 5)
        for e in g["empresas"]:
            self.assertTrue(e["nome"] and e["url"] and e["url"].startswith("http"))
        html = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        self.assertIn("empresa(s) mapeada(s)", html); self.assertIn('o.produto==="empresas"', html)

    def test_retroativo_monta_a_edicao_do_dia_pedido(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        from src.sensores import registro, _paginas
        from src.retroativo import SUPORTAM_DATA, dias_sem_leitura
        dou = [x for x in registro() if x["id"] == "dou"][0]
        u = [x for x in _paginas(dict(dou, _data=datetime.date(2026, 9, 5))) if "leiturajornal" in x][0]
        self.assertIn("data=05-09-2026", u)
        pn = [x for x in registro() if x["id"] == "pncp-api"][0]
        u2 = _paginas(dict(pn, _data=datetime.date(2026, 9, 5)))[0]
        self.assertIn("dataInicial=20260905", u2); self.assertIn("dataFinal=20260905", u2)
        self.assertEqual(SUPORTAM_DATA, {"dou", "pncp-api"})
        faltam = dias_sem_leitura("dou", 2026, 9, datetime.date(2026, 9, 19))
        self.assertIsInstance(faltam, list)
        r = json.loads((ROOT / "estado/varredura_retroativa.json").read_text(encoding="utf-8"))
        self.assertIn("sem_arquivo_por_data", r); self.assertGreaterEqual(len(r["sem_arquivo_por_data"]["sensores"]), 20)


if __name__ == "__main__":
    unittest.main()
