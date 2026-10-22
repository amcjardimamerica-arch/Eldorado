"""A chave do livro nesta missão: o livro é o PROGRAMA, não a edição.

A chave tira o número do ato e o ano ("Edital nº 3/2026" e "Edital nº 5/2025" do mesmo programa e órgão caem no mesmo
livro), os acentos e as palavras sem conteúdo; junta o título normalizado, o órgão e a UF.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

VAZIAS = {"de", "da", "do", "das", "dos", "e", "a", "o", "as", "os", "para", "em", "no", "na", "nos", "nas", "com", "por", "ao", "aos",
          "edital", "chamamento", "chamada", "publico", "publica", "aviso", "abertura", "inscricoes", "abre", "aberta", "aberto", "n", "numero"}


def normalizar(texto: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFKD", str(texto or "").lower()) if not unicodedata.combining(c))
    t = re.sub(r"\bn[ºo°.]*\s*\d+[\d./-]*", " ", t)          # nº 3/2026, n. 005-2025
    t = re.sub(r"\b(19|20)\d{2}\b", " ", t)                   # anos
    t = re.sub(r"\b\d+[ªaº]?\s*edicao\b|\bedicao\s*\d+\b", " ", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return " ".join(p for p in t.split() if p not in VAZIAS and not p.isdigit())


def chave(titulo: str, orgao: str | None = None, uf: str | None = None) -> str:
    base = f"{normalizar(titulo)}|{normalizar(orgao or '')}|{(uf or '').upper()}"
    return hashlib.sha256(base.encode()).hexdigest()[:20]
