"""14/10/2026 (titular): replicador nunca é fonte oficial; o motor segue para o lugar que o replicador indica e acha o
PDF do edital na fonte; o que dá certo nos casos conhecidos vira aprendizado."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import fonte_oficial as F

PAG = {
    "https://www.capitaai.com.br/edital-x": '<a href="/outro">outro edital</a><a href="https://www.facebook.com/x">face</a>'
        '<a href="https://www.anapolis.go.gov.br/chamamento-cultura-2026">Acesse o edital completo</a>',
    "https://www.anapolis.go.gov.br/chamamento-cultura-2026": '<a href="/wp-content/uploads/2026/10/edital-chamamento-cultura.pdf">Edital de chamamento</a>'
        '<a href="/noticias">notícias</a>',
    "https://pncp.gov.br/api/consulta/v1/orgaos/01612092000123/compras/2026/7": json.dumps({"linkSistemaOrigem": "https://www.goiania.go.gov.br/edital-7"}),
    "https://www.goiania.go.gov.br/edital-7": '<a href="https://www.goiania.go.gov.br/arquivos/edital-7.pdf">Baixar o edital</a>',
    "https://captadores.org.br/editais/y": '<a href="https://www.institutoexemplo.org.br/programa">Veja aqui</a><a href="https://www.blogqualquer.com/z">mais</a>',
}
get = lambda u: PAG[u]


class TesteFonteOficial(unittest.TestCase):
    def test_classificacao(self):
        for u in ("https://pncp.gov.br/app/editais/1/2026/1", "https://www.capitaai.com.br/x", "https://data.queridodiario.ok.org.br/x", "https://captadores.org.br/x"):
            self.assertTrue(F.eh_replicador(u), u)
        for u in ("https://prosas.com.br/editais/1", "https://mapacultural.secult.ce.gov.br/oportunidade/1", "https://www.bndes.gov.br/x"):
            self.assertFalse(F.eh_replicador(u), u); self.assertTrue(F.eh_fonte(u), u)

    def test_replicador_leva_a_fonte_e_ao_pdf(self):
        o = F.resolver("https://www.capitaai.com.br/edital-x", "Chamamento Cultura 2026", "Prefeitura de Anápolis", get, {"replicadores": {}, "oficiais": {}})
        self.assertEqual(o["fonte"], "https://www.anapolis.go.gov.br/chamamento-cultura-2026")
        self.assertTrue(o["pdfs"] and o["pdfs"][0]["url"].endswith("edital-chamamento-cultura.pdf"))

    def test_pncp_segue_o_link_de_origem_do_orgao(self):
        o = F.resolver("https://pncp.gov.br/app/editais/01612092000123/2026/7", "Edital 7", "Prefeitura de Goiânia", get, {"replicadores": {}, "oficiais": {}})
        self.assertEqual(o["fonte"], "https://www.goiania.go.gov.br/edital-7"); self.assertEqual(len(o["pdfs"]), 1)

    def test_aprendizado_aumenta_a_assertividade(self):
        sem = F.escolher_fonte("https://captadores.org.br/editais/y", PAG["https://captadores.org.br/editais/y"], "Programa", "Instituto", {"replicadores": {}})
        com = F.escolher_fonte("https://captadores.org.br/editais/y", PAG["https://captadores.org.br/editais/y"], "Programa", "Instituto",
                               {"replicadores": {"captadores.org.br": {"ancoras": {"veja aqui": 5}}}})
        self.assertGreater(com[1], sem[1]); self.assertEqual(com[0], "https://www.institutoexemplo.org.br/programa")

    def test_repositorio_nao_aceita_replicador_como_site_oficial(self):
        src = (ROOT / "src/repositorio_unico.py").read_text(encoding="utf-8")
        self.assertIn("if link and _eh_rep(link):", src)
        self.assertTrue((ROOT / ".github/workflows/treino-fontes.yml").exists())


if __name__ == "__main__":
    unittest.main()


class TesteFontesEstruturadas(unittest.TestCase):
    """14/10 (treino real): Querido Diário → diário original do município (API); PNCP → linkProcessoEletronico."""
    def test_querido_e_pncp(self):
        P = {"https://api.queridodiario.ok.org.br/gazettes?territory_ids=2919603&published_since=2026-10-05&published_until=2026-10-05&size=20":
             json.dumps({"gazettes": [{"url": "http://macajuba.ba.gov.br/diario/2026-10-05.pdf", "txt_url": "https://data.queridodiario.ok.org.br/2919603/2026-10-05/43d2f4b96e7df3c2791d13314a81bae6bbb73cb7.txt"}]}),
             "https://pncp.gov.br/api/consulta/v1/orgaos/07598634000137/compras/2026/159": json.dumps({"linkSistemaOrigem": None, "linkProcessoEletronico": "https://www.medianeira.pr.gov.br/arquivos/compras/2026/edital-159.pdf"})}
        o = F.resolver("https://data.queridodiario.ok.org.br/2919603/2026-10-05/43d2f4b96e7df3c2791d13314a81bae6bbb73cb7.pdf", "", "", P.__getitem__, {})
        self.assertEqual(o["fonte"], "http://macajuba.ba.gov.br/diario/2026-10-05.pdf")
        o = F.resolver("https://pncp.gov.br/app/editais/07598634000137/2026/159", "", "", P.__getitem__, {})
        self.assertTrue(o["fonte"].startswith("https://www.medianeira.pr.gov.br/")); self.assertTrue(o["pdfs"])


class TestePrefeituraSemLink(unittest.TestCase):
    def test_pncp_sem_link_usa_o_site_da_prefeitura(self):
        P = {"https://pncp.gov.br/api/consulta/v1/orgaos/76206606000140/compras/2026/9": json.dumps(
                {"linkSistemaOrigem": None, "linkProcessoEletronico": None, "orgaoEntidade": {"esferaId": "M"},
                 "unidadeOrgao": {"municipioNome": "Medianeira", "ufSigla": "PR"}}),
             "https://www.medianeira.pr.gov.br/": "<html>Prefeitura de Medianeira</html>"}
        def g(u):
            if u not in P:
                raise OSError(u)
            return P[u]
        self.assertEqual(F.link_de_origem_pncp("https://pncp.gov.br/app/editais/76206606000140/2026/9", g), "https://www.medianeira.pr.gov.br/")


class TesteNaColeta(unittest.TestCase):
    def test_resolvedor_roda_na_coleta(self):
        self.assertIn("python scripts/treino_fontes.py --aplicar", (ROOT / ".github/workflows/motor-agregadores.yml").read_text(encoding="utf-8"))
        self.assertIn('"scripts/treino_fontes.py", "--aplicar"', (ROOT / "src/comando.py").read_text(encoding="utf-8"))   # 15/10: fase do comando
        self.assertIn("so_novas=True", (ROOT / "scripts/treino_fontes.py").read_text(encoding="utf-8"))


class TesteQueridoPeloIbge(unittest.TestCase):
    def test_querido_sem_original_vai_ao_site_da_prefeitura(self):
        P = {"https://api.queridodiario.ok.org.br/gazettes?territory_ids=2919603&published_since=2026-10-05&published_until=2026-10-05&size=20":
             json.dumps({"gazettes": [{"url": "https://data.queridodiario.ok.org.br/2919603/2026-10-05/43d2f4b96e7df3c2791d13314a81bae6bbb73cb7.pdf",
                                       "territory_name": "Macajuba", "state_code": "BA"}]}),
             "https://www.macajuba.ba.gov.br/": "<html>Prefeitura</html>"}
        def g(u):
            if u not in P:
                raise OSError(u)
            return P[u]
        o = F.resolver("https://data.queridodiario.ok.org.br/2919603/2026-10-05/43d2f4b96e7df3c2791d13314a81bae6bbb73cb7.pdf", "", "", g, {})
        self.assertEqual(o["fonte"], "https://www.macajuba.ba.gov.br/")


class TesteMapaDosRaspadores(unittest.TestCase):
    """14/10 (pesquisa no GitHub): mapa IBGE → endereço oficial do diário, dos raspadores do Querido Diário (MIT)."""
    def _g(self, P):
        def g(u):
            if u not in P:
                raise OSError(u)
            return P[u]
        return g

    def test_mapa_resolve_mesmo_sem_a_api(self):
        M = json.loads((ROOT / "config/querido_diario_fontes.json").read_text(encoding="utf-8"))["municipios"]
        self.assertGreater(len(M), 400); self.assertIn("4205407", M)
        g = self._g({"https://www.curitiba.pr.gov.br/": "ok", "https://curitiba.pr.gov.br/": "ok"})
        o = F.resolver("https://data.queridodiario.ok.org.br/4106902/2026-09-30/4b4cb769910e7956d376d69f4674a5a626b27f3e.pdf", "", "", g, {})
        self.assertIn("curitiba.pr.gov.br", o["fonte"])

    def test_dominio_fora_do_padrao_e_plataforma_oficial(self):
        g = self._g({"https://pmf.sc.gov.br/": "ok"})
        o = F.resolver("https://data.queridodiario.ok.org.br/4205407/2026-09-30/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.pdf", "", "", g, {})
        self.assertTrue(o["fonte"] is None or "sc.gov.br" in o["fonte"])
        g2 = self._g({"https://doem.org.br": "ok"})
        o2 = F.resolver("https://data.queridodiario.ok.org.br/2919603/2026-10-05/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.pdf", "", "", g2, {})
        self.assertEqual(o2["fonte"], "https://doem.org.br")
