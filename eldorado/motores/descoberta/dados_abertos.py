"""Forma 2: os dados abertos: as APIs oficiais (pela configuração de cada motor) e os portais CKAN (dados.gov.br e
estaduais), pelo endpoint padrão package_search. A terceira rota (Brasil.io) fica como reserva, a testar na criação.
"""
from __future__ import annotations

import json
from urllib.parse import quote

import jmespath

from .pistas import Buscar, Pista


def ckan(buscar: Buscar, base: str, termos: str, linhas: int = 50) -> list[Pista]:
    d = json.loads(buscar(f"{base.rstrip('/')}/api/3/action/package_search?q={quote(termos)}&rows={linhas}").conteudo)
    if not d.get("success", False):
        raise ValueError("CKAN respondeu sem sucesso")
    saida = []
    for p in d["result"]["results"]:
        recursos = p.get("resources") or []
        link = (recursos[0].get("url") if recursos else None) or f"{base.rstrip('/')}/dataset/{p.get('name')}"
        saida.append(Pista(titulo=p.get("title") or p.get("name", ""), link=link, origem=f"dados abertos (CKAN {base})",
                           data=p.get("metadata_modified"), resumo=(p.get("notes") or "")[:500],
                           extra={"organizacao": (p.get("organization") or {}).get("title"), "recursos": len(recursos)}))
    return saida


def api_oficial(buscar: Buscar, url: str, caminhos: dict[str, str]) -> list[Pista]:
    """Uma API oficial descrita só na configuração do motor: o endereço e onde está cada campo (jmespath).

    caminhos = {"itens": "data[*]", "titulo": "objeto", "link": "linkSistemaOrigem", "data": "dataEncerramentoProposta"}
    """
    d = json.loads(buscar(url).conteudo)
    itens = jmespath.search(caminhos["itens"], d) or []
    saida = []
    for i in itens:
        link = jmespath.search(caminhos["link"], i)
        if link:
            extra = {k: jmespath.search(v, i) for k, v in caminhos.items() if k not in ("itens", "titulo", "link", "data")}
            saida.append(Pista(titulo=str(jmespath.search(caminhos["titulo"], i) or ""), link=str(link), origem=f"API oficial ({url.split('?')[0]})",
                               data=jmespath.search(caminhos.get("data", "nada_ha"), i), extra=extra))
    return saida
