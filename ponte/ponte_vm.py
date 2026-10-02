#!/usr/bin/env python3
"""PONTE BRASIL em máquina virtual (alternativa ao ponte.php) — o mesmo protocolo, em Python puro.

Use numa VM com IP brasileiro (Oracle Cloud Always Free em São Paulo/Vinhedo, ou VM paga). Mais simples ainda: na VM,
rode o próprio repositório pelo cron (scripts/instalar_vm_brasil.sh) — aí esta ponte nem é necessária. Ela serve
quando se prefere que todo o trabalho continue no GitHub e a VM só empreste o endereço.

    ELDORADO_PONTE_CHAVE='frase longa' python3 ponte/ponte_vm.py --porta 8088
    (ponha um HTTPS na frente — Caddy faz isso sozinho: `caddy reverse-proxy --from ponte.seudominio --to :8088`)

Segurança: pedido assinado (HMAC-SHA256 de "ts\\nurl", 5 minutos), só os domínios de `python -m src.indexadores
ponte-dominios` (arquivo ponte/dominios.txt ou a lista embutida), só destino de IP público, 120 pedidos/minuto, 6 MB.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import ipaddress
import json
import os
import socket
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 6_000_000
LIMITE_POR_MINUTO = 120
SUFIXOS_PADRAO = ["gov.br", "jus.br", "leg.br", "mp.br", "def.br"]
_contagem: dict = {}


def dominios() -> list[str]:
    arq = Path(__file__).with_name("dominios.txt")
    if arq.exists():
        return [x.strip().lower() for x in arq.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    return SUFIXOS_PADRAO


def permitido(host: str, lista: list[str]) -> bool:
    h = (host or "").lower()
    return any(h == d or h.endswith("." + d) for d in lista)


def ip_publico(host: str) -> bool:
    try:
        return all(ipaddress.ip_address(info[4][0]).is_global for info in socket.getaddrinfo(host, None))
    except Exception:
        return False


def atender(pedido: dict, chave: str, lista: list[str], abrir=urllib.request.urlopen, checar_ip=ip_publico) -> tuple[int, dict]:
    url, ts, sig = str(pedido.get("url") or ""), int(pedido.get("ts") or 0), str(pedido.get("assinatura") or "")
    if abs(time.time() - ts) > 300:
        return 403, {"ok": False, "erro": "pedido expirado"}
    esperado = hmac.new(chave.encode(), f"{ts}\n{url}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, sig):
        return 403, {"ok": False, "erro": "assinatura inválida"}
    u = urlsplit(url)
    if u.scheme not in ("https", "http") or not u.hostname:
        return 400, {"ok": False, "erro": "endereço inválido"}
    if not permitido(u.hostname, lista):
        return 403, {"ok": False, "erro": f"dominio fora da lista da ponte: {u.hostname}"}
    if not checar_ip(u.hostname):
        return 403, {"ok": False, "erro": "destino não é público"}
    minuto = int(time.time() // 60)
    _contagem[minuto] = _contagem.get(minuto, 0) + 1
    if _contagem[minuto] > LIMITE_POR_MINUTO:
        return 429, {"ok": False, "erro": "limite de pedidos por minuto"}
    mx = max(1000, min(MAX_BYTES, int(pedido.get("max_bytes") or MAX_BYTES)))
    cab = {"User-Agent": "Mozilla/5.0 (compatible; EldoradoIndexadores/1.0; ponte Brasil VM)"}
    for k, v in (pedido.get("cabecalhos") or {}).items():
        if str(k).lower() in ("accept", "accept-language", "if-none-match", "if-modified-since"):
            cab[k] = str(v).replace("\r", "").replace("\n", "")
    try:
        with abrir(urllib.request.Request(url, headers=cab), timeout=40) as r:
            st, final, hdr, corpo = getattr(r, "status", 200), r.geturl(), dict(r.headers.items()), r.read(mx)
    except urllib.error.HTTPError as e:
        st, final, hdr, corpo = e.code, url, dict(e.headers.items()) if e.headers else {}, (e.read(4000) if e.fp else b"")
    except Exception as e:
        return 200, {"ok": False, "erro": f"falha de rede na ponte: {type(e).__name__}"}
    if not permitido(urlsplit(final).hostname or "", lista):
        return 403, {"ok": False, "erro": "redirecionou para domínio fora da lista"}
    guardar = {k.lower(): v for k, v in hdr.items() if k.lower() in ("content-type", "etag", "last-modified", "server", "cf-ray",
                                                                      "content-encoding", "x-wp-totalpages", "x-wp-total")}
    return 200, {"ok": True, "status": st, "url_final": final, "cabecalhos": guardar, "corpo_b64": base64.b64encode(corpo).decode()}


def servir(porta: int) -> None:
    chave = os.environ.get("ELDORADO_PONTE_CHAVE") or ""
    if len(chave) < 24:
        raise SystemExit("defina ELDORADO_PONTE_CHAVE com uma frase de 24+ caracteres")
    lista = dominios()

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                n = int(self.headers.get("Content-Length") or 0)
                pedido = json.loads(self.rfile.read(min(n, 100_000)).decode("utf-8"))
                codigo, resp = atender(pedido, chave, lista)
            except Exception:
                codigo, resp = 400, {"ok": False, "erro": "pedido inválido"}
            corpo = json.dumps(resp, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, *a):
            pass

    print(f"ponte Brasil ouvindo na porta {porta} ({len(lista)} domínios)")
    ThreadingHTTPServer(("0.0.0.0", porta), H).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--porta", type=int, default=8088)
    servir(ap.parse_args().porta)
