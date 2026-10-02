"""PONTE BRASIL — leitura por um IP brasileiro para os portais que recusam IP estrangeiro.

Três jeitos, do mais barato ao mais robusto; o motor usa o que estiver disponível:

  1. COMPUTADOR DO TITULAR (grátis): scripts/coleta_brasil.py (ou o agendador instalado por
     scripts/agendar_coleta_brasil.ps1) roda com ELDORADO_LOCAL_BR=1 e lê direto, com a conexão de casa.
  2. MÁQUINA VIRTUAL NO BRASIL (grátis ou paga): o mesmo script num servidor com IP brasileiro, pelo cron
     (scripts/instalar_vm_brasil.sh). Oracle Cloud Always Free (São Paulo/Vinhedo), ou VM paga de R$ 30 a 60/mês.
  3. PONTE HTTP EM HOSPEDAGEM BRASILEIRA (Hostgator, Locaweb, KingHost...): ponte/ponte.php recebe o pedido
     assinado do GitHub, lê o portal com o IP brasileiro da hospedagem e devolve a página. O GitHub continua
     fazendo todo o trabalho; a hospedagem só empresta o endereço. Segredos do repositório:
        ELDORADO_PONTE_URL    https://seudominio.com.br/ponte/ponte.php
        ELDORADO_PONTE_CHAVE  uma frase longa e aleatória (a mesma gravada no ponte.php)

Protocolo (o mesmo em ponte/ponte.php e ponte/ponte_vm.py):
  POST JSON {"url", "ts", "assinatura", "cabecalhos", "max_bytes"}
  assinatura = HMAC-SHA256(chave, f"{ts}\n{url}") em hexadecimal; o servidor recusa ts com mais de 5 minutos,
  assinatura errada e domínio fora da lista permitida — a ponte não é um proxy aberto.
  Resposta JSON {"ok": true, "status", "url_final", "cabecalhos", "corpo_b64"} ou {"ok": false, "erro", "status"}.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request

ENV_URL = "ELDORADO_PONTE_URL"
ENV_CHAVE = "ELDORADO_PONTE_CHAVE"


class ErroPonte(Exception):
    def __init__(self, tipo: str, detalhe: str = "", status: int | None = None):
        super().__init__(f"{tipo}: {detalhe}")
        self.tipo, self.detalhe, self.status = tipo, detalhe, status


def local_brasil() -> bool:
    """Rodando no Brasil (computador do titular ou VM brasileira): lê direto, sem ponte."""
    return os.environ.get("ELDORADO_LOCAL_BR") == "1"


def configurada() -> bool:
    return bool(os.environ.get(ENV_URL) and os.environ.get(ENV_CHAVE))


def assinar(chave: str, ts: int, url: str) -> str:
    return hmac.new(chave.encode("utf-8"), f"{ts}\n{url}".encode("utf-8"), hashlib.sha256).hexdigest()


def buscar(url: str, cabecalhos: dict, timeout: int, max_bytes: int, *, abrir=None) -> tuple[int, str, bytes, dict]:
    ponte, chave = os.environ.get(ENV_URL), os.environ.get(ENV_CHAVE)
    if not (ponte and chave):
        raise ErroPonte("ponte_indisponivel", "segredos da ponte não configurados")
    ts = int(time.time())
    corpo = json.dumps({"url": url, "ts": ts, "assinatura": assinar(chave, ts, url), "max_bytes": int(max_bytes),
                        "cabecalhos": {k: v for k, v in cabecalhos.items() if k.lower() in (
                            "accept", "accept-language", "if-none-match", "if-modified-since")}}).encode("utf-8")
    req = urllib.request.Request(ponte, data=corpo, method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "EldoradoPonte/1.0"})
    try:
        with (abrir or urllib.request.urlopen)(req, timeout=timeout + 15) as r:
            dado = json.loads(r.read(int(max_bytes * 1.4) + 100_000).decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ErroPonte("ponte_indisponivel", f"a ponte respondeu HTTP {e.code}", e.code)
    except Exception as e:
        raise ErroPonte("ponte_indisponivel", f"{type(e).__name__}: {str(e)[:100]}")
    if not dado.get("ok"):
        st = dado.get("status")
        erro = str(dado.get("erro") or "")[:160]
        tipo = "geo" if st in (403, 451) else "rede" if not st else "http"
        if "dominio" in erro.lower() or "assinatura" in erro.lower():
            tipo = "ponte_indisponivel"
        raise ErroPonte(tipo, f"pela ponte: {erro}", st)
    hdr = {str(k).lower(): str(v) for k, v in (dado.get("cabecalhos") or {}).items()}
    return int(dado.get("status") or 200), str(dado.get("url_final") or url), base64.b64decode(dado.get("corpo_b64") or ""), hdr
