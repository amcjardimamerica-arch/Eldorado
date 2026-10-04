"""O PILOTO — cria prompts de busca, VOA até a internet e lê o que encontrou.

O erro que este módulo corrige: o modelo local não tem internet. Perguntar a ele "que
institutos publicam edital?" só devolve o que estava nos pesos — por isso as missões
vinham "secas". A ordem certa é outra:

    1. o Piloto CRIA a consulta de busca (é nisso que o modelo é bom: formular)
    2. o sistema EXECUTA a busca na internet (o runner do GitHub tem rede)
    3. o Piloto LÊ os resultados reais e diz o que serve, com o site oficial
    4. o que passa vira alvo; o que não passa vira lição

Busca sem API paga: DuckDuckGo HTML (html.duckduckgo.com) e Bing HTML como reserva.
"""
from __future__ import annotations

import gzip
import json
import os
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CFG = ROOT / "config/motor_piloto.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
VETOR = re.compile(r"observatorio3setor|captadores\.org|prosas\.com|gife\.org\.br/noticias|g1\.globo|uol\.com|facebook|instagram|linkedin|youtube|twitter|x\.com|wikipedia", re.I)
LIXO = re.compile(r"duckduckgo|bing\.com|google\.|/search\?|javascript:|mailto:", re.I)


class _Res(HTMLParser):
    """Extrai (titulo, url, trecho) da página de resultados."""
    def __init__(self):
        super().__init__(); self.itens = []; self._a = None; self._t = []; self._sn = False; self._snt = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and "result__a" in (d.get("class") or ""):
            self._a = d.get("href"); self._t = []
        elif tag == "a" and self._a is None and (d.get("href") or "").startswith("http") and "result" in (d.get("class") or ""):
            self._a = d.get("href"); self._t = []
        elif tag == "a" and "result__snippet" in (d.get("class") or ""):
            self._sn = True; self._snt = []
    def handle_data(self, s):
        if self._a is not None and not self._sn:
            self._t.append(s)
        elif self._sn:
            self._snt.append(s)
    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None and not self._sn:
            tit = re.sub(r"\s+", " ", "".join(self._t)).strip()
            url = self._a
            from .nucleo import resolver_redirecionamento
            url = resolver_redirecionamento(url)         # qualquer variante do embrulho do buscador
            if tit and url.startswith("http") and not LIXO.search(url):
                self.itens.append({"titulo": tit[:160], "url": url, "trecho": ""})
            self._a = None
        elif tag == "a" and self._sn:
            if self.itens:
                self.itens[-1]["trecho"] = re.sub(r"\s+", " ", "".join(self._snt)).strip()[:300]
            self._sn = False


class _ResGoogle(HTMLParser):
    """Resultados do Google HTML: links em /url?q=<destino>&sa=..."""
    def __init__(self):
        super().__init__(); self.itens = []; self._a = None; self._t = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        h = dict(attrs).get("href") or ""
        if h.startswith("/url?q="):
            u = urllib.parse.unquote(h[7:].split("&")[0])
            if u.startswith("http") and not LIXO.search(u):
                self._a = u; self._t = []
    def handle_data(self, s):
        if self._a is not None:
            self._t.append(s)
    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            tit = re.sub(r"\s+", " ", "".join(self._t)).strip()
            if len(tit) > 8:
                self.itens.append({"titulo": tit[:160], "url": self._a, "trecho": ""})
            self._a = None


# Google, Bing e DuckDuckGo recusam IP de datacenter — e o Piloto roda num servidor do GitHub.
# Por isso a lista tem também buscadores que aceitam robôs declaradamente (Mojeek e Marginalia).
# A ordem é a da chance de responder de lá, não a do tamanho do índice.
# MEDIDO no proprio servidor (22/09 17:33): dos seis buscadores, SO o html.duckduckgo.com
# respondeu. Google, Bing, Mojeek, Marginalia e o DDG-lite devolveram zero — recusam IP de
# datacenter. Carregar cinco buscadores mortos custava ate 20 s de espera CADA, por voo, para
# nada. Ficaram so os que provaram funcionar, mais as saidas com chave (opcionais e gratuitas).
BUSCADORES = [
    ("duckduckgo", "https://html.duckduckgo.com/html/?q={q}", _Res),
]
# Reserva: so entram se o titular gravar a chave no segredo do repositorio. Ambas tem camada
# gratuita suficiente para o nosso volume e NAO bloqueiam datacenter, porque sao API.
CHAVES = {
    "brave": ("BRAVE_SEARCH_KEY", "https://api.search.brave.com/res/v1/web/search?q={q}&country=BR&count=20"),
    "google_cse": ("GOOGLE_CSE_KEY", "https://www.googleapis.com/customsearch/v1?key={k}&cx={cx}&q={q}&num=10"),
}
# REVEZAMENTO DAS VIAS. Cada consulta usa UMA via, e a seguinte usa a próxima da roda. Assim
# nenhuma apanha o volume inteiro — que foi o que fez o DuckDuckGo começar a cortar. A via só
# é pulada quando está BLOQUEADA: falhou, entra em descanso e a roda segue sem ela até voltar.
VIAS = ROOT / "estado/piloto/vias.json"
DESCANSO_MIN = 25          # quanto tempo uma via fica de fora depois de bloquear


