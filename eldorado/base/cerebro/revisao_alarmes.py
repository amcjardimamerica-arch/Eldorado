"""O ciclo de vida dos alarmes (titular, 25/10/2026: a sala mostrava alarmes antigos, de causas já corrigidas, porque o
sistema abria alarmes e nada os fechava). A cada passagem, cada alarme aberto é conferido e fechado se a causa se resolveu:
  a falha de um nó          → o nó voltou a concluir depois do alarme
  a recusa de um evento     → "UNIQUE constraint failed": aquilo já estava no banco (a união, o livro, o achado): duplicata
  a carga acima de 85%      → as leituras do servidor depois do alarme estão abaixo de 85%
  o veredito recusado (R41) → o veredito daquele lote foi importado (08/11/2026: o de 05/11 ficava aceso para sempre)
  10/11/2026 (parecer da Sala, passo 4): a carga do Comandante (comandante:carga), o motor preso além do orçamento que voltou
  a ler, o voo do Interceptador que caiu e o piloto voltou a voar, e a triagem aprendida recusada pela R41
O que não se resolveu continua aberto (e aceso na sala)."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def revisar(cer: sqlite3.Connection, expurgo: Path | None = None) -> list[tuple[int, str]]:
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
        elif expurgo is not None and (lt := re.search(r"recusado \(R41[^)]*\).*?do (lote-chrome-documentos-[\w-]+)", msg)) and \
                (expurgo / "vereditos" / "importados" / f"veredito-{lt.group(1)}.json").exists():
            fechar.append((aid, f"o veredito do {lt.group(1)} foi importado"))
        elif modulo in ("governador", "comandante:carga") and "acima de 85%" in msg:
            # 10/11/2026 (parecer, passo 4): também o alarme do Comandante (o mesmo aviso, outro módulo): 12 abertos desde 28/10
            depois = [c for em, c in leituras if (em or "") > aberto]
            if depois and all((c or 0) < 0.85 for c in depois[-3:]):
                fechar.append((aid, "a carga voltou abaixo de 85%"))
        elif modulo == "regencia:coleta" and "preso(s) além do orçamento" in msg:
            # 10/11/2026 (parecer, passo 4): o motor abandonado numa passagem que depois voltou a ler sem erro
            nomes = [x.strip() for x in msg.rsplit(":", 1)[-1].split(",") if x.strip()]
            if nomes and all(_leu_depois(cer, n, aberto) for n in nomes):
                fechar.append((aid, f"o(s) motor(es) voltaram a ler sem erro: {', '.join(nomes)}"))
        elif modulo == "piloto:interceptador" and "falhou" in msg:
            # 10/11/2026 (parecer, passo 4): o voo que caiu, com voos avaliados depois dele (o piloto voltou a voar)
            if _voou_depois(cer, aberto):
                fechar.append((aid, "o Interceptador voltou a voar e os voos seguintes foram avaliados"))
        elif modulo == "analise-externa" and "triagem-aprendida" in msg:
            # 10/11/2026 (parecer, passo 1; R53): a triagem do próprio sistema não passa mais pela conferência do Chrome (R41)
            fechar.append((aid, "a triagem aprendida é do sistema: a entrega completa do Chrome (R41) não se aplica a ela"))
    return fechar


def _leu_depois(cer: sqlite3.Connection, motor: str, desde: str) -> bool:
    try:
        return cer.execute("SELECT 1 FROM execucao_motor WHERE motor = ? AND inicio > ? AND fim IS NOT NULL AND erro IS NULL LIMIT 1",
                           (motor, desde)).fetchone() is not None
    except sqlite3.Error:
        return False


def _voou_depois(cer: sqlite3.Connection, desde: str) -> bool:
    try:
        return cer.execute("SELECT 1 FROM comandante_decisao WHERE etapa = 'interceptador' AND em > ? AND recompensa IS NOT NULL LIMIT 1",
                           (desde,)).fetchone() is not None
    except sqlite3.Error:
        return False


def no_revisar_alarmes(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o início): fecha os alarmes cuja causa se resolveu."""
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if not p.exists():
        return [{"fechados": 0}]
    cer = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        fechar = revisar(cer, Path(parametros.get("expurgo", "verificacao/expurgo")))
    finally:
        cer.close()
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for aid, _motivo in fechar:
        contexto.diario.emitir("alarme.fechado", "revisao", {"id": aid, "fechado_em": agora})
    return [{"fechados": len(fechar)}]
