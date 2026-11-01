"""A retenção da telemetria no Cérebro (titular, 01/11/2026): os dados da operação ficam 30 dias, completos, para o
Comandante aprender e propor melhorias; o que passa desse prazo sai. Os arquivos do diário da operação (já aplicados ao
Cérebro) saem depois de 48 horas."""
from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

DIAS = 30
HORAS_ARQUIVO = 48
TABELAS = ("medicao", "comandante_decisao", "execucao_passo", "memoria", "recibo", "medicao_arquivos", "sala_medicao")
SEM_DATA_MAX = 200_000   # a tabela sem coluna de data guarda as linhas mais recentes


def reter(cerebro: str | Path, pasta_eventos: str | Path, dias: int = DIAS) -> dict[str, int]:
    from ..nucleo.eventos import pasta_operacao

    saida: dict[str, int] = {}
    corte = (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat()
    con = sqlite3.connect(str(cerebro), timeout=30)
    try:
        for t in TABELAS:
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
            if not cols:
                continue
            if "em" in cols:
                n = con.execute(f"DELETE FROM {t} WHERE em < ?", (corte,)).rowcount
            else:
                n = con.execute(f"DELETE FROM {t} WHERE rowid <= (SELECT MAX(rowid) FROM {t}) - ?", (SEM_DATA_MAX,)).rowcount
            saida[t] = max(0, n)
        con.commit()
    finally:
        con.close()
    apagados = 0
    op = pasta_operacao(pasta_eventos)
    if op.exists():
        limite = time.time() - HORAS_ARQUIVO * 3600
        for a in op.rglob("*.jsonl"):
            if a.stat().st_mtime < limite:
                a.unlink(missing_ok=True)
                apagados += 1
    saida["arquivos_apagados"] = apagados
    return saida
