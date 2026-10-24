"""Operar perto de 85% da capacidade (titular, 24/10/2026): os motores em paralelo, pela carga medida pelo governador."""
import time

from eldorado.base.cerebro.governador import Governador, Leitura
from eldorado.base.nucleo.contratos import Achado


class MotorLento:
    def __init__(self, mid):
        self.id = mid

    def buscar(self, plano):
        time.sleep(0.4)                                       # espera a rede (o caso comum)
        return [Achado(id=f"{self.id}-1", motor=self.id, titulo="Edital", link_divulgacao="https://x/" + self.id, encontrado_em="2026-10-24", dados={})]


def test_os_motores_rodam_em_paralelo_pela_carga(bancos, diario):
    from eldorado.base.cerebro.regencia import Regencia
    from eldorado.base.nucleo.registro import Registro
    reg = Registro()
    for i in range(8):
        reg._modulos[f"m{i}"] = MotorLento(f"m{i}")
    folga = Governador(lambda: Leitura(processador=.2, memoria=.3, disco=.4))
    rg = Regencia(None, folga, reg, diario, especial=bancos["biblioteca"])
    plano = {"passagem": "p", "motores": [{"modulo": f"m{i}", "janela_inicio": "", "janela_fim": "", "motivo": "teste"} for i in range(8)]}
    t = time.monotonic()
    achados, adiados = rg.acionar(plano)
    assert len(achados) == 8 and not adiados
    assert time.monotonic() - t < 8 * 0.4 * 0.6                 # em paralelo: bem menos que um depois do outro
    cheia = Governador(lambda: Leitura(processador=.95, memoria=.5, disco=.4))
    rg2 = Regencia(None, cheia, reg, diario, especial=bancos["biblioteca"])
    achados, adiados = rg2.acionar(plano)
    assert not achados and len(adiados) == 8                    # acima do alvo, sem folga: adia (não sobrecarrega)
