"""MOTOR DO JUDICIÁRIO — CNJ e TJGO (versão 1, 02/10/2026). Reúne os antigos `dje-tjgo` e `cnj-destinacoes`.

Parecer do conselho: docs/pareceres/motor-judiciario-cnj-tjgo.md.

O que os motores antigos faziam e por que rendiam zero (40 leituras cada, 0 achados):
  • `dje-tjgo` lia 5 páginas do portal do TJGO que dão 404 desde a reforma do site (/execucao-penal,
    /coordenadoria-de-execucao-penal, /editais-de-chamamento, /20140-prestacao-pecuniaria, /dje — verificado no navegador
    do titular em 02/10/2026). Na nuvem o portal recusa IP estrangeiro, então o que sobrava era o Jusbrasil, que é
    republicador e devolvia a navegação dos diários de todo o país (12CJM, AAM…), e o MPGO, que é outro órgão. A coleta
    no computador do titular leria as mesmas páginas mortas — e, mesmo que achasse, o scripts/coleta_brasil.py não
    grava os achados na base.
  • `cnj-destinacoes` lia a home do CNJ, a página de licitações de COMPRAS do CNJ e /penas-e-medidas-alternativas/ (404).

Onde o Judiciário publica o que interessa a uma entidade (verificado ao vivo em 02/10/2026):
  • cada COMARCA abre o seu edital de seleção de projetos com recursos de prestações pecuniárias (Resolução CNJ
    558/2024; Código de Normas da Corregedoria de Goiás, art. 257) e o TJGO anuncia na Agência de Notícias, com o PDF
    do edital anexado (/files/<ano>/<mês>/… ou /images/docs/ccs/…). Exemplos: Goiânia, 1ª Vara de Execução Penal,
    Edital 01/2026 (12/01, habilitação até 30/01); Rio Verde, Edital 01/2026 (03/07, inscrições até 30/09);
    Piracanjuba, Cocalzinho de Goiás, Itaberaí;
  • a entidade precisa estar cadastrada no BANCO DE PROJETOS SOCIAIS da Corregedoria (corregedoria.tjgo.jus.br/basesocial);
  • o Portal do CNJ republica editais dos tribunais (busca ?s=) e publica a regra nacional;
  • o PNCP traz os credenciamentos do próprio TJGO para entidades sem fins lucrativos (o motor 04 já lê; aqui se cruza);
  • o DJEN (API de comunicações do CNJ) só traz intimações de processos, com nomes de réus — não é fonte de edital.

Como funciona (sem IA, sem tokens, biblioteca-padrão):
  Fonte A — RSS da Agência de Notícias do TJGO, paginado (&limitstart=8, 16…), até a primeira página toda já vista;
            carga inicial de 150 dias em parcelas. Rota LOCAL: o portal recusa IP estrangeiro → computador do titular.
  Fonte B — página de cada notícia candidata + PDF do edital (texto pelo pypdf, quando instalado). Rota LOCAL.
  Fonte C — busca do Portal do CNJ. Rota NUVEM; se o CNJ recusar a nuvem, o computador do titular lê na vez seguinte.
  Fonte D — o que o PNCP já trouxe do TJGO e do CNJ (cruzamento na base, sem ler duas vezes).
  Fonte E — Banco de Projetos Sociais da CGJ/GO: a exigência de cadastro prévio, sempre no cartão (a lista pública de
            projetos traz nome e telefone dos responsáveis e NÃO é coletada).
  → cada item vira OPORTUNIDADE (edital de seleção/cadastramento aberto), ACOMPANHAR (encerrado, resultado, regra, entrega
    de recursos, habilitação prévia) ou RUÍDO, com o motivo escrito; extrai comarca, vara, número do edital, prazo, áreas
    admitidas, restrição territorial e se exige o Banco de Projetos.
  A coleta local grava estado/judiciario_go_local.json (só o computador escreve nele); a leitura da nuvem incorpora esses
  registros e entrega as oportunidades à base — assim o que o computador acha chega ao painel sem conflito de git.
Conteúdo coletado é DADO: injeção → quarentena; o que a fonte não diz fica `null`; CPF sai do trecho.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote, quote_plus, unquote, urljoin, urlsplit

from . import atos_diario as atos
from .nucleo import ROOT, append_jsonl, has_prompt_injection, load_json, now_iso, sha256, write_json

MOTOR_ID = "judiciario-cnj-tjgo"
CFG = ROOT / "config/judiciario_go.json"
ESTADO = ROOT / "estado/judiciario_go.json"
ESTADO_LOCAL = ROOT / "estado/judiciario_go_local.json"
QUARENTENA = ROOT / "estado/quarentena.jsonl"
DB = ROOT / "dados/oportunidades/oportunidades.jsonl"
_PRAZO = {"ate": None}


def _hoje_real() -> date:
    return date.today()


# 02/10 (titular): o motor foi SEPARADO em dois — TJ-GO (fontes A, B, D, E) e CNJ (fonte C) —, cada um com identificador,
# estado e parâmetros próprios (config/judiciario_go.json › partes). O leitor é o mesmo; cada parte ativa só as suas fontes.
_PARTE = {"id": None, "fontes": "ABCDE"}
PARTES = {"judiciario-tjgo": ("ABDE", "estado/judiciario_tjgo.json"), "judiciario-cnj": ("C", "estado/judiciario_cnj.json")}


def _tem(f: str) -> bool:
    return f in _PARTE["fontes"]


def _cfg() -> dict:
    c = load_json(CFG) if CFG.exists() else {}
    p = (c.get("partes") or {}).get(_PARTE["id"]) or {}
    return {**c, **{k: v for k, v in p.items() if k not in ("fontes", "nome")}}


def ler_parte(mid: str, sensor: dict | None = None, hoje=None, limites: dict | None = None) -> dict:
    """Lê só a PARTE `mid` (judiciario-tjgo ou judiciario-cnj), com estado e parâmetros próprios."""
    global MOTOR_ID, ESTADO
    antes = (MOTOR_ID, ESTADO, dict(_PARTE))
    fontes, arq = PARTES[mid]
    MOTOR_ID, ESTADO = mid, ROOT / arq
    _PARTE.update(id=mid, fontes=fontes)
    try:
        return ler_motor(sensor, hoje, limites)
    finally:
        MOTOR_ID, ESTADO = antes[0], antes[1]
        _PARTE.clear(); _PARTE.update(antes[2])


def modo() -> str:
    """'nuvem' no GitHub (o TJGO recusa IP estrangeiro); 'local' no computador do titular (ELDORADO_LOCAL_BR=1)."""
    if os.environ.get("GITHUB_ACTIONS") and not os.environ.get("ELDORADO_LOCAL_BR"):
        # 03/10 (titular): com a ponte da Hostgator (IP brasileiro) configurada, o GitHub lê também o TJGO
        from .ponte_brasil import configurada
        return "ponte" if configurada() else "nuvem"
    return "local"


def _tempo_esgotado() -> bool:
    return _PRAZO["ate"] is not None and time.monotonic() > _PRAZO["ate"]


def _N(t) -> str:
    return re.sub(r"\s+", " ", atos.sem_acento(str(t or "")).upper()).strip()


def _limpo(t) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", str(t or "")))).strip()


# ─────────────────────────── rede ───────────────────────────
def _abrir(url: str, binario: bool = False, max_bytes: int = 4_000_000):
    """Texto (ou bytes) de uma URL pública. Isolado para os testes trocarem a rede por respostas gravadas."""
    if binario:
        from .diario_goiania import _get as _get_bytes
        return _get_bytes(url, timeout=60, max_bytes=max_bytes, aceitar="application/pdf,*/*")
    from .camara_goiania import _get_texto
    return _get_texto(url, timeout=30, max_bytes=max_bytes)


def _get(url: str, cfg: dict, fonte: dict, binario: bool = False, max_bytes: int = 4_000_000):
    from .camara_goiania import Recusa
    ritmo = cfg.get("ritmo", {})
    ultimo = None
    for _ in range(2):
        if _tempo_esgotado():
            raise RuntimeError("prazo da execução esgotado — o restante fica para a próxima passagem")
        try:
            r = _abrir(url, binario=binario, max_bytes=max_bytes)
            fonte["consultas"] = fonte.get("consultas", 0) + 1
            fonte["bytes"] = fonte.get("bytes", 0) + len(r)
            time.sleep(float(ritmo.get("pausa_segundos", 1.5)))
            return r
        except Recusa as exc:
            ultimo = exc
            fonte["recusado"] = True
            break
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            if getattr(exc, "code", None) in (400, 401, 404, 410) or isinstance(exc, ValueError):
                break
            time.sleep(float(ritmo.get("espera_erro_segundos", 4)))
    raise RuntimeError(_erro(ultimo))


def _erro(exc) -> str:
    code = getattr(exc, "code", None)
    nome = type(exc).__name__
    return (str(exc) if nome in ("Recusa", "RuntimeError") else f"HTTP {code}" if code else nome)[:160]


# ─────────────────────────── leitura: RSS, notícia, PDF ───────────────────────────
def _dia_rss(s: str) -> str | None:
    try:
        return parsedate_to_datetime(s).date().isoformat()
    except Exception:  # noqa: BLE001
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s or "")
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def itens_do_rss(xml: str) -> list[dict]:
    """RSS 2.0 do Joomla (Agência de Notícias do TJGO): título, link, data, categoria e o resumo."""
    try:
        raiz = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    except ET.ParseError:
        return []
    out = []
    for it in raiz.iter("item"):
        def g(tag):
            e = it.find(tag)
            return (e.text or "").strip() if e is not None and e.text else ""
        url = g("link") or g("guid")
        if not url:
            continue
        out.append({"titulo": _limpo(g("title")), "url": url, "descricao": _limpo(g("description"))[:1200],
                    "publicado": _dia_rss(g("pubDate")), "categoria": _limpo(g("category")) or None})
    return out


# notícia que PODE ser edital de destinação a entidades (decide se a página é aberta)
CANDIDATA = re.compile(
    r"PRESTAC(?:AO|OES) PECUNIARIA|PENAS? PECUNIARIA|PENAS? ALTERNATIVA|MEDIDAS ALTERNATIVAS|TRANSACAO PENAL|RECURSOS DE PENA|"
    r"PROJETOS? SOCIA|FINALIDADE SOCIAL|DESTINACAO SOCIAL|DESTINACAO DE (?:RECURSOS|VALORES)|BANCO DE PROJETOS|BASE ?SOCIAL|"
    r"CADASTRAMENTO DE (?:ENTIDADES|INSTITUICOES)|CREDENCIAMENTO DE (?:ENTIDADES|INSTITUICOES)|"
    r"ENTIDADES? (?:SEM FINS|SOCIA|BENEFICENTE|FILANTROP|PUBLICAS OU PRIVADAS)|INSTITUICOES (?:PUBLICAS|PRIVADAS|SOCIAIS)|"
    r"\bVEPEMA\b|EXECUCAO PENAL.{0,40}EDITAL|EDITAL.{0,60}(?:ENTIDADES|PROJETOS|INSTITUICOES)")


def candidata(titulo: str, descricao: str = "") -> bool:
    return bool(CANDIDATA.search(_N(f"{titulo} {descricao}")))


def _url_segura(u: str) -> str:
    """'/images/docs/ccs/03.07 - Edital 01-2026.pdf' (espaços no nome, como o TJGO publica) → URL que o urllib abre."""
    p = urlsplit(u)
    return p._replace(path=quote(unquote(p.path), safe="/:@!$&'()*+,;=-._~")).geturl()


_SCRIPT = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_A = re.compile(r"<a\b[^>]*?href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.S | re.I)
_TIME = re.compile(r"<time\b[^>]*datetime\s*=\s*[\"'](\d{4}-\d{2}-\d{2})", re.I)
_CORPO = re.compile(r"class\s*=\s*[\"'][^\"']*\b(?:item-page|entry-content)\b|itemprop\s*=\s*[\"']articleBody[\"']|<article\b", re.I)
_META_PUB = re.compile(r"<meta\b[^>]*property\s*=\s*[\"']article:published_time[\"'][^>]*content\s*=\s*[\"'](\d{4}-\d{2}-\d{2})", re.I)
_FIM_ARTIGO = re.compile(r"sharer|shareArticle|class=[\"'][^\"']*(?:share|social|pager|related|tags)", re.I)


def artigo(pagina_html: str, url: str, titulo: str = "", hosts_pdf=()) -> dict:
    """Notícia do TJGO (Joomla) ou do CNJ (WordPress): texto do corpo, data e os PDFs anexados AO CORPO (os PDFs do
    rodapé do portal não contam)."""
    h = _SCRIPT.sub(" ", pagina_html or "")
    # Joomla 4 do TJGO: <div class="com-content-article item-page"> (verificado em 02/10/2026); WordPress do CNJ: entry-content/article
    mi = _CORPO.search(h)
    ini = h.rfind("<", 0, mi.start() + 1) if mi else -1
    if ini < 0 and titulo:
        ini = h.find(_html.escape(titulo[:60], quote=False))
    if ini < 0:
        ini = 0
    fim_m = _FIM_ARTIGO.search(h, ini + 200)
    fim = h.rfind("<", ini, fim_m.start() + 1) if fim_m else min(len(h), ini + 80_000)
    trecho = h[ini:fim]
    texto = _limpo(trecho)
    for corte in ("(Texto:", "Facebook LinkedIn", "Compartilhe"):
        k = texto.find(corte)
        if k > 200:
            texto = texto[:k]
    hosts = {x.lower() for x in hosts_pdf} or {(urlsplit(url).hostname or "").lower()}
    pdfs, vistos = [], set()
    for m in _A.finditer(trecho):
        alvo = _url_segura(urljoin(url, _html.unescape(m.group(1).strip())))
        caminho = urlsplit(alvo).path.lower()
        if not caminho.endswith(".pdf") or (urlsplit(alvo).hostname or "").lower() not in hosts or alvo in vistos:
            continue
        vistos.add(alvo)
        pdfs.append({"url": alvo, "rotulo": _limpo(m.group(2))[:120]})
    # 03/10 (teste do motor 11): no CNJ os <time> da página são da barra lateral ("notícias recentes") — uma notícia de
    # 21/07/2020 saía com a data de hoje e o prazo "18 de agosto" virava 2027. A data certa está no meta do artigo.
    pub = _META_PUB.search(h)
    if pub:
        publicado = pub.group(1)
    else:
        txt_pub = re.search(r"(?:Post publicado|Publicad[oa] em)\s*:?\s*(\d{1,2}) de ([a-zç]+) de (\d{4})", _limpo(h[ini:ini + 8000]), re.I)
        mes = _MESES.get(_N(txt_pub.group(2)).lower()) if txt_pub else None
        if txt_pub and mes:
            publicado = f"{txt_pub.group(3)}-{mes:02d}-{int(txt_pub.group(1)):02d}"
        else:
            data = _TIME.search(h[max(0, ini - 1500): fim])           # só perto do corpo; nunca a página inteira
            publicado = data.group(1) if data else None
    return {"texto": texto[:20_000], "publicado": publicado, "pdfs": pdfs[:6],
            "banco_projetos": bool(re.search(r"basesocial|BANCO DE PROJETOS SOCIAIS", trecho, re.I))}


# ─────────────────────────── extração ───────────────────────────
_PARADA = {"EXECUCAO", "EXECUCOES", "PENAS", "PENA", "MEDIDAS", "PROJETOS", "PROJETO", "PRESTACAO", "PRESTACOES", "RECURSOS",
           "ENTIDADES", "SELECAO", "JUSTICA", "TRIBUNAL", "INFANCIA", "FAMILIA", "FAZENDA", "FAZENDAS", "CRIMES", "VIOLENCIA",
           "GARANTIAS", "TRANSITO", "REGISTROS", "ORFAOS", "SUCESSOES", "PRECATORIOS", "CORREGEDORIA", "DIRETORIA", "FORO",
           "VARA", "VARAS", "JUIZADO", "COMARCA", "EDITAL", "SEGURANCA", "EDUCACAO", "SAUDE", "PROCESSAMENTO", "UNIDADE",
           "GOIAS", "ESTADO", "CODIGO", "NORMAS", "PORTARIA", "RESOLUCAO", "CNJ", "TJGO", "CGJ", "UPJ", "MINISTERIO", "PUBLICO",
           "POLICIA", "BANCO", "ATENDIMENTO", "ALTERNATIVAS", "INTERESSE", "CUNHO", "NATUREZA", "INSTITUICOES", "BRASIL",
           "PENAL", "PENAIS", "CRIMINAL", "CRIMINAIS", "CIVEL", "CIVEIS", "ESPECIAL", "ESPECIAIS", "PUBLICA", "PUBLICAS",
           "AUDITORIA", "MILITAR", "ELEITORAL", "PRIMEIRA", "SEGUNDA", "TERCEIRA"}
_CONECTORES = {"DE", "DO", "DA", "DOS", "DAS", "D'"}
_LIG = r"(?:de|do|da|dos|das|d'|D')"
_NOME = r"[A-ZÀ-Ý][\wÀ-ÿ'’\-]+(?:\s+(?:" + _LIG + r"\s+)?[A-ZÀ-Ý][\wÀ-ÿ'’\-]+){0,3}"
_COMARCA_RX = re.compile(r"[Cc]omarca\s+de\s+(" + _NOME + r")")
_LUGAR_RX = re.compile(r"\b(?:de|em|da|do)\s+(" + _NOME + r")")
_APELIDOS = {"VEPEMA": "Goiânia"}         # Vara de Execução de Penas e Medidas Alternativas de Goiânia


def _ok_lugar(nome: str) -> str | None:
    partes = nome.split()
    while partes and (atos.sem_acento(partes[0]).upper().strip("'’") in _PARADA or partes[0].upper() in _CONECTORES):
        partes = partes[1:]                      # "Execução Penal de Rio Verde" → começa de novo depois do "de"
    if not partes:
        return None
    nome = " ".join(partes)
    n = atos.sem_acento(nome).upper()
    if n in _PARADA or len(n) < 3 or re.fullmatch(r"(?:GO|GOIAS|BRASIL)", n):
        return None
    return re.sub(r"\s+(?:" + _LIG + r")$", "", nome).strip()


def comarca_de(titulo: str, texto: str = "") -> str | None:
    """'1ª Vara de Execução Penal de Rio Verde abre edital…' → 'Rio Verde'; 'Juiz abre edital … em Cocalzinho de Goiás'
    → 'Cocalzinho de Goiás'; 'Vepema lança edital…' → 'Goiânia'. A 'Comarca de X' do texto vale mais que o título."""
    for fonte in (texto[:1500], titulo):
        m = _COMARCA_RX.search(fonte or "")
        if m and _ok_lugar(m.group(1)):
            return _ok_lugar(m.group(1))
    T = _N(titulo)
    for apelido, nome in _APELIDOS.items():
        if re.search(rf"\b{apelido}\b", T):
            return nome
    achados = []
    for m in _LUGAR_RX.finditer(titulo or ""):
        bruto = m.group(1)
        # "de Execução Penal de Rio Verde": o grupo engole o segundo "de" — reparte e fica com o último lugar válido
        for pedaco in re.split(r"\s+" + _LIG + r"\s+(?=[A-ZÀ-Ý])", bruto):
            lugar = _ok_lugar(pedaco)
            if lugar:
                achados.append((m.start(), lugar))
        lugar = _ok_lugar(bruto)
        if lugar and len(lugar.split()) > 1:
            achados.append((m.start(), lugar))
    if not achados:
        return None
    achados.sort(key=lambda x: (x[0], -len(x[1])))
    # o lugar mais longo dentro do mesmo trecho ("Cocalzinho de Goiás" vence "Cocalzinho")
    melhor = achados[-1][1]
    for _, l in achados:
        if melhor in l and len(l) > len(melhor):
            melhor = l
    return melhor


_VARA_RX = re.compile(r"((?:\d+\s*[ªºa]\s+)?(?:Vara|Juizado|UPJ|Vepema|VEP)\b[^,.;:()]{0,80}?)(?=\s+(?:da|de|do)\s+Comarca|\s+(?:abre|publica|lança|lanca|torna|seleciona|divulga)\b|[,.;:()]|$)")
_NUM_RX = re.compile(r"\bEdital\s+(?:de\s+[\wÀ-ÿ ]{3,40}?\s+)?(?:n[º°o.]*\s*)?(\d{1,4})\s*[/.\-]\s*(20\d{2})", re.I)
_AREAS = [("seguranca_publica", r"SEGURANCA PUBLICA"), ("educacao", r"\bEDUCACAO\b"), ("saude", r"\bSAUDE\b"),
          ("assistencia_social", r"ASSISTENCIA SOCIAL|VULNERABILIDADE"), ("crianca_adolescente", r"CRIANCA|ADOLESCENTE"),
          ("idoso", r"\bIDOSO|TERCEIRA IDADE"), ("dependencia_quimica", r"DEPENDENTES? QUIMIC|DEPENDENCIA QUIMICA"),
          ("meio_ambiente", r"MEIO AMBIENTE"), ("cultura", r"\bCULTURA"), ("esporte", r"\bESPORTE"),
          ("pessoa_com_deficiencia", r"PESSOAS? COM DEFICIENCIA")]
_TERRIT_RX = re.compile(r"(?:desenvolvam|sediad[ao]s?|com sede|atuem|atuantes?|instalad[ao]s?)[^.]{0,90}?(?:munic[íi]pio|comarca|cidade)\s+de\s+("
                        + _NOME + r")", re.I)
_VALOR = re.compile(r"R\$\s?\d[\d.]*(?:,\d{2})?(?:\s?(?:mil|milh[õo]es|milh[ãa]o))?", re.I)
_MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
          "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}


def _prazo_relativo(texto: str, publicado: str | None) -> str | None:
    """'requerimento de Habilitação até o dia 30 deste mês' → último dia citado no mês da publicação; 'até o dia 10 do
    próximo mês' → mês seguinte. Só com o verbo do prazo por perto (inscrição, habilitação, requerimento, envio)."""
    if not publicado:
        return None
    T = _N(texto)
    m = re.search(r"(?:INSCRI|HABILITA|REQUERIMENTO|CADASTR|ENVI|PROTOCOL|APRESENT)[^.]{0,80}?ATE O DIA (\d{1,2})\s+"
                  r"(DESTE MES|DO MES CORRENTE|DO CORRENTE MES|DO PROXIMO MES|DO MES SEGUINTE)", T)
    if not m:
        return None
    try:
        p = date.fromisoformat(publicado)
        ano, mes = p.year, p.month
        if "PROXIMO" in m.group(2) or "SEGUINTE" in m.group(2):
            ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
        return date(ano, mes, int(m.group(1))).isoformat()
    except ValueError:
        return None


