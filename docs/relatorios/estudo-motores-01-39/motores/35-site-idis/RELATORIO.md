# Motor 35 — site-idis (IDIS — Instituto para o Desenvolvimento do Investimento Social)

Estudo de 02/10/2026. Tipo: AGREGADOR, mas na prática é um agregador "de parceiros": o IDIS só divulga editais que ele mesmo opera como gestor técnico para empresas e institutos (Zurich, Chamex, Mosaic, Einstein, Google.org), mais casos raros de terceiros (Catalyst 2030). Foram usadas 39 chamadas de WebFetch. O curl direto foi bloqueado pelo proxy (403 no CONNECT).

## 1. Rota (teste e conclusão)

| Teste | URL exata | Resultado |
|---|---|---|
| robots.txt | https://www.idis.org.br/robots.txt | `Disallow:` vazio (tudo liberado). Sitemaps: `/sitemap_index.xml` e `/en/sitemap_index.xml` |
| Rota configurada (feed) | https://www.idis.org.br/feed/ | Responde. Entrega 8 itens com título, link, pubDate e categorias. Não tem campo de prazo, valor nem link oficial (isso fica só no corpo do texto). O `lastBuildDate` era 11/09/2026 e o feed não trazia os posts de 22/09 (Zurich) e 28/09 (Territórios em Rede), que aparecem na API. Conclusão: o feed estava em cache ou desatualizado no momento do teste. Dos 8 itens, nenhum era edital: eram notícias, mídia e 2 vagas de emprego. |
| Página pública | é a mesma URL do feed | O titular vê XML cru, sem uma página humana de editais. |
| Sitemap | https://www.idis.org.br/sitemap_index.xml | Responde com 20 sub-sitemaps. Os de posts são `post-sitemap.xml` e `post-sitemap2.xml`, com lastmod de 02/10/2026. |
| API WordPress (categorias) | https://www.idis.org.br/wp-json/wp/v2/categories?per_page=100 | Responde. Não existe categoria "Editais": os editais caem em "Notícias" (1.004 posts). |
| API WordPress (busca com data) | `https://www.idis.org.br/wp-json/wp/v2/posts?search=edital&after=2023-10-02T00:00:00&per_page=100&_fields=date,link,title` | Responde, com data ISO, filtro de período e busca textual. Foi o caminho usado para montar o histórico. |

**Conclusão:** a rota atual funciona, mas não é a melhor. Ela traz pouco sinal (cerca de 1 edital em cada 10 posts), demora a refletir publicações e não guarda histórico. A rota melhor verificada é a **API REST do WordPress**, `https://www.idis.org.br/wp-json/wp/v2/posts?search=<termo>&after=<data>&per_page=100&_fields=date,link,title,content`, consultada com vários termos ("edital", "inscrições", "chamada", "abre", "seleção"). O `post-sitemap.xml` serve para a varredura completa do histórico. A página que o titular vê deveria ser o post do IDIS ou, melhor, a página oficial do financiador, e não o XML do feed.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

Método: a API REST foi consultada com os termos edital, inscrições, inscricoes, inscri, chamada, prêmio, abre, seleção, Chamex, Zurich, água e Institutos Comunitários, em janelas de data. Depois, cada post candidato foi lido.

| Data | Título | Financiador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| 2026-09-28 | Territórios em Rede (fortalecimento de OSCs) | Hospital Israelita Albert Einstein + IDIS | não confirmado (einstein.br deu 403) | 2026-10-30 | ABERTA | não (só territórios de São Paulo/SP e Salvador/BA) |
| 2026-09-22 | Edital Zurich de Leis de Incentivo 2026 | Zurich Seguros | https://www.zurich.com.br/leis-de-incentivo-2026 | 2026-10-19 | ABERTA | depende (exige projeto já aprovado em Rouanet, Esporte, Fundo do Idoso ou FIA) |
| 2026-03-24 | Edital da Água 2026 (8ª edição) | Mosaic Fertilizantes | https://mosaicco.com.br/ | 2026-04-24 | ENCERRADA | não (em GO só Catalão, Ouvidor e Rio Verde) |
| 2026-03-02 | 6º Edital Educação com Cidadania | Instituto Chamex (Sylvamo) | https://institutochamex.com.br/ | 2026-04-10 | ENCERRADA | sim (nacional) |
| 2025-10-22 | Chamada Pública IA.3 – capacitação em IA | IDIS / Google.org | https://www.idis.org.br/ia-ponto3/ | 2025-11-23 | ENCERRADA | sim (nacional) |
| 2025-06-30 | Edital Zurich de projetos incentivados 2025 | Zurich Seguros | https://www.zurich.com.br (domínio) | 2025-08-03 | ENCERRADA | depende |
| 2025-06-23 | Edital da Água 2025 (7ª edição) | Mosaic Fertilizantes | https://mosaicco.com.br/ | 2025-07-11 | ENCERRADA | não (em GO só Catalão, Ouvidor e Rio Verde) |
| 2025-03-11 | 5º Edital Educação com Cidadania | Instituto Chamex (Sylvamo) | https://institutochamex.com.br/ | 2025-04-11 | ENCERRADA | sim |
| 2024-10-31 | 2º Desafio Fundo Catalisador 2030 | Catalyst 2030 Brasil (recursos AMA/Ambev) | https://brazil.catalyst2030.net/ | 2024-11-10 | ENCERRADA | depende (exige coalizão de 2 ou mais atores) |
| 2024-04-27 | 6º Edital da Água | Instituto Mosaic | https://mosaicco.com.br/ | 2024-05-17 | ENCERRADA | depende (GO elegível, municípios não confirmados) |

