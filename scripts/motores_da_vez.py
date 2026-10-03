#!/usr/bin/env python3
"""MOTORES DA VEZ — a lista que o fluxo 22 lê SOZINHO a cada passagem (teste dos motores, 03/10/2026).

O defeito medido no GitHub (03/10): a agenda e o maestro disparavam o fluxo 01 passando os motores no pedido
(`fontes=...`). O fluxo 01 leva de 45 minutos a 1h50 (testes, coleta geral, sensores) e só admite uma execução em
espera; cada disparo novo CANCELAVA o anterior que esperava — 20 execuções canceladas, e os motores pedidos nelas
nunca rodaram. A cobertura do dia ficou em 30%.

Agora o fluxo 22 não recebe a lista: ele a CALCULA no início de cada passagem, a partir do estado real:
  1. o que o maestro mede como pendente ou parcial no dia (rede neural de cobertura, com até 3 tentativas);
  2. o que a agenda diz que está no horário ou que perdeu o horário (recuperação);
  3. o que a passagem anterior adiou por falta de tempo.
Se uma passagem em espera for substituída por outra, nada se perde: a seguinte recalcula tudo.

    python scripts/motores_da_vez.py            # imprime os ids, separados por vírgula, na ordem de prioridade
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

SEMANAIS_NO_FLUXO_01 = {"motor-gife", "motor-patrocinio"}   # rodam no passo próprio de empresas do fluxo 01


def lista(disparar: bool = True) -> list[str]:
    ordem: list[str] = []

    def por(ids):
        for i in ids:
            i = str(i).strip()
            if i and i not in ordem and i not in SEMANAIS_NO_FLUXO_01:
                ordem.append(i)
    try:
        from src.maestro import controlar
        por(controlar(disparar=disparar).get("a_disparar") or [])
    except Exception as e:  # noqa: BLE001
        print(f"maestro indisponível: {type(e).__name__}", file=sys.stderr)
    try:
        import agenda_motores as A
        por(sorted(set(A.devidos()) | set(A.recuperar())))
    except Exception as e:  # noqa: BLE001
        print(f"agenda indisponível: {type(e).__name__}", file=sys.stderr)
    try:
        u = json.loads((RAIZ / "estado/esquadra.json").read_text(encoding="utf-8")).get("ultima_execucao") or {}
        por(u.get("adiados_por_tempo") or [])
    except Exception:  # noqa: BLE001
        pass
    # os motores numerados do painel (1, 2, 3…) vêm primeiro, na ordem do painel; depois as fontes sem horário próprio
    try:
        pos = (json.loads((RAIZ / "config/ordem_motores.json").read_text(encoding="utf-8")).get("posicoes") or {})
    except Exception:  # noqa: BLE001
        pos = {}
    idx = {m: i for i, m in enumerate(ordem)}
    return sorted(ordem, key=lambda m: (int(pos.get(m, pos.get(m.replace("plat-", ""), 10 ** 6))), idx[m]))


if __name__ == "__main__":
    print(",".join(lista(disparar="--sem-registrar" not in sys.argv)))
