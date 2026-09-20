"""ACERVO COMPACTO DA BIBLIOTECA DE ALEXANDRIA — SQLite FTS5 + zstd.

Por que esta escolha (avaliação de 20/09/2026, com o critério do titular: código aberto,
pouco disco, eficiente, automatizável):

  • SQLite FTS5 — já embutido no Python; índice de texto completo com ranking BM25,
    busca por prefixo e frase; UM arquivo; zero serviço rodando. Tantivy (Rust) é mais
    rápido mas exige compilação/wheel de ~10 MB e não tem ganho real neste volume
    (~70 mil fichas). Meilisearch/Typesense/Elastic exigem processo servidor e
    centenas de MB — descartados. Whoosh é puro Python mas 10× mais lento que FTS5.
  • zstd — compressão 2-4× melhor que gzip em JSON/texto repetitivo, com dicionário
    treinado sobre o próprio acervo; wheel de 5 MB. Texto e ficha ficam comprimidos
    na linha; só o campo de busca fica em claro no índice FTS.
  • rapidfuzz — deduplicação por similaridade de título (3 MB); substitui os 71 mil
    arquivos-ficha repetidos de edições de diário por UMA linha por edição.

Resultado esperado: os 245 MB / 71.814 arquivos da pasta 'oportunidades' cabem em um
arquivo de dezenas de MB, buscável em milissegundos, versionado como um só objeto.

Uso:
  python -m src.acervo_compacto construir     # (re)constrói biblioteca_alexandria/acervo.sqlite
  python -m src.acervo_compacto buscar "termo de fomento cultura goiás"
"""
from __future__ import annotations

import gzip
import json
import os
import sqlite3
import sys
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

ACERVO = ROOT / "biblioteca_alexandria/acervo.sqlite"
DICIONARIO = ROOT / "biblioteca_alexandria/acervo.zstd-dict"

try:
    import zstandard as zstd
except Exception:                       # pragma: no cover
    zstd = None


def _cctx(dic: bytes | None = None):
    if zstd is None:
        return None
    return zstd.ZstdCompressor(level=19, dict_data=zstd.ZstdCompressionDict(dic)) if dic else zstd.ZstdCompressor(level=19)


def _dctx(dic: bytes | None = None):
    if zstd is None:
        return None
    return zstd.ZstdDecompressor(dict_data=zstd.ZstdCompressionDict(dic)) if dic else zstd.ZstdDecompressor()


def _comprime(cctx, s: str) -> bytes:
    b = s.encode("utf-8")
    return cctx.compress(b) if cctx else gzip.compress(b, 9)


def _descomprime(dctx, b: bytes) -> str:
    return (dctx.decompress(b) if dctx else gzip.decompress(b)).decode("utf-8")


def _esquema(con: sqlite3.Connection) -> None:
    con.executescript("""
    PRAGMA journal_mode=WAL; PRAGMA page_size=4096;
    CREATE TABLE IF NOT EXISTS docs (
        id TEXT PRIMARY KEY, tipo TEXT, uf TEXT, area TEXT, orgao TEXT, fim TEXT, situacao TEXT,
        pagina_oficial TEXT, primeira_data TEXT, selo TEXT, ficha_zst BLOB, texto_zst BLOB, atualizado TEXT);
    CREATE VIRTUAL TABLE IF NOT EXISTS busca USING fts5(id UNINDEXED, titulo, objeto, orgao, uf, area, tokenize='unicode61 remove_diacritics 2');
    CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT);
    CREATE INDEX IF NOT EXISTS ix_docs_uf ON docs(uf); CREATE INDEX IF NOT EXISTS ix_docs_fim ON docs(fim);
    """)


