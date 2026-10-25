"""A importação das empresas do Eldorado0 (titular, 25/10/2026: 22.174 empresas com os programas validados deveriam ter sido
incorporadas). Unifica com as empresas da Biblioteca pelo CNPJ: o que a Biblioteca já tem prevalece e o que falta vem do
Eldorado0; a ficha completa (o cadastro, o potencial, o Salic, a avaliação, os programas com a prova) é guardada na
empresa; os incentivos validados entram com a prova e a fonte, sem repetir. Tudo pelos eventos (só o gravador escreve)."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

LEI = {"rouanet": "Rouanet", "pat": "PAT", "esporte": "Esporte", "pronon": "Pronon", "pronas": "Pronas", "goyazes": "Goyazes", "fia": "FIA",
       "idoso": "Idoso", "icms": "ICMS"}


def _cnpj(x: str | None) -> str | None:
    d = re.sub(r"\D", "", x or "")
    return d if len(d) == 14 else None


def importar(bib: sqlite3.Connection, ranking_e0: dict[str, Any], diario) -> dict[str, int]:
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existentes = {r[0]: r for r in bib.execute("SELECT cnpj, razao_social, nome_fantasia, uf, municipio_ibge, porte, atividade_principal, "
                                               "regime_tributario, site, descoberta_por, descoberta_em FROM empresa")}
    ja_inc = {(r[0], r[1]) for r in bib.execute("SELECT cnpj, lei FROM incentivo")}
    conta = {"empresas": 0, "novas": 0, "completadas": 0, "incentivos": 0, "sem_cnpj": 0}
    for e in ranking_e0.get("empresas", []):
        cad = e.get("cadastro") or {}
        cnpj = _cnpj(cad.get("cnpj") or e.get("cnpj"))
        chave = cnpj or f"E0:{e.get('uid') or e.get('_chave') or e.get('nome')}"[:120]
        if not cnpj:
            conta["sem_cnpj"] += 1
        ex = existentes.get(chave)
        novo = {"cnpj": chave, "razao_social": (ex and ex[1]) or cad.get("razao_social") or e.get("nome") or chave,
                "nome_fantasia": (ex and ex[2]) or cad.get("nome_fantasia") or e.get("nome"),
                "uf": (ex and ex[3]) or cad.get("uf"), "municipio_ibge": (ex and ex[4]) or cad.get("municipio") or e.get("municipio"),
                "porte": (ex and ex[5]) or cad.get("porte"), "atividade_principal": (ex and ex[6]) or cad.get("cnae_principal") or e.get("setor"),
                "regime_tributario": ex and ex[7], "site": (ex and ex[8]) or cad.get("site"),
                "descoberta_por": (ex and ex[9]) or "importacao", "descoberta_em": (ex and ex[10]) or agora, "atualizada_em": agora,
                "ficha": json.dumps({"eldorado0": {k: e.get(k) for k in ("origem", "nivel", "nivel_ordem", "pontuacao", "pontos_lista", "potencial",
                                                                           "salic", "avaliacao", "programas", "faixa", "apoia", "via_de_entrada", "condicao")},
                                     "cadastro": cad}, ensure_ascii=False, default=str)}
        diario.emitir("empresa.registrada", "importacao-eldorado0", novo)
        conta["empresas"] += 1
        conta["novas" if not ex else "completadas"] += 1
        for p in e.get("programas") or []:
            lei = LEI.get(str(p.get("chave") or "").lower())
            if not lei or not (p.get("verificado") or p.get("historico")) or (chave, lei) in ja_inc:
                continue
            ja_inc.add((chave, lei))
            valor = (e.get("salic") or {}).get("total") if lei == "Rouanet" else None
            diario.emitir("incentivo.registrado", "importacao-eldorado0", {
                "cnpj": chave, "lei": lei, "ano": None, "valor": valor, "comprovado": int(bool(p.get("verificado"))),
                "fonte": f"Eldorado0 · {p.get('fonte') or p.get('orgao') or ''} · {str(p.get('prova') or '')[:300]}".strip(" ·"), "em": agora})
            conta["incentivos"] += 1
    return conta
