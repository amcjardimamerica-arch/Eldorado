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
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INTERVALO_S = 3.0
CARGA_MAXIMA = 85.0
POLITICA_VALE_S = 600  # a política do Espião é refeita do Cérebro a cada 10 minutos

_trava = threading.Lock()
_fim: dict[str, float] = {}
_politica: dict[str, Any] = {}


def _parametros(dados: Path) -> tuple[float, float]:
    """A carga máxima e o intervalo, do Arquivo do Cérebro (os parâmetros do Comandante); a regra da titular é a reserva."""
    with _trava:
        p = _politica.get("parametros")
        if p and time.monotonic() - p["em"] < 60:
            return p["v"]
    v = (CARGA_MAXIMA, INTERVALO_S)
    try:
        from .parametros import valor

        cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
        try:
            v = (float(valor(cer, "pilotos", "carga_maxima", CARGA_MAXIMA)), float(valor(cer, "pilotos", "intervalo_s", INTERVALO_S)))
        finally:
            cer.close()
    except (sqlite3.Error, ValueError, TypeError):
        pass
    with _trava:
        _politica["parametros"] = {"v": v, "em": time.monotonic()}
    return v


REINICIAR = threading.Event()  # o Comandante pede o reinício do ciclo (a memória não cede): termina, grava e religa
MEMORIA_REINICIO, REINICIO_S, PRESSAO_S = 92.0, 15 * 60, 10 * 60
_pressao: dict[str, float | None] = {"carga_desde": None, "memoria_desde": None}


def carga() -> float:
    """A carga da máquina: o maior entre o processador e a memória (em %). Cada leitura alimenta a pressão que o Comandante
    mede (26/10/2026: a memória presa em 96% parou o sistema por 3 horas, todos esperando a regra dos 85%)."""
    try:
        import psutil

        from ..cerebro.governador import cpu_sem_ia

        mem = psutil.virtual_memory().percent
        c = max(cpu_sem_ia(0.5) * 100, mem)   # o processador sem a IA (26/10/2026: um voo bloqueava o outro)
    except Exception:  # noqa: BLE001
        return 0.0
    agora = time.monotonic()
    with _trava:
        _pressao["carga_desde"] = (_pressao["carga_desde"] or agora) if c > CARGA_MAXIMA else None
        _pressao["memoria_desde"] = (_pressao["memoria_desde"] or agora) if mem >= MEMORIA_REINICIO else None
        if _pressao["memoria_desde"] and agora - _pressao["memoria_desde"] >= REINICIO_S:
            REINICIAR.set()
    return c


_ocio: dict[str, float | None] = {"desde": None}


_amostras: "deque[tuple[float, float]]" = deque()


ALVO_BAIXO, ALVO_ALTO = 0.78, 0.92        # a faixa em torno de 85% do processador TOTAL (com a IA)
MEM_SEGURA, MEM_EMERGENCIA = 0.86, 0.90   # a memória: acima de 86%, fecha uma vaga; acima de 90%, volta a 1
# 30/10/2026: 1 voo com a IA (um pedido de cada vez) e 2 preparando o material do próximo (antes 4, o dobro das 2 vagas
# da IA; e antes 8, quando os voos achavam o material e ficavam sem a vez da IA)
VAGAS_MAX = 3
_ctrl = {"vagas": 1, "ultimo_ajuste": 0.0, "cpu": None, "mem": None}


def vagas_por_ociosidade() -> int:
    """29/10/2026 (titular, a regra do sistema: coordenar as missões com a disponibilidade, mantendo o processador perto de
    85%). Um controlador: a cada minuto, pela média do último minuto do processador TOTAL (com a IA) e pela memória,
    abre uma vaga se o processador está abaixo de 78%, fecha uma acima de 92%, mantém entre os dois; a memória acima de 86%
    fecha uma vaga e acima de 90% volta a 1. Antes: o processador SEM a IA abaixo de 45% e a memória abaixo de 78% —
    o processador ficava entre 0% e 29% e, com a memória em 80%, o Interceptador ficava com 1 vaga por horas."""
    try:
        import psutil

        from ..cerebro.governador import cpu_total
        total, mem = cpu_total(0.3), psutil.virtual_memory().percent / 100
    except Exception:  # noqa: BLE001
        return _ctrl["vagas"]
    agora_m = time.monotonic()
    with _trava:
        _amostras.append((agora_m, total))
        while _amostras and agora_m - _amostras[0][0] > 60:
            _amostras.popleft()
        media = sum(v for _, v in _amostras) / len(_amostras)
        _ctrl["cpu"], _ctrl["mem"] = media, mem
        v = _ctrl["vagas"]
        if mem >= MEM_EMERGENCIA:
            v = 1
        elif agora_m - _ctrl["ultimo_ajuste"] >= 60 and len(_amostras) >= 3:
            if media > ALVO_ALTO or mem > MEM_SEGURA:
                v = max(1, v - 1)
            elif media < ALVO_BAIXO:
                v = min(VAGAS_MAX, v + 1)
            _ctrl["ultimo_ajuste"] = agora_m
        _ctrl["vagas"] = v
    return v


