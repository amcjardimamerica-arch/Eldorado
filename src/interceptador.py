"""PILOTO - INTERCEPTADOR (titular, 26/09) — a segunda IA do sistema, com o mesmo modelo (Qwen3-8B).

O Espião descobre; o Interceptador COMPROVA. Ele não explora, não cria, não aposta. Pega os indícios de
oportunidade que já existem no sistema — a fila de resgate (o que o Espião achou nos sites do terceiro setor,
e os editais do acervo sem prazo, objeto ou página oficial) e os editais abertos do painel com itens em falta —
e, um por um:

    1. entende os dados já indicados;
    2. MAPEIA O SITE OFICIAL da oportunidade (conhecido, escolhido entre os links da divulgação, ou buscado);
    3. lê o documento/edital na fonte oficial e comprova as DOZE condições da oportunidade, cada uma com
       trecho literal encontrado no texto;
    4. para o que faltar, registra a dispensa só se o próprio edital a disser, com trecho.

Nada entra sem prova. O que ele confirma volta para a fila de resgate (o item vira 'resgatado' e vai à
Biblioteca), para o registro do edital (a ficha do painel) e para o bordo (prazo aberto confirmado = OURO).
"""
from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path

from .investigador import DOZE, investigar_um, registro
from .nucleo import load_json, now_iso, write_json

ROOT = Path(__file__).resolve().parents[1]
FILA = ROOT / "estado/piloto/fila_resgate.json"
ESTADO = ROOT / "estado/interceptador/estado.json"          # pasta PRÓPRIA: o Espião nunca a toca
PUB = ROOT / "docs/dados/interceptador.json"
BORDO_INT = ROOT / "estado/interceptador/bordo.json"
RELATORIOS = ROOT / "estado/interceptador/relatorios"
FONTES_EMPRESAS = ROOT / "estado/interceptador/fontes_empresas.json"
MOTOR = "piloto-aberto"        # o motor de busca aberta da família Piloto: as estrelas de ouro aparecem nele
REVISITA_DIAS = 7

# ── PARÂMETROS DO INTERCEPTADOR (titular, 26/09): distintos dos do Espião ────────────────────
CORTE = "2026-09-26"      # valida informação NOVA a partir daqui (titular, 26/09); nunca refaz o que já fez
PARAMETROS = {
    "regra": "um alvo por voo, a cada 3 segundos; nada entra sem trecho literal na fonte; dispensa só se o edital a disser; "
             "estuda o que os motores de busca e o Espião trouxerem — informação nova a partir de " + CORTE + " — e nunca refaz o que já fez",
    "finalidade": "levantar os dados mínimos de cada possibilidade (link original, fonte oficial, condições comprovadas, parecer 'como serve como fonte') "
                  "para a decisão externa do Claude, que analisa, valida ou descarta a cada 3 dias",
    "ordem_dos_alvos": ["1. edital NOVO trazido pelos motores de busca (descoberto desde o corte)", "2. indício NOVO trazido pelo Espião (candidatas)",
                        "3. oportunidade ABERTA atual com itens em falta (alimenta o que já está no painel)", "4. empresa NOVA do radar do Espião (ficha de fonte de recurso)"],
    "modos": {
        "validar": "editais dos motores de busca e oportunidades abertas atuais: mapear a fonte oficial e comprovar as doze condições",
        "complementar": "os achados do Piloto - Espião — indícios de edital e empresas sem edital (fontes de recurso)",
    },
    "padrao_de_qualidade_edital": {
        "validada": "prazo de inscrição comprovado NA FONTE OFICIAL + página oficial mapeada + pelo menos 9 das 12 condições comprovadas ou dispensadas",
        "parcial": "página oficial mapeada e pelo menos 6 condições",
        "insuficiente": "abaixo disso — o relatório diz o que faltou e onde procurar",
    },
    "padrao_de_qualidade_empresa": {
        "fonte_confirmada": "site oficial + canal de pedido (edital, formulário ou contato institucional) + áreas apoiadas, tudo com trecho; e pelo menos 5 dos 8 itens",
        "fonte_possivel": "site oficial + ao menos 3 itens",
        "sem_evidencia": "o resto",
    },
}

