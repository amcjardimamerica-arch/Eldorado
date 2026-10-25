"""Os pilotos de forma permanente (titular, 25/10/2026: "execute eles de forma permanente, da forma que foram desenvolvidos
para funcionar").

Como foram desenvolvidos (o Eldorado0 e o plano): voos contínuos e independentes — o Interceptador consumindo a fila
livro após livro, sem parar; o Espião fazendo missões em sequência, com o descanso das rotas. Como rodavam: nós dentro da
passagem, depois da coleta e do Cartório, com 5 e 3 minutos de orçamento (poucos minutos por passagem, e nada quando a
passagem era interrompida antes deles).

Agora os dois voam em segundo plano durante todo o ciclo (o funcionamento permanente os liga). O que trazem fica na fila
de entrega; os nós deles, na passagem seguinte, entregam o que os voos trouxeram à Pertinência e ao Cartório. A carga
do servidor é respeitada (acima de 90% de memória, esperam). Falha de um voo vira registro; o voo seguinte segue (R18).
"""
from __future__ import annotations

import queue
import threading
import time
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ATIVO = threading.Event()                      # os voos permanentes estão ligados (os nós só entregam)
ENTREGAS: dict[str, queue.Queue] = {"interceptador": queue.Queue(), "espiao": queue.Queue()}
SITUACAO: dict[str, dict[str, Any]] = {"interceptador": {}, "espiao": {}}


def entregas(piloto: str) -> list[dict[str, Any]]:
    """O que os voos trouxeram desde a última passagem (o nó do piloto devolve isto)."""
    saida = []
    while True:
        try:
            saida.append(ENTREGAS[piloto].get_nowait())
        except queue.Empty:
            return saida


def _carga_alta() -> bool:
    try:
        import psutil
        return psutil.virtual_memory().percent >= 90
    except Exception:  # noqa: BLE001
        return False


def sinal(diario, piloto: str, motivo: str) -> None:
    """O sinal de vida do piloto (25/10/2026): os quadros do site leem o "ligado/agora" por ele, não pelo último resultado."""
    diario.emitir("medicao.registrada", f"piloto:{piloto}", {"marcador": f"piloto:{piloto}", "nivel": "componente",
                                                              "em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "ponto": "v",
                                                              "valor": 1, "motivo": motivo[:300]})


def _contexto(dados: Path, diario):
    from .encaminhamento import _contexto_pilotos
    return _contexto_pilotos({"dados": str(dados), "modulos": "config/modulos.toml", "intervalo_s": 1.0}, SimpleNamespace(diario=diario))


def voar_interceptador(dados: Path, diario, parar: threading.Event, tempo_livro_s: float = 180, pausa_s: float = 5) -> None:
    """O Interceptador: um livro por vez, pelo plano de voo, sem parar (a fila é refeita a cada volta)."""
    from ...motores.descoberta.metabusca import Metabusca
    from ...motores.pilotos.interceptador import Interceptador, fila
    from ..nucleo.ia import IA
    from .encaminhamento import Encaminhamento
    from .rede import rede_atual
    while not parar.is_set():
        try:
            dados_, con, escada, registro = _contexto(dados, diario)
            try:
                ia, rede = IA(), rede_atual(dados_)
                mb = Metabusca(buscar=escada.buscar)

                def buscar_links(q: str, mb=mb) -> list[str]:
                    try:
                        return [p.link for p in mb.consultar(q, limite=10)[0]]
                    except Exception:  # noqa: BLE001
                        return []
                enc = Encaminhamento(con, diario, registro, Interceptador(con, diario, escada, metabusca=buscar_links,
                                                                         ia=ia if ia.disponivel() else None), rede)
                livros = enc.ordenar(fila(con, date.today().isoformat()))[:30]      # uma volta: até 30 livros, depois refaz a fila
                for lv in livros:
                    if parar.is_set():
                        break
                    while _carga_alta() and not parar.is_set():
                        parar.wait(30)
                    SITUACAO["interceptador"] = {"livro": lv.id, "titulo": lv.titulo, "desde": time.time()}
                    sinal(diario, "interceptador", f"em voo: {lv.titulo}")
                    quem, achados = enc.encaminhar(lv, time.monotonic() + tempo_livro_s)
                    for a in (achados if isinstance(achados, list) else [achados] if achados else []):
                        ENTREGAS["interceptador"].put(a)
                    parar.wait(pausa_s)
                if not livros:
                    sinal(diario, "interceptador", "aguardando: a fila de livros está vazia")
                    parar.wait(300)                                   # a fila vazia: espera a próxima passagem trazer livros
            finally:
                con.close()
        except Exception as e:  # noqa: BLE001 — um voo que falha vira registro; o seguinte segue
            diario.emitir("alarme.aberto", "piloto:interceptador", {"gravidade": "media", "modulo": "piloto:interceptador",
                                                                    "mensagem": f"o voo permanente do Interceptador falhou: {type(e).__name__}: {str(e)[:300]}",
                                                                    "aberto_em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())})
            parar.wait(120)


def voar_espiao(dados: Path, diario, parar: threading.Event, orcamento_s: float = 150, pausa_s: float = 120) -> None:
    """O Espião: missão após missão (as rotas descansam sozinhas quando falham), com uma pausa entre os voos."""
    from .encaminhamento import Encaminhamento
    from .pilotos import missoes
    while not parar.is_set():
        try:
            while _carga_alta() and not parar.is_set():
                parar.wait(30)
            dados_, con, escada, registro = _contexto(dados, diario)
            try:
                SITUACAO["espiao"] = {"desde": time.time()}
                sinal(diario, "espiao", "em voo: missão de busca")
                achados, _ = missoes(dados_, con, escada, True, orcamento_s, diario=diario)
                enc = Encaminhamento(con, diario, registro, None)
                for a in achados:
                    ENTREGAS["espiao"].put(enc._entregar(a, "espiao"))
                sinal(diario, "espiao", f"pousou: {len(achados)} achado(s)")
            finally:
                con.close()
        except Exception as e:  # noqa: BLE001
            diario.emitir("alarme.aberto", "piloto:espiao", {"gravidade": "media", "modulo": "piloto:espiao",
                                                             "mensagem": f"o voo permanente do Espião falhou: {type(e).__name__}: {str(e)[:300]}",
                                                             "aberto_em": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())})
        parar.wait(pausa_s)


def ligar(dados: Path, eventos: Path, parar: threading.Event) -> list[threading.Thread]:
    """Liga os dois voos permanentes (o funcionamento permanente chama no início do ciclo)."""
    from ..nucleo.eventos import Diario
    ATIVO.set()
    fios = [threading.Thread(target=voar_interceptador, args=(dados, Diario(eventos, "interceptador"), parar), daemon=True, name="interceptador"),
            threading.Thread(target=voar_espiao, args=(dados, Diario(eventos, "espiao"), parar), daemon=True, name="espiao")]
    for f in fios:
        f.start()
    return fios
