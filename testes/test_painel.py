"""As visões do painel: cada tela recebe os dados certos dos bancos (só leitura)."""
import json
from datetime import date

from conftest import AGORA, ev

from eldorado.base.painel.visoes import gerar, publicar


def livro(i, titulo, abr="estadual_go", prazo="aberta", fim="2026-11-30", validacao="aprovado"):
    return [ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo=titulo, orgao="Secult", uf="GO", estrela="prata", selo_livro="sem",
               informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
            ev("livro.decupado", livro_id=i, abrangencia=abr, situacao_prazo=prazo, inscricao_fim=fim, validacao=validacao, validado_em=AGORA)]


def test_visoes_do_painel(gravador, bancos, tmp_path):
    from eldorado.base.cerebro.regencia import achado_para_evento
    from eldorado.base.nucleo.contratos import Achado
    prog = Achado(id="goyazes-programa-abc", motor="goyazes", encontrado_em="2026-10-22", link_divulgacao="https://x", titulo="Programa Goyazes", dados={},
                  link_oficial="https://goias.gov.br/cultura/programa-goyazes/legislacao/")
    eventos = livro("A", "Edital de fomento cultural") + livro("B", "Edital antigo", prazo="encerrada", fim="2025-01-10") + livro("C", "Duplicado de A") + \
        livro("P", "Programa Goyazes", prazo="sem prazo", fim=None) + livro("N", "Goyazes reabre inscrições", prazo="sem prazo", fim=None)
    eventos += [ev("livro.unido", livro_que_fica="A", livro_unido="C", em=AGORA, motivo="mesma chave"),
                ev("lei.registrada", id="lei-go-13613-2000", esfera="estadual_go", ementa="Lei Goyazes", atualizada_em=AGORA),
                ev("livro.legislacao", livro_id="P", lei_id="lei-go-13613-2000", papel="rege o programa", em=AGORA),
                ev("livro.legislacao", livro_id="N", lei_id="lei-go-13613-2000", papel="rege o programa", em=AGORA),
                ev("achado.entregue", **{**achado_para_evento(prog), "livro_id": "P"}, decisao="aceito", motivo="oportunidade"),
                ev("certidao.gravada", livro_id="P", item="Valor", valor="montante global R$ 40.000.000,00", trecho="...", pagina=3, fase="certificacao",
                   situacao="comprovado", em=AGORA)]
    assert gravador.aplicar(eventos).ok
    (tmp_path / "config").mkdir()
    (tmp_path / "config/agenda.toml").write_text('[[modulo]]\nid = "goyazes"\nhorarios = ["09:23"]\n')
    d = gerar(tmp_path, tmp_path / "config", hoje=date(2026, 10, 22))                          # os bancos da fixture ficam em tmp_path
    assert [x["id"] for x in d["abertas"]] == ["A"]                                               # C está unido a A; B encerrou
    assert d["resumo"]["livros"] == 4 and d["resumo"]["territorio"] == {"Governo de Goiás": 4}
    assert [p["id"] for p in d["programas"]] == ["P"] and [x["id"] for x in d["programas"][0]["relacionados"]] == ["N"]
    assert d["programas"][0]["certidoes"][0]["valor"].endswith("R$ 40.000.000,00") and d["motores"][0]["id"] == "goyazes"
    r = publicar(tmp_path, tmp_path / "docs", tmp_path / "config")
    assert r["abertas"] == 1 and json.loads((tmp_path / "docs/dados/painel.json").read_text(encoding="utf-8"))["resumo"]["abertas"] == 1
    assert "Painel de captação" in (tmp_path / "docs/index.html").read_text(encoding="utf-8")
