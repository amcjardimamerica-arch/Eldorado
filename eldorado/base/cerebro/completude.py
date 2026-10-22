"""A completude do dia: o que estava devido foi lido? O que precisa ser reacionado?

Uma única medida, definida por escrito: motores lidos ÷ motores devidos no plano (lição do Eldorado0, em que três
fontes mediam a mesma coisa com nomes parecidos e discordavam).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..nucleo.eventos import Diario


def calcular(diario: Diario, dia: str, devidos: list[str], lidos: list[str], alvos_na_janela: int = 0, alvos_lidos: int = 0) -> dict[str, Any]:
    faltam = sorted(set(devidos) - set(lidos))
    dados = {"dia": dia, "motores_devidos": len(set(devidos)), "motores_lidos": len(set(devidos) & set(lidos)),
             "alvos_na_janela": alvos_na_janela, "alvos_lidos": alvos_lidos, "completo": int(not faltam and alvos_lidos >= alvos_na_janela)}
    diario.emitir("cobertura.dia", "completude", dados)
    return dados | {"reacionar": faltam}


def no_completude(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Lê do diário desta execução o plano e as execuções dos motores (sem depender do gravador)."""
    devidos: list[str] = []
    lidos: list[str] = []
    for ev in contexto.diario.eventos():
        if ev.tipo == "plano.criado":
            devidos += [m["modulo"] for m in ev.dados.get("motores", [])]
        elif ev.tipo == "motor.execucao" and not ev.dados.get("erro"):
            lidos.append(ev.dados["motor"])
    dia = datetime.now(timezone.utc).date().isoformat()
    return [calcular(contexto.diario, dia, devidos, lidos)]
