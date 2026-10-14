# Diagnóstico do sistema · 2026-10-14 20:29 UTC

## Cumprimento da finalidade · índice geral 65%
- Motores: 98% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 69% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 99% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 76% (atencao) — toda aberta com site oficial
- Prazo: 24% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 99% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 70% (atencao) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 65% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 5, 'ok': 28, 'atencao': 3, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-14T20:28 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-14T19:49 · sucesso 60% · cadência None h
- 05 · Busca ativa (a cada 3 dias): falha · última 2026-10-03T02:26 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: falha · última 2026-09-27T05:46 · sucesso 0% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): falha · última 2026-10-14T14:13 · sucesso 0% · cadência 24.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-14T12:06 · sucesso 33% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-14T16:15 · sucesso 50% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 3 etapa(s) falharam em silêncio na última execução de motores-da-vez.yml: IndexError: list index out of range | Traceback (most recent call last): | ge

## Sala de controle · 25 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Alimentação externa diária']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 451 · validadas: 46 (10.2%) · por estado: {'em_verificacao': 398, 'validada': 46, 'validacao_manual': 7}
- com livro: 431 · sem livro (problema): 3 · sem livro por regra: 17 {'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 16, 'empresa sem edital por concorrência: é fonte de busca, não livro': 1} · livro inexistente: 0
- sem site oficial: 109 · sem prazo: 343 · prazo vencido ainda aberta: 0
- fora da tela: 3 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 390, 'Resultado': 377, 'Prazo de inscrição': 365, 'Valor': 361, 'Anexos': 340, 'Requisitos': 336, 'Destinação': 311, 'Área de atuação': 311, 'Território': 274, 'Objeto': 264, 'Órgão / financiador': 258, 'Esfera': 255}

## Sistemas
- motores: 41 funcionando · 1 em falha · 3 inativos · 5 com leitura parcial
  - em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (47 h); última leitura 12/10 17:57
- maestro: cobertura 69.2% · esgotados 12
- rede neural: AUC 0.843 · rotulados 2008 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6981 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)']
- saúde: 7 alerta(s) · índice da sala de controle: 93

## Integração
- contagens: {'repositorio_abertas': 451, 'diagnostico_abertas': 451, 'tela_cartoes': 579, 'fichas': 461, 'sala_controle_abertas': 451}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.4, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.0, 'maestro': 0.5, 'rede_neural': 0.4, 'saude': 0.6}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (24)
- [alta] 7 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '01 · Eldorado — motores por hora (00h–06h BRT)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 3 abertas no repositório que não aparecem na tela de oportunidades → refazer a tela
- [alta] motor em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (47 h); última leitura 12/10 17:57 → investigar o motor (sem correção automática)
- [alta] 3 de 451 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] tela mostra 579 oportunidades e o repositório conta 451 → refazer a tela
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 272.6 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 321.9 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 289 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] saúde · claude: 1299 item(ns) esperando a análise do Claude (próxima: 2026-10-14) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, ES, RS → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 3 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 109 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 343 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
