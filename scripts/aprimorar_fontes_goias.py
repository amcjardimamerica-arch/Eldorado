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
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/fontes_captacao_260.json"

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


def _acrescentar(lista: list, novos) -> tuple[list, int]:
    atual = list(lista or [])
    add = [x for x in novos if x not in atual]
    return atual + add, len(add)


def aprimorar(caminho: Path = CONFIG) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    tocadas, novos_sites = [], 0
    for fonte in dados["fontes"]:
        if fonte.get("uf") != "GO" or fonte.get("area") != "cultura":
            continue
        # só as fontes ESTADUAIS: as municipais de Goiânia têm portal próprio e
        # não publicam nas páginas do Estado
        if fonte.get("nivel") != "estadual":
            continue
        programa = (fonte.get("programa") or "").lower()
        alvo = []
        if "pnab" in programa:
            alvo = SITES_PNAB_GO
        elif "fica" in programa:
            alvo = SITES_FICA + SITES_PNAB_GO[:1]
        elif "fundo de arte e cultura" in programa or "goyazes" in programa:
            alvo = SITES_PNAB_GO[:1]
        if not alvo:
            continue
        fonte["sites"], n = _acrescentar(fonte.get("sites"), alvo)
        if n:
            novos_sites += n
            tocadas.append(fonte["id"])
        dominios = set(fonte.get("dominios") or [])
        for url in alvo:
            host = url.split("//", 1)[-1].split("/", 1)[0]
            if host in DOMINIOS_NOVOS:
                dominios.add(host)
        fonte["dominios"] = sorted(dominios)

    dados.setdefault("armadilhas", [])
    for a in ARMADILHAS:
        if not any(x.get("url") == a["url"] for x in dados["armadilhas"]):
            dados["armadilhas"].append(a)

    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"fontes_atualizadas": sorted(set(tocadas)), "sites_acrescentados": novos_sites,
            "armadilhas_registradas": len(dados["armadilhas"])}


if __name__ == "__main__":
    rel = aprimorar()
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    sys.exit(0)
