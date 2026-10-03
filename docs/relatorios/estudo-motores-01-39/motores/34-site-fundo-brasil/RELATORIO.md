# Motor 34 — site-fundo-brasil — Fundo Brasil de Direitos Humanos

Estudo de 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Foram usadas 34 chamadas de WebFetch. O `robots.txt` libera tudo (`User-agent: * / Disallow:`) e aponta `sitemap_index.xml`. Não houve login, CAPTCHA nem formulário. Nenhuma página trouxe texto com instruções dirigidas a uma IA.

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| `https://www.fundobrasil.org.br/wp-json/wp/v2/edital` (rota configurada) | Sim (JSON) | **Só 2 itens**: Raízes Amazônia/Cerrado (id 14398, 15/07/2026) e Justiça Criminal 2026 (id 13921, 11/05/2026). Traz `date`, `link` e título. O prazo e o valor aparecem apenas dentro do texto do conteúdo, não em campos próprios. |
| `.../wp/v2/edital?per_page=100&after=2023-10-01...` | Sim | Os mesmos 2 itens |
| `.../wp/v2/edital?slug=geral-2026-...,lgbtqia-...-2026,direitos-digitais-2026` | Sim | Os mesmos 2 itens: **o filtro `slug` foi ignorado**. A API parece expor só uma seleção fixa ou em destaque. |
| `https://www.fundobrasil.org.br/editais/` (página do titular) | Sim | 7 cartões por página, paginação "01/07", filtro Aberto/Encerrado e menção a "43 editais específicos". Mostra a data do resultado, mas não o prazo nem o valor. |
| `https://www.fundobrasil.org.br/sitemap_index.xml` | Sim | 8 sitemaps do Yoast |
| **`https://www.fundobrasil.org.br/edital-sitemap.xml`** | Sim | **85 URLs** do tipo `edital`, de 2008 a 2026, em PT e EN, com `lastmod`. É o arquivo completo. |

**Conclusão:** a rota configurada responde, mas está muito incompleta. Ela explica os "2 achados" do painel. Hoje ela já não devolve o Edital Geral 2026 nem o LGBTQIAPN+ 2026, que constam nas sementes. **A melhor rota verificada é `https://www.fundobrasil.org.br/edital-sitemap.xml`**: serve para descobrir os editais, e o `lastmod` mostra o que é novo ou foi alterado. Depois disso, o motor deve ler a página oficial de cada edital (`/edital/<slug>/`), onde estão de forma regular "Período de submissão", valor, elegibilidade e data do resultado. A API pode continuar como sinal rápido do edital em destaque. Atenção: muitos `lastmod` são de 07/11/2024, data de uma migração em massa, e não servem como data de publicação. URLs `/en/edital/` são traduções e devem ser descartadas.

Situação das 3 sementes (as 3 verificadas):
- Raízes Amazônia/Cerrado: o link abre. Prazo **21/08/2026**, que a semente não tinha. Encerrado.
- Geral 2026: o link abre. Prazo **06/03/2026**. Encerrado. Some da API.
- LGBTQIAPN+ 2026: o link abre. Prazo **06/02/2026**. Encerrado. Some da API.
- As três sementes estão com `prazo: null`. O motor não extrai o prazo do texto, e isso deixaria editais encerrados aparecendo como vigentes.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

O financiador é sempre o Fundo Brasil de Direitos Humanos. O site oficial é `https://www.fundobrasil.org.br/edital/<slug>/` (veja a URL de cada item em `livros.json`). Parceiros financeiros citados nas páginas: Laudes Foundation, Fundação Ford, Open Society Foundations, Porticus, Instituto Itaúsa, Forest People Climate, Fundação Grupo Volkswagen, Warner Music Group/Blavatnik Family Foundation e Oak Foundation.

