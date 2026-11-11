"""Forma 3: a estrutura do site: o mapa do site, os feeds (RSS e Atom), a API do WordPress e os links da página.

O mapa do site é lido por um leitor próprio (e não pelo ultimate-sitemap-parser), porque toda busca passa pela escada
de acesso; o feedparser continua, porque recebe os bytes já obtidos pela escada.
"""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit

import feedparser

from .pistas import Buscar, Pista

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


_LOC_INDICE = re.compile(r"<(?:\w+:)?sitemap\b[^>]*>.*?<(?:\w+:)?loc>\s*(.*?)\s*</(?:\w+:)?loc>", re.S | re.I)
_LOC_URL = re.compile(r"<(?:\w+:)?url\b[^>]*>(.*?)</(?:\w+:)?url>", re.S | re.I)
_LOC = re.compile(r"<(?:\w+:)?loc>\s*(?:<!\[CDATA\[)?\s*(.*?)\s*(?:\]\]>)?\s*</(?:\w+:)?loc>", re.S | re.I)
_LASTMOD = re.compile(r"<(?:\w+:)?lastmod>\s*(.*?)\s*</(?:\w+:)?lastmod>", re.S | re.I)


def ler_mapa(conteudo: bytes | str) -> tuple[str | None, list[tuple[str, str | None]]]:
    """10/11/2026 (parecer da Sala, passo 5): a leitura TOLERANTE do mapa do site — ("indice" | "urlset" | None, [(loc, lastmod)]).
    Antes, o analisador XML estrito quebrava com espaço ou BOM antes da declaração, prefixo sem namespace (image:, news:)
    ou resposta em HTML, e a fonte «Mapa do site» virava ERRO (16 fontes, 15 motores acesos na Sala). Agora: o .gz é
    aberto; o BOM e os espaços saem; a página sem <urlset> nem <sitemapindex> é «site sem mapa» (None, sem erro); o XML
    defeituoso é lido pelos <loc> (o mesmo recurso do índice das subpáginas)."""
    import gzip
    if isinstance(conteudo, str):
        conteudo = conteudo.encode("utf-8", "replace")
    b = conteudo or b""
    if b[:2] == b"\x1f\x8b":
        try:
            b = gzip.decompress(b)
        except OSError:
            return None, []
    t = b.decode("utf-8", "replace").lstrip("\ufeff \t\r\n")
    baixo = t[:20000].lower()
    tipo = "indice" if "<sitemapindex" in baixo else "urlset" if "<urlset" in baixo else None
    if tipo is None:
        return None, []
    try:
        raiz = ET.fromstring(t.encode("utf-8"))
        nome = lambda el: el.tag.rsplit("}", 1)[-1]   # noqa: E731 — o nome sem o namespace
        if tipo == "indice":
            itens = [((s_.find("./{*}loc").text if s_.find("./{*}loc") is not None else "") or "", None)
                     for s_ in raiz if nome(s_) == "sitemap"]
        else:
            itens = []
            for u in raiz:
                if nome(u) != "url":
                    continue
                loc, mod = u.find("./{*}loc"), u.find("./{*}lastmod")
                itens.append(((loc.text if loc is not None else "") or "", (mod.text if mod is not None else None)))
    except ET.ParseError:
        if tipo == "indice":
            itens = [(m.group(1), None) for m in _LOC_INDICE.finditer(t)]
        else:
            itens = []
            for bloco in _LOC_URL.finditer(t):
                loc, mod = _LOC.search(bloco.group(1)), _LASTMOD.search(bloco.group(1))
                if loc:
                    itens.append((loc.group(1), mod.group(1) if mod else None))
    return tipo, [(html.unescape(loc.strip()), (mod or "").strip() or None) for loc, mod in itens if loc and loc.strip()]


