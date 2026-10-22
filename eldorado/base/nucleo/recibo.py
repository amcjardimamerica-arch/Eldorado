"""A medição de uma chamada: tempo, processador e memória de pico, e se deu certo.

Usada pelo executor (cada nó) e pela Regência (cada motor acionado). O recibo é a base do ponto de cada arquivo
na Sala e do custo de cada módulo no governador.
"""
from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from typing import Any, Callable

from .eventos import Diario, agora


@dataclass
class Medida:
    ok: bool
    resultado: Any
    erro: str
    duracao_ms: int
    cpu_ms: int
    memoria_pico_kb: int | None


def medir(fn: Callable[..., Any], *args: Any, medir_memoria: bool = True, **kwargs: Any) -> Medida:
    rastreando = False
    if medir_memoria:
        rastreando = not tracemalloc.is_tracing()
        if rastreando:
            tracemalloc.start()
        tracemalloc.reset_peak()
    t0, c0 = time.perf_counter(), time.process_time()
    ok, resultado, erro = True, None, ""
    try:
        resultado = fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001 — a falha é registrada no recibo; quem chamou decide o que fazer
        ok, erro = False, f"{type(e).__name__}: {e}"
    duracao = int((time.perf_counter() - t0) * 1000)
    cpu = int((time.process_time() - c0) * 1000)
    pico = None
    if medir_memoria:
        pico = tracemalloc.get_traced_memory()[1] // 1024
        if rastreando:
            tracemalloc.stop()
    return Medida(ok, resultado, erro, duracao, cpu, pico)


def emitir_recibo(diario: Diario, execucao: str | None, modulo: str, chamado_por: str, m: Medida) -> None:
    diario.emitir("chamada.recibo", "recibo", {"execucao": execucao, "modulo": modulo, "chamado_por": chamado_por, "ok": int(m.ok),
                                               "duracao_ms": m.duracao_ms, "cpu_ms": m.cpu_ms, "memoria_pico_kb": m.memoria_pico_kb,
                                               "erro": m.erro or None, "em": agora()})
