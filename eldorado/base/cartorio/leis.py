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


ORCAMENTO_S, LIMITE_LEI_S = 120.0, 30.0   # 23/11/2026 (C-06): o acompanhamento das leis com prazo (sem ele, 2 h 55 presas no nó)


def _ler_com_limite(ler: Callable[[str], str | None], url: str, limite_s: float) -> str | None:
    """A leitura da lei com tempo limite: a que não responde segue sozinha em segundo plano e fica para a próxima passagem."""
    import threading
    saida: dict = {}

    def _ler():
        try:
            saida["t"] = ler(url)
        except Exception as e:  # noqa: BLE001
            saida["e"] = e
    t = threading.Thread(target=_ler, daemon=True)
    t.start()
    t.join(limite_s)
    if t.is_alive():
        raise TimeoutError(f"a lei não respondeu em {limite_s:.0f} s")
    if "e" in saida:
        raise saida["e"]
    return saida.get("t")


def acompanhar(con: sqlite3.Connection, diario, ler: Callable[[str], str | None], agora: datetime | None = None,
               orcamento_s: float = ORCAMENTO_S, limite_lei_s: float = LIMITE_LEI_S) -> dict[str, Any]:
    agora = agora or datetime.now(timezone.utc)
    corte = (agora - timedelta(days=DIAS)).isoformat()
    try:
        leis = con.execute("SELECT id, esfera, numero, ementa, situacao, link_oficial FROM lei WHERE link_oficial IS NOT NULL AND link_oficial <> '' "
                           "AND COALESCE(atualizada_em, '') < ? ORDER BY atualizada_em LIMIT ?", (corte, LIMITE)).fetchall()
        sem_link = con.execute("SELECT COUNT(*) FROM lei WHERE link_oficial IS NULL OR link_oficial = ''").fetchone()[0]
    except sqlite3.Error:
        return {"conferidas": 0}
    import time
    feitas, mudaram, adiadas, fim = 0, [], 0, time.monotonic() + orcamento_s
    for lid, esfera, numero, ementa, situacao, link in leis:
        restante = fim - time.monotonic()
        if restante <= 1:                           # C-06: o orçamento acabou — as demais ficam para a próxima passagem
            adiadas += 1
            continue
        try:
            texto = _ler_com_limite(ler, link, min(limite_lei_s, restante)) or ""
        except Exception:  # noqa: BLE001 — a lei que não abriu (ou não respondeu a tempo) fica para a próxima passagem
            adiadas += 1
            continue
        if not texto:
            continue
        nova = "revogada" if REVOGADA.search(texto[:4000]) else (situacao if situacao and situacao != "revogada" else "vigente")
        diario.emitir("lei.registrada", "cartorio", {"id": lid, "esfera": esfera, "numero": numero, "ementa": ementa, "situacao": nova,
                                                     "link_oficial": link, "atualizada_em": agora.isoformat(timespec="seconds")})
        feitas += 1
        if nova != situacao:
            mudaram.append(f"{numero or lid}: {situacao} → {nova}")
    return {"conferidas": feitas, "mudaram": mudaram, "leis_sem_link": sem_link, "adiadas": adiadas}
