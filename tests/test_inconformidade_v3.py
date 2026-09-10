"""Famílias e sinais aprendidos na validação individual de 09/09/2026.

Nesta rodada não houve leitura de documento: foi a leitura atenta do objeto que
o próprio órgão declarou na API oficial do PNCP, um registro por vez. O que ela
produziu foram cinco famílias novas de reprovação, três sinais novos de
APROVAÇÃO — que são os que evitam o erro caro — e um discriminador que faltava.
"""
import unittest

from src.inconformidade import avaliar


def familia(t):
    return avaliar(t)["familia"]


def veredito(t):
    r = avaliar(t)
    return "reprovado" if not r["ok"] else ("atencao" if r["atencao"] else "aprovado")


class FamiliasNovas(unittest.TestCase):
    def test_convenio_de_desconto_nao_tem_repasse_em_direcao_nenhuma(self):
        # CRC do Ceará e DETRAN-SP: credenciam empresa para dar desconto a
        # associado e a servidor. Ninguém repassa nada a ninguém.
        t = ("credenciamento de parcerias com pessoas jurídicas para oferecer desconto de, no mínimo, "
             "15% (quinze por cento) sobre seus serviços aos profissionais registrados perante o CRCCE")
        self.assertEqual(familia(t), "convenio_de_desconto")

    def test_cadastro_de_fornecedor_por_tempo_indeterminado(self):
        t = ("CHAMAMENTO PÚBLICO, tem como objeto cadastrar empresas sediadas no Estado de Rondônia "
             "voltadas ao ramo turístico, tais como Meios de Hospedagem, por tempo indeterminado")
        self.assertEqual(familia(t), "cadastro_de_fornecedor")

    def test_aquisicao_de_vagas_e_compra(self):
        t = ("CREDENCIAMENTO DE INSTITUIÇÕES DE ENSINO COM E SEM FINS LUCRATIVOS - AQUISIÇÃO DE ATÉ 9000 "
             "(NOVE MIL VAGAS AO LONGO DE SESSENTA MESES DE VIGÊNCIA DO EDITAL) DE EDUCAÇÃO INFANTIL")
        self.assertEqual(familia(t), "compra_de_vaga")

    def test_contrapartida_em_passagem_aerea_nao_e_fomento(self):
        # CREFITO-5, Porto Alegre: a entidade indica um fisioterapeuta e recebe
        # transporte aéreo de ida e volta. É a contrapartida mais barata da base.
        t = ("credenciamento de pessoas jurídicas de direito privado sem fins lucrativos, para que esta "
             "indique 01 (um) fisioterapeuta regularmente inscrito no CREFITO-5, mediante oportuno "
             "fornecimento de transporte aéreo de ida e volta")
        self.assertEqual(familia(t), "contrapartida_sem_repasse")


class DiscriminadorDaLeiInvocada(unittest.TestCase):
    """Quando o município celebra parceria, cita a 13.019. Quando compra vaga,
    cita a 14.133. A lei invocada decide o que o objeto não diz."""

    def test_acolhimento_pela_14133_e_compra_de_vaga(self):
        t = ("Credenciamento de serviços de acolhimento Institucional de Longa Permanência para Idosos "
             "(ILPI), de acordo com a Lei Federal no 14.133, de 1º de abril de 2021, Lei 10.741/2003 – "
             "Estatuto do Idoso")
        self.assertEqual(familia(t), "compra_de_vaga")

    def test_a_grafia_no_sem_ordinal_tambem_casa(self):
        # O órgão publica "Lei Federal no 14.133" sem o caractere ordinal, e o
        # filtro tem de reconhecer assim mesmo.
        self.assertEqual(familia("acolhimento institucional conforme Lei Federal no 14.133/2021"),
                         "compra_de_vaga")

    def test_acolhimento_que_cita_as_duas_leis_vai_a_conferencia(self):
        t = ("Credenciamento de OSC para acolhimento institucional, nos termos da Lei Federal nº 13.019 de "
             "2014 e da Lei 14.133/2021")
        self.assertEqual(veredito(t), "atencao")


