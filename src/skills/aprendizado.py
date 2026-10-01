"""SKILL · APRENDIZADO E RESULTADO (titular, 29/09) — a cada 100 ERROS, parâmetros de busca melhores.

Erro = missão sem resultado: no Interceptador, estudo 'insuficiente'/'sem_evidencia' ou voo com erro; no Espião,
avaliação com motivo de insucesso (nada no crivo, fora do objeto, página não confirma, busca vazia). A cada 100 erros
novos de um Piloto, abre um CICLO: mede onde falhou (por origem/missão, motivo, condição que faltou, erro técnico) e
grava parâmetros novos em config/parametros_pilotos.json — que os Pilotos leem na próxima missão:
  Interceptador  expressões extras para as condições que mais faltam (skill de PDF) · origens de baixo rendimento
                 (vão para o fim da fila) · ordem das rotas do site oficial pelo que funciona
  Espião         peso de cada tipo de missão pelo rendimento (o que rende 0,2% perde vagas no voo) · termos que
                 marcam 'fora do objeto' (descartados na origem)
Histórico: estado/aprendizado/ciclos.jsonl · resumo para o painel: docs/dados/aprendizado_pilotos.json
"""
from __future__ import annotations

import glob
import json
import lzma
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAR = ROOT / "config/parametros_pilotos.json"
EST = ROOT / "estado/aprendizado/estado.json"
HIST = ROOT / "estado/aprendizado/ciclos.jsonl"
PUB = ROOT / "docs/dados/aprendizado_pilotos.json"
LOTE = 100
SINONIMOS = {   # termos a acrescentar quando a condição falha muito
    "Prazo de recurso": [r"recurso[s]?\s+(?:administrativo|contra)", r"\d+\s*\(\w+\)\s*dias\s+(?:[uú]teis|corridos)[^.]{0,40}recurso", r"impugna[cç][aã]o"],
    "Resultado": [r"lista\s+(?:final\s+)?(?:de\s+)?(?:selecionad|classificad|aprovad)", r"classifica[cç][aã]o\s+final", r"resultado\s+ser[aá]\s+(?:publicado|divulgado)"],
    "Prazo de inscrição": [r"submiss[aã]o\s+(?:das\s+)?propostas", r"envio\s+(?:das\s+)?propostas", r"prazo\s+de\s+envio", r"at[eé]\s+as?\s+\d{1,2}h"],
    "Valor": [r"montante", r"aporte", r"teto\s+(?:por|de)", r"at[eé]\s+R\$"],
    "Área de atuação": [r"[aá]reas?\s+(?:de\s+)?(?:atua[cç][aã]o|tem[aá]ticas?)", r"eixos?\s+tem[aá]ticos?", r"linhas?\s+de\s+apoio"],
    "Requisitos": [r"crit[eé]rios\s+de\s+elegibilidade", r"quem\s+pode\s+participar", r"n[aã]o\s+poder[aã]o\s+participar"],
}
STOP = set(("de da do das dos e a o as os em para por com sem um uma no na nos nas que se ao aos à às edital inscrições abre abertas projetos programa 2025 2026 "
            "serve finalidade associação associações entidade entidades objeto oportunidade oportunidades social sociais terceiro setor recursos apoio "
            "página pagina texto titulo título porque sobre esta este").split())


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def parametros() -> dict:
    return _j(PAR, {})


def _erros_interceptador() -> list[dict]:
    vs = [v for f in sorted(glob.glob(str(ROOT / "estado/interceptador/relatorios/*.json"))) for v in (_j(Path(f), {}).get("voos") or [])]
    return [v for v in vs if v.get("erro") or v.get("qualidade") in ("insuficiente", "sem_evidencia")], vs


def _erros_espiao() -> tuple[list[dict], list[dict]]:
    av = []
    for f in glob.glob(str(ROOT / "estado/piloto/aprendizados/avaliacoes/*.json")):
        a = _j(Path(f), None)
        if a:
            av.append(a)
    for f in glob.glob(str(ROOT / "estado/piloto/aprendizados/avaliacoes/arquivo-*.jsonl.xz")):
        try:
            av += [json.loads(l).get("avaliacao") or {} for l in lzma.decompress(Path(f).read_bytes()).decode().splitlines() if l.strip()]
        except Exception:
            pass
    av.sort(key=lambda a: str(a.get("em") or ""))
    return [a for a in av if a.get("motivo_do_insucesso")], av


