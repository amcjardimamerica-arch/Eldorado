"""CATÁLOGO ÚNICO DE EMPRESAS POR INCENTIVO (titular, 29/09).

Uma empresa aparece UMA vez — identificada pela RAIZ do CNPJ (8 dígitos: matriz e filiais juntas) — com os incentivos
de que participou agrupados dentro dela, cada um com a fonte oficial:
  Rouanet   SALIC/MinC — 23.498 incentivadores (valor doado) + lotes detalhados de 26/09 (doações por projeto)
  Goyazes   Secult-GO — créditos concedidos 2024 e 2025 (projeto, valor, cidade). As planilhas não trazem CNPJ: a
            empresa é casada pelo NOME com o PAT e o SALIC (Goiás primeiro); sem casamento seguro, fica pelo nome.
  PAT       MTE — relação de beneficiárias até 31/03/2026 (estabelecimentos ativos e inativos, trabalhadores).
            Inscrição no PAT NÃO prova Lucro Real.
Fontes brutas: biblioteca_alexandria/base/incentivos/ · saída: biblioteca_alexandria/empresas/catalogo_incentivos.jsonl.gz
e o resumo em biblioteca_alexandria/empresas/catalogo_incentivos_resumo.json.
"""
from __future__ import annotations

import gzip
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "biblioteca_alexandria/base/incentivos"
SAIDA = ROOT / "biblioteca_alexandria/empresas/catalogo_incentivos.jsonl.gz"
RESUMO = ROOT / "biblioteca_alexandria/empresas/catalogo_incentivos_resumo.json"
PAT_FONTE = "MTE — relação de beneficiárias do PAT até 31/03/2026"


def dig(x) -> str:
    return re.sub(r"\D", "", str(x or ""))


def norm(n: str) -> str:
    t = unicodedata.normalize("NFKD", str(n or "").upper())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\b(LTDA|S\.?/?A\.?|EIRELI|ME|EPP|CIA|COMPANHIA|IND(USTRIA)?|COM(ERCIO)?|DE|DA|DO|DOS|DAS|E|EM|MEI)\b\.?", " ", t)
    return re.sub(r"[^A-Z0-9]", "", t)[:40]


def norm_esp(n: str) -> str:
    """Como norm(), mas mantendo os espaços — para a comparação aproximada por palavras."""
    t = unicodedata.normalize("NFKD", str(n or "").upper())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\b(LTDA|LIMITADA|S\.?/?A\.?|EIRELI|EIRELL|ME|EPP|CIA|COMPANHIA|IND(USTRIA)?|COM(ERCIO|ERCIA)?|DE|DA|DO|DOS|DAS|E|EM|MEI|COORPERATIVA)\b\.?", " ", t)
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", t)).strip()


def valor_br(x) -> float | None:
    """290000 · 290000.5 · 'R$ 1.373.032,92' · '1.373.032,92' → float (formato brasileiro entendido)."""
    if isinstance(x, (int, float)):
        return float(x)
    s = re.sub(r"[^\d,.\-]", "", str(x or ""))
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


LIXO_PLANILHA = re.compile(r"(?i)^(sub)?total|^valor|^soma|utilizado$")


def _goyazes() -> dict:
    import openpyxl
    out = defaultdict(lambda: {"grafias": set(), "por_ano": defaultdict(lambda: {"projetos": 0, "valor": 0.0, "cidades": set()})})
    for f in sorted((BASE / "goyazes").glob("PLANILHA-CREDITOS-CONCEDIDOS*.xlsx")):
        ano = re.search(r"(20\d\d)", f.name).group(1)
        if "Publicar-no-SITE" in f.name:             # a mesma planilha de 2025, publicada no site: não conta duas vezes
            continue
        for r in openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True):
            if len(r) < 4 or not r[3] or not isinstance(r[3], str) or r[3].strip().upper() in ("EMPRESA", "-"):
                continue
            v = valor_br(r[2])
            if v is None:
                continue
            if LIXO_PLANILHA.search(r[3].strip()):
                continue                                  # linha de total da planilha não é empresa
            k = norm(r[3])
            if not k:
                continue
            e = out[k]; e["grafias"].add(r[3].strip()); p = e["por_ano"][ano]; p["projetos"] += 1; p["valor"] += v
            if len(r) > 4 and r[4]:
                p["cidades"].add(str(r[4]).strip()[:60])
    return out


