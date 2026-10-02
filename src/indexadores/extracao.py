"""Extração dos indícios: título, prazo, valor, UF, link oficial, perfil do público e chave de duplicata.

Regras do sistema que valem aqui:
  - o prazo do agregador é PISTA (vai em `prazo`, e o fluxo o trata como `prazo_agregador`); só a fonte oficial
    confirma o prazo;
  - o link oficial é o do FINANCIADOR ou da plataforma oficial de inscrição — nunca o próprio agregador, notícia,
    rede social, buscador ou lei citada;
  - o que a página não diz fica None; nada é estimado;
  - conteúdo coletado é dado: texto com cara de instrução para IA vai para quarentena.
"""
from __future__ import annotations

import html as _html
import json
import re
import unicodedata
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode

MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
                                     "setembro", "outubro", "novembro", "dezembro"], 1)}
MESES.update({"marco": 3})
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
ESTADOS = {"acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA", "ceara": "CE",
           "distrito federal": "DF", "espirito santo": "ES", "goias": "GO", "maranhao": "MA", "mato grosso do sul": "MS",
           "mato grosso": "MT", "minas gerais": "MG", "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE",
           "piaui": "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS", "rondonia": "RO",
           "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO"}
EDITAL = re.compile(r"edital|chamad|chamamento|sele[cç][aã]o|pr[eê]mio|inscri|credenciamento|fomento|apoio a projetos|"
                    r"call for|grant|funding|proposals|fellowship|award|open call", re.I)
INJECAO = re.compile(r"ignore (all |the )?(previous|prior) instructions|ignore as instru[cç][õo]es|you are (now )?an? (ai|assistant)|"
                     r"system prompt|desconsidere (as|todas)|aja como|act as a|<\s*script", re.I)


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", sem_acento(s).lower()).strip()


# ------------------------------------------------------------------ HTML
class _Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.textos: list[str] = []
        self.titulo = ""
        self.h1 = ""
        self.meta: dict = {}
        self.jsonld_brutos: list[str] = []
        self._a = None
        self._at: list[str] = []
        self._em = None
        self._ignorar = 0
        self._ld = False
        self._ldbuf: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            if tag == "script" and "ld+json" in (d.get("type") or ""):
                self._ld, self._ldbuf = True, []
            else:
                self._ignorar += 1
            return
        if tag == "a":
            self._a, self._at = d.get("href"), []
        elif tag in ("title", "h1"):
            self._em = tag
        elif tag == "meta":
            k = (d.get("property") or d.get("name") or "").lower()
            if k in ("og:title", "og:description", "description", "og:url", "article:published_time", "article:modified_time"):
                self.meta[k] = d.get("content") or ""
        elif tag in ("br", "p", "div", "li", "tr", "h2", "h3", "h4"):
            self.textos.append("\n")

    def handle_endtag(self, tag):
        if tag == "script" and self._ld:
            self.jsonld_brutos.append("".join(self._ldbuf)); self._ld = False; return
        if tag in ("script", "style", "noscript", "svg"):
            self._ignorar = max(0, self._ignorar - 1); return
        if tag == "a" and self._a is not None:
            self.links.append((self._a, " ".join("".join(self._at).split())[:200])); self._a = None
        if tag == self._em:
            self._em = None

    def handle_data(self, d):
        if self._ld:
            self._ldbuf.append(d); return
        if self._ignorar:
            return
        self.textos.append(d)
        if self._a is not None:
            self._at.append(d)
        if self._em == "title" and not self.titulo:
            self.titulo = " ".join(d.split())[:300]
        elif self._em == "h1":
            self.h1 = (self.h1 + " " + " ".join(d.split())).strip()[:300]


def pagina(html: str) -> _Pagina:
    p = _Pagina()
    try:
        p.feed(html or "")
    except Exception:
        pass
    return p


def texto_de(html: str, limite: int = 60_000) -> str:
    p = pagina(html)
    t = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.textos))
    return re.sub(r"\n\s*\n+", "\n", t).strip()[:limite]


def html_para_texto(fragmento: str, limite: int = 20_000) -> str:
    return texto_de(f"<div>{fragmento or ''}</div>", limite)


