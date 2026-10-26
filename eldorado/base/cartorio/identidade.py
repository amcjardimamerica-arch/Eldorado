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


LUGARES = ("acre", "alagoas", "amapa", "amazonas", "bahia", "ceara", "distrito federal", "espirito santo", "goias", "maranhao",
           "mato grosso", "mato grosso do sul", "minas gerais", "para", "paraiba", "parana", "pernambuco", "piaui", "rio de janeiro",
           "rio grande do norte", "rio grande do sul", "rondonia", "roraima", "santa catarina", "sao paulo", "sergipe", "tocantins",
           "brasil", "nacional", "internacional")


def titulo_normal(t: str | None) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    # o sufixo de lugar acrescentado pelo sistema (" — Goiás", " — Goiás / Cidade", " — Brasil"), repetido ou não; só o que
    # É um lugar (25/10/2026: " - Circo", " - Dança" saíam junto e os editais da PNAB ficavam com o mesmo nome)
    while True:
        m = re.search(r"\s+[—–-]\s+([^—–-]{2,60})$", t)
        if not m or not (m.group(1).strip().split(" / ")[0].strip() in LUGARES or " / " in m.group(1)):
            break
        t = t[: m.start()]
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def generico(t: str) -> bool:
    """Título que não identifica a oportunidade sozinho (poucas palavras próprias)."""
    proprias = [w for w in t.split() if w not in PALAVRAS_VAZIAS and not w.isdigit() and len(w) > 2]
    return len(proprias) < 3


def _link(u: str | None) -> str:
    return re.sub(r"^https?://(www\.)?", "", (u or "").strip().lower()).rstrip("/")


def indice(lv: dict[str, Any]) -> str | None:
    """A chave do índice (titular, 25/10/2026): NÍVEL · ÁREA · SITE; o prazo e o objeto confirmam depois, e o nome é a
    última parte. Sem nível ou sem site, o livro não tem índice (vale o nome e o link)."""
    nivel, area, _prazo, site = (lv.get("codigo") or "? · ? · ? · ?").split(" · ")
    return None if "?" in (nivel, site) else f"{nivel} · {area} · {site}"


def mesma_oportunidade(a: dict[str, Any], b: dict[str, Any]) -> str | None:
    """O motivo, se a e b são a mesma oportunidade; None, se não (ou se há conflito). A ordem da titular: o índice
    identifica (nível, área e site), o prazo e o objeto confirmam ou separam, e o nome é a última parte."""
    ia, ib = indice(a), indice(b)
    if ia and ia == ib:
        if a.get("fim") and b.get("fim") and a["fim"] != b["fim"]:
            return None                                              # prazos diferentes: edições ou oportunidades diferentes
        if not nome_muito_diferente(a, b):
            return f"o mesmo índice ({ia}), o prazo compatível e o mesmo nome"
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


# ------------------------------------------------------------------ o código da oportunidade (25/10/2026)
AREAS = (("CUL", r"cultur|arte|patrim|audiovis|music|teatr|danca|literat|aldir|pnab|rouanet"), ("ESP", r"esport|atleta|paradesport|lazer"),
         ("EDU", r"educa|escol|ensino|bolsa de estudo|capacita"), ("AMB", r"ambient|clima|sustent|florest|agua|biodivers|cerrado"),
         ("SAU", r"saude|sus\b|hospital|medic"), ("SOC", r"assistencia social|social|crianca|idoso|vulnerab|fome|direitos da"),
         ("CIE", r"ciencia|tecnolog|inovac|pesquisa|cnpq|fapeg|finep"), ("DIR", r"direitos humanos|igualdade|mulher|lgbt|racial|indigen"))
NIVEL = {"internacional": "INT", "federal": "FED", "nacional": "FED", "estadual": "EST", "municipal": "MUN", "privada": "PRI"}


def _sem_acento(t: str) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def codigo(lv: dict[str, Any]) -> str:
    """NÍVEL · ÁREA · PRAZO · SITE (o que falta fica marcado com ?)."""
    esfera, abr = (lv.get("esfera") or "").lower(), (lv.get("abrangencia") or "").lower()
    nivel = NIVEL.get(esfera) or ("INT" if "internac" in abr else "MUN" if abr.startswith("municipal") else "EST" if abr.startswith("estadual")
                                  else "FED" if abr == "nacional" else "?")
    if nivel in ("EST", "MUN") and lv.get("uf"):
        nivel += "-" + str(lv["uf"]).upper()
    fonte = _sem_acento(lv.get("area") or "") or _sem_acento(lv.get("titulo") or "")
    areas = [a for a, rx in AREAS if re.search(rx, fonte)]
    area = areas[0] if len(areas) == 1 else ("MUL" if areas else "?")
    prazo = (lv.get("fim") or "").replace("-", "")[:8] or "SEM-PRAZO"
    site = re.sub(r"^www\.", "", (re.sub(r"^https?://", "", (lv.get("oficial") or "").lower()).split("/")[0])) or "?"
    return f"{nivel} · {area} · {prazo} · {site}"


NUM = re.compile(r"n[ºo°.]*\s*(\d{1,4})\s*/\s*(\d{2,4})")


def _tokens(t: str) -> set[str]:
    return {w for w in t.split() if w not in PALAVRAS_VAZIAS and len(w) > 2 and not w.isdigit()}


