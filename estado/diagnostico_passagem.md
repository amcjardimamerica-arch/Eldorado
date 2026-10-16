# Diagnóstico do sistema · 2026-10-16 13:04 UTC

## Cumprimento da finalidade · índice geral 66%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 82% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 17% (falha) — toda oportunidade aberta validada
- Site oficial: 72% (atencao) — toda aberta com site oficial
- Prazo: 27% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 69% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 1, 'ok': 31, 'atencao': 8, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-16T12:19 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-15T15:14 · sucesso 12% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: atencao · última 2026-10-16T13:03 · sucesso 67% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-16T10:47 · sucesso 10% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-16T12:04 · sucesso 22% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-16T11:39 · sucesso 60% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-16T11:10 · sucesso 50% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 399 · validadas: 66 (16.5%) · por estado: {'em_verificacao': 326, 'validada': 66, 'validacao_manual': 7}
- com livro: 382 · sem livro (problema): 1 · sem livro por regra: 16 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 14, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 1, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 1} · livro inexistente: 0
- sem site oficial: 111 · sem prazo: 291 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 293, 'Anexos': 266, 'Resultado': 248, 'Prazo de inscrição': 236, 'Requisitos': 232, 'Valor': 231, 'Objeto': 194, 'Território': 186, 'Destinação': 158, 'Órgão / financiador': 118, 'Esfera': 115, 'Área de atuação': 108}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 82.0% · esgotados 12
- rede neural: AUC 0.843 · rotulados 1680 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6944 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 7 alerta(s) · índice da sala de controle: 90

## Integração
- contagens: {'repositorio_abertas': 399, 'diagnostico_abertas': 399, 'tela_cartoes': 420, 'fichas': 405, 'sala_controle_abertas': 399}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.6, 'maestro': 0.6, 'rede_neural': 0.0, 'saude': 1.1}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (21)
- [alta] 4 etapa(s) com erro nos ciclos de hoje: catalogar: catalogar:3: TypeError: 'int' object is not subscriptable | catalogar: catalogar:3: TypeError: 'int' object is not subscriptable | pncp: pncp:1: código 124 → investigar a etapa (sem correção automática)
- [alta] [qualificar] oportunidades abertas para associação: 1 de 399 contrariam a regra — pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) → rever o veredito (sem correção automática)
- [alta] 10 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 1 de 399 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] tela mostra 420 oportunidades e o repositório conta 399 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 313.1 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 362.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 215 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 25 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1211 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em GO, __nac__, BA, SP, SC → refazer tela e indicadores
- [media] saúde · mapa: 1 oportunidade(s) no mapa sem decisão (curadoria) → ver o fluxo/arquivo indicado
- [media] saúde · opressores: 7 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 111 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 291 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 7 ciclo(s) hoje · 4 vermelho(s) · 4 etapa(s) com erro · fases puladas {'treinar_rede': 7, 'expurgo': 6, 'biblioteca_diaria': 6, 'vigilancia_diaria': 6}
- cobertura do dia: 82.0% de 128 motores
- retentativa: {'aguardando_retentativa': 573, 'fora_da_fila': 25, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-6': 3, 'f260-captacao-240': 1, 'recorrencia': 3, 'outras-oportunidades-5': 2, 'outras-oportunidades-8': 3, 'f260-captacao-228': 1, 'f260-espalhado-rouanet-cultura-gov-br': 1, 'f260-curadoria-005': 1, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'outras-oportunidades-7': 2, 'f260-captacao-118': 1, 'plat-empresas-editais-incentivados': 2}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 476
- curadoria do link oficial: {'em curadoria': 243, 'reprovado': 79, 'aprovado': 44, 'sem link oficial': 38}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-16T13:03:59+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 128) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **incorreto** (1 de 399) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar) · ex.: op-op-cf55833374d2: Aviso de Chamamento Público Nº 1/2026 — Goiás
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 399) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 399) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 288) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2399) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 13) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 2193) — regra: ato legislativo não gera livro