def jsonld(html_ou_pagina) -> list[dict]:
    """Todos os objetos JSON-LD da página, com @graph achatado."""
    p = html_ou_pagina if isinstance(html_ou_pagina, _Pagina) else pagina(html_ou_pagina)
    saida = []
    for bruto in p.jsonld_brutos:
        try:
            dado = json.loads(bruto.strip())
        except Exception:
            continue
        pilha = dado if isinstance(dado, list) else [dado]
        while pilha:
            x = pilha.pop(0)
            if not isinstance(x, dict):
                continue
            if isinstance(x.get("@graph"), list):
                pilha.extend(x["@graph"])
            saida.append(x)
    return saida


def de_tipo(objs: list[dict], *tipos: str) -> list[dict]:
    t = {x.lower() for x in tipos}
    out = []
    for o in objs:
        ty = o.get("@type")
        tys = ty if isinstance(ty, list) else [ty]
        if any(str(y or "").lower() in t for y in tys):
            out.append(o)
    return out


def limpar(s, n: int = 300) -> str:
    return re.sub(r"\s+", " ", _html.unescape(str(s or ""))).strip()[:n]


def limpar_titulo(t: str, *nomes_site: str) -> str:
    t = limpar(t, 400)
    for nome in nomes_site:
        if nome:
            t = re.sub(r"\s*[|·–—-]\s*" + re.escape(nome) + r".*$", "", t, flags=re.I)
    return t.strip(" -–—|·")[:300]


# ------------------------------------------------------------------ prazo, valor, UF
def _data_ok(a: int, m: int, d: int, ref: date) -> str | None:
    try:
        x = date(a, m, d)
    except ValueError:
        return None
    if not (ref.year - 1 <= x.year <= ref.year + 3):
        return None
    return x.isoformat()


_GATILHO = r"(?:inscri[cç][õo]es?|prazo|encerra\w*|at[eé]|deadline|due|submiss\w*|candidaturas?|propostas?|limite)"


def prazo(texto: str, ref: date | None = None) -> str | None:
    """A data que fecha as inscrições, quando o texto a diz perto de um gatilho ('inscrições até', 'prazo',
    'deadline'). Datas soltas não contam. Sem ano ('até 02/10'): o próximo 02/10 a partir de `ref`."""
    ref = ref or date.today()
    t = re.sub(r"\s+", " ", sem_acento(str(texto or ""))).lower()
    cands: list[str] = []
    gat = r"\b" + _GATILHO.replace("[cç]", "c").replace("[õo]", "o").replace("[eé]", "e")
    # período "de 01/09/2026 a 30/09/2026" perto de um gatilho: vale o FIM do período
    for m in re.finditer(gat + r"[^0-9]{0,60}?(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\s*(?:a|ate|-|–|to|until|e)\s*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", t):
        d, mo, a = int(m.group(4)), int(m.group(5)), int(m.group(6)); a = a + 2000 if a < 100 else a
        x = _data_ok(a, mo, d, ref)
        if x:
            cands.append(x)
    if cands:
        futuras = sorted(c for c in cands if c >= ref.isoformat())
        return futuras[0] if futuras else sorted(cands)[-1]
    for m in re.finditer(gat + r"[^0-9]{0,40}?(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", t):
        d, mo, a = int(m.group(1)), int(m.group(2)), int(m.group(3)); a = a + 2000 if a < 100 else a
        x = _data_ok(a, mo, d, ref)
        if x:
            cands.append(x)
    meses_rx = "|".join(sorted({sem_acento(k) for k in MESES}, key=len, reverse=True))
    for m in re.finditer(r"\b(?:inscricoes?|prazo|encerra\w*|ate)[^0-9]{0,40}?(\d{1,2})\s*[°o]?\s*(?:de\s+)?(" + meses_rx + r")\b(?:\s*(?:de\s+)?(\d{4}))?", t):
        d, mo = int(m.group(1)), MESES[m.group(2)]
        if m.group(3):
            x = _data_ok(int(m.group(3)), mo, d, ref)
        else:                                            # "inscrições até 13 de novembro": o próximo 13/11
            x = next((y for y in (_data_ok(a, mo, d, ref) for a in (ref.year, ref.year + 1)) if y and y >= ref.isoformat()), None)
        if x:
            cands.append(x)
    mon_rx = "|".join(sorted(MONTHS, key=len, reverse=True))
    for m in re.finditer(r"(?:deadline|due|closes?|until|by)[^0-9a-z]{0,20}(?:(\d{1,2})[\s-]+(" + mon_rx + r")[a-z]*[\s,-]+(\d{2,4})|(" + mon_rx + r")[a-z]*\s+(\d{1,2}),?\s+(\d{4}))", t):
        if m.group(1):
            d, mo, a = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))
        else:
            d, mo, a = int(m.group(5)), MONTHS[m.group(4)], int(m.group(6))
        a = a + 2000 if a < 100 else a
        x = _data_ok(a, mo, d, ref)
        if x:
            cands.append(x)
    if not cands:
        for m in re.finditer(r"(?:inscricoes?[^0-9]{0,25}ate|prazo[^0-9]{0,15}|ate)\s*(\d{1,2})/(\d{1,2})(?![/\d])", t):
            d, mo = int(m.group(1)), int(m.group(2))
            for a in (ref.year, ref.year + 1):
                x = _data_ok(a, mo, d, ref)
                if x and x >= ref.isoformat():
                    cands.append(x); break
    if not cands:
        return None
    futuras = sorted(c for c in cands if c >= ref.isoformat())
    return futuras[0] if futuras else sorted(cands)[-1]


