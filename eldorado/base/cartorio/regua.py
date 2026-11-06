"""A régua única (R46, titular, 05/11/2026; parecer de teste do site, 06/11/2026): UMA função conta as oportunidades para
todas as telas — o Início, a Bússola, a Sala de controle, o Cartório e o Farol leem daqui, e só daqui.

ABERTA        = o livro vivo com o prazo de inscrição aberto (situacao_prazo = 'aberta'), fora do arquivo
VALIDADA      = a aberta no Farol (passou pela verificação)
EM VERIFICAÇÃO= a aberta numa etapa da esteira do Cartório (validadas + em verificação = abertas)
COM DATA      = a aberta com a data-limite de inscrição; SEM DATA = fluxo contínuo, permanente por lei, ciclo da LOA
ESTEIRA       = todos os livros vivos nas etapas da esteira (com ou sem prazo aberto): o que o Cartório tem na linha
ARQUIVO       = os livros vivos no arquivo
"""
from __future__ import annotations

import sqlite3
from typing import Any

ESTEIRA = ("recepcao", "certificacao", "preparacao", "validacao", "analise externa")
_VIVO = "l.situacao NOT IN ('excluido', 'unido')"
_ABERTA = f"{_VIVO} AND d.situacao_prazo = 'aberta' AND p.fase <> 'arquivo'"
_BASE = "FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id"


def regua(bib: sqlite3.Connection, fila_interceptador: int | None = None) -> dict[str, Any]:
    q = lambda sql, *a: bib.execute(sql, a).fetchone()[0] or 0  # noqa: E731
    por_etapa = {f: n for f, n in bib.execute(f"SELECT p.fase, COUNT(*) {_BASE} WHERE {_ABERTA} GROUP BY 1")}
    abertas = sum(por_etapa.values())
    validadas = por_etapa.get("farol", 0)
    marcas = ",".join("?" * len(ESTEIRA))
    return {
        "abertas": abertas,
        "validadas": validadas,
        "em_verificacao": abertas - validadas,
        "por_etapa": por_etapa,
        "com_data": q(f"SELECT COUNT(*) {_BASE} WHERE {_ABERTA} AND d.inscricao_fim IS NOT NULL AND d.inscricao_fim <> ''"),
        "validadas_com_data": q(f"SELECT COUNT(*) {_BASE} WHERE {_ABERTA} AND p.fase = 'farol' AND d.inscricao_fim IS NOT NULL "
                                f"AND d.inscricao_fim <> ''"),
        "estrelas": {e: n for e, n in bib.execute(f"SELECT COALESCE(l.estrela, 'sem'), COUNT(*) {_BASE} WHERE {_ABERTA} GROUP BY 1")},
        "esteira": q(f"SELECT COUNT(*) FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE {_VIVO} AND p.fase IN ({marcas})",
                     *ESTEIRA),
        "arquivo": q(f"SELECT COUNT(*) FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE {_VIVO} AND p.fase = 'arquivo'"),
        "farol_total": q(f"SELECT COUNT(*) FROM livro l JOIN passaporte p ON p.livro_id = l.id WHERE {_VIVO} AND p.fase = 'farol'"),
        "fila_interceptador": fila_interceptador,
        "regra": "R46: aberta = prazo aberto fora do arquivo; validada = a aberta no Farol; em verificação = a aberta na esteira",
    }
