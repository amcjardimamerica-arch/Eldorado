"""O Comandante decide (a etapa C2), em PARALELO com a ordem fixa (a fase 2 do desenho): ordena todos os motores e as
famílias de missão do Espião pela política aprendida e registra cada escolha no Arquivo do Cérebro, com o motivo e a nota.
Ainda não aciona: a ordem fixa continua acionando, e a sala compara o rendimento das duas."""

from __future__ import annotations

import json
import sqlite3
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .politica import Politica, contexto

ESCOLHAS_MOTORES = 8


def _motores(config: Path) -> list[str]:
    d = tomllib.loads((config / "modulos.toml").read_text(encoding="utf-8"))
    return [Path(m["parametros"]["configuracao"]).stem for m in d.get("modulo", []) if (m.get("parametros") or {}).get("configuracao")]


def _estado_motores(bib: sqlite3.Connection, motores: list[str], agora: datetime) -> dict[str, dict]:
    ult = dict(bib.execute("SELECT motor, MAX(encontrado_em) FROM achado WHERE decisao = 'aceito' GROUP BY motor").fetchall())
    tot = dict(bib.execute("SELECT motor, COUNT(*) FROM achado GROUP BY motor").fetchall())
    try:   # R35: os descartados (sem livro) saíram da Biblioteca; o registro deles no Cérebro entra no total de cada motor
        arq = bib.execute("PRAGMA database_list").fetchone()[2]
        cer = Path(arq).with_name("cerebro.db") if arq else None
        if cer and cer.exists():
            c = sqlite3.connect(f"file:{cer}?mode=ro", uri=True)
            for m_, n_ in c.execute("SELECT motor, COUNT(*) FROM achado_descartado GROUP BY motor"):
                tot[m_] = tot.get(m_, 0) + n_
            c.close()
    except sqlite3.Error:
        pass
    ace = dict(bib.execute("SELECT motor, COUNT(*) FROM achado WHERE decisao = 'aceito' GROUP BY motor").fetchall())
    saida = {}
    for m in motores:
        try:
            dias = (agora.date() - datetime.fromisoformat(str(ult[m])[:10]).date()).days if ult.get(m) else None
        except ValueError:
            dias = None
        saida[m] = {"dias_sem": dias, "taxa": round((ace.get(m, 0) + 1) / (tot.get(m, 0) + 2), 3)}
    return saida


def _estado_familias(cer: sqlite3.Connection) -> dict[str, dict]:
    try:
        linhas = cer.execute("SELECT nome, usos, achados FROM espiao_familia").fetchall()
    except sqlite3.Error:
        return {}
    return {n: {"dias_sem": None, "taxa": round(((a or 0) + 1) / ((u or 0) + 2), 3)} for n, u, a in linhas}


def decidir(dados: Path, config: Path, diario, plano: dict | None = None, agora: datetime | None = None) -> dict[str, Any]:
    agora = agora or datetime.now(timezone.utc)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'comandante_decisao'").fetchone():
            return {"decisoes": 0, "motivo": "o Arquivo do Cérebro ainda não está na versão 10"}
        ordem_fixa = {m["modulo"] for m in (plano or {}).get("motores", [])}
        resumo = {}
        for etapa, opcoes, k, acao in (("coleta", _estado_motores(bib, _motores(config), agora), ESCOLHAS_MOTORES, "acionar o motor"),):
            if not opcoes:
                continue
            pol = Politica(etapa, list(opcoes))
            aprendidas = pol.reaprender(cer)
            ctx = contexto(agora, opcoes)
            for alvo, prob in pol.ordenar(ctx)[:k]:
                c = opcoes.get(alvo, {})
                motivo = f"nota {prob:.2f} (política aprendida com {aprendidas} decisões avaliadas) · rendimento histórico {c.get('taxa', 0):.0%}" + (
                    f" · {c['dias_sem']} dia(s) sem achado aceito" if c.get("dias_sem") is not None else ""
                )
                if etapa == "coleta":
                    motivo += " · também na ordem fixa" if alvo in ordem_fixa else " · fora da ordem fixa desta passagem"
                diario.emitir(
                    "comandante.decidiu",
                    "comandante",
                    {
                        "em": agora.isoformat(timespec="seconds"),
                        "etapa": etapa,
                        "acao": acao,
                        "alvo": alvo,
                        "motivo": motivo,
                        "nota": round(prob, 4),
                        "politica": "vw-squarecb",
                        "contexto": json.dumps({**ctx, "lista": pol.opcoes, "prob": prob, "na_ordem_fixa": alvo in ordem_fixa}, ensure_ascii=False),
                    },
                )
            resumo[etapa] = {"opcoes": len(opcoes), "escolhas": k, "aprendidas": aprendidas}
        return {"decisoes": resumo}
    finally:
        bib.close()
        cer.close()


def no_comandante_decidir(
    itens: list[dict[str, Any]],
    parametros: dict[str, Any],
    contexto_,
) -> list[dict[str, Any]]:
    """Nó da passagem (logo depois do planejamento): o Comandante decide em paralelo com a ordem fixa (fase 2)."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return []
    plano = next((x.get("plano") for x in itens if x.get("plano")), None)
    return [decidir(dados, Path(parametros.get("config", "config")), contexto_.diario, plano)]
