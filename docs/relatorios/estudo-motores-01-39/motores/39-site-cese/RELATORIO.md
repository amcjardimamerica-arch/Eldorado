# Motor 39 — site-cese — CESE (Coordenadoria Ecumênica de Serviço)

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Gasto: 19 chamadas de WebFetch e 2 tentativas de WebSearch.

**Resultado principal: o site cese.org.br NÃO respondeu a partir deste ambiente durante todo o estudo.** Por isso nenhuma oportunidade pôde ser confirmada na fonte, e o `livros.json` foi entregue vazio (`[]`), conforme a regra "inclua só as oportunidades que VOCÊ confirmou ou extraiu". Tudo o que segue sobre o conteúdo do site vem do arquivo de indícios do próprio sistema (`sementes/39_site-cese.json`) e dos registros internos do Eldorado, e está marcado como não verificado.

## 1. Rota (teste e conclusão)

| URL testada | Responde? | Detalhe |
|---|---|---|
| https://cese.org.br/robots.txt | Não | WebFetch: `robots.txt fetch failed: ConnectTimeout` |
| https://cese.org.br/wp-json/wp/v2/edital?per_page=100 (rota configurada) | Não | O WebFetch não lê páginas sem antes ler o robots.txt, e o robots.txt dá timeout. |
| https://cese.org.br/wp-json/wp/v2/edital | Não | `Failed to fetch or parse robots.txt` |
| https://cese.org.br/wp-json/wp/v2/edital?per_page=100&_fields=id,date,slug,link,title | Não | idem |
| https://cese.org.br/ (página do titular) | Não | idem |
| https://www.cese.org.br/ | Não | ConnectTimeout |
| https://cese.org.br/feed/ | Não | idem |
| https://cese.org.br/wp-sitemap.xml | Não | idem |
| https://cese.org.br/editais/ | Não | idem |
| http://cese.org.br/?edital=juventudes-e-direitos-digitais | Não | idem |
| https://cese.org.br/?edital=bem-viver-nas-cidades-movimentos-urbanos-na-defesa-de-direitos | Não | ConnectTimeout |
| `curl` direto (rota configurada e robots.txt) | Não | O proxy de saída do ambiente devolveu 403 no CONNECT para cese.org.br:443 ("policy denial or upstream failure"). |
| web.archive.org (cópia da rota) | Não | Domínio bloqueado para o WebFetch (`SITE_BLOCKED`). |
| WebSearch | Não | Recurso não habilitado na organização (HTTP 403 do proxy). |

Controle: no mesmo momento, o WebFetch leu normalmente https://gife.org.br/editais/ e https://abong.org.br/. A falha é específica de cese.org.br. As hipóteses são: o site filtra conexões de fora do Brasil ou de data centers, ou estava instável. **Não tentei contornar** a falha com espelhos, leitores de terceiros ou outros meios, conforme as regras.

**O que os registros internos mostram (não verificado por mim):**
- `idx_dados.json`, fonte `cese` (motor idx-feeds, leitor `wordpress`, rota "nuvem", P2, cadência de 24 h): última leitura em 2026-10-02T14:04:32Z, sem falhas, `diag: lidos_api 11, novos 11` e 11 indícios no acervo. **A partir da nuvem do sistema, a rota responde e entrega 11 itens.**
- `docs_dados_motores.json`, motor `site-cese`: "ativo, sem achados", 0 achados e relevância 0. A agenda roda 6 vezes ao dia (06:13 a 21:13), embora a fonte declare cadência de 24 h.
- Pelos indícios, cada item da API traz título, data (`date`) e link no formato `https://cese.org.br/?edital=<slug>`. Os campos `prazo`, `valor`, `uf` e `resumo` chegam todos `null`. **A rota não entrega prazo, valor nem abrangência.**

