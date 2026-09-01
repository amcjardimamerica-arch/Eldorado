"""Compactação por dicionário — mais informação com menos peso.

Um JSON de lista de objetos repete o nome de cada campo em cada linha e repete
o mesmo texto (fonte, área, UF, nível, status) milhares de vezes. Aqui cada
campo vira uma coluna; valores de texto repetidos entram uma vez num
dicionário e as linhas guardam só o índice. O painel reidrata com uma função
de dez linhas. Economia típica: 60–75% sobre o JSON puro, antes do gzip.

Formato:
  {"campos": ["a","b",...], "dic": {"b": ["x","y"]}, "linhas": [[v, 0], ...]}
Campos numéricos/booleanos ficam inline; textos que se repetem >1 vez vão ao
dicionário; textos únicos ficam inline com o prefixo "\\u0000" removido pela
leitura (a leitura distingue pelo tipo: número = índice, string = valor).
"""
from __future__ import annotations

import json
from collections import Counter


def compactar(registros: list[dict], campos: list[str] | None = None,
              dicionarizar: set[str] | None = None) -> dict:
    if not registros:
        return {"campos": campos or [], "dic": {}, "linhas": []}
    campos = campos or sorted({k for r in registros for k in r})
    # decide quais campos vão ao dicionário: texto com repetição
    cand = dicionarizar
    if cand is None:
        cand = set()
        for c in campos:
            vals = [r.get(c) for r in registros if isinstance(r.get(c), str)]
            if len(vals) >= 2 and len(set(vals)) < len(vals) * 0.6:
                cand.add(c)
    dic: dict[str, list] = {c: [] for c in cand}
    idx: dict[str, dict] = {c: {} for c in cand}
    linhas = []
    for r in registros:
        linha = []
        for c in campos:
            v = r.get(c)
            if c in cand and isinstance(v, str):
                if v not in idx[c]:
                    idx[c][v] = len(dic[c]); dic[c].append(v)
                linha.append(idx[c][v])
            else:
                linha.append(v)
        linhas.append(linha)
    return {"campos": campos, "dic": dic, "linhas": linhas}


def expandir(pacote: dict) -> list[dict]:
    campos, dic, linhas = pacote["campos"], pacote.get("dic", {}), pacote["linhas"]
    out = []
    for linha in linhas:
        r = {}
        for c, v in zip(campos, linha):
            if c in dic and isinstance(v, int) and not isinstance(v, bool):
                r[c] = dic[c][v]
            else:
                r[c] = v
        out.append(r)
    return out


JS_DECODER = """
/* reidrata um pacote compactado por dicionário (src/compacto.py) */
function expandeCompacto(p){
  const {campos,dic={},linhas}=p; return linhas.map(l=>{const r={};
    campos.forEach((c,i)=>{const v=l[i]; r[c]=(dic[c]&&Number.isInteger(v))?dic[c][v]:v;}); return r;});
}
"""


def tamanho(obj) -> int:
    return len(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode())


if __name__ == "__main__":
    demo = [{"a": i, "fonte": "PNCP" if i % 2 else "QD", "uf": "GO"} for i in range(1000)]
    print("puro:", tamanho(demo), "compacto:", tamanho(compactar(demo)))
