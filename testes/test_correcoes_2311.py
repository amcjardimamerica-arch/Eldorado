"""Manutenção de 23/11/2026 — as correções do relatório (C-01 a C-10)."""
import json
import re
from pathlib import Path


def _config(tmp_path):
    s = Path("config/eldorado.toml").read_text(encoding="utf-8")
    s = re.sub(r'(?m)^dados\s*=.*$', f'dados = "{tmp_path / "dados"}"', s)
    s = re.sub(r'(?m)^eventos\s*=.*$', f'eventos = "{tmp_path / "eventos"}"', s)
    (tmp_path / "eldorado.toml").write_text(s, encoding="utf-8")
    (tmp_path / "dados").mkdir()
    return tmp_path / "eldorado.toml"


def _lei(diario, n):
    diario.emitir("lei.registrada", "teste", {"id": f"L{n}", "esfera": "federal", "numero": f"Lei {n}", "ementa": "x", "situacao": "vigente",
                                              "link_oficial": None, "atualizada_em": "2026-11-23"})


def _aplicar(comandos, cfg):
    import pytest
    import typer
    with pytest.raises(typer.Exit) as fim:
        comandos.aplicar(cfg)
    assert fim.value.exit_code == 0                         # nenhum evento recusado


def test_a_execucao_restaura_os_bancos_da_anterior_e_aplica_so_os_eventos_novos(tmp_path):
    """C-01: com os bancos e a marca dados/aplicados.json da execução anterior, o aplicar lê só os arquivos novos."""
    from eldorado.base.nucleo import comandos
    cfg = _config(tmp_path)
    from eldorado.base.nucleo.eventos import Diario
    _lei(Diario(tmp_path / "eventos", "execucao-a"), 1)
    _aplicar(comandos, cfg)                                 # a «execução anterior»: aplica e marca
    marca = json.loads((tmp_path / "dados" / "aplicados.json").read_text(encoding="utf-8"))
    assert any("execucao-a" in k for k in marca["arquivos"])
    _lei(Diario(tmp_path / "eventos", "execucao-b"), 2)
    lidos = []
    import eldorado.base.nucleo.eventos as ev
    ler_original = ev.ler

    def espia(raiz, **k):
        for x in ler_original(raiz, **k):
            lidos.append(x)
            yield x
    comandos_ler = getattr(comandos, "ler", None)
    try:
        comandos.ler = espia
        _aplicar(comandos, cfg)                             # a execução seguinte, com os bancos e a marca guardados
    finally:
        if comandos_ler is not None:
            comandos.ler = comandos_ler
    assert [x.dados["id"] for x in lidos] == ["L2"]         # só o arquivo novo


def test_o_fluxo_restaura_a_guarda_antes_de_iniciar_e_salva_sempre():
    """C-01: o YAML tem o passo de restaurar antes de «eldorado iniciar» e o de salvar com if: always()."""
    import yaml
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    nomes = [p.get("uses", "") + "|" + p.get("run", "") for p in passos]
    restaura = next(i for i, n in enumerate(nomes) if "actions/cache/restore" in n)
    inicia = next(i for i, n in enumerate(nomes) if "eldorado iniciar" in n)
    assert restaura < inicia
    fim = [p for p in passos if "actions/cache/save" in p.get("uses", "") and p.get("with", {}).get("key", "").endswith("-fim")]
    assert fim and fim[0].get("if") == "always()" and "dados/aplicados.json" in fim[0]["with"]["path"]
    assert sum("actions/cache/save" in p.get("uses", "") for p in passos) == 6               # 5 blocos de hora e o fim


def test_a_avaliacao_herdada_sem_porque_ganha_o_motivo_e_nao_derruba_o_ranking(tmp_path):
    """23/11/2026: na produção, a empresa com a ficha do Eldorado0 (coluna que o banco de amostra não tem) e a avaliação
    herdada sem «porque» derrubava o ranking — a trava caía no portão das regras e o sistema parou desde a madrugada de 23/11."""
    import shutil
    import sqlite3

    from eldorado.base.painel.dados import _molde
    from eldorado.base.painel.ranking import montar
    shutil.copy("dados/biblioteca.db", tmp_path / "b.db")
    con = sqlite3.connect(tmp_path / "b.db")
    if "ficha" not in {r[1] for r in con.execute("PRAGMA table_info(empresa)")}:
        con.execute("ALTER TABLE empresa ADD COLUMN ficha TEXT")
    cnpj = con.execute("SELECT cnpj FROM empresa LIMIT 1").fetchone()[0]
    con.execute("UPDATE empresa SET ficha = ? WHERE cnpj = ?",
                (json.dumps({"eldorado0": {"pontos_lista": 999, "pontuacao": {"base": 90}, "nivel": "ouro"}}), cnpj))
    con.commit()
    r = montar(con, _molde)
    e = next(x for x in r["empresas"] if x["pontos_lista"] == 999)                     # a empresa da ficha herdada
    assert "Eldorado0" in e["pontuacao"]["porque"]
    assert all(x["pontuacao"]["porque"] for x in r["empresas"])


