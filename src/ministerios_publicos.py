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
        perto = re.sub(r"<[^>]+>", " ", html[max(0, m.start() - 300):m.end() + 300])
        url = urllib.parse.urljoin(base, m.group(1))
        mu = re.search(r"/(20\d\d)/(\d{2})/(\d{2})(?:/|$)", url)
        out.append({"titulo": texto[:300], "url": url, "data_publicacao": _iso(texto) or _iso(perto) or (f"{mu.group(1)}-{mu.group(2)}-{mu.group(3)}" if mu else None)})
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


def outra_regional(titulo: str) -> bool:
    """Edital de OUTRA regional do MPT (não a 18ª, de Goiás)."""
    return bool(re.search(r"\bPRT[- ]?(?!18\b)\d{1,2}\b|\b(?!18)\d{1,2}[ªa] Regi[aã]o|\bMPT[- ](?!GO\b)[A-Z]{2}\b", str(titulo or "")))


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
        it = {**it, "prazo_dias": dias, "prazo_tipo": None, "data_limite_segura": seg, "exige_cadastro": it.get("exige_cadastro", True)}
        if seg and seg >= hoje.isoformat():
            return {**it, "fim": seg, "classificacao": "OPORTUNIDADE",
                    "motivo": f"edital de {dias} dias aberto (o edital não diz se são úteis ou corridos; data segura {seg}); exige cadastro prévio no Sistema de Destinações"}
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
    op = _opener()
    h = _abrir(pagina, cfg, op).decode("utf-8", "ignore")
    tok = re.search(r'\{\s*"name"\s*:\s*"([0-9a-f]{32})"\s*,\s*"value"\s*:\s*"1"\s*\}', h)
    dados = {"sEcho": "1", "iColumns": "5", "iDisplayStart": "0", "iDisplayLength": str(n), "sSearch": "", "option": "com_mpt", "task": task, "format": "raw"}
    if tok:
        dados[tok.group(1)] = "1"
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(pagina))
    return json.loads(_abrir(base + "/index.php", cfg, op, dados, pagina).decode("utf-8", "ignore"))


def _texto_pdf(b: bytes) -> str:
    try:
        from pypdf import PdfReader
        return " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(b)).pages[:8])
    except Exception:  # noqa: BLE001 — sem pypdf ou PDF sem texto: valem os dados da tabela
        return ""


