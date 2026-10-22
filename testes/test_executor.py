import subprocess
import sys
import textwrap
from pathlib import Path

from eldorado.base.fluxo.definicao import de_dicionario
from eldorado.base.fluxo.executor import Executor
from eldorado.base.nucleo.eventos import Diario, ler

T = "nos_teste:"


def wf(nos, conexoes=()):
    return de_dicionario({"workflow": {"id": "teste"}, "no": nos, "conexao": list(conexoes)})


def linha(ids, **extra):
    return wf([{"id": i, "tipo": T + "contar", "parametros": extra} for i in ids], [{"de": a, "para": b} for a, b in zip(ids, ids[1:], strict=False)])


def eventos_da(execucao, pasta):
    return Diario(pasta, execucao).eventos()


def test_execucao_linear_com_recibo_medido(tmp_path):
    r = Executor(linha(["a", "b", "c"]), tmp_path).executar([{"x": 1}])
    assert r.estado == "concluida" and r.saidas["c"][0]["passou_por"] == ["a", "b", "c"]
    recibos = [e.dados for e in eventos_da(r.execucao, tmp_path) if e.tipo == "chamada.recibo"]
    assert len(recibos) == 3 and all(x["ok"] == 1 and x["cpu_ms"] is not None and x["memoria_pico_kb"] is not None for x in recibos)


def test_tentativas_com_espera_curta_e_sucesso(tmp_path):
    esperas = []
    d = wf([{"id": "a", "tipo": T + "falhar_vezes", "tentativas": 3, "esperas_s": [1, 2], "parametros": {"arquivo": str(tmp_path / "n"), "vezes": 2}}])
    r = Executor(d, tmp_path / "ev", dormir=esperas.append).executar()
    assert r.estado == "concluida" and r.saidas["a"][0]["chamada"] == 3 and esperas == [1, 2]
    recibos = [e.dados["ok"] for e in eventos_da(r.execucao, tmp_path / "ev") if e.tipo == "chamada.recibo"]
    assert recibos == [0, 0, 1]


def test_esgotar_sem_saida_de_erro_falha_com_alarme(tmp_path):
    d = wf([{"id": "a", "tipo": T + "sempre_falha", "tentativas": 2}])
    r = Executor(d, tmp_path, dormir=lambda s: None).executar()
    assert r.estado == "falhou" and "sempre falha" in r.erro
    assert any(e.tipo == "alarme.aberto" for e in eventos_da(r.execucao, tmp_path))


def test_esgotar_com_saida_de_erro_desvia(tmp_path):
    d = wf([{"id": "a", "tipo": T + "sempre_falha"}, {"id": "seguinte", "tipo": T + "contar"}, {"id": "devolucao", "tipo": T + "contar"}],
           [{"de": "a", "para": "seguinte"}, {"de": "a", "para": "devolucao", "saida": "erro"}])
    r = Executor(d, tmp_path).executar([{"livro": "L1"}])
    assert r.estado == "concluida" and "seguinte" not in r.saidas
    assert r.saidas["devolucao"][0]["erro"].startswith("ValueError") and r.saidas["devolucao"][0]["itens"] == [{"livro": "L1"}]


def test_saida_que_nao_e_lista_conta_como_falha(tmp_path):
    r = Executor(wf([{"id": "a", "tipo": T + "devolve_errado"}]), tmp_path).executar()
    assert r.estado == "falhou" and "lista de dicionários" in r.erro


def test_dados_fixos_nao_chamam_a_funcao(tmp_path):
    d = wf([{"id": "a", "tipo": T + "nao_deveria_rodar", "fixo": [{"pagina": "gravada"}]}, {"id": "b", "tipo": T + "contar"}], [{"de": "a", "para": "b"}])
    r = Executor(d, tmp_path).executar()
    assert r.estado == "concluida" and r.saidas["b"][0]["pagina"] == "gravada"


def test_linhagem_passa_de_no_em_no(tmp_path):
    r = Executor(linha(["a", "b"]), tmp_path).executar([{"_linhagem": {"livro": "L9", "achado": "A9"}}])
    assert r.saidas["b"][0]["_linhagem"] == {"livro": "L9", "achado": "A9"}


