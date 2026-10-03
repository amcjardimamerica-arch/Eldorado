# Motor 36 — site-undef — UNDEF (Fundo das Nações Unidas para a Democracia)

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica as próprias chamadas). Período analisado: 02/10/2023 a 02/10/2026. Foram usadas 24 chamadas de WebFetch. O WebSearch está bloqueado para a organização (HTTP 403 no proxy), e o curl direto também foi recusado pelo proxy (403). Por isso, toda a coleta foi feita com WebFetch nas páginas oficiais.

robots.txt (`https://www.un.org/robots.txt`): pede `Crawl-delay: 10` e bloqueia apenas diretórios de sistema (`/admin/`, `/search/`, `/node/add/`, login etc.). Não bloqueia `/democracyfund/` e não declara sitemap. Todos os acessos deste estudo ficaram dentro do que é permitido.

Nenhuma página continha instruções dirigidas ao agente.

---

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| Rota configurada: `None` (leitor html_listagem) | — | Não há rota configurada. O leitor cai na página do titular. |
| `https://www.un.org/democracyfund/` (página do titular) | Sim (200) | 12 notícias com data e link, mais links fixos (Apply for Funding, Projects, Evaluations). Não informa prazo, valor nem estado da rodada. Quase tudo é notícia de projeto, não chamada. |
| `https://www.un.org/democracyfund/en/apply-for-funding` | Sim | É a página canônica da chamada. Traz janela (abertura e prazo), valor (US$ 100 mil a 200 mil), duração, temas e regra de envio (só OPPS). Em 02/10/2026 ainda mostrava a janela de 2025 (01 a 28/02/2025). |
| `https://www.un.org/democracyfund/en/content/when-apply-and-who-can-apply` | Sim | Elegibilidade completa. Traz o aviso de que os detalhes da chamada de 2026 serão publicados ali. Foi o melhor sinal de "próxima chamada" encontrado. |
| `https://www.un.org/democracyfund/node/310` (All Stories) | Sim | Arquivo de notícias com data, título e link, cerca de 50 por página. A paginação usa `?block_config_key=block_1.2cqOwwJ0T8UWUeGu_zRPZG1BCBeEnHlS954F_hwOvhg&page=N` (page=1 volta até maio/2021). É aqui que saem os anúncios de chamada e de resultado. |
| `https://www.un.org/democracyfund/en/news` | Sim | O mesmo conteúdo de node/310. |
| `https://www.un.org/democracyfund/sitemap.xml` | Não (404) | Não existe. |
| `https://www.un.org/democracyfund/en/news/undef-advisory-board-endorses-projects-19th-round-funding` (URL deduzida) | Não (404) | Não há notícia de resultado da Rodada 19 nesse padrão. |
| `http://projects.undemocracyfund.org/` | Sim | Banco oficial de projetos financiados, com filtros por rodada ("R19 - 2025" até "R1 - 2006"), país, foco e região. O filtro é um formulário: `?round=19` não filtra. Serve para histórico e previsão, não para captação. |
| `https://www.un.org/democracyfund/en/newsletters` | Sim | Só tem edições até 2022. Não serve. |

**Conclusão.** A rota atual ("None", que cai na home) é fraca: entrega notícias de projetos e nenhuma chamada estruturada. Os 2 achados do painel mostram isso. Um deles é a própria página Apply (útil); o outro é uma notícia de mesa-redonda da CSW, que é um falso positivo.

**Rota melhor verificada.** Recomendo 3 URLs fixas, com leitor de página única e detecção de mudança:
1. `https://www.un.org/democracyfund/en/apply-for-funding` (principal: janela, prazo e valor);
2. `https://www.un.org/democracyfund/en/content/when-apply-and-who-can-apply` (aviso da chamada do ano e elegibilidade);
3. `https://www.un.org/democracyfund/node/310` (listagem de notícias, filtrada por léxico de chamada: "call for proposals", "round of funding", "annual call", "opens").

