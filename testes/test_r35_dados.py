"""R35 — A TRAVA ABSOLUTA DOS DADOS (titular, 30/10/2026: "não deve existir cópia de nenhum site; o sistema não é repositório
de sites nem de arquivos; os dados são uma trava absoluta, que não devem ter nenhum dado fora do Cérebro ou da Biblioteca,
onde cada um tem sua finalidade; jamais mude esta regra").

Fica o texto da oportunidade (os dados do livro e as certidões, com o trecho literal do edital) e os endereços (o site
oficial e o de divulgação). A leitura de um site é efêmera: serve ao Cartório e sai."""

import sqlite3
from pathlib import Path


def _base(tmp):
    from eldorado.base.fluxo.nos import abrir_bancos
    from eldorado.base.nucleo.eventos import Diario
    from eldorado.base.nucleo.gravador import Gravador

    ev = tmp / "eventos"
    (tmp / "dados").mkdir()
    g = Gravador(abrir_bancos(str(tmp / "dados")))
    d = Diario(ev, "motor-x")
    d.emitir(
        "documento.registrado",
        "motor-x",
        {"url": "https://site.gov.br/edital.pdf", "sha256": "abc", "tipo": "pdf", "paginas": 1, "obtido_em": "2026-10-29T00:00:00+00:00"},
    )
    d.emitir("pagina.gravada", "motor-x", {"documento_sha256": "abc", "numero": 1, "texto": "EDITAL 01/2026 inscrições até 10/11"})
    return ev, g


def test_a_leitura_do_site_nunca_entra_no_historico(tmp_path):
    from eldorado.base.nucleo.eventos import pasta_efemera

    ev, _ = _base(tmp_path)
    assert not any("pagina.gravada" in linha for f in ev.rglob("*.jsonl") for linha in open(f, encoding="utf-8"))
    assert any("pagina.gravada" in linha for f in pasta_efemera(ev).rglob("*.jsonl") for linha in open(f, encoding="utf-8"))


def test_a_leitura_serve_ao_cartorio_e_sai_do_banco_e_o_endereco_fica(tmp_path):
    from eldorado.base.cartorio.leitura_efemera import expurgar
    from eldorado.base.nucleo.eventos import ler

    ev, g = _base(tmp_path)
    assert not g.aplicar(list(ler(ev))).recusados
    bib = sqlite3.connect(tmp_path / "dados" / "biblioteca.db")
    assert bib.execute("SELECT COUNT(*) FROM pagina").fetchone()[0] == 1  # o Cartório pode certificar
    assert expurgar(tmp_path / "dados" / "biblioteca.db", ev, horas=0)["documentos"] == 1
    assert not g.aplicar(list(ler(ev))).recusados
    assert bib.execute("SELECT COUNT(*) FROM pagina").fetchone()[0] == 0
    assert bib.execute("SELECT COUNT(*) FROM busca WHERE busca MATCH 'edital'").fetchone()[0] == 0
    assert bib.execute("SELECT url FROM documento").fetchone()[0] == "https://site.gov.br/edital.pdf"


def test_nenhuma_copia_de_site_no_historico_do_repositorio():
    """A varredura do histórico inteiro: nenhuma leitura de site gravada (eram 70.427, 264 MB)."""
    for f in Path("eventos").rglob("*.jsonl"):
        with open(f, "rb") as h:
            for linha in h:
                assert b'"tipo":"pagina.gravada"' not in linha[:200], f"cópia de site no histórico: {f}"


def test_o_expurgo_depois_de_cada_passagem_e_a_releitura_desligada():
    from eldorado.base.cartorio import releitura

    c = Path("eldorado/base/nucleo/comandos.py").read_text(encoding="utf-8")
    assert "_expurgar_leituras(" in c
    assert releitura.escolher(None, None, 50) == []
    assert "dados/leitura_efemera/" in Path(".gitignore").read_text(encoding="utf-8")
    assert "leitura_efemera" not in Path("scripts/gravar.sh").read_text(encoding="utf-8")
