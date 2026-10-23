"""A IA com saída validada (pydantic-ai) e a otimização das instruções (DSPy): a IA propõe, o sistema valida."""
import json

import pytest

from eldorado.base.nucleo import ia as I

PAGINAS = ["Edital de Fomento 2026. As inscrições vão de 10/10/2026 até 30/11/2026. O valor total é de R$ 1,5 milhão."]


def test_saida_validada_aceita_o_trecho_verdadeiro_e_recusa_o_inventado(tmp_path, monkeypatch):
    pytest.importorskip("pydantic_ai")
    from pydantic_ai.models.test import TestModel
    monkeypatch.setenv("ELDORADO_DADOS", str(tmp_path))
    proposta = {"itens": [{"item": "Prazo de inscrição", "valor": "30/11/2026", "trecho": "até 30/11/2026", "pagina": 1},
                          {"item": "Valor", "valor": "R$ 9 milhões", "trecho": "o valor total é de R$ 9 milhões", "pagina": 1}]}
    ia = I.IA(url="http://127.0.0.1:9")
    ia._modelo_validado = TestModel(custom_output_args=proposta)
    aceitos, uso = I.comprovar(ia, ["Prazo de inscrição", "Valor"], PAGINAS, "Edital de Fomento 2026", ("Prazo de inscrição", "Valor"))
    assert list(aceitos) == ["Prazo de inscrição"] and aceitos["Prazo de inscrição"]["trecho"] == "até 30/11/2026"
    assert any("não existe" in r for r in uso.recusas)                                              # o inventado, recusado


def test_otimizacao_escolhe_exemplos_pela_regra_do_sistema(tmp_path):
    dspy = pytest.importorskip("dspy")
    from dspy.utils import DummyLM

    from eldorado.motores.pilotos import otimizacao as O
    exemplos = [{"titulo": f"Edital {i}", "item": "Valor", "valor": f"R$ {i}0 mil", "trecho": f"O valor é de R$ {i}0 mil por projeto selecionado."} for i in range(1, 5)]
    respostas = [{"valor": e["valor"], "trecho": e["trecho"]} for e in exemplos] * 3
    saida = tmp_path / "ex.json"
    escolhidos = O.compilar(exemplos, lm=DummyLM(respostas), saida=saida, maximo=3)
    assert 1 <= len(escolhidos) <= 3 and json.loads(saida.read_text())[0]["item"] == "Valor"
    assert "Exemplos de comprovação correta" in O.exemplos_para_instrucao(saida) and dspy is not None
