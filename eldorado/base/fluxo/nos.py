"""Os nós próprios da plataforma, usados nos workflows de operação (manutenção, aplicação de eventos)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ...banco.biblioteca import esquema as biblioteca
from ...banco.cerebro_db import esquema as cerebro
from ...banco.especial import esquema as especial
from ..cerebro.governador import Governador, medidor_psutil, tamanho
from ..nucleo.eventos import ler
from ..nucleo.gravador import Gravador


def passar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    return itens


def abrir_bancos(dados: str | Path) -> dict:
    d = Path(dados)
    return {"biblioteca": biblioteca.abrir(d / "biblioteca.db"), "especial": especial.abrir(d / "especial.db"),
            "cerebro": cerebro.abrir(d / "cerebro.db")}


def aplicar_eventos(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Aplica todos os eventos da pasta aos bancos (idempotente). Recusas viram alarmes, aplicados pelo próprio gravador."""
    bancos = abrir_bancos(parametros.get("dados", "dados"))
    try:
        r = Gravador(bancos).aplicar(ler(parametros.get("eventos", "eventos")))
    finally:
        for c in bancos.values():
            c.close()
    return [{"aplicados": r.aplicados, "repetidos": r.repetidos, "recusados": len(r.recusados)}]


def ler_maquina(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Lê a máquina e o tamanho de cada parte; grava a leitura (maquina.leitura) para o mostrador."""
    g = Governador(medidor_psutil(parametros.get("disco", ".")), diario=contexto.diario)
    dados = parametros.get("dados", "dados")
    tamanhos = {"biblioteca": tamanho(Path(dados) / "biblioteca.db"), "especial": tamanho(Path(dados) / "especial.db"),
                "cerebro": tamanho(Path(dados) / "cerebro.db"), "eventos": tamanho(parametros.get("eventos", "eventos")),
                "motores": tamanho(parametros.get("motores", "dados/motores"))}
    return [g.registrar(tamanhos, g.paralelismo())]
