"""A fila de tarefas (Huey sobre SQLite): executa workflows, sob o governador e a pausa do sistema.

- Antes de começar, consulta o governador; sem folga, a tarefa se adia sozinha (sem segurar a máquina).
- Com o sistema pausado (arquivo de pausa), a tarefa também se adia.
- Execução que volta "reagendada" (espera longa entre tentativas: 6 h, 24 h) tem a retomada agendada para a hora certa.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from huey import SqliteHuey

from ..cerebro.governador import Governador
from . import definicao
from .executor import Executor


class Fila:
    def __init__(self, arquivo: str | Path, pasta_eventos: str | Path, governador: Governador | None = None,
                 arquivo_pausa: str | Path | None = None, imediata: bool = False, adiamento_s: int = 60):
        Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
        self.huey = SqliteHuey("eldorado", filename=str(arquivo), immediate=imediata, utc=True)
        self.pasta_eventos = Path(pasta_eventos)
        self.governador = governador
        self.arquivo_pausa = Path(arquivo_pausa) if arquivo_pausa else None
        self.adiamento_s = adiamento_s
        self._tarefa = self.huey.task(name="executar_workflow")(self._executar)

    def pausado(self) -> bool:
        return bool(self.arquivo_pausa and self.arquivo_pausa.exists())

    def _executar(self, workflow: str, execucao: str | None = None, entrada: list[dict[str, Any]] | None = None,
                  modulo: str | None = None, peso: str = "leve") -> dict[str, Any]:
        args = (workflow, execucao, entrada, modulo, peso)
        if self.pausado():
            self._tarefa.schedule(args, delay=self.adiamento_s)
            return {"estado": "adiada", "motivo": "sistema pausado"}
        if self.governador and not self.governador.pode_iniciar(modulo, peso):
            self._tarefa.schedule(args, delay=self.adiamento_s)
            return {"estado": "adiada", "motivo": self.governador.motivo()}
        r = Executor(definicao.carregar(workflow), self.pasta_eventos).executar(entrada, execucao)
        if r.estado == "reagendada":
            self._tarefa.schedule((workflow, r.execucao, None, modulo, peso), delay=int(r.reagendar_em_s or self.adiamento_s))
        return {"estado": r.estado, "execucao": r.execucao, "erro": r.erro}

    def enfileirar(self, workflow: str | Path, entrada: list[dict[str, Any]] | None = None, modulo: str | None = None, peso: str = "leve"):
        return self._tarefa(str(workflow), None, entrada, modulo, peso)

    def agendar(self, workflow: str | Path, atraso_s: int, entrada: list[dict[str, Any]] | None = None, modulo: str | None = None, peso: str = "leve"):
        return self._tarefa.schedule((str(workflow), None, entrada, modulo, peso), delay=atraso_s)

    def agendadas(self) -> list:
        return self.huey.scheduled()

    def pendentes(self) -> int:
        return self.huey.pending_count()
