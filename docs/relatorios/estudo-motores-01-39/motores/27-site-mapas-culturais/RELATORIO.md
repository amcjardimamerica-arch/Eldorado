# Motor 27 — site-mapas-culturais (Mapas Culturais) — Relatório

Data do estudo: 02/10/2026. Janela do histórico: 02/10/2023 a 02/10/2026. Chamadas WebFetch usadas: 34 (limite ~40).
Observação técnica: `curl` direto é bloqueado pelo proxy (403 CONNECT); todos os testes foram feitos via WebFetch.
Nenhuma instrução dirigida ao agente foi encontrada no conteúdo das páginas.

## 1. Rota (teste e conclusão)

**Rota configurada:** `None` (leitor `mapas_culturais`). **Página do titular:** https://mapagoiano.cultura.go.gov.br/ (rede de instâncias).

robots.txt: `mapagoiano.cultura.go.gov.br/robots.txt` e `mapa.cultura.gov.br/robots.txt` retornam **404** (nenhuma restrição declarada). `mapas.cultura.gov.br` (com "s") foi **recusado pelo WebFetch** ("robots.txt fetch failed: Response too large") — não insisti.

| URL testada | Resposta | O que entrega |
|---|---|---|
| `https://mapagoiano.cultura.go.gov.br/api/opportunity/find?@select=id,name,registrationFrom,registrationTo,createTimestamp,ownerEntity,shortDescription&@order=registrationTo%20DESC&@limit=100&registrationTo=GTE(2023-10-02)` | 200, JSON | **61 oportunidades** no período, com data de abertura, prazo (registrationTo), data de criação, resumo. Sem valor e sem link oficial. |
| mesma rota com `@select=id,type,isVerified,ownerEntity.name,owner.name` | 200, JSON | tipo (Edital, Oficina, Festival…), selo verificado, entidade dona. Atenção: `owner.name` traz nome de pessoa física (não armazenar). |
| `https://mapa.cultura.gov.br/api/opportunity/find?@count=1&registrationTo=GTE(2023-10-02)` | 200 | **284** oportunidades no período (instância nacional/MinC). |
| `https://mapa.cultura.gov.br/api/opportunity/find?...&@limit=100&@page=1..3&registrationTo=GTE(2023-10-02)` | 200, JSON | paginação funciona (3 páginas cobrem as 284). |
| `https://mapa.cultura.gov.br/api/opportunity/find?@select=...,site,shortDescription,registrationCategories&id=IN(...)` | 200, JSON | detalhe em lote; `site` vem **null** em todos os itens testados; categorias vêm preenchidas. |
| `...&isVerified=EQ(1)` | **500** | filtro por selo quebra a API nacional — não usar. |
| `https://mapa.cultura.gov.br/oportunidade/11685/` (página HTML) | 200, mas SPA | só título e descrição; datas/valores não aparecem no HTML. A API é muito melhor que a página. |
| `https://pnab.cultura.go.gov.br/api/opportunity/find` | 302 → goias.gov.br/cultura/pnab/ | **não é instância Mapas**; PNAB Goiás usa o **Sistema Baru** (sistemabaru.cultura.go.gov.br). |

**Conclusão:** a rota `None` deve ser substituída pela API REST do Mapas, uma por instância, com filtro de prazo e paginação:
`https://<instância>/api/opportunity/find?@select=id,name,registrationFrom,registrationTo,createTimestamp,type,ownerEntity.name,shortDescription,registrationCategories&@order=registrationTo%20DESC&@limit=100&@page=N&registrationTo=GTE(AAAA-MM-DD)`.
Instâncias prioritárias: `mapagoiano.cultura.go.gov.br` (GO) e `mapa.cultura.gov.br` (nacional/MinC); secundárias (não varridas por limite de chamadas, apenas abertas por amostra): `mapacultural.pa.gov.br`, `mapa.cultura.es.gov.br`.

**Achado crítico:** o Mapa Goiano está quase parado para editais estaduais. Em 2026 só recebeu o Goyazes Excepcionais; a PNAB Goiás 2024–2026 roda no **Sistema Baru** e a inscrição regular do Goyazes em `editaiscultura.sistemas.go.gov.br`. A PNAB Goiânia 2024 também não está no Mapa Goiano. O motor, sozinho, **não vê** os principais editais de Goiás desde 2024.

## 2. Histórico de 3 anos

