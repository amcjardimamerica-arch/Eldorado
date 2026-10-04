"""PILOTO GRAVA SÓ O LIVRO EM QUE TRABALHOU (titular, 04/10/2026).

Antes, ao pousar, o Interceptador regenerava o catálogo INTEIRO da Biblioteca e gravava — um voo alterava todos os
livros e podia gravar por cima de atualizações implantadas no meio do caminho. Agora: o fluxo guarda o catálogo da
main (antes de regenerar) e este script devolve esse catálogo trocando SÓ os livros dos alvos deste voo (o próprio livro
ou o livro da oportunidade do mapa). O resto da Biblioteca não é tocado.
Uso: python scripts/gravar_so_o_livro.py <catalogo_da_main.json> [<pasta_relatorios_do_interceptador>] [--janela-min 90]
"""
from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"


def alvos_do_voo(pasta: Path, janela_min: int = 90) -> set[str]:
    desde = (datetime.now(timezone.utc) - timedelta(minutes=janela_min)).isoformat()
    ids = set()
    for f in glob.glob(str(pasta / "*.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for v in d.get("voos") or []:
            if str(v.get("em") or v.get("inicio") or "") >= desde[:19]:
                a = v.get("alvo") or {}
                for k in ("id", "livro", "opressor"):
                    x = a.get(k) if isinstance(a, dict) else (a if k == "id" else None)
                    if x:
                        ids.add(str(x))
    return ids


def livros_dos_alvos(ids: set[str], cat: dict) -> set[str]:
    livros = {x["id"] for x in cat.get("motores") or []}
    out = {i for i in ids if i in livros}
    try:                                               # oportunidade do mapa → o livro dela
        F = json.loads((ROOT / "docs/dados/fluxo_oportunidades.json").read_text(encoding="utf-8"))
        for v in F.get("itens_por_uf", {}).values():
            for it in v:
                if it.get("id") in ids and it.get("opressor") in livros:
                    out.add(it["opressor"])
    except Exception:  # noqa: BLE001
        pass
    return out


def run(base_main: str, pasta: str | None = None, janela_min: int = 90) -> dict:
    main = json.loads(Path(base_main).read_text(encoding="utf-8"))
    novo = json.loads(CAT.read_text(encoding="utf-8"))
    ids = alvos_do_voo(Path(pasta or ROOT / "estado/interceptador/relatorios"), janela_min)
    trocar = livros_dos_alvos(ids, novo)
    por_id = {x["id"]: x for x in novo.get("motores") or []}
    saida = []
    for x in main.get("motores") or []:
        saida.append(por_id.get(x["id"], x) if x["id"] in trocar else x)
    ja = {x["id"] for x in saida}
    saida += [por_id[i] for i in trocar if i not in ja and i in por_id]       # livro criado pelo próprio voo
    main["motores"] = saida
    CAT.write_text(json.dumps(main, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"alvos": sorted(ids), "livros_gravados": sorted(trocar)}


if __name__ == "__main__":
    a = sys.argv
    jm = int(a[a.index("--janela-min") + 1]) if "--janela-min" in a else 90
    pos = [x for x in a[1:] if not x.startswith("--") and not x.isdigit()]
    print(json.dumps(run(pos[0], pos[1] if len(pos) > 1 else None, jm), ensure_ascii=False))
