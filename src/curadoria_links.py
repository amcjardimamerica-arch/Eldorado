"""CURADORIA DO LINK OFICIAL (titular, 15/10/2026) — dois links por oportunidade e o trecho exato dela.

Cada oportunidade aberta passa a ter:
  · LINK DE ACESSO — onde o motor a encontrou (notícia, agregador, diário, portal);
  · LINK OFICIAL   — onde o órgão ou financiador a publicou, usado pelo sistema para análise e validação interna.
    Os dois só são o mesmo quando a oportunidade foi captada direto no local oficial de publicação;
  · TRECHO         — exatamente o texto da oportunidade, com a fonte do trecho: do documento oficial (com página) ou,
    enquanto não comprovado, do link de acesso.

O link oficial precisa oferecer todas as informações e atualizações da oportunidade; por isso passa por curadoria com
critérios objetivos, todos verificáveis:
  C1 domínio oficial       órgão público (.gov.br, .leg.br, .jus.br, .mp.br, .def.br, .tc.br), arquivo do órgão no PNCP,
                           plataforma de publicação do próprio emissor (Prosas, Mapas Culturais…) ou site do financiador;
  C2 não é agregador       nem replicador de notícias ou editais;
  C3 acessível             não está fora da fila de retentativa (5 erros iguais);
  C4 contém a oportunidade o Cartório extraiu ao menos um item desse documento;
  C5 informações completas leitura total no Cartório (12 de 12 comprovados ou dispensados);
  C6 atualizado            conferido pelo Cartório nos últimos 7 dias (retificações e prorrogações).
Resultado: APROVADO (C1–C5; C6 vencido só alerta) · EM CURADORIA (C1–C3 ok, falta C4 ou C5) · REPROVADO (falha C1, C2 ou
C3: o link deixa de valer como oficial e a oportunidade volta à busca da fonte oficial) · SEM LINK OFICIAL (a buscar).
Saídas: estado/curadoria_links.json e docs/dados/curadoria_links.json
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "dados/oportunidades/repositorio_unico.json"
CERT = ROOT / "estado/cartorio/certidoes.json"
ESTADO = ROOT / "estado/curadoria_links.json"
PAINEL = ROOT / "docs/dados/curadoria_links.json"
INSTITUCIONAL = re.compile(r"\.edu\.br$|\.ufg?\.br$|\.if\w+\.edu\.br$")   # 15/10: universidades e institutos federais
PUBLICO = re.compile(r"\.(gov|leg|jus|mp|def|tc)\.br$|^(gov|leg|jus|mp)\.br$|\.gov(\.[a-z]{2})?$|\.gob\.[a-z]{2}$|\.gouv\.[a-z]{2}$|\.europa\.eu$|\.int$")
AGREGADORES = ("editaisdobrasil", "editais.net", "captadores", "capitaai", "farolcultural", "observatorio3setor", "filantropia.ong",
               "portaldoterceirosetor", "licitario", "conlicitacao", "effecti", "queridodiario", "editaldeculturaeesporte")
PNCP_ARQUIVO = re.compile(r"pncp\.gov\.br/(?:pncp-)?api/.*/arquivos/\d+", re.I)
STOP = {"de", "da", "do", "das", "dos", "e", "para", "the", "of", "and", "fundacao", "instituto", "secretaria", "municipal", "estado"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _dom(u: str) -> str:
    return (urlsplit(str(u or "")).hostname or "").lower().removeprefix("www.")


def classe(url: str, orgao: str = "") -> str:
    """órgão público · arquivo do órgão no PNCP · plataforma do emissor · site do financiador · agregador · não identificado"""
    from .fonte_oficial import EMISSOR_PROPRIO, eh_replicador
    d = _dom(url)
    if not d:
        return "sem link"
    if PNCP_ARQUIVO.search(url or ""):
        return "arquivo do órgão no PNCP"
    if any(a in d for a in AGREGADORES) or (eh_replicador(url) and "pncp.gov.br" not in d):
        return "agregador ou replicador"
    if "pncp.gov.br" in d:
        return "página do PNCP (não é o documento)"
    if re.search(r"planalto\.gov\.br/ccivil|normas\.leg\.br|leisestaduais|/legislacao/(?!diariooficial)|legislacao\.\w+\.gov\.br", str(url), re.I):
        return "texto de lei (não é a oportunidade)"               # 15/10 (ciclo 4): a LC 195 virou "link oficial"
    if any(e in d or e in str(url) for e in EMISSOR_PROPRIO):
        return "plataforma de publicação do emissor"
    caminho = (urlsplit(str(url)).path or "/").strip("/")
    if (not caminho and not urlsplit(str(url)).query) or \
            (d == "gov.br" and len([x for x in caminho.split("/") if x]) <= 1):   # gov.br/<órgão> é a página inicial do órgão
        return "página inicial genérica (não é a oportunidade)"     # 15/10: home do órgão não prova a oportunidade
    if PUBLICO.search(d):
        return "órgão público"
    if INSTITUCIONAL.search(d):
        return "instituição pública ou de ensino"
    plano = d.replace("-", "").replace(".", "")
    toks = {t for t in re.findall(r"[a-z0-9]{4,}", _sem(orgao)) if t not in STOP}
    junto = re.sub(r"[^a-z0-9]", "", _sem(orgao))                     # 15/10: "Instituto ACP" → institutoacp
    sigla = [t for t in re.findall(r"\b[a-z0-9]{2,4}\b", _sem(orgao)) if t not in STOP]
    if (toks and any(t in plano for t in toks)) or (len(junto) >= 6 and junto in plano) or any(len(x) >= 3 and x in plano for x in sigla):
        return "site do financiador"
    return "não identificado como oficial"


def _sem(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


OFICIAIS = ("órgão público", "arquivo do órgão no PNCP", "plataforma de publicação do emissor", "site do financiador",
            "instituição pública ou de ensino")


def curar(r: dict, cert: dict | None, agora: datetime) -> dict:
    from . import fila_retentativa as FR
    acesso = r.get("url")
    oficial = (cert or {}).get("link_oficial") or r.get("link_oficial")
    if (not oficial or classe(oficial, r.get("orgao")) not in OFICIAIS) and classe(acesso, r.get("orgao")) in OFICIAIS:
        oficial = acesso            # captada direto no local oficial (15/10: também quando o link proposto não vale)
    _quem = r.get("orgao") or r.get("titulo")                   # 15/10 (ciclo 7): sem órgão, o título identifica o financiador
    cl = classe(oficial, _quem) if oficial else "sem link"
    docs_cert = {str(v.get("documento") or "") for v in ((cert or {}).get("itens") or {}).values() if isinstance(v, dict)}
    em = str((cert or {}).get("em") or "")
    C = {"C1 domínio oficial": cl in OFICIAIS,
         "C2 não é agregador": cl != "agregador ou replicador" and bool(oficial),
         "C3 acessível": bool(oficial) and not FR.fora_da_fila(oficial),
         "C4 contém a oportunidade": bool(oficial) and (oficial in docs_cert or (bool(docs_cert) and (cert or {}).get("link_oficial") == oficial)),
         "C5 informações completas": bool(cert) and (cert or {}).get("leitura", "total" if not (cert or {}).get("ainda_faltam") else "parcial") == "total"
                                     and not (cert or {}).get("ainda_faltam") and bool((cert or {}).get("link_oficial")),
         "C6 atualizado (7 dias)": bool(em) and em >= (agora - timedelta(days=7)).isoformat()}
    if not oficial:
        status = "sem link oficial"
    elif not (C["C1 domínio oficial"] and C["C2 não é agregador"] and C["C3 acessível"]):
        status = "reprovado"
    elif C["C4 contém a oportunidade"] and C["C5 informações completas"]:
        status = "aprovado"
    else:
        status = "em curadoria"
    obj = ((cert or {}).get("itens") or {}).get("Objeto") or {}
    if obj.get("trecho"):
        trecho = {"texto": obj["trecho"], "fonte": "documento oficial", "documento": obj.get("documento"), "pagina": obj.get("pagina")}
    else:
        o2 = (r.get("itens") or {}).get("Objeto") or {}
        trecho = {"texto": o2.get("trecho") or o2.get("valor"), "fonte": "link de acesso (ainda não comprovado no documento oficial)",
                  "documento": acesso, "pagina": None}
    return {"id": r.get("id"), "titulo": str(r.get("titulo") or "")[:200], "orgao": r.get("orgao"),
            "link_acesso": acesso, "link_oficial": oficial if status != "reprovado" else None, "link_oficial_proposto": oficial,
            "classe_do_link_oficial": cl, "mesmo_link": bool(oficial) and oficial == acesso and status != "reprovado",
            "captada_direto_na_fonte_oficial": bool(oficial) and oficial == acesso and cl in OFICIAIS,
            "curadoria": status, "criterios": C, "falham": [k for k, v in C.items() if not v],
            "proximo_passo": {"sem link oficial": "buscar a fonte oficial (resolvedor e Cartório)", "reprovado": "buscar a fonte oficial (o link proposto não é oficial ou não abre)",
                              "em curadoria": "Cartório: ler o documento oficial até 12 de 12",
                              "aprovado": "validar e seguir ao Farol"}[status],
            "trecho": trecho, "conferido_em": em or None}


def run() -> dict:
    agora = datetime.now(timezone.utc).replace(microsecond=0)
    regs = (_j(REPO, {}) or {}).get("registros") or []
    certs = (_j(CERT, {}) or {}).get("certidoes") or {}
    por_id: dict = {}
    for k, c in certs.items():
        por_id[str(k).split(":", 1)[-1]] = c
    out = []
    for r in regs:
        if r.get("arquivada") or r.get("estado") in ("arquivada", "encerrada", "descartada", "fechada"):   # 16/10: "fechada" faltava
            continue
        c = por_id.get(r.get("id")) or next((por_id[i] for i in (r.get("ids_origem") or []) if i in por_id), None)
        out.append(curar(r, c, agora))
    from collections import Counter
    res = {"em": agora.isoformat(), "regra": __doc__.split("Saídas:")[0].strip(), "abertas": len(out),
           "curadoria": dict(Counter(x["curadoria"] for x in out)),
           "classe_do_link_oficial": dict(Counter(x["classe_do_link_oficial"] for x in out)),
           "mesmo_link_e_oficial": sum(1 for x in out if x["captada_direto_na_fonte_oficial"]),
           "mesmo_link_reprovado": sum(1 for x in out if x["link_acesso"] == x["link_oficial_proposto"] and x["curadoria"] == "reprovado"),
           "trecho_do_documento_oficial": sum(1 for x in out if x["trecho"]["fonte"] == "documento oficial"),
           "itens": out}
    for p in (ESTADO, PAINEL):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, ensure_ascii=False, indent=1 if p == ESTADO else None), encoding="utf-8")
    return {k: v for k, v in res.items() if k not in ("itens", "regra")}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