Universo bruto: 61 (GO) + 284 (nacional) = 345 registros. Depois de tirar ruído (testes, formulários de prestação de contas, recursos, divulgação de shows/serviços de particulares, oficinas de pessoas físicas), ficaram **97 oportunidades** neste estudo (inclui 6 sementes verificadas e 21 oportunidades oficiais de Goiás/Goiânia/MinC fora do Mapas, confirmadas no site oficial):
- **6 abertas**, **88 encerradas (encerrado_arquivar)**, **3 sem data**;
- aplicáveis a OSC de Goiânia: **14 sim**, **47 dependem**, **36 não**;
- **56 criar_livro** (com site oficial confirmado) e **41 aguardar_fonte**.

Verificação das sementes (19 indícios): 16 links da instância nacional conferidos em lote pela API (todos existem, status 1) e 4 páginas abertas (11685, 11453, PA 2472, ES 2161 — todas abrem, mas são SPA sem datas no HTML). **Nenhum `link_oficial` das sementes é site oficial do financiador** — todos são a própria página do agregador. Das 19 sementes, só 7 são oportunidades reais (11453, 11455, 11683, 11882, 5386, 2472, 2161); 12 são ruído: prestação de contas (9806, 8483), utilitário (5388), formulário de escuta (6614), testes (6873, 6876) e anúncios de particulares (9922, 5691, 5706, 8365, 2352, 2354). Prazos "2100/2111" são marcadores de "sem prazo", não datas reais.

