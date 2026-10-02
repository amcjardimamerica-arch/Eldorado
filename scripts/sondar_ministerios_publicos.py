"""SONDAGEM DOS MINISTÉRIOS PÚBLICOS — motor 12 (titular, 02/10/2026; prompt em docs/prompts/PROMPT-MOTOR-12-MINISTERIOS-PUBLICOS.md).

Estuda ao vivo onde MP-GO (programa Destina), MPT-GO, MPT, MPF, MPDFT, MPM, MPU, CNMP e o Fundo de Defesa de Direitos Difusos
publicam editais de destinação de recursos de reparação e bens lesados. Respeita o robots.txt; não contorna login nem
CAPTCHA; conteúdo coletado é dado. Só biblioteca-padrão. Saída: biblioteca_alexandria/base/ministerios_publicos/sondagem.json
"""
from __future__ import annotations

import gzip
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "biblioteca_alexandria/base/ministerios_publicos/sondagem.json"
UA = "Mozilla/5.0 (compatible; EldoradoBot/1.0; +https://github.com/amcjardimamerica-arch/Eldorado)"
KW = re.compile(r"destina|destina[cç][aã]o|editai?s?\b|chamamento|cadastr|entidades?|projetos? socia|\bTAC\b|ajustamento|fundo|"
                r"repara[cç][aã]o|bens lesados|dano moral coletivo|multas?|presta[cç][aã]o pecuni|transa[cç][aã]o penal|benefici[aá]ri|"
                r"direitos difusos|doa[cç][aã]o|revers[aã]o", re.I)
DATA = re.compile(r"\b(\d{2})/(\d{2})/(20(?:2[3-6]))\b")
ORGAOS = {
    "MP-GO": {"dominios": ["mpgo.mp.br"], "sementes": ["https://www.mpgo.mp.br/", "https://www.mpgo.mp.br/portal/", "https://www.mpgo.mp.br/destina",
              "https://www.mpgo.mp.br/portal/pagina/destina", "https://www.mpgo.mp.br/portal/conteudo/destina"]},
    "MPT-GO (PRT-18)": {"dominios": ["prt18.mpt.mp.br"], "sementes": ["https://www.prt18.mpt.mp.br/",
              "https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos", "https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais",
              "https://www.prt18.mpt.mp.br/informe-se/noticias-do-mpt-go"]},
    "MPT nacional": {"dominios": ["mpt.mp.br", "www.mpt.mp.br", "diario.mpt.mp.br"], "sementes": ["https://mpt.mp.br/", "https://www.mpt.mp.br/", "https://diario.mpt.mp.br/"]},
    "MPF (PR-GO e nacional)": {"dominios": ["mpf.mp.br"], "sementes": ["https://www.mpf.mp.br/go", "https://www.mpf.mp.br/", "https://www.mpf.mp.br/servicos"]},
    "MPDFT": {"dominios": ["mpdft.mp.br"], "sementes": ["https://www.mpdft.mp.br/portal/", "https://www.mpdft.mp.br/"]},
    "MPM": {"dominios": ["mpm.mp.br"], "sementes": ["https://www.mpm.mp.br/"]},
    "MPU": {"dominios": ["mpu.mp.br"], "sementes": ["https://www.mpu.mp.br/"]},
    "CNMP": {"dominios": ["cnmp.mp.br"], "sementes": ["https://www.cnmp.mp.br/portal/"]},
    "FDD (Fundo de Defesa de Direitos Difusos)": {"dominios": ["www.gov.br/mj"], "sementes": [
              "https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/direitos-difusos"]},
}
POR_DOMINIO, PROFUNDIDADE, PAUSA, PRAZO_TOTAL = 60, 2, 1.0, 32 * 60


class _P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.titulo = ""; self._t = False; self._a = None; self._txt = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._t = True
        if tag == "a" and a.get("href"):
            self._a = a["href"]; self._txt = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "a" and self._a is not None:
            self.links.append((self._a, " ".join("".join(self._txt).split())[:140])); self._a = None

    def handle_data(self, d):
        if self._t:
            self.titulo += d
        if self._a is not None:
            self._txt.append(d)


def ler(url: str, limite=4_000_000) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", "Accept-Encoding": "gzip"})
        with urllib.request.urlopen(req, timeout=25) as r:
            b = r.read(limite)
            if (r.headers.get("Content-Encoding") or "") == "gzip":
                b = gzip.decompress(b)
            return {"status": r.status, "final": r.geturl(), "tipo": r.headers.get("Content-Type") or "", "bytes": len(b), "corpo": b}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "final": url, "tipo": "", "bytes": 0, "corpo": b""}
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "final": url, "tipo": "", "bytes": 0, "corpo": b"", "erro": f"{type(e).__name__}: {str(e)[:120]}"}


def dentro(url: str, doms: list[str]) -> bool:
    p = urllib.parse.urlsplit(url); h = (p.hostname or "").lower()
    for d in doms:
        if "/" in d:
            host, cam = d.split("/", 1)
            if h == host and p.path.startswith("/" + cam):
                return True
        elif h == d or h.endswith("." + d):
            return True
    return False


def robots(base: str) -> tuple[urllib.robotparser.RobotFileParser, dict]:
    rp = urllib.robotparser.RobotFileParser(); r = ler(urllib.parse.urljoin(base, "/robots.txt"), 300_000)
    txt = r["corpo"].decode("utf-8", "ignore") if r["status"] == 200 else ""
    rp.parse(txt.splitlines()) if txt else rp.parse([])
    return rp, {"status": r["status"], "sitemaps": re.findall(r"(?im)^sitemap:\s*(\S+)", txt)[:10], "proibicoes": re.findall(r"(?im)^disallow:\s*(\S+)", txt)[:30]}


