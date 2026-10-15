# Diagnóstico do sistema · 2026-10-15 17:11 UTC

## Cumprimento da finalidade · índice geral 67%
- Motores: 93% (atencao) — todo motor ativo lê dentro da sua cadência
- Maestro: 67% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 75% (atencao) — toda aberta com site oficial
- Prazo: 28% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 69% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 60% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 1, 'ok': 32, 'atencao': 7, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-15T16:45 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): atencao · última 2026-10-15T15:14 · sucesso 12% · cadência 24.0 h
- 05 · Busca ativa (a cada 3 dias): atencao · última 2026-10-15T16:31 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: atencao · última 2026-10-15T16:09 · sucesso 14% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-15T10:59 · sucesso 0% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-15T16:38 · sucesso 78% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-15T11:42 · sucesso 50% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T10:38 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão'] | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 9 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verifica | - [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (40% de sucesso) → investigar o fluxo (sem correção automática)

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 405 · validadas: 40 (9.9%) · por estado: {'em_verificacao': 358, 'validada': 40, 'validacao_manual': 7}
- com livro: 378 · sem livro (problema): 0 · sem livro por regra: 27 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 22, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 4, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 1} · livro inexistente: 0
- sem site oficial: 101 · sem prazo: 291 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 346, 'Resultado': 337, 'Prazo de inscrição': 332, 'Valor': 321, 'Anexos': 309, 'Requisitos': 298, 'Destinação': 283, 'Área de atuação': 282, 'Território': 250, 'Objeto': 245, 'Órgão / financiador': 234, 'Esfera': 230}

## Sistemas
- motores: 41 funcionando · 3 em falha · 1 inativos · 4 com leitura parcial
  - em falha: Adaptador WordPress — sites oficiais pela API pública — falha na leitura de 15/10 12:33 — nenhuma página leu
  - em falha: Adaptador Mapas Culturais — oportunidades com inscrição aberta — falha na leitura de 15/10 13:56 — nenhuma página leu
  - em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 1 dia(s) (28 h); última leitura 14/10 09:09
- maestro: cobertura 67.2% · esgotados 7
- rede neural: AUC 0.843 · rotulados 2050 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6935 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 2 alerta(s) · índice da sala de controle: 83

## Integração
- contagens: {'repositorio_abertas': 405, 'diagnostico_abertas': 405, 'tela_cartoes': 405, 'fichas': 412, 'sala_controle_abertas': 405}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.1, 'maestro': 0.1, 'rede_neural': 0.0, 'saude': 1.1}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (14)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 13 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão'] | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 9 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verifica → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] motor em falha: Adaptador WordPress — sites oficiais pela API pública — falha na leitura de 15/10 12:33 — nenhuma página leu → investigar o motor (sem correção automática)
- [alta] motor em falha: Adaptador Mapas Culturais — oportunidades com inscrição aberta — falha na leitura de 15/10 13:56 — nenhuma página leu → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 1 dia(s) (28 h); última leitura 14/10 09:09 → investigar o motor (sem correção automática)
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 293.3 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 342.6 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] saúde · claude: 1357 item(ns) esperando a análise do Claude (próxima: 2026-10-15) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em SC, GO, __nac__, BA, SP → refazer tela e indicadores
- [media] 101 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 291 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 3 ciclo(s) hoje · 0 vermelho(s) · 0 etapa(s) com erro · fases puladas {'treinar_rede': 3, 'biblioteca_diaria': 3}
- cobertura do dia: 67.2% de 131 motores
- retentativa: {'aguardando_retentativa': 143, 'fora_da_fila': 0, 'fora_da_fila_por_escopo': {}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 60
- curadoria do link oficial: {'em curadoria': 387, 'sem link oficial': 199, 'reprovado': 78, 'aprovado': 18}
- validação por exceção: trava fechada: acerto do Cartório 66.1% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T02:12:35+00:00', 'acerto_pct': 66.1, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 6}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-15T17:11:14+00:00', 'proposicoes': 12}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 131) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 405) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 405) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 405) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 304) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2708) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 11) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1939) — regra: ato legislativo não gera livro
