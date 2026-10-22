from eldorado.base.cerebro.governador import Governador, Leitura
from eldorado.base.nucleo.eventos import ler


def fixo(cpu, mem, disco=0.3):
    return lambda: Leitura(cpu, mem, disco)


def test_folga_permite_e_falta_de_folga_segura():
    assert Governador(fixo(0.50, 0.40)).pode_iniciar()
    assert not Governador(fixo(0.84, 0.40)).pode_iniciar()                 # 0,84 + 0,05 passaria de 0,85
    assert not Governador(fixo(0.20, 0.90)).pode_iniciar()                 # memória também conta


def test_tarefa_pesada_exige_mais_folga():
    g = Governador(fixo(0.55, 0.30))
    assert g.pode_iniciar(peso="leve") and g.pode_iniciar(peso="pesado")          # 0,55 + 0,25 = 0,80 cabe
    g2 = Governador(fixo(0.65, 0.30))
    assert g2.pode_iniciar(peso="leve") and not g2.pode_iniciar(peso="pesado")


def test_disco_cheio_nao_e_carga_mas_disco_critico_para_tudo():
    assert Governador(fixo(0.0, 0.06, disco=0.92)).pode_iniciar()          # o caso real do teste de fumaça
    g = Governador(fixo(0.0, 0.06, disco=0.96))
    assert not g.pode_iniciar() and "disco" in g.motivo() and g.paralelismo() == 0


def test_paralelismo_pela_folga_e_pelo_custo_aprendido():
    g = Governador(fixo(0.45, 0.20), paralelismo_maximo=16)
    assert g.paralelismo() == 8                                              # (0,85 − 0,45) / 0,05
    g.custos["motor-pesado"] = 0.2
    assert g.paralelismo("motor-pesado") == 2


def test_custo_e_aprendido_dos_recibos():
    g = Governador(fixo(0.1, 0.1))
    c1 = g.aprender_custo("m", cpu_ms=900, duracao_ms=1000, memoria_pico_kb=10)
    c2 = g.aprender_custo("m", cpu_ms=100, duracao_ms=1000, memoria_pico_kb=10)
    assert c2 < c1 and g.custos["m"] == c2


def test_simulacao_a_carga_nunca_passa_de_85_por_cento():
    """Critério de pronto da Fase 2: tarefas chegam sem parar; o governador só deixa começar quando cabe."""
    em_curso: list[tuple[int, float]] = []
    base = 0.30

    def carga():
        return base + sum(c for _, c in em_curso)

    g = Governador(lambda: Leitura(carga(), 0.2, 0.3))
    maxima, iniciadas, adiadas = 0.0, 0, 0
    for tique in range(500):
        em_curso[:] = [(fim, c) for fim, c in em_curso if fim > tique]      # tarefas que terminaram
        for n in range(3):                                                    # três tarefas chegam a cada tique
            peso = "pesado" if (tique + n) % 4 == 0 else "leve"
            if g.pode_iniciar(peso=peso):
                em_curso.append((tique + 5 + n, 0.25 if peso == "pesado" else 0.05))
                iniciadas += 1
            else:
                adiadas += 1
            maxima = max(maxima, carga())
    assert maxima <= 0.85 + 1e-9 and iniciadas > 100 and adiadas > 0


def test_leitura_registrada_e_alarme_de_disco(diario, tmp_path):
    g = Governador(fixo(0.1, 0.1, disco=0.9), diario=diario)
    g.registrar({"biblioteca": 1000}, paralelismo=4)
    tipos = [e.tipo for e in ler(tmp_path / "eventos")]
    assert tipos.count("maquina.leitura") == 1 and tipos.count("alarme.aberto") == 1
