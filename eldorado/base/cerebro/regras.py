"""A tabela única de regras e decisões da titular (reativada em 25/10/2026: estava inativa, sem nó que a chamasse).

As duas fontes formam uma tabela só: as regras por tema (config/regras.toml) e o registro das regras com as travas
(config/regras_titular.json, cada uma com o seu tema). Onde as duas falam do mesmo tema, vale a mais recente; no mesmo
dia, o registro (precedência 1). O nó da passagem registra a tabela no Cérebro (idempotente) e abre o alarme de
contradição uma vez só; a trava do portão recusa uma regra nova que contradiga outra, até a titular decidir.

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

    def registrar(self, diario: Diario, abertos: set[str] | None = None) -> None:
        """Grava a tabela no Cérebro: cada regra, e a substituição das que não são mais vigentes."""
        import hashlib

        from ..nucleo.eventos import emitir_se_mudou  # 29/10/2026: só quando muda (eram 2.867 por dia)
        ids: dict[Regra, int] = {}
        for r in self.regras:                                    # a identidade pelo conteúdo: o texto mudou, é uma regra nova
            i = int(hashlib.sha1(f"{r.tema}|{r.regra}|{r.data}".encode()).hexdigest()[:13], 16)
            ids[r] = i
            emitir_se_mudou(diario, "regra.registrada", "regras", str(i), {"id": i, "tema": r.tema, "regra": r.regra, "data": r.data,
                                                          "decisao_da_titular": int(r.decisao_da_titular), "precedencia": r.precedencia})
        for t in self.temas():
            lista = self.do_tema(t)
            for antiga in lista[1:]:
                emitir_se_mudou(diario, "regra.substituida", "regras", str(ids[antiga]), {"id": ids[antiga], "vigente": 0, "substituida_por": ids[lista[0]]})
        for t, topo in self.contradicoes():
            msg = f"contradição no tema '{t}': {len(topo)} regras com o mesmo peso e textos diferentes"
            if msg in (abertos or set()):
                continue                                         # o alarme já está aberto: não se repete
            diario.emitir("alarme.aberto", "regras", {"gravidade": "alta", "modulo": "regras", "aberto_em": topo[0].data, "mensagem": msg})


def carregar(arquivo: str | Path) -> Regras:
    p = Path(arquivo)
    if not p.exists():
        return Regras([])
    d = tomllib.loads(p.read_text(encoding="utf-8"))
    return Regras([Regra(tema=r["tema"], regra=r["regra"], data=str(r["data"]), decisao_da_titular=bool(r.get("decisao_da_titular", False)),
                         precedencia=int(r.get("precedencia", 0)), parametros=dict(r.get("parametros", {}))) for r in d.get("regra", [])])


def carregar_tudo(raiz: str | Path = ".") -> Regras:
    """A tabela única: as regras por tema e o registro das regras da titular (o registro com precedência 1)."""
    import json
    raiz = Path(raiz)
    base = carregar(raiz / "config/regras.toml")
    try:
        reg = json.loads((raiz / "config/regras_titular.json").read_text(encoding="utf-8")).get("regras", [])
    except (OSError, ValueError):
        reg = []
    novas = [Regra(tema=r.get("tema") or r["id"], regra=f"{r['id']}: {r['regra']}", data=str(r.get("data") or ""), decisao_da_titular=True,
                   precedencia=1) for r in reg]
    return Regras(base.regras + novas)


def no_regras(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o início): registra a tabela única no Cérebro e acende a contradição, se houver."""
    import sqlite3
    regras = carregar_tudo(parametros.get("raiz", "."))
    abertos: set[str] = set()
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if p.exists():
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        try:
            abertos = {m for (m,) in con.execute("SELECT mensagem FROM alarme WHERE modulo = 'regras' AND fechado_em IS NULL")}
        except sqlite3.Error:
            pass
        finally:
            con.close()
    regras.registrar(contexto.diario, abertos)
    return [{"regras": len(regras.regras), "temas": len(regras.temas()), "contradicoes": len(regras.contradicoes())}]
