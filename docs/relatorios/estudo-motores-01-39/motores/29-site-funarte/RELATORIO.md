# Motor 29 — site-funarte (Funarte, Fundação Nacional de Artes)

Data do estudo: 02/10/2026. Tipo de site: FINANCIADOR (publica os próprios editais). Chamadas de WebFetch usadas: 39 (limite de cerca de 40). O `curl` direto para www.gov.br foi recusado pelo proxy de saída, por isso todas as leituras foram feitas por WebFetch.

robots.txt de www.gov.br: não há regra Disallow para `/funarte`. O padrão declarado permite acesso a tudo o que é público. Não houve login, CAPTCHA nem formulário. Não encontrei nenhuma instrução dirigida a IA nas páginas lidas.

---

## 1. Rota (teste e conclusão)

| URL testada | Resposta | O que entrega |
|---|---|---|
| Rota configurada: `None` (html_listagem) | — | Não há rota própria. O motor depende da página pública. |
| https://www.gov.br/funarte/pt-br/editais/editais-abertos | 200 | 4 itens: Funarte Aberta, Ibermúsicas 2026, Quadrienal de Praga PQ 2027 (link externo cenografiasdoavesso.com) e Laç(z)os CPLP. A listagem só tem título e link: não traz data, prazo nem valor. Os links usam o caminho `/editais-abertos/<slug>`. |
| https://www.gov.br/funarte/pt-br/editais/2026 | 200 | 5 itens (só título e link) |
| https://www.gov.br/funarte/pt-br/editais/2025 | 200 | 10 itens |
| https://www.gov.br/funarte/pt-br/editais/2024 | 200 | 9 itens |
| https://www.gov.br/funarte/pt-br/editais/2023 | 200 | 23 itens |
| https://www.gov.br/funarte/pt-br/editais/2025/RSS | 404 | Não existe feed RSS por pasta |
| https://www.gov.br/funarte/pt-br/@@search?path=/funarte/pt-br/editais&sort_on=created... | 200, mas vazia | O resultado é montado por JavaScript. Não serve ao leitor HTML. |
| https://www.gov.br/funarte/pt-br/editais/editais-em-andamento | 404 | O link aparece no menu, mas o slug deduzido não existe |
| Páginas de detalhe `/editais/AAAA/<slug>` | 200 (2 exceções) | Trazem "Publicado em dd/mm/aaaa", "Atualizado em", período de inscrição com ano, valores, quem pode participar e o link do Prosas. Exceções: `laczos-artisticos-...` respondeu **403** (nos dois caminhos testados) e `premio-ibero-americano-de-danca` respondeu **302 para linktr.ee/plataforma_pid**. |

As páginas por ano não têm paginação: em todas, a lista inteira cabe numa página só.

**Conclusão.** A página `editais-abertos` serve para saber o que está aberto, mas não basta. A rota melhor verificada é a combinação abaixo:
1. `editais-abertos`, para marcar o que está aberto;
2. as pastas de ano `https://www.gov.br/funarte/pt-br/editais/{2026,2025,2024,2023}`, para o histórico completo;
3. a leitura obrigatória de cada página de detalhe, de onde saem as datas e os valores. Nas páginas que são "programa-mãe" (Ações Continuadas, Difusão Nacional, Conexões Internacionais, Ibercena, Funarte Aberta), é preciso descer um nível até as subpáginas.

---

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

Para descobrir o histórico, usei as pastas por ano (`/editais/2023` a `/editais/2026`). Há também um link "Editais Anteriores" para 2021–2022, fora do período.

**A. Oportunidades do período com detalhe confirmado na página oficial**

