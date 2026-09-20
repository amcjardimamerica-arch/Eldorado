"""EMPRESAS → ROTAS DE BUSCA.

Os motores 27 (Incentivos Fiscais) e 28 (Patrocínio Privado) produzem EMPRESAS, não
editais. Este módulo transforma cada empresa mapeada em ROTAS onde ela pode divulgar
oportunidade — e entrega essas rotas ao motor de descoberta de editais de empresas
(plat-empresas-editais-incentivados) e ao catálogo de fontes.

Onde uma empresa divulga o que financia (o mesmo recurso, várias portas):
  1. site institucional — /sustentabilidade, /responsabilidade-social, /instituto,
     /editais, /projetos-incentivados, /investimento-social (padrões observados)
  2. instituto ou fundação com nome próprio (Instituto X, Fundação Y) — site próprio
  3. portais do terceiro setor onde anuncia (Observatório, ABCR, GIFE, Prosas)
  4. Salic (projetos que ela já incentivou → padrão de destinação)
  5. redes sociais institucionais — PISTA, nunca fonte

Saída: config/rotas_empresas.json — reaplicada ao catálogo de fontes a cada geração.
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

BASE = ROOT / "dados/empresas/base_empresas.jsonl.gz"
PATROC = ROOT / "dados/empresas/go/patrocinios.json"
SAIDA = ROOT / "config/rotas_empresas.json"

# caminhos onde as empresas costumam publicar o que financiam (observado em Renner, Porto Itapoá, BNDES, Maria Emília)
CAMINHOS_RSE = ["/sustentabilidade", "/responsabilidade-social", "/instituto", "/fundacao", "/editais",
                "/projetos-incentivados", "/investimento-social", "/esg", "/doacoes", "/patrocinio", "/patrocinios"]
LEXICO_EMPRESA = ["edital", "seleção de projetos", "projetos incentivados", "investimento social", "responsabilidade social",
                  "patrocínio", "doação", "instituto", "fundação", "Lei Rouanet", "FIA", "Fundo do Idoso",
                  "Lei de Incentivo ao Esporte", "PRONAS", "PRONON", "inscrições", "organizações sem fins lucrativos"]


def _dominio(e: dict) -> str | None:
    s = e.get("site")
    if isinstance(s, dict):
        return s.get("dominio")
    if isinstance(s, str) and "." in s:
        return urlsplit(s if s.startswith("http") else "https://" + s).hostname
    return None


def _slug(nome: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", nome or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(s/?a|ltda|s\.a\.|eireli|me|epp|cia|companhia|do brasil|industria|comercio|distribuidora|de|da|do|e)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s[:24]


def _candidatos_dominio(nome: str) -> list[str]:
    """Quando a base não tem o site, o motor testa os domínios mais prováveis e marca 'a confirmar'."""
    sl = _slug(nome)
    return [f"https://www.{sl}.com.br", f"https://{sl}.com.br", f"https://www.{sl}.com"] if len(sl) >= 4 else []


def _nome_instituto(e: dict) -> str | None:
    """'INSTITUTO X' ou 'FUNDAÇÃO Y' que a empresa já declarou (parcerias, cadastro)."""
    alvo = " ".join(str(x) for x in [e.get("nome"), (e.get("cadastro") or {}).get("nome_fantasia"), *(e.get("motivos") or [])])
    m = re.search(r"(Instituto|Funda[çc][ãa]o)\s+[A-ZÀ-Ú][\w\s]{2,40}", alvo)
    return m.group(0).strip() if m else None


def montar() -> dict:
    base = [json.loads(l) for l in gzip.open(BASE, "rt", encoding="utf-8") if l.strip()] if BASE.exists() else []
    pat = load_json(PATROC) if PATROC.exists() else {}
    rotas = []
    for e in sorted(base, key=lambda x: -(x.get("score") or 0)):
        dom = _dominio(e)
        nome = (e.get("cadastro") or {}).get("nome_fantasia") or e.get("nome")
        r = {"empresa": nome, "cnpj": e.get("cnpj"), "score": e.get("score"), "classe": e.get("classe"),
             "origem": "motor 27 — incentivos fiscais", "rotas": []}
        if dom:
            r["rotas"].append({"tipo": "site_institucional", "url": f"https://{dom}", "prioridade": 1})
            for c in CAMINHOS_RSE[:6]:
                r["rotas"].append({"tipo": "pagina_rse", "url": f"https://{dom}{c}", "prioridade": 2})
        if not dom:
            # descoberta do site: busca pública (HTML, sem API) + domínios candidatos a confirmar
            r["rotas"].append({"tipo": "descobrir_site", "url": f"https://html.duckduckgo.com/html/?q={re.sub(r'\s+','+',nome or '')}+site+oficial", "prioridade": 1, "nota": "o sensor lê a página de busca e a camada 1 escolhe o link do site oficial"})
            for u in _candidatos_dominio(nome)[:2]:
                r["rotas"].append({"tipo": "dominio_candidato", "url": u, "prioridade": 2, "nota": "a confirmar na leitura"})
        inst = _nome_instituto(e)
        if inst:
            r["instituto"] = inst
            r["rotas"].append({"tipo": "instituto_proprio", "busca": f"{inst} edital", "prioridade": 1})
        r["rotas"].append({"tipo": "vetor_terceiro_setor", "busca": f"{nome} edital OR seleção de projetos", "onde": ["observatorio3setor.org.br", "captadores.org.br", "gife.org.br", "prosas.com.br"], "prioridade": 3})
        r["rotas"].append({"tipo": "salic_historico", "url": f"https://salic.cultura.gov.br/", "nota": "projetos já incentivados pela empresa indicam o padrão de destinação", "prioridade": 4})
        r["rotas"].append({"tipo": "pista_redes", "busca": f"{nome} instituto edital", "nota": "PISTA — nunca fonte", "prioridade": 5})
        r["sem_site"] = not dom
        rotas.append(r)
    # patrocinadores observados pelo motor 28 (privado)
    for a in (pat.get("achados") or []):
        nome = a.get("empresa") or a.get("nome")
        if not nome or any(x["empresa"] == nome for x in rotas):
            continue
        rotas.append({"empresa": nome, "origem": "motor 28 — patrocínio privado observado", "evento": (a.get("evento") or a.get("trecho") or "")[:100],
                      "rotas": [{"tipo": "vetor_terceiro_setor", "busca": f"{nome} patrocínio OR edital", "prioridade": 3},
                                {"tipo": "imprensa", "url": a.get("url") or a.get("fonte"), "nota": "onde o patrocínio foi visto", "prioridade": 4}]})
    res = {"versao": 1, "gerado_em": now_iso(), "regra": "toda empresa mapeada pelos motores 27/28 vira ROTAS de busca de oportunidade (site, página de RSE, instituto próprio, portais do terceiro setor, Salic); as rotas alimentam o motor plat-empresas-editais-incentivados e o catálogo de fontes",
           "lexico": LEXICO_EMPRESA, "total_empresas": len(rotas), "com_site": sum(1 for r in rotas if not r.get("sem_site", True)),
           "empresas": rotas}
    write_json(SAIDA, res)
    return {"total_empresas": res["total_empresas"], "com_site": res["com_site"], "rotas": sum(len(r["rotas"]) for r in rotas)}


def rotas_para_sensor(limite: int = 40) -> list[str]:
    """URLs de site/RSE das empresas de maior pontuação, para o sensor de editais de empresas."""
    if not SAIDA.exists():
        return []
    d = load_json(SAIDA)
    urls = []
    for r in d.get("empresas", []):
        for x in r["rotas"]:
            if x.get("url") and x["tipo"] in ("site_institucional", "pagina_rse", "descobrir_site", "dominio_candidato") and x["prioridade"] <= 2:
                urls.append(x["url"])
    return urls[:limite]


if __name__ == "__main__":
    print(json.dumps(montar(), ensure_ascii=False, indent=2))
