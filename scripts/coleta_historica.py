#!/usr/bin/env python3
"""BASE HISTÓRICA DOS INCENTIVOS — 5 anos, para o Piloto não pesquisar o que já é público.

Roda no servidor do GitHub (tem internet; o ambiente de desenvolvimento não alcança os portais do
governo). Um adaptador por fonte; cada um grava o que obteve e, quando não obtém, grava POR QUÊ — a
lacuna fica visível em vez de virar silêncio.

    fonte        o que se busca                                        caminho
    rouanet      projetos aprovados e INCENTIVADORES (empresas, valores) API pública do SALIC
    esporte      projetos e patrocinadores da Lei de Incentivo ao Esporte portal de dados abertos (CKAN)
    pronon       instituições e projetos aprovados                     portal de dados abertos (CKAN)
    pronas       instituições e projetos aprovados                     portal de dados abertos (CKAN)
    fia          fundos da infância (CNPJ dos fundos) e repasses       portal de dados abertos (CKAN)
    idoso        fundos do idoso                                        portal de dados abertos (CKAN)
    pat          empresas beneficiárias do PAT                          portal de dados abertos (CKAN)
    goyazes      projetos aprovados pela Lei Goyazes (Secult-GO)        sem base estruturada pública conhecida

Saída: biblioteca_alexandria/base/incentivos/<fonte>.jsonl.gz, empresas_incentivadoras.jsonl (a lista
de empresas que já destinaram por lei, que o Piloto consulta antes de "descobrir" uma empresa) e
status.json com o resultado de cada fonte.

    python3 scripts/coleta_historica.py [fonte ...]
"""
from __future__ import annotations

import gzip
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "biblioteca_alexandria/base/incentivos"
ANOS = list(range(date.today().year - 4, date.today().year + 1))   # os últimos 5 anos
UA = {"User-Agent": "Eldorado/1.0 (coleta de dados publicos; associacao sem fins lucrativos)", "Accept": "application/json"}


def get(url: str, tempo: float = 40) -> tuple[int, object]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=tempo) as r:
            corpo = r.read()
            try:
                return r.status, json.loads(corpo.decode("utf-8", "ignore"))
            except ValueError:
                return r.status, corpo
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return -1, str(e)[:120]


def gravar(nome: str, linhas: list[dict]) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    with gzip.open(SAIDA / f"{nome}.jsonl.gz", "wt", encoding="utf-8") as f:
        for x in linhas:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    return len(linhas)


# ── ROUANET (SALIC) ─────────────────────────────────────────────────────────────────────────
SALIC = "https://api.salic.cultura.gov.br/api/v1"


def _salic_paginas(caminho: str, params: dict, teto: int = 400) -> tuple[list[dict], dict]:
    itens, diag, offset = [], {"paginas": 0, "http": []}, 0
    while diag["paginas"] < teto:
        q = urllib.parse.urlencode({**params, "limit": 100, "offset": offset})
        cod, d = get(f"{SALIC}/{caminho}?{q}")
        diag["http"].append(cod) if len(diag["http"]) < 5 else None
        if cod != 200 or not isinstance(d, dict):
            break
        emb = d.get("_embedded") or {}
        lote = next((v for v in emb.values() if isinstance(v, list)), []) if emb else (d.get("items") or [])
        if not lote:
            break
        itens += lote; diag["paginas"] += 1; offset += 100
        if len(lote) < 100:
            break
        time.sleep(0.3)
    return itens, diag


def rouanet() -> dict:
    projetos, dp = [], {}
    for uf in ("GO",):
        p, dp = _salic_paginas("projetos", {"UF": uf, "format": "json"})
        projetos += [x for x in p if str(x.get("ano_projeto") or x.get("data_inicio") or "")[:4].isdigit()
                     and int(str(x.get("ano_projeto") or x.get("data_inicio"))[:4]) >= ANOS[0]] or p
    inc, di = _salic_paginas("incentivadores", {"tipo_pessoa": "juridica", "format": "json"}, teto=800)
    n1 = gravar("rouanet_projetos_go", [{k: x.get(k) for k in ("PRONAC", "nome", "UF", "municipio", "area", "segmento", "valor_aprovado",
                                                               "valor_captado", "data_inicio", "data_termino", "proponente", "cgccpf") if k in x} for x in projetos])
    empresas = [{"nome": x.get("nome"), "cnpj": x.get("cgccpf"), "uf": x.get("UF"), "municipio": x.get("municipio"),
                 "total_doado": x.get("total_doado"), "lei": "Rouanet", "fonte": "SALIC"} for x in inc if x.get("nome")]
    n2 = gravar("rouanet_incentivadores", empresas)
    return {"projetos_go": n1, "incentivadores_pj": n2, "diag_projetos": dp, "diag_incentivadores": di,
            "empresas": empresas}


