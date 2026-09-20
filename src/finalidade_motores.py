"""FINALIDADE DOS MOTORES — DESCOBERTA × RECORRÊNCIA — e ESPALHAMENTO.

Dois trabalhos diferentes, que antes se misturavam num só motor:

  DESCOBERTA ..... procurar o que ainda não existe na base: novas chamadas, novos
                   financiadores, novas rotas. Léxico amplo, cadência diária.
  RECORRÊNCIA .... revisitar o que já foi identificado: a página oficial de cada
                   oportunidade validada, para pegar retificação, prorrogação, resultado
                   — e, quando o ciclo fecha, a época em que o mesmo financiador
                   costuma reabrir. Léxico estreito (o próprio edital), cadência
                   por estado: aberta → a cada 2 dias; encerrada → mensal até a época
                   prevista; época prevista → diária.

ESPALHAMENTO: toda oportunidade nova validada gera (a) uma ROTA DE RECORRÊNCIA na
página oficial, (b) o financiador vira FONTE no catálogo se ainda não for, e (c) o
território e a área alimentam os motores de descoberta vizinhos (a prefeitura que
abriu chamamento entra na rota das 50 maiores; a empresa que publicou edital entra
nas rotas de empresas).

Saídas: config/finalidade_motores.json · estado/rotas_recorrencia.json
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

DESCOBERTA = {"do-goiania", "do-goias", "dou", "pncp-api", "plat-observatorio-3setor", "plat-abcr", "plat-gife", "plat-prosas",
              "plat-prosas-premios", "plat-salic", "plat-secult-go", "plat-ovg", "plat-goias-social", "plat-fundos-estaduais-go",
              "plat-fapeg", "plat-prefeituras-50-go", "plat-empresas-editais-incentivados", "plat-mp-destinacoes-reparacao",
              "plat-cnpq-extensao", "empresas-incentivadas", "dje-tjgo", "dj-trf1-go"}
INSUMO = {"alego-pl": "emenda parlamentar", "camara-goiania-pl": "utilidade pública", "cnj-destinacoes": "referência normativa"}
VETOR = re.compile(r"pncp\.gov|queridodiario|in\.gov\.br|diariooficial|observatorio3setor|captadores\.org|bussolasocial|prosas\.com", re.I)


def _cadencia_recorrencia(e: dict, hoje: date) -> tuple[int, str]:
    fim = e.get("fim")
    if fim and fim >= hoje.isoformat():
        return 2, "aberta: retificação, prorrogação ou resultado podem sair a qualquer momento"
    if fim:
        try:
            f = date.fromisoformat(fim)
            prox = f.replace(year=f.year + 1)                       # época provável de reabertura
            dias = (prox - hoje).days
            if -15 <= dias <= 45:
                return 1, f"época prevista de reabertura ({prox.isoformat()}): leitura diária"
            return 30, f"encerrada em {fim}: leitura mensal até a época prevista ({prox.isoformat()})"
        except ValueError:
            pass
    return 7, "sem prazo confirmado: leitura semanal até confirmar"


def montar() -> dict:
    hoje = date.today()
    from .sensores import registro
    regulares = [s for s in registro() if not s.get("fontes_260")]
    finalidade = {}
    for s in regulares:
        if s["id"] in INSUMO:
            finalidade[s["id"]] = {"finalidade": "insumo", "do_que": INSUMO[s["id"]], "cadencia_dias": 7}
        elif s["id"] in DESCOBERTA:
            finalidade[s["id"]] = {"finalidade": "descoberta", "cadencia_dias": 1}
        else:
            finalidade[s["id"]] = {"finalidade": "descoberta", "cadencia_dias": 1}
    finalidade["recorrencia"] = {"finalidade": "recorrencia", "nome": "Motor de Recorrência — revisita as oportunidades identificadas",
                                 "cadencia_dias": "por estado da oportunidade", "rotas": "estado/rotas_recorrencia.json"}
    # ── rotas de recorrência: uma por oportunidade validada, na página oficial ──
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = list(dados.get("editais") or [])
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        from .compacto import expandir
        vistos = {x["id"] for x in universo}
        universo += [o for o in expandir(load_json(ab)) if o.get("id") not in vistos]
    op = [e for e in universo if e.get("tipo_registro") in ("edital", "regra_anual") and e.get("selo_validacao") == "validada"]
    rotas = []
    novas_fontes = []
    for e in op:
        pag = e.get("pagina_divulgacao") or (e.get("validacao") or {}).get("site")
        if not pag or (VETOR.search(str(pag)) and "/arquivos/" not in str(pag)):
            continue
        cad, motivo = _cadencia_recorrencia(e, hoje)
        rotas.append({"edital_id": e["id"], "titulo": (e.get("titulo") or "")[:100], "url": pag, "orgao": e.get("orgao") or e.get("fonte_nome"),
                      "uf": e.get("uf"), "area": e.get("area"), "fim": e.get("fim"), "cadencia_dias": cad, "motivo": motivo,
                      "lexico": [w for w in ["retifica", "prorroga", "errata", "resultado", "homologa", "classificados", "recurso", "suspens", "revoga", "novo edital", "inscrições"]],
                      "proxima_leitura": hoje.isoformat()})     # a primeira leitura é imediata; o sensor reprograma pela cadência
        # espalhamento: o financiador vira fonte no catálogo, se ainda não for
        from urllib.parse import urlsplit
        host = urlsplit(pag).hostname
        if host:
            novas_fontes.append({"host": host, "orgao": e.get("orgao") or e.get("fonte_nome"), "uf": e.get("uf"), "area": e.get("area"), "origem_edital": e["id"]})
    cat = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    hosts_cat = {d for f in cat for d in (f.get("dominios") or [])}
    espalhar = {}
    for nf in novas_fontes:
        if nf["host"] not in hosts_cat:
            espalhar.setdefault(nf["host"], nf)
    res_rec = {"em": now_iso(), "total": len(rotas), "por_cadencia": {str(c): sum(1 for r in rotas if r["cadencia_dias"] == c) for c in sorted({r["cadencia_dias"] for r in rotas})},
               "regra": "cada oportunidade validada tem rota de recorrência na página oficial: aberta a cada 2 dias, encerrada mensal até a época prevista de reabertura, época prevista diária",
               "rotas": rotas}
    write_json(ROOT / "estado/rotas_recorrencia.json", res_rec)
    res_fin = {"versao": 1, "em": now_iso(), "regra": "DESCOBERTA procura o que não existe na base (léxico amplo, diário); RECORRÊNCIA revisita o identificado (léxico estreito, cadência por estado); INSUMO alimenta habilitação e emenda",
               "motores": finalidade,
               "espalhamento": {"regra": "toda oportunidade validada gera rota de recorrência; o financiador vira fonte no catálogo; território e área alimentam os motores de descoberta vizinhos",
                                "financiadores_novos_para_o_catalogo": list(espalhar.values())[:60], "total_novos": len(espalhar)}}
    write_json(ROOT / "config/finalidade_motores.json", res_fin)
    # curadoria: financiadores novos entram como fontes_novas (reaplicadas na regeneração do catálogo)
    cur_p = ROOT / "config/curadoria_fontes.json"
    if cur_p.exists() and espalhar:
        cur = load_json(cur_p)
        ids = {f.get("id") for f in (cur.get("fontes_novas") or [])}
        n = 0
        for host, nf in list(espalhar.items())[:30]:
            fid = "espalhado-" + re.sub(r"[^a-z0-9]+", "-", host.lower())[:40]
            if fid in ids:
                continue
            cur.setdefault("fontes_novas", []).append({"id": fid, "programa": f"{nf['orgao'] or host} — oportunidades (espalhado de edital validado)",
                "nivel": "municipal" if nf.get("uf") else "privada", "area": nf.get("area") or "outros", "tipo": "edital",
                "uf": nf.get("uf"), "orgao": nf.get("orgao") or host, "sites": [f"https://{host}/"], "dominios": [host],
                "confianca_site": "confirmada", "origem": f"espalhamento do edital {nf['origem_edital']} (validado)"})
            n += 1
        if n:
            cur["atualizada_em"] = hoje.isoformat()
            write_json(cur_p, cur)
        res_fin["espalhamento"]["adicionados_a_curadoria"] = n
    return {"descoberta": sum(1 for v in finalidade.values() if v.get("finalidade") == "descoberta"),
            "insumo": sum(1 for v in finalidade.values() if v.get("finalidade") == "insumo"),
            "rotas_recorrencia": len(rotas), "por_cadencia": res_rec["por_cadencia"],
            "financiadores_novos": len(espalhar), "adicionados_a_curadoria": res_fin["espalhamento"].get("adicionados_a_curadoria", 0)}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
