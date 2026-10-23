"""O motor padrão: as habilidades de descoberta e leitura do plano (23/10/2026)."""
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from eldorado.motores.descoberta import dados_abertos
from eldorado.motores.descoberta.estrutura_site import _regiao, links, mapa_completo


class R:
    def __init__(self, c, tipo="text/html"):
        self.conteudo, self.tipo = c, tipo


def test_api_em_xml_vira_dados_consultaveis():
    pytest.importorskip("xmltodict")
    xml = b'<?xml version="1.0"?><Materias><Materia codigo="1"><Ementa>Fundo do Terceiro Setor</Ementa></Materia><Materia codigo="2"><Ementa>Outra</Ementa></Materia></Materias>'
    doc = dados_abertos.carregar_json(lambda _u: R(xml), "https://x/api")
    p = dados_abertos.pistas_da_api(doc, {"itens": "Materias.Materia", "titulo": "Ementa", "link": "codigo"}, "senado")
    assert [x.titulo for x in p] == ["Fundo do Terceiro Setor", "Outra"]


def test_seletor_xpath_e_seletor_adaptavel(tmp_path, monkeypatch):
    pytest.importorskip("scrapling")
    monkeypatch.setenv("ELDORADO_DADOS", str(tmp_path))
    (tmp_path / "motores").mkdir()
    antes = '<html><body><nav><a href="/x">Menu</a></nav><div id="editais" class="lista"><a href="/e1">Edital 1</a><a href="/e2">Edital 2</a></div></body></html>'
    assert "Edital 1" in _regiao(antes, "https://site/editais", "xpath://div[@id='editais']")
    assert "Edital 1" in _regiao(antes, "https://site/editais", "#editais")                       # guarda a impressão digital
    depois = antes.replace('id="editais"', 'id="lista-de-editais"')                                # o site mudou o id
    regiao = _regiao(depois, "https://site/editais", "#editais")
    assert regiao and "Edital 1" in regiao and "Menu" not in regiao                               # reencontrada pelo Scrapling
    p = links(lambda _u: R(depois.encode()), "https://site/editais", seletor="#editais")
    assert [x.titulo for x in p] == ["Edital 1", "Edital 2"]


def test_mapa_completo_pela_escada():
    pytest.importorskip("usp")
    paginas = {"/robots.txt": b"Sitemap: http://127.0.0.1:{p}/sitemap_index.xml",
               "/sitemap_index.xml": b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>http://127.0.0.1:{p}/s1.xml</loc></sitemap></sitemapindex>',
               "/s1.xml": b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>http://127.0.0.1:{p}/edital-7-2026</loc><lastmod>2026-10-10</lastmod></url></urlset>'}
    pedidos = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            c = paginas.get(self.path)
            self.send_response(200 if c else 404)
            self.end_headers()
            self.wfile.write(c.replace(b"{p}", str(srv.server_address[1]).encode()) if c else b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        import urllib.request
        def buscar(u):
            pedidos.append(u)
            with urllib.request.urlopen(u) as r:
                return R(r.read())
        p = mapa_completo(buscar, f"http://127.0.0.1:{srv.server_address[1]}/")
    finally:
        srv.shutdown()
    assert [x.link.rsplit("/", 1)[-1] for x in p] == ["edital-7-2026"] and p[0].data == "2026-10-10"
    assert any(u.endswith("/robots.txt") for u in pedidos)                                        # tudo pela escada
