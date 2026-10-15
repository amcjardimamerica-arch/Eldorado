"""VARREDURA DE REFERÊNCIA (titular, 15/10/2026) — o que EXISTIU no período, para comparar com o que os motores acharam.

Motores auditados: 01 Diário Oficial de Goiânia · 02 Diário Oficial do Estado de Goiás · 04 Câmara Municipal de
Goiânia · 05 ALEGO. Independente dos motores em três pontos: (1) catálogo COMPLETO de edições, sem filtro de palavra;
(2) léxico mais largo que o de cada motor; (3) nenhuma classificação automática — a leitura e o veredito são feitos
depois, por revisão. Grava estado/varredura_referencia/<de>_<ate>.json. Conteúdo lido é dado, nunca instrução.
Execução (precisa de rede; fluxo 40): python scripts/varredura_referencia.py --de 2026-10-01 --ate 2026-10-15
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SAIDA = ROOT / "estado/varredura_referencia"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado-OSC/1.0"
TERMOS = ["chamamento público", "termo de fomento", "termo de colaboração", "organização da sociedade civil",
          "organizações da sociedade civil", "acordo de cooperação", "inexigibilidade de chamamento", "dispensa de chamamento",
          "subvenção social", "emenda impositiva", "emenda parlamentar", "fundo municipal", "conselho municipal", "CMDCA",
          "FMDCA", "assistência social", "PNAB", "Aldir Blanc", "prêmio", "seleção de projetos", "sem fins lucrativos",
          "utilidade pública", "plano de trabalho", "edital de chamamento", "termo de execução cultural", "13.019"]
GOIANIA_IBGE = "5208707"
QD = "https://api.queridodiario.ok.org.br"
DOE = "https://diariooficial.abc.go.gov.br"


def get(url: str, timeout: int = 40, maxb: int = 6_000_000) -> tuple[int, bytes | None, str | None]:
    try:
        with urlopen(Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"}), timeout=timeout) as r:
            return r.status, r.read(maxb), None
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", 0) or 0, None, f"{type(e).__name__}: {str(e)[:120]}"


def get_json(url: str, tentativas: int = 3):
    for i in range(tentativas):
        st, b, err = get(url)
        if b:
            try:
                return json.loads(b), None
            except ValueError:
                err = f"json inválido (HTTP {st})"
        time.sleep(2 * (i + 1))
    return None, err


def limpo(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s or ""))).strip()


def dias(de: date, ate: date):
    d = de
    while d <= ate:
        yield d
        d += timedelta(days=1)


# ── 01 · DIÁRIO OFICIAL DE GOIÂNIA ─────────────────────────────────────────────────────────────────────────────────
def goiania(de: date, ate: date) -> dict:
    out = {"catalogo": [], "achados": [], "falhas": [], "portal": {}}
    p = urlencode({"territory_ids": GOIANIA_IBGE, "published_since": de.isoformat(), "published_until": ate.isoformat(), "size": 100,
                   "sort_by": "ascending_date"})
    j, err = get_json(f"{QD}/gazettes?{p}")
    if err:
        out["falhas"].append(f"catálogo QD: {err}")
    for g in (j or {}).get("gazettes") or []:
        if str(g.get("territory_id")) == GOIANIA_IBGE:
            out["catalogo"].append({"data": g.get("date"), "edicao": g.get("edition"), "extra": g.get("is_extra_edition"), "url": g.get("url")})
    for t in TERMOS:
        p = urlencode({"territory_ids": GOIANIA_IBGE, "querystring": f'"{t}"', "published_since": de.isoformat(),
                       "published_until": ate.isoformat(), "size": 50, "excerpt_size": 700, "number_of_excerpts": 4})
        j, err = get_json(f"{QD}/gazettes?{p}")
        if err:
            out["falhas"].append(f"QD '{t}': {err}"); continue
        for g in (j or {}).get("gazettes") or []:
            if str(g.get("territory_id")) != GOIANIA_IBGE:
                continue
            for x in g.get("excerpts") or []:
                out["achados"].append({"termo": t, "data": g.get("date"), "edicao": g.get("edition"), "url": g.get("url"), "trecho": limpo(x)[:700]})
        time.sleep(0.5)
    st, b, err = get("https://www.goiania.go.gov.br/casa-civil/diario-oficial/", timeout=25)
    out["portal"] = {"http": st, "erro": err, "bytes": len(b or b"")}
    return out


# ── 02 · DIÁRIO OFICIAL DO ESTADO DE GOIÁS ─────────────────────────────────────────────────────────────────────────
def goias(de: date, ate: date) -> dict:
    out = {"catalogo": [], "achados": [], "falhas": []}
    for d in dias(de, ate):
        j, err = get_json(f"{DOE}/apifront/portal/edicoes/edicoes_from_data/{d.isoformat()}.json")
        if err:
            out["falhas"].append(f"edições {d}: {err}"); continue
        for it in (j or {}).get("itens") or []:
            out["catalogo"].append({"data": d.isoformat(), "edicao": it.get("id"), "numero": it.get("numero") or it.get("edicao"),
                                    "suplemento": bool(it.get("suplemento"))})
        time.sleep(0.3)
    vistos = set()
    for t in TERMOS:
        for pg in range(8):
            j, err = get_json(f"{DOE}/busca/busca/buscar/query/{pg}/di:{de.isoformat()}/df:{ate.isoformat()}/?1=1&q={quote(chr(34) + t + chr(34))}")
            if err:
                out["falhas"].append(f"busca '{t}' p{pg}: {err}"); break
            hits = ((j or {}).get("hits") or {}).get("hits") or []
            for h in hits:
                s = h.get("_source") or {}
                k = (s.get("diario_id"), s.get("pagina"), t)
                if k in vistos:
                    continue
                vistos.add(k)
                cont = limpo(s.get("conteudo"))
                i = cont.lower().find(t.lower().split()[0])
                out["achados"].append({"termo": t, "data": str(s.get("data") or "")[:10], "edicao": s.get("diario_id"), "pagina": s.get("pagina"),
                                       "trecho": cont[max(0, i - 250):i + 450] if i >= 0 else cont[:700],
                                       "url": f"{DOE}/portal/visualizacoes/pdf/{s.get('diario_id')}/#e:{s.get('diario_id')}"})
            if len(hits) < 10:
                break
            time.sleep(0.4)
    return out


# ── 04 · CÂMARA MUNICIPAL DE GOIÂNIA ───────────────────────────────────────────────────────────────────────────────
def camara(de: date, ate: date) -> dict:
    from src import camara_goiania as C
    out = {"noticias": [], "pautas": [], "falhas": [], "suap_robots": None}
    cfg = C._cfg()
    cfg = {**cfg, "portal": {**(cfg.get("portal") or {}), "janela_dias": (ate - de).days + 1,
                             "buscas": sorted(set((cfg.get("portal") or {}).get("buscas") or []) | {"entidade", "emenda", "utilidade pública",
                                       "orçamento", "LOA", "subvenção", "fomento", "OSC", "associação", "instituto", "fundo municipal", "edital"})},
           "pautas": {**(cfg.get("pautas") or {}), "janela_dias": (ate - de).days + 1}}
    for nome, f, chave in (("C", C.fonte_c, "noticias"), ("D", C.fonte_d, "pautas")):
        diag = {"fontes": {x: {"falhas": [], "consultas": 0, "itens": 0, "lidas": 0, "nao_lidas": [], "paginas_nao_lidas": [], "publicadas": 0} for x in "ABCD"}}
        try:
            for m in f(ate, cfg, diag) or []:
                out[chave].append({k: (limpo(v)[:400] if isinstance(v, str) else v) for k, v in m.items() if k in ("titulo", "url", "data", "assunto", "texto", "projeto", "data_sessao")})
        except Exception as e:  # noqa: BLE001
            out["falhas"].append(f"fonte {nome}: {type(e).__name__}: {str(e)[:120]}")
        out["falhas"] += [f"{nome}: {x}" for x in diag["fontes"][nome]["falhas"]][:10]
    try:
        out["suap_robots"] = C.robots_permite("https://suap.camaragyn.go.gov.br/consulta", cfg)
    except Exception as e:  # noqa: BLE001
        out["suap_robots"] = f"erro: {type(e).__name__}"
    return out


# ── 05 · ALEGO ─────────────────────────────────────────────────────────────────────────────────────────────────────
def alego(de: date, ate: date) -> dict:
    out = {"spl": {}, "noticias": [], "falhas": []}
    for u in ("https://alegodigital.al.go.leg.br/spl/", "https://alegodigital.al.go.leg.br/spl/consulta-producao.aspx"):
        st, b, err = get(u, timeout=25)
        out["spl"][u] = {"http": st, "erro": err, "bytes": len(b or b"")}
    vistos = set()
    for pg in range(1, 13):
        st, b, err = get(f"https://portal.al.go.leg.br/noticias?page={pg}", timeout=25)
        if not b:
            out["falhas"].append(f"notícias p{pg}: {err or st}"); break
        h = b.decode("utf-8", "replace")
        for m in re.finditer(r'href="(https://portal\.al\.go\.leg\.br/noticias/(\d+)/[^"]+)"[^>]*>(.*?)</a>', h, re.S):
            if m.group(2) in vistos:
                continue
            vistos.add(m.group(2))
            out["noticias"].append({"url": m.group(1), "titulo": limpo(m.group(3))[:200]})
        time.sleep(0.5)
    return out


def main(de: date, ate: date) -> dict:
    res = {"periodo": [de.isoformat(), ate.isoformat()], "termos": TERMOS}
    for nome, f in (("01_diario_goiania", goiania), ("02_diario_goias", goias), ("04_camara_goiania", camara), ("05_alego", alego)):
        t0 = time.time()
        try:
            res[nome] = f(de, ate)
        except Exception as e:  # noqa: BLE001
            res[nome] = {"erro": f"{type(e).__name__}: {str(e)[:200]}"}
        res[nome]["segundos"] = round(time.time() - t0)
        print(nome, {k: (len(v) if isinstance(v, list) else v) for k, v in res[nome].items() if k != "portal"}, flush=True)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{de.isoformat()}_{ate.isoformat()}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--de", default=date.today().replace(day=1).isoformat())
    ap.add_argument("--ate", default=date.today().isoformat())
    a = ap.parse_args()
    main(date.fromisoformat(a.de), date.fromisoformat(a.ate))
