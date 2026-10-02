"""Rede dos indexadores: robots.txt (RFC 9309), cortesia por site, cache condicional, orçamento e rotas.

Uma única instância de `Rede` por rodada. Ela:
  - lê e guarda o robots.txt de cada host (24 h) e respeita Disallow/Allow e Crawl-delay;
  - espera o intervalo do site entre duas requisições ao mesmo host;
  - manda If-None-Match / If-Modified-Since quando já leu o endereço (304 = nada mudou, nada se baixa);
  - conta as requisições e o tempo: estourou o orçamento, para e deixa o resto para a próxima rodada;
  - escolhe a SAÍDA: direta (nuvem ou coleta local no Brasil) ou pela ponte Brasil;
  - classifica a falha (robots, geo, waf, limite, http, rede) para a escada de rotas decidir o próximo passo.
"""
from __future__ import annotations

import gzip
import re
import socket
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from . import ponte as _ponte


class Bloqueio(Exception):
    """Falha classificada. tipo: robots | geo | waf | limite | http | rede | ponte_indisponivel | orcamento | tamanho"""

    def __init__(self, tipo: str, detalhe: str = "", status: int | None = None):
        super().__init__(f"{tipo}: {detalhe}")
        self.tipo, self.detalhe, self.status = tipo, detalhe, status


@dataclass
class Resposta:
    url: str
    url_final: str
    status: int
    corpo: bytes
    cabecalhos: dict
    saida: str                       # direta | ponte | cache
    nao_mudou: bool = False

    def texto(self) -> str:
        cs = "utf-8"
        m = re.search(r"charset=([\w-]+)", self.cabecalhos.get("content-type", ""), re.I)
        if m:
            cs = m.group(1)
        else:
            m = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", self.corpo[:3000], re.I)
            if m:
                cs = m.group(1).decode("ascii", "ignore")
        try:
            return self.corpo.decode(cs, "replace")
        except LookupError:
            return self.corpo.decode("utf-8", "replace")


# ------------------------------------------------------------------ robots.txt (RFC 9309)
def analisar_robots(txt: str) -> list[dict]:
    """Grupos do robots.txt: [{'agentes': [...], 'regras': [(permite, padrão)], 'atraso': float|None}].
    Linhas User-agent seguidas formam um grupo; regras antes de qualquer User-agent são ignoradas."""
    grupos: list[dict] = []
    atual = None
    ultimo_foi_agente = False
    for linha in (txt or "").splitlines():
        linha = linha.split("#", 1)[0].strip()
        if ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        chave, valor = chave.strip().lower(), valor.strip()
        if chave == "user-agent":
            if atual is None or not ultimo_foi_agente:
                atual = {"agentes": [], "regras": [], "atraso": None}
                grupos.append(atual)
            atual["agentes"].append(valor.lower())
            ultimo_foi_agente = True
            continue
        ultimo_foi_agente = False
        if atual is None:
            continue
        if chave in ("allow", "disallow"):
            if valor:
                atual["regras"].append((chave == "allow", valor))
            elif chave == "disallow":
                pass                                    # "Disallow:" vazio = sem restrição
        elif chave == "crawl-delay":
            try:
                atual["atraso"] = float(valor)
            except ValueError:
                pass
    return grupos


def _casa_padrao(padrao: str, caminho: str) -> bool:
    rx = "".join(".*" if c == "*" else re.escape(c) for c in padrao.rstrip("$"))
    rx = "^" + rx + ("$" if padrao.endswith("$") else "")
    return re.match(rx, caminho) is not None


def regras_para(grupos: list[dict], token: str) -> tuple[list, float | None]:
    """Soma os grupos do nosso token (se houver) ou, senão, TODOS os grupos de '*' (RFC 9309 §2.2.1)."""
    t = token.lower()
    meus = [g for g in grupos if any(a != "*" and a in t for a in g["agentes"])]
    if not meus:
        meus = [g for g in grupos if "*" in g["agentes"]]
    regras = [r for g in meus for r in g["regras"]]
    atrasos = [g["atraso"] for g in meus if g.get("atraso")]
    return regras, (max(atrasos) if atrasos else None)


