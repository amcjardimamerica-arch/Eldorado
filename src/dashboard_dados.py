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
from datetime import date, datetime

from . import parlamentares as mod_parlamentares
from .programas import caracterizar
from .relatorio_busca import _situacao
from .nucleo import ROOT, carregar_oportunidades, load_json, now_iso, write_json

# ---------------- áreas e cores (tons claros) ----------------
AREAS = {
    "cultura":            {"rotulo": "Cultura",              "cor": "#7C4DBE"},
    "esporte":            {"rotulo": "Esporte",              "cor": "#1E7E4B"},
    "educacao":           {"rotulo": "Educação",             "cor": "#1F5B99"},
    "assistencia_social": {"rotulo": "Assistência social",   "cor": "#C2571B"},
    "crianca_adolescente":{"rotulo": "Criança e adolescente","cor": "#C23B69"},
    "pessoa_idosa":       {"rotulo": "Pessoa idosa",         "cor": "#8A6A16"},
    "saude":              {"rotulo": "Saúde",                "cor": "#0F8B8D"},
    "meio_ambiente":      {"rotulo": "Meio ambiente",        "cor": "#4A7C2F"},
    "direitos_humanos":   {"rotulo": "Direitos humanos",     "cor": "#5B5EA6"},
    "justica":            {"rotulo": "Justiça",              "cor": "#6D4C41"},
    "seguranca_alimentar":{"rotulo": "Segurança alimentar",  "cor": "#B0752B"},
    "outros":             {"rotulo": "Outros",               "cor": "#607086"},
}
_PALAVRAS_AREA = [
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

def _editais(hoje: date) -> list[dict]:
    cfg_prog = load_json(ROOT / "config/programas.json")
    saida = []
    for item in carregar_oportunidades().values():
        if item.get("status") in {"quarentena_prompt_injection", "descartada"}:
            continue
        carac = item.get("caracterizacao") or caracterizar(item, cfg_prog)
        periodo = carac.get("periodo") or {}
        fim_iso = _iso_de_br(item.get("prazo_texto")) or periodo.get("fim")
        situ = _situacao(periodo.get("inicio"), fim_iso, hoje)
        q = item.get("qualidade") or {}
        req = item.get("requisitos") or {}
        fonte = _fontes().get(item.get("fonte_id")) or {}
        saida.append({
            "id": item["id"], "protocolo": item["id"],
            "titulo": item.get("titulo"), "url": item.get("url"),
            "fonte_id": item.get("fonte_id"), "fonte_nome": item.get("fonte_nome"),
            "territorio": item.get("territorio"), "nivel": item.get("nivel"),
            "status": item.get("status"), "confianca": item.get("confianca"),
            "area": area_do_edital(item), "programa": carac.get("programa"),
            "lei": carac.get("lei"), "objeto": carac.get("modalidade"),
            "inicio": periodo.get("inicio"), "fim": fim_iso,
            "inicio_br": _br(periodo.get("inicio")), "fim_br": _br(fim_iso),
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
    dias = [{"data": k, "houve_busca": True, "camadas": sorted(set(v["buscas"])),
             "fontes_ok": v["fontes_ok"], "fontes_falha": v["fontes_falha"], "novas": v["novas"],
             "validado": v["fontes_falha"] == 0}
            for k, v in sorted(por_dia.items())]
    # fontes com edital aberto: caixa própria com links e anexos
    abertos = [e for e in editais if e["estado_export"] in {"aberto", "a_abrir", "sem_prazo"}]
    por_fonte: dict[str, dict] = {}
    for e in abertos:
        f = _fontes().get(e["fonte_id"]) or {}
        cx = por_fonte.setdefault(e["fonte_id"], {
            "fonte_id": e["fonte_id"], "fonte_nome": e["fonte_nome"],
            "url_fonte": f.get("url"), "tipo": f.get("tipo"),
            "categoria": _categoria_fonte(f.get("tipo")),
            "editais": []})
        cx["editais"].append({"id": e["id"], "titulo": e["titulo"], "url": e["url"],
                              "anexos": e["anexos"],
                              "anexos_pendentes": not e["anexos"]})
    return {"dias": dias, "categorias": CATEGORIAS_FONTE,
            "fontes_com_editais": sorted(por_fonte.values(), key=lambda x: -len(x["editais"])),
            "regra": "monitor de integridade: cada dia registra se houve busca e o que validou; anexos ausentes são pendência declarada, não omissão silenciosa"}

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
        "documentacao_pronta": [
            {"id": e["id"], "titulo": e["titulo"], "area": e["area"], "status": e["status"],
             "qualificacao": e["detalhes"]["qualificacao"]}
            for e in editais if str(e["status"]).startswith(("verificada", "elegivel"))][:6],
    }

def coletar(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    editais = _editais(hoje)
    leis = load_json(ROOT / "biblioteca/leis/catalogo.json")["itens"]
    revisao = load_json(ROOT / "estado/revisao_normativa.json") if (ROOT / "estado/revisao_normativa.json").exists() else {}
    parl = mod_parlamentares.carregar_do_disco(hoje.year)
    ch = load_json(ROOT / "estado/ultima_carga_historica.json") if (ROOT / "estado/ultima_carga_historica.json").exists() else {"status": "nunca_executada"}
    return {
        "gerado_em": now_iso(), "referencia": hoje.isoformat(),
        "cadencia": {"varredura": "segundas e sextas, 6h de Brasília",
                     "leis": "revisão mensal (dia 1º)",
                     "historico": "compilado mensal + campanha única de 5 anos"},
        "areas": AREAS, "tipos_evento": _TIPOS_EVT,
        "editais": editais,
        "eventos": _eventos(editais),
        "bussola": _bussola(editais),
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

def run(hoje: date | None = None) -> dict:
    dados = coletar(hoje)
    write_json(ROOT / "docs/dashboard-dados.json", dados)
    conteudo = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (ROOT / "docs/dashboard-dados.js").write_text("window.DADOS=" + conteudo + ";\n", encoding="utf-8")
    return {"gerado_em": dados["gerado_em"], "editais": len(dados["editais"]),
            "eventos_calendario": len(dados["eventos"]),
            "dias_com_busca": len(dados["bussola"]["dias"])}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
