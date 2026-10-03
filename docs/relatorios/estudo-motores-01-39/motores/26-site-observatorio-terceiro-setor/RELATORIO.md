# Motor 26 — site-observatorio-terceiro-setor (Observatório do Terceiro Setor)

Estudo de 02/10/2026. Tipo: AGREGADOR (portal jornalístico que repercute editais de terceiros). Foram 38 chamadas de WebFetch, dentro do teto de cerca de 40. O curl direto ao domínio foi bloqueado pelo proxy de saída (CONNECT 403). Por isso todas as leituras foram feitas via WebFetch.

## 1. Rota (teste e conclusão)

**robots.txt** (`https://www.observatorio3setor.org.br/robots.txt`): `User-agent: *` e `Disallow: /dlm_uploads/`. Não há linha `Sitemap:`. As rotas usadas abaixo são permitidas.

| URL testada | Responde? | O que entrega |
|---|---|---|
| `https://www.observatorio3setor.org.br/secoes_tematicas/editais/feed/` (rota configurada) | Sim (RSS 2.0, lastBuildDate 30/09/2026) | 20 itens, de 18/08/2026 a 30/09/2026. Cada item traz título, link e pubDate. A descrição é um resumo truncado e não há `content:encoded` completo. O prazo aparece no texto sem ano ("inscrições até 13 de novembro"). O valor só aparece quando está no título ou no resumo. **O link oficial do financiador não vem no feed.** Não há `atom:link rel=next`. |
| `https://www.observatorio3setor.org.br/secoes_tematicas/editais/` (página do titular) | Sim | 12 posts por página, com paginação `/secoes_tematicas/editais/page/N/` e **43 páginas** no total (cerca de 516 posts). |
| `https://www.observatorio3setor.org.br/secoes_tematicas/editais/feed/?paged=N` | **Sim, testado de N=2 a N=26** | 20 itens por página. O arquivo termina em N=26 (15 itens, recuando até 2016). **É o caminho de histórico.** |
| `https://www.observatorio3setor.org.br/wp-json/wp/v2/types` e `/taxonomies` | Sim (API REST do WordPress aberta) | Só tem `post`, `category`, `post_tag` e afins. **A taxonomia `secoes_tematicas` não aparece na API.** |
| `https://www.observatorio3setor.org.br/wp-json/wp/v2/categories?slug=editais` | Sim | A categoria id 6667 "Editais" (pai 3, Notícias) tem `count` 484, com link `/category/noticias/editais/`. |
| `https://www.observatorio3setor.org.br/wp-json/wp/v2/posts?categories=6667&after=2023-10-02T00:00:00&before=2026-10-03T00:00:00&per_page=100&_fields=date,title,link` | Sim, mas **só 3 posts** | A seção temática não corresponde à categoria 6667. **A API REST não serve como rota.** |
| `https://www.observatorio3setor.org.br/wp-json/wp/v2/tags?search=edita` | Sim | Tags por edital específico (contagem 0–2). Não servem como rota. |

**Conclusão.** A rota configurada funciona e continua sendo a melhor para a cadência diária: é leve, tem pubDate e é estável. O problema é que ela só cobre cerca de 6 semanas. A melhor rota para histórico e reprocessamento é **`https://www.observatorio3setor.org.br/secoes_tematicas/editais/feed/?paged=N` (N=1…26)**, verificada nesta sessão. O janela de 3 anos corresponde às páginas 1 a 24: o item mais antigo da janela, de 04/10/2023, está na página 24. O feed nunca entrega o link oficial. Para obtê-lo é preciso abrir o post (`pagina_agregador`) e tirar o link do **corpo do artigo**, excluindo o rodapé e a caixa "Apoio". Ver a melhoria 3.

**Densidade.** Até meados de 2024 eram cerca de 1 a 2 posts por mês (páginas 23 a 24). Desde o 2º semestre de 2024 são cerca de 14 a 20 por mês. Estimativa: cerca de 470 posts na janela de 3 anos.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**Método.** Li o feed nas páginas 1, 2, 3, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24 e 25. São 14 de 26 páginas, cerca de 270 posts, e cobrem todos os semestres da janela. Também li as páginas HTML 1 e 4. Retirei conteúdo que não é oportunidade, como podcasts, notícias de resultado e artigos de dicas. As páginas 4, 5, 7, 9, 11, 13, 15, 17, 19, 21 e 23 **não foram lidas** por causa do limite de chamadas (ver seção 8).

**Regra de ano do prazo.** Quando a fonte dá o prazo sem ano, usei o ano da publicação e somei 1 se o mês do prazo for anterior ao mês da publicação. É o oposto do que o motor faz hoje (ver seção 6).

**Totais.** São **153 oportunidades extraídas**: 13 abertas, 111 encerradas (`encerrado_arquivar`) e 29 sem data. Há **120 financiadores ou órgãos distintos**. A aplicabilidade para uma OSC de Goiânia/GO ficou assim: 18 sim, 94 depende e 41 não. Há 29 itens com `criar_livro`, porque o site oficial foi confirmado nesta sessão, e 124 com `aguardar_fonte`.

### 2.1 Verificação por amostra de links oficiais do arquivo de indícios (12 links)

