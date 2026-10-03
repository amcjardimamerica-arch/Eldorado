# Motor 28 — site-abcr (ABCR — Associação Brasileira de Captadores de Recursos) — Relatório

Data do estudo: 02/10/2026. Janela do histórico: 02/10/2023 a 02/10/2026. Chamadas WebFetch usadas: 39 (limite ~40).
Observação técnica: `curl` direto para captadores.org.br é bloqueado pelo proxy (403 CONNECT); todos os testes foram feitos via WebFetch.
robots.txt (`https://captadores.org.br/robots.txt`): só bloqueia `/wp-admin/`; declara `Sitemap: https://captadores.org.br/wp-sitemap.xml`. Nada do que foi lido está proibido.
Nenhuma instrução dirigida ao agente foi encontrada no conteúdo das páginas.

## 1. Rota (teste e conclusão)

**Rota configurada:** `https://captadores.org.br/category/editais/feed/` (feed). **Página do titular:** `https://captadores.org.br/category/editais/`.

| URL testada | Resposta | O que entrega |
|---|---|---|
| `https://captadores.org.br/category/editais/feed/` | 200, RSS | **10 itens** (último build 28/09/2026), com `pubDate` e **`content:encoded` completo**: no texto aparecem prazo, valor, público e link oficial. Não há campos estruturados de prazo/valor — precisam ser extraídos do texto. |
| `https://captadores.org.br/category/editais/feed/?paged=N` | 200, RSS | **Paginação do feed funciona**: N=2…31 testados, 10 itens por página, com conteúdo completo. N=31 chega a 27/10/2023 (limite da janela). É o caminho do histórico. |
| `https://captadores.org.br/category/editais/feed/?m=202506` | 200, mas **ignora o filtro** | devolve os 10 mais recentes — filtro por mês não serve. |
| `https://captadores.org.br/category/editais/` | 200, HTML | 12 itens por página, só título, data e link; "Página 1 de 34". Não traz prazo/valor/link oficial. |
| `https://captadores.org.br/category/editais/page/2/` | (indicada pela página) | paginação HTML; não usada, o feed paginado é melhor. |
| `https://captadores.org.br/wp-json/wp/v2/categories?slug=editais` | 200, JSON | categoria **id 162**, **402 posts** no total. |
| `https://captadores.org.br/wp-json/wp/v2/posts?categories=162&per_page=40&after=2023-10-02T00:00:00&_fields=date,slug` | 200, JSON | API REST do WordPress responde e aceita `after`, `per_page`, `page`; o parâmetro `_fields` **parece ignorado** (resposta pesada) e o WebFetch truncou em ~14 itens por chamada. Num leitor próprio (requests) não há esse limite. |
| `https://captadores.org.br/wp-sitemap.xml` | 200 | índice com `wp-sitemap-posts-post-1..3.xml` (todos os posts do site, não só editais) — útil só para auditoria. |

**Conclusão:** a rota configurada **responde e é boa** (feed com conteúdo completo, link oficial no corpo). Melhorias verificadas:
1. Para cadência diária, manter `https://captadores.org.br/category/editais/feed/` (10 itens cobrem ~3–4 semanas; o site publica ~6–10 editais/mês).
2. Para o histórico e a recuperação de falhas, usar `https://captadores.org.br/category/editais/feed/?paged=N` (N=1…31 cobre 02/10/2023→hoje; ~41 páginas no total) **ou** a API REST `https://captadores.org.br/wp-json/wp/v2/posts?categories=162&after=AAAA-MM-DDT00:00:00&per_page=100&page=N` (mesmo conteúdo, com `date` ISO e `content.rendered`).

**Defeitos graves do que o sistema guardou (14 indícios em `sementes/28_site-abcr.json`):**
- **Ano do prazo errado em 10 de 10 prazos preenchidos**: todos vêm como 2027 quando a fonte diz 2026 (ex.: CONANDA 17/09/2026 → gravado 2027-09-17; BNB 13/09/2026 → 2027-09-13; Futuro Bem Maior 17/08/2026 → 2027-08-17). O leitor deduz "próximo ano" quando o mês do prazo já passou em relação à data de leitura (02/10), em vez de usar a data de publicação do post. **Resultado: editais encerrados aparecem como abertos** — explica parte dos "18 achados" do painel.
- ContraFluxo: prazo real 08/10/2026, gravado 2027-07-13 (data sem relação com o texto).
- **link_oficial errado em 2 indícios**: ContraFluxo → `pesquisavoluntariado.org.br` (site do IDIS sobre pesquisa de voluntariado, sem relação); Futuro Bem Maior → `meufuturosite.shop/elementor-7/` (domínio não resolve DNS; o oficial é `editais.movimentobemmaior.org.br/2026/`). O leitor está pegando o primeiro link externo do corpo/rodapé, não o link do edital.
- **link_oficial pouco útil em 2**: BNB → página de login do ConveniosWeb (o feed traz `bnb.gov.br/web/guest/sustentabilidade/investimentos-sociais-e-esportivos`); Juventude Solidária → notícia gov.br que hoje exige autenticação.
- **UF errada**: CONANDA gravado "AM" (é nacional), BNB "ES" (é Nordeste + norte de MG/ES), Futuro Bem Maior "BA" (nacional), Porto "SP" (seis estados). O leitor pega a primeira sigla de estado do texto.
- **Valor errado**: ContraFluxo "R$ 600 mil" (não há repasse, é produção de vídeo), Impactos Positivos "R$ 600 mil" (fonte não informa valor), Juventude "R$ 12 mil" (correto), Rio Doce "R$ 225 milhões" (total, não por projeto).
- `financiador` vem `null` em todos os 14.
- Santa Luzia do Paruá é **licitação (diálogo competitivo) para contratar empresa de captação**, não oportunidade de fomento para OSC — ruído.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**Método:** feed paginado com `content:encoded`. Pelo limite de ~40 chamadas, foram lidas as páginas **1 a 11** (cobertura contínua de 17/09/2025 a 29/09/2026) e as páginas-amostra **14, 19, 24, 30 e 31** (mai–jun/2025, dez/2024–jan/2025, jul/2024, out/2023–fev/2024). Ficaram **sem leitura** as páginas 12–13, 15–18, 20–23 e 25–29 (~150 posts, estimativa). O universo do período é de ~310 posts (31 páginas × 10).

Resultado deste estudo: **160 posts lidos → 159 oportunidades** (2 posts do IDIS IA unidos; 2 posts de Santa Luzia unidos; o post do Ministério das Mulheres desdobrado em 2 editais).
- **6 abertas**, **145 encerradas (encerrado_arquivar)**, **8 sem data**;
- aplicáveis a OSC de Goiânia/GO: **34 sim**, **64 dependem**, **61 não**;
- **139 criar_livro** (com site/página oficial do financiador ou da plataforma de inscrição indicada por ele) e **20 aguardar_fonte** (só Google Forms, bit.ly, short.gy, Sway, Drive, Qualtrics, Forms Office, e-mail ou link truncado);
- **~115 financiadores distintos**.

Critérios: prazo sem ano na fonte teve o ano deduzido pela **data de publicação do post** (primeira ocorrência daquele dia/mês depois da publicação) — é a regra que o motor deveria usar. Páginas Prosas/Bússola Social/Funbio Chamadas/AGO Social foram aceitas como página oficial de inscrição indicada pelo financiador.

**Verificação por amostra dos links oficiais dos indícios (12 de 14):**

| indício | link_oficial do sistema | resultado |
|---|---|---|
| ContraFluxo | pesquisavoluntariado.org.br | **abre, mas é do IDIS (pesquisa de voluntariado) — link errado** |
| Futuro Bem Maior | meufuturosite.shop/elementor-7/ | **não abre (DNS não resolve) — link errado** |
| CONANDA/SNDCA 01/2026 | gov.br/mdh/…/SEI_MDHC5765902Edital.pdf | abre; é o edital oficial; prazo 17/09/2026 (encerrado) |
| BNDES Periferias em Rede | bndes.gov.br/periferias | abre; oficial; prazo 04/12/2026 (**aberto**) |
| Funbio RPPN plano de manejo | chamadas.funbio.org.br/planodemanejo-rppn | abre; oficial; "Chamada Encerrada", prazo 25/09/2026 |
| Prêmio Impactos Positivos | impactospositivos.com | abre; oficial; inscrições 2026 encerradas |
| Desafio saúde mental (Vital Strategies) | desafiosaudemental.prosas.com.br | **não verificado — robots.txt do Prosas bloqueia** |
| Periferias Fortes Norte | periferiasfortes.phi.org.br | abre; Instituto Phi (operador com BNDES); inscrição completa até 07/10/2026 (**aberto**, só Norte + MA) |
| Rio Doce (FBB) | fbb.org.br/edital-publico/editalriodoce/ | abre; oficial; encerrado 29/07/2026 |
| Zurich Impulsiona | zurich.com.br/zurich-impulsiona | abre; oficial; encerrado e concluído |
| Edital Social Porto | investidor.bussolasocial.com.br/portoseguro/… | abre, mas página é SPA sem conteúdo legível |
| Juventude Solidária | gov.br/secretariageral/…/juventude-solidaria… | **exige autenticação ("Conteúdo Restrito")** |

