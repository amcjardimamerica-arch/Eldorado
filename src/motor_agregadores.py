"""MOTOR REGULAR — AGREGADORES DE EDITAIS (titular, 28/09) — REUNIDO AOS MOTORES INDEXADORES em 02/10/2026.

O antigo motor lia três listagens (CapitaAI /editais-abertos/para-ong, Farol Cultural /editais e o RSS do IDIS), no
máximo 40 editais por site e por rodada. Agora cada site tem o seu motor, com a metodologia do próprio site, e os
motores com a mesma metodologia formam uma família (src/indexadores/, config/indexadores.json):

  CapitaAI       → idx-sitemaps  (sitemap-captacao.xml + página pública de cada edital: ~550 páginas, não 40)
  Farol Cultural → idx-apis      (API /api/v1/editais?status=Aberto: os ~500 editais abertos, com link oficial)
  IDIS           → idx-feeds     (o mesmo RSS, filtrado por edital)

A saída continua a mesma — estado/agregadores/itens.json, com os mesmos ids — e este módulo continua existindo para
quem o chama: `python -m src.motor_agregadores` roda uma rodada dos motores indexadores.
"""
from __future__ import annotations

import json

from .indexadores.motor import rodada


def rodar() -> dict:
    r = rodada()
    return {"por_fonte": {k: v for k, v in (r.get("sites") or {}).items()}, "itens_vivos": r.get("no_fluxo"),
            "novos": r.get("novos"), "fora_do_fluxo": r.get("fora_do_fluxo")}


if __name__ == "__main__":
    print(json.dumps(rodar(), ensure_ascii=False, indent=1))
