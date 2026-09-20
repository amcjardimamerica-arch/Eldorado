"""LÉXICO QUE APRENDE — a cada busca, a cada validação.

Inteligência aqui é estatística honesta, não adivinhação: os termos que aparecem nos
títulos e objetos dos editais APROVADOS (validados como oportunidade) e que ainda não
estão no léxico viram CANDIDATOS a termo positivo; os que aparecem nos REPROVADOS viram
candidatos a VETO. Um candidato é promovido quando:

  • positivo: aparece em ≥ 3 aprovados e em NENHUM reprovado (P24: falso positivo é o erro caro);
  • veto:     aparece em ≥ 5 reprovados e em NENHUM aprovado.

O léxico aprendido fica em config/lexico_aprendido.json e é somado à camada 1 de todos
os motores de descoberta. Cada termo carrega a contagem e os ids que o sustentam —
auditável, reversível, nunca invisível.

Fonte de verdade: dados/editais/analises.json (selo) + docs/dashboard-dados.json (títulos/objetos).
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .nucleo import ROOT, load_json, now_iso, write_json

SAIDA = ROOT / "config/lexico_aprendido.json"
MIN_POS, MIN_VETO = 3, 5
PAREDE = set("""a o os as de da do das dos e em no na nos nas para por com sem um uma uns umas ao aos à às que se sua seu suas seus
este esta estes estas esse essa isso isto aquele aquela ou não nº n° n ° art arts inciso lei anexo item itens edital editais
municipio município municipal estadual federal prefeitura secretaria estado governo publico público pública publica
2024 2025 2026 2023 2022 2021 ate até dia dias data ano anos valor r$ mil milhoes milhões diario diário oficial""".split())
STOP_NUM = re.compile(r"^\d+$|^[ivx]+$")
ARTEFATOS = {"continue", "lendo", "continue lendo", "leia", "leia mais", "saiba", "saiba mais", "acessar", "clique", "aqui",
             "selecionadas", "selecionados", "receberem", "receber", "abre", "abrem", "lanca", "lancam", "divulga", "publica"}
LIMITE_PROMOCAO = 80          # por rodada, os mais fortes; o resto fica em candidatos


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def _ngramas(texto: str) -> set[str]:
    toks = [w for w in _norm(texto).split() if w not in PAREDE and not STOP_NUM.match(w) and len(w) > 2]
    out = set(toks)
    out |= {f"{a} {b}" for a, b in zip(toks, toks[1:])}
    out |= {f"{a} {b} {c}" for a, b, c in zip(toks, toks[1:], toks[2:])}
    return out


def _lexico_atual() -> set[str]:
    termos = set()
    for arq in (ROOT / "config/lexico_terceiro_setor.json", ROOT / "config/rotas_motores.json"):
        if not arq.exists():
            continue
        d = load_json(arq)
        def walk(x):
            if isinstance(x, str) and 3 <= len(x) <= 60:
                termos.add(_norm(x).strip())
            elif isinstance(x, list):
                for y in x: walk(y)
            elif isinstance(x, dict):
                for k, v in x.items():
                    if k in ("lexico_camada1", "lexico_camada2", "camada_1_geral", "camada_1_veto", "veto_camada1", "termos", "positivos", "negativos"):
                        walk(v)
        walk(d)
    return termos


def aprender() -> dict:
    an = load_json(ROOT / "dados/editais/analises.json") if (ROOT / "dados/editais/analises.json").exists() else {}
    dados = load_json(ROOT / "docs/dashboard-dados.json")
    universo = {e["id"]: e for e in (dados.get("editais") or [])}
    ab = ROOT / "docs/dados/abertas.json"
    if ab.exists():
        from .compacto import expandir
        for o in expandir(load_json(ab)):
            universo.setdefault(o["id"], o)
    from .fonte_edital import EXTRAIDOS
    pos, neg = Counter(), Counter()
    pos_ids, neg_ids = defaultdict(set), defaultdict(set)
    n_pos = n_neg = 0
    for eid, a in an.items():
        e = universo.get(eid) or {}
        ex = load_json(EXTRAIDOS / f"{eid}.json") if (EXTRAIDOS / f"{eid}.json").exists() else {}
        texto = " ".join(str(x) for x in [e.get("titulo"), e.get("objeto"), (ex.get("itens") or {}).get("Objeto")] if x)
        if not texto.strip():
            continue
        g = _ngramas(texto)
        if a.get("selo") == "conformidade" or (a.get("verificacoes") or {}).get("e_oportunidade") and a.get("selo") != "inconformidade":
            n_pos += 1
            for t in g: pos[t] += 1; pos_ids[t].add(eid)
        elif a.get("selo") == "inconformidade" and not (a.get("verificacoes") or {}).get("duplicata"):
            n_neg += 1
            for t in g: neg[t] += 1; neg_ids[t].add(eid)
    atual = _lexico_atual()
    aprendido = load_json(SAIDA) if SAIDA.exists() else {"positivos": {}, "vetos": {}, "candidatos": {}}
    promov_pos, promov_veto, cand = {}, {}, {}
    for t, c in pos.items():
        if t in atual or len(t) < 5 or t in ARTEFATOS or any(w in ARTEFATOS for w in t.split()):
            continue
        if " " not in t and len(t) < 7:                      # palavra solta curta é vaga demais
            continue
        if c >= MIN_POS and neg.get(t, 0) == 0:
            promov_pos[t] = {"em_aprovados": c, "em_reprovados": 0, "ids": sorted(pos_ids[t])[:6], "desde": aprendido.get("positivos", {}).get(t, {}).get("desde") or now_iso()[:10]}
        elif c >= 2:
            cand[t] = {"tipo": "positivo", "em_aprovados": c, "em_reprovados": neg.get(t, 0)}
    for t, c in neg.items():
        if t in atual or len(t) < 5 or t in ARTEFATOS or any(w in ARTEFATOS for w in t.split()):
            continue
        if " " not in t and len(t) < 7:
            continue
        if c >= MIN_VETO and pos.get(t, 0) == 0:
            promov_veto[t] = {"em_reprovados": c, "em_aprovados": 0, "ids": sorted(neg_ids[t])[:6], "desde": aprendido.get("vetos", {}).get(t, {}).get("desde") or now_iso()[:10]}
        elif c >= 3 and pos.get(t, 0) == 0:
            cand[t] = {"tipo": "veto", "em_reprovados": c, "em_aprovados": 0}
    # poda: termos genéricos demais (aparecem em >40% dos aprovados E dos reprovados) nunca entram
    res = {"versao": 1, "em": now_iso(), "base": {"aprovados": n_pos, "reprovados": n_neg},
           "regra": f"positivo promovido com ≥{MIN_POS} aprovados e 0 reprovados; veto com ≥{MIN_VETO} reprovados e 0 aprovados; termos já no léxico base não são repetidos; tudo auditável pelos ids",
           "positivos": dict(sorted(promov_pos.items(), key=lambda kv: -kv[1]["em_aprovados"])[:LIMITE_PROMOCAO]),
           "vetos": dict(sorted(promov_veto.items(), key=lambda kv: -kv[1]["em_reprovados"])[:LIMITE_PROMOCAO]),
           "poda": {"artefatos_de_portal": sorted(ARTEFATOS), "limite_por_rodada": LIMITE_PROMOCAO, "palavra_solta_minima": 7},
           "candidatos": dict(sorted(cand.items(), key=lambda kv: -(kv[1].get("em_aprovados", 0) + kv[1].get("em_reprovados", 0)))[:80])}
    write_json(SAIDA, res)
    return {"aprovados": n_pos, "reprovados": n_neg, "positivos_promovidos": len(promov_pos), "vetos_promovidos": len(promov_veto), "candidatos": len(cand)}


def termos_aprendidos() -> tuple[list[str], list[str]]:
    if not SAIDA.exists():
        return [], []
    d = load_json(SAIDA)
    return list(d.get("positivos", {})), list(d.get("vetos", {}))


if __name__ == "__main__":
    print(json.dumps(aprender(), ensure_ascii=False, indent=2))
