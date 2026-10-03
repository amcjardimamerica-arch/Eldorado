"""MOTOR DO CONGRESSO NACIONAL — Câmara dos Deputados, Senado Federal e CMO (versão 1, 02/10/2026).

Parecer do conselho: docs/pareceres/motor-congresso-nacional.md. É o par federal dos motores 05 (Câmara de Goiânia) e
06 (ALEGO). O que o sistema tinha antes: só a área de emendas (src/emendas.py), que levanta os 594 parlamentares pelas
APIs e marca uma janela FIXA de captação (01/10–30/11) — sem ler o prazo oficial da Comissão Mista de Orçamento (CMO),
sem ler proposições e sem ler as próprias Casas. O ponto da fonte "emenda parlamentar federal" no catálogo das 260
apontava para as homes da Câmara e do Senado, que não trazem nada disso.

O que o Congresso produz para uma OSC (verificado ao vivo em 02/10/2026):
  • a JANELA DE EMENDAS ao orçamento da União — PLOA 2027 = PLN 24/2026, recebido em 31/08; R$ 28,5 bi em emendas
    individuais (≈ R$ 43,0 mi por deputado e R$ 79,1 mi por senador, 50% na saúde) e R$ 16,3 bi de bancada estadual
    (Informativo Conjunto, 04/09/2026). O prazo de apresentação é fixado pela CMO depois do despacho; em 02/10 a etapa
    "Apresentação de emendas" estava NÃO INICIADA. É a oportunidade de recurso mais importante do Congresso para a
    associação: a entidade leva projeto e ofício ao gabinete ANTES de a emenda ser apresentada;
  • REGRAS que mudam a vida das entidades: alterações da Lei 13.019 (MROSC), imunidade e IBS/CBS das entidades sem fins
    lucrativos, REFIS do terceiro setor, crédito do FGTS para filantrópicas, cessão de créditos de energia… (insumo de
    habilitação e de planejamento, não edital);
  • raramente, chamamento, prêmio, honraria ou cessão das próprias Casas (as convocações públicas do Senado desde 2017
    não tiveram nenhuma dirigida a OSC).

Como funciona (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — orçamento/CMO: página da LOA do ano seguinte (etapa "Apresentação de emendas": situação e datas) e os
            comunicados da CMO (prazo de emendas, cronograma, LOA, LDO);
  Fonte B — Câmara, API de dados abertos: proposições apresentadas na janela de dias, por expressão;
  Fonte C — Senado, API de dados abertos (/processo): proposições e as que viraram lei;
  Fonte D — notícias das duas Casas (RSS): edital, prêmio, honraria, orçamento e programas com entidades;
  Fonte E — convocações públicas do Senado (chamamentos/PMI): vigia.
  → cada item vira OPORTUNIDADE (janela de emendas aberta; chamamento/prêmio com entidades e prazo), ACOMPANHAR
    (emendas a abrir ou encerradas, comunicado da CMO, regra para entidades, programa com entidades, honraria) ou RUÍDO,
    com o motivo escrito. A situação da janela de emendas vai para estado/congresso_nacional.json › janela_emendas, que
    a área de emendas (src/emendas.py) usa como prazo oficial.
Conteúdo coletado é DADO: injeção → quarentena; o que a fonte não diz fica `null`.
"""
from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode, urljoin

from . import atos_diario as atos
from .camara_goiania import (EDITAL, ENTIDADE, FOMENTO, NAO_OSC_EDITAL, PROGRAMA, PUBLICO_OSC, REGRA_OSC, RUIDO_TEMA, Recusa,
                             _ENT_PUBLICA, _N, _erro, _get_texto, _limpo, _prazo)
from .nucleo import ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256, write_json

MOTOR_ID = "congresso-nacional"
CFG = ROOT / "config/congresso_nacional.json"
ESTADO = ROOT / "estado/congresso_nacional.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
_PRAZO = {"ate": None}


def _hoje_real() -> date:
    return date.today()


def _tempo_esgotado() -> bool:
    return _PRAZO["ate"] is not None and time.monotonic() > _PRAZO["ate"]


def _cfg() -> dict:
    return load_json(CFG) if CFG.exists() else {}


def _get(url: str, cfg: dict, fonte: dict) -> str:
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
        except Recusa as exc:
            ultimo = exc; break
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            if getattr(exc, "code", None) in (400, 401, 404) or isinstance(exc, ValueError):
                break
            time.sleep(float(ritmo.get("espera_erro_segundos", 4)))
    raise RuntimeError(_erro(ultimo))


def _json(t: str):
    try:
        return json.loads(t)
    except ValueError:
        return None


def _data_br(s: str) -> str | None:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return None


# ─────────────────────────── Fonte A: orçamento / CMO ───────────────────────────
_STATUS = [("nao_iniciada", re.compile(r"NAO INICIAD[OA]|NAO ABERT[OA]|A INICIAR|AGUARDANDO|PREVIST[OA]")),   # negações primeiro
           ("encerrada", re.compile(r"ENCERRAD[OA]|CONCLUID[OA]|FINALIZAD[OA]")),
           ("em_andamento", re.compile(r"EM ANDAMENTO|\bABERT[OA]\b|EM CURSO|EM EXECUCAO"))]
_ETAPA = re.compile(r"^\W*APRESENTACAO DE EMENDAS\W*$")                       # a etapa exata — não "emendas ao Parecer Preliminar"
_OUTRAS_ETAPAS = re.compile(r"ANALISE D[AO]|APRESENTACAO DO (?:PROJETO|RELATORIO)|VOTACAO|SANCAO|RELATORIOS? (?:SETORIA|PRELIMINAR|GERAL|DA RECEITA)|"
                            r"APRESENTACAO DE EMENDAS (?:AO|A|AOS) ")
_TR = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S | re.I)
_TD = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.S | re.I)


