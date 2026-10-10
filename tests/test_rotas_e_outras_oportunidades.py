"""10/10 (titular): leitura diária; 5 vazias → alterar rota, com rotas alternativas (inclusive câmara e ponte) e uma rede
que aprende onde buscar; motor Outras Oportunidades em clones dimensionados; agregadores recebem locais novos."""
import json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import rotas_motores as RM
from src import outras_oportunidades as OO


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); T = Path(self.tmp.name)
        self.o = {k: getattr(RM, k) for k in ("PASTA", "ESTADO", "APRENDIDAS", "PONTE", "MODELO", "AFINADOR", "RELATORIO")}
        RM.PASTA = T; RM.ESTADO = T / "r.json"; RM.APRENDIDAS = T / "a.json"; RM.PONTE = T / "p.json"; RM.MODELO = T / "m.json"
        RM.AFINADOR = T / "f.json"; RM.RELATORIO = T / "rel.json"
        self.oo = (OO.FONTES, OO.AGREGADORES); OO.FONTES = T / "fontes.json"; OO.AGREGADORES = T / "ag.json"

    def tearDown(self):
        for k, v in self.o.items():
            setattr(RM, k, v)
        OO.FONTES, OO.AGREGADORES = self.oo; self.tmp.cleanup()


class TesteRotas(Base):
    S = {"id": "m1", "nome": "Câmara Municipal X", "tipo": "legislativo", "urls": ["https://www.camarax.go.leg.br/"]}
    VAZIA = {"achados": [], "diagnostico": {"paginas_lidas": 1, "links_total": 0, "motivo_zero": "página respondeu mas não tem links (conteúdo carregado por JavaScript)"}}
    SEM_OPORT = {"achados": [], "diagnostico": {"paginas_lidas": 3, "links_total": 80, "motivo_zero": "nenhum edital aberto hoje"}}

    def test_cinco_vazias_pedem_alterar_rota_e_leitura_sem_oportunidade_nao_conta(self):
        for i in range(4):
            self.assertEqual(RM.registrar(self.VAZIA, self.S)["status"], "ok")
        self.assertEqual(RM.registrar(self.VAZIA, self.S)["status"], "alterar rota", "5ª vazia")
        self.assertEqual(RM.registrar(self.SEM_OPORT, self.S)["vazias_seguidas"], 0, "leu a página: dia sem oportunidade não é rota errada")

    def test_camara_tem_rotas_proprias(self):
        urls = [c["url"] for c in RM.candidatas(self.S)]
        self.assertTrue(any("/api/sessao/sessaoplenaria" in u for u in urls), "sessões do SAPL")
        self.assertTrue(any("/pauta" in u or "ordem-do-dia" in u for u in urls), "pauta / ordem do dia")
        self.assertTrue(any("diario-oficial" in u for u in urls), "diário oficial da câmara")
        self.assertTrue(any(u.startswith("https://sapl.camarax.go.leg.br") for u in urls))

    def test_afinador_acha_a_rota_usa_a_ponte_e_a_rede_aprende(self):
        for _ in range(5):
            RM.registrar(self.VAZIA, self.S)
        def baixar(u):
            raise OSError("recusou a nuvem")
        def ponte(u):
            if "/pauta" in u:
                return (b"<html>" + b"".join(b'<a href="/s%d">Pauta da sess\xc3\xa3o %d</a>' % (i, i) for i in range(5)) + b"</html>", "text/html")
            return (b"<html>vazio</html>", "text/html")
        import src.sensores as SS
        orig = SS.registro; SS.registro = lambda: [dict(self.S)]
        try:
            out = RM.afinar(3, baixar=baixar, ponte=ponte)
        finally:
            SS.registro = orig
        m = out["afinados"][0]["melhor"]
        self.assertEqual(m["via"], "ponte"); self.assertIn("/pauta", m["url"])
        self.assertIn("www.camarax.go.leg.br", json.loads(RM.PONTE.read_text())["dominios"], "domínio passa a atravessar a ponte")
        self.assertGreater(RM.prever("https://outra.go.leg.br/pauta", "legislativo", "ponte", "câmara"),
                           RM.prever("https://outra.go.leg.br/qualquer", "legislativo", "direto", "padrão"), "a rede aprendeu onde buscar")
        s = RM.aplicar([dict(self.S)])[0]
        self.assertEqual(s["urls"][0], m["url"]); self.assertIn("https://www.camarax.go.leg.br/", s["urls"], "a rota original fica (redundância)")
        self.assertEqual(RM.registrar(self.SEM_OPORT, self.S)["status"], "rota nova funcionando")
        self.assertIn("alterar_rota", RM.publicar()["resumo"])


