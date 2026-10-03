"""Motores indexadores (titular, 02/10/2026): robots.txt RFC 9309, extração, os seis leitores, a escada de rotas,
a ponte Brasil, a coleta assistida e a entrada no fluxo — tudo sem rede (respostas gravadas em memória)."""
from __future__ import annotations

import gzip
import io
import json
import shutil
import tempfile
import unittest
import urllib.error
import zipfile
from datetime import date, datetime, timezone
from email.message import Message
from pathlib import Path
from unittest import mock

from src.indexadores import extracao as X
from src.indexadores import leitores as L
from src.indexadores import motor as M
from src.indexadores import ponte as P
from src.indexadores.rede import Bloqueio, Rede, analisar_robots, permitido, regras_para

HOJE = date(2026, 10, 2)
ROBOTS_PROSAS = """User-agent: *
Disallow: /admin/
Crawl-Delay: 30

User-agent: *
Disallow: /uploads/system/arquivos/

User-agent: google
User-agent: googlebot
Disallow: /admin/
Crawl-Delay: 15

User-agent: *
Disallow: /
"""


class _Resp:
    def __init__(self, url, status, corpo, cab):
        self._url, self.status, self._c = url, status, corpo
        m = Message()
        for k, v in (cab or {}).items():
            m[k] = v
        self.headers = m

    def geturl(self):
        return self._url

    def read(self, n=-1):
        return self._c if n < 0 else self._c[:n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Web:
    """Internet de mentira: url (ou prefixo terminado em *) → (status, corpo, cabeçalhos)."""

    def __init__(self, rotas: dict):
        self.rotas, self.pedidos = rotas, []

    def __call__(self, req, timeout=0):
        url = req.full_url
        self.pedidos.append((url, dict(req.header_items())))
        alvo = self.rotas.get(url)
        if alvo is None:
            for k, v in self.rotas.items():
                if k.endswith("*") and url.startswith(k[:-1]):
                    alvo = v; break
        if alvo is None:
            if url.endswith("/robots.txt"):
                alvo = (404, b"", {})
            else:
                raise urllib.error.HTTPError(url, 404, "nao achou", Message(), io.BytesIO(b""))
        if callable(alvo):
            alvo = alvo(req)
        st, corpo, cab = alvo
        if isinstance(corpo, str):
            corpo = corpo.encode("utf-8")
        if st >= 300:
            m = Message()
            for k, v in (cab or {}).items():
                m[k] = v
            raise urllib.error.HTTPError(url, st, "erro", m, io.BytesIO(corpo))
        return _Resp(url, st, corpo, cab)


def rede(web, **kw):
    return Rede(token="EldoradoIndexadores", user_agent="EldoradoIndexadores/teste", pausa_padrao=0, abrir=web,
                dormir=lambda s: None, **kw)


def ctx(**kw):
    return dict({"hoje": HOJE, "via": "direta", "limites": {"itens_por_site_por_rodada": 80}, "estado_motores": {}, "rota": "nuvem"}, **kw)


class RobotsRFC9309(unittest.TestCase):
    def test_grupos_de_asterisco_se_somam_prosas_fecha_tudo(self):
        regras, atraso = regras_para(analisar_robots(ROBOTS_PROSAS), "EldoradoIndexadores")
        self.assertFalse(permitido(regras, "/selecao/widgets/listagem-editais"))
        self.assertFalse(permitido(regras, "/selecao/api/v2/publics/oportunidades"))
        self.assertEqual(atraso, 30.0)

    def test_regra_mais_longa_e_allow_no_empate(self):
        txt = "User-agent: *\nDisallow: /editais/\nDisallow: /editais$\nAllow: /editais/abertos\nDisallow: /api/\n"
        r, _ = regras_para(analisar_robots(txt), "EldoradoIndexadores")
        self.assertTrue(permitido(r, "/editais-abertos/para-ong"))        # CapitaAI: prefixo /editais/ não pega /editais-abertos
        self.assertTrue(permitido(r, "/captacao/edital-x"))
        self.assertFalse(permitido(r, "/editais"))
        self.assertFalse(permitido(r, "/editais/123"))
        self.assertTrue(permitido(r, "/editais/abertos/1"))
        self.assertFalse(permitido(r, "/api/v1"))

    def test_disallow_vazio_e_grupo_proprio(self):
        txt = "User-agent: *\nDisallow: /\n\nUser-agent: EldoradoIndexadores\nDisallow:\n"
        r, _ = regras_para(analisar_robots(txt), "EldoradoIndexadores")
        self.assertTrue(permitido(r, "/qualquer"))

    def test_rede_recusa_por_robots(self):
        web = Web({"https://prosas.com.br/robots.txt": (200, ROBOTS_PROSAS, {})})
        with self.assertRaises(Bloqueio) as c:
            rede(web).obter("https://prosas.com.br/selecao/widgets/listagem-editais")
        self.assertEqual(c.exception.tipo, "robots")
        self.assertEqual(len(web.pedidos), 1)                             # só o robots.txt foi pedido


class Extracao(unittest.TestCase):
    def test_prazos(self):
        self.assertEqual(X.prazo("Inscrições até 15/10/2026", HOJE), "2026-10-15")
        self.assertEqual(X.prazo("inscrições abertas até 30 de outubro de 2026", HOJE), "2026-10-30")
        self.assertEqual(X.prazo("Recebimento de propostas: 01/09/2026 a 30/10/2026", HOJE), "2026-10-30")
        self.assertEqual(X.prazo("Deadline: October 20, 2026", HOJE), "2026-10-20")
        self.assertEqual(X.prazo("Deadline: 15-Oct-2026", HOJE), "2026-10-15")
        self.assertEqual(X.prazo("captar R$ 10 mil até 02/10.", HOJE), "2026-10-02")
        self.assertIsNone(X.prazo("Edital 03/2026 publicado em 10/12/2026", HOJE))

    def test_valor_uf_perfil(self):
        self.assertEqual(X.valor("apoio de até R$ 1,5 milhão"), "R$ 1,5 milhão")
        self.assertEqual(X.uf("2º PRÊMIO CULTURA VIVA | IBIASSUCÉ-BA"), "BA")
        self.assertEqual(X.uf("Secretaria de Cultura do Estado de Goiás"), "GO")
        self.assertIsNone(X.uf("recursos para pessoas"))
        self.assertEqual(X.perfil("podem participar organizações da sociedade civil")[0], "osc")
        self.assertEqual(X.perfil("bolsas de doutorado para pesquisadores")[0], "fora")
        self.assertEqual(X.perfil("prêmio de música")[0], "indefinido")

    def test_link_oficial_nao_e_agregador_rede_social_nem_lei(self):
        links = [("https://www.facebook.com/x", "Facebook"), ("https://www.planalto.gov.br/ccivil_03/leis/l13019.htm", "Lei 13.019"),
                 ("https://capitaai.com.br/captacao/outro", "veja também"),
                 ("https://goias.gov.br/fapeg/wp-content/uploads/2026/09/CHAMADA_FAPEG_08.2026.pdf", "Edital completo")]
        self.assertEqual(X.oficial("https://capitaai.com.br/captacao/fapeg-08", links, "Chamada pública FAPEG 08/2026"),
                         "https://goias.gov.br/fapeg/wp-content/uploads/2026/09/CHAMADA_FAPEG_08.2026.pdf")

    def test_chave_canonica(self):
        a = X.chave({"link_oficial": "https://www.pncp.gov.br/app/editais/1/2026/137?utm_source=farol", "titulo": "A"})
        b = X.chave({"link_oficial": "http://pncp.gov.br/app/editais/1/2026/137/", "titulo": "B"})
        self.assertEqual(a, b)
        self.assertTrue(X.chave({"titulo": "Edital X", "prazo": "2026-10-10"}).startswith("t:"))


RSS = """<?xml version="1.0"?><rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
<item><title>Fundação Maria Emília abre edital com apoio de até R$ 1 milhão</title>
<link>https://captadores.org.br/2026/09/maria-emilia-edital/</link><pubDate>Mon, 28 Sep 2026 10:00:00 +0000</pubDate>
<content:encoded><![CDATA[<p>Inscrições até 30/10/2026 para organizações da sociedade civil.</p>
<a href="https://www.facebook.com/abcr">curta</a> <a href="https://fundacaomariaemilia.org.br/edital-2026">Edital</a>]]></content:encoded></item>
<item><title>Edital sem link no feed</title><link>https://captadores.org.br/2026/09/sem-link/</link>
<description>Saiba mais no artigo.</description></item>
</channel></rss>"""


class LeitorFeed(unittest.TestCase):
    def site(self):
        return {"id": "abcr", "nome": "ABCR — editais", "motor": "idx-feeds", "leitor": "feed", "seguir_artigo": True,
                "url": "https://captadores.org.br/category/editais/feed/", "pagina": "https://captadores.org.br/category/editais/"}

    def test_feed_le_link_oficial_do_conteudo_e_do_artigo_e_304_depois(self):
        art = '<html><h1>Edital sem link no feed</h1><p>Inscrições até 20/11/2026.</p><a href="https://instituto.org.br/edital.pdf">Regulamento</a></html>'
        web = Web({"https://captadores.org.br/category/editais/feed/": (200, RSS, {"ETag": '"v1"'}),
                   "https://captadores.org.br/category/editais/feed/?paged=2": (404, "", {}),
                   "https://captadores.org.br/2026/09/sem-link/": (200, art, {})})
        est, r = {}, rede(web)
        res = L.ler_feed(dict(self.site(), paginas_retroativas=2), r, est, ctx())
        self.assertEqual(len(res["itens"]), 2)
        a, b = res["itens"]
        self.assertEqual(a["link_oficial"], "https://fundacaomariaemilia.org.br/edital-2026")
        self.assertEqual(a["prazo"], "2026-10-30")
        self.assertEqual(a["perfil"], "osc")
        self.assertEqual(b["link_oficial"], "https://instituto.org.br/edital.pdf")
        self.assertEqual(b["prazo"], "2026-11-20")
        self.assertTrue(a["id"].startswith("agr-"))
        # segunda rodada: o feed responde 304 (nada mudou) e nada é relido
        web.rotas["https://captadores.org.br/category/editais/feed/"] = lambda req: (
            304, "", {}) if req.get_header("If-none-match") == '"v1"' else (200, RSS, {})
        res2 = L.ler_feed(self.site(), r, est, ctx())
        self.assertEqual(res2["itens"], [])


class LeitorWordPress(unittest.TestCase):
    def test_tipo_proprio_do_financiador_e_link_oficial(self):
        dados = [{"id": 1, "date": "2026-07-17T14:39:47", "modified": "2026-08-26T09:17:18",
                  "link": "https://casa.org.br/chamadas/mulheres-que-transformam/",
                  "title": {"rendered": "Mulheres que Transformam o Futuro &#8211; Apoio a Soluções Comunitárias"},
                  "content": {"rendered": "<p>Inscrições até 30/10/2026. Podem participar grupos comunitários.</p>"}, "excerpt": {"rendered": ""}}]
        web = Web({"https://casa.org.br/wp-json/wp/v2/chamadas?*": (200, json.dumps(dados), {"X-WP-TotalPages": "1"})})
        site = {"id": "fundo-casa", "nome": "Fundo Casa", "motor": "idx-feeds", "leitor": "wordpress", "proprio": True,
                "url": "https://casa.org.br/wp-json/wp/v2/chamadas", "pagina": "https://casa.org.br/chamadas/", "areas": ["meio ambiente"]}
        est = {}
        res = L.ler_wordpress(site, rede(web), est, ctx())
        it = res["itens"][0]
        self.assertEqual(it["link_oficial"], "https://casa.org.br/chamadas/mulheres-que-transformam/")
        self.assertIn("–", it["titulo"])
        self.assertEqual(it["prazo"], "2026-10-30")
        self.assertEqual(it["areas"], ["meio ambiente"])
        self.assertEqual(est["modificado_ate"], "2026-08-26T09:17:18")
        self.assertIn("modified", web.pedidos[-1][0])


class LeitorFarol(unittest.TestCase):
    def test_api_paginada_ids_do_motor_antigo(self):
        def pag(n):
            dados = [{"id": n, "slug": f"municipio-de-sobral-edital-{n}", "titulo": f"Seleção de projetos culturais {n}",
                      "instituicao_nome": "MUNICIPIO DE SOBRAL", "pais": "BR", "estado": "CE", "cidade": "Sobral",
                      "area_artistica": ["Teatro"], "tipo": "Fomento", "status": "Aberto", "valor_total": 200000, "valor_por_projeto": None,
                      "moeda": "BRL", "data_fim_inscricao": "2026-10-20", "url_original": "https://pncp.gov.br/app/editais/07598634000137/2026/137",
                      "url_pdf": None, "resumo": "Apoio a coletivos e pessoas jurídicas sem fins lucrativos"}]
            return (200, json.dumps({"success": True, "data": dados, "meta": {"page": n, "per_page": 100, "total": 2, "total_pages": 2}}), {})
        web = Web({"https://farolcultural.art/api/v1/editais?status=Aberto&per_page=100&page=1": pag(1),
                   "https://farolcultural.art/api/v1/editais?status=Aberto&per_page=100&page=2": pag(2)})
        site = {"id": "farolcultural", "nome": "Farol Cultural — API", "motor": "idx-apis", "leitor": "farol_api",
                "url": "https://farolcultural.art/api/v1/editais", "areas": ["cultura"]}
        res = L.ler_farol_api(site, rede(web), {}, ctx())
        self.assertEqual(len(res["itens"]), 2)
        it = res["itens"][0]
        self.assertEqual(it["id"], L.id_de("https://farolcultural.art/e/municipio-de-sobral-edital-1"))
        self.assertEqual(it["link_oficial"], "https://pncp.gov.br/app/editais/07598634000137/2026/137")
        self.assertEqual((it["uf"], it["pais"], it["prazo"], it["valor"]), ("CE", "BR", "2026-10-20", "R$ 200.000,00"))
        self.assertIn("cultura", it["areas"])
        self.assertEqual(it["perfil"], "osc")


class LeitorMapasCulturais(unittest.TestCase):
    def test_filtra_tipo_e_sonda_candidatas(self):
        lista = [{"id": 11453, "name": "2º PRÊMIO TRAJETÓRIAS CULTURAIS | IBIASSUCÉ-BA", "shortDescription": "EDITAL DE CHAMAMENTO PÚBLICO",
                  "registrationTo": {"date": "2026-10-20 18:00:00.000000"}, "registrationFrom": {"date": "2026-09-18 08:00:00.000000"},
                  "singleUrl": "https://mapa.cultura.gov.br/oportunidade/11453/", "type": {"id": 9, "name": "Edital"}},
                 {"id": 12029, "name": "WORKSHOP DE PROJETOS", "shortDescription": "Workshop", "registrationTo": {"date": "2026-10-18 21:47:00"},
                  "singleUrl": "https://mapa.cultura.gov.br/oportunidade/12029/", "type": {"id": 23, "name": "Curso"}}]
        web = Web({"https://mapa.cultura.gov.br/api/opportunity/find?*": (200, json.dumps(lista), {}),
                   "https://spcultura.prefeitura.sp.gov.br/api/opportunity/find?*": (200, "[]", {})})
        site = {"id": "mapas-culturais", "nome": "Mapas Culturais", "motor": "idx-apis", "leitor": "mapas_culturais", "tipos": "edital|pr[eê]mio",
                "instancias": [{"host": "mapa.cultura.gov.br", "uf": None, "nome": "MinC", "confirmada": True},
                               {"host": "spcultura.prefeitura.sp.gov.br", "uf": "SP", "nome": "SP Cultura", "confirmada": False}]}
        est = {}
        res = L.ler_mapas_culturais(site, rede(web), est, ctx())
        self.assertEqual([x["titulo"] for x in res["itens"]], ["2º PRÊMIO TRAJETÓRIAS CULTURAIS | IBIASSUCÉ-BA"])
        x = res["itens"][0]
        self.assertEqual((x["link_oficial"], x["prazo"], x["uf"]), ("https://mapa.cultura.gov.br/oportunidade/11453/", "2026-10-20", "BA"))
        self.assertTrue(est["instancias"]["spcultura.prefeitura.sp.gov.br"]["responde"])
        self.assertIn("registrationTo=GTE%282026-10-02%29", next(u for u, _ in web.pedidos if "mapa.cultura" in u and "registrationTo" in u))


CAPTACAO = """<html><head><script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",
"headline":"Edital FAPEG Goiás pelo Mundo 2026: Guia de Captação","description":"Pesquisadores podem captar R$ 10 mil no edital FAPEG 2026 até 02/10.",
"datePublished":"2026-09-13T05:34:36.094Z"}</script><script type="application/ld+json">{"@type":"BreadcrumbList","itemListElement":[
{"@type":"ListItem","position":1,"name":"Capitaai"},{"@type":"ListItem","position":2,"name":"Editais"},
{"@type":"ListItem","position":3,"name":"CHAMADA PÚBLICA FAPEG Nº 08/2026 - Programa Goiás pelo Mundo"}]}</script></head>
<body><a href="https://goias.gov.br/fapeg/wp-content/uploads/2026/09/CHAMADA_FAPEG_N_08.2026.pdf">Edital</a>
<a href="https://goias.gov.br/fapeg/">FAPEG</a></body></html>"""


class LeitorSitemap(unittest.TestCase):
    def test_le_so_paginas_novas_ou_alteradas_com_cota(self):
        sm = "<urlset>" + "".join(f"<url><loc>https://capitaai.com.br/captacao/edital-{i}</loc><lastmod>2026-10-0{1 + i % 2}T05:00:00Z</lastmod></url>"
                                  for i in range(5)) + "<url><loc>https://capitaai.com.br/blog/x</loc></url></urlset>"
        web = Web({"https://capitaai.com.br/sitemap-captacao.xml": (200, sm, {}), "https://capitaai.com.br/captacao/*": (200, CAPTACAO, {})})
        site = {"id": "capitaai", "nome": "CapitaAI", "motor": "idx-sitemaps", "leitor": "sitemap_jsonld", "prefixo": "/captacao/",
                "url": "https://capitaai.com.br/sitemap-captacao.xml", "itens_por_rodada": 3}
        est, r = {}, rede(web)
        res = L.ler_sitemap_jsonld(site, r, est, ctx())
        self.assertEqual(len(res["itens"]), 3)
        self.assertTrue(res["pendente"])
        it = res["itens"][0]
        self.assertEqual(it["titulo"], "CHAMADA PÚBLICA FAPEG Nº 08/2026 - Programa Goiás pelo Mundo")
        self.assertEqual(it["link_oficial"], "https://goias.gov.br/fapeg/wp-content/uploads/2026/09/CHAMADA_FAPEG_N_08.2026.pdf")
        self.assertEqual(it["prazo"], "2026-10-02")
        res2 = L.ler_sitemap_jsonld(site, r, est, ctx())
        self.assertEqual(len(res2["itens"]), 2)
        self.assertFalse(res2["pendente"])
        res3 = L.ler_sitemap_jsonld(site, r, est, ctx())
        self.assertEqual(res3["itens"], [])


    def test_capitaai_prazo_do_cartao_e_nao_das_datas_ilustrativas_do_guia(self):
        """Calibrado no navegador (02/10/2026): o guia de /captacao/ tem datas inventadas ("perder prazos em 14 de março
        de 2024", "até 15 de julho de 2026"); o prazo de verdade está no cartão de /editais-abertos/<segmento>, e o
        link da fonte vem rotulado como "página oficial" (DOU, Google Forms, site do campus)."""
        pag = lambda bc, links: ("""<html><head><title>Guia · Capitaai</title><script type="application/ld+json">{"@type":"Article",
"headline":"Edital 2026: Guia de Captação","description":"Organizações sem fins lucrativos podem captar recursos em 2026. Entenda regras, prazos e erros.",
"datePublished":"2026-10-02T05:36:32.973Z"}</script><script type="application/ld+json">{"@type":"BreadcrumbList","itemListElement":[
{"@type":"ListItem","position":1,"name":"Capitaai"},{"@type":"ListItem","position":2,"name":"%s"}]}</script></head><body><main>
<p>Eu já vi captador experiente perder prazos preciosos em 14 de março de 2024 porque tentou aplicar em categoria errada.</p>
<p>O perfil primário desejado pela coordenação do campus vale até 15 de julho de 2026.</p>%s</main></body></html>""" % (bc, links))
        dou = "http://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?data=01/10/2026&jornal=530&pagina=210"
        p1 = pag("AVISO DE CHAMAMENTO PÚBLICO Nº 2/2026 - SECULJE",
                 f'<a href="{dou}">página oficial</a><a href="https://www.gov.br/cultura/pt-br/assuntos/pnab">Ministério da Cultura - Política Nacional</a>'
                 '<a href="http://www.planalto.gov.br/legislacao">Planalto - Legislação Federal</a>')
        p2 = pag("AVISO DE CHAMAMENTO PÚBLICO Nº 2/2026 - CP", '<a href="https://forms.gle/AyXhMZE5YHWD5pMu5">página oficial</a>')
        cartao = lambda slug, t, org, pz: (f'<a href="/captacao/{slug}"><div><div><div><h3>{t}</h3><p>{org}</p></div></div><p><span>Aceita:</span> '
                                           f'<!-- -->organizações da sociedade civil, empresas</p><div><span>Prazo: <!-- -->{pz} (13d)</span>'
                                           '<span>Ver detalhes →</span></div></div></a>')
        lista = ("<html><body>" + cartao("seculje-lauro", "Aviso de Chamamento Público nº 2/2026 - SECULJE", "Prefeitura Municipal de Lauro de Freitas", "15/10/2026")
                 + cartao("anater-4", "Aviso de Chamada Pública nº 4/2026 - ANATER", "Agência Nacional de Assistência Técnica e Extensão Rural", "20/10/2026")
                 + "</body></html>")
        base = "https://capitaai.com.br"
        sm = "<urlset>" + "".join(f"<url><loc>{base}/captacao/{s}</loc><lastmod>2026-10-02T05:3{i}:00Z</lastmod></url>"
                                  for i, s in enumerate(["anater-4", "portalegre-cp", "seculje-lauro"])) + "</urlset>"
        web = Web({f"{base}/sitemap-captacao.xml": (200, sm, {}),
                   f"{base}/sitemap-editais.xml": (200, f"<urlset><url><loc>{base}/editais-abertos/cultura</loc></url><url><loc>{base}/leis-de-incentivo</loc></url></urlset>", {}),
                   f"{base}/editais-abertos/cultura": (200, lista, {}), f"{base}/editais-abertos/para-ong": (200, "<html></html>", {}),
                   f"{base}/captacao/seculje-lauro": (200, p1, {}), f"{base}/captacao/portalegre-cp": (200, p2, {}),
                   f"{base}/captacao/anater-4": (200, pag("Aviso de Chamada Pública nº 4/2026 - ANATER",
                                                         '<a href="https://www.gov.br/anater/pt-br/chamada-4-2026.pdf">página oficial</a>'), {})})
        site = {"id": "capitaai", "nome": "CapitaAI", "motor": "idx-sitemaps", "leitor": "sitemap_jsonld", "prefixo": "/captacao/",
                "url": f"{base}/sitemap-captacao.xml", "pagina": f"{base}/editais-abertos/para-ong", "itens_por_rodada": 2,
                "listas_sitemap": f"{base}/sitemap-editais.xml", "listas_prefixo": "/editais-abertos", "listas_por_rodada": 5, "prazo_no_texto": False}
        est = {}
        res = L.ler_sitemap_jsonld(site, rede(web), est, ctx())
        por = {x["pagina_agregador"].rsplit("/", 1)[1]: x for x in res["itens"]}
        self.assertEqual(set(por), {"seculje-lauro", "portalegre-cp", "anater-4"})
        a = por["seculje-lauro"]
        self.assertEqual((a["link_oficial"], a["prazo"], a["financiador"]), (dou, "2026-10-15", "Prefeitura Municipal de Lauro de Freitas"))
        self.assertEqual(a["titulo"], "AVISO DE CHAMAMENTO PÚBLICO Nº 2/2026 - SECULJE")
        b = por["portalegre-cp"]                                   # sem cartão: prazo fica para a fonte oficial, nunca 2024 nem julho
        self.assertEqual((b["link_oficial"], b["prazo"]), ("https://forms.gle/AyXhMZE5YHWD5pMu5", None))
        c = por["anater-4"]                                        # fora da cota de páginas: indício imediato pelo cartão
        self.assertEqual((c["prazo"], c["link_oficial"]), ("2026-10-20", None))
        self.assertEqual(c["financiador"], "Agência Nacional de Assistência Técnica e Extensão Rural")
        self.assertTrue(res["pendente"])
        self.assertEqual(res["diag"]["cartoes_com_prazo"], 2)
        res2 = L.ler_sitemap_jsonld(site, rede(web), est, ctx())     # cartão sem mudança não se repete; a página da ANATER completa o item
        self.assertEqual([x["pagina_agregador"].rsplit("/", 1)[1] for x in res2["itens"]], ["anater-4"])
        self.assertEqual((res2["itens"][0]["prazo"], res2["itens"][0]["link_oficial"]),
                         ("2026-10-20", "https://www.gov.br/anater/pt-br/chamada-4-2026.pdf"))


class LeitorListagem(unittest.TestCase):
    def test_testa_candidatas_e_guarda_a_que_responde(self):
        lista = '<a href="/funarte/pt-br/editais/2026/premio-funarte-x">Prêmio Funarte X 2026</a><a href="/sobre">Sobre</a>'
        item = '<html><head><meta property="og:title" content="Prêmio Funarte X 2026"></head><p>Inscrições até 05/11/2026. Pessoas jurídicas sem fins lucrativos.</p></html>'
        web = Web({"https://www.gov.br/funarte/pt-br/editais-1": (200, lista, {}),
                   "https://www.gov.br/funarte/pt-br/editais/2026/premio-funarte-x": (200, item, {})})
        site = {"id": "funarte", "nome": "Funarte — editais", "motor": "idx-listagens", "leitor": "html_listagem", "proprio": True,
                "listas": ["https://www.gov.br/funarte/pt-br/editais", "https://www.gov.br/funarte/pt-br/editais-1"], "padrao_link": "/editais/20\\d\\d/"}
        est = {}
        res = L.ler_html_listagem(site, rede(web), est, ctx())
        self.assertEqual(est["lista_ok"], "https://www.gov.br/funarte/pt-br/editais-1")
        self.assertEqual(res["itens"][0]["link_oficial"], "https://www.gov.br/funarte/pt-br/editais/2026/premio-funarte-x")
        self.assertEqual(res["itens"][0]["prazo"], "2026-11-05")


class LeitorDadosAbertos(unittest.TestCase):
    def test_siconv_programas_abertos_para_osc(self):
        csv_txt = ("COD_PROGRAMA;NOME_PROGRAMA;DESC_ORGAO_SUP_PROGRAMA;SIT_PROGRAMA;DT_PROG_INI_RECEB_PROP;DT_PROG_FIM_RECEB_PROP;NATUREZA_JURIDICA_PROGRAMA;UF_PROGRAMA\n"
                   "3600020260001;Apoio a projetos esportivos;MINISTERIO DO ESPORTE;DISPONIBILIZADO;01/09/2026;30/10/2026;Organização da Sociedade Civil;GO\n"
                   "3600020260001;Apoio a projetos esportivos;MINISTERIO DO ESPORTE;DISPONIBILIZADO;01/09/2026;30/10/2026;Organização da Sociedade Civil;DF\n"
                   "4100020260002;Obras municipais;MINISTERIO DAS CIDADES;DISPONIBILIZADO;01/09/2026;30/10/2026;Administração Pública Municipal;GO\n"
                   "5000020250009;Programa encerrado;MINISTERIO X;DISPONIBILIZADO;01/01/2026;30/06/2026;Organização da Sociedade Civil;GO\n")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("siconv_programa.csv", csv_txt.encode("utf-8"))
        web = Web({"https://api-publica.transferegov.gestao.gov.br/downloads/dadosgov/siconv_programa.zip": (200, buf.getvalue(), {})})
        site = {"id": "siconv-programas", "nome": "Siconv", "motor": "idx-dados-abertos", "leitor": "siconv_zip",
                "url": "https://api-publica.transferegov.gestao.gov.br/downloads/dadosgov/siconv_programa.zip",
                "pagina": "https://discricionarias.transferegov.sistema.gov.br/voluntarias/programa/ConsultarPrograma/ConsultarPrograma.do"}
        res = L.ler_siconv_zip(site, rede(web), {}, ctx())
        self.assertEqual(len(res["itens"]), 1, res)
        it = res["itens"][0]
        self.assertEqual((it["prazo"], it["financiador"], it["uf"]), ("2026-10-30", "MINISTERIO DO ESPORTE", None))
        self.assertIn("3600020260001", it["titulo"])


class PonteBrasil(unittest.TestCase):
    def test_assinatura_e_via_ponte(self):
        chave = "uma frase longa e aleatoria para a ponte"
        visto = {}

        def ponte_web(req, timeout=0):
            pedido = json.loads(req.data.decode())
            visto.update(pedido)
            ok = pedido["assinatura"] == P.assinar(chave, pedido["ts"], pedido["url"])
            corpo = json.dumps({"ok": ok, "status": 200, "url_final": pedido["url"], "cabecalhos": {"content-type": "text/html"},
                                "corpo_b64": __import__("base64").b64encode(b"<html>ok</html>").decode()})
            return _Resp(req.full_url, 200, corpo.encode(), {})
        with mock.patch.dict("os.environ", {P.ENV_URL: "https://hospedagem.com.br/ponte/ponte.php", P.ENV_CHAVE: chave}):
            with mock.patch("urllib.request.urlopen", ponte_web):
                r = rede(Web({"https://www.tjgo.jus.br/robots.txt": (404, "", {})}))
                resp = r.obter("https://www.tjgo.jus.br/index.php/execucao-penal", via="ponte", checar_robots=False)
        self.assertEqual(resp.saida, "ponte")
        self.assertEqual(resp.texto(), "<html>ok</html>")
        self.assertEqual(visto["url"], "https://www.tjgo.jus.br/index.php/execucao-penal")

    def test_sem_ponte_fora_do_brasil(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(Bloqueio) as c:
                rede(Web({})).obter("https://www.tjgo.jus.br/x", via="ponte", checar_robots=False)
        self.assertEqual(c.exception.tipo, "ponte_indisponivel")

    def test_ponte_vm_recusa_dominio_fora_da_lista_e_assinatura(self):
        import importlib.util, time
        sp = importlib.util.spec_from_file_location("ponte_vm", Path(__file__).resolve().parents[1] / "ponte/ponte_vm.py")
        vm = importlib.util.module_from_spec(sp); sp.loader.exec_module(vm)
        chave, ts = "x" * 30, int(time.time())
        st, r = vm.atender({"url": "https://evil.example.com/", "ts": ts, "assinatura": P.assinar(chave, ts, "https://evil.example.com/")}, chave, ["gov.br"])
        self.assertEqual((st, r["ok"]), (403, False))
        st, r = vm.atender({"url": "https://www.tjgo.jus.br/", "ts": ts, "assinatura": "errada"}, chave, ["jus.br"])
        self.assertEqual(r["erro"], "assinatura inválida")
        st, r = vm.atender({"url": "https://www.tjgo.jus.br/", "ts": ts, "assinatura": P.assinar(chave, ts, "https://www.tjgo.jus.br/")}, chave, ["jus.br"],
                           abrir=lambda req, timeout=0: _Resp("https://www.tjgo.jus.br/", 200, b"oi", {"Content-Type": "text/html"}), checar_ip=lambda h: True)
        self.assertTrue(r["ok"])
        self.assertEqual(__import__("base64").b64decode(r["corpo_b64"]), b"oi")


class RodadaCompleta(unittest.TestCase):
    """Rodada inteira num repositório temporário: catálogo, rotas, duplicata entre indexadores, fluxo, fila e ângulos."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "config").mkdir()
        cat = {"limites": {"itens_por_site_por_rodada": 80, "falhas_para_ponte": 2, "dias_sem_prazo_no_fluxo": 60,
                           "indicios_no_fluxo_max": 1000, "requisicoes_por_rodada": 200,
                           "ordem_do_fluxo": ["GO", "BR", "internacional", "outros_estados"]},
               "ponte": {"escolha": "computador_do_titular", "dias_sem_leitura_para_navegador": 3},
               "agente": {"token_robots": "EldoradoIndexadores", "user_agent": "teste"},
               "motores": {k: {"nome": k, "metodo": "m", "horarios_brt": "x"} for k in
                           ("idx-feeds", "idx-apis", "idx-sitemaps", "idx-listagens", "idx-dados-abertos", "idx-ponte-brasil", "idx-assistido")},
               "sites": [
                   {"id": "farolcultural", "nome": "Farol", "motor": "idx-apis", "leitor": "farol_api", "url": "https://farolcultural.art/api/v1/editais",
                    "prioridade": "P1", "rota": "nuvem", "cadencia_horas": 6, "areas": ["cultura"]},
                   {"id": "capitaai", "nome": "CapitaAI", "motor": "idx-sitemaps", "leitor": "sitemap_jsonld", "prefixo": "/captacao/",
                    "url": "https://capitaai.com.br/sitemap-captacao.xml", "prioridade": "P1", "rota": "nuvem", "cadencia_horas": 3},
                   {"id": "portal-geo", "nome": "Portal que recusa IP estrangeiro", "motor": "idx-listagens", "leitor": "html_listagem",
                    "listas": ["https://portal.go.gov.br/editais"], "prioridade": "P2", "rota": "nuvem", "cadencia_horas": 1},
                   {"id": "prosas", "nome": "Prosas", "motor": "idx-assistido", "leitor": "assistido", "url": "https://prosas.com.br/x",
                    "rota": "assistida", "motivo": "robots", "prioridade": "P1", "angulo_piloto": "procure o financiador fora do Prosas",
                    "rota_indireta": {"site": "capitaai", "pagina": "https://capitaai.com.br/editais-abertos/prosas"}},
               ]}
        (self.tmp / "config/indexadores.json").write_text(json.dumps(cat), encoding="utf-8")
        (self.tmp / "estado/agregadores").mkdir(parents=True)
        antigo = {"itens": [{"id": "agr-antigo000001", "fonte": "capitaai", "titulo": "Edital antigo da CapitaAI ainda aberto",
                             "pagina_agregador": "https://capitaai.com.br/captacao/antigo", "link_oficial": "https://orgao.gov.br/antigo",
                             "prazo": "2026-12-01", "visto_em": "2026-09-28", "primeiro_visto": "2026-09-20"}]}
        (self.tmp / "estado/agregadores/itens.json").write_text(json.dumps(antigo), encoding="utf-8")
        alvo = {k: self.tmp / v for k, v in {"CATALOGO": "config/indexadores.json", "SENSORES": "config/sensores.json",
                                              "ESTADO": "estado/indexadores/estado.json", "ACERVO": "estado/indexadores/indicios.json",
                                              "FILA": "estado/indexadores/fila_assistida.json", "DIARIO": "estado/indexadores/diario.json",
                                              "ANGULOS": "estado/indexadores/angulos_piloto.json", "FLUXO": "estado/agregadores/itens.json",
                                              "PAINEL": "docs/dados/indexadores.json", "ESQUADRA": "estado/esquadra.json",
                                              "DELTAS_BRASIL": "entrada_manual/indexadores/deltas"}.items()}
        for k, v in alvo.items():
            p = mock.patch.object(M, k, v); p.start(); self.addCleanup(p.stop)
        e = mock.patch.dict("os.environ", {}, clear=True); e.start(); self.addCleanup(e.stop)

    def web(self):
        farol = {"success": True, "meta": {"total": 3, "total_pages": 1}, "data": [
            {"slug": "sobral-2026", "titulo": "Seleção de projetos culturais de Sobral", "instituicao_nome": "MUNICIPIO DE SOBRAL", "pais": "BR",
             "estado": "CE", "data_fim_inscricao": "2026-10-20", "url_original": "https://pncp.gov.br/app/editais/07598634000137/2026/137",
             "resumo": "coletivos e associações"},
            {"slug": "residencia-berlim", "titulo": "Residência artística em Berlim", "instituicao_nome": "Haus X", "pais": "DE",
             "data_fim_inscricao": "2026-11-01", "url_original": "https://hausx.de/call", "resumo": "residency for German artists"},
            {"slug": "bolsa-doutorado", "titulo": "Bolsas de doutorado em artes", "instituicao_nome": "Universidade", "pais": "BR",
             "data_fim_inscricao": "2026-11-10", "url_original": "https://univ.br/bolsas", "resumo": "bolsas de doutorado"}]}
        pagina_capitaai = ('<html><script type="application/ld+json">{"@type":"Article","headline":"Edital Sobral 2026: projetos culturais",'
                           '"description":"Coletivos e associações de Sobral captam até 20/10.","datePublished":"2026-09-20T05:00:00Z"}</script>'
                           '<a href="https://www.sobral.ce.gov.br/">Prefeitura</a>'
                           '<a href="https://pncp.gov.br/app/editais/07598634000137/2026/137">Edital no PNCP</a></html>')
        sm = "<urlset><url><loc>https://capitaai.com.br/captacao/sobral</loc><lastmod>2026-10-01T05:00:00Z</lastmod></url></urlset>"
        return Web({"https://farolcultural.art/api/v1/editais?*": (200, json.dumps(farol), {}),
                    "https://capitaai.com.br/sitemap-captacao.xml": (200, sm, {}),
                    "https://capitaai.com.br/captacao/sobral": (200, pagina_capitaai, {}),
                    "https://portal.go.gov.br/robots.txt": (403, "Forbidden", {}),
                    "https://portal.go.gov.br/editais": (403, "Forbidden", {})})

    def test_rodada(self):
        web = self.web()
        agora = datetime(2026, 10, 2, 12, 13, tzinfo=timezone.utc)
        r1 = M.rodada(agora=agora, rede=rede(web))
        fluxo = json.loads((self.tmp / "estado/agregadores/itens.json").read_text(encoding="utf-8"))
        ids = {x["id"]: x for x in fluxo["itens"]}
        # o mesmo edital no Farol e no CapitaAI é UM indício com as duas fontes
        sobral = [x for x in fluxo["itens"] if "pncp.gov.br/app/editais/07598634000137/2026/137" in (x.get("link_oficial") or "")]
        self.assertEqual(len(sobral), 1)
        self.assertEqual(set(sobral[0]["fontes"]), {"farolcultural", "capitaai"})
        # o item do motor antigo foi migrado com o mesmo id e a data em que apareceu
        self.assertIn("agr-antigo000001", ids)
        self.assertEqual(ids["agr-antigo000001"]["primeiro_visto"], "2026-09-20")
        # fora do fluxo (mas no acervo): estrangeiro sem aplicação ao Brasil e bolsa de doutorado
        self.assertFalse(any("Berlim" in x["titulo"] for x in fluxo["itens"]))
        self.assertFalse(any("doutorado" in x["titulo"] for x in fluxo["itens"]))
        self.assertEqual(fluxo["fora_do_fluxo"]["nao_se_aplica_ao_brasil"], 1)
        self.assertEqual(fluxo["fora_do_fluxo"]["fora_do_perfil"], 1)
        # o portal que recusa IP estrangeiro: 1ª falha conta; na 2ª sobe para a ponte
        est = json.loads((self.tmp / "estado/indexadores/estado.json").read_text(encoding="utf-8"))
        self.assertEqual(est["sites"]["portal-geo"]["falhas_seguidas"], 1)
        M.rodada(agora=datetime(2026, 10, 2, 15, 13, tzinfo=timezone.utc), rede=rede(web))
        est = json.loads((self.tmp / "estado/indexadores/estado.json").read_text(encoding="utf-8"))
        self.assertEqual(est["sites"]["portal-geo"]["rota"], "ponte")
        painel = json.loads((self.tmp / "docs/dados/indexadores.json").read_text(encoding="utf-8"))
        # 02/10: um motor por site — o site levado à ponte aparece no PRÓPRIO motor, com a rota "ponte"
        _mid = next(x["motor"] for x in painel["sites"] if x["id"] == "portal-geo")
        self.assertIn("ponte", next(m for m in painel["motores"] if m["id"] == _mid).get("rotas", []))
        # Prosas: na fila assistida, com a rota indireta, e o Piloto ganha o ângulo de busca
        fila = json.loads((self.tmp / "estado/indexadores/fila_assistida.json").read_text(encoding="utf-8"))
        self.assertEqual(fila["itens"][0]["id"], "prosas")
        self.assertEqual(fila["itens"][0]["rota_indireta"]["site"], "capitaai")
        ang = json.loads((self.tmp / "estado/indexadores/angulos_piloto.json").read_text(encoding="utf-8"))
        self.assertEqual(ang["angulos"][0]["id"], "idx-prosas")
        self.assertFalse(any("prosas.com.br" in u for u, _ in web.pedidos))     # o robô nunca tocou o Prosas
        # diário da família (calendário do painel)
        diario = json.loads((self.tmp / "estado/indexadores/diario.json").read_text(encoding="utf-8"))
        self.assertEqual(diario["idx-apis"]["2026-10-02"]["cor"], "amarelo")
        self.assertGreaterEqual(r1["no_fluxo"], 2)

    def test_ponte_pelo_computador_e_navegador_apos_3_dias(self):
        """Decisão do titular (02/10/2026): a ponte é o computador dele. A nuvem não tenta o site da rota 'ponte' — espera
        a coleta no computador; se o computador não ler por 3 dias, o site entra também na fila do navegador."""
        web = self.web()
        for h in (12, 15, 18):
            M.rodada(agora=datetime(2026, 10, 2, h, 13, tzinfo=timezone.utc), rede=rede(web))
        est = json.loads((self.tmp / "estado/indexadores/estado.json").read_text(encoding="utf-8"))
        self.assertEqual((est["sites"]["portal-geo"]["rota"], est["sites"]["portal-geo"]["aguardando_ponte_desde"]), ("ponte", "2026-10-02"))
        n = len(web.pedidos)
        M.rodada(agora=datetime(2026, 10, 5, 18, 13, tzinfo=timezone.utc), rede=rede(web))
        self.assertFalse(any("portal.go.gov.br" in u for u, _ in web.pedidos[n:]))     # a nuvem não insiste: é a vez do computador
        fila = json.loads((self.tmp / "estado/indexadores/fila_assistida.json").read_text(encoding="utf-8"))
        g = next(x for x in fila["itens"] if x["id"] == "portal-geo")
        self.assertIn("computador do titular", g["motivo"])
        painel = json.loads((self.tmp / "docs/dados/indexadores.json").read_text(encoding="utf-8"))
        self.assertEqual(painel["ponte"]["escolha"], "computador_do_titular")
        self.assertIn("portal-geo", painel["ponte"]["sites_na_ponte"])
        # a coleta no computador lê o site com o IP de casa e tira a espera
        casa = Web({"https://portal.go.gov.br/editais": (200, '<a href="/editais/2026/edital-01-fomento">Edital 01/2026 de fomento a OSC</a>', {}),
                    "https://portal.go.gov.br/editais/2026/edital-01-fomento": (200, "<h1>Edital 01/2026</h1><p>Inscrições até 30/11/2026.</p>", {})})
        with mock.patch.dict("os.environ", {"ELDORADO_LOCAL_BR": "1"}):
            r = M.rodada(agora=datetime(2026, 10, 5, 19, 13, tzinfo=timezone.utc), rede=rede(casa, local_brasil=True))
        self.assertEqual(r["rota_da_execucao"], "ponte")
        est = json.loads((self.tmp / "estado/indexadores/estado.json").read_text(encoding="utf-8"))
        self.assertNotIn("aguardando_ponte_desde", est["sites"]["portal-geo"])
        self.assertTrue(est["ultima_coleta_brasil"]["em"].startswith("2026-10-05"))

    def test_computador_envia_delta_e_a_nuvem_aplica_e_apaga(self):
        """O computador do titular grava a rodada como ARQUIVO NOVO de delta; a nuvem aplica os deltas em ordem sobre o
        main mais novo, antes do seu, e apaga os arquivos — sem conflito de git e sem perder o que cada um leu."""
        web = self.web()
        for h in (12, 15, 18):
            M.rodada(agora=datetime(2026, 10, 2, h, 13, tzinfo=timezone.utc), rede=rede(web))
        pasta = self.tmp / "entrada_manual/indexadores/deltas"; pasta.mkdir(parents=True)
        arq = pasta / "brasil-20261002-191000.json"
        casa = Web({"https://portal.go.gov.br/editais": (200, '<a href="/editais/2026/edital-02-fomento">Edital 02/2026 de fomento a OSC</a>', {}),
                    "https://portal.go.gov.br/editais/2026/edital-02-fomento": (200, "<h1>Edital 02/2026</h1><p>Inscrições até 30/11/2026.</p>", {})})
        # no computador: a rodada grava o delta (e os arquivos de estado de lá são descartados pelo coleta_brasil.py)
        copia = {f: f.read_bytes() for f in (self.tmp / "estado").rglob("*.json")} | {f: f.read_bytes() for f in (self.tmp / "docs").rglob("*.json")}
        with mock.patch.dict("os.environ", {"ELDORADO_LOCAL_BR": "1"}):
            M.rodada(agora=datetime(2026, 10, 2, 22, 10, tzinfo=timezone.utc), rede=rede(casa, local_brasil=True), delta_em=arq)
        for f, b in copia.items():
            f.write_bytes(b)
        d = json.loads(arq.read_text(encoding="utf-8"))
        self.assertEqual((d["rota"], set(d["sites"])), ("ponte", {"portal-geo"}))
        self.assertTrue(all(h == "portal.go.gov.br" for h in d["robots"]))         # só o cache do que ele leu
        (pasta / "brasil-20261002-000000.json").write_text('{"versao": 9}', encoding="utf-8")   # lixo: recusado e apagado
        r = M.aplicar_deltas_do_brasil(remover=True)
        self.assertEqual((r["aplicados"], [x["arquivo"] for x in r["recusados"]]), (["brasil-20261002-191000.json"], ["brasil-20261002-000000.json"]))
        self.assertEqual(list(pasta.glob("*.json")), [])
        fluxo = json.loads((self.tmp / "estado/agregadores/itens.json").read_text(encoding="utf-8"))
        self.assertTrue(any("Edital 02/2026" in x["titulo"] for x in fluxo["itens"]))
        est = json.loads((self.tmp / "estado/indexadores/estado.json").read_text(encoding="utf-8"))
        self.assertNotIn("aguardando_ponte_desde", est["sites"]["portal-geo"])
        self.assertIn("ultima_coleta_brasil", est)

    def test_delta_reaplicado_nao_apaga_o_que_outro_gravou(self):
        web = self.web()
        delta_arq = self.tmp / "delta.json"
        M.rodada(agora=datetime(2026, 10, 2, 12, 13, tzinfo=timezone.utc), rede=rede(web), delta_em=delta_arq)
        # outro processo (coleta no Brasil) grava um indício no meio tempo
        acervo = json.loads((self.tmp / "estado/indexadores/indicios.json").read_text(encoding="utf-8"))
        acervo["itens"]["agr-brasil00000001"] = {"id": "agr-brasil00000001", "fonte": "portal-geo", "titulo": "Edital lido pelo Brasil",
                                                "pagina_agregador": "https://portal.go.gov.br/e/1", "prazo": "2026-12-01",
                                                "primeiro_visto": "2026-10-02", "visto_em": "2026-10-02", "pais": "BR", "perfil": "osc"}
        (self.tmp / "estado/indexadores/indicios.json").write_text(json.dumps(acervo), encoding="utf-8")
        M.aplicar(json.loads(delta_arq.read_text(encoding="utf-8")))
        fluxo = json.loads((self.tmp / "estado/agregadores/itens.json").read_text(encoding="utf-8"))
        self.assertIn("agr-brasil00000001", {x["id"] for x in fluxo["itens"]})


class OrdemDoFluxo(unittest.TestCase):
    def test_goias_brasil_internacional_outros_estados_e_limite(self):
        """Decisão do titular (02/10/2026): até 1.000 indícios — Goiás, Brasil, internacional e, por último, outros estados;
        dentro do grupo, o prazo mais próximo primeiro e o sem prazo no fim."""
        sites = {"farol": {}, "fundsforngos-brasil": {"internacional": True}}
        b = {"perfil": "osc", "primeiro_visto": "2026-10-01", "visto_em": "2026-10-02", "fonte": "farol", "pais": "BR"}
        itens = {"sp": dict(b, id="sp", titulo="Edital de São Paulo", uf="SP", prazo="2026-10-03"),
                 "int": dict(b, id="int", fonte="fundsforngos-brasil", pais=None, titulo="Grant for Brazilian NGOs", prazo="2026-10-09"),
                 "us": dict(b, id="us", pais="US", titulo="Call open to organizations in Brazil", prazo="2026-10-04"),
                 "br": dict(b, id="br", titulo="Edital nacional de fomento", prazo="2026-11-30"),
                 "br2": dict(b, id="br2", titulo="Chamada nacional sem prazo publicado"),
                 "go": dict(b, id="go", titulo="Edital de Goiás", uf="GO", prazo="2026-12-20"),
                 "go2": dict(b, id="go2", titulo="Chamamento de Goiânia", uf="GO", prazo="2026-10-10"),
                 "mg": dict(b, id="mg", titulo="Edital de Minas", uf="MG", prazo="2026-10-02")}
        lim = {"ordem_do_fluxo": ["GO", "BR", "internacional", "outros_estados"], "indicios_no_fluxo_max": 1000}
        entrada, fora = M.entrada_do_fluxo({"itens": itens}, sites, HOJE, lim)
        self.assertEqual([x["id"] for x in entrada], ["go2", "go", "br", "br2", "us", "int", "mg", "sp"])
        self.assertEqual(M.por_grupo(entrada, sites), {"GO": 2, "BR": 2, "internacional": 2, "outros_estados": 2})
        entrada, fora = M.entrada_do_fluxo({"itens": itens}, sites, HOJE, dict(lim, indicios_no_fluxo_max=6))
        self.assertEqual([x["id"] for x in entrada][-1], "int")                  # o corte cai sobre os outros estados
        self.assertEqual(fora["acima_do_limite"], 2)
        self.assertEqual(len(M.entrada_do_fluxo({"itens": itens}, sites, HOJE, {})[0]), 8)   # padrão: 1.000

    def test_catalogo_registra_as_decisoes(self):
        cat = json.loads((Path(__file__).resolve().parents[1] / "config/indexadores.json").read_text(encoding="utf-8"))
        self.assertEqual(cat["limites"]["indicios_no_fluxo_max"], 1000)
        self.assertEqual(cat["limites"]["ordem_do_fluxo"], ["GO", "BR", "internacional", "outros_estados"])
        self.assertEqual(cat["ponte"]["escolha"], "computador_do_titular")
        sites = {s["id"]: s for s in cat["sites"]}
        self.assertNotIn("se_autorizado", sites["prosas"])                       # sem pedido de licença
        self.assertEqual(len(sites["prosas"]["caminhos_indiretos"]), 3)
        self.assertEqual(sites["capitaai"]["listas_fixas"], {"https://capitaai.com.br/editais-abertos/prosas": "prosas"})


class RotaIndiretaProsas(unittest.TestCase):
    def test_listagem_do_prosas_no_capitaai_em_toda_rodada(self):
        base = "https://capitaai.com.br"
        card = ('<a href="/captacao/potencias-negras"><div><h3>EDITAL SMCT Nº 22/2026 - POTÊNCIAS NEGRAS</h3>'
                '<p>Secretaria Municipal de Cultura</p><p><span>Aceita:</span> organizações da sociedade civil</p>'
                '<div><span>Prazo: <!-- -->30/10/2026 (28d)</span></div></div></a>')
        web = Web({f"{base}/sitemap-captacao.xml": (200, "<urlset></urlset>", {}),
                   f"{base}/sitemap-editais.xml": (200, f"<urlset><url><loc>{base}/editais-abertos/prosas</loc></url>"
                                                        f"<url><loc>{base}/editais-abertos/cultura</loc></url></urlset>", {}),
                   f"{base}/editais-abertos/prosas": (200, f"<html>{card}</html>", {}),
                   f"{base}/editais-abertos/cultura": (200, "<html></html>", {})})
        site = {"id": "capitaai", "nome": "CapitaAI", "motor": "idx-sitemaps", "leitor": "sitemap_jsonld", "prefixo": "/captacao/",
                "url": f"{base}/sitemap-captacao.xml", "listas_sitemap": f"{base}/sitemap-editais.xml", "listas_prefixo": "/editais-abertos",
                "listas_por_rodada": 1, "prazo_no_texto": False, "listas_fixas": {f"{base}/editais-abertos/prosas": "prosas"}}
        est = {}
        res = L.ler_sitemap_jsonld(site, rede(web), est, ctx())
        self.assertEqual(len(res["itens"]), 1)
        x = res["itens"][0]
        self.assertEqual((x["rota_indireta_de"], x["prazo"]), ("prosas", "2026-10-30"))
        self.assertEqual(res["diag"]["cartoes_rota_indireta_prosas"], 1)
        self.assertNotIn(f"{base}/editais-abertos/prosas", est["listas"])          # fora do rodízio: é lida sempre
        for _ in range(2):
            L.ler_sitemap_jsonld(site, rede(web), est, ctx())
        lidas = [u for u, _ in web.pedidos if u.endswith("/editais-abertos/prosas")]
        self.assertEqual(len(lidas), 3)                                           # uma vez em cada rodada
        self.assertFalse(any("prosas.com.br" in u for u, _ in web.pedidos))       # o robô nunca toca o Prosas
        cat = {"sites": [{"id": "prosas", "nome": "Prosas", "url": "https://prosas.com.br/x", "rota": "assistida", "prioridade": "P1",
                          "caminhos_indiretos": ["a", "b", "c"]}]}
        fila = M.montar_fila(cat, {}, {"prosas": ("assistida", "robots")}, HOJE, {"itens": {x["id"]: x}})
        self.assertEqual(fila["itens"][0]["cobertos_pela_rota_indireta"], 1)


class ColetaAssistida(unittest.TestCase):
    def test_importa_captura_do_prosas_uma_vez(self):
        tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, tmp, True)
        entrada = tmp / "entrada"; entrada.mkdir()
        cap = {"eldorado": "indicios-v1", "capturado_em": "2026-10-02T13:00:00Z", "paginas": [{"url": "https://prosas.com.br/selecao/widgets/listagem-editais",
               "host": "prosas.com.br", "itens": [{"titulo": "EDITAL SMCT Nº 22/2026 - POTÊNCIAS NEGRAS", "url": "https://prosas.com.br/editais/18917",
                                                   "prazo": "2026-10-20", "financiador": "SECRETARIA MUNICIPAL DE CULTURA DE UBERLÂNDIA/MG"}]}]}
        (entrada / "indicios-prosas.com.br-2026-10-02.json").write_text(json.dumps(cap), encoding="utf-8")
        (entrada / "lixo.json").write_text("{}", encoding="utf-8")
        from src.indexadores import assistida as A
        cat = {"sites": [{"id": "prosas", "nome": "Prosas", "motor": "idx-assistido", "url": "https://prosas.com.br/selecao/widgets/listagem-editais"}]}
        with mock.patch.object(A, "ENTRADA", entrada), mock.patch.object(A, "catalogo", lambda: cat), \
                mock.patch.object(A, "ESTADO", tmp / "estado.json"):
            r = A.importar(hoje=HOJE, gravar=False)
            self.assertEqual(r["itens"], 1)
            self.assertEqual(len(r["recusados"]), 1)
            it = r["delta"]["itens"][0]
            self.assertEqual((it["fonte"], it["link_oficial"], it["rota"], it["uf"]), ("prosas", "https://prosas.com.br/editais/18917", "assistida", "MG"))
            (tmp / "estado.json").write_text(json.dumps({"importados": r["delta"]["importados"]}), encoding="utf-8")
            self.assertEqual(A.importar(hoje=HOJE, gravar=False)["itens"], 0)       # o mesmo arquivo não entra de novo


class Catalogo(unittest.TestCase):
    def test_catalogo_real_consistente(self):
        raiz = Path(__file__).resolve().parents[1]
        cat = json.loads((raiz / "config/indexadores.json").read_text(encoding="utf-8"))
        ids = [s["id"] for s in cat["sites"]]
        self.assertEqual(len(ids), len(set(ids)))
        agregados = (cat.get("agregados") or {}).get("motores") or {}      # 03/10: sites agregados a um motor regular
        for s in cat["sites"]:
            if s["motor"] in agregados:
                self.assertIn(s["id"], {a["site"] for a in agregados[s["motor"]]}, s["id"])
            else:
                self.assertIn(s["motor"], cat["motores"], s["id"])
            self.assertTrue(s["leitor"] in L.LEITORES or s["leitor"] == "assistido", s["id"])
            if s["leitor"] == "delegado":
                self.assertTrue(s.get("delegado_a"))
        agenda = json.loads((raiz / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        for mid in cat["motores"]:
            self.assertIn(mid, agenda)
        for legado in ("plat-observatorio-3setor", "plat-abcr", "plat-mapa-osc"):
            self.assertEqual(agenda[legado]["dias"], "inativo")
            self.assertTrue(agenda[legado]["agregado_a"].startswith("site-"))      # 02/10: o motor do próprio site
        inv = {f["id"]: f for f in json.loads((raiz / "config/investigacao.json").read_text(encoding="utf-8"))["fontes"]}
        self.assertFalse(inv["observatorio-3setor"]["ativa"])
        self.assertFalse(inv["abcr"]["ativa"])


class LeitorProsasAutorizado(unittest.TestCase):
    def test_so_le_com_autorizacao_escrita(self):
        api = {"data": [{"id": "18917", "type": "oportunidade", "attributes": {"id": 18917, "nome": "EDITAL SMCT Nº 22/2026 - POTÊNCIAS NEGRAS",
                         "data_final_inscricoes": "2026-10-20T17:00:00.000-03:00", "prazo": "definido"},
                         "relationships": {"incentivador": {"data": {"id": "1068", "type": "incentivador"}}, "area_interesses": {"data": [{"id": "6", "type": "area_interesse"}]}}}],
               "included": [{"id": "1068", "type": "incentivador", "attributes": {"nome_fantasia": "SECRETARIA MUNICIPAL DE CULTURA DE UBERLÂNDIA/MG"}},
                            {"id": "6", "type": "area_interesse", "attributes": {"nome": "Cultura e Artes"}}],
               "links": {"first": 1, "last": 1, "total": 1}}
        web = Web({"https://prosas.com.br/robots.txt": (200, ROBOTS_PROSAS, {}),
                   "https://prosas.com.br/selecao/api/v2/publics/oportunidades?*": (200, json.dumps(api), {})})
        site = {"id": "prosas", "nome": "Prosas", "motor": "idx-apis", "leitor": "prosas_api", "url": "https://prosas.com.br/selecao/api/v2/publics/oportunidades"}
        sem = L.ler_prosas_api(site, rede(web), {}, ctx())
        self.assertEqual((sem["itens"], sem["falhas"][0]["tipo"]), ([], "robots"))
        com = L.ler_prosas_api(dict(site, autorizacao={"por": "Prosas", "em": "2026-10-10", "documento": "e-mail de 10/10/2026"}), rede(web), {}, ctx())
        it = com["itens"][0]
        self.assertEqual((it["link_oficial"], it["prazo"], it["uf"]), ("https://prosas.com.br/editais/18917", "2026-10-20", "MG"))
        self.assertIn("cultura e artes", it["areas"])
        self.assertFalse(any(u.endswith("/robots.txt") for u, _ in web.pedidos))


if __name__ == "__main__":
    unittest.main()