Não existe API, feed RSS nem sitemap.

---

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

O UNDEF faz uma única chamada por ano (ou por ciclo), com janela de cerca de 1 mês. No período, duas janelas foram confirmadas e uma terceira está anunciada sem data.

| data (publicação) | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2023-10-20 | 18th annual call for proposals (Rodada 18), janela 01 a 30/11/2023 | UNDEF | https://www.un.org/democracyfund/en/news/undef%E2%80%99s-advisory-board-approves-new-call-proposals-opens-1-30-november-2023 | 2023-11-30 | ENCERRADA (encerrado_arquivar) | depende |
| "" (abertura em 2025-02-01) | Chamada anual 2025 (Rodada 19), janela 01 a 28/02/2025 | UNDEF | https://www.un.org/democracyfund/en/apply-for-funding | 2025-02-28 | ENCERRADA (encerrado_arquivar) | depende |
| "" | Chamada anual 2026, anunciada mas sem datas publicadas | UNDEF | https://www.un.org/democracyfund/en/content/when-apply-and-who-can-apply | "" | SEM_DATA | depende |

Eventos do período que não são oportunidades, mas ajudam na previsão:
- 29/04/2024: o Conselho Consultivo endossou 39 projetos da Rodada 18. Foram 1.863 propostas de 133 países, somando mais de US$ 7,6 milhões. A taxa de aprovação ficou perto de 2,1%, com uma lista longa de 201 projetos.
- O banco de projetos registra pelo menos um projeto R19 (Ucrânia, US$ 198 mil, de outubro/2026 a março/2028). Isso indica que a seleção da R19 só fechou em 2026.
- Projetos no Brasil aparecem no banco: Associação Direitos Humanos em Rede (R18, US$ 165 mil) e Delibera Brasil (R17, US$ 198 mil). Isso prova que OSCs brasileiras são financiadas.

Sobre os 2 indícios do sistema:
- `apply-for-funding`: verificado. É a página oficial da chamada de 2025 (R19) e entrou em livros.json com fonte "verificado".
- `undef-cso-round-table-during-70th-session-csw` (25/03/2026): verificado como notícia de evento (mesa-redonda com 10 OSCs), não como oportunidade. É um falso positivo e não gera livro.

Por que "depende" e não "sim": a associação de Goiânia pode concorrer, porque não há restrição de país e basta ser legalmente constituída. Mas há quatro condições: o projeto precisa ser de democracia, governança ou direitos; o texto deve ser em inglês ou francês; o valor mínimo é de US$ 100 mil; e o UNDEF dá preferência a países menos desenvolvidos ou em transição democrática, enquanto o Brasil é de renda média-alta.

---

## 3. Onde publica

- **Site oficial:** `un.org/democracyfund`, um site Drupal da ONU dentro do UN Office for Partnerships.
- **Página de editais:** "Apply for Funding" (`/en/apply-for-funding`), apoiada por FAQs (`/en/apply-for-funding-faqs` e subpáginas `/en/content/...`) e pela página de diretrizes (`/content/proposal-guideline-technical-support`, com PDFs em inglês e francês).
- **Anúncio:** notícia no arquivo "All Stories" (node/310), publicada cerca de 10 a 30 dias antes da abertura (ex.: 20/10/2023 para a janela de 01/11/2023). Em 2025 não houve notícia de abertura no arquivo, só a atualização da página Apply. Por isso o motor não pode depender apenas das notícias.
- **Plataforma de inscrição:** formulário próprio, o Online Project Proposal System (OPPS), aberto só durante a janela. O UNDEF não aceita e-mail, correio nem entrega em mãos. Não usa Prosas, Mapas Culturais nem Transferegov.
- **Resultados:** notícia do Conselho Consultivo e banco `projects.undemocracyfund.org`.

## 4. Tipos de oportunidade

