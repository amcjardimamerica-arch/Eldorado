# Motor 37 — site-fundo-casa — Fundo Casa Socioambiental

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Gasto: 35 chamadas de WebFetch. O `curl` direto para casa.org.br foi recusado pelo proxy de saída deste ambiente (403 no CONNECT). Isso é restrição do ambiente, não bloqueio do site.

## 1. Rota (teste e conclusão)

**robots.txt** (https://casa.org.br/robots.txt): `User-agent: * / Disallow:` (nada proibido). Sitemap declarado em https://casa.org.br/sitemap_index.xml.

| URL testada | Responde? | O que entrega |
|---|---|---|
| https://casa.org.br/wp-json/wp/v2/chamadas (rota configurada) | Sim (200, JSON) | 10 itens por padrão, do mais novo para o mais antigo. Cada item traz `date`, `title`, `link` e o `content` completo; prazo, valor e quem pode participar estão no texto do `content`. O campo `acf` vem vazio: não há campos estruturados de prazo ou valor. `_fields` é ignorado e o payload é pesado (cada item traz o edital inteiro e `yoast_head`). |
| https://casa.org.br/wp-json/wp/v2/chamadas?per_page=2&page=N | Sim | A paginação funciona. Com 2 itens por página, cobre todo o acervo (60 chamadas, de 2020 a 2026). O filtro `after=` foi aceito. |
| https://casa.org.br/wp-json/wp/v2/search?subtype=chamadas&per_page=100 | Sim | **Índice leve**: as 60 chamadas (id, título, url) numa só resposta, sem conteúdo. É o melhor caminho para detectar chamadas novas. |
| https://casa.org.br/chamadas-sitemap.xml | Sim | As mesmas 60 URLs, com `lastmod`. O `lastmod` reflete a última edição (publicação de resultado), não a data de lançamento. |
| https://casa.org.br/chamadas/ (página do titular) | Sim | Uma só seção, "Chamadas Encerradas", com as 59 a 60 chamadas e o rótulo "Encerrada". Sem paginação, filtro, datas ou valores. Hoje não há chamada aberta. |

**Conclusão.** A rota configurada é correta: é a API oficial do próprio financiador e traz o link oficial em `link`. Melhor arranjo verificado: (a) descobrir com `wp-json/wp/v2/search?subtype=chamadas&per_page=100` ou com `chamadas-sitemap.xml`; (b) detalhar só os ids novos com `wp-json/wp/v2/chamadas/{id}` ou `?include={id}`, e extrair do `content` o prazo ("De DD/MM/AAAA a DD/MM/AAAA até 18h"), o valor ("R$ … total" e "até R$ … por projeto") e a abrangência. O "satisfatório — 1 achado" do painel subestima a fonte: o acervo do período tem 32 chamadas.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

Método: o índice da API search (60 chamadas) mais a leitura do `content` página a página (`per_page=2`, páginas 1 a 18) e de 5 páginas oficiais para completar dados. Entraram as chamadas publicadas no período ou com prazo dentro dele. Ficaram de fora, por terem prazo anterior a 02/10/2023: MATOPIBA (prazo 26/09/2023), Povos das Florestas (07/07/2023), Educação para o Bem Viver 2023 (27/07/2023) e Mata Atlântica 2023 (27/06/2023).

Resultado: **32 chamadas. 0 abertas, 31 encerradas (encerrado_arquivar) e 1 sem data.** Aplicáveis a uma OSC de Goiânia/GO: 0 "sim", 14 "depende" e 18 "não".

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2026-07-17 | Mulheres que Transformam o Futuro – Apoio a Soluções Comunitárias para a Resiliência Climática e a Justiça Socioambiental | Fundo Casa Socioambiental | https://casa.org.br/chamadas/mulheres-que-transformam-o-futuro-apoio-a-solucoes-comunitarias-para-a-resiliencia-climatica-e-a-justica-socioambiental/ | 2026-08-25 | ENCERRADA | depende |
| 2026-06-15 | Chamada Simplificada – Apoio Direto a Iniciativas Comunitárias | Fundo Casa Socioambiental | https://casa.org.br/chamadas/chamada-simplificada-apoio-direto-a-iniciativas-comunitarias/ | 2026-07-14 | ENCERRADA | depende |
| 2026-06-01 | Juventudes e Justiça Climática – Apoio a soluções lideradas por juventudes periféricas e de comunidades tradicionais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/juventudes-e-justica-climatica-apoio-a-solucoes-lideradas-por-juventudes-perifericas-e-de-comunidades-tradicionais/ | 2026-06-30 | ENCERRADA | depende |
| 2026-05-11 | Territórios Vivos da Amazônia: apoio a soluções comunitárias | Fundo Casa Socioambiental | https://casa.org.br/chamadas/territorios-vivos-da-amazonia-apoio-a-solucoes-comunitarias/ | 2026-06-16 | ENCERRADA | nao |
| 2026-04-10 | Fortalecimento dos direitos territoriais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/fortalecimento-dos-direitos-territoriais/ | 2026-05-19 | ENCERRADA | nao |
| 2026-03-16 | Chamada Educação para o Bem Viver 2026 – Fortalecendo organizações indígenas e quilombolas pela equidade na educação | Fundo Casa Socioambiental | https://casa.org.br/chamadas/chamada-educacao-para-o-bem-viver-2026-fortalecendo-organizacoes-indigenas-e-quilombolas-pela-equidade-na-educacao/ | 2026-04-28 | ENCERRADA | nao |
| 2026-02-26 | Crédito Comunitário Sustentável (CCS) – Ampliando o acesso ao crédito rural para agricultores e agricultoras familiares por meio de organizações comunitárias | Fundo Casa Socioambiental | https://casa.org.br/chamadas/credito-comunitario-sustentavel-ccs-ampliando-o-acesso-ao-credito-rural-para-agricultores-e-agricultoras-familiares-por-meio-de-organizacoes-comunitarias/ | 2026-04-09 | ENCERRADA | nao |
| 2026-02-20 | Mata Atlântica Viva – Apoiando soluções para conservação e regeneração 2026 | Fundo Casa Socioambiental | https://casa.org.br/chamadas/mata-atlantica-viva-apoiando-solucoes-para-conservacao-e-regeneracao-2026/ | 2026-03-25 | ENCERRADA | depende |
| 2026-01-05 | Apoio a ações comunitárias frente aos incêndios florestais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/apoio-a-acoes-comunitarias-frente-aos-incendios-florestais/ | 2026-02-04 | ENCERRADA | depende |
| 2025-11-11 | Teia da Sociobiodiversidade – 2025 | Fundo Casa Socioambiental | https://casa.org.br/chamadas/teia-da-sociobiodiversidade-2025/ | 2025-12-16 | ENCERRADA | depende |
| 2025-08-15 | Reconstruir RS – Apoio à Resiliência Climática e Reconstrução Comunitária 2025 | Fundo Casa Socioambiental | https://casa.org.br/chamadas/reconstruir-rs-apoio-a-resiliencia-climatica-e-reconstrucao-comunitaria-2025/ | 2025-09-22 | ENCERRADA | nao |
| 2025-07-10 | Fortalecimento dos direitos territoriais frente a megaprojetos de energia | Fundo Casa Socioambiental | https://casa.org.br/chamadas/fortalecimento-dos-direitos-territoriais-frente-a-megaprojetos-de-energia-2/ | 2025-08-12 | ENCERRADA | nao |
| 2025-06-04 | Amazônia Resiliente – Fortalecendo Soluções Comunitárias Frente às Mudanças Climáticas | Fundo Casa Socioambiental | https://casa.org.br/chamadas/amazonia-resiliente-fortalecendo-solucoes-comunitarias-frente-as-mudancas-climaticas/ | 2025-07-10 | ENCERRADA | nao |
| 2025-05-06 | Amazônia Viva – Fortalecendo a Autonomia e a Resiliência dos Povos da Floresta | Fundo Casa Socioambiental | https://casa.org.br/chamadas/amazonia-viva-fortalecendo-a-autonomia-e-a-resiliencia-dos-povos-da-floresta/ | 2025-06-24 | ENCERRADA | nao |
| 2025-04-07 | Fortalecendo o protagonismo local na agenda climática – Apoio a ações de incidência e produção de conhecimento para a COP30 e outros espaços | Fundo Casa Socioambiental | https://casa.org.br/chamadas/fortalecendo-o-protagonismo-local-na-agenda-climatica-apoio-a-acoes-de-incidencia-e-producao-de-conhecimento-para-a-cop30-e-outros-espacos/ | 2025-05-08 | ENCERRADA | depende |
| 2025-02-19 | Educação para o bem-viver: apoio às comunidades quilombolas por uma educação antirracista | Fundo Casa Socioambiental | https://casa.org.br/chamadas/educacao-para-o-bem-viver-apoio-as-comunidades-quilombolas-por-uma-educacao-antirracista/ | 2025-03-25 | ENCERRADA | nao |
| 2025-02-03 | Mata Atlântica Viva – apoiando soluções para conservação e regeneração | Fundo Casa Socioambiental | https://casa.org.br/chamadas/mata-atlantica-viva-apoiando-solucoes-para-conservacao-e-regeneracao/ | 2025-03-10 | ENCERRADA | depende |
| 2025-01-23 | Educação para o bem-viver – Apoio às comunidades indígenas pela equidade na educação | Fundo Casa Socioambiental | https://casa.org.br/chamadas/educacao-para-o-bem-viver-apoio-as-comunidades-indigenas-pela-equidade-na-educacao-2/ | 2025-03-27 | ENCERRADA | nao |
| 2024-10-18 | Teia da Sociobiodiversidade – 2024 | Fundo Casa Socioambiental | https://casa.org.br/chamadas/teia-da-sociobiodiversidade/ | 2024-12-16 | ENCERRADA | depende |
| 2024-09-26 | Apoio a grupos locais no enfrentamento de Emergências Climáticas provocadas a partir dos Incêndios Florestais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/apoio-a-grupos-locais-no-enfrentamento-de-emergencias-climaticas-provocadas-a-partir-dos-incendios-florestais/ | 2024-10-28 | ENCERRADA | depende |
| 2024-09-05 | Reforço imediato: Apoio Emergencial às Brigadas Voluntárias e Comunitárias | Fundo Casa Socioambiental | https://casa.org.br/chamadas/reforco-imediato-apoio-emergencial-as-brigadas-voluntarias-e-comunitarias/ | — | SEM_DATA | depende |
| 2024-08-02 | Transição energética justa: fortalecendo e aplicando salvaguardas sociais e ambientais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/transicao-energetica-justa-fortalecendo-e-aplicando-salvaguardas-sociais-e-ambientais/ | 2024-09-16 | ENCERRADA | nao |
| 2024-07-16 | Reconstruir RS – Apoio à Resiliência Climática e Reconstrução Comunitária | Fundo Casa Socioambiental | https://casa.org.br/chamadas/reconstruir-rs-apoio-a-resiliencia-climatica-e-reconstrucao-comunitaria/ | 2024-09-03 | ENCERRADA | nao |
| 2024-04-18 | Fortalecendo juventudes no enfrentamento ao racismo ambiental | Fundo Casa Socioambiental | https://casa.org.br/chamadas/fortalecendo-juventudes-no-enfrentamento-ao-racismo-ambiental/ | 2024-05-20 | ENCERRADA | depende |
| 2024-04-10 | Defensores ambientais: Vozes pela ação climática | Fundo Casa Socioambiental | https://casa.org.br/chamadas/defensores-ambientais-vozes-pela-acao-climatica/ | 2024-05-10 | ENCERRADA | nao |
| 2024-04-04 | Transição energética justa e fortalecimento da pesca artesanal | Fundo Casa Socioambiental | https://casa.org.br/chamadas/transicao-energetica-justa-e-fortalecimento-da-pesca-artesanal/ | 2024-05-22 | ENCERRADA | nao |
| 2024-03-20 | Amazônia Viva – Fortalecendo a Autonomia e Resiliência dos Povos da Floresta | Fundo Casa Socioambiental | https://casa.org.br/chamadas/amazonia-viva-fortalecendo-a-autonomia-e-resiliencia-dos-povos-da-floresta/ | 2024-05-20 | ENCERRADA | nao |
| 2024-02-27 | Comunicação Comunitária e Direitos Humanos – Fortalecimento de organizações, coletivos e redes de comunicação comunitária e popular | Fundo Casa Socioambiental | https://casa.org.br/chamadas/comunicacao-comunitaria-e-direitos-humanos-fortalecimento-de-organizacoes-coletivos-e-redes-de-comunicacao-comunitaria-e-popular/ | 2024-04-01 | ENCERRADA | nao |
| 2024-01-18 | Resiliência Climática e Equidade de Gênero: Fortalecendo Comunidades para Promoção da Inclusão e Diversidade | Fundo Casa Socioambiental | https://casa.org.br/chamadas/resiliencia-climatica-e-equidade-de-genero-fortalecendo-comunidades-para-promocao-da-inclusao-e-diversidade/ | 2024-02-19 | ENCERRADA | depende |
| 2023-12-18 | Amazônia Resiliente II – Fortalecimento de Organizações Locais e de Populações Tradicionais – Povos da Floresta | Fundo Casa Socioambiental | https://casa.org.br/chamadas/amazonia-resiliente-ii-fortalecimento-de-organizacoes-locais-e-de-populacoes-tradicionais-povos-da-floresta/ | 2024-01-31 | ENCERRADA | nao |
| 2023-09-27 | Apoio a Grupos de Base no Enfrentamento de Emergências Climáticas Provocadas a partir dos Incêndios Florestais | Fundo Casa Socioambiental | https://casa.org.br/chamadas/apoio-a-grupos-de-base-no-enfrentamento-de-emergencias-climaticas-provocadas-a-partir-dos-incendios-florestais-3/ | 2023-11-05 | ENCERRADA | depende |
| 2023-09-06 | Fortalecendo a autonomia e resiliência dos Povos Indígenas – Apoio ao enfrentamento de incêndios florestais e monitoramento territorial na Amazônia | Fundo Casa Socioambiental | https://casa.org.br/chamadas/fortalecendo-a-autonomia-e-resiliencia-dos-povos-indigenas-apoio-ao-enfrentamento-de-incendios-florestais-e-monitoramento-territorial-na-amazonia/ | 2023-10-16 | ENCERRADA | nao |
Observações:
- "data" é o campo `date` da API (publicação). As páginas exibem "modificado em", que é a data do resultado. Exemplo: a Chamada Simplificada mostra 08/09/2026, mas abriu em 15/06/2026.
- Reforço Imediato (2024) fica como SEM_DATA: o texto diz "a partir de 06/09/2024" e não traz data final (apoio emergencial com divulgação semanal).
- O indício já guardado (Teia da Sociobiodiversidade 2025) foi verificado. O link abre e é do próprio financiador. O prazo era 16/12/2025, e no indício estava `null`. O resultado (203 selecionados) saiu em 27/03/2026. Ele entrou em livros.json com `"fonte": "verificado"`.
- Critério do "depende": são chamadas de abrangência nacional, mas exigem perfil específico (comunidade tradicional ou local, liderança jovem ou feminina, brigada, organização nova ou que retoma atividades) e teto de orçamento entre R$ 200 mil e R$ 500 mil. Uma associação de bairro de Goiânia só entra se comprovar esse perfil. O "não" cobre as chamadas restritas a Amazônia Legal, Nordeste, Matopiba ou RS (nenhuma inclui GO), a públicos exclusivamente indígenas ou quilombolas e ao crédito rural (CCS).

## 3. Onde publica

- **Site oficial**: https://casa.org.br/chamadas/, um post do tipo `chamadas` no WordPress, com a versão em inglês em /en/calls/. O edital completo fica no corpo do post: datas, valor, elegibilidade, documentos, oficina tira-dúvidas e e-mail de contato.
- **Inscrição**: até o início de 2024, por formulário Word e planilha Excel enviados a e-mails dedicados (clima@, florestas@, matopiba@, chamadaMMAA@casa.org.br). De 2024 a 2025 o modelo foi híbrido (CasaDigital ou e-mail). Desde 2025, a inscrição é **exclusivamente pela plataforma própria CasaDigital** (https://bd.casa.org.br/CasaDigital/Create?chamadaId=NN). Não usa Prosas, Mapas Culturais nem Transferegov.
- **Resultados**: publicados no próprio post da chamada e em https://casa.org.br/noticias.
- **Financiadores por trás** (o Fundo Casa faz o regranting; os editais são do Fundo Casa): MacKenzie Scott (Yield Giving), Fundo Socioambiental CAIXA, Instituto Itaúsa, Gordon and Betty Moore Foundation, Charles Stewart Mott Foundation, Imaginable Futures, Global Greengrants Fund, Alliance for the Amazon and Beyond, Hempel Foundation, Comic Relief, Forests People Climate, Fondation CHANEL, VEJA, Fundação Arymax, Porticus, Oak Foundation, Instituto Clima e Sociedade, WWF-Brasil, Fundación Avina, Hivos, IEB, Aliança GAGGA, BrazilFoundation, GlobalGiving, Wellspring, Embaixada da França, entre outros. Todos chegam ao titular pelo mesmo canal: o site do Fundo Casa.

## 4. Tipos de oportunidade

- **Edital de projeto (chamada de projetos)**: 31 das 32. São apoios de R$ 20 mil a R$ 100 mil por projeto, com execução de 10 a 12 meses. O desembolso costuma ser de 90% na assinatura e 10% após o relatório.
- **Crédito comunitário / fundo rotativo** (CCS 2026): até R$ 100 mil para organizações rurais operarem crédito a agricultores familiares. Classificado como "outro".
- **Apoio emergencial de fluxo contínuo** (Reforço Imediato 2024, brigadas): até R$ 20 mil.
- Não há prêmio, bolsa, cadastro nem chamada internacional no período. Houve chamadas sul-americanas apenas até 2022.
- **Áreas**: clima e incêndios florestais, direitos territoriais, Amazônia, Mata Atlântica, sociobiodiversidade, educação indígena e quilombola, gênero, juventudes, comunicação comunitária, transição energética justa, pesca artesanal, reconstrução no RS.
- **Faixas de valor**: R$ 450 mil a R$ 3,6 milhões por chamada (a Teia soma R$ 20 milhões em duas chamadas). Por projeto: R$ 20 mil, R$ 30 mil, R$ 40 mil, R$ 50 mil, R$ 60 mil, R$ 70 mil ou R$ 100 mil. A moda é R$ 50 mil a R$ 60 mil.
- **Quem pode**: organizações de base sem fins lucrativos com orçamento anual de até R$ 200 mil, R$ 250 mil, R$ 300 mil ou R$ 500 mil. Há prioridade para povos indígenas, quilombolas, comunidades tradicionais, periferias e brigadas. Grupos sem CNPJ entram via organização parceira, com exceção da Teia e do CCS, que exigem CNPJ. Uma proposta por organização.

## 5. Calendário

Lançamentos no período (mês de abertura):

| Mês | Chamadas |
|---|---|
| jan | Resiliência e Gênero (2024), EBV Indígena (2025), Incêndios (2026) |
| fev | Comunicação Comunitária (2024), Mata Atlântica Viva e EBV Quilombola (2025), CCS e Mata Atlântica Viva (2026) |
| mar | Amazônia Viva (2024), EBV 2026 |
| abr | Defensores, Pesca Artesanal e Juventudes (2024), COP30 (2025), Direitos Territoriais (2026) |
| mai | Amazônia Viva (2025), Territórios Vivos (2026) |
| jun | Amazônia Resiliente (2025), Juventudes e Simplificada (2026) |
| jul | Reconstruir RS (2024), Megaprojetos de Energia (2025), Mulheres (2026) |
| ago | Transição Energética (2024), Reconstruir RS (2025) |
| set | Incêndios e Povos Indígenas (2023), Reforço Imediato e Incêndios (2024) |
| out | Teia 2024 |
| nov | Teia 2025 |
| dez | Amazônia Resiliente II (2023) |

O ritmo é de cerca de 10 a 11 chamadas por ano, com janela de inscrição de 30 a 45 dias (fechamento às 18h). Há duas temporadas fortes: **fevereiro a abril** (Mata Atlântica, Educação para o Bem Viver, temas anuais) e **setembro a novembro** (incêndios, Teia). As chamadas recorrentes são: Incêndios (set/out ou jan), Mata Atlântica Viva (fev), Educação para o Bem Viver (jan a mar), Amazônia Viva ou Resiliente (mai/jun), Teia (out/nov) e Juventudes (abr a jun). Previsão para out a dez/2026: provável chamada de incêndios e/ou nova edição da Teia. É previsão; não foi confirmada.

## 6. Conselho de 7 lentes, com a síntese do neutro

1. **Extremamente pessimista — Dra. Helga Brandt, chief engineer, rabugenta e precisa.** "O painel diz 'satisfatório' com 1 achado num site que publicou 32 chamadas em três anos. O motor lê a API, mas não extrai nada: `acf` vazio, prazo e valor enterrados no HTML do `content`. O indício chegou com `prazo: null` e `uf: null`, e o próprio texto dizia 16/12/2025. Isso é motor cego que acha que enxerga."
2. **Pessimista — Prof. Otávio Lacerda, pós-doc em Python, metódico.** "Por padrão, a rota devolve 10 itens com o edital inteiro, e `_fields` é ignorado. Se o leitor não pagina, perde o histórico; se pagina com per_page alto, o payload explode. E a `date` da API não é a data de abertura: a página exibe 'modificado em' (a data do resultado), o que confunde a deduplicação por data."
3. **Levemente pessimista — Renata Ishikawa, staff engineer, pragmática.** "A taxa de aplicabilidade para Goiânia é baixa: 0 'sim', 14 'depende'. Sem filtro de abrangência (Amazônia Legal, NE, RS) e de perfil (tradicional, juventude), o titular vai receber alertas inúteis. E não existe status 'aberta' estruturado: precisa vir do parse do período."
4. **Neutro — Dr. Marcelo Antunes, CTO de big tech, sereno.** (síntese abaixo)
5. **Levemente otimista — Prof.ª Lúcia Ferraz, pós-doc em computação, didática.** "A fonte é limpa e estável: WordPress com robots liberado, API pública, sitemap e índice de busca. O texto segue um molde fixo ('De DD/MM/AAAA a DD/MM/AAAA até as 18h', 'até R$ X,00'). Um parser de regex resolve mais de 90% dos casos."
6. **Otimista — Diego Sampaio, chief engineer, entusiasmado.** "São cerca de 10 chamadas por ano, de R$ 50 mil a R$ 100 mil, sem contrapartida, com inscrição simples e aceitando grupos sem CNPJ. Várias são nacionais (Teia, Incêndios, Simplificada, COP30, Resiliência e Gênero). Para uma associação comunitária, é das fontes de maior valor esperado."
7. **Extremamente otimista — Prof. Arthur Nogueira, pós-doc em Python, visionário.** "Com histórico parseado, o motor prevê a próxima Teia e a próxima de Incêndios e avisa o titular semanas antes, com a documentação pronta. O link oficial é sempre do financiador, o que dá livros 100% limpos. O ganho ideal é a recomendação ativa, não só o alerta."

**Síntese do neutro (Dr. Marcelo Antunes)**

- **Decisão**: MANTER o motor 37 com a rota atual (é a API oficial) e REBAIXAR o status do painel para "parcial", até que o parse de prazo, valor e abrangência funcione. Não há chamada aberta hoje; as 32 do período vão para os livros como `encerrado_arquivar` (31) e `sem_data` (1).
- **Melhorias**: ver a seção 7.
- **Parâmetros de qualidade**:
  - cobertura de 100% das URLs do `chamadas-sitemap.xml` / search;
  - prazo extraído em pelo menos 95% das chamadas posteriores a 2023;
  - valor por projeto extraído em pelo menos 90%;
  - zero livros com `url` fora de casa.org.br/chamadas;
  - latência menor que 24 h entre a publicação e o alerta;
  - zero duplicatas por id WP;
  - 0% de alertas "aplicável" para chamadas restritas a regiões sem GO.
- **Riscos e mitigação**:
  - (R1) Mudança de layout ou texto quebra a regex. Mitigação: testes com as 32 chamadas como fixture e alerta quando o prazo vier vazio em post novo.
  - (R2) Payload pesado ou rate limit. Mitigação: usar search/sitemap para descobrir, detalhar só ids novos e manter cadência diária, não horária.
  - (R3) "Modificado em" tratado como chamada nova (republicação ao divulgar resultado). Mitigação: chave = id WP, mais detecção de "resultado/selecionados".
  - (R4) Prorrogação ("PRORROGADA", "INSCRIÇÕES PRORROGADAS" no título) não captada. Mitigação: reprocessar posts com `modified` recente e atualizar o prazo.
  - (R5) Falso "aplicável" por abrangência. Mitigação: dicionário de abrangência (Amazônia Legal, Nordeste, Matopiba, RS, bioma Mata Atlântica) cruzado com a UF do titular.
  - (R6) Acesso direto bloqueado no ambiente (o proxy recusou o curl). Mitigação: rodar o motor no coletor local/navegador, que já tem acesso.

## 7. Melhorias do motor (lista numerada)

1. **Rota/descoberta**: trocar a varredura da lista completa por `https://casa.org.br/wp-json/wp/v2/search?subtype=chamadas&per_page=100` (ou `chamadas-sitemap.xml`) para detectar ids novos, e buscar o detalhe em `https://casa.org.br/wp-json/wp/v2/chamadas?include={id}`.
2. **Parse de prazo**: regex sobre o `content` sem HTML, com padrões `De (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})`, `(\d{1,2}) de (mês) (a|até) (\d{1,2}) de (mês) de (\d{4})` e "prorrogad[ao] até DD/MM/AAAA". Gravar `inicio` e `prazo`.
3. **Parse de valor**: capturar o "total de R$ X" e o "até R$ Y por projeto/iniciativa" e o número de projetos.
4. **Filtro de abrangência e perfil**: classificar a abrangência em Nacional, Amazônia Legal, Nordeste, Matopiba, RS ou bioma, e o público (tradicional, jovens, mulheres, brigadas, rural). Marcar "nao" quando GO estiver fora e "depende" quando houver exigência de perfil.
5. **Léxico de status**: "Encerrada", "CONFIRA A LISTA DOS SELECIONADOS", "resultado", "PRORROGADA". O status "aberta" deve vir de `prazo ≥ hoje`, nunca do rótulo da página.
6. **Cadência**: diária às 8h, com leitura extra quando `lastmod` do `chamadas-sitemap.xml` mudar. Em fev a abr e set a nov (temporadas fortes), ler a cada 12 h.
7. **Histórico**: importar as 32 chamadas de livros.json como base de previsão por série (Teia, Incêndios, Mata Atlântica Viva, EBV, Amazônia Viva, Juventudes) e emitir um "pré-alerta" no mês típico de abertura.
8. **Deduplicação**: chave = id WP (`id`), com o slug como reserva (os slugs com sufixo -2 e -3 são edições novas, não duplicatas). Nunca usar a data "modificado".
9. **Link oficial**: `url` = campo `link` da API (casa.org.br/chamadas/...). Guardar também a URL CasaDigital (`chamadaId=NN`) como `link_inscricao`.

## 8. O que não foi confirmado e por quê

- **Data final do Reforço Imediato (2024)**: o texto só diz "a partir de 06/09/2024". Ficou como SEM_DATA.
- **Financiadores de 2 chamadas** (Pesca Artesanal 2024 e Povos Indígenas/Incêndios 2023): o extrator não encontrou apoiadores citados; o campo ficou só com Fundo Casa.
- **Inclusão de Goiás no bioma Mata Atlântica** (chamadas MA 2025/2026): o edital fala em "17 estados" sem listá-los no trecho lido. Ficou "depende", e Goiânia, que está no Cerrado, provavelmente não se enquadra.
- **Leitura via WebFetch**: os dados vieram de um extrator que resume a página. Valores e datas foram conferidos em mais de uma leitura quando houve conflito, como a data de publicação "modificado em" contra a `date` da API. Uma conferência byte a byte via `curl` não foi possível, porque o proxy do ambiente recusou a conexão.
- **Chamadas futuras (out a dez/2026)**: são previsão pelo calendário, sem confirmação.
- **Instruções dirigidas a IA**: nenhuma foi encontrada nas páginas lidas.
- Não foram coletados dados pessoais. As listas de selecionados citam entidades, que não foram transcritas.
