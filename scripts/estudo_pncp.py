#!/usr/bin/env python3
"""ESTUDO DO MÊS DO MOTOR DO PNCP (titular, 15/10/2026).

Cada compra DISTINTA que o motor do PNCP registrou no período é reclassificada com as regras atuais (portão de captação
para associação + classificador do motor) e cruzada com o que gerou no sistema. Categorias:
  efetiva aberta · efetiva encerrada · ruído (por motivo) — e, à parte, as RELEITURAS (mesma compra recontada) e a
  OCUPAÇÃO INDEVIDA (registro de ruído guardado em arquivos ativos: repositório, livros, certidões, fichas, filas).
Saídas: estado/pncp/estudo_mes.json e docs/relatorios/estudo-pncp-AAAA-MM-DD.md
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import pncp_osc as P  # noqa: E402
from src import vistos as V  # noqa: E402
from src.repositorio_unico import uf_por_municipio  # noqa: E402


def _j(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def item_do_titulo(x: dict, repo: dict) -> dict:
    t = str(x.get("titulo") or "")
    orgao, _, obj = t.partition(" — ")
    r = repo.get(V.chave(x)) or {}
    uf = r.get("uf") or uf_por_municipio(orgao) or None
    mun = None
    mo = re.search(r"(?:MUNICIPIO|PREFEITURA MUNICIPAL|CAMARA MUNICIPAL|FUNDO MUNICIPAL DE [A-Z ]{3,40}?) DE ([A-ZÀ-Ú ]{3,40})", orgao.upper())
    if mo:
        mun = mo.group(1).title()
    esfera = "M" if re.search(r"MUNICIP|PREFEIT|CAMARA MUNICIPAL|CONSORCIO", orgao.upper()) else ("F" if re.search(
        r"MINISTERIO D[AOE] (?!PUBLICO DO ESTADO)|FEDERAL|UNIAO|TRIBUNAL REGIONAL|TRIBUNAL SUPERIOR|COMPANHIA NACIONAL|INSTITUTO FEDERAL", orgao.upper()) else "E")
    return {"titulo": t, "objeto": obj or t, "orgao": orgao, "uf": uf, "municipio": mun, "esfera": esfera,
            "encerramento": (r.get("fim") or x.get("prazo_texto") or None), "url": x.get("url")}


def grupo(motivo: str) -> str:
    m = motivo.lower()
    for k, rx in (("município de outro estado", r"munic[íi]pio de outro estado|fora do territ"), ("licitação/compra", r"licita|compra|fornecimento|preg"),
                  ("contrato de serviço", r"prestar servi|contrato"), ("ILPI/acolhimento fora de GO/capitais", r"ilpi|acolhimento"),
                  ("PNAE", r"pnae|agricultura familiar"), ("pessoa física", r"pessoas f[íi]sicas|jornalis"),
                  ("sem sinal de terceiro setor", r"contrata[çc][ãa]o p[úu]blica comum|nenhum sinal"), ("veto do motor", r".")):
        if re.search(rx, m):
            return k
    return "outro"


def main() -> dict:
    hoje = date.today().isoformat()
    ev = _j(ROOT / "biblioteca_alexandria/livros/especiais/empresas/financiadores/pncp-api/eventos.compacto.json", {})
    linhas = [dict(zip(ev.get("schema") or [], x)) for x in ev.get("linhas") or []]
    regs = (_j(ROOT / "biblioteca_alexandria/livros/_vistas/repositorio_unico.json", {}) or {}).get("registros") or []
    repo = {}
    for r in regs:
        for u in (r.get("url"), r.get("link_oficial")):
            if u:
                repo.setdefault(V.chave({"url": u}), r)
    cert = (__import__("src.livro_arquivo", fromlist=["x"]).ler_arquivo(ROOT / "estado/cartorio/certidoes.json", {}) or {}).get("certidoes") or {}
    cat = (_j(ROOT / "biblioteca_alexandria/fontes/motores.json", {}) or {}).get("motores") or []
    fichas = _j(ROOT / "docs/dados/fichas_oportunidades.json", {}) or {}
    fichas = fichas.get("fichas") if isinstance(fichas, dict) else {}
    livros_por_chave = defaultdict(list)
    for lv in cat:
        for u in (lv.get("url"), lv.get("fonte"), lv.get("site_oficial")):
            if u and "pncp" in str(u):
                livros_por_chave[V.chave({"url": u})].append(lv.get("id"))
    out, cat_c, ruido_c, ocupa = [], Counter(), Counter(), Counter()
    for x in linhas:
        m = item_do_titulo(x, repo)
        c = P.classificar_item(m, date.today(), P.TODAS_UFS)
        k = V.chave(x)
        r = repo.get(k)
        if c["veredito"] == "OPORTUNIDADE":
            fim = str(m.get("encerramento") or "")[:10]
            categoria = "efetiva encerrada" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) and fim < hoje else "efetiva aberta"
        else:
            categoria = "ruído"; ruido_c[grupo(c["motivos"][0] if c.get("motivos") else "")] += 1
        cat_c[categoria] += 1
        lugares = []
        if r:
            lugares.append(f"repositório ({r.get('estado')})")
            if r.get("id") in fichas:
                lugares.append("ficha")
            if any(kk.endswith(":" + str(r.get("id"))) for kk in cert):
                lugares.append("certidão")
        if livros_por_chave.get(k):
            lugares.append(f"livro ({len(livros_por_chave[k])})")
        if categoria == "ruído":
            for lg in lugares:
                ocupa[lg.split(" (")[0]] += 1
        out.append({"chave": k, "titulo": m["titulo"][:200], "uf": m["uf"], "categoria": categoria,
                    "motivo": (c.get("motivos") or [""])[0][:200], "onde_esta": lugares, "coletado_em": x.get("coletado_em")})
    est = _j(ROOT / "estado/pncp_osc.json", {})
    H = est.get("historico") or {}
    soma = sum(int(v.get("OPORTUNIDADE") or 0) for v in H.values())
    lidos = sum(int(v.get("itens") or 0) for v in H.values())
    res = {"em": hoje, "periodo": [min(H) if H else None, max(H) if H else None], "dias": len(H),
           "itens_lidos_no_pncp": lidos, "marcadas_oportunidade_somando_releituras": soma, "compras_distintas": len(linhas),
           "releituras": max(0, soma - len(linhas)), "categorias": dict(cat_c), "ruido_por_motivo": dict(ruido_c.most_common()),
           "ruido_ocupando_espaco": dict(ocupa), "itens": out}
    d = ROOT / "estado/pncp"; d.mkdir(parents=True, exist_ok=True)
    (d / "estudo_mes.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: v for k, v in res.items() if k != "itens"}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=1))
