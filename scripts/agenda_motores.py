#!/usr/bin/env python3
"""AGENDA DOS MOTORES — quais motores rodam AGORA. Chamado de hora em hora pelo workflow
agenda-motores (minutos :23 e :53). Imprime os ids separados por vírgula, para a coleta
rodar só eles (MOTORES_FONTES). Motor de coleta local não sai daqui: roda no computador do
titular. Com --tudo, lista a agenda inteira."""
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def devidos(agora_utc: datetime | None = None) -> list[str]:
    ag = json.loads((RAIZ / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
    est = RAIZ / "estado/esquadra.json"     # 03/10: o registro das leituras é a esquadra (estado/sensores.json não existe)
    ult = (json.loads(est.read_text(encoding="utf-8")).get("sensores") or {}) if est.exists() else {}
    brt = (agora_utc or datetime.now(timezone.utc)) - timedelta(hours=3)
    faixa = "23" if brt.minute < 38 else "53"
    saida = []
    for mid, a in ag.items():
        if a.get("coleta") == "local" or a.get("horarios_brt") == "contínuo" or str(a.get("coleta") or "").startswith("fluxo"):
            continue                                        # 02/10: motores por site são lidos pelo fluxo 16, não pela agenda
        horas = [h.strip() for h in str(a["horarios_brt"]).split(",")]
        if not any(h == f"{brt.hour:02d}:{faixa}" for h in horas):
            continue
        d = str(a.get("dias") or "todos")
        if d.startswith("dia "):
            if brt.day != int(d.split()[1]): continue
        elif d not in ("todos",) and DIAS[brt.weekday()] not in d.split(","):
            continue
        cad = a.get("cadencia_dias") or 1
        u = (ult.get(mid) or {}).get("ultima")
        if cad >= 2 and u:                                  # cadência longa: não repete antes da hora
            try:
                if datetime.now(timezone.utc) - datetime.fromisoformat(u.replace("Z", "+00:00")) < timedelta(days=cad - 0.5):
                    continue
            except ValueError:
                pass
        saida.append(mid)
    return saida


def _ultimas_leituras() -> dict:
    """última leitura de cada motor, do painel (docs/dados/motores.json): id sem o prefixo plat- → ISO UTC."""
    try:
        M = json.loads((RAIZ / "docs/dados/motores.json").read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for p in (M.get("plataformas") or []) + (M.get("oficiais") or []):
        u = p.get("ultima_leitura")
        if not u:   # 29/09: motor que não grava a última leitura (ex.: recorrência) entrava em TODA varredura — usa o último dia executado
            feitos = [d.get("d") for d in (p.get("dias") or []) if d.get("cor") not in (None, "cinza", "fora", "futuro")]
            u = (max(feitos) + "T12:00:00+00:00") if feitos else None
        out[str(p.get("id")).replace("plat-", "")] = u
    return out


def recuperar(agora_utc=None) -> list[str]:
    """RECUPERAÇÃO DO HORÁRIO PERDIDO (28/09): o GitHub entrega só 8 a 12 das 48 execuções horárias por dia, e o motor
    só saía se a execução caísse EXATAMENTE no seu horário — perdia o dia inteiro. Agora, em cada execução que acontece,
    sai todo motor cujo último horário devido (dentro da cadência) já passou e que não rodou desde então."""
    ag = json.loads((RAIZ / "config/agenda_motores.json").read_text(encoding="utf-8"))
    ag = ag.get("motores") or ag
    agora = (agora_utc or datetime.now(timezone.utc))
    brt = agora - timedelta(hours=3)
    ult = _ultimas_leituras(); saida = []
    for mid, a in ag.items():
        if not isinstance(a, dict) or a.get("coleta") == "local" or a.get("horarios_brt") in (None, "contínuo") or str(a.get("coleta") or "").startswith("fluxo"):
            continue
        horas = sorted([h.strip() for h in str(a["horarios_brt"]).split(",") if ":" in h], reverse=True)
        d = str(a.get("dias") or "todos"); devido = None
        for atras in range(0, 8):
            dia = (brt - timedelta(days=atras)).date()
            if d.startswith("dia "):
                if dia.day != int(d.split()[1]): continue
            elif d != "todos" and DIAS[dia.weekday()] not in d.split(","):
                continue
            for h in horas:
                hh, mm = (int(x) for x in h.split(":"))
                slot = datetime(dia.year, dia.month, dia.day, hh, mm, tzinfo=timezone.utc) + timedelta(hours=3)   # BRT → UTC
                if slot <= agora:
                    devido = slot; break
            if devido:
                break
        if not devido or agora - devido > timedelta(days=(a.get("cadencia_dias") or 1) + 0.5):
            continue
        if mid.replace("plat-", "") not in ult:
            continue            # motor que o painel não acompanha: sem como saber se rodou — fica só com o horário exato
        u = ult.get(mid.replace("plat-", ""))
        try:
            ja = u and datetime.fromisoformat(str(u).replace("Z", "+00:00")) >= devido
        except ValueError:
            ja = False
        if not ja:
            saida.append(mid)
    return saida


if __name__ == "__main__":
    if "--tudo" in sys.argv:
        ag = json.loads((RAIZ / "config/agenda_motores.json").read_text(encoding="utf-8"))["motores"]
        for mid, a in sorted(ag.items(), key=lambda kv: kv[1]["horarios_brt"]):
            print(f"{a['horarios_brt']:12} {a['dias']:18} {mid}")
    else:
        print(",".join(sorted(set(devidos()) | set(recuperar()))))
