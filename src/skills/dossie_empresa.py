"""SKILL · DOSSIÊ INVESTIGATIVO DE EMPRESA (titular, 29/09) — Interceptador, empresas do CADASTRO.

Para cada empresa já conhecida (Goiás primeiro): COMPOSIÇÃO (razão social, CNAE, porte, sócios/administradores),
CONTATOS (telefone, e-mail, endereço, site), PROJETOS em que já participou (incentivos verificados em fonte oficial:
Rouanet, Goyazes, Esporte…, com anos e valores), e um RESUMO INVESTIGATIVO de atuação no terceiro setor — lido do
site da empresa (instituto, responsabilidade social, sustentabilidade) pelo modelo local, sem inventar.
Fontes: BrasilAPI (dados abertos da Receita), base de incentivos do sistema, site da própria empresa.
Saída: estado/interceptador/dossies/<cnpj>.json e o índice docs/dados/dossies_empresas.json (para o painel).
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "estado/interceptador/dossies"
IDX = ROOT / "docs/dados/dossies_empresas.json"
UA = {"User-Agent": "Mozilla/5.0 (Eldorado; associacao sem fins lucrativos; pesquisa de apoiadores)"}
PAGINAS_SOCIAIS = ["", "/instituto", "/responsabilidade-social", "/sustentabilidade", "/social", "/fundacao", "/esg", "/investimento-social"]


def _get(url: str, t: int = 25) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
            return r.read(2_000_000).decode("utf-8", "ignore")
    except Exception:
        return ""


def _texto(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def receita(cnpj: str) -> dict:
    c = re.sub(r"\D", "", cnpj or "")
    if len(c) != 14:
        return {}
    try:
        d = json.loads(_get(f"https://brasilapi.com.br/api/cnpj/v1/{c}") or "{}")
    except Exception:
        return {}
    if not d.get("cnpj"):
        return {}
    return {"razao_social": d.get("razao_social"), "nome_fantasia": d.get("nome_fantasia"), "situacao": d.get("descricao_situacao_cadastral"),
            "abertura": d.get("data_inicio_atividade"), "cnae": f"{d.get('cnae_fiscal')} — {d.get('cnae_fiscal_descricao')}", "porte": d.get("porte"),
            "natureza": d.get("natureza_juridica"), "capital_social": d.get("capital_social"),
            "endereco": ", ".join(str(x) for x in (d.get("logradouro"), d.get("numero"), d.get("bairro"), d.get("municipio"), d.get("uf"), d.get("cep")) if x),
            "telefones": [t for t in (d.get("ddd_telefone_1"), d.get("ddd_telefone_2")) if t], "email": d.get("email"),
            "socios": [{"nome": s.get("nome_socio"), "qualificacao": s.get("qualificacao_socio"), "desde": s.get("data_entrada_sociedade")} for s in (d.get("qsa") or [])][:12]}


def projetos(cnpj: str, nome: str) -> list[dict]:
    """Participações verificadas em mecanismos de incentivo (fonte oficial), da base do sistema."""
    try:
        base = json.loads((ROOT / "biblioteca_alexandria/empresas/incentivos_verificados.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    c8 = re.sub(r"\D", "", cnpj or "")[:8]
    for e in base.get("empresas") or []:
        if (c8 and re.sub(r"\D", "", str(e.get("cnpj") or ""))[:8] == c8) or (nome and str(e.get("nome", "")).lower() == nome.lower()):
            out = []
            for mec, v in (e.get("mecanismos") or e.get("incentivos") or {}).items():
                if isinstance(v, dict):
                    out.append({"mecanismo": mec, "anos": v.get("anos"), "valor": v.get("valor") or v.get("total"), "fonte": v.get("fonte")})
            return out
    return []


def site_da_empresa(emp: dict, rf: dict) -> str | None:
    s = emp.get("site") or (emp.get("cadastro") or {}).get("site")
    if s:
        return s if s.startswith("http") else "https://" + s
    em = str(rf.get("email") or "")
    dom = em.split("@")[-1].lower() if "@" in em else ""
    if dom and not re.search(r"gmail|hotmail|yahoo|outlook|uol|bol|terra|live|icloud|contab|escritorio", dom):
        return "https://" + dom
    # 01/10: os 80 primeiros dossiês ficaram sem site — procura pelo nome e aceita só o domínio que contém o nome
    try:
        from ..piloto_busca import buscar
        from ..sites_oficiais import e_republicador
        nome = str(emp.get("nome") or rf.get("nome_fantasia") or rf.get("razao_social") or "")
        toks = [w for w in re.findall(r"[a-z]{4,}", nome.lower()) if w not in {"industria", "comercio", "servicos", "brasil", "ltda", "participacoes", "holding", "goias"}]
        for r in buscar(f'"{nome}" site oficial', 6) or []:
            h = re.sub(r"^www\.", "", (re.sub(r"^https?://", "", r.get("url") or "").split("/")[0]).lower())
            if h and not e_republicador(r["url"]) and not re.search(r"facebook|instagram|linkedin|youtube|wikipedia|reclameaqui|jusbrasil|econodata|cnpj", h) \
               and any(t in h.replace("-", "") for t in toks[:3]):
                return "https://" + h
    except Exception:
        pass
    return None


PROMPT = """Você lê textos do SITE de uma empresa e escreve um RESUMO INVESTIGATIVO da atuação dela no TERCEIRO SETOR
(instituto, fundação, programa social, patrocínio, doação, voluntariado, leis de incentivo). Use SÓ o que está no
texto; se não houver nada, diga isso. Responda SOMENTE com JSON:
{"atua_no_terceiro_setor": true|false, "resumo": "até 90 palavras", "programas": ["..."], "causas": ["..."],
 "como_apoia": ["incentivo fiscal"|"patrocínio"|"doação"|"edital próprio"|"voluntariado"], "contato_social": "e-mail/página ou vazio"}"""


def dossie(emp: dict, ia=None) -> dict:
    cnpj = re.sub(r"\D", "", str(emp.get("cnpj") or ""))
    rf = receita(cnpj)
    pj = projetos(cnpj, emp.get("nome") or "")
    site = site_da_empresa(emp, rf)
    textos = []
    if site:
        for p in PAGINAS_SOCIAIS:
            t = _texto(_get(site.rstrip("/") + p))
            if len(t) > 300 and not any(t[:200] == x[:200] for x in textos):
                textos.append(t[:4000])
            if len(textos) >= 3:
                break
    resumo = {}
    if ia and textos:
        try:
            r = ia.perguntar(PROMPT + "\n\nTEXTOS DO SITE:\n" + "\n\n---\n\n".join(textos)[:9000])
            resumo = r if isinstance(r, dict) else {}
        except Exception:
            resumo = {}
    if not resumo:
        mec = ", ".join(sorted({p["mecanismo"] for p in pj})) or "nenhum mecanismo verificado"
        resumo = {"atua_no_terceiro_setor": bool(pj), "resumo": f"Participação verificada em incentivos: {mec}." + (" Site sem página social legível." if site and not textos else ""),
                  "programas": [], "causas": [], "como_apoia": ["incentivo fiscal"] if pj else [], "contato_social": rf.get("email") or ""}
    d = {"cnpj": cnpj, "nome": emp.get("nome"), "uf": emp.get("uf") or rf.get("endereco", "")[-11:-9], "em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "composicao": {k: rf.get(k) for k in ("razao_social", "nome_fantasia", "situacao", "abertura", "cnae", "porte", "natureza", "capital_social", "socios")} if rf else {},
         "contatos": {"telefones": rf.get("telefones"), "email": rf.get("email"), "endereco": rf.get("endereco"), "site": site} if rf or site else {},
         "projetos": pj, "resumo_investigativo": resumo, "paginas_lidas": len(textos),
         "completude": sum(bool(x) for x in (rf, rf.get("socios") if rf else None, (rf or {}).get("telefones") or (rf or {}).get("email"), pj, textos, resumo.get("resumo")))}
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR / f"{cnpj or re.sub(r'[^a-z0-9]', '', str(emp.get('nome','')).lower())[:30]}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    indexar()
    return d


def indexar() -> None:
    itens = []
    for f in sorted(DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        itens.append({"cnpj": d.get("cnpj"), "nome": d.get("nome"), "uf": d.get("uf"), "em": d.get("em"), "completude": d.get("completude"),
                      "socios": ", ".join(f"{s.get('nome')} ({s.get('qualificacao')})" for s in ((d.get("composicao") or {}).get("socios") or [])[:8]), "contatos": d.get("contatos"), "projetos": d.get("projetos"),
                      "resumo": (d.get("resumo_investigativo") or {}).get("resumo"), "atua": (d.get("resumo_investigativo") or {}).get("atua_no_terceiro_setor")})
    IDX.write_text(json.dumps({"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "total": len(itens), "itens": itens}, ensure_ascii=False), encoding="utf-8")


def empresas_goias_sem_dossie() -> list[dict]:
    feitos = {f.stem for f in DIR.glob("*.json")} if DIR.exists() else set()
    out, vistos = [], set()
    for f in ("biblioteca_alexandria/empresas/ranking_destinacao_tributaria.json", "biblioteca_alexandria/empresas/ranking_patrocinio_privado.json"):
        try:
            for e in json.loads((ROOT / f).read_text(encoding="utf-8")).get("empresas", []):
                uf = str((e.get("cadastro") or {}).get("uf") or e.get("uf") or "")
                c = re.sub(r"\D", "", str(e.get("cnpj") or ""))
                if (uf == "GO" or e.get("icms_goias") or e.get("goias")) and c and c not in feitos and c not in vistos:
                    vistos.add(c); out.append({**e, "cnpj": c, "uf": "GO"})
        except Exception:
            pass
    out.sort(key=lambda e: -float(e.get("pontos") or e.get("pontuacao") or 0))
    return out
