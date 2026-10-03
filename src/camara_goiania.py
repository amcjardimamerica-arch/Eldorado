"""MOTOR 05 — Câmara Municipal de Goiânia (versão 2, 01/10/2026).

Parecer do conselho: docs/pareceres/motor-05-camara-goiania.md. O que o motor antigo fazia e por que rendia zero:

1. Lia a home do portal (Plone), o RSS, o SAPL e páginas de transparência. A home vem com o menu e sem lista de
   proposições; `/feed/` e `/diario-oficial` dão 404 (o RSS do Plone é `/RSS`); `sapl.goiania.go.leg.br` responde com
   certificado inválido e não é o sistema em uso; `/transparencia/licitacoes-e-contratos` só tem contratos da própria
   Câmara. 40 leituras, 0 achados e 3 a 5 falhas todos os dias de setembro.
2. As proposições estão no SUAP da Câmara (`suap.camaragyn.go.gov.br/camara/consulta_publica/`, o "Processos
   Eletrônicos" do Portal da Transparência): cada projeto de lei tem número, assunto, autor, setor atual, data e,
   na página do processo, a lista de documentos (parecer jurídico, despachos, votação) com data.
3. O que a Câmara produz para uma OSC quase nunca é edital: é HABILITAÇÃO (lei de utilidade pública municipal),
   leis que criam programas, fundos, isenções e parcerias com entidades, emendas impositivas dos vereadores e,
   raramente, um chamamento da própria Câmara. O motor procurava "edital" no rótulo de links e não via nada disso —
   nem o Projeto de Lei nº 288/2026, que declara de utilidade pública a própria A.M.C. Jardim América.

Como funciona agora (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — SUAP, consulta pública de processos legislativos, por assunto (utilidade pública, entidade, associação,
            fundo, subvenção, programa, isenção, emenda, parceria, doação, sociedade civil…), do mais novo ao mais
            antigo, até sair da janela de dias.
  Fonte B — os processos da PRÓPRIA associação (pelos nomes em config), com a lista de documentos e datas: o motor
            avisa quando a tramitação anda (parecer, despacho, votação, sanção).
  Fonte C — notícias do portal da Câmara (`/search_rss` do Plone): chamamentos, editais, doações e programas.
  → cada item vira OPORTUNIDADE (chamamento/edital aberto para OSC, com prazo), ACOMPANHAR (utilidade pública da
    associação, lei de fomento/parceria/isenção para entidades, emenda impositiva, tema do bairro) ou RUÍDO
    (denominação de rua, título honorífico, data comemorativa, concurso público…), sempre com o motivo escrito;
  → as declarações de utilidade pública vão para a lista de HABILITAÇÃO (entidade, número do projeto, vereador).

Os portais da Câmara (`camaragyn.go.gov.br`, `goiania.go.leg.br`) recusam IP estrangeiro: no GitHub o motor tenta e,
se nada responder, registra "aguardando coleta local"; a leitura completa é a do computador do titular
(`scripts/coleta_brasil.py`). Conteúdo coletado é DADO: injeção → quarentena; o que a fonte não diz fica `null`.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from urllib import robotparser
from datetime import date, datetime, timedelta
from urllib.parse import quote, urlencode, urlsplit

from . import atos_diario as atos
from .nucleo import (ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256,
                     validate_public_https, write_json)

MOTOR_ID = "camara-goiania-pl"
CFG = ROOT / "config/camara_goiania.json"
ESTADO = ROOT / "estado/camara_goiania.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
_PRAZO = {"ate": None}


def _hoje_real() -> date:
    return date.today()


def _tempo_esgotado() -> bool:
    return _PRAZO["ate"] is not None and time.monotonic() > _PRAZO["ate"]


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _N(t) -> str:
    return re.sub(r"\s+", " ", atos.sem_acento(str(t or "")).upper()).strip()


def _limpo(t) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", str(t or "")))).strip()


# ─────────────────────────── rede ───────────────────────────
class Recusa(RuntimeError):
    """Conexão recusada/derrubada ou 403 — o padrão dos portais que só aceitam IP brasileiro."""


def _get_texto(url: str, timeout: int = 25, max_bytes: int = 4_000_000) -> str:
    from urllib.error import HTTPError, URLError
    from urllib.request import HTTPRedirectHandler, Request, build_opener

    class _Redir(HTTPRedirectHandler):                     # destino de cada redirecionamento também é checado
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            validate_public_https(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    validate_public_https(url)
    # 03/10 (titular): DIRETO PRIMEIRO, com as cadeias de certificado que o site não envia (SUAP: src/certificados.py);
    # a ponte da Hostgator fica de RESERVA — só entra se a leitura direta for recusada ou falhar.
    try:
        return _direto(url, timeout, max_bytes, _Redir)
    except Exception as exc_direto:  # noqa: BLE001
        from . import ponte_brasil
        if ponte_brasil.usar(url):
            try:
                return ponte_brasil.texto(url, timeout=timeout, max_bytes=max_bytes)
            except Exception as exc:  # noqa: BLE001
                raise Recusa(f"direto: {str(exc_direto)[:80]} · pela ponte Brasil: {str(exc)[:80]}") from exc
        raise


def _direto(url: str, timeout: int, max_bytes: int, _Redir) -> str:
    from urllib.error import HTTPError, URLError
    from urllib.request import HTTPSHandler, Request, build_opener
    from .certificados import contexto
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    try:
        with build_opener(_Redir(), HTTPSHandler(context=contexto())).open(req, timeout=timeout) as r:
            dados = r.read(max_bytes + 1)
            cs = r.headers.get_content_charset() or "utf-8"
    except HTTPError as exc:
        if exc.code == 403:
            raise Recusa("HTTP 403 — acesso negado (padrão de bloqueio de IP estrangeiro)") from exc
        raise
    except (URLError, ConnectionError) as exc:
        motivo = getattr(exc, "reason", exc)
        if "CERTIFICATE" in str(motivo).upper() or type(motivo).__name__.startswith("SSL"):
            raise RuntimeError(f"certificado do site inválido ({type(motivo).__name__}) — não é recusa de IP") from exc
        if type(motivo).__name__ in ("gaierror", "TimeoutError", "timeout"):
            raise RuntimeError(f"{'endereço não resolve (DNS)' if type(motivo).__name__ == 'gaierror' else 'tempo esgotado'}") from exc
        raise Recusa(f"conexão recusada ou derrubada ({type(motivo).__name__})") from exc
    if len(dados) > max_bytes:
        raise ValueError(f"resposta maior que {max_bytes // 1_000_000} MB")
    return dados.decode(cs, "replace")


def _erro(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    causa = (str(exc) if isinstance(exc, Recusa) else
             "tempo esgotado" if "Timeout" in nome or "timed out" in str(exc) else
             "endereço não resolve (DNS)" if nome == "gaierror" else f"HTTP {code}" if code else nome)
    return f"{causa}"[:160]


class ProibidoRobots(RuntimeError):
    """O robots.txt do site proíbe a leitura automática deste endereço (03/10/2026: o SUAP da Câmara — `Disallow: /`)."""


_ROBOTS: dict = {}
AGENTE_ROBOTS = "Eldorado-OSC"


def robots_permite(url: str, cfg: dict | None = None) -> bool:
    """03/10 (teste do motor 04): o motor passa a CONSULTAR E RESPEITAR o robots.txt de cada host antes de ler.
    `config/camara_goiania.json › robots.proibe_hosts` guarda o que foi medido (vale mesmo se o robots não abrir);
    robots ilegível = permitido (mesma regra de nucleo.robots_permite)."""
    host = (urlsplit(url).hostname or "").lower()
    if host in {h.lower() for h in ((cfg or {}).get("robots") or {}).get("proibe_hosts", [])}:
        return False
    if host not in _ROBOTS:
        rp = robotparser.RobotFileParser()
        try:
            rp.parse(_get_texto(f"https://{host}/robots.txt", timeout=15, max_bytes=200_000).splitlines())
        except Exception:  # noqa: BLE001
            rp = None
        _ROBOTS[host] = rp
    rp = _ROBOTS[host]
    return True if rp is None else rp.can_fetch(AGENTE_ROBOTS, url)


def _get(url: str, cfg: dict, fonte: dict) -> str:
    if not robots_permite(url, cfg):
        raise ProibidoRobots(f"o robots.txt de {urlsplit(url).hostname} proíbe a leitura automática")
    ritmo = cfg.get("ritmo", {})
    ultimo = None
    for _ in range(2):
        if _tempo_esgotado():
            raise RuntimeError("prazo da execução esgotado — o restante fica para a próxima passagem")
        try:
            t = _get_texto(url)
            fonte["consultas"] += 1
            fonte["bytes"] = fonte.get("bytes", 0) + len(t)
            time.sleep(float(ritmo.get("pausa_segundos", 1.0)))
            return t
        except Recusa as exc:                              # recusa não melhora na segunda tentativa
            ultimo = exc; break
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            if getattr(exc, "code", None) in (400, 401, 404) or isinstance(exc, ValueError):
                break
            time.sleep(float(ritmo.get("espera_erro_segundos", 4)))
    if isinstance(ultimo, Recusa):
        raise ultimo
    raise RuntimeError(_erro(ultimo))


# ─────────────────────────── Fonte A: SUAP, consulta pública ───────────────────────────
_ABRE_CAIXA = r"""<div\s[^>]*class=["'][^"']*\bgeneral-box\b[^"']*["'][^>]*>"""
_CAIXA = re.compile(_ABRE_CAIXA + r"(.*?)(?=" + _ABRE_CAIXA + r"""|<ul\s[^>]*class=["'][^"']*pagination|</main>|$)""", re.S)
_TITULO = re.compile(r"""<h3\b[^>]*class=["'][^"']*\btitle\b[^>]*>\s*<a\b[^>]*href=["']([^"']+)["'][^>]*>\s*(.*?)\s*</a>""", re.S)
_ASSUNTO = re.compile(r"<dt\b[^>]*>\s*Assunto:\s*</dt>\s*<dd\b[^>]*>(.*?)</dd>", re.S)
_CAMPO = re.compile(r"<dt\b[^>]*>(?:\s*<(?:span|i)\b[^>]*>\s*</(?:span|i)>)?\s*([^<:]+?):\s*</dt>\s*<dd\b[^>]*>(.*?)</dd>", re.S)
_SITUACAO = re.compile(r"""<span\b[^>]*class=["'][^"']*\bstatus-([a-z-]+)[^"']*["'][^>]*>([^<]+)</span>""")
_TOTAL = re.compile(r"Total de\s*([\d.]+)\s*ite")


def _data_br(s: str) -> str | None:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return None


def processos_da_pagina(html: str, base: str) -> tuple[list[dict], int | None]:
    """Página de resultado da consulta pública → (processos, total de itens)."""
    out = []
    for bloco in _CAIXA.findall(html or ""):
        t = _TITULO.search(bloco)
        if not t:
            continue
        campos = {_N(k): _limpo(v) for k, v in _CAMPO.findall(bloco)}
        situ = [_limpo(x[1]) for x in _SITUACAO.findall(bloco)]
        a = _ASSUNTO.search(bloco)
        assunto = atos.mascarar_pii(_limpo(a.group(1)) if a else campos.get("ASSUNTO", ""))
        num = re.search(r"(Projeto de (?:Lei(?: Complementar)?|Resolu[çc][ãa]o|Decreto Legislativo|Emenda[^º°\d]{0,40})|"
                        r"P\.?\s?L\.?|Requerimento[^º°\d]{0,20}|Of[íi]cio|Emenda[^º°\d]{0,40}|Veto[^º°\d]{0,20})\s*"
                        r"(?:n[º°o.]*|N[º°O.]*)\s*(\d[\d./]*\d|\d)", assunto, re.I)
        href = _html.unescape(t.group(1))
        dono = urlsplit(base).hostname
        if href.startswith("//") or (urlsplit(href).hostname and urlsplit(href).hostname != dono):
            continue                                            # link para outro host não é seguido
        out.append({
            "fonte": "A", "processo": _limpo(t.group(2)).replace("Processo ", "").strip(),
            "url": (base.rstrip("/") + href) if href.startswith("/") else href,
            "assunto": assunto, "tipo_documento": (num.group(1).strip() if num else None),
            "numero": (num.group(2).strip(" ./") if num else None),
            "autor": atos.mascarar_pii(campos.get("INTERESSADOS") or "") or None, "setor": campos.get("SETOR ATUAL") or None,
            "tipo": campos.get("TIPO") or None, "criado": _data_br(campos.get("DATA DE CRIACAO", "")),
            "situacao": next((s for s in situ if s.lower() not in ("público", "publico", "restrito", "sigiloso")), None),
            "publico": any(s.lower() in ("público", "publico") for s in situ),
        })
    m = _TOTAL.search(html or "")
    return out, (int(m.group(1).replace(".", "")) if m else None)


def fonte_a(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    a = cfg.get("suap") or {}
    base = a.get("base", "https://suap.camaragyn.go.gov.br").rstrip("/")
    F = diag["fontes"]["A"]
    if a.get("ativa") is False or not robots_permite(f"{base}/camara/consulta_publica/", cfg):
        F["proibido_robots"] = a.get("ativa") is not False
        return []                                               # 03/10: robots.txt do SUAP = Disallow: / (nada é lido)
    janela = int(a.get("janela_dias", 35))
    corte = (hoje - timedelta(days=janela)).isoformat()
    vistos: dict[str, dict] = {}
    anos = sorted({hoje.year, (hoje - timedelta(days=janela)).year})          # em janeiro, também o ano anterior
    max_pag = int(a.get("max_paginas_por_assunto", 4))
    seguidas = 0

    def _dentro():
        d = [p for p in vistos.values() if (p["criado"] or "9999") >= corte]
        F["lidos"], F["itens"] = len(vistos), len(d)            # lidos nas páginas × criados dentro da janela
        return d

    for termo in a.get("assuntos", []):
        for ano in anos:
            for pag in range(1, max_pag + 1):
                q = urlencode({"classificacao": "PL", "assunto": termo, "interessado": "", "numero_protocolo": "",
                               "ano": str(ano), "page": str(pag), "consultapublicaprocesso_form": "Enviar"})
                try:
                    html = _get(f"{base}/camara/consulta_publica/?{q}", cfg, F)
                    seguidas = 0
                except Recusa as exc:
                    if not vistos:
                        raise                                   # o portal recusa este IP: nada vai responder
                    F["falhas"].append(f"{termo}: {exc}")       # recusa no meio (limite): fica o que já foi lido
                    return _dentro()
                except Exception as exc:  # noqa: BLE001
                    F["falhas"].append(f"{termo}: {exc}"); seguidas += 1
                    if seguidas >= int(cfg.get("falhas_seguidas_para_abortar_fonte", 3)):
                        return _dentro()
                    break
                itens, total = processos_da_pagina(html, base)
                if total and not itens:                         # "Total de N itens" sem nenhuma caixa: o HTML mudou
                    F.setdefault("formato_desconhecido", []).append(termo)
                for p in itens:
                    v = vistos.setdefault(p["processo"], dict(p, termos=[]))
                    v["termos"] = sorted(set(v.get("termos", [])) | {termo})
                datas = [p["criado"] for p in itens if p["criado"]]
                fim_da_lista = not itens or (total is not None and pag * 20 >= total) or (total is None and len(itens) < 20)
                if fim_da_lista or (datas and min(datas) < corte):
                    break                                       # a lista vem do mais novo para o mais antigo
                if pag == max_pag:
                    F.setdefault("cortados", []).append(f"{termo}/{ano}")   # mais páginas dentro da janela do que o limite
    return _dentro()


# ─────────────────────────── Fonte B: processos da própria associação ───────────────────────────
_DOC = re.compile(r"""<h3\b[^>]*id=["']__doc_\d+["'][^>]*>\s*(.*?)\s*</h3>\s*(?:<p\b[^>]*class=["'][^"']*\bobs\b[^>]*>\s*(.*?)\s*</p>)?""", re.S)


def documentos_do_processo(html: str) -> tuple[list[dict], int]:
    """Página do processo → ([{titulo, data}], total de itens)."""
    docs = []
    for t, d in _DOC.findall(html or ""):
        tit = atos.mascarar_pii(_limpo(t))[:160]
        if has_prompt_injection(tit):                       # título escrito por terceiro: dado, nunca instrução
            tit = "[título em quarentena]"
        docs.append({"titulo": tit, "data": _data_br(_limpo(d)) if d else None})
    m = _TOTAL.search(html or "")
    return docs, (int(m.group(1).replace(".", "")) if m else len(docs))


def fonte_b(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    a = cfg.get("suap") or {}
    base = a.get("base", "https://suap.camaragyn.go.gov.br").rstrip("/")
    F = diag["fontes"]["B"]
    if a.get("ativa") is False or not robots_permite(f"{base}/camara/consulta_publica/", cfg):
        F["proibido_robots"] = a.get("ativa") is not False
        return []
    proprios: dict[str, dict] = {}
    for nome in (cfg.get("associacao") or {}).get("nomes_no_processo", []):
        q = urlencode({"classificacao": "PL", "assunto": nome, "interessado": "", "numero_protocolo": "", "ano": "",
                       "consultapublicaprocesso_form": "Enviar"})
        try:
            html = _get(f"{base}/camara/consulta_publica/?{q}", cfg, F)
        except Recusa:
            raise
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{nome}: {exc}"); continue
        for p in processos_da_pagina(html, base)[0]:
            proprios.setdefault(p["processo"], dict(p, fonte="B", propria=True))
    for p in proprios.values():
        docs, total, completo = [], 0, True
        for pag in range(1, 6):
            try:
                html = _get(p["url"] + (f"?page={pag}" if pag > 1 else ""), cfg, F)
            except Recusa:
                raise
            except Exception as exc:  # noqa: BLE001
                F["falhas"].append(f"processo {p['processo']}: {exc}"); completo = False; break
            d, total = documentos_do_processo(html)
            docs += d
            if not d or len(docs) >= total:
                break
        p["documentos_completos"] = completo and bool(docs)   # leitura falhou → o estado anterior é mantido
        p["documentos"] = docs
        p["total_documentos"] = total or len(docs)
        datados = [x for x in docs if x["data"]]
        p["ultimo_documento"] = docs[-1]["titulo"] if docs else None
        p["ultima_data"] = max((x["data"] for x in datados), default=None)
    F["itens"] = len(proprios)
    return list(proprios.values())


# ─────────────────────────── Fonte C: notícias do portal (Plone) ───────────────────────────
_RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
_DC = "{http://purl.org/dc/elements/1.1/}"
_RSS1 = "{http://purl.org/rss/1.0/}"


def noticias_do_rss(xml: str) -> list[dict]:
    try:
        raiz = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    except ET.ParseError:
        return []
    out = []
    for it in list(raiz.iter(_RSS1 + "item")) + list(raiz.iter("item")):
        def g(tag):
            e = it.find(tag)
            return (e.text or "").strip() if e is not None and e.text else ""
        tipo = g(_DC + "type")
        out.append({"fonte": "C", "titulo": _limpo(g(_RSS1 + "title") or g("title")), "url": g(_RSS1 + "link") or g("link"),
                    "descricao": _limpo(g(_RSS1 + "description") or g("description")),
                    "publicado": (_dia_iso(g(_DC + "date")) or None), "tipo_conteudo": tipo or None})
    return out


def _dia_iso(s: str) -> str | None:
    m = re.match(r"(\d{4})[-/](\d{2})[-/](\d{2})", s or "")
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError:
        return None


def fonte_c(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("portal") or {}
    if c.get("ativa", True) is False:
        return []
    base = c.get("base", "https://www.goiania.go.leg.br").rstrip("/")
    F = diag["fontes"]["C"]
    corte = (hoje - timedelta(days=int(c.get("janela_dias", 35)))).isoformat()
    vistos: dict[str, dict] = {}
    for termo in c.get("buscas", []):
        try:
            xml = _get(f"{base}/search_rss?SearchableText={quote(termo)}&sort_on=created&sort_order=reverse", cfg, F)
        except Recusa:
            raise
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{termo}: {exc}"); continue
        for n in noticias_do_rss(xml):
            if n["url"] and (n["publicado"] or "") >= corte and (n["tipo_conteudo"] or "").lower() not in ("arquivo", "file", "imagem", "image"):
                vistos.setdefault((_N(n["titulo"]), n["publicado"]), n)      # a mesma notícia sai em mais de uma seção
    F["itens"] = len(vistos)
    return list(vistos.values())


# ─────────────────────────── Fonte D: pautas de projetos do Plenário (PDF no portal) ───────────────────────────
# 03/10 (teste do motor 04): o SUAP proíbe robôs; o portal da Câmara (robots liberado) publica a PAUTA DE PROJETOS de cada
# sessão em PDF, com tipo, número, data de criação, autoria, fase e resumo de cada projeto — utilidade pública, programas,
# fundos, títulos. É a fonte pública e permitida dos processos legislativos. PUBLICADO × LIDO: toda pauta da janela é lida;
# a que falhar vai para `paginas_nao_lidas` e o maestro dispara o motor de novo.
_PAUTA_PDF = re.compile(r"""href=["']([^"']*?/(pauta-de-projetos-(\d{2})-(\d{2})-(\d{4})[^"'/]*?\.pdf))(?:/view)?["']""", re.I)
_TIPO_PROJ = r"Projeto de (?:Lei(?: Complementar)?|Decreto Legislativo|Resolu[çc][ãa]o|Emenda[^\d_]{0,40}?)"
_BLOCO = re.compile(r"(" + _TIPO_PROJ + r")\s+(\d{1,4}/\d{4})\s+Cria[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})(.*?)(?=" + _TIPO_PROJ +
                    r"\s+\d{1,4}/\d{4}\s+Cria|$)", re.S)


def pautas_da_listagem(html: str, base: str) -> list[dict]:
    """Página `processo-legislativo/pautas-de-sessoes` → [{url, arquivo, data}] (uma por arquivo, data do nome do arquivo)."""
    out, vistos = [], set()
    for href, arq, d, m, a in _PAUTA_PDF.findall(html or ""):
        try:
            dia = date(int(a), int(m), int(d)).isoformat()
        except ValueError:
            continue
        url = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        if (urlsplit(url).hostname or "") != (urlsplit(base).hostname or "") or arq.lower() in vistos:
            continue                                            # link para outro host não é seguido
        vistos.add(arq.lower())
        out.append({"url": url.split("/view")[0], "arquivo": arq, "data": dia})
    return sorted(out, key=lambda x: x["data"], reverse=True)


def projetos_da_pauta(texto: str, url: str, data_sessao: str) -> list[dict]:
    """Texto do PDF da pauta → um item por projeto (o mesmo formato das fontes A/B)."""
    t = re.sub(r"\s+", " ", texto or "")
    out = []
    for tipo, num, criacao, corpo in _BLOCO.findall(t):
        fase = re.search(r"Fase:\s*(\S+)", corpo)
        resumo = re.search(r"Resumo:\s*(.*?)(?:\s+Comiss[ãa]o:|\s*_{5,}|$)", corpo)
        autoria = re.search(r"Autoria:\s*(.*?)\s+Fase:", corpo)
        assunto = atos.mascarar_pii(_limpo(resumo.group(1) if resumo else ""))[:600]
        if has_prompt_injection(assunto):
            assunto = "[resumo em quarentena]"
        out.append({"fonte": "D", "processo": f"{tipo.strip()} {num}", "url": url, "assunto": assunto,
                    "tipo_documento": tipo.strip(), "numero": num, "autor": (atos.mascarar_pii(autoria.group(1)) if autoria else None),
                    "criado": _data_br(criacao), "situacao": f"em pauta na sessão de {data_sessao}"
                    + (f" ({fase.group(1).lower()} votação)" if fase and fase.group(1).lower() != "única" else " (votação única)" if fase else ""),
                    "pauta": data_sessao, "setor": "Plenário", "publico": True})
    return out


def _get_bytes(url: str, cfg: dict, fonte: dict, max_bytes: int = 15_000_000) -> bytes:
    """PDF do portal: direto primeiro (cadeia de certificados de src/certificados.py), ponte Brasil de reserva."""
    if not robots_permite(url, cfg):
        raise ProibidoRobots(f"o robots.txt de {urlsplit(url).hostname} proíbe a leitura automática")
    if _tempo_esgotado():
        raise RuntimeError("prazo da execução esgotado — o restante fica para a próxima passagem")
    from urllib.request import HTTPSHandler, Request, build_opener
    from .certificados import contexto
    validate_public_https(url)
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*;q=0.5"})
        with build_opener(HTTPSHandler(context=contexto())).open(req, timeout=40) as r:
            dados = r.read(max_bytes + 1)
    except Exception as exc_direto:  # noqa: BLE001
        from . import ponte_brasil
        if not ponte_brasil.usar(url):
            raise RuntimeError(_erro(exc_direto)) from exc_direto
        st, _f, dados, _h = ponte_brasil.abrir(url, aceitar="application/pdf,*/*;q=0.5", max_bytes=max_bytes)
        if st >= 400:
            raise RuntimeError(f"HTTP {st} pela ponte")
    if len(dados) > max_bytes:
        raise ValueError(f"PDF maior que {max_bytes // 1_000_000} MB")
    fonte["consultas"] += 1
    fonte["bytes"] = fonte.get("bytes", 0) + len(dados)
    time.sleep(float((cfg.get("ritmo") or {}).get("pausa_segundos", 1.0)))
    return dados


def _texto_pdf(dados: bytes) -> str | None:
    from .diario_goiania import texto_do_pdf
    return texto_do_pdf(dados)


def fonte_d(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    p = cfg.get("pautas") or {}
    if not p or p.get("ativa") is False:
        return []
    base = (cfg.get("portal") or {}).get("base", "https://www.goiania.go.leg.br").rstrip("/")
    F = diag["fontes"]["D"]
    corte = (hoje - timedelta(days=int(p.get("janela_dias", 35)))).isoformat()
    try:
        html = _get(base + "/" + p.get("listagem", "processo-legislativo/pautas-de-sessoes").lstrip("/"), cfg, F)
    except ProibidoRobots:
        F["proibido_robots"] = True; return []
    except Exception as exc:  # noqa: BLE001
        F["falhas"].append(f"listagem das pautas: {exc}")
        F["paginas_nao_lidas"] = ["listagem das pautas de projetos"]
        return []
    pautas = [x for x in pautas_da_listagem(html, base) if corte <= x["data"] <= hoje.isoformat()][: int(p.get("max_pautas", 25))]
    F["publicadas"], F["lidas"], F["nao_lidas"] = len(pautas), 0, []
    itens: list[dict] = []
    for x in pautas:                                            # da mais nova para a mais antiga
        try:
            texto = _texto_pdf(_get_bytes(x["url"], cfg, F))
            if texto is None:
                raise RuntimeError("PDF sem texto legível (leitor de PDF ausente ou arquivo de imagem)")
            novos = projetos_da_pauta(texto, x["url"], x["data"])
            if not novos and len(texto) > 500:
                F.setdefault("formato_desconhecido", []).append(x["arquivo"])
            itens += novos; F["lidas"] += 1
        except Exception as exc:  # noqa: BLE001 — uma pauta não derruba as outras
            F["falhas"].append(f"{x['arquivo']}: {str(exc)[:120]}")
            F["nao_lidas"].append(f"pauta de {x['data']} ({x['arquivo']})")
    if F["nao_lidas"]:
        F["paginas_nao_lidas"] = F["nao_lidas"]
    vistos: dict[str, dict] = {}
    for m in itens:                                             # o mesmo projeto em várias pautas: fica a mais recente
        vistos.setdefault(m["processo"], m)
    F["itens"] = len(vistos)
    return list(vistos.values())


# ─────────────────────────── classificação ───────────────────────────
UTILIDADE = re.compile(r"UTILIDADE PUBLICA")
DENOMINACAO = re.compile(r"\bDENOMINA(?:R|CAO)?\b(?: DE)? (?:A |O |AS |OS )?(?:VIA|RUA|AVENIDA|ALAMEDA|PRACA|PARQUE|BOSQUE|VIADUTO|"
                         r"TRAVESSA|RODOVIA|ESCOLA|CENTRO MUNICIPAL|CMEI|UNIDADE|TERMINAL|ESTADIO|GINASIO|AREA PUB|LOGRADOURO|"
                         r"\")|DA NOME|LOGRADOURO|VIA PUBLICA")
RUIDO_TEMA = [
    ("denominação de logradouro ou próprio público", DENOMINACAO),
    ("título honorífico ou homenagem", re.compile(r"TITULO (?:HONORIFICO )?DE CIDADA|CIDADANIA GOIANIENSE|CIDADA[O]? GOIANIENSE|"
                                                  r"COMENDA|HONRA AO MERITO|MEDALHA|"
                                                  r"DIPLOMA DE|SESSAO SOLENE|VOTO DE (?:LOUVOR|APLAUSO|PESAR)|HOMENAGEM")),
    ("data comemorativa no calendário", re.compile(r"INSTITUI (?:O|A) (?:DIA|SEMANA|MES)\b|CALENDARIO OFICIAL|DATA COMEMORATIVA|"
                                                   r"INCLUI NO CALENDARIO")),
    ("concurso público ou pessoal da Câmara", re.compile(r"CONCURSO PUBLICO|CONCURSO/\d{4}|SERVIDORES DA CAMARA|CARGOS? DE PROVIMENTO")),
]
_ENT_PUBLICA = re.compile(r"(?:ORGAOS E |)ENTIDADES? DA ADMINISTRACAO|ENTIDADES? (?:PUBLICAS|DA AREA PUBLICA)|INSTITUTO DE PREVIDENCIA|"
                          r"\bIPSM\b|AUTARQUI|FUNDACOES PUBLICAS|EMPRESAS PUBLICAS")
ENTIDADE = re.compile(r"ENTIDADES?\b|ASSOCIAC(?:AO|OES)|\bOSCS?\b|SOCIEDADE CIVIL|SEM FINS LUCRATIVOS|INSTITUICOES? (?:SEM|FILANTROP|SOCIA)|"
                      r"TERCEIRO SETOR|FILANTROP|COOPERATIVAS?|ORGANIZAC(?:AO|OES) (?:SOCIA|NAO GOVERNAMENTA|COMUNITARIA)|"
                      r"COLETIVOS|INSTITUTOS?\b|FUNDACOES\b|PROJETOS SOCIAIS")
FOMENTO = re.compile(r"SUBVENC|REPASSE|TERMO DE (?:FOMENTO|COLABORACAO)|PARCERIAS?\b|13\.019|MROSC|CHAMAMENTO|FUNDO MUNICIPAL|"
                     r"CRIA (?:O )?FUNDO|INCENTIVO|FOMENTO|ISENC|IMUNIDADE|DOACAO|CESSAO DE USO|COMODATO|CONVENIO|AUXILIO|"
                     r"PREMIO|BOLSA|CREDENCIAMENTO")
PROGRAMA = re.compile(r"INSTITUI (?:O |A )?(?:PROGRAMA|POLITICA|PLANO|PROJETO)|CRIA (?:O |A )?(?:PROGRAMA|POLITICA|CONSELHO)")
REGRA_OSC = re.compile(r"ENTIDADES PARCEIRAS|INSTITUICOES PRIVADAS E ENTIDADES|PARCERIAS? (?:CELEBRADAS|FIRMADAS) COM|"
                       r"ORGANIZACOES DA SOCIEDADE CIVIL|\bOSCS?\b|TERCEIRO SETOR|ENTIDADES (?:SEM FINS|DO TERCEIRO|SOCIAIS|"
                       r"FILANTROP|BENEFICENTES|DE ASSISTENCIA|CONVENIADAS)")
ORCAMENTO = re.compile(r"LEI ORCAMENTARIA|\bLOA\b|\bPLOA\b|ORCAMENTO (?:DE |PARA )?20\d\d|DIRETRIZES ORCAMENTARIAS|\bLDO\b")
EMENDA_IMP = re.compile(r"EMENDAS? IMPOSITIVAS?|EMENDAS? PARLAMENTAR(?:ES)? INDIVIDUA|IMPEDIMENTO DE ORDEM TECNICA")
EDITAL = re.compile(r"\bEDITAL\b|CHAMAMENTO|CHAMADA PUBLICA|INSCRICOES (?:ABERTAS|ATE|VAO|PODEM)|SELECAO DE (?:PROJETOS|ENTIDADES|OSC)|"
                    r"CREDENCIAMENTO DE (?:ENTIDADES|OSC|ASSOCIAC)")
NAO_OSC_EDITAL = re.compile(r"CONCURSO\b|\bBANCA\b|\bVAGAS\b|CANDIDATOS|\bMBA\b|POS-?GRADUACAO|PROCESSO SELETIVO|ESTAGI|PREGAO|"
                            r"LICITAC|SERVIDOR|ESTUDANTES|PARLAMENTO JOVEM|ALUNOS")
PUBLICO_OSC = re.compile(r"ENTIDADES? (?:INTERESSADAS|SEM FINS|SOCIAIS|FILANTROP|BENEFICENTES|DE ASSISTENCIA|DA SOCIEDADE)|\bOSCS?\b|"
                         r"ORGANIZACOES DA SOCIEDADE CIVIL|ASSOCIACOES (?:DE MORADORES|COMUNITARIAS|SEM FINS)|INSTITUICOES SEM FINS|"
                         r"SEM FINS LUCRATIVOS|TERCEIRO SETOR")


def _prazo(texto: str, publicado: str | None) -> tuple[str | None, bool, str | None]:
    from .gife_editais import prazo_do_texto           # o mesmo leitor de prazo do motor 22 ("até 19 de outubro"…)
    return prazo_do_texto(texto, publicado)


def entidade_da_utilidade_publica(assunto: str) -> str | None:
    """"…declara de Utilidade Pública Municipal a Associação X." → "Associação X"."""
    m = re.search(r"utilidade p[úu]blica(?: municipal)?(?:,?\s+no [âa]mbito d[oa] [^,]{3,40},)?,?\s+(?:d[aoe]s?|à|ao|a|o)\s+"
                  r"(.{3,220}?)(?:\.?[\"”]|\.\s*$|\s+e d[áa] outras|$)", (assunto or "").strip(), re.I)
    return m.group(1).strip(" ,;-–\"“”") if m else None


def classificar_item(m: dict, hoje: date, cfg: dict | None = None) -> dict:
    """Um processo (A/B) ou notícia (C) → OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo escrito."""
    cfg = cfg or {}
    nomes = [_N(x) for x in (cfg.get("associacao") or {}).get("nomes", [])]
    bairro = _N((cfg.get("associacao") or {}).get("bairro") or "")
    texto = " ".join(x for x in (m.get("assunto"), m.get("titulo"), m.get("descricao")) if x)
    T = _N(texto)
    TE = _ENT_PUBLICA.sub(" ", T)          # "órgãos e entidades da Administração", "Instituto de Previdência" não são OSC
    projetos = {str(x).strip() for x in (cfg.get("associacao") or {}).get("projetos", [])}
    propria = bool(m.get("propria")) or any(n and n in T for n in nomes) or (str(m.get("numero") or "") in projetos)
    base = {"categoria": None, "regime": None, "motivos": [], "sinais": [], "propria": propria, "fim": None,
            "entidade": None}
    if m.get("fonte") == "C":                                   # notícia
        fim, fluxo, trecho = _prazo(texto, m.get("publicado"))
        base["fim"] = fim
        if EDITAL.search(T) and PUBLICO_OSC.search(T) and not NAO_OSC_EDITAL.search(T):
            if fim and fim >= hoje.isoformat():
                return {**base, "veredito": "OPORTUNIDADE", "categoria": "chamamento", "regime": "chamamento_municipal",
                        "motivos": [f"chamamento ou edital com entidades como público, inscrições até {fim} — conferir o edital"]}
            return {**base, "veredito": "ACOMPANHAR", "categoria": "chamamento", "regime": "chamamento_municipal",
                    "motivos": [f"edital ou chamamento citado em notícia {'encerrado em ' + fim if fim else 'sem prazo no texto'} — conferir"]}
        if (FOMENTO.search(T) or PROGRAMA.search(T) or EMENDA_IMP.search(T)) and ENTIDADE.search(TE):
            return {**base, "veredito": "ACOMPANHAR", "categoria": "noticia_fomento", "regime": "lei_ou_recurso",
                    "motivos": ["notícia de lei, programa ou recurso que envolve entidades — acompanhar a tramitação"]}
        if REGRA_OSC.search(TE):                    # 03/10: lei que muda as regras das parcerias com o terceiro setor
            return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_para_entidades", "regime": "obrigacao_de_parceria",
                    "motivos": ["notícia de lei que muda regras das parcerias com entidades do terceiro setor — afeta a habilitação"]}
        if ORCAMENTO.search(T) or EMENDA_IMP.search(T):   # 03/10: LOA/LDO em tramitação = janela das emendas impositivas
            return {**base, "veredito": "ACOMPANHAR", "categoria": "orcamento_emendas", "regime": "emenda_impositiva",
                    "motivos": ["orçamento do município em tramitação na Câmara — janela das emendas impositivas dos vereadores"]}
        if propria or (bairro and bairro in T):
            return {**base, "veredito": "ACOMPANHAR", "categoria": "bairro", "motivos": ["notícia sobre o Jardim América ou a associação"]}
        return {**base, "veredito": "RUIDO", "motivos": ["notícia sem chamamento, recurso ou entidade"]}
    # processo legislativo (A/B)
    if UTILIDADE.search(T) and not re.search(r"\bDENOMINA\b.{0,40}(?:VIA|RUA|AVENIDA|PRACA|LOGRADOURO)", T):
        ent = entidade_da_utilidade_publica(m.get("assunto") or "")
        base.update({"categoria": "utilidade_publica", "regime": "habilitacao", "entidade": ent})
        if propria:
            ult = f"; último documento: {m['ultimo_documento']} ({m.get('ultima_data') or 's/d'})" if m.get("ultimo_documento") else ""
            return {**base, "veredito": "ACOMPANHAR",
                    "motivos": [f"utilidade pública da própria associação ({m.get('tipo_documento') or 'projeto'} nº {m.get('numero')}, "
                                f"{m.get('situacao') or 'situação não informada'}, setor {m.get('setor') or '—'}){ult}"]}
        return {**base, "veredito": "RUIDO",
                "motivos": [f"utilidade pública de outra entidade ({ent or 'nome não lido'}) — vai para a lista de habilitação"]}
    if propria and not DENOMINACAO.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "propria", "motivos": ["processo que cita a própria associação"]}
    for nome, rx in RUIDO_TEMA:
        if rx.search(T) and not (FOMENTO.search(T) and ENTIDADE.search(TE)):
            return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": [nome]}
    if ORCAMENTO.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "orcamento_emendas", "regime": "emenda_impositiva",
                "motivos": ["projeto de lei orçamentária (LOA/LDO) — janela das emendas impositivas a entidades"]}
    if EMENDA_IMP.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "emenda_impositiva", "regime": "emenda_impositiva",
                "motivos": ["emenda impositiva de vereador — recurso que pode ser destinado a entidade"]}
    if ENTIDADE.search(TE) and (FOMENTO.search(T) or PROGRAMA.search(T)):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "fomento_parceria", "regime": "lei_de_fomento",
                "motivos": ["projeto de lei que cria programa, fundo, isenção, doação ou parceria com entidades — "
                            "pode abrir recurso ou chamamento depois de aprovado"]}
    if REGRA_OSC.search(TE):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_para_entidades", "regime": "obrigacao_de_parceria",
                "motivos": ["projeto que cria regra ou exigência para entidades parceiras do município — afeta a habilitação"]}
    if re.search(r"FUNDO MUNICIPAL|CRIA (?:O )?FUNDO|SUBVENC", T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "fundo", "regime": "fundo_municipal",
                "motivos": ["projeto que cria ou altera fundo municipal ou subvenção — conferir se entidades podem receber"]}
    if bairro and bairro in T:
        return {**base, "veredito": "ACOMPANHAR", "categoria": "bairro", "motivos": ["projeto que trata do Jardim América"]}
    return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["projeto sem entidade, recurso ou parceria"]}


