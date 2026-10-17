# Diagnóstico do sistema · 2026-10-17 02:28 UTC

## Cumprimento da finalidade · índice geral 68%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 85% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 92% (atencao) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 65% (falha) — toda aberta com site oficial
- Prazo: 17% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 59% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 30% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 2, 'ok': 30, 'atencao': 8, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-17T02:06 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-16T14:17 · sucesso 22% · cadência 24.0 h
- 06 · Alimentação manual (arquivos e links do titular): atencao · última 2026-10-17T01:57 · sucesso 50% · cadência None h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: falha · última 2026-10-17T02:19 · sucesso 11% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-16T13:37 · sucesso 20% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-17T01:43 · sucesso 22% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-16T11:39 · sucesso 60% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-16T16:29 · sucesso 50% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motor-agregadores.yml: mapa: falhou
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in

## Sala de controle · 34 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Última importação do Chrome']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 407 · validadas: 42 (10.3%) · por estado: {'em_verificacao': 352, 'validada': 42, 'validacao_manual': 13}
- com livro: 360 · sem livro (problema): 32 · sem livro por regra: 15 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 15} · livro inexistente: 0
- sem site oficial: 143 · sem prazo: 336 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Anexos': 357, 'Prazo de recurso': 354, 'Território': 349, 'Requisitos': 349, 'Valor': 347, 'Resultado': 346, 'Modalidade': 343, 'Objeto': 340, 'Prazo de inscrição': 338, 'Esfera': 338, 'Área de atuação': 337, 'Órgão / financiador': 336}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 85.2% · esgotados 19
- rede neural: AUC 0.843 · rotulados 1692 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.5889 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 5 alerta(s) · índice da sala de controle: 86

## Integração
- contagens: {'repositorio_abertas': 407, 'diagnostico_abertas': 407, 'tela_cartoes': 407, 'fichas': 410, 'sala_controle_abertas': 407}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.8, 'maestro': 0.7, 'rede_neural': 0.0, 'saude': 12.7}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (18)
- [alta] 1 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: mapa: falhou → investigar a etapa (sem correção automática)
- [alta] 6 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos' falhou nas últimas execuções (11% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 32 de 407 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 326.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 375.9 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 60 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 22 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1180 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, GO, SC, SP, MG → refazer tela e indicadores
- [media] saúde · opressores: 1 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 143 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 336 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 0 ciclo(s) hoje · 12 vermelho(s) · 0 etapa(s) com erro · fases puladas {}
- cobertura do dia: 85.2% de 128 motores
- retentativa: {'aguardando_retentativa': 713, 'fora_da_fila': 22, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-6': 3, 'f260-captacao-240': 1, 'recorrencia': 3, 'outras-oportunidades-5': 2, 'outras-oportunidades-8': 3, 'f260-captacao-228': 1, 'f260-espalhado-rouanet-cultura-gov-br': 1, 'f260-curadoria-005': 1, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'outras-oportunidades-7': 2, 'f260-captacao-118': 1, 'plat-empresas-editais-incentivados': 2, 'f260-captacao-221': 2, 'f260-captacao-237': 1, 'f260-captacao-238': 1, 'cartorio': 9}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro', 'destinos': {'Claude no Chrome': 9, 'rota quebrada': 16, 'ponte ou Chrome': 13, 'sem destino': 0}} · leitura parcial na fila: 599
- curadoria do link oficial: {'aprovado': 19, 'em curadoria': 260, 'sem link oficial': 48, 'reprovado': 30}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-17T02:28:04+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 128) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 407) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 407) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 407) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 264) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 140) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 11) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1209) — regra: ato legislativo não gera livro
