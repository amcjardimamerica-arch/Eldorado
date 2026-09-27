"""ONDE A OPORTUNIDADE NASCE — o site oficial da fonte, não quem a republicou (titular, 27/09).

O edital do BNDES apareceu com "página oficial" no Facebook da ABCR: o site onde a notícia foi vista virou o
"órgão", a busca partiu dele e o primeiro resultado foi aceito. Este módulo separa as duas coisas:

  CATÁLOGO DE REPUBLICADORES (config/republicadores.json) — sites de notícia, agregadores, redes sociais e
  encurtadores. São INDÍCIO e insumo de busca, nunca fonte oficial. Plataformas de inscrição (Prosas etc.) são
  aceitas como canal oficial só quando trazem o regulamento do edital.

  APRENDIZADO (estado/interceptador/sites_oficiais.json) — para cada financiador, o domínio oficial já
  confirmado, a rota que funcionou e exemplos. A próxima oportunidade do mesmo financiador começa por ele.

  ROTAS, em ordem, até uma página ser VALIDADA (fala do programa + tem sinais de edital):
    1. domínio já aprendido do financiador          → busca "programa" dentro dele
    2. links citados no texto da notícia            → os que levam ao domínio do financiador
    3. buscas criativas pelo financiador e programa → site:domínio, "regulamento", "inscrições", PDF, .gov.br
    4. nada validado → sem página oficial (a notícia fica como indício, marcada)
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "config/republicadores.json"
APRENDIZADO = ROOT / "estado/interceptador/sites_oficiais.json"


def _n(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    return re.sub(r"[^a-z0-9 ]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


def host(u: str) -> str:
    return (urlsplit(str(u or "")).hostname or "").lower().replace("www.", "")


def _cat() -> dict:
    try:
        return json.loads(CATALOGO.read_text(encoding="utf-8"))
    except Exception:
        return {}


def classificar(url: str) -> str:
    """oficial_possivel | noticia | agregador | rede_social | encurtador | plataforma_inscricao | buscador"""
    h, u = host(url), str(url or "").lower()
    if not h:
        return "invalido"
    c = _cat()
    for cat in ("rede_social", "encurtador", "buscador", "agregador", "noticia", "plataforma_inscricao"):
        for d in c.get(cat, []):
            if h == d or h.endswith("." + d):
                return cat
    # caminho com cara de notícia em qualquer site: /noticias/, /blog/, /2026/09/...
    if re.search(r"/(noticias?|news|blog|artigos?|post|imprensa|clipping)/|/20\d\d/\d\d/", u):
        return "noticia"
    return "oficial_possivel"


def e_republicador(url: str) -> bool:
    return classificar(url) in ("noticia", "agregador", "rede_social", "encurtador", "buscador")


# ── aprendizado ───────────────────────────────────────────────────────────────────────────────
def _apr() -> dict:
    try:
        return json.loads(APRENDIZADO.read_text(encoding="utf-8"))
    except Exception:
        base = _cat().get("financiadores_conhecidos", {})
        return {"regra": "financiador → domínio oficial confirmado; alimentado a cada página oficial validada", "financiadores": {
            k: {"dominio": v, "origem": "semente do catálogo", "confirmacoes": 0, "exemplos": []} for k, v in base.items()}}


def dominio_aprendido(financiador: str) -> str | None:
    f = _n(financiador)
    if not f:
        return None
    for k, v in _apr()["financiadores"].items():
        kn = _n(k)
        if kn and (kn == f or kn in f or (len(f) > 5 and f in kn)):
            return v.get("dominio")
    return None


def aprender(financiador: str, url: str, rota: str) -> None:
    if not financiador or not url or e_republicador(url):
        return
    a = _apr(); k = financiador.strip()[:80]
    r = a["financiadores"].setdefault(k, {"dominio": host(url), "origem": rota, "confirmacoes": 0, "exemplos": []})
    r["dominio"] = r.get("dominio") or host(url)
    r["confirmacoes"] = r.get("confirmacoes", 0) + 1
    r["ultima_rota"] = rota; r["atualizado_em"] = date.today().isoformat()
    r["exemplos"] = ([url] + [x for x in r.get("exemplos", []) if x != url])[:5]
    rotas = a.setdefault("rotas_que_funcionam", {}); rotas[rota] = rotas.get(rota, 0) + 1
    APRENDIZADO.parent.mkdir(parents=True, exist_ok=True)
    APRENDIZADO.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")


# ── o financiador real, lido na notícia ───────────────────────────────────────────────────────
PROMPT_FINANCIADOR = """Você lê uma NOTÍCIA que divulga uma oportunidade (edital, chamada, prêmio). Quem REPUBLICA a notícia não é o
financiador. Diga quem de fato financia/publica a oportunidade e como ela se chama. Responda APENAS o JSON:
{{"financiador": "nome da organização que publica o edital", "parceiros": ["co-realizadores citados"],
  "programa": "nome do edital/chamada/programa", "site_citado": "endereço citado no texto para inscrição/regulamento ou null",
  "publico": true|false, "palavras_chave": ["3 a 5 termos distintivos do edital"]}}
