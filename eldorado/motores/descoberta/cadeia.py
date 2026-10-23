"""A leitura em cadeia (canivete suíço): a lista → cada item → o detalhe → o texto, sem código por fonte.

Serve a diários oficiais, tribunais e portais cuja listagem é em etapas (as edições do dia → o sumário de cada edição →
cada matéria). Cada elo lê JSON (com jmespath) ou HTML (com seletor CSS) e tira os campos de cada item; os campos
passam ao elo seguinte (que monta o seu endereço com eles) e às pistas do último elo.

Campos de HTML: "texto" (o texto do elemento), "attr:<nome>" (um atributo), "ancestrais:<seletor>" (o texto do seletor
em cada ancestral, do mais externo ao mais interno, juntos por " › "), "re:<regex>" (o grupo 1 aplicado ao HTML do
elemento). Campos de JSON: uma expressão jmespath relativa ao item.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urljoin

from selectolax.lexbor import LexborHTMLParser


@dataclass
class Elo:
    formato: str                          # "json" ou "html"
    itens: str                            # jmespath (json) ou seletor CSS (html)
    campos: dict[str, str] = field(default_factory=dict)
    url: str | None = None                # o endereço deste elo, montado com os campos do item anterior (o primeiro usa o da fonte)
    filtro: dict[str, str] = field(default_factory=dict)   # campo → regex: só seguem os itens que casam
    limite: int = 300


class _Formato(dict):
    def __missing__(self, chave: str) -> str:
        return ""


def formatar(modelo: str, campos: dict[str, Any]) -> str:
    return modelo.format_map(_Formato({k: ("" if v is None else v) for k, v in campos.items()}))


def _ancestrais(no, seletor: str) -> str:
    nomes = []
    pai = no.parent
    while pai is not None and pai.tag not in ("html", "-undef"):
        alvo = pai.css_first(seletor) if hasattr(pai, "css_first") else None
        if alvo is not None and alvo is not no and pai.tag in ("li", "details", "tr"):
            t = alvo.text(strip=True)
            if t and (not nomes or nomes[-1] != t):
                nomes.append(t)
        pai = pai.parent
    return " › ".join(reversed(nomes))


def _itens_html(conteudo: bytes, base: str, elo: Elo) -> list[dict[str, Any]]:
    arvore = LexborHTMLParser(conteudo.decode("utf-8", errors="replace"))
    saida = []
    for no in arvore.css(elo.itens)[:elo.limite]:
        item: dict[str, Any] = {}
        for nome, spec in elo.campos.items():
            if spec == "texto":
                item[nome] = re.sub(r"\s+", " ", no.text(strip=True))
            elif spec.startswith("attr:"):
                v = no.attributes.get(spec[5:])
                item[nome] = urljoin(base, v) if (v and spec[5:] in ("href", "src")) else v
            elif spec.startswith("ancestrais:"):
                item[nome] = _ancestrais(no, spec[len("ancestrais:"):])
            elif spec.startswith("re:"):
                m = re.search(spec[3:], no.html or "", re.I | re.S)
                item[nome] = m.group(1) if m and m.groups() else (m.group(0) if m else None)
        saida.append(item)
    return saida


def _itens_json(conteudo: bytes, elo: Elo) -> list[dict[str, Any]]:
    import jmespath
    doc = json.loads(conteudo)
    lista = jmespath.search(elo.itens, doc) or []
    saida = []
    for x in lista[:elo.limite]:
        saida.append({nome: jmespath.search(expr, x) for nome, expr in elo.campos.items()} if elo.campos else (x if isinstance(x, dict) else {"valor": x}))
    return saida


def percorrer(buscar: Callable[[str], Any], url: str, elos: list[Elo], relatorio: list[str] | None = None) -> list[dict[str, Any]]:
    """Percorre a cadeia; um item cujo elo falha não derruba os outros (a falha vai ao relatório)."""
    relatorio = relatorio if relatorio is not None else []
    atuais: list[dict[str, Any]] = [{"_url": url}]
    for n, elo in enumerate(elos):
        proximos: list[dict[str, Any]] = []
        for pai in atuais:
            endereco = pai["_url"] if n == 0 else formatar(elo.url or "", pai)
            try:
                r = buscar(endereco)
                filhos = _itens_json(r.conteudo, elo) if elo.formato == "json" else _itens_html(r.conteudo, endereco, elo)
            except Exception as e:  # noqa: BLE001 — a cadeia segue com os outros itens; a falha fica registrada
                relatorio.append(f"elo {n + 1} ({endereco[:90]}): {type(e).__name__}: {str(e)[:150]}")
                continue
            for f in filhos:
                item = {**{k: v for k, v in pai.items() if k != "_url"}, **f, "_url": endereco}
                if all(re.search(rx, str(item.get(campo) or ""), re.I) for campo, rx in elo.filtro.items()):
                    proximos.append(item)
        atuais = proximos
    return atuais