| Data (publicado) | Título | Financiador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| 2024-07-02 | Bolsa Funarte Brasil Conexões Internacionais 2024 (R$ 600 mil; 40 × R$ 15 mil) | Funarte | gov.br/funarte/.../2024/bolsa-funarte-brasil-conexoes-internacionais-2024 | 2024-08-19 | encerrado_arquivar | depende |
| 2024-07-19 | Programa Ibercena 2024 | Funarte / Ibercena | .../2024/programa-ibercena-2024 | 2024-07-30 | encerrado_arquivar | depende |
| 2024-07-22 | Retomada Cultural RS – Bolsa Ações Artísticas Continuadas 2024 (R$ 4,5 mi) | Funarte | .../2024/programa-retomada-cultural-rs-...-2024-1 | 2024-08-05 | encerrado_arquivar | não (só RS) |
| 2024-08-05 | Bolsa Funarte Residência Artística na Enclo 2024 | Funarte | .../2024/bolsa-funarte-residencia-artistica-na-enclo | 2024-08-30 | encerrado_arquivar | não (só PF) |
| 2024-08-19 | Prêmio Funarte Marc Ferrez de Fotografia – 17ª ed. (R$ 660 mil) | Funarte | .../2024/premio-funarte-marc-ferrez-...-17a-edicao | 2024-09-17 | encerrado_arquivar | depende |
| 2024-11-04 | Processo seletivo ENCLO Turma 2025-2026 / Bolsa Cultural (R$ 3,7 mi) | Funarte | .../2024/processo-seletivo-...-enclo-turma-2025-2026-bolsa-cultural | 2024-12-02 | encerrado_arquivar | não (só PF) |
| 2024-11-14 | Edital de Mobilidade Cultural MinC/Funarte – Intercâmbio (R$ 1,4 mi) | MinC / Funarte | .../2024/edital-de-mobilidade-cultural-minc-funarte-... | 2025-02-03 (2º ciclo; inscrições suspensas) | encerrado_arquivar | depende |
| 2024-12-20 | Funarte Aberta 2025 – Ocupação MG e SP (pauta gratuita) | Funarte | .../2024/programa-funarte-aberta-2025-...-mg-e-sp | 2025-12-01 | encerrado_arquivar | depende |
| 2024-12-28 | Funarte Aberta 2025 – Ocupação RJ (pauta gratuita) | Funarte | .../2024/programa-funarte-aberta-2025-...-rio-de-janeiro | 2025-12-01 | encerrado_arquivar | depende |
| 2025-03-17 | Conexões Internacionais 2025 – Brasil-França – Participação em Eventos (R$ 1,578 mi) | Funarte | .../2025/bolsa-funarte-...-participacao-em-eventos | 2025-04-11 | encerrado_arquivar | depende |
| 2025-06-30 | Ações Continuadas 2025 – Teatro (R$ 4,5 mi; módulos de R$ 100/300/500 mil) | Funarte | .../2025/programa-funarte-de-apoio-a-acoes-continuadas-2025/...-teatro | 2025-08-08 | encerrado_arquivar | depende |
| 2025-08-29 | Prêmio Funarte Mestras e Mestres das Artes 2025 (R$ 5 mi; 50 × R$ 100 mil) | Funarte | .../2025/premio-funarte-mestras-e-mestres-das-artes-2025 | 2025-09-29 | encerrado_arquivar | depende |
| 2025-09-22 | Bolsa de Investigação Magaly Muguercia 2025-2027 (€ 7.500) | Funarte / Ibercena | .../2025/bolsa-de-investigacao-magaly-muguercia-2025-2027 | 2025-11-05 | encerrado_arquivar | não (só PF) |
| 2025-12-19 | Difusão Nacional 2025 – Circuito Myriam Muniz de Teatro (R$ 4,5 mi) | Funarte | .../2025/programa-funarte-de-difusao-nacional-2025/circuito-myriam-muniz-de-teatro | 2026-01-28 | encerrado_arquivar | depende |
| 2025-12-19 | Bolsa Funarte de Mobilidade Artística Internacional (R$ 2 mi + supl.; 91 selecionados) | Funarte | .../2025/programa-funarte-brasil-conexoes-internacionais/bolsa-funarte-de-mobilidade-artistica-internacional | "" (resultado publicado) | encerrado_arquivar | depende |

**B. Oportunidades do período só com título e link (o prazo não aparece na página ou a página não foi aberta)**