_PERIODO_ANO = re.compile(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\s*(?:a|at[ée]|e)\s*(?:o dia\s*)?(\d{1,2})/(\d{1,2})/(\d{4})", re.I)


def prazo(texto: str, publicado: str | None) -> tuple[str | None, str | None]:
    from .gife_editais import prazo_do_texto
    # 03/10 (teste do motor 07): período com ano escrito ("de 20/07 a 18/08/2020") manda — o edital de Itaberaí era de 2020
    mp = _PERIODO_ANO.search(texto or "")
    if mp and re.search(r"INSCRI|PROTOCOL|PEDIDO|HABILITA|RECEB|APRESENT|ENVI|CADASTR|PERIODO", _N(texto[max(0, mp.start() - 200):mp.start()])):
        try:
            return date(int(mp.group(6)), int(mp.group(5)), int(mp.group(4))).isoformat(), mp.group(0)
        except ValueError:
            pass
    fim, _fluxo, trecho = prazo_do_texto(texto, publicado)
    # data SEM ano empurrada para o ano seguinte (ex.: "até 18/08" lido em setembro → agosto do ano que vem) não é prazo:
    # fica a confirmar no edital — evita oportunidade "aberta" que na verdade já encerrou
    if fim and publicado and trecho and not re.search(r"\b20\d{2}\b", str(trecho)):
        try:
            if (date.fromisoformat(fim) - date.fromisoformat(publicado)).days > 200:
                fim, trecho = None, None
        except ValueError:
            pass
    if not fim:
        fim = _prazo_relativo(texto, publicado)
        trecho = "prazo relativo ('até o dia N deste mês') resolvido pela data da publicação" if fim else None
    return fim, trecho


def extrair(titulo: str, texto: str, publicado: str | None) -> dict:
    full = f"{titulo}. {texto}"
    T = _N(full)
    num = _NUM_RX.search(full)
    vara = _VARA_RX.search(texto[:2500]) or _VARA_RX.search(titulo)
    terr = _TERRIT_RX.search(texto)
    so_local = bool(re.search(r"ATUACAO (?:SEJA |DEVE SER |ESTEJA )?(?:NO|EM) (?:O )?MUNICIPIO|SEDIAD[AO]S? NO MUNICIPIO|ATUEM NO MUNICIPIO|"
                              r"ATUANTES? NO MUNICIPIO|NO AMBITO DA (?:COMARCA|CIRCUNSCRICAO)", _N(texto)))
    fim, trecho = prazo(full, publicado)
    areas = [k for k, rx in _AREAS if re.search(rx, T)]
    return {"comarca": comarca_de(titulo, texto), "vara": re.sub(r"\s+", " ", vara.group(1)).strip()[:90] if vara else None,
            "numero_edital": f"{int(num.group(1)):02d}/{num.group(2)}" if num else None, "fim": fim, "trecho_prazo": trecho,
            "areas_admitidas": areas or None,
            "restricao_territorial": _ok_lugar(terr.group(1)) if terr else (comarca_de(titulo, texto) if so_local else None),
            "valor_texto": (_VALOR.search(full) or [None])[0] if _VALOR.search(full) else None,
            "exige_banco_projetos": bool(re.search(r"BANCO DE PROJETOS|BASESOCIAL|BASE SOCIAL", T)),
            "forma_inscricao": ("e-mail" if re.search(r"E-?MAIL|ENDERECO ELETRONICO", T) else None) if re.search(r"INSCRI|HABILITA|REQUERIMENTO", T) else None}


# ─────────────────────────── classificação ───────────────────────────
DESTINACAO = re.compile(r"PRESTAC(?:AO|OES) PECUNIARIA|PENAS? PECUNIARIA|PENAS? (?:E MEDIDAS )?ALTERNATIVA|TRANSACAO PENAL|RECURSOS DE PENA|"
                        r"DESTINACAO DE (?:RECURSOS|VALORES)|VALORES (?:ARRECADADOS|DEPOSITADOS)|FINALIDADE SOCIAL|DESTINACAO SOCIAL|"
                        r"BANCO DE PROJETOS SOCIAIS|\bVEPEMA\b|PENA DE MULTA|PERDA DE BENS")
SELECAO = re.compile(r"\bEDITA(?:L|IS)\b|SELECAO D[EO]S? (?:PROJETOS|ENTIDADES|INSTITUICOES)|SELECIONA(?:R)? PROJETOS|CADASTRAMENTO|CREDENCIAMENTO|"
                     r"HABILITACAO|CHAMAMENTO|INSCRICOES? (?:ABERTAS|ATE)|PODEM SE INSCREVER|APRESENTAR (?:PROJETOS|PROPOSTAS)")
ABERTURA = re.compile(r"\bABRE\b|\bABRIU\b|\bLANCA\b|\bLANCOU\b|\bPUBLICA\b|\bPUBLICOU\b|ESTAO ABERTAS|ABERTAS? AS INSCRI|"
                      r"RECEBE (?:PROJETOS|PROPOSTAS|INSCRI)|PRAZO PARA|INSCRICOES ATE|PODEM SE INSCREVER|SELECIONA PROJETOS")
RESULTADO = re.compile(r"\bRESULTADO\b|HOMOLOGA|SELECIONAD[OA]S\b|CONTEMPLAD[OA]S|\bENTREGA\b|\bENTREGOU|\bENTREGUE|REPASS|BENEFICIAD[OA]S|"
                       r"RECEBEM (?:RECURSOS|EQUIPAMENTOS)|CERIMONIA|DOACAO DE EQUIPAMENTOS|DESTINA R\$|DESTINOU|AQUISICAO DE")
REGRA = re.compile(r"\bPROVIMENTO\b|RESOLUCAO (?:N[O.]?\s*)?(?:558|154)|CODIGO DE NORMAS|ART(?:IGO)?\.? 257|NOVAS REGRAS|DIRETRIZES|"
                   r"REGULAMENTA|NORMATIZ")
GOIAS = re.compile(r"\bGOIAS\b|\(GO\)|\bTJGO\b|\bGOIAN[OA]S?\b|\bGOIANIA\b|CGJ/GO|CORREGEDORIA-GERAL DA JUSTICA DE GOIAS")
CREDENC_OSC = re.compile(r"CREDENCIAMENTO DE (?:ENTIDADES|INSTITUICOES|ASSOCIACOES|COOPERATIVAS)[^.]{0,80}SEM FINS LUCRATIVOS|"
                         r"ENTIDADES SEM FINS LUCRATIVOS APTAS")
RUIDO_FORTE = re.compile(r"CONCURSO PUBLICO|PROCESSO SELETIVO (?:SIMPLIFICADO )?PARA (?:ESTAGI|SERVIDOR|CONCILIADOR|JUIZ)|\bESTAGIARIOS?\b|"
                         r"\bLEILAO\b|PREGAO|LICITACAO|JUIZ(?:ES)? LEIGOS?|CONCILIADORES|RESIDENCIA JURIDICA|VESTIBULAR|"
                         r"REMOCAO|PROMOCAO DE MAGISTRAD|EDITAL DE (?:CITACAO|INTIMACAO|PRACA|LEILAO|PROCLAMAS)")


def classificar_item(m: dict, hoje: date, cfg: dict | None = None) -> dict:
    cfg = cfg or {}
    titulo, texto = m.get("titulo") or "", m.get("texto") or m.get("descricao") or ""
    T = _N(f"{titulo} {texto[:6000]}")
    TT = _N(titulo)
    ex = extrair(titulo, texto, m.get("publicado"))
    base = {**ex, "categoria": None, "regime": "destinacao_pena_pecuniaria", "motivos": [], "sinais": []}
    destina = bool(DESTINACAO.search(T))
    if m.get("fonte") == "C" and not GOIAS.search(T):
        # republicação do CNJ de outro estado: o edital de prestação pecuniária só aceita entidades daquela comarca
        if destina and REGRA.search(T) and not SELECAO.search(TT):
            return {**base, "veredito": "ACOMPANHAR", "categoria": "regra", "regime": "regra_destinacao",
                    "motivos": ["regra nacional sobre a gestão e a destinação das prestações pecuniárias (CNJ)"]}
        return {**base, "veredito": "RUIDO", "categoria": "ruido",
                "motivos": ["notícia do CNJ sobre outro estado — edital de comarca só aceita entidades daquela comarca"]}
    if CREDENC_OSC.search(T):
        base["regime"] = "credenciamento_osc_judiciario"
        if ex["fim"] and ex["fim"] < hoje.isoformat():
            return {**base, "veredito": "ACOMPANHAR", "categoria": "credenciamento_encerrado",
                    "motivos": [f"credenciamento de entidades sem fins lucrativos do Judiciário encerrado em {ex['fim']}"]}
        return {**base, "veredito": "OPORTUNIDADE", "categoria": "credenciamento",
                "motivos": [f"credenciamento de entidades sem fins lucrativos aberto{' até ' + ex['fim'] if ex['fim'] else ''} — conferir o edital"]}
    if RUIDO_FORTE.search(TT) and not destina:
        return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["concurso, licitação, leilão ou edital processual — não é destinação a entidades"]}
    if not destina:
        return {**base, "veredito": "RUIDO", "categoria": "ruido", "motivos": ["notícia sem destinação de recursos a entidades"]}
    resultado_no_titulo = bool(RESULTADO.search(TT)) and not ABERTURA.search(TT)
    if SELECAO.search(T) and not resultado_no_titulo:
        onde = f" — comarca de {ex['comarca']}" if ex["comarca"] else ""
        exige = " · exige cadastro no Banco de Projetos Sociais da CGJ/GO" if ex["exige_banco_projetos"] else ""
        assoc = _N((cfg or {}).get("comarca_da_associacao") or "Goiânia")
        if ex["restricao_territorial"] and _N(ex["restricao_territorial"]) != assoc:
            # 03/10 (teste do motor 11): o edital exige atuação na própria comarca — continua visível (decisão do titular
            # de 02/10), mas o aviso fica no motivo para não parecer que a A.M.C. pode concorrer sem conferir
            exige += f" · ATENÇÃO: restrito a entidades que atuam em {ex['restricao_territorial']} — conferir se a A.M.C. pode concorrer"
        if ex["fim"] and ex["fim"] >= hoje.isoformat():
            return {**base, "veredito": "OPORTUNIDADE", "categoria": "edital_destinacao",
                    "motivos": [f"edital de seleção de projetos com recursos de prestação pecuniária{onde}, inscrições até {ex['fim']}{exige}"]}
        if ex["fim"]:
            return {**base, "veredito": "ACOMPANHAR", "categoria": "edital_encerrado",
                    "motivos": [f"edital de destinação{onde} encerrado em {ex['fim']} — a comarca costuma abrir o próximo no mesmo período do ano"]}
        pub = m.get("publicado")
        janela = int(cfg.get("janela_oportunidade_sem_prazo_dias", 20))
        if pub and pub >= (hoje - timedelta(days=janela)).isoformat() and ABERTURA.search(T):
            return {**base, "veredito": "OPORTUNIDADE", "categoria": "edital_destinacao", "prazo_a_confirmar": True,
                    "motivos": [f"edital de destinação aberto{onde} (publicado em {pub}); o prazo não está no texto da notícia — conferir no PDF{exige}"]}
        return {**base, "veredito": "ACOMPANHAR", "categoria": "edital_sem_prazo",
                "motivos": [f"edital de destinação{onde} sem prazo legível — conferir no edital"]}
    if resultado_no_titulo or RESULTADO.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "resultado_ou_entrega",
                "motivos": ["resultado, entrega ou repasse de recursos de pena a entidades — mostra quem recebe e quando a comarca destina"]}
    if REGRA.search(T):
        return {**base, "veredito": "ACOMPANHAR", "categoria": "regra", "regime": "regra_destinacao",
                "motivos": ["regra sobre a gestão e a destinação das prestações pecuniárias (CNJ ou Corregedoria)"]}
    return {**base, "veredito": "ACOMPANHAR", "categoria": "noticia_destinacao",
            "motivos": ["notícia sobre destinação de recursos de pena — acompanhar"]}


