"""A ESTEIRA DO CARTÓRIO (o Comandante organiza as 5 etapas; titular, 02/11/2026 — R37).

O defeito: a preparação (etapa 3) só sai por um achado novo — o Interceptador ou o motor trazem informação, o Cartório
valida (etapa 4) e decide: Farol, arquivo ou análise externa. Mas a fila do Interceptador só aceita o livro que ainda tem
o que buscar; o livro que já está completo (ou sem nada que o Interceptador possa buscar) nunca recebe achado novo e
fica parado na preparação para sempre, inflando a etapa (livros de ouro com 12 de 12 aguardando "preparação").

A correção, a cada passagem, para os livros na preparação:
  - prazo encerrado → arquivo (a estrela vira o selo do livro);
  - completo nas certidões (os 12 itens comprovados ou dispensados), ou fora da fila do Interceptador por não ter mais
    o que buscar → validação (etapa 4), e a validação de sempre decide: ouro com prazo aberto → Farol; encerrada →
    arquivo; ainda faltando → análise externa (o Claude no Chrome).
Nenhum livro é apagado; cada passagem grava o relatório da etapa e a medição.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from ..missao import itens as I
from ..nucleo.registro import instanciar
from .migrados import sql_migrado


def candidatos(con: sqlite3.Connection, hoje: str) -> dict[str, list[str]]:
    from ...motores.pilotos.interceptador import fila
    na_fila = {lv.id for lv in fila(con, hoje)}
    con.row_factory = None
    certs: dict[str, set[str]] = {}
    for lid, it in con.execute("SELECT livro_id, item FROM certidao WHERE situacao IN ('comprovado', 'dispensado')"):
        certs.setdefault(lid, set()).add(it)
    out: dict[str, list[str]] = {"encerrados": [], "completos": [], "sem_o_que_buscar": []}
    for lid, fim, mig in con.execute(
            "SELECT l.id, d.inscricao_fim, " + sql_migrado() + " FROM passaporte p JOIN livro l ON l.id = p.livro_id "
            "JOIN livro_dados d ON d.livro_id = l.id WHERE p.fase = 'preparacao' AND l.situacao NOT IN ('excluido', 'unido') "
            "AND COALESCE(d.validacao, '') <> 'expurgado' AND l.id NOT IN (SELECT livro_unido FROM uniao)"):
        if fim and fim < hoje:
            out["encerrados"].append(lid)
        elif set(I.DOZE) <= certs.get(lid, set()):
            out["completos"].append(lid)
        elif lid not in na_fila:
            out["sem_o_que_buscar"].append(lid)
    return out


def organizar(con: sqlite3.Connection, diario, missao, hoje: str | None = None) -> dict[str, Any]:
    from .cartorio import Cartorio
    hoje = hoje or date.today().isoformat()
    c = candidatos(con, hoje)
    cart = Cartorio(con, missao, diario)
    destino: dict[str, int] = {}
    for lid in c["encerrados"]:
        ok, _ = cart.passaporte.mover(lid, "arquivo", "o prazo encerrou na preparação: a oportunidade foi arquivada (esteira do Cartório)",
                                      {"gerou": "prazo encerrado na preparação", "analise": "interna"})
        destino["arquivo"] = destino.get("arquivo", 0) + int(ok)
    for chave, motivo in (("completos", "completo na preparação: os 12 itens resolvidos"),
                          ("sem_o_que_buscar", "fora da fila do Interceptador: nada mais a buscar")):
        for lid in c[chave]:
            ok, _ = cart.passaporte.mover(lid, "validacao", f"etapa 4: {motivo} (esteira do Cartório)",
                                          {"gerou": motivo, "analise": "interna"})
            if not ok:
                continue
            r = cart.revalidar(lid, {}, f"{motivo}: validado sem nova coleta", analise="interna")
            destino[r["etapa"] or "?"] = destino.get(r["etapa"] or "?", 0) + 1
    res = {k: len(v) for k, v in c.items()} | {"destino": destino}
    diario.emitir("medicao.registrada", "esteira", {"marcador": "esteira:preparacao", "nivel": "componente", "em": __import__("datetime").datetime.now().astimezone().isoformat(),
                                                    "valor": float(sum(len(v) for v in c.values())), "motivo": str(res)[:500]})
    return res


def no_organizar_esteira(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C7): a esteira do Cartório — nenhum livro parado na preparação sem motivo."""
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        missao = instanciar(parametros.get("missao", "eldorado.base.missao.oportunidades:MissaoOportunidades"), parametros.get("missao_parametros"))
        return [{"esteira": organizar(con, contexto.diario, missao)}]
    finally:
        con.close()