class TesteOutras(Base):
    def test_dimensionamento_e_clones(self):
        d = OO.dimensionar(197)
        self.assertEqual(d["clones"], 4); self.assertTrue(d["le_todas_no_dia"])
        self.assertEqual(OO.dimensionar(126)["clones"], 3); self.assertEqual(OO.dimensionar(5000)["clones"], OO.MAX_CLONES)

    def test_um_site_por_vez_todos_no_dia_e_a_rede_prioriza(self):
        fontes = {f"s{i}.org.br": {"url": f"https://s{i}.org.br", "leituras": 10, "achados": 0} for i in range(40)}
        fontes["bom.org.br"] = {"url": "https://bom.org.br", "leituras": 10, "achados": 9}
        OO.FONTES.write_text(json.dumps({"fontes": fontes}))
        vistos = set()
        for h in (2, 12, 20):
            vistos |= set(OO.lista_do_clone(1, 1, datetime(2026, 10, 10, h, tzinfo=timezone.utc)))
        self.assertEqual(len(vistos), 41, "as 3 janelas do dia leem todas as fontes do clone")
        self.assertGreater(OO._prioridade("bom.org.br", fontes["bom.org.br"]), OO._prioridade("s1.org.br", fontes["s1.org.br"]), "quem rende vem antes")
        OO.contabilizar({"achados": [{"url": "https://s3.org.br/edital"}]}, {"id": "outras-oportunidades-1", "urls": ["https://s3.org.br"]})
        f = json.loads(OO.FONTES.read_text())["fontes"]["s3.org.br"]
        self.assertEqual((f["leituras"], f["achados"]), (11, 1))

    def test_agregadores_recebem_locais_novos(self):
        out = OO.alimentar_agregadores({"instituto.org.br": {"url": "https://instituto.org.br", "origem": "conselho"},
                                        "prefeitura.go.gov.br": {"url": "https://prefeitura.go.gov.br", "origem": "conselho"}})
        nomes = [x["nome"] for x in out["patrocinio"]]
        self.assertIn("instituto.org.br", nomes); self.assertNotIn("prefeitura.go.gov.br", nomes, "governo não vai para patrocínio")
        self.assertIn("sites_para_agregadores.json", (ROOT / "src/patrocinios.py").read_text(encoding="utf-8"))
        self.assertIn("sites_para_agregadores.json", (ROOT / "src/sensores.py").read_text(encoding="utf-8"))


class TesteConfig(unittest.TestCase):
    def test_leitura_diaria_e_motor_na_esquadra(self):
        c = json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8"))
        self.assertEqual(c["cadencia"]["rodizio_semanal"], []); self.assertIn("site_oficial", c["cadencia"]["diaria"])
        a = json.loads((ROOT / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        ativos = {k: v for k, v in a.items() if str(v.get("dias")) != "inativo" and not v.get("agregado_a")}
        self.assertFalse([k for k, v in ativos.items() if str(v.get("cadencia_dias") or 1) != "1"], "todo motor ativo é lido diariamente")
        self.assertIn("outras-oportunidades-1", a); self.assertNotIn("fontes-irmas", a)
        self.assertTrue(any(s["id"] == "outras-oportunidades" for s in c["sensores_especiais"]))
        self.assertIn("python -m src.rotas_motores", (ROOT / ".github/workflows/cartorio.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


class TesteValidacao(unittest.TestCase):
    def test_segunda_rodada_tem_perguntas_novas_e_responde(self):
        from src import conselho_validacao as CV
        self.assertEqual(len(CV.PERGUNTAS), 7)
        o = CV.run(gravar=False)
        for k in CV.PERGUNTAS:
            self.assertIn(k, o["respostas"])
        self.assertIn("## Dra. Irene", CV.relatorio_md(o))

    def test_afinador_respeita_o_orcamento(self):
        import time
        lento = lambda u: (time.sleep(0.2), (b"<html></html>", "text/html"))[1]
        t0 = time.time()
        r = RM.testar({"id": "x", "tipo": "site_oficial", "urls": ["https://x.go.gov.br/"]}, lento, None, None, 16, prazo=time.time() + 0.5)
        self.assertLess(time.time() - t0, 1.5); self.assertLess(len(r["testes"]), 16)
