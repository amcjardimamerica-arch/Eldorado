"""ITINERÁRIO DAS PESQUISAS (titular, 02/10/2026) — config/itinerario.json

Horários por família, no ritmo de publicação de cada tipo de fonte. Regra: a PRIMEIRA passagem do dia fecha o DIA ANTERIOR
inteiro (D-1); as seguintes pegam o que sai ao longo do dia. Todo registro leva a data ORIGINAL da publicação e a data da
CONSULTA. A agenda só dispara em HH:23 e HH:53. Indexadores (fluxo próprio), coleta local, contínuos e Pilotos não mudam.
aplicar() é idempotente e guarda o horário antigo de cada motor (reversível).
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/itinerario.json"
AG = ROOT / "config/agenda_motores.json"
SK = ROOT / "config/skills_motores.json"
LEGIS = re.compile(r"camara|alego|congresso|assembleia|legislativ")


def familia(mid: str, sk: dict) -> str:
    if LEGIS.search(mid):
        return "legislativo"
    return (sk.get(mid) or {}).get("familia") or "?"


def aplicar(gravar: bool = True) -> dict:
    cfg = json.loads(CFG.read_text(encoding="utf-8")); A = json.loads(AG.read_text(encoding="utf-8")); sk = json.loads(SK.read_text(encoding="utf-8"))["motores"]
    mudou, antes = [], cfg.setdefault("horarios_anteriores", {})
    for mid, a in A["motores"].items():
        if mid.startswith("idx-") or a.get("coleta") == "local" or a.get("horarios_brt") == "contínuo" or str(a.get("dias", "")).startswith("inativ"):
            continue
        fam = familia(mid, sk); novo = (cfg["familias"].get(fam) or {}).get("horarios_brt")
        if not novo or a.get("horarios_brt") == novo:
            continue
        antes.setdefault(mid, a.get("horarios_brt"))
        a["horarios_brt"] = novo
        a["por_que_esta_hora"] = f"itinerário 02/10 ({fam}): {cfg['familias'][fam]['por_que']}; a 1ª passagem fecha o dia anterior (D-1)"
        mudou.append((mid, fam, antes[mid], novo))
    if gravar:
        cfg["aplicado_em"] = date.today().isoformat()
        CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
        AG.write_text(json.dumps(A, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"motores_ajustados": len(mudou), "mudancas": mudou}


if __name__ == "__main__":
    r = aplicar()
    print(f"{r['motores_ajustados']} motor(es) ajustado(s)")
    for m in r["mudancas"]:
        print(f"  {m[0]:34} {m[1]:18} {m[2]} → {m[3]}")
