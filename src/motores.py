"""Motores de Busca — os 260 pontos de captação, um motor por ponto.

O titular quer ver, na Bússola, todos os 260 pontos agregados por TIPO e
segmentados por território: Rouanet é nacional; a Aldir Blanc tem um bloco
estadual (todos os editais do Estado) e um municipal (todos os de Goiânia).
Com filtro de estado e de quais editais buscar. Cada ponto mostra as 11
camadas (Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor,
Órgão/financiador, Território, Esfera, Requisitos, Anexos, Destinação), o link
da página de publicação e a validação do conteúdo pelo motor — e um
diagnóstico quando faltam camadas: o que falta, a causa e a ação.

Este módulo monta o fragmento `docs/dados/motores.json` (compacto). O botão
"Ativar motor" no painel gera o pedido com os pontos selecionados; a execução
real acontece no GitHub Actions (workflow_dispatch com o campo `fontes`), que
lê o pedido e roda só os motores escolhidos.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date

from .nucleo import ROOT, load_json, now_iso, slug, write_json

CAMADAS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor",
           "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação",
           "Área de atuação")

_FAMILIAS = [
    (r"pnab|aldir", "PNAB / Aldir Blanc"), (r"rouanet|pronac", "Lei Rouanet"),
    (r"goyazes", "Lei Goyazes"), (r"incentivo ao esporte|\blie\b", "Lei de Incentivo ao Esporte"),
    (r"emenda", "Emendas parlamentares"), (r"fmdca|cmdca|crian", "Fundo da Criança (FMDCA/FIA)"),
    (r"fmas|cmas|assist", "Assistência social (FMAS/FEAS)"), (r"idos", "Fundo do Idoso"),
    (r"pronon|pronas", "PRONON / PRONAS"), (r"tjgo|vara|justi[çc]a|cnj|presta[çc][ãa]o", "Destinação judicial"),
    (r"mpgo|mpf|minist[ée]rio p[úu]blico|\btac\b", "Ministério Público"),
    (r"receita federal|apreendid", "Receita Federal (doação)"), (r"sebrae", "Sebrae"),
    (r"bndes|amaz[ôo]nia", "BNDES"),
    (r"funda[çc][ãa]o|instituto|grupo|coca|natura|ita[úu]|bradesco|telef[ôo]nica|vale|claro|renner|neoenergia|sabin|sicoob|unibanco|votorantim|localiza|arcelor", "Fundações e institutos privados"),
    (r"unesco|unicef|banco mundial|\bbid\b|usaid|pnud|ford|open society|gates|skoll|echoing|rockefeller|oak|google|meta|microsoft|europ|climate|gef", "Internacionais"),
]


def familia(programa: str) -> str:
    p = (programa or "").lower()
    for rx, nome in _FAMILIAS:
        if re.search(rx, p):
            return nome
    return "Outros programas"


def segmento(f: dict) -> str:
    """Nacional / Estadual GO / Municipal Goiânia / Privado / Internacional."""
    n = f.get("nivel")
    if n == "federal":
        return "Nacional"
    if n == "estadual":
        return f'Estadual {f.get("uf") or ""}'.strip()
    if n == "municipal":
        return "Municipal Goiânia" if (f.get("goias") or (f.get("uf") == "GO")) else "Municipal"
    if n == "internacional":
        return "Internacional"
    return "Privado"


def _ultimo_edital_da_fonte(fonte: dict, con) -> dict | None:
    """O edital mais recente do acervo ligado ao órgão desta fonte."""
    toks = [t for t in re.findall(r"[a-zà-ú]{5,}", (fonte.get("orgao") or "").lower())
            if t not in ("secretaria", "municipal", "estadual", "federal", "governo", "estado", "goiás", "goiania", "goiânia", "programa", "fundo")]
    if not toks:
        return None
    rows = con.execute("SELECT ficha FROM historico ORDER BY data_publicacao DESC LIMIT 6000").fetchall()
    for (fj,) in rows:
        f = json.loads(fj)
        alvo = f'{f.get("financiador","")} {f.get("titulo","")}'.lower()
        if sum(1 for t in toks if t in alvo) >= max(1, min(2, len(toks))):
            return f
    return None


def _edital_manual_da_fonte(fonte_id: str) -> dict | None:
    """Documento enviado pelo titular para esta fonte — fonte MÁXIMA, prevalece."""
    base = ROOT / "biblioteca_alexandria/oportunidades"
    melhor = None
    for fp in base.glob("*/*/ficha.json"):
        try:
            f = load_json(fp)
        except Exception:
            continue
        if f.get("origem") == "alimentacao_manual" and f.get("fonte_id") == fonte_id:
            if melhor is None or (f.get("enviado_em") or "") > (melhor.get("enviado_em") or ""):
                rc = fp.parent / "requisitos_condicoes_valores.json"
                f["requisitos_condicoes_valores"] = _camadas_de_itens(f, load_json(rc).get("itens", {})) if rc.exists() else None
                melhor = f
    return melhor


def _camadas_de_itens(ficha: dict, itens: dict) -> dict:
    """Converte a extração do documento nos 11 itens do padrão."""
    marcos = {m.get("tipo"): m for m in ficha.get("marcos") or []}
    val = [
        ("Objeto", itens.get("objeto") or ficha.get("objeto")),
        ("Prazo de inscrição", (f'{ficha.get("inicio") or "?"} a {ficha["fim"]}' if ficha.get("fim") else None)),
        ("Resultado", (marcos.get("resultado_preliminar") or {}).get("data_texto")),
        ("Prazo de recurso", (marcos.get("recurso") or {}).get("data_texto")),
        ("Valor", (ficha.get("valores_citados") or [None])[0]),
        ("Órgão / financiador", ficha.get("financiador") or ficha.get("fonte_nome")),
        ("Território", ficha.get("uf") or ficha.get("territorio")),
        ("Esfera", ficha.get("nivel")),
        ("Requisitos", ", ".join(ficha.get("exigencias_detectadas") or []) or None),
        ("Anexos", ", ".join(ficha.get("anexos_no_ato") or ficha.get("modelos") or []) or None),
        ("Destinação", (ficha.get("destinacao") or {}).get("motivo")),
        ("Área de atuação", (lambda a: None if a in (None, "outros") else a)(ficha.get("area"))),
    ]
    return {"itens": [{"item": k, "valor": (str(v)[:200] if v else None), "comprovado": bool(v)} for k, v in val]}


def camadas_da_fonte(fonte: dict, edital: dict | None) -> list[dict]:
    """As 11 camadas com o valor real (ou lacuna) — a partir do último edital."""
    itens = ((edital or {}).get("requisitos_condicoes_valores") or {}).get("itens") or []
    por_nome = {i["item"]: i for i in itens}
    saida = []
    for c in CAMADAS:
        i = por_nome.get(c)
        if i:
            saida.append({"camada": c, "ok": bool(i["comprovado"]), "valor": (i.get("valor") or "")[:120]})
        elif c == "Órgão / financiador":
            saida.append({"camada": c, "ok": True, "valor": fonte.get("orgao")})
        elif c == "Território":
            saida.append({"camada": c, "ok": True, "valor": fonte.get("uf") or "Brasil"})
        elif c == "Esfera":
            saida.append({"camada": c, "ok": fonte.get("nivel") in ("federal", "estadual", "municipal"), "valor": fonte.get("nivel")})
        elif c == "Área de atuação":
            a = area_da_fonte(fonte, familia(fonte.get("programa", "")))
            saida.append({"camada": c, "ok": a != "outros", "valor": a})
        else:
            saida.append({"camada": c, "ok": False, "valor": None})
    return saida


def diagnostico(fonte: dict, camadas: list[dict], sensor: dict | None, bloqueio: dict | None) -> dict:
    faltam = [c["camada"] for c in camadas if not c["ok"]]
    if not faltam:
        return {"estado": "completo", "faltam": [], "causa": None, "acao": "motor pode parar"}
    if not fonte.get("sites"):
        causa, acao = "sem página de publicação conhecida", "localizar por IA (degrau 4) ou LAI"
    elif bloqueio:
        causa = f'página bloqueada ({", ".join(bloqueio.get("erros", {}))}) em {bloqueio.get("bloqueios")} tentativa(s)'
        acao = "descer a escada: espelho institucional → Wayback → agregador → IA"
    elif not sensor:
        causa, acao = "motor ainda não saiu com rede", "aguarda a primeira saída no GitHub Actions"
    elif sensor.get("achados_total", 0) == 0:
        causa = "página respondeu mas sem edital reconhecido pelo léxico"
        acao = ("trocar URL para a listagem de editais" if sensor.get("vazias_seguidas", 0) >= 3
                else "continuar leitura diária; conferir se a URL é listagem")
    else:
        causa = "edital encontrado, mas o texto integral ainda não foi extraído"
        acao = "campanha de completude / extração do ato"
    return {"estado": "incompleto", "faltam": faltam, "causa": causa, "acao": acao,
            "obtidas": len(camadas) - len(faltam), "total": len(camadas)}


_AREA_FAM = {"PNAB / Aldir Blanc": "cultura", "Lei Rouanet": "cultura", "Lei Goyazes": "cultura",
             "Lei de Incentivo ao Esporte": "esporte", "Fundo da Criança (FMDCA/FIA)": "crianca_adolescente",
             "Assistência social (FMAS/FEAS)": "assistencia_social", "Fundo do Idoso": "pessoa_idosa",
             "PRONON / PRONAS": "saude", "Receita Federal (doação)": "doacao_bens"}
# palavras do programa/órgão que decidem a área quando a família não decide
_AREA_TXT = (("apreendid|receita federal", "doacao_bens"),
             ("aliment|fome|nutri|merenda|cesta", "seguranca_alimentar"),
             ("ambient|clim|reciclag|resíduo|residuo|nascente|horta|compostagem|circular|amaz|catador", "meio_ambiente"),
             ("assist|suas|feas|fmas|acolhimento|vulnerab", "assistencia_social"),
             ("crian|adolesc|fmdca|cmdca|conanda", "crianca_adolescente"),
             ("cultur|artes|audiovisual|patrim[oô]nio|m[uú]sica|teatro|danç|circo|leitura", "cultura"),
             ("direitos humanos|mulher|lgbt|racial|ind[ií]gena|quilomb|cidadania|difus", "direitos_humanos"),
             ("educa|escola|alfabetiza|bolsas", "educacao"),
             ("esport|atleta|paradesport|lazer", "esporte"),
             ("infraestrutura|obra|reforma|constru|mobilidade|saneamento", "infraestrutura"),
             ("idos", "pessoa_idosa"),
             ("sa[uú]de|pronon|pronas|defici|oncol|prevenç", "saude"))


def area_da_fonte(f: dict, fam: str) -> str:
    """Área de atuação nas 13 áreas canônicas da tela inicial — decidida pela
    família e, quando ela não decide, pelo texto do programa e do órgão."""
    if fam in _AREA_FAM:
        return _AREA_FAM[fam]
    # 1º a área do catálogo de origem (quando é clara), 2º o texto do programa/órgão
    cat = (f.get("area") or "").lower()
    for rx, area in (("ambient", "meio_ambiente"), ("cultur", "cultura"), ("esport", "esporte"),
                     ("educa", "educacao"), ("sa[uú]de", "saude"), ("assist|aliment", "assistencia_social"),
                     ("crian|adolesc", "crianca_adolescente"), ("idos", "pessoa_idosa")):
        if re.search(rx, cat):
            # refina dentro da área do catálogo pelo texto do programa
            prog = (f.get("programa") or "").lower()
            if area == "assistencia_social" and re.search(r"aliment|fome|nutri|merenda|cesta", prog):
                return "seguranca_alimentar"
            if area == "meio_ambiente" and re.search(r"direitos humanos|mulher|lgbt|racial|ind[ií]gena|quilomb", prog):
                return "direitos_humanos"
            return area
    alvo = f'{f.get("programa","")} {f.get("orgao","")}'.lower()
    for rx, area in _AREA_TXT:
        if re.search(rx, alvo):
            return area
    return "outros"


def _mencoes_recentes(dias: int = 60) -> list[dict]:
    """Oportunidades captadas pelos motores regulares (diários, plataformas, API)
    nos últimos dias — é a MENÇÃO que ativa uma fonte específica."""
    from datetime import date as _d, timedelta as _td
    try:
        from .nucleo import carregar_oportunidades
        ops = carregar_oportunidades().values()
    except Exception:
        return []
    corte = (_d.today() - _td(days=dias)).isoformat()
    # só o que os MOTORES REGULARES (diários, justiça, legislativo, plataformas)
    # captaram de fato; o acervo histórico do PNCP/Querido Diário não é menção
    return [o for o in ops if (o.get("coletado_em") or "")[:10] >= corte
            and str(o.get("tipo_fonte", "")).startswith(("sensor_", "investigacao_"))
            and (o.get("destinacao") or {}).get("elegivel") is not False]


_GENERICOS = {"secretaria", "municipal", "estadual", "federal", "governo", "estado", "goiás", "goiania",
              "goiânia", "programa", "fundo", "edital", "editais", "projeto", "projetos", "apoio", "recursos",
              "captação", "captacao", "entidade", "entidades", "social", "sociais", "cultura", "cultural",
              "culturais", "esporte", "esportivo", "esportivos", "educação", "educacao", "educativo", "saúde",
              "saude", "ambiente", "ambiental", "pessoa", "pessoas", "física", "fisica", "jurídica", "juridica",
              "destinação", "destinacao", "chamamento", "público", "publico", "pública", "publica", "termo",
              "fomento", "convênio", "convenio", "parceria", "emenda", "emendas", "doação", "doacao",
              "incentivo", "nacional", "brasil", "assistência", "assistencia", "crianças", "criancas",
              "adolescentes", "idosos", "comunitária", "comunitario", "comunitário"}


def _toks(txt: str) -> set:
    return {t for t in re.findall(r"[a-zà-ú]{5,}", (txt or "").lower()) if t not in _GENERICOS}


def status_da_fonte(f: dict, fam: str, mencoes: list[dict], prazo: dict, hoje) -> dict:
    """ATIVA só quando: há menção a este edital nos locais oficiais/plataformas,
    OU é a época prevista pelo histórico/regramento. Fora disso, INATIVA (oculta)."""
    toks = _toks(f["programa"]) | _toks(f.get("orgao") or "")
    toks_chave = _toks(f["programa"])
    # menção exige TODOS os termos distintivos do programa (até 3); programa sem
    # termo distintivo só ativa por época — nunca por casamento genérico
    chave = sorted(toks_chave, key=len, reverse=True)[:3]
    mencionada = [m for m in mencoes
                  if chave and all(t in (m.get("titulo", "") + " " + (m.get("evidencia") or "")).lower() for t in chave)]
    regime = (prazo or {}).get("regime_de_prazo") or ""
    pd = (prazo or {}).get("proxima_data") or {}
    mes = hoje.isoformat()[:7]
    em_epoca = False; base_epoca = None
    if regime.startswith("permanente"):
        em_epoca, base_epoca = True, "fonte permanente: captação o ano inteiro"
    elif pd.get("inicio") and pd.get("fim") and pd["inicio"][:7] <= mes <= pd["fim"][:7]:
        em_epoca, base_epoca = True, f'época prevista: {pd["inicio"]} a {pd["fim"]}'
    elif pd.get("mes") and pd["mes"] == mes:
        em_epoca, base_epoca = True, f'mês previsto pelo histórico: {pd["mes"]}'
    ativa = bool(mencionada) or em_epoca
    return {"ativa": ativa,
            "motivo": (f'mencionada em {len(mencionada)} publicação(ões) recente(s)' if mencionada
                       else base_epoca if em_epoca
                       else "sem menção nos locais oficiais e fora da época prevista"),
            "mencoes": [{"titulo": (m.get("titulo") or "")[:110], "url": m.get("url"),
                         "fonte": m.get("fonte_nome"), "em": (m.get("coletado_em") or "")[:10]} for m in mencionada[:3]],
            "em_epoca": em_epoca, "proxima": pd or None}


def _trinta_dias(reg: dict, hoje) -> list[dict]:
    """Calendário do motor: do 1º dia do mês anterior até o fim do mês corrente
    (o painel recorta o mês que o titular escolher). Cada dia: cor e trecho."""
    from datetime import timedelta as _td
    import calendar as _cal
    ini = (hoje.replace(day=1) - _td(days=1)).replace(day=1)
    fim = hoje.replace(day=_cal.monthrange(hoje.year, hoje.month)[1])
    saida = []
    d0 = ini
    while d0 <= fim:
        d = d0.isoformat(); d0 += _td(days=1)
        r = reg.get(d)
        saida.append({"d": d, "cor": (r or {}).get("cor", "cinza" if d <= hoje.isoformat() else "futuro"),
                      "n": (r or {}).get("achados", 0),
                      "t": (r or {}).get("trecho"), "u": (r or {}).get("url"), "http": (r or {}).get("http")})
    return saida


def _novas_sem_referencia(mencoes: list[dict], fontes: list[dict]) -> list[dict]:
    """Oportunidade anunciada nos locais oficiais que NÃO casa com nenhuma das
    260: ganha caixa própria (nova oportunidade histórica)."""
    toks_f = [(_toks(f["programa"]) | _toks(f.get("orgao") or "")) for f in fontes]
    novas = []
    for m in mencoes:
        tm = _toks(m.get("titulo", "") + " " + (m.get("evidencia") or "")[:300])
        if not tm:
            continue
        casa = any(len(tm & tf) >= 2 for tf in toks_f if tf)
        if not casa:
            novas.append(m)
    return novas[:60]


def run() -> dict:
    from datetime import date as _date
    hoje = _date.today()
    fontes = load_json(ROOT / "config/fontes_captacao_260.json").get("fontes", [])
    mencoes = _mencoes_recentes()
    diario = load_json(ROOT / "estado/esquadra_diario.json").get("sensores", {}) if (ROOT / "estado/esquadra_diario.json").exists() else {}
    esq = load_json(ROOT / "estado/esquadra.json").get("sensores", {}) if (ROOT / "estado/esquadra.json").exists() else {}
    blq = load_json(ROOT / "estado/bloqueios.json").get("dominios", {}) if (ROOT / "estado/bloqueios.json").exists() else {}
    prazos = {p["programa"]: p for p in load_json(ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json").get("lista", [])} \
        if (ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json").exists() else {}
    try:
        from .banco import conectar
        con = conectar()
    except Exception:
        con = None
    from urllib.parse import urlsplit
    # qual motor (sensor) atende cada fonte — vários pontos compartilham o mesmo site
    motor_da_fonte = {}
    try:
        from .sensores import registro
        for s in registro():
            for fid in s.get("fontes_260") or []:
                motor_da_fonte[fid] = s["id"]
    except Exception:
        pass
    motores = []
    for f in fontes:
        edital = _edital_manual_da_fonte(f["id"]) or (_ultimo_edital_da_fonte(f, con) if con else None)
        cam = camadas_da_fonte(f, edital)
        sid = motor_da_fonte.get(f["id"], f"f260-{f['id']}")
        s = esq.get(sid)
        dom = urlsplit(f["sites"][0]).hostname if f.get("sites") else None
        b = blq.get(dom) if dom else None
        pz = prazos.get(f["programa"], {})
        validacao = ("bloqueada" if b else "não lida ainda" if not s else
                     "lida, edital encontrado" if s.get("achados_total") else "lida, sem edital reconhecido")
        fam = familia(f["programa"])
        if fam == "Emendas parlamentares":
            continue                                   # emendas têm calendário próprio; não entram aqui
        st = status_da_fonte(f, fam, mencoes, pz, hoje)
        motores.append({
            "id": f["id"], "programa": f["programa"], "orgao": f.get("orgao"), "motor": sid,
            "familia": fam, "segmento": segmento(f), "area_atuacao": area_da_fonte(f, fam),
            "natureza": "privada" if f["nivel"] in ("privada", "internacional") else "publica",
            "esfera": ({"federal": "Brasil", "estadual": "Estado", "municipal": "Município",
                        "internacional": "Internacional"}.get(f["nivel"])
                       or ("Estado" if f.get("uf") else "Brasil")),     # privada nacional → Brasil
            "ativa": st["ativa"], "motivo_status": st["motivo"], "mencoes": st["mencoes"], "em_epoca": st["em_epoca"],
            "tipo": f["tipo"], "nivel": f["nivel"], "uf": f.get("uf") or ("BR" if f["nivel"] == "federal" else None),
            "goias": bool(f.get("goias")),
            "pagina": f["sites"][0] if f.get("sites") else None,
            "paginas": f.get("sites", [])[:3], "confianca_pagina": f.get("confianca_site"),
            "validacao": validacao,
            "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
            "http": ((s or {}).get("saude") or [{}])[0].get("http") if s else None,
            "regime_prazo": pz.get("regime_de_prazo"), "certeza_prazo": pz.get("certeza"),
            "proxima_data": pz.get("proxima_data"),
            "ultimo_edital": ({"titulo": (edital.get("titulo") or "")[:100], "url": edital.get("url"),
                               "publicado": edital.get("data_publicacao")} if edital else None),
            "camadas": cam, "obtidas": sum(1 for c in cam if c["ok"]),
            "diagnostico": diagnostico(f, cam, s, b),
        })
    if con:
        con.close()
    # ativação automática: o que está ativo hoje vai para os sensores
    ativas = {m["id"]: m["motivo_status"] for m in motores if m["ativa"]}
    write_json(ROOT / "estado/ativacao_fontes.json", {"data": hoje.isoformat(), "ativas": ativas,
               "regra": "fonte específica só sai na época prevista ou após menção em local oficial/plataforma; "
                        "os motores regulares (diários, justiça, legislativo, API, plataformas) saem todo dia"})
    novas = _novas_sem_referencia(mencoes, fontes)
    # plataformas indicadas pelo titular (Prosas etc.): rodando de forma satisfatória?
    plataformas = []
    inv = load_json(ROOT / "config/investigacao.json").get("fontes", []) if (ROOT / "config/investigacao.json").exists() else []
    for p in inv:
        s = esq.get(f"plat-{p['id']}")
        b = blq.get(urlsplit(p["url"]).hostname)
        plataformas.append({"id": p["id"], "nome": p["nome"], "url": p["url"],
                            "dias": _trinta_dias(diario.get(f"plat-{p['id']}", {}), hoje),
                            "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
                            "leituras": (s or {}).get("leituras", 0),
                            "situacao": ("bloqueada" if b else "sem leitura ainda" if not s else
                                         "satisfatória — obtendo editais" if s.get("achados_total") else
                                         "lendo, sem editais reconhecidos")})
    # diários e locais oficiais
    esp = load_json(ROOT / "config/sensores.json").get("sensores_especiais", [])
    oficiais = []
    for e in esp:
        s = esq.get(e["id"]); b = blq.get(urlsplit(e["urls"][0]).hostname)
        oficiais.append({"id": e["id"], "nome": e["nome"], "tipo": e["tipo"], "url": e["urls"][0],
                         "dias": _trinta_dias(diario.get(e["id"], {}), hoje),
                         "ultima_leitura": (s or {}).get("ultima"), "achados": (s or {}).get("achados_total", 0),
                         "situacao": ("bloqueado" if b else "sem leitura ainda" if not s else
                                      "ativo — captando" if s.get("achados_total") else "ativo, sem achados")})
    motores.sort(key=lambda m: (not m["goias"], m["familia"], m["segmento"], m["programa"]))
    resumo = {
        "gerado_em": now_iso(), "total": len(motores),
        "por_familia": dict(Counter(m["familia"] for m in motores).most_common()),
        "por_segmento": dict(Counter(m["segmento"] for m in motores)),
        "completos": sum(1 for m in motores if m["diagnostico"]["estado"] == "completo"),
        "media_camadas": round(sum(m["obtidas"] for m in motores) / len(motores), 2) if motores else 0,
        "plataformas": plataformas, "oficiais": oficiais,
        "ativas": len(ativas), "inativas": len(motores) - len(ativas),
        "novas_sem_referencia": [{"titulo": (m.get("titulo") or "")[:120], "url": m.get("url"),
                                  "fonte": m.get("fonte_nome"), "em": (m.get("coletado_em") or "")[:10],
                                  "prazo": m.get("prazo_texto"), "valor": m.get("valor_texto"),
                                  "uf": m.get("uf"), "nivel": m.get("nivel")} for m in novas],
        "camadas": list(CAMADAS),
    }
    write_json(ROOT / "biblioteca_alexandria/fontes/motores.json", {**resumo, "motores": motores})
    from .compacto import compactar
    pasta = ROOT / "docs/dados"; pasta.mkdir(parents=True, exist_ok=True)
    from .opressores import proximidade as _prox, _estado as _est_op
    lig = _est_op().get("ligados", {})
    for m in motores:
        m["proximidade"] = "ligado" if m["id"] in lig else _prox(m, hoje)
        r = lig.get(m["id"])
        m["disjuntor"] = ({"dias": r.get("dias"), "ate": r.get("ate"), "origem": r.get("origem"),
                           "ia": len(r.get("ia", [])), "conselho": bool(r.get("conselho")),
                           "proxima_ia_em": (3 - (r.get("dias") or 0) % 3) % 3 or 3,
                           "itens_ia": len(r.get("itens", {}))} if r else None)
    leve = [{k: m[k] for k in ("id", "programa", "orgao", "familia", "segmento", "tipo", "nivel", "uf", "goias",
                              "pagina", "confianca_pagina", "validacao", "ultima_leitura", "achados", "http",
                              "regime_prazo", "certeza_prazo", "obtidas", "area_atuacao", "natureza", "esfera",
                              "ativa", "motivo_status", "em_epoca", "proximidade")}
            | {"disjuntor": json.dumps(m["disjuntor"], ensure_ascii=False) if m.get("disjuntor") else None}
            | {"camadas_ok": "".join("1" if c["ok"] else "0" for c in m["camadas"]),
               "camadas_val": "|".join((c["valor"] or "").replace("|", "/")[:90] for c in m["camadas"]),
               "mencoes": " · ".join(x["titulo"][:70] for x in m["mencoes"]) or None,
               "faltam": "|".join(m["diagnostico"]["faltam"]),
               "causa": m["diagnostico"]["causa"], "acao": m["diagnostico"]["acao"],
               "ultimo_titulo": (m["ultimo_edital"] or {}).get("titulo"),
               "ultimo_url": (m["ultimo_edital"] or {}).get("url"),
               "proxima": json.dumps(m["proxima_data"], ensure_ascii=False) if m["proxima_data"] else None}
            for m in motores]
    pac = compactar(leve)
    pac["resumo"] = {k: v for k, v in resumo.items() if k not in ("plataformas", "oficiais", "novas_sem_referencia")}
    pac["plataformas"] = plataformas; pac["oficiais"] = oficiais; pac["novas"] = resumo["novas_sem_referencia"]
    hz = ROOT / "config/horarios.json"
    pac["horarios"] = load_json(hz) if hz.exists() else {}
    ri = ROOT / "estado/relatorios/indice.json"
    pac["relatorios"] = load_json(ri) if ri.exists() else {"dias": []}
    hoje_rel = ROOT / "estado/relatorios" / f"{hoje.isoformat()}.json"
    pac["relatorio_hoje"] = load_json(hoje_rel) if hoje_rel.exists() else None
    (pasta / "motores.json").write_text(json.dumps(pac, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {k: v for k, v in resumo.items() if k not in ("plataformas", "oficiais", "camadas")}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
