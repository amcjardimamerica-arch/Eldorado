# Diagnóstico do sistema · 2026-10-15 21:51 UTC

## Cumprimento da finalidade · índice geral 73%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 71% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 11% (falha) — toda oportunidade aberta validada
- Site oficial: 75% (atencao) — toda aberta com site oficial
- Prazo: 25% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 68% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 60% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 100% (ok) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'ok': 32, 'atencao': 7, 'atrasado': 3, 'manual': 2}
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-15T15:14 · sucesso 12% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-15T10:59 · sucesso 0% · cadência 24.0 h
- 16 · Motores indexadores (feeds, APIs, sitemaps, listagens, dados abertos, ponte Brasil, coleta assistida): atrasado · última 2026-10-15T04:32 · sucesso 100% · cadência 3.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-15T20:08 · sucesso 70% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-15T11:42 · sucesso 50% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T10:38 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 391 · validadas: 42 (10.7%) · por estado: {'em_verificacao': 342, 'validada': 42, 'validacao_manual': 7}
- com livro: 373 · sem livro (problema): 0 · sem livro por regra: 18 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 16, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 1, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 1} · livro inexistente: 0
- sem site oficial: 97 · sem prazo: 292 · prazo vencido ainda aberta: 0
- fora da tela: 1 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 334, 'Resultado': 325, 'Prazo de inscrição': 318, 'Valor': 310, 'Anexos': 296, 'Requisitos': 289, 'Destinação': 273, 'Área de atuação': 273, 'Território': 238, 'Objeto': 233, 'Órgão / financiador': 222, 'Esfera': 218}

## Sistemas
- motores: 44 funcionando · 0 em falha · 1 inativos · 5 com leitura parcial
- maestro: cobertura 71.3% · esgotados 37
- rede neural: AUC 0.843 · rotulados 2057 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6827 certificado · fluxos do GitHub com falha: []
- saúde: 2 alerta(s) · índice da sala de controle: 79

## Integração
- contagens: {'repositorio_abertas': 391, 'diagnostico_abertas': 391, 'tela_cartoes': 394, 'fichas': 397, 'sala_controle_abertas': 391}
- idade (h): {'repositorio': 0.0, 'fluxo': 1.2, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.0, 'maestro': 1.7, 'rede_neural': 1.2, 'saude': 3.2}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (11)
- [alta] 1 abertas no repositório que não aparecem na tela de oportunidades → refazer a tela
- [alta] tela mostra 394 oportunidades e o repositório conta 391 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 297.9 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '16 · Motores indexadores (feeds, APIs, sitemaps, listagens, dados abertos, ponte Brasil, coleta assistida)' sem rodar há 17.3 h (cadência 3.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 347.2 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] saúde · claude: 1357 item(ns) esperando a análise do Claude (próxima: 2026-10-15) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em SC, GO, __nac__, BA, SP → refazer tela e indicadores
- [media] 97 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 292 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 8 ciclo(s) hoje · 0 vermelho(s) · 0 etapa(s) com erro · fases puladas {'treinar_rede': 8, 'biblioteca_diaria': 8}
- cobertura do dia: 71.3% de 129 motores
- retentativa: {'aguardando_retentativa': 266, 'fora_da_fila': 0, 'fora_da_fila_por_escopo': {}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 157
- curadoria do link oficial: {'em curadoria': 404, 'sem link oficial': 202, 'aprovado': 17, 'reprovado': 80}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 6}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-15T20:38:31+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 129) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 391) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 391) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 391) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 294) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2817) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 10) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1952) — regra: ato legislativo não gera livro
