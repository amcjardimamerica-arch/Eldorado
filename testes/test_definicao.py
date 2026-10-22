import pytest

from eldorado.base.fluxo.definicao import WorkflowInvalido, carregar, de_dicionario

NO = "eldorado.base.fluxo.nos:passar"


def wf(nos, conexoes=()):
    return {"workflow": {"id": "w"}, "no": nos, "conexao": list(conexoes)}


def test_workflow_do_repositorio_e_valido():
    d = carregar("workflows/manutencao.toml")
    assert d.ordem() == ["maquina", "aplicar"] and len(d.versao) == 16


def test_versao_e_estavel_e_muda_com_o_conteudo():
    a = de_dicionario(wf([{"id": "a", "tipo": NO}]))
    b = de_dicionario(wf([{"id": "a", "tipo": NO}]))
    c = de_dicionario(wf([{"id": "a", "tipo": NO, "tentativas": 2}]))
    assert a.versao == b.versao != c.versao


@pytest.mark.parametrize("dados,erro", [
    (wf([{"id": "a", "tipo": NO}, {"id": "a", "tipo": NO}]), "repetidos"),
    (wf([{"id": "a", "tipo": NO}], [{"de": "a", "para": "x"}]), "inexistente"),
    (wf([{"id": "a", "tipo": NO}, {"id": "b", "tipo": NO}], [{"de": "a", "para": "b"}, {"de": "b", "para": "a"}]), "ciclo"),
    (wf([{"id": "a", "tipo": NO, "tentativas": 4}]), "1 a 3"),
    (wf([{"id": "a", "tipo": NO, "tentativas": 2, "esperas_s": [1, 2]}]), "esperas"),
    (wf([{"id": "a", "tipo": "eldorado.nao_existe:x"}]), "não encontrada"),
    (wf([{"id": "a", "tipo": "sem_dois_pontos"}]), "modulo:funcao"),
    (wf([{"id": "a", "tipo": NO, "chave_inventada": 1}]), "desconhecidas"),
    (wf([]), "não tem nós"),
    ({"no": [{"id": "a", "tipo": NO}]}, "id"),
    (wf([{"id": "a", "tipo": NO}], [{"de": "a", "para": "a"}]), "si mesmo"),
    (wf([{"id": "a", "tipo": NO}, {"id": "b", "tipo": NO}], [{"de": "a", "para": "b", "saida": "outra"}]), "saída"),
])
def test_definicoes_invalidas_sao_recusadas(dados, erro):
    with pytest.raises(WorkflowInvalido, match=erro):
        de_dicionario(dados)


def test_no_com_dados_fixos_nao_exige_funcao_importavel():
    d = de_dicionario(wf([{"id": "a", "tipo": "eldorado.nao_existe:x", "fixo": [{"a": 1}]}]))
    assert d.no("a").fixo == ({"a": 1},)
