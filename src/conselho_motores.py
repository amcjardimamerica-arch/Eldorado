"""CONSELHO DOS MOTORES (titular, 10/10/2026) — sete prompts, sete auditorias, uma por conselheiro.

Cada conselheiro escreveu o SEU prompt, com uma lente que os outros não usam, e o procedimento abaixo executa esse prompt
individualmente sobre CADA motor, com os dados reais da produção (diário de 30 dias, funil de leitura, destino dos
achados no fluxo e no Cartório, mapa de domínios cobertos). Saída: docs/dados/conselho_motores.json e o relatório
docs/relatorios/conselho-motores-<data>.md — onde cada motor falha e o que melhorar, e as inovações de alcance.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "docs/dados/conselho_motores.json"
FONTES_IRMAS = ROOT / "estado/conselho/fontes_irmas.json"

CONSELHO = [
    {"id": "falso_verde", "lente": "extremamente pessimista", "nome": "Dra. Irene Lacerda — auditora forense de silêncio",
     "prompt": "Você é uma auditora forense que desconfia de todo motor 'verde'. Para CADA motor, prove se ele está realmente "
               "enxergando ou só respondendo: cruze 30 dias de diário (HTTP, achados, falhas), o funil da última leitura "
               "(links vistos → candidatos → vetados pela camada 1 → achados), a duração e as leituras vazias seguidas. Aponte o "
               "motor CEGO (responde 200 e nunca acha nada), o ESTRANGULADO (vê centenas de links e o filtro descarta todos), o "
               "CONGELADO (repete o mesmo achado), o de PÁGINA VAZIA (lê em menos de 1 s: JavaScript ou bloqueio) e o "
               "INTERMITENTE (cai e volta). Para cada um, diga a causa provável e o conserto."},
    {"id": "funil", "lente": "pessimista", "nome": "Prof. Caio Menezes — caçador de vazamentos do funil",
     "prompt": "Você mede onde o valor de cada motor vaza. Para CADA motor, siga os achados até o fim: achado → oportunidade no "
               "fluxo → confirmada (objeto + prazo + site oficial) → certidão do Cartório → ouro. Ache a etapa em que o motor "
               "perde mais, separe o motor que gera RUÍDO (muitos achados, nenhuma confirmação) do que gera OURO, e diga que "
               "procedimento faltou na etapa que vaza."},
    {"id": "redundancia", "lente": "levemente pessimista", "nome": "Eng. Luana Freire — engenheira de custo e redundância",
     "prompt": "Você corta desperdício. Para CADA motor, calcule o custo por achado útil (segundos de leitura ÷ achados), ache os "
               "domínios lidos por mais de um motor (trabalho duplicado) e os motores que gastam tempo sem retorno. Proponha "
               "fundir, reduzir a cadência ou redistribuir o tempo para quem rende."},
    {"id": "cobertura", "lente": "neutra", "nome": "Dr. Otávio Lemos — juiz de cobertura",
     "prompt": "Você é o juiz imparcial do alcance. Compare onde as oportunidades REALMENTE aparecem (UF, tipo de financiador, "
               "origem: motor, Piloto ou agregador) com onde os motores olham. Cada oportunidade achada fora dos motores é um "
               "ponto cego. Diga quais territórios e tipos de fonte não têm motor e quanto do total vem de fora deles."},
    {"id": "ritmo", "lente": "levemente otimista", "nome": "Eng. Diego Arakaki — arquiteto do ritmo",
     "prompt": "Você ajusta o relógio de cada motor ao ritmo da fonte. Para CADA motor, veja em quais dias ele achou algo nos "
               "últimos 30 dias e com que intervalo; compare com a cadência da agenda. Recomende a cadência certa: ler mais "
               "quem publica muito, ler menos quem publica pouco, e o dia da semana em que a fonte costuma publicar."},
    {"id": "fontes_irmas", "lente": "otimista", "nome": "Profa. Clara Nogueira — mineradora de fontes irmãs",
     "prompt": "Você descobre fontes que o sistema já tocou mas não vigia. Liste os domínios OFICIAIS que aparecem nas "
               "oportunidades, nas certidões do Cartório e na biblioteca de sites, e que NENHUM motor cobre. Ordene pelo número "
               "de oportunidades que já renderam e transforme a lista num motor novo, lido todos os dias."},
    {"id": "plataformas", "lente": "extremamente otimista", "nome": "Dr. Fábio Rangel — inventor de alcance em massa",
     "prompt": "Você pensa em escala: uma solução que cubra centenas de fontes de uma vez. Agrupe os endereços oficiais conhecidos "
               "pela PLATAFORMA que os gera (WordPress, portais de transparência de fornecedores, diários municipais em lote, "
               "Mapas Culturais, sistemas de editais) e calcule quantos órgãos cada adaptador cobriria. Proponha as inovações "
               "que multiplicam o alcance: adaptador por plataforma, detecção de mudança por sitemap/feed, consultas inversas."},
]


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


def dados() -> dict:
    fl = _j(ROOT / "docs/dados/fluxo_oportunidades.json", {})
    return {"esq": (_j(ROOT / "estado/esquadra.json", {}).get("sensores") or {}),
            "diario": (_j(ROOT / "estado/esquadra_diario.json", {}).get("sensores") or {}),
            "itens": [x for L in (fl.get("itens_por_uf") or {}).values() for x in L],
            "certs": (_j(ROOT / "estado/cartorio/certidoes.json", {}).get("certidoes") or {}),
            "cob": _j(ROOT / "docs/dados/cobertura.json", {}),
            "agenda": (_j(ROOT / "config/agenda_motores.json", {}).get("motores") or {}),
            "bib": (_j(ROOT / "estado/cartorio/biblioteca_sites.json", {}).get("sites") or {})}


def _origem_motor(x: dict) -> str:
    o = str(x.get("origem") or "")
    return o.split("motor ", 1)[1].split(" ")[0] if o.startswith("motor ") else o.split(" ·")[0]


# ── 1 · FALSO VERDE ────────────────────────────────────────────────────────────────────────────────────────────
def a_falso_verde(D: dict) -> dict:
    out = {}
    for mid, s in D["esq"].items():
        dg = s.get("diagnostico") or {}; di = D["diario"].get(mid) or {}
        dias = sorted(di)[-30:]; reg = [di[d] for d in dias]
        ok200 = sum(1 for r in reg if r.get("http") == 200); ach = sum(int(r.get("achados") or 0) for r in reg)
        verm = sum(1 for r in reg if r.get("cor") == "vermelho")
        trechos = [r.get("trecho") for r in reg if r.get("trecho")]
        links, cand = int(dg.get("links_total") or 0), int(dg.get("links_candidatos") or 0)
        vet = int(dg.get("camada1_vetados") or 0)
        f = []
        if ok200 >= 10 and ach == 0:
            f.append(("CEGO", f"respondeu 200 em {ok200} de {len(reg)} dias e não achou nada em 30 dias",
                      "conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)"))
        if links >= 80 and cand == 0:
            f.append(("ESTRANGULADO", f"viu {links} links e nenhum virou candidato",
                      "o filtro de candidatos está estreito demais: incluir termos de chamamento/edital da fonte e seguir PDFs"))
        if vet and cand and vet / max(1, vet + cand) > 0.9:
            f.append(("FILTRO AGRESSIVO", f"a camada 1 vetou {vet} de {vet + cand} candidatos",
                      "revisar as regras de veto (termos amplos demais) com amostra de 20 vetados"))
        if len(trechos) >= 5 and len(set(trechos)) == 1:
            f.append(("CONGELADO", f"o mesmo achado repetido em {len(trechos)} dias", "detectar mudança por hash/lastmod e só contar o que é novo"))
        if s.get("duracao_s") is not None and float(s.get("duracao_s") or 0) < 1 and int(dg.get("paginas_lidas") or 0) <= 1:
            f.append(("PÁGINA VAZIA", f"leitura em {s.get('duracao_s')} s com {dg.get('paginas_lidas')} página(s)",
                      "a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte"))
        if 4 <= verm <= len(reg) - 4:
            f.append(("INTERMITENTE", f"{verm} dias vermelhos alternados com dias bons", "retentativa com espera e rota de reserva (ponte do titular)"))
        if int(s.get("vazias_seguidas") or 0) >= 14:
            f.append(("SILÊNCIO LONGO", f"{s.get('vazias_seguidas')} leituras vazias seguidas", "reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço"))
        out[mid] = {"achados_30d": ach, "dias_http_200": ok200, "dias_vermelhos": verm, "falhas": f}
    return out


# ── 2 · FUNIL ──────────────────────────────────────────────────────────────────────────────────────────────────
def a_funil(D: dict) -> dict:
    por = defaultdict(lambda: {"no_fluxo": 0, "confirmadas": 0, "certidoes": 0, "completas": 0, "ouro": 0})
    for x in D["itens"]:
        m = _origem_motor(x); p = por[m]; p["no_fluxo"] += 1; p["confirmadas"] += bool(x.get("confirmada"))
    for c in D["certs"].values():
        m = _origem_motor(c); p = por[m]; p["certidoes"] += 1
        p["completas"] += bool(c.get("link_oficial") and not c.get("ainda_faltam")); p["ouro"] += c.get("selo_depois") == "ouro"
    out = {}
    for mid, s in D["esq"].items():
        p = dict(por.get(mid) or por.get(mid.replace("plat-", "")) or {"no_fluxo": 0, "confirmadas": 0, "certidoes": 0, "completas": 0, "ouro": 0})
        p["achados_total"] = int(s.get("achados_total") or 0)
        etapas = [("achado → fluxo", p["achados_total"], p["no_fluxo"]), ("fluxo → confirmada", p["no_fluxo"], p["confirmadas"]),
                  ("confirmada → certidão completa", p["confirmadas"], p["completas"])]
        vaza = max(((n, a, b) for n, a, b in etapas if a), key=lambda t: (t[1] - t[2]) / t[1], default=None)
        f = []
        if p["achados_total"] >= 20 and p["confirmadas"] == 0:
            f.append(("RUÍDO", f"{p['achados_total']} achados e nenhuma oportunidade confirmada",
                      "exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício"))
        if vaza and vaza[1] >= 5 and (vaza[1] - vaza[2]) / vaza[1] >= 0.8:
            f.append(("VAZAMENTO", f"perde {round(100 * (vaza[1] - vaza[2]) / vaza[1])}% na etapa '{vaza[0]}'",
                      {"achado → fluxo": "achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver",
                       "fluxo → confirmada": "faltam prazo ou site oficial: entregar o documento (url_documento) ao Cartório",
                       "confirmada → certidão completa": "o documento oficial não traz os 12 itens: anexos e termo de referência"}[vaza[0]]))
        out[mid] = {**p, "falhas": f, "valor": "ouro" if p["ouro"] else "confirma" if p["confirmadas"] else "ruído" if p["achados_total"] >= 20 else "baixo volume"}
    return out


# ── 3 · REDUNDÂNCIA E CUSTO ────────────────────────────────────────────────────────────────────────────────────
def a_redundancia(D: dict) -> dict:
    dom_mot = defaultdict(set)
    for mid, di in D["diario"].items():
        for r in di.values():
            if r.get("url"):
                dom_mot[_dom(r["url"])].add(mid)
    for dom, mid in ((D["cob"].get("por_dominio") or {}).items()):
        dom_mot[dom.replace("www.", "")].add(mid)
    out = {}
    for mid, s in D["esq"].items():
        dur = float(s.get("duracao_s") or 0); ach = int(s.get("achados_ultima") or 0)
        meus = [d for d, ms in dom_mot.items() if mid in ms]
        dup = sorted({m for d in meus for m in dom_mot[d] if m != mid})
        f = []
        if dur >= 120 and ach == 0:
            f.append(("CUSTO SEM RETORNO", f"{round(dur)} s na última leitura sem achado", "reduzir páginas por leitura ou a cadência; transferir o tempo para motores que rendem"))
        # 10/10 (titular): ler o mesmo ponto por mais de um motor é REDUNDÂNCIA de propósito — informa, não é falha
        out[mid] = {"duracao_s": dur, "segundos_por_achado": round(dur / ach, 1) if ach else None, "dominios": meus[:6], "redundancia_com": dup[:6], "falhas": f}
    return out


# ── 4 · COBERTURA ──────────────────────────────────────────────────────────────────────────────────────────────
def a_cobertura(D: dict) -> dict:
    origens = Counter(); por_uf = defaultdict(Counter)
    motores = set(D["esq"]) | {m.replace("plat-", "") for m in D["esq"]}
    for x in D["itens"]:
        o = _origem_motor(x); fora = o not in motores
        tipo = "motor" if not fora else ("Piloto" if "Piloto" in str(x.get("origem")) else "agregador/outra")
        origens[tipo] += 1; por_uf[x.get("uf") or "nacional"][tipo] += 1
    ufs_motor = Counter(str(s.get("uf") or (s.get("diagnostico") or {}).get("uf") or "?") for s in D["esq"].values())
    cegos = sorted(((uf, c) for uf, c in por_uf.items() if c["motor"] == 0 and sum(c.values()) >= 2), key=lambda t: -sum(t[1].values()))
    tot = sum(origens.values()) or 1
    return {"origem_das_oportunidades": dict(origens), "fora_dos_motores_pct": round(100 * (tot - origens["motor"]) / tot, 1),
            "ufs_sem_motor_com_oportunidade": [{"uf": u, "oportunidades": sum(c.values()), "de_onde": dict(c)} for u, c in cegos[:15]],
            "motores_por_uf": dict(ufs_motor.most_common(12))}


# ── 5 · RITMO ──────────────────────────────────────────────────────────────────────────────────────────────────
def a_ritmo(D: dict) -> dict:
    out = {}
    for mid in D["esq"]:
        di = D["diario"].get(mid) or {}
        dias = sorted(d for d, r in di.items() if int(r.get("achados") or 0) > 0)
        lidos = len(di)
        ag = D["agenda"].get(mid) or {}
        cad = int(ag.get("cadencia_dias") or 1)
        sem = Counter(date.fromisoformat(d).weekday() for d in dias if re.match(r"\d{4}-\d{2}-\d{2}$", d))
        nomes = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        if len(dias) >= 2:
            gaps = [(date.fromisoformat(b) - date.fromisoformat(a)).days for a, b in zip(dias, dias[1:])]
            intervalo = round(sum(gaps) / len(gaps), 1)
        else:
            intervalo = None
        rec = cad; motivo = "manter"
        if len(dias) >= 12 and cad > 1:
            rec, motivo = 1, "publica quase todo dia: ler diariamente"
        # 10/10 (titular): a leitura é SEMPRE diária, mesmo sem oportunidade — nunca se recomenda espaçar
        f = [] if rec == cad else [("CADÊNCIA FORA DO RITMO", f"agenda a cada {cad} dia(s); a fonte rendeu em {len(dias)} de {lidos} dias",
                                    f"ler a cada {rec} dia(s) — {motivo}" + (f"; dia forte: {nomes[sem.most_common(1)[0][0]]}" if sem else ""))]
        out[mid] = {"dias_com_achado": len(dias), "dias_lidos": lidos, "intervalo_medio": intervalo, "cadencia_atual": cad,
                    "cadencia_recomendada": rec, "dia_forte": nomes[sem.most_common(1)[0][0]] if sem else None, "falhas": f}
    return out


# ── 6 · FONTES IRMÃS ───────────────────────────────────────────────────────────────────────────────────────────
def a_fontes_irmas(D: dict) -> dict:
    from .cartorio_leitura import regua
    cob = {d.replace("www.", "") for d in (D["cob"].get("por_dominio") or {})}
    for di in D["diario"].values():
        for r in di.values():
            if r.get("url"):
                cob.add(_dom(r["url"]))
    cont, exemplo = Counter(), {}
    def ver(u, peso=1):
        d = _dom(u)
        if not d or d in cob or any(d.endswith("." + c) for c in cob) or not regua(u)[0] or d in ("pncp.gov.br", "in.gov.br", "gov.br"):
            return
        cont[d] += peso; exemplo.setdefault(d, u)
    for x in D["itens"]:
        ver(x.get("link_oficial"), 2)
    for c in D["certs"].values():
        ver(c.get("link_oficial"), 2)
    for e in D["bib"].values():
        for u in (e.get("urls") or [])[:3]:
            ver(u, 1)
    lista = [{"dominio": d, "peso": n, "url": exemplo[d]} for d, n in cont.most_common(120)]
    return {"total": len(cont), "fontes": lista}


# ── 7 · PLATAFORMAS (alcance em massa) ─────────────────────────────────────────────────────────────────────────
ASSINATURAS = [("WordPress", r"/wp-content/|/wp-json/|/\?p=\d+"), ("Mapas Culturais", r"mapas?cultura|/oportunidade/\d+"),
               ("Diário municipal em lote (AGM/DOM)", r"diariomunicipal|diariooficial\.[a-z]+\.org|dom\.[a-z]+|/diario-?oficial"),
               ("Portal de transparência de fornecedor", r"transparencia|portaldatransparencia|/transparencia/"),
               ("Sistemas de editais (Prosas/Editais)", r"editais\.|/editais/|/edital/"),
               ("Querido Diário", r"queridodiario"), ("PNCP", r"pncp\.gov\.br"), ("Leis e atos (Leis Municipais)", r"leismunicipais|sapl\.")]


def a_plataformas(D: dict) -> dict:
    urls = set()
    for x in D["itens"]:
        for k in ("link_oficial", "url"):
            if x.get(k):
                urls.add(x[k])
    for e in D["bib"].values():
        urls |= set(e.get("urls") or [])
    for c in D["certs"].values():
        for d in c.get("documentos") or []:
            if d.get("url"):
                urls.add(d["url"])
    from .cartorio_leitura import regua
    plat, listas = {}, {}
    for nome, rx in ASSINATURAS:
        doms = {_dom(u) for u in urls if re.search(rx, u, re.I) and (nome in ("Mapas Culturais",) or regua(u)[0])}
        doms.discard("")
        plat[nome] = {"orgaos": len(doms), "exemplos": sorted(doms)[:6]}; listas[nome] = sorted(doms)
    try:
        (ROOT / "estado/conselho").mkdir(parents=True, exist_ok=True)
        (ROOT / "estado/conselho/plataformas.json").write_text(json.dumps(listas, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    inov = [
        {"inovacao": "Adaptador por plataforma", "o_que": "um leitor por plataforma (WordPress: /wp-json/wp/v2/posts?search=edital; Mapas Culturais: API /api/opportunity/find) em vez de um por órgão",
         "alcance": f"{plat['WordPress']['orgaos']} órgãos WordPress e {plat['Mapas Culturais']['orgaos']} instâncias de Mapas Culturais já conhecidos de uma vez"},
        {"inovacao": "Detecção de mudança barata", "o_que": "ler o sitemap.xml (lastmod) e os feeds RSS/Atom dos sites oficiais; só baixar a página quando muda",
         "alcance": "permite vigiar 10× mais fontes no mesmo tempo de execução"},
        {"inovacao": "Consulta inversa", "o_que": "frases distintivas de editais confirmados (ex.: 'Política Nacional Aldir Blanc' + 'chamamento') viram buscas por editais irmãos em outros municípios",
         "alcance": "cada edital confirmado gera pistas em dezenas de municípios que publicam o mesmo modelo"},
        {"inovacao": "Motor de fontes irmãs", "o_que": "domínios oficiais que já renderam oportunidade e nenhum motor vigia passam a ser lidos todos os dias",
         "alcance": "implantado como motor Outras Oportunidades (clones calculados para ler todas as fontes no dia)"}]
    return {"plataformas": plat, "inovacoes": inov}


# ── EXECUÇÃO E RELATÓRIO ───────────────────────────────────────────────────────────────────────────────────────
def run(gravar: bool = True) -> dict:
    D = dados()
    r = {c["id"]: f(D) for c, f in zip(CONSELHO, (a_falso_verde, a_funil, a_redundancia, a_cobertura, a_ritmo, a_fontes_irmas, a_plataformas))}
    por_motor = {}
    for mid, s in D["esq"].items():
        fal = []
        for cid in ("falso_verde", "funil", "redundancia", "ritmo"):
            for tipo, prova, conserto in (r[cid].get(mid) or {}).get("falhas") or []:
                fal.append({"conselheiro": cid, "falha": tipo, "prova": prova, "melhoria": conserto})
        por_motor[mid] = {"nome": s.get("nome"), "tipo": s.get("tipo"), "saude": s.get("saude"), "achados_total": s.get("achados_total"),
                          "valor": (r["funil"].get(mid) or {}).get("valor"), "achados_30d": (r["falso_verde"].get(mid) or {}).get("achados_30d"),
                          "cadencia": {k: (r["ritmo"].get(mid) or {}).get(k) for k in ("cadencia_atual", "cadencia_recomendada", "dia_forte")},
                          "falhas": fal}
    resumo = Counter(f["falha"] for m in por_motor.values() for f in m["falhas"])
    out = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "conselho": [{k: c[k] for k in ("id", "lente", "nome", "prompt")} for c in CONSELHO],
           "resumo": {"motores": len(por_motor), "motores_com_falha": sum(1 for m in por_motor.values() if m["falhas"]), "falhas_por_tipo": dict(resumo)},
           "cobertura": r["cobertura"], "fontes_irmas": {"total": r["fontes_irmas"]["total"], "top": r["fontes_irmas"]["fontes"][:25]},
           "plataformas": r["plataformas"], "por_motor": por_motor}
    if gravar:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        FONTES_IRMAS.parent.mkdir(parents=True, exist_ok=True)
        FONTES_IRMAS.write_text(json.dumps({"em": out["em"], "regra": "domínios oficiais que já renderam oportunidade e nenhum motor vigia (Profa. Clara)",
                                            "fontes": r["fontes_irmas"]["fontes"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def relatorio_md(out: dict) -> str:
    L = [f"# Conselho dos motores — {out['em'][:10]}", "",
         f"{out['resumo']['motores']} motores avaliados; {out['resumo']['motores_com_falha']} com pelo menos uma falha.", ""]
    L += ["## Os sete prompts", ""] + [f"**{c['nome']}** ({c['lente']})\n\n> {c['prompt']}\n" for c in out["conselho"]]
    L += ["## Falhas por tipo", ""] + [f"- {k}: {v}" for k, v in sorted(out["resumo"]["falhas_por_tipo"].items(), key=lambda kv: -kv[1])] + [""]
    C = out["cobertura"]
    L += ["## Cobertura (Dr. Otávio)", "", f"{C['fora_dos_motores_pct']}% das oportunidades vieram de fora dos motores: {C['origem_das_oportunidades']}.", ""]
    L += [f"- {u['uf']}: {u['oportunidades']} oportunidades, nenhuma de motor ({u['de_onde']})" for u in C["ufs_sem_motor_com_oportunidade"]] + [""]
    L += ["## Fontes irmãs (Profa. Clara)", "", f"{out['fontes_irmas']['total']} domínios oficiais já renderam e não têm motor. Os primeiros:", ""]
    L += [f"- {f['dominio']} (peso {f['peso']})" for f in out["fontes_irmas"]["top"]] + [""]
    L += ["## Plataformas e inovações (Dr. Fábio)", ""] + [f"- {k}: {v['orgaos']} órgãos" for k, v in out["plataformas"]["plataformas"].items()] + [""]
    L += [f"- **{i['inovacao']}** — {i['o_que']}. Alcance: {i['alcance']}." for i in out["plataformas"]["inovacoes"]] + [""]
    L += ["## Motor a motor", ""]
    for mid, m in sorted(out["por_motor"].items(), key=lambda kv: -len(kv[1]["falhas"])):
        L.append(f"### {m['nome'] or mid} (`{mid}`) — {m['valor']}, {m['achados_30d']} achados em 30 dias")
        if not m["falhas"]:
            L.append("Sem falha encontrada pelas quatro lentes motor a motor.\n"); continue
        L += [f"- **{f['falha']}** ({f['conselheiro']}): {f['prova']}. → {f['melhoria']}" for f in m["falhas"]] + [""]
    return "\n".join(L)


if __name__ == "__main__":
    o = run()
    md = relatorio_md(o)
    p = ROOT / f"docs/relatorios/conselho-motores-{o['em'][:10]}.md"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(md, encoding="utf-8")
    print(json.dumps({"resumo": o["resumo"], "cobertura": o["cobertura"]["fora_dos_motores_pct"], "fontes_irmas": o["fontes_irmas"]["total"],
                      "relatorio": str(p.relative_to(ROOT))}, ensure_ascii=False, indent=1))
