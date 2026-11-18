"""17/11/2026 (C-23): os três arquivos críticos que não tinham teste — eldorado/banco/consolidar.py,
.github/workflows/eldorado.yml e workflows/passagem.toml."""
import sqlite3
from pathlib import Path


def test_a_consolidacao_traz_o_banco_do_motor_para_o_cerebro_sem_duplicar(tmp_path):
    """eldorado/banco/consolidar.py: o banco paralelo de cada motor entra no Cérebro (motor_entregue), uma vez."""
    from eldorado.banco.consolidar import consolidar
    (tmp_path / "motores").mkdir()
    m = sqlite3.connect(tmp_path / "motores" / "site-x.db")
    m.execute("CREATE TABLE entregue (chave TEXT, em TEXT, achado TEXT, fonte TEXT)")
    m.executemany("INSERT INTO entregue VALUES (?, '2026-11-17', NULL, 'f')", [("a",), ("b",)])
    m.commit()
    m.close()
    r1 = consolidar(tmp_path)
    r2 = consolidar(tmp_path)
    c = sqlite3.connect(tmp_path / "cerebro.db")
    assert r1["motores"] == 1 and c.execute("SELECT COUNT(*) FROM motor_entregue WHERE motor = 'site-x'").fetchone()[0] == 2
    assert not (tmp_path / "motores" / "site-x.db").exists()                       # o banco paralelo é apagado depois de copiado
    assert r2["motores"] == 0 and c.execute("SELECT COUNT(*) FROM motor_entregue").fetchone()[0] == 2            # nada duplica


def test_o_workflow_eldorado_aplica_os_eventos_confere_as_travas_e_roda_a_passagem():
    """.github/workflows/eldorado.yml: a ordem que mantém o sistema de pé — iniciar, aplicar, consolidar, travas, permanente."""
    t = Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")
    ordem = ["eldorado iniciar", "eldorado aplicar", "eldorado consolidar-bancos", "eldorado travas", "eldorado permanente"]
    pos = 0
    for x in ordem:                                  # cada passo depois do anterior (o cabeçalho cita alguns em comentário)
        pos = t.find(f"run: {x}", pos) if f"run: {x}" in t[pos:] else t.find(x, pos)
        assert pos >= 0, x
    # funcionamento permanente (titular, 22/10/2026): sem horário fixo — cada execução dispara a próxima
    assert "workflow_dispatch" in t and "actions/workflows/eldorado.yml/dispatches" in t


def test_a_passagem_declara_nos_que_existem():
    """workflows/passagem.toml: cada nó aponta para uma função que existe (modulo:funcao) — nenhum nó fantasma."""
    import importlib
    import tomllib
    wf = tomllib.loads(Path("workflows/passagem.toml").read_text(encoding="utf-8"))
    assert wf["no"]
    for n in wf["no"]:
        mod, fun = n["tipo"].split(":")
        assert callable(getattr(importlib.import_module(mod), fun)), n["id"]
