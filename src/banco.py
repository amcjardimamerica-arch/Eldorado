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

_ESQUEMA_HISTORICO = """
CREATE TABLE IF NOT EXISTS historico (
    chave TEXT, ano TEXT, id TEXT, titulo TEXT, url TEXT,
    financiador TEXT, territorio TEXT, uf TEXT, nivel TEXT, area TEXT,
    data_publicacao TEXT, inicio TEXT, fim TEXT, estado_prazo TEXT,
    tem_resultado INTEGER, vencedores TEXT, criterios TEXT,
    exigencias TEXT, forca_probatoria TEXT, ficha TEXT, parecer TEXT,
    PRIMARY KEY (chave, ano, id)
);
CREATE INDEX IF NOT EXISTS idx_h_fin   ON historico(financiador);
CREATE INDEX IF NOT EXISTS idx_h_area  ON historico(area);
CREATE INDEX IF NOT EXISTS idx_h_uf    ON historico(uf);
CREATE INDEX IF NOT EXISTS idx_h_fim   ON historico(fim);
CREATE INDEX IF NOT EXISTS idx_h_venc  ON historico(tem_resultado);
"""

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


EXPORT = CAMINHO_BANCO.parent / "historico_export.jsonl.gz"   # 4,8 MB — viaja no Git; o .db (148 MB) não
_TABELAS_EXPORT = ("historico", "confirmacao", "destinacao", "itens11", "edicoes")


def conectar(caminho: Path = CAMINHO_BANCO, reconstruir: bool | None = None) -> sqlite3.Connection:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    novo = not caminho.exists()
    if reconstruir is None:
        reconstruir = (caminho == CAMINHO_BANCO)        # só o banco principal (caso do CI)
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(_ESQUEMA)
    con.executescript(_ESQUEMA_HISTORICO)
    if novo and reconstruir and EXPORT.exists():
        # CI sem banco: RECONSTRÓI o acervo a partir do export versionado
        _reconstruir(con, EXPORT)
    return con


def exportar(caminho: Path = EXPORT) -> dict:
    """Exporta as tabelas do acervo para um JSONL gzip pequeno e versionável —
    é assim que o banco chega ao CI e volta com o que o CI produziu."""
    import gzip, json
    con = sqlite3.connect(CAMINHO_BANCO)
    con.row_factory = sqlite3.Row
    n = {}
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(caminho, "wt", encoding="utf-8", compresslevel=6) as gz:
        for tb in _TABELAS_EXPORT:
            try:
                rows = con.execute(f"SELECT * FROM {tb}").fetchall()
            except sqlite3.OperationalError:
                continue
            sql = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tb,)).fetchone()
            if sql and sql[0]:
                gz.write(json.dumps({"_t": "__schema__", "tabela": tb, "sql": sql[0].replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1)}, ensure_ascii=False) + "\n")
            n[tb] = len(rows)
            for r in rows:
                gz.write(json.dumps({"_t": tb, **dict(r)}, ensure_ascii=False) + "\n")
    con.close()
    return {"arquivo": str(caminho), "linhas": n, "mb": round(caminho.stat().st_size / 1048576, 2)}


