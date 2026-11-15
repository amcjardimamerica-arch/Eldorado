"""K2 (R57, titular, 14/11/2026): a finalidade em cada decisão do Comandante — toda decisão leva a FINALIDADE (descobrir,
completar, revalidar, prever; e «operar», a decisão de pular uma etapa da passagem, que não é missão de busca) e a MEDIDA do
que conta como sucesso. Vão no contexto da decisão (comandante_decisao.contexto), sem mudar o esquema do Cérebro; a Sala
soma o rendimento por finalidade."""
from __future__ import annotations

import json
from typing import Any

FINALIDADE: dict[str, tuple[str, str]] = {
    "coleta": ("descobrir", "o livro novo chega ao Farol ou ao arquivo com edição anterior"),
    "espiao": ("descobrir", "o livro do objetivo chega ao Farol"),
    "interceptador": ("completar", "os itens do checklist certificados no livro"),
    "revalidacao": ("revalidar", "o prazo e o link oficial do livro conferidos"),
    "previsao": ("prever", "a edição prevista abre na data"),
    "passagem": ("operar", "o tempo da passagem poupado sem perder trabalho"),
}


def anotar(contexto: Any, etapa: str) -> str:
    """O contexto da decisão (texto JSON ou dicionário) com a finalidade e a medida da etapa."""
    if isinstance(contexto, str):
        try:
            ctx = json.loads(contexto) if contexto else {}
        except ValueError:
            ctx = {"contexto": contexto}
    else:
        ctx = dict(contexto or {})
    fin, med = FINALIDADE.get(etapa, ("operar", "a decisão cumprida"))
    ctx.setdefault("finalidade", fin)
    ctx.setdefault("medida", med)
    return json.dumps(ctx, ensure_ascii=False)