**Conclusão sobre a rota.** O tipo de post `edital` na API REST do WordPress é, em tese, a rota certa: é a fonte primária do próprio financiador e traz o link oficial. Não foi possível verificar se ela é a melhor nem testar alternativas (paginação, `?after=`, `wp/v2/search?subtype=edital`, sitemap do tipo `edital`, feed `?post_type=edital&feed=rss2`). **Nenhuma rota melhor foi verificada.** Problemas visíveis nos dados:
1. O número de itens lidos (11) bate com o limite de uma página e não foi conferido com o cabeçalho `X-WP-Total`. Pode haver mais editais em páginas seguintes.
2. Dez dos 11 itens têm `publicado` entre 19 e 23/10/2025, uma concentração atípica para lançamentos. Isso sugere que o campo `date` reflete republicação ou migração, e não a abertura real do edital.
3. Sem prazo extraído do `content`, o motor não consegue classificar o item como aberto e nada vira achado. Isso explica o "0 achados" diante de 11 indícios.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**Não foi possível extrair o histórico na fonte** porque o site não respondeu. A tabela abaixo reproduz os 11 indícios que o sistema já guardou. A classificação é **provisória e feita só pelo título**: nenhum prazo foi lido. Para todos, o site oficial é a página do próprio financiador (cese.org.br), que é a mesma registrada em `pagina_agregador`.

| data (indício) | título | financiador | site oficial | prazo | estado (provisório) | aplicável (provisório) |
|---|---|---|---|---|---|---|
| 2026-07-29 | Bem Viver nas Cidades: Movimentos Urbanos na Defesa de Direitos (título no indício: "Resultado do edital prorrogado para o dia 15 de outubro de 2026") | CESE | https://cese.org.br/?edital=bem-viver-nas-cidades-movimentos-urbanos-na-defesa-de-direitos | "" | ENCERRADA (a fase de inscrição já terminou, pois o resultado está previsto) | depende |
| 2025-10-23 | Juventudes e Direitos Digitais | CESE | https://cese.org.br/?edital=juventudes-e-direitos-digitais | "" | SEM_DATA | depende |
| 2025-10-23 | Povos do Cerrado enfrentando as Mudanças Climáticas: Direitos Territoriais e Sistemas Alimentares | CESE | https://cese.org.br/?edital=povos-do-cerrado-enfrentando-as-mudancas-climaticas-direitos-territoriais-e-sistemas-alimentares | "" | SEM_DATA | depende (Goiás está no Cerrado; o público provável são povos e comunidades) |
| 2025-10-23 | Amazônia de Todas as Lutas: Direitos e Espiritualidades para o Bem Viver | CESE | https://cese.org.br/?edital=amazonia-de-todas-as-lutas-direitos-e-espiritualidades-para-o-bem-viver | "" | SEM_DATA | não (recorte amazônico) |
| 2025-10-23 | Entre os Campos e as Cidades: Justiça Socioambiental e Climática como defesa de direitos | CESE | https://cese.org.br/?edital=entre-os-campos-e-as-cidades-justica-socioambienta-e-climatica-como-defesa-de-direitos | "" | SEM_DATA | depende |
| 2025-10-23 | Dabucury: Compartilhando experiências e fortalecendo a gestão etnoambiental das terras indígenas da Amazônia | CESE | https://cese.org.br/?edital=dabucury-compartilhando-experiencias-e-fortalecendo-a-gestao-etnoambiental-das-terras-indigenas-da-amazonia | "" | SEM_DATA | não (terras indígenas da Amazônia) |
| 2025-10-23 | Apoio para participação na III Marcha das Mulheres Indígenas | CESE | https://cese.org.br/?edital=apoio-para-participacao-na-iii-marcha-das-mulheres-indigenas | "" | SEM_DATA | não (organizações indígenas) |
| 2025-10-23 | Apoio a projetos de fortalecimento de organizações indígenas de mulheres da Amazônia e do Cerrado | CESE | https://cese.org.br/?edital=apoio-a-projetos-de-fortalecimento-de-organizacoes-indigenas-de-mulheres-da-amazonia-e-do-cerrado | "" | SEM_DATA | não (organizações indígenas de mulheres) |
| 2025-10-20 | CESE e COIAB lançam 2º Edital para fortalecer a Gestão Territorial e Ambiental das Terras Indígenas da Amazônia Legal | CESE, com a COIAB | https://cese.org.br/?edital=cese-e-coiab-lancam-2o-edital-para-fortalecer-a-gestao-territorial-e-ambiental-das-terras-indigenas-da-amazonia-legal | "" | SEM_DATA | não (Amazônia Legal; Goiás não faz parte) |
| 2025-10-20 | Sementes Ancestrais, Futuros Possíveis: Mulheres e Juventudes por Justiça Socioambiental e Climática | CESE | https://cese.org.br/?edital=sementes-ancestrais-futuros-possiveis-mulheres-e-juventudes-por-justica-socioambiental-e-climatica | "" | SEM_DATA | depende |
| 2025-10-19 | Prêmio Zanetti de Direitos Humanos para organizações populares de todo o país | CESE | https://cese.org.br/?edital=premio-zanetti-de-direitos-humanos-para-organizacoes-populares-de-todo-o-pais | "" | SEM_DATA | depende (abrangência nacional, segundo o título) |

