"""SKILL DO ESPIÃO — LEITURA DE IMAGENS (titular, 16/10/2026).

Em sites de associações de Goiás e de eventos, quem patrocina aparece em IMAGEM: flyer, cartaz, banner, faixa de logos
("patrocínio", "apoio", "realização"). A skill separa essas imagens da página, envia ao modelo de visão e devolve os
NOMES DAS EMPRESAS patrocinadoras/apoiadoras, com a imagem de onde saíram (prova). Sem credencial de IA não roda —
nunca simula. Nada é suposto: empresa só entra se o nome estiver legível na imagem.
"""
from __future__ import annotations

import base64
import json
import re
import urllib.request
from urllib.parse import urljoin

PISTA = re.compile(r"(?i)patroc|apoio|apoiador|parceir|realiza|flyer|cartaz|banner|faixa|logos?|sponsor|evento|programa")
TIPOS = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}


def imagens_da_pagina(url: str, html: str, maximo: int = 4) -> list[str]:
    """As imagens com cara de flyer/cartaz/faixa de patrocínio (pelo nome do arquivo, alt ou classe)."""
    out = []
    for m in re.finditer(r"<img\b[^>]*>", html or "", re.I):
        tag = m.group(0)
        src = re.search(r"""(?:data-src|src)=["']([^"']+)["']""", tag, re.I)
        if not src:
            continue
        u = urljoin(url, src.group(1))
        ext = u.lower().split("?")[0].rsplit(".", 1)[-1]
        if ext not in TIPOS or u in out:
            continue
        if PISTA.search(tag) or PISTA.search(u):
            out.append(u)
        if len(out) >= maximo:
            break
    return out


def _baixar(u: str, limite: int = 4_000_000) -> tuple[bytes, str] | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
            b = r.read(limite + 1)
        if len(b) > limite or len(b) < 2000:
            return None
        return b, TIPOS.get(u.lower().split("?")[0].rsplit(".", 1)[-1], "image/jpeg")
    except Exception:  # noqa: BLE001
        return None


def patrocinadores(url: str, html: str | None = None, maximo: int = 4) -> list[dict]:
    """[{empresa, papel, imagem}] lidos nas imagens da página. [] sem credencial ou sem imagem legível."""
    from .. import ia
    if not ia.credencial():
        return []
    if html is None:
        b = _baixar(url, limite=3_000_000)
        html = b[0].decode("utf-8", "replace") if b else ""
    blocos = []
    usadas = []
    for u in imagens_da_pagina(url, html, maximo):
        b = _baixar(u)
        if b:
            blocos.append({"type": "image", "source": {"type": "base64", "media_type": b[1], "data": base64.b64encode(b[0]).decode()}})
            blocos.append({"type": "text", "text": f"(imagem {len(usadas) + 1}: {u})"})
            usadas.append(u)
    if not blocos:
        return []
    blocos.append({"type": "text", "text": "Liste SOMENTE empresas/instituições cujo NOME está legível nas imagens como patrocinadora, apoiadora, "
                   "parceira ou realizadora. Não deduza nem complete nomes. Responda só JSON: "
                   "[{\"empresa\": \"...\", \"papel\": \"patrocínio|apoio|parceria|realização\", \"imagem\": <número>}]"})
    try:
        txt = ia.chamar("leitura_imagens", "Você lê flyers e faixas de logos de eventos de associações e extrai patrocinadores, sem supor nada.",
                        blocos, max_tokens=1200)
        dados = json.loads(re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip())
    except Exception:  # noqa: BLE001
        return []
    out = []
    for d in dados if isinstance(dados, list) else []:
        n = int(d.get("imagem") or 0)
        if d.get("empresa") and 1 <= n <= len(usadas):
            out.append({"empresa": str(d["empresa"]).strip()[:120], "papel": d.get("papel"), "imagem": usadas[n - 1], "pagina": url})
    return out