def permitido(regras: list, caminho: str) -> bool:
    """A regra mais longa que casa decide; empate → Allow vence. /robots.txt é sempre permitido."""
    if caminho == "/robots.txt":
        return True
    melhor = None
    for permite, padrao in regras:
        if _casa_padrao(padrao, caminho):
            tam = len(padrao.replace("*", "").rstrip("$"))
            if melhor is None or tam > melhor[0] or (tam == melhor[0] and permite):
                melhor = (tam, permite)
    return True if melhor is None else melhor[1]


# ------------------------------------------------------------------ rede
_WAF = re.compile(r"cf-ray|cloudflare|akamai|incapsula|sucuri|ddos-guard|perimeterx|captcha|challenge", re.I)


@dataclass
class Rede:
    token: str
    user_agent: str
    pausa_padrao: float = 1.5
    timeout: int = 25
    bytes_max: int = 4_000_000
    orcamento: int = 700
    tempo_max: float = 1500
    local_brasil: bool = False
    robots_cache: dict = field(default_factory=dict)       # host -> {'em','status','regras','atraso'}
    http_cache: dict = field(default_factory=dict)         # url  -> {'etag','lm'}
    abrir: object = None                                   # injeção para testes: abrir(req, timeout) -> resposta
    dormir: object = time.sleep
    relogio: object = time.monotonic
    _ultimo: dict = field(default_factory=dict)
    usadas: int = 0
    por_host: dict = field(default_factory=dict)

    def __post_init__(self):
        self._inicio = self.relogio()
        if self.abrir is None:
            self.abrir = urllib.request.urlopen

    # ---- orçamento
    def resta_tempo(self) -> float:
        return self.tempo_max - (self.relogio() - self._inicio)

    def esgotado(self) -> bool:
        return self.usadas >= self.orcamento or self.resta_tempo() <= 0

    # ---- robots
    def robots(self, url: str, via: str = "direta") -> tuple[bool, float | None]:
        u = urlsplit(url)
        host = (u.hostname or "").lower()
        reg = self.robots_cache.get(host)
        agora = datetime.now(timezone.utc)
        fresco = reg and reg.get("em") and datetime.fromisoformat(reg["em"]) > agora - timedelta(hours=24)
        if not fresco:
            regras, atraso, status = [], None, None
            try:
                r = self._baixar(f"{u.scheme or 'https'}://{u.netloc}/robots.txt", via=via, pausa=0.5, condicional=False,
                                 max_bytes=500_000)
                status = r.status
                regras, atraso = regras_para(analisar_robots(r.texto()), self.token)
            except Bloqueio as b:
                status = b.status
                if b.status and 400 <= b.status < 500:
                    regras = []                          # 4xx: robots inexistente → tudo permitido (RFC 9309)
                elif reg:                                # falhou agora, mas há leitura anterior: vale a anterior
                    return permitido(reg.get("regras") or [], u.path or "/"), reg.get("atraso")
                else:
                    raise Bloqueio(b.tipo if b.tipo in ("geo", "waf", "rede", "ponte_indisponivel") else "rede",
                                   f"robots.txt inacessível: {b.detalhe}", b.status)
            reg = {"em": agora.isoformat(timespec="seconds"), "status": status, "regras": regras, "atraso": atraso}
            self.robots_cache[host] = reg
        caminho = (u.path or "/") + (("?" + u.query) if u.query else "")
        return permitido(reg.get("regras") or [], caminho), reg.get("atraso")

    # ---- leitura
    def obter(self, url: str, *, via: str = "direta", pausa: float | None = None, timeout: int | None = None,
              max_bytes: int | None = None, condicional: bool = True, aceitar: str = "*/*",
              checar_robots: bool = True) -> Resposta:
        if self.esgotado():
            raise Bloqueio("orcamento", "orçamento da rodada esgotado")
        atraso = None
        if checar_robots:
            ok, atraso = self.robots(url, via=via)
            if not ok:
                raise Bloqueio("robots", f"robots.txt proíbe {urlsplit(url).path}")
        p = max(float(pausa if pausa is not None else self.pausa_padrao), float(atraso or 0))
        return self._baixar(url, via=via, pausa=p, timeout=timeout, max_bytes=max_bytes, condicional=condicional, aceitar=aceitar)

    def _esperar(self, host: str, pausa: float) -> None:
        ult = self._ultimo.get(host)
        if ult is not None:
            falta = pausa - (self.relogio() - ult)
            if falta > 0:
                self.dormir(min(falta, 60))
        self._ultimo[host] = self.relogio()

    def _baixar(self, url: str, *, via: str, pausa: float, timeout: int | None = None, max_bytes: int | None = None,
                condicional: bool = True, aceitar: str = "*/*") -> Resposta:
        host = (urlsplit(url).hostname or "").lower()
        if not url.startswith(("https://", "http://")):
            raise Bloqueio("http", "endereço inválido")
        tmo = int(timeout or self.timeout)
        lim = int(max_bytes or self.bytes_max)
        self._esperar(host, pausa)
        self.usadas += 1
        self.por_host[host] = self.por_host.get(host, 0) + 1
        cab = {"User-Agent": self.user_agent, "Accept": aceitar, "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.6"}
        cache = self.http_cache.get(url) if condicional else None
        if cache:
            if cache.get("etag"):
                cab["If-None-Match"] = cache["etag"]
            if cache.get("lm"):
                cab["If-Modified-Since"] = cache["lm"]
        if via == "ponte" and not self.local_brasil:
            if not _ponte.configurada():
                raise Bloqueio("ponte_indisponivel", "sem ponte configurada e fora do Brasil")
            try:
                status, final, corpo, hdr = _ponte.buscar(url, cab, tmo, lim)
            except _ponte.ErroPonte as e:
                raise Bloqueio(e.tipo, e.detalhe, e.status)
            saida = "ponte"
        else:
            req = urllib.request.Request(url, headers=cab)
            try:
                with self.abrir(req, timeout=tmo) as r:
                    status = getattr(r, "status", 200) or 200
                    final = r.geturl() if hasattr(r, "geturl") else url
                    hdr = {k.lower(): v for k, v in (r.headers.items() if getattr(r, "headers", None) else [])}
                    corpo = r.read(lim + 1)
            except urllib.error.HTTPError as e:
                hdr = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
                if e.code == 304:
                    return Resposta(url, url, 304, b"", hdr, "cache", nao_mudou=True)
                trecho = b""
                try:
                    trecho = e.read(4000)
                except Exception:
                    pass
                raise Bloqueio(classificar_http(e.code, hdr, trecho), f"HTTP {e.code}", e.code)
            except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError) as e:
                motivo = getattr(e, "reason", e)
                raise Bloqueio("rede", f"{type(e).__name__}: {str(motivo)[:120]}")
            saida = "direta"
        if status == 304:
            return Resposta(url, final, 304, b"", hdr, "cache", nao_mudou=True)
        if status >= 400:
            raise Bloqueio(classificar_http(status, hdr, corpo[:4000]), f"HTTP {status}", status)
        if len(corpo) > lim:
            corpo = corpo[:lim]
        enc = (hdr.get("content-encoding") or "").lower()
        try:
            if "gzip" in enc or corpo[:2] == b"\x1f\x8b":
                corpo = gzip.decompress(corpo)
            elif "deflate" in enc:
                corpo = zlib.decompress(corpo)
        except Exception:
            pass
        if hdr.get("etag") or hdr.get("last-modified"):
            self.http_cache[url] = {"etag": hdr.get("etag"), "lm": hdr.get("last-modified")}
        return Resposta(url, final, status, corpo, hdr, saida)


def classificar_http(status: int, cabecalhos: dict, corpo: bytes = b"") -> str:
    """403/451 sem sinal de proteção anti-robô → 'geo' (o portal recusa IP estrangeiro/de datacenter);
    com Cloudflare/Akamai/captcha → 'waf' (precisa de navegador); 429 → 'limite'; o resto → 'http'."""
    sinais = " ".join(f"{k}:{v}" for k, v in (cabecalhos or {}).items()) + " " + (corpo or b"")[:4000].decode("utf-8", "ignore")
    if status in (403, 451, 401):
        return "waf" if _WAF.search(sinais) else "geo"
    if status == 429:
        return "limite"
    return "http"
