"""FLUXO DAS OPORTUNIDADES (titular, 27/09) — do que é encontrado ao mapa, ao calendário e à previsão.

    1. ENCONTRADAS   tudo o que os motores, o Espião e o Interceptador trouxeram
                     (arquivo mestre · candidatas do Espião · registros estudados pelo Interceptador)
    2. ÚNICAS        a mesma oportunidade conta uma vez (endereço e título normalizados)
    3. POSSÍVEIS     abertas ou possivelmente abertas: prazo ainda não vencido, ou sem prazo e publicada nos
                     últimos 60 dias — mesmo sem informação nenhuma (menção em diário oficial conta)
    4. CONFIRMADAS   com o MÍNIMO: objeto + data-limite de inscrição ainda aberta + link do site oficial
                     (de empresa, instituto ou ente público)
    5. OPRESSOR      oportunidade nova (não coberta por opressor existente) gera um livro de oportunidade próprio,
                     ligado por 30 dias, com a página dela — e o Interceptador a lê (5ª fila)
    6. PREDITIVO     cada oportunidade é cadastrada em biblioteca_alexandria/base/preditivo/oportunidades.jsonl
                     com órgão, tipo (pontual/recorrente), prazo e próxima janela estimada

Publica docs/dados/fluxo_oportunidades.json: etapas, números do mapa por estado (1º número = confirmadas,
2º = possíveis) e os prazos para o calendário. Roda no monitoramento diário e ao fim de cada voo do Interceptador.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MESTRE = ROOT / "dados/oportunidades/oportunidades.jsonl"
EXT = ROOT / "dados/editais/extraidos"
CAT_OPR = ROOT / "biblioteca_alexandria/fontes/motores.json"
EST_OPR = ROOT / "estado/opressores.json"
PRED = ROOT / "biblioteca_alexandria/base/preditivo/oportunidades.jsonl"
SAIDA = ROOT / "docs/dados/fluxo_oportunidades.json"
AGREGADORES = re.compile(r"duckduckgo|bing\.com|google\.|queridodiario|captadores\.org|observatorio3setor|prosas\.com|filantropia\.ong|gife\.org|idis\.org|pncp\.gov\.br/app", re.I)
CHECKLIST = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera",
             "Requisitos", "Anexos", "Destinação", "Área de atuação"]
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _d(*v) -> str | None:
    for x in v:
        s = str(x or "")[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}$", s):
            return s
    return None


def _nt(t: str) -> str:
    t = re.sub(r"(?i)^continue lendo\s+", "", str(t or ""))
    t = unicodedata.normalize("NFKD", t.lower()); t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t)[:70]


def _nu(u: str) -> str:
    p = urlsplit(str(u or "")); return ((p.hostname or "").replace("www.", "") + p.path.rstrip("/")).lower()


def _oficial(*us) -> str | None:
    from .sites_oficiais import e_republicador       # catálogo de republicadores (config/republicadores.json)
    for u in us:
        if isinstance(u, str) and u.startswith("http") and not AGREGADORES.search(u) and not e_republicador(u):
            return u
    return None


def _registro_ext(eid: str) -> dict:
    return _j(EXT / f"{eid}.json", {}) if eid else {}


TRIAGEM: dict = {}


def _orgao_real(m: dict, e: dict) -> str | None:
    """28/09: o 'órgão' gravado costuma ser o site que REPUBLICOU (IDIS, Observatório do 3º Setor, ABCR...). Vale o
    financiador lido pelo Interceptador; senão o órgão gravado, se não for republicador; senão nada."""
    fin = ((e.get("busca_do_oficial") or {}).get("financiador") or "").strip()
    if fin:
        return fin
    o = (m.get("orgao") or e.get("orgao") or "").strip()
    if re.search(r"(?i)idis|observat[oó]rio|captadores|abcr|filantropia|gife|prosas|piloto|espi[aã]o|interceptador|querido di[aá]rio|not[ií]cia", o):
        return None
    return o or None


AREAS = [("emendas", r"emenda parlamentar"),
         ("cultura", r"cultur|art[ií]st|\barte\b|artes|pnab|aldir|rouanet|cinema|m[uú]sica|teatro|patrim[oô]nio|leitura|audiovis|dan[cç]a|festival|museu|biblioteca|circo|artesan"),
         ("esporte", r"esport|atleta|lazer|olimp|paral[ií]mp|futebol|jogos"),
         ("saude", r"sa[uú]de|hospital|pronon|pronas|m[eé]dic|sus\b|oncol|defici[eê]ncia|reabilita|autis|tgd|intelectual"),
         ("crianca", r"crian[cç]a|adolesc|inf[aâ]ncia|\bfia\b|juventude|jovens|\beca\b|conanda|cmdca|socioeducativ|primeira inf[aâ]ncia|creche"),
         ("idoso", r"idos|envelhec|longevid|pessoa idosa"),
         ("assistencia", r"assist[eê]ncia social|vulnerab|alimentar|nutricional|filantr[oó]p|pobreza|fome|perif[eé]ri|suas\b|acolhimento|popula[cç][aã]o de rua|mulher|g[eê]nero|direitos humanos|cras|creas|servi[cç]os? de conviv|fortalecimento de v[ií]nculos|prote[cç][aã]o social|pcd|pessoa com defici"),
         ("ambiente", r"ambient|clima|sustent|floresta|[aá]gua|amaz[oô]n|energ|reciclag|biodivers|res[ií]duo"),
         ("educacao", r"educa|escola|ensino|alfabetiz|forma[cç][aã]o|capacita|bolsa")]


def area_tematica(*textos: str) -> str | None:
    """28/09: o tema da oportunidade, pela primeira fonte que o diga (Área de atuação comprovada, objeto, título...)."""
    for tx in textos:
        for k, rx in AREAS:
            if tx and re.search(rx, tx, re.I):
                return k
    return None


def consolidar() -> list[dict]:
    hoje = date.today(); lim = (hoje - timedelta(days=60)).isoformat()
    brutos = []
    for l in MESTRE.open(encoding="utf-8") if MESTRE.exists() else []:
        if not l.strip():
            continue
        m = json.loads(l)
        if m.get("estado_export") in ("arquivado", "excluido"):
            continue
        brutos.append(("motor " + str(m.get("fonte_id") or m.get("fonte_nome") or ""), m))
    for c in (_j(ROOT / "estado/piloto/candidatas_do_catalogo.json", {}).get("candidatas") or []):
        cid = "cat-" + hashlib.sha1(c["url"].encode()).hexdigest()[:12]
        brutos.append(("Piloto - Espião", {"id": cid, "titulo": c.get("titulo"), "url": c.get("url"), "orgao": c.get("visto_em"),
                                            "descoberto_em": c.get("descoberto_em"), "fonte_id": "piloto-espiao", "enquadramento": c.get("enquadramento")}))
    # EMENDAS PARLAMENTARES NO FLUXO (titular, 28/09): a captação de emendas (federal, estadual de Goiás e municipal de
    # Goiânia) abre todo ano em 01/10 e vai a 30/11 (config/emendas.json). Ficavam só no conjunto antigo do painel e
    # sumiram do Radar, do mapa e dos calendários quando eles passaram a ler o fluxo validado. Voltam, a cada ano.
    try:
        _dd = (ROOT / "docs/dashboard-dados.js").read_text(encoding="utf-8")
        _D = json.loads(_dd[_dd.index("{"):_dd.rindex("}") + 1])
        for em in (_D.get("editais") or []):
            if em.get("area") == "emendas_parlamentares" and em.get("fim"):
                _u = em.get("url") or ""
                if "dadosabertos.camara.leg.br/api" in _u:      # endereço de API não é página para a entidade abrir
                    _u = "https://www.camara.leg.br/deputados/quem-sao"
                brutos.append(("calendário legislativo · emendas", {"id": em["id"], "titulo": em.get("titulo"), "url": _u,
                               "orgao": em.get("orgao") or em.get("fonte_nome"), "uf": em.get("uf"), "objeto": em.get("objeto"),
                               "fim": em.get("fim"), "inicio": em.get("inicio"), "data_publicacao": em.get("inicio"),
                               "fonte_id": em.get("fonte_id"), "nivel": em.get("nivel"), "_emenda": True}))
    except Exception:
        pass
    # MOTOR AGREGADORES NO FLUXO (28/09): capitaai, farolcultural, IDIS — indícios com o link da fonte oficial
    for ag in (_j(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens", []):
        brutos.append((f"motor agregadores · {ag.get('fonte')}", {"id": ag["id"], "titulo": ag.get("titulo"), "url": ag.get("link_oficial") or ag.get("pagina_agregador"),
                       # 29/09: prazo de agregador NÃO é prazo (regra do titular) — fica como pista até a fonte oficial confirmar
                       "fim": None, "prazo_agregador": ag.get("prazo"), "uf": ag.get("uf"), "data_publicacao": ag.get("primeiro_visto"), "fonte_id": "motor-agregadores",
                       "pagina_agregador": ag.get("pagina_agregador"), "areas_fonte": ["cultura"] if ag.get("fonte") == "farolcultural" else []}))
    for arq in EXT.glob("*.json"):
        e = _j(arq, {})
        if e.get("investigacao_ia") and arq.stem.startswith(("cat-", "op-")):
            brutos.append(("Piloto - Interceptador", {"id": arq.stem, "titulo": e.get("titulo"), "url": e.get("url"), "orgao": e.get("orgao"),
                                                      "descoberto_em": str((e.get("investigacao_ia") or {}).get("em", ""))[:10], "fonte_id": "piloto-interceptador"}))
    # NÃO É OPORTUNIDADE (27/09): pauta legislativa, assembleia, contrato já assinado, resultado e lista de aprovados.
    # Retificação e alteração de cronograma FICAM: indicam edital aberto.
    RUIDO = re.compile(r"^\s*\d{1,2}:\d{2}\b|vota[cç][õo]es|requerimentos|t[ií]tulos? de cidadania|utilidades? p[uú]blica|convoca[cç][aã]o de assembleia|"
                       r"^\s*extrato|resultado|lista de aprovados|aprovados e suplentes|heteroidentifica|homologa|inexigibilidade|dispensa de chamamento|termo aditivo", re.I)
    _IDX = (_j(ROOT / "estado/opressores_indice.json", {}) or {}).get("indice") or {}
    _OPR = {x.get("id"): x for x in (_j(CAT_OPR, {}) or {}).get("motores", [])}
    vistos_t, vistos_u, out = set(), set(), []
    # VALIDAÇÃO INDIVIDUAL (27/09): decisão registrada prevalece; o que não foi validado passa pelas regras aprendidas
    from . import validacao_mapa as _vm
    VAL = _vm.carregar(); HER = _vm.indice_heranca(VAL)
    ARQ = _j(ROOT / "dados/editais/arquivados.json", {})
    TRIAGEM.clear(); TRIAGEM.update({"saiu_por_validacao": 0, "saiu_por_arquivo": 0, "dispensado_pela_regra": 0, "regras": {}})
    for origem, m in brutos:
        tit = re.sub(r"\s+", " ", str(m.get("titulo") or "")).strip()
        if not tit or RUIDO.search(tit):
            continue
        v = VAL.get(m.get("id"))
        if not v:
            h = _vm.herdada(m, HER)
            if h and h["decisao"] in _vm.SAEM_DO_MAPA:
                TRIAGEM["herdou_decisao"] = TRIAGEM.get("herdou_decisao", 0) + 1; continue
        if v and v["decisao"] in _vm.SAEM_DO_MAPA:
            TRIAGEM["saiu_por_validacao"] += 1; continue
        if m.get("id") in ARQ:
            TRIAGEM["saiu_por_arquivo"] += 1; continue          # exclusão sistêmica (dashboard ou validação)
        e = _registro_ext(m.get("id"))
        ve = e.get("verificacao_externa") if isinstance(e.get("verificacao_externa"), dict) else {}
        inv = e.get("investigacao_ia") or {}; campos = inv.get("campos") or {}
        val = e.get("validacao") if isinstance(e.get("validacao"), dict) else {}
        pub = _d(m.get("data_publicacao"), m.get("descoberto_em"), m.get("coletado_em"))
        fim = _d(e.get("fim"), ve.get("prazo"), val.get("prazo_valor"), m.get("fim"))
        if m.get("_emenda"):
            e = {**e, "inicio": m.get("inicio")}
        link = _oficial(ve.get("pagina_oficial"), e.get("pagina_oficial"), val.get("site"), m.get("url"))
        objeto = m.get("objeto") or e.get("objeto") or ((campos.get("Objeto") or {}).get("valor") if (campos.get("Objeto") or {}).get("comprovado") else None)
        if v and v["decisao"] in ("valida_aberta", "valida_fora_abrangencia") and v.get("fonte_oficial"):
            fim = v.get("prazo") or fim; link = v["fonte_oficial"]; objeto = v.get("objeto") or objeto
        diario = bool(re.match(r"(?i)di[aá]rio oficial", tit))
        # 3. possível: prazo não vencido, ou sem prazo e publicada nos últimos 60 dias
        possivel = (fim and fim >= hoje.isoformat()) or (not fim and pub and pub >= lim)
        if not possivel:
            continue
        if not v:                                            # regra aprendida só conta o que ainda estaria no mapa
            dsp = _vm.dispensa(origem, m, "menção em diário oficial" if diario else None)
            if dsp:
                TRIAGEM["dispensado_pela_regra"] += 1; TRIAGEM["regras"][dsp["regra"]] = TRIAGEM["regras"].get(dsp["regra"], 0) + 1
                continue
        kt, ku = _nt(tit), _nu(m.get("url"))
        if (kt and kt in vistos_t) or (ku and ku in vistos_u and not diario):
            continue
        vistos_t.add(kt); vistos_u.add(ku)
        uf = str(m.get("uf") or e.get("uf") or (v or {}).get("uf") or "").upper()
        if uf not in UFS:                                  # 30/09: sem estado registrado, deduz do domínio oficial ou do motor goiano
            _h = (urlsplit(str(link or m.get("url") or "")).hostname or "").lower()
            _f = str(m.get("fonte_id") or m.get("motor") or origem or "").lower()
            if _h in ("goias.gov.br", "www.goias.gov.br") or _h.endswith(".go.gov.br") or _h.endswith(".go.leg.br") \
               or any(k in _f for k in ("secult-go", "goias", "do-goiania", "go-")):
                uf = "GO"
        if m.get("_emenda") and m.get("nivel") == "federal":
            uf = ""
        # fluxo contínuo: o próprio edital dispensa a data-limite (validação no site oficial) — vale como prazo aberto
        prazo_disp = bool(v and v["decisao"].startswith("valida") and ((v.get("doze_itens") or {}).get("Prazo de inscrição") or {}).get("status") == "dispensado pelo edital")
        confirmada = bool(objeto and link and ((fim and fim >= hoje.isoformat()) or (prazo_disp and not fim)))
        # CONDIÇÕES E OPRESSOR DE CADA OPORTUNIDADE (28/09)
        _cp = [k for k, c in campos.items() if (c or {}).get("comprovado")]; _dp = [k for k, c in campos.items() if (c or {}).get("dispensado")]
        condicoes = {"comprovadas": len(_cp), "dispensadas": len(_dp), "faltam": [k for k in campos if k not in _cp and k not in _dp],
                     "dispensas": {k: str((campos[k] or {}).get("trecho_dispensa") or "")[:120] for k in _dp}} if campos else None
        # CHECKLIST DOS 12 ITENS (28/09): a situação de CADA item — ok (comprovado com trecho), disp (dispensado pelo edital),
        # val (confirmado na validação individual), falta (estudado e não achado), pend (ainda não estudado)
        _vv = v or {}
        _val_ok = {"Objeto": objeto, "Prazo de inscrição": fim or (_vv.get("prazo_dispensado") and "fluxo contínuo"),
                   "Órgão / financiador": _vv.get("orgao") or _vv.get("financiador"), "Valor": _vv.get("valor"),
                   "Território": _vv.get("uf") or _vv.get("territorio"), "Requisitos": _vv.get("requisitos")} if (_vv.get("decisao") or "").startswith("valida") else {}
        checklist = {}
        for k in CHECKLIST:
            c = (campos or {}).get(k) or {}
            if c.get("comprovado"):
                checklist[k] = {"s": "ok", "v": str(c.get("valor") or "")[:90], "t": str(c.get("trecho") or "")[:160]}
            elif c.get("dispensado"):
                checklist[k] = {"s": "disp", "v": "dispensado pelo edital", "t": str(c.get("trecho_dispensa") or "")[:160]}
            elif _val_ok.get(k):
                checklist[k] = {"s": "val", "v": str(_val_ok[k])[:90]}
            elif campos:
                checklist[k] = {"s": "falta"}
            elif m.get("_emenda"):
                # EMENDA (28/09): não há edital — o calendário legislativo (config/emendas.json) diz o que se sabe; o resto não se aplica
                _em = {"Objeto": (str(objeto or "")[:90], "val"), "Prazo de inscrição": (f"{m.get('inicio')} a {fim}", "val"),
                       "Órgão / financiador": (str(m.get("orgao") or "casa legislativa")[:90], "val"), "Território": ("nacional" if m.get("nivel") == "federal" else "Goiás", "val"),
                       "Esfera": (str(m.get("nivel") or ""), "val"), "Área de atuação": ("qualquer área de atuação da entidade", "val"),
                       "Requisitos": ("entidade regular: CNPJ, certidões e cadastro na casa legislativa", "val"),
                       "Valor": ("definido pelo parlamentar", "disp"), "Destinação": ("definida pelo parlamentar na indicação", "disp"),
                       "Resultado": ("não há edital: indicação do parlamentar", "disp"), "Prazo de recurso": ("não há edital nem recurso", "disp"),
                       "Anexos": ("não há edital: ofício e plano de trabalho da entidade", "disp")}
                vv, ss = _em.get(k, ("", "pend")); checklist[k] = {"s": ss, "v": vv}
            else:
                checklist[k] = {"s": "pend"}
        _ix = _IDX.get(m.get("id")) or {}
        if v and (v["decisao"] == "pendente" or (v["decisao"].startswith("valida") and not v.get("fonte_oficial"))):
            confirmada = False                                # a validação não achou a fonte oficial: não confirma (29/09: nem prazo de outra origem)
        insp = None
        if inv.get("em"):
            po = e.get("pagina_oficial")
            from .sites_oficiais import e_republicador as _rep
            po_ok = bool(po and not _rep(po))
            insp = {"em": str(inv.get("em"))[:16], "qualidade": inv.get("qualidade"), "comprovados": inv.get("comprovados"),
                    "prazo": fim, "pagina_oficial": po if po_ok else None,
                    "ok": bool(fim and po_ok)}          # verde = achou prazo E site oficial; vermelho = não achou
        out.append({"id": m.get("id"), "titulo": re.sub(r"(?i)^continue lendo\s+", "", tit)[:180], "orgao": _orgao_real(m, e),
                    "uf": uf if uf in UFS else None, "origem": origem, "tipo": "menção em diário oficial" if diario else ("empresa/instituto" if (m.get("nivel") in ("privada", "privado") or origem.startswith("Piloto")) else "ente público"),
                    "publicado_em": pub, "inicio": _d(e.get("inicio"), ve.get("inicio"), m.get("inicio") if m.get("_emenda") else None), "fim": fim, "link_oficial": link,
                    "objeto": str(objeto)[:240] if objeto else None, "confirmada": confirmada, "url": m.get("url"), "inspecao": insp, "condicoes": condicoes, "checklist": checklist,
                    "area": area_tematica(((checklist.get("Área de atuação") or {}).get("v") or ""), str(objeto or ""), tit, str(m.get("orgao") or ""),
                                          " ".join(m.get("areas_fonte") or []) if isinstance(m.get("areas_fonte"), list) else str(m.get("areas_fonte") or ""))
                            or ("diario" if diario else None), "opressor": _ix.get("opressor"), "opressor_dispensa": _ix.get("dispensa"),
                    "opressor_edicoes": len((_OPR.get(_ix.get("opressor")) or {}).get("historico") or []) or None,
                    "opressor_previsao": (_OPR.get(_ix.get("opressor")) or {}).get("previsao"),
                    "validacao": ({"decisao": v["decisao"], "motivo": v.get("motivo"), "em": v.get("validado_em")} if v else None)})
    return out


def _tipo_ciclo(t: str) -> str:
    rec = re.search(r"fundo|programa|conv[eê]nio|anual|lei |pnab|rouanet|destina[cç]|permanente|fluxo cont", t, re.I)
    pon = re.search(r"edital|chamamento|n[ºo°] ?\d|/20\d\d|pr[eê]mio", t, re.I)
    return "recorrente" if rec and not pon else "pontual" if pon else "indefinido"


def opressores_e_preditivo(itens: list[dict]) -> dict:
    """Oportunidade nova (não coberta) → opressor próprio ligado por 30 dias + cadastro preditivo."""
    C = _j(CAT_OPR, {"motores": []}); L = _j(EST_OPR, {"ligados": {}})
    # DUPLICADOS NA REGENERAÇÃO (28/09): cópia velha de um voo pode trazer opressores repetidos (mesmo programa +
    # órgão); a cada regeneração fica um só — o que tem dados da validação ou está ligado.
    grupos = {}
    for x in C.get("motores") or []:
        grupos.setdefault(_nt(f"{x.get('programa')}{x.get('orgao')}"), []).append(x)
    manter, fora = [], []
    for g in grupos.values():
        g.sort(key=lambda x: (bool(x.get("validacao_mapa") or x.get("dados_confirmados") or x.get("decisao")), x["id"] in (L.get("ligados") or {}), len(json.dumps(x))), reverse=True)
        manter.append(g[0]); fora += [y["id"] for y in g[1:]]
    if fora:
        C["motores"] = [x for x in C["motores"] if x["id"] not in set(fora)]
        for i in fora:
            (L.get("ligados") or {}).pop(i, None)
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
        EST_OPR.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    # OPRESSOR ACOMPANHA A VALIDAÇÃO (28/09): oportunidade descartada ou encerrada desliga o opressor dela; válida
    # marca o opressor com os dados confirmados. Antes, 9 "novas anunciadas" tinham opressor e NENHUM estava coerente.
    from . import validacao_mapa as _vmo
    _VAL = {_nt(v.get("titulo")): v for v in _vmo.carregar().values() if v.get("titulo")}
    _ruido = re.compile(r"^\s*extrato|termo de (fomento|colabora[cç][aã]o) n[ºo°]|resultado|homologa", re.I)
    mudou = False
    for x in C.get("motores") or []:
        if not str(x.get("id", "")).startswith("nova-"):
            continue
        v = _VAL.get(_nt(x.get("programa")))
        dec = (v or {}).get("decisao") or ("descartada" if _ruido.search(str(x.get("programa") or "")) else None)
        if dec in ("descartada", "arquivada_encerrada") and x["id"] in (L.get("ligados") or {}):
            L["ligados"].pop(x["id"], None); x["desligado_por"] = f"validação: {dec} — {str((v or {}).get('motivo') or 'extrato/termo já celebrado')[:120]}"; mudou = True
        elif dec in ("valida_aberta", "valida_fora_abrangencia") and not str(x.get("validacao", "")).startswith("confirmada"):
            x["validacao"] = f"confirmada pela validação individual em {v.get('validado_em')}"; x["proxima_data"] = {"inicio": v.get("inicio"), "fim": v.get("prazo")}
            if v.get("fonte_oficial"): x["pagina"] = v["fonte_oficial"]
            mudou = True
    if mudou:
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
        EST_OPR.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    cobertos_u = {_nu(x.get("pagina") or "") for x in C.get("motores") or [] if x.get("pagina")}
    cobertos_t = {_nt(f"{x.get('programa')}") for x in C.get("motores") or []} | {_nt(f"{x.get('programa')}{x.get('orgao')}") for x in C.get("motores") or []}
    PRED.parent.mkdir(parents=True, exist_ok=True)
    ja_pred = {json.loads(l).get("id") for l in PRED.open(encoding="utf-8") if l.strip()} if PRED.exists() else set()
    novos_opr = novos_pred = 0; hoje = date.today()
    linhas_pred = []
    for it in itens:
        if it["tipo"] == "menção em diário oficial":
            continue                                   # menção sem página própria: conta no mapa, não vira opressor
        pagina = it.get("link_oficial") or it.get("url")
        ku, kt = _nu(pagina), _nt(it["titulo"])
        # só vira opressor o que tem CARA DE OPORTUNIDADE — não notícia, não dispensa de chamamento
        cara = re.search(r"edital|chamad|chamamento|pr[eê]mio|sele[cç][aã]o|fundo|inscri[cç]|apoio a projetos|patroc", it["titulo"], re.I) \
               and not re.match(r"(?i)(dispensa|extrato|homologa|resultado|termo aditivo|inexigibilidade)", it["titulo"])
        # oportunidade VALIDADA ganha opressor mesmo com título de notícia (ex.: o credenciamento do Goiás Social)
        if (it.get("validacao") or {}).get("decisao") in ("valida_aberta", "valida_fora_abrangencia"):
            cara = True
            pagina = it.get("link_oficial") or pagina; ku = _nu(pagina)
        if False and pagina and cara and ku not in cobertos_u and kt not in cobertos_t:   # 28/09: quem cria é src/opressores_repositorio.py
            oid = "nova-" + hashlib.sha1(ku.encode()).hexdigest()[:12]
            C.setdefault("motores", []).append({"id": oid, "programa": it["titulo"][:160], "orgao": it.get("orgao") or "", "motor": "f260-" + oid,
                                                "familia": "Outros programas", "esfera": "Estado" if it.get("uf") else "Brasil", "uf": it.get("uf") or "BR",
                                                "ativa": True, "tipo": "oportunidade_mapeada", "pagina": pagina, "paginas": [pagina], "validacao": "não lida ainda",
                                                "motivo_status": f"criado pelo fluxo das oportunidades ({it['origem']})", "criado_em": hoje.isoformat(),
                                                "proxima_data": {"inicio": it.get("inicio"), "fim": it.get("fim")} if it.get("fim") else None, "mencoes": [{"titulo": it["titulo"][:120], "url": it.get("url")}]})
            L.setdefault("ligados", {})[oid] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=30)).isoformat(),
                                                "origem": f"automática: oportunidade nova ({it['origem']})", "dias": 0, "ia": [], "itens": {}}
            cobertos_u.add(ku); cobertos_t.add(kt); novos_opr += 1; it["opressor"] = oid
        if it["id"] not in ja_pred:
            ciclo = _tipo_ciclo(it["titulo"])
            prox = None
            if ciclo == "pontual" and it.get("fim"):
                prox = (date.fromisoformat(it["fim"]) + timedelta(days=365)).isoformat()[:7]
            elif it.get("publicado_em"):
                prox = (date.fromisoformat(it["publicado_em"]) + timedelta(days=365)).isoformat()[:7]
            linhas_pred.append({"id": it["id"], "titulo": it["titulo"], "orgao": it.get("orgao"), "uf": it.get("uf"), "origem": it["origem"],
                                "tipo": it["tipo"], "ciclo": ciclo, "publicado_em": it.get("publicado_em"), "prazo": it.get("fim"),
                                "proxima_janela_estimada": prox, "confianca": "baixa" if ciclo == "indefinido" else "media",
                                "confirmada": it["confirmada"], "cadastrado_em": hoje.isoformat()})
            novos_pred += 1
    if novos_opr:
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
        EST_OPR.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    if linhas_pred:
        with PRED.open("a", encoding="utf-8") as f:
            for x in linhas_pred:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    return {"opressores_criados": novos_opr, "cadastrados_para_previsao": novos_pred,
            "opressores_total": len(C.get("motores") or []), "previsao_total": len(ja_pred) + novos_pred}


def atualizar_preditivo(eid: str, dados: dict) -> bool:
    """Cada investigação do Interceptador compõe o cadastro preditivo: prazo, página oficial, financiador,
    qualidade, parecer — o entendimento daquela oportunidade."""
    if not PRED.exists():
        return False
    linhas = [json.loads(l) for l in PRED.open(encoding="utf-8") if l.strip()]
    achou = False
    for x in linhas:
        if x.get("id") == eid:
            x.setdefault("estudos", []).append({k: v for k, v in dados.items() if v is not None})
            x["estudos"] = x["estudos"][-5:]
            if dados.get("prazo"):
                x["prazo"] = dados["prazo"]
                if x.get("ciclo") == "pontual":
                    x["proxima_janela_estimada"] = (date.fromisoformat(dados["prazo"]) + timedelta(days=365)).isoformat()[:7]
                x["confianca"] = "alta" if dados.get("pagina_oficial") else x.get("confianca")
            achou = True
    if achou:
        PRED.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")
    return achou


def _resumo_opressores(itens: list[dict]) -> dict:
    """28/09: os números REAIS dos livros de oportunidades, para a Bússola ('fontes monitoradas' = opressores ligados)."""
    C = (_j(CAT_OPR, {}) or {}).get("motores", []); L = (_j(EST_OPR, {}) or {}).get("ligados", {})
    ids = {x.get("id") for x in C}; lig = [k for k in L if k in ids]
    de_abertas = {x.get("opressor") for x in itens if x.get("opressor")}
    # por mês: opressores CRIADOS e, deles, os ACIONADOS COM RESULTADO (geraram oportunidade: uma aberta agora ou edição guardada)
    por_mes = {}
    for x in C:
        m = str(x.get("criado_em") or "")[:7]
        if not m:
            continue
        p = por_mes.setdefault(m, {"criados": 0, "com_resultado": 0}); p["criados"] += 1
        if x.get("id") in de_abertas or any(h.get("origem") == "aberta" for h in (x.get("historico") or [])):
            p["com_resultado"] += 1
    return {"por_mes": por_mes, "catalogo": len(C), "ligados": len(lig), "ligados_de_oportunidades_abertas": sum(1 for k in lig if k in de_abertas),
            "ligados_fontes_permanentes": sum(1 for k in lig if k not in de_abertas),
            "abertas_com_opressor": sum(1 for x in itens if x.get("opressor")), "abertas_dispensadas": sum(1 for x in itens if x.get("opressor_dispensa")),
            "abertas_sem_opressor_nem_dispensa": sum(1 for x in itens if not x.get("opressor") and not x.get("opressor_dispensa")),
            "com_historico_de_edicoes": sum(1 for x in C if len(x.get("historico") or []) >= 2), "com_previsao": sum(1 for x in C if x.get("previsao")),
            "arquivadas_encerradas": sum(1 for v in ((_j(ROOT / "dados/editais/arquivados.json", {}) or {}).values() if isinstance(_j(ROOT / "dados/editais/arquivados.json", {}), dict) else [])
                                         if "encerr" in json.dumps(v, ensure_ascii=False).lower())}


def montar() -> dict:
    itens = consolidar()
    etapa = opressores_e_preditivo(itens)
    mapa = {}
    for it in itens:
        k = it["uf"] or "__nac__"
        p = mapa.setdefault(k, {"confirmadas": 0, "possiveis": 0})
        p["possiveis"] += 1; p["confirmadas"] += 1 if it["confirmada"] else 0
    tot = {"confirmadas": sum(v["confirmadas"] for v in mapa.values()), "possiveis": sum(v["possiveis"] for v in mapa.values())}
    cal = [{**{k: it.get(k) for k in ("id", "titulo", "orgao", "uf", "inicio", "fim", "link_oficial", "origem", "publicado_em", "tipo")},
            "inspecionada": bool(it.get("inspecao"))} for it in itens if it["confirmada"]]
    from . import validacao_mapa as _vm2
    _V = _vm2.carregar()
    res = {"validacao": {"aplicada": True, "decisoes": len(_V), "arquivos": sorted({v.get("_arquivo") for v in _V.values()}),
                         "sem_decisao": sum(1 for x in itens if not x.get("validacao") and not x.get("confirmada"))},   # confirmada (objeto+prazo+link) não precisa de decisão
           "em": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Publica")[0].strip(),
           "etapas": {"possiveis_abertas": tot["possiveis"], "confirmadas_com_minimo": tot["confirmadas"],
                      "por_origem": {o: sum(1 for x in itens if x["origem"].startswith(o)) for o in ("motor", "Piloto - Espião", "Piloto - Interceptador")},
                      "por_tipo": {t: sum(1 for x in itens if x["tipo"] == t) for t in ("ente público", "empresa/instituto", "menção em diário oficial")},
                      "por_validacao": {d: sum(1 for x in itens if (x.get("validacao") or {}).get("decisao") == d) for d in ("valida_aberta", "valida_fora_abrangencia", "pendente")},
                      "triagem": dict(TRIAGEM), **etapa},
           "mapa": {"total": tot, "por_uf": mapa}, "calendario": cal, "opressores": _resumo_opressores(itens),
           "confirmadas": [x for x in itens if x["confirmada"]][:300],
           "itens_por_uf": {k: sorted([{kk: x.get(kk) for kk in ("id", "titulo", "url", "link_oficial", "fim", "inicio", "tipo", "origem", "confirmada", "inspecao", "orgao", "publicado_em", "validacao",
                                                                  "objeto", "condicoes", "checklist", "area", "opressor", "opressor_dispensa", "opressor_edicoes", "opressor_previsao")}
                                       for x in itens if (x["uf"] or "__nac__") == k], key=lambda y: (not y["confirmada"], not y["inspecao"], str(y.get("fim") or "9"), y["titulo"]))
                            for k in mapa},
           "possiveis_sem_minimo": [x for x in itens if not x["confirmada"] and x["tipo"] != "menção em diário oficial"][:300]}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"mapa_total": tot, **res["etapas"]}


def atualizar_mapa() -> dict:
    """28/09 (titular): o mapa nunca é gravado sem a validação e sem decisão para o que chegou depois dela."""
    montar()
    from . import curadoria_automatica, validacao_mapa
    c = curadoria_automatica.run()
    try:
        validacao_mapa.run()
    except Exception as ex:
        c["validacao_mapa"] = f"falhou: {type(ex).__name__}"
    try:
        from .opressores_repositorio import sincronizar
        c["repositorio_dos_opressores"] = sincronizar()
    except Exception as ex:
        c["repositorio_dos_opressores"] = f"falhou: {type(ex).__name__}"
    try:                                     # 01/10: livros de LEIS — parametrizam o Farol de Alexandria
        from .livros_leis import montar as _leis
        c["livros_de_leis"] = _leis()
    except Exception as ex:
        c["livros_de_leis"] = f"falhou: {type(ex).__name__}"
    try:                                     # 29/09: cada opressor é um LIVRO — curadoria (separa/junta) e classificação
        from .livros_opressores import curar
        c["livros"] = curar()
    except Exception as ex:
        c["livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 01/10: regra dos livros — o livro existente recebe o checklist; locais de busca
        from .livros_regra import aplicar_motores
        c["regra_dos_livros"] = aplicar_motores()
    except Exception as ex:
        c["regra_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 29/09: os 12 parâmetros de cada opressor, pesquisados na fonte oficial
        from .parametros_opressores import aplicar as _par
        c["parametros_opressores"] = _par()
    except Exception as ex:
        c["parametros_opressores"] = f"falhou: {type(ex).__name__}"
    r = montar(); r["curadoria"] = c
    return r


if __name__ == "__main__":
    import sys
    print(json.dumps(atualizar_mapa() if "--completo" in sys.argv else montar(), ensure_ascii=False, indent=1))
