"""FLUXO DAS OPORTUNIDADES (titular, 27/09) — do que é encontrado ao mapa, ao calendário e à previsão.

    1. ENCONTRADAS   tudo o que os motores, o Espião e o Interceptador trouxeram
                     (arquivo mestre · candidatas do Espião · registros estudados pelo Interceptador)
    2. ÚNICAS        a mesma oportunidade conta uma vez (endereço e título normalizados)
    3. POSSÍVEIS     abertas ou possivelmente abertas: prazo ainda não vencido, ou sem prazo e publicada nos
                     últimos 60 dias — mesmo sem informação nenhuma (menção em diário oficial conta)
    4. CONFIRMADAS   com o MÍNIMO: objeto + data-limite de inscrição ainda aberta + link do site oficial
                     (de empresa, instituto ou ente público)
    5. OPRESSOR      oportunidade nova (não coberta por opressor existente) gera um motor opressor próprio,
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
    for arq in EXT.glob("*.json"):
        e = _j(arq, {})
        if e.get("investigacao_ia") and arq.stem.startswith(("cat-", "op-")):
            brutos.append(("Piloto - Interceptador", {"id": arq.stem, "titulo": e.get("titulo"), "url": e.get("url"), "orgao": e.get("orgao"),
                                                      "descoberto_em": str((e.get("investigacao_ia") or {}).get("em", ""))[:10], "fonte_id": "piloto-interceptador"}))
    # NÃO É OPORTUNIDADE (27/09): pauta legislativa, assembleia, contrato já assinado, resultado e lista de aprovados.
    # Retificação e alteração de cronograma FICAM: indicam edital aberto.
    RUIDO = re.compile(r"^\s*\d{1,2}:\d{2}\b|vota[cç][õo]es|requerimentos|t[ií]tulos? de cidadania|utilidades? p[uú]blica|convoca[cç][aã]o de assembleia|"
                       r"^\s*extrato|resultado|lista de aprovados|aprovados e suplentes|heteroidentifica|homologa|inexigibilidade|dispensa de chamamento|termo aditivo", re.I)
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
        uf = str(m.get("uf") or e.get("uf") or "").upper()
        # fluxo contínuo: o próprio edital dispensa a data-limite (validação no site oficial) — vale como prazo aberto
        prazo_disp = bool(v and v["decisao"].startswith("valida") and ((v.get("doze_itens") or {}).get("Prazo de inscrição") or {}).get("status") == "dispensado pelo edital")
        confirmada = bool(objeto and link and ((fim and fim >= hoje.isoformat()) or (prazo_disp and not fim)))
        if v and v["decisao"] == "pendente":
            confirmada = False                                # a validação não achou a fonte oficial: não confirma
        insp = None
        if inv.get("em"):
            po = e.get("pagina_oficial")
            from .sites_oficiais import e_republicador as _rep
            po_ok = bool(po and not _rep(po))
            insp = {"em": str(inv.get("em"))[:16], "qualidade": inv.get("qualidade"), "comprovados": inv.get("comprovados"),
                    "prazo": fim, "pagina_oficial": po if po_ok else None,
                    "ok": bool(fim and po_ok)}          # verde = achou prazo E site oficial; vermelho = não achou
        out.append({"id": m.get("id"), "titulo": re.sub(r"(?i)^continue lendo\s+", "", tit)[:180], "orgao": m.get("orgao") or e.get("orgao"),
                    "uf": uf if uf in UFS else None, "origem": origem, "tipo": "menção em diário oficial" if diario else ("empresa/instituto" if (m.get("nivel") in ("privada", "privado") or origem.startswith("Piloto")) else "ente público"),
                    "publicado_em": pub, "inicio": _d(e.get("inicio"), ve.get("inicio")), "fim": fim, "link_oficial": link,
                    "objeto": str(objeto)[:240] if objeto else None, "confirmada": confirmada, "url": m.get("url"), "inspecao": insp,
                    "validacao": ({"decisao": v["decisao"], "motivo": v.get("motivo"), "em": v.get("validado_em")} if v else None)})
    return out


def _tipo_ciclo(t: str) -> str:
    rec = re.search(r"fundo|programa|conv[eê]nio|anual|lei |pnab|rouanet|destina[cç]|permanente|fluxo cont", t, re.I)
    pon = re.search(r"edital|chamamento|n[ºo°] ?\d|/20\d\d|pr[eê]mio", t, re.I)
    return "recorrente" if rec and not pon else "pontual" if pon else "indefinido"


def opressores_e_preditivo(itens: list[dict]) -> dict:
    """Oportunidade nova (não coberta) → opressor próprio ligado por 30 dias + cadastro preditivo."""
    C = _j(CAT_OPR, {"motores": []}); L = _j(EST_OPR, {"ligados": {}})
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
        if pagina and cara and ku not in cobertos_u and kt not in cobertos_t:
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


def montar() -> dict:
    itens = consolidar()
    etapa = opressores_e_preditivo(itens)
    mapa = {}
    for it in itens:
        k = it["uf"] or "__nac__"
        p = mapa.setdefault(k, {"confirmadas": 0, "possiveis": 0})
        p["possiveis"] += 1; p["confirmadas"] += 1 if it["confirmada"] else 0
    tot = {"confirmadas": sum(v["confirmadas"] for v in mapa.values()), "possiveis": sum(v["possiveis"] for v in mapa.values())}
    cal = [{k: it.get(k) for k in ("id", "titulo", "orgao", "uf", "inicio", "fim", "link_oficial", "origem")} for it in itens if it["confirmada"]]
    res = {"em": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "regra": __doc__.split("Publica")[0].strip(),
           "etapas": {"possiveis_abertas": tot["possiveis"], "confirmadas_com_minimo": tot["confirmadas"],
                      "por_origem": {o: sum(1 for x in itens if x["origem"].startswith(o)) for o in ("motor", "Piloto - Espião", "Piloto - Interceptador")},
                      "por_tipo": {t: sum(1 for x in itens if x["tipo"] == t) for t in ("ente público", "empresa/instituto", "menção em diário oficial")},
                      "por_validacao": {d: sum(1 for x in itens if (x.get("validacao") or {}).get("decisao") == d) for d in ("valida_aberta", "valida_fora_abrangencia", "pendente")},
                      "triagem": dict(TRIAGEM), **etapa},
           "mapa": {"total": tot, "por_uf": mapa}, "calendario": cal,
           "confirmadas": [x for x in itens if x["confirmada"]][:300],
           "itens_por_uf": {k: sorted([{kk: x.get(kk) for kk in ("id", "titulo", "url", "link_oficial", "fim", "tipo", "origem", "confirmada", "inspecao", "orgao", "publicado_em", "validacao")}
                                       for x in itens if (x["uf"] or "__nac__") == k], key=lambda y: (not y["confirmada"], not y["inspecao"], str(y.get("fim") or "9"), y["titulo"]))
                            for k in mapa},
           "possiveis_sem_minimo": [x for x in itens if not x["confirmada"] and x["tipo"] != "menção em diário oficial"][:300]}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"mapa_total": tot, **res["etapas"]}


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=1))
