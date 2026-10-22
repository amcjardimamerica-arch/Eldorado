"""A normalização: datas, valores, números por extenso e CNPJ, a partir do texto literal.

Formas de data vistas nas 7.612 certidões reais do Eldorado0: 30/10/2026, 30/10/26, 2026-10-30, "30 de outubro de
2026" e datas sem o ano ("até o dia 4 de outubro"), cujo ano é deduzido pela data de referência do documento.
Os números por extenso têm regra própria: o number-parser foi descartado por não aceitar português (medido).
"""
from __future__ import annotations

import re
from datetime import date

from price_parser import Price
from validate_docbr import CNPJ

MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
         "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
_MES = "|".join(MESES)
DATA = re.compile(rf"\b(\d{{1,2}})/(\d{{1,2}})(?:/(\d{{2,4}}))?\b"
                  rf"|\b(\d{{4}})-(\d{{2}})-(\d{{2}})\b"
                  rf"|\b(\d{{1,2}})º?\s+de\s+({_MES})(?:\s+de\s+(\d{{4}}))?\b", re.I)
_ESCALA = r"(?:\s*(?:milh(?:ões|oes|ão|ao)|bilh(?:ões|oes|ão|ao)|mil)\b)?"
VALOR = re.compile(r"R\$\s*\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?" + _ESCALA + r"|R\$\s*\d+(?:,\d{1,2})?" + _ESCALA, re.I)
CNPJ_RX = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")

UNIDADES = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
            "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "catorze": 14, "quatorze": 14, "quinze": 15, "dezesseis": 16,
            "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60,
            "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100, "cento": 100, "duzentos": 200, "duzentas": 200, "trezentos": 300,
            "trezentas": 300, "quatrocentos": 400, "quatrocentas": 400, "quinhentos": 500, "quinhentas": 500, "seiscentos": 600,
            "seiscentas": 600, "setecentos": 700, "setecentas": 700, "oitocentos": 800, "oitocentas": 800, "novecentos": 900, "novecentas": 900}
MULTIPLICADORES = {"mil": 1_000, "milhão": 1_000_000, "milhao": 1_000_000, "milhões": 1_000_000, "milhoes": 1_000_000,
                   "bilhão": 1_000_000_000, "bilhao": 1_000_000_000, "bilhões": 1_000_000_000, "bilhoes": 1_000_000_000}
EXTENSO = re.compile(r"\b(?:(?:" + "|".join(sorted(UNIDADES, key=len, reverse=True)) + "|" + "|".join(MULTIPLICADORES) + r")(?:\s+e\s+|\s+|$))+", re.I)


def _ano(a: str | None, referencia: date, mes: int, dia: int) -> int:
    if a:
        n = int(a)
        return n + 2000 if n < 100 else n
    ano = referencia.year                        # sem ano: o do documento; se ficaria mais de 6 meses para trás, o seguinte
    try:
        if (referencia - date(ano, mes, dia)).days > 183:
            ano += 1
    except ValueError:
        pass
    return ano


def datas(texto: str, referencia: date | None = None) -> list[date]:
    """Todas as datas do texto, na ordem em que aparecem (datas impossíveis são ignoradas)."""
    ref = referencia or date.today()
    saida = []
    for m in DATA.finditer(texto):
        try:
            if m.group(1):
                d, mes = int(m.group(1)), int(m.group(2))
                saida.append(date(_ano(m.group(3), ref, mes, d), mes, d))
            elif m.group(4):
                saida.append(date(int(m.group(4)), int(m.group(5)), int(m.group(6))))
            else:
                d, mes = int(m.group(7)), MESES[m.group(8).lower()]
                saida.append(date(_ano(m.group(9), ref, mes, d), mes, d))
        except ValueError:
            continue
    return saida


def extenso(texto: str) -> int | None:
    """'trinta mil' → 30000; 'dois milhões e quinhentos mil' → 2500000. None se não for número por extenso."""
    palavras = re.findall(r"[a-zà-ú]+", texto.lower())
    total, grupo, achou = 0, 0, False
    for p in palavras:
        if p == "e":
            continue
        if p in UNIDADES:
            grupo += UNIDADES[p]
            achou = True
        elif p in MULTIPLICADORES:
            total += max(grupo, 1) * MULTIPLICADORES[p]
            grupo, achou = 0, True
        else:
            return None
    return total + grupo if achou else None


def valores(texto: str) -> list[float]:
    """Os valores em reais do texto, inclusive 'R$ 1,5 milhão' e 'R$ 100 mil'."""
    saida = []
    for m in VALOR.finditer(texto):
        bruto = m.group(0)
        mult = (1_000_000_000 if re.search(r"bilh", bruto, re.I) else 1_000_000 if re.search(r"milh", bruto, re.I)
                else 1_000 if re.search(r"\bmil\b", bruto, re.I) else 1)
        numero = re.sub(r"(?i)\s*(mil|milh(?:ão|ões|ao|oes)|bilh(?:ão|ões))", "", bruto)
        p = Price.fromstring(numero, decimal_separator=",")
        if p.amount is not None:
            saida.append(float(p.amount) * mult)
    ocupados = [m.span() for m in VALOR.finditer(texto)]
    inicio = "|".join(sorted((u for u in UNIDADES if u != "zero"), key=len, reverse=True))
    for m in re.finditer(rf"\b((?:{inicio})(?:\s+(?:e\s+)?[a-zà-ú]+){{0,8}}?)\s+(?:de\s+)?reais\b", texto, re.I):
        if any(a < m.end() and m.start() < b for a, b in ocupados):
            continue                                      # já lido como valor em reais
        n = extenso(m.group(1))
        if n:
            saida.append(float(n))
    return saida


def cnpjs(texto: str) -> list[str]:
    """Os CNPJ válidos (pelos dígitos verificadores), só com números."""
    v = CNPJ()
    return [re.sub(r"\D", "", c) for c in CNPJ_RX.findall(texto) if v.validate(re.sub(r"\D", "", c))]
