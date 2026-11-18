"""17/11/2026 (titular, decisão de 16/11 — C-20): toda empresa que tem oportunidade tem vínculo empresa–livro; o setor público
fica sem vínculo com empresa. A cada passagem: o livro vivo de esfera PRIVADA ou INTERNACIONAL com o financiador identificado
(o órgão do livro ou o financiador do catálogo de ouro) ganha o vínculo com a empresa do cadastro (pelo nome); sem a empresa no
cadastro, ela entra pelo nome, «a completar (sem CNPJ)». Livros de esfera federal, estadual e municipal não geram vínculo."""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from typing import Any

PRIVADAS = ("privada", "internacional")


def _norm(t: str | None) -> str:
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(s\.?a\.?|ltda|eireli|me|epp|cia|companhia|grupo)\b", " ", t)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split())


def _financiador(orgao: str | None, catalogo_ouro: str | None) -> str | None:
    try:
        f = ((json.loads(catalogo_ouro or "{}") or {}).get("catalogo") or {}).get("financiador")
    except (ValueError, TypeError):
        f = None
    nome = (f or orgao or "").split("—")[0].strip()
    return nome if len(_norm(nome)) >= 4 else None


def vincular(con: sqlite3.Connection, diario, agora: str) -> dict[str, Any]:
    try:
        livros = con.execute("SELECT l.id, l.titulo, l.orgao, l.link_oficial, d.esfera, d.inscricao_inicio, d.inscricao_fim, d.catalogo_ouro "
                             "FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao NOT IN ('excluido', 'unido')").fetchall()
        empresas = con.execute("SELECT cnpj, razao_social, nome_fantasia FROM empresa").fetchall()
        ja = {r[0] for r in con.execute("SELECT livro_id FROM vinculo_livro")}
    except sqlite3.Error:
        return {"vinculos": 0}
    por_nome: dict[str, str] = {}
    for cnpj, rs, nf in empresas:
        for n in (nf, rs):
            if n and _norm(n):
                por_nome.setdefault(_norm(n), cnpj)
    vinculos = novas = 0
    for lid, titulo, orgao, link, esfera, ini, fim, cat in livros:
        if lid in ja or (esfera or "") not in PRIVADAS:      # o setor público fica sem vínculo com empresa
            continue
        nome = _financiador(orgao, cat)
        if not nome:
            continue
        cnpj = por_nome.get(_norm(nome))
        if not cnpj:                                    # a empresa entra pelo nome e fica «a completar»
            cnpj = "nome:" + _norm(nome).replace(" ", "-")[:80]
            if cnpj not in por_nome.values():
                diario.emitir("empresa.registrada", "cartorio", {"cnpj": cnpj, "razao_social": nome[:200], "nome_fantasia": nome[:200],
                                                                  "atividade_principal": "a completar (sem CNPJ): financiador de livro",
                                                                  "descoberta_por": "motor", "descoberta_em": agora, "atualizada_em": agora})
                por_nome[_norm(nome)] = cnpj
                novas += 1
        diario.emitir("vinculo_livro.registrado", "cartorio", {"cnpj": cnpj, "livro_id": lid, "papel": "financiador", "em": agora})
        diario.emitir("oportunidade_empresa.registrada", "cartorio", {"id": f"livro:{lid}", "cnpj": cnpj, "titulo": (titulo or lid)[:300],
                                                                      "tipo": "livro", "link_oficial": link, "abertura": ini,
                                                                      "encerramento": fim, "encontrada_por": "cartorio", "encontrada_em": agora})
        vinculos += 1
    return {"vinculos": vinculos, "empresas_novas_pelo_nome": novas}
