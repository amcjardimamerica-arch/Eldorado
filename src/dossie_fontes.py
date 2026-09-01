"""Dossiê de cada fonte de recurso — o que o histórico ensina sobre ela.

Premissa do titular: cada fonte do catálogo de captação (e cada conselho
municipal, estadual ou federal) recebe um dossiê montado a partir dos editais
históricos da Biblioteca de Alexandria: quantos editais, em que meses abrem,
quanto duram as inscrições, que áreas atendem, o que costumam exigir, quem
venceu quando publicado — e a previsão da próxima janela provável.

Saída: `biblioteca_alexandria/fontes/<slug>/dossie.json` + índice. Fonte sem
histórico recebe dossiê declarando isso, nunca um padrão inventado.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date

from .nucleo import ROOT, load_json, now_iso, slug, write_json
from .previsao import orgao_real

SAIDA = ROOT / "biblioteca_alexandria/fontes"

_MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _fontes_catalogo() -> list[dict]:
    fontes = []
    cfg = ROOT / "config/fontes.json"
    if cfg.exists():
        for f in load_json(cfg).get("fontes", []):
            fontes.append({"id": f.get("id"), "nome": f.get("nome"),
                           "tipo": f.get("tipo"), "territorio": f.get("territorio"),
                           "url": f.get("url"), "origem": "catalogo_captacao",
                           "areas": f.get("areas") or []})
    con = ROOT / "config/conselhos.json"
    if con.exists():
        for c in load_json(con).get("conselhos", []):
            fontes.append({"id": c["id"], "nome": c["nome"], "tipo": f'conselho_{c["esfera"]}',
                           "territorio": c["territorio"], "url": c.get("url"),
                           "origem": "conselho", "areas": [c["area"]],
                           "fundo": c.get("fundo"), "lei": c.get("lei")})
    return fontes


def _tokens(nome: str) -> set[str]:
    return {t for t in re.findall(r"[a-zà-ú]{4,}", (nome or "").lower())
            if t not in {"prefeitura", "municipal", "estadual", "secretaria", "conselho",
                         "goiás", "goiania", "goiânia", "estado", "governo", "portal",
                         "diário", "oficial", "editais", "fundação", "instituto"}}


_AGREGADORES = re.compile(r"querido di[áa]rio|pncp|portal nacional de contrata", re.I)


def eh_agregador(fonte: dict) -> bool:
    """Agregador (Querido Diário, PNCP) não é fonte de recurso: é canal.
    Não recebe dossiê de financiador — os editais que ele republica são
    atribuídos ao ÓRGÃO real."""
    return bool(_AGREGADORES.search(fonte.get("nome") or ""))


def _casa(fonte: dict, orgao: str, financiador: str, titulo: str) -> bool:
    """A fonte e o registro histórico falam do mesmo órgão?

    Regra estrita: TODOS os tokens distintivos do nome da fonte precisam
    aparecer no órgão real ou no financiador do registro — o título não conta,
    porque menciona temas genéricos (criança, fundo, cultura) e produzia
    casamentos falsos (Conanda e UNESCO com centenas de editais alheios)."""
    fid = str(fonte.get("id") or "").lower()
    alvo = " ".join((orgao or "", financiador or "")).lower()
    if fid and len(fid) >= 5 and fid in alvo.replace(" ", "-"):
        return True
    tk = _tokens(fonte.get("nome") or "")
    return bool(tk) and all(t in alvo for t in tk)


def montar(con: sqlite3.Connection | None = None, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    fechar = con is None
    if con is None:
        from .banco import conectar
        con = conectar()
    rows = con.execute(
        "SELECT financiador, titulo, area, uf, data_publicacao, inicio, fim, "
        "vencedores, exigencias, chave, ano FROM historico").fetchall()
    if fechar:
        con.close()
    regs = [{"orgao": orgao_real(r[0], r[1]), "financiador": r[0], "titulo": r[1],
             "area": r[2], "uf": r[3], "pub": r[4], "inicio": r[5], "fim": r[6],
             "vencedores": json.loads(r[7] or "[]"), "exigencias": json.loads(r[8] or "[]"),
             "chave": r[9], "ano": r[10]} for r in rows]
    SAIDA.mkdir(parents=True, exist_ok=True)
    indice, com_historico = [], 0
    for fonte in _fontes_catalogo():
        if eh_agregador(fonte):
            indice.append({"id": fonte["id"], "nome": fonte["nome"], "origem": fonte["origem"],
                           "tipo": "agregador", "territorio": fonte["territorio"],
                           "editais": 0, "meses_recorrentes": [], "proxima_janela": None,
                           "nota": "canal agregador — editais atribuídos ao órgão real"})
            continue
        casos = [r for r in regs if _casa(fonte, r["orgao"], r["financiador"], r["titulo"])]
        meses = Counter(); anos = set(); duracoes = []; areas = Counter()
        exig = Counter(); venc = Counter()
        for c in casos:
            d = c["inicio"] or c["pub"]
            if d:
                meses[int(d[5:7])] += 1; anos.add(d[:4])
            if c["inicio"] and c["fim"] and c["fim"] > c["inicio"]:
                duracoes.append((date.fromisoformat(c["fim"]) - date.fromisoformat(c["inicio"])).days)
            areas[c["area"] or "outros"] += 1
            exig.update(c["exigencias"]); venc.update(c["vencedores"])
        recorrentes = [m for m, n in meses.items() if n >= 2]
        proxima = None
        if recorrentes:
            futuros = sorted(m for m in recorrentes if m > hoje.month) or sorted(recorrentes)
            m = futuros[0]
            ano = hoje.year if m > hoje.month else hoje.year + 1
            proxima = {"mes": f"{ano}-{m:02d}", "base": f"{meses[m]} ocorrência(s) em {_MESES[m-1]}",
                       "confianca": "alta" if meses[m] >= 3 else "media"}
        dossie = {
            "fonte": fonte, "gerado_em": now_iso(),
            "editais_no_historico": len(casos),
            "anos_com_publicacao": sorted(anos),
            "meses_de_abertura": {_MESES[m-1]: n for m, n in sorted(meses.items())},
            "meses_recorrentes": [_MESES[m-1] for m in sorted(recorrentes)],
            "duracao_tipica_inscricao_dias": (round(sum(duracoes)/len(duracoes)) if duracoes else None),
            "areas_atendidas": dict(areas.most_common()),
            "exigencias_frequentes": [{"exigencia": e, "n": n} for e, n in exig.most_common(10)],
            "vencedores_conhecidos": [{"entidade": v, "n": n} for v, n in venc.most_common(10)],
            "proxima_janela_provavel": proxima,
            "casos": [{"ano": c["ano"], "chave": c["chave"], "titulo": (c["titulo"] or "")[:110],
                       "inicio": c["inicio"], "fim": c["fim"]} for c in casos[:40]],
            "nota": ("dossiê montado exclusivamente do histórico catalogado; fonte sem "
                     "casos recebe dossiê vazio — nenhum padrão é inventado"
                     if casos else
                     "sem editais desta fonte no histórico da Biblioteca; a rota "
                     "de monitoramento segue ativa"),
        }
        pasta = SAIDA / slug(fonte["id"] or fonte["nome"])
        write_json(pasta / "dossie.json", dossie)
        com_historico += bool(casos)
        indice.append({"id": fonte["id"], "nome": fonte["nome"], "origem": fonte["origem"],
                       "tipo": fonte["tipo"], "territorio": fonte["territorio"],
                       "editais": len(casos), "meses_recorrentes": dossie["meses_recorrentes"],
                       "proxima_janela": proxima, "pasta": str(pasta.relative_to(ROOT))})
    resumo = {"gerado_em": now_iso(), "fontes": len(indice), "com_historico": com_historico,
              "conselhos": sum(1 for i in indice if i["origem"] == "conselho"),
              "itens": indice}
    write_json(SAIDA / "indice.json", resumo)
    return resumo


if __name__ == "__main__":
    r = montar()
    print(json.dumps({k: v for k, v in r.items() if k != "itens"}, ensure_ascii=False, indent=2))
