"""Camada de banco recomendada no parecer de arquitetura (conselho de 7).

Decisão: manter Python e trocar a ESTRUTURA de dados — o JSONL era lido
inteiro na memória a cada execução. Este módulo sincroniza o JSONL (que
permanece como espelho legível e trilha de auditoria) para um banco SQLite
com índices, permitindo consultas em milissegundos sem carregar tudo.

SQLite vem embutido no Python: nenhuma dependência nova, um arquivo só
(dados/eldorado.db), transações seguras contra interrupção de workflow.

Limiares definidos no parecer:
  - até 2.000 editais: JSONL direto ainda é confortável;
  - acima disso: o painel passa a consultar por aqui;
  - acima de 20.000: repensar a publicação (busca sob demanda).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ / "dados" / "eldorado.db"
CAMINHO_JSONL = RAIZ / "dados" / "oportunidades" / "oportunidades.jsonl"

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS oportunidades (
    id          TEXT PRIMARY KEY,
    titulo      TEXT NOT NULL,
    url         TEXT,
    fonte_id    TEXT,
    territorio  TEXT,
    uf          TEXT,
    nivel       TEXT,
    status      TEXT,
    area        TEXT,
    inicio      TEXT,
    fim         TEXT,
    registro    TEXT NOT NULL          -- JSON integral do registro
);
CREATE INDEX IF NOT EXISTS idx_uf     ON oportunidades(uf);
CREATE INDEX IF NOT EXISTS idx_area   ON oportunidades(area);
CREATE INDEX IF NOT EXISTS idx_fim    ON oportunidades(fim);
CREATE INDEX IF NOT EXISTS idx_status ON oportunidades(status);
"""


def conectar(caminho: Path = CAMINHO_BANCO) -> sqlite3.Connection:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(_ESQUEMA)
    return con


def sincronizar(jsonl: Path = CAMINHO_JSONL, banco: Path = CAMINHO_BANCO) -> dict:
    """Espelha o JSONL no SQLite em uma única transação.

    O JSONL continua sendo a fonte de escrita das varreduras (trilha de
    auditoria legível e versionável); o banco é a camada de CONSULTA.
    """
    from src.dashboard_dados import uf_do_territorio, area_do_edital  # evita import circular

    con = conectar(banco)
    lidos = gravados = 0
    with con:
        con.execute("DELETE FROM oportunidades")
        if jsonl.exists():
            for linha in jsonl.read_text(encoding="utf-8").splitlines():
                linha = linha.strip()
                if not linha:
                    continue
                lidos += 1
                try:
                    r = json.loads(linha)
                except json.JSONDecodeError:
                    continue  # linha truncada por interrupção: ignorada, JSONL audita
                con.execute(
                    "INSERT OR REPLACE INTO oportunidades "
                    "(id,titulo,url,fonte_id,territorio,uf,nivel,status,area,"
                    " inicio,fim,registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (r.get("id"), r.get("titulo") or "", r.get("url"),
                     r.get("fonte_id"), r.get("territorio"),
                     uf_do_territorio(r), r.get("nivel"), r.get("status"),
                     area_do_edital(r),
                     (r.get("prazos") or {}).get("inicio"),
                     (r.get("prazos") or {}).get("fim"),
                     json.dumps(r, ensure_ascii=False)),
                )
                gravados += 1
    con.close()
    return {"lidos": lidos, "gravados": gravados, "banco": str(banco)}


def consultar(uf: str | None = None, area: str | None = None,
              abertos_em: str | None = None,
              banco: Path = CAMINHO_BANCO) -> list[dict]:
    """Consulta indexada; devolve os registros integrais (JSON) que casam."""
    con = conectar(banco)
    sql, args = "SELECT registro FROM oportunidades WHERE 1=1", []
    if uf:
        sql += " AND uf=?"; args.append(uf.upper())
    if area:
        sql += " AND area=?"; args.append(area)
    if abertos_em:
        sql += " AND (fim IS NULL OR fim>=?) AND (inicio IS NULL OR inicio<=?)"
        args += [abertos_em, abertos_em]
    linhas = con.execute(sql, args).fetchall()
    con.close()
    return [json.loads(l[0]) for l in linhas]


def total(banco: Path = CAMINHO_BANCO) -> int:
    con = conectar(banco)
    n = con.execute("SELECT COUNT(*) FROM oportunidades").fetchone()[0]
    con.close()
    return n


if __name__ == "__main__":
    print(json.dumps(sincronizar(), ensure_ascii=False, indent=2))
