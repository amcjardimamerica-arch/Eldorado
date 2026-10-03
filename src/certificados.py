"""CADEIAS DE CERTIFICADO QUE OS SITES NÃO ENVIAM (titular, 03/10/2026).

Alguns portais enviam só o próprio certificado. O navegador completa a cadeia sozinho; o Python não. Aqui a conexão
segura usa o cadastro de confiança normal MAIS as cadeias guardadas em config/certificados/ (baixadas dos endereços
oficiais da autoridade certificadora pelo fluxo 25 — scripts/certificado_suap.py). A verificação continua SEMPRE ligada.
Caso real: o SUAP da Câmara de Goiânia (Let's Encrypt YR2 → ISRG Root YR → ISRG Root X1).
"""
from __future__ import annotations

import ssl
from functools import lru_cache
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1] / "config/certificados"


@lru_cache(maxsize=1)
def contexto() -> ssl.SSLContext:
    ctx = ssl.create_default_context()                     # verificação de certificado e de nome LIGADAS
    for pem in sorted(PASTA.glob("*.pem")):
        ctx.load_verify_locations(cafile=str(pem))
    return ctx
