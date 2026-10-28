"""O Comandante atualiza a Biblioteca (titular, 25/10/2026): a base de cada livro (os 5 dados), a fila de completar com 2
tentativas e 30 minutos entre elas, o Chrome depois da 2ª, a exclusão do não validado e o Interceptador com 5 voos."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from eldorado.base.comandante import biblioteca as CB
from eldorado.base.nucleo.eventos import Diario, ler


def _livro(b, i, titulo, oficial, divulg, fim=None, esfera=None, area=None, prazo=None):
    agora = datetime.now(timezone.utc).isoformat()
    b.execute(
        "INSERT INTO livro(id, missao, chave, titulo, orgao, uf, link_oficial, link_divulgacao, estrela, selo_livro, informacoes_validadas, situacao, "
        "criado_em, atualizado_em) VALUES (?, 'oportunidades', ?, ?, '', 'GO', ?, ?, 'sem', 'sem', 0, 'em trabalho', ?, ?)",
        (i, i, titulo, oficial, divulg, agora, agora),
    )
    b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES (?, 'preparacao', ?)", (i, agora))
    b.execute(
        "INSERT INTO livro_dados(livro_id, validacao, validado_em, inscricao_fim, esfera, area, situacao_prazo) VALUES (?, 'aprovado', ?, ?, ?, ?, ?)",
        (i, agora, fim, esfera, area, prazo),
    )


def _ap(g, pasta):
    r = g.aplicar(list(ler(pasta)))
    assert r.ok, r.recusados
    for f in pasta.rglob("*.jsonl"):
        f.unlink()


def test_a_base_a_fila_as_duas_tentativas_e_o_chrome(bancos, gravador, tmp_path):
    b, ev, agora = bancos["biblioteca"], tmp_path / "ev", datetime.now(timezone.utc)
    _livro(b, "C", "Edital Completo 2026", "https://gov.br/a", "https://site.org/a", "2026-11-30", "estadual", "Cultura", "aberta")
    _livro(b, "A", "Edital Aberto 2026", None, "https://site.org/b", "2026-11-30", "estadual", "Cultura", "aberta")
    _livro(b, "R", "Edital Recuperável 2025", "https://gov.br/r", "https://site.org/r", None, "estadual", "Cultura", "encerrada")
    _livro(b, "S", "Edital Sem Base", None, None, None, None, None, None)
    _livro(b, "N", "Anexo 8 – Declaração Pessoa com Deficiência", "https://gov.br/n", "https://site.org/n")
    b.execute(
        "INSERT INTO certidao(livro_id, item, valor, situacao, fase, em) VALUES ('C', 'Requisitos', 'organizações de todo o Brasil', "
        "'comprovado', 'certificacao', '2026-10-27T10:00:00+00:00')"
    )  # 27/10/2026: a aberta precisa da cláusula de quem pode participar
    b.commit()
    av = {x["id"]: x for x in CB.avaliar(b)}
    assert av["C"]["classe"] == "base completa" and av["A"]["classe"] == "aberta incompleta" and av["A"]["buscar"] == ["site oficial", CB.QUEM_PODE]
    assert av["R"]["classe"] == "recuperável" and av["R"]["buscar"] == ["prazo de inscrição"] and av["S"]["classe"] == "sem base"
    assert av["N"]["classe"] == "não é oportunidade"
    assert [x["id"] for x in CB.fila(list(av.values()), agora)] == ["A", "R", "S"]  # as abertas primeiro
    CB.atualizar(b, Diario(ev, "c"), agora)
    _ap(gravador, ev)
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id = 'N'").fetchone()[0] == "analise externa"  # não é oportunidade: o Chrome
    CB.registrar_tentativa(Diario(ev, "c"), {**av["R"], "tentativas": 0}, agora)  # a 1ª tentativa
    _ap(gravador, ev)
    av = {x["id"]: x for x in CB.avaliar(b)}
    assert "R" not in [x["id"] for x in CB.fila(list(av.values()), agora + timedelta(minutes=10))]  # antes de 30 minutos, não
    assert "R" in [x["id"] for x in CB.fila(list(av.values()), agora + timedelta(minutes=31))]  # depois de 30, a 2ª
    CB.registrar_tentativa(Diario(ev, "c"), av["R"], agora + timedelta(minutes=31))
    _ap(gravador, ev)
    CB.atualizar(b, Diario(ev, "c"), agora + timedelta(minutes=40))
    _ap(gravador, ev)
    # 28/10/2026: o prazo encerrado não vai ao Chrome (ia e voltava ao arquivo a cada passagem: o vai e volta)
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id = 'R'").fetchone()[0] == "preparacao"
    CB.ao_chrome(b, Diario(ev, "c"), {**av["R"], "fase": "preparacao"}, "ensaio do lote: enviado à mão")  # o restante testa o lote
    _ap(gravador, ev)
    from eldorado.base.cartorio.analise_externa import gerar_lote, importar

    lote = gerar_lote(b, agora.date())
    r_ = next(x for x in lote["livros"] if x["livro_id"] == "R")
    assert r_["buscar"] == ["prazo de inscrição"] and "A BASE DO LIVRO" in lote["instrucoes"]
    importar(json.dumps({"vereditos": [{"livro_id": "N", "decisao": "descartar", "motivo": "é um anexo, não uma oportunidade"}]}), b, Diario(ev, "x"))
    _ap(gravador, ev)
    assert b.execute("SELECT situacao FROM livro WHERE id = 'N'").fetchone()[0] == "excluido"  # o não validado: excluído


def test_o_interceptador_voa_2_livros_em_paralelo():
    from eldorado.base.cerebro import pilotos_permanentes as PP

    assert PP.PARALELOS_INTERCEPTADOR == 5
    import tomllib

    c = tomllib.loads(Path("config/cargos.toml").read_text(encoding="utf-8"))
    assert c["cargo"]["interceptador"]["vagas"] == [2, 3, 4, 5, 6] and c["servidor"]["vagas"] == 7
    from eldorado.base.nucleo.ia import IA

    assert {IA("http://x", cargo_nome="interceptador", vaga=k).cargo["vaga"] for k in range(5)} == {2, 3, 4, 5, 6}  # cada voo na sua vaga
    assert "-np 7" in Path(".github/workflows/eldorado.yml").read_text(encoding="utf-8")


def test_o_prevoo_completa_sem_a_ia(tmp_path):
    from types import SimpleNamespace

    from eldorado.base.comandante.biblioteca import prevoo

    html = b'<html><a href="/arquivos/edital-07-2026.pdf">Edital n 07/2026</a><a href="https://facebook.com/x">rede</a></html>'

    class Inter:
        def _ler(self, url):
            return url, None, html

    ev = []
    diario = SimpleNamespace(emitir=lambda t, m, d: ev.append((t, d)))
    lv = SimpleNamespace(id="L1", titulo="Edital nº 07/2026 de Cultura", link_divulgacao="https://noticias.com.br/x", orgao="Ministério da Cultura")
    feito = prevoo(diario, Inter(), lv, {"buscar": ["site oficial", "esfera", "área de atuação"]})
    assert feito == ["site oficial", "esfera"]
    links = next(d for t, d in ev if t == "livro.links")
    assert links["link_oficial"] == "https://noticias.com.br/arquivos/edital-07-2026.pdf"
    assert next(d for t, d in ev if t == "livro.esfera")["esfera"] == "federal"
    assert next(d for t, d in ev if t == "livro.origem")["origem"] == "candidato"


def test_a_aberta_volta_a_fila_em_24h_e_a_encerrada_nao_vai_ao_chrome():
    """28/10/2026: a inscrição aberta volta à fila do Interceptador a cada 24 h (mesmo com 2 tentativas ou esperando o
    Chrome); o livro de prazo encerrado não vai ao Chrome (o vai e volta arquivo ↔ análise externa)."""
    from datetime import datetime, timedelta, timezone

    agora = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
    velho = (agora - timedelta(hours=30)).isoformat()
    novo = (agora - timedelta(hours=2)).isoformat()
    base = {"classe": "aberta incompleta", "buscar": ["site oficial"], "fim": "2026-11-30", "titulo": "x", "antes": None}
    livros = [
        {**base, "id": "esperando", "fase": "analise externa", "prazo": "aberta", "tentativas": 2, "ultima": velho},
        {**base, "id": "recente", "fase": "analise externa", "prazo": "aberta", "tentativas": 2, "ultima": novo},
        {**base, "id": "duas", "fase": "preparacao", "prazo": "aberta", "tentativas": 2, "ultima": velho},
    ]
    ids = [x["id"] for x in CB.fila(livros, agora)]
    assert "esperando" in ids and "duas" in ids and "recente" not in ids
    src = Path("eldorado/base/comandante/biblioteca.py").read_text(encoding="utf-8")
    assert 'if x["prazo"] == "encerrada":' in src
