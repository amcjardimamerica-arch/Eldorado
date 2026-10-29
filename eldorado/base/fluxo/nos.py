"""Os nós próprios da plataforma, usados nos workflows de operação (manutenção, aplicação de eventos)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ...banco.biblioteca import esquema as biblioteca
from ...banco.cerebro_db import esquema as cerebro
from ..cerebro.governador import Governador, medidor_psutil, tamanho
from ..nucleo.eventos import ler
from ..nucleo.gravador import Gravador


def passar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    return itens


def abrir_bancos(dados: str | Path) -> dict:
    d = Path(dados)
    b = biblioteca.abrir(d / "biblioteca.db")                 # os livros e as empresas, no mesmo banco
    return {"biblioteca": b, "especial": b, "cerebro": cerebro.abrir(d / "cerebro.db")}


_APLICADO_DESDE: float | None = None


def aplicar_eventos(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Aplica todos os eventos da pasta aos bancos (idempotente). Recusas viram alarmes, aplicados pelo próprio gravador."""
    global _APLICADO_DESDE
    import time as _t

    # 29/10/2026: só o que é novo. A partida do ciclo aplica o histórico inteiro (eldorado aplicar); dentro da passagem,
    # cada etapa lê só os arquivos modificados desde a aplicação anterior (a primeira referência: a marca de início do
    # ciclo). O gravador ignora o que já foi aplicado, então ler um arquivo a mais nunca duplica; a margem de 60 s cobre
    # as escritas simultâneas.
    marca = Path(".inicio_ciclo")
    desde = _APLICADO_DESDE if _APLICADO_DESDE is not None else (marca.stat().st_mtime if marca.exists() else None)
    inicio = _t.time()
    bancos = abrir_bancos(parametros.get("dados", "dados"))
    try:
        r = Gravador(bancos).aplicar(ler(parametros.get("eventos", "eventos"), desde - 60 if desde is not None else None))
        _APLICADO_DESDE = inicio
    finally:
        for c in bancos.values():
            c.close()
    return [{"aplicados": r.aplicados, "repetidos": r.repetidos, "recusados": len(r.recusados)}]


def ler_maquina(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Lê a máquina e o tamanho de cada parte; grava a leitura (maquina.leitura) para o mostrador."""
    g = Governador(medidor_psutil(parametros.get("disco", ".")), diario=contexto.diario)
    dados = parametros.get("dados", "dados")
    tamanhos = {"biblioteca": tamanho(Path(dados) / "biblioteca.db"),
                "cerebro": tamanho(Path(dados) / "cerebro.db"), "eventos": tamanho(parametros.get("eventos", "eventos")),
                "motores": tamanho(parametros.get("motores", "dados/motores"))}
    return [g.registrar(tamanhos, g.paralelismo())]