def nome_muito_diferente(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Com o mesmo código, só se separa com o nome muito diferente: números de edital diferentes, objetos certificados
    diferentes, ou pouco em comum nos nomes (o caso da Aldir Blanc: os mesmos dados e objetos diferentes)."""
    na, nb = NUM.search(_sem_acento(a.get("titulo") or "")), NUM.search(_sem_acento(b.get("titulo") or ""))
    if na and nb and (int(na.group(1)), na.group(2)[-2:]) != (int(nb.group(1)), nb.group(2)[-2:]):
        return True
    oa, ob = _tokens(titulo_normal(a.get("objeto"))), _tokens(titulo_normal(b.get("objeto")))
    if oa and ob and len(oa & ob) / len(oa | ob) < 0.4:
        return True
    ta, tb = _tokens(a["t"]), _tokens(b["t"])
    if not ta or not tb or len(ta & tb) / len(ta | tb) < 0.5:
        return True
    # cada nome com uma palavra ou um número que o outro não tem: são objetos diferentes (a PNAB Goiás: Circo × Dança;
    # o Goyazes: até R$ 20 mil × de R$ 20 mil a R$ 250 mil); os repetidos de verdade diferem só por acréscimos de um lado
    da, db = set(a["t"].split()) - set(b["t"].split()), set(b["t"].split()) - set(a["t"].split())
    substantivas = lambda x: {w for w in x if (w.isdigit() or (w not in PALAVRAS_VAZIAS and len(w) > 2))}  # noqa: E731
    return bool(substantivas(da)) and bool(substantivas(db))


def _livros(con: sqlite3.Connection) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    linhas = con.execute(
        "SELECT l.id, l.titulo, l.uf, l.link_oficial AS oficial, l.link_divulgacao AS divulgacao, l.estrela, l.criado_em, "
        "d.inscricao_fim AS fim, d.municipio, d.esfera, d.abrangencia, d.area, "
        "(SELECT c.valor FROM certidao c WHERE c.livro_id = l.id AND c.item = 'Objeto' AND c.situacao = 'comprovado' ORDER BY c.id DESC LIMIT 1) AS objeto, "
        "(SELECT COUNT(*) FROM certidao c WHERE c.livro_id = l.id AND c.situacao = 'comprovado') AS certs "
        "FROM livro l LEFT JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao NOT IN ('excluido', 'unido')").fetchall()
    con.row_factory = None
    saida = [{**dict(r), "t": titulo_normal(r["titulo"])} for r in linhas]
    for lv in saida:
        lv["codigo"] = codigo(lv)
    return saida


def grupos(con: sqlite3.Connection) -> list[tuple[str, list[tuple[str, str]]]]:
    """Os livros repetidos: [(o livro que fica, [(o unido, o motivo)])]. Os candidatos vêm de duas chaves (o código
    completo e o nome); as uniões se encadeiam (A = B e B = C: os três num só livro)."""
    livros = _livros(con)
    por_id = {lv["id"]: lv for lv in livros}
    baldes: dict[str, list[dict]] = defaultdict(list)
    for lv in livros:
        if indice(lv):
            baldes["indice:" + indice(lv)].append(lv)                 # o índice identifica os candidatos
        if lv["t"]:
            baldes["nome:" + lv["t"]].append(lv)
    pai: dict[str, str] = {}

    def raiz(x: str) -> str:
        while pai.get(x, x) != x:
            x = pai.get(x, x)
        return x
    motivos: dict[str, str] = {}
    for lista in baldes.values():
        if len(lista) < 2:
            continue
        if len(lista) > 400:                                           # um balde gigante: só os de nome igual se comparam
            sub: dict[str, list] = defaultdict(list)
            for x in lista:
                sub[x["t"]].append(x)
            lista = [x for v in sub.values() if len(v) > 1 for x in v]
        for k, a in enumerate(lista):
            for b in lista[k + 1:]:
                if raiz(a["id"]) == raiz(b["id"]):
                    continue
                m = mesma_oportunidade(a, b)
                if m:
                    ra, rb = raiz(a["id"]), raiz(b["id"])
                    pai[rb] = ra
                    motivos[b["id"]] = motivos.get(b["id"]) or m
                    motivos[a["id"]] = motivos.get(a["id"]) or m
    comp: dict[str, list[dict]] = defaultdict(list)
    for x in list(pai):
        comp[raiz(x)].append(por_id[x])
    for r in list(comp):
        comp[r].append(por_id[r])
    saida = []
    for membros in comp.values():
        membros = list({m["id"]: m for m in membros}.values())
        membros.sort(key=lambda x: (-RANK.get(x["estrela"], 0), -x["certs"], x["criado_em"] or ""))
        fica = membros[0]
        saida.append((fica["id"], [(m["id"], motivos.get(m["id"], "a mesma oportunidade")) for m in membros[1:]]))
    return [g for g in saida if g[1]]


def codigos_a_gravar(con: sqlite3.Connection) -> list[tuple[str, str]]:
    """Os livros cujo código mudou (o índice novo, gravado no livro)."""
    atuais = dict(con.execute("SELECT livro_id, codigo FROM livro_dados"))
    return [(lv["id"], lv["codigo"]) for lv in _livros(con) if lv["id"] in atuais and atuais[lv["id"]] != lv["codigo"]]


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
        cods = 0
        if False:   # 25/10/2026: o código de cada livro é o do Comandante (LOCAL·ÁREA·NATUREZA·OBJETO), no nó organizar_livros
            for lid, cod in codigos_a_gravar(con):
                contexto.diario.emitir("livro.codigo", "identidade", {"livro_id": lid, "codigo": cod})
                cods += 1
        n = 0
        for fica, unidos in grupos(con):
            for unido, motivo in unidos:
                unir(con, contexto.diario, fica, unido, motivo)
                n += 1
    finally:
        con.close()
    return [{"unidos": n, "codigos": cods}]