Não abertos (para poupar chamadas / regra de não logar): BNB ConveniosWeb (é tela de login) e Santa Luzia do Paruá.
Fora dos indícios também foram abertos: `zurich.com.br/leis-de-incentivo-2026` (oficial, aberto até 19/10/2026) e `patrocinio.embratur.com.br` (abre, mas sem conteúdo legível).

**Oportunidades abertas (prazo ≥ 02/10/2026):**
1. Zurich – Seleção de Projetos via Leis de Incentivo 2026 — até 19/10/2026 — nacional, OSC com projeto aprovado (Rouanet, Esporte, Fundo Idoso, FIA) — **depende** (precisa de projeto incentivado aprovado). *Não está nos indícios.*
2. Fundação Maria Emília – FME Transforma 02/2026 — até 30/10/2026 — até R$ 1 milhão, saúde e educação — **depende**; só Google Forms → aguardar_fonte. *Não está nos indícios.*
3. BNDES Periferias em Rede (6º ciclo) — até 04/12/2026 — projeto mínimo R$ 20 milhões, entidade gestora que apoia organizações de base — **depende** (porte).
4. BNDES Periferias Fortes Norte — até 07/10/2026 — **não** (só Norte e MA).
5. ContraFluxo (Curitiba) — até 08/10/2026 — **não**.
6. Credenciamento FMC Bombinhas (SC) — até 27/11/2026 — **não**.

Também na pauta (não "abertos" pela regra, mas de interesse): Embratur patrocínio 2026 (post de 06/01/2026 cita "3 de outubro" sem ano; site oficial sem conteúdo legível → sem_data), Instituto Impactarte (edital contínuo, cultura incentivada) e Sebrae-SP credenciamento (permanente).

