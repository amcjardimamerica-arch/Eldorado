"""FONTE OFICIAL (titular, 14/10/2026) — a oportunidade se encontra NA FONTE.

Regra:
  · REPLICADOR nunca é fonte oficial: PNCP, Querido Diário, CapitaAI, Captadores, Observatório do Terceiro Setor,
    Farol Cultural, editais.net, GIFE (listas), Funcafé e semelhantes. O motor segue para o lugar que o replicador
    INDICA (no PNCP, o link de origem informado pelo próprio órgão; nos demais, o link de saída da página).
  · FONTE: o site da empresa ou do instituto, o site governamental (.gov.br, .jus.br, .mp.br, .leg.br) ou o da
    instituição nacional/internacional que lança o edital.
  · EXCEÇÕES — plataformas onde o PRÓPRIO emissor publica o edital: Prosas, Mapas Culturais dos governos, sistemas
    de editais do Ministério da Cultura.

Resolvedor (com aprendizado): página do replicador → link para a fonte → PDF do edital na fonte. O que deu certo nos
casos conhecidos (scripts/treino_fontes.py) vira dica por site em estado/aprendizado_fontes.json: o texto do link que
leva à fonte em cada replicador e o trecho de caminho onde ficam os PDFs em cada site oficial.
"""
from __future__ import annotations

import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
APRENDIZADO = ROOT / "estado/aprendizado_fontes.json"

REPLICADORES = ("pncp.gov.br", "queridodiario.ok.org.br", "capitaai.com.br", "captadores.org.br", "observatorio3setor.org.br",
                "farolcultural.com.br", "editais.net", "funcafe.org.br", "editaldeculturaeesporte", "filantropia.ong",
                "gife.org.br", "portaldoterceirosetor", "licitario.com.br", "licitacoes-e", "conlicitacao", "effecti.com.br")
EMISSOR_PROPRIO = ("prosas.com.br", "mapacultural", "mapas.cultura", "culteditais.cultura.gov.br", "editais.cultura.gov.br",
                   "prosas.org", "editais.funarte.gov.br", "transferegov", "plataformamaisbrasil")
NAO_FONTE = ("facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "youtube.com", "whatsapp", "t.me",
             "google.com", "goo.gl", "bit.ly", "wa.me", "mailto:", "javascript:")
CHAVE_LINK = re.compile(r"edital|regulamento|chamad|inscri|site oficial|p[aá]gina oficial|acesse|saiba mais|mais informa|"
                        r"leia mais|clique aqui|link|fonte|original|document", re.I)
CHAVE_PDF = re.compile(r"edital|regulamento|chamada|chamamento|anexo|termo de refer|retifica|resultado|aviso", re.I)


def _dom(u: str) -> str:
    return (urlsplit(str(u or "")).hostname or "").lower().replace("www.", "")


def _sem(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "").lower()) if not unicodedata.combining(c))


def eh_replicador(url: str) -> bool:
    d = _dom(url)
    return bool(d) and any(r in d for r in REPLICADORES) and not any(e in d or e in str(url) for e in EMISSOR_PROPRIO)


def eh_fonte(url: str) -> bool:
    return bool(_dom(url)) and not eh_replicador(url) and not any(n in str(url).lower() for n in NAO_FONTE)


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self._a = None; self._txt = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._a = dict(attrs).get("href"); self._txt = []

    def handle_data(self, data):
        if self._a is not None:
            self._txt.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._a:
            self.links.append((self._a, " ".join("".join(self._txt).split())[:160]))
            self._a = None


def links(html: str, base: str) -> list[tuple[str, str]]:
    p = _Links()
    try:
        p.feed(html or "")
    except Exception:  # noqa: BLE001
        pass
    return [(urljoin(base, h), t) for h, t in p.links if h and not h.startswith("#")]


def _aprendizado() -> dict:
    try:
        return json.loads(APRENDIZADO.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"replicadores": {}, "oficiais": {}}


def _tokens(*txt) -> set:
    return {w for w in re.findall(r"[a-z0-9]{4,}", _sem(" ".join(str(t or "") for t in txt)))
            if w not in {"edital", "editais", "chamada", "publica", "publico", "projeto", "projetos", "para", "com", "2025", "2026", "2027", "https", "http"}}


