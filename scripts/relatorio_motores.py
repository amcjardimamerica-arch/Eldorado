#!/usr/bin/env python3
"""RELATÓRIO INDIVIDUAL DOS MOTORES — um capítulo por motor, com o fluxo de cada um.

Para decidir se um motor fica, muda ou sai, é preciso ver onde ele perde o que busca. Cada
capítulo segue o mesmo caminho que o registro percorre:

    AGENDA      o motor rodou nos dias em que devia?
    LEITURA     as páginas abriram, ou o site bloqueou?
    LÉXICO      o texto lido casou com os termos do motor?
    CAPTURA     quantos registros ele trouxe?
    TRIAGEM     quantos eram mesmo edital de fomento a OSC?
    ABRANGÊNCIA quantos eram de Goiás, Goiânia ou nacional?
    BIBLIOTECA  quantos ficaram como oportunidade ativa?

O lugar onde a contagem despenca é "onde o motor para" — e é ali que a correção tem de mirar.

Tudo sai dos arquivos do próprio sistema. Onde o dado não existe, o relatório escreve "sem
dado" e diz por quê: um número inventado aqui decidiria errado o destino de um motor.

    python3 scripts/relatorio_motores.py
"""
from __future__ import annotations

import collections
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

SAIDA_MD = RAIZ / "biblioteca_alexandria/pareceres/RELATORIO-MOTORES-INDIVIDUAL-2026-09-24.md"
SAIDA_JSON = RAIZ / "docs/dados/relatorio_motores.json"


def ler(p: str, padrao=None):
    f = RAIZ / p
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else padrao
    except Exception:
        return padrao


def dominio(u: str) -> str:
    return (urlsplit(str(u or "")).hostname or "").replace("www.", "")


def pct(a, b) -> str:
    return f"{100 * a / b:.0f}%" if b else "—"