QUEM REPUBLICOU (não é o financiador): {republicador}
TÍTULO: {titulo}
TEXTO:
{texto}
"""


def financiador(ia, titulo: str, url_noticia: str, texto: str) -> dict:
    r = ia.perguntar(PROMPT_FINANCIADOR.format(republicador=host(url_noticia), titulo=titulo[:200], texto=texto[:9000]),
                     '{"financiador","parceiros","programa","site_citado","publico","palavras_chave"}') if ia else None
    r = r if isinstance(r, dict) else {}
    if not r.get("financiador"):
        m = re.search(r"(?:o|a)\s+((?:Banco|Fundação|Instituto|Ministério|Secretaria|Governo|Prefeitura|Conselho|Fundo)[^,.;:]{3,70})", texto or "")
        r["financiador"] = m.group(1).strip() if m else ""
    if host(r.get("financiador") or "") and e_republicador(r["financiador"]):
        r["financiador"] = ""
    return r


# ── validação de uma página candidata ─────────────────────────────────────────────────────────
def validar(url: str, texto_pagina: str, programa: str, chaves: list[str]) -> tuple[bool, str]:
    if not url or e_republicador(url):
        return False, "republicador/notícia/rede social"
    t = _n(texto_pagina)[:60000]
    alvo = [w for w in _n(" ".join([programa or ""] + (chaves or []))).split() if len(w) > 3][:12]
    bate = sum(1 for w in set(alvo) if w in t) / max(1, len(set(alvo)))
    sinais = sum(1 for s in ("inscri", "regulamento", "edital", "prazo", "anexo", "cronograma", "elegib", "propost", "chamada", "selecao") if s in t)
    if classificar(url) == "plataforma_inscricao" and sinais < 3:
        return False, "plataforma sem regulamento"
    ok = bate >= 0.5 and sinais >= 2
    return ok, f"termos do edital {int(bate * 100)}% · sinais de edital {sinais}"


def rotas_de_busca(fin: dict, dominio: str | None, titulo: str) -> list[tuple[str, str]]:
    """Consultas criativas, das mais cirúrgicas às mais abertas. Cada uma com o nome da rota (para o aprendizado)."""
    prog = (fin.get("programa") or re.sub(r"(?i)^continue lendo\s+", "", titulo))[:90]
    f = (fin.get("financiador") or "")[:70]; ch = " ".join((fin.get("palavras_chave") or [])[:3])
    ano = str(date.today().year)
    rs = []
    if dominio:
        rs += [("site_do_financiador", f'site:{dominio} {prog}'), ("site_do_financiador_edital", f'site:{dominio} edital {ch or prog[:40]}')]
    if f:
        rs += [("financiador_programa_edital", f'"{prog}" {f} edital inscrições'), ("financiador_regulamento", f'{f} {prog[:50]} regulamento'),
               ("financiador_pdf", f'{f} {prog[:50]} edital filetype:pdf'), ("financiador_ano", f'{f} edital {ano} {ch}')]
        if fin.get("publico"):
            rs.append(("governo", f'{prog[:60]} {f} site:gov.br'))
    for p in (fin.get("parceiros") or [])[:2]:
        rs.append(("parceiro", f'{p} {prog[:50]} edital'))
    rs.append(("programa_puro", f'"{prog}" inscrições'))
    return rs


def descobrir(ia, e: dict, ler, buscar, links_da_pagina) -> tuple[str | None, str, dict]:
    """A página oficial da oportunidade. Devolve (url, como_foi_achada, diagnostico)."""
    diag = {"indicios": [], "tentativas": []}
    titulo = e.get("titulo") or ""
    noticia = e.get("url") or ""
    if noticia and e_republicador(noticia):
        diag["indicios"].append({"url": noticia, "tipo": classificar(noticia)})
    txt_noticia = ler(noticia) if noticia.startswith("http") else ""
    fin = financiador(ia, titulo, noticia, txt_noticia or titulo)
    diag["financiador"] = fin.get("financiador"); diag["programa"] = fin.get("programa")
    dom = dominio_aprendido(fin.get("financiador") or "")
    chaves = fin.get("palavras_chave") or []
    candidatos = []
    # rota 0: site citado no próprio texto
    if fin.get("site_citado") and str(fin["site_citado"]).startswith("http") and not e_republicador(fin["site_citado"]):
        candidatos.append((fin["site_citado"], "site_citado_na_noticia"))
    # rota 2: links da notícia que levam ao domínio do financiador (ou a um domínio que tenha o nome dele)
    toks = [w for w in _n(fin.get("financiador") or "").split() if len(w) > 3]
    for u, _rot in (links_da_pagina(noticia) if noticia.startswith("http") else []):
        if e_republicador(u):
            continue
        h = host(u).replace(".", " ")
        if (dom and host(u).endswith(dom)) or any(w in h for w in toks):
            candidatos.append((u, "link_da_noticia_para_o_financiador"))
    # rota 1 e 3: buscas
    for rota, q in rotas_de_busca(fin, dom, titulo):
        try:
            res = buscar(q, maximo=8) or []
        except Exception:
            res = []
        diag["tentativas"].append({"rota": rota, "consulta": q[:120], "resultados": len(res)})
        for r in res:
            u = r.get("url") or ""
            if not u.startswith("http") or e_republicador(u):
                continue
            h = host(u)
            pontos = (3 if dom and h.endswith(dom) else 0) + (2 if any(w in h.replace(".", " ") for w in toks) else 0) + \
                     (1 if re.search(r"edital|chamad|regulamento|inscri|selec|premio|\.pdf", u.lower()) else 0) + (1 if h.endswith(".gov.br") and fin.get("publico") else 0)
            candidatos.append((u, rota, pontos))
        if len(candidatos) >= 10:
            break
    vistos = set()
    cand = sorted([(c[0], c[1], c[2] if len(c) > 2 else 5) for c in candidatos], key=lambda c: -c[2])
    for u, rota, _p in cand:
        if u in vistos:
            continue
        vistos.add(u)
        tp = ler(u)
        ok, porque = validar(u, tp, fin.get("programa") or titulo, chaves)
        diag["tentativas"].append({"validou": u[:140], "ok": ok, "porque": porque, "rota": rota})
        if ok:
            aprender(fin.get("financiador") or "", u, rota)
            return u, f"{rota} — {porque}", diag
        if len(vistos) >= 8:
            break
    return None, "nenhuma página oficial validada — a notícia fica como indício", diag
