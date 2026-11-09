"""08/11/2026 (parecer individual dos motores): os filtros de ENTRADA do motor genérico — a idade da pista, o território
(a regra do portão já na entrada), o título genérico de link e o alvo sem léxico — e o título tirado do documento."""
import json
from datetime import timedelta

import pymupdf
import pytest
from servidor_local import criar_servidor

from eldorado.motores.canal.motor import (
    VISTA_PLONE,
    MotorCanal,
    _cita_data_recente,
    _idade_dias,
    _prazo_no_titulo,
    _titulo_do_documento,
    _variantes_do_endereco,
    hoje_local,
)


def pdf(texto):
    d = pymupdf.open()
    pg = d.new_page()
    pg.insert_textbox(pymupdf.Rect(40, 40, 555, 800), texto, fontsize=9)
    return d.tobytes()


HOJE = hoje_local()   # 09/11/2026: o mesmo relógio do motor (o dia de Goiânia); date.today() é o dia do servidor, e entre 21 h e 24 h as datas diferem
POSTS = json.dumps([
    {"title": {"rendered": "Edital de chamamento para OSC de Goiânia"}, "link": "/p/novo", "date": (HOJE - timedelta(days=10)).isoformat() + "T10:00:00",
     "excerpt": {"rendered": "inscrições abertas"}},
    {"title": {"rendered": "Edital de chamamento 2023 para OSC"}, "link": "/p/velho", "date": (HOJE - timedelta(days=900)).isoformat() + "T10:00:00",
     "excerpt": {"rendered": "encerrado"}},
    {"title": {"rendered": "Edital de chamamento da Prefeitura de Morro do Chapéu (BA)"}, "link": "/p/bahia",
     "date": (HOJE - timedelta(days=5)).isoformat() + "T10:00:00", "excerpt": {"rendered": "município de Morro do Chapéu"}},
]).encode()
PAGINA = """<html><body><div id="c">
<a href="/menu/carometro">Saiba mais sobre o carômetro</a>
<a href="/docs/doacao.pdf">Clique aqui e leia o edital</a>
<a href="/n/edital-cultura">Edital de chamamento público para a cultura</a>
</div></body></html>""".encode()
VELHA = (HOJE - timedelta(days=900)).isoformat()
NOTICIAS = """<html><body><div id="c">
<a href="/n/velha">Edital seleciona entidades de Goiás para receber recursos</a>
<a href="/n/velha-com-prazo">Edital de chamamento republicado para OSC</a>
<a href="/n/nova">Edital de chamamento para OSC de Anápolis</a>
</div></body></html>""".encode()


def noticia(data, corpo):
    return (f'<html><head><meta property="article:published_time" content="{data}T10:00:00"></head>'
            f'<body><article><h1>Notícia</h1><p>{corpo}</p>'
            + "<p>O conselho reuniu as entidades sociais para apresentar o edital e as regras de participação. </p>" * 12
            + '</article></body></html>').encode()


EDITAL_DOACAO = "MINISTÉRIO PÚBLICO FEDERAL\nEDITAL DE DOAÇÃO DE BENS Nº 2/2026\nTorna público o edital de doação de bens a entidades sem fins lucrativos."


@pytest.fixture(scope="module")
def site():
    srv, estado = criar_servidor({"/wp/posts": (200, POSTS, "application/json"),
                                  "/editais.html": (200, PAGINA, "text/html; charset=utf-8"),
                                  "/docs/doacao.pdf": (200, pdf(EDITAL_DOACAO), "application/pdf"),
                                  "/n/edital-cultura": (200, b"<html><body>edital</body></html>", "text/html"),
                                  "/noticias.html": (200, NOTICIAS, "text/html; charset=utf-8"),
                                  "/plone.html": (200, b'<html><body><a href="/docs/doacao.pdf/view">editaldestinacao_121120-2026_Gerado-em-13-10-2026.pdf</a></body></html>',
                                                  "text/html; charset=utf-8"),
                                  "/n/velha": (200, noticia(VELHA, "O edital recebeu propostas até 10/03/2024."), "text/html"),
                                  "/n/velha-com-prazo": (200, noticia(VELHA, f"Inscrições até {(HOJE + timedelta(days=20)).strftime('%d/%m/%Y')}."), "text/html"),
                                  "/n/nova": (200, noticia((HOJE - timedelta(days=4)).isoformat(), "Inscrições abertas."), "text/html")})
    yield f"http://127.0.0.1:{estado.porta}"
    srv.shutdown()