| # | Indício | link_oficial | Abre? | É do financiador? | Achado |
|---|---|---|---|---|---|
| 1 | Karibu Foundation | karibu.no/…/apply-for-a-grant… | sim | sim | Há ciclos em mar/mai/ago/out. Novos candidatos só entram por nota de interesse. O valor vai de US$ 5 mil a 20 mil. |
| 2 | Fundo Baobá — Marielle Franco | editais.baoba.org.br/programa-marielle-franco-2 | sim | sim | R$ 300 mil por organização, com 85% ou mais de mulheres negras na liderança. A página não mostra o prazo; o feed dá 19/10. |
| 3 | Fundação Maria Emília — FME Transforma | mariaemilia.org.br/edital-fme-transforma/ | sim | sim | Inscrições de 24/08/2026 a 30/10/2026, por formulário Google. **ABERTA.** |
| 4 | Fundo Brasil — apoio emergencial | fundobrasil.org.br/…/apoio-emergencial/ | sim | sim | Demanda contínua, pedido por e-mail. A seed está correta (prazo nulo). |
| 5 | Instituto Lojas Renner — Encantando Comunidades | institutolojasrenner.org.br/edital-encantando-comunidades/ | sim | sim | O prazo real é **21/09/2026**; a seed diz 2027-09-13. Atende só RS, RJ e SP. **Não se aplica a GO.** |
| 6 | iCS — Comunicação para Ação Climática | climaesociedade.org/edital/… | sim | sim | Inscrições de 03/08 a **31/08/2026**; a seed diz 2027-08-31. Inscrição pela plataforma Fluxx. |
| 7 | Fundo Ecos — Edital 49º | fundoecos.org.br/edital/edital-49o… | sim | sim (ISPN) | O prazo foi **31/08/2026** e a página marca "encerradas"; a seed diz 2027-08-31. Atende só MA, TO e MT. |
| 8 | Fundo Casa — Chamada Simplificada | casa.org.br/chamadas/… | sim | sim | Inscrições de 15/06 a **14/07/2026**; a seed diz 2027-07-30. Abrangência nacional, pelo sistema CasaDigital. |
| 9 | Cáritas Brasileira | caritas.org.br/editais-e-vagas | sim | sim | **É uma página genérica**: o edital específico não aparece. O link é fraco. |
| 10 | Enap — Prêmio MDHC | enap.gov.br/…/concurso-premio-mdhc/ | sim | sim | O prazo foi **29/09/2026**; a seed diz 2027-09-29. |
| 11 | Floresta+ Amazônia | florestamaisamazonia.org.br/editais/… | **não** | — | Tempo esgotado no robots.txt do site. O feed dá o prazo de 04/09 (2026); a seed diz 2027-09-04. |
| 12 | Sonhar o Mundo 2026 | conjunta.org/ | **não** | provavelmente não | Tempo esgotado. O post do agregador atribui o programa à SEC-SP/SISEM e à Fundação Energia e Saneamento, com inscrição por forms.cloud.microsoft. **O conjunta.org não é citado no corpo do texto.** |
| extra | Campus Mobile | escolaaberta3setor.org.br | — | **não** | O post mostra que esse domínio está na caixa **"Apoio" do rodapé**, não no corpo. O financiador é o Instituto Claro e o link do corpo é um bit.ly. **O motor capturou o anúncio do rodapé.** |

Resultado: 10 dos 12 links abrem e são do financiador, 2 caíram e 1 extra é errado. **Em 6 dos 7 indícios verificados com prazo, o ano do prazo estava errado (2027 em vez de 2026).**

