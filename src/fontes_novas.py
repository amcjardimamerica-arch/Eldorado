"""FONTES NOVAS PARA OS MOTORES (titular, 26/09) — a finalidade primordial do Piloto - Espião.

O que o Espião descobre e o Interceptador confirma vira FONTE dos motores regulares: entra em
config/fontes.json (modo html_publico, ativa) e passa a ser lida todo dia pelo monitoramento, como as
outras 83. Assim uma oportunidade achada uma vez vira busca permanente — as próximas edições do mesmo
edital, do mesmo instituto, do mesmo agregador, chegam pelos motores, sem depender do Piloto.

Dois caminhos:
    agregar_pagina_oficial(...)   página oficial de uma oportunidade mapeada pelo Interceptador
    agregar_do_catalogo()         sites do terceiro setor com várias páginas de editais/inscrições (agregadores)
Registro do que entrou: config/fontes_novas.json.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from .nucleo import load_json, write_json

ROOT = Path(__file__).resolve().parents[1]
FONTES = ROOT / "config/fontes.json"
REGISTRO = ROOT / "config/fontes_novas.json"


def _host(u: str) -> str:
    return (urlsplit(u).hostname or "").replace("www.", "").lower()


def _ja_monitorado(host: str) -> bool:
    f = load_json(FONTES) or {}
    for x in f.get("fontes") or []:
        hs = [_host(x.get("url") or "")] + [str(h).replace("www.", "").lower() for h in (x.get("hosts_links") or [])]
        if host and any(host == h or host.endswith("." + h) for h in hs if h):
            return True
    return False


def agregar(url: str, nome: str, tipo: str, origem: str, nivel: str = "privado", areas: list | None = None, uf: str | None = None) -> bool:
    """Entra em config/fontes.json se o domínio ainda não é monitorado. Devolve True se entrou."""
    host = _host(url)
    if not host or _ja_monitorado(host) or re.search(r"duckduckgo|bing\.com|google\.|facebook|instagram|linkedin|youtube|forms\.gle|pncp\.gov\.br", host + url):
        return False
    f = load_json(FONTES) or {"fontes": []}
    fid = "esp-" + re.sub(r"[^a-z0-9]+", "-", host.split(".")[0])[:30]
    if any(x.get("id") == fid for x in f["fontes"]):
        fid += "-" + date.today().strftime("%m%d")
    f["fontes"].append({"id": fid, "nome": nome[:80], "nivel": nivel, "tipo": tipo, "territorio": "BR" if not uf else uf, "uf": uf,
                        "municipio": None, "areas": areas or [], "url": url, "hosts_links": [host], "confianca": "descoberta",
                        "modo": "html_publico", "ativa": True, "origem": origem, "agregada_em": date.today().isoformat()})
    write_json(FONTES, f)
    reg = load_json(REGISTRO) if REGISTRO.exists() else {"regra": "fontes descobertas pelo Espião e confirmadas pelo Interceptador viram monitoramento dos motores", "fontes": []}
    reg["fontes"].append({"id": fid, "nome": nome[:80], "url": url, "tipo": tipo, "origem": origem, "em": date.today().isoformat()})
    write_json(REGISTRO, reg)
    return True


def agregar_pagina_oficial(reg_edital: dict, origem: str = "Piloto - Interceptador") -> bool:
    u = reg_edital.get("pagina_oficial")
    if not u:
        return False
    # monitora a PÁGINA-MÃE do edital (a seção de editais do site), não o edital específico
    p = urlsplit(u); base = f"{p.scheme}://{p.netloc}" + "/".join(p.path.rstrip("/").split("/")[:-1]) if p.path.count("/") > 1 else u
    nome = (reg_edital.get("orgao") or reg_edital.get("titulo") or _host(u))[:80]
    return agregar(base, f"{nome} — editais", "editais_privados" if (reg_edital.get("nivel") in (None, "privada")) else "editais_publicos", origem,
                   nivel=reg_edital.get("nivel") or "privado", areas=[reg_edital["area"]] if reg_edital.get("area") else [], uf=reg_edital.get("uf"))


def agregar_do_catalogo(minimo_paginas: int = 3) -> int:
    """Site do terceiro setor com várias páginas de editais/inscrições é um AGREGADOR: vira fonte."""
    cat = load_json(ROOT / "estado/piloto/catalogo_terceiro_setor.json") or {}
    n = 0
    for v in (cat.get("sites") or {}).values():
        pags = [p for p in (v.get("paginas_para_entidades") or []) if re.search(r"edital|editais|chamada|inscri|pr[eê]mio|fundo", str(p.get("rotulo", "")) + str(p.get("url", "")), re.I)]
        if len(pags) >= minimo_paginas and v.get("url") and v.get("tipo") != "pagina-de-entidades":
            alvo = next((p["url"] for p in pags if re.search(r"/editais?/?$|/editais?/|/oportunidades|/chamadas", str(p.get("url")))), v["url"])
            if agregar(alvo, f"{v.get('nome', '')} — editais e chamadas", "agregador_terceiro_setor", "Piloto - Espião (catálogo)"):
                n += 1
    return n
