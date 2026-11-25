"""N-04 (manutenção de 25/11/2026; titular, 25/11/2026: «o governador passa a decidir pela memória livre real, com margem
de 1 GB»): a IA local ocupa 6,3 a 8,5 GB FIXOS dos 15,7 GB; somada à carga, o governador adiava até 74 motores numa hora
dizendo «memória sem folga até 85%» com memória disponível. O alarme acima de 85% continua igual."""
from eldorado.base.cerebro.governador import Governador, Leitura

TOTAL = 15701.0


def _gov(memoria, livre_mb, ia_mb=8239.0, processador=0.18):
    return Governador(lambda: Leitura(processador=processador, memoria=memoria, disco=0.5,
                                      mem_livre_mb=livre_mb, mem_ia_mb=ia_mb, mem_total_mb=TOTAL))


def test_memoria_fixa_da_ia_nao_adia_motor_quando_ha_memoria_livre():
    g = _gov(0.835, livre_mb=2590.0)                 # a leitura de 25/11 17h56: 83,5%, IA 8,2 GB, ~2,5 GB livres
    assert g.pode_iniciar("motor-x", "leve")         # antes: 0,835 + 0,02 > 0,85 → adiado
    assert g.paralelismo("motor-x") >= 1


def test_sem_memoria_livre_para_o_custo_mais_1_gb_o_motor_espera_e_o_motivo_mostra_as_partes():
    g = _gov(0.90, livre_mb=1200.0)                  # 1,2 GB livres < 0,08 × 15,7 GB + 1 GB (o pesado)
    assert not g.pode_iniciar("motor-x", "pesado")
    m = g.motivo()
    assert "IA 8.0 GB fixos" in m and "livre 1.2 GB" in m and "motores e sistema" in m


def test_acima_de_95_por_cento_nada_comeca_e_o_alarme_de_85_continua():
    g = _gov(0.96, livre_mb=5000.0)
    assert not g.pode_iniciar("motor-x")
    assert any("acima de 85%" in a for a in g.alertas())
    assert any("acima de 85%" in a for a in _gov(0.86, livre_mb=3000.0).alertas())   # o alarme não mudou


def test_o_limite_de_85_por_cento_nao_foi_folgado():
    assert Governador(lambda: Leitura(0.1, 0.1, 0.1)).limite == 0.85
    g = Governador(lambda: Leitura(processador=0.1, memoria=0.84, disco=0.5))   # sem a medida em MB: a regra de antes
    assert not g.pode_iniciar("m", "pesado")