### 2.2 Tabela do histórico extraído

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2026-09-30 | Sonhar o Mundo 2026 (instituições museológicas de SP) | Secretaria da Cultura de SP / SISEM-SP e Fundação Energia e Saneamento | (aguardar_fonte) | 2026-11-13 | aberto | nao |
| 2026-09-29 | Programa padrão de financiamento — Ásia, América Latina, Oriente Médio e Global | Karibu Foundation | https://www.karibu.no/our-partners/apply-for-a-grant-asia-latinamerica-middleeast-global/ | 2026-11-01 | aberto | depende |
| 2026-09-24 | Campus Mobile 2026 | Instituto Claro (com LSI-TEC, LSI-USP e beOn) | (aguardar_fonte) | 2026-10-18 | aberto | nao |
| 2026-09-22 | Edital Conta que Soma | — | (aguardar_fonte) | 2026-10-14 | aberto | depende |
| 2026-09-21 | Edital 2026 de seleção de projetos culturais incentivados | Parque Bondinho Pão de Açúcar | (aguardar_fonte) | 2026-10-09 | aberto | depende |
| 2026-09-18 | LUPPA — seleção de dez cidades para políticas alimentares | LUPPA (Instituto Comida do Amanhã / ICLEI) | (aguardar_fonte) | 2026-10-20 | aberto | nao |
| 2026-09-17 | Programa Marielle Franco — 2º Apoio Coletivo | Fundo Baobá | https://editais.baoba.org.br/programa-marielle-franco-2 | 2026-10-19 | aberto | depende |
| 2026-09-16 | Prêmio LED Globo 2027 | Globo (Movimento LED) | https://somos.globo.com/google/amp/movimento-led/premio-led/noticia/inscricoes-abertas-para-o-premio-led-globo-2027.ghtml | 2026-09-23 | encerrado_arquivar | sim |
| 2026-09-13 | Edital Rede Memória Viva — Iniciativa Viva Pequena África | Viva Pequena África | (aguardar_fonte) | 2026-10-03 | aberto | depende |
| 2026-09-11 | Chamada pública de projetos de eficiência energética | Grupo Equatorial | (aguardar_fonte) | 2026-11-09 | aberto | depende |
| 2026-09-10 | Edital FME Transforma | Fundação Maria Emília | https://mariaemilia.org.br/edital-fme-transforma/ | 2026-10-30 | aberto | sim |
| 2026-09-08 | Seleção de projetos sociais e culturais para captação via leis de incentivo | Redion | (aguardar_fonte) | 2026-09-14 | encerrado_arquivar | depende |
| 2026-09-02 | Edital Alimento no Prato — territórios urbanos | Ministério do Desenvolvimento Agrário (MDA) | (aguardar_fonte) | 2026-09-14 | encerrado_arquivar | depende |
| 2026-08-30 | Floresta+ Amazônia — apoio a projetos locais | Projeto Floresta+ Amazônia | (aguardar_fonte) | 2026-09-04 | encerrado_arquivar | nao |
| 2026-08-28 | Rede Memória Viva — inscrições de organizações | Viva Pequena África | (aguardar_fonte) | 2026-10-05 | aberto | depende |
| 2026-08-27 | Apoio emergencial a defensores de direitos humanos | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/nosso-trabalho/apoio-a-sociedade-civil/apoio-emergencial/ | — | sem_data | depende |
| 2026-08-26 | 1º Prêmio Nacional de Proteção Integral de Crianças e Adolescentes em Situação de Rua | Enap / SNDCA-MDHC | https://enap.gov.br/educacao-e-capacitacao/programa-de-aperfeicoamento-para-carreiras/premios/concurso-premio-mdhc/ | 2026-09-29 | encerrado_arquivar | sim |
| 2026-08-24 | Apoio a projetos em periferias | BNDES | (aguardar_fonte) | 2026-12-04 | aberto | depende |
| 2026-08-21 | Edital Encantando Comunidades | Instituto Lojas Renner | https://www.institutolojasrenner.org.br/edital-encantando-comunidades/ | 2026-09-21 | encerrado_arquivar | nao |
| 2026-08-18 | Edital de apoio a campanhas comunitárias — Dia de Doar | Dia de Doar | (aguardar_fonte) | 2026-08-28 | encerrado_arquivar | sim |
| 2026-08-15 | Comunicação para Ação Climática no Brasil | Instituto Clima e Sociedade (iCS) | https://climaesociedade.org/edital/comunicacao-para-acao-climatica-no-brasil/ | 2026-08-31 | encerrado_arquivar | sim |
| 2026-08-14 | Raízes — direitos, autonomia e sustentabilidade na Amazônia e no Cerrado | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | 2026-08-21 | encerrado_arquivar | sim |
| 2026-08-12 | Edital 49º — apoio a organizações na Amazônia Legal | Fundo Ecos (ISPN) | https://fundoecos.org.br/edital/edital-49o-3o-2026-para-apoio-a-organizacoes-na-amazonia-legal/ | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-11 | Edital de projetos de impacto social | Instituto Impactarte | (aguardar_fonte) | — | sem_data | depende |
| 2026-08-07 | Edital Territórios Clínicos 2026 (saúde mental) | Fundação Tide Setubal | (aguardar_fonte) | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-04 | Edital de apoio a organizações sociais | Movimento Bem Maior | (aguardar_fonte) | 2026-08-17 | encerrado_arquivar | depende |
| 2026-08-01 | Banco de Projetos Incentivados Municipais 2026 | Santos Brasil | (aguardar_fonte) | 2026-10-30 | aberto | nao |
| 2026-07-31 | Edital Ambev Brasilidades 2026 | Ambev | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | sim |
| 2026-07-30 | Edital de projetos incentivados | Instituto EDP | (aguardar_fonte) | 2026-08-31 | encerrado_arquivar | depende |
| 2026-07-28 | Edital para projetos de infância e adolescência | BNDES | (aguardar_fonte) | 2026-08-25 | encerrado_arquivar | depende |
| 2026-07-26 | Edital SFDT 02/2026 — sociobiodiversidade e plantas medicinais | Ministério do Desenvolvimento Agrário (MDA) | (aguardar_fonte) | 2026-08-09 | encerrado_arquivar | depende |
| 2026-07-24 | Edital Clima e Território (lideranças climáticas) | BONDE | (aguardar_fonte) | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-21 | iF Social Impact Prize | iF Design | (aguardar_fonte) | 2026-08-19 | encerrado_arquivar | depende |
| 2026-07-16 | Periferias Fortes — Norte e Nordeste | BNDES | (aguardar_fonte) | — | sem_data | nao |
| 2026-07-15 | Edital de projetos de impacto social, ambiental e educacional | Whirlpool | (aguardar_fonte) | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-14 | Dados e IA para promoção da saúde mental de crianças e adolescentes | Vital Strategies | (aguardar_fonte) | 2026-08-03 | encerrado_arquivar | depende |
| 2026-07-10 | Jornada Fortalecidas (formação de OSCs de direitos das mulheres) | Instituto Lojas Renner | https://www.institutolojasrenner.org.br/ | 2026-07-24 | encerrado_arquivar | depende |
| 2026-07-09 | Edital Transformação — aceleração de negócios de impacto | Instituto Sabin | (aguardar_fonte) | 2026-07-15 | encerrado_arquivar | nao |
| 2026-07-09 | Edital para coletivos culturais das periferias de SP | Ação Educativa | (aguardar_fonte) | 2026-07-20 | encerrado_arquivar | nao |
| 2026-07-08 | Edital de enfrentamento à violência sexual infantojuvenil | Cáritas Brasileira | https://caritas.org.br/ | 2026-07-17 | encerrado_arquivar | depende |
| 2026-07-01 | Programa de Bolsas de Filantropia da Ford | Fundação Ford | (aguardar_fonte) | 2026-08-15 | encerrado_arquivar | nao |
| 2026-07-01 | Processo seletivo de organizações de impacto social | Glocal Aceleradora | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | depende |
| 2026-06-26 | Chamada Simplificada — Apoio Direto a Iniciativas Comunitárias | Fundo Casa Socioambiental | https://casa.org.br/chamadas/chamada-simplificada-apoio-direto-a-iniciativas-comunitarias/ | 2026-07-14 | encerrado_arquivar | sim |
| 2026-06-26 | Edital de inclusão produtiva | Fundação Grupo Volkswagen | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | depende |
| 2026-06-23 | Apoio a projetos sociais | Fundação Salvador Arena | (aguardar_fonte) | 2026-07-13 | encerrado_arquivar | depende |
| 2026-06-21 | Prêmio Pacto Contra a Fome 2026 | Pacto Contra a Fome | (aguardar_fonte) | 2026-07-07 | encerrado_arquivar | sim |
| 2026-06-20 | Prêmio Nacional Liga STEAM 2026 | Fundação ArcelorMittal / UNESCO | (aguardar_fonte) | 2026-06-26 | encerrado_arquivar | nao |
| 2026-06-18 | Fundo de Cidadania Ativa (Campinas) | Casa Hacker | (aguardar_fonte) | — | sem_data | nao |
| 2026-06-17 | Pró-Memórias — preservação e digitalização de acervos | Programa Pró-Memórias | (aguardar_fonte) | 2026-08-02 | encerrado_arquivar | depende |
| 2026-06-16 | Coleta e reciclagem de óleo de cozinha usado | Petrobras | (aguardar_fonte) | 2026-07-03 | encerrado_arquivar | depende |
| 2026-06-14 | Adaptação climática em comunidades vulneráveis de 7 estados | Instituto Clima e Sociedade (iCS) | https://climaesociedade.org/ | 2026-07-01 | encerrado_arquivar | depende |
| 2026-06-09 | Patrimônio cultural Brasil–Holanda | Fundo Patrimonial Cultural | (aguardar_fonte) | 2026-06-30 | encerrado_arquivar | depende |
| 2026-06-08 | Programa Movimento Sustentável 2026/2027 | Auren Energia | (aguardar_fonte) | 2026-06-14 | encerrado_arquivar | depende |
| 2026-06-02 | Programa Incentivar (capacitação de projetos sociais) | Instituto Rumo | (aguardar_fonte) | 2026-06-10 | encerrado_arquivar | depende |
| 2026-06-02 | Juventude Solidária — projetos em territórios vulneráveis | Plataforma Juventude Solidária | (aguardar_fonte) | 2026-06-09 | encerrado_arquivar | depende |
| 2026-03-13 | Edital Educação com Cidadania 2026 | Instituto Chamex / IDIS | (aguardar_fonte) | 2026-04-03 | encerrado_arquivar | depende |
| 2026-03-12 | Programa Impacto Feminino | Instituto Rede Mulher Empreendedora | (aguardar_fonte) | 2026-03-16 | encerrado_arquivar | nao |
| 2026-03-10 | Reformas de espaços de OSCs | Fundação FEAC | (aguardar_fonte) | 2026-03-13 | encerrado_arquivar | nao |
| 2026-03-09 | Prêmio Melhores ONGs 2026 | Prêmio Melhores ONGs | (aguardar_fonte) | 2026-05-15 | encerrado_arquivar | sim |
| 2026-03-06 | Chamada Fundo Casa Socioambiental (mar/2026) | Fundo Casa Socioambiental | https://casa.org.br/ | 2026-03-25 | encerrado_arquivar | depende |
| 2026-03-04 | Patrimônio Cultural Indígena | FUNAI | (aguardar_fonte) | 2026-03-13 | encerrado_arquivar | nao |
| 2026-03-03 | Edital Instituto Tecendo Infâncias | Instituto Tecendo Infâncias | (aguardar_fonte) | — | sem_data | depende |
| 2026-02-28 | Feminismos Populares | Pacová | (aguardar_fonte) | 2026-03-31 | encerrado_arquivar | depende |
| 2026-02-26 | Programa Alimentação Saudável | Fundação Salvador Arena | (aguardar_fonte) | 2026-03-30 | encerrado_arquivar | depende |
| 2026-02-25 | Youth Climate Justice Fund | Youth Climate Justice Fund | (aguardar_fonte) | 2026-03-01 | encerrado_arquivar | depende |
| 2026-02-25 | Prêmio MapBiomas 2026 | MapBiomas | (aguardar_fonte) | 2026-03-22 | encerrado_arquivar | depende |
| 2026-02-23 | Combate ao desmatamento na Amazônia | Anater / MDA / MMA / Incra | (aguardar_fonte) | 2026-03-02 | encerrado_arquivar | nao |
| 2026-02-20 | Semeia 2026 | Fundação Cargill | (aguardar_fonte) | 2026-03-03 | encerrado_arquivar | depende |
| 2026-02-13 | Bolsas Instituto Max Fabiani | Instituto Max Fabiani | (aguardar_fonte) | 2026-03-13 | encerrado_arquivar | nao |
| 2026-02-11 | Pajubá em Movimento | Abong | (aguardar_fonte) | 2026-03-02 | encerrado_arquivar | nao |
| 2026-02-09 | Projeto Legado 2026 | Instituto Legado | (aguardar_fonte) | 2026-02-28 | encerrado_arquivar | depende |
| 2025-12-09 | Prêmio Isabel Salgado | Prêmio Isabel Salgado | (aguardar_fonte) | 2026-01-21 | encerrado_arquivar | depende |
| 2025-12-08 | Conservação de aves marinhas em ilhas brasileiras | BNDES | (aguardar_fonte) | 2025-12-12 | encerrado_arquivar | nao |
| 2025-12-04 | Edital de apoio a creches | Fundação Abrinq / Fundação Salvador Arena | (aguardar_fonte) | — | sem_data | depende |
| 2025-12-04 | Prevenção social da violência com juventudes | Governo de Pernambuco | (aguardar_fonte) | 2025-12-27 | encerrado_arquivar | nao |
| 2025-12-03 | Edital Prospera Sociobio | Projeto Sociobioeconomia na Amazônia | (aguardar_fonte) | 2026-01-09 | encerrado_arquivar | nao |
| 2025-12-01 | Fundo Hydro — projetos comunitários | Fundo Hydro | (aguardar_fonte) | 2026-01-06 | encerrado_arquivar | nao |
| 2025-11-27 | Redes de cooperação solidária | Ministério do Trabalho e Emprego (MTE) / SENAES | (aguardar_fonte) | 2025-12-06 | encerrado_arquivar | depende |
| 2025-11-26 | FIFA Global Citizen Education Fund | FIFA / Global Citizen | (aguardar_fonte) | 2025-12-31 | encerrado_arquivar | depende |
| 2025-11-25 | Pesquisas colaborativas na Amazônia e no Cerrado | Ministério da Ciência, Tecnologia e Inovação | (aguardar_fonte) | 2026-01-30 | encerrado_arquivar | nao |
| 2025-11-24 | Edital Floresta em Pé | Rede Transformar / Votorantim | (aguardar_fonte) | 2025-12-12 | encerrado_arquivar | nao |
| 2025-11-24 | Edital Ambev Brasilidades 2026 (abertura) | Ambev | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | sim |
| 2025-11-21 | Apoio a projetos sociais | Instituto Faber-Castell | (aguardar_fonte) | — | sem_data | depende |
| 2025-11-20 | Projetos de sociobiodiversidade | Fundo Casa Socioambiental | https://casa.org.br/ | 2025-12-16 | encerrado_arquivar | depende |
| 2025-11-18 | Prêmio MapBiomas (edição 2026) | MapBiomas | (aguardar_fonte) | 2026-03-22 | encerrado_arquivar | depende |
| 2025-11-17 | Doação de passagens aéreas | Instituto GOL | (aguardar_fonte) | 2025-11-30 | encerrado_arquivar | sim |
| 2025-10-17 | Juventudes indígenas na Amazônia Legal | UNFPA | (aguardar_fonte) | 2025-10-30 | encerrado_arquivar | nao |
| 2025-10-17 | Projetos via leis de incentivo em SP e RJ | Generali Brasil | (aguardar_fonte) | 2025-10-28 | encerrado_arquivar | nao |
| 2025-10-15 | Capacitação de OSCs em gestão de parcerias | Secretaria-Geral da Presidência da República | (aguardar_fonte) | — | sem_data | depende |
| 2025-10-13 | Apoio a projetos para pessoas com deficiência | SEPcD (AM) | (aguardar_fonte) | 2025-10-31 | encerrado_arquivar | nao |
| 2025-10-10 | Edital de Apoio à Filantropia Comunitária | Dia de Doar / ABCR | (aguardar_fonte) | 2025-10-23 | encerrado_arquivar | sim |
| 2025-10-08 | Projetos sustentáveis no Cerrado e na Caatinga | Fundo Ecos (ISPN) | https://fundoecos.org.br/ | 2025-11-10 | encerrado_arquivar | sim |
| 2025-10-08 | Bikeatona 2025 | Instituto Aromeiazero | (aguardar_fonte) | 2025-10-27 | encerrado_arquivar | depende |
| 2025-10-06 | Concurso Fotográfico de Direitos Humanos | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | 2025-10-20 | encerrado_arquivar | nao |
| 2025-10-06 | Convocatória de projetos incentivados | Muda Cultural | (aguardar_fonte) | — | sem_data | depende |
| 2025-10-03 | Edital Ouro Negro 2026 | Governo da Bahia | (aguardar_fonte) | 2025-10-15 | encerrado_arquivar | nao |
| 2025-09-30 | Equidade racial no câncer | Instituto Oncoguia | (aguardar_fonte) | 2025-10-17 | encerrado_arquivar | depende |
| 2025-09-29 | Qualificação profissional | Ministério do Trabalho e Emprego (MTE) | (aguardar_fonte) | 2025-10-15 | encerrado_arquivar | depende |
| 2025-09-26 | Edital Sementes da Ancestralidade | Fundação Cultural Palmares | (aguardar_fonte) | 2025-10-06 | encerrado_arquivar | sim |
| 2025-09-03 | Editais Sociais 2025 | Banco do Nordeste | (aguardar_fonte) | — | sem_data | nao |
| 2025-08-28 | Prêmio LED 2026 | Globo (Movimento LED) | https://somos.globo.com/ | 2025-09-03 | encerrado_arquivar | sim |
| 2025-08-26 | Desafio de proteção da vida marinha | Constellation | (aguardar_fonte) | 2025-09-22 | encerrado_arquivar | depende |
| 2025-08-22 | 5º Edital de Educação | ENGIE Brasil | (aguardar_fonte) | 2025-08-29 | encerrado_arquivar | depende |
| 2025-08-20 | Patrocínio via leis de incentivo | MAPFRE | (aguardar_fonte) | 2025-12-15 | encerrado_arquivar | depende |
| 2025-08-19 | Programa Rouanet Nordeste | Ministério da Cultura | (aguardar_fonte) | 2025-09-04 | encerrado_arquivar | nao |
| 2025-08-18 | Proteção de defensores de direitos humanos | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | — | sem_data | depende |
| 2025-08-13 | Edital Dabucury | CESE / COIAB | (aguardar_fonte) | 2025-08-31 | encerrado_arquivar | nao |
| 2025-08-11 | Malunga pelo Bem Viver | Fundo Agbara | (aguardar_fonte) | — | sem_data | nao |
| 2025-08-10 | Energia solar em organizações sociais | EDP | (aguardar_fonte) | — | sem_data | nao |
| 2025-07-20 | Justiça socioambiental na Bacia do Rio Doce | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | 2025-07-22 | encerrado_arquivar | nao |
| 2025-07-19 | Edital Fundo Juntos pela Amazônia | Fundo Juntos pela Amazônia | (aguardar_fonte) | 2025-08-04 | encerrado_arquivar | nao |
| 2025-07-18 | Formação e apoio a lideranças sociais | Fundação Fenômenos | (aguardar_fonte) | 2025-08-13 | encerrado_arquivar | depende |
| 2025-07-11 | Agricultura familiar sustentável | Fundo Socioambiental CAIXA | (aguardar_fonte) | — | sem_data | depende |
| 2025-07-09 | Qualidade de vida da população LGBTQIA+ | Fundo Positivo | (aguardar_fonte) | 2025-07-31 | encerrado_arquivar | depende |
| 2025-07-03 | Apoio a coletivos de periferia | Fundação Abrinq | (aguardar_fonte) | — | sem_data | depende |
| 2025-07-03 | Chamada de projetos incentivados 2025 | EDP Brasil | (aguardar_fonte) | 2025-08-04 | encerrado_arquivar | depende |
| 2025-07-02 | 7º Edital Itaú Esporte | Itaú Unibanco | (aguardar_fonte) | — | sem_data | depende |
| 2025-07-02 | Edital da Água | Mosaic Fertilizantes | (aguardar_fonte) | 2025-07-11 | encerrado_arquivar | depende |
| 2025-07-01 | Projetos sociais com incentivo fiscal | Zurich Seguros | (aguardar_fonte) | 2025-08-03 | encerrado_arquivar | depende |
| 2025-06-01 | VOA 2025 | Ambev | (aguardar_fonte) | 2025-06-17 | encerrado_arquivar | depende |
| 2025-05-30 | Edital Itaú Viver Mais | Itaú / Fundos da Pessoa Idosa | (aguardar_fonte) | 2025-06-12 | encerrado_arquivar | depende |
| 2025-05-28 | Projetos sociais liderados por mulheres | ONU Mulheres / Futuros Coletivos | (aguardar_fonte) | 2025-05-30 | encerrado_arquivar | depende |
| 2025-05-22 | Comunidades tradicionais da Amazônia | Fundo Casa Socioambiental | https://casa.org.br/ | — | sem_data | nao |
| 2025-05-22 | The Audacious Project | The Audacious Project / TED | (aguardar_fonte) | 2025-06-15 | encerrado_arquivar | depende |
| 2025-05-16 | Fundo Social Sicredi | Sicredi Integração RS/MG | (aguardar_fonte) | 2025-05-31 | encerrado_arquivar | nao |
| 2025-04-02 | Justiça climática liderada por jovens | Roots | (aguardar_fonte) | 2025-04-14 | encerrado_arquivar | depende |
| 2025-03-26 | IA para sustentabilidade | Instituto Clima e Sociedade (iCS) | https://climaesociedade.org/ | 2025-04-22 | encerrado_arquivar | depende |
| 2025-03-26 | 5º Edital Educação com Cidadania | Instituto Chamex / IDIS | (aguardar_fonte) | 2025-04-11 | encerrado_arquivar | depende |
| 2025-03-25 | Projetos via leis federais de incentivo | Agibank | (aguardar_fonte) | 2025-04-21 | encerrado_arquivar | depende |
| 2025-03-12 | Educação quilombola | Fundo Casa Socioambiental | https://casa.org.br/ | 2025-03-25 | encerrado_arquivar | depende |
| 2025-02-26 | Controle do tabaco | ACT Promoção da Saúde | (aguardar_fonte) | — | sem_data | depende |
| 2025-02-25 | Prêmio FGV — populações vulneráveis | FGV | (aguardar_fonte) | 2025-04-11 | encerrado_arquivar | depende |
| 2024-12-12 | Injustiças econômicas | Robert Bosch Stiftung | (aguardar_fonte) | 2024-12-15 | encerrado_arquivar | depende |
| 2024-12-11 | Programa ITAIPU Mais que Energia | Itaipu Binacional | (aguardar_fonte) | 2025-01-21 | encerrado_arquivar | depende |
| 2024-11-18 | Bolsas de pós-graduação | Fundação Maria Emília | https://mariaemilia.org.br/ | 2024-12-16 | encerrado_arquivar | nao |
| 2024-11-18 | Justiça climática liderada por mulheres | WomenStrong International | (aguardar_fonte) | 2024-11-30 | encerrado_arquivar | depende |
| 2024-10-30 | Igualdade de gênero | Plan International Brasil | (aguardar_fonte) | — | sem_data | depende |
| 2024-10-28 | Inclusão social de pessoas em situação de rua | Ministério da Justiça e Segurança Pública | (aguardar_fonte) | — | sem_data | depende |
| 2024-10-05 | Brigadas voluntárias contra incêndios florestais | Fundo Casa Socioambiental | https://casa.org.br/ | — | sem_data | depende |
| 2024-08-06 | 2º Prêmio Pacto Contra a Fome | Pacto Contra a Fome | (aguardar_fonte) | 2024-08-19 | encerrado_arquivar | sim |
| 2024-08-05 | Prêmio LED 2025 | Globo (Movimento LED) | https://somos.globo.com/ | 2024-08-12 | encerrado_arquivar | sim |
| 2024-08-05 | AIPÊ — turismo sustentável | AIPÊ / BNDES / Santander / Instituto Votorantim | (aguardar_fonte) | 2024-08-21 | encerrado_arquivar | depende |
| 2024-08-02 | Labora — trabalho digno no campo, águas e florestas | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | — | sem_data | depende |
| 2024-07-26 | Projeto Fermenta 2024 | Ambev | (aguardar_fonte) | 2024-07-31 | encerrado_arquivar | depende |
| 2024-07-24 | Edital Astraea para ativistas LGBTQI+ | Astraea Foundation | (aguardar_fonte) | — | sem_data | depende |
| 2024-06-06 | Prêmio Zayed de Sustentabilidade | Prêmio Zayed de Sustentabilidade | (aguardar_fonte) | 2024-06-23 | encerrado_arquivar | depende |
| 2024-05-30 | Porta de Saída 2024 | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/ | — | sem_data | depende |
| 2024-05-11 | 8º Edital Mulheres em Movimento | ELAS+ / ONU Mulheres | (aguardar_fonte) | — | sem_data | depende |
| 2024-04-10 | 4º Edital Educação com Cidadania | Instituto Chamex / IDIS | (aguardar_fonte) | — | sem_data | depende |
| 2024-03-07 | 6º Edital LGBT+ Orgulho | Itaú Unibanco / Instituto +Diversidade | (aguardar_fonte) | 2024-04-01 | encerrado_arquivar | depende |
| 2024-01-08 | Projetos de impacto social e ambiental | Itaipu Binacional / Caixa | (aguardar_fonte) | — | sem_data | depende |
| 2023-11-10 | Política Nacional Aldir Blanc (PNAB) | Ministério da Cultura | (aguardar_fonte) | — | sem_data | depende |
| 2023-10-26 | Projetos culturais, esportivos e sociais com incentivo fiscal | BASF | (aguardar_fonte) | — | sem_data | depende |

