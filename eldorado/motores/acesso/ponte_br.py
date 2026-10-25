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


def assinar(chave: str, ts: int, url: str) -> str:
    return hmac.new(chave.encode("utf-8"), f"{ts}\n{url}".encode(), hashlib.sha256).hexdigest()


def buscar(url: str, tempo_limite: float = 40, max_bytes: int = 6_000_000) -> Resposta:
    ponte, chave = os.environ["ELDORADO_PONTE_URL"], os.environ["ELDORADO_PONTE_CHAVE"]
    ts = int(time.time())
    corpo = {"url": url, "ts": ts, "assinatura": assinar(chave, ts, url), "max_bytes": int(max_bytes),
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

