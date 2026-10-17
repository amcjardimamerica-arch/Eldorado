# Diagnóstico do sistema · 2026-10-17 00:08 UTC

## Cumprimento da finalidade · índice geral 68%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 86% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 98% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 15% (falha) — toda oportunidade aberta validada
- Site oficial: 71% (atencao) — toda aberta com site oficial
- Prazo: 23% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 30% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'atencao': 8, 'ok': 31, 'atrasado': 2, 'manual': 2, 'falha': 1}
- 00 · Verificar prontidão: atencao · última 2026-10-17T00:07 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-16T14:17 · sucesso 22% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: falha · última 2026-10-16T20:11 · sucesso 20% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-16T13:37 · sucesso 20% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-16T23:25 · sucesso 25% · cadência 1.0 h
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
- abertas: 397 · validadas: 59 (14.9%) · por estado: {'em_verificacao': 333, 'validada': 59, 'validacao_manual': 5}
- com livro: 377 · sem livro (problema): 7 · sem livro por regra: 13 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 13} · livro inexistente: 0
- sem site oficial: 114 · sem prazo: 307 · prazo vencido ainda aberta: 2
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Anexos': 289, 'Prazo de recurso': 288, 'Resultado': 239, 'Requisitos': 239, 'Objeto': 231, 'Território': 231, 'Valor': 227, 'Prazo de inscrição': 225, 'Modalidade': 160, 'Órgão / financiador': 129, 'Esfera': 123, 'Área de atuação': 107}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 85.5% · esgotados 19
- rede neural: AUC 0.843 · rotulados 1689 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.7044 certificado · fluxos do GitHub com falha: ['12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos']
- saúde: 5 alerta(s) · índice da sala de controle: 78

## Integração
- contagens: {'repositorio_abertas': 397, 'diagnostico_abertas': 397, 'tela_cartoes': 403, 'fichas': 400, 'sala_controle_abertas': 397}
- idade (h): {'repositorio': 0.5, 'fluxo': 0.5, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.7, 'maestro': 0.7, 'rede_neural': 3.4, 'saude': 10.4}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (24)
- [alta] o comando único não fecha um ciclo há 3.8 h (passa a cada 30 min) → investigar o fluxo 22 (sem correção automática)
- [alta] [farol] oportunidades prontas para o Farol: 1 de 13 contrariam a regra — pronta só com prazo vigente e link oficial aprovado na curadoria → rever a regra de prontidão (sem correção automática)
- [alta] [qualificar] oportunidades abertas para associação: 1 de 397 contrariam a regra — pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) → rever o veredito (sem correção automática)
- [alta] 1 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: mapa: falhou → investigar a etapa (sem correção automática)
- [alta] 6 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos' falhou nas últimas execuções (20% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 7 de 397 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] 2 oportunidades com prazo vencido ainda contadas como abertas → refazer o repositório
- [alta] tela mostra 403 oportunidades e o repositório conta 397 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] [prazo] oportunidades contadas como abertas: 2 de 397 contrariam a regra — prazo vencido sai das abertas → refazer o repositório
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 324.2 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 373.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 7 oportunidade(s) usam o link de acesso como oficial sem serem fonte oficial → buscar a fonte oficial (resolvedor e Cartório)
- [media] 17 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 36 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1180 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, GO, SC, SP, MG → refazer tela e indicadores
- [media] saúde · opressores: 1 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 114 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 307 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 0 ciclo(s) hoje · 9 vermelho(s) · 0 etapa(s) com erro · fases puladas {}
- cobertura do dia: 85.5% de 131 motores
- retentativa: {'aguardando_retentativa': 695, 'fora_da_fila': 36, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-6': 3, 'f260-captacao-240': 1, 'recorrencia': 3, 'outras-oportunidades-5': 2, 'outras-oportunidades-8': 3, 'f260-captacao-228': 1, 'f260-espalhado-rouanet-cultura-gov-br': 1, 'f260-curadoria-005': 1, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'outras-oportunidades-7': 2, 'f260-captacao-118': 1, 'plat-empresas-editais-incentivados': 2, 'f260-captacao-221': 2, 'f260-captacao-237': 1, 'f260-captacao-238': 1, 'cartorio': 7}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 581
- curadoria do link oficial: {'em curadoria': 235, 'aprovado': 46, 'reprovado': 78, 'sem link oficial': 38}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-17T00:08:11+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 131) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **incorreto** (1 de 397) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) · ex.: op-op-cf55833374d2: Aviso de Chamamento Público Nº 1/2026 — Goiás
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 397) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **incorreto** (2 de 397) — regra: prazo vencido sai das abertas · ex.: agr-f43c233385e2: fim 2026-10-16; 7a5b6e2eb4296c1398e4: fim 2026-10-16
- site_oficial · link oficial gravado no repositório: **correto** (0 de 283) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2143) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **incorreto** (1 de 13) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria · ex.: 7a5b6e2eb4296c1398e4: prazo vencido
- biblioteca · livros da Biblioteca: **correto** (0 de 1945) — regra: ato legislativo não gera livro
