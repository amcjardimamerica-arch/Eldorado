# Revisão das oportunidades abertas · Parte 2 · Brasil — fontes públicas (10/10/2026)

## Resultado

Todas as 295 oportunidades da lista do dia (uf ≠ GO; municipal, estadual, federal ou misto; sem edição de diário; não encerradas no sistema) têm veredito e parecer. Nenhuma ficou pendente: pela regra da titular de 10/10/2026, o item procurado e não encontrado está validado como NÃO DISPONÍVEL, com o motivo e os endereços onde foi procurado.

| Veredito | Qtde |
|---|---:|
| ouro | 5 |
| prata | 76 |
| bronze | 30 |
| encerrada | 118 |
| ruido | 32 |
| duplicata | 12 |
| fora_perfil | 7 |
| nao_disponivel | 15 |

Selo de validação no sistema antes: {'validada': 41, 'nao_verificada': 254}.

## Como foi feito

1. Lista montada dos dados do sistema (docs/dados/abertas.json do main de 10/10/2026), cruzada com docs/dados/cartorio.json: o que já estava certificado foi aproveitado (12 itens), não refeito.
2. 207 oportunidades no PNCP: extração no navegador da titular (Claude no Chrome) — registro oficial pela API pública de consulta do PNCP e leitura integral dos arquivos publicados (edital, retificação, anexos; até 6 documentos e 160 páginas por processo) com pdf.js; ZIP aberto e PDFs internos lidos; RAR e PDF escaneado sem texto registrados como não legíveis. Os 12 itens foram localizados por regras e cada trecho passou por controle de qualidade (trecho que não sustenta o item é descartado e o item vai para não disponível com o motivo).
3. 88 oportunidades fora do PNCP (DOU, gov.br, BNDES, BNB, fundos, portais municipais de compras): leitura por agentes, cada um em aba própria, documento oficial lido; DOU (in.gov.br) não lido por robots.txt — buscado no site do órgão e no PNCP.
4. Veredito por regra: encerrada (fim < 10/10/2026 ou situação anulada/revogada no PNCP), fora_perfil (sem participação de OSC), duplicata (mesmo processo), e ouro/prata/bronze pelo critério permanente.

## Janelas vigentes (ouro, prata e bronze), por prazo