# ── FICHA DE FONTE DE RECURSO — para EMPRESAS sem edital (8 itens) ──────────────────────────
OITO = ["Site oficial", "Instituto, fundação ou programa social", "Canal de pedido", "Leis de incentivo que usa",
        "Áreas apoiadas", "Território de atuação social", "Porte do apoio", "Exigências para a entidade"]
ESQUEMA_EMPRESA = {
    "instituto": {"valor": "nome do instituto, fundação ou programa de investimento social, ou null", "trecho": "trecho literal"},
    "canal": {"valor": "edital|formulario|contato|patrocinio_por_proposta|nenhum", "url": "endereço ou null", "trecho": "trecho literal"},
    "leis": {"lista": ["rouanet|esporte|fia|idoso|pronon|pronas|goyazes|pat"], "trecho": "trecho literal"},
    "areas": {"lista": ["cultura|educacao|saude|assistencia_social|esporte|meio_ambiente|direitos|outros"], "trecho": "trecho literal"},
    "territorio": {"valor": "nacional|estados citados|municipios citados", "trecho": "trecho literal"},
    "porte": {"valor": "valores ou faixas de apoio como estão escritos, ou null", "trecho": "trecho literal"},
    "exigencias": {"lista": ["exigência para a entidade proponente"], "trecho": "trecho literal"},
}
PROMPT_EMPRESA = """Você é o Piloto - Interceptador. A empresa abaixo apareceu como possível FONTE DE RECURSOS (patrocínio, doação,
investimento social ou lei de incentivo) para organizações da sociedade civil. Leia o texto do site dela e responda ao
esquema. REGRAS: só o que está escrito; cada campo com "trecho" copiado LITERALMENTE (30 a 200 caracteres); sem trecho,
valor null. Devolva APENAS o JSON com as chaves do esquema.
EMPRESA: {nome}
ONDE FOI VISTA: {vias}
ESQUEMA: {esquema}
TEXTO DO SITE (pode estar truncado):
{texto}
"""
PROMPT_SERVE = """Você é o Piloto - Interceptador. Com base SOMENTE no que foi comprovado abaixo sobre «{titulo}», responda em JSON:
{{"serve_como_fonte": "sim|talvez|nao", "por_que": "uma ou duas frases", "para_a_amc": "o que uma associação comunitária de Goiânia
(assistência social, cultura, educação, esporte) precisaria fazer para acessar", "proximo_passo": "uma ação concreta", "risco": "o que pode impedir"}}
COMPROVADO: {comprovado}
NÃO ENCONTRADO: {faltou}
"""


def _mestre_por_url() -> dict:
    """Ids do arquivo mestre por URL — a fila de resgate guarda a URL; o registro do edital, o id."""
    from .investigador import _mestre
    return {v.get("url"): k for k, v in _mestre().items() if v.get("url")}