Tabela completa (159 oportunidades; ordem do feed, mais recentes primeiro):

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2026-09-28 | Edital de Seleção de Projetos via Leis de Incentivo Fiscal 2026 | Zurich Seguros | https://www.zurich.com.br/leis-de-incentivo-2026 | 2026-10-19 | aberto | depende |
| 2026-09-18 | ContraFluxo: filme gratuito para uma OSC de Curitiba | Festival ContraFluxo / Trópico Audiovisual | (aguardar_fonte) | 2026-10-08 | aberto | nao |
| 2026-09-15 | Edital MAPFRE 2026 (projetos incentivados) | MAPFRE Brasil | https://mapfre.hubdoincentivo.com.br | 2026-09-30 | encerrado_arquivar | depende |
| 2026-09-06 | Edital de Chamamento Público CONANDA/SNDCA nº 01/2026 | Ministério dos Direitos Humanos e da Cidadania / CONANDA | https://www.gov.br/mdh/pt-br/navegue-por-temas/crianca-e-adolescente/publicacoes/editais/SEI_MDHC5765902Edital.pdf | 2026-09-17 | encerrado_arquivar | sim |
| 2026-09-04 | Edital FME Transforma nº 02/2026 | Fundação Maria Emília | (aguardar_fonte) | 2026-10-30 | aberto | depende |
| 2026-08-27 | Edital Encantando Comunidades: Recursos Flexíveis | Instituto Lojas Renner | https://www.institutolojasrenner.org.br/edital-encantando-comunidades/ | 2026-09-13 | encerrado_arquivar | nao |
| 2026-08-26 | Editais Sociais 2026 (incentivos fiscais) | Banco do Nordeste | https://www.bnb.gov.br/web/guest/sustentabilidade/investimentos-sociais-e-esportivos | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-21 | BNDES Periferias em Rede – Chamada Permanente do Fundo Socioambiental (6º ciclo) | BNDES | https://bndes.gov.br/periferias | 2026-12-04 | aberto | depende |
| 2026-08-20 | Edital Territórios Clínicos (3ª edição) | Fundação Tide Setubal | https://conteudo.fundacaotidesetubal.org.br/edital-territorios-clinicos-2026 | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-17 | 6º Edital de Microprojetos – São Paulo | Agência do Bem / Rede do Bem | https://rededobem.org.br/editais/6-edital-de-microprojetos-sao-paulo/ | 2026-08-22 | encerrado_arquivar | nao |
| 2026-08-10 | BNDES Periferias Fortes – Nordeste | BNDES / Instituto Ekloos | https://www.ekloos.org/periferiasfortes | 2026-08-12 | encerrado_arquivar | nao |
| 2026-08-06 | Editais de fortalecimento institucional 2026 (Movimento Bem Maior e parceiros) | Movimento Bem Maior / Brainvest / Instituto Ivete Sangalo / Instituto Lina Galvani | https://editais.movimentobemmaior.org.br/2026/ | 2026-08-17 | encerrado_arquivar | sim |
| 2026-08-05 | Edital Banrisul – premiação de 50 organizações do RS | Banrisul Instituto Cultural e Social | https://banrisulcultural.com.br/ | 2026-08-21 | encerrado_arquivar | nao |
| 2026-06-10 | Edital de Diálogo Competitivo nº 002/2026 – contratação de organização de captação de recursos | Prefeitura de Santa Luzia do Paruá (MA) | https://www.santaluziadoparua.ma.gov.br/licitacaolista.php?id=731 | — | sem_data | nao |
| 2026-07-31 | 6º Edital Futuro Bem Maior | Movimento Bem Maior / Instituto Phomenta / Instituto Phi | https://editais.movimentobemmaior.org.br/2026/ | 2026-08-17 | encerrado_arquivar | sim |
| 2026-07-28 | Chamada 07/2026 – Implementação de Planos de Manejo de RPPNs (Programa Biodiversidade Litoral do Paraná) | FUNBIO / Programa Biodiversidade Litoral do Paraná | https://chamadas.funbio.org.br/planodemanejo-rppn | 2026-09-25 | encerrado_arquivar | nao |
| 2026-07-28 | Edital de projetos sociais ArcelorMittal Pecém | ArcelorMittal Pecém | (aguardar_fonte) | 2026-08-16 | encerrado_arquivar | nao |
| 2026-07-22 | Prêmio Impactos Positivos 2026 (6ª edição) | Impactos Positivos (patrocínio Sebrae) | https://impactospositivos.com/ | 2026-07-24 | encerrado_arquivar | depende |
| 2026-07-14 | Edital Social Porto 2026 (projetos incentivados) | Grupo Porto | https://investidor.bussolasocial.com.br/portoseguro/editais/ | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-14 | Desafio Dados e IA para a Promoção da Saúde Mental de Crianças e Adolescentes | Vital Strategies / Google.org | https://desafiosaudemental.prosas.com.br/ | 2026-08-03 | encerrado_arquivar | depende |
| 2026-07-07 | Edital de microprojetos – Região Metropolitana do RJ | Agência do Bem | (aguardar_fonte) | 2026-07-24 | encerrado_arquivar | nao |
| 2026-07-06 | BNDES Periferias Fortes – Norte e Maranhão | BNDES / Instituto Phi / Instituto Phomenta | https://periferiasfortes.phi.org.br/ | 2026-10-07 | aberto | nao |
| 2026-07-02 | Jornada Fortalecidas (formação para OSCs de gênero) | Instituto Lojas Renner / Instituto ACP | https://www.institutolojasrenner.org.br/jornada-fortalecidas/ | 2026-07-24 | encerrado_arquivar | depende |
| 2026-07-01 | Edital Rio Doce Participativo e Comunitário | Fundação Banco do Brasil | https://fbb.org.br/edital-publico/editalriodoce/ | 2026-07-29 | encerrado_arquivar | nao |
| 2026-06-23 | 2º Edital Somando Impactos | Fundação Grupo Volkswagen | https://selecao.simbi.social/fgvw | 2026-07-22 | encerrado_arquivar | depende |
| 2026-06-18 | Glocal Aceleradora – seleção de projetos (ciclo 2026) | Glocal Aceleradora | https://aceleradora.glocal.org.br/ | 2026-07-22 | encerrado_arquivar | nao |
| 2026-06-15 | Edital PAPS – Fundação Salvador Arena | Fundação Salvador Arena | https://www.papsfsa.com.br/ | 2026-07-13 | encerrado_arquivar | sim |
| 2026-06-08 | Zurich Impulsiona 2026 (capacitação e mentoria) | Zurich Seguros / Civicus | https://www.zurich.com.br/zurich-impulsiona | 2026-06-26 | encerrado_arquivar | sim |
| 2026-06-01 | Plataforma Juventude Solidária | Secretaria Nacional de Juventude / Secretaria-Geral da Presidência, MEC e MDS | (aguardar_fonte) | 2026-06-09 | encerrado_arquivar | depende |
| 2026-05-27 | Edital Agitando Pensamentos 2026 | Fundo SAAP / FASE | https://fase.org.br/pt/acervo/documentos/edital-agitando-pensamentos-2026-roteiro/ | 2026-06-08 | encerrado_arquivar | sim |
| 2026-05-26 | Consultoria gratuita para OSCs | Fundação Salvador Arena | http://www.fundacaosalvadorarena.org.br/ | 2026-05-31 | encerrado_arquivar | sim |
| 2026-05-26 | Credenciamento de consultores e instrutores do Programa SOMA Sebrae | Sebrae/SP | https://contato.sebraesp.com.br/credenciamento/ | — | sem_data | depende |
| 2026-05-19 | Programa Movimento Sustentável – ciclo 2026/2027 | Auren Energia | https://monitorsocial.org.br/auren/edital/22-programa-movimento-sustentavel-ciclo-20262027 | 2026-05-31 | encerrado_arquivar | nao |
| 2026-05-16 | Edital Itaú Viver Mais 2026 | Itaú Viver Mais | http://www.itauvivermais.com.br/pilares/editais/edital-ivm-2026 | 2026-06-12 | encerrado_arquivar | depende |
| 2026-05-08 | Formação em Captação e Gestão para Organizações de Periferia | Fiocruz / SOCULTFio / Secretaria Nacional de Periferias | https://socultfio.org.br/wp-content/uploads/2026/04/Chamamento-Formacao-em-Captacao-e-Gestao-para-Organizacoes-de-Periferia.pdf | 2026-05-13 | encerrado_arquivar | depende |
| 2026-05-07 | Nutrindo Soluções Locais – 6ª edição (Região Sul) | Fundação Cargill | https://fundacaocargill.org.br/nutrindo-solucoes-locais/ | 2026-05-25 | encerrado_arquivar | nao |
| 2026-05-07 | Edital Instituto Alcoa 2026 | Instituto Alcoa | https://institutoalcoa.sponsor.com/ | 2026-05-29 | encerrado_arquivar | nao |
| 2026-05-06 | Ambev VOA 2026 | Ambev | https://conteudo.agosocial.com.br/ambev-voa | 2026-05-07 | encerrado_arquivar | sim |
| 2026-05-05 | Edital nº 2/2026 UNAIDS/DATHI – ações comunitárias em HIV/aids e ISTs | Ministério da Saúde / UNAIDS | https://unaids.org.br/wp-content/uploads/2026/04/2026-Edital-2-UNAIDS-DATHI-220426-12h54min.pdf | 2026-05-22 | encerrado_arquivar | depende |
| 2026-04-28 | Edital Instituto Porto – educação na Grande São Paulo | Instituto Porto | https://investidor.bussolasocial.com.br/portoseguro/editais/Edital%20Social_Porto%202026 | 2026-05-22 | encerrado_arquivar | nao |
| 2026-04-22 | iFood Chega Junto 2026 | iFood | https://institucional.ifood.com.br/entregadores/ifood-chega-junto/ | 2026-05-04 | encerrado_arquivar | depende |
| 2026-04-15 | Desafio de Acesso à Justiça – 8ª edição | Instituto Mattos Filho | https://institutomattosfilho.org/desafio-de-acesso-a-justica/ | 2026-04-28 | encerrado_arquivar | sim |
| 2026-04-08 | Laboratório de Projetos 2026 | Instituto Cactus | https://institutocactus.org.br/inscricoes-abertas-para-o-laboratorio-de-projetos-2026/ | 2026-04-30 | encerrado_arquivar | depende |
| 2026-04-03 | Edital democracia e incidência política (20 OSCs) | Fundo OSC / Cáritas Brasileira | (aguardar_fonte) | 2026-05-31 | encerrado_arquivar | sim |
| 2026-03-31 | Edital inclusão socioprodutiva de mulheres | Instituto Lojas Renner | https://www.institutolojasrenner.org.br/edital/ | 2026-05-18 | encerrado_arquivar | sim |
| 2026-03-26 | Edital da Água 2026 | MOSAIC / IDIS | https://www.idis.org.br/mosaic-abre-inscricoes-para-o-edital-da-agua-2026-com-foco-em-eficiencia-no-saneamento-rural-e-a-agua-potavel/ | 2026-04-24 | encerrado_arquivar | sim |
| 2026-03-24 | 2º Edital conjunto Raízes e Labora | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/noticia/segundo-edital-conjunto-raizes-e-labora-destinam-r-225-milhoes-para-solucoes-climaticas-construidas-nos-territorios/ | 2026-05-08 | encerrado_arquivar | depende |
| 2026-03-18 | Programa SAP/ASID – capacitação para OSCs de pessoas com deficiência | SAP / ASID Brasil | (aguardar_fonte) | 2026-04-20 | encerrado_arquivar | nao |
| 2026-03-17 | Prêmio Empreendedor Social 2026 | Folha de S.Paulo / Fundação Schwab | https://prosas.com.br/editais/17400-pr-mio-empreendedor-social-2026?locale=pt | 2026-04-30 | encerrado_arquivar | depende |
| 2026-03-10 | Prêmio Impacta Mais 2026 | Companhia de Impacto / Certificadora Social | https://impactamais.com/premio-impacta-mais-2026/ | 2026-03-16 | encerrado_arquivar | depende |
| 2026-03-04 | Programa contra a insegurança alimentar | Fundação Salvador Arena | https://www.pasfsa.com.br | 2026-03-30 | encerrado_arquivar | sim |
| 2026-03-03 | Edital Instituto Tecendo Infâncias | Instituto Tecendo Infâncias | https://prosas.com.br/editais/17443?locale=pt | 2026-04-24 | encerrado_arquivar | sim |
| 2026-03-02 | 6º Edital Educação com Cidadania | Instituto Chamex | https://institutochamex.com.br/inscricoes-abertas-instituto-chamex-lanca-sexto-edital-educacao-com-cidadania/ | 2026-04-03 | encerrado_arquivar | sim |
| 2026-02-27 | Chamada pública OIM – projetos comunitários na Amazônia | Organização Internacional para as Migrações (OIM) | https://brazil.iom.int/pt-br/news/oim-lanca-chamada-publica-para-apoiar-projetos-comunitarios-na-amazonia | 2026-03-06 | encerrado_arquivar | nao |
| 2026-02-23 | Chamada Feminismos Populares em Defesa do Bem Viver e dos Territórios | Pacová | https://pacova.org/2026/02/20/chamada-feminismos-populares-em-defesa-do-bem-viver-e-dos-territorios/ | 2026-03-31 | encerrado_arquivar | depende |
| 2026-02-18 | Chamada pública Fundo do Idoso | Cemig | https://prosas.com.br/editais/16509 | 2026-07-13 | encerrado_arquivar | nao |
| 2026-02-17 | Prêmio Zayed de Sustentabilidade – ciclo 2027 | Prêmio Zayed (Emirados Árabes Unidos) | https://www.zayedsustainabilityprize.com | 2026-06-15 | encerrado_arquivar | depende |
| 2026-02-10 | Chamada Semeia 2026 | Fundação Cargill | https://fundacaocargill.org.br/ | 2026-03-03 | encerrado_arquivar | sim |
| 2026-02-09 | Consultoria gratuita ESPM Social 2026 | ESPM Social | https://www.espmsocial.org | 2026-02-23 | encerrado_arquivar | nao |
| 2026-02-04 | Chamada de avaliação de impactos ambientais (Programa Biodiversidade Litoral do Paraná) | FUNBIO | https://chamadas.funbio.org.br/avaliacao-de-impactos | 2026-02-27 | encerrado_arquivar | nao |
| 2026-01-29 | Projeto Legado 2026 | Instituto Legado de Empreendedorismo Social | https://institutolegado.org/aceleracao/projeto-legado/ | 2026-02-28 | encerrado_arquivar | depende |
| 2026-01-29 | Edital contínuo Instituto Impactarte | Instituto Impactarte | https://impactarte.org.br/cadastro-proponente | — | sem_data | depende |
| 2026-01-27 | Prêmio FGV de Responsabilidade Social – 3ª edição | FGV / Globo / Aegea | https://premioresponsabilidadesocial.fgv.br/ | 2026-03-31 | encerrado_arquivar | sim |
| 2026-01-26 | Aceleração AXIA (40 ONGs) | AXIA Energia / Instituto Phomenta | (aguardar_fonte) | 2026-02-27 | encerrado_arquivar | depende |
| 2026-01-22 | Credenciamento de empresas culturais (Lei Rouanet) – FMC Bombinhas | Fundação Municipal de Cultura de Bombinhas (SC) | https://mapacultural.cim-amfri.sc.gov.br/oportunidade/178/ | 2026-11-27 | aberto | nao |
| 2026-01-19 | Chamada Comunicação Popular Fortalecendo Lutas | Pacová | https://pacova.org/2026/01/13/chamada-comunicacao-popular-fortalecendo-lutas/ | 2026-03-16 | encerrado_arquivar | depende |
| 2026-01-15 | Glocal Aceleradora – 14º ciclo | Glocal Aceleradora | https://aceleradora.glocal.org.br/ | 2026-02-04 | encerrado_arquivar | nao |
| 2026-01-12 | Edital de projetos sociais Instituto de Ação Social 2026 | Capemisa – Instituto de Ação Social | https://investidor.bussolasocial.com.br/capemisa_social/editais/projetossociais_institutoacaosocial2026 | 2026-02-12 | encerrado_arquivar | sim |
| 2026-01-07 | Edital LGBTQIA+ Defendendo Direitos 2026 | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/lgbtqia-defendendo-direitos-2026 | 2026-02-06 | encerrado_arquivar | depende |
| 2026-01-06 | Edital de patrocínio Embratur (2026) | Embratur | https://patrocinio.embratur.com.br | — | sem_data | depende |
| 2025-12-26 | Edital de restauro do patrimônio histórico de MG | Cemig | https://prosas.com.br/editais/16768 | 2026-03-12 | encerrado_arquivar | nao |
| 2025-12-22 | Edital de microinvestimento – Zona Oeste do RJ e Cabreúva | Instituto Lojas Renner | https://www.institutolojasrenner.org.br/edital-de-microinvestimento-rio-de-janeiro-e-sao-paulo/ | 2026-01-17 | encerrado_arquivar | nao |
| 2025-12-17 | Edital Fortalecendo Redes | Instituto TIM | https://editalinstitutotim.prosas.com.br/ | 2026-01-23 | encerrado_arquivar | depende |
| 2025-12-17 | Edital 2026 Instituto BRZ – Dona Neném | Instituto BRZ – Dona Neném | https://www.institutodonanenembrz.com/edital-2026 | 2026-01-05 | encerrado_arquivar | nao |
| 2025-12-09 | Edital de direitos humanos 2026 | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br | 2026-03-06 | encerrado_arquivar | sim |
| 2025-12-03 | Projeto Nanet – cuidados digitais e combate à desinformação | Abong / Ibase / Ação Educativa | (aguardar_fonte) | 2025-12-20 | encerrado_arquivar | depende |
| 2025-12-02 | Edital EBANX de projetos incentivados | EBANX | https://www.ebanx.com/pt-br/edital/ | 2025-12-07 | encerrado_arquivar | nao |
| 2025-11-24 | Edital Ambev Brasilidades 2026 | Ambev | https://prosas.com.br/editais/16452-edital-ambev-brasilidades-2026 | — | sem_data | depende |
| 2025-11-19 | Edital Corredor 2025 – Fundo Hydro | Fundo Hydro | http://www.editalcorredor2025.com.br | 2026-01-06 | encerrado_arquivar | nao |
| 2025-11-13 | Chamada Teia da Sociobiodiversidade 2025 | Fundo Casa Socioambiental / Fundo Socioambiental CAIXA | https://casa.org.br/chamadas/teia-da-sociobiodiversidade-2025 | 2025-12-16 | encerrado_arquivar | depende |
| 2025-11-12 | Re-Farm Cria – 4ª edição | FARM Rio / Instituto Regatão Amazônia | (aguardar_fonte) | 2025-11-21 | encerrado_arquivar | depende |
| 2025-11-11 | Edital de fortalecimento de redes de economia solidária | Ministério do Trabalho e Emprego / SENAES | https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/economia-solidaria/editais-e-chamamentos-publicos | 2025-12-05 | encerrado_arquivar | sim |
| 2025-11-05 | Edital socioambiental Raízen São Paulo | Raízen | https://www.raizen.com.br/sustentabilidade/social/performance-social | 2025-11-14 | encerrado_arquivar | nao |
| 2025-11-04 | Prêmio Educação para Gentileza e Generosidade 2025 | Plataforma EGG | https://www.gentilezagenerosidade.org.br | 2025-12-05 | encerrado_arquivar | nao |
| 2025-10-31 | IA ponto 3 – capacitação de OSCs em inteligência artificial | IDIS / Google.org | https://www.idis.org.br/ia-ponto3 | 2025-11-23 | encerrado_arquivar | sim |
| 2025-10-27 | Edital Carnaval da Liberdade 2026 | Cemig | https://prosas.com.br/editais/16455 | 2025-12-07 | encerrado_arquivar | nao |
| 2025-10-23 | Edital de patrocínio Banco da Amazônia | Banco da Amazônia | https://www.bancoamazonia.com.br/o-banco/patrocinio | 2025-11-28 | encerrado_arquivar | nao |
| 2025-10-20 | Prêmio Fundação Banco do Brasil de Tecnologia Social – 13ª edição | Fundação Banco do Brasil | https://transforma.fbb.org.br/premio/19 | 2025-12-01 | encerrado_arquivar | sim |
| 2025-10-18 | 2º Edital Social Transforma | Nexa Resources | https://editalsocialnexa2025.prosas.com.br | 2025-11-07 | encerrado_arquivar | nao |
| 2025-10-15 | Edital de criação e consolidação de RPPNs no litoral do PR | FUNBIO / Programa Biodiversidade Litoral do Paraná | https://chamadas.funbio.org.br | 2025-12-10 | encerrado_arquivar | nao |
| 2025-10-14 | Credenciamento de captadores de recursos via Lei Rouanet – Jundiaí | Prefeitura de Jundiaí / Fundação Casa da Cultura e Esportes | (aguardar_fonte) | — | sem_data | nao |
| 2025-10-08 | Edital Eneva FIA 2025 | Eneva | https://editalenevafia2025.prosas.com.br | 2025-10-31 | encerrado_arquivar | nao |
| 2025-10-08 | 45º Edital Cerrado e Caatinga | Fundo Ecos / GEF / PNUD / ISPN | https://fundoecos.org.br/editais/45o-edital-cerrado-e-caatinga/ | 2025-11-10 | encerrado_arquivar | depende |
| 2025-09-30 | Seleção pública Petrobras – soluções baseadas na natureza em áreas urbanas | Petrobras | https://investidor.bussolasocial.com.br/petrobras/editais/editalpetrobras-sbn2025 | 2025-10-27 | encerrado_arquivar | nao |
| 2025-09-25 | Bikeatona 2025 | Instituto Aromeiazero | https://aromeiazero.org.br/bikeatona | 2025-10-27 | encerrado_arquivar | depende |
| 2025-09-24 | Edital Instituto Vakinha Porto Alegre | Instituto Vakinha | https://vakinha.org.br | 2025-10-20 | encerrado_arquivar | nao |
| 2025-09-23 | Investimento sociocultural Mercado Livre (incentivados) | Mercado Livre | https://sustentabilidademercadolivre.com/iniciativas/investimento-sociocultural | 2025-09-29 | encerrado_arquivar | nao |
| 2025-09-17 | Programa de Apoio a Projetos de Equidade Racial no Câncer | Instituto Oncoguia | https://oncoguia.org.br/conteudo/programa-de-apoio-a-projetos-de-equidade-racial-no-cancer/17871/1424/ | 2025-10-17 | encerrado_arquivar | depende |
| 2025-09-15 | Edital de projetos inovadores no controle do tabaco | ACT Promoção da Saúde | (aguardar_fonte) | 2025-10-24 | encerrado_arquivar | depende |
| 2025-09-05 | Selo Organização Parceira ChildFund 2025 | ChildFund Brasil | https://childfundbrasil.org.br/dashboard/wp-content/uploads/2025/08/Edital-Selo-Organizacao-Parceira-do-ChildFund_2025.pdf | 2025-09-15 | encerrado_arquivar | depende |
| 2025-09-02 | Edital BV cultural para mulheres negras | Banco BV | https://bipcultura.prosas.com.br | 2025-09-19 | encerrado_arquivar | depende |
| 2025-09-02 | Seleção de atividades na Casa das ONGs (COP30) | Abong | (aguardar_fonte) | 2025-09-25 | encerrado_arquivar | depende |
| 2025-08-27 | Rede D'Or – projetos incentivados 2025 | Rede D'Or / Instituto Phi | (aguardar_fonte) | 2025-09-30 | encerrado_arquivar | depende |
| 2025-08-26 | Programa Rouanet Nordeste | Ministério da Cultura | https://salic.cultura.gov.br | 2025-09-05 | encerrado_arquivar | nao |
| 2025-08-20 | Edital Segurança Integral de Defensoras/es de Direitos Humanos | Fundo Brasil / Fundação Ford / Porticus | https://www.fundobrasil.org.br/edital/seguranca-integral-de-defensoras-es-de-direitos-humanos-apoiando-a-linha-de-frente-em-defesa-da-democracia/ | 2025-09-01 | encerrado_arquivar | depende |
| 2025-08-19 | iFood Chega Junto – 2ª edição | iFood | https://entregador.ifood.com.br/programa-de-incentivo-ifood-chega-junto/ | 2025-09-08 | encerrado_arquivar | depende |
| 2025-08-13 | Seleção Pública de Patrocínios 2025 | Embratur | https://patrocinio.embratur.com.br/ | 2025-12-31 | encerrado_arquivar | depende |
| 2025-08-13 | 5º Edital de Educação ENGIE | ENGIE Brasil e parceiras | https://www.engie.com.br/editaleducacao | 2025-08-29 | encerrado_arquivar | depende |
| 2025-06-17 | Edital RD Saúde / MOL Impacto | RD Saúde / MOL Impacto | (aguardar_fonte) | 2025-07-04 | encerrado_arquivar | depende |
| 2025-06-11 | Edital de educação integral | Itaú Social / Fundação Lemann / Porticus | https://www.itausocial.org.br/editais | 2025-07-04 | encerrado_arquivar | depende |
| 2025-06-10 | 5º Prêmio de Comunicação Fundação José Luiz Setúbal | Fundação José Luiz Setúbal | https://fundacaojles.org.br/premio-de-comunicacao-jose-luiz-setubal/ | 2025-07-11 | encerrado_arquivar | depende |
| 2025-06-09 | 2º Prêmio David Miranda Causas de Vida | Instituto David Miranda | https://institutodavidmiranda.org | 2025-06-23 | encerrado_arquivar | nao |
| 2025-06-09 | Edital de Chamamento Público nº 1/2025 – adaptação climática em periferias urbanas | Ministério das Cidades / Ministério do Meio Ambiente | https://www.gov.br/cidades/pt-br/acesso-a-informacao/participacao-social/editais-de-chamamento-publico/edital-de-chamamento-publico-no-1-2025/ | 2025-07-17 | encerrado_arquivar | sim |
| 2025-06-04 | Seleção Caixa Cultural 2025 | Caixa Econômica Federal | https://selecaocaixacultural.com.br | 2025-06-13 | encerrado_arquivar | nao |
| 2025-06-03 | Edital FIA 2025 | Itaú Social | https://www.itausocial.org.br/editais | 2025-07-11 | encerrado_arquivar | nao |
| 2025-05-27 | Edital Social Porto 2025 | Grupo Porto | https://investidor.bussolasocial.com.br/portoseguro/editais/porto2025crianças_adolescentes_pessoaidosa | 2025-07-30 | encerrado_arquivar | nao |
| 2025-05-23 | Chamada Elas 40+ | Instituto Lojas Renner / Cruzando Histórias | https://cruzandohistorias.org | 2025-05-26 | encerrado_arquivar | nao |
| 2025-05-19 | Edital Itaú Viver Mais 2025 (7ª edição) | Itaú Viver Mais / Fundo de Direitos da Pessoa Idosa | https://www.itauvivermais.com.br/pilares/editais/edital-ivm-2025/ | 2025-06-12 | encerrado_arquivar | depende |
| 2025-01-10 | Edital Programa Itaipu Mais que Energia | Itaipu Binacional / Caixa | https://prosas.com.br/editais/15243-edital-programa-itaipu-mais-que-energia | 2025-01-21 | encerrado_arquivar | nao |
| 2025-01-09 | Chamamento público – enfrentamento às mudanças climáticas | Prefeitura de Curitiba | https://www.curitiba.pr.gov.br/conteudo/chamamento-publico-2024/3445 | 2025-03-20 | encerrado_arquivar | nao |
| 2025-01-08 | Fundo Instituto General Motors RS | Instituto General Motors | (aguardar_fonte) | 2025-01-22 | encerrado_arquivar | nao |
| 2025-01-07 | Edital de Mobilidade Cultural | Secretaria de Estado da Cultura do Paraná | https://www.cultura.pr.gov.br/Pagina/Edital-de-Mobilidade-Cultural | — | sem_data | nao |
| 2025-01-06 | Prêmio Isabel Salgado | Confederação Brasileira de Voleibol / Banco do Brasil | https://prosas.com.br/editais/14950-premio-isabel-salgado | 2025-01-15 | encerrado_arquivar | depende |
| 2024-12-30 | Edital Labora – trabalhadores informais | Labora / Fundo Brasil de Direitos Humanos | https://fundobrasil-institucional-prd.s3.sa-east-1.amazonaws.com/app/uploads/2024/12/Edital-Labora-PDF.pdf | 2025-02-07 | encerrado_arquivar | depende |
| 2024-12-17 | Glocal Aceleradora – 12º edital | Glocal Aceleradora | https://aceleradora.glocal.org.br/inscricao/ | 2025-02-05 | encerrado_arquivar | nao |
| 2024-12-16 | Edital Democracia e Direitos | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/democracia-e-direitos-construindo-o-futuro-com-justica-e-igualdade/ | 2025-03-10 | encerrado_arquivar | sim |
| 2024-12-16 | Edital Raízes – justiça climática | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/raizes-comunidades-tradicionais-quilombolas-e-povos-indigenas-lutando-por-justica-climatica/ | 2025-02-11 | encerrado_arquivar | depende |
| 2024-12-11 | 1º Edital Jornada Equatorial | Instituto Equatorial | https://institutoequatorial.prosas.com.br | 2024-12-20 | encerrado_arquivar | sim |
| 2024-07-29 | Programa BTG Soma Empreendedorismo | BTG Pactual / AGO Social | https://conteudo.agosocial.com.br/btg-soma-empreendedorismo | 2024-08-10 | encerrado_arquivar | depende |
| 2024-07-22 | Glocal Aceleradora – 11º edital | Glocal Aceleradora | https://aceleradora.glocal.org.br/ | 2024-07-24 | encerrado_arquivar | nao |
| 2024-07-22 | Chamada Reconstruir RS | Fundo Casa Socioambiental | https://casa.org.br/chamadas/reconstruir-rs-apoio-a-resiliencia-climatica-e-reconstrucao-comunitaria/ | 2024-08-13 | encerrado_arquivar | nao |
| 2024-07-19 | InovaSUAS – Sudene | Sudene | https://www.gov.br/sudene/pt-br/assuntos/inovasuas | 2024-09-02 | encerrado_arquivar | nao |
| 2024-07-19 | Consultoria ESPM Social 2024 | ESPM Social | (aguardar_fonte) | — | sem_data | nao |
| 2024-07-19 | Edital Doritos / Fundação PepsiCo | Fundação PepsiCo / Doritos | https://prosas.com.br/editais/14582 | 2024-08-12 | encerrado_arquivar | depende |
| 2024-07-18 | Nanet – combate a discurso de ódio e desinformação | Abong / Ação Educativa / Ibase | https://abong.org.br/nanet-democratizando-a-tecnologia/ | 2024-07-24 | encerrado_arquivar | depende |
| 2024-07-17 | Chamada socioambiental Instituto General Motors | Instituto General Motors | (aguardar_fonte) | 2024-07-26 | encerrado_arquivar | depende |
| 2024-07-16 | Chamada LBTQI+ América Latina | Fundação Astraea | https://astraeafoundation.org/ | 2024-08-15 | encerrado_arquivar | depende |
| 2024-07-16 | Edital nº 01/2024 – Plano de Desenvolvimento Sustentável dos Povos e Comunidades Tradicionais | Ministério do Meio Ambiente | https://www.gov.br/mma/pt-br/acesso-a-informacao/acoes-e-programas/apoio-a-projetos/outros%20editais/editaldechamamentopblicon01-2024sei_1680301_edital_01_2024.pdf | 2024-07-24 | encerrado_arquivar | depende |
| 2024-02-06 | Chamada pública Mãe Gilda de Ogum | Ministério da Igualdade Racial / Fiocruz | https://prosas.com.br/editais/14413-chamada-publica-mae-gilda-de-ogum | 2024-03-21 | encerrado_arquivar | depende |
| 2024-01-23 | Global Innovation Challenge (pessoas em situação de rua) | Citi Foundation | https://citi.fluxx.io/apply/Challenge | 2024-02-13 | encerrado_arquivar | depende |
| 2024-01-15 | Edital Instituto Localiza 2024 | Instituto Localiza | http://editalinstitutolocaliza.prosas.com.br/ | 2024-01-31 | encerrado_arquivar | sim |
| 2024-01-11 | Chamamento público – Praças da Cidadania de Mauá e Diadema | Fundo Social de São Paulo | (aguardar_fonte) | 2024-02-09 | encerrado_arquivar | nao |
| 2024-01-10 | Edital ACT de financiamento de projetos em controle do tabaco | ACT Promoção da Saúde | https://actbr.org.br/uploads/arquivos/Edital-Act-de-Financiamento-de-Projetos.pdf | 2024-02-18 | encerrado_arquivar | depende |
| 2024-01-02 | Floresta Viva – Corredores de Biodiversidade | Floresta Viva (BNDES) / FUNBIO | https://chamadas.funbio.org.br/floresta-viva-corredores-de-biodiversidade | 2024-03-18 | encerrado_arquivar | depende |
| 2023-12-19 | Programa Nutrir+ | Citrosuco / AGO Social | https://conteudo.agosocial.com.br/programa-nutrir-citrosuco | 2024-01-31 | encerrado_arquivar | nao |
| 2023-12-18 | Fortalecendo Trabalhadores Informais na Luta por Direitos 2024 | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/fortalecendo-trabalhadores-informais-na-luta-por-direitos-2024/ | 2024-02-07 | encerrado_arquivar | depende |
| 2023-12-16 | Prêmio Cidadania na Periferia | MDHC / Secom-PR | (aguardar_fonte) | 2024-03-01 | encerrado_arquivar | sim |
| 2023-12-13 | Edital socioeconômico para mulheres negras | Fundação Banco do Brasil | https://editalmulheresnegras.fbb.org.br/ | 2024-02-19 | encerrado_arquivar | depende |
| 2023-12-12 | Edital Geral 2024 – Vozes por Direitos e Justiça | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/edital-geral-2024-vozes-por-direitos-e-justica-fortalecendo-a-autonomia-e-acao-da-sociedade-civil/ | 2024-02-29 | encerrado_arquivar | sim |
| 2023-12-05 | Seleção Pública Petrobras Socioambiental 2023 – 2ª fase | Petrobras | https://investidor.bussolasocial.com.br/petrobras/editais/naoincentivados2023.2 | 2024-02-29 | encerrado_arquivar | nao |
| 2023-11-28 | Edital Comunidades Tradicionais Lutando por Justiça Climática | Fundo Brasil de Direitos Humanos | https://www.fundobrasil.org.br/edital/edital-comunidades-tradicionais-lutando-por-justica-climatica/ | 2024-01-31 | encerrado_arquivar | depende |
| 2023-11-21 | Edital socioambiental GRU Airport | GRU Airport | https://www.gru.com.br/pt/projetosocioambiental | 2023-12-08 | encerrado_arquivar | nao |
| 2023-11-14 | Edital 01/2023 – Índice de Transparência e Governança Pública | Transparência Internacional Brasil | https://comunidade.transparenciainternacional.org.br/edital-01-2023 | 2023-11-30 | encerrado_arquivar | sim |
| 2023-11-14 | Edital 01/2023 Viva Periferia – pessoa idosa | Secretaria Nacional dos Direitos da Pessoa Idosa (MDHC) | https://www.gov.br/mdh/pt-br/navegue-por-temas/pessoa-idosa/Edital012023VivaPeriferia.pdf | 2023-11-24 | encerrado_arquivar | sim |
| 2023-11-14 | Criança Esperança 2023/2024 (prorrogação) | Criança Esperança / UNESCO | https://projetos.criancaesperanca.unesco.org | 2023-11-30 | encerrado_arquivar | sim |
| 2023-11-08 | Edital nº 1/2023 – formação de mulheres em autonomia econômica e cuidado | Ministério das Mulheres | https://www.gov.br/mulheres/pt-br/acesso-a-informacao/editais-1/edital-ndeg-1-2023-selecao-de-organizacoes-da-sociedade-civil-para-execucao-de-projetos-de-formacao-com-mulheres-em-autonomia-economica-e-cuidado/ | 2023-11-24 | encerrado_arquivar | sim |
| 2023-11-08 | Edital nº 2/2023 – educação para prevenção às violências contra mulheres | Ministério das Mulheres | https://www.gov.br/mulheres/pt-br/acesso-a-informacao/editais-1/edital-ndeg-2-2023-selecao-de-organizacoes-da-sociedade-civil-para-execucao-de-acoes-de-educacao-para-prevencao-as-violencias-contra-mulheres | 2023-11-29 | encerrado_arquivar | sim |
| 2023-11-01 | Edital Unipar 2023 (incentivados e não incentivados) | Unipar / Instituto Unipar | https://prosas.com.br/editais/14234-edital-unipar-e-instituto-unipar-projetos-incentivados-e-nao-incentivados-2023 | 2023-11-12 | encerrado_arquivar | nao |
| 2023-10-27 | Selo Organização Parceira ChildFund (Legacy Fund) 2023 | ChildFund Brasil | http://www.childfundbrasil.org.br/wp-content/uploads/2023/10/Edital-Selo-Organiza%C3%A7%C3%A3o-Parceira_Legacy-Fund_final_-1.pdf | 2023-12-05 | encerrado_arquivar | sim |

