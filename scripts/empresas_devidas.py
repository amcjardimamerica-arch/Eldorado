#!/usr/bin/env python3
"""MOTORES 20 e 21 (empresas) — a semana venceu? (teste do motor 20, 03/10/2026)

Os motores de empresas rodam no fluxo 01 pelo agendamento de domingo 06h UTC. O GitHub pulou o domingo 27/09 e não
havia recuperação: o maestro e o fluxo 22 deixam esses dois motores de fora. Este script diz ao fluxo 22 se a última
rotina semanal tem mais de 7,5 dias — então o próprio fluxo 22 roda a rotina (uma vez; a seguinte já a vê em dia).

    python scripts/empresas_devidas.py      # imprime "sim" ou "nao" na última linha
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LOG = RAIZ / "estado/empresas_semanal.jsonl"


def ultima_semanal() -> datetime | None:
    if not LOG.exists():
        return None
    ult = None
    for linha in LOG.read_text(encoding="utf-8").splitlines():
        try:
            em = datetime.fromisoformat(json.loads(linha)["em"].replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            continue
        ult = em if not ult or em > ult else ult
    return ult


def devida(agora: datetime | None = None, dias: float = 7.5) -> bool:
    agora = agora or datetime.now(timezone.utc)
    u = ultima_semanal()
    return u is None or agora - u > timedelta(days=dias)


if __name__ == "__main__":
    u = ultima_semanal()
    print(f"última rotina semanal de empresas: {u.isoformat() if u else 'nunca'}", file=sys.stderr)
    print("sim" if devida() else "nao")