Totais: 10 oportunidades, sendo 2 abertas, 8 encerradas e 0 sem data.

Posts descartados por não serem oportunidade para OSC: vagas de emprego (pessoa física); inscrições no Fórum Brasileiro de Filantropos (evento); anúncios de contemplados Chamex (17/06/2025 e 03/06/2026); "Fundos emergenciais preventivos" do Transformando Territórios (29/07/2026), em que R$ 50 mil por fundo foram para fundações comunitárias já selecionadas, sem chamada aberta.

**Verificação por amostra dos links oficiais (10 links):**

| # | Link | Abre? | É do financiador? |
|---|---|---|---|
| 1 | http://transformandoterritorios.org.br/ (link_oficial do indício "Territórios em Rede") | sim | **Não.** É o site de outro programa do IDIS/Mott e não cita Territórios em Rede nem Einstein. O link do indício está errado. |
| 2 | https://www.zurich.com.br/leis-de-incentivo-2026 (indício Zurich) | sim | **Sim.** Prazo 21/09 a 19/10/2026 confere. A inscrição migrou para `pt.surveymonkey.com/r/incentivofiscalzurich2026`. |
| 3 | https://institutochamex.com.br/ | sim | sim, mas não exibe o edital |
| 4 | https://institutochamex.com.br/inscricoes-abertas-para-o-5o-edital-educacao-com-cidadania/ | **não (404)** | — |
| 5 | https://mosaicco.com.br/ | sim | sim; tem notícias do Edital da Água 2026 e dos vencedores de 2025 |
| 6 | https://brazil.catalyst2030.net/ | sim | sim; aponta o post do fundo de R$ 240 mil |
| 7 | https://www.idis.org.br/ia-ponto3/ | sim | sim (o IDIS é o executor; Google.org é o financiador) |
| 8 | https://www.einstein.br/ | **não (403)** | não verificado |
| 9 | https://pt.surveymonkey.com/r/... (Zurich 2025, Chamex 6ª) | não testado | é plataforma de inscrição, não site oficial |
| 10 | https://forms.gle/UqL8FhpC16RPZwJ47 (Territórios em Rede) | não testado (formulário) | é plataforma de inscrição, não site oficial |

O arquivo de indícios tem só 2 links: 1 correto (Zurich) e 1 errado (Territórios em Rede).

## 3. Onde publica

- **IDIS** publica o anúncio como post em "Notícias" (idis.org.br/<slug>/). Muitas vezes o regulamento fica em PDF no próprio `wp-content/uploads` do IDIS.
- **Financiadores:** Zurich tem página própria (zurich.com.br/leis-de-incentivo-AAAA). Mosaic publica notícia em mosaicco.com.br/Noticias e põe a ficha de inscrição para download. Instituto Chamex teve página de inscrição em 2025, que hoje dá 404, e em 2026 só aparece via IDIS. Catalyst 2030 publica post no site do capítulo brasileiro. Einstein não foi confirmado.
- **Plataformas de inscrição:** SurveyMonkey (Zurich, Chamex), e-mail para `@idisconsultoria.org.br` (Mosaic), Google Forms (Catalyst, Territórios em Rede) e regulamento com formulário próprio (IA.3). Não aparecem Prosas, Mapas Culturais nem Transferegov.
- O resultado sai por notícia no IDIS e no site do financiador, cerca de 1 a 2 meses após o prazo.

## 4. Tipos de oportunidade