| Data (início) | Título | Financiador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| 27/11/2023 | Comunidades Tradicionais Lutando por Justiça Climática | Fundo Brasil | /edital/edital-comunidades-tradicionais-lutando-por-justica-climatica/ | 31/01/2024 | encerrado_arquivar | depende |
| 10/12/2023 | Edital Geral 2024 – Vozes por Direitos e Justiça | Fundo Brasil | /edital/edital-geral-2024-vozes-por-direitos-e-justica-.../ | 29/02/2024 | encerrado_arquivar | sim |
| 15/12/2023 | Trabalhadores Informais na Luta por Direitos 2024 (Labora) | Fundo Brasil (+Laudes, Ford, OSF) | /edital/fortalecendo-trabalhadores-informais-na-luta-por-direitos-2024/ | 07/02/2024 | encerrado_arquivar | depende |
| 02/02/2024 | Enfrentando o Racismo a partir da Base 2024 | Fundo Brasil (+WMG/Blavatnik, Ford) | /edital/edital-enfrentando-o-racismo-a-partir-da-base-2024/ | 25/03/2024 | encerrado_arquivar | depende |
| 13/03/2024 | Povos Indígenas Lutando por Justiça Climática | Fundo Brasil (+Itaúsa) | /edital/edital-povos-indigenas-lutando-por-justica-climatica/ | 07/05/2024 | encerrado_arquivar | não |
| 03/04/2024 | Incidência Popular em Segurança Pública | Fundo Brasil (+OSF) | /edital/incidencia-popular-e-seguranca-publica/ | 17/06/2024 | encerrado_arquivar | depende |
| 02/05/2024 | Porta de Saída 2024 – Egressos do Sistema Prisional | Fundo Brasil (+Porticus) | /edital/porta-de-saida-2024-.../ | 24/06/2024 | encerrado_arquivar | depende |
| 04/07/2024 | Transição Justa e Trabalho Digno (Labora) | Fundo Brasil (+Laudes, Ford, OSF) | /edital/transicao-justa-e-trabalho-digno-.../ | 30/08/2024 | encerrado_arquivar | depende |
| 26/07/2024 | Direitos Humanos na Bacia do Rio Doce | Fundo Brasil | /edital/promocao-e-defesa-de-direitos-humanos-na-bacia-do-rio-doce/ | 09/09/2024 | encerrado_arquivar | não (só MG/ES) |
| 13/12/2024 | Edital Geral 2025 – Democracia e Direitos | Fundo Brasil | /edital/democracia-e-direitos-construindo-o-futuro-com-justica-e-igualdade/ | 10/03/2025 | encerrado_arquivar | sim |
| 13/12/2024 | Raízes: Comunidades Tradicionais, Quilombolas e Povos Indígenas | Fundo Brasil | /edital/raizes-comunidades-tradicionais-quilombolas-.../ | 11/02/2025 | encerrado_arquivar | depende |
| 17/12/2024 | Trabalhadores Informais 2025 (Labora) | Fundo Brasil (+Laudes, Ford, OSF) | /edital/fortalecendo-trabalhadores-informais-na-luta-por-direitos-2025/ | 07/02/2025 | encerrado_arquivar | depende |
| 19/03/2025 | Fortalecendo Soluções… Justiça Climática e Transição Justa | Fundo Brasil (+Laudes, Ford, OSF, Fund. VW) | /edital/fortalecendo-solucoes-de-povos-indigenas-.../ | 25/04/2025 | encerrado_arquivar | depende |
| 15/05/2025 | Enfrentando o Racismo a partir da Base 2025 | Fundo Brasil | /edital/enfrentando-o-racismo-a-partir-da-base-2025/ | 27/06/2025 | encerrado_arquivar | depende |
| 11/06/2025 | Direitos Humanos na Bacia do Rio Doce 2025 | Fundo Brasil | /edital/promocao-e-defesa-de-direitos-humanos-na-bacia-do-rio-doce-2025/ | 22/07/2025 | encerrado_arquivar | não (só MG/ES) |
| 06/08/2025 | Segurança Integral de Defensoras/es de DH | Fundo Brasil (+Ford, Porticus) | /edital/seguranca-integral-de-defensoras-es-.../ | 01/09/2025 | encerrado_arquivar | depende |
| 06/12/2025 | Edital Geral 2026 – Fortalecendo Direitos e Gestando um Mundo Novo | Fundo Brasil | /edital/geral-2026-fortalecendo-direitos-e-gestando-um-mundo-novo/ | 06/03/2026 | encerrado_arquivar | sim |
| 06/12/2025 | LGBTQIAPN+: Defendendo Direitos 2026 | Fundo Brasil | /edital/lgbtqia-defendendo-direitos-2026/ | 06/02/2026 | encerrado_arquivar | depende |
| 17/12/2025 | Trabalhadores Informais 2026 (Labora) | Fundo Brasil (+Laudes, Ford, OSF) | /edital/edital-fortalecendo-trabalhadores-informais-na-luta-por-direitos-2026/ | 09/02/2026 | encerrado_arquivar | depende |
| 16/03/2026 | Soluções Climáticas a partir da Base | Fundo Brasil (+Laudes, Ford, OSF) | /edital/solucoes-climaticas-a-partir-da-base/ | 08/05/2026 | encerrado_arquivar | depende |
| 06/04/2026 | Direitos Digitais 2026 | Fundo Brasil | /edital/direitos-digitais-2026/ | 19/05/2026 | encerrado_arquivar | depende |
| 11/05/2026 | DH e Justiça Criminal 2026 – Estado de Coisas Inconstitucional | Fundo Brasil | /edital/direitos-humanos-e-justica-criminal-2026-.../ | 26/06/2026 | encerrado_arquivar | depende |
| 15/07/2026 | Raízes: Amazônia e Cerrado | Fundo Brasil (+FPC, Itaúsa) | /edital/raizes-fortalecendo-direitos-autonomia-e-sustentabilidade-na-amazonia-e-no-cerrado/ | 21/08/2026 | encerrado_arquivar | depende (Eixo Cerrado inclui GO, só povos e comunidades tradicionais) |
| — | Apoio Emergencial Defensores de Direitos Humanos | Fundo Brasil | /edital/apoio-emergencial-defensores-de-direitos-humanos/ | fluxo contínuo | sem_data | depende |

