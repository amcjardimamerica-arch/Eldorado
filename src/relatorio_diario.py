"""Relatório de funcionamento — um por dia, um registro por bloco.

Cada saída dos motores (00h diários, 01h justiça/legislativo, 02h plataformas/
API, 03h completude, 04h Opressores, 05h busca ativa, 06h relatório) grava o
que fez: sensores executados, achados, novos na base, falhas, bloqueios e
tempo. O painel mostra o dia consolidado na caixa Motores de Busca e o
histórico dos últimos 30 dias — é o "relatório de funcionamento automatizado".
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta

from .nucleo import ROOT, load_json, now_iso, write_json

PASTA = ROOT / "estado/relatorios"


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / f"{hoje.isoformat()}.json"
    rel = load_json(arq) if arq.exists() else {"data": hoje.isoformat(), "blocos": {}}
    bloco = os.environ.get("MOTORES_BLOCO", "completo")
    esq = load_json(ROOT / "estado/esquadra.json") if (ROOT / "estado/esquadra.json").exists() else {}
    u = esq.get("ultima_execucao") or {}
    blq = load_json(ROOT / "estado/bloqueios.json") if (ROOT / "estado/bloqueios.json").exists() else {}
    pert = load_json(ROOT / "estado/pertinencia.json") if (ROOT / "estado/pertinencia.json").exists() else {}
    ba = load_json(ROOT / "estado/busca_ativa.json") if (ROOT / "estado/busca_ativa.json").exists() else {}
    ed = None
    try:
        from .banco import conectar
        con = conectar()
        ed = con.execute("SELECT COUNT(*), SUM(ok) FROM edicoes").fetchone()
        con.close()
    except Exception:
        pass
    registro = {
        "em": now_iso(), "bloco": bloco,
        "sensores_executados": u.get("sensores_executados") if u.get("data") == hoje.isoformat() else 0,
        "achados": u.get("achados") if u.get("data") == hoje.isoformat() else 0,
        "novos_na_base": u.get("novos_na_base") if u.get("data") == hoje.isoformat() else 0,
        "por_tipo": u.get("por_tipo") if u.get("data") == hoje.isoformat() else {},
        "dominios_bloqueados": len(blq.get("dominios", {})),
        "descartados_por_pertinencia": pert.get("descartados"),
        "busca_ativa_em_acompanhamento": len(ba.get("itens", {})),
        "edicoes_extraidas": {"total": ed[0], "com_ato": ed[1]} if ed else None,
        "teste_ci": (open(ROOT / "estado/ultimo_teste_ci.txt", encoding="utf-8").read().split("\n")[2]
                     if (ROOT / "estado/ultimo_teste_ci.txt").exists() else None),
    }
    rel["blocos"][bloco] = registro
    rel["consolidado"] = {
        "blocos_executados": sorted(rel["blocos"]),
        "sensores": sum(b.get("sensores_executados") or 0 for b in rel["blocos"].values()),
        "achados": sum(b.get("achados") or 0 for b in rel["blocos"].values()),
        "novos_na_base": sum(b.get("novos_na_base") or 0 for b in rel["blocos"].values()),
        "atualizado_em": now_iso(),
    }
    write_json(arq, rel)
    # índice dos últimos 30 dias, leve, para o painel
    corte = (hoje - timedelta(days=30)).isoformat()
    dias = []
    for f in sorted(PASTA.glob("*.json")):
        if f.stem < corte or f.stem == "indice":
            continue
        r = load_json(f)
        dias.append({"data": r["data"], **(r.get("consolidado") or {}),
                     "blocos": list((r.get("blocos") or {}).keys())})
    write_json(PASTA / "indice.json", {"gerado_em": now_iso(), "dias": dias[-31:]})
    return {"data": hoje.isoformat(), "bloco": bloco, "consolidado": rel["consolidado"]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
