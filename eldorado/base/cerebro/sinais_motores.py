"""Os SINAIS de cada motor (titular, 05/11/2026: «o sistema deve mostrar o que está ocorrendo além do resultado; sem os
sinais o motor aparece como funcionando e eu tenho perdas grandes de finalidade»).

«Leu hoje sem erro» não diz se o motor está servindo: a execução termina sem erro mesmo quando uma fonte só pode ser lida
no computador local, quando uma fonte deixou de ser lida, quando a página nunca rende nada ou quando o motor passa dias
sem nenhuma novidade. Daqui, pelo estado de cada fonte (motor_fonte) e pelas entregas (motor_entregue), no Cérebro:

  - pendente no computador local: a fonte só se lê no computador da titular e o pedido fica esperando;
  - abandonada: a fonte da configuração não é lida há mais de 7 dias;
  - falhando: a última leitura da fonte deu erro;
  - sem novidade: nenhuma oportunidade nova entregue há mais de 7 dias;
  - nunca entregou: lê há mais de 7 dias e nunca entregou nada.

Luz: vermelho se todas as fontes falham ou se nunca entregou; amarelo com qualquer outro sinal; verde sem sinal.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

DIAS = 7


def _dt(t: str | None) -> datetime | None:
    if not t:
        return None
    try:
        d = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def da_config(motor: str) -> tuple[list[str], bool]:
    """As fontes e os alvos da configuração do motor (os nomes do registro de cada fonte) e se o destino é o especial."""
    import tomllib
    from pathlib import Path
    p = Path(__file__).resolve().parents[2] / "motores" / "canal" / "config" / f"{motor}.toml"
    if not p.exists():
        return [], False
    try:
        cfg = tomllib.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return [], False
    nomes = [f.get("nome", "") for f in cfg.get("fonte", [])] + [f"alvo · {a.get('id') or a.get('nome', '')}" for a in cfg.get("alvo", [])]
    return [n for n in nomes if n], (cfg.get("motor") or {}).get("destino") == "especial"


def sinais(cer: sqlite3.Connection, motor: str, fontes_config: list[str] | None = None, especial: bool | None = None,
           agora: datetime | None = None) -> dict[str, Any]:
    agora = agora or datetime.now(timezone.utc)
    if fontes_config is None or especial is None:
        cfg_nomes, cfg_esp = da_config(motor)
        fontes_config = cfg_nomes if fontes_config is None else fontes_config
        especial = cfg_esp if especial is None else especial
    limite = agora - timedelta(days=DIAS)
    try:
        linhas = cer.execute("SELECT nome, leituras, sem_mudanca, falhas, ultimo_erro, ultima, situacao FROM motor_fonte WHERE motor = ?",
                             (motor,)).fetchall()
        ult_ent = cer.execute("SELECT MAX(em), MIN(em) FROM motor_entregue WHERE motor = ?", (motor,)).fetchone()
    except sqlite3.Error:
        return {"luz": None, "sinais": [], "lidas": 0, "sem_mudanca": 0, "ultima_novidade": None}
    por = {r[0]: r for r in linhas}
    nomes = fontes_config if fontes_config else list(por)
    pend, aband, falha, lidas, sem_m = [], [], [], 0, 0
    for n in nomes:
        r = por.get(n)
        if r is None or (_dt(r[5]) and _dt(r[5]) < limite):
            aband.append(n)
            continue
        erro = str(r[4] or "")
        if "computador local" in erro:
            pend.append(n)
        elif r[6] == "erro":
            falha.append(n)
        else:
            lidas += 1
            sem_m += int(r[6] == "sem mudança")
    ultima_nov = (ult_ent[0] if ult_ent else None)
    primeira_leitura = min((_dt(r[5]) for r in linhas if _dt(r[5])), default=None)
    s = []
    if pend:
        s.append(f"{len(pend)} fonte(s) pendente(s) no computador local: {', '.join(pend)[:160]}")
    if aband:
        s.append(f"{len(aband)} fonte(s) sem leitura há mais de {DIAS} dias: {', '.join(aband)[:160]}")
    if falha:
        s.append(f"{len(falha)} fonte(s) falhando: {', '.join(falha)[:160]}")
    nunca = not especial and not ultima_nov and bool(linhas)
    if nunca:
        s.append("nunca entregou nenhuma oportunidade")
    elif not especial and ultima_nov and _dt(ultima_nov) < limite:
        s.append(f"sem oportunidade nova há {(agora - _dt(ultima_nov)).days} dias (a última em {str(ultima_nov)[8:10]}/{str(ultima_nov)[5:7]})")
    todas_falham = bool(nomes) and len(falha) + len(aband) + len(pend) == len(nomes)
    luz = "vermelho" if (todas_falham or nunca) else ("amarelo" if s else "verde")
    return {"luz": luz, "sinais": s, "lidas": lidas, "sem_mudanca": sem_m, "ultima_novidade": ultima_nov,
            "pendentes_local": pend, "abandonadas": aband, "falhando": falha, "nunca_entregou": nunca,
            "primeira_leitura": primeira_leitura.isoformat() if primeira_leitura else None}
