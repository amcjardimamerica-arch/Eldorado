"""ESQUADRILHA DO PILOTO — missões sorteadas, abates e diário de bordo.

O Piloto voa sobre os motores. A cada ciclo sorteia missões (caçar oportunidade nova,
afiar um motor, descobrir um local novo de publicação), executa uma por vez e registra
tudo num DIÁRIO DE BORDO que o painel lê para animar o avião e contar as estrelas.

ABATE = oportunidade NOVA na base, com objeto e onde procurar. É o que vira estrela ao
lado do motor onde foi encontrada — como os aviões de guerra marcavam no fuselagem.

Saídas:
  estado/sindico/bordo.json ....... missão atual, últimas missões, abates por motor
  docs/dados/esquadrilha.json ..... o mesmo, enxuto, para o painel
"""
from __future__ import annotations

import json
import random
import re
import time
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

BORDO = ROOT / "estado/sindico/bordo.json"
PUB = ROOT / "docs/dados/esquadrilha.json"
MISSOES = ("cacar_oportunidade", "afiar_motor", "descobrir_local")


def _cfg() -> dict:
    return (load_json(ROOT / "config/cargo_sindico.json") or {}).get("parametros", {})


def bordo() -> dict:
    return load_json(BORDO) if BORDO.exists() else {"missao_atual": None, "missoes": [], "abates": {}, "total_abates": 0, "iniciado_em": now_iso()}


def sortear(n: int | None = None, motores: list[str] | None = None) -> list[dict]:
    """Semente do dia + rodízio: o motor só repete quando todos tiverem sido visitados."""
    p = _cfg(); s = p.get("sorteio", {})
    lim = p.get("tarefas_por_ciclo", {"minimo": 4, "maximo": 12})
    n = n or random.Random(date.today().toordinal()).randint(lim["minimo"], lim["maximo"])
    b = bordo()
    visitados = {m["motor"] for m in b.get("missoes", [])[-40:] if m.get("motor")}
    if motores is None:
        # 22/09: o Síndico voa SÓ sobre os motores onde há oportunidade nova (26, 27, 28 e o 29).
        # Rouanet, diários e portais conhecidos releem o que já está mapeado — não são dele.
        motores = list((_cfg().get("motores_do_sindico") or {}).get("ids") or [])
        if not motores:
            from .sensores import registro
            motores = [x["id"] for x in registro() if not x.get("fontes_260")]
    fila = [m for m in motores if m not in visitados] or list(motores)
    rnd = random.Random(f"{date.today()}-{len(b.get('missoes', []))}")
    rnd.shuffle(fila)
    pesos = [s.get("cacar_oportunidade", .5), s.get("afiar_motor", .35), s.get("descobrir_local", .15)]
    saida = []
    for i in range(n):
        tipo = rnd.choices(MISSOES, weights=pesos)[0]
        saida.append({"tipo": tipo, "motor": fila[i % len(fila)] if fila else None, "ordem": i + 1})
    return saida


def abrir_missao(m: dict, alvo: str = "") -> dict:
    b = bordo()
    b["missao_atual"] = {**m, "alvo": alvo, "inicio": now_iso(), "estado": "em_voo"}
    write_json(BORDO, b); _publicar(b)
    return b["missao_atual"]


def fechar_missao(resultado: str, achados: list[dict] | None = None, licao: str = "") -> dict:
    """achados: [{titulo, onde, url, uf, novo: bool}] — os NOVOS viram estrela no motor."""
    b = bordo()
    m = b.get("missao_atual") or {}
    achados = achados or []
    novos = [a for a in achados if a.get("novo")]
    reg = {**m, "fim": now_iso(), "estado": "pousou", "resultado": resultado[:200],
           "achados": len(achados), "abates": len(novos), "licao": licao[:160],
           "alvos": [{"titulo": (a.get("titulo") or "")[:90], "onde": a.get("onde"), "url": a.get("url"), "uf": a.get("uf")} for a in achados[:6]]}
    b["missoes"] = ([reg] + b.get("missoes", []))[:60]
    if m.get("motor") and novos:
        e = b["abates"].setdefault(m["motor"], {"n": 0, "ultimos": []})
        e["n"] += len(novos)
        e["ultimos"] = ([{"titulo": (a.get("titulo") or "")[:80], "url": a.get("url"), "em": date.today().isoformat()} for a in novos] + e["ultimos"])[:8]
    b["total_abates"] = sum(v["n"] for v in b["abates"].values())
    b["missao_atual"] = None
    write_json(BORDO, b); _publicar(b)
    return reg


def _publicar(b: dict) -> None:
    PUB.write_text(json.dumps({
        "em": now_iso(),
        "missao_atual": b.get("missao_atual"),
        "ultimas": b.get("missoes", [])[:12],
        "abates": b.get("abates", {}),
        "total_abates": b.get("total_abates", 0),
        "legenda": {"cacar_oportunidade": "caçando oportunidade nova", "afiar_motor": "afiando o motor", "descobrir_local": "procurando um novo local de publicação"},
    }, ensure_ascii=False, indent=1), encoding="utf-8")


def resumo() -> dict:
    b = bordo()
    return {"total_abates": b.get("total_abates", 0), "motores_com_abate": len(b.get("abates", {})),
            "missoes_registradas": len(b.get("missoes", [])), "em_voo": bool(b.get("missao_atual"))}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sortear":
        print(json.dumps(sortear(), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(resumo(), ensure_ascii=False, indent=1))
