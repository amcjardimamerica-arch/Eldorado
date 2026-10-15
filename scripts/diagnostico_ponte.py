"""DIAGNÓSTICO DA PONTE BRASIL (titular, 15/10/2026): a ponte funciona? Para cada portal que hoje passa por ela, compara
a leitura PELA PONTE com a leitura DIRETA da nuvem. Grava estado/ponte/diagnostico.json. Não lê páginas proibidas
por robots (SUAP da Câmara fica de fora)."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
ALVOS = {
    "ALEGO · SPL (proposições)": "https://alegodigital.al.go.leg.br/spl/",
    "ALEGO · portal": "https://portal.al.go.leg.br/noticias",
    "Prefeitura de Goiânia · lista do Diário": "https://www.goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp?ano=2026",
    "Câmara de Goiânia · pautas": "https://www.goiania.go.leg.br/processo-legislativo/pautas-de-sessoes",
    "TJGO · portal": "https://www.tjgo.jus.br/",
    "Diário do Estado de Goiás": "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/2026-10-14.json",
    "Governo de Goiás": "https://www.goias.gov.br/",
    "MPGO": "https://www.mpgo.mp.br/",
}


def direto(u: str) -> dict:
    t0 = time.time()
    try:
        with urlopen(Request(u, headers={"User-Agent": UA, "Accept-Language": "pt-BR"}), timeout=30) as r:
            b = r.read(3_000_000)
            return {"ok": True, "http": r.status, "bytes": len(b), "s": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "http": getattr(e, "code", None), "erro": f"{type(e).__name__}: {str(e)[:120]}", "s": round(time.time() - t0, 1)}


def pela_ponte(u: str) -> dict:
    from src.indexadores import ponte
    t0 = time.time()
    try:
        st, final, corpo, _h = ponte.buscar(u, {"Accept": "text/html,application/json,*/*", "Accept-Language": "pt-BR"}, 40, 3_000_000)
        return {"ok": st < 400, "http": st, "bytes": len(corpo), "s": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "erro": f"{type(e).__name__}: {str(e)[:160]}", "tipo": getattr(e, "tipo", None),
                "http": getattr(e, "status", None), "s": round(time.time() - t0, 1)}


def main() -> dict:
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "segredos": {"ELDORADO_PONTE_URL": bool(os.environ.get("ELDORADO_PONTE_URL")), "ELDORADO_PONTE_CHAVE": bool(os.environ.get("ELDORADO_PONTE_CHAVE"))},
           "alvos": {}}
    for nome, u in ALVOS.items():
        out["alvos"][nome] = {"url": u, "direto": direto(u), "ponte": pela_ponte(u)}
        print(nome, out["alvos"][nome]["direto"].get("ok"), out["alvos"][nome]["ponte"].get("ok"), flush=True)
        time.sleep(1)
    a = out["alvos"].values()
    out["resumo"] = {"ponte_ok": sum(1 for x in a if x["ponte"]["ok"]), "direto_ok": sum(1 for x in a if x["direto"]["ok"]),
                     "so_pela_ponte": [n for n, x in out["alvos"].items() if x["ponte"]["ok"] and not x["direto"]["ok"]],
                     "nenhum": [n for n, x in out["alvos"].items() if not x["ponte"]["ok"] and not x["direto"]["ok"]], "total": len(out["alvos"])}
    (ROOT / "estado/ponte").mkdir(parents=True, exist_ok=True)
    (ROOT / "estado/ponte/diagnostico.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(json.dumps(main()["resumo"], ensure_ascii=False))