- **Edital de projeto** com repasse financeiro: Chamex (R$ 35.000 a R$ 37.500, 5 a 6 projetos, educação), Mosaic Edital da Água (até R$ 45.000, de 10 a 12 projetos ou mais, água e saneamento, restrito a municípios de operação), Catalyst (R$ 240.000 no total, coalizões).
- **Captação via incentivo fiscal:** Zurich escolhe projetos já aprovados em Rouanet, Esporte, Fundo do Idoso ou FIA. O valor não é fixo e depende da disponibilidade da empresa.
- **Programa de fortalecimento / cadastro** (sem dinheiro direto): IA.3 (capacitação em IA, até 250 ONGs, nacional) e Territórios em Rede (mentoria e PDI, até 18 OSCs em SP e BA).
- Não foram encontrados prêmio, bolsa, fundo rotativo nem chamada internacional no período.
- **Áreas:** educação, água e saneamento, clima, inclusão produtiva, saúde, desenvolvimento institucional e tecnologia.
- **Quem pode participar:** OSC sem fins lucrativos com CNPJ. Alguns editais aceitam instituições de ensino e coletivos (Catalyst). O recorte territorial é frequente (Mosaic, Einstein).

## 5. Calendário

| Mês | O que abre (padrão observado) |
|---|---|
| Março | Edital Educação com Cidadania (Chamex), 2025 e 2026; Edital da Água 2026 |
| Abril/Maio | Edital da Água 2024 (prazo em maio) |
| Junho/Julho | Edital da Água 2025; Zurich 2025 |
| Setembro/Outubro | Zurich 2026; Territórios em Rede; IA.3 (out/2025); Catalyst (out/2024) |

O ciclo é anual. Os prazos são curtos, de 2 a 6 semanas entre o anúncio e o encerramento. O volume é baixo, cerca de 3 a 4 oportunidades por ano.

## 6. Conselho de 7 lentes (sobre o MOTOR)

1. **Extremamente pessimista — Dra. Helena Barbosa Kuster, chief engineer, rígida e obcecada por falha silenciosa.** "O feed estava 3 semanas atrasado no dia do teste. O motor marca 'satisfatório' com 2 achados enquanto a fonte esconde metade do ano. E o pior: um dos 2 indícios aponta um link oficial errado (transformandoterritorios.org.br), o que gera livro com URL de outro programa. Um motor que não sabe quando está cego é pior que nenhum."
2. **Pessimista — Prof. Rodrigo Tanaka, pós-doutor em Python, metódico.** "A relação sinal/ruído é ruim: o feed mistura vagas de emprego, mídia e artigos. Sem léxico de exclusão, 'Vaga para Estagiário… inscrições até 17/09' vira edital. O prazo vem no corpo em texto livre, como 'prorrogado de 03/04 para 10/04', e o parser precisa tratar prorrogação."
3. **Levemente pessimista — Marta Okonkwo-Lima, staff engineer, pragmática.** "A busca da API devolve poucos itens por termo e é sensível a acento ('inscrições' e 'inscricoes' dão resultados diferentes). A busca do Edital da Água por 'água' nem voltou. Depender só de busca textual perde post; é preciso varrer o sitemap."
4. **Neutro — Eng. Paulo Venturini, CTO de big tech, árbitro.** A síntese dele está abaixo.
5. **Levemente otimista — Prof.ª Luiza Andrade Ferraz, pós-doutora em Python, didática.** "A fonte é limpa: WordPress padrão, robots liberado, API com filtro de data e `_fields`. Com uma chamada por termo temos o histórico de 3 anos. Custo baixo e estabilidade alta."
6. **Otimista — Caio Mendes Rocha, chief engineer, entusiasta de dados.** "O IDIS é gestor técnico dos editais, então a informação é de primeira mão: prazo, valor, regulamento e e-mail de inscrição saem antes de aparecer em qualquer agregador grande. O padrão anual (Chamex em março, Zurich em setembro) permite alarme preditivo."
7. **Extremamente otimista — Dr. Sérgio Nakamura-Brandão, CTO visionário.** "Zurich é nacional e o financiamento por incentivo é recorrente. Se a A.M.C. Jardim América aprovar um projeto na Lei Rouanet, no FIA ou no Fundo do Idoso ao longo de 2027, entra todo ano nesse funil. O motor vira o gatilho de um calendário de captação, não só um coletor."

### Síntese do neutro (Paulo Venturini)

**Decisão:** manter o motor, **trocar a rota principal** do feed para a API REST do WordPress com filtro de data e léxico, e adotar o `post-sitemap.xml` como varredura semanal de segurança. O status deve passar de "satisfatório" para **"satisfatório com correção"**, porque o indício de Territórios em Rede tem link oficial errado.

**Melhorias:** ver a seção 7.

**Parâmetros de qualidade:**
- Atraso máximo entre a publicação no IDIS e a captura: 24 h.
- Precisão do filtro (o item capturado é edital ou chamada para OSC): 90% ou mais. Hoje o feed bruto dá cerca de 10%.
- 100% dos livros com `url` em domínio do financiador. Se não houver, `aguardar_fonte`.
- Prazo extraído em 95% ou mais dos itens, com a data prorrogada prevalecendo.
- Zero vagas de emprego ou eventos classificados como oportunidade.
- Revalidar o link oficial a cada 30 dias. Um 404 rebaixa o livro para `aguardar_fonte`.