Itens com `(aguardar_fonte)` são aqueles cujo site oficial não foi aberto nesta sessão. A `pagina_agregador` de cada um está no livros.json.

## 3. Onde publica

- **O agregador.** O Observatório do Terceiro Setor (WordPress) publica uma notícia por edital na seção temática "Editais". Os mesmos posts saem no feed RSS da seção e na listagem paginada. O link para o financiador aparece **só no corpo do post**, quase sempre como "clique aqui". Às vezes é um encurtador (bit.ly) ou um formulário direto. O rodapé traz uma caixa "Apoio" com links de patrocinadores (escolaaberta3setor.org.br), que **não são financiadores dos editais**.
- **Os financiadores** publicam em lugares diferentes:
  - **Site próprio com página de edital**: Fundação Maria Emília, Instituto Lojas Renner, iCS, Fundo Ecos/ISPN, Fundo Brasil, Cáritas, Enap e Karibu.
  - **Subdomínio próprio de editais**: editais.baoba.org.br.
  - **Plataformas de inscrição**:
    - Prosas (Ambev, EDP, Santos Brasil, Viva Pequena África; aparece nos indícios);
    - Fluxx (iCS);
    - CasaDigital (Fundo Casa);
    - JotForm (Fundo Ecos);
    - Formulários Google ou Microsoft (Maria Emília, Sonhar o Mundo);
    - SurveyMonkey (Baobá);
    - sistema GMS próprio (Karibu);
    - Central de Inscrições da Enap;
    - e-mail (Fundo Brasil emergencial);
    - Simbi (Fundação VW, nos indícios).
  - **Gestoras de edital** para empresas: gestaocpp (Equatorial), Monitor Social (Auren), Ekloos (BNDES Periferias), Jornada Social (Sabin).
  - **Órgãos públicos**: gov.br/mda, bndes.gov.br e enap.gov.br.