## 3. Onde publica

- **A ABCR é agregador editorial**: publica notícias curtas (categoria "Editais", id 162, ~402 posts desde o início; ~6–10 por mês em 2025–2026) reescrevendo o edital e quase sempre colocando **o link oficial no fim do texto**. Não há campos estruturados; tudo está no corpo (`content:encoded`).
- **Onde os financiadores publicam e recebem inscrições** (contagem sobre as 159 oportunidades):
  - **Site próprio do financiador** (página de edital/notícia): Fundo Brasil, Instituto Lojas Renner, Fundação Salvador Arena, FBB, Zurich, BNDES, Cargill, Pacová, Instituto Cactus, Mattos Filho, ENGIE etc. — é a maioria.
  - **Prosas** (`prosas.com.br/editais/N` ou subdomínio `<edital>.prosas.com.br`): Cemig (3), Instituto TIM, Eneva, Nexa, Localiza, Tecendo Infâncias, PepsiCo, Itaipu, Ambev, MIR/Fiocruz, Unipar, Equatorial, Banco BV, Folha. ~18 casos. **O robots.txt do Prosas bloqueia leitura automatizada.**
  - **Bússola Social** (`investidor.bussolasocial.com.br/<empresa>/editais/…`): Porto, Petrobras, Capemisa. Página SPA, sem conteúdo legível sem JavaScript.
  - **FUNBIO Chamadas** (`chamadas.funbio.org.br/<chamada>`): Programa Biodiversidade Litoral do PR, Floresta Viva.
  - **gov.br / Transferegov**: MDHC/CONANDA, Ministério das Mulheres, Ministério das Cidades, MTE/SENAES, MMA, Sudene, MinC (Salic). Os editais federais exigem proposta no **Transferegov.br**.
  - **Operadores/aceleradoras**: AGO Social (Ambev VOA, BTG Soma, Nutrir+), Phomenta/Phi (BNDES Periferias Fortes, AXIA), Ekloos, Simbi (`selecao.simbi.social`), Monitor Social (Auren), Hub do Incentivo (MAPFRE), Sponsor (Alcoa).
  - **Formulário solto** (Google Forms, Forms Office, Qualtrics, SurveyMonkey) e **e-mail**: ~20 casos — sem página oficial estável (aguardar_fonte).
  - **Mapas Culturais** apareceu 1 vez (FMC Bombinhas, `mapacultural.cim-amfri.sc.gov.br`).

