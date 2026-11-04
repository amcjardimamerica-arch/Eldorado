"""R43 (titular, 04/11/2026): o governador por recurso e os voos só na missão do Comandante."""
import threading
import time

from eldorado.base.cerebro.governador import Governador, Leitura


def test_a_memoria_residente_nao_trava_com_o_processador_livre():
    g = Governador(medidor=lambda: Leitura(processador=0.02, memoria=0.80, disco=0.5))
    assert g.pode_iniciar(None, "leve")                       # antes: 0,80 + 0,05 → no limite; com custo aprendido alto, adiado
    g1 = Governador(medidor=lambda: Leitura(processador=0.02, memoria=0.74, disco=0.5))
    assert g1.pode_iniciar(None, "pesado")                    # antes: 0,74 + 0,25 > 0,85 → adiado com o processador em 2%
    g2 = Governador(medidor=lambda: Leitura(processador=0.70, memoria=0.40, disco=0.5))
    assert not g2.pode_iniciar(None, "pesado")                # o processador sem folga continua adiando
    g3 = Governador(medidor=lambda: Leitura(processador=0.10, memoria=0.80, disco=0.5))
    assert not g3.pode_iniciar(None, "pesado")                # a memória sem folga para a tarefa também


def test_sem_missao_do_comandante_nenhum_voo(monkeypatch, tmp_path):
    import eldorado.base.cerebro.pilotos_permanentes as PP
    import eldorado.base.comandante.biblioteca as CB
    import eldorado.motores.pilotos.interceptador as I
    voos = []

    class Con:
        def execute(self, q, *a):
            return [(0, "base_classe")]

        def close(self):
            pass

    monkeypatch.setattr(PP, "_voo_interceptador", lambda vaga, parar, lv_id, base, tempo: voos.append(lv_id))
    monkeypatch.setattr(PP, "_contexto", lambda dados, diario: (dados, Con(), None, None))
    monkeypatch.setattr(PP, "paralelos_agora", lambda: 2)
    monkeypatch.setattr(CB, "avaliar", lambda con: [])
    monkeypatch.setattr(CB, "fila", lambda av: [{"id": f"L{i}"} for i in range(10)])   # a base quer voar…
    monkeypatch.setattr(I, "fila", lambda con, hoje: [])                               # …mas o Comandante não direcionou

    class Diario:
        pasta = tmp_path

        def emitir(self, *a, **k):
            pass

    parar = threading.Event()
    t = threading.Thread(target=PP.voar_interceptador, args=(tmp_path, Diario(), parar), daemon=True)
    t.start()
    time.sleep(0.6)
    parar.set()
    assert voos == []
