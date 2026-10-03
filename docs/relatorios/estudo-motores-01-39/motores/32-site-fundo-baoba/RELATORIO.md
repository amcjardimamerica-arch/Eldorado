# Motor 32 — site-fundo-baoba (Fundo Baobá para Equidade Racial)

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Foram usadas 37 chamadas de WebFetch. O `curl` direto ao domínio foi recusado pelo proxy do ambiente (CONNECT 403), então toda a coleta passou pelo WebFetch.

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| Rota configurada: `None` (leitor `html_listagem`) | — | Não há rota gravada. O motor depende da página pública e de um rastreamento genérico. |
| https://baoba.org.br/editais/ | Sim (200) | 17 itens em 3 blocos: **Editais abertos** (1), **Em curso** (8) e **Finalizados** (8). Traz o título e o link de cada item, sem datas, prazos ou valores. Dois links são encurtadores bit.ly que levam a `editais.baoba.org.br`. Sem paginação. |
| https://baoba.org.br/robots.txt | Sim | `Disallow:` vazio, ou seja, tudo é permitido. Sitemap: `https://baoba.org.br/sitemap_index.xml`. |
| https://baoba.org.br/sitemap_index.xml | Sim | 8 sitemaps filhos (post, page, attachment ×3, category, post_tag, author), todos com `lastmod`. |
| https://baoba.org.br/page-sitemap.xml | Sim | 62 páginas com `lastmod`. Mostra páginas de edital novas (por exemplo `/edital-aya/`, `/programa-de-bolsas/`, `/home/programa-marielle-franco-apoio-individual/`). |
| https://baoba.org.br/category-sitemap.xml | Sim | 50 categorias. Inclui `/category/edital/` e as subcategorias `black-stem`, `ja-e`, `programa-marielle-franco`, `carreiras-em-movimento` etc. |
| **https://baoba.org.br/category/edital/feed/** | Sim (RSS) | 10 itens por página, com `pubDate` e trechos que trazem prazo e valor (por exemplo "inscrições com início em 26 de março, vão até 7 de maio"). |
| https://baoba.org.br/category/edital/feed/?paged=2 | Sim | 7 itens (2024–2025). A paginação do feed funciona. |
| **https://baoba.org.br/?s=inscri%C3%A7%C3%B5es&feed=rss2** | Sim (RSS) | Busca em RSS. Trouxe a Bolsa Alcance (30/04/2026), o Black STEM 3 e o Marielle Franco 2, com prazos. |
| https://baoba.org.br/wp-json/wp/v2/pages?search=edital | Sim | A API REST do WordPress responde (retornou id 14861, data, modificação e link do Marielle Franco Individual). Pelo WebFetch só veio parte da lista. |
| https://bit.ly/PMFColetivo2 → https://editais.baoba.org.br/programa-marielle-franco-2 | 302 → 200 | Página oficial do edital aberto (Apoio Coletivo 2ª ed.). Traz R$ 300.000,00, a elegibilidade e a inscrição via SurveyMonkey. **Não traz datas.** |
| https://bit.ly/BS-3edicao → https://editais.baoba.org.br/lp-black-stem | 302 → 200 | Página do Black STEM 3: R$ 42 mil/ano, 3 bolsas, com menção a "prorrogação" mas sem datas. |
| https://editais.baoba.org.br/ (raiz) | **404** | O subdomínio não tem índice. Só funcionam as páginas individuais. |
| PDF do edital Coletivo 2 (cloudfront RD Station) | **Bloqueado por robots.txt** | Não foi lido. |

**Conclusão da rota.** Hoje o motor não tem rota (`None`). A melhor combinação verificada é esta:
1. **Listagem principal:** `https://baoba.org.br/editais/`, que mostra o estado (aberto, em curso ou finalizado) definido pelo próprio financiador. Para cada link `bit.ly`, seguir o redirecionamento e gravar a URL final `editais.baoba.org.br/...`.
2. **Datas e prazos:** `https://baoba.org.br/category/edital/feed/` (com `?paged=N`) e `https://baoba.org.br/?s=inscri%C3%A7%C3%B5es&feed=rss2`. O RSS traz `pubDate`, e os prazos aparecem no texto.
3. **Detecção de páginas novas:** `https://baoba.org.br/page-sitemap.xml`, comparando o `lastmod`.
4. Opcional: `https://baoba.org.br/wp-json/wp/v2/pages?search=edital&_fields=id,date,modified,link,title` (API WordPress).

