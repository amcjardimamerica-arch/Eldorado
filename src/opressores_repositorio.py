"""MOTOR OPRESSOR = REPOSITÓRIO DE UMA OPORTUNIDADE (titular, 28/09).

Cada opressor guarda UMA oportunidade (um programa/edital recorrente de um financiador): as edições que já existiram
(com prazo, página oficial, condições comprovadas e o estudo do Interceptador), a edição atual e a previsão da
próxima. Serve de rota de busca (a página oficial) e de histórico para a análise preditiva.

  QUEM PRECISA TER   toda oportunidade com CRITÉRIO DE SELEÇÃO — edital, chamada, chamamento, prêmio, concurso,
                     credenciamento, seleção — aberta ou já encerrada (o histórico é o que permite prever).
  QUEM É DISPENSADO  empresa, doação, patrocínio, propaganda/publicidade e demais atos sem concorrência nem abertura a
                     todas as associações (inclusive emenda parlamentar, que é indicação); fica registrado o motivo.
  EDIÇÕES            a mesma oportunidade de anos diferentes cai no MESMO opressor (chave = programa + financiador,
                     sem anos, números de edital e "nª edição"); cada edição entra no histórico.
  PREVISÃO           com duas ou mais edições, o mês em que as inscrições costumam fechar dá a próxima janela.

Fontes: oportunidades abertas do fluxo validado e as oportunidades catalogadas na Biblioteca. O que a validação
descartou (não é oportunidade) não vira opressor. Grava o catálogo (biblioteca_alexandria/fontes/motores.json), os
ligados (estado/opressores.json) e o índice oportunidade → opressor (estado/opressores_indice.json).
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LIG = ROOT / "estado/opressores.json"
IDX = ROOT / "estado/opressores_indice.json"
FLUXO = ROOT / "docs/dados/fluxo_oportunidades.json"
FICHAS = ROOT / "biblioteca_alexandria/oportunidades"

SELECAO = re.compile(r"edital|chamad|chamamento|sele[cç][aã]o|pr[eê]mio|concurso|credenciamento|inscri[cç]|convocat|processo seletivo", re.I)
SEM_CONCORRENCIA = re.compile(r"doa[cç][aã]o|doa[cç][õo]es|patroc[ií]nio|patrocina|propaganda|publicidade|como solicitar|fale conosco|"
                              r"apoio institucional|emenda parlamentar|investimento social privado|responsabilidade social", re.I)


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def chave(titulo: str, orgao: str = "") -> str:
    t = unicodedata.normalize("NFKD", f"{titulo} {orgao}".lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\b(n[ºo°]\.?\s*\d+\s*[/\-]?\s*\d*|\d+\s*[ªº]|20\d\d|19\d\d|edicao|abre|abrem|inscricoes|inscricao|lanca|lancam|continue lendo)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", "", t)[:70]


NAO_E_SELECAO = re.compile(r"dispensa de (chamamento|licita)|inexigibilidade|pessoa[s]? f[ií]sica|credenciamento (de |para (os |a )?)?(profissionais|m[eé]dicos|pessoas|empresas?|leiloeir|hot[eé]is|prestadores)|"
                           r"leiloeir|concess[aã]o (de |onerosa)|contrata[cç][aã]o de profissionais|profissionais da (?:[aá]rea da )?sa[uú]de|"
                           r"preg[aã]o|licita[cç][aã]o|tomada de pre[cç]os|registro de pre[cç]os|contrata[cç][aã]o de empresa|termo aditivo|extrato", re.I)


def dispensa(item: dict) -> str | None:
    """Motivo da dispensa de opressor, ou None (precisa de opressor)."""
    t = f"{item.get('titulo') or ''} {item.get('orgao') or ''}"
    if NAO_E_SELECAO.search(t):     # 28/09: dispensa de chamamento, inexigibilidade, pessoa física, compra — não é seleção aberta a associações
        return "não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento de pessoa física ou compra)"
    # 01/10 (titular): parâmetros da Biblioteca na CRIAÇÃO — público municipal só de Goiás; empresa só como edital.
    try:
        from .curadoria_biblioteca import fora_da_abrangencia, empresa_sem_edital
        x = {"programa": item.get("titulo"), "orgao": item.get("orgao"), "geo": item.get("uf") or None,
             "pagina": item.get("pagina_oficial") or item.get("link_oficial") or item.get("url"), "origem": item.get("origem")}
        if not x["geo"]:
            from .livros_opressores import uf_do_dominio
            x["geo"] = uf_do_dominio(x["pagina"])[0]
        if fora_da_abrangencia(x):     # 14/10/2026 (titular, confirmado): só Goiás tem livros municipais
            return "fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros municipais)"
        if item.get("tipo") == "empresa/instituto" and empresa_sem_edital(x):
            return "empresa sem edital por concorrência: é fonte de busca, não livro"
    except Exception:
        pass
    return None


FINANCIADOR_INT = re.compile(r"\b(ford|gates|oak|rockefeller|skoll|kellogg|open society|mott|macarthur|packard|hewlett|bloomberg|wellcome|"
                             r"unesco|unicef|pnud|undp|onu|nações unidas|united nations|opas|oms|who\b|usaid|união europeia|european union|europeaid|"
                             r"erasmus|horizon europe|banco mundial|world bank|\bbid\b|banco interamericano|caf\b|jica|koica|giz\b|british council|"
                             r"goethe|institut français|alliance française|embaixada|embassy|consulado|fundo global|global fund|ars electronica)\b", re.I)
TLD_EXTERIOR = re.compile(r"\.(eu|int|de|fr|uk|us|ca|jp|kr|es|it|pt|nl|ch|at|se|no|dk|be|fi|ie|au|nz|mx|ar|cl|co|pe|uy)(/|$)|usaid\.gov|ec\.europa|\.un\.org|worldbank\.org|iadb\.org|\.art/.*(austria|europe)", re.I)


def internacional(x: dict) -> bool:
    """28/09 (titular): oportunidade INTERNACIONAL — financiador estrangeiro ou multilateral, ou página em domínio de
    outro país. 'Festival internacional' realizado no Brasil (ex.: FICA, em Goiás) NÃO conta."""
    t = f"{x.get('programa') or x.get('titulo') or ''} {x.get('orgao') or ''}"
    if re.search(r"(?i)festival internacional|mostra internacional|congresso internacional", t) and not FINANCIADOR_INT.search(t):
        return False
    if str(x.get("esfera") or "") == "Internacional" or str(x.get("familia") or "") == "Internacionais":
        return True
    pag = str(x.get("pagina") or x.get("link_oficial") or x.get("url") or "")
    host = re.sub(r"^https?://(www\.)?", "", pag).split("/")[0].lower()
    from .sites_oficiais import e_republicador
    return bool(FINANCIADOR_INT.search(t) or (host and not e_republicador(pag) and TLD_EXTERIOR.search(host + "/")))


def _edicao(item: dict, origem: str) -> dict:
    ano = (item.get("fim") or item.get("publicado_em") or item.get("data_publicacao") or "")[:4]
    return {k: v for k, v in {"id": item.get("id"), "titulo": str(item.get("titulo") or "")[:180], "ano": ano or None,
                              "publicado_em": item.get("publicado_em") or item.get("data_publicacao"), "inicio": item.get("inicio"),
                              "fim": item.get("fim") or item.get("prazo"), "pagina_oficial": item.get("link_oficial") or item.get("pagina_oficial"),
                              "uf": item.get("uf"), "condicoes": item.get("condicoes"), "estudo": item.get("inspecao"),
                              "decisao": (item.get("validacao") or {}).get("decisao") if isinstance(item.get("validacao"), dict) else item.get("decisao"),
                              "origem": origem}.items() if v not in (None, "", {})}


def _previsao(hist: list[dict]) -> dict | None:
    fins = sorted({h["fim"][:7] for h in hist if h.get("fim")})
    anos = {f[:4] for f in fins}
    if len(anos) < 2:
        return None
    mes = Counter(f[5:7] for f in fins).most_common(1)[0][0]
    hoje = date.today()
    ano = hoje.year if int(mes) >= hoje.month else hoje.year + 1
    return {"proxima_janela": f"{ano}-{mes}", "base": f"{len(fins)} edições em {len(anos)} anos", "confianca": "média" if len(anos) == 2 else "alta"}


def canonica_por_revisao() -> dict:
    """id → id da oportunidade CANÔNICA, pelos vereditos de duplicata da revisão humana (segue cadeias)."""
    try:
        V = json.loads((ROOT / "dados/editais/vereditos_revisao.json").read_text(encoding="utf-8")).get("vereditos") or {}
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for i, x in V.items():
        if x.get("veredito") != "duplicata" or not x.get("duplicata_de"):
            continue
        r, vis = str(x["duplicata_de"]), {i}
        while (V.get(r) or {}).get("veredito") == "duplicata" and (V.get(r) or {}).get("duplicata_de") and r not in vis:
            vis.add(r); r = str(V[r]["duplicata_de"])
        out[i] = r
    return out


def sincronizar() -> dict:
    C = _j(CAT, {"motores": []}); L = _j(LIG, {"ligados": {}}); L.setdefault("ligados", {})
    try:                                   # 29/09: opressor que a pesquisa dos 12 parâmetros descartou não religa
        from .parametros_opressores import dispensados
        _disp = dispensados()
    except Exception:
        _disp = set()
    try:
        from .validacao_mapa import carregar
        V = carregar()
    except Exception:
        V = {}
    por_chave, por_pag = {}, {}
    _pg = lambda u: re.sub(r"^https?://(www\.)?", "", str(u or "")).rstrip("/").lower()
    for x in C.get("motores") or []:
        por_chave.setdefault(chave(x.get("programa") or "", x.get("orgao") or ""), x)
        por_chave.setdefault(chave(x.get("programa") or ""), x)          # o fluxo criava opressor só com o título
        if x.get("pagina"):
            por_pag.setdefault(_pg(x["pagina"]), x)
    hoje = date.today(); idx = {}; st = Counter()
    # 11/10 (titular): UMA OPORTUNIDADE = UM LIVRO; duplicatas têm um único livro, o da oportunidade canônica.
    por_item = {}
    for x in C.get("motores") or []:
        for h in x.get("historico") or []:
            if isinstance(h, dict) and h.get("id"):
                por_item.setdefault(str(h["id"]), x)
    _canon = canonica_por_revisao()

    def opressor_de(item: dict, origem: str, aberta: bool) -> str:
        k = chave(item.get("titulo") or "", item.get("orgao") or "")
        x = por_chave.get(k) or por_chave.get(chave(item.get("titulo") or ""))
        pelo_nome = bool(x)
        if not x:
            x = por_pag.get(_pg(item.get("link_oficial") or item.get("pagina_oficial") or ""))
        # 01/10 (titular): PNAB e outros programas abrem VÁRIOS editais — cada edital tem o seu livro. Edital com número,
        # faixa, objeto ou cidade diferente não entra como "edição" de outro; pela página, só junta com o mesmo nome.
        if x:
            try:
                from .curadoria_biblioteca import editais_distintos, _base, GEN
                cand = {"programa": item.get("titulo"), "nome_classificado": item.get("titulo"), "livro": {"checklist": {"Objeto": {"v": item.get("objeto") or ""}}}}
                ultimos = [x] + [{"programa": h.get("titulo"), "nome_classificado": h.get("titulo")} for h in (x.get("historico") or [])[-6:]]
                distinto = any(editais_distintos(cand, o) for o in ultimos)
                if not pelo_nome:
                    da = {w for w in _base(cand).split() if w not in GEN and len(w) > 2}
                    db = {w for w in _base(x).split() if w not in GEN and len(w) > 2}
                    distinto = distinto or da != db
                if distinto:
                    k = k + "|" + chave(str(item.get("titulo") or "") + str(item.get("objeto") or ""))[:40] + "|" + "".join(re.findall(r"\d+", str(item.get("titulo") or "")))[:20]
                    x = por_chave.get(k)
            except Exception:
                pass
        _iid = str(item.get("id") or "")
        _x0 = por_item.get(_canon.get(_iid, _iid)) or por_item.get(_iid)     # duplicata → o livro da canônica
        if _x0 is not None:
            x = _x0
            if _canon.get(_iid, _iid) != _iid:
                st["duplicatas_no_livro_da_canonica"] += 1
        if not x:
            pag = item.get("link_oficial") or item.get("pagina_oficial") or item.get("url")
            x = {"id": "op-" + hashlib.sha1(k.encode()).hexdigest()[:12], "programa": str(item.get("titulo") or "")[:160],
                 "orgao": item.get("orgao") or "", "motor": "repositorio",
                 "familia": "Internacionais" if internacional({**item, "pagina": pag}) else "Oportunidade com seleção",
                 "esfera": "Internacional" if internacional({**item, "pagina": pag}) else ("Estado" if item.get("uf") else "Brasil"), "uf": item.get("uf") or "BR", "ativa": True,
                 "tipo": "repositorio_de_oportunidade", "pagina": pag, "paginas": [pag] if pag else [], "validacao": "não lida ainda",
                 "motivo_status": f"criado como repositório da oportunidade ({origem})", "criado_em": hoje.isoformat(), "historico": []}
            C.setdefault("motores", []).append(x); por_chave[k] = x; por_chave[chave(item.get("titulo") or "")] = x
            if pag: por_pag[_pg(pag)] = x
            st["criados_" + origem] += 1
        hist = x.setdefault("historico", [])
        e = _edicao(item, origem)
        if e.get("id"):
            por_item.setdefault(str(e["id"]), x); por_item.setdefault(_canon.get(str(e["id"]), str(e["id"])), x)
            if _canon.get(str(e["id"]), str(e["id"])) != str(e["id"]):
                e["duplicata_de"] = _canon[str(e["id"])]
        if e.get("id") and not any(h.get("id") == e["id"] for h in hist):
            hist.append(e); st["edicoes_novas"] += 1
        elif e.get("id"):
            for h in hist:
                if h.get("id") == e["id"]:
                    h.update({kk: vv for kk, vv in e.items() if vv})
        hist.sort(key=lambda h: str(h.get("fim") or h.get("publicado_em") or ""))
        x["edicoes"] = len(hist)
        pv = _previsao(hist)
        if pv:
            x["previsao"] = pv
        if aberta:
            x["atual"] = item.get("id")
            if item.get("fim"):
                x["proxima_data"] = {"inicio": item.get("inicio"), "fim": item.get("fim")}
            if item.get("link_oficial"):
                x["pagina"] = item["link_oficial"]
            if x["id"] not in L["ligados"] and x["id"] not in _disp:
                L["ligados"][x["id"]] = {"desde": hoje.isoformat(), "ate": (hoje + timedelta(days=30)).isoformat(),
                                         "origem": f"automática: repositório de oportunidade aberta ({origem})", "dias": 0, "ia": [], "itens": {}}
        return x["id"]

    # 1) oportunidades ABERTAS do fluxo validado
    F = _j(FLUXO, {})
    try:                                    # 11/10: duplicatas AUTOMÁTICAS (URL canônica, nº do edital + órgão — regra M1 do
        from .saneamento_motores import agrupar_duplicatas   # saneamento) também vão para o livro da canônica
        _todos = [x for L_ in (F.get("itens_por_uf") or {}).values() for x in L_]
        for _dup, _inf in (agrupar_duplicatas(_todos) or {}).items():
            _can = (_inf or {}).get("canonico") if isinstance(_inf, dict) else _inf
            if _can and str(_can) != str(_dup):
                _canon.setdefault(str(_dup), str(_can))
    except Exception:  # noqa: BLE001
        pass
    for uf, itens in (F.get("itens_por_uf") or {}).items():
        for it in itens:
            if (it.get("validacao") or {}).get("decisao") in ("descartada",):
                continue
            m = dispensa(it)
            if m:
                idx[it["id"]] = {"dispensa": m}; st["dispensadas"] += 1; continue
            if it.get("tipo") == "menção em diário oficial" and not SELECAO.search(it.get("titulo") or ""):
                idx[it["id"]] = {"dispensa": "menção em diário sem ato de seleção identificado"}; continue
            idx[it["id"]] = {"opressor": opressor_de(it, "aberta", True)}
    # 1b) 11/10 (titular): TODA oportunidade aberta do REPOSITÓRIO ÚNICO tem livro — inclusive as que vêm só da caixa
    #     dos motores (não passam pelo fluxo); as mesmas regras de dispensa valem
    _rep = _j(ROOT / "dados/oportunidades/repositorio_unico.json", {})
    for x in _rep.get("registros") or []:
        # 11/10: a arquivada (municipal de fora de GO) mantém o estado — o livro é criado/vinculado como o de qualquer aberta
        if x.get("estado") not in ("em_verificacao", "validada", "validacao_manual") or str(x.get("proximo_passo") or "").startswith("dispensar"):
            continue                                    # 11/10: o que vai ser dispensado (não é chamamento) não ganha livro
        _ja = [idx[i] for i in [x["id"]] + list(x.get("ids_origem") or []) if i in idx]
        if any("opressor" in j for j in _ja):
            continue
        _motivo = next((j.get("dispensa") for j in _ja if j.get("dispensa")), "") or ""
        if re.match(r"(?i)n[ãa]o [ée] sele[çc][ãa]o aberta|empresa sem edital", _motivo):
            continue                                    # não se aplica a OSC: o destino é a dispensa, não um livro
        it = {"id": x["id"], "titulo": x.get("titulo"), "orgao": x.get("orgao"), "link_oficial": x.get("link_oficial"), "url": x.get("url"),
              "fim": x.get("fim"), "uf": x.get("uf"), "origem": x.get("origem")}
        m = dispensa(it)
        if m and not re.match(r"(?i)sem crit[ée]rio de sele", m):     # 14/10: municipal de outro estado também não ganha livro
            idx[x["id"]] = {"dispensa": m}; st["dispensadas"] += 1; continue
        _lid = opressor_de(it, "aberta", True)                 # 11/10: aberta (por decisão da titular) → tem livro
        idx[x["id"]] = {"opressor": _lid}; st["do_repositorio_unico"] += 1
        if m:
            for _x in C.get("motores") or []:
                if _x.get("id") == _lid:
                    _x["abrangencia"] = m[:120]; break
    # 2) oportunidades CATALOGADAS na Biblioteca (histórico): encerradas também viram repositório
    for f in FICHAS.glob("*/*/ficha.json"):
        fi = _j(f, {})
        fid = fi.get("id") or f.parent.parent.name
        if fid in idx or (V.get(fid) or {}).get("decisao") == "descartada":
            continue
        tit = fi.get("titulo") or fi.get("programa") or ""
        if not tit or re.match(r"(?i)di[aá]rio oficial", tit):
            continue
        item = {"id": fid, "titulo": tit, "orgao": fi.get("orgao") or fi.get("financiador") or "", "uf": fi.get("uf"),
                "tipo": "empresa/instituto" if fi.get("nivel") in ("privado", "privada") else "ente público",
                "publicado_em": fi.get("data_publicacao"), "fim": fi.get("prazo") or fi.get("fim"), "pagina_oficial": fi.get("pagina_oficial") or fi.get("url"),
                "decisao": (V.get(fid) or {}).get("decisao")}
        m = dispensa(item)
        if m:
            idx[fid] = {"dispensa": m}; st["dispensadas_biblioteca"] += 1; continue
        if not SELECAO.search(f"{tit} {item['orgao']}"):
            idx[fid] = {"dispensa": "sem critério de seleção identificado no título"}; continue
        idx[fid] = {"opressor": opressor_de(item, "biblioteca", False)}
    # REPOSITÓRIO CRIADO PARA ATO QUE NÃO É SELEÇÃO (28/09): sai do catálogo
    antes = len(C["motores"])
    C["motores"] = [x for x in C["motores"] if x.get("parametros") or not (x.get("tipo") == "repositorio_de_oportunidade" and NAO_E_SELECAO.search(f"{x.get('programa') or ''} {x.get('orgao') or ''}"))]   # 30/09: pesquisado nunca sai
    # título que é data/hora ou lixo de página ("23 Set. 08:50 In…") não é oportunidade (28/09)
    _lixo = re.compile(r"^\s*\d{1,2}\s+[a-zç]{3}\.?\s+\d{1,2}:\d{2}|^\s*\d{1,2}:\d{2}\b|^\W*$", re.I)
    C["motores"] = [x for x in C["motores"] if x.get("parametros") or not (str(x.get("id", "")).startswith(("nova-", "op-")) and _lixo.search(str(x.get("programa") or "")))]
    st["repositorios_indevidos_removidos"] = antes - len(C["motores"])
    # LIGADO SEM OPRESSOR NÃO É FONTE MONITORADA (28/09): 33 ligados não existiam mais no catálogo e inflavam a contagem
    ids = {x.get("id") for x in C.get("motores") or []}
    orfaos = [k for k in L["ligados"] if k not in ids]
    for k in orfaos:
        L["ligados"].pop(k, None)
    st["ligados_orfaos_removidos"] = len(orfaos)
    # 11/10 (titular): RELATÓRIO DE APRENDIZADO da busca externa gravado no LIVRO da oportunidade
    try:
        _apr = (json.loads((ROOT / "estado/biblioteca/aprendizados_externos.json").read_text(encoding="utf-8")).get("aprendizados") or {})
        _por = {str(h.get("id")): x for x in C.get("motores") or [] for h in (x.get("historico") or []) if isinstance(h, dict) and h.get("id")}
        for oid, a in _apr.items():
            x = _por.get(_canon.get(oid, oid)) or _por.get(oid)
            if not x:
                continue
            ap = x.setdefault("aprendizados", [])
            if not any(z.get("oportunidade") == oid and z.get("em") == a.get("em") for z in ap):
                ap.append({"oportunidade": oid, **a}); x["aprendizados"] = ap[-10:]; st["aprendizados_gravados"] += 1
            if a.get("onde_estava") and str(a["onde_estava"]).startswith("http"):
                x["pagina_aprendida"] = a["onde_estava"]          # o livro passa a indicar onde o edital realmente estava
    except Exception:  # noqa: BLE001
        pass
    # 11/10 (titular): FORA DO PRAZO → o livro é ATUALIZADO e GUARDADO (arquivado, nunca apagado): a edição fica com a
    # situação 'encerrada' e o prazo; o livro sai das estantes ativas até chegar uma edição nova aberta
    try:
        _ver = (json.loads((ROOT / "dados/editais/vereditos_revisao.json").read_text(encoding="utf-8")).get("vereditos") or {})
        _enc = {i: x for i, x in _ver.items() if x.get("veredito") == "encerrada"}
        for x in C.get("motores") or []:
            hist = [h for h in (x.get("historico") or []) if isinstance(h, dict)]
            mudou = False
            for h in hist:
                v = _enc.get(str(h.get("id")))
                if v and h.get("situacao") != "encerrada":
                    h["situacao"] = "encerrada"; mudou = True
                    if (v.get("prazo") or {}).get("fim") and not h.get("fim"):
                        h["fim"] = v["prazo"]["fim"]
            if mudou or (hist and x.get("arquivado") is None and all(h.get("situacao") == "encerrada" for h in hist)):
                if hist and all(h.get("situacao") == "encerrada" for h in hist):
                    x["arquivado"] = {"em": hoje.isoformat(), "motivo": "prazo de inscrição vencido em todas as edições (revisão/busca externa)",
                                      "ultima_edicao": hist[-1].get("id")}
                    st["livros_arquivados"] += 1
            elif x.get("arquivado") and any(h.get("situacao") != "encerrada" for h in hist):
                x.pop("arquivado", None); st["livros_reabertos"] += 1        # edição nova aberta: volta à estante
    except Exception:  # noqa: BLE001
        pass
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    LIG.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
    IDX.write_text(json.dumps({"regra": __doc__.split("Fontes:")[0].strip(), "indice": idx}, ensure_ascii=False), encoding="utf-8")
    com_hist = [x for x in C["motores"] if len(x.get("historico") or []) >= 2]
    return {**st, "opressores": len(C["motores"]), "com_duas_ou_mais_edicoes": len(com_hist),
            "com_previsao": sum(1 for x in C["motores"] if x.get("previsao")), "indice": len(idx)}


if __name__ == "__main__":
    print(json.dumps(sincronizar(), ensure_ascii=False, indent=1))
