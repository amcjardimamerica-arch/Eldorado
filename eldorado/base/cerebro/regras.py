"""A tabela única de regras e decisões da titular.

Para cada tema, a regra vigente é a decisão da titular mais recente; depois a precedência; depois a data.
As anteriores ficam registradas como substituídas (nunca apagadas). Duas regras do mesmo tema com o mesmo peso
e textos diferentes são uma contradição: viram alarme, até a titular decidir.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..nucleo.eventos import Diario


@dataclass(frozen=True)
class Regra:
    tema: str
    regra: str
    data: str
    decisao_da_titular: bool = False
    precedencia: int = 0
    parametros: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def peso(self) -> tuple:
        return (self.decisao_da_titular, self.data, self.precedencia)


class Regras:
    def __init__(self, regras: list[Regra]):
        self.regras = list(regras)

    def temas(self) -> list[str]:
        return sorted({r.tema for r in self.regras})

    def do_tema(self, tema: str) -> list[Regra]:
        return sorted((r for r in self.regras if r.tema == tema), key=Regra.peso, reverse=True)

    def vigente(self, tema: str) -> Regra | None:
        lista = self.do_tema(tema)
        return lista[0] if lista else None

    def contradicoes(self) -> list[tuple[str, list[Regra]]]:
        saida = []
        for t in self.temas():
            lista = self.do_tema(t)
            topo = [r for r in lista if r.peso() == lista[0].peso()]
            if len({r.regra for r in topo}) > 1:
                saida.append((t, topo))
        return saida

    def registrar(self, diario: Diario) -> None:
        """Grava a tabela no Cérebro: cada regra, e a substituição das que não são mais vigentes."""
        ids: dict[Regra, int] = {}
        for i, r in enumerate(self.regras, 1):
            ids[r] = i
            diario.emitir("regra.registrada", "regras", {"id": i, "tema": r.tema, "regra": r.regra, "data": r.data,
                                                          "decisao_da_titular": int(r.decisao_da_titular), "precedencia": r.precedencia})
        for t in self.temas():
            lista = self.do_tema(t)
            for antiga in lista[1:]:
                diario.emitir("regra.substituida", "regras", {"id": ids[antiga], "vigente": 0, "substituida_por": ids[lista[0]]})
        for t, topo in self.contradicoes():
            diario.emitir("alarme.aberto", "regras", {"gravidade": "alta", "modulo": "regras", "aberto_em": topo[0].data,
                                                      "mensagem": f"contradição no tema '{t}': {len(topo)} regras com o mesmo peso e textos diferentes"})


def carregar(arquivo: str | Path) -> Regras:
    p = Path(arquivo)
    if not p.exists():
        return Regras([])
    d = tomllib.loads(p.read_text(encoding="utf-8"))
    return Regras([Regra(tema=r["tema"], regra=r["regra"], data=str(r["data"]), decisao_da_titular=bool(r.get("decisao_da_titular", False)),
                         precedencia=int(r.get("precedencia", 0)), parametros=dict(r.get("parametros", {}))) for r in d.get("regra", [])])
