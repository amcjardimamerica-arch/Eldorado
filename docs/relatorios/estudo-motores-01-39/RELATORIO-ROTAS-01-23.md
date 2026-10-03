# Relatório de auditoria das rotas — motores 01 a 23

Data: 2026-10-02 · Base: `/home/claude/m39/rotas_01_39.txt` (seções 01 a 23) · Método: WebFetch a partir de ambiente fora do Brasil, no máximo ~3 tentativas por rota, robots.txt respeitado, sem login e sem formulários.

Legenda das respostas: **sim** = respondeu com conteúdo útil · **JS** = página carrega a lista por JavaScript/AJAX (HTML vem vazio) · **IP/Brasil** = recusa, desconexão ou tempo esgotado típico de bloqueio de IP estrangeiro (precisa de coleta local, no Brasil) · **robots** = robots.txt proíbe ou não pôde ser lido (a ferramenta não prossegue) · **CAPTCHA** = verificação anti-robô (não contornada).

Ressalva importante: alguns domínios que falharam aqui (ex.: in.gov.br) aparecem no sistema com coleta "nuvem" e achados de hoje. A nuvem do Eldorado não é este ambiente; o que falhou aqui deve ser lido como "não confirmável deste ponto", não como prova de defeito.

## Tabela-resumo

| nº | motor | rotas | respondem da nuvem (aqui) | achados | diagnóstico |
|---|---|---|---|---|---|
| 01 | do-goiania | 4 | 3 (1 só genérica) | 2 | FUNCIONA PARCIAL |
| 02 | do-goias | 6 | 6 | 121 | FUNCIONA |
| 03 | dou | 4 | 0 (servidor desconecta) | 30 | BLOQUEADA NA NUVEM (aqui); funciona no sistema |
| 04 | camara-goiania-pl | 2 | 0 | 0 | BLOQUEADA NA NUVEM / ROTA PARCIAL |
| 05 | alego-pl | 2 | 1 (home genérica) | 17 | ROTA ERRADA |
| 06 | congresso-nacional | 7 | 7 | 0 | FUNCIONA PARCIAL (APIs sem filtro) |
| 07 | judiciario-tjgo | 5 | 2 | 0 | NUNCA RODOU (rotas parcialmente erradas) |
| 08 | mpgo-destinacao | 22 (+URL principal) | 19 | 0 | NUNCA RODOU / ROTA ERRADA (rotas copiadas do MPT/MPF; sem rota MP-GO) |
| 09 | mptgo-destinacao | 22 | 19 | 0 | NUNCA RODOU (rota principal exige JS) |
| 10 | mpu-destinacao | 22 | 19 | 0 | NUNCA RODOU |
| 11 | judiciario-cnj | 5 (as mesmas do 07) | 2 | 0 | NUNCA RODOU / BLOQUEADA (CNJ 403) |
| 12 | dj-trf1-go | 2 | 0 (robots.txt proíbe) | 0 | BLOQUEADA (robots) / ROTA ERRADA (home) |
| 13 | prefeituras-50-go | 3 (1 é arquivo) | 0 | 0 | FUNCIONA PARCIAL / ROTA ERRADA |
| 14 | estaduais-go-gov | 0 | — | 0 | SEM ROTA |
| 15 | pncp-api | 3 | 2 | 386 | FUNCIONA |
| 16 | salic | 4 (+URL principal) | 2 | 105 | FUNCIONA PARCIAL (rotas secundárias quebradas) |
| 17 | cnpq-extensao | 3 | 0 (404 + 2 CAPTCHA) | 0 | ROTA ERRADA |
| 18 | gife | 2 | 2 | 11 | FUNCIONA |
| 19 | empresas-editais-incentivados | 3 (1 arquivo, 1 vazia) | 1 | 0 | ROTA ERRADA (URL principal é empresa de SC) |
| 20 | motor-gife (incentivos) | 3 (1 vazia) | 1 | 60 | FUNCIONA PARCIAL |
| 21 | motor-patrocinio | 3 (1 vazia) | 1 | 3 | FUNCIONA PARCIAL (DuckDuckGo não respondeu) |
| 22 | piloto-aberto | 3 (1 vazia) | 0 | 439 | FUNCIONA PARCIAL (busca DuckDuckGo não respondeu aqui) |
| 23 | piloto-interceptador | 0 (arquivo local) | — | 262 | SEM ROTA (motor interno); dados locais divergem |

---

### 01 do-goiania — Diário Oficial do Município de Goiânia

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Lista oficial das edições (Casa Civil) | https://www.goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp?ano=2026 | diario | **sim** — lista as edições 8875 (01/10/2026), 8874 (30/09), 8873 (29/09), PDFs | sim |
| Querido Diário — Goiânia | https://api.queridodiario.ok.org.br/gazettes?territory_ids=5208707 | api | **não** — falha de TLS (handshake) ao ler robots.txt | domínio antigo |
| SMC — editais PNAB | https://www.goiania.go.gov.br/secretaria/secretaria-municipal-de-cultura/ | secretaria | **sim**, mas página institucional (estrutura/competências), sem editais | não |
| Conselhos Municipais | https://www.goiania.go.gov.br/conselhos-municipais/ | conselho | **sim**, mas a lista de conselhos não vem no HTML (filtro por JS) | não (genérica/JS) |

**Onde pesquisa:** goiania.go.gov.br (lista do Diário, secretaria de cultura, conselhos) e a API do Querido Diário.

