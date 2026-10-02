"""Linha de comando dos motores indexadores.

  python -m src.indexadores                      importa as capturas assistidas e roda uma rodada (rota da máquina)
  python -m src.indexadores rodada [--motor idx-feeds,idx-apis] [--site farolcultural] [--rota nuvem|ponte] [--forcar]
  python -m src.indexadores importar             só importa entrada_manual/indexadores/*.json
  python -m src.indexadores tudo --delta /tmp/d.json   (nuvem) rodada que guarda o delta …
  python -m src.indexadores aplicar --delta /tmp/d.json … reaplicado sobre o main mais recente antes do push
  python -m src.indexadores status               resumo do painel (docs/dados/indexadores.json)
  python -m src.indexadores ponte-dominios       domínios que a ponte Brasil deve aceitar (para o ponte.php)
"""
from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlsplit

from . import motor as M


def _lista(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()] or None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.indexadores")
    ap.add_argument("acao", nargs="?", default="tudo", choices=["tudo", "rodada", "importar", "aplicar", "status", "ponte-dominios"])
    ap.add_argument("--motor"); ap.add_argument("--site"); ap.add_argument("--rota", choices=["nuvem", "ponte"])
    ap.add_argument("--forcar", action="store_true", help="lê mesmo os sites cuja cadência ainda não venceu")
    ap.add_argument("--delta", help="rodada: grava o delta neste arquivo · aplicar: aplica este delta sobre os arquivos atuais")
    a = ap.parse_args(argv)
    if a.acao == "ponte-dominios":
        # sufixos públicos do Brasil (qualquer site deles pode cair na ponte pela escada de rotas) + todos os hosts do catálogo
        cat = M.catalogo()
        doms = {"gov.br", "jus.br", "leg.br", "mp.br", "def.br"} | set(M.hosts_exige_brasil())
        for s in cat.get("sites") or []:
            for u in [s.get("url"), s.get("pagina")] + list(s.get("listas") or []) + [f"https://{i['host']}/" for i in s.get("instancias") or []]:
                if u:
                    doms.add((urlsplit(u).hostname or "").lower().replace("www.", ""))
        print("\n".join(sorted(d for d in doms if d)))
        return 0
    if a.acao == "status":
        p = M._j(M.PAINEL, {})
        print(json.dumps({"em": p.get("em"), "acervo": p.get("acervo"), "no_fluxo": p.get("no_fluxo"), "ponte": p.get("ponte"),
                          "motores": [{k: m.get(k) for k in ("id", "sites", "ultima_leitura", "indicios_no_fluxo", "com_falha", "escalados")}
                                      for m in p.get("motores") or []]}, ensure_ascii=False, indent=1))
        return 0
    saida = {}
    if a.acao == "aplicar":
        if not a.delta:
            ap.error("aplicar exige --delta <arquivo>")
        saida["aplicado"] = M.aplicar(json.loads(open(a.delta, encoding="utf-8").read()))
        print(json.dumps(saida, ensure_ascii=False, indent=1))
        return 0
    extra = None
    if a.acao in ("tudo", "importar"):
        from .assistida import importar
        imp = importar(gravar=(a.acao == "importar"))
        extra = imp.pop("delta", None)
        saida["importacao"] = imp
    if a.acao in ("tudo", "rodada"):
        saida["rodada"] = M.rodada(motores=_lista(a.motor), sites=_lista(a.site), rota=a.rota, forcar=a.forcar,
                                   extra=extra, delta_em=a.delta)
    print(json.dumps(saida, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
