"""A fase 6 (titular, 25/10/2026): o Comandante apresenta à titular o que decidir primeiro e por quê — as oportunidades
que fecham antes (o ouro primeiro), o que falta e o dia —, no máximo a cada 6 horas; sem a IA, pela regra."""

from datetime import datetime, timedelta, timezone

from eldorado.base.comandante.apresentar import apresentar


def test_a_apresentacao_a_titular(bancos, tmp_path):
    b, agora = bancos["biblioteca"], datetime.now(timezone.utc)
    for i, (dias, estrela) in enumerate(((5, "bronze"), (2, "ouro"), (2, "prata"), (30, "ouro"))):
        lid = f"L-ap-{i}"
        b.execute(
            "INSERT INTO livro(id, missao, chave, titulo, orgao, uf, link_oficial, estrela, selo_livro, informacoes_validadas, situacao, criado_em, "
            "atualizado_em) VALUES (?, 'oportunidades', ?, ?, 'Órgão', 'GO', 'https://x.gov.br', ?, 'sem', 0, 'em trabalho', ?, ?)",
            (lid, lid, f"Edital {i}", estrela, agora.isoformat(), agora.isoformat()),
        )
        b.execute("INSERT INTO passaporte(livro_id, fase, entrou_em) VALUES (?, 'preparacao', ?)", (lid, agora.isoformat()))
        b.execute(
            "INSERT INTO livro_dados(livro_id, situacao_prazo, inscricao_fim, validacao, validado_em) VALUES (?, 'aberta', ?, 'aprovado', ?)",
            (lid, (agora + timedelta(days=dias)).date().isoformat(), agora.isoformat()),
        )
    b.commit()
    pasta = tmp_path / "relatorios"
    r = apresentar(tmp_path, pasta, agora)
    assert r and r["abertas"] == 4 and len(r["fecham_em_7_dias"]) == 3
    assert [x["titulo"] for x in r["fecham_em_7_dias"]] == ["Edital 1", "Edital 2", "Edital 0"]  # o que fecha antes; o ouro primeiro
    assert "Edital 1" in r["redacao"]["prioridades"][0]["o_que"] and r["redigido_por"].startswith("a regra")  # sem a IA: a regra
    assert len(list(pasta.glob("*.md"))) == 1 and "Para a sua decisão" in next(pasta.glob("*.md")).read_text(encoding="utf-8")
    assert apresentar(tmp_path, pasta, agora + timedelta(hours=2)) is None  # no máximo a cada 6 horas
    assert apresentar(tmp_path, pasta, agora + timedelta(hours=7))
