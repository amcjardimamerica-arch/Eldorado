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


def indice_commoncrawl(dominio: str, prefixo: str = "", limite: int = 300) -> list[Pista]:
    """O índice do Common Crawl (cdx_toolkit): a segunda cópia arquivada, além do Wayback; as URLs que o rastreio aberto
    já guardou do domínio (páginas que saíram do ar, editais antigos)."""
    import cdx_toolkit
    cdx = cdx_toolkit.CDXFetcher(source="cc")
    saida, vistos = [], set()
    for obj in cdx.iter(f"{dominio.rstrip('/')}/{prefixo.lstrip('/')}*", limit=limite, filter=["status:200"]):
        u = obj.data.get("url")
        if u and u not in vistos:
            vistos.add(u)
            saida.append(Pista(titulo=u.rstrip("/").rsplit("/", 1)[-1], link=u, data=(obj.data.get("timestamp") or "")[:8] or None,
                               origem="índice do Common Crawl"))
    return saida


def arquivar(url: str) -> str | None:
    """Arquiva a página no Wayback (waybackpy) e devolve o endereço da cópia: a prova da oportunidade fica guardada mesmo
    que o site mude. Lento (segundos a minutos): usado com parcimônia (os achados com prazo, com limite por execução)."""
    from waybackpy import WaybackMachineSaveAPI
    salvo = WaybackMachineSaveAPI(url, user_agent="Eldorado/1.0 (arquivo de oportunidades para OSC)").save()
    return str(salvo) if salvo else None
