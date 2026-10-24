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
    arquivos_do_erro: tuple[str, ...] = ()   # os arquivos do sistema no rastro do erro (o ponto vermelho do mapa dos arquivos)


def medir(fn: Callable[..., Any], *args: Any, medir_memoria: bool = True, **kwargs: Any) -> Medida:
    rastreando = False
    if medir_memoria:
        rastreando = not tracemalloc.is_tracing()
        if rastreando:
            tracemalloc.start()
        tracemalloc.reset_peak()
    t0, c0 = time.perf_counter(), time.thread_time()
    ok, resultado, erro, arquivos = True, None, "", ()
    try:
        resultado = fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001 — a falha é registrada no recibo; quem chamou decide o que fazer
        ok, erro = False, f"{type(e).__name__}: {e}"
        import traceback
        rastro = [f.filename.replace("\\", "/") for f in traceback.extract_tb(e.__traceback__)]
        import re
        achados = (re.search(r"(eldorado/(?:base|motores|banco)/[^\s]+\.py)$", r) for r in rastro if "/site-packages/" not in r)
        arquivos = tuple(dict.fromkeys(a.group(1) for a in achados if a and not a.group(1).endswith("nucleo/recibo.py")))
    duracao = int((time.perf_counter() - t0) * 1000)
    cpu = int((time.thread_time() - c0) * 1000)
    pico = None
    if medir_memoria:
        pico = tracemalloc.get_traced_memory()[1] // 1024
        if rastreando:
            tracemalloc.stop()
    return Medida(ok, resultado, erro, duracao, cpu, pico, arquivos if not ok else ())


def emitir_recibo(diario: Diario, execucao: str | None, modulo: str, chamado_por: str, m: Medida) -> None:
    diario.emitir("chamada.recibo", "recibo", {"execucao": execucao, "modulo": modulo, "chamado_por": chamado_por, "ok": int(m.ok),
                                               "duracao_ms": m.duracao_ms, "cpu_ms": m.cpu_ms, "memoria_pico_kb": m.memoria_pico_kb,
                                               "erro": m.erro or None, "em": agora()})
