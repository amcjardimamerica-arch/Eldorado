"""Forma 2: os dados abertos: as APIs oficiais (pela configuração de cada motor) e os portais CKAN (dados.gov.br e
estaduais), pelo endpoint padrão package_search. A terceira rota (Brasil.io) fica como reserva, a testar na criação.
"""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

import jmespath

from .pistas import Buscar, Pista


def ckan(buscar: Buscar, base: str, termos: str, linhas: int = 50) -> list[Pista]:
    d = json.loads(buscar(f"{base.rstrip('/')}/api/3/action/package_search?q={quote(termos)}&rows={linhas}").conteudo)
    if not d.get("success", False):
        raise ValueError("CKAN respondeu sem sucesso")
    saida = []
    for p in d["result"]["results"]:
        recursos = p.get("resources") or []
        link = (recursos[0].get("url") if recursos else None) or f"{base.rstrip('/')}/dataset/{p.get('name')}"
        saida.append(Pista(titulo=p.get("title") or p.get("name", ""), link=link, origem=f"dados abertos (CKAN {base})",
                           data=p.get("metadata_modified"), resumo=(p.get("notes") or "")[:500],
                           extra={"organizacao": (p.get("organization") or {}).get("title"), "recursos": len(recursos)}))
    return saida


def lista_js(texto: str, nome: str) -> Any:
    """14/11/2026 (parecer dos motores da Bússola, motor 58): a lista que a página guarda como código JavaScript
    («const EDITAIS = [ {n:'...', link:'https://...'}, ... ]», com comentários) convertida em JSON, sem executar nada: tira os
    comentários fora das cadeias (o «//» dos endereços fica), passa as aspas simples a duplas, põe aspas nos nomes dos
    campos e tira a vírgula final. Erro claro se a lista não estiver na página ou não for convertível."""
    import re
    m = re.search(r"(?:const|let|var)\s+" + re.escape(nome) + r"\s*=\s*\[", texto)
    if not m:
        raise ValueError(f"lista JavaScript {nome} não encontrada na página")
    i, prof, saida, n = m.end() - 1, 0, [], len(texto)
    while i < n:
        c = texto[i]
        if c in "'\"":                                  # a cadeia: copiada como JSON (aspas duplas, escapes preservados)
            q, j, buf = c, i + 1, []
            while j < n and texto[j] != q:
                if texto[j] == "\\" and j + 1 < n:
                    buf.append(texto[j:j + 2] if texto[j + 1] != "'" else "'")
                    j += 2
                    continue
                buf.append('\\"' if texto[j] == '"' else texto[j])
                j += 1
            saida.append('"' + "".join(buf) + '"')
            i = j + 1
            continue
        if texto.startswith("//", i):                      # o comentário de linha (fora de cadeia)
            i = texto.find("\n", i)
            i = n if i < 0 else i
            continue
        if texto.startswith("/*", i):
            i = texto.find("*/", i)
            i = n if i < 0 else i + 2
            continue
        if (c.isalpha() or c in "_$") and saida and "".join(saida).rstrip()[-1:] in ("{", ","):
            j = i
            while j < n and (texto[j].isalnum() or texto[j] in "_$"):
                j += 1
            k = j
            while k < n and texto[k] in " \t\r\n":
                k += 1
            if k < n and texto[k] == ":":                  # o nome do campo (fora de cadeia): entre aspas
                saida.append('"' + texto[i:j] + '"')
                i = j
                continue
        if c in "[{":
            prof += 1
        elif c in "]}":
            prof -= 1
        saida.append(c)
        i += 1
        if prof == 0:
            break
    js = "".join(saida)
    js = re.sub(r",\s*([\]}])", r"\1", js)                            # a vírgula final
    return json.loads(js)


def carregar_json(buscar: Buscar, url: str, json_em: str | None = None) -> Any:
    """A resposta da API como dados. json_em: o seletor EXATO do bloco de JSON dentro de uma página HTML (lição do DOU:
    a mesma página tem outro bloco, o da busca, com uma lista vazia que enganava a versão antiga)."""
    conteudo = buscar(url).conteudo
    if not json_em:
        if conteudo.lstrip()[:1] == b"<":                 # a API que responde em XML (xmltodict): os mesmos caminhos jmespath
            import xmltodict
            return xmltodict.parse(conteudo, attr_prefix="", cdata_key="texto")
        return json.loads(conteudo)
    if json_em.startswith("js:"):                          # 14/11/2026: a lista JavaScript «const NOME = [...]» da página
        return lista_js(conteudo.decode("utf-8", errors="replace"), json_em[3:].strip())
    from selectolax.lexbor import LexborHTMLParser
    no = LexborHTMLParser(conteudo.decode("utf-8", errors="replace")).css_first(json_em)
    if no is None:
        raise ValueError(f"bloco {json_em} não encontrado na página")
    return json.loads(no.text())