def _reconstruir(con: sqlite3.Connection, caminho: Path) -> dict:
    import gzip, json
    n = {}
    with con:
        with gzip.open(caminho, "rt", encoding="utf-8") as gz:
            for linha in gz:
                d = json.loads(linha); tb = d.pop("_t")
                if tb == "__schema__":
                    con.execute(d["sql"]); continue
                cols = list(d.keys())
                con.execute(f"INSERT OR REPLACE INTO {tb} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                            [d[c] for c in cols])
                n[tb] = n.get(tb, 0) + 1
    return n


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


def indexar_historico(banco: Path = CAMINHO_BANCO, apagar_pastas: bool = False) -> dict:
    """Move o acervo histórico para o SQLite (melhoria do parecer).

    Motivo: 9.474 editais catalogados viraram 19.915 arquivos e 196 MB — peso
    incompatível com um repositório Git. O banco guarda tudo com índices e
    consulta em milissegundos; ficam em pasta apenas os editais RELEVANTES
    (com vencedor identificado, com fator decisivo, ou ainda abertos), que são
    os que o Farol efetivamente consulta.
    """
    import json as _json
    from .biblioteca import OPORTUNIDADES
    con = conectar(banco)
    guardados = removidos = mantidos = 0
    with con:
        for fp in sorted(OPORTUNIDADES.glob("*/*/ficha.json")):
            try:
                ficha = _json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            if ficha.get("origem") != "catalogacao_historica_5_anos":
                mantidos += 1
                continue
            pp = fp.parent / "parecer_historico.json"
            parecer = _json.loads(pp.read_text(encoding="utf-8")) if pp.exists() else {}
            venc = ficha.get("vencedores_identificados") or []
            crit = ficha.get("criterios_de_julgamento") or []
            con.execute(
                "INSERT OR REPLACE INTO historico VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ficha.get("chave"), ficha.get("ano"), ficha.get("id"),
                 ficha.get("titulo"), ficha.get("url"), ficha.get("financiador"),
                 ficha.get("territorio"), ficha.get("uf"), ficha.get("nivel"),
                 ficha.get("area"), ficha.get("data_publicacao"), ficha.get("inicio"),
                 ficha.get("fim"), ficha.get("estado_prazo"),
                 int(bool(ficha.get("tem_resultado_publicado"))),
                 _json.dumps(venc, ensure_ascii=False),
                 _json.dumps(crit, ensure_ascii=False),
                 _json.dumps(ficha.get("exigencias_detectadas") or [], ensure_ascii=False),
                 (parecer.get("forca_probatoria") or "baixa"),
                 _json.dumps(ficha, ensure_ascii=False),
                 _json.dumps(parecer, ensure_ascii=False)))
            guardados += 1
            # Pasta permanece só para o que tem DADO REAL: vencedor, critério
            # de julgamento ou data de prazo publicada. Presunção de "aberto"
            # (publicação recente sem data) não justifica arquivo em disco —
            # o registro continua íntegro no banco.
            relevante = bool(venc) or bool(crit) or bool(ficha.get("fim"))
            if apagar_pastas and not relevante:
                import shutil
                shutil.rmtree(fp.parent, ignore_errors=True)
                removidos += 1
            else:
                mantidos += 1
    con.close()
    # limpa diretórios de chave que ficaram vazios
    if apagar_pastas:
        for d in sorted(OPORTUNIDADES.glob("*"), reverse=True):
            if d.is_dir() and not any(d.rglob("*")):
                d.rmdir()
    return {"no_banco": guardados, "pastas_mantidas": mantidos,
            "pastas_removidas": removidos, "banco": str(banco)}


def consultar_historico(financiador: str | None = None, area: str | None = None,
                        uf: str | None = None, com_vencedor: bool = False,
                        limite: int = 50, banco: Path = CAMINHO_BANCO) -> list[dict]:
    """Consulta o acervo histórico — a fonte de padrões para o Farol."""
    import json as _json
    con = conectar(banco)
    sql, args = "SELECT ficha, parecer FROM historico WHERE 1=1", []
    if financiador:
        sql += " AND financiador=?"; args.append(financiador)
    if area:
        sql += " AND area=?"; args.append(area)
    if uf:
        sql += " AND uf=?"; args.append(uf.upper())
    if com_vencedor:
        sql += " AND vencedores NOT IN ('[]','')"
    sql += f" LIMIT {int(limite)}"
    linhas = con.execute(sql, args).fetchall()
    con.close()
    return [{"ficha": _json.loads(f), "parecer": _json.loads(p or "{}")}
            for f, p in linhas]


def total_historico(banco: Path = CAMINHO_BANCO) -> int:
    con = conectar(banco)
    n = con.execute("SELECT COUNT(*) FROM historico").fetchone()[0]
    con.close()
    return n


def total(banco: Path = CAMINHO_BANCO) -> int:
    con = conectar(banco)
    n = con.execute("SELECT COUNT(*) FROM oportunidades").fetchone()[0]
    con.close()
    return n


if __name__ == "__main__":
    print(json.dumps(sincronizar(), ensure_ascii=False, indent=2))
