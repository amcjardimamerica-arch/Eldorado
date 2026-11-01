"""Os livros migrados do Eldorado0 (titular, 01/11/2026): dado histórico, sem nova releitura nem avaliação — exceto os que
estão com o prazo de inscrição aberto (são oportunidades atuais). Os prefixos dos identificadores da migração."""
from __future__ import annotations

PREFIXOS = ("op-", "nova-", "captacao-", "curadoria-", "espalhado-")


def e_migrado(livro_id: str | None) -> bool:
    return bool(livro_id) and str(livro_id).startswith(PREFIXOS)


def sql_migrado(col: str = "l.id") -> str:
    """A cláusula SQL: o livro é migrado."""
    return "(" + " OR ".join(f"{col} LIKE '{p}%'" for p in PREFIXOS) + ")"
