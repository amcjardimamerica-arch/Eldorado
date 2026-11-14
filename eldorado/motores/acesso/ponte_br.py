"""A ponte da HostGator (titular, 25/10/2026): o IP brasileiro para os sites que recusam a nuvem (a CESE, o TJ-GO, o MP-GO,
a Câmara de Goiânia, as prefeituras de Goiás...). É a ponte do Eldorado0, a mesma que está instalada e funcionando:
ponte/ponte.php na hospedagem da titular recebe o pedido ASSINADO, lê a página pública com o IP brasileiro e devolve.

O protocolo (o mesmo do PHP): POST JSON {"url", "ts", "assinatura", "max_bytes"}, com a assinatura
HMAC-SHA256(chave, f"{ts}\\n{url}") em hexadecimal; o servidor recusa ts com mais de 5 minutos, assinatura errada e domínio
fora da lista (a ponte não é um proxy aberto). A resposta: {"ok": true, "status", "url_final", "cabecalhos", "corpo_b64"}
ou {"ok": false, "erro", "status"}. Os segredos: ELDORADO_PONTE_URL e ELDORADO_PONTE_CHAVE (nunca em arquivo).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .escada import Bloqueado, Indisponivel, Passageiro, Resposta

LISTA = Path(__file__).resolve().parents[3] / "config/ponte_dominios.txt"
# 14/11/2026 (R56, S6): os domínios que a ponte já atendia e que o sistema não manda direto por ela
LISTA_BASE = Path(__file__).resolve().parents[3] / "config/ponte_base.txt"


def dominios_da_ponte() -> list[str]:
    """A lista DOMINIOS do ponte.php: a união da lista do sistema (os que recusam a nuvem) e da base (R56, S6)."""
    out = set()
    for arq in (LISTA, LISTA_BASE):
        try:
            for linha in arq.read_text(encoding="utf-8").splitlines():
                d = linha.split("#")[0].strip().lower()
                if d:
                    out.add(d)
        except OSError:
            continue
    return sorted(out)


def configurada() -> bool:
    return bool(os.environ.get("ELDORADO_PONTE_URL") and os.environ.get("ELDORADO_PONTE_CHAVE"))


@lru_cache(maxsize=1)
def dominios() -> frozenset[str]:
    try:
        return frozenset(x.strip().lower() for x in LISTA.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#"))
    except OSError:
        return frozenset()


def precisa(url: str) -> bool:
    h = (urlsplit(url).hostname or "").lower()
    return h in dominios() or h.removeprefix("www.") in dominios() or f"www.{h}" in dominios()


def usar(url: str) -> bool:
    """Passa pela ponte? Com a ponte configurada e num domínio da lista (os que recusam a nuvem)."""
    return configurada() and precisa(url)


def assinar(chave: str, ts: int, url: str, modo: str = "") -> str:
    msg = f"{ts}\n{modo}\n{url}" if modo else f"{ts}\n{url}"          # 14/11/2026 (R55, C17): o modo entra na assinatura
    return hmac.new(chave.encode("utf-8"), msg.encode(), hashlib.sha256).hexdigest()


# 08/11/2026 (parecer dos motores): o arquivo de programas do Transferegov tem 11 MB e a ponte cortava em 6 MB ("Callback
# aborted": 108 de 118 leituras do motor em erro, caindo no computador local). O ponte.php aceita até 16 MB (MAX_BYTES).
MAX_BYTES = 15_000_000


def buscar(url: str, tempo_limite: float = 40, max_bytes: int = MAX_BYTES, modo: str = "") -> Resposta:
    ponte, chave = os.environ["ELDORADO_PONTE_URL"], os.environ["ELDORADO_PONTE_CHAVE"]
    ts = int(time.time())
    corpo = {"url": url, "ts": ts, "assinatura": assinar(chave, ts, url, modo), "max_bytes": int(max_bytes),
             **({"modo": modo} if modo else {}),
             "cabecalhos": {"Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.5", "Accept-Language": "pt-BR,pt;q=0.9"}}
    try:
        r = httpx.post(ponte, json=corpo, timeout=tempo_limite, headers={"User-Agent": "EldoradoPonte/1.0"})
        d = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise Passageiro(f"a ponte BR não respondeu: {type(e).__name__}") from e
    if not d.get("ok"):
        erro = str(d.get("erro") or "")
        if "dominio" in erro.lower() or "domínio" in erro.lower():
            raise Bloqueado(f"a ponte BR recusou o domínio (fora da lista do ponte.php): {erro[:120]}")
        if "assinatura" in erro.lower():
            raise Indisponivel(f"a ponte BR recusou a assinatura (a chave do GitHub difere da do ponte.php): {erro[:120]}")
        raise Passageiro(f"a ponte BR: {erro[:150] or d.get('status')}")
    conteudo = base64.b64decode(d.get("corpo_b64") or "")
    cab = {str(k).lower(): v for k, v in (d.get("cabecalhos") or {}).items()}
    return Resposta(d.get("url_final") or url, int(d.get("status") or 200), conteudo, cab.get("content-type", ""), alertas=["lida pela ponte BR (HostGator)"])


def diagnostico(url: str) -> dict:
    """Um teste da ponte (o comando eldorado ponte-br)."""
    if not configurada():
        return {"configurada": False}
    t = time.monotonic()
    try:
        r = buscar(url)
        return {"configurada": True, "ok": True, "status": r.status, "bytes": len(r.conteudo), "s": round(time.monotonic() - t, 1)}
    except Exception as e:  # noqa: BLE001
        return {"configurada": True, "ok": False, "erro": f"{type(e).__name__}: {str(e)[:200]}"}



class DegrauPonteBR:
    """A ponte como ferramenta do canivete de todo motor (titular, 25/10/2026): na escada, logo depois dos dois degraus da
    nuvem; um site que a nuvem não abre é tentado pela ponte antes dos navegadores (e a escada aprende o degrau)."""
    nome = "P · ponte BR (HostGator)"
    pesado = False                                               # não é navegador: não pede folga ao governador

    # 14/11/2026 (R55, C17): o modo do Espião — os sites privados fora da lista, até TETO_ESPIAO por turno, com a memória de
    # 6 horas do que a ponte recusou (o mesmo endereço não volta a ser pedido nesse prazo)
    modo: str = ""
    TETO_ESPIAO = 300
    MEMORIA_H = 6
    _pedidos_espiao = 0
    _recusados: dict = {}

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        if not configurada():
            raise Indisponivel("a ponte BR não está configurada neste ambiente (os segredos ELDORADO_PONTE_URL e ELDORADO_PONTE_CHAVE)")
        if self.modo != "espiao":
            return buscar(url, tempo_limite)
        agora = time.time()
        if DegrauPonteBR._recusados.get(url, 0) > agora:
            raise Bloqueado("a ponte recusou este endereço nas últimas 6 horas (memória do Espião)")
        if DegrauPonteBR._pedidos_espiao >= self.TETO_ESPIAO:
            raise Indisponivel(f"teto do Espião na ponte ({self.TETO_ESPIAO} por turno)")
        DegrauPonteBR._pedidos_espiao += 1
        try:
            return buscar(url, tempo_limite, modo="espiao")
        except (Bloqueado, Indisponivel):
            DegrauPonteBR._recusados[url] = agora + self.MEMORIA_H * 3600
            raise
