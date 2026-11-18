"""17/11/2026 (C-21): o acompanhamento das leis — as 27 leis tinham a mesma data de atualização (22/10, a importação) e nada
conferia o andamento. A cada passagem, até LIMITE leis com link oficial e sem conferência há DIAS dias são lidas pela escada:
a página diz se a lei está revogada; a situação e a data são gravadas (lei.registrada)."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

LIMITE, DIAS = 5, 7
REVOGADA = re.compile(r"(?i)\b(revogad[ao]|revoga[çc][ãa]o total)\b")


def acompanhar(con: sqlite3.Connection, diario, ler: Callable[[str], str | None], agora: datetime | None = None) -> dict[str, Any]:
    agora = agora or datetime.now(timezone.utc)
    corte = (agora - timedelta(days=DIAS)).isoformat()
    try:
        leis = con.execute("SELECT id, esfera, numero, ementa, situacao, link_oficial FROM lei WHERE link_oficial IS NOT NULL AND link_oficial <> '' "
                           "AND COALESCE(atualizada_em, '') < ? ORDER BY atualizada_em LIMIT ?", (corte, LIMITE)).fetchall()
        sem_link = con.execute("SELECT COUNT(*) FROM lei WHERE link_oficial IS NULL OR link_oficial = ''").fetchone()[0]
    except sqlite3.Error:
        return {"conferidas": 0}
    feitas, mudaram = 0, []
    for lid, esfera, numero, ementa, situacao, link in leis:
        try:
            texto = ler(link) or ""
        except Exception:  # noqa: BLE001 — a lei que não abriu fica para a próxima passagem
            continue
        if not texto:
            continue
        nova = "revogada" if REVOGADA.search(texto[:4000]) else (situacao if situacao and situacao != "revogada" else "vigente")
        diario.emitir("lei.registrada", "cartorio", {"id": lid, "esfera": esfera, "numero": numero, "ementa": ementa, "situacao": nova,
                                                     "link_oficial": link, "atualizada_em": agora.isoformat(timespec="seconds")})
        feitas += 1
        if nova != situacao:
            mudaram.append(f"{numero or lid}: {situacao} → {nova}")
    return {"conferidas": feitas, "mudaram": mudaram, "leis_sem_link": sem_link}