def chaves(m: dict, c: dict) -> list[str]:
    """Um edital visto na notícia do TJGO, no PDF e na republicação do CNJ é UM registro."""
    ks = []
    com = _N(c.get("comarca") or "")
    if com and c.get("numero_edital"):
        ks.append(f"ed:{com}:{c['numero_edital']}")
    if com and c.get("fim") and c.get("categoria") in ("edital_destinacao", "edital_encerrado"):
        ks.append(f"pz:{com}:{c['fim']}")
    for p in (m.get("pdfs") or [])[:1]:
        ks.append("pdf:" + p["url"].split("?")[0])
    ks.append("url:" + (m.get("url") or "").split("?")[0].rstrip("/"))
    return ks


_ORIGEM = {"A": "TJGO — Agência de Notícias", "B": "TJGO — edital (PDF)", "C": "Portal do CNJ", "D": "PNCP", "E": "Corregedoria (CGJ/GO)"}


def _registro(c: dict, m: dict, ks: list[str]) -> dict:
    titulo = atos.mascarar_pii(m.get("titulo") or "")
    ev = atos.mascarar_pii(" ".join(str(x) for x in (titulo, (m.get("texto") or m.get("descricao") or "")[:900]) if x))[:900]
    pdf = (m.get("pdfs") or [{}])[0].get("url")
    org = "Tribunal de Justiça do Estado de Goiás" + (f" — {c['vara']}" if c.get("vara") else "") if m.get("fonte") in ("A", "B") else \
        "Conselho Nacional de Justiça (republicação)" if m.get("fonte") == "C" else _ORIGEM.get(m.get("fonte"), "Judiciário")
    nacional = m.get("fonte") == "C" and not c.get("comarca") and not re.search(r"GOIAS|\(GO\)|GOIANIA", _N(m.get("titulo")))
    return {
        "id": sha256(f"jud|{ks[0]}".encode())[:20], "status": "capturada",
        "titulo": (f"{c['comarca']} — " if c.get("comarca") else "") + titulo[:260],
        "url": pdf or m.get("url"), "url_noticia": m.get("url"), "url_documento": pdf,
        "fonte_id": MOTOR_ID, "fonte_nome": _ORIGEM.get(m.get("fonte"), "Judiciário"), "orgao": org,
        "territorio": "BR" if nacional else (f"GO/{c['comarca']}" if c.get("comarca") else "GO"),
        "uf": None if nacional else "GO", "municipio": f"GO/{c['comarca']}" if c.get("comarca") else None,
        "nivel": "federal" if nacional else "estadual", "comarca": c.get("comarca"), "vara": c.get("vara"),
        "tipo_fonte": "judiciario_destinacao", "confianca": "primaria" if m.get("fonte") in ("A", "B") else "secundaria",
        "forma_divulgacao": {"A": "noticia_tjgo", "B": "pdf_tjgo", "C": "noticia_cnj"}.get(m.get("fonte")),
        "coletado_em": now_iso(), "data_publicacao": m.get("publicado"), "fim": c.get("fim"), "prazo_texto": c.get("fim"),
        "prazo_a_confirmar": bool(c.get("prazo_a_confirmar")), "numero_edital": c.get("numero_edital"),
        "areas_admitidas": c.get("areas_admitidas"), "restricao_territorial": c.get("restricao_territorial"),
        "exige_banco_projetos": c.get("exige_banco_projetos"), "valor_texto": c.get("valor_texto"),
        "regime": c.get("regime"), "categoria": c.get("categoria"), "chaves": ks,
        "evidencia": ev, "hash_evidencia": sha256(ev.encode()),
        "classificacao_ato": {"veredito": c["veredito"], "regime": c.get("regime"), "motivos": c["motivos"], "sinais": c.get("sinais") or [],
                              "tipo": "abertura" if c["veredito"] == "OPORTUNIDADE" else "acompanhamento"},
        "sensor": MOTOR_ID, "forca_lexica": 3,
    }


