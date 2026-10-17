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
    # 17/10: amostra dos achados fora dos livros (DOU e pilotos)
    "Ministério do Esporte — EXTRATO DE TERMO DE FOMENTO — Implementação e Desenvolvimento do Projeto",
    "MMA (meio ambiente) — EXTRATO DE TERMO ADITIVO",
    "Ministério do Esporte — EXTRATO DE PRORROGAÇÃO DE OFÍCIO",
    "Prefeitura de Campo Alegre de Goiás — EXTRATO DE DISTRATO",
    "SEDS-GO / Goiás Social — Extrato_aditivo_201910319003401",
    "Edital de convocacao de assembleia geral",
    "Bazar beneficente Missão Vida em Anápolis nos dias 3 e 4 de julho",
    "MDS (desenvolvimento e assistência social) — EXTRATO DE FOMENTO Nº 7AAEKP/2026 — Fortalecer e qualificar",
    "MDS (desenvolvimento e assistência social) — EXTRATO DE COLABORAÇÃO — O objeto do presente Termo",
    "Ministério do Esporte — EXTRATOS DE TERMOS DE COMPROMISSO — Estabelecer as obrigações",
    "Coordenadoria Estadual em Sergipe — aviso de dispensa de chamamento público",
    "MCTI (ciência e tecnologia) — resultado de julgamento",
    "Prefeitura de Goiânia — Parceria celebrada no âmbito da Secretaria Municipal de Governo",
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
    "Mosaic abre inscrições para o Edital da Água 2026 com foco em eficiência no uso da água",
    "Edital Fundo Canadá Para Iniciativas Locais (Fcil) - Brasil (2026-2027)",
    "Fundação financia projetos em saúde e educação com valor de até R$100 mil",
    "Aberta Chamada de Projetos 2026 no Instituto Mahle",
    "Zurich abre edital nacional para apoiar projetos sociais via leis de incentivo",
    "Prefeitura de Goiânia — Edital nº 1/2026",
    "5ª edição do Edital de Apoio à Filantropia Comunitária",
]


class PortaoCasosReais(unittest.TestCase):
    def test_barra_o_ruido(self):
        for t in BARRAR:
            self.assertIsNotNone(M({"titulo": t, "uf": "GO"}), t)

    def test_deixa_passar_a_oportunidade(self):
        for t in PASSAR:
            self.assertIsNone(M({"titulo": t, "uf": "GO"}), t)
