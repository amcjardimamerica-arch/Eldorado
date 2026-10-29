"""A cópia de segurança dos livros (titular, 29/10/2026): a cada 3 dias, e SÓ dos livros que mudaram desde a cópia
anterior (os parados ficam com a cópia antiga). É precaução, não forma de operação: o banco não foi feito para quebrar, e
a fonte da verdade são os eventos (a gravação a cada 5 min é o registro do trabalho, não uma cópia do banco).

    backups/livros/AAAA-MM-DD.jsonl.zst   um livro por linha: o livro, os dados, a fase e as certidões
    backups/livros/indice.json            a data de cada cópia e quantos livros ela levou
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import zstandard

INTERVALO = timedelta(days=3)


def copiar(dados: str | Path = "dados", destino: str | Path = "backups/livros", agora: datetime | None = None, forcar: bool = False) -> str:
    agora = agora or datetime.now(timezone.utc)
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    arq_indice = destino / "indice.json"
    indice = json.loads(arq_indice.read_text(encoding="utf-8")) if arq_indice.exists() else {"copias": []}
    ultima = indice["copias"][-1]["em"] if indice["copias"] else None
    if ultima and not forcar and agora - datetime.fromisoformat(ultima) < INTERVALO:
        return f"a próxima cópia em {(datetime.fromisoformat(ultima) + INTERVALO).date()} (a última: {ultima[:10]})"
    b = Path(dados) / "biblioteca.db"
    if not b.exists():
        return "sem a Biblioteca"
    con = sqlite3.connect(f"file:{b}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        desde = ultima or "0000"
        ids = [r[0] for r in con.execute("SELECT id FROM livro WHERE COALESCE(atualizado_em, criado_em, '') > ?", (desde,))]
        linhas = []
        for i in ids:
            livro = dict(con.execute("SELECT * FROM livro WHERE id = ?", (i,)).fetchone())
            dd = con.execute("SELECT * FROM livro_dados WHERE livro_id = ?", (i,)).fetchone()
            fase = con.execute("SELECT fase FROM passaporte WHERE livro_id = ?", (i,)).fetchone()
            certs = [dict(r) for r in con.execute(
                "SELECT item, valor, pagina, trecho, fase, situacao, justificativa, em FROM certidao WHERE livro_id = ?", (i,))]
            linhas.append(json.dumps({"livro": livro, "dados": dict(dd) if dd else None, "fase": fase[0] if fase else None, "certidoes": certs},
                                     ensure_ascii=False, default=str))
    finally:
        con.close()
    nome = f"{agora:%Y-%m-%d}.jsonl.zst"
    (destino / nome).write_bytes(zstandard.ZstdCompressor(level=19).compress("\n".join(linhas).encode("utf-8")))
    indice["copias"].append({"em": agora.isoformat(timespec="seconds"), "arquivo": nome, "livros": len(linhas), "desde": desde})
    arq_indice.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"cópia dos livros: {len(linhas)} livro(s) que mudaram desde {desde[:10]} → {nome}"