def _vias_estado() -> dict:
    d = load_json(VIAS) if VIAS.exists() else {}
    d.setdefault("roda", 0)
    d.setdefault("situacao", {})
    return d


def _via_disponivel(nome: str, d: dict) -> bool:
    s = (d.get("situacao") or {}).get(nome) or {}
    if not s.get("bloqueada_em"):
        return True
    return (time.time() - s["bloqueada_em"]) > DESCANSO_MIN * 60


def _marcar_via(nome: str, ok: bool, quantos: int = 0) -> None:
    d = _vias_estado()
    s = d.setdefault("situacao", {}).setdefault(nome, {"usos": 0, "entregas": 0, "bloqueios": 0})
    s["usos"] += 1
    if ok:
        s["entregas"] += 1
        s["resultados"] = s.get("resultados", 0) + quantos
        s["bloqueada_em"] = None
        s["ultima_boa"] = now_iso()[:16]
    else:
        s["bloqueios"] += 1
        s["bloqueada_em"] = time.time()
        s["descansa_ate"] = now_iso()[:16] + f" +{DESCANSO_MIN}min"
    write_json(VIAS, d)


def vias_da_roda() -> list[str]:
    """Todas as vias disponíveis, na ordem da roda a partir de onde parou."""
    import os
    todas = [b[0] for b in BUSCADORES] + [n for n in CHAVES if os.environ.get(CHAVES[n][0])]
    d = _vias_estado()
    livres = [v for v in todas if _via_disponivel(v, d)] or todas      # todas bloqueadas: tenta assim mesmo
    i = d.get("roda", 0) % len(livres)
    d["roda"] = (i + 1) % max(1, len(livres))
    write_json(VIAS, d)
    return livres[i:] + livres[:i]


_ULTIMA_BUSCA = [0.0]
ESPERA_ENTRE_BUSCAS = 4.0      # o DuckDuckGo corta quem metralha consultas — 14 buscas vazias vieram disso


def _por_api(nome: str, consulta: str, tempo: float) -> list[dict]:
    """Busca por API com chave. Só funciona se o segredo estiver gravado; sem ele, devolve
    lista vazia em silêncio — nunca quebra o voo."""
    import os
    if nome == "brave":
        k = os.environ.get("BRAVE_SEARCH_KEY")
        if not k:
            return []
        req = urllib.request.Request(CHAVES["brave"][1].format(q=urllib.parse.quote(consulta)),
                                     headers={"X-Subscription-Token": k, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=tempo) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        return [{"titulo": (x.get("title") or "")[:160], "url": x.get("url"), "trecho": (x.get("description") or "")[:200],
                 "buscador": "brave"} for x in ((d.get("web") or {}).get("results") or []) if x.get("url")]
    if nome == "google_cse":
        k, cx = os.environ.get("GOOGLE_CSE_KEY"), os.environ.get("GOOGLE_CSE_CX")
        if not (k and cx):
            return []
        req = urllib.request.Request(CHAVES["google_cse"][1].format(k=k, cx=cx, q=urllib.parse.quote(consulta)),
                                     headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=tempo) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        return [{"titulo": (x.get("title") or "")[:160], "url": x.get("link"), "trecho": (x.get("snippet") or "")[:200],
                 "buscador": "google_cse"} for x in (d.get("items") or []) if x.get("link")]
    return []


def buscar_na_fonte(dominio: str, termos: list[str], tempo: float = 20, teto: int = 60) -> list[dict]:
    """SAÍDA QUE NENHUM BUSCADOR BLOQUEIA: ler o site oficial por dentro.

    Todo site publica um mapa (sitemap.xml) ou uma página de listagem. Buscar ali é gratuito,
    não depende de Google nem de DuckDuckGo, e ninguém barra — é o mesmo que um visitante faz.
    Mais lento e mais estreito (só acha no domínio informado), mas nunca volta vazio por bloqueio.
    """
    alvos, achados, vistos = [], [], set()
    for caminho in ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml", "/robots.txt"):
        try:
            req = urllib.request.Request(f"https://{dominio}{caminho}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=tempo) as r:
                txt = r.read().decode("utf-8", "ignore")
        except Exception:
            continue
        if caminho.endswith("robots.txt"):
            alvos += re.findall(r"(?i)sitemap:\s*(\S+)", txt)
        else:
            alvos += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)
        if alvos:
            break
    filhos = [u for u in alvos if u.endswith(".xml")][:4]
    for u in filhos:                                          # mapa de mapas
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=tempo) as r:
                alvos += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.read().decode("utf-8", "ignore"))
        except Exception:
            pass
    termos_l = [x.lower() for x in termos if x]
    for u in alvos:
        if u.endswith(".xml") or u in vistos:
            continue
        vistos.add(u)
        alvo_l = urllib.parse.unquote(u).lower()
        if any(x in alvo_l for x in termos_l):
            achados.append({"titulo": urllib.parse.unquote(u.rstrip("/").split("/")[-1]).replace("-", " ")[:140],
                            "url": u, "trecho": "", "buscador": f"fonte:{dominio}"})
        if len(achados) >= teto:
            break
    return achados


