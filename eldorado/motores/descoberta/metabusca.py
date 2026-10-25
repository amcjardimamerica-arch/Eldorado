"""Forma 1: a metabusca, o canivete de busca: SearXNG (serviço próprio), o DDGS por seis motores (Bing, Brave, Mojeek,
Yahoo, Google, DuckDuckGo), o Marginalia, o Querido Diário e o PNCP; os resultados se somam.

Rota que falha ou bate no limite DESCANSA (o "descanso dos buscadores" do Espião do Eldorado0) e a próxima assume.
O SearXNG e o Marginalia passam pela escada de acesso; o ddgs é uma biblioteca de metabusca com o seu próprio cliente
(extra 'metabusca'), por isso é a rota do meio, não a principal.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from .pistas import Buscar, Pista


@dataclass
class Metabusca:
    buscar: Buscar
    searxng: str | None = None                     # o serviço próprio (ex.: http://localhost:8888)

    def __post_init__(self):
        import os
        self.searxng = self.searxng or os.environ.get("ELDORADO_SEARXNG")   # o SearXNG do próprio fluxo (scripts/instalar.sh)
    marginalia: str | None = "https://api.marginalia.nu/public"
    usar_ddgs: bool = True
    descanso_s: int = 3600
    _descansando: dict[str, float] = field(default_factory=dict)
    relogio: callable = time.monotonic

    def _livre(self, rota: str) -> bool:
        return self.relogio() >= self._descansando.get(rota, 0)

    def _descansar(self, rota: str) -> None:
        self._descansando[rota] = self.relogio() + self.descanso_s

    # o canivete de busca (titular, 25/10/2026: o Espião e o Interceptador dependiam do DuckDuckGo): rotas independentes,
    # cada uma descansa sozinha quando falha; os resultados de várias rotas se SOMAM (sem repetir links) até o limite
    MOTORES_DDGS = ("bing", "brave", "mojeek", "yahoo", "google", "duckduckgo")

    def rotas(self, termos: str) -> list[tuple[str, Any]]:
        r = [("searxng", self._searxng)]
        r += [(f"ddgs-{b}", (lambda t, lim, b=b: self._ddgs(t, lim, b))) for b in self.MOTORES_DDGS]
        r.append(("marginalia", self._marginalia))
        if "site:" not in termos:                       # as rotas temáticas de editais (não aceitam a restrição a um site)
            r += [("querido-diario", self._querido_diario), ("pncp", self._pncp)]
        return r

    def consultar(self, termos: str, limite: int = 20) -> tuple[list[Pista], list[str]]:
        """As pistas (somadas de várias rotas, sem repetir links) e o relatório de cada rota tentada."""
        relato: list[str] = []
        vistas: dict[str, Pista] = {}
        for rota, fn in self.rotas(termos):
            if len(vistas) >= limite:
                break
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
            novas = 0
            for p in pistas:
                k = p.link.split("#")[0].rstrip("/")
                if k not in vistas:
                    vistas[k] = p
                    novas += 1
            relato.append(f"{rota}: {len(pistas)} pista(s), {novas} nova(s)")
        return list(vistas.values())[:limite], relato

    def _searxng(self, termos: str, limite: int) -> list[Pista]:
        if not self.searxng:
            raise _Desligada("serviço próprio não configurado")
        d = json.loads(self.buscar(f"{self.searxng.rstrip('/')}/search?q={quote(termos)}&format=json&language=pt-BR").conteudo)
        return [Pista(titulo=r.get("title", ""), link=r["url"], origem="metabusca (SearXNG)", resumo=r.get("content"), data=r.get("publishedDate"))
                for r in d.get("results", []) if r.get("url")]

    def _ddgs(self, termos: str, limite: int, motor: str = "auto") -> list[Pista]:
        if not self.usar_ddgs:
            raise _Desligada("desligado")
        try:
            from ddgs import DDGS
        except ImportError as e:
            raise _Desligada("não instalado (extra 'metabusca')") from e
        return [Pista(titulo=r.get("title", ""), link=r["href"], origem=f"metabusca ({motor})", resumo=r.get("body"))
                for r in DDGS().text(termos, region="br-pt", max_results=limite, backend=motor) if r.get("href")]

    def _querido_diario(self, termos: str, limite: int) -> list[Pista]:
        """O texto integral dos diários oficiais municipais (a API do Querido Diário)."""
        d = json.loads(self.buscar(f"https://queridodiario.ok.org.br/api/gazettes?querystring={quote(termos)}&size={min(limite, 10)}"
                                   "&excerpt_size=400&number_of_excerpts=1&sort_by=descending_date").conteudo)
        return [Pista(titulo=f"Diário oficial de {g.get('territory_name', '')} ({g.get('date', '')})", link=g.get("url") or g.get("txt_url"),
                      origem="metabusca (Querido Diário)", data=g.get("date"), resumo=" ".join(g.get("excerpts") or [])[:600])
                for g in d.get("gazettes", []) if g.get("url") or g.get("txt_url")]

    def _pncp(self, termos: str, limite: int) -> list[Pista]:
        """Os editais públicos com proposta aberta (a busca do PNCP)."""
        d = json.loads(self.buscar(f"https://pncp.gov.br/api/search/?q={quote(termos)}&tipos_documento=edital&ordenacao=-data"
                                   f"&pagina=1&tam_pagina={min(limite, 10)}&status=recebendo_proposta").conteudo)
        return [Pista(titulo=i.get("title") or i.get("description", "")[:120], link="https://pncp.gov.br/app/" + str(i.get("item_url", "")).lstrip("/"),
                      origem="metabusca (PNCP)", data=(i.get("data_publicacao_pncp") or "")[:10] or None, resumo=i.get("description"))
                for i in d.get("items", []) if i.get("item_url")]

    def _marginalia(self, termos: str, limite: int) -> list[Pista]:
        if not self.marginalia:
            raise _Desligada("desligado")
        d = json.loads(self.buscar(f"{self.marginalia.rstrip('/')}/search/{quote(termos)}?count={limite}").conteudo)
        return [Pista(titulo=r.get("title", ""), link=r["url"], origem="metabusca (Marginalia)", resumo=r.get("description"))
                for r in d.get("results", []) if r.get("url")]


class _Desligada(Exception):
    pass
