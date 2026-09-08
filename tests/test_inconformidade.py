"""Testes do veto de inconformidade de objeto.

Os casos são reais: vieram da verificação manual dos 210 registros de
`docs/dados/nao_verificados.json` feita em 08/09/2026, e o id de cada um está
no comentário para que se possa reabrir o documento de origem.

A propriedade que mais importa é a segunda lista: o filtro NUNCA pode barrar um
edital de fomento legítimo. Um falso negativo custa ruído na base; um falso
positivo custa uma oportunidade perdida, que é irreversível.
"""
import unittest

from src.inconformidade import avaliar, avaliar_item

REPROVADOS = [
    # (id de origem, família esperada, texto)
    ("4cb4007f", "resultado_de_edital",
     "Contratação do proponente GABRIEL FABIANO DOS SANTOS, para apresentação do projeto "
     "Música para violoncelo e piano, selecionado e classificado no Edital do Chamamento Público 01/2025"),
    ("4a7d9b04", "resultado_de_edital",
     "Contratação artística, segundo edital de chamamento público nº 001/25 - Grupos 2 - Música"),
    ("f379aced", "empresa_ou_mercado",
     "CHAMAMENTO PÚBLICO para seleção de empresa do ramo da Construção Civil visando a elaboração de projetos"),
    ("b4f7e3b8", "empresa_ou_mercado",
     "Chamada Pública tem por objeto a prospecção de mercado imobiliário e a seleção de imóvel urbano para futura locação"),
    ("4c336356", "empresa_ou_mercado",
     "seleção de Entidade Fechada de Previdência Complementar (EFPC) para administração de plano de benefícios"),
    ("7d0bb9ae", "empresa_ou_mercado",
     "Chamamento público para seleção de interessados na utilização de espaço público para construção de estrutura física"),
    ("39ec7ccb", "busca_patrocinador",
     'CHAMAMENTO PÚBLICO PARA A OFERTA DE COTAS DE PATROCÍNIO PARA A REALIZAÇÃO DO "XX CAMPEONATO MUNICIPAL DE VOLEIBOL"'),
    ("93b289ee", "busca_patrocinador",
     "Chamamento Público para a captação de cotas de patrocínio para custeio das despesas da 4ª edição da feira Ecopark"),
    ("22ca6714", "qualificacao_previa",
     "CHAMAMENTO PÚBLICO PARA QUALIFICAÇÃO DE PESSOAS JURÍDICAS DE DIREITO PRIVADO, SEM FINS LUCRATIVOS, "
     "COMO ORGANIZAÇÃO SOCIAL DE SAÚDE - OSS"),
    ("04c2f694", "qualificacao_previa",
     "CHAMAMENTO PÚBLICO PARA SELEÇÃO PÚBLICA DE ENTIDADES PRIVADAS SEM FINS LUCRATIVOS, "
     "QUALIFICADAS COMO ORGANIZAÇÕES SOCIAIS NO MUNICÍPIO DE JAPERI"),
    ("a05a1fc4", "contrato_de_gestao",
     "CHAMAMENTO PÚBLICO para celebração de CONTRATO DE GESTÃO, tendo por objeto o gerenciamento, "
     "a operacionalização e a execução das ações e serviços de saúde"),
    ("2b0e9fec", "parceria_ja_celebrada",
     "Dispensa de Chamamento Público, com vistas à celebração de parceria, entre o Município de Bom Retiro e a entidade"),
    ("2d4d4892", "parceria_ja_celebrada",
     "Termo de Fomento entre a Secretaria de Educação de Balneário Piçarras e a APAE"),
    ("fa8d9e9b", "parceria_ja_celebrada",
     "CONVOCAÇÃO DAS ENTIDADES E COLETIVOS CULTURAIS LISTADOS NO ART. 2º, RECONHECIDOS COMO PONTOS DE CULTURA"),
    ("d846d4f3", "compra_publica",
     "processo de seleção de Empreendedores Familiares Rurais, Grupos Formais de Agricultores Familiares, "
     "Cooperativas e Associações, interessados em fornecer gêneros alimentícios"),
    ("3b458de7", "conteudo_editorial",
     "Histórias de sucesso INSTITUTO NOVO SERTÃO — Monitoramento de dados ajudou o Instituto a vencer o Prêmio"),
    ("3f5feb59", "empresa_ou_mercado",
     "SELEÇÃO PÚBLICA, MEDIANTE CHAMAMENTO PÚBLICO, DE EMPRESAS PARA CONCESSÃO DE INCENTIVO ECONÔMICO"),
    ("b905c766", "empresa_ou_mercado",
     "Chamamento Público para credenciar instituições interessadas na DOAÇÃO DE BENS MÓVEIS considerados INSERVÍVEIS"),
    ("e177587a", "empresa_ou_mercado",
     "CREDENCIAMENTO de pessoas jurídicas, com ou sem fins lucrativos (livreiros, distribuidoras e editoras), "
     "para exporem e comercializarem materiais literários junto à 39ª Feira do Livro"),
]

