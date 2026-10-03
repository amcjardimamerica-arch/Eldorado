"""MOTOR 22 — GIFE: seleção de editais do investimento social privado (versão 2, 01/10/2026).

Parecer do conselho: docs/pareceres/motor-22-gife.md. O que o motor antigo fazia e por que não achava edital:

1. O sensor genérico lia a HOME institucional (https://gife.org.br/) e a /agenda/ (eventos). A "descoberta de
   listagem" chegava à seleção mensal de editais ("Confira editais com inscrições abertas…"), mas ali cada edital
   é um bloco — título em negrito, parágrafo com financiador, prazo e valor, e um link "Inscreva-se", "Acesse" ou
   "Saiba mais". O sensor só considera links com rótulo de 10 letras ou mais: os três links de cada seleção eram
   descartados e o título do edital (sem link) nunca era lido. Setembro inteiro: 0 editais.
2. "Instituto" e "fundação" no léxico da camada 1 transformavam a ficha de qualquer ASSOCIADO em candidato: a única
   "oportunidade" do motor (29/09 a 01/10) foi "Fundação FEAC" — a página de perfil do associado, não um edital.
3. A descoberta seguia "Transparência" (/transparencia), que responde erro: 1 falha por dia, 26 ao todo.
4. Os links da seleção apontam para a plataforma Capta (capta.org.br/oportunidades/…), que publica cada
   oportunidade com campos fixos — "Região", "Inscrições até: dd/mm/aaaa" e "Edital: <link oficial>" — e nunca
   foi lida.
5. A seleção de 31/08 ficou só na categoria "Notícias", fora da categoria "Editais": seguir uma só listagem perde
   seleções.

Como funciona agora (sem IA, sem tokens, biblioteca-padrão; os dois sites são WordPress com API pública e robots
que permite a leitura):
  Fonte A — GIFE: API de posts (/wp-json/wp/v2/posts) da categoria "Editais" + busca por "edital", "inscrições
            abertas", "chamada" e "seleciona projetos" nos últimos `janela_dias`. Seleção mensal → um item por bloco
            (título em negrito/subtítulo + texto + links); notícia de edital único → um item.
  Fonte B — Capta: API de posts da categoria "Oportunidades" — prazo, região e link oficial em campos fixos.
  → A e B se cruzam pelo endereço da oportunidade na Capta (o link "Inscreva-se" do GIFE) ou pelo título;
  → cada item é classificado: OPORTUNIDADE · ACOMPANHAR · RUÍDO, sempre com o motivo escrito (prazo vigente,
    público OSC × pesquisador/estudante/jornalista/município/empresa, abrangência nacional ou Goiás).

O GIFE e a Capta são CURADORIA (fonte secundária): a URL do registro é o link OFICIAL do financiador quando a
publicação o traz; a página do GIFE/Capta vai em `url_fonte`. Conteúdo coletado é DADO: injeção → quarentena;
o que a publicação não diz fica `null`.
"""
from __future__ import annotations

import html as _html
import json
import re
import time
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from urllib.parse import quote, urlsplit

from . import atos_diario as atos
from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "plat-gife"
CFG = ROOT / "config/gife_editais.json"
ESTADO = ROOT / "estado/gife_editais.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
_PRAZO = {"ate": None}
CAMPOS = "id,date,modified,slug,link,title,content,categories"


def _hoje_real() -> date:
    # 03/10 (teste do motor 18): o dia é o de Brasília (o executor roda em UTC)
    from datetime import timezone
    return datetime.now(timezone(timedelta(hours=-3))).date()


def _tempo_esgotado() -> bool:
    return _PRAZO["ate"] is not None and time.monotonic() > _PRAZO["ate"]


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _N(t) -> str:
    return re.sub(r"\s+", " ", atos.sem_acento(str(t or "")).upper())


def _limpo(t) -> str:
    return re.sub(r"\s+", " ", _ZW.sub("", _html.unescape(re.sub(r"<[^>]+>", " ", str(t or ""))))).strip()


# ─────────────────────────── rede ───────────────────────────
def _get_json(url: str, timeout: int = 30, max_bytes: int = 6_000_000):
    """JSON da API do WordPress → (dados, total_de_páginas). Acima do limite → erro, nunca corte silencioso."""
    from urllib.request import HTTPRedirectHandler, Request, build_opener

    class _Redir(HTTPRedirectHandler):                     # o destino de cada redirecionamento passa pela mesma checagem
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            validate_public_https(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    validate_public_https(url)
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "pt-BR,pt;q=0.9"})
    with build_opener(_Redir()).open(req, timeout=timeout) as r:
        paginas = int(r.headers.get("X-WP-TotalPages") or 1)
        dados = r.read(max_bytes + 1)
    if len(dados) > max_bytes:
        raise ValueError(f"resposta maior que {max_bytes // 1_000_000} MB")
    return (json.loads(dados.decode("utf-8", "replace")) if dados.strip() else []), paginas


