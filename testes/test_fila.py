from eldorado.base.cerebro.governador import Governador, Leitura
from eldorado.base.fluxo.fila import Fila


def fila(tmp_path, carga=0.2, **kw):
    g = Governador(lambda: Leitura(carga, 0.1, 0.3))
    return Fila(tmp_path / "fila.db", tmp_path / "ev", g, tmp_path / "PAUSADO", imediata=True, **kw)


def test_fila_executa_o_workflow(tmp_path):
    r = fila(tmp_path).enfileirar(_wf(tmp_path)).get()
    assert r["estado"] == "concluida"


def test_sem_folga_a_tarefa_se_adia(tmp_path):
    f = fila(tmp_path, carga=0.9)
    r = f.enfileirar(_wf(tmp_path)).get()
    assert r["estado"] == "adiada" and "carga" in r["motivo"] and len(f.agendadas()) == 1


def test_sistema_pausado_adia(tmp_path):
    f = fila(tmp_path)
    (tmp_path / "PAUSADO").write_text("x")
    assert f.enfileirar(_wf(tmp_path)).get()["motivo"] == "sistema pausado"


def test_execucao_reagendada_tem_a_retomada_agendada(tmp_path):
    p = tmp_path / "w.toml"
    p.write_text(f'''[workflow]
id = "r"
[[no]]
id = "a"
tipo = "nos_teste:falhar_vezes"
tentativas = 2
esperas_s = [21600]
parametros = {{ arquivo = "{(tmp_path / 'n').as_posix()}", vezes = 1 }}
''')
    f = fila(tmp_path)
    r = f.enfileirar(p).get()
    assert r["estado"] == "reagendada" and len(f.agendadas()) == 1


def _wf(tmp_path):
    p = tmp_path / "simples.toml"
    p.write_text('[workflow]\nid = "s"\n[[no]]\nid = "a"\ntipo = "eldorado.base.fluxo.nos:passar"\n')
    return p