def alvos(maximo: int = 40) -> list[dict]:
    """Quem precisa de comprovação, em ordem: fila de resgate (mais urgente primeiro), depois os editais
    abertos do painel com itens em falta. Um alvo já interceptado só volta depois de REVISITA_DIAS."""
    est = load_json(ESTADO) if ESTADO.exists() else {}
    feitos = est.get("feitos") or {}
    def recente(k):
        return k in feitos                                     # nunca refaz o que já fez (titular, 26/09)
    out, vistos = [], set()
    fila = (load_json(FILA) or {}).get("itens") or {} if FILA.exists() else {}
    por_url = _mestre_por_url()
    for it in sorted(fila.values(), key=lambda x: -(x.get("urgencia") or 0)):
        if it.get("estado") == "resgatado":
            continue
        eid = it.get("id") if registro(str(it.get("id") or "")) else por_url.get(it.get("url"))
        if not eid and it.get("url") and it.get("id"):
            # indício vindo do catálogo do Espião: ainda não tem registro — o Interceptador cria um, a partir da fila
            eid = str(it["id"])
            arq = ROOT / "dados/editais/extraidos" / f"{eid}.json"
            if not arq.exists():
                write_json(arq, {"edital_id": eid, "titulo": it.get("titulo"), "url": it.get("url"), "orgao": it.get("orgao"),
                                 "fonte_nome": it.get("orgao"), "origem": "fila de resgate (catálogo do Espião)",
                                 "enquadramento": it.get("enquadramento"), "descoberto_em": it.get("descoberto_em")})
        if not eid or eid in vistos or recente(eid):
            continue
        vistos.add(eid); out.append({"id": eid, "de": "fila de resgate", "fila_id": it.get("id"), "titulo": it.get("titulo")})
        if len(out) >= maximo:
            return out
    # editais ABERTOS com itens em falta: o prazo aberto vive no registro (verificação do titular ou
    # investigação anterior), não no arquivo mestre — é por ele que o painel monta os cartões
    hoje = date.today().isoformat()
    for arq in sorted((ROOT / "dados/editais/extraidos").glob("*.json")):
        if len(out) >= maximo:
            break
        eid = arq.stem
        if eid in vistos or recente(eid):
            continue
        try:
            ex = json.loads(arq.read_text(encoding="utf-8"))
        except ValueError:
            continue
        ve = ex.get("verificacao_externa") if isinstance(ex.get("verificacao_externa"), dict) else {}
        prazo = str(ve.get("prazo") or ex.get("fim") or (ex.get("itens") or {}).get("prazo") or "")[:10]
        if not prazo or prazo < hoje:
            continue
        inv = ex.get("investigacao_ia") or {}
        if inv.get("comprovados", 0) >= len(DOZE):
            continue
        e = registro(eid) or {}
        if str(e.get("titulo") or "").startswith("Diário Oficial de") or not (e.get("url") or e.get("pagina_oficial")):
            continue
        vistos.add(eid); out.append({"id": eid, "de": "edital aberto com itens em falta", "titulo": e.get("titulo"), "prazo": prazo})
    return out


def _devolver_a_fila(alvo: dict, e_inv: dict) -> None:
    """O que foi comprovado volta à fila de resgate: prazo confirmado = item resgatado (e vai à Biblioteca)."""
    if not alvo.get("fila_id"):
        return
    try:
        from .missao_especial import registrar_resgate
        campos = e_inv.get("campos") or {}
        reg = registro(alvo["id"]) or {}
        dados = {"prazo": reg.get("fim"), "inicio": reg.get("inicio"), "pagina_oficial": reg.get("pagina_oficial"),
                 "objeto": reg.get("objeto"), "orgao": reg.get("orgao"), "valor": reg.get("valor_texto"),
                 "trecho": (campos.get("Prazo de inscrição") or {}).get("trecho")}
        registrar_resgate(alvo["fila_id"], {k: v for k, v in dados.items() if v})
    except Exception:
        pass


def _abate(alvo: dict, e_inv: dict) -> None:
    """Prazo aberto confirmado com trecho = estrela de OURO no motor do Piloto."""
    try:
        from .esquadrilha import abrir_missao, fechar_missao
        reg = registro(alvo["id"]) or {}
        fim = reg.get("fim")
        abrir_missao({"tipo": "interceptar", "motor": MOTOR, "ordem": 1, "alvo_id": alvo["id"], "_alvo": {"titulo": alvo.get("titulo")}}, "Piloto - Interceptador")
        achados = []
        if fim and fim >= date.today().isoformat() and (e_inv.get("campos") or {}).get("Prazo de inscrição", {}).get("comprovado"):
            achados.append({"titulo": reg.get("titulo"), "url": reg.get("pagina_oficial") or reg.get("url"), "prazo": fim,
                            "situacao": "aberta", "resgate": True, "novo": False})
        fechar_missao(f"{e_inv.get('comprovados', 0)}/{len(DOZE)} comprovados", achados,
                      f"interceptador · {(reg.get('titulo') or '')[:60]}: {e_inv.get('comprovados', 0)}/{len(DOZE)} itens comprovados ou dispensados")
    except Exception:
        pass


def qualidade_edital(reg: dict, inv: dict) -> str:
    campos = inv.get("campos") or {}
    n = sum(1 for v in campos.values() if v.get("comprovado") or v.get("dispensado"))
    prazo_of = (campos.get("Prazo de inscrição") or {}).get("comprovado") and (campos.get("Prazo de inscrição") or {}).get("fonte_oficial")
    if prazo_of and reg.get("pagina_oficial") and n >= 9:
        return "validada"
    if reg.get("pagina_oficial") and n >= 6:
        return "parcial"
    return "insuficiente"


