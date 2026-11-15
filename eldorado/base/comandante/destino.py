"""K1 (R57, titular, 14/11/2026): a recompensa pelo DESTINO FINAL do livro — o Comandante é medido pelo que o livro virou, e
não por ter sido aceito (65% dos livros criados acabavam descartados; «aceito» não é «útil»). Farol = 1; arquivo com edição
anterior guardada = 0,7; arquivo sem edição = 0,5; unido = 0,2; descartado = 0. O livro ainda na esteira não tem destino e
fica fora da conta; a recompensa é revista a cada passagem, quando o destino muda."""
from __future__ import annotations

import json
import sqlite3

RECOMPENSA = {"farol": 1.0, "arquivo_com_edicao": 0.7, "arquivo": 0.5, "unido": 0.2, "descartado": 0.0}


def destinos(bib: sqlite3.Connection) -> dict[str, float]:
    """Livro → a recompensa do destino final (só os livros que já têm destino)."""
    saida: dict[str, float] = {}
    try:
        edicoes = {}
        for lid, datas in bib.execute("SELECT livro_id, datas_encontrado FROM previsao"):
            try:
                n = len(json.loads(datas)) if datas and str(datas).startswith("[") else len([d for d in str(datas or "").split(",") if d.strip()])
            except ValueError:
                n = 0
            edicoes[lid] = n
    except sqlite3.Error:
        edicoes = {}
    try:
        linhas = bib.execute("SELECT l.id, l.situacao, p.fase FROM livro l LEFT JOIN passaporte p ON p.livro_id = l.id").fetchall()
    except sqlite3.Error:                                # o banco sem livros (os ensaios): nenhum destino
        return saida
    for lid, situacao, fase in linhas:
        if situacao == "excluido":
            saida[lid] = RECOMPENSA["descartado"]
        elif situacao == "unido":
            saida[lid] = RECOMPENSA["unido"]
        elif fase == "farol" or situacao == "transferido ao farol":
            saida[lid] = RECOMPENSA["farol"]
        elif fase == "arquivo":
            saida[lid] = RECOMPENSA["arquivo_com_edicao"] if edicoes.get(lid, 0) >= 1 else RECOMPENSA["arquivo"]
    return saida