PLACEHOLDER = re.compile(r"(?i)a pergunta que orienta|o buraco que vejo|pergunta de pesquisa|exemplo de pergunta|<[^>]+>")


def _cons(a: dict) -> str | None:
    c = a.get("consulta")
    if not c:
        m = re.search(r"'([^']{6,140})'", str(a.get("licao_do_voo") or ""))
        c = m.group(1) if m else None
    return re.sub(r"\s+", " ", c).strip().lower() if c else None


def aprender_consultas() -> dict:
    """APRENDIZADO DAS BUSCAS (titular, 30/09) — a cada pouso: cada consulta feita pelo Espião (recuperada até das
    missões antigas, pelo texto da lição), quantas vezes foi tentada, quantas deram resultado e quantos achados; e os
    TERMOS que mais aparecem nas buscas que funcionam e nas que falham. Vira parâmetro: o Espião repete o que funciona,
    abandona o que falha 3 vezes sem nada e evita os termos das buscas ruins."""
    _, av = _erros_espiao()
    _pe0 = (parametros().get("espiao") or {})
    from datetime import timedelta as _td
    _desde = (datetime.now(timezone.utc) - _td(days=int(_pe0.get("janela_aprendizado_dias", 7)))).isoformat()
    _nao_pune = set(_pe0.get("motivos_que_nao_punem_a_consulta") or ["busca_vazia", "busca_bloqueada", "sem_texto"])
    av = [a for a in av if str(a.get("em") or "") >= _desde and (int(a.get("uteis") or 0) > 0 or a.get("motivo_do_insucesso") not in _nao_pune)]
    por = {}                                   # 01/10: só os últimos dias; bloqueio do buscador não reprova a consulta
    for a in av:
        c = _cons(a)
        if not c or PLACEHOLDER.search(c):
            continue
        p = por.setdefault(c, {"tentativas": 0, "com_resultado": 0, "achados": 0, "missao": a.get("missao"), "motivos": Counter()})
        p["tentativas"] += 1; u = int(a.get("uteis") or 0)
        if u:
            p["com_resultado"] += 1; p["achados"] += u
        else:
            p["motivos"][a.get("motivo_do_insucesso") or "—"] += 1
    boas = sorted([(c, p) for c, p in por.items() if p["com_resultado"]], key=lambda kv: (-kv[1]["com_resultado"] / kv[1]["tentativas"], -kv[1]["achados"]))
    # reprovação só conta tentativas depois de 'reprovas_desde' (01/10: o período do bloqueio do buscador não reprova)
    _rd = str(_pe0.get("reprovas_desde") or "")
    _tent_validas = Counter(_cons(a) for a in av if str(a.get("em") or "") >= _rd and not int(a.get("uteis") or 0))
    ruins = [(c, p) for c, p in por.items() if _tent_validas.get(c, 0) >= int(_pe0.get("minimo_tentativas_para_reprovar", 3)) and not p["com_resultado"]]
    tb, tr = Counter(), Counter()
    for c, p in por.items():
        for w in set(re.findall(r"[a-zà-ú]{4,}", c)) - STOP:
            (tb if p["com_resultado"] else tr)[w] += 1
    termos_bons = [w for w, n in tb.most_common(40) if n >= 2 and tb[w] > tr.get(w, 0)][:15]
    termos_ruins = [w for w, n in tr.most_common(60) if n >= 3 and not tb.get(w)][:15]
    rend = defaultdict(lambda: [0, 0])
    for c, p in por.items():
        r = rend[str(p["missao"])]; r[0] += p["tentativas"]; r[1] += p["com_resultado"]
    P = parametros(); pe = P.setdefault("espiao", {})
    pe["consultas_boas"] = [{"consulta": c, "tentativas": p["tentativas"], "com_resultado": p["com_resultado"], "achados": p["achados"], "missao": p["missao"]} for c, p in boas[:20]]
    pe["consultas_ruins"] = [{"consulta": c, "tentativas": p["tentativas"], "motivo": p["motivos"].most_common(1)[0][0] if p["motivos"] else "—", "missao": p["missao"]} for c, p in ruins[:40]]
    pe["termos_bons"] = termos_bons; pe["termos_ruins"] = termos_ruins
    pe["rendimento_das_buscas"] = {m: {"tentativas": r[0], "com_resultado": r[1], "taxa": round(r[1] / r[0], 3) if r[0] else 0} for m, r in rend.items()}
    pe["consultas_aprendidas_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    PAR.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"consultas": len(por), "boas": len(boas), "ruins": len(ruins), "termos_bons": termos_bons[:6], "termos_ruins": termos_ruins[:6]}


def ciclo(forcar: bool = False) -> dict:
    E = _j(EST, {}); P = parametros(); feitos = []
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # ── INTERCEPTADOR
    ei, ti = _erros_interceptador()
    novos = len(ei) - int(E.get("interceptador_erros_vistos", 0))
    if novos >= LOTE or (forcar and ei):
        lote = ei[-LOTE:]
        falta = Counter(k for v in lote for k in (v.get("nao_resolvidos") or []))
        por_origem = Counter(str(v.get("de") or "—") for v in ti)
        ok_origem = Counter(str(v.get("de") or "—") for v in ti if v.get("qualidade") in ("validada", "parcial", "fonte_confirmada"))
        baixo = sorted([o for o, n in por_origem.items() if n >= 15 and ok_origem[o] / n < 0.25], key=lambda o: ok_origem[o] / por_origem[o])
        tecnicos = Counter(str(v.get("erro"))[:60] for v in lote if v.get("erro"))
        rotas = (_j(ROOT / "estado/interceptador/sites_oficiais.json", {}) or {}).get("rotas_que_funcionam") or {}
        pi = P.setdefault("interceptador", {})
        pi["expressoes_extras"] = {c: SINONIMOS[c] for c, _ in falta.most_common(3) if c in SINONIMOS}
        pi["origens_baixo_rendimento"] = baixo
        pi["rotas_ordem"] = [r for r, _ in sorted(rotas.items(), key=lambda kv: -kv[1])]
        diag = {"piloto": "interceptador", "em": agora, "erros_no_lote": len(lote), "condicoes_que_mais_faltam": falta.most_common(6),
                "erros_tecnicos": tecnicos.most_common(4), "origens_baixo_rendimento": [(o, f"{ok_origem[o]}/{por_origem[o]}") for o in baixo],
                "parametros_novos": {k: pi[k] for k in ("expressoes_extras", "origens_baixo_rendimento", "rotas_ordem")},
                "onde_falha": ("condições do cronograma (recurso/resultado/inscrição) não achadas no texto — expressões ampliadas" if falta else "") +
                              (f"; origens com rendimento < 25%: {', '.join(baixo)} — vão para o fim da fila" if baixo else "")}
        feitos.append(diag); E["interceptador_erros_vistos"] = len(ei)
    # ── ESPIÃO
    ee, ta = _erros_espiao()
    novos = len(ee) - int(E.get("espiao_erros_vistos", 0))
    if novos >= LOTE or (forcar and ee):
        lote = ee[-max(LOTE, 1000):]
        tipos = Counter(str(a.get("missao") or a.get("tipo") or "—") for a in ta[-5000:])
        rend = Counter(str(a.get("missao") or a.get("tipo") or "—") for a in ta[-5000:] if not a.get("motivo_do_insucesso"))
        pesos = {t: round(max(0.1, min(1.0, (rend[t] / n) / 0.02)), 2) for t, n in tipos.items() if n >= 30}
        motivos = Counter(a.get("motivo_do_insucesso") for a in lote)
        palavras = Counter(w for a in lote if a.get("motivo_do_insucesso") == "fora_do_objeto"
                           for d in (a.get("alvo"),) for w in re.findall(r"[a-zà-ú]{5,}", str(d or "").lower())
                           if w not in STOP)
        pe = P.setdefault("espiao", {})
        pe["pesos_missao"] = pesos
        pe["termos_fora_do_objeto"] = [w for w, n in palavras.most_common(20) if n >= 5]
        diag = {"piloto": "espiao", "em": agora, "erros_no_lote": len(lote), "motivos": motivos.most_common(5),
                "rendimento_por_missao": {t: f"{rend[t]}/{n}" for t, n in tipos.most_common(8)}, "parametros_novos": {k: pe[k] for k in ("pesos_missao", "termos_fora_do_objeto")},
                "onde_falha": "missões que quase nunca rendem (" + ", ".join(t for t, p in pesos.items() if p <= 0.2) + ") perdem vagas; termos de 'fora do objeto' descartados na origem"}
        feitos.append(diag); E["espiao_erros_vistos"] = len(ee)
    if feitos:
        P["atualizado_em"] = agora; P["regra"] = __doc__.split("Histórico:")[0].strip()
        PAR.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
        HIST.parent.mkdir(parents=True, exist_ok=True)
        with HIST.open("a", encoding="utf-8") as fh:
            for d in feitos:
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    try:
        _cc = ciclo_criativo()                # 01/10: a cada 100 pesquisas, estratégia nova (sem regra fixa)
    except Exception as ex:
        _cc = {"erro": type(ex).__name__}
    try:
        _cq = aprender_consultas()            # a cada pouso — não espera 100 erros
    except Exception as ex:
        _cq = {"erro": type(ex).__name__}
    EST.parent.mkdir(parents=True, exist_ok=True); EST.write_text(json.dumps(E, ensure_ascii=False, indent=1), encoding="utf-8")
    PUB.write_text(json.dumps({"em": agora, "lote": LOTE, "estado": E, "ultimos_ciclos": [json.loads(l) for l in HIST.read_text(encoding="utf-8").splitlines()[-6:]] if HIST.exists() else [],
                               "parametros": P}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ciclos_abertos": [d["piloto"] for d in feitos], "erros_interceptador": len(ei), "erros_espiao": len(ee), "consultas": _cq}


if __name__ == "__main__":
    import sys
    print(json.dumps(ciclo("--forcar" in sys.argv), ensure_ascii=False, indent=1))


# ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# CICLO CRIATIVO A CADA 100 PESQUISAS (titular, 01/10) — sem regra fixa de busca. A cada 100 pesquisas de um Piloto, a
# estratégia é TROCADA por outra, gerada por sorteio e nunca repetida; o resultado de cada estratégia é medido e o
# que funcionou ganha peso na seguinte. FIXO, só o NEGATIVO: config/parametros_pilotos.json › <piloto> › restricoes_fixas.
# ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
RECURSOS = ["edital", "chamada pública", "prêmio", "seleção de projetos", "fundo", "patrocínio", "doação", "bolsa", "termo de fomento",
            "chamamento público", "programa de apoio", "investimento social", "incentivo fiscal", "financiamento de projetos"]
AREAS = ["assistência social", "criança e adolescente", "pessoa idosa", "cultura", "saúde", "esporte", "educação", "inclusão",
         "segurança alimentar", "pessoa com deficiência", "juventude", "mulheres", "voluntariado", "direitos humanos"]
LUGARES = ["Goiás", "Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Senador Canedo", "Trindade", "Catalão", "Itumbiara",
           "Centro-Oeste", "Brasil", "nacional"]
MOLDES = ["{recurso} {area} {lugar} {ano}", "\"{recurso}\" \"organizações da sociedade civil\" {area} {lugar}", "{quem} {recurso} {area}",
          "{recurso} para associações {area} inscrições {ano}", "{quem} abre {recurso} {lugar}", "{area} {recurso} entidades sem fins lucrativos {lugar}",
          "{recurso} {area} OSC {ano} inscrições abertas", "como inscrever associação {recurso} {quem}"]


def _proibido(q: str, rf: dict) -> bool:
    ql = q.lower()
    return ql in {c.lower() for c in (rf.get("consultas_proibidas") or [])} or any(t in ql for t in (rf.get("termos_proibidos") or []))


def _nova_estrategia_espiao(pe: dict, hist: list) -> dict:
    import random
    semente = int(datetime.now(timezone.utc).timestamp())
    rnd = random.Random(semente)
    rf = pe.get("restricoes_fixas") or {}
    pesos = Counter()                                    # elementos das estratégias que deram resultado ganham peso
    for h in hist:
        if h.get("taxa", 0) > 0:
            for e in h.get("elementos_bons") or []:
                pesos[e] += 1
    cat = _j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}).get("motores") or []
    quem = [re.sub(r"\s+", " ", str(x.get("orgao")))[:40] for x in cat if x.get("orgao") and (x.get("livro") or {}).get("checklist")
            and x.get("geo") in ("GO", "BR") and len(str(x.get("orgao"))) < 45 and not re.search(r"(?i)munic[ií]pio|prefeitura|secretaria", str(x.get("orgao")))]
    quem = sorted(set(quem)) or ["instituto empresarial", "fundação empresarial"]
    usadas = {c for h in hist for c in (h.get("pool") or [])}
    ano = str(date.today().year)
    escolhe = lambda L: rnd.choices(L, weights=[1 + 2 * pesos.get(x, 0) for x in L])[0]
    pool, tent = [], 0
    while len(pool) < 14 and tent < 400:
        tent += 1
        q = rnd.choice(MOLDES).format(recurso=escolhe(RECURSOS), area=escolhe(AREAS), lugar=escolhe(LUGARES), quem=rnd.choice(quem), ano=ano)
        q = re.sub(r"\s+", " ", q).strip()
        if q.lower() not in usadas and q not in pool and not _proibido(q, rf):
            pool.append(q)
    return {"id": f"E{len(hist) + 1:03d}", "criada_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "semente": semente, "pool": pool,
            "pesquisas_no_inicio": None}


def ciclo_criativo() -> dict:
    """A cada 100 pesquisas, uma estratégia nova para cada Piloto (sem regra fixa); mede a anterior."""
    import random
    P = parametros(); feito = {}
    # ── ESPIÃO: pesquisas = avaliações de missão desde o reset
    _, av = _erros_espiao()
    pe = P.setdefault("espiao", {}); est = pe.get("estrategia_criativa"); hist = pe.setdefault("estrategias_anteriores", [])
    n = len(av)
    if not est or n - int(est.get("pesquisas_no_inicio") or 0) >= 100:
        if est:                                          # mede a estratégia que termina
            lote = av[int(est.get("pesquisas_no_inicio") or 0):]
            ok = [a for a in lote if int(a.get("uteis") or 0) > 0]
            bons = {w for a in ok for w in re.findall(r"[a-zà-ú]{4,}", str(_cons(a) or ""))}
            elems = [e for e in RECURSOS + AREAS + LUGARES if any(w in e.lower() for w in bons)]
            hist.append({"id": est["id"], "pesquisas": len(lote), "com_resultado": len(ok), "taxa": round(len(ok) / max(1, len(lote)), 3),
                         "elementos_bons": elems[:12], "pool": est.get("pool", [])})
            pe["estrategias_anteriores"] = hist[-30:]
        est = _nova_estrategia_espiao(pe, hist); est["pesquisas_no_inicio"] = n
        pe["estrategia_criativa"] = est; feito["espiao"] = est["id"]
    # 01/10: a estratégia em uso é sempre conferida contra as restrições fixas (um voo antigo gerou uma sem elas)
    _rf = pe.get("restricoes_fixas") or {}
    _limpo = [q for q in (est.get("pool") or []) if not _proibido(q, _rf)]
    if len(_limpo) != len(est.get("pool") or []):
        if len(_limpo) < 8:
            _n0 = est.get("pesquisas_no_inicio"); est = _nova_estrategia_espiao(pe, hist); est["pesquisas_no_inicio"] = _n0
            pe["estrategia_criativa"] = est; feito["espiao"] = est["id"] + " (refeita: havia consulta proibida)"
        else:
            est["pool"] = _limpo; pe["estrategia_criativa"] = est
    # ── INTERCEPTADOR: pesquisas = estudos desde o reset
    vs = [v for f in sorted(glob.glob(str(ROOT / "estado/interceptador/relatorios/*.json"))) for v in (_j(Path(f), {}).get("voos") or [])]
    pi = P.setdefault("interceptador", {}); ei = pi.get("estrategia_criativa"); hi = pi.setdefault("estrategias_anteriores", [])
    m = len(vs)
    if not ei or m - int(ei.get("pesquisas_no_inicio") or 0) >= 100:
        if ei:
            lote = vs[int(ei.get("pesquisas_no_inicio") or 0):]
            ok = sum(1 for v in lote if v.get("qualidade") in ("validada", "parcial", "fonte_confirmada"))
            hi.append({"id": ei["id"], "estudos": len(lote), "com_resultado": ok, "taxa": round(ok / max(1, len(lote)), 3),
                       "rotas": ei.get("rotas"), "foco_area": ei.get("foco_area")}); pi["estrategias_anteriores"] = hi[-30:]
        rnd = random.Random(int(datetime.now(timezone.utc).timestamp()))
        rotas = list((pi.get("rotas_ordem") or ["financiador_regulamento", "site_do_financiador", "financiador_programa_edital", "link_da_noticia_para_o_financiador"]))
        melhor = max(hi, key=lambda h: h.get("taxa", 0)) if hi else None
        rnd.shuffle(rotas)
        if melhor and melhor.get("rotas") and rnd.random() < 0.5:
            rotas = melhor["rotas"][:1] + [r for r in rotas if r != melhor["rotas"][0]]   # metade das vezes, parte da melhor
        ei = {"id": f"I{len(hi) + 1:03d}", "criada_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rotas": rotas,
              "foco_area": rnd.choice(AREAS[:8]), "pesquisas_no_inicio": m}
        pi["estrategia_criativa"] = ei; pi["rotas_ordem"] = rotas; feito["interceptador"] = ei["id"]
    PAR.write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
    return feito or {"sem_troca": True}
