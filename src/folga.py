"""FOLGA DO PILOTO — só cede lugar se comprometer o sistema (titular, 26/09).

No GitHub Actions cada execução tem máquina própria: o Piloto nunca disputa CPU nem memória com os
motores de busca, e esta regra não muda nada. Ela existe para o dia em que Piloto e motores voarem na
MESMA máquina (servidor próprio, Oracle): aí, com os motores rodando e o uso acima de 85% de CPU ou
memória, o Piloto troca para o modelo menor do banco de reserva; se mesmo assim passar do limite,
pousa e espera. Abaixo de 85%, voa normalmente com o modelo principal.
"""
from __future__ import annotations

import os

LIMITE = 0.85


def recursos() -> dict:
    """Uso de CPU (carga média de 1 min por núcleo) e de memória, lidos do próprio sistema."""
    cpu = mem = None
    try:
        cpu = os.getloadavg()[0] / max(1, os.cpu_count() or 1)
    except Exception:
        pass
    try:
        info = {}
        for linha in open("/proc/meminfo", encoding="utf-8"):
            k, v = linha.split(":", 1)
            info[k] = int(v.strip().split()[0])
        mem = 1 - info["MemAvailable"] / info["MemTotal"]
    except Exception:
        pass
    return {"cpu": None if cpu is None else round(cpu, 2), "memoria": None if mem is None else round(mem, 2),
            "mesma_maquina_dos_motores": os.environ.get("ELDORADO_MOTORES_NA_MESMA_MAQUINA") == "1"}


def escolher(cargo: dict) -> tuple[dict, str]:
    """O modelo que voa agora: o ocupante, ou o menor da reserva se o sistema estiver no limite."""
    oc = cargo.get("ocupante_atual") or {}
    r = recursos()
    if not r["mesma_maquina_dos_motores"]:
        return oc, "máquina própria: voa com o ocupante"
    uso = max(r["cpu"] or 0, r["memoria"] or 0)
    if uso < LIMITE:
        return oc, f"uso em {int(uso * 100)}%: voa com o ocupante"
    reservas = sorted([x for x in (cargo.get("banco_de_reserva") or []) if x.get("url")], key=lambda x: float(x.get("gb") or 9))
    menor = reservas[0] if reservas else None
    if menor and float(menor.get("gb") or 9) < float(oc.get("gb") or 0):
        return menor, f"uso em {int(uso * 100)}% com os motores rodando: voa com o menor ({menor['nome']})"
    return {}, f"uso em {int(uso * 100)}% e sem modelo menor: pousa e espera"