## 4. Tipos de oportunidade

Classificação dos 153 itens extraídos:

| Tipo | Itens | O que entra |
|---|---|---|
| Edital de projeto | 110 | É a maioria. Inclui fundos independentes (Casa, Brasil, Baobá, Ecos, ELAS+, Agbara), institutos empresariais e editais de **seleção de projetos incentivados** (Ambev, EDP, Santos Brasil, Zurich, MAPFRE, Generali, Agibank). |
| Prêmio | 15 | LED/Globo, Pacto Contra a Fome, Melhores ONGs, MapBiomas, Enap/MDHC. |
| Chamada internacional | 10 | Karibu, FIFA/Global Citizen, Audacious/TED, Bosch, Astraea, Zayed, Youth Climate Justice Fund, iF Social Impact Prize. |
| Cadastro / banco de projetos | 3 | Rede Memória Viva, LUPPA, Muda Cultural. |
| Outro | 15 | Formação gratuita, aceleração, bolsas para pessoa física, doação de passagens (Instituto GOL) e apoio emergencial. |

O motor também traz ruído que não é oportunidade:
- vagas de docente (ITEC);
- notícias institucionais (Redes Bahia, Abrace uma Causa);
- podcasts e artigos de dicas no fim do arquivo.

**Faixas de valor**:
- micro: R$ 1 mil a 25 mil (Dia de Doar, Agência do Bem, Lojas Renner, Cáritas, Fundo Casa);
- médio: R$ 50 mil a 300 mil (Fundo Brasil, Baobá, Tide Setubal, Ecos, Impactarte);
- alto: R$ 500 mil a 2 milhões (iCS, BNDES Periferias, Maria Emília);
- carteiras incentivadas: R$ 12 milhões a 67 milhões no total (EDP, Ambev, Equatorial).

