"""TESTE DA PONTE HOSTGATOR (titular, 03/10/2026) — roda no GitHub, com os segredos ELDORADO_PONTE_URL e ELDORADO_PONTE_CHAVE.

Fase 1 — página por página: cada endereço que recusa a nuvem é pedido DIRETO (esperado: recusa) e PELA PONTE
(esperado: 200), com código, tamanho, título e tempo.
Fase 2 — os motores de verdade: Câmara de Goiânia (04), TJ-GO (07) e Prefeituras (13), um por vez, com o número de
pedidos que passaram pela ponte.
O relatório NUNCA mostra o endereço nem a chave da ponte. Saída: docs/relatorios/teste-ponte/AAAA-MM-DD.{md,json}
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PASTA = ROOT / "docs/relatorios/teste-ponte"
UA = "Mozilla/5.0 (compatible; EldoradoBot/1.0)"
_SEGREDOS = [v for v in (os.environ.get("ELDORADO_PONTE_URL"), os.environ.get("ELDORADO_PONTE_CHAVE")) if v]


def limpo(t) -> str:
    t = str(t or "")
    for s in _SEGREDOS:
        t = t.replace(s, "[ponte]")
    return re.sub(r"https?://[^\s'\"]*ponte\.php[^\s'\"]*", "[ponte]", t)[:300]


def paginas() -> list[tuple[str, str]]:
    P = json.loads((ROOT / "config/prefeituras_25_go.json").read_text(encoding="utf-8"))
    cid = next(v for v in P.values() if isinstance(v, list) and v and isinstance(v[0], dict))
    pref = [(f"13 Prefeituras — {c['municipio']}", c["site"]) for c in cid if c.get("site") and c["municipio"] in
            ("Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Catalão", "Senador Canedo")]
    return [("04 Câmara de Goiânia — SUAP", "https://suap.camaragyn.go.gov.br/"),
            ("04 Câmara de Goiânia — portal", "https://www.goiania.go.leg.br/"),
            ("07 TJ-GO — RSS da Agência de Notícias", "https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss")] + pref


def titulo(corpo: bytes) -> str:
    t = corpo[:300000].decode("utf-8", "ignore")
    m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:90] if m else ("RSS" if "<rss" in t[:2000] else "")


def direto(url: str) -> dict:
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20) as r:
            b = r.read(400000)
            return {"status": r.status, "bytes": len(b), "segundos": round(time.monotonic() - t0, 1)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "segundos": round(time.monotonic() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "erro": type(e).__name__, "segundos": round(time.monotonic() - t0, 1)}


def pela_ponte(url: str) -> dict:
    from src import ponte_brasil as PB
    t0 = time.monotonic()
    try:
        st, final, corpo, hdr = PB.abrir(url, timeout=60)
        return {"status": st, "bytes": len(corpo), "titulo": titulo(corpo), "final_mesmo_site": (final or url).split("/")[2] == url.split("/")[2],
                "segundos": round(time.monotonic() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "erro": f"{type(e).__name__}: {limpo(e)}", "segundos": round(time.monotonic() - t0, 1)}


MOTOR = r'''
import json, sys
from src.sensores import registro, ler
from src import ponte_brasil as PB
mid = sys.argv[1]
s = next((x for x in registro() if x["id"] in (mid, "plat-" + mid)), None)
r = ler(s) if s else {"achados": [], "falhas": [{"causa": "não encontrado no registro"}]}
d = r.get("diagnostico") or {}
print(json.dumps({"sensor": (s or {}).get("id"), "achados": len(r.get("achados") or []), "falhas": len(r.get("falhas") or []),
                  "falhas_exemplo": [str(f.get("causa") or f.get("erro"))[:140] for f in (r.get("falhas") or [])[:3]],
                  "paginas": d.get("paginas_lidas"), "exige_brasil_pulado": bool(r.get("pulado_exige_brasil")),
                  "ponte": dict(PB.USO), "motivo_zero": str(d.get("motivo_zero") or "")[:200]}, ensure_ascii=False))
'''


def run() -> dict:
    from src import ponte_brasil as PB
    PASTA.mkdir(parents=True, exist_ok=True)
    dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "na_nuvem": PB.na_nuvem(), "ponte_configurada": PB.configurada(),
           "paginas": [], "motores": []}
    for nome, url in paginas():
        r = {"nome": nome, "url": url, "direto": direto(url), "ponte": pela_ponte(url)}
        out["paginas"].append(r); print(f"{nome}: direto {r['direto'].get('status')} · ponte {r['ponte'].get('status')} {r['ponte'].get('erro') or ''}", flush=True)
        time.sleep(1)
    for mid in ("camara-goiania-pl", "judiciario-tjgo", "prefeituras-50-go"):
        t0 = time.monotonic()
        try:
            p = subprocess.run([sys.executable, "-c", MOTOR, mid], cwd=ROOT, capture_output=True, text=True, timeout=900)
            res = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else {"erro": limpo(p.stderr[-300:])}
        except subprocess.TimeoutExpired:
            res = {"erro": "estourou 15 minutos"}
        except Exception as e:  # noqa: BLE001
            res = {"erro": f"{type(e).__name__}: {limpo(e)}"}
        res["segundos"] = round(time.monotonic() - t0)
        out["motores"].append({"motor": mid, **res}); print(f"motor {mid}: {limpo(res)}", flush=True)
    ok = sum(1 for p in out["paginas"] if p["ponte"].get("status") == 200)
    out["veredito"] = (f"a ponte funciona: {ok} de {len(out['paginas'])} páginas abriram pela ponte" if ok else
                       "a ponte NÃO respondeu" if out["ponte_configurada"] else "a ponte não está configurada nesta execução")
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    for seg in _SEGREDOS:
        txt = txt.replace(seg, "[ponte]")
    (PASTA / f"{dia}.json").write_text(txt, encoding="utf-8")
    L = [f"# Teste da ponte Hostgator — {dia}", "", f"**Veredito:** {out['veredito']}", "", f"Rodou na nuvem: {out['na_nuvem']} · ponte configurada: {out['ponte_configurada']}", "",
         "## Página por página", "", "| página | direto da nuvem | pela ponte | título lido pela ponte | tempo |", "|---|---|---|---|---|"]
    for p in out["paginas"]:
        L.append(f"| {p['nome']} | {p['direto'].get('status') or p['direto'].get('erro')} | {p['ponte'].get('status') or ''} {limpo(p['ponte'].get('erro') or '')} | {p['ponte'].get('titulo') or ''} | {p['ponte'].get('segundos')} s |")
    L += ["", "## Os motores", "", "| motor | achados | falhas | pedidos pela ponte (ok/falhas) | tempo |", "|---|---|---|---|---|"]
    for m in out["motores"]:
        u = m.get("ponte") or {}
        L.append(f"| {m['motor']} | {m.get('achados', '—')} | {m.get('falhas', m.get('erro', ''))} | {u.get('ok', 0)}/{u.get('falhas', 0)} de {u.get('pedidos', 0)} | {m.get('segundos')} s |")
    (PASTA / f"{dia}.md").write_text(limpo("\n".join(L)) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    print(run()["veredito"])