def test_espera_longa_reagenda_e_a_retomada_continua_da_tentativa_seguinte(tmp_path):
    d = wf([{"id": "a", "tipo": T + "falhar_vezes", "tentativas": 3, "esperas_s": [21600, 86400], "parametros": {"arquivo": str(tmp_path / "n"), "vezes": 1}},
            {"id": "b", "tipo": T + "contar"}], [{"de": "a", "para": "b"}])
    ex = Executor(d, tmp_path / "ev")
    r1 = ex.executar()
    assert r1.estado == "reagendada" and r1.reagendar_em_s == 21600 and r1.no_reagendado == "a"
    r2 = ex.retomar(r1.execucao)
    assert r2.estado == "concluida" and r2.saidas["a"][0]["chamada"] == 2          # a 1ª tentativa não foi repetida


def test_retomar_execucao_concluida_nao_reexecuta(tmp_path):
    cont = tmp_path / "cont"
    ex = Executor(linha(["a", "b"], contador=str(cont)), tmp_path / "ev")
    r = ex.executar()
    ex.retomar(r.execucao)
    assert cont.read_text().split() == ["a", "b"]


def test_queda_real_do_processo_retoma_do_mesmo_passo(tmp_path):
    """Critério de pronto da Fase 2: o processo é derrubado no 3º nó; a retomada não repete os nós 1 e 2."""
    cont, marca, ev = tmp_path / "cont", tmp_path / "marca", tmp_path / "ev"
    nos = [{"id": "a", "tipo": T + "contar", "parametros": {"contador": str(cont)}},
           {"id": "b", "tipo": T + "contar", "parametros": {"contador": str(cont)}},
           {"id": "c", "tipo": T + "derrubar_uma_vez", "parametros": {"contador": str(cont), "marca": str(marca)}},
           {"id": "d", "tipo": T + "contar", "parametros": {"contador": str(cont)}}]
    con = [{"de": "a", "para": "b"}, {"de": "b", "para": "c"}, {"de": "c", "para": "d"}]
    roteiro = textwrap.dedent(f"""
        import sys; sys.path[:0] = {[str(Path(__file__).parent), str(Path(__file__).parent.parent)]!r}
        from eldorado.base.fluxo.definicao import de_dicionario
        from eldorado.base.fluxo.executor import Executor
        d = de_dicionario({{"workflow": {{"id": "teste"}}, "no": {nos!r}, "conexao": {con!r}}})
        Executor(d, {str(ev)!r}).executar([{{"livro": "L1"}}], execucao="exec-queda")
    """)
    p = subprocess.run([sys.executable, "-c", roteiro], capture_output=True, text=True)
    assert p.returncode == 1, p.stderr                                   # o processo caiu de verdade
    assert cont.read_text().split() == ["a", "b", "c"]
    r = Executor(wf(nos, con), ev).retomar("exec-queda")
    assert r.estado == "concluida"
    assert cont.read_text().split() == ["a", "b", "c", "c", "d"]         # a e b não rodaram de novo; c recomeçou; d rodou
    assert r.saidas["d"][0]["livro"] == "L1"                              # a entrada original foi recuperada do diário


def test_eventos_do_executor_sao_aceitos_pelo_gravador(tmp_path, gravador, bancos):
    Executor(linha(["a", "b"]), tmp_path / "ev").executar([{"x": 1}])
    r = gravador.aplicar(ler(tmp_path / "ev"))
    assert r.ok, r.recusados
    c = bancos["cerebro"]
    assert c.execute("SELECT estado FROM execucao").fetchone()[0] == "concluida"
    assert c.execute("SELECT COUNT(*) FROM recibo WHERE cpu_ms IS NOT NULL AND memoria_pico_kb IS NOT NULL").fetchone()[0] == 2
    assert c.execute("SELECT COUNT(*) FROM workflow").fetchone()[0] == 1


def test_ligacao_de_ordem_nao_passa_dados(tmp_path):
    d = wf([{"id": "a", "tipo": T + "contar"}, {"id": "b", "tipo": T + "contar"}, {"id": "c", "tipo": T + "contar"}],
           [{"de": "a", "para": "c"}, {"de": "b", "para": "c", "saida": "ordem"}])
    r = Executor(d, tmp_path).executar([{"x": 1}])
    assert r.estado == "concluida" and len(r.saidas["c"]) == 1 and r.saidas["c"][0]["passou_por"] == ["a", "c"]
    d2 = wf([{"id": "a", "tipo": T + "contar"}, {"id": "depois", "tipo": T + "contar"}], [{"de": "a", "para": "depois", "saida": "ordem"}])
    r2 = Executor(d2, tmp_path / "2").executar([{"x": 1}])
    assert r2.saidas["depois"] == [{"passou_por": ["depois"]}]           # rodou depois, sem receber os itens de "a"
