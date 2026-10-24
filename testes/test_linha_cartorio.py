"""A linha de produção do Cartório (titular, 22/10/2026): a estrela é da oportunidade aberta; encerrada, vira o selo do
livro; as etapas na ordem; o relatório de cada etapa; a etapa 5 (o veredito do Chrome)."""
import json
from datetime import date

import msgspec
from conftest import AGORA, ev

from eldorado.base.cartorio.analise_externa import gerar_lote, importar
from eldorado.base.cartorio.auditoria import arquivar_encerrados
from eldorado.base.cartorio.cartorio import Cartorio
from eldorado.base.missao import itens as I
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.contratos import Achado
from eldorado.base.nucleo.eventos import ler

VALORES = {"Objeto": "seleção de projetos culturais", "Órgão / financiador": "Secretaria de Cultura", "Esfera": "estadual",
           "Território": "Estado de Goiás", "Área de atuação": "cultura", "Modalidade": "fomento", "Valor": "R$ 500.000,00",
           "Requisitos": "organizações da sociedade civil sediadas em Goiás", "Resultado": "publicado em 15/12/2099",
           "Prazo de recurso": "5 dias úteis", "Anexos": "Anexo I — plano de trabalho"}


def livro(i, fase, fim="30/11/2099", itens=None):
    evs = [ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo=f"Edital de fomento cultural {i}", orgao="Secult", uf="GO",
              link_oficial=f"https://goias.gov.br/cultura/edital-{i}.pdf", estrela="sem", selo_livro="sem", informacoes_validadas=0,
              situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA),
           ev("livro.passagem", livro_id=i, de=None, para="recepcao", em=AGORA, autorizado_por="regencia")]
    caminho = {"recepcao": [], "certificacao": ["certificacao"], "preparacao": ["certificacao", "preparacao"],
               "analise externa": ["certificacao", "preparacao", "analise externa"], "arquivo": ["certificacao", "arquivo"]}[fase]
    de = "recepcao"
    for f in caminho:
        evs.append(ev("livro.passagem", livro_id=i, de=de, para=f, em=AGORA, autorizado_por="regencia"))
        de = f
    for item in itens if itens is not None else VALORES:
        evs.append(ev("certidao.gravada", livro_id=i, item=item, valor=VALORES[item], trecho=VALORES[item], pagina=1, fase="certificacao",
                      situacao="comprovado", em=AGORA))
    evs.append(ev("certidao.gravada", livro_id=i, item="Prazo de inscrição", valor=f"de 01/10/2026 a {fim}", trecho=f"inscrições até {fim}", pagina=1,
                  fase="certificacao", situacao="comprovado", em=AGORA))
    # a origem confirmada (o link original): sem ela, pela régua da titular, o livro não passa de bronze
    evs.append(ev("livro.decupado", livro_id=i, validacao="aprovado", validado_em=AGORA, origem="confirmado", origem_motivo="teste"))
    return evs


def aplicar(gravador, tmp_path):
    assert gravador.aplicar(list(ler(tmp_path / "eventos"))).ok


def processar(gravador, bancos, diario, livro_id, n=1):
    """O caminho real: o achado é registrado (pela Regência ou pela rede) antes de chegar ao Cartório."""
    from eldorado.base.cerebro.regencia import achado_para_evento
    a = Achado(id=f"a{livro_id}{n}", motor="m", encontrado_em="2026-10-22", link_divulgacao="https://x",
               titulo=f"Edital de fomento cultural {livro_id}", dados={"livro_id": livro_id})
    assert gravador.aplicar([ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="informação pedida")]).ok
    return Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])


def etapa(b, i):
    return b.execute("SELECT fase FROM passaporte WHERE livro_id=?", (i,)).fetchone()[0]


def test_estrela_de_ouro_com_prazo_aberto_vai_ao_farol(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro("A", "preparacao")).ok
    processar(gravador, bancos, diario, "A")
    aplicar(gravador, tmp_path)
    b = bancos["biblioteca"]
    assert etapa(b, "A") == "farol" and b.execute("SELECT estrela FROM livro WHERE id='A'").fetchone()[0] == "ouro"


def test_encerrada_a_estrela_vira_o_selo_do_livro_e_vai_ao_arquivo(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro("E", "preparacao", fim="30/09/2026")).ok
    processar(gravador, bancos, diario, "E")
    aplicar(gravador, tmp_path)
    b = bancos["biblioteca"]
    assert etapa(b, "E") == "arquivo"
    assert tuple(b.execute("SELECT estrela, selo_livro FROM livro WHERE id='E'").fetchone()) == ("sem", "ouro")   # livro de ouro


