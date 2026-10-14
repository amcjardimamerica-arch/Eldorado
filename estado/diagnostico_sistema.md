# Diagnóstico do sistema · 2026-10-14 19:21 UTC

## Oportunidades
- abertas: 572 · validadas: 45 (7.9%) · por estado: {'em_verificacao': 520, 'validada': 45, 'validacao_manual': 7}
- com livro: 539 · sem livro (problema): 0 · sem livro por regra: 33 {'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 31, 'empresa sem edital por concorrência: é fonte de busca, não livro': 1, 'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 1} · livro inexistente: 0
- sem site oficial: 185 · sem prazo: 444 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 507, 'Resultado': 492, 'Prazo de inscrição': 479, 'Valor': 471, 'Anexos': 450, 'Requisitos': 448, 'Destinação': 417, 'Área de atuação': 417, 'Território': 366, 'Objeto': 358, 'Órgão / financiador': 346, 'Esfera': 342}

## Sistemas
- motores: 39 funcionando · 3 em falha · 0 inativos · 5 com leitura parcial
  - em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (46 h); última leitura 12/10 17:57
  - em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:10
  - em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:13
- maestro: cobertura 68.0% · esgotados 12
- rede neural: AUC 0.843 · rotulados 2008 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6904 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão', '03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)', '35 · Alimentação diária externa (editais abertos)']
- saúde: 7 alerta(s) · índice da sala de controle: 96

## Integração
- contagens: {'repositorio_abertas': 572, 'diagnostico_abertas': 572, 'tela_cartoes': 572, 'fichas': 675, 'sala_controle_abertas': 572}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 0.0, 'maestro': 0.0, 'rede_neural': 0.0, 'saude': 1.1}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (12)
- [alta] motor em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (46 h); última leitura 12/10 17:57 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:10 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (247 h); última leitura 04/10 09:13 → investigar o motor (sem correção automática)
- [media] saúde · claude: 1297 item(ns) esperando a análise do Claude (próxima: 2026-10-14) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, RS, PR → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 3 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 185 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 444 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
