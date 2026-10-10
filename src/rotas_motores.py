"""APRENDIZ DE ROTAS DOS MOTORES (titular, 10/10/2026).

Toda leitura de motor é registrada. Leitura VAZIA = página sem conteúdo útil: não respondeu, sem links (JavaScript),
recusou a nuvem, endereço errado, ou só página institucional sem rótulo de edital. Ao chegar a 5 VAZIAS SEGUIDAS numa
rota, o motor entra no relatório como "ALTERAR ROTA" e o afinador testa rotas alternativas:
  · caminhos de edital no mesmo domínio (/editais, /chamamentos, /chamadas-publicas, /transparencia/editais, /noticias)
  · a API e o mapa do site (/wp-json/wp/v2/posts?search=edital, /feed, /sitemap.xml)
  · sites oficiais já conhecidos do mesmo órgão (biblioteca do Cartório)
  · CÂMARAS MUNICIPAIS: sessões e matérias do SAPL (Interlegis), pauta / ordem do dia, diário oficial da câmara, notícias —
    qualquer uma prova a atividade do dia, mesmo sem oportunidade
  · cada rota é tentada DIRETO e, se o site recusar a nuvem, pela PONTE do titular (IP do Brasil)
A melhor rota entra no motor (as originais ficam, pela redundância) e, se só funcionou pela ponte, o domínio passa a
atravessar a ponte. Uma rede neural pequena (regressão logística online sobre o padrão da rota, o tipo do motor e o
caminho de acesso) aprende com cada teste ONDE costuma estar o lugar certo de busca e ordena as próximas tentativas.
Relatório: docs/dados/rotas_motores.json.
"""
from __future__ import annotations

import json
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PASTA = ROOT / "estado/rotas"
ESTADO = PASTA / "rotas.json"
APRENDIDAS = PASTA / "rotas_aprendidas.json"
PONTE = PASTA / "ponte_aprendida.json"
MODELO = PASTA / "modelo_rotas.json"
AFINADOR = PASTA / "afinador.json"                         # escrito só pelo afinador (fluxo 30); rotas.json só pelos motores
RELATORIO = ROOT / "docs/dados/rotas_motores.json"
LIMIAR = 5
CAMINHOS = ["/editais", "/edital", "/chamamentos", "/chamamento-publico", "/chamadas-publicas", "/transparencia/editais",
            "/licitacoes", "/noticias", "/wp-json/wp/v2/posts?search=edital&per_page=20", "/feed", "/sitemap.xml"]
CAMARA = ["/api/sessao/sessaoplenaria/?o=-data_inicio", "/api/materia/materialegislativa/?o=-data_apresentacao", "/sessao/pauta-sessao",
          "/pauta", "/ordem-do-dia", "/sessoes", "/diario-oficial", "/noticias", "/feed"]
