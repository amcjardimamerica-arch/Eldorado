"""INDEXAÇÃO DOS LIVROS AOS MOTORES DE BUSCA — tarefa do Piloto Espião (titular, 02/10/2026).

O Espião observa os livros da Biblioteca e as fontes de busca: para cada livro, descobre QUAL MOTOR EXISTENTE lê o
domínio onde aquela oportunidade é publicada e grava o índice no livro (livro › indexacao). Livro cujo domínio nenhum
motor lê fica marcado "sem motor" e o domínio entra na lista de candidatos a NOVA FONTE DE BUSCA — assim cada livro
tem pelo menos um motor que o acompanha. O índice também alimenta a chave de acionamento (léxico temporário).
Fontes do mapa domínio → motor: plataformas (config/investigacao.json), rotas dos motores, sites dos indexadores,
sensores especiais, catálogo das 260 fontes e órgãos do motor estadual de Goiás.
Saída: docs/dados/indexacao_livros.json
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
SAIDA = ROOT / "docs/dados/indexacao_livros.json"
# domínio com MOTOR DONO: indexa só a ele (o motor das prefeituras também consulta o PNCP, mas o dono do PNCP é o motor 04)
DONOS = {"pncp.gov.br": "pncp-api", "queridodiario.ok.org.br": "querido-diario", "in.gov.br": "dou", "goias.gov.br": "plat-estaduais-go-gov"}
GENERICOS = {"gov.br", "www.gov.br", "google.com", "duckduckgo.com", "bing.com", "facebook.com", "instagram.com", "youtube.com",
             "linkedin.com", "twitter.com", "x.com", "drive.google.com", "docs.google.com", "bit.ly", "wa.me"}


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def host(u) -> str:
    try:
        h = (urlsplit(str(u or "")).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def _urls(o) -> list[str]:
    out = []
    if isinstance(o, dict):
        for v in o.values():
            out += _urls(v)
    elif isinstance(o, list):
        for v in o:
            out += _urls(v)
    elif isinstance(o, str) and o.startswith("http"):
        out.append(o)
    return out


def mapa_dominios() -> dict[str, set[str]]:
    """domínio → motores que o leem (só motores ativos)."""
    try:
        from .sensores import registro
        ativos = {s["id"] for s in registro()}
    except Exception:  # noqa: BLE001
        ativos = set()
    M: dict[str, set[str]] = defaultdict(set)

    def add(url, motor):
        h = host(url)
        if h and h not in GENERICOS and (not ativos or motor in ativos or motor.startswith("idx-")):
            M[h].add(motor)
    for f in (_j(ROOT / "config/investigacao.json", {}).get("fontes") or []):
        if f.get("ativa", True) is not False:
            add(f.get("url"), "plat-" + f["id"])
    R = _j(ROOT / "config/rotas_motores.json", {}); R = R.get("motores", R)
    for mid, v in (R or {}).items():
        for u in _urls((v or {}).get("rotas")):
            add(u, mid)
    for s in (_j(ROOT / "config/indexadores.json", {}).get("sites") or []):
        add(s.get("url"), s.get("delegado_a") or s.get("motor") or "idx")
    for s in (_j(ROOT / "config/sensores.json", {}).get("sensores_especiais") or []):
        for u in _urls(s.get("urls")):
            add(u, s["id"])
    for f in (_j(ROOT / "config/fontes_captacao_260.json", {}).get("fontes") or []):
        if isinstance(f, dict) and f.get("id"):
            for u in _urls({k: f.get(k) for k in ("url", "urls", "rotas")}):
                add(u, f"f260-{f['id']}" if not str(f["id"]).startswith("f260") else f["id"])
    for o in ((_j(ROOT / "estado/estaduais_go.json", {}) or {}).get("orgaos") or {}).values():
        add(o.get("site"), "plat-estaduais-go-gov")
    add("https://pncp.gov.br", "pncp-api"); add("https://queridodiario.ok.org.br", "querido-diario"); add("https://www.in.gov.br", "dou")
    M["goias.gov.br"].add("plat-estaduais-go-gov")
    return M


def indexar(origem: str = "Piloto - Espião", gravar: bool = True) -> dict:
    C = _j(CAT, {}); M = mapa_dominios(); hoje = date.today().isoformat()
    sem, com, por_motor = Counter(), 0, Counter()
    for x in C.get("motores") or []:
        if x.get("papel") == "fonte_de_busca":
            continue
        doms = [host(u) for u in [x.get("pagina")] + [h.get("pagina_oficial") for h in (x.get("historico") or []) if isinstance(h, dict)]]
        doms = [d for d in dict.fromkeys(doms) if d and d not in GENERICOS]
        motores = set()
        for d in doms:
            dono = next((v for k, v in DONOS.items() if d == k or d.endswith("." + k)), None)
            motores |= {dono} if dono else {m for k, ms in M.items() if d == k or d.endswith("." + k) for m in ms}
        motores = sorted(motores)
        if motores:
            com += 1; por_motor.update(motores)
            x["indexacao"] = {"motores": motores, "dominios": doms[:5], "por": origem, "em": hoje}
        else:
            x["indexacao"] = {"motores": [], "sem_motor": True, "dominios": doms[:5], "por": origem, "em": hoje}
            for d in doms[:1]:
                sem[d] += 1
    total = sum(1 for x in C.get("motores") or [] if x.get("papel") != "fonte_de_busca")
    out = {"em": hoje, "regra": __doc__.split("Fontes do mapa")[0].strip(), "livros": total, "indexados": com,
           "sem_motor": total - com, "por_motor": dict(por_motor.most_common()),
           "candidatos_a_nova_fonte": [{"dominio": d, "livros": n} for d, n in sem.most_common(60)]}
    if gravar:
        CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: out[k] for k in ("livros", "indexados", "sem_motor")}


if __name__ == "__main__":
    print(json.dumps(indexar(), ensure_ascii=False, indent=1))