| data (início) | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2026-10-06 | Programa Ciclos de Saberes e Conhecimentos Tradicionais, Populares e das Artes | Secretaria de Formação Artística e Cultural, Livro e Leitura (SEFLI/MinC) | (aguardar_fonte) | 2026-10-24 | aberto | nao |
| 2026-10-02 | 2ª EDIÇÃO - EDITAL DE SELEÇÃO CULTURA VIVA - FOMENTO À REDE DE PONTÕES CULTURA VIVA | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) | (aguardar_fonte) | 2026-10-30 | aberto | depende |
| 2026-09-18 | 2º PRÊMIO TRAJETÓRIAS CULTURAIS / QUADRILHAS JUNINAS / IBIASSUCÊ-BA | Aldir Blanc Ibiassucê-BA (Ciclo 2) | (aguardar_fonte) | 2026-10-02 | aberto | nao |
| 2026-09-18 | 1º CISCO CULTURAL / DIVERSAS ÁREAS CULTURAIS / IBIASSUCÊ-BA | Aldir Blanc Ibiassucê-BA (Ciclo 2) | (aguardar_fonte) | 2026-10-02 | aberto | nao |
| 2026-09-18 | 2º PRÊMIO CULTURA VIVA / PONTOS DE CULTURA / IBIASSUCÊ-BA | Aldir Blanc Ibiassucê-BA (Ciclo 2) | (aguardar_fonte) | 2026-10-02 | aberto | nao |
| 2026-07-29 | Chamamento Público para o Mercado das Indústrias Criativas do Sul - MICSUL 2026 | Economia Criativa / MinC | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/edital-de-selecao-micsul-2026/edital-de-selecao-micsul-2026 | 2026-08-12 | encerrado_arquivar | nao |
| 2026-06-16 | Programa Rouanet Centro-Oeste (Edital MinC nº 3, de 15/06/2026) | Ministério da Cultura | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-centro-oeste/programa-rouanet-centro-oeste | 2026-08-13 | encerrado_arquivar | depende |
| 2026-06-15 | EDITAL DE INTERCÂMBIO CULTURAL MINC Nº 1 - CIRCULAÇÃO E PARTICIPAÇÃO AUDIOVISUAL | Secretaria do Audiovisual (SAv/MinC) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-de-intercambio-cultural-circulacao-e-participacao-audiovisual-no-exterior | 2026-09-29 | encerrado_arquivar | depende |
| 2026-06-15 | LUIZ ALVES - PNAB - EDITAL DE CHAMAMENTO PÚBLICO 01/2026 - SEMEC | Secretaria de Esportes e Cultura de Luiz Alves (SC) | (aguardar_fonte) | 2026-07-20 | encerrado_arquivar | nao |
| 2026-06-11 | Chamamento Público 01/26 - PNAB Camaquã - Seleção de Projetos Culturais | Secretaria Municipal de Cultura, Turismo e Eventos de Camaquã/RS | (aguardar_fonte) | 2026-07-13 | encerrado_arquivar | nao |
| 2026-06-11 | Chamamento Público 2/26 Camaquã - Premiação de Pontos e Pontões de Cultura | Secretaria Municipal de Cultura, Turismo e Eventos de Camaquã/RS | (aguardar_fonte) | 2026-07-13 | encerrado_arquivar | nao |
| 2026-06-02 | EDITAL DE CHAMAMENTO PÚBLICO Nº 01/2026 - ALTEROSA | Secretaria Municipal de Cultura, Lazer e Turismo de Alterosa/MG | (aguardar_fonte) | 2026-07-03 | encerrado_arquivar | nao |
| 2026-05-04 | Certificação de Escolas Livres de Formação em Arte e Cultura | Secretaria de Formação Artística e Cultural, Livro e Leitura (SEFLI/MinC) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-escolas-livres-de-formacao-em-arte-e-cultura | 2026-07-05 | encerrado_arquivar | sim |
| 2026-03-20 | 1º EDITAL RIO CULTURAL - FOMENTO ÀS DIVERSAS ÁREAS CULTURAIS (RIO DO ANTÔNIO-BA) | Aldir Blanc Rio do Antônio-BA (Ciclo 2) | (aguardar_fonte) | 2026-04-17 | encerrado_arquivar | nao |
| 2026-03-20 | 2º EDITAL - PRÊMIO CULTURA VIVA RIO DO ANTÔNIO - BA | Aldir Blanc Rio do Antônio-BA (Ciclo 2) | (aguardar_fonte) | 2026-04-17 | encerrado_arquivar | nao |
| 2026-03-20 | 2º EDITAL - PRÊMIO TRAJETÓRIAS CULTURAIS - RIO DO ANTÔNIO - BA | Aldir Blanc Rio do Antônio-BA (Ciclo 2) | (aguardar_fonte) | 2026-04-17 | encerrado_arquivar | nao |
| 2026-01-20 | PROGRAMA GOYAZES 2026 - EXCEPCIONAIS | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/programa-goyazes/ | 2026-06-10 | encerrado_arquivar | depende |
| 2026-01-16 | EDITAL DE CHAMAMENTO - PROGRAMAÇÃO DA 6ª TEIA NACIONAL PONTOS DE CULTURA | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) | (aguardar_fonte) | 2026-02-02 | encerrado_arquivar | depende |
| 2025-11-28 | INOVA CULTURA | Economia Criativa / MinC | (aguardar_fonte) | 2026-01-30 | encerrado_arquivar | nao |
| 2025-11-27 | EDITAL Nº03/2025 - FUNDO MUNICIPAL DE CULTURA DE SÃO ROQUE | Fundo Municipal de Cultura de São Roque (SP) | (aguardar_fonte) | 2026-01-20 | encerrado_arquivar | nao |
| 2025-11-10 | Edital de Premiação de Iniciativas de Boas Práticas nos CEUs das Artes | Subsecretaria de Espaços e Equipamentos Culturais (SEEC/MinC) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-premio-boas-praticas-dos-ceus-das-artes | 2026-01-23 | encerrado_arquivar | depende |
| 2025-06-10 | Prêmio VIVALEITURA 2025 | Ministério da Cultura (livro e leitura) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-premio-vivaleitura | 2025-07-21 | encerrado_arquivar | sim |
| 2025-05-22 | EDITAL DE CHAMAMENTO PÚBLICO - MICBR 2025 | MICBR 2025 (MinC) | (aguardar_fonte) | 2025-06-23 | encerrado_arquivar | depende |
| 2025-01-06 | PROGRAMA GOYAZES 2025 - EXCEPCIONAIS | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/programa-goyazes/ | 2025-08-29 | encerrado_arquivar | depende |
| 2024-12-17 | INSCRIÇÕES CINE GOIÁS ITINERANTE 2025 | Secretaria de Estado da Cultura de Goiás | (aguardar_fonte) | 2025-03-06 | encerrado_arquivar | depende |
| 2024-12-01 | Cadastro Nacional de Pontos e Pontões de Cultura | Cadastro Nacional Cultura Viva (MinC) | (aguardar_fonte) | — | sem_data | sim |
| 2024-11-14 | PROGRAMA DE INTERCÂMBIO CULTURAL - EDITAL DE MOBILIDADE CULTURAL Nº 01/2024 | Programa de Intercâmbio Cultural (MinC) | (aguardar_fonte) | 2025-03-26 | encerrado_arquivar | depende |
| 2024-11-08 | PRÊMIO TRAJETÓRIAS CULTURAIS - FAZEDORES E COLETIVOS DE CULTURA DE IBIASSUCÊ | PNAB Ibiassucê-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-11-08 | EDITAL MÃE MÔNICA PNAB - FOMENTO ÀS DIVERSAS ÁREAS CULTURAIS (IBIASSUCÊ-BA) | PNAB Ibiassucê-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-11-08 | SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS, AMBIENTES E INICIATIVAS ARTÍSTICO-CULTURAIS (IBIASSUCÊ-BA) | PNAB Ibiassucê-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-11-08 | PRÊMIO CULTURA VIVA IBIASSUCÊ-BA | PNAB Ibiassucê-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-11-08 | PRÊMIO TRAJETÓRIAS CULTURAIS - RIO DO ANTÔNIO-BA | PNAB Rio do Antônio-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-11-08 | PRÊMIO CULTURA VIVA RIO DO ANTÔNIO-BA | PNAB Rio do Antônio-BA 2024 | (aguardar_fonte) | 2024-12-09 | encerrado_arquivar | nao |
| 2024-10-23 | EDITAL Nº 001/2024 - SELEÇÃO DE PROJETOS - PNAB - ALTO PARAÍSO DE GOIÁS | Prefeitura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-12-16 | encerrado_arquivar | nao |
| 2024-10-23 | EDITAL Nº 002/2024 - PREMIAÇÃO AGENTES CULTURAIS - PNAB - ALTO PARAÍSO DE GOIÁS | Prefeitura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-12-16 | encerrado_arquivar | nao |
| 2024-10-23 | EDITAL Nº 003/2024 - SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS - PNAB - ALTO PARAÍSO DE GOIÁS | Prefeitura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-12-16 | encerrado_arquivar | nao |
| 2024-09-20 | PRÊMIO RETOMADA – DIVERSIDADE CULTURAL / RS | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) | (aguardar_fonte) | 2024-10-14 | encerrado_arquivar | nao |
| 2024-09-16 | Edital de Patrocínio MINC/SECOM-PR nº 1/2024 - Cultura Viva - Apoio Cultural às Rádios Comunitárias | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) e SECOM-PR | (aguardar_fonte) | 2024-10-07 | encerrado_arquivar | depende |
| 2024-05-08 | REGIÃO CENTRO-OESTE: Agente Territorial de Cultura | Ministério da Cultura | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-dos-agentes-territoriais-de-cultura-2024 | 2024-06-10 | encerrado_arquivar | nao |
| 2024-04-02 | Programa Goyazes 2024 - ABRIL | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/programa-goyazes/ | 2024-04-30 | encerrado_arquivar | depende |
| 2024-01-02 | Programa Goyazes 2024 - EXCEPCIONAIS | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/programa-goyazes/ | 2024-04-30 | encerrado_arquivar | depende |
| 2023-11-23 | SCDC/MinC - REABERTURA Edital nº 09/2023 Cultura Viva - Fomento a Pontões | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-cultura-viva-2023-fomento-a-pontoes-de-cultura | 2023-11-29 | encerrado_arquivar | depende |
| 2023-11-21 | EDITAL Nº 001/2023 - FOMENTO AUDIOVISUAL - LPG ALTO PARAÍSO DE GOIÁS | Secretaria Municipal de Cultura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-02-09 | encerrado_arquivar | nao |
| 2023-11-21 | EDITAL Nº 002/2023 - PREMIAÇÃO AUDIOVISUAL - LPG ALTO PARAÍSO DE GOIÁS | Secretaria Municipal de Cultura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-02-09 | encerrado_arquivar | nao |
| 2023-11-21 | EDITAL Nº 003/2023 - PREMIAÇÃO DEMAIS ÁREAS - LPG ALTO PARAÍSO DE GOIÁS | Secretaria Municipal de Cultura de Alto Paraíso de Goiás | (aguardar_fonte) | 2024-02-09 | encerrado_arquivar | nao |
| 2023-11-13 | Edital 01/2023 - Audiovisual - Uruaçu-GO | Secretaria de Cultura de Uruaçu | (aguardar_fonte) | 2023-12-31 | encerrado_arquivar | nao |
| 2023-11-13 | Edital 02/2023 - Demais Áreas Culturais - Uruaçu-GO | Secretaria de Cultura de Uruaçu | (aguardar_fonte) | 2023-12-31 | encerrado_arquivar | nao |
| 2023-11-09 | EDITAL Nº 03/2023 - APOIO A SALAS DE CINEMA - LEI PAULO GUSTAVO IBIASSUCÊ-BA | Lei Paulo Gustavo Ibiassucê-BA | (aguardar_fonte) | 2023-11-17 | encerrado_arquivar | nao |
| 2023-10-26 | SCDC/MinC - Prêmio Construção Nacional da Cultura Hip Hop 2023 | Secretaria de Cidadania e Diversidade Cultural (SCDC/MinC) | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/edital-premio-cultura-viva-construcao-nacional-do-hip-hop-2023-1 | 2023-12-25 | encerrado_arquivar | sim |
| 2023-10-18 | Edital 001/2023 Audiovisual - Goiânia-GO | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/leipaulogustavo/ | 2023-11-09 | encerrado_arquivar | depende |
| 2023-10-18 | Edital 002/2023 Áreas - Inciso I - Goiânia-GO | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/leipaulogustavo/ | 2023-11-09 | encerrado_arquivar | depende |
| 2023-10-18 | Edital 003/2023 Áreas - Inciso II - Goiânia-GO | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/leipaulogustavo/ | 2023-11-09 | encerrado_arquivar | depende |
| 2023-10-18 | Edital 004/2023 Áreas - Inciso III - Goiânia-GO | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/leipaulogustavo/ | 2023-11-09 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 20/2023 - PONTOS DE CULTURA - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | (aguardar_fonte) | 2023-10-16 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 19/2023 - DINAMIZAÇÃO DE EMPRESAS E ESPAÇOS CULTURAIS - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 18/2023 - OCUPA GOIÁS - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 17/2023 - TRABALHADORES DA CULTURA EM FORMAÇÃO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 16/2023 - ARTE EM CRIAÇÃO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 15/2023 - AÇÕES FORMATIVAS EM GOIÁS - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 14/2023 - CIRCULA GOIÁS - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 13/2023 - POVOS TRADICIONAIS E ORIGINÁRIOS - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 12/2023 - CULTURA LGBTQIAPN+ - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 11/2023 - ECONOMIA SOLIDÁRIA - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | sim |
| 2023-09-20 | EDITAL Nº 10/2023 - ECONOMIA CRIATIVA - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 9/2023 - APOIO A EMPRESAS DO SETOR AUDIOVISUAL - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | nao |
| 2023-09-20 | EDITAL Nº 8/2023 - FORMAÇÃO E DIFUSÃO AUDIOVISUAL - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 7/2023 - DINAMIZAÇÃO DE SALAS DE CINEMA - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | nao |
| 2023-09-20 | EDITAL Nº 6/2023 - PRODUÇÃO AUDIOVISUAL (DESENVOLVIMENTO E FINALIZAÇÃO) - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 5/2023 - PRODUÇÃO AUDIOVISUAL (VIDEOCLIPE, VIDEODANÇA, GAMES) - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 4/2023 - CURTA, SERIADA, TELEFILME, DOCUMENTÁRIO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 3/2023 - CURTA, SERIADA, TELEFILME FICÇÃO/ANIMAÇÃO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 2/2023 - LONGA DOCUMENTÁRIO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-09-20 | EDITAL Nº 1/2023 - LONGA FICÇÃO/ANIMAÇÃO - LEI PAULO GUSTAVO | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/editais/ | 2023-10-16 | encerrado_arquivar | depende |
| 2023-08-17 | Conferências Municipais e Intermunicipais de Cultura (cadastro para municípios) | Secretaria de Estado da Cultura de Goiás | (aguardar_fonte) | 2023-11-26 | encerrado_arquivar | nao |
| 2023-08-10 | Inscrição Cine Goiás Itinerante 2024 | Secretaria de Estado da Cultura de Goiás | (aguardar_fonte) | 2024-10-31 | encerrado_arquivar | depende |
|  | EDITAL DE CONVOCAÇÃO E CHAMAMENTO PÚBLICO N° 001/2026 - BOLSA AGENTE CULTURA VIVA (IDESS) | Instituto de Desenvolvimento Econômico e Social Santanense (IDESS) | (aguardar_fonte) | 2026-10-02 | aberto | nao |
|  | Seleção de bailarinos e bailarinas - coletivo de Dança contemporânea Gáspea | Coletivo Gáspea (Linhares-ES) | (aguardar_fonte) | — | sem_data | nao |
|  | Edital Biblioteca Comunitária é Cultura Viva | Ministério da Cultura | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/edital-biblioteca-comunitaria-e-cultura-viva1/edital-biblioteca-comunitaria-e-cultura-viva | — | sem_data | sim |
|  | PNAB Goiás 2026 - Edital 01 - Bolsas para 6ª Teia Nacional | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 02 - Manutenção Continuada de Grupos/Cias de Arte | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 03 - Manutenção Continuada de Espaços de Cultura | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 04 - Infância e Juventude na Cultura | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 05 - Formação Cultural | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 06 - Cultura e Social | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | sim |
|  | PNAB Goiás 2026 - Edital 07 - Teatro | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 08 - Dança | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 09 - Circo | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 10 - Literatura | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 11 - Música | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 12 - Artesanato | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiás 2026 - Edital 13 - Artes Visuais | Secretaria de Estado da Cultura de Goiás | https://goias.gov.br/cultura/pnab/edital-2026-pnab/ | — | encerrado_arquivar | depende |
|  | PNAB Goiânia 2024 - Edital 08 - Fomento Cultural I – Criação, Montagem, Circulação | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | depende |
|  | PNAB Goiânia 2024 - Edital 09 - Fomento Cultural II – Ações Formativas | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | depende |
|  | PNAB Goiânia 2024 - Edital 10 - Fomento Cultural III – Patrimônio Cultural | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | depende |
|  | PNAB Goiânia 2024 - Edital 11 - Obras e Reformas de Espaços Culturais | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | depende |
|  | PNAB Goiânia 2024 - Edital 12 - Subsídio para Manutenção de Espaços Culturais | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | sim |
|  | PNAB Goiânia 2024 - Edital 13 - Cultura Viva para fomento a Pontos de Cultura | Secretaria Municipal de Cultura de Goiânia | https://www.goiania.go.gov.br/secult/pnab-2024/ | — | encerrado_arquivar | sim |

