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
def _bases_qd() -> list[str]:
    try:
        return json.loads((ROOT / "config/diario_goiania.json").read_text(encoding="utf-8"))["querido_diario"]["bases"]
    except Exception:  # noqa: BLE001
        return ["https://api.queridodiario.org.br", QD]


def qd_json(caminho: str):
    err = None
    for b in _bases_qd():
        j, err = get_json(f"{b.rstrip('/')}{caminho}", tentativas=2)
        if j is not None:
            return j, None
    return None, err


def goiania(de: date, ate: date) -> dict:
    out = {"catalogo": [], "achados": [], "falhas": [], "portal": {}}
    p = urlencode({"territory_ids": GOIANIA_IBGE, "published_since": de.isoformat(), "published_until": ate.isoformat(), "size": 100,
                   "sort_by": "ascending_date"})
    j, err = qd_json(f"/gazettes?{p}")
    if err:
        out["falhas"].append(f"catálogo QD: {err}")
    for g in (j or {}).get("gazettes") or []:
        if str(g.get("territory_id")) == GOIANIA_IBGE:
            out["catalogo"].append({"data": g.get("date"), "edicao": g.get("edition"), "extra": g.get("is_extra_edition"), "url": g.get("url")})
    for t in TERMOS:
        p = urlencode({"territory_ids": GOIANIA_IBGE, "querystring": f'"{t}"', "published_since": de.isoformat(),
                       "published_until": ate.isoformat(), "size": 50, "excerpt_size": 700, "number_of_excerpts": 4})
        j, err = qd_json(f"/gazettes?{p}")
        if err:
            out["falhas"].append(f"QD '{t}': {err}"); continue
        for g in (j or {}).get("gazettes") or []:
            if str(g.get("territory_id")) != GOIANIA_IBGE:
                continue
            for x in g.get("excerpts") or []:
                out["achados"].append({"termo": t, "data": g.get("date"), "edicao": g.get("edition"), "url": g.get("url"), "trecho": limpo(x)[:700]})
        time.sleep(0.5)
    # portal oficial DIRETO da nuvem (o motor só tenta pela ponte): lista de 2026 e as edições do período
    from src import diario_goiania as G
    st, b, err = get(f"https://www.goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp?ano={de.year}", timeout=40)
    eds = [e for e in G.edicoes_da_lista((b or b"").decode("latin-1", "replace")) if de.isoformat() <= e["data"] <= ate.isoformat()] if b else []
    out["portal"] = {"lista_http": st, "lista_erro": err, "edicoes_no_periodo": eds, "pdfs": []}
    for e in sorted(eds, key=lambda x: x["numero"])[:20]:
        st2, b2, err2 = get(e["url"], timeout=90, maxb=20_000_000)
        txt = None
        if b2:
            try:
                pg = G.texto_do_pdf(b2)
                txt = len(pg or "")
            except Exception:  # noqa: BLE001
                txt = None
        out["portal"]["pdfs"].append({"numero": e["numero"], "data": e["data"], "http": st2, "erro": err2, "bytes": len(b2 or b""), "letras": txt})
        time.sleep(1)
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
        if pg == 1:
            out["amostra_html"] = [limpo(x)[:200] for x in re.findall(r"<a[^>]+noticia[^>]*>.*?</a>", h, re.S | re.I)[:8]]
        for m in re.finditer(r'href=["\']((?:https?://portal\.al\.go\.leg\.br)?/?noticias/(\d+)[^"\']*)["\'][^>]*>(.*?)</a>', h, re.S | re.I):
            if m.group(2) in vistos or not limpo(m.group(3)):
                continue
            vistos.add(m.group(2))
            u = m.group(1) if m.group(1).startswith("http") else "https://portal.al.go.leg.br/" + m.group(1).lstrip("/")
            data = re.search(r"(\d{2}/\d{2}/\d{4})", h[m.end():m.end() + 600])
            out["noticias"].append({"url": u, "titulo": limpo(m.group(3))[:200], "data": data.group(1) if data else None})
        time.sleep(0.5)
    return out


def main(de: date, ate: date, partes: str = "") -> dict:
    arq = SAIDA / f"{de.isoformat()}_{ate.isoformat()}.json"
    res = json.loads(arq.read_text(encoding="utf-8")) if (partes and arq.exists()) else {}
    res.update({"periodo": [de.isoformat(), ate.isoformat()], "termos": TERMOS})
    for nome, f in (("01_diario_goiania", goiania), ("02_diario_goias", goias), ("04_camara_goiania", camara), ("05_alego", alego)):
        if partes and nome[:2] not in partes.split(","):
            continue
        t0 = time.time()
        try:
            res[nome] = f(de, ate)
        except Exception as e:  # noqa: BLE001
            res[nome] = {"erro": f"{type(e).__name__}: {str(e)[:200]}"}
        res[nome]["segundos"] = round(time.time() - t0)
        print(nome, {k: (len(v) if isinstance(v, list) else v) for k, v in res[nome].items() if k != "portal"}, flush=True)
    SAIDA.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--de", default=date.today().replace(day=1).isoformat())
    ap.add_argument("--ate", default=date.today().isoformat())
    ap.add_argument("--partes", default="", help="ex.: 01,05 (as demais ficam como estavam)")
    a = ap.parse_args()
    main(date.fromisoformat(a.de), date.fromisoformat(a.ate), a.partes)
