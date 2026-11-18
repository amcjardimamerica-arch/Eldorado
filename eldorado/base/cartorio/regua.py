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
# 17/11/2026 (R60, C-24): o mecanismo (programa regulado por lei, vigência contínua) fica fora da conta de abertas e de «sem
# data de fim»; é contado à parte
_ABERTA_BASE = f"{_VIVO} AND d.situacao_prazo = 'aberta' AND p.fase <> 'arquivo'"
_ABERTA = _ABERTA_BASE + " AND COALESCE(d.tipo_livro, '') <> 'mecanismo'"
_MECANISMO = f"{_VIVO} AND d.tipo_livro = 'mecanismo'"


def tem_tipo(bib: sqlite3.Connection) -> bool:
    """A Biblioteca já tem o tipo do livro (versão 16)? O banco antigo (os ensaios, a cópia) segue sem o filtro."""
    try:
        return "tipo_livro" in {r[1] for r in bib.execute("PRAGMA table_info(livro_dados)")}
    except sqlite3.Error:
        return False
_BASE = "FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id"
# 16/11/2026 (C-02): a condição ÚNICA de «prazo aberto», para a devolução do arquivo e a saída do Farol (as duas usavam
# critérios diferentes e o livro ia e voltava: saiu do Farol às 11:30 e voltou às 11:57)
PRAZO_ABERTO = "COALESCE(d.situacao_prazo, '') = 'aberta' AND (d.inscricao_fim IS NULL OR d.inscricao_fim >= date('now'))"


def regua(bib: sqlite3.Connection, fila_interceptador: int | None = None) -> dict[str, Any]:
    q = lambda sql, *a: bib.execute(sql, a).fetchone()[0] or 0  # noqa: E731
    _ABERTA = globals()["_ABERTA"] if tem_tipo(bib) else _ABERTA_BASE   # R60: o mecanismo fora, quando a coluna existe
    por_etapa = {f: n for f, n in bib.execute(f"SELECT p.fase, COUNT(*) {_BASE} WHERE {_ABERTA} GROUP BY 1")}
    abertas = sum(por_etapa.values())
    validadas = por_etapa.get("farol", 0)
    marcas = ",".join("?" * len(ESTEIRA))
    try:                                          # R60 (C-24): os mecanismos permanentes, à parte
        mecanismos = bib.execute(f"SELECT COUNT(*) {_BASE} WHERE {_MECANISMO}").fetchone()[0]
    except sqlite3.Error:
        mecanismos = 0
    return {
        "mecanismos": mecanismos,
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
