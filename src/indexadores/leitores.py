"""Os leitores — um por METODOLOGIA. Cada site do catálogo usa um deles, com os parâmetros do próprio site.

Assinatura comum: ler(site, rede, est, ctx) -> dict com
  itens     indícios (dicionários no contrato de estado/agregadores/itens.json, com campos extras)
  falhas    [{url, tipo, detalhe, status}]  (tipo vem de rede.Bloqueio: robots, geo, waf, limite, http, rede...)
  lidas     páginas lidas com sucesso (304 conta como leitura)
  pendente  True quando ficou trabalho para a próxima rodada (orçamento, cota do site, retroativo)
  diag      números do site para o painel
`est` é o estado do site (cursor, vistos, lista que funcionou) e é atualizado no lugar.
`ctx` = {"hoje": date, "via": "direta"|"ponte", "limites": {...}, "estado_motores": {...}}
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode, urljoin, urlsplit
import xml.etree.ElementTree as ET

from . import extracao as X
from .rede import Bloqueio

NS = {"content": "http://purl.org/rss/1.0/modules/content/", "atom": "http://www.w3.org/2005/Atom",
      "dc": "http://purl.org/dc/elements/1.1/"}


_RESULTADO = re.compile(r"resultado|aprovad[oa]s|selecionad[oa]s|divulga lista|homologa|classifica[cç][ãa]o final|encerrad[oa]", re.I)


# ------------------------------------------------------------------ item
def id_de(pagina: str) -> str:
    """Mesmo id do antigo motor de agregadores (sha1 da página do agregador): decisões já registradas valem."""
    return "agr-" + hashlib.sha1(str(pagina).encode()).hexdigest()[:12]


def item(site: dict, ctx: dict, *, titulo: str, pagina: str, link_oficial: str | None = None, prazo: str | None = None,
         financiador: str | None = None, valor: str | None = None, uf: str | None = None, pais: str | None = None,
         areas: list | None = None, tipo: str | None = None, resumo: str | None = None, publicado: str | None = None,
         texto_perfil: str = "", extra: dict | None = None) -> dict:
    titulo = X.limpar_titulo(titulo, site.get("nome", "").split(" — ")[0])
    texto = " ".join(x for x in (titulo, resumo or "", texto_perfil or "") if x)
    pf, motivo = X.perfil(texto)
    if _RESULTADO.search(titulo):                       # resultado, lista de aprovados, encerrado: guardado, fora do fluxo
        pf, motivo = "fora", "o título indica resultado ou encerramento, não inscrição aberta"
    if financiador and re.fullmatch(r"(?i)\s*mapas? cultura(l|is)?\s*", str(financiador)):
        financiador = None                              # o Farol põe "Mapa Cultural" no lugar do órgão
    if not uf:
        uf = X.uf_do_endereco(link_oficial) or X.uf_do_endereco(pagina) or (X.uf(financiador) if financiador else None)
    hoje = ctx["hoje"].isoformat()
    it = {"id": id_de(pagina), "fonte": site["id"], "fonte_nome": site.get("nome"), "motor": site.get("motor"),
          "titulo": titulo, "pagina_agregador": pagina, "link_oficial": link_oficial, "prazo": prazo,
          "financiador": X.limpar(financiador, 160) or None, "valor": valor, "uf": uf,
          "pais": pais or ("BR" if not site.get("internacional") else None),
          "areas": sorted(set((areas or []) + list(site.get("areas") or []))), "tipo": tipo,
          "resumo": X.limpar(resumo, 300) or None, "publicado": (publicado or "")[:10] or None,
          "perfil": pf, "perfil_motivo": motivo, "rota": ctx.get("rota", "nuvem"), "visto_em": hoje}
    if X.injecao(texto):
        it["quarentena"] = "texto com cara de instrução para IA — dado, não ordem; revisar antes de usar"
    if extra:
        it.update(extra)
    it["chave"] = X.chave(it)
    return it


def _falha(url: str, b: Exception) -> dict:
    if isinstance(b, Bloqueio):
        return {"url": url, "tipo": b.tipo, "detalhe": b.detalhe[:160], "status": b.status}
    return {"url": url, "tipo": "erro", "detalhe": f"{type(b).__name__}: {str(b)[:140]}", "status": None}


def _cota(site: dict, ctx: dict) -> int:
    return int(site.get("itens_por_rodada") or ctx["limites"].get("itens_por_site_por_rodada", 80))


def _get(rede, url, site, ctx, **kw):
    # robots.txt só deixa de valer com AUTORIZAÇÃO ESCRITA do site registrada no catálogo (quem, quando, documento)
    aut = site.get("autorizacao") or {}
    if aut.get("documento") and aut.get("em"):
        kw.setdefault("checar_robots", False)
    return rede.obter(url, via=ctx.get("via", "direta"), pausa=site.get("pausa_s"), timeout=site.get("timeout_s"),
                      max_bytes=site.get("bytes_max"), **kw)


def _artigo(rede, url, site, ctx) -> tuple[str, list, str, list]:
    """Lê a página de um item: (texto, links, titulo, jsonld)."""
    r = _get(rede, url, site, ctx, condicional=False)
    html = r.texto()
    p = X.pagina(html)
    titulo = p.meta.get("og:title") or p.h1 or p.titulo
    return X.texto_de(html), p.links, titulo, X.jsonld(p)


# ------------------------------------------------------------------ L1a: feed RSS/Atom
def _itens_feed(xml_txt: str) -> list[dict]:
    out = []
    try:
        raiz = ET.fromstring(xml_txt.encode("utf-8") if isinstance(xml_txt, str) else xml_txt)
    except ET.ParseError:
        raiz = None
    if raiz is not None:
        for it in raiz.iter("item"):
            out.append({"titulo": (it.findtext("title") or "").strip(), "link": (it.findtext("link") or "").strip(),
                        "data": it.findtext("pubDate") or it.findtext("dc:date", namespaces=NS) or "",
                        "html": it.findtext("content:encoded", namespaces=NS) or it.findtext("description") or "",
                        "categorias": [c.text or "" for c in it.findall("category")]})
        for en in raiz.iter("{http://www.w3.org/2005/Atom}entry"):
            ln = en.find("atom:link[@rel='alternate']", NS)
            if ln is None:
                ln = en.find("atom:link", NS)
            out.append({"titulo": (en.findtext("atom:title", namespaces=NS) or "").strip(),
                        "link": (ln.get("href") if ln is not None else "") or "",
                        "data": en.findtext("atom:updated", namespaces=NS) or en.findtext("atom:published", namespaces=NS) or "",
                        "html": en.findtext("atom:content", namespaces=NS) or en.findtext("atom:summary", namespaces=NS) or "",
                        "categorias": [c.get("term") or "" for c in en.findall("atom:category", NS)]})
        return out
    for bloco in re.findall(r"<item[\s>]([\s\S]*?)</item>", xml_txt or ""):       # feed malformado: leitura tolerante
        g = lambda tag: re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", bloco) or [None, ""])[1]).strip()
        out.append({"titulo": X.limpar(g("title")), "link": g("link"), "data": g("pubDate"),
                    "html": g("content:encoded") or g("description"), "categorias": []})
    return out


def _data_feed(s: str) -> str | None:
    s = (s or "").strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None


def ler_feed(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"no_feed": 0, "novos": 0, "artigos_lidos": 0}}
    vistos = est.setdefault("vistos", {})
    paginas = [site["url"]]
    if not est.get("retro_feito"):
        sep = "&" if "?" in site["url"] else "?"
        paginas += [f"{site['url']}{sep}paged={n}" for n in range(2, int(site.get("paginas_retroativas") or 1) + 1)]
    host = urlsplit(site.get("pagina") or site["url"]).hostname or ""
    filtro = re.compile(site["filtro_titulo"], re.I) if site.get("filtro_titulo") else None
    cota, gastos, terminou = _cota(site, ctx), 0, True
    for n, u in enumerate(paginas):
        try:
            r = _get(rede, u, site, ctx, condicional=(n == 0), aceitar="application/rss+xml, application/xml, text/xml, */*")
        except Bloqueio as b:
            if b.tipo == "orcamento":
                res["pendente"] = True; terminou = False; break
            if n == 0:
                res["falhas"].append(_falha(u, b))
            break                                   # páginas retroativas que não existem encerram o retroativo
        res["lidas"] += 1
        if r.nao_mudou:
            continue
        for e in _itens_feed(r.texto()):
            res["diag"]["no_feed"] += 1
            link = e["link"]
            if not link or not e["titulo"] or link in vistos:
                continue
            if filtro and not filtro.search(e["titulo"] + " " + " ".join(e["categorias"])):
                vistos[link] = ctx["hoje"].isoformat()
                continue
            frag = e["html"] or ""
            links = X.pagina(frag).links
            texto = X.html_para_texto(frag)
            oficial = X.oficial(link, links, e["titulo"], [host])
            pz = X.prazo(texto, ctx["hoje"], _data_feed(e["data"]))      # 03/10: sem ano, vale o ano do post
            if site.get("seguir_artigo") and (not oficial or not pz):
                if gastos >= cota or rede.esgotado():
                    res["pendente"] = True; terminou = False
                    continue                        # fica para a próxima rodada (não marca como visto)
                try:
                    t2, l2, _, _ = _artigo(rede, link, site, ctx)
                    gastos += 1; res["diag"]["artigos_lidos"] += 1
                    texto = (texto + "\n" + t2)[:60_000]
                    oficial = oficial or X.oficial(link, l2, e["titulo"], [host])
                    pz = pz or X.prazo(t2, ctx["hoje"], _data_feed(e["data"]))
                except Bloqueio as b:
                    if b.tipo == "orcamento":
                        res["pendente"] = True; terminou = False; continue
                    res["falhas"].append(_falha(link, b))
                    fa = est.setdefault("falhas_artigo", {}); fa[link] = fa.get(link, 0) + 1
                    if fa[link] < 3:
                        res["pendente"] = True; continue          # tenta de novo na próxima rodada
            vistos[link] = ctx["hoje"].isoformat()
            res["itens"].append(item(site, ctx, titulo=e["titulo"], pagina=link, link_oficial=oficial, prazo=pz,
                                     valor=X.valor(texto), uf=X.uf(e["titulo"]) or X.uf(texto[:1500]),
                                     resumo=texto[:300], publicado=_data_feed(e["data"]), texto_perfil=texto[:4000],
                                     financiador=site.get("financiador")))
            res["diag"]["novos"] += 1
    if terminou and not res["falhas"]:
        est["retro_feito"] = True
    _podar(vistos, 600)
    return res


def _podar(d: dict, n: int) -> None:
    if len(d) > n:
        for k in sorted(d, key=lambda k: str(d[k]))[: len(d) - n]:
            del d[k]


# ------------------------------------------------------------------ L1b: API REST do WordPress
def ler_wordpress(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"lidos_api": 0, "novos": 0}}
    host = urlsplit(site.get("pagina") or site["url"]).hostname or ""
    desde = est.get("modificado_ate")
    params = {"per_page": 50, "orderby": "modified", "order": "desc", "_fields": "id,date,modified,link,title,content,excerpt"}
    if desde:
        params["modified_after"] = desde
    else:
        params["after"] = (ctx["hoje"] - timedelta(days=int(site.get("janela_dias") or 180))).isoformat() + "T00:00:00"
    maior = desde
    vistos = est.setdefault("vistos", {})
    lidos_artigo = 0
    for pag in range(1, int(site.get("paginas_max") or 4) + 1):
        u = site["url"] + "?" + urlencode({**params, "page": pag})
        try:
            r = _get(rede, u, site, ctx, condicional=False, aceitar="application/json")
        except Bloqueio as b:
            if b.tipo == "orcamento":
                res["pendente"] = True
            elif not (b.status == 400 and pag > 1):          # WP responde 400 depois da última página
                res["falhas"].append(_falha(u, b))
            break
        res["lidas"] += 1
        try:
            lista = json.loads(r.texto())
        except Exception:
            res["falhas"].append({"url": u, "tipo": "http", "detalhe": "resposta não é JSON", "status": r.status}); break
        if not isinstance(lista, list) or not lista:
            break
        for p in lista:
            res["diag"]["lidos_api"] += 1
            link = p.get("link") or ""
            mod = p.get("modified") or p.get("date") or ""
            maior = max(maior or "", mod) or None
            if not link or vistos.get(link) == mod:
                continue
            titulo = X.limpar((p.get("title") or {}).get("rendered"))
            frag = (p.get("content") or {}).get("rendered") or ""
            texto = (X.html_para_texto((p.get("excerpt") or {}).get("rendered") or "") + "\n" + X.html_para_texto(frag))[:60_000]
            links = X.pagina(frag).links
            oficial = link if site.get("proprio") else (X.oficial(link, links, titulo, [host]) or None)
            if site.get("seguir_artigo") and not site.get("proprio") and (not oficial or not X.prazo(texto, ctx["hoje"])):
                if lidos_artigo >= _cota(site, ctx) or rede.esgotado():
                    res["pendente"] = True
                    continue                                    # o item volta na próxima rodada (não marca como visto)
                try:
                    t2, l2, _, _ = _artigo(rede, link, site, ctx)
                    lidos_artigo += 1
                    texto = (texto + "\n" + t2)[:60_000]
                    oficial = oficial or X.oficial(link, l2, titulo, [host])
                except Bloqueio as b:
                    if b.tipo == "orcamento":
                        res["pendente"] = True; continue
                    res["falhas"].append(_falha(link, b))
                    fa = est.setdefault("falhas_artigo", {}); fa[link] = fa.get(link, 0) + 1
                    if fa[link] < 3:
                        res["pendente"] = True; maior = desde; continue     # o cursor não avança: o item volta
            vistos[link] = mod
            res["itens"].append(item(site, ctx, titulo=titulo, pagina=link, link_oficial=oficial, prazo=X.prazo(texto, ctx["hoje"], (p.get("date") or "")[:10]),
                                     valor=X.valor(texto), uf=X.uf(titulo) or X.uf(texto[:2000]), resumo=texto[:300],
                                     publicado=(p.get("date") or "")[:10], texto_perfil=texto[:4000],
                                     financiador=site.get("financiador")))
            res["diag"]["novos"] += 1
        tot = r.cabecalhos.get("x-wp-totalpages")
        if tot and pag >= int(tot):
            break
        if len(lista) < params["per_page"]:
            break
    else:
        res["pendente"] = True
    if maior and not res["falhas"]:
        est["modificado_ate"] = maior[:19]
    _podar(vistos, 800)
    return res


# ------------------------------------------------------------------ L2a: API do Farol Cultural
def _moeda(v, moeda) -> str | None:
    if v in (None, "", 0):
        return None
    try:
        n = float(v)
    except (TypeError, ValueError):
        return X.limpar(v, 40)
    simb = {"BRL": "R$", "USD": "US$", "EUR": "€", "GBP": "£"}.get(str(moeda or "BRL").upper(), str(moeda or ""))
    inteiro = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{simb} {inteiro}".strip()


def ler_farol_api(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"abertos": 0, "paginas": 0, "brasil": 0}}
    total_paginas = None
    for pag in range(1, int(site.get("paginas_max") or 8) + 1):
        u = site["url"] + "?" + urlencode({"status": site.get("status", "Aberto"), "per_page": site.get("por_pagina", 100), "page": pag})
        try:
            r = _get(rede, u, site, ctx, condicional=False, aceitar="application/json")
        except Bloqueio as b:
            if b.tipo == "orcamento":
                res["pendente"] = True
            else:
                res["falhas"].append(_falha(u, b))
            break
        res["lidas"] += 1
        try:
            d = json.loads(r.texto())
        except Exception:
            res["falhas"].append({"url": u, "tipo": "http", "detalhe": "resposta não é JSON", "status": r.status}); break
        meta = d.get("meta") or {}
        total_paginas = int(meta.get("total_pages") or 1)
        res["diag"]["abertos"] = int(meta.get("total") or 0)
        res["diag"]["paginas"] = pag
        for e in d.get("data") or []:
            slug = e.get("slug") or str(e.get("id") or "")
            if not slug or not e.get("titulo"):
                continue
            pagina = f"https://farolcultural.art/e/{slug}"
            pais = (e.get("pais") or "").upper() or None
            ufe = (e.get("estado") or "").upper()
            ufe = ufe if ufe in X.UFS else (X.uf(e.get("titulo") or "") if pais in (None, "BR") else None)
            res["diag"]["brasil"] += 1 if pais == "BR" else 0
            areas = ["cultura"] + [X.limpar(a, 40).lower() for a in (e.get("area_artistica") or []) if a][:6]
            res["itens"].append(item(site, ctx, titulo=e.get("titulo"), pagina=pagina,
                                     link_oficial=e.get("url_original") or e.get("url_pdf"),
                                     prazo=(e.get("data_fim_inscricao") or "")[:10] or None,
                                     financiador=e.get("instituicao_nome"),
                                     valor=_moeda(e.get("valor_por_projeto") or e.get("valor_total"), e.get("moeda")),
                                     uf=ufe or None, pais=pais, areas=areas, tipo=e.get("tipo"), resumo=e.get("resumo"),
                                     publicado=e.get("data_publicacao") or e.get("created_at"),
                                     texto_perfil=f"{e.get('resumo') or ''} {e.get('tipo') or ''}",
                                     extra={"cidade": e.get("cidade"), "pdf": e.get("url_pdf")}))
        if pag >= total_paginas:
            break
    else:
        res["pendente"] = True
    return res


# ------------------------------------------------------------------ L2b: rede Mapas Culturais
def instancias_ativas(site: dict, est: dict, hoje: date) -> list[dict]:
    ok = est.setdefault("instancias", {})
    out = []
    for i in site.get("instancias") or []:
        s = ok.get(i["host"]) or {}
        if i.get("confirmada") or s.get("responde"):
            out.append(i)
    return out


def ler_mapas_culturais(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"instancias": {}, "sondadas": {}}}
    hoje = ctx["hoje"]
    tipos = re.compile(site.get("tipos") or "edital", re.I)
    info = est.setdefault("instancias", {})
    # sondagem semanal das instâncias candidatas (as que ainda não sabemos se respondem)
    for i in site.get("instancias") or []:
        s = info.setdefault(i["host"], {})
        if i.get("confirmada") or (s.get("sondada_em") and s["sondada_em"] > (hoje - timedelta(days=7)).isoformat()):
            continue
        u = f"https://{i['host']}/api/opportunity/find?" + urlencode({"@select": "id", "@limit": 1})
        try:
            r = _get(rede, u, site, ctx, condicional=False, aceitar="application/json")
            s["responde"] = isinstance(json.loads(r.texto()), list)
        except Bloqueio as b:
            if b.tipo == "orcamento":
                res["pendente"] = True; break
            s["responde"] = False; s["erro"] = b.tipo
        except Exception:
            s["responde"] = False
        s["sondada_em"] = hoje.isoformat()
        res["diag"]["sondadas"][i["host"]] = s.get("responde")
    for i in instancias_ativas(site, est, hoje):
        n_inst = 0
        for pag in range(1, 6):
            q = {"@select": "id,name,shortDescription,registrationFrom,registrationTo,singleUrl,type",
                 "registrationTo": f"GTE({hoje.isoformat()})", "@order": "registrationTo ASC", "@limit": 100, "@page": pag}
            u = f"https://{i['host']}/api/opportunity/find?" + urlencode(q)
            try:
                r = _get(rede, u, site, ctx, condicional=False, aceitar="application/json")
                lista = json.loads(r.texto())
            except Bloqueio as b:
                if b.tipo == "orcamento":
                    res["pendente"] = True
                else:
                    res["falhas"].append(_falha(u, b))
                break
            except Exception:
                res["falhas"].append({"url": u, "tipo": "http", "detalhe": "resposta não é JSON", "status": None}); break
            res["lidas"] += 1
            if not isinstance(lista, list) or not lista:
                break
            for o in lista:
                tipo = ((o.get("type") or {}).get("name") or "")
                nome = o.get("name") or ""
                if not (tipos.search(tipo) or X.EDITAL.search(nome)):
                    continue
                fim = ((o.get("registrationTo") or {}).get("date") or "")[:10] or None
                link = o.get("singleUrl") or f"https://{i['host']}/oportunidade/{o.get('id')}/"
                res["itens"].append(item(site, ctx, titulo=nome, pagina=link, link_oficial=link, prazo=fim,
                                         uf=i.get("uf") or X.uf(nome), tipo=tipo or None, resumo=o.get("shortDescription"),
                                         publicado=((o.get("registrationFrom") or {}).get("date") or "")[:10],
                                         texto_perfil=f"{nome} {o.get('shortDescription') or ''}",
                                         extra={"plataforma": i.get("nome"), "instancia": i["host"]}))
                n_inst += 1
            if len(lista) < 100:
                break
        res["diag"]["instancias"][i["host"]] = n_inst
        if rede.esgotado():
            res["pendente"] = True
            break
    return res


# ------------------------------------------------------------------ L2c: Transferegov — módulo Gestão de Parcerias
def ler_transferegov_api(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"programas": 0, "abertos": 0}}
    hoje = ctx["hoje"].isoformat()
    for pag in range(1, 6):
        u = site["url"] + "?" + urlencode({"situacao_programa": site.get("situacao", "Disponibilizado"), "tamanho_da_pagina": 100, "pagina": pag})
        try:
            r = _get(rede, u, site, ctx, condicional=False, aceitar="application/json")
            d = json.loads(r.texto())
        except Bloqueio as b:
            res["falhas"].append(_falha(u, b)); break
        except Exception:
            res["falhas"].append({"url": u, "tipo": "http", "detalhe": "resposta não é JSON", "status": None}); break
        res["lidas"] += 1
        lista = d.get("data") or []
        res["diag"]["programas"] = int(d.get("total_items") or len(lista))
        for p in lista:
            fins = [p.get(k) for k in ("dt_fim_beneficiario_espontaneo", "dt_fim_beneficiario_especifico", "dt_fim_beneficiario_emenda")]
            fins = [str(f)[:10] for f in fins if f and str(f)[:10] >= hoje]
            if not fins:
                continue
            cd = p.get("cd_programa") or p.get("id_programa")
            pagina = site["url"] + "?" + urlencode({"cd_programa": cd})
            texto = " ".join(str(p.get(k) or "") for k in ("ds_objetivo", "ds_publico_alvo", "tp_instrumento", "qualificacao_beneficiario"))
            res["itens"].append(item(site, ctx, titulo=f"{X.limpar(p.get('nm_programa'), 220)} (programa {cd})", pagina=pagina,
                                     prazo=max(fins), financiador=p.get("nm_ente_repassador") or p.get("nm_ente_superior"),
                                     tipo=p.get("tp_instrumento"), resumo=p.get("ds_objetivo"), texto_perfil=texto,
                                     valor=_moeda(p.get("nr_vlr_global"), "BRL"),
                                     extra={"pagina_e_api": True, "qualificacao": p.get("qualificacao_beneficiario"),
                                            "publico_alvo": X.limpar(p.get("ds_publico_alvo"), 300) or None}))
            res["diag"]["abertos"] += 1
        if pag >= int(d.get("total_pages") or 1):
            break
    return res


# ------------------------------------------------------------------ L2d: Prosas (JSON:API do widget) — só com autorização
def ler_prosas_api(site, rede, est, ctx) -> dict:
    """A lista pública do widget do Prosas (/selecao/api/v2/publics/oportunidades, JSON:API, 100 por página).
    Só roda com `autorizacao` do Prosas registrada no catálogo: o robots.txt do Prosas fecha o site a robôs."""
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"abertas": 0}}
    if not (site.get("autorizacao") or {}).get("documento"):
        res["falhas"].append({"url": site.get("url"), "tipo": "robots", "detalhe": "sem autorização escrita do Prosas", "status": None})
        return res
    for pag in range(1, 8):
        u = site["url"] + "?" + urlencode({"page[page]": pag, "page[size]": 100, "include": "incentivador,area_interesses"})
        try:
            r = _get(rede, u, site, ctx, condicional=False, aceitar="application/vnd.api+json, application/json")
            d = json.loads(r.texto())
        except Bloqueio as b:
            res["falhas"].append(_falha(u, b)); break
        except Exception:
            res["falhas"].append({"url": u, "tipo": "http", "detalhe": "resposta não é JSON", "status": None}); break
        res["lidas"] += 1
        inc = {(x.get("type"), x.get("id")): x.get("attributes") or {} for x in d.get("included") or []}
        for o in d.get("data") or []:
            a = o.get("attributes") or {}
            iv = ((o.get("relationships") or {}).get("incentivador") or {}).get("data") or {}
            areas = [(inc.get(("area_interesse", x.get("id"))) or {}).get("nome") for x in ((o.get("relationships") or {}).get("area_interesses") or {}).get("data") or []]
            link = f"https://prosas.com.br/editais/{a.get('id') or o.get('id')}"
            res["itens"].append(item(site, ctx, titulo=a.get("nome"), pagina=link, link_oficial=link,
                                     prazo=(a.get("data_final_inscricoes") or a.get("encerramento_das_inscricoes") or "")[:10] or None,
                                     financiador=(inc.get(("incentivador", iv.get("id"))) or {}).get("nome_fantasia") or a.get("nome_empresa"),
                                     areas=[X.limpar(x, 40).lower() for x in areas if x], texto_perfil=a.get("nome") or "",
                                     extra={"continuo": a.get("prazo") == "continuo"}))
        res["diag"]["abertas"] = int(((d.get("links") or {}).get("total")) or len(res["itens"]))
        if pag >= int((d.get("links") or {}).get("last") or 1):
            break
    return res


# ------------------------------------------------------------------ L3: sitemap + página estruturada (JSON-LD)
def _sitemap(xml_txt: str) -> list[tuple[str, str]]:
    out = []
    for bloco in re.findall(r"<url>([\s\S]*?)</url>", xml_txt or ""):
        loc = (re.search(r"<loc>\s*([^<\s]+)\s*</loc>", bloco) or [None, ""])[1]
        lm = (re.search(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", bloco) or [None, ""])[1]
        if loc:
            out.append((X.limpar(loc, 600), lm))
    return out


def ler_sitemap_jsonld(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"no_sitemap": 0, "novos_ou_alterados": 0, "lidos": 0}}
    vistos = est.setdefault("vistos", {})
    try:
        r = _get(rede, site["url"], site, ctx, condicional=not est.get("fila"), aceitar="application/xml, text/xml, */*")
        res["lidas"] += 1
        if not r.nao_mudou:
            entradas = [(u, lm) for u, lm in _sitemap(r.texto()) if (site.get("prefixo") or "/") in urlsplit(u).path]
            res["diag"]["no_sitemap"] = len(entradas)
            fila = [(u, lm) for u, lm in entradas if vistos.get(u) != (lm or "sem-data")]
            fila.sort(key=lambda x: x[1] or "", reverse=True)                 # o mais recente primeiro
            est["fila"] = [u for u, _ in fila]
            est["lastmod"] = {u: lm for u, lm in fila}
    except Bloqueio as b:
        if b.tipo != "orcamento":
            res["falhas"].append(_falha(site["url"], b))
        if not est.get("fila"):
            return res
    cartoes = _listagens_de_cartoes(site, rede, est, ctx, res)
    fila = list(est.get("fila") or [])
    res["diag"]["novos_ou_alterados"] = len(fila)
    cota, feitos = _cota(site, ctx), 0
    host = urlsplit(site["url"]).hostname or ""
    while fila and feitos < cota:
        u = fila[0]
        try:
            txt, links, tit_pag, objs = _artigo(rede, u, site, ctx)
        except Bloqueio as b:
            if b.tipo == "orcamento":
                break
            res["falhas"].append(_falha(u, b))
            fila.pop(0)
            if b.tipo in ("robots", "geo", "waf"):
                break
            continue
        fila.pop(0); feitos += 1; res["lidas"] += 1; res["diag"]["lidos"] += 1
        lm = (est.get("lastmod") or {}).get(u) or "sem-data"
        vistos[u] = lm
        migalha = X.de_tipo(objs, "BreadcrumbList")
        oficial_nome = None
        if migalha:
            els = migalha[0].get("itemListElement") or []
            if els:
                oficial_nome = X.limpar((els[-1] or {}).get("name"), 300)
        art = (X.de_tipo(objs, "Article", "NewsArticle", "Event", "GovernmentService") or [{}])[0]
        titulo = oficial_nome or art.get("headline") or art.get("name") or tit_pag
        descricao = X.limpar(art.get("description"), 600)
        base_txt = f"{descricao}\n{txt}"
        ref = ctx["hoje"]
        try:
            pub = (art.get("datePublished") or "")[:10]
            ref = min(ctx["hoje"], date.fromisoformat(pub)) if pub else ctx["hoje"]
        except ValueError:
            pass
        c = cartoes.get(u) or {}
        if c.get("prazo"):
            pz = c["prazo"]                               # campo estruturado do cartão da listagem
        elif site.get("prazo_no_texto", True):
            pz = X.prazo(descricao, ref) or X.prazo(txt, ref)
        else:
            pz = None                                     # o texto do guia tem datas ilustrativas: prazo fica para a fonte oficial
        oficial = X.oficial(u, links, titulo, [host])
        perfil_txt = f"{('Aceita: ' + c['publico']) if c.get('publico') else ''}\n{base_txt}"
        res["itens"].append(item(site, ctx, titulo=titulo or c.get("titulo"), pagina=u, link_oficial=oficial, prazo=pz,
                                 financiador=c.get("financiador"), valor=X.valor(base_txt),
                                 uf=X.uf(titulo) or X.uf(c.get("financiador") or "") or X.uf(base_txt[:2500]),
                                 resumo=descricao or txt[:300], publicado=art.get("datePublished"),
                                 texto_perfil=perfil_txt[:5000], extra=_extra_cartao(c)))
        if c:
            est.setdefault("cartao_emitido", {})[u] = _assinatura_cartao(c)
    # cartões novos ou alterados de páginas que não couberam nesta rodada (ou já lidas): indício imediato com o
    # prazo do cartão; o id é o da página, então a leitura da página depois só completa o link oficial
    emitidos = est.setdefault("cartao_emitido", {})
    for u, c in cartoes.items():
        sig = _assinatura_cartao(c)
        if emitidos.get(u) == sig or not c.get("titulo"):
            continue
        emitidos[u] = sig
        res["itens"].append(item(site, ctx, titulo=c["titulo"], pagina=u, prazo=c.get("prazo"), financiador=c.get("financiador"),
                                 uf=X.uf(c["titulo"]) or X.uf(c.get("financiador") or ""),
                                 texto_perfil=f"Aceita: {c.get('publico') or ''}",
                                 extra=_extra_cartao(c)))
        res["diag"]["cartoes_emitidos"] = res["diag"].get("cartoes_emitidos", 0) + 1
    _podar(emitidos, 5000)
    est["fila"] = fila
    res["pendente"] = bool(fila)
    _podar(vistos, 5000)
    return res


def _assinatura_cartao(c: dict) -> str:
    return (f"{c.get('titulo') or ''}|{c.get('prazo') or ''}|{c.get('financiador') or ''}|{int(bool(c.get('continuo')))}|"
            f"{c.get('indireta') or ''}")


def _listagens_de_cartoes(site, rede, est, ctx, res) -> dict:
    """Listagens com cartões estruturados (CapitaAI: /editais-abertos/<segmento>, 84 páginas no sitemap-editais.xml):
    lê `listas_por_rodada` delas em rodízio e guarda {página do item: cartão}. O cartão traz órgão, público e PRAZO."""
    if not site.get("listas_sitemap"):
        return dict(est.get("cartoes") or {})
    hoje = ctx["hoje"].isoformat()
    if est.get("listas_em") != hoje or not est.get("listas"):
        try:
            r = _get(rede, site["listas_sitemap"], site, ctx, condicional=False, aceitar="application/xml, text/xml, */*")
            res["lidas"] += 1
            pref = site.get("listas_prefixo") or "/"
            urls = [u for u, _ in _sitemap(r.texto()) if urlsplit(u).path.startswith(pref)]
            if site.get("pagina") and site["pagina"] not in urls:
                urls.insert(0, site["pagina"])
            ant = [u for u in (est.get("listas") or []) if u in urls]
            est["listas"] = ant + [u for u in urls if u not in ant]
            est["listas_em"] = hoje
        except Bloqueio as b:
            if b.tipo != "orcamento":
                res["falhas"].append(_falha(site["listas_sitemap"], b))
    fixas = dict(site.get("listas_fixas") or {})          # {listagem: site fechado que ela cobre} — lidas em TODA rodada
    listas = [u for u in (est.get("listas") or []) if u not in fixas]
    cart = est.setdefault("cartoes", {})
    lidas = 0
    rodizio = [listas.pop(0) for _ in range(min(len(listas), int(site.get("listas_por_rodada") or 12)))]
    listas.extend(rodizio)                                 # rodízio: as lidas vão para o fim da fila
    for lista in list(fixas) + rodizio:
        try:
            r = _get(rede, lista, site, ctx, condicional=False)
        except Bloqueio as b:
            if b.tipo == "orcamento":
                break
            res["falhas"].append(_falha(lista, b))
            if b.tipo in ("robots", "geo", "waf"):
                break
            continue
        res["lidas"] += 1; lidas += 1
        for u, c in X.cartoes(r.texto(), lista, site.get("prefixo") or "/").items():
            ant = cart.get(u) or {}
            cart[u] = {k: (v if v not in (None, "") else ant.get(k)) for k, v in c.items()} | {"visto": hoje}
            if fixas.get(lista) or ant.get("indireta"):
                cart[u]["indireta"] = fixas.get(lista) or ant.get("indireta")
    est["listas"] = listas
    corte = (ctx["hoje"] - timedelta(days=45)).isoformat()
    for u in [u for u, c in cart.items() if (c.get("visto") or "") < corte or (c.get("prazo") and c["prazo"] < corte)]:
        del cart[u]
    res["diag"]["listagens_lidas"] = lidas
    res["diag"]["cartoes"] = len(cart)
    res["diag"]["cartoes_com_prazo"] = sum(1 for c in cart.values() if c.get("prazo"))
    for tag in set(fixas.values()):
        res["diag"][f"cartoes_rota_indireta_{tag}"] = sum(1 for c in cart.values() if c.get("indireta") == tag)
    return dict(cart)


def _extra_cartao(c: dict) -> dict | None:
    ex = {}
    if c.get("continuo"):
        ex["prazo_continuo"] = True
    if c.get("indireta"):
        ex["rota_indireta_de"] = c["indireta"]            # edital de site fechado a robôs, achado pela rota indireta
    return ex or None


# ------------------------------------------------------------------ L4: listagem HTML + página do item
_NAV = re.compile(r"/(login|entrar|cadastro|cadastre|planos?|blog|sobre|quem-somos|contato|privacidade|termos|faq|imprensa|"
                  r"wp-login|feed|tag|categoria|category|author|autor)(/|$)|#|\.(jpg|png|gif|svg|css|js)$", re.I)


def ler_html_listagem(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"lista": None, "links": 0, "novos": 0}}
    padrao = re.compile(site.get("padrao_link") or X.EDITAL.pattern, re.I)
    listas = list(site.get("listas") or [site.get("url")])
    if est.get("lista_ok") in listas:
        listas.remove(est["lista_ok"]); listas.insert(0, est["lista_ok"])
    links, lista_ok = [], None
    for lista in listas:
        try:
            r = _get(rede, lista, site, ctx, condicional=False)
        except Bloqueio as b:
            res["falhas"].append(_falha(lista, b))
            if b.tipo in ("orcamento", "robots", "geo", "waf"):
                break
            continue
        res["lidas"] += 1
        p = X.pagina(r.texto())
        hosts_ok = {urlsplit(x).hostname for x in (site.get("listas") or []) if x} | {urlsplit(r.url_final).hostname}
        for h, t in p.links:
            u = re.sub(r"[?&]_authenticator=[^&#]*", "", urljoin(r.url_final, h or "")).split("#")[0]
            hu = urlsplit(u).hostname
            if not u.startswith("http") or hu not in hosts_ok or _NAV.search(u) or u.rstrip("/") in (lista.rstrip("/"), r.url_final.rstrip("/")):
                continue
            if padrao.search(u) or padrao.search(t or ""):
                links.append((u, t))
        lista_ok = lista
        if site.get("pagina_unica"):                    # o próprio endereço é a página do edital vigente
            txt = X.texto_de(r.texto())
            tit = p.meta.get("og:title") or p.h1 or p.titulo
            if X.EDITAL.search(txt[:5000]):
                res["itens"].append(item(site, ctx, titulo=tit, pagina=r.url_final, link_oficial=r.url_final, prazo=X.prazo(txt, ctx["hoje"]),
                                         valor=X.valor(txt), resumo=txt[:300], texto_perfil=txt[:5000], financiador=site.get("financiador"),
                                         publicado=p.meta.get("article:modified_time") or p.meta.get("article:published_time")))
            links = []
        break
    if lista_ok:
        est["lista_ok"] = lista_ok
        res["diag"]["lista"] = lista_ok
    vistos = est.setdefault("vistos", {})
    unicos = list(dict.fromkeys(u for u, _ in links))
    rotulo = {u: t for u, t in links}
    res["diag"]["links"] = len(unicos)
    hoje = ctx["hoje"]
    revisar = (hoje - timedelta(days=14)).isoformat()
    novos = [u for u in unicos if not vistos.get(u) or vistos[u] < revisar]
    cota, feitos = _cota(site, ctx), 0
    host_lista = urlsplit(lista_ok or "").hostname or ""
    for u in novos:
        if feitos >= cota or rede.esgotado():
            res["pendente"] = True; break
        try:
            txt, ls, tit, objs = _artigo(rede, u, site, ctx)
            feitos += 1; res["lidas"] += 1
        except Bloqueio as b:
            if b.tipo == "orcamento":
                res["pendente"] = True; break
            res["falhas"].append(_falha(u, b))
            txt, ls, tit, objs = "", [], rotulo.get(u) or "", []
        vistos[u] = hoje.isoformat()
        ev = (X.de_tipo(objs, "Event", "Article", "GovernmentService", "WebPage") or [{}])[0]
        titulo = ev.get("name") or ev.get("headline") or tit or rotulo.get(u) or ""
        if len(titulo.split()) < 2 or not (X.EDITAL.search(titulo) or X.EDITAL.search(txt[:3000])):
            continue
        if _RESULTADO.search(titulo):                   # resultado, lista de aprovados: não é oportunidade
            continue
        pz = (ev.get("endDate") or "")[:10] or X.prazo(txt, hoje)
        oficial = u if site.get("proprio") else (ev.get("sameAs") if isinstance(ev.get("sameAs"), str) else None) or X.oficial(u, ls, titulo, [host_lista])
        res["itens"].append(item(site, ctx, titulo=titulo, pagina=u, link_oficial=oficial, prazo=pz, valor=X.valor(txt),
                                 uf=X.uf(titulo) or X.uf(txt[:2000]), resumo=txt[:300], texto_perfil=txt[:5000],
                                 financiador=site.get("financiador"),
                                 publicado=ev.get("datePublished") or ev.get("dateModified") or ev.get("startDate")))
        res["diag"]["novos"] += 1
    _podar(vistos, 1500)
    return res


# ------------------------------------------------------------------ L5: dados abertos (Siconv — programas)
def _col(cab: list[str], *partes: str) -> str | None:
    for c in cab:
        n = X.norm(c).replace(" ", "_")
        if all(p in n for p in partes):
            return c
    return None


def ler_siconv_zip(site, rede, est, ctx) -> dict:
    res = {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "diag": {"linhas": 0, "programas_abertos": 0, "colunas": None}}
    try:
        r = _get(rede, site["url"], site, ctx, condicional=True, aceitar="application/zip, */*")
    except Bloqueio as b:
        res["falhas"].append(_falha(site["url"], b)); return res
    res["lidas"] += 1
    if r.nao_mudou:
        res["diag"]["nao_mudou"] = True
        return res
    try:
        z = zipfile.ZipFile(io.BytesIO(r.corpo))
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        bruto = z.read(nome)
    except Exception as e:
        res["falhas"].append({"url": site["url"], "tipo": "http", "detalhe": f"zip ilegível: {type(e).__name__}", "status": r.status}); return res
    for enc in ("utf-8-sig", "latin-1"):
        try:
            txt = bruto.decode(enc); break
        except UnicodeDecodeError:
            continue
    delim = ";" if txt[:2000].count(";") >= txt[:2000].count(",") else ","
    leitor = csv.DictReader(io.StringIO(txt), delimiter=delim)
    cab = leitor.fieldnames or []
    c = {"cod": _col(cab, "cod", "programa"), "nome": _col(cab, "nome", "programa"), "orgao": _col(cab, "desc", "orgao"),
         "sit": _col(cab, "sit", "programa"), "fim": _col(cab, "fim", "receb"), "ini": _col(cab, "ini", "receb"),
         "fim_esp": _col(cab, "fim", "benef", "esp"), "fim_em": _col(cab, "fim", "emenda"), "nat": _col(cab, "natureza"),
         "uf": _col(cab, "uf", "programa"), "mod": _col(cab, "modalidade")}
    res["diag"]["colunas"] = {k: v for k, v in c.items() if v}
    if not (c["cod"] and c["nome"] and (c["fim"] or c["fim_esp"])):
        res["falhas"].append({"url": site["url"], "tipo": "formato", "detalhe": "colunas não reconhecidas: " + ", ".join(cab[:30]), "status": r.status})
        return res
    hoje = ctx["hoje"].isoformat()
    progs: dict = {}

    def dia(v):
        v = str(v or "").strip()
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", v) or None
        if m:
            return v[:10]
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", v)
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None

    for lin in leitor:
        res["diag"]["linhas"] += 1
        fins = [dia(lin.get(c[k])) for k in ("fim", "fim_esp") if c.get(k)]
        fins = [f for f in fins if f and f >= hoje]
        if not fins:
            continue
        if c["sit"] and lin.get(c["sit"]) and not re.search(r"dispon|aberto|ativ", lin[c["sit"]], re.I):
            continue
        nat = lin.get(c["nat"]) if c["nat"] else ""
        cod = (lin.get(c["cod"]) or "").strip()
        p = progs.setdefault(cod, {"nome": lin.get(c["nome"]), "orgao": lin.get(c["orgao"]) if c["orgao"] else None,
                                   "fim": max(fins), "naturezas": set(), "ufs": set(), "mod": lin.get(c["mod"]) if c["mod"] else None})
        p["fim"] = max(p["fim"], *fins)
        if nat:
            p["naturezas"].add(nat.strip())
        if c["uf"] and lin.get(c["uf"]):
            p["ufs"].add(lin[c["uf"]].strip())
    for cod, p in progs.items():
        nats = " ".join(sorted(p["naturezas"]))
        if nats and not re.search(r"privad|sem fins|sociedade civil|osc|entidade", nats, re.I):
            continue                                            # programa só para órgão público
        ufs = sorted(x for x in p["ufs"] if x in X.UFS)
        res["itens"].append(item(site, ctx, titulo=f"{X.limpar(p['nome'], 220)} (programa {cod})", pagina=f"{site['pagina']}#programa-{cod}",
                                 prazo=p["fim"], financiador=p["orgao"], uf=ufs[0] if len(ufs) == 1 else None, tipo=p["mod"],
                                 texto_perfil=f"{p['nome']} {nats}",
                                 extra={"codigo_programa": cod, "naturezas_aceitas": sorted(p["naturezas"])[:6] or None,
                                        "consulta_publica": site.get("pagina")}))
        res["diag"]["programas_abertos"] += 1
    return res


# ------------------------------------------------------------------ delegado: motor existente lê o site
def ler_delegado(site, rede, est, ctx) -> dict:
    s = ((ctx.get("estado_motores") or {}).get("sensores") or {}).get(site.get("delegado_a")) or {}
    return {"itens": [], "falhas": [], "lidas": 0, "pendente": False, "delegado": True,
            "diag": {"delegado_a": site.get("delegado_a"), "ultima": s.get("ultima"), "achados_ultima": s.get("achados_ultima"),
                     "achados_total": s.get("achados_total")}}


LEITORES = {"feed": ler_feed, "wordpress": ler_wordpress, "farol_api": ler_farol_api, "mapas_culturais": ler_mapas_culturais,
            "transferegov_api": ler_transferegov_api, "prosas_api": ler_prosas_api, "sitemap_jsonld": ler_sitemap_jsonld, "html_listagem": ler_html_listagem,
            "siconv_zip": ler_siconv_zip, "delegado": ler_delegado}