**Resultado no sistema:** ativo — captando; 2 achados; luz verde (2 achados hoje); última leitura 2026-10-02 14:31.

**Diagnóstico:** FUNCIONA PARCIAL — a rota do Diário é boa (e o goiania.go.gov.br respondeu do exterior); Querido Diário inacessível no domínio antigo; as rotas de cultura e conselhos apontam para páginas institucionais.

**Correção:**
- Trocar a rota da SMC por `https://www.goiania.go.gov.br/secult/editais/` (verificada: lista Chamada Pública 02/2025 de 02/09/2025, 02/2022 e Edital 01/2022) e acrescentar `https://www.goiania.go.gov.br/secult/pnab-2024/` (link verificado na página `/secult`).
- Querido Diário: o domínio `queridodiario.org.br` respondeu (home), `queridodiario.ok.org.br` deu tempo esgotado. O endereço da API (`api.queridodiario.org.br` ou `queridodiario.org.br/api`) **não pôde ser confirmado** daqui (tempo esgotado). Testar no computador do titular antes de trocar.
- Conselhos: a página exige JS; manter só se a coleta local usar navegador, ou substituir quando houver URL específica dos fundos (CMDCA/CMAS) verificada.

### 02 do-goias — Diário Oficial do Estado de Goiás

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Busca de texto completo | https://diariooficial.abc.go.gov.br/busca/busca/buscar/query/0/ | diario | **sim** — JSON (Elasticsearch), mas 0 resultados com o literal `query` | parcialmente: o termo vai no caminho |
| Edições do dia | https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/ | diario | **sim** — `/2026-10-01.json` retorna edição 24877 (80 págs.) + suplemento; `/2026-10-02.json` = "Edição não existente" (ainda não publicada no momento) | sim |
| SECULT-GO — Chamamentos 2026 | https://goias.gov.br/cultura/chamamentos-publicos-2026-lei-13-019-14/ | secretaria | **sim** — Chamamentos 01/2026 e 02/2026 | sim |
| SECULT-GO — Chamamentos (geral) | https://goias.gov.br/cultura/chamamentos-publicos-secult/ | secretaria | **sim** — índice 2021–2026 | sim |
| SEDS — API de posts | https://goias.gov.br/social/wp-json/wp/v2/posts | secretaria | **sim** — JSON, mas sem filtro vem agenda/nomeações | parcial |
| SEEL — Chamamento público | https://goias.gov.br/esporte/chamamento-publico/ | secretaria | **sim** — índice com chamamento 2022 e Serra Dourada | sim (pouco movimento) |

**Onde pesquisa:** diariooficial.abc.go.gov.br (busca e edições) e goias.gov.br (SECULT, SEDS, SEEL).

**Resultado no sistema:** ativo — captando; 121 achados; luz verde (5 hoje); última 2026-10-02 14:33.

**Diagnóstico:** FUNCIONA.

**Correção:**
- Busca: o termo entra no caminho — `https://diariooficial.abc.go.gov.br/busca/busca/buscar/chamamento/0/` retornou 12.366 resultados (verificado). Conferir se o código substitui `query`; se não, trocar.
- SEDS: acrescentar `?search=chamamento` — `https://goias.gov.br/social/wp-json/wp/v2/posts?search=chamamento` retornou "Edital de chamamento público 001/2026 – Socioeducativo" (14/09/2026), "Edital/Chamamento Público 2026" (27/08/2026) etc.
- Opcional: acrescentar `https://goias.gov.br/cultura/wp-json/wp/v2/posts?search=edital` (verificado; editais SECULT de 24 a 29/09/2026).

### 03 dou — Diário Oficial da União

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| DOU Seção 1 | https://www.in.gov.br/leiturajornal?secao=do1 | diario | **não** — servidor desconecta (nem o robots.txt responde) | sim |
| DOU Seção 3 | https://www.in.gov.br/leiturajornal?secao=do3 (testado também com `data=02-10-2026`) | diario | **não** — idem | sim |
| DOU extra | https://www.in.gov.br/leiturajornal?secao=do1e | diario | não testada à parte (mesmo domínio, mesma desconexão) | sim |
| Busca semanal | https://www.in.gov.br/consulta/-/buscar/dou?q=chamamento&s=todos&exactDate=semana | diario | **não** — idem | sim |

**Onde pesquisa:** in.gov.br (Leitura do Jornal, seções 1, 3 e extra; busca).

**Resultado no sistema:** ativo — captando; 30 achados; luz verde (2 hoje); última 2026-10-02 14:34.

**Diagnóstico:** BLOQUEADA NA NUVEM deste ambiente (o servidor encerra a conexão com IP estrangeiro); no sistema real está funcionando.

**Correção:** nenhuma de URL. Manter; como reserva, cadastrar coleta local no computador do titular para os dias em que a nuvem do sistema também for recusada.

### 04 camara-goiania-pl — Câmara Municipal de Goiânia

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| SUAP — consulta pública | https://suap.camaragyn.go.gov.br/camara/consulta_publica/ | legislativo | **não** — certificado TLS com cadeia incompleta | sim (consulta de processos) |
| Portal (Plone) — search_rss | https://www.goiania.go.leg.br/search_rss | noticias | **não** — erro 502; com `?SearchableText=utilidade+publica`, tempo esgotado | sim, mas instável |

**Onde pesquisa:** suap.camaragyn.go.gov.br e goiania.go.leg.br. A home `https://www.goiania.go.leg.br/` respondeu (notícias, pauta de sessões).