**Totais: 24 oportunidades, sendo 0 abertas, 23 encerradas e 1 sem data.** Ficaram fora da janela de 3 anos, porque abriram e fecharam antes de 02/10/2023: LGBTQIA+ 2023 (prazo 12/05/2023), Justiça Criminal – Tortura (06/09/2023), Defensoras/es – Desenvolvimento Institucional (29/09/2023) e Trabalhadores Informais 2023 (03/02/2023).

Critério de aplicabilidade, pensando na A.M.C. Jardim América, uma OSC de bairro em Goiânia:
- **sim**: os editais gerais, que aceitam qualquer OSC de direitos humanos do Brasil.
- **depende**: os editais temáticos, que exigem público ou liderança específicos (pessoas negras, LGBTQIAPN+, trabalhadores informais, povos e comunidades tradicionais, egressos etc.).
- **não**: os editais restritos a MG/ES ou só a organizações indígenas.

## 3. Onde publica

- **Site oficial**: cada edital ganha sua própria página em `fundobrasil.org.br/edital/<slug>/`, com o texto completo (período, valores, eixos, elegibilidade, calendário). A vitrine fica em `/editais/`, com filtro Aberto/Encerrado e paginação.
- **Inscrição**: no **Portal de Projetos próprio** (`https://fundobrasil.powerappsportals.com/`, sistema Microsoft Power Pages), com cadastro e login. Os editais Raízes, indígenas e de comunidades tradicionais e o Rio Doce 2024 aceitaram também **e-mail ou WhatsApp**. Não usa Prosas, Mapas Culturais nem Transferegov.
- **Descoberta por máquina**: `edital-sitemap.xml` (completo) e a API WordPress `/wp-json/wp/v2/edital` (parcial). Há versão em inglês em `/en/edital/`.

## 4. Tipos de oportunidade

- **Edital de projeto / apoio institucional** (praticamente todos): doação não reembolsável para fortalecimento institucional e projetos de 12 a 18 meses.
- **Fluxo contínuo**: Apoio Emergencial a defensores de direitos humanos (aceita também pessoa física).
- Não há prêmio, bolsa individual, fundo rotativo nem chamada de cadastro. O dinheiro tem origem internacional (Ford, OSF, Laudes, Oak, Porticus), mas a chamada é nacional e em português.
- **Áreas**: direitos humanos em geral, combate ao racismo, LGBTQIAPN+, trabalho informal e transição justa (programa Labora), justiça climática para povos e comunidades tradicionais (programa Raízes), justiça criminal e egressos, segurança pública, defensores de direitos humanos, direitos digitais e Bacia do Rio Doce.
- **Faixas de valor**: de R$ 40 mil a R$ 160 mil por proposta. O padrão é R$ 50 mil (até R$ 60 mil em 2025-26), e os eixos maiores ficam entre R$ 100 mil e R$ 160 mil. Cada edital soma de R$ 0,8 mi a R$ 2,65 mi, com 10 a 43 apoios.
- **Quem pode**: grupos, coletivos, movimentos, sindicatos e OSCs sem fins lucrativos, **com ou sem CNPJ**. Quem não tem CNPJ precisa de uma parceira fiscal. Alguns eixos exigem CNPJ. Ficam de fora pessoa física (exceto no emergencial), governo, universidade, ONG internacional, partido e empresa.

