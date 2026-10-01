"""MOTOR REGULAR — AGREGADORES DE EDITAIS (titular, 28/09).

Sites que REPUBLICAM editais de fontes oficiais servem como INDÍCIO: este motor lê as listagens deles, extrai de cada
edital o título, o prazo e — o que importa — o LINK DA FONTE OFICIAL, e entrega ao fluxo das oportunidades. De lá seguem
curadoria, validação, livro de oportunidade e o estudo do Piloto - Interceptador, sempre sobre a fonte oficial; a página do
agregador fica só como indício (nunca é "site oficial").

Fontes (sondagem de 28/09, biblioteca_alexandria/base/sondagem_agregadores.json):
  capitaai.com.br     listagem de editais para ONGs · 44 editais · 8/8 com link oficial e prazo
  farolcultural.art   editais culturais · 20 na listagem · 5/8 com link oficial (muitos no PNCP) · 8/8 com prazo
  idis.org.br (RSS)   notícias; entra só o que fala de edital/chamada
  (mabus.com.br: listagens inexistentes e conteúdo de licitação/compra — fora)
Educado com os sites: respeita o robots.txt (só as listagens públicas), 1 s entre páginas, no máximo 40 editais por
site e por rodada. Roda no servidor (monitoramento diário). Saída: estado/agregadores/itens.json.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "estado/agregadores/itens.json"
UA = {"User-Agent": "Mozilla/5.0 (Eldorado; associacao sem fins lucrativos; leitura de editais publicos)"}
FONTES = [
    {"id": "capitaai", "nome": "CapitaAI — editais abertos para ONGs", "listas": ["https://capitaai.com.br/editais-abertos/para-ong"]},
    {"id": "farolcultural", "nome": "Farol Cultural — editais culturais", "listas": ["https://farolcultural.art/editais", "https://farolcultural.art/"]},
    {"id": "idis", "nome": "IDIS — notícias (RSS)", "rss": "https://www.idis.org.br/feed/"},
]
EDITAL = re.compile(r"edital|chamad|chamamento|sele[cç][aã]o|pr[eê]mio|inscri|credenciamento|fomento|/e/", re.I)
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
                                     "outubro", "novembro", "dezembro"], 1)}
UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()


class _P(HTMLParser):
    def __init__(self):
        super().__init__(); self.l = []; self._h = None; self._t = []; self.texto = []; self.titulo = ""; self._em_h1 = False
    def handle_starttag(self, tag, a):
        if tag == "a":
            self._h = dict(a).get("href"); self._t = []
        if tag in ("h1", "title") and not self.titulo:
            self._em_h1 = True
    def handle_endtag(self, tag):
        if tag == "a" and self._h:
            self.l.append((self._h, " ".join("".join(self._t).split())[:180])); self._h = None
        if tag in ("h1", "title"):
            self._em_h1 = False
    def handle_data(self, d):
        self.texto.append(d)
        if self._h is not None:
            self._t.append(d)
        if self._em_h1 and d.strip() and not self.titulo:
            self.titulo = " ".join(d.split())[:200]


def _get(url: str, t: int = 30) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
            return r.read(4_000_000).decode("utf-8", "ignore")
    except Exception:
        return ""


def _prazo(texto: str) -> str | None:
    t = re.sub(r"\s+", " ", texto)
    m = re.search(r"(?:inscri[cç][õo]es?[^.]{0,40}?at[eé]|prazo[^0-9]{0,25}|at[eé])\s*(\d{1,2})/(\d{1,2})/(\d{2,4})", t, re.I)
    if m:
        d, mo, a = int(m.group(1)), int(m.group(2)), int(m.group(3)); a = a + 2000 if a < 100 else a
        return f"{a:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else None
    m = re.search(r"(?:inscri[cç][õo]es?[^.]{0,40}?at[eé]|prazo[^0-9]{0,25}|at[eé])\s*(\d{1,2}) de ([a-zç]+) de (\d{4})", t, re.I)
    if m and m.group(2).lower() in MESES:
        return f"{int(m.group(3)):04d}-{MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None


def _oficial(pagina: str, links: list, titulo: str = "") -> str | None:
    """O link da FONTE OFICIAL do edital. Lei citada no texto (planalto, lexml, diários de legislação) não é fonte do
    edital; ganha quem tem sinal de edital e, sobretudo, o domínio do órgão que aparece no título (Itapajé → itapaje.ce.gov.br)."""
    import unicodedata
    from .sites_oficiais import e_republicador
    sem = lambda x: "".join(c for c in unicodedata.normalize("NFKD", x.lower()) if not unicodedata.combining(c))
    toks = [w for w in re.findall(r"[a-z]{5,}", sem(titulo)) if w not in {"edital", "publico", "chamamento", "selecao", "credenciamento", "organizacoes", "sociedade", "projetos", "recursos", "captar"}]
    host = urlsplit(pagina).hostname
    cands = []
    for ordem, (h, t) in enumerate(links):
        s = urljoin(pagina, h or "")
        hs = (urlsplit(s).hostname or "")
        if not s.startswith("http") or hs in (host, "") or e_republicador(s):
            continue
        if re.search(r"facebook|instagram|linkedin|twitter|whatsapp|youtube|wa\.me|google|apple|t\.me", s):
            continue
        if re.search(r"planalto\.gov\.br|/ccivil|lexml|legislacao|normas\.leg|jusbrasil|/leis?/|lei-?\d", s, re.I):
            continue                                            # lei citada não é a fonte do edital
        pts = (3 if re.search(r"edital|inscri|regulamento|chamad|oportunidade|\.pdf|pncp\.gov\.br/app/editais|mapacultural|prosas", s + " " + t, re.I) else 0) + \
              (2 if re.search(r"\.gov\.br|\.leg\.br|\.jus\.br|\.org\.br|\.gov\.|\.org", s) else 0) + \
              (4 if any(w in sem(hs) for w in toks) else 0)
        if pts:
            cands.append((pts, -ordem, s))
    return sorted(cands, reverse=True)[0][2] if cands else None


def _uf(texto: str) -> str | None:
    m = re.search(r"\b(" + "|".join(UFS) + r")\b(?:\s*[-–/]|\s*$)", texto)
    return m.group(1) if m else None


def _ler_listagem(f: dict, maximo: int = 40) -> list[dict]:
    vistos, itens = set(), []
    for lista in f.get("listas", []):
        html = _get(lista); p = _P(); p.feed(html)
        host = urlsplit(lista).hostname
        for h, t in p.l:
            u = urljoin(lista, h or "")
            if urlsplit(u).hostname != host or u in vistos or u.rstrip("/") == lista.rstrip("/"):
                continue
            if not (EDITAL.search(u) or EDITAL.search(t)) or re.search(r"/(login|cadastro|planos|blog|sobre|contato)", u):
                continue
            vistos.add(u)
            if len(vistos) > maximo:
                break
        time.sleep(1)
    for u in list(vistos)[:maximo]:
        html = _get(u); p = _P(); p.feed(html)
        texto = " ".join(p.texto)
        titulo = re.sub(r"\s*[·|–-]\s*(CapitaAI|Capitaai|Farol Cultural|FAROL|IDIS)[^·|]*$", "", p.titulo or "").strip()   # sem o nome do site
        if len(titulo.split()) < 3 or not EDITAL.search(titulo + " " + texto[:3000]):
            continue
        itens.append({"id": "agr-" + hashlib.sha1(u.encode()).hexdigest()[:12], "fonte": f["id"], "titulo": titulo,
                      "pagina_agregador": u, "link_oficial": _oficial(u, p.l, titulo), "prazo": _prazo(texto),
                      "uf": _uf(titulo) or _uf(texto[:1500]), "visto_em": date.today().isoformat()})
        time.sleep(1)
    return itens


def _ler_rss(f: dict) -> list[dict]:
    xml = _get(f["rss"]); itens = []
    for bloco in re.findall(r"<item>([\s\S]*?)</item>", xml)[:30]:
        tit = re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(r"<title>([\s\S]*?)</title>", bloco) or [None, ""])[1]).strip()
        link = (re.search(r"<link>([\s\S]*?)</link>", bloco) or [None, ""])[1].strip()
        if not EDITAL.search(tit) or not link:
            continue
        html = _get(link); p = _P(); p.feed(html)
        itens.append({"id": "agr-" + hashlib.sha1(link.encode()).hexdigest()[:12], "fonte": f["id"], "titulo": tit[:200],
                      "pagina_agregador": link, "link_oficial": _oficial(link, p.l, tit), "prazo": _prazo(" ".join(p.texto)),
                      "uf": _uf(tit), "visto_em": date.today().isoformat()})
        time.sleep(1)
    return itens


def rodar() -> dict:
    ant = {}
    try:
        ant = {x["id"]: x for x in json.loads(SAIDA.read_text(encoding="utf-8")).get("itens", [])}
    except Exception:
        pass
    rel = {}
    for f in FONTES:
        try:
            novos = _ler_rss(f) if f.get("rss") else _ler_listagem(f)
        except Exception as e:
            rel[f["id"]] = {"erro": f"{type(e).__name__}"}; continue
        for x in novos:
            x["primeiro_visto"] = (ant.get(x["id"]) or {}).get("primeiro_visto") or x["visto_em"]
            ant[x["id"]] = {**(ant.get(x["id"]) or {}), **{k: v for k, v in x.items() if v}, "link_oficial": x.get("link_oficial"), "titulo": x.get("titulo")}
        rel[f["id"]] = {"lidos": len(novos), "com_link_oficial": sum(1 for x in novos if x.get("link_oficial")),
                        "com_prazo": sum(1 for x in novos if x.get("prazo"))}
    hoje = date.today().isoformat()
    vivos = [x for x in ant.values() if not x.get("prazo") or x["prazo"] >= hoje]     # prazo vencido sai
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Fontes")[0].strip(),
           "por_fonte": rel, "itens": sorted(vivos, key=lambda x: str(x.get("prazo") or "9999"))}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"por_fonte": rel, "itens_vivos": len(vivos)}


if __name__ == "__main__":
    print(json.dumps(rodar(), ensure_ascii=False, indent=1))
