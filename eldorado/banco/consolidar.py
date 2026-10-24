"""A consolidação dos bancos (titular, 24/10/2026): só o Cérebro tem um banco paralelo, o de aprendizado; os livros vivem
só na Biblioteca. Importa, uma vez, os bancos antigos de cada motor (dados/motores/<id>.db) e do Espião para dentro do
Cérebro (tabelas motor_* e espiao_*), e apaga os arquivos paralelos: a fila e os seletores (refeitos no Cérebro) e o
índice de busca (a busca lê a Biblioteca). Idempotente: sem arquivo antigo, não faz nada.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

TABELAS_MOTOR = {"assinatura": "motor_assinatura", "mapa_url": "motor_mapa_url", "mapa_dominio": "motor_mapa_dominio",
                 "alvo_mudanca": "motor_alvo_mudanca", "entregue": "motor_entregue", "fonte": "motor_fonte", "retorno": "motor_retorno"}
TABELAS_ESPIAO = {"familia": "espiao_familia", "consulta": "espiao_consulta", "missao": "espiao_missao", "rota": "espiao_rota"}


def _copiar(origem: Path, cer: sqlite3.Connection, mapa: dict[str, str], motor: str | None) -> int:
    o = sqlite3.connect(f"file:{origem}?mode=ro", uri=True)
    n = 0
    try:
        for antiga, nova in mapa.items():
            if not o.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (antiga,)).fetchone():
                continue
            destino = [r[1] for r in cer.execute(f"PRAGMA table_info({nova})")]
            cols = [r[1] for r in o.execute(f"PRAGMA table_info({antiga})") if r[1] in destino]
            linhas = o.execute(f"SELECT {', '.join(cols)} FROM {antiga}").fetchall()
            if motor is not None:
                cols, linhas = ["motor", *cols], [(motor, *x) for x in linhas]
            cer.executemany(f"INSERT OR IGNORE INTO {nova} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})", linhas)
            n += len(linhas)
    finally:
        o.close()
    return n


def consolidar(dados: Path = Path("dados")) -> dict[str, int]:
    from ..motores.canal.estado import EstadoMotor
    rel = {"motores": 0, "linhas": 0, "apagados": 0}
    EstadoMotor(dados / "cerebro.db", "consolidacao").con.close()          # as tabelas motor_* existem
    cer = sqlite3.connect(dados / "cerebro.db", timeout=60)
    try:
        esp = dados / "motores" / "espiao.db"
        if esp.exists():
            from ..motores.pilotos.espiao import Espiao
            Espiao(dados / "cerebro.db", lambda q: ([], []), lambda u: None).con.close()   # as tabelas espiao_* existem
            rel["linhas"] += _copiar(esp, cer, TABELAS_ESPIAO, None)
        for p in sorted((dados / "motores").glob("*.db")) if (dados / "motores").exists() else []:
            if p.name in ("espiao.db", "seletores.db"):
                continue
            rel["linhas"] += _copiar(p, cer, TABELAS_MOTOR, p.stem)
            rel["motores"] += 1
        cer.commit()
    finally:
        cer.close()
    for p in [*((dados / "motores").glob("*.db*") if (dados / "motores").exists() else []), dados / "fila.db", dados / "biblioteca_busca.db"]:
        if p.exists():
            p.unlink()
            rel["apagados"] += 1
    return rel
