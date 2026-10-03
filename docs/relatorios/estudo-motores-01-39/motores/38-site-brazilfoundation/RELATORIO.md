# Motor 38 — site-brazilfoundation (BrazilFoundation)

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Janela do histórico: 02/10/2023 a 02/10/2026. Usei 24 chamadas de WebFetch. A busca na web (WebSearch) está bloqueada nesta organização e o curl direto foi recusado pelo proxy, então todo o acesso passou pelo WebFetch.

## 1. Rota (teste e conclusão)

| Teste | URL exata | Resultado |
|---|---|---|
| Rota configurada | `None` (leitor html_listagem) | Não existe rota. O motor não tem o que ler, e por isso marca "ativo, sem achados". |
| Página pública | https://brazilfoundation.org/edital/ | Responde (200). Mostra 4 cartões, todos dos editais de 2023: Empreendedorismo Negro, Equidade de Gênero, Meio Ambiente & Mudanças Climáticas e Educação. Não traz data, prazo, valor nem plataforma. Os links de dois cartões usam o domínio antigo `novo.brazilfoundation.org`, que redireciona (302) para `brazilfoundation.org`. |
| robots.txt | https://brazilfoundation.org/robots.txt | Responde 404, ou seja, não há restrição publicada. |
| Sitemap | https://brazilfoundation.org/sitemap_index.xml | Responde 404. |
| API WordPress, busca | https://brazilfoundation.org/wp-json/wp/v2/search?search=edital&per_page=100 | Responde com JSON. Devolve posts e páginas de editais de 2016 a 2023. |
| API WordPress, posts com filtro de data | https://brazilfoundation.org/wp-json/wp/v2/posts?after=2023-10-01T00:00:00&per_page=100&_fields=date,title,link | Responde e aceita os filtros `after`, `before` e `search`. Traz data, título e link. |
| API WordPress, páginas | https://brazilfoundation.org/wp-json/wp/v2/pages?after=2023-10-01T00:00:00&per_page=100&_fields=date,modified,title,link | Responde. As páginas novas são fundos de doadores (Kobra, Baccarelli, PUC-Rio), não chamadas. |

**Conclusão:** a página /edital/ é uma vitrine parada desde 2023 e não serve como fonte única. A melhor rota verificada é a **API REST do WordPress**:

- Principal: `https://brazilfoundation.org/wp-json/wp/v2/posts?search=edital&after=<última_execução>&per_page=100&_fields=date,modified,title,link`
- Complementares: as mesmas consultas com `search=selecionadas`, `search=chamada` e `search=convite`. Elas pegam os anúncios de seleção, que hoje são a única marca dos ciclos.

A API entrega a data de publicação e o link oficial. O prazo e o valor só aparecem no corpo do post: dá para pedir `content` na própria API ou abrir o link.

## 2. Histórico de 3 anos

O que se constatou: **na janela de 02/10/2023 a 02/10/2026 a BrazilFoundation não publicou nenhum edital público novo.** Para chegar a isso, li a lista completa de posts do período, dividida em quatro faixas de datas, e fiz buscas por "edital", "chamada" e "convite". Dentro da janela só há dois marcos do ciclo de seleção:

- **20/12/2023:** resultado dos editais de 2023 de Educação e de Meio Ambiente. Foram 342 propostas e 16 selecionadas, 8 por fundo. Nenhuma das selecionadas é de Goiás.
- **18/07/2026:** anúncio das selecionadas de 2026, por **carta-convite** e não por chamada pública, nos fundos de Meio Ambiente e de Equidade de Gênero. Na lista há uma entidade de GO: Associação de Coletores de Sementes da Chapada dos Veadeiros – Cerrado de Pé, de Alto Paraíso.

