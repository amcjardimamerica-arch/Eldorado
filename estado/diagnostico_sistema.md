# Diagnóstico do sistema · 2026-10-15 12:13 UTC

## Cumprimento da finalidade · índice geral 60%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 0% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 9% (falha) — toda oportunidade aberta validada
- Site oficial: 80% (atencao) — toda aberta com site oficial
- Prazo: 26% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 65% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 4, 'ok': 32, 'atencao': 4, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-15T12:07 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-15T11:59 · sucesso 75% · cadência None h
- 05 · Busca ativa (a cada 3 dias): falha · última 2026-10-03T02:26 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: falha · última 2026-09-27T05:46 · sucesso 0% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-15T10:59 · sucesso 0% · cadência 24.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-15T11:42 · sucesso 50% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T10:38 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: [] | - [alta] 12 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: [] | - [alta]  | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 7 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Páginas aguardando nova tentativa', 'Páginas fora da fila (5 erros iguais)', 'Links oficiais aprovados na curadoria', 'Alimentação externa diária']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 514 · validadas: 47 (9.1%) · por estado: {'em_verificacao': 460, 'validada': 47, 'validacao_manual': 7}
- com livro: 398 · sem livro (problema): 0 · sem livro por regra: 116 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 88, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 22, 'fora da abrangência: municipal de outro estado (PE) que não é capital — só Goiás tem munic': 2, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 2, 'fora da abrangência: municipal de outro estado (BA) que não é capital — só Goiás tem munic': 1, 'fora da abrangência: municipal de outro estado (SP) que não é capital — só Goiás tem munic': 1} · livro inexistente: 0
- sem site oficial: 105 · sem prazo: 381 · prazo vencido ainda aberta: 0
- fora da tela: 1 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 448, 'Resultado': 433, 'Prazo de inscrição': 422, 'Valor': 417, 'Anexos': 394, 'Requisitos': 391, 'Destinação': 359, 'Área de atuação': 357, 'Território': 318, 'Objeto': 307, 'Órgão / financiador': 296, 'Esfera': 293}

## Sistemas
- motores: 42 funcionando · 0 em falha · 3 inativos · 1 com leitura parcial
- maestro: cobertura 0.0% · esgotados 0
- rede neural: AUC 0.843 · rotulados 2027 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 7 alerta(s) · índice da sala de controle: 87

## Integração
- contagens: {'repositorio_abertas': 514, 'diagnostico_abertas': 514, 'tela_cartoes': 513, 'fichas': 524, 'sala_controle_abertas': 514}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.1, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.0, 'maestro': 4.3, 'rede_neural': 0.2, 'saude': 0.1}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (25)
- [alta] o comando único ainda não gravou recibo (docs/dados/comando.json) → investigar o fluxo 22 (sem correção automática)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 12 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: [] | - [alta] 12 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: [] | - [alta]  | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 1 abertas no repositório que não aparecem na tela de oportunidades → refazer a tela
- [alta] 4 oportunidades municipais de outros estados ainda abertas (só Goiás tem municipais) → refazer o repositório
- [alta] tela mostra 513 oportunidades e o repositório conta 514 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] maestro sem atualização há 4.3 h (limite 3 h) → ver o fluxo que gera este dado
- [media] [site_oficial] link oficial gravado no repositório: 4 de 409 contrariam a regra — agregador ou replicador nunca é link oficial → buscar a fonte oficial (resolvedor e Cartório)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 288.3 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 337.6 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] saúde · claude: 1354 item(ns) esperando a análise do Claude (próxima: 2026-10-15) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em SC, GO, __nac__, BA, SP → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 105 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 381 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 0 ciclo(s) hoje · None vermelho(s) · 0 etapa(s) com erro · fases puladas {}
- cobertura do dia: 0.0% de 121 motores
- retentativa: {'aguardando_retentativa': 0, 'fora_da_fila': 0} · leitura parcial na fila: 0
- curadoria do link oficial: {}
- validação por exceção: None
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T02:12:35+00:00', 'acerto_pct': 66.1, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 6}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-15T10:17:22+00:00', 'proposicoes': 8}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **não conferido (sem registro desta etapa ainda)** (0 de 0) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 514) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 514) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 514) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **incorreto** (4 de 409) — regra: agregador ou replicador nunca é link oficial · ex.: fa359a0aafb11debea10: https://editaisdobrasil.com/oportunidade/premio-nacional-de-inovacao; c37bbca075f562f5aeef: https://editaisdobrasil.com/oportunidades
- certificar · itens certificados pelo Cartório: **correto** (0 de 2645) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 40) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1905) — regra: ato legislativo não gera livro