def montar(tmp_path, base, fontes, lexico, alvo=""):
    texto = f'''
[motor]
id = "entrada-teste"
nome = "Filtros de entrada (teste)"
categoria = "Portais"
finalidade = "conferir os filtros de entrada"
uf = "GO"
{fontes}
{alvo}
[acesso]
degraus = ["api", "leve"]
intervalo_s = 0
[leitura]
documentos = true
paginas_dos_achados = false
[canivete]
ligado = false
[lexico]
{lexico}
'''.replace("{base}", base)
    (tmp_path / "m.toml").write_text(texto, encoding="utf-8")
    m = MotorCanal(tmp_path / "m.toml", dados=tmp_path / "motores", ponte=tmp_path / "ponte")
    m.escada.intervalo_padrao = 0
    return m


def test_a_idade_e_o_territorio_na_entrada(site, tmp_path):
    fontes = '[[fonte]]\nnome = "WP"\nurl = "{base}/wp/posts"\ntipo = "wordpress"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["edital"]\nidade_maxima_dias = 365\nterritorio = "goias"')
    titulos = [a.titulo for a in m.buscar(None)]
    assert titulos == ["Edital de chamamento para OSC de Goiânia"]               # o velho (900 dias) e o da Bahia ficaram de fora
    rel = " ".join(m.relatorio)
    assert "publicada há mais de 365 dias (1)" in rel and "município de outro estado (não capital) (1)" in rel


def test_sem_os_filtros_tudo_entra(site, tmp_path):
    fontes = '[[fonte]]\nnome = "WP"\nurl = "{base}/wp/posts"\ntipo = "wordpress"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["edital"]')
    assert len(list(m.buscar(None))) == 3                                        # "livre" e sem idade: o comportamento anterior


def test_o_titulo_generico_de_link(site, tmp_path):
    fontes = '[[fonte]]\nnome = "Editais"\nurl = "{base}/editais.html"\ntipo = "pagina"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["re:edital|carometro|clique"]')
    achados = {a.link_divulgacao.rsplit("/", 1)[-1]: a.titulo for a in m.buscar(None)}
    assert "carometro" not in achados                                            # o menu "Saiba mais" sai na entrada
    assert achados["doacao.pdf"].startswith("EDITAL DE DOAÇÃO DE BENS")          # o PDF ganha o título do próprio documento
    assert achados["edital-cultura"] == "Edital de chamamento público para a cultura"


def test_o_alvo_sem_lexico_entrega_so_a_pagina(site, tmp_path):
    alvo = '[[alvo]]\nid = "a1"\nnome = "Portal sem léxico"\nenderecos = ["{base}/editais.html"]\n'
    m = montar(tmp_path, site, "", "", alvo=alvo)
    achados = list(m.buscar(None))
    assert [a.titulo for a in achados] == ["Portal sem léxico"]                  # antes: todos os links do portal


def test_a_idade_das_datas_e_o_titulo_do_documento():
    assert _idade_dias((HOJE - timedelta(days=3)).isoformat()) == 3
    assert _idade_dias((HOJE - timedelta(days=3)).strftime("%d/%m/%Y")) == 3
    assert _idade_dias("data inválida") is None and _idade_dias(None) is None
    assert _titulo_do_documento({"paginas": ["cabeçalho\nAVISO DE CHAMAMENTO PÚBLICO Nº 5/2026\nobjeto"]}) == "AVISO DE CHAMAMENTO PÚBLICO Nº 5/2026"


def test_o_alvo_de_outro_estado_nao_e_lido_com_o_territorio_de_goias(site, tmp_path):
    alvo = ('[[alvo]]\nid = "a2"\nnome = "PNCP — MUNICIPIO DE CARAZINHO — oportunidades"\nenderecos = ["{base}/editais.html"]\n'
            '[[alvo]]\nid = "a3"\nnome = "Portal de Goiás"\nenderecos = ["{base}/editais.html"]\n')
    m = montar(tmp_path, site, "", 'territorio = "goias"', alvo=alvo)
    assert [a.titulo for a in m.buscar(None)] == ["Portal de Goiás"]
    assert any("CARAZINHO" in r and "fora do território" in r for r in m.relatorio)