def coletar() -> dict:
    rotas = ler("config/rotas_motores.json", {})
    motores = rotas.get("motores") or {}
    veto = rotas.get("camada_1_veto") or []
    geral = rotas.get("camada_1_geral") or []
    aud = {x["id"]: x for x in (ler("estado/auditoria_motores.json", {}).get("itens") or [])}
    val = ler("docs/dados/validacao_motores_mes.json", {}).get("motores") or {}
    alertas = {x["id"]: x for x in (ler("estado/alerta_motores.json", {}).get("alertas") or [])}
    bloq = ler("estado/bloqueios.json", {}).get("dominios") or {}
    fin = dict(ler("config/finalidade_motores.json", {}).get("motores") or [])
    an = ler("dados/editais/analises.json", {}) or {}

    # o elo registro → motor: a ficha da Biblioteca guarda de que fonte o registro veio
    from src.nucleo import chave_curta
    por_fonte = collections.defaultdict(lambda: collections.Counter())
    for f in (RAIZ / "biblioteca_alexandria/oportunidades").glob("*/*/ficha.json"):
        try:
            v = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        fid = v.get("fonte_id") or "?"
        a = an.get(v.get("id")) or an.get(chave_curta(v.get("id"))) or {}
        marca = ("fora_do_objeto" if (v.get("fora_do_objeto") or a.get("fora_do_objeto")) else
                 "fora_de_abrangencia" if ("fora_de_abrangencia" in (v.get("alcance"), a.get("alcance"))) else
                 "ativo")
        por_fonte[fid][marca] += 1
        por_fonte[fid]["total"] += 1

    ids_motores = set(motores) | set(aud) | set(val)

    def fontes_do_motor(mid: str) -> list[str]:
        # o motor plat-X também traz registros gravados como fonte 'X'; o motor 'X-api' grava 'X'.
        # Uma fonte que é ela mesma id de motor pertence só a ele — sem contagem dupla.
        alvo = {mid}
        if mid.startswith("plat-") and mid[5:] not in ids_motores:
            alvo.add(mid[5:])
        if mid.endswith("-api") and mid[:-4] not in ids_motores:
            alvo.add(mid[:-4])
        return [f for f in por_fonte if f in alvo]

    saida = []
    for mid in sorted(set(motores) | set(aud) | set(val)):
        m = motores.get(mid) or {}
        a = aud.get(mid) or {}
        vv = val.get(mid) or {}
        rts = m.get("rotas") or []
        doms = sorted({dominio(r.get("url")) for r in rts if r.get("url")} - {""})   # rota local não é domínio
        bloqueios = {d: bloq[d]["bloqueios"] for d in doms if d in bloq}
        for d, info in bloq.items():                       # subdomínio também conta
            if d not in bloqueios and any(d.endswith("." + x) or x.endswith("." + d) for x in doms):
                bloqueios[d] = info.get("bloqueios")
        dias = vv.get("dias") or []
        estados_dia = collections.Counter(x.get("estado") for x in dias)
        res = collections.Counter()
        fts = fontes_do_motor(mid)
        for f in fts:
            res.update(por_fonte[f])
        total = res["total"]
        elim = res["fora_do_objeto"] + res["fora_de_abrangencia"]

        # ONDE PARA: o primeiro estágio em que a contagem despenca
        esperados, execs = vv.get("dias_esperados"), vv.get("dias_executados")
        # MOTOR NOVO NÃO É MOTOR PARADO. Quem nasceu em 20/09 e rodou todo dia desde então aparecia
        # como "3 de 23" e era mandado reativar. O esperado passa a contar do primeiro dia em que
        # o motor rodou; antes disso ele não existia.
        cad = vv.get("cadencia") or 1
        rodou = [x.get("dia") for x in dias if x.get("estado") not in ("nao_exec", None)]
        desde = min(rodou) if rodou else None
        if desde and esperados and cad == 1:
            ultimo = max(x.get("dia") for x in dias)
            vida = (datetime.fromisoformat(ultimo) - datetime.fromisoformat(desde)).days + 1
            esperados = min(esperados, vida)
        falhas = estados_dia.get("falha", 0)
        achados = a.get("achados_total")
        if not (a or vv):
            para = ("sem medição", "o motor não tem auditoria nem validação: nunca foi medido como os outros")
        elif a.get("estado") == "BLOQUEADO":
            para = ("leitura", f"o site recusa o servidor — {a.get('base')}")
        elif esperados and execs is not None and execs < 0.5 * esperados:
            para = ("agenda", f"rodou {execs} de {esperados} dias esperados")
        elif execs and falhas >= max(1, 0.5 * execs):
            para = ("leitura", f"{falhas} de {execs} execuções falharam")
        elif not achados and not vv.get("encontrados"):
            para = ("léxico", "lê as páginas e nada casa com os termos — nenhum achado no mês")
        elif total and elim / total > 0.5:
            para = ("triagem", f"{elim} de {total} registros eliminados ({pct(elim, total)})")
        elif total:
            para = ("chega à biblioteca", f"{res['ativo']} de {total} ativos")
        else:
            para = ("captura sem ficha", f"{achados or vv.get('encontrados')} achado(s) sem ficha na Biblioteca")

        # VEREDITO — regra escrita, para a decisão poder ser refeita
        coleta = m.get("coleta") or "nuvem"
        finalidade = (fin.get(mid) or {}).get("finalidade")
        if not (a or vv):
            ver = ("MEDIR", "entrou no sistema depois da auditoria; sem número não há como julgar")
        elif coleta == "local" and (a.get("estado") in ("BLOQUEADO", "LENDO SEM ACHAR") or not achados):
            # a fonte recusa o servidor por desenho: 'ler sem achar' na nuvem é ler a página de recusa
            ver = ("COLETA LOCAL", "a fonte recusa endereço de fora do país; o que a nuvem lê é a página de "
                                   "recusa — só rende pelo computador do titular")
            para = ("leitura", "a nuvem é recusada; a coleta desta fonte é local")
        elif finalidade == "insumo":
            ver = ("INSUMO", f"não busca oportunidade: alimenta o sistema com {(fin.get(mid) or {}).get('do_que') or 'referência'}; "
                             "não se mede por achado")
        elif a.get("estado") == "BLOQUEADO":
            ver = ("COLETA LOCAL", "o servidor é recusado; só lê pelo computador do titular" if coleta != "local"
                   else "já marcado como coleta local; falta rodar pelo computador do titular")
        elif para[0] == "agenda":
            ver = ("REATIVAR", "não está rodando nos dias previstos")
        elif para[0] == "léxico" and (execs or 0) < 7:
            # três dias sem achado não condenam ninguém: a fonte pode simplesmente não ter publicado
            ver = ("OBSERVAR", f"só {execs} execução(ões) desde que nasceu — amostra curta demais para julgar o léxico")
        elif para[0] == "léxico" and execs and execs >= 10:
            ver = ("ELIMINAR OU REFAZER", f"{execs} execuções no mês sem nenhum achado")
        elif para[0] == "léxico":
            ver = ("AFINAR LÉXICO", "lê, mas os termos não casam com o que a fonte publica")
        elif para[0] == "triagem":
            ver = ("AFINAR FILTRO", "traz volume, mas quase tudo é ruído")
        elif para[0] == "leitura":
            ver = ("CONSERTAR ROTA", "as páginas falham com frequência")
        else:
            ver = ("MANTER", "produz e o que produz sobrevive à triagem")

        saida.append({
            "id": mid, "nome": a.get("nome") or vv.get("nome") or m.get("perfil") or mid,
            "perfil": m.get("perfil"), "tipo": a.get("tipo"), "coleta": coleta, "nota_coleta": m.get("nota_coleta"),
            "finalidade": (fin.get(mid) or {}).get("finalidade"), "cadencia_dias": (fin.get(mid) or {}).get("cadencia_dias") or vv.get("cadencia"),
            "rotas": [{"nome": r.get("nome"), "url": r.get("url"), "tipo": r.get("tipo")} for r in rts],
            "dominios": doms, "lexico_1": m.get("lexico_camada1") or [], "lexico_2": m.get("lexico_camada2") or [],
            "estado": a.get("estado") or "sem auditoria", "base": a.get("base"), "ultima": a.get("ultima"),
            "achados_total": achados, "alerta": (alertas.get(mid) or {}).get("problema"),
            "bloqueios": bloqueios,
            "mes": {"esperados": esperados, "executados": execs, "cobertura": vv.get("cobertura"),
                    "encontrados": vv.get("encontrados"), "falhas": vv.get("falhas"),
                    "dias": dict(estados_dia), "veredito": vv.get("veredito")},
            "fontes_no_acervo": fts, "resultado": {"total": total, "ativo": res["ativo"],
                                                   "fora_do_objeto": res["fora_do_objeto"],
                                                   "fora_de_abrangencia": res["fora_de_abrangencia"],
                                                   "pct_eliminado": round(100 * elim / total, 1) if total else None},
            "onde_para": {"estagio": para[0], "porque": para[1]},
            "veredito": {"decisao": ver[0], "porque": ver[1]},
            "conselho_da_auditoria": a.get("conselho"),
        })
    return {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "veto_geral": veto, "lexico_geral": geral, "motores": saida,
            "fontes_sem_motor": {f: dict(c) for f, c in por_fonte.items()
                                 if not any(f in x["fontes_no_acervo"] for x in saida)}}


