#!/usr/bin/env python3
"""HISTÓRICO DE DOAÇÕES DA ROUANET, EMPRESA POR EMPRESA — retomável, das maiores para as menores.

A API pública do SALIC dá, para cada incentivador, a lista das doações (projeto/PRONAC, valor, data). O
coletor anterior guardou só o resumo (total doado); sem o histórico não há ano a ano, projeto apoiado nem
ESTADO DE DESTINO do recurso — que é o que o ranking precisa para filtrar.

Etapas (cada uma grava o que conseguiu e por que parou, em base/incentivos/rouanet_status.json):
    A. incentivadores com o link de doações (o SALIC identifica o incentivador por um código próprio)
    B. doações de cada empresa, das maiores doadoras para as menores, até o orçamento de tempo da execução;
       a próxima execução continua de onde parou (base/incentivos/rouanet_feitas.json)
    C. estado de destino: o estado do PROJETO que recebeu a doação (consulta por PRONAC, com cache)
    D. publica o índice e o histórico por empresa para o painel (docs/dados/doadoras/)

    python3 scripts/coleta_rouanet.py [minutos]
"""
from __future__ import annotations

import gzip
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "biblioteca_alexandria/base/incentivos"
PUB = RAIZ / "docs/dados/doadoras"
SALIC = "https://api.salic.cultura.gov.br/api/v1"
UA = {"User-Agent": "Eldorado/1.0 (dados publicos; associacao sem fins lucrativos)", "Accept": "application/json"}
ANO_MIN = date.today().year - 4


def get(url: str, tempo: float = 30):
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=tempo) as r:
                return r.status, json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(5 * (tentativa + 1)); continue
            return e.code, None
        except Exception as e:
            if tentativa == 2:
                return -1, str(e)[:100]
            time.sleep(2)
    return -1, None