def _erro(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    causa = ("bloqueio (HTTP 403)" if code == 403 else "limite de requisições (HTTP 429)" if code == 429 else
             "tempo esgotado" if "Timeout" in nome or "timed out" in str(exc) else
             "endereço não resolve (DNS)" if nome == "gaierror" else f"HTTP {code}" if code else nome)
    return f"{causa}: {str(exc)[:90]}"


def _get(url: str, cfg: dict):
    """Uma chamada com o ritmo configurado; erro transitório → 1 nova tentativa."""
    ritmo = cfg.get("ritmo", {})
    ultimo = None
    for i in range(2):
        if _tempo_esgotado():
            raise RuntimeError("prazo da execução esgotado — o restante fica para a próxima passagem")
        try:
            r = _get_json(url)
            time.sleep(float(ritmo.get("pausa_segundos", 1.0)))
            return r
        except Exception as exc:  # noqa: BLE001 — vira diagnóstico, nunca silêncio
            ultimo = exc
            if getattr(exc, "code", None) in (400, 401, 403, 404) or isinstance(exc, ValueError):
                break
            time.sleep(float(ritmo.get("espera_erro_segundos", 5)))
    raise RuntimeError(_erro(ultimo))


def _posts(base: str, consulta: str, cfg: dict, fonte: dict, max_paginas: int = 3) -> list[dict]:
    """Todas as páginas de uma consulta à API de posts (até `max_paginas`)."""
    out, pag = [], 1
    while pag <= max_paginas:
        dados, total = _get(f"{base}/wp-json/wp/v2/posts?{consulta}&per_page={int(cfg.get('por_pagina', 50))}"
                            f"&page={pag}&_fields={CAMPOS}", cfg)
        fonte["consultas"] += 1
        fonte["bytes"] = fonte.get("bytes", 0) + len(json.dumps(dados, ensure_ascii=False))
        out += [p for p in (dados or []) if isinstance(p, dict)]
        if pag >= total:
            break
        pag += 1
    return out


def _categoria(base: str, slug: str, reserva, cfg: dict, fonte: dict):
    """Id da categoria pelo slug (o id pode mudar se o site for refeito); sem resposta → o id de reserva."""
    try:
        dados, _ = _get(f"{base}/wp-json/wp/v2/categories?slug={quote(slug)}&_fields=id,slug", cfg)
        fonte["consultas"] += 1
        for c in dados or []:
            if c.get("slug") == slug and c.get("id"):
                return int(c["id"])
    except Exception as exc:  # noqa: BLE001
        fonte["falhas"].append(f"categoria {slug}: {exc}")
    return reserva


# ─────────────────────────── HTML do post → blocos ───────────────────────────
_ZW = re.compile("[\u200b-\u200d\u2060\ufeff]")      # espaços de largura zero que o editor do WordPress deixa


class _Blocos(HTMLParser):
    """Blocos de texto (p, h2–h4, li…) com o texto em negrito e os links de cada um."""
    BLOCO = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "blockquote", "figcaption", "div"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocos: list[dict] = []
        self._cur = None
        self._neg = 0
        self._a = None

    def _abre(self, tag):
        self._fecha()
        self._cur = {"tag": tag, "texto": [], "negrito": [], "links": [], "fora_link": []}

    def _fecha(self):
        c = self._cur
        if c:
            t = re.sub(r"[ \t\r\f\v\xa0]+", " ", _ZW.sub("", "".join(c["texto"])))
            t = re.sub(r" ?\n[\s]*", "\n", t).strip()           # <br> fica como quebra (campos da Capta numa linha cada)
            if t or c["links"]:
                self.blocos.append({"tag": c["tag"], "texto": t, "negrito": re.sub(r"\s+", " ", _ZW.sub("", "".join(c["negrito"]))).strip(),
                                    "texto_sem_links": re.sub(r"\s+", " ", _ZW.sub("", "".join(c["fora_link"]))).strip(),
                                    "links": c["links"]})
        self._cur = None

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCO and tag != "div":
            self._abre(tag)
        elif tag in ("strong", "b"):
            self._neg += 1
        elif tag == "a":
            self._a = {"href": dict(attrs).get("href") or "", "texto": []}
        elif tag == "br" and self._cur:
            self._cur["texto"].append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCO and tag != "div":
            self._fecha()
        elif tag in ("strong", "b"):
            self._neg = max(0, self._neg - 1)
        elif tag == "a" and self._a is not None:
            if self._cur is None:
                self._abre("p")
            self._cur["links"].append((self._a["href"], re.sub(r"\s+", " ", "".join(self._a["texto"])).strip()))
            self._a = None

    def handle_data(self, data):
        if self._cur is None:
            if not data.strip():
                return
            self._abre("p")
        c = self._cur
        if self._neg:
            c["negrito"].append(data)
        c["texto"].append(data)
        if self._a is not None:
            self._a["texto"].append(data)
        else:
            c["fora_link"].append(data)

    def close(self):
        super().close()
        self._fecha()


def blocos_do_html(conteudo: str) -> list[dict]:
    p = _Blocos()
    p.feed(conteudo or "")
    p.close()
    return p.blocos


def _eh_titulo(b: dict) -> bool:
    """Subtítulo de um bloco de edital: h2–h4, ou parágrafo em negrito (fora o texto dos links), curto, sem ponto final de
    frase e que não seja ele mesmo um prazo ("Inscrições até 19 de outubro") ou um campo ("Região: …")."""
    t = b["texto"]
    if not (4 <= len(t) <= 160) or "\n" in t or re.match(r"(?i)(inscreva|acesse|saiba|veja|conhe[çc]a|leia|clique|confira)\b", t):
        return False
    T = _N(t)
    if re.search(r"INSCRI|PRAZO|\bATE\b|\d{1,2}/\d{1,2}", T) and not re.search(r"\bEDITA|PROGRAMA|PREMIO|CHAMADA|FUNDO", T):
        return False
    if b["tag"] in ("h2", "h3", "h4", "h5"):
        return True
    fora = b.get("texto_sem_links", t)
    return b["tag"] == "p" and bool(b["negrito"]) and len(b["negrito"]) >= len(fora) - 3 and not t.endswith((".", ":")) \
        and not re.match(r"(?i)(regi[ãa]o|inscri[çc][õo]es at[ée]|edital|prazo|valor)\s*:", t)


def _titulo_em_linha(b: dict) -> str:
    """Parágrafo que COMEÇA com o nome do edital em negrito e segue com o texto ("<strong>Edital X</strong> – O Fundo…").
    → o título (até o travessão/dois-pontos), ou "" se o bloco não tem esse formato."""
    t, n = b["texto"], b["negrito"]
    if b["tag"] not in ("p", "li") or not (4 <= len(n) <= 200) or len(t) < len(n) + 40 or not t.startswith(n[:15]):
        return ""
    m = re.match(r"(.{4,160}?)\s*[–—:]\s", t)
    tit = m.group(1) if m and len(m.group(1)) <= len(n) + 3 else n
    return tit.strip(" –—-:.")


# ─────────────────────────── itens ───────────────────────────
_RX_SELECAO = re.compile(r"\bEDITAIS\b.{0,60}(?:INSCRIC|ABERT|SELEC)|(?:CONFIRA|SELECAO|OS) .{0,30}\bEDITAIS\b|"
                         r"OPORTUNIDADES .{0,20}(?:ABERTAS|DO MES)")
_RX_EDITAL = re.compile(r"\bEDITA(?:L|IS)\b|\bCHAMADA\b|CHAMAMENTO|INSCRICOES (?:ABERTAS|ATE|VAO|SEGUEM|PODEM|ESTAO|DEVEM|"
                        r"PARA)|ABRE(?:M)? (?:AS )?INSCRICOES|SELECIONA(?:RA|RAO|R)? (?:ATE )?(?:\d+ )?(?:PROJETOS|ORGANIZAC|"
                        r"INICIATIVAS|PROPOSTAS)|SELECAO (?:DE PROJETOS|PUBLICA)|\bPREMIO\b|ACELERACAO")


def _host_capta(cfg: dict) -> str:
    return urlsplit((cfg.get("capta") or {}).get("base") or "https://capta.org.br").hostname or "capta.org.br"


def _slug_capta(href: str, host_capta: str) -> str | None:
    u = urlsplit(href or "")
    if (u.hostname or "").replace("www.", "") != host_capta.replace("www.", ""):
        return None
    partes = [x for x in u.path.split("/") if x]
    if len(partes) < 2 or partes[0] != "oportunidades" or "." in partes[-1]:
        return None                                    # só /oportunidades/<slug>/ — não /newsletter/, nem PDF
    return partes[-1]


def _oficial(links: list, hosts_curadoria: set) -> str | None:
    """Primeiro link https que não é do GIFE nem da Capta (e não é rede social/encurtador conhecido) — o do financiador."""
    for href, _ in links:
        u = urlsplit(href or "")
        h = (u.hostname or "").replace("www.", "")
        if u.scheme != "https" or not h or h in hosts_curadoria:
            continue
        if re.search(r"(?:^|\.)(?:facebook|instagram|twitter|x|linkedin|youtube|wa\.me|whatsapp|tiktok)\.", h + "."):
            continue
        return href
    return None


def _dia(s) -> str | None:
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(s or ""))
    try:
        return date.fromisoformat(m.group(1)).isoformat() if m else None
    except ValueError:
        return None


