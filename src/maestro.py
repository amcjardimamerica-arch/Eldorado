"""MAESTRO — A REDE NEURAL CONDUZ O DIA (titular, 02/10/2026).

Os motores são ferramentas de uma etapa. O maestro, a cada passagem do fluxo de status (4 vezes por dia):
  1. PLANEJA  quais motores rodam hoje (agenda) e em que ordem: rendimento real do canal (oportunidades validadas como
              reais por leitura — linha de produção), diagnóstico (planos de correção) e livros com abertura próxima
              no índice do motor (léxico temporário da chave de acionamento);
  2. MEDE     a cobertura do dia de cada motor: completa (leu sem falha de página) · parcial (falha em parte das páginas)
              · pendente (ainda não leu) · pendente_local (exige IP brasileiro — coleta no computador do titular);
  3. CONTROLA dispara de novo os pendentes e os parciais, até 3 vezes por dia, para a busca do dia NÃO ficar parcial;
  4. FECHA    o dia quando todos os motores planejados estão completos (ou esgotaram as tentativas — fica registrado).
Saída: docs/dados/maestro.json · estado: estado/maestro/AAAA-MM-DD.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/maestro.json"
DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def hoje_brt():
    return datetime.now(timezone(timedelta(hours=-3))).date()


def roda_hoje(ag: dict, dia) -> bool:
    d = str((ag or {}).get("dias") or "todos").lower()
    if d.startswith("inativ"):
        return False
    return d == "todos" or DIAS[dia.weekday()] in d or (d == "uteis" and dia.weekday() < 5)


def cobertura(sid: str, reg: dict | None, diag: dict | None) -> str:
    if not reg:
        return "pendente_local" if "exige" in json.dumps(diag or {}, ensure_ascii=False).lower() else "pendente"
    if reg.get("cor") in ("vermelho",) or int(reg.get("falhas") or 0) > 0:
        return "parcial"
    if reg.get("cor") in ("cinza", "futuro", "fora"):
        return "pendente"
    return "completa"


def planejar(dia=None) -> list[dict]:
    dia = dia or hoje_brt()
    try:
        from .sensores import registro
        ativos = [s["id"] for s in registro()]
    except Exception:  # noqa: BLE001
        ativos = []
    A = (_j(ROOT / "config/agenda_motores.json", {}) or {}).get("motores", {})
    canais = {c["canal"]: c for c in (_j(ROOT / "docs/dados/linha_producao.json", {}) or {}).get("canais", [])}
    planos = {m["motor"]: m for m in (_j(ROOT / "docs/dados/planos_correcao.json", {}) or {}).get("motores", [])}
    E = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("sensores", {})
    lex = (_j(ROOT / "estado/lexico_temporario_livros.json", {}) or {}).get("itens", [])
    from .linha_producao import canal_canonico
    plano = []
    for sid in ativos:
        ag = A.get(sid) or A.get(sid.replace("plat-", "")) or {}
        if not roda_hoje(ag, dia):
            continue
        c = canais.get(canal_canonico(sid)) or {}
        leituras = int((E.get(sid) or {}).get("leituras") or 0)
        rend = (int(c.get("validadas_como_reais") or 0) + 0.5) / (leituras + 5)        # oportunidades reais por leitura
        diag = (planos.get(sid) or {}).get("diagnostico", "saudavel")
        livros_proximos = sum(1 for it in lex if sid in (it.get("motores") or []))
        prioridade = round(rend * (0.5 if diag in ("sem_rendimento", "falha_parcial") else 1.0) + 0.02 * livros_proximos, 4)
        plano.append({"motor": sid, "prioridade": prioridade, "diagnostico": diag, "livros_com_abertura_proxima": livros_proximos,
                      "horarios": ag.get("horarios_brt"), "coleta": ag.get("coleta") or "nuvem"})
    return sorted(plano, key=lambda p: -p["prioridade"])


def controlar(disparar: bool = False, dia=None) -> dict:
    dia = dia or hoje_brt(); d0 = dia.isoformat()
    cfg = (_j(ROOT / "config/esteira.json", {}) or {}).get("maestro", {}); limite = int(cfg.get("tentativas_por_dia", 3))
    est_p = ROOT / f"estado/maestro/{d0}.json"; est = _j(est_p, {"tentativas": {}})
    D = (_j(ROOT / "estado/esquadra_diario.json", {}) or {}).get("sensores", {})
    S = {m.get("id"): m for m in (_j(ROOT / "docs/dados/status_motores.json", {}) or {}).get("motores", [])}
    plano = planejar(dia)
    try:   # o que a agenda JÁ esperava ter lido (respeita horário e cadência de cada motor)
        sp = importlib.util.spec_from_file_location("ag", ROOT / "scripts/agenda_motores.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        atrasados = set(m.recuperar())
    except Exception:  # noqa: BLE001
        atrasados = set()
    for p in plano:
        c = cobertura(p["motor"], (D.get(p["motor"]) or {}).get(d0), S.get(p["motor"]) or S.get(p["motor"].replace("plat-", "")))
        if c == "pendente" and p["motor"] not in atrasados:
            c = "aguardando_horario"                 # ainda não chegou a hora (ou a cadência) — não se dispara
        p["cobertura"] = c
        p["tentativas_hoje"] = int(est["tentativas"].get(p["motor"]) or 0)
    a_disparar = [p["motor"] for p in plano if p["cobertura"] in ("pendente", "parcial") and p["tentativas_hoje"] < limite and p["coleta"] != "local"]
    a_disparar += [x for x in atrasados if x not in a_disparar and int(est["tentativas"].get(x) or 0) < limite]
    if disparar:
        for x in a_disparar:
            est["tentativas"][x] = int(est["tentativas"].get(x) or 0) + 1
    from collections import Counter
    cont = Counter(p["cobertura"] for p in plano)
    completos = cont.get("completa", 0)
    esgotados = [p["motor"] for p in plano if p["cobertura"] in ("pendente", "parcial") and p["tentativas_hoje"] >= limite]
    fechado = all(p["cobertura"] == "completa" or p["motor"] in esgotados or p["cobertura"] == "pendente_local" for p in plano)
    completos_ou_esperando = completos + cont.get("aguardando_horario", 0)
    out = {"dia": d0, "em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Saída")[0].strip(),
           "planejados": len(plano), "cobertura": dict(cont), "cobertura_percentual": round(100 * completos / max(1, len(plano) - cont.get("aguardando_horario", 0)), 1),
           "a_disparar": a_disparar, "esgotaram_tentativas": esgotados, "dia_fechado": fechado, "plano": plano}
    est_p.parent.mkdir(parents=True, exist_ok=True)
    est.update({"ultima": out["em"], "cobertura": dict(cont), "dia_fechado": fechado}); est_p.write_text(json.dumps(est, ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = controlar(disparar="--disparar" in sys.argv)
    if "--ids" in sys.argv or "--disparar" in sys.argv:
        print(",".join(o["a_disparar"]))
    else:
        print(json.dumps({k: o[k] for k in ("dia", "planejados", "cobertura", "cobertura_percentual", "a_disparar", "dia_fechado")}, ensure_ascii=False, indent=1))
