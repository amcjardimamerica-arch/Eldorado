"""REGRA DE ABRANGÊNCIA (titular, 14/10/2026) — um só lugar, usado pelo repositório, pela curadoria dos livros e pelos
MOTORES DE BUSCA (que descartam na coleta, antes de a oportunidade entrar no sistema).

  · Goiás: oportunidades e livros MUNICIPAIS permitidos (os 246 municípios).
  · Outros estados: só ESTADUAIS — e as MUNICIPAIS DAS CAPITAIS (exceção da titular, 14/10).
  · Nacionais e internacionais: permitidas.
  · Municipal de outro estado que não seja capital: DESCARTADA pelo motor que a encontrou.
  · Sem estado determinado com segurança: fica (há municípios homônimos).
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sem(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "").lower()) if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _capitais() -> dict:
    T = json.loads((ROOT / "config/territorio_goias.json").read_text(encoding="utf-8"))
    return {_sem(v["capital"]): uf for uf, v in (T.get("outros_estados") or {}).items() if v.get("capital")}


def capital_citada(texto: str) -> str | None:
    """UF da capital de outro estado citada como município ('prefeitura/município/câmara/diário oficial de X' ou
    'X/UF', 'X (UF)', 'X - UF'); None se não houver."""
    t = _sem(texto)
    for cap, uf in _capitais().items():
        c = re.escape(cap)
        if re.search(rf"\b(?:prefeitura|municipio|camara|diario oficial|secretaria municipal [a-z ]{{0,40}})(?: municipal)? (?:de |do |da )?{c}\b", t) \
                or re.search(rf"\b{c}\s*(?:[-/(]\s*){uf.lower()}\b", t):
            return uf
    return None


def descartar_na_coleta(item: dict, uf_agregador: str | None = None) -> str | None:
    """Motivo do descarte, se a oportunidade for municipal de outro estado (fora das capitais); None se fica."""
    from .repositorio_unico import municipal_fora_de_goias
    m = municipal_fora_de_goias(item, uf_agregador)
    if not m:
        return None
    uf = (re.search(r"\(([A-Z]{2})\)", m) or [None, "?"])[1]
    return f"municipal de outro estado ({uf}) que não é capital — só Goiás tem municipais (e as capitais)"


REGISTRO = ROOT / "estado/descartes_abrangencia.json"


def registrar_descarte(motor: str, item: dict, motivo: str) -> None:
    """Conta o descarte por motor e guarda os 30 últimos exemplos (estado/descartes_abrangencia.json)."""
    from datetime import datetime, timezone
    try:
        d = json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {}
    except Exception:  # noqa: BLE001
        d = {}
    m = d.setdefault("por_motor", {}).setdefault(str(motor or "?"), {"total": 0})
    m["total"] += 1; m["ultimo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ex = d.setdefault("exemplos", [])
    ex.append({"motor": motor, "titulo": str(item.get("titulo") or "")[:140], "url": item.get("url") or item.get("link_oficial"), "motivo": motivo, "em": m["ultimo"]})
    d["exemplos"] = ex[-30:]; d["total"] = sum(v["total"] for v in d["por_motor"].values())
    d["regra"] = __doc__.strip().splitlines()[0]
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def filtro(motor: str, item: dict, uf_agregador: str | None = None) -> bool:
    """True se o motor deve DESCARTAR o achado (e registra o descarte)."""
    try:
        m = descartar_na_coleta(item, uf_agregador)
    except Exception:  # noqa: BLE001
        return False
    if m:
        registrar_descarte(motor, item, m)
    return bool(m)
