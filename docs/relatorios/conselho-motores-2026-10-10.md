# Conselho dos motores — 2026-10-10

145 motores avaliados; 89 com pelo menos uma falha.

## Os sete prompts

**Dra. Irene Lacerda — auditora forense de silêncio** (extremamente pessimista)

> Você é uma auditora forense que desconfia de todo motor 'verde'. Para CADA motor, prove se ele está realmente enxergando ou só respondendo: cruze 30 dias de diário (HTTP, achados, falhas), o funil da última leitura (links vistos → candidatos → vetados pela camada 1 → achados), a duração e as leituras vazias seguidas. Aponte o motor CEGO (responde 200 e nunca acha nada), o ESTRANGULADO (vê centenas de links e o filtro descarta todos), o CONGELADO (repete o mesmo achado), o de PÁGINA VAZIA (lê em menos de 1 s: JavaScript ou bloqueio) e o INTERMITENTE (cai e volta). Para cada um, diga a causa provável e o conserto.

**Prof. Caio Menezes — caçador de vazamentos do funil** (pessimista)

> Você mede onde o valor de cada motor vaza. Para CADA motor, siga os achados até o fim: achado → oportunidade no fluxo → confirmada (objeto + prazo + site oficial) → certidão do Cartório → ouro. Ache a etapa em que o motor perde mais, separe o motor que gera RUÍDO (muitos achados, nenhuma confirmação) do que gera OURO, e diga que procedimento faltou na etapa que vaza.

**Eng. Luana Freire — engenheira de custo e redundância** (levemente pessimista)

> Você corta desperdício. Para CADA motor, calcule o custo por achado útil (segundos de leitura ÷ achados), ache os domínios lidos por mais de um motor (trabalho duplicado) e os motores que gastam tempo sem retorno. Proponha fundir, reduzir a cadência ou redistribuir o tempo para quem rende.

**Dr. Otávio Lemos — juiz de cobertura** (neutra)

> Você é o juiz imparcial do alcance. Compare onde as oportunidades REALMENTE aparecem (UF, tipo de financiador, origem: motor, Piloto ou agregador) com onde os motores olham. Cada oportunidade achada fora dos motores é um ponto cego. Diga quais territórios e tipos de fonte não têm motor e quanto do total vem de fora deles.

**Eng. Diego Arakaki — arquiteto do ritmo** (levemente otimista)

> Você ajusta o relógio de cada motor ao ritmo da fonte. Para CADA motor, veja em quais dias ele achou algo nos últimos 30 dias e com que intervalo; compare com a cadência da agenda. Recomende a cadência certa: ler mais quem publica muito, ler menos quem publica pouco, e o dia da semana em que a fonte costuma publicar.

**Profa. Clara Nogueira — mineradora de fontes irmãs** (otimista)

> Você descobre fontes que o sistema já tocou mas não vigia. Liste os domínios OFICIAIS que aparecem nas oportunidades, nas certidões do Cartório e na biblioteca de sites, e que NENHUM motor cobre. Ordene pelo número de oportunidades que já renderam e transforme a lista num motor novo, lido todos os dias.

**Dr. Fábio Rangel — inventor de alcance em massa** (extremamente otimista)

> Você pensa em escala: uma solução que cubra centenas de fontes de uma vez. Agrupe os endereços oficiais conhecidos pela PLATAFORMA que os gera (WordPress, portais de transparência de fornecedores, diários municipais em lote, Mapas Culturais, sistemas de editais) e calcule quantos órgãos cada adaptador cobriria. Proponha as inovações que multiplicam o alcance: adaptador por plataforma, detecção de mudança por sitemap/feed, consultas inversas.

## Falhas por tipo

- SILÊNCIO LONGO: 45
- VAZAMENTO: 35
- CEGO: 26
- RUÍDO: 19
- CONGELADO: 18
- PÁGINA VAZIA: 9
- INTERMITENTE: 2
- ESTRANGULADO: 1
- CUSTO SEM RETORNO: 1

## Cobertura (Dr. Otávio)

74.6% das oportunidades vieram de fora dos motores: {'agregador/outra': 320, 'Piloto': 89, 'motor': 139}.


## Fontes irmãs (Profa. Clara)

197 domínios oficiais já renderam e não têm motor. Os primeiros:

