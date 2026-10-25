"""A rede neural vigia os sites ORIGINAIS dos livros (titular, 23/10/2026): com o histórico do livro, ele tem um site de
divulgação e um site original (a origem confirmada). A rede escolhe os livros com origem confirmada (primeiro os
arquivados, que esperam a próxima edição; depois os em trabalho e no Farol) e pede ao motor de cada livro o mapa do
site original; o motor entrega as URLs novas que têm a ver com o livro, e elas entram pela Pertinência e pelo Cartório
(no livro arquivado, é a nova oportunidade, que volta pela recepção).
"""
from __future__ import annotations

import re
import sqlite3
import time
from typing import Any

NUMERO = re.compile(r"n[º°o.]*\s*0*(\d{1,4})\s*[/_-]\s*(20\d\d)", re.I)
ORDEM_DAS_FASES = ("arquivo", "preparacao", "analise externa", "validacao", "farol", "certificacao")


def livros_com_origem(con: sqlite3.Connection, limite: int = 200) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    linhas = con.execute("SELECT l.id, l.titulo, l.orgao, l.link_oficial, p.fase FROM livro l JOIN livro_dados d ON d.livro_id = l.id "
                         "JOIN passaporte p ON p.livro_id = l.id WHERE d.origem = 'confirmado' AND l.link_oficial IS NOT NULL "
                         "AND l.situacao NOT IN ('excluido', 'unido') AND l.id NOT IN (SELECT livro_unido FROM uniao)").fetchall()
    livros = []
    for r in sorted(linhas, key=lambda r: (ORDEM_DAS_FASES.index(r["fase"]) if r["fase"] in ORDEM_DAS_FASES else 9, r["id"]))[:limite]:
        m = NUMERO.search(r["titulo"] or "")
        livros.append({"id": r["id"], "titulo": r["titulo"], "orgao": r["orgao"], "link_oficial": r["link_oficial"], "fase": r["fase"],
                       "numero": f"{int(m.group(1))}/{m.group(2)}" if m else None})
    return livros


def vigiar(con: sqlite3.Connection, registro, orcamento_s: float = 120, diario=None) -> tuple[list, dict[str, int]]:
    """Os mapas dos sites originais, pelo motor de cada livro, até o orçamento de tempo do batimento."""
    from .livros_motores import motores_do_livro
    inicio, achados, conta = time.monotonic(), [], {"livros": 0, "novidades": 0, "sem_motor": 0}
    vistos: set[tuple[str, str]] = set()
    for lv in livros_com_origem(con):
        if time.monotonic() - inicio >= orcamento_s:
            break
        dominio = (lv["link_oficial"].split("//", 1)[-1].split("/", 1)[0])
        motores = [m for m in motores_do_livro(con, lv["id"]) if m in registro.ids() and hasattr(registro.obter(m), "vigiar_original")]
        if not motores:
            conta["sem_motor"] += 1
            continue
        if (motores[0], dominio) in vistos:                          # o mesmo domínio, no mesmo motor, uma vez por batimento
            continue
        vistos.add((motores[0], dominio))
        conta["livros"] += 1
        motor = registro.obter(motores[0])
        if diario is not None and hasattr(motor, "estado"):          # o que o motor aprende vai ao Cérebro pelo diário
            motor.estado.diario = diario
        novos = motor.vigiar_original(lv)
        conta["novidades"] += len(novos)
        achados += novos
    return achados, conta
