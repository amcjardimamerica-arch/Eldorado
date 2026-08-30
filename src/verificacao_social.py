from __future__ import annotations

import json
from urllib.error import HTTPError, URLError

from .eldorado import candidates, fetch
from .nucleo import ROOT, append_jsonl, load_json, now_iso, write_json


def run() -> dict:
    cfg = load_json(ROOT / "config/verificacao_social.json")
    policy = load_json(ROOT / "config/fontes.json")["politica"]
    scope = load_json(ROOT / "config/escopo.json")
    report = {"executado_em": now_iso(), "fontes_total": 0, "fontes_ok": 0, "fontes_falha": 0, "pistas": 0, "falhas": []}
    output = ROOT / "dados/oportunidades/pistas_sociais.jsonl"
    known = {}
    if output.exists():
        for line in output.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line); known[item["id"]] = item
    for item in cfg["fontes"]:
        if not item.get("ativa") or item.get("modo") != "pagina_social_publica" or (item.get("uf") and item["uf"] not in scope["ufs_ativas"]):
            continue
        report["fontes_total"] += 1
        source = {**item, "tipo": "rede_social_oficial", "territorio": item.get("municipio") or item.get("uf") or "BR", "confianca": "secundaria", "hosts_links": [item["url"].split("/")[2]]}
        try:
            data, final, _ = fetch(source, policy)
            report["fontes_ok"] += 1
            for found in candidates(source, data, final):
                found.update({"status": "pista_social", "emissor_id": item["emissor_id"], "evidencia_identidade": item["evidencia_identidade"]})
                known[found["id"]] = found
        except (HTTPError, URLError, OSError, ValueError) as exc:
            report["fontes_falha"] += 1; report["falhas"].append({"fonte": item["id"], "erro": type(exc).__name__})
    report["pistas"] = len(known)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n" for x in sorted(known.values(), key=lambda x: x["id"])), encoding="utf-8")
    write_json(ROOT / "estado/verificacao_social.json", report)
    append_jsonl(ROOT / "estado/auditoria.jsonl", {"evento": "verificacao_social", **report})
    return report


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
