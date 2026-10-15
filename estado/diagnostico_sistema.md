# Diagnóstico do sistema · 2026-10-15 14:41 UTC

Correções aplicadas: 5 de 5 etapas · problemas antes 17 → depois 16

- ok  repositório único (2.4 s)
- ok  tela das oportunidades (fluxo completo) (105.3 s)
- ok  fichas das oportunidades (1.0 s)
- ok  sala de controle (5.4 s)
- ok  saúde do sistema (3.9 s)

## Cumprimento da finalidade · índice geral 62%
- Motores: 100% (ok) — todo motor ativo lê dentro da sua cadência
- Maestro: 4% (falha) — cobertura completa do dia planejado
- Rede neural: 99% (ok) — discernimento (AUC) de pelo menos 0,85
- Biblioteca: 100% (ok) — toda oportunidade aberta aplicável com livro existente
- Validação: 10% (falha) — toda oportunidade aberta validada
- Site oficial: 62% (falha) — toda aberta com site oficial
- Prazo: 28% (falha) — toda aberta com prazo (ou fluxo contínuo)
- Cartório: 70% (atencao) — 12 de 12 itens certificados na fonte oficial
- Tela e fichas: 100% (ok) — tudo que está aberto aparece na tela e tem ficha
- Integração: 100% (ok) — mesmas contagens e dados em dia em todos os sistemas
- Fluxos automáticos: 65% (falha) — todo fluxo agendado roda na cadência e sem falha
- Execução sem falha silenciosa: 0% (falha) — nenhuma etapa falha em silêncio

## Execução · fluxos: {'falha': 4, 'ok': 32, 'atencao': 4, 'atrasado': 2, 'manual': 2}
- 00 · Verificar prontidão: falha · última 2026-10-15T14:02 · sucesso 0% · cadência 24.0 h
- 35 · Alimentação diária externa (editais abertos): falha · última 2026-10-14T14:40 · sucesso 0% · cadência 24.0 h
- 36 · Análise do sistema (diagnóstico único e correção): atencao · última 2026-10-15T14:02 · sucesso 78% · cadência None h
- 05 · Busca ativa (a cada 3 dias): falha · última 2026-10-03T02:26 · sucesso 0% · cadência None h
- 09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes: atrasado · última 2026-10-03T11:56 · sucesso 100% · cadência 24.0 h
- 10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar: falha · última 2026-09-27T05:46 · sucesso 0% · cadência None h
- 01 · Eldorado — motores por hora (00h–06h BRT): atencao · última 2026-10-15T10:59 · sucesso 0% · cadência 24.0 h
- 34 · Motores de empresas (semanal, com recuperação): atencao · última 2026-10-15T11:42 · sucesso 50% · cadência 24.0 h
- 03 · Eldorado — carga histórica de cinco anos (campanha única, mês a mês): atencao · última 2026-10-15T10:38 · sucesso 60% · cadência 6.0 h
- 02 · Alexandria — revisão mensal de leis e procedimentos: atrasado · última 2026-10-01T10:36 · sucesso 50% · cadência 24.0 h
- falha silenciosa em cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last):
- falha silenciosa em analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão'] | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 9 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verifica | - [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)

## Sala de controle · 29 indicadores · atualizada há 0.0 h
- divergências com a fonte: nenhuma
- sem leitura: ['Alimentação externa diária']
- estados incoerentes: nenhum
- sugestões de apresentação: ['decisões da titular (descartadas/inscritas aguardando aplicação e livros sinalizados para o Claude)']

