"""O Comandante comanda os pilotos (a etapa C5; a fase 4 do desenho, titular, 25/10/2026). Cada missão do Espião e cada
voo do Interceptador só começa com as quatro regras, todas obrigatórias:
  1. o intervalo: 3 segundos desde o fim da missão anterior daquele piloto;
  2. a janela de busca: o Espião tem rota de busca disponível; o Interceptador tem livro na fila;
  3. o acionamento do Comandante: ele escolhe a família da missão do Espião (pela política aprendida no Cérebro) e
     registra o livro do voo do Interceptador; cada autorização vira uma decisão com o motivo, avaliada pelo Aprendizado;
  4. os recursos da máquina: a carga (o maior entre processador e memória) até 85%; acima, a próxima missão espera.
Os dois pilotos voam em paralelo, cada um no seu fio e na sua vaga da IA."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INTERVALO_S = 3.0
CARGA_MAXIMA = 85.0
POLITICA_VALE_S = 600  # a política do Espião é refeita do Cérebro a cada 10 minutos

_trava = threading.Lock()
_fim: dict[str, float] = {}
_politica: dict[str, Any] = {}


def carga() -> float:
    """A carga da máquina: o maior entre o processador e a memória (em %)."""
    try:
        import psutil

        return max(psutil.cpu_percent(interval=0.5), psutil.virtual_memory().percent)
    except Exception:  # noqa: BLE001
        return 0.0


def pousou(piloto: str) -> None:
    with _trava:
        _fim[piloto] = time.monotonic()


def _janela_espiao(cer: sqlite3.Connection) -> bool:
    agora_ = datetime.now(timezone.utc).isoformat()
    rotas = dict(cer.execute("SELECT nome, descansa_ate FROM espiao_rota"))
    return not (len(rotas) >= 3 and all((v or "") > agora_ for v in rotas.values()))


def _familia(dados: Path, cer: sqlite3.Connection) -> tuple[str | None, float, int]:
    from .decidir import _estado_familias
    from .politica import Politica, contexto

    opcoes = _estado_familias(cer)
    if not opcoes:
        return None, 0.0, 0
    with _trava:
        p = _politica.get("espiao")
        if p is None or time.monotonic() - p["em"] > POLITICA_VALE_S or set(p["pol"].opcoes) != set(opcoes):
            pol = Politica("espiao", list(opcoes))
            pol.reaprender(cer)
            _politica["espiao"] = p = {"pol": pol, "em": time.monotonic()}
    ctx = contexto(datetime.now(timezone.utc), opcoes)
    alvo, prob = p["pol"].ordenar(ctx)[0]
    p["ultimo_ctx"] = (ctx, p["pol"].opcoes, prob)
    return alvo, prob, p["pol"].aprendidas


def autorizar(piloto: str, dados: Path, diario, parar: threading.Event, alvo: str | None = None, titulo: str = "") -> dict[str, Any] | None:
    """Espera as quatro regras e devolve a autorização (para o Espião, com a família escolhida); None se o sistema parar
    ou se não houver janela de busca."""
    while not parar.is_set():  # regra 1: o intervalo de 3 segundos
        with _trava:
            falta = INTERVALO_S - (time.monotonic() - _fim.get(piloto, 0.0))
        if falta <= 0:
            break
        parar.wait(falta)
    c = carga()
    while c > CARGA_MAXIMA and not parar.is_set():  # regra 4: a carga até 85%
        parar.wait(10)
        c = carga()
    if parar.is_set():
        return None
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    try:
        if piloto == "espiao":
            if not _janela_espiao(cer):  # regra 2: a janela de busca
                return None
            alvo, prob, aprendidas = _familia(dados, cer)  # regra 3: o Comandante escolhe a família
            if alvo is None:
                return None
            ctx, lista, _ = _politica["espiao"]["ultimo_ctx"]
            motivo = f"missão autorizada: carga {c:.0f}% (até 85%) · nota {prob:.2f} pela política aprendida com {aprendidas} decisões avaliadas"
            dec = {
                "etapa": "espiao",
                "acao": "voar a família",
                "alvo": alvo,
                "nota": round(prob, 4),
                "contexto": json.dumps({**ctx, "lista": lista, "prob": prob}, ensure_ascii=False),
            }
        else:
            if not alvo:  # regra 2: há livro na fila
                return None
            motivo = f"voo autorizado: carga {c:.0f}% (até 85%) · o livro na frente da fila (a nota da rede): {titulo[:120]}"
            dec = {"etapa": "interceptador", "acao": "investigar o livro", "alvo": alvo, "nota": None, "contexto": None}
    finally:
        cer.close()
    diario.emitir(
        "comandante.decidiu",
        "comandante",
        {
            "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "motivo": motivo,
            "politica": "vw-squarecb" if piloto == "espiao" else "fila da rede",
            **dec,
        },
    )
    return {"alvo": dec["alvo"], "carga": c, "motivo": motivo}
