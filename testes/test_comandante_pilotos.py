"""As quatro regras dos pilotos (titular, 25/10/2026): 3 segundos, a janela de busca, o acionamento do Comandante e a
carga perto de 85%; os dois pilotos em paralelo; cada autorização registrada como decisão no Arquivo do Cérebro."""

import threading
import time

from eldorado.base.comandante import pilotos as cp
from eldorado.base.nucleo.eventos import Diario, ler


def test_as_quatro_regras_dos_pilotos(bancos, gravador, tmp_path, monkeypatch):
    c = bancos["cerebro"]
    c.executemany(
        "INSERT INTO espiao_familia(nome, a, b, usos, achados) VALUES (?,?,?,?,?)",
        [("setor_apoio_regiao", 3, 1, 4, 3), ("internacional_ingles", 1, 3, 4, 0)],
    )
    c.commit()
    parar, ev = threading.Event(), tmp_path / "ev"
    cargas = iter([95.0, 92.0, 70.0] + [70.0] * 50)
    monkeypatch.setattr(cp, "carga", lambda: next(cargas))
    monkeypatch.setattr(cp, "INTERVALO_S", 0.3)
    esperas = []
    monkeypatch.setattr(parar, "wait", lambda s: (esperas.append(s), time.sleep(min(s, 0.31)))[1])
    a = cp.autorizar("espiao", tmp_path, Diario(ev, "c"), parar)  # regra 4: espera a carga baixar de 85%
    assert a and a["alvo"] in ("setor_apoio_regiao", "internacional_ingles") and a["carga"] <= 85 and esperas.count(10) == 2
    cp.pousou("espiao")
    t0 = time.monotonic()
    assert cp.autorizar("espiao", tmp_path, Diario(ev, "c"), parar)  # regra 1: o intervalo depois do pouso
    assert time.monotonic() - t0 >= 0.25
    assert cp.autorizar("interceptador", tmp_path, Diario(ev, "c"), parar) is None  # regra 2: sem livro na fila, não voa
    assert cp.autorizar("interceptador", tmp_path, Diario(ev, "c"), parar, alvo="L-1", titulo="Edital X")
    assert gravador.aplicar(list(ler(ev))).ok
    dec = c.execute("SELECT etapa, motivo FROM comandante_decisao ORDER BY id").fetchall()  # regra 3: cada autorização registrada
    assert [d[0] for d in dec] == ["espiao", "espiao", "interceptador"] and all("carga" in d[1] for d in dec)


def test_os_dois_pilotos_em_paralelo(bancos, tmp_path, monkeypatch):
    c = bancos["cerebro"]
    c.execute("INSERT INTO espiao_familia(nome) VALUES ('setor_apoio_regiao')")
    c.commit()
    monkeypatch.setattr(cp, "carga", lambda: 50.0)
    monkeypatch.setattr(cp, "INTERVALO_S", 0.0)
    parar, fim = threading.Event(), {}

    def voo(piloto, **kw):
        assert cp.autorizar(piloto, tmp_path, Diario(tmp_path / "ev", piloto), parar, **kw)
        time.sleep(0.5)
        fim[piloto] = time.monotonic()

    t0 = time.monotonic()
    fios = [threading.Thread(target=voo, args=("espiao",)), threading.Thread(target=voo, args=("interceptador",), kwargs={"alvo": "L-2"})]
    for f in fios:
        f.start()
    for f in fios:
        f.join()
    assert max(fim.values()) - t0 < 0.95  # os dois juntos: nenhum esperou o outro
