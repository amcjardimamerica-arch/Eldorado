"""Ranking ampliado e paginado, ciclo contínuo e avião errante (22/09)."""
import json, pathlib, unittest
from src.ranking_apoiadores import montar, POR_PAGINA
ROOT = pathlib.Path(__file__).resolve().parents[1]


class TesteRanking(unittest.TestCase):
    def test_lista_unica_ordenada_por_pontuacao(self):
        r = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))
        E = r["empresas"]
        self.assertGreater(r["total"], 100)                                   # ampliado além das 100
        self.assertTrue(all(E[i]["pontos"] >= E[i + 1]["pontos"] for i in range(len(E) - 1)))
        self.assertEqual([e["posicao"] for e in E[:3]], [1, 2, 3])
        self.assertGreaterEqual(len(r["por_origem"]), 2)

    def test_paginas_de_cem(self):
        r = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))
        self.assertEqual(r["por_pagina"], 100); self.assertEqual(POR_PAGINA, 100)
        pg = r["paginas"]
        self.assertEqual(pg[0], {"de": 1, "ate": 100}); self.assertEqual(pg[-1]["ate"], r["total"])
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("rank-apoiadores", "window.paginaApoiadores", "window.fichaApoiador", "rk-pag", "rk-item"):
            self.assertIn(x, h, x)

    def test_dados_cadastrais(self):
        r = json.loads((ROOT / "docs/dados/ranking_apoiadores.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(r["com_cnpj"], 50); self.assertGreaterEqual(r["com_cnae"], 50)
        self.assertGreaterEqual(r["com_qsa"], 50); self.assertGreaterEqual(r["com_contato"], 50)
        com = [e for e in r["empresas"] if e["cadastro"].get("qsa")][0]["cadastro"]
        for c in ("cnpj", "cnae_principal", "qsa", "telefone", "razao_social"):
            self.assertTrue(com.get(c), c)
        self.assertTrue(all(isinstance(s.get("nome"), str) for s in com["qsa"]))
        self.assertTrue(all("a_completar" in e["cadastro"] for e in r["empresas"]))   # o que falta é declarado
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("Quadro societário (QSA)", "CNAE principal", "CNAEs secundários", "Natureza jurídica"):
            self.assertIn(x, h, x)


class TesteCicloContinuoEAviao(unittest.TestCase):
    def test_encadeamento_sem_esperar_horario(self):
        w = (ROOT / ".github/workflows/sindico.yml").read_text(encoding="utf-8")
        self.assertIn("Pousar 3 segundos e decolar de novo", w)
        self.assertIn("estado/piloto_pausado", w)                              # trava manual
        self.assertIn("teto do dia atingido", w)
        self.assertIn("in_progress", w)                                      # não empilha voo
        self.assertIn('cron: "0 */2 * * *"', w)                                # rede de segurança
        c = json.loads((ROOT / "config/sindico.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(c["voos_por_dia"], 10); self.assertLessEqual(c["orcamento"]["teto_minutos"], 40)

    def test_piloto_escolhe_o_rumo_lendo_a_biblioteca(self):
        src = (ROOT / "src/sindico.py").read_text(encoding="utf-8")
        self.assertIn("def escolher_rumo", src); self.assertIn("def _contar_voo", src)
        self.assertIn("BIBLIOTECA HOJE", src); self.assertIn("ÂNGULOS QUE VIERAM SECOS", src)
        self.assertIn("Pense em quem PAGA", src)
        m = json.loads((ROOT / "config/motor_sindico.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(m["angulos_de_ataque"]), 12)

    def test_aviao_passeia_sobre_o_trabalho(self):
        h = (ROOT / "docs/dashboard.html").read_text(encoding="utf-8")
        for x in ("pil-errante", "ONDE_POUSAR", "pousarAviaoErrante", "pil-balao", "pil-voa", "@keyframes pil-travessia"):
            self.assertIn(x, h, x)
        self.assertIn('cacar_oportunidade:["#rank-apoiadores"', h)             # caçando → sobrevoa o ranking
        self.assertIn('afiar_motor:["#pil-posto-bussola"', h)                  # afiando → sobrevoa o posto da Bússola
        self.assertNotIn(".mt-item.oficial", h.split("ONDE_POUSAR")[1][:300])   # nunca sobre a lista de motores

    def test_painel_protegido_do_job_de_dados(self):
        w = (ROOT / ".github/workflows/monitoramento-diario.yml").read_text(encoding="utf-8")
        self.assertIn("PROTEÇÃO DO PAINEL", w)
        self.assertIn("docs/dashboard.html", w.split("PROTEÇÃO DO PAINEL")[1][:400])
