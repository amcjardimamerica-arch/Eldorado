import pytest

from eldorado.base.nucleo.eventos import CATALOGO, Diario, EventoInvalido, criar, ler


def test_tipo_fora_do_catalogo_e_recusado():
    with pytest.raises(EventoInvalido):
        criar("livro.apagado", "teste", {})


def test_evento_exige_modulo_e_dados_em_dicionario():
    with pytest.raises(EventoInvalido):
        criar("livro.criado", "", {})
    with pytest.raises(EventoInvalido):
        criar("livro.criado", "teste", [1, 2])


def test_diario_preserva_a_ordem_de_criacao(tmp_path):
    d = Diario(tmp_path)
    ids = [d.emitir("maquina.leitura", "teste", {"em": str(i)}).id for i in range(200)]
    assert [e.id for e in ler(tmp_path)] == ids


def test_linha_corrompida_nao_e_ignorada(tmp_path):
    d = Diario(tmp_path)
    d.emitir("maquina.leitura", "teste", {"em": "1"})
    with open(d.arquivo, "ab") as f:
        f.write(b'{"quebrado": \n')
    with pytest.raises(EventoInvalido, match="linha 2"):
        list(ler(tmp_path))


def test_todo_alvo_do_catalogo_aponta_para_um_banco_conhecido():
    for tipo, alvos in CATALOGO.items():
        for a in alvos:
            assert a.banco in ("biblioteca", "especial", "cerebro", "*"), tipo
