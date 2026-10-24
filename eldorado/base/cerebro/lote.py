"""Os modelos em lote do Cérebro (plano C: scikit-learn): para cada pergunta da rede, um modelo treinado com o histórico
inteiro e medido em ordem cronológica, treinando com o passado e testando no futuro (o mesmo discernimento, a área sob a
curva ROC); o Cérebro usa, em cada pergunta, o que discernir melhor: o aprendizado contínuo (river) ou o lote. Com
poucos casos (ou uma classe só), fica o contínuo."""
from __future__ import annotations

from typing import Any

MINIMO = 40


class Lote:
    def __init__(self, pipeline, discernimento: float, amostras: int):
        self.pipeline, self.discernimento, self.amostras = pipeline, discernimento, amostras

    def nota(self, x: dict[str, float]) -> float:
        return float(self.pipeline.predict_proba([x])[0][1])


def treinar(xs: list[dict[str, float]], ys: list[bool]) -> Lote | None:
    if len(xs) < MINIMO or len(set(ys)) < 2 or min(ys.count(True), ys.count(False)) < 5:
        return None
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.pipeline import make_pipeline
    # esparso e linear: rápido o bastante para reaprender a cada batimento (as árvores densas levavam 160 s com 3.296 casos)
    pipe = make_pipeline(DictVectorizer(sparse=True), LogisticRegression(C=2.0, max_iter=600, class_weight="balanced", solver="lbfgs"))
    # lbfgs: o liblinear recusa as matrizes esparsas com índices de 64 bits que os dados reais produzem (24/10/2026)
    # em ordem cronológica (os casos chegam ordenados): treina com o passado e testa no futuro, em janelas, a mesma condição
    # em que o contínuo é medido; embaralhar deixaria o lote ver o futuro e o favoreceria injustamente
    import numpy as np
    reais, prev = [], []
    for treino, teste in TimeSeriesSplit(n_splits=5).split(xs):
        yt = [ys[i] for i in treino]
        if len(set(yt)) < 2:
            continue
        pipe.fit([xs[i] for i in treino], yt)
        prev += list(pipe.predict_proba([xs[i] for i in teste])[:, 1])
        reais += [ys[i] for i in teste]
    if len(set(reais)) < 2:
        return None
    auc = float(roc_auc_score(reais, np.array(prev)))
    pipe.fit(xs, ys)
    return Lote(pipe, round(auc, 4), len(xs))


def comparar_e_ligar(rede, casos: list[tuple[str, str, dict[str, float], bool]]) -> dict[str, Any]:
    """Treina o lote de cada pergunta com os mesmos casos da rede e liga o que discernir melhor."""
    relato: dict[str, Any] = {}
    for pergunta in rede.PERGUNTAS:
        xs = [x for _, p, x, _ in casos if p == pergunta]
        ys = [bool(v) for _, p, _, v in casos if p == pergunta]
        try:
            lote = treinar(xs, ys)
        except ImportError:
            relato[pergunta] = {"lote": "scikit-learn ausente"}
            continue
        continuo = rede.p[pergunta].metricas().get("discernimento")
        if lote is None:
            relato[pergunta] = {"lote": "poucos casos", "continuo": continuo}
            continue
        usa = continuo is None or lote.discernimento > continuo
        rede.p[pergunta].lote = lote if usa else None
        relato[pergunta] = {"lote": lote.discernimento, "continuo": continuo, "usa": "lote" if usa else "contínuo", "amostras": lote.amostras}
    return relato
