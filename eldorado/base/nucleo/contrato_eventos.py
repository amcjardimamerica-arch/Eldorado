"""O CONTRATO DOS EVENTOS (07/11/2026) — o evento que o banco recusaria é barrado ONDE NASCE, não no gravador.

Por que existe: os alertas "evento recusado (medicao.registrada, …): CHECK constraint failed: nivel IN (…)" voltaram
três vezes. Em 29/10/2026 o medidor de memória emitiu nivel="etapa"; em 06/11/2026 o ciclo dos pilotos emitiu
nivel="aprendizado" (390 eventos recusados, 322 alarmes na Sala). Cada vez a correção foi pontual (um mapa no catálogo)
e o próximo módulo novo repetiu o erro, porque nada comparava o evento com o banco antes de ele chegar ao gravador:
os testes dos módulos usam tabelas falsas, sem as restrições do esquema real.

O que faz: monta, uma vez, os bancos em memória a partir do DDL real (biblioteca e Cérebro) e ensaia a escrita de cada
alvo do catálogo (CATALOGO) dentro de um SAVEPOINT desfeito em seguida. Só as violações do próprio dado contam
(os CHECK: o valor fora da lista); NOT NULL, chave estrangeira e gatilhos dependem de outras linhas e são do gravador.

Onde é usado:
- `testes/test_contrato_eventos.py` (a TRAVA) percorre o código e valida toda chamada `emitir("tipo", …, {…})` com
  valores literais contra o esquema real — o erro aparece no envio (fluxo de qualidade), antes de chegar à Sala. Foi
  ela que, rodada sobre o código de 07/11, apontou as duas linhas do ciclo dos pilotos.
- `Diario.emitir` confere cada evento (0,01 ms). Em produção o evento segue gravado (o dado não se perde; o catálogo
  conserta o legado conhecido) e a violação vai ao log com o MÓDULO que a emitiu — o que o alarme do gravador não diz.
  Com ELDORADO_CONTRATO_EVENTOS=estrito a violação é um erro na hora (para o módulo novo testado com o diário real).
"""
from __future__ import annotations

import os
import re
import sqlite3
import threading
from functools import lru_cache
from typing import Any

ESTRITO = "estrito"
_OPERACOES_DE_ESCRITA = {"inserir", "inserir_se_novo", "inserir_ou_atualizar"}
_trava = threading.Lock()


class EventoForaDoContrato(ValueError):
    """O evento tem um valor que o banco recusaria (um CHECK do esquema)."""


@lru_cache(maxsize=1)
def _bancos() -> dict[str, sqlite3.Connection]:
    from ...banco.biblioteca import esquema as bib
    from ...banco.cerebro_db import esquema as cer

    def montar(modulo) -> sqlite3.Connection:
        real = modulo.abrir(":memory:")   # o esquema completo, com todas as versões (o mesmo caminho do banco real)
        tabelas = real.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL "
                               "AND name NOT LIKE 'sqlite_%' AND sql NOT LIKE 'CREATE VIRTUAL%'").fetchall()
        real.close()
        # o ensaio guarda só as restrições do VALOR (os CHECK): o evento parcial (a atualização de uma linha que já existe,
        # o campo que o gravador completa) é legítimo, então NOT NULL, chaves estrangeiras e gatilhos ficam fora
        con = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
        for _nome, sql in tabelas:
            sql = re.sub(r"\bNOT NULL\b", "", sql)
            sql = re.sub(r"\bREFERENCES\s+\w+(\s*\([^)]*\))?", "", sql)
            try:
                con.execute(sql)
            except sqlite3.Error:
                pass
        return con

    livros = montar(bib)
    return {"biblioteca": livros, "especial": livros, "cerebro": montar(cer)}


@lru_cache(maxsize=None)
def _colunas(banco: str, tabela: str) -> tuple[str, ...]:
    con = _bancos().get(banco)
    if con is None:
        return ()
    return tuple(r[1] for r in con.execute(f'PRAGMA table_info("{tabela}")'))


def _relevante(erro: sqlite3.Error) -> bool:
    return "CHECK constraint failed" in str(erro)


def violacoes(tipo: str, dados: dict[str, Any]) -> list[str]:
    """As violações do contrato (vazio = o evento passa). Só os alvos de escrita direta são ensaiados."""
    from .eventos import CATALOGO

    erros: list[str] = []
    for alvo in CATALOGO.get(tipo, ()):
        if alvo.operacao not in _OPERACOES_DE_ESCRITA:
            continue
        cols = _colunas(alvo.banco, alvo.tabela)
        if not cols:
            continue
        # o dado COMO O MÓDULO O EMITIU: o mapa do catálogo só conserta o legado já gravado; o evento novo tem de nascer certo
        d = dict(dados)
        if alvo.mapa and not any(k in cols for k in d):
            try:
                d = alvo.mapa(dict(dados))   # o mapa que traduz o formato (outros nomes de campo)
            except Exception:  # noqa: BLE001 — o mapa com dado incompleto é assunto do gravador
                continue
        linha = {k: v for k, v in d.items() if k in cols and not isinstance(v, (dict, list))}
        if not linha:
            continue
        con = _bancos()[alvo.banco]
        sql = f'INSERT INTO "{alvo.tabela}" ({", ".join(chr(34) + c + chr(34) for c in linha)}) VALUES ({", ".join("?" * len(linha))})'
        with _trava:
            con.execute("SAVEPOINT contrato")
            try:
                con.execute(sql, tuple(linha.values()))
            except sqlite3.IntegrityError as e:
                if _relevante(e):
                    erros.append(f"{alvo.banco}.{alvo.tabela}: {e}")
            except sqlite3.Error:
                pass
            finally:
                con.execute("ROLLBACK TO contrato")
                con.execute("RELEASE contrato")
    return erros


def estrito() -> bool:
    return os.environ.get("ELDORADO_CONTRATO_EVENTOS", "").strip().lower() == ESTRITO


def conferir(tipo: str, modulo: str, dados: dict[str, Any]) -> list[str]:
    """Chamado por Diario.emitir. Estrito: levanta o erro com o módulo e a causa. Fora dele: devolve as violações."""
    try:
        erros = violacoes(tipo, dados)
    except Exception:  # noqa: BLE001 — a conferência nunca derruba a emissão
        return []
    if not erros:
        return erros
    msg = f"evento fora do contrato ({tipo}, módulo {modulo}): " + "; ".join(erros)
    if estrito():
        raise EventoForaDoContrato(msg)
    try:
        from loguru import logger

        logger.warning(msg)
    except Exception:  # noqa: BLE001
        pass
    return erros


def valores_permitidos(banco: str, tabela: str, coluna: str) -> set[str] | None:
    """Os valores de um CHECK (coluna IN (...)) do esquema real, lidos do banco montado (a mesma fonte do banco)."""
    con = _bancos().get(banco)
    if con is None:
        return None
    r = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabela,)).fetchone()
    if not r:
        return None
    c = re.search(r"CHECK \(" + re.escape(coluna) + r" IN \(([^)]*)\)\)", r[0])
    return {v.strip().strip("'") for v in c.group(1).split(",")} if c else None
