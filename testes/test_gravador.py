import zstandard
from conftest import AGORA, ev, livro

from eldorado.base.nucleo.eventos import ler


def caminho_completo():
    return [
        ev("achado.entregue", id="A1", motor="do-goias", encontrado_em="2026-10-20", link_divulgacao="https://portal/x", titulo="Edital X", dados={"uf": "GO"}),
        ev("pertinencia.decidida", etapa="coleta", referencia="A1", decisao="aceito", motivo="terceiro setor, Goiás", em=AGORA),
        livro(),
        ev("livro.vinculado", achado_id="A1", livro_id="L1"),
        ev("livro.passagem", livro_id="L1", de="coleta", para="certificacao", em="2026-10-21", autorizado_por="regencia"),
        ev("certidao.gravada", livro_id="L1", item="prazo", valor="30/10/2026", trecho="inscrições até 30/10/2026", pagina=2, fase="certificacao", situacao="comprovado", em="2026-10-21"),
        ev("certidao.gravada", livro_id="L1", item="valor", fase="certificacao", situacao="dispensado", justificativa="edital sem valor fixo", em="2026-10-21"),
        ev("selo.calculado", id="L1", estrela="bronze", selo_livro="sem", informacoes_validadas=2, atualizado_em=AGORA),
        ev("relatorio.etapa", livro_id="L1", fase="certificacao", gerou="2 itens", aprendeu="o prazo fica na página 2", em="2026-10-22"),
        ev("veredito.gravado", livro_id="L1", origem="chrome", decisao="valida", em="2026-10-22"),
    ]


def test_caminho_completo_de_um_livro(gravador, bancos):
    r = gravador.aplicar(caminho_completo())
    assert r.ok, r.recusados
    b = bancos["biblioteca"]
    assert b.execute("SELECT decisao, livro_id FROM achado WHERE id='A1'").fetchone()[:] == ("aceito", "L1")
    assert b.execute("SELECT fase FROM passaporte WHERE livro_id='L1'").fetchone()[0] == "certificacao"
    assert b.execute("SELECT estrela FROM livro WHERE id='L1'").fetchone()[0] == "bronze"
    historia = [r[0] for r in b.execute("SELECT tipo FROM historia_do_livro WHERE livro_id='L1' ORDER BY em")]
    assert historia[0] == "achado" and "passagem" in historia and "veredito" in historia
    assert bancos["cerebro"].execute("SELECT COUNT(*) FROM rotulo").fetchone()[0] == 1          # o veredito vira rótulo da rede


def test_reaplicar_nao_duplica_nada(gravador, bancos):
    evs = caminho_completo()
    r1 = gravador.aplicar(evs)
    r2 = gravador.aplicar(evs)
    assert r1.ok and r2.aplicados == 0 and r2.repetidos == r1.aplicados
    assert bancos["biblioteca"].execute("SELECT COUNT(*) FROM certidao").fetchone()[0] == 2


def test_operacoes_proibidas_viram_recusa_com_alarme(gravador, bancos):
    gravador.aplicar([livro()])
    proibidos = [
        ev("livro.passagem", livro_id="L1", para="farol", em=AGORA, autorizado_por="cartorio"),                         # sem a Regência
        ev("livro.excluido_logicamente", id="L1", atualizado_em=AGORA),                                                  # sem justificativa
        ev("certidao.gravada", livro_id="L1", item="x", fase="c", situacao="dispensado", em=AGORA),                       # dispensa sem justificativa
        ev("tentativa.registrada", livro_id="L1", fase="f", ferramenta="t", numero=4, em=AGORA),                          # 4ª tentativa
        livro(id="L2", chave="k1"),                                                                                       # livro duplicado
        ev("aprendizado.registrado", o_que="x", criado_em="2026-10-01", expira_em="2026-12-01"),                         # temporário > 30 dias
        ev("livro.criado", id="L3", missao="o", chave="k3", situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA, campo_inventado=1),
    ]
    r = gravador.aplicar(proibidos)
    assert len(r.recusados) == len(proibidos)
    assert "colunas desconhecidas" in r.recusados[-1][2]
    alarmes = bancos["cerebro"].execute("SELECT COUNT(*) FROM alarme WHERE modulo='gravador'").fetchone()[0]
    assert alarmes == len(proibidos)
    assert bancos["biblioteca"].execute("SELECT situacao FROM livro WHERE id='L1'").fetchone()[0] == "em trabalho"


