"""Forma 5: a vigilância: só segue quando a página mudou.

A assinatura é do trecho que importa (o texto da página, ou o de um seletor), sem as partes que mudam a toda hora
(datas, horas, contadores de acesso). Página sem mudança não é relida, o que poupa a fonte e a máquina. As janelas
previstas pela análise chegam no plano da Regência; a vigilância não consulta a base.
"""
from __future__ import annotations

import hashlib
import re

from selectolax.lexbor import LexborHTMLParser

VOLATIL = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}:\d{2}(?::\d{2})?|\b\d+\s*(?:visualiza|acessos|views)\w*|\b\d{10,}\b", re.I)


def assinatura(html: bytes, seletor: str | None = None) -> str:
    arvore = LexborHTMLParser(html.decode("utf-8", errors="replace"))
    for no in arvore.css("script, style, noscript"):
        no.decompose()
    alvo = arvore.css_first(seletor) if seletor else arvore.body
    texto = (alvo.text(separator=" ") if alvo else "") or ""
    texto = VOLATIL.sub("#", re.sub(r"\s+", " ", texto)).strip().lower()
    return hashlib.sha256(texto.encode()).hexdigest()


def mudou(anterior: str | None, atual: str) -> bool:
    return anterior != atual
