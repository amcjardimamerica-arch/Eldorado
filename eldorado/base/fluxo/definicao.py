"""A definição de um workflow (conceito do n8n, reescrito do zero para o Eldorado).

Um workflow é um arquivo TOML com nós e conexões:

    [workflow]
    id = "manutencao"
    descricao = "..."

    [[no]]
    id = "ler"                                   # identificador único no workflow
    tipo = "eldorado.base.fluxo.nos:passar"      # a função que executa o nó (modulo:funcao)
    tentativas = 3                               # de 1 a 3 (regra da plataforma)
    esperas_s = [2, 21600]                       # espera antes de cada nova tentativa; acima de 5 s, vira reagendamento pela fila
    parametros = { chave = "valor" }
    fixo = [ { a = 1 } ]                         # dados fixos de teste: o nó não roda, devolve isto (conceito "pinData")

    [[conexao]]
    de = "ler"
    para = "gravar"
    saida = "principal"                          # ou "erro": o caminho tomado quando o nó esgota as tentativas

A versão é a assinatura do conteúdo normalizado: a mesma definição tem sempre a mesma versão.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ESPERA_MAXIMA_EM_PROCESSO_S = 5      # esperas maiores não seguram a máquina: viram reagendamento


class WorkflowInvalido(Exception):
    pass


@dataclass(frozen=True)
class No:
    id: str
    tipo: str
    tentativas: int = 1
    esperas_s: tuple[float, ...] = ()
    parametros: dict[str, Any] = field(default_factory=dict)
    fixo: tuple[dict[str, Any], ...] | None = None
    pesado: bool = False             # o governador só deixa começar se houver folga para uma tarefa pesada


@dataclass(frozen=True)
class Conexao:
    de: str
    para: str
    saida: str = "principal"


@dataclass(frozen=True)
class Definicao:
    id: str
    descricao: str
    nos: tuple[No, ...]
    conexoes: tuple[Conexao, ...]
    versao: str

    def no(self, id: str) -> No:
        for n in self.nos:
            if n.id == id:
                return n
        raise KeyError(id)

    def entradas(self, id: str, saida: str = "principal") -> list[str]:
        return [c.de for c in self.conexoes if c.para == id and c.saida == saida]

    def saidas(self, id: str, saida: str = "principal") -> list[str]:
        return [c.para for c in self.conexoes if c.de == id and c.saida == saida]

    def ordem(self) -> list[str]:
        """Ordem topológica de todos os nós (as conexões de erro também ordenam)."""
        grau = {n.id: 0 for n in self.nos}
        for c in self.conexoes:
            grau[c.para] += 1
        fila = [n.id for n in self.nos if grau[n.id] == 0]
        ordem: list[str] = []
        while fila:
            atual = fila.pop(0)
            ordem.append(atual)
            for c in self.conexoes:
                if c.de == atual:
                    grau[c.para] -= 1
                    if grau[c.para] == 0:
                        fila.append(c.para)
        return ordem

    def como_json(self) -> str:
        return json.dumps({"id": self.id, "descricao": self.descricao,
                           "nos": [n.__dict__ | {"esperas_s": list(n.esperas_s), "fixo": list(n.fixo) if n.fixo is not None else None} for n in self.nos],
                           "conexoes": [c.__dict__ for c in self.conexoes]}, ensure_ascii=False, sort_keys=True)


def resolver(tipo: str) -> Callable[..., Any]:
    """Importa a função de um nó a partir de 'modulo:funcao'."""
    if ":" not in tipo:
        raise WorkflowInvalido(f"tipo de nó deve ser 'modulo:funcao': {tipo}")
    modulo, nome = tipo.split(":", 1)
    try:
        fn = getattr(importlib.import_module(modulo), nome)
    except (ImportError, AttributeError) as e:
        raise WorkflowInvalido(f"função do nó não encontrada: {tipo} ({e})") from e
    if not callable(fn):
        raise WorkflowInvalido(f"o tipo não é uma função: {tipo}")
    return fn


def de_dicionario(d: dict[str, Any], conferir_funcoes: bool = True) -> Definicao:
    w = d.get("workflow") or {}
    if not w.get("id"):
        raise WorkflowInvalido("o workflow precisa de [workflow] com id")
    nos: list[No] = []
    for bruto in d.get("no", []):
        desconhecidas = set(bruto) - {"id", "tipo", "tentativas", "esperas_s", "parametros", "fixo", "pesado"}
        if desconhecidas:
            raise WorkflowInvalido(f"nó {bruto.get('id')}: chaves desconhecidas: {', '.join(sorted(desconhecidas))}")
        if not bruto.get("id") or not bruto.get("tipo"):
            raise WorkflowInvalido("todo nó precisa de id e tipo")
        t = int(bruto.get("tentativas", 1))
        if not 1 <= t <= 3:
            raise WorkflowInvalido(f"nó {bruto['id']}: tentativas deve ser de 1 a 3 (recebido {t})")
        esperas = tuple(float(x) for x in bruto.get("esperas_s", []))
        if len(esperas) > t - 1 or any(x < 0 for x in esperas):
            raise WorkflowInvalido(f"nó {bruto['id']}: no máximo {t - 1} esperas, todas positivas")
        fixo = bruto.get("fixo")
        nos.append(No(id=bruto["id"], tipo=bruto["tipo"], tentativas=t, esperas_s=esperas, parametros=dict(bruto.get("parametros", {})),
                      fixo=tuple(fixo) if fixo is not None else None, pesado=bool(bruto.get("pesado", False))))
    if not nos:
        raise WorkflowInvalido("o workflow não tem nós")
    ids = [n.id for n in nos]
    repetidos = {i for i in ids if ids.count(i) > 1}
    if repetidos:
        raise WorkflowInvalido(f"nós repetidos: {', '.join(sorted(repetidos))}")
    conexoes: list[Conexao] = []
    for c in d.get("conexao", []):
        cx = Conexao(de=c.get("de", ""), para=c.get("para", ""), saida=c.get("saida", "principal"))
        if cx.de not in ids or cx.para not in ids:
            raise WorkflowInvalido(f"conexão para nó inexistente: {cx.de} → {cx.para}")
        if cx.saida not in ("principal", "erro"):
            raise WorkflowInvalido(f"saída desconhecida: {cx.saida}")
        if cx.de == cx.para:
            raise WorkflowInvalido(f"nó ligado a si mesmo: {cx.de}")
        conexoes.append(cx)
    provisoria = Definicao(id=w["id"], descricao=w.get("descricao", ""), nos=tuple(nos), conexoes=tuple(conexoes), versao="")
    if len(provisoria.ordem()) != len(nos):
        raise WorkflowInvalido("o workflow tem um ciclo")
    if conferir_funcoes:
        for n in nos:
            if n.fixo is None:
                resolver(n.tipo)
    versao = hashlib.sha256(provisoria.como_json().encode()).hexdigest()[:16]
    return Definicao(id=provisoria.id, descricao=provisoria.descricao, nos=provisoria.nos, conexoes=provisoria.conexoes, versao=versao)


def carregar(arquivo: str | Path, conferir_funcoes: bool = True) -> Definicao:
    p = Path(arquivo)
    try:
        dados = tomllib.loads(p.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise WorkflowInvalido(f"{p}: {e}") from e
    return de_dicionario(dados, conferir_funcoes)
