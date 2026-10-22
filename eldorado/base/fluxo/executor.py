"""O executor durável dos workflows.

- Percorre os nós na ordem das conexões. Cada chamada é medida (tempo, processador e memória de pico) e vira um recibo.
- Tentativas por nó (até 3). Esperas curtas acontecem no processo; esperas longas (acima de 5 s, como as de 6 h e
  24 h) viram reagendamento: a execução para como "reagendada" e a fila a retoma na hora certa.
- Esgotadas as tentativas, segue pela saída de erro, se houver (a devolução do livro); se não houver, a execução
  falha e um alarme é aberto.
- Os itens carregam a linhagem (o livro e o achado de origem) de nó em nó.
- Durável: cada passo é gravado no diário (com sincronização no disco) antes do próximo. Ao retomar, o executor relê
  o diário e pula o que já foi feito, inclusive as tentativas já gastas. O diário é a verdade; o gravador aplica
  depois os mesmos eventos ao banco do Cérebro.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..nucleo.alarmes import Alarmes
from ..nucleo.eventos import Diario, agora
from ..nucleo.recibo import emitir_recibo, medir
from .definicao import ESPERA_MAXIMA_EM_PROCESSO_S, Definicao, No, resolver

LINHAGEM = "_linhagem"
ENTRADA = "_entrada"


@dataclass
class Contexto:
    """O que cada nó recebe além dos itens: quem está rodando e onde gravar eventos."""
    execucao: str
    no: str
    tentativa: int
    diario: Diario
    alarmes: Alarmes


@dataclass
class Resultado:
    execucao: str
    estado: str                                   # 'concluida', 'falhou', 'reagendada'
    saidas: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    reagendar_em_s: float | None = None
    no_reagendado: str | None = None
    erro: str | None = None


class _Reagendar(Exception):
    def __init__(self, no: str, espera: float):
        self.no, self.espera = no, espera


class Executor:
    def __init__(self, definicao: Definicao, pasta_eventos: str | Path, medir_memoria: bool = True,
                 dormir: Callable[[float], None] = time.sleep, funcoes: dict[str, Callable[..., Any]] | None = None):
        self.d = definicao
        self.pasta = Path(pasta_eventos)
        self.medir_memoria = medir_memoria
        self.dormir = dormir
        self._funcoes = dict(funcoes or {})

    # ------------------------------------------------------------------ execução

    def executar(self, entrada: list[dict[str, Any]] | None = None, execucao: str | None = None) -> Resultado:
        diario = Diario(self.pasta, execucao)
        alarmes = Alarmes(diario)
        estado = _Estado.do_diario(diario, diario.execucao)
        if estado.concluida:
            return Resultado(diario.execucao, estado.concluida, estado.saidas)
        if estado.iniciada:
            diario.emitir("execucao.retomada", "executor", {"id": diario.execucao, "estado": "retomada"})
            entrada = estado.entrada
        else:
            diario.emitir("workflow.versao", "executor", {"id": self.d.id, "versao": self.d.versao, "definicao": self.d.como_json(), "criado_em": agora()})
            diario.emitir("execucao.iniciada", "executor", {"id": diario.execucao, "workflow": self.d.id, "versao": self.d.versao,
                                                            "inicio": agora(), "estado": "rodando"})
            entrada = list(entrada or [])
            estado.registrar_passo(diario, ENTRADA, "entrada", [], entrada)
        try:
            for no_id in self.d.ordem():
                if no_id in estado.saidas or no_id in estado.desviados:
                    continue
                itens = self._entradas(no_id, estado, entrada)
                if itens is None:
                    continue                                   # nó não ativado nesta execução
                self._rodar_no(self.d.no(no_id), itens, estado, diario, alarmes)
        except _Reagendar as r:
            diario.emitir("execucao.concluida", "executor", {"id": diario.execucao, "estado": "aguardando"} | {"fim": None})
            return Resultado(diario.execucao, "reagendada", estado.saidas, r.espera, r.no)
        except _Falhou as f:
            diario.emitir("execucao.concluida", "executor", {"id": diario.execucao, "fim": agora(), "estado": "falhou"})
            return Resultado(diario.execucao, "falhou", estado.saidas, erro=str(f))
        diario.emitir("execucao.concluida", "executor", {"id": diario.execucao, "fim": agora(), "estado": "concluida"})
        return Resultado(diario.execucao, "concluida", estado.saidas)

    def retomar(self, execucao: str) -> Resultado:
        return self.executar(execucao=execucao)

    # ------------------------------------------------------------------ nós

    def _entradas(self, no_id: str, estado: "_Estado", entrada: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
        principais = self.d.entradas(no_id, "principal")
        de_erro = self.d.entradas(no_id, "erro")
        so_ordem = self.d.entradas(no_id, "ordem")
        if not principais and not de_erro:
            if so_ordem:                                  # só ordem: roda depois dos indicados, sem receber dados
                return [] if any(p in estado.saidas or p in estado.desviados for p in so_ordem) else None
            return list(entrada)
        itens: list[dict[str, Any]] = []
        ativado = False
        for p in principais:
            if p in estado.saidas:
                ativado = True
                itens.extend(estado.saidas[p])
        for p in de_erro:
            if p in estado.desviados:
                ativado = True
                itens.extend(estado.desviados[p])
        return itens if ativado else None

    def _rodar_no(self, no: No, itens: list[dict[str, Any]], estado: "_Estado", diario: Diario, alarmes: Alarmes) -> None:
        if no.fixo is not None:
            estado.registrar_passo(diario, no.id, "concluido", itens, [dict(x) for x in no.fixo])
            return
        fn = self._funcoes.get(no.tipo) or resolver(no.tipo)
        tentativa = estado.tentativas_gastas.get(no.id, 0)
        ultimo_erro = ""
        while tentativa < no.tentativas:
            tentativa += 1
            ctx = Contexto(diario.execucao, no.id, tentativa, diario, alarmes)
            ok, saida, erro = self._chamar(fn, no, itens, ctx, diario)
            if ok:
                estado.registrar_passo(diario, no.id, "concluido", itens, self._herdar_linhagem(itens, saida))
                return
            ultimo_erro = erro
            estado.tentativas_gastas[no.id] = tentativa
            if tentativa < no.tentativas:
                espera = no.esperas_s[tentativa - 1] if tentativa - 1 < len(no.esperas_s) else 0
                if espera > ESPERA_MAXIMA_EM_PROCESSO_S:
                    estado.registrar_passo(diario, no.id, "reagendado", itens, [{"proxima_tentativa": tentativa + 1, "espera_s": espera}])
                    raise _Reagendar(no.id, espera)
                if espera:
                    self.dormir(espera)
        desvio = self.d.saidas(no.id, "erro")
        item_erro = [{"erro": ultimo_erro, "no": no.id, "itens": itens}]
        if desvio:
            estado.registrar_passo(diario, no.id, "desviado", itens, item_erro)
            return
        estado.registrar_passo(diario, no.id, "falhou", itens, item_erro)
        alarmes.abrir("alta", f"workflow:{self.d.id}", f"o nó {no.id} falhou depois de {no.tentativas} tentativa(s): {ultimo_erro}")
        raise _Falhou(f"{no.id}: {ultimo_erro}")

    def _chamar(self, fn: Callable[..., Any], no: No, itens: list[dict[str, Any]], ctx: Contexto, diario: Diario) -> tuple[bool, list[dict[str, Any]], str]:
        def chamada():
            r = fn([dict(x) for x in itens], dict(no.parametros), ctx)
            saida = [] if r is None else r
            if not isinstance(saida, list) or not all(isinstance(x, dict) for x in saida):
                raise TypeError("o nó deve devolver uma lista de dicionários")
            return saida
        m = medir(chamada, medir_memoria=self.medir_memoria)
        emitir_recibo(diario, ctx.execucao, no.tipo, no.id, m)
        return m.ok, (m.resultado or []), m.erro

    @staticmethod
    def _herdar_linhagem(entrada: list[dict[str, Any]], saida: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Conceito do n8n (pairedItem): com um único item de entrada, toda saída herda a linhagem dele."""
        if len(entrada) == 1 and LINHAGEM in entrada[0]:
            return [x if LINHAGEM in x else {**x, LINHAGEM: entrada[0][LINHAGEM]} for x in saida]
        return saida