def valor(texto: str) -> str | None:
    t = str(texto or "")
    m = re.search(r"(R\$|US\$|USD|EUR|€|£)\s?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?(?:\s?(?:milh[õo]es|milh[ãa]o|mil|mi\b|bi\b))?", t, re.I)
    return limpar(m.group(0), 40) if m else None


def uf(texto: str) -> str | None:
    t = str(texto or "")
    m = re.search(r"(?:[-–/(,]\s*|\b)(" + "|".join(UFS) + r")\b(?:\s*[)\-–/,.]|\s*$)", t)
    if m:
        return m.group(1)
    tn = " " + norm(t) + " "
    for nome, sigla in sorted(ESTADOS.items(), key=lambda x: -len(x[0])):
        prefixo = r"(?:estado d[eoa]s?|governo d[eoa]s?|secretaria .{0,40}d[eoa]s?)" if nome == "para" else \
            r"(?:estado d[eoa]s?|governo d[eoa]s?|secretaria .{0,40}d[eoa]s?|de|do|da)"
        if re.search(prefixo + r"\s+" + nome + r"\b", tn):
            return sigla
    return None


def uf_do_endereco(u: str | None) -> str | None:
    """UF pelo domínio do órgão: sobral.ce.gov.br → CE, mapacultural.secult.ce.gov.br → CE, mapagoiano.cultura.go.gov.br → GO."""
    h = (urlsplit(str(u or "")).hostname or "").lower()
    m = re.search(r"\.([a-z]{2})\.(?:gov|leg|jus|mp)\.br$", h)
    if m and m.group(1).upper() in UFS:
        return m.group(1).upper()
    return None


# ------------------------------------------------------------------ link oficial
_LIXO = re.compile(r"facebook|instagram|linkedin|twitter|x\.com/|whatsapp|wa\.me|youtube|youtu\.be|t\.me|tiktok|"
                   r"google\.|goo\.gl|apple\.com|bit\.ly|addtoany|sharethis|mailto:|javascript:|wp-login|/feed/?$|/tag/|/category/|/author/",
                   re.I)
_LEI = re.compile(r"planalto\.gov\.br|/ccivil|lexml|legislacao|normas\.leg|jusbrasil|/leis?/|lei-?\d", re.I)
_SINAL = re.compile(r"edital|inscri|regulamento|chamad|oportunidade|selecao|seleção|premio|prêmio|award|apply|call|grant|\.pdf|"
                    r"p[aá]gina oficial|site oficial|fonte oficial|link oficial|official (?:site|page|website)|"
                    r"pncp\.gov\.br/app/editais|mapacultural|mapa\.cultura|prosas\.com\.br/editais|/oportunidade/", re.I)


_REP_CACHE: dict = {}


_ROTULO_OFICIAL = re.compile(r"p[aá]gina oficial|site oficial|fonte oficial|link oficial|official (?:site|page|website)", re.I)
_FORMULARIO = re.compile(r"forms\.gle/|docs\.google\.com/forms/", re.I)


