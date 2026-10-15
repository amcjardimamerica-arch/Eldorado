# Diagnóstico do sistema · 2026-10-15 06:23 UTC

## Cumprimento da finalidade · índice geral 63%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 0% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 9% (falha) — toda oportunidade aberta validada
- Site oficial: 80% (atencao) — toda aberta com site oficial
- Prazo: 27% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 68% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'ok': 31, 'falha': 4, 'atencao': 4, 'atrasado': 2, 'manual': 2}
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-14T23:58 · sucesso 67% · cadência None h
- 05 · Busca ativa (a cada 3 dias): falha · última 2026-10-03T02:26 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: falha · última 2026-09-27T05:46 · sucesso 0% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): falha · última 2026-10-14T14:13 · sucesso 0% · cadência 24.0 h
- 22 · Motores da vez — cada passagem calcula sozinha o que está pendente (agenda + maestro): atencao · última 2026-10-15T06:20 · sucesso 75% · cadência 1.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-14T12:06 · sucesso 33% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T02:35 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em motores-da-vez.yml: Traceback (most recent call last): | TypeError: '>' not supported between instances of 'NoneType' and 'NoneType' | src.sensores: falhou ou estourou (código 1)
- falha silenciosa em monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-in
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6987 certificado · fluxos do GitHub com falha: ['.github/workflows/00-prontidao.yml'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 2 etapa(s) falharam em silêncio na última execução de motor-agregadores.yml: "rede: robots.txt inacessível: URLError: [SSL: CERTIFICATE_VERIFY_FAILED] 

## Sala de controle · 25 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Alimentação externa diária']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 490 · validadas: 46 (9.4%) · por estado: {'em_verificacao': 437, 'validada': 46, 'validacao_manual': 7}
- com livro: 375 · sem livro (problema): 1 · sem livro por regra: 114 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 87, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 22, 'fora da abrangência: municipal de outro estado (PE) que não é capital — só Goiás tem munic': 2, 'fora da abrangência: municipal de outro estado (BA) que não é capital — só Goiás tem munic': 1, 'fora da abrangência: municipal de outro estado (SP) que não é capital — só Goiás tem munic': 1, 'fora da abrangência: município de outro estado que não é capital (livro apagado)': 1} · livro inexistente: 0
- sem site oficial: 99 · sem prazo: 357 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 425, 'Resultado': 410, 'Prazo de inscrição': 398, 'Valor': 394, 'Anexos': 376, 'Requisitos': 370, 'Destinação': 346, 'Área de atuação': 341, 'Território': 305, 'Objeto': 293, 'Órgão / financiador': 286, 'Esfera': 283}

## Sistemas
- motores: 42 funcionando · 0 em falha · 3 inativos · 1 com leitura parcial
- maestro: cobertura 0.0% · esgotados 0
- rede neural: AUC 0.843 · rotulados 2027 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6996 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão', '03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)']
- saúde: 6 alerta(s) · índice da sala de controle: 88

## Integração
- contagens: {'repositorio_abertas': 490, 'diagnostico_abertas': 490, 'tela_cartoes': 490, 'fichas': 500, 'sala_controle_abertas': 490}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.1, 'maestro': 0.1, 'rede_neural': 0.0, 'saude': 6.4}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (23)
- [alta] 3 etapa(s) falharam em silêncio na última execução de motores-da-vez.yml: Traceback (most recent call last): | TypeError: '>' not supported between instances of 'NoneType' and 'NoneType' | src.sensores: falhou ou estourou (código 1) → investigar a etapa (sem correção automática)
- [alta] 7 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6987 certificado · fluxos do GitHub com falha: ['.github/workflows/00-prontidao.yml'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec → investigar a etapa (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '01 · Eldorado — motores por hora (00h–06h BRT)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 4 oportunidades municipais de outros estados ainda abertas (só Goiás tem municipais) → refazer o repositório
- [alta] 1 de 490 oportunidades abertas sem livro e sem regra que justifique → criar/vincular livros
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 282.5 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 331.8 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 180 livros municipais de outros estados no catálogo (só Goiás tem livros municipais) → refazer a tela
- [media] saúde · claude: análise do Claude atrasada desde 2026-10-14: 1305 item(ns) esperando validação ou descarte → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, ES, RS → refazer tela e indicadores
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 99 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 357 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)