def ceder_para_a_passagem() -> None:
    """30/10/2026: a passagem tem prioridade: adiada pelo governador, os voos do Interceptador voltam a 1 vaga (o
    controlador volta a abrir as vagas, uma por minuto, quando o processador tiver folga)."""
    with _trava:
        _ctrl["vagas"] = 1
        _ctrl["ultimo_ajuste"] = time.monotonic()


def estado_vagas() -> dict:
    """As vagas liberadas agora, o processador total (média do minuto) e a memória: para o quadro e a Sala."""
    with _trava:
        return dict(_ctrl)


def pressao() -> float:
    """Há quantos segundos a carga está acima de 85% sem parar (0 se não está)."""
    with _trava:
        d = _pressao["carga_desde"]
    return time.monotonic() - d if d else 0.0


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
    # 27/10/2026: SORTEIA pela distribuição (como desenhado); pegar sempre a primeira fez 399 de 421 missões irem a uma
    # família só, quase todas sem achado. A família cansada (10 missões seguidas sem achado) descansa 30 minutos.
    import random
    agora_m = time.monotonic()
    lista = [(a, pr) for a, pr in p["pol"].ordenar(ctx) if _cansaco.get(a, {}).get("descansa_ate", 0) <= agora_m] or p["pol"].ordenar(ctx)
    pesos = [max(pr, 0.0) for _a, pr in lista]
    alvo, prob = random.choices(lista, weights=pesos)[0] if sum(pesos) > 0 else random.choice(lista)
    p["ultimo_ctx"] = (ctx, p["pol"].opcoes, prob)
    return alvo, prob, p["pol"].aprendidas


_cansaco: dict[str, dict] = {}
CANSACO_MISSOES, DESCANSO_S = 10, 30 * 60


def registrar_missao(familia: str | None, achados: int) -> None:
    """O resultado da missão do Espião: 10 seguidas sem achado deixam a família 30 minutos de fora."""
    if not familia:
        return
    with _trava:
        c = _cansaco.setdefault(familia, {"zeros": 0, "descansa_ate": 0.0})
        c["zeros"] = 0 if achados else c["zeros"] + 1
        if c["zeros"] >= CANSACO_MISSOES:
            c["zeros"], c["descansa_ate"] = 0, time.monotonic() + DESCANSO_S


def autorizar(piloto: str, dados: Path, diario, parar: threading.Event, alvo: str | None = None, titulo: str = "") -> dict[str, Any] | None:
    """Espera as quatro regras e devolve a autorização (para o Espião, com a família escolhida); None se o sistema parar
    ou se não houver janela de busca."""
    # a carga máxima e o intervalo vêm do Arquivo do Cérebro (os parâmetros do Comandante); a regra da titular é a reserva
    maxima, intervalo = _parametros(dados) if (dados / "cerebro.db").exists() else (CARGA_MAXIMA, INTERVALO_S)
    intervalo = min(intervalo, INTERVALO_S)  # (os testes encurtam o intervalo; na produção os dois são 3 s)
    while not parar.is_set():  # regra 1: o intervalo de 3 segundos
        with _trava:
            falta = intervalo - (time.monotonic() - _fim.get(piloto, 0.0))
        if falta <= 0:
            break
        parar.wait(falta)
    c = carga()
    avisou = False
    while c > maxima and not parar.is_set():  # regra 4: a carga até 85%
        parar.wait(10)
        c = carga()
        if pressao() >= PRESSAO_S and not avisou:  # 10 minutos sem ceder: a limpeza e o alarme (os voos caem para 2)
            import gc

            gc.collect()
            diario.emitir(
                "alarme.aberto",
                "comandante",
                {
                    "gravidade": "alta",
                    "modulo": "comandante:carga",
                    "aberto_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "mensagem": f"a carga está acima de {maxima:.0f}% há mais de 10 minutos ({c:.0f}%): os voos do Interceptador caem para 2; "
                    f"com a memória acima de {MEMORIA_REINICIO:.0f}% por 15 minutos, o ciclo é reiniciado (termina, grava e religa)",
                },
            )
            avisou = True
        if REINICIAR.is_set():
            return None
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
            motivo = (
                f"missão autorizada: carga {c:.0f}% (até {maxima:.0f}%) · nota {prob:.2f} pela política aprendida com {aprendidas} decisões avaliadas"
            )
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
            motivo = f"voo autorizado: carga {c:.0f}% (até {maxima:.0f}%) · o livro na frente da fila (a nota da rede): {titulo[:120]}"
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
