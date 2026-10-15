#!/usr/bin/env python3
"""AMOSTRA DE VALIDAÇÃO (titular, 15/10/2026) — 20 oportunidades abertas sorteadas para o Claude validar lendo os
documentos, item por item, contra o que o Eldorado decidiu. Sorteio reprodutível (semente = data).

Para cada oportunidade guarda: o que o sistema decidiu (estado, veredito, prazo, link de acesso, link oficial,
curadoria, os 12 itens e a certidão do Cartório) e o TEXTO dos documentos — link de acesso e link oficial — lidos
com a mesma rede e o mesmo leitor do Cartório. Saída: estado/amostra_validacao/AAAA-MM-DD.json.gz

    python scripts/amostra_validacao.py [quantidade]
"""
from __future__ import annotations

import gzip
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def ler(rede, url: str) -> dict:
    from src import cartorio_leitura as L
    if not url:
        return {"ok": False, "motivo": "sem link"}
    raw, tipo, err = rede.get(url)
    if err or not raw:
        return {"ok": False, "motivo": err or "vazio", "url": url}
    lido = L.paginas(raw, tipo, 40)
    pgs = lido.get("paginas") or []
    tot, out = 0, []
    for p in pgs:                                       # até 60 mil caracteres por documento
        if tot > 60000:
            break
        out.append(p[:60000 - tot]); tot += len(out[-1])
    return {"ok": bool(lido.get("ok")), "motivo": lido.get("motivo"), "tipo": lido.get("tipo"), "url": url, "paginas": out}


def main(n: int = 20) -> dict:
    from src.cartorio import Rede
    regs = (_j(ROOT / "dados/oportunidades/repositorio_unico.json", {}) or {}).get("registros") or []
    ab = [r for r in regs if not r.get("arquivada") and r.get("estado") not in ("arquivada", "encerrada", "descartada", "fechada") and r.get("url")]
    from datetime import datetime, timezone
    semente = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")      # 15/10: amostra nova a cada análise
    rnd = random.Random(semente)
    amostra = rnd.sample(ab, min(n, len(ab)))
    cur = {x.get("id"): x for x in (_j(ROOT / "estado/curadoria_links.json", {}) or {}).get("itens") or []}
    certs = (_j(ROOT / "estado/cartorio/certidoes.json", {}) or {}).get("certidoes") or {}
    por_id = {str(k).split(":", 1)[-1]: c for k, c in certs.items()}
    rede = Rede(pausa=0.5)
    out = []
    for r in amostra:
        c = por_id.get(r["id"]) or next((por_id[i] for i in (r.get("ids_origem") or []) if i in por_id), None)
        cu = cur.get(r["id"]) or {}
        oficial = (c or {}).get("link_oficial") or r.get("link_oficial") or cu.get("link_oficial_proposto")
        reg = {"id": r["id"], "sistema": {k: r.get(k) for k in ("titulo", "orgao", "uf", "fim", "estado", "motivo_estado", "url", "link_oficial", "origem",
                                                                 "nota_rede", "pronta_para_farol", "livro", "itens", "faltam")},
               "curadoria": {k: cu.get(k) for k in ("curadoria", "classe_do_link_oficial", "falham", "link_oficial_proposto", "trecho")},
               "certidao": {k: (c or {}).get(k) for k in ("link_oficial", "leitura", "ainda_faltam", "itens", "dispensas", "em")} if c else None,
               "doc_acesso": ler(rede, r.get("url")),
               "doc_oficial": ler(rede, oficial) if oficial and oficial != r.get("url") else {"igual_ao_acesso": bool(oficial), "ok": False}}
        out.append(reg)
        print(f"{len(out):2d} {r['id']} acesso={'ok' if reg['doc_acesso'].get('ok') else reg['doc_acesso'].get('motivo')} "
              f"oficial={'ok' if reg['doc_oficial'].get('ok') else reg['doc_oficial'].get('motivo', '—')}", flush=True)
    p = ROOT / f"estado/amostra_validacao/{semente.replace(':', '')}.json.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        json.dump({"data": date.today().isoformat(), "semente": semente, "quantidade": len(out), "itens": out}, fh, ensure_ascii=False)
    return {"amostra": len(out), "arquivo": str(p)}


if __name__ == "__main__":
    print(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20))
