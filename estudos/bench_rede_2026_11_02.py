"""Benchmark da rede neural do Cérebro (titular, 02/11/2026): para cada pergunta (oportunidade, ação, motor), compara
configurações do aprendizado contínuo em ordem cronológica e prequencial (prevê antes de aprender): o otimizador e a taxa,
a regularização L2 e o limiar de decisão (escolhido nos primeiros 70% dos casos, medido nos 30% mais recentes).
Uso: python estudos/bench_rede_2026_11_02.py [dados]"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from river import linear_model, metrics, optim

import eldorado.base.cerebro.lote as lote_mod
from eldorado.base.cerebro.rede import RedeNeural

CASOS: list = []


def _captura(rede, casos):
    CASOS.extend(casos)
    return {}


def casos(dados: Path) -> dict[str, list]:
    lote_mod.comparar_e_ligar = _captura
    b = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    c = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    RedeNeural.treinar(b, c)
    out: dict[str, list] = {}
    for _em, p, x, y in CASOS:
        out.setdefault(p, []).append((x, y))
    return out


def rodar(cs: list, otim, l2: float = 0.0) -> dict:
    m = linear_model.LogisticRegression(optimizer=otim, l2=l2)
    auc, ps, ys = metrics.ROCAUC(), [], []
    for x, y in cs:
        p = m.predict_proba_one(x).get(True, 0.5)
        auc.update(y, p)
        ps.append(p)
        ys.append(y)
        m.learn_one(x, y)
    n = len(ys)
    corte = int(n * 0.7)
    brier = sum((p - y) ** 2 for p, y in zip(ps, ys, strict=True)) / n
    # o limiar: o que maximiza F1 nos primeiros 70%; medido nos 30% mais recentes
    def prf(lim, a, b):
        tp = sum(1 for p, y in zip(ps[a:b], ys[a:b], strict=True) if p >= lim and y)
        fp = sum(1 for p, y in zip(ps[a:b], ys[a:b], strict=True) if p >= lim and not y)
        fn = sum(1 for p, y in zip(ps[a:b], ys[a:b], strict=True) if p < lim and y)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rv = tp / (tp + fn) if tp + fn else 0.0
        return pr, rv, (2 * pr * rv / (pr + rv) if pr + rv else 0.0)
    lims = [i / 100 for i in range(5, 96, 5)]
    melhor = max(lims, key=lambda t: prf(t, 0, corte)[2])
    p05, r05, f05 = prf(0.5, corte, n)
    pl, rl, fl = prf(melhor, corte, n)
    return {"auc": round(auc.get(), 4), "brier": round(brier, 4), "p@0.5": round(p05, 3), "r@0.5": round(r05, 3), "f1@0.5": round(f05, 3),
            "limiar": melhor, "p@lim": round(pl, 3), "r@lim": round(rl, 3), "f1@lim": round(fl, 3)}


CONFIGS = {
    "atual: SGD 0.1": (lambda: optim.SGD(0.1), 0.0),
    "SGD 0.05": (lambda: optim.SGD(0.05), 0.0),
    "SGD 0.02": (lambda: optim.SGD(0.02), 0.0),
    "SGD 0.2": (lambda: optim.SGD(0.2), 0.0),
    "SGD 0.05 + L2 1e-4": (lambda: optim.SGD(0.05), 1e-4),
    "SGD 0.1 + L2 1e-3": (lambda: optim.SGD(0.1), 1e-3),
    "Adam 0.01": (lambda: optim.Adam(0.01), 0.0),
    "Adam 0.03": (lambda: optim.Adam(0.03), 0.0),
    "Adam 0.01 + L2 1e-4": (lambda: optim.Adam(0.01), 1e-4),
    "AdaGrad 0.1": (lambda: optim.AdaGrad(0.1), 0.0),
    "AdaGrad 0.3": (lambda: optim.AdaGrad(0.3), 0.0),
}

if __name__ == "__main__":
    dados = Path(sys.argv[1] if len(sys.argv) > 1 else "dados")
    cs = casos(dados)
    res = {}
    for perg, lst in cs.items():
        res[perg] = {"casos": len(lst), "positivos": sum(1 for _, y in lst if y)}
        for nome, (o, l2) in CONFIGS.items():
            res[perg][nome] = rodar(lst, o(), l2)
    print(json.dumps(res, ensure_ascii=False, indent=1))
