import json
import re
import unicodedata
from pathlib import Path

import pytest
from conftest import AGORA, ev

from eldorado.base.cartorio import origem, selos
from eldorado.base.cartorio.certificacao import Certificacao, Pagina, localizar
from eldorado.base.cartorio.indice import Indice
from eldorado.base.cartorio.passaporte import Passaporte
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.contratos import Achado

EDITAL = """SECRETARIA DE ESTADO DA CULTURA DE GOIÁS
EDITAL DE CHAMAMENTO PÚBLICO Nº 3/2026
1. DO OBJETO
1.1. O presente edital tem por objeto a seleção de projetos culturais de organizações da sociedade civil para celebração de termo de fomento.
2. DAS INSCRIÇÕES
2.1. As inscrições estarão abertas de 01/10/2026 a 30/11/2026, pelo sistema eletrônico.
3. DO VALOR
3.1. Serão destinados R$ 500.000,00 para até 10 projetos, no Estado de Goiás.
4. DOS REQUISITOS
4.1. Poderão participar: organizações da sociedade civil com no mínimo 2 anos de existência e sede em Goiás.
5. DO RESULTADO
5.1. O resultado final será publicado em 15/12/2026. Caberá recurso no prazo de 5 (cinco) dias úteis.
Anexo I – Formulário de inscrição. Área: cultura."""


def achado(i="A1", titulo="Edital de Chamamento Público nº 3/2026 — Fomento a projetos culturais de organizações da sociedade civil", uf="GO", **kw):
    return Achado(id=i, motor="do-goias", encontrado_em="2026-10-20", publicado_em=kw.pop("publicado_em", "2026-10-01"),
                  link_divulgacao=kw.pop("link", "https://goias.gov.br/cultura/edital-3-2026"), titulo=titulo,
                  dados={"uf": uf, "orgao": "Secult", **kw.pop("dados", {})}, **kw)


def test_certificacao_acha_os_itens_com_trecho_e_pagina(diario):
    novas = Certificacao(diario).certificar("L1", [Pagina(7, 1, EDITAL)])
    assert {"Objeto", "Prazo de inscrição", "Valor", "Território", "Requisitos", "Resultado", "Prazo de recurso", "Modalidade"} <= set(novas)
    assert novas["Valor"]["valor"] == "R$ 500.000,00" and novas["Valor"]["pagina"] == 1 and "Serão destinados" in novas["Valor"]["trecho"]


def test_regressao_da_certificacao_nas_certidoes_reais():
    """600 certidões validadas do Eldorado0, nunca usadas para ajustar os padrões. Linha de base de 22/10: ponta a ponta 54%."""
    casos = json.loads((Path(__file__).parent / "dados/certidoes_ouro.json").read_text(encoding="utf-8"))["casos"]
    sem = lambda s: "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))  # noqa: E731
    achou = certo = 0
    for item, trecho, valor in casos:
        r = localizar(item, [Pagina(0, 1, trecho)])
        if r:
            achou += 1
            a, b = set(re.findall(r"\w{3,}|\d+", sem(r["valor"]))), set(re.findall(r"\w{3,}|\d+", sem(valor)))
            certo += bool(a and b and len(a & b) / min(len(a), len(b)) >= 0.5)
    assert achou / len(casos) >= 0.60 and certo / max(achou, 1) >= 0.80 and certo / len(casos) >= 0.50


def test_selo_do_livro_pelo_historico():
    E = selos.Edicao
    assert selos.selo_do_livro([E(2026, True, True), E(2025, True, True)], 2026) == "ouro"
    assert selos.selo_do_livro([E(2026, True, True), E(2023, False, False)], 2026) == "prata"
    assert selos.selo_do_livro([E(2026, True, True)], 2026) == "bronze"
    assert selos.selo_do_livro([], 2026) == "sem"


def test_a_origem_e_decidida_por_livro_com_evidencia():
    """Titular, 23/10/2026: nenhum site é original por regra; o mesmo portal pode replicar ou ter oportunidade própria."""
    assert origem.classificar("https://prosas.com.br/editais/123", "Instituto Votorantim")[0] == "candidato"        # o Prosas replicando
    assert origem.classificar("https://prosas.com.br/editais/123", "Prosas")[0] == "confirmado"                      # a oportunidade do próprio Prosas
    assert origem.classificar("https://buritidegoias.go.gov.br/edital.pdf", "Fundo Municipal de Saúde de Buriti de Goiás")[0] == "confirmado"
    assert origem.classificar("https://www.diariomunicipal.com.br/agm/edicao.pdf", "Prefeitura Municipal de Ipameri")[0] == "candidato"
    assert origem.classificar("https://www.gov.br/saude/pt-br/se/pronon", "Ministério da Saúde")[0] == "confirmado"
    assert origem.classificar("https://captadores.org.br/edital-x", "Secult")[0] == "candidato"                         # indício, não decide
    assert origem.classificar("https://x.org/y", "Qualquer", confirmado_antes=True)[0] == "confirmado"                 # nunca rebaixa
    assert origem.classificar(None, "x")[0] == "ausente"
    assert origem.classificar("https://mapa.cultura.gov.br/oportunidade/1", "Secretaria Municipal de Cultura de Anápolis")[0] == "candidato"  # setor não é nome
    assert origem.classificar("https://www.anapolis.go.gov.br/edital", "Secretaria Municipal de Cultura de Anápolis")[0] == "confirmado"


def test_indice_vincula_pela_chave_e_pelo_mesmo_edital_em_outro_canal(diario):
    ix = Indice(None, MissaoOportunidades(), diario)
    l1, novo1, _ = ix.resolver(achado("A1"))
    l2, novo2, como2 = ix.resolver(achado("A2", titulo="Edital nº 5/2025 — Fomento a projetos culturais de organizações da sociedade civil"))
    l3, novo3, como3 = ix.resolver(achado("A3", titulo="Edital de Chamamento Público 3/2026: fomento a projetos culturais das organizações da sociedade civil goianas"))
    l4, novo4, _ = ix.resolver(achado("A4", uf="MG"))
    assert novo1 and not novo2 and l2 == l1 and como2 == "mesma chave"
    assert not novo3 and l3 == l1 and "outro canal" in como3
    assert novo4 and l4 != l1                                        # outra UF: outro livro, nunca unido por engano


def test_passaporte_so_com_a_regencia_e_no_maximo_3_tentativas(diario):
    p = Passaporte(None, diario)
    assert p.mover("L1", "recepcao")[0] and p.mover("L1", "certificacao")[0]
    assert not p.mover("L1", "recepcao")[0]                          # volta não autorizada
    assert [p.tentar("L1", "leitura", "faltam itens") for _ in range(4)] == [True, True, True, False]


@pytest.fixture
def documento(gravador):
    gravador.aplicar([ev("documento.registrado", id=1, url="https://goias.gov.br/cultura/edital-3-2026.pdf", sha256="sha-edital", obtido_em=AGORA, oficial=1, drive_id="d1"),
                      ev("pagina.gravada", documento_id=1, numero=1, texto=EDITAL)])