def pistas_da_api(doc: Any, caminhos: dict[str, str], origem: str) -> list[Pista]:
    """As pistas de uma resposta: onde está cada campo (jmespath). titulo, link, data e resumo são da pista; os demais
    (uf, orgao, fim, municipio...) vão para os dados do item."""
    saida = []
    for i in jmespath.search(caminhos["itens"], doc) or []:
        link = jmespath.search(caminhos["link"], i)
        if not link:
            continue
        proprios = ("itens", "titulo", "link", "data", "resumo", "total_paginas")
        extra = {k: jmespath.search(v, i) for k, v in caminhos.items() if k not in proprios}
        resumo = jmespath.search(caminhos["resumo"], i) if "resumo" in caminhos else None
        # 08/11/2026: as APIs de busca devolvem o termo marcado em HTML (<span class='highlight'>, <mark>): o título e o resumo
        # da pista são texto, sem as marcas
        titulo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", str(jmespath.search(caminhos["titulo"], i) or ""))).strip()
        resumo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(resumo))).strip() if resumo else None
        saida.append(Pista(titulo=titulo, link=str(link), origem=origem,
                           data=jmespath.search(caminhos["data"], i) if "data" in caminhos else None,
                           resumo=resumo[:1000] if resumo else None, extra={k: v for k, v in extra.items() if v not in (None, "")}))
    return saida


def api_oficial(buscar: Buscar, url: str, caminhos: dict[str, str], json_em: str | None = None) -> list[Pista]:
    """Uma API oficial descrita só na configuração do motor: o endereço e onde está cada campo (jmespath).

    caminhos = {"itens": "data[*]", "titulo": "objeto", "link": "linkSistemaOrigem", "data": "dataEncerramentoProposta"}
    """
    return pistas_da_api(carregar_json(buscar, url, json_em), caminhos, f"API oficial ({url.split('?')[0]})")


def _col(cabecalho: list[str], *partes: str) -> str | None:
    """A coluna cujo nome contém todas as partes (os nomes do arquivo mudam de ano para ano)."""
    for c in cabecalho:
        n = c.lower()
        if all(p in n for p in partes):
            return c
    return None


def siconv_programas(buscar: Buscar, url: str, hoje: str) -> list[Pista]:
    """Transferegov (dados abertos): os programas com recebimento de propostas aberto que aceitam entidades privadas
    sem fins lucrativos. Lógica aproveitada do leitor do Eldorado0 (colunas pelo nome, agrupamento por programa)."""
    import csv
    import io
    import re
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(buscar(url).conteudo))
    bruto = z.read(next(n for n in z.namelist() if n.lower().endswith(".csv")))
    for cod in ("utf-8-sig", "latin-1"):
        try:
            txt = bruto.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    leitor = csv.DictReader(io.StringIO(txt), delimiter=";" if txt[:2000].count(";") >= txt[:2000].count(",") else ",")
    cab = leitor.fieldnames or []
    c = {"cod": _col(cab, "cod", "programa"), "nome": _col(cab, "nome", "programa"), "orgao": _col(cab, "desc", "orgao"),
         "sit": _col(cab, "sit", "programa"), "fim": _col(cab, "fim", "receb"), "fim_esp": _col(cab, "fim", "benef", "esp"),
         "nat": _col(cab, "natureza"), "uf": _col(cab, "uf", "programa"), "mod": _col(cab, "modalidade")}
    if not (c["cod"] and c["nome"] and (c["fim"] or c["fim_esp"])):
        raise ValueError("colunas do Transferegov não reconhecidas: " + ", ".join(cab[:30]))

    def dia(v: str | None) -> str | None:
        v = str(v or "").strip()
        if re.match(r"\d{4}-\d{2}-\d{2}", v):
            return v[:10]
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", v)
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None

    progs: dict[str, dict] = {}
    for lin in leitor:
        fins = [f for f in (dia(lin.get(c[k])) for k in ("fim", "fim_esp") if c.get(k)) if f and f >= hoje]
        if not fins or (c["sit"] and lin.get(c["sit"]) and not re.search(r"dispon|aberto|ativ", lin[c["sit"]], re.I)):
            continue
        cod = (lin.get(c["cod"]) or "").strip()
        p = progs.setdefault(cod, {"nome": lin.get(c["nome"]), "orgao": lin.get(c["orgao"]) if c["orgao"] else None, "fim": max(fins),
                                   "nat": set(), "ufs": set(), "mod": lin.get(c["mod"]) if c["mod"] else None})
        p["fim"] = max(p["fim"], *fins)
        if c["nat"] and lin.get(c["nat"]):
            p["nat"].add(lin[c["nat"]].strip())
        if c["uf"] and lin.get(c["uf"]):
            p["ufs"].add(lin[c["uf"]].strip())
    saida = []
    for cod, p in progs.items():
        nats = " ".join(sorted(p["nat"]))
        if nats and not re.search(r"privad|sem fins|sociedade civil|osc|entidade", nats, re.I):
            continue                                            # programa só para órgão público
        ufs = sorted(p["ufs"])
        link = f"https://discricionarias.transferegov.sistema.gov.br/voluntarias/programa/{cod}"
        saida.append(Pista(titulo=f"{(p['nome'] or '').strip()[:220]} (programa {cod})", link=link,
                           origem="dados abertos (Transferegov)", resumo=nats[:500] or None,
                           extra={"orgao": p["orgao"], "fim": p["fim"], "uf": ufs[0] if len(ufs) == 1 else None, "modalidade": p["mod"],
                                  "codigo_programa": cod}))
    return saida
