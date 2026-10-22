import pytest

from eldorado.banco.biblioteca import esquema as bib
from eldorado.banco.cerebro_db import esquema as cer
from eldorado.banco.especial import esquema as esp
from eldorado.base.nucleo.eventos import Diario, criar
from eldorado.base.nucleo.gravador import Gravador

AGORA = "2026-10-22T12:00:00+00:00"


@pytest.fixture
def bancos(tmp_path):
    b = {"biblioteca": bib.abrir(tmp_path / "biblioteca.db"), "especial": esp.abrir(tmp_path / "especial.db"),
         "cerebro": cer.abrir(tmp_path / "cerebro.db")}
    yield b
    for c in b.values():
        c.close()


@pytest.fixture
def diario(tmp_path):
    return Diario(tmp_path / "eventos")


@pytest.fixture
def gravador(bancos, diario):
    return Gravador(bancos, diario)


def ev(tipo, **dados):
    return criar(tipo, "teste", dados)


def livro(id="L1", chave="k1", **extra):
    d = dict(id=id, missao="oportunidades", chave=chave, titulo="Edital de fomento", situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA)
    d.update(extra)
    return ev("livro.criado", **d)
