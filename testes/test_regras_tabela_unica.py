"""A tabela única das regras da titular (reativada em 25/10/2026): as duas fontes, a vigência por tema e a contradição."""
from types import SimpleNamespace

from eldorado.base.cerebro.regras import Regra, Regras, carregar_tudo, no_regras
from eldorado.base.nucleo.eventos import ler


def test_a_tabela_unica_nao_tem_contradicao_e_a_mais_recente_vale():
    r = carregar_tudo(".")
    assert not r.contradicoes(), f"contradição entre regras: a titular decide ({r.contradicoes()})"   # o portão recusa
    assert r.vigente("acesso a sites").regra.startswith("R03")            # o robots.txt é informação (substituiu "é lei")
    assert len({x.tema for x in r.regras}) == len(r.temas()) and len(r.regras) >= 39


def test_a_contradicao_vira_alarme_uma_vez_so(bancos, gravador, diario, tmp_path):
    r = Regras([Regra("t", "a", "2026-10-25", True), Regra("t", "b", "2026-10-25", True)])
    msg = "contradição no tema 't': 2 regras com o mesmo peso e textos diferentes"
    r.registrar(diario)
    r.registrar(diario, {msg})                                             # já aberto: não se repete
    assert sum(1 for e in ler(tmp_path / "eventos") if e.tipo == "alarme.aberto") == 1


def test_o_no_registra_a_tabela_sem_duplicar(bancos, gravador, diario, tmp_path):
    for _ in range(2):
        no_regras([], {"dados": str(tmp_path), "raiz": "."}, SimpleNamespace(diario=diario))
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok                # idempotente: o mesmo id atualiza
    n = bancos["cerebro"].execute("SELECT COUNT(*) FROM regra").fetchone()[0]
    assert n == len(carregar_tudo(".").regras)