def parecer_fonte(ia, titulo: str, inv: dict) -> dict:
    """A pergunta do titular: como esta busca inicial pode servir como fonte de recursos?"""
    campos = inv.get("campos") or {}
    comp = {k: v.get("valor") for k, v in campos.items() if v.get("comprovado") or v.get("dispensado")}
    falt = [k for k, v in campos.items() if not (v.get("comprovado") or v.get("dispensado"))]
    r = ia.perguntar(PROMPT_SERVE.format(titulo=titulo[:160], comprovado=json.dumps(comp, ensure_ascii=False)[:3000], faltou=", ".join(falt) or "nada"),
                     '{"serve_como_fonte","por_que","para_a_amc","proximo_passo","risco"}')
    return r if isinstance(r, dict) else {"serve_como_fonte": "indefinido", "por_que": "o modelo não respondeu"}


def _abate_proprio(reg: dict, inv: dict, alvo: dict) -> None:
    """Bordo PRÓPRIO do Interceptador (o Espião grava o dele por cima do que tinha; arquivos separados não colidem).
    Prazo aberto comprovado na fonte = OURO; o painel soma os dois bordos."""
    b = load_json(BORDO_INT) if BORDO_INT.exists() else {"abates": {}, "missoes": []}
    e = b["abates"].setdefault(MOTOR, {"n": 0, "ouro": 0, "prata": 0, "ultimos": []})
    fim = reg.get("fim"); pz = (inv.get("campos") or {}).get("Prazo de inscrição") or {}
    url = reg.get("pagina_oficial") or reg.get("url")
    if fim and fim >= date.today().isoformat() and pz.get("comprovado") and url and url not in {x.get("url") for x in e["ultimos"]}:
        e["ouro"] += 1; e["n"] = e["ouro"] + e["prata"]
        e["ultimos"] = ([{"titulo": (reg.get("titulo") or "")[:80], "url": url, "tipo": "ouro", "em": date.today().isoformat(), "papel": "Piloto - Interceptador"}] + e["ultimos"])[:40]
    b["missoes"] = ([{"tipo": "interceptar", "modo": alvo.get("modo"), "alvo": (reg.get("titulo") or "")[:80], "comprovados": inv.get("comprovados"), "em": now_iso()}] + b["missoes"])[:60]
    b["total_abates"] = sum(v.get("n", 0) for v in b["abates"].values())
    write_json(BORDO_INT, b)