**Resultado no sistema:** ativo, sem achados; 0 achados; luz cinza (não rodou hoje); última 2026-09-30 09:34; coleta local.

**Diagnóstico:** BLOQUEADA NA NUVEM (SUAP) e ROTA INSTÁVEL (search_rss 502). Nunca gerou achado.

**Correção:** manter a coleta local. Acrescentar como reserva `https://www.goiania.go.leg.br/processo-legislativo/pautas-de-sessoes` (link verificado na home) para ler pautas, já que o search_rss falhou.

### 05 alego-pl — Assembleia Legislativa de Goiás

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Proposições da ALEGO | https://portal.al.go.leg.br/ | legislativo | **sim**, mas é a home institucional | não — a consulta de proposições fica em alegodigital.al.go.leg.br |
| LOA e emendas — SEFAZ/SEGPLAN | https://www.economia.go.gov.br/ | orcamento | **não** — certificado não vale para `www.economia.go.gov.br` (nome errado) | não — domínio antigo |

**Onde pesquisa:** portal.al.go.leg.br (home) e economia.go.gov.br.

**Resultado no sistema:** ativo — captando; 17 achados; luz verde (sem dados novos); última 2026-10-01 21:57.

**Diagnóstico:** ROTA ERRADA (as duas apontam para homes; a segunda para domínio desativado).

**Correção:**
- Trocar `https://www.economia.go.gov.br/` por `https://goias.gov.br/economia/orcamento-geral-do-estado/` (verificado; remete à LOA vigente em `https://transparencia.go.gov.br/orcamento-e-planejamento-pecas`). Não há página de emendas impositivas nessa seção.
- Proposições: a home aponta para `https://alegodigital.al.go.leg.br` (Consulta Legislativa), que **não respondeu daqui** (ConnectError) — testar pela coleta local e, confirmando, usar como rota.

### 06 congresso-nacional — Congresso Nacional

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| CMO — LOA 2027 | https://www.congressonacional.leg.br/web/orcamento/acompanhe/orcamento-anual/-/loa/2027 | orcamento | **sim** — etapa "Apresentação de emendas": não iniciada | sim |
| CMO — comunicados | https://www.congressonacional.leg.br/web/cmo/comunicados | orcamento | **sim** — 02/10/2026 "Matérias novas… e prazo de emendas"; 30/09 "LOA 2027 – Instruções do Lexor" | sim |
| Câmara — API proposições | https://dadosabertos.camara.leg.br/api/v2/proposicoes | api | **sim**, mas sem parâmetros devolve PLs de 2003–2004 | parcial (falta filtro) |
| Senado — API /processo | https://legis.senado.leg.br/dadosabertos/processo | api | **sim**, mas sem parâmetros devolve MPVs de 2001 e vetos de 2008 | parcial (falta filtro) |
| Câmara — RSS | https://www.camara.leg.br/noticias/rss/ultimas-noticias | noticias | **sim** (01/10/2026) | genérica (notícias) |
| Senado — RSS | https://www12.senado.leg.br/noticias/feed/todasnoticias/rss | noticias | **sim** (01/10/2026) | genérica (notícias) |
| Senado — convocações públicas | https://www6g.senado.leg.br/transparencia/licitacoes-e-contratos/sadcon/convocacoes-publicas | chamamento | **sim** — 1/2026 (13/01/2026), 4/2025, 2/2025 (não são para OSC) | sim |

**Onde pesquisa:** congressonacional.leg.br (CMO), dadosabertos.camara.leg.br, legis.senado.leg.br, camara.leg.br, senado.leg.br.

**Resultado no sistema:** ativo, sem achados; 0 achados; luz verde (sem dados novos); última 2026-10-02 14:34.

**Diagnóstico:** FUNCIONA PARCIAL — todas respondem, mas as APIs sem filtro de data trazem material antigo, o que explica zero achados úteis.

**Correção:**
- Câmara: `https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataApresentacaoInicio=2026-09-25&dataApresentacaoFim=2026-10-02&ordem=DESC&ordenarPor=id&itens=20` (verificado: PL 5520/2026, 5519/2026, 5514/2026).
- Senado: `https://legis.senado.leg.br/dadosabertos/processo?dataInicioApresentacao=2026-09-25&dataFimApresentacao=2026-10-02` (verificado: MPV 1393/2026, PL 5481/2026, PL 5503/2026).
- Vigiar o comunicado da CMO de 02/10/2026 sobre prazo de emendas da LOA 2027 (é o gatilho para emendas parlamentares a OSC).

### 07 judiciario-tjgo — TJ-GO

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Agência de Notícias (RSS) | https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss | tribunal | **sim** — RSS 2.0 de 02/10/2026; nenhum item de prestação pecuniária hoje | sim (genérica, mas é onde os editais são noticiados) |
| PDF do edital | https://www.tjgo.jus.br/files/ | tribunal | **não** — redirecionamentos em excesso | não — é prefixo, não página |
| CGJ/GO — Banco de Projetos Sociais | https://corregedoria.tjgo.jus.br/basesocial | secretaria | **sim** — página de cadastro/login; sem editais; link para "Busca pública de Projetos" | parcial (é cadastro, não edital) |
| Portal do CNJ — busca | https://www.cnj.jus.br/?s=presta%C3%A7%C3%A3o+pecuni%C3%A1ria+edital | referencia | **403** (o site inteiro do CNJ deu 403, inclusive a home) | sim |
| PNCP — app/editais | https://pncp.gov.br/app/editais | vetor | **sim**, mas é SPA Angular — **exige JavaScript**; HTML sem editais | não — usar a API |

