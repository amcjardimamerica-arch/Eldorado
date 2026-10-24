"""A análise (fase F9 do plano): a previsão da próxima abertura, o calendário e a história de cada livro.

A previsão: das aberturas da oportunidade em anos anteriores (as datas de publicação dos achados e o início das
inscrições), o mês provável da próxima edição; o alerta 30 dias antes; a confiança cresce com os anos que abriram no
mesmo mês (um ano só: confiança baixa). Vale para os livros que esperam a próxima edição (no arquivo) e para os
encerrados; nunca é certidão: é previsão, e o livro diz isso.
"""
from __future__ import annotations

import sqlite3
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

ALERTA_DIAS = 30


def _data(t: str | None) -> date | None:
    if not t:
        return None
    try:
        return date.fromisoformat(str(t)[:10])
    except ValueError:
        return None


def aberturas(con: sqlite3.Connection) -> dict[str, list[date]]:
    """As datas em que cada livro abriu: o início das inscrições e a publicação dos achados (uma por ano)."""
    por: dict[str, list[date]] = defaultdict(list)
    for lid, ini in con.execute("SELECT livro_id, inscricao_inicio FROM livro_dados WHERE inscricao_inicio IS NOT NULL"):
        if (d := _data(ini)):
            por[lid].append(d)
    for lid, pub, enc in con.execute("SELECT livro_id, publicado_em, encontrado_em FROM achado WHERE livro_id IS NOT NULL"):
        if (d := _data(pub) or _data(enc)):
            por[lid].append(d)
    saida = {}
    for lid, ds in por.items():
        por_ano: dict[int, date] = {}
        for d in sorted(ds):
            por_ano.setdefault(d.year, d)                       # a primeira data de cada ano: a abertura daquela edição
        saida[lid] = sorted(por_ano.values())
    return saida


def prever(datas: list[date], hoje: date | None = None) -> dict[str, Any] | None:
    hoje = hoje or date.today()
    if not datas:
        return None
    meses = [d.month for d in datas]
    dia = int(statistics.median(d.day for d in datas))
    mes = statistics.mode(meses)
    ano = hoje.year if date(hoje.year, mes, min(dia, 28)) > hoje else hoje.year + 1
    prevista = date(ano, mes, min(dia, 28))
    iguais = sum(1 for m in meses if abs(m - mes) <= 1 or abs(m - mes) == 11)
    confianca = round(min(0.95, 0.35 + 0.2 * (iguais - 1)) if len(datas) > 1 else 0.3, 2)
    return {"proxima_abertura_prevista": prevista.isoformat(), "alerta_em": (prevista - timedelta(days=ALERTA_DIAS)).isoformat(),
            "confianca": confianca, "anos": sorted({d.year for d in datas})}


def calcular(con: sqlite3.Connection, diario, hoje: date | None = None) -> dict[str, int]:
    """A previsão dos livros que esperam a próxima edição (o arquivo) e dos encerrados; o evento previsao.calculada."""
    hoje = hoje or date.today()
    alvo = {r[0] for r in con.execute("SELECT p.livro_id FROM passaporte p JOIN livro_dados d ON d.livro_id = p.livro_id "
                                      "WHERE p.fase = 'arquivo' OR d.situacao_prazo = 'encerrada'")}
    ab = aberturas(con)
    motores = defaultdict(set)
    for lid, m in con.execute("SELECT livro_id, motor FROM achado WHERE livro_id IS NOT NULL"):
        motores[lid].add(m)
    feitas = 0
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for lid in sorted(alvo):
        p = prever(ab.get(lid, []), hoje)
        if p is None:
            continue
        diario.emitir("previsao.calculada", "analise", {"livro_id": lid, "motores_que_encontraram": ", ".join(sorted(motores.get(lid, []))),
                                                        "datas_encontrado": ", ".join(d.isoformat() for d in ab.get(lid, [])),
                                                        "proxima_abertura_prevista": p["proxima_abertura_prevista"], "alerta_em": p["alerta_em"],
                                                        "confianca": p["confianca"], "calculada_em": agora})
        feitas += 1
    return {"livros_esperando": len(alvo), "previsoes": feitas}


def calendario(con: sqlite3.Connection, hoje: date | None = None, dias: int = 365) -> list[dict[str, Any]]:
    """As abertas (o prazo) e as previstas (a próxima abertura), em ordem de data."""
    hoje = hoje or date.today()
    ate = (hoje + timedelta(days=dias)).isoformat()
    itens = [{"data": f, "tipo": "encerramento", "livro_id": i, "titulo": t} for i, t, f in con.execute(
        "SELECT l.id, l.titulo, d.inscricao_fim FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE d.situacao_prazo = 'aberta' "
        "AND d.inscricao_fim >= ? AND l.situacao <> 'excluido'", (hoje.isoformat(),))]
    itens += [{"data": p, "tipo": "abertura prevista", "livro_id": i, "titulo": t, "alerta_em": a, "confianca": c} for i, t, p, a, c in con.execute(
        "SELECT l.id, l.titulo, v.proxima_abertura_prevista, v.alerta_em, v.confianca FROM previsao v JOIN livro l ON l.id = v.livro_id "
        "WHERE v.proxima_abertura_prevista BETWEEN ? AND ?", (hoje.isoformat(), ate))]
    return sorted(itens, key=lambda x: x["data"])


def historia(con: sqlite3.Connection, lid: str) -> list[dict[str, Any]]:
    """A história do livro: os achados, as certidões, as passagens, os relatórios e as transferências, em ordem."""
    linhas = []
    for em, m, t in con.execute("SELECT encontrado_em, motor, titulo FROM achado WHERE livro_id = ?", (lid,)):
        linhas.append({"em": em, "o_que": f"achado pelo motor {m}", "detalhe": t})
    for em, i, s, v in con.execute("SELECT em, item, situacao, valor FROM certidao WHERE livro_id = ?", (lid,)):
        linhas.append({"em": em, "o_que": f"certidão {s}: {i}", "detalhe": v})
    for em, de, para, por in con.execute("SELECT em, de, para, autorizado_por FROM passagem WHERE livro_id = ?", (lid,)):
        linhas.append({"em": em, "o_que": f"passagem {de or 'início'} → {para}", "detalhe": por})
    for em, fase, gerou in con.execute("SELECT em, fase, gerou FROM relatorio_etapa WHERE livro_id = ?", (lid,)):
        linhas.append({"em": em, "o_que": f"relatório da etapa {fase}", "detalhe": gerou})
    for em, v in con.execute("SELECT em, versao_formato FROM transferencia WHERE livro_id = ?", (lid,)):
        linhas.append({"em": em, "o_que": "transferido ao Farol", "detalhe": v})
    return sorted(linhas, key=lambda x: str(x["em"]))


def no_analise(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a previsão da próxima abertura dos livros que esperam a próxima edição."""
    from pathlib import Path
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return []
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        return [calcular(con, contexto.diario)]
    finally:
        con.close()