def diagnostico(consulta: str = "edital apoio a projetos sociais 2026", tempo: float = 15) -> dict:
    """Testa cada buscador de onde o Piloto realmente está e diz quem respondeu.
    É a única forma honesta de saber: aqui no contêiner tudo falha por bloqueio de rede."""
    saida = {}
    for nome, molde, parser in BUSCADORES:
        try:
            r = buscar(consulta, maximo=5, tempo=tempo, motores=[nome])
            saida[nome] = {"resultados": len(r), "exemplo": (r[0]["url"][:90] if r else None)}
        except Exception as ex:
            saida[nome] = {"resultados": 0, "erro": f"{type(ex).__name__}: {ex}"[:120]}
    vivos = [k for k, v in saida.items() if v.get("resultados")]
    return {"em": now_iso(), "consulta": consulta, "responderam": vivos,
            "nenhum_respondeu": not vivos, "detalhe": saida}


_DDG_NO_VOO = {"usadas": 0, "bloqueado": False}


def _google_noticias(consulta: str, maximo: int, tempo: float) -> list[dict]:
    """Google Notícias por RSS (01/10): sem chave, sem cartão; medido no servidor: 61 a 100 resultados por busca,
    6 buscas seguidas sem bloqueio. Traz NOTÍCIAS (anúncios de editais, prêmios, chamadas) — o título e a fonte viram o
    trecho que o crivo lê; a fonte oficial é confirmada depois pelo Interceptador."""
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(consulta) + "&hl=pt-BR&gl=BR&ceid=BR:pt-419")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml,application/xml"})
    with urllib.request.urlopen(req, timeout=tempo) as r:
        xml = r.read(3_000_000).decode("utf-8", "ignore")
    import html as _h
    out = []
    for it in re.findall(r"<item>(.*?)</item>", xml, re.S)[:maximo * 2]:
        tit = _h.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<title>(.*?)</title>", it, re.S) or [None, ""])[1]))
        link = (re.search(r"<link>(.*?)</link>", it, re.S) or [None, ""])[1].strip()
        fonte = _h.unescape((re.search(r"<source[^>]*>(.*?)</source>", it, re.S) or [None, ""])[1])
        fonte_url = (re.search(r'<source url="([^"]+)"', it) or [None, ""])[1]
        data = (re.search(r"<pubDate>(.*?)</pubDate>", it) or [None, ""])[1]
        if tit and link:
            out.append({"titulo": tit[:160], "url": link, "trecho": f"{tit} — {fonte} ({data[:16]})"[:300], "fonte_url": fonte_url, "buscador": "google_noticias"})
    return out[:maximo]


