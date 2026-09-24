#!/usr/bin/env python3
"""AGENDA DOS MOTORES — quais motores rodam AGORA. Chamado de hora em hora pelo workflow
agenda-motores (minutos :23 e :53). Imprime os ids separados por vírgula, para a coleta
rodar só eles (MOTORES_FONTES). Motor de coleta local não sai daqui: roda no computador do
titular. Com --tudo, lista a agenda inteira."""
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def devidos(agora_utc: datetime | None = None) -> list[str]:
    ag = json.loads((RAIZ / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
    est = RAIZ / "estado/sensores.json"
    ult = (json.loads(est.read_text(encoding="utf-8")).get("sensores") or {}) if est.exists() else {}
    brt = (agora_utc or datetime.now(timezone.utc)) - timedelta(hours=3)
    faixa = "23" if brt.minute < 38 else "53"
    saida = []
    for mid, a in ag.items():
        if a.get("coleta") == "local" or a.get("horarios_brt") == "contínuo":
            continue
        horas = [h.strip() for h in str(a["horarios_brt"]).split(",")]
        if not any(h == f"{brt.hour:02d}:{faixa}" for h in horas):
            continue
        d = str(a.get("dias") or "todos")
        if d.startswith("dia "):
            if brt.day != int(d.split()[1]): continue
        elif d not in ("todos",) and DIAS[brt.weekday()] not in d.split(","):
            continue
        cad = a.get("cadencia_dias") or 1
        u = (ult.get(mid) or {}).get("ultima")
        if cad >= 2 and u:                                  # cadência longa: não repete antes da hora
            try:
                if datetime.now(timezone.utc) - datetime.fromisoformat(u.replace("Z", "+00:00")) < timedelta(days=cad - 0.5):
                    continue
            except ValueError:
                pass
        saida.append(mid)
    return saida


if __name__ == "__main__":
    if "--tudo" in sys.argv:
        ag = json.loads((RAIZ / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        for mid, a in sorted(ag.items(), key=lambda kv: kv[1]["horarios_brt"]):
            print(f"{a['horarios_brt']:12} {a['dias']:18} {mid}")
    else:
        print(",".join(devidos()))
