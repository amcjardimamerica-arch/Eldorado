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
LIVROS = re.compile(r"^biblioteca_alexandria/(fontes/|livros/|indice\.json$)")   # 16/10: a área do CATÁLOGO (catálogo, índices, ficha de cada livro) é dos livros
FAROL = re.compile(r"^(dados/farol|dados/associacoes|biblioteca_alexandria/associacoes)(/|$)")
CONTROLE = re.compile(r"^estado/(esquadra[^/]*\.json|achados_vistos\.json|fila_retentativa\.json|comando/|maestro[^/]*|analise_[^/]*|"
                      r"expurgo/|[a-z_]*migracao\.json|modalidade_[a-z]+\.json|rotas/|ponte/|robots[^/]*|pausa[^/]*|vigilancia_diaria\.txt|unir_livros\.txt|"
                      r"diagnostico_[^/]*|sala[^/]*|alerta[^/]*|saude[^/]*|cursores?[^/]*)")


def grupo(rel: str) -> str:
    p = rel.split("/")
    return "/".join(p[:3]) if len(p) > 3 else "/".join(p[:2])


# 16/10/2026 (titular): estado/ guarda os REGISTROS OPERACIONAIS das ferramentas (execução, cursores, logs, estado dos
# motores) = controle. Exceção: os arquivos que guardam DADO DE OPORTUNIDADE continuam contados até irem aos livros.
OPORTUNIDADE_EM_ESTADO = re.compile(r"^estado/(fila_verificacao\.json|curadoria_links\.json|abertos_sem_informacao\.json|"
                                    r"resultados_editais\.jsonl|catalogo_achados_ia\.json|previsoes\.json|prazos_ia\.json|"
                                    r"cartorio/(resultados_livros|biblioteca_sites|gabaritos))")   # 16/10: a fila p/ o Interceptador e o log são controle


def classe(rel: str) -> str:
    if rel.startswith("estado/") and not OPORTUNIDADE_EM_ESTADO.search(rel):
        return "controle"
    if LIVROS.search(rel):
        return "livros"
    if FAROL.search(rel):
        return "farol"
    if CONTROLE.search(rel):
        return "controle"
    return "PARALELO"


CHAVES = {"oportunidade": ({"titulo"}, {"url", "link_oficial", "fim", "prazo", "edital_id", "pagina_oficial"}),
          "empresa": (set(), {"cnpj", "cnpj_raiz", "razao_social", "empresa"}),
          "livro": ({"programa", "orgao"}, set())}


def _colecao(d):
    """A maior coleção de registros (dicionários) do arquivo."""
    melhor = []
    def ver(o, prof=0):
        nonlocal melhor
        if prof > 3:
            return
        if isinstance(o, list):
            regs = [x for x in o if isinstance(x, dict)]
            if len(regs) > len(melhor):
                melhor = regs
            for x in o[:3]:
                ver(x, prof + 1)
        elif isinstance(o, dict):
            regs = [x for x in o.values() if isinstance(x, dict)]
            if len(regs) > len(melhor) and len(regs) >= 10:
                melhor = regs
            for v in o.values():
                if isinstance(v, (list, dict)):
                    ver(v, prof + 1)
    ver(d)
    return melhor


def _natureza_de(regs):
    amostra = regs[:40]
    for nome, (todas, alguma) in CHAVES.items():
        ok = sum(1 for x in amostra if todas <= set(x) and (not alguma or alguma & set(x)))
        if amostra and ok >= 0.6 * len(amostra):
            return nome
    return None


def natureza(minimo: int = 50) -> dict:
    """Arquivo FORA da área dos livros com >= 50 registros de oportunidade, empresa ou livro, não declarado como vista em
    config/vistas_permitidas.json, é BANCO PARALELO — esteja na pasta que estiver. Dentro da área dos livros, o arquivo
    que guarda registros de muitas oportunidades juntas é COLETIVO (a distribuir em cada livro)."""
    vistas = (json.loads((ROOT / "config/vistas_permitidas.json").read_text(encoding="utf-8")).get("vistas") or {}) \
        if (ROOT / "config/vistas_permitidas.json").exists() else {}
    alvos = [p for a in (*AREAS, "docs/dados", "config") for p in (ROOT / a).rglob("*.json*")] + list((ROOT / "docs").glob("*.json"))
    par, vis, col = [], [], []
    for p in alvos:
        rel = str(p.relative_to(ROOT))
        if p.stat().st_size > 60_000_000 or p.suffix not in (".json", ".jsonl"):
            continue
        if LIVROS.search(rel) and not rel.startswith("biblioteca_alexandria/livros/_acervo/"):
            continue                                       # o livro, o catálogo e as vistas dos livros
        try:
            if p.suffix == ".jsonl":
                d = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()[:5000] if l.strip()]
            else:
                d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        regs = _colecao(d)
        nat = _natureza_de(regs) if len(regs) >= minimo else None
        if not nat:
            continue
        reg = {"arquivo": rel, "natureza": nat, "registros": len(regs), "mb": round(p.stat().st_size / 1e6, 2)}
        (vis if rel in vistas else col if rel.startswith("biblioteca_alexandria/livros/") else par).append(reg)
    ordem = lambda x: -x["registros"]  # noqa: E731
    return {"paralelos_por_natureza": sorted(par, key=ordem), "vistas_declaradas": sorted(vis, key=ordem),
            "coletivos_nos_livros": sorted(col, key=ordem),
            "bancos_paralelos_por_natureza": len(par)}


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
    res.update(natureza())                                    # 17/10: pela NATUREZA do dado, não só pela pasta
    out = ROOT / "docs/dados/banco_unico.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k != "paralelos"}, ensure_ascii=False, indent=1))
    for x in r["paralelos"][:int(sys.argv[1]) if len(sys.argv) > 1 else 25]:
        print(f"  {x['mb']:8.2f} MB {x['arquivos']:6} arq  {x['grupo']}")