# ── 02/10/2026 (parecer dos pilotos): CONTINUIDADE DAS BUSCAS ────────────────────────────────────────────────
# Medido: no servidor do GitHub o DuckDuckGo entrega 2 buscas por máquina e bloqueia; depois disso o voo inteiro caía no
# Google Notícias — e as vias por API (Brave, Google) NUNCA eram tentadas, mesmo com a chave gravada. E o Espião repetia
# as mesmas consultas a cada voo (uma delas 241 vezes), gastando as 2 buscas boas no que já sabia. Agora:
#   1. CACHE de 24 h por consulta (6 h se veio vazia): a mesma pergunta não gasta busca de novo;
#   2. quando o DuckDuckGo esgota, a ordem é: API com chave (Brave, Google) → ponte Brasil (se configurada) → Google
#      Notícias — nessa ordem, sempre;
#   3. no computador do titular ou na VM do Brasil (ELDORADO_LOCAL_BR=1), IP que o buscador não trata como robô de
#      datacenter: até 30 buscas por voo no DuckDuckGo, com 6 s de intervalo.
CACHE_BUSCAS = ROOT / "estado/piloto/cache_buscas.json"
_PONTE_NO_VOO = {"usadas": 0}


def local_brasil() -> bool:
    import os
    return os.environ.get("ELDORADO_LOCAL_BR") == "1"