## 3. Onde publica

- **Mapas Culturais é plataforma de inscrição, não só vitrine.** Quem é dono da oportunidade (órgão, prefeitura, coletivo ou pessoa física) publica e recebe inscrições ali. Qualquer usuário cadastrado pode abrir "oportunidade", e por isso há muito ruído.
- **MinC** (SCDC/Cultura Viva, SAv/Audiovisual, SEFLI/Formação e Livro, SEEC/CEUs, Economia Criativa): inscreve no `mapa.cultura.gov.br` e espelha o edital em `gov.br/cultura/pt-br/assuntos/editais/` (abertos / em andamento / encerrados). Editais do MinC fora do Mapas: Rouanet Centro-Oeste e Rouanet nas Favelas (Salic), Biblioteca Comunitária é Cultura Viva (cadastro SNBP), CNPq/MinC (plataforma CNPq).
- **Secult Goiás:** página oficial `goias.gov.br/cultura/` (editais LPG 2023, PNAB, Goyazes, FAC, Arranjos Regionais FSA). Plataformas: Mapa Goiano (LPG 2023 e Goyazes Excepcionais), **Sistema Baru** (PNAB 2024–2026) e `editaiscultura.sistemas.go.gov.br` (Goyazes regular).
- **SECULT Goiânia:** `goiania.go.gov.br/secult/` (LPG 2023 no Mapa Goiano; PNAB 2024, Lei de Incentivo 2024 e Fundo Municipal fora do Mapas).
- **Prefeituras do interior** (Alto Paraíso, Uruaçu; e, na nacional, municípios da BA, RS, MG, SC e SP): usam o Mapas como formulário; o site oficial não aparece no Mapas (`site` = null).
- **Instâncias estaduais** (PA, ES e outras): mesma lógica; entidades locais publicam bolsas e chamadas.

