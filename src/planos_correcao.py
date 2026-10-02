"""PLANOS DE CORREÇÃO DOS CANAIS (titular, 02/10/2026).

Cada motor e Piloto é diagnosticado a cada ciclo pelo seu histórico (estado/esquadra*.json, status dos motores, bloqueios)
e recebe o plano previsto no fluxograma (config/linha_producao.json › planos_de_correcao):
  sem_rendimento · falha_parcial · bloqueio · exige_brasil · formato_mudou · (contrato_violado e injecao: por registro)
O plano nunca desliga um canal sozinho: ele diz o que fazer e qual skill usar. Saída: docs/dados/planos_correcao.json
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/planos_correcao.json"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def diagnosticar(sid: str, s: dict, dias: dict, status: dict, hoje: date, finalidade: str = "descoberta") -> tuple[str | None, str]:
    ult = sorted(dias)[-14:]
    falhas_7 = sum(1 for d in ult[-7:] if (dias[d].get("falhas") or 0) > 0 or dias[d].get("cor") == "vermelho")
    ach_antes = sum(dias[d].get("achados") or 0 for d in ult[:-2]); ach_agora = sum(dias[d].get("achados") or 0 for d in ult[-2:])
    txt = json.dumps(status, ensure_ascii=False).lower()
    if "exige" in txt and "brasil" in txt:
        return "exige_brasil", "o site recusa o IP da nuvem"
    if any(x in txt for x in ("403", "429", "waf", "bloque")):
        return "bloqueio", "respostas de bloqueio no status"
    if finalidade == "descoberta" and (s.get("leituras") or 0) >= 5 and not s.get("achados_total"):   # insumo não é cobrado por achado
        return "sem_rendimento", f"{s.get('leituras')} leituras e nenhum achado"
    if len(ult) >= 9 and ach_antes > 0 and ach_agora == 0 and dias[ult[-1]].get("cor") in ("vermelho", "cinza"):
        return "formato_mudou", f"{ach_antes} achado(s) nos dias anteriores e nenhum nos 2 últimos"
    if falhas_7 >= 3:
        return "falha_parcial", f"falhas em {falhas_7} dos últimos 7 dias"
    return None, "saudável"


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    cfg = _j(ROOT / "config/linha_producao.json", {}); planos = cfg.get("planos_de_correcao") or {}
    E = (_j(ROOT / "estado/esquadra.json", {}) or {}).get("sensores", {}); D = (_j(ROOT / "estado/esquadra_diario.json", {}) or {}).get("sensores", {})
    S = {m.get("id"): m for m in (_j(ROOT / "docs/dados/status_motores.json", {}) or {}).get("motores", [])}
    try:
        from .sensores import registro
        ativos = {s["id"] for s in registro()}
    except Exception:  # noqa: BLE001
        ativos = set(E)
    from .linha_producao import canal_canonico, familia
    FIN = (_j(ROOT / "config/finalidade_motores.json", {}) or {}).get("motores", {})
    out = []
    for sid in sorted(ativos | {k for k in E if k.startswith("piloto")}):
        st = S.get(sid) or S.get(sid.replace("plat-", "")) or {}
        fin = (FIN.get(sid) or FIN.get(sid.replace("plat-", "")) or {}).get("finalidade") or "descoberta"
        classe, evid = diagnosticar(sid, E.get(sid) or {}, D.get(sid) or {}, st, hoje, fin)
        p = planos.get(classe) or {}
        out.append({"motor": sid, "canal": canal_canonico(sid), "familia": familia(canal_canonico(sid)), "diagnostico": classe or "saudavel",
                    "evidencia": evid, "plano": p.get("plano") or [], "skill": p.get("skill"),
                    "leituras": (E.get(sid) or {}).get("leituras"), "achados_total": (E.get(sid) or {}).get("achados_total")})
    out.sort(key=lambda z: (z["diagnostico"] == "saudavel", z["diagnostico"], z["motor"]))
    rel = {"em": hoje.isoformat(), "regra": __doc__.split("Saída")[0].strip(), "resumo": dict(Counter(z["diagnostico"] for z in out)), "motores": out}
    SAIDA.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    return rel["resumo"]


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
