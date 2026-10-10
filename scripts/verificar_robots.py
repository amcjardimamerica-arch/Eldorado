"""Verifica pela nuvem (GitHub) o robots.txt e as rotas de dados de sites marcados como 'coleta assistida'.

10/10 (titular, motor 40 — Mapa das OSC): a marcação "o site proíbe robôs" não tinha verificação registrada. Este
script lê o robots.txt, testa se cada caminho é permitido para robôs (RFC 9309, via urllib.robotparser), e — só nos
caminhos PERMITIDOS — abre a página e procura endpoints de dados (API/JSON) citados no código dela. Nada é lido em
caminho proibido. Resultado: estado/indexadores/robots_verificacao.json.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "estado/indexadores/robots_verificacao.json"
UA = "EldoradoBot/1.0 (+https://github.com/amcjardimamerica-arch/Eldorado)"
SITES = {"mapa-osc": ("https://mapaosc.ipea.gov.br", ["/", "/editais", "/editais.html", "/api/", "/api/editais", "/api/edital",
                                                      "/api/osc/", "/visualizar-osc.html", "/dados-abertos", "/arquivos/"])}


def _get(url: str, limite: int = 600_000) -> tuple[int | None, str, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,text/plain,*/*"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.headers.get("content-type", ""), r.read(limite).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, "", ""
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__, ""


def verificar(base: str, caminhos: list[str]) -> dict:
    st, ct, robots = _get(base + "/robots.txt", 100_000)
    rp = urllib.robotparser.RobotFileParser(); rp.parse(robots.splitlines() if st == 200 else [])
    res = {"robots_http": st, "robots_txt": robots[:3000] if st == 200 else None, "caminhos": [], "endpoints_encontrados": []}
    for c in caminhos:
        u = base + c
        livre = rp.can_fetch(UA, u) and rp.can_fetch("*", u)
        item = {"caminho": c, "permitido_para_robos": livre}
        if livre and not c.startswith("/api"):
            s, t, corpo = _get(u)
            item.update({"http": s, "tipo": t[:60], "tamanho": len(corpo), "links_edital": len(re.findall(r"(?i)edital|chamamento|chamada", corpo))})
            for e in sorted(set(re.findall(r"""["'](/?api/[A-Za-z0-9_/\-?=&.{}]+|https?://[^"' ]*/api/[^"' ]+)["']""", corpo)))[:30]:
                res["endpoints_encontrados"].append(e)
        elif livre:
            s, t, corpo = _get(u, 200_000)
            item.update({"http": s, "tipo": t[:60], "tamanho": len(corpo), "json": corpo.lstrip()[:1] in ("[", "{")})
        res["caminhos"].append(item)
    res["endpoints_encontrados"] = sorted(set(res["endpoints_encontrados"]))
    # documentação da API (Swagger/OpenAPI): lista as rotas que falam de edital — só se a documentação for permitida
    docs = [e for e in res["endpoints_encontrados"] if "documentation" in e or "swagger" in e or "api-docs" in e]
    res["api"] = {}
    for d in docs[:2]:
        u = d if d.startswith("http") else base + ("/" + d.lstrip("/"))
        if not rp.can_fetch(UA, u):
            continue
        s1, t1, h = _get(u, 400_000)
        specs = sorted(set(re.findall(r"""["']([^"']*(?:api-docs[^"']*|swagger[^"']*\.json|openapi[^"']*\.json))["']""", h)))[:5]
        res["api"][u] = {"http": s1, "specs": specs}
        for sp in specs:
            su = sp if sp.startswith("http") else base + "/" + sp.lstrip("/")
            if not rp.can_fetch(UA, su):
                continue
            s2, t2, js = _get(su, 3_000_000)
            try:
                paths = list((json.loads(js).get("paths") or {}).keys())
            except Exception:  # noqa: BLE001
                paths = re.findall(r'"(/[^"]+)"\s*:\s*\{\s*"(?:get|post)"', js)
            res["api"][u].setdefault("rotas_total", len(paths))
            res["api"][u]["rotas_edital"] = [x for x in paths if re.search(r"(?i)edital|chamad|oportun", x)][:40]
            res["api"][u]["base_spec"] = su
    permitidos_com_dado = [x for x in res["caminhos"] if x["permitido_para_robos"] and x.get("http") == 200 and (x.get("json") or x.get("links_edital"))]
    res["conclusao"] = ("há caminho PERMITIDO com dados: o motor pode sair da coleta assistida — " + ", ".join(x["caminho"] for x in permitidos_com_dado)
                        if permitidos_com_dado else
                        "robots.txt proíbe os caminhos de dados (ou eles não respondem): segue em coleta assistida / rota indireta"
                        if st == 200 else f"robots.txt não respondeu (HTTP {st}): sem verificação conclusiva")
    return res


def main() -> dict:
    out = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "regra": __doc__.split("\n\n")[1], "sites": {}}
    for sid, (base, caminhos) in SITES.items():
        out["sites"][sid] = verificar(base, caminhos)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: {"robots_http": v["robots_http"], "conclusao": v["conclusao"], "endpoints": v["endpoints_encontrados"][:8]} for k, v in o["sites"].items()}, ensure_ascii=False, indent=1))
    sys.exit(0)