## Oportunidades
- abertas: 437 · validadas: 42 (9.6%) · por estado: {'em_verificacao': 387, 'validada': 42, 'validacao_manual': 8}
- com livro: 392 · sem livro (problema): 0 · sem livro por regra: 45 {'fora da abrangência: oportunidade pública municipal de outro estado (só Goiás tem livros m': 33, 'não é seleção aberta a associações (dispensa/inexigibilidade de chamamento, credenciamento': 5, 'fora da abrangência: municipal de outro estado (PE) que não é capital — só Goiás tem munic': 2, 'fora da abrangência: municipal de outro estado (PI) que não é capital — só Goiás tem munic': 2, 'fora da abrangência: municipal de outro estado (BA) que não é capital — só Goiás tem munic': 1, 'fora da abrangência: municipal de outro estado (SP) que não é capital — só Goiás tem munic': 1} · livro inexistente: 0
- sem site oficial: 167 · sem prazo: 313 · prazo vencido ainda aberta: 0
- fora da tela: 0 · sem ficha: 0
- itens que mais faltam: {'Prazo de recurso': 375, 'Resultado': 364, 'Prazo de inscrição': 357, 'Valor': 347, 'Anexos': 335, 'Requisitos': 325, 'Destinação': 308, 'Área de atuação': 306, 'Território': 270, 'Objeto': 261, 'Órgão / financiador': 251, 'Esfera': 248}

## Sistemas
- motores: 42 funcionando · 0 em falha · 3 inativos · 2 com leitura parcial
- maestro: cobertura 4.0% · esgotados 2
- rede neural: AUC 0.843 · rotulados 2027 · treinada em 2026-10-14T05:54:08+00:00
- Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão']
- saúde: 2 alerta(s) · índice da sala de controle: 84

## Integração
- contagens: {'repositorio_abertas': 437, 'diagnostico_abertas': 437, 'tela_cartoes': 437, 'fichas': 447, 'sala_controle_abertas': 437}
- idade (h): {'repositorio': 0.0, 'fluxo': 0.0, 'fichas': 0.0, 'sala_controle': 0.0, 'status_motores': 2.1, 'maestro': 2.0, 'rede_neural': 0.0, 'saude': 0.0}
- decisões da titular: 0 · não aplicadas: 0

## Problemas (16)
- [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most recent call last): → investigar a etapa (sem correção automática)
- [alta] 9 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verificar prontidão'] | - [alta] 2 etapa(s) falharam em silêncio na última execução de cartorio.yml: KeyError: 'https://mapaosc.ipea.gov.br/api/api/documentation' | Traceback (most rec | - [alta] 9 etapa(s) falharam em silêncio na última execução de analise-sistema.yml: - Cartório: 0.6963 certificado · fluxos do GitHub com falha: ['00 · Verifica → investigar a etapa (sem correção automática)
- [alta] fluxo '00 · Verificar prontidão' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '35 · Alimentação diária externa (editais abertos)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '05 · Busca ativa (a cada 3 dias)' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] fluxo '10 · Histórico de doações da Rouanet (empresa por empresa) — retoma sozinho até completar' falhou nas últimas execuções (0% de sucesso) → investigar o fluxo (sem correção automática)
- [alta] 6 oportunidades municipais de outros estados ainda abertas (só Goiás tem municipais) → refazer o repositório
- [alta] 3 módulos de teste em quarentena por DEFEITO REAL → corrigir o código e tirar da quarentena (sem correção automática)
- [media] fluxo '09 · Base histórica dos incentivos (5 anos) — Rouanet, Esporte, PRONON, PRONAS, FIA, Idoso, PAT, Goyazes' sem rodar há 290.8 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] fluxo '02 · Alexandria — revisão mensal de leis e procedimentos' sem rodar há 340.1 h (cadência 24.0 h) → investigar o agendamento (sem correção automática)
- [media] 69 oportunidade(s) usam o link de acesso como oficial sem serem fonte oficial → buscar a fonte oficial (resolvedor e Cartório)
- [media] saúde · claude: 1357 item(ns) esperando a análise do Claude (próxima: 2026-10-15) → ver o fluxo/arquivo indicado
- [media] saúde · coerência: mapa e lista divergem em SC, __nac__, BA, SP, ES → refazer tela e indicadores
- [media] 167 abertas ainda sem site oficial → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 313 abertas sem prazo de inscrição conhecido → Cartório/Interceptador (sem correção automática imediata)
- [baixa] 18 módulos de teste em quarentena (envelhecidos) → atualizar o teste à regra atual (sem correção automática)

