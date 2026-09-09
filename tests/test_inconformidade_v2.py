"""Famílias de inconformidade aprendidas na verificação de 09/09/2026.

Os textos deste arquivo são objetos reais, copiados da API oficial de consulta
do PNCP e das páginas oficiais dos patrocinadores. Cada teste guarda um caso
que o filtro antigo deixava passar — ou, no sentido inverso, um caso que o
filtro novo não pode barrar.
"""
import unittest

from src.inconformidade import avaliar, avaliar_item


def familia(texto):
    return avaliar(texto)["familia"]


def veredito(texto):
    r = avaliar(texto)
    if not r["ok"]:
        return "reprovado"
    return "atencao" if r["atencao"] else "aprovado"


class ServicoAoOrgao(unittest.TestCase):
    """A família grande: 116 dos 317 objetos lidos no PNCP nesta rodada."""

    def test_consulta_e_exame_com_ou_sem_fins_lucrativos(self):
        # Itajaí/SC. A frase "com ou sem fins lucrativos" era o que fazia o
        # registro passar pelo filtro antigo.
        t = ("CREDENCIAMENTO PARA EMPRESAS, COM OU SEM FINS LUCRATIVOS, ESPECIALIZADAS PARA "
             "REALIZAÇÃO DE CONSULTAS E EXAMES ELETIVOS DE MÉDIA COMPLEXIDADE, ATENDENDO AS "
             "DEMANDAS DA SECRETARIA MUNICIPAL DE SAÚDE DE ITAJAÍ")
        self.assertEqual(familia(t), "servico_ao_orgao")

    def test_complementar_ao_sus_com_entidade_filantropica(self):
        # Estado do Espírito Santo, repetido em 6 registros.
        t = ("Credenciamento de instituições filantrópicas privadas (com e sem fins lucrativos), "
             "prestadoras de serviços de saúde interessadas em participar, de forma complementar, "
             "do SUS - ES na prestação de SERVIÇOS ESPECIALIZADOS")
        self.assertEqual(familia(t), "servico_ao_orgao")

    def test_tabela_sigtap_e_venda_de_procedimento(self):
        t = ("CREDENCIAMENTO DA ASSOCIACAO EDUCACIONAL P/ REALIZAR PROCEDIMENTOS DIAGNÓSTICO EM "
             "LABORATÓRIO CLÍNICO DA TABELA SUS SIGTAP")
        self.assertEqual(familia(t), "servico_ao_orgao")


class OutrasFamiliasNovas(unittest.TestCase):
    def test_banco_de_fomento_nao_e_fomento(self):
        # Campos Novos/SC. A palavra "fomento" aparece duas vezes e não há
        # fomento nenhum: é credenciamento de banco.
        t = ("CREDENCIAMENTO DE INSTITUIÇÕES FINANCEIRAS, COOPERATIVAS DE CRÉDITO, AGÊNCIAS OU "
             "BANCOS DE FOMENTO, A FIM DE OPERACIONALIZAR O PROGRAMA JURO ZERO, FOMENTANDO "
             "PEQUENOS NEGÓCIOS")
        self.assertEqual(familia(t), "instituicao_financeira")

    def test_adesao_de_municipios(self):
        # Chamada Pública 01/2026 da SECULT/GO: quem adere são as prefeituras.
        t = ("A presente Chamada Pública tem por objeto a adesão institucional voluntária de até "
             "120 (cento e vinte) municípios e distritos do Estado de Goiás ao projeto CineLeitura "
             "do Bem")
        self.assertEqual(familia(t), "destinado_a_entes_publicos")

    def test_premio_para_jornalista_pessoa_fisica(self):
        t = ("2º Prêmio MOL de Jornalismo para a Solidariedade, aberto a profissionais e estudantes "
             "de comunicação, nas categorias Jovem Jornalista e Profissional")
        self.assertEqual(familia(t), "destinado_a_pessoa_fisica")

    def test_resultado_de_habilitacao(self):
        t = "Pnab 2026: Divulgado resultado final de habilitados e não habilitados dos Editais"
        self.assertEqual(familia(t), "resultado_de_habilitacao")

    def test_parecerista_e_pagamento_por_parecer(self):
        t = ("CREDENCIAMENTO DE AVALIADORES/PARECERISTAS DE PROJETOS CULTURAIS PNAB, para análise e "
             "emissão de pareceres técnicos")
        self.assertEqual(familia(t), "parecerista_ou_juri")

    def test_parceiro_nominal_com_cnpj_no_objeto(self):
        # Araquari/SC: o parceiro está nomeado com CNPJ, o negócio está fechado.
        t = ("Celebração de parceria com a COOPERATIVA DE ARAQUARI AGRICULTURA FAMILIAR, inscrita no "
             "CNPJ sob o nº 30.639.217/001-07, por meio da formalização de termo de colaboração")
        self.assertEqual(familia(t), "parceria_ja_celebrada")

    def test_espaco_publico_para_venda(self):
        t = ("Credenciamento e seleção para habilitação de entidades filantrópicas sem fins lucrativas "
             "para espaços (barracas) para venda de bebidas em geral durante o evento")
        self.assertEqual(familia(t), "uso_de_espaco_publico")

    def test_prospeccao_imobiliaria(self):
        t = ("Chamamento público para prospecção do mercado imobiliário em Caieiras/SP, visando à "
             "locação de imóvel comercial para uso institucional")
        self.assertEqual(familia(t), "imovel_ou_mercado")

    def test_captacao_de_cotas_de_patrocinio_pelo_orgao(self):
        # Parintins/AM. O municipio busca patrocinador: o recurso entra no orgao.
        t = ("CREDENCIAMENTO PARA A CAPTAÇÃO DE COTAS DE PATROCÍNIO POR PESSOAS FÍSICAS E/OU JURÍDICAS "
             "DE DIREITO PRIVADO, COM OU SEM FINS LUCRATIVOS, PARA APOIO NO CUSTEIO DOS EVENTOS")
        self.assertEqual(familia(t), "busca_patrocinador")

    def test_credenciamento_de_medicos_e_servico(self):
        t = "CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE MÉDICOS ESPECIALISTAS E EXAMES ESPECIALIZADOS"
        self.assertEqual(familia(t), "servico_ao_orgao")

    def test_pagina_de_noticia_do_portal(self):
        t = "Instituto Sabin lança livro que registra a história do voluntariado corporativo"
        self.assertEqual(familia(t), "conteudo_institucional")