def _status_e_datas(trecho: str) -> tuple[str, str | None, str | None]:
    """Status = o PRIMEIRO que aparece no trecho (negações testadas antes); datas só do trecho."""
    achados = [(m.start(), nome) for nome, rx in _STATUS for m in [rx.search(trecho)] if m]
    status = min(achados)[1] if achados else "desconhecido"
    datas = [(m.start(), d) for m in re.finditer(r"\d{2}/\d{2}/\d{4}", trecho) for d in [_data_br(m.group(0))] if d]
    if not datas:
        return status, None, None
    if len(datas) == 1:
        antes = trecho[max(0, datas[0][0] - 14): datas[0][0]]
        return (status, None, datas[0][1]) if re.search(r"\bATE\b|PRAZO|FIM|TERMINO", antes) else (status, datas[0][1], None)
    return status, datas[0][1], datas[-1][1]


def etapa_emendas(html: str) -> dict:
    """Página da LOA → {status, inicio, fim, projeto, situacao, trecho}. Lê a LINHA da tabela cuja 1ª célula é exatamente
    "Apresentação de emendas"; sem tabela, o trecho do texto até a próxima etapa. Status: nao_iniciada · em_andamento ·
    encerrada · desconhecido (formato novo: o motor avisa em vez de adivinhar)."""
    T = _N(_limpo(html))
    proj = re.search(r"\bPLN\s*(\d{1,3})\s*/\s*(\d{4})", T)
    # 03/10 (teste do motor 06): a situação é a do "Último estado" do projeto. Antes o motor pegava o 1º "AGUARDANDO…" da
    # página — que é o item de MENU "Matérias Aguardando Sanção" — e gravava "Aguardando sanção" para o PLOA que aguarda despacho.
    ue = re.search(r"ULTIMO ESTADO:?\s*(\d{2}/\d{2}/\d{4})\s*-\s*([A-Z ]{3,60}?)(?= COMUNICADO| ACOMPANHAR| EMENTA| AUTORIA|\s*$)", T)
    sit = None if ue else re.search(r"(?<!MATERIAS )(AGUARDANDO [A-Z ]{3,40}?|TRANSFORMADA EM NORMA JURIDICA[A-Z ]{0,30}|EM TRAMITACAO|"
                                    r"PRONTA PARA PAUTA)(?= |$)", T)
    situacao = (ue.group(2) if ue else sit.group(1) if sit else None)
    base = {"projeto": f"PLN {int(proj.group(1))}/{proj.group(2)}" if proj else None,
            "situacao": situacao.strip().capitalize() if situacao else None,
            "situacao_desde": _data_br(ue.group(1)) if ue else None}
    for tr in _TR.findall(html or ""):
        celulas = [_N(_limpo(c)) for c in _TD.findall(tr)]
        if celulas and _ETAPA.match(celulas[0]):
            trecho = " ".join(celulas[1:])
            st, ini, fim = _status_e_datas(trecho)
            return {**base, "status": st, "inicio": ini, "fim": fim, "trecho": ("APRESENTACAO DE EMENDAS " + trecho)[:260]}
    for m in re.finditer(r"APRESENTACAO DE EMENDAS(?! (?:AO|A|AOS) )", T):        # sem tabela: texto até a próxima etapa
        resto = T[m.end(): m.end() + 260]
        prox = _OUTRAS_ETAPAS.search(resto)
        trecho = resto[: prox.start()] if prox else resto[:120]
        st, ini, fim = _status_e_datas(trecho)
        return {**base, "status": st, "inicio": ini, "fim": fim, "trecho": ("APRESENTACAO DE EMENDAS" + trecho)[:260]}
    return {**base, "status": "desconhecido", "inicio": None, "fim": None, "trecho": None}


# 03/10 (teste do motor 06): a página da CMO usa href RELATIVO ("comunicados/-/blogs/…", sem barra antes) e põe a data
# DENTRO do link ("02/10/2026 12:35<br/><span>título</span>"). O padrão antigo exigia "/comunicados/" e não casava com
# nenhum link: os 6 comunicados de 01/09 a 02/10 (LOA 2027, Lexor, ofício de apoio à emenda) nunca foram lidos.
_A_COMUNICADO = re.compile(r"""<a\b[^>]*href=["']([^"']*?comunicados/-/blogs/[^"'#?]+)(?:[?#][^"']*)?["'][^>]*>(.*?)</a>""", re.S | re.I)


def comunicados_da_pagina(html: str, base: str) -> list[dict]:
    """`base` = endereço da PÁGINA dos comunicados (o href relativo é resolvido a partir dela)."""
    out, vistos = [], set()
    pagina = base if "/comunicados" in base else base.rstrip("/") + "/web/cmo/comunicados"
    for m in _A_COMUNICADO.finditer(html or ""):
        url = urljoin(pagina, m.group(1))
        interno = _limpo(m.group(2))
        dentro = _data_br(interno)
        tit = re.sub(r"^\s*\d{2}/\d{2}/\d{4}(?:\s+\d{1,2}:\d{2})?\s*[-–]?\s*", "", interno).strip()
        if len(tit) < 6 or url in vistos:
            continue
        vistos.add(url)
        prox = _A_COMUNICADO.search(html or "", m.end())
        depois = _limpo((html or "")[m.end(): min(m.end() + 200, prox.start() if prox else len(html or ""))])
        antes = _limpo((html or "")[max(0, m.start() - 160): m.start()])
        out.append({"fonte": "A", "tipo": "comunicado", "titulo": tit[:300], "url": url,
                    "publicado": dentro or _data_br(depois) or (_data_br(antes[-40:]) if antes else None)})
    return out