def _chave(m: dict) -> str:
    return ("proc:" + m["processo"]) if m.get("processo") else ("url:" + (m.get("url") or "").split("?")[0].rstrip("/"))


def _registro(c: dict, m: dict) -> dict:
    titulo = m.get("assunto") or m.get("titulo") or ""
    ev = atos.mascarar_pii(" ".join(x for x in (titulo, m.get("descricao")) if x))[:700]
    return {
        "id": sha256(f"cmg|{_chave(m)}".encode())[:20], "status": "capturada",
        "titulo": f"Câmara de Goiânia — {titulo}"[:300], "url": m.get("url"), "fonte_id": MOTOR_ID,
        "fonte_nome": "Câmara Municipal de Goiânia" + (" — notícia" if m.get("fonte") == "C" else " — processo legislativo"),
        "territorio": "GO/Goiânia", "uf": "GO", "nivel": "municipal", "municipio": "GO/Goiânia",
        "tipo_fonte": "legislativo_municipal", "confianca": "primaria" if m.get("fonte") in ("A", "B") else "secundaria",
        "forma_divulgacao": "suap_camara" if m.get("fonte") in ("A", "B") else "portal_camara",
        "coletado_em": now_iso(), "data_publicacao": m.get("criado") or m.get("publicado"), "fim": c.get("fim"),
        "prazo_texto": c.get("fim"), "processo": m.get("processo"), "numero": m.get("numero"),
        "tipo_documento": m.get("tipo_documento"), "autor": m.get("autor"), "setor": m.get("setor"), "situacao": m.get("situacao"),
        "regime": c.get("regime"), "categoria": c.get("categoria"), "entidade": c.get("entidade"), "propria": c.get("propria"),
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()),
        "classificacao_ato": {"veredito": c["veredito"], "regime": c.get("regime"), "motivos": c["motivos"], "sinais": c["sinais"],
                              "tipo": "abertura" if c["veredito"] == "OPORTUNIDADE" else "tramitacao"},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def classificar_lote(itens: list[dict], hoje: date, cfg: dict | None = None) -> tuple[dict, dict, list, dict]:
    """→ ({id: OPORTUNIDADE}, {id: ACOMPANHAR}, [utilidade pública de outras entidades], contagens)."""
    oport, acomp, habilitacao = {}, {}, []
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0, "erros": 0}
    vistos: dict[str, dict] = {}
    for m in sorted(itens, key=lambda x: x.get("fonte") != "B"):          # B (própria, com documentos) primeiro
        vistos.setdefault(_chave(m), m)
    for m in vistos.values():
        bruto = " ".join(str(m.get(k) or "") for k in ("assunto", "titulo", "descricao"))
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1
            continue
        try:
            c = classificar_item(m, hoje, cfg)
            cont[c["veredito"]] += 1
            if c["categoria"] == "utilidade_publica" and not c["propria"]:
                habilitacao.append({"entidade": c["entidade"], "projeto": f"{m.get('tipo_documento') or 'Projeto'} nº {m.get('numero')}",
                                    "autor": m.get("autor"), "criado": m.get("criado"), "situacao": m.get("situacao"),
                                    "setor": m.get("setor"), "url": m.get("url"), "processo": m.get("processo")})
            if c["veredito"] == "RUIDO":
                continue
            r = _registro(c, m)
            if m.get("documentos") is not None:
                r["documentos"] = m["documentos"][-12:]
                r["ultimo_documento"], r["ultima_data"] = m.get("ultimo_documento"), m.get("ultima_data")
        except Exception:  # noqa: BLE001 — um item malformado não derruba o lote
            cont["erros"] += 1
            continue
        (oport if c["veredito"] == "OPORTUNIDADE" else acomp)[r["id"]] = r
    return oport, acomp, habilitacao, cont


