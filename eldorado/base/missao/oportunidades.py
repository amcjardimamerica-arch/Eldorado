"""A missão das oportunidades, no contrato da plataforma: itens, chave e portão."""
from __future__ import annotations

import tomllib
from pathlib import Path

import msgspec

from ..nucleo.contratos import Achado, Descricao, Missao, Saude
from . import chave as _chave
from . import itens as _itens
from . import portao as _portao

RAIZ = Path(__file__).resolve().parents[3]


class MissaoOportunidades(Missao):
    def __init__(self, hoje: str | None = None):
        self.hoje = hoje
        self.declaracao = tomllib.loads((Path(__file__).parent / "oportunidades.toml").read_text(encoding="utf-8"))["missao"]

    def descrever(self) -> Descricao:
        return Descricao(id="oportunidades", tipo="missao", parte="BASE", componente="Missão (finalidade trocável)",
                         finalidade="oportunidades de recursos para organizações da sociedade civil",
                         metrica="decisões contrariadas por veredito (zero) e casos de ouro (100%)")

    def saude(self) -> Saude:
        faltam = [d for d in self.declaracao["dados"] if not (RAIZ / d).exists()]
        return Saude(ok=not faltam, mensagem="dados da missão presentes" if not faltam else f"faltam: {', '.join(faltam)}")

    def itens(self) -> list[dict[str, str]]:
        return _itens.itens()

    def chave(self, achado: Achado) -> str:
        d = achado.dados or {}
        return _chave.chave(achado.titulo or "", d.get("orgao"), d.get("uf"))

    def portao(self, achado: Achado) -> tuple[bool, str]:
        item = {**(achado.dados or {}), **msgspec.to_builtins(achado)}
        m = _portao.motivo(item, self.hoje)
        return (m is None, m or "oportunidade")