## 4. Tipos de oportunidade

- **Edital de projeto** (fomento LPG/PNAB, Pontões Cultura Viva, Goyazes, Inova Cultura) — a maior parte.
- **Prêmio** (Cultura Viva, Hip Hop, Vivaleitura, CEUs das Artes, trajetórias culturais municipais).
- **Cadastro/certificação** (Cadastro Nacional de Pontos e Pontões, Escolas Livres, Biblioteca Comunitária, conferências, mapeamentos).
- **Chamada internacional / intercâmbio** (Intercâmbio Audiovisual MinC, Mobilidade Cultural 2024).
- **Bolsa** (Agente Cultura Viva, bolsas IFG, Bolsas Teia) — em geral só para pessoa física.
- **Outro:** mercados (MICSUL, MICBR), seleção de agentes territoriais, credenciamento de pareceristas.
- **Áreas:** audiovisual (muito forte em GO), cultura viva/pontos de cultura, culturas populares e tradicionais, hip hop, leitura/bibliotecas, artes cênicas, economia criativa e solidária, patrimônio.
- **Faixas de valor:** a API não traz valor. Valor confirmado só no Rouanet Centro-Oeste (R$ 29 mi no total; faixas até R$ 200 mil / 500 mil / 650 mil). Os demais estão no PDF do edital.
- **Quem pode participar:** varia. OSC sem fins lucrativos (Pontões, Escolas Livres, Hip Hop, Vivaleitura, Biblioteca Comunitária); PJ cultural com CNAE (Rouanet); pessoa física (agentes territoriais, bolsas); só IFES (Ciclos de Saberes); só residentes do município (editais municipais).