**Defeito grave no que o sistema já guardou.** Os 4 "achados" do painel quase certamente são falsos positivos. No arquivo de indícios, exatamente 4 itens têm prazo em 2027, e todos estão errados:
- Marielle Franco Individual: o indício diz 2027-09-11, mas as inscrições foram de 11/09 a **14/10/2025**.
- Educação e Identidades: o indício diz 2027-08-03, mas é um edital de 2022 e está na lista de **finalizados**.
- Primeira Infância: o indício diz 2027-01-20, mas é de 2021 e está **finalizado**.
- Quilombolas: o indício diz 2027-09-23, mas é de 2021 e está **finalizado**. A lista final de selecionadas saiu em 22/12/2021.

O padrão aponta para o parser: ele lê "dia de mês" sem ano e projeta a data para o próximo ano futuro. O indício de Carreiras em Movimento também tem valor truncado ("R$ 5" em vez de "R$ 5.000,00 a R$ 10.000,00").

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

Recorte usado: todas as chamadas publicadas pelo Fundo Baobá cujo período de inscrição tocou a janela.

| data (abertura / publicação) | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 21/09/2023 | Edital Carreiras em Movimento | Fundo Baobá + MOVER | https://baoba.org.br/programa-presente-e-futuro-em-movimento/carreiras-em-movimento/ | 02/10/2023 | ENCERRADA | não (só PF) |
| 23/07/2023 (indício) | Edital Educação em Tecnologia | Fundo Baobá + MOVER (apoio Imaginable Futures, Fundação Lemann) | https://baoba.org.br/programa-presente-e-futuro-em-movimento/educacao-em-tecnologia/ | "" (página diz "inscrições encerradas") | ENCERRADA | depende (OSC/empresa negra de tecnologia) |
| 22/03/2024 | Black STEM – 1ª edição | Fundo Baobá + B3 Social + BRASA | https://baoba.org.br/blackstem/ | 30/04/2024 | ENCERRADA | não (só PF) |
| 27/03/2025 | Black STEM – 2ª edição | Fundo Baobá + B3 Social + BRASA | https://baoba.org.br/editais-em-curso/blackstem-2edicao/ | 12/05/2025 | ENCERRADA | não (só PF) |
| 06/05/2025 | Edital Já É – 2ª edição | Fundo Baobá | https://baoba.org.br/programa-ja-e-2025/ | 06/06/2025 | ENCERRADA | não (só PF) |
| 11/09/2025 | Programa Marielle Franco – Apoio Individual (2ª ed.) | Fundo Baobá (apoio Ford, Ibirapitanga, OSF) | https://baoba.org.br/home/programa-marielle-franco-apoio-individual/ | 14/10/2025 | ENCERRADA | não (só PF) |
| "" | Programa Marielle Franco – Apoio Coletivo (2ª ed.) | Fundo Baobá | https://editais.baoba.org.br/programa-marielle-franco-2 | "" | SEM_DATA (listado como aberto) | depende (exige 85% de mulheres negras na direção e na membresia) |
| 26/03/2026 | Black STEM – 3ª edição | Fundo Baobá + B3 Social + BRASA | https://baoba.org.br/programa-black-stem-abre-oportunidade-de-apoio-a-estudo-no-exterior-para-estudantes-brasileiros/ | 07/05/2026 | ENCERRADA | não (só PF) |
| 30/04/2026 | Bolsa Complementar Alcance | Fundação Lemann, com apoio do Fundo Baobá | https://baoba.org.br/fundo-baoba-apoia-programa-de-pos-graduacao-no-exterior/ | 11/05/2026 | ENCERRADA | não (só PF) |

Total: **9 oportunidades** (0 abertas com data, 8 encerradas, 1 sem data). Todas foram para o `livros.json` com `acao: criar_livro`, porque todas têm site oficial.

