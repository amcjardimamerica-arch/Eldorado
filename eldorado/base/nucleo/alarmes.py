"""Nenhum erro é engolido: todo erro vira um evento de alarme, e o erro continua subindo.

Lições do Eldorado0: o painel ficou congelado por quatro horas por um erro silenciado (27/09) e o Interceptador
ficou parado por cinco dias sem que ninguém visse (17/10 a 22/10).
"""
from __future__ import annotations

import traceback
from contextlib import contextmanager
from typing import Iterator

from loguru import logger

from .eventos import Diario, Evento, agora

GRAVIDADES = ("baixa", "media", "alta", "critica")


class Alarmes:
    def __init__(self, diario: Diario):
        self.diario = diario

    def abrir(self, gravidade: str, modulo: str, mensagem: str, rastro: str | None = None) -> Evento:
        if gravidade not in GRAVIDADES:
            raise ValueError(f"gravidade desconhecida: {gravidade}")
        logger.bind(modulo=modulo).log("CRITICAL" if gravidade == "critica" else "ERROR", mensagem)
        return self.diario.emitir("alarme.aberto", modulo, {
            "gravidade": gravidade, "modulo": modulo, "mensagem": mensagem[:2000],
            "rastro": (rastro or "")[-8000:] or None, "aberto_em": agora()})

    def fechar(self, alarme_id: int, modulo: str) -> Evento:
        return self.diario.emitir("alarme.fechado", modulo, {"id": alarme_id, "fechado_em": agora()})

    @contextmanager
    def vigiar(self, modulo: str, gravidade: str = "alta") -> Iterator[None]:
        """Envolve um trabalho: se der erro, abre o alarme com o rastro e deixa o erro subir."""
        try:
            yield
        except Exception as e:
            self.abrir(gravidade, modulo, f"{type(e).__name__}: {e}", traceback.format_exc())
            raise