# ─────────────────────────── o motor ───────────────────────────
def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 05 com a mesma saída de `sensores.ler`."""
    pedido = hoje or (sensor or {}).get("_data")
    hoje = _hoje_real() if pedido is None else pedido
    vazio = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0}
    if pedido is not None and pedido < _hoje_real():
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                "diagnostico": {**vazio, "motivo_zero": "o motor 05 lê a tramitação de hoje; dia passado não é relido",
                                "retroativo": True}}
    cfg = _cfg()
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 300))
    diag = {**vazio, "motivo_zero": None, "versao": "motor-05 v2 (01/10/2026)",
            "fontes": {k: {"falhas": [], "consultas": 0, "itens": 0} for k in ("A", "B", "C", "D")}}
    itens, recusas = [], []
    for nome, fn in (("B", fonte_b), ("A", fonte_a), ("D", fonte_d), ("C", fonte_c)):   # B primeiro: a associação nunca fica sem leitura
        try:
            itens += fn(hoje, cfg, diag)
        except Recusa as exc:
            recusas.append(f"{nome}: {exc}"); diag["fontes"][nome]["falhas"].append(str(exc))
        except ProibidoRobots:
            diag["fontes"][nome]["proibido_robots"] = True
        except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba a outra
            diag["fontes"][nome]["falhas"].append(f"etapa: {_erro(exc)}")
    _PRAZO["ate"] = None
    F = diag["fontes"]
    leu = any(F[k]["consultas"] for k in F)
    na_nuvem = bool(os.environ.get("GITHUB_ACTIONS")) and not os.environ.get("ELDORADO_LOCAL_BR")
    suap_recusou = any(r.startswith(("A:", "B:")) for r in recusas) and not (F["A"]["consultas"] or F["B"]["consultas"])
    # 02/10 — leitura real no servidor do GitHub: o SUAP não respondeu a NENHUMA consulta (RuntimeError em todas), mas as
    # fontes registram a falha consulta a consulta, sem levantar Recusa. Na nuvem isso é "exige IP brasileiro": os
    # projetos e a tramitação ficam para a coleta local e as NOTÍCIAS (fonte C) continuam sendo lidas.
    suap_fora = na_nuvem and not (F["A"]["consultas"] or F["B"]["consultas"]) and bool(F["A"]["falhas"] or F["B"]["falhas"])
    if suap_fora:
        diag["exige_brasil"] = True
        diag["suap_na_nuvem"] = (F["A"]["falhas"] + F["B"]["falhas"])[:5]
        if not recusas:
            recusas.append("A/B: o SUAP não respondeu ao servidor do GitHub")
        F["A"]["falhas"], F["B"]["falhas"] = [], []
        suap_recusou = suap_recusou or not F["C"]["consultas"]
    if suap_recusou and na_nuvem:
        # medido, não suposto: os portais da Câmara recusam o IP do GitHub — vale a coleta local
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(), "pulado_exige_brasil": True,
                "diagnostico": {**diag, "exige_brasil": True,
                                "motivo_zero": "aguardando coleta local (Brasil): os portais da Câmara recusaram o IP do GitHub ("
                                               + recusas[0][:120] + "); a leitura é a de scripts/coleta_brasil.py no computador do titular"
                                               + ("; notícias: " + (F["C"]["falhas"] or ["ok"])[0][:80] if F["C"]["falhas"] else "")}}
    oport, acomp, habilitacao, cont = classificar_lote(itens, hoje, cfg)
    est = load_json(ESTADO) if ESTADO.exists() else {}
    # tramitação da própria associação: avisa quando aparece documento novo
    antes = est.get("processos_proprios") or {}
    agora, novidades = {}, []
    for m in itens:
        if m.get("fonte") == "B" and m.get("documentos_completos"):     # leitura parcial não sobrescreve nem gera aviso
            agora[m["processo"]] = {k: m.get(k) for k in ("processo", "assunto", "url", "situacao", "setor", "total_documentos",
                                                          "ultimo_documento", "ultima_data")}
            a0 = antes.get(m["processo"]) or {}
            if a0 and (m.get("total_documentos") or 0) > (a0.get("total_documentos") or 0):
                novidades.append(f"{m.get('numero') or m['processo']}: {m.get('ultimo_documento')} ({m.get('ultima_data') or 's/d'})")
    if novidades:
        diag["novidade_associacao"] = novidades
    ja = {h.get("processo") for h in (est.get("utilidade_publica") or [])}
    diag.update({"vereditos": cont, "paginas_lidas": sum(F[k]["consultas"] for k in F), "links_total": len(itens),
                 "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"],
                 "habilitacao_novas": sum(1 for h in habilitacao if h.get("processo") not in ja)})
    if F["A"].get("formato_desconhecido"):
        diag["alerta_formato"] = ("o SUAP disse ter processos, mas o leitor não reconheceu nenhum bloco (assuntos: "
                                  + ", ".join(F["A"]["formato_desconhecido"][:4]) + ") — o HTML pode ter mudado")
    if F["A"].get("cortados"):
        diag["cobertura_cortada"] = F["A"]["cortados"][:10]
    # 03/10 (teste do motor 04): PUBLICADO × LIDO — pauta publicada e não lida faz o maestro ver "parcial" e disparar de novo
    if F["D"].get("paginas_nao_lidas"):
        diag["paginas_nao_lidas"] = F["D"]["paginas_nao_lidas"][:20]
    if F["D"].get("formato_desconhecido"):
        diag["alerta_formato"] = "pauta lida sem nenhum projeto reconhecido (o PDF pode ter mudado): " + ", ".join(F["D"]["formato_desconhecido"][:3])
    diag["leitura_do_dia"] = {"pautas_publicadas": F["D"].get("publicadas"), "pautas_lidas": F["D"].get("lidas"),
                              "noticias": F["C"]["itens"], "nao_lidas": F["D"].get("nao_lidas") or []}
    proib = [k for k in F if F[k].get("proibido_robots")]
    if proib:
        diag["proibido_robots"] = {"fontes": proib, "motivo": "o robots.txt do SUAP (suap.camaragyn.go.gov.br) proíbe robôs "
                                   "(Disallow: /) — os processos e a tramitação vêm das pautas do Plenário no portal; a ficha do "
                                   "processo da associação no SUAP é conferida pelo titular (consulta humana)"}
    d0 = hoje.isoformat()
    hist = est.setdefault("historico", {})
    hist[d0] = {**{f"consultas_{k}": F[k]["consultas"] for k in F}, **{f"itens_{k}": F[k]["itens"] for k in F},
                **cont, "falhou": not leu}
    seq, d = 0, hoje
    for _ in range(30):
        h = hist.get(d.isoformat())
        if not h or not h.get("falhou"):
            break
        seq += 1; d -= timedelta(days=1)
    if seq >= 2:
        diag["alerta"] = f"{seq} leituras seguidas sem resposta da Câmara — " + (sum((F[k]["falhas"] for k in F), []) + ["sem causa"])[0]
    campos = ("id", "titulo", "url", "data_publicacao", "fim", "autor", "setor", "situacao", "categoria", "propria")
    completo = leu and not any(F[k]["falhas"] for k in F) and not diag.get("exige_brasil")   # sem SUAP: o já conhecido fica
    abertas_l = [{k: r.get(k) for k in campos} for r in oport.values()]
    if not completo:                     # leitura falhou ou saiu parcial: o que não foi relido hoje continua na lista
        novos = {r["id"] for r in abertas_l}
        abertas_l += [r for r in (est.get("abertas") or []) if r.get("id") not in novos and str(r.get("fim") or "9999") >= d0]
    est["abertas"] = sorted(abertas_l, key=lambda r: str(r.get("fim") or "9999"))
    acomp_l = [{k: a.get(k) for k in campos} | {"motivo": a["classificacao_ato"]["motivos"][0]} for a in acomp.values()]
    if not completo:
        novos = {a["id"] for a in acomp_l}
        limite = (hoje - timedelta(days=60)).isoformat()
        acomp_l += [dict(a, nao_relido_em=d0) for a in (est.get("acompanhar") or [])
                    if a.get("id") not in novos and (a.get("propria") or str(a.get("data_publicacao") or "") >= limite)]
    acomp_l.sort(key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)
    est["acompanhar"] = sorted(acomp_l, key=lambda a: 0 if a.get("propria") else 1)[:200]   # a da associação primeiro
    hab = {h["processo"]: h for h in (est.get("utilidade_publica") or []) if h.get("processo")}
    for h in habilitacao:
        if h.get("processo"):
            hab[h["processo"]] = h
    est["utilidade_publica"] = sorted(hab.values(), key=lambda h: str(h.get("criado") or ""), reverse=True)[:600]
    if agora:
        est["processos_proprios"] = {**antes, **agora}
    est["ultima"] = {"em": now_iso(), "data": d0, "vereditos": cont, "falhas": sum((F[k]["falhas"] for k in F), [])[:10]}
    est["historico"] = {k: v for k, v in hist.items() if k >= (hoje - timedelta(days=120)).isoformat()}
    write_json(ESTADO, est)
    hosts = {"D": (cfg.get("portal") or {}).get("base", "https://www.goiania.go.leg.br"),
             "A": (cfg.get("suap") or {}).get("base", "https://suap.camaragyn.go.gov.br"),
             "B": (cfg.get("suap") or {}).get("base", "https://suap.camaragyn.go.gov.br"),
             "C": (cfg.get("portal") or {}).get("base", "https://www.goiania.go.leg.br")}
    falhas = [{"url": hosts[k], "erro": "camara", "code": None, "waf": None, "causa": f"{k}: {f}"}
              for k in F for f in F[k]["falhas"]][:6]
    saude = [{"url": hosts[k], "http": 200, "bytes": F[k].get("bytes", 0), "itens": F[k]["itens"]} for k in F if F[k]["consultas"]]
    if not oport:
        diag["motivo_zero"] = (f"{len(itens)} itens lidos (pautas D {F['D']['itens']} projetos em {F['D'].get('lidas') or 0} pauta(s) · "
                               f"processos A {F['A']['itens']} · própria B {F['B']['itens']} · notícias C "
                               f"{F['C']['itens']}): nenhum chamamento aberto para OSC · {cont['ACOMPANHAR']} a acompanhar · "
                               f"{len(habilitacao)} utilidade(s) pública(s) para a lista de habilitação" if leu else
                               "a Câmara não respondeu: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    if diag.get("exige_brasil"):
        diag["motivo_zero"] = ("SUAP só pelo Brasil: os projetos de lei e a tramitação da associação aguardam a coleta local "
                               "(scripts/coleta_brasil.py); notícias lidas na nuvem — " + str(diag.get("motivo_zero") or "sem oportunidade nas notícias"))
    return {"sensor": MOTOR_ID, "achados": sorted(oport.values(), key=lambda r: str(r.get("fim") or "9999")), "falhas": falhas,
            "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return (est.get("acompanhar") or [])[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