| Fim | Veredito | Oportunidade | id |
|---|---|---|---|
| 2026-10-13T13:00 | bronze | MUNICIPIO DE PAROBE — Formalização de parceria estabelecida pela administração pública com Organização de Soci | `b5f50031116de0c53690` |
| 2026-10-13T13:00 | bronze | MUNICIPIO DE PAROBE — Formalização de parceria estabelecida pela Administração Pública com Organização da Soci | `c745bb5c2cd1b215bedc` |
| 2026-10-13T17:00 | prata | MUNICIPIO DE OLINDINA — o Chamamento Público nº 002/2026, destinado à seleção de projetos culturais para execu | `4ddcee904eef691c218c` |
| 2026-10-14T17:00 | prata | MUNICIPIO DE ITAGIBA — Chamamento Público a seleção de associação ou cooperativa de catadores de materiais rec | `75c434816e399484e9c9` |
| 2026-10-15T00:00 | prata | MUNICIPIO DE LAURO DE FREITAS — Concessão de apoio financeiro para execução de projetos culturais, no âmbito d | `20f8c4b2f5df921e4163` |
| 2026-10-16T00:00 | prata | MUNICIPIO DE ITACOATIARA — [LICITANET] - Seleção de Projetos Culturais para Concessão de Apoio Financeiro e Ce | `4cc0563cfad32112b128` |
| 2026-10-16T16:00 | prata | SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS COM RECURSOS DA POLÍTICA NACIONAL ALD | `a2f833bf388f4584743c` |
| 2026-10-17T23:59 | prata | MUNICIPIO DE JACAREI — CHAMADA PÚBLICA Nº 03/2026 - SEMAPLAN-  SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL (OSC) | `07058d13f051c4fa41cd` |
| 2026-10-17T23:59 | prata | MUNICIPIO DE IBATE — ABERTURA DE EDITAL PARA SELEÇÃO DE PROJETOS CULTURAIS DE ACORDO COM A POLÍTICA NACIONAL A | `db0914e3d455a10e9ad2` |
| 2026-10-19T09:00 | prata | MUNICIPIO DE CAFELANDIA — SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL - OSCS, SEM FINS LUCRATIVOS, PARA CELEBRA | `eaf338374cd00fe1e042` |
| 2026-10-20T14:30 | prata | COMPANHIA NACIONAL DE ABASTECIMENTO — Contratação de entidade sem fins lucrativos, inscrita e aprovada no Cada | `c33c88172f0ce041cc81` |
| 2026-10-20T23:59 | bronze | MUNICIPIO DE IVAIPORA — PREMIAÇÃO POR TRAJETÓRIA, PREVISTO EM PLANO DE AÇÃO DA PNAB, EM ATENDIMENTO ÀS NECESSI | `b8b9f49ac12387efb376` |
| 2026-10-21T00:00 | bronze | CONSELHO DE ARQUITETURA E URBANISMO DO ESTADO DE MINAS GERAIS — O concurso PRÊMIO DE BOAS PRÁTICAS URBANAS: AM | `eedf3e2c1d25c3dfbbc2` |
| 2026-10-21T16:00 | prata | MUNICIPIO DE JARAGUA DO SUL — EDITAL DE CREDENCIAMENTO de sociedades e/ou clubes de tiro, constituídos como pe | `b42a4b4930d247caf973` |
| 2026-10-22T14:00 | prata | MUNICIPIO DE IELMO MARINHO — Seleção de Organização da Sociedade Civil – OSC, em regime de mútua cooperação, p | `a04e689bdd68a474743a` |
| 2026-10-22T23:59 | prata | MUNICIPIO DE PALMAS — Selecao de Organizacao da Sociedade Civil - OSC para celebracao de Termo de Colaboracao  | `b1ef691ad10f4747ba3c` |
| 2026-10-23T09:00 | prata | MUNICIPIO DE CAFELANDIA — CHAMAMENTO PÚBLICO PARA CADASTRAMENTO DE ENTIDADES SEM FINS LUCRATIVOS DEVIDAMENTE C | `13cf5ff5b8a613422109` |
| 2026-10-23T09:00 | prata | MUNICIPIO DE ALEXANDRIA — SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL - OSC PARA CELEBRAÇÃO DE TERMO DE COLABORA | `2e41430c20d9d7510989` |
| 2026-10-23T23:59 | prata | MUNICIPIO DE VERA CRUZ — Seleção de proposta/Plano de trabalho para a formalização de parceria através de Term | `509b167451aff1013f95` |
| 2026-10-25T23:59 | prata | MUNICIPIO DE SIMOES FILHO — Seleção de projetos culturais para receberem apoio financeiro nas categorias
desc | `ba78086f580da195a28e` |
| 2026-10-26 | ouro | Ministério da Saúde — EDITAL DE CHAMAMENTO PÚBLICO Nº 6/2026 | `53e63b00b33f797d57e8` |
| 2026-10-26 | ouro | Ministério da Saúde — EDITAL DE CHAMAMENTO PÚBLICO Nº 7/2026 | `5a82c53aac8b6f4e5d28` |
| 2026-10-26T08:59 | prata | MUNICIPIO DE SENADOR POMPEU — Constitui objeto desta chamada pública a seleção e apoio a realização de iniciat | `10a6c7656762dd1545d2` |
| 2026-10-26T23:59 | prata | FUNDACAO CULTURAL DE RIO DO SUL — CREDENCIAMENTO PARA EVENTUAIS E FUTURAS CONTRATAÇÕES DE SERVIÇOS ARTÍSTICOS  | `eeb3853aeb4c9cedf3b4` |
| 2026-10-27T18:00 | prata | MUNICIPIO DE VOLTA REDONDA — Chamamento destinado a premiação  de atividades e ações já realizadas por pontos  | `f0575775c56f933c8430` |
| 2026-10-27T23:59 | prata | MUNICIPIO DE ITAMONTE — Credenciamento de entidades privadas sem fins lucrativos para a prestação de serviços  | `3bdbb3eae19591c52807` |
| 2026-10-28T23:59 | prata | Seleção de projetos culturais de artesãos locais para a confecção, entrega, montagem e desmontagem de decoraçã | `20ec3e11386b87af1e16` |
| 2026-10-30T17:00 | prata | MUNICIPIO DE BARAO — SELEÇÃO DE PROJETOS CULTURAIS PARA RECEBIMENTO DE RECURSOS DA LEI ALDIR BLANC | `98f376948bbeb7284fec` |
| 2026-10-30T18:00 | prata | MINISTERIO PUBLICO DO ESTADO DO CEARA — Seleção e premiação de trabalhos jornalísticos que abordem o tema “Min | `57bc9ffcadd9fb58077d` |
| 2026-10-31 | ouro | Lei Rouanet — apresentação de propostas culturais no SALIC (2026): de 01/02 a 31/10 | `4b30661ea4d6e01e0607` |
| 2026-11-03T17:00 | prata | MUNICIPIO DE SANTO ANTONIO DE JESUS — Seleção de Organização da Sociedade Civil – OSC para a celebração de TER | `c95d24c20468afd69320` |
| 2026-11-04T10:00 | bronze | MUNICIPIO DE CACHOEIRINHA — Seleção de Organização da Sociedade Civil - OSC, por meio de Chamamento Público, p | `b81b46a1275ddeb324a1` |
| 2026-11-09T18:00 | prata | CHAMAMENTO PUBLICO PARA CREDENCIAMENTO DE INSTITUICOES PRIVADAS  COM OU SEM FINS LUCRATIVOS  ESPECIALIZADA NA  | `8ed7377b4962ae08907b` |
| 2026-11-10T13:59 | prata | MUNICIPIO DE NOVO HAMBURGO — CHAMAMENTO PÚBLICO PARA SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL (OSC), SEM FINS | `073f196011843d451f36` |
| 2026-11-12T23:59 | prata | MUNICIPIO DE VERA CRUZ — Formalização de parceria através de Termo de Colaboração, com Organizações da Socieda | `1721977585e3ca35e848` |
| 2026-11-13T09:00 | bronze | MUNICIPIO DE CARAZINHO — Abertura de CHAMAMENTO PÚBLICO para a seleção de Organizações da Sociedade Civil - OS | `93cb00c624de9b7ca82b` |
| 2026-11-18 | ouro | Agência Nacional de Assistência Técnica e Extensão Rural — AVISO DE SELEÇÃO PÚBLICA | `b629cc2bc40bb6443783` |
| 2026-11-19T14:30 | prata | SUP. EST. DE LICITACAO — O presente Chamamento Público tem por objeto selecionar Organização da Sociedade Civi | `3b0a8b47aa7165a5b8da` |
| 2026-11-25T11:42 | prata | MUNICIPIO DE RIO DE JANEIRO — Credenciamento de instituições privadas, sem fins lucrativos,
que ofereçam acolh | `fb1a2ebe8e4bf465a30e` |
| 2026-11-28T08:00 | bronze | MUNICIPIO DE RIO REAL — EDITAL  DE  CREDENCIAMENTO  Nº  012/2026,  PARA FINS DE CREDENCIAR ORGANIZAÇÕES  DA SO | `844ef740fd826aeea799` |
| 2026-11-30T00:00 | prata | MUNICIPIO DE SANTA HELENA — CHAMAMENTO PÚBLICO COM A FINALIDADE DE SELECIONAR PROJETOS ESPORTIVOS VISANDO ATEN | `ea635ceac61bc61e6dd5` |
| 2026-12-03T17:00 | prata | FUNDACAO JOAQUIM NABUCO FUNDAJ — Realização de concurso de premiação destinado à seleção de Práticas Pedagógic | `f8684c2f36149d7434e3` |
| 2026-12-04T17:00 | prata | MUNICIPIO DE MONTES CLAROS — CHAMAMENTO PUBLICO PARA O CREDENCIAMENTO DE ESTABELECIMENTOS HOSPITALARES DE SAUD | `d4ba242de9b46c64ada9` |
| 2026-12-10T08:00 | prata | Credenciamento de associações, cooperativas, entidades sem fins lucrativos e empresas para a coleta seletiva s | `f5f21c7b1d22fd5f7741` |
| 2026-12-10T23:59 | bronze | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL DE JAGUARUNA — CREDENCIAMENTO DE INSTITUIÇÕES SEM FINS LUCRATIVOS, DESTI | `e365c795e23c145705fd` |
| 2026-12-11T09:00 | prata | MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO DE SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSC) PARA CELEBRAÇ | `0c0e5d9749876f121e93` |
| 2026-12-30T09:52 | prata | AGENCIA MUNICIPAL DE REGULACAO DE SERVICOS DELEGADOS- ARSER — CHAMAMENTO PÚBLICO PARA A SELEÇÃO DE UMA ORGANIZ | `cb432735cfee7c76d00c` |
| 2026-12-31T00:00 | prata | MUNICIPIO DE PERITIBA — O objeto deste Edital é a seleção de projetos culturais para receberem apoio financeir | `5b744c9be242e7f5a4fb` |
| 2026-12-31T10:10 | prata | DEFENSORIA PUBLICA DO ESTADO DO PARANA — O objeto do presente credenciamento selecionar associações e/ou coope | `0dfc53b2787c26812fd2` |
| 2026-12-31T18:00 | prata | MUNICIPIO DE GOVERNADOR CELSO RAMOS — CREDENCIAMENTO DE PESSOAS JURÍDICAS COM OU SEM FINS LUCRATIVOS INTERESSA | `259543bcbd79cc952f82` |
| 2026-12-31T23:59 | prata | MUNICIPIO DE MARACANAU — HAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ENTIDADES COMUNITÁRIAS, SEM FINS LUCRATIVOS/ | `f2329152462a87d05c3f` |
| 2027-02-02T23:59 | prata | MUNICIPIO DE CLEVELANDIA — Chamamento Público destinado à seleção de projetos de Organizações da Sociedade Civ | `cd7d07b0009238ddda36` |
| 2027-02-05T00:00 | prata | MUNICIPIO DE NOVO HAMBURGO — CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE OSCS APTAS A EXECUÇÃO DO SERVIÇO DE ACO | `cbd60d52f1eeca58bdcf` |
| 2027-03-08T09:00 | prata | MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO (OSC’S) DE EXECUÇÃO DE PROJETO ESPORTIVO VOLTADO Á DIFUSÃO DO ESP | `edb376915e2eaa590a49` |
| 2027-03-11T17:00 | prata | MUNICIPIO DE RESTINGA SECA — O objeto deste Termo de Referencia e o credenciamento de Organizacoes da Sociedad | `49da9f5df54f25e60580` |
| 2027-03-26T10:00 | prata | MUNICIPIO DE EUSEBIO — Chamamento Público para credenciamento de entidades privadas, sem fins lucrativos, que  | `7e88f1b374732125b1f4` |
| 2027-04-08T00:00 | prata | FUNDO MUNICIPAL DO BEM ESTAR SOCIAL — Credenciamento de instituições privadas, com ou sem fins lucrativos, par | `7fb96ad0c678671f55f6` |
| 2027-04-09T00:00 | prata | MUNICIPIO DE SAPUCAIA DO SUL — O presente Termo de Colaboração tem por objeto estabelecer as condições para o  | `55d0539fef97234b8ec9` |
| 2027-04-15T23:59 | prata | MUNICIPIO DE BIQUINHAS — contratação de ONG ou OSC para execução de projetos para crianças e adolescentes, con | `9f4a8a40c4cfeaeaefde` |
| 2027-04-22T08:16 | prata | MUNICIPIO DE QUATIGUA — Credenciamento para seleção de associação de estudantes regularmente constituída, sem  | `69183c19f4109edfe34d` |
| 2027-05-04T17:00 | bronze | (UO) ESP-CIA.PTA DE TRENS METROPS-CPTM — Credenciamento de associações e/ou cooperativas de catadores de mater | `4b7b01fdcbb766bdb605` |
| 2027-05-20T17:00 | prata | MUNICIPIO DE PALMEIRA DOS INDIOS — CREDENCIAMENTO DE CARÁTER PERMANENTE DAS ORGANIZAÇÕES DA SOCIEDADE CIVIL –  | `bdb24ed7d6f1d24f0697` |
| 2027-05-27T16:00 | bronze | SECRETARIA MUNICIPAL DE EDUCACAO — Credenciamento de Organizações da Sociedade Civil (OSC), com vistas a possí | `41b5e8d92382497ee954` |
| 2027-06-11T23:59 | bronze | MUNICIPIO DE CASTRO — CHAMAMENTO PÚBLICO PARA FINS DE  CREDENCIAMENTO DE COOPERATIVA OU ASSOCIAÇÃO OU DA INICI | `a5b735b5c65fa78c06c8` |
| 2027-06-18T18:00 | bronze | MUNICIPIO DE GRAVATAI — Credenciamento para seleção de pontos de cultura. | `854473337395b5da8c26` |
| 2027-06-28T09:49 | prata | MUNICIPIO DE PALMEIRA DOS INDIOS — Constitui-se objeto do presente Edital estabelecer o cumprimento das normas | `69322c6a48f05a2475c3` |
| 2027-06-30T00:00 | prata | MUNICIPIO DE APUCARANA — Chamamento público para formação de cadastro de pessoas físicas, jurídicas e entidade | `73961f49f7a9b54816cc` |
| 2027-07-10T08:00 | prata | MUNICIPIO DE ITAITINGA — CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL – OSCS PARA EXECUÇÃO DE ESCOLINHAS  | `4c81862de69688f20a15` |
| 2027-07-22T17:00 | prata | MUNICIPIO DE CRICIUMA — Convocação de pessoas jurídicas, com ou sem fins lucrativos, interessadas em se creden | `b373cd034c5e2fe02065` |
| 2027-07-27T00:00 | prata | FUNDO MUNICIPAL DE SAUDE DE LAGES — O presente Edital tem por objeto o credenciamento de Pessoas Jurídicas (PJ | `1074b72bdf1e1e67f415` |
| 2027-07-30T23:59 | prata | MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO — Reabertura do Edital de Credenciamento SEE nº 02/2025 - Creden | `9a64fee8a5cb67d5cbf0` |
| 2027-08-11T23:59 | prata | MUNICIPIO DE JANDAIRA — CREDENCIAMENTO DE ARTISTAS, GRUPOS, COLETIVOS E AGENTES CULTURAIS, NOS TERMOS DA LEI F | `f1217f4e9361558eeb40` |
| 2027-08-20T08:00 | prata | MUNICIPIO DE JOAQUIM GOMES — CREDENCIAMENTO SAÚDE, PARA FINS DE SELECIONAR ORGANIZAÇÕES DA SOCIEDADE CIVIL PAR | `0fbc79bf69e4084959e8` |
| 2027-09-10T19:00 | bronze | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL DE JOACABA — Credenciamento de organizações da sociedade civil para a pr | `a38a503f0bc769fda218` |
| 2027-09-14T18:00 | prata | FUNDO MUNICIPAL DE SAUDE DE JEQUIE — 1.1.  Contratação de Organização da Sociedade Civil (OSC) para prestação  | `083fb24f28267223a151` |
| 2027-09-30T14:00 | prata | MUNICIPIO DE BOA VISTA — credenciamento de Instituições de Longa Permanência para Idosos – ILPI, pessoas juríd | `8e41abc05e4b987f5bde` |
| 2027-12-31T00:00 | prata | MUNICIPIO DE CANOAS — O Município de Canoas torna pública a abertura de inscrições que tem por objeto o creden | `1bec3d5e5a013248c7ed` |
| 2027-12-31T00:00 | prata | MUNICIPIO DE CANOAS — Credenciamento de Agremiações Carnavalescas, Agremiações de Samba com personalidade jurí | `1c42fb1302349fa265d7` |
| 2027-12-31T00:00 | prata | MUNICIPIO DE CANOAS — EDITAL Nº. 305/2024 CHAMAMENTO PÚBLICO – O Município de Canoas torna pública a abertura  | `83c2d963e00c05e5c3b8` |
| 2027-12-31T00:00 | prata | MUNICIPIO DE CANOAS — Credenciamento de grupos e/ou artistas individuais da área da música, pessoas físicas ou | `b1484be332471bd2ca73` |
| 2028-01-18T23:59 | prata | MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entidades privadas ou públicas, com ou sem fins lucrativos | `de5a129df213bb5aabaf` |
| 2028-01-31T18:00 | prata | TRIBUNAL REGIONAL ELEITORAL DO AMAZONAS — O presente procedimento tem por objeto selecionar as associações e/o | `92a0f7cc763648155875` |
| 2028-02-08T18:00 | bronze | UNIVERSIDADE FEDERAL DE PERNAMBUCO — Selecionar e habilitar as associações e/ou cooperativas de catadores de m | `b06dc0bf0fa9f50b01ba` |
| 2028-04-15T23:59 | prata | MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entidades privadas, com ou sem fins lucrativos, para acolh | `ad01cbbd839850376a04` |
| 2028-11-14T13:30 | bronze | MUNICIPIO DE GUARATUBA — Credenciamento de Organizações da Sociedade Civil (OSC), conforme o disposto na Lei F | `8b08eb6f9f5235ef5fc2` |
| 2028-12-11T17:00 | bronze | MUNICIPIO DE CARAZINHO — Celebração de termo de colaboração, com Organização da Sociedade Civil (OSC), em regi | `9529614b736be766828b` |
| 2028-12-29T17:00 | prata | MUNICIPIO DE QUATRO BARRAS — Credenciamento de Instituições de longa permanência para idosos (ILPI), com e sem | `dbfc56b208ea4a40af25` |
| 2029-11-05T14:01 | bronze | MUNICIPIO DE PERUIBE — CREDENCIAMENTO DE INSTITUIÇÕES PRIVADAS, COM OU SEM FINS LUCRATIVOS, INSTITUIÇÕES DE LO | `436cca92657e114402d7` |
| 2029-11-12T08:15 | bronze | MUNICIPIO DE CARAZINHO — Atendimento de matrículas na educação infantil oferecida em escolas ou centros de edu | `e05f89c18b8ce4aae022` |
| 2029-11-28T17:00 | bronze | MUNICIPIO DE CARAZINHO — Celebração de termo de colaboração, com Organização da Sociedade Civil (OSC), em regi | `010a967394a8e184acbc` |
| 2029-12-05T17:00 | bronze | MUNICIPIO DE CARAZINHO — Celebração de termo de colaboração, com Organização da Sociedade Civil (OSC), em regi | `9cca448fbd87acdc205c` |
| 2030-04-05T08:00 | bronze | TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciamento de associação e/ou cooperativa de catadores de mat | `bc7f2307e42ed5bd8536` |
| 2030-08-16T16:00 | prata | MUNICIPIO DE TELEMACO BORBA — Credenciamento de cooperativas e associações de catadores de materiais recicláve | `7f36da8ad9945612c787` |
| 2030-09-07T18:00 | bronze | SAO PAULO TRIBUNAL DE JUSTICA — Chamamento  Público  para  seleção  e  cadastro  de  cooperativas  e/ou  assoc | `e1a46fb1b974d54599f6` |
| 2030-11-11T00:00 | prata | MUNICIPIO DE ESTANCIA VELHA — 1.1. O presente Edital tem como objeto o credenciamento de Organizações da Socie | `f53b2577ce78d95e00ee` |
| 2030-11-18T09:00 | prata | MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO PARA EXECUÇÃO DE TERMO DE COLABORAÇÃO PARA OSC’S PRESTA | `7b300087659bb0b387c9` |
| 2030-11-25T09:00 | prata | MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO PARA PARCERIA EM REGIME DE COLABORAÇÃO ENTRE A SECRETAR | `d810b5f262c0ac09c067` |
| 2030-12-04T00:00 | bronze | TRIBUNAL DE JUSTICA DO ESTADO DE ALAGOAS — [LICITANET] - Chamamento público na forma de credenciamento de asso | `a8b026eec92ee050dabe` |
| 2030-12-11T08:00 | bronze | FUNDACAO UBERLANDENSE DO TURISMO ESPORTE E LAZER — Credenciamento de interessados (terceiro facilitador) na ca | `1f6f8ec7518f17718fc9` |
| 2031-06-25T23:59 | prata | MUNICIPIO DE PASSOS — Credenciamento de Instituições de Longa Permanência para Idosos – ILPI, pessoas jurídica | `5cac39c12aff0c6a38f4` |
| 2034-04-26T18:00 | bronze | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento TRT4 n° 01/2023 Credenciamento de associações e/ou cooperativas | `9b629429aba64de24cec` |
| 2035-01-15T17:00 | bronze | INSTITUTO FEDERAL DE EDUCACAO, CIENCIA E TECNOLOGIA DO SUL DE MINAS GERAIS — O presente procedimento tem por o | `52a1fdf5d0e54202eeb0` |
| 2035-01-17T10:00 | prata | MUNICIPIO DE SAPUCAIA DO SUL — Credenciamento de instituições e/ou organizações da sociedade civil que ofertem | `36ea5a7aff849b51f69f` |
| 2035-03-12T08:00 | bronze | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento de Cooperativas ou Associações de catadores de materiais recicl | `41375e79a6330c95344c` |
| 2035-05-14T18:00 | prata | TRIBUNAL SUPERIOR ELEITORAL — Credenciamento de associações e/ou cooperativas de catadores de materiais recicl | `6e7349afbef4f1ca58af` |
| 2035-06-15T18:00 | bronze | MINISTERIO PUBLICO DO ESTADO DO PARANA — Selecionar associação e/ou cooperativa de catadores de materiais reci | `6d88f6e5b147d98ea783` |
| 2035-07-18T00:00 | bronze | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL DE INDAIAL — Credenciamento de instituições privadas, com ou sem fins lu | `c395006ea4b6ded6ec82` |
| 2036-07-01T23:59 | prata | MUNICIPIO DE NOVA SANTA RITA — CREDENCIAMENTO DE INSTITUIÇÕES DE LONGA PERMANÊNCIA PARA IDOSOS (ILPI), pública | `c5a5fb20f0d79a868571` |
| 2074-04-18T08:00 | prata | MUNICIPIO DE RIO DO SUL — CREDENCIAMENTO DE COOPERATIVAS/ASSOCIAÇÕES DE CATADORES DE RESÍDUOS RECICLÁVEIS E EM | `2465eeabeeaebe0b06a1` |
| fluxo contínuo | bronze | Patrocínios | `a79ca2660a0964f27c52` |
| fluxo contínuo ( | ouro | [Portal de Compras Públicas] - CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSC), NOS TERMOS DA LEI Nº 1 | `86986fa70777dd1369fa` |

## Eficiência dos 12 itens nas oportunidades ativas (ouro, prata, bronze e não disponível)

| Item | Obtidos | Dispensados | Não disponíveis | % resolvido |
|---|---:|---:|---:|---:|
| Objeto | 118 | 0 | 8 | 94% |
| Prazo de inscrição | 111 | 0 | 15 | 88% |
| Resultado | 33 | 3 | 90 | 29% |
| Prazo de recurso | 24 | 6 | 96 | 24% |
| Valor | 99 | 0 | 27 | 79% |
| Órgão / financiador | 114 | 0 | 12 | 90% |
| Território | 114 | 0 | 12 | 90% |
| Esfera | 114 | 0 | 12 | 90% |
| Requisitos | 97 | 0 | 29 | 77% |
| Anexos | 111 | 0 | 15 | 88% |
| Destinação | 35 | 2 | 89 | 29% |
| Área de atuação | 105 | 0 | 21 | 83% |

## Não disponíveis (oportunidade sem documento oficial acessível)

- `dda8007e1d8312ed1ab8` MUNICIPIO DE IJUI — Credenciamento de instituicoes privadas sem fins lucrativos  atuantes  — Prazo de inscrição: não disponível: não consta nos documentos lidos por inteiro (EDITAL CH 02 2026 [Edital] (12 págs.) | não legíveis: ETP [Estudo Técnico Preli; Resultado: não disponível: não consta nos documentos lidos por inteiro (EDITAL CH 02 2026 [Edital] (12 págs.) | não legíveis: ETP [Estudo Técnico Preli
- `1670991e14bacea46454` CONTRATAÇÃO DE ENTIDADES PRIVADAS, SEM FINS LUCRATIVOS, ORGANIZAÇÕES DA SOCIEDADE CIVIL DE — Prazo de inscrição: não disponível: não consta nos documentos lidos por inteiro (EDITAL corrigido pos parecer juridico [Edital (60 págs.); 13 FORMALIZACAO DA DE; Resultado: não disponível: não consta nos documentos lidos por inteiro (EDITAL corrigido pos parecer juridico [Edital (60 págs.); 13 FORMALIZACAO DA DE
- `5b28b15d43e434599db1` Credenciamento no CHAMAMENTO PÚBLICO Nº. 002/2025, referente ao Credenciamento de Entidade — Prazo de inscrição: não disponível: não consta nos documentos lidos por inteiro (edital_42_2026_2865_documento.pdf [Edital] (42 págs.)); Resultado: não disponível: não consta nos documentos lidos por inteiro (edital_42_2026_2865_documento.pdf [Edital] (42 págs.))
- `3e23011b7b440988c469` Edital de Apoio a Projetos para a Melhoria de Resíduos Sólidos em Minas Gerais — Prazo de inscrição: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f; Resultado: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f
- `8cb4feb3bc32b59b3b56` Editais de Fomento a Ações de Prevenção e Combate de Incêndios Florestais na Amazônia e Pa — Prazo de inscrição: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f; Resultado: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f
- `097bcd4b298c7e73615e` MMA (meio ambiente) — AVISO DO CHAMAMENTO PÚBLICO Nº 3/2026 — Objeto: documento não acessível: ato publicado só no DOU (in.gov.br bloqueado por robots.txt) e não localizado no site do órgão nem no PNCP; Prazo de inscrição: documento não acessível: ato publicado só no DOU (in.gov.br bloqueado por robots.txt) e não localizado no site do órgão nem no PNCP
- `794d37e62371237ba9dd` Gráfica do Exército — AVISO DE CHAMAMENTO PÚBLICO Nº 1/2026 — é selecionar as associações  — Objeto: documento não acessível: ato publicado só no DOU (in.gov.br bloqueado por robots.txt) e não localizado no site do órgão nem no PNCP; Prazo de inscrição: documento não acessível: ato publicado só no DOU (in.gov.br bloqueado por robots.txt) e não localizado no site do órgão nem no PNCP
- `6304cd5b5ce07ac96cdf` MEC (educação) — EDITAL DE CHAMAMENTO PÚBLICO Nº 13/2026/UFSJ/PROEX — Objeto: documento não acessível: ato só localizado no DOU (in.gov.br bloqueado por robots.txt) e não encontrado no site oficial da instituição nem n; Prazo de inscrição: documento não acessível: ato só localizado no DOU (in.gov.br bloqueado por robots.txt) e não encontrado no site oficial da instituição nem n
- `400d80f3c84332f2aa0c` EDITAL DE Nº 126/IFAL, DE 18 DE SETEMBRO DE 2026 — Objeto: documento não acessível: ato só localizado no DOU (in.gov.br bloqueado por robots.txt) e não encontrado no site oficial da instituição nem n; Prazo de inscrição: documento não acessível: ato só localizado no DOU (in.gov.br bloqueado por robots.txt) e não encontrado no site oficial da instituição nem n
- `50bebfcc82d0f1110001` Prêmio Guardiãs FNRB — Prazo de inscrição: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f; Resultado: documento não acessível: a página do registro e a notícia oficial vinculada exigem login no gov.br/mma ('Conteúdo Restrito'); o edital não f
- `9431061aa045496e1845` Instituto Federal de Educação, Ciência e Tecnologia do Maranhão AVISO DE CHAMADA PÚBLICA N — Objeto: documento oficial não acessível: o agregador remete ao DOU (pesquisa.in.gov.br, bloqueado por robots.txt e pela regra da instrução); a busca; Prazo de inscrição: documento oficial não acessível: o agregador remete ao DOU (pesquisa.in.gov.br, bloqueado por robots.txt e pela regra da instrução); a busca
- `cbf635c775d28f9e101a` Instituto Federal de Educação, Ciência e Tecnologia do Sul de Minas Gerais AVISO DE CHAMAD — Objeto: documento oficial não acessível: o agregador remete ao DOU de 30/09/2026 (pesquisa.in.gov.br, bloqueado); no PNCP o IF Sul de Minas tem só a; Prazo de inscrição: documento oficial não acessível: o agregador remete ao DOU de 30/09/2026 (pesquisa.in.gov.br, bloqueado); no PNCP o IF Sul de Minas tem só a
- `9491bc3deb96c68589a5` Instituto Nacional de Cardiologia Aviso de Chamamento Público - Instituto Nacional de Card — Objeto: documento oficial não acessível: o agregador remete ao DOU de 01/10/2026 (pesquisa.in.gov.br, bloqueado); o PNCP não tem chamamento do Insti; Prazo de inscrição: documento oficial não acessível: o agregador remete ao DOU de 01/10/2026 (pesquisa.in.gov.br, bloqueado); o PNCP não tem chamamento do Insti
- `ebc8c536f562b184c9ba` Prêmio Pretas Potências seleciona 25 artistas negros com premiação de até R$ 15 mil — Objeto: documento oficial não acessível: a notícia (pista) leva ao login do Prosas (prosas.com.br/users/sign_in — exige login e é agregador); o site; Prazo de inscrição: documento oficial não acessível: a notícia (pista) leva ao login do Prosas (prosas.com.br/users/sign_in — exige login e é agregador); o site
- `e4b7a02df6a39d46c2d4` CHAMAMENTO PÚBLICO 
                                     
                               — Prazo de inscrição: documento não acessível: download do edital bloqueado por verificação de conexão (antibot) em carire.ce.gov.br; não consta na página de deta; Resultado: documento não acessível: download do edital bloqueado por verificação de conexão (antibot) em carire.ce.gov.br; não consta na página de deta

## Reclassificações (encerrada, ruído, duplicata, fora do perfil)

| id | Veredito | Oportunidade | Duplicata de |
|---|---|---|---|
| `d99362ca1a0bdd6b20f1` | duplicata | MUNICIPIO DE CONFINS — SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULT | a2f833bf388f4584743c |
| `50964527e53485d348d7` | duplicata | Seleção de Organização da Sociedade Civil – OSC, em regime de mútua cooperação, para celeb | a04e689bdd68a474743a |
| `b858a9eb612d1ab1fe14` | duplicata | CREDENCIAMENTO DE INSTITUIÇÕES PRIVADAS, COM OU SEM FINS LUCRATIVOS, INSTITUIÇÕES DE LONGA | 436cca92657e114402d7 |
| `c56aeb316394d1876f1e` | duplicata | Formalização de parceria através de Termo de Colaboração, com Organizações da Sociedade Ci | 1721977585e3ca35e848 |
| `88df90e8e285a45cc48f` | duplicata | Lei Rouanet | 4b30661ea4d6e01e0607 |
| `b2db4fce01db2a315c98` | duplicata | Lei Rouanet | 4b30661ea4d6e01e0607 |
| `674ef20921aacd611cf1` | duplicata | Patrocínio a projetos culturais | a79ca2660a0964f27c52 |
| `3dc97bcded767d8821fb` | duplicata | Patrocínio a projetos culturais | 674ef20921aacd611cf1 |
| `b5323a434235b31a79fc` | duplicata | regulamento do edital | bfc98b5b97b2d69e9156 |
| `8d68b63a3f33ff43ac3f` | duplicata | Credenciamento de Agremiações Carnavalescas, Agremiações de Samba com personalidade jurídi | 1c42fb1302349fa265d7 |
| `ab865aa353056669100e` | duplicata | [LICITANET] - Chamamento público na forma de credenciamento de associações e/ou cooperativ | a8b026eec92ee050dabe |
| `38de63878d5d74c687cb` | duplicata | o Chamamento Público nº 002/2026, destinado à seleção de projetos culturais para execução  | 4ddcee904eef691c218c |
| `2d3a38f3a6dd4116daa6` | encerrada | UNIVERSIDADE FEDERAL RURAL DA AMAZONIA — PROCEDIMENTO DE HABILITAÇÃO DAS ASSOCIAÇÕES E/OU  |  |
| `0b450a2c39a0f35d0cfa` | encerrada | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL DE JOACABA — Credenciamento de organizações da socie |  |
| `6a58f8a7ec70081b3bdc` | encerrada | TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciamento de associação e/ou cooperativa |  |
| `d85b46356336683ae29c` | encerrada | TRIBUNAL SUPERIOR DO TRABALHO — EDITAL CREDENCIAMENTO 001/2024 - Credenciamento de associa |  |
| `001575a84b970c14e51a` | encerrada | Credenciamento de Organizações da Sociedade Civil - OSCs, sem fins lucrativos, destinados  |  |
| `02beaaebc68cfe0ebe7b` | encerrada | Seleção de propostas para a celebração de parceria entre o Município de Indaiatuba, por in |  |
| `09f664bbbfa76202950d` | encerrada | Credenciamento prévio de Organizações da Sociedade Civil (OSC) que trabalhem no ramo de AT |  |
| `0ca64575883fcb221817` | encerrada | Contratação de Serviço de Contratação de Assessoria Técnica em Comunicação e Educação em S |  |
| `0d4f0342c8c749f89bc2` | encerrada | O Município de AURORA através da SECRETARIA MUNICIPAL DA SAÚDE, torna público que, a reali |  |
| `124e729949bb04e846cf` | encerrada | Chamamento público tem por objeto o credenciamento de Organizações da Sociedade Civil para |  |
| `14a08a92997115da8279` | encerrada | SELECAO DE PROJETOS CULTURAIS COM RECURSOS DA POLITICA NACIONAL ALDIR BLANC DE FOMENTO A C |  |
| `14bd072e6e716efd39ce` | encerrada | Credenciamento de OFICINAS ARTÍSTICAS para a execução de oficinas culturais, educacionais  |  |
| `20e277641af167ecdbdb` | encerrada | PMIS - Credenciamento de Organizações da Sociedade Civil – OSCs para Prestar Serviço de Pr |  |
| `244e3090efac17f5c82b` | encerrada | CHAMAMENTO PÚBLICO VISANDO A FORMALIZAÇÃO DE PARCERIA COM ORGANIZAÇÃO DA SOCIEDADE CIVIL P |  |
| `25763cc0ca8d2e40e805` | encerrada | Credenciamento das entidades hospitalares filantrópicas ou privadas sem fins lucrativos, i |  |
| `29585d83ca0266020fe0` | encerrada | Credenciamento de Entidades sem fins lucrativos e/ou Empresas Privadas de Acolhimento Inst |  |
| `2abadd217ee84f41ed61` | encerrada | O presente Chamamento Público reger-se-á pela legislação aplicável à espécie, especialment |  |
| `34fcd0f7fbf6291a42f3` | encerrada | PROCESSO PARA SELEÇÃO DE ENTIDADE DE DIREITO PRIVADO, SEM FINS LUCRATIVOS, QUALIFICADA COM |  |
| `370a35b17408d622d9aa` | encerrada | SELEÇÃO DE PROJETOS DE CAPACITAÇÕES, AÇÕES EDUCATIVAS, DE FORMAÇÃO E/OU QUALIFICAÇÃO NA ÁR |  |
| `3cc9781a2d18e14bc2bb` | encerrada | Credenciamento de associações e/ou cooperativas de catadores de materiais recicláveis para |  |
| `3d3a5eb6350efeaad0a5` | encerrada | Incremento dos serviços que estão sob o ecopo da OSC Associação Pestalozzi de Sumaré conve |  |
| `423df80a2594fd93c5e3` | encerrada | SELEÇÃO DE PROPOSTAS DE APOIO AS ORGANIZAÇÕES DA SOCIEDADE CIVIL, NA PREFEITURA MUNICIPAL  |  |
| `43ec6258b8523a140c08` | encerrada | SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSC) INTERESSADAS EM CELEBRAR TERMO DE FOMENTO |  |
| `46111422f37ef6518d03` | encerrada | O PRESENTE CHAMAMENTO TEM POR OBJETO SELECIONAR 1 (UMA) PESSOA JURÍDICA DE DIREITO PRIVADO |  |
| `48e4eaa9e03f92b585f2` | encerrada | CREDENCIAMENTO, com o objetivo de formalização de Parceria, através de Termo de Fomento, c |  |
| `4e8961e172feb22c5227` | encerrada | Termo de Colaboração para apoio cultural com entidades mantenedoras de rádios comunitárias |  |
| `52715deee843fac8f817` | encerrada | Seleção projetos de Organizações da Sociedade Civil - OSC para celebração de Termo de Fome |  |
| `57c89961908faa5f036f` | encerrada | CHAMAMENTO PÚBLICO para seleção de Entidades sem Fins Lucrativos ¿ ESFL, inscritas no Cada |  |
| `57e0fb4aaec433d2ce48` | encerrada | SELEÇÃO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL (OSC) PARA A EXECUÇÃO DAS AÇÕES DO PROGRAMA MUNI |  |
| `5a164e842a017b25540d` | encerrada | Análise de Projeto Esportivo na Modalidade Oficinas Esportivas Arbitragem e Premiação para |  |
| `5cac35cde6c492702230` | encerrada | CHAMAMENTO PÚBLICO Nº 005/2024, credenciamento de grupos formais, organizações produtivas  |  |
| `630ea3c4bbb8cb73700c` | encerrada | Premiação de credenciamento de pessoa física e jurídica referente aos recursos remanescent |  |
| `645f8bc3798ac55c4cfe` | encerrada | Celebração de Termo de Colaboração para a consecução de finalidade de interesse público de |  |
| `65a4aa3ab802e3c2daa1` | encerrada | CONVOCAÇÃO PÚBLICA PARA CREDENCIAMENTO DESTINADA À QUALIFICAÇÃO DE PESSOAS JURÍDICAS DE DI |  |
| `68111c6e0dae2ee91834` | encerrada | 1Contratação de serviço de fisioterapia sessão em grupo (por grupo), conforme Comunicação  |  |
| `6f4da659dfd7edee94a3` | encerrada | Contratação de serviço de profissional de serviço profissional técnico em Radiologia (regi |  |
| `7042e5df6724ab70d55c` | encerrada | Seleção de projetos que contemplem as mais variadas formas de atividades artísticas e cult |  |
| `7895a614dca5280de279` | encerrada | Contratação objetivando a recepção e seleção de instituições/ Organizações da Sociedade Ci |  |
| `7a194405a57ce59aeb49` | encerrada | CHAMAMENTO PUBLICO  para fins de CREDENCIAMENTO de estabelecimentos de saude prestadores d |  |
| `7ac70128a1901aa7d24d` | encerrada | CREDENCIAMENTO DE PESSOAS JURÍDICAS COM OU SEM FINS LUCRATIVOS PARA REALIZAÇÃO DE PROCEDIM |  |
| `7fdf39fdc8408c972ef1` | encerrada | PARCERIA PARA EXECUÇÃO POR ORGANIZAÇÃO DA SOCIEDADE CIVIL (OSC) DE SERVIÇO DE CASTRAÇÃO DE |  |
| `80283fe7346eec3fae05` | encerrada | Chamamento Publico  n° 01/2024 com as organizações da Sociedade Civil para a execução do C |  |
| `82f947d591f92ed7759c` | encerrada | O presente procedimento tem por objeto subsidiar o Chamamento Público para a seleção de as |  |
| `83b1ac3d9e82bc828c5b` | encerrada | Credenciamento de organizações da sociedade civil, com sede em Farroupilha/RS, interessada |  |
| `898d930ce5601d1616e3` | encerrada | ABERTURA DE EDITAL DE CHAMAMENTO PÚBLICO LEI 13.019/2014, PARA CELEBRAÇÃO DE PARCERIA COM  |  |
| `8a087eb42abe7a9cadac` | encerrada | Objeto: Seleção de projetos apresentados por organizações da sociedade civil (OSC) para ex |  |
| `8de3468c73e21f339b92` | encerrada | Credenciamento de organizações da sociedade civil, para fins de habilitação prévia e compo |  |
| `8f2b345468262e913bff` | encerrada | CREDENCIAMENTO PRÉVIO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL OSCS PARA O ESTABELECIMENTO DE PA |  |
| `927812b31bac98bfee40` | encerrada | O presente credenciamento tem o objetivo de permitir que todo interessado que preencha os  |  |
| `92c21c1e8670fffb0d05` | encerrada | CREDENCIAMENTO PARA FINS DE CELEBRAÇÃO DE TERMO DE COLABORAÇÃO, COM DURAÇÃO CERTA, EM REGI |  |
| `93433ccdd865b20f832b` | encerrada | Contratação de profissional especializado em serviço de profissional de nível superior na  |  |
| `947fe159cbb672558135` | encerrada | CHAMAMENTO PÚBLICO POR CREDENCIAMENTO PARA PREMIAÇÃO DE AGENTE CULTURAL, ATIVIDADES OU AÇÕ |  |
| `95ca296b9b2eb1502b2f` | encerrada | Seleção de Organização da Sociedade Civil mediante a formalização de Termo de Colaboração, |  |
| `98adb3ec8fb15b79c169` | encerrada | Chamada Pública para credenciamento de cooperativas de catadores de materiais recicláveis, |  |
| `98ea4aea93be9ea8d3c1` | encerrada | Chamamento Público para Credenciamento de Instituição 
Sem Fins Lucrativos para Apoio à Fi |  |
| `a26f47ec4bb812e7c2b1` | encerrada | Credenciamento de pessoas jurídicas de direito privado, com preferência às entidades filan |  |
| `a44774f99276c7b58d0a` | encerrada | CREDENCIAMENTO DE PESSOAS JURÍDICAS SEM FINS LUCRATIVOS PARA AMPLIAÇÃO REGULAR E CONTINUAD |  |
| `a500abb89cb4cab26e41` | encerrada | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSCS) PARA CREDENCIAME |  |
| `a8d4a669e256d81e9e43` | encerrada | credenciamento de instituições reconhecidas como Organizações da Sociedade Civil (OSC) jun |  |
| `ae150797cb8ff2c5fa0f` | encerrada | Chamamento público na modalidade de chancela para seleção de proposta visando à celebração |  |
| `af36808be886e8cc826f` | encerrada | CREDENCIAMENTO DE INSTITUIÇÕES PRIVADAS, COM OU SEM FINS LUCRATIVOS, PRESTADORAS DE SERVIÇ |  |
| `b30e68d141accc6e1d27` | encerrada | Seleção de Organizações da Sociedade Civil que executem Serviços para auxílio estudantil à |  |
| `b618e2a14345d1661228` | encerrada | Constitui objeto do presente Edital, o Credenciamento de pessoas jurídicas de direito priv |  |
| `b8c90c7a8928773bd959` | encerrada | Chamamento Publico para selecao de uma  01  Organizacao da Sociedade Civil  OSC  para o se |  |
| `ba3fdfb0c88991036c09` | encerrada | Concessão de premiação e contratação de propostas artísticas de Artes Visuais Urbanas, com |  |
| `bf76e91037c86c00bc00` | encerrada | CREDENCIAMENTO DE PROJETOS CULTURAIS DO AUDIOVISUAL, PARA RECEBEREM APOIO FINANCEIRO NAS C |  |
| `c3bd65eb244f7217efa3` | encerrada | CREDENCIAMENTO DE PESSOA(S) JURÍDICA(S) SEM FINS LUCRATIVOS INTERESSADA(S) EM EXECUTAR SER |  |
| `ccc296e9e783767e56b2` | encerrada | ORGANIZAÇÕES DA SOCIEDADE CIVIL SEM FINS LUCRATIVOS PARA EVENTUAL CELEBRAÇÃO DE TERMO DE C |  |
| `ced063d82912665631c2` | encerrada | Formalização de parceria, mediante Termo de Colaboração, com Organização da Sociedade Civi |  |
| `cf6049e43af73106fb8b` | encerrada | O presente objeto constitui-se em  concurso para  seleção de 14 (quatorze) projetos cultur |  |
| `cfd881f2b0593c78f803` | encerrada | Contratação por meio de Credenciamento de instituição privada (com ou sem fins lucrativos) |  |
| `d231d9c66de43682d22a` | encerrada | Credenciamento de projetos culturais - PNAB |  |
| `d2dfb98c5cd7d2f18302` | encerrada | CREDENCIAMENTO DE INSTITUIÇÕES PRIVADAS, COM OU SEM FINS LUCRATIVOS, PRESTADORAS DE SERVIÇ |  |
| `d3030fab3b9dc994dd70` | encerrada | CELEBRAÇÃO DE TERMO DE FOMENTO QUE TEM POR OBJETO REPAS
SE FINANCEIRO A ASSOCIAÇÃO BENEFIC |  |
| `d6ff07772a8525e4a45c` | encerrada | EDITAL DE CHAMAMENTO PÚBLICO N. 116/2024, PARA SELEÇÃO DE ESPAÇOS, AMBIENTES E INICIATIVAS |  |
| `d8f8b8f285ea9736728b` | encerrada | CHAMAMENTO PUBLICO PARA CREDENCIAMENTO DE PESSOA FISICA OU JURIDICA COM OU SEM FINS LUCRAT |  |
| `e06d3756df5fe308fc57` | encerrada | Dispõe sobre a realização de Credenciamento de pessoas jurídicas de direito privado, sem f |  |
| `e080181a9a109e669934` | encerrada | Edital a seleção de Entidades Educacionais, sem fins lucrativos, para formalizar Termo de  |  |
| `e177587a928805d87bee` | encerrada | CRIAÇÃO DE CHAMAMENTO PÚBLICO PARA PESSOAS JURÍDICAS, COM OU SEM FINS LUCRATIVOS (LIVREIRO |  |
| `e20d48e682fda70ed030` | encerrada | seleção de Propostas apresentadas pelas Organizações da Sociedade Civil de Alagoinhas, par |  |
| `e59147d5c5bbf24f3208` | encerrada | O presente Termo de Referência tem por objeto fundamentar e orientar a execução do Edital  |  |
| `e898545160e5981ad4f9` | encerrada | Seleção de Organizações da Sociedade Civil que executem Serviços na área de atuação na rad |  |
| `ea7eed21a60d0d9475be` | encerrada | Chamamento Público para CREDENCIAMENTO de entidades de utilidade pública sem fins lucrativ |  |
| `eaa12d99fc473fb7ac68` | encerrada | SELEÇÃO DE ENTIDADE DE DIREITO PRIVADO, SEM FINS LUCRATIVOS, QUALIFICADA COMO ORGANIZAÇÃO  |  |
| `ee4548fc647fefc6a2e1` | encerrada | Selecionar uma Organização da Sociedade Civil – OSC, regularmente constituída e com experi |  |
| `ef328b28ca2e1398da23` | encerrada | CREDENCIAMENTO VIA CHAMAMENTO PÚBLICO, DESTINADA À CONVOCAÇÃO DE ENTIDADES SEM FINS LUCRAT |  |
| `f09d7bec24306a331f41` | encerrada | Recurso do incremento temporário da Emenda MAC será destinado ao custeio de materiais de c |  |
| `f153027623609ed268f6` | encerrada | Credenciamento de entidades públicas, filantrópicas e/ou sem fins lucrativos e entidades p |  |
| `f1ca92b53138bf67e586` | encerrada | CHAMAMENTO PUBLICO PARA SELEÇÃO DE PROJETOS APRESENTADOS POR ORGANIZAÇÕES DA SOCIEDADE CIV |  |
| `f9f05ff87196cbface7e` | encerrada | Chamamento Público 007.2025 - Credenciamento de Serviços de Acolhimento Institucional de A |  |
| `fcb79d2f17ce07c67d21` | encerrada | Concurso de Projetos nº 002/2024 das Parcerias a serem firmadas com as Organizações da Soc |  |
| `2bef5397b19e4a9449e4` | encerrada | Seleção Pública de Projetos para Patrocínio Cultural nº 01/2025 - Projetos Audiovisuais de |  |
| `d7105e41bd5331e8443e` | encerrada | Edital Fundo do Idoso 
             Veja as regras do edital do BNDES para apoiar projetos |  |
| `6f4db80af126d4259d2e` | encerrada | Ler Mais Sobre24/09/2025 – Inscrições abertas para apresentação de projetos ao amparo dos  |  |
| `37628c4973db5bc6f11d` | encerrada | Ler Mais Sobre21/08/2025 - Chamada Pública para Apoio a Projetos Sociais com Amparo em Inc |  |
| `b9255e2b8ea8f4d45153` | encerrada | 11º edital anual de seleção pública de projetos |  |
| `004e7ce1fa17d4cd851c` | encerrada | 🔵 Fundo Positivo lança hoje o edital de seleção pública de projetos! Tema: Prevenção Combi |  |
| `bfc98b5b97b2d69e9156` | encerrada | Para quem é o edital? |  |
| `4d76ce5af9d05b8ea86a` | encerrada | Edital nº 001/2026 - Chamamento público para  registro de candidatura de Profissionais int |  |
| `35e078b3750706139127` | encerrada | QUEM PODE SE INSCREVER? |  |
| `1229a56cafe058007b03` | encerrada | SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL – OSC, SEM FINS LUCRATIVOS,
REGULARMENTE CONSTI |  |
| `2e216c29f9b5444501ba` | encerrada | EDITAL DE CHAMAMENTO PÚBLICO DA PNAB COLÍDER/MT Nº 01/2024 
SELEÇÃO DE PROJETOS PARA FIRMA |  |
| `3bf5ffe3d0da406d895f` | encerrada | SELEÇÃO PÚBLICA E O CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL PARA FINS DE CELEBRA |  |
| `4c15d746b94be0c7f647` | encerrada | credenciamento de instituição especializada, preferencialmente Organização da Sociedade Ci |  |
| `5b2002af84d7311550c8` | encerrada | Concurso para  seleção de 14 (quatorze) projetos culturais nas Categorias Eventos (realiza |  |
| `6110c2223fa6ce0f8e0e` | encerrada | [Portal de Compras Públicas] - Chamamento Público destinado à seleção de Organizações da S |  |
| `97e10cdefb4a772fb529` | encerrada | [Portal de Compras Públicas] - Chamamento Público destinado à seleção de Organizações da S |  |
| `a36ee8a76017ea615080` | encerrada | EDITAL 04 - FOMENTO E PREMIAÇÃO PARA AGENTES CULTURAIS DO MUNICÍPIO, COM RECURSOS DO GOVER |  |
| `b755253db7c120e34580` | encerrada | [Portal de Compras Públicas] - Chamamento Público destinado à seleção de Organizações da S |  |
| `c017e9d77579ac18ec79` | encerrada | [Portal de Compras Públicas] - CREDENCIAMENTO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL OU ORGANIZ |  |
| `ebc55c857ceb4b7c6d91` | encerrada | SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL  - OSC, SEM FINS LUCRATIVOS, REGULARMENTE CONSTI |  |
| `841e718b859d6dc7e59a` | encerrada | CREDENCIAMENTO DE ENTIDADES PUBLICAS, FILANTRÓPICAS E/OU SEM FINS LUCRATIVOS E ENTIDADES P |  |
| `217ba2edfd96404374b3` | encerrada | Constitui objeto do presente Chamamento Público selecionar e premiar 40 (quarenta) ações d |  |
| `2c9fe5e7033bfb872af7` | encerrada | CHAMAMENTO PÚBLICO PARA O CREDENCIAMENTO DE ENTIDADES COMUNITÁRIAS, SEM FINS LUCRATIVOS/EC |  |
| `5865b8b689804b8e557e` | encerrada | Seleção de entidade de direito privado, sem fins lucrativos, qualificada como Organização  |  |
| `a83a765314a02716d983` | encerrada | [LICITANET] - Credenciamento de seleção e apoio financeiro às Quadrilhas Juninas para os F |  |
| `30ec946c0da038e039cc` | encerrada | CHAMAMENTO PÚBLICO PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO CUJO OBJETO É A CONCESSÃO DOS S |  |
| `d2145e5e31fa77187780` | encerrada | Seleção de Projetos das Organizações da Sociedade Civil |  |
| `596e7daa5e97ac628e9e` | fora_perfil | SECRETARIA MUNICIPAL DE EDUCACAO — Contratação, pelo PODER CONCEDENTE, representado pela S |  |
| `b0984d0a767b7ae674dc` | fora_perfil | DEFENSORIA PUBLICA DO ESTADO — Concurso de artigos para publicação na 2ª edição da Revista |  |
| `16872582ce529dbad93a` | fora_perfil | MUNICIPIO DE CAMPINA DA LAGOA — Chamamento Público de Instituições/Associações Estudantis  |  |
| `5e943a6e40ebbd9e14bf` | fora_perfil | MUNICIPIO DE NOVA PALMEIRA — Credenciamento de facilitadores, profissionais e assessoria t |  |
| `89cf211a1e1ff0429e77` | fora_perfil | Campus Mobile abre inscrições com viagem ao Vale do Silício entre os prêmios |  |
| `ec04d6d543d2adfd50aa` | fora_perfil | Prefeitura Municipal de Itapetininga AVISO DE CHAMAMENTO PÚBLICO Nº 11/2026 até  22/10 |  |
| `94f7eb69f4d3ba60e04d` | fora_perfil | Festival Ubuntu abre edital para selecionar 21 artistas e projetos culturais |  |
| `575706d9ad755cd36a5d` | ruido | EXTRATO DE TERMO DE FOMENTO Nº 997181/2026 |  |
| `9107398972ccec107a35` | ruido | EDITAL DE INTIMAÇÃO |  |
| `ca24a73387bc378e278a` | ruido | EXTRATO DE TERMO DE FOMENTO |  |
| `647bacd91908be74d5ff` | ruido | EXTRATO DE TERMO DE FOMENTO |  |
| `dad0d1baa214f9ba880a` | ruido | EXTRATO DE TERMO DE FOMENTO |  |
| `15de137a3b958a197005` | ruido | Consulta de Emendas Parlamentares |  |
| `54da845f173c87b1cb6e` | ruido | Consulta de Emendas Parlamentares |  |
| `f67a347288a288133839` | ruido | ﻿O Fundo Nacional do Meio Ambiente torna público em 21/09/2026, o resultado preliminar do  |  |
| `07b51af34420730537e7` | ruido | Cartilhas e Emendas Parlamentares |  |
| `80e9325986e27ee93e8f` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA |  |
| `c51a214fd5e7a1afd668` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA |  |
| `1605e8fcffe87410b7d3` | ruido | Organizações da Sociedade Civil |  |
| `2360340f6a39b77ecd77` | ruido | Organizações da Sociedade Civil |  |
| `196514ae3146c661d6b1` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA |  |
| `7f38f074dd3050937b4d` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA |  |
| `9910e0c5d4d7c9347422` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA Nº 7 /2026 |  |
| `aada3c74210262b72f9d` | ruido | EXTRATO DE ACORDO DE COOPERAÇÃO TÉCNICA Nº 1.2026/AGEDOCE |  |
| `1147574ff00c17dc58ef` | ruido | Engajamento, agentes de mudança e governança climática |  |
| `4d519a11c8b5c23bd8d5` | ruido | Termo de Fomento nº 01/2026 |  |
| `8100f6629766a09260b5` | ruido | Acesse a lista de projetos inscritos no edital, divulgada em 30.09.2026 (PDF - 52 kB) |  |
| `fc56fb286d328265dc1b` | ruido | Programas de fomento |  |
| `4529a1455793c5ca85cd` | ruido | I Encontro Nacional com as Organizações da Sociedade Civil (OSC’s) apoiadas pelo 19º Edita |  |
| `f5cb0dda754097e74f36` | ruido | É com muita satisfação e muita alegria que nós comunicamos e visibilizamos os projetos apo |  |
| `5e9a2d872539d330d387` | ruido | COMUNICADO DE CANCELAMENTO DE EDITAL |  |
| `995b293835374e0bffc0` | ruido | Fundo Positivo divulga os 15 projetos escolhidos no 8º edital de seleção |  |
| `db228097c0550283cb97` | ruido | I° Encontro Nacional com as Organizações da Sociedade Civil (OSC’s) apoiadas pelo 17º Edit |  |
| `edaf5301f1587346f3aa` | ruido | Quero me inscrever |  |
| `e4537d5a296d5fdd1747` | ruido | Prêmio Alimentação em Foco |  |
| `5c213e8efa9ee33649f7` | ruido | Chamamento Público |  |
| `5de6fd8eea555fc16b48` | ruido | PORTAL LICITA CARIRÉ |  |
| `aa1915a7e0a5373291a2` | ruido | SALA DO EMPREENDEDOR - ITABAIANINHA |  |
| `aa9db373dd52bb032a8c` | ruido | Prefeitura de Cariré divulga resultado final do edital Cariré Criativo |  |

## Conselho de 7 lentes

- **Extremamente pessimista:** a maior parte dos itens do PNCP foi localizada por busca de termos; mesmo com o controle de qualidade, um trecho pode estar no edital certo mas na cláusula errada. Credenciamentos em que a data de encerramento do PNCP é igual à de abertura podem ser permanentes e terem sido marcados como encerrados.
- **Pessimista:** 117 oportunidades que o sistema dava como abertas ou possíveis já estão encerradas — o motor está deixando passar processos antigos (2023–2025). DOU segue fora por robots.txt; arquivos com erro HTTP 422 no PNCP e PDFs escaneados ficaram sem leitura.
- **Levemente pessimista:** território e destinação raramente aparecem como regra expressa; quando ausentes, o território foi o município/UF do registro oficial, o que não prova restrição.
- **Neutro (decisão):** aplicar o arquivo. Parâmetros de qualidade: (1) ouro só com 12 itens obtidos/dispensados, cada um com trecho + documento + página, site oficial e prazo vigente; (2) item sem prova = não disponível com motivo; (3) encerrada só com data oficial anterior a hoje; (4) agregador nunca é fonte. Mitigações: conferir manualmente os ouros antes de inscrever (feito nesta rodada), revisar por amostra 10% das pratas, e reabrir os credenciamentos com encerramento igual à abertura. Correções feitas antes de entregar: descartados trechos de valor de fornecedor, finalidade fora de contexto, cláusula de recurso intempestivo ou 'não caberá mais recurso' tratada como dispensa, prazo de contrarrazões tomado como prazo de recurso, modelo de assinatura tratado como território e certidões antigas do Cartório sem relação com o item; o selo final foi recalculado pelo critério oficial (src/criterio_selos.py) e o ouro caiu de 49 para 5.
- **Levemente otimista:** 295 de 295 com veredito, documento e parecer; nada pendente.
- **Otimista:** a lista de janelas vigentes acima é acionável hoje, com prazo, valor e documento oficial.
- **Extremamente otimista:** o extrator do PNCP (API + pdf.js no navegador) pode virar motor permanente e fechar as próximas rodadas sem trabalho manual.

## Limites

Sem login, sem CAPTCHA, sem formulário; robots.txt respeitado (DOU). PNCP com HTTP 422 em alguns arquivos e 429 em rajadas. Nenhum texto dirigido a IA foi seguido; um site (ANATER) tinha propaganda de apostas inserida, registrada em alertas.