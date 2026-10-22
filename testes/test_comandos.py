import shutil

from typer.testing import CliRunner

from eldorado.base.nucleo.comandos import ADIADO, app

R = CliRunner()


def preparar(tmp_path):
    (tmp_path / "config").mkdir()
    shutil.copy("config/eldorado.toml", tmp_path / "config")
    return str(tmp_path / "config" / "eldorado.toml")


def test_iniciar_executar_e_aplicar(tmp_path, monkeypatch):
    cfg = preparar(tmp_path)
    monkeypatch.setattr("eldorado.base.nucleo.comandos.Governador.pode_iniciar", lambda self, *a, **k: True)
    assert R.invoke(app, ["iniciar", "--config", cfg]).exit_code == 0
    wf = tmp_path / "w.toml"
    wf.write_text('[workflow]\nid = "s"\n[[no]]\nid = "a"\ntipo = "eldorado.base.fluxo.nos:passar"\n')
    r = R.invoke(app, ["executar", str(wf), "--config", cfg, "--entrada", '[{"a": 1}]'])
    assert r.exit_code == 0 and '"concluida"' in r.output
    r = R.invoke(app, ["aplicar", "--config", cfg])
    assert r.exit_code == 0 and "recusados 0" in r.output
    assert "aplicados 0" in R.invoke(app, ["aplicar", "--config", cfg]).output


def test_pausado_nao_executa(tmp_path):
    cfg = preparar(tmp_path)
    R.invoke(app, ["pausar", "--config", cfg])
    r = R.invoke(app, ["executar", "workflows/manutencao.toml", "--config", cfg])
    assert r.exit_code == ADIADO and "pausado" in r.output
    R.invoke(app, ["despausar", "--config", cfg])
    assert not (tmp_path / "dados" / "PAUSADO").exists()


def test_sem_folga_adia(tmp_path, monkeypatch):
    cfg = preparar(tmp_path)
    monkeypatch.setattr("eldorado.base.nucleo.comandos.Governador.pode_iniciar", lambda self, *a, **k: False)
    monkeypatch.setattr("eldorado.base.nucleo.comandos.Governador.motivo", lambda self: "carga 90%")
    assert R.invoke(app, ["executar", "workflows/manutencao.toml", "--config", cfg]).exit_code == ADIADO


def test_maquina_mostra_a_folga(tmp_path):
    r = R.invoke(app, ["maquina", "--config", preparar(tmp_path)])
    assert r.exit_code == 0 and "limite 85%" in r.output
