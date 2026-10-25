"""O nó de agente do Comandante (a fase 3 do desenho; a engenharia do n8n, titular, 25/10/2026): no início de cada
passagem, o Comandante escolhe quais etapas rodam, pela necessidade medida no Arquivo do Cérebro.

A etapa candidata que NÃO RENDEU NADA nas últimas 6 passagens é pulada — nunca as essenciais (a coleta, as aplicações
aos bancos, a medição, a memória, a conferência, a apresentação) e nunca mais de 3 passagens seguidas (a garantia).
Em SOMBRA enquanto o parâmetro comandante.aciona não for "sim": registra o que pularia e por quê, sem pular; como a etapa
roda mesmo assim, o Aprendizado avalia se a escolha estava certa (rodou e não rendeu: pular estava certo)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANDIDATAS = [
    "unir_repetidos",
    "encaminhar",
    "espiao",
    "originais",
    "validar",
    "analise_externa",
    "farol",
    "analise",
    "completude",
    "aprender",
    "reler_documentos",
]
JANELA = 6
SEGUIDAS_MAX = 3


def rendeu(saida: str | None) -> bool:
    """A etapa trouxe algo: uma saída com algum número maior que zero ou alguma lista não vazia."""
    try:
        itens = json.loads(saida or "[]")
    except ValueError:
        return bool(saida)

    def algo(v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return v > 0
        if isinstance(v, (list, dict)):
            return any(algo(x) for x in (v.values() if isinstance(v, dict) else v))
        return False

    return any(algo(x) for x in (itens if isinstance(itens, list) else [itens]))


def escolher(cer: sqlite3.Connection) -> list[dict[str, Any]]:
    """As etapas que o Comandante pularia agora, cada uma com o motivo."""
    saida = []
    for no in CANDIDATAS:
        hist = cer.execute(
            "SELECT estado, saida FROM execucao_passo WHERE no = ? AND estado IN ('concluido', 'pulado') ORDER BY em DESC LIMIT ?",
            (no, JANELA + SEGUIDAS_MAX),
        ).fetchall()
        rodadas = [h for h in hist if h[0] == "concluido"][:JANELA]
        seguidas = 0
        for est, _s in hist:
            if est != "pulado":
                break
            seguidas += 1
        if len(rodadas) < JANELA or seguidas >= SEGUIDAS_MAX:
            continue
        if not any(rendeu(s) for _e, s in rodadas):
            saida.append(
                {
                    "no": no,
                    "motivo": f"nada rendeu nas últimas {JANELA} passagens em que rodou"
                    + (f" (já pulada {seguidas} vez(es) seguidas; o máximo é {SEGUIDAS_MAX})" if seguidas else ""),
                }
            )
    return saida


def no_comandante_escolher(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C2): escolhe as etapas desta passagem; em sombra, só registra."""
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if not p.exists():
        return []
    cer = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'comandante_decisao'").fetchone():
            return []
        from .parametros import valor

        aciona = str(valor(cer, "comandante", "aciona", "nao")).lower() == "sim"
        pular = escolher(cer)
    finally:
        cer.close()
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for x in pular:
        contexto.diario.emitir(
            "comandante.decidiu",
            "comandante",
            {
                "em": agora,
                "etapa": "passagem",
                "acao": "pular a etapa" if aciona else "pularia a etapa (em sombra)",
                "alvo": x["no"],
                "motivo": x["motivo"],
                "nota": None,
                "politica": "necessidade medida",
                "contexto": json.dumps({"execucao": contexto.execucao, "aciona": aciona}),
            },
        )
    r = {"pular": [x["no"] for x in pular], "aciona": aciona}
    if aciona and pular:
        r["__pular__"] = [x["no"] for x in pular]
    return [r]
