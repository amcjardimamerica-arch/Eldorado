"""Critério de pronto da Fase 4: um achado aceito vira livro certificado, com selos, movido pela Regência."""
import json
from pathlib import Path

from conftest import AGORA, ev
from test_cartorio import EDITAL

from eldorado.base.fluxo.definicao import carregar
from eldorado.base.fluxo.executor import Executor
from eldorado.base.fluxo.nos import abrir_bancos
from eldorado.base.nucleo.gravador import Gravador


def test_achado_aceito_vira_livro_certificado_com_selos(tmp_path):
    dados, eventos = tmp_path / "dados", tmp_path / "eventos"
    b = abrir_bancos(dados)
    assert Gravador(b).aplicar([ev("documento.registrado", id=1, url="https://goias.gov.br/cultura/edital-3-2026.pdf", sha256="sha-edital",
                                   obtido_em=AGORA, oficial=1, drive_id="d1"), ev("pagina.gravada", documento_id=1, numero=1, texto=EDITAL)]).ok
    (tmp_path / "modulos.toml").write_text('[[modulo]]\nclasse = "modulos_passagem:MotorEdital"\n')
    (tmp_path / "agenda.toml").write_text('[[modulo]]\nid = "do-goias"\nhorarios = ["06:00"]\n')
    wf = Path("workflows/passagem.toml").read_text(encoding="utf-8")
    # os pilotos em nós próprios (24/10/2026): nos testes, sem sair para a rede (no portão da produção eles buscavam na internet)
    wf = wf.replace("orcamento_pilotos_s = 180", "orcamento_pilotos_s = 0").replace("orcamento_originais_s = 120", "orcamento_originais_s = 0")
    wf = wf.replace("limite = 15, orcamento_s = 90", "limite = 0, orcamento_s = 0")         # a releitura também, sem rede
    wf = (wf.replace('"config/agenda.toml"', json.dumps(str(tmp_path / "agenda.toml"))).replace('"config/modulos.toml"', json.dumps(str(tmp_path / "modulos.toml")))
            .replace('dados = "dados"', f"dados = {json.dumps(str(dados))}").replace('eventos = "eventos"', f"eventos = {json.dumps(str(eventos))}")
            .replace('dados = "dados" }', f"dados = {json.dumps(str(dados))} }}"))
    # 29/10/2026: a pasta da análise externa também temporária (a trava rodava o nó sobre a verificacao/ REAL; com o lote
    # regerado a cada passagem, a etapa vazia do banco de teste apagava os lotes de verdade)
    wf = wf.replace('pasta = "verificacao"', f"pasta = {json.dumps(str(tmp_path / 'verificacao'))}")
    wf = wf.replace('parametros = { agenda', 'parametros = { agora = "2026-10-22T06:10:00-03:00", carga_fixa = 0.1, agenda', 1)
    wf = wf.replace('tipo = "eldorado.base.cerebro.regencia:no_acionar"\nparametros = { ', 'tipo = "eldorado.base.cerebro.regencia:no_acionar"\nparametros = { carga_fixa = 0.1, ', 1)
    (tmp_path / "passagem.toml").write_text(wf)
    r = Executor(carregar(tmp_path / "passagem.toml"), eventos).executar()
    assert r.estado == "concluida", r.erro
    assert len(r.saidas["decidir"]) == 1                                               # a licitação foi barrada pelo portão
    livro = r.saidas["cartorio"][0]
    assert livro["estrela"] in ("bronze", "prata", "ouro") and livro["selo_livro"] == "sem"      # o selo só quando a oportunidade encerra
    b = abrir_bancos(dados)
    try:
        bib = b["biblioteca"]
        lid = livro["livro"]
        assert bib.execute("SELECT fase FROM passaporte WHERE livro_id=?", (lid,)).fetchone()[0] in ("preparacao", "farol")  # fase 3, ou completo
        assert {x[0] for x in bib.execute("SELECT autorizado_por FROM passagem WHERE livro_id=?", (lid,))} == {"regencia"}
        assert bib.execute("SELECT COUNT(*) FROM certidao WHERE livro_id=? AND trecho IS NOT NULL AND pagina=1", (lid,)).fetchone()[0] >= 6
        assert bib.execute("SELECT estrela, link_oficial FROM livro WHERE id=?", (lid,)).fetchone()[0] == livro["estrela"]
        historia = [x[0] for x in bib.execute("SELECT tipo FROM historia_do_livro WHERE livro_id=? ORDER BY em", (lid,))]
        assert {"achado", "passagem", "certidão", "relatório interna"} <= set(historia)
        assert [tuple(x) for x in bib.execute("SELECT decisao, COUNT(*) FROM achado GROUP BY 1")] == [("aceito", 1), ("barrado", 1)]
        med = {m: p for m, p in b["cerebro"].execute("SELECT marcador, ponto FROM medicao WHERE nivel='arquivo'")}
        for arq in ("eldorado/base/cartorio/cartorio.py", "eldorado/base/cerebro/pertinencia.py"):
            assert med[arq] == "v", arq
    finally:
        for c in b.values():
            c.close()