def classificar_lote(itens: list[dict], hoje: date, cfg: dict | None = None) -> tuple[dict, dict, dict]:
    """Dedupe por chaves (comarca + nº do edital; comarca + prazo; PDF; URL). A fonte primária (TJGO) vem antes."""
    oport, acomp = {}, {}
    cont = {"OPORTUNIDADE": 0, "ACOMPANHAR": 0, "RUIDO": 0, "quarentena": 0, "erros": 0, "duplicados": 0}
    por_chave: dict[str, str] = {}
    ordem = {"A": 0, "B": 0, "C": 1}
    for m in sorted(itens, key=lambda x: ordem.get(x.get("fonte"), 2)):
        bruto = " ".join(str(m.get(k) or "") for k in ("titulo", "descricao", "texto"))
        if has_prompt_injection(bruto):
            append_jsonl(QUARENTENA, {"origem": MOTOR_ID, "url": m.get("url"), "em": now_iso(), "hash": sha256(bruto.encode())[:16]})
            cont["quarentena"] += 1
            continue
        try:
            c = classificar_item(m, hoje, cfg)
            if c["veredito"] == "RUIDO":
                cont["RUIDO"] += 1
                continue
            ks = chaves(m, c)
            dono = next((por_chave[k] for k in ks if k in por_chave), None)
            if dono:
                cont["duplicados"] += 1
                alvo = oport.get(dono) or acomp.get(dono)
                if alvo:
                    alvo.setdefault("vista_tambem_em", [])
                    if m.get("url") and m["url"] not in alvo["vista_tambem_em"]:
                        alvo["vista_tambem_em"].append(m["url"])
                    for campo in ("fim", "numero_edital", "comarca", "vara", "url_documento", "valor_texto"):
                        if not alvo.get(campo) and c.get(campo):
                            alvo[campo] = c[campo]
                for k in ks:
                    por_chave.setdefault(k, dono)
                continue
            r = _registro(c, m, ks)
            cont[c["veredito"]] += 1
        except Exception:  # noqa: BLE001 — um item malformado não derruba o lote
            cont["erros"] += 1
            continue
        for k in ks:
            por_chave[k] = r["id"]
        (oport if c["veredito"] == "OPORTUNIDADE" else acomp)[r["id"]] = r
    return oport, acomp, cont


