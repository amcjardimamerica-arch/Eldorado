"""As subpáginas novas do domínio (titular, 08/11/2026 — R49: a segunda etapa de cada local de busca).

Cada local que o motor lê (a página de editais, o feed, a API do WordPress, o alvo vigiado) tem um domínio; o mapa do site
desse domínio mostra as páginas NOVAS — muitas vezes o edital aparece ali antes de entrar na lista da página. A segunda
etapa lê, uma vez por dia, o mapa do site (robots.txt "Sitemap:", /sitemap_index.xml, /sitemap.xml, /wp-sitemap.xml) e:
  - com a data de cada página (lastmod): as páginas dos últimos dias;
  - sem data: as páginas que não estavam na última leitura (a primeira leitura é a base: não entrega nada).
Sem mapa do site, o feed do domínio (/feed/) faz a mesma função. Só passam as páginas que o léxico do motor aceita (o
endereço vira o título: "edital-de-chamamento-002-2026" → "edital de chamamento 002 2026"). Nada é copiado (R35): fica
só o endereço.
"""
from __future__ import annotations

import gzip
import re
from datetime import date, timedelta
from typing import Callable
from urllib.parse import unquote, urlsplit

from .pistas import Pista

CANDIDATOS = ("/sitemap_index.xml", "/sitemap.xml", "/wp-sitemap.xml")
PREFERIDOS = re.compile(r"(?i)post|edita|chamad|noticia|oportun|aviso|publica|page")
SINAL = re.compile(r"(?i)edita|chamad|chamament|selec|premi|inscri|fomento|credenc|concurso-cultural|oportunidad|call|grant")
INDICE = re.compile(r"<sitemap>.*?<loc>\s*(.*?)\s*</loc>(?:.*?<lastmod>\s*(.*?)\s*</lastmod>)?.*?</sitemap>", re.S)
URL = re.compile(r"<url>.*?<loc>\s*(.*?)\s*</loc>(?:.*?<lastmod>\s*(.*?)\s*</lastmod>)?.*?</url>", re.S)
SEM_DOMINIO = re.compile(r"(?i)(^api[.-]|dadosabertos|queridodiario|wp-json|\.json\b|legisla\.|pncp\.gov\.br$|in\.gov\.br$)")


def titulo_do_endereco(url: str) -> str:
    """O título que o endereço dá: o último pedaço do caminho, sem hífens."""
    partes = [p for p in urlsplit(url).path.split("/") if p]
    t = unquote(partes[-1] if partes else urlsplit(url).hostname or url)
    t = re.sub(r"\.(html?|php|aspx?)$", "", t, flags=re.I)
    return re.sub(r"[-_+]+", " ", t).strip()[:200]


def _texto(conteudo: bytes) -> str:
    if conteudo[:2] == b"\x1f\x8b":
        try:
            conteudo = gzip.decompress(conteudo)
        except OSError:
            return ""
    return conteudo.decode("utf-8", "ignore")


def _base(host: str) -> str:
    return host.rstrip("/") if "://" in host else f"https://{host}"


def mapa_do_dominio(ler: Callable[[str], bytes | None], host: str) -> tuple[str | None, list[tuple[str, str]]]:
    """O mapa do site do domínio: (endereço do mapa, [(url, lastmod)]). Do índice, só os sub-mapas mais recentes (até 3).
    host: o domínio ("site.org.br") ou a base com o esquema ("http://127.0.0.1:8000")."""
    base = _base(host)
    candidatos: list[str] = []
    robots = ler(base + "/robots.txt")
    if robots:
        candidatos += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", _texto(robots))
    candidatos += [base + c for c in CANDIDATOS]
    for c in dict.fromkeys(candidatos):
        bruto = ler(c)
        t = _texto(bruto) if bruto else ""
        if "<urlset" not in t and "<sitemapindex" not in t:
            continue
        filhos = [(u.replace("&amp;", "&"), m or "") for u, m in INDICE.findall(t)]
        if filhos:
            filhos.sort(key=lambda x: (bool(PREFERIDOS.search(x[0])), x[1]), reverse=True)
            urls: list[tuple[str, str]] = []
            for u, _m in filhos[:3]:
                b = ler(u)
                urls += [(x.replace("&amp;", "&"), m or "") for x, m in URL.findall(_texto(b) if b else "")]
            return c, urls
        return c, [(x.replace("&amp;", "&"), m or "") for x, m in URL.findall(t)]
    return None, []


def feed_do_dominio(ler: Callable[[str], bytes | None], host: str) -> list[tuple[str, str, str]]:
    """O feed do domínio (WordPress e semelhantes): [(link, título, data)]."""
    bruto = ler(_base(host) + "/feed/")
    if not bruto or b"<rss" not in bruto[:2000] and b"<feed" not in bruto[:2000]:
        return []
    import feedparser
    f = feedparser.parse(bruto)
    return [(e.get("link", ""), e.get("title", ""), e.get("published") or e.get("updated") or "") for e in f.entries if e.get("link")]


def novas(ler: Callable[[str], bytes | None], host: str, hoje: date, vistas: set[str], janela_dias: int = 3) \
        -> tuple[list[Pista], list[str], str]:
    """As subpáginas novas do domínio: (pistas, endereços a memorizar quando o mapa não tem data, a rota usada)."""
    mapa, urls = mapa_do_dominio(ler, host)
    corte = (hoje - timedelta(days=janela_dias)).isoformat()
    if mapa and urls:
        com_data = [(u, m) for u, m in urls if m]
        if com_data:
            recentes = [(u, m) for u, m in com_data if m[:10] >= corte]
            return ([Pista(titulo=titulo_do_endereco(u), link=u, origem=f"subpáginas novas (mapa do site {host})", data=m[:10],
                           extra={"titulo_do_endereco": True}) for u, m in recentes], [], "mapa do site (com data)")
        candidatas = sorted({u for u, _ in urls if SINAL.search(u)})
        if not vistas:
            return [], candidatas, "mapa do site (sem data): a primeira leitura é a base"
        return ([Pista(titulo=titulo_do_endereco(u), link=u, origem=f"subpáginas novas (mapa do site {host})",
                       extra={"titulo_do_endereco": True}) for u in candidatas if u not in vistas], candidatas, "mapa do site (sem data)")
    itens = feed_do_dominio(ler, host)
    if itens:
        return ([Pista(titulo=t or titulo_do_endereco(u), link=u, origem=f"subpáginas novas (feed {host})", data=d or None) for u, t, d in itens],
                [], "feed do domínio")
    return [], [], "sem mapa do site nem feed"
