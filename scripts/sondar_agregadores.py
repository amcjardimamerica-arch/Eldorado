#!/usr/bin/env python3
"""SONDAGEM DOS AGREGADORES DE EDITAIS (titular, 28/09) — roda no servidor do GitHub.

Para cada site: a listagem responde? o conteúdo vem no HTML ou depende de JavaScript? há RSS / sitemap? o robots.txt
permite? quantos editais aparecem? e, lendo algumas páginas de edital, QUANTAS apontam para a fonte oficial — é isso
que decide se o site serve como motor de INDÍCIOS. Grava biblioteca_alexandria/base/sondagem_agregadores.json.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.sites_oficiais import e_republicador  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Eldorado; associacao sem fins lucrativos; leitura de editais publicos)"}
SITES = {
    "capitaai": ["https://capitaai.com.br/editais-abertos/para-ong", "https://capitaai.com.br/editais-abertos", "https://capitaai.com.br/"],
    "farolcultural": ["https://farolcultural.art/", "https://farolcultural.art/editais", "https://farolcultural.art/e/"],
    "mabus": ["https://mabus.com.br/licitacao", "https://mabus.com.br/", "https://mabus.com.br/chamamento-publico"],
    "idis": ["https://www.idis.org.br/category/editais-e-chamadas/", "https://www.idis.org.br/editais/", "https://www.idis.org.br/"],
}
EDITAL = re.compile(r"edital|chamad|chamamento|sele[cç][aã]o|pr[eê]mio|inscri|credenciamento|/e/|licitacao|oportunidade", re.I)


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.l = []; self._h = None; self._t = []; self.scripts = 0; self.texto = []
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "a":
            self._h = a.get("href"); self._t = []
        if tag == "script":
            self.scripts += 1
        if tag == "link" and "alternate" in str(a.get("rel")) and "rss" in str(a.get("type")):
            self.l.append(("__rss__", a.get("href")))
    def handle_data(self, d):
        self.texto.append(d)
        if self._h is not None:
            self._t.append(d)
    def handle_endtag(self, tag):
        if tag == "a" and self._h:
            self.l.append((self._h, " ".join("".join(self._t).split())[:140])); self._h = None


def get(url, t=30):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
            return r.status, r.read(6_000_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, str(e)[:100]


def sondar(urls):
    host = urlsplit(urls[0]).hostname
    rob_c, rob = get(f"https://{host}/robots.txt", 15)
    sm_c, sm = get(f"https://{host}/sitemap.xml", 20)
    res = {"site": host, "robots_http": rob_c, "robots": (rob or "")[:600], "sitemap_http": sm_c,
           "sitemap_urls": len(re.findall(r"<loc>", sm or "")), "listagens": [], "amostra": []}
    edital_urls = []
    for u in urls:
        c, html = get(u)
        p = Links(); p.feed(html or "")
        visivel = re.sub(r"\s+", " ", " ".join(p.texto)).strip()
        eds = {}
        for h, t in p.l:
            if h == "__rss__":
                res.setdefault("rss", t); continue
            full = urljoin(u, h or "")
            if urlsplit(full).hostname == host and EDITAL.search(f"{full} {t}") and len(t.split()) >= 3:
                eds[full] = t
        res["listagens"].append({"url": u, "http": c, "bytes": len(html or ""), "texto_visivel": len(visivel), "scripts": p.scripts,
                                 "depende_de_js": bool(c == 200 and len(visivel) < 1500 and p.scripts > 5),
                                 "editais_na_listagem": len(eds), "exemplos": list(eds.values())[:5]})
        edital_urls += list(eds)
        time.sleep(1)
    vistos = set()
    for f in edital_urls:
        if f in vistos or len(res["amostra"]) >= 8:
            continue
        vistos.add(f)
        c, html = get(f)
        p = Links(); p.feed(html or "")
        saidas = []
        for h, t in p.l:
            if not h or h == "__rss__":
                continue
            s = urljoin(f, h)
            if s.startswith("http") and urlsplit(s).hostname not in (host, None) and not e_republicador(s) \
               and not re.search(r"facebook|instagram|linkedin|twitter|whatsapp|youtube|wa\.me|google|apple|t\.me", s):
                saidas.append(s)
        oficiais = [s for s in saidas if re.search(r"\.gov\.br|\.org\.br|\.leg\.br|\.jus\.br|edital|inscri|regulamento|\.pdf|prosas|mapasculturais", s, re.I)]
        prazo = re.search(r"(?:at[eé]|prazo[^0-9]{0,20})\s*(\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2} de [a-zç]+ de \d{4})", " ".join(p.texto), re.I)
        res["amostra"].append({"url": f, "http": c, "saidas_oficiais": oficiais[:4], "tem_link_oficial": bool(oficiais),
                               "prazo_no_texto": prazo.group(1) if prazo else None})
        time.sleep(1)
    am = res["amostra"]
    ok = [l for l in res["listagens"] if l["http"] == 200]
    res["resumo"] = {"listagem_ok": any(l["editais_na_listagem"] for l in ok), "editais_vistos": len(set(edital_urls)),
                     "amostra_lida": len(am), "com_link_oficial": sum(1 for a in am if a["tem_link_oficial"]),
                     "com_prazo_no_texto": sum(1 for a in am if a["prazo_no_texto"]),
                     "depende_de_js": all(l["depende_de_js"] for l in ok) if ok else None, "rss": res.get("rss")}
    return res


if __name__ == "__main__":
    out = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "sites": {n: sondar(u) for n, u in SITES.items()}}
    dest = RAIZ / "biblioteca_alexandria/base/sondagem_agregadores.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({n: s["resumo"] for n, s in out["sites"].items()}, ensure_ascii=False, indent=1))
