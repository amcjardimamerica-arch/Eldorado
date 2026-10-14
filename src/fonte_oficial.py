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


def site_da_prefeitura(municipio: str, uf: str, getter) -> str | None:
    """O site oficial da prefeitura (município.uf.gov.br, com e sem www), conferido."""
    if not municipio or not uf:
        return None
    slug = re.sub(r"[^a-z0-9]", "", _sem(municipio))
    for cand in (f"https://www.{slug}.{uf.lower()}.gov.br/", f"https://{slug}.{uf.lower()}.gov.br/", f"http://www.{slug}.{uf.lower()}.gov.br/"):
        try:
            if getter(cand):
                return cand
        except Exception:  # noqa: BLE001
            continue
    return None


def link_de_origem_pncp(url: str, getter) -> str | None:
    """PNCP: o link de origem que o PRÓPRIO órgão informou (linkSistemaOrigem), pela API pública de consulta."""
    m = re.search(r"/(?:app/)?editais/(\d{14})/(\d{4})/(\d+)", url or "")
    if not m:
        return None
    cnpj, ano, seq = m.groups()
    js = None
    for base in (f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}",     # 14/10 (treino): os 3 endereços da API
                 f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}", f"https://pncp.gov.br/pncp-api/v1/orgaos/{cnpj}/compras/{ano}/{seq}"):
        try:
            js = json.loads(getter(base)); break
        except Exception:  # noqa: BLE001
            continue
    if not js:
        return None
    for campo in ("linkSistemaOrigem", "linkProcessoEletronico"):      # 14/10 (treino): o 2º campo cobre quem não preenche o 1º
        lk = (js.get(campo) or "").strip()
        if lk and eh_fonte(lk):
            return lk
    # 14/10 (treino real): órgão municipal sem link nenhum → o site da prefeitura (município.uf.gov.br), conferido
    un = js.get("unidadeOrgao") or {}; esfera = str((js.get("orgaoEntidade") or {}).get("esferaId") or "")
    mun, uf = un.get("municipioNome"), un.get("ufSigla")
    if mun and uf and esfera in ("M", ""):
        return site_da_prefeitura(mun, uf, getter)
    return None


def diario_original_querido(url: str, getter) -> str | None:
    """Querido Diário: o endereço ORIGINAL do diário, publicado pelo município (API pública do projeto)."""
    m = re.search(r"queridodiario\.ok\.org\.br/(\d{7})/(\d{4}-\d{2}-\d{2})/([0-9a-f]{20,})", url or "")
    if not m:
        return None
    ibge, dia, h = m.groups()
    js = None
    for base in ("https://api.queridodiario.ok.org.br", "https://queridodiario.ok.org.br/api"):   # 14/10 (treino): o endereço que funciona primeiro
        try:
            js = json.loads(getter(f"{base}/gazettes?territory_ids={ibge}&published_since={dia}&published_until={dia}&size=20")); break
        except Exception:  # noqa: BLE001
            continue
    js = js or {"gazettes": []}                       # 14/10: sem a API, o mapa dos raspadores ainda resolve
    gz = js.get("gazettes") or []
    alvo = next((g for g in gz if h in str(g.get("txt_url") or "") + str(g.get("url") or "") + str(g.get("file_checksum") or "")), None) or (gz[0] if len(gz) == 1 else None)
    lk = str((alvo or {}).get("url") or "").strip()
    if lk and eh_fonte(lk):
        return lk
    # 14/10 (pesquisa no GitHub): os raspadores do próprio Querido Diário trazem o endereço OFICIAL do diário de cada
    # município (config/querido_diario_fontes.json, 418 municípios) — vale antes de qualquer adivinhação
    mapa = _mapa_querido().get(ibge) or {}
    for u in mapa.get("urls") or []:
        d = _dom(u)
        if re.search(r"\.gov\.br$", d) and eh_fonte(u):          # domínio do próprio município: é o site da prefeitura
            raiz = f"{urlsplit(u).scheme}://{urlsplit(u).netloc}/"
            try:
                if getter(raiz):
                    return raiz
            except Exception:  # noqa: BLE001
                pass
    # 14/10 (3º treino): a API do projeto só devolve a CÓPIA dele (replicador); o diário é do município — pelo código
    # IBGE (API pública do IBGE) chega-se ao nome e ao estado, e daí ao site da prefeitura
    nome, uf = ((alvo or {}).get("territory_name"), (alvo or {}).get("state_code"))
    if not (nome and uf):
        try:
            m = json.loads(getter(f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{ibge}"))
            nome = m.get("nome"); uf = (((m.get("microrregiao") or {}).get("mesorregiao") or {}).get("UF") or {}).get("sigla") or \
                ((((m.get("regiao-imediata") or {}).get("regiao-intermediaria") or {}).get("UF")) or {}).get("sigla")
        except Exception:  # noqa: BLE001
            nome, uf = None, None                         # 14/10: sem IBGE, ainda vale a plataforma oficial do mapa
    achou = site_da_prefeitura(nome, uf, getter)
    if achou:
        return achou
    # sem site da prefeitura: a plataforma oficial onde o município publica o diário (ex.: doem.org.br na Bahia)
    return next((u for u in (mapa.get("urls") or []) if eh_fonte(u)), None)


_MAPA_Q: dict = {}


def _mapa_querido() -> dict:
    if not _MAPA_Q:
        try:
            _MAPA_Q.update(json.loads((ROOT / "config/querido_diario_fontes.json").read_text(encoding="utf-8")).get("municipios") or {})
        except Exception:  # noqa: BLE001
            _MAPA_Q["_"] = {}
    return _MAPA_Q


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
    if out["replicador"] and "queridodiario" in _dom(url):
        fonte = diario_original_querido(url, getter)
        out["passos"].append(f"Querido Diário → diário original do município: {fonte or 'não encontrado'}")
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