def itens_gife(post: dict, cfg: dict) -> list[dict]:
    """Post do GIFE → itens. Seleção mensal: um por bloco; notícia de edital: um; outro assunto: nenhum."""
    titulo = _limpo(_rendered(post, "title"))
    pub = _dia(post.get("date"))
    url_post = post.get("link") or ""
    blocos = blocos_do_html(_rendered(post, "content"))
    hc = _host_capta(cfg)
    curadoria = {"gife.org.br", hc.replace("www.", "")}
    base = {"fonte": "A", "post_id": post.get("id"), "url_fonte": url_post, "publicado": pub, "titulo_post": titulo}
    idx = [i for i, b in enumerate(blocos) if _eh_titulo(b)]
    em_linha = [i for i, b in enumerate(blocos) if _titulo_em_linha(b)]
    if len(idx) < 2 and len(em_linha) >= 2:                      # "<strong>Edital X</strong> – texto" em cada parágrafo
        idx = em_linha
    selecao = bool(_RX_SELECAO.search(_N(titulo + " " + (post.get("slug") or "").replace("-", " ")))) and len(idx) >= 1
    if not selecao and len(idx) >= 2:
        # título fora do padrão ("Editais do mês", "Oportunidades para OSCs em outubro"): é seleção se ao menos DUAS seções
        # trazem edital — link da Capta próprio, ou a palavra edital/chamada/prêmio com um prazo. Uma notícia com
        # subtítulos ("Como se inscrever", "Quem foi…") continua sendo UMA notícia.
        com_edital = 0
        for k, i in enumerate(idx):
            sec = blocos[i: idx[k + 1] if k + 1 < len(idx) else len(blocos)]
            txt = " ".join(b["texto"] for b in sec)
            if any(_slug_capta(h, hc) for b in sec for h, _ in b["links"]) or \
                    (_RX_EDITAL.search(_N(txt)) and prazo_do_texto(txt, pub)[0]):
                com_edital += 1
        selecao = com_edital >= 2
    if selecao:
        out = []
        for k, i in enumerate(idx):
            fim = idx[k + 1] if k + 1 < len(idx) else len(blocos)
            inline = _titulo_em_linha(blocos[i]) and not _eh_titulo(blocos[i])
            corpo = blocos[i: fim] if inline else blocos[i + 1: fim]
            texto = " ".join(b["texto"] for b in corpo if b["texto"])
            if inline:
                texto = texto[len(_titulo_em_linha(blocos[i])):].lstrip(" –—-:.")
            links = [l for b in corpo for l in b["links"]] + ([] if inline else blocos[i]["links"])
            if len(texto) < 40:                                  # subtítulo sem conteúdo (ex.: "Serviço"): o que houver
                if out:                                          # (prazo, link) fica com o edital anterior
                    out[-1]["texto"] = (out[-1]["texto"] + " " + blocos[i]["texto"] + " " + texto).strip()
                    if not out[-1]["capta_slug"]:
                        out[-1]["capta_slug"] = next((x for x in (_slug_capta(h, hc) for h, _ in links) if x), None)
                        out[-1]["url_capta"] = next((h for h, _ in links if _slug_capta(h, hc)), None)
                    out[-1]["url_oficial"] = out[-1]["url_oficial"] or _oficial(links, curadoria)
                continue
            capta = next((s for s in (_slug_capta(h, hc) for h, _ in links) if s), None)
            out.append({**base, "tipo": "selecao",
                        "titulo": _titulo_em_linha(blocos[i]) if inline else (blocos[i].get("texto_sem_links") or blocos[i]["texto"]),
                        "texto": texto,
                        "capta_slug": capta, "url_capta": next((h for h, _ in links if _slug_capta(h, hc)), None),
                        "url_oficial": _oficial(links, curadoria), "regiao": None, "prazo_campo": None})
        if out:
            return out
    texto = " ".join(b["texto"] for b in blocos if b["texto"])
    T = _N(titulo + " " + texto[:900])
    if not _RX_EDITAL.search(T) or not re.search(r"INSCRI|CANDIDAT|SUBMISS|PROPOSTAS|PRAZO", _N(titulo + " " + texto)):
        return []
    links = [l for b in blocos for l in b["links"]]
    capta = next((s for s in (_slug_capta(h, hc) for h, _ in links) if s), None)
    return [{**base, "tipo": "noticia", "titulo": titulo, "texto": texto, "capta_slug": capta,
             "url_capta": next((h for h, _ in links if _slug_capta(h, hc)), None),
             "url_oficial": _oficial(links, curadoria), "regiao": None, "prazo_campo": None}]


_CAMPO = re.compile(r"^(regi[ãa]o|inscri[çc][õo]es at[ée]|edital|prazo|valor|quem pode participar)\s*:\s*(.*)$", re.I | re.S)


def _rendered(post: dict, campo: str) -> str:
    v = post.get(campo)
    return str((v.get("rendered") if isinstance(v, dict) else v) or "")


def item_capta(post: dict, cfg: dict) -> dict | None:
    """Post da Capta → item com os campos fixos (Região, Inscrições até, Edital)."""
    titulo = _limpo(_rendered(post, "title"))
    if not titulo:
        return None
    blocos = blocos_do_html(_rendered(post, "content"))
    campos, texto, oficial = {}, [], None
    hc = _host_capta(cfg)
    curadoria = {"gife.org.br", hc.replace("www.", "")}
    for b in blocos:
        resto = []
        for linha in b["texto"].split("\n"):              # "Região: Nacional<br>Inscrições até: 19/10/2026"
            m = _CAMPO.match(linha.strip())
            if m:
                chave = _N(m.group(1)).split()[0]
                campos.setdefault(chave, m.group(2).strip())
                if chave == "EDITAL":
                    oficial = oficial or _oficial(b["links"], curadoria)
            elif linha.strip() and linha.strip() != titulo:
                resto.append(linha.strip())
        if resto:
            texto.append(" ".join(resto))
    return {"fonte": "B", "post_id": post.get("id"), "url_fonte": post.get("link") or "", "publicado": _dia(post.get("date")),
            "titulo_post": titulo, "tipo": "capta", "titulo": titulo, "texto": " ".join(texto),
            "capta_slug": post.get("slug") or _slug_capta(post.get("link") or "", hc), "url_capta": post.get("link"),
            "url_oficial": oficial or _oficial([l for b in blocos for l in b["links"]], curadoria),
            "regiao": campos.get("REGIAO") or None, "prazo_campo": campos.get("INSCRICOES") or campos.get("PRAZO") or None}