def fonte_a(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("orcamento") or {}
    if c.get("ativa", True) is False:
        return []
    base = c.get("base", "https://www.congressonacional.leg.br").rstrip("/")
    F = diag["fontes"]["A"]
    out = []
    # o PLOA chega em 31/08: de agosto a dezembro tramita o do ANO SEGUINTE; de janeiro a julho, a LOA do ano corrente
    # (sancionada ou, em anos de atraso, ainda em votação). Página inexistente fora do ciclo não é falha.
    ano = hoje.year + 1 if hoje.month >= 8 else hoje.year
    url = base + c.get("loa", "/web/orcamento/acompanhe/orcamento-anual/-/loa/{ano}").format(ano=ano)
    try:
        html = _get(url, cfg, F)
        e = etapa_emendas(html)
        if e["status"] == "desconhecido":
            F["formato_desconhecido"] = True
        out.append({"fonte": "A", "tipo": "etapa_emendas", "ano": ano, "url": url, "titulo": f"PLOA {ano} — apresentação de emendas", **e})
    except Exception as exc:  # noqa: BLE001
        if "404" in str(exc):
            F["fora_do_ciclo"] = f"LOA {ano} ainda sem página na CMO"
        else:
            F["falhas"].append(f"LOA {ano}: {exc}")
    corte = (hoje - timedelta(days=int(c.get("janela_dias", 60)))).isoformat()
    try:
        pag = base + c.get("comunicados", "/web/cmo/comunicados")
        html = _get(pag, cfg, F)
        lista = comunicados_da_pagina(html, pag)
        F["comunicados_na_pagina"] = len(lista)
        if not lista and "comunicados/-/blogs/" in (html or ""):
            F["formato_desconhecido_comunicados"] = True       # há links de comunicado e o leitor não reconheceu nenhum
        datas = [x["publicado"] for x in lista if x["publicado"]]
        if lista and datas and min(datas) >= corte and len(lista) >= int(c.get("comunicados_por_pagina", 10)):
            F.setdefault("cortados", []).append("comunicados da CMO: a 1ª página não alcança o início da janela")
        out += [x for x in lista if not x["publicado"] or x["publicado"] >= corte]
    except Exception as exc:  # noqa: BLE001
        F["falhas"].append(f"comunicados: {exc}")
    F["itens"] = len(out)
    return out


# ─────────────────────────── Fonte B: Câmara (API) ───────────────────────────
def proposicoes_camara(dados) -> list[dict]:
    out = []
    for p in ((dados or {}).get("dados") if isinstance(dados, dict) else None) or []:
        if not isinstance(p, dict) or not p.get("id"):
            continue
        ident = f"{p.get('siglaTipo') or ''} {p.get('numero') or ''}/{p.get('ano') or ''}".strip()
        out.append({"fonte": "B", "casa": "Câmara dos Deputados", "id_casa": str(p["id"]), "identificacao": ident,
                    "titulo": ident, "ementa": _limpo(p.get("ementa")), "publicado": str(p.get("dataApresentacao") or "")[:10] or None,
                    "url": f"https://www.camara.leg.br/propostas-legislativas/{p['id']}"})
    return out


def fonte_b(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("camara") or {}
    if c.get("ativa", True) is False:
        return []
    F = diag["fontes"]["B"]
    api = c.get("api", "https://dadosabertos.camara.leg.br/api/v2").rstrip("/")
    ini = (hoje - timedelta(days=int(c.get("janela_dias", 45)))).isoformat()
    vistos: dict[str, dict] = {}
    for kw in c.get("keywords", []):
        q = urlencode({"keywords": kw, "dataApresentacaoInicio": ini, "itens": int(c.get("itens_por_consulta", 100)),
                       "ordem": "DESC", "ordenarPor": "id"})
        try:
            dados = _json(_get(f"{api}/proposicoes?{q}", cfg, F))
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{kw}: {exc}"); continue
        if dados is None:
            F["falhas"].append(f"{kw}: resposta não é JSON"); continue
        lote = proposicoes_camara(dados)
        if len(lote) >= int(c.get("itens_por_consulta", 100)):
            F.setdefault("cortados", []).append(kw)          # mais resultados que uma página: o resto fica para a próxima janela
        for p in lote:
            vistos.setdefault(p["id_casa"], {**p, "termo": kw})
    F["itens"] = len(vistos)
    return list(vistos.values())


# ─────────────────────────── Fonte C: Senado (API /processo) ───────────────────────────
def processos_senado(dados) -> list[dict]:
    out = []
    for p in (dados if isinstance(dados, list) else []):
        if not isinstance(p, dict) or not (p.get("id") or p.get("codigoMateria")):
            continue
        cod = p.get("codigoMateria")
        out.append({"fonte": "C", "casa": "Senado Federal", "id_casa": str(p.get("id") or cod), "identificacao": p.get("identificacao"),
                    "titulo": p.get("identificacao") or "", "ementa": _limpo(p.get("ementa")),
                    "publicado": str(p.get("dataApresentacao") or "")[:10] or None, "situacao": p.get("situacaoAtual"),
                    "norma": p.get("normaGerada"), "tramitando": p.get("tramitando"), "autoria": p.get("autoria"),
                    "url": (f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{cod}" if cod else p.get("urlDocumento"))})
    return out


def fonte_c(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("senado") or {}
    if c.get("ativa", True) is False:
        return []
    F = diag["fontes"]["C"]
    api = c.get("api", "https://legis.senado.leg.br/dadosabertos").rstrip("/")
    ini = (hoje - timedelta(days=int(c.get("janela_dias", 45)))).isoformat()
    vistos: dict[str, dict] = {}
    for termo in c.get("termos", []):
        q = urlencode({"termo": termo, "dataInicioApresentacao": ini, "v": 1})
        try:
            dados = _json(_get(f"{api}/processo?{q}", cfg, F))
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{termo}: {exc}"); continue
        if dados is None:
            F["falhas"].append(f"{termo}: resposta não é JSON"); continue
        if not isinstance(dados, list):
            F["formato_desconhecido"] = True; F["falhas"].append(f"{termo}: a API do Senado não devolveu lista"); continue
        for p in processos_senado(dados):
            vistos.setdefault(p["id_casa"], {**p, "termo": termo})
    F["itens"] = len(vistos)
    return list(vistos.values())


# ─────────────────────────── Fonte D: notícias (RSS) ───────────────────────────
def noticias_rss(xml: str, casa: str) -> list[dict]:
    try:
        raiz = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    except ET.ParseError:
        return []
    out = []
    for it in raiz.iter("item"):
        g = lambda tag: ((it.find(tag).text or "").strip() if it.find(tag) is not None and it.find(tag).text else "")
        pub = None
        try:
            pub = parsedate_to_datetime(g("pubDate")).date().isoformat() if g("pubDate") else None
        except (TypeError, ValueError):
            pub = None
        out.append({"fonte": "D", "casa": casa, "titulo": _limpo(g("title"))[:300], "url": g("link"),
                    "descricao": _limpo(g("description"))[:900], "publicado": pub})
    return out


def fonte_d(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("noticias") or {}
    if c.get("ativa", True) is False:
        return []
    F = diag["fontes"]["D"]
    corte = (hoje - timedelta(days=int(c.get("janela_dias", 15)))).isoformat()
    vistos: dict[str, dict] = {}
    # 03/10 (teste do motor 06): o RSS das Casas traz só as ~20 últimas notícias (≈ 1 dia). Se o motor passar um dia sem ler,
    # o que saiu no meio NUNCA é visto. Agora: o item mais antigo do feed é comparado com a última leitura completa; havendo
    # buraco, a listagem paginada da Casa é lida até cobri-lo; o que não couber vira `paginas_nao_lidas` (maestro: parcial).
    lidas_ate = dict((diag.get("_estado") or {}).get("noticias_lidas_ate") or {})
    for f in c.get("feeds", []):
        casa = f.get("casa") or ""
        try:
            xml = _get(f["url"], cfg, F)
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{casa}: {exc}"); continue
        lote = noticias_rss(xml, casa)
        for n in lote:
            if n["url"] and (n["publicado"] or "9999") >= corte:
                vistos.setdefault(n["url"], n)
        datas = sorted(n["publicado"] for n in lote if n["publicado"])
        ate = lidas_ate.get(casa)
        if not datas:
            continue
        if ate and datas[0] > ate:                           # buraco entre a última leitura e o item mais antigo do feed
            coberto = _recuperar_listagem(f, ate, cfg, F, vistos, corte)
            if not coberto:
                F.setdefault("paginas_nao_lidas", []).append(f"notícias da {casa} entre {ate} e {datas[0]} (feed curto)")
                continue
        lidas_ate[casa] = datas[-1]
    F["lidas_ate"] = lidas_ate
    F["itens"] = len(vistos)
    return list(vistos.values())


_A_NOTICIA = re.compile(r"""<a\b[^>]*href=["']((?:https?://[^"'/]+)?/noticias/(?:materias/\d{4}/\d{2}/\d{2}/|\d{6,}-)[^"'#?]+)["'][^>]*>(.*?)</a>""",
                        re.S | re.I)


def noticias_da_listagem(html: str, casa: str, pagina: str = "") -> list[dict]:
    """Listagem paginada de notícias (Câmara: /noticias/ultimas?pagina=N, link absoluto · Senado: /noticias/ultimas/N, link
    relativo com a data no endereço) → itens com data."""
    out, vistos = [], set()
    for m in _A_NOTICIA.finditer(html or ""):
        url, tit = urljoin(pagina, m.group(1)) if pagina else m.group(1), _limpo(m.group(2))
        if not url.startswith("http"):
            continue
        if len(tit) < 12 or url in vistos:
            continue
        vistos.add(url)
        d = re.search(r"/materias/(\d{4})/(\d{2})/(\d{2})/", url)          # Senado: a data está no endereço
        prox = _A_NOTICIA.search(html or "", m.end())                          # Câmara: <span class="g-chamada__data"> logo depois
        depois = _limpo((html or "")[m.end(): min(m.end() + 400, prox.start() if prox else len(html or ""))])
        pub = f"{d.group(1)}-{d.group(2)}-{d.group(3)}" if d else _data_br(depois)
        out.append({"fonte": "D", "casa": casa, "titulo": tit[:300], "url": url, "descricao": "", "publicado": pub})
    return out


def _recuperar_listagem(f: dict, ate: str, cfg: dict, F: dict, vistos: dict, corte: str) -> bool:
    """Lê a listagem paginada da Casa até alcançar `ate` (a última leitura). True = buraco coberto."""
    modelo = f.get("listagem")
    if not modelo:
        return False
    for pagina in range(1, int(f.get("max_paginas_recuperacao", 15)) + 1):
        try:
            end = modelo.format(pagina=pagina)
            itens = noticias_da_listagem(_get(end, cfg, F), f.get("casa") or "", end)
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"{f.get('casa')} (recuperação, página {pagina}): {exc}"); return False
        if not itens:
            return False
        for n in itens:
            if (n["publicado"] or "9999") >= corte:
                vistos.setdefault(n["url"], n)
        datas = [n["publicado"] for n in itens if n["publicado"]]
        if datas and min(datas) <= ate:
            F.setdefault("recuperadas", []).append(f"{f.get('casa')}: {pagina} página(s) da listagem")
            return True
    return False


# ─────────────────────────── Fonte E: convocações públicas do Senado ───────────────────────────
_A_CONV = re.compile(r"""<a\b[^>]*href=["']([^"']*/convocacoes-publicas/[\w-]+)["'][^>]*>(.*?)</a>""", re.S | re.I)


def convocacoes_da_pagina(html: str, base: str) -> list[dict]:
    out, vistos = [], set()
    for m in _A_CONV.finditer(html or ""):
        url = urljoin(base, m.group(1))
        if url in vistos:
            continue
        vistos.add(url)
        fim_tr = (html or "").find("</tr>", m.end())
        prox = _A_CONV.search(html or "", m.end())
        corte = min(x for x in (fim_tr if fim_tr > 0 else len(html or ""), prox.start() if prox else len(html or ""), m.end() + 700))
        bloco = _limpo((html or "")[m.start(): corte])      # só a linha da própria convocação
        out.append({"fonte": "E", "casa": "Senado Federal", "titulo": bloco[:300], "url": url, "publicado": _data_br(bloco)})
    return out


def fonte_e(hoje: date, cfg: dict, diag: dict) -> list[dict]:
    c = cfg.get("convocacoes") or {}
    if c.get("ativa", True) is False or not c.get("url"):
        return []
    F = diag["fontes"]["E"]
    try:
        html = _get(c["url"], cfg, F)
    except Exception as exc:  # noqa: BLE001
        F["falhas"].append(str(exc)); return []
    corte = (hoje - timedelta(days=int(c.get("janela_dias", 400)))).isoformat()
    out = [x for x in convocacoes_da_pagina(html, c["url"]) if (x["publicado"] or "9999") >= corte]   # sem data: fica (é a lista oficial)
    F["itens"] = len(out)
    return out


# ─────────────────────────── classificação ───────────────────────────
TRIBUTARIO = re.compile(r"IMUNIDADE|ART(?:IGO)?S?\.? 150\b|ISENC|\bIBS\b|\bCBS\b|TRIBUT|REFIS|CEBAS|LEI COMPLEMENTAR (?:N. )?187|CERTIFICAC(?:AO|OES) DAS ENTIDADES|"
                        r"RENUNCIAS? DE RECEITA|INCENTIVOS? (?:FISCA|TRIBUT)|DEDUC")
MROSC = re.compile(r"13\.019|MARCO REGULATORIO DAS ORGANIZACOES|TERMOS? DE (?:FOMENTO|COLABORACAO)|"
                   r"PARCERIAS? (?:ENTRE|COM) (?:A ADMINISTRACAO|O PODER|ORGANIZAC|ENTIDADES)|"
                   r"ACORDOS? DE COOPERACAO (?:COM|ENTRE)[^.]{0,40}(?:ORGANIZAC|ENTIDADES|OSC)")
NAO_ENTIDADE = re.compile(r"ASSOCIAC(?:AO|OES) DE PROTECAO PATRIMONIAL[A-Z ]{0,20}|PROTECAO VEICULAR|ASSOCIAC(?:AO|OES) CRIMINOSAS?|ORGANIZAC(?:AO|OES) CRIMINOSAS?|ENTIDADES? DE CLASSE PATRONA|ENTIDADES? FECHADAS")
ENT_PREMIADA = re.compile(r"PREMI\w* (?:A |AS |PARA |DE )?(?:ENTIDADES|OSCS?|ORGANIZACOES|ASSOCIACOES|INSTITUICOES|PROJETOS SOCIAIS|INICIATIVAS)|"
                          r"RECONHECE (?:ENTIDADES|OSCS?|ORGANIZACOES|ASSOCIACOES|INSTITUICOES|INICIATIVAS|PROJETOS)|"
                          r"ENTIDADES (?:PODEM SE INSCREVER|INSCRITAS|PREMIADAS|AGRACIADAS|HOMENAGEADAS)")
REGIME_ENTIDADES = re.compile(r"REGIME JURIDICO (?:ESPECIFICO |PROPRIO )?D[AO]S? (?:ASSOCIAC|ENTIDADES|ORGANIZAC|FUNDACOES|OSC)|"
                              r"ASSOCIACOES CIVIS SEM FINS|ESTATUTO D[AO]S? (?:ENTIDADES|ASSOCIAC|ORGANIZAC)|"
                              r"CODIGO CIVIL[^.]{0,80}(?:ASSOCIAC|FUNDACO)")
EMENDAS = re.compile(r"EMENDAS? (?:PARLAMENTAR|INDIVIDUA|DE BANCADA|DE COMISSAO|IMPOSITIVA)|TRANSFERENCIAS? ESPECIA|"
                     r"LEI COMPLEMENTAR (?:N. )?210|\bRP ?[6789]\b")
ORCAMENTO = re.compile(r"\bPLOA\b|\bLOA\b|\bLDO\b|ORCAMENTO (?:DE )?20\d\d|LEI ORCAMENTARIA|DIRETRIZES ORCAMENTARIAS|COMISSAO MISTA DE (?:PLANOS|ORCAMENTO)|\bCMO\b")
RECURSO = re.compile(r"CESSAO (?:DE )?CREDITOS?|TARIFA SOCIAL|OPERAC(?:AO|OES) DE CREDITO|\bFGTS\b|GRATUIDADE|DESCONTO|"
                     r"TRANSFERENCIA DE RECURSOS|DESTINAC(?:AO|OES) DE RECURSOS|REPASSE|RECURSOS PUBLICOS|APOIO A ACOES")
HONRARIA = re.compile(r"PREMIO|COMENDA|DIPLOMA|HONRARIA|MEDALHA|SELO\b")
INDICACAO = re.compile(r"INDICAC(?:AO|OES)|INSCRIC(?:AO|OES)|CANDIDATURAS?|INSCREV")
PRAZO_EMENDA = re.compile(r"PRAZO (?:DE|PARA) (?:APRESENTACAO DE )?EMENDAS|CRONOGRAMA|APRESENTACAO DE EMENDAS|EMENDAS AO (?:PLOA|PROJETO)|"
                          r"\bLOA 20\d\d|\bLDO 20\d\d|OFICIO DE APOIO")


def _proposicao(m: dict, T: str, TE: str, base: dict) -> dict:
    virou = f"virou lei ({m['norma']}) — " if m.get("norma") else ""
    for nome, rx in RUIDO_TEMA:
        if rx.search(T) and not (FOMENTO.search(T) and ENTIDADE.search(TE)):
            return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": [nome]}
    if not ENTIDADE.search(TE) and not EMENDAS.search(T) and not MROSC.search(T):
        return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["proposição sem entidade sem fins lucrativos nem emenda"]}
    if EMENDAS.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_emendas", "regime": "emenda_parlamentar_federal",
                "motivos": [virou + "regra sobre emendas parlamentares — muda como a entidade recebe emenda federal"]}
    if MROSC.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_mrosc", "regime": "regra_para_entidades",
                "motivos": [virou + "altera o regime das parcerias com OSC (Lei 13.019) — afeta habilitação e prestação de contas"]}
    if REGIME_ENTIDADES.search(TE):                     # 03/10: regime jurídico das associações civis (antes era ruído)
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_para_entidades", "regime": "regra_para_entidades",
                "motivos": [virou + "muda o regime jurídico das associações ou entidades sem fins lucrativos — conferir efeito no estatuto"]}
    if TRIBUTARIO.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "tributario_entidades", "regime": "regra_para_entidades",
                "motivos": [virou + "tributação, imunidade, certificação ou regularização das entidades sem fins lucrativos"]}
    if PROGRAMA.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "programa_com_entidades", "regime": "lei_de_fomento",
                "motivos": [virou + "cria programa ou política com entidades — pode abrir recurso ou chamamento depois de aprovado"]}
    if FOMENTO.search(T) or RECURSO.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "fomento_parceria", "regime": "lei_de_fomento",
                "motivos": [virou + "recurso, desconto, cessão ou apoio para entidades sem fins lucrativos"]}
    if REGRA_OSC.search(TE):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra_para_entidades", "regime": "regra_para_entidades",
                "motivos": [virou + "muda regra ou regime jurídico das entidades sem fins lucrativos — conferir efeito na associação"]}
    return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["cita entidades sem criar recurso, programa ou regra para elas"]}


