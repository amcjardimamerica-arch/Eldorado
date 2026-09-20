"""VARREDURA RETROATIVA — completa os dias em que o motor não leu.

Motores que aceitam consulta POR DATA (DOU por edição, PNCP por dataInicial/dataFinal)
podem voltar e ler os dias que ficaram sem execução no mês. Os demais (portais sem
arquivo por data) não têm como recuperar o passado — o calendário deles fica honesto:
"não executado". Para esses, a garantia é para a frente: a escala de 20/09 nunca mais
os corta.

Cada dia lido retroativamente entra em estado/esquadra_diario.json com a marca
"retroativo": true, para que o calendário do motor mostre que a lacuna foi coberta
depois, e não no dia.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

SUPORTAM_DATA = {"dou", "pncp-api"}          # têm {data}/{data8} na URL: leem a edição de qualquer dia


def dias_sem_leitura(sid: str, ano: int, mes: int, ate: date) -> list[date]:
    _d = load_json(ROOT / "estado/esquadra_diario.json") if (ROOT / "estado/esquadra_diario.json").exists() else {}
    hist = (_d.get("sensores") or _d).get(sid) or {}
    faltam = []
    d = date(ano, mes, 1)
    while d <= ate and d.month == mes:
        if d.isoformat() not in hist:
            faltam.append(d)
        d += timedelta(days=1)
    return faltam


def varrer(sid: str, dias: list[date], limite: int = 10) -> dict:
    """Lê o sensor 'sid' para cada dia da lista (até 'limite' dias por execução) e grava
    no histórico com a marca retroativa. Sem rede aqui, só roda no CI ou no Desktop."""
    from .sensores import registro, ler
    s = next((x for x in registro() if x["id"] == sid), None)
    if not s:
        return {"sensor": sid, "erro": "sensor não encontrado"}
    arq = ROOT / "estado/esquadra_diario.json"
    _d = load_json(arq) if arq.exists() else {"sensores": {}}
    sens = _d.setdefault("sensores", {})
    hist = sens.setdefault(sid, {})
    feitos = []
    for d in sorted(dias)[-limite:]:
        r = ler(s, data=d)
        ach = len(r.get("achados") or []); fal = len(r.get("falhas") or [])
        okh = any(x.get("http") in (200, 201) for x in (r.get("saude") or []))
        hist[d.isoformat()] = {"cor": "verde" if ach else ("vermelho" if (fal and not okh) else "azul"), "achados": ach, "falhas": fal,
                               "http": 200 if okh else None, "trecho": (r.get("achados") or [{}])[0].get("titulo") if ach else None,
                               "url": (r.get("achados") or [{}])[0].get("url") if ach else None,
                               "retroativo": True, "lido_em": now_iso()}
        feitos.append({"dia": d.isoformat(), "achados": ach, "falhas": fal})
    _d["atualizado_em"] = now_iso()
    write_json(arq, _d)
    return {"sensor": sid, "dias_lidos": feitos}


def run(limite_por_sensor: int = 10) -> dict:
    hoje = date.today()
    res = {"em": now_iso(), "mes": f"{hoje.year}-{hoje.month:02d}", "sensores": {}}
    for sid in sorted(SUPORTAM_DATA):
        faltam = dias_sem_leitura(sid, hoje.year, hoje.month, hoje - timedelta(days=1))
        res["sensores"][sid] = {"dias_faltantes": [d.isoformat() for d in faltam]}
        if faltam and (os.environ.get("GITHUB_ACTIONS") or os.environ.get("ELDORADO_LOCAL_BR")):
            res["sensores"][sid]["varredura"] = varrer(sid, faltam, limite_por_sensor)
        elif faltam:
            res["sensores"][sid]["nota"] = "sem rede nesta sessão — a varredura roda no CI ou no Desktop"
    outros = sorted(set(x["id"] for x in __import__("src.sensores", fromlist=["registro"]).registro() if not x.get("fontes_260")) - SUPORTAM_DATA)
    res["sem_arquivo_por_data"] = {"sensores": outros,
                                   "nota": "portais sem edição por data não permitem recuperar dias passados; a lacuna fica registrada como 'não executado' e a escala de 20/09 garante a leitura diária daqui para a frente"}
    write_json(ROOT / "estado/varredura_retroativa.json", res)
    return {"mes": res["mes"], "com_data": {k: len(v["dias_faltantes"]) for k, v in res["sensores"].items()}, "sem_arquivo_por_data": len(outros)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
