"""A identidade das oportunidades (titular, 24/10/2026): a mesma oportunidade não pode ter mais de um livro. O que já tem
livro agrega ao livro existente; o que está repetido no banco é reunido num só livro.

Mesma oportunidade = o mesmo título (sem acentos, pontuação e o sufixo de estado/cidade que o sistema acrescenta) E pelo
menos uma prova a mais: o mesmo link (oficial ou de divulgação), ou o mesmo prazo final e o mesmo território. Nunca une
com conflito: prazos finais diferentes (edições diferentes) ou municípios diferentes. Títulos genéricos ("Edital 2026",
"Chamamento público nº 06/2026") só se unem com o mesmo link.

A união é completa e nada se apaga: os achados e as certidões do livro unido passam ao livro que fica, os links que faltam
são completados, e o unido ganha a situação "unido" (a tabela uniao aponta para o que ficou).
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

PALAVRAS_VAZIAS = {"de", "da", "do", "das", "dos", "e", "a", "o", "as", "os", "para", "em", "no", "na", "nos", "nas", "por", "com",
                   "edital", "editais", "chamamento", "chamada", "publico", "publica", "processo", "selecao", "n", "numero",
                   "abre", "abertas", "inscricoes", "inscricao", "aviso", "como", "uma", "um", "sobre", "programa"}
RANK = {"ouro": 3, "prata": 2, "bronze": 1, "sem": 0, None: 0}


def titulo_normal(t: str | None) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+[—–-]\s+[^—–-]{2,40}$", "", t)                 # o sufixo " — Estado / Cidade" acrescentado pelo sistema
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def generico(t: str) -> bool:
    """Título que não identifica a oportunidade sozinho (poucas palavras próprias)."""
    proprias = [w for w in t.split() if w not in PALAVRAS_VAZIAS and not w.isdigit() and len(w) > 2]
    return len(proprias) < 3


def _link(u: str | None) -> str:
    return re.sub(r"^https?://(www\.)?", "", (u or "").strip().lower()).rstrip("/")


def mesma_oportunidade(a: dict[str, Any], b: dict[str, Any]) -> str | None:
    """O motivo, se a e b são a mesma oportunidade; None, se não (ou se há conflito)."""
    if not a["t"] or a["t"] != b["t"]:
        return None
    if a.get("fim") and b.get("fim") and a["fim"] != b["fim"]:
        return None                                                  # prazos diferentes: edições diferentes
    if a.get("municipio") and b.get("municipio") and a["municipio"] != b["municipio"]:
        return None
    if a.get("uf") and b.get("uf") and a["uf"] != b["uf"]:
        return None                                                  # UFs diferentes nunca se unem
    links_a = {x for x in (_link(a.get("oficial")), _link(a.get("divulgacao"))) if x}
    links_b = {x for x in (_link(b.get("oficial")), _link(b.get("divulgacao"))) if x}
    if links_a & links_b:
        return "o mesmo título e o mesmo link"
    if generico(a["t"]):
        return None                                                  # o genérico só se une pelo link
    territorio = (not a.get("uf") or not b.get("uf") or a["uf"] == b["uf"])
    if a.get("fim") and a.get("fim") == b.get("fim") and territorio:
        return "o mesmo título, o mesmo prazo final e o mesmo território"
    return None


def _livros(con: sqlite3.Connection) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    linhas = con.execute(
        "SELECT l.id, l.titulo, l.uf, l.link_oficial AS oficial, l.link_divulgacao AS divulgacao, l.estrela, l.criado_em, "
        "d.inscricao_fim AS fim, d.municipio, (SELECT COUNT(*) FROM certidao c WHERE c.livro_id = l.id AND c.situacao = 'comprovado') AS certs "
        "FROM livro l LEFT JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao NOT IN ('excluido', 'unido')").fetchall()
    con.row_factory = None
    return [{**dict(r), "t": titulo_normal(r["titulo"])} for r in linhas]


def grupos(con: sqlite3.Connection) -> list[tuple[str, list[tuple[str, str]]]]:
    """Os livros repetidos: [(o livro que fica, [(o unido, o motivo)])]."""
    por_titulo: dict[str, list[dict]] = defaultdict(list)
    for lv in _livros(con):
        if lv["t"]:
            por_titulo[lv["t"]].append(lv)
    saida = []
    for lista in por_titulo.values():
        if len(lista) < 2:
            continue
        lista.sort(key=lambda x: (-RANK.get(x["estrela"], 0), -x["certs"], x["criado_em"] or ""))
        restantes = list(lista)
        while restantes:
            fica, unidos = restantes.pop(0), []
            for outro in list(restantes):
                motivo = mesma_oportunidade(fica, outro)
                if motivo:
                    unidos.append((outro["id"], motivo))
                    restantes.remove(outro)
            if unidos:
                saida.append((fica["id"], unidos))
    return saida


def unir(con: sqlite3.Connection, diario, fica: str, unido: str, motivo: str) -> None:
    """A união completa (por eventos; nada se apaga)."""
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    diario.emitir("livro.unido", "identidade", {"livro_que_fica": fica, "livro_unido": unido, "em": agora, "motivo": motivo})
    for (aid,) in con.execute("SELECT id FROM achado WHERE livro_id = ?", (unido,)).fetchall():
        diario.emitir("livro.vinculado", "identidade", {"achado_id": aid, "livro_id": fica})
    con.row_factory = sqlite3.Row
    ja = {(r["item"], r["valor"]) for r in con.execute("SELECT item, valor FROM certidao WHERE livro_id = ?", (fica,))}
    for c in con.execute("SELECT * FROM certidao WHERE livro_id = ? AND situacao IN ('comprovado', 'dispensado')", (unido,)).fetchall():
        if (c["item"], c["valor"]) in ja:
            continue
        diario.emitir("certidao.gravada", "identidade", {"livro_id": fica, "item": c["item"], "valor": c["valor"], "documento_id": c["documento_id"],
                                                         "pagina": c["pagina"], "trecho": c["trecho"], "fase": c["fase"], "situacao": c["situacao"],
                                                         "justificativa": (c["justificativa"] or "") + f" (da união com o livro {unido})", "em": c["em"]})
    a = con.execute("SELECT link_oficial, link_divulgacao FROM livro WHERE id = ?", (fica,)).fetchone()
    b = con.execute("SELECT link_oficial, link_divulgacao FROM livro WHERE id = ?", (unido,)).fetchone()
    con.row_factory = None
    if a and b and ((not a["link_oficial"] and b["link_oficial"]) or (not a["link_divulgacao"] and b["link_divulgacao"])):
        diario.emitir("livro.links", "identidade", {"id": fica, "link_oficial": a["link_oficial"] or b["link_oficial"],
                                                    "link_divulgacao": a["link_divulgacao"] or b["link_divulgacao"], "atualizado_em": agora})
    diario.emitir("livro.situacao", "identidade", {"id": unido, "situacao": "unido", "atualizado_em": agora})


def no_unir_repetidos(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem: a revisão do banco; as oportunidades idênticas em mais de um livro são reunidas num só."""
    from pathlib import Path
    p = Path(parametros.get("dados", "dados")) / "biblioteca.db"
    if not p.exists():
        return [{"unidos": 0}]
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        n = 0
        for fica, unidos in grupos(con):
            for unido, motivo in unidos:
                unir(con, contexto.diario, fica, unido, motivo)
                n += 1
    finally:
        con.close()
    return [{"unidos": n}]
