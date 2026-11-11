"""O Aprendizado avalia as decisões do Comandante (a etapa A4): quando o resultado aparece, cada decisão recebe a sua
recompensa, e a política do Comandante reaprende com ela na passagem seguinte.
  coleta: o motor escolhido trouxe achado aceito naquele dia (todo motor lê todo dia, então o resultado sempre aparece);
  interceptador: o voo autorizado registrou passos do plano de voo com material para o livro;
  espiao: R48 (08/11/2026) — a família trouxe achado ACEITO na Biblioteca nas 24 h seguintes (a família que não voou em
          24 h não é avaliada: a recompensa fica vazia, com o motivo)."""

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
                # R48 (titular, 08/11/2026): a recompensa é o ACHADO ACEITO NOVO da família nas 24 h depois da decisão (o dia
                # da decisão e o seguinte), não «alguma missão, a qualquer tempo depois, achou algo» (mediana de 114 missões
                # por avaliação: 0,736 de «acerto» sem significado). Avalia só depois de passadas as 24 h.
                # 08/11/2026 (a correção dos motores unificada à R48): a decisão vale pela MISSÃO QUE ELA AUTORIZOU — a primeira
                # da família nas 2 h seguintes (antes contava qualquer missão posterior, e a família mais usada sempre tinha
                # alguma com achado) — e acerta se essa missão trouxe ACHADO ACEITO na Biblioteca nas 24 h (R48), não só
                # candidato no crivo do Espião. Avalia só depois de passadas as 24 h.
                fim_ = (datetime.fromisoformat(em) + timedelta(hours=24))
                if fim_ <= agora:
                    lim2 = (datetime.fromisoformat(em) + timedelta(hours=2)).isoformat()
                    m = cer.execute("SELECT em, achados FROM espiao_missao WHERE familia = ? AND em > ? AND em <= ? ORDER BY em LIMIT 1",
                                    (alvo, em, lim2)).fetchone()
                    if m is None:
                        resultado = "a família não voou nas 2 h depois da decisão: sem avaliação"
                        conta["sem_execucao"] += 1
                    elif not (m[1] or 0):
                        rec, resultado = 0.0, "a missão autorizada trouxe 0 achado(s)"
                    else:
                        try:
                            n = bib.execute(
                                "SELECT COUNT(*) FROM achado WHERE motor = 'espiao' AND decisao = 'aceito' AND json_extract(dados, '$.familia') = ? "
                                "AND substr(encontrado_em, 1, 10) BETWEEN ? AND ?", (alvo, m[0][:10], fim_.date().isoformat())
                            ).fetchone()[0]
                        except sqlite3.Error:
                            n = 0
                        rec, resultado = (1.0 if n else 0.0), f"a missão autorizada trouxe {m[1]} achado(s); {n} aceito(s) na Biblioteca"
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