**Onde pesquisa:** tjgo.jus.br, corregedoria.tjgo.jus.br, cnj.jus.br, pncp.gov.br.

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca.

**Diagnóstico:** NUNCA RODOU; duas rotas não servem para coleta (prefixo `/files/` e SPA do PNCP).

**Correção:**
- Remover `https://www.tjgo.jus.br/files/` como rota (é só o prefixo dos PDFs; o motor deve segui-los a partir do RSS).
- Trocar `https://pncp.gov.br/app/editais` pela API de busca `https://pncp.gov.br/api/search/?q=chamamento&tipos_documento=edital&pagina=1` (verificado: JSON, 68.725 itens) ou deixar só no motor 15.
- CNJ: 403 a partir do exterior — passar para coleta local.

### 08 mpgo-destinacao — MP-GO — Programa Destina

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| (URL principal) MP-GO Destina, edital 02/2024 | https://www.mpgo.mp.br/portal/conteudo/destina-destinacao-articulada-de-acordos-edital-n-02-2024 | — | **não** — tempo esgotado (home também falhou) | sim, mas **não está entre as 22 rotas** |
| MPT-GO — editais de destinação | https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens | tabela_mpt | **sim**, mas tabela "Carregando dados do servidor" — **exige JS/AJAX** | sim |
| MPT-GO — entidades assistenciais | https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais | lista_habilitadas | **sim**, tabela por AJAX (vazia no HTML) | sim (lista de habilitadas) |
| MPT-GO — notícias | https://www.prt18.mpt.mp.br/informe-se/noticias-do-mpt-go | listagem_html | **sim** — 01/10, 23/09, 22/09/2026 | genérica (notícias) |
| MPT — search_rss | https://mpt.mp.br/search_rss?SearchableText=edital+cadastramento+entidades&sort_on=Date&sort_order=reverse | rss | **sim** — 27/08/2026 "Cadastro de órgãos e entidades… reversões" | sim |
| MPT — PGT RSS | https://mpt.mp.br/pgt/noticias/RSS | rss | **sim**, mas itens mais novos de julho/2026 (feed parado) | genérica e desatualizada |
| MPF PR-GO — notícias | https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias | listagem_html | **sim** — 23/09, 15/09, 11/09/2026 | genérica |
| MPF PR-GO — bens para doação | https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao | listagem_html | **sim** — Edital de Doação de Bens 01-2025 + históricos | sim (doação de bens móveis) |
| MPF PR-GO — transparência | https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia | listagem_html | **sim** — índice | genérica |
| MPF PR-GO — notícia do cadastro | https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-… | listagem_html | **sim** — notícia de 09/10/2025, sem prazo; link do edital `mpf.mp.br/docs/edital-de-chamamento-para-recebimento-de-bens-e-valores` dá **404** | página fixa (não é listagem) |
| MPF — busca nacional | https://www.mpf.mp.br/search?SearchableText=edital+chamamento+recebimento+bens+valores | listagem_html | **sim** — 292 itens (PR-SE 1/2025, PR-RJ 05/2025, PR-RS 11/2025) | sim |
| MPF PR-BA (modelo) | https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores | listagem_html | **sim** — Edital PRBA nº 92 | sim (fora de GO; modelo) |
| MPF — serviços | https://www.mpf.mp.br/servicos/mpf-servicos | listagem_html | **sim**, sem serviço de cadastro de entidades | não |
| MPDFT — tag medidas alternativas | https://www.mpdft.mp.br/portal/index.php/tags/medidas-alternativas | listagem_html | **sim** — 18/09/2026 "MPDFT habilita 51 instituições para cadastro de destinação de recursos" | sim |
| MPDFT — TACs | https://www.mpdft.mp.br/transparencia/index.php?item=tac | listagem_html | **sim** — TACs até 06/08/2026 | indireta |
| MPDFT — notícias 2026 | https://www.mpdft.mp.br/portal/index.php/comunicacao-menu/sala-de-imprensa/noticias/noticias-2026-completo | listagem_html | **sim** — 02/10/2026 | genérica |
| MPM — busca | https://www.mpm.mp.br/?s=presta%C3%A7%C3%A3o+pecuni%C3%A1ria | listagem_html | **sim** — só notícias de condenações (2022–2026) | não |
| MPU — sitemap | https://www.mpu.mp.br/sitemap | listagem_html | **sim** — mapa institucional | não |
| MJ — Direitos Difusos (FDD) | https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/direitos-difusos | listagem_html | **sim** — índice | genérica |
| MJ — CFDD seleção em andamento | …/direitos-difusos/selecao-em-andamento | estado_pagina | **sim** — "Não há" (atualizada em 08/07/2026) | sim (sinal de abertura) |
| MJ — seleções anteriores | …/direitos-difusos/selecoes-anteriores | listagem_html | **sim** — 2015 a 2023 | histórico |
| MJ — anexos de atas | …/direitos-difusos/reunioes-do-cfdd/anexos-atas | listagem_html | **sim** — calendário 2026 e atas | indireta |
| MJ — convênios e transferências | …/direitos-difusos/convenios-e-transferencias | listagem_html | **sim** — índice | genérica |

**Onde pesquisa:** prt18.mpt.mp.br, mpt.mp.br, mpf.mp.br, mpdft.mp.br, mpm.mp.br, mpu.mp.br, gov.br/mj. **Não pesquisa em mpgo.mp.br**, que é o próprio objeto do motor.

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca; agenda a cada 30 dias.