VAZIA = re.compile(r"(?i)não tem links|sem links|recusa|403|404|dns|não resolve|tempo esgotado|conexão recusada|robots|"
                   r"institucional|nenhum rótulo|aguardando coleta local|parte das páginas respondeu")


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _w(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ── 1 · REGISTRO DE CADA LEITURA ───────────────────────────────────────────────────────────────────────────────
def classificar(r: dict) -> str:
    """ok · vazia — a partir do resultado do motor (sensores.ler)."""
    if r.get("achados"):
        return "ok"
    dg = r.get("diagnostico") or {}
    if int(dg.get("paginas_lidas") or 0) == 0 or int(dg.get("links_total") or 0) == 0 or VAZIA.search(str(dg.get("motivo_zero") or "")):
        return "vazia"
    return "ok"                                            # leu a página da fonte, só não havia oportunidade hoje


def registrar(r: dict, sensor: dict) -> dict:
    est = _j(ESTADO, {}) or {}
    m = est.setdefault(sensor["id"], {"vazias_seguidas": 0, "leituras": 0, "ok": 0, "status": "ok", "historico": []})
    c = classificar(r); m["leituras"] += 1
    m["ultima"] = {"em": _agora(), "classe": c, "motivo": str((r.get("diagnostico") or {}).get("motivo_zero") or "")[:160]}
    apr = (_j(APRENDIDAS, {}) or {}).get(sensor["id"])
    if apr and apr.get("aprendido_em") != m.get("rota_aplicada"):          # rota nova chegou: recomeça a contagem com ela
        m["rota_aplicada"] = apr.get("aprendido_em"); m["vazias_seguidas"] = 0; m["status"] = "rota nova em teste"
    if c == "ok":
        m["ok"] += 1; m["vazias_seguidas"] = 0
        m["status"] = "rota nova funcionando" if apr else "ok"
    else:
        m["vazias_seguidas"] += 1
        if m["vazias_seguidas"] >= LIMIAR:
            m["status"] = "alterar rota"
    m["historico"] = (m.get("historico") or [])[-29:] + [c[0]]
    m.update({"nome": sensor.get("nome"), "tipo": sensor.get("tipo"), "urls": (sensor.get("urls") or [])[:4]})
    _w(ESTADO, est)
    return m


# ── 2 · A REDE QUE APRENDE ONDE BUSCAR ─────────────────────────────────────────────────────────────────────────
def _feats(url: str, tipo: str, via: str, origem: str) -> list[str]:
    try:
        p = urlsplit(url); caminho = (p.path or "/").lower(); h = (p.hostname or "").lower()
    except ValueError:
        return ["malformada"]
    toks = [t for t in re.split(r"[/\-_.?=&]+", caminho + "?" + (p.query or "")) if 3 <= len(t) <= 20][:6]
    f = [f"tok:{t}" for t in toks] + [f"tipo:{tipo}", f"via:{via}", f"origem:{origem}", f"tld:{h.rsplit('.', 1)[-1] if '.' in h else ''}"]
    gov = bool(re.search(r"\.(gov|leg|jus|mp)\.br$", h)); raiz = caminho in ("", "/"); sapl = "sapl" in h or "/api/" in caminho
    f += [f"gov:{gov}", f"raiz:{raiz}", f"sapl:{sapl}"]
    return f


def prever(url: str, tipo: str, via: str = "direto", origem: str = "padrão") -> float:
    w = (_j(MODELO, {}) or {}).get("pesos") or {}
    z = w.get("vies", 0.0) + sum(w.get(f, 0.0) for f in _feats(url, tipo, via, origem))
    return 1 / (1 + math.exp(-max(-20, min(20, z))))


def aprender(url: str, tipo: str, via: str, origem: str, funcionou: bool, taxa: float = 0.3) -> None:
    mdl = _j(MODELO, {}) or {"pesos": {}, "exemplos": 0}
    w = mdl.setdefault("pesos", {})
    p = prever(url, tipo, via, origem); erro = (1.0 if funcionou else 0.0) - p
    for f in _feats(url, tipo, via, origem) + ["vies"]:
        w[f] = round(w.get(f, 0.0) + taxa * erro, 4)
    mdl["exemplos"] = int(mdl.get("exemplos") or 0) + 1; mdl["atualizado"] = _agora()
    _w(MODELO, mdl)


# ── 3 · CANDIDATAS E TESTE ─────────────────────────────────────────────────────────────────────────────────────
def candidatas(sensor: dict, bib: dict | None = None) -> list[dict]:
    urls = [u for u in (sensor.get("urls") or []) if str(u).startswith("http")]
    doms = []
    for u in urls:
        try:
            p = urlsplit(u); doms.append(f"{p.scheme}://{p.netloc}")
        except ValueError:
            pass
    doms = list(dict.fromkeys(doms))[:2]
    out = [{"url": u, "origem": "rota original"} for u in urls[:2]]
    camara = bool(re.search(r"(?i)c[âa]mara|legislativ|\.leg\.br", f"{sensor.get('id')} {sensor.get('nome')} {sensor.get('tipo')} {' '.join(urls)}"))
    for d in doms:
        if camara:                                     # câmara: atividade do dia (sessões, pauta, diário) vem primeiro
            h = urlsplit(d).netloc
            out += [{"url": d + c, "origem": "câmara"} for c in CAMARA]
            out += [{"url": f"https://sapl.{h.removeprefix('www.')}{c}", "origem": "câmara"} for c in CAMARA[:2]]
        out += [{"url": d + c, "origem": "padrão"} for c in CAMINHOS]
    for e in (bib or {}).values():
        for u in e.get("urls") or []:
            if any(urlsplit(u).netloc == urlsplit(d).netloc for d in doms if u.startswith("http")):
                out.append({"url": u, "origem": "biblioteca"})
    vistos, res = set(), []
    for c in out:
        if c["url"] not in vistos:
            vistos.add(c["url"]); res.append(c)
    tipo = sensor.get("tipo") or ""
    res.sort(key=lambda c: -prever(c["url"], tipo, "direto", c["origem"]))
    return res[:24]


EDITAL = re.compile(r"(?i)edital|chamamento|chamada p[úu]blica|sele[çc][ãa]o|inscri[çc][õo]es|pauta|ordem do dia|sess[ãa]o|mat[ée]ria|projeto de lei|di[áa]rio")


def avaliar(b: bytes, tipo_ct: str = "") -> dict:
    t = (b or b"")[:600000].decode("utf-8", "ignore")
    if t.lstrip().startswith(("[", "{")):
        try:
            d = json.loads(t); n = len(d) if isinstance(d, list) else len(d.get("results") or d.get("items") or [])
            return {"pontos": min(30, n * 2), "links": n, "sinais": n, "formato": "json"}
        except ValueError:
            pass
    if "<loc>" in t or "<item>" in t or "<entry>" in t:
        n = len(re.findall(r"<loc>|<item>|<entry>", t)); s = len(EDITAL.findall(t))
        return {"pontos": min(30, s + n // 10), "links": n, "sinais": s, "formato": "sitemap/feed"}
    links = re.findall(r"""<a\s[^>]*href=["'][^"']+["'][^>]*>(.*?)</a>""", t, re.I | re.S)
    sinais = sum(1 for x in links if EDITAL.search(re.sub(r"<[^>]+>", " ", x)))
    return {"pontos": sinais * 2 + (1 if len(links) > 20 else 0), "links": len(links), "sinais": sinais, "formato": "html"}


def testar(sensor: dict, baixar=None, ponte=None, bib: dict | None = None, maximo: int = 16, prazo: float | None = None) -> dict:
    """Testa as candidatas (direto e, se recusar, pela ponte); devolve a melhor e ensina a rede."""
    if baixar is None:
        from .executor_skills import baixar as baixar
    tipo = sensor.get("tipo") or ""
    testes, melhor = [], None
    import time as _t
    for c in candidatas(sensor, bib)[:maximo]:
        if prazo and _t.time() > prazo:
            break                                           # orçamento de tempo do afinador
        for via in ("direto", "ponte"):
            fn = baixar if via == "direto" else ponte
            if fn is None:
                continue
            try:
                if prazo and _t.time() > prazo:
                    break
                b, ct = fn(c["url"]); av = avaliar(b, ct); erro = None
            except Exception as e:  # noqa: BLE001
                av, erro = {"pontos": 0, "links": 0, "sinais": 0}, f"{type(e).__name__}"
            ok = av["pontos"] >= 3
            aprender(c["url"], tipo, via, c["origem"], ok)
            testes.append({"url": c["url"], "origem": c["origem"], "via": via, **av, "erro": erro, "funcionou": ok})
            if ok and (not melhor or av["pontos"] > melhor["pontos"]):
                melhor = {"url": c["url"], "via": via, "origem": c["origem"], "pontos": av["pontos"], "formato": av.get("formato")}
            if ok or not erro:
                break                                       # direto funcionou ou respondeu: não precisa da ponte
    return {"melhor": melhor, "testes": testes}


def _ponte_baixar():
    try:
        from . import ponte_brasil as PB
        if not PB.configurada():
            return None
        def f(url):
            st, _f, corpo, hdr = PB.abrir(url, timeout=45)
            if st != 200 or not corpo:
                raise RuntimeError(f"ponte HTTP {st}")
            return corpo, (hdr or {}).get("content-type", "")
        return f
    except Exception:  # noqa: BLE001
        return None


def afinar(maximo_motores: int = 8, baixar=None, ponte="auto", segundos: int = 330) -> dict:
    """Para cada motor em 'alterar rota' (5+ vazias seguidas): testa rotas, grava a melhor e ensina a rede."""
    from .sensores import registro
    est = _j(ESTADO, {}) or {}; afi = _j(AFINADOR, {}) or {}
    reg = {s["id"]: s for s in registro()}
    bib = (_j(ROOT / "estado/cartorio/biblioteca_sites.json", {}).get("sites") or {})
    pb = _ponte_baixar() if ponte == "auto" else ponte
    apr = _j(APRENDIDAS, {}) or {}; pon = _j(PONTE, {"dominios": []})
    feitos = []
    fila = sorted((mid for mid, m in est.items() if m.get("status") == "alterar rota" and mid in reg),
                  key=lambda mid: (str((afi.get(mid) or {}).get("em") or ""), -int(est[mid].get("vazias_seguidas") or 0)))
    import time as _t
    fim = _t.time() + segundos
    for mid in fila[:maximo_motores]:
        if _t.time() > fim:
            break
        r = testar(reg[mid], baixar, pb, bib, prazo=fim)
        afi[mid] = {"em": _agora(), "testes": len(r["testes"]), "melhor": r["melhor"], "detalhe": r["testes"][:16]}
        if r["melhor"]:
            apr[mid] = {"urls": [r["melhor"]["url"]], "via": r["melhor"]["via"], "origem": r["melhor"]["origem"],
                        "pontos": r["melhor"]["pontos"], "aprendido_em": _agora()}
            if r["melhor"]["via"] == "ponte":
                h = (urlsplit(r["melhor"]["url"]).hostname or "").lower()
                pon["dominios"] = sorted(set(pon.get("dominios") or []) | {h})
            afi[mid]["resultado"] = "rota nova em teste"
        else:
            afi[mid]["resultado"] = "nenhuma alternativa funcionou — segue ao Interceptador/Chrome"
        feitos.append({"motor": mid, "melhor": r["melhor"], "testes": len(r["testes"])})
        _w(AFINADOR, afi); _w(APRENDIDAS, apr); _w(PONTE, pon)       # grava a cada motor: interrupção não perde nada
    _w(AFINADOR, afi); _w(APRENDIDAS, apr); _w(PONTE, pon)
    return {"afinados": feitos, "ponte_disponivel": bool(pb)}


def aplicar(sensores: list[dict]) -> list[dict]:
    """No registro da esquadra: a rota aprendida vem PRIMEIRO; as originais ficam (redundância)."""
    apr = _j(APRENDIDAS, {}) or {}
    for s in sensores:
        a = apr.get(s.get("id"))
        if a and a.get("urls"):
            s["urls"] = list(dict.fromkeys(list(a["urls"]) + list(s.get("urls") or [])))
            s["rota_aprendida"] = a
    return sensores


def publicar() -> dict:
    est = _j(ESTADO, {}) or {}; apr = _j(APRENDIDAS, {}) or {}; mdl = _j(MODELO, {}) or {}; afi = _j(AFINADOR, {}) or {}
    top = sorted(((f, w) for f, w in (mdl.get("pesos") or {}).items() if f != "vies"), key=lambda kv: -kv[1])
    out = {"em": _agora(), "regra": (__doc__ or "").split("\n\n")[1], "limiar_vazias": LIMIAR,
           "resumo": {"motores": len(est), "alterar_rota": sum(1 for m in est.values() if str(m.get("status", "")).startswith("alterar rota")),
                      "rota_nova": len(apr), "via_ponte": len((_j(PONTE, {}) or {}).get("dominios") or []), "exemplos_da_rede": mdl.get("exemplos", 0)},
           "a_rede_aprendeu": {"melhores_sinais": top[:12], "piores_sinais": top[-8:]},
           "motores": {mid: {k: m.get(k) for k in ("nome", "status", "vazias_seguidas", "leituras", "ok", "ultima", "historico")}
                       | {"rota_aprendida": apr.get(mid), "afinado": {k: (afi.get(mid) or {}).get(k) for k in ("em", "testes", "melhor", "resultado")} if afi.get(mid) else None}
                       for mid, m in sorted(est.items(), key=lambda kv: -int(kv[1].get("vazias_seguidas") or 0))}}
    _w(RELATORIO, out)
    return out


def semear_da_esquadra() -> int:
    """Primeira vez: usa as leituras vazias seguidas que a esquadra já contou (não espera mais 5 dias)."""
    if ESTADO.exists() and _j(ESTADO, {}):
        return 0
    est = {}; n = 0
    for mid, s in (_j(ROOT / "estado/esquadra.json", {}).get("sensores") or {}).items():
        if mid in est:
            continue
        vs = int(s.get("vazias_seguidas") or 0); dg = s.get("diagnostico") or {}
        vazia = int(dg.get("paginas_lidas") or 0) == 0 or int(dg.get("links_total") or 0) == 0 or VAZIA.search(str(dg.get("motivo_zero") or ""))
        est[mid] = {"vazias_seguidas": vs if vazia else 0, "leituras": int(s.get("leituras") or 0), "ok": 0,
                    "status": "alterar rota" if (vazia and vs >= LIMIAR) else "ok", "historico": [], "nome": s.get("nome"), "tipo": s.get("tipo"),
                    "ultima": {"em": s.get("ultima"), "classe": "vazia" if vazia else "ok", "motivo": str(dg.get("motivo_zero") or "")[:160]}}
        n += 1
    _w(ESTADO, est)
    return n


if __name__ == "__main__":
    import sys
    semear_da_esquadra()
    try:
        out = afinar(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
    except Exception as ex:  # noqa: BLE001
        out = {"afinados": [], "ponte_disponivel": None, "erro": f"{type(ex).__name__}: {ex}"}
    pub = publicar()                                         # o relatório sai sempre
    print(json.dumps({"afinados": len(out["afinados"]), "ponte": out["ponte_disponivel"], "resumo": pub["resumo"]}, ensure_ascii=False))