def _devido(fonte: dict, est: dict, cfg: dict, hoje: date) -> bool:
    cad = int((cfg.get("cadencia_dias") or {}).get(fonte["modo"], 7))
    u = (est.get("ultima_por_fonte") or {}).get(fonte["id"])
    return not u or u <= (hoje - timedelta(days=cad)).isoformat()


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None) -> dict:
    """Leitura do motor 12 com a mesma saída de `sensores.ler`."""
    hoje = hoje or (sensor or {}).get("_data") or datetime.now(timezone(timedelta(hours=-3))).date()
    cfg = _cfg(); est = load_json(ESTADO) if ESTADO.exists() else {}
    _PRAZO["ate"] = time.monotonic() + float(cfg.get("prazo_total_segundos", 600))
    diag = {"versao": "motor 12 Ministérios Públicos v2 (02/10/2026)", "fontes": {}, "nunca_acessadas": cfg.get("nunca_acessar"), "pdfs_lidos": 0, "sem_texto": 0}
    itens, falhas, saude = [], [], []
    pdf_cache = est.setdefault("pdf_cache", {})
    for f in cfg["fontes"]:
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
                        t = _texto_pdf(_abrir(it["ultimo_link_pdf"], cfg)); diag["pdfs_lidos"] += 1
                        if not t.strip():
                            diag["sem_texto"] += 1; continue
                        if has_prompt_injection(t):
                            D.setdefault("quarentena", []).append(k); continue
                        x = {kk: v for kk, v in extrair_pdf_mpt(t).items() if v is not None}
                        x.pop("procedimento", None); it.update(x); pdf_cache[k] = x
                itens += novos; D.update({"situacao": "lida", "itens": len(novos)})
            elif f["modo"] == "lista_habilitadas":
                h = habilitadas(_tabela(f["url"], "entidadesassistenciais", cfg), cfg["associacao"]["reconhecer"])
                est["habilitadas"] = {**h, "em": hoje.isoformat()}; D.update({"situacao": "lida", **h})
            elif f["modo"] == "listagem_html":
                ls = [l for l in links_da_listagem(_abrir(f["url"], cfg).decode("utf-8", "ignore"), f["url"])
                      if any(re.search(p, l["titulo"], re.I) for p in cfg.get("lexico_alvo") or [])]
                itens += [{**l, "orgao": f["orgao"], "unidade": f["unidade"], "link_oficial": l["url"], "fonte": f["id"], "tipo": "listagem"} for l in ls]
                D.update({"situacao": "lida", "itens": len(ls)})
            elif f["modo"] == "rss":
                rs = [r for r in itens_do_rss(_abrir(f["url"], cfg).decode("utf-8", "ignore"))
                      if re.search(r"destina[cç][aã]o|cadastr|revers[aã]o", f"{r['titulo']} {r['descricao']}", re.I)]
                for r in rs:   # editais de OUTRAS regionais do MPT são ruído para a A.M.C.
                    r["outra_regional"] = outra_regional(r["titulo"])
                itens += [{**r, "orgao": f["orgao"], "unidade": f["unidade"], "link_oficial": r["url"], "fonte": f["id"], "tipo": "rss"} for r in rs]
                D.update({"situacao": "lida", "itens": len(rs)})
            elif f["modo"] == "estado_pagina":
                t = re.sub(r"<[^>]+>", " ", _abrir(f["url"], cfg).decode("utf-8", "ignore"))
                nao_ha = bool(re.search(r"n[aã]o h[aá]", t[t.lower().find("sele"):][:4000] if "sele" in t.lower() else t, re.I))
                est["fdd_selecao"] = {"nao_ha": nao_ha, "em": hoje.isoformat()}; D.update({"situacao": "lida", "selecao_aberta": not nao_ha})
                if not nao_ha:
                    itens.append({"titulo": "FDD/CFDD — seleção em andamento (a página deixou de dizer 'Não há')", "orgao": f["orgao"], "unidade": f["unidade"],
                                  "link_oficial": f["url"], "url": f["url"], "data_publicacao": None, "fonte": f["id"], "tipo": "estado_pagina",
                                  "alerta_selecao": True, "descricao": "fundo de defesa de direitos difusos"})
            est.setdefault("ultima_por_fonte", {})[f["id"]] = hoje.isoformat()
            saude.append({"url": f["url"], "http": 200, "itens": D.get("itens", 0)})
        except AcessoProibido as e:
            D["situacao"] = f"não acessada: {e}"
        except Exception as e:  # noqa: BLE001 — uma fonte nunca derruba as outras
            D["situacao"] = "falhou"; falhas.append({"url": f["url"], "erro": type(e).__name__, "code": getattr(e, "code", None), "waf": None, "causa": str(e)[:160]})
    _PRAZO["ate"] = None
    # registros fixos (regras permanentes que nunca são acessadas pelo robô)
    for r in cfg.get("registros_fixos") or []:
        itens.append({**{k: v for k, v in r.items() if k != "chave"}, "fonte": "regra_fixa_manual", "tipo": "regra_fixa", "data_publicacao": None})
    classif = []
    for it in mesclar(itens):
        if it.get("tipo") == "regra_fixa":
            classif.append({**it, "classificacao": it.get("classificacao", "OPORTUNIDADE")})
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
    pend = list(cfg.get("pendencias_presidente") or [])
    if (est.get("habilitadas") or {}).get("associacao_consta"):
        pend = [p for p in pend if "Sistema de Destinações" not in p]
    # inventário de 3 anos nos livros: UMA vez (com nova tentativa se falhar)
    inv = est.setdefault("inventario", {})
    if not inv.get("inventario_base_registrado"):
        try:
            from .livros_regra import registrar_achados
            r = registrar_achados(inventario_base(), "Motor 12 — inventário-base (estudo de 02/10/2026)")
            inv.update({"inventario_base_registrado": True, "em": now_iso(), "resultado": {k: v for k, v in (r or {}).items() if isinstance(v, (int, str))}})
            inv.pop("pendentes_livros", None)
        except Exception as e:  # noqa: BLE001
            inv["pendentes_livros"] = f"{type(e).__name__}: {str(e)[:120]} — nova tentativa na próxima leitura"
    est.update({"abertas_registros": abertas, "acompanhar": acompanhar, "pendencias_presidente": pend,
                "ruido_ultimo": [x for x in classif if x["classificacao"] == "RUIDO"][:60],
                "ultima": {"em": now_iso(), "data": hoje.isoformat(), "abertas": len(abertas), "acompanhar": len(acompanhar), "falhas": len(falhas)}})
    write_json(ESTADO, est)
    cont = {c: sum(1 for x in classif if x["classificacao"] == c) for c in ("OPORTUNIDADE", "ACOMPANHAR", "RUIDO")}
    diag.update({"vereditos": cont, "abertas": len(abertas), "pendencias_presidente": pend, "habilitadas": est.get("habilitadas"),
                 "paginas_lidas": len(saude), "links_total": len(itens), "links_candidatos": cont["OPORTUNIDADE"] + cont["ACOMPANHAR"],
                 "inventario": {k: v for k, v in inv.items() if k != "resultado"},
                 "motivo_zero": None if abertas else "nenhum edital de destinação aberto hoje nas fontes lidas"})
    return {"sensor": MOTOR_ID, "achados": [registro_base(x, hoje) for x in abertas], "falhas": falhas[:8], "saude": saude,
            "diagnostico": diag, "lido_em": now_iso()}


if __name__ == "__main__":
    print(json.dumps(ler_motor()["diagnostico"], ensure_ascii=False, indent=2)[:4000])
