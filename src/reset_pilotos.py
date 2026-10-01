"""RESET DAS MISSÕES DOS PILOTOS (titular, 01/10) — idempotente. Missão com data anterior ao reset já está no histórico
arquivado (estado/pilotos/historico/) e sai do estado de trabalho. Roda a cada pouso: se um voo que começou antes do
reset gravar o estado antigo de volta, a limpeza refaz o reset sem perder nada."""
from __future__ import annotations

import json
import lzma
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESET = "2026-10-01T14:01:07+00:00"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def run() -> dict:
    n_av = n_arq = n_voo = 0
    D = ROOT / "estado/piloto/aprendizados/avaliacoes"
    for f in D.glob("*.json") if D.exists() else []:
        if str(_j(f, {}).get("em") or "") < RESET:
            f.unlink(); n_av += 1
    for f in D.glob("arquivo-*.jsonl.xz") if D.exists() else []:
        try:
            fica = [l for l in lzma.decompress(f.read_bytes()).decode().splitlines() if l.strip() and str((json.loads(l).get("avaliacao") or {}).get("em") or "") >= RESET]
        except Exception:
            fica = []
        f.write_bytes(lzma.compress(("\n".join(fica) + "\n").encode())) if fica else f.unlink(); n_arq += 1
    B = ROOT / "estado/piloto/bordo.json"; b = _j(B, {})
    if b.get("missoes"):
        antes = len(b["missoes"]); b["missoes"] = [m for m in b["missoes"] if str(m.get("inicio") or m.get("fim") or "") >= RESET]
        if len(b["missoes"]) != antes:
            B.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in (ROOT / "estado/interceptador/relatorios").glob("*.json"):
        d = _j(f, {}); vs = d.get("voos") or []
        novos = [v for v in vs if str(v.get("em") or v.get("inicio") or "") >= RESET]
        if len(novos) != len(vs):
            n_voo += len(vs) - len(novos)
            if novos:
                d["voos"] = novos; f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            else:
                f.unlink()
    return {"avaliacoes_antigas_retiradas": n_av, "arquivos_mensais_filtrados": n_arq, "voos_antigos_retirados": n_voo}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
