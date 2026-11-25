"""C-10 da manutenção de 23/11 (pendente em 25/11, P-04): 8 livros parados na recepção, o mais antigo desde 05/11
(em 16/11 eram 4). Critério: nenhum livro na recepção há mais de 24 h."""
from __future__ import annotations

from datetime import datetime, timezone

from conftest import ev, livro

from eldorado.base.cartorio.auditoria import liberar_recepcao_parada


def _na_recepcao(lid: str, em: str):
    return ev("livro.passagem", livro_id=lid, de=None, para="recepcao", em=em, autorizado_por="regencia", motivo="livro novo")


def test_livro_parado_na_recepcao_ha_mais_de_24h_segue_e_a_causa_fica_visivel(bancos, diario, gravador):
    gravador.aplicar([livro("L1", "k1"), livro("L2", "k2"), _na_recepcao("L1", "2026-11-05T17:17:56+00:00"),
                      _na_recepcao("L2", "2026-11-25T10:00:00+00:00")])
    liberados = liberar_recepcao_parada(bancos["biblioteca"], diario, datetime(2026, 11, 25, 12, tzinfo=timezone.utc))
    assert liberados == ["L1"]                                              # o de 2 h fica (ainda é a entrada normal)
    r = gravador.aplicar(diario.eventos())
    assert not r.recusados, r.recusados
    fases = dict(bancos["biblioteca"].execute("SELECT livro_id, fase FROM passaporte"))
    assert fases == {"L1": "preparacao", "L2": "recepcao"}
    alarme = [e.dados["mensagem"] for e in diario.eventos() if e.tipo == "alarme.aberto"]
    assert alarme and "L1" in alarme[0] and "livro novo" in alarme[0]
