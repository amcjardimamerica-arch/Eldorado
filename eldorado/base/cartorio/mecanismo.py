"""17/11/2026 (titular, R60 — C-24): o livro de MECANISMO. Programa que tem lei e norma próprias (lei de incentivo, destinação
de bens, como a doação de mercadorias apreendidas pela Receita Federal, que dura o ano inteiro quando não há eleição) tem livro
próprio: não há edital, a informação vem toda da lei, e um edital novo não muda o livro.

A cada passagem: o livro ganha o tipo «mecanismo» pelo catálogo de ouro (a validação no edital, 15 e 16/11) e pelos programas
conhecidos; os livros que apontam para a mesma lei são listados para a titular (nada é unido sem ela)."""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from typing import Any

# os programas regulados por lei que o catálogo já conhece (R44) — a doação de mercadorias apreendidas da Receita Federal
PROGRAMAS_CONHECIDOS = ("captacao-208",)
LEI_NO_TEXTO = re.compile(r"(?i)\b(lei|decreto|portaria|instru[çc][ãa]o normativa)\s*(?:complementar\s*)?(?:federal\s*|estadual\s*|municipal\s*)?"
                          r"(?:rfb\s*)?n?[º°o.]?\s*([\d.]+\s*/\s*\d{2,4}|[\d.]{3,})")


def eh_mecanismo(catalogo_ouro: str | None) -> bool:
    try:
        return (json.loads(catalogo_ouro or "{}") or {}).get("tipo") == "mecanismo"
    except (ValueError, TypeError):
        return False


def classificar(con: sqlite3.Connection, diario) -> dict[str, Any]:
    """Grava o tipo «mecanismo» nos livros vivos que ainda não o têm; lista as famílias de livros que apontam para a mesma lei."""
    try:
        linhas = con.execute("SELECT l.id, l.titulo, d.catalogo_ouro, d.tipo_livro FROM livro l JOIN livro_dados d ON d.livro_id = l.id "
                             "WHERE l.situacao NOT IN ('excluido', 'unido')").fetchall()
    except sqlite3.Error:                          # a Biblioteca antes da versão 16
        return {"mecanismos": 0}
    novos, mecs, por_lei = 0, [], defaultdict(list)
    for lid, titulo, cat, tipo in linhas:
        mec = eh_mecanismo(cat) or lid in PROGRAMAS_CONHECIDOS
        if not mec:
            continue
        mecs.append(lid)
        if tipo != "mecanismo":
            diario.emitir("livro.tipo", "cartorio", {"livro_id": lid, "tipo_livro": "mecanismo"})
            novos += 1
        m = LEI_NO_TEXTO.search(titulo or "")
        if m:
            por_lei[f"{m.group(1).lower()} {re.sub(r'\\s+', '', m.group(2))}"].append(lid)
    familias = {lei: ids for lei, ids in por_lei.items() if len(ids) > 1}
    return {"mecanismos": len(mecs), "novos": novos, "mesma_lei_para_a_titular": familias}
