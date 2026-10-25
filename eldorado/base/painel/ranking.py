"""O ranking de empresas (titular, 25/10/2026: a aba "Ranking de empresas" estava zerada: o arquivo ranking_apoiadores.json
era a estrutura vazia do Eldorado0, e ninguém montava o ranking a partir das empresas e incentivos da Biblioteca).

As duas listas:
  destinação tributária  as empresas com incentivo fiscal registrado: o patrocínio pela Lei Rouanet (o Salic, com o valor:
                         verificado) e os maiores contribuintes do ICMS de Goiás (o potencial para o Goyazes e os
                         incentivos estaduais);
  doação e patrocínio    as empresas sem incentivo fiscal registrado (o patrocínio direto, o instituto, o marketing social).
A pontuação (0 a 100, com o motivo): o valor patrocinado pela Rouanet (escala logarítmica), ser grande contribuinte do ICMS,
ter o cadastro completo (CNPJ, atividade, site) e ser de Goiás.
"""

from __future__ import annotations

import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

LEIS = [
    {
        "chave": "rouanet",
        "nome": "Lei Rouanet (cultura)",
        "curto": "Rouanet",
        "lei": "Lei 8.313/1991",
        "orgao": "MinC / Salic",
        "teto": "4% do IRPJ devido (Lucro Real)",
        "porta": "o projeto aprovado no Salic; a empresa patrocina e deduz",
        "cor": "#D63A6B",
    },
    {
        "chave": "goyazes",
        "nome": "Lei Goyazes (cultura, Goiás)",
        "curto": "Goyazes",
        "lei": "Lei estadual 13.613/2000",
        "orgao": "Secult-GO",
        "teto": "parte do ICMS devido",
        "porta": "o projeto aprovado no Goyazes; a empresa contribuinte do ICMS-GO patrocina",
        "cor": "#B8860B",
    },
    {
        "chave": "esporte",
        "nome": "Lei de Incentivo ao Esporte",
        "curto": "Esporte",
        "lei": "Lei 11.438/2006",
        "orgao": "Ministério do Esporte",
        "teto": "2% do IRPJ devido",
        "porta": "o projeto aprovado na LIE",
        "cor": "#7CB518",
    },
    {
        "chave": "pronon",
        "nome": "PRONON (oncologia)",
        "curto": "PRONON",
        "lei": "Lei 12.715/2012",
        "orgao": "Ministério da Saúde",
        "teto": "1% do IRPJ devido",
        "porta": "a instituição credenciada no PRONON",
        "cor": "#2F79D0",
    },
    {
        "chave": "pronas",
        "nome": "PRONAS/PCD (pessoa com deficiência)",
        "curto": "PRONAS",
        "lei": "Lei 12.715/2012",
        "orgao": "Ministério da Saúde",
        "teto": "1% do IRPJ devido",
        "porta": "a instituição credenciada no PRONAS/PCD",
        "cor": "#12A5B5",
    },
    {
        "chave": "fia",
        "nome": "Fundo da Infância e da Adolescência",
        "curto": "FIA",
        "lei": "ECA, art. 260",
        "orgao": "os conselhos de direitos",
        "teto": "1% do IRPJ devido",
        "porta": "o depósito no fundo do conselho, com o projeto chancelado",
        "cor": "#E0A100",
    },
    {
        "chave": "idoso",
        "nome": "Fundo da Pessoa Idosa",
        "curto": "Idoso",
        "lei": "Lei 12.213/2010",
        "orgao": "os conselhos da pessoa idosa",
        "teto": "1% do IRPJ devido",
        "porta": "o depósito no fundo do conselho",
        "cor": "#8C6D3F",
    },
]
ORIGEM_TRIB, ORIGEM_DOA = "destinação tributária", "doação e patrocínio"
NIVEIS = {"Destinadora ativa": 1, "Grande contribuinte do ICMS": 2, "Parceira social": 3, "A qualificar": 5}


def _din(v: float) -> str:
    return f"R$ {v / 1e6:.1f} mi".replace(".", ",") if v >= 1e6 else f"R$ {round(v / 1e3)} mil" if v >= 1e3 else f"R$ {v:.0f}"


