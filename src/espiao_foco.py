"""PILOTO - ESPIÃO · FOCO PRIVADO E INTERNACIONAL (titular, 09/10/2026).

Avaliação que motivou (semana de 08 a 09/10): 792 missões, 2 com resultado (0,25%); 782 vazias. As buscas eram de
editais PÚBLICOS (secretarias, câmaras, prefeituras) — o território dos 142 motores — e a "descoberta de entidades"
registrou 179 nomes sem CNPJ, vários que nem são empresas.

Novo papel: o Espião caça SÓ o que nenhum motor alcança —
  editais_de_empresas        editais e chamadas de institutos, fundações e empresas privadas
  oportunidades_de_empresas  patrocínio, doação, investimento social, voluntariado, matching, cessão — mesmo sem edital
  internacional              fundos, embaixadas, cooperação, fundações estrangeiras, chamadas em inglês e espanhol
Descarta: domínio de governo (é dos motores), agregadores, endereço já vigiado por um motor, o que já está cadastrado.

Buscas CRIATIVAS por famílias (combinações de setor, empresa conhecida, público, região, idioma, operador de busca,
financiador internacional, rastro de patrocínio). A família é escolhida por amostragem de Thompson (aprende sozinha).
A cada 100 VOOS: avaliação com a REDE NEURAL (nota de oportunidade real de cada achado) — reforça as famílias que
rendem, aposenta as consultas que falharam, cria mutações novas das melhores. Histórico em estado/piloto/espiao_cerebro.json.

Empresas novas encontradas vão ao campo de empresas (motor de patrocínio privado → painel "Oportunidades de Empresas"),
marcadas com a modalidade (doação, patrocínio, edital próprio, internacional) e se estão FORA da lista de incentivo fiscal.
"""
from __future__ import annotations

import json
import math
import random
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CEREBRO = ROOT / "estado/piloto/espiao_cerebro.json"
CANDIDATAS = ROOT / "estado/piloto/candidatas_do_catalogo.json"
EMPRESAS_ESPIAO = ROOT / "dados/empresas/go/espiao_empresas.json"
AVALIACAO = ROOT / "docs/dados/espiao_avaliacao.json"
CICLO_VOOS = 100

SETORES = ["mineradora", "agronegócio", "cooperativa agroindustrial", "energia elétrica", "saneamento", "rede de supermercados",
           "atacarejo", "banco", "cooperativa de crédito", "operadora de telefonia", "indústria farmacêutica", "frigorífico",
           "construtora", "empresa de tecnologia", "seguradora", "montadora", "indústria de alimentos", "indústria de bebidas",
           "shopping center", "rede de farmácias", "transportadora", "usina de etanol", "indústria de fertilizantes", "hospital privado"]
APOIOS = ["edital de patrocínio", "chamada de projetos sociais", "programa de investimento social", "seleção de projetos",
          "fundo de doação para ONGs", "doação de equipamentos para entidades", "voluntariado corporativo", "doação casada (matching)",
          "prêmio de iniciativas sociais", "patrocínio a projetos culturais", "patrocínio a projetos esportivos", "apoio a projetos comunitários",
          "doação de alimentos para instituições", "edital do instituto", "chamada pública de parceiros sociais"]
PUBLICOS = ["crianças e adolescentes", "pessoa idosa", "mulheres", "juventude", "pessoas com deficiência", "comunidades periféricas",
            "catadores de recicláveis", "agricultura familiar", "cultura popular", "esporte de base", "educação", "meio ambiente",
            "segurança alimentar", "população em situação de rua"]
REGIOES = ["Goiás", "Goiânia", "Centro-Oeste", "Brasil", "Anápolis", "Aparecida de Goiânia", "Rio Verde"]
INTERNACIONAIS = ["Fundo Canadá para Iniciativas Locais", "Embaixada da Alemanha microprojetos", "Embaixada do Japão Assistência a Projetos Comunitários",
                  "Embaixada da França fundo de apoio", "Embaixada dos Países Baixos", "União Europeia sociedade civil Brasil",
                  "Fundação Interamericana IAF", "GEF Small Grants Programme Brasil", "Global Fund for Children", "Fundação Avina",
                  "Open Society Foundations", "Ford Foundation Brasil", "W.K. Kellogg Foundation", "Porticus", "Laudes Foundation",
                  "Oak Foundation", "ONU Mulheres fundo", "UNESCO Fundo Internacional para a Diversidade Cultural", "Ibercultura Viva",
                  "Iberescena", "Ibermedia", "Rotary Foundation global grants", "Lions LCIF", "Fondation de France", "Comic Relief"]
