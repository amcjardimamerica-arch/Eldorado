"""A origem da oportunidade, decidida POR LIVRO, com evidência (titular, 23/10/2026).

Nenhum motor é, por regra, a fonte original: diários oficiais, portais e sites de divulgação divulgam; um portal (como o
Prosas) tanto replica oportunidades de outros quanto tem as suas. O livro, em geral, tem o link onde foi encontrado (a
divulgação) e outro com a oportunidade original (nos diários, quase sempre a secretaria do município).

Um link é CONFIRMADO como a oportunidade original quando há evidência no próprio livro:
  - o domínio é o do órgão ou do financiador do livro (pelo nome, pelos financiadores conhecidos, ou, num órgão
    municipal, pelo domínio do município: "Secretaria Municipal de Saúde de Buriti de Goiás" ↔ buritidegoias.go.gov.br);
  - a análise externa (o Claude no Chrome) ou a titular o confirmou;
  - o Interceptador o comprovou (o documento com o edital no domínio do órgão).
Fora disso, o link é CANDIDATO: a primeira busca é cega, e a rede neural vincula e aprofunda depois. A lista de
republicadores é só um indício (pesa contra, mas não decide).
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[3]
CONFIRMADO, CANDIDATO, AUSENTE = "confirmado", "candidato", "ausente"
SIGLAS_GOVBR = {"saude": "saúde", "esporte": "esporte", "cultura": "cultura", "mdh": "direitos humanos", "mds": "desenvolvimento social",
                "mec": "educação", "mma": "meio ambiente", "cnpq": "cnpq", "funarte": "funarte", "conanda": "conanda", "mulheres": "mulheres",
                "turismo": "turismo", "mcti": "ciência"}


def _sem(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", "".join(c for c in unicodedata.normalize("NFKD", (t or "").lower()) if not unicodedata.combining(c)))


def dominio(url: str | None) -> str:
    return (urlsplit(str(url or "")).hostname or "").lower().removeprefix("www.")


@lru_cache(maxsize=1)
def _referencias() -> dict:
    return json.loads((RAIZ / "config/missao/republicadores.json").read_text(encoding="utf-8"))


def eh_republicador(url: str | None) -> bool:
    """Um INDÍCIO de divulgação (notícia, agregador, rede social, encurtador, buscador); nunca decide sozinho."""
    d, ref = dominio(url), _referencias()
    lista = {h.lower() for g in ("noticia", "agregador", "rede_social", "encurtador", "buscador") for h in ref.get(g, [])}
    return bool(d) and any(d == r or d.endswith("." + r) for r in lista)


def _municipio_do_orgao(orgao: str) -> str | None:
    m = re.search(r"(?:munic[ií]pio|municipal|prefeitura)(?: municipal)? (?:de |do |da )?(.+?)(?:$| - | – |/| › )", orgao or "", re.I)
    return m.group(1).strip() if m else None


def evidencia(url: str | None, orgao: str | None, localidade: str | None = None) -> str | None:
    """A evidência de que o link é do órgão ou do financiador do livro; None se não houver."""
    d = dominio(url)
    if not d or not orgao and not localidade:
        return None
    o = _sem(orgao or "")
    for nome, dom in (_referencias().get("financiadores_conhecidos") or {}).items():
        if _sem(nome) in o and (d == dom or d.endswith("." + dom)) and dom != "gov.br":
            return f"domínio do financiador conhecido ({nome})"
    if d == "gov.br" or d.endswith(".gov.br") and d.count(".") == 1:
        caminho = urlsplit(str(url)).path.strip("/").split("/")[0].lower()
        if caminho in SIGLAS_GOVBR and _sem(SIGLAS_GOVBR[caminho]) in o:
            return f"página do órgão no gov.br (/{caminho})"
    raiz = d.split(".")[0]
    palavras = [p for p in o.split() if len(p) > 4 and p not in {"secretaria", "municipal", "estadual", "estado", "fundacao", "instituto", "ministerio",
                                                                  "nacional", "prefeitura", "goias", "brasil", "publico", "publica", "governo"}]
    for p in palavras:
        if p in raiz:
            return f"o domínio traz o nome do órgão ({p})"
    municipio = _municipio_do_orgao(orgao or "") or localidade
    if municipio:
        slug = _sem(municipio).replace(" ", "")
        if slug and slug in d.replace("-", "") and re.search(r"\.(go|[a-z]{2})\.gov\.br$|\.gov\.br$", d):
            return f"domínio do município ({municipio})"
    return None


def classificar(url: str | None, orgao: str | None, localidade: str | None = None, confirmado_antes: bool = False) -> tuple[str, str]:
    """confirmado, candidato ou ausente, com o motivo."""
    if not url:
        return AUSENTE, "sem link da oportunidade original"
    if confirmado_antes:
        return CONFIRMADO, "confirmado antes (análise externa, titular ou Interceptador)"
    ev = evidencia(url, orgao, localidade)
    if ev:
        return CONFIRMADO, ev
    return CANDIDATO, ("indício de divulgação (site que republica)" if eh_republicador(url) else "sem evidência do órgão no link: a rede aprofunda")
