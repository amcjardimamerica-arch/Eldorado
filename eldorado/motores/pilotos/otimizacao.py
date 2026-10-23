"""A otimização das instruções dos pilotos (plano C: DSPy): a partir das certidões já validadas no banco (o item, o
valor e o trecho literal do documento), o DSPy escolhe os exemplos que melhor ensinam o modelo local a comprovar; os
exemplos compilados entram nas instruções do Interceptador. A métrica é a regra do sistema: o trecho proposto tem de
existir no documento e o valor tem de bater.

    eldorado ia otimizar     (no fluxo da IA, onde o modelo local roda)
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

ARQUIVO = Path(os.environ.get("ELDORADO_DADOS", "dados")) / "ia" / "exemplos_comprovar.json"


def exemplos_validados(biblioteca: sqlite3.Connection, limite: int = 60) -> list[dict]:
    """As certidões comprovadas com trecho literal: o item, o valor, o trecho e o título do livro."""
    sql = ("SELECT l.titulo, c.item, c.valor, c.trecho FROM certidao c JOIN livro l ON l.id = c.livro_id WHERE c.situacao = 'comprovado' "
           "AND length(c.trecho) BETWEEN 30 AND 400 AND c.valor IS NOT NULL ORDER BY c.em DESC LIMIT ?")
    return [{"titulo": t, "item": i, "valor": v, "trecho": tr} for t, i, v, tr in biblioteca.execute(sql, (limite,))]


def compilar(exemplos: list[dict], lm=None, saida: Path = ARQUIVO, maximo: int = 6) -> list[dict]:
    """O DSPy (BootstrapFewShot) escolhe os exemplos que o modelo acerta pela regra do sistema; grava os escolhidos."""
    import dspy

    from ...base.nucleo.ia import trecho_existe

    class ComprovarItem(dspy.Signature):
        """Do trecho de um edital, extrair o valor do item pedido, copiando o trecho literal que o comprova."""
        titulo: str = dspy.InputField()
        documento: str = dspy.InputField()
        item: str = dspy.InputField()
        valor: str = dspy.OutputField()
        trecho: str = dspy.OutputField()

    def metrica(ex, pred, trace=None) -> bool:
        return trecho_existe(pred.trecho or "", ex.documento) and ex.valor.lower()[:20] in (pred.valor or "").lower() + ex.documento.lower()
    if lm is not None:
        dspy.configure(lm=lm)
    treino = [dspy.Example(titulo=e["titulo"], documento=e["trecho"], item=e["item"], valor=e["valor"], trecho=e["trecho"])
              .with_inputs("titulo", "documento", "item") for e in exemplos]
    otimizador = dspy.BootstrapFewShot(metric=metrica, max_bootstrapped_demos=maximo, max_labeled_demos=maximo)
    programa = otimizador.compile(dspy.Predict(ComprovarItem), trainset=treino)
    escolhidos = [{"titulo": d.titulo, "item": d.item, "valor": d.valor, "trecho": d.trecho} for d in programa.demos][:maximo]
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(escolhidos, ensure_ascii=False, indent=1), encoding="utf-8")
    return escolhidos


def exemplos_para_instrucao(arquivo: Path = ARQUIVO) -> str:
    """Os exemplos compilados, em texto, para o começo do pedido do Interceptador ('' se ainda não houver)."""
    if not arquivo.exists():
        return ""
    ex = json.loads(arquivo.read_text(encoding="utf-8"))
    if not ex:
        return ""
    linhas = [f'- item "{e["item"]}": valor "{e["valor"]}"; trecho literal: "{e["trecho"]}"' for e in ex]
    return "Exemplos de comprovação correta (valor e trecho copiado do documento):\n" + "\n".join(linhas) + "\n\n"
