"""A memória sob o Comandante (26/10/2026: a memória subiu até 96% e a regra dos 85% parou o sistema por 3 horas): cada
voo reaproveita o contexto da sua vaga; sob pressão, os voos caem para 2; a memória presa pede o reinício do ciclo."""

from eldorado.base.cerebro import pilotos_permanentes as PP
from eldorado.base.comandante import pilotos as CP


class _Mem:
    def __init__(self, cpu, mem):
        self.cpu, self.percent = cpu, mem


def test_a_pressao_reduz_os_voos_e_pede_o_reinicio(monkeypatch):
    import psutil

    relogio = [1000.0]
    monkeypatch.setattr(CP.time, "monotonic", lambda: relogio[0])
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval=None: 40.0)
    mem = [70.0]
    monkeypatch.setattr(psutil, "virtual_memory", lambda: _Mem(0, mem[0]))
    CP.REINICIAR.clear()
    CP._pressao.update(carga_desde=None, memoria_desde=None)
    CP.carga()
    assert PP.paralelos_agora() == 2  # sem pressão: 5 voos
    mem[0] = 90.0
    CP.carga()
    relogio[0] += 11 * 60
    CP.carga()
    assert PP.paralelos_agora() == 1 and not CP.REINICIAR.is_set()  # 10 minutos acima de 85%: 1 voo
    mem[0] = 96.0
    CP.carga()
    relogio[0] += 16 * 60
    CP.carga()
    assert CP.REINICIAR.is_set()  # 15 minutos acima de 92%: o reinício
    mem[0] = 60.0
    CP.carga()
    assert PP.paralelos_agora() == 2
    CP.REINICIAR.clear()


def test_cada_vaga_reaproveita_o_contexto(monkeypatch, tmp_path):
    criados = []

    def contexto_falso(dados, diario):
        criados.append(1)

        class C:
            def close(self):
                pass

        class Esc:
            buscar = None

        return dados, C(), Esc(), None

    monkeypatch.setattr(PP, "_contexto", contexto_falso)
    import eldorado.base.cerebro.encaminhamento as E
    import eldorado.base.cerebro.rede as R
    import eldorado.motores.descoberta.metabusca as M
    import eldorado.motores.pilotos.interceptador as I

    monkeypatch.setattr(E, "Encaminhamento", lambda *a, **k: object())
    monkeypatch.setattr(I, "Interceptador", lambda *a, **k: object())
    monkeypatch.setattr(R, "rede_atual", lambda d: None)
    monkeypatch.setattr(M, "Metabusca", lambda **k: None)
    import eldorado.base.nucleo.ia as IAm

    monkeypatch.setattr(IAm.IA, "disponivel", lambda self: False)
    v = PP._Vaga(tmp_path, tmp_path / "ev", 0)
    for _ in range(PP._Vaga.RENOVAR):
        v.contexto()
        v.feitos += 1
    assert len(criados) == 1  # 20 livros no mesmo contexto
    v.contexto()
    assert len(criados) == 2  # renovado depois de 20