def classificar_item(m: dict, hoje: date, cfg: dict | None = None) -> dict:
    """Item de qualquer fonte → OPORTUNIDADE · ACOMPANHAR · RUÍDO, com o motivo escrito."""
    cfg = cfg or {}
    nomes = [_N(x) for x in (cfg.get("associacao") or {}).get("nomes", [])]
    texto = " ".join(str(x) for x in (m.get("titulo"), m.get("ementa"), m.get("descricao")) if x)
    T = _N(texto)
    TE = NAO_ENTIDADE.sub(" ", _ENT_PUBLICA.sub(" ", T))
    propria = any(n and n in T for n in nomes)
    base = {"categoria": None, "regime": None, "motivos": [], "sinais": [], "propria": propria, "fim": None}
    ref = ((cfg.get("orcamento") or {}).get("referencia_ploa") or {})
    if m.get("tipo") == "etapa_emendas":
        valores = (f" Referência do PLOA {ref.get('ano')}: emendas individuais {ref.get('individual_por_deputado')} por deputado e "
                   f"{ref.get('individual_por_senador')} por senador ({ref.get('saude_minimo_individuais')} na saúde); bancada estadual "
                   f"{ref.get('bancada_estadual_total')} no total.") if ref.get("ano") == m.get("ano") else ""
        st = m.get("status")
        if st == "em_andamento":
            return {**base, "veredito": "OPORTUNIDADE", "categoria": "janela_emendas", "regime": "emenda_parlamentar_federal",
                    "fim": m.get("fim"),
                    "motivos": [f"apresentação de emendas ao PLOA {m.get('ano')} ABERTA na CMO"
                                + (f" ({m.get('inicio')} a {m.get('fim')})" if m.get("fim") else " (datas não lidas — conferir na CMO)")
                                + ": levar projeto e ofício aos gabinetes (bancada de Goiás) antes do fim." + valores]}
        if st == "nao_iniciada":
            return {**base, "veredito": "ACOMPANHAR", "categoria": "emendas_a_abrir", "regime": "emenda_parlamentar_federal",
                    "motivos": [f"prazo de emendas ao PLOA {m.get('ano')} ainda não aberto ({m.get('projeto') or 'PLOA'}: "
                                f"{m.get('situacao') or 'situação não lida'}) — é a hora de preparar projeto e ofícios." + valores]}
        if st == "encerrada":
            return {**base, "veredito": "ACOMPANHAR", "categoria": "emendas_encerradas", "regime": "emenda_parlamentar_federal",
                    "motivos": [f"apresentação de emendas ao PLOA {m.get('ano')} encerrada — acompanhar a indicação de beneficiários e a execução"]}
        return {**base, "veredito": "ACOMPANHAR", "categoria": "emendas_formato", "regime": "emenda_parlamentar_federal",
                "motivos": ["a página da LOA mudou de formato: situação da etapa de emendas não reconhecida — conferir na CMO"]}
    if m.get("fonte") == "A":                               # comunicado da CMO
        if PRAZO_EMENDA.search(T) or EMENDAS.search(T) or ORCAMENTO.search(T):
            return {**base, "veredito": "ACOMPANHAR", "categoria": "comunicado_cmo", "regime": "emenda_parlamentar_federal",
                    "motivos": ["comunicado da Comissão Mista de Orçamento sobre LOA/LDO, emendas ou prazos"]}
        return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["comunicado da CMO sem emenda, prazo ou orçamento"]}
    if m.get("fonte") in ("B", "C"):
        return _proposicao(m, T, TE, base)
    # notícias (D) e convocações (E)
    fim, _fluxo, _trecho = _prazo(texto, m.get("publicado"))
    base["fim"] = fim
    if EDITAL.search(T) and PUBLICO_OSC.search(T) and not NAO_OSC_EDITAL.search(T):
        if fim and fim >= hoje.isoformat():
            return {**base, "veredito": "OPORTUNIDADE", "categoria": "chamamento", "regime": "chamamento_federal",
                    "motivos": [f"chamamento, edital ou seleção com entidades como público, inscrições até {fim} — conferir o edital"]}
        return {**base, "veredito": "ACOMPANHAR", "categoria": "chamamento", "regime": "chamamento_federal",
                "motivos": [f"chamamento com entidades {'encerrado em ' + fim if fim else 'sem prazo no texto'} — conferir"]}
    if m.get("fonte") == "E":
        return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["convocação pública para empresas ou soluções, não para OSC"]}
    if HONRARIA.search(T) and INDICACAO.search(T) and ENT_PREMIADA.search(TE):      # a entidade é a premiada, não quem indica
        return {**base, "veredito": "OPORTUNIDADE" if fim and fim >= hoje.isoformat() else "ACOMPANHAR", "categoria": "honraria",
                "regime": "premio_reconhecimento",
                "motivos": [f"prêmio ou honraria do Congresso com indicação de entidades{' até ' + fim if fim else ''} — "
                            "reconhecimento (reputação), não recurso"]}
    if EMENDAS.search(T) or (ORCAMENTO.search(T) and re.search(r"EMENDA|PRAZO|VOTA|RELATOR|CRONOGRAMA", T)):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "orcamento", "regime": "emenda_parlamentar_federal",
                "motivos": ["notícia sobre orçamento da União ou emendas parlamentares"]}
    if (FOMENTO.search(T) or PROGRAMA.search(T)) and (ENTIDADE.search(TE) or PUBLICO_OSC.search(T)):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "noticia_fomento", "regime": "lei_de_fomento",
                "motivos": ["notícia de lei, programa ou recurso que envolve entidades — acompanhar a tramitação"]}
    if propria:
        return {**base, "veredito": "ACOMPANHAR", "categoria": "propria", "motivos": ["cita a própria associação"]}
    return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["notícia sem edital, recurso, regra ou entidade"]}