# ─────────────────────────── fontes ───────────────────────────
def fonte_a(hoje: date, cfg: dict, diag: dict, est: dict) -> list[dict]:
    """RSS paginado da Agência de Notícias do TJGO: lê até a primeira página toda já vista; a carga inicial de N dias vai
    em parcelas (cursor), para não pesar numa execução só."""
    if not _tem("A"):
        return []
    f = (cfg.get("fontes") or {}).get("A_noticias_tjgo") or {}
    F = diag["fontes"]["A"]
    if not f.get("ativa", True):
        return []
    rss = est.setdefault("rss", {})
    vistos = set(rss.get("vistos") or [])
    passo = int(f.get("itens_por_pagina_rss", 8))
    carga_dias = int(f.get("carga_inicial_dias", 150))
    corte = (hoje - timedelta(days=carga_dias)).isoformat()
    novas: list[dict] = []
    paginas = int(f.get("paginas_por_execucao", 6))
    for pag in range(paginas):
        try:
            xml = _get(f"{f['rss']}&limitstart={pag * passo}" if pag else f["rss"], cfg, F)
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"RSS página {pag + 1}: {_erro(exc)}")
            break
        itens = itens_do_rss(xml)
        if not itens:
            F["formato_desconhecido"] = pag == 0
            break
        F["itens"] += len(itens)
        frescos = [i for i in itens if i["url"] not in vistos]
        novas += frescos
        if not frescos:                       # página inteira já vista: o resto também foi
            break
    # carga inicial / retomada: continua de onde parou, até o corte de dias
    if not rss.get("carga_concluida"):
        cur = int(rss.get("cursor") or paginas)
        for _ in range(int(f.get("paginas_carga_inicial_por_execucao", 25))):
            if _tempo_esgotado():
                break
            try:
                itens = itens_do_rss(_get(f"{f['rss']}&limitstart={cur * passo}", cfg, F))
            except Exception as exc:  # noqa: BLE001
                F["falhas"].append(f"carga inicial, página {cur + 1}: {_erro(exc)}")
                break
            if not itens:
                rss["carga_concluida"] = True
                break
            F["itens"] += len(itens)
            novas += [i for i in itens if i["url"] not in vistos]
            cur += 1
            if all((i.get("publicado") or "9999") < corte for i in itens):
                rss["carga_concluida"] = True
                break
        rss["cursor"] = cur
    unicas = list({i["url"]: i for i in novas}.values())
    cands = [i for i in unicas if candidata(i["titulo"], i.get("descricao") or "")]
    F["candidatas"] = len(cands)
    for i in unicas:
        if i not in cands:
            vistos.add(i["url"])             # o que não é candidato não precisa ser relido
    out = []
    pend = list(rss.get("pendentes") or []) + [i for i in cands if i["url"] not in {p["url"] for p in rss.get("pendentes") or []}]
    lidas = 0
    restantes = []
    for i in pend:
        if lidas >= int(f.get("max_artigos_por_execucao", 20)) or _tempo_esgotado():
            restantes.append(i)
            continue
        try:
            pagina = _get(i["url"], cfg, F)
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"notícia {i['url'][-60:]}: {_erro(exc)}")
            restantes.append(i)
            continue
        lidas += 1
        a = artigo(pagina, i["url"], i["titulo"], ((cfg.get("fontes") or {}).get("B_pdf_edital") or {}).get("hosts") or ())
        out.append({**i, "fonte": "A", "texto": a["texto"] or i.get("descricao"), "publicado": a["publicado"] or i.get("publicado"),
                    "pdfs": a["pdfs"], "banco_projetos": a["banco_projetos"]})
        vistos.add(i["url"])
    rss["pendentes"] = restantes[:200]
    corte_vistos = sorted(vistos)[-6000:]
    rss["vistos"] = corte_vistos
    F["lidas"] = lidas
    return out


