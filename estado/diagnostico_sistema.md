# Diagnóstico do sistema · 2026-10-17 10:58 UTC

## Cumprimento da finalidade · índice geral 63%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 81% (atencao) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 99% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 76% (atencao) — toda aberta com site oficial
- Prazo: 12% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 53% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 91% (atencao) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 55% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 10% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 1, 'ok': 30, 'atencao': 9, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-17T10:45 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-16T14:17 · sucesso 22% · cadência 24.0 h
- 06 · Alimentação manual (arquivos e links do titular): atencao · última 2026-10-17T01:57 · sucesso 50% · cadência None h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T17:32 · sucesso 10% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 25% · cadência None h
- 12 · Piloto - Interceptador — um alvo por voo, a cada 3 segundos: atencao · última 2026-10-17T10:57 · sucesso 22% · cadência 1.0 h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-17T10:13 · sucesso 22% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-17T10:32 · sucesso 38% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-17T10:57 · sucesso 67% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-17T10:17 · sucesso 67% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motor-agregadores.yml: "rede: robots.txt inacessível: URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)" | "rede: robots.txt inacessível: URLError: timed out", | mapa: falhou
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in

## Sala de controle · 34 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Última importação do Chrome']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 173 · validadas: 17 (9.8%) · por estado: {'em_verificacao': 154, 'validada': 17, 'validacao_manual': 2}
- com livro: 172 · sem livro (problema): 1 · sem livro por regra: 0 {} · livro inexistente: 0
- sem site oficial: 42 · sem prazo: 152 · prazo vencido ainda aberta: 0
- fora da tela: 16 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 156, 'Requisitos': 155, 'Anexos': 152, 'Resultado': 151, 'Território': 150, 'Prazo de inscrição': 147, 'Valor': 147, 'Objeto': 146, 'Modalidade': 144, 'Área de atuação': 140, 'Esfera': 139, 'Órgão / financiador': 137}

## Sistemas
- motores: 43 funcionando · 0 em falha · 2 inativos · 4 com leitura parcial
- maestro: cobertura 81.1% · esgotados 6
- rede neural: AUC 0.843 · rotulados 1684 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.5311 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 5 alerta(s) · índice da sala de controle: 93

## Integração
- contagens: {'repositorio_abertas': 173, 'diagnostico_abertas': 173, 'tela_cartoes': 158, 'fichas': 174, 'sala_controle_abertas': 173}
- idade (h): {'repositorio': 0.0, 'fluxo': 1.3, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.0, 'maestro': 1.3, 'rede_neural': 1.3, 'saude': 21.2}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (20)
- [alta] 4 etapa(s) com erro nos ciclos de hoje: recalcular: recalcular:1: código 124 | recalcular: recalcular:1: código 124 | recalcular: recalcular:1: código 124 → investigar a etapa (sem correção automática)
- [alta] 3 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: "rede: robots.txt inacessível: URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)" | "rede: robots.txt inacessível: URLError: timed out", | mapa: falhou → investigar a etapa (sem correção automática)
- [alta] 6 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 16 abertas no repositório que não aparecem na tela de oportunidades → refazer a tela
- [alta] 1 de 173 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] tela mostra 158 oportunidades e o repositório conta 173 → refazer a tela
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 335.0 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 384.4 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 43 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] 49 página(s)/documento(s) fora da fila após 5 erros iguais → corrigir a rota ou ler no Chrome (sem correção automática)
- [media] saúde · claude: 1180 item(ns) esperando a análise do Claude (próxima: 2026-10-16) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, GO, SC, SP, MG → refazer tela e indicadores
- [media] saúde · opressores: 1 opressor(es) duplicado(s) no catálogo → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): últimas 4 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 42 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 152 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 8 ciclo(s) hoje · 4 vermelho(s) · 4 etapa(s) com erro · fases puladas {'modalidade': 8, 'treinar_rede': 8, 'expurgo': 7, 'migracao_livros': 8, 'unir_livros': 7, 'biblioteca_diaria': 7, 'vigilancia_diaria': 7, 'recalcular': 4}
- cobertura do dia: 81.1% de 127 motores
- retentativa: {'aguardando_retentativa': 816, 'fora_da_fila': 49, 'fora_da_fila_por_escopo': {'outras-oportunidades-1': 8, 'outras-oportunidades-6': 2, 'recorrencia': 4, 'outras-oportunidades-5': 5, 'outras-oportunidades-8': 4, 'outras-oportunidades-3': 1, 'f260-captacao-044': 1, 'outras-oportunidades-2': 2, 'plat-empresas-editais-incentivados': 2, 'f260-captacao-238': 2, 'cartorio': 18, 'outras-oportunidades-7': 2, 'f260-captacao-242': 1, 'f260-captacao-224': 1, 'empresas-incentivadas': 1, 'f260-curadoria-005': 1}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro', 'destinos': {'Claude no Chrome': 18, 'rota quebrada': 6, 'ponte ou Chrome': 31, 'sem destino': 0}} · leitura parcial na fila: 677
- curadoria do link oficial: {'em curadoria': 131, 'reprovado': 18, 'aprovado': 8, 'sem link oficial': 8}
- validação por exceção: trava fechada: acerto do Cartório 77.4% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T19:53:25+00:00', 'acerto_pct': 77.4, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 5}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-17T10:08:36+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 127) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 173) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 173) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 173) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 131) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 83) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 4) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1299) — regra: ato legislativo não gera livro