def tipo_pagina(url: str, titulo: str, texto: str) -> str:
    s = f"{url} {titulo}".lower()
    if url.lower().split("?")[0].endswith(".pdf"):
        return "pdf"
    if re.search(r"resolu[cç][aã]o|recomenda[cç][aã]o|normativ", s):
        return "regra"
    if re.search(r"/noticia|/noticias|/informe-se/|/imprensa", s):
        return "notícia"
    if re.search(r"edital|chamamento|cadastro|destina", s):
        return "edital ou listagem"
    return "página"


def run() -> dict:
    ini = time.monotonic(); out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Saída")[0].strip(), "orgaos": {}}
    for orgao, cfg in ORGAOS.items():
        doms = cfg["dominios"]; O = {"dominios": doms, "robots": {}, "sitemap_urls_com_sinal": [], "paginas": []}
        rps = {}
        for s in cfg["sementes"]:
            b = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(s))
            if b not in rps:
                rps[b], O["robots"][b] = robots(b)
        for b, info in list(O["robots"].items()):                        # sitemaps: endereços com sinal de destinação
            for sm in info["sitemaps"][:4]:
                r = ler(sm, 6_000_000); txt = r["corpo"].decode("utf-8", "ignore")
                for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)[:20000]:
                    if KW.search(loc) and dentro(loc, doms):
                        O["sitemap_urls_com_sinal"].append(loc)
                time.sleep(PAUSA)
        O["sitemap_urls_com_sinal"] = list(dict.fromkeys(O["sitemap_urls_com_sinal"]))[:300]
        fila = deque((s, 0) for s in cfg["sementes"] + O["sitemap_urls_com_sinal"][:40]); vistos = set()
        while fila and len(O["paginas"]) < POR_DOMINIO and time.monotonic() - ini < PRAZO_TOTAL:
            url, prof = fila.popleft()
            if url in vistos:
                continue
            vistos.add(url)
            b = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(url))
            rp = rps.get(b)
            if rp is None:
                rps[b], O["robots"][b] = robots(b); rp = rps[b]
            if not rp.can_fetch(UA, url):
                O["paginas"].append({"url": url, "robots": "proibido"}); continue
            r = ler(url); time.sleep(PAUSA)
            pg = {"url": url, "final": r["final"], "status": r["status"], "tipo_conteudo": r["tipo"][:40], "bytes": r["bytes"], **({"erro": r["erro"]} if r.get("erro") else {})}
            if r["status"] == 200 and "html" in r["tipo"]:
                html = r["corpo"].decode("utf-8", "ignore"); p = _P()
                try:
                    p.feed(html)
                except Exception:  # noqa: BLE001
                    pass
                texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", html)))
                links = [(urllib.parse.urljoin(r["final"], h).split("#")[0], t) for h, t in p.links if not h.startswith(("javascript:", "mailto:", "tel:"))]
                kl = [(u, t) for u, t in links if KW.search(f"{u} {t}") and dentro(u, doms)]
                datas = sorted({f"{a}-{m}-{d}" for d, m, a in DATA.findall(texto)}, reverse=True)
                pg.update({"titulo": " ".join(p.titulo.split())[:160], "tipo": tipo_pagina(r["final"], p.titulo, texto),
                           "sinais": len(KW.findall(texto)), "links_com_sinal": [{"url": u, "texto": t} for u, t in dict.fromkeys(kl)][:60],
                           "pdfs": [{"url": u, "texto": t} for u, t in dict.fromkeys(links) if u.lower().split("?")[0].endswith(".pdf")][:60],
                           "datas": datas[:60], "anos": sorted({d[:4] for d in datas}),
                           "paginacao": [u for u, t in links if re.search(r"[?&](page|pagina|start|p)=\d|/page/\d|pr[oó]xim", f"{u} {t}", re.I) and dentro(u, doms)][:10],
                           "trecho": texto[:600]})
                if prof < PROFUNDIDADE:
                    for u, _ in kl:
                        if u not in vistos:
                            fila.append((u, prof + 1))
            O["paginas"].append(pg)
        out["orgaos"][orgao] = O
        print(f"{orgao}: {len(O['paginas'])} páginas · sitemap com sinal {len(O['sitemap_urls_com_sinal'])} · robots {[v['status'] for v in O['robots'].values()]}", flush=True)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: len(v["paginas"]) for k, v in out["orgaos"].items()}


def bruto(urls: list[str]) -> dict:
    """02/10: guarda o HTML COMPLETO (com os scripts) das páginas pedidas, para achar de onde a tabela montada por
    JavaScript busca os dados. Respeita o robots.txt. Saída: biblioteca_alexandria/base/ministerios_publicos/bruto/"""
    pasta = SAIDA.parent / "bruto"; pasta.mkdir(parents=True, exist_ok=True); out = {}
    for u in urls:
        b = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(u)); rp, _ = robots(b)
        if not rp.can_fetch(UA, u):
            out[u] = "robots proíbe"; continue
        r = ler(u); time.sleep(PAUSA)
        nome = re.sub(r"[^a-z0-9]+", "-", u.lower().split("//", 1)[1])[:120] + ".html"
        (pasta / nome).write_bytes(r["corpo"][:3_000_000]); out[u] = {"status": r["status"], "bytes": r["bytes"], "arquivo": nome, "tipo": r["tipo"]}
    (pasta / "indice.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    if "--bruto" in sys.argv:
        print(json.dumps(bruto([a for a in sys.argv[sys.argv.index("--bruto") + 1:] if a.startswith("http")]), ensure_ascii=False))
    else:
        print(json.dumps(run(), ensure_ascii=False))
