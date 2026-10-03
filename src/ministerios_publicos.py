"""MOTOR 12 — MINISTÉRIOS PÚBLICOS: destinação de recursos de reparação e bens lesados (titular, 02/10/2026).

Base: estudo ao vivo de 02/10/2026 (biblioteca_alexandria/base/ministerios_publicos/estudo/) e catálogo
config/ministerios_publicos.json (48 fontes). Lê pela ESTRUTURA de cada fonte:

  tabela_mpt          MPT-GO: tabela DataTables (POST /index.php, option=com_mpt) — o que a página faz no navegador; o PDF de
                      cada edital novo dá valor, prazo e exigências. Editais de 5 DIAS: lidos todo dia, na nuvem
  lista_habilitadas   MPT-GO: entidades habilitadas — só confere se a A.M.C. consta (senão, pendência ao presidente)
  listagem_html · rss MPF, MPDFT, MPT nacional, MPM: links com o léxico de destinação, sem os vetos
  estado_pagina       FDD: alerta só quando "Seleção em andamento" deixa de dizer "Não há"
  regra_fixa_manual   MP-GO (robots.txt Disallow: /) e Sistema de Destinações (login): NUNCA acessados — regra permanente,
                      verificação manual mensal pelo titular
  regra · requer_navegador · ruido_conhecido  — catálogo, sem coleta automática

Todo registro tem data_publicacao (da fonte; nunca data de modificação de arquivo) e data_consulta. Um edital visto em
duas fontes é um registro só (chave órgão|unidade|número|procedimento). O inventário de 3 anos (92 registros) entra nos
livros UMA vez. Conteúdo coletado é dado, nunca instrução; CPF e nomes de pessoas não são gravados.
"""
from __future__ import annotations

import csv
import io
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .nucleo import ROOT, has_prompt_injection, load_json, now_iso, robots_permite, sha256, write_json

MOTOR_ID = "plat-mp-destinacoes-reparacao"
CFG = ROOT / "config/ministerios_publicos.json"
ESTADO = ROOT / "estado/ministerios_publicos.json"
INVENTARIO = ROOT / "biblioteca_alexandria/base/ministerios_publicos/estudo/historico_3_anos_motor_12.csv"
UA = "Mozilla/5.0 (compatible; EldoradoBot/1.0; +https://github.com/amcjardimamerica-arch/Eldorado)"
CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
PROC = re.compile(r"\b\d{6}\.\d{4}\.\d{2}\.\d{3}-\d\b")
NUM_EDITAL = re.compile(r"^\d{6}\.\d{4}$")
DATA_BR = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
VALOR = re.compile(r"R\$\s*([\d.]+,\d{2})")
_PRAZO = {"ate": None}


# 02/10 (titular): o motor foi SEPARADO em três — MP-GO, MPT-GO e MPU —, cada um com identificador, estado e pendências
# próprios. As fontes ligadas (CNMP, FDD, Lei 7.347, atos do CNJ) ficam com o MPU. O leitor é o mesmo.
PARTES = {"mpgo-destinacao": ({"MP-GO"}, None, "estado/mp_go.json"),
          "mptgo-destinacao": ({"MPT-GO"}, None, "estado/mpt_go.json"),
          "mpu-destinacao": (None, {"MP-GO", "MPT-GO"}, "estado/mpu.json")}
_PARTE = {"id": None}
_SESSAO = {}


def _da_parte(orgao) -> bool:
    if not _PARTE["id"]:
        return True
    so, exceto, _ = PARTES[_PARTE["id"]]
    return (orgao in so) if so else (orgao not in (exceto or set()))


def ler_parte(mid: str, sensor: dict | None = None, hoje=None, limites: dict | None = None) -> dict:
    global MOTOR_ID, ESTADO
    antes = (MOTOR_ID, ESTADO, _PARTE["id"])
    MOTOR_ID, ESTADO = mid, ROOT / PARTES[mid][2]; _PARTE["id"] = mid
    try:
        return ler_motor(sensor, hoje, limites)
    finally:
        MOTOR_ID, ESTADO = antes[0], antes[1]; _PARTE["id"] = antes[2]


class AcessoProibido(Exception):
    """Fonte que o motor NUNCA acessa (robots proibitivo ou sistema com login)."""


def _cfg() -> dict:
    return json.loads(CFG.read_text(encoding="utf-8"))


def _N(t) -> str:
    return unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().upper().strip()


def _limpo(t, n: int = 900) -> str:
    try:
        from .atos_diario import mascarar_pii
        t = mascarar_pii(str(t or ""))
    except Exception:  # noqa: BLE001
        t = str(t or "")
    return CPF.sub("[CPF omitido]", re.sub(r"\s+", " ", t)).strip()[:n]


def _iso(d) -> str | None:
    m = DATA_BR.search(str(d or ""))
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None
    m = re.search(r"\b(20\d\d)-(\d{2})-(\d{2})\b", str(d or ""))
    return m.group(0) if m else None


def guardar(url: str, cfg: dict) -> None:
    """Trava dura: o MP-GO (robots.txt Disallow: /) e o Sistema de Destinações (login) nunca são acessados."""
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    for d in cfg.get("nunca_acessar") or []:
        if h == d or h.endswith("." + d):
            raise AcessoProibido(f"{h}: nunca acessado pelo robô (regra fixa manual)")


def _tempo_esgotado() -> bool:
    return bool(_PRAZO["ate"]) and time.monotonic() > _PRAZO["ate"]