def fonte_b(itens: list[dict], hoje: date, cfg: dict, diag: dict, est: dict) -> None:
    """PDF do edital: o texto completo (pypdf) completa prazo, número e requisitos que a notícia não trouxe."""
    if not _tem("B"):
        return None
    f = (cfg.get("fontes") or {}).get("B_pdf_edital") or {}
    F = diag["fontes"]["B"]
    if not f.get("ativa", True):
        return
    try:
        from .diario_goiania import texto_do_pdf
    except Exception:  # noqa: BLE001
        texto_do_pdf = None
    lidos = est.setdefault("pdfs_lidos", {})
    feitos = 0
    for m in itens:
        if not m.get("pdfs") or not candidata(m.get("titulo") or "", m.get("texto") or ""):
            continue
        u = m["pdfs"][0]["url"]
        if u in lidos:
            if lidos[u]:
                m["texto"] = f"{m.get('texto') or ''}\n{lidos[u]}"
            continue
        if feitos >= int(f.get("max_pdfs_por_execucao", 6)) or _tempo_esgotado():
            break
        try:
            dados = _get(u, cfg, F, binario=True, max_bytes=int(f.get("max_bytes", 15_000_000)))
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"PDF {u[-50:]}: {_erro(exc)}")
            continue
        feitos += 1
        txt = texto_do_pdf(dados) if texto_do_pdf else None
        if not txt:
            F["sem_texto"] = F.get("sem_texto", 0) + 1
            lidos[u] = ""
            continue
        trecho = atos.mascarar_pii(re.sub(r"\s+", " ", txt))[:6000]
        lidos[u] = trecho
        m["texto"] = f"{m.get('texto') or ''}\n{trecho}"
        F["itens"] += 1
    est["pdfs_lidos"] = dict(list(lidos.items())[-300:])


def resultados_cnj(pagina_html: str, base: str = "https://www.cnj.jus.br/") -> list[dict]:
    """Página de busca do WordPress do CNJ: cada resultado é um <h2|h3><a href=…>título</a>."""
    out = []
    for m in re.finditer(r"<h[23][^>]*>\s*<a\b[^>]*href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", pagina_html or "", re.S | re.I):
        u = urljoin(base, _html.unescape(m.group(1)))
        if (urlsplit(u).hostname or "").endswith("cnj.jus.br"):
            out.append({"titulo": _limpo(m.group(2)), "url": u, "descricao": "", "publicado": None})
    return list({x["url"]: x for x in out}.values())


