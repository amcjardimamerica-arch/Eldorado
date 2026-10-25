"""O Aprendizado avalia as decisões do Comandante (a etapa A4): quando o resultado aparece, cada decisão recebe a sua
recompensa, e a política do Comandante reaprende com ela na passagem seguinte.
  coleta: o motor escolhido trouxe achado aceito naquele dia (todo motor lê todo dia, então o resultado sempre aparece);
  interceptador: o voo autorizado registrou passos do plano de voo com material para o livro;
  espiao: a família escolhida voou depois da decisão e a missão achou algo (a família que não voou em 24 h não é avaliada:
          a recompensa fica vazia, com o motivo)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def avaliar(dados: Path, diario, agora: datetime | None = None) -> dict[str, int]:
    agora = agora or datetime.now(timezone.utc)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    conta = {"avaliadas": 0, "acertos": 0, "sem_execucao": 0}
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'comandante_decisao'").fetchone():
            return conta
        maduras = (agora - timedelta(hours=2)).isoformat()
        for did, etapa, alvo, em in cer.execute(
            "SELECT id, etapa, alvo, em FROM comandante_decisao WHERE avaliada_em IS NULL AND em < ?", (maduras,)
        ):
            rec, resultado = None, None
            if etapa == "coleta":
                dia = em[:10]
                n = bib.execute(
                    "SELECT COUNT(*) FROM achado WHERE motor = ? AND decisao = 'aceito' AND substr(encontrado_em, 1, 10) = ?", (alvo, dia)
                ).fetchone()[0]
                if em[:10] < agora.date().isoformat():
                    rec, resultado = (1.0 if n else 0.0), f"{n} achado(s) aceito(s) em {dia}"
            elif etapa == "espiao":
                m = cer.execute(
                    "SELECT COUNT(*), SUM(CASE WHEN achados > 0 THEN 1 ELSE 0 END) FROM espiao_missao WHERE familia = ? AND em > ?", (alvo, em)
                ).fetchone()
                if m[0]:
                    rec, resultado = (1.0 if (m[1] or 0) > 0 else 0.0), f"{m[0]} missão(ões) depois da decisão, {m[1] or 0} com achado"
                elif em < (agora - timedelta(hours=24)).isoformat():
                    resultado = "a família não voou em 24 h: sem avaliação"
                    conta["sem_execucao"] += 1
            elif etapa == "interceptador":  # o voo autorizado trouxe material para o livro?
                t = bib.execute(
                    "SELECT COUNT(*), SUM(CASE WHEN resultado NOT LIKE '%sem material%' THEN 1 ELSE 0 END) FROM tentativa "
                    "WHERE livro_id = ? AND em >= ? AND ferramenta LIKE 'abordagem%'",
                    (alvo, em),
                ).fetchone()
                if t[0]:
                    rec, resultado = (1.0 if (t[1] or 0) > 0 else 0.0), f"{t[0]} passo(s) do plano de voo, {t[1] or 0} com material"
                elif em < (agora - timedelta(hours=24)).isoformat():
                    resultado = "o voo não registrou passos em 24 h: sem avaliação"
                    conta["sem_execucao"] += 1
            elif etapa == "passagem":  # a escolha de pular: a etapa rodou (em sombra) e não rendeu?
                from ..comandante.escolher import rendeu

                ex = None
                try:
                    import json as _j

                    ex = _j.loads(cer.execute("SELECT contexto FROM comandante_decisao WHERE id = ?", (did,)).fetchone()[0] or "{}").get("execucao")
                except (ValueError, TypeError):
                    ex = None
                p_ = cer.execute("SELECT estado, saida FROM execucao_passo WHERE execucao = ? AND no = ?", (ex, alvo)).fetchone() if ex else None
                if p_ and p_[0] == "concluido":
                    rec, resultado = (
                        (0.0, "a etapa rodou e rendeu: pular estaria errado")
                        if rendeu(p_[1])
                        else (1.0, "a etapa rodou e não rendeu: pular estava certo")
                    )
                elif p_ and p_[0] == "pulado":
                    rec, resultado = None, "pulada de verdade (a avaliação vem da próxima passagem em que ela rodar)"
            if resultado is None:
                continue
            diario.emitir(
                "comandante.avaliada",
                "aprendizado",
                {"id": did, "resultado": resultado, "recompensa": rec, "avaliada_em": agora.isoformat(timespec="seconds")},
            )
            conta["avaliadas"] += 1
            conta["acertos"] += int(rec == 1.0)
    finally:
        bib.close()
        cer.close()
    return conta


def comparacao(bib: sqlite3.Connection, cer: sqlite3.Connection, dias: int = 7) -> dict[str, Any]:
    """O rendimento das escolhas do Comandante contra o da ordem fixa, nos mesmos dias (a sala mostra)."""
    desde = (datetime.now(timezone.utc) - timedelta(days=dias)).date().isoformat()
    try:
        c = cer.execute(
            "SELECT COUNT(*), AVG(recompensa) FROM comandante_decisao WHERE etapa = 'coleta' AND recompensa IS NOT NULL AND em >= ?", (desde,)
        ).fetchone()
        dias_ = [
            d
            for (d,) in cer.execute(
                "SELECT DISTINCT substr(em, 1, 10) FROM comandante_decisao WHERE etapa = 'coleta' AND recompensa IS NOT NULL AND em >= ?", (desde,)
            )
        ]
        lidos = (
            set(
                cer.execute(
                    "SELECT motor || '|' || substr(inicio, 1, 10) FROM execucao_motor WHERE substr(inicio, 1, 10) IN (%s)"
                    % ",".join("?" * len(dias_)),
                    dias_,
                ).fetchall()
            )
            if dias_
            else set()
        )
        com_achado = {f"{m}|{d}" for m, d in bib.execute("SELECT DISTINCT motor, substr(encontrado_em, 1, 10) FROM achado WHERE decisao = 'aceito'")}
        fixa = (sum(1 for (x,) in lidos if x in com_achado) / len(lidos)) if lidos else None
    except sqlite3.Error:
        return {"comandante": None, "ordem_fixa": None, "decisoes": 0}
    return {
        "comandante": round(c[1], 3) if c[1] is not None else None,
        "ordem_fixa": round(fixa, 3) if fixa is not None else None,
        "decisoes": c[0] or 0,
    }


def no_avaliar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Aprendizado, A4): avalia as decisões maduras do Comandante."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return []
    return [avaliar(dados, contexto.diario)]