def fluxo(x: dict) -> str:
    """O workflow do motor em Mermaid, com os números reais em cada passagem."""
    ms, r = x["mes"], x["resultado"]
    n = lambda v: "—" if v is None else str(v)
    bl = sum(v or 0 for v in x["bloqueios"].values())
    para = x["onde_para"]["estagio"]
    alvo = {"agenda": "A", "leitura": "L", "léxico": "X", "triagem": "T",
            "captura sem ficha": "C", "chega à biblioteca": "B", "sem medição": "A"}.get(para, "")
    linhas = [
        "```mermaid", "flowchart LR",
        f'  A["AGENDA<br/>cada {n(x["cadencia_dias"])} dia(s)<br/>{n(ms["executados"])}/{n(ms["esperados"])} dias"]',
        f'  L["LEITURA<br/>{len(x["rotas"])} rota(s)<br/>falhas no mês: {n(ms["falhas"])}<br/>bloqueios: {bl}"]',
        f'  X["LÉXICO<br/>{len(x["lexico_1"])}+{len(x["lexico_2"])} termos<br/>dias com achado: {n(ms["dias"].get("encontrado", ms["dias"].get("com_oport")))}"]',
        f'  C["CAPTURA<br/>{n(x["achados_total"])} achado(s)"]',
        f'  T["TRIAGEM<br/>fora do objeto: {r["fora_do_objeto"]}<br/>fora da abrangência: {r["fora_de_abrangencia"]}"]',
        f'  B["BIBLIOTECA<br/>{r["ativo"]} restante(s) de {r["total"]}"]',
        "  A --> L --> X --> C --> T --> B",
    ]
    # vermelho só onde o motor PARA; motor que chega à biblioteca termina em verde
    if para == "chega à biblioteca":
        linhas.append("  style B fill:#EAF6EF,stroke:#1E7E4B,stroke-width:2px")
    elif alvo:
        linhas.append(f"  style {alvo} fill:#FDECEA,stroke:#B3261E,stroke-width:2px")
    linhas.append("```")
    return "\n".join(linhas)


