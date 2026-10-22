"""A leitura de páginas: estrutura, links, tabelas, texto limpo, dados embutidos e o sistema do site.

- selectolax (183 MB/s medido) para a estrutura, os links e as tabelas; resiliparse (166 MB/s) para o texto limpo.
- Dados embutidos no código-fonte: JSON-LD, o __NEXT_DATA__ e objetos JavaScript (chompjs), onde muitos portais
  guardam a lista de editais que a página só mostra depois.
- O sistema do site (WordPress, Joomla, Drupal) e o endereço da API dele, para o acesso usar a API em vez da página.
"""
from __future__ import annotations

import csv
import io
import json
import re
from urllib.parse import urljoin

import chompjs
from resiliparse.extract.html2text import extract_plain_text
from selectolax.lexbor import LexborHTMLParser

from .leitores import Leitura, Pagina, Registro, decodificar, sha256

JS_ESTADO = re.compile(r"(?:window\.)?(__\w+__|__INITIAL_STATE__|__NUXT__|__APOLLO_STATE__)\s*=\s*(\{.*\})\s*;?\s*$", re.S)


def sistema_do_site(html: str, url: str | None = None) -> dict[str, str] | None:
    h = html.lower()
    gerador = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', h)
    g = gerador.group(1) if gerador else ""
    base = re.match(r"https?://[^/]+", url or "")
    raiz = base.group(0) if base else ""
    if "wordpress" in g or "/wp-content/" in h or "/wp-json/" in h:
        return {"sistema": "WordPress", "api": f"{raiz}/wp-json/wp/v2/posts" if raiz else "/wp-json/wp/v2/posts"}
    if "joomla" in g or "/media/jui/" in h or "option=com_" in h:
        return {"sistema": "Joomla", "api": f"{raiz}/api/index.php/v1/content/articles" if raiz else ""}
    if "drupal" in g or "drupal-settings-json" in h or "/sites/default/files/" in h:
        return {"sistema": "Drupal", "api": f"{raiz}/jsonapi/node" if raiz else ""}
    return None


class LeitorPagina:
    nome = "página (selectolax + resiliparse)"
    tipos = ("html",)

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        html = decodificar(conteudo)
        r = Leitura(tipo="html", leitor=self.nome, sha256=sha256(conteudo))
        arvore = LexborHTMLParser(html)
        base = nome if nome and nome.startswith("http") else None
        vistos = set()
        for a in arvore.css("a[href]"):
            href = (a.attributes.get("href") or "").strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                u = urljoin(base, href) if base else href
                if u not in vistos:
                    vistos.add(u)
                    r.links.append(u)
        for t in arvore.css("table"):
            linhas = [[c.text(strip=True) for c in tr.css("th, td")] for tr in t.css("tr")]
            if any(linhas):
                r.tabelas.append([lin for lin in linhas if lin])
        titulo = arvore.css_first("title")
        r.dados["titulo"] = titulo.text(strip=True) if titulo else None
        jsonld = []
        for s in arvore.css('script[type="application/ld+json"]'):
            try:
                jsonld.append(json.loads(s.text()))
            except ValueError:
                r.alertas.append("JSON-LD inválido na página")
        if jsonld:
            r.dados["jsonld"] = jsonld
        embutidos = {}
        prox = arvore.css_first("script#__NEXT_DATA__")
        if prox:
            try:
                embutidos["__NEXT_DATA__"] = json.loads(prox.text())
            except ValueError:
                r.alertas.append("__NEXT_DATA__ inválido")
        for s in arvore.css("script:not([src])"):
            m = JS_ESTADO.search(s.text() or "")
            if m:
                try:
                    embutidos[m.group(1)] = chompjs.parse_js_object(m.group(2))
                except ValueError:
                    r.alertas.append(f"objeto JavaScript {m.group(1)} não lido")
        if embutidos:
            r.dados["embutidos"] = embutidos
        sistema = sistema_do_site(html, base)
        if sistema:
            r.dados["sistema"] = sistema
        r.paginas.append(Pagina(1, extract_plain_text(html, main_content=False, links=False, list_bullets=True)))
        return r


class LeitorTexto:
    nome = "texto, JSON, XML e CSV"
    tipos = ("texto", "json", "xml", "csv")

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        texto = decodificar(conteudo)
        r = Leitura(tipo="texto", leitor=self.nome, sha256=sha256(conteudo))
        if (nome or "").lower().endswith((".csv", ".tsv")):
            dialeto = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t|") if texto.strip() else csv.excel
            r.tabelas.append([lin for lin in csv.reader(io.StringIO(texto), dialeto)])
        elif texto.lstrip().startswith(("{", "[")):
            try:
                r.dados["json"] = json.loads(texto)
            except ValueError:
                r.alertas.append("JSON inválido")
        r.paginas.append(Pagina(1, texto))
        return r
