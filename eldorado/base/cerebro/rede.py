"""A rede neural única, de aprendizado contínuo (River): aprende a cada veredito e dá as notas.

Avaliação honesta (prequencial): para cada caso, primeiro prevê, depois aprende; as métricas medem o acerto
antes de a rede ver a resposta. O modelo fica fora do Git (dados/modelo); o Cérebro guarda as métricas de cada versão.
"""
from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Any

from river import linear_model, metrics, optim

from ..nucleo.eventos import Diario, agora

PALAVRA = re.compile(r"[a-zà-ú]{4,}")


def caracteristicas(item: dict[str, Any]) -> dict[str, float]:
    f: dict[str, float] = {"vies": 1.0}
    for campo in ("motor", "uf", "tema", "orgao"):
        v = item.get(campo) or (item.get("dados") or {}).get(campo)
        if v:
            f[f"{campo}={str(v).lower()[:40]}"] = 1.0
    f["tem_link_oficial"] = 1.0 if item.get("link_oficial") else 0.0
    f["pista"] = 1.0 if item.get("pista") else 0.0
    for p in sorted(set(PALAVRA.findall(str(item.get("titulo") or "").lower())))[:25]:
        f[f"p={p}"] = 1.0
    return f


class Rede:
    def __init__(self):
        self.modelo = linear_model.LogisticRegression(optimizer=optim.SGD(0.1))
        self.discernimento = metrics.ROCAUC()
        self.precisao = metrics.Precision()
        self.revocacao = metrics.Recall()
        self.amostras = 0

    def nota(self, item: dict[str, Any]) -> float:
        return float(self.modelo.predict_proba_one(caracteristicas(item)).get(True, 0.5))

    def aprender(self, item: dict[str, Any], valido: bool) -> float:
        x = caracteristicas(item)
        p = self.modelo.predict_proba_one(x)
        self.discernimento.update(valido, p)
        self.precisao.update(valido, p.get(True, 0.0) >= 0.5)
        self.revocacao.update(valido, p.get(True, 0.0) >= 0.5)
        self.modelo.learn_one(x, valido)
        self.amostras += 1
        return p.get(True, 0.5)

    def metricas(self) -> dict[str, float | None]:
        if not self.amostras:
            return {"discernimento": None, "precisao": None, "revocacao": None}
        return {"discernimento": round(float(self.discernimento.get()), 4), "precisao": round(float(self.precisao.get()), 4),
                "revocacao": round(float(self.revocacao.get()), 4)}

    def salvar(self, pasta: str | Path, diario: Diario | None = None) -> Path:
        p = Path(pasta)
        p.mkdir(parents=True, exist_ok=True)
        versao = f"{self.amostras:07d}-{agora().replace(':', '').replace('-', '')[:15]}"
        arq = p / f"rede-{versao}.pkl"
        arq.write_bytes(pickle.dumps(self))
        (p / "rede-atual.txt").write_text(arq.name)
        if diario:
            diario.emitir("modelo.treinado", "rede", {"versao": versao, "treinado_em": agora(), "arquivo": arq.name, **self.metricas()})
        return arq

    @classmethod
    def carregar(cls, pasta: str | Path) -> "Rede":
        p = Path(pasta)
        atual = p / "rede-atual.txt"
        if not atual.exists():
            return cls()
        return pickle.loads((p / atual.read_text().strip()).read_bytes())
