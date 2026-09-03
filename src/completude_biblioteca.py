"""Biblioteca de Alexandria · requisitos, condições e valores de cada edital.

Determinação do titular: em cada pasta de edital anterior devem constar os
requisitos, condições e valores; onde já existir, conferir a completude dos
11 itens — Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor,
Órgão/financiador, Território, Esfera, Requisitos, Anexos e Destinação — e
catalogar os SITES históricos desses editais para compor o motor de busca.
Foco em Goiás e Goiânia, sem deixar nenhum edital de fora.

Saídas:
  · em cada registro do banco e em cada pasta existente:
    `requisitos_condicoes_valores.json` com os 11 itens (comprovado / lacuna)
  · `biblioteca_alexandria/fontes/sites_historicos.json` — domínios e páginas
    de onde os editais vieram, com contagem, UF e áreas, priorizando GO
  · relatório de completude por item e por UF

Regra: item não comprovado é declarado como lacuna, nunca preenchido.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from urllib.parse import urlsplit

from .biblioteca import OPORTUNIDADES
from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "biblioteca_alexandria/fontes"
RELATORIO = ROOT / "biblioteca_alexandria/historico/completude_11_itens.json"

# 12 itens: os 11 originais + Área de atuação (educação, esporte, cultura…)
ITENS = ("Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor",
         "Órgão / financiador", "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação")

_ANEXO = re.compile(r"\banexos?\b|\bmodelos?\b|\bformul[áa]rios?\b", re.I)
_OBJETO = re.compile(r"\bobjeto\b|\bfinalidade\b|\bdestina\w*\s+a\b|\bvisa\b", re.I)


def _area_do_edital(ficha: dict, texto: str) -> str | None:
    """Área de atuação canônica (educação, esporte, cultura…). 'outros' não comprova."""
    try:
        from .dashboard_dados import area_canonica, inferir_area, AREAS
        a = area_canonica(ficha.get("area")) if ficha.get("area") else "outros"
        if a == "outros":
            a = inferir_area(texto)
        return AREAS.get(a, {}).get("rotulo") if a != "outros" else None
    except Exception:
        return None


def onze_itens(ficha: dict, parecer: dict | None = None) -> dict:
    """Os 11 itens de análise sobre uma ficha histórica; lacuna declarada."""
    texto = " ".join(str(ficha.get(c) or "") for c in ("titulo", "evidencia"))
    marcos = {m.get("tipo"): m for m in (ficha.get("marcos") or [])}
    dest = ficha.get("destinacao") or {}
    itens = [
        ("Objeto", (re.search(r"objeto[^.]{0,200}", texto, re.I) or [None])[0]
         if _OBJETO.search(texto) else None),
        ("Prazo de inscrição",
         (f'{ficha.get("inicio") or "?"} a {ficha["fim"]}' if ficha.get("fim") else None)),
        ("Resultado", (marcos.get("resultado_preliminar") or marcos.get("resultado_final") or {}).get("data")),
        ("Prazo de recurso", (marcos.get("recurso") or {}).get("data")),
        ("Valor", (ficha.get("valores_citados") or [None])[0]),
        ("Órgão / financiador", ficha.get("financiador")),
        ("Território", ficha.get("uf") or ficha.get("territorio")),
        ("Esfera", ficha.get("nivel") if ficha.get("nivel") in ("federal", "estadual", "municipal") else None),
        ("Requisitos", ", ".join(ficha.get("exigencias_detectadas") or []) or None),
        ("Anexos", "menciona anexos/modelos" if _ANEXO.search(texto) else None),
        ("Destinação", dest.get("motivo") if dest.get("elegivel") is not None else None),
        ("Área de atuação", _area_do_edital(ficha, texto)),
    ]
    saida = []
    for nome, valor in itens:
        saida.append({"item": nome, "valor": (str(valor)[:200] if valor else None),
                      "comprovado": bool(valor),
                      "lacuna": None if valor else f"{nome.lower()} não consta da evidência capturada"})
    comp = sum(1 for s in saida if s["comprovado"])
    return {"itens": saida, "comprovados": comp, "total": len(saida),
            "completude_pct": round(comp / len(saida) * 100),
            "conferido_em": now_iso(),
            "nota": "requisitos, condições e valores conforme a evidência; lacuna nunca é preenchida"}


def _dominio(url: str | None) -> str | None:
    try:
        h = urlsplit(url or "").hostname
        return h.lower() if h else None
    except Exception:
        return None


def run(limite: int | None = None) -> dict:
    from .banco import conectar
    con = conectar()
    with con:
        con.execute("CREATE TABLE IF NOT EXISTS itens11 (chave TEXT, ano TEXT, id TEXT, "
                    "comprovados INTEGER, total INTEGER, detalhe TEXT, PRIMARY KEY (chave, ano, id))")
    rows = con.execute("SELECT chave, ano, id, ficha, parecer FROM historico").fetchall()
    if limite:
        rows = rows[:limite]
    por_item: Counter = Counter()
    por_uf: dict[str, Counter] = defaultdict(Counter)
    sites: dict[str, dict] = {}
    paginas: dict[str, dict] = {}
    n = 0
    with con:
        for chave, ano, cid, fj, pj in rows:
            ficha = json.loads(fj); parecer = json.loads(pj or "{}")
            r = onze_itens(ficha, parecer)
            n += 1
            for it in r["itens"]:
                if it["comprovado"]:
                    por_item[it["item"]] += 1
            uf = ficha.get("uf") or "—"
            por_uf[uf]["editais"] += 1
            por_uf[uf]["comprovados"] += r["comprovados"]
            con.execute("INSERT OR REPLACE INTO itens11 VALUES (?,?,?,?,?,?)",
                        (chave, ano, cid, r["comprovados"], r["total"],
                         json.dumps(r, ensure_ascii=False)))
            ficha["requisitos_condicoes_valores"] = r
            con.execute("UPDATE historico SET ficha=? WHERE chave=? AND ano=? AND id=?",
                        (json.dumps(ficha, ensure_ascii=False), chave, ano, cid))
            pasta = OPORTUNIDADES / chave / ano
            if (pasta / "ficha.json").exists():
                write_json(pasta / "requisitos_condicoes_valores.json", r)
            # catálogo de sites históricos (motor de busca)
            dom = _dominio(ficha.get("url"))
            if dom:
                s = sites.setdefault(dom, {"dominio": dom, "editais": 0, "ufs": Counter(),
                                           "areas": Counter(), "anos": set(), "exemplo": ficha.get("url")})
                s["editais"] += 1; s["ufs"][uf] += 1
                s["areas"][ficha.get("area") or "outros"] += 1
                if ficha.get("data_publicacao"):
                    s["anos"].add(ficha["data_publicacao"][:4])
                pg = paginas.setdefault(ficha["url"], {"url": ficha["url"], "dominio": dom,
                                                        "editais": 0, "uf": uf})
                pg["editais"] += 1
    con.close()

    lista_sites = sorted(
        [{"dominio": s["dominio"], "editais": s["editais"],
          "ufs": dict(s["ufs"].most_common(5)), "areas": dict(s["areas"].most_common(5)),
          "anos": sorted(s["anos"]), "exemplo": s["exemplo"],
          "goias": s["ufs"].get("GO", 0) > 0,
          "prioridade": ("goias" if s["ufs"].get("GO", 0) > 0 else "nacional")}
         for s in sites.values()],
        key=lambda s: (not s["goias"], -s["editais"]))
    SAIDA.mkdir(parents=True, exist_ok=True)
    write_json(SAIDA / "sites_historicos.json", {
        "gerado_em": now_iso(), "dominios": len(lista_sites),
        "paginas": len(paginas), "goias": sum(1 for s in lista_sites if s["goias"]),
        "sites": lista_sites,
        "paginas_goias": sorted([p for p in paginas.values() if p["uf"] == "GO"],
                                key=lambda p: -p["editais"])[:300],
        "nota": "domínios e páginas de onde os editais históricos vieram; entram no motor de busca ativa"})
    relatorio = {
        "gerado_em": now_iso(), "editais_conferidos": n,
        "completude_por_item": {k: {"comprovados": v, "pct": round(v / n * 100, 1) if n else 0}
                                for k, v in ((i, por_item.get(i, 0)) for i in ITENS)},
        "por_uf": {uf: {"editais": c["editais"],
                        "media_itens_comprovados": round(c["comprovados"] / c["editais"], 2)}
                   for uf, c in sorted(por_uf.items(), key=lambda x: -x[1]["editais"])},
        "sites_historicos": len(lista_sites),
        "nota": ("a evidência é a ementa do diário: itens como Resultado, Recurso e Anexos "
                 "só se comprovam com o edital integral — é isso que a campanha de "
                 "completude e a busca ativa perseguem"),
    }
    RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    write_json(RELATORIO, relatorio)
    return relatorio


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2)[:2200])
