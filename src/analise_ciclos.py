"""ANALISE O SISTEMA — workflow completo, decisões do Eldorado e ciclos de análise (titular, 15/10/2026).

Acrescenta ao diagnóstico único (src/diagnostico_sistema.py) três camadas:

1. WORKFLOW  a estrutura de 15/10: comando único (recibos, fases puladas, etapas com erro, cobertura sem agenda),
             fila de retentativa (aguardando e fora da fila), leitura parcial, curadoria do link oficial, validação
             por exceção e sua trava, auditorias (gabarito do Cartório, varredura de referência, ponte e robots) e o
             acompanhamento legislativo.
2. DECISÕES  em cada etapa, o que o Eldorado DECIDIU e a regra que DEVERIA valer; cada conferência dá "correto" ou
             "incorreto" com os casos — é a análise de se o sistema agiu como deveria.
3. CICLOS    intervalos de análise. Cada análise cobre a janela desde a anterior, lista as melhorias e correções
             implantadas na janela (PRs integrados e correções automáticas) e compara os problemas com o ciclo
             anterior: RESOLVIDO · PERSISTE (a correção implantada não resolveu) · NOVO (surgiu depois das correções) ·
             SEM DIAGNÓSTICO (não tem correção definida). A janela seguinte começa na implantação dessas correções, para
             validar o que ainda falha. Estado: estado/analise_ciclos.json
"""
from __future__ import annotations

import glob
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "docs/dados"
CICLOS = ROOT / "estado/analise_ciclos.json"


