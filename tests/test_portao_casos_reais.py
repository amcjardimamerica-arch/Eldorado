"""Portão com BATERIA DE CASOS REAIS (titular, 17/10/2026): ruídos que passaram e oportunidades que foram barradas por
engano. Cada regra nova do portão precisa manter os dois lados."""
import unittest

from src.porta_oportunidade import motivo_para_nao_guardar as M

BARRAR = [
    "Chamamento público para prospecção do mercado imobiliário em Caieiras/SP, visando locação",
    "Chamamento Público visando nova prospecção de imóvel para locação na cidade de Palmas",
    "CHAMAMENTO PÚBLICO, tem como objeto cadastrar empresas sediadas no Estado de Rondônia",
    "Credenciamento de empresas especializadas na prestação de serviços de administração de benefícios",
    "CREDENCIAMENTO PÚBLICO, com o objetivo de realizar a Aquisição de Gêneros Alimentícios",
    "O CREDENCIAMENTO DE PRESTAÇÃO DE SERVIÇOS DE MÃO DE OBRA DE TORNEIRO E SOLDADOR",
    "SELEÇÃO PÚBLICA, MEDIANTE CHAMAMENTO PÚBLICO, DE EMPRESAS PARA CONCESSÃO DE INCENTIVOS FISCAIS",
    "Prestação de Contas de Auxílio Financeiro",
    "Chamamento para contrato de gestão de unidade de saúde por Organização Social",
]
PASSAR = [
    "BNDES abre edital de R$ 35 milhões para fortalecer organizações sociais do Nordeste",
    "Movimento Bem Maior abre edital com apoio de até R$ 100 mil para organizações sociais",
    "Emenda Parlamentar — Câmara e Senado — captação 2026",
    "SERVICO DE LIMPEZA URBANA — Credenciamento de Cooperativas/Associações de Catadores",
    "Política Nacional Aldir Blanc - PNAB Goiás - fomento a pontos de cultura",
    "Chamada pública para selecionar Organização da Sociedade Civil para a execução de projeto",
    "Fundação FEAC abre edital para projetos sociais",
    "Credenciamento de instituição especializada, preferencialmente Organização da Sociedade Civil",
]


class PortaoCasosReais(unittest.TestCase):
    def test_barra_o_ruido(self):
        for t in BARRAR:
            self.assertIsNotNone(M({"titulo": t, "uf": "GO"}), t)

    def test_deixa_passar_a_oportunidade(self):
        for t in PASSAR:
            self.assertIsNone(M({"titulo": t, "uf": "GO"}), t)