# ── PORTAL DE DADOS ABERTOS (CKAN) ───────────────────────────────────────────────────────────
CKAN = ["https://dados.gov.br/api/3/action/package_search", "https://dados.gov.br/dados/api/publico/conjuntos-dados"]


def ckan(consulta: str, nome: str) -> dict:
    tentativas = []
    for base in CKAN:
        cod, d = get(f"{base}?{urllib.parse.urlencode({'q': consulta, 'rows': 20})}")
        tentativas.append({"url": base, "http": cod})
        res = ((d or {}).get("result") or {}).get("results") if isinstance(d, dict) else None
        if cod == 200 and res:
            recursos = [{"conjunto": r.get("title"), "orgao": (r.get("organization") or {}).get("title"),
                         "arquivos": [{"nome": x.get("name"), "formato": x.get("format"), "url": x.get("url")}
                                      for x in (r.get("resources") or []) if str(x.get("format", "")).lower() in ("csv", "json", "xlsx", "xls", "zip")]}
                        for r in res]
            linhas = []
            for rc in recursos[:3]:
                for arq in rc["arquivos"][:2]:
                    if str(arq["formato"]).lower() == "csv" and arq.get("url"):
                        c2, corpo = get(arq["url"], tempo=90)
                        if c2 == 200 and isinstance(corpo, (bytes, bytearray)):
                            import csv, io
                            txt = corpo.decode("utf-8", "ignore") if b"\xef\xbb\xbf" not in corpo[:3] else corpo.decode("utf-8-sig", "ignore")
                            sep = ";" if txt[:2000].count(";") > txt[:2000].count(",") else ","
                            for row in list(csv.DictReader(io.StringIO(txt), delimiter=sep))[:200000]:
                                linhas.append({**row, "_conjunto": rc["conjunto"]})
            n = gravar(nome, linhas) if linhas else 0
            return {"conjuntos": [{"conjunto": r["conjunto"], "orgao": r["orgao"], "arquivos": len(r["arquivos"])} for r in recursos[:8]],
                    "linhas": n, "tentativas": tentativas}
    return {"conjuntos": [], "linhas": 0, "tentativas": tentativas,
            "lacuna": "o portal de dados abertos não respondeu à consulta pública (o portal novo exige chave de acesso)"}


FONTES_CKAN = {
    "esporte": "lei de incentivo ao esporte projetos",
    "pronon": "PRONON oncologia projetos",
    "pronas": "PRONAS pessoa com deficiencia projetos",
    "fia": "fundo da infancia e adolescencia",
    "idoso": "fundo do idoso",
    "pat": "programa de alimentacao do trabalhador empresas",
}


def goyazes() -> dict:
    return {"linhas": 0, "lacuna": "a Secult-GO publica os resultados da Lei Goyazes em PDF, sem base estruturada pública; "
                                   "o caminho é o Diário Oficial de Goiás (motor do-goias) e os editais da Secult (plat-secult-go)"}


def main(escolha: list[str]) -> dict:
    status = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "anos": ANOS, "fontes": {}}
    empresas = []
    for f in escolha or (["rouanet"] + list(FONTES_CKAN) + ["goyazes"]):
        try:
            if f == "rouanet":
                r = rouanet(); empresas += r.pop("empresas", [])
            elif f == "goyazes":
                r = goyazes()
            else:
                r = ckan(FONTES_CKAN[f], f)
        except Exception as e:
            r = {"erro": f"{type(e).__name__}: {str(e)[:120]}"}
        status["fontes"][f] = r
        print(f"{f}: {json.dumps({k: v for k, v in r.items() if k in ('projetos_go','incentivadores_pj','linhas','lacuna','erro')}, ensure_ascii=False)}")
    if empresas:
        vistos, lista = set(), []
        for e in empresas:
            k = (str(e.get("cnpj") or "") or str(e.get("nome") or "").lower())[:40]
            if k and k not in vistos:
                vistos.add(k); lista.append(e)
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / "empresas_incentivadoras.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lista), encoding="utf-8")
        status["empresas_incentivadoras"] = len(lista)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
    return status


if __name__ == "__main__":
    main(sys.argv[1:])
