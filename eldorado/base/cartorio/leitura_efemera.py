"""R35 — a leitura efêmera (titular, 30/10/2026: "não deve existir cópia de nenhum site; o sistema não é repositório de sites
nem de arquivos; os dados são uma trava absoluta").

O texto lido de um site serve ao Cartório para certificar e sai do banco em seguida: ficam o texto da oportunidade (os dados
do livro e as certidões, com o trecho literal do edital) e os endereços (o documento: o site oficial e o de divulgação).
Depois de cada passagem, a leitura com mais de 2 h é expurgada do banco (o evento leitura.expurgada) e o diário efêmero com
mais de 6 h é apagado.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..nucleo.eventos import Diario, pasta_efemera

HORAS_NO_BANCO = 2
HORAS_NO_DIARIO = 6


def expurgar(banco: str | Path, eventos: str | Path, horas: float = HORAS_NO_BANCO, execucao: str = "expurgo-leituras") -> dict[str, int]:
    """Expurga do banco a leitura dos documentos lidos há mais de `horas` (horas=0: todas) e apaga o diário efêmero vencido."""
    corte = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
    con = sqlite3.connect(f"file:{Path(banco)}?mode=ro", uri=True)
    try:
        docs = [
            r[0]
            for r in con.execute(
                "SELECT DISTINCT p.documento_id FROM pagina p JOIN documento d ON d.id = p.documento_id WHERE COALESCE(d.obtido_em, '') < ?", (corte,)
            )
        ]
    finally:
        con.close()
    if docs:
        dia = Diario(eventos, execucao)
        for doc in docs:
            dia.emitir("leitura.expurgada", "leitura-efemera", {"documento_id": doc, "motivo": "R35: a leitura do site não fica guardada"})
    apagados = 0
    ef = pasta_efemera(eventos)
    if ef.exists():
        limite = time.time() - HORAS_NO_DIARIO * 3600
        for a in ef.rglob("*.jsonl"):
            if a.stat().st_mtime < limite:
                a.unlink(missing_ok=True)
                apagados += 1
    # o resíduo da transição: a leitura de site que um código antigo gravou no histórico nas últimas 48 h sai dele
    limpos = 0
    corte_h = time.time() - 48 * 3600
    for a in Path(eventos).rglob("*.jsonl"):
        if a.stat().st_mtime < corte_h:
            continue
        linhas = a.read_bytes().splitlines(keepends=True)
        fica = [x for x in linhas if b'"tipo":"pagina.gravada"' not in x[:200]]
        if len(fica) != len(linhas):
            a.write_bytes(b"".join(fica))
            limpos += len(linhas) - len(fica)
    return {"documentos": len(docs), "diarios_apagados": apagados, "leituras_tiradas_do_historico": limpos}