def _republicador(u: str, aceitar_encurtador: bool = False) -> bool:
    """Agregador, notícia, rede social, encurtador ou buscador PELO DOMÍNIO (config/republicadores.json). O caminho não
    conta: /wp-content/uploads/2026/09/edital.pdf tem cara de data de notícia, mas é o edital no site do órgão."""
    if not _REP_CACHE:
        try:
            from pathlib import Path
            cat = json.loads((Path(__file__).resolve().parents[2] / "config/republicadores.json").read_text(encoding="utf-8"))
            _REP_CACHE["d"] = {d.lower() for k in ("noticia", "agregador", "rede_social", "encurtador", "buscador") for d in cat.get(k, [])}
            _REP_CACHE["enc"] = {d.lower() for d in cat.get("encurtador", [])}
        except Exception:
            _REP_CACHE["d"], _REP_CACHE["enc"] = set(), set()
    h = (urlsplit(u).hostname or "").lower().replace("www.", "")
    dominios = _REP_CACHE["d"] - (_REP_CACHE.get("enc") or set()) if aceitar_encurtador else _REP_CACHE["d"]
    return any(h == d or h.endswith("." + d) for d in dominios)


def oficial(pagina_url: str, links: list[tuple[str, str]], titulo: str = "", hosts_proibidos=()) -> str | None:
    """O link da FONTE OFICIAL entre os links da página do agregador. Pontos: sinal de edital no endereço ou no
    rótulo (4), domínio institucional .gov/.org/.jus/.leg (2) e nome do órgão do título no domínio (3)."""
    toks = [w for w in re.findall(r"[a-z]{5,}", norm(titulo)) if w not in {
        "edital", "publico", "publica", "chamamento", "chamada", "selecao", "credenciamento", "organizacoes", "sociedade",
        "projetos", "recursos", "captar", "inscricoes", "abertas", "programa", "municipal", "estadual", "federal"}]
    host = (urlsplit(pagina_url or "").hostname or "").lower()
    proib = {h.lower() for h in hosts_proibidos if h} | {host}
    cands = []
    for ordem, (h, t) in enumerate(links or []):
        s = urljoin(pagina_url or "", (h or "").strip())
        hs = (urlsplit(s).hostname or "").lower()
        if not s.startswith("http") or not hs or hs in proib or any(hs.endswith("." + p) for p in proib):
            continue
        rotulado = bool(_ROTULO_OFICIAL.search(t or ""))          # o agregador diz "página oficial": formulário do órgão vale
        formulario = rotulado and bool(_FORMULARIO.search(s))
        if (_LIXO.search(s) and not formulario) or _LEI.search(s) or _republicador(s, aceitar_encurtador=formulario):
            continue
        pts = (4 if _SINAL.search(s + " " + (t or "")) else 0) + (3 if rotulado else 0) + \
              (2 if re.search(r"\.gov\.br|\.leg\.br|\.jus\.br|\.mp\.br|\.org\.br|\.gov\b|\.gov\.|\.org\b|\.int\b|\.edu", s) else 0) + \
              (3 if any(w in norm(hs) for w in toks) else 0)
        if pts:
            cands.append((pts, len(urlsplit(s).path.strip("/")) > 0, -ordem, s))      # empate: o endereço mais específico
    return sorted(cands, reverse=True)[0][3] if cands else None


_CARTAO = re.compile(r'<a\b[^>]*?href="(?P<h>[^"]+)"[^>]*>(?P<c>.*?)</a>', re.S | re.I)
_TAG = re.compile(r"<!--.*?-->|<[^>]+>", re.S)


def cartoes(html: str, base: str, prefixo: str) -> dict:
    """Cartões de uma listagem (CapitaAI: <a href="/captacao/..."><h3>título</h3><p>órgão</p><p>Aceita: ...</p>
    <span>Prazo: dd/mm/aaaa</span></a>): {página do item: {titulo, financiador, publico, prazo, continuo}}.
    O prazo do cartão é o campo estruturado do agregador — vale mais que datas soltas no texto do guia."""
    out: dict = {}
    for m in _CARTAO.finditer(html or ""):
        h = urljoin(base or "", _html.unescape(m.group("h"))).split("#")[0]
        if not prefixo or prefixo not in urlsplit(h).path:
            continue
        c = m.group("c")
        tit = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", c, re.S | re.I)
        if not tit:
            continue
        resto = c[tit.end():]
        ps = [limpar(_TAG.sub(" ", p), 300) for p in re.findall(r"<p[^>]*>(.*?)</p>", resto, re.S | re.I)]
        aceita = [re.sub(r"(?i)^aceita\s*:\s*", "", p) for p in ps if re.match(r"(?i)aceita\s*:", p)]
        fin = next((p for p in ps if p and not re.match(r"(?i)(aceita|prazo)\s*:", p)), None)
        txt = limpar(_TAG.sub(" ", resto), 800)
        pz = None
        mp = re.search(r"(?i)prazo\s*:\s*(\d{1,2})/(\d{1,2})/(\d{4})", txt)
        if mp:
            try:
                pz = date(int(mp.group(3)), int(mp.group(2)), int(mp.group(1))).isoformat()
            except ValueError:
                pz = None
        out[h] = {"titulo": limpar(_TAG.sub(" ", tit.group(1)), 300), "financiador": fin,
                  "publico": aceita[0] if aceita else None, "prazo": pz,
                  "continuo": bool(re.search(r"(?i)prazo\s*:\s*(cont[ií]nu|fluxo cont|permanente|sem prazo)", txt))}
    return out


