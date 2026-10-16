#!/usr/bin/env python3
"""TESTE DO BANCO ÚNICO (titular, 16/10/2026): o único banco de dados do ELDORADO são os livros.

Lista tudo o que existe FORA dos livros e classifica:
  livros     catálogo (biblioteca_alexandria/fontes/motores.json) e arquivos de livro (biblioteca_alexandria/livros/)
  farol      dados do Farol e da associação — a outra metade do sistema, fora da regra
  vitrine    painéis do site (docs/dados), gerados a partir dos livros
  controle   controle operacional permitido (cursores, filas que apontam para livros, marcos, estado do comando)
  PARALELO   todo o resto: banco de dados paralelo que ainda precisa ir para os livros
Saída: docs/dados/banco_unico.json (o mostrador da sala de controle lê daqui). Código de saída 0 sempre (é um relatório).
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREAS = ("dados", "estado", "biblioteca_alexandria")
LIVROS = re.compile(r"^biblioteca_alexandria/(fontes/motores\.json|livros/)")
FAROL = re.compile(r"^(dados/farol|dados/associacoes|biblioteca_alexandria/associacoes)(/|$)")
CONTROLE = re.compile(r"^estado/(esquadra[^/]*\.json|achados_vistos\.json|fila_retentativa\.json|comando/|maestro[^/]*|analise_[^/]*|"
                      r"expurgo/|[a-z_]*migracao\.json|modalidade_[a-z]+\.json|rotas/|ponte/|robots[^/]*|pausa[^/]*|vigilancia_diaria\.txt|unir_livros\.txt|"
                      r"diagnostico_[^/]*|sala[^/]*|alerta[^/]*|saude[^/]*|cursores?[^/]*)")


def grupo(rel: str) -> str:
    p = rel.split("/")
    return "/".join(p[:3]) if len(p) > 3 else "/".join(p[:2])


def classe(rel: str) -> str:
    if LIVROS.search(rel):
        return "livros"
    if FAROL.search(rel):
        return "farol"
    if CONTROLE.search(rel):
        return "controle"
    return "PARALELO"


def run() -> dict:
    g = defaultdict(lambda: {"classe": None, "arquivos": 0, "mb": 0.0})
    for a in AREAS:
        for r_, _d, fs in os.walk(ROOT / a):
            for f in fs:
                p = Path(r_) / f; rel = str(p.relative_to(ROOT))
                c = classe(rel); k = grupo(rel) if c == "PARALELO" else c
                g[k]["classe"] = c; g[k]["arquivos"] += 1; g[k]["mb"] += p.stat().st_size / 1e6
    par = {k: v for k, v in g.items() if v["classe"] == "PARALELO"}
    res = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
           "regra": "o único banco de dados do Eldorado são os livros; o Farol (e a associação) fica fora",
           "por_classe": {c: {"arquivos": sum(v["arquivos"] for v in g.values() if v["classe"] == c),
                              "mb": round(sum(v["mb"] for v in g.values() if v["classe"] == c), 1)}
                          for c in ("livros", "farol", "controle", "PARALELO")},
           "bancos_paralelos": len(par),
           "paralelos": sorted(({"grupo": k, "arquivos": v["arquivos"], "mb": round(v["mb"], 2)} for k, v in par.items()),
                               key=lambda x: -x["mb"])}
    out = ROOT / "docs/dados/banco_unico.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k != "paralelos"}, ensure_ascii=False, indent=1))
    for x in r["paralelos"][:int(sys.argv[1]) if len(sys.argv) > 1 else 25]:
        print(f"  {x['mb']:8.2f} MB {x['arquivos']:6} arq  {x['grupo']}")
