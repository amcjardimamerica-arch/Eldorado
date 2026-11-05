"""05/11/2026 (titular: a ponte BR no canivete de todo motor): a escada tenta a ponte mesmo quando o domínio aprendeu um
degrau depois dela, e a pendência no computador local leva o motivo de cada degrau que falhou."""
import pytest

from eldorado.motores.acesso.escada import Bloqueado, Escada, Pendente, Resposta


class D:
    pesado = False

    def __init__(self, nome, faz):
        self.nome, self.faz, self.chamado = nome, faz, 0

    def buscar(self, url, tempo_limite):
        self.chamado += 1
        return self.faz(url)


def _bloq(u):
    raise Bloqueado("403")


def _pend(u):
    raise Pendente("pedido entregue ao computador local (x)")


def test_a_ponte_e_tentada_antes_do_degrau_aprendido():
    ponte = D("P · ponte BR (HostGator)", lambda u: Resposta(u, 200, b"<html>" + b"x" * 3000 + b"</html>", "text/html"))
    arq = D("6 · cópia arquivada", _bloq)
    e = Escada([D("1 · api", _bloq), ponte, arq], intervalo_padrao=0)
    e.aprendido["exemplo.gov.br"] = 2                          # aprendeu a cópia arquivada (depois da ponte)
    r = e.buscar("https://exemplo.gov.br/x")
    assert r.degrau.startswith("P ·") and ponte.chamado == 1 and arq.chamado == 0


def test_a_pendencia_leva_os_motivos():
    e = Escada([D("1 · api", _bloq), D("P · ponte BR (HostGator)", _bloq), D("9 · computador", _pend)], intervalo_padrao=0)
    with pytest.raises(Pendente) as x:
        e.buscar("https://exemplo.gov.br/y")
    assert "antes:" in str(x.value) and "ponte BR" in str(x.value)
