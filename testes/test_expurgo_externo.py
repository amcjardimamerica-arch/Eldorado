"""O expurgo físico pela análise externa: apaga o livro e os dependentes, recria as travas e registra; a automação segue travada."""
import sqlite3

import pytest
from conftest import AGORA, ev

from eldorado.base.nucleo.expurgo_externo import expurgar


def test_expurgo_apaga_dependentes_recria_travas_e_registra(gravador, bancos):
    livro = lambda i: ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo=f"Livro {i}", estrela="sem", selo_livro="sem",  # noqa: E731
                         informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA)
    assert gravador.aplicar([livro("A"), livro("B"),
                             ev("certidao.gravada", livro_id="A", item="Objeto", valor="fomento", fase="certificacao", situacao="comprovado", em=AGORA),
                             ev("veredito.gravado", livro_id="A", origem="chrome", decisao="valida", em=AGORA),
                             ev("livro.passagem", livro_id="A", de=None, para="certificacao", em=AGORA, autorizado_por="regencia"),
                             ev("livro.unido", livro_que_fica="B", livro_unido="A", em=AGORA, motivo="mesma chave")]).ok
    b, c = bancos["biblioteca"], bancos["cerebro"]
    with pytest.raises(ValueError):
        expurgar(b, c, ["A"], "curto")
    r = expurgar(b, c, ["A"], "não é oportunidade (validação de 22/10/2026)")
    assert r["livros"] == 1 and r["por_tabela"]["certidao.livro_id"] == 1 and r["por_tabela"]["cerebro.rotulo"] == 1
    assert [x[0] for x in b.execute("SELECT id FROM livro")] == ["B"]
    for t in ("certidao", "veredito", "passagem", "uniao", "passaporte"):
        assert b.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == 0, t
    with pytest.raises(sqlite3.DatabaseError):                       # as travas voltaram: a automação continua sem apagar
        b.execute("DELETE FROM livro WHERE id='B'")
    reg = b.execute("SELECT livros, motivo, ids FROM expurgo_externo").fetchone()
    assert reg[0] == 1 and "validação" in reg[1] and reg[2] == '["A"]'
    with pytest.raises(sqlite3.DatabaseError):
        b.execute("DELETE FROM expurgo_externo")
    with pytest.raises(sqlite3.DatabaseError):
        b.execute("UPDATE expurgo_externo SET motivo='x'")
