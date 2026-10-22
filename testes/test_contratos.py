import pytest

from eldorado.base.nucleo.contratos import Achado, ContratoVioladoErro, Descricao, Motor, Plano, Saude, verificar_contrato


class MotorCompleto(Motor):
    def descrever(self):
        return Descricao(id="teste", tipo="motor", parte="MOTORES", finalidade="testar", metrica="achados por janela")

    def saude(self):
        return Saude(ok=True)

    def planejar(self, plano):
        return plano.alvos

    def buscar(self, plano):
        yield Achado(id="a1", motor="teste", encontrado_em="2026-10-22", link_divulgacao="https://x", dados={})

    def aprender(self, retornos):
        pass

    def painel(self):
        return {}


def test_motor_completo_cumpre_o_contrato():
    d = verificar_contrato(MotorCompleto())
    assert d.id == "teste"
    achados = list(MotorCompleto().buscar(Plano(passagem="p", janela_inicio="a", janela_fim="b")))
    assert achados[0].link_divulgacao == "https://x"


def test_motor_incompleto_nao_pode_ser_criado():
    class Incompleto(Motor):
        def descrever(self):
            return None
    with pytest.raises(TypeError):
        Incompleto()


def test_descricao_incompleta_e_recusada():
    class SemFinalidade(MotorCompleto):
        def descrever(self):
            return Descricao(id="x", tipo="motor", parte="MOTORES", finalidade="", metrica="m")
    with pytest.raises(ContratoVioladoErro, match="finalidade"):
        verificar_contrato(SemFinalidade())


def test_tipo_da_descricao_deve_bater_com_o_modulo():
    class TipoErrado(MotorCompleto):
        def descrever(self):
            return Descricao(id="x", tipo="piloto", parte="MOTORES", finalidade="f", metrica="m")
    with pytest.raises(ContratoVioladoErro, match="piloto"):
        verificar_contrato(TipoErrado())


def test_objeto_que_nao_e_modulo_e_recusado():
    with pytest.raises(ContratoVioladoErro):
        verificar_contrato(object())
