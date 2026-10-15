"""15/10/2026: do site ao PDF — o resolvedor entra no site oficial até o documento (2 níveis, mesmo site)."""
import json
import unittest

from src import fonte_oficial as F

BASE = "https://www.anapolis.go.gov.br"
SITE = {
    f"{BASE}/noticia/edital-pnab": '<a href="/">Início</a><a href="/editais">Editais e Chamamentos</a>'
                                  '<a href="https://facebook.com/x">Face</a><a href="https://outro.gov.br/editais">Outro site</a>',
    f"{BASE}/editais": '<a href="/editais/cultura">Cultura</a><a href="/editais/saude">Saúde</a>'
                       '<a href="/editais/chamamento-004-2026">Chamamento Público 004/2026 - PNAB</a>',
    f"{BASE}/editais/chamamento-004-2026": '<a href="/wp-content/uploads/2026/09/EDITAL-004-2026-PNAB.pdf">Edital completo</a>'
                                           '<a href="/wp-content/uploads/2026/09/ANEXO-I.pdf">Anexo I</a>',
    f"{BASE}/editais/cultura": "<p>nada</p>", f"{BASE}/editais/saude": "<p>nada</p>", f"{BASE}/": "<p>home</p>",
}


class Rede:
    def __init__(self, mapa):
        self.mapa, self.pedidos = mapa, []

    def __call__(self, url):
        self.pedidos.append(url)
        if url not in self.mapa:
            raise OSError("404")
        return self.mapa[url]


class Navegacao(unittest.TestCase):
    TIT = "Prefeitura de Anápolis — Chamamento Público nº 004/2026 PNAB cultura"

    def test_chega_ao_pdf_dois_niveis_dentro(self):
        g = Rede(SITE)
        pdfs, caminho = F.navegar(f"{BASE}/noticia/edital-pnab", SITE[f"{BASE}/noticia/edital-pnab"], self.TIT, g, {})
        self.assertTrue(pdfs)
        self.assertTrue(pdfs[0]["url"].endswith("EDITAL-004-2026-PNAB.pdf"), pdfs)
        self.assertEqual(pdfs[0]["nivel"], 2)
        self.assertFalse(any("facebook" in u or "outro.gov.br" in u for u in g.pedidos))   # só o mesmo site
        self.assertLessEqual(len(g.pedidos), F.NAV_PAGINAS)

    def test_resolver_usa_a_navegacao_e_pode_desligar(self):
        url = f"{BASE}/noticia/edital-pnab"
        com = F.resolver(url, self.TIT, "", Rede(SITE), {})
        sem = F.resolver(url, self.TIT, "", Rede(SITE), {}, navegacao=False)
        self.assertTrue(com["pdfs"] and com["pdfs"][0]["url"].endswith("EDITAL-004-2026-PNAB.pdf"))
        self.assertEqual(sem["pdfs"], [])
        self.assertTrue(any("navegação no site" in p for p in com["passos"]))

    def test_pdf_na_propria_pagina_nao_navega(self):
        h = '<a href="/arq/edital-004-2026.pdf">Edital 004/2026</a><a href="/editais">Editais</a>'
        g = Rede({f"{BASE}/x": h})
        o = F.resolver(f"{BASE}/x", self.TIT, "", g, {})
        self.assertTrue(o["pdfs"][0]["url"].endswith("edital-004-2026.pdf"))
        self.assertEqual(g.pedidos, [f"{BASE}/x"])                                          # nenhuma página a mais

    def test_wordpress_biblioteca_de_midia(self):
        midia = json.dumps([{"source_url": f"{BASE}/wp-content/uploads/2026/10/edital-4-2026.pdf", "title": {"rendered": "Edital 4/2026"}}])
        h = '<link href="/wp-content/themes/x/style.css"><a href="/contato">Contato</a>'
        g = Rede({f"{BASE}/p": h, f"{BASE}/wp-json/wp/v2/media?search=4/2026&per_page=10": midia})
        pdfs, cam = F.navegar(f"{BASE}/p", h, "Edital de Chamamento 004/2026", g, {})
        self.assertTrue(pdfs and pdfs[0]["url"].endswith("edital-4-2026.pdf"), (pdfs, cam))

    def test_numero_do_edital(self):
        self.assertEqual(F._numero("Edital nº 004/2026"), ("4", "2026"))
        self.assertTrue(F._tem_numero("EDITAL-004-2026-PNAB.pdf", ("4", "2026")))
        self.assertFalse(F._tem_numero("edital 14/2026", ("4", "2026")))


if __name__ == "__main__":
    unittest.main()


class ArquivoDoOrgaoNoPNCP(unittest.TestCase):
    def test_sistema_de_compras_sem_pdf_usa_o_arquivo_do_orgao(self):
        api = "https://pncp.gov.br/api/consulta/v1/orgaos/12345678000199/compras/2026/7"
        arq = "https://pncp.gov.br/pncp-api/v1/orgaos/12345678000199/compras/2026/7/arquivos"
        mapa = {api: json.dumps({"linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/x"}),
                "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/x": "<div id=app></div>",
                arq: json.dumps([{"url": arq + "/2", "tipoDocumentoNome": "Anexo", "titulo": "Planilha", "statusAtivo": True},
                                 {"url": arq + "/1", "tipoDocumentoNome": "Edital", "titulo": "Edital 7/2026", "statusAtivo": True},
                                 {"url": arq + "/3", "tipoDocumentoNome": "Edital", "titulo": "antigo", "statusAtivo": False}])}
        o = F.resolver("https://pncp.gov.br/app/editais/12345678000199/2026/7", "Chamamento 7/2026", "", Rede(mapa), {})
        self.assertTrue(o["fonte"].startswith("https://cnetmobile"))          # a fonte continua sendo o órgão
        self.assertEqual(o["pdfs"][0]["url"], arq + "/1")
        self.assertNotIn(arq + "/3", [p["url"] for p in o["pdfs"]])
        sem = F.resolver("https://pncp.gov.br/app/editais/12345678000199/2026/7", "Chamamento 7/2026", "", Rede(mapa), {}, navegacao=False)
        self.assertEqual(sem["pdfs"], [])