## Workflow (estrutura de 15/10)
- comando único: 1 ciclo(s) hoje · 0 vermelho(s) · 0 etapa(s) com erro · fases puladas {'treinar_rede': 1, 'biblioteca_diaria': 1}
- cobertura do dia: 4.0% de 125 motores
- retentativa: {'aguardando_retentativa': 28, 'fora_da_fila': 0, 'fora_da_fila_por_escopo': {}, 'regra': 'volta em 30 min; sai após 5 tentativas com o mesmo erro'} · leitura parcial na fila: 16
- curadoria do link oficial: {'reprovado': 120, 'em curadoria': 408, 'aprovado': 24, 'sem link oficial': 117}
- validação por exceção: trava fechada: acerto do Cartório 66.1% < 85.0% — candidatas vão à frente da conferência humana
- auditorias: {'gabarito_do_cartorio': {'em': '2026-10-15T02:12:35+00:00', 'acerto_pct': 66.1, 'documentos_lidos': 142}, 'varredura_referencia': '2026-10-01_2026-10-15', 'robots': {'em': '2026-10-15T10:07:53+00:00', 'motores_com_bloqueio': 6}, 'ponte': {'ponte_ok': 7, 'direto_ok': 5, 'so_pela_ponte': ['ALEGO · SPL (proposições)', 'MPGO'], 'nenhum': ['TJGO · portal'], 'total': 8}}
- legislativo: {'atualizado_em': '2026-10-15T12:46:01+00:00', 'proposicoes': 8}

## Decisões do Eldorado: agiu como deveria?
- decidir · motores escolhidos para ler na passagem: **correto** (0 de 125) — regra: todo motor pendente ou parcial com tentativa sobrando entra na passagem (sem agenda)
- qualificar · oportunidades abertas para associação: **correto** (0 de 437) — regra: pregão, registro de preços, credenciamento de prestadores, contratação de empresa, OS da saúde e seleção de pessoal não são oportunidade (ruído ou acompanhar)
- legislativo · atos legislativos fora das oportunidades: **correto** (0 de 437) — regra: projeto de lei, utilidade pública e orçamento vão ao acompanhamento legislativo, nunca às abertas
- prazo · oportunidades contadas como abertas: **correto** (0 de 437) — regra: prazo vencido sai das abertas
- site_oficial · link oficial gravado no repositório: **correto** (0 de 270) — regra: agregador ou replicador nunca é link oficial
- certificar · itens certificados pelo Cartório: **correto** (0 de 2661) — regra: todo item certificado tem trecho literal e documento
- validar · validação por exceção: **correto** (0 de 0) — regra: só valida sozinho com acerto do Cartório ≥ 85% no gabarito e link oficial aprovado na curadoria
- farol · oportunidades prontas para o Farol: **correto** (0 de 17) — regra: pronta só com prazo vigente e link oficial aprovado na curadoria
- biblioteca · livros da Biblioteca: **correto** (0 de 1909) — regra: ato legislativo não gera livro

## Ciclo de análise nº 4 · janela 2026-10-15T13:33 → 2026-10-15T14:41
- 1 resolvido(s) · 11 persistem apesar de 3 correção(ões) implantada(s) · 0 novo(s) · 7 sem correção definida
- correções implantadas na janela: #232 Comando se reaciona até 98%; link oficial respeita a curadoria; #233 Fluxo 00: testes do motor 01 sem rede real; #234 Fluxo 35: envio com retentativa e motivo visível
- resolvidos: ['decisao_site_oficial']
- persistem: ['falha_silenciosa', 'fluxo_atrasado', 'fluxo_falhando', 'link_acesso_como_oficial', 'municipal_de_outro_estado_aberta', 'saude_claude', 'saude_coerência', 'sem_prazo', 'sem_site_oficial', 'teste_em_quarentena', 'teste_em_quarentena_defeito']
- novos: nenhum
- sem correção definida: ['falha_silenciosa', 'fluxo_atrasado', 'fluxo_falhando', 'sem_prazo', 'sem_site_oficial', 'teste_em_quarentena', 'teste_em_quarentena_defeito']
- a próxima janela começa em 2026-10-15T14:41 (implantação das correções)
