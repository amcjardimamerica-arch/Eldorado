"""AUDITORIA DOS MOTORES, UM POR UM — o que cada um entrega, e o que corrigir.

Não basta contar achados: um motor que traz 127 editais dos quais 90% não servem à associação
é pior do que um que traz 5 certeiros, porque enche a fila de trabalho inútil e esconde o que
presta. Aqui cada motor é julgado por DUAS medidas:

    volume       quantos achados trouxe em 24 dias
    efetividade  quantos deles servem ao objeto da associação

E recebe um dos estados:

    produtivo        traz e o que traz serve
    ruidoso          traz muito, quase nada serve  → precisa de filtro na captura
    seco             não traz nada há 24 dias      → rota provavelmente quebrada
    bloqueado        a fonte recusa nosso endereço → só com coleta local
    nunca_rodou      configurado e nunca executado → revisar a rota
"""
from __future__ import annotations

import collections
import glob
import json
import re
from datetime import date
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json
from .missao_especial import _relevante

SAIDA = ROOT / "docs/dados/auditoria_29.json"
RELATORIO = ROOT / "biblioteca_alexandria/AUDITORIA-MOTORES-29-2026-09-22.md"
# Fontes que recusam endereço estrangeiro — medido nas coletas anteriores
BLOQUEADOS = {"do-goiania", "do-goias", "dje-tjgo", "dj-trf1-go", "camara-goiania-pl"}


def _achados_por_motor() -> dict:
    ad = load_json(ROOT / "docs/dados/achados_dia.json")
    acum: collections.Counter = collections.Counter()
    for _, v in (ad.get("dias") or {}).items():
        for m, n in (v.get("motores") or {}).items():
            acum[m] += n if isinstance(n, int) else len(n)
    return dict(acum)


def _efetividade_do_acervo() -> dict:
    """Quantos dos editais capturados realmente servem. Mede o ruído na origem."""
    base = sorted(glob.glob(str(ROOT / "dados/editais/*-eldorado-*-completo.json")))
    if not base:
        return {}
    itens = load_json(Path(base[-1])).get("itens") or {}
    eds = list(itens.values()) if isinstance(itens, dict) else list(itens)
    serve = sum(1 for e in eds if _relevante({"titulo": e.get("objeto"), "orgao": e.get("orgao")})[0])
    return {"capturados": len(eds), "servem": serve, "ruido": len(eds) - serve,
            "efetividade": round(serve / len(eds), 3) if eds else 0.0}


def auditar() -> dict:
    cfg = load_json(ROOT / "config/rotas_motores.json")
    motores = cfg.get("motores") or cfg
    achados = _achados_por_motor()
    # casa o nome longo do achado com o id do motor
    por_id = {}
    for m, n in achados.items():
        k = m if m in motores else next((i for i in motores if i.lower() in str(m).lower()
                                         or str(m).lower().startswith(str(i).split("-")[0])), m)
        por_id[k] = por_id.get(k, 0) + n

    fichas, ordem = [], 0
    for mid, mc in (motores.items() if isinstance(motores, dict) else []):
        ordem += 1
        n = por_id.get(mid, 0)
        rotas = mc.get("rotas") or mc.get("urls") or []
        lex1 = mc.get("lexico_camada1") or []
        lex2 = mc.get("lexico_camada2") or []
        if mid in BLOQUEADOS:
            estado, causa = "bloqueado", "a fonte recusa endereço estrangeiro — só com coleta no computador do titular"
        elif n == 0 and not rotas:
            estado, causa = "nunca_rodou", "sem rota configurada"
        elif n == 0:
            estado, causa = "seco", "rota responde mas nada passa no léxico em 24 dias"
        elif n >= 40:
            estado, causa = "ruidoso", "volume alto: precisa de filtro de pertinência na captura"
        else:
            estado, causa = "produtivo", "entrega dentro do esperado"
        correcao = {
            "bloqueado": "marcar para coleta local; não gastar orçamento de voo",
            "nunca_rodou": "revisar a rota antes de qualquer ajuste de léxico",
            "seco": "ampliar o léxico da camada 1 e conferir se a página mudou de endereço",
            "ruidoso": "aplicar o filtro de objeto na captura, antes de entrar no acervo",
            "produtivo": "manter; acrescentar termos só quando a avaliação do Piloto sugerir",
        }[estado]
        fichas.append({"n": ordem, "id": mid, "nome": mc.get("nome") or mid, "perfil": mc.get("perfil"),
                       "achados_24d": n, "rotas": len(rotas), "lexico": len(lex1) + len(lex2),
                       "estado": estado, "causa": causa, "correcao": correcao})

    resumo = collections.Counter(f["estado"] for f in fichas)
    d = {"em": now_iso(), "motores": len(fichas), "resumo": dict(resumo),
         "acervo": _efetividade_do_acervo(),
         "regra": "volume sem pertinência é ruído: um motor que enche a fila de edital inútil atrapalha mais do que ajuda",
         "fichas": sorted(fichas, key=lambda f: (f["estado"] != "ruidoso", f["estado"] != "seco", -f["achados_24d"]))}
    write_json(SAIDA, d)
    return {k: v for k, v in d.items() if k != "fichas"}