## 4. Tipos de oportunidade

- **Edital de projeto (117/159)** — doação direta (não reembolsável) a OSC, de R$ 1,5 mil (Pacová) a R$ 1 milhão por projeto (CONANDA, FME, BNB) e chamadas-guarda-chuva de R$ 20 milhões+ (BNDES Periferias, Fundo Casa Teia).
- **Seleção de projetos incentivados (subtipo importante, ~20)** — empresas escolhem projetos **já aprovados** em Rouanet, Lei do Esporte, FIA, Fundo do Idoso, PRONON/PRONAS: Zurich, MAPFRE, Porto, BNB, Mercado Livre, Rede D'Or, EBANX, Cemig, Petrobras, Ambev Brasilidades, Eneva. Para a A.M.C. Jardim América só servem se houver projeto aprovado e captação autorizada.
- **Capacitação/aceleração/consultoria ("outro", 21)** — Zurich Impulsiona, IDIS IA, Ambev VOA, Glocal, ESPM Social, Fundação Salvador Arena, SAP/ASID, Jornada Equatorial. Algumas trazem capital-semente.
- **Prêmio (13)** — FBB Tecnologia Social (até R$ 6 milhões), FGV Responsabilidade Social, Empreendedor Social, Impactos Positivos, Cidadania na Periferia (R$ 50 mil × 120).
- **Cadastro/credenciamento (4)** — Sebrae-SP, Impactarte (contínuo), Jundiaí e Bombinhas (captadores/empresas).
- **Internacional (4)** — Zayed, Citi Foundation, Astraea, OIM (USD).
- Não apareceu fundo rotativo nem bolsa individual relevante.

