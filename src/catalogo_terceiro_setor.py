"""CATÁLOGO DO TERCEIRO SETOR — a missão do Piloto quando não há resgate a fazer.

Regra do titular (24/09): o Piloto primeiro resgata oportunidades publicadas nos últimos 30 dias.
Não havendo o que resgatar, ele vai aos sites especializados do terceiro setor e de outras entidades
para identificar as EMPRESAS que aparecem neles — apoiadores, patrocinadores, parceiros — e as empresas
que declaram ESG no próprio site, catalogando os sites oficiais e as páginas voltadas a entidades.

O que cada visita grava no catálogo (estado/piloto/catalogo_terceiro_setor.json):
    site           o endereço oficial e quando foi lido
    paginas_para_entidades   links da página que se dirigem a OSC (editais, parcerias, apoio, inscrições)
    empresas       empresas que aparecem no texto como apoiadoras/patrocinadoras (via ler_rastros)
    esg            se o site declara ESG/sustentabilidade/responsabilidade social, e onde

As empresas encontradas seguem para o radar de reconhecimento (registrar), que já alimenta a lista de
empresas. Um site lido hoje só volta ao plano depois de 7 dias — sem isso a missão lia as mesmas quatro
páginas a cada voo.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urljoin, urlsplit

from .nucleo import ROOT, load_json, now_iso, write_json

CATALOGO = ROOT / "estado/piloto/catalogo_terceiro_setor.json"
PUB = ROOT / "docs/dados/catalogo_terceiro_setor.json"
SEMENTES = ROOT / "config/sites_terceiro_setor.json"
REVISITA_DIAS = 7

RX_ENTIDADE = re.compile(r"edital|chamada|chamamento|inscri[çc]|parceir|apoio|patroc|para (ongs|oscs|organiza|entidades|institui)|"
                         r"terceiro setor|sociedade civil|projetos sociais|fomento|doa[çc]|volunt", re.I)
RX_ESG = re.compile(r"\bESG\b|sustentabilidade|responsabilidade social|impacto social|investimento social|"
                    r"relat[óo]rio de sustentabilidade|pacto global|ODS\b", re.I)


def catalogo() -> dict:
    return load_json(CATALOGO) if CATALOGO.exists() else {"em": None, "sites": {}}


def sementes() -> list[dict]:
    d = load_json(SEMENTES) if SEMENTES.exists() else {}
    return d.get("sites") or []


def _chave(url: str) -> str:
    return (urlsplit(url).hostname or url).lower().replace("www.", "")


def sementes_de_associacoes() -> list[dict]:
    """ASSOCIAÇÕES QUE JÁ EXISTEM (titular, 24/09): toda entidade do sistema que tem site próprio entra
    no rodízio — é no site delas que aparecem os apoiadores, patrocinadores e parceiros."""
    import json as _j
    out, vistos = [], set()
    for base in (ROOT / "biblioteca_alexandria/associacoes", ROOT / "dados/associacoes"):
        for f in base.rglob("*.json") if base.exists() else []:
            try:
                d = _j.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for it in (d if isinstance(d, list) else (d.get("itens") or d.get("associacoes") or [d])):
                if not isinstance(it, dict):
                    continue
                u = str(it.get("site") or it.get("url") or it.get("website") or "")
                if u.startswith("http") and not re.search(r"facebook|instagram|gov\.br|mapaosc|youtube", u) and _chave(u) not in vistos:
                    vistos.add(_chave(u)); out.append({"url": u, "nome": it.get("nome") or it.get("razao_social") or _chave(u), "tipo": "associacao"})
    return out


def empresas_ja_conhecidas() -> set[str]:
    """Empresas que já constam da base de incentivadores (SALIC etc.): o Piloto não gasta voo 'descobrindo'."""
    arq = ROOT / "biblioteca_alexandria/base/incentivos/empresas_incentivadoras.jsonl"
    if not arq.exists():
        return set()
    import json as _j
    return {re.sub(r"[^a-z0-9]", "", str(_j.loads(l).get("nome") or "").lower())[:40] for l in arq.read_text(encoding="utf-8").splitlines() if l.strip()}


def proximo_site() -> dict | None:
    """O site há mais tempo sem leitura, entre as sementes e os sites já catalogados."""
    cat = catalogo()
    limite = (datetime.now(timezone.utc) - timedelta(days=REVISITA_DIAS)).isoformat(timespec="seconds")
    candidatos = []
    for s in sementes() + sementes_de_associacoes():
        k = _chave(s["url"])
        reg = cat["sites"].get(k) or {}
        lido = reg.get("lido_em") or ""
        if lido < limite and not reg.get("inacessivel"):
            candidatos.append((lido, {"url": s["url"], "nome": s.get("nome") or k, "tipo": s.get("tipo") or "especializado"}))
    for k, v in cat["sites"].items():
        if any(_chave(s["url"]) == k for s in sementes()):
            continue
        if (v.get("lido_em") or "") < limite and v.get("url") and not v.get("inacessivel"):
            candidatos.append((v.get("lido_em") or "", {"url": v["url"], "nome": v.get("nome") or k, "tipo": v.get("tipo") or "descoberto"}))
    candidatos.sort(key=lambda x: x[0])
    if candidatos:
        return candidatos[0][1]
    # PÁGINAS PARA ENTIDADES (24/09): esgotadas as sementes, o Piloto desce um nível — visita as páginas
    # voltadas a OSC que ele mesmo catalogou (editais, parcerias, inscrições). É onde a oportunidade está.
    lidas = {k for k in cat["sites"]}
    for k, v in sorted(cat["sites"].items(), key=lambda kv: kv[1].get("lido_em") or ""):
        for pg in v.get("paginas_para_entidades") or []:
            u = pg.get("url") or ""
            ck = _chave(u) + urlsplit(u).path.rstrip("/")[:60]
            if u.startswith("http") and ck not in lidas and (cat["sites"].get(ck) or {}).get("lido_em", "") < limite:
                return {"url": u, "nome": f"{v.get('nome')} · {pg.get('rotulo') or 'página para entidades'}"[:90], "tipo": "pagina-de-entidades", "_chave": ck}
    return None


def falhou(site: dict) -> None:
    """SITE QUE NÃO RESPONDE SAI DA VEZ (25/09). A falha não gravava leitura, e o mesmo site era escolhido de
    novo a cada voo — o Captamos foi tentado 30 vezes seguidas. A tentativa conta como leitura; na terceira
    falha seguida o site é marcado inacessível e deixa o rodízio."""
    cat = catalogo()
    k = site.get("_chave") or _chave(site["url"])
    v = cat["sites"].setdefault(k, {"url": site["url"], "nome": site.get("nome"), "tipo": site.get("tipo")})
    v["lido_em"] = now_iso(); v["falhas_seguidas"] = (v.get("falhas_seguidas") or 0) + 1
    if v["falhas_seguidas"] >= 3:
        v["inacessivel"] = True
    cat["em"] = now_iso(); write_json(CATALOGO, cat)


def catalogar(site: dict, texto: str, links: list[tuple[str, str]]) -> dict:
    """Grava o que a página mostrou: páginas para entidades, empresas presentes, ESG declarado."""
    from .reconhecimento import ler_rastros, registrar
    url = site["url"]
    paginas = []
    vistos = set()
    for href, rotulo in links[:400]:
        u = urljoin(url, href or "")
        if not u.startswith("http") or u in vistos:
            continue
        if RX_ENTIDADE.search(f"{rotulo} {u}"):
            vistos.add(u); paginas.append({"url": u, "rotulo": (rotulo or "")[:90]})
        if len(paginas) >= 30:
            break
    rastros = ler_rastros(texto, url)
    empresas = []
    conhecidas = empresas_ja_conhecidas()
    for r in rastros[:40]:
        it = registrar(r, "site_especializado", 1)
        if it:
            ja = re.sub(r"[^a-z0-9]", "", str(it.get("empresa") or "").lower())[:40] in conhecidas
            empresas.append({"empresa": it.get("empresa"), "via": r.get("via"), "ja_na_base_de_incentivos": ja})
    m = RX_ESG.search(texto or "")
    esg = {"declarado": bool(m), "trecho": (texto[max(0, m.start() - 60): m.end() + 80].strip() if m else None)}
    cat = catalogo()
    k = site.get("_chave") or _chave(url)
    anterior = cat["sites"].get(k) or {}
    cat["sites"][k] = {"url": url, "nome": site.get("nome") or k, "tipo": site.get("tipo"), "lido_em": now_iso(), "falhas_seguidas": 0,
                       "leituras": (anterior.get("leituras") or 0) + 1,
                       "paginas_para_entidades": paginas, "empresas": empresas, "esg": esg,
                       "texto_bytes": len((texto or "").encode())}
    cat["em"] = now_iso()
    write_json(CATALOGO, cat)
    publicar()
    return cat["sites"][k]


def publicar() -> dict:
    cat = catalogo()
    resumo = {"em": cat.get("em"), "sites": len(cat["sites"]),
              "com_esg": sum(1 for v in cat["sites"].values() if (v.get("esg") or {}).get("declarado")),
              "paginas_para_entidades": sum(len(v.get("paginas_para_entidades") or []) for v in cat["sites"].values()),
              "empresas": sorted({e["empresa"] for v in cat["sites"].values() for e in (v.get("empresas") or []) if e.get("empresa")}),
              "itens": [{"nome": v.get("nome"), "url": v.get("url"), "tipo": v.get("tipo"), "lido_em": v.get("lido_em"),
                         "paginas": len(v.get("paginas_para_entidades") or []), "empresas": len(v.get("empresas") or []),
                         "esg": (v.get("esg") or {}).get("declarado")} for v in cat["sites"].values()]}
    write_json(PUB, resumo)
    return resumo
