"""N-06 (manutenção de 25/11/2026): o mesmo número com valores diferentes — abertas 424 no relatório da titular, 418 nas
abas e na lista, 396 na Sala; Farol 207 no Cartório e 217 na Sala. Cada tela tinha a sua cópia da condição de «aberta»,
sem tirar o mecanismo (R60). R46 (régua única), R19."""
from __future__ import annotations

import re
from pathlib import Path

from conftest import AGORA, ev, livro

from eldorado.base.cartorio.regua import clausula_aberta, regua


def _aberto(lid, fase, tipo=None):
    return [livro(lid, f"k-{lid}"),
            ev("livro.passagem", livro_id=lid, de=None, para=fase, em=AGORA, autorizado_por="regencia", motivo="t"),
            ev("livro.decupado", livro_id=lid, situacao_prazo="aberta", inscricao_fim="2099-12-31", tipo_livro=tipo, validacao="aprovado", validado_em=AGORA)]


def test_abertas_e_farol_tem_o_mesmo_numero_em_todas_as_telas(bancos, gravador):
    evs = _aberto("A", "farol") + _aberto("B", "preparacao") + _aberto("M", "farol", "mecanismo")
    r = gravador.aplicar(evs)
    assert not r.recusados, r.recusados
    bib = bancos["biblioteca"]
    rg = regua(bib)
    lista = bib.execute("SELECT COUNT(*) FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id "
                        f"WHERE {clausula_aberta(bib)}").fetchone()[0]
    sala = bib.execute("SELECT COUNT(*) FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p_ab ON p_ab.livro_id = l.id "
                       f"WHERE {clausula_aberta(bib, 'p_ab')}").fetchone()[0]
    assert rg["abertas"] == lista == sala == 2 and rg["validadas"] == 1 and rg["mecanismos"] == 1
    # nenhuma tela tem a sua própria cópia da condição: todas usam a régua
    for arq in ("eldorado/base/painel/dados.py", "eldorado/base/painel/sala.py", "eldorado/base/comandante/apresentar.py"):
        fonte = Path(arq).read_text(encoding="utf-8")
        assert not re.search(r"situacao_prazo = 'aberta' AND l\.situacao NOT IN \('excluido', 'unido'\) AND p(_ab)?\.fase <> 'arquivo'", fonte), arq
        assert "clausula_aberta" in fonte, arq
    assert "_farol_regua" in Path("eldorado/base/painel/cartorio.py").read_text(encoding="utf-8")