def mapa_do_site(buscar: Buscar, url: str, limite: int = 2000, profundidade: int = 2) -> list[Pista]:
    """As URLs do mapa do site (e dos mapas internos, até a profundidade), com a data de modificação. O site sem mapa
    devolve a lista vazia (não é erro); o mapa interno que falha não derruba os outros."""
    saida: list[Pista] = []
    fila = [(url, 0)]
    while fila and len(saida) < limite:
        atual, nivel = fila.pop(0)
        try:
            tipo, itens = ler_mapa(buscar(atual).conteudo)
        except Exception:  # noqa: BLE001 — o primeiro mapa propaga o erro de acesso (a fonte falha); o interno, não
            if nivel == 0:
                raise
            continue
        if tipo == "indice":
            if nivel < profundidade:
                fila += [(loc, nivel + 1) for loc, _ in itens]
            continue
        for loc, mod in itens:
            saida.append(Pista(titulo=loc.rstrip("/").rsplit("/", 1)[-1].replace("-", " "), link=loc, origem="mapa do site", data=mod))
    return saida[:limite]


def feed(buscar: Buscar, url: str) -> list[Pista]:
    f = feedparser.parse(buscar(url).conteudo)
    return [Pista(titulo=e.get("title", "").strip(), link=e.get("link", ""), origem="feed", data=e.get("published") or e.get("updated"),
                  resumo=(e.get("summary") or "")[:500]) for e in f.entries if e.get("link")]


def wordpress(buscar: Buscar, api: str, busca: str | None = None, por_pagina: int = 50) -> list[Pista]:
    """A API do WordPress (/wp-json/wp/v2/posts): título, link e data de cada publicação."""
    from urllib.parse import quote
    url = f"{api}{'&' if '?' in api else '?'}per_page={por_pagina}"
    if busca:
        url += f"&search={quote(busca)}"
    itens = json_tolerante(buscar(url).conteudo)
    return [Pista(titulo=_texto(i.get("title")), link=i.get("link", ""), origem="API do WordPress", data=i.get("date"),
                  resumo=_texto(i.get("excerpt"))[:500]) for i in itens if i.get("link")]


def _regiao(html: str, url: str, seletor: str) -> str | None:
    """A região do conteúdo: CSS (selectolax), XPath ('xpath:...', lxml) ou, quando o seletor configurado sumiu (o site
    mudou), o seletor adaptável (Scrapling), que reencontra a região pela impressão digital guardada da última vez."""
    if seletor.startswith("xpath:"):
        from lxml import html as lhtml
        nos = lhtml.fromstring(html).xpath(seletor[6:])
        return lhtml.tostring(nos[0], encoding="unicode") if nos else None
    from selectolax.lexbor import LexborHTMLParser
    no = LexborHTMLParser(html).css_first(seletor)
    try:
        import os

        from scrapling import Selector
        pasta = os.environ.get("ELDORADO_DADOS", "dados")
        sel = Selector(html, url=url, adaptive=True, storage_args={"storage_file": os.path.join(pasta, "cerebro.db"), "url": url})   # no Cérebro
        achados = sel.css(seletor, auto_save=no is not None, adaptive=no is None)
        if no is None and achados:
            return achados[0].html_content                  # o site mudou: a região reencontrada
    except Exception:  # noqa: BLE001 — sem o Scrapling (ou sem impressão guardada), só o CSS
        pass
    return no.html if no is not None else None


def json_tolerante(conteudo: bytes | str):
    """08/11/2026 (Cristalina): o WordPress com aviso do PHP ("<br />…") antes do JSON. Lê a partir do primeiro [ ou {."""
    t = conteudo.decode("utf-8", errors="replace") if isinstance(conteudo, bytes) else conteudo
    try:
        return json.loads(t)
    except ValueError:
        i = min((k for k in (t.find("["), t.find("{")) if k >= 0), default=-1)
        if i <= 0:
            raise
        return json.loads(t[i:])