**Diagnóstico:** NUNCA RODOU e ROTA ERRADA — as 22 rotas são cópia idêntica das dos motores 09 e 10; não há nenhuma rota do MP-GO, e o domínio mpgo.mp.br não respondeu do exterior.

**Correção:** substituir as 22 rotas pelas do próprio MP-GO: a URL principal (`…/destina-destinacao-articulada-de-acordos-edital-n-02-2024`) e a página de notícias do portal, com **coleta local** (mpgo.mp.br recusou daqui). Deixar MPT/MPF/MPDFT/MJ só nos motores 09 e 10, para não ler três vezes as mesmas páginas.

### 09 mptgo-destinacao — MPT-GO — editais de 5 dias

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| As mesmas 22 rotas do motor 08 | (ver tabela do 08 — resultados reaproveitados) | — | 19 respondem; as 2 tabelas do PRT18 exigem JS | — |

Rotas próprias do objeto: `prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens` (**sim, mas tabela por AJAX**), `…/entidades-assistenciais` (**AJAX**), `…/noticias-do-mpt-go` (**sim**), `mpt.mp.br/search_rss…` (**sim**, item de 27/08/2026).

**Onde pesquisa:** a mesma lista do 08; o que interessa ao objeto é o prt18.mpt.mp.br e o mpt.mp.br.

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca; agenda diária 07:53 e 16:23.

**Diagnóstico:** NUNCA RODOU; a rota principal responde, mas a tabela de editais é carregada por JavaScript — um coletor só de HTML verá a tabela vazia.

**Correção:** (1) reduzir a lista às rotas MPT (prt18 + mpt.mp.br search_rss); (2) para a tabela do PRT18, coletar com navegador (coleta local com Playwright) ou descobrir o endereço AJAX que alimenta a tabela (não identificado daqui — não proponho URL não verificada); (3) retirar `mpt.mp.br/pgt/noticias/RSS` (feed parado em julho/2026).

### 10 mpu-destinacao — MPU (MPF, MPDFT, MPM, MPT nacional, CNMP, FDD)

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| As mesmas 22 rotas do motor 08 | (ver tabela do 08 — resultados reaproveitados) | — | 19 respondem | — |

Úteis para o objeto: busca nacional do MPF (292 itens de editais de destinação), PR-GO bens para doação, MPDFT tag medidas alternativas (habilitação de 51 instituições em 18/09/2026), CFDD seleção em andamento ("Não há"). Pouco úteis: MPF serviços, MPM busca, MPU sitemap, MJ convênios.

**Onde pesquisa:** mpf.mp.br, mpdft.mp.br, mpm.mp.br, mpu.mp.br, gov.br/mj (e também as do MPT, repetidas).

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca.

**Diagnóstico:** NUNCA RODOU; a maioria das rotas responde da nuvem — o problema é de agenda/execução, não de rota.

**Correção:** retirar as rotas do MPT (ficam no 09); retirar `mpu.mp.br/sitemap`, `mpf.mp.br/servicos/mpf-servicos` e a busca do MPM (não trazem editais); tirar a rota da notícia do MPF-GO de 2025 (link do edital dá 404); manter a busca nacional do MPF e a página "seleção em andamento" do FDD como sinalizador. Verificar por que o motor nunca rodou (agenda diária 16:23 configurada).

### 11 judiciario-cnj — CNJ — prestações pecuniárias

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| As mesmas 5 rotas do motor 07 | (resultados reaproveitados do 07) | — | TJGO RSS sim; CGJ basesocial sim; `/files/` falha; CNJ 403; PNCP app exige JS | — |
| (URL principal) https://www.cnj.jus.br/ | | — | **403** | sim |

**Onde pesquisa:** os mesmos domínios do 07; a única rota do CNJ dá 403 daqui.

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca.

**Diagnóstico:** NUNCA RODOU / BLOQUEADA NA NUVEM (CNJ 403); rotas duplicadas com o 07.

**Correção:** deixar no 11 só a busca do CNJ e rodá-la pela coleta local; tirar do 11 as rotas do TJGO (ficam no 07).

### 12 dj-trf1-go — Diário da Justiça Federal — SJGO

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| DJF — SJGO | https://www.trf1.jus.br/sjgo/ | diario | **robots.txt proíbe** a leitura (nem o próprio robots.txt pôde ser exibido) | não — home da seção, não o Diário |
| Editais de prestação pecuniária — TRF1 | https://www.trf1.jus.br/ | secretaria | **robots.txt proíbe** | não — home do tribunal |

**Onde pesquisa:** trf1.jus.br (homes).

**Resultado no sistema:** ativo, sem achados; 0 achados; luz cinza (não rodou hoje); última 2026-09-30 09:35; coleta local.

**Diagnóstico:** BLOQUEADA (robots.txt) e ROTA ERRADA (duas homes, nenhuma página de editais).

**Correção:** como o robots.txt do TRF1 proíbe robôs, **suspender a coleta automática** (mesmo a local) até se confirmar, pelo titular, o que o robots permite; acompanhar manualmente ou por outra fonte (ex.: editais republicados no PNCP/DOU). Não há URL substituta verificada.

