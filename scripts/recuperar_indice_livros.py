#!/usr/bin/env python3
"""Recuperação do índice dos livros (17/10/2026) — uso único, registrado para auditoria.

O _origens.json caiu de 8.412 entradas (08:13) para 1 (09:11) e ficou em 263. Este script junta ao índice ATUAL as
entradas de versões anteriores do histórico do git, mas SÓ as que apontam para conteúdo que existe hoje nos livros:
    - entrada atual: fica como está (nunca é trocada);
    - entrada antiga: volta se TODOS os seus pedaços estão no livro; se só parte está, volta só a parte conferida;
    - pedaço que mudou de livro numa junção (o índice perdido não recebeu a troca): aponta para o livro onde ele está
      HOJE, desde que exista em UM único livro;
    - entrada antiga sem nenhum conteúdo nos livros: não volta (apontaria para o nada).

    python scripts/recuperar_indice_livros.py <versao_antiga.json> [<outra.json> ...]   # simula e relata
    python scripts/recuperar_indice_livros.py --gravar <versao_antiga.json> ...         # grava (atômico)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src import livro_arquivo as LA  # noqa: E402


def onde_esta() -> dict:
    """(arquivo antigo, pedaço) -> livros que guardam esse pedaço hoje."""
    m: dict = {}
    for f in LA.PASTA.glob("*.json"):
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for rel, ent in (d.get("acervo") or {}).items():
            for ci in ent:
                m.setdefault((rel, ci), set()).add(f.stem)
    return m


def recuperar(atual: dict, antigas: list[dict], mapa: dict | None = None) -> tuple[dict, dict]:
    cache: dict = {}
    mapa = mapa or {}
    movidos = 0

    def achar(lid, ci, rel):
        """O livro que guarda o pedaço: o original, ou o único livro para onde ele foi numa junção."""
        nonlocal movidos
        if tem(lid, ci, rel):
            return lid
        outros = mapa.get((rel, ci)) or set()
        if len(outros) == 1:
            movidos += 1
            return next(iter(outros))
        return None

    def tem(lid, ci, rel) -> bool:
        if lid not in cache:
            f = LA.PASTA / f"{lid}.json"
            try:
                cache[lid] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
            except ValueError:
                cache[lid] = None
        d = cache[lid]
        return bool(d) and ((d.get("acervo") or {}).get(rel) or {}).get(ci) is not None

    novo = dict(atual)
    rel_ = {"atuais": len(atual), "inteiras": 0, "parciais": 0, "sem_conteudo": 0, "controle": 0}
    vistos = set(atual)
    for antiga in antigas:
        for rel, o in antiga.items():
            if rel in vistos:
                continue
            vistos.add(rel)
            o = json.loads(json.dumps(o))
            if o.get("inteiro"):
                lid = achar(o["inteiro"][0], o["inteiro"][1], rel)
                if lid:
                    o["inteiro"][0] = lid
                    novo[rel] = o; rel_["inteiras"] += 1
                else:
                    rel_["sem_conteudo"] += 1
                continue
            conts = o.get("conteineres") or {}
            if not conts:
                if "controle" in o:
                    novo[rel] = o; rel_["controle"] += 1
                else:
                    rel_["sem_conteudo"] += 1
                continue
            total = sum(len(c.get("entradas") or []) for c in conts.values())
            for c in conts.values():
                ents = []
                for e in c.get("entradas") or []:
                    lid = achar(e[0], e[1], rel)
                    if lid:
                        ents.append([lid, *e[1:]])
                c["entradas"] = ents
            ficou = sum(len(c["entradas"]) for c in conts.values())
            if ficou == 0:
                rel_["sem_conteudo"] += 1
                continue
            novo[rel] = o
            rel_["inteiras" if ficou == total else "parciais"] += 1
    rel_["pedacos_remarcados_para_o_livro_atual"] = movidos
    rel_["final"] = len(novo)
    return novo, rel_


def main(argv: list[str]) -> int:
    gravar = "--gravar" in argv
    antigas = [json.loads(Path(a).read_text(encoding="utf-8")) for a in argv if a != "--gravar"]
    atual = LA.ler_origens_para_gravar()
    novo, r = recuperar(atual, antigas, onde_esta())
    print(json.dumps(r, ensure_ascii=False))
    if gravar:
        LA.gravar_origens(novo)
        print("gravado:", LA.ORIGENS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
