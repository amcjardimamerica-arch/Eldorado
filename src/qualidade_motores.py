"""PLACAR DE QUALIDADE DOS MOTORES (titular, 17/10/2026).

Para cada motor: o que a triagem barrou na entrada e o que o Claude no Chrome decidiu sobre o que ele trouxe (válida,
encerrada, ruído, fora do perfil, duplicata) e a média de itens certificados das suas oportunidades abertas. É com este
placar que se sabe qual motor é eficiente e qual precisa de correção na fonte.
"""
from __future__ import annotations

import collections
import json
import re

from .nucleo import ROOT

SAIDA = ROOT / "docs/dados/qualidade_motores.json"
VALIDAS = {"ouro", "prata", "bronze", "validacao_manual", "pendente"}


def _j(p, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _familia(m) -> str:
    m = re.sub(r"^motor\s+", "", str(m or "")).strip()
    m = re.sub(r"outras-oportunidades-\d+", "outras-oportunidades", m)
    m = re.sub(r"agregadores\s*·.*", "agregadores", m)
    return m or "(sem motor)"


def montar(gravar: bool = True) -> dict:
    ver = (_j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json", {}) or {}).get("vereditos") or {}
    tri = (_j(ROOT / "estado/triagem_entrada.json", {}) or {}).get("por_motor") or {}
    regs = (_j(ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json", {}) or {}).get("registros") or []
    m: dict = collections.defaultdict(lambda: {"vereditos": collections.Counter(), "barrados_na_entrada": 0,
                                               "abertas": 0, "itens_certificados": 0, "completas": 0})
    for v in ver.values():
        if (v or {}).get("motor"):
            m[_familia(v["motor"])]["vereditos"][v.get("veredito")] += 1
    for k, n in tri.items():
        m[_familia(k)]["barrados_na_entrada"] += int(n)
    for r in regs:
        if r.get("estado") == "fechada" or r.get("arquivada"):
            continue
        f = m[_familia(r.get("origem"))]
        n = sum(1 for x in (r.get("itens") or {}).values() if isinstance(x, dict) and x.get("estado") in ("comprovado", "dispensado"))
        f["abertas"] += 1; f["itens_certificados"] += n; f["completas"] += 1 if n >= 12 else 0
    out = []
    for nome, f in m.items():
        nv = sum(f["vereditos"].values())
        out.append({"motor": nome, "abertas": f["abertas"],
                    "itens_por_oportunidade": round(f["itens_certificados"] / f["abertas"], 1) if f["abertas"] else None,
                    "completas_pct": round(100 * f["completas"] / f["abertas"]) if f["abertas"] else None,
                    "vereditos": nv, "validas_pct": round(100 * sum(f["vereditos"][k] for k in VALIDAS) / nv) if nv else None,
                    "descartadas_no_chrome_pct": round(100 * (nv - sum(f["vereditos"][k] for k in VALIDAS)) / nv) if nv else None,
                    "barrados_na_entrada": f["barrados_na_entrada"], "por_veredito": dict(f["vereditos"])})
    out.sort(key=lambda x: -(x["abertas"] + x["vereditos"]))
    res = {"regra": "eficiente = traz oportunidade válida, com o edital e os 12 itens; o placar orienta a correção na fonte",
           "vereditos_com_motor": sum(1 for v in ver.values() if (v or {}).get("motor")), "vereditos": len(ver), "motores": out}
    if gravar:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: v for k, v in res.items() if k != "motores"} | {"motores": len(out)}