def test_cada_etapa_concluida_deixa_o_seu_relatorio(gravador, bancos, diario, tmp_path):
    a = Achado(id="n1", motor="m", encontrado_em="2026-10-22", link_divulgacao="https://x.go.gov.br/e", titulo="Chamada pública para organizações da sociedade civil",
               dados={"uf": "GO"})
    from eldorado.base.cerebro.regencia import achado_para_evento
    assert gravador.aplicar([ev("achado.entregue", **achado_para_evento(a), decisao="aceito", motivo="oportunidade")]).ok
    lid = Cartorio(bancos["biblioteca"], MissaoOportunidades(), diario).processar([msgspec.to_builtins(a)])[0]["livro"]
    aplicar(gravador, tmp_path)
    b = bancos["biblioteca"]
    assert [r[0] for r in b.execute("SELECT fase FROM relatorio_etapa WHERE livro_id=? ORDER BY id", (lid,))] == ["recepcao", "certificacao"]
    assert etapa(b, lid) == "preparacao"                                                     # o livro indica a etapa em que está


def test_arquivado_volta_pela_recepcao_com_nova_oportunidade(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro("R", "arquivo", fim="30/09/2026")).ok
    processar(gravador, bancos, diario, "R", 2)
    aplicar(gravador, tmp_path)
    fases = [r[0] for r in bancos["biblioteca"].execute("SELECT para FROM passagem WHERE livro_id='R' ORDER BY id")]
    assert fases[-3:-1] == ["recepcao", "certificacao"]                                        # nunca pula etapa


def test_arquivamento_pelo_tempo(gravador, bancos, diario, tmp_path):
    assert gravador.aplicar(livro("T", "preparacao", fim="30/09/2026") + [ev("selo.calculado", id="T", estrela="prata", atualizado_em=AGORA)]).ok
    assert arquivar_encerrados(bancos["biblioteca"], diario, date(2026, 10, 22)) == 1
    aplicar(gravador, tmp_path)
    b = bancos["biblioteca"]
    assert etapa(b, "T") == "arquivo" and tuple(b.execute("SELECT estrela, selo_livro FROM livro WHERE id='T'").fetchone()) == ("sem", "prata")


def test_etapa_5_veredito_do_chrome(gravador, bancos, diario, tmp_path):
    faltando = [k for k in VALORES if k not in ("Anexos", "Prazo de recurso")]
    assert gravador.aplicar(livro("V", "analise externa", itens=faltando) + livro("D", "analise externa") + livro("X", "preparacao")).ok
    b = bancos["biblioteca"]
    lote = gerar_lote(b, date(2026, 10, 22))
    assert {x["livro_id"] for x in lote["livros"]} == {"V", "D"} and next(x for x in lote["livros"] if x["livro_id"] == "V")["faltam"] == ["Prazo de recurso", "Anexos"]
    retorno = json.dumps({"lote": lote["lote"], "vereditos": [
        {"livro_id": "V", "decisao": "valido", "itens": [{"item": "Anexos", "valor": "Anexo I", "trecho": "Anexo I — plano de trabalho", "pagina": 9},
                                                         {"item": "Valor", "valor": "R$ 1", "trecho": ""}],
         "dispensas": [{"item": "Prazo de recurso", "justificativa": "não há recurso previsto neste edital (seleção por ordem de inscrição)"},
                       {"item": "Objeto", "justificativa": "não se aplica a este edital, segundo o Chrome"}],
         "aprendizado": "os anexos ficam numa página separada do órgão"},
        {"livro_id": "D", "decisao": "descartar", "motivo": "é uma compra do órgão"},
        {"livro_id": "X", "decisao": "valido"}]})
    r = importar(retorno, b, diario)
    aplicar(gravador, tmp_path)
    assert etapa(b, "V") == "farol" and any("sem trecho" in x for x in r[0]["recusas"])
    assert any(x.startswith("dispensa de Objeto: recusada") for x in r[0]["recusas"])            # o núcleo nunca se dispensa
    assert b.execute("SELECT justificativa FROM certidao WHERE livro_id='V' AND situacao='dispensado'").fetchone()[0].startswith("não há recurso previsto")
    assert b.execute("SELECT situacao FROM livro WHERE id='D'").fetchone()[0] == "excluido"
    assert "recusado" in r[2] and etapa(b, "X") == "preparacao"                                # fora da etapa 5
    assert bancos["cerebro"].execute("SELECT COUNT(*) FROM aprendizado_temporario WHERE modulo='analise externa'").fetchone()[0] == 1
    assert I.DOZE
