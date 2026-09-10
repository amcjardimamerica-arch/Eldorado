#!/usr/bin/env python3
"""Aponta os motores de Goiás para as páginas onde os editais realmente saem.

Descoberto na verificação de 08/09/2026. As 18 fontes estaduais de cultura de
Goiás (PNAB, FICA, Fundo de Arte e Cultura, Goyazes) apontavam apenas para
`goias.gov.br/cultura/` — o índice da secretaria — e para o Diário Oficial. O
índice não lista os editais abertos, e o resultado prático foi que os 18 editais
do PNAB Ciclo 2 de 2026 (inscrições de 13/03 a 17/04/2026, pela Plataforma Baru)
NÃO entraram na base, enquanto três registros apontavam para
`goias.gov.br/cultura/termos-de-fomento` — a lista de termos já celebrados por
inexigibilidade, que não tem inscrição e nunca terá prazo.

Este script acrescenta às fontes de cultura de Goiás os endereços verificados,
sem remover nada do que já existe, e é idempotente: rodar duas vezes não
duplica. Rodar com `python scripts/aprimorar_fontes_goias.py`.

Desde 09/09/2026 grava em `config/curadoria_fontes.json` — o arquivo que a
regeneração de dados não reescreve — e regenera o catálogo em seguida. Antes
gravava no catálogo gerado, e a regeneração seguinte apagava tudo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Endereços conferidos em 08/09/2026, com navegador, um a um.
SITES_PNAB_GO = [
    "https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/",  # a página que lista os 18 editais
    "https://pnab.cultura.go.gov.br",                            # portal PNAB do Estado
]
SITES_FICA = [
    "https://fica.go.gov.br",
    "https://web.ufg.br/plateia-editais/",  # plataforma onde as chamadas do FICA são publicadas
]
DOMINIOS_NOVOS = {
    "www.goias.gov.br",
    "pnab.cultura.go.gov.br",
    "fica.go.gov.br",
    "web.ufg.br",
}

# Fonte que só devolve termo já celebrado: fica registrada como armadilha para
# que nenhuma rodada futura a reintroduza como se fosse página de edital.
ARMADILHAS = [
    {
        "url": "https://goias.gov.br/cultura/termos-de-fomento",
        "motivo": ("lista de termos JÁ CELEBRADOS por inexigibilidade: não há fase de "
                   "inscrição e nunca haverá prazo"),
        "verificado_em": "2026-09-08",
    }
]


# Critério das fontes ESTADUAIS de cultura de Goiás. As municipais de Goiânia
# têm portal próprio e não publicam nas páginas do Estado — colar URL estadual
# nelas foi o erro de 08/09/2026, e há teste guardando contra ele.
_ESTADUAL_GO_CULTURA = {"uf": "GO", "area": "cultura", "nivel": "estadual"}

REGRAS = [
    {"quando": dict(_ESTADUAL_GO_CULTURA, programa_contem=["pnab"]),
     "sites_acrescentar": SITES_PNAB_GO, "verificado_em": "2026-09-08"},
    {"quando": dict(_ESTADUAL_GO_CULTURA, programa_contem=["fica"]),
     "sites_acrescentar": SITES_FICA + SITES_PNAB_GO[:1], "verificado_em": "2026-09-08"},
    {"quando": dict(_ESTADUAL_GO_CULTURA,
                    programa_contem=["fundo de arte e cultura", "goyazes"]),
     "sites_acrescentar": SITES_PNAB_GO[:1], "verificado_em": "2026-09-08"},
]


def aprimorar() -> dict:
    from src import curadoria_fontes, fontes260

    rel = curadoria_fontes.registrar(regras=REGRAS, armadilhas=ARMADILHAS,
                                     atualizada_em="2026-09-08")
    resumo = fontes260.run()
    cur = resumo.get("curadoria", {})
    return {"curadoria_acrescentada": rel,
            "fontes_corrigidas": sorted(set(cur.get("fontes_corrigidas") or [])),
            "sites_reaplicados": cur.get("sites_reaplicados", 0),
            "armadilhas_registradas": cur.get("armadilhas", 0)}


if __name__ == "__main__":
    rel = aprimorar()
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    sys.exit(0)
