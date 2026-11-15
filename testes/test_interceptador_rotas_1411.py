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


def test_o_disjuntor_da_forma_validada_vai_direto_a_reserva(monkeypatch):
    from eldorado.base.nucleo import ia as IA

    class _IA:
        url = "http://local"

        def disponivel(self):
            return True

        def pedir(self, nome, pedido):
            return {"itens": []}, IA.Uso("comprovar")
    chamadas = []

    def falha(ia, pedido):
        chamadas.append(1)
        raise RuntimeError("ModelAPIError")
    monkeypatch.setattr(IA, "_validado", falha)
    monkeypatch.setitem(IA.DISJUNTOR, "seguidas", 0)
    monkeypatch.setitem(IA.DISJUNTOR, "desligado_ate", 0.0)
    for _ in range(IA.DISJUNTOR_FALHAS + 2):
        IA.comprovar(_IA(), ["Prazo de inscrição"], ["Edital de chamamento. As inscrições estão abertas até 30/11/2026, pelo site."],
                     "Edital", ("Prazo de inscrição",))
    assert len(chamadas) == IA.DISJUNTOR_FALHAS           # depois de 3 falhas seguidas, a forma validada fica em pausa


def test_o_material_que_a_ia_nao_leu_volta_no_proximo_voo():
    fonte = inspect.getsource(M.Interceptador.investigar)
    assert 'f"ia pendente · abordagem {n}" if ("adiada" in ia_d or "estourou" in ia_d)' in fonte
    assert "WHERE fase='preparacao' AND ferramenta LIKE 'abordagem %'" in inspect.getsource(M.fila)   # a pendente não conta


def test_o_livro_sem_link_oficial_passa_pelo_interceptador_antes_do_chrome():
    assert "lv.link_oficial or (lv.link_divulgacao and lv.vp_rodadas == 0)" in inspect.getsource(M.fila)
    from pathlib import Path
    assert "if lid not in na_fila:" in Path("eldorado/base/comandante/cartorio.py").read_text(encoding="utf-8")


def test_o_mapa_do_orgao_e_do_municipio_para_o_site_oficial():
    it = M.Interceptador.__new__(M.Interceptador)
    it.con = sqlite3.connect(":memory:")
    it.con.executescript("CREATE TABLE empresa(nome_fantasia TEXT, razao_social TEXT, site TEXT);"
                         "INSERT INTO empresa VALUES ('Fundação Exemplo', 'Fundação Exemplo S.A.', 'fundacaoexemplo.org.br')")
    assert it._mapa_oficial(_lv(municipio="Anápolis", uf="GO")) == ["https://www.anapolis.go.gov.br/"]
    assert it._mapa_oficial(_lv(municipio="Tupaciguara", uf="MG")) == []                       # outro estado: não
    assert it._mapa_oficial(_lv(orgao="Fundação Exemplo")) == ["https://fundacaoexemplo.org.br"]