### 13 prefeituras-50-go — Prefeituras das 25 maiores cidades de Goiás

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Portal da prefeitura | config/municipios_maiores.json | prefeitura | arquivo de configuração, não URL — não testável aqui | — |
| Querido Diário | https://queridodiario.ok.org.br/ | diario | **não** — tempo esgotado (home); `queridodiario.org.br` respondeu | não — home, não API; domínio antigo |
| PNCP | https://pncp.gov.br/ | vetor | **não** — erro de leitura (a home é SPA) | não — home |
| (URL principal) https://www.goiania.go.gov.br/ | | — | **sim** — home; sem link direto de editais | não |

**Onde pesquisa:** portais das prefeituras listados no JSON, Querido Diário e PNCP (homes).

**Resultado no sistema:** lendo, sem editais reconhecidos; 0 achados; luz vermelha (1 página com falha); última 2026-10-01 12:03.

**Diagnóstico:** FUNCIONA PARCIAL / ROTA ERRADA — as rotas de apoio são homes, e a URL principal é a home de Goiânia.

**Correção:** trocar `https://pncp.gov.br/` por `https://pncp.gov.br/api/consulta/v1/contratacoes/proposta?dataFinal=20270214&codigoModalidadeContratacao=12&uf=GO&pagina=1` (verificado: 279 registros de credenciamento em GO, inclusive municípios); trocar a URL principal de Goiânia por `https://www.goiania.go.gov.br/secult/editais/`; usar o catálogo de rotas das 25 prefeituras já preparado no projeto (CATALOGO-ROTAS-25-PREFEITURAS-GO) em vez do portal genérico; Querido Diário só depois de confirmar o endereço da API pela coleta local.

### 14 estaduais-go-gov — Oportunidades estaduais de Goiás

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| (nenhuma rota configurada) | URL principal https://goias.gov.br/ | — | **sim** — home institucional, sem link de editais | não |

**Onde pesquisa:** nenhum lugar (sem rotas, sem "como funciona", coleta = None).

**Resultado no sistema:** sem leitura ainda; 0 achados; luz cinza; última: nunca.

**Diagnóstico:** SEM ROTA.

**Correção:** configurar as APIs WordPress das secretarias, filtradas por termo (verificadas hoje):
- `https://goias.gov.br/social/wp-json/wp/v2/posts?search=chamamento`
- `https://goias.gov.br/cultura/wp-json/wp/v2/posts?search=edital`
- `https://goias.gov.br/wp-json/wp/v2/posts?search=chamamento` (responde, mas mistura notícias gerais)
- páginas de índice `https://goias.gov.br/cultura/chamamentos-publicos-secult/` e `https://goias.gov.br/esporte/chamamento-publico/`.
Atenção para não duplicar com o motor 02, que já lê SECULT/SEDS/SEEL — ou o 14 assume essas rotas e o 02 fica só com o Diário.

### 15 pncp-api — PNCP — API de contratações

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| API — propostas abertas | https://pncp.gov.br/api/consulta/v1/contratacoes/proposta (testada com `dataFinal=20270214&codigoModalidadeContratacao=12&uf=GO&pagina=1`) | api | **sim** — JSON, 279 registros (credenciamentos de Nova Roma, Rio Verde etc.) | sim |
| Busca do portal | https://pncp.gov.br/api/search/ | api | **sim** com `?q=chamamento&tipos_documento=edital&pagina=1` (68.725 itens); com `status`, `ufs` e `ordenacao` juntos deu erro | sim |
| Arquivos do órgão | https://pncp.gov.br/pncp-api/v1/orgaos/ | documento | **503** no prefixo (esperado: só funciona com CNPJ/ano/sequencial) | prefixo, não página |

**Onde pesquisa:** pncp.gov.br (API de consulta, API de busca, arquivos).

**Resultado no sistema:** ativo — captando; 386 achados; luz verde (221 hoje); última 2026-10-02 14:49.

**Diagnóstico:** FUNCIONA — mas o volume (221 em um dia) indica muito ruído: a modalidade 12 (credenciamento) traz serviços de lavagem de veículos, transporte escolar, profissionais de saúde.

**Correção:** nenhuma de URL; apertar o filtro de confirmação (exigir "organização da sociedade civil", "Lei 13.019", "termo de fomento/colaboração") antes de contar como achado.

### 16 salic — SALIC — Lei Rouanet

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| (URL principal) MinC — editais | https://www.gov.br/cultura/pt-br/assuntos/editais | — | **sim** — índice (abertos, em andamento, encerrados) | sim |
| MinC — Lei Rouanet | https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet | secretaria | **sim**, institucional; conteúdo pede autenticação | não |
| Salic | https://salic.cultura.gov.br/ | plataforma | **não** — robots.txt devolve erro 500 | sistema com login (não é fonte de editais) |
| Instrução Normativa | https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet/legislacao | regramento | **404** | rota morta |
| VerSalic | https://versalic.cultura.gov.br/ | listagem | **sim**, mas é aviso de migração para `https://aplicacoes.cultura.gov.br/comparar/salicnet/`, que deu "redirecionamentos em excesso" | rota morta (migrou) |

**Onde pesquisa:** gov.br/cultura, salic.cultura.gov.br, versalic.cultura.gov.br.

**Resultado no sistema:** satisfatória — obtendo editais; 105 achados; luz verde (5 hoje); última 2026-10-02 17:55.

**Diagnóstico:** FUNCIONA PARCIAL — os achados vêm da URL principal; das 4 rotas, 1 é 404 e 1 foi desativada.

