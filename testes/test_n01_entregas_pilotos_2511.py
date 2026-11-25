"""N-01 (manutenção de 25/11/2026): uma em cada cinco passagens falhava com «o nó deve devolver uma lista de dicionários».

Com o laço em 5 blocos (C-01 de 23/11), cada bloco é um processo novo: a fila em memória dos pilotos se perde, a entrega é
lida do arquivo e era convertida em objeto Achado; o executor recusava o retorno e o arquivo já tinha sido apagado — os
achados daquele lote sumiam. R18 (o que falha é pulado), R35 (nenhum dado se perde).
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import eldorado.base.cerebro.pilotos_permanentes as PP
from eldorado.base.nucleo.contratos import Achado


def _limpar_filas():
    for q in PP.ENTREGAS.values():
        while not q.empty():
            q.get_nowait()


def _achado(i: str, motor: str) -> Achado:
    return Achado(id=i, motor=motor, encontrado_em="2026-11-25", link_divulgacao=f"https://exemplo.org/{i}", titulo=f"Edital {i}", dados={})


def test_entregas_do_interceptador_e_do_espiao_viram_dicionarios_mesmo_com_a_fila_perdida(tmp_path, monkeypatch):
    monkeypatch.setattr(PP, "PASTA_ENTREGAS", tmp_path)
    _limpar_filas()
    for piloto in ("interceptador", "espiao"):
        PP.entregar(piloto, _achado(f"{piloto}-1", piloto))          # o objeto Achado (o caso que derrubava a passagem)
        PP.entregar(piloto, {"id": f"{piloto}-2", "motor": piloto})   # o dicionário de Encaminhamento._entregar
        com_fila = PP.entregas(piloto)                                # o mesmo processo (a fila viva)
        assert com_fila and all(isinstance(x, dict) for x in com_fila)
        PP.confirmar_entregas(piloto)
        PP.entregar(piloto, _achado(f"{piloto}-3", piloto))
        _limpar_filas()                                               # o processo novo (o bloco seguinte da C-01)
        sem_fila = PP.entregas(piloto)
        assert [x["id"] for x in sem_fila] == [f"{piloto}-3"]
        assert all(isinstance(x, dict) for x in sem_fila)
        PP.confirmar_entregas(piloto)


def test_a_entrega_so_e_apagada_depois_que_a_passagem_aceita(tmp_path, monkeypatch):
    monkeypatch.setattr(PP, "PASTA_ENTREGAS", tmp_path)
    _limpar_filas()
    PP.entregar("espiao", _achado("e1", "espiao"))
    _limpar_filas()
    primeira = PP.entregas("espiao")                 # a passagem lê... e falha antes de aceitar (sem confirmar)
    assert [x["id"] for x in primeira] == ["e1"]
    PP.entregar("espiao", _achado("e2", "espiao"))
    _limpar_filas()
    segunda = PP.entregas("espiao")                  # a passagem seguinte entrega os mesmos achados e os novos
    assert [x["id"] for x in segunda] == ["e1", "e2"]
    PP.confirmar_entregas("espiao")                  # agora aceitou
    assert PP.entregas("espiao") == []
    assert not list(tmp_path.glob("espiao*.jsonl"))


def test_a_entrega_ilegivel_e_separada_com_alarme_e_as_outras_seguem(tmp_path, monkeypatch):
    monkeypatch.setattr(PP, "PASTA_ENTREGAS", tmp_path)
    _limpar_filas()
    (tmp_path / "interceptador.jsonl").write_text(json.dumps({"id": "ok"}) + "\n{quebrado\n[1, 2]\n", encoding="utf-8")
    abertos = []
    ctx = SimpleNamespace(alarmes=SimpleNamespace(abrir=lambda *a: abertos.append(a)))
    saida = PP.entregas("interceptador")
    PP.alarmar_invalidas(ctx, "interceptador")
    assert saida == [{"id": "ok"}]
    assert len((tmp_path / "interceptador.invalidas.jsonl").read_text(encoding="utf-8").splitlines()) == 2
    assert abertos and "2 entrega(s)" in abertos[0][2]
    PP.confirmar_entregas("interceptador")


def test_o_executor_confirma_a_entrega_so_depois_do_passo_concluido(tmp_path, monkeypatch):
    """No executor de verdade: o nó do piloto que conclui apaga a entrega; o que falha depois dele a deixa para a próxima."""
    from eldorado.base.cerebro import encaminhamento as E
    from eldorado.base.fluxo.definicao import de_dicionario
    from eldorado.base.fluxo.executor import Executor

    monkeypatch.setattr(PP, "PASTA_ENTREGAS", tmp_path / "pilotos")
    _limpar_filas()
    assert callable(getattr(E.no_encaminhar, "confirmar", None)) and callable(getattr(E.no_espiao, "confirmar", None))

    def no_piloto(itens, parametros, contexto):
        return PP.entregas("espiao")
    no_piloto.confirmar = lambda: PP.confirmar_entregas("espiao")

    def no_que_falha(itens, parametros, contexto):
        raise RuntimeError("o nó do piloto falhou")

    d = de_dicionario({"workflow": {"id": "teste"}, "no": [{"id": "espiao", "tipo": "x:piloto"}]}, conferir_funcoes=False)
    PP.entregar("espiao", _achado("e1", "espiao"))
    _limpar_filas()
    falha = Executor(d, tmp_path / "ev1", funcoes={"x:piloto": no_que_falha}, dormir=lambda s: None).executar()
    assert falha.estado == "falhou" and (tmp_path / "pilotos" / "espiao.jsonl").exists()   # nada foi lido nem apagado
    ok = Executor(d, tmp_path / "ev2", funcoes={"x:piloto": no_piloto}).executar()
    assert ok.estado == "concluida" and [x["id"] for x in ok.saidas["espiao"]] == ["e1"]
    assert not list((tmp_path / "pilotos").glob("espiao*.jsonl"))   # aceito: saiu do disco
