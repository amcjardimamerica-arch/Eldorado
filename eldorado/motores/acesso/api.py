"""Degrau 1: as APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN) com o httpx."""
from __future__ import annotations

import httpx

from .escada import Passageiro, Resposta

AGENTE = "Eldorado/0.1 (+oportunidades para organizacoes da sociedade civil)"   # cabeçalho HTTP: só ASCII


class DegrauAPI:
    nome = "1 · API oficial (httpx)"
    pesado = False

    def __init__(self, cabecalhos: dict[str, str] | None = None):
        self.cliente = httpx.Client(follow_redirects=True, headers={"User-Agent": AGENTE, "Accept": "application/json, */*", **(cabecalhos or {})})

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        try:
            r = self.cliente.get(url, timeout=tempo_limite)
        except httpx.TransportError as e:
            raise Passageiro(f"{type(e).__name__}: {e}") from e
        return Resposta(str(r.url), r.status_code, r.content, r.headers.get("content-type", ""))