**Áreas mais frequentes:** direitos humanos e democracia (Fundo Brasil — o financiador mais recorrente, 10 editais), periferias, criança e adolescente/FIA, pessoa idosa, mulheres e gênero, meio ambiente/clima (Funbio, Fundo Casa, Fundo Ecos), educação, segurança alimentar, saúde (saúde mental, HIV, câncer, tabaco), cultura e esporte incentivados, fortalecimento institucional.

**Quem pode:** quase sempre OSC com CNPJ (muitas pedem 1–2 anos de existência); várias aceitam coletivos informais (Bem Maior, Periferias Fortes, Fundo SAAP); algumas são restritas a municípios de atuação da empresa (Alcoa, Nexa, Eneva, Renner, Auren, Itaipu); poucas aceitam pessoa física (iFood, FME — pessoa com doutorado). Abrangência: ~40% nacional; o resto concentrado em SP, RJ, PR, RS, MG e Nordeste. **Goiás aparece explicitamente só 3 vezes** (Edital da Água/MOSAIC 2026, Jornada Equatorial 2024, Transparência Internacional Centro-Oeste 2023) e indiretamente em editais do Cerrado (Fundo Ecos, Floresta Viva).

## 5. Calendário

Contagem por mês de publicação na amostra lida (159 itens; meses com páginas não lidas estão sub-representados):

