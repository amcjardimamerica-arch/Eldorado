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


@pytest.fixture(autouse=True)
def _sem_servicos_da_producao(monkeypatch, request):
    """Os testes não usam a IA local nem o buscador próprio (24/10/2026: no portão da produção eles estão ligados, e os
    testes da passagem inteira chamavam o modelo e buscavam na internet; o portão passava de 8 min)."""
    monkeypatch.delenv("ELDORADO_SEARXNG", raising=False)
    if request.module.__name__.endswith("test_ia"):                  # os testes da IA usam a IA simulada deles
        return
    from eldorado.base.nucleo import ia as _ia
    monkeypatch.setattr(_ia.IA, "disponivel", lambda self: False)
    monkeypatch.delenv("ELDORADO_IA_URL", raising=False)
