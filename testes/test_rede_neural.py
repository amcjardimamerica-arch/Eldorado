"""A rede neural do Cérebro: aprende as três perguntas com o histórico dos bancos e escolhe a ação na etapa 3."""
import json

from conftest import AGORA, ev

from eldorado.base.cerebro.encaminhamento import Encaminhamento
from eldorado.base.cerebro.rede import RedeNeural
from eldorado.base.nucleo.registro import Registro
from eldorado.motores.pilotos.interceptador import Livro


def livro(i, titulo, link="https://goias.gov.br/cultura/e.pdf"):
    return ev("livro.criado", id=i, missao="oportunidades", chave=f"k{i}", titulo=titulo, orgao="Secult", uf="GO", link_oficial=link, estrela="sem",
              selo_livro="sem", informacoes_validadas=0, situacao="em trabalho", criado_em=AGORA, atualizado_em=AGORA)


def test_rede_aprende_as_tres_perguntas(gravador, bancos):
    evs = []
    for i in range(30):                                              # a abordagem 5 traz; a 1 não traz (no mesmo tipo de livro)
        evs.append(livro(f"L{i}", f"Edital de fomento cultural {i}"))
        for n, dia in ((5, 15), (1, 16)):                            # a 5 vem antes da certidão (trouxe); a 1, depois (não trouxe)
            evs.append(ev("tentativa.registrada", livro_id=f"L{i}", fase="preparacao", ferramenta=f"abordagem {n}", numero=1, em=f"2026-10-{dia}T10:00:00+00:00",
                          resultado=json.dumps({"faltam": ["Valor"]})))
        evs.append(ev("certidao.gravada", livro_id=f"L{i}", item="Valor", valor="R$ 10.000,00", trecho="R$ 10.000,00", pagina=1, fase="certificacao",
                      situacao="comprovado", em="2026-10-15T12:00:00+00:00"))
        evs.append(ev("veredito.gravado", livro_id=f"L{i}", origem="chrome", decisao="valido", em=AGORA))
    for i in range(30):
        evs.append(ev("achado.entregue", id=f"b{i}", motor="m", encontrado_em="2026-10-01", link_divulgacao="https://x", titulo=f"Pregão para aquisição de gêneros alimentícios {i}",
                      dados={}, decisao="barrado", motivo="compra do órgão"))
    assert gravador.aplicar(evs).ok
    for i in range(20):
        bancos["cerebro"].execute("INSERT INTO execucao_motor (motor, inicio, fim, achados) VALUES (?, ?, ?, ?)",
                                  ("dou", f"2026-10-{1 + i:02d}T10:00:00+00:00", f"2026-10-{1 + i:02d}T10:05:00+00:00", 5))
        bancos["cerebro"].execute("INSERT INTO execucao_motor (motor, inicio, fim, achados) VALUES (?, ?, ?, ?)",
                                  ("vazio", f"2026-10-{1 + i:02d}T10:00:00+00:00", f"2026-10-{1 + i:02d}T10:05:00+00:00", 0))
    rede = RedeNeural.treinar(bancos["biblioteca"], bancos["cerebro"])
    m = rede.metricas()
    assert m["oportunidade"]["amostras"] == 60 and m["motor"]["amostras"] == 40 and m["acao"]["amostras"] == 60
    assert rede.nota_oportunidade({"titulo": "Edital de fomento cultural novo"}) > rede.nota_oportunidade({"titulo": "Pregão para aquisição de gêneros alimentícios"})
    assert rede.nota_motor("dou", 7, 2) > rede.nota_motor("vazio", 7, 2)
    vivo = {"link_oficial": "https://goias.gov.br/cultura/e.pdf", "estrela": "sem", "faltam": ["Valor"]}
    assert rede.nota_acao("abordagem 5", vivo) > rede.nota_acao("abordagem 1", vivo)                    # aprendeu qual abordagem traz


class _Interceptador:
    def __init__(self):
        self.ordem = None

    def investigar(self, lv, ordem=None, ate=None):
        self.ordem = ordem
        return {"livro": lv.id, "abordagem": ordem[0], "achado": None, "esgotado": False}


class _Rede:
    def nota_acao(self, acao, livro):
        return 0.9 if acao == "abordagem 9" else 0.1

    def nota_oportunidade(self, livro):
        return 0.5


def test_a_rede_escolhe_a_acao_na_etapa_3(bancos, diario):
    lv = Livro("L", "Edital", "Secult", "https://x.gov.br/e.pdf", None, "bronze", "2099-01-01", {}, set())
    inter = _Interceptador()
    quem, _ = Encaminhamento(bancos["biblioteca"], diario, Registro(), inter, _Rede()).encaminhar(lv)
    assert quem == "interceptador · abordagem 9" and inter.ordem[0] == 9                                  # fora da ordem do balcão (1, 2, 3, 9…)
