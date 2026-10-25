"""Os parâmetros do Comandante (as etapas C7 e C9; titular, 25/10/2026). Cada parâmetro de cada etapa vive no Arquivo do
Cérebro, com a versão e a cópia anterior; toda mudança feita em funcionamento é CONFERIDA 20 MINUTOS DEPOIS: se a versão
conferida foi sobrescrita (outra versão sem a sua própria conferência) ou apagada, abre o alarme e o valor é restaurado.
(A titular: "pelo cérebro pode atualizar em funcionamento desde que verifique em 20 minutos se a atualização foi
sobrescrita ou apagada".)"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONFERIR_MIN = 20
# os parâmetros que o Comandante mantém, com a origem do valor inicial
INICIAIS = {
    ("pilotos", "carga_maxima"): ("85", "regra da titular: a carga perto de 85%"),
    ("pilotos", "intervalo_s"): ("3", "regra da titular: 3 segundos entre as missões"),
}


def valor(cer: sqlite3.Connection, etapa: str, chave: str, padrao: Any = None) -> Any:
    try:
        r = cer.execute("SELECT valor FROM parametro WHERE etapa = ? AND chave = ? ORDER BY versao DESC LIMIT 1", (etapa, chave)).fetchone()
    except sqlite3.Error:
        return padrao
    return r[0] if r else padrao


def definir(cer: sqlite3.Connection, diario, etapa: str, chave: str, novo: str, origem: str, agora: datetime | None = None) -> bool:
    agora = agora or datetime.now(timezone.utc)
    r = cer.execute("SELECT versao, valor FROM parametro WHERE etapa = ? AND chave = ? ORDER BY versao DESC LIMIT 1", (etapa, chave)).fetchone()
    if r and r[1] == novo:
        return False
    versao = (r[0] + 1) if r else 1
    iso = agora.isoformat(timespec="seconds")
    diario.emitir(
        "parametro.definido",
        "comandante",
        {"etapa": etapa, "chave": chave, "versao": versao, "valor": novo, "anterior": r[1] if r else None, "origem": origem, "em": iso},
    )
    diario.emitir(
        "conferencia.agendada",
        "comandante",
        {
            "etapa": etapa,
            "chave": chave,
            "versao": versao,
            "verificar_em": (agora + timedelta(minutes=CONFERIR_MIN)).isoformat(timespec="seconds"),
            "estado": "aguardando",
            "conferida_em": None,
        },
    )
    return True


def conferir(cer: sqlite3.Connection, diario, agora: datetime | None = None) -> dict[str, int]:
    """As conferências vencidas: intacta, ou sobrescrita (alarme + restauração da versão conferida)."""
    agora = agora or datetime.now(timezone.utc)
    iso = agora.isoformat(timespec="seconds")
    conta = {"intactas": 0, "restauradas": 0}
    for cid, etapa, chave, versao in cer.execute(
        "SELECT id, etapa, chave, versao FROM conferencia WHERE estado = 'aguardando' AND verificar_em <= ?", (iso,)
    ).fetchall():
        conferida = cer.execute("SELECT valor FROM parametro WHERE etapa = ? AND chave = ? AND versao = ?", (etapa, chave, versao)).fetchone()
        ultima = cer.execute(
            "SELECT versao, valor, origem FROM parametro WHERE etapa = ? AND chave = ? ORDER BY versao DESC LIMIT 1", (etapa, chave)
        ).fetchone()
        outra_conferida = (
            ultima
            and ultima[0] > versao
            and cer.execute("SELECT 1 FROM conferencia WHERE etapa = ? AND chave = ? AND versao = ?", (etapa, chave, ultima[0])).fetchone()
        )
        if conferida and ultima and (ultima[0] == versao or outra_conferida):
            diario.emitir("conferencia.feita", "comandante", {"id": cid, "estado": "intacta", "conferida_em": iso})
            conta["intactas"] += 1
            continue
        motivo = "apagada" if not conferida else f"sobrescrita pela versão {ultima[0]} ({ultima[2]})"
        diario.emitir(
            "alarme.aberto",
            "comandante",
            {
                "gravidade": "alta",
                "modulo": "comandante:conferencia",
                "aberto_em": iso,
                "mensagem": f"o parâmetro {etapa}.{chave} (versão {versao}) foi {motivo} em menos de 20 minutos: "
                "a regra proíbe; o valor conferido foi restaurado",
            },
        )
        if conferida:
            nova = (ultima[0] if ultima else versao) + 1
            diario.emitir(
                "parametro.definido",
                "comandante",
                {
                    "etapa": etapa,
                    "chave": chave,
                    "versao": nova,
                    "valor": conferida[0],
                    "anterior": ultima[1] if ultima else None,
                    "origem": "restauração da conferência",
                    "em": iso,
                },
            )
        diario.emitir("conferencia.feita", "comandante", {"id": cid, "estado": "restaurada", "conferida_em": iso})
        conta["restauradas"] += 1
    return conta


def no_conferir(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C7 e C9): os parâmetros iniciais e as conferências de 20 minutos."""
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    if not p.exists():
        return []
    cer = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'parametro'").fetchone():
            return []
        iniciais = sum(definir(cer, contexto.diario, e, k, v, o) for (e, k), (v, o) in INICIAIS.items() if valor(cer, e, k) is None)
        return [{"parametros_iniciais": iniciais, **conferir(cer, contexto.diario)}]
    finally:
        cer.close()
