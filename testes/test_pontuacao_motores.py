"""05/11/2026 (titular): a pontuação de cada motor — os acertos parametrizados com os erros, e o indicador abaixo do fósforo."""
import json
import sqlite3
from pathlib import Path

from eldorado.base.cerebro.pontuacao_motores import calcular, parametros


def _bib():
    b = sqlite3.connect(":memory:")
    b.executescript("CREATE TABLE achado(livro_id TEXT, motor TEXT, encontrado_em TEXT);"
                    "CREATE TABLE livro(id TEXT, situacao TEXT, criado_em TEXT, justificativa_exclusao TEXT);"
                    "CREATE TABLE passaporte(livro_id TEXT, fase TEXT);")
    for i, (sit, fase) in enumerate([("aguardando", "farol"), ("excluido", "arquivo"), ("excluido", "arquivo"), ("aguardando", "arquivo")]):
        b.execute("INSERT INTO achado VALUES (?, 'site-rede-comua', '2026-11-01')", (f"L{i}",))
        b.execute("INSERT INTO livro VALUES (?, ?, '2026-11-03', ?)", (f"L{i}", sit, "página institucional do órgão" if sit == "excluido" else ""))
        b.execute("INSERT INTO passaporte VALUES (?, ?)", (f"L{i}", fase))
    return b


def test_acertos_contra_erros_e_as_indicacoes(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "pontuacao_motores.toml").write_text(Path("config/pontuacao_motores.toml").read_text(encoding="utf-8"), encoding="utf-8")
    v = tmp_path / "verificacao" / "vereditos" / "importados"
    v.mkdir(parents=True)
    v.joinpath("x.json").write_text(json.dumps({"vereditos": [{"livro_id": "L3", "decisao": "valido"}]}))
    r = calcular(_bib(), None, tmp_path)["site-rede-comua"]
    assert (r["acertos"], r["erros"]) == (2, 2) and r["precisao"] == 0.5          # o Farol e o válido; os dois expurgos
    assert r["erros_por_tipo"] == {"pagina_institucional": 2} and r["melhorias"][0]["tipo"] == "pagina_institucional"
    assert r["faixa"] == "formacao"                                                    # 4 decididos (< 5): em formação


def test_os_pesos_somam_100_e_o_indicador_substitui_os_botoes():
    assert sum(parametros()["pesos"].values()) == 100
    h = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    # 05/11/2026 (titular): ao lado dos dados de cima, acima do calendário, encostado ao fósforo; azul e laranja
    assert '</div>${pmIndicador(o.id)}</div>' in h and '<div class="mt-lado-dir">${iconesAcao(o.id,o.nome)}</div>' in h
    assert "mt-ico upload" not in h and "mt-ico link" not in h and 'stroke="#0B4EA2"' in h and 'stroke="#E07B00"' in h
