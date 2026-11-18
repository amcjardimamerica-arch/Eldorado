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

ESPERA_DESTINO_DIAS = 14   # 17/11/2026 (C-06): o prazo para o livro ganhar destino; depois, sem destino, vale como arquivo (0,5)


def pelo_destino(livros: list, dest: dict, em: str, agora: datetime) -> tuple[float | None, str | None]:
    """C-06 (R57): a recompensa da decisão é o MELHOR destino entre os livros dos achados aceitos — Farol 1, arquivo com
    edição 0,7, arquivo 0,5, unido 0,2, descartado 0 (a avaliação gravava só 0 e 1). Sem achado aceito: 0. Livro ainda sem
    destino: espera ESPERA_DESTINO_DIAS dias (None, None) e, depois, vale 0,5."""
    if not livros:
        return 0.0, "nenhum achado aceito"
    sem_livro = [x for x in livros if not x]
    livros = [x for x in livros if x]
    if not livros and sem_livro:                    # aceito, mas o livro ainda não nasceu: espera como o livro sem destino
        livros = ["_sem_livro_"]
    vals = [dest[x] for x in livros if x in dest]
    if vals:
        return max(vals), f"{len(livros)} livro(s); o melhor destino vale {max(vals)}"
    if agora - datetime.fromisoformat(em) < timedelta(days=ESPERA_DESTINO_DIAS):
        return None, None
    return 0.5, f"{len(livros)} livro(s) sem destino em {ESPERA_DESTINO_DIAS} dias: vale como arquivo"

def avaliar(dados: Path, diario, agora: datetime | None = None) -> dict[str, int]:
    agora = agora or datetime.now(timezone.utc)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    conta = {"avaliadas": 0, "acertos": 0, "sem_execucao": 0}
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'comandante_decisao'").fetchone():
            return conta
        maduras = (agora - timedelta(hours=2)).isoformat()
        from ..comandante.destino import destinos
        dest = destinos(bib)                                # C-06 (R57): o destino final de cada livro
        for did, etapa, alvo, em in cer.execute(
            "SELECT id, etapa, alvo, em FROM comandante_decisao WHERE avaliada_em IS NULL AND em < ?", (maduras,)
        ):
            rec, resultado = None, None
            if etapa == "coleta":
                dia = em[:10]
                livros = [r[0] for r in bib.execute(
                    "SELECT livro_id FROM achado WHERE motor = ? AND decisao = 'aceito' AND substr(encontrado_em, 1, 10) = ?", (alvo, dia))]
                if em[:10] < agora.date().isoformat():
                    rec, resultado = pelo_destino(livros, dest, em, agora)       # C-06 (R57): pelo destino dos livros
                    if rec is None and resultado is None:
                        continue
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
                            livros = [r[0] for r in bib.execute(
                                "SELECT livro_id FROM achado WHERE motor = 'espiao' AND decisao = 'aceito' AND json_extract(dados, '$.familia') = ? "
                                "AND substr(encontrado_em, 1, 10) BETWEEN ? AND ?", (alvo, m[0][:10], fim_.date().isoformat()))]
                        except sqlite3.Error:
                            livros = []
                        rec, resultado = pelo_destino(livros, dest, em, agora)    # C-06 (R57): pelo destino dos livros
                        if rec is None and resultado is None:
                            continue
                        resultado = f"a missão autorizada trouxe {m[1]} achado(s); {resultado}"
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
        conta["reavaliadas"] = reavaliar(cer, bib, dest, diario, agora)     # C-06: o destino mudou, a recompensa muda
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


def reavaliar(cer: sqlite3.Connection, bib: sqlite3.Connection, dest: dict, diario, agora: datetime, dias: int = 30) -> int:
    """17/11/2026 (C-06, R57: «a recompensa de um livro é revista quando o destino muda»): as decisões de coleta e do Espião
    avaliadas nos últimos `dias` dias são recalculadas pelo destino atual dos livros e regravadas quando o valor mudou."""
    desde = (agora - timedelta(days=dias)).isoformat()
    n = 0
    try:
        decisoes = cer.execute(
            "SELECT id, etapa, alvo, em, recompensa FROM comandante_decisao WHERE etapa IN ('coleta', 'espiao') AND avaliada_em >= ? "
            "AND recompensa IS NOT NULL", (desde,)).fetchall()
    except sqlite3.Error:                            # o Cérebro sem as colunas da avaliação: nada a rever
        return 0
    for did, etapa, alvo, em, rec in decisoes:
        dia = em[:10]
        if etapa == "coleta":
            sql, args = ("SELECT livro_id FROM achado WHERE motor = ? AND decisao = 'aceito' AND substr(encontrado_em, 1, 10) = ?", (alvo, dia))
        else:
            fim = (datetime.fromisoformat(em) + timedelta(hours=24)).date().isoformat()
            sql, args = ("SELECT livro_id FROM achado WHERE motor = 'espiao' AND decisao = 'aceito' AND json_extract(dados, '$.familia') = ? "
                         "AND substr(encontrado_em, 1, 10) BETWEEN ? AND ?", (alvo, dia, fim))
        try:
            livros = [r[0] for r in bib.execute(sql, args)]
        except sqlite3.Error:
            continue
        novo, motivo = pelo_destino(livros, dest, em, agora)
        if novo is None or abs(novo - float(rec)) < 1e-9:
            continue
        diario.emitir("comandante.avaliada", "aprendizado", {"id": did, "resultado": f"reavaliada (o destino mudou): {motivo}", "recompensa": novo,
                                                             "avaliada_em": agora.isoformat(timespec="seconds")})
        n += 1
    return n
