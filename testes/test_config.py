import pytest

from eldorado.base.nucleo.config import ConfiguracaoInvalida, carregar


def test_configuracao_do_repositorio_e_valida():
    c = carregar("config/eldorado.toml")
    assert c.limites.carga_maxima == 0.85 and c.limites.tentativas_por_ferramenta == 3


def test_arquivo_ausente_usa_os_padroes(tmp_path):
    assert carregar(tmp_path / "nao-existe.toml").missao.ativa == "oportunidades"


@pytest.mark.parametrize("conteudo", ['chave_inventada = 1', '[limites]\ncarga_maxima = 1.5', '[limites]\ntentativas_por_ferramenta = 4',
                                      '[limites]\nretencao_temporario_dias = 31', 'nome = "  "'])
def test_configuracao_invalida_impede_a_passagem(tmp_path, conteudo):
    p = tmp_path / "c.toml"
    p.write_text(conteudo)
    with pytest.raises(ConfiguracaoInvalida):
        carregar(p)
