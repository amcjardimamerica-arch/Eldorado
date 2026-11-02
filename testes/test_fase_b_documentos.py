"""Trava da fase B do expurgo (titular, 02/11/2026): só sai o que não é real nem utilizável; nada real vai embora às cegas."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("fase_b", Path(__file__).parents[1] / "implantar/fase_b_documentos_2026_11_02.py")
fb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fb)


def test_o_ano_nao_e_o_numero_do_edital_e_pasta_generica_nao_vincula():
    assert fb.chave("https://www.gov.br/funarte/pt-br/editais/2024/premio-x/anexo.pdf") is None
    assert fb.chave("https://data.queridodiario.ok.org.br/5208707/2026-10-29/abc.pdf#ato-3") is None
    assert fb.chave("https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/publicacoes_ver_conteudo/752566") is None
    assert fb.chave("https://mapa.cultura.gov.br/oportunidade/11685/#info") == "mapa.cultura.gov.br/oportunidade/11685"
    assert fb.chave("https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-30-2026/Anexo_II.pdf") \
        == "gov.br/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-30-2026".replace("gov.br/", "gov.br/cnpq/", 1)


def test_sinal_de_oportunidade_vigente_vai_ao_chrome_e_nao_ao_expurgo():
    assert fb.tem_sinal("https://captadores.org.br/editais/zurich-seguros-abre-edital-nacional")
    assert fb.tem_sinal("https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-741126435")
    assert not fb.tem_sinal("https://www.fundobrasil.org.br/edital/edital-anual-2017-combate")
    assert not fb.tem_sinal("https://senadorcanedo.go.gov.br/sistema-de-escrita-fiscal-atualizado")


def test_lixo_comprovado_e_so_o_que_o_sistema_ja_decidiu_ou_e_encerrado():
    assert fb.lixo_comprovado("https://gazetadoestado.com.br/tag/edital-de-protesto", set())
    assert fb.lixo_comprovado("https://x.gov.br/resultado-final-2024.pdf", set())
    assert fb.lixo_comprovado("https://y.org/qualquer", {"https://y.org/qualquer"})
    assert not fb.lixo_comprovado("https://x.gov.br/resultado-parcial-2026.pdf", set())
