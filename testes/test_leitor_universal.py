"""O leitor universal (Tika) é reserva: a falha dele (o servidor que não inicia) nunca derruba o motor (24/10/2026)."""
import pytest

from eldorado.motores.leitura.leitores import Registro, SemLeitor


def test_a_reserva_que_falha_vira_sem_leitor():
    class TikaQuebrado:
        nome = "universal"
        tipos = ()

        def ler(self, conteudo, nome, registro):
            from eldorado.motores.leitura import universal
            u = universal.LeitorUniversal.__new__(universal.LeitorUniversal)
            u._parser = type("P", (), {"from_buffer": staticmethod(lambda c: (_ for _ in ()).throw(RuntimeError("Unable to start Tika server.")))})()
            return u.ler(conteudo, nome, registro)
    pytest.importorskip("tika")
    with pytest.raises(SemLeitor):
        Registro(universal=TikaQuebrado()).ler(b"\x00\x01binario-desconhecido", "x.bin")