## 5. Calendário

- **Goiás (Mapa Goiano):** LPG em set–out/2023 (prazo 16/10/2023); Goiânia LPG em out–nov/2023; prefeituras do interior em out–dez (2023 e 2024); Goyazes Excepcionais abre em jan e fecha entre abr e ago; Cine Goiás Itinerante abre em dez/ago.
- **MinC (nacional):** Cultura Viva em set–out (2023: 01/09–16/10; 2024: Rádios Comunitárias set–out; 2026: Pontões 02/10–30/10); prêmios em out–dez; intercâmbio e mercados em mai–ago; CEUs e Inova Cultura em nov–jan.
- **Municípios (PNAB ciclo 2):** mar–abr e jun–jul de 2026; set–out de 2026 (BA).
- **Pico anual:** set a dez. O segundo pico é mar a jul, nos anos de PNAB.

## 6. Conselho de 7 lentes

1. **Extremamente pessimista — Dra. Helena Kowalski (chief engineer, rabugenta e minuciosa):** "A rota é `None`. O motor depende de uma instância (Mapa Goiano) que a própria Secult abandonou para os editais grandes: PNAB foi para o Baru e o Goyazes regular para outro sistema. Das 19 sementes, 12 são lixo (testes, prestação de contas, anúncio de terapeuta). Todos os `link_oficial` apontam para o agregador. O painel diz 'satisfatório' e está medindo o lixo."
2. **Pessimista — Prof. Ricardo Amaral (pós-doc em Python, cético com dados):** "Prazo 2100/2111 é usado como 'sem prazo' e o motor grava como data. Não há deduplicação entre instâncias nem entre etapas do mesmo edital (inscrição, recurso, contrarrazão, prestação de contas têm IDs diferentes). `isVerified=EQ(1)` dá erro 500 na nacional. E `owner.name` expõe pessoas físicas — risco LGPD se for armazenado."
3. **Levemente pessimista — Marta Okonkwo (staff engineer, pragmática):** "A API é boa, mas `site` vem null. Para o livro nascer com URL oficial, o motor precisa de um mapa 'dono → site oficial' (SCDC → gov.br/cultura/…/editais; Secult GO → goias.gov.br/cultura; Goiânia → goiania.go.gov.br/secult). Sem isso, tudo vira aguardar_fonte."
4. **Neutro — Eng. Paulo Shimizu (CTO de big tech, mediador):** síntese abaixo.
5. **Levemente otimista — Profa. Lúcia Barreto (pós-doc, foco em dados abertos):** "A API é pública, sem login e sem robots restritivo, aceita filtro `GTE` de prazo, ordenação e paginação. Uma chamada por instância traz 3 anos de histórico com datas confiáveis. É a fonte mais barata do pacote."
6. **Otimista — Diego Ventura (staff engineer, entusiasta):** "A rede nacional concentra o Cultura Viva do MinC, que é o programa mais aderente a uma associação de bairro. Hoje mesmo abriu a 2ª edição dos Pontões (até 30/10). E o Cadastro Nacional de Pontos de Cultura é porta de entrada permanente para a A.M.C."
7. **Extremamente otimista — Dr. Ana Valéria Teixeira (chief engineer, visionária):** "Com as rotas da API em 2–6 instâncias, o filtro por tipo e dono, e o cruzamento com o gov.br, este motor vira o radar oficial de cultura do Eldorado: todos os ciclos PNAB municipais do país, o Cultura Viva e o histórico para prever o calendário. O ganho ideal é ver o edital no dia em que abre."

### Síntese do neutro (Paulo Shimizu)

**Decisão:** manter o motor, **trocar a rota `None` pela API REST** do Mapas (GO + nacional) e **rebaixar o status** de "satisfatório" para "**parcial**". O Mapa Goiano não cobre mais a PNAB GO (Baru) nem a PNAB Goiânia. Essas fontes devem virar motores próprios ou ser monitoradas pelas páginas oficiais (goias.gov.br/cultura/pnab, goiania.go.gov.br/secult/editais).

**Parâmetros de qualidade:**
- ≥ 90% dos itens com `registrationTo` válido (prazo ≥ 2100 = sem_data);
- ruído ≤ 20% (testes, prestação de contas, recurso, anúncios de PF);
- 100% dos livros com URL fora do domínio Mapas, ou acao = aguardar_fonte;
- zero nome de pessoa física armazenado;
- latência ≤ 24 h entre a publicação no Mapas e a captura;
- revisão trimestral de cobertura (que órgão de GO saiu do Mapas).

**Riscos e mitigação:**
- **R1** Migração de órgãos para outros sistemas (Baru, Salic). Mitigação: checagem mensal das páginas oficiais de editais e alerta quando uma instância ficar 90 dias sem edital de órgão público.
- **R2** Ruído de usuários. Mitigação: filtro por `type` (Edital, Concurso, Programa) + léxico de exclusão + lista de donos institucionais.
- **R3** Mudança de versão da API (v5 → v7) e erro 500 em filtros. Mitigação: testar o contrato a cada execução, usar só `GTE`/`IN`/`@page` e cair para `@count` + paginação.
- **R4** LGPD. Mitigação: nunca selecionar `owner.name`; usar só `ownerEntity.name` quando `@entityType` for órgão ou entidade.
- **R5** Prazos-sentinela (2100/2111). Mitigação: normalizar para sem_data.
- **R6** Página SPA sem conteúdo. Mitigação: ler só pela API, nunca pelo HTML.