**Correção:** trocar a URL principal por `https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas` (verificada: Biblioteca Comunitária é Cultura Viva, MICSUL 2026, Rouanet nas Favelas 2, CNPq/MinC 17/2026); remover a rota `…/lei-rouanet/legislacao` (404) e a do VerSalic (migrado; o novo endereço não abriu daqui).

### 17 cnpq-extensao — CNPq / MCTI / Setec-MEC

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| CNPq — chamadas públicas | https://www.gov.br/cnpq/pt-br/acesso-a-informacao/acoes-e-programas/programas/chamadas-publicas | fundacao | **404** | não — URL morta |
| MCTI | https://www.gov.br/mcti/pt-br | secretaria | **CAPTCHA** (verificação anti-robô); home institucional | não (home) |
| Setec/MEC | https://www.gov.br/mec/pt-br/acesso-a-informacao/institucional/secretarias/secretaria-de-educacao-profissional-e-tecnologica | secretaria | **CAPTCHA** | não (institucional) |

**Onde pesquisa:** gov.br/cnpq, gov.br/mcti, gov.br/mec.

**Resultado no sistema:** lendo, sem editais reconhecidos; 0 achados; luz vermelha (2 páginas com falha); última 2026-10-01 12:04.

**Diagnóstico:** ROTA ERRADA — a rota principal do CNPq morreu (404); as outras duas são institucionais e hoje caem em CAPTCHA.

**Correção:** trocar a rota do CNPq por `https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao` (verificada: Chamadas 30/2026, 32/2026, 29/2026 com prazos). MCTI e MEC: não contornar CAPTCHA; retirar as homes e, se for o caso, buscar as chamadas do MCTI pela página do CNPq (as chamadas MCTI/CNPq aparecem lá).

### 18 gife — GIFE

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| GIFE — API de posts | https://gife.org.br/wp-json/wp/v2/posts | api | **sim** — 28/09/2026 "Confira editais com inscrições abertas entre setembro e outubro" | sim |
| Capta — API de posts | https://capta.org.br/wp-json/wp/v2/posts | api | **sim** — oportunidades com prazo (Baobá até 19/10, LUPPA até 20/10, Aperam até 04/10) | sim |
| (URL principal) https://gife.org.br/editais | | — | **sim** | sim |

**Onde pesquisa:** gife.org.br e capta.org.br (APIs WordPress).

**Resultado no sistema:** satisfatória; 11 achados; luz verde (3 hoje); última 2026-10-02 20:09.

**Diagnóstico:** FUNCIONA.

**Correção:** nenhuma obrigatória; a API do GIFE sem filtro mistura matérias de clima — se o código não filtra por categoria, acrescentar o parâmetro de categoria "Editais".

### 19 empresas-editais-incentivados — FIA, Idoso, LIE, Pronas, Pronon, Goyazes

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Página de editais da empresa (ranking) | biblioteca_alexandria/empresas/ranking_destinacao_tributaria.json | empresa | arquivo interno, não URL | — |
| Portais do terceiro setor | https://captadores.org.br/editais/ | vetor | **sim** — ABCR, 34 páginas; Zurich Incentivo Fiscal 2026 (28/09), MAPFRE 2026 | sim |
| Redes sociais | None | pista | rota vazia | — |
| (URL principal) https://www.portoitapoa.com/ | | — | **sim** — Porto Itapoá, Itapoá/SC; sem página de editais | **não** — empresa de SC, sem editais |

**Onde pesquisa:** o ranking interno de empresas e captadores.org.br.

**Resultado no sistema:** lendo, sem editais reconhecidos; 0 achados; luz vermelha (2 páginas com falha); última 2026-10-01 12:03.

**Diagnóstico:** ROTA ERRADA — a URL principal é a de uma empresa de Santa Catarina sem editais (provável primeiro item do ranking); a única rota web que responde é a ABCR.

**Correção:** trocar a URL principal por `https://captadores.org.br/editais/` (verificada) e revisar o ranking para que cada empresa tenha a URL da sua página de edital/RSE, não a home; retirar a rota "None".

### 20 motor-gife — Incentivos fiscais (base ICMS/RFB/SALIC)

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Maiores contribuintes do ICMS | https://goias.gov.br/economia/os-maiores-contribuintes-do-icms/ | lista | **sim** — 500 maiores, PDFs 2005–2025 (2025 atualizado em 28/01/2026) | sim |
| Site de cada empresa | None | fonte_derivada | rota vazia (derivada) | — |
| Salic | https://salic.cultura.gov.br/ | plataforma | **não** (robots.txt erro 500) — reaproveitado do motor 16 | sistema com login |

**Onde pesquisa:** goias.gov.br/economia (lista ICMS) e Salic.

**Resultado no sistema:** ativo — captando; 60 achados; luz cinza (fora da agenda hoje); última 2026-09-29 00:17; agenda domingo 03:23.

**Diagnóstico:** FUNCIONA PARCIAL — a lista ICMS funciona; a rota do Salic não serve para saber que empresa incentivou o quê (VerSalic migrou).

**Correção:** retirar a rota `salic.cultura.gov.br`; a substituta citada no aviso do VerSalic (`aplicacoes.cultura.gov.br/comparar/salicnet/`) não abriu daqui — testar pela coleta local antes de cadastrar.

