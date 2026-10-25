"""O curador do Aprendizado (a etapa A5; o conceito do curador do Hermes Agent, titular, 25/10/2026).

As skills (skills/<nome>/SKILL.md, o formato aberto do Hermes e da Anthropic) são registradas no Arquivo do Cérebro, e o
uso e o resultado de cada uma são contados PELA EVIDÊNCIA no Cérebro (as decisões avaliadas, os passos concluídos, as
missões que acharam), recalculados a cada passagem — sem contadores soltos. O ciclo de vida, como no Hermes:
  ativa → parada (14 dias sem uso) → arquivada (30 dias parada); volta a ativa quando é usada; nunca apaga;
  a skill nunca usada e mais nova que 14 dias continua ativa (sem uso não é prova de inutilidade).
A skill que rende pouco (20 usos ou mais, menos de 20% de sucesso) vira uma proposta de melhoria (o aprendizado
temporário, 30 dias). O grafo liga o dono à skill, a skill à etapa e as skills relacionadas."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PARADA_DIAS, ARQUIVADA_DIAS = 14, 30
POUCO_RENDIMENTO = (20, 0.2)


def ler_skill(caminho: Path) -> dict[str, Any] | None:
    """O cabeçalho do SKILL.md (só os campos que o curador usa; sem depender do PyYAML)."""
    t = caminho.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", t, re.S)
    if not m:
        return None
    c = m.group(1)

    def campo(nome: str) -> str:
        r = re.search(rf"^\s*{nome}:\s*(.+)$", c, re.M)
        return r.group(1).strip().strip('"') if r else ""

    rel = re.search(r"related_skills:\s*\[(.*?)\]", c)
    return {
        "nome": campo("name"),
        "descricao": campo("description"),
        "versao": campo("version"),
        "dono": campo("dono"),
        "etapa": campo("etapa"),
        "evidencia": campo("evidencia"),
        "caminho": str(caminho),
        "relacionadas": [x.strip() for x in (rel.group(1).split(",") if rel else []) if x.strip()],
    }


def skills(pasta: Path = Path("skills")) -> list[dict[str, Any]]:
    return [s for p in sorted(pasta.glob("*/SKILL.md")) if (s := ler_skill(p)) and s["nome"]]


def evidencia(cer: sqlite3.Connection, bib: sqlite3.Connection, ev: str) -> tuple[int, int, int, str | None]:
    """(usos, sucessos, falhas, último uso) pela evidência no Cérebro e na Biblioteca."""
    tipo, _, alvo = ev.partition(":")
    try:
        if tipo == "decisoes":
            r = cer.execute(
                "SELECT COUNT(*), SUM(recompensa = 1), SUM(recompensa = 0), MAX(em) FROM comandante_decisao WHERE etapa = ?", (alvo,)
            ).fetchone()
        elif tipo == "passo":
            r = cer.execute(
                "SELECT COUNT(*), SUM(estado = 'concluido'), SUM(estado = 'falhou'), MAX(em) FROM execucao_passo WHERE no = ?", (alvo,)
            ).fetchone()
        elif tipo == "missoes":
            r = cer.execute("SELECT COUNT(*), SUM(achados > 0), SUM(achados = 0), MAX(em) FROM espiao_missao").fetchone()
        elif tipo == "abordagens":
            r = bib.execute(
                "SELECT COUNT(*), SUM(resultado NOT LIKE '%sem material%'), SUM(resultado LIKE '%sem material%'), MAX(em) "
                "FROM tentativa WHERE ferramenta LIKE 'abordagem%'"
            ).fetchone()
        elif tipo == "parametros":
            r = cer.execute("SELECT COUNT(*), COUNT(*), 0, MAX(em) FROM parametro").fetchone()
        elif tipo == "conferencias":
            r = cer.execute(
                "SELECT COUNT(*), SUM(estado IN ('intacta', 'restaurada')), SUM(estado = 'sobrescrita'), MAX(conferida_em) "
                "FROM conferencia WHERE estado != 'aguardando'"
            ).fetchone()
        else:
            return 0, 0, 0, None
    except sqlite3.Error:
        return 0, 0, 0, None
    return int(r[0] or 0), int(r[1] or 0), int(r[2] or 0), r[3]


def curar(dados: Path, diario, pasta: Path = Path("skills"), agora: datetime | None = None) -> dict[str, int]:
    agora = agora or datetime.now(timezone.utc)
    iso = agora.isoformat(timespec="seconds")
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    conta = {"skills": 0, "registradas": 0, "estados": 0, "propostas": 0, "arestas": 0}
    try:
        if not cer.execute("SELECT 1 FROM sqlite_master WHERE name = 'skill'").fetchone():
            return conta
        atuais = {r[0]: r for r in cer.execute("SELECT nome, versao, descricao, estado, usos, sucessos, falhas, ultimo_uso, criada_em FROM skill")}
        propostas = {r[0] for r in cer.execute("SELECT o_que FROM aprendizado_temporario WHERE modulo = 'curador'")}
        for s in skills(pasta):
            conta["skills"] += 1
            n = s["nome"]
            if n not in atuais:
                diario.emitir(
                    "skill.registrada",
                    "aprendizado",
                    {
                        "nome": n,
                        "dono": s["dono"] or "aprendizado",
                        "descricao": s["descricao"],
                        "caminho": s["caminho"],
                        "versao": s["versao"],
                        "estado": "ativa",
                        "usos": 0,
                        "sucessos": 0,
                        "falhas": 0,
                        "ultimo_uso": None,
                        "criada_em": iso,
                        "atualizada_em": iso,
                    },
                )
                conta["registradas"] += 1
                criada, estado = iso, "ativa"
            else:
                _, versao, desc, estado, *_r, criada = atuais[n]
                if versao != s["versao"] or desc != s["descricao"]:
                    diario.emitir(
                        "skill.atualizada",
                        "aprendizado",
                        {"nome": n, "descricao": s["descricao"], "caminho": s["caminho"], "versao": s["versao"], "atualizada_em": iso},
                    )
            usos, suc, fal, ultimo = evidencia(cer, bib, s["evidencia"])
            antes = atuais.get(n)
            if not antes or (antes[4], antes[5], antes[6], antes[7]) != (usos, suc, fal, ultimo):
                diario.emitir("skill.usada", "aprendizado", {"nome": n, "usos": usos, "sucessos": suc, "falhas": fal, "ultimo_uso": ultimo})
            # o ciclo de vida (nunca apaga)
            ref = ultimo or criada
            dias = (agora - datetime.fromisoformat(str(ref).replace("Z", "+00:00"))).days if ref else 0
            novo = "ativa" if dias < PARADA_DIAS else ("arquivada" if dias >= PARADA_DIAS + ARQUIVADA_DIAS else "parada")
            if novo != estado:
                diario.emitir("skill.estado", "aprendizado", {"nome": n, "estado": novo, "atualizada_em": iso})
                conta["estados"] += 1
            # a proposta de melhoria (o aprendizado temporário)
            if usos >= POUCO_RENDIMENTO[0] and (suc + fal) and suc / (suc + fal) < POUCO_RENDIMENTO[1]:
                o_que = f"a skill {n} rende pouco ({suc} sucessos em {suc + fal} usos avaliados): rever a rotina"
                if o_que not in propostas:
                    diario.emitir(
                        "aprendizado.registrado",
                        "curador",
                        {
                            "modulo": "curador",
                            "o_que": o_que,
                            "evidencia": s["evidencia"],
                            "usos": 0,
                            "criado_em": iso,
                            "expira_em": (agora + timedelta(days=30)).isoformat(timespec="seconds"),
                        },
                    )
                    conta["propostas"] += 1
            # o grafo do aprendizado
            arestas = [(f"dono:{s['dono']}", n, "responsavel"), (n, f"etapa:{s['etapa']}", "executa")] + [
                (n, r, "relacionada") for r in s["relacionadas"]
            ]
            existentes = {
                (o, d, t) for o, d, t in cer.execute("SELECT origem, destino, tipo FROM grafo_aresta WHERE origem = ? OR destino = ?", (n, n))
            }
            existentes |= {(o, d, t) for o, d, t in cer.execute("SELECT origem, destino, tipo FROM grafo_aresta WHERE destino = ?", (n,))}
            for o, d, t in arestas:
                if (o, d, t) not in existentes:
                    diario.emitir("grafo.ligado", "aprendizado", {"origem": o, "destino": d, "tipo": t, "peso": 1.0, "em": iso})
                    conta["arestas"] += 1
    finally:
        cer.close()
        bib.close()
    return conta


def no_curar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Aprendizado, A5): registra, conta, mantém e liga as skills."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return []
    return [curar(dados, contexto.diario, Path(parametros.get("skills", "skills")))]
