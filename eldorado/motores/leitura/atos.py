"""O recorte dos atos (canivete suíço): a edição inteira de um diário em PDF ou texto → um ato por cabeçalho.

Cada ato traz o cabeçalho (o título), o órgão (as linhas logo acima do cabeçalho), o começo do texto (para os vetos
que precisam olhar além do título: um "EDITAL Nº" de licença ambiental tem o mesmo título de um edital de verdade) e o
texto integral até o próximo cabeçalho.
"""
from __future__ import annotations

import re

CABECALHO = (r"(?m)^[ \t]*((?:EDITAL|AVISO|PORTARIA|DECRETO|LEI|EXTRATO|RESOLU[ÇC][ÃA]O|INSTRU[ÇC][ÃA]O NORMATIVA|TERMO|CHAMAMENTO|CHAMADA|"
             r"ATO|DESPACHO|COMUNICADO|RETIFICA[ÇC][ÃA]O|ERRATA|CONVOCA[ÇC][ÃA]O|SELE[ÇC][ÃA]O|PR[ÊE]MIO|HOMOLOGA[ÇC][ÃA]O)\b[^\n]{0,140})$")
ORGAO = re.compile(r"(?i)secretaria|fundo|funda[çc][ãa]o|instituto|procuradoria|gabinete|ag[êe]ncia|companhia|conselho|controladoria|prefeitura|"
                   r"c[âa]mara|tribunal|minist[ée]rio|superintend|diretoria|coordena")


def recortar(texto: str, cabecalho: str = CABECALHO, inicio: int = 400) -> list[dict[str, str | int]]:
    marcas = list(re.finditer(cabecalho, texto))
    atos = []
    for n, m in enumerate(marcas):
        fim = marcas[n + 1].start() if n + 1 < len(marcas) else len(texto)
        corpo = texto[m.start():fim].strip()
        if len(corpo) < 60:                                          # cabeçalho solto, sem ato
            continue
        acima = [x.strip() for x in texto[max(0, m.start() - 400):m.start()].splitlines() if x.strip()][-4:]
        orgao = " › ".join(x for x in acima if ORGAO.search(x) and len(x) < 140)
        depois = re.sub(r"\s+", " ", corpo[len(m.group(1)):])[:inicio].strip()
        atos.append({"ordem": len(atos) + 1, "titulo": re.sub(r"\s+", " ", m.group(1)).strip(), "orgao": orgao, "inicio": depois,
                     "texto": corpo})
    return atos
