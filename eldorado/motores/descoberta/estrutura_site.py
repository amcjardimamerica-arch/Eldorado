"""Forma 3: a estrutura do site: o mapa do site, os feeds (RSS e Atom), a API do WordPress e os links da página.

O mapa do site é lido por um leitor próprio (e não pelo ultimate-sitemap-parser), porque toda busca passa pela escada
de acesso; o feedparser continua, porque recebe os bytes já obtidos pela escada.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit

import feedparser

from .pistas import Buscar, Pista

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def mapa_do_site(buscar: Buscar, url: str, limite: int = 2000, profundidade: int = 2) -> list[Pista]:
    """As URLs do mapa do site (e dos mapas internos, até a profundidade), com a data de modificação."""
    saida: list[Pista] = []
    fila = [(url, 0)]
    while fila and len(saida) < limite:
        atual, nivel = fila.pop(0)
        raiz = ET.fromstring(buscar(atual).conteudo)
        if raiz.tag == f"{NS}sitemapindex" and nivel < profundidade:
            fila += [(s.findtext(f"{NS}loc", "").strip(), nivel + 1) for s in raiz.findall(f"{NS}sitemap")]
            continue
        for u in raiz.findall(f"{NS}url"):
            loc = u.findtext(f"{NS}loc", "").strip()
            if loc:
                saida.append(Pista(titulo=loc.rstrip("/").rsplit("/", 1)[-1].replace("-", " "), link=loc, origem="mapa do site",
                                   data=(u.findtext(f"{NS}lastmod") or None)))
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
    itens = json.loads(buscar(url).conteudo)
    return [Pista(titulo=_texto(i.get("title")), link=i.get("link", ""), origem="API do WordPress", data=i.get("date"),
                  resumo=_texto(i.get("excerpt"))[:500]) for i in itens if i.get("link")]


def links(buscar: Buscar, url: str, mesmo_dominio: bool = True, seletor: str | None = None) -> list[Pista]:
    """Os links da página (com o texto de cada um), pelo leitor de páginas; com seletor, só os da região do conteúdo
    (em portais grandes, como o gov.br, os menus trazem centenas de links que não são da fonte)."""
    from selectolax.lexbor import LexborHTMLParser
    r = buscar(url)
    arvore = LexborHTMLParser(r.conteudo.decode("utf-8", errors="replace"))
    if seletor and arvore.css_first(seletor) is not None:
        arvore = arvore.css_first(seletor)
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
        saida.append(Pista(titulo=texto or u.rstrip("/").rsplit("/", 1)[-1], link=u, origem="links da página"))
    return saida


def _texto(v) -> str:
    """O texto sem as marcações e com os códigos de HTML decodificados (&#8211; → –)."""
    import html
    import re
    t = v.get("rendered", "") if isinstance(v, dict) else str(v or "")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

