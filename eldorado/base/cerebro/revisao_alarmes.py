"""O ciclo de vida dos alarmes (titular, 25/10/2026: a sala mostrava alarmes antigos, de causas já corrigidas, porque o
sistema abria alarmes e nada os fechava). A cada passagem, cada alarme aberto é conferido e fechado se a causa se resolveu:
  a falha de um nó          → o nó voltou a concluir depois do alarme
  a recusa de um evento     → "UNIQUE constraint failed": aquilo já estava no banco (a união, o livro, o achado): duplicata
  a carga acima de 85%      → as leituras do servidor depois do alarme estão abaixo de 85%
O que não se resolveu continua aberto (e aceso na sala)."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def revisar(cer: sqlite3.Connection) -> list[tuple[int, str]]:
    """Os alarmes resolvidos: [(o id, o motivo do fechamento)]."""
    volta = dict(cer.execute("SELECT no, MAX(em) FROM execucao_passo WHERE estado = 'concluido' GROUP BY no").fetchall())
    leituras = cer.execute("SELECT em, MAX(processador, memoria) FROM maquina ORDER BY em").fetchall() if \
        cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'maquina'").fetchone() else []
    fechar = []
    for aid, modulo, msg, aberto in cer.execute("SELECT id, modulo, mensagem, aberto_em FROM alarme WHERE fechado_em IS NULL"):
        msg, aberto = msg or "", aberto or ""
        m = re.search(r"o nó ([a-z_]+) falhou", msg)
        if m and volta.get(m.group(1), "") > aberto:
            fechar.append((aid, f"o nó {m.group(1)} voltou a concluir"))
        elif modulo == "gravador" and "UNIQUE constraint failed" in msg:
            fechar.append((aid, "duplicata: aquilo já estava no banco"))
        elif modulo == "governador" and "acima de 85%" in msg:
            depois = [c for em, c in leituras if (em or "") > aberto]
            if depois and all((c or 0) < 0.85 for c in depois[-3:]):
                fechar.append((aid, "a carga voltou abaixo de 85%"))
    return fechar


def no_revisar_alarmes(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o início): fecha os alarmes cuja causa se resolveu."""
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if not p.exists():
        return [{"fechados": 0}]
    cer = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        fechar = revisar(cer)
    finally:
        cer.close()
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for aid, _motivo in fechar:
        contexto.diario.emitir("alarme.fechado", "revisao", {"id": aid, "fechado_em": agora})
    return [{"fechados": len(fechar)}]
