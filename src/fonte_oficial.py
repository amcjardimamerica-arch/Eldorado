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


# ── NAVEGAÇÃO DENTRO DO SITE OFICIAL (titular, 15/10/2026) ─────────────────────────────────────────────────────────
# Do site ao PDF: quando a página da fonte não traz o PDF, o resolvedor entra no próprio site pelos caminhos onde os
# órgãos publicam editais (Editais, Chamamentos, Publicações, Transparência, Licitações, PNAB…), pontuando cada link
# pelo número e pelas palavras do título. Limites: mesmo site, 2 níveis, NAV_PAGINAS páginas. WordPress: busca interna
# e biblioteca de mídia pelo número do edital.
NAV = re.compile(r"edita(?:l|is)|chamamentos?|chamadas?|sele[çc](?:[ãa]o|[õo]es)|publica[çc](?:[ãa]o|[õo]es)|transpar[êe]ncia|"
                 r"licita[çc](?:[ãa]o|[õo]es)|concursos?|processos? seletivos?|documentos|downloads?|arquivos|di[áa]rio oficial|"
                 r"fomento|aldir blanc|pnab|paulo gustavo|terceiro setor|\bosc\b|mrosc|parcerias?|conv[êe]nios?|"
                 r"cultura|assist[êe]ncia social|leis? de incentivo|oportunidades|inscri[çc][õo]es", re.I)
NAV_FORA = re.compile(r"mailto:|tel:|javascript:|whatsapp|facebook|instagram|twitter|youtube|linkedin|/login|/wp-admin|"
                      r"\.(?:jpe?g|png|gif|svg|webp|css|js|ico|mp4|mp3|zip|rar)(?:$|\?)|/feed/?$|/tag/|/author/|#", re.I)
NAV_PAGINAS = 10
NUMERO = re.compile(r"\b0*(\d{1,4})\s*[/.-]\s*(20\d{2})\b")


def _numero(titulo: str) -> tuple[str, str] | None:
    m = NUMERO.search(str(titulo or ""))
    return (m.group(1), m.group(2)) if m else None


def _tem_numero(txt: str, num: tuple[str, str] | None) -> bool:
    if not num:
        return False
    return bool(re.search(rf"(?<!\d)0*{num[0]}\s*[/.\-_]\s*{num[1]}(?!\d)|{num[1]}\s*[/.\-_]\s*0*{num[0]}(?!\d)", txt))


def _mesmo_site(a: str, b: str) -> bool:
    da, db = _dom(a), _dom(b)
    return bool(da and db) and (da == db or da.endswith("." + db) or db.endswith("." + da))


def _pontuar_navegacao(href: str, txt: str, tk: set, num) -> float:
    alvo = f"{txt} {href}"
    p = 0.0
    if NAV.search(alvo):
        p += 2
    p += min(4, 1.5 * len(tk & _tokens(txt, href)))
    if _tem_numero(alvo, num):
        p += 5
    if re.search(r"20(2[4-7])", href):
        p += 0.5
    return p


def _pdf_forte(pdf: dict, tk: set, num) -> bool:
    alvo = f"{pdf.get('texto', '')} {pdf.get('url', '')}"
    return _tem_numero(alvo, num) or len(tk & _tokens(alvo)) >= 2


def navegar(url_fonte: str, html: str, titulo: str, getter, A: dict | None = None, limite: int = 3,
            max_paginas: int = NAV_PAGINAS) -> tuple[list[dict], list[str]]:
    """Entra no site oficial atrás do PDF do edital. Devolve (pdfs, caminho percorrido)."""
    tk, num = _tokens(titulo), _numero(titulo)
    achados: dict = {}
    caminho: list[str] = []

    def colher(url: str, h: str, nivel: int):
        for pdf in achar_pdfs(url, h, titulo, A, limite=8):
            pdf = dict(pdf)
            if _pdf_forte(pdf, tk, num):
                pdf["pontos"] = round(pdf["pontos"] + 3, 1)
            pdf["achado_em"] = url; pdf["nivel"] = nivel
            if pdf["url"] not in achados or achados[pdf["url"]]["pontos"] < pdf["pontos"]:
                achados[pdf["url"]] = pdf

    def candidatos(url: str, h: str, vistos: set) -> list[tuple[float, str, str]]:
        out = []
        for href, txt in links(h, url):
            href = href.split("#")[0]
            if not href or href in vistos or NAV_FORA.search(href) or not _mesmo_site(href, url_fonte):
                continue
            if re.search(r"\.pdf($|\?)", href, re.I):
                continue
            p = _pontuar_navegacao(href, txt, tk, num)
            if p >= 2:
                out.append((p, href, txt))
        return sorted(out, key=lambda x: -x[0])

    colher(url_fonte, html, 0)
    vistos = {url_fonte.split("#")[0]}
    fila = [(p, h, t, 1) for p, h, t in candidatos(url_fonte, html, vistos)[:12]]
    # WordPress: busca interna e biblioteca de mídia pelo número (sem gastar o orçamento de navegação)
    base = "{0.scheme}://{0.netloc}".format(urlsplit(url_fonte))
    if re.search(r"wp-content|wp-json|wordpress", html or "", re.I) and (num or tk):
        termo = f"{num[0]}/{num[1]}" if num else " ".join(sorted(tk)[:3])
        try:
            midia = json.loads(getter(f"{base}/wp-json/wp/v2/media?search={termo.replace(' ', '+')}&per_page=10") or "[]")
            for it in midia if isinstance(midia, list) else []:
                u = str((it or {}).get("source_url") or "")
                if u.lower().endswith(".pdf"):
                    t = str(((it or {}).get("title") or {}).get("rendered") or "")
                    achados.setdefault(u, {"url": u, "texto": t or "biblioteca de mídia", "pontos": 6.0, "achado_em": "wp-json/media", "nivel": 1})
            caminho.append(f"WordPress: biblioteca de mídia por '{termo}'")
        except Exception:  # noqa: BLE001
            pass
        fila.insert(0, (9.0, f"{base}/?s={termo.replace(' ', '+')}", "busca interna", 1))
    lidas = 0
    while fila and lidas < max_paginas:
        if any(_pdf_forte(p, tk, num) for p in achados.values()):
            break
        fila.sort(key=lambda x: -x[0])
        p, href, txt, nivel = fila.pop(0)
        if href in vistos:
            continue
        vistos.add(href)
        try:
            h = getter(href)
        except Exception:  # noqa: BLE001
            continue
        lidas += 1
        caminho.append(f"nível {nivel}: {txt[:40] or href} ({p:.1f})")
        colher(href, h or "", nivel)
        if nivel < 2:
            for p2, h2, t2 in candidatos(href, h or "", vistos)[:8]:
                fila.append((p2 - 0.5, h2, t2, nivel + 1))
    pdfs = sorted(achados.values(), key=lambda x: -x["pontos"])[:limite]
    return pdfs, caminho



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