def construir() -> dict:
    cat: dict[str, dict] = {}
    por_nome_go, por_nome = {}, {}

    def pega(raiz: str, nome: str, uf: str | None = None, municipio: str | None = None, cnpj: str | None = None) -> dict:
        e = cat.get(raiz)
        if not e:
            e = cat[raiz] = {"raiz": raiz, "cnpj": cnpj, "nome": nome, "uf": uf, "municipio": municipio, "goias": uf == "GO", "incentivos": {}}
        if cnpj and (not e.get("cnpj") or cnpj.endswith("0001", 0, 12)):
            e["cnpj"] = cnpj
        if uf == "GO":
            e["goias"] = True
        return e

    # 1) PAT — estabelecimentos consolidados por raiz
    pat = defaultdict(lambda: {"ativos": 0, "inativos": 0, "trab": 0, "ufs": Counter(), "nome": None, "matriz": None, "mun": None, "uf": None})
    for arq, situ in (("pat_beneficiarias_ativas_2026-03-31.jsonl.gz", "ativos"), ("pat_beneficiarias_inativas_2026-03-31.jsonl.gz", "inativos")):
        with gzip.open(BASE / arq, "rt", encoding="utf-8") as fh:
            for l in fh:
                r = json.loads(l); c = dig(r.get("CNPJ"))
                if len(c) < 8:
                    continue
                p = pat[c[:8]]; p[situ] += 1; p["ufs"][r.get("UF")] += 1
                if situ == "ativos":
                    try:
                        p["trab"] += int(float(r.get("Total Trabalhadores") or 0))
                    except (TypeError, ValueError):
                        pass
                if not p["nome"] or str(r.get("Matriz ou Filial", "")).upper().startswith("MATRIZ"):
                    p["nome"] = r.get("Razão Social"); p["uf"] = r.get("UF"); p["mun"] = r.get("Município")
                    if len(c) == 14:
                        p["matriz"] = c
    for raiz, p in pat.items():
        e = pega(raiz, p["nome"], p["uf"], p["mun"], p["matriz"])
        e["goias"] = e["goias"] or bool(p["ufs"].get("GO"))
        e["incentivos"]["PAT"] = {"situacao": "ativa" if p["ativos"] else "inativa", "estabelecimentos_ativos": p["ativos"],
                                  "estabelecimentos_inativos": p["inativos"], "trabalhadores": p["trab"], "ufs": dict(p["ufs"].most_common(6)),
                                  "fonte": PAT_FONTE, "nota": "inscrição no PAT não prova Lucro Real"}
    # 2) ROUANET — catálogo do SALIC + lotes detalhados
    lotes = {}
    try:
        with gzip.open(BASE / "rouanet_lotes_2026-09-26.json.gz", "rt", encoding="utf-8") as fh:
            lotes = json.load(fh).get("cnpjs") or {}
    except Exception:
        pass
    for l in open(BASE / "empresas_incentivadoras.jsonl", encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l); c = dig(r.get("cnpj"))
        if len(c) != 14:                                  # pessoa física não entra no catálogo de empresas
            continue
        e = pega(c[:8], r.get("nome"), r.get("uf"), r.get("municipio"), c)
        inc = e["incentivos"].setdefault("Rouanet", {"total_doado": 0.0, "fonte": "SALIC/MinC"})
        inc["total_doado"] = round(inc["total_doado"] + float(r.get("total_doado") or 0), 2)
        det = lotes.get(c) or {}
        if det.get("doacoes"):
            inc["doacoes"] = det["doacoes"][:30]
    # 3) GOYAZES — casamento pelo nome (Goiás primeiro)
    for e in cat.values():
        k = norm(e.get("nome"))
        if k:
            (por_nome_go if e.get("goias") else por_nome).setdefault(k, e["raiz"])
    try:
        from rapidfuzz import process, fuzz
    except Exception:
        process = None
    nomes_go = {norm_esp(e.get("nome")): e["raiz"] for e in cat.values() if e.get("goias") and e.get("nome")}
    lista_go = list(nomes_go)
    # grafias da MESMA empresa na planilha ("COMPLEM - COOPERATIVA…", "COMPLEM COOPERATIVA…") viram uma só
    gz = _goyazes(); grupos = []
    for k, g in gz.items():
        ne = norm_esp(sorted(g["grafias"])[0])
        alvo = None
        if process:
            for gr in grupos:
                if ne.split(" ")[0] == gr["ne"].split(" ")[0] and (fuzz.token_sort_ratio(ne, gr["ne"]) >= 85 or fuzz.partial_ratio(ne, gr["ne"]) >= 95
                                                                     or fuzz.token_set_ratio(ne, gr["ne"]) >= 92):
                    alvo = gr; break
        if not alvo:
            alvo = {"ne": ne, "chaves": [], "grafias": set(), "por_ano": defaultdict(lambda: {"projetos": 0, "valor": 0.0, "cidades": set()})}
            grupos.append(alvo)
        alvo["chaves"].append(k); alvo["grafias"] |= g["grafias"]
        for a, p in g["por_ano"].items():
            q = alvo["por_ano"][a]; q["projetos"] += p["projetos"]; q["valor"] += p["valor"]; q["cidades"] |= p["cidades"]
    g_st = Counter()
    for g in grupos:
        raiz, modo = None, None
        for k in g["chaves"]:
            raiz = por_nome_go.get(k) or por_nome.get(k)
            if raiz:
                modo = "nome exato"; break
        if not raiz and process and lista_go:
            prim = g["ne"].split(" ")[0]
            # mesma primeira palavra (tolerando plural e erro de digitação: LATICÍNIO × LATICÍNIOS)
            cands = [c for c in lista_go if c.split(" ")[0][:1] == prim[:1] and fuzz.ratio(c.split(" ")[0], prim) >= 85]
            m = process.extractOne(g["ne"], cands, scorer=fuzz.token_sort_ratio, score_cutoff=90) if cands else None
            if m:
                raiz = nomes_go[m[0]]; modo = f"nome muito parecido ({int(m[1])}%)"
            else:
                ini = [c for c in cands if min(len(c), len(g["ne"])) >= 8 and (c.startswith(g["ne"]) or g["ne"].startswith(c))]
                if len(ini) == 1:                       # um só candidato começando igual: casamento seguro
                    raiz = nomes_go[ini[0]]; modo = "início igual, nome contido"
                elif not ini and cands and len(g["ne"]) >= 12:
                    m = process.extractOne(g["ne"], cands, scorer=fuzz.partial_ratio, score_cutoff=95)
                    if m and len(m[0]) >= 12:
                        raiz = nomes_go[m[0]]; modo = f"início igual, nome contido ({int(m[1])}%)"
        if not raiz:
            raiz = "nome:" + g["chaves"][0]; modo = "sem CNPJ (planilha só traz o nome)"
            pega(raiz, sorted(g["grafias"])[0], "GO")
        e = cat[raiz]; e["goias"] = True
        ant = e["incentivos"].get("Goyazes")
        if ant:                                          # outra grafia da MESMA empresa: SOMA, nunca sobrescreve
            for a, p in g["por_ano"].items():
                q = ant["por_ano"].setdefault(a, {"projetos": 0, "valor": 0.0, "cidades": []})
                q["projetos"] += p["projetos"]; q["valor"] = round(q["valor"] + p["valor"], 2)
                q["cidades"] = sorted(set(q["cidades"]) | p["cidades"])[:12]
            ant["grafias"] = sorted(set(ant["grafias"]) | g["grafias"])
            continue
        e["incentivos"]["Goyazes"] = {"por_ano": {a: {"projetos": p["projetos"], "valor": round(p["valor"], 2), "cidades": sorted(p["cidades"])[:12]}
                                                  for a, p in sorted(g["por_ano"].items())},
                                      "grafias": sorted(g["grafias"]), "casamento": modo, "fonte": "Secult-GO — créditos concedidos (Programa Goyazes)"}
        g_st[modo.split(" (")[0]] += 1
    # saída
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(SAIDA, "wt", encoding="utf-8") as fh:
        for e in sorted(cat.values(), key=lambda x: (not x.get("goias"), -len(x["incentivos"]), str(x.get("nome")))):
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    combo = Counter("+".join(sorted(e["incentivos"])) for e in cat.values())
    res = {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Fontes brutas")[0].strip(),
           "empresas": len(cat), "de_goias": sum(1 for e in cat.values() if e.get("goias")),
           "por_incentivo": {m: sum(1 for e in cat.values() if m in e["incentivos"]) for m in ("Rouanet", "Goyazes", "PAT")},
           "combinacoes": dict(combo.most_common()), "goyazes_casamento": dict(g_st),
           "goias_por_incentivo": {m: sum(1 for e in cat.values() if e.get("goias") and m in e["incentivos"]) for m in ("Rouanet", "Goyazes", "PAT")}}
    RESUMO.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    print(json.dumps(construir(), ensure_ascii=False, indent=1))
