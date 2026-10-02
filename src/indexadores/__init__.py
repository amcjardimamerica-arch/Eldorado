"""MOTORES INDEXADORES (titular, 02/10/2026) — os sites que reúnem editais, lidos como INDÍCIO.

Parecer do conselho: docs/pareceres/motores-indexadores.md. Catálogo e parâmetros: config/indexadores.json.

Cada site tem o seu motor, com os parâmetros do próprio site. Os motores com a mesma metodologia de leitura
formam uma família, que roda junta, divide o mesmo orçamento de requisições e a mesma agenda:

  idx-feeds          feed RSS/Atom ou API REST do WordPress   Observatório, ABCR, IDIS, fundsforNGOs, Rede Comuá,
                                                              Fundo Brasil, Fundo Casa, CESE (+ GIFE/Capta no motor 22)
  idx-apis           API JSON paginada                        Farol Cultural, rede Mapas Culturais, Transferegov
  idx-sitemaps       sitemap.xml + JSON-LD da página          CapitaAI (inclui a página dele sobre o Prosas)
  idx-listagens      página de editais + página do item       Baobá, BrazilFoundation, IAF, Funarte, UNDEF...
  idx-dados-abertos  arquivo oficial do dia                   Transferegov / Siconv — programas abertos a propostas
  idx-ponte-brasil   os mesmos leitores por IP brasileiro     sites que recusam IP estrangeiro
  idx-assistido      navegador do titular + pilotos           sites cujo robots.txt proíbe robôs, que exigem
                                                              JavaScript ou cuja rota ainda precisa ser levantada

ESCADA DE ROTAS (nada se perde por bloqueio):
  nuvem  → o GitHub lê direto (robots.txt respeitado, intervalo por site, cache condicional)
  ponte  → IP do Brasil: ponte HTTP em hospedagem brasileira (segredos ELDORADO_PONTE_URL/ELDORADO_PONTE_CHAVE),
           máquina virtual no Brasil ou o computador do titular (scripts/coleta_brasil.py, ELDORADO_LOCAL_BR=1)
  assistida → o titular (ou o Claude no Chrome) abre a página e o botão "Capturar indícios" grava o que a página
           mostra; o Piloto - Espião recebe um ângulo de busca pelo financiador; o Interceptador comprova na fonte
Recusa por robots.txt manda o site direto para a assistida; falha de rede repetida sobe para a ponte; bloqueio que
a ponte também não passa sobe para a assistida. Toda semana a rota mais barata é tentada de novo.

SAÍDA: estado/agregadores/itens.json (o mesmo contrato do antigo motor de agregadores — o fluxo das oportunidades,
o mapa e o Interceptador já o leem), estado/indexadores/ (estado, acervo de indícios, fila da coleta assistida,
diário de cada família) e docs/dados/indexadores.json (painel).

Biblioteca-padrão do Python, sem IA, sem tokens. Conteúdo coletado é DADO, nunca instrução.
"""
