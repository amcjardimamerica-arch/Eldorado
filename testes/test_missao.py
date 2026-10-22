"""Os casos de ouro da missão: validados pela titular no Eldorado0 (17/10 e 14/10/2026). Devem dar 100%."""
import pytest

from eldorado.base.missao import chave, itens, portao
from eldorado.base.missao import regras_portao as R
from eldorado.base.missao.oportunidades import MissaoOportunidades
from eldorado.base.nucleo.contratos import Achado, verificar_contrato

BARRAR = [
    "Chamamento público para prospecção do mercado imobiliário em Caieiras/SP, visando locação",
    "Chamamento Público visando nova prospecção de imóvel para locação na cidade de Palmas",
    "CHAMAMENTO PÚBLICO, tem como objeto cadastrar empresas sediadas no Estado de Rondônia",
    "Credenciamento de empresas especializadas na prestação de serviços de administração de benefícios",
    "CREDENCIAMENTO PÚBLICO, com o objetivo de realizar a Aquisição de Gêneros Alimentícios",
    "O CREDENCIAMENTO DE PRESTAÇÃO DE SERVIÇOS DE MÃO DE OBRA DE TORNEIRO E SOLDADOR",
    "SELEÇÃO PÚBLICA, MEDIANTE CHAMAMENTO PÚBLICO, DE EMPRESAS PARA CONCESSÃO DE INCENTIVOS FISCAIS",
    "Prestação de Contas de Auxílio Financeiro",
    "Chamamento para contrato de gestão de unidade de saúde por Organização Social",
    "Ministério do Esporte — EXTRATO DE TERMO DE FOMENTO — Implementação e Desenvolvimento do Projeto",
    "MMA (meio ambiente) — EXTRATO DE TERMO ADITIVO",
    "Ministério do Esporte — EXTRATO DE PRORROGAÇÃO DE OFÍCIO",
    "Prefeitura de Campo Alegre de Goiás — EXTRATO DE DISTRATO",
    "SEDS-GO / Goiás Social — Extrato_aditivo_201910319003401",
    "Edital de convocacao de assembleia geral",
    "Bazar beneficente Missão Vida em Anápolis nos dias 3 e 4 de julho",
    "MDS (desenvolvimento e assistência social) — EXTRATO DE FOMENTO Nº 7AAEKP/2026 — Fortalecer e qualificar",
    "MDS (desenvolvimento e assistência social) — EXTRATO DE COLABORAÇÃO — O objeto do presente Termo",
    "Ministério do Esporte — EXTRATOS DE TERMOS DE COMPROMISSO — Estabelecer as obrigações",
    "Coordenadoria Estadual em Sergipe — aviso de dispensa de chamamento público",
    "MCTI (ciência e tecnologia) — resultado de julgamento",
    "Prefeitura de Goiânia — Parceria celebrada no âmbito da Secretaria Municipal de Governo",
]
PASSAR = [
    "BNDES abre edital de R$ 35 milhões para fortalecer organizações sociais do Nordeste",
    "Movimento Bem Maior abre edital com apoio de até R$ 100 mil para organizações sociais",
    "Emenda Parlamentar — Câmara e Senado — captação 2026",
    "SERVICO DE LIMPEZA URBANA — Credenciamento de Cooperativas/Associações de Catadores",
    "Política Nacional Aldir Blanc - PNAB Goiás - fomento a pontos de cultura",
    "Chamada pública para selecionar Organização da Sociedade Civil para a execução de projeto",
    "Fundação FEAC abre edital para projetos sociais",
    "Credenciamento de instituição especializada, preferencialmente Organização da Sociedade Civil",
    "Mosaic abre inscrições para o Edital da Água 2026 com foco em eficiência no uso da água",
    "Edital Fundo Canadá Para Iniciativas Locais (Fcil) - Brasil (2026-2027)",
    "Fundação financia projetos em saúde e educação com valor de até R$100 mil",
    "Aberta Chamada de Projetos 2026 no Instituto Mahle",
    "Zurich abre edital nacional para apoiar projetos sociais via leis de incentivo",
    "Prefeitura de Goiânia — Edital nº 1/2026",
    "5ª edição do Edital de Apoio à Filantropia Comunitária",
]


