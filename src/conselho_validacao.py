"""CONSELHO DOS MOTORES · 2ª RODADA — VALIDAÇÃO DAS CORREÇÕES (titular, 10/10/2026).

Depois das correções de 10/10 (leitura diária, aprendiz de rotas com ponte e rotas de câmara, motor Outras
Oportunidades em clones, adaptadores WordPress e Mapas Culturais, agregadores alimentados), cada conselheiro fez
PERGUNTAS NOVAS — não repete a 1ª rodada: pergunta se a correção funcionou. As respostas vêm dos dados da produção,
comparadas com a 1ª rodada (docs/dados/conselho_motores.json). Saída: docs/dados/conselho_validacao.json e
docs/relatorios/conselho-validacao-<data>.md.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/conselho_validacao.json"

PERGUNTAS = {
    "falso_verde": ("Dra. Irene Lacerda (extremamente pessimista)",
                    ["Dos motores cegos e de página vazia da 1ª rodada, quantos já tiveram a rota testada pelo afinador?",
                     "A rota nova traz sinal de edital ou só responde?", "Algum continua cego mesmo depois da troca de rota?"]),
    "funil": ("Prof. Caio Menezes (pessimista)",
              ["Os motores de ruído da 1ª rodada continuam registrando achados que não viram oportunidade?",
               "A troca de rota aumentou a produção sem perder precisão?"]),
    "redundancia": ("Eng. Luana Freire (levemente pessimista)",
                    ["A redundância é saudável ou há pontos lidos por vários motores sem que nenhum renda (redundância vazia)?",
                     "Quanto custa o afinador e quantos domínios passaram a depender da ponte?"]),
    "cobertura": ("Dr. Otávio Lemos (neutro)",
                  ["A fatia de oportunidades achadas fora dos motores diminuiu?",
                   "Quais domínios só os agregadores encontram e ainda não têm motor?"]),
    "ritmo": ("Eng. Diego Arakaki (levemente otimista)",
              ["A leitura diária está sendo cumprida por todos os motores ativos?", "Quem não foi lido ontem nem hoje?"]),
    "fontes_irmas": ("Profa. Clara Nogueira (otimista)",
                     ["Outras Oportunidades está recebendo as fontes novas e lendo todas no mesmo dia?", "Os clones dão conta do volume?"]),
    "plataformas": ("Dr. Fábio Rangel (extremamente otimista)",
                    ["Os adaptadores por plataforma responderam? Quantas APIs abriram e quantos achados vieram?",
                     "Quais plataformas valem o próximo adaptador?"]),
}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _dom(u) -> str:
    try:
        return (urlsplit(str(u or "")).hostname or "").lower().replace("www.", "")
    except ValueError:
        return ""


def run(gravar: bool = True) -> dict:
    esq = _j(ROOT / "estado/esquadra.json", {}).get("sensores") or {}
    diario = _j(ROOT / "estado/esquadra_diario.json", {}).get("sensores") or {}
    r1 = _j(ROOT / "docs/dados/conselho_motores.json", {})
    rotas = _j(ROOT / "docs/dados/rotas_motores.json", {})
    agenda = _j(ROOT / "config/agenda_motores.json", {}).get("motores") or {}
    fl = _j(ROOT / "docs/dados/fluxo_oportunidades.json", {}); itens = [x for L in (fl.get("itens_por_uf") or {}).values() for x in L]
    oo = _j(ROOT / "estado/outras_oportunidades/fontes.json", {}).get("fontes") or {}
    pm1 = r1.get("por_motor") or {}; rm = rotas.get("motores") or {}
    res = {}

    # 1 · Irene — os cegos da 1ª rodada depois da troca de rota
    cegos = [m for m, v in pm1.items() if any(f["falha"] in ("CEGO", "PÁGINA VAZIA") for f in v.get("falhas") or [])]
    lin = []
    for m in cegos:
        r = rm.get(m) or {}; af = r.get("afinado") or {}; ap = r.get("rota_aprendida") or {}
        lin.append({"motor": m, "status": r.get("status") or "sem registro ainda", "vazias_seguidas": r.get("vazias_seguidas"),
                    "testado": bool(af), "rota_nova": ap.get("urls", [None])[0] if ap else None, "via": ap.get("via"),
                    "sinal_da_rota": ap.get("pontos"), "achados_hoje": (esq.get(m) or {}).get("achados_ultima")})
    res["falso_verde"] = {"cegos_da_1a_rodada": len(cegos), "testados": sum(1 for x in lin if x["testado"]),
                          "com_rota_nova": sum(1 for x in lin if x["rota_nova"]), "via_ponte": sum(1 for x in lin if x["via"] == "ponte"),
                          "continuam_cegos": [x["motor"] for x in lin if x["testado"] and not x["rota_nova"]],
                          "aguardando_afinador": sum(1 for x in lin if not x["testado"]), "detalhe": lin}

    # 2 · Caio — ruído
    ruido = [m for m, v in pm1.items() if v.get("valor") == "ruído"]
    conf = Counter(); para = Counter()
    for x in itens:
        o = str(x.get("origem") or ""); mid = o.split("motor ", 1)[1].split(" ")[0] if o.startswith("motor ") else ""
        para[mid] += 1; conf[mid] += bool(x.get("confirmada"))
    res["funil"] = {"motores_de_ruido_1a": len(ruido),
                    "ruido_agora": [{"motor": m, "achados_total_1a": (pm1.get(m) or {}).get("achados_total"), "achados_total_agora": (esq.get(m) or {}).get("achados_total"),
                                     "no_fluxo": para.get(m, 0), "confirmadas": conf.get(m, 0)} for m in ruido],
                    "ruido_que_passou_a_confirmar": [m for m in ruido if conf.get(m)]}

    # 3 · Luana — redundância vazia e ponte
    dom_mot = defaultdict(set)
    for mid, di in diario.items():
        for d in di.values():
            if d.get("url"):
                dom_mot[_dom(d["url"])].add(mid)
    def rendeu(mid):
        return sum(int(d.get("achados") or 0) for d in (diario.get(mid) or {}).values()) > 0
    vazia = sorted(((d, sorted(ms)) for d, ms in dom_mot.items() if len(ms) >= 2 and not any(rendeu(m) for m in ms)), key=lambda t: -len(t[1]))
    res["redundancia"] = {"pontos_com_redundancia": sum(1 for ms in dom_mot.values() if len(ms) >= 2),
                          "redundancia_vazia": [{"dominio": d, "motores": ms} for d, ms in vazia[:20]],
                          "dominios_via_ponte": (rotas.get("resumo") or {}).get("via_ponte"),
                          "exemplos_da_rede_de_rotas": (rotas.get("resumo") or {}).get("exemplos_da_rede")}

    # 4 · Otávio — cobertura antes/depois e domínios só de agregador
    motores = set(esq) | {m.replace("plat-", "") for m in esq}
    orig = Counter(); so_agreg = Counter()
    cob = {d.replace("www.", "") for d in ((_j(ROOT / "docs/dados/cobertura.json", {}).get("por_dominio") or {}))} | set(oo)
    for x in itens:
        o = str(x.get("origem") or ""); mid = o.split("motor ", 1)[1].split(" ")[0] if o.startswith("motor ") else o.split(" ·")[0]
        tipo = "motor" if mid in motores else ("Piloto" if "Piloto" in o else "agregador/outra"); orig[tipo] += 1
        if tipo == "agregador/outra" and x.get("link_oficial") and _dom(x["link_oficial"]) not in cob:
            so_agreg[_dom(x["link_oficial"])] += 1
    tot = sum(orig.values()) or 1
    res["cobertura"] = {"fora_dos_motores_pct_1a": (r1.get("cobertura") or {}).get("fora_dos_motores_pct"),
                        "fora_dos_motores_pct_agora": round(100 * (tot - orig["motor"]) / tot, 1), "origem": dict(orig),
                        "dominios_so_de_agregador": [{"dominio": d, "oportunidades": n} for d, n in so_agreg.most_common(15)],
                        "nota": "a fatia só cai depois que os motores novos (Outras Oportunidades, plataformas) completarem as primeiras leituras"}

    # 5 · Diego — leitura diária cumprida
    hoje = max((d for v in diario.values() for d in v), default=date.today().isoformat())
    ontem = (date.fromisoformat(hoje) - timedelta(days=1)).isoformat()
    inativos = {m for m, v in agenda.items() if str(v.get("dias")) == "inativo" or v.get("agregado_a")}
    ativos = [m for m in set(esq) | {m for m in agenda if m not in inativos} if m not in inativos]
    nao_lidos = sorted(m for m in ativos if m in esq and ontem not in (diario.get(m) or {}) and hoje not in (diario.get(m) or {}))
    res["ritmo"] = {"dia_de_referencia": hoje, "ativos": len(ativos), "lidos_ontem": sum(1 for m in ativos if ontem in (diario.get(m) or {})),
                    "lidos_hoje": sum(1 for m in ativos if hoje in (diario.get(m) or {})), "nao_lidos_ontem_nem_hoje": nao_lidos[:40],
                    "ainda_sem_primeira_leitura": sorted(m for m in ativos if m not in esq)}

    # 6 · Clara — Outras Oportunidades
    from .outras_oportunidades import dimensionar
    dim = dimensionar(len(oo))
    lidas_24h = sum(1 for f in oo.values() if str(f.get("ultima_leitura") or "") >= (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat())
    clones = {m: {"ultima": esq[m].get("ultima"), "duracao_s": esq[m].get("duracao_s"), "achados": esq[m].get("achados_ultima")} for m in esq if m.startswith("outras-oportunidades-")}
    res["fontes_irmas"] = {"fontes_recebidas": len(oo), "por_origem": dict(Counter(f.get("origem") for f in oo.values())),
                           "lidas_nas_ultimas_24h": lidas_24h, "dimensionamento": dim, "clones_que_ja_leram": clones,
                           "com_achado": sum(1 for f in oo.values() if f.get("achados"))}

    # 7 · Fábio — adaptadores por plataforma
    plat = {m: {"ultima": esq[m].get("ultima"), "achados": esq[m].get("achados_ultima"),
                "diagnostico": {k: (esq[m].get("diagnostico") or {}).get(k) for k in ("sites", "instancias", "respostas_json", "posts", "oportunidades", "motivo_zero")}}
            for m in ("plataforma-wordpress", "plataforma-mapas-culturais") if m in esq}
    res["plataformas"] = {"adaptadores": plat or "aguardando a primeira leitura pela agenda (09h53 e 11h23 de Brasília)",
                          "proximos_candidatos": {k: v for k, v in ((r1.get("plataformas") or {}).get("plataformas") or {}).items() if v.get("orgaos", 0) >= 5}}

    out = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "rodada": 2,
           "perguntas": {k: {"conselheiro": v[0], "perguntas": v[1]} for k, v in PERGUNTAS.items()}, "respostas": res}
    if gravar:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def relatorio_md(o: dict) -> str:
    R = o["respostas"]; L = [f"# Conselho dos motores — 2ª rodada (validação das correções) — {o['em'][:10]}", ""]
    for k, v in o["perguntas"].items():
        L += [f"## {v['conselheiro']}", ""] + [f"- {p}" for p in v["perguntas"]] + ["", "```json", json.dumps({kk: vv for kk, vv in R[k].items() if kk != "detalhe"}, ensure_ascii=False, indent=1)[:3500], "```", ""]
    return "\n".join(L)


if __name__ == "__main__":
    o = run()
    p = ROOT / f"docs/relatorios/conselho-validacao-{o['em'][:10]}.md"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(relatorio_md(o), encoding="utf-8")
    R = o["respostas"]
    print(json.dumps({"cegos": {k: R["falso_verde"][k] for k in ("cegos_da_1a_rodada", "testados", "com_rota_nova", "via_ponte", "aguardando_afinador")},
                      "continuam_cegos": R["falso_verde"]["continuam_cegos"], "ruido_que_confirma": R["funil"]["ruido_que_passou_a_confirmar"],
                      "redundancia_vazia": len(R["redundancia"]["redundancia_vazia"]), "cobertura": {k: R["cobertura"][k] for k in ("fora_dos_motores_pct_1a", "fora_dos_motores_pct_agora")},
                      "ritmo": {k: R["ritmo"][k] for k in ("ativos", "lidos_ontem", "lidos_hoje")}, "nao_lidos": len(R["ritmo"]["nao_lidos_ontem_nem_hoje"]),
                      "outras": {k: R["fontes_irmas"][k] for k in ("fontes_recebidas", "lidas_nas_ultimas_24h", "com_achado")}, "plataformas": R["plataformas"]["adaptadores"]},
                     ensure_ascii=False, indent=1, default=str))
