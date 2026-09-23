#!/usr/bin/env python3
"""VIGIA DAS DATAS DOS TESTES — avisa antes que um teste apodreça.

O que aconteceu em 23/09: um teste guardava um edital com prazo fixo em 2026-09-30.
Enquanto faltavam mais de 7 dias, tudo passava. Quando o relógio virou e sobraram
exatamente 7, a regra do conselho ("≤7 dias com ≥4 documentos pendentes → regularizar
antes") passou a disparar, a etapa 4 deixou de escolher qualquer entidade e dois testes
ficaram vermelhos. Nada no sistema havia mudado: só o calendário.

Esse tipo de defeito é traiçoeiro porque aparece dias depois da última alteração, e quem
o encontra procura o erro no lugar errado. Este script lista as datas fixas que estão
prestes a cruzar um limite, para que sejam trocadas por datas relativas ANTES de quebrar.

    python3 scripts/datas_dos_testes.py            lista o que está perto
    python3 scripts/datas_dos_testes.py --falhar   sai com erro se algo já cruzou

Como corrigir uma fixture: troque a data fixa por uma relativa ao dia de hoje.

    "fim": "2026-09-30"
    "fim": (datetime.date.today() + datetime.timedelta(days=60)).isoformat()

Datas no passado geralmente são intencionais (testam edital encerrado) e ficam de fora.
"""
from __future__ import annotations

import datetime
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
# limites do sistema que mudam o comportamento conforme o prazo se aproxima
LIMITES = {7: "conselho passa a mandar 'regularizar antes'",
           15: "prazo entra na faixa de urgência do painel",
           0: "edital vira encerrado"}
FOLGA = 45          # a partir de quantos dias de folga paramos de nos preocupar
CAMPOS = re.compile(r'"(fim|prazo|encerramento|inscricoes_ate)":\s*"(20\d\d-\d\d-\d\d)"')


def varrer() -> list[dict]:
    hoje = datetime.date.today()
    achados = []
    for arq in sorted((RAIZ / "tests").glob("*.py")):
        for n, linha in enumerate(arq.read_text(encoding="utf-8").split("\n"), 1):
            for m in CAMPOS.finditer(linha):
                dias = (datetime.date.fromisoformat(m.group(2)) - hoje).days
                if 0 <= dias < FOLGA:
                    perto = [f"{k} dia(s): {v}" for k, v in sorted(LIMITES.items())
                             if 0 <= dias - k <= 3 or dias == k]
                    achados.append({"arquivo": arq.name, "linha": n, "campo": m.group(1),
                                    "data": m.group(2), "dias": dias, "cruza": perto})
    return sorted(achados, key=lambda x: x["dias"])


def main() -> int:
    achados = varrer()
    if not achados:
        print("nenhuma data fixa perto de cruzar um limite — tudo folgado")
        return 0
    criticos = [a for a in achados if a["dias"] <= 7]
    print(f"{len(achados)} data(s) fixa(s) com menos de {FOLGA} dias de folga"
          f"{f' — {len(criticos)} já em zona crítica' if criticos else ''}:\n")
    for a in achados:
        marca = "!!" if a["dias"] <= 7 else "  "
        print(f" {marca} {a['arquivo']}:{a['linha']:<5} {a['campo']}={a['data']} → faltam {a['dias']} dia(s)"
              + (f"  [{'; '.join(a['cruza'])}]" if a["cruza"] else ""))
    print("\nTroque por data relativa antes que quebre:"
          "\n  (datetime.date.today() + datetime.timedelta(days=60)).isoformat()")
    return 1 if ("--falhar" in sys.argv and criticos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