Entre 2024 e 2025 só houve posts institucionais (galas, Financial Times Summit, COP30, reconstrução do RS, Donor Advised Fund) e nenhum edital. O post sobre o RS não descreve nenhuma chamada.

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2023-07-14 (resultado em 2023-12-20) | Edital Fundo de Educação (2023) | BrazilFoundation | https://brazilfoundation.org/edital-2023-fundo-de-educacao/ | 2023-08-18 | encerrado_arquivar | sim |
| 2023-07-14 (resultado em 2023-12-20) | Edital 2023 — Fundo de Meio Ambiente & Mudanças Climáticas | BrazilFoundation | https://brazilfoundation.org/edital-2023-fundo-do-meio-ambiente-mudancas-climaticas/ | 2023-08-18 | encerrado_arquivar | sim |
| 2026-07-18 | Seleção 2026 por carta-convite (Meio Ambiente; Equidade de Gênero) | BrazilFoundation | https://brazilfoundation.org/brazilfoundation-anuncia-selecionadas-2026/ | "" | encerrado_arquivar | depende (só convidadas) |

Antecedentes de fora da janela, que entram para a série histórica e para a previsão:

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2022-12-21 | Edital 2023 — Fundo de Equidade de Gênero | BrazilFoundation | https://brazilfoundation.org/edital-2023-fundo-de-equidade-de-genero/ | 2023-01-30 | encerrado_arquivar | depende (OSC de mulheres ou LGBTQIA+) |
| 2022-12-21 | Edital 2023 — Fundo de Empreendedorismo Negro | BrazilFoundation | https://brazilfoundation.org/edital-2023-fundo-de-empreendedorismo-negro/ | "" | encerrado_arquivar | depende (aceleradoras de negócios negros) |

Mais para trás, a busca mostra editais anuais de 2016 a 2021 e chamadas regionais em 2019, com a Fundação Renova, no leste de MG, em Baixo Guandu/ES e em Brumadinho. Ficam como contexto e não entram nos livros.

**Indício do sistema:** há 1 só, "Editais", com link https://brazilfoundation.org/edital/. O link abre e é do próprio financiador, mas aponta para a vitrine e não para uma oportunidade. A data guardada, 2023-07-20, vem da página. Entrou nos livros como `aguardar_fonte` / `sem_data`, com "fonte": "verificado".

## 3. Onde publica

- **Site oficial:** brazilfoundation.org, em português e com espelho em inglês em /en/. Os editais saem como posts do blog, e a página /edital/ só reúne os cartões.
- **Inscrição:** formulário próprio no Microsoft Forms (forms.office.com), ligado ao post do edital. Não aceita inscrição por e-mail. Não usa Prosas, Mapas Culturais nem Transferegov.
- **Resultados e prorrogações:** também saem como posts, com títulos como "anuncia as organizações selecionadas", "prorrogado prazo" e "nova data de divulgação".
- **A partir de 2026, carta-convite:** a fundação faz um mapeamento estratégico e convida as organizações. Não há inscrição aberta, e o único sinal público é o post com as selecionadas. As páginas "Como apoiamos" e "saiba-mais/edital" dizem expressamente que o ingresso é por "Carta convite ou Edital".

## 4. Tipos de oportunidade

- **Edital de projeto** de apoio institucional e programático: R$ 150 mil por 12 meses, renovável por mais 12, com mentoria, monitoramento semestral e fortalecimento institucional. Foram os 4 fundos temáticos de 2023.
- **Carta-convite** em 2026: mesmo valor (até R$ 150 mil por ano, renovável) e mesmos fundos.
- **Chamadas regionais com parceiro**, como as de 2019 com a Fundação Renova em MG e ES. Hoje são só histórico.
- **Não aparecem:** prêmio, bolsa, fundo rotativo nem chamada internacional para OSC. Os "Fundos" de doadores (Kobra, Baccarelli, PUC-Rio, IMEC, Instituto Caldeira, DAF) são veículos de doação dos EUA para o Brasil, e não chamadas abertas.
- **Áreas:** os quatro fundos temáticos (Educação, Meio Ambiente & Mudanças Climáticas, Equidade de Gênero e Empreendedorismo Negro).
- **Quem pode:** OSCs brasileiras formalizadas. Ficam de fora partidos, instituições religiosas, sindicatos, universidades, escolas, hospitais e o Sistema S.
- **Faixa de valor:** R$ 150 mil por ano por organização. Em 2025 a fundação informa ter investido R$ 45 milhões no total.

## 5. Calendário

