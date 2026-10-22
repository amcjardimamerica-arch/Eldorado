"""O ciclo de aprendizado: temporário (30 dias) → permanente, se funcionou; arquivado, se falhou; vencido, sai.

O uso e o resultado decidem (conceito do Hermes: skills com contagem de uso e resultado). Nada da Biblioteca é
tocado: o temporário vive só no Cérebro.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ..nucleo.eventos import Diario, agora


class Aprendizado:
    def __init__(self, diario: Diario, retencao_dias: int = 30, usos_minimos: int = 3, promover_se: float = 0.7, arquivar_se: float = 0.3):
        if not 1 <= retencao_dias <= 30:
            raise ValueError("o temporário dura de 1 a 30 dias")
        self.diario, self.retencao = diario, retencao_dias
        self.usos_minimos, self.promover_se, self.arquivar_se = usos_minimos, promover_se, arquivar_se

    def registrar(self, modulo: str, o_que: str, evidencia: str | None = None, quando: datetime | None = None) -> dict[str, Any]:
        q = quando or datetime.now(timezone.utc)
        dados = {"modulo": modulo, "o_que": o_que, "evidencia": evidencia, "usos": 0, "resultado": None,
                 "criado_em": q.isoformat(), "expira_em": (q + timedelta(days=self.retencao)).isoformat()}
        self.diario.emitir("aprendizado.registrado", "aprendizado", dados)
        return dados

    def usar(self, id: int, usos: int, resultado: float) -> None:
        self.diario.emitir("aprendizado.usado", "aprendizado", {"id": id, "usos": usos, "resultado": resultado})

    def avaliar(self, temporarios: list[dict[str, Any]], quando: datetime | None = None) -> dict[str, list[int]]:
        """Decide o destino de cada temporário. Devolve os ids promovidos, arquivados e vencidos."""
        q = quando or datetime.now(timezone.utc)
        saida: dict[str, list[int]] = {"promovidos": [], "arquivados": [], "vencidos": []}
        for t in temporarios:
            usos, resultado = t.get("usos") or 0, t.get("resultado")
            if usos >= self.usos_minimos and resultado is not None and (resultado >= self.promover_se or resultado <= self.arquivar_se):
                arquivado = resultado <= self.arquivar_se
                self.diario.emitir("aprendizado.promovido", "aprendizado", {
                    "modulo": t.get("modulo"), "o_que": t["o_que"], "promovido_em": q.isoformat(), "origem_temporario": t["id"],
                    "medicao_que_provou": f"{usos} usos, resultado {resultado:.2f}", "arquivado": int(arquivado)})
                self.diario.emitir("aprendizado.expirado", "aprendizado", {"id": t["id"]})
                saida["arquivados" if arquivado else "promovidos"].append(t["id"])
            elif datetime.fromisoformat(t["expira_em"]) <= q:
                self.diario.emitir("aprendizado.expirado", "aprendizado", {"id": t["id"]})
                saida["vencidos"].append(t["id"])
        return saida


def no_aprendizado(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    p = Path(parametros.get("dados", "dados")) / "cerebro.db"
    temporarios: list[dict[str, Any]] = []
    if p.exists():
        con = sqlite3.connect(p)
        con.row_factory = sqlite3.Row
        try:
            temporarios = [dict(r) for r in con.execute("SELECT * FROM aprendizado_temporario")]
        finally:
            con.close()
    r = Aprendizado(contexto.diario).avaliar(temporarios)
    return [{k: len(v) for k, v in r.items()} | {"avaliados": len(temporarios), "em": agora()}]
