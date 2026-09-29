#!/usr/bin/env python3
"""Sondagem das fontes com falha (30/09): código, endereço final, tipo, tamanho e erro exato — sem as regras do coletor."""
import json, sys, time, urllib.request
from pathlib import Path
R = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (compatible; Eldorado-OSC/3.0; +https://github.com/amcjardimamerica-arch/Eldorado)"}
out = []
for f in json.loads((R / "config/_sondagem_fontes_falha.json").read_text(encoding="utf-8")):
    for url in [f["url"], f["url"].replace("://www.", "://") if "://www." in f["url"] else f["url"].replace("://", "://www.", 1)]:
        r = {"id": f["id"], "erro_coletor": f["erro"], "url": url}
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as resp:
                corpo = resp.read(9_000_000)
                r.update({"http": resp.status, "final": resp.geturl(), "tipo": resp.headers.get_content_type(), "bytes": len(corpo)})
        except urllib.error.HTTPError as e:
            r.update({"http": e.code, "erro": "HTTPError", "final": getattr(e, "url", None)})
        except Exception as e:
            r.update({"erro": type(e).__name__, "msg": str(e)[:160]})
        out.append(r); time.sleep(0.5)
(R / "biblioteca_alexandria/base/sondagem_fontes_falha.json").write_text(json.dumps({"em": time.strftime("%Y-%m-%dT%H:%M:%S"), "itens": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "sondagens")