# ─────────────────────────── prazo, valor, financiador ───────────────────────────
MESES = {"JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
         "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12}
_M = "(" + "|".join(MESES) + ")"
_HORA = r"(?:(?:AS\s+)?\d{1,2}\s*H(?:\d{2})?(?:MIN)?(?:\s*\(HORARIO DE BRASILIA\))?\s+(?:DO\s+|DE\s+)?)?"     # "até as 18h do dia 4…"
_DATAS = [
    re.compile(r"\bATE\s+" + _HORA + r"(?:O\s+)?(?:DIA\s+)?(\d{1,2})(?:º|O)?\s+DE\s+" + _M + r"(?:\s+(?:DE\s+)?(\d{4}))?"),
    re.compile(r"\bATE\s+" + _HORA + r"(?:O\s+)?(?:DIA\s+)?(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?"),
    re.compile(r"(?:ENCERRA(?:M|RAO|-SE)?|TERMINA(?:M|RAO)?|PRAZO(?:\s+FINAL)?(?:\s+(?:E|SERA|PARA|DE)[^.]{0,30}?)?)"
               r"(?:\s+(?:EM|NO DIA|DIA|ATE|:))?\s+(\d{1,2})(?:º|O)?\s+DE\s+" + _M + r"(?:\s+(?:DE\s+)?(\d{4}))?"),
    re.compile(r"\bA\s+(\d{1,2})(?:º|O)?\s+DE\s+" + _M + r"(?:\s+(?:DE\s+)?(\d{4}))?"),          # "de 1º a 30 de setembro"
    re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\s+(?:A|ATE)\s+(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?"),  # "01/09/2026 a 20/09/2026"
]
_CONTEXTO_PRAZO = re.compile(r"INSCRI|INSCREV|PRAZO|CANDIDAT|SUBMISS|PROPOSTA|ENVIO|CADASTR|PARTICIPA|ADES|ABERT[AO]S?\b|RECEBE")
_CONTEXTO_OUTRO = re.compile(r"RESULTADO|DIVULGA|ANUNCI|EXECU[CT]|VIGENCIA|EVENTO SERA|REALIZA|CERIMONIA|PREMIACAO|INICIO DAS|"
                             r"CONCLU|FINALIZ|ENTREGA DO RELATORIO|PRESTACAO DE CONTAS|DURACAO|DESENVOLVID")
FLUXO = re.compile(r"FLUXO CONTINUO|INSCRICOES (?:PERMANENTES|CONTINUAS)|A QUALQUER MOMENTO|EM CARATER PERMANENTE|"
                   r"RECEBE PROPOSTAS (?:CONTINUAMENTE|O ANO TODO|AO LONGO DO ANO)")


def _montar(d, m, a, ref: date) -> date | None:
    try:
        d, m = int(d), (MESES[m] if not str(m).isdigit() else int(m))
        if a:
            a = int(a); a = a + 2000 if a < 100 else a
            return date(a, m, d)
        x = date(ref.year, m, d)
        return date(ref.year + 1, m, d) if x < ref - timedelta(days=20) else x     # "até 15 de janeiro" num post de dezembro
    except (ValueError, KeyError):
        return None


def prazo_do_texto(texto: str, publicado: str | None, campo: str | None = None) -> tuple[str | None, bool, str | None]:
    """(data final ISO, fluxo contínuo?, trecho). O campo fixo da Capta vale mais que o texto corrido."""
    ref = date.fromisoformat(publicado) if publicado else _hoje_real()
    if campo:
        C = _N(campo)
        if FLUXO.search(C):
            return None, True, campo
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", C) or re.search(r"(\d{1,2})(?:º|O)?\s+DE\s+" + _M + r"(?:\s+DE\s+(\d{4}))?", C)
        if m:
            d = _montar(m.group(1), m.group(2), m.group(3), ref)
            if d:
                return d.isoformat(), False, campo
    T = _N(texto)
    candidatos = []
    for rx in _DATAS:
        for m in rx.finditer(T):
            d = _montar(m.group(1), m.group(2), m.group(3), ref)
            if not d:
                continue
            antes = T[max(0, m.start() - 110): m.start()]
            frase = re.split(r"[.;]\s", antes)[-1]                  # só a frase do próprio prazo
            depois = re.split(r"[.;]\s", T[m.end(): m.end() + 50])[0]   # "estão abertas até 4 de fevereiro AS INSCRIÇÕES"
            peso = (2 if _CONTEXTO_PRAZO.search(frase) or _CONTEXTO_PRAZO.search(depois) else
                    1 if _CONTEXTO_PRAZO.search(antes) else 0) - (3 if _CONTEXTO_OUTRO.search(frase[-60:]) else 0)
            candidatos.append((peso, m.start(), d, T[max(0, m.start() - 60): m.end()]))
    bons = [c for c in candidatos if c[0] >= 1]       # data sem contexto de inscrição não vira prazo (execução, evento…)
    if bons:
        bons.sort(key=lambda c: (-c[0], c[1]))
        return bons[0][2].isoformat(), False, bons[0][3].strip()
    if FLUXO.search(T):
        return None, True, FLUXO.search(T).group(0)
    return None, False, None


_VALOR = re.compile(r"R\$\s?\d[\d.,]*(?:\s?(?:MIL|MILHOES|MILHAO|BILHAO|BILHOES)\b)?", re.I)
_FIN = re.compile(r"(?:lan[çc]ad[oa]|promovid[oa]|realizad[oa]|organizad[oa]|coordenad[oa]|apoiad[oa]) pel[oa]s?\s+"
                  r"((?:Fundo|Funda[çc][ãa]o|Instituto|Associa[çc][ãa]o|Banco|Minist[ée]rio|Iniciativa|Rede|Grupo|Movimento|"
                  r"Programa|Conselho|Secretaria|Empresa|Companhia|Cooperativa|Sociedade|Ag[êe]ncia|Centro|Observat[óo]rio|"
                  r"[A-Z][\w&]+)[^,.;:()]{0,70})|"
                  r",\s*d[oa]s?\s+((?:Fundo|Funda[çc][ãa]o|Instituto|Associa[çc][ãa]o|Iniciativa|Banco|Minist[ée]rio|Rede|"
                  r"Programa)[^,.;:()]{2,70})|"
                  r"(?:^|\.\s+)(?:O|A|Os|As)\s+((?:Fundo|Funda[çc][ãa]o|Instituto|Associa[çc][ãa]o|Banco|Minist[ée]rio|"
                  r"Iniciativa|Rede|Grupo|Movimento)[^,.;:()]{2,70}?)\s+(?:lan[çc]|abr|abriu|est[áa] com|anuncia|divulga|"
                  r"seleciona|realiza|promove)")


def financiador(texto: str) -> str | None:
    m = _FIN.search(texto or "")
    if not m:
        return None
    nome = next(g for g in m.groups() if g)
    nome = re.split(r"\s+(?:est[áa]|que|com|para|abriu|abre|lan[çc]ou|lan[çc]a|e o|e a)\s", nome)[0]
    return nome.strip()[:90] or None


# ─────────────────────────── público e território ───────────────────────────
OSC = re.compile(   # quem PODE SE INSCREVER: plural ("organizações", "associações", "coletivos") — o singular costuma ser o nome
    # de um parceiro ("em parceria com a Associação do Laboratório…") e só vale na forma "organização da sociedade civil"
    r"(?<!COM A )(?<!PELA )(?<!PARCERIA DA )ORGANIZACAO DA SOCIEDADE CIVIL|"
    r"\bORGANIZACOES\b(?! DAS NACOES| INTERNACIONA| EMPRESARIA)|\bOSCS?\b|SEM FINS (?:LUCRATIVOS|ECONOMICOS)|\bASSOCIACOES\b|"
    r"INSTITUICOES PRIVADAS SEM|"
    r"\bCOLETIVOS\b|\bMOVIMENTOS\b|\bONGS\b|\bENTIDADES\b|TERCEIRO SETOR|\bCOOPERATIVAS\b|"
    r"INICIATIVAS (?:COMUNITARIA|DE MULHERES|SOCIA|LOCA|DE BASE|PERIFERICA)|COM OU SEM (?:FORMALIZACAO|CNPJ)|"
    r"GRUPOS (?:COMUNITARIOS|DE BASE|FORMAIS|INFORMAIS|E COLETIVOS|ORGANIZADOS)|"
    r"COMUNIDADES (?:TRADICIONAIS|INDIGENAS|QUILOMBOLAS)|NEGOCIOS SOCIAIS|PROJETOS SOCIAIS|"
    r"PROJETOS (?:APROVADOS|INCENTIVADOS|ENQUADRADOS) (?:EM|NAS?) (?:LEIS?|MECANISMOS) DE INCENTIVO")
PUBLICOS = [   # público que NÃO é OSC — se for o único público, o item é ruído
    ("pesquisadores", re.compile(r"PESQUISADOR(?:ES|A|AS)?\b|RESIDENCIA (?:E PESQUISA|DE PESQUISA|ARTISTICA)|"
                                 r"BOLSAS? (?:DE|PARA) (?:PESQUISA|ESTUDO|MESTRADO|DOUTORADO|INICIACAO)")),
    ("programas de pós-graduação e universidades", re.compile(r"POS-?GRADUACAO|INSTITUICOES DE ENSINO SUPERIOR|"
                                                                r"\bUNIVERSIDADES\b|\bIES\b|PROGRAMAS? DE MESTRADO")),
    ("estudantes", re.compile(r"\bESTUDANTES?\b|\bUNIVERSITARIOS\b|\bALUNOS\b|GRADUANDOS|\bBOLSISTAS\b|"
                              r"\bJOVENS [A-Z ]{0,25}QUE (?:DESEJAM|QUEIRAM|PRETENDEM) INGRESSAR")),
    ("jornalistas", re.compile(r"JORNALISTAS?\b|PREMIO [^.]{0,40}JORNALISMO|REPORTAGE")),
    ("municípios e gestores públicos", re.compile(r"\bMUNICIPIOS\b|\bPREFEITURAS\b|GESTORES? (?:PUBLICOS|MUNICIPAIS)|"
                                                  r"CHAMADA CIDADES|\bCIDADES (?:BRASILEIRAS|PARTICIPANTES|INTERESSADAS|SELECIONADAS)|"
                                                  r"ADMINISTRAC(?:AO|OES) PUBLICA")),
    ("empresas e startups", re.compile(r"\bSTARTUPS?\b|EMPRESAS? (?:DE TECNOLOGIA|NASCENTES|INOVADORAS)|"
                                       r"EMPREENDEDORES? INDIVIDUA|\bMEIS?\b|NEGOCIOS DE IMPACTO|PEQUENAS EMPRESAS")),
    ("pessoas físicas", re.compile(r"PESSOAS? FISICAS?|ARTISTAS? (?:INDIVIDUA|SOLO)|\bPROFESSOR(?:ES|AS)?\b|\bEDUCADOR(?:ES|AS)\b|"
                                   r"\bCANDIDATOS? (?:INDIVIDUAIS|PESSOA)")),
]
ELEGIVEIS = re.compile(r"PODE(?:M|RAO) (?:SE INSCREVER|PARTICIPAR|CONCORRER|APRESENTAR|SUBMETER|SE CANDIDATAR|CANDIDATAR)|"
                       r"DESTINAD[OA]S? A|VOLTAD[OA]S? (?:A|AO|AOS|AS|PARA)|ELEGIVE|PUBLICO-?ALVO|ACEITA PROPOSTAS|PROPONENTES?\b|"
                       r"SELECIONARA|APOIARA|PARA SE INSCREVER|RECEBE (?:PROJETOS|PROPOSTAS|INSCRICOES) DE|INSCRICOES DE")


def publico_alvo(T: str) -> tuple:
    """(sinal de OSC ou None, outros públicos). Vale primeiro o que as frases de ELEGIBILIDADE dizem ("podem participar",
    "destinado a", "aceita propostas de"); sem elas, havendo OSC e outro público, vence o que aparece primeiro —
    "bolsas para pesquisadores que estudam organizações" é de pesquisador; "organizações e pesquisadores", de OSC."""
    TS = _sem_autodescricao(T)
    eleg = " ".join(f for f in re.split(r"(?<=[.;!?])\s+", TS) if ELEGIVEIS.search(f))
    if eleg:
        o = OSC.search(eleg)
        if o:
            return o, [nome for nome, rx in PUBLICOS if rx.search(eleg)]
        fora = [nome for nome, rx in PUBLICOS if rx.search(eleg)]
        if fora:
            return None, fora
    o = OSC.search(TS)
    outros = [nome for nome, rx in PUBLICOS if rx.search(TS)]
    if o and outros:
        primeiro = min(rx.search(TS).start() for nome, rx in PUBLICOS if rx.search(TS))
        if primeiro < o.start():
            return None, outros
    return o, outros


EVENTO = re.compile(r"\bENCONTRO\b|SEMINARIO|CONGRESSO|WEBINAR|\bCURSOS?\b|\bFORUM\b|CONFERENCIA|\bEVENTO\b|OFICINA|"
                    r"CAPACITACAO|FORMACAO GRATUITA|\bJORNADA\b|\bFESTIVAL\b")
_RESTRITO = r"(?!\s+(?:O |A |OS |AS )?(?:ESTADO|MUNICIPIO|CIDADE|REGIAO|DA |DO |DE |DOS |DAS |NO |NA |EM ))"
NACIONAL = re.compile(r"ABRANGENCIA NACIONAL|AMBITO NACIONAL|CARATER NACIONAL|ESCALA NACIONAL|"
                      r"TODO O (?:BRASIL|PAIS|TERRITORIO NACIONAL|TERRITORIO BRASILEIRO)\b|BRASIL INTEIRO|PAIS INTEIRO|"
                      r"QUALQUER (?:ESTADO BRASILEIRO|UNIDADE DA FEDERACAO|LUGAR DO (?:BRASIL|PAIS)|REGIAO DO (?:BRASIL|PAIS))|"
                      r"QUALQUER (?:ESTADO|REGIAO)" + _RESTRITO + r"|TODOS OS ESTADOS" + _RESTRITO + r"|TODAS AS REGIOES" + _RESTRITO +
                      r"|TODAS AS UNIDADES DA FEDERACAO|(?:AS )?CINCO REGIOES|TODOS OS ESTADOS (?:BRASILEIROS|DO (?:BRASIL|PAIS))|"
                      r"(?:EDITAL|CHAMADA|PROGRAMA|SELECAO|PREMIO|CONCURSO) NACIONAL|(?:INICIATIVAS?|ORGANIZACOES|PROJETOS) DE TODO O "
                      r"(?:BRASIL|PAIS)")
REGIOES = [
    (re.compile(r"AMAZONIA LEGAL|AMAZONIA BRASILEIRA|\bAMAZONIA\b|AMAZONICO|AMAZONICA|BIOMA AMAZONIA"),
     {"AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"}, "Amazônia"),
    (re.compile(r"\bNORDESTE\b|NORDESTINO|SEMIARIDO"), {"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}, "Nordeste"),
    (re.compile(r"REGIAO NORTE\b|\bNORTE DO (?:BRASIL|PAIS)"), {"AC", "AM", "AP", "PA", "RO", "RR", "TO"}, "Norte"),
    (re.compile(r"\bSUDESTE\b"), {"ES", "MG", "RJ", "SP"}, "Sudeste"),
    (re.compile(r"REGIAO SUL\b|\bSUL DO (?:BRASIL|PAIS)"), {"PR", "RS", "SC"}, "Sul"),
    (re.compile(r"CENTRO-? ?OESTE"), {"DF", "GO", "MS", "MT"}, "Centro-Oeste"),
    (re.compile(r"\bCERRADO\b"), {"BA", "DF", "GO", "MA", "MG", "MS", "MT", "PI", "PR", "SP", "TO"}, "Cerrado"),
    (re.compile(r"\bPANTANAL\b"), {"MS", "MT"}, "Pantanal"),
    (re.compile(r"VALE DO ACO|VALE DO JEQUITINHONHA|TRIANGULO MINEIRO"), {"MG"}, "Minas Gerais"),
]
ENTORNO = re.compile(r"MUNICIPIOS (?:ONDE|EM QUE|NOS QUAIS) A (?:EMPRESA|COMPANHIA)|RAIO DE (?:ATE )?\d+ ?(?:KM|QUILOMETROS)|"
                     r"ENTORNO D[AO]S? (?:UNIDADES|OPERACOES|FABRICAS|PLANTAS|USINAS|EMPREENDIMENTOS)|COMUNIDADES DO ENTORNO|"
                     r"AREAS? DE (?:INFLUENCIA|ATUACAO) D[AO] (?:EMPRESA|COMPANHIA|GRUPO)|"
                     r"ONDE (?:A EMPRESA|A COMPANHIA|O GRUPO|A [A-Z]+) (?:ATUA|OPERA|MANTEM|TEM|POSSUI) (?:OPERACOES|UNIDADES|SEDES?)")
_ESTADOS = {"ACRE": "AC", "ALAGOAS": "AL", "AMAPA": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARA": "CE", "ESPIRITO SANTO": "ES",
            "MARANHAO": "MA", "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "MINAS GERAIS": "MG", "PARAIBA": "PB",
            "PARANA": "PR", "PERNAMBUCO": "PE", "PIAUI": "PI", "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS",
            "RONDONIA": "RO", "RORAIMA": "RR", "SANTA CATARINA": "SC", "SERGIPE": "SE", "TOCANTINS": "TO", "GOIAS": "GO",
            "GOIANIA": "GO", "DISTRITO FEDERAL": "DF", "BRASILIA": "DF", "ESTADO DO RIO DE JANEIRO": "RJ",
            "ESTADO DE SAO PAULO": "SP", "ESTADO DO PARA": "PA"}
_SIGLAS = "AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO"
_SIGLA_LOCAL = re.compile(r"(?<=[A-Z]{3})(?:\s*(?:/|\()\s*(" + _SIGLAS + r")|\s*-\s*(?!SE\b)(" + _SIGLAS + r"))\b(?!-)")
# "-SE" é pronome ("inscreva-se", "candidate-se"), não Sergipe; Sergipe por extenso ou "/SE" e "(SE)" continuam valendo


def territorio(texto: str, regiao: str | None, ufs_assoc: list[str]) -> tuple[str, set, str | None]:
    """→ (nível: "nacional" | "regional" | "nao_informado", UFs alcançadas, rótulo). O campo Região da Capta vale primeiro."""
    for alvo in ([_N(regiao)] if regiao else []) + [_N(texto)]:
        if re.fullmatch(r"\W*(?:NACIONAL|BRASIL|TODO O BRASIL|TODO O PAIS|TODOS OS ESTADOS)\W*", alvo) or NACIONAL.search(alvo):
            return "nacional", set(), "nacional"
        ufs, rot = set(), []
        for rx, conj, nome in REGIOES:
            if rx.search(alvo):
                ufs |= conj; rot.append(nome)
        resto = alvo
        for nome in sorted(_ESTADOS, key=len, reverse=True):        # o nome mais longo primeiro e sai do texto
            if re.search(r"\b" + nome + r"\b", resto):
                ufs.add(_ESTADOS[nome]); rot.append(nome.title())
                resto = re.sub(r"\b" + nome + r"\b", " ", resto)
        ufs |= {a or b for a, b in _SIGLA_LOCAL.findall(alvo)}
        if ufs:
            return "regional", ufs, ", ".join(dict.fromkeys(rot)) or "/".join(sorted(ufs))
    return "nao_informado", set(), None


_AUTODESCRICAO = re.compile(r"\b(?:E|SAO|FOI|SE TORNOU|ATUA COMO) (?:UMA?|A|O|COMO) (?:[A-Z]+ ){0,2}(?:ORGANIZAC|ASSOCIAC|ENTIDADE|"
                            r"\bOSC|INSTITUICAO|INSTITUTO|FUNDACAO|ONG\b)|SEM FINS LUCRATIVOS,? QUE (?:ATUA|DESENVOLVE|TEM|TRABALHA|NASCEU)|"
                            r"\bFUNDAD[OA] EM \d{4}")


def _sem_autodescricao(T: str) -> str:
    """Tira as frases em que o FINANCIADOR se descreve ("o Instituto X é uma organização da sociedade civil…"): o que
    importa é quem pode se inscrever, não a natureza de quem paga."""
    return " ".join(f for f in re.split(r"(?<=[.;!?])\s+", T) if not _AUTODESCRICAO.search(f))


# ─────────────────────────── classificação ───────────────────────────
def classificar_item(m: dict, hoje: date, ufs: list[str] | None = None, cfg: dict | None = None) -> dict:
    """Um edital da curadoria → OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo escrito.

    1. prazo (campo fixo da Capta ou texto: "até o dia 19 de outubro") · 2. público (OSC × pesquisador, estudante,
    jornalista, município, empresa, pessoa física) · 3. abrangência (nacional ou que alcance Goiás)."""
    cfg = cfg or {}
    ufs = ufs or ["GO"]
    texto = " ".join(x for x in (m.get("titulo"), m.get("texto")) if x)
    T = _N(texto)
    fim, fluxo, trecho = prazo_do_texto(texto, m.get("publicado"), m.get("prazo_campo"))
    nivel, alcance, rotulo = territorio(texto, m.get("regiao"), ufs)
    base = {"fim": fim, "fluxo_continuo": fluxo, "trecho_prazo": trecho, "nivel": nivel,
            "territorio": "BR" if nivel != "regional" else ("/".join(sorted(alcance & set(ufs))) or "fora"),
            "abrangencia": rotulo, "regime": "investimento_social_privado", "publico": None, "motivos": [], "sinais": []}
    titulo_N = _N(m.get("titulo"))
    if re.search(r"\bPREMIO\b", titulo_N):
        base["regime"] = "premio"
    elif EVENTO.search(titulo_N) and not re.search(r"EDITAL|CHAMADA|SELECAO|ACELERACAO|FUNDO", titulo_N):
        base["regime"] = "capacitacao_evento"
    osc, outros = publico_alvo(T)
    base["publico"] = "OSC" if osc else (", ".join(outros) or None)
    base["sinais"] = [s for s in (("osc:" + osc.group(0).lower()) if osc else None, *("publico:" + o for o in outros)) if s]
    hoje_s = hoje.isoformat()
    no_titulo = [nome for nome, rx in PUBLICOS if rx.search(titulo_N)]
    if no_titulo and not OSC.search(titulo_N):
        return {**base, "veredito": "RUIDO", "motivos": [f"destinado a {', '.join(no_titulo)} (dito no título) — não a OSC"]}
    if not osc and outros:
        return {**base, "veredito": "RUIDO", "motivos": [f"destinado a {', '.join(outros)} — não a organizações da sociedade civil"]}
    if fim and fim < hoje_s:
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": [f"inscrições encerradas em {fim} — financiador e edital recorrente para vigiar a próxima edição"]}
    if nivel == "regional" and not (alcance & set(ufs)):
        return {**base, "veredito": "ACOMPANHAR", "territorio": "fora",
                "motivos": [f"restrito a {rotulo} — não alcança {'/'.join(ufs)}"]}
    if nivel != "nacional" and ENTORNO.search(T) and "GOIANIA" not in T:
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": ["restrito ao entorno das operações do financiador — conferir se Goiânia está na lista"]}
    if base["regime"] == "capacitacao_evento":
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": ["evento ou capacitação para o terceiro setor — não é recurso" + (f"; inscrições até {fim}" if fim else "")]}
    if not osc:
        return {**base, "veredito": "ACOMPANHAR", "motivos": ["o texto não diz quem pode participar — conferir no edital"]}
    publicado = m.get("publicado") or hoje_s
    dias_sem_prazo = int(cfg.get("dias_sem_prazo_oportunidade", 45))
    if not fim and not fluxo and publicado < (hoje - timedelta(days=dias_sem_prazo)).isoformat():
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": [f"publicado em {publicado} sem prazo no texto — conferir se ainda está aberto"]}
    if nivel == "nao_informado":
        return {**base, "veredito": "ACOMPANHAR",
                "motivos": ["abrangência não informada (pode ser restrito à região do financiador) — conferir no edital"]}
    prazo = f"inscrições até {fim}" if fim else "fluxo contínuo" if fluxo else "prazo não informado — conferir no edital"
    alc = "nacional" if nivel == "nacional" else f"alcança {'/'.join(sorted(alcance & set(ufs)))} ({rotulo})"
    restam = (date.fromisoformat(fim) - hoje).days if fim else None
    if restam is not None and restam <= int(cfg.get("dias_prazo_curto", 5)):
        # 03/10 (teste do motor 18): prazo curto sobe com alerta — a Rede Memória Viva vencia no dia do teste
        quando = "hoje" if restam == 0 else f"em {restam} dia(s)"
        return {**base, "veredito": "OPORTUNIDADE", "alerta_prazo": True, "dias_restantes": restam,
                "motivos": [f"URGENTE — vence {quando}: edital aberto para OSC ({prazo}; {alc})"]}
    return {**base, "veredito": "OPORTUNIDADE", "dias_restantes": restam, "motivos": [f"edital aberto para OSC ({prazo}; {alc})"]}


def _url_norm(u: str | None) -> str | None:
    """Endereço do edital para comparar: host + caminho + consulta; a home do financiador (caminho vazio) não serve."""
    p = urlsplit(u or "")
    if not p.hostname or p.path.strip("/") == "":
        return None
    return (p.hostname.replace("www.", "") + p.path.rstrip("/") + ("?" + p.query if p.query else "")).lower()


def _chave(m: dict) -> str:
    if m.get("capta_slug"):
        return "capta:" + m["capta_slug"]
    if _url_norm(m.get("url_oficial")):
        return "url:" + _url_norm(m["url_oficial"])
    return "tit:" + re.sub(r"[^A-Z0-9]+", " ", _N(m.get("titulo"))).strip()[:80]


def _conflito(k1: str, k2: str) -> bool:
    """Duas chaves FORTES do mesmo tipo e diferentes (dois slugs da Capta, dois links oficiais) = editais diferentes."""
    t1, t2 = k1.split(":", 1)[0], k2.split(":", 1)[0]
    return t1 == t2 and t1 != "tit" and k1 != k2


def _tokens(t: str) -> set:
    return {w for w in re.findall(r"[A-Z0-9]{4,}", _N(t)) if w not in {"EDITAL", "PROGRAMA", "CHAMADA", "PROJETOS", "PARA", "COM"}}


def _registro(c: dict, m: dict, ident: str | None = None) -> dict:
    texto = re.sub(r"\s+", " ", m.get("texto") or "")
    ev = atos.mascarar_pii(texto)[:700]
    fin = financiador(texto)
    val = _VALOR.search(texto)
    via = "Capta" if m["fonte"] == "B" and len(m.get("fontes", ["B"])) == 1 else "GIFE"
    return {
        "id": ident or sha256(f"gife|{m['chave']}".encode())[:20], "status": "capturada",
        "titulo": (f"{fin} — {m['titulo']}" if fin and _N(fin) not in _N(m["titulo"]) else m["titulo"])[:300],
        "url": m.get("url_oficial") or m.get("url_capta") or m.get("url_fonte"), "url_fonte": m.get("url_fonte"),
        "url_capta": m.get("url_capta"), "url_oficial": m.get("url_oficial"),
        "fonte_id": MOTOR_ID, "fonte_nome": f"GIFE — seleção de editais (via {via})",
        "territorio": c["territorio"], "uf": None, "nivel": "privada", "abrangencia": c["abrangencia"],
        "tipo_fonte": "curadoria_investimento_social", "confianca": "secundaria", "forma_divulgacao": "curadoria_gife",
        "coletado_em": now_iso(), "data_publicacao": m.get("publicado"), "fim": c["fim"],
        "prazo_texto": c["fim"] or ("fluxo contínuo" if c["fluxo_continuo"] else None), "trecho_prazo": c["trecho_prazo"],
        "valor_texto": val.group(0) if val else None, "financiador": fin, "orgao": fin, "publico": c["publico"],
        "objeto": texto[:600] or None, "regime": c["regime"],
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()), "fontes_observadas": m.get("fontes", [m["fonte"]]),
        "classificacao_ato": {k: c[k] for k in ("veredito", "regime", "motivos", "sinais")} | {"tipo": "abertura"},
        "sensor": MOTOR_ID, "forca_lexica": 3,
        "alerta_prazo": bool(c.get("alerta_prazo")), "dias_restantes": c.get("dias_restantes"),
    }


def classificar_lote(itens: list[dict], hoje: date, ufs: list[str] | None = None,
                     cfg: dict | None = None, apelidos: dict | None = None) -> tuple[dict, dict, dict]:
    """→ ({id: OPORTUNIDADE}, {id: ACOMPANHAR}, contagens). GIFE e Capta se cruzam: um registro por oportunidade.

    `apelidos` (chave → id, guardado no estado) mantém o id quando um dia a Capta não responde e o mesmo edital chega
    só pelo GIFE, com outra chave."""
    apelidos = {} if apelidos is None else apelidos
    oport, acomp = {}, {}
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0, "erros": 0}
    vistos: dict[str, dict] = {}
    for m in sorted(itens, key=lambda x: x["fonte"], reverse=True):          # Capta (B) primeiro: campos fixos
        k = _chave(m)
        ant = vistos.get(k)
        if not ant and m["fonte"] == "A":
            uo = _url_norm(m.get("url_oficial"))
            tk = _tokens(m.get("titulo"))
            for v in vistos.values():          # o mesmo edital na Capta, com outro título ou sem o link da Capta
                if "B" not in v["fontes"] or _conflito(k, v["chave"]):
                    continue
                tv = _tokens(v.get("titulo"))
                if (uo and uo == _url_norm(v.get("url_oficial"))) or \
                        (len(tk & tv) >= 3 and len(tk & tv) / len(tk | tv) >= 0.6):
                    ant = v; break
        if ant:
            ant["chaves"] = sorted(set(ant.get("chaves", [])) | {k})
            ant["fontes"] = sorted(set(ant["fontes"]) | {m["fonte"]})
            for c in ("url_oficial", "regiao", "prazo_campo", "url_capta", "capta_slug"):
                ant[c] = ant.get(c) or m.get(c)
            if m["fonte"] == "A" and m.get("texto") and m["texto"] not in (ant.get("texto") or ""):
                ant["texto"] = ((ant.get("texto") or "") + " " + m["texto"]).strip()
                ant["url_fonte_gife"] = m.get("url_fonte")
            ant["publicado"] = min(x for x in (ant.get("publicado"), m.get("publicado")) if x) if (ant.get("publicado") or m.get("publicado")) else None
            continue
        vistos[k] = dict(m, fontes=[m["fonte"]], chave=k, chaves=[k])
    for m in vistos.values():
        bruto = " ".join(str(m.get(k) or "") for k in ("titulo", "texto"))
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url_fonte"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1
            continue
        try:
            c = classificar_item(m, hoje, ufs, cfg)
            ident = next((apelidos[x] for x in [m["chave"], *m["chaves"]] if x in apelidos), None) or \
                sha256(f"gife|{m['chave']}".encode())[:20]
            for x in m["chaves"]:
                apelidos[x] = ident
            cont[c["veredito"]] += 1
            if c["veredito"] == "RUIDO":
                continue
            r = _registro(c, m, ident)
        except Exception:  # noqa: BLE001 — um item malformado não derruba o lote
            cont["erros"] += 1
            continue
        (oport if c["veredito"] == "OPORTUNIDADE" else acomp)[r["id"]] = r
    return oport, acomp, cont


# ─────────────────────────── fontes ───────────────────────────
def fonte_a(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    g = cfg.get("gife") or {}
    base = g.get("base", "https://gife.org.br").rstrip("/")
    F = diag["fontes"]["A"]
    depois = (hoje - timedelta(days=int(g.get("janela_dias", 90)))).isoformat() + "T00:00:00"
    antes = (hoje + timedelta(days=1)).isoformat() + "T00:00:00"
    posts: dict = {}
    cat = _categoria(base, g.get("categoria_slug", "editais"), g.get("categoria_id", 25), cfg, F)
    consultas = ([f"categories={cat}&after={depois}&before={antes}"] if cat else []) + \
                [f"search={quote(t)}&after={depois}&before={antes}" for t in g.get("buscas", [])]
    for q in consultas:
        try:
            for p in _posts(base, q, cfg, F):
                posts.setdefault(p.get("id"), p)
        except Exception as exc:  # noqa: BLE001 — uma consulta nunca derruba as outras
            F["falhas"].append(str(exc))
            if len(F["falhas"]) >= int(cfg.get("falhas_seguidas_para_abortar_fonte", 3)) and not posts:
                break
    F["posts"] = len(posts)
    itens = []
    for p in posts.values():
        try:
            itens += itens_gife(p, cfg)
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"post {p.get('id')}: {type(exc).__name__}")
    F["itens"] = len(itens)
    return itens


def fonte_b(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("capta") or {}
    if c.get("ativa", True) is False:
        return []
    base = c.get("base", "https://capta.org.br").rstrip("/")
    F = diag["fontes"]["B"]
    depois = (hoje - timedelta(days=int(c.get("janela_dias", 365)))).isoformat() + "T00:00:00"
    antes = (hoje + timedelta(days=1)).isoformat() + "T00:00:00"
    cat = _categoria(base, c.get("categoria_slug", "oportunidades"), c.get("categoria_id", 4), cfg, F)
    try:
        posts = _posts(base, (f"categories={cat}&" if cat else "") + f"after={depois}&before={antes}", cfg, F)
    except Exception as exc:  # noqa: BLE001
        F["falhas"].append(str(exc)); return []
    F["posts"] = len(posts)
    itens = []
    for p in posts:
        try:
            x = item_capta(p, cfg)
        except Exception as exc:  # noqa: BLE001 — um post malformado não derruba a fonte
            F["falhas"].append(f"post {p.get('id')}: {type(exc).__name__}"); continue
        if x:
            itens.append(x)
    F["itens"] = len(itens)
    return itens


# ─────────────────────────── o motor ───────────────────────────
def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 22 com a mesma saída de `sensores.ler`."""
    pedido = hoje or (sensor or {}).get("_data")
    hoje = _hoje_real() if pedido is None else pedido
    if pedido is not None and pedido < _hoje_real():
        # o que importa é o que está ABERTO hoje: reler um dia passado gravaria como aberto um edital já encerrado
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                "diagnostico": {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0,
                                "motivo_zero": "o motor 22 lê os editais abertos hoje; dia passado não é relido", "retroativo": True}}
    cfg = _cfg()
    ufs = list((cfg.get("territorio") or {}).get("ufs") or ["GO"])
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 180))
    diag = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0, "motivo_zero": None,
            "versao": "motor-22 v2 (01/10/2026)",
            "fontes": {"A": {"falhas": [], "consultas": 0, "posts": 0, "itens": 0},
                       "B": {"falhas": [], "consultas": 0, "posts": 0, "itens": 0}}}
    itens = []
    try:
        itens += fonte_a(hoje, cfg, diag)
    except Exception as exc:  # noqa: BLE001
        diag["fontes"]["A"]["falhas"].append(f"etapa: {_erro(exc)}")
    try:
        itens += fonte_b(hoje, cfg, diag)
    except Exception as exc:  # noqa: BLE001
        diag["fontes"]["B"]["falhas"].append(f"etapa: {_erro(exc)}")
    _PRAZO["ate"] = None
    est = load_json(ESTADO) if ESTADO.exists() else {}
    apelidos = dict(est.get("apelidos") or {})
    oport, acomp, cont = classificar_lote(itens, hoje, ufs, cfg, apelidos)
    A, B = diag["fontes"]["A"], diag["fontes"]["B"]
    diag.update({"vereditos": cont, "paginas_lidas": A["consultas"] + B["consultas"], "links_total": len(itens),
                 "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"]})
    leu = A["consultas"] > 0 or B["consultas"] > 0          # `consultas` conta só as chamadas que responderam
    d0 = hoje.isoformat()
    hist = est.setdefault("historico", {})
    hist[d0] = {"consultas_A": A["consultas"], "consultas_B": B["consultas"], "posts_A": A["posts"], "posts_B": B["posts"],
                "itens": len(itens), **cont, "falhou": not leu}
    seq, d = 0, hoje
    for _ in range(30):
        h = hist.get(d.isoformat())
        if not h or not h.get("falhou"):
            break
        seq += 1; d -= timedelta(days=1)
    if seq >= 2:
        diag["alerta"] = f"{seq} dias seguidos sem resposta do GIFE e da Capta — " + (A["falhas"] + B["falhas"] + ["sem causa"])[0]
    campos = ("id", "titulo", "url", "url_fonte", "fim", "financiador", "abrangencia", "publico", "regime")
    est["abertas"] = sorted(({k: r.get(k) for k in campos} for r in oport.values()), key=lambda r: str(r.get("fim") or "9999"))
    est["acompanhar"] = sorted(({k: a.get(k) for k in campos} | {"motivo": a["classificacao_ato"]["motivos"][0]}
                                for a in acomp.values()), key=lambda a: str(a.get("fim") or "0000"), reverse=True)[:200]
    est["ultima"] = {"em": now_iso(), "data": d0, "vereditos": cont, "falhas": (A["falhas"] + B["falhas"])[:10]}
    est["historico"] = {k: v for k, v in hist.items() if k >= (hoje - timedelta(days=120)).isoformat()}
    est["apelidos"] = dict(list(apelidos.items())[-3000:])
    write_json(ESTADO, est)
    g, c = (cfg.get("gife") or {}).get("base", "https://gife.org.br"), (cfg.get("capta") or {}).get("base", "https://capta.org.br")
    falhas = [{"url": (g if i < len(A["falhas"]) else c) + "/wp-json/wp/v2/posts", "erro": "wp-json", "code": None, "waf": None,
               "causa": f} for i, f in enumerate((A["falhas"] + B["falhas"])[:6])]
    saude = ([{"url": g + "/wp-json/wp/v2/posts", "http": 200, "bytes": A.get("bytes", 0), "posts": A["posts"]}] if A["consultas"] else []) + \
            ([{"url": c + "/wp-json/wp/v2/posts", "http": 200, "bytes": B.get("bytes", 0), "posts": B["posts"]}] if B["consultas"] else [])
    if leu:
        # categoria sem resposta (usou o id de reserva) e post malformado (ficou no diagnóstico) não são falha de leitura
        falhas = [f for f in falhas if not f["causa"].startswith(("categoria ", "post "))]
    if not oport:
        diag["motivo_zero"] = (f"{len(itens)} editais lidos na seleção do GIFE e na Capta (A {A['itens']} · B {B['itens']}): "
                               f"nenhum aberto para OSC com abrangência nacional ou em Goiás · {cont['ACOMPANHAR']} a acompanhar · "
                               f"{cont['RUIDO']} ruído" if leu else
                               "o GIFE e a Capta não responderam: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    return {"sensor": MOTOR_ID, "achados": sorted(oport.values(), key=lambda r: str(r.get("fim") or "9999")), "falhas": falhas,
            "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return (est.get("acompanhar") or [])[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