| Data | Título | Financiador | Site oficial | Prazo | Estado | Aplicável |
|---|---|---|---|---|---|---|
| "" | Programa Funarte Aberta (2026), listado como aberto | Funarte | .../2026/programa-funarte-aberta | "" | sem_data | depende |
| "" | Programa Ibermúsicas – Convocatórias 2026 (14 linhas), listado como aberto | Funarte / Ibermúsicas | .../2026/programa-ibermusicas-convocatorias-2026 | "" | sem_data | depende |
| "" | Laç(z)os Artísticos – Chamada Especial CPLP, listado como aberto | Funarte | .../2026/laczos-artisticos-2013-chamada-especial-cplp (403) | "" | sem_data | depende |
| "" | Mostra dos Estudantes – 16ª Quadrienal de Praga PQ 2027, listado como aberto | não confirmado | link externo cenografiasdoavesso.com (não aberto) | "" | sem_data (aguardar_fonte) | depende |
| "" | Programa Ibercena – Convocatória 2026-2027 | Funarte / Ibercena | .../2026/programa-ibercena-convocatoria-2026-2027 | "" | sem_data | depende |
| "" | Prêmio Ibero-Americano de Dança | Funarte / Plataforma Iberoamericana de Danza | .../2026/premio-ibero-americano-de-danca (302 para linktree) | "" | sem_data | depende |
| "" | Programa Ibercena – Convocatória 2025-2026 | Funarte / Ibercena | .../2025/programa-ibercena-convocatoria-2025-2026 | "" | sem_data | depende |
| "" | Ibercena – Confluências das Artes Cênicas Afro Ibero-americanas e da Diáspora | Funarte / Ibercena | .../2025/programa-ibercena-confluencias-... | "" | sem_data | depende |
| "" | Conexões Internacionais 2025 – Brasil-França – Jovens criadores (OFF Avignon / Bienal de Lyon) | Funarte | .../2025/bolsa-funarte-...-off-avignon-e-na-bienal-de-danca-de-lyon | "" | sem_data | depende |
| "" | Programa Ibermúsicas – Convocatórias 2025 | Funarte / Ibermúsicas | .../2025/programa-ibermusicas-convocatorias-2025 | "" | sem_data | depende |

Os itens de 2025 desta tabela B não constam em `editais-abertos`. Muito provavelmente já estão encerrados, mas ficaram como sem_data porque não li um prazo.

**C. Itens publicados em 2023 e conferidos: todos ficam fora do período, porque fecharam antes de 02/10/2023**
- Ações Continuadas 2023 – Grupos e Coletivos: publicado em 31/07/2023, inscrições até 13/09/2023, R$ 10 mi, só PJ cultural.
- Mestras e Mestres 2023: publicado em 20/07/2023, inscrições até 18/08/2023.
- Retomada 2023 – Teatro: publicado em 12/07/2023, inscrições até 06/09/2023.
- XXV Bienal de Música Brasileira Contemporânea: publicado em 08/09/2023, inscrições até 18/09/2023.

Os outros 19 itens da pasta 2023 são da mesma safra (meados de 2023) e não foram abertos. Estão listados na seção 8.

**Verificação dos 18 indícios do sistema.** Abri 15 links oficiais: 13 responderam com conteúdo e são da Funarte; Laç(z)os deu 403; Prêmio Ibero-Americano de Dança redirecionou para linktr.ee. Programa Ibermúsicas 2025 e Funarte Brasil Conexões Internacionais 2025 (página-mãe) aparecem nas listagens, mas a página de detalhe não foi aberta. Os indícios têm **defeitos graves**:
- **Os prazos estão errados em todos os 8 indícios que trazem prazo e que conferi.** O motor parece pegar dia e mês e projetar o ano para o futuro: Marc Ferrez 2026-11-14 (real: 2024-09-17); Magaly 2026-11-05 (real: 2025-11-05); Residência Enclo 2026-10-17 (real: 2024-08-30); Retomada RS 2026-10-08 (real: 2024-08-05); Conexões 2024 2027-07-02 (real: 2024-08-19); Ibercena 2024 2027-07-30 (real: 2024-07-30); Mobilidade 2027-01-06 (real: 2025-02-03); ENCLO 2026-11-28 (real: 2024-12-02). Por causa disso, editais encerrados há 1 a 2 anos aparecem no painel como abertos.
- O campo `publicado` está vazio em 17 dos 18 indícios, embora toda página de detalhe traga "Publicado em dd/mm/aaaa".
- Há títulos errados: "plataforma_pid | Linktree" (o motor seguiu o redirecionamento) e "Laçzos" (o slug virou título).
- Há valores truncados: "R$ 100" nas duas páginas Funarte Aberta, onde a cessão de pauta é gratuita.
- O `resumo` é texto de menu e acessibilidade, sem conteúdo útil.
- Há duplicidade de caminho: o mesmo edital aparece como `/editais-abertos/<slug>` e como `/editais/2026/<slug>`.

---

## 3. Onde publica

- **Site oficial:** portal gov.br da Funarte, `https://www.gov.br/funarte/pt-br/editais/`, com pastas por ano e uma página de "editais abertos". Cada edital tem uma página própria com período, valores, anexos e contato (e-mail @funarte.gov.br).
- **Plataforma de inscrição:** quase sempre o **Prosas** (`prosas.com.br/editais/<id>` ou um subdomínio `*.prosas.com.br`). As exceções verificadas:
  - Edital de Mobilidade MinC/Funarte: inscrição pelo **Mapa da Cultura** (mapa.cultura.gov.br/oportunidade/5325);
  - Ibercena: plataforma própria em **iberescena.org**;
  - Ações Continuadas 2023: e-mail para as etapas seguintes;
  - Prêmio Ibero-Americano de Dança: linktree da Plataforma Iberoamericana de Danza.
