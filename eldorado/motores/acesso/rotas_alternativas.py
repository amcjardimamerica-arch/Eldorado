"""Degraus 7 e 8, reservas desligadas até o teste real na criação: o Tor (IP diferente) e o leitor público de páginas.

O Tor é o degrau 2 por um proxy SOCKS (exige o serviço do Tor na máquina). O leitor público (Jina Reader) devolve a
página já como texto e tem limite de uso. Os dois só entram quando ligados na configuração do motor.
"""
from __future__ import annotations

import socket

import httpx

from .escada import Indisponivel, Passageiro, Resposta
from .leve import DegrauLeve


class DegrauTor(DegrauLeve):
    nome = "7 · rota pelo Tor (reserva)"

    def __init__(self, porta: int = 9050):
        with socket.socket() as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", porta)) != 0:
                raise Indisponivel(f"serviço do Tor não encontrado na porta {porta}")
        super().__init__(proxy=f"socks5h://127.0.0.1:{porta}")


class DegrauLeitorPublico:
    nome = "8 · leitor público de páginas (reserva)"
    pesado = False

    def __init__(self, base: str = "https://r.jina.ai"):
        self.base = base.rstrip("/")

    def buscar(self, url: str, tempo_limite: float) -> Resposta:
        try:
            r = httpx.get(f"{self.base}/{url}", timeout=tempo_limite, follow_redirects=True)
        except httpx.TransportError as e:
            raise Passageiro(f"leitor público: {e}") from e
        resp = Resposta(url, r.status_code, r.content, r.headers.get("content-type", "text/plain"))
        resp.alertas.append("lido pelo leitor público (texto já convertido)")
        return resp
