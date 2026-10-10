"""MOTOR OUTRAS OPORTUNIDADES (titular, 10/10/2026).

Lê, TODOS OS DIAS, as fontes oficiais que já renderam oportunidade e nenhum outro motor vigiava (197 no conselho de
10/10), UM SITE POR VEZ, na ordem que a rede aprende (quem mais rende primeiro; o nunca lido ganha a vez cedo).
RECEBE fontes novas sozinho: a lista é refeita a cada execução com as fontes irmãs do conselho, as candidatas
privadas/internacionais do Espião e os sites oficiais certificados pelo Cartório que nenhum motor cobre.

Dimensionamento (medido na produção em 10/10): 2,6 s por página (mediana; 7 s no pior caso), ~2 páginas por site
(início + listagem de editais). Uma execução lê SITES_POR_EXECUCAO sites; com EXECUCOES_POR_DIA execuções, um clone cobre
SITES_POR_EXECUCAO × EXECUCOES_POR_DIA sites por dia. Os clones (outras-oportunidades-1…N) repartem as fontes por domínio
e N é calculado para ler TODAS as fontes no mesmo dia (teto: MAX_CLONES).
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FONTES = ROOT / "estado/outras_oportunidades/fontes.json"
SITES_POR_EXECUCAO = 17
EXECUCOES_POR_DIA = 3
MAX_CLONES = 8
SEG_POR_PAGINA = (2.6, 7.0)
PAGINAS_POR_SITE = 2


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _dom(u) -> str:
    try:
        return (urlsplit(str(u or "")).hostname or "").lower().replace("www.", "")
    except ValueError:
        return ""


def receber() -> dict:
    """Junta as fontes (conselho + Espião + Cartório), preservando a estatística de cada domínio."""
    from .cartorio_leitura import regua
    atual = _j(FONTES, {}) or {}
    fontes = atual.get("fontes") or {}
    cob = {d.replace("www.", "") for d in ((_j(ROOT / "docs/dados/cobertura.json", {}).get("por_dominio") or {}))}
    novas = []
    def pôr(url, origem, peso=1):
        d = _dom(url)
        if not d or d in cob or not str(url).startswith("http") or not regua(url)[0] or d in ("pncp.gov.br", "in.gov.br", "gov.br"):
            return
        if d not in fontes:
            fontes[d] = {"url": f"{urlsplit(url).scheme}://{urlsplit(url).netloc}", "exemplo": url, "origem": origem, "peso": 0,
                         "leituras": 0, "achados": 0, "entrou_em": datetime.now(timezone.utc).date().isoformat()}
            novas.append(d)
        fontes[d]["peso"] = max(int(fontes[d].get("peso") or 0), int(peso))
    for f in (_j(ROOT / "estado/conselho/fontes_irmas.json", {}).get("fontes") or []):
        pôr(f.get("url"), "conselho (fontes irmãs)", f.get("peso") or 1)
    for c in (_j(ROOT / "estado/piloto/candidatas_do_catalogo.json", {}).get("candidatas") or []):
        if str(c.get("origem") or "").startswith("Piloto - Espião (privado"):
            pôr(c.get("url"), "Espião (privado/internacional)", 1)
    for c in ((_j(ROOT / "estado/cartorio/certidoes.json", {}).get("certidoes") or {}).values()):
        if c.get("link_oficial"):
            pôr(c["link_oficial"], "Cartório (site oficial certificado)", 1)
    out = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "regra": (__doc__ or "").split("\n\n")[1],
           "fontes": fontes, "novas_nesta_rodada": novas[-50:]}
    FONTES.parent.mkdir(parents=True, exist_ok=True)
    FONTES.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        alimentar_agregadores(fontes)
    except Exception:  # noqa: BLE001
        pass
    return out


AGREGADORES = ROOT / "estado/outras_oportunidades/sites_para_agregadores.json"


def alimentar_agregadores(fontes: dict | None = None) -> dict:
    """Os motores que AGREGAM (patrocínio privado e incentivos fiscais) recebem os locais novos de busca:
    sites de empresas/organizações privadas descobertos pelo Espião e as fontes privadas das Outras Oportunidades."""
    from .cartorio_leitura import GOV
    fontes = fontes if fontes is not None else (_j(FONTES, {}).get("fontes") or {})
    priv = {}
    for d, f in fontes.items():
        if not GOV.search(d) and not d.endswith("in.gov.br"):
            priv[d] = {"url": f["url"], "nome": d, "origem": f.get("origem")}
    for a in (_j(ROOT / "dados/empresas/go/espiao_empresas.json", {}).get("achados") or []):
        d = _dom(a.get("url"))
        if d and not GOV.search(d):
            priv.setdefault(d, {"url": f"{urlsplit(a['url']).scheme}://{urlsplit(a['url']).netloc}", "nome": a.get("empresa") or d, "origem": "Espião"})
    lista = sorted(priv.values(), key=lambda x: x["nome"])
    out = {"em": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "patrocinio": lista, "incentivos": lista,
           "regra": "locais novos de busca para os motores agregadores (patrocínio privado e incentivos fiscais)"}
    AGREGADORES.parent.mkdir(parents=True, exist_ok=True)
    AGREGADORES.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def dimensionar(n_fontes: int) -> dict:
    por_clone_dia = SITES_POR_EXECUCAO * EXECUCOES_POR_DIA
    clones = max(1, min(MAX_CLONES, math.ceil(n_fontes / por_clone_dia)))
    seg = [round(SITES_POR_EXECUCAO * PAGINAS_POR_SITE * s) for s in SEG_POR_PAGINA]
    return {"fontes": n_fontes, "sites_por_execucao": SITES_POR_EXECUCAO, "execucoes_por_dia": EXECUCOES_POR_DIA,
            "sites_por_clone_por_dia": por_clone_dia, "clones": clones, "cobertura_diaria": min(n_fontes, clones * por_clone_dia),
            "segundos_por_execucao": {"tipico": seg[0], "pior_caso": seg[1]},
            "le_todas_no_dia": clones * por_clone_dia >= n_fontes}


def _prioridade(d: str, f: dict) -> float:
    """A rede aprende quem rende: taxa de achados (Laplace) + bônus para quem nunca foi lido + peso de origem."""
    lei = int(f.get("leituras") or 0); ach = int(f.get("achados") or 0)
    return (ach + 1) / (lei + 2) + (0.5 if lei == 0 else 0) + 0.05 * min(10, int(f.get("peso") or 0))


def lista_do_clone(k: int, n: int, agora: datetime | None = None) -> list[str]:
    """Os sites que o clone k (1…n) lê NESTA execução: sua parte das fontes, na ordem da rede, janela do horário."""
    fontes = (_j(FONTES, {}).get("fontes") or {})
    parte = [(d, f) for d, f in fontes.items() if int(hashlib.md5(d.encode()).hexdigest(), 16) % n == (k - 1)]
    parte.sort(key=lambda df: -_prioridade(*df))
    if not parte:
        return []
    agora = agora or datetime.now(timezone.utc)
    vez = (agora.timetuple().tm_yday * EXECUCOES_POR_DIA + min(EXECUCOES_POR_DIA - 1, agora.hour * EXECUCOES_POR_DIA // 24))
    ini = (vez * SITES_POR_EXECUCAO) % len(parte)
    janela = (parte[ini:] + parte[:ini])[:SITES_POR_EXECUCAO]
    return [f.get("exemplo") or f["url"] for _d, f in janela]


def expandir(modelo: dict) -> list[dict]:
    """No registro da esquadra: o modelo 'outras-oportunidades' vira N clones, cada um com a sua lista do horário."""
    try:
        n_fontes = len(receber()["fontes"])
    except Exception:  # noqa: BLE001
        n_fontes = len((_j(FONTES, {}).get("fontes") or {}))
    dim = dimensionar(n_fontes)
    out = []
    for k in range(1, dim["clones"] + 1):
        s = dict(modelo); s["id"] = f"outras-oportunidades-{k}"; s["nome"] = f"Outras Oportunidades {k}/{dim['clones']}"
        s["urls"] = lista_do_clone(k, dim["clones"]); s["max_paginas"] = SITES_POR_EXECUCAO * PAGINAS_POR_SITE
        s["dimensionamento"] = dim; s.pop("urls_dinamicas", None)
        out.append(s)
    return out


def contabilizar(r: dict, sensor: dict) -> None:
    """Depois da leitura de um clone: cada site lido soma 1 leitura; cada achado soma 1 ao seu domínio (a rede aprende)."""
    if not str(sensor.get("id") or "").startswith("outras-oportunidades-"):
        return
    d = _j(FONTES, {}) or {}
    fontes = d.get("fontes") or {}
    for u in sensor.get("urls") or []:
        if _dom(u) in fontes:
            fontes[_dom(u)]["leituras"] = int(fontes[_dom(u)].get("leituras") or 0) + 1
            fontes[_dom(u)]["ultima_leitura"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for a in r.get("achados") or []:
        if _dom(a.get("url")) in fontes:
            fontes[_dom(a.get("url"))]["achados"] = int(fontes[_dom(a.get("url"))].get("achados") or 0) + 1
    d["fontes"] = fontes
    FONTES.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
