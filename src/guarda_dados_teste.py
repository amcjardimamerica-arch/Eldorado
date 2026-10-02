"""GUARDA CONTRA DADOS DE TESTE (02/10/2026).

Um teste gravava fichas FALSAS na Biblioteca real (página x.gov.br, prazo 2099, valor "R$ 100 mil") e o fluxo de produção,
que rodava a suíte sobre os dados reais, as publicava. A causa foi corrigida (testes numa cópia isolada; o teste não grava
mais fora da pasta temporária); esta guarda roda a cada ciclo e retira o que tiver domínio de teste — nada de dado real é
tocado: só entradas cujo endereço é de domínio reservado a teste.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMINIO_TESTE = re.compile(r"https?://(x\.gov\.br|x\.go\.gov\.br|teste\.go\.gov\.br|example\.(com|org)|exemplo\.com\.br|exemplo\.com)(/|$)", re.I)


def e_teste(u) -> bool:
    return bool(DOMINIO_TESTE.search(str(u or "")))


def limpar_catalogo(C: dict) -> dict:
    n_hist = n_livros = 0; removidos = []
    for x in C.get("motores") or []:
        h0 = x.get("historico") or []
        h1 = [h for h in h0 if not (isinstance(h, dict) and e_teste(h.get("pagina_oficial")))]
        n_hist += len(h0) - len(h1)
        x["historico"] = h1
    fica = []
    for x in C.get("motores") or []:
        if e_teste(x.get("pagina")) and not any(isinstance(h, dict) and h.get("pagina_oficial") and not e_teste(h.get("pagina_oficial")) for h in x.get("historico") or []):
            removidos.append(x.get("id")); n_livros += 1
            continue
        if e_teste(x.get("pagina")):
            x["pagina"] = next(h["pagina_oficial"] for h in x["historico"] if isinstance(h, dict) and h.get("pagina_oficial") and not e_teste(h["pagina_oficial"]))
        fica.append(x)
    C["motores"] = fica
    if removidos:
        C.setdefault("removidos_por_dado_de_teste", []).extend(removidos)
    return {"entradas_de_historico": n_hist, "livros_falsos": n_livros, "ids": removidos}


def limpar_arquivos(ids: list[str] | None = None) -> dict:
    fichas = 0
    for f in (ROOT / "biblioteca_alexandria/oportunidades").glob("*/*/ficha.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if e_teste(d.get("pagina_oficial")) or e_teste(d.get("url")):
            f.unlink(); fichas += 1
            for p in (f.parent, f.parent.parent):
                try:
                    p.rmdir()
                except OSError:
                    pass
    extr = 0
    for i in ids or []:
        for f in (ROOT / "dados/editais/extraidos").glob(f"*{i}*.json"):
            f.unlink(); extr += 1
    val = 0
    for f in (ROOT / "dados/oportunidades/validacao_mapa").glob("validacao_*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        its = d.get("itens") or []
        bons = [i for i in its if not e_teste(i.get("url"))]
        if len(bons) != len(its):
            val += len(its) - len(bons); d["itens"] = bons
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"fichas_falsas": fichas, "extracoes": extr, "itens_de_validacao": val}


def run() -> dict:
    cat = ROOT / "biblioteca_alexandria/fontes/motores.json"
    C = json.loads(cat.read_text(encoding="utf-8"))
    r = limpar_catalogo(C)
    if r["entradas_de_historico"] or r["livros_falsos"]:
        cat.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    ids = r["ids"] + ["op-93e731ebaa16", "op-c54ee31645b5"]
    return {**r, **limpar_arquivos(ids)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