def canonica(u: str | None) -> str | None:
    if not u:
        return None
    try:
        p = urlsplit(u.strip())
    except Exception:
        return None
    if not p.scheme.startswith("http") or not p.hostname:
        return None
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
         if not re.match(r"utm_|fbclid|gclid|mc_|ref$|source$", k, re.I)]
    caminho = re.sub(r"/+$", "", p.path or "") or "/"
    return urlunsplit(("https", p.hostname.lower().replace("www.", ""), caminho, urlencode(q), ""))


def chave(item: dict) -> str:
    """Chave comum de duplicata: o link oficial canônico; sem ele, título normalizado + prazo."""
    lo = canonica(item.get("link_oficial"))
    if lo and not re.search(r"pncp\.gov\.br/?$|\.gov\.br/?$", lo):
        return "u:" + lo
    t = " ".join(norm(item.get("titulo") or "").split()[:14])
    return f"t:{t}|{item.get('prazo') or ''}"


def chaves(item: dict) -> list[str]:
    """Todas as chaves pelas quais o indício pode ser o mesmo de outro: o link oficial e, quando há prazo e UF,
    título + prazo + UF (o mesmo edital republicado por dois indexadores com endereços diferentes)."""
    ks = [chave(item)]
    pal = norm(item.get("titulo") or "").split()
    if item.get("prazo") and item.get("uf") and len(pal) >= 4:
        ks.append(f"tu:{' '.join(pal[:14])}|{item['prazo']}|{item['uf']}")
    return list(dict.fromkeys(ks))


# ------------------------------------------------------------------ perfil do público
_OSC = re.compile(r"\bosc\b|\boscs\b|organiza[cç][õo]es? da sociedade civil|sem fins lucrativos|associa[cç][ãa]o|associa[cç][õo]es|"
                  r"entidades?|institui[cç][õo]es? (?:privadas?|sociais|filantr)|coletivos?|movimentos?|grupos? comunit|"
                  r"pessoas? jur[ií]dicas?|ponto[s]? de cultura|cooperativas?|ongs?\b|nonprofit|non-profit|ngos?\b|civil society|"
                  r"community[- ]based|grassroots|terceiro setor|fundo a fundo|termo de fomento|termo de colabora", re.I)
_FORA = re.compile(r"bolsas? de (?:mestrado|doutorado|p[oó]s-?doutorado|inicia[cç][ãa]o cient[ií]fica|produtividade)|"
                   r"pesquisador(?:a|es)? (?:doutor|bolsista)|(?:para|destinad[oa]s? a) (?:startups?|empresas?|micro ?empresas?|prefeituras?|munic[ií]pios)|"
                   r"apenas pessoas? f[ií]sicas?|exclusivamente (?:a )?pessoas? f[ií]sicas?|"
                   r"phd (?:students?|candidates?)|doctoral|postdoctoral|for (?:students|researchers|startups|companies|businesses)\b|"
                   r"vestibular|processo seletivo para (?:alunos|estudantes)|concurso p[uú]blico", re.I)


def perfil(texto: str) -> tuple[str, str]:
    """'osc' (o texto fala de associação/OSC/entidade/coletivo), 'fora' (o texto restringe a pesquisador, estudante,
    empresa, prefeitura ou pessoa física, sem falar de OSC) ou 'indefinido'. Conservador: na dúvida, 'indefinido'."""
    t = str(texto or "")
    if _OSC.search(t):
        return "osc", "o texto cita OSC, associação, entidade, coletivo ou pessoa jurídica sem fins lucrativos"
    m = _FORA.search(t)
    if m:
        return "fora", f"público restrito: '{limpar(m.group(0), 60)}'"
    return "indefinido", "o texto não diz quem pode concorrer"


def injecao(texto: str) -> bool:
    return bool(INJECAO.search(str(texto or "")))
