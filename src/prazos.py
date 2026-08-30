"""Vigilância de prazos — determinística, sem IA e sem tokens.

Lê o prazo textual extraído da fonte (`prazo_texto`), calcula os dias corridos
restantes e classifica cada oportunidade em faixas de urgência definidas em
`config/padroes_edital.json` → prazos.alerta_dias.

Nada aqui substitui a leitura do edital: o prazo capturado é sempre rotulado
como *mencionado na fonte, exige conferência*. Prazos vencidos não somem — o
histórico alimenta o aprendizado de janelas recorrentes.

Saídas: `estado/prazos.json` (consumido pelo painel, pelas fichas HTML e pelo
resumo de execução) e marcação `alerta_prazo` em `estado/alerta_prazos.json`
quando algo entra na faixa crítica.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime

from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

_DATA_BR = re.compile(r"(\d{1,2})/(\d{1,2})/(20\d{2})")
_DATA_ISO = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")

def data_do_prazo(item: dict) -> date | None:
    """Extrai a data do prazo sem inventar: só converte o que está escrito."""
    for campo in ("prazo_final", "prazo_texto"):
        bruto = str(item.get(campo) or "")
        achado = _DATA_BR.search(bruto)
        if achado:
            dia, mes, ano = (int(g) for g in achado.groups())
            try:
                return date(ano, mes, dia)
            except ValueError:
                continue
        achado = _DATA_ISO.search(bruto)
        if achado:
            ano, mes, dia = (int(g) for g in achado.groups())
            try:
                return date(ano, mes, dia)
            except ValueError:
                continue
    return None

def classificar(dias: int | None, faixas: list[int]) -> str:
    if dias is None:
        return "sem_prazo_identificado"
    if dias < 0:
        return "encerrado"
    for limite in sorted(faixas):
        if dias <= limite:
            return f"faltam_{limite}_dias_ou_menos"
    return "em_aberto"

def run(hoje: date | None = None) -> dict:
    cfg = load_json(ROOT / "config/padroes_edital.json")["prazos"]
    faixas = cfg["alerta_dias"]
    hoje = hoje or date.today()
    registros = carregar_oportunidades()
    linhas = []
    for item in registros.values():
        vencimento = data_do_prazo(item)
        dias = (vencimento - hoje).days if vencimento else None
        situacao = classificar(dias, faixas)
        item["prazo_situacao"] = situacao
        item["prazo_dias_restantes"] = dias
        if vencimento:
            linhas.append({
                "id": item["id"], "titulo": item.get("titulo"), "url": item.get("url"),
                "fonte_nome": item.get("fonte_nome"), "territorio": item.get("territorio"),
                "status": item.get("status"), "vencimento": vencimento.isoformat(),
                "dias_restantes": dias, "situacao": situacao,
                "observacao": "prazo mencionado na fonte — conferir no edital antes de qualquer decisão",
            })
    linhas.sort(key=lambda x: x["dias_restantes"])
    criticos = [x for x in linhas if x["dias_restantes"] is not None and 0 <= x["dias_restantes"] <= max(faixas)]
    relatorio = {
        "gerado_em": now_iso(), "referencia": hoje.isoformat(),
        "com_prazo": len(linhas), "criticos": len(criticos),
        "encerrados": sum(1 for x in linhas if x["situacao"] == "encerrado"),
        "sem_prazo": sum(1 for x in registros.values() if x.get("prazo_situacao") == "sem_prazo_identificado"),
        "faixas_alerta": faixas, "itens": linhas[:500],
    }
    write_json(ROOT / "estado/prazos.json", relatorio)

    if criticos:
        corpo = ["Oportunidades com prazo próximo do encerramento (data mencionada na fonte, conferir no edital):", ""]
        corpo += [f"- **{x['dias_restantes']} dia(s)** — [{x['titulo']}]({x['url']}) · {x['fonte_nome']}" for x in criticos[:40]]
        write_json(ROOT / "estado/alerta_prazos.json", {
            "abrir_issue": True, "titulo": f"Prazos a vencer — {hoje.isoformat()}",
            "corpo": "\n".join(corpo), "quantidade": len(criticos), "gerado_em": now_iso(),
        })
    else:
        write_json(ROOT / "estado/alerta_prazos.json", {"abrir_issue": False, "gerado_em": now_iso()})

    from .nucleo import gravar_oportunidades
    gravar_oportunidades(registros)
    return {k: v for k, v in relatorio.items() if k != "itens"}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
