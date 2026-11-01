"""A retenção da telemetria no Cérebro (titular, 01/11/2026): os dados da operação ficam 30 dias, completos, para o
Comandante aprender e propor melhorias; o que passa desse prazo sai — no Cérebro e na pasta operacao/ (guardada no
repositório: os dias passados são compactados em .jsonl.gz e os de mais de 30 dias são apagados)."""
from __future__ import annotations

import gzip
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

DIAS = 30
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
    apagados = compactados = 0
    op = pasta_operacao(pasta_eventos)
    if op.exists():
        hoje = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        limite_dias = (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y/%m/%d")
        recente = time.time() - 2 * 3600
        for a in sorted(op.rglob("*.jsonl*")):
            dia = "/".join(a.relative_to(op).parts[:3])
            if dia < limite_dias:
                a.unlink(missing_ok=True)
                apagados += 1
            elif a.name.endswith(".jsonl") and dia < hoje and a.stat().st_mtime < recente:
                destino = a.with_name(a.name + ".gz")
                destino.write_bytes(gzip.compress(a.read_bytes(), 6))
                a.unlink()
                compactados += 1
        for d in sorted((x for x in op.rglob("*") if x.is_dir()), key=lambda x: -len(x.parts)):
            if not any(d.iterdir()):
                d.rmdir()
    saida["arquivos_apagados"] = apagados
    saida["arquivos_compactados"] = compactados
    return saida