**Riscos e mitigação:**
1. *Feed ou CDN em cache e desatualizado.* Mitigação: usar a API com `after=` e conferir o lastmod do sitemap.
2. *Busca textual perde posts (acento, limite de relevância).* Mitigação: termos com e sem acento, mais varredura do sitemap e leitura do título.
3. *Link oficial errado ou herdado de outro programa.* Mitigação: só aceitar URL cujo domínio seja do financiador citado e cuja página mencione o título do programa.
4. *Páginas oficiais efêmeras (Chamex deu 404 em 2025).* Mitigação: guardar `pagina_agregador` e o PDF do regulamento como prova histórica.
5. *Recorte territorial (Mosaic: GO só em Catalão, Ouvidor e Rio Verde).* Mitigação: extrair a lista de municípios e marcar `aplicavel` = "nao" quando Goiânia não estiver nela.
6. *Bloqueio do site do financiador (einstein.br deu 403).* Mitigação: registrar `aguardar_fonte` e não substituir a URL oficial pela do agregador.

## 7. Melhorias do motor (lista numerada)

1. **Rota:** substituir `https://www.idis.org.br/feed/` por `https://www.idis.org.br/wp-json/wp/v2/posts?after=<última_coleta>&per_page=100&_fields=date,link,title,content`, com o feed como fallback.
2. **Histórico:** fazer uma carga única via `post-sitemap.xml` e `post-sitemap2.xml`, filtrando lastmod de 2023-10-02 em diante, para fechar lacunas da busca textual.
3. **Léxico de inclusão no título:** "abre inscrições", "inscrições abertas", "edital", "chamada pública", "seleção de projetos", "selecionará", "desafio", "fundo". Usar formas com e sem acento.
4. **Léxico de exclusão:** "vaga", "estagiário", "anuncia contemplados", "vencedores", "Fórum Brasileiro", "IDIS na Mídia", "webinar", "retrospectiva".
5. **Filtro por categoria:** descartar as categorias 372 (IDIS na Mídia) e 22 (Artigos) e manter 84 (Notícias).
6. **Extração de prazo:** regex para "até DD de mês", "prorrogad[oa]" (vale a última data) e "inscrições de X a Y". Extrair também valor ("até R$"), número de vagas e lista de municípios.
7. **Link oficial:** pegar os links externos do corpo, excluir surveymonkey, forms.gle, docs.google, sympla e drive, e validar que o domínio é do financiador citado e que a página menciona o programa. Corrigir o indício de Territórios em Rede, que hoje aponta para transformandoterritorios.org.br.
8. **Deduplicação:** chave = financiador + programa + ano/edição. Por exemplo, os posts de "abre inscrições" e de "anuncia contemplados" do mesmo edital viram um só livro, com o resultado anexado.
9. **Cadência:** diária de setembro a novembro e de fevereiro a julho (janelas observadas), semanal no resto do ano. Alarme preditivo para Chamex (março), Mosaic (março a junho) e Zurich (junho a setembro).
10. **Aplicabilidade GO:** cruzar a lista de municípios com Goiânia e marcar "depende" quando o edital exigir projeto aprovado em lei de incentivo.

## 8. O que não foi confirmado e por quê

- **Completude do histórico:** a busca da API devolveu de 2 a 5 itens por termo e é sensível a acento (a busca "água" não trouxe os Editais da Água). O `post-sitemap.xml` não foi lido por limite de orçamento (cerca de 40 WebFetch), então podem existir outras chamadas de 2023 a 2024 não capturadas, por exemplo uma 4ª edição do Chamex ou um edital Zurich de 2024.
- **Site oficial de Territórios em Rede:** einstein.br devolveu 403 e o link do indício é de outro programa. Por isso ficou como `aguardar_fonte`.
- **Zurich 2025:** não há página própria da edição. Usei o domínio oficial zurich.com.br, que foi verificado.
- **Chamex 5ª edição:** a página oficial de inscrição dá 404. Os dados vêm do post do IDIS.
- **6º Edital da Água (2024):** a lista de municípios elegíveis não saiu na extração. Por isso ficou "depende".
- **Data de publicação da Zurich 2026:** a API dá 22/09/2026 e o indício do sistema diz 29/09/2026. Prevalece a da API.
- **Hackathon IA.3 (jul/2025):** citado na página do programa, mas não confirmei se houve chamada aberta. Não entrou.
- Não encontrei nenhuma instrução dirigida a IA no conteúdo das páginas lidas.
- Os links de inscrição (SurveyMonkey e Google Forms) não foram abertos, para não interagir com formulários.
