# Diagnóstico do sistema · 2026-10-14 20:03 UTC

## Cumprimento da finalidade · índice geral 66%
- Motores: 98% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 69% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 8% (falha) — toda oportunidade aberta validada
- Site oficial: 68% (falha) — toda aberta com site oficial
- Prazo: 22% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 69% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 63% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 5, 'ok': 27, 'atencao': 3, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-14T19:57 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-14T19:49 · sucesso 60% · cadência None h
- 05 · Busca ativa (a cada 3 dias): falha · última 2026-10-03T02:26 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: falha · última 2026-09-27T05:46 · sucesso 0% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): falha · última 2026-10-14T14:13 · sucesso 0% · cadência 24.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-14T12:06 · sucesso 33% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-14T16:15 · sucesso 50% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motores-da-vez.yml: IndexError: list index out of range | Traceback (most recent call last): | gerador dos motores falhou
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 3 etapa(s) falharam em silêncio na última execução de motores-da-vez.yml: IndexError: list index out of range | Traceback (most recent call last): | ge

## Sala de controle · 20 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: nenhum
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)', 'fichas das oportunidades (cobertura da janela de detalhe)', 'alimentação externa diária (enviada, itens, hash confirmado)', 'diagnóstico único (problemas por gravidade e índice de cumprimento da finalidade)', 'percentual de oportunidades validadas (hoje só aparece o total de abertas)']

## Oportunidades
- abertas: 579 · validadas: 45 (7.8%) · por estado: {'em_verificacao': 527, 'validada': 45, 'validacao_manual': 7}
- com livro: 547 · sem livro (problema): 0 · sem livro por regra: 32 {'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 31, 'empresa sem edital por concorrência: é fonte de busca, não livro': 1} · livro inexistente: 0
- sem site oficial: 187 · sem prazo: 451 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 513, 'Resultado': 498, 'Prazo de inscrição': 486, 'Valor': 478, 'Anexos': 456, 'Requisitos': 455, 'Destinação': 424, 'Área de atuação': 424, 'Território': 373, 'Objeto': 365, 'Órgão / financiador': 353, 'Esfera': 349}

## Sistemas
- motores: 41 funcionando · 1 em falha · 3 inativos · 5 com leitura parcial
  - em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (47 h); última leitura 12/10 17:57
- maestro: cobertura 69.2% · esgotados 12
- rede neural: AUC 0.843 · rotulados 2008 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)']
- saúde: 7 alerta(s) · índice da sala de controle: 96

## Integração
- contagens: {'repositorio_abertas': 579, 'diagnostico_abertas': 579, 'tela_cartoes': 579, 'fichas': 682, 'sala_controle_abertas': 579}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.1, 'maestro': 0.0, 'rede_neural': 0.0, 'saude': 1.8}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (21)
- [alta] 3 etapa(s) falharam em silêncio na última execução de motores-da-vez.yml: IndexError: list index out of range | Traceback (most recent call last): | gerador dos motores falhou → investigar a etapa (sem correção automática)
- [alta] 7 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '01 · Eldorado — motores por hora (00h–06h BRT)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] motor em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (47 h); última leitura 12/10 17:57 → investigar o motor (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 272.1 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 321.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] saúde · claude: 1297 item(ns) esperando a análise do Claude (próxima: 2026-10-14) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, RS, PR → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 3 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 187 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 451 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