def investigar_empresa(ia, emp: dict) -> dict:
    """Empresa sem edital: a ficha de fonte de recurso (8 itens), lida no site oficial dela."""
    from .investigador import texto_do_edital, comprovado, _norm, _recortar
    nome = emp.get("empresa") or emp.get("nome") or ""
    site = emp.get("site") or emp.get("dominio")
    if site and not str(site).startswith("http"):
        site = "https://" + str(site)
    if not site:
        try:
            from .piloto_busca import buscar
            r = next((x for x in (buscar(f"{nome} site oficial instituto responsabilidade social", maximo=5) or []) if x.get("url") and not re.search(r"wikipedia|linkedin|facebook|instagram", x["url"])), None)
            site = r["url"] if r else None
        except Exception:
            site = None
    ficha = {"empresa": nome, "em": now_iso(), "site_oficial": site, "itens": {}, "qualidade": "sem_evidencia"}
    if not site:
        ficha["erro"] = "site oficial não encontrado"; return ficha
    texto, fontes = texto_do_edital({"pagina_oficial": site, "anexos": []})
    if not texto.strip():
        ficha["erro"] = "site sem texto legível"; return ficha
    r = ia.perguntar(PROMPT_EMPRESA.format(nome=nome, vias=", ".join(emp.get("vias") or []), esquema=json.dumps(ESQUEMA_EMPRESA, ensure_ascii=False), texto=_recortar(texto, 30_000)),
                     json.dumps(ESQUEMA_EMPRESA, ensure_ascii=False))
    tn = _norm(texto); itens = {"Site oficial": {"valor": site, "comprovado": True}}
    def ok(b, curto=False): return isinstance(b, dict) and comprovado(b.get("trecho") or "", tn, curto)
    g = lambda k: (r or {}).get(k) if isinstance((r or {}).get(k), dict) else {}
    b = g("instituto"); itens["Instituto, fundação ou programa social"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": ok(b) and bool(b.get("valor"))}
    b = g("canal"); itens["Canal de pedido"] = {"valor": b.get("valor"), "url": b.get("url"), "trecho": b.get("trecho"), "comprovado": ok(b) and str(b.get("valor")) not in ("", "None", "nenhum", "null")}
    # leis: o texto do site OU o histórico público (SALIC) comprovam
    hist = []
    try:
        idx = load_json(ROOT / "docs/dados/doadoras/indice.json") or {}
        kn = re.sub(r"[^a-z0-9]", "", nome.lower())
        hist = [x.get("l", ["Rouanet"]) for x in idx.get("empresas", []) if kn and re.sub(r"[^a-z0-9]", "", str(x.get("n", "")).lower()).startswith(kn[:12])][:1]
    except Exception:
        pass
    b = g("leis"); leis = sorted({str(x).lower() for x in (b.get("lista") or []) if x} | {l.lower() for h in hist for l in h})
    itens["Leis de incentivo que usa"] = {"valor": ", ".join(leis) or None, "trecho": b.get("trecho") or ("histórico público (SALIC)" if hist else None), "comprovado": bool(hist) or (ok(b, True) and bool(leis))}
    b = g("areas"); areas = [str(x).lower() for x in (b.get("lista") or []) if x]; itens["Áreas apoiadas"] = {"valor": ", ".join(areas) or None, "trecho": b.get("trecho"), "comprovado": ok(b, True) and bool(areas)}
    b = g("territorio"); itens["Território de atuação social"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": ok(b, True) and bool(b.get("valor"))}
    b = g("porte"); itens["Porte do apoio"] = {"valor": b.get("valor"), "trecho": b.get("trecho"), "comprovado": ok(b) and bool(re.search(r"\d|mil|milh", str(b.get("valor") or ""), re.I))}
    b = g("exigencias"); ex = [str(x)[:120] for x in (b.get("lista") or []) if x]; itens["Exigências para a entidade"] = {"valor": ", ".join(ex)[:300] or None, "trecho": b.get("trecho"), "comprovado": ok(b) and bool(ex)}
    n = sum(1 for v in itens.values() if v.get("comprovado"))
    ficha["itens"] = itens; ficha["comprovados"] = n; ficha["total"] = len(OITO)
    ficha["qualidade"] = "fonte_confirmada" if (itens["Canal de pedido"]["comprovado"] and itens["Áreas apoiadas"]["comprovado"] and n >= 5) else ("fonte_possivel" if n >= 3 else "sem_evidencia")
    ficha["fontes"] = fontes
    return ficha


def empresas_pendentes() -> list[dict]:
    """Empresas do radar do Espião que ainda não têm ficha de fonte de recurso."""
    try:
        from .reconhecimento import alvos as _radar
        feitas = (load_json(FONTES_EMPRESAS) or {}).get("fichas", {}) if FONTES_EMPRESAS.exists() else {}
        out = []
        for k, v in (_radar().get("itens") or {}).items():
            nome = v.get("empresa")
            if nome and nome not in feitas:
                out.append({"chave": k, "empresa": nome, "vias": v.get("vias") or [], "site": v.get("site") or v.get("dominio"), "onde": (v.get("onde_foi_vista") or [])[:2]})
        return out
    except Exception:
        return []


def novos_dos_motores(maximo: int = 30) -> list[dict]:
    """Editais que os MOTORES trouxeram desde o corte — os que ainda não foram estudados."""
    from .investigador import _mestre
    est = load_json(ESTADO) if ESTADO.exists() else {}
    feitos = est.get("feitos") or {}
    out = []
    for eid, m in _mestre().items():
        d = str(m.get("descoberto_em") or m.get("coletado_em") or "")[:10]
        if d < CORTE or eid in feitos or not m.get("url"):
            continue
        if m.get("fonte_id") == "querido-diario" or str(m.get("titulo") or "").startswith("Diário Oficial de"):
            continue
        if m.get("estado_export") in ("arquivado", "excluido") or (m.get("fim") and m["fim"] < date.today().isoformat()):
            continue
        out.append({"id": eid, "de": "edital novo dos motores", "titulo": m.get("titulo"), "fonte": m.get("fonte_id"), "descoberto_em": d})
    out.sort(key=lambda x: x["descoberto_em"], reverse=True)
    return out[:maximo]


def proximo_alvo() -> dict | None:
    """UM ALVO POR VOO, na ordem dos parâmetros: novo dos motores → novo do Espião → aberto atual com falta →
    empresa nova. Quem já foi estudado não volta (memória em estado/interceptador)."""
    est = load_json(ESTADO) if ESTADO.exists() else {}
    feitos = est.get("feitos") or {}
    nm = [a for a in novos_dos_motores() if a["id"] not in feitos]
    if nm:
        return {**nm[0], "modo": "validar", "tipo": "edital"}
    lista = alvos(60)
    fila = [a for a in lista if a["de"] == "fila de resgate" and a["id"] not in feitos]
    if fila:
        return {**fila[0], "modo": "complementar", "tipo": "edital"}
    abertos = [a for a in lista if a["de"] == "edital aberto com itens em falta" and a["id"] not in feitos]
    if abertos:
        return {**abertos[0], "modo": "validar", "tipo": "edital"}
    emp = [e for e in empresas_pendentes() if e["chave"] not in feitos]
    if emp:
        return {**emp[0], "id": emp[0]["chave"], "modo": "complementar", "tipo": "empresa", "de": "radar do Espião", "titulo": emp[0]["empresa"]}
    return None


def voo(ia) -> dict:
    """Um voo do Interceptador: um alvo, relatório ao pousar."""
    t0 = time.time()
    a = proximo_alvo()
    est = load_json(ESTADO) if ESTADO.exists() else {"feitos": {}, "rodadas": []}
    est.setdefault("feitos", {}); est.setdefault("rodadas", [])
    rel = {"em": now_iso(), "papel": "Piloto - Interceptador", "modelo": "qwen3-8b", "parametros": PARAMETROS["regra"]}
    if not a:
        rel["resultado"] = "nada a interceptar: sem edital aberto com itens em falta, sem indício na fila, sem empresa sem ficha"
    elif a["tipo"] == "empresa":
        f = investigar_empresa(ia, a)
        F = load_json(FONTES_EMPRESAS) if FONTES_EMPRESAS.exists() else {"fichas": {}}
        F.setdefault("fichas", {})[a["empresa"]] = f; write_json(FONTES_EMPRESAS, F)
        rel.update({"modo": a["modo"], "tipo": "empresa", "alvo": a["empresa"], "de": a["de"], "qualidade": f.get("qualidade"),
                    "comprovados": f.get("comprovados"), "total": f.get("total"), "site_oficial": f.get("site_oficial"), "erro": f.get("erro"),
                    "itens": {k: {"valor": v.get("valor"), "comprovado": v.get("comprovado")} for k, v in (f.get("itens") or {}).items()}})
        est["feitos"][a["id"]] = {"em": now_iso(), "tipo": "empresa", "qualidade": f.get("qualidade")}
    else:
        x = investigar_um(a["id"], ia, "qwen3-8b")
        reg = registro(a["id"]) or {}; inv = reg.get("investigacao_ia") or {}
        q = qualidade_edital(reg, inv) if "erro" not in x else "insuficiente"
        par = parecer_fonte(ia, reg.get("titulo") or a.get("titulo") or "", inv) if inv.get("campos") else {}
        inv["qualidade"] = q; inv["parecer_fonte"] = par
        arq = ROOT / "dados/editais/extraidos" / f"{a['id']}.json"
        if arq.exists():
            e = json.loads(arq.read_text(encoding="utf-8")); e["investigacao_ia"] = inv; arq.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        _devolver_a_fila(a, inv); _abate_proprio(reg, inv, a)
        try:
            from .fontes_novas import agregar_pagina_oficial
            rel["fonte_nova_para_os_motores"] = agregar_pagina_oficial(reg)
        except Exception:
            pass
        rel.update({"modo": a["modo"], "tipo": "edital", "alvo": reg.get("titulo") or a.get("titulo"), "de": a["de"], "qualidade": q,
                    "comprovados": x.get("comprovados"), "dispensados": x.get("dispensados"), "total": len(DOZE),
                    "nao_resolvidos": x.get("nao_resolvidos"), "pagina_oficial": x.get("pagina_oficial"), "passos": x.get("passos"),
                    "fontes_oficiais": [c for c, v in (inv.get("campos") or {}).items() if v.get("fonte_oficial")],
                    "parecer_fonte": par, "erro": x.get("erro")})
        est["feitos"][a["id"]] = {"em": now_iso(), "tipo": "edital", "qualidade": q, "comprovados": x.get("comprovados"), "de": a["de"]}
    try:
        from .para_claude import montar as _para_claude
        rel["para_o_claude"] = _para_claude()
    except Exception as ex:
        rel["para_o_claude"] = f"falhou: {type(ex).__name__}"
    rel["segundos"] = round(time.time() - t0)
    est["rodadas"] = (est["rodadas"] + [{k: v for k, v in rel.items() if k not in ("passos", "itens")}])[-60:]
    write_json(ESTADO, est)
    RELATORIOS.mkdir(parents=True, exist_ok=True)
    write_json(RELATORIOS / f"{date.today().isoformat()}.json", {"dia": date.today().isoformat(), "voos": ([v for v in (load_json(RELATORIOS / f"{date.today().isoformat()}.json") or {}).get("voos", [])] if (RELATORIOS / f"{date.today().isoformat()}.json").exists() else []) + [rel]})
    fe = est["feitos"]
    write_json(PUB, {**rel, "acumulado": {"interceptados": len(fe), "validadas": sum(1 for v in fe.values() if v.get("qualidade") == "validada"),
                                          "parciais": sum(1 for v in fe.values() if v.get("qualidade") == "parcial"),
                                          "fontes_confirmadas": sum(1 for v in fe.values() if v.get("qualidade") == "fonte_confirmada")},
                     "parametros": PARAMETROS, "ultimos_voos": est["rodadas"][-6:]})
    return rel


def rodada(ia, minutos: float = 280, maximo: int = 40) -> dict:
    fim = time.time() + minutos * 60
    est = load_json(ESTADO) if ESTADO.exists() else {"feitos": {}, "rodadas": []}
    est.setdefault("feitos", {}); est.setdefault("rodadas", [])
    lista = alvos(maximo)
    r = {"em": now_iso(), "papel": "Piloto - Interceptador", "modelo": "qwen3-8b", "alvos": len(lista), "editais": []}
    for a in lista:
        if time.time() > fim:
            r["parou"] = "tempo da rodada esgotado"; break
        x = investigar_um(a["id"], ia, "qwen3-8b")
        x["de"] = a["de"]
        r["editais"].append(x)
        e_inv = (registro(a["id"]) or {}).get("investigacao_ia") or {}
        _devolver_a_fila(a, e_inv)
        _abate(a, e_inv)
        est["feitos"][a["id"]] = {"em": now_iso(), "comprovados": x.get("comprovados"), "de": a["de"]}
        write_json(ESTADO, est)
        print(f"{a['id']} · {x.get('comprovados', '-')}/{len(DOZE)} · {x.get('s', '-')} s · {a['de']} · {str(a.get('titulo'))[:60]} · {x.get('erro') or ''}", flush=True)
    r["resumo"] = {"interceptados": len(r["editais"]),
                   "media_itens": round(sum(x.get("comprovados", 0) for x in r["editais"]) / max(1, len(r["editais"])), 1),
                   "completos": sum(1 for x in r["editais"] if x.get("comprovados") == len(DOZE)),
                   "com_prazo_confirmado": sum(1 for x in r["editais"] if "Prazo de inscrição" not in (x.get("nao_resolvidos") or []) and "comprovados" in x)}
    est["rodadas"] = (est["rodadas"] + [{k: v for k, v in r.items() if k != "editais"}])[-30:]
    write_json(ESTADO, est)
    PUB.parent.mkdir(parents=True, exist_ok=True)
    write_json(PUB, {**r, "editais": [{k: v for k, v in x.items() if k != "passos"} for x in r["editais"]],
                     "acumulado": {"interceptados": len(est["feitos"]), "rodadas": len(est["rodadas"])}})
    return r
