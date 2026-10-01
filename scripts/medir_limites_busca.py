#!/usr/bin/env python3
"""Medição dos limites de busca a partir do servidor do GitHub (01/10): DuckDuckGo (HTML e lite, intervalos de 3, 15
e 30 s, tempo de recuperação), fontes gratuitas sem chave (Google Notícias RSS, Bing Notícias RSS, Mojeek) e o site
da Open Datacenter (produtos)."""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
R = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
Q = ["edital assistência social Goiás 2026", "chamamento público organizações da sociedade civil 2026", "fundo municipal da criança edital 2026",
     "edital cultura Goiânia inscrições", "instituto empresarial edital projetos sociais", "prêmio iniciativas sociais inscrições 2026",
     "edital pessoa idosa OSC 2026", "patrocínio projetos sociais empresa 2026", "edital esporte organizações sociais 2026", "fundação doação projetos sociais Goiás",
     "edital saúde entidades filantrópicas 2026", "chamada pública projetos culturais 2026"]
def get(url, data=None, t=25):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", "Accept": "text/html,application/xml,*/*"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            return r.status, r.read(3_000_000).decode("utf-8", "ignore"), round(time.time() - t0, 1)
    except urllib.error.HTTPError as e:
        return e.code, "", round(time.time() - t0, 1)
    except Exception as e:
        return type(e).__name__, "", round(time.time() - t0, 1)
def ddg(q, modo):
    if modo == "html":
        st, h, s = get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q))
        n = len(re.findall(r'class="result__a"', h))
    elif modo == "html_post":
        st, h, s = get("https://html.duckduckgo.com/html/", data=urllib.parse.urlencode({"q": q}).encode())
        n = len(re.findall(r'class="result__a"', h))
    else:
        st, h, s = get("https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(q))
        n = len(re.findall(r"class=['\"]result-link['\"]", h))
    return {"status": st, "resultados": n, "segundos": s, "desafio": bool(re.search(r"anomaly|captcha|challenge", h, re.I))}
out = {"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "duckduckgo": [], "recuperacao": [], "fontes_sem_chave": [], "open_datacenter": []}
for modo, intervalo, n in (("html", 3, 10), ("pausa", 120, 0), ("lite", 3, 10), ("pausa", 120, 0), ("html_post", 15, 10), ("pausa", 90, 0), ("html", 30, 8)):
    if modo == "pausa":
        time.sleep(intervalo); continue
    serie = []
    for i in range(n):
        r = ddg(Q[i % len(Q)], modo); serie.append(r); time.sleep(intervalo)
    out["duckduckgo"].append({"modo": modo, "intervalo_s": intervalo, "serie": serie})
for _ in range(6):                                    # rajada até bloquear, depois mede a recuperação
    ddg(Q[_], "html")
for espera in (30, 60, 120, 240):
    time.sleep(espera); r = ddg(Q[espera % len(Q)], "html"); out["recuperacao"].append({"apos_s": espera, **r})
fontes = {"google_noticias_rss": "https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
          "bing_noticias_rss": "https://www.bing.com/news/search?q={q}&format=rss&setlang=pt-BR",
          "mojeek": "https://www.mojeek.com/search?q={q}"}
for nome, molde in fontes.items():
    serie = []
    for q in Q[:6]:
        st, h, s = get(molde.format(q=urllib.parse.quote(q)))
        n = len(re.findall(r"<item>", h)) if "rss" in nome else len(re.findall(r'class="ob"|<a class="title"|class="results-standard"', h))
        serie.append({"status": st, "resultados": n, "segundos": s}); time.sleep(3)
    ex = ""
    if "rss" in nome:
        st, h, s = get(molde.format(q=urllib.parse.quote(Q[0])))
        ex = re.findall(r"<title>(.*?)</title>", h)[1:4]
    out["fontes_sem_chave"].append({"fonte": nome, "serie": serie, "exemplos": ex})
for dom in ("https://www.opendatacenter.com.br", "https://opendatacenter.com.br", "https://www.opendc.com.br", "https://www.opendatacenter.com"):
    st, h, s = get(dom)
    if not h:
        out["open_datacenter"].append({"site": dom, "status": st}); continue
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)))
    links = sorted({urllib.parse.urljoin(dom, l) for l in re.findall(r'href="([^"#]+)"', h) if re.search(r"(?i)cloud|nuvem|servidor|vps|colocation|produto|solu|servi|dedicad|ia|gpu|backup|plano|preco|pre%C3%A7o", l)})[:25]
    paginas = []
    for l in links[:10]:
        st2, h2, _ = get(l)
        t2 = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h2)))
        paginas.append({"url": l, "status": st2, "texto": t2[:1800]})
    out["open_datacenter"].append({"site": dom, "status": st, "titulo": (re.findall(r"<title>(.*?)</title>", h, re.I) or [""])[0], "texto": txt[:3000], "links": links, "paginas": paginas})
    break
(R / "biblioteca_alexandria/base/limites_busca_2026-10-01.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")