def arquivos_pncp(url: str, getter, titulo: str = "", limite: int = 3) -> list[dict]:
    """15/10/2026 (treino): quando o link de origem do PNCP é sistema de compras (Comprasnet, Licitanet, BNC, SEI —
    aplicativo com login, sem página navegável), o edital é o ARQUIVO QUE O PRÓPRIO ÓRGÃO publicou na compra
    (/arquivos/N — o Cartório já o aceita como documento oficial). O tipo "Edital" vem primeiro."""
    m = re.search(r"/(?:app/)?editais/(\d{14})/(\d{4})/(\d+)", url or "")
    if not m:
        return []
    cnpj, ano, seq = m.groups()
    lista = None
    for base in (f"https://pncp.gov.br/pncp-api/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos",
                 f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos"):
        try:
            lista = json.loads(getter(base)); break
        except Exception:  # noqa: BLE001
            continue
    if not isinstance(lista, list):
        return []
    out = []
    for a in lista:
        if not isinstance(a, dict) or a.get("statusAtivo") is False:
            continue
        u = str(a.get("url") or a.get("uri") or "")
        if not u:
            continue
        tipo = str(a.get("tipoDocumentoNome") or ""); tit = str(a.get("titulo") or "")
        p = 4.0 + (4 if re.search(r"(?i)edital", tipo) else 2 if re.search(r"(?i)termo de refer|aviso", tipo) else 0)
        p += min(2, len(_tokens(titulo) & _tokens(tit)))
        out.append({"url": u, "texto": f"{tipo}: {tit}".strip(": "), "pontos": round(p, 1), "achado_em": "PNCP — arquivo publicado pelo órgão"})
    return sorted(out, key=lambda x: -x["pontos"])[:limite]


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


def resolver(url: str, titulo: str = "", orgao: str = "", getter=None, A: dict | None = None, navegacao: bool = True) -> dict:
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
                html_fonte = getter(fonte)
                out["pdfs"] = achar_pdfs(fonte, html_fonte, titulo, A)
                out["passos"].append(f"fonte → {len(out['pdfs'])} PDF(s) do edital")
                tk, num = _tokens(titulo), _numero(titulo)
                if navegacao and not any(_pdf_forte(p, tk, num) for p in out["pdfs"]):
                    pdfs, caminho = navegar(fonte, html_fonte, titulo, getter, A)
                    out["passos"] += caminho
                    if pdfs and (not out["pdfs"] or pdfs[0]["pontos"] > out["pdfs"][0]["pontos"]):
                        out["pdfs"] = pdfs
                        out["passos"].append(f"navegação no site → {len(pdfs)} PDF(s): {pdfs[0]['url'][:100]}")
            except Exception as e:  # noqa: BLE001
                out["passos"].append(f"fonte ilegível: {type(e).__name__}")
    # PNCP: sem PDF forte pela fonte (sistema de compras, login, página ilegível) → o edital publicado pelo órgão
    if out["replicador"] and "pncp.gov.br" in _dom(url) and navegacao:
        tk, num = _tokens(titulo), _numero(titulo)
        if not any(_pdf_forte(p, tk, num) for p in out["pdfs"]):
            arq = arquivos_pncp(url, getter, titulo)
            if arq:
                out["pdfs"] = arq
                out["passos"].append(f"PNCP → arquivo publicado pelo próprio órgão: {arq[0]['texto'][:60]}")
    return out