- **Programas multilaterais** em que a Funarte representa o Brasil: Ibercena, Ibermúsicas, CPLP (Laç(z)os) e Plataforma Iberoamericana de Danza. Nesses casos a Funarte republica a chamada, e as bases ficam no site do programa.

## 4. Tipos de oportunidade

- **Edital de projeto/fomento:** Ações Continuadas (para grupos, espaços e eventos calendarizados; módulos de R$ 100 a 500 mil), Difusão Nacional (circuitos de R$ 150 a 500 mil por linguagem), Retomada (2023 e RS 2024), Mobilidade Cultural.
- **Prêmio:** Mestras e Mestres das Artes (R$ 100 mil cada), Marc Ferrez de Fotografia (R$ 30 mil, mais bolsas de R$ 60 mil), Bienal de Música (R$ 5 a 10 mil).
- **Bolsa:** Conexões Internacionais (R$ 15 a 17 mil individual; grupos até R$ 148 mil), residências e curso técnico da ENCLO, Magaly Muguercia (€ 7.500).
- **Cessão de espaço (pauta gratuita):** Funarte Aberta, com espaços no RJ, em MG e em SP.
- **Chamada internacional:** Ibercena, Ibermúsicas, CPLP, Quadrienal de Praga.
- **Áreas:** teatro, dança, circo, música, artes visuais e fotografia.
- **Quem pode participar:** varia por edital. Os grandes fomentos (Ações Continuadas, Difusão) aceitam **só PJ de direito privado de natureza cultural**, com ou sem fins lucrativos; uma OSC entra se o estatuto e o histórico forem culturais. Prêmios e bolsas costumam aceitar PF, MEI, EI e PJ. Escola de circo e Magaly aceitam só PF. Retomada RS era só para o RS. Os editais nacionais têm **cota regional**: Ações Continuadas 2025 – Teatro reserva no mínimo R$ 700 mil por região, inclusive o Centro-Oeste.
- **Aplicabilidade à A.M.C. Jardim América (Goiânia/GO):** quase tudo ficou como "depende". O peso está na exigência de natureza cultural e de 3 anos de atividade artística continuada (em Ações Continuadas 2023). Nenhuma oportunidade é exclusiva de outro estado, exceto Retomada RS e as pautas físicas em RJ, MG e SP.

## 5. Calendário

| Mês | O que abriu (2023–2026) |
|---|---|
| mar | Conexões Internacionais Brasil-França (2025) |
| jun–ago | Ações Continuadas (jul/2023, jun/2025), Retomada (jul/2023), Retomada RS (jul/2024), Conexões 2024 (jul), Ibercena (jul/2024), Mestras e Mestres (jul/2023), Residência Enclo (ago/2024), Marc Ferrez (ago/2024), Mestras e Mestres 2025 (ago) |
| set | Bienal de Música (2023), Magaly Muguercia (2025) |
| nov | ENCLO (2024), Mobilidade MinC/Funarte (2024) |
| dez | Funarte Aberta (ocupação do ano seguinte, aberta até 1º/dez), Difusão Nacional (2025, fecha em jan), Mobilidade Artística Internacional (2025) |

Há dois picos: **julho a setembro** (fomentos grandes e prêmios) e **dezembro** (Funarte Aberta e Difusão). As inscrições ficam abertas por 2 a 6 semanas, com prorrogações frequentes.

---

## 6. Conselho de 7 lentes sobre o motor