Fora da janela, mas verificadas como histórico (indícios antigos, todos ENCERRADOS):
- Já É 1ª ed. (2022)
- Educação e Identidades Negras (2022; 12 organizações receberam R$ 175 mil cada)
- Primeira Infância (2021)
- Programa Marielle Franco 1ª ed. (2021/2022)
- Recuperação Econômica (2021)
- Vidas Negras (2021)
- Quilombolas em Defesa (setembro de 2021)
- Negros, Negócios e Alimentação (2021)
- Chamada para Artigos (lançada em 06/08/2020)
- Aliança entre Fundos (Baobá + Fundo Brasil + Fundo Casa): editais de setembro/outubro de 2021

Não entram nos livros.

Apoios que não passaram por chamada pública (não são oportunidades):
- R$ 1,25 milhão à Marcha das Mulheres Negras 2025.
- Renovação de R$ 300 mil à Sociedade Protetora dos Desvalidos (25/09/2026).

## 3. Onde publica

- **Site oficial:** `baoba.org.br`, em WordPress com Yoast SEO. A página `/editais/` é a vitrine, com três blocos de estado. Cada edital tem uma página própria, sem padrão de URL. Exemplos: `/programa-ja-e-2025/`, `/editais-em-curso/blackstem-2edicao/`, `/home/programa-marielle-franco-apoio-individual/`, `/programa-presente-e-futuro-em-movimento/...`.
- **Subdomínio de landing pages:** `editais.baoba.org.br`, ao que parece em RD Station, porque o PDF fica em `d335luupugsy2.cloudfront.net/cms/files/205828/...`. Os editais mais novos (Coletivo 2, Black STEM 3) chegam por **bit.ly**, e a raiz do subdomínio dá 404.
- **Notícias (posts):** os anúncios de abertura com as datas saem como posts na categoria `edital` (RSS disponível). Os resultados também saem como posts.
- **Plataforma de inscrição:** formulário próprio ou formulário eletrônico (Carreiras em Movimento, Marielle Individual), **SurveyMonkey** (Marielle Coletivo 2) e e-mail de apoio `programadebolsas@baoba.org.br` (bolsas). O edital da Bolsa Alcance fica num PDF no Google Drive. **Não usa** Prosas, Mapas Culturais nem Transferegov.

## 4. Tipos de oportunidade

- **Bolsas para pessoa física** (maioria no período):
  - Black STEM: R$ 35–42 mil/ano para graduação STEM no exterior.
  - Já É: R$ 700/mês por 2 anos.
  - Marielle Franco Individual: R$ 3.500/mês por 18 meses.
  - Carreiras em Movimento: R$ 5–10 mil.
  - Alcance: USD 7 mil/ano para pós-graduação no exterior.
- **Edital de projeto / fortalecimento institucional para organizações:**
  - Marielle Franco Coletivo 2: R$ 300 mil.
  - Educação em Tecnologia: R$ 250–500 mil.
  - No histórico de 2021–2022: Educação e Identidades (R$ 175 mil), Quilombolas e Vidas Negras.
- **Doações diretas por convite** (sem chamada): Marcha das Mulheres Negras, SPD.
- **Áreas:** equidade racial com foco em educação, STEM, carreira e empregabilidade, liderança de mulheres negras, fortalecimento institucional de organizações negras e quilombolas, e empreendedorismo negro (2021).
- **Quem participa:** pessoas negras (PF) e organizações, coletivos e grupos **liderados por pessoas negras**. Alguns editais aceitam grupos não formalizados. A abrangência é nacional, com prioridade frequente para o Norte e o Nordeste.
- **Faixas de valor:** PF de R$ 5 mil a cerca de R$ 63 mil por pessoa. Organizações de R$ 175 mil a R$ 500 mil.
- **Internacional:** Black STEM e Alcance são bolsas para estudo no exterior, mas a chamada é nacional.

## 5. Calendário

| Mês típico de abertura | Chamada |
|---|---|
| março (fecha abril/maio) | Black STEM (2024, 2025, 2026) |
| abril/maio | Bolsa Alcance (2026) |
| maio (fecha junho) | Já É (2025) |
| setembro (fecha outubro) | Carreiras em Movimento (2023), Marielle Franco Individual (2025) |
| 2º semestre | Notícia de 26/08/2026: "para o segundo semestre, estão previstas novas oportunidades de fortalecimento institucional". O Marielle Coletivo 2 aparece como aberto em 02/10/2026. |