def _chave(m: dict) -> str:
    if m.get("tipo") == "etapa_emendas":
        return f"loa:{m.get('ano')}"
    if m.get("id_casa"):
        return f"{m['fonte']}:{m['id_casa']}"
    return "url:" + (m.get("url") or "").split("?")[0].rstrip("/")


_FONTE_NOME = {"A": "Congresso Nacional — Comissão Mista de Orçamento", "E": "Senado Federal — convocações públicas"}


def _registro(c: dict, m: dict) -> dict:
    titulo = m.get("titulo") or ""
    if m.get("fonte") in ("B", "C"):
        titulo = f"{m.get('identificacao') or ''} — {m.get('ementa') or ''}"
    titulo = atos.mascarar_pii(titulo)
    ev = atos.mascarar_pii(" ".join(str(x) for x in (titulo, m.get("descricao"), m.get("trecho")) if x))[:700]
    casa = m.get("casa") or _FONTE_NOME.get(m.get("fonte"), "Congresso Nacional")
    return {
        "id": sha256(f"cn|{_chave(m)}".encode())[:20], "status": "capturada",
        "titulo": f"{casa} — {titulo}"[:300], "url": m.get("url"), "fonte_id": MOTOR_ID, "fonte_nome": casa,
        "territorio": "BR", "uf": None, "nivel": "federal", "abrangencia": "nacional",
        "tipo_fonte": "legislativo_federal", "confianca": "primaria" if m.get("fonte") in ("A", "B", "C", "E") else "secundaria",
        "forma_divulgacao": {"A": "cmo", "B": "api_camara", "C": "api_senado", "D": "noticias_casas", "E": "convocacoes_senado"}.get(m.get("fonte")),
        "coletado_em": now_iso(), "data_publicacao": m.get("publicado"), "inicio": m.get("inicio"), "fim": c.get("fim"),
        "prazo_texto": c.get("fim"), "identificacao": m.get("identificacao"), "situacao": m.get("situacao"), "norma": m.get("norma"),
        "regime": c.get("regime"), "categoria": c.get("categoria"), "propria": c.get("propria"),
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()),
        "classificacao_ato": {"veredito": c["veredito"], "regime": c.get("regime"), "motivos": c["motivos"], "sinais": c["sinais"],
                              "tipo": "abertura" if c["veredito"] == "OPORTUNIDADE" else "tramitacao"},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def classificar_lote(itens: list[dict], hoje: date, cfg: dict | None = None) -> tuple[dict, dict, dict]:
    oport, acomp = {}, {}
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0, "erros": 0}
    vistos: dict[str, dict] = {}
    for m in itens:
        vistos.setdefault(_chave(m), m)
    for m in vistos.values():
        bruto = " ".join(str(m.get(k) or "") for k in ("titulo", "ementa", "descricao", "trecho", "situacao"))
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1
            continue
        try:
            c = classificar_item(m, hoje, cfg)
            cont[c["veredito"]] += 1
            if c["veredito"] == "RUIDO":
                continue
            r = _registro(c, m)
        except Exception:  # noqa: BLE001 — um item malformado não derruba o lote
            cont["erros"] += 1
            continue
        (oport if c["veredito"] == "OPORTUNIDADE" else acomp)[r["id"]] = r
    return oport, acomp, cont