def escrever(d: dict) -> str:
    M = d["motores"]
    ordem = {"MANTER": 0, "AFINAR FILTRO": 1, "AFINAR LÉXICO": 2, "CONSERTAR ROTA": 3, "REATIVAR": 4,
             "COLETA LOCAL": 5, "INSUMO": 6, "OBSERVAR": 7, "MEDIR": 8, "ELIMINAR OU REFAZER": 9}
    cont = collections.Counter(x["veredito"]["decisao"] for x in M)
    out = [f"# Relatório individual dos motores de busca",
           f"\n**Gerado em:** {d['em'][:16].replace('T', ' ')} UTC · **{len(M)} motores** · "
           "números lidos dos arquivos do sistema; onde não há dado, está escrito *sem dado*.",
           "\n## Como ler",
           "\nCada motor percorre o mesmo caminho: **agenda → leitura → léxico → captura → triagem → "
           "biblioteca**. O fluxo de cada um mostra os números reais em cada passagem, e o estágio em "
           "vermelho é **onde ele para** — é ali que a correção tem de mirar.",
           "\n## Painel das decisões\n",
           "| decisão | motores |", "|---|---|"]
    for k in sorted(cont, key=lambda k: ordem.get(k, 9)):
        out.append(f"| **{k}** | {cont[k]} |")
    out += ["\n| # | motor | estado | mês (exec/esperado · falhas · achados) | acervo (ativo/total · % eliminado) | para em | decisão |",
            "|---|---|---|---|---|---|---|"]
    for i, x in enumerate(sorted(M, key=lambda x: (ordem.get(x["veredito"]["decisao"], 9), x["id"])), 1):
        ms, r = x["mes"], x["resultado"]
        out.append(f"| {i} | `{x['id']}` | {x['estado']} | "
                   f"{ms['executados'] if ms['executados'] is not None else '—'}/{ms['esperados'] or '—'} · "
                   f"{ms['falhas'] if ms['falhas'] is not None else '—'} · {ms['encontrados'] if ms['encontrados'] is not None else '—'} | "
                   f"{r['ativo']}/{r['total']} · {str(r['pct_eliminado']) + '%' if r['pct_eliminado'] is not None else '—'} | "
                   f"{x['onde_para']['estagio']} | **{x['veredito']['decisao']}** |")
    out += ["\n---\n", "## Os motores, um a um\n"]
    for i, x in enumerate(sorted(M, key=lambda x: (ordem.get(x["veredito"]["decisao"], 9), x["id"])), 1):
        ms, r = x["mes"], x["resultado"]
        out += [f"### {i}. {x['nome']}  \n`{x['id']}` · decisão: **{x['veredito']['decisao']}** — {x['veredito']['porque']}\n",
                "**Parâmetros.** "
                f"{x['perfil'] or 'perfil não descrito'}. Tipo: {x['tipo'] or '—'} · finalidade: {x['finalidade'] or '—'} · "
                f"cadência: a cada {x['cadencia_dias'] or '—'} dia(s) · coleta: **{x['coleta']}**"
                + (f" ({x['nota_coleta']})" if x.get("nota_coleta") else "") + ".\n",
                f"**Onde busca.** {len(x['rotas'])} rota(s) em {len(x['dominios'])} domínio(s): "
                + ("; ".join(f"{rt['nome'] or '—'} (`{dominio(rt['url'])}`)" for rt in x["rotas"][:6]) or "nenhuma rota cadastrada")
                + (f" … e mais {len(x['rotas']) - 6}" if len(x["rotas"]) > 6 else "") + ".\n",
                f"**Léxico.** Camada 1 ({len(x['lexico_1'])} termos, abre a leitura): "
                + (", ".join(f"*{t}*" for t in x["lexico_1"][:10]) or "—")
                + (f" … +{len(x['lexico_1']) - 10}" if len(x["lexico_1"]) > 10 else "")
                + f". Camada 2 ({len(x['lexico_2'])} termos, confirma): "
                + (", ".join(f"*{t}*" for t in x["lexico_2"][:8]) or "—")
                + (f" … +{len(x['lexico_2']) - 8}" if len(x["lexico_2"]) > 8 else "")
                + f". Veto geral: {len(d['veto_geral'])} termos.\n",
                "**Bloqueio.** " + (f"estado **{x['estado']}**" + (f" — {x['base']}" if x.get("base") else ""))
                + (f". Domínios com recusa registrada: " + ", ".join(f"`{k}` ({v})" for k, v in x["bloqueios"].items())
                   if x["bloqueios"] else ". Nenhum domínio dele na lista de bloqueios.")
                + (f" Alerta aberto: {x['alerta']}." if x.get("alerta") else "") + "\n",
                f"**Setembro.** " + (f"rodou {ms['executados']} de {ms['esperados']} dias ({pct(ms['executados'] or 0, ms['esperados'] or 0)}); "
                                    f"dias por estado: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in ms["dias"].items())
                                    + f"; achados no mês: {ms['encontrados']}; veredito da validação: *{ms['veredito']}*."
                                    if ms["esperados"] else "sem dado: o motor não está na validação mensal.") + "\n",
                f"**Resultado no acervo.** " + (f"{r['total']} registro(s) na Biblioteca — **{r['ativo']} não eliminado(s)** (ainda não quer dizer aprovado), "
                                               f"{r['fora_do_objeto']} fora do objeto, {r['fora_de_abrangencia']} fora da abrangência: "
                                               f"**{r['pct_eliminado']}% eliminado**. Fontes: {', '.join(f'`{f}`' for f in x['fontes_no_acervo'])}."
                                               if r["total"] else "nenhuma ficha na Biblioteca atribuída a ele.")
                + (f" Achados totais na auditoria: {x['achados_total']}." if x["achados_total"] is not None else "")
                + (f" **{x['achados_total'] - r['total']} achado(s) ficaram entre a captura e a Biblioteca** "
                   "(duplicata de registro já existente ou descarte antes de virar ficha)."
                   if (x["achados_total"] or 0) > r["total"] else "") + "\n",
                f"**Onde para: {x['onde_para']['estagio']}.** {x['onde_para']['porque']}.\n",
                "**Fluxo do motor**\n", fluxo(x), "\n"]
        c = x.get("conselho_da_auditoria") or {}
        if c.get("neutro_decide"):
            out.append(f"> *Auditoria de 23/09 (ponderadora):* {c['neutro_decide']}\n")
        out.append("---\n")
    pares = []
    for i, a in enumerate(M):
        for b in M[i + 1:]:
            comum = sorted(set(a["dominios"]) & set(b["dominios"]))
            if comum:
                pares.append((a["id"], b["id"], comum))
    d["sobreposicao"] = [{"a": a, "b": b, "dominios": c} for a, b, c in pares]
    out += ["## Sobreposição de rotas — candidatos a fusão\n",
            "Dois motores que leem o mesmo domínio gastam duas leituras para o mesmo conteúdo, e o site "
            "conta as duas contra o limite dele. Onde há sobreposição, um motor absorve o outro.\n"]
    if pares:
        out += ["| motor | motor | domínios em comum |", "|---|---|---|"]
        for a, b, c in sorted(pares, key=lambda x: -len(x[2])):
            out.append(f"| `{a}` | `{b}` | {', '.join(f'`{x}`' for x in c[:5])}{' …' if len(c) > 5 else ''} |")
    else:
        out.append("Nenhum par de motores lê o mesmo domínio: os nomes parecidos não são duplicata.")
    out.append("")
    if d["fontes_sem_motor"]:
        out += ["## Fontes no acervo que nenhum motor reivindica\n",
                "Registros cuja origem não corresponde a nenhum dos motores — plataformas de captação e "
                "cargas antigas. Não entram no julgamento dos motores, mas pesam no acervo.\n",
                "| fonte | total | ativo | fora do objeto | fora da abrangência |", "|---|---|---|---|---|"]
        for f, c in sorted(d["fontes_sem_motor"].items(), key=lambda kv: -kv[1].get("total", 0))[:25]:
            out.append(f"| `{f}` | {c.get('total', 0)} | {c.get('ativo', 0)} | {c.get('fora_do_objeto', 0)} | {c.get('fora_de_abrangencia', 0)} |")
    parecer = RAIZ / "config/parecer_motores.md"
    if parecer.exists():
        out += ["\n---\n", parecer.read_text(encoding="utf-8")]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    d = coletar()
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA_MD.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_MD.write_text(escrever(d), encoding="utf-8")
    c = collections.Counter(x["veredito"]["decisao"] for x in d["motores"])
    print(f"{len(d['motores'])} motores · decisões: {dict(c)}")
    print(f"→ {SAIDA_MD.relative_to(RAIZ)}\n→ {SAIDA_JSON.relative_to(RAIZ)}")
