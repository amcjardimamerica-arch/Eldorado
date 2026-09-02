"""Portão de fidelidade — o padrão de qualidade das telas.

Regra do titular, sem exceção:
  · PRESENTE e PASSADO: só dado real e confirmado — extraído do ato, ou
    confirmado com evidência registrada (titular ou sensor);
  · FUTURO: estimativa permitida, sempre marcada como tal;
  · janela de uma fonte NUNCA vem por analogia com outra fonte.

Este módulo é o último passo antes da publicação: classifica cada item que
vai às telas em `confirmado` / `estimado` / `hipotese`, e REMOVE do presente e
do passado tudo que não for confirmado. Registra o que removeu e por quê —
nada some em silêncio. Se um item chega aqui com data no presente e sem
confirmação, é defeito de origem e vira alerta.
"""
from __future__ import annotations

import json
from datetime import date

from .nucleo import ROOT, now_iso, write_json

RELATORIO = ROOT / "estado/portao_fidelidade.json"

_CONFIRMADOS = {"verificada_primaria", "verificada", "verificada_regra_anual",
                "verificada_janela_confirmada", "catalogada_historica"}


def classificar(e: dict, hoje: date) -> str:
    """confirmado | estimado | hipotese, com a regra explícita."""
    if e.get("sem_edital") and e.get("regra_anos") is None and e.get("etapa", 1) >= 2:
        return "confirmado"                      # emendas: regra anual do titular
    if e.get("janela_confirmada"):
        return "confirmado"                      # confirmada com evidência (titular/sensor)
    if e.get("regra_anos"):
        return "confirmado" if e.get("ano_permitido") is not None else "hipotese"
    if e.get("acervo") == "historico":
        c = e.get("ciclo") or {}
        insc = c.get("inscricao") or {}
        # histórico: a barra só é confirmada se as datas vieram do texto
        return "confirmado" if (insc and not insc.get("projetado")) else "estimado"
    if e.get("verificacao_dupla") or e.get("status") in _CONFIRMADOS:
        return "confirmado"
    return "hipotese"


def _no_presente_ou_passado(e: dict, hoje: date) -> bool:
    c = e.get("ciclo") or {}
    insc = c.get("inscricao") or {}
    ini = insc.get("inicio") or e.get("inicio")
    return bool(ini) and ini <= hoje.isoformat()


def aplicar(dados: dict, hoje: date | None = None) -> dict:
    """Aplica o portão ao pacote que vai às telas. Devolve o relatório."""
    hoje = hoje or date.today()
    removidos, marcados = [], {"confirmado": 0, "estimado": 0, "hipotese": 0}
    mantidos = []
    for e in dados.get("editais", []):
        classe = classificar(e, hoje)
        e["fidelidade"] = classe
        marcados[classe] += 1
        if classe != "confirmado" and _no_presente_ou_passado(e, hoje):
            # estimativa no presente/passado: NÃO vai à tela como faixa. Se for
            # histórico com abertura projetada, a barra vira bandeira de prazo
            if e.get("acervo") == "historico" and (e.get("ciclo") or {}).get("inscricao"):
                e["ciclo"]["inscricao"]["inicio"] = None      # sem início inventado
                e["ciclo"]["inscricao"]["projetado"] = False
                e["fidelidade"] = "confirmado_parcial"
                mantidos.append(e)
                continue
            removidos.append({"id": e.get("id"), "titulo": (e.get("titulo") or "")[:80],
                              "classe": classe, "motivo": "estimativa datada no presente/passado"})
            continue
        mantidos.append(e)
    dados["editais"] = mantidos
    # previsões: só futuro, e nunca por analogia (campo 'analogia' é proibido)
    prev = dados.get("previsoes", {})
    ok = []
    for p in prev.get("itens", []):
        if p.get("analogia"):
            removidos.append({"id": p["id"], "classe": "hipotese", "motivo": "janela por analogia com outra fonte"})
            continue
        if p["inicio"][:7] <= hoje.isoformat()[:7] and not p.get("especial"):
            # recorrência estatística no mês corrente não é dado: sai
            removidos.append({"id": p["id"], "classe": "estimado", "motivo": "estimativa no mês corrente"})
            continue
        ok.append(p)
    prev["itens"] = ok
    rel = {"aplicado_em": now_iso(), "referencia": hoje.isoformat(), "classes": marcados,
           "removidos": len(removidos), "amostra_removidos": removidos[:20],
           "regra": ("presente e passado só com confirmado; futuro estimado e marcado; "
                     "nada por analogia; o que sai fica registrado aqui")}
    write_json(RELATORIO, rel)
    dados["portao_fidelidade"] = {k: rel[k] for k in ("aplicado_em", "classes", "removidos", "regra")}
    return rel