## 5. Calendário

Os lançamentos seguem um padrão que se repete:
- **Dezembro**: um pacote anual com Edital Geral, Labora (trabalhadores informais), LGBTQIAPN+ e, em 2024, Raízes. As inscrições fecham entre fevereiro e março.
- **Março e abril**: clima e Raízes/Labora; segurança pública; direitos digitais.
- **Maio e junho**: Racismo, Porta de Saída e Justiça Criminal; Rio Doce (junho e julho).
- **Julho e agosto**: Transição Justa, Rio Doce, Defensoras/es e Raízes Amazônia/Cerrado.
- **Duração das inscrições**: de 4 a 13 semanas, sempre com fechamento às 18h (horário de Brasília). O resultado sai de 2 a 4 meses depois.
- **Próxima janela provável para a A.M.C.**: o **Edital Geral 2027**, por volta de **início de dezembro de 2026**. É uma previsão baseada nos 3 anos anteriores (10/12/2023, 13/12/2024 e 06/12/2025), não um fato confirmado.

## 6. Conselho de 7 lentes

1. **Extremamente pessimista — Dr. Heitor Brandão (staff engineer, cético por ofício):** "O motor está cego. A rota devolve 2 de 24 editais do período, e o painel o chama de 'satisfatório'. Isso é um falso verde. Os 2 itens que ele guardou hoje já fecharam. As sementes estão com `prazo: null`, então para o sistema três editais encerrados continuam 'vigentes'. Quando um edital some da API, o motor não percebe."
2. **Pessimista — Profa. Lúcia Feitosa (pós-doutora em Python, rigor de dados):** "O texto que vira 'resumo' é a descrição de imagem ('PARA TODOS VEREM'), não o edital. Prazo e valor vivem no corpo do HTML ('Período de submissão: de X a Y'), e o motor não usa regex para extraí-los. A `publicado` vem com fuso UTC (05/12 contra 06/12 na página). As URLs `/en/` causariam duplicidade."
3. **Levemente pessimista — Eng. Rafael Quintana (chief engineer, pragmático):** "Um site que publica cerca de 8 editais por ano, todos com a mesma estrutura, é fácil de ler, e mesmo assim lemos pelo canal errado. Falta usar o `lastmod` do sitemap como gatilho e um parser de página. Nada disso é complexo."
4. **Neutro — Dra. Beatriz Sampaio (CTO de big tech, árbitra):** a síntese está abaixo.
5. **Levemente otimista — Prof. Daniel Okafor (pós-doutor em Python, didático):** "O site é bem-comportado: robots.txt aberto, Yoast, slugs estáveis e um texto padronizado ('Período de submissão', 'Valor máximo', 'Divulgação de resultados'). Um extrator de 30 linhas cobre tudo."
6. **Otimista — Eng. Marina Takahashi (staff engineer, foco em produto):** "Há três ciclos completos de histórico, com calendário previsível. Isso permite avisar a A.M.C. em novembro para preparar a proposta do Edital Geral de dezembro, que é o único 'sim' recorrente: R$ 40 a 50 mil, sem exigência complexa."
7. **Extremamente otimista — Dr. Augusto Mendonça (CTO, visionário):** "O Fundo Brasil é uma porta de entrada para Ford, OSF, Laudes, Porticus e Oak. Mapear esses parceiros a partir das páginas abre novos motores de financiadores internacionais. Com previsão por sazonalidade, o motor deixa de reagir e passa a antecipar."

**Síntese do neutro (Dra. Beatriz Sampaio):**
- **Decisão**: **manter o motor, mas reclassificá-lo de "satisfatório" para "parcial"**. A rota principal passa a ser o `edital-sitemap.xml` mais a leitura de cada página oficial. A API fica só como sinal secundário. Arquivar os 23 encerrados como histórico. Criar um alerta de previsão para o Edital Geral 2027 em novembro de 2026.
- **Melhorias**: estão na seção 7.
- **Parâmetros de qualidade**:
  - cobertura de pelo menos 95% dos slugs PT do sitemap no período;
  - prazo extraído em pelo menos 90% dos itens;
  - 0 itens com prazo vencido marcados como abertos;
  - 0 duplicados PT/EN;
  - atraso de detecção de no máximo 7 dias após o `lastmod`;
  - `url` sempre em `fundobrasil.org.br/edital/`.