class _Falhou(Exception):
    pass


@dataclass
class _Estado:
    """O estado de uma execução, reconstruído do diário."""
    iniciada: bool = False
    concluida: str | None = None
    entrada: list[dict[str, Any]] = field(default_factory=list)
    saidas: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    desviados: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    tentativas_gastas: dict[str, int] = field(default_factory=dict)
    ultimo_passo: int = -1

    @classmethod
    def do_diario(cls, diario: Diario, execucao: str) -> "_Estado":
        e = cls()
        for ev in diario.eventos():
            d = ev.dados
            if ev.tipo == "execucao.iniciada":
                e.iniciada = True
            elif ev.tipo == "execucao.concluida" and d.get("estado") in ("concluida", "falhou"):
                e.concluida = d["estado"]
            elif ev.tipo == "execucao.passo" and d.get("execucao") == execucao:
                e.ultimo_passo = max(e.ultimo_passo, d["passo"])
                if d["no"] == ENTRADA:
                    e.entrada = d["saida"]
                elif d["estado"] == "concluido":
                    e.saidas[d["no"]] = d["saida"]
                elif d["estado"] == "desviado":
                    e.desviados[d["no"]] = d["saida"]
            elif ev.tipo == "chamada.recibo" and d.get("execucao") == execucao and not d.get("ok"):
                e.tentativas_gastas[d["chamado_por"]] = e.tentativas_gastas.get(d["chamado_por"], 0) + 1
        return e

    def registrar_passo(self, diario: Diario, no: str, estado: str, entrada: list[dict[str, Any]], saida: list[dict[str, Any]]) -> None:
        self.ultimo_passo += 1
        diario.emitir("execucao.passo", "executor", {"execucao": diario.execucao, "passo": self.ultimo_passo, "no": no, "estado": estado,
                                                      "entrada": entrada, "saida": saida, "em": agora()})
        if no == ENTRADA:
            self.entrada = saida
        elif estado == "concluido":
            self.saidas[no] = saida
        elif estado == "desviado":
            self.desviados[no] = saida
