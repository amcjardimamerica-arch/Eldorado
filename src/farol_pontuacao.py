"""PONTUAÇÃO DO FAROL — cada edital medido contra o que o titular já selecionou.

Os pesos não são opinião: são as taxas de aprovação observadas nos vereditos do titular
(biblioteca_alexandria/base/pontuacao/criterios.json), refeitas a cada varredura. Critério sem
três casos julgados não pontua — não se inventa peso. A nota vai de 0 a 100 e vem com o porquê.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERIOS = ROOT / "biblioteca_alexandria/base/pontuacao/criterios.json"
PESOS = {"por_tema": 30, "por_esfera": 15, "por_abrangencia": 25, "por_fonte": 10, "por_faixa_de_valor": 10, "exigencias": 10}


def _criterios() -> dict:
    try:
        return json.loads(CRITERIOS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _faixa(v) -> str | None:
    try:
        v = float(str(v).replace(".", "").replace(",", "."))
    except Exception:
        return None
    return "ate_50k" if v <= 50_000 else "50k_200k" if v <= 200_000 else "200k_1M" if v <= 1_000_000 else "acima_1M"


def pontuar(edital: dict) -> dict:
    c = _criterios()
    if not c:
        return {"nota": None, "porque": ["sem critérios: a base ainda não foi construída"]}
    nota, maximo, porque = 0.0, 0.0, []
    chaves = {"por_tema": edital.get("tema") or edital.get("area"), "por_esfera": edital.get("esfera") or edital.get("nivel"),
              "por_abrangencia": edital.get("abrangencia"), "por_fonte": edital.get("fonte_id"),
              "por_faixa_de_valor": _faixa(edital.get("valor"))}
    for crit, valor in chaves.items():
        tab = c.get(crit) or {}
        if valor is None or str(valor) not in tab:
            continue
        t = tab[str(valor)]["taxa"]
        nota += PESOS[crit] * t; maximo += PESOS[crit]
        porque.append(f"{crit[4:]} '{valor}': {int(t * 100)}% de aprovação em {tab[str(valor)]['aprovados'] + tab[str(valor)]['reprovados']} julgados")
    ex = c.get("exigencias_frequentes") or {}
    presentes = [e for e in (edital.get("exigencias") or []) if e in ex]
    if presentes:
        taxa = sum(ex[e]["aprovados"] / max(1, ex[e]["aprovados"] + ex[e]["reprovados"]) for e in presentes) / len(presentes)
        nota += PESOS["exigencias"] * taxa; maximo += PESOS["exigencias"]
        porque.append(f"exigências conhecidas ({len(presentes)}): {int(taxa * 100)}% de aprovação média")
    if not maximo:
        return {"nota": None, "porque": ["nenhum critério com casos julgados se aplica a este edital"]}
    return {"nota": round(100 * nota / maximo), "cobertura": round(maximo / sum(PESOS.values()), 2), "porque": porque}
