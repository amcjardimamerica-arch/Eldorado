"""R55 (titular, 14/11/2026): as correções do Interceptador do parecer das rotas dos pilotos (envio 3)."""
import inspect
import json
import sqlite3

from eldorado.base.cerebro import ciclo_pilotos as C
from eldorado.base.cerebro import pilotos_permanentes as PP
from eldorado.motores.pilotos import interceptador as M


def _lv(**kw):
    base = {"id": "L-1", "titulo": "Edital de chamamento", "orgao": None, "link_oficial": "https://x.org/edital", "link_divulgacao": None,
            "estrela": "sem", "fim": None, "certidoes": {}, "tentadas": set()}
    return M.Livro(**{**base, **kw})


def test_a_abordagem_que_nao_se_aplica_e_pulada_sem_contar():
    lv = _lv()
    assert not M.aplica(9, lv) and not M.aplica(2, lv) and not M.aplica(5, lv) and not M.aplica(11, lv) and not M.aplica(4, lv)
    assert M.aplica(9, _lv(link_oficial="https://x.org/edital.pdf")) and M.aplica(2, _lv(link_divulgacao="https://pncp.gov.br/app/editais/1"))
    assert M.aplica(5, _lv(titulo="Edital nº 12/2026")) and M.aplica(11, _lv(municipio="Anápolis")) and M.aplica(4, _lv(orgao="Fundação X"))
    assert "or not aplica(n, lv)" in inspect.getsource(M.Interceptador.plano_de_voo)       # antes de virar tentativa


def test_o_tempo_por_livro_cabe_na_leitura_da_ia():
    assert PP.TEMPO_LIVRO_S >= 400 and inspect.signature(M.Interceptador.voar).parameters["tempo_livro_s"].default >= 400


def test_o_ciclo_conta_os_itens_dos_extratores_e_so_as_abordagens():
    b = sqlite3.connect(":memory:")
    b.execute("CREATE TABLE tentativa(ferramenta TEXT, resultado TEXT, em TEXT)")
    b.execute("INSERT INTO tentativa VALUES ('abordagem 12', ?, '2026-11-15')", (json.dumps({"ia": {"aceitas": 0, "extratores": ["Prazo", "Valor"]}}),))
    b.execute("INSERT INTO tentativa VALUES ('motor-x', ?, '2026-11-15')", (json.dumps({"trouxe": False}),))
    a = C.avaliar_interceptador(b)
    assert a["erros"] == 0 and a["abordagens"]["abordagem 12"]["aceitos"] == 2 and "motor-x" not in a["abordagens"]


def test_a_abordagem_do_computador_aposentada_e_o_quadro_com_o_teto_real():
    assert M.APOSENTADAS == frozenset({8})
    from eldorado.base.comandante.pilotos import VAGAS_MAX
    assert PP._vagas_max() == VAGAS_MAX and "de {_vagas_max()}" in inspect.getsource(PP)


def test_os_agregadores_dos_livros_sem_link_oficial():
    for d in ("alteditais.com.br", "farolcultural.com.br", "licitario.com.br", "capta.org.br", "editaisdobrasil.com.br", "conjunta.org"):
        assert M.Interceptador.AGREGADORES.search(d), d


def test_o_vigia_de_voo_longo():
    fonte = inspect.getsource(PP.voar_interceptador)
    assert PP.VOO_LONGO_S == 900 and "def vigiar()" in fonte and "voo longo" in fonte and "geracao[k] = geracao.get(k, 0) + 1" in fonte