1. **Dra. Helena Vasconcelos, professora de computação com pós-doutorado em Python (extremamente pessimista):** "O motor diz que está 'satisfatório' e entrega 18 itens. Em 8 deles, o prazo inventa um ano futuro: edital de 2024 aparece com prazo em 2027. Isso não é falha pequena. É um gerador de falso positivo que leva o titular a correr atrás de editais mortos. Além disso, não existe rota configurada (`None`), o `publicado` sai vazio quase sempre e o título vem do linktree. Hoje o motor é pior do que ter nada, porque passa uma confiança que não tem."
2. **Rafael Toledo, chief engineer (pessimista):** "A listagem não tem data. O motor visita o detalhe, mas extrai o texto errado: o resumo é o menu de acessibilidade. Ele não desce para as subpáginas dos programas-mãe, por isso Ações Continuadas e Difusão viram um item só e perdem os cinco editais reais de cada um. Os caminhos `/editais-abertos/` e `/editais/2026/` duplicam itens. O 403 e o 302 externo não são tratados."
3. **Marina Okabe, staff engineer (levemente pessimista):** "O site é Plone e é bem previsível: pastas por ano, sem paginação, 'Publicado em' padronizado e 'De dd/mm/aaaa até dd/mm/aaaa' com ano. O defeito está todo no parser, não na fonte. Dá para corrigir com pouco código. Falta só um teste de regressão com datas que não trazem o ano."
4. **Prof. Dr. Augusto Ferraz, pós-doutorado em Python (neutro):** a síntese vem no fim desta seção.
5. **Carla Mendes, CTO de big tech (levemente otimista):** "A fonte é oficial, estável e permitida pelo robots, e cobre 3 anos com 4 URLs. Cada página de detalhe tem valor, público e link do Prosas. Com o parser corrigido, o motor passa a ser referência para o fomento federal às artes."
6. **Dr. Tiago Brandão, staff engineer (otimista):** "A Funarte publica fomentos de R$ 4,5 a 10 milhões com cota regional para o Centro-Oeste e aceita PJ sem fins lucrativos. O histórico dá um calendário confiável (julho a setembro e dezembro), e o motor pode dar alerta antecipado, antes de o edital abrir."
7. **Profa. Lúcia Arantes, chief engineer (extremamente otimista):** "No cenário ideal, o motor lê editais-abertos todo dia e as pastas de ano toda semana, desce às subpáginas e extrai período, valor e quem pode. Também faz a ponte com o Prosas, pelo id do edital, e com iberescena.org. O resultado é 100% de cobertura do fomento federal às artes, com classificação correta e previsão anual."

**Síntese do neutro (Prof. Dr. Augusto Ferraz)**

- **Decisão:** manter o motor ativo, mas **rebaixar o status de "satisfatório" para "defeituoso – corrigir parser"**. Até a correção, suspender a marcação "aberto" que hoje vem dos indícios. Os 18 indícios atuais devem ser reclassificados com as datas reais deste relatório: todos estão encerrados ou sem data.
- **Melhorias:** estão na seção 7.
- **Parâmetros de qualidade:**
  - 100% dos itens com `publicado` preenchido a partir de "Publicado em";
  - 0 prazos com ano inferido; quando o ano não aparecer explicitamente, usar "";
  - prazo conferido por amostra ≥ 95% correto (5 itens por rodada);
  - 0 títulos de domínio externo (linktree);
  - duplicidade por slug = 0;
  - cobertura: os itens das pastas de ano mais as subpáginas devem bater com a contagem manual (2024 = 9; 2025 ≥ 10 + subpáginas; 2026 ≥ 5).
- **Riscos e mitigação:**
  1. *Mudança de layout no gov.br.* Mitigação: âncoras textuais ("Publicado em", "Inscrições"), alarme quando 0 datas forem extraídas.
  2. *403 ou bloqueio de bot em algumas páginas* (já ocorreu em Laç(z)os). Mitigação: registrar, tentar de novo no dia seguinte, sem contornar; manter a URL como sem_data.
  3. *Redirecionamento para sites externos* (linktree, Ibercena). Mitigação: não seguir domínio externo para título e prazo; marcar como "fonte externa – aguardar".
  4. *Programas-mãe sem dados.* Mitigação: descer um nível; se ainda faltar dado, sem_data.
  5. *Página "Atualizado em 09/09/2026" em massa*, que dá falsa novidade. Mitigação: usar "Publicado em" como data, nunca "Atualizado em".
  6. *Elegibilidade restrita* (PJ de natureza cultural). Mitigação: o filtro marca "depende" e lista a exigência em `quem_pode`.

## 7. Melhorias do motor (lista numerada)

