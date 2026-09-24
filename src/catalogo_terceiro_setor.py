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


def proximo_site() -> dict | None:
    """O site há mais tempo sem leitura, entre as sementes e os sites já catalogados."""
    cat = catalogo()
    limite = (datetime.now(timezone.utc) - timedelta(days=REVISITA_DIAS)).isoformat(timespec="seconds")
    candidatos = []
    for s in sementes():
        k = _chave(s["url"])
        lido = (cat["sites"].get(k) or {}).get("lido_em") or ""
        if lido < limite:
            candidatos.append((lido, {"url": s["url"], "nome": s.get("nome") or k, "tipo": s.get("tipo") or "especializado"}))
    for k, v in cat["sites"].items():
        if any(_chave(s["url"]) == k for s in sementes()):
            continue
        if (v.get("lido_em") or "") < limite and v.get("url"):
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
    for r in rastros[:40]:
        it = registrar(r, "site_especializado", 1)
        if it:
            empresas.append({"empresa": it.get("empresa"), "via": r.get("via")})
    m = RX_ESG.search(texto or "")
    esg = {"declarado": bool(m), "trecho": (texto[max(0, m.start() - 60): m.end() + 80].strip() if m else None)}
    cat = catalogo()
    k = site.get("_chave") or _chave(url)
    anterior = cat["sites"].get(k) or {}
    cat["sites"][k] = {"url": url, "nome": site.get("nome") or k, "tipo": site.get("tipo"), "lido_em": now_iso(),
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
