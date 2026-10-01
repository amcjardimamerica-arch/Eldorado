"""Os 12 parâmetros de cada Livro de oportunidade, pesquisados na fonte oficial (29/09/2026).

Regra do titular: cada opressor ligado persegue os 12 parâmetros do edital do seu recurso — Objeto, Prazo de
inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos,
Destinação e Área de atuação. Quando o recurso não tem algum deles (programa permanente, fluxo contínuo, doação,
destinação de imposto, TAC, emenda), fica registrada a DISPENSA e o porquê.

A pesquisa é feita por blocos e gravada em `dados/opressores/parametros/parametros_AAAA-MM-DD.json` (um registro
por opressor; o arquivo mais recente prevalece). Este módulo leva esses dados para:

- `estado/opressores.json` → `ligados[id].itens` (texto que a rotina dos disjuntores já entende: o item preenchido
  não é mais perguntado à IA) e `ligados[id].parametros` (os 12 com status, a edição de referência e a fonte);
- o histórico dos desligados (`historico[].parametros`), para a edição encerrada alimentar a previsão;
- o catálogo (`parametros` em cada motor), chamado por `src.motores` antes de gravar.

Decisões: V = edital vigente aberto · A = última edição encerrada (histórico) · R = programa permanente sem edital
periódico · D = não é recurso para OSC (o opressor é desligado e não volta a ser ligado automaticamente) ·
P = pendente, com o motivo. Nada é inventado: dado sem fonte oficial fica null com o status "não localizado".
Aplicação idempotente: rodar duas vezes não muda nada.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .nucleo import ROOT

PASTA = ROOT / "dados/opressores/parametros"
EST = ROOT / "estado/opressores.json"
ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
         "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")
STATUS = ("confirmado", "dispensado pelo edital", "não informado no edital", "não localizado")
DECISOES = {"V": "edital vigente aberto", "A": "última edição encerrada (histórico)", "R": "programa permanente sem edital periódico",
            "D": "não é recurso para OSC — opressor desligado", "P": "pendente"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def carregar() -> dict[str, dict]:
    """Registro por opressor; arquivos lidos em ordem alfabética — o mais recente prevalece."""
    out: dict[str, dict] = {}
    for arq in sorted(PASTA.glob("parametros_*.json")) if PASTA.exists() else []:
        d = _j(arq, {})
        for r in d.get("itens") or []:
            if r.get("id") and r.get("decisao") in DECISOES:
                out[r["id"]] = {**r, "verificado_em": r.get("verificado_em") or d.get("data")}
    _reg = out
    # 30/09: a curadoria dos livros pode ter juntado/renomeado o opressor pesquisado — segue o mapa de identificadores
    _m = dict((_j(PASTA / "mapa_ids_2026-09-30.json", {}) or {}).get("mapa") or {})
    try:                                       # 01/10: livro juntado a outro na conferência — a pesquisa segue para o que ficou
        for _x in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}) or {}).get("motores") or []:
            for _i in _x.get("ids_juntados") or []:
                _m.setdefault(_i, _x["id"])
    except Exception:
        pass
    for _a, _n in _m.items():
        if _a in _reg and _n not in _reg:
            _reg[_n] = {**_reg[_a], "id": _n, "id_pesquisado": _a}
    return _reg


def dispensados() -> set[str]:
    """Opressores que a pesquisa mostrou não serem recurso: não voltam a ser ligados automaticamente."""
    return {k for k, r in carregar().items() if r["decisao"] == "D"}


def texto_item(v: dict | None) -> str | None:
    """Converte {valor, status} no texto gravado em ligados[id].itens. 'não localizado' fica vazio (a busca continua)."""
    if not isinstance(v, dict):
        return None
    st, val = v.get("status"), (str(v.get("valor")).strip() if v.get("valor") not in (None, "") else None)
    if st == "confirmado" and val:
        return val
    if st == "dispensado pelo edital":
        return "dispensado pelo edital" + (f": {val}" if val else "")
    if st == "não informado no edital":
        return "não informado no edital" + (f": {val}" if val else "")
    return None


def resumo(r: dict) -> dict:
    dz = r.get("dados") or {}
    doze = {k: {"valor": (dz.get(k) or {}).get("valor"), "status": (dz.get(k) or {}).get("status") or "não localizado"} for k in ITENS} \
        if r["decisao"] in ("V", "A", "R") else None
    fechados = sum(1 for v in (doze or {}).values() if v["status"] != "não localizado")
    return {"decisao": r["decisao"], "significado": DECISOES[r["decisao"]], "verificado_em": r.get("verificado_em"),
            "motivo": r.get("motivo"), "edital": r.get("edital_referencia"), "fonte_oficial": r.get("fonte_oficial"),
            "origem_fonte": r.get("origem_fonte"), "inicio": r.get("inicio"), "prazo": r.get("prazo"),
            "pagina_oficial_verificada": r.get("pagina_monitorar"), "recomendacao": r.get("motor_recomendacao"),
            "fora_abrangencia": bool(r.get("fora_abrangencia")), "fechados": fechados, "doze": doze}


def _catalogo() -> dict[str, dict]:
    return {m.get("id"): m for m in (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}) or {}).get("motores", [])}


def _resumo_com_dispensa(r: dict, mo: dict | None) -> dict:
    """resumo() + a análise de dispensa provável dos itens 'não localizado' (src/dispensas_itens.py, 01/10/2026)."""
    from . import dispensas_itens as DI
    rs = resumo(r)
    DI.no_livro(rs, mo, str((r.get("edital_referencia") or {}).get("titulo") or ""), str((mo or {}).get("programa") or ""))
    return rs


def aplicar(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    P = carregar(); CAT = _catalogo()
    est = _j(EST, {"ligados": {}})
    est.setdefault("ligados", {}); est.setdefault("historico", [])
    res = {"registros": len(P), "itens_gravados": 0, "opressores_atualizados": 0, "desligados": 0, "historico_anotado": 0}
    mudou = False
    for oid in list(est["ligados"]):
        r = P.get(oid)
        if not r:
            # livro com 12 itens vindos de outra verificação (validação individual): só ganha a análise de dispensa provável
            par = (est["ligados"][oid] or {}).get("parametros")
            if isinstance(par, dict) and par.get("doze"):
                antes = json.dumps(par, sort_keys=True, ensure_ascii=False)
                from . import dispensas_itens as DI
                DI.no_livro(par, CAT.get(oid), str((par.get("edital") or {}).get("titulo") or ""), str((CAT.get(oid) or {}).get("programa") or ""))
                if json.dumps(par, sort_keys=True, ensure_ascii=False) != antes:
                    res["opressores_atualizados"] += 1; mudou = True
            continue
        reg = est["ligados"][oid]
        if r["decisao"] == "D":
            est["historico"].append({**reg, "id": oid, "desligado_em": hoje.isoformat(),
                                     "motivo": f"parâmetros {r.get('verificado_em')}: {r.get('motivo')}", "parametros": _resumo_com_dispensa(r, CAT.get(oid))})
            est["ligados"].pop(oid)
            res["desligados"] += 1; mudou = True
            continue
        alterou = False
        itens = reg.setdefault("itens", {})
        for k in ITENS:
            t = texto_item((r.get("dados") or {}).get(k))
            if t and itens.get(k) != t:
                itens[k] = t; res["itens_gravados"] += 1; alterou = True
        rs = _resumo_com_dispensa(r, CAT.get(oid))
        if reg.get("parametros") != rs:
            reg["parametros"] = rs; alterou = True
        if r.get("fonte_oficial") and r["decisao"] in ("V", "A", "R") and reg.get("url_edital") != ((r.get("edital_referencia") or {}).get("url") or r["fonte_oficial"]):
            reg["url_edital"] = (r.get("edital_referencia") or {}).get("url") or r["fonte_oficial"]; alterou = True
        if alterou:
            res["opressores_atualizados"] += 1; mudou = True
    for h in est["historico"]:
        r = P.get(h.get("id"))
        if r and h.get("id") not in est["ligados"] and h.get("parametros") != _resumo_com_dispensa(r, CAT.get(h.get("id"))):
            h["parametros"] = _resumo_com_dispensa(r, CAT.get(h.get("id"))); res["historico_anotado"] += 1; mudou = True
    est["historico"] = est["historico"][-400:]
    if mudou:
        EST.write_text(json.dumps(est, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def no_catalogo(motores: list[dict]) -> int:
    """Anota os 12 parâmetros em cada motor do catálogo (chamado por src.motores antes de gravar)."""
    P = carregar(); n = 0
    for m in motores:
        r = P.get(m.get("id"))
        if r:
            m["parametros"] = _resumo_com_dispensa(r, m); n += 1
    return n


def run() -> dict:
    return aplicar()


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