def _chave_consulta(c: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFD", (c or "").lower())
    return re.sub(r"\s+", " ", "".join(ch for ch in t if unicodedata.category(ch) != "Mn")).strip()


def _cache_ler(consulta: str) -> list[dict] | None:
    try:
        d = load_json(CACHE_BUSCAS) if CACHE_BUSCAS.exists() else {}
    except Exception:  # noqa: BLE001
        return None
    x = d.get(_chave_consulta(consulta))
    if not x:
        return None
    validade = 24 * 3600 if x.get("itens") else 6 * 3600
    return x.get("itens") if time.time() - float(x.get("t") or 0) < validade else None


def _cache_gravar(consulta: str, itens: list[dict]) -> None:
    try:
        d = load_json(CACHE_BUSCAS) if CACHE_BUSCAS.exists() else {}
        d[_chave_consulta(consulta)] = {"t": time.time(), "em": now_iso()[:16], "itens": itens[:12]}
        if len(d) > 400:                                     # fica o mais recente
            d = dict(sorted(d.items(), key=lambda kv: -float(kv[1].get("t") or 0))[:400])
        write_json(CACHE_BUSCAS, d)
    except Exception:  # noqa: BLE001 — cache nunca derruba a busca
        pass


def _ddg_pela_ponte(consulta: str, tempo: float) -> list[dict]:
    """O DuckDuckGo pelo IP da ponte Brasil (hospedagem ou VM): outra máquina, outra cota de buscas."""
    from .indexadores import ponte as _ponte
    if not _ponte.configurada():
        return []
    st, _final, corpo, hdr = _ponte.buscar("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(consulta),
                                           {"Accept": "text/html", "Accept-Language": "pt-BR,pt;q=0.9"}, int(tempo), 2_000_000)
    if (hdr.get("content-encoding") or "") == "gzip":
        corpo = gzip.decompress(corpo)
    p = _Res(); p.feed(corpo.decode("utf-8", "ignore"))
    return [{**it, "buscador": "duckduckgo_ponte"} for it in p.itens]


def _vias_de_reserva(consulta: str, maximo: int, tempo: float, pe: dict) -> list[dict]:
    """Quando o DuckDuckGo direto esgota: API com chave → ponte Brasil → Google Notícias."""
    import os
    for nome in ("brave", "google_cse"):
        if not os.environ.get(CHAVES[nome][0]):
            continue
        try:
            itens = _por_api(nome, consulta, tempo)
            _marcar_via(nome, bool(itens), len(itens))
            if itens:
                return itens[:maximo]
        except Exception:  # noqa: BLE001
            _marcar_via(nome, False)
    if _PONTE_NO_VOO["usadas"] < int(pe.get("max_buscas_ponte_por_voo", 3)):
        try:
            _PONTE_NO_VOO["usadas"] += 1
            itens = _ddg_pela_ponte(consulta, tempo)
            if itens:
                _marcar_via("duckduckgo_ponte", True, len(itens))
                return itens[:maximo]
        except Exception:  # noqa: BLE001
            _marcar_via("duckduckgo_ponte", False)
    try:
        return _google_noticias(consulta, maximo, tempo)
    except Exception:  # noqa: BLE001
        return []


def buscar(consulta: str, maximo: int = 10, tempo: float = 20, motores: list[str] | None = None) -> list[dict]:
    """Busca com cache e vias de reserva (02/10/2026) — ver _buscar_sem_cache. O cache vale só no voo real (nuvem ou
    Brasil), nunca em teste."""
    import os
    usar_cache = not motores and (os.environ.get("ELDORADO_VOO_REAL") == "1" or local_brasil())
    if usar_cache:
        c = _cache_ler(consulta)
        if c is not None:
            return [dict(x, do_cache=True) for x in c][:maximo]
    r = _buscar_sem_cache(consulta, maximo, tempo, motores)
    if usar_cache:
        _cache_gravar(consulta, r)
    return r


def _buscar_sem_cache(consulta: str, maximo: int = 10, tempo: float = 20, motores: list[str] | None = None) -> list[dict]:
    """Busca real na internet pelas vias disponíveis, EM REVEZAMENTO.

    Cada consulta começa por uma via diferente, para que nenhuma apanhe o volume inteiro —
    foi o excesso numa só que fez o DuckDuckGo começar a cortar. A via seguinte só é usada
    quando a atual não entrega; quem falha entra em descanso e sai da roda por um tempo."""
    try:                                                    # 03/10: navegador do titular primeiro (IP e navegador de verdade)
        from . import navegador_local as _nav
        if not motores and _nav.disponivel():
            _r = _nav.buscar(consulta, maximo)
            if _r:
                return _r
    except Exception:  # noqa: BLE001 — o navegador nunca derruba a busca: segue pelas vias de sempre
        pass
    saida, vistos = [], set()
    try:                                                    # 01/10: parâmetros aprendidos (config/parametros_pilotos.json)
        _pe = (json.loads((Path(__file__).resolve().parents[1] / "config/parametros_pilotos.json").read_text(encoding="utf-8")).get("espiao") or {})
    except Exception:
        _pe = {}
    ESPERA = float(_pe.get("intervalo_busca_local_s", 6.0) if local_brasil() else _pe.get("intervalo_busca_s", ESPERA_ENTRE_BUSCAS))
    espera = ESPERA - (time.time() - _ULTIMA_BUSCA[0])
    if espera > 0:
        time.sleep(min(espera, ESPERA))                    # respeita o intervalo, senão o buscador corta
    _ULTIMA_BUSCA[0] = time.time()
    # 01/10 — MEDIDO no servidor: o DuckDuckGo entrega 2 buscas por máquina e bloqueia (desafio anti-robô, status 202)
    # por mais de 4 minutos — esperar não adianta. Cada voo é uma máquina nova: no máximo 2 buscas nele; depois, ou se
    # bloquear, o Google Notícias (RSS) assume o resto do voo.
    cota = int(_pe.get("max_buscas_duckduckgo_por_voo_local", 30) if local_brasil() else _pe.get("max_buscas_duckduckgo_por_voo", 2))
    if not motores and (_DDG_NO_VOO["bloqueado"] or _DDG_NO_VOO["usadas"] >= cota):
        return _vias_de_reserva(consulta, maximo, tempo, _pe)
    ordem = [v for v in vias_da_roda() if not motores or v in motores] or [b[0] for b in BUSCADORES]
    porMolde = {b[0]: (b[1], b[2]) for b in BUSCADORES}
    for nome in ordem:
        if nome in CHAVES:                                   # via por API
            try:
                itens = _por_api(nome, consulta, tempo)
                for it in itens:
                    chave = re.sub(r"[#?].*$", "", it["url"]).rstrip("/")
                    if chave not in vistos:
                        vistos.add(chave); saida.append(it)
                _marcar_via(nome, bool(itens), len(itens))
                if saida:
                    return saida[:maximo]
            except Exception:
                _marcar_via(nome, False)
            continue
        molde, parser = porMolde.get(nome, (None, None))
        if not molde:
            continue
        try:
            url = molde.format(q=urllib.parse.quote(consulta))
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9",
                                                       "Accept": "text/html,application/xhtml+xml"})
            with urllib.request.urlopen(req, timeout=tempo) as r:
                bruto = r.read()
                if (r.headers.get("Content-Encoding") or "") == "gzip":
                    bruto = gzip.decompress(bruto)
                html = bruto.decode("utf-8", "ignore")
            p = parser(); p.feed(html)
            for it in p.itens:
                chave = re.sub(r"[#?].*$", "", it["url"]).rstrip("/")
                if chave in vistos:
                    continue
                vistos.add(chave); saida.append({**it, "buscador": nome})
            _marcar_via(nome, bool(p.itens), len(p.itens))
            if nome == "duckduckgo":
                _DDG_NO_VOO["usadas"] += 1
                if not p.itens:
                    _DDG_NO_VOO["bloqueado"] = True    # bloqueou: o resto do voo vai pelo Google Notícias
            if saida:
                break                          # entregou: a roda para aqui e a próxima consulta começa na via seguinte
        except Exception:
            _marcar_via(nome, False)           # bloqueou: descansa e a roda segue sem ela
            time.sleep(1.2)
    # 01/10: ZERO resultados é o bloqueio silencioso do DuckDuckGo (medido: 8, 8, 0, 0, 0). Espera e tenta de novo,
    # ignorando o "descanso" — antes, a via descansava e todas as buscas seguintes do voo saíam vazias.
    if not saida and not motores:
        _DDG_NO_VOO["bloqueado"] = True
        r = _vias_de_reserva(consulta, maximo, tempo, _pe)
        if r:
            return r
    if not saida:
        BLOQUEIO_DO_BUSCADOR[0] += 1
    return saida[:maximo]