EN = ["call for proposals Brazil civil society {ano}", "grants for NGOs in Brazil {ano}", "small grants Brazil community organizations {ano}",
      "funding opportunity nonprofits Latin America {ano} Brazil eligible", "request for proposals Brazil social projects {ano}"]
ES = ["convocatoria organizaciones de la sociedad civil Brasil {ano}", "fondos para ONG América Latina Brasil {ano}",
      "convocatoria proyectos comunitarios Brasil elegible {ano}"]
OPERADORES = ['"regulamento" "inscrições"', 'filetype:pdf "edital"', 'intitle:edital', '"inscrições abertas"', '"chamada de projetos"']
NAO_EMPRESA = re.compile(r"(?i)\b(governo|prefeitura|secretaria|minist[ée]rio|c[âa]mara|assembleia|tribunal|universidade federal|"
                         r"pol[íi]tica nacional|lei |edital n|di[áa]rio oficial|ve[íi]culos?|not[íi]cias?|portal)\b")
OPORT = re.compile(r"(?i)edital|regulamento|inscri[çc][õo]es|chamada|call for proposals|apply now|grant|convocatoria|patroc[ií]nio|"
                   r"doa[çc][ãa]o|sele[çc][ãa]o de projetos|programa de apoio|investimento social|fondos?")
