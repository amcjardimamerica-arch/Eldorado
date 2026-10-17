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
    6. PREDITIVO     cada oportunidade é cadastrada em biblioteca_alexandria/livros/_acervo/base/preditivo/oportunidades.jsonl
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
PRED = ROOT / "biblioteca_alexandria/livros/_acervo/base/preditivo/oportunidades.jsonl"
SAIDA = ROOT / "docs/dados/fluxo_oportunidades.json"
AGREGADORES = re.compile(r"duckduckgo|bing\.com|google\.|queridodiario|captadores\.org|observatorio3setor|prosas\.com|filantropia\.ong|gife\.org|idis\.org|pncp\.gov\.br/app", re.I)
CHECKLIST = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador", "Território", "Esfera",
             "Requisitos", "Anexos", "Modalidade", "Área de atuação"]
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


def _cart_item(eid, item):
    """09/10: o item que o Cartório certificou para esta estrela (ou None)."""
    try:
        from .cartorio import item_checklist
        return item_checklist(str(eid or ""), item) if eid else None
    except Exception:  # noqa: BLE001
        return None


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
    # 14/10 (análise do sistema): só 59% com tema — vocabulário mais amplo do painel, convertido aos temas da tela, e
    # as chamadas de projetos sociais genéricos (impacto social, inclusão, vulnerabilidade) como assistência
    junto = " ".join(t for t in textos if t)
    try:
        from .dashboard_dados import inferir_area
        conv = {"cultura": "cultura", "esporte": "esporte", "saude": "saude", "educacao": "educacao", "meio_ambiente": "ambiente",
                "crianca_adolescente": "crianca", "idoso": "idoso", "assistencia_social": "assistencia", "direitos_humanos": "assistencia",
                "seguranca_alimentar": "assistencia", "emendas_parlamentares": "emendas"}.get(inferir_area(junto))
        if conv:
            return conv
    except Exception:  # noqa: BLE001
        pass
    if re.search(r"impacto social|projetos? sociais|inclus[aã]o social|vulnerabilidade|desenvolvimento (social|comunit)|"
                 r"transforma[cç][aã]o social|comunidades?|popula[cç][aã]o (em situa|de baixa)|direitos? (humanos|sociais)|"
                 r"combate [aà] fome|seguran[cç]a alimentar|g[eê]nero|equidade|diversidade|antirracis", junto, re.I):
        return "assistencia"
    return None


def _achados_dos_livros() -> list[dict]:
    """Achados dos motores lidos dos livros; a base bruta só como reserva enquanto os livros não têm os achados."""
    try:
        from .banco_livros import achados
        a = achados()
        if a:
            return a
    except Exception:  # noqa: BLE001
        pass
    return [json.loads(l) for l in MESTRE.open(encoding="utf-8") if l.strip()] if MESTRE.exists() else []


