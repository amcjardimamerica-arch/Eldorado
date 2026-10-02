"""02/10/2026 (titular): motor 08 v2 — 25 maiores prefeituras de Goiás (diário AGM, WordPress, Querido Diário, portais)."""
import importlib.util, json, os, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from src import prefeituras_25_go as P
except Exception:                                   # autoteste (--testar) fora do repositório
    _spec = importlib.util.spec_from_file_location("prefeituras_25_go", os.environ["PREF25_MODULO"])
    P = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(P)

H = date(2026, 10, 2)
LEX = P.CONFIG_PADRAO["lexico"]


def c(t, r="", pub=H):
    return P.classificar(t, r, pub, H, LEX)


class TesteClassificador(unittest.TestCase):
    def test_oportunidades_reais_do_inventario(self):
        casos = [
            ("Prefeitura de Goiânia abre chamamento público para seleção de instituições de longa permanência e Casa-Lar para idosos", "", "OPORTUNIDADE_OSC"),
            ("CHAMADA PUBLICA", "objeto é a Seleção de Organização da Sociedade Civil (OSC) para celebrar Termo de Colaboração", "OPORTUNIDADE_OSC"),
            ("CHAMAMENTO PÚBLICO Nº 06/2026 – PROCESSO Nº 23713/2026", "", "OPORTUNIDADE_OSC"),
            ("Edital de Chamamento Público - Termo de Fomento Nº 001/2026", "", "OPORTUNIDADE_OSC"),
            ("SEMASC abre Chamamento Público para seleção de projetos voltados à proteção de crianças e adolescentes", "", "CMDCA_FIA"),
            ("Prefeitura de Anápolis lança editais da lei Aldir Blanc para o setor cultural", "", "OPORTUNIDADE_CULTURA"),
            ("EDITAL DE CHAMAMENTO PÚBLICO Nº 001-CMDCA-2026", "", "CMDCA_FIA"),
            ("Prefeito Mabel lança credenciamento para entidades socioassistenciais e destaca parceria com o terceiro setor", "", "OPORTUNIDADE_OSC"),
        ]
        for t, r, cat in casos:
            x = c(t, r)
            self.assertEqual(x["veredito"], "OPORTUNIDADE", t); self.assertEqual(x["categoria"], cat, t)

    def test_parceria_direta(self):
        for t, r in (("TERMO DE FOMENTO N° 007/2026", "O presente Termo de Fomento tem por objeto"),
                     ("EXTRATO – JUSTIFICATIVA DE INEXIGIBILIDADE DE CHAMAMENTO PÚBLICO", "organização da sociedade civil"),
                     ("EXTRATO DE CONVENIO", "Termo de Convênio de subvenção social com a entidade filantrópica")):
            x = c(t, r)
            self.assertEqual(x["categoria"], "PARCERIA_DIRETA", t); self.assertEqual(x["veredito"], "ACOMPANHAR", t)

    def test_ruido_tipico_vira_veto(self):
        for t, r in (("Chamada Pública Escolar 2027: Secretaria de Educação divulga edital para ingresso na Rede Municipal", ""),
                     ("Prefeitura de Aparecida reforça o chamamento para quem ainda não se vacinou contra a febre amarela", ""),
                     ("CHAMAMENTO PÚBLICO Nº 05/2026 – FESTIVAL GASTRONÔMICO", ""),
                     ("Prefeitura de Goiânia publica Chamamento Público para seleção de influenciadores digitais", ""),
                     ("Aparecida conquista 1º lugar em Prêmio da Qualidade da Informação Contábil do Tesouro Nacional", ""),
                     ("EXTRATO DE ORDEM DE FORNECIMENTO N° 51285/2026", "CONTRATAÇÃO DE EMPRESA PARA FORNECIMENTO DE COMBUSTÍVEL"),
                     ("EDITAL DE INTIMAÇÃO FISCAL Nº 00043, DE 01 DE OUTUBRO DE 2026", ""),
                     ("EDITAL DE CONVOCAÇÃO N.° 023/2026 PARA APRESENTAÇÃO DE DOCUMENTOS E EXAME DE APTIDÃO FÍSICA", "")):
            self.assertEqual(c(t, r)["veredito"], "RUIDO", t)

    def test_resultado_e_ato_do_edital(self):
        self.assertEqual(c("RESULTADO PRELIMINAR – CHAMAMENTO PÚBLICO 01/2026")["categoria"], "RESULTADO")
        self.assertEqual(c("Prefeitura de Anápolis prorroga inscrições dos editais da Política Nacional Aldir Blanc até 26 de julho")["categoria"], "ATO_DO_EDITAL")
        self.assertEqual(c("Chamada Pública nº 01/2026 do programa de aquisição de alimentos (PAA)")["categoria"], "AGRICULTURA_FAMILIAR")

    def test_prazo_e_aberta(self):
        x = c("Edital de Chamamento Público nº 01/2026 – projetos culturais PNAB", "inscrições até 20/10/2026", date(2026, 9, 20))
        self.assertTrue(x["aberta"]); self.assertEqual(x["prazo"], "2026-10-20")
        self.assertFalse(c("Edital de Chamamento Público nº 01/2024 – PNAB", "inscrições até 20/07/2024", date(2024, 6, 25))["aberta"])

    def test_concordancia_com_o_inventario(self):
        """A régua automática concorda com a curadoria humana do inventário em pelo menos 70% das oportunidades e nunca
        manda para RUÍDO mais de 1/4 delas."""
        ops = [r for r in P.INVENTARIO_BASE if r[3] in ("OPORTUNIDADE_OSC", "OPORTUNIDADE_CULTURA", "CMDCA_FIA")]
        ver = [c(r[4])["veredito"] for r in ops]
        self.assertGreaterEqual(sum(v == "OPORTUNIDADE" for v in ver) / len(ver), 0.70)
        self.assertLessEqual(sum(v == "RUIDO" for v in ver) / len(ver), 0.25)


