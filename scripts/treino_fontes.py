#!/usr/bin/env python3
"""TREINO PRÁTICO DOS MOTORES — fonte oficial e PDF do edital (titular, 14/10/2026).

Casos conhecidos: oportunidades que chegaram por um REPLICADOR e cujo site oficial já foi confirmado. Para cada caso,
parte da página do replicador e tenta chegar à fonte já conhecida e ao PDF do edital:
  1ª passada (sem aprendizado) → mede a assertividade
  aprendizado: em cada replicador, o texto do link que leva à fonte; em cada site oficial, o trecho do caminho onde
               ficam os PDFs (estado/aprendizado_fontes.json, acumulado entre treinos)
  2ª passada (com aprendizado) → mede de novo
  aplicação: oportunidades abertas com "site oficial" vazio ou de replicador → resolvidas (estado/fontes_resolvidas.json)
Precisa de internet (roda no GitHub, fluxo 38). Resultado: estado/treino_fontes.json.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src import fonte_oficial as F  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "text/html,application/json,application/pdf;q=0.9,*/*;q=0.5", "Accept-Language": "pt-BR,pt;q=0.9"}
_cache: dict = {}


def getter(url: str) -> str:
    if url in _cache:
        if isinstance(_cache[url], Exception):
            raise _cache[url]
        return _cache[url]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            tipo = r.headers.get("Content-Type", "")
            corpo = r.read(3_000_000)
        txt = "" if "pdf" in tipo else corpo.decode("utf-8", "replace")
        _cache[url] = txt
        return txt
    except Exception as e:  # noqa: BLE001
        _cache[url] = e
        raise


def mesmo_site(a: str | None, b: str | None) -> bool:
    da, db = F._dom(a or ""), F._dom(b or "")
    return bool(da and db) and (da == db or da.endswith("." + db) or db.endswith("." + da))


def casos() -> list[dict]:
    R = json.loads((RAIZ / "dados/oportunidades/repositorio_unico.json").read_text(encoding="utf-8"))["registros"]
    return [r for r in R if r.get("url") and F.eh_replicador(r["url"]) and r.get("link_oficial") and F.eh_fonte(r["link_oficial"])]


def passada(C: list[dict], A: dict) -> dict:
    res = []
    for r in C:
        o = F.resolver(r["url"], r.get("titulo") or "", r.get("orgao") or "", getter, A)
        res.append({"id": r["id"], "replicador": F._dom(r["url"]), "esperado": r["link_oficial"], "fonte": o["fonte"],
                    "acertou_fonte": mesmo_site(o["fonte"], r["link_oficial"]), "pdfs": len(o["pdfs"]), "passos": o["passos"]})
    n = len(res) or 1
    return {"casos": len(res), "fonte_pct": round(100 * sum(x["acertou_fonte"] for x in res) / n),
            "pdf_pct": round(100 * sum(1 for x in res if x["acertou_fonte"] and x["pdfs"]) / n),
            "por_replicador": {d: f"{sum(1 for x in res if x['replicador'] == d and x['acertou_fonte'])}/{sum(1 for x in res if x['replicador'] == d)}"
                               for d in sorted({x["replicador"] for x in res})}, "resultados": res}


def aprender(C: list[dict], A: dict) -> dict:
    novos = Counter()
    for r in C:
        dr, do = F._dom(r["url"]), F._dom(r["link_oficial"])
        try:                                           # replicador: qual texto de link levou ao site oficial conhecido
            for href, txt in F.links(getter(r["url"]), r["url"]):
                if mesmo_site(href, r["link_oficial"]) and txt:
                    anc = " ".join(F._sem(txt).split()[:3])
                    if anc and len(anc) >= 4:
                        a = A.setdefault("replicadores", {}).setdefault(dr, {}).setdefault("ancoras", {})
                        a[anc] = a.get(anc, 0) + 1; novos["ancoras"] += 1
                    break
        except Exception:  # noqa: BLE001
            pass
        try:                                           # site oficial: onde ficam os PDFs
            for href, txt in F.links(getter(r["link_oficial"]), r["link_oficial"]):
                if re.search(r"\.pdf($|\?)", href, re.I) and (F.CHAVE_PDF.search(txt) or F.CHAVE_PDF.search(href)):
                    caminho = urlsplit(href).path
                    seg = "/".join(caminho.split("/")[:3]) + "/" if caminho.count("/") >= 2 else caminho
                    p = A.setdefault("oficiais", {}).setdefault(do, {}).setdefault("pdf_padroes", {})
                    p[seg.lower()] = p.get(seg.lower(), 0) + 1; novos["pdf_padroes"] += 1
                    break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.3)
    return dict(novos)


def aplicar(A: dict, limite: int = 120, so_novas: bool = False) -> dict:
    R = json.loads((RAIZ / "dados/oportunidades/repositorio_unico.json").read_text(encoding="utf-8"))["registros"]
    alvo = [r for r in R if r.get("estado") != "fechada" and not r.get("arquivada") and r.get("url") and F.eh_replicador(r["url"])
            and (not r.get("link_oficial") or F.eh_replicador(r["link_oficial"]))]
    try:
        ja = json.loads((RAIZ / "estado/fontes_resolvidas.json").read_text(encoding="utf-8")).get("resolvidas") or {}
    except Exception:  # noqa: BLE001
        ja = {}
    if so_novas:                                      # na coleta: só o que ainda não foi resolvido, do mais novo ao mais velho
        alvo = sorted((r for r in alvo if r["id"] not in ja), key=lambda r: str(r.get("descoberto_em") or r.get("publicado_em") or ""), reverse=True)
    out = {}
    for r in alvo[:limite]:
        o = F.resolver(r["url"], r.get("titulo") or "", r.get("orgao") or "", getter, A)
        if o["fonte"]:
            out[r["id"]] = {"fonte": o["fonte"], "pdfs": [p["url"] for p in o["pdfs"]], "passos": o["passos"],
                            "em": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    ant = {}
    try:
        ant = json.loads((RAIZ / "estado/fontes_resolvidas.json").read_text(encoding="utf-8")).get("resolvidas") or {}
    except Exception:  # noqa: BLE001
        pass
    ant.update(out)
    (RAIZ / "estado/fontes_resolvidas.json").write_text(json.dumps({"regra": F.__doc__.strip().splitlines()[0], "resolvidas": ant},
                                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return {"tentadas": len(alvo[:limite]), "resolvidas_agora": len(out), "resolvidas_total": len(ant)}


def main() -> dict:
    C = casos()
    antes = passada(C, {"replicadores": {}, "oficiais": {}})
    A = F._aprendizado(); novos = aprender(C, A)
    F.APRENDIZADO.write_text(json.dumps(A, ensure_ascii=False, indent=1), encoding="utf-8")
    depois = passada(C, A)
    ap = aplicar(A)
    sai = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "casos_conhecidos": len(C),
           "antes": {k: v for k, v in antes.items() if k != "resultados"}, "aprendido": novos,
           "depois": {k: v for k, v in depois.items() if k != "resultados"}, "aplicacao": ap,
           "erros_depois": [x for x in depois["resultados"] if not x["acertou_fonte"]][:30]}
    (RAIZ / "estado/treino_fontes.json").write_text(json.dumps(sai, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: sai[k] for k in ("casos_conhecidos", "antes", "aprendido", "depois", "aplicacao")}


if __name__ == "__main__":
    if "--aplicar" in sys.argv:                       # 14/10: na coleta (fluxos 22 e 16) — só resolve, com o aprendizado
        print(json.dumps(aplicar(F._aprendizado(), limite=40, so_novas=True), ensure_ascii=False))
    else:
        print(json.dumps(main(), ensure_ascii=False, indent=1))