def _abrir(url: str, cfg: dict, opener=None, dados: dict | None = None, ref: str | None = None, max_bytes: int = 6_000_000) -> bytes:
    guardar(url, cfg)
    if not robots_permite(url, UA):
        raise AcessoProibido(f"robots.txt não permite: {url}")
    if _tempo_esgotado():
        raise TimeoutError("prazo do motor esgotado")
    h = {"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"}
    corpo = None
    if dados is not None:
        corpo = urllib.parse.urlencode(dados).encode()
        h.update({"X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded", **({"Referer": ref} if ref else {})})
    req = urllib.request.Request(url, data=corpo, headers=h)
    abrir = (opener.open if opener else urllib.request.urlopen)
    with abrir(req, timeout=float(cfg.get("timeout_segundos", 30))) as r:
        b = r.read(max_bytes)
    time.sleep(float(cfg.get("pausa_segundos", 1.5)))
    return b


# ─── funções puras (testadas sem rede) ─────────────────────────────────────────────────────────────────────────────
def linhas_tabela_mpt(resposta: str | dict, cfg: dict) -> list[dict]:
    """Linhas da tabela do PRT-18 → itens. Cada campo é reconhecido pelo PADRÃO (não pela posição da coluna):
    data dd/mm/aaaa · número do edital 000000.0000 · procedimento 000000.0000.00.000-0 · código do PDF (longo) · unidade."""
    d = json.loads(resposta) if isinstance(resposta, str) else resposta
    pagina = "https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens"
    un = {_N(k): v for k, v in (cfg.get("unidades_mpt") or {}).items()}
    out = []
    for lin in d.get("aaData") or []:
        cel = [str(c or "").strip() for c in lin]
        data = next((c for c in cel if DATA_BR.fullmatch(c)), None)
        num = next((c for c in cel if NUM_EDITAL.fullmatch(c)), None)
        proc = next((c for c in cel if PROC.fullmatch(c)), None)
        tok = next((c for c in cel if len(c) >= 40 and re.fullmatch(r"[A-Za-z0-9_\-]+", c)), None)
        unid = next((c for c in cel if c not in (data, num, proc, tok)), "")
        if not (data and (num or proc)):
            continue
        out.append({"orgao": "MPT-GO", "unidade": un.get(_N(unid), unid.title() or "PRT 18ª Região"), "numero_edital": num, "procedimento": proc,
                    "titulo": f"Edital {num or ''} para indicação de destinação de recursos ou bens — {un.get(_N(unid), unid.title())}".replace("  ", " "),
                    "data_publicacao": _iso(data), "link_oficial": pagina,
                    "ultimo_link_pdf": f"{pagina}?task=baixa&format=raw&arq={tok}" if tok else None, "fonte": "tabela_mpt", "tipo": "edital_mpt"})
    return out


def extrair_pdf_mpt(texto: str) -> dict:
    """Do texto do edital do MPT: valor, prazo em dias, exigência de cadastro e o procedimento."""
    t = re.sub(r"\s+", " ", texto or "")
    valor = None
    for m in VALOR.finditer(t):
        if re.search(r"valor|montante|import[aâ]ncia|quantia|total|at[eé]\s*$|de at[eé]", t[max(0, m.start() - 90):m.start()], re.I):
            valor = m.group(1); break
    if valor is None and (m := VALOR.search(t)):
        valor = m.group(1)
    pz = re.search(r"prazo (?:de )?(\d{1,2})\s*(?:\(\w+\)\s*)?dias", t, re.I)
    proc = PROC.search(t)
    return {"valor": f"R$ {valor}" if valor else None, "prazo_dias": int(pz.group(1)) if pz else None,
            "exige_cadastro": bool(re.search(r"cadastr\w+ (pr[eé]vi\w+|no sistema)|sistema de destina[cç][oõ]es|edital prt ?18", t, re.I)),
            "procedimento": proc.group(0) if proc else None}


def habilitadas(resposta: str | dict, padrao: str) -> dict:
    d = json.loads(resposta) if isinstance(resposta, str) else resposta
    nomes = [str((l or [""])[0]) for l in d.get("aaData") or []]
    return {"total": int(d.get("iTotalRecords") or len(nomes)), "associacao_consta": any(re.search(padrao, n, re.I) for n in nomes)}


def links_da_listagem(html: str, base: str) -> list[dict]:
    """Links de uma listagem HTML com o texto e a data mais próxima (no próprio texto, no entorno ou no endereço)."""
    out = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if len(texto) < 12:
            continue
        # 03/10 (teste do motor 10): a data é procurada DEPOIS do link até o próximo link e, se não houver, ANTES dele desde o
        # link anterior — a janela fixa de 300 caracteres dava a data do item vizinho a quase todos os links da lista.
        prox = html.find("<a ", m.end()); prox = len(html) if prox < 0 else prox
        ant = html.rfind("</a>", 0, m.start()); ant = 0 if ant < 0 else ant + 4
        depois = re.sub(r"<[^>]+>", " ", html[m.end():min(prox, m.end() + 300)])
        antes = re.sub(r"<[^>]+>", " ", html[max(ant, m.start() - 300):m.start()])
        url = urllib.parse.urljoin(base, m.group(1))
        mu = re.search(r"/(20\d\d)/(\d{2})/(\d{2})(?:/|$)", url)
        out.append({"titulo": texto[:300], "url": url, "data_publicacao": _iso(texto) or _iso(depois) or _iso(antes)
                    or (f"{mu.group(1)}-{mu.group(2)}-{mu.group(3)}" if mu else None)})
    return out


