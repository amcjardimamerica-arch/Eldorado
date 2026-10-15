"""QUAIS MOTORES TÊM FONTES QUE PROÍBEM ROBÔS (titular, 15/10/2026). Lê o robots.txt de cada domínio de cada motor
pela RFC 9309 (src.executor_skills._ler_robots): 200 → obedece; 4xx → permitido; 5xx → não acessar. Nos portais que
recusam a nuvem, o robots.txt é lido PELA PONTE (bloqueio de rede não é proibição). Grava estado/robots_motores.json."""
from __future__ import annotations

import json
import sys
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
EXTRAS = {"camara-goiania-pl": ["https://suap.camaragyn.go.gov.br/consulta/processos/", "https://www.goiania.go.leg.br/processo-legislativo/pautas-de-sessoes"],
          "do-goiania": ["https://www.goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp?ano=2026", "https://api.queridodiario.org.br/gazettes"],
          "do-goias": ["https://diariooficial.abc.go.gov.br/busca/busca/buscar/query/0/"], "pncp-api": ["https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"]}


def robots(base: str, exige: set):
    from src import executor_skills as X
    host = urlsplit(base).hostname or ""
    if host in exige:
        try:
            from src import ponte_brasil as PB
            if PB.configurada():
                from src.indexadores import ponte
                st, _f, corpo, _h = ponte.buscar(base + "/robots.txt", {"Accept": "text/plain"}, 30, 500_000)
                if st >= 400:
                    return None, f"robots.txt indisponível pela ponte ({st}): permitido"
                rp = urllib.robotparser.RobotFileParser(); rp.parse(corpo.decode("utf-8", "ignore").splitlines())
                return rp, "robots.txt lido pela ponte (200): regras aplicadas"
        except Exception as e:  # noqa: BLE001
            return None, f"robots.txt inacessível pela ponte ({type(e).__name__}): permitido"
    return X._ler_robots(base)


def main() -> dict:
    from src import sensores as S
    exige = set((json.loads((ROOT / "config/sensores.json").read_text(encoding="utf-8")).get("exige_brasil") or {}).get("dominios") or [])
    motores = {}
    for s in S.registro():
        us = [u for u in (s.get("urls") or []) if str(u).startswith("http")]
        if us:
            motores.setdefault(s["id"], {"nome": s.get("nome"), "urls": []})["urls"] += us
    for k, us in EXTRAS.items():
        motores.setdefault(k, {"nome": k, "urls": []})["urls"] += us
    cache, out = {}, {}
    for mid, m in motores.items():
        res = []
        for u in dict.fromkeys(m["urls"]):
            p = urlsplit(u); base = f"{p.scheme}://{p.netloc}"
            if base not in cache:
                cache[base] = robots(base, exige)
            rp, motivo = cache[base]
            ok = True if rp is None else (False if rp is False else rp.can_fetch("EldoradoBot", u))
            res.append({"url": u, "permitido": ok, "robots": motivo})
        out[mid] = {"nome": m["nome"], "bloqueadas": [r for r in res if not r["permitido"]], "total": len(res)}
    resumo = {mid: {"nome": v["nome"], "bloqueadas": len(v["bloqueadas"]), "de": v["total"], "urls": [b["url"] for b in v["bloqueadas"]]}
              for mid, v in out.items() if v["bloqueadas"]}
    sai = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "motores_verificados": len(out),
           "dominios": len(cache), "motores_com_bloqueio": resumo,
           "dominios_proibem": sorted(b for b, (rp, mo) in cache.items() if rp is False or (rp is not None and "regras" in mo and not rp.can_fetch("EldoradoBot", b + "/")))}
    (ROOT / "estado/robots_motores.json").write_text(json.dumps(sai, ensure_ascii=False, indent=1), encoding="utf-8")
    return sai


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("motores_verificados", "dominios")}, ensure_ascii=False), len(r["motores_com_bloqueio"]), "motor(es) com bloqueio")
