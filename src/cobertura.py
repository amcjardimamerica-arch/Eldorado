"""MAPA DE COBERTURA — onde os 29 motores já olham, e onde ninguém olha.

O Piloto não existe para repetir o trabalho dos motores. Se o PNCP, o Diário Oficial e a
Rouanet já são lidos todo dia por um motor, gastar voo neles é desperdício puro: o motor lê
mais rápido, mais barato e sem depender de buscador.

Este módulo monta a lista do que já está coberto — domínios, plataformas e tipos de fonte —
e entrega ao Piloto a instrução inversa: **vá onde isto não alcança**. Também guarda os vazios
conhecidos, que é onde o dinheiro privado costuma estar e nenhum diário oficial publica.
"""
from __future__ import annotations

import json
import re
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "docs/dados/cobertura.json"

# O que nenhum dos 29 motores alcança, por natureza da fonte
VAZIOS = [
    {"vazio": "instituto ou fundação empresarial que seleciona por formulário no próprio site",
     "porque": "não publica em diário oficial nem em plataforma agregadora"},
    {"vazio": "patrocínio declarado no rodapé do site de outra entidade",
     "porque": "é rastro, não é edital: nenhum motor procura rodapé de site alheio"},
    {"vazio": "relatório ESG com o valor investido e onde",
     "porque": "documento corporativo, fora de qualquer portal de editais"},
    {"vazio": "edital de anos anteriores de um financiador privado",
     "porque": "já encerrado, some dos agregadores — mas indica quando o próximo sai"},
    {"vazio": "notícia que anuncia edital ainda não lançado",
     "porque": "o motor só vê o edital depois de publicado; a notícia vem antes"},
    {"vazio": "ata de conselho municipal que aprova repasse",
     "porque": "o repasse aprovado vira edital semanas depois, e ninguém lê atas"},
    {"vazio": "programa de doação de multinacional com inscrição local",
     "porque": "publicado em inglês, no site global, fora do radar brasileiro"},
    {"vazio": "portal especializado em captação que agrega editais",
     "porque": "é fonte de fontes: se for bom, vira motor próprio e sai da mão do Piloto"},
]


def _dominios_cobertos() -> dict:
    cfg = load_json(ROOT / "config/rotas_motores.json")
    motores = cfg.get("motores") or cfg
    cobertos: dict[str, str] = {}
    for mid, mc in (motores.items() if isinstance(motores, dict) else []):
        if not isinstance(mc, dict):
            continue
        for u in (mc.get("rotas") or mc.get("urls") or []):
            url = u.get("url") if isinstance(u, dict) else u
            h = (urlsplit(str(url)).hostname or "").replace("www.", "")
            if h:
                cobertos.setdefault(h, mid)
    return cobertos


def mapa() -> dict:
    cob = _dominios_cobertos()
    d = {"em": now_iso(), "dominios_cobertos": len(cob), "por_dominio": cob,
         "regra": "o Piloto não vai a domínio já coberto por motor: o motor lê aquilo todo dia, mais rápido e sem depender de buscador",
         "vazios_conhecidos": VAZIOS,
         "tipos_ja_cobertos": ["diário oficial", "PNCP", "Rouanet/SALIC", "plataformas agregadoras conhecidas",
                               "editais de secretaria estadual e municipal", "fundos públicos"]}
    write_json(SAIDA, d)
    return {k: v for k, v in d.items() if k != "por_dominio"}


def ja_coberto(url: str) -> tuple[bool, str]:
    """Este endereço já é vigiado por algum motor?"""
    h = (urlsplit(str(url or "")).hostname or "").replace("www.", "")
    if not h:
        return False, ""
    cob = load_json(SAIDA).get("por_dominio", {}) if SAIDA.exists() else _dominios_cobertos()
    for dom, mid in cob.items():
        if h == dom or h.endswith("." + dom):
            return True, mid
    return False, ""


def instrucao_para_o_piloto(limite: int = 14) -> str:
    """O texto que entra no prompt: onde NÃO ir, e o que procurar em vez disso."""
    cob = load_json(SAIDA).get("por_dominio", {}) if SAIDA.exists() else _dominios_cobertos()
    doms = sorted(set(cob))[:limite]
    return ("O QUE JÁ ESTÁ COBERTO por motor próprio (não perca voo com isto): "
            + ", ".join(doms) + (" e outros." if len(cob) > limite else ".")
            + "\nTambém já são lidos todo dia: diário oficial, PNCP, Rouanet e as plataformas agregadoras conhecidas.\n"
            + "SEU LUGAR É ONDE ISTO NÃO ALCANÇA:\n- "
            + "\n- ".join(f"{v['vazio']} ({v['porque']})" for v in VAZIOS))


if __name__ == "__main__":
    print(json.dumps(mapa(), ensure_ascii=False, indent=1))
    print("\n" + instrucao_para_o_piloto())
