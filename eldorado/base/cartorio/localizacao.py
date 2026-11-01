"""A localização de cada livro pelas provas que ele próprio tem (titular, 01/11/2026): a UF, o município e a esfera.

A importação do sistema anterior gravou dados errados (um edital da prefeitura de Colinas do Sul com UF "BR" e esfera
"federal"), e o dado errado separava duas fichas da mesma oportunidade (índices diferentes) ou deixava de separar duas
diferentes. Aqui, cada livro é conferido contra as próprias provas, na ordem de força: a certidão de Território, o site
oficial (o domínio de prefeitura ou de estado) e o órgão. Só corrige o que a prova sustenta; o resto fica como está.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from typing import Any

UFS = {"ac": "acre", "al": "alagoas", "ap": "amapa", "am": "amazonas", "ba": "bahia", "ce": "ceara", "df": "distrito federal",
       "es": "espirito santo", "go": "goias", "ma": "maranhao", "mt": "mato grosso", "ms": "mato grosso do sul", "mg": "minas gerais",
       "pa": "para", "pb": "paraiba", "pr": "parana", "pe": "pernambuco", "pi": "piaui", "rj": "rio de janeiro", "rn": "rio grande do norte",
       "rs": "rio grande do sul", "ro": "rondonia", "rr": "roraima", "sc": "santa catarina", "sp": "sao paulo", "se": "sergipe",
       "to": "tocantins"}
NOME_UF = {v: k for k, v in UFS.items()}
# os órgãos estaduais com domínio <sigla>.<uf>.gov.br (não são municípios)
ORGAOS_ESTADUAIS = {"secult", "seduc", "saude", "seds", "segov", "sedi", "casacivil", "fapeg", "fapesc", "fapesp", "fapemig", "faperj",
                    "cultura", "educacao", "esporte", "social", "governo", "diariooficial", "doe", "sefaz", "economia", "sead", "seplan",
                    "agricultura", "meioambiente", "semad", "detran", "pc", "pm", "tj", "mp", "tce", "alego", "al", "assembleia", "sejus",
                    "sigrp", "portal", "www", "sic", "transparencia", "ouvidoria", "fomento", "goiasfomento", "emater", "seinfra", "sedh"}


def _n(t: str | None) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c)).strip()


def _uf_de(texto: str | None) -> str | None:
    t = _n(texto)
    m = re.search(r"(?:/|\s-\s|,\s*|\()\s*([a-z]{2})\s*\)?\s*$", t)
    if m and m.group(1) in UFS:
        return m.group(1).upper()
    if t in UFS:
        return t.upper()
    for nome, sigla in sorted(NOME_UF.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"\b{nome}\b", t):
            return sigla.upper()
    return None


def _host(u: str | None) -> str:
    m = re.match(r"https?://(www\.)?([^/]+)", (u or "").strip().lower())
    return m.group(2) if m else ""


def provas(lv: dict[str, Any]) -> dict[str, Any]:
    """O que as provas do livro dizem: {uf, municipio, esfera, motivo} (só o que é sustentado)."""
    out: dict[str, Any] = {}
    ter = _n(lv.get("territorio"))
    if ter:
        if re.search(r"\b(nacional|todo o (territorio|pais|brasil)|brasil)\b", ter) and "/" not in ter:
            out.update(uf="BR", motivo="a certidão de Território (nacional)")
        else:
            m = re.match(r"^(?:municipio de |cidade de )?([a-z' -]{3,60}?)\s*(?:/|\s-\s|,)\s*([a-z]{2})\b", ter)
            if m and m.group(2) in UFS and m.group(1).strip() not in NOME_UF:
                out.update(uf=m.group(2).upper(), municipio=(lv.get("territorio") or "").split("/")[0].split(" - ")[0].split(",")[0].strip(),
                           esfera_mun=True, motivo=f"a certidão de Território ({lv.get('territorio')})")
            elif _uf_de(ter):
                out.update(uf=_uf_de(ter), motivo=f"a certidão de Território ({lv.get('territorio')})")
    for u in (lv.get("oficial"), lv.get("divulgacao")):
        h = _host(u)
        m = re.match(r"^(?:diariooficial\.)?([a-z0-9-]+)\.([a-z]{2})\.gov\.br$", h)
        if m and m.group(2) in UFS and "uf" not in out:
            out["uf"] = m.group(2).upper()                              # o domínio prova a UF; a esfera municipal exige a
            out.setdefault("motivo", f"o site oficial ({h})")          # certidão com o município ou um órgão municipal
        m2 = re.match(r"^([a-z]+)\.gov\.br$", h)
        if m2 and m2.group(1) in NOME_UF and "uf" not in out:
            out.update(uf=NOME_UF[m2.group(1)].upper(), esfera_est=True, motivo=f"o portal do estado ({h})")
    org = _n(lv.get("orgao"))
    m = re.search(r"\b(?:prefeitura(?: municipal)?|fundo municipal[a-z ]*?|camara municipal|secretaria municipal[a-z ]*?) de ([a-z' ]{3,40})", org)
    if m:
        out["esfera_mun"] = True
        out.setdefault("municipio", " ".join(w.capitalize() if w not in ("de", "do", "da", "dos", "das") else w for w in m.group(1).strip().split()))
        out.setdefault("motivo", f"o órgão ({lv.get('orgao')})")
    elif re.search(r"\b(governo (do estado )?de|secretaria de estado|estado de)\b", org):
        out["esfera_est"] = True
        if "uf" not in out and _uf_de(org):
            out.update(uf=_uf_de(org), motivo=f"o órgão ({lv.get('orgao')})")
    if out.get("esfera_mun"):
        out["esfera"] = "municipal"
    elif out.get("esfera_est"):
        out["esfera"] = "estadual"
    return out


def correcoes(con: sqlite3.Connection) -> list[dict[str, Any]]:
    """As correções de localização sustentadas pelas provas: [{livro_id, uf?, municipio?, esfera?, motivo}]."""
    con.row_factory = sqlite3.Row
    linhas = con.execute(
        "SELECT l.id, l.titulo, l.orgao, l.uf AS uf_l, l.link_oficial AS oficial, l.link_divulgacao AS divulgacao, "
        "d.uf AS uf_d, d.municipio, d.esfera, "
        "(SELECT c.valor FROM certidao c WHERE c.livro_id = l.id AND c.item = 'Território' AND c.situacao = 'comprovado' "
        "ORDER BY c.id DESC LIMIT 1) AS territorio "
        "FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao NOT IN ('excluido', 'unido')").fetchall()
    con.row_factory = None
    saida = []
    for r in linhas:
        lv = dict(r)
        p = provas(lv)
        c: dict[str, Any] = {}
        uf_atual = (lv["uf_l"] or lv["uf_d"] or "").upper()
        if p.get("uf") and p["uf"] != uf_atual and not (p["uf"] == "BR" and p.get("esfera") == "municipal"):
            if p["uf"] != "BR" or uf_atual in ("", "NONE"):
                c["uf"] = p["uf"]
        if p.get("municipio") and not (lv["municipio"] or "").strip():
            c["municipio"] = p["municipio"]
        if p.get("esfera") and p["esfera"] != (lv["esfera"] or "") and (lv["esfera"] or "") != "privada":   # o financiador privado fica
            c["esfera"] = p["esfera"]
        if c:
            saida.append({"livro_id": lv["id"], **c, "motivo": p.get("motivo") or "as provas do livro"})
    return saida