## 7. Melhorias do motor

1. **Rota:** substituir `None` por `https://<instância>/api/opportunity/find?@select=id,name,registrationFrom,registrationTo,createTimestamp,type,ownerEntity.name,shortDescription,registrationCategories&@order=registrationTo%20DESC&@limit=100&@page=N&registrationTo=GTE(<hoje-30d>)` para `mapagoiano.cultura.go.gov.br` e `mapa.cultura.gov.br`; depois incluir PA, ES e outras.
2. **Filtro de ruído:** excluir nomes com "teste", "prestação de conta", "recurso", "contrarrazão", "monitoramento", "formulário", "questionário", "importação"; manter `type.name` ∈ {Edital, Concurso, Programa, Prêmio}, ou dono institucional.
3. **Léxico de interesse para OSC:** "Cultura Viva", "Ponto de Cultura", "Pontão", "OSC", "sem fins lucrativos", "PNAB", "Aldir Blanc", "Paulo Gustavo", "Goyazes", "Termo de Compromisso Cultural", "Termo de Execução Cultural".
4. **Prazo-sentinela:** registrationTo ≥ 2100 → estado sem_data; registrationTo < hoje → encerrado_arquivar.
5. **Link oficial:** tabela dono → site oficial (SCDC/SAv/SEFLI/SEEC → `gov.br/cultura/pt-br/assuntos/editais/…`; Secult GO → `goias.gov.br/cultura/editais/`; Goyazes → `goias.gov.br/cultura/programa-goyazes/`; SECULT Goiânia → `goiania.go.gov.br/secult/`). Sem correspondência → aguardar_fonte.
6. **Deduplicação:** chave = (instância, id); agrupar etapas do mesmo edital por número do edital no título (ex.: "Edital nº 09/2023") e por dono.
7. **Cadência:** diária na nacional (tem pico set–dez) e semanal no Mapa Goiano; varredura histórica trimestral com `GTE(hoje-3 anos)`.
8. **Histórico:** gravar os 345 registros brutos (61 GO + 284 nacional) como base de previsão de calendário; ciclos Cultura Viva em set–out e PNAB municipal em mar–jul.
9. **Cobertura de Goiás:** criar ou ligar motores para a PNAB GO (goias.gov.br/cultura/pnab + Sistema Baru, só a página pública) e para a SECULT Goiânia (`/secult/editais/`), porque saíram do Mapa Goiano.
10. **LGPD:** retirar `owner` do `@select`; aceitar `ownerEntity` só quando o tipo for agente coletivo ou órgão.
11. **Valor:** a API não traz valor; buscar no PDF/página oficial na fase de enriquecimento.

## 8. O que não foi confirmado e por quê

- **Valores** de quase todos os editais: a API e as páginas SPA não trazem valor; os PDFs não foram abertos (limite de chamadas).
- **Site oficial** de prefeituras do interior (Alto Paraíso, Uruaçu, municípios de BA/RS/MG/SC/SP) e de várias chamadas do MinC (Pontões 2026, Ciclos de Saberes, Inova Cultura, Teia, Rádios Comunitárias, Retomada RS, MICBR, Mobilidade 2024): não confirmados → aguardar_fonte. A 2ª edição dos Pontões (11685, aberta até 30/10/2026) não apareceu em `gov.br/cultura/.../inscricoes-abertas`; a inscrição oficial é no próprio Mapa da Cultura do MinC. **Prioridade** para confirmar a página gov.br.
- **Datas e valores da PNAB Goiás 2026 e da PNAB Goiânia 2024:** as páginas oficiais listam os editais e a situação ("resultado final", "inscrições encerradas"), mas não trazem datas no texto → prazo "".
- **Prazo da semente PA 2472** (2026-10-02): mantido do indício; a página abriu sem datas (SPA) e a API do PA não foi consultada.
- **Instância `mapas.cultura.gov.br`:** não acessada (o WebFetch recusou o robots.txt por tamanho).
- **Outras instâncias estaduais** (PA, ES, CE, SP etc.): não varridas por completo (limite de ~40 chamadas).
- **Listagem gov.br "abertos" desatualizada:** MICSUL (encerrou 12/08/2026) e Rouanet Centro-Oeste (encerrou 13/08/2026) ainda aparecem como abertos; tratei pelas datas.
- Os 41 itens nacionais de particulares (oficinas, shows, consultorias) e os testes **não** entraram nos livros.