# ─────────────────────────── o motor ───────────────────────────
def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor do Congresso com a mesma saída de `sensores.ler`."""
    pedido = hoje or (sensor or {}).get("_data")
    hoje = _hoje_real() if pedido is None else pedido
    vazio = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0}
    if pedido is not None and pedido < _hoje_real():
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                "diagnostico": {**vazio, "motivo_zero": "o motor do Congresso lê a situação de hoje; dia passado não é relido",
                                "retroativo": True}}
    cfg = _cfg()
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 300))
    diag = {**vazio, "motivo_zero": None, "versao": "motor Congresso Nacional v1.1 (03/10/2026)",
            "fontes": {k: {"falhas": [], "consultas": 0, "itens": 0} for k in "ABCDE"},
            "_estado": (load_json(ESTADO) if ESTADO.exists() else {})}
    itens = []
    for nome, fn in (("A", fonte_a), ("B", fonte_b), ("C", fonte_c), ("D", fonte_d), ("E", fonte_e)):
        try:
            itens += fn(hoje, cfg, diag)
        except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba a outra
            diag["fontes"][nome]["falhas"].append(f"etapa: {_erro(exc)}")
    _PRAZO["ate"] = None
    diag.pop("_estado", None)
    F = diag["fontes"]
    leu = any(F[k]["consultas"] for k in F)
    oport, acomp, cont = classificar_lote(itens, hoje, cfg)
    est = load_json(ESTADO) if ESTADO.exists() else {}
    etapa = next((m for m in itens if m.get("tipo") == "etapa_emendas"), None)
    if etapa and etapa.get("status") == "desconhecido":     # formato novo não apaga a última situação reconhecida
        est["janela_emendas_tentativa"] = {k: etapa.get(k) for k in ("ano", "status", "url")} | {"lido_em": hoje.isoformat()}
        diag["janela_emendas"] = "desconhecido"
    elif etapa:
        est["janela_emendas"] = {k: etapa.get(k) for k in ("ano", "projeto", "situacao", "situacao_desde", "status", "inicio", "fim", "url")} | {
            "lido_em": hoje.isoformat(), "referencia": (cfg.get("orcamento") or {}).get("referencia_ploa")}
        diag["janela_emendas"] = est["janela_emendas"]["status"]
    if F["A"].get("formato_desconhecido"):
        diag["alerta_formato"] = "a página da LOA não trouxe a etapa 'Apresentação de emendas' reconhecível — o HTML pode ter mudado"
    if F["C"].get("formato_desconhecido"):
        diag["alerta_formato_senado"] = "a API do Senado não devolveu lista — o serviço /processo pode ter mudado"
    if F["A"].get("fora_do_ciclo"):
        diag["fora_do_ciclo"] = F["A"]["fora_do_ciclo"]
    if F["B"].get("cortados") or F["A"].get("cortados"):
        diag["cobertura_cortada"] = (F["B"].get("cortados") or []) + (F["A"].get("cortados") or [])
    if F["A"].get("formato_desconhecido_comunicados"):
        diag["alerta_formato_cmo"] = "a página de comunicados da CMO tem links e o leitor não reconheceu nenhum — o HTML pode ter mudado"
    if F["D"].get("paginas_nao_lidas"):                     # 03/10: publicado × lido nas notícias → maestro vê "parcial"
        diag["paginas_nao_lidas"] = F["D"]["paginas_nao_lidas"][:10]
    if F["D"].get("recuperadas"):
        diag["noticias_recuperadas"] = F["D"]["recuperadas"]
    diag["leitura_do_dia"] = {"comunicados_cmo": F["A"].get("comunicados_na_pagina"), "camara": F["B"]["itens"], "senado": F["C"]["itens"],
                              "noticias": F["D"]["itens"], "nao_lidas": F["D"].get("paginas_nao_lidas") or []}
    d0 = hoje.isoformat()
    hist = est.setdefault("historico", {})
    hist[d0] = {**{f"consultas_{k}": F[k]["consultas"] for k in F}, **{f"itens_{k}": F[k]["itens"] for k in F}, **cont, "falhou": not leu}
    seq, d = 0, hoje
    for _ in range(30):
        h = hist.get(d.isoformat())
        if not h or not h.get("falhou"):
            break
        seq += 1; d -= timedelta(days=1)
    if seq >= 2:
        diag["alerta"] = f"{seq} leituras seguidas sem resposta do Congresso — " + (sum((F[k]["falhas"] for k in F), []) + ["sem causa"])[0]
    campos = ("id", "titulo", "url", "data_publicacao", "fim", "categoria", "identificacao", "situacao", "norma", "propria")
    completo = leu and not any(F[k]["falhas"] for k in F)
    abertas = [{k: r.get(k) for k in campos} for r in oport.values()]
    acomp_l = [{k: a.get(k) for k in campos} | {"motivo": a["classificacao_ato"]["motivos"][0]} for a in acomp.values()]
    novos = {a["id"] for a in acomp_l} | {r["id"] for r in abertas}
    # as fontes leem JANELAS (60 dias, 15 dias): oportunidade com prazo futuro continua mesmo sem ser relida hoje
    abertas += [r for r in (est.get("abertas") or []) if r.get("id") not in novos and r.get("fim") and str(r["fim"]) >= d0]
    if not completo:                                        # leitura parcial: o que não foi relido hoje continua (com data)
        limite = (hoje - timedelta(days=60)).isoformat()
        acomp_l += [dict(a, nao_relido_em=d0) for a in (est.get("acompanhar") or [])
                    if a.get("id") not in novos and str(a.get("data_publicacao") or "") >= limite]
    est["abertas"] = sorted(abertas, key=lambda r: str(r.get("fim") or "9999"))
    ordem_cat = {"janela_emendas": 0, "emendas_a_abrir": 0, "emendas_formato": 0, "emendas_encerradas": 1, "comunicado_cmo": 1, "regra_emendas": 2, "regra_mrosc": 2,
                 "tributario_entidades": 3, "programa_com_entidades": 3, "fomento_parceria": 4, "regra_para_entidades": 4}
    acomp_l.sort(key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)
    est["acompanhar"] = sorted(acomp_l, key=lambda a: ordem_cat.get(a.get("categoria"), 5))[:200]
    est["ultima"] = {"em": now_iso(), "data": d0, "vereditos": cont, "falhas": sum((F[k]["falhas"] for k in F), [])[:10]}
    if F["D"].get("lidas_ate"):
        est["noticias_lidas_ate"] = F["D"]["lidas_ate"]
    est["historico"] = {k: v for k, v in hist.items() if k >= (hoje - timedelta(days=120)).isoformat()}
    write_json(ESTADO, est)
    diag.update({"vereditos": cont, "paginas_lidas": sum(F[k]["consultas"] for k in F), "links_total": len(itens),
                 "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"]})
    hosts = {"A": (cfg.get("orcamento") or {}).get("base", "https://www.congressonacional.leg.br"),
             "B": (cfg.get("camara") or {}).get("api", "https://dadosabertos.camara.leg.br/api/v2"),
             "C": (cfg.get("senado") or {}).get("api", "https://legis.senado.leg.br/dadosabertos"),
             "D": "https://www.camara.leg.br/noticias", "E": (cfg.get("convocacoes") or {}).get("url", "https://www6g.senado.leg.br")}
    falhas = [{"url": hosts[k], "erro": "congresso", "code": None, "waf": None, "causa": f"{k}: {f}"} for k in F for f in F[k]["falhas"]][:6]
    saude = [{"url": hosts[k], "http": 200, "bytes": F[k].get("bytes", 0), "itens": F[k]["itens"]} for k in F if F[k]["consultas"]]
    if not oport:
        je = (est.get("janela_emendas") or {})
        diag["motivo_zero"] = (f"{len(itens)} itens lidos (CMO A {F['A']['itens']} · Câmara B {F['B']['itens']} · Senado C {F['C']['itens']} · "
                               f"notícias D {F['D']['itens']} · convocações E {F['E']['itens']}): nenhuma janela de emendas aberta nem chamamento "
                               f"para OSC · {cont['ACOMPANHAR']} a acompanhar"
                               + (f" · emendas ao PLOA {je.get('ano')}: {je.get('status')}" if je else "")
                               if leu else "o Congresso não respondeu: " + (falhas[0]["causa"] if falhas else "sem leitura"))
    return {"sensor": MOTOR_ID, "achados": sorted(oport.values(), key=lambda r: str(r.get("fim") or "9999")), "falhas": falhas,
            "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return (est.get("acompanhar") or [])[:limite]


def janela_oficial() -> dict | None:
    """Situação oficial da apresentação de emendas lida na CMO (para a área de emendas)."""
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return est.get("janela_emendas")


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