def fonte_c(hoje: date, cfg: dict, diag: dict, est: dict, rota: str) -> list[dict]:
    if not _tem("C"):
        return []
    f = (cfg.get("fontes") or {}).get("C_cnj_busca") or {}
    F = diag["fontes"]["C"]
    if not f.get("ativa", True):
        return []
    cnj = est.setdefault("cnj", {})
    if rota == "local":
        bloq = (load_json(ESTADO).get("cnj") or {}).get("recusado_na_nuvem_em") if ESTADO.exists() else None
        if not bloq or bloq < (hoje - timedelta(days=3)).isoformat():
            F["pulado"] = "a nuvem leu o CNJ — o computador não repete"
            return []
    ultima = cnj.get("ultima")
    if ultima and ultima > (hoje - timedelta(days=int(f.get("cadencia_dias", 1)))).isoformat():
        F["pulado"] = f"cadência: já lido em {ultima}"
        return []
    vistos = set(cnj.get("vistos") or [])
    achados: list[dict] = []
    max_pg = int(f.get("max_paginas", 3))
    nao_alcancou = []
    for termo in f.get("termos") or []:
        # 03/10 (teste do motor 11): a busca do WordPress ordena por RELEVÂNCIA — a 1ª página trazia notícias de 2020 e
        # escondia as novas. Por DATA, da mais nova para a mais antiga, até alcançar o que já foi visto.
        for pg in range(1, max_pg + 1):
            url = (f.get("busca_pagina") if pg > 1 else f["busca"]) or f["busca"]
            try:
                res = resultados_cnj(_get(url.format(termo=quote_plus(termo), pagina=pg), cfg, F))
            except Exception as exc:  # noqa: BLE001
                F["falhas"].append(f"busca '{termo}' p{pg}: {_erro(exc)}")
                if F.get("recusado") and rota == "nuvem":
                    cnj["recusado_na_nuvem_em"] = hoje.isoformat()
                break
            achados += res
            if not res or any(x["url"] in vistos for x in res) or not vistos:
                break                                  # alcançou o já visto (ou 1ª leitura: só a 1ª página)
            if pg == max_pg:
                nao_alcancou.append(termo)
        if F.get("recusado") and rota == "nuvem":
            break
    unicos = [x for x in {x["url"]: x for x in achados}.values() if x["url"] not in vistos and candidata(x["titulo"])]
    F["itens"] = len(achados)
    F["candidatas"] = len(unicos)
    lim = int(f.get("max_artigos_por_execucao", 8))
    cortados = max(0, len(unicos) - lim) + len(nao_alcancou)
    if cortados:
        # leitura parcial: o maestro dispara de novo e a próxima passagem continua de onde parou
        diag["cortados"] = cortados
        F["parcial"] = (f"{max(0, len(unicos) - lim)} notícia(s) candidata(s) ficaram para a próxima passagem"
                        + (f"; a busca por {', '.join(nao_alcancou)} não alcançou o já visto em {max_pg} páginas" if nao_alcancou else ""))
    out = []
    for x in unicos[:lim]:
        try:
            a = artigo(_get(x["url"], cfg, F), x["url"], x["titulo"], ("www.cnj.jus.br", "cnj.jus.br", "www.tjgo.jus.br"))
        except Exception as exc:  # noqa: BLE001
            F["falhas"].append(f"notícia CNJ: {_erro(exc)}")
            continue
        vistos.add(x["url"])
        out.append({**x, "fonte": "C", "texto": a["texto"], "publicado": a["publicado"], "pdfs": a["pdfs"]})
    if not F["falhas"] and not cortados:          # leitura cortada não conta como "lida no dia" (a cadência não a pula)
        cnj["ultima"] = hoje.isoformat()
        if rota == "nuvem":
            cnj.pop("recusado_na_nuvem_em", None)
    cnj["vistos"] = sorted(vistos)[-2000:]
    return out


def fonte_d(cfg: dict, diag: dict) -> list[dict]:
    """O que o motor 04 (PNCP) já gravou na base com órgão TJGO ou CNJ — cruzado, não relido."""
    if not _tem("D"):
        return []
    f = (cfg.get("fontes") or {}).get("D_pncp_cruzado") or {}
    F = diag["fontes"]["D"]
    if not f.get("ativa", True) or not DB.exists():
        return []
    cnpjs = set((f.get("cnpjs") or {}).keys())
    rx = re.compile(f.get("orgao_regex") or r"$^")
    out = []
    with DB.open(encoding="utf-8") as fh:
        for linha in fh:
            if '"pncp-api"' not in linha or not (any(c in linha for c in cnpjs) or rx.search(_N(linha[:4000]))):
                continue
            try:
                r = json.loads(linha)
            except ValueError:
                continue
            if r.get("fonte_id") != "pncp-api":
                continue
            org = _N(r.get("orgao") or r.get("fonte_nome") or "")
            if not (rx.search(org) or any(c in (r.get("url") or "") for c in cnpjs)):
                continue
            out.append({k: r.get(k) for k in ("id", "titulo", "url", "fim", "modalidade_pncp", "data_publicacao")})
    F["itens"] = len(out)
    return out


def habilitacao_previa(cfg: dict) -> dict:
    if not _tem("E"):
        return None
    f = (cfg.get("fontes") or {}).get("E_banco_projetos") or {}
    return {"id": sha256(b"jud|banco-projetos-cgjgo")[:20], "categoria": "habilitacao_previa",
            "titulo": "Banco de Projetos Sociais da Corregedoria (CGJ/GO) — cadastro prévio exigido pelos editais de prestação pecuniária",
            "url": f.get("url") or "https://corregedoria.tjgo.jus.br/basesocial", "fim": None, "data_publicacao": None,
            "motivo": "os editais das comarcas só aceitam entidades já cadastradas (ex.: Rio Verde, Edital 01/2026) — manter o "
                      "cadastro da associação e o projeto atualizados antes de cada edital"}


# ─────────────────────────── o motor ───────────────────────────
_CAMPOS = ("id", "titulo", "url", "url_noticia", "data_publicacao", "fim", "categoria", "comarca", "vara", "numero_edital",
           "areas_admitidas", "restricao_territorial", "exige_banco_projetos", "prazo_a_confirmar", "fonte_nome", "chaves")


