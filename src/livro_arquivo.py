"""O LIVRO EM ARQUIVO PRÓPRIO E A ABSORÇÃO DOS BANCOS PARALELOS (titular, 16/10/2026).

REGRA MÁXIMA: o único banco de dados do Eldorado são os LIVROS. Todo dado de oportunidade vive no livro dela.
Oportunidade aberta com livro acrescenta as informações do edital atual às anteriores (o edital atual sempre vale);
oportunidade sem livro ganha um livro com todas as informações levantadas. É proibido criar dados fora dos livros.

  biblioteca_alexandria/livros/<livro>.json   o CONTEÚDO do livro: o que cada etapa e ferramenta levantou sobre a
                                              oportunidade, por origem ("acervo"), com a data em que entrou
  biblioteca_alexandria/fontes/motores.json   a CAPA dos livros (identidade e ficha) — índice do catálogo
  biblioteca_alexandria/livros/_origens.json  controle: de que arquivo antigo veio cada entrada e em que formato,
                                              para os leitores remontarem a mesma estrutura a partir dos livros

ABSORÇÃO (absorver): cada ENTRADA de um arquivo paralelo (chave de dicionário, item de lista ou linha de JSONL) é ligada
a um livro pela chave, pelo id, pelo link ou pelo título+órgão; ligada → vai ao arquivo do livro; não ligada → se for
oportunidade com prazo vigente que passa nos portões, ganha livro; senão é descartada. Depois o arquivo antigo é APAGADO.
LEITURA (carregar): o leitor pede o caminho antigo e recebe a mesma estrutura, montada a partir dos livros.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from .nucleo import ROOT
from .vistos import chave

PASTA = ROOT / "biblioteca_alexandria/livros"
ORIGENS = PASTA / "_origens.json"
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
URL = re.compile(r"https?://[^\s\"'<>]+")


def _j(p: Path, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rel(p) -> str:
    p = Path(p)
    try:
        return str(p.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(p)


# ── livro em arquivo ──────────────────────────────────────────────────────────────────────────────────────────────
def ler(lid: str) -> dict:
    return _j(PASTA / f"{lid}.json", {"id": lid, "acervo": {}})


def gravar(lid: str, d: dict) -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / f"{lid}.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


# ── ligação ───────────────────────────────────────────────────────────────────────────────────────────────────────
def indice() -> dict:
    """chave/id/link/título → livro, a partir da capa (catálogo) e do conteúdo já registrado."""
    from .banco_livros import _chaves_do_livro
    L = (_j(CAT, {}) or {}).get("motores") or []
    idx = {}
    for lv in L:
        lid = lv.get("id"); idx[lid] = lid
        for k in _chaves_do_livro(lv):
            idx.setdefault(k, lid)
        op = lv.get("oportunidade") if isinstance(lv.get("oportunidade"), dict) else {}
        if op.get("id_repositorio"):
            idx[op["id_repositorio"]] = lid
        for sec in ("coleta", "brutos"):
            for i, b in (lv.get(sec) or {}).items():
                idx.setdefault(str(i).split(":")[-1], lid)
                if isinstance(b, dict) and b.get("url"):
                    idx.setdefault(chave(b), lid)
        for e in lv.get("historico") or []:
            if isinstance(e, dict):
                if e.get("id"):
                    idx.setdefault(e["id"], lid)
                if isinstance(e.get("pagina_oficial"), str):
                    idx.setdefault(chave({"url": e["pagina_oficial"]}), lid)
        t = f"{lv.get('programa') or ''}|{lv.get('orgao') or ''}".lower().strip("|")
        if len(t) > 12:
            idx.setdefault("t:" + t, lid)
    return idx


def ligar(k, v, idx: dict) -> str | None:
    cands = []
    if isinstance(k, str):
        cands.append(k)
        if k.startswith("http"):
            cands.append(chave({"url": k}))
    if isinstance(v, dict):
        for f in ("livro", "livro_id", "opressor", "oportunidade_id", "id_repositorio", "id"):
            if isinstance(v.get(f), str):
                cands.append(v[f])
        for f in ("url", "link_oficial", "pagina", "pagina_oficial", "site_oficial", "fonte"):
            if isinstance(v.get(f), str) and v[f].startswith("http"):
                cands.append(chave({"url": v[f]}))
        t = f"{v.get('programa') or v.get('titulo') or ''}|{v.get('orgao') or ''}".lower().strip("|")
        if len(t) > 12:
            cands.append("t:" + t)
    for c in cands:
        if c in idx:
            return idx[c]
    if isinstance(v, (dict, list)):                       # último recurso: um link que já pertence a um livro
        for u in URL.findall(json.dumps(v, ensure_ascii=False)[:20000]):
            c = chave({"url": u.rstrip(".,;)")})
            if c in idx:
                return idx[c]
    return None


def _oportunidade_vigente(v) -> bool:
    if not isinstance(v, dict) or not (v.get("titulo") and (v.get("url") or v.get("link_oficial"))):
        return False
    fim = str(v.get("fim") or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim) or fim < date.today().isoformat():
        return False
    from .porta_oportunidade import motivo_para_nao_guardar
    return motivo_para_nao_guardar(v) is None


# ── absorção ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _unidades(p: Path):
    t = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix == ".jsonl":
        return "jsonl", [(str(i), json.loads(l)) for i, l in enumerate(t.splitlines()) if l.strip()]
    o = json.loads(t)
    if isinstance(o, dict):
        return "dict", list(o.items())
    if isinstance(o, list):
        return "list", [(str(i), x) for i, x in enumerate(o)]
    return "valor", [("_", o)]


def absorver(caminhos: list, gravar_: bool = True, apagar: bool = True) -> dict:
    from .banco_livros import _novo_livro
    idx = indice()
    cat = _j(CAT, {"motores": []}); L = cat.setdefault("motores", [])
    origens = _j(ORIGENS, {})
    livros: dict = {}
    st = Counter(); criados = 0; arquivos = []
    for p in caminhos:
        p = Path(p)
        if not p.is_file() or p.suffix not in (".json", ".jsonl"):
            continue
        try:
            forma, unidades = _unidades(p)
        except Exception:  # noqa: BLE001
            st["arquivo ilegível"] += 1; continue
        rel = _rel(p); mapa = []
        for k, v in unidades:
            lid = ligar(k, v, idx)
            if not lid and _oportunidade_vigente(v):        # oportunidade sem livro: ganha livro (com o que foi levantado)
                lv = _novo_livro(v, chave(v)); L.append(lv); idx[chave(v)] = lv["id"]; lid = lv["id"]; criados += 1
            if not lid:
                st["descartadas (não ligam e não são oportunidade vigente)"] += 1; continue
            d = livros.setdefault(lid, ler(lid))
            d.setdefault("acervo", {}).setdefault(rel, {})[k] = {"dado": v, "absorvido_em": _agora()}
            mapa.append([lid, k]); st["absorvidas"] += 1
        origens[rel] = {"forma": forma, "entradas": mapa}
        arquivos.append(p)
    if gravar_:
        for lid, d in livros.items():
            gravar(lid, d)
        PASTA.mkdir(parents=True, exist_ok=True)
        ORIGENS.write_text(json.dumps(origens, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if criados:
            CAT.write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if apagar:
            for p in arquivos:
                p.unlink()                                 # o banco paralelo é APAGADO (à força)
    return {"arquivos": len(arquivos), "livros_tocados": len(livros), "livros_criados": criados, **dict(st)}


# ── leitura pelos módulos antigos ─────────────────────────────────────────────────────────────────────────────────
def carregar(caminho, padrao=None):
    """O leitor pede o CAMINHO antigo e recebe a mesma estrutura, montada a partir dos livros."""
    rel = _rel(caminho)
    o = (_j(ORIGENS, {}) or {}).get(rel)
    if not o:
        return padrao
    cache: dict = {}
    vals = []
    for lid, k in o["entradas"]:
        d = cache.setdefault(lid, ler(lid))
        x = ((d.get("acervo") or {}).get(rel) or {}).get(k)
        if x is not None:
            vals.append((k, x["dado"]))
    if o["forma"] == "dict":
        return {k: v for k, v in vals}
    if o["forma"] in ("list", "jsonl"):
        return [v for _k, v in vals]
    return vals[0][1] if vals else padrao


def arquivos_de(pasta) -> list[str]:
    """Os 'arquivos' antigos de uma pasta (agora dentro dos livros), para quem fazia glob."""
    pre = _rel(pasta).rstrip("/") + "/"
    return sorted(k for k in (_j(ORIGENS, {}) or {}) if k.startswith(pre))