def test_exclusao_logica_com_justificativa_e_aceita(gravador, bancos):
    r = gravador.aplicar([livro(), ev("livro.excluido_logicamente", id="L1", justificativa_exclusao="edital cancelado pelo órgão", atualizado_em=AGORA)])
    assert r.ok
    assert bancos["biblioteca"].execute("SELECT situacao FROM livro WHERE id='L1'").fetchone()[0] == "excluido"


def test_pagina_comprimida_e_achada_pela_busca(gravador, bancos):
    texto = "EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026. As inscrições vão até 30 de outubro de 2026. " * 20
    r = gravador.aplicar([ev("documento.registrado", id=1, url="https://orgao.gov.br/e.pdf", sha256="abc", obtido_em=AGORA, drive_id="d1"),
                          ev("pagina.gravada", documento_id=1, numero=1, texto=texto)])
    assert r.ok, r.recusados
    b = bancos["biblioteca"]
    blob = b.execute("SELECT texto_zstd FROM pagina").fetchone()[0]
    assert len(blob) < len(texto.encode()) and zstandard.ZstdDecompressor().decompress(blob).decode() == texto
    achou = b.execute("SELECT m.numero FROM busca JOIN busca_mapa m ON m.rowid = busca.rowid WHERE busca MATCH 'chamamento'").fetchall()
    assert [a[0] for a in achou] == [1]


def test_lote_da_migracao_e_reaplicavel(gravador, bancos):
    lote = ev("importacao.lote", eventos=[
        {"tipo": "empresa.registrada", "dados": {"cnpj": "1", "razao_social": "Empresa A", "descoberta_por": "importacao", "descoberta_em": AGORA, "atualizada_em": AGORA}},
        {"tipo": "incentivo.registrado", "dados": {"cnpj": "1", "lei": "FIA", "ano": 2025, "valor": 1000.0, "fonte": "planilha", "em": AGORA}},
    ])
    assert gravador.aplicar([lote]).ok
    assert gravador.aplicar([lote]).aplicados == 0
    assert bancos["especial"].execute("SELECT COUNT(*) FROM incentivo").fetchone()[0] == 1


def test_alarme_da_recusa_fica_no_diario(gravador, diario):
    gravador.aplicar([ev("livro.passagem", livro_id="nao-existe", para="farol", em=AGORA, autorizado_por="regencia")])
    tipos = [e.tipo for e in ler(diario.arquivo.parent.parent.parent.parent)]
    assert "alarme.aberto" in tipos


def test_a_mesma_criacao_de_livro_duas_vezes_e_repeticao(gravador, bancos):
    """O Cartório e a rede, na mesma passagem, criam o mesmo livro (o id vem da chave): a segunda é repetição, não recusa."""
    from conftest import AGORA, ev
    criar = dict(id="L-abc", missao="oportunidades", chave="abc", titulo="Edital", estrela="sem", selo_livro="sem", informacoes_validadas=0,
                 situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA)
    r = gravador.aplicar([ev("livro.criado", **criar), ev("livro.criado", **criar)])
    assert r.ok and r.aplicados == 1 and r.repetidos == 1
    outro = gravador.aplicar([ev("livro.criado", **{**criar, "id": "L-outro", "chave": "outra"}), ev("livro.criado", **{**criar, "id": "L-abc", "chave": "zzz"})])
    assert not outro.ok and len(outro.recusados) == 1                                       # um id repetido com outra chave segue sendo recusado