### 21 motor-patrocinio — Patrocínio privado (mídia e eventos de Goiás)

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Imprensa | https://www.opopular.com.br/ | imprensa | **tempo esgotado** com `www`; `https://opopular.com.br/` **sim** (home) | genérica (home do jornal) |
| Site do patrocinador | None | fonte_derivada | rota vazia | — |
| Busca DuckDuckGo | https://html.duckduckgo.com/html/?q=patroc%C3%ADnio+evento+cultural+Goi%C3%A2nia+2026 | busca | **não** — erro de leitura (robots.txt permite; o serviço recusou a requisição) | sim (busca) |

**Onde pesquisa:** opopular.com.br e DuckDuckGo HTML.

**Resultado no sistema:** ativo — captando; 3 achados; luz cinza (fora da agenda); última 2026-09-29 00:20.

**Diagnóstico:** FUNCIONA PARCIAL.

**Correção:** trocar `https://www.opopular.com.br/` por `https://opopular.com.br/` (verificado — o `www` deu tempo esgotado; a URL principal do motor já é sem `www`). Busca DuckDuckGo: instável para robôs; manter com tolerância a falha.

### 22 piloto-aberto — Piloto Espião — busca aberta

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| Busca aberta por ângulo sorteado | https://html.duckduckgo.com/html/?q= (testada com a URL principal `?q=edital+organizações+da+sociedade+civil+2026`) | busca | **não** — erro de leitura daqui | sim |
| Site oficial do financiador | None | fonte_derivada | rota vazia (derivada) | — |
| Plataformas não catalogadas | https://html.duckduckgo.com/html/?q=plataforma+editais+terceiro+setor+brasil | busca | **não** — erro de leitura | sim |

**Onde pesquisa:** só DuckDuckGo HTML (e depois os sites que a busca revela).

**Resultado no sistema:** satisfatória; 439 achados; luz vermelha (1 página com falha, 18 achados mesmo assim); última 2026-10-01 12:04.

**Diagnóstico:** FUNCIONA PARCIAL — depende de um único buscador que recusa robôs de forma intermitente (a falha de hoje no sistema é coerente com o que vi).

**Correção:** acrescentar um segundo caminho de descoberta que não dependa do DuckDuckGo, usando fontes já verificadas: `https://captadores.org.br/editais/`, `https://capta.org.br/wp-json/wp/v2/posts`, `https://pncp.gov.br/api/search/?q=chamamento&tipos_documento=edital&pagina=1`.

### 23 piloto-interceptador — Piloto Interceptador — comprova na fonte oficial

| rota | url | tipo | resposta hoje | aponta para o lugar certo? |
|---|---|---|---|---|
| (nenhuma rota web) | URL principal: docs/dados/interceptador.json (arquivo interno) | — | arquivo existe em `/home/claude/Eldorado/docs/dados/interceptador.json` (gravado em 2026-10-01) | — |

**Onde pesquisa:** nas fontes oficiais que os outros motores e o Espião trazem (um alvo por voo); não tem rota própria.

**Resultado no sistema:** satisfatória — comprovando editais; 262 achados; luz verde (sem dados novos); última 2026-10-02 20:00.

**Dados do arquivo local (cópia de 2026-10-01 16:48):** modelo qwen3-8b; 15 missões, **0 validadas, 0 parciais, 15 insuficientes**, 0 fontes confirmadas; fila: 30 editais novos dos motores, 17 indícios do Espião, 3 abertos com itens em falta, 115 empresas sem ficha.

**Diagnóstico:** SEM ROTA (motor interno). Os "262 achados" do painel não batem com o arquivo local, que mostra 15 missões todas insuficientes — ou a cópia local está desatualizada, ou o painel conta outra coisa.

**Correção:** conferir no repositório a versão de hoje do `interceptador.json` e qual campo alimenta o número 262; se as missões continuarem todas "insuficientes", rever o modelo/limiar do Interceptador antes de contá-las como comprovadas.

---

## Rotas que só funcionam (ou só podem ser confirmadas) pelo computador do titular, no Brasil

| motor | url | motivo observado daqui |
|---|---|---|
| 01, 13 | api.queridodiario.ok.org.br / queridodiario.ok.org.br / api.queridodiario.org.br | falha de TLS e tempo esgotado; endereço correto da API a confirmar |
| 03 | https://www.in.gov.br/leiturajornal (do1, do3, do1e) e /consulta | servidor encerra a conexão |
| 04 | https://suap.camaragyn.go.gov.br/camara/consulta_publica/ | cadeia de certificado incompleta |
| 04 | https://www.goiania.go.leg.br/search_rss | 502 / tempo esgotado (instável) |
| 05 | https://alegodigital.al.go.leg.br | ConnectError |
| 07, 11 | https://www.cnj.jus.br/?s=… (e todo o cnj.jus.br) | 403 |
| 08 | https://www.mpgo.mp.br/portal/… (Destina) | tempo esgotado |
| 09 | https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens e /entidades-assistenciais | respondem, mas a tabela exige navegador (JS/AJAX) |
| 16, 20 | https://salic.cultura.gov.br/ e https://aplicacoes.cultura.gov.br/comparar/salicnet/ | robots.txt com erro 500 / redirecionamento em excesso |
| 17 | https://www.gov.br/mcti/pt-br e a página da Setec/MEC | CAPTCHA (não contornar — melhor retirar) |
| 21, 22 | https://html.duckduckgo.com/html/?q=… | requisição recusada daqui |

Fora desta lista: **TRF1 (motor 12)** — o robots.txt proíbe robôs; não deve ser coletado automaticamente nem pelo computador do titular sem antes rever essa permissão.

Observação de segurança: nenhuma página visitada continha instrução dirigida ao auditor.