| Ciclo | Abertura | Prazo | Resultado |
|---|---|---|---|
| Edital 2023, 1ª leva (Equidade de Gênero; Empreendedorismo Negro) | dezembro de 2022 | 30/01/2023 | 07/06/2023 (previsto para abril, adiado) |
| Edital 2023, 2ª leva (Educação; Meio Ambiente) | julho de 2023 | 18/08/2023 | 20/12/2023 (previsto para início de dezembro, prorrogado) |
| 2024–2025 | não houve edital público | — | — |
| Seleção 2026 | carta-convite, sem data pública | — | 18/07/2026 |

Quando havia edital público, as aberturas caíam em **dezembro e julho**, as inscrições duravam cerca de 30 a 40 dias e o resultado saía 4 a 5 meses depois, quase sempre com atraso. Um ciclo novo, se vier, deve se anunciar por post entre junho e julho ou entre novembro e dezembro.

## 6. Conselho de 7 lentes

- **Extremamente pessimista — Dra. Helena Vasconcelos, chief engineer, rabugenta e precisa.** "Rota `None` com leitor html_listagem é um motor que finge funcionar. O painel diz 'ativo', mas ele não lê nada. Pior: a fonte deixou de publicar edital público desde 2023 e passou para carta-convite. Mesmo consertado, o motor pode passar anos sem achar nada aplicável. O 'ativo, sem achados' esconde uma falha de rota atrás de uma ausência real de oferta."
- **Pessimista — Prof. Ricardo Okamoto, pós-doutor em Python, metódico.** "A vitrine /edital/ está congelada, com links para um subdomínio antigo que redireciona por 302. Um raspador de HTML que dependa dos cartões vai repetir os mesmos 4 editais encerrados para sempre. Também não há sitemap, e o robots responde 404, de modo que não se pode confiar em descoberta passiva."
- **Levemente pessimista — Marcos Teixeira, staff engineer, pragmático.** "Os posts saem em duplicata, em PT e em /en/, com o mesmo conteúdo. Sem deduplicar por título normalizado ou por par de tradução, o motor conta tudo em dobro. E o prazo vem só no corpo do texto, em português corrido ('17 de julho a 18 de agosto'), o que pede um parser de datas por extenso."
- **Neutro — Dr. Augusto Lemos, professor de computação, árbitro sereno.** A síntese está mais abaixo.
- **Levemente otimista — Carla Moura, staff engineer, construtiva.** "A API WordPress está aberta, aceita `after`, `before` e `search` e devolve JSON leve com `_fields`. É barata, estável e dispensa raspagem de HTML. Uma chamada por semana resolve."
- **Otimista — Prof.ª Beatriz Salgado, pós-doutora em Python, entusiasta de dados.** "O padrão é muito regular: R$ 150 mil, 12 meses mais 12, quatro fundos fixos, abertura em julho ou dezembro, Microsoft Forms. Isso permite prever ciclos e montar uma ficha pronta. E o Fundo de Meio Ambiente cita o Cerrado de forma expressa: a seleção de 2026 já trouxe uma OSC goiana."
- **Extremamente otimista — Rafael Antunes, CTO de big tech, visionário.** "O ganho ideal é tratar a BrazilFoundation como sinal de relacionamento, e não só de edital. Os posts de 'selecionadas' mostram quem a fundação mapeia. Se a associação ficar visível no mapeamento (Cerrado, gênero, educação pública), pode ser convidada. Cada anúncio de seleção vira alerta estratégico, e cada edital público que reaparecer é capturado no mesmo dia."

### Síntese do neutro (Dr. Augusto Lemos)

**Decisão:** manter o motor, mas **trocar a rota e reclassificá-lo como baixa cadência e alto valor**. A rota `None`/html_listagem sai e entra a API REST do WordPress. O estado no painel passa a ser "ativo — fonte sem edital público desde 2023 (carta-convite em 2026)", para não mascarar falha.

**Melhorias:** estão na seção 7.