- fundopositivo.org.br (peso 14)
- baoba.org.br (peso 13)
- chamadas.funbio.org.br (peso 12)
- fundoecos.org.br (peso 12)
- mariaemilia.org.br (peso 9)
- resartis.org (peso 7)
- fundacaogrupoboticario.org.br (peso 7)
- blog.bondinho.com.br (peso 7)
- itausocial.org.br (peso 6)
- notasocial.com.br (peso 6)
- goias365.com.br (peso 6)
- luppa.comidadoamanha.org (peso 5)
- fondationfrancoisschneider.org (peso 5)
- itamarandibahoje.com.br (peso 5)
- dopaonlineupload.procempa.com.br (peso 5)
- sapl.arapongas.pr.leg.br (peso 5)
- corrivus.com.br (peso 5)
- institutogenesio.org.br (peso 5)
- rit.org.br (peso 4)
- assai.com.br (peso 4)
- institutoacp.org.br (peso 4)
- iracemapolis.siscam.com.br (peso 4)
- ecrie.com.br (peso 4)
- folhauberaba.com.br (peso 4)
- institutolojasrenner.org.br (peso 4)

## Plataformas e inovações (Dr. Fábio)

- WordPress: 42 órgãos
- Mapas Culturais: 9 órgãos
- Diário municipal em lote (AGM/DOM): 5 órgãos
- Portal de transparência de fornecedor: 14 órgãos
- Sistemas de editais (Prosas/Editais): 33 órgãos
- Querido Diário: 0 órgãos
- PNCP: 1 órgãos
- Leis e atos (Leis Municipais): 1 órgãos

- **Adaptador por plataforma** — um leitor por plataforma (WordPress: /wp-json/wp/v2/posts?search=edital; Mapas Culturais: API /api/opportunity/find) em vez de um por órgão. Alcance: 42 órgãos WordPress e 9 instâncias de Mapas Culturais já conhecidos de uma vez.
- **Detecção de mudança barata** — ler o sitemap.xml (lastmod) e os feeds RSS/Atom dos sites oficiais; só baixar a página quando muda. Alcance: permite vigiar 10× mais fontes no mesmo tempo de execução.
- **Consulta inversa** — frases distintivas de editais confirmados (ex.: 'Política Nacional Aldir Blanc' + 'chamamento') viram buscas por editais irmãos em outros municípios. Alcance: cada edital confirmado gera pistas em dezenas de municípios que publicam o mesmo modelo.
- **Motor de fontes irmãs** — domínios oficiais que já renderam oportunidade e nenhum motor vigia passam a ser lidos todos os dias. Alcance: implantado como motor Outras Oportunidades (clones calculados para ler todas as fontes no dia).

## Motor a motor

### Prefeituras das 50 maiores cidades de Goiás — portais de editais (`plat-prefeituras-50-go`) — ruído, 5 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **RUÍDO** (funil): 42 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'fluxo → confirmada'. → faltam prazo ou site oficial: entregar o documento (url_documento) ao Cartório
- **CUSTO SEM RETORNO** (redundancia): 306 s na última leitura sem achado. → reduzir páginas por leitura ou a cadência; transferir o tempo para motores que rendem

