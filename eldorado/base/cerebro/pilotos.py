"""O Cérebro dos pilotos (titular, 22/10/2026): mede a recorrência de cada piloto e manda nova missão sempre que
possível, quando houver ociosidade (nenhum motor com leitura devida) e não houver bloqueio na busca.

  Interceptador: age na etapa 3 do Cartório (pela rede neural); a medida é quantas tentativas trouxeram informação.
  Espião: missões de busca livre; a medida é quantas missões tiveram resultado e o rendimento de cada família.
A dose de missões segue a recorrência: sem histórico, explora (2 por ciclo); com resultado recente, até 4; com muitas
missões sem resultado, só 1 (para não gastar à toa).
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def recorrencia_interceptador(con: sqlite3.Connection, horas: int = 72) -> dict[str, Any]:
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
    n, com = 0, 0
    for (res,) in con.execute("SELECT resultado FROM tentativa WHERE fase = 'preparacao' AND em >= ?", (desde,)):
        n += 1
        try:
            r = json.loads(res or "{}")
        except ValueError:
            r = {}
        com += bool(r.get("trouxe") or r.get("documentos"))
    return {"tentativas": n, "trouxeram": com, "taxa": round(com / n, 3) if n else None}


def dose(recorrencia: dict[str, Any]) -> int:
    if not recorrencia.get("missoes"):
        return 2
    if recorrencia.get("com_resultado"):
        return 4
    return 1 if recorrencia["missoes"] >= 20 else 2


def _ler(escada, leitura):
    def ler(url: str) -> tuple[str, str] | None:
        from ...motores.acesso.escada import Bloqueado, Indisponivel, Pendente
        from ...motores.leitura import leitores
        try:
            r = escada.buscar(url)
            lido = leitura.ler(r.conteudo, url)
        except (Bloqueado, Indisponivel, Pendente, leitores.SemLeitor):
            return None
        m = re.search(rb"<title[^>]*>(.*?)</title>", r.conteudo[:20000], re.I | re.S)
        titulo = re.sub(r"\s+", " ", m.group(1).decode("utf-8", "replace")).strip() if m else ""
        return titulo, lido.texto
    return ler


def missoes(dados: str | Path, biblioteca: sqlite3.Connection, escada, ociosidade: bool, orcamento_s: float = 180,
            consultar=None, ler=None) -> tuple[list, dict[str, Any]]:
    """Mede a recorrência dos pilotos e, havendo ociosidade e nenhum bloqueio, manda as missões do Espião."""
    import time

    from ...motores.descoberta.metabusca import Metabusca
    from ...motores.leitura import leitores
    from ...motores.pilotos.espiao import Espiao, vigiados_pelos_motores
    dados = Path(dados)
    relatorio: dict[str, Any] = {"interceptador": recorrencia_interceptador(biblioteca)}
    conhecidos = {(r[0] or "").rstrip("/") for r in biblioteca.execute("SELECT link_oficial FROM livro UNION SELECT link_divulgacao FROM livro") if r[0]}
    empresas: list[str] = []
    if (dados / "especial.db").exists():
        esp = sqlite3.connect(f"file:{dados / 'especial.db'}?mode=ro", uri=True)
        try:
            empresas = [r[0] for r in esp.execute("SELECT COALESCE(nome_fantasia, razao_social) FROM empresa WHERE uf = 'GO' LIMIT 300") if r[0]]
        finally:
            esp.close()
    mb = None
    if consultar is None:
        mb = Metabusca(buscar=escada.buscar)
        consultar = lambda q: mb.consultar(q, limite=10)  # noqa: E731
    espiao = Espiao(dados / "motores" / "espiao.db", consultar, ler or _ler(escada, leitores.padrao()), vigiados_pelos_motores(), conhecidos, empresas)
    if mb is not None:
        agora_ = datetime.now(timezone.utc)
        for rota, ate in espiao.con.execute("SELECT nome, descansa_ate FROM rota"):   # o descanso vale entre as execuções
            if ate and ate > agora_.isoformat():
                mb._descansando[rota] = time.monotonic() + (datetime.fromisoformat(ate) - agora_).total_seconds()
    rec = espiao.recorrencia()
    relatorio["espiao"] = rec
    if not ociosidade:
        relatorio["decisao"] = "sem ociosidade: os motores têm leitura devida; o Espião espera"
        return [], relatorio
    if espiao.bloqueado():
        relatorio["decisao"] = "bloqueio: todas as rotas de busca descansando; o Espião espera"
        return [], relatorio
    n, achados, inicio = dose(rec), [], time.monotonic()
    feitas = []
    for _ in range(n):
        if time.monotonic() - inicio > orcamento_s:
            break
        m = espiao.missao()
        feitas.append({k: v for k, v in m.items() if k != "achados"} | {"achados": len(m["achados"])})
        achados += m["achados"]
        if m["bloqueada"]:
            break
    relatorio["decisao"] = f"ociosidade: {len(feitas)} missão(ões) do Espião (dose {n} pela recorrência)"
    relatorio["missoes"] = feitas
    return achados, relatorio
