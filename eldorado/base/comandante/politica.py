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


# ---------------------------------------------------------------------------------------------------------------------
# R48 (titular, 08/11/2026 — o parecer da etapa 8): a AMOSTRAGEM DE THOMPSON (Beta-Bernoulli) no lugar do Vowpal Wabbit
# na coleta e no Espião. Pela reconstrução do histórico (25/10 a 08/11), as escolhas do VW renderam 0,331 por motor-dia,
# o mesmo que um sorteio (0,320) e a ordem fixa (0,326); a regra simples (os 8 de maior taxa histórica) rendeu 0,767.
# O VW registrava a probabilidade da opção (mediana 0,002), não a de ela entrar entre as escolhidas, e reaprendia cada
# decisão repetida dezenas de vezes (19 s por passagem). Aqui a crença de cada opção vem do RESULTADO REAL inteiro
# (todo motor lê todo dia: nenhum peso de importância é preciso) e a probabilidade registrada é a de inclusão.
class Thompson:
    """A crença Beta(1 + acertos, 1 + erros) de cada opção; a escolha sorteia uma taxa de cada uma e fica com as maiores."""

    SORTEIOS_INCLUSAO = 300

    def __init__(self, etapa: str, contagens: dict[str, tuple[int, int]], fator: dict[str, float] | None = None, semente: int | None = None):
        import random

        self.etapa = etapa
        self.contagens = {o: (max(0, int(a)), max(0, int(e))) for o, (a, e) in contagens.items()}
        self.fator = fator or {}
        self.opcoes = sorted(self.contagens)
        self.aprendidas = sum(a + e for a, e in self.contagens.values())
        self.rnd = random.Random(semente)

    def media(self, o: str) -> float:
        a, e = self.contagens[o]
        return (a + 1) / (a + e + 2) * self.fator.get(o, 1.0)

    def _sorteio(self) -> list[str]:
        t = {o: self.rnd.betavariate(a + 1, e + 1) * self.fator.get(o, 1.0) for o, (a, e) in self.contagens.items()}
        return sorted(t, key=lambda o: -t[o])

    def escolher(self, k: int) -> list[tuple[str, float]]:
        """As k escolhas, cada uma com a PROBABILIDADE DE INCLUSÃO (a fração de sorteios em que ela entra entre as k)."""
        if not self.opcoes:
            return []
        k = max(1, min(k, len(self.opcoes)))
        escolha = self._sorteio()[:k]
        conta = dict.fromkeys(self.opcoes, 0)
        for _ in range(self.SORTEIOS_INCLUSAO):
            for o in self._sorteio()[:k]:
                conta[o] += 1
        return [(o, max(conta[o], 1) / self.SORTEIOS_INCLUSAO) for o in escolha]


def contagens_coleta(bib: sqlite3.Connection, cer: sqlite3.Connection, motores: list[str], ate: str) -> dict[str, tuple[int, int]]:
    """Para cada motor: os dias LIDOS com achado aceito (acertos) e sem (erros), até a véspera (ate = AAAA-MM-DD, exclusive)."""
    lidos: dict[str, set[str]] = {m: set() for m in motores}
    for m, d in cer.execute("SELECT DISTINCT motor, substr(inicio, 1, 10) FROM execucao_motor WHERE substr(inicio, 1, 10) < ?", (ate,)):
        if m in lidos:
            lidos[m].add(d)
    com: dict[str, set[str]] = {m: set() for m in motores}
    for m, d in bib.execute("SELECT DISTINCT motor, substr(encontrado_em, 1, 10) FROM achado WHERE decisao = 'aceito' AND substr(encontrado_em, 1, 10) < ?",
                            (ate,)):
        if m in com:
            com[m].add(d)
    # o dia com achado aceito conta como lido (o achado prova a leitura, mesmo sem o registro da execução)
    return {m: (len(com[m]), len(lidos[m] - com[m])) for m in motores}


def contagens_espiao(bib: sqlite3.Connection, cer: sqlite3.Connection, familias: list[str]) -> dict[str, tuple[int, int]]:
    """Para cada família do Espião: as missões que trouxeram achado ACEITO na Biblioteca (acerto) contra as demais (erro).
    O «achado» da missão (o que passou no crivo) não serve: a internacional_espanhol teve 7.006 missões «com achado» e
    deu 3 oportunidades reais em 11.904 missões."""
    missoes = dict(cer.execute("SELECT familia, COUNT(*) FROM espiao_missao GROUP BY familia").fetchall())
    aceitos: dict[str, int] = {}
    try:
        for fam, n in bib.execute("SELECT json_extract(dados, '$.familia'), COUNT(*) FROM achado WHERE motor = 'espiao' AND decisao = 'aceito' "
                                  "GROUP BY 1"):
            if fam:
                aceitos[fam] = n
    except sqlite3.Error:
        pass
    return {f: (min(aceitos.get(f, 0), missoes.get(f, 0)), max(0, missoes.get(f, 0) - aceitos.get(f, 0))) for f in familias}