def links(buscar: Buscar, url: str, mesmo_dominio: bool = True, seletor: str | None = None) -> list[Pista]:
    """Os links da página (com o texto de cada um), pelo leitor de páginas; com seletor, só os da região do conteúdo
    (em portais grandes, como o gov.br, os menus trazem centenas de links que não são da fonte)."""
    from selectolax.lexbor import LexborHTMLParser
    r = buscar(url)
    html = r.conteudo.decode("utf-8", errors="replace")
    arvore = LexborHTMLParser(html)
    if seletor:
        regiao = _regiao(html, url, seletor)
        if regiao is not None:
            arvore = LexborHTMLParser(regiao)
    dom = urlsplit(url).hostname
    saida: list[Pista] = []
    posicao: dict[str, int] = {}
    sem_texto: set[str] = set()
    for a in arvore.css("a[href]"):
        href = (a.attributes.get("href") or "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        u = urljoin(url, href)
        if mesmo_dominio and urlsplit(u).hostname != dom:
            continue
        texto = a.text(strip=True)
        if u in posicao:                    # o mesmo endereço de novo: o link com texto substitui o do ícone, sem texto (Plone)
            if texto and u in sem_texto:
                saida[posicao[u]] = Pista(titulo=texto, link=u, origem="links da página")
                sem_texto.discard(u)
            continue
        posicao[u] = len(saida)
        if not texto:
            sem_texto.add(u)
        titulo = texto or u.rstrip("/").rsplit("/", 1)[-1]
        if not texto or TEXTO_GENERICO.search(texto):           # 08/11/2026 (passada no Chrome): "abrir/salvar", "Saiba mais"
            titulo = titulo_do_bloco(a) or titulo
        extra = {}
        situ = situacao_do_bloco(a)
        if situ:
            extra["situacao"] = situ
        saida.append(Pista(titulo=titulo, link=u, origem="links da página", data=data_do_bloco(a), extra=extra))
    return saida


# 08/11/2026 (passada completa no Chrome, Claude × motores): o que uma pessoa lê no item da lista e o motor não lia.
TEXTO_GENERICO = re.compile(r"(?i)^\s*(abrir|abrir/salvar|baixar|download|saiba mais|leia mais|acesse|acessar|clique aqui|"
                            r"veja mais|ver mais|mais informa[cç][oõ]es|confira|inscreva-se|visualizar|ver edital)\W*$")
_ABERTA = re.compile(r"(?i)inscri[cç][oõ]es abertas|inscri[cç][oõ]es prorrogadas|recebendo propostas|\bem aberto\b|\baberto\b|em andamento")
_ENCERRADA = re.compile(r"(?i)\bencerrad[oa]s?\b|inscri[cç][oõ]es encerradas|resultado final|homologa[cç][aã]o|"
                        r"habilita[cç][aã]o para pagamento|avalia[cç][aã]o de m[eé]rito|\bconclu[ií]d[oa]\b")


def _item_da_lista(a):
    """O item da lista onde o link está (li, tr, article, dd, dt, p ou um cartão), subindo até 5 níveis."""
    no = a
    for _ in range(5):
        no = no.parent
        if no is None or no.tag in ("ul", "ol", "table", "tbody", "body", "main", "section", "nav"):
            return None
        classe = (no.attributes.get("class") or "") if hasattr(no, "attributes") else ""
        if no.tag in ("li", "tr", "article", "dd", "dt", "p") or re.search(r"(?i)card|item|post|entry|edital", classe or ""):
            return no
    return None


def titulo_do_bloco(a) -> str | None:
    """O título que a pessoa lê quando o link tem texto genérico: o cabeçalho do cartão (h1–h4/strong) ou, numa linha de
    tabela, as células juntas (ex.: MPT "GOIÂNIA 27/10/2026 094312.2026 … abrir/salvar")."""
    no = _item_da_lista(a)
    if no is None:
        return None
    for sel in ("h1", "h2", "h3", "h4", "h5", "strong", "b"):
        h = no.css_first(sel)
        if h is not None and len(h.text(strip=True)) >= 8:
            return h.text(separator=" ", strip=True)[:160]
    texto = re.sub(r"\s+", " ", no.text(separator=" ")).strip()
    texto = TEXTO_GENERICO.sub("", texto).replace("abrir/salvar", "").strip(" |-")
    return texto[:160] if len(texto) >= 8 else None


def situacao_do_bloco(a) -> str | None:
    """O rótulo de situação ao lado do link ("Inscrições abertas", "Encerrado", "Habilitação para Pagamento") — na página
    da PNAB Goiás, da Funarte e do Prosas é ele, e não a data, que diz se o edital está aberto."""
    no = _item_da_lista(a)
    if no is None:
        return None
    texto = no.text(separator=" ")[:600]
    if _ENCERRADA.search(texto):
        return "encerrada"
    if _ABERTA.search(texto):
        return "aberta"
    return None


_MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b|\b(\d{1,2})º? de (" + "|".join(_MESES) + r") de (20\d\d)\b", re.I)


def _iso(m) -> str | None:
    from datetime import date
    try:
        if m.group(1):
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        return date(int(m.group(6)), _MESES.index(m.group(5).lower()) + 1, int(m.group(4))).isoformat()
    except ValueError:
        return None


def data_do_bloco(a) -> str | None:
    """08/11/2026 (estudo Claude × motores): a data que uma pessoa vê ao lado do link — no próprio item da lista (li, tr,
    article, dt/dd, p), quando ele traz UMA data só. Sem ela, a pista vinha sem data e a idade não se aplicava na entrada."""
    no = a
    for _ in range(4):
        no = no.parent
        if no is None or no.tag in ("ul", "ol", "table", "tbody", "body", "main", "section"):
            return None
        if no.tag in ("li", "tr", "article", "dd", "dt", "p"):
            texto = no.text(separator=" ")[:600]
            datas = {m.group(0) for m in _DATA.finditer(texto)}
            if len(datas) > 1 and re.search(r"(?i)\bfim\b|at[eé]|encerra|prazo|inscri[cç]", texto):
                # 08/11/2026: linha com início e fim (Valparaíso "06/11/2026 … 11/11/2026"): a data que vale é o prazo
                todas = sorted(_iso(m) for m in _DATA.finditer(texto) if _iso(m))
                return todas[-1] if todas else None
            if len(datas) != 1:
                return None
            m = _DATA.search(next(iter(datas)))
            try:
                from datetime import date
                if m.group(1):
                    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
                return date(int(m.group(6)), _MESES.index(m.group(5).lower()) + 1, int(m.group(4))).isoformat()
            except ValueError:
                return None
    return None


def _texto(v) -> str:
    """O texto sem as marcações e com os códigos de HTML decodificados (&#8211; → –)."""
    import html
    import re
    t = v.get("rendered", "") if isinstance(v, dict) else str(v or "")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()



def mapa_completo(buscar: Buscar, raiz: str, limite: int = 5000) -> list[Pista]:
    """Os mapas de site completos pelo leitor do plano (ultimate-sitemap-parser: robots, índices, compactados, notícias,
    texto), buscando PELA ESCADA (intervalo, degraus e bloqueios do sistema); sem a biblioteca, ImportError."""
    from usp.tree import sitemap_tree_for_homepage
    from usp.web_client.abstract_client import AbstractWebClient, AbstractWebClientSuccessResponse, WebClientErrorResponse

    class Resposta(AbstractWebClientSuccessResponse):
        def __init__(self, url, conteudo):
            self._url, self._conteudo = url, conteudo

        def status_code(self):
            return 200

        def status_message(self):
            return "OK"

        def header(self, nome):
            return None

        def raw_data(self):
            return self._conteudo

        def url(self):
            return self._url

    class PelaEscada(AbstractWebClient):
        def set_max_response_data_length(self, n):
            pass

        def get(self, url):
            try:
                return Resposta(url, buscar(url).conteudo)
            except Exception as e:  # noqa: BLE001 — o leitor de mapas trata o erro como mapa ausente
                return WebClientErrorResponse(message=str(e)[:200], retryable=False)
    arvore = sitemap_tree_for_homepage(raiz, web_client=PelaEscada())
    saida: list[Pista] = []
    for p in arvore.all_pages():
        saida.append(Pista(titulo=p.url.rstrip("/").rsplit("/", 1)[-1], link=p.url, data=p.last_modified.date().isoformat() if p.last_modified else None,
                           origem="mapa do site (ultimate-sitemap-parser)"))
        if len(saida) >= limite:
            break
    return saida


def tecnologia(buscar: Buscar, url: str) -> list[str]:
    """A tecnologia do site (webtech): WordPress, Joomla, Plone... indica a rota na criação do motor (a API do WordPress,
    o Plone com #content-core, o Joomla com tabela por POST)."""
    from webtech import WebTech
    r = buscar(url)
    troca = {"request": {"method": "GET", "url": url, "headers": {}},
             "response": {"status": 200, "headers": dict(getattr(r, "cabecalhos", {}) or {"Content-Type": r.tipo or "text/html"}),
                          "body": r.conteudo.decode("utf-8", errors="replace")}}
    rel = WebTech(options={"json": True}).start_from_exchange(troca)
    techs = rel.get("tech", []) if isinstance(rel, dict) else []
    return sorted({t.get("name") for t in techs if t.get("name")})
