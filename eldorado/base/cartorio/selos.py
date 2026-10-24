"""Os dois selos de cada livro, calculados a cada passagem.

- A estrela (a oportunidade atual): a completude dos 12 itens, pelo critério único de 04/10 (missao/itens.py).
- O selo do livro (o histórico): a previsibilidade da próxima edição, pelos últimos 3 anos (titular, 03/10):
  ouro = edições em 2 ou mais dos últimos 3 anos, com página oficial e data; prata = há edição anterior, sem prova
  completa; bronze = só a edição atual; sem = nenhuma edição conhecida.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..missao import itens as I
from ..nucleo.eventos import Diario, agora


@dataclass(frozen=True)
class Edicao:
    ano: int
    pagina_oficial: bool
    data: bool


def selo_do_livro(edicoes: list[Edicao], ano_atual: int) -> str:
    if not edicoes:
        return "sem"
    janela = {ano_atual - 2, ano_atual - 1, ano_atual}
    provadas = {e.ano for e in edicoes if e.ano in janela and e.pagina_oficial and e.data}
    if len(provadas) >= 2:
        return "ouro"
    if any(e.ano < ano_atual for e in edicoes):
        return "prata"
    return "bronze"


RANK = {"sem": 0, "bronze": 1, "prata": 2, "ouro": 3}


def calcular(diario: Diario, livro: str, certidoes: dict[str, dict], edicoes: list[Edicao], ano_atual: int,
             prazo: str | None = None, selo_atual: str | None = None, origem_confirmada: bool = False) -> tuple[str, str]:
    """A ESTRELA valida a oportunidade ATUAL (só existe com o prazo em aberto); o SELO DO LIVRO é o histórico. Quando a
    oportunidade é arquivada (prazo encerrado), a estrela vira o selo do livro (estrela de ouro → livro de ouro) e a
    estrela volta a "sem", aguardando a próxima oportunidade (titular, 22/10/2026)."""
    # a régua da titular (23/10/2026): a estrela e o selo pela mesma régua (bronze: o prazo; prata: o prazo e o link
    # original; ouro: todas as informações, ou dispensadas pelo Chrome); o selo nunca diminui
    nivel = I.nivel(certidoes, origem_confirmada)
    selo = selo_atual if selo_atual in RANK else "sem"
    if prazo == "encerrada":
        estrela, selo = "sem", max((selo, nivel), key=RANK.get)
    else:
        estrela = nivel
    diario.emitir("selo.calculado", "selos", {"id": livro, "estrela": estrela, "selo_livro": selo,
                                              "informacoes_validadas": sum(1 for k in I.DOZE if I.resolvido(certidoes.get(k))), "atualizado_em": agora()})
    return estrela, selo
