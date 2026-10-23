"""O mapa do site original (titular, 23/10/2026): as URLs novas do livro no site da origem confirmada."""
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from conftest import AGORA, ev

from eldorado.base.cerebro.originais import livros_com_origem
from eldorado.motores.canal.motor import MotorCanal
from eldorado.motores.descoberta import mapa_original as M

RECENTE, ANTIGA = (date.today() - timedelta(days=5)).isoformat(), "2024-03-01"
URLS = {"/editais/edital-de-chamamento-7-2026-fundo-de-apoio-a-cultura-anapolina/": RECENTE,
        "/wp-content/uploads/2026/10/regulamento-fundo-anapolina.pdf": RECENTE,
        "/noticias/festa-junina-no-parque/": RECENTE,
        "/editais/edital-3-2024-fundo-de-apoio-a-cultura-anapolina/": ANTIGA}


@pytest.fixture
def site():
    urls = dict(URLS)
    acessos = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            acessos.append(self.path)
            b = f"http://127.0.0.1:{srv.server_address[1]}"
            if self.path == "/robots.txt":
                corpo, tipo = f"User-agent: *\nSitemap: {b}/sitemap_index.xml\n".encode(), "text/plain"
            elif self.path == "/sitemap_index.xml":
                corpo, tipo = (f'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                               f'<sitemap><loc>{b}/post-sitemap.xml</loc></sitemap></sitemapindex>').encode(), "application/xml"
            elif self.path == "/post-sitemap.xml":
                corpo = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                         "".join(f"<url><loc>{b}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls.items()) + "</urlset>").encode()
                tipo = "application/xml"
            elif self.path.startswith(("/editais/", "/noticias/", "/fundo")):
                corpo, tipo = ("<html><body><main><h1>Fundo de Apoio à Cultura Anapolina</h1><p>" + "Edital de chamamento público. " * 10 +
                               "</p></main></body></html>").encode(), "text/html; charset=utf-8"
            else:
                corpo, tipo = None, None
            self.send_response(200 if corpo else 404)
            self.send_header("Content-Type", tipo or "text/plain")
            self.end_headers()
            self.wfile.write(corpo or b"")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", urls, acessos
    srv.shutdown()


def motor(tmp_path):
    (tmp_path / "m.toml").write_text('[motor]\nid = "teste"\nnome = "t"\ncategoria = "c"\nfinalidade = "f"\n\n[[fonte]]\nnome = "x"\nurl = "http://127.0.0.1:9/x"\n'
                                     '\n[acesso]\ndegraus = ["api"]\nintervalo_s = 0\n', encoding="utf-8")
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_relevancia_para_o_livro():
    pal = M.palavras_proprias("Fundo de Apoio à Cultura Anapolina — Edital de Chamamento nº 7/2026")
    assert "anapolina" in pal and "cultura" not in pal                                                          # setor não conta
    assert M.relevancia("https://x/editais/edital-7-2026-x/", pal, "7/2026").startswith("o número do edital")
    assert M.relevancia("https://x/up/regulamento-anapolina.pdf", pal, None).startswith("arquivo com palavra")
    assert M.relevancia("https://x/noticias/festa-junina/", pal, None) is None


def test_mapa_do_site_original(site, tmp_path):
    base, urls, acessos = site
    m = motor(tmp_path)
    livro = {"id": "L", "titulo": "Fundo de Apoio à Cultura Anapolina — Edital de Chamamento nº 7/2026", "link_oficial": f"{base}/fundo", "numero": "7/2026"}
    a = m.vigiar_original(livro)
    entregues = {x.link_divulgacao.replace(base, "") for x in a}
    assert entregues == {"/editais/edital-de-chamamento-7-2026-fundo-de-apoio-a-cultura-anapolina/", "/wp-content/uploads/2026/10/regulamento-fundo-anapolina.pdf"}
    assert all(x.dados["livro_id"] == "L" and x.dados["origem"] == "mapa do site original" for x in a)
    n = len(acessos)
    assert m.vigiar_original(livro) == [] and len(acessos) == n                                                  # uma vez por semana
    urls["/editais/edital-de-chamamento-8-2027-fundo-de-apoio-a-cultura-anapolina/"] = ANTIGA                    # a próxima edição aparece
    novo = m.vigiar_original({**livro, "numero": None}, intervalo_dias=0)
    assert [x.link_divulgacao.replace(base, "") for x in novo] == ["/editais/edital-de-chamamento-8-2027-fundo-de-apoio-a-cultura-anapolina/"]
    assert m.vigiar_original(livro, intervalo_dias=0) == []                                                      # nada novo


def test_a_rede_escolhe_os_livros_com_origem_confirmada(gravador, bancos):
    evs = []
    for i, (_fase, origem) in enumerate((("preparacao", "confirmado"), ("arquivo", "confirmado"), ("arquivo", "candidato"))):
        lid = f"L{i}"
        evs += [ev("livro.criado", id=lid, missao="oportunidades", chave=lid, titulo=f"Edital nº {i}/2026 do Fundo", orgao="Secult", uf="GO",
                   link_oficial="https://goias.gov.br/x", estrela="sem", selo_livro="sem", informacoes_validadas=0, situacao="em trabalho",
                   criado_em=AGORA, atualizado_em=AGORA),
                ev("livro.decupado", livro_id=lid, validacao="aprovado", validado_em=AGORA, origem=origem, origem_motivo="t"),
                ev("livro.passagem", livro_id=lid, de=None, para="recepcao", em=AGORA, autorizado_por="regencia")]
    assert gravador.aplicar(evs).ok
    bancos["biblioteca"].execute("UPDATE passaporte SET fase = CASE livro_id WHEN 'L0' THEN 'preparacao' ELSE 'arquivo' END")
    assert [x["id"] for x in livros_com_origem(bancos["biblioteca"])] == ["L1", "L0"]                           # arquivados primeiro; candidato fora
