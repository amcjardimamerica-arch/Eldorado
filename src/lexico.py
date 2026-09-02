"""Léxico do terceiro setor — o filtro comum de todos os sensores.

156 termos em cinco grupos (entidades, instrumentos, recursos, ação,
negativos), compilados UMA vez em uma expressão por grupo. Um texto é
candidato quando casa entidade OU instrumento, e recurso OU ação; um negativo
só derruba quando não há entidade no texto. Custo: cinco `search` por texto,
sem IA — a IA entra só depois, nos candidatos.
"""
from __future__ import annotations

import re
from functools import lru_cache

from .nucleo import ROOT, load_json

CFG = ROOT / "config/lexico_terceiro_setor.json"


def _rx(termos: list[str]) -> re.Pattern:
    def flex(t: str) -> str:
        t = re.escape(t.lower())
        # tolera acentos e plural nos termos comuns
        t = (t.replace("ç", "[çc]").replace("ã", "[ãa]").replace("õ", "[õo]")
             .replace("é", "[ée]").replace("ê", "[êe]").replace("á", "[áa]")
             .replace("â", "[âa]").replace("í", "[íi]").replace("ó", "[óo]")
             .replace("ú", "[úu]").replace("\\ ", r"s?\s+"))   # plural em cada palavra
        # plural tolerante na última palavra: entidade(s), assistencial/assistenciais
        t = re.sub(r"(al)$", r"(?:al|ais)", t)
        return t + r"(?:s|es)?"
    return re.compile(r"\b(?:" + "|".join(flex(t) for t in termos) + r")\b", re.I)


@lru_cache(maxsize=1)
def compilado() -> dict[str, re.Pattern]:
    lex = load_json(CFG)
    return {g: _rx(lex[g]) for g in ("entidades", "instrumentos", "recursos", "acao", "negativos")}


def casar(texto: str) -> dict:
    """Devolve os grupos casados e o veredito de candidatura."""
    rx = compilado()
    achados = {g: sorted({m.group(0).lower() for m in r.finditer(texto)})[:6]
               for g, r in rx.items()}
    tem = {g: bool(v) for g, v in achados.items()}
    # entidade + qualquer outro sinal basta; sem entidade, exige instrumento + recurso
    candidato = ((tem["entidades"] and (tem["instrumentos"] or tem["recursos"] or tem["acao"]))
                 or (tem["instrumentos"] and tem["recursos"])) \
        and not (tem["negativos"] and not tem["entidades"])
    forca = sum(1 for g in ("entidades", "instrumentos", "recursos", "acao") if tem[g])
    return {"candidato": candidato, "forca": forca, "termos": achados}


def total_termos() -> int:
    lex = load_json(CFG)
    return sum(len(v) for v in lex.values() if isinstance(v, list))