class TesteInventarioECatalogo(unittest.TestCase):
    def test_inventario(self):
        self.assertEqual(len(P.INVENTARIO_BASE), 357)
        nomes = {m["municipio"] for m in P.CONFIG_PADRAO["municipios"]}
        self.assertEqual(len(nomes), 25); self.assertEqual({r[0] for r in P.INVENTARIO_BASE}, nomes)
        self.assertTrue(all(r[5].startswith("https://") for r in P.INVENTARIO_BASE))

    def test_catalogo_rotas(self):
        ms = {m["municipio"]: m for m in P.CONFIG_PADRAO["municipios"]}
        self.assertEqual(sorted(k for k, m in ms.items() if m.get("agm")),
                         sorted(["Águas Lindas de Goiás", "Cristalina", "Formosa", "Inhumas", "Senador Canedo", "Trindade"]))
        self.assertEqual(P.CONFIG_PADRAO["querido_diario"]["api"], "https://api.queridodiario.org.br")
        for m in ms.values():
            self.assertTrue(P._rotas(m), m["municipio"])
        self.assertTrue(all(m.get("ibge") is None or len(m["ibge"]) == 7 for m in ms.values()))

    def test_janelas_previsiveis(self):
        j = P.janelas_previsiveis()
        self.assertIn(4, j["Itaberaí"]["CMDCA_FIA"])
        self.assertTrue(j["Águas Lindas de Goiás"]["OPORTUNIDADE_CULTURA"])


AGM_HTML = """<p>33 matérias</p><ul>
<li class="materia-card"><h2>TERMO DE FOMENTO N° 007/2026</h2><span>Prefeitura Municipal de Inhumas</span>
<p>O presente Termo de Fomento tem por objeto a execução do projeto da associação</p><span>Circulação 17/07/2026 Edição 3640</span>
<a href="https://www.diariomunicipal.com.br/agm/materia/824F71A0">Abrir matéria</a></li>
<li class="materia-card"><h2>CHAMADA PUBLICA</h2><p>Seleção de Organização da Sociedade Civil (OSC) para celebrar Termo de Colaboração, inscrições até 30/10/2026</p>
<span>Circulação 25/09/2026</span><a href="/agm/materia/D8B273E6">Abrir matéria</a></li></ul>"""