def consolidar() -> list[dict]:
    hoje = date.today(); lim = (hoje - timedelta(days=60)).isoformat()
    brutos = []
    for m in _achados_dos_livros():                  # 16/10/2026 (etapa 3): os achados vêm dos LIVROS
        if not isinstance(m, dict):
            continue
        if m.get("estado_export") in ("arquivado", "excluido"):
            continue
        brutos.append(("motor " + str(m.get("fonte_id") or m.get("fonte_nome") or ""), m))
    # 10/10 (revisão humana, Partes 1 a 3): OPORTUNIDADES NOVAS (derivadas) — entram com o id da revisão, para a
    # certidão da revisão (estrela:<id>) se ligar a elas; só as não descartadas (ruído, fora do perfil, encerrada, duplicata ficam fora)
    for _rid, _dv in ((_j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/derivadas_revisao.json", {}).get("derivadas") or {}).items()):
        if (_dv or {}).get("veredito") in ("ruido", "fora_perfil", "encerrada", "duplicata"):
            continue
        _ob = ((_dv.get("itens") or {}).get("Objeto") or {}).get("valor") or _dv.get("parecer") or _rid
        _pz = _dv.get("prazo") or {}
        brutos.append(("revisão humana", {"id": _rid, "titulo": str(_ob)[:300], "url": _dv.get("link_documento") or _dv.get("site_oficial"),
                                          "link_oficial": _dv.get("link_documento") or _dv.get("site_oficial"), "fim": (_pz.get("fim") or None),
                                          "inicio": (_pz.get("inicio") or None), "fonte_id": "revisao-humana", "descoberto_em": str(_dv.get("em") or "")[:10],
                                          "derivada_de": _dv.get("derivada_de"), "orgao": ((_dv.get("itens") or {}).get("Órgão / financiador") or {}).get("valor")}))
    for c in ((__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/piloto/candidatas_do_catalogo.json", {}) or {}).get("candidatas") or []):
        cid = "cat-" + hashlib.sha1(c["url"].encode()).hexdigest()[:12]
        brutos.append(("Piloto - Espião", {"id": cid, "titulo": c.get("titulo"), "url": c.get("url"), "orgao": c.get("visto_em"),
                                            "descoberto_em": c.get("descoberto_em"), "fonte_id": "piloto-espiao", "enquadramento": c.get("enquadramento")}))
    # EMENDAS PARLAMENTARES NO FLUXO (titular, 28/09): a captação de emendas (federal, estadual de Goiás e municipal de
    # Goiânia) abre todo ano em 01/10 e vai a 30/11 (config/emendas.json). Ficavam só no conjunto antigo do painel e
    # sumiram do Radar, do mapa e dos calendários quando eles passaram a ler o fluxo validado. Voltam, a cada ano.
    try:
        # 16/10/2026 (titular): da CONFIGURAÇÃO (config/emendas.json), não do painel do site lido de volta
        from .emendas import _cfg as _ecfg, oportunidade as _eop
        _ec = _ecfg(); _hj = date.today()
        class _LevVazio(dict):                          # o fluxo não usa o levantamento dos parlamentares
            def __missing__(self, k):
                return [] if k == "parlamentares" else 0
        _ems = [_eop(t, _hj.year, _LevVazio(), _hj) for t in (_ec.get("tipos") or [])]
        for em in _ems:
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
    # 02/10: os MOTORES INDEXADORES (src/indexadores) gravam o mesmo arquivo, com financiador, áreas e o motor da família
    for ag in (__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/agregadores/itens.json", {}) or {}).get("itens", []):
        brutos.append((f"motor agregadores · {ag.get('fonte')}", {"id": ag["id"], "titulo": ag.get("titulo"), "url": ag.get("link_oficial") or ag.get("pagina_agregador"),
                       # 29/09: prazo de agregador NÃO é prazo (regra do titular) — fica como pista até a fonte oficial confirmar
                       "fim": None, "prazo_agregador": ag.get("prazo"), "uf": ag.get("uf"), "data_publicacao": ag.get("primeiro_visto"), "fonte_id": "motor-agregadores",
                       "orgao": ag.get("financiador"), "motor_indexador": ag.get("motor"),
                       "pagina_agregador": ag.get("pagina_agregador"),
                       "areas_fonte": ag.get("areas") or (["cultura"] if ag.get("fonte") == "farolcultural" else [])}))
    for arq, e in __import__("src.livro_arquivo", fromlist=["x"]).ler_pasta(EXT).items():   # 16/10: em bloco (cada livro 1 vez)
        e = e or {}
        if e.get("investigacao_ia") and arq.stem.startswith(("cat-", "op-")):
            # 16/10 (titular): o Interceptador passa pelo PORTÃO e pelo LIVRO, como qualquer motor
            _it = {"id": arq.stem, "titulo": e.get("titulo"), "url": e.get("url"), "orgao": e.get("orgao"), "uf": e.get("uf"),
                   "descoberto_em": str((e.get("investigacao_ia") or {}).get("em", ""))[:10], "fonte_id": "piloto-interceptador"}
            from .porta_oportunidade import motivo_para_nao_guardar as _mot
            if _mot({k: v for k, v in _it.items() if v}) is not None:
                continue
            try:
                from .banco_livros import registrar_achados as _reg
                _reg([{**_it, "sensor": "piloto-interceptador"}], motor="piloto-interceptador")
            except Exception:  # noqa: BLE001
                pass
            brutos.append(("Piloto - Interceptador", _it))
    # NÃO É OPORTUNIDADE (27/09): pauta legislativa, assembleia, contrato já assinado, resultado e lista de aprovados.
    # Retificação e alteração de cronograma FICAM: indicam edital aberto.
    RUIDO = re.compile(r"^\s*\d{1,2}:\d{2}\b|vota[cç][õo]es|requerimentos|t[ií]tulos? de cidadania|utilidades? p[uú]blica|convoca[cç][aã]o de assembleia|"
                       r"^\s*extrato|resultado|lista de aprovados|aprovados e suplentes|heteroidentifica|homologa|inexigibilidade|dispensa de chamamento|termo aditivo", re.I)
    _IDX = (_j(ROOT / "estado/opressores_indice.json", {}) or {}).get("indice") or {}
    try:                                     # 11/10 (validação das 558 abertas): a mesma régua do motor dos agregadores
        from .indexadores.extracao import nao_e_fomento as _nao_fom
    except Exception:  # noqa: BLE001
        _nao_fom = lambda t: None
    _OPR = {x.get("id"): x for x in (_j(CAT_OPR, {}) or {}).get("motores", [])}
    _EO = (_j(EST_OPR, {}) or {}).get("ligados") or {}
    vistos_t, vistos_u, out = set(), set(), []
    # VALIDAÇÃO INDIVIDUAL (27/09): decisão registrada prevalece; o que não foi validado passa pelas regras aprendidas
    from . import validacao_mapa as _vm
    from . import dispensas_itens as _DI
    VAL = _vm.carregar(); HER = _vm.indice_heranca(VAL)
    ARQ = _j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/arquivados.json", {})
    TRIAGEM.clear(); TRIAGEM.update({"saiu_por_validacao": 0, "saiu_por_arquivo": 0, "dispensado_pela_regra": 0, "regras": {}})
    for origem, m in brutos:
        tit = re.sub(r"\s+", " ", str(m.get("titulo") or "")).strip()
        if not tit or RUIDO.search(tit) or (not origem.startswith("motor") or "agregadores" in origem or "outras" in origem.lower() or "Espião" in origem) and _nao_fom(tit):
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
        try:                                   # 09/10 (titular): o link CERTIFICADO pelo Cartório vem primeiro (régua única)
            from .cartorio import link_oficial as _lo_cart
            _lcart = _lo_cart(m.get("id"))
        except Exception:  # noqa: BLE001
            _lcart = None
        link = _oficial(_lcart, ve.get("pagina_oficial"), e.get("pagina_oficial"), val.get("site"), m.get("url"))
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
        _ix = _IDX.get(m.get("id")) or {}
        _vok = (_vv.get("decisao") or "").startswith("valida")
        _doze = _vv.get("doze_itens") or {} if _vok else {}
        _val_ok = {"Objeto": objeto, "Prazo de inscrição": fim or (_vv.get("prazo_dispensado") and "fluxo contínuo"),
                   "Órgão / financiador": _vv.get("orgao") or _vv.get("financiador"), "Valor": _vv.get("valor"),
                   "Território": _vv.get("uf") or _vv.get("territorio"), "Requisitos": _vv.get("requisitos")} if _vok else {}
        # 01/10: os 12 itens da validação individual (doze_itens) e os parâmetros do livro também alimentam o checklist.
        # Antes só valiam campos que a validação nem grava (orgao, valor, territorio...) e 'doze_itens' era ignorado.
        _par = ((_EO.get(_ix.get("opressor")) or {}).get("parametros") or {}) if _ix.get("opressor") else {}
        _pdz = _par.get("doze") or {}
        _mesmo = bool(link and _par and _nu(link) in {_nu(x) for x in (_par.get("fonte_oficial"), (_par.get("edital") or {}).get("url")) if x})
        checklist = {}
        for k in CHECKLIST:
            c = (campos or {}).get(k) or {}
            dz = _doze.get(k) or {}; pz = _pdz.get(k) or {}
            if c.get("comprovado"):
                checklist[k] = {"s": "ok", "v": str(c.get("valor") or "")[:90], "t": str(c.get("trecho") or "")[:160]}
            elif c.get("dispensado"):
                checklist[k] = {"s": "disp", "v": "dispensado pelo edital", "t": str(c.get("trecho_dispensa") or "")[:160]}
            elif dz.get("status") == "confirmado" and dz.get("valor"):
                checklist[k] = {"s": "val", "v": str(dz["valor"])[:90]}
            elif dz.get("status") in ("dispensado pelo edital", "não informado no edital", "dispensado pelo tipo"):   # 02/10: dispensa fundamentada no tipo
                checklist[k] = {"s": "disp", "v": (dz.get("status") if not dz.get("valor") else f"{dz['status']}: {dz['valor']}")[:90], "t": "validação individual no site oficial"}
            elif _val_ok.get(k):
                checklist[k] = {"s": "val", "v": str(_val_ok[k])[:90]}
            elif pz.get("status") in ("confirmado", "dispensado pelo edital", "não informado no edital") and _par.get("decisao") in ("V", "R") \
                    and (pz.get("valor") or pz.get("status") != "confirmado"):
                # parâmetros do livro: valem como 'val'/'disp' só se for o MESMO edital; senão são 'ref' (edição de referência)
                st = "val" if (_mesmo and pz["status"] == "confirmado") else ("disp" if (_mesmo and pz["status"] != "confirmado") else "ref")
                checklist[k] = {"s": st, "v": str(pz.get("valor") or pz["status"])[:90], "t": "parâmetros do livro" + ("" if _mesmo else " (edital de referência, não confirmado como o desta oportunidade)")}
            elif _cart_item(m.get("id"), k):
                # 09/10 (titular): CARTÓRIO — item lido no documento oficial (trecho + página) ou dispensa justificada
                checklist[k] = _cart_item(m.get("id"), k)
            elif campos:
                checklist[k] = {"s": "falta"}
            elif m.get("_emenda"):
                # EMENDA (28/09): não há edital — o calendário legislativo (config/emendas.json) diz o que se sabe; o resto não se aplica
                _em = {"Objeto": (str(objeto or "")[:90], "val"), "Prazo de inscrição": (f"{m.get('inicio')} a {fim}", "val"),
                       "Órgão / financiador": (str(m.get("orgao") or "casa legislativa")[:90], "val"), "Território": ("nacional" if m.get("nivel") == "federal" else "Goiás", "val"),
                       "Esfera": (str(m.get("nivel") or ""), "val"), "Área de atuação": ("qualquer área de atuação da entidade", "val"),
                       "Requisitos": ("entidade regular: CNPJ, certidões e cadastro na casa legislativa", "val"),
                       "Valor": ("definido pelo parlamentar", "disp"), "Modalidade": ("definida pelo parlamentar na indicação", "disp"),
                       "Resultado": ("não há edital: indicação do parlamentar", "disp"), "Prazo de recurso": ("não há edital nem recurso", "disp"),
                       "Anexos": ("não há edital: ofício e plano de trabalho da entidade", "disp")}
                vv, ss = _em.get(k, ("", "pend")); checklist[k] = {"s": ss, "v": vv}
            else:
                checklist[k] = {"s": "pend"}
        # 01/10: DISPENSA PROVÁVEL pelo tipo de recurso (config/dispensas_por_regime.json). Não conta como item feito.
        _mo = _OPR.get(_ix.get("opressor"))
        # esfera comprovada vale mais que o 'nivel' bruto do motor (que erra em agregadores e diários)
        _esf = str((checklist.get("Esfera") or {}).get("v") or "").lower() if (checklist.get("Esfera") or {}).get("s") in ("ok", "val", "disp") else ""
        _privada = ("privad" in _esf or "internacional" in _esf) if re.search(r"privad|internacional|federal|estadual|municipal|distrital", _esf) \
            else (m.get("nivel") in ("privada", "privado") or str((_mo or {}).get("natureza") or "") == "privada")
        _reg, _reg_o = _DI.regime(_mo, tit, str(m.get("orgao") or ""), emenda=bool(m.get("_emenda")),
                                  prazo_dispensado=prazo_disp,
                                  privada=_privada)
        dispensa_analise = _DI.aplicar_ao_checklist(checklist, _reg, _reg_o)
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
                    "objeto": str(objeto)[:240] if objeto else None, "confirmada": confirmada, "url": m.get("url"), "inspecao": insp, "condicoes": condicoes, "checklist": checklist, "regime": dispensa_analise["regime"], "dispensa_analise": dispensa_analise,
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
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # 11/10: formato único (compacto)
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
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # 11/10: formato único (compacto)
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
        CAT_OPR.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")   # 11/10: formato único (compacto)
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


_ORDEM_SELO = {"bronze": 0, "prata": 1, "ouro": 2}


def _selos_dos_itens(itens: list[dict]) -> dict:
    """03/10 (titular): a ESTRELA mede o EDITAL ATUAL e só existe na oportunidade ABERTA:
    bronze = há o site oficial da publicação; prata = + o prazo de inscrição conhecido; ouro = + os 12 critérios
    conhecidos (ou dispensados quando não se aplicam). Não herda do livro nem da edição anterior: quando a oportunidade
    fecha, a estrela sai e o que se sabia dela vira histórico do LIVRO; quando abre uma nova edição, a estrela recomeça
    pelo edital novo. (O LIVRO tem o seu próprio selo, pelo histórico de 3 anos — selo_livro — e aparece sempre.)"""
    from collections import Counter
    from datetime import date as _d
    hoje = _d.today().isoformat()
    for it in itens:
        I = it.get("inspecao") or {}
        u = str(it.get("url") or "")
        oficial = it.get("link_oficial") or I.get("pagina_oficial") or \
            (u if re.search(r"\.(gov|leg|jus|mp)\.br(/|$)|pncp\.gov\.br", u, re.I) else None)   # o mesmo critério do painel
        fim = str(it.get("fim") or "")[:10]
        reg = str(it.get("regime") or "")
        continuo = "contínuo" in reg or "continuo" in reg
        if fim and fim < hoje:
            it["selo"] = None; it["selo_de"] = "fechada — a estrela vira histórico do livro"; continue
        it["site_oficial_conhecido"] = bool(oficial)                       # informação; o selo vem dos 12 itens
        # 04/10 (titular): critério único — bronze = objeto + prazo + território; prata = + valor + requisitos;
        # ouro = os 12 validados ou dispensados COM justificativa ("não informado" é falta, não dispensa)
        from .criterio_selos import nivel, faltando
        ck = it.get("checklist") or {}
        it["selo"] = nivel(ck)
        it["selo_faltando"] = faltando(ck)
        it["selo_de"] = "edital atual" if it["selo"] else "edital atual sem objeto, prazo e território identificados"
    from .criterio_selos import auditar_estrelas
    _casos = auditar_estrelas(itens)                                       # 04/10: regra permanente — nada acima do critério
    if _casos:
        (ROOT / "estado/auditoria_selos.json").write_text(json.dumps({"em": hoje, "rebaixados": _casos}, ensure_ascii=False, indent=1), encoding="utf-8")
    return dict(Counter(it["selo"] for it in itens if it.get("selo")))


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
    _mon = (_j(EST_OPR, {}) or {}).get("monitoramento") or {}
    return {"por_mes": por_mes, "catalogo": len(C), "ligados": len(lig), "ligados_de_oportunidades_abertas": sum(1 for k in lig if k in de_abertas),
            "monitorados_abertos": _mon.get("abertos"), "monitorados_prestes": _mon.get("prestes_a_abrir"), "monitorados_continuos": _mon.get("fluxo_continuo"),
            "ligados_fontes_permanentes": sum(1 for k in lig if k not in de_abertas),
            "abertas_com_opressor": sum(1 for x in itens if x.get("opressor")), "abertas_dispensadas": sum(1 for x in itens if x.get("opressor_dispensa")),
            "abertas_sem_opressor_nem_dispensa": sum(1 for x in itens if not x.get("opressor") and not x.get("opressor_dispensa")),
            "com_historico_de_edicoes": sum(1 for x in C if len(x.get("historico") or []) >= 2), "com_previsao": sum(1 for x in C if x.get("previsao")),
            "arquivadas_encerradas": sum(1 for v in ((_j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/arquivados.json", {}) or {}).values() if isinstance(_j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/arquivados.json", {}), dict) else [])
                                         if "encerr" in json.dumps(v, ensure_ascii=False).lower())}


FECHADAS = ("ruido", "encerrada", "fora_perfil", "duplicata")


def aplicar_parametro(itens: list[dict], vereditos: dict | None = None, hoje: str | None = None) -> tuple[list[dict], dict]:
    """PARÂMETRO ÚNICO (titular, 11/10/2026): OPORTUNIDADE ABERTA = está no fluxo, não foi fechada por veredito (ruído,
    encerrada, fora do perfil, duplicata) e não tem prazo vencido. Cada aberta está em UM estado:
      validada          objeto + prazo vigente + site oficial comprovados, ou veredito ouro
      validacao_manual  veredito vermelho (aguarda validação/exclusão manual)
      em_verificacao    as demais
    Abertas = validadas + em verificação + validação manual — o mesmo número em todos os painéis."""
    from datetime import date as _date
    if vereditos is None:
        vereditos = (_j(ROOT / "biblioteca_alexandria/livros/_acervo/editais/vereditos_revisao.json", {}) or {}).get("vereditos") or {}
    hoje = hoje or _date.today().isoformat()
    fora = {"fechada por veredito": 0, "prazo vencido": 0}
    abertas = []
    for it in itens:
        v = (vereditos.get(str(it.get("id"))) or {}).get("veredito")
        if v in FECHADAS:
            fora["fechada por veredito"] += 1; continue
        if it.get("fim") and str(it["fim"])[:10] < hoje:
            fora["prazo vencido"] += 1; continue
        it["estado"] = ("validacao_manual" if v == "validacao_manual" else
                        "validada" if (v == "ouro" or it.get("confirmada")) else "em_verificacao")
        abertas.append(it)
    par = {"regra": aplicar_parametro.__doc__.split("\n")[0].strip(), "abertas": len(abertas),
           "validadas": sum(1 for x in abertas if x["estado"] == "validada"),
           "em_verificacao": sum(1 for x in abertas if x["estado"] == "em_verificacao"),
           "validacao_manual": sum(1 for x in abertas if x["estado"] == "validacao_manual"),
           "fora_do_parametro": fora, "em": hoje}
    return abertas, par


def deduplicar(itens: list[dict]) -> tuple[list[dict], dict]:
    """11/10 (titular, melhoria dos motores): a duplicata é fundida ANTES do registro — na consolidação das entradas de
    todos os motores (Piloto, agregadores, Espião…). Fica a canônica (revisão humana; senão a regra M1 do saneamento:
    URL canônica, nº do edital + órgão), completada com o que só a cópia tinha (site oficial, prazo, itens lidos)."""
    canon = {}
    try:
        from .opressores_repositorio import canonica_por_revisao
        canon.update(canonica_por_revisao())
    except Exception:  # noqa: BLE001
        pass
    try:
        from .saneamento_motores import agrupar_duplicatas
        for d, inf in (agrupar_duplicatas(itens) or {}).items():
            c = (inf or {}).get("canonico") if isinstance(inf, dict) else inf
            if c and str(c) != str(d):
                canon.setdefault(str(d), str(c))
    except Exception:  # noqa: BLE001
        pass
    por_id = {str(x.get("id")): x for x in itens}
    fica, fundidas = [], 0
    for x in itens:
        c = canon.get(str(x.get("id")))
        if c and c in por_id and c != str(x.get("id")):
            alvo = por_id[c]; fundidas += 1
            alvo.setdefault("ids_origem", [alvo.get("id")])
            if x.get("id") not in alvo["ids_origem"]:
                alvo["ids_origem"].append(x.get("id"))
            for k in ("link_oficial", "fim", "inicio", "orgao", "uf"):
                if not alvo.get(k) and x.get(k):
                    alvo[k] = x[k]
            for k, v in (x.get("checklist") or {}).items():
                if (v or {}).get("s") in ("ok", "val", "dt", "disp") and (alvo.get("checklist") or {}).get(k, {}).get("s") not in ("ok", "val", "dt", "disp"):
                    alvo.setdefault("checklist", {})[k] = v
            continue
        fica.append(x)
    return fica, {"duplicatas_fundidas_antes_do_registro": fundidas}


def incluir_do_repositorio(res: dict) -> int:
    """11/10/2026 (titular): a tela inicial contava a lista do fluxo (465) e a Bússola o repositório único (558) — as
    oportunidades que vêm só da caixa dos motores não estavam na lista. Elas entram aqui, com o estado do repositório,
    e a lista passa a ter o mesmo universo do parâmetro."""
    rep = (_j(ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json", {}) or {}).get("registros") or []
    por_uf = res.setdefault("itens_por_uf", {})
    if rep:                                  # a lista segue o repositório: sem fechadas e uma linha por oportunidade
        dono = {i: r for r in rep for i in [r["id"], *(r.get("ids_origem") or [])]}
        vistos = set()
        for uf in list(por_uf):
            fica = []
            for x in por_uf[uf]:
                r = dono.get(str(x.get("id")))
                if r is None:
                    fica.append(x); continue
                if r.get("estado") == "fechada" or r.get("arquivada") or r["id"] in vistos:
                    continue
                vistos.add(r["id"]); x["estado"] = r.get("estado"); fica.append(x)
            por_uf[uf] = fica
    ja = {str(x.get("id")) for L in por_uf.values() for x in L} | {str(i) for L in por_uf.values() for x in L for i in (x.get("ids_origem") or [])}
    n = 0
    for r in rep:
        if r.get("estado") == "fechada" or r.get("arquivada") or r["id"] in ja or any(i in ja for i in r.get("ids_origem") or []):
            continue
        ck = {k: ({"s": "ok", "v": str(v.get("valor") or "")[:120]} if v.get("estado") == "comprovado" else
                  {"s": "disp", "v": str(v.get("motivo") or "")[:120]} if v.get("estado") == "dispensado" else
                  {"s": "ok", "v": str(v.get("valor") or "")[:120]} if v.get("estado") == "nao_comprovado" else {"s": "falta"})
              for k, v in (r.get("itens") or {}).items()}
        item = {"id": r["id"], "titulo": r.get("titulo"), "url": r.get("url"), "link_oficial": r.get("link_oficial"), "fim": r.get("fim"),
                "orgao": r.get("orgao"), "uf": r.get("uf"), "origem": r.get("origem") or "repositório único", "estado": r.get("estado"),
                "confirmada": r.get("estado") == "validada", "checklist": ck, "livro": r.get("livro"), "ids_origem": r.get("ids_origem"),
                "do_repositorio": True}
        por_uf.setdefault(r.get("uf") or "__nac__", []).append(item)
        n += 1
    return n


def montar() -> dict:
    itens = consolidar()
    # 16/10/2026 (titular): em outros estados, só ESTADUAIS e CAPITAIS — município de outro estado não entra no fluxo
    # (a página inicial, as abertas, os achados do dia e a fila de verificação vêm daqui)
    try:
        from .repositorio_unico import municipal_fora_de_goias
        itens = [x for x in itens if not municipal_fora_de_goias(x)]
    except Exception:  # noqa: BLE001
        pass
    itens, _DEDUP = deduplicar(itens)
    itens, _PARAM = aplicar_parametro(itens)
    etapa = opressores_e_preditivo(itens)
    try:                                     # 02/10 (titular): marcador de iniciativa (poder público / privada / mista)
        from .pareceres_livros import iniciativa_por_id
        _INI = iniciativa_por_id()
        for it in itens:
            it["iniciativa"] = _INI.get(it.get("id"))
    except Exception:
        pass
    try:                                     # 03/10 (titular): selo do LIVRO (histórico de 3 anos) ao lado da estrela
        from .selo_livros import selo_por_livro
        _SL = selo_por_livro()
        for it in itens:
            it["selo_livro"] = _SL.get(it.get("opressor"))
    except Exception:
        pass
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
           "parametro": _PARAM, "deduplicacao": _DEDUP,
           "em": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Publica")[0].strip(),
           "etapas": {"possiveis_abertas": tot["possiveis"], "confirmadas_com_minimo": tot["confirmadas"],
                      "por_origem": {o: sum(1 for x in itens if x["origem"].startswith(o)) for o in ("motor", "Piloto - Espião", "Piloto - Interceptador")},
                      "por_tipo": {t: sum(1 for x in itens if x["tipo"] == t) for t in ("ente público", "empresa/instituto", "menção em diário oficial")},
                      "por_validacao": {d: sum(1 for x in itens if (x.get("validacao") or {}).get("decisao") == d) for d in ("valida_aberta", "valida_fora_abrangencia", "pendente")},
                      "triagem": dict(TRIAGEM), **etapa},
           "selos": _selos_dos_itens(itens),
           "mapa": {"total": tot, "por_uf": mapa}, "calendario": cal, "opressores": _resumo_opressores(itens),
           "confirmadas": [x for x in itens if x["confirmada"]][:300],
           "itens_por_uf": {k: sorted([{kk: x.get(kk) for kk in ("id", "titulo", "url", "link_oficial", "fim", "inicio", "tipo", "origem", "confirmada", "estado", "inspecao", "orgao", "publicado_em", "validacao",
                                                                  "objeto", "condicoes", "checklist", "regime", "dispensa_analise", "area", "opressor", "opressor_dispensa", "opressor_edicoes", "opressor_previsao", "selo", "selo_de", "iniciativa", "selo_livro")}
                                       for x in itens if (x["uf"] or "__nac__") == k], key=lambda y: (not y["confirmada"], not y["inspecao"], str(y.get("fim") or "9"), y["titulo"]))
                            for k in mapa},
           "possiveis_sem_minimo": [x for x in itens if not x["confirmada"] and x["tipo"] != "menção em diário oficial"][:300]}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    try:                                     # 11/10 (titular): REPOSITÓRIO ÚNICO — todas as origens num só lugar; a tela
        from .repositorio_unico import construir as _repo     # inicial, o Cartório e o Chrome contam o MESMO universo
        _r = _repo()
        res["incluidas_do_repositorio"] = incluir_do_repositorio(res)        # 11/10: UM universo — a lista = o repositório
        # 16/10 (titular): FONTE ÚNICA — a lista contém SÓ as oportunidades abertas do repositório (nada por fora)
        _ab = {x["id"] for x in (_j(ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json", {}) or {}).get("registros") or []
               if x.get("estado") != "fechada"}
        if _ab:
            _antes = sum(len(v) for v in (res.get("itens_por_uf") or {}).values())
            res["itens_por_uf"] = {u: [x for x in v if x.get("id") in _ab] for u, v in (res.get("itens_por_uf") or {}).items()}
            res["itens_por_uf"] = {u: v for u, v in res["itens_por_uf"].items() if v}
            for _k in ("confirmadas", "possiveis_sem_minimo"):
                res[_k] = [x for x in res.get(_k) or [] if x.get("id") in _ab]
            res["fora_do_repositorio_retiradas"] = _antes - sum(len(v) for v in res["itens_por_uf"].values())
        res["parametro"] = {**(res.get("parametro") or {}), **{k: _r[k] for k in ("abertas", "validadas", "em_verificacao", "validacao_manual")},
                            "estantes": _r.get("estantes"), "fonte": "repositório único (biblioteca_alexandria/livros/_vistas/repositorio_unico.json)",
                            "auditoria": _r.get("auditoria")}
        SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    except Exception as ex:  # noqa: BLE001 — o repositório nunca derruba o fluxo
        res.setdefault("etapas", {})["repositorio_unico"] = f"falhou: {type(ex).__name__}"
    return {"mapa_total": tot, **res["etapas"]}


def sincronizar_com_repositorio() -> dict:
    """16/10/2026 (titular): FONTE ÚNICA, leve (fase de fechamento) — o fluxo publicado passa a conter só as oportunidades
    abertas do repositório, e o parâmetro é o resumo do repositório. Segundos, sem refazer a montagem."""
    from .repositorio_unico import SAIDA as _RS
    rep = _j(_RS, {}) or {}
    regs = rep.get("registros") or []
    ab = {x["id"] for x in regs if x.get("estado") != "fechada"}
    res = _j(SAIDA, {}) or {}
    if not ab or not res:
        return {"sincronizado": False}
    try:
        res["incluidas_do_repositorio"] = incluir_do_repositorio(res)     # o que o repositório tem e a lista não
    except Exception:  # noqa: BLE001
        pass
    antes = sum(len(v) for v in (res.get("itens_por_uf") or {}).values())
    dono = {str(o): r["id"] for r in regs for o in [r["id"], *(r.get("ids_origem") or [])]}   # origem → id do repositório
    vistos, novo = set(), {}
    for u, v in (res.get("itens_por_uf") or {}).items():
        for x in v:
            rid = dono.get(str(x.get("id")))
            if rid in ab and rid not in vistos:
                vistos.add(rid)
                if x.get("id") != rid:
                    x["id_origem"], x["id"] = x.get("id"), rid
                novo.setdefault(u, []).append(x)
    for r in regs:                                    # o que o repositório tem aberto e ainda falta: entra do próprio registro
        if r["id"] in ab and r["id"] not in vistos:
            vistos.add(r["id"])
            novo.setdefault(r.get("uf") or "__nac__", []).append({k: r.get(k) for k in ("id", "titulo", "url", "link_oficial", "fim", "inicio",
                                                                     "origem", "estado", "uf", "area", "objeto")} | {"confirmada": r.get("estado") == "validada"})
    res["itens_por_uf"] = novo
    for k in ("confirmadas", "possiveis_sem_minimo"):
        res[k] = [x for x in res.get(k) or [] if dono.get(str(x.get("id"))) in ab]
    cont = {"abertas": len(ab), "validadas": sum(1 for x in regs if x.get("estado") == "validada"),
            "em_verificacao": sum(1 for x in regs if x.get("estado") == "em_verificacao"),
            "validacao_manual": sum(1 for x in regs if x.get("estado") == "validacao_manual")}
    res["parametro"] = {**(res.get("parametro") or {}), **cont, "fonte": "repositório único (dos livros), no fechamento da passagem"}
    res["fora_do_repositorio_retiradas"] = antes - sum(len(v) for v in res["itens_por_uf"].values())
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    lista = sum(len(v) for v in res["itens_por_uf"].values())
    return {**cont, "lista": lista, "retiradas": res["fora_do_repositorio_retiradas"], "abertas_fora_da_lista": len(ab) - lista}


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
    try:                                     # 03/10 (titular): selo ouro/prata/bronze do LIVRO pelo histórico de 3 anos
        from .selo_livros import aplicar as _selos
        c["selos_dos_livros"] = _selos()
    except Exception as ex:
        c["selos_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10 (titular): pareceres individuais acumulados nos livros
        from .pareceres_livros import aplicar as _pareceres
        c["pareceres_nos_livros"] = _pareceres()
    except Exception as ex:
        c["pareceres_nos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 01/10: conferência da Biblioteca — abrangência, empresas e duplicidade
        from .curadoria_biblioteca import conferir
        c["conferencia_dos_livros"] = conferir()
    except Exception as ex:
        c["conferencia_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 11/10 (titular): UMA OPORTUNIDADE = UM LIVRO; duplicatas num único livro
        from .unificar_livros import unificar as _unificar
        c["um_livro_por_oportunidade"] = _unificar()["resumo"]
    except Exception as ex:
        c["um_livro_por_oportunidade"] = f"falhou: {type(ex).__name__}"
    try:                                     # 11/10: o repositório enxerga os livros da MESMA rodada (estantes e Farol em dia)
        from .repositorio_unico import construir as _repo2
        c["repositorio_depois_dos_livros"] = {k: v for k, v in _repo2().items() if k in ("abertas", "validadas", "em_verificacao", "prontas_para_o_farol", "estantes")}
    except Exception as ex:
        c["repositorio_depois_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: guarda contra dados de teste (domínios reservados) — antes de tudo
        from .guarda_dados_teste import run as _guarda
        c["guarda_dados_teste"] = _guarda()
    except Exception as ex:
        c["guarda_dados_teste"] = f"falhou: {type(ex).__name__}"
    try:                                     # 01/10: regra dos livros — o livro existente recebe o checklist; locais de busca
        from .livros_regra import aplicar_motores
        c["regra_dos_livros"] = aplicar_motores()
    except Exception as ex:
        c["regra_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: previsão da próxima abertura e ativação 30 dias antes
        from .previsao_livros import run as _prev
        c["previsao_dos_livros"] = _prev()
    except Exception as ex:
        c["previsao_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: chave de acionamento dos livros e léxico temporário (janela de 30 dias)
        from .chaves_livros import run as _chaves
        c["chaves_dos_livros"] = _chaves()
    except Exception as ex:
        c["chaves_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: preparação dos editais de fluxo permanente (Farol de Alexandria)
        from .preparacao_livros import run as _prep
        c["preparacao_dos_livros"] = _prep()
    except Exception as ex:
        c["preparacao_dos_livros"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: linha de produção (bronze → prata → ouro → qualificado), sem eliminar nada
        from .linha_producao import run as _linha
        c["linha_de_producao"] = _linha()["funil"]
    except Exception as ex:
        c["linha_de_producao"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: rede neural (treina por semana; pontua a cada ciclo) — apoio, nunca filtro
        from .rede_neural import run as _rede, anotar_livros, precisa_treinar
        _r = _rede(treinar=precisa_treinar())
        c["rede_neural"] = {"validacao_cruzada": _r.get("validacao_cruzada"), "pendentes_provaveis_reais": _r.get("pendentes_provaveis_reais"),
                            "livros_com_nota": anotar_livros()}
    except Exception as ex:
        c["rede_neural"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: esteira de selos (bronze → prata → ouro), depois da nota da rede
        from .esteira import run as _esteira
        c["esteira_de_selos"] = _esteira()
    except Exception as ex:
        c["esteira_de_selos"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: descarte pelas estantes → restrição no motor de origem (ruído)
        from .descartes import run as _descartes
        c["descartes"] = _descartes()
    except Exception as ex:
        c["descartes"] = f"falhou: {type(ex).__name__}"
    try:                                     # 02/10: planos de correção de cada canal
        from .planos_correcao import run as _planos
        c["planos_de_correcao"] = _planos()
    except Exception as ex:
        c["planos_de_correcao"] = f"falhou: {type(ex).__name__}"
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
