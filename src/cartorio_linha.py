"""LINHA DE PRODUÇÃO DO CARTÓRIO (titular, 09/10/2026).

Balcões por SELO — cada oportunidade está numa etapa e, ao subir de selo, passa sozinha para a seguinte:
  sem_estrela → bronze   foco: site oficial + Objeto, Prazo de inscrição e Território
  bronze      → prata    foco: Valor e Requisitos
  prata       → ouro     foco: os demais itens (resultado, recurso, anexos, destinação...) e as dispensas
(estrela: criterio_selos.nivel do checklist; livro: selo da esteira.)

DEZ ABORDAGENS, uma diferente a cada tentativa, no máximo 10 por oportunidade. Cada balcão as percorre numa ordem
afiada para o seu foco; abordagem sem material para aquela oportunidade é pulada (não gasta tentativa). Os itens se
ACUMULAM entre as tentativas (a certidão nunca perde o que já achou).
   1 documento na mão          o que o motor entregou (arquivo, link oficial) e os documentos ligados direto a ele
   2 anexos completos           todos os arquivos do processo (PNCP) e todos os documentos da página oficial
   3 página oficial e citados   navega mais fundo no site do órgão (até 8 páginas/documentos a mais) e nos embutidos
   4 biblioteca de sites        sites oficiais JÁ CONHECIDOS do órgão/município (livros, certidões, catálogo)
   5 mídia do WordPress         busca o número do edital na biblioteca de mídia do site oficial
   6 mapa do site               sitemap.xml do domínio oficial, filtrado por edital/chamamento e número
   7 releitura com gabarito     relê os documentos oficiais já lidos com o gabarito do órgão atualizado
   8 ponte do titular           refaz pela ponte (IP do Brasil) o que o site recusou à nuvem
   9 leitura profunda           até 150 páginas e tabelas; edição inteira localizada pelo órgão
  10 busca no domínio           busca restrita ao domínio oficial pelo número e pelo título
Depois da 10ª: encaminhada de vez ao Interceptador (e ao Chrome, se o robots.txt proíbe).
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from . import cartorio_leitura as L

ROOT = Path(__file__).resolve().parents[1]
BIBLIOTECA = ROOT / "estado/cartorio/biblioteca_sites.json"
MAX_TENTATIVAS = 10

ABORDAGENS = {1: "documento na mão", 2: "anexos completos", 3: "página oficial e citados", 4: "biblioteca de sites",
              5: "mídia do WordPress", 6: "mapa do site", 7: "releitura com gabarito", 8: "ponte do titular",
              9: "leitura profunda", 10: "busca no domínio"}
ORDEM = {"sem_estrela": [1, 4, 3, 10, 6, 5, 8, 2, 9, 7],
         "bronze": [1, 2, 3, 9, 7, 4, 10, 6, 5, 8],
         "prata": [1, 2, 9, 7, 3, 4, 10, 6, 5, 8]}
FOCO = {"sem_estrela": ["Objeto", "Prazo de inscrição", "Território"],
        "bronze": ["Valor", "Requisitos"],
        "prata": ["Resultado", "Prazo de recurso", "Órgão / financiador", "Esfera", "Anexos", "Destinação", "Área de atuação"]}
NOME_BALCAO = {"sem_estrela": "Sem estrela → bronze", "bronze": "Bronze → prata", "prata": "Prata → ouro"}


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")


# ── ESTÁGIO (balcão de selo) ───────────────────────────────────────────────────────────────────────────────────
def estagio(op: dict) -> str | None:
    """sem_estrela · bronze · prata — ou None quando já é ouro (sai da linha)."""
    if op.get("_tipo") == "livro":
        s = op.get("selo")
        return None if s == "ouro" else ("prata" if s == "prata" else "bronze" if s == "bronze" and not op.get("_sem_site") else "sem_estrela")
    from .criterio_selos import nivel
    n = nivel(op.get("checklist") or {})
    return {None: "sem_estrela", "bronze": "bronze", "prata": "prata"}.get(n)


def proxima_abordagem(est: str, usadas: list[int]) -> list[int]:
    """As abordagens que ainda restam, na ordem afiada do balcão."""
    return [n for n in ORDEM.get(est or "sem_estrela", ORDEM["sem_estrela"]) if n not in usadas]


# ── BIBLIOTECA DE SITES OFICIAIS JÁ CONHECIDOS ─────────────────────────────────────────────────────────────────
def chave_municipio(texto: str, uf: str = "") -> str | None:
    t = _sem_acento(texto)
    m = re.search(r"diario oficial d[eo] ([a-z' -]+?) \(([a-z]{2})\)", t) or \
        re.search(r"(?:prefeitura(?: municipal)? d[eoa]|municipio d[eoa]|camara municipal d[eoa]) ([a-z' -]{3,40}?)(?:\s*[-/(,]\s*([a-z]{2})\b|$|\s+—|\s+-)", t)
    if not m:
        return None
    cid = re.sub(r"\s+", " ", m.group(1)).strip()
    u = (m.group(2) if m.lastindex and m.lastindex >= 2 and m.group(2) else _sem_acento(uf))[:2]
    return f"municipio:{cid}-{u}" if cid and u else None


def chaves(op: dict) -> list[str]:
    ks = []
    for u in (op.get("link_oficial"), op.get("url"), op.get("url_documento")):
        ks += L.chaves_orgao(str(u or ""), "")
    ks += L.chaves_orgao("", str(op.get("orgao") or ""))
    for t in (op.get("titulo"), op.get("orgao")):
        k = chave_municipio(str(t or ""), str(op.get("uf") or ""))
        if k:
            ks.append(k)
    return [k for k in dict.fromkeys(ks) if k]


def construir_biblioteca(catalogo: dict, certidoes: dict) -> dict:
    """Índice órgão/município → sites oficiais conhecidos, de tudo o que o sistema já confirmou."""
    bib: dict = {}

    def pôr(ks, url, origem):
        if not (url and str(url).startswith("http") and L.regua(url)[0]):
            return
        for k in ks:
            e = bib.setdefault(k, {"urls": [], "origens": []})
            if url not in e["urls"]:
                e["urls"].append(url); e["origens"].append(origem)
                e["urls"] = e["urls"][-8:]; e["origens"] = e["origens"][-8:]

    for x in (catalogo.get("motores") or []):
        base = {"orgao": x.get("orgao"), "titulo": x.get("programa"), "uf": x.get("uf")}
        p = x.get("parametros") or {}; e = x.get("esteira") or {}
        urls = [x.get("pagina"), p.get("fonte_oficial"), (p.get("edital") or {}).get("url"), e.get("site_oficial")] + \
               [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)]
        for u in urls:
            if u:
                ks = chaves({**base, "url": u})
                if x.get("municipio") and x.get("uf"):
                    ks.append(f"municipio:{_sem_acento(x['municipio'])}-{_sem_acento(x['uf'])}")
                pôr(ks, u, "livro")
    for c in (certidoes or {}).values():
        if c.get("link_oficial"):
            pôr(chaves({"orgao": c.get("orgao"), "titulo": c.get("titulo"), "uf": c.get("uf"), "url": c["link_oficial"]}), c["link_oficial"], "certidão")
    return bib


def sites_conhecidos(op: dict, bib: dict) -> list[str]:
    out = []
    for k in chaves(op):
        out += (bib.get(k) or {}).get("urls") or []
    return list(dict.fromkeys(out))[:6]


def dominios(op: dict, bib: dict, anterior: dict | None) -> list[str]:
    us = [op.get("link_oficial"), (anterior or {}).get("link_oficial"), op.get("url")] + sites_conhecidos(op, bib)
    out = []
    for u in us:
        if u and L.regua(u)[0]:
            try:
                out.append("{0.scheme}://{0.netloc}".format(urlsplit(u)))
            except ValueError:
                pass
    return [d for d in dict.fromkeys(out) if "pncp.gov.br" not in d and "in.gov.br" not in d][:3]


def termos(op: dict) -> list[str]:
    t = str(op.get("titulo") or "")
    num = re.findall(r"\b\d{1,4}\s*/\s*20\d{2}\b", t)
    pal = [w for w in re.findall(r"[A-Za-zÀ-ú]{5,}", _sem_acento(t)) if w not in
           ("diario", "oficial", "edital", "publico", "publica", "municipio", "prefeitura", "municipal", "chamamento", "selecao")][:4]
    return [n.replace(" ", "") for n in num] + pal


# ── DOCUMENTOS DE CADA ABORDAGEM ───────────────────────────────────────────────────────────────────────────────
def documentos(n: int, op: dict, rede, anterior: dict | None, bib: dict, maximo: int = 4) -> tuple[list[dict], dict]:
    """(documentos candidatos, ajustes de leitura). Lista vazia = a abordagem não tem material para esta oportunidade."""
    from . import cartorio as C
    ant = anterior or {}
    oficiais_lidos = [d["url"] for d in (ant.get("documentos") or []) if d.get("oficial")]
    aj = {"seguir_links": n in (1, 2, 3, 4, 6, 10), "paginas": 150 if n == 9 else 60, "extra": 8 if n == 3 else 4}
    if n == 1:
        return C.documentos(op, rede, 3, pncp_teto=3), aj
    if n == 2:
        docs = C.documentos(op, rede, 12, pncp_teto=15)
        return [d for d in docs if d["url"] not in oficiais_lidos] or docs, {**aj, "seguir_links": True}
    if n == 3:
        us = [u for u in (op.get("link_oficial"), ant.get("link_oficial"), op.get("url")) if u and L.regua(u)[0]]
        return [{"url": u, "degrau": 1, "como": "página oficial e documentos citados nela"} for u in dict.fromkeys(us)], aj
    if n == 4:
        return [{"url": u, "degrau": 1, "como": "biblioteca de sites oficiais conhecidos do órgão"} for u in sites_conhecidos(op, bib)], aj
    if n == 5:
        out = []
        for d in dominios(op, bib, ant):
            for t in termos(op)[:2]:
                out += [{"url": u, "degrau": 2, "como": f"mídia do WordPress do site oficial ({t})"} for u in C._wordpress(d, t, rede)]
        return out[:maximo], aj
    if n == 6:
        return mapa_do_site(op, rede, bib, ant)[:maximo], aj
    if n == 7:
        us = oficiais_lidos + [u for u in (op.get("historico_urls") or []) if op.get("_tipo") == "livro"]
        return [{"url": u, "degrau": 0, "como": "releitura com o gabarito do órgão atualizado"} for u in dict.fromkeys(us)][:maximo], aj
    if n == 8:
        falhos = [d["url"] for d in (ant.get("documentos") or []) if str(d.get("falha") or "").startswith("erro_rede")]
        return [{"url": u, "degrau": 0, "como": "ponte do titular (IP do Brasil)"} for u in dict.fromkeys(falhos)][:maximo], {**aj, "ponte": True}
    if n == 9:
        us = oficiais_lidos + [u for u in (op.get("url_documento"), op.get("link_oficial")) if u]
        return [{"url": u, "degrau": 0, "como": "leitura profunda (até 150 páginas e tabelas)"} for u in dict.fromkeys(us)][:maximo], aj
    if n == 10:
        out = []
        try:
            from .piloto_busca import buscar_na_fonte
            for d in dominios(op, bib, ant):
                for r in buscar_na_fonte(urlsplit(d).netloc, termos(op), tempo=15, teto=10) or []:
                    u = r.get("url") or r.get("link")
                    if u and L.regua(u)[0]:
                        out.append({"url": u, "degrau": 2, "como": "busca restrita ao domínio oficial"})
        except Exception:  # noqa: BLE001
            pass
        return out[:maximo], aj
    return [], aj


def mapa_do_site(op: dict, rede, bib: dict, ant: dict) -> list[dict]:
    out, tt = [], termos(op)
    num = [t for t in tt if "/" in t]
    for d in dominios(op, bib, ant):
        for cam in ("/sitemap.xml", "/wp-sitemap.xml", "/sitemap_index.xml"):
            raw, _t, err = rede.get(d + cam)
            if err or not raw or b"<loc>" not in raw[:200000]:
                continue
            locs = re.findall(rb"<loc>\s*([^<\s]+)\s*</loc>", raw)[:3000]
            filhos = [l.decode("utf-8", "ignore") for l in locs if l.endswith(b".xml")][:3]
            for f in filhos:
                r2, _t2, e2 = rede.get(f)
                if not e2 and r2:
                    locs += re.findall(rb"<loc>\s*([^<\s]+)\s*</loc>", r2)[:3000]
            for l in locs:
                u = l.decode("utf-8", "ignore"); us = _sem_acento(u)
                if re.search(r"edital|chamamento|chamada|selecao|premio|credenciamento", us) and \
                        (any(n.replace("/", "-") in us or n.replace("/", "") in us for n in num) or sum(1 for p in tt if p in us) >= 2):
                    out.append({"url": u, "degrau": 2, "como": "mapa do site oficial (sitemap)"})
            break
    return list({d["url"]: d for d in out}.values())


# ── ACÚMULO ENTRE TENTATIVAS ───────────────────────────────────────────────────────────────────────────────────
def acumular(anterior: dict | None, nova: dict, n: int, faltam_agora: list[str]) -> dict:
    """A certidão nunca perde o que já achou: itens e dispensas se somam; registra a abordagem e o que ela rendeu."""
    a = anterior or {}
    itens = {**(a.get("itens") or {}), **(nova.get("itens") or {})}
    disp = {k: v for k, v in {**(a.get("dispensas") or {}), **(nova.get("dispensas") or {})}.items() if k not in itens}
    ganhou = sorted(k for k in list(nova.get("itens") or {}) + list(nova.get("dispensas") or {})
                    if k not in (a.get("itens") or {}) and k not in (a.get("dispensas") or {}))
    hist = list(a.get("abordagens") or [])
    if a and not hist:                                    # certidão anterior à linha de produção: vale como a 1ª
        hist = [{"n": 1, "nome": ABORDAGENS[1], "em": a.get("em"), "ganhou": sorted(a.get("itens") or {}), "legado": True}]
    hist.append({"n": n, "nome": ABORDAGENS[n], "em": nova.get("em"), "ganhou": ganhou,
                 "documentos": len(nova.get("documentos") or []), "link_oficial_novo": bool(nova.get("link_oficial") and not a.get("link_oficial"))})
    faltavam = list(dict.fromkeys(list(a.get("faltavam") or []) + list(faltam_agora)))
    res = [k for k in faltavam if k in itens or k in disp]
    out = {**a, **{k: v for k, v in nova.items() if v not in (None, [], {})}}
    out.update({"itens": itens, "dispensas": disp, "abordagens": hist, "tentativa": len(hist), "faltavam": faltavam,
                "resolvidos": res, "ainda_faltam": [k for k in faltavam if k not in res],
                "eficiencia": round(len(res) / len(faltavam), 3) if faltavam else 1.0,
                "link_oficial": a.get("link_oficial") or nova.get("link_oficial"),
                "documentos": ((a.get("documentos") or []) + (nova.get("documentos") or []))[-24:]})
    for k in ("degrau", "como", "regua"):
        if a.get("link_oficial"):
            out[k] = a.get(k)
    if out["tentativa"] >= MAX_TENTATIVAS and (out["ainda_faltam"] or not out["link_oficial"]):
        out["encaminhado"] = ("Chrome (último recurso): robots.txt proíbe" if "robots" in str(nova.get("encaminhado") or "") else
                              "Interceptador: as 10 abordagens do Cartório foram esgotadas") + f" — faltam {', '.join(out['ainda_faltam'][:6]) or 'o site oficial'}"
        out["esgotada"] = True
    elif not out["ainda_faltam"] and out["link_oficial"]:
        out["encaminhado"] = None
    return out
