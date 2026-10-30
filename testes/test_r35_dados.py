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
    # o documento do ensaio não pertence a nenhum livro: sai inteiro (a leitura e o endereço); o de livro fica com o endereço
    assert bib.execute("SELECT COUNT(*) FROM documento").fetchone()[0] == 0


def test_nenhuma_copia_de_site_no_historico_do_repositorio():
    """A varredura do histórico inteiro: nenhuma leitura de site gravada (eram 70.427, 264 MB)."""
    from datetime import date, timedelta

    ontem = (date.today() - timedelta(days=1)).strftime("%Y/%m/%d")
    for f in Path("eventos").rglob("*.jsonl"):
        dia = "/".join(f.parts[1:4]) if len(f.parts) > 4 else ""
        if dia > ontem:  # o dia corrente: o expurgo depois de cada passagem tira o resíduo da transição (48 h)
            continue
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


def test_o_que_nao_virou_livro_sai_e_o_livro_fica(gravador, bancos, diario, tmp_path):
    """R35 (titular: "não exclua nenhum livro, apenas os dados que não são livros; o Cérebro mantém o seu aprendizado"): o
    achado sem livro sai da Biblioteca e o registro dele (sem conteúdo) fica no Cérebro; o achado de livro não se apaga."""
    import pytest

    b, c = bancos["biblioteca"], bancos["cerebro"]
    b.execute(
        "INSERT INTO achado(id, motor, encontrado_em, titulo, link_divulgacao, dados, decisao) VALUES ('A1', 'dou', '2026-10-01', 'aviso de licitação', 'https://x', '{}', 'barrado')"
    )
    assert gravador.aplicar(
        [
            __import__("eldorado.base.nucleo.eventos", fromlist=["criar"]).criar(
                "achado.descartado",
                "r35",
                {
                    "id": "A1",
                    "motor": "dou",
                    "encontrado_em": "2026-10-01",
                    "decisao": "barrado",
                    "motivo": "licitação",
                    "link": "https://x",
                    "descartado_em": "2026-10-30T12:00:00+00:00",
                },
            )
        ]
    ).ok
    assert b.execute("SELECT COUNT(*) FROM achado WHERE id = 'A1'").fetchone()[0] == 0
    assert c.execute("SELECT motivo FROM achado_descartado WHERE id = 'A1'").fetchone()[0] == "licitação"
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, situacao, criado_em, atualizado_em) VALUES ('L1', 'oportunidades', 'k', 't', 'em trabalho', '2026-10-01', '2026-10-01')"
    )
    b.execute(
        "INSERT INTO achado(id, motor, encontrado_em, titulo, link_divulgacao, dados, decisao, livro_id) VALUES ('A2', 'dou', '2026-10-01', 't', 'https://y', '{}', 'aceito', 'L1')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        b.execute("DELETE FROM achado WHERE id = 'A2'")  # o achado de livro fica
    s = Path("eldorado/motores/canal/estado.py").read_text(encoding="utf-8")
    assert "SELECT 1 FROM achado_descartado WHERE id = ?" in s  # o canal não entrega de novo
    assert "achado_descartado GROUP BY motor" in Path("eldorado/base/comandante/decidir.py").read_text(encoding="utf-8")


def test_as_excecoes_empresas_e_propostas_legislativas_ficam():
    """R35 — as exceções da titular (30/10/2026): as empresas e as propostas legislativas ficam na Biblioteca. Os achados
    dos motores legislativos ficam mesmo sem livro; o descarte nunca alcança empresa, incentivo, lei nem livro_lei."""
    from eldorado.base.cartorio.leitura_efemera import MOTORES_LEGISLATIVOS

    assert set(MOTORES_LEGISLATIVOS) == {"alego-pl", "camara-goiania-pl", "congresso-nacional"}
    s = Path("eldorado/base/cartorio/leitura_efemera.py").read_text(encoding="utf-8")
    assert "motor NOT IN" in s and "OR motor IN" in s
    g = Path("eldorado/base/nucleo/gravador.py").read_text(encoding="utf-8")
    for t in ("empresa", "incentivo", "lei", "livro_lei"):
        assert f"DELETE FROM {t} " not in g and f"DELETE FROM {t}\\n" not in g