- **Tipo:** apenas chamada internacional de projetos (subvenção a fundo perdido). Não oferece prêmio, bolsa, cadastro nem fluxo contínuo.
- **Valor:** de US$ 100.000 a US$ 200.000 por projeto, com duração padrão de 2 anos. A Rodada 18 somou US$ 7,6 milhões em 39 projetos.
- **Áreas:** Estado de direito e direitos humanos; mídia e liberdade de informação; liderança e empoderamento de mulheres; juventude; interação sociedade civil-governo; processos eleitorais; engajamento cívico para ação climática (ênfase desde 2023); ativismo comunitário; ferramentas de conhecimento.
- **Quem pode:** OSC/ONG que promovam a democracia; órgãos independentes e constitucionais (comissões eleitorais, ouvidorias, instituições nacionais de direitos humanos); organismos intergovernamentais globais ou regionais que não sejam da ONU. O proponente precisa ser legalmente constituído e não precisa de credenciamento na ONU. O UNDEF prioriza a sociedade civil local. Pessoa física e empresa não aparecem como elegíveis. Na prática, financia no máximo um projeto por organização.
- **Concorrência:** cerca de 1.870 propostas por rodada para 34 a 39 projetos, o que dá aprovação de cerca de 2%.

## 5. Calendário

| Rodada | Anúncio | Janela | Lista curta | Aprovação / início |
|---|---|---|---|---|
| R17 | 07/11/2022 | novembro/2022 | — | endosso em 27/03/2023 |
| R18 | 20/10/2023 | 01 a 30/11/2023 | — | endosso em 29/04/2024 (39 projetos) |
| R19 | sem notícia (página Apply) | 01 a 28/02/2025 | junho/julho (padrão do FAQ) | "não antes de setembro/2025", com projetos iniciando até out/2026 |
| 2026 | anunciada ("details of the 2026 call will be available here") | não publicada até 02/10/2026 | — | — |

Padrão: uma janela por ano, de cerca de 4 semanas, historicamente em novembro (R15 a R18) e em fevereiro na R19. A pré-seleção sai em junho/julho e a aprovação a partir de setembro. Os intervalos entre rodadas estão aumentando (R18 em novembro/2023, R19 em fevereiro/2025, 2026 ainda sem data). O monitor deve estar ativo sobretudo de outubro a março.

---

## 6. Conselho de 7 lentes sobre o MOTOR

**1. Extremamente pessimista: Dra. Helga Vasconcelos, professora de Computação (pós-doutorado em Python, sistemas de recuperação de informação), implacável.**
"O motor não tem rota: está literalmente configurado como `None`. Lê a home de um site institucional da ONU e chama de 'satisfatório' um resultado de 2 achados, dos quais 1 é notícia de mesa-redonda. Isso é uma taxa de falso positivo de 50% numa amostra minúscula. Pior: em fevereiro de 2025 a chamada abriu e fechou sem nenhuma notícia no arquivo. Um leitor de listagem de notícias teria perdido a janela inteira. E não há sitemap, feed nem API. Qualquer mudança no tema Drupal quebra o parser sem aviso."

**2. Pessimista: Rafael Toledo, chief engineer, metódico e desconfiado de 'verde no painel'.**
"O estado 'satisfatório' é enganoso. O indicador mede páginas coletadas, não chamadas reais. O motor não extrai prazo nem valor, embora a página Apply traga os dois em texto claro. Também não deduplica: a página Apply é reescrita a cada ciclo na mesma URL, e sem chave composta (URL + janela) o sistema trata a R19 e a chamada de 2026 como o mesmo item. E a paginação de node/310 usa um `block_config_key` opaco, que pode mudar."

**3. Levemente pessimista: Camila Reis, staff engineer, pragmática.**
"Eu não jogaria fora: o volume é baixo (1 chamada por ano), então uma rota simples resolve. Mas a cadência precisa ser definida. A janela dura 28 a 30 dias e um rastreio semanal pode perder a primeira semana. Outro ponto é a aplicabilidade: as chamadas são em inglês ou francês e o valor mínimo é de US$ 100 mil, o que exige filtro de perfil. Senão o painel vai sugerir à associação uma chamada que ela dificilmente vence."