1. **Rota:** configurar a rota explícita como a lista `editais-abertos` + `/editais/{ano corrente}` + `/editais/{ano-1}`, mais uma varredura semanal de `/editais/{ano-2}` e `/editais/{ano-3}`. Hoje a rota é `None`.
2. **Parser de data (crítico):** extrair `publicado` de "Publicado em dd/mm/aaaa" e o prazo do texto "até dd/mm/aaaa" ou "a dd de <mês> de aaaa". **Proibir inferir o ano.** Se o ano não estiver no texto, deixar "". Validar que prazo ≥ publicado e que prazo ≤ publicado + 18 meses.
3. **Histórico/subpáginas:** quando a página for um programa-mãe (lista de links filhos sob o mesmo caminho), descer um nível e criar um item por linha, como Ações Continuadas (5 linguagens), Difusão Nacional (5 circuitos), Ibercena (3 linhas) e Funarte Aberta (sedes).
4. **Deduplicação:** usar o último segmento do slug como chave; normalizar `/editais-abertos/<slug>` para `/editais/<ano>/<slug>`; ignorar sufixos `-1`.
5. **Link oficial:** guardar a URL gov.br como `url` e o link do Prosas, Mapa da Cultura ou iberescena.org como "plataforma_inscricao". Não substituir o título pelo do destino de um redirecionamento.
6. **Léxico e extração:** remover do texto o bloco de menu e acessibilidade antes do resumo; capturar valor com unidade ("mil", "milhões", "€") para evitar o "R$ 100"; capturar "Pessoas Jurídicas de direito privado... com ou sem fins lucrativos" para marcar `perfil = osc`.
7. **Filtro de aplicabilidade:** regra "só PF" ⇒ não; "só PJ de natureza cultural" ⇒ depende; abrangência restrita a outro estado (RS, pautas RJ/MG/SP) ⇒ não ou depende.
8. **Cadência:** diária para `editais-abertos` (pico em julho a setembro e em dezembro) e semanal para as pastas de ano. Gerar alerta antecipado em junho e em novembro.
9. **Estado:** classificar como aberto só quando houver prazo ≥ hoje com ano explícito, ou quando o item estiver em `editais-abertos`. Neste último caso, sem prazo explícito, usar sem_data com a marca "listado como aberto".

## 8. O que não foi confirmado e por quê

- **Prazos das oportunidades listadas como abertas** (Funarte Aberta 2026, Ibermúsicas 2026, Laç(z)os CPLP, Quadrienal de Praga PQ 2027): as páginas-mãe não trazem prazo. Laç(z)os respondeu 403. A Quadrienal leva a um site externo (cenografiasdoavesso.com) que não abri, e o promotor ficou sem confirmação; por isso recebeu `aguardar_fonte`.
- **Prêmio Ibero-Americano de Dança:** a URL da Funarte redireciona para linktr.ee/plataforma_pid, que não abri. Prazo e valor não foram confirmados.
- **Linhas filhas não abertas, por limite de chamadas:** Ações Continuadas 2025 (Artes Visuais, Circo, Dança, Música); Difusão Nacional 2025 (circuitos Marcantonio Vilaça, Carequinha, Klauss Vianna, Pixinguinha); Ibercena 2025-2026 e 2026-2027 (3 linhas cada; a URL deduzida de uma subpágina deu 404); Ibercena Confluências; Brasil-França Avignon/Lyon; Ibermúsicas 2025. Os URLs das filhas de Ações Continuadas e Difusão não foram registrados em livros para não inventar caminhos.
- **Prazo da Bolsa de Mobilidade Artística Internacional:** a página não traz o período de inscrição de forma clara, só o resultado (91 selecionados). Ficou como encerrada, com prazo "".
- **Pasta 2023:** abri 4 dos 23 itens, e todos fecharam antes de 02/10/2023. Os outros 19 não foram abertos: Rede das Artes 2023 (5 bolsas), Funarte Aberta 2023 RJ e MG/SP, Ibermúsicas 2023, Mid Atlantic 2023, Ações Continuadas 2023 (Eventos e Espaços), Bolsa Mobilidade Artística 2023, Retomada 2023 (Artes Visuais, Circo, Dança, Música), Ibercena 2023/2024, Magaly 2023-2025 e uma revogação. Não dá para afirmar se algum deles teve prazo depois de 02/10/2023. O mais provável é Ibercena 2023/2024.
- **"Editais Anteriores" e "Editais em andamento":** o link de editais em andamento existe no menu, mas o slug deduzido deu 404. Editais Anteriores cobre 2021–2022 e está fora do período.
- **Rota sem JavaScript:** a busca interna (`@@search`) e um eventual feed não estão disponíveis para leitura HTML (RSS deu 404).
- **Coleta por `curl`:** o proxy recusou a conexão (CONNECT 403), então não foi possível medir os cabeçalhos HTTP diretamente.
- **Dados pessoais:** nenhum nome de pessoa física premiada foi registrado.
