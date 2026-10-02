"""PREPARAÇÃO DOS EDITAIS DE FLUXO PERMANENTE (titular, 02/10/2026) — orientação no Farol de Alexandria.

Os livros de editais em fluxo contínuo ou recorrente recebem a organização da preparação: os documentos-base do MROSC,
o que é específico do edital, o roteiro do projeto-base e os passos. Os três validados no parecer das 238 (SEDS/GO,
iCS e MPT/PRT-18) têm preparação própria; os demais livros de inscrição contínua recebem o modelo geral.
Parâmetros: config/preparacao_fluxos.json · saída para o Farol: docs/dados/preparacao_farol.json
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
CFG = ROOT / "config/preparacao_fluxos.json"
FAROL = ROOT / "docs/dados/preparacao_farol.json"


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def run(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    cfg = _j(CFG, {}); C = _j(CAT, {}); proprios = cfg.get("livros") or {}
    base = {"documentos_base": (cfg.get("documentos_base_mrosc") or {}).get("itens") or [],
            "fundamento": (cfg.get("documentos_base_mrosc") or {}).get("fundamento"), "projeto_base_roteiro": cfg.get("projeto_base_roteiro") or []}
    farol, n_prop, n_geral = [], 0, 0
    for x in C.get("motores") or []:
        if x.get("papel") == "fonte_de_busca" or (x.get("qualificacao") or {}).get("veredito") == "NÃO APLICA":
            continue
        p = proprios.get(x.get("id"))
        if p:
            x["preparacao"] = {**base, **p, "modelo": "próprio", "atualizada_em": hoje.isoformat()}; n_prop += 1
        elif x.get("regime_inscricao") == "contínuo":
            x["preparacao"] = {**base, "tipo": "fluxo contínuo", "modelo": "geral", "atualizada_em": hoje.isoformat(),
                               "especificos": ["Conferir no edital vigente os documentos e formulários próprios"]}; n_geral += 1
        else:
            if (x.get("preparacao") or {}).get("modelo") == "geral":
                x.pop("preparacao", None)
            continue
        farol.append({"livro": x["id"], "nome": x.get("nome_classificado"), "geo": x.get("geo"), "modelo": x["preparacao"]["modelo"],
                      "edital": x["preparacao"].get("edital"), "janela": x["preparacao"].get("janela"), "passos": x["preparacao"].get("passos")})
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    farol.sort(key=lambda f: (f["modelo"] != "próprio", f["geo"] != "GO", str(f["nome"])))
    FAROL.write_text(json.dumps({"gerado_em": hoje.isoformat(), "regra": __doc__.split("Parâmetros")[0].strip(), "documentos_base": base["documentos_base"],
                                 "projeto_base_roteiro": base["projeto_base_roteiro"], "livros": farol}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"preparacao_propria": n_prop, "preparacao_geral": n_geral}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