**Áreas**: socioambiental e clima (as mais frequentes), direitos humanos, equidade racial e de gênero, infância e adolescência, segurança alimentar, cultura e memória, esporte por incentivo e saúde mental.

**Quem pode participar**: na maioria, OSCs com CNPJ. Muitas aceitam coletivos sem CNPJ. Há recortes territoriais frequentes: Amazônia Legal, Norte/Nordeste, SP, RJ, RS e municípios de atuação da empresa. Esses recortes **excluem GO**, o que explica os 41 "não". Para Goiânia, o recorte "Cerrado" é favorável: Fundo Ecos Cerrado/Caatinga 2025, Fundo Brasil Raízes 2026 e Fundo Casa (brigadas contra incêndios).

## 5. Calendário

Distribuição por mês de publicação na amostra lida:

- **jun–set**: pico absoluto, com 20 posts por página de feed cobrindo cerca de 3 a 5 semanas. Saem nesse período os editais de projetos incentivados (Ambev, EDP, Itaú, Santos Brasil, Zurich), o LED/Globo (ago–set), o Pacto Contra a Fome (jun–ago), o Fundo Brasil (jul–ago) e o iCS (jun e ago).
- **out–dez**: segundo pico. Saem os editais de fim de ano e os prazos de dezembro e janeiro (BNDES, Fundo Casa sociobiodiversidade, Fundo Ecos Cerrado, FIFA, MTE, Dia de Doar em out).
- **fev–abr**: ciclo de começo de ano (Educação com Cidadania/Chamex em mar–abr, MapBiomas, Salvador Arena, Fundo Casa quilombola em mar, Cargill Semeia em fev).
- **jan e mai**: meses mais fracos.
- **Janela típica de inscrição**: 1 a 4 semanas depois do post, com mediana em torno de 15 a 20 dias. **Para não perder prazos, o motor precisa rodar no mínimo diariamente.**
- **Editais recorrentes anuais** que servem de previsão: Prêmio LED (ago–set), Pacto Contra a Fome (jun–ago), Educação com Cidadania (mar–abr), Dia de Doar (ago e out), Ambev (VOA em mai–jun; Brasilidades em nov–set), EDP incentivados (jul–ago), Fundo Brasil Raízes e Defensores (ago) e Karibu (mar/mai/ago/out).