def comparacao(bib: sqlite3.Connection, cer: sqlite3.Connection, dias: int = 14, k: int = 8) -> dict[str, Any]:
    """O rendimento da POLÍTICA EM VIGOR do Comandante contra a ordem fixa, nos mesmos dias (a Sala mostra).

    10/11/2026 (parecer da Sala, passo 8): só as decisões da política em vigor (Thompson, desde 09/11; antes, 225 dos 233
    motor-dias da janela eram da política antiga e o mostrador mostrava −4 medindo o que já não decide) e, quando a decisão
    traz a probabilidade de inclusão de todos os motores, o VALOR ESPERADO da política no dia: a soma de probabilidade ×
    resultado sobre os motores lidos, dividida por 8 (todo motor lê todo dia, o resultado de cada um é conhecido) — a média
    das 8 escolhas sorteadas oscilava 6 a 7 pontos por acaso. Mantém a unidade motor-dia (08/11) e as referências: o sorteio
    de 8 motores e a REGRA SIMPLES (os 8 de maior taxa até a véspera), a que a política precisa superar para acionar."""
    import json as _json
    desde = (datetime.now(timezone.utc) - timedelta(days=dias)).date().isoformat()
    try:
        cols = {r[1] for r in cer.execute("PRAGMA table_info(comandante_decisao)")}
        filtro = " AND politica = 'thompson'" if "politica" in cols else ""          # (o Arquivo antigo, sem a política)
        decs = cer.execute(f"SELECT alvo, substr(em, 1, 10), {'contexto' if 'contexto' in cols else 'NULL'} FROM comandante_decisao "
                           f"WHERE etapa = 'coleta'{filtro} AND recompensa IS NOT NULL AND em >= ?", (desde,)).fetchall()
        escolhas = {(a, d) for a, d, _c in decs}
        inclusao: dict[str, dict[str, float]] = {}
        for _a, d, c in decs:
            if d in inclusao:
                continue
            try:
                inc = (_json.loads(c or "{}") or {}).get("inclusao") or {}
            except ValueError:
                inc = {}
            if inc:
                inclusao[d] = {m: float(p) for m, p in inc.items()}
        dias_ = sorted({d for _a, d in escolhas})
        lidos: dict[str, set[str]] = {}
        historico: dict[str, set[str]] = {}
        for m, d in cer.execute("SELECT DISTINCT motor, substr(inicio, 1, 10) FROM execucao_motor"):
            historico.setdefault(d, set()).add(m)
            if d in dias_:
                lidos.setdefault(d, set()).add(m)
        com_achado = {(m, d) for m, d in bib.execute("SELECT DISTINCT motor, substr(encontrado_em, 1, 10) FROM achado WHERE decisao = 'aceito'")}
    except sqlite3.Error:
        return {"comandante": None, "ordem_fixa": None, "decisoes": 0, "politica": "thompson", "unidade": "motor-dia"}
    cm = [(a, d) for a, d in escolhas if a in lidos.get(d, set())]
    # o valor esperado por dia (com a inclusão de todos) ou, sem ela, o realizado (as escolhas do dia)
    por_dia: list[float] = []
    for d in dias_:
        v = lidos.get(d, set())
        inc = inclusao.get(d)
        if inc and v:
            tot = sum(inc.get(m, 0.0) for m in v)
            if tot > 0:
                por_dia.append(sum(inc.get(m, 0.0) * ((m, d) in com_achado) for m in v) / tot)
                continue
        esc = [(a, x) for a, x in cm if x == d]
        if esc:
            por_dia.append(sum((a, x) in com_achado for a, x in esc) / len(esc))
    fixa_n = sum(len(v) for v in lidos.values())
    n_lido: dict[str, int] = {}
    n_ace: dict[str, int] = {}
    regra: list[bool] = []
    for d in sorted(historico):
        if d in lidos:
            top = sorted(lidos[d], key=lambda m: -((n_ace.get(m, 0) + 1) / (n_lido.get(m, 0) + 2)))[:k]
            regra += [(m, d) in com_achado for m in top]
        for m in historico[d]:
            n_lido[m] = n_lido.get(m, 0) + 1
            n_ace[m] = n_ace.get(m, 0) + int((m, d) in com_achado)
    sorteio = (sum(sum((m, d) in com_achado for m in v) / len(v) for d, v in lidos.items() if v) / len(lidos)) if lidos else None
    return {
        "comandante": round(sum(por_dia) / len(por_dia), 3) if por_dia else None,
        "comandante_realizado": round(sum((a, d) in com_achado for a, d in cm) / len(cm), 3) if cm else None,
        "ordem_fixa": round(sum((m, d) in com_achado for d, v in lidos.items() for m in v) / fixa_n, 3) if fixa_n else None,
        "regra_simples": round(sum(regra) / len(regra), 3) if regra else None,
        "sorteio": round(sorteio, 3) if sorteio is not None else None,
        "decisoes": len(cm),
        "dias": len(dias_),
        "dias_valor_esperado": sum(1 for d in dias_ if d in inclusao),
        "unidade": "motor-dia",
        "politica": "thompson",
    }


def no_avaliar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Aprendizado, A4): avalia as decisões maduras do Comandante."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return []
    return [avaliar(dados, contexto.diario)]