class SinaisDeAprovacaoQueEvitamOErroCaro(unittest.TestCase):
    def test_doacao_de_bens_a_entidade_e_captacao(self):
        # Colombo/PR. A entidade RECEBE bens: é captação em espécie, e o sistema
        # não tinha essa modalidade catalogada. Sem este sinal, "bens móveis"
        # caía em compra e a oportunidade se perdia.
        t = ("Credenciamento de Entidades sem fins lucrativos do Município de Colombo, para doação de bens "
             "móveis declarados inservíveis pela Prefeitura Municipal")
        r = avaliar(t)
        self.assertTrue(r["ok"])
        self.assertIn("captação em espécie", r["atencao"])

    def test_coleta_seletiva_solidaria_e_oportunidade(self):
        # A cooperativa não recebe repasse: recebe o material e vive da venda,
        # no modelo do Decreto 5.940/2006. Sem este sinal, "serviço de coleta"
        # caía em serviço ao órgão.
        t = ("Chamada Pública para credenciamento de cooperativas de catadores de materiais recicláveis, sem "
             "fins lucrativos, para realizarem a triagem, classificação e comercialização dos resíduos")
        r = avaliar(t)
        self.assertTrue(r["ok"])
        self.assertIn("Decreto 5.940", r["atencao"])

    def test_plano_de_trabalho_com_osc_passa_limpo(self):
        # Campina Grande/PB. "Nos termos do plano de trabalho" é a marca mais
        # forte que existe: o repasse segue o plano, não o procedimento.
        t = ("PARCERIA PARA EXECUÇÃO POR ORGANIZAÇÃO DA SOCIEDADE CIVIL DE SERVIÇO DE CASTRAÇÃO DE CÃES E "
             "GATOS, NOS TERMOS DO PLANO DE TRABALHO, NO TERRITÓRIO DO MUNICÍPIO")
        self.assertEqual(veredito(t), "aprovado")


class ObjetoInsuficienteNaOrigem(unittest.TestCase):
    def test_objeto_de_tres_palavras_vai_a_conferencia_nao_a_reprovacao(self):
        # Triunfo/RS publicou "CHAMAMENTO PUBLICO CREDENCIMENTO" — três palavras
        # e um erro de digitação. O defeito é de publicação, não de coleta, e o
        # princípio do módulo é não vetar por ausência.
        r = avaliar("CHAMAMENTO PUBLICO CREDENCIMENTO")
        self.assertTrue(r["ok"])
        self.assertIn("defeito é de publicação", r["atencao"])

    def test_objeto_normal_nao_cai_na_regra_do_objeto_curto(self):
        t = ("Credenciamento de organizações da sociedade civil para celebração de termo de fomento na área "
             "da assistência social do município")
        self.assertNotIn("defeito é de publicação", avaliar(t)["atencao"] or "")


class SingularDaSociedadeCivil(unittest.TestCase):
    """O padrão antigo só pegava o plural, e muitos editais escrevem no singular."""

    def test_organizacao_no_singular_conta_como_terceiro_setor(self):
        t = ("SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL, SEM FINS LUCRATIVOS, PARA CELEBRAR PARCERIA COM O "
             "CONSÓRCIO INTERMUNICIPAL PARA EXECUÇÃO DE SERVIÇO DE ACOLHIMENTO")
        self.assertTrue(avaliar(t)["ok"])

    def test_parceria_com_plano_de_trabalho_no_singular_passa_limpo(self):
        # Campina Grande/PB passou por essa fresta: "POR ORGANIZAÇÃO DA
        # SOCIEDADE CIVIL", singular, não casava com o padrão antigo.
        t = ("PARCERIA PARA EXECUÇÃO POR ORGANIZAÇÃO DA SOCIEDADE CIVIL DE SERVIÇO DE CASTRAÇÃO, NOS TERMOS "
             "DO PLANO DE TRABALHO")
        self.assertEqual(veredito(t), "aprovado")


class AtoDecorrenteDisfarcadoDeFomento(unittest.TestCase):
    def test_contratacao_de_osc_nos_termos_de_edital_antigo_e_ato_decorrente(self):
        # Cocalzinho de Goiás. Tudo no objeto soa como fomento — OSC, termo de
        # colaboração — e é: mas é o ato decorrente de um edital de 2021, com a
        # entidade já escolhida. Não há fase de inscrição.
        t = ("CONTRATAÇÃO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO, NOS "
             "TERMOS DO EDITAL DE CHAMAMENTO PÚBLICO N° 001/2021")
        self.assertEqual(familia(t), "resultado_de_habilitacao")


class NaoQuebrouOQueJaFuncionava(unittest.TestCase):
    def test_servico_ao_orgao_continua_barrado(self):
        t = ("CREDENCIAMENTO PARA EMPRESAS, COM OU SEM FINS LUCRATIVOS, PARA REALIZAÇÃO DE CONSULTAS E "
             "EXAMES ELETIVOS DE MÉDIA COMPLEXIDADE")
        self.assertEqual(familia(t), "servico_ao_orgao")

    def test_termo_de_fomento_com_osc_continua_aprovado(self):
        t = ("CREDENCIAMENTO, com o objetivo de formalização de Parceria, através de Termo de Fomento, com "
             "Organizações da Sociedade Civil (OSC) para execução de atividades")
        self.assertEqual(veredito(t), "aprovado")


if __name__ == "__main__":
    unittest.main()