def escolher_fonte(url_rep: str, html: str, titulo: str = "", orgao: str = "", A: dict | None = None) -> tuple[str | None, float, str]:
    """Na página do replicador, o link que mais provavelmente leva à FONTE (pontuação, motivo)."""
    A = A if A is not None else _aprendizado()
    dica = (A.get("replicadores") or {}).get(_dom(url_rep)) or {}
    tk = _tokens(titulo, orgao); melhor = (None, 0.0, "")
    for href, txt in links(html, url_rep):
        if not eh_fonte(href) or _dom(href) == _dom(url_rep):
            continue
        p, por = 0.0, []
        if CHAVE_LINK.search(txt):
            p += 2; por.append("texto do link")
        st = _sem(txt)
        for anc, n in (dica.get("ancoras") or {}).items():
            if anc and anc in st:
                p += 1.5 + min(2, n / 3); por.append(f"aprendido: '{anc}'")
                break
        d = _dom(href)
        if re.search(r"\.gov\.br$|\.jus\.br$|\.mp\.br$|\.leg\.br$|\.edu\.br$|\.org\.br$|\.org$|\.int$", d):
            p += 1; por.append("domínio institucional")
        sobre = tk & _tokens(d.replace(".", " "), href)
        if sobre:
            p += min(3, 1.5 * len(sobre)); por.append("órgão/título no endereço")
        if re.search(r"\.pdf($|\?)", href, re.I):
            p += 1; por.append("PDF")
        if p > melhor[1]:
            melhor = (href, p, ", ".join(por))
    return melhor


def achar_pdfs(url_fonte: str, html: str, titulo: str = "", A: dict | None = None, limite: int = 3) -> list[dict]:
    """Na página da FONTE, os PDFs do edital (pontuados pelo texto do link, pelo título e pelo aprendido do site)."""
    A = A if A is not None else _aprendizado()
    dica = (A.get("oficiais") or {}).get(_dom(url_fonte)) or {}
    tk = _tokens(titulo); achados = []
    for href, txt in links(html, url_fonte):
        h = href.lower()
        if not (re.search(r"\.pdf($|\?)", h) or re.search(r"download|arquivo|anexo|documento|/files?/|uploads", h)):
            continue
        p = 0.0
        if re.search(r"\.pdf($|\?)", h):
            p += 2
        if CHAVE_PDF.search(txt) or CHAVE_PDF.search(h):
            p += 2
        p += min(3, len(tk & _tokens(txt, href)))
        for seg, n in (dica.get("pdf_padroes") or {}).items():
            if seg and seg in h:
                p += 1 + min(2, n / 3); break
        if p >= 3:
            achados.append({"url": href, "texto": txt, "pontos": round(p, 1)})
    return sorted(achados, key=lambda x: -x["pontos"])[:limite]


def link_de_origem_pncp(url: str, getter) -> str | None:
    """PNCP: o link de origem que o PRÓPRIO órgão informou (linkSistemaOrigem), pela API pública de consulta."""
    m = re.search(r"/(?:app/)?editais/(\d{14})/(\d{4})/(\d+)", url or "")
    if not m:
        return None
    cnpj, ano, seq = m.groups()
    try:
        js = json.loads(getter(f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}"))
    except Exception:  # noqa: BLE001
        return None
    lk = (js.get("linkSistemaOrigem") or "").strip()
    return lk if lk and eh_fonte(lk) else None


def resolver(url: str, titulo: str = "", orgao: str = "", getter=None, A: dict | None = None) -> dict:
    """Do replicador à fonte e ao PDF. getter(url) -> texto (injeção para testes e para a rota de coleta)."""
    A = A if A is not None else _aprendizado()
    out = {"origem": url, "replicador": eh_replicador(url), "fonte": None, "pdfs": [], "passos": []}
    if not getter:
        return out
    fonte = url if not out["replicador"] else None
    if out["replicador"] and "pncp.gov.br" in _dom(url):
        fonte = link_de_origem_pncp(url, getter)
        out["passos"].append(f"PNCP → link de origem do órgão: {fonte or 'não informado'}")
    if out["replicador"] and not fonte:
        try:
            html = getter(url)
        except Exception as e:  # noqa: BLE001
            out["passos"].append(f"replicador ilegível: {type(e).__name__}"); return out
        fonte, pts, por = escolher_fonte(url, html, titulo, orgao, A)
        out["passos"].append(f"replicador → fonte ({pts} pontos: {por})" if fonte else "replicador sem link para a fonte")
    out["fonte"] = fonte
    if fonte:
        if re.search(r"\.pdf($|\?)", fonte, re.I):
            out["pdfs"] = [{"url": fonte, "texto": "o próprio link é o PDF", "pontos": 9}]
        else:
            try:
                out["pdfs"] = achar_pdfs(fonte, getter(fonte), titulo, A)
                out["passos"].append(f"fonte → {len(out['pdfs'])} PDF(s) do edital")
            except Exception as e:  # noqa: BLE001
                out["passos"].append(f"fonte ilegível: {type(e).__name__}")
    return out
