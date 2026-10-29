"""O registro dos módulos ligados: confere o contrato antes de aceitar, e arquiva em vez de apagar.

Os módulos podem vir de uma configuração (`[[modulo]] classe = "pacote.modulo:Classe"`), para que um motor novo
entre escrevendo um arquivo, sem mudar a base.
"""
from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import Any

from .contratos import Modulo, verificar_contrato
from .eventos import Diario


class RegistroErro(Exception):
    pass


class Registro:
    def __init__(self, diario: Diario | None = None):
        self.diario = diario
        self._modulos: dict[str, Modulo] = {}
        self._arquivados: dict[str, Modulo] = {}

    def registrar(self, modulo: Modulo) -> str:
        d = verificar_contrato(modulo)
        if d.id in self._modulos:
            raise RegistroErro(f"módulo já registrado: {d.id}")
        self._modulos[d.id] = modulo
        self._arquivados.pop(d.id, None)
        self._emitir(modulo, ligado=1, arquivado=0)
        return d.id

    def arquivar(self, id: str) -> None:
        """Excluir é arquivar (conceito do Hermes): o módulo sai de uso, mas pode ser restaurado."""
        m = self._modulos.pop(id)
        self._arquivados[id] = m
        self._emitir(m, ligado=0, arquivado=1)

    def restaurar(self, id: str) -> None:
        self.registrar(self._arquivados[id])

    def obter(self, id: str) -> Modulo:
        try:
            return self._modulos[id]
        except KeyError as e:
            raise RegistroErro(f"módulo não registrado: {id}") from e

    def ids(self, tipo: str | None = None) -> list[str]:
        return sorted(i for i, m in self._modulos.items() if tipo is None or m.tipo == tipo)

    def _emitir(self, m: Modulo, ligado: int, arquivado: int) -> None:
        if not self.diario:
            return
        d = m.descrever()
        from .eventos import emitir_se_mudou  # 29/10/2026: só quando muda (eram 5.490 recadastros por dia)
        emitir_se_mudou(self.diario, "modulo.registrado", "registro", d.id, {"id": d.id, "tipo": d.tipo, "parte": d.parte, "componente": d.componente,
                                                              "finalidade": d.finalidade, "metrica": d.metrica, "ligado": ligado,
                                                              "arquivado": arquivado, "versao": d.versao})


def instanciar(classe: str, parametros: dict[str, Any] | None = None) -> Modulo:
    if ":" not in classe:
        raise RegistroErro(f"classe deve ser 'modulo:Classe': {classe}")
    mod, nome = classe.split(":", 1)
    try:
        cls = getattr(importlib.import_module(mod), nome)
    except (ImportError, AttributeError) as e:
        raise RegistroErro(f"classe não encontrada: {classe} ({e})") from e
    return cls(**(parametros or {}))


def carregar(arquivo: str | Path, diario: Diario | None = None) -> Registro:
    reg = Registro(diario)
    p = Path(arquivo)
    if p.exists():
        for m in tomllib.loads(p.read_text(encoding="utf-8")).get("modulo", []):
            if m.get("ligado", True):
                reg.registrar(instanciar(m["classe"], m.get("parametros")))
    return reg