def ler_json(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao
    except Exception:
        return padrao


def lote(d: dict) -> list:
    emb = (d or {}).get("_embedded") or {}
    return next((v for v in emb.values() if isinstance(v, list)), []) if emb else ((d or {}).get("items") or [])


def etapa_a(status: dict) -> list[dict]:
    """Incentivadores PJ com o link de doações, guardados crus."""
    arq = BASE / "rouanet_incentivadores_raw.jsonl.gz"
    if arq.exists():
        return [json.loads(l) for l in gzip.open(arq, "rt", encoding="utf-8")]
    todos, off = [], 0
    while True:
        cod, d = get(f"{SALIC}/incentivadores?{urllib.parse.urlencode({'tipo_pessoa': 'juridica', 'limit': 100, 'offset': off, 'format': 'json'})}")
        if cod != 200:
            status["a"] = {"parou_em_offset": off, "http": cod}; break
        l = lote(d)
        if not l:
            break
        todos += l; off += 100
        if len(l) < 100:
            break
        time.sleep(0.2)
    with gzip.open(arq, "wt", encoding="utf-8") as f:
        for x in todos:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    status["a"] = {"incentivadores": len(todos), "com_link_de_doacoes": sum(1 for x in todos if (x.get("_links") or {}).get("doacoes"))}
    return todos


def _link_doacoes(x: dict) -> str | None:
    h = ((x.get("_links") or {}).get("doacoes") or {}).get("href")
    if h:
        return h.replace("http://", "https://")
    i = x.get("incentivador_id") or x.get("id")
    return f"{SALIC}/incentivadores/{i}/doacoes" if i else None


def etapa_b(incs: list[dict], minutos: float, status: dict) -> None:
    feitas = set(ler_json(BASE / "rouanet_feitas.json", []))
    parte = BASE / "rouanet_doacoes" / f"parte-{time.strftime('%Y%m%d-%H%M')}.jsonl.gz"
    parte.parent.mkdir(parents=True, exist_ok=True)
    fim = time.time() + minutos * 60
    fila = sorted(incs, key=lambda x: -float(x.get("total_doado") or 0))
    n = novas = 0
    with gzip.open(parte, "wt", encoding="utf-8") as f:
        for x in fila:
            if time.time() > fim:
                break
            cn = str(x.get("cgccpf") or "")
            if not cn or cn in feitas:
                continue
            link = _link_doacoes(x)
            if not link:
                feitas.add(cn); continue
            off = 0
            while True:
                cod, d = get(f"{link}{'&' if '?' in link else '?'}{urllib.parse.urlencode({'limit': 100, 'offset': off, 'format': 'json'})}")
                l = lote(d) if cod == 200 else []
                for dd in l:
                    f.write(json.dumps({"cnpj": cn, "empresa": x.get("nome"), **{k: dd.get(k) for k in
                            ("PRONAC", "nome_projeto", "valor", "data_recibo", "UF", "municipio", "area", "segmento") if k in dd}}, ensure_ascii=False) + "\n")
                    novas += 1
                if len(l) < 100:
                    break
                off += 100
            feitas.add(cn); n += 1
            time.sleep(0.15)
    (BASE / "rouanet_feitas.json").write_text(json.dumps(sorted(feitas)), encoding="utf-8")
    status["b"] = {"empresas_nesta_execucao": n, "doacoes_nesta_execucao": novas, "empresas_concluidas": len(feitas),
                   "de": len(incs), "completo": len(feitas) >= len(incs)}


def doacoes() -> list[dict]:
    out = []
    for p in sorted((BASE / "rouanet_doacoes").glob("*.jsonl.gz")):
        out += [json.loads(l) for l in gzip.open(p, "rt", encoding="utf-8")]
    return out


def etapa_c(ds: list[dict], minutos: float, status: dict) -> dict:
    """Estado de destino: o estado do projeto. Cache por PRONAC; o que faltar, consulta."""
    cache = ler_json(BASE / "rouanet_pronac_uf.json", {})
    fim = time.time() + minutos * 60
    faltam = {str(d["PRONAC"]) for d in ds if d.get("PRONAC") and not d.get("UF")} - set(cache)
    for pr in sorted(faltam):
        if time.time() > fim:
            break
        cod, d = get(f"{SALIC}/projetos/{pr}?format=json")
        if cod == 200 and isinstance(d, dict):
            cache[pr] = {"uf": d.get("UF"), "municipio": d.get("municipio"), "area": d.get("area"), "nome": d.get("nome")}
        else:
            cache[pr] = {"uf": None}
        time.sleep(0.1)
    (BASE / "rouanet_pronac_uf.json").write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    status["c"] = {"pronacs_conhecidos": len(cache), "faltam": len(faltam - set(cache))}
    return cache


def etapa_d(incs: list[dict], ds: list[dict], cache: dict, status: dict) -> None:
    """Índice de todas as empresas + histórico por empresa, em fatias pelo começo do CNPJ."""
    resumo = {}
    base = BASE / "rouanet_incentivadores.jsonl.gz"
    if base.exists():
        for l in gzip.open(base, "rt", encoding="utf-8"):
            x = json.loads(l); resumo[str(x.get("cnpj") or "")] = x
    for x in incs:
        cn = str(x.get("cgccpf") or "")
        resumo.setdefault(cn, {"nome": x.get("nome"), "cnpj": cn, "uf": x.get("UF"), "municipio": x.get("municipio"),
                               "total_doado": x.get("total_doado")})
    hist = defaultdict(lambda: {"por_ano": defaultdict(float), "por_uf_destino": defaultdict(float), "projetos": []})
    for d in ds:
        cn = d["cnpj"]; v = float(d.get("valor") or 0); ano = str(d.get("data_recibo") or "")[:4]
        uf = d.get("UF") or (cache.get(str(d.get("PRONAC"))) or {}).get("uf")
        h = hist[cn]
        if ano.isdigit():
            h["por_ano"][ano] += v
        if uf:
            h["por_uf_destino"][uf] += v
        if len(h["projetos"]) < 60:
            h["projetos"].append({"pronac": d.get("PRONAC"), "projeto": (d.get("nome_projeto") or (cache.get(str(d.get("PRONAC"))) or {}).get("nome") or "")[:90],
                                  "valor": round(v, 2), "data": str(d.get("data_recibo") or "")[:10], "uf": uf})
    PUB.mkdir(parents=True, exist_ok=True)
    indice = []
    fatias = defaultdict(dict)
    for cn, r in resumo.items():
        if not cn:
            continue
        h = hist.get(cn)
        ufs = dict(sorted((h["por_uf_destino"] if h else {}).items(), key=lambda kv: -kv[1]))
        indice.append({"n": r.get("nome"), "c": cn, "u": r.get("uf"), "m": r.get("municipio"), "t": round(float(r.get("total_doado") or 0), 2),
                       "l": ["Rouanet"], "d": {k: round(v) for k, v in ufs.items()},
                       "a": sorted((h["por_ano"] if h else {}).keys())})
        if h:
            fatias[cn[:2]][cn] = {"por_ano": {k: round(v, 2) for k, v in sorted(h["por_ano"].items())},
                                   "por_uf_destino": {k: round(v, 2) for k, v in ufs.items()},
                                   "projetos": sorted(h["projetos"], key=lambda p: p["data"], reverse=True)}
    indice.sort(key=lambda x: -x["t"])
    (PUB / "indice.json").write_text(json.dumps({"em": time.strftime("%Y-%m-%d"), "leis": ["Rouanet"], "total": len(indice),
                                                  "empresas": indice}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (PUB / "h").mkdir(exist_ok=True)
    for k, v in fatias.items():
        (PUB / "h" / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    status["d"] = {"empresas_no_indice": len(indice), "com_historico": sum(len(v) for v in fatias.values()), "fatias": len(fatias)}


def main(minutos: float = 95) -> dict:
    BASE.mkdir(parents=True, exist_ok=True)
    status = ler_json(BASE / "rouanet_status.json", {})
    status["em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    incs = etapa_a(status)
    if incs:
        etapa_b(incs, minutos * 0.8, status)
    ds = doacoes()
    cache = etapa_c(ds, minutos * 0.15, status) if ds else {}
    etapa_d(incs, ds, cache, status)
    (BASE / "rouanet_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))
    return status


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 95)
