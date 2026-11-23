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