**4. Neutro: Prof. Dr. Otávio Mendonça, ex-CTO de big tech e professor de Computação, árbitro.** A síntese dele está no fim desta seção.

**5. Levemente otimista: Bruno Akira, staff engineer, focado em custo-benefício.**
"O site é limpo, estável, sem login, sem CAPTCHA e com robots permissivo. Três URLs fixas cobrem 100% do que importa. O custo de manutenção é quase zero e a confiabilidade do link oficial é máxima, porque o próprio financiador publica."

**6. Otimista: Dra. Lúcia Ferraz, professora de Computação (pós-doutorado em Python, PLN aplicado).**
"O ganho de previsão é real. Com o arquivo de notícias desde 2021 e o banco de projetos por rodada, o sistema consegue montar um calendário preditivo: anúncio em outubro, janela em novembro ou fevereiro, resultado em abril, início em setembro. Além disso, o banco mostra OSCs brasileiras financiadas (Delibera Brasil, Direitos Humanos em Rede), que viram referência para a proposta da associação."

**7. Extremamente otimista: Marcos Albuquerque, CTO de big tech, visionário.**
"É a porta de entrada internacional mais limpa do motor inteiro: até US$ 200 mil, a fundo perdido, por 2 anos, sem contrapartida obrigatória e sem restrição de país. Se o motor avisar a associação com 60 dias de antecedência, dá tempo de preparar uma proposta em inglês sobre participação cidadã ou juventude em Goiânia. Um único projeto aprovado vale mais que dezenas de editais municipais."

### Síntese do neutro (Prof. Dr. Otávio Mendonça)

**Decisão:** manter o motor, mas **reconfigurar já** (prioridade média). O estado no painel deve mudar de "satisfatório" para "satisfatório com rota a corrigir". Como é financiador internacional e de baixa frequência, o motor deve funcionar como **monitor de página com detecção de mudança**, e não como rastreador de listagem.

**Melhorias concretas:** ver a seção 7 (numeradas).

**Parâmetros de qualidade:**
- Q1. Cobertura: 100% das chamadas anuais detectadas em até 7 dias após a abertura (meta: até 2 dias).
- Q2. Precisão: pelo menos 90% dos itens gerados devem ser chamadas reais. Notícias de projetos e eventos devem ser descartadas (hoje a precisão é de 50%).
- Q3. Campos: inicio, prazo e valor preenchidos em 100% das chamadas detectadas, com url sempre no domínio `un.org/democracyfund`.
- Q4. Deduplicação: uma chamada por ciclo, com chave `site-undef|AAAA` (ano da janela) ou `site-undef|R<n>`.
- Q5. Estabilidade: alerta quando a página Apply ficar 18 meses sem mudança, ou quando o parser não encontrar o padrão de datas.

**Riscos e mitigação:**
- R1. Chamada abre sem notícia (como em 2025). Mitigação: monitorar a página Apply e a página "When to apply" por hash ou diff de texto, sem depender de node/310.
- R2. Janela curta (cerca de 28 dias) perdida por cadência semanal. Mitigação: cadência diária de outubro a março e semanal no resto do ano, com alerta imediato quando surgir "deadline" ou data futura.
- R3. Página Apply reaproveitada entre ciclos, causando sobrescrita ou duplicação. Mitigação: gravar um snapshot por ciclo e usar chave por ano ou rodada; ao detectar nova janela, a anterior vai para `encerrado_arquivar`.
- R4. Falso positivo vindo de notícias. Mitigação: léxico positivo obrigatório ("call for proposals", "annual call", "round of funding", "apply", "deadline") e léxico negativo ("round table", "handbook", "evaluation", "International Day").
- R5. Indicação de oportunidade pouco realista à associação (inglês, US$ 100 mil, temática democrática, cerca de 2% de aprovação). Mitigação: `aplicavel="depende"` fixo, com nota de requisitos (idioma, tema, porte) e prioridade de alerta "estratégica", não "urgente".
- R6. Mudança de tema Drupal ou de URL. Mitigação: testar a rota em cada execução; se receber 404 ou não encontrar datas, abrir pendência no painel.
- R7. Crawl-delay de 10 s no robots. Mitigação: no máximo 3 a 4 requisições por execução, com intervalo de pelo menos 10 s.