@pytest.mark.parametrize("titulo", BARRAR)
def test_caso_de_ouro_barrar(titulo):
    assert portao.motivo({"titulo": titulo, "uf": "GO"}) is not None


@pytest.mark.parametrize("titulo", PASSAR)
def test_caso_de_ouro_passar(titulo):
    assert portao.motivo({"titulo": titulo, "uf": "GO"}) is None


def test_casos_de_ouro_do_territorio():
    D = R.municipal_fora_de_goias
    assert D({"titulo": "Chamamento — Prefeitura Municipal de Curitiba", "orgao": "Prefeitura de Curitiba", "uf": "PR"}) is None
    assert D({"titulo": "Edital", "orgao": "Prefeitura de São Paulo", "uf": "SP"}) is None
    assert D({"titulo": "Edital — Prefeitura de Campinas", "orgao": "Prefeitura de Campinas", "uf": "SP"})
    assert D({"titulo": "MUNICIPIO DE ITAGIBA — Chamamento", "uf": "BA"})
    assert D({"titulo": "Credenciamento", "orgao": "MUNICIPIO DE SENADOR CANEDO"}) is None
    assert D({"titulo": "Edital estadual", "orgao": "Secretaria de Estado", "nivel": "estadual", "uf": "MG"}) is None
    assert R.capital_citada("campanha de natal de luz") is None
    assert R.capital_citada("Prefeitura de Belo Horizonte/MG") == "MG"


def test_servico_ao_cidadao_nao_e_oportunidade():
    for t in ("Obter o Certificado de Registro e Licenciamento de Veículo (CRLV-e) — Goiás", "Solicitar Certificado do Encceja — Goiás",
              "Requerer Bolsa de Formação - FAPEG — Goiás", "Acessar Edital — Brasil"):
        assert portao.motivo({"titulo": t}).startswith("serviço público ao cidadão"), t


def test_prazo_encerrado_e_sem_titulo():
    assert portao.motivo({"titulo": "Edital de fomento cultural", "fim": "2026-01-10"}, hoje="2026-10-22").startswith("prazo encerrado")
    assert portao.motivo({"titulo": "abc"}) == "sem título"


def test_a_missao_cumpre_o_contrato_e_confere_os_dados():
    m = MissaoOportunidades(hoje="2026-10-22")
    assert verificar_contrato(m).id == "oportunidades" and m.saude().ok
    a = Achado(id="a", motor="m", encontrado_em="2026-10-22", link_divulgacao="https://x", titulo="Chamada pública para selecionar Organização da Sociedade Civil", dados={"uf": "GO"})
    assert m.portao(a) == (True, "oportunidade")


def test_a_chave_junta_as_edicoes_do_mesmo_programa():
    a = chave.chave("Edital nº 3/2026 — Fomento Cultural de Goiás", "Secult", "GO")
    b = chave.chave("Edital n. 005/2025 Fomento Cultural de Goiás", "SECULT", "GO")
    c = chave.chave("Edital nº 3/2026 — Fomento Cultural de Goiás", "Secult", "MG")
    assert a == b != c


def test_criterio_da_estrela():
    prova = lambda i: {"item": i, "situacao": "comprovado", "valor": f"valor de {i}"}  # noqa: E731
    bronze = {i: prova(i) for i in itens.BRONZE}
    assert itens.nivel(bronze) == "bronze" and itens.nivel({}) == "sem"
    assert itens.nivel({i: prova(i) for i in itens.PRATA}) == "prata"
    ouro = {i: prova(i) for i in itens.DOZE}
    assert itens.nivel(ouro) == "ouro"
    ouro["Resultado"] = {"item": "Resultado", "situacao": "comprovado", "valor": "não informado"}
    assert itens.nivel(ouro) == "prata"                                                   # "não informado" é falta
    assert itens.dispensa_valida("Prazo de recurso", "não se aplica: prêmio sem etapa de recurso")
    assert not itens.dispensa_valida("Objeto", "não se aplica: qualquer justificativa longa")   # núcleo nunca é dispensado
