"""10/10 (titular): conselho dos motores — sete prompts com lentes diferentes, cada um executado individualmente sobre
cada motor; relatório por motor; inovações de alcance (fontes irmãs, adaptadores WordPress e Mapas Culturais)."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import conselho_motores as CM
from src import motor_plataformas as MP


def _dados():
    dias = {f"2026-09-{d:02d}": {"cor": "azul", "achados": 0, "falhas": 0, "http": 200, "trecho": None, "url": "https://a.go.gov.br/x"} for d in range(1, 26)}
    congelado = {f"2026-09-{d:02d}": {"cor": "verde", "achados": 1, "falhas": 0, "http": 200, "trecho": "Edital 1/2026", "url": "https://b.go.gov.br/y"} for d in range(1, 26)}
    return {"esq": {"cego": {"nome": "Cego", "diagnostico": {"links_total": 300, "links_candidatos": 0, "paginas_lidas": 3}, "duracao_s": 150, "achados_ultima": 0, "vazias_seguidas": 20},
                    "congelado": {"nome": "Congelado", "diagnostico": {"links_total": 10, "links_candidatos": 2, "paginas_lidas": 2}, "duracao_s": 5, "achados_total": 40, "achados_ultima": 1}},
            "diario": {"cego": dias, "congelado": congelado},
            "itens": [{"id": "1", "origem": "motor congelado", "confirmada": False, "link_oficial": "https://irma.org.br/edital", "uf": "GO"},
                      {"id": "2", "origem": "Piloto - Interceptador", "confirmada": True, "link_oficial": "https://www.cidade.go.gov.br/wp-content/uploads/e.pdf", "uf": "GO"}],
            "certs": {}, "cob": {"por_dominio": {"a.go.gov.br": "cego", "b.go.gov.br": "congelado"}}, "agenda": {"congelado": {"cadencia_dias": 3}},
            "bib": {"k": {"urls": ["https://mapacultural.exemplo.gov.br/oportunidade/1"]}}}


class TestePrompts(unittest.TestCase):
    def test_sete_conselheiros_lentes_e_prompts_diferentes(self):
        self.assertEqual(len(CM.CONSELHO), 7)
        self.assertEqual(len({c["lente"] for c in CM.CONSELHO}), 7)
        self.assertEqual(len({c["prompt"] for c in CM.CONSELHO}), 7)
        for c in CM.CONSELHO:
            self.assertGreater(len(c["prompt"]), 200, c["id"])

    def test_cada_prompt_roda_individualmente_sobre_cada_motor(self):
        D = _dados()
        fv = CM.a_falso_verde(D)
        self.assertIn("CEGO", [f[0] for f in fv["cego"]["falhas"]])
        self.assertIn("ESTRANGULADO", [f[0] for f in fv["cego"]["falhas"]])
        self.assertIn("CONGELADO", [f[0] for f in fv["congelado"]["falhas"]])
        fu = CM.a_funil(D); self.assertIn("RUÍDO", [f[0] for f in fu["congelado"]["falhas"]])
        rd = CM.a_redundancia(D); self.assertIn("CUSTO SEM RETORNO", [f[0] for f in rd["cego"]["falhas"]])
        co = CM.a_cobertura(D); self.assertEqual(co["fora_dos_motores_pct"], 50.0)
        ri = CM.a_ritmo(D); self.assertEqual(ri["congelado"]["cadencia_recomendada"], 1, "publica todo dia: ler diariamente")
        fi = CM.a_fontes_irmas(D); self.assertIn("irma.org.br", [f["dominio"] for f in fi["fontes"]])
        self.assertNotIn("a.go.gov.br", [f["dominio"] for f in fi["fontes"]], "domínio já vigiado não é fonte irmã")
        pl = CM.a_plataformas(D); self.assertGreaterEqual(pl["plataformas"]["WordPress"]["orgaos"], 1)
        self.assertEqual(len(pl["inovacoes"]), 4)

    def test_relatorio_motor_a_motor(self):
        out = CM.run(gravar=False)
        md = CM.relatorio_md(out)
        self.assertIn("## Os sete prompts", md); self.assertIn("## Motor a motor", md)
        self.assertEqual(out["resumo"]["motores"], len(out["por_motor"]))


class TesteAdaptadores(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.o = (MP.PLATAFORMAS, MP.CURSOR); MP.PLATAFORMAS = T / "p.json"; MP.CURSOR = T / "c.json"
        MP.PLATAFORMAS.write_text(json.dumps({"WordPress": ["prefeitura.go.gov.br"], "Mapas Culturais": ["mapa.cultura.gov.br"]}))

    def tearDown(self):
        MP.PLATAFORMAS, MP.CURSOR = self.o; self.tmp.cleanup()

    def test_wordpress(self):
        posts = [{"link": "https://prefeitura.go.gov.br/edital-cultura-2026", "title": {"rendered": "Edital de chamamento público para organizações da sociedade civil de cultura"},
                  "excerpt": {"rendered": "<p>Inscrições abertas para OSC e associações culturais até 30/11/2026, com recursos de fomento.</p>"}, "date": "2026-10-01"},
                 {"link": "https://prefeitura.go.gov.br/obra", "title": {"rendered": "Inauguração de praça"}, "excerpt": {"rendered": "obra"}}]
        r = MP.ler_wordpress({"id": "plataforma-wordpress", "nome": "WP", "tipo": "api", "max_paginas": 5}, date(2026, 10, 10),
                             baixar=lambda u: (json.dumps(posts).encode(), "application/json"))
        self.assertEqual(r["diagnostico"]["respostas_json"], 3)
        self.assertTrue(all("wp-json/wp/v2/posts" in f.get("url", "wp-json/wp/v2/posts") for f in r["falhas"]))
        self.assertLessEqual(len(r["achados"]), 1); self.assertTrue(r["diagnostico"]["links_candidatos"] >= 3)

    def test_mapas_culturais(self):
        ops = [{"id": 7, "name": "Prêmio de fomento a pontos de cultura e organizações da sociedade civil", "shortDescription": "Seleção pública para OSC culturais",
                "registrationTo": {"date": "2026-11-20 23:59:00.000000"}, "singleUrl": "https://mapa.cultura.gov.br/oportunidade/7/"}]
        r = MP.ler_mapas({"id": "plataforma-mapas-culturais", "nome": "Mapas", "tipo": "api", "max_paginas": 5}, date(2026, 10, 10),
                         baixar=lambda u: (json.dumps(ops).encode(), "application/json"))
        self.assertEqual(r["diagnostico"]["oportunidades"], 1)
        if r["achados"]:
            self.assertEqual(r["achados"][0]["prazo_texto"], "2026-11-20")

    def test_esquadra_e_agenda(self):
        cfg = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        ids = {s["id"] for s in cfg["sensores_especiais"]}
        ag = json.loads((ROOT / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        for n in ("outras-oportunidades", "plataforma-wordpress", "plataforma-mapas-culturais"):
            self.assertIn(n, ids)
        for n in ("outras-oportunidades-1", "plataforma-wordpress", "plataforma-mapas-culturais"):
            self.assertIn(n, ag)
        s = (ROOT / "src/sensores.py").read_text(encoding="utf-8")
        self.assertIn('urls_dinamicas") == "outras_oportunidades"', s); self.assertIn("ler_wordpress", s); self.assertIn("ler_mapas", s)
        self.assertIn("python -m src.conselho_motores", (ROOT / ".github/workflows/cartorio.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
