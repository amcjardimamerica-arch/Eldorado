"""Forma 1: a metabusca, com rotas de reserva: SearXNG (serviço próprio) → ddgs → Marginalia.

Rota que falha ou bate no limite DESCANSA (o "descanso dos buscadores" do Espião do Eldorado0) e a próxima assume.
O SearXNG e o Marginalia passam pela escada de acesso; o ddgs é uma biblioteca de metabusca com o seu próprio cliente
(extra 'metabusca'), por isso é a rota do meio, não a principal.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from urllib.parse import quote

from .pistas import Buscar, Pista


@dataclass
class Metabusca:
    buscar: Buscar
    searxng: str | None = None                     # o serviço próprio (ex.: http://localhost:8888)
    marginalia: str | None = "https://api.marginalia.nu/public"
    usar_ddgs: bool = True
    descanso_s: int = 3600
    _descansando: dict[str, float] = field(default_factory=dict)
    relogio: callable = time.monotonic

    def _livre(self, rota: str) -> bool:
        return self.relogio() >= self._descansando.get(rota, 0)

    def _descansar(self, rota: str) -> None:
        self._descansando[rota] = self.relogio() + self.descanso_s

    def consultar(self, termos: str, limite: int = 20) -> tuple[list[Pista], list[str]]:
        """As pistas e o relatório de cada rota tentada."""
        relato: list[str] = []
        for rota, fn in (("searxng", self._searxng), ("ddgs", self._ddgs), ("marginalia", self._marginalia)):
            if not self._livre(rota):
                relato.append(f"{rota}: descansando")
                continue
            try:
                pistas = fn(termos, limite)
            except _Desligada as e:
                relato.append(f"{rota}: {e}")
                continue
            except Exception as e:  # noqa: BLE001 — falha ou limite: a rota descansa e a próxima assume (registrado)
                self._descansar(rota)
                relato.append(f"{rota}: falhou ({type(e).__name__}); descansa {self.descanso_s // 60} min")
                continue
            relato.append(f"{rota}: {len(pistas)} pista(s)")
            return pistas[:limite], relato
        return [], relato

    def _searxng(self, termos: str, limite: int) -> list[Pista]:
        if not self.searxng:
            raise _Desligada("serviço próprio não configurado")
        d = json.loads(self.buscar(f"{self.searxng.rstrip('/')}/search?q={quote(termos)}&format=json&language=pt-BR").conteudo)
        return [Pista(titulo=r.get("title", ""), link=r["url"], origem="metabusca (SearXNG)", resumo=r.get("content"), data=r.get("publishedDate"))
                for r in d.get("results", []) if r.get("url")]

    def _ddgs(self, termos: str, limite: int) -> list[Pista]:
        if not self.usar_ddgs:
            raise _Desligada("desligado")
        try:
            from ddgs import DDGS
        except ImportError as e:
            raise _Desligada("não instalado (extra 'metabusca')") from e
        return [Pista(titulo=r.get("title", ""), link=r["href"], origem="metabusca (ddgs)", resumo=r.get("body"))
                for r in DDGS().text(termos, region="br-pt", max_results=limite) if r.get("href")]

    def _marginalia(self, termos: str, limite: int) -> list[Pista]:
        if not self.marginalia:
            raise _Desligada("desligado")
        d = json.loads(self.buscar(f"{self.marginalia.rstrip('/')}/search/{quote(termos)}?count={limite}").conteudo)
        return [Pista(titulo=r.get("title", ""), link=r["url"], origem="metabusca (Marginalia)", resumo=r.get("description"))
                for r in d.get("results", []) if r.get("url")]


class _Desligada(Exception):
    pass
