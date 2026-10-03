"""02/10 (titular): motor Oportunidade Estaduais Governamentais de Goiás — órgãos do Executivo de Goiás, um por vez, em camadas."""
import json, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import estaduais_go as E

LEX = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))["lexico"]
H = date(2026, 10, 2)


class TesteClassificador(unittest.TestCase):
    def c(self, t, r="", pub=H):
        return E.classificar(t, r, pub, H, LEX)

    def test_acertos_do_historico(self):
        x = self.c("Secult Goiás lança edital para levar produção artística goiana ao Rio", "inscrições até 29/10 para agentes culturais e coletivos")
        self.assertEqual(x["veredito"], "OPORTUNIDADE"); self.assertTrue(x["aberta"]); self.assertEqual(x["prazo"], "2026-10-29")
        self.assertEqual(self.c("Edital de chamamento público 001/2026 - Socioeducativo", "seleção de organizações da sociedade civil")["veredito"], "OPORTUNIDADE")

    def test_descartes_do_historico_viraram_veto(self):
        for t in ("Chamada Pública Merenda Escolar Goiás 2026", "Capacitações sobre gênero", "Edital de chamamento de ex-empregados celetistas",
                  "Chamada FAPEG para bolsas de pesquisa e pesquisadores"):
            self.assertEqual(self.c(t, "entidades")["veredito"], "RUIDO", t)

    def test_falsos_positivos_da_primeira_leitura(self):
        """02/10: títulos reais que a primeira leitura classificou errado — viraram veto ou ACOMPANHAR."""
        for t in ("Vem aí a 7 edição do Prêmio Goiás + Transparente", "Juceg ganha Troféu Diamante no 1º Prêmio de Ouvidoria Pública",
                  "Governo de Goiás é destaque nacional no 5º Prêmio Conexão Inova com 12 iniciativas premiadas",
                  "CHAMADA PÚBLICA FAPEG/Nº 27/2025 -Seleção de Bolsistas para Projetos", "Governo de Goiás publica edital de chamamento público para nova gestão do Hugo",
                  "Governo de Goiás oferece consultoria gratuita para novos negócios liderados por mulheres",
                  "SIC anuncia Edital de Chamamento Público para o Mercadão Goiano de Águas Lindas de Goiás",
                  "Inscrições para a 2ª edição do Prêmio Professor Transformador podem ser feitas até o dia 1° de dezembro"):
            self.assertNotEqual(self.c(t, "entidades")["veredito"], "OPORTUNIDADE", t)
        self.assertEqual(self.c("Fapeg divulga resultado final de edital com bolsas para projetos")["veredito"], "ACOMPANHAR")
        for t in ("Governo de Goiás lança editais da Pnab para Pontos e Pontões de Cultura",
                  "Edital de Chamamento Público de Instituições sem Fins Lucrativos para a Execução do Programa"):
            self.assertEqual(self.c(t)["veredito"], "OPORTUNIDADE", t)

    def test_veto_cede_a_chamamento_de_osc(self):
        x = self.c("Chamamento público para OSC executar curso de capacitação", "termo de fomento com organizações da sociedade civil")
        self.assertEqual(x["veredito"], "OPORTUNIDADE")

    def test_resultado_e_repasse_acompanhar(self):
        self.assertEqual(self.c("Resultado do edital de chamamento para entidades", "")["veredito"], "ACOMPANHAR")
        self.assertEqual(self.c("Goiás Social aumenta repasse do Auxílio Nutricional às entidades filantrópicas")["veredito"], "ACOMPANHAR")

    def test_do_passado_nao_e_aberta(self):
        x = self.c("Secult abre inscrições do edital para projetos culturais", "inscrições até 10/03/2023", pub=date(2023, 2, 1))
        self.assertEqual(x["veredito"], "OPORTUNIDADE"); self.assertFalse(x["aberta"])


