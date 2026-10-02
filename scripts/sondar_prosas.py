"""Sondagem TEMPORÁRIA do Prosas (02/10/2026): como o site publica os editais (HTML, JavaScript, sitemap, API)."""
import gzip, json, re, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def get(u, t=30):
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip", "Accept-Language": "pt-BR"})
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            b = r.read(15_000_000); b = gzip.decompress(b) if (r.headers.get("Content-Encoding") or "") == "gzip" else b
            return r.status, b.decode("utf-8", "ignore"), r.headers.get("Content-Type"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", None, u
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"[:200], None, u
rel = {}
for u in ["https://prosas.com.br/robots.txt", "https://prosas.com.br/sitemap.xml", "https://prosas.com.br/sitemap_index.xml", "https://prosas.com.br/sitemap",
          "https://prosas.com.br/editais", "https://prosas.com.br/editais?page=2", "https://prosas.com.br/editais?natureza=premio",
          "https://prosas.com.br/editais.json", "https://prosas.com.br/api/v1/editais", "https://prosas.com.br/api/editais", "https://api.prosas.com.br/editais",
          "https://prosas.com.br/editais?status=encerrado", "https://prosas.com.br/editais?encerrados=true", "https://prosas.com.br/editais/encerrados",
          "https://produtos.prosas.com.br/editais"]:
    st, b, ct, fin = get(u); time.sleep(1)
    links = sorted(set(re.findall(r"(?:https?://(?:www\.)?prosas\.com\.br)?(/editais/\d+[^\s\"'<>?#]*)", b)))
    rel[u] = {"status": st, "tipo": ct, "final": fin, "bytes": len(b), "links_edital": len(links), "exemplos": links[:6],
              "sitemaps": re.findall(r"<loc>([^<]+)</loc>", b)[:12] if "xml" in str(ct) or b.lstrip().startswith("<?xml") else [],
              "robots": b[:1500] if u.endswith("robots.txt") else None, "json": b[:600] if "json" in str(ct) else None,
              "scripts_api": sorted(set(re.findall(r"https?://[a-z0-9.-]*prosas[a-z0-9.-]*/[a-z0-9/_-]*api[a-z0-9/_-]*", b)))[:8],
              "next_data": "__NEXT_DATA__" in b, "nuxt": "__NUXT__" in b, "inicio": re.sub(r"\s+", " ", b[:300])}
# a primeira página de edital achada: estrutura (título, datas, prazo, financiador, valor)
amostras = [l for r in rel.values() for l in r["exemplos"]][:3]
for loc in [s for r in rel.values() for s in r["sitemaps"]][:4]:
    st, b, ct, fin = get(loc); time.sleep(1)
    eds = re.findall(r"<loc>([^<]*?/editais/\d+[^<]*)</loc>", b); mods = re.findall(r"<lastmod>([^<]+)</lastmod>", b)
    rel["SITEMAP " + loc] = {"status": st, "bytes": len(b), "editais": len(eds), "exemplos": eds[:5], "lastmod_min": min(mods) if mods else None, "lastmod_max": max(mods) if mods else None}
    amostras += [re.sub(r"^https?://(?:www\.)?prosas\.com\.br", "", e) for e in eds[:3]]
for l in amostras[:3]:
    st, b, ct, fin = get("https://prosas.com.br" + l); time.sleep(1)
    rel["EDITAL " + l] = {"status": st, "bytes": len(b), "titulo": (re.findall(r"<title>(.*?)</title>", b, re.S) or [""])[0][:200],
                          "datas": re.findall(r"\d{2}/\d{2}/\d{4}", b)[:10], "json_ld": "application/ld+json" in b,
                          "trecho": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", b)))[:1500]}
json.dump(rel, open("/tmp/sondagem_prosas.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: v.get(kk) for kk in ("status", "bytes", "links_edital", "editais")} for k, v in rel.items()}, ensure_ascii=False, indent=1))