Contagem provisória: 11 indícios, sendo 0 abertos, 1 encerrado e 10 sem data. Aplicáveis à OSC de Goiânia: 0 "sim", 6 "depende" e 5 "não". Financiadores: 1 (CESE), mais 1 parceiro citado no título (COIAB).

Busca em fontes secundárias: a página https://gife.org.br/editais/ não traz nenhum edital da CESE. Em https://abong.org.br/?s=CESE+edital, o único resultado é de 2018, fora do período. Em https://observatorio3setor.org.br/?s=CESE, nenhum resultado trata de edital da CESE. Nenhuma fonte secundária acrescentou oportunidades do período.

## 3. Onde publica

O que se pode afirmar pelos dados do sistema:
- **Site oficial:** cese.org.br, um WordPress com tipo de post próprio `edital`. A URL canônica de cada edital tem a forma `https://cese.org.br/?edital=<slug>`, que também serve de API em `wp-json/wp/v2/edital`.
- **Parcerias:** pelo menos um edital é lançado em conjunto com uma organização do movimento indígena, a COIAB. O edital é publicado no site da CESE.
- **Plataforma de inscrição:** não confirmada. Não foi possível ver se a inscrição é por formulário próprio, e-mail, Prosas ou outro meio.
- O edital não aparece no GIFE nem em outros agregadores consultados. **A fonte primária é o único canal confiável observado.**

## 4. Tipos de oportunidade

Pelos títulos dos indícios (não verificado):
- **Editais de projeto temáticos** (a maioria): justiça socioambiental e climática, direitos territoriais, sistemas alimentares, Cerrado, Amazônia, juventudes, direitos digitais, mulheres, movimentos urbanos e espiritualidades.
- **Prêmio:** Prêmio Zanetti de Direitos Humanos, para organizações populares de todo o país.
- **Apoio a mobilização e participação:** apoio para a participação na III Marcha das Mulheres Indígenas.
- **Intercâmbio e fortalecimento institucional:** Dabucury e fortalecimento de organizações indígenas de mulheres.
- Público recorrente: movimentos e organizações populares, povos indígenas, comunidades tradicionais, mulheres e juventudes.
- **Valores e quem pode participar: não confirmados** (o campo `valor` é nulo em todos os indícios).

## 5. Calendário

Não confirmado. Os únicos sinais de data são o `publicado` dos indícios: 10 itens entre 19 e 23/10/2025 e 1 item em 29/07/2026. A concentração de outubro de 2025 parece efeito de republicação em lote e não deve ser usada como calendário de abertura sem conferir o texto de cada edital. O único marco datado no próprio texto é "resultado prorrogado para 15/10/2026" (Bem Viver nas Cidades).

## 6. Conselho de 7 lentes

**1. Extremamente pessimista — Dra. Helga Brandão, chief engineer (implacável e orientada a incidentes).**
"Um motor que roda 6 vezes ao dia, leu 11 itens, tem 0 achados e relevância 0 está morto com sinal verde no painel. Ele não extrai prazo, então nunca classifica nada como aberto. Não confere o `X-WP-Total`, então não sabe se viu tudo. Grava `date` como publicação, mas dez itens com a mesma semana de data é sintoma clássico de reindexação. E hoje o site nem respondeu para fora da nuvem do sistema: se essa rota cair, ninguém percebe, porque 'zero achados' já é o estado normal."

**2. Pessimista — Prof. Dr. Otávio Lacerda, pós-doutor em Python (minucioso e cético com metadados).**
"O leitor `wordpress` é genérico. Ele pega `title`, `date` e `link` e joga fora o `content`, onde moram prazo, valor e quem pode participar. Também falta normalizar o título: o indício 'Bem Viver nas Cidades' veio com o título de uma notícia de resultado, e não com o do edital. A deduplicação por URL funciona, mas a classificação por título engana."

**3. Levemente pessimista — Rafael Mendonça, staff engineer (pragmático).**
"A fonte é boa, o processamento é que está raso. Cadência de 6 vezes ao dia para um financiador que publica poucos editais por ano é desperdício; 1 vez ao dia basta. E o perfil 'fora' ou 'indefinido' de todos os itens mostra que o filtro geográfico e temático não tem texto para trabalhar."

