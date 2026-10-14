# Diagnóstico do sistema · 2026-10-14 19:52 UTC

Correções aplicadas: 5 de 5 etapas · problemas antes 25 → depois 24

- ok  repositório único (1.5 s)
- ok  tela das oportunidades (fluxo completo) (115.5 s)
- ok  fichas das oportunidades (0.9 s)
- ok  sala de controle (6.0 s)
- ok  saúde do sistema (17.9 s)

## Cumprimento da finalidade · índice geral 67%
- Motores: 93% (atencao) — todo motor ativo lê dentro da sua cadência
- Maestro: 68% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 11% (falha) — toda oportunidade aberta validada
- Site oficial: 78% (atencao) — toda aberta com site oficial
- Prazo: 24% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 69% (falha) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 63% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 5, 'ok': 27, 'atencao': 3, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-14T19:49 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-14T19:49 · sucesso 50% · cadência None h
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

## Sala de controle · 25 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Alimentação externa diária']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 426 · validadas: 45 (10.6%) · por estado: {'em_verificacao': 374, 'validada': 45, 'validacao_manual': 7}
- com livro: 334 · sem livro (problema): 0 · sem livro por regra: 92 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 75, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 16, 'empresa sem edital por concorrência: é fonte de busca, não livro': 1} · livro inexistente: 0
- sem site oficial: 95 · sem prazo: 323 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 366, 'Resultado': 354, 'Prazo de inscrição': 343, 'Valor': 339, 'Anexos': 316, 'Requisitos': 314, 'Área de atuação': 290, 'Destinação': 289, 'Território': 252, 'Objeto': 243, 'Órgão / financiador': 238, 'Esfera': 235}

## Sistemas
- motores: 39 funcionando · 3 em falha · 0 inativos · 5 com leitura parcial
  - em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (46 h); última leitura 12/10 17:57
  - em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:10
  - em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:13
- maestro: cobertura 68.0% · esgotados 12
- rede neural: AUC 0.843 · rotulados 2008 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)']
- saúde: 7 alerta(s) · índice da sala de controle: 92

## Integração
- contagens: {'repositorio_abertas': 426, 'diagnostico_abertas': 426, 'tela_cartoes': 426, 'fichas': 432, 'sala_controle_abertas': 426}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.5, 'maestro': 0.5, 'rede_neural': 0.0, 'saude': 0.0}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (24)
- [alta] 3 etapa(s) falharam em silêncio na última execução de motores-da-vez.yml: IndexError: list index out of range | Traceback (most recent call last): | gerador dos motores falhou → investigar a etapa (sem correção automática)
- [alta] 7 etapa(s) falharam em silêncio na última execução de monitoramento-diario.yml: "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ba | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-ed | "erro": "FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Eldorado/Eldorado/biblioteca_alexandria/oportunidades/abcr-continue-lendo-fu → investigar a etapa (sem correção automática)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)'] | - [alta] 15 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6933 certificado · fluxos do GitHub com falha: ['03 · Eldorad | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '01 · Eldorado — motores por hora (00h–06h BRT)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] motor em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (46 h); última leitura 12/10 17:57 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:10 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:13 → investigar o motor (sem correção automática)
- [alta] 2 oportunidades municipais de outros estados ainda abertas (só Goiás tem municipais) → refazer o repositório
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 271.9 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 321.3 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] saúde · claude: 1299 item(ns) esperando a análise do Claude (próxima: 2026-10-14) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, ES, RS → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 3 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 95 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 323 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