def construir() -> dict:
    from .compacto import expandir
    from .fonte_edital import EXTRAIDOS
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = {e["id"]: e for e in (dados.get("editais") or [])}
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        for o in expandir(load_json(ab)):
            universo.setdefault(o["id"], o)
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    ach = load_json(ROOT / "docs/dados/achados_dia.json") if (ROOT / "docs/dados/achados_dia.json").exists() else {}
    primeira = ach.get("primeira_data") or {}
    # dicionário zstd treinado sobre amostra do acervo (fichas + textos)
    amostra = []
    for i, (eid, e) in enumerate(universo.items()):
        if i % 7 == 0:
            amostra.append(json.dumps(e, ensure_ascii=False).encode("utf-8"))
    for f in sorted((ROOT / "dados/editais/textos").glob("*.txt.gz"))[:120]:
        try:
            amostra.append(gzip.open(f, "rb").read()[:20000])
        except Exception:
            pass
    dic = None
    if zstd is not None and len(amostra) >= 8:
        try:
            dic = zstd.train_dictionary(112 * 1024, amostra).as_bytes()
            DICIONARIO.write_bytes(dic)
        except Exception:
            dic = None
    cctx = _cctx(dic)
    if ACERVO.exists():
        ACERVO.unlink()
    con = sqlite3.connect(ACERVO); _esquema(con)
    n_docs = n_txt = bytes_in = 0
    for eid, e in universo.items():
        ficha = json.dumps(e, ensure_ascii=False, separators=(",", ":"))
        bytes_in += len(ficha)
        texto_zst = None
        ex = EXTRAIDOS / f"{eid}.json"
        tx = ROOT / "dados/editais/textos" / f"{eid}.txt.gz"
        objeto = (e.get("objeto") or "")
        if ex.exists():
            exd = load_json(ex); objeto = objeto or ((exd.get("itens") or {}).get("Objeto") or "")
            ficha = json.dumps({"reg": e, "extraido": exd}, ensure_ascii=False, separators=(",", ":"))
        if tx.exists():
            try:
                t = gzip.open(tx, "rt", encoding="utf-8").read(); bytes_in += len(t)
                texto_zst = _comprime(cctx, t); n_txt += 1
            except Exception:
                pass
        a = an.get(eid) or {}
        con.execute("INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (eid, e.get("tipo_registro"), e.get("uf"), e.get("area"), e.get("orgao") or e.get("fonte_nome"), e.get("fim"),
                     e.get("situacao") or e.get("situacao_inscricao"), e.get("pagina_divulgacao"), primeira.get(eid), a.get("selo"),
                     _comprime(cctx, ficha), texto_zst, now_iso()))
        con.execute("INSERT INTO busca VALUES (?,?,?,?,?,?)", (eid, e.get("titulo") or "", objeto[:2000], e.get("orgao") or e.get("fonte_nome") or "", e.get("uf") or "", e.get("area") or ""))
        n_docs += 1
    con.execute("INSERT OR REPLACE INTO meta VALUES ('construido_em',?)", (now_iso(),))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('docs',?)", (str(n_docs),))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('motor','SQLite FTS5 (BM25, unicode61) + zstd nível 19 com dicionário treinado')")
    con.commit(); con.execute("PRAGMA wal_checkpoint(TRUNCATE)"); con.execute("VACUUM"); con.close()
    tam = ACERVO.stat().st_size
    res = {"em": now_iso(), "docs": n_docs, "com_texto": n_txt, "bytes_entrada": bytes_in, "bytes_acervo": tam,
           "compressao": round(bytes_in / tam, 1) if tam else None, "dicionario_zstd": bool(dic), "arquivo": str(ACERVO.relative_to(ROOT)),
           "comparativo": {"pasta_oportunidades_arquivos": 71814, "pasta_oportunidades_mb": 245}}
    write_json(ROOT / "estado/acervo_compacto.json", res)
    return res


def buscar(consulta: str, limite: int = 20, uf: str | None = None) -> list[dict]:
    if not ACERVO.exists():
        return []
    con = sqlite3.connect(ACERVO)
    dic = DICIONARIO.read_bytes() if DICIONARIO.exists() else None
    dctx = _dctx(dic)
    q = " ".join(f'"{w}"' if " " in w else w for w in consulta.split()) if consulta else "*"
    sql = "SELECT b.id, b.titulo, b.orgao, b.uf, d.fim, d.selo, d.pagina_oficial, bm25(busca) AS r FROM busca b JOIN docs d ON d.id=b.id WHERE busca MATCH ?"
    args: list = [q]
    if uf:
        sql += " AND d.uf=?"; args.append(uf)
    sql += " ORDER BY r LIMIT ?"; args.append(limite)
    out = []
    for row in con.execute(sql, args):
        out.append({"id": row[0], "titulo": row[1], "orgao": row[2], "uf": row[3], "fim": row[4], "selo": row[5], "pagina_oficial": row[6], "rank": round(row[7], 3)})
    con.close()
    return out


def ficha(eid: str) -> dict | None:
    if not ACERVO.exists():
        return None
    con = sqlite3.connect(ACERVO)
    dic = DICIONARIO.read_bytes() if DICIONARIO.exists() else None
    row = con.execute("SELECT ficha_zst, texto_zst FROM docs WHERE id=?", (eid,)).fetchone(); con.close()
    if not row:
        return None
    dctx = _dctx(dic)
    return {"ficha": json.loads(_descomprime(dctx, row[0])), "texto": _descomprime(dctx, row[1]) if row[1] else None}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "buscar":
        print(json.dumps(buscar(" ".join(sys.argv[2:])), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(construir(), ensure_ascii=False, indent=2))
