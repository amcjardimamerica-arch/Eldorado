"""A HISTÓRIA COMPLETA DE CADA LIVRO (titular, 02/11/2026): cada livro com todas as suas informações ligadas, sem
separação. Quando dois livros se unem, só as certidões comprovadas e os achados passam ao livro que fica; os vereditos,
as tentativas, os relatórios das etapas, as previsões, as leis, as transferências e as passagens continuavam presos ao
livro unido. Aqui o livro reúne a FAMÍLIA inteira (ele e, em cadeia, todos os que se uniram a ele) e cada linha diz de
qual livro veio. Só leitura: nada se move nem se apaga (a trava dos livros)."""
from __future__ import annotations

import json
import sqlite3
from typing import Any

TABELAS = {   # tabela: (colunas, ordem) — tudo o que a Biblioteca guarda de um livro
    "certidoes": ("certidao", "item, valor, situacao, fase, trecho, pagina, documento_id, justificativa, em", "item, em"),
    "achados": ("achado", "id, motor, encontrado_em, publicado_em, link_divulgacao, link_oficial, titulo, decisao, motivo, documento_id, pista, veio_de_copia_arquivada", "encontrado_em"),
    "vereditos": ("veredito", "origem, decisao, motivo, como_encontrou, em", "em"),
    "tentativas": ("tentativa", "fase, ferramenta, numero, resultado, em, proxima_em", "em"),
    "relatorios": ("relatorio_etapa", "fase, gerou, aprendeu, faltou, analise, em", "em"),
    "passagens": ("passagem", "*", "em"),
    "previsoes": ("previsao", "motores_que_encontraram, datas_encontrado, proxima_abertura_prevista, alerta_em, confianca, calculada_em", "calculada_em"),
    "leis": ("livro_lei", "lei_id, papel, em", "em"),
    "transferencias": ("transferencia", "em, versao_formato", "em"),
    "analises_rede": ("analise_rede", "nota, pertinencia, explicacao, modelo_versao, em", "em"),
    "empresas": ("vinculo_livro", "cnpj, papel, em", "em"),
}


def familia(con: sqlite3.Connection, livro: str) -> list[str]:
    """O livro e, em cadeia, todos os livros que se uniram a ele (o primeiro é o próprio livro)."""
    ids = [r[0] for r in con.execute(
        "WITH RECURSIVE f(id) AS (SELECT ? UNION SELECT u.livro_unido FROM uniao u JOIN f ON u.livro_que_fica = f.id) SELECT id FROM f", (livro,))]
    return [livro] + [i for i in ids if i != livro]


def _linhas(con: sqlite3.Connection, tabela: str, colunas: str, ordem: str, ids: list[str]) -> list[dict[str, Any]]:
    try:
        cur = con.execute(f"SELECT livro_id, {colunas} FROM {tabela} WHERE livro_id IN ({','.join('?' * len(ids))}) ORDER BY {ordem}", ids)
    except sqlite3.Error:
        return []
    nomes = [d[0] for d in cur.description]
    out = []
    for r in cur.fetchall():
        x = dict(zip(nomes, r))
        de = x.pop("livro_id")
        if de != ids[0]:
            x["de_livro"] = de          # a linha veio de um livro unido a este
        out.append(x)
    return out


def historia_completa(con: sqlite3.Connection, livro: str) -> dict[str, Any]:
    antes = con.row_factory                 # a conexão é compartilhada (o site): o formato das linhas volta como estava
    con.row_factory = None
    ids = familia(con, livro)
    con.row_factory = sqlite3.Row
    try:
        lv = con.execute("SELECT * FROM livro WHERE id = ?", (livro,)).fetchone()
        dd = con.execute("SELECT * FROM livro_dados WHERE livro_id = ?", (livro,)).fetchone()
        pp = con.execute("SELECT fase, entrou_em FROM passaporte WHERE livro_id = ?", (livro,)).fetchone()
        un = [dict(r) for r in con.execute(f"SELECT * FROM uniao WHERE livro_que_fica IN ({','.join('?' * len(ids))}) ORDER BY em", ids)]
    finally:
        con.row_factory = None
    try:
        return _montar(con, livro, ids, lv, dd, pp, un)
    finally:
        con.row_factory = antes


def _montar(con, livro, ids, lv, dd, pp, un) -> dict[str, Any]:
    h: dict[str, Any] = {"livro": dict(lv) if lv else None, "dados": dict(dd) if dd else None, "passaporte": dict(pp) if pp else None,
                         "familia": ids, "unioes": un}
    for chave, (tab, cols, ordem) in TABELAS.items():
        h[chave] = _linhas(con, tab, cols, ordem, ids)
    # as certidões dos unidos que já foram copiadas na união não se repetem
    vistos, cert = set(), []
    for c in h["certidoes"]:
        k = (c["item"], c["valor"])
        if c.get("de_livro") and k in vistos:
            continue
        vistos.add(k)
        cert.append(c)
    h["certidoes"] = cert
    docs = {c["documento_id"] for c in cert if c.get("documento_id")} | {a["documento_id"] for a in h["achados"] if a.get("documento_id")}
    h["documentos"] = []
    if docs:
        cur = con.execute(f"SELECT id, url, tipo, paginas, oficial, drive_id, leitor, obtido_em FROM documento WHERE id IN ({','.join('?' * len(docs))})", list(docs))
        h["documentos"] = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    # a escada de cada achado (o degrau que conseguiu, o motor e a fonte), para a página das etapas do livro
    if h["achados"]:
        ids_a = [a["id"] for a in h["achados"]]
        esc = {}
        for i, d in con.execute(f"SELECT id, dados FROM achado WHERE id IN ({','.join('?' * len(ids_a))})", ids_a):
            try:
                e = (json.loads(d or "{}") or {}).get("escada")
            except ValueError:
                e = None
            if isinstance(e, str):
                try:
                    e = json.loads(e.replace("'", '"'))
                except ValueError:
                    e = {"degrau": e}
            if e:
                esc[i] = e
        for a in h["achados"]:
            if a["id"] in esc:
                a["escada"] = esc[a["id"]]
    # a oportunidade anterior: os livros unidos a este (o mais recente primeiro), com os dados e as certidões de cada um
    h["anteriores"] = []
    for outro in reversed(ids[1:]):
        try:
            cur = con.execute("SELECT * FROM livro WHERE id = ?", (outro,))
            lv2 = cur.fetchone()
            if not lv2:
                continue
            lv2 = dict(zip([c[0] for c in cur.description], lv2))
            cur = con.execute("SELECT * FROM livro_dados WHERE livro_id = ?", (outro,))
            dd2 = cur.fetchone()
            dd2 = dict(zip([c[0] for c in cur.description], dd2)) if dd2 else None
        except sqlite3.Error:
            continue
        h["anteriores"].append({"livro": lv2, "dados": dd2, "certidoes": [c for c in h["certidoes"] if c.get("de_livro") == outro],
                                "uniao": next((u for u in h["unioes"] if u.get("livro_unido") == outro), None)})
    primeiro = h["achados"][0] if h["achados"] else None
    h["motor_que_gerou"] = primeiro["motor"] if primeiro else None
    h["motores"] = sorted({a["motor"] for a in h["achados"]})
    return json.loads(json.dumps(h, default=str))