def test_todo_passo_antes_do_laco_tem_limite_de_tempo():
    """C-02: uma execução ficou 11 h sem passagem — todo passo antes do laço tem timeout-minutes."""
    import yaml
    passos = yaml.safe_load(Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8"))["jobs"]["passagem"]["steps"]
    i_laco = next(i for i, p in enumerate(passos) if p.get("name", "").startswith("Funcionamento permanente"))
    sem = [p.get("name") for p in passos[:i_laco] if "run" in p and "timeout-minutes" not in p
           and not p.get("name", "").startswith(("A hora do começo", "Conferir a guarda"))]
    assert sem == [], f"passos sem limite de tempo: {sem}"
    reaplicar = next(p for p in passos if p.get("name") == "Reaplicar os eventos pendentes")
    assert "45" in str(reaplicar["timeout-minutes"]) and "240" in str(reaplicar["timeout-minutes"])   # com e sem a guarda


def test_o_vigia_cancela_e_religa_o_ciclo_travado():
    """C-02: o vigia só religava sem ciclo nenhum; o ciclo travado (gravação e execução há mais de 90 min) é cancelado e
    religado — e a remontagem sem guarda (Reaplicar, até 240 min) não é travamento."""
    import yaml
    run = yaml.safe_load(Path(".github/workflows/vigia.yml").read_text(encoding="utf-8"))["jobs"]["vigiar"]["steps"][0]["run"]
    assert '[ "$idade" -gt 90 ] && [ "$idade_ciclo" -gt 90 ]' in run and 'gh run cancel "$run_id"' in run
    assert '"Reaplicar os eventos pendentes"*)' in run and "o passo em curso" in run


def _painel():
    import yaml
    return yaml.safe_load(Path(".github/workflows/painel.yml").read_text(encoding="utf-8"))["jobs"]["publicar"]["steps"]


def test_a_chave_da_guarda_do_painel_nao_expira_por_semana_nem_por_codigo():
    """C-03: a chave mudava a cada semana e a cada mudança de código — na segunda-feira a guarda zerou e o site parou."""
    texto = Path(".github/workflows/painel.yml").read_text(encoding="utf-8")
    assert "hashFiles(" not in texto and "semana.outputs" not in texto
    rest = next(p for p in _painel() if "actions/cache/restore" in p.get("uses", ""))
    assert rest["with"]["key"] == "painel-bancos-${{ github.run_id }}"
    assert rest["with"]["restore-keys"].split() == ["eldorado-bancos-", "painel-bancos-"]     # a guarda do ciclo primeiro


def test_o_site_publica_com_a_sala_da_producao_quando_a_aplicacao_nao_termina():
    """C-03: a aplicação que não cabe no tempo não impede a publicação — os livros voltam à guarda (coerentes, sem números
    misturados) e a tela avisa a hora deles; a Sala é a medida pela produção."""
    import inspect

    from eldorado.base.painel import dados
    passos = _painel()
    nomes = [p.get("name", "") for p in passos]
    ap = passos[nomes.index("Os eventos mais recentes no banco (o estado de agora)")]
    assert ap.get("continue-on-error") is True and ap.get("timeout-minutes") == 12
    volta = next(p for p in passos if "ELDORADO_LIVROS_DE" in p.get("run", ""))
    assert "steps.aplicar.outcome != 'success'" in volta["if"] and "/tmp/guarda_antes/biblioteca.db" in volta["run"]
    gera = next(p for p in passos if p.get("name", "").startswith("Gerar o site"))
    assert "if" not in gera                                                                   # publica sempre
    assert 'os.environ.get("ELDORADO_LIVROS_DE")' in inspect.getsource(dados.gerar)
