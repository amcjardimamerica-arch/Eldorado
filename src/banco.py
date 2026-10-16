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


def expurgar_acervo(caminho: Path = EXPORT, gravar: bool = True) -> dict:
    """16/10/2026 (titular): o histórico de edições passa pelos MESMOS portões do resto do sistema — território (outros
    estados só estaduais e capitais), pertinência para associação e portão do PNCP. Prazo e 'ano anterior' não valem
    aqui (histórico é passado por natureza). A edição que não passa sai de TODAS as tabelas (histórico, confirmação,
    destinação, itens, extração)."""
    import gzip, json
    from collections import Counter
    from .repositorio_unico import municipal_fora_de_goias, nao_e_oportunidade
    from .pncp_osc import veredito_por_titulo
    if not caminho.exists():
        return {"acervo": "ausente"}
    linhas = []
    with gzip.open(caminho, "rt", encoding="utf-8") as gz:
        for l in gz:
            linhas.append(json.loads(l))
    fora, motivos = set(), Counter()
    for d in linhas:
        if d.get("_t") != "historico":
            continue
        uf = None if d.get("uf") in (None, "None", "") else d.get("uf")
        a = {"titulo": d.get("titulo"), "orgao": d.get("financiador"), "uf": uf, "url": d.get("url"), "nivel": d.get("nivel")}
        m = municipal_fora_de_goias(a)
        if not m:
            n = nao_e_oportunidade(a)
            m = n if n and not n.startswith("edital de ano anterior") else None
        if not m and "pncp.gov.br" in str(d.get("url")):
            m = veredito_por_titulo(str(d.get("titulo") or ""), str(d.get("url") or ""), uf)
        if m:
            fora.add((d.get("chave"), str(d.get("ano")), d.get("id"))); motivos[str(m).split(" —")[0].split(" (")[0][:50]] += 1
    manter = [d for d in linhas if d.get("_t") == "__schema__" or (d.get("chave"), str(d.get("ano")), d.get("id")) not in fora]
    if gravar and fora:
        tmp = caminho.with_suffix(".tmp.gz")
        with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as gz:
            for d in manter:
                gz.write(json.dumps(d, ensure_ascii=False) + "\n")
        tmp.replace(caminho)
        if CAMINHO_BANCO.exists():                       # o índice temporário é remontado a partir do acervo limpo
            CAMINHO_BANCO.unlink()
    return {"edicoes_removidas": len(fora), "linhas_removidas": len(linhas) - len(manter), "linhas_mantidas": len(manter),
            "motivos": dict(motivos.most_common())}


def historico_para_livros(caminho: Path = EXPORT, gravar: bool = True) -> dict:
    """16/10/2026 (titular): 'cada oportunidade validada gera um livro ou se liga ao livro dela' — o histórico só fica se
    se LIGAR com segurança ao livro de uma oportunidade (mesmo endereço; ou título ≥ 60% igual com o mesmo financiador
    e, em diários oficiais, a mesma cidade). Vai para o histórico do livro com o link da publicação; o link oficial fica
    marcado como 'a encontrar'. O que não se liga sai do acervo (todas as tabelas)."""
    import gzip, json, re, unicodedata
    from collections import Counter, defaultdict
    CAT = RAIZ / "biblioteca_alexandria" / "fontes" / "motores.json"
    if not caminho.exists() or not CAT.exists():
        return {"acervo": "ausente"}
    sem = lambda s: "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")
    STOP = set("de da do das dos e a o em para por com no na nos nas edital chamada publica publico selecao programa projetos "
               "projeto premio n no".split())
    tok = lambda s: {w for w in re.findall(r"[a-z0-9]{3,}", sem(s)) if w not in STOP and not w.isdigit()}
    cid = lambda t: (re.search(r"diario oficial d[eoa] ([a-z ]+?)(?: \(|$| \d)", sem(t)) or [None, None])[1]
    cat = json.loads(CAT.read_text(encoding="utf-8")); L = cat.get("motores") or []
    urls, idx = {}, defaultdict(set)
    ids_hist = {}
    for lv in L:                                          # todo livro é de uma oportunidade (atual ou passada)
        for u in [lv.get("pagina"), lv.get("site_oficial"), *(lv.get("paginas") if isinstance(lv.get("paginas"), list) else [])]:
            if isinstance(u, str) and u.startswith("http"):
                urls[u.rstrip("/")] = lv["id"]
        for e in lv.get("historico") or []:               # a edição já registrada no histórico do livro (id ou link)
            if isinstance(e, dict):
                if e.get("id"):
                    ids_hist[e["id"]] = lv["id"]
                if isinstance(e.get("pagina_oficial"), str):
                    urls.setdefault(e["pagina_oficial"].rstrip("/"), lv["id"])
        lv["_t"] = tok(f"{lv.get('programa') or ''} {lv.get('orgao') or ''}")
        for w in lv["_t"]:
            idx[w].add(lv["id"])
    por_id = {lv["id"]: lv for lv in L}
    linhas = []
    with gzip.open(caminho, "rt", encoding="utf-8") as gz:
        for l in gz:
            linhas.append(json.loads(l))
    ligadas = {}
    for d in linhas:
        if d.get("_t") != "historico":
            continue
        alvo = ids_hist.get(d.get("id")) or urls.get(str(d.get("url") or "").rstrip("/"))
        if not alvo:
            T = tok(f"{d.get('titulo')} {d.get('financiador')}"); F = tok(d.get("financiador"))
            for i, _c in Counter(i for w in T for i in idx.get(w, ())).most_common(15):
                lv = por_id[i]; j = len(T & lv["_t"]) / max(1, len(T | lv["_t"]))
                c1, c2 = cid(d.get("titulo")), cid(lv.get("programa"))
                if (c1 or c2) and c1 != c2:
                    continue
                if j >= 0.6 and (not F or F & tok(lv.get("orgao"))):
                    alvo = i; break
        if alvo:
            ligadas[(d.get("chave"), str(d.get("ano")), d.get("id"))] = alvo
            h = por_id[alvo].setdefault("historico", [])           # 16/10: o histórico ÚNICO do livro
            if not any(isinstance(x, dict) and x.get("id") == d.get("id") for x in h):
                h.append({"id": d.get("id"), "titulo": d.get("titulo"), "ano": d.get("ano"), "pagina_oficial": None,
                          "link_publicacao": d.get("url"), "buscar_link_oficial": True, "publicado_em": d.get("data_publicacao"),
                          "inicio": d.get("inicio"), "fim": d.get("fim"), "origem": "acervo de histórico"})
    for lv in L:
        lv.pop("_t", None)
    manter = [d for d in linhas if d.get("_t") == "__schema__" or (d.get("chave"), str(d.get("ano")), d.get("id")) in ligadas]
    n_hist = sum(1 for d in linhas if d.get("_t") == "historico")
    if gravar:
        CAT.write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        tmp = caminho.with_suffix(".tmp.gz")
        with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as gz:
            for d in manter:
                gz.write(json.dumps(d, ensure_ascii=False) + "\n")
        tmp.replace(caminho)
        if CAMINHO_BANCO.exists():
            CAMINHO_BANCO.unlink()
    return {"edicoes": n_hist, "ligadas_a_livros": len(ligadas), "livros_com_historico": len(set(ligadas.values())),
            "edicoes_removidas": n_hist - len(ligadas)}
