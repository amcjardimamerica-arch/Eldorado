"""MOTOR — OPORTUNIDADES ESTADUAIS GOVERNAMENTAIS (titular, 02/10/2026).

Só órgãos do Poder Executivo do Estado de Goiás e entidades vinculadas (secretarias, autarquias, fundações, empresas
estatais, conselhos e fundos). Agrega os antigos motores 09 (Secult), 14 (FAPEG), 15 (fundos), 16 (Goiás Social) e
17 (OVG) e todos os demais órgãos estaduais, lidos UM POR VEZ, em camadas:

  1 · DESCOBERTA       onde o órgão publica (notícias pela API do portal, páginas de editais, links do site)
  2 · HISTÓRICO        publicações dos últimos 5 anos ligadas a oportunidades, com data (busca por termos)
  3 · OPORTUNIDADES    classifica cada publicação (OPORTUNIDADE / ACOMPANHAR / RUÍDO, com o motivo); as abertas viram
                       achados; as do passado entram no histórico dos livros da Biblioteca (alimentam a previsão)
  4 · MONITORAMENTO    depois do histórico, só as publicações novas, todo dia

O portal goias.gov.br hospeda cada órgão como um site WordPress com API pública (lida da nuvem pelo motor 02).
Parâmetros e léxico: config/estaduais_go.json (léxico tirado das decisões da validação sobre órgãos estaduais).
Estado: estado/estaduais_go.json · painel: docs/dados/estaduais_go.json
"""
from __future__ import annotations

import gzip
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/estaduais_go.json"
ESTADO = ROOT / "estado/estaduais_go.json"
PAINEL = ROOT / "docs/dados/estaduais_go.json"
MOTOR_ID = "plat-estaduais-go-gov"
NOME = "Oportunidade Estaduais Governamentais de Goiás"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado/estaduais"
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
         "outubro": 10, "novembro": 11, "dezembro": 12}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def sem(t) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))


def limpar(html) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", str(html or "")))).strip()