def _j(p: Path, padrao=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao if padrao is not None else {}


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _idade_h(ts) -> float | None:
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        return round((datetime.now(timezone.utc) - t).total_seconds() / 3600, 1)
    except Exception:  # noqa: BLE001
        return None


def _abertas() -> list[dict]:
    regs = (_j(ROOT / "dados/oportunidades/repositorio_unico.json") or {}).get("registros") or []
    return [r for r in regs if not r.get("arquivada") and r.get("estado") not in ("arquivada", "encerrada", "descartada", "fechada")]


# ── 1. WORKFLOW ────────────────────────────────────────────────────────────────────────────────────────────────────
def workflow(P: list, problema) -> dict:
    cm = _j(D / "comando.json"); u = cm.get("ultimo_ciclo") or {}
    hoje = _j(ROOT / f"estado/comando/{date.today().isoformat()}.json").get("ciclos") or []
    erros = [r for c in hoje for r in (c.get("recibos") or []) if r.get("erro")]
    puladas = Counter(d.get("fase") for c in hoje for d in (c.get("decisoes") or []) if d.get("pulou"))
    if not cm:
        problema(P, "comando_sem_recibo", "alta", "o comando único ainda não gravou recibo (docs/dados/comando.json)", "investigar o fluxo 22 (sem correção automática)")
    elif (_idade_h(cm.get("atualizado_em")) or 0) > 2:
        problema(P, "comando_parado", "alta", f"o comando único não fecha um ciclo há {_idade_h(cm.get('atualizado_em'))} h (passa a cada 30 min)", "investigar o fluxo 22 (sem correção automática)")
    if erros:
        problema(P, "comando_etapa_com_erro", "alta", f"{len(erros)} etapa(s) com erro nos ciclos de hoje: " + " | ".join(f"{e.get('etapa')}: {e.get('erro')}" for e in erros[:3]),
                 "investigar a etapa (sem correção automática)", len(erros), [e.get("etapa") for e in erros])
    ma = _j(D / "maestro.json")
    if ma.get("cobertura_percentual") is not None and ma["cobertura_percentual"] < 90 and datetime.now(timezone.utc).hour >= 23:
        problema(P, "cobertura_do_dia_baixa", "alta", f"cobertura do dia {ma['cobertura_percentual']}% ao fim do dia (meta 98%)", "investigar os motores pendentes (sem correção automática)")
    fr = _j(ROOT / "estado/fila_retentativa.json"); fora = fr.get("fora_da_fila") or {}
    if fora:
        problema(P, "pagina_fora_da_fila", "media", f"{len(fora)} página(s)/documento(s) fora da fila após 5 erros iguais",
                 "corrigir a rota ou ler no Chrome (sem correção automática)", len(fora), list(fora)[:8])
    cu = _j(ROOT / "estado/curadoria_links.json"); cc = cu.get("curadoria") or {}
    # 15/10 (ciclo 4): mede o REPOSITÓRIO (o que o sistema usa), não a entrada da curadoria
    reprov = {x.get("id") for x in cu.get("itens") or [] if x.get("curadoria") == "reprovado"}
    usam = [r.get("id") for r in _abertas() if r.get("link_oficial") and r.get("link_oficial") == r.get("url") and r.get("id") in reprov]
    if usam:
        problema(P, "link_acesso_como_oficial", "media", f"{len(usam)} oportunidade(s) usam o link de acesso como oficial sem serem fonte oficial",
                 "buscar a fonte oficial (resolvedor e Cartório)", len(usam), usam)
    ve = _j(ROOT / "estado/comando/validacao_excecao.json")
    av = _j(ROOT / "biblioteca_alexandria/livros/anexos/cartorio_avaliacao/resultado.json"); acerto = (av.get("geral") or {}).get("acerto_pct")
    if (_idade_h(av.get("em")) or 0) > 24 * 8:
        problema(P, "gabarito_desatualizado", "media", f"avaliação do Cartório com gabarito tem {_idade_h(av.get('em'))} h (semanal)", "disparar o fluxo 39")
    vr = sorted(glob.glob(str(ROOT / "estado/varredura_referencia/*.json")))
    ultima_var = vr[-1].rsplit("/", 1)[-1][:21] if vr else None
    if not vr or (vr and (_idade_h(_j(Path(vr[-1])).get("periodo", [None, None])[1] + "T23:59:00+00:00") or 0) > 24 * 16):
        problema(P, "varredura_desatualizada", "media", "varredura de referência dos diários e casas legislativas com mais de 15 dias", "disparar o fluxo 40")
    rb = _j(ROOT / "estado/robots_motores.json"); lg = _j(ROOT / "biblioteca_alexandria/livros/especiais/legislativo/legislativo.json")
    return {"comando": {"atualizado_em": cm.get("atualizado_em"), "ciclos_hoje": len(hoje), "vermelhos_hoje": cm.get("vermelhos_hoje"),
                        "etapas_com_erro_hoje": len(erros), "fases_puladas_hoje": dict(puladas),
                        "ultimo_ciclo": {"estado": u.get("estado"), "novos_na_base": u.get("novos_na_base"),
                                         "decisoes": u.get("decisoes"), "avaliacao": {k: (u.get("avaliacao") or {}).get(k) for k in ("cobertura_do_dia_pct", "completos", "reacionar", "para_humano")}}},
            "maestro": {k: ma.get(k) for k in ("planejados", "cobertura_percentual", "cobertura", "dia_fechado")},
            "retentativa": fr.get("resumo") or {"aguardando_retentativa": 0, "fora_da_fila": 0},
            "leitura_parcial": sum(1 for r in (fr.get("fila") or {}).values() if r.get("escopo") == "cartorio" and str(r.get("erro") or "").startswith(("parcial", "sem link"))),
            "curadoria": {"em": cu.get("em"), "resultado": cc, "captadas_direto_na_fonte_oficial": cu.get("mesmo_link_e_oficial"),
                          "trecho_do_documento_oficial": cu.get("trecho_do_documento_oficial")},
            "validacao_por_excecao": {k: ve.get(k) for k in ("em", "trava_aberta", "acerto_do_cartorio_pct", "candidatas", "acao")},
            "auditorias": {"gabarito_do_cartorio": {"em": av.get("em"), "acerto_pct": acerto, "documentos_lidos": av.get("documentos_lidos")},
                           "varredura_referencia": ultima_var, "robots": {"em": rb.get("em"), "motores_com_bloqueio": len(rb.get("motores_com_bloqueio") or {})},
                           "ponte": (_j(ROOT / "estado/ponte/diagnostico.json").get("resumo") or {})},
            "legislativo": {"atualizado_em": lg.get("atualizado_em"), "proposicoes": len(lg.get("itens") or {})}}


# ── 2. DECISÕES — o Eldorado agiu como deveria? ────────────────────────────────────────────────────────────────────
NAO_OPORTUNIDADE = re.compile(r"preg[ãa]o|registro de pre[çc]os|credenciamento de (?:prestadores|profissionais|farm[áa]cias|empresas|cl[íi]nicas)|"
                              r"contrata[çc][ãa]o de empresa|organiza[çc][ãa]o social na [áa]rea da sa[úu]de|processo seletivo simplificado", re.I)
LEGISLATIVO = re.compile(r"projeto de lei|utilidade p[úu]blica|lei or[çc]ament[áa]ria", re.I)


def decisoes(P: list, problema) -> list[dict]:
    hoje = date.today().isoformat(); ab = _abertas(); out = []

    def conf(etapa, decisao, regra, casos, total, como_corrigir, conferivel=True):
        if not conferivel:
            out.append({"etapa": etapa, "decisao": decisao, "regra": regra, "conferidos": 0, "incorretos": 0,
                        "veredito": "não conferido (sem registro desta etapa ainda)", "exemplos": []}); return
        ok = not casos
        out.append({"etapa": etapa, "decisao": decisao, "regra": regra, "conferidos": total, "incorretos": len(casos),
                    "veredito": "correto" if ok else "incorreto", "exemplos": casos[:6]})
        if not ok:
            problema(P, f"decisao_{etapa}", "alta" if etapa in ("qualificar", "validar", "farol") else "media",
                     f"[{etapa}] {decisao}: {len(casos)} de {total} contrariam a regra — {regra}", como_corrigir, len(casos), casos)

    ma = _j(D / "maestro.json"); u = (_j(D / "comando.json").get("ultimo_ciclo") or {})
    dec = next((d for d in (u.get("decisoes") or []) if d.get("fase") == "decidir"), {})
    pend = [p["motor"] for p in ma.get("plano") or [] if p.get("cobertura") in ("pendente", "parcial") and int(p.get("tentativas_hoje") or 0) < 3]
    conf("decidir", "motores escolhidos para ler na passagem",
         "todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)",
         pend if (pend and not dec.get("motores")) else [], len(ma.get("plano") or []), "investigar o comando (sem correção automática)",
         conferivel=bool(u))

    errados = [f"{r.get('id')}: {str(r.get('titulo'))[:90]}" for r in ab if NAO_OPORTUNIDADE.search(f"{r.get('titulo')} {(r.get('itens') or {}).get('Objeto', {}).get('valor') if isinstance((r.get('itens') or {}).get('Objeto'), dict) else ''}")]
    conf("qualificar", "oportunidades abertas para associação",
         "pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)",
         errados, len(ab), "rever o veredito (sem correção automática)")
    leg = [f"{r.get('id')}: {str(r.get('titulo'))[:90]}" for r in ab if LEGISLATIVO.search(str(r.get("titulo") or ""))]
    conf("legislativo", "atos legislativos fora das oportunidades",
         "projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas", leg, len(ab), "rever o veredito (sem correção automática)")
    venc = [f"{r.get('id')}: fim {r.get('fim')}" for r in ab if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("fim") or "")) and str(r["fim"]) < hoje]
    conf("prazo", "oportunidades contadas como abertas", "prazo vencido sai das abertas", venc, len(ab), "refazer o repositório")

    cu = {x.get("id"): x for x in (_j(ROOT / "estado/curadoria_links.json").get("itens") or [])}
    from .curadoria_links import classe
    agreg = [f"{r.get('id')}: {r.get('link_oficial')}" for r in ab if r.get("link_oficial") and classe(r["link_oficial"], r.get("orgao")) == "agregador ou replicador"]
    conf("site_oficial", "link oficial gravado no repositório", "agregador ou replicador nunca é link oficial", agreg, sum(1 for r in ab if r.get("link_oficial")),
         "buscar a fonte oficial (resolvedor e Cartório)")

    C = (__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/cartorio/certidoes.json", {}).get("certidoes") or {})
    sem_prova = []
    for k, c in C.items():
        for item, v in (c.get("itens") or {}).items():
            if isinstance(v, dict) and (not v.get("trecho") or not v.get("documento")):
                sem_prova.append(f"{k} · {item}"); break
    conf("certificar", "itens certificados pelo Cartório", "todo item certificado tem trecho literal e documento", sem_prova, len(C), "rever a extração (sem correção automática)")

    v1 = ROOT / "dados/oportunidades/validacao_mapa/validacao_0001-excecao.json"
    ve = _j(ROOT / "estado/comando/validacao_excecao.json")
    trava = [f"{len((_j(v1).get('itens') or []))} validada(s) por exceção com a trava fechada"] if (v1.exists() and ve and not ve.get("trava_aberta")) else []
    conf("validar", "validação por exceção", "só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria",
         trava, len((_j(v1).get("itens") or [])) if v1.exists() else 0, "apagar a validação automática indevida")

    farol = [f"{r.get('id')}: " + ("prazo vencido" if str(r.get("fim") or "9") < hoje else "link oficial não aprovado na curadoria")
             for r in ab if r.get("pronta_para_farol") and (str(r.get("fim") or "9") < hoje or (cu and (cu.get(r.get("id")) or {}).get("curadoria") != "aprovado"))]
    if not cu:
        farol = [x for x in farol if "prazo vencido" in x]             # sem curadoria ainda: confere só o prazo
    conf("farol", "oportunidades prontas para o Farol", "pronta só com prazo vigente e link oficial aprovado na curadoria", farol,
         sum(1 for r in ab if r.get("pronta_para_farol")), "rever a regra de prontidão (sem correção automática)")

    cat = (_j(ROOT / "biblioteca_alexandria/fontes/motores.json") or {}).get("motores") or []
    lv_leg = [f"{x.get('id')}: {str(x.get('programa') or x.get('titulo'))[:80]}" for x in cat if LEGISLATIVO.search(str(x.get("programa") or x.get("titulo") or ""))]
    conf("biblioteca", "livros da Biblioteca", "ato legislativo não gera livro", lv_leg, len(cat), "arquivar o livro (sem correção automática)")
    return out


# ── 3. CICLOS DE ANÁLISE ───────────────────────────────────────────────────────────────────────────────────────────
def _correcoes_na_janela(de: str, ate: str, gh) -> list[dict]:
    prs = gh("pulls?state=closed&sort=updated&direction=desc&per_page=100") or []
    out = [{"pr": p.get("number"), "titulo": p.get("title"), "implantada_em": p.get("merged_at")} for p in prs if isinstance(p, dict)
           and p.get("merged_at") and de <= str(p["merged_at"]).replace("Z", "+00:00") <= ate]
    return sorted(out, key=lambda x: x["implantada_em"])


def registrar_ciclo(diag: dict, log: list, gh, anterior_diag: dict | None = None) -> dict:
    H = _j(CICLOS, {"ciclos": []}); ciclos = H.setdefault("ciclos", [])
    ant = ciclos[-1] if ciclos else None
    agora = _agora()
    if ant:
        de = ant.get("proxima_janela_comeca_em") or ant.get("ate")
        prob_ant = ant.get("problemas") or {}
    else:                                             # 1º ciclo: a base é o diagnóstico anterior gravado
        de = (anterior_diag or {}).get("em") or agora
        prob_ant = {p["codigo"]: p.get("quantidade") or 1 for p in (anterior_diag or {}).get("problemas") or []}
    prob = {}
    sem_corr = []
    for p in diag.get("problemas") or []:
        prob[p["codigo"]] = prob.get(p["codigo"], 0) + (p.get("quantidade") or 1)
        c = str(p.get("correcao") or "")
        if not c or any(t in c for t in ("sem correção", "investigar")):
            sem_corr.append(p["codigo"])
    correcoes = _correcoes_na_janela(str(de), agora, gh)
    auto = [{"etapa": x["etapa"], "ok": x["ok"]} for x in log or []]
    comp = {"resolvidos": sorted(set(prob_ant) - set(prob)),
            "persistem": sorted(k for k in prob if k in prob_ant),
            "novos": sorted(k for k in prob if k not in prob_ant),
            "sem_diagnostico_de_correcao": sorted(set(sem_corr))}
    implant = max([c["implantada_em"] for c in correcoes] + ([agora] if any(a["ok"] for a in auto) else []) + [str(de)])
    c = {"n": (ant or {}).get("n", 0) + 1, "de": de, "ate": agora, "problemas": prob,
         "correcoes_implantadas_na_janela": correcoes, "correcoes_automaticas": auto, "comparacao_com_o_ciclo_anterior": comp,
         "proxima_janela_comeca_em": implant,
         "leitura": (f"{len(comp['resolvidos'])} resolvido(s) · {len(comp['persistem'])} persistem apesar de {len(correcoes)} correção(ões) "
                     f"implantada(s) · {len(comp['novos'])} novo(s) · {len(comp['sem_diagnostico_de_correcao'])} sem correção definida")}
    ciclos.append(c); H["ciclos"] = ciclos[-60:]
    CICLOS.parent.mkdir(parents=True, exist_ok=True)
    CICLOS.write_text(json.dumps(H, ensure_ascii=False, indent=1), encoding="utf-8")
    return c


def resumo_md(diag: dict, ciclo: dict | None) -> str:
    L = []
    w = diag.get("workflow") or {}
    if w:
        cm = w.get("comando") or {}
        L += ["## Workflow (estrutura de 15/10)",
              f"- comando único: {cm.get('ciclos_hoje')} ciclo(s) hoje · {cm.get('vermelhos_hoje')} vermelho(s) · {cm.get('etapas_com_erro_hoje')} etapa(s) com erro · fases puladas {cm.get('fases_puladas_hoje')}",
              f"- cobertura do dia: {(w.get('maestro') or {}).get('cobertura_percentual')}% de {(w.get('maestro') or {}).get('planejados')} motores",
              f"- retentativa: {w.get('retentativa')} · leitura parcial na fila: {w.get('leitura_parcial')}",
              f"- curadoria do link oficial: {(w.get('curadoria') or {}).get('resultado')}",
              f"- validação por exceção: {(w.get('validacao_por_excecao') or {}).get('acao')}",
              f"- auditorias: {w.get('auditorias')}", f"- legislativo: {w.get('legislativo')}", ""]
    dec = diag.get("decisoes") or []
    if dec:
        L += ["## Decisões do Eldorado: agiu como deveria?"] + \
             [f"- {d['etapa']} · {d['decisao']}: **{d['veredito']}** ({d['incorretos']} de {d['conferidos']}) — regra: {d['regra']}"
              + (f" · ex.: {'; '.join(d['exemplos'][:2])}" if d["exemplos"] else "") for d in dec] + [""]
    if ciclo:
        cp = ciclo["comparacao_com_o_ciclo_anterior"]
        L += [f"## Ciclo de análise nº {ciclo['n']} · janela {str(ciclo['de'])[:16]} → {ciclo['ate'][:16]}", f"- {ciclo['leitura']}",
              f"- correções implantadas na janela: " + ("; ".join(f"#{c['pr']} {c['titulo']}" for c in ciclo["correcoes_implantadas_na_janela"]) or "nenhuma lida (sem token)"),
              f"- resolvidos: {cp['resolvidos'] or 'nenhum'}", f"- persistem: {cp['persistem'] or 'nenhum'}", f"- novos: {cp['novos'] or 'nenhum'}",
              f"- sem correção definida: {cp['sem_diagnostico_de_correcao'] or 'nenhum'}",
              f"- a próxima janela começa em {str(ciclo['proxima_janela_comeca_em'])[:16]} (implantação das correções)", ""]
    return "\n".join(L)
