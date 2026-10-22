"""As cinco formas de descoberta, com respostas simuladas (toda busca passa pela escada; aqui, por uma função falsa)."""
import json

from eldorado.motores.acesso.escada import Resposta
from eldorado.motores.descoberta import arquivos_web, dados_abertos, estrutura_site, vigilancia
from eldorado.motores.descoberta.metabusca import Metabusca


def falso(paginas):
    def buscar(url):
        for chave, corpo in paginas.items():
            if url.startswith(chave):
                if isinstance(corpo, Exception):
                    raise corpo
                return Resposta(url, 200, corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode(), "")
        raise AssertionError(f"pedido inesperado: {url}")
    return buscar


def test_mapa_do_site_com_indice_aninhado():
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
    b = falso({"https://s/sitemap.xml": f'<sitemapindex {ns}><sitemap><loc>https://s/editais.xml</loc></sitemap></sitemapindex>'.encode(),
               "https://s/editais.xml": f'<urlset {ns}><url><loc>https://s/edital-de-fomento-2026</loc><lastmod>2026-10-01</lastmod></url></urlset>'.encode()})
    p = estrutura_site.mapa_do_site(b, "https://s/sitemap.xml")
    assert [(x.link, x.data, x.titulo) for x in p] == [("https://s/edital-de-fomento-2026", "2026-10-01", "edital de fomento 2026")]


def test_feed_rss():
    rss = b"<?xml version='1.0'?><rss version='2.0'><channel><item><title>Edital aberto</title><link>https://s/e1</link><pubDate>Mon, 19 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"
    p = estrutura_site.feed(falso({"https://s/feed": rss}), "https://s/feed")
    assert p[0].titulo == "Edital aberto" and p[0].link == "https://s/e1" and p[0].data


def test_wordpress_e_links():
    wp = [{"title": {"rendered": "Chamamento <b>público</b> 3/2026"}, "link": "https://s/c3", "date": "2026-10-01T10:00:00", "excerpt": {"rendered": "<p>Fomento</p>"}}]
    p = estrutura_site.wordpress(falso({"https://s/wp-json/wp/v2/posts": wp}), "https://s/wp-json/wp/v2/posts", busca="edital fomento")
    assert p[0].titulo == "Chamamento público 3/2026" and p[0].resumo == "Fomento"
    html = b'<html><body><a href="/e.pdf">Edital</a><a href="https://outro.org/x">Fora</a><a href="#x">ancora</a></body></html>'
    assert [(x.link, x.titulo) for x in estrutura_site.links(falso({"https://s/": html}), "https://s/pagina")] == [("https://s/e.pdf", "Edital")]


def test_ckan_e_api_oficial():
    ck = {"success": True, "result": {"results": [{"title": "Editais de fomento 2026", "name": "editais", "resources": [{"url": "https://d/e.csv"}],
                                                    "organization": {"title": "Secult"}, "metadata_modified": "2026-10-01"}]}}
    p = dados_abertos.ckan(falso({"https://dados.gov.br/api": ck}), "https://dados.gov.br", "fomento")
    assert p[0].link == "https://d/e.csv" and p[0].extra["organizacao"] == "Secult"
    api = {"data": [{"objeto": "Chamamento para OSC", "linkSistemaOrigem": "https://pncp/1", "dataEncerramentoProposta": "2026-11-30", "uf": "GO"}]}
    p = dados_abertos.api_oficial(falso({"https://pncp/api": api}), "https://pncp/api",
                                  {"itens": "data[*]", "titulo": "objeto", "link": "linkSistemaOrigem", "data": "dataEncerramentoProposta", "uf": "uf"})
    assert (p[0].titulo, p[0].link, p[0].data, p[0].extra["uf"]) == ("Chamamento para OSC", "https://pncp/1", "2026-11-30", "GO")


def test_metabusca_rota_que_falha_descansa_e_a_proxima_assume():
    relogio = [0.0]
    b = falso({"http://searx": ConnectionError("fora do ar"),
               "https://api.marginalia.nu": {"results": [{"title": "Edital de fomento", "url": "https://m/1", "description": "x"}]}})
    m = Metabusca(b, searxng="http://searx", usar_ddgs=False, relogio=lambda: relogio[0])
    pistas, relato = m.consultar("edital fomento")
    assert pistas[0].link == "https://m/1" and any("searxng: falhou" in r for r in relato)
    _, relato2 = m.consultar("edital fomento")
    assert any("searxng: descansando" in r for r in relato2)
    relogio[0] += 4000
    _, relato3 = m.consultar("edital fomento")
    assert any("searxng: falhou" in r for r in relato3)                                  # o descanso terminou: tentou de novo


def test_indice_da_wayback():
    cdx = [["urlkey", "timestamp", "original", "mimetype"], ["k", "20250101", "https://s/edital-2025.pdf", "application/pdf"]]
    p = arquivos_web.indice_wayback(falso({"https://web.archive.org/cdx": cdx}), "s")
    assert p[0].link == "https://s/edital-2025.pdf" and p[0].extra["tipo"] == "application/pdf"


def test_assinatura_ignora_o_que_muda_a_toda_hora():
    a = vigilancia.assinatura(b"<html><body><p>Edital 3/2026</p><p>Acessado em 22/10/2026 10:15</p><script>var t=1</script></body></html>")
    b = vigilancia.assinatura(b"<html><body><p>Edital 3/2026</p><p>Acessado em 23/10/2026 18:40</p><script>var t=99</script></body></html>")
    c = vigilancia.assinatura(b"<html><body><p>Edital 4/2026</p><p>Acessado em 23/10/2026 18:40</p></body></html>")
    assert a == b != c and vigilancia.mudou(a, c) and not vigilancia.mudou(a, b)
    assert vigilancia.assinatura(b"<html><body><div id='e'>X</div><div>muda</div></body></html>", "#e") == \
        vigilancia.assinatura(b"<html><body><div id='e'>X</div><div>mudou outra coisa</div></body></html>", "#e")
