"""K3 (R57, titular, 14/11/2026): o motivo do descarte volta para o Comandante — cada descarte é classificado nas seis classes
da Lição 4 do estudo e somado por motor, família do Espião e domínio. O domínio com 20 descartes ou mais e menos de 5% de
livros úteis (Farol ou arquivo) entra na lista de RUÍDO do crivo do Espião. Gravado uma vez por dia no Cérebro (medições
«descartes:classes» e «crivo:ruido»)."""
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlsplit

CLASSES = (
    ("link quebrado ou sem dados", re.compile(r"(?i)link quebrad|sem dados|sem t[íi]tulo|sem link|n[ãa]o abriu|404|p[áa]gina n[ãa]o (existe|encontrada)|vazi")),
    ("notícia ou página genérica",
     re.compile(r"(?i)not[íi]cia|p[áa]gina gen[ée]rica|n[ãa]o [ée] (oportunidade|edital)|institucional|evento|programa[çc][ãa]o|listagem")),
    ("fora do território", re.compile(r"(?i)territ[óo]rio|outro estado|munic[íi]pio de outro|fora de goi[áa]s|n[ãa]o capital|interior")),
    ("licitação ou compra", re.compile(r"(?i)licita[çc]|preg[ãa]o|compra|contrata[çc][ãa]o|aquisi[çc][ãa]o|fornecedor")),
    ("só para pessoa física", re.compile(r"(?i)pessoa f[íi]sica|bolsa|est[áa]gio|concurso p[úu]blico|vaga|individual")),
)
RUIDO_MIN_DESCARTES, RUIDO_MAX_UTEIS = 20, 0.05


def classificar(motivo: str) -> str:
    for nome, rx in CLASSES:
        if rx.search(motivo or ""):
            return nome
    return "outros"


def _dominio(url: str | None) -> str:
    return (urlsplit(url or "").hostname or "").lower().removeprefix("www.")


def medir(bib: sqlite3.Connection) -> dict[str, Any]:
    """As classes por motor, família e domínio, e os domínios de ruído."""
    from .destino import destinos
    dest = destinos(bib)
    origem: dict[str, tuple[str, str | None]] = {}
    for lid, mot, dados in bib.execute("SELECT livro_id, motor, dados FROM achado WHERE livro_id IS NOT NULL ORDER BY encontrado_em"):
        if lid not in origem:
            fam = None
            if mot == "espiao":
                try:
                    fam = json.loads(dados or "{}").get("familia")
                except ValueError:
                    fam = None
            origem[lid] = (mot, fam)
    por_motor: dict[str, Counter] = defaultdict(Counter)
    por_familia: dict[str, Counter] = defaultdict(Counter)
    por_dominio: dict[str, Counter] = defaultdict(Counter)
    uteis_dom: Counter = Counter()
    total = Counter()
    for lid, situacao, motivo, link in bib.execute("SELECT id, situacao, justificativa_exclusao, link_divulgacao FROM livro"):
        dom = _dominio(link)
        if situacao == "excluido":
            c = classificar(motivo)
            total[c] += 1
            mot, fam = origem.get(lid, ("?", None))
            por_motor[mot][c] += 1
            if fam:
                por_familia[fam][c] += 1
            if dom:
                por_dominio[dom][c] += 1
        elif dest.get(lid, 0) >= 0.5 and dom:
            uteis_dom[dom] += 1
    ruido = sorted(d for d, c in por_dominio.items()
                   if sum(c.values()) >= RUIDO_MIN_DESCARTES and uteis_dom[d] / (sum(c.values()) + uteis_dom[d]) < RUIDO_MAX_UTEIS)
    return {"classes": dict(total), "por_motor": {k: dict(v) for k, v in por_motor.items()},
            "por_familia": {k: dict(v) for k, v in por_familia.items()}, "ruido": ruido}


def gravar_diario(bib: sqlite3.Connection, cer: sqlite3.Connection, diario, agora: datetime | None = None) -> dict | None:
    """Uma vez por dia: grava a classificação e a lista de ruído no Cérebro."""
    agora = agora or datetime.now(timezone.utc)
    try:
        ult = cer.execute("SELECT MAX(em) FROM medicao WHERE marcador = 'crivo:ruido'").fetchone()[0]
    except sqlite3.Error:
        ult = None
    if ult and agora - datetime.fromisoformat(str(ult).replace("Z", "+00:00")) < timedelta(hours=24):
        return None
    try:
        m = medir(bib)
    except sqlite3.Error:
        return None
    em = agora.isoformat(timespec="seconds")
    diario.emitir("medicao.registrada", "comandante", {"marcador": "descartes:classes", "nivel": "componente", "em": em,
                                                      "valor": sum(m["classes"].values()), "motivo": json.dumps(m, ensure_ascii=False)[:60000]})
    diario.emitir("medicao.registrada", "comandante", {"marcador": "crivo:ruido", "nivel": "componente", "em": em,
                                                      "valor": len(m["ruido"]), "motivo": json.dumps(m["ruido"], ensure_ascii=False)})
    return m


def ruido(cer: sqlite3.Connection) -> set[str]:
    """A lista de ruído mais recente (os domínios que o crivo do Espião recusa)."""
    try:
        r = cer.execute("SELECT motivo FROM medicao WHERE marcador = 'crivo:ruido' ORDER BY em DESC LIMIT 1").fetchone()
        return set(json.loads(r[0])) if r and r[0] else set()
    except (sqlite3.Error, ValueError):
        return set()
