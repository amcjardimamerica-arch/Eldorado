# Diagnóstico do sistema · 2026-10-16 22:08 UTC

## Cumprimento da finalidade · índice geral 68%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 86% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 15% (falha) — toda oportunidade aberta validada
- Site oficial: 73% (atencao) — toda aberta com site oficial
- Prazo: 23% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 30% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 2, 'ok': 31, 'atencao': 7, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-16T20:11 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-16T14:17 · sucesso 22% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: falha · última 2026-10-16T20:11 · sucesso 20% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-16T13:37 · sucesso 20% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-16T20:32 · sucesso 33% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-16T11:39 · sucesso 60% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-16T16:29 · sucesso 50% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motor-agregadores.yml: mapa: falhou
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in

## Sala de controle · 30 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 402 · validadas: 59 (14.7%) · por estado: {'em_verificacao': 338, 'validada': 59, 'validacao_manual': 5}
- com livro: 392 · sem livro (problema): 0 · sem livro por regra: 10 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 10} · livro inexistente: 0
- sem site oficial: 110 · sem prazo: 310 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 300, 'Anexos': 298, 'Requisitos': 255, 'Resultado': 253, 'Objeto': 245, 'Território': 244, 'Valor': 240, 'Prazo de inscrição': 238, 'Modalidade': 183, 'Órgão / financiador': 153, 'Esfera': 147, 'Área de atuação': 133}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 85.5% · esgotados 19
- rede neural: AUC 0.843 · rotulados 1689 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.7008 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão', '12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos']
- saúde: 5 alerta(s) · índice da sala de controle: 85

## Integração
- contagens: {'repositorio_abertas': 402, 'diagnostico_abertas': 402, 'tela_cartoes': 410, 'fichas': 405, 'sala_controle_abertas': 402}
- idade (h): {'repositorio': 0.5, 'fluxo': 0.5, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.7, 'maestro': 0.7, 'rede_neural': 0.5, 'saude': 8.3}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (21)
- [alta] 9 etapa(s) com erro nos ciclos de hoje: catalogar: catalogar:3: TypeError: 'int' object is not subscriptable | catalogar: catalogar:3: TypeError: 'int' object is not subscriptable | pncp: pncp:1: código 124 → investigar a etapa (sem correção automática)
- [alta] [qualificar] oportunidades abertas para associação: 1 de 402 contrariam a regra — pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) → rever o veredito (sem correção automática)
- [alta] 1 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: mapa: falhou → investigar a etapa (sem correção automática)
- [alta] 6 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos' falhou nas últimas execuções (20% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] tela mostra 410 oportunidades e o repositório conta 402 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 322.2 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 371.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 7 oportunidade(s) usam o link de acesso como oficial sem serem fonte oficial → buscar a fonte oficial (resolvedor e Cartório)
- [media] 53 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 36 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1180 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, GO, SC, SP, MG → refazer tela e indicadores
- [media] saúde · opressores: 1 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 110 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 310 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 18 ciclo(s) hoje · 9 vermelho(s) · 9 etapa(s) com erro · fases puladas {'treinar_rede': 18, 'expurgo': 16, 'biblioteca_diaria': 17, 'vigilancia_diaria': 17, 'migracao_livros': 9, 'modalidade': 5, 'unir_livros': 1}
- cobertura do dia: 85.5% de 131 motores
- retentativa: {'aguardando_retentativa': 680, 'fora_da_fila': 36, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-6': 3, 'f260-captacao-240': 1, 'recorrencia': 3, 'outras-oportunidades-5': 2, 'outras-oportunidades-8': 3, 'f260-captacao-228': 1, 'f260-espalhado-rouanet-cultura-gov-br': 1, 'f260-curadoria-005': 1, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'outras-oportunidades-7': 2, 'f260-captacao-118': 1, 'plat-empresas-editais-incentivados': 2, 'f260-captacao-221': 2, 'f260-captacao-237': 1, 'f260-captacao-238': 1, 'cartorio': 7}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 566
- curadoria do link oficial: {'em curadoria': 236, 'aprovado': 48, 'reprovado': 75, 'sem link oficial': 43}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-16T22:07:46+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 131) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **incorreto** (1 de 402) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) · ex.: op-op-cf55833374d2: Aviso de Chamamento Público Nº 1/2026 — Goiás
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 402) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 402) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 292) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2168) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 12) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1958) — regra: ato legislativo não gera livro