class TesteLeitores(unittest.TestCase):
    def test_parse_agm(self):
        tot, itens = P.parse_agm(AGM_HTML, "Inhumas")
        self.assertEqual(tot, 33); self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0]["data"], "2026-07-17"); self.assertTrue(itens[1]["url"].endswith("/agm/materia/D8B273E6"))
        self.assertEqual(c(itens[1]["titulo"], itens[1]["resumo"], date(2026, 9, 25))["veredito"], "OPORTUNIDADE")

    def test_wp_e_volume(self):
        cfg = P.CONFIG_PADRAO; m = {"municipio": "Planaltina", "site": "https://www.planaltina.go.gov.br", "wp_api": True}
        post = [{"id": 1, "date": "2026-09-08T10:00:00", "link": "https://www.planaltina.go.gov.br/chamamento-publico-no-06-2026/",
                 "title": {"rendered": "CHAMAMENTO PÚBLICO Nº 06/2026"}, "excerpt": {"rendered": "<p>seleção de OSC</p>"}}]
        with mock.patch.object(P, "_get", return_value=(200, json.dumps(post), {"x-wp-total": "1"})), mock.patch.object(P.time, "sleep"):
            st, itens, vol = P.ler_wp(m, cfg, "2023-10-02", 1e18, ["chamamento"], 1)
        self.assertEqual(st, "lida"); self.assertEqual(len(itens), 1); self.assertEqual(vol["chamamento/posts"], 1)
        with mock.patch.object(P, "_get", return_value=(401, "", {})):
            self.assertTrue(P.ler_wp(m, cfg, "2023-10-02", 1e18, ["x"], 1)[0].startswith("fechada"))

    def test_catalao_avisos(self):
        html = ('<a href="/avisos/edital-de-chamamento-publico/termo-de-fomento-001-2026">01/06/2026 | EDITAL DE CHAMAMENTO PÚBLICO Termo de Fomento Nº 001/2026</a>'
                '<a href="/avisos/x/velho">01/06/2022 | antigo</a>')
        m = {"municipio": "Catalão", "site": "https://www.catalao.go.gov.br", "portal": {"modo": "avisos_paginado", "secoes": ["avisos/edital-de-chamamento-publico"], "max_paginas": 2}}
        with mock.patch.object(P, "_get", return_value=(200, html, {})), mock.patch.object(P.time, "sleep"):
            st, itens, _ = P.ler_portal(m, P.CONFIG_PADRAO, "2023-10-02", 1e18)
        self.assertEqual(st, "lida"); self.assertEqual(len(itens), 1); self.assertEqual(itens[0]["data"], "2026-06-01")

    def test_requer_navegador_nao_finge_leitura(self):
        m = {"municipio": "Mineiros", "site": "https://www.mineiros.go.gov.br", "portal": {"modo": "requer_navegador"}}
        st, itens, _ = P.ler_portal(m, P.CONFIG_PADRAO, "2023-10-02", 1e18)
        self.assertTrue(st.startswith("requer navegador")); self.assertEqual(itens, [])

    def test_qd_instavel_vira_falha_explicita(self):
        m = {"municipio": "Goiânia", "ibge": "5208707", "qd": "5208707"}
        with mock.patch.object(P, "_get", return_value=(0, "TimeoutError", {})):
            self.assertTrue(P.ler_qd(m, P.CONFIG_PADRAO, "2023-10-02", 1e18, ["x"])[0].startswith("falhou"))


class TesteHonestidade(unittest.TestCase):
    def test_github_sem_brasil_nao_tenta_sites_e_nao_marca_lida(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(P, "ESTADO", Path(d) / "e.json"), mock.patch.object(P, "PAINEL", Path(d) / "p.json"), \
             mock.patch.object(P, "CFG", Path(d) / "nao-existe.json"), mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "1", "PREFEITURAS_SEM_LIVROS": "1"}), \
             mock.patch.object(P, "_get", return_value=(0, "TimeoutError", {})) as g, mock.patch.object(P.time, "sleep"):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            r = P.ler_motor(hoje=H, orcamento=60)
            self.assertFalse(any(".go.gov.br" in str(a.args[0]) for a in g.call_args_list))
            st = r["diagnostico"]["cidades_por_status"]
            self.assertNotIn("lida", st)
            self.assertGreaterEqual(st.get("aguardando coleta local (Brasil)", 0), 15)
            pn = json.loads((Path(d) / "p.json").read_text(encoding="utf-8"))
            self.assertEqual(pn["totais"]["inventario_base"], 357); self.assertEqual(len(pn["cidades"]), 25)
            e = json.loads((Path(d) / "e.json").read_text(encoding="utf-8"))
            self.assertTrue(e["pendentes_livros"])          # o inventário-base fica pendente para os livros (não se perde)


class TesteInstalacao(unittest.TestCase):
    def test_instalar_e_idempotente(self):
        with tempfile.TemporaryDirectory() as d:
            R = Path(d); (R / "src").mkdir(); (R / "config").mkdir()
            (R / "src/sensores.py").write_text('def ler(sensor, limites=None, pausa=None, data=None):\n    if sensor.get("id") == "dou":\n        return 1\n', encoding="utf-8")
            (R / "config/coletores_api.json").write_text('{"bases": [\n   "https://queridodiario.ok.org.br/api",\n   "https://api.queridodiario.ok.org.br"\n]}', encoding="utf-8")
            P.instalar(R); P.instalar(R)
            t = (R / "src/sensores.py").read_text(encoding="utf-8")
            self.assertEqual(t.count("prefeituras_25_go"), 1)
            self.assertIn("api.queridodiario.org.br", (R / "config/coletores_api.json").read_text(encoding="utf-8"))
            json.loads((R / "config/coletores_api.json").read_text(encoding="utf-8"))
            self.assertTrue((R / "tests/test_motor_prefeituras_25_go.py").exists())
            self.assertEqual(len(json.loads((R / "config/prefeituras_25_go.json").read_text(encoding="utf-8"))["municipios"]), 25)


if __name__ == "__main__":
    unittest.main()
