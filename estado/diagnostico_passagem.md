# Diagnóstico do sistema · 2026-10-17 01:42 UTC

## Cumprimento da finalidade · índice geral 68%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 85% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 15% (falha) — toda oportunidade aberta validada
- Site oficial: 72% (atencao) — toda aberta com site oficial
- Prazo: 21% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 71% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 30% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 2, 'ok': 30, 'atencao': 8, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-17T01:42 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-16T14:17 · sucesso 22% · cadência 24.0 h
- 06 · Alimentação manual (arquivos e links do titular): atencao · última 2026-10-17T01:42 · sucesso 75% · cadência None h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: falha · última 2026-10-17T01:33 · sucesso 11% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-16T13:37 · sucesso 20% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-17T01:28 · sucesso 25% · cadência 1.0 h
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
- abertas: 397 · validadas: 61 (15.4%) · por estado: {'em_verificacao': 331, 'validada': 61, 'validacao_manual': 5}
- com livro: 389 · sem livro (problema): 0 · sem livro por regra: 8 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 8} · livro inexistente: 0
- sem site oficial: 111 · sem prazo: 313 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 289, 'Anexos': 288, 'Resultado': 234, 'Requisitos': 231, 'Objeto': 230, 'Território': 223, 'Valor': 220, 'Prazo de inscrição': 213, 'Modalidade': 147, 'Órgão / financiador': 110, 'Esfera': 107, 'Área de atuação': 89}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 85.0% · esgotados 19
- rede neural: AUC 0.843 · rotulados 1690 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.71 certificado · fluxos do GitHub com falha: []
- saúde: 5 alerta(s) · índice da sala de controle: 84

## Integração
- contagens: {'repositorio_abertas': 397, 'diagnostico_abertas': 397, 'tela_cartoes': 400, 'fichas': 409, 'sala_controle_abertas': 397}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.6, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.7, 'maestro': 0.7, 'rede_neural': 0.5, 'saude': 11.9}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (19)
- [alta] [qualificar] oportunidades abertas para associação: 1 de 397 contrariam a regra — pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) → rever o veredito (sem correção automática)
- [alta] 1 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: mapa: falhou → investigar a etapa (sem correção automática)
- [alta] 6 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos' falhou nas últimas execuções (11% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] tela mostra 400 oportunidades e o repositório conta 397 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 325.8 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 375.1 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 57 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 37 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1180 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, GO, SC, SP, MG → refazer tela e indicadores
- [media] saúde · opressores: 1 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 111 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 313 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 0 ciclo(s) hoje · 11 vermelho(s) · 0 etapa(s) com erro · fases puladas {}
- cobertura do dia: 85.0% de 127 motores
- retentativa: {'aguardando_retentativa': 710, 'fora_da_fila': 37, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-6': 3, 'f260-captacao-240': 1, 'recorrencia': 3, 'outras-oportunidades-5': 2, 'outras-oportunidades-8': 3, 'f260-captacao-228': 1, 'f260-espalhado-rouanet-cultura-gov-br': 1, 'f260-curadoria-005': 1, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'outras-oportunidades-7': 2, 'f260-captacao-118': 1, 'plat-empresas-editais-incentivados': 2, 'f260-captacao-221': 2, 'f260-captacao-237': 1, 'f260-captacao-238': 1, 'cartorio': 8}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 596
- curadoria do link oficial: {'aprovado': 47, 'em curadoria': 245, 'reprovado': 73, 'sem link oficial': 41}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-17T01:42:17+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 127) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **incorreto** (1 de 397) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) · ex.: op-op-cf55833374d2: Aviso de Chamamento Público Nº 1/2026 — Goiás
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 397) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 397) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 286) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2158) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 11) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1960) — regra: ato legislativo não gera livro