| jan | fev | mar | abr | mai | jun | jul | ago | set | out | nov | dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 8 | 9 | 5 | 13 | 13 | 20 | 14 | 14 | 10 | 15 | 18 |

Padrões observados (repetem de um ano para o outro):
- **Dezembro–janeiro:** Fundo Brasil (editais gerais, clima, trabalhadores — prazos fev/mar), Glocal, Capemisa, Instituto TIM, Localiza, FBB mulheres negras.
- **Março–maio:** Instituto Lojas Renner (inclusão de mulheres), Porto/Instituto Porto, Itaú Viver Mais (mai–jun, todo ano), iFood Chega Junto, Fundação Cargill, Edital da Água (MOSAIC/IDIS, inclui GO).
- **Junho–agosto:** Itaú Social FIA, Edital Social Porto (incentivados), Fundação Salvador Arena (PAPS), Movimento Bem Maior (agosto, todo ano), Rio Doce, Periferias Fortes (BNDES).
- **Setembro–novembro ("temporada dos incentivados" antes do fechamento do IR):** Zurich, MAPFRE, Mercado Livre, Rede D'Or, Petrobras, BNB, Eneva FIA, Cemig, Banco da Amazônia, FBB Prêmio Tecnologia Social, Fundo Casa, Fundo Ecos, MTE.
- Janela típica entre publicação e prazo: **2 a 5 semanas** (muitas com 7–15 dias). Um motor com cadência semanal perde parte delas.

## 6. Conselho de 7 lentes sobre o MOTOR

**1. Extremamente pessimista — Dra. Helena Vasconcelos, professora de computação (pós-doc em Python, análise de dados textuais), implacável com dados sujos.**
"O motor é perigoso como está. Cem por cento dos prazos preenchidos estão com o ano errado — todos jogados para 2027. Isso não é ruído, é viés sistemático: transforma editais mortos em 'abertos' e faz o painel dizer 'satisfatório' com 18 achados quando, hoje, só existem 6 abertos e apenas 3 que talvez sirvam para uma OSC de Goiânia. Dois links oficiais apontam para sites sem relação, um deles para um domínio que nem resolve. Se a associação seguir esse painel, vai preparar proposta para edital encerrado."

**2. Pessimista — Rafael Moura, chief engineer, metódico e desconfiado de heurísticas.**
"O extrator de link oficial pega o primeiro `href` externo, e o post da ABCR tem links de patrocinadores e de outras matérias no corpo — daí o IDIS no lugar do ContraFluxo. A UF sai da primeira sigla que aparece. O valor sai do primeiro 'R$' do texto, que às vezes é o total do programa. `financiador` vem nulo sempre. E o motor só lê 10 itens: se cair por 3 semanas, perde editais sem perceber, porque não pagina."

**3. Levemente pessimista — Profa. Lúcia Tanaka, pós-doc em Python e recuperação de informação, cuidadosa com cobertura.**
"Um quinto dos editais leva a Google Forms, bit.ly ou Drive; outros vão para Prosas, que proíbe robôs, e Bússola Social, que é SPA. Então mesmo com o link certo, a confirmação no site oficial vai falhar em ~30% dos casos. E a ABCR é forte em SP/RJ/PR/RS e em incentivados — para Goiânia o rendimento líquido é baixo: 34 'sim' em 159, quase todos nacionais."

**4. Neutro — Eng. Marcelo Andrade, staff engineer, pragmático, fecha a sessão.** (síntese abaixo)

**5. Levemente otimista — Carla Figueiredo, CTO de big tech, orientada a custo-benefício.**
"A fonte é limpa e barata: WordPress padrão, robots liberal, feed com conteúdo completo, paginação por `?paged=N` e API REST com filtro `after`. Uma chamada por dia resolve a cadência; 31 chamadas reconstroem três anos. Poucas fontes do Eldorado têm essa relação custo/qualidade."

**6. Otimista — Prof. Dr. André Siqueira, pós-doc em Python e PLN, entusiasta de extração estruturada.**
"O texto da ABCR é muito regular: 'inscrições até DD de mês', 'até R$ X', 'acesse o edital' no último parágrafo. Com regras simples — prazo ancorado na data do post, link oficial = último link externo após 'edital/inscrições/acesse', UF só quando o texto diz 'organizações de <estado>' — a precisão sobe muito. E o motor vira um **mapa de quem financia**: ~115 financiadores com site oficial, cada um vira um alvo de monitoramento direto."

**7. Extremamente otimista — Beatriz Lemos, chief engineer de produto, visionária.**
"O ganho ideal não é a notícia, é o calendário. Com três anos de histórico arquivado, o Eldorado sabe que Bem Maior abre em agosto, Itaú Viver Mais em maio, Fundo Brasil em dezembro, a temporada dos incentivados em setembro. A associação pode preparar a proposta **antes** do edital sair. A ABCR vira o radar de descoberta, e os sites oficiais viram os alvos de vigilância."

