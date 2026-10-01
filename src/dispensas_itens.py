"""Dispensa dos 12 itens por tipo de recurso (titular, 01/10/2026).

Cada oportunidade e cada livro da Biblioteca persegue os 12 itens de um edital: Objeto, Prazo de inscrição, Resultado,
Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação e Área de atuação.
Alguns recursos não têm certos itens (emenda parlamentar não tem edital, fluxo contínuo não tem data final,
destinação judicial tem valor fixado no processo). Este módulo classifica o recurso num REGIME
(`config/dispensas_por_regime.json`) e diz que itens ainda faltantes são DISPENSA PROVÁVEL.

Duas coisas diferentes, nunca misturadas:
- dispensa CONFIRMADA ('disp'): o próprio edital ou regramento oficial declara que o item não existe;
- dispensa PROVÁVEL ('prov'): hipótese pelo regime — não conta como item preenchido e não é dado do edital.

Item que o regime exige continua faltando até a fonte oficial ser lida. Nada é inventado.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from .nucleo import ROOT

MATRIZ = ROOT / "config/dispensas_por_regime.json"
ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")
PADRAO = "chamamento_publico"

_RX_CONTINUO = re.compile(r"fluxo cont[ií]nuo|demanda cont[ií]nua|credenciamento permanente|cadastro permanente|inscri[cç][õo]es? permanentes?", re.I)
_RX_EMENDA = re.compile(r"emendas? parlamentares?|emenda impositiva|indica[cç][ãa]o parlamentar", re.I)
_RX_INCENTIVO = re.compile(r"rouanet|pronac|incentivo fiscal|lei de incentivo|goyazes|pronon|pronas|fundo da inf[âa]ncia|fundo do idoso|\bfmdca\b|\bfia\b", re.I)
_RX_JUDICIAL = re.compile(r"presta[cç][õo]es? pecuni[áa]rias?|destina[cç][ãa]o (de recursos|judicial)|\bTAC\b|termo de ajustamento|penas? pecuni[áa]rias?|\bprograma destina\b", re.I)
_RX_BENS = re.compile(r"doa[cç][ãa]o de (bens|mercadorias)|mercadorias apreendidas|bens apreendidos", re.I)


@lru_cache(maxsize=1)
def matriz() -> dict:
    try:
        return json.loads(MATRIZ.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"regimes": {PADRAO: {"nome": "Edital ou chamamento público com seleção", "itens": {}}}}


def regime_do_motor(mo: dict | None) -> tuple[str | None, str | None]:
    """Regime a partir do que o catálogo já sabe do motor (campos estruturados, mais confiáveis que o título)."""
    if not mo:
        return None, None
    to, tp, fam = str(mo.get("tipo_objeto") or ""), str(mo.get("tipo") or ""), str(mo.get("familia") or "")
    if to == "Emenda" or tp == "emenda":
        return "emenda_parlamentar", "catálogo do motor"
    if to == "Incentivo fiscal" or tp == "incentivo_fiscal" or fam in ("Lei Rouanet", "Lei de Incentivo ao Esporte", "PRONON / PRONAS", "Fundo da Criança (FMDCA/FIA)", "Fundo do Idoso"):
        return "incentivo_fiscal", "catálogo do motor"
    if to == "Destinação judicial" or tp == "destinacao_judicial" or fam in ("Destinação judicial", "Ministério Público"):
        return "destinacao_judicial", "catálogo do motor"
    if mo.get("regime_inscricao") == "contínuo" or mo.get("regime_prazo") == "permanente_fluxo_continuo":
        return "fluxo_continuo", "catálogo do motor"
    if to in ("Doação/patrocínio", "Grant internacional") or tp in ("doacao_patrocinio", "grant") or fam in ("Internacionais", "Fundações e institutos privados"):
        return "patrocinio_privado", "catálogo do motor"
    return None, None


def regime_por_texto(*textos: str, privada: bool = False) -> tuple[str, str]:
    t = " ".join(str(x or "") for x in textos)
    if _RX_EMENDA.search(t):
        return "emenda_parlamentar", "palavra-chave no título"
    if _RX_BENS.search(t):
        return "doacao_de_bens", "palavra-chave no título"
    if _RX_JUDICIAL.search(t):
        return "destinacao_judicial", "palavra-chave no título"
    if _RX_INCENTIVO.search(t):
        return "incentivo_fiscal", "palavra-chave no título"
    if _RX_CONTINUO.search(t):
        return "fluxo_continuo", "palavra-chave no título"
    if privada:
        return "patrocinio_privado", "financiador privado"
    return PADRAO, "padrão (edital com seleção)"


def regime(motor: dict | None = None, *textos: str, privada: bool = False, emenda: bool = False, prazo_dispensado: bool = False) -> tuple[str, str]:
    if emenda:
        return "emenda_parlamentar", "calendário legislativo"
    if prazo_dispensado:
        return "fluxo_continuo", "o edital dispensa a data-limite"
    r, o = regime_do_motor(motor)
    if r:
        return r, o
    return regime_por_texto(*textos, privada=privada)


def analisar(reg: str, fechados: set[str] | None = None) -> dict:
    """Para um regime, o que é dispensa provável e o que o regime ainda exige. `fechados` = itens já preenchidos/dispensados."""
    fechados = fechados or set()
    M = matriz(); R = (M.get("regimes") or {}).get(reg) or (M.get("regimes") or {}).get(PADRAO) or {}
    itens = R.get("itens") or {}
    prov = {k: {"situacao": v["situacao"], "porque": v["porque"], "base": v.get("base"), "confianca": v.get("confianca")}
            for k, v in itens.items() if k in ITENS and k not in fechados and v.get("situacao") in ("dispensa_provavel", "nao_se_aplica")}
    exig = [k for k in ITENS if k not in fechados and k not in prov]
    return {"regime": reg if reg in (M.get("regimes") or {}) else PADRAO, "nome": R.get("nome"), "provaveis": prov, "exigidos_em_aberto": exig}


def aplicar_ao_checklist(checklist: dict, reg: str, origem: str | None = None) -> dict:
    """Troca 'falta'/'pend' por 'prov' nos itens que o regime dispensa provavelmente. Não mexe em ok/disp/val/ref."""
    fechados = {k for k, c in checklist.items() if c.get("s") in ("ok", "disp", "val", "ref")}
    a = analisar(reg, fechados)
    for k, d in a["provaveis"].items():
        c = checklist.get(k) or {}
        if c.get("s") in ("falta", "pend", None):
            checklist[k] = {"s": "prov", "v": d["porque"], "t": (d.get("base") or "")[:160], "c": d.get("confianca")}
    return {"regime": a["regime"], "nome": a["nome"], "origem": origem,
            "provaveis": sorted(d for d in a["provaveis"] if checklist.get(d, {}).get("s") == "prov"),
            "exigidos_em_aberto": [k for k in a["exigidos_em_aberto"] if checklist.get(k, {}).get("s") in ("falta", "pend")]}


def no_livro(par: dict | None, mo: dict | None, *textos: str) -> dict | None:
    """Anota em `parametros.doze` do livro, item a item, a dispensa provável dos 'não localizado'. Devolve o regime usado."""
    if not par or not par.get("doze"):
        return None
    reg, origem = regime(mo, *textos, privada=str((mo or {}).get("natureza") or "") == "privada")
    fechados = {k for k, v in par["doze"].items() if v.get("status") != "não localizado"}
    a = analisar(reg, fechados)
    for k, v in par["doze"].items():
        v.pop("dispensa_provavel", None)
        if v.get("status") == "não localizado" and k in a["provaveis"]:
            d = a["provaveis"][k]
            v["dispensa_provavel"] = {"porque": d["porque"], "base": d.get("base"), "confianca": d.get("confianca")}
    par["regime"] = {"id": a["regime"], "nome": a["nome"], "origem": origem}
    par["faltam_exigidos"] = [k for k in ITENS if par["doze"].get(k, {}).get("status") == "não localizado" and k not in a["provaveis"]]
    return par["regime"]