**4. Neutro — Dra. Beatriz Okafor, CTO de big tech (síntese).** Ver abaixo.

**5. Levemente otimista — Prof. Dr. Henrique Sá, pós-doutor em Python (didático).**
"O essencial está certo: a rota é a API do próprio financiador, o link guardado já é o oficial e o tipo de post `edital` separa os editais das notícias. Com um extrator de `content` de umas 40 linhas (regex de datas em português e de 'R$'), o motor passa de zero a útil."

**6. Otimista — Camila Ventura, staff engineer (foco em produto).**
"A CESE é um dos poucos financiadores que apoiam movimentos populares urbanos, juventudes e direitos digitais com abrangência nacional. Três ou quatro dos 11 indícios podem servir a uma associação de bairro de Goiânia. Com prazo extraído e alerta, o motor vira um canal de alta precisão e baixo ruído."

**7. Extremamente otimista — Dr. Marcos Tavares, chief engineer (visionário).**
"Os títulos dos editais de 2023 a 2026 formam uma série temática: Cerrado, cidades, juventudes, mulheres. Com o histórico completo e o `content` arquivado, dá para prever o próximo ciclo e preparar a proposta antes do lançamento. Ganho ideal: 100% dos editais da CESE capturados no dia do lançamento, com prazo, valor e elegibilidade estruturados."

### Síntese do neutro (Dra. Beatriz Okafor)

**Decisão:** manter o motor ativo e a rota `wp-json/wp/v2/edital`, mas rebaixar o painel de "ativo, sem achados" para **"ativo, extração incompleta"** até que o prazo seja extraído. Reestudar a rota a partir de um ponto de saída que alcance o site, como a nuvem do sistema ou um acesso pelo Brasil.

**Melhorias concretas:** ver a seção 7 (numeradas de 1 a 10).

**Parâmetros de qualidade:**
- Cobertura: o número de itens lidos é igual a `X-WP-Total` em 100% das leituras.
- Prazo extraído em pelo menos 80% dos editais com inscrição (os demais são marcados como `sem_data` com motivo).
- Valor extraído em pelo menos 60% dos editais.
- Link oficial: 100% dos links no domínio cese.org.br e respondendo 200.
- Zero duplicatas por `id` do WordPress.
- Falha de leitura vira alerta em até 24 h, e não "0 achados".
- Tempo de detecção de edital novo: até 24 h.

**Riscos e mitigação:**
1. *O site é inacessível de certas redes (filtro geográfico ou de data center).* Mitigação: manter a leitura na nuvem que hoje funciona, registrar o HTTP de cada leitura no painel (hoje `http: null`) e alertar após 2 falhas seguidas.
2. *A data `date` não reflete o lançamento.* Mitigação: usar a data de início escrita no `content`; na falta dela, usar `primeiro_visto`; guardar `modified` à parte.
3. *A estrutura do texto muda e a regex de prazo quebra.* Mitigação: testes com amostras reais arquivadas e um alerta quando a taxa de prazo extraído cair abaixo de 50%.
4. *Falso negativo geográfico (edital nacional marcado "fora").* Mitigação: só marcar "não" com recorte explícito (Amazônia Legal, um estado nomeado, indígenas); nos demais casos usar "depende".
5. *Notícia de resultado confundida com edital.* Mitigação: detectar no título ou no texto palavras como "resultado", "selecionados" e "prorrogado" e vincular ao edital de origem pelo slug, sem criar item novo.

## 7. Melhorias do motor

