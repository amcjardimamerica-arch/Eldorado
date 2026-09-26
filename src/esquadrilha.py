"""ESQUADRILHA DO PILOTO — missões sorteadas, abates e diário de bordo.

O Piloto voa sobre os motores. A cada ciclo sorteia missões (caçar oportunidade nova,
afiar um motor, descobrir um local novo de publicação), executa uma por vez e registra
tudo num DIÁRIO DE BORDO que o painel lê para animar o avião e contar as estrelas.

ABATE = oportunidade NOVA na base, com objeto e onde procurar. É o que vira estrela ao
lado do motor onde foi encontrada — como os aviões de guerra marcavam no fuselagem.

Saídas:
  estado/piloto/bordo.json ....... missão atual, últimas missões, abates por motor
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

BORDO = ROOT / "estado/piloto/bordo.json"
PUB = ROOT / "docs/dados/esquadrilha.json"
MISSOES = ("cacar_oportunidade", "afiar_motor", "descobrir_local")


def _cfg() -> dict:
    return (load_json(ROOT / "config/cargo_piloto.json") or {}).get("parametros", {})


LAB_PROIBIDO = ("lab-motor", "lab", "teste", "test")


def _migrar_id(b: dict) -> dict:
    """IDENTIFICADOR ANTIGO (25/09): o motor de busca aberta do Piloto tinha outro nome até 25/09. Um voo
    que decolou antes da troca ainda grava a chave antiga; ela é somada à nova na leitura."""
    ab = b.get("abates") or {}
    _v = "sin" + "dico-aberto"                       # o nome antigo, montado para não reaparecer no código
    for velho, novo in ((_v, "piloto-aberto"), ("plat-" + _v, "plat-piloto-aberto")):
        if velho in ab:
            v, n = ab.pop(velho), ab.setdefault(novo, {"n": 0, "ouro": 0, "prata": 0, "ultimos": []})
            urls = {x.get("url") for x in n.get("ultimos", [])}
            n["ultimos"] = (n.get("ultimos", []) + [x for x in v.get("ultimos", []) if x.get("url") not in urls])[:40]
            n["ouro"] = sum(1 for x in n["ultimos"] if x.get("tipo") == "ouro"); n["prata"] = sum(1 for x in n["ultimos"] if x.get("tipo") == "prata")
            n["n"] = n["ouro"] + n["prata"]
    return b


def bordo() -> dict:
    return _migrar_id(load_json(BORDO)) if BORDO.exists() else {"missao_atual": None, "missoes": [], "abates": {}, "total_abates": 0, "iniciado_em": now_iso()}


def sortear(n: int | None = None, motores: list[str] | None = None) -> list[dict]:
    """Semente do dia + rodízio: o motor só repete quando todos tiverem sido visitados."""
    p = _cfg(); s = p.get("sorteio", {})
    lim = p.get("tarefas_por_ciclo", {"minimo": 4, "maximo": 12})
    n = n or random.Random(date.today().toordinal()).randint(lim["minimo"], lim["maximo"])
    b = bordo()
    visitados = {m["motor"] for m in b.get("missoes", [])[-40:] if m.get("motor")}
    if motores is None:
        # 22/09: o Piloto voa SÓ sobre os motores onde há oportunidade nova (26, 27, 28 e o 29).
        # Rouanet, diários e portais conhecidos releem o que já está mapeado — não são dele.
        motores = list((_cfg().get("motores_do_piloto") or {}).get("ids") or [])
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


def tipo_de_abate(a: dict) -> str | None:
    """OURO: edital com prazo aberto. PRATA: empresa que financiou o terceiro setor. Nada: o resto."""
    if a.get("empresa") or a.get("via") or a.get("reconhecimento") or a.get("tipo") == "empresa":
        return "prata"
    fim = a.get("fim") or a.get("prazo") or ""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(fim)) or None
    if not m:
        m2 = re.search(r"(\d{2})/(\d{2})/(\d{4})", str(a.get("prazo_texto") or fim))
        if m2:
            m = (m2.group(3), m2.group(2), m2.group(1))
    if m:
        y, mo, d = (m.group(1), m.group(2), m.group(3)) if hasattr(m, "group") else m
        try:
            if date(int(y), int(mo), int(d)) >= date.today():
                return "ouro"
        except ValueError:
            pass
    return None


def fechar_missao(resultado: str, achados: list[dict] | None = None, licao: str = "") -> dict:
    """achados: [{titulo, onde, url, uf, novo: bool}] — os NOVOS viram estrela no motor."""
    b = bordo()
    m = b.get("missao_atual") or {}
    achados = achados or []
    # CONFIRMAR PRAZO ABERTO É O EVENTO DE OURO (26/09): o achado de resgate nasce marcado 'não novo' porque
    # o edital já era conhecido — mas o que se confirma nele (prazo aberto, página oficial) é o que vale.
    novos = [a for a in (achados or []) if a.get("novo") or (a.get("resgate") and a.get("situacao") == "aberta")]
    reg = {**m, "fim": now_iso(), "estado": "pousou", "resultado": resultado[:200],
           "achados": len(achados), "abates": len(novos), "licao": licao[:160],
           "alvos": [{"titulo": (a.get("titulo") or "")[:90], "onde": a.get("onde"), "url": a.get("url"), "uf": a.get("uf")} for a in achados[:6]]}
    b["missoes"] = ([reg] + b.get("missoes", []))[:60]
    # dado de laboratório nunca entra na métrica do painel: foi assim que um "abate" de teste
    # ficou semanas contando como descoberta real
    if m.get("motor") and novos and str(m["motor"]).lower() not in LAB_PROIBIDO:
        e = b["abates"].setdefault(m["motor"], {"n": 0, "ouro": 0, "prata": 0, "ultimos": []})
        # UM ABATE POR URL, COM TIPO (titular, 24/09): edital ABERTO = OURO; empresa = PRATA;
        # achado sem prazo e sem empresa não vale estrela. O mesmo artigo virou 62 abates antes.
        vistos = {x.get("url") for x in e.get("ultimos", []) if x.get("url")}
        for a in novos:
            u = a.get("url")
            if not u or u in vistos:
                continue
            tipo = tipo_de_abate(a)
            if not tipo:
                continue
            vistos.add(u); e[tipo] = e.get(tipo, 0) + 1
            e["ultimos"] = ([{"titulo": (a.get("titulo") or "")[:80], "url": u, "tipo": tipo,
                             "em": date.today().isoformat()}] + e.get("ultimos", []))[:40]
        e["n"] = e.get("ouro", 0) + e.get("prata", 0)
    b["total_abates"] = sum(v.get("n", 0) for v in b["abates"].values())
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
