"""SKILL · CADASTRO (titular, 29/09) — o que o sistema JÁ conhece. O Espião procura entidades NOVAS: empresa, instituto
ou fundação que já está nos rankings, nos incentivadores do SALIC (23 mil) ou nas fichas de empresas não é descoberta."""
from __future__ import annotations

import gzip
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUFIXOS = r"\b(s\.?\s?a\.?|ltda\.?|me|epp|eireli|cia\.?|companhia|holding|participacoes|do brasil|brasil)\b"


def norm(nome: str) -> str:
    t = unicodedata.normalize("NFKD", str(nome or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(SUFIXOS, " ", t)
    return re.sub(r"[^a-z0-9]+", "", t)[:40]


@lru_cache(maxsize=1)
def _conhecidos() -> tuple[frozenset, frozenset]:
    nomes, cnpjs = set(), set()
    for f in ("biblioteca_alexandria/empresas/ranking_destinacao_tributaria.json", "biblioteca_alexandria/empresas/ranking_patrocinio_privado.json",
              "docs/dados/ranking_apoiadores.json"):
        try:
            for e in json.loads((ROOT / f).read_text(encoding="utf-8")).get("empresas", []):
                nomes.add(norm(e.get("nome") or e.get("razao_social"))); cnpjs.add(re.sub(r"\D", "", str(e.get("cnpj") or ""))[:8])
        except Exception:
            pass
    try:
        with gzip.open(ROOT / "biblioteca_alexandria/base/incentivos/rouanet_incentivadores.jsonl.gz", "rt", encoding="utf-8") as fh:
            for l in fh:
                r = json.loads(l); nomes.add(norm(r.get("nome"))); cnpjs.add(re.sub(r"\D", "", str(r.get("cnpj") or ""))[:8])
    except Exception:
        pass
    try:
        for k in (json.loads((ROOT / "estado/interceptador/fontes_empresas.json").read_text(encoding="utf-8")).get("fichas") or {}):
            nomes.add(norm(k))
    except Exception:
        pass
    nomes.discard(""); cnpjs.discard("")
    return frozenset(nomes), frozenset(cnpjs)


def conhecida(nome: str = "", cnpj: str = "") -> bool:
    nomes, cnpjs = _conhecidos()
    c = re.sub(r"\D", "", str(cnpj or ""))[:8]
    return bool((c and c in cnpjs) or (norm(nome) and norm(nome) in nomes))


def total() -> int:
    return len(_conhecidos()[0])