1. **Rota/paginação:** ler `wp-json/wp/v2/edital?per_page=100&page=N` até esgotar, conferindo `X-WP-Total` e `X-WP-TotalPages`. Hoje 11 itens podem ser só a primeira página.
2. **Rota/descoberta leve:** testar `wp-json/wp/v2/search?subtype=edital&per_page=100` e o sitemap do tipo `edital` (`wp-sitemap-posts-edital-1.xml` ou equivalente) como índice barato. Ler o detalhe (`/edital/{id}`) só dos ids novos ou com `modified` alterado.
3. **Extração de prazo:** fazer o parse do `content.rendered` com regex de datas em português ("até DD de mês de AAAA", "DD/MM/AAAA", "inscrições de ... a ..."). Sem isso, o motor fica com 0 achados para sempre.
4. **Léxico de valor e de quem pode participar:** extrair "R$", "até R$ ... por projeto", "organizações populares", "grupos não formalizados", "CNPJ" e a abrangência ("todo o país", "Amazônia Legal", nomes de estados e biomas).
5. **Filtro de aplicabilidade:** "não" só com recorte explícito (Amazônia Legal, indígenas, outro estado); "Cerrado", "cidades", "juventudes" e "todo o país" ficam em "depende" com prioridade para Goiás.
6. **Datas:** gravar separadamente `date`, `modified`, início e prazo do texto e `primeiro_visto`. Não usar `date` como data de lançamento quando houver lote de republicação (vários itens com a mesma data).
7. **Deduplicação:** usar como chave o `id` do WordPress e o slug. Notícias de "resultado" ou "prorrogação" atualizam o estado do edital de origem e não criam item novo; normalizar o título removendo o prefixo "Resultado ...".
8. **Cadência:** reduzir de 6 vezes ao dia para 1 vez ao dia (a fonte já declara 24 h). Na falta de edital aberto, uma leitura semanal completa do histórico.
9. **Link oficial:** manter `link` da API (`?edital=<slug>`) como `url` e `pagina_agregador` vazio, porque a CESE é o próprio financiador. Gravar também o link de inscrição encontrado no `content` (formulário ou plataforma).
10. **Monitoramento:** registrar o HTTP e a contagem de itens de cada leitura (hoje `http: null` em todos os dias do painel). Alertar quando houver timeout ou quando a contagem cair, para não confundir falha com "sem achados".

## 8. O que não foi confirmado e por quê

- **Nada do conteúdo do site foi confirmado.** cese.org.br não respondeu: o robots.txt deu ConnectTimeout no WebFetch, e o proxy de saída do ambiente recusou o `curl` com 403. Por respeito às regras, não usei espelhos, caches nem leitores de terceiros para contornar a falha. A cópia do Internet Archive também estava bloqueada para o WebFetch, e o WebSearch não está habilitado.
- **Rota melhor:** não verificada. As alternativas da seção 7 (itens 1 e 2) são propostas a testar.
- **Histórico completo de 3 anos:** não extraído. Só os 11 indícios do sistema são conhecidos, e não se sabe se a API tem mais itens.
- **Prazos, valores, quem pode participar, plataforma de inscrição e calendário:** não confirmados, pois os indícios trazem esses campos como nulos.
- **Classificações da seção 2:** são provisórias, feitas só pelo título.
- **livros.json:** entregue vazio (`[]`). Nenhuma oportunidade foi confirmada por mim, e a regra manda incluir só as confirmadas ou extraídas. Os 11 indícios serão tratados à parte pelo sistema.
- **Verificação por amostra de links oficiais:** a regra é para agregadores, e este site é financiador. Mesmo assim, tentei abrir 2 links do arquivo de indícios (`?edital=juventudes-e-direitos-digitais` e `?edital=bem-viver-nas-cidades-...`), e ambos falharam por timeout. Todos os 11 links estão no domínio do próprio financiador.
- **Instruções em páginas:** nenhuma página com instrução dirigida ao agente foi encontrada (quase nenhuma página foi lida).
- **Próximo passo recomendado:** repetir as tarefas 1 e 2 a partir da nuvem do sistema, onde a leitura de 2026-10-02 às 14:04Z funcionou, ou de uma rede no Brasil.

---

## Adendo (02/10/2026, coordenação do estudo): o robots.txt da CESE proíbe o Claude

O robots.txt foi lido pelo navegador do titular, que tem IP brasileiro, em `https://cese.org.br/robots.txt`. Ele tem uma regra específica para `User-agent: ClaudeBot`: **`Disallow: /`**. A regra também vale para Applebot e Baiduspider. Para os demais robôs, o site é liberado (`Allow: /`, exceto `/wp-admin/`), e o sitemap fica em `https://cese.org.br/sitemap_index.xml`.

**Conduta adotada:** como este estudo é feito pelo Claude, a CESE **não foi lida** por nenhuma via, nem pelo navegador do titular. A extração dos 3 anos fica pendente.

**Para o motor do sistema:**

- O robô do Eldorado se identifica como robô próprio, não como ClaudeBot, e pode ler a API `wp-json/wp/v2/edital`, porque o robots.txt libera os robôs em geral.
- A extração dos 3 anos deve ser feita pelo próprio motor, na carga de histórico, usando o sitemap do tipo edital.
- **Não é permitido** ao motor usar identificação de IA para ler esse site.
