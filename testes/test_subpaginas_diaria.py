"""08/11/2026 (titular, R49): cada local de busca é lido UMA vez por dia, todo dia — sem janela nem intervalo — e tem a
segunda etapa: as subpáginas novas do domínio (o mapa do site; sem ele, o feed)."""
from datetime import date, timedelta

import pytest
from servidor_local import criar_servidor

from eldorado.motores.canal.motor import MotorCanal
from eldorado.motores.descoberta import subpaginas as S

HOJE = date.today()
PAG = lambda t: (200, f"<html><head><title>{t}</title></head><body><h1>{t}</h1><p>{'Texto do edital para organizações da sociedade civil. ' * 12}</p></body></html>".encode(), "text/html; charset=utf-8")  # noqa: E731


@pytest.fixture()
def site():
    rotas = {"/editais": (200, ("<html><body><div id='c'><a href='/x'>Sobre</a><p>" + "Página de editais da secretaria. " * 40
                                + "</p></div></body></html>").encode(), "text/html; charset=utf-8"),
             "/robots.txt": (200, b"User-agent: *\nSitemap: {base}/sitemap_index.xml\n", "text/plain"),
             "/edital-de-chamamento-07-2026": PAG("EDITAL DE CHAMAMENTO PÚBLICO Nº 07/2026"),
             "/edital-de-chamamento-01-2024": PAG("Edital 01/2024"),
             "/noticia-sobre-evento": PAG("Notícia")}
    srv, estado = criar_servidor(rotas)
    base = f"http://127.0.0.1:{estado.porta}"
    rotas["/robots.txt"] = (200, f"User-agent: *\nSitemap: {base}/sitemap_index.xml\n".encode(), "text/plain")
    rotas["/sitemap_index.xml"] = (200, f"<sitemapindex><sitemap><loc>{base}/post-sitemap.xml</loc><lastmod>{HOJE}</lastmod></sitemap></sitemapindex>".encode(), "application/xml")
    rotas["/post-sitemap.xml"] = (200, ("<urlset>"
                                        f"<url><loc>{base}/edital-de-chamamento-07-2026</loc><lastmod>{HOJE - timedelta(days=1)}</lastmod></url>"
                                        f"<url><loc>{base}/edital-de-chamamento-01-2024</loc><lastmod>2024-03-01</lastmod></url>"
                                        f"<url><loc>{base}/noticia-sobre-evento</loc><lastmod>{HOJE}</lastmod></url>"
                                        "</urlset>").encode(), "application/xml")
    yield base
    srv.shutdown()


def motor(tmp_path, base, alvo=False):
    fonte = '' if alvo else f'[[fonte]]\nnome = "Editais"\nurl = "{base}/editais"\ntipo = "pagina"\n'
    alvo_ = (f'[[alvo]]\nid = "a1"\nnome = "Portal"\nenderecos = ["{base}/editais"]\nprevisao_meses = [{(HOJE.month + 5) % 12 + 1}]\n'
             if alvo else '')
    (tmp_path / "m.toml").write_text(f'''
[motor]
id = "subpaginas-teste"
nome = "Subpáginas (teste)"
categoria = "Portais"
finalidade = "conferir a segunda etapa"
uf = "GO"
{fonte}{alvo_}
[acesso]
degraus = ["api", "leve"]
intervalo_s = 0
[leitura]
paginas_dos_achados = true
[canivete]
ligado = false
[lexico]
termos = ["re:edital|chamamento"]
''', encoding="utf-8")
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "motores", ponte=tmp_path / "p")
    m.escada.intervalo_padrao = 0
    return m


def test_as_subpaginas_novas_pelo_mapa_do_site(site, tmp_path, monkeypatch):
    m = motor(tmp_path, site)
    achados = list(m.buscar(None))
    links = {a.link_divulgacao.rsplit("/", 1)[-1]: a for a in achados}
    assert set(links) == {"edital-de-chamamento-07-2026"}            # a de 2024 (lastmod antigo) e a notícia (léxico) ficam de fora
    assert links["edital-de-chamamento-07-2026"].titulo.startswith("EDITAL DE CHAMAMENTO PÚBLICO")   # o título vem da página
    assert any("subpáginas · 127.0.0.1" in r and "mapa do site (com data)" in r for r in m.relatorio)


def test_cada_local_uma_vez_por_dia(site, tmp_path, monkeypatch):
    m = motor(tmp_path, site)
    list(m.buscar(None))
    m.relatorio.clear()
    assert list(m.buscar(None)) == []
    assert any("já lida hoje (R49" in r for r in m.relatorio)
    monkeypatch.setenv("ELDORADO_FORCAR", "1")                         # o acionamento à mão (a titular) lê de novo
    m.relatorio.clear()
    list(m.buscar(None))
    assert not any("já lida hoje" in r for r in m.relatorio)


def test_a_janela_nao_impede_a_leitura_diaria(site, tmp_path):
    m = motor(tmp_path, site, alvo=True)                                # previsão de edição daqui a ~6 meses
    list(m.buscar(None))
    assert any("fora da janela prevista — lido assim mesmo (R49)" in r for r in m.relatorio)
    assert m.estado._fonte("alvo · a1").get("leituras") == 1


def test_o_mapa_sem_data_tem_a_primeira_leitura_como_base():
    paginas = {"https://s.org/robots.txt": b"", "https://s.org/sitemap.xml":
               b"<urlset><url><loc>https://s.org/edital-1</loc></url><url><loc>https://s.org/sobre</loc></url></urlset>"}
    ler = paginas.get
    p, mem, rota = S.novas(ler, "s.org", HOJE, set())
    assert p == [] and mem == ["https://s.org/edital-1"] and "base" in rota
    paginas["https://s.org/sitemap.xml"] = paginas["https://s.org/sitemap.xml"].replace(b"</urlset>", b"<url><loc>https://s.org/edital-2</loc></url></urlset>")
    p, mem, _ = S.novas(ler, "s.org", HOJE, set(mem))
    assert [x.link for x in p] == ["https://s.org/edital-2"] and S.titulo_do_endereco(p[0].link) == "edital 2"


def test_a_data_ao_lado_do_link():
    """08/11/2026 (estudo Claude × motores): a data que uma pessoa vê no item da lista vira a data da pista."""
    from selectolax.lexbor import LexborHTMLParser

    from eldorado.motores.descoberta.estrutura_site import data_do_bloco
    h = LexborHTMLParser("<ul><li><a href='/a'>Edital 5/2026</a> — publicado em 03/11/2026</li>"
                         "<li><a href='/b'>Chamamento</a> 4 de outubro de 2025</li><li><a href='/c'>Sem data</a></li>"
                         "<li><a href='/d'>Duas datas</a> 01/01/2026 a 31/01/2026</li></ul>")
    datas = [data_do_bloco(a) for a in h.css("a")]
    assert datas == ["2026-11-03", "2025-10-04", None, None]
