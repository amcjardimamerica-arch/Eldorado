"""O enriquecimento de cada achado (o canivete do motor padrão; plano C, as ferramentas adotadas): o que o texto e a
página dizem além do título, para o Cartório certificar e o Interceptador completar.

  idioma         lingua-py: o idioma do texto (as fontes internacionais)
  publicacao     htmldate: a data de publicação da página
  datas          dateparser e datefinder: as datas citadas no texto, com o trecho ao redor (candidatas a prazo)
  valores        price-parser: os valores em reais citados, com o trecho
  metadados      extruct: os dados estruturados embutidos (JSON-LD, microdata: eventos, organizações, datas)
  texto_principal  trafilatura: o texto principal da página, sem menus e rodapés

Cada habilidade só age com a biblioteca instalada (o fluxo instala todas: scripts/instalar.sh); sem ela, o motivo fica
registrado em "ausentes". Nada é inventado: o que vem daqui é dado com trecho, nunca certidão.
"""
from __future__ import annotations

import re
from datetime import date
from functools import lru_cache
from typing import Any

HABILIDADES = ("idioma", "publicacao", "datas", "valores", "metadados", "texto_principal")
CONTEXTO_PRAZO = re.compile(r"(?i)inscri|prazo|encerr|até|data limite|submiss|entrega|vig[êe]ncia|resultado|recurso")


@lru_cache(maxsize=1)
def _detector():
    from lingua import LanguageDetectorBuilder
    return LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()


def idioma(texto: str) -> str | None:
    lang = _detector().detect_language_of(texto[:4000])
    return lang.iso_code_639_1.name.lower() if lang else None


def publicacao(html: str, url: str | None = None) -> str | None:
    from htmldate import find_date
    return find_date(html, url=url, outputformat="%Y-%m-%d", original_date=True)


def datas(texto: str, limite: int = 25) -> list[dict[str, str]]:
    """As datas citadas, com o trecho; marcadas quando o trecho fala de prazo (inscrição, encerramento, resultado...)."""
    import datefinder
    saida, vistos = [], set()
    for d, fonte in datefinder.find_dates(texto[:200000], source=True, first="day"):
        if not (2000 <= d.year <= date.today().year + 3):
            continue
        iso = d.date().isoformat()
        i = texto.find(fonte)
        trecho = re.sub(r"\s+", " ", texto[max(0, i - 120):i + len(fonte) + 40]).strip() if i >= 0 else fonte
        if (iso, trecho[:60]) in vistos:
            continue
        vistos.add((iso, trecho[:60]))
        saida.append({"data": iso, "trecho": trecho, "prazo": bool(CONTEXTO_PRAZO.search(trecho))})
        if len(saida) >= limite:
            break
    return saida


def valores(texto: str, limite: int = 15) -> list[dict[str, Any]]:
    from price_parser import Price
    saida = []
    for m in re.finditer(r"R\$\s?[\d.]+(?:,\d{1,2})?(?:\s?(?:milh[õo]es|milh[ãa]o|bilh[õo]es|bilh[ãa]o|mil)\b)?", texto[:200000]):
        p = Price.fromstring(m.group(0), decimal_separator=",")
        if p.amount is None:
            continue
        g = m.group(0)
        mult = 1_000_000_000 if "bilh" in g else 1_000_000 if "milh" in g else 1_000 if "mil" in g else 1
        trecho = re.sub(r"\s+", " ", texto[max(0, m.start() - 100):m.end() + 40]).strip()
        saida.append({"valor": float(p.amount) * mult, "texto": m.group(0), "trecho": trecho})
        if len(saida) >= limite:
            break
    return saida


def metadados(html: str, url: str | None = None) -> list[dict[str, Any]]:
    import extruct
    d = extruct.extract(html, base_url=url, syntaxes=["json-ld", "microdata", "opengraph"], uniform=True)
    itens = []
    for sintaxe in ("json-ld", "microdata", "opengraph"):
        for item in d.get(sintaxe) or []:
            if isinstance(item, dict):
                itens.append({k: v for k, v in item.items() if k in ("@type", "name", "headline", "startDate", "endDate", "datePublished",
                                                                        "dateModified", "organizer", "author", "description", "og:title",
                                                                        "og:description", "article:published_time")})
    return [i for i in itens if i][:10]


def texto_principal(html: str, url: str | None = None) -> str | None:
    import trafilatura
    return trafilatura.extract(html, url=url, include_comments=False, include_tables=True, favor_recall=True)


def enriquecer(texto: str | None, html: str | None = None, url: str | None = None, ligadas: tuple[str, ...] = HABILIDADES) -> dict[str, Any]:
    """O que o canivete extrai do texto e da página; cada habilidade ausente fica registrada (nunca simula)."""
    r: dict[str, Any] = {"ausentes": []}
    base = texto or ""
    if html and "texto_principal" in ligadas:
        try:
            principal = texto_principal(html, url)
            if principal and len(principal) > 200:
                r["texto_principal"] = principal[:20000]
                base = base or principal
        except ImportError:
            r["ausentes"].append("texto_principal (trafilatura)")
    acoes = {"idioma": lambda: idioma(base) if len(base) > 40 else None, "datas": lambda: datas(base) if base else [],
             "valores": lambda: valores(base) if base else [], "publicacao": lambda: publicacao(html, url) if html else None,
             "metadados": lambda: metadados(html, url) if html else []}
    for nome, fn in acoes.items():
        if nome not in ligadas:
            continue
        try:
            v = fn()
            if v:
                r[nome] = v
        except ImportError as e:
            r["ausentes"].append(f"{nome} ({e.name})")
        except Exception as e:  # noqa: BLE001 — uma habilidade que falha num documento não derruba o achado
            r.setdefault("falhas", []).append(f"{nome}: {type(e).__name__}")
    if not r["ausentes"]:
        r.pop("ausentes")
    return r