### Síntese do neutro (Marcelo Andrade)

**Decisão:** **manter o motor, mas rebaixar o painel de "satisfatório" para "com defeito" até corrigir o ano do prazo e o link oficial.** A rota está certa; o problema é o parser. Todos os 14 indícios atuais devem ser reprocessados (prazo e UF) antes de qualquer alerta.

**Melhorias concretas** — ver seção 7 (numeradas por rota, léxico, filtro, cadência, histórico, deduplicação e link oficial).

**Parâmetros de qualidade (metas):**
- Prazo com ano correto: ≥ 98% (teste: nenhum prazo > publicação + 400 dias; nenhum prazo anterior à publicação).
- Link oficial válido (abre e é do domínio do financiador/plataforma indicada): ≥ 85%; 0% de links para domínios que não resolvem.
- `financiador` preenchido: ≥ 95%.
- UF correta (nacional = ""): ≥ 90% numa amostra mensal de 10.
- Estado "aberto" falso-positivo: 0 (todo aberto precisa de prazo ≥ hoje e fonte com ano).
- Cobertura: 100% dos posts da categoria 162 desde a última leitura (comparar contagem da API REST).
- Ruído (licitação, credenciamento de empresa, curso pago): ≤ 5% dos livros.

**Riscos e mitigação:**
1. *Ano do prazo inferido errado* → ancorar na data de publicação; se o texto tiver ano, usar o ano do texto; validar janela [publicação, publicação+400 d]; fora disso, `sem_data` + revisão.
2. *Link oficial errado (pega link de patrocinador/rodapé)* → buscar só no corpo do post, priorizar âncoras próximas de "edital", "inscrições", "acesse", "regulamento"; lista negra de domínios da própria ABCR, redes sociais e encurtadores; checar se o domínio contém o nome do financiador.
3. *Link oficial em plataforma não legível (Prosas bloqueado, Bússola SPA, Google Forms)* → aceitar como "página de inscrição" sem raspar; marcar `aguardar_fonte` quando for formulário solto e buscar o site institucional do financiador.
4. *Perda de itens por queda do motor* → paginar o feed até encontrar o último `guid` já visto (ou usar `after=` na API REST).
5. *Mudança de layout/WordPress* → teste de fumaça diário: o feed deve ter ≥ 1 item com `pubDate` nos últimos 21 dias; senão, alarme.
6. *Bloqueio do proxy/curl (403 hoje)* → o leitor do sistema precisa de rota liberada ou leitura via serviço que respeite robots; registrar erro em vez de "0 achados".
7. *Ruído (licitação de prefeitura, credenciamento de empresas, cursos)* → filtro léxico negativo (ver melhoria 4).
8. *Baixa aderência a Goiás* → não descartar nacionais; aplicar o filtro de aplicabilidade e promover os financiadores recorrentes a motores próprios.

## 7. Melhorias do motor (lista numerada)

1. **Rota (cadência diária):** manter `https://captadores.org.br/category/editais/feed/`; ler `content:encoded` (não só `description`).
2. **Rota (histórico e recuperação):** adicionar varredura `https://captadores.org.br/category/editais/feed/?paged=N` até o `guid` já conhecido (ou até 02/10/2023 na carga inicial, N≈31), ou a API `https://captadores.org.br/wp-json/wp/v2/posts?categories=162&after=<última data>&per_page=100&page=N`.
3. **Prazo (correção crítica):** inferir o ano a partir da data de publicação do post, nunca da data de leitura; aceitar formatos "até DD de mês", "DD/MM", "DD de mês de AAAA", "prorrogado até…"; quando houver duas datas (pré-inscrição e inscrição completa, chamadas 1 e 2), guardar a última e anotar as duas.
4. **Léxico/filtro:** positivo — "edital", "chamada", "chamamento", "prêmio", "seleção", "inscrições abertas", "fundo"; negativo (rebaixar para `outro` ou descartar) — "diálogo competitivo", "licitação", "credenciamento de empresas/consultores/captadores", "curso pago". Marcar `incentivado=true` quando aparecer "Rouanet", "Lei de Incentivo", "FIA", "Fundo do Idoso", "PRONON", "PRONAS" — exige projeto aprovado.
5. **Link oficial:** escolher a âncora do corpo mais próxima de "edital/inscrições/acesse/regulamento/saiba mais"; ignorar domínios captadores.org.br, redes sociais, encurtadores (bit.ly, short.gy), Google Drive; se só houver Forms/e-mail → `aguardar_fonte`. Verificar se o domínio responde (HEAD) antes de gravar.
6. **Financiador:** extrair do título/lead ("<Instituição> abre/lança edital…") — o padrão da ABCR é estável; preencher `orgao` sempre.
7. **UF/abrangência:** "todo o país", "nacional", "em todo o Brasil" → uf ""; listar estados só quando o texto restringir ("organizações do Ceará", "nos estados de…"); nunca usar a primeira sigla do texto.
8. **Valor:** separar "valor por projeto" de "valor total do programa"; quando não houver repasse (produção de vídeo, formação), gravar o benefício em texto e não um número.
9. **Cadência:** diária (o site publica 6–10 editais/mês e as janelas são de 1 a 5 semanas); alerta imediato para prazos ≤ 10 dias.
10. **Deduplicação:** chave = financiador normalizado + ano + link oficial; unir posts de "prorrogação" e "últimos dias" ao edital original (ex.: IDIS IA 31/10 e 18/11/2025; Santa Luzia 10/06 e 03/08/2026; Bem Maior 31/07 e 06/08/2026), atualizando o prazo.
11. **Histórico/previsão:** arquivar os encerrados como `encerrado_arquivar` e gerar o calendário por financiador (Bem Maior → agosto; Itaú Viver Mais → maio; Fundo Brasil → dezembro; incentivados → setembro).
12. **Promoção de financiadores recorrentes a motores próprios:** Fundo Brasil de Direitos Humanos, Instituto Lojas Renner, Fundação Salvador Arena, Fundação Banco do Brasil, BNDES (Periferias), Cemig, Movimento Bem Maior, Funbio Chamadas, Fundo Casa, Itaú Social/Viver Mais.
13. **Reprocessar os 14 indícios atuais** com as regras 3, 5 e 7 e rebaixar o status do painel até a correção.

## 8. O que não foi confirmado e por quê

- **~150 posts do período não foram lidos** (páginas 12–13, 15–18, 20–23 e 25–29 do feed), pelo limite de ~40 chamadas WebFetch. Faixas não cobertas: out/2024–mai/2025 parcial, jul–dez/2024 parcial, fev–jun/2024. O método está pronto para completar (feed `?paged=N`).
- **Prazos com ano deduzido:** quando a fonte dá só dia e mês, o ano foi deduzido pela data do post; as datas e valores vêm do texto do agregador e só foram conferidos no site oficial nos casos marcados `"fonte": "verificado"` (8 livros).
- **Embratur patrocínio 2026:** o post (06/01/2026) cita "3 de outubro" sem ano; `patrocinio.embratur.com.br` abriu sem conteúdo legível. Ficou `sem_data` — se for 03/10/2026, está aberto por mais um dia.
- **Desafio Dados e IA (Vital Strategies):** página no Prosas bloqueada por robots.txt — não aberta.
- **Edital Social Porto / Bússola Social:** página SPA sem conteúdo legível; estados não confirmados.
- **Juventude Solidária:** página gov.br exige login — não aberta (regra: sem login).
- **BNB ConveniosWeb:** é tela de login — não aberta; usado o link institucional citado no post.
- **Santa Luzia do Paruá:** prazo "30 dias úteis após publicação no PNCP" — data não confirmada; é contratação, não fomento.
- **Funbio usopublico-rppn** (segunda chamada do mesmo post de 28/07/2026): não aberta; prazo do agregador ambíguo ("04 e 18 de setembro") — não virou livro separado.
- **Prêmio Cidadania na Periferia (MDHC, 2023):** o link gov.br veio truncado no feed — ficou `aguardar_fonte`.
- **20 oportunidades com `aguardar_fonte`:** o post só traz Google Forms, bit.ly, short.gy, Sway, Drive, Qualtrics, Forms Office ou e-mail; o site institucional do financiador não foi buscado por limite de chamadas.
- Pessoas físicas premiadas/beneficiárias não foram registradas. Nenhuma instrução dirigida ao agente foi encontrada nas páginas.