Previsão: o primeiro semestre concentra as bolsas para PF. O segundo semestre (setembro–outubro) concentra os editais de lideranças e de fortalecimento institucional, que interessam a OSCs.

## 6. Conselho de 7 lentes, com a síntese do neutro

1. **Extremamente pessimista — Dr. Haroldo Vasconcelos, chief engineer, ríspido e obcecado por dado falso.**
   "O painel diz 'satisfatório, 4 achados', e os 4 são lixo: editais de 2021–2025 marcados com prazo em 2027. O motor não tem rota, o parser inventa ano e o valor sai truncado ('R$ 5'). Um motor que mostra edital morto como aberto é pior do que motor nenhum, porque gasta a atenção da associação."
2. **Pessimista — Profa. Dra. Lúcia Tavares, pós-doc em Python e engenharia de dados, metódica.**
   "A página `/editais/` não tem nenhuma data, e o leitor `html_listagem` fica cego. O link do único edital aberto é bit.ly, que o motor não segue. O subdomínio `editais.baoba.org.br` não tem índice, e o PDF com o cronograma está bloqueado por robots. Sem RSS nem sitemap, os editais novos ficam invisíveis até alguém citar o link."
3. **Levemente pessimista — Rafael Okoye, staff engineer, pragmático.**
   "O site é pequeno, com 1 a 4 chamadas por ano. Quase 80% delas são bolsas para pessoa física, que a associação não pode usar. O filtro de aplicabilidade precisa descartar essas chamadas cedo, senão o motor gera ruído."
4. **Neutro — Dra. Beatriz Konno, CTO de big tech, moderadora** (síntese abaixo).
5. **Levemente otimista — Prof. Dr. Samuel Adeyemi, pós-doc em sistemas distribuídos, didático.**
   "O WordPress entrega de graça um RSS por categoria (`/category/edital/feed/`) e uma busca em RSS. Com `pubDate` e prazo no texto, um parser simples de 'de X a Y de mês' ancorado no ano do `pubDate` resolve as datas."
6. **Otimista — Camila Ferraz, chief engineer de produto, entusiasmada.**
   "O financiador separa sozinho 'abertos', 'em curso' e 'finalizados'. Basta respeitar esse rótulo como verdade de base, e o motor nunca mais mostra um 2021 como aberto. O histórico também já está pronto para o calendário de previsão."
7. **Extremamente otimista — Dr. Thiago Mbeki, CTO, visionário.**
   "Com sitemap, RSS e API REST, este é o motor mais barato de manter do sistema. Bem calibrado, ele avisa a associação em setembro de cada ano sobre o edital de fortalecimento institucional (R$ 175–500 mil) e pode virar um modelo para todos os financiadores em WordPress."

**Síntese do neutro (Dra. Beatriz Konno)**

- **Decisão:** **manter e corrigir com urgência**. Rebaixar o painel de "satisfatório" para "**com defeito**" até as correções 1 a 4 entrarem. Os 4 achados atuais devem ser reclassificados como `encerrado_arquivar`.
- **Melhorias:** ver a seção 7.
- **Parâmetros de qualidade:**
  - 0 itens com prazo inferido para um ano posterior ao do `pubDate`/`publicado` sem ano explícito no texto.
  - 100% dos itens do bloco "Finalizados" com estado `encerrado_arquivar`.
  - 100% dos links `bit.ly` resolvidos até a URL final.
  - Valor monetário completo (regex com milhar e centavos, ou "mil"/"milhão").
  - Detecção de edital novo em até 7 dias após aparecer no RSS ou no sitemap.
  - Taxa de falso aberto abaixo de 5%.
- **Riscos e mitigação:**
  1. *Parser de ano errado.* Ancorar o ano no `pubDate` e exigir `inicio ≤ prazo ≤ pubDate + 18 meses`.
  2. *Encurtadores bit.ly e subdomínio sem índice.* Seguir os redirecionamentos (até 3) e registrar a URL final, sem depender da raiz do subdomínio.
  3. *Cronograma só no PDF bloqueado por robots.* Respeitar o bloqueio, marcar `sem_data` e ler a data da notícia RSS.
  4. *Ruído de bolsa PF.* Classificar `aplicavel: "nao"` quando o texto disser "pessoa física", "bolsa", "estudante" ou "autodeclarada" sem menção a organização.
  5. *Mudança de layout ou de URL.* O sitemap com `lastmod` funciona como sentinela, e um alerta deve disparar se `/editais/` deixar de ter os 3 blocos.

