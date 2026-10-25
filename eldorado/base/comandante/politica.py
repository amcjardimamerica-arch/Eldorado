"""A política de decisão do Comandante: o Vowpal Wabbit (o bandido contextual SquareCB), eleito no estudo (92% a 96% do
ótimo, contra cerca de 50% da ordem fixa). O modelo nasce do Arquivo do Cérebro: a cada passagem, relê as decisões já
avaliadas e reaprende (sem arquivo à parte: o Cérebro é a memória do Comandante)."""

from __future__ import annotations

import json
import math
import re
import sqlite3
from datetime import datetime
from typing import Any


def _nome(a: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", a)


class Politica:
    def __init__(self, etapa: str, opcoes: list[str]):
        import vowpalwabbit

        self.etapa, self.opcoes = etapa, sorted(set(opcoes))
        self.vw = vowpalwabbit.Workspace("--cb_explore_adf --squarecb --quiet --random_seed 7", enable_logging=False)
        self.aprendidas = 0

    def _exemplo(self, ctx: dict[str, Any], opcoes: list[str], rotulo: tuple[str, float, float] | None = None) -> list[str]:
        linhas = [f"shared |s hs:{ctx['hs']:.3f} hc:{ctx['hc']:.3f} dia_{ctx['dia']}"]
        for o in opcoes:
            c = ctx["opcoes"].get(o, {})
            linha = f"|o op_{_nome(o)} desde:{min(1.0, (c.get('dias_sem') or 30) / 30):.3f} taxa:{c.get('taxa', 0.5):.3f}"
            if rotulo and o == rotulo[0]:
                linha = f"0:{-rotulo[1]}:{max(rotulo[2], 1e-3)} " + linha
            linhas.append(linha)
        return linhas

    def reaprender(self, cer: sqlite3.Connection) -> int:
        """Relê, em ordem, as decisões avaliadas desta etapa (a recompensa e a probabilidade com que foram tomadas)."""
        try:
            linhas = cer.execute(
                "SELECT alvo, recompensa, contexto FROM comandante_decisao WHERE etapa = ? AND recompensa IS NOT NULL ORDER BY em", (self.etapa,)
            ).fetchall()
        except sqlite3.Error:
            return 0
        for alvo, rec, ctx_json in linhas:
            try:
                ctx = json.loads(ctx_json)
            except (TypeError, ValueError):
                continue
            opcoes = [o for o in ctx.get("lista", self.opcoes)]
            if alvo in opcoes:
                self.vw.learn(self._exemplo(ctx, opcoes, (alvo, float(rec), float(ctx.get("prob", 0.1)))))
                self.aprendidas += 1
        return self.aprendidas

    def ordenar(self, ctx: dict[str, Any], rnd=None) -> list[tuple[str, float]]:
        """A ordem das opções SORTEADA pela distribuição da política (a exploração do bandido contextual: sem ela, a mesma
        escolha se repete e nada se aprende). Cada opção leva a probabilidade com que foi escolhida (o aprendizado a usa)."""
        import random

        rnd = rnd or random.Random()
        pmf = self.vw.predict(self._exemplo(ctx, self.opcoes))
        restantes, saida = list(zip(self.opcoes, pmf, strict=False)), []
        while restantes:
            total = sum(max(p, 1e-9) for _o, p in restantes)
            alvo, acum = rnd.random() * total, 0.0
            for i, (o, p) in enumerate(restantes):
                acum += max(p, 1e-9)
                if acum >= alvo:
                    saida.append((o, p))
                    restantes.pop(i)
                    break
        return saida


def contexto(agora: datetime, opcoes: dict[str, dict]) -> dict[str, Any]:
    h = agora.hour + agora.minute / 60
    return {"hs": math.sin(2 * math.pi * h / 24), "hc": math.cos(2 * math.pi * h / 24), "dia": agora.weekday(), "opcoes": opcoes}