class TesteCamadas(unittest.TestCase):
    def test_um_orgao_passa_pelas_quatro_camadas(self):
        posts = [{"id": 1, "date": "2026-09-30T10:00:00", "link": "https://goias.gov.br/x/edital-1/",
                  "title": {"rendered": "Secretaria abre chamamento público para OSC"}, "excerpt": {"rendered": "inscrições até 30/10 para organizações da sociedade civil"}},
                 {"id": 2, "date": "2023-05-02T10:00:00", "link": "https://goias.gov.br/x/edital-2023/",
                  "title": {"rendered": "Secretaria abre chamamento público para OSC"}, "excerpt": {"rendered": "inscrições até 30/05/2023 para entidades"}}]

        def falso(url, timeout=25):
            if "/wp-json/wp/v2/posts" in url:
                return 200, json.dumps(posts), {"X-WP-Total": "2"}
            if "/wp-json/wp/v2/pages" in url:
                return 200, "[]", {}
            return 200, "<html><a href='/editais/'>Editais</a></html>", {}
        with tempfile.TemporaryDirectory() as tmp:
            cfg = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))
            cfg["orgaos_semente"] = [{"id": "x", "nome": "Secretaria X", "tipo": "secretaria", "site": "https://goias.gov.br/x"}]
            cfg["pausa_entre_requisicoes"] = 0; cfg["descoberta"]["paginas_indice"] = []
            p = Path(tmp) / "cfg.json"; p.write_text(json.dumps(cfg), encoding="utf-8")
            with mock.patch.object(E, "CFG", p), mock.patch.object(E, "ESTADO", Path(tmp) / "e.json"), mock.patch.object(E, "PAINEL", Path(tmp) / "p.json"), \
                 mock.patch.object(E, "_get", falso), mock.patch("src.livros_regra.registrar_achados", return_value={"livros_novos": 1}) as reg:
                r = E.ler_motor(hoje=H, orcamento=60)
                est = json.loads((Path(tmp) / "e.json").read_text(encoding="utf-8"))
        o = est["orgaos"]["x"]
        self.assertEqual(o["camada"], 4); self.assertTrue(o["wordpress"]); self.assertIn("notícias do site (API do portal)", o["onde_publica"])
        self.assertEqual(o["publicacoes_por_ano"], {"2023": 1, "2026": 1}); self.assertEqual(o["oportunidades_abertas"], 1); self.assertEqual(o["oportunidades_historicas"], 1)
        self.assertEqual(len(r["achados"]), 1); self.assertEqual(r["achados"][0]["fim"], "2026-10-30")
        self.assertEqual(len(reg.call_args[0][0]), 2, "a do passado e a aberta vão para os livros")


class TesteIntegracao(unittest.TestCase):
    def test_sensor_novo_e_antigos_agregados(self):
        from src.sensores import registro
        ids = [s["id"] for s in registro()]
        self.assertIn("plat-estaduais-go-gov", ids)
        for k in ("plat-secult-go", "plat-fapeg", "plat-fundos-estaduais-go", "plat-goias-social", "plat-ovg"):
            self.assertNotIn(k, ids)
        self.assertIn('if sensor.get("id") == "plat-estaduais-go-gov"', (ROOT / "src/sensores.py").read_text(encoding="utf-8"))

    def test_agregados_saem_do_painel(self):
        """02/10 (titular): os motores 09, 14, 15, 16 e 17 foram agregados — não aparecem nem contam na numeração."""
        src = (ROOT / "src/motores.py").read_text(encoding="utf-8")
        self.assertIn('if p.get("ativa") in (False, "False", "false"):', src)
        inv = json.loads((ROOT / "config/investigacao.json").read_text(encoding="utf-8"))["fontes"]
        for k in ("secult-go", "fapeg", "fundos-estaduais-go", "goias-social", "ovg"):
            f = next(x for x in inv if x["id"] == k)
            self.assertFalse(f["ativa"]); self.assertEqual(f["agregado_a"], "estaduais-go-gov")

    def test_so_executivo(self):
        cfg = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))
        import re
        for o in cfg["orgaos_semente"]:
            self.assertFalse(re.search(cfg["descoberta"]["fora_do_executivo"], o["nome"], re.I), o["nome"])


if __name__ == "__main__":
    unittest.main()