## 6. Conselho de 7 lentes

1. **Dra. Helena Barros-Kuhn** (professora titular, pós-doutorado em Python; lente extremamente pessimista; seca e implacável): "O motor **mente sobre o ano**. Há 28 de 42 indícios com prazo em 2027, e nas verificações 6 de 6 eram de 2026 e já tinham vencido. Ele inferiu o ano comparando com *hoje* em vez de comparar com a *data do post*. Na prática, chama de aberto o que está encerrado. Para um sistema de captação, isso é o pior erro possível: o titular corre atrás de edital morto. Além disso, `financiador` está nulo em 41 de 42 e `valor` vale 'US$ 20 mil' em 12 de 42, um valor que vazou do post da Karibu. Isso é contaminação de estado entre itens."
2. **Rafael Monteiro** (chief engineer; pessimista; pragmático e desconfiado): "O `link_oficial` pega o primeiro link externo da página, inclusive o rodapé 'Apoio' (escolaaberta3setor.org.br no Campus Mobile) e home pages genéricas (conjunta.org, caritas.org.br/editais-e-vagas). O livro nasce com uma URL que não é do edital. Também não há filtro de público: Campus Mobile (estudantes), ITEC (vaga de docente) e LUPPA (prefeituras) entram como se fossem para OSC."
3. **Takeshi Arakaki** (staff engineer; levemente pessimista; metódico): "A rota só enxerga 20 itens. Nunca houve carga de histórico, embora o arquivo `?paged=N` exista e vá até a página 26. Sem histórico não há previsão de recorrência. Faltam UF e recorte territorial: 36 de 42 estão com `uf` nulo, e o único 'AL' está errado (BNDES Norte/Nordeste)."
4. **Marina Oliveira-Sato** (CTO de big tech; lente neutra; fecha a sessão; síntese abaixo).
5. **Prof. Diego Fontenelle** (pós-doutorado em Python, sistemas distribuídos; levemente otimista; didático): "A fonte é excelente para um agregador. É RSS limpo, com robots.txt permissivo e paginação estável, e a curadoria é voltada para OSC. Dos 12 links da amostra, 10 abriram e eram do financiador. O problema está no parser, não na fonte."
6. **Beatriz Quaresma** (chief engineer de plataforma; otimista; entusiasmada): "Em 3 anos são cerca de 470 posts e 120 financiadores distintos. É um **catálogo de quem financia OSC no Brasil**. Cada financiador vira um motor-alvo próprio (Fundo Casa, Fundo Brasil, Baobá, iCS, Ecos). O agregador funciona como descobridor de fontes, e isso vale mais do que os editais em si."
7. **Prof. Otávio Lindqvist** (pós-doutorado em computação, ex-CTO; extremamente otimista; visionário): "Com o ano corrigido, link do corpo, filtro de público e histórico, o motor 26 vira o radar nacional da A.M.C. Jardim América. Ele prevê LED, Pacto, Dia de Doar e Ambev com meses de antecedência e alimenta automaticamente a fila de 'aguardar_fonte' → 'criar_livro'. O ganho ideal é nunca mais perder um edital nacional aberto a OSC de Goiânia."

### Síntese do neutro (Marina Oliveira-Sato)

**Decisão.** **Manter a rota configurada como cadência diária e REBAIXAR a situação no painel de "satisfatória" para "requer correção"** até as melhorias 1 a 3 entrarem em produção. Hoje a contagem "42 achados" superestima as abertas: na data deste estudo, só cerca de 10 a 13 dos posts recentes têm prazo de 02/10/2026 em diante. **Acrescentar a rota de histórico `…/feed/?paged=N`.**

**Melhorias.** Lista numerada na seção 7.

**Parâmetros de qualidade** (meta):
- 0% de prazos com ano inferido após a data do post mais 13 meses;
- 100% dos prazos com ano ≥ ano de publicação e ≤ publicação + 12 meses;
- `link_oficial` fora do domínio do agregador e fora da lista de bloqueio (rodapé/apoio) em ≥ 95%;
- links que abrem (HTTP 200) em ≥ 90% numa amostra semanal de 10;
- `financiador` preenchido em ≥ 90%;
- `valor` igual a nulo quando ausente, nunca herdado: 0 valores repetidos entre itens distintos sem que estejam no texto;
- itens sem oportunidade (vaga, podcast, notícia) ≤ 5%;
- `uf`/recorte preenchido quando o texto cita estado ou bioma em ≥ 80%;
- latência entre publicação e captura ≤ 24 h.

**Riscos e mitigação:**

