"""O leitor universal de reserva (Apache Tika, extra 'universal'): mais de mil formatos, quando nenhum outro lê.

Pesado (exige Java): só entra quando instalado e ligado no registro. Seu uso deve ser raro; cada uso fica registrado.
"""
from __future__ import annotations

from .leitores import Leitura, Pagina, Registro, SemLeitor, sha256


class LeitorUniversal:
    nome = "universal (Apache Tika, reserva)"
    tipos = ()

    def __init__(self):
        try:
            from tika import parser
        except ImportError as e:
            raise SemLeitor("leitor universal desligado: instale o extra 'universal'") from e
        self._parser = parser

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        try:
            r = self._parser.from_buffer(conteudo)
        except Exception as e:  # noqa: BLE001 — a reserva que falha (o servidor do Tika) nunca derruba o motor (24/10/2026)
            raise SemLeitor(f"o leitor universal (Tika) falhou: {type(e).__name__}: {str(e)[:150]}") from e
        return Leitura(tipo="outro", leitor=self.nome, sha256=sha256(conteudo), paginas=[Pagina(1, r.get("content") or "")],
                       alertas=["lido pela reserva universal (uso deve ser raro)"])
