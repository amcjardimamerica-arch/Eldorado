"""Funções de nó usadas só pelos testes."""
import os
from pathlib import Path


def _contar(parametros, nome):
    if parametros.get("contador"):
        with open(parametros["contador"], "a") as f:
            f.write(nome + "\n")


def contar(itens, parametros, contexto):
    _contar(parametros, contexto.no)
    return [dict(x, passou_por=x.get("passou_por", []) + [contexto.no]) for x in itens] or [{"passou_por": [contexto.no]}]


def falhar_vezes(itens, parametros, contexto):
    """Falha as primeiras N chamadas (contadas num arquivo), depois funciona."""
    p = Path(parametros["arquivo"])
    n = int(p.read_text()) if p.exists() else 0
    p.write_text(str(n + 1))
    if n < int(parametros["vezes"]):
        raise RuntimeError(f"falha provocada {n + 1}")
    return [{"ok": True, "chamada": n + 1}]


def sempre_falha(itens, parametros, contexto):
    raise ValueError("sempre falha")


def devolve_errado(itens, parametros, contexto):
    return "isto não é uma lista"


def derrubar_uma_vez(itens, parametros, contexto):
    """Derruba o processo inteiro na primeira chamada (queda real, sem limpeza); depois funciona."""
    _contar(parametros, contexto.no)
    marca = Path(parametros["marca"])
    if not marca.exists():
        marca.write_text("caiu")
        os._exit(1)
    return itens


def nao_deveria_rodar(itens, parametros, contexto):
    raise AssertionError("um nó com dados fixos não deve ser chamado")


def agente_pula_a(itens, parametros, contexto):
    """O nó de agente do Comandante (a fase 3): escolhe pular a etapa «a»."""
    return [{"__pular__": ["a"]}]