| Risco | Mitigação |
|---|---|
| R1. Prazo com ano errado marca edital encerrado como aberto. | Inferir o ano pela data do post. Se o prazo for menor que a data do post, somar 1 ano. Se o resultado ficar mais de 12 meses à frente, marcar `prazo_duvidoso` e não usar no alarme. |
| R2. Link de patrocinador ou rodapé vira "site oficial". | Extrair links só de `.entry-content` / `article`. Manter lista de bloqueio de domínios (observatorio3setor, escolaaberta3setor, redes sociais, bit.ly sem expansão). Seguir o redirecionamento do encurtador e validar o domínio. |
| R3. Cobertura curta (20 itens) perde editais se o motor ficar mais de 3 semanas parado. | Paginar `?paged=2..3` na rotina diária e `?paged=1..26` numa carga única de histórico, com deduplicação por URL do post. |
| R4. Mudança de layout ou WordPress quebra o parser. | Teste de contrato semanal: feed com ≥ 10 itens e pubDate válido. Alerta se o corpo do post vier sem nenhum link externo. |
| R5. Bloqueio ou timeout de sites de financiadores (Floresta+, conjunta.org caíram). | Repetir em até 24 h. Manter `aguardar_fonte` sem descartar. Não contornar o bloqueio. |
| R6. Ruído (vagas para pessoa física, chamadas para prefeituras). | Léxico negativo e campo `quem_pode`. Marcar `aplicavel: nao` em vez de descartar, para manter o histórico. |
| R7. Duplicatas (o mesmo edital noticiado duas vezes, por exemplo Fundo Ecos 21/07 e 12/08, Ambev nov/2025 e jul/2026, ou com prorrogação). | Chave de deduplicação = domínio do link oficial + título normalizado + ano. Atualizar o prazo em vez de criar um livro novo. |

## 7. Melhorias do motor (lista numerada)

1. **Prazo e ano (filtro/parse):** inferir o ano a partir da `pubDate` do post, nunca a partir da data de execução. Aceitar "até 13 de novembro", "13/11", "1º de novembro" e prorrogações. Validar a janela `pubDate ≤ prazo ≤ pubDate + 12 meses`. Reprocessar os 42 indícios atuais: 28 estão com 2027 suspeito.
2. **Valor:** extrair por item, do título e do resumo, com regex local. Zerar o estado entre itens, porque o 'US$ 20 mil' da Karibu vazou para 12 indícios. Distinguir "por projeto" de "total".
3. **Link oficial:** abrir o post e extrair links só do corpo do artigo (`article .entry-content`). Excluir a caixa "Apoio" e o rodapé. Aplicar lista de bloqueio de domínios (escolaaberta3setor.org.br, observatorio3setor.org.br, redes sociais). Expandir encurtadores (bit.ly) por HEAD. Priorizar âncoras "clique aqui", "edital", "inscrições" e "regulamento". Rejeitar home pages genéricas quando existir link mais profundo.
4. **Financiador:** extrair a organização do título (padrão "X abre/lança edital") e do primeiro parágrafo. Hoje está nulo em 41 de 42.
5. **Rota de histórico:** carga única de `https://www.observatorio3setor.org.br/secoes_tematicas/editais/feed/?paged=1..24`, que cobre a janela de 3 anos. Os itens vencidos vão para `encerrado_arquivar`. Na cadência diária, ler `?paged=1..2`.
6. **Cadência:** diária (o pico de jun–set publica de 3 a 5 por semana e as janelas duram de 1 a 4 semanas), com captura no máximo 24 h depois da pubDate.
7. **Léxico e filtro de público:** léxico positivo (edital, chamada, inscrições, prêmio, seleção, fundo). Léxico negativo (vaga, docente, seleciona professores, podcast, "dicas", "resultado", "selecionadas"). Marcar `aplicavel` como "nao" quando o público for "universitários", "estudantes", "pessoa física", "municípios" ou "prefeituras", ou quando houver recorte de UF ou bioma que exclua GO. Sinalizar positivamente "Cerrado", "Goiás", "Centro-Oeste" e "nacional".
8. **UF e recorte territorial:** extrair estados, regiões e biomas citados ("Amazônia Legal", "Norte e Nordeste", "MA, TO e MT") para `uf` e `area`. Corrigir o 'AL' indevido no item BNDES Norte/Nordeste.
9. **Deduplicação:** chave = domínio oficial + título normalizado + ano. Unir notícias repetidas do mesmo edital e prorrogações (por exemplo "prorroga inscrições"), atualizando o prazo.
10. **Descoberta de fontes:** gravar cada financiador novo (120 na amostra) numa fila de "motores candidatos". Promover os recorrentes que publicam no próprio site (Fundo Casa, Fundo Brasil, Baobá, iCS, Fundo Ecos, Maria Emília, Lojas Renner, Cáritas) a motores diretos.
11. **Painel:** separar "achados" de "abertos válidos". Hoje "42 achados / satisfatória" esconde que a maioria está vencida.

## 8. O que não foi confirmado e por quê

- **Páginas de feed 4, 5, 7, 9, 11, 13, 15, 17, 19, 21 e 23 não foram lidas.** O teto era de cerca de 40 chamadas e usei 38. Estimo cerca de 200 posts da janela fora desta extração. Eles devem entrar pela melhoria 5.
- **124 itens estão em `aguardar_fonte`**: o site oficial não foi aberto nesta sessão. O feed não traz links externos, e abrir cada post e cada site custaria cerca de 2 chamadas por item.
- **Prazos sem ano** nos itens do feed: o ano foi inferido pela regra "prazo ≥ data do post". Não foi confirmado no site oficial, exceto nos itens marcados `fonte: verificado`.
- **Floresta+ Amazônia e conjunta.org**: tempo esgotado ao ler o robots.txt de cada site. Não contornei.
- **Fundo Baobá**: a página oficial não mostra o prazo. O prazo de 19/10/2026 vem do feed do agregador.
- **Cáritas**: o link do indício leva a uma página genérica, sem o edital específico. O prazo (17/07/2026) vem do feed.
- **Karibu**: a página oficial dá meses de ciclo, sem ano explícito. O prazo de 01/11/2026 vem do feed. Novos candidatos dependem de convite após a nota de interesse.
- **API REST e categoria 6667**: só devolveram 3 posts. A seção temática usa uma estrutura que a API não expõe (não confirmada).
- **Curl direto**: bloqueado pelo proxy de saída (403 CONNECT). Usei só WebFetch.
- **Instruções em páginas dirigidas ao assistente**: nenhuma encontrada.
- **Dados pessoais**: nomes de pessoas físicas presentes nos posts (por exemplo, a parlamentar autora das "Emendas Sâmia" e as vereadoras do "Marinas por SP") não foram transformados em livros. Esses itens de emenda parlamentar ficaram fora do livros.json.