**Parâmetros de qualidade:**
- A rota responde 200 com JSON válido em pelo menos 95% das execuções.
- Zero duplicatas PT/EN nos livros.
- 100% dos livros com `url` em brazilfoundation.org.
- Prazo extraído em pelo menos 90% dos posts de edital.
- Alerta em até 7 dias depois da publicação de um edital ou de um anúncio de selecionadas.
- Nenhum edital de 2023 marcado como aberto.

**Riscos e mitigação:**
1. *A API REST ser desligada ou bloqueada:* manter como reserva a leitura de /edital/ e de `/feed/` (RSS padrão do WordPress, não testado) e alertar quando houver 3 falhas seguidas.
2. *Ciclos só por convite, sem edital público:* registrar os anúncios de selecionadas como sinal (`tipo: outro`, aplicável "depende") e levar à coordenação a tarefa de relacionamento (mapeamento e visibilidade).
3. *Falso positivo com edital antigo:* aceitar só posts com `date` posterior à última execução e prazo igual ou posterior a hoje para marcar ABERTA.
4. *Parser de datas por extenso falhar:* quando não houver prazo, gravar `prazo` "" e `estado` "sem_data", sem inventar, e mandar para revisão manual.
5. *Mudança de domínio ou subdomínio (como o `novo.`):* normalizar o host e seguir o redirecionamento 302 antes de deduplicar.

## 7. Melhorias do motor

1. **Rota:** trocar `None`/html_listagem por `https://brazilfoundation.org/wp-json/wp/v2/posts?search=edital&after=<última_execução>&per_page=100&_fields=date,modified,title,link,content`, com segunda consulta para `search=selecionadas` e terceira para `search=chamada`.
2. **Léxico:** entram "edital", "chamada de projetos", "inscrições", "carta-convite", "selecionadas", "Fundo de Educação", "Fundo de Meio Ambiente", "Fundo de Equidade de Gênero" e "Fundo de Empreendedorismo Negro". Ficam de fora "Gala", "Summit", "Donor Advised Fund", "vaga" e as páginas de fundos de doadores (Kobra, Baccarelli, PUC-Rio).
3. **Filtro:** descartar o caminho `/en/`, que é o espelho em inglês. Para marcar ABERTA, exigir prazo extraído igual ou posterior à data da execução. Posts de "selecionadas" e "resultado" viram `encerrado_arquivar` ou sinal de convite.
4. **Cadência:** semanal. Pode ser quinzenal fora de junho–julho e novembro–dezembro, mas o mais simples é manter semanal, já que custa uma única chamada.
5. **Histórico:** fazer uma carga única com `search=edital` e `search=chamada`, sem `after`, para ter a série 2016–2026 (anuais, Brumadinho e Renova) e servir de base de previsão.
6. **Deduplicação:** usar uma chave formada por host normalizado (`novo.` passa a `brazilfoundation.org`), slug sem `/en/` e título normalizado. Agrupar os posts de edital, prorrogação e resultado do mesmo ciclo num único livro.
7. **Link oficial:** usar sempre o `link` do post no domínio brazilfoundation.org e guardar a URL do Microsoft Forms só como campo de inscrição. Nunca usar como `url` o espelho em inglês ou o subdomínio antigo.
8. **Painel:** substituir "ativo, sem achados" por um estado explícito de fonte ("sem edital público desde 2023") e por um alerta de falha de rota separado.

## 8. O que não foi confirmado e por quê

- **Prazo e valor do Edital 2023 do Fundo de Empreendedorismo Negro:** não abri a página do edital, para economizar chamadas. A data de 21/12/2022 vem da API. Esses campos ficaram "".
- **Datas do ciclo de convite de 2026** (convite, prazo, número de convidadas): o anúncio não informa.
- **Feed RSS (`/feed/`):** não testei, e fica como hipótese de rota reserva.
- **Existência de editais 2024–2025 fora do blog:** não pude confirmar por busca externa, porque o WebSearch está bloqueado na organização. A API não mostra nenhum.
- **robots.txt:** responde 404, então não há restrição publicada. Respeitei o uso moderado, com 24 chamadas.
- **Instruções dirigidas à IA:** não encontrei nenhuma nas páginas lidas.
- **Dados pessoais:** não registrei. Citei só entidades.