def montar(bib: sqlite3.Connection, molde) -> dict[str, Any]:
    fmt = bib.row_factory
    bib.row_factory = None
    try:
        tem_ficha = "ficha" in {r[1] for r in bib.execute("PRAGMA table_info(empresa)")}
        empresas = bib.execute(
            "SELECT cnpj, razao_social, nome_fantasia, uf, municipio_ibge, porte, atividade_principal, regime_tributario, site, "
            "descoberta_por, " + ("ficha" if tem_ficha else "NULL") + " FROM empresa"
        ).fetchall()
        inc = defaultdict(list)
        for cnpj, lei, ano, valor, comprovado, fonte in bib.execute("SELECT cnpj, lei, ano, valor, comprovado, fonte FROM incentivo"):
            inc[cnpj].append({"lei": lei, "ano": ano, "valor": valor, "comprovado": bool(comprovado), "fonte": fonte})
    except sqlite3.Error:
        empresas, inc = [], {}
    finally:
        bib.row_factory = fmt
    saida = []
    for cnpj, razao, fantasia, uf, mun, porte, atividade, regime, site, por, ficha in empresas:
        regs = inc.get(cnpj, [])
        rou = [x for x in regs if (x["lei"] or "").lower() == "rouanet"]
        icms = [x for x in regs if (x["lei"] or "").upper() == "ICMS"]
        valor_rou = sum(x["valor"] or 0 for x in rou)
        base, porque = 0, []
        if rou:
            pts = min(60, 25 + int(10 * math.log10(max(valor_rou, 10))))
            base += pts
            porque.append(f"patrocinou pela Rouanet ({_din(valor_rou)} no Salic): {pts}")
        if icms:
            base += 25
            porque.append("um dos 500 maiores contribuintes do ICMS de Goiás (potencial para o Goyazes): 25")
        cad = sum(bool(x) for x in (cnpj, atividade, site))
        base += 3 * cad
        porque.append(f"cadastro ({cad} de 3: CNPJ, atividade, site): {3 * cad}")
        if uf == "GO":
            base += 6
            porque.append("de Goiás: 6")
        base = min(100, base)
        anos = sorted({x["ano"] for x in rou if x["ano"]})
        bonus = 5 * max(0, len(anos) - 1)
        nivel = (
            "Destinadora ativa" if rou else "Grande contribuinte do ICMS" if icms else "Parceira social" if por == "importacao" else "A qualificar"
        )
        programas = (
            [{"chave": "rouanet", "verificado": True, "historico": True, "prova": f"{len(rou)} registro(s) no Salic · {_din(valor_rou)}"}]
            if rou
            else []
        ) + ([{"chave": "goyazes", "verificado": False, "historico": False, "prova": "contribuinte do ICMS-GO (o potencial)"}] if icms else [])
        saida.append(
            {
                "uid": cnpj or razao,
                "nome": fantasia or razao,
                "origem": ORIGEM_TRIB if regs else ORIGEM_DOA,
                "site": site,
                "cadastro": {
                    "cnpj": cnpj,
                    "razao_social": razao,
                    "nome_fantasia": fantasia,
                    "uf": uf,
                    "municipio": mun,
                    "porte": porte,
                    "cnae_principal": atividade,
                    "regime": regime,
                },
                "programas": programas,
                "nivel": nivel,
                "nivel_ordem": NIVEIS[nivel],
                "pontuacao": {"base": base, "bonus": bonus, "porque": " · ".join(porque)},
                "pontos_lista": base + bonus,
                "potencial": {"apurou": False},
                "apoia": ", ".join(p["chave"] for p in programas),
                "avaliacao": {
                    "criterios": [
                        {"chave": "cadastro", "rotulo": "cadastro", "pontos": 3 * cad, "valor": f"{cad} de 3", "porque": "CNPJ, atividade e site"},
                        {"chave": "goias", "rotulo": "Goiás", "pontos": 6 if uf == "GO" else 0, "valor": uf or "—", "porque": "a sede em Goiás"},
                    ]
                },
                "valor_rouanet": valor_rou,
                "incentivos": [{"lei": x["lei"], "ano": x["ano"], "valor": x["valor"], "fonte": x["fonte"]} for x in regs][:12],
            }
        )
        # a ficha do Eldorado0 (25/10/2026): o cadastro completo, o potencial, o Salic, a avaliação e os programas validados
        try:
            f = json.loads(ficha) if ficha else {}
        except ValueError:
            f = {}
        e0 = f.get("eldorado0") or {}
        if e0:
            e = saida[-1]
            e["cadastro"] = {**(f.get("cadastro") or {}), **{k: v for k, v in e["cadastro"].items() if v}}
            for k in ("potencial", "salic", "avaliacao", "faixa", "via_de_entrada", "condicao"):
                if e0.get(k):
                    e[k] = e0[k]
            prog = {p["chave"]: p for p in (e0.get("programas") or []) if isinstance(p, dict) and p.get("chave")}
            for p in e["programas"]:
                prog.setdefault(p["chave"], p)
            e["programas"] = list(prog.values())
            e["apoia"] = ", ".join(prog)
            if e0.get("origem") in (ORIGEM_TRIB, ORIGEM_DOA):
                e["origem"] = e0["origem"]
            if (e0.get("pontos_lista") or 0) > e["pontos_lista"]:  # vale a melhor avaliação (a do Eldorado0 ou a de agora)
                e["pontos_lista"], e["pontuacao"] = e0["pontos_lista"], e0.get("pontuacao") or e["pontuacao"]
                if e0.get("nivel"):
                    e["nivel"], e["nivel_ordem"] = e0["nivel"], e0.get("nivel_ordem") or 5
            e["valor_rouanet"] = max(e["valor_rouanet"], float((e0.get("salic") or {}).get("total") or 0))
    for e in saida:                                                # o arquivo enxuto: o que se repete fica de fora
        e.pop("incentivos", None)
        e["cadastro"].pop("cnaes_secundarios", None)
    for origem in (ORIGEM_TRIB, ORIGEM_DOA):
        lista = sorted(
            [e for e in saida if e["origem"] == origem], key=lambda e: (-e["pontos_lista"], -e["valor_rouanet"], e["nome"] or "")
        )  # o desempate: quem mais destinou
        for n, e in enumerate(lista, 1):
            e["n_na_lista"] = e["posicao"] = n
    r = molde("ranking_apoiadores.json")
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    trib = [e for e in saida if e["origem"] == ORIGEM_TRIB]
    doa = [e for e in saida if e["origem"] == ORIGEM_DOA]
    r.update(
        {
            "gerado_em": agora,
            "por_pagina": 100,
            "catalogo_de_leis": LEIS,
            "empresas": sorted(saida, key=lambda e: (e["origem"], e["n_na_lista"])),
            "regra": "o ranking montado da Biblioteca: as empresas e os incentivos registrados (a Rouanet pelo Salic, o ICMS de Goiás)",
            "total": len(saida),
            "nas_duas_listas": 0,
            "com_cnpj": sum(1 for e in saida if e["cadastro"].get("cnpj")),
            "com_cnae": sum(1 for e in saida if e["cadastro"].get("cnae_principal")),
            "com_site": sum(1 for e in saida if e["site"]),
            "com_programa": sum(1 for e in saida if e["programas"]),
            "com_potencial": sum(1 for e in saida if any(p["chave"] == "goyazes" for p in e["programas"])),
            "da_base_publica": sum(1 for e in saida if e["programas"]),
            "niveis": dict(sorted({k: sum(1 for e in saida if e["nivel"] == k) for k in {e["nivel"] for e in saida}}.items(), key=lambda kv: -kv[1])),
        }
    )
    for chave, lst, rot in (("destinacao_tributaria", trib, "Destinação tributária"), ("patrocinio_privado", doa, "Doação e patrocínio")):
        r.setdefault("listas", {})[chave] = {
            "rotulo": rot,
            "total": len(lst),
            "paginas": [{"n": i // 100 + 1, "de": i + 1, "ate": min(i + 100, len(lst))} for i in range(0, len(lst), 100)],
            "criterios": ["Rouanet (Salic)", "ICMS-GO", "cadastro", "Goiás"],
            "teto": 100,
            "confianca_media": round(sum(e["pontuacao"]["base"] for e in lst) / len(lst), 1) if lst else 0,
            "criterios_sem_dado": ["o valor direcionável do IRPJ (o lucro real não é público)"],
        }
    return r