---

## 7. Melhorias do motor (lista numerada)

1. **Rota:** trocar `None` (home) por monitor de 3 URLs fixas: `/en/apply-for-funding` (principal), `/en/content/when-apply-and-who-can-apply` (aviso do ciclo) e `/node/310` (anúncios). O leitor passa de `html_listagem` para `pagina_unica + diff`.
2. **Extração:** analisar na página Apply as expressões "between DD Month and DD Month YYYY", "deadline" e "US$ ... to US$ ...", preenchendo inicio, prazo e valor automaticamente.
3. **Léxico:** positivo ("call for proposals", "annual call", "round of funding", "online proposal system", "deadline", "apply") e negativo ("round table", "handbook", "evaluation", "International Day", "story", nomes de países em título de notícia de projeto).
4. **Filtro:** descartar notícias de node/310 sem termo positivo no título. Isso elimina o falso positivo da CSW.
5. **Cadência:** diária de outubro a março, semanal de abril a setembro, sempre respeitando crawl-delay de 10 s.
6. **Histórico:** semear o arquivo com as rodadas R17 (nov/2022), R18 (nov/2023) e R19 (fev/2025), e consultar o banco `projects.undemocracyfund.org` uma vez por ano para registrar rodadas e projetos brasileiros como referência.
7. **Deduplicação:** usar a chave `site-undef|<ano da janela>`. A mesma URL Apply em ciclos diferentes gera livros distintos, e o anterior passa automaticamente para `encerrado_arquivar`.
8. **Link oficial:** usar sempre o domínio `www.un.org/democracyfund`. Na chamada aberta, apontar para `/en/apply-for-funding`. Nunca usar o OPPS como url, porque só existe durante a janela.
9. **Aplicabilidade:** fixar `aplicavel="depende"`, com nota padrão: "inglês/francês; US$ 100–200 mil; tema democracia/direitos; OSC legalmente constituída; preferência a países em transição".
10. **Painel:** substituir o indicador "achados" por "ciclo atual: aberto / anunciado sem data / fechado".

---

## 8. O que não foi confirmado e por quê

- **Datas da chamada de 2026 (provável Rodada 20):** o site só diz que os detalhes serão publicados. O número "20" não aparece em fonte oficial e não foi usado como fato.
- **Data de publicação da chamada R19 (2025):** não há notícia de abertura no arquivo, e a página Apply não traz data de publicação. Por isso publicado_em ficou "".
- **Resultado da Rodada 19 (nº de propostas e projetos):** não há notícia oficial. A URL deduzida retornou 404. O banco mostra só parte da lista (um projeto R19 visível).
- **Restrição formal de país ou renda:** o FAQ diz que não há restrição, apenas preferência. Não existe lista oficial de países elegíveis.
- **Busca externa:** o WebSearch está bloqueado (403 no proxy), então não houve verificação cruzada fora do domínio oficial. O curl direto também foi recusado pelo proxy.
- **Divergência no banco de projetos:** o rótulo de ano por rodada (ex.: "R18 (2023)") e as datas de início de alguns projetos não batem perfeitamente com a janela da chamada. Foram anotados como dados do banco, sem inferência.
- **Agregador:** não se aplica, porque o UNDEF é financiador direto. Não houve verificação por amostra de 10 links de indícios: o arquivo só tem 2, e ambos foram verificados.
