"""O portão da missão das oportunidades (titular, 16/10/2026), com as regras aproveitadas do Eldorado0.

Cada achado passa por aqui antes de virar livro. O que não é oportunidade é barrado com o motivo (e contado, nunca
guardado como livro). Diferença de princípio em relação ao Eldorado0: nenhuma regra é pulada por erro. Se uma regra
quebrar, o erro sobe, e a Pertinência barra o achado com alarme (o Eldorado0 deixava o achado passar em silêncio).
"""
from __future__ import annotations

import re
from datetime import date

from . import regras_portao as R


def motivo(a: dict, hoje: str | None = None) -> str | None:
    """O motivo para NÃO aceitar o achado; None se for oportunidade."""
    hoje = hoje or date.today().isoformat()
    titulo = str(a.get("titulo") or a.get("nome") or "").strip()
    if len(titulo) < 6:
        return "sem título"
    item = {**a, "titulo": titulo}
    m = R.nao_e_oportunidade(item)
    if m:
        return m
    if R.municipal_fora_de_goias(item):
        return "município de outro estado (não capital)"
    url = f"{a.get('url') or a.get('link_divulgacao') or ''} {a.get('link_oficial') or ''}"
    if "pncp.gov.br" in url:
        m = R.veredito_por_titulo(titulo, str(a.get("url") or a.get("link_divulgacao") or ""), a.get("uf"), a.get("fim"))
        if m:
            return f"PNCP — {m}"
    fim = str(a.get("fim") or a.get("prazo_fim") or "")[:10]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) and fim < hoje:
        return f"prazo encerrado em {fim}"
    return None
