"""Dados consolidados do dashboard — v2, estrutura Eldorado / Farol.

Alimentado às SEGUNDAS e SEXTAS pela varredura, e mensalmente pela revisão de
leis e pelo compilado histórico. Produz tudo que o painel precisa:

- **Calendário**: eventos por dia (abertura, encerramento, resultado
  preliminar/final, prorrogação, retificação, recurso), cada edital com a cor
  da sua ÁREA (cultura, esporte, educação…). Prorrogação atualiza a data
  exibida e mantém a original visível.
- **Editais abertos**: resumo por caixa + detalhes (protocolo, requisitos,
  pontuação, documentos) — o que a fonte não disse aparece como pendência.
- **Bússola**: um quadro por dia do mês com o registro de auditoria — se houve
  busca, quais camadas rodaram, quantas fontes responderam — e as fontes com
  edital aberto, cada uma com seus links e anexos conhecidos.
- **Farol**: biblioteca de normas (26) e espaços de Documentos (posteriormente).

Quando o segredo de acesso está configurado, o publicador cifra este conteúdo
(AES-256-GCM) e nada legível vai ao ar. Sem IA e sem tokens.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
import os
from datetime import date, datetime, timedelta

from . import parlamentares as mod_parlamentares
from .programas import caracterizar
from .relatorio_busca import _situacao
from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

# ---------------- áreas e cores (tons claros) ----------------
# Paleta do demonstrativo (azul, laranja, verde, roxo, azul claro) ampliada para
# 13 matizes distintos entre si, de modo que o filtro de Área e as barras do
# calendário distingam cada área sem ambiguidade de cor.
AREAS = {
    "saude":              {"rotulo": "Saúde",                "cor": "#2F7FE0"},
    "infraestrutura":     {"rotulo": "Infraestrutura",       "cor": "#F08C1E"},
    "educacao":           {"rotulo": "Educação",             "cor": "#3FA34D"},
    "meio_ambiente":      {"rotulo": "Meio ambiente",        "cor": "#7B4BE0"},
    "assistencia_social": {"rotulo": "Assistência social",   "cor": "#17B8CF"},
    "cultura":            {"rotulo": "Cultura",              "cor": "#D6336C"},
    "esporte":            {"rotulo": "Esporte",              "cor": "#8FBF26"},
    "crianca_adolescente":{"rotulo": "Criança e adolescente","cor": "#F2B705"},
    "pessoa_idosa":       {"rotulo": "Pessoa idosa",         "cor": "#A9611F"},
    "direitos_humanos":   {"rotulo": "Direitos humanos",     "cor": "#E8503A"},
    "justica":            {"rotulo": "Justiça e Ministério Público", "cor": "#4A5568"},
    "direitos_difusos":   {"rotulo": "Direitos difusos e cidadania", "cor": "#6B5B95"},
    "seguranca_alimentar":{"rotulo": "Segurança alimentar",  "cor": "#0E8A74"},
    "outros":             {"rotulo": "Outros",               "cor": "#94A3B8"},
    "emendas_parlamentares": {"rotulo": "Emendas parlamentares", "cor": "#B8860B"},
    "doacao_bens":          {"rotulo": "Doação de bens (Receita Federal)", "cor": "#5C7A3F"},
}
# previsão (não é área): cinza claro, só nos meses futuros
COR_PREVISAO = "#D5D9DE"
_PALAVRAS_AREA = [
    ("infraestrutura", r"infraestrutur|pavimenta|ilumina[çc][ãa]o p[úu]blica|obra|saneament|mobilidade urbana|drenagem"),
    ("cultura", r"cultur|audiovisual|artist|patrim[oô]nio|m[uú]sic|teatro|danca|dança|pnab|aldir|paulo gustavo|rouanet|goyazes"),
    ("esporte", r"esport|atleta|desport|paradesporto|lei pel[eé]|lie\b"),
    ("educacao", r"educa|escolar|alfabetiz|creche|contraturno"),
    ("crianca_adolescente", r"crian[çc]a|adolescente|cmdca|fmdca|conanda|eca\b"),
    ("pessoa_idosa", r"idos[oa]|pessoa idosa|cmi\b|cndi"),
    ("assistencia_social", r"assist[eê]ncia social|socioassistencial|suas\b|cmas|loas|vulnerabilidade"),
    ("saude", r"sa[uú]de|sus\b|pronon|pronas|hospital"),
    ("meio_ambiente", r"ambient|sustentab|res[íi]duo|reciclag"),
    ("direitos_humanos", r"direitos humanos|mulher|igualdade|viol[eê]ncia"),
    ("justica", r"pecuni[áa]ria|tribunal|tjgo|cnj|minist[eé]rio p[uú]blico|tac\b"),
    ("seguranca_alimentar", r"seguran[çc]a alimentar|aliment|fome"),
]
_FONTES_CACHE = None
def _fontes() -> dict:
    global _FONTES_CACHE
    if _FONTES_CACHE is None:
        _FONTES_CACHE = {f["id"]: f for f in load_json(ROOT / "config/fontes.json")["fontes"]}
    return _FONTES_CACHE

def _n(t): return unicodedata.normalize("NFKD", t or "").encode("ascii","ignore").decode().lower()

def area_do_edital(item: dict) -> str:
    texto = _n(" ".join(str(item.get(c) or "") for c in ("titulo", "evidencia", "consulta_origem")))
    for area, padrao in _PALAVRAS_AREA:
        if re.search(padrao, texto):
            return area
    fonte = _fontes().get(item.get("fonte_id")) or {}
    for a in fonte.get("areas") or []:
        if a in AREAS:
            return a
    return "outros"

def _br(iso):
    if not iso: return None
    try: return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError: return iso

def _iso_de_br(br):
    if not br: return None
    m = re.search(r"(\d{1,2})/(\d{1,2})/(20\d{2})", str(br))
    if not m: return None
    d, mo, a = map(int, m.groups())
    try: return date(a, mo, d).isoformat()
    except ValueError: return None

# ---------------- editais com detalhes ----------------
_VALOR = re.compile(r"R\$\s?([\d\.]{1,12}(?:,\d{2})?)(\s?(?:mil|milh[õo]es|milh[ãa]o))?", re.I)

def valor_citado(texto: str) -> str | None:
    m = _VALOR.search(texto or "")
    return ("R$ " + m.group(1) + (m.group(2) or "")).strip() if m else None

UFS = ("AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB",
       "PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO")

def uf_do_territorio(item: dict) -> str | None:
    """UF do edital, derivada do território ('GO', 'GO/Goiânia') ou da fonte.

    O campo nunca era preenchido e o filtro de estado comparava contra `null`:
    nenhuma linha casava. Território nacional ('BR') não vira UF — fica `None` e
    é tratado como 'alcança todos os estados' pelo filtro do painel.
    """
    territorio = str(item.get("territorio") or "").strip().upper()
    if territorio in UFS:
        return territorio
    if "/" in territorio:                       # 'GO/Goiânia'
        sigla = territorio.split("/")[0].strip()
        if sigla in UFS:
            return sigla
    fonte = _fontes().get(item.get("fonte_id")) or {}
    da_fonte = str(fonte.get("territorio") or "").split("/")[0].strip().upper()
    return da_fonte if da_fonte in UFS else None

# vocabulário que caracteriza um edital de verdade (e não notícia ou página de portal)
_EH_EDITAL = re.compile(
    r"edital|chamada\s+p[úu]blica|chamamento|sele[çc][ãa]o\s+p[úu]blica|concurso|"
    r"pr[êe]mio|inscri[çc][õo]es|fomento|apoio\s+a\s+projetos|credenciamento|"
    r"chamada\s+de\s+propostas|edital\s+de", re.I)

# programas cujo alcance é o país inteiro (valem para qualquer estado)
PROGRAMAS_NACIONAIS = {
    "rouanet", "pnab-aldir-blanc", "paulo-gustavo", "lie-esporte", "mrosc",
    "fundo-crianca", "fundo-idoso", "suas", "fdd", "pronon", "pronas",
}

def alcance_nacional(item: dict, carac: dict | None = None) -> bool:
    """Nacional = aplica-se a QUALQUER estado (ex.: Rouanet, um por modalidade).

    Não basta a fonte ser federal: portais nacionais também publicam notícias e
    páginas de navegação. Exige-se, cumulativamente, que (1) não haja UF; (2) o
    item seja de nível federal ou de um programa de alcance nacional; e (3) o
    texto tenha vocabulário de edital. O que não passa fica como alcance
    'indefinido' e não é contado como nacional — aparece apenas em 'Brasil'.
    """
    if uf_do_territorio(item):
        return False
    carac = carac or item.get("caracterizacao") or {}
    programa_nacional = str(carac.get("programa_id") or "") in PROGRAMAS_NACIONAIS
    if not (programa_nacional or item.get("nivel") == "federal"):
        return False
    texto = " ".join(str(item.get(c) or "") for c in ("titulo", "evidencia"))
    return bool(_EH_EDITAL.search(texto))

def abrangencia(item: dict, carac: dict | None = None) -> str:
    if uf_do_territorio(item):
        return "estadual"
    return "nacional" if alcance_nacional(item, carac) else "indefinida"

def painel_bussola(editais: list[dict], bussola: dict, hoje: date) -> dict:
    """Números reais dos cartões da página Bússola (nada demonstrativo).

    - novas na última varredura e verificados na semana vêm de coletado_em;
    - fontes ativas vêm do catálogo de fontes; sites do catálogo de rotas;
    - casos no Farol: contagem real de casos abertos (0 até a 1ª execução);
    - atualizações: últimos acontecimentos reais (coleta, verificação, prazo).
    """
    import json as _json
    iso_hoje = hoje.isoformat()
    def col(e): return str((e.get("detalhes") or {}).get("coletado_em") or "")[:10]
    datas = sorted({col(e) for e in editais if col(e)}, reverse=True)
    ultima = datas[0] if datas else None
    novas = sum(1 for e in editais if col(e) == ultima) if ultima else 0
    semana = [ (hoje - __import__("datetime").timedelta(days=i)).isoformat() for i in range(7) ]
    verif_semana = sum(1 for e in editais
                       if str(e.get("status","")).startswith("verificada") and col(e) in semana)
    fontes_cfg = _fontes()
    ativas = sum(1 for f in fontes_cfg.values() if f.get("ativa"))
    try:
        rotas = _json.loads((ROOT/"estado/cobertura_catalogo.json").read_text(encoding="utf-8"))
        sites = int(rotas.get("total") or rotas.get("pontos_total") or 0) or len(fontes_cfg)
    except Exception:
        sites = len(fontes_cfg)
    casos_dir = ROOT/"dados/associacoes/amc-jardim-america/casos"
    casos = len(list(casos_dir.glob("*/"))) if casos_dir.exists() else 0
    urgentes = [e for e in editais
                if e.get("estado_export") in ("aberto","a_abrir")
                and e.get("fim") and 0 <= ( __import__("datetime").date.fromisoformat(e["fim"]) - hoje ).days <= 7]
    verificados = sum(1 for e in editais if str(e.get("status","")).startswith("verificada")
                      or e.get("status")=="elegivel")

    # linha do tempo: últimos acontecimentos reais
    eventos=[]
    for e in editais:
        if col(e):
            eventos.append({"data": col(e), "tipo": "novo",
                "titulo": "Novo edital captado",
                "sub": f'{e.get("fonte_nome","")} · {e.get("valor_texto") or "valor não publicado"}',
                "id": e.get("id")})
        if str(e.get("status","")).startswith("verificada"):
            eventos.append({"data": col(e) or iso_hoje, "tipo": "verificada",
                "titulo": "Oportunidade verificada",
                "sub": e.get("fonte_nome",""), "id": e.get("id")})
    for e in urgentes:
        eventos.append({"data": e["fim"], "tipo": "prazo",
            "titulo": "Prazo se aproximando",
            "sub": f'{e.get("fonte_nome","")} · encerra {e["fim"][8:10]}/{e["fim"][5:7]}',
            "id": e.get("id")})
    eventos.sort(key=lambda x: x["data"], reverse=True)
    return {"novas_ultima": novas, "fontes_ativas": ativas, "sites": sites,
            "verificados": verificados, "verificados_semana": verif_semana,
            "urgentes_7d": len(urgentes), "casos_farol": casos,
            "casos_nota": "aguardando primeira execução do Farol" if casos==0 else "em análise",
            "atualizacoes": eventos[:8]}


def _editais(hoje: date) -> list[dict]:
    cfg_prog = load_json(ROOT / "config/programas.json")
    saida = []
    for item in carregar_oportunidades().values():
        if item.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        carac = item.get("caracterizacao") or caracterizar(item, cfg_prog)
        periodo = carac.get("periodo") or {}
        # INÍCIO só quando a fonte declarou a abertura das inscrições.
        # Sem declaração, a data que existe é a de PUBLICAÇÃO — vai para
        # publicado_em e nunca vira início de inscrição (era isso que fazia
        # o calendário mostrar "abriu mês passado, vigência indeterminada").
        ini_decl = bool(periodo.get("inicio_declarado"))
        inicio_iso = periodo.get("inicio") if ini_decl else None
        publicado_em = None if ini_decl else periodo.get("inicio")
        fim_iso = _iso_de_br(item.get("prazo_texto")) or periodo.get("fim")
        fim_decl = bool(item.get("prazo_texto") or periodo.get("fim_declarado") or periodo.get("fim"))
        lacuna_datas = None
        if inicio_iso and fim_iso and fim_iso < inicio_iso:
            # datas incoerentes na fonte: preserva o PRAZO (o dado decisivo)
            # e descarta o início, registrando a divergência
            lacuna_datas = (f"datas divergentes na fonte (início {inicio_iso} "
                            f"posterior ao fim {fim_iso}); início desconsiderado")
            inicio_iso = None
        confirmacao = ("ambas" if inicio_iso and fim_iso
                       else "so_fim" if fim_iso
                       else "so_publicacao" if publicado_em
                       else "nenhuma")
        situ = _situacao(inicio_iso, fim_iso, hoje)
        q = item.get("qualidade") or {}
        req = item.get("requisitos") or {}
        fonte = _fontes().get(item.get("fonte_id")) or {}
        saida.append({
            "id": item["id"], "protocolo": item["id"],
            "titulo": item.get("titulo"), "url": item.get("url"),
            "fonte_id": item.get("fonte_id"), "fonte_nome": item.get("fonte_nome"),
            "territorio": item.get("territorio"), "nivel": item.get("nivel"),
            "uf": uf_do_territorio(item), "abrangencia": abrangencia(item, carac),
            "status": item.get("status"), "confianca": item.get("confianca"),
            "area": area_do_edital(item), "programa": carac.get("programa"),
            "lei": carac.get("lei"), "objeto": carac.get("modalidade"),
            "inicio": inicio_iso, "fim": fim_iso,
            "inicio_br": _br(inicio_iso), "fim_br": _br(fim_iso),
            "publicado_em": publicado_em, "datas": confirmacao,
            "prazo_prorrogado": bool(item.get("prazo_prorrogado")),
            "prazo_original": item.get("prazo_original"),
            "estado_export": situ["estado"],
            "resumo": (item.get("evidencia") or "")[:220],
            "valor_texto": valor_citado(item.get("evidencia")),
            "detalhes": {
                "qualificacao": {"nota": q.get("nota"), "classe": q.get("classe")},
                "requisitos_estruturados": req or None,
                "pontuacao": (req or {}).get("criterios_pontuacao") or None,
                "documentos_exigidos": (req or {}).get("documentos") or None,
                "pendencias": [x["rotulo"] for x in (q.get("conteudo_pendente") or [])],
                "atendidos": [x["rotulo"] for x in (q.get("conteudo_atendido") or [])],
                "evidencia": (item.get("evidencia") or "")[:600],
                "hash_evidencia": item.get("hash_evidencia"),
                "coletado_em": item.get("coletado_em"),
                "lacuna": ("requisitos detalhados, pontuação e documentos ainda não extraídos do edital "
                           "— exigem leitura do documento primário (fase Farol)") if not req else None,
            },
            "marcos": item.get("marcos_resultado") or [],
            "anexos": item.get("anexos") or [],
            "ficha": f"editais/{item['id']}.html",
        })
    return saida

# ---------------- eventos do calendário ----------------
_TIPOS_EVT = {
    "abertura":            {"rotulo": "Abertura de inscrições", "simbolo": "▲"},
    "encerramento":        {"rotulo": "Encerramento",           "simbolo": "■"},
    "resultado_preliminar":{"rotulo": "Resultado preliminar",   "simbolo": "◐"},
    "resultado_final":     {"rotulo": "Resultado final",        "simbolo": "●"},
    "prorrogacao":         {"rotulo": "Prorrogação",            "simbolo": "⟳"},
    "retificacao":         {"rotulo": "Retificação",            "simbolo": "✎"},
    "recurso":             {"rotulo": "Fase de recurso",        "simbolo": "§"},
}
def _eventos(editais: list[dict]) -> list[dict]:
    eventos = []
    for e in editais:
        if e["inicio"]:
            eventos.append({"data": e["inicio"], "tipo": "abertura", "edital_id": e["id"],
                            "titulo": e["titulo"], "area": e["area"]})
        if e["fim"]:
            eventos.append({"data": e["fim"], "tipo": "encerramento", "edital_id": e["id"],
                            "titulo": e["titulo"], "area": e["area"],
                            "prorrogado": e["prazo_prorrogado"],
                            "data_original": _iso_de_br(e.get("prazo_original"))})
        for m in e["marcos"]:
            d = _iso_de_br(m.get("data"))
            if d and m.get("tipo") in _TIPOS_EVT:
                eventos.append({"data": d, "tipo": m["tipo"], "edital_id": e["id"],
                                "titulo": e["titulo"], "area": e["area"]})
    return sorted(eventos, key=lambda x: x["data"])

# ---------------- bússola: auditoria dia a dia ----------------
_CAMADA_FONTE = {  # tipo de fonte -> categoria visual da bússola
    "diario_oficial": "diario_oficial", "diario_oficial_municipal": "diario_oficial",
    "api_oficial": "api_oficial",
    "plataforma": "plataforma", "plataforma_radar": "plataforma",
    "rede_social_indireta": "rede_social", "rede_social_oficial": "rede_social",
    "busca_retroativa_dominio_catalogado": "busca",
}
CATEGORIAS_FONTE = {
    "diario_oficial": {"rotulo": "Diário oficial", "cor": "#1F5B99"},
    "site_oficial":   {"rotulo": "Site oficial",   "cor": "#1E7E4B"},
    "api_oficial":    {"rotulo": "API oficial (PNCP/QD)", "cor": "#7C4DBE"},
    "plataforma":     {"rotulo": "Plataforma agregadora", "cor": "#C2571B"},
    "rede_social":    {"rotulo": "Rede social (pista)",   "cor": "#C23B69"},
    "imprensa":       {"rotulo": "Imprensa (pista)",      "cor": "#8A6A16"},
    "busca":          {"rotulo": "Busca retroativa",      "cor": "#607086"},
}
def _categoria_fonte(tipo: str | None) -> str:
    return _CAMADA_FONTE.get(tipo or "", "site_oficial")

def _bussola(editais: list[dict]) -> dict:
    auditoria = ROOT / "estado/auditoria.jsonl"
    por_dia: dict[str, dict] = defaultdict(lambda: {"buscas": [], "fontes_ok": 0, "fontes_falha": 0, "novas": 0})
    if auditoria.exists():
        for linha in auditoria.read_text(encoding="utf-8").splitlines():
            if not linha.strip(): continue
            try: ev = json.loads(linha)
            except json.JSONDecodeError: continue
            quando = (ev.get("executado_em") or ev.get("em") or "")[:10]
            if not quando: continue
            d = por_dia[quando]
            d["buscas"].append(ev.get("evento", "execucao"))
            d["fontes_ok"] += int(ev.get("fontes_ok") or 0)
            d["fontes_falha"] += int(ev.get("fontes_falha") or 0)
            d["novas"] += int(ev.get("novas") or ev.get("pistas_novas") or 0)
    # Cada camada de busca corresponde a uma frente de coleta (ponto de cor).
    # A pesquisa deve atuar em TODAS as frentes; o dia mostra em quais houve
    # captação e se algo foi ENCONTRADO.
    CAMADA_CATEGORIA = {
        "coleta_diaria": "site_oficial", "verificacao_social": "rede_social",
        "coleta_api": "api_oficial", "rmg_diarios": "api_oficial",
        "capilaridade": "imprensa", "redes_indireta": "rede_social",
        "retrospectivo": "busca", "carga_historica": "busca",
        "catalogacao_historica": "busca", "plataformas": "plataforma",
        "coleta_plataforma": "plataforma", "ciclo_acesso": None,
    }
    dias = []
    for k, v in sorted(por_dia.items()):
        cats = sorted({c for b in v["buscas"]
                       if (c := CAMADA_CATEGORIA.get(b))})
        encontrou = v["novas"] > 0
        dias.append({
            "data": k, "houve_busca": True, "camadas": sorted(set(v["buscas"])),
            "categorias_ativas": cats,
            "fontes_ok": v["fontes_ok"], "fontes_falha": v["fontes_falha"],
            "novas": v["novas"],
            # ENCONTRADO = a varredura trouxe indícios de edital naquele dia
            "encontrado": encontrou,
            "situacao": "encontrado" if encontrou else "ausente",
            "integridade": ("integra" if v["fontes_falha"] == 0 else "com_falhas"),
            "validado": v["fontes_falha"] == 0,
        })
    # fontes com edital aberto: caixa própria com links e anexos
    # a caixa consolida por fonte; o filtro do painel decide o que exibir
    por_fonte: dict[str, dict] = {}
    for e in editais:
        f = _fontes().get(e["fonte_id"]) or {}
        cx = por_fonte.setdefault(e["fonte_id"], {
            "fonte_id": e["fonte_id"], "fonte_nome": e["fonte_nome"],
            "url_fonte": f.get("url"), "tipo": f.get("tipo"),
            "categoria": _categoria_fonte(f.get("tipo")),
            "editais": []})
        det = e.get("detalhes") or {}
        ciclo = e.get("ciclo") or {}
        insc = ciclo.get("inscricao") or {}
        # análise da ETAPA 2, item a item, para a caixa exibir por edital
        analise = [
            {"item": "Objeto", "valor": (e.get("objeto") or "")[:180] or None,
             "comprovado": bool(e.get("objeto"))},
            {"item": "Prazo de inscrição",
             "valor": (f'{insc.get("inicio") or "?"} a {insc.get("fim") or "?"}'
                       + (" (abertura projetada)" if insc.get("projetado") else ""))
                      if insc else None,
             "comprovado": bool(insc.get("fim"))},
            {"item": "Resultado",
             "valor": ((ciclo["resultado"]["data"]
                        + (" (projetado)" if ciclo["resultado"].get("projetado") else ""))
                       if ciclo.get("resultado") else None),
             "comprovado": bool(ciclo.get("resultado")
                                and not (ciclo["resultado"] or {}).get("projetado"))},
            {"item": "Prazo de recurso",
             "valor": ((f'{ciclo["recurso"]["inicio"]} a {ciclo["recurso"]["fim"]}'
                        + (" (projetado)" if ciclo["recurso"].get("projetado") else ""))
                       if ciclo.get("recurso") else None),
             "comprovado": bool(ciclo.get("recurso")
                                and not ciclo["recurso"].get("projetado"))},
            {"item": "Valor", "valor": e.get("valor_texto"),
             "comprovado": bool(e.get("valor_texto"))},
            {"item": "Órgão / financiador", "valor": e.get("fonte_nome"),
             "comprovado": bool(e.get("fonte_nome"))},
            {"item": "Território", "valor": e.get("territorio"),
             # alcance nacional é território definido, ainda que sem UF
             "comprovado": bool(e.get("uf")) or e.get("abrangencia") == "nacional"},
            {"item": "Esfera", "valor": e.get("nivel"),
             "comprovado": e.get("nivel") in ("federal", "estadual", "municipal")},
            {"item": "Requisitos", "valor": ", ".join(det.get("documentos_exigidos") or [])[:160] or None,
             "comprovado": bool(det.get("documentos_exigidos"))},
            {"item": "Anexos", "valor": (f'{len(e.get("anexos") or [])} anexo(s)'
                                         if e.get("anexos") else None),
             "comprovado": bool(e.get("anexos"))},
            {"item": "Destinação",
             "valor": (e.get("destinacao") or {}).get("motivo"),
             "comprovado": (e.get("destinacao") or {}).get("elegivel") is True},
        ]
        cx["editais"].append({"id": e["id"], "titulo": e["titulo"], "url": e["url"],
                              "uf": e.get("uf"), "area": e.get("area"),
                              "nivel": e.get("nivel"), "fim": e.get("fim"),
                              "estado_export": e.get("estado_export"),
                              "objeto": e.get("objeto"),
                              "valor_texto": e.get("valor_texto"),
                              "confirmacao": e.get("confirmacao"),
                              "analise_etapa2": analise,
                              "comprovados": sum(1 for a in analise if a["comprovado"]),
                              "total_itens": len(analise),
                              "pendencias": (det.get("pendencias") or [])[:6],
                              "anexos": e["anexos"],
                              "anexos_pendentes": not e["anexos"]})
    # frentes que a pesquisa deve percorrer, com a cobertura observada
    cobertura = {c: sum(1 for d in dias if c in d["categorias_ativas"]) for c in CATEGORIAS_FONTE}
    return {"dias": dias, "categorias": CATEGORIAS_FONTE,
            "frentes_cobertura": cobertura,
            "frentes_sem_cobertura": [c for c, n in cobertura.items() if n == 0],
            "fontes_com_editais": sorted(por_fonte.values(), key=lambda x: -len(x["editais"])),
            "regra": "monitor de integridade: cada dia registra se houve busca e o que validou; anexos ausentes são pendência declarada, não omissão silenciosa"}

def _assocs_publicas() -> list[dict]:
    from .biblioteca import ASSOCIACOES as _A
    i = _A / "indice.json"
    if not i.exists():
        return []
    return [{"slug": a["slug"], "nome": a["nome"]}
            for a in load_json(i).get("associacoes", [])]


def _farol_resumo(editais: list[dict]) -> dict:
    """Números da página inicial. Aderência média só existe após a primeira
    execução real do Farol (resultados/*/ranking.json); antes disso é null e o
    painel declara a pendência em vez de inventar percentual."""
    notas = []
    for ranking in (ROOT / "resultados").glob("*/ranking.json"):
        try:
            for opp in load_json(ranking).get("oportunidades", []):
                if opp.get("elegivel"):
                    notas.append(opp.get("pontuacao") or 0)
        except (ValueError, OSError):
            continue
    abertos = [e for e in editais if e["estado_export"] in {"aberto", "a_abrir", "sem_prazo"}]
    pendentes = sum(len(e["detalhes"].get("pendencias") or []) for e in abertos)
    contagem = {"elegiveis": 0, "acao_necessaria": 0, "verificadas": 0, "descartadas": 0, "capturadas": 0}
    for e in editais:
        s = e["status"] or ""
        if s == "elegivel": contagem["elegiveis"] += 1
        elif s in {"descartada", "inelegivel"}: contagem["descartadas"] += 1
        elif s.startswith("verificada"): contagem["verificadas"] += 1
        elif e["detalhes"].get("pendencias"): contagem["acao_necessaria"] += 1
        else: contagem["capturadas"] += 1
    return {
        "aderencia_media": round(sum(notas) / len(notas)) if notas else None,
        "aderencia_nota": None if notas else "aguarda a primeira execução do Farol (requer FAROL_AI_API_KEY)",
        "avaliacoes": len(notas),
        "requisitos_pendentes": pendentes,
        "decisoes": contagem,
        "credencial_ia": bool(os.environ.get("FAROL_AI_API_KEY")),
        "associacoes_publicas": _assocs_publicas(),
        "documentacao_pronta": [
            {"id": e["id"], "titulo": e["titulo"], "area": e["area"], "status": e["status"],
             "qualificacao": e["detalhes"]["qualificacao"]}
            for e in editais if str(e["status"]).startswith(("verificada", "elegivel"))][:6],
        "fila_enquadrados": _fila_enquadrados(editais),
    }


def _fila_enquadrados(editais: list[dict]) -> list[dict]:
    """Fila prioritária: projetos JÁ ENQUADRADOS numa associação, com o estado
    real da documentação para protocolo.

    Enquadrado = existe caso aberto para a associação (dados/associacoes/<slug>/
    casos/<id>/). O progresso vem dos arquivos do caso realmente presentes.
    Enquanto o Farol não roda, a fila fica vazia e o painel declara o motivo —
    não se inventa enquadramento.
    """
    base = ROOT / "dados/associacoes"
    porid = {e["id"]: e for e in editais}
    fila: list[dict] = []
    if not base.exists():
        return fila
    for assoc in sorted(base.glob("*/")):
        if assoc.name.upper() == "EXEMPLO":
            continue
        perfil = assoc / "perfil_publico.json"
        nome = assoc.name
        if perfil.exists():
            try:
                nome = load_json(perfil).get("nome") or nome
            except Exception:
                pass
        for caso in sorted((assoc / "casos").glob("*/")) if (assoc / "casos").exists() else []:
            edital = porid.get(caso.name)
            if edital is None:
                continue
            arquivos = {f.name for f in caso.glob("*") if f.is_file()}
            etapas = [
                ("enquadramento", any(a.startswith("01") for a in arquivos)),
                ("plano_de_trabalho", any(a.startswith("02") for a in arquivos)),
                ("orcamento", any(a.startswith("03") for a in arquivos)),
                ("documentos", any(a.startswith("04") for a in arquivos)),
                ("parecer", any(a.startswith(("06", "07")) for a in arquivos)),
            ]
            prontas = sum(1 for _, ok in etapas if ok)
            submissao = (caso / "submissao").exists()
            fila.append({
                "id": edital["id"], "associacao": nome,
                "titulo": edital["titulo"], "area": edital["area"],
                "fonte_nome": edital["fonte_nome"], "valor_texto": edital.get("valor_texto"),
                "fim": edital.get("fim"), "uf": edital.get("uf"),
                "etapas": dict(etapas), "etapas_prontas": prontas, "etapas_total": len(etapas),
                "protocolo_pronto": submissao,
                "situacao": ("pronta para protocolo" if submissao
                             else "documentação em preparo" if prontas
                             else "enquadrado, sem documentos"),
            })
    fila.sort(key=lambda c: (not c["protocolo_pronto"], -c["etapas_prontas"], c["fim"] or "9999"))
    return fila

def _recorte_painel(editais: list[dict], hoje: date) -> list[dict]:
    """O painel publica o recorte OPERACIONAL; o acervo completo (13 mil+
    pistas históricas) permanece no JSONL e no banco SQLite. Critério:
    inscrições abertas ou por abrir; qualquer prazo futuro; encerradas nos
    últimos 60 dias; verificadas; e as captadas nos últimos 14 dias.
    Motivo: com a carga histórica o arquivo do painel chegou a 37 MB — acima
    do limite de 2 MB definido no parecer de arquitetura."""
    corte_enc = (hoje - timedelta(days=60)).isoformat()
    corte_col = (hoje - timedelta(days=14)).isoformat()
    def col(e): return str((e.get("detalhes") or {}).get("coletado_em") or "")[:10]
    def nucleo(e):
        if e["estado_export"] in ("aberto", "a_abrir"):
            return True
        if e.get("fim") and e["fim"] >= corte_enc:
            return True
        if str(e.get("status", "")).startswith(("verificada", "elegivel")):
            return True
        # captura recente entra direto só quando traz data de inscrição
        return col(e) >= corte_col and e.get("datas") in ("ambas", "so_fim")
    painel = [e for e in editais if nucleo(e)]
    # feed de "novas": as capturas mais recentes SEM data entram até um teto,
    # para o radar mostrar novidade sem estourar o limite de 2 MB do parecer
    ids = {e["id"] for e in painel}
    recentes = sorted((e for e in editais if e["id"] not in ids and col(e) >= corte_col),
                      key=col, reverse=True)[:300]
    return painel + recentes


def _historicos_encerrados(hoje: date, limite: int = 250) -> list[dict]:
    """Editais históricos catalogados (fases 1 e 2) que compõem o filtro
    «inscrições encerradas».

    Vêm do SQLite — o acervo completo tem 9.474 registros e não caberia no
    arquivo publicado. Entram os mais recentes, marcados como catalogados
    (não confundir com os verificados em dupla, que são os do Dashboard vivo).
    """
    try:
        from .banco import consultar_historico, conectar
    except Exception:
        return []
    try:
        con = conectar()
        linhas = con.execute(
            # prioridade: com data real, depois com vencedor/critério
            "SELECT ficha, parecer FROM historico ORDER BY "
            "  (fim IS NOT NULL) DESC, "
            "  (vencedores NOT IN ('[]','')) DESC, "
            "  (criterios NOT IN ('[]','')) DESC, "
            "  data_publicacao DESC LIMIT ?",
            (limite * 3,)).fetchall()
        con.close()
    except Exception:
        return []
    import json as _json
    saida = []
    for f, pj in linhas:
        fi = _json.loads(f)
        # fase 2: fora do escopo do terceiro setor não entra no painel
        if (fi.get("destinacao") or {}).get("elegivel") is False:
            continue
        pa = _json.loads(pj or "{}")
        fim = fi.get("fim")
        saida.append({
            "id": fi["id"], "protocolo": fi["id"],
            "titulo": fi.get("titulo") or "", "url": fi.get("url"),
            "fonte_id": fi.get("fonte_id"), "fonte_nome": fi.get("financiador"),
            "territorio": fi.get("territorio"), "uf": fi.get("uf"),
            "abrangencia": "estadual" if fi.get("uf") else "indefinida",
            "nivel": fi.get("nivel"), "status": "catalogada_historica",
            "area": fi.get("area") or "outros",
            "programa": "—", "lei": "—",
            "objeto": (fi.get("evidencia") or "")[:160],
            "inicio": fi.get("inicio"), "fim": fim,
            "inicio_br": _br(fi.get("inicio")), "fim_br": _br(fim),
            "datas": "ambas" if fi.get("inicio") and fim else ("so_fim" if fim else "nenhuma"),
            "publicado_em": fi.get("data_publicacao"),
            "prazo_prorrogado": False,
            "estado_export": fi.get("estado_prazo") or "encerrado",
            "base_do_prazo": fi.get("base_do_prazo"),
            "confirmacao": (fi.get("confirmacao") or {}).get("nivel_confirmacao"),
            "destinacao": fi.get("destinacao"),
            "nivel_confirmacao_itens": (fi.get("confirmacao") or {}).get("nao_comprovados", [])[:6],
            "resumo": (fi.get("evidencia") or "")[:180],
            "valor_texto": (fi.get("valores_citados") or [None])[0],
            "acervo": "historico",
            "historico": {"vencedores": fi.get("vencedores_identificados") or [],
                          "fator_decisivo": pa.get("fator_decisivo"),
                          "forca_probatoria": pa.get("forca_probatoria"),
                          "uso_recomendado": pa.get("uso_recomendado"),
                          "leitura_do_conselho": pa.get("leitura_do_conselho")},
            "detalhes": {"qualificacao": {"nota": None, "classe": "histórico"},
                         "documentos_exigidos": fi.get("exigencias_detectadas") or [],
                         "pontuacao": [], "atendidos": [],
                         "pendencias": fi.get("lacunas") or [],
                         "evidencia": fi.get("evidencia") or "",
                         "coletado_em": fi.get("data_publicacao"),
                         "lacuna": None},
            "marcos": _marcos_projetados(fim),
            "anexos": [], "ficha": "",
        })
    return saida[:limite]


def _marcos_projetados(fim: str | None) -> list[dict]:
    """Marcos do ciclo, projetados a partir do prazo de inscrição quando o
    edital não os publica. Projeção vem sempre declarada."""
    if not fim:
        return []
    from datetime import timedelta as _td
    d = date.fromisoformat(fim)
    return [
        {"tipo": "encerramento", "data": fim, "projetado": False},
        {"tipo": "resultado_preliminar", "data": (d + _td(days=15)).isoformat(),
         "projetado": True, "base": "praxe: ~15 dias após o encerramento"},
        {"tipo": "recurso", "data": (d + _td(days=16)).isoformat(),
         "projetado": True, "base": "praxe: abre no dia seguinte ao resultado"},
    ]


def ciclo_do_edital(e: dict) -> dict:
    """As três faixas do Calendário de Editais, na cor da área:

      1. INSCRIÇÃO — barra preenchida do dia de abertura ao último dia;
      2. RESULTADO — estrela na data de divulgação;
      3. RECURSO   — barra preenchida do primeiro ao último dia do prazo.

    Datas publicadas prevalecem. Sem publicação, projeta-se pela praxe
    (resultado ~15 dias após o encerramento; recurso nos 5 dias seguintes) e a
    projeção fica declarada em cada item. O edital permanece no calendário até
    o ENCERRAMENTO TOTAL do ciclo — não some quando a inscrição fecha.
    """
    from datetime import timedelta as _td
    marcos = {m["tipo"]: m for m in (e.get("marcos") or []) if m.get("data")}
    fim = e.get("fim")
    ciclo: dict = {"inscricao": None, "resultado": None, "recurso": None}

    if e.get("inicio") and fim:
        ciclo["inscricao"] = {"inicio": e["inicio"], "fim": fim, "projetado": False}
    elif fim:
        # Abertura não declarada: projeta-se a partir da PUBLICAÇÃO (o edital
        # não existia antes dela) e, sem publicação, pela praxe de 30 dias de
        # janela. A barra aparece como projeção — igual ao recurso.
        pub = e.get("publicado_em") or (e.get("detalhes") or {}).get("coletado_em")
        pub = str(pub or "")[:10] or None
        if pub and pub < fim:
            ini_proj, base = pub, "abertura projetada pela data de publicação"
        else:
            ini_proj = (date.fromisoformat(fim) - _td(days=30)).isoformat()
            base = "abertura projetada pela praxe (janela de 30 dias)"
        ciclo["inscricao"] = {"inicio": ini_proj, "fim": fim, "projetado": True,
                              "base": base,
                              "nota": "abertura não declarada na fonte"}

    res = marcos.get("resultado_preliminar") or marcos.get("resultado_final")
    if res:
        ciclo["resultado"] = {"data": res["data"],
                              "projetado": bool(res.get("projetado")),
                              "base": res.get("base"),
                              "tipo": ("resultado_final" if "resultado_final" in marcos
                                       and res is marcos.get("resultado_final")
                                       else "resultado_preliminar")}

    rec = marcos.get("recurso")
    if rec:
        ini = date.fromisoformat(rec["data"])
        fim_rec = rec.get("fim") or (ini + _td(days=4)).isoformat()
        ciclo["recurso"] = {"inicio": rec["data"], "fim": fim_rec,
                            "projetado": bool(rec.get("projetado")),
                            "base": rec.get("base") or "praxe: 5 dias de prazo recursal"}

    ultimas = [x for x in (
        (ciclo["recurso"] or {}).get("fim"),
        (ciclo["resultado"] or {}).get("data"),
        (ciclo["inscricao"] or {}).get("fim")) if x]
    ciclo["fim_do_ciclo"] = max(ultimas) if ultimas else None
    return ciclo


def _so_completos(editais: list[dict], hoje: date) -> list[dict]:
    """REGRA DO TITULAR: apenas editais VERIFICADOS EM DUPLA (fonte + conteúdo
    completo pela campanha de 30 dias) compõem o Dashboard. Datas passam a vir
    do texto integral; cada item carrega o selo da verificação e os modelos."""
    from . import completude as _comp
    mapa = _comp.completos()
    saida = []
    for e in editais:
        c = mapa.get(e["id"])
        if not c:
            continue
        e = dict(e)
        e["inicio"], e["fim"] = c.get("inicio") or e["inicio"], c.get("fim") or e["fim"]
        e["datas"] = "ambas" if e["inicio"] and e["fim"] else ("so_fim" if e["fim"] else e["datas"])
        situ = _situacao(e["inicio"], e["fim"], hoje)
        e["estado_export"] = situ["estado"]
        e["verificacao_dupla"] = c["verificacao"]
        e["anexos_modelo"] = [{"nome": a["nome"], "arquivo": a["arquivo"]}
                              for a in c.get("anexos_modelo", [])]
        e["pasta_farol"] = f'dados/farol/editais/{c["chave"]}/{c["ano"]}'
        saida.append(e)
    return saida


TIPOS_DECISAO = ("resultado_preliminar", "resultado_final", "recurso")


def etapa_do_edital(e: dict, decididos: set, preparados: set,
                    com_parecer: set) -> dict:
    """Em que etapa do fluxo este edital está — a mesma numeração do painel.

      1 Descobrir  identificado, aguardando confirmação
      2 Confirmar  verificação dupla concluída (ou confirmação documental)
      3 Enquadrar  conselho deliberou (parecer emitido)
      4 Decidir    entidade escolhida e pasta do edital criada
      5 Preparar   documentos preenchidos e nota técnica emitida
    """
    chave = (e.get("pasta_farol") or "").split("/")
    ident = f'{chave[-2]}/{chave[-1]}' if len(chave) >= 2 else None
    if ident and ident in preparados:
        n = 5
    elif ident and ident in decididos:
        n = 4
    elif ident and ident in com_parecer:
        n = 3
    elif e.get("verificacao_dupla") or e.get("confirmacao") == "confirmado_documental":
        n = 2
    else:
        n = 1
    return {"etapa": n,
            "etapa_nome": ("Descobrir", "Confirmar", "Enquadrar",
                           "Decidir", "Preparar")[n - 1]}


def _marca_etapas(editais: list[dict]) -> list[dict]:
    from .biblioteca import OPORTUNIDADES as _OP
    def conjunto(padrao):
        return {f"{p.parent.parent.name}/{p.parent.name}"
                for p in _OP.glob(padrao)} if _OP.exists() else set()
    decididos = conjunto("*/*/decisao.json")
    preparados = conjunto("*/*/preparacao.json")
    praiz = ROOT / "biblioteca_alexandria/pareceres"
    com_parecer = ({f"{p.parent.parent.name}/{p.parent.name}"
                    for p in praiz.glob("*/*/parecer.json")} if praiz.exists() else set())
    com_parecer |= conjunto("*/*/conselho.json")
    for e in editais:
        if e.get("sem_edital") or e.get("janela_confirmada"):   # etapa e ciclo próprios
            continue
        e.update(etapa_do_edital(e, decididos, preparados, com_parecer))
        e["ciclo"] = ciclo_do_edital(e)
    return editais


def _parecer_prazos() -> dict:
    """Resumo do parecer de prazo das 260 fontes (a lista completa vai em
    fragmento; aqui só o que o painel mostra de imediato)."""
    p = ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json"
    if not p.exists():
        return {}
    d = load_json(p)
    return {k: d.get(k) for k in ("fontes", "permanentes", "periodicos",
                                  "com_datas_conhecidas", "regimes", "por_area",
                                  "goias", "nota")}


def _cobertura_260(previsoes: dict, fichas: dict) -> dict:
    """Quantas das 260 fontes o Calendário de Editais consegue representar hoje,
    e o motivo de cada ausência. Sem isso o calendário mente por omissão."""
    from collections import Counter as _C
    lista = fichas.get("fontes_lista", [])
    itens = previsoes.get("itens", [])
    com_prev = {p.get("id", "").replace("prev260-", "").rsplit("-", 1)[0]
                for p in itens if p.get("das_260")}
    motivos: _C = _C()
    por_area: dict[str, dict] = {}
    for f in lista:
        area = "cultura" if "cultur" in (f["programa"] + f.get("orgao", "")).lower() else \
               "esporte" if "esport" in (f["programa"] + f.get("orgao", "")).lower() else \
               "fundo" if "fundo" in (f["programa"] + f.get("orgao", "")).lower() else "demais"
        a = por_area.setdefault(area, {"fontes": 0, "no_calendario": 0, "com_historico": 0})
        a["fontes"] += 1
        a["com_historico"] += bool(f.get("editais"))
        if f["id"] in com_prev:
            a["no_calendario"] += 1
            motivos["no_calendario"] += 1
        elif not f.get("editais"):
            motivos["sem_historico_para_prever"] += 1
        else:
            motivos["historico_em_um_unico_ano"] += 1
    return {
        "fontes": len(lista), "no_calendario": motivos.get("no_calendario", 0),
        "motivos": dict(motivos), "por_area": por_area,
        "explicacao": ("uma fonte só entra no calendário com janela sustentada por "
                       "publicação no mesmo mês em ANOS DISTINTOS; a coleta começou "
                       "em ago/2026, então quase todo o histórico está em um único "
                       "ano — o segundo ano de observação é o que destrava a previsão"),
        "o_que_destrava": ("extrair as edições do diário (7.094 na fila) recupera "
                           "datas reais de 2021-2025 e cria o segundo ano de observação"),
    }


def _funil_5_passos(base: list[dict], completos: list[dict], _=None) -> dict:
    """Quantos itens estão em cada um dos 5 passos, agora.

    1 Descobrir  · tudo que foi identificado
    2 Confirmar  · campanhas de completude em andamento
    3 Enquadrar  · editais completos na Biblioteca (com parecer, quando houver)
    4 Decidir    · editais com decisão registrada (pasta criada na entidade)
    5 Preparar   · editais com documentos preenchidos e nota técnica
    """
    from . import completude as _comp
    from .biblioteca import OPORTUNIDADES as _OP
    campanhas = _comp._estado().get("campanhas", {})
    em_campanha = sum(1 for c in campanhas.values() if c.get("status") == "monitorando")
    decididos = len(list(_OP.glob("*/*/decisao.json"))) if _OP.exists() else 0
    preparados = len(list(_OP.glob("*/*/preparacao.json"))) if _OP.exists() else 0
    pareceres = len(list((ROOT / "biblioteca_alexandria/pareceres").glob("*/*/parecer.json"))) \
        if (ROOT / "biblioteca_alexandria/pareceres").exists() else 0
    conselhos = len(list(_OP.glob("*/*/conselho.json"))) if _OP.exists() else 0
    passos = [
        {"n": 1, "nome": "Descobrir", "modulo": "Eldorado",
         "descricao": "mapear oportunidades e fontes de recursos",
         "quantidade": len(base)},
        {"n": 2, "nome": "Confirmar", "modulo": "Eldorado",
         "descricao": "elegibilidade, requisitos, documentos e anexos",
         "quantidade": em_campanha},
        {"n": 3, "nome": "Enquadrar", "modulo": "Eldorado + Farol",
         "descricao": "Biblioteca alimentada; IA cruza requisitos e histórico",
         "quantidade": len(completos), "pareceres": pareceres,
         "conselhos": conselhos,
         "instrumento": "conselho de 7 lentes — voto do neutro é vinculante"},
        {"n": 4, "nome": "Decidir", "modulo": "Farol",
         "descricao": "entidades com chance real e documentos separados",
         "quantidade": decididos},
        {"n": 5, "nome": "Preparar", "modulo": "Farol",
         "descricao": "documentos preenchidos e nota técnica do que falta",
         "quantidade": preparados},
    ]
    return {"passos": passos, "atualizado_em": now_iso(),
            "nota": "etapas 4 e 5 são automáticas; não dependem de ação do titular"}


def _calendario_decisao(editais: list[dict], hoje: date) -> dict:
    """Calendário de RESULTADOS e RECURSOS do Farol.

    Reúne os marcos que decidem o destino da inscrição — resultado preliminar,
    resultado final e a fase de recurso — com a contagem de dias. Datas
    ausentes na fonte NÃO são estimadas: viram alerta para acompanhamento.
    """
    itens, sem_data = [], []
    for e in editais:
        marcos = {m["tipo"]: m.get("data") for m in (e.get("marcos") or [])}
        achou = False
        for tipo in TIPOS_DECISAO:
            data = marcos.get(tipo)
            if not data:
                continue
            achou = True
            dias = (date.fromisoformat(data) - hoje).days
            itens.append({
                "edital_id": e["id"], "titulo": e["titulo"], "area": e["area"],
                "fonte_nome": e.get("fonte_nome"), "tipo": tipo, "data": data,
                "dias": dias, "passou": dias < 0,
                "prazo_recurso_aberto": (tipo == "recurso" and dias >= 0),
            })
        if not achou and e.get("estado_export") in ("aberto", "a_abrir"):
            sem_data.append({"edital_id": e["id"], "titulo": e["titulo"],
                             "alerta": "edital sem data de resultado ou recurso "
                                       "declarada — acompanhar publicação"})
    itens.sort(key=lambda x: x["data"])
    proximos = [i for i in itens if not i["passou"]]
    return {"marcos": itens, "proximos": proximos[:12],
            "total": len(itens), "sem_data": sem_data[:20],
            "recursos_abertos": sum(1 for i in itens if i["prazo_recurso_aberto"]),
            "nota": "datas conforme publicadas na fonte; ausência vira alerta, nunca estimativa"}


def _monitoramentos(hoje: date) -> dict:
    """Bússola: os MONITORAMENTOS encontrados — cada identificação com sua
    campanha diária de completude (dia X/30, tentativas, pendências)."""
    from . import completude as _comp
    est = _comp._estado()
    campanhas = est.get("campanhas", {})
    itens = {}
    for oid, item in carregar_oportunidades().items():
        itens[oid] = item
    amostra = []
    contagem = {"encontrados": len(campanhas), "monitorando": 0,
                "completos": 0, "expirados": 0}
    for oid, c in campanhas.items():
        contagem[{"monitorando": "monitorando", "completo": "completos",
                  "expirado": "expirados"}.get(c["status"], "monitorando")] += 1
    ordem = sorted(((oid, c) for oid, c in campanhas.items() if oid in itens),
                   key=lambda x: (x[1]["status"] != "monitorando",
                                  x[1].get("criado_em", "")))
    for oid, c in ordem[:40]:
        it = itens[oid]
        dias_camp = (hoje - date.fromisoformat(c["criado_em"])).days + 1
        amostra.append({"id": oid, "titulo": it.get("titulo", "")[:120],
                        "fonte": it.get("fonte_nome"), "territorio": it.get("territorio"),
                        "status": c["status"], "dia": min(dias_camp, 30),
                        "tentativas": len(c.get("tentativas", [])),
                        "pendencias": (c.get("pendencias") or [])[:2],
                        "fim_detectado": c.get("fim_iso"), "url": it.get("url")})
    contagem["amostra"] = amostra
    contagem["regra"] = ("cada identificação em diário abre campanha de até 30 dias "
                         "consecutivos atrás do edital integral nos sites oficiais")
    return contagem


def coletar(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    editais_base = _editais(hoje)
    completos_lista = _so_completos(editais_base, hoje)
    historicos = _historicos_encerrados(hoje)
    from .emendas import oportunidades_do_painel as _emendas
    emendas = _emendas(hoje)
    prev_p = ROOT / "biblioteca_alexandria/previsoes/previsoes.json"
    previsoes = load_json(prev_p) if prev_p.exists() else {"itens": [], "previsoes": 0}
    dos_p = ROOT / "biblioteca_alexandria/fontes/indice.json"
    dossies = load_json(dos_p) if dos_p.exists() else {"itens": []}
    esq_p = ROOT / "estado/esquadra.json"
    esq = load_json(esq_p) if esq_p.exists() else {}
    try:
        from .sensores import escala_do_dia
        escala = escala_do_dia(hoje)
        from collections import Counter as _C
        esquadra = {"total": escala["total"], "saem_hoje": len(escala["saem"]),
                    "em_espera": escala["ficam"], "previsoes_ativas": escala["previsoes_ativas"],
                    "por_tipo": dict(_C(s["tipo"] for s in escala["saem"])),
                    "motivos": dict(_C(s["motivo"].split(":")[0] for s in escala["saem"])),
                    "ultima_execucao": esq.get("ultima_execucao"),
                    "alertas": [{"sensor": k, "alerta": v["alerta"]} for k, v in
                                (esq.get("sensores") or {}).items() if v.get("alerta")][:20]}
    except Exception as exc:
        esquadra = {"erro": type(exc).__name__}
    ft_p = ROOT / "biblioteca_alexandria/fontes/fichas_tres_tempos.json"
    fichas = load_json(ft_p) if ft_p.exists() else {"fontes_lista": []}
    aud_p = ROOT / "biblioteca_alexandria/historico/auditoria_individual.json"
    auditoria = load_json(aud_p) if aud_p.exists() else {}
    vivos = completos_lista
    editais = _marca_etapas(
        (_recorte_painel(vivos, hoje) if len(vivos) > 600 else vivos) + historicos)
    # as três emendas anuais entram como linha própria, já com etapa definida
    from .janelas import oportunidades as _janelas
    janelas = _janelas(hoje)
    editais = emendas + janelas + editais
    # janela confirmada deixa de ser projeção: sai da lista de previsões do ano
    conf_ids = {f'prev-{j["fonte_id"]}-{hoje.year}' for j in janelas}
    previsoes["itens"] = [p0 for p0 in previsoes.get("itens", []) if p0["id"] not in conf_ids]
    leis = load_json(ROOT / "biblioteca/leis/catalogo.json")["itens"]
    revisao = load_json(ROOT / "estado/revisao_normativa.json") if (ROOT / "estado/revisao_normativa.json").exists() else {}
    parl = mod_parlamentares.carregar_do_disco(hoje.year)
    ch = load_json(ROOT / "estado/ultima_carga_historica.json") if (ROOT / "estado/ultima_carga_historica.json").exists() else {"status": "nunca_executada"}
    from . import biblioteca as _bib
    import os as _os
    bib_idx = _bib.RAIZ / "indice.json"
    biblioteca = load_json(bib_idx) if bib_idx.exists() else {}
    for acervo, arq in (("leis", _bib.LEIS), ("oportunidades", _bib.OPORTUNIDADES),
                        ("associacoes", _bib.ASSOCIACOES)):
        i = arq / "indice.json"
        if i.exists():
            d0 = load_json(i)
            biblioteca.setdefault("detalhe", {})[acervo] = {
                k: v for k, v in d0.items() if k not in ("editais", "por_tema")}
            if acervo == "leis":
                biblioteca["detalhe"][acervo]["por_tema"] = {
                    tema: [{"titulo": x["titulo"], "tipo": x["tipo"], "esfera": x["esfera"],
                            "status": x["status"]} for x in itens]
                    for tema, itens in d0.get("por_tema", {}).items()}
    pareceres = {}
    praiz = ROOT / "biblioteca_alexandria/pareceres"
    if praiz.exists():
        for pj in praiz.glob("*/*/parecer.json"):
            try:
                pp = load_json(pj)
                pareceres[pp["edital"].get("chave")] = {
                    "recomendacao": pp.get("recomendacao"),
                    "alertas": pp.get("alertas", []),
                    "resumo": (pp.get("ia") or {}).get("parecer", "")[:1200],
                    "gerado_em": pp.get("gerado_em")}
            except Exception:
                continue
    decisao = _calendario_decisao(completos_lista, hoje)
    funil = _funil_5_passos(editais_base, completos_lista, monit_prev := None)
    monit = _monitoramentos(hoje)
    saida_bussola = painel_bussola(completos_lista, _bussola(editais), hoje)
    saida_bussola["monitoramentos"] = monit
    saida_bussola["totais"] = {"base_completa": len(editais_base),
        "monitoramentos": monit["encontrados"], "completos": len(completos_lista),
        "no_painel": len(editais), "historicos_catalogados": len(historicos),
        "nota": "o Dashboard publica somente editais completos (verificação dupla); "
                "o restante segue em monitoramento na Bússola"}
    return {
        "gerado_em": now_iso(), "referencia": hoje.isoformat(),
        "cadencia": {"varredura": "segundas e sextas, 6h de Brasília",
                     "leis": "revisão mensal (dia 1º)",
                     "historico": "compilado mensal + campanha única de 5 anos"},
        "areas": AREAS, "tipos_evento": _TIPOS_EVT,
        "editais": editais,
        "eventos": _eventos(editais),
        "biblioteca": biblioteca, "pareceres": pareceres,
        "calendario_decisao": decisao, "funil": funil,
        "previsoes": {"referencia": previsoes.get("referencia"),
                      "total": previsoes.get("previsoes", 0),
                      "por_mes": previsoes.get("por_mes", {}),
                      "cor": COR_PREVISAO,
                      # só o essencial de cada previsão (o detalhe fica na Biblioteca)
                      "itens": [{k: i.get(k) for k in
                                 ("id", "titulo", "orgao", "area", "uf", "nivel", "inicio",
                                  "fim", "forca", "especial", "das_260", "goias", "base",
                                  "status_verificacao", "fonte_confirmacao", "lei")}
                                for i in previsoes.get("itens", [])]},
        "esquadra": esquadra,
        "auditoria": {k: auditoria.get(k) for k in
                      ("editais_auditados", "completos_11_itens", "parciais_6_a_10",
                       "abaixo_de_6", "causas", "itens_que_mais_faltam", "por_ano",
                       "dominios_sem_sensor", "janela")},
        "fontes_tres_tempos": {k: fichas.get(k) for k in ("fontes", "com_passado", "com_presente", "com_futuro")},
        "cobertura_calendario": _cobertura_260(previsoes, fichas),
        "parecer_prazos": _parecer_prazos(),
        "dossies_fontes": {"total": dossies.get("fontes", 0),
                           "com_historico": dossies.get("com_historico", 0),
                           "conselhos": dossies.get("conselhos", 0),
                           "itens": [i for i in dossies.get("itens", []) if i.get("editais")]},
        "bussola": _bussola(editais),
        "bussola_painel": saida_bussola,
        "farol_resumo": _farol_resumo(editais),
        "farol": {
            "documentos": {"status": "em_construcao", "nota": "ícones e detalhes serão definidos posteriormente"},
            "biblioteca": [{"id": l["id"], "titulo": l["titulo"], "esfera": l.get("esfera"),
                            "tipo": l.get("tipo"), "status": l.get("status")} for l in leis],
            "revisao_normativa": {k: revisao.get(k) for k in ("executado_em", "alteradas", "sem_url") if k in revisao},
        },
        "emendas": {"meses": [10, 11], "aciona_farol": False,
                    "parlamentares": parl.get("parlamentares", []), "pendencias": parl.get("pendencias", [])},
        "carga_historica": ch,
        "avisos": ["Dados automatizados exigem conferência na fonte primária.",
                   "Datas e requisitos ausentes são lacunas declaradas, nunca estimadas.",
                   "Detecção de resultado/prorrogação é textual — conferir na página."],
    }

LIMITE_TOTAL_MB = 20      # orçamento total do painel (núcleo + fragmentos)
LIMITE_NUCLEO_MB = 3      # o que carrega na abertura; o resto vem sob demanda


def publicar_fragmentos(dados: dict, hoje: date) -> dict:
    """Publicação em CAMADAS: o núcleo carrega na abertura; fragmentos
    compactados por dicionário são buscados sob demanda pelo painel.

    - historico.json ...... até 4.000 editais históricos (filtro «encerradas»)
    - previsoes.json ...... todas as previsões dos próximos 12 meses
    - parlamentares.json .. levantamento completo das emendas
    Cada fragmento contém apenas dado de registro público (editais e mandatos).
    """
    from .compacto import compactar, tamanho
    pasta = ROOT / "docs/dados"
    pasta.mkdir(parents=True, exist_ok=True)
    tamanhos = {}

    hist = _historicos_encerrados(hoje, limite=4000)
    campos_h = ["id", "protocolo", "titulo", "url", "fonte_id", "fonte_nome", "territorio",
                "uf", "abrangencia", "nivel", "status", "area", "objeto", "inicio", "fim",
                "datas", "publicado_em", "estado_export", "resumo", "valor_texto", "acervo",
                "confirmacao", "etapa", "etapa_nome"]
    hist_l = _marca_etapas(hist)
    pac = compactar([{k: e.get(k) for k in campos_h} for e in hist_l], campos_h)
    pac["ciclos"] = {e["id"]: e.get("ciclo") for e in hist_l if e.get("ciclo")}
    pac["historico"] = {e["id"]: e.get("historico") for e in hist_l}
    (pasta / "historico.json").write_text(json.dumps(pac, ensure_ascii=False,
                                                     separators=(",", ":")), encoding="utf-8")
    tamanhos["historico.json"] = tamanho(pac)

    prev = dados.get("previsoes", {}).get("itens", [])
    campos_p = ["id", "titulo", "orgao", "area", "uf", "nivel", "inicio", "fim", "forca",
                "especial", "das_260", "goias", "base", "status_verificacao",
                "fonte_confirmacao", "lei"]
    pacp = compactar([{k: p0.get(k) for k in campos_p} for p0 in prev], campos_p)
    (pasta / "previsoes.json").write_text(json.dumps(pacp, ensure_ascii=False,
                                                     separators=(",", ":")), encoding="utf-8")
    tamanhos["previsoes.json"] = tamanho(pacp)

    pp = ROOT / "biblioteca_alexandria/fontes/parecer_prazos.json"
    if pp.exists():
        lst = load_json(pp).get("lista", [])
        pacp2 = compactar([{**x, "proxima_data": (x.get("proxima_data") or {}).get("inicio"),
                            "proxima_fim": (x.get("proxima_data") or {}).get("fim"),
                            "proxima_origem": (x.get("proxima_data") or {}).get("origem")}
                           for x in lst]) if lst else {"campos": [], "dic": {}, "linhas": []}
        (pasta / "prazos.json").write_text(json.dumps(pacp2, ensure_ascii=False,
                                                      separators=(",", ":")), encoding="utf-8")
        tamanhos["prazos.json"] = tamanho(pacp2)

    ft_p = ROOT / "biblioteca_alexandria/fontes/fichas_tres_tempos.json"
    if ft_p.exists():
        lista = load_json(ft_p).get("fontes_lista", [])
        pacf = compactar(lista) if lista else {"campos": [], "dic": {}, "linhas": []}
        (pasta / "fontes.json").write_text(json.dumps(pacf, ensure_ascii=False,
                                                      separators=(",", ":")), encoding="utf-8")
        tamanhos["fontes.json"] = tamanho(pacf)

    parl = {}
    for e in dados.get("editais", []):
        if e.get("sem_edital") and e.get("parlamentares"):
            parl[e["id"]] = compactar(e["parlamentares"])
    (pasta / "parlamentares.json").write_text(json.dumps(parl, ensure_ascii=False,
                                                         separators=(",", ":")), encoding="utf-8")
    tamanhos["parlamentares.json"] = tamanho(parl)
    return {"fragmentos": tamanhos, "total_bytes": sum(tamanhos.values()),
            "historico_publicado": len(hist_l), "previsoes_publicadas": len(prev)}


def enxugar_nucleo(dados: dict, hoje: date) -> dict:
    """O núcleo fica com o que a abertura precisa; o resto aponta para o fragmento."""
    prev = dados.get("previsoes", {})
    lim = f"{hoje.year + (hoje.month + 1) // 12}-{(hoje.month + 1) % 12 + 1:02d}"
    # no núcleo: os dois meses seguintes + TODAS as janelas especiais (Rouanet,
    # Aldir Blanc, Goyazes) e as das 260 fontes de Goiás — são a informação que
    # o titular procura primeiro; o restante vem do fragmento sob demanda
    prev["itens"] = [p0 for p0 in prev.get("itens", [])
                     if p0["inicio"][:7] <= lim or p0.get("especial")
                     or (p0.get("das_260") and p0.get("goias"))]
    prev["completo"] = False
    prev["fragmento"] = "dados/previsoes.json"
    for e in dados.get("editais", []):
        if e.get("sem_edital"):
            e["parlamentares_total"] = len(e.get("parlamentares") or [])
            e["parlamentares"] = []
            e["fragmento_parlamentares"] = "dados/parlamentares.json"
    dados["fragmentos"] = {"historico": "dados/historico.json",
                           "previsoes": "dados/previsoes.json",
                           "parlamentares": "dados/parlamentares.json",
                           "nota": "carregados sob demanda; só registro público"}
    return dados


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    dados = coletar(hoje)
    from .fidelidade import aplicar as _portao
    portao = _portao(dados, hoje)            # ÚLTIMO passo antes de publicar
    frag = publicar_fragmentos(dados, hoje)
    dados = enxugar_nucleo(dados, hoje)
    write_json(ROOT / "docs/dashboard-dados.json", dados)
    conteudo = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (ROOT / "docs/dashboard-dados.js").write_text("window.DADOS=" + conteudo + ";\n", encoding="utf-8")
    import os
    nucleo = os.path.getsize(ROOT / "docs/dashboard-dados.js")
    return {"gerado_em": dados["gerado_em"], "editais": len(dados["editais"]),
            "eventos_calendario": len(dados["eventos"]),
            "dias_com_busca": len(dados["bussola"]["dias"]),
            "publicacao": {"nucleo_mb": round(nucleo / 1048576, 2),
                           "fragmentos_mb": round(frag["total_bytes"] / 1048576, 2),
                           "total_mb": round((nucleo + frag["total_bytes"]) / 1048576, 2),
                           "limite_total_mb": LIMITE_TOTAL_MB,
                           "portao_fidelidade": {"classes": portao["classes"], "removidos": portao["removidos"]},
                           "limite_nucleo_mb": LIMITE_NUCLEO_MB,
                           **{k: v for k, v in frag.items() if k != "total_bytes"}}}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