def itens_do_rss(xml: str) -> list[dict]:
    out = []
    for it in re.findall(r"<item\b.*?</item>", xml or "", re.S | re.I):
        g = lambda tag: (re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", it, re.S | re.I) or [None, ""])[1]   # noqa: E731
        tit = re.sub(r"<!\[CDATA\[|\]\]>|<[^>]+>", "", g("title")).strip()
        data = None
        try:
            from email.utils import parsedate_to_datetime
            data = parsedate_to_datetime(g("pubDate").strip()).date().isoformat() if g("pubDate").strip() else _iso(g("dc:date"))
        except Exception:  # noqa: BLE001
            data = _iso(g("dc:date"))
        out.append({"titulo": tit[:300], "url": g("link").strip(), "data_publicacao": data,
                    "descricao": re.sub(r"<!\[CDATA\[|\]\]>|<[^>]+>", " ", g("description"))[:600]})
    return out


_UF_FORA = r"(?:AC|AL|AP|AM|BA|CE|DF|ES|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)"


def outra_regional(titulo: str) -> bool:
    """Edital de OUTRA regional do MPT (não a 18ª, de Goiás). 03/10 (teste do motor 10): também "MPT/AL", "MPT-PA/AP" e
    "entidades de ES" — antes o cadastro do MPT do Espírito Santo entrava como ACOMPANHAR para a A.M.C."""
    t = str(titulo or "")
    return bool(re.search(r"\bPRT[- ]?(?!18\b)\d{1,2}\b|\b(?!18)\d{1,2}[ªa] Regi[aã]o|\bMPT\s*[-/ ]\s*(?!GO\b)[A-Z]{2}\b|"
                          r"\b(?:de|do|da|no|na|em)\s+" + _UF_FORA + r"\b(?!\$)", t))


def texto_visivel(html: str) -> str:
    """Texto que o leitor vê: sem <script>, <style> e comentários (03/10: no gov.br, 2 mil caracteres de código ficam entre
    o título "Seleção em andamento" e o "Não há" — o motor via a seleção aberta e alarmava sem motivo)."""
    h = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>|<!--.*?-->", " ", html or "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def selecao_sem_edital(texto: str) -> bool:
    """FDD: "Não há" perto de "Seleção em andamento" — ANTES ou DEPOIS da palavra (a página pode trazer as duas ordens)."""
    t = re.sub(r"\s+", " ", texto or "")
    for m in re.finditer(r"sele[cç][aã]o", t, re.I):
        if re.search(r"n[aã]o h[aá]", t[max(0, m.start() - 300):m.end() + 300], re.I):
            return True
    return not re.search(r"sele[cç][aã]o", t, re.I)       # sem a seção, não há alarme


def pagina_como_item(html: str, url: str) -> dict | None:
    """Página de notícia avulsa (ex.: o cadastro do MPF em Goiás) lida como o PRÓPRIO item: título e data da publicação."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I) or re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if not h1:
        return None
    tit = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h1.group(1))).strip()
    pub = re.search(r"(?:publicad[oa]|data|em)\s*:?\s*(\d{2}/\d{2}/\d{4})", re.sub(r"<[^>]+>", " ", html), re.I)
    return {"titulo": tit[:300], "url": url, "data_publicacao": _iso(pub.group(1)) if pub else _iso(re.sub(r"<[^>]+>", " ", html)[:3000])}


def chave(it: dict) -> str:
    """Chave natural: órgão|unidade|número|procedimento (ou o título normalizado com a data, sem número)."""
    if it.get("numero_edital") or it.get("procedimento"):
        return "|".join(str(it.get(k) or "") for k in ("orgao", "unidade", "numero_edital", "procedimento"))
    return f"{it.get('orgao')}|{re.sub(r'[^A-Z0-9 ]', '', _N(it.get('titulo')))[:120]}|{it.get('data_publicacao') or ''}"


def classificar(it: dict, hoje: date, cfg: dict) -> dict:
    """OPORTUNIDADE · ACOMPANHAR · RUÍDO, sempre com o motivo (regras da seção 3 do relatório e vetos da seção 6)."""
    txt = f"{it.get('titulo') or ''} {it.get('descricao') or ''}"
    if it.get("outra_regional"):
        return {**it, "classificacao": "RUIDO", "motivo": "veto: edital de outra regional do MPT (fora de Goiás)"}
    for padrao, motivo in cfg.get("lexico_veto") or []:
        if re.search(padrao, txt, re.I):
            return {**it, "classificacao": "RUIDO", "motivo": f"veto: {motivo}"}
    if it.get("tipo") == "edital_mpt":
        pub = date.fromisoformat(it["data_publicacao"]) if it.get("data_publicacao") else None
        dias = int(it.get("prazo_dias") or cfg.get("mpt_prazo_dias", 5))
        seg = (pub + timedelta(days=dias - 1)).isoformat() if pub else None
        it = {**it, "prazo_dias": dias, "prazo_tipo": None, "data_limite_segura": seg, "exige_cadastro": it.get("exige_cadastro")}
        if seg and seg >= hoje.isoformat():
            # 03/10 (teste do motor 09): o edital 009220.2026 aceita "qualquer pessoa jurídica de direito privado", com a indicação nos
            # autos do PA-INTER — a exigência de cadastro só é escrita quando o PDF a traz
            cad = {True: "exige cadastro prévio no Sistema de Destinações", False: "o edital não exige cadastro prévio: a indicação é feita nos autos do procedimento",
                   None: "conferir no PDF se exige cadastro prévio (o PDF não foi lido)"}[it["exige_cadastro"]]
            return {**it, "fim": seg, "classificacao": "OPORTUNIDADE",
                    "motivo": f"edital de {dias} dias aberto (o edital não diz se são úteis ou corridos; data segura {seg}); {cad}"}
        return {**it, "classificacao": "ACOMPANHAR", "motivo": "edital de 5 dias encerrado — mostra o padrão e o ritmo da unidade"}
    fora = (cfg.get("fora_do_territorio") or {}).get(it.get("orgao"))
    if fora:
        return {**it, "classificacao": "ACOMPANHAR", "motivo": fora}
    alvo = [p for p in cfg.get("lexico_alvo") or [] if re.search(p, txt, re.I)]
    if not alvo:
        return {**it, "classificacao": "RUIDO", "motivo": "sem termo de destinação a entidades"}
    if it.get("alerta_selecao"):
        return {**it, "classificacao": "OPORTUNIDADE", "motivo": "a página de seleção em andamento deixou de dizer 'Não há' — conferir o edital"}
    return {**it, "classificacao": "ACOMPANHAR", "motivo": f"menciona destinação ({alvo[0]}) — conferir o edital na fonte"}


def mesclar(itens: list[dict]) -> list[dict]:
    """Um edital visto em duas fontes = um registro (fontes_encontradas reúne as fontes)."""
    por = {}
    for it in itens:
        k = chave(it)
        if k in por:
            a = por[k]
            a["fontes_encontradas"] = sorted(set(a.get("fontes_encontradas") or [a.get("fonte")]) | {it.get("fonte")})
            for c, v in it.items():
                if v and not a.get(c):
                    a[c] = v
        else:
            por[k] = {**it, "chave": k, "fontes_encontradas": [it.get("fonte")]}
    return list(por.values())


def registro_base(it: dict, hoje: date) -> dict:
    """Registro para a base de oportunidades (mesmo formato dos outros motores)."""
    k = it.get("chave") or chave(it)
    return {"id": sha256(f"mp12|{k}".encode())[:20], "status": "capturada", "titulo": _limpo(it.get("titulo"), 300),
            "url": it.get("ultimo_link_pdf") or it.get("link_oficial") or it.get("url"), "url_noticia": it.get("link_oficial") or it.get("url"),
            "fonte_id": MOTOR_ID, "fonte_nome": f"Motor 12 — {it.get('orgao')}", "orgao": f"{it.get('orgao')} — {it.get('unidade') or ''}".strip(" —"),
            "territorio": "GO" if it.get("orgao") in ("MPT-GO", "MP-GO", "MPF") else "BR", "uf": "GO" if it.get("orgao") in ("MPT-GO", "MP-GO", "MPF") else None,
            "data_publicacao": it.get("data_publicacao"), "data_consulta": hoje.isoformat(), "fim": it.get("fim"),
            "evidencia": _limpo(" · ".join(str(x) for x in (it.get("titulo"), it.get("valor") and f"valor {it['valor']}", it.get("procedimento") and f"procedimento {it['procedimento']}",
                                                            it.get("motivo")) if x)), "categoria": it.get("tipo") or "destinacao_mp", "classificacao": it.get("classificacao"),
            "numero_edital": it.get("numero_edital"), "procedimento": it.get("procedimento"), "valor": it.get("valor"), "prazo_dias": it.get("prazo_dias"),
            "prazo_tipo": it.get("prazo_tipo"), "data_limite_segura": it.get("data_limite_segura"), "exige_cadastro": it.get("exige_cadastro"),
            "fluxo_continuo": it.get("fluxo_continuo"), "chave": k}


def inventario_base() -> list[dict]:
    """O histórico de 3 anos do estudo (92 registros) → achados para os livros (entra UMA vez)."""
    if not INVENTARIO.exists():
        return []
    out = []
    for r in csv.DictReader(io.StringIO(INVENTARIO.read_text(encoding="utf-8-sig")), delimiter=";"):
        if r.get("classificacao") == "RUIDO":
            continue
        out.append({"titulo": _limpo(r.get("titulo"), 260), "programa": _limpo(r.get("titulo"), 160), "orgao": f"{r.get('orgao')} — {r.get('unidade')}".strip(" —"),
                    "url": r.get("link_oficial") or r.get("link_pdf"), "pagina_oficial": r.get("link_oficial"), "data_publicacao": r.get("data_publicacao") or None,
                    "inicio": r.get("inscricao_inicio") or None, "fim": r.get("inscricao_fim") or None, "valor": r.get("valor") or None,
                    "uf": "GO" if r.get("orgao") in ("MPT-GO", "MP-GO", "MPF") else None, "fonte_id": MOTOR_ID, "origem": "inventário-base do motor 12 (estudo de 02/10/2026)"})
    return out


# ─── leitura ───────────────────────────────────────────────────────────────────────────────────────────────────────
def _opener():
    import http.cookiejar
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def _tabela(pagina: str, task: str, cfg: dict, n: int = 200) -> dict:
    """O que a página do PRT-18 faz no navegador: abre a página (cookie e token público do formulário) e pede a tabela."""
    op = _opener(); _SESSAO["op"] = op                  # o PDF do edital é baixado nesta mesma sessão (cookie)
    h = _abrir(pagina, cfg, op).decode("utf-8", "ignore")
    tok = re.search(r'\{\s*"name"\s*:\s*"([0-9a-f]{32})"\s*,\s*"value"\s*:\s*"1"\s*\}', h)
    dados = {"sEcho": "1", "iColumns": "5", "iDisplayStart": "0", "iDisplayLength": str(n), "sSearch": "", "option": "com_mpt", "task": task, "format": "raw"}
    if tok:
        dados[tok.group(1)] = "1"
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(pagina))
    return json.loads(_abrir(base + "/index.php", cfg, op, dados, pagina).decode("utf-8", "ignore"))


_PDF_ERRO = {"motivo": None}


def _texto_pdf(b: bytes) -> str:
    _PDF_ERRO["motivo"] = None
    try:
        from pypdf import PdfReader
    except Exception:  # noqa: BLE001
        _PDF_ERRO["motivo"] = "sem_leitor_pdf"            # 03/10: registrado no diagnóstico — o PDF não foi lido
        return ""
    if not (b or b"").lstrip().startswith(b"%PDF"):
        _PDF_ERRO["motivo"] = "resposta_nao_e_pdf"
        return ""
    try:
        return " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(b)).pages[:8])
    except Exception:  # noqa: BLE001 — PDF sem texto: valem os dados da tabela
        _PDF_ERRO["motivo"] = "pdf_sem_texto"
        return ""


def busca_doe(fonte: dict, hoje: date) -> list[dict]:
    """03/10/2026 (teste do motor 08): leitura INDIRETA do Destina/DAAMP do MP-GO. O site do MP-GO proíbe robôs; quem
    recebe e aplica o recurso (prefeituras, entidades) publica no Diário Oficial do Estado, que é aberto. Cada página
    achada vira um item de inteligência (quem recebeu, área, valor) — nunca edital."""
    from . import diario_goias as dg
    de = (hoje - timedelta(days=int(fonte.get("janela_dias", 365)))).isoformat()
    out, vistos = [], set()
    for q in fonte.get("consultas") or []:
        for pg in range(5):
            j = dg._get_json(dg.url_busca(q, de, hoje.isoformat(), pg))
            hits = ((j.get("hits") or {}).get("hits")) or []
            for h in hits:
                src = h.get("_source") or {}
                k = f"{src.get('diario_id')}|{src.get('pagina')}"
                if k in vistos:
                    continue
                vistos.add(k)
                c = re.sub(r"\s+", " ", src.get("conteudo") or "")
                m = re.search(r"DAAMP|Destina[çc][ãa]o Articulada|Centro de Autocomposi", c, re.I)
                if not m:
                    continue
                trecho = c[max(0, m.start() - 400): m.end() + 300]
                if has_prompt_injection(trecho):
                    continue
                quem = re.search(r"(?:Munic[ií]pio|Prefeitura Municipal) de ([A-ZÀ-Ú][\wÀ-ú' ]{2,40}?)(?:/GO|-GO| -|,|\.|\s{2})", trecho)
                obj = re.search(r"Obj[e]?[t]?o\s*:\s*(.{20,200}?)(?:,? em conformidade|\.|;)", trecho, re.I)
                out.append({"orgao": "MP-GO", "unidade": fonte.get("unidade"), "fonte": fonte["id"], "tipo": "busca_doe",
                            "titulo": "Recurso do Destina/DAAMP do MP-GO aplicado" + (f" — {quem.group(1).strip()}" if quem else "")
                                      + (f" — {obj.group(1).strip()}" if obj else ""),
                            "descricao": _limpo(CPF.sub("[CPF]", trecho), 700), "data_publicacao": str(src.get("data") or "")[:10] or None,
                            "link_oficial": f"{dg.BASE}/portal/visualizacoes/pdf/{src.get('diario_id')}/#e:{src.get('diario_id')}",
                            "url": f"{dg.BASE}/portal/visualizacoes/pdf/{src.get('diario_id')}/#e:{src.get('diario_id')}",
                            "pagina_doe": src.get("pagina"), "classificacao": "ACOMPANHAR",
                            "motivo": "leitura indireta: recurso de acordo do MP-GO (Destina/DAAMP) aplicado por quem recebeu — "
                                      "mostra para onde vai o dinheiro, áreas e valores; não é edital"})
            if len(hits) < 10:
                break
    return out


def lacuna_da_listagem(links: list[dict], desde: str | None) -> bool:
    """PUBLICADO × LIDO (03/10): a 1ª página só cobre o intervalo desde a última leitura se o item datado mais antigo dela
    for anterior (ou igual) a essa leitura. Página inteira mais nova que a última leitura = pode haver itens não lidos."""
    datas = sorted(l["data_publicacao"] for l in links if l.get("data_publicacao"))
    return bool(desde and len(datas) >= 3 and datas[0] > desde)


def feed_parado(itens: list[dict], hoje: date, dias: int = 45) -> bool:
    """RSS cujo item mais novo tem mais de `dias` dias: a fonte parou de publicar ali (03/10: o RSS de notícias da PGT
    parou em 28/07/2026)."""
    datas = [i["data_publicacao"] for i in itens if i.get("data_publicacao")]
    return bool(datas) and max(datas) < (hoje - timedelta(days=dias)).isoformat()


def _devido(fonte: dict, est: dict, cfg: dict, hoje: date) -> bool:
    cad = int((cfg.get("cadencia_dias") or {}).get(fonte["modo"], 7))
    u = (est.get("ultima_por_fonte") or {}).get(fonte["id"])
    return not u or u <= (hoje - timedelta(days=cad)).isoformat()


def _so_regra_fixa(cfg: dict) -> bool:
    """A parte do motor não tem leitura DIRETA da fonte (só regra fixa e leitura indireta) — caso do MP-GO."""
    fs = [x for x in cfg["fontes"] if _da_parte(x["orgao"])]
    return bool(fs) and not any(x["modo"] in ("tabela_mpt", "lista_habilitadas", "listagem_html", "rss", "estado_pagina", "pagina_item") for x in fs)


def _texto_regra_fixa(diag: dict, cfg: dict) -> str:
    ind = [v for v in diag["fontes"].values() if v.get("modo") == "busca_doe"]
    lida = ind and ind[0].get("situacao") in ("lida", "em dia (cadência)")
    ult = (cfg.get("verificacoes_manuais") or {}).get(_PARTE["id"])
    return ("sem leitura automática: o site do MP-GO proíbe robôs. Leitura indireta pelo Diário do Estado: "
            + ("feita" if lida else "falhou" if ind and ind[0].get("situacao") == "falhou" else "não feita")
            + f". Conferência manual mensal: {('em ' + str(ult)) if ult else 'ainda não registrada'}.")


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 12 com a mesma saída de `sensores.ler`."""
    hoje = hoje or (sensor or {}).get("_data") or datetime.now(timezone(timedelta(hours=-3))).date()
    cfg = _cfg(); est = load_json(ESTADO) if ESTADO.exists() else {}
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 600))
    diag = {"versao": "motor 12 Ministérios Públicos v2 (02/10/2026)", "fontes": {}, "nunca_acessadas": cfg.get("nunca_acessar"), "pdfs_lidos": 0, "sem_texto": 0}
    itens, falhas, saude = [], [], []
    pdf_cache = est.setdefault("pdf_cache", {})
    for f in [x for x in cfg["fontes"] if _da_parte(x["orgao"])]:
        D = diag["fontes"].setdefault(f["id"], {"orgao": f["orgao"], "modo": f["modo"], "url": f["url"]})
        if f["modo"] in ("regra_fixa_manual", "regra", "requer_navegador", "ruido_conhecido"):
            D["situacao"] = {"regra_fixa_manual": "nunca acessada (regra fixa; verificação manual mensal)", "regra": "referência (sem coleta)",
                             "requer_navegador": "requer navegador (sem coleta automática)", "ruido_conhecido": "ruído conhecido (não lida)"}[f["modo"]]
            continue
        if not _devido(f, est, cfg, hoje):
            D["situacao"] = "em dia (cadência)"; continue
        try:
            if f["modo"] == "tabela_mpt":
                novos = linhas_tabela_mpt(_tabela(f["url"], "editaisdestinacaorecursosoubens", cfg), cfg)
                for it in novos:
                    k = chave(it)
                    if k in pdf_cache:
                        it.update(pdf_cache[k])
                    elif it.get("ultimo_link_pdf") and diag["pdfs_lidos"] < int(cfg.get("pdfs_por_leitura", 15)) \
                            and str(it.get("data_publicacao") or "") >= (hoje - timedelta(days=60)).isoformat():
                        t = _texto_pdf(_abrir(it["ultimo_link_pdf"], cfg, _SESSAO.get("op"))); diag["pdfs_lidos"] += 1
                        if not t.strip():
                            diag["sem_texto"] += 1
                            diag.setdefault("pdf_motivos", {})[_PDF_ERRO["motivo"] or "pdf_sem_texto"] = diag.get("pdf_motivos", {}).get(_PDF_ERRO["motivo"] or "pdf_sem_texto", 0) + 1
                            it["exige_cadastro"] = None                # 03/10: sem o PDF não se sabe — não presumir cadastro
                            continue
                        if has_prompt_injection(t):
                            D.setdefault("quarentena", []).append(k); continue
                        x = {kk: v for kk, v in extrair_pdf_mpt(t).items() if v is not None}
                        x.pop("procedimento", None); it.update(x); pdf_cache[k] = x
                itens += novos; D.update({"situacao": "lida", "itens": len(novos)})
            elif f["modo"] == "lista_habilitadas":
                h = habilitadas(_tabela(f["url"], "entidadesassistenciais", cfg), cfg["associacao"]["reconhecer"])
                est["habilitadas"] = {**h, "em": hoje.isoformat()}; D.update({"situacao": "lida", **h})
            elif f["modo"] == "listagem_html":
                todos = links_da_listagem(_abrir(f["url"], cfg).decode("utf-8", "ignore"), f["url"])
                desde = (est.get("ultima_por_fonte") or {}).get(f["id"])
                pag = f.get("paginacao")                    # ex.: "?b_start:int={offset}" (passo = itens por página)
                n = 0
                while lacuna_da_listagem(todos, desde) and pag and n < int(f.get("max_paginas", 5)):
                    n += 1
                    todos += links_da_listagem(_abrir(f["url"].split("?")[0] + pag.format(offset=n * int(f.get("passo", 10))), cfg)
                                               .decode("utf-8", "ignore"), f["url"])
                if lacuna_da_listagem(todos, desde):
                    diag.setdefault("paginas_nao_lidas", []).append(f"{f['id']} {f['orgao']}: a listagem não alcança a última leitura ({desde})")
                    D["lacuna"] = True                       # a última leitura não avança: a próxima passagem relê
                elif n:
                    D["paginas_extras"] = n
                ls = [l for l in todos if any(re.search(p, l["titulo"], re.I) for p in cfg.get("lexico_alvo") or [])]
                itens += [{**l, "orgao": f["orgao"], "unidade": f["unidade"], "link_oficial": l["url"], "fonte": f["id"], "tipo": "listagem"} for l in ls]
                D.update({"situacao": "lida", "itens": len(ls)})
            elif f["modo"] == "pagina_item":
                pg = pagina_como_item(_abrir(f["url"], cfg).decode("utf-8", "ignore"), f["url"])
                if pg and any(re.search(p, pg["titulo"], re.I) for p in cfg.get("lexico_alvo") or []):
                    itens.append({**pg, "orgao": f["orgao"], "unidade": f["unidade"], "link_oficial": f["url"], "fonte": f["id"], "tipo": "pagina_item"})
                D.update({"situacao": "lida", "itens": 1 if pg else 0})
            elif f["modo"] == "rss":
                todos = itens_do_rss(_abrir(f["url"], cfg).decode("utf-8", "ignore"))
                if feed_parado(todos, hoje):
                    D["feed_parado"] = max(i["data_publicacao"] for i in todos if i.get("data_publicacao"))
                    diag.setdefault("alertas", []).append(f"{f['id']}: o feed parou em {D['feed_parado']} — trocar a rota")
                rs = [r for r in todos
                      if re.search(r"destina[cç][aã]o|cadastr|revers[aã]o", f"{r['titulo']} {r['descricao']}", re.I)]
                for r in rs:   # editais de OUTRAS regionais do MPT são ruído para a A.M.C.
                    r["outra_regional"] = outra_regional(r["titulo"])
                itens += [{**r, "orgao": f["orgao"], "unidade": f["unidade"], "link_oficial": r["url"], "fonte": f["id"], "tipo": "rss"} for r in rs]
                D.update({"situacao": "lida", "itens": len(rs)})
            elif f["modo"] == "busca_doe":
                bd = busca_doe(f, hoje)
                itens += bd; D.update({"situacao": "lida", "itens": len(bd)})
            elif f["modo"] == "estado_pagina":
                t = texto_visivel(_abrir(f["url"], cfg).decode("utf-8", "ignore"))
                nao_ha = selecao_sem_edital(t)
                est["fdd_selecao"] = {"nao_ha": nao_ha, "em": hoje.isoformat()}; D.update({"situacao": "lida", "selecao_aberta": not nao_ha})
                if not nao_ha:
                    itens.append({"titulo": "FDD/CFDD — seleção em andamento (a página deixou de dizer 'Não há')", "orgao": f["orgao"], "unidade": f["unidade"],
                                  "link_oficial": f["url"], "url": f["url"], "data_publicacao": None, "fonte": f["id"], "tipo": "estado_pagina",
                                  "alerta_selecao": True, "descricao": "fundo de defesa de direitos difusos"})
            if not D.get("lacuna"):
                est.setdefault("ultima_por_fonte", {})[f["id"]] = hoje.isoformat()
            saude.append({"url": f["url"], "http": 200, "itens": D.get("itens", 0)})
        except AcessoProibido as e:
            D["situacao"] = f"não acessada: {e}"
        except Exception as e:  # noqa: BLE001 — uma fonte nunca derruba as outras
            D["situacao"] = "falhou"; falhas.append({"url": f["url"], "erro": type(e).__name__, "code": getattr(e, "code", None), "waf": None, "causa": str(e)[:160]})
    _PRAZO["ate"] = None
    # 03/10: o alerta do FDD continua enquanto a última leitura disser que há seleção (antes sumia na leitura seguinte,
    # porque não tem prazo e a fonte só é relida pela cadência)
    if "estado_pagina" not in {(diag["fontes"].get(x["id"]) or {}).get("modo") for x in cfg["fontes"] if (diag["fontes"].get(x["id"]) or {}).get("situacao") == "lida"} \
            and (est.get("fdd_selecao") or {}).get("nao_ha") is False:
        f35 = next((x for x in cfg["fontes"] if x["modo"] == "estado_pagina" and _da_parte(x["orgao"])), None)
        if f35:
            itens.append({"titulo": "FDD/CFDD — seleção em andamento (a página deixou de dizer 'Não há')", "orgao": f35["orgao"], "unidade": f35["unidade"],
                          "link_oficial": f35["url"], "url": f35["url"], "data_publicacao": None, "fonte": f35["id"], "tipo": "estado_pagina",
                          "alerta_selecao": True, "descricao": "fundo de defesa de direitos difusos"})
    # registros fixos (regras permanentes que nunca são acessadas pelo robô)
    for r in [x for x in cfg.get("registros_fixos") or [] if _da_parte(x.get("orgao"))]:
        itens.append({**{k: v for k, v in r.items() if k != "chave"}, "fonte": "regra_fixa_manual", "tipo": "regra_fixa", "data_publicacao": None})
    classif = []
    for it in mesclar(itens):
        if it.get("tipo") == "regra_fixa":
            classif.append({**it, "classificacao": it.get("classificacao", "OPORTUNIDADE")})
        elif it.get("tipo") == "busca_doe":
            classif.append(it)                 # 03/10: inteligência já classificada (o veto "ao município de" não se aplica)
        else:
            classif.append(classificar(it, hoje, cfg))
    for it in classif:
        it["data_consulta"] = hoje.isoformat(); it["titulo"] = _limpo(it.get("titulo"), 300)
    # abertas VIVAS continuam de uma leitura para a outra (a cadência não relê toda fonte todo dia): fica enquanto o prazo
    # seguro não venceu; a regra permanente (fluxo contínuo) fica sempre; a leitura nova substitui a antiga pela chave
    d0 = hoje.isoformat()
    ab = {x["chave"]: x for x in est.get("abertas_registros") or []
          if x.get("fluxo_continuo") or (x.get("fim") and str(x["fim"]) >= d0)}
    ab.update({x["chave"]: x for x in classif if x["classificacao"] == "OPORTUNIDADE"})
    for k, x in list(ab.items()):                      # o que a leitura nova rebaixou (ex.: encerrou) sai das abertas
        if any(c["chave"] == k and c["classificacao"] != "OPORTUNIDADE" for c in classif):
            ab.pop(k)
    abertas = sorted(ab.values(), key=lambda x: (not x.get("fim"), str(x.get("fim") or "9999")))
    acomp = {x["chave"]: x for x in est.get("acompanhar") or []}
    acomp.update({x["chave"]: x for x in classif if x["classificacao"] == "ACOMPANHAR"})
    limite = (hoje - timedelta(days=1100)).isoformat()
    acompanhar = sorted([a for a in acomp.values() if str(a.get("data_publicacao") or hoje.isoformat()) >= limite],
                        key=lambda a: str(a.get("data_publicacao") or ""), reverse=True)[:400]
    _alvo = {"mpgo-destinacao": ("Destina",), "mptgo-destinacao": ("Sistema de Destinações", "trabalhista"), "mpu-destinacao": ("MPF",)}.get(_PARTE["id"])
    # 03/10 (teste do motor 08): palavra inteira — "Destina" casava com "Sistema de Destinações" e a pendência do MPT
    # aparecia no motor do MP-GO
    pend = [p for p in cfg.get("pendencias_presidente") or [] if not _alvo or any(re.search(rf"\b{re.escape(a)}\b", p) for a in _alvo)]
    vm = (cfg.get("verificacoes_manuais") or {})
    if _PARTE["id"] in vm:
        ult = vm.get(_PARTE["id"])
        if not ult or str(ult) < (hoje - timedelta(days=30)).isoformat():
            pend.append("Conferência manual mensal do Destina no site do MP-GO (o robô não pode entrar): "
                        + (f"a última foi em {ult}." if ult else "ainda não registrada.") + " Depois de conferir, avise para registrar a data.")
    if (est.get("habilitadas") or {}).get("associacao_consta"):
        pend = [p for p in pend if "Sistema de Destinações" not in p]
    # inventário de 3 anos nos livros: UMA vez (com nova tentativa se falhar)
    inv = est.setdefault("inventario", {})
    if not inv.get("inventario_base_registrado"):
        try:
            from .livros_regra import registrar_achados
            r = registrar_achados([x for x in inventario_base() if _da_parte(x.get("orgao", "").split(" — ")[0])],
                                  f"{MOTOR_ID} — inventário-base (estudo de 02/10/2026)")
            inv.update({"inventario_base_registrado": True, "em": now_iso(), "resultado": {k: v for k, v in (r or {}).items() if isinstance(v, (int, str))}})
            inv.pop("pendentes_livros", None)
        except Exception as e:  # noqa: BLE001
            inv["pendentes_livros"] = f"{type(e).__name__}: {str(e)[:120]} — nova tentativa na próxima leitura"
    est.update({"abertas_registros": abertas, "acompanhar": acompanhar, "pendencias_presidente": pend,
                "ruido_ultimo": [x for x in classif if x["classificacao"] == "RUIDO"][:60],
                "ultima": {"em": now_iso(), "data": hoje.isoformat(), "abertas": len(abertas), "acompanhar": len(acompanhar), "falhas": len(falhas),
                           **({"regra_fixa": _texto_regra_fixa(diag, cfg)} if _so_regra_fixa(cfg) else {})}})
    write_json(ESTADO, est)
    cont = {c: sum(1 for x in classif if x["classificacao"] == c) for c in ("OPORTUNIDADE", "ACOMPANHAR", "RUIDO")}
    diag.update({"vereditos": cont, "abertas": len(abertas), "pendencias_presidente": pend, "habilitadas": est.get("habilitadas"),
                 "paginas_lidas": len(saude), "links_total": len(itens), "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"],
                 "inventario": {k: v for k, v in inv.items() if k != "resultado"},
                 "motivo_zero": None if abertas else "nenhum edital de destinação aberto hoje nas fontes lidas"})
    if diag.get("sem_texto"):          # 03/10: edital cujo PDF não foi lido = leitura parcial (o maestro dispara de novo)
        diag["cortados"] = diag["sem_texto"]
    if diag.get("paginas_nao_lidas"):                    # 03/10: o maestro vê "parcial" e dispara de novo
        diag["paginas_nao_lidas"] = diag["paginas_nao_lidas"][:10]
    return {"sensor": MOTOR_ID, "achados": [registro_base(x, hoje) for x in abertas], "falhas": falhas[:8], "saude": saude,
            "diagnostico": diag, "lido_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2)[:4000])
