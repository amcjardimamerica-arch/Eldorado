"""O site oficial: a oportunidade se encontra NA FONTE (titular, 14/10/2026).

O que vem de notícia, agregador, rede social, encurtador ou buscador é pista: insumo de busca, nunca fonte oficial.
A lista de republicadores é a do Eldorado0 (config/missao/republicadores.json), aumentada quando aparece um novo.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[3]
GRUPOS = ("noticia", "agregador", "rede_social", "encurtador", "buscador")


@lru_cache(maxsize=1)
def _republicadores() -> tuple[str, ...]:
    d = json.loads((RAIZ / "config/missao/republicadores.json").read_text(encoding="utf-8"))
    return tuple(sorted({h.lower() for g in GRUPOS for h in d.get(g, [])}))


def dominio(url: str | None) -> str:
    return (urlsplit(str(url or "")).hostname or "").lower().removeprefix("www.")


def eh_republicador(url: str | None) -> bool:
    d = dominio(url)
    return bool(d) and any(d == r or d.endswith("." + r) for r in _republicadores())


def eh_fonte(url: str | None) -> bool:
    return bool(dominio(url)) and str(url).startswith(("http://", "https://")) and not eh_republicador(url)


def escolher(links: list[str | None]) -> str | None:
    """O primeiro link que é fonte (não republicador); None se só houver pistas."""
    for u in links:
        if u and eh_fonte(u):
            return u
    return None