def test_a_idade_lida_na_pagina_da_noticia(site, tmp_path):
    """08/11/2026: a pista da busca HTML vem sem data; a data é lida na própria página e a notícia velha sai — salvo quando
    o texto cita um prazo dentro da janela (a data da página pode estar errada; o prazo de agora vale mais)."""
    fontes = '[[fonte]]\nnome = "Notícias"\nurl = "{base}/noticias.html"\ntipo = "pagina"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["edital"]\nidade_maxima_dias = 365')
    m.cfg = m.cfg.model_copy(update={"leitura": m.cfg.leitura.model_copy(update={"paginas_dos_achados": True})})
    achados = {a.link_divulgacao.rsplit("/", 1)[-1]: a for a in m.buscar(None)}
    assert set(achados) == {"velha-com-prazo", "nova"}                         # a velha sem prazo atual ficou de fora
    assert achados["nova"].publicado_em == (HOJE - timedelta(days=4)).isoformat()   # a data lida vira a data de publicação
    assert "publicada há mais de 365 dias (data lida na página) (1)" in " ".join(m.relatorio)


def test_sem_idade_maxima_a_data_lida_so_informa(site, tmp_path):
    fontes = '[[fonte]]\nnome = "Notícias"\nurl = "{base}/noticias.html"\ntipo = "pagina"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["edital"]')
    m.cfg = m.cfg.model_copy(update={"leitura": m.cfg.leitura.model_copy(update={"paginas_dos_achados": True})})
    achados = list(m.buscar(None))
    assert len(achados) == 3 and all(a.publicado_em for a in achados)


def test_a_data_recente_citada_no_texto():
    assert _cita_data_recente("Inscrições de 1º de dezembro de " + str(HOJE.year) + " até o fim", 365)
    assert _cita_data_recente("prazo: " + (HOJE + timedelta(days=30)).strftime("%d/%m/%Y"), 365)
    assert not _cita_data_recente("propostas até 10/03/2019 e resultado em 5 de maio de 2019", 365)


def test_o_arquivo_pdf_view_do_plone_e_o_nome_de_arquivo(site, tmp_path):
    """08/11/2026: o "arquivo.pdf/view" do Plone (gov.br, MPT) se lê como o arquivo; o título que é nome de arquivo passa na
    entrada e é trocado pelo título do próprio documento."""
    fontes = '[[fonte]]\nnome = "Plone"\nurl = "{base}/plone.html"\ntipo = "pagina"\n'
    m = montar(tmp_path, site, fontes, 'termos = ["re:edital"]')
    [a] = list(m.buscar(None))
    assert a.link_divulgacao.endswith("/docs/doacao.pdf/view") and a.documento["url"].endswith("/docs/doacao.pdf")
    assert a.titulo.startswith("EDITAL DE DOAÇÃO DE BENS")
    assert VISTA_PLONE.sub(r"\1", "https://www.gov.br/x/edital.pdf/view") == "https://www.gov.br/x/edital.pdf"


def test_o_filtro_da_fonte(site, tmp_path):
    """08/11/2026: o filtro da fonte (campo → expressão) sobre os campos da pista e os dados do item."""
    fontes = '[[fonte]]\nnome = "WP"\nurl = "{base}/wp/posts"\ntipo = "wordpress"\nfiltro = { titulo = "(?i)goi[âa]nia|bahia" }\n'
    m = montar(tmp_path, site, fontes, 'termos = ["edital"]')
    titulos = sorted(a.titulo for a in m.buscar(None))
    assert titulos == ["Edital de chamamento para OSC de Goiânia"]                 # o velho (2023) e o da Bahia não casam
    assert "filtro da fonte (" in " ".join(m.relatorio)


def test_o_prazo_declarado_no_titulo():
    """08/11/2026: os agregadores põem o prazo no título ("…até 22 de out. de 2026"): vencido, sai na entrada (com a idade)."""
    from datetime import date as d
    assert _prazo_no_titulo("Edital Hospital Universitário 2026: Guia de Credenciamentoaté 22 de out. de 2026") == d(2026, 10, 22)
    assert _prazo_no_titulo("O Edital SoMar Azul — com inscrições abertas até o dia 5 de novembro de 2026") == d(2026, 11, 5)
    assert _prazo_no_titulo("Edital X — inscrições até 30/11/2026") == d(2026, 11, 30)
    assert _prazo_no_titulo("Edital de chamamento 05/2026") is None


def test_as_variantes_do_endereco():
    """08/11/2026: o mesmo edital pelo RSS (www.) e pela página (sem www.) é um só."""
    v = _variantes_do_endereco("https://www.observatorio3setor.org.br/editais/x/")
    assert v[0] == "https://www.observatorio3setor.org.br/editais/x/"
    assert "https://observatorio3setor.org.br/editais/x" in v and "http://observatorio3setor.org.br/editais/x/" in v
    assert _variantes_do_endereco("https://a.org/p?id=1")[:2] == ["https://a.org/p?id=1", "https://www.a.org/p?id=1"]
