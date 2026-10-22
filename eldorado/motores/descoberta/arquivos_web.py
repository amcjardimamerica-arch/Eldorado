"""Forma 4: os arquivos da web: o índice da Wayback Machine lista as URLs já vistas de um domínio (inclusive editais
antigos e páginas que saíram do ar). O índice do Common Crawl segue o mesmo formato e fica como reserva.
"""
from __future__ import annotations

import json
from urllib.parse import quote

from .pistas import Buscar, Pista


def indice_wayback(buscar: Buscar, dominio: str, prefixo: str = "", base: str = "https://web.archive.org", limite: int = 500) -> list[Pista]:
    alvo = quote(f"{dominio}/{prefixo}".rstrip("/"))
    d = json.loads(buscar(f"{base.rstrip('/')}/cdx/search/cdx?url={alvo}&matchType=prefix&output=json&collapse=urlkey&limit={limite}").conteudo or b"[]")
    if len(d) < 2:
        return []
    cab = d[0]
    saida = []
    for linha in d[1:]:
        c = dict(zip(cab, linha, strict=False))
        url = c.get("original", "")
        saida.append(Pista(titulo=url.rstrip("/").rsplit("/", 1)[-1], link=url, origem="arquivos da web (Wayback)",
                           data=c.get("timestamp"), extra={"tipo": c.get("mimetype")}))
    return saida
