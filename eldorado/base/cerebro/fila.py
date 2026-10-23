"""A fila do sistema (titular, 22/10/2026): o Eldorado funciona de forma permanente, sem horário de trabalho e descanso.
Sempre que houver fila, ele trabalha: uma rotina depois da outra (monitorar, acionar, validar, aprender). Sem fila, ele
espera só até a próxima ação que o Cérebro previu (a próxima hora aprendida de alguma fonte)."""
from __future__ import annotations

import sqlite3
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def fila_do_sistema(dados: str | Path = "dados", config: str | Path = "config", agora: datetime | None = None) -> dict[str, Any]:
    from .decisao import proxima
    from .regencia import _decidir
    dados, config, agora = Path(dados), Path(config), agora or datetime.now(timezone.utc)
    modulos = [Path(m["parametros"]["configuracao"]).stem for m in tomllib.loads((config / "modulos.toml").read_text(encoding="utf-8")).get("modulo", [])
               if (m.get("parametros") or {}).get("configuracao")]
    parametros = {"dados": str(dados), "agenda": str(config / "agenda.toml")}
    devidos = _decidir(agora, modulos, parametros)
    preparacao = 0
    if (dados / "biblioteca.db").exists():
        con = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
        try:
            preparacao = con.execute("SELECT COUNT(*) FROM passaporte WHERE fase IN ('recepcao','certificacao','preparacao','validacao')").fetchone()[0]
        finally:
            con.close()
    from .decisao import Execucao
    historico: list[Execucao] = []
    if (dados / "cerebro.db").exists():
        con = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
        try:
            historico = [Execucao(m, datetime.fromisoformat(i), a or 0) for m, i, a in con.execute("SELECT motor, inicio, achados FROM execucao_motor")]
        finally:
            con.close()
    ponto = {}
    if (config / "agenda.toml").exists():
        for mod in tomllib.loads((config / "agenda.toml").read_text(encoding="utf-8")).get("modulo", []):
            ponto[mod["id"]] = {int(h.split(":")[0]) for h in mod.get("horarios", [])}
    prox = proxima(agora, modulos, historico, ponto)
    return {"motores_devidos": [d.motor for d in devidos], "livros_em_trabalho": preparacao, "total": len(devidos) + preparacao,
            "proxima_acao": prox.isoformat(), "proxima_s": max(0.0, (prox - agora).total_seconds())}
