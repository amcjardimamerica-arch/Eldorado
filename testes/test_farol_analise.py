"""A transferência ao Farol (etapa 08) e a análise (a previsão, o calendário, a história): o plano, sobre o banco real."""
import json
import shutil
from datetime import date

import pytest

from eldorado.base.analise import previsao as P
from eldorado.base.transferencia import farol


def test_previsao_pela_repeticao_das_aberturas():
    p = P.prever([date(2023, 9, 20), date(2024, 9, 26), date(2025, 9, 18)], hoje=date(2026, 3, 1))
    assert p["proxima_abertura_prevista"] == "2026-09-20" and p["alerta_em"] == "2026-08-21" and p["confianca"] >= 0.7
    um = P.prever([date(2025, 5, 10)], hoje=date(2026, 6, 1))
    assert um["proxima_abertura_prevista"] == "2027-05-10" and um["confianca"] == 0.3                # um ano só: confiança baixa
    assert P.prever([]) is None


@pytest.fixture(scope="module")
def copia(tmp_path_factory):
    from eldorado.base.fluxo.nos import abrir_bancos
    tmp_path = tmp_path_factory.mktemp("farol")                       # uma cópia só para os testes (o banco é grande)
    for n in ("biblioteca", "cerebro"):
        shutil.copy(f"dados/{n}.db", tmp_path / f"{n}.db")
    bancos = abrir_bancos(tmp_path)
    yield tmp_path, bancos
    for c in bancos.values():
        c.close()


def test_transferencia_ao_farol_de_ponta_a_ponta(copia):
    from eldorado.base.nucleo.eventos import Diario, ler
    from eldorado.base.nucleo.gravador import Gravador
    pasta, bancos = copia
    con = bancos["biblioteca"]
    # a condição criada na cópia (24/10/2026: a produção já transferiu todos; o teste não pode depender do estado do dia)
    con.execute("DELETE FROM transferencia WHERE livro_id IN (SELECT livro_id FROM passaporte WHERE fase = 'farol' LIMIT 6)")
    con.commit()
    antes = len(farol.para_transferir(con))
    assert antes > 0
    diario = Diario(pasta / "eventos", "teste")
    r = farol.transferir(con, diario, pasta / "farol", limite=5)
    assert r["transferidos"] == 5
    arq = json.loads(next((pasta / "farol").glob("*.json")).read_text(encoding="utf-8"))
    if arq.get("formato") is None:
        arq = json.loads(sorted((pasta / "farol").glob("*.json"))[0].read_text(encoding="utf-8"))
    assert {"livro", "links", "itens", "dispensas", "passaporte", "relatorios", "achados"} <= set(arq) or arq.get("livros")
    assert len(json.loads((pasta / "farol" / "manifesto.json").read_text(encoding="utf-8"))["livros"]) == 5
    assert Gravador(bancos).aplicar(list(ler(pasta / "eventos"))).ok                             # o registro no livro
    assert con.execute("SELECT COUNT(*) FROM transferencia").fetchone()[0] >= 5
    assert len(farol.para_transferir(con)) == antes - 5                                           # só vai de novo o que mudar


def test_calendario_e_historia(copia):
    _, bancos = copia
    con = bancos["biblioteca"]
    cal = P.calendario(con, hoje=date(2026, 10, 1))
    assert cal == sorted(cal, key=lambda x: x["data"]) and all(x["tipo"] in ("encerramento", "abertura prevista") for x in cal)
    lid = con.execute("SELECT livro_id FROM passagem LIMIT 1").fetchone()[0]
    h = P.historia(con, lid)
    assert h and any(x["o_que"].startswith("passagem") for x in h)
