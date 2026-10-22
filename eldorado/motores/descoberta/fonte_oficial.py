"""Seguir até a fonte oficial: na página de DIVULGAÇÃO (notícia, post, agregador), o documento OFICIAL do edital.

Lógica aproveitada do Eldorado0 (fonte_oficial.achar_pdfs): só links de documento (PDF, download, anexo, arquivo);
pontos para PDF, para as palavras de edital no texto do link, para as palavras em comum com o título e, sobretudo, para
o mesmo número do edital. Redes sociais, encurtadores e republicadores nunca contam; as plataformas oficiais de
inscrição (Prosas, Mapas Culturais, Transferegov...) contam como fonte.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urljoin, urlsplit

from selectolax.lexbor import LexborHTMLParser

from ..acesso.escada import dominio

CHAVE = re.compile(r"(?i)edital|regulamento|chamada|chamamento|anexo|termo de refer|retifica|cronograma|instru[çc][ãa]o normativa|portaria")
DOCUMENTO = re.compile(r"(?i)\.(pdf|docx?|odt|xlsx?|zip)($|\?)|download|/arquivos?/|anexo|/uploads?/|/files?/|documento")
NAO_FONTE = ("facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "youtube.com", "whatsapp", "t.me", "google.com",
             "goo.gl", "bit.ly", "wa.me", "tiktok.com")
PLATAFORMA_OFICIAL = ("prosas.com.br", "prosas.org", "mapacultural", "mapas.cultura", "mapa.cultura.gov.br", "editais.cultura.gov.br",
                      "editais.funarte.gov.br", "transferegov", "plataformamaisbrasil", "salic.cultura.gov.br")
VAZIAS = {"para", "com", "edital", "editais", "abre", "aberta", "abertas", "inscricoes", "inscricao", "sobre", "pela", "pelo", "como", "mais", "sera", "serao"}


def _sem(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", (t or "").lower()) if not unicodedata.combining(c))


def tokens(*textos: str) -> set[str]:
    return {p for t in textos for p in re.findall(r"[a-z0-9]{4,}", _sem(t)) if p not in VAZIAS}


def numero(texto: str) -> str | None:
    m = re.search(r"n[º°o.]*\s*(\d{1,4})\s*[/_-]\s*(20\d\d)", _sem(texto))
    return f"{int(m.group(1))}/{m.group(2)}" if m else None


def candidatos(html: bytes | str, url: str, titulo: str = "", limite: int = 3) -> list[dict]:
    """Os documentos oficiais prováveis da página, do mais forte ao mais fraco (só os com 3 pontos ou mais)."""
    texto = html.decode("utf-8", errors="replace") if isinstance(html, bytes) else html
    tk, num, achados, vistos = tokens(titulo), numero(titulo), [], set()
    for a in LexborHTMLParser(texto).css("a[href]"):
        href = urljoin(url, (a.attributes.get("href") or "").strip())
        txt = a.text(strip=True)
        h = href.lower()
        if href in vistos or not h.startswith("http") or any(n in h for n in NAO_FONTE):
            continue
        vistos.add(href)
        plataforma = any(p in h for p in PLATAFORMA_OFICIAL)
        if not (DOCUMENTO.search(h) or plataforma):
            continue
        p = 0.0
        if re.search(r"\.pdf($|\?)", h):
            p += 2
        if CHAVE.search(txt) or CHAVE.search(h):
            p += 2
        if plataforma:
            p += 1.5
        p += min(3, len(tk & tokens(txt, href)))
        if num and numero(f"{txt} {href}") == num:
            p += 5
        if p >= 3:
            achados.append({"url": href, "texto": txt, "pontos": round(p, 1), "dominio": dominio(href)})
    return sorted(achados, key=lambda x: -x["pontos"])[:limite]


def mesmo_site(a: str, b: str) -> bool:
    return (urlsplit(a).hostname or "").removeprefix("www.") == (urlsplit(b).hostname or "").removeprefix("www.")