## 7. Melhorias do motor (lista numerada)

1. **Rota:** configurar a rota primária `https://baoba.org.br/editais/` (estado por bloco) e as secundárias `https://baoba.org.br/category/edital/feed/` (com `?paged=N`) e `https://baoba.org.br/?s=inscri%C3%A7%C3%B5es&feed=rss2`.
2. **Filtro de estado:** item no bloco "Editais finalizados" vira `encerrado_arquivar`. Item em "Editais em curso" também vira `encerrado_arquivar`, porque a seleção já foi feita. Só o bloco "Editais abertos" pode gerar `aberto` ou `sem_data`.
3. **Datas:** corrigir o parser. Datas sem ano ("11 de setembro") usam o ano do `pubDate` ou do `publicado`, e nunca o próximo ano futuro. Reprocessar os 4 indícios com prazo em 2027.
4. **Link oficial:** resolver bit.ly e outros encurtadores e gravar a URL final (`editais.baoba.org.br/...`). Aceitar `editais.baoba.org.br` como domínio oficial do financiador.
5. **Léxico:** incluir "inscrições abertas", "de X a Y de", "até as 17h", "bolsa", "apoio coletivo", "fortalecimento institucional", "Black STEM", "Já É", "Marielle Franco", "SurveyMonkey".
6. **Filtro de aplicabilidade:** marcar como `nao` as bolsas para PF (Black STEM, Já É, Marielle Individual, Carreiras, Alcance) e como `depende` os editais para organizações com recorte (lideranças negras, 85% mulheres negras).
7. **Valor:** usar uma regex que capture "R$ 5.000,00 a R$ 10.000,00", "R$ 42 mil", "USD 7 mil" e "R$ 1,25 milhão" sem truncar.
8. **Cadência:** semanal de agosto a novembro e em março–maio (janelas típicas), quinzenal no resto do ano. Ligar um sentinela diário barato no `lastmod` do `page-sitemap.xml` e do `post-sitemap.xml`.
9. **Histórico:** carregar uma vez a lista de "Finalizados" e o RSS paginado como base de previsão (calendário da seção 5).
10. **Deduplicação:** usar a chave (programa + edição), porque a mesma chamada aparece em `/editais/`, no post de abertura, no post de resultado e na landing `editais.`. Normalizar as variantes "Apoio Individual 2ª ed." e "segunda edição".

## 8. O que não foi confirmado e por quê

- **Prazo e datas do Marielle Franco – Apoio Coletivo 2ª ed.:** a página oficial não traz datas. O PDF do edital (cloudfront/RD Station) está **bloqueado por robots.txt** e não foi lido. As buscas RSS por "coletivo" e "marielle" não trouxeram post de abertura. Por isso ficou `sem_data`, mesmo listado como aberto.
- **Período de inscrição do Educação em Tecnologia:** a página diz apenas "inscrições encerradas". A data de publicação (23/07/2023) vem do arquivo de indícios. Não foi confirmado se as inscrições tocaram a janela de 02/10/2023.
- **Edital Ayá** (`/edital-aya/`, 01/02/2024; subpáginas coletivo e individual de 15/08/2025): a página não traz datas, valor nem forma de inscrição, e aparece como guarda-chuva do Programa Marielle Franco. Não foi confirmado como chamada distinta e não entrou nos livros.
- **Datas de início da Bolsa Alcance e o ano do prazo:** a notícia diz "até 11 de maio". O ano 2026 foi deduzido da data da publicação (30/04/2026). O edital completo está no Google Drive e não foi aberto. O site oficial da Fundação Lemann não foi consultado.
- **Data de publicação** de várias páginas (Black STEM 1 e 2, Já É 2): os metadados mostram apenas uma modificação em 10/06/2026, então o campo ficou "".
- **API WordPress:** respondeu, mas o WebFetch resumiu o retorno. A listagem completa por API não foi validada.
- **Acesso por curl:** o proxy do ambiente recusou a conexão direta (403). Não foi tentado contorno.
- **Instruções dirigidas ao agente:** nenhuma foi encontrada nas páginas lidas.
