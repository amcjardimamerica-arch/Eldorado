"""Degrau 6: a cópia arquivada (Wayback Machine), quando o site está fora do ar ou bloqueou.

Usa a API pública direto (sem o waybackpy: uma chamada simples não justifica a dependência). O achado que vem daqui
é marcado como cópia arquivada; a fonte oficial continua sendo o site do órgão.
"""
from __future__ import annotations

import httpx

from .escada import Bloqueado, Passageiro, Resposta


class DegrauArquivo:
    nome = "6 · cópia arquivada (Wayback Machine)"
    pesado = False

    def __init__(self, base: str = "https://web.archive.org"):
        self.base = base.rstrip("/")
        self.cliente = httpx.Client(follow_redirects=True, headers={"User-Agent": "Eldorado/0.1"})

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        try:
            r = self.cliente.get(f"{self.base}/cdx/search/cdx", params={"url": url, "output": "json", "limit": "-1", "filter": "statuscode:200"},
                                 timeout=tempo_limite)
            linhas = r.json() if r.status_code == 200 and r.content.strip() else []
        except (httpx.TransportError, ValueError) as e:
            raise Passageiro(f"Wayback: {e}") from e
        if len(linhas) < 2:
            raise Bloqueado("sem cópia arquivada")
        campos = dict(zip(linhas[0], linhas[-1], strict=False))
        copia = f"{self.base}/web/{campos['timestamp']}id_/{campos.get('original', url)}"
        try:
            c = self.cliente.get(copia, timeout=tempo_limite)
        except httpx.TransportError as e:
            raise Passageiro(f"Wayback: {e}") from e
        r = Resposta(url, c.status_code, c.content, c.headers.get("content-type", ""), copia_arquivada=True)
        r.alertas.append(f"cópia arquivada de {campos['timestamp']}")
        return r
