import os

os.environ.setdefault("ELDORADO_ARQUIVAR", "nao")   # os testes nunca arquivam no Wayback (chamada externa)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))   # as funções de nó dos testes (nos_teste)

import pytest

from eldorado.banco.biblioteca import esquema as bib
from eldorado.banco.cerebro_db import esquema as cer
from eldorado.base.nucleo.eventos import Diario, criar
from eldorado.base.nucleo.gravador import Gravador

AGORA = "2026-10-22T12:00:00+00:00"


@pytest.fixture
def bancos(tmp_path):
    livros = bib.abrir(tmp_path / "biblioteca.db")                  # os livros e as empresas, no mesmo banco
    b = {"biblioteca": livros, "especial": livros,
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