class TesteMotor14(unittest.TestCase):
    """Teste do motor 14 de 03/10/2026."""

    def test_osc_no_singular_e_oportunidade(self):
        t = "Edital de chamamento público ' 001/2026 ' Socioeducativo"
        r = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL PARA CELEBRAÇÃO DE TERMO DE "
             "COLABORAÇÃO DESTINADO À EXECUÇÃO DE AÇÕES COMPLEMENTARES NO ÂMBITO DO ATENDIMENTO SOCIOEDUCATIVO")
        x = E.classificar(t, r, date(2026, 9, 14), date(2026, 10, 3), LEX)
        self.assertEqual((x["veredito"], x["aberta"]), ("OPORTUNIDADE", True))

    def test_indice_e_enderecos_novos(self):
        cfg = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))
        self.assertIn("https://goias.gov.br/administracao-direta/", cfg["descoberta"]["paginas_indice"])
        self.assertEqual(cfg["slugs_alternativos"]["secti"][0], "inovacao")
        self.assertEqual(cfg["slugs_alternativos"]["seds"][0], "social")

    def _cenario(self, est0, falso, cfg_extra=None):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))
            cfg["orgaos_semente"] = []; cfg["pausa_entre_requisicoes"] = 0; cfg["descoberta"]["paginas_indice"] = []
            cfg.update(cfg_extra or {})
            p = Path(tmp) / "cfg.json"; p.write_text(json.dumps(cfg), encoding="utf-8")
            (Path(tmp) / "e.json").write_text(json.dumps(est0), encoding="utf-8")
            with mock.patch.object(E, "CFG", p), mock.patch.object(E, "ESTADO", Path(tmp) / "e.json"), mock.patch.object(E, "PAINEL", Path(tmp) / "p.json"), \
                 mock.patch.object(E, "_get", falso), mock.patch("src.livros_regra.registrar_achados", return_value={}):
                r = E.ler_motor(hoje=date(2026, 10, 3), orcamento=60)
                est = json.loads((Path(tmp) / "e.json").read_text(encoding="utf-8"))
        return r, est

    def test_monitoramento_pagina_em_ordem_crescente_e_revisa_com_lexico_novo(self):
        pedidas = []

        def falso(url, timeout=25):
            pedidas.append(url)
            pg = int(url.split("&page=")[1].split("&")[0]) if "&page=" in url else 1
            lote = [{"id": pg * 1000 + i, "date": f"2026-09-{10 + pg:02d}T10:00:00", "link": f"https://goias.gov.br/x/p{pg}-{i}/",
                     "title": {"rendered": "Notícia"}, "excerpt": {"rendered": ""}} for i in range(100 if pg < 3 else 7)]
            return 200, json.dumps(lote), {"X-WP-TotalPages": "3"}
        est0 = {"catalogo_em": "2026-10-03", "lexico_versao": "antiga", "orgaos": {"x": {
            "id": "x", "nome": "Secretaria X", "site": "https://goias.gov.br/x", "camada": 4, "wordpress": True,
            "ultima_publicacao_vista": "2026-10-02", "publicacoes_por_ano": {"2026": 1}}}}
        r, est = self._cenario(est0, falso)
        self.assertTrue(all("order=asc" in u for u in pedidas))
        self.assertIn("after=2026-08-04", pedidas[0])                         # revisão de 60 dias com o léxico novo
        self.assertEqual(len(pedidas), 3)                                      # paginou até o fim
        self.assertEqual(est["orgaos"]["x"]["ultima_publicacao_vista"], "2026-09-13")
        self.assertEqual(est["lexico_versao"], LEX["versao"])
        self.assertNotIn("paginas_nao_lidas", r["diagnostico"])

    def test_falha_e_orgao_nao_lido_viram_leitura_parcial(self):
        def falso(url, timeout=25):
            return 503, "", {}
        est0 = {"catalogo_em": "2026-10-03", "lexico_versao": LEX["versao"], "orgaos": {"x": {
            "id": "x", "nome": "Secretaria X", "site": "https://goias.gov.br/x", "camada": 4, "wordpress": True,
            "ultima_publicacao_vista": "2026-10-02", "publicacoes_por_ano": {"2026": 1}}}}
        r, est = self._cenario(est0, falso)
        self.assertTrue(any("monitoramento" in f["erro"] for f in r["falhas"]))
        self.assertEqual(r["diagnostico"]["paginas_nao_lidas"], 1)
        self.assertEqual(est["ultima"]["cobertura_orgaos"]["pendentes"], ["x"])

    def test_site_fora_do_portal_passa_a_ser_monitorado(self):
        pagina = {"v": "<a href='/editais/antigo'>Edital de chamamento 2024 para entidades</a>"}

        def falso(url, timeout=25):
            return 200, pagina["v"], {}
        est0 = {"catalogo_em": "2026-10-03", "lexico_versao": LEX["versao"], "orgaos": {"ovg": {
            "id": "ovg", "nome": "OVG", "site": "https://www.ovg.org.br", "camada": 4, "wordpress": False,
            "onde_publica": ["link do site: Editais — https://www.ovg.org.br/editais"], "publicacoes_por_ano": {"2024": 1}}}}
        r1, est1 = self._cenario(est0, falso)
        self.assertEqual(r1["achados"], [])                                    # 1ª passagem só registra o que já existe
        pagina["v"] += "<a href='/editais/novo'>OVG abre chamamento público para organizações da sociedade civil</a>"
        r2, est2 = self._cenario(est1, falso)
        self.assertEqual(len(r2["achados"]), 1)
        self.assertEqual(est2["orgaos"]["ovg"]["monitorado_em"], "2026-10-03")


class TesteRegistroDaPassagem(unittest.TestCase):
    def test_resultado_tem_lido_em_e_sensor(self):
        """03/10: sem 'lido_em' a passagem de sensores caía com KeyError logo depois do motor 14 (e do 13)."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = json.loads((ROOT / "config/estaduais_go.json").read_text(encoding="utf-8"))
            cfg["orgaos_semente"] = []; cfg["descoberta"]["paginas_indice"] = []
            p = Path(tmp) / "cfg.json"; p.write_text(json.dumps(cfg), encoding="utf-8")
            (Path(tmp) / "e.json").write_text(json.dumps({"catalogo_em": "2026-10-03", "lexico_versao": LEX["versao"], "orgaos": {}}), encoding="utf-8")
            with mock.patch.object(E, "CFG", p), mock.patch.object(E, "ESTADO", Path(tmp) / "e.json"), mock.patch.object(E, "PAINEL", Path(tmp) / "p.json"):
                r = E.ler_motor(hoje=date(2026, 10, 3), orcamento=5)
        self.assertEqual(r["sensor"], "plat-estaduais-go-gov")
        self.assertTrue(r["lido_em"])

    def test_passagem_normaliza_resultado_sem_lido_em(self):
        src = (ROOT / "src/sensores.py").read_text(encoding="utf-8")
        i = src.index("r = ler(s, pausa=pausa)")
        self.assertLess(i, src.index('r.setdefault(_k, _v)'))
        self.assertLess(src.index('r.setdefault(_k, _v)'), src.index('reg.update({"ultima": r["lido_em"]'))