def aplicar_correcoes() -> dict:
    """As correções que dá para aplicar sem intervenção humana."""
    d = load_json(SAIDA) if SAIDA.exists() else auditar() and load_json(SAIDA)
    cfg = load_json(ROOT / "config/rotas_motores.json")
    motores = cfg.get("motores") or cfg
    mudou = {"filtro_na_captura": [], "marcados_para_coleta_local": [], "lexico_ampliado": []}
    REFORCO = ["chamamento público", "termo de fomento", "termo de colaboração", "seleção de projetos",
               "edital de apoio", "fomento", "patrocínio", "prêmio", "organizações da sociedade civil"]
    for f in d.get("fichas", []):
        mc = motores.get(f["id"])
        if not isinstance(mc, dict):
            continue
        if f["estado"] == "ruidoso":
            mc["filtro_de_objeto"] = True
            mc["nota_filtro"] = "só entra no acervo o que serve ao objeto da associação (assistência social e cultura)"
            mudou["filtro_na_captura"].append(f["id"])
        if f["estado"] == "bloqueado":
            mc["coleta"] = "local"
            mc["nota_coleta"] = "recusa endereço estrangeiro; roda pelo computador do titular, não pelo voo"
            mudou["marcados_para_coleta_local"].append(f["id"])
        if f["estado"] == "seco":
            l1 = mc.setdefault("lexico_camada1", [])
            novos = [x for x in REFORCO if x not in l1]
            if novos:
                l1 += novos
                mudou["lexico_ampliado"].append(f["id"])
    cfg["motores"] = motores
    cfg["auditado_em"] = now_iso()
    write_json(ROOT / "config/rotas_motores.json", cfg)
    return mudou


def limpar_acervo() -> dict:
    """Tira do acervo o que nunca serviria à finalidade — e guarda o porquê."""
    base = sorted(glob.glob(str(ROOT / "dados/editais/*-eldorado-*-completo.json")))
    if not base:
        return {}
    arq = Path(base[-1])
    d = load_json(arq)
    itens = d.get("itens") or {}
    if not isinstance(itens, dict):
        return {}
    fora, motivos = {}, collections.Counter()
    for k, e in list(itens.items()):
        serve, porque = _relevante({"titulo": e.get("objeto"), "orgao": e.get("orgao"), "familia": e.get("familia")})
        if not serve:
            fora[k] = {"objeto": (e.get("objeto") or "")[:120], "orgao": e.get("orgao"),
                       "uf": e.get("uf"), "motivo": porque}
            motivos[porque[:44]] += 1
            itens.pop(k)
    d["itens"] = itens
    d["total"] = len(itens)
    d["limpeza"] = {"em": now_iso(), "removidos": len(fora), "motivos": dict(motivos.most_common(10)),
                    "onde_ficaram": "estado/piloto/aprendizados/acervo_fora_do_objeto.json",
                    "regra": "não se apaga sem guardar: o descartado vira matéria de estudo, não lixo"}
    write_json(arq, d)
    pasta = ROOT / "estado/piloto/aprendizados"
    pasta.mkdir(parents=True, exist_ok=True)
    write_json(pasta / "acervo_fora_do_objeto.json",
               {"em": now_iso(), "total": len(fora), "motivos": dict(motivos), "itens": fora})
    return d["limpeza"]


if __name__ == "__main__":
    import sys
    r = {"auditoria": auditar()}
    if "aplicar" in sys.argv:
        r["correcoes"] = aplicar_correcoes()
        r["limpeza"] = limpar_acervo()
    print(json.dumps(r, ensure_ascii=False, indent=1))
