"""STATUS DOS MOTORES A CADA 6 HORAS (titular, 01/10/2026) — monitoramento e tomada de decisão.

Para cada motor regular: a data e a hora da ÚLTIMA LEITURA, o resultado e UMA de três luzes:
  VERDE     coletou hoje (horário de Brasília), com dados ou sem dados novos
  VERMELHO  a coleta de hoje teve erro ou falha
  CINZA     o motor não rodou hoje (fora da agenda, aguardando coleta local, parado)
Não existe outra cor. Recalculado a cada 6 horas pelo fluxo .github/workflows/status-motores.yml, que antes dispara
os motores cuja leitura do dia ficou pendente. Saída: docs/dados/status_motores.json
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOTORES = ROOT / "docs/dados/motores.json"
SAIDA = ROOT / "docs/dados/status_motores.json"
BRT = timezone(timedelta(hours=-3))
CADA_HORAS = 6
# o calendário de cada motor também fica com as três cores
TRES_CORES = {"verde": "verde", "azul": "verde", "amarelo": "verde", "vermelho": "vermelho", "cinza": "cinza", "fora": "cinza"}
PROPRIOS = {"do-goiania": ROOT / "estado/diario_goiania.json", "do-goias": ROOT / "estado/diario_goias.json"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _brt(iso) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(BRT)
    except Exception:
        return None


def status_de(p: dict, hoje: str) -> dict:
    """A luz de um motor a partir do painel (e do registro próprio, nos motores 01 e 02)."""
    ult = _brt(p.get("ultima_leitura"))
    dia = next((d for d in (p.get("dias") or []) if d.get("d") == hoje), {}) or {}
    cor_dia = TRES_CORES.get(dia.get("cor"), "cinza")
    falha = ""
    # registro diário do motor (estado/esquadra_diario.json): quantas páginas falharam hoje
    reg = (_DIARIO.get(p.get("id")) or _DIARIO.get("plat-" + str(p.get("id"))) or {}).get(hoje) or {}
    if reg:
        nf = int(reg.get("falhas") or 0)
        if reg.get("cor") == "vermelho":
            cor_dia, falha = "vermelho", "nenhuma página leu" + (f" (HTTP {reg.get('http')})" if reg.get("http") else "")
        elif nf:
            cor_dia, falha = "vermelho", f"{nf} página(s) com falha; as demais foram lidas"
        elif cor_dia == "cinza":
            cor_dia = "verde"
        dia = {"n": reg.get("achados") or 0, "t": reg.get("trecho")}
    proprio = PROPRIOS.get(p.get("id"))
    if proprio and proprio.exists():                 # motores 01 e 02: registro por fonte
        u = _j(proprio, {}).get("ultima") or {}
        up = _brt(u.get("em"))
        if up and (not ult or up > ult):
            ult = up
        if up and up.date().isoformat() == hoje:
            fontes = u.get("fonte_do_dia") or {}
            if fontes and all(v != "leu" for v in fontes.values()):
                cor_dia, falha = "vermelho", "nenhuma fonte leu: " + ", ".join(f"{k} {v}" for k, v in fontes.items())
            else:
                cor_dia = "verde"
                vd = u.get("vereditos") or {}
                dia = {"n": vd.get("OPORTUNIDADE") or 0, "t": f"{sum(v for k, v in vd.items() if isinstance(v, int))} ato(s) lido(s)"}
                falhas = [k for k, v in fontes.items() if v == "falhou"]
                if falhas:
                    falha = "fonte(s) com falha: " + ", ".join(falhas)
    leu_hoje = bool(ult and ult.date().isoformat() == hoje)
    if cor_dia == "vermelho":
        luz = "vermelho"
        resultado = "falha na coleta de hoje" + (f" — {falha}" if falha else "")
        if int(dia.get("n") or 0):
            resultado += f" · {dia.get('n')} achado(s) mesmo assim"
    elif leu_hoje or cor_dia == "verde":
        luz = "verde"
        n = int(dia.get("n") or 0)
        resultado = f"coletou hoje — {n} achado(s)" if n else "coletou hoje — sem dados novos"
        if falha:
            resultado += f" (atenção: {falha})"
    else:
        luz = "cinza"
        dg = p.get("diagnostico") or {}
        motivo = ("fora da agenda hoje" if dia.get("cor") == "fora" or (p.get("agenda_dias") and p.get("agenda_dias") != "todos"
                  and ["seg", "ter", "qua", "qui", "sex", "sab", "dom"][datetime.now(BRT).weekday()] not in str(p.get("agenda_dias")))
                  else "aguardando coleta local" if "coleta local" in str(dg.get("motivo_zero") or p.get("situacao") or "")
                  else "ainda não rodou hoje")
        resultado = f"não rodou hoje — {motivo}"
    return {"id": p.get("id"), "nome": p.get("nome"), "luz": luz, "resultado": resultado,
            "ultima_leitura": ult.isoformat(timespec="minutes") if ult else None,
            "agenda": " ".join(x for x in (str(p.get("agenda_dias") or ""), str(p.get("agenda_hora") or "")) if x and x != "None") or None}


_DIARIO: dict = {}


def run() -> dict:
    global _DIARIO
    _DIARIO = (_j(ROOT / "estado/esquadra_diario.json", {}) or {}).get("sensores") or {}
    M = _j(MOTORES, {})
    agora = datetime.now(BRT); hoje = agora.date().isoformat()
    motores = [status_de(p, hoje) for p in (M.get("oficiais") or []) + (M.get("plataformas") or []) if p.get("id")]
    cont = {c: sum(1 for m in motores if m["luz"] == c) for c in ("verde", "vermelho", "cinza")}
    out = {"gerado_em": agora.isoformat(timespec="minutes"), "proxima_atualizacao": (agora + timedelta(hours=CADA_HORAS)).isoformat(timespec="minutes"),
           "a_cada_horas": CADA_HORAS, "regra": __doc__.split("Não existe")[0].strip(), "contagem": cont, "motores": motores}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"gerado_em": out["gerado_em"], "contagem": cont}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
