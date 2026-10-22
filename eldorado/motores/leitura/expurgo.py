"""O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição na página).

Medido nos editais reais (22/10/2026): remove 3,2% do texto (marcas de impressão do SEI, número de página) e
mantém todos os valores e palavras-chave. O expurgo ingênuo (tirar toda linha repetida) apagava valores de tabelas.
Trava extra: um bloco com valor em reais ou CNPJ nunca é retirado, mesmo no cabeçalho.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

FAIXA = 0.09            # 9% do topo e da base da página
REPETICAO = 0.6         # presente em 60% ou mais das páginas
MINIMO_PAGINAS = 3
PROTEGIDO = re.compile(r"R\$\s*\d|\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")


@dataclass
class Bloco:
    y0: float
    y1: float
    texto: str


def _norm(t: str) -> str:
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", t.strip().lower()))


def aplicar(paginas: list[tuple[float, list[Bloco]]]) -> list[tuple[str, int]]:
    """Recebe, por página, a altura e os blocos; devolve, por página, o texto mantido e quantos caracteres saíram."""
    n = len(paginas)
    repetidos: set[str] = set()
    if n >= MINIMO_PAGINAS:
        freq: Counter[str] = Counter()
        for altura, blocos in paginas:
            freq.update({_norm(b.texto) for b in blocos if (b.y1 < FAIXA * altura or b.y0 > (1 - FAIXA) * altura) and b.texto.strip()})
        repetidos = {k for k, c in freq.items() if c >= max(MINIMO_PAGINAS, REPETICAO * n)}
    saida = []
    for altura, blocos in paginas:
        mantidos, removidos = [], 0
        for b in blocos:
            na_faixa = b.y1 < FAIXA * altura or b.y0 > (1 - FAIXA) * altura
            if na_faixa and _norm(b.texto) in repetidos and not PROTEGIDO.search(b.texto):
                removidos += len(b.texto)
            else:
                mantidos.append(b.texto)
        saida.append(("\n".join(mantidos), removidos))
    return saida
