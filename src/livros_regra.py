"""REGRA DOS LIVROS PARA OS MOTORES E O ESPIÃO (titular, 01/10).

MOTORES REGULARES (todos): cada oportunidade que um motor encontra é comparada com a Biblioteca.
  · já tem livro  → o livro RECEBE as informações básicas dos 12 itens do checklist (preenche o que faltava; atualiza o
                    que mudou), com a data e o motor de origem;
  · não tem livro → o livro é CRIADO (pelo repositório, no mesmo ciclo).
  Depois, o parâmetro LOCAIS DE BUSCA é recalculado: quantos livros, páginas e domínios a Biblioteca cobre e quantos
  livros cada motor criou ou atualizou no dia (docs/dados/locais_de_busca.json e o cabeçalho do catálogo).
PILOTO - ESPIÃO: busca o que NÃO está nos livros; cada achado novo vira um livro na hora (o que já existe só recebe a
  informação nova). Empresa encontrada vai ao ranking de empresas, na aba que se aplicar (Destinação Tributária e/ou
  Doação e patrocínio), marcada 'a verificar' até o Interceptador confirmar.
Só dados — nenhum arquivo é anexado a um livro.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
INDICE = ROOT / "estado/opressores_indice.json"
LOCAIS = ROOT / "docs/dados/locais_de_busca.json"
DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera",
        "Requisitos", "Anexos", "Destinação", "Área de atuação"]


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _valor(v) -> str:
    if isinstance(v, dict):
        v = v.get("v") or v.get("valor") or v.get("trecho") or ""
    return re.sub(r"\s+", " ", str(v or "")).strip()[:200]


def anotar_checklist(livro: dict, checklist: dict, origem: str) -> int:
    """Leva ao livro as informações básicas dos 12 itens. Devolve quantos itens mudaram."""
    lv = livro.setdefault("livro", {}); ck = lv.setdefault("checklist", {}); mud = 0
    for item in DOZE:
        novo = _valor((checklist or {}).get(item))
        if not novo:
            continue
        atual = (ck.get(item) or {}).get("v")
        if atual != novo:
            ck[item] = {"v": novo, "de": origem[:60], "em": date.today().isoformat()}; mud += 1
    if mud:
        lv["checklist_itens"] = sum(1 for i in DOZE if (ck.get(i) or {}).get("v"))
        at = lv.setdefault("atualizacoes", [])
        at.append({"em": _agora(), "o_que": f"{mud} item(ns) do checklist atualizado(s) por {origem[:60]}"}); lv["atualizacoes"] = at[-8:]
    return mud


def _checklist_de(it: dict) -> dict:
    """Checklist básico de um achado que não veio com checklist pronto (ex.: Espião)."""
    return {"Objeto": it.get("objeto") or it.get("titulo"), "Prazo de inscrição": " a ".join(x for x in (it.get("inicio"), it.get("fim") or it.get("prazo")) if x),
            "Valor": it.get("valor"), "Órgão / financiador": it.get("orgao") or it.get("empresa"), "Território": it.get("uf"),
            "Anexos": it.get("url") or it.get("link_oficial"), "Área de atuação": it.get("area") or it.get("tema")}


def aplicar_motores() -> dict:
    """Todos os motores regulares: oportunidade com livro → o livro recebe o checklist; locais de busca recalculados."""
    C = _j(CAT, {}); ms = C.get("motores") or []
    por_id = {x.get("id"): x for x in ms}
    idx = (_j(INDICE, {}) or {}).get("indice") or {}
    F = _j(FLUXO, {})
    hoje = date.today().isoformat()
    atual, criado = Counter(), Counter()
    for uf, itens in (F.get("itens_por_uf") or {}).items():
        for it in itens:
            oid = (idx.get(it.get("id")) or {}).get("opressor")
            x = por_id.get(oid)
            if not x:
                continue
            origem = str(it.get("origem") or "motor")
            if str(x.get("criado_em") or "") == hoje:
                criado[origem] += 1
            if anotar_checklist(x, it.get("checklist") or {}, origem):
                atual[origem] += 1
    hosts = {(urlsplit(str(x.get("pagina") or "")).hostname or "").lower().removeprefix("www.") for x in ms if x.get("pagina")}
    hosts.discard("")
    locais = {"em": _agora(), "regra": __doc__.split("PILOTO - ESPIÃO")[0].strip(),
              "livros": len(ms), "livros_com_pagina": sum(1 for x in ms if x.get("pagina")), "dominios_distintos": len(hosts),
              "por_geografia": dict(Counter(str(x.get("geo") or "—") for x in ms).most_common()),
              "hoje": {"livros_criados_por_motor": dict(criado.most_common()), "livros_atualizados_por_motor": dict(atual.most_common())}}
    C["locais_de_busca"] = {k: locais[k] for k in ("em", "livros", "livros_com_pagina", "dominios_distintos")}
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    LOCAIS.write_text(json.dumps(locais, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"livros_atualizados": sum(atual.values()), "livros_criados_hoje": sum(criado.values()), "locais_de_busca": locais["livros"],
            "dominios": locais["dominios_distintos"]}


def registrar_achados_do_espiao(achados: list[dict]) -> dict:
    """Espião: achado que não está nos livros vira um livro novo na hora; o que já existe recebe a informação nova."""
    from .opressores_repositorio import chave, internacional
    from .livros_opressores import classificar
    C = _j(CAT, {}); ms = C.setdefault("motores", [])
    por_chave = {}
    for x in ms:
        por_chave.setdefault(chave(x.get("programa") or "", x.get("orgao") or ""), x)
        por_chave.setdefault(chave(x.get("programa") or ""), x)
    criados = atualizados = 0
    for a in achados or []:
        tit = str(a.get("titulo") or a.get("nome") or "").strip()
        url = str(a.get("url") or a.get("onde") or "")
        if len(tit) < 8 or not url.startswith("http"):
            continue
        k = chave(tit, a.get("orgao") or a.get("empresa") or "")
        x = por_chave.get(k) or por_chave.get(chave(tit))
        if x:
            if anotar_checklist(x, _checklist_de(a), "Piloto - Espião"):
                atualizados += 1
            continue
        lid = "op-" + hashlib.sha1(("espiao|" + k).encode()).hexdigest()[:12]
        x = {"id": lid, "programa": tit[:200], "orgao": a.get("orgao") or a.get("empresa") or "", "motor": "repositorio",
             "tipo": "repositorio_de_oportunidade", "familia": "Oportunidade com seleção", "uf": a.get("uf"), "pagina": url,
             "ativa": True, "validacao": "não lida ainda", "criado_em": date.today().isoformat(),
             "motivo_status": "livro criado pelo Piloto - Espião (oportunidade que não estava na Biblioteca)",
             "historico": [{"id": lid, "titulo": tit[:200], "fim": a.get("prazo") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a.get("prazo") or "")) else None,
                            "uf": a.get("uf"), "pagina_oficial": url, "origem": "Piloto - Espião", "visto_em": date.today().isoformat()}]}
        if internacional(x):
            x["internacional"] = True
        classificar(x); anotar_checklist(x, _checklist_de(a), "Piloto - Espião")
        ms.append(x); por_chave[k] = x; criados += 1
    if criados or atualizados:
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"livros_novos": criados, "livros_atualizados": atualizados}


if __name__ == "__main__":
    print(json.dumps(aplicar_motores(), ensure_ascii=False, indent=1))