APROVADOS = [
    # editais de fomento reais — nenhum destes pode ser barrado
    ("1eaba08f", "Chamamento Público Cultural nº 11/2024 - Edital de Fomento à Produção Artística e Cultural, "
                 "seleção de projetos culturais inéditos propostos por agentes culturais"),
    ("48513973", "EDITAL DE CHAMAMENTO PÚBLICO Nº 24/2025 da Lei 13.019/14 - TERMO DE COLABORAÇÃO para promover "
                 "o atendimento dos direitos da criança e do adolescente, convoca as OSC inscritas no COMDICA"),
    ("0b2e6b2e", "EDITAL DE CHAMAMENTO PÚBLICO N° 13/2026 LEI N° 13.019/2014 Termo de Colaboração com o objetivo "
                 "de realização do projeto Oficinas de Dança Tradicionalista"),
    ("c0a95ca4", "seleção de 14 propostas de projetos culturais para receberem apoio financeiro na categoria "
                 "AUDIOVISUAL com recursos da Política Nacional Aldir Blanc"),
    ("279fd516", "seleção de Organizações da Sociedade Civil - OSC, sem fins lucrativos, para celebrar Termo de "
                 "Colaboração, voltadas ao atendimento de pessoas idosas"),
    ("c341e848", "EDITAL DE CHAMAMENTO PÚBLICO ASSOCIAÇÕES E COOPERATIVAS DE CATADORES DE MATERIAIS RECICLÁVEIS "
                 "para firmar termo de compromisso para coleta seletiva cidadã"),
    ("8c6a2a0e", "SELEÇÃO DE ASSOCIAÇÃO RURAL PRIVADA, SEM FINS LUCRATIVOS, REPRESENTATIVA DE AGRICULTORES "
                 "FAMILIARES, PARA A CELEBRAÇÃO DE ACORDO DE COOPERAÇÃO"),
    ("6846a6fd", "seleção de entidade de direito privado, sem fins lucrativos, qualificada como Organização da "
                 "Sociedade Civil de Interesse Público - OSCIP, para celebrar Termo de Parceria"),
    ("20ec3e11", "seleção de 6 projetos culturais inéditos na categoria de Árvores Natalinas, propostos por "
                 "artesãos locais"),
    ("2beebeda", "EDITAL DE CHAMAMENTO PARA CONCURSO DE PREMIAÇÃO DE DESTINAÇÃO DE IMPOSTO DE RENDA AO FUNDO "
                 "MUNICIPAL DA CRIANÇA E ADOLESCENTE"),
]


class TesteInconformidade(unittest.TestCase):
  def test_reprovados_por_familia(self):
      for origem, familia, texto in REPROVADOS:
          v = avaliar(texto)
          assert v["ok"] is False, f"{origem} deveria ser reprovado: {texto[:60]}"
          assert v["familia"] == familia, f"{origem}: esperava {familia}, veio {v['familia']}"


  def test_aprovados_nunca_sao_barrados(self):
      """Falso positivo é o erro caro: perde oportunidade e não deixa rastro."""
      for origem, texto in APROVADOS:
          v = avaliar(texto)
          assert v["ok"] is True, f"{origem} foi barrado indevidamente por {v['familia']}: {v['motivo']}"


  def test_oscip_qualificada_passa_mas_com_atencao(self):
      v = avaliar("seleção de entidade qualificada como Organização da Sociedade Civil de Interesse Público "
                  "- OSCIP para celebrar Termo de Parceria na área de saúde")
      assert v["ok"] is True
      assert v["atencao"] and "OSCIP" in v["atencao"]


  def test_inexigibilidade_gera_atencao_e_nao_reprova(self):
      v = avaliar("Chamamento Público nº 07/2024 - Inexigibilidade de licitação nº 047/2024 - seleção de "
                  "propostas de organizações da sociedade civil para Termo de Colaboração")
      assert v["ok"] is True
      assert v["atencao"] and "inexigibilidade" in v["atencao"].lower()


  def test_pagina_de_termos_celebrados_pelo_titulo_isolado(self):
      """A armadilha de goias.gov.br/cultura/termos-de-fomento: título sem edital."""
      v = avaliar_item({"titulo": "Termos de Fomento", "objeto": ""})
      assert v["ok"] is False
      assert v["familia"] == "pagina_de_termos_celebrados"


  def test_titulo_de_fomento_parecido_nao_e_confundido_com_a_pagina(self):
      v = avaliar_item({"titulo": "Edital de Fomento nº 04/2024 - Termos de Fomento a projetos culturais",
                        "objeto": "seleção de projetos culturais"})
      assert v["ok"] is True


if __name__ == "__main__":
    unittest.main()
