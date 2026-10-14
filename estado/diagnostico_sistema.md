# Diagnóstico do sistema · 2026-10-14 18:14 UTC

Correções aplicadas: 6 de 6 etapas · problemas antes 13 → depois 12

- ok  livros: criar ou vincular para cada oportunidade (2.2 s)
- ok  repositório único (1.6 s)
- ok  tela das oportunidades (fluxo completo) (118.9 s)
- ok  fichas das oportunidades (1.0 s)
- ok  sala de controle (2.5 s)
- ok  saúde do sistema (13.3 s)

## Oportunidades
- abertas: 569 · validadas: 45 (7.9%) · por estado: {'em_verificacao': 517, 'validada': 45, 'validacao_manual': 7}
- com livro: 536 · sem livro (problema): 0 · sem livro por regra: 33 {'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 31, 'empresa sem edital por concorrência: é fonte de busca, não livro': 1, 'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 1} · livro inexistente: 0
- sem site oficial: 185 · sem prazo: 441 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 504, 'Resultado': 489, 'Prazo de inscrição': 476, 'Valor': 468, 'Anexos': 448, 'Requisitos': 445, 'Área de atuação': 415, 'Destinação': 414, 'Território': 364, 'Objeto': 356, 'Órgão / financiador': 344, 'Esfera': 340}

## Sistemas
- motores: 39 funcionando · 3 em falha · 0 inativos · 4 com leitura parcial
  - em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (43 h); última leitura 12/10 17:57
  - em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (244 h); última leitura 04/10 09:10
  - em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (244 h); última leitura 04/10 09:13
- maestro: cobertura 74.5% · esgotados 4
- rede neural: AUC 0.843 · rotulados 2008 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6904 certificado · fluxos do GitHub com falha: ['01 · Eldorado — motores por hora (00h–06h BRT)', '03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês)', '35 · Alimentação diária externa (editais abertos)']
- saúde: 7 alerta(s) · índice da sala de controle: 98

## Integração
- contagens: {'repositorio_abertas': 569, 'diagnostico_abertas': 569, 'tela_cartoes': 569, 'fichas': 672, 'sala_controle_abertas': 569}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 1.6, 'maestro': 1.6, 'rede_neural': 0.0, 'saude': 0.0}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (12)
- [alta] motor em falha: PNCP — API de contratações (chamamentos e credenciamentos) — falha — não lê há 1 dia(s) (43 h); última leitura 12/10 17:57 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) — falha — não lê há 10 dia(s) (244 h); última leitura 04/10 09:10 → investigar o motor (sem correção automática)
- [alta] motor em falha: Motor Patrocínio Privado — mídia e eventos de Goiás (empresas) — falha — não lê há 10 dia(s) (244 h); última leitura 04/10 09:13 → investigar o motor (sem correção automática)
- [media] saúde · claude: 1297 item(ns) esperando a análise do Claude (próxima: 2026-10-14) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em __nac__, BA, SP, RS, PR → refazer tela e indicadores
- [media] saúde · workflows: 00 · Verificar prontidão: últimas 3 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 35 · Alimentação diária externa (editais abertos): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 05 · Busca ativa (a cada 3 dias): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] saúde · workflows: 01 · Eldorado — motores por hora (00h–06h BRT): últimas 5 execuções sem sucesso → ver o fluxo/arquivo indicado
- [media] 185 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 441 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
