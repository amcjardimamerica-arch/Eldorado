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


# 26/10/2026: os testes não acessam a internet. Na nuvem (a Qualidade) a internet é livre e alguns degraus da escada (a
# cópia arquivada, a busca, o servidor do Tika) escapavam para sites de verdade: resultados diferentes (o PNCP com 22 em
# vez de 8) ou testes pendurados até o limite de 1 h (desde 25/10 nenhuma Qualidade terminou). Só o próprio computador
# (os servidores de ensaio) pode ser acessado; o resto falha na hora, igual em qualquer ambiente.
import socket as _socket  # noqa: E402 — a barreira de rede fica junto da sua explicação

_LOCAIS = ("127.", "::1", "0.0.0.0", "localhost")
_conectar_original = _socket.socket.connect
_conectar_ex_original = _socket.socket.connect_ex


def _so_local(endereco) -> bool:
    if isinstance(endereco, (tuple, list)) and endereco:
        return str(endereco[0]).startswith(_LOCAIS)
    return isinstance(endereco, (str, bytes))                    # os sockets de arquivo (unix) são locais


def _conectar(self, endereco):
    if not _so_local(endereco):
        raise OSError(f"rede externa bloqueada nos testes: {endereco}")
    return _conectar_original(self, endereco)


def _conectar_ex(self, endereco):
    if not _so_local(endereco):
        return 111                                                 # recusada
    return _conectar_ex_original(self, endereco)


_socket.socket.connect = _conectar
_socket.socket.connect_ex = _conectar_ex



@pytest.fixture(autouse=True)
def _memoria_de_emissao_limpa():
    """29/10/2026: a gravação só quando muda guarda, no processo, o que já foi gravado; cada trava começa do zero."""
    from eldorado.base.nucleo import eventos as _ev

    _ev._JA_EMITIDOS.clear()
    yield


# 29/10/2026: a QUARENTENA da Qualidade. Estas 6 travas buscam os sites reais na nuvem (a barreira de rede não alcança
# curl_cffi e primp; a tentativa de barrá-los prendeu a bateria) e falham lá, deixando a Qualidade SEMPRE vermelha: uma
# falha nova passava despercebida no meio delas. Só na Qualidade (ELDORADO_QUARENTENA_REDE=1) elas são puladas, com o
# motivo; aqui e no portão continuam rodando. Sair da quarentena = resolver a rede das travas (pendência registrada).
QUARENTENA_REDE = {
    "testes/test_motores_api.py::test_transferegov",
    "testes/test_motores_api.py::test_wordpress_de_goias",
    "testes/test_motores_api.py::test_pncp_pagina_e_traz_os_dados_de_cada_item",
    "testes/test_motor_diarios_municipais.py::test_entrega_com_o_municipio_e_veta_o_ruido",
    "testes/test_interceptador_funciona.py::test_o_plano_de_voo_segue_os_itens_que_faltam",
    "testes/test_interceptador.py::test_rede_interceptador_e_cartorio_fase_4",
}


def pytest_collection_modifyitems(config, items):
    import os

    if os.environ.get("ELDORADO_QUARENTENA_REDE") != "1":
        return
    pular = pytest.mark.skip(reason="quarentena da rede: busca os sites reais na nuvem (29/10/2026)")
    for item in items:
        if item.nodeid in QUARENTENA_REDE:
            item.add_marker(pular)