class ResgatesQueImpedemFalsoPositivo(unittest.TestCase):
    """Falso positivo é o erro caro: perde oportunidade e não deixa rastro."""

    def test_termo_de_fomento_com_osc_nunca_e_barrado(self):
        # Dois Vizinhos/PR. Tem a palavra "execução de atividades", que a família
        # de serviço poderia pegar; o instrumento de fomento resgata.
        t = ("CREDENCIAMENTO, com o objetivo de formalização de Parceria, através de Termo de Fomento, "
             "com Organizações da Sociedade Civil (OSC) para execução de atividades em regime de mútua "
             "cooperação com a administração pública")
        self.assertTrue(avaliar(t)["ok"])
        self.assertEqual(veredito(t), "aprovado")

    def test_pnab_para_artistas_e_grupos_vira_atencao_nao_reprovacao(self):
        # Itacaré/BA. Sem o resgate cultural isto cairia em cachê artístico e a
        # oportunidade seria perdida em silêncio.
        t = ("EDITAL PARA CREDENCIAMENTO DE ARTISTAS E GRUPOS CULTURAIS LOCAIS, POR MEIO DE FOMENTO "
             "DIRETO À EXECUÇÃO DE AÇÕES, PARA REPASSE DE RECURSOS NÃO REEMBOLSÁVEIS PROVENIENTES DA "
             "POLÍTICA NACIONAL ALDIR BLANC - PNAB")
        self.assertTrue(avaliar(t)["ok"])
        self.assertEqual(veredito(t), "atencao")

    def test_cache_de_show_continua_barrado(self):
        # O resgate não pode virar porta aberta: sem marca de fomento, é cachê.
        t = ("CREDENCIAMENTO DE PESSOAS JURÍDICAS PARA APRESENTAÇÃO DE SHOWS MUSICAIS (BANDAS, DUPLAS "
             "OU CANTORES) PARA ATENDER OS EVENTOS MUNICIPAIS")
        self.assertEqual(familia(t), "cache_artistico")

    def test_acolhimento_socioassistencial_com_osc_vai_a_conferencia(self):
        # Palmas/PR. Pode ser termo de colaboração ou compra de vaga: o objeto
        # não diz, então o sistema não decide sozinho.
        t = ("Credenciamento de Organizações da Sociedade Civil – OSCs para Prestar Serviço de Proteção "
             "Social Especial de Alta Complexidade na modalidade de acolhimento para idosos")
        self.assertTrue(avaliar(t)["ok"])
        self.assertEqual(veredito(t), "atencao")

    def test_selecao_de_osc_por_lei_13019_passa_limpo(self):
        t = ("SELEÇÃO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL (OSC) PARA A EXECUÇÃO DAS AÇÕES DO PROGRAMA "
             "MUNICIPAL OLHANDO PARA O FUTURO. FUNDAMENTAÇÃO LEGAL: Lei nº 13.019, de 31 de julho de 2014")
        self.assertTrue(avaliar(t)["ok"])


class SemMarcaNenhuma(unittest.TestCase):
    def test_objeto_pobre_nao_e_reprovado_e_sim_marcado_para_conferencia(self):
        # Curitiba publicou um objeto de tres palavras. Barrar por ausencia de
        # vocabulario e o erro que este modulo existe para nao cometer: pode ser
        # parceria com cooperativa de catadores.
        t = "CHAMAMENTO PÚBLICO RESÍDUOS SÓLIDOS"
        r = avaliar(t)
        self.assertTrue(r["ok"])
        self.assertIn("insuficiente", (r["atencao"] or ""))

    def test_errata_de_cronograma_e_sinal_de_atencao(self):
        t = ("Errata e retificação de cronograma dos Editais do PNAB 2026 para organizações da "
             "sociedade civil")
        r = avaliar(t)
        self.assertTrue(r["ok"])
        self.assertIn("errata", (r["atencao"] or "").lower())


class ItemCompleto(unittest.TestCase):
    def test_avaliar_item_usa_titulo_objeto_e_evidencia(self):
        item = {"titulo": "Chamamento Público 02/2026",
                "objeto": "seleção de Organização da Sociedade Civil para firmar Termo de Colaboração",
                "evidencia": ""}
        self.assertTrue(avaliar_item(item)["ok"])


if __name__ == "__main__":
    unittest.main()