### Diário da Justiça Federal — Seção Judiciária de Goiás (`dj-trf1-go`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 24 de 30 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte
- **SILÊNCIO LONGO** (falso_verde): 47 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Diário da Justiça Eletrônico — TJGO (`dje-tjgo`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 21 de 26 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **INTERMITENTE** (falso_verde): 5 dias vermelhos alternados com dias bons. → retentativa com espera e rota de reserva (ponte do titular)
- **SILÊNCIO LONGO** (falso_verde): 40 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Programa estadual de eventos esportivos (`f260-captacao-051`) — ruído, 78 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 13 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **RUÍDO** (funil): 108 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Destinação de IR pessoa física para FMDCA (`f260-captacao-118`) — ruído, 13 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 13 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **RUÍDO** (funil): 24 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Lei Rouanet - doação de pessoa física (`f260-captacao-035`) — ruído, 55 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 20 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **RUÍDO** (funil): 89 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC (`plat-cnpq-extensao`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 38 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço
- **VAZAMENTO** (funil): perde 100% na etapa 'fluxo → confirmada'. → faltam prazo ou site oficial: entregar o documento (url_documento) ao Cartório

### Assembleia Legislativa de Goiás — proposições (`alego-pl`) — baixo volume, 9 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 33 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Câmara Municipal de Goiânia — projetos de lei (`camara-goiania-pl`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 30 de 30 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 69 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### CNJ — destinações de penas e prestações pecuniárias (`cnj-destinacoes`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 26 de 27 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 40 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — API de contratações (chamamentos e credenciamentos) (`pncp-api`) — ouro, 1987 achados em 30 dias
- **INTERMITENTE** (falso_verde): 6 dias vermelhos alternados com dias bons. → retentativa com espera e rota de reserva (ponte do titular)
- **VAZAMENTO** (funil): perde 99% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### GIFE — Grupo de Institutos, Fundações e Empresas (`plat-gife`) — ruído, 21 achados em 30 dias
- **RUÍDO** (funil): 45 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Prosas — prêmios, concursos e cursos para OSCs (`plat-prosas-premios`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 13 de 13 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 26 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### FEAS-GO - cofinanciamento da assistência social (`f260-captacao-098`) — ruído, 41 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 28 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **RUÍDO** (funil): 58 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício

### Emenda estadual para saúde comunitária (`f260-captacao-151`) — ruído, 33 achados em 30 dias
- **RUÍDO** (funil): 56 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia (`f260-captacao-190`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 29 de 29 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 45 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### MPGO - TAC com destinação social (`f260-captacao-196`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 29 de 29 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 46 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Escolinha de natação/paradesporto adaptado (`f260-captacao-060`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 20 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 28 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Destinação de IR pessoa jurídica para Fundo da Criança (`f260-captacao-119`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 20 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 28 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Cessão de bens móveis apreendidos (`f260-captacao-208`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 17 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 25 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Bússola Social - Bússola Editais (`f260-captacao-217`) — ruído, 69 achados em 30 dias
- **RUÍDO** (funil): 91 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Capta - oportunidades e editais (`f260-captacao-218`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 37 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundação Bradesco (`f260-captacao-223`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 36 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Coca-Cola Brasil (`f260-captacao-227`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte
- **SILÊNCIO LONGO** (falso_verde): 35 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Votorantim (`f260-captacao-229`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 25 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundação ArcelorMittal (`f260-captacao-230`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 17 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 37 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundação Vale (`f260-captacao-231`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 19 de 19 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 37 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Sicoob (`f260-captacao-233`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 16 de 18 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 35 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Unibanco (`f260-captacao-234`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 18 de 18 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 25 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Lojas Renner (`f260-captacao-235`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 16 de 16 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 22 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Sabin (`f260-captacao-237`) — ruído, 12 achados em 30 dias
- **RUÍDO** (funil): 49 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Editais FICA Goiás - artes visuais/exposição (`f260-captacao-038`) — ruído, 64 achados em 30 dias
- **RUÍDO** (funil): 99 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Emenda estadual para projeto educativo em Goiás (`f260-captacao-068`) — baixo volume, 5 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 23 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Acordo de cooperação sem transferência financeira (`f260-captacao-207`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 16 de 17 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 23 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundação Itaú (`f260-captacao-222`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 17 de 17 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 35 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Instituto Clima e Sociedade (iCS) — chamadas de comunicação e clima (`f260-curadoria-006`) — ruído, 56 achados em 30 dias
- **RUÍDO** (funil): 84 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Instituto Impactarte — cadastro de proponente em fluxo contínuo (`f260-curadoria-008`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 23 de 23 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 34 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### FAPEG — Fundação de Amparo à Pesquisa de Goiás (`plat-fapeg`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 10 de 10 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 19 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundos estaduais de Goiás com conselho — FIA, Idoso, FUNJUVE, Meio Ambiente (`plat-fundos-estaduais-go`) — baixo volume, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 10 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Goiás Social — programas e editais para entidades (`plat-goias-social`) — baixo volume, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 10 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Ministérios Públicos — editais de destinação de recursos de reparação e bens lesados (`plat-mp-destinacoes-reparacao`) — ruído, 24 achados em 30 dias
- **RUÍDO** (funil): 42 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### OVG — Organização das Voluntárias de Goiás: editais e chamamentos (`plat-ovg`) — baixo volume, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 10 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Prosas — editais para o terceiro setor (`plat-prosas`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 10 de 10 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 19 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — FUNDO MUNICIPAL DE CULTURA - CAVALCANTE — oportunidades (espalhado de edital validado) (`f260-espalhado-acessoainformacao-cavalcante-go-gov-br`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 13 de 13 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 18 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — FUNDO MUNICIPAL DE EDUCACAO E CULTURA - FMEC — oportunidades (espalhado de edital validado) (`f260-espalhado-senadorcanedo-go-gov-br`) — baixo volume, 0 achados em 30 dias
- **CEGO** (falso_verde): respondeu 200 em 10 de 10 dias e não achou nada em 30 dias. → conferir se o léxico do motor casa com o vocabulário da fonte e se a página lida é a de editais (não a inicial)
- **SILÊNCIO LONGO** (falso_verde): 14 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Emenda municipal para saúde preventiva (`f260-captacao-152`) — baixo volume, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### PNAB Goiás - Artes Visuais (`f260-captacao-025`) — ruído, 25 achados em 30 dias
- **RUÍDO** (funil): 28 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### BNDES Fundo Socioambiental (`f260-captacao-220`) — baixo volume, 9 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### BNDES Periferias - geração de emprego e renda (`f260-captacao-175`) — baixo volume, 9 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### FDD/Pronasci - cultura e cidadania em territórios vulneráveis (`f260-captacao-169`) — baixo volume, 5 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Instituto Localiza (`f260-captacao-228`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### MDS - Cozinhas Solidárias 2026 (`f260-captacao-090`) — baixo volume, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### PNUD – Small Grants Programme (`f260-captacao-242`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Projeto de coleta seletiva inclusiva (`f260-captacao-180`) — baixo volume, 5 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Banco do Nordeste — Editais Sociais (incentivo fiscal) (`f260-curadoria-001`) — ruído, 8 achados em 30 dias
- **RUÍDO** (funil): 20 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### MP-GO — Programa Destina (cadastro de entidades para receber bens e valores de acordos) (`mpgo-destinacao`) — baixo volume, 8 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 8 dias. → detectar mudança por hash/lastmod e só contar o que é novo
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### MPT-GO — editais de 5 dias para indicação de destinação de recursos ou bens (PRT 18ª Região) (`mptgo-destinacao`) — ruído, 15 achados em 30 dias
- **RUÍDO** (funil): 37 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### SECULT Goiás — chamamentos públicos da Lei 13.019/2014 (`f260-curadoria-009`) — ruído, 40 achados em 30 dias
- **RUÍDO** (funil): 40 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Ministério da Cultura — SALIC — oportunidades (espalhado de edital validado) (`f260-espalhado-rouanet-cultura-gov-br`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Diário Oficial do Município de Goiânia (`do-goiania`) — confirma, 10 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 10 dias. → detectar mudança por hash/lastmod e só contar o que é novo

### Diário Oficial da União (`dou`) — confirma, 28 achados em 30 dias
- **ESTRANGULADO** (falso_verde): viu 5160 links e nenhum virou candidato. → o filtro de candidatos está estreito demais: incluir termos de chamamento/edital da fonte e seguir PDFs

### Editais incentivados de empresas — destinação tributária (Rouanet, LIE, FIA, PRONON) (`empresas-incentivadas`) — ruído, 42 achados em 30 dias
- **RUÍDO** (funil): 42 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício

### Sebrae Goiás - parcerias com OSC para empreendedorismo (`f260-captacao-238`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 49 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Projetos aptos à captação na LIE (`f260-captacao-044`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 36 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Mapa das OSC - área de editais (`f260-captacao-216`) — baixo volume, 13 achados em 30 dias
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Instituto Neoenergia (`f260-captacao-232`) — baixo volume, 9 achados em 30 dias
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Editais de empresas incentivadoras (modelo Porto Itapoá) — FIA, Idoso, Esporte, Rouanet, PRONAS (`plat-empresas-editais-incentivados`) — ruído, 158 achados em 30 dias
- **RUÍDO** (funil): 454 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício

### SALIC — Lei Rouanet (Ministério da Cultura) (`plat-salic`) — ouro, 79 achados em 30 dias
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Motor do Piloto — busca aberta no terceiro setor (`plat-piloto-aberto`) — ouro, 568 achados em 30 dias
- **VAZAMENTO** (funil): perde 99% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### Congresso Nacional — Câmara, Senado e Comissão Mista de Orçamento (emendas, regras e chamamentos) (`congresso-nacional`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 27 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Convênio com órgão público estadual (`f260-captacao-206`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte

### BNDES Corais - meio ambiente (`f260-captacao-176`) — baixo volume, 9 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo

### Fundação Banco do Brasil (`f260-captacao-221`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 17 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Fundação Telefônica Vivo (`f260-captacao-224`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 17 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Google.org (`f260-captacao-251`) — confirma, 5 achados em 30 dias
- **CONGELADO** (falso_verde): o mesmo achado repetido em 5 dias. → detectar mudança por hash/lastmod e só contar o que é novo

### Instituto Natura (`f260-captacao-226`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 17 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Meta Community Grants (`f260-captacao-252`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte

### UNESCO – Fundo Internacional para Diversidade Cultural (`f260-captacao-240`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 17 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Agência do Bem / Rede do Bem — Edital de Microprojetos (`f260-curadoria-004`) — ruído, 16 achados em 30 dias
- **RUÍDO** (funil): 20 achados e nenhuma oportunidade confirmada. → exigir no motor o sinal mínimo (prazo ou chamamento + OSC) antes de registrar; o resto vira indício

### Fundação Tide Setubal — Edital Territórios Clínicos (`f260-curadoria-005`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 17 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Banrisul Instituto Cultural e Social — Edital Merece! (`f260-curadoria-007`) — baixo volume, 4 achados em 30 dias
- **VAZAMENTO** (funil): perde 100% na etapa 'achado → fluxo'. → achados não chegam ao fluxo: registrar com id/URL canônica e prazo quando houver

### TJ-GO — editais das comarcas (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO (`judiciario-tjgo`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 36 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### CNJ — destinação de prestações pecuniárias: busca no Portal do CNJ e regra nacional (Res. 558/2024) (`judiciario-cnj`) — baixo volume, 1 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte

### MPU — MPF, MPDFT, MPM e MPT nacional: destinação de bens e valores (com CNMP e FDD) (`mpu-destinacao`) — baixo volume, 0 achados em 30 dias
- **PÁGINA VAZIA** (falso_verde): leitura em 0 s com 0 página(s). → a fonte provavelmente monta o conteúdo por JavaScript ou bloqueia: usar a API/JSON da página ou a ponte

### PNCP — MUNICIPIO DE NOVO HAMBURGO — oportunidades (espalhado de edital validado) (`f260-espalhado-www-novohamburgo-rs-gov-br`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — MUNICIPIO DE MIRASSOL D'OESTE — oportunidades (espalhado de edital validado) (`f260-espalhado-sistema-mirassoldoeste-mt-gov-br`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — MUNICIPIO DE ROSARIO DO SUL — oportunidades (espalhado de edital validado) (`f260-espalhado-www-rosariodosul-rs-gov-br`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### PNCP — MUNICIPIO DE BENTO GONCALVES — oportunidades (espalhado de edital validado) (`f260-espalhado-www-bentogoncalves-rs-gov-br`) — baixo volume, 0 achados em 30 dias
- **SILÊNCIO LONGO** (falso_verde): 16 leituras vazias seguidas. → reavaliar a URL de entrada: a seção de editais pode ter mudado de endereço

### Outras Oportunidades 3/3 (`outras-oportunidades-3`) — baixo volume, 2 achados em 30 dias
- **VAZAMENTO** (funil): perde 100% na etapa 'fluxo → confirmada'. → faltam prazo ou site oficial: entregar o documento (url_documento) ao Cartório

### Diário Oficial do Estado de Goiás (`do-goias`) — confirma, 117 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### ABCR — Associação Brasileira de Captadores (`plat-abcr`) — confirma, 90 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Captamos — oportunidades de captação (`plat-captamos`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Observatório do Terceiro Setor — editais (`plat-observatorio-3setor`) — confirma, 115 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Rede Filantropia — editais (`plat-rede-filantropia`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Instituto Grupo Boticário (`f260-captacao-236`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Editais de ocupação cultural municipal (`f260-captacao-039`) — baixo volume, 2 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Secult Goiás — Goyazes e Aldir Blanc (`plat-secult-go`) — confirma, 145 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Motor de Recorrência — revisita as oportunidades identificadas (`recorrencia`) — confirma, 257 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Mapa das OSC — editais (`plat-mapa-osc`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Judiciário — CNJ e TJGO: editais das varas de execução penal e das comarcas (prestações pecuniárias) e credenciamentos de entidades (`judiciario-cnj-tjgo`) — baixo volume, 1 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Emenda municipal para entidade assistencial (`f260-captacao-107`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Emenda municipal para projeto educativo em Goiânia (`f260-captacao-069`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### TCM-GO - regularidade municipal e controle (`f260-captacao-212`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### SEMAD Goiás - banco de projetos de autocomposição ambiental (`f260-captacao-177`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### BID – Laboratório de Inovação (`f260-captacao-244`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Banco Mundial – Social Development Grants (`f260-captacao-243`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Climate Justice Resilience Fund (`f260-captacao-255`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Echoing Green (`f260-captacao-259`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Emenda parlamentar federal individual (`f260-captacao-200`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Ford Foundation (`f260-captacao-249`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### GEF Small Grants (`f260-captacao-256`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Gates Foundation (`f260-captacao-250`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Global Fund for Women (`f260-captacao-254`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Instituto Claro (`f260-captacao-225`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Microsoft Philanthropies (`f260-captacao-253`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Oak Foundation (`f260-captacao-260`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Open Society Foundations (`f260-captacao-248`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Rockefeller Foundation (`f260-captacao-257`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Skoll Foundation (`f260-captacao-258`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### UNICEF – Programas de parceria com OSC (`f260-captacao-241`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### USAID – Grants Globais (`f260-captacao-245`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### União Europeia – Erasmus+ (`f260-captacao-246`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### União Europeia – EuropeAid (`f260-captacao-247`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Funbio — Programa Biodiversidade Litoral do Paraná (`f260-curadoria-002`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Movimento Bem Maior — Edital Futuro Bem Maior (`f260-curadoria-003`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Oportunidade Estaduais Governamentais de Goiás (`plat-estaduais-go-gov`) — baixo volume, 1 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### MDHC / CONANDA — Chamamentos publicos de fomento a OSC (`f260-curadoria-010`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Fundacao Maria Emilia — Edital FME Transforma (`f260-curadoria-011`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Querido Diário — diários oficiais municipais — oportunidades (espalhado de edital validado) (`f260-espalhado-www-arapongas-pr-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — CONSELHO REGIONAL DE CONTABILIDADE DO ESTADO DE GOIAS — oportunidades (espalhado de edital validado) (`f260-espalhado-crcgo-org-br`) — baixo volume, 4 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE IPORA — oportunidades (espalhado de edital validado) (`f260-espalhado-www-ipora-pr-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE SENADOR POMPEU — oportunidades (espalhado de edital validado) (`f260-espalhado-www-senadorpompeu-ce-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE CARAZINHO — oportunidades (espalhado de edital validado) (`f260-espalhado-carazinho-atende-net`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — ESTADO DO RIO DE JANEIRO — oportunidades (espalhado de edital validado) (`f260-espalhado-www-detran-rj-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE SAO JOSE DO RIO PRETO — oportunidades (espalhado de edital validado) (`f260-espalhado-www-riopreto-sp-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE CACOAL — oportunidades (espalhado de edital validado) (`f260-espalhado-transparencia-cacoal-ro-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE ITABAIANINHA — oportunidades (espalhado de edital validado) (`f260-espalhado-www-itabaianinha-se-gov-br`) — baixo volume, 8 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE PARANATINGA — oportunidades (espalhado de edital validado) (`f260-espalhado-transparencia-agilicloud-com-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE RIBEIRAO DAS NEVES — oportunidades (espalhado de edital validado) (`f260-espalhado-www-ribeiraodasneves-mg-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### ABCR — Associação Brasileira de Captadores — oportunidades (espalhado de edital validado) (`f260-espalhado-www-santaluziadoparua-ma-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE NOBRES — oportunidades (espalhado de edital validado) (`f260-espalhado-transparencia-nobres-mt-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE VILA RICA — oportunidades (espalhado de edital validado) (`f260-espalhado-www-vilarica-mt-gov-br`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### PNCP — MUNICIPIO DE CARIRE — oportunidades (espalhado de edital validado) (`f260-espalhado-carire-ce-gov-br`) — baixo volume, 16 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Outras Oportunidades 1/3 (`outras-oportunidades-1`) — baixo volume, 0 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.

### Outras Oportunidades 2/3 (`outras-oportunidades-2`) — baixo volume, 2 achados em 30 dias
Sem falha encontrada pelas quatro lentes motor a motor.
