"""ALERTA DIÁRIO DOS MOTORES + VALIDAÇÃO DIA A DIA.

Duas perguntas que o painel tem de responder todo dia, sem exceção:

  1. Que motores NÃO funcionaram hoje (não leram, leram e falharam, ou estão além da
     cadência)?  →  estado/alerta_motores.json — a lista vira alerta no painel e vai
     para o pacote do Claude Desktop, que tenta complementar.

  2. Em cada dia do mês, cada motor LEU as rotas que devia? A pergunta de cobertura
     ("naquele dia, todas as oportunidades que poderiam existir foram procuradas nos
     lugares possíveis?") só se responde olhando o calendário motor a motor.
     →  estado/validacao_motores_mes.json — grade dia × motor, com o que faltou.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

CADENCIA_PADRAO = 1          # motores regulares: todo dia
CADENCIAS = {"semanal": 7, "mensal": 30}


def _cadencia(sid: str, rotas_cfg: dict) -> int:
    m = (rotas_cfg.get("motores") or {}).get(sid) or {}
    return CADENCIAS.get(m.get("cadencia"), CADENCIA_PADRAO)


def alerta_diario(hoje: date | None = None) -> dict:
    from .sensores import registro
    hoje = hoje or date.today()
    esq = load_json(ROOT / "estado/esquadra.json").get("sensores", {}) if (ROOT / "estado/esquadra.json").exists() else {}
    rotas = load_json(ROOT / "config/rotas_motores.json") if (ROOT / "config/rotas_motores.json").exists() else {}
    regulares = [s for s in registro() if not s.get("fontes_260")]
    alertas, ok = [], []
    for s in regulares:
        e = esq.get(s["id"]) or {}
        cad = _cadencia(s["id"], rotas)
        ult = (e.get("ultima") or "")[:10]
        if not ult:
            alertas.append({"id": s["id"], "nome": s["nome"], "gravidade": "alta", "problema": "nunca rodou",
                            "acao": "conferir se o sensor está na escala; se for novo, esperar a próxima saída"})
            continue
        dias = (hoje - date.fromisoformat(ult)).days
        saude = e.get("saude") or []
        falhou_tudo = bool(saude) and all(x.get("erro") for x in saude)
        aguarda_local = e.get("pulado_exige_brasil") or ("aguardando coleta local" in str((e.get("diagnostico") or {}).get("motivo_zero") or "") and not saude)
        if aguarda_local:
            alertas.append({"id": s["id"], "nome": s["nome"], "gravidade": "media", "problema": "aguardando coleta local (portal recusa IP estrangeiro)",
                            "acao": "rodar scripts/coleta_brasil.py no computador do titular — ou o Claude Desktop faz isso ao abrir"})
        elif falhou_tudo:
            alertas.append({"id": s["id"], "nome": s["nome"], "gravidade": "alta", "problema": f"todas as páginas falharam em {ult}",
                            "acao": "conferir bloqueio/mudança de formato; o Claude Desktop abre a rota no navegador"})
        elif dias > cad:
            alertas.append({"id": s["id"], "nome": s["nome"], "gravidade": "alta" if dias > 2 * cad else "media",
                            "problema": f"{dias} dia(s) sem leitura (cadência {cad})", "acao": "conferir escala e limite por execução"})
        else:
            ok.append(s["id"])
    alertas.sort(key=lambda a: (0 if a["gravidade"] == "alta" else 1, a["id"]))
    res = {"em": now_iso(), "data": hoje.isoformat(), "total": len(regulares), "funcionando": len(ok), "em_alerta": len(alertas),
           "alertas": alertas, "ok": ok,
           "regra": "todo motor regular tem de ler dentro da sua cadência; o que não leu vira alerta e vai para o pacote do Claude Desktop"}
    write_json(ROOT / "estado/alerta_motores.json", res)
    write_json(ROOT / "docs/dados/alerta_motores.json", res)
    return res


def validacao_mes(ano: int, mes: int, ate: date | None = None) -> dict:
    """Grade dia × motor: para cada dia do mês até 'ate', o motor leu? achou? falhou?
    Usa estado/esquadra_diario.json (histórico por dia) e a escala esperada."""
    from .sensores import registro
    _d = load_json(ROOT / "estado/esquadra_diario.json") if (ROOT / "estado/esquadra_diario.json").exists() else {}
    diario = _d.get("sensores") or _d          # {sensor: {AAAA-MM-DD: {cor, achados, falhas, http}}}
    rotas = load_json(ROOT / "config/rotas_motores.json") if (ROOT / "config/rotas_motores.json").exists() else {}
    regulares = [s for s in registro() if not s.get("fontes_260")]
    ate = ate or date.today()
    dias = []
    d = date(ano, mes, 1)
    while d <= ate and d.month == mes:
        dias.append(d); d += timedelta(days=1)
    grade = {}
    for s in regulares:
        cad = _cadencia(s["id"], rotas)
        hist = diario.get(s["id"]) or {}
        linha = []
        for dd in dias:
            k = dd.isoformat(); reg = hist.get(k) if isinstance(hist, dict) else None
            if reg is None:
                linha.append({"dia": k, "estado": "nao_exec"})
            elif isinstance(reg, dict):
                cor = reg.get("cor")
                if cor == "vermelho" or (reg.get("falhas") and not reg.get("http")):
                    linha.append({"dia": k, "estado": "falha", "falhas": reg.get("falhas")})
                elif (reg.get("achados") or 0) > 0 or cor == "verde":
                    linha.append({"dia": k, "estado": "encontrado", "achados": reg.get("achados")})
                else:
                    linha.append({"dia": k, "estado": "sem_oport"})
            else:
                linha.append({"dia": k, "estado": "sem_oport"})
        exec_ = sum(1 for x in linha if x["estado"] != "nao_exec")
        esperado = len(dias) if cad == 1 else max(1, len(dias) // cad)
        grade[s["id"]] = {"nome": s["nome"], "cadencia": cad, "dias_executados": exec_, "dias_esperados": esperado,
                          "cobertura": round(min(1.0, exec_ / esperado), 2) if esperado else None,
                          "encontrados": sum(1 for x in linha if x["estado"] == "encontrado"),
                          "falhas": sum(1 for x in linha if x["estado"] == "falha"),
                          "veredito": ("íntegro" if exec_ >= esperado else "lacunas" if exec_ > 0 else "não executou"),
                          "dias": linha}
    res = {"em": now_iso(), "mes": f"{ano}-{mes:02d}", "ate": ate.isoformat(), "dias_no_periodo": len(dias),
           "motores": grade,
           "resumo": {"integros": sum(1 for g in grade.values() if g["veredito"] == "íntegro"),
                      "com_lacunas": sum(1 for g in grade.values() if g["veredito"] == "lacunas"),
                      "nao_executaram": sum(1 for g in grade.values() if g["veredito"] == "não executou")},
           "pergunta": "em cada dia, todas as oportunidades que poderiam existir foram procuradas nos lugares possíveis? Um motor com lacunas é um dia em que uma rota não foi olhada."}
    write_json(ROOT / "estado/validacao_motores_mes.json", res)
    write_json(ROOT / "docs/dados/validacao_motores_mes.json", res)
    return res


def run() -> dict:
    hoje = date.today()
    a = alerta_diario(hoje)
    v = validacao_mes(hoje.year, hoje.month, hoje)
    return {"alerta": {k: a[k] for k in ("data", "total", "funcionando", "em_alerta")},
            "validacao_mes": v["resumo"]}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