OSC = re.compile(r"(?i)\bosc\b|\bongs?\b|organiza[çc][õo]es? (da sociedade civil|sociais|sem fins)|associa[çc][õo]es|sociedade civil|"
                 r"nonprofit|non-profit|\bngos?\b|sin fines de lucro|terceiro setor|projetos sociais|entidades")


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _w(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ── FAMÍLIAS DE BUSCA CRIATIVA ─────────────────────────────────────────────────────────────────────────────────
def _empresas_semente() -> list[str]:
    """Empresas já conhecidas que patrocinam ou destinam — viram ponto de partida para achar o instituto e o edital delas."""
    out = []
    for f in ("biblioteca_alexandria/empresas/ranking_patrocinio_privado.json", "docs/dados/ranking_apoiadores.json",
              "biblioteca_alexandria/empresas/go/patrocinios.json"):
        for e in (_j(ROOT / f, {}).get("empresas") or [])[:200]:
            n = str(e.get("nome") or e.get("razao_social") or "").strip()
            if 4 <= len(n) <= 60 and not NAO_EMPRESA.search(n):
                out.append(n)
    return list(dict.fromkeys(out))[:300]


SITES_FECHADOS = {
    "idx-prosas": ['"inscrições" "pelo Prosas" edital {ano}', '"plataforma Prosas" edital projetos sociais {ano}', '"via Prosas" instituto edital inscrições {ano}',
                   '"prosas.com.br" edital instituto fundação {ano} inscrições abertas'],
    # FINEP fica com os motores e o DOU: domínio de governo é descartado pelo Espião por regra (não é o alvo dele)
}


def _consultas_sites_fechados() -> list[str]:
    """Consultas para os sites fechados que os indexadores pediram ao Piloto (estado/indexadores/angulos_piloto.json)."""
    ids = [a.get("id") for a in (_j(ROOT / "estado/indexadores/angulos_piloto.json", {}).get("angulos") or [])] or list(SITES_FECHADOS)
    out = [q for i in ids for q in SITES_FECHADOS.get(i, [])]
    return out or [q for v in SITES_FECHADOS.values() for q in v]


def familias() -> dict:
    return {
        "setor_apoio_regiao": lambda r, a: f"{r.choice(SETORES)} {r.choice(APOIOS)} {r.choice(REGIOES)} {a}",
        "empresa_semente": lambda r, a: (lambda s: f'"{r.choice(s)}" {r.choice(["instituto", "fundação", "patrocínio", "edital"])} projetos sociais {a}' if s else None)(_empresas_semente()),
        "publico_apoio_empresa": lambda r, a: f"empresa {r.choice(APOIOS)} {r.choice(PUBLICOS)} {r.choice(REGIOES)} {a}",
        "operador_avancado": lambda r, a: f"{r.choice(OPERADORES)} {r.choice(['instituto', 'fundação empresarial', 'empresa'])} {r.choice(PUBLICOS)} {a}",
        "rastro_de_patrocinio": lambda r, a: f'"patrocínio" "{r.choice(PUBLICOS)}" projeto {r.choice(REGIOES)} "apoio" {a}',
        "nao_financeiro": lambda r, a: f"{r.choice(['doação de computadores', 'doação de alimentos', 'cessão de espaço', 'voluntariado de funcionários', 'doação de móveis'])} para ONGs empresa {r.choice(REGIOES)} {a}",
        "internacional_financiador": lambda r, a: f'"{r.choice(INTERNACIONAIS)}" {r.choice(["edital", "chamada", "call for proposals", "inscrições"])} {a}',
        "internacional_ingles": lambda r, a: r.choice(EN).format(ano=a),
        "internacional_espanhol": lambda r, a: r.choice(ES).format(ano=a),
        # 10/10 (titular): SITES FECHADOS a robôs (Prosas, FINEP…) — o Espião acha o FINANCIADOR e o edital no site oficial
        # dele, fora do site fechado (religa o ângulo dos indexadores, que ia nas missões de aposta desligadas pelo foco)
        "sites_fechados": lambda r, a: (lambda q: q.format(ano=a) if q else None)(r.choice(_consultas_sites_fechados())),
        "premio_empresarial": lambda r, a: f"prêmio {r.choice(['inovação social', 'empreendedorismo social', 'impacto social', 'boas práticas'])} {r.choice(SETORES)} inscrições {a}",
    }


FRENTE_DA_FAMILIA = {"sites_fechados": "editais_de_empresas", "internacional_financiador": "internacional", "internacional_ingles": "internacional", "internacional_espanhol": "internacional",
                     "nao_financeiro": "oportunidades_de_empresas", "rastro_de_patrocinio": "oportunidades_de_empresas"}


def cerebro() -> dict:
    c = _j(CEREBRO, {}) or {}
    c.setdefault("regra", __doc__.split("\n\n")[1].strip() if __doc__ else "")
    c.setdefault("voos", 0); c.setdefault("voos_desde_avaliacao", 0); c.setdefault("avaliacoes", [])
    fam = c.setdefault("familias", {})
    for f in familias():
        fam.setdefault(f, {"a": 1.0, "b": 1.0, "usos": 0, "achados": 0, "empresas": 0, "nota_media": None})
    c.setdefault("consultas", {}); c.setdefault("mutacoes", [])
    return c


def escolher(c: dict, rnd: random.Random | None = None) -> tuple[str, str]:
    """(família, consulta). Amostragem de Thompson entre as famílias; 1 em 4 vezes usa uma MUTAÇÃO de consulta boa."""
    rnd = rnd or random.Random()
    ano = date.today().year
    ruins = {q for q, v in c["consultas"].items() if v.get("usos", 0) >= 3 and not v.get("achados")}
    if c.get("mutacoes") and rnd.random() < 0.25:
        q = rnd.choice(c["mutacoes"])
        if q not in ruins:
            return "mutacao", q
    fams = familias()
    sorteio = sorted(((rnd.betavariate(max(0.1, v["a"]), max(0.1, v["b"])), f) for f, v in c["familias"].items() if f in fams), reverse=True)
    for _p, f in sorteio:
        for _ in range(6):
            q = fams[f](rnd, ano)
            if q and q not in ruins:
                return f, re.sub(r"\s+", " ", q).strip()
    return "setor_apoio_regiao", fams["setor_apoio_regiao"](rnd, ano)


# ── O QUE CONTA COMO ACHADO (privado/internacional, fora do alcance dos motores) ───────────────────────────────
def fora_dos_motores(url: str) -> tuple[bool, str]:
    from .cartorio_leitura import GOV, VETOR_ESTRITO
    try:
        h = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return False, "endereço malformado"
    if not h or not url.startswith("http"):
        return False, "sem endereço"
    if GOV.search(h) or h.endswith("in.gov.br"):
        return False, "domínio de governo — é território dos motores"
    if VETOR_ESTRITO.search(url) or re.search(r"(^|\.)(duckduckgo\.com|bing\.com|google\.[a-z.]+|wikipedia\.org|youtube\.com|facebook\.com|"
                                               r"instagram\.com|linkedin\.com|twitter\.com|x\.com|tiktok\.com)$", h):
        return False, "agregador, buscador ou rede social"
    try:
        from .cobertura import ja_coberto
        cob, mid = ja_coberto(url)
        if cob:
            return False, f"já vigiado pelo motor {mid}"
    except Exception:  # noqa: BLE001
        pass
    return True, ""


def frente(url: str, texto: str, fam: str) -> str:
    h = (urlsplit(url).hostname or "").lower()
    t = (texto or "")[:3000]
    if fam in FRENTE_DA_FAMILIA and FRENTE_DA_FAMILIA[fam] == "internacional" or not h.endswith(".br") and \
            re.search(r"(?i)\b(the|grants?|apply|convocatoria|organizaciones)\b", t):
        return "internacional"
    if re.search(r"(?i)edital|regulamento|chamada|sele[çc][ãa]o de projetos|inscri[çc][õo]es", t):
        return "editais_de_empresas"
    return "oportunidades_de_empresas"


GENERICO = re.compile(r"(?i)^(responsabilidade social|sustentabilidade|edital|editais|in[íi]cio|home|projetos?( sociais)?|not[íi]cias?|"
                      r"grants?|call for proposals|apoio|patroc[íi]nio|investimento social|quem somos|contato|programas?|p[áa]gina inicial|bem-vindo|welcome)\b")
ORG = re.compile(r"(?i)\b(instituto|funda[çc][ãa]o|grupo|banco|cooperativa|associa[çc][ãa]o|foundation|fund|trust|embaixada|embassy|"
                 r"rede|empresa|ind[úu]stria|companhia|cia\.?|s\.\s?a\.?|ltda|holding|supermercados?|usina|mineradora)\b")


def nome_da_organizacao(titulo: str, url: str) -> str:
    """Do título da página ('Edital 2026 | Instituto X'), a parte que nomeia a organização; senão, o domínio."""
    partes = [p.strip() for p in re.split(r"\s[|–—-]\s|\s::\s", titulo or "") if p.strip()]
    uteis = [p for p in partes if not GENERICO.search(p) and len(p) >= 3]
    org = [p for p in uteis if ORG.search(p)]
    if org:
        return org[-1][:80]
    h = (urlsplit(url).hostname or "").lower().replace("www.", "")
    raiz = h.split(".")[0]
    if uteis and len(uteis[-1]) <= 60:
        return uteis[-1][:80]
    return raiz.replace("-", " ").title()[:80] if raiz else ""


def modalidade(texto: str, fr: str) -> str:
    t = (texto or "")[:4000]
    if fr == "internacional":
        return "internacional"
    if re.search(r"(?i)edital|regulamento|chamada|sele[çc][ãa]o", t):
        return "edital próprio"
    if re.search(r"(?i)doa[çc][ãa]o|doar|cess[ãa]o|voluntariado", t):
        return "doação"
    return "patrocínio"


def nota_rede(titulo: str, texto: str, url: str) -> float:
    """Probabilidade de ser oportunidade real para OSC, pela rede neural (sem modelo: 0,5)."""
    try:
        from .rede_neural import nota
        n = nota({"titulo": titulo, "evidencia": (texto or "")[:600], "url": url, "origem": "Piloto - Espião"})
        return float(n) if n is not None else 0.5
    except Exception:  # noqa: BLE001
        return 0.5


# ── A MISSÃO ───────────────────────────────────────────────────────────────────────────────────────────────────
def missao(ordem: int, buscar=None, ler_pagina=None, conhecida=None, rnd: random.Random | None = None) -> tuple[str, list[dict], str]:
    """Uma busca criativa → lê os resultados → fica só o privado/internacional fora dos motores → candidata ao
    Interceptador (quando é edital/chamada) e empresa nova no campo de empresas."""
    if buscar is None or ler_pagina is None:
        from .piloto_busca import buscar as _b, ler_pagina as _l
        buscar = buscar or _b; ler_pagina = ler_pagina or _l
    if conhecida is None:
        from .skills.cadastro import conhecida as _c
        conhecida = _c
    c = cerebro()
    fam, q = escolher(c, rnd)
    res = buscar(q, maximo=8) or []
    ja_cand = {x.get("url") for x in (_j(CANDIDATAS, {}).get("candidatas") or [])}
    emp_arq = _j(EMPRESAS_ESPIAO, {"uf": "GO", "achados": []})
    ja_emp = {(x.get("empresa") or "").upper() for x in emp_arq.get("achados") or []}
    ach, cand, emps, motivos, notas = [], [], [], {}, []
    for r in res[:6]:
        url = r.get("url") or ""; titulo = str(r.get("titulo") or "")[:160]
        ok, porque = fora_dos_motores(url)
        if not ok:
            motivos[porque.split(" —")[0]] = motivos.get(porque.split(" —")[0], 0) + 1
            continue
        texto = ler_pagina(url, limite=9000) or ""
        base = f"{titulo} {texto[:4000]}"
        if not (OPORT.search(base) and OSC.search(base)):
            motivos["sem sinal de oportunidade para OSC"] = motivos.get("sem sinal de oportunidade para OSC", 0) + 1
            continue
        fr = frente(url, texto, fam); nt = nota_rede(titulo, texto, url); notas.append(nt)
        m = OPORT.search(base); trecho = re.sub(r"\s+", " ", base[max(0, m.start() - 120):m.end() + 160]).strip()
        org = nome_da_organizacao(titulo, url)
        if fr in ("editais_de_empresas", "internacional") and url not in ja_cand:
            cand.append({"url": url, "titulo": titulo or url, "visto_em": f"Espião · {fr}", "enquadramento": "A VERIFICAR",
                         "descoberto_em": date.today().isoformat(), "origem": "Piloto - Espião (privado/internacional)",
                         "frente": fr, "familia": fam, "consulta": q, "nota_rede": round(nt, 3), "organizacao": org})
            ja_cand.add(url)
        nova_emp = bool(org) and not NAO_EMPRESA.search(org) and not conhecida(org) and org.upper() not in ja_emp
        if nova_emp:
            ja_emp.add(org.upper())
            emps.append({"empresa": org, "evento": titulo[:140] or f"{modalidade(texto, fr)} — {org}", "area": _area(base),
                         "fonte": "Piloto - Espião", "tipo_fonte": f"espião · {fr}", "url": url, "trecho": trecho[:300],
                         "em": _agora(), "modalidade": modalidade(texto, fr), "fora_da_lista_de_incentivo": True,
                         "frente": fr, "nota_rede": round(nt, 3), "consulta": q})
        ach.append({"titulo": titulo or org, "url": url, "novo": True, "empresa": org if nova_emp else None, "frente": fr, "nota_rede": round(nt, 3)})
    if cand:
        C = _j(CANDIDATAS, {"candidatas": []}); C["candidatas"] = (C.get("candidatas") or []) + cand; C["em"] = date.today().isoformat(); _w(CANDIDATAS, C)
    if emps:
        emp_arq["achados"] = ((emp_arq.get("achados") or []) + emps)[-3000:]; emp_arq["em"] = _agora()
        emp_arq["regra"] = "empresas e organizações privadas/internacionais descobertas pelo Espião, fora da lista de incentivo fiscal; o motor de patrocínio as agrega ao painel"
        _w(EMPRESAS_ESPIAO, emp_arq)
    # recompensa da família (aprendizado contínuo): achado vale pela nota da rede; empresa nova vale 1
    recompensa = sum(notas) + len(emps)
    f = c["familias"].get(fam) or c["familias"].setdefault(fam, {"a": 1.0, "b": 1.0, "usos": 0, "achados": 0, "empresas": 0, "nota_media": None})
    f["usos"] += 1; f["achados"] += len(ach); f["empresas"] += len(emps)
    f["a"] = round(f["a"] + min(3.0, recompensa), 3); f["b"] = round(f["b"] + (1.0 if not ach else 0.2), 3)
    if notas:
        f["nota_media"] = round(((f["nota_media"] or 0) * (f["usos"] - 1) + sum(notas) / len(notas)) / f["usos"], 3)
    cq = c["consultas"].setdefault(q, {"familia": fam, "usos": 0, "achados": 0, "empresas": 0})
    cq["usos"] += 1; cq["achados"] += len(ach); cq["empresas"] += len(emps)
    if len(c["consultas"]) > 1500:
        c["consultas"] = dict(sorted(c["consultas"].items(), key=lambda kv: -(kv[1]["achados"] * 10 + kv[1]["usos"]))[:1200])
    _w(CEREBRO, c)
    licao = (f"espião · {fam} · '{q[:80]}': {len(res)} resultado(s), {len(ach)} privado/internacional fora dos motores, "
             f"{len(cand)} candidata(s), {len(emps)} empresa(s) nova(s)" + (f" · descartes: {motivos}" if motivos else ""))
    return q, ach, licao


def _area(t: str) -> str:
    try:
        from .patrocinios import classificar_area
        return classificar_area(t)
    except Exception:  # noqa: BLE001
        return "outras"


# ── A CADA 100 VOOS: AVALIAÇÃO E EVOLUÇÃO COM A REDE NEURAL ────────────────────────────────────────────────────
def inicio_do_voo() -> dict:
    c = cerebro(); c["voos"] += 1; c["voos_desde_avaliacao"] += 1
    out = {"voos": c["voos"], "desde_avaliacao": c["voos_desde_avaliacao"]}
    _w(CEREBRO, c)
    if c["voos_desde_avaliacao"] >= CICLO_VOOS:
        out["avaliacao"] = avaliar_e_evoluir()
    else:
        publicar(c)                                   # o quadro do Espião no painel acompanha voo a voo
    return out


def avaliar_e_evoluir(rnd: random.Random | None = None) -> dict:
    """Mede cada família (achados, empresas, nota média da rede neural), reforça as boas, aposenta consultas que
    falharam 3 vezes, e cria MUTAÇÕES das melhores consultas (troca setor, público, região ou financiador)."""
    rnd = rnd or random.Random()
    c = cerebro()
    tab = []
    for f, v in c["familias"].items():
        rend = (v["achados"] + 2 * v["empresas"]) / v["usos"] if v["usos"] else None
        tab.append({"familia": f, "usos": v["usos"], "achados": v["achados"], "empresas": v["empresas"], "nota_media_rede": v["nota_media"],
                    "rendimento": round(rend, 3) if rend is not None else None})
    tab.sort(key=lambda x: -(x["rendimento"] or 0))
    # reforço: as 3 melhores ganham peso; as que nada renderam com 10+ usos perdem
    for i, t in enumerate(tab):
        v = c["familias"][t["familia"]]
        if i < 3 and t["rendimento"]:
            v["a"] = round(v["a"] + 2.0, 3)
        elif (t["usos"] or 0) >= 10 and not t["achados"]:
            v["b"] = round(v["b"] + 3.0, 3)
    aposentadas = [q for q, v in c["consultas"].items() if v.get("usos", 0) >= 3 and not v.get("achados")]
    boas = sorted(((q, v) for q, v in c["consultas"].items() if v.get("achados")), key=lambda kv: -(kv[1]["achados"] + 2 * kv[1]["empresas"]))[:10]
    trocas = [SETORES, PUBLICOS, REGIOES, INTERNACIONAIS, APOIOS]
    mut = []
    for q, _v in boas:
        for lista in trocas:
            hit = next((x for x in lista if x in q), None)
            if hit:
                novo = q.replace(hit, rnd.choice([x for x in lista if x != hit]))
                if novo not in c["consultas"]:
                    mut.append(novo)
    c["mutacoes"] = list(dict.fromkeys(mut + (c.get("mutacoes") or [])))[:60]
    av = {"em": _agora(), "voo": c["voos"], "familias": tab, "consultas_aposentadas": len(aposentadas),
          "mutacoes_criadas": len(mut), "melhores_consultas": [q for q, _ in boas[:5]],
          "achados_no_ciclo": sum(t["achados"] for t in tab), "empresas_no_ciclo": sum(t["empresas"] for t in tab)}
    c["avaliacoes"] = (c["avaliacoes"] + [av])[-30:]
    c["voos_desde_avaliacao"] = 0
    _w(CEREBRO, c)
    publicar(c)
    return av


def publicar(c: dict | None = None) -> dict:
    c = c or cerebro()
    E = _j(EMPRESAS_ESPIAO, {}).get("achados") or []
    C = [x for x in (_j(CANDIDATAS, {}).get("candidatas") or []) if str(x.get("origem") or "").startswith("Piloto - Espião (privado")]
    out = {"em": _agora(), "regra": (__doc__ or "").split("\n\n")[0], "voos": c["voos"], "proxima_avaliacao_em_voos": CICLO_VOOS - c["voos_desde_avaliacao"],
           "familias": c["familias"], "avaliacoes": c["avaliacoes"][-10:],
           "empresas_novas": len(E), "empresas_por_modalidade": _conta(E, "modalidade"), "empresas_por_frente": _conta(E, "frente"),
           "candidatas_privadas_internacionais": len(C), "candidatas_por_frente": _conta(C, "frente"),
           "ultimas_empresas": [{k: x.get(k) for k in ("empresa", "modalidade", "frente", "url", "nota_rede", "em")} for x in E[-20:]]}
    _w(AVALIACAO, out)
    return out


def _conta(L, k):
    d = {}
    for x in L:
        d[str(x.get(k))] = d.get(str(x.get(k)), 0) + 1
    return d