BLOQUEIO_DO_BUSCADOR = [0]


def _buscar_de_novo(consulta: str, maximo: int, tempo: float) -> list[dict]:
    """Uma segunda tentativa direta no DuckDuckGo HTML, sem a roda de vias."""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(consulta)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=tempo) as r:
        bruto = r.read()
        if (r.headers.get("Content-Encoding") or "") == "gzip":
            bruto = gzip.decompress(bruto)
    p = _Res(); p.feed(bruto.decode("utf-8", "ignore"))
    _ULTIMA_BUSCA[0] = time.time()
    if not p.itens:
        BLOQUEIO_DO_BUSCADOR[0] += 1
    return [{**it, "buscador": "duckduckgo"} for it in p.itens][:maximo]


def ler_pagina(url: str, limite: int = 6000, tempo: float = 20) -> str:
    """Texto da página, para o Piloto confirmar que é oportunidade de verdade."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=tempo) as r:
            bruto = r.read(400_000)
            if (r.headers.get("Content-Encoding") or "") == "gzip":
                bruto = gzip.decompress(bruto)
            html = bruto.decode("utf-8", "ignore")
        html = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", html)
        texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()[:limite]
    except Exception:
        texto = ""
    if len(texto) < 400:                                    # 03/10: vazia ou só o esqueleto → abre no navegador do titular
        try:
            from . import navegador_local as _nav
            if _nav.disponivel():
                return re.sub(r"\s+", " ", _nav.ler(url))[:limite]
        except Exception:  # noqa: BLE001
            pass
    return texto


def _oficial(url: str) -> bool:
    return bool(url) and url.startswith("http") and not VETOR.search(url)


def _similar(a: str, b: str) -> float:
    """Jaccard entre conjuntos de palavras — barato e suficiente para barrar consulta repetida."""
    A = {w for w in re.findall(r"[a-zà-ú0-9]{4,}", (a or "").lower())}
    B = {w for w in re.findall(r"[a-zà-ú0-9]{4,}", (b or "").lower())}
    return len(A & B) / len(A | B) if A and B else 0.0


def consultas_ja_usadas(n: int = 60) -> list[str]:
    cfg = load_json(CFG) if CFG.exists() else {}
    fora = []
    for r in (cfg.get("consultas_usadas") or [])[:n]:
        fora += [c for c in (r.get("consultas") or [])]
    return fora[:n]


def inedita(c: str, usadas: list[str], teto: float | None = None) -> bool:
    teto = teto if teto is not None else ((load_json(CFG).get("prompt_unico") or {}).get("similaridade_maxima") or 0.72)
    return all(_similar(c, u) < teto for u in usadas)


UF_SIGLAS = "ac al am ap ba ce df es ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to".split()
_GO = re.compile(r"\bgoi[aá]s\b|goi[aâ]nia|an[aá]polis|aparecida de goi|rio verde|catal[aã]o|luzi[aâ]nia|senador canedo|\bgo\b ?- ?brasil", re.I)
_BR = re.compile(r"todo o (territ[oó]rio )?(nacional|brasil)|abrang[eê]ncia nacional|em todo o pa[ií]s|todas as regi[oõ]es|organiza[cç][oõ]es de todo o brasil|edital nacional", re.I)
_INT_BR = re.compile(r"\bbrazil\b|\bbrasil\b|latin america|am[eé]rica latina|worldwide|global call|all countries|any country|todos os pa[ií]ses", re.I)


def territorio(url: str, texto: str = "") -> str:
    """04/10 (titular): o Espião foca em GOIÁS, no que vale para TODO O BRASIL e no INTERNACIONAL aberto ao Brasil.
    GO · BR · INT · fora (outro estado, ou internacional sem o Brasil)."""
    h = (urllib.parse.urlsplit(url or "").hostname or "").lower()
    t = (texto or "")[:6000]
    if h.endswith(".go.gov.br") or h.endswith(".go.leg.br") or "goias" in h or "goiania" in h or _GO.search(t):
        return "GO"
    m = re.search(r"\.([a-z]{2})\.(gov|leg|jus|mp)\.br$", h)
    if m and m.group(1) in UF_SIGLAS:
        return "BR" if _BR.search(t) else "fora"
    if h.endswith(".br") or h.endswith("gov.br"):
        return "BR"
    return "INT" if _INT_BR.search(t) else "fora"


def foco_da_consulta(consulta: str, n: int) -> str:
    """Consulta sem território ganha o foco, em rodízio: Goiás → nacional → internacional aberto ao Brasil."""
    if re.search(r"goi[aá]s|goi[aâ]nia|nacional|brasil|brazil|international|internacional", consulta, re.I):
        return consulta
    foco = (load_json(CFG).get("espiao") or {}).get("foco_territorial") or {}
    suf = foco.get("sufixos") or ["Goiás", "nacional todo o Brasil", "internacional elegível Brasil"]
    return f"{consulta} {suf[n % len(suf)]}"


def caçar(ia, angulo: dict, conhecidos: set[str], max_consultas: int = 3, max_paginas: int = 4) -> tuple[list[dict], str, list[str]]:
    """O voo completo: o Piloto cria as consultas, busca, lê e decide.
    Devolve (achados, lição, consultas usadas)."""
    if not local_brasil():                                  # 03/10 (titular): na nuvem, 2 buscas por voo
        max_consultas = min(max_consultas, int(os.environ.get("ELDORADO_BUSCAS_NA_NUVEM", "2")))
    from .cargo_piloto import licoes_para_o_prompt
    cfg = load_json(CFG)
    lic = licoes_para_o_prompt()
    # 1) o Piloto CRIA um QUESTIONAMENTO NOVO — nunca repete consulta nem variação próxima
    usadas = consultas_ja_usadas()
    amostra = usadas[:18]
    r = ia.perguntar((lic + "\n\n" if lic else "") +
                     f"OBJETIVO DA MISSÃO ({angulo.get('nivel','')}): {angulo['pergunta']}\n\n"
                     + ("JÁ PERGUNTEI ISTO ANTES (não repita, nem com palavras parecidas):\n- " + "\n- ".join(amostra) + "\n\n" if amostra else "")
                     + "Escreva consultas de busca NOVAS, em português do Brasil, que encontrem PÁGINAS OFICIAIS. "
                       "Foque em EMPRESA PRIVADA: instituto próprio, fundação, programa social, relatório ESG, patrocínio declarado, edital de anos anteriores. "
                       "Varie o ângulo a cada consulta (setor, região, tipo de documento, ano) — consultas parecidas entre si não servem.",
                     '{"consultas": ["consulta 1", "consulta 2", "consulta 3"], "porque_sao_novas": "uma frase"}')
    brutas = [c for c in ((r or {}).get("consultas") or []) if isinstance(c, str) and len(c) > 8]
    consultas, descartadas = [], 0
    for c in brutas:
        if inedita(c, usadas + consultas):
            consultas.append(c)
        else:
            descartadas += 1
        if len(consultas) >= max_consultas:
            break
    if not consultas:                                   # rede de segurança com variação do ângulo e do ano
        import random as _rr
        tempero = _rr.Random(f"{date.today()}-{angulo['id']}").choice(["site oficial", "edital 2026", "programa social", "relatório ESG", "seleção de projetos", "instituto"])
        consultas = [re.sub(r"\s+", " ", angulo["pergunta"])[:100] + " " + tempero]
    # 2) BUSCA DE VERDADE
    brutos, vistos = [], set()
    consultas = [foco_da_consulta(c, len(usadas) + k) for k, c in enumerate(consultas)]   # 04/10: GO → BR → INT
    for c in consultas:
        for it in buscar(c, 8):
            if it["url"] in vistos:
                continue
            vistos.add(it["url"]); brutos.append({**it, "consulta": c})
    if not brutos:
        return [], f"ângulo '{angulo['id']}': a busca não devolveu resultado (rede ou bloqueio)", consultas
    # 3) o Piloto LÊ os resultados reais e escolhe
    lista = "\n".join(f"{i+1}. {b['titulo']} — {b['url']}\n   {b['trecho'][:160]}" for i, b in enumerate(brutos[:14]))
    q = ia.perguntar(f"OBJETIVO: {angulo['pergunta']}\n\nRESULTADOS REAIS DA BUSCA:\n{lista}\n\n"
                     "Quais destes são MESMO oportunidade de recurso para organização sem fins lucrativos (edital, chamada, seleção de projetos, patrocínio, doação, incentivo fiscal)? "
                     "Descarte notícia, vaga de emprego, licitação, curso e página institucional sem oportunidade.",
                     '{"escolhidos": [{"n": número da lista, "porque": "uma frase", "tipo": "edital|programa|financiador"}]}')
    escolhidos = [(x.get("n"), x) for x in ((q or {}).get("escolhidos") or []) if isinstance(x.get("n"), int) and 1 <= x["n"] <= len(brutos[:14])]
    achados = []
    for n, x in escolhidos[:max_paginas]:
        b = brutos[n - 1]
        texto = ler_pagina(b["url"])                     # 4) confirma na própria página
        conf = None
        if len(texto) < 300:                              # página não abriu: o trecho do resultado ainda serve de pista
            texto = f"{b['titulo']} {b.get('trecho','')}"
        if len(texto) > 60:
            conf = ia.perguntar(
                f"PÁGINA: {b['url']}\nTEXTO: {texto[:3500]}\n\n"
                "Isto é uma oportunidade de recurso para organização sem fins lucrativos? "
                "Leia com atenção o PRAZO e os DOCUMENTOS exigidos. "
                "Se o prazo já passou ou o edital é de ano anterior, marque situacao='arquivada' — ela ainda serve, "
                "porque indica que o financiador costuma abrir de novo. Só escreva prazo se a data estiver ESCRITA na página.",
                '{"e_oportunidade": true|false, "nome": "nome da oportunidade ou do financiador", '
                '"trecho": "frase literal da página que comprova", "quem_pode": "...", "onde_inscrever": "url ou null", '
                '"situacao": "aberta|arquivada|sem_prazo_na_pagina", "prazo": "AAAA-MM-DD ou null", '
                '"documentos": ["documento exigido", "..."], "valor": "o que a página diz sobre valores ou null", '
                '"recorrente": true|false}')
        def _n(s): return re.sub(r"[^a-z0-9 ]", " ", re.sub(r"\s+", " ", (s or "").lower())).strip()
        ok = bool(conf and conf.get("e_oportunidade") and conf.get("trecho") and _n(str(conf["trecho"]))[:45] in _n(texto))
        nome = (conf or {}).get("nome") or b["titulo"]
        chave = re.sub(r"[^a-z0-9 ]", "", str(nome).lower())[:60]
        c = conf or {}
        prazo = c.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("prazo") or "")) else None
        sit = c.get("situacao") if c.get("situacao") in ("aberta", "arquivada", "sem_prazo_na_pagina") else "sem_prazo_na_pagina"
        if prazo:                                         # a data manda: o modelo às vezes erra o rótulo
            sit = "aberta" if prazo >= date.today().isoformat() else "arquivada"
        achados.append({"titulo": str(nome)[:110], "onde": b["url"][:140], "url": b["url"],
                        "trecho": c.get("trecho", "")[:180], "porque": x.get("porque", "")[:120],
                        "situacao": sit, "prazo": prazo,
                        "documentos": [str(d)[:70] for d in (c.get("documentos") or [])][:8],
                        "quem_pode": str(c.get("quem_pode") or "")[:120], "valor": str(c.get("valor") or "")[:90],
                        "recorrente": bool(c.get("recorrente")), "onde_inscrever": c.get("onde_inscrever"),
                        "consulta": b["consulta"][:90], "confirmado_na_pagina": ok,
                        "territorio": (terr := territorio(b["url"], texto)),
                        "novo": ok and _oficial(b["url"]) and chave not in conhecidos and terr in ("GO", "BR", "INT")})
    novos = sum(1 for a in achados if a["novo"])
    abertas = sum(1 for a in achados if a.get("situacao") == "aberta")
    arquiv = sum(1 for a in achados if a.get("situacao") == "arquivada")
    fontes = ", ".join(sorted({b.get("buscador", "?") for b in brutos}))
    licao = (f"ângulo '{angulo['id']}': {len(consultas)} consulta(s) nova(s)" + (f" ({descartadas} repetida(s) descartada(s))" if descartadas else "") +
             f" → {len(brutos)} resultado(s) [{fontes}] → {len(achados)} lido(s) → {novos} confirmado(s) na página"
             f" ({abertas} aberta(s), {arquiv} arquivada(s))"
             if achados else f"ângulo '{angulo['id']}': busca voltou {len(brutos)} resultados, nenhum passou no crivo")
    return achados, licao, consultas


if __name__ == "__main__":
    import sys
    print(json.dumps(buscar(" ".join(sys.argv[1:]) or "edital organizações da sociedade civil 2026", 6), ensure_ascii=False, indent=1))