- **Riscos e mitigação**:
  - (a) o sitemap pode mudar de nome ou o Yoast pode ser removido: ler primeiro o `sitemap_index.xml` e usar a vitrine `/editais/?status=aberto` como alternativa;
  - (b) a redação do "Período de submissão" pode variar: aplicar vários padrões de regex e, se nenhum casar, marcar `prazo=""` e `sem_data` para revisão humana;
  - (c) `lastmod` em massa (como a migração de 07/11/2024): ignorar `lastmod` como data de publicação e usar a data de início da página;
  - (d) muitos editais exigem público específico, o que gera falso "sim": manter "depende" por padrão e dar "sim" apenas aos editais gerais;
  - (e) o portal de inscrição exige login: o motor não entra nele e só lê páginas públicas.

## 7. Melhorias do motor (lista numerada)

1. **Rota**: trocar a rota principal para `https://www.fundobrasil.org.br/edital-sitemap.xml` (descoberta e `lastmod`) e manter `/wp-json/wp/v2/edital` só como sinal de destaque.
2. **Histórico**: fazer a carga inicial a partir do sitemap, filtrando os slugs PT com data de início a partir de 02/10/2023 (os 23 editais mais o emergencial deste relatório).
3. **Extração de prazo, início e valor**: aplicar regex sobre o texto da página oficial: "Período de submissão/inscrição: de DD de mês (de AAAA) a DD de mês de AAAA"; "Valor máximo… R$"; "Valor total… R$"; "Divulgação de resultados".
4. **Filtro de estado**: se `prazo < hoje`, marcar `encerrado_arquivar`. Também reconhecer o texto "INSCRIÇÕES ENCERRADAS" na página e o filtro Aberto/Encerrado da vitrine.
5. **Léxico de aplicabilidade**: "Edital Geral" leva a "sim"; "Rio Doce" ou "Barragem de Fundão" levam a "não" (MG/ES); "povos indígenas", "quilombolas", "liderados por", "egressas", "trabalhadores informais" e "LGBTQIAPN+" levam a "depende"; "Cerrado" deve ser marcado como incluindo GO.
6. **Deduplicação**: descartar `/en/edital/`; usar o slug como chave; tratar o sufixo `-2` como possível duplicado.
7. **Link oficial**: `url` = `link` da página do edital; `pagina_agregador` = "" (o site é o próprio financiador).
8. **Resumo**: descartar parágrafos que começam com "PARA TODOS VEREM" / "PRA TODOS VEREM" (descrição de imagem) e usar o bloco "APRESENTAÇÃO".
9. **Cadência**: semanal no ano todo e diária de 25/11 a 20/12, que é a janela do pacote anual (Edital Geral, Labora, LGBTQIAPN+).
10. **Painel**: um motor que devolve menos itens que o sitemap no período deve mostrar estado "parcial", não "satisfatório".
11. **Parceiros**: registrar os cofinanciadores citados (Ford, OSF, Laudes, Porticus, Oak, Itaúsa, FPC, Fundação VW) como pistas para outros motores.

## 8. O que não foi confirmado e por quê

- **Por que a API devolve só 2 itens**: o comportamento foi observado (filtros `after` e `slug` ignorados), mas a causa (plugin, cache ou consulta personalizada) não pôde ser verificada sem acesso ao servidor.
- **Data exata de publicação** do Edital Geral 2024 (a página só diz "dezembro de 2023"; o início das inscrições foi 10/12/2023) e do LGBTQIAPN+ 2026 (a página mostra a data de atualização, 06/02/2026). Nesses casos, `publicado_em` ficou "". As sementes trazem 2025-12-05 para o Geral 2026 e o LGBTQIAPN+ 2026, enquanto as páginas indicam lançamento em 06/12/2025, uma provável diferença de fuso UTC.
- **Elegibilidade detalhada** do Justiça Criminal 2026: lida apenas pelo resumo da API (Eixo 1, organizações com capacidade técnica; Eixo 2, organizações lideradas por egressos).
- **Valor e forma de solicitação** do Apoio Emergencial: a página não informa e remete a um "Saiba mais", que não foi aberto.
- **Valor total** do Racismo 2024 e do Porta de Saída 2024: a página informa só o valor por proposta e a quantidade de apoios.
- **Vitrine `/editais/`**: só a página 1 de 7 foi lida. O sitemap substituiu as demais. O número "43 editais específicos" não foi conferido item a item.
- As datas de lançamento foram extraídas por WebFetch, que resume a página com um modelo. Os valores foram conferidos de forma coerente entre as páginas, mas não houve leitura do PDF de cada edital.
