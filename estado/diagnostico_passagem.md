# Diagnóstico do sistema · 2026-10-16 00:00 UTC

## Cumprimento da finalidade · índice geral 75%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 72% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 76% (atencao) — toda aberta com site oficial
- Prazo: 25% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 68% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 65% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 80% (atencao) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'ok': 33, 'atencao': 7, 'atrasado': 2, 'manual': 2}
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-15T15:14 · sucesso 12% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-15T10:59 · sucesso 0% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-15T23:32 · sucesso 38% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-15T11:42 · sucesso 50% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T10:38 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motor-agregadores.yml: "rede: robots.txt inacessível: URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)" | "rede: robots.txt inacessível: URLError: timed out",

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 396 · validadas: 41 (10.4%) · por estado: {'em_verificacao': 348, 'validada': 41, 'validacao_manual': 7}
- com livro: 378 · sem livro (problema): 0 · sem livro por regra: 18 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 16, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 1, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 1} · livro inexistente: 0
- sem site oficial: 97 · sem prazo: 298 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 340, 'Resultado': 331, 'Prazo de inscrição': 324, 'Valor': 316, 'Anexos': 302, 'Requisitos': 295, 'Destinação': 279, 'Área de atuação': 279, 'Território': 244, 'Objeto': 239, 'Órgão / financiador': 228, 'Esfera': 224}

## Sistemas
- motores: 44 funcionando · 0 em falha · 1 inativos · 5 com leitura parcial
- maestro: cobertura 71.7% · esgotados 0
- rede neural: AUC 0.843 · rotulados 2057 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6765 certificado · fluxos do GitHub com falha: []
- saúde: 2 alerta(s) · índice da sala de controle: 84

## Integração
- contagens: {'repositorio_abertas': 396, 'diagnostico_abertas': 396, 'tela_cartoes': 396, 'fichas': 402, 'sala_controle_abertas': 396}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.5, 'maestro': 0.5, 'rede_neural': 0.0, 'saude': 5.3}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (11)
- [alta] 2 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: "rede: robots.txt inacessível: URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)" | "rede: robots.txt inacessível: URLError: timed out", → investigar a etapa (sem correção automática)
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] [prazo] oportunidades contadas como abertas: 2 de 396 contrariam a regra — prazo vencido sai das abertas → refazer o repositório
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 300.1 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 349.4 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 4 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1357 item(ns) esperando a análise do Claude (próxima: 2026-10-15) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em SC, GO, __nac__, BA, SP → refazer tela e indicadores
- [media] 97 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 298 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 0 ciclo(s) hoje · 1 vermelho(s) · 0 etapa(s) com erro · fases puladas {}
- cobertura do dia: 71.7% de 127 motores
- retentativa: {'aguardando_retentativa': 328, 'fora_da_fila': 4, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 1, 'outras-oportunidades-5': 1, 'outras-oportunidades-6': 1, 'plat-empresas-editais-incentivados': 1}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 207
- curadoria do link oficial: {'em curadoria': 432, 'sem link oficial': 181, 'aprovado': 17, 'reprovado': 80}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 6}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-15T23:59:49+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 127) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 396) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 396) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **incorreto** (2 de 396) — regra: prazo vencido sai das abertas · ex.: agr-a9a2db3bde97: fim 2026-10-15; 97773a721bd40ede563f: fim 2026-10-15
- site_oficial · link oficial gravado no repositório: **correto** (0 de 299) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2869) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 10) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1958) — regra: ato legislativo não gera livro