def _get(url: str, timeout: float = 25) -> tuple[int, str, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/html;q=0.9,*/*;q=0.5",
                                               "Accept-Language": "pt-BR,pt;q=0.9", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read(6_000_000)
            if (r.headers.get("Content-Encoding") or "") == "gzip":
                b = gzip.decompress(b)
            return r.status, b.decode("utf-8", "ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"[:200], {}


# ── classificação de uma publicação (notícia ou página) ─────────────────────────────────────────────────────────────
def _prazo(txt: str, ref: date) -> date | None:
    t = sem(txt)
    cands = []
    for m in re.finditer(r"at[ée]\s+(?:o dia\s+)?(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", t):
        d, mo, a = int(m.group(1)), int(m.group(2)), m.group(3)
        ano = int(a) + (2000 if a and len(a) == 2 else 0) if a else ref.year
        cands.append((ano, mo, d))
    for m in re.finditer(r"at[ée]\s+(?:o dia\s+)?(\d{1,2})\s+de\s+([a-z]+)(?:\s+de\s+(\d{4}))?", t):
        mo = MESES.get(m.group(2))
        if mo:
            cands.append((int(m.group(3)) if m.group(3) else ref.year, mo, int(m.group(1))))
    out = []
    for a, mo, d in cands:
        try:
            x = date(a, mo, d)
            if x < ref - timedelta(days=5) and not re.search(r"\b20\d\d\b", t):   # "até 10/02" publicado em dezembro
                x = date(a + 1, mo, d)
            out.append(x)
        except ValueError:
            pass
    return max(out) if out else None


def classificar(titulo: str, resumo: str, publicado: date | None, hoje: date, lex: dict) -> dict:
    texto = f"{titulo} . {resumo}"
    t = sem(texto)
    osc = bool(re.search(lex["publico_alvo"], t))
    for veto in lex.get("vetos") or []:
        nome, rx, cede = (list(veto) + [False])[:3]
        if re.search(rx, t) and not (cede and osc and re.search(r"chamamento|termo de (fomento|colabora)|mrosc|13\.019", t)):
            return {"veredito": "RUIDO", "motivo": f"veto: {nome}"}
    if lex.get("resultado_no_titulo") and re.search(lex["resultado_no_titulo"], sem(titulo)):
        return {"veredito": "ACOMPANHAR", "motivo": "resultado, premiação ou informação sobre seleção já feita"}
    abre = bool(re.search(lex["abertura"], t))
    acomp = bool(re.search(lex["acompanhar"], t))
    pz = _prazo(texto, publicado or hoje)
    if abre and osc and not re.search(r"^(resultado|homologa|aprovados|selecionados|classificados)", sem(titulo)):
        aberta = (pz and pz >= hoje) or (not pz and publicado and (hoje - publicado).days <= 45)
        return {"veredito": "OPORTUNIDADE", "motivo": "abertura de seleção para entidades/projetos", "prazo": pz.isoformat() if pz else None,
                "aberta": bool(aberta)}
    if acomp or (abre and not osc):
        return {"veredito": "ACOMPANHAR", "motivo": "resultado, celebração ou repasse" if acomp else "seleção sem público de entidades identificado",
                "prazo": pz.isoformat() if pz else None}
    return {"veredito": "RUIDO", "motivo": "sem sinal de oportunidade"}


# ── camadas ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _continua(titulo: str, hoje: date, lex: dict) -> bool:
    """Reavalia uma oportunidade já guardada (só o título): sai só o que cai num VETO ou é RESULTADO — nunca por falta de
    sinal, porque a confirmação pode ter vindo do resumo, que não fica guardado."""
    c = classificar(titulo, "", None, hoje, lex)
    return not (str(c.get("motivo") or "").startswith("veto:") or c.get("veredito") == "ACOMPANHAR" and "resultado" in str(c.get("motivo")))


def _api(site: str) -> str:
    return site.rstrip("/") + "/wp-json/wp/v2"


def descobrir_catalogo(cfg: dict, est: dict) -> int:
    """Lê as páginas-índice do portal e confirma, pela API, cada site de órgão estadual que ainda não está no catálogo."""
    ds = cfg["descoberta"]; ign = set(ds["caminhos_ignorados"]); fora = re.compile(ds["fora_do_executivo"], re.I)
    conhecidos = {o["site"].rstrip("/").lower() for o in est["orgaos"].values()}
    slugs = set()
    for pg in ds["paginas_indice"]:
        st, html, _ = _get(pg)
        if st == 200:
            slugs |= {m.group(1) for m in re.finditer(r"https?://(?:www\.)?goias\.gov\.br/([a-z0-9][a-z0-9-]{1,40})/", html)}
        time.sleep(cfg["pausa_entre_requisicoes"])
    novos = 0
    for s in sorted(slugs - ign):
        site = f"https://goias.gov.br/{s}"
        if site.lower() in conhecidos:
            continue
        st, corpo, _ = _get(site + "/wp-json/")
        if st != 200:
            continue
        try:
            nome = json.loads(corpo).get("name") or s
        except Exception:
            continue
        if fora.search(nome):
            continue
        est["orgaos"][f"go-{s}"] = {"id": f"go-{s}", "nome": unescape(nome), "tipo": "órgão estadual (descoberto no portal)", "site": site,
                                    "camada": 1, "descoberto_em": date.today().isoformat()}
        novos += 1
        time.sleep(cfg["pausa_entre_requisicoes"])
    return novos


def camada1(o: dict, cfg: dict) -> None:
    """Onde o órgão publica."""
    onde = []
    st, corpo, _ = _get(_api(o["site"]) + "/posts?per_page=1&_fields=id,date")
    o["wordpress"] = st == 200 and corpo.strip().startswith("[")
    if not o["wordpress"] and "goias.gov.br/" in o["site"]:        # 02/10: endereço suposto errado → tenta os alternativos
        for slug in (cfg.get("slugs_alternativos") or {}).get(o["id"], []):
            alt = f"https://goias.gov.br/{slug}"
            st, corpo, _ = _get(_api(alt) + "/posts?per_page=1&_fields=id,date")
            if st == 200 and corpo.strip().startswith("["):
                o["site_anterior"] = o["site"]; o["site"] = alt; o["wordpress"] = True; break
            time.sleep(cfg["pausa_entre_requisicoes"])
    if o["wordpress"]:
        onde.append("notícias do site (API do portal)")
        for termo in ("edital", "chamamento"):
            st2, c2, _ = _get(_api(o["site"]) + "/pages?per_page=20&_fields=title,link&search=" + urllib.parse.quote(termo))
            if st2 == 200:
                try:
                    for p in json.loads(c2):
                        onde.append(f"página: {limpar(p['title']['rendered'])[:70]} — {p['link']}")
                except Exception:
                    pass
            time.sleep(cfg["pausa_entre_requisicoes"])
    st3, html, _ = _get(o["site"])
    o["site_responde"] = st3
    if st3 == 200:
        for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
            txt = limpar(m.group(2)); href = urllib.parse.urljoin(o["site"] + "/", m.group(1))
            if re.search(r"edita|chamament|sele[cç]|credenciament|pr[eê]mio|fomento|transfer[eê]ncia|parceria|conv[eê]nio|terceiro setor", sem(txt + " " + href)) \
               and len(txt) < 90:
                onde.append(f"link do site: {txt or href} — {href}")
    o["onde_publica"] = list(dict.fromkeys(onde))[:25]
    o["camada"] = 2
    o["camada1_em"] = date.today().isoformat()


def _post(p: dict) -> dict:
    return {"id": p.get("id"), "data": str(p.get("date") or "")[:10], "url": p.get("link"),
            "titulo": limpar((p.get("title") or {}).get("rendered"))[:300], "resumo": limpar((p.get("excerpt") or {}).get("rendered"))[:900]}


def camada2(o: dict, cfg: dict, fim: float) -> bool:
    """Histórico de 5 anos. Devolve True quando terminou (pode continuar na próxima execução)."""
    lex = cfg["lexico"]; desde = (date.today() - timedelta(days=365 * cfg["anos_de_historico"])).isoformat()
    pubs = {str(x["id"]) + "|" + str(x.get("url")): x for x in o.get("_publicacoes") or []}
    feitos = set(o.get("_termos_feitos") or [])
    o.setdefault("volume_por_termo", {})
    if o.get("wordpress"):
        for termo in lex["buscar"]:
            if termo in feitos:
                continue
            if time.time() > fim:
                o["_publicacoes"] = list(pubs.values()); o["_termos_feitos"] = sorted(feitos)
                return False
            for pg in range(1, cfg["paginas_por_termo"] + 1):
                url = (_api(o["site"]) + "/posts?per_page=100&_fields=id,date,link,title,excerpt&after=" + desde + "T00:00:00"
                       + "&search=" + urllib.parse.quote(termo) + f"&page={pg}")
                st, corpo, h = _get(url)
                if st != 200:
                    break
                try:
                    lista = json.loads(corpo)
                except Exception:
                    break
                if pg == 1:
                    o["volume_por_termo"][termo] = int(h.get("X-WP-Total") or h.get("x-wp-total") or len(lista))
                for p in lista:
                    x = _post(p); pubs[str(x["id"]) + "|" + str(x["url"])] = x
                time.sleep(cfg["pausa_entre_requisicoes"])
                if len(lista) < 100 or len(pubs) >= cfg["maximo_publicacoes_por_orgao"]:
                    break
            feitos.add(termo)
    else:                                     # site fora do portal: as páginas de publicação achadas na camada 1
        for linha in [l for l in o.get("onde_publica") or [] if l.startswith("link do site:")][:6]:
            href = linha.rsplit(" — ", 1)[-1]
            st, html, _ = _get(href)
            if st != 200:
                continue
            for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
                txt = limpar(m.group(2))
                if 15 <= len(txt) <= 200 and re.search(r"edita|chamament|sele[cç]|pr[eê]mio|credenciament|inscri", sem(txt)):
                    u = urllib.parse.urljoin(href, m.group(1)); ano = re.search(r"\b(20[12]\d)\b", txt + u)
                    pubs[u] = {"id": sha256(u.encode()).hexdigest()[:10], "data": f"{ano.group(1)}-01-01" if ano else "", "url": u, "titulo": txt, "resumo": ""}
            time.sleep(cfg["pausa_entre_requisicoes"])
    o["_publicacoes"] = list(pubs.values()); o["_termos_feitos"] = sorted(feitos)
    o["camada"] = 3
    return True


def camada3(o: dict, cfg: dict, hoje: date) -> tuple[list[dict], list[dict]]:
    """Classifica tudo; devolve (abertas, do_passado)."""
    lex = cfg["lexico"]; abertas, passadas = [], []
    por_ano, ver = Counter(), Counter()
    for x in o.get("_publicacoes") or []:
        pub = None
        try:
            pub = date.fromisoformat(x["data"]) if x.get("data") else None
        except ValueError:
            pass
        c = classificar(x["titulo"], x["resumo"], pub, hoje, lex)
        ver[c["veredito"]] += 1
        if pub:
            por_ano[str(pub.year)] += 1
        if c["veredito"] == "OPORTUNIDADE":
            r = {**x, **c, "orgao": o["nome"], "orgao_id": o["id"]}
            (abertas if c.get("aberta") else passadas).append(r)
    o["publicacoes_por_ano"] = dict(sorted(por_ano.items())); o["vereditos"] = dict(ver)
    o["oportunidades_historicas"] = len(passadas); o["oportunidades_abertas"] = len(abertas)
    o["exemplos"] = [{"titulo": r["titulo"][:140], "data": r["data"], "url": r["url"], "aberta": bool(r.get("aberta"))}
                     for r in sorted(abertas + passadas, key=lambda z: z["data"], reverse=True)[:8]]
    o["ultima_publicacao_vista"] = max([x["data"] for x in o.get("_publicacoes") or [] if x.get("data")] or [None]) if o.get("_publicacoes") else None
    o["camada"] = 4; o["historico_em"] = hoje.isoformat()
    o.pop("_publicacoes", None); o.pop("_termos_feitos", None)
    return abertas, passadas


def _monitorar_sem_api(o: dict, cfg: dict, hoje: date) -> list[dict]:
    """03/10 (teste do motor 14): site fora do portal (OVG, UEG, Saneago…) não tinha monitoramento nenhum depois do
    histórico. Agora relê as páginas de publicação achadas na camada 1 e trata como novo o link que ainda não foi visto."""
    vistos = set(o.get("links_vistos") or [])
    novos, lidas = [], 0
    for linha in [l for l in o.get("onde_publica") or [] if l.startswith("link do site:")][:6]:
        href = linha.rsplit(" — ", 1)[-1]
        st, html, _ = _get(href)
        if st != 200:
            continue
        lidas += 1
        for m in re.finditer(r"""<a[^>]+href=["']([^"'#]+)["'][^>]*>(.*?)</a>""", html, re.S | re.I):
            txt = limpar(m.group(2)); u = urllib.parse.urljoin(href, m.group(1))
            if 15 <= len(txt) <= 200 and u not in vistos and re.search(r"edita|chamament|sele[cç]|pr[eê]mio|credenciament|inscri", sem(txt)):
                vistos.add(u); novos.append({"id": sha256(u.encode()).hexdigest()[:10], "data": hoje.isoformat(), "url": u, "titulo": txt, "resumo": ""})
        time.sleep(cfg["pausa_entre_requisicoes"])
    primeira = "links_vistos" not in o
    o["links_vistos"] = sorted(vistos)[-500:]
    o["monitorado_em"] = hoje.isoformat(); o["monitoramento_http"] = 200 if lidas else (o.get("site_responde") or 0)
    if primeira:
        return []                 # 1ª passagem só registra o que já existe (o histórico já foi classificado na camada 3)
    out = []
    for x in novos:
        c = classificar(x["titulo"], "", hoje, hoje, cfg["lexico"])
        if c["veredito"] == "OPORTUNIDADE" and c.get("aberta"):
            out.append({**x, **c, "orgao": o["nome"], "orgao_id": o["id"]})
    return out


def camada4(o: dict, cfg: dict, hoje: date) -> list[dict]:
    """Monitoramento: só as publicações novas desde a última vista."""
    if not o.get("wordpress"):
        return _monitorar_sem_api(o, cfg, hoje)
    desde = o.get("ultima_publicacao_vista") or (hoje - timedelta(days=3)).isoformat()
    # 03/10 (teste do motor 14): eram só os 50 primeiros posts — num órgão com mais publicações no período (Saúde,
    # Procon) o resto se perdia e a "última vista" pulava por cima. Agora pagina até o fim (ou marca como cortado).
    lista, st, total_pg = [], 0, int(cfg.get("paginas_monitoramento", 5))
    for pg in range(1, total_pg + 1):
        st, corpo, h = _get(_api(o["site"]) + "/posts?per_page=100&_fields=id,date,link,title,excerpt&orderby=date&order=asc&after="
                            + desde + f"T00:00:00&page={pg}")     # do mais antigo ao mais novo: o corte não perde nada
        if st != 200:
            break
        try:
            parte = [_post(p) for p in json.loads(corpo)]
        except Exception:
            st = -1; break
        lista += parte
        paginas = int(h.get("X-WP-TotalPages") or h.get("x-wp-totalpages") or 1)
        if pg >= paginas or len(parte) < 100:
            break
        time.sleep(cfg["pausa_entre_requisicoes"])
    else:
        o["monitoramento_cortado"] = True
    o["monitorado_em"] = hoje.isoformat(); o["monitoramento_http"] = st
    if st != 200:
        o["monitoramento_falhou_em"] = hoje.isoformat()
        raise RuntimeError(f"monitoramento HTTP {st}")       # vira falha no diagnóstico (antes era silêncio)
    o.pop("monitoramento_falhou_em", None)
    out = []
    for x in lista:
        pub = date.fromisoformat(x["data"]) if x.get("data") else None
        c = classificar(x["titulo"], x["resumo"], pub, hoje, cfg["lexico"])
        if c["veredito"] == "OPORTUNIDADE" and c.get("aberta"):
            out.append({**x, **c, "orgao": o["nome"], "orgao_id": o["id"]})
    if lista:                    # em ordem crescente, avançar até a última lida é seguro mesmo com corte
        o["ultima_publicacao_vista"] = max(x["data"] for x in lista if x.get("data"))
    return out


def _registro(r: dict) -> dict:
    ev = re.sub(r"\s+", " ", f"{r['titulo']} {r.get('resumo') or ''}")[:700]
    return {"id": sha256(f"estgo|{r['url']}".encode()).hexdigest()[:20], "status": "capturada", "titulo": f"{r['orgao']} — {r['titulo']}"[:300],
            "url": r["url"], "fonte_id": MOTOR_ID, "fonte_nome": NOME, "territorio": "GO", "uf": "GO", "nivel": "estadual",
            "tipo_fonte": "site_oficial_estadual", "confianca": "primaria", "forma_divulgacao": "site_oficial", "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data_publicacao": r.get("data") or None, "fim": r.get("prazo"), "prazo_texto": r.get("prazo"), "orgao": r["orgao"],
            "evidencia": ev, "hash_evidencia": sha256(ev.encode()).hexdigest(), "classificacao_ato": {"veredito": r["veredito"], "motivos": [r["motivo"]]},
            "sensor": MOTOR_ID, "forca_lexica": 3}


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None, orcamento: float | None = None) -> dict:
    cfg = _j(CFG, {}); hoje = hoje or date.today()
    est = _j(ESTADO, {}) or {}
    est.setdefault("orgaos", {})
    for s in cfg.get("orgaos_semente") or []:
        est["orgaos"].setdefault(s["id"], {**s, "camada": 1})
    fim = time.time() + float(orcamento or cfg.get("orcamento_segundos_por_execucao", 900))
    diag = {"motor": NOME, "orgaos": len(est["orgaos"]), "descobertos_agora": 0, "camadas_feitas": Counter(), "falhas": [], "paginas_lidas": 0,
            "motivo_zero": None}
    if str(est.get("catalogo_em") or "") < (hoje - timedelta(days=7)).isoformat():   # o catálogo é refeito toda semana
        try:
            diag["descobertos_agora"] = descobrir_catalogo(cfg, est); est["catalogo_em"] = hoje.isoformat()
        except Exception as ex:
            diag["falhas"].append(f"descoberta: {type(ex).__name__}: {ex}"[:160])
    for o in est["orgaos"].values():
        if o.get("camada") == 4 and not o.get("wordpress") and not (o.get("publicacoes_por_ano") or {}) \
           and str(o.get("camada1_em") or "") < (hoje - timedelta(days=cfg.get("refazer_descoberta_dias", 7))).isoformat():
            o["camada"] = 1
    vistos = {}
    for k in sorted(est["orgaos"], key=lambda k: (k.startswith("go-"), k)):
        st_ = est["orgaos"][k]["site"].rstrip("/").lower()
        if st_ in vistos:
            est["orgaos"].pop(k)
        else:
            vistos[st_] = k
    # 03/10 (teste do motor 14): léxico novo → os últimos N dias de cada órgão são relidos UMA vez com ele, e os órgãos sem
    # histórico voltam à camada 1 (endereços alternativos, como goias.gov.br/inovacao da SECTI)
    if est.get("lexico_versao") != cfg["lexico"].get("versao"):
        rev = (hoje - timedelta(days=int(cfg.get("janela_revisao_dias", 60)))).isoformat()
        for o in est["orgaos"].values():
            if o.get("camada") == 4 and o.get("wordpress") and str(o.get("ultima_publicacao_vista") or rev) > rev:
                o["ultima_publicacao_vista"] = rev
            if o.get("camada") == 4 and not o.get("wordpress") and not (o.get("publicacoes_por_ano") or {}):
                o["camada"] = 1
        est["lexico_versao"] = cfg["lexico"].get("versao"); diag["revisao_lexico"] = rev
    abertas, passadas = [], []
    # 1º: monitoramento dos órgãos que já têm histórico (barato) · 2º: os demais, UM POR VEZ, camada a camada
    a_monitorar = [o for o in est["orgaos"].values() if o.get("camada") == 4]
    # quem ficou para trás ontem (tempo ou falha) vai primeiro
    a_monitorar.sort(key=lambda o: (str(o.get("monitorado_em") or "") == hoje.isoformat() and not o.get("monitoramento_cortado"),
                                    str(o.get("monitorado_em") or "")))
    for o in a_monitorar:
        if time.time() > fim:
            break
        o.pop("monitoramento_cortado", None)
        try:
            abertas += camada4(o, cfg, hoje); diag["camadas_feitas"]["4"] += 1
        except Exception as ex:
            diag["falhas"].append(f"{o['id']} monitoramento: {type(ex).__name__}: {ex}"[:140])
    for o in sorted([o for o in est["orgaos"].values() if o.get("camada", 1) < 4], key=lambda z: (not z.get("antigo_motor"), z.get("camada", 1) == 1, z["id"])):
        if time.time() > fim:
            break
        try:
            if o.get("camada", 1) == 1:
                camada1(o, cfg); diag["camadas_feitas"]["1"] += 1
            if o.get("camada") == 2 and time.time() < fim:
                if camada2(o, cfg, fim):
                    diag["camadas_feitas"]["2"] += 1
            if o.get("camada") == 3:
                a, p = camada3(o, cfg, hoje); abertas += a; passadas += p; diag["camadas_feitas"]["3"] += 1
        except Exception as ex:
            diag["falhas"].append(f"{o['id']}: {type(ex).__name__}: {ex}"[:160])
    # o do passado vai para o HISTÓRICO dos livros (alimenta a previsão); o aberto vira achado (e livro, pelo ciclo).
    # O que não puder ser registrado agora (ex.: execução de verificação fora da main) fica PENDENTE e entra na próxima.
    import os
    novos = [{"titulo": f"{r['orgao']} — {r['titulo']}", "url": r["url"], "orgao": r["orgao"], "uf": "GO",
              "prazo": r.get("prazo"), "publicado_em": r.get("data")} for r in passadas + abertas]
    pend = {x["url"]: x for x in (est.get("pendentes_livros") or []) + novos
            if x["titulo"].split(" — ", 1)[-1].strip() and _continua(x["titulo"].split(" — ", 1)[-1], hoje, cfg["lexico"])}
    if os.environ.get("ESTADUAIS_SEM_LIVROS"):
        est["pendentes_livros"] = list(pend.values())
    elif pend:
        try:
            from .livros_regra import registrar_achados
            diag["livros"] = registrar_achados(list(pend.values()), NOME); est["pendentes_livros"] = []
        except Exception as ex:
            est["pendentes_livros"] = list(pend.values()); diag["falhas"].append(f"livros: {type(ex).__name__}: {ex}"[:160])
    diag["pendentes_livros"] = len(est.get("pendentes_livros") or [])
    achados = [_registro(r) for r in {r["url"]: r for r in abertas}.values()]
    diag["camadas_feitas"] = dict(diag["camadas_feitas"])
    diag["paginas_lidas"] = sum(diag["camadas_feitas"].values())
    # cobertura do dia: órgãos monitorados hoje × órgãos que deviam ser; o que faltar vira leitura PARCIAL para o maestro
    devidos = [o for o in est["orgaos"].values() if o.get("camada") == 4]
    faltam = [o["id"] for o in devidos if o.get("monitorado_em") != hoje.isoformat() or o.get("monitoramento_cortado")
              or o.get("monitoramento_falhou_em") == hoje.isoformat()]
    faltam += [o["id"] for o in est["orgaos"].values() if o.get("camada", 1) < 4]          # histórico ainda em construção
    diag["cobertura_orgaos"] = {"devidos": len(devidos), "monitorados_hoje": len(devidos) - len([f for f in faltam if est["orgaos"][f].get("camada") == 4]),
                                "pendentes": faltam[:20]}
    if faltam:
        diag["paginas_nao_lidas"] = len(faltam)
    por_camada = Counter(o.get("camada", 1) for o in est["orgaos"].values())
    diag["orgaos_por_camada"] = {f"camada {k}": v for k, v in sorted(por_camada.items())}
    if not achados:
        diag["motivo_zero"] = (f"{diag['orgaos_por_camada'].get('camada 4', 0)} órgão(s) já com histórico e monitorados; nenhuma seleção aberta nova hoje"
                               if not diag["falhas"] else "falhas: " + "; ".join(diag["falhas"][:2]))
    est["ultima"] = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "data": hoje.isoformat(), "achados": len(achados),
                     "historicas_registradas": len(passadas), "orgaos_por_camada": diag["orgaos_por_camada"], "falhas": diag["falhas"][:10],
                     "cobertura_orgaos": diag["cobertura_orgaos"], **({"paginas_nao_lidas": diag["paginas_nao_lidas"]} if diag.get("paginas_nao_lidas") else {})}
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(est, ensure_ascii=False, indent=1), encoding="utf-8")
    painel()
    saude = [{"url": o.get("site"), "http": o.get("site_responde") or o.get("monitoramento_http")} for o in est["orgaos"].values() if o.get("site_responde") or o.get("monitoramento_http")]
    return {"sensor": MOTOR_ID, "achados": achados, "falhas": [{"erro": f} for f in diag["falhas"]], "saude": saude[:40], "diagnostico": diag,
            "lido_em": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def painel() -> dict:
    est = _j(ESTADO, {}) or {}
    org = sorted(est.get("orgaos", {}).values(), key=lambda o: (-(o.get("oportunidades_historicas") or 0) - 10 * (o.get("oportunidades_abertas") or 0), o["id"]))
    out = {"motor": NOME, "em": (est.get("ultima") or {}).get("em"), "orgaos": [
        {k: o.get(k) for k in ("id", "nome", "tipo", "site", "antigo_motor", "camada", "wordpress", "onde_publica", "publicacoes_por_ano",
                               "vereditos", "oportunidades_historicas", "oportunidades_abertas", "volume_por_termo", "exemplos", "historico_em",
                               "monitorado_em")} for o in org],
           "totais": {"orgaos": len(org), "com_historico": sum(1 for o in org if o.get("camada") == 4),
                      "oportunidades_historicas": sum(o.get("oportunidades_historicas") or 0 for o in org),
                      "oportunidades_abertas": sum(o.get("oportunidades_abertas") or 0 for o in org)}}
    PAINEL.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out["totais"]


if __name__ == "__main__":
    r = ler_motor()
    print(json.dumps(r["diagnostico"], ensure_ascii=False, indent=1)); print(len(r["achados"]), "oportunidade(s) aberta(s)")
