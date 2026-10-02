"""CONDICIONAIS DE INTEGRIDADE (titular, 02/10/2026) — antes de a rede neural opinar, o maestro confere se a LEITURA é
confiável. Origem: testes com 14 erros artificiais — 13 passavam sem aviso e a rede dava nota média a todos (0,28–0,61),
inclusive a um diário lido em 12%, a uma data em 2099 e a um registro vazio.

Cada verificação devolve {codigo, gravidade, motivo, acao}:
  BLOQUEIA  a informação não pode ser usada como está → reprocessar (nunca o lixo) e a rede responde "inconclusiva"
  ALERTA    segue, com ressalva registrada → a rede responde "com ressalva" e a nota é puxada para o meio
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RASTREIO = re.compile(r"^(utm_[a-z]+|fbclid|gclid|mc_cid|mc_eid|_ga|ref|origem)$", re.I)
PAGINA_DE_ERRO = re.compile(r"p[aá]gina n[aã]o encontrada|page not found|erro 404|\b404\b.{0,20}(not found|n[aã]o)|acesso negado|access denied|"
                            r"forbidden|em manuten[cç][aã]o|captcha|javascript (is )?required|habilite o javascript|sess[aã]o expirada|"
                            r"service unavailable|bad gateway|internal server error", re.I)
MOJIBAKE = re.compile(r"Ã[§£©º¡³ª­µ¢ƒ‰]|â€[™œ\x9d“”]|Ã¢|Ã‡")
CONTINUA = re.compile(r"continua na pr[oó]xima|p[aá]gina \d+ de \d+|carregar mais|ver mais resultados", re.I)
GENERICO = re.compile(r"^\s*di[aá]rio oficial\b.{0,60}(edi[cç][aã]o|n[º°o.]*\s*\d+)", re.I)
OPORT = re.compile(r"chamamento|edital|sele[cç][aã]o|inscri[cç]|credenciamento|pr[eê]mio|termo de (fomento|colabora)", re.I)
SEM_TEXTO = re.compile(r"imagem digitalizada|pdf (escaneado|imagem)|documento digitalizado", re.I)
GOIAS = re.compile(r"\b(goi[aâ]nia|goi[aá]s|aparecida de goi[aâ]nia|an[aá]polis)\b", re.I)


def url_canonica(u: str | None) -> str:
    """Sem parâmetros de rastreio, sem fragmento, sem barra final — a mesma página tem um endereço só."""
    try:
        p = urlsplit(str(u or "").strip())
    except ValueError:
        return str(u or "")
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not RASTREIO.match(k)]
    return urlunsplit((p.scheme.lower(), p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), urlencode(q), ""))


def _d(s) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None


def verificar(reg: dict, hoje: date | None = None) -> list[dict]:
    hoje = hoje or date.today()
    tit = str(reg.get("titulo") or ""); ev = str(reg.get("evidencia") or reg.get("objeto") or "")
    texto = f"{tit} {ev}"
    out = []

    def f(codigo, gravidade, motivo, acao):
        out.append({"codigo": codigo, "gravidade": gravidade, "motivo": motivo, "acao": acao})

    if not tit.strip():
        f("REGISTRO_VAZIO", "bloqueia", "sem título", "reler a página na fonte")
    try:
        bl, bt = float(reg.get("bytes_lidos") or 0), float(reg.get("bytes_total") or 0)
        if bt and bl / bt < 0.95:
            f("LEITURA_INCOMPLETA", "bloqueia", f"lido {100 * bl / bt:.0f}% do documento ({int(bl)} de {int(bt)} bytes)", "reler o documento inteiro")
    except (TypeError, ValueError):
        pass
    try:
        pl, pt = int(reg.get("paginas_lidas") or 0), int(reg.get("paginas_total") or 0)
        if pt and pl < pt:
            f("PAGINACAO_CORTADA", "bloqueia", f"lidas {pl} de {pt} páginas", "continuar a leitura das páginas restantes")
    except (TypeError, ValueError):
        pass
    if CONTINUA.search(texto) and not any(x["codigo"] == "PAGINACAO_CORTADA" for x in out):
        f("PAGINACAO_CORTADA", "alerta", "o texto indica que a lista continua em outra página", "conferir se a leitura chegou ao fim")
    pub = _d(reg.get("data_publicacao"))
    if reg.get("data_publicacao") in (None, ""):
        f("SEM_DATA_DE_PUBLICACAO", "alerta", "só há a data da consulta; a data original da publicação não foi registrada", "extrair a data da publicação na fonte")
    elif not pub or pub.year < 2000 or pub > hoje + timedelta(days=1):
        f("DATA_IMPOSSIVEL", "bloqueia", f"data de publicação impossível: {reg.get('data_publicacao')}", "reler a data na fonte")
    elif (hoje - pub).days > 400 and not (_d(reg.get("fim")) and _d(reg.get("fim")) >= hoje):
        f("PUBLICACAO_ANTIGA", "alerta", f"publicado em {pub.isoformat()}, há mais de 400 dias, sem prazo vigente", "tratar como histórico, não como novidade")
    fim = _d(reg.get("fim"))
    if reg.get("fim") and fim:
        if fim.year > hoje.year + 6 or fim.year < 2000:
            f("PRAZO_IMPOSSIVEL", "bloqueia", f"prazo impossível: {reg.get('fim')}", "reler o prazo na fonte")
        elif pub and fim < pub:
            f("PRAZO_ANTES_DA_PUBLICACAO", "bloqueia", f"prazo {fim} anterior à publicação {pub}", "reler as duas datas na fonte")
    if PAGINA_DE_ERRO.search(texto):
        f("PAGINA_DE_ERRO", "bloqueia", "o conteúdo é uma página de erro ou bloqueio, não o edital", "reler a página (ou mudar de rota)")
    if MOJIBAKE.search(texto):
        f("ACENTOS_QUEBRADOS", "alerta", "texto com codificação quebrada (ex.: 'Ã§')", "reler com a codificação correta")
    try:
        from .nucleo import has_prompt_injection
        if has_prompt_injection(texto):
            f("INJECAO", "bloqueia", "o texto coletado traz instrução ao modelo", "quarentena: não vira livro nem prompt")
    except Exception:  # noqa: BLE001
        pass
    if not ev.strip() and SEM_TEXTO.search(tit):
        f("SEM_TEXTO", "alerta", "documento digitalizado sem texto legível", "ler com OCR ou buscar a versão em texto")
    if GENERICO.search(tit) and not OPORT.search(ev):
        f("TITULO_GENERICO", "alerta", "título genérico da edição do diário, sem ato identificado", "localizar o ato dentro da edição")
    uf = str(reg.get("uf") or "").upper()
    if uf and uf not in ("GO", "BR", "") and GOIAS.search(texto):
        f("UF_DIVERGENTE", "alerta", f"o texto fala de Goiás, mas o registro está como {uf}", "corrigir a UF pelo órgão")
    if url_canonica(reg.get("url")) != str(reg.get("url") or "").strip().rstrip("/") and RASTREIO.pattern and "utm_" in str(reg.get("url") or ""):
        f("URL_COM_RASTREIO", "alerta", "endereço com parâmetros de rastreio (vira duplicata)", "usar o endereço canônico")
    return out


def situacao(flags: list[dict]) -> str:
    if any(x["gravidade"] == "bloqueia" for x in flags):
        return "inconclusiva"
    return "com_ressalva" if flags else "confiavel"


MESES = {m: n for n, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
                                     "novembro", "dezembro"], 1)}
_PUB_TXT = re.compile(r"(?:publicad[oa]|edi[cç][aã]o|di[aá]rio oficial|D\.?O\.?[EMU]?\.?)[^0-9]{0,40}(\d{1,2})[/.](\d{1,2})[/.](20\d\d)", re.I)
_PUB_EXT = re.compile(r"(?:publicad[oa]|edi[cç][aã]o)[^0-9]{0,40}(\d{1,2}) de (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro) de (20\d\d)", re.I)
_PUB_URL = re.compile(r"/(20\d\d)[/-](\d{2})[/-](\d{2})(?:/|$|\D)|[^0-9](20\d\d)(\d{2})(\d{2})[^0-9]")


def completar_datas(reg: dict, hoje: date | None = None) -> dict:
    """02/10 (titular): todo registro novo leva a data ORIGINAL da publicação e a data da CONSULTA.
    Se a fonte não informou a publicação, tenta o texto (\"publicado em\", \"edição de\") e o endereço (/2026/10/01/);
    a origem fica registrada. Nada inventado: sem pista, fica null e o sinal SEM_DATA_DE_PUBLICACAO aparece."""
    hoje = hoje or date.today()
    reg.setdefault("data_consulta", str(reg.get("coletado_em") or hoje.isoformat())[:10])
    if reg.get("data_publicacao"):
        reg.setdefault("data_publicacao_origem", "fonte")
        return reg
    txt = f"{reg.get('titulo') or ''} {reg.get('evidencia') or ''}"
    cand = None
    m = _PUB_TXT.search(txt)
    if m:
        cand = (int(m.group(3)), int(m.group(2)), int(m.group(1))); orig = "texto"
    elif (m := _PUB_EXT.search(txt)):
        cand = (int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))); orig = "texto"
    elif (m := _PUB_URL.search(str(reg.get("url") or ""))):
        g = [x for x in m.groups() if x]; cand = (int(g[0]), int(g[1]), int(g[2])); orig = "endereço"
    if cand:
        try:
            d = date(*cand)
            if date(2000, 1, 1) <= d <= hoje:
                reg["data_publicacao"] = d.isoformat(); reg["data_publicacao_origem"] = f"extraída do {orig}"
        except ValueError:
            pass
    return reg