def _vivas(registros: list[dict], hoje: date, cfg: dict) -> list[dict]:
    """Oportunidade continua enquanto o prazo não venceu; sem prazo, só dentro da janela de dias da publicação."""
    janela = (hoje - timedelta(days=int(cfg.get("janela_oportunidade_sem_prazo_dias", 20)))).isoformat()
    d0 = hoje.isoformat()
    return [r for r in registros if (r.get("fim") and str(r["fim"]) >= d0) or (not r.get("fim") and str(r.get("data_publicacao") or "") >= janela)]


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor do Judiciário com a mesma saída de `sensores.ler`."""
    pedido = hoje or (sensor or {}).get("_data")
    hoje = _hoje_real() if pedido is None else pedido
    vazio = {"paginas_lidas": 0, "links_total": 0, "links_candidatos": 0, "descobertas": [], "pdf_links": 0}
    if pedido is not None and pedido < _hoje_real():
        return {"sensor": MOTOR_ID, "achados": [], "falhas": [], "saude": [], "lido_em": now_iso(),
                "diagnostico": {**vazio, "motivo_zero": "o motor do Judiciário lê a situação de hoje; dia passado não é relido", "retroativo": True}}
    cfg = _cfg()
    rota = modo()
    _pt = cfg.get("prazo_total_segundos") or {}
    _PRAZO["ate"] = time.monotonic() + float(_pt.get(rota) or (_pt.get("local", 600) if rota == "ponte" else 300))
    diag = {**vazio, "motivo_zero": None, "versao": "motor Judiciário CNJ+TJGO v1 (02/10/2026)", "rota": rota,
            "fontes": {k: {"falhas": [], "consultas": 0, "itens": 0} for k in "ABCDE"}}
    arq = ESTADO_LOCAL if rota == "local" else ESTADO
    est = load_json(arq) if arq.exists() else {}
    itens: list[dict] = []
    if rota in ("local", "ponte"):
        try:
            itens += fonte_a(hoje, cfg, diag, est)
        except Exception as exc:  # noqa: BLE001 — uma fonte nunca derruba a outra
            diag["fontes"]["A"]["falhas"].append(f"etapa: {_erro(exc)}")
        try:
            fonte_b(itens, hoje, cfg, diag, est)
        except Exception as exc:  # noqa: BLE001
            diag["fontes"]["B"]["falhas"].append(f"etapa: {_erro(exc)}")
    elif _tem("A"):
        diag["fontes"]["A"]["pulado"] = diag["fontes"]["B"]["pulado"] = \
            "na nuvem o TJGO recusa IP estrangeiro: notícias e PDFs são lidos no computador do titular (scripts/coleta_brasil.py)"
    if _tem("C") and not (est.get("cnj") or {}).get("datas_v2"):
        # 03/10 (teste do motor 11): as notícias do CNJ lidas com a data da barra lateral são relidas UMA vez com a data
        # certa (meta do artigo) — a de Itaberaí (2020) estava aberta até 2027
        refazer = {r.get("url_noticia") for r in est.get("abertas_registros") or [] if r.get("forma_divulgacao") == "noticia_cnj"}
        est["abertas_registros"] = [r for r in est.get("abertas_registros") or [] if r.get("forma_divulgacao") != "noticia_cnj"]
        cnj0 = est.setdefault("cnj", {})
        cnj0["vistos"] = [u for u in cnj0.get("vistos") or [] if u not in refazer]
        cnj0.pop("ultima", None); cnj0["datas_v2"] = hoje.isoformat()
        diag["revalidadas_cnj"] = len(refazer)
    try:
        itens += fonte_c(hoje, cfg, diag, est, rota)
    except Exception as exc:  # noqa: BLE001
        diag["fontes"]["C"]["falhas"].append(f"etapa: {_erro(exc)}")
    _PRAZO["ate"] = None
    oport, acomp, cont = classificar_lote(itens, hoje, cfg)
    d0 = hoje.isoformat()
    novas = list(oport.values())
    novos_acomp = [{k: a.get(k) for k in _CAMPOS} | {"motivo": a["classificacao_ato"]["motivos"][0]} for a in acomp.values()]
    # o que já estava guardado continua (as fontes leem janelas): abertas vivas e acompanhar dos últimos 365 dias
    guard_ab = {r["id"]: r for r in est.get("abertas_registros") or []}
    guard_ab.update({r["id"]: r for r in novas})
    abertas = _vivas(list(guard_ab.values()), hoje, cfg)
    ac = {a["id"]: a for a in est.get("acompanhar") or []}
    ac.update({a["id"]: a for a in novos_acomp})
    limite_ac = (hoje - timedelta(days=365)).isoformat()
    acompanhar = [a for a in ac.values() if str(a.get("data_publicacao") or d0) >= limite_ac]
    # registros do computador do titular entram na leitura da nuvem (sem o computador gravar na base)
    local = {}
    if rota in ("nuvem", "ponte") and _tem("A") and ESTADO_LOCAL.exists():
        local = load_json(ESTADO_LOCAL)
        ids = {r["id"] for r in abertas}
        ks = {k for r in abertas for k in (r.get("chaves") or [])}
        for r in _vivas(local.get("abertas_registros") or [], hoje, cfg):
            if r["id"] not in ids and not (set(r.get("chaves") or []) & ks):
                abertas.append(r)
        ida = {a["id"] for a in acompanhar}
        acompanhar += [a for a in local.get("acompanhar") or [] if a["id"] not in ida and str(a.get("data_publicacao") or d0) >= limite_ac]
        ult = (local.get("ultima") or {}).get("data")
        diag["coleta_local"] = {"ultima": ult, "abertas": len(local.get("abertas_registros") or [])}
        if not ult or ult < (hoje - timedelta(days=3)).isoformat():
            diag["alerta_local"] = (f"o computador do titular não roda a coleta desde {ult or 'nunca'} — as notícias e os editais das "
                                    "comarcas do TJGO só são lidos por ele (scripts/coleta_brasil.py)")
    elif rota == "nuvem" and _tem("A"):
        diag["alerta_local"] = "a coleta no computador do titular ainda não rodou — as notícias e os editais das comarcas do TJGO só são lidos por ele"
    pncp = fonte_d(cfg, diag)
    habil = habilitacao_previa(cfg)
    if habil and habil["id"] not in {a["id"] for a in acompanhar}:
        acompanhar.insert(0, habil)
    comarca_assoc = _N(cfg.get("comarca_da_associacao") or "Goiânia")
    abertas.sort(key=lambda r: (_N(r.get("comarca")) != comarca_assoc, str(r.get("fim") or "9999")))
    ordem_cat = {"habilitacao_previa": 0, "edital_sem_prazo": 1, "credenciamento_encerrado": 2, "edital_encerrado": 2,
                 "resultado_ou_entrega": 3, "regra": 4, "noticia_destinacao": 5}
    acompanhar.sort(key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)
    acompanhar.sort(key=lambda a: ordem_cat.get(a.get("categoria"), 6))
    F = diag["fontes"]
    hist = est.setdefault("historico", {})
    leu = any(F[k]["consultas"] for k in "ABC")
    hist[d0] = {**{f"consultas_{k}": F[k]["consultas"] for k in "ABC"}, **{f"itens_{k}": F[k]["itens"] for k in "ABCD"}, **cont, "falhou": not leu and rota == "local"}
    est.update({"abertas_registros": abertas[:300], "acompanhar": acompanhar[:300], "pncp_cruzado": pncp[:60],
                "ultima": {"em": now_iso(), "data": d0, "rota": rota, "vereditos": cont, "falhas": sum((F[k]["falhas"] for k in F), [])[:10],
                           **({"cortados": diag["cortados"]} if diag.get("cortados") else {})},
                "historico": {k: v for k, v in hist.items() if k >= (hoje - timedelta(days=120)).isoformat()}})
    est["abertas"] = [{k: r.get(k) for k in _CAMPOS} for r in abertas]
    write_json(arq, est)
    diag.update({"vereditos": cont, "paginas_lidas": sum(F[k]["consultas"] for k in F), "links_total": len(itens),
                 "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"], "pncp_do_judiciario": len(pncp),
                 "abertas": len(abertas)})
    hosts = {"A": "https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs", "B": "https://www.tjgo.jus.br/files/",
             "C": "https://www.cnj.jus.br/", "D": "https://pncp.gov.br", "E": "https://corregedoria.tjgo.jus.br/basesocial"}
    falhas = [{"url": hosts[k], "erro": "judiciario", "code": None, "waf": None, "causa": f"{k}: {x}"} for k in F for x in F[k]["falhas"]][:6]
    saude = [{"url": hosts[k], "http": 200, "bytes": F[k].get("bytes", 0), "itens": F[k]["itens"]} for k in F if F[k]["consultas"]]
    if not abertas:
        diag["motivo_zero"] = (f"{len(itens)} notícias lidas (TJGO A {F['A']['itens']} no RSS · CNJ C {F['C']['itens']}) e "
                               f"{len(pncp)} do TJGO/CNJ no PNCP (lidas pelo motor 04, já na base): nenhum edital de destinação aberto hoje · {cont['ACOMPANHAR']} a acompanhar"
                               + (f" · {diag['alerta_local']}" if diag.get("alerta_local") else ""))
    return {"sensor": MOTOR_ID, "achados": abertas, "falhas": falhas, "saude": saude, "diagnostico": diag, "lido_em": now_iso()}


def atos_para_painel(limite: int = 12) -> list[dict]:
    est = load_json(ESTADO) if ESTADO.exists() else {}
    return (est.get("acompanhar") or [])[:limite]


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2))
