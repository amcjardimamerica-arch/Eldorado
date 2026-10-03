# Motor 31 — site-rede-comua (Rede Comuá) — Estudo de 02/10/2026

Escopo: só este motor. 44 chamadas de WebFetch (curl direto ao domínio foi bloqueado pelo proxy da sessão). O robots.txt (`/robots.txt`) só bloqueia PetalBot e SemrushBot e pede crawl-delay a Bing e Google; nenhuma rota usada aqui está proibida. Não houve login, CAPTCHA nem formulário. Nenhuma página trouxe instrução dirigida ao agente.

Observação de tipo: o painel classifica o site como FINANCIADOR, mas a Rede Comuá é uma **rede de fundos independentes** e funciona como **agregador**: cada post repassa uma chamada de um fundo associado (Fundo Casa, Fundo Brasil, iCS, Fundo Ecos, Baobá etc.), que publica e recebe inscrições no próprio site. O estudo cobre as duas leituras: lista todas as chamadas do período e identifica quem publica e onde.

---

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| `https://redecomua.org.br/wp-json/wp/v2/_editais` (rota configurada) | Sim, JSON | Tipo de post `_editais`. Campos: id, date, modified, slug, link, title, content. **Sem** campos de prazo, valor ou link oficial (sem `acf`/`meta`; sem taxonomias). O padrão do WordPress é 10 itens por página. |
| `…/_editais?per_page=100&after=2023-10-02T00:00:00&before=…&_fields=id,date,slug,title` | Sim | Filtro por data funciona. Com fatias de data, o período inteiro saiu em 4 chamadas: **86 posts** entre 24/10/2023 e 14/07/2026. |
| `…/_editais/12641` (item único) | Sim | `content.rendered` não traz prazo nem link oficial de forma estruturada. |
| `https://redecomua.org.br/edital/` (página do titular) | Sim | Lista com "Carregar mais" (sem paginação por URL). Mostra prazo só em 2 itens marcados como ativos, e os dois já estavam vencidos (18/09 e 14/07/2026). O selo de "ativo" não é confiável. |
| `https://redecomua.org.br/editais/<slug>/` (página de cada edital) | Sim, 25 de 25 | **É aqui que estão o prazo ("Inscrições até …"), o valor, quem pode participar e o link oficial do financiador.** |

**Conclusão.** A rota configurada é a melhor porta de **descoberta**, mas da forma como está (sem `per_page`) ela só vê os 10 posts mais recentes e não traz prazo nem link oficial. Rota recomendada, verificada:

```
https://redecomua.org.br/wp-json/wp/v2/_editais?per_page=100&_fields=id,date,modified,slug,link,title&after=<AAAA-MM-DDT00:00:00>
```

Depois, para cada id **novo ou com `modified` alterado**, buscar a página HTML `link` e extrair "Inscrições até", valor e o link externo do financiador. Feed RSS e sitemap não foram testados (orçamento de chamadas usado na extração).

**Defeito grave nos 5 indícios guardados.** Os 5 estão ENCERRADOS, mas o sistema registrou 3 deles com prazo em 2027:

| Indício | Prazo no sistema | Prazo real (fonte) | Causa provável |
|---|---|---|---|
| Fundo Brasil – Direitos Digitais 2026 | 2027-04-06 | 2026-05-19 (site oficial: "Encerrado") | pegou a data de **início** (6/abr) e passou o ano para frente |
| iCS – Clima na Economia | 2027-03-09 | 2026-04-08 (site oficial: "Inscrições Encerradas") | mesma causa (início 9/mar) |
| Fundo Brasil – Soluções Climáticas a partir da Base | 2027-03-16 | 2026-05-08 | mesma causa (início 16/mar) |
| Crias pelo Clima (Procomum/KondZilla/Querô) | 2027-03-16 | 2026-04-30 | data sem relação; e o link oficial `ngosource.org/...badge` está **errado** (é página de segurança Incapsula, sem relação com a chamada). É só para pessoa física. |
| Prêmio iCS-ANPEC 2026 | 2026-09-18 | **2026-10-02** (site oficial prorrogou) | o agregador não atualizou; só para pessoa física (doutores) |

O parser trata uma data "dd de mês" que já passou como se fosse do ano seguinte e confunde início com fim do período de inscrição. Por isso aparecem **falsos abertos**. O mesmo erro afetaria "08 de Outubro" (Belém, 2025), que viraria 08/10/2026.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**86 oportunidades** publicadas no período: 1 aberta (prazo hoje, não aplicável), 85 encerradas e 0 sem data. As 25 mais recentes (30/09/2025 em diante) foram abertas uma a uma. As 61 anteriores vieram da API só com título e data; o encerramento delas foi **inferido** porque todas foram publicadas há mais de 12 meses (ver seção 8).

### 2a. Verificadas individualmente (25)

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2026-07-14 | Prêmio iCS-ANPEC de Economia & Clima 2026 | iCS + ANPEC (Hub de Economia e Clima) | hubdeeconomiaeclima.org.br/premio-ics-anpec-de-economia-e-clima/ | 2026-10-02 | ABERTA (último dia) | não (só PF) |
| 2026-07-14 | Agenda Rio 2030 – Penha e Alemão | Casa Fluminense | casafluminense.org.br/atuacao/fundo-casa-fluminense/ | 2026-07-12 | ENCERRADA | não (RJ) |
| 2026-06-17 | Apoio direto para iniciativas comunitárias | Fundo Casa | casa.org.br/chamadas/chamada-simplificada-apoio-direto-a-iniciativas-comunitarias/ | 2026-07-14 | ENCERRADA | depende (grupos novos ou em retomada) |
| 2026-06-17 | Justiça climática liderada por juventudes | Fundo Casa | casa.org.br/chamadas/juventudes-e-justica-climatica-… | 2026-06-30 | ENCERRADA | depende |
| 2026-06-17 | Soluções climáticas a partir da base e dos territórios | iCS | climaesociedade.org/edital/solucoes-de-adaptacao-climatica-… | 2026-07-01 | ENCERRADA | depende |
| 2026-06-17 | Territórios Vivos da Amazônia | Fundo Casa | casa.org.br/chamadas/territorios-vivos-da-amazonia-… | 2026-06-16 | ENCERRADA | não (Amazônia) |
| 2026-06-17 | Direitos humanos e justiça criminal 2026 | Fundo Brasil | fundobrasil.org.br/edital/direitos-humanos-e-justica-criminal-2026-… | 2026-06-26 | ENCERRADA | depende |
| 2026-06-17 | Crias pelo Clima | Procomum, KondZilla, Querô | criaspeloclima.procomum.org | 2026-04-30 | ENCERRADA | não (PF, Baixada Santista) |
| 2026-06-17 | Fortalecimento dos direitos territoriais | Fundo Casa | casa.org.br/chamadas/fortalecimento-dos-direitos-territoriais/ | 2026-05-19 | ENCERRADA | não (Amazônia Legal e NE) |
| 2026-06-09 | Territórios conservados por povos indígenas e comunidades tradicionais | Fundo Ecos (ISPN) | fundoecos.org.br | 2026-04-27 | ENCERRADA | depende |
| 2026-06-09 | Black STEM 2026 | Fundo Baobá | editais.baoba.org.br/lp-black-stem | 2026-05-18 | ENCERRADA | não (PF) |
| 2026-06-09 | Trilha de formação em adaptação climática | iCS | (só LinkedIn, aguardar fonte) | 2026-04-06 | ENCERRADA | depende |
| 2026-04-21 | Direitos Digitais 2026 | Fundo Brasil | fundobrasil.org.br/edital/direitos-digitais-2026/ | 2026-05-19 | ENCERRADA | depende |
| 2026-03-20 | Clima na Economia | iCS | climaesociedade.org/edital/clima-na-economia-… | 2026-04-08 | ENCERRADA | depende |
| 2026-03-19 | Soluções Climáticas a partir da Base | Fundo Brasil (Raízes/Labora) | fundobrasil.org.br/edital/solucoes-climaticas-a-partir-da-base/ | 2026-05-08 | ENCERRADA | depende |
| 2026-03-19 | Educação para o Bem Viver 2026 | Fundo Casa | casa.org.br/chamadas/chamada-educacao-para-o-bem-viver-2026-… | 2026-04-28 | ENCERRADA | depende (indígenas e quilombolas) |
| 2026-03-19 | Mata Atlântica Viva 2026 | Fundo Casa | casa.org.br/chamadas/mata-atlantica-viva-…-2026/ | 2026-03-25 | ENCERRADA | depende (bioma) |
| 2026-03-05 | Crédito Comunitário Sustentável | Fundo Casa | casa.org.br/chamadas/credito-comunitario-sustentavel-… | 2026-04-09 | ENCERRADA | não (Amazônia) |
| 2026-01-22 | Trabalhadores Informais 2026 | Fundo Brasil (Labora) | fundobrasil.org.br/edital/fortalecendo-trabalhadores-informais-…-2026/ | 2026-02-09 | ENCERRADA | depende |
| 2026-01-21 | ICOM – Justiça Climática Começa nos Territórios | ICOM (Florianópolis) | (conjunta.org não confirmado, aguardar fonte) | 2026-02-06 | ENCERRADA | não (SC) |
| 2025-12-11 | Edital Geral 2026 | Fundo Brasil | fundobrasil.org.br/edital/geral-2026-… | 2026-03-06 | ENCERRADA | **sim** |
| 2025-12-11 | LGBTQIAPN+ Defendendo Direitos 2026 | Fundo Brasil | fundobrasil.org.br/edital/lgbtqia-defendendo-direitos-2026/ | 2026-02-06 | ENCERRADA | depende |
| 2025-11-14 | Fundo Regenerativo PcD | Associação Nossa Cidade | nossacidade.net/pt/chapters/fundo-pcd | 2025-11-17 | ENCERRADA | não (MG) |
| 2025-09-30 | 45º Edital Cerrado e Caatinga | Fundo Ecos (ISPN) | fundoecos.org.br/editais/45o-edital-cerrado-e-caatinga/ | 2025-11-10 | ENCERRADA | **sim** (GO tem selecionados) |
| 2025-09-30 | Cuidar e Enfrentar a Crise Climática em Belém | Procomum e Rádio Savia | confluenciasdoscuidados.procomum.org/chamada-publica/ | 2025-10-08* | ENCERRADA | não (PA) |

\* ano inferido pela data de publicação, porque a página diz só "08 de Outubro".

### 2b. Listadas pela API, sem abertura individual (61, de 24/10/2023 a 24/09/2025)

Todas estão como `encerrado_arquivar` + `aguardar_fonte` em `livros.json`, com título e data exatos da API. O financiador só foi preenchido quando aparece no título: Fundo Positivo, Casa Fluminense, Fundo Casa, FunBEA, iCS, Fundo Brasil, CESE, ELAS+, Baobá, ICOM, Procomum. Destaques recorrentes que interessam a uma OSC de Goiânia: **Edital Geral** do Fundo Brasil (2024 e 2025), **PPP-ECOS Cerrados & Caatinga** (2024), **Trabalhadores Informais** (2024 e 2025), **Enfrentando o Racismo a partir da Base 2024**, **Mulheres em Movimento 2024** (ELAS+) e **Incidência Popular em Segurança Pública**. Lista completa no JSON.

## 3. Onde publica

- **Rede Comuá** (`redecomua.org.br/editais/<slug>/`): repassa a chamada com resumo, prazo, valor e botão para o site do fundo. Não recebe inscrições.
- **Financiadores (site oficial e inscrição):**
  - Fundo Brasil de Direitos Humanos: `fundobrasil.org.br/edital/<slug>/`; inscrição no portal próprio `fundobrasil.powerappsportals.com`.
  - Fundo Casa Socioambiental: `casa.org.br/chamadas/<slug>/`; inscrição na plataforma própria CasaDigital.
  - Instituto Clima e Sociedade (iCS): `climaesociedade.org/edital/<slug>/` (formulário eletrônico próprio) e `hubdeeconomiaeclima.org.br` (Microsoft Forms).
  - Fundo Ecos / ISPN: `fundoecos.org.br/editais/<slug>/`; inscrição por JotForm, com versão .doc offline.
  - Fundo Baobá: `editais.baoba.org.br/lp-…`.
  - Instituto Procomum: subdomínios por chamada (`criaspeloclima.procomum.org`, `confluenciasdoscuidados.procomum.org`).
  - Casa Fluminense: `casafluminense.org.br/atuacao/fundo-casa-fluminense/`, com edital em PDF.
  - Outros: ICOM (link via `conjunta.org`, não confirmado), Associação Nossa Cidade (`nossacidade.net`), Fundo Positivo, FunBEA, CESE e ELAS+ (sites não visitados).
- Nenhuma chamada do período usa Prosas, Mapas Culturais ou Transferegov. Todas usam formulário ou portal do próprio fundo.

## 4. Tipos de oportunidade

- **Edital de projeto** (cerca de 90%): apoio institucional ou a projetos de grupos de base, quase sempre aceitando **coletivos sem CNPJ**.
- **Prêmio**: iCS-ANPEC, para pessoa física.
- **Bolsa ou formação** (tipo "outro"): Black STEM e Já É (Baobá), Marielle Franco – Apoio Individual, trilhas do iCS, formações do ICOM, Crias pelo Clima. Em geral são para pessoa física.
- **Crédito comunitário / fundo rotativo**: Crédito Comunitário Sustentável (Fundo Casa).
- Não houve chamada internacional para OSC; o Black STEM é bolsa para estudar no exterior.
- **Áreas:** justiça climática e adaptação (dominante desde 2024), direitos humanos, racismo, LGBTQIAPN+, mulheres, trabalhadores informais, povos indígenas, quilombolas e comunidades tradicionais, educação, direitos digitais, justiça criminal, direito à cidade, biomas (Amazônia, Cerrado/Caatinga, Mata Atlântica).
- **Faixas de valor:** micro de R$ 3 mil a R$ 20 mil (Nossa Cidade, Fundo Casa apoio direto, ICOM); padrão de R$ 30 mil a R$ 60 mil (Fundo Brasil, Fundo Casa); médio de R$ 100 mil a R$ 250 mil (Fundo Ecos, eixo 2 do Fundo Brasil); grande de R$ 200 mil a R$ 500 mil (crédito rural e pesquisa do iCS). O total por chamada vai de R$ 1,75 milhão a R$ 5 milhões.
- **Quem pode:** organizações e coletivos de base, com ou sem CNPJ. Muitas chamadas têm recorte territorial (Amazônia, Nordeste, RJ, SC, Baixada Santista, BH, Belém) ou de público (indígenas, quilombolas, juventudes, mulheres, LGBTQIAPN+).

## 5. Calendário

Posts por mês de publicação (86 no período): jan 8, fev 6, mar 11, abr 7, mai 6, **jun 22**, jul 6, ago 2, set 8, out 3, nov 2, dez 5. Por ano: 2023 (out-dez) 6, 2024 32, 2025 28, 2026 (até jul) 20.

- **Dez-jan:** Fundo Brasil abre o Edital Geral, o LGBTQIA+ e o Trabalhadores Informais, com fechamento em fevereiro ou março.
- **Mar-jun (pico):** Fundo Casa (Mata Atlântica, Bem Viver, Amazônia), iCS, Fundo Brasil temáticos, Fundo Ecos, ELAS+. As inscrições duram de 3 a 7 semanas.
- **Set-nov:** Fundo Ecos Cerrado/Caatinga, ICOM, chamadas pós-incêndios.
- A Rede Comuá publica em lotes e com atraso. Vários posts de 17/06/2026 e de 14/07/2026 já saíram com o prazo vencido. **O motor precisa ler direto as páginas oficiais dos fundos.**

## 6. Conselho de 7 lentes

1. **Extremamente pessimista – Dr. Heitor Valadares** (chief engineer, ríspido): "O motor está 'satisfatório' e guarda 5 achados, e os 5 estão mortos. Três deles têm prazo em 2027, tirado da data de abertura com o ano empurrado para frente. Um aponta para uma página de firewall da ngosource. O painel mente. Isto é pior que zero achados, porque gera alarme falso de oportunidade aberta."
2. **Pessimista – Profa. Lígia Sampaio** (pós-doc em Python, metódica): "A rota sem `per_page` vê 10 itens e não tem paginação nem `after`. A API não expõe prazo, então tudo depende de raspar o HTML, que muda com o tema. A página `/edital/` marca como 'ativo' o que já venceu. E `financiador` está nulo em 3 de 5."
3. **Levemente pessimista – Marcos Ito** (staff engineer, pragmático): "O agregador atrasa. Posts saem com o prazo vencido, e o prêmio iCS-ANPEC foi prorrogado no site oficial sem atualização na Comuá. Usar o agregador como fonte de prazo é estruturalmente fraco; ele serve para descoberta."
4. **Neutro – Dra. Beatriz Okafor** (CTO de big tech, síntese): fecha abaixo.
5. **Levemente otimista – Prof. Renato Queiroz** (pós-doc, didático): "A API é limpa: filtro por data, `_fields`, `modified` para detectar mudança. Em 4 chamadas saiu o histórico inteiro de 3 anos. Poucos motores têm descoberta tão barata."
6. **Otimista – Camila Durães** (chief engineer de dados): "Cada post traz link oficial de domínio do próprio fundo (casa.org.br, fundobrasil.org.br, climaesociedade.org, fundoecos.org.br) com padrão de URL estável. O motor pode aprender esses domínios e semear rotas diretas aos fundos."
7. **Extremamente otimista – Dr. Otávio Lacerda** (staff engineer visionário): "É a melhor carteira de filantropia independente do país, com valor típico de R$ 50 mil, coletivos sem CNPJ aceitos e calendário previsível. Com a série histórica, dá para prever a abertura do Edital Geral do Fundo Brasil (dezembro) e do Fundo Ecos Cerrado (setembro) e preparar a A.M.C. com meses de antecedência."

**Síntese do neutro (Dra. Beatriz Okafor):**

- **Decisão:** manter o motor, rebaixá-lo de "satisfatório" para **"em correção"** e invalidar já os 5 indícios atuais (todos encerrados; 3 com prazo falso em 2027; 1 com link errado). Daqui em diante, a Comuá serve como **descobridor**; prazo e link valem pelo site oficial do fundo.
- **Melhorias:** ver seção 7.
- **Parâmetros de qualidade:**
  - 0 prazos com ano maior que o da publicação mais 1 sem ano explícito no texto;
  - 100% dos livros com `url` em domínio do financiador (lista branca), nunca redes sociais ou terceiros;
  - `financiador` preenchido em pelo menos 95% dos casos;
  - divergência de prazo entre agregador e site oficial registrada, valendo o oficial;
  - cobertura de 100% dos ids da API no período (conferir `X-WP-Total`);
  - latência de no máximo 24 h para post novo.
- **Riscos e mitigação:**
  1. Falso aberto por ano inferido. Mitigação: exigir o ano explícito ou o ano da publicação; nunca somar +1 ao ano.
  2. Mudança do tema HTML quebra a extração. Mitigação: testes com 3 páginas fixas e alarme se o prazo vier vazio em mais de 30% dos casos.
  3. Link oficial errado ou de rede social. Mitigação: lista branca de domínios e `aguardar_fonte` fora dela.
  4. Atraso ou prorrogação não refletidos. Mitigação: reconferir o site oficial a cada 7 dias enquanto aberto.
  5. Bloqueio ou limite (robots pede crawl-delay a bots grandes). Mitigação: no máximo 1 requisição a cada 5 s e cadência diária, não horária.
  6. Recortes territoriais ou de pessoa física poluindo a lista da A.M.C. Mitigação: filtro de aplicabilidade (UF/bioma, PF/PJ) antes de notificar.

## 7. Melhorias do motor

1. **Rota:** trocar para `…/_editais?per_page=100&_fields=id,date,modified,slug,link,title&after=<último visto>`, paginar por `X-WP-TotalPages` e reprocessar quando `modified` mudar.
2. **Extração de prazo (correção crítica):** ler o rótulo "Inscrições até:" da página do post; em "de X a Y", o prazo é **Y**; sem ano explícito, usar o ano da publicação; **proibir** que o ano avance automaticamente.
3. **Link oficial:** pegar o botão "acesse/saiba mais" e validar contra uma lista branca de domínios dos fundos (casa.org.br, fundobrasil.org.br, climaesociedade.org, hubdeeconomiaeclima.org.br, fundoecos.org.br, baoba.org.br, procomum.org, casafluminense.org.br, nossacidade.net…). LinkedIn, Instagram ou terceiros vão para `aguardar_fonte`.
4. **Confirmação na fonte oficial:** para cada candidato a aberto, abrir o site oficial e preferir o prazo de lá (caso iCS-ANPEC prorrogado; status "Encerrado" do Fundo Brasil e do iCS).
5. **Financiador:** extrair do texto ("lançado pelo…") ou do domínio do link oficial; nunca `null`.
6. **Filtro de aplicabilidade:** marcar PF (prêmios, bolsas, "apoio individual", "jovens selecionados") e recorte territorial (Amazônia Legal, RJ, SC, SP, MG, PA) como `nao` para a A.M.C.; Cerrado e nacional como `sim/depende`.
7. **Histórico:** importar os 86 posts do período como `encerrado_arquivar`, para alimentar a previsão de calendário (Fundo Brasil em dez/jan, Fundo Casa em mar-jun, Fundo Ecos em set).
8. **Deduplicação:** chave = domínio + caminho do link oficial; quando não houver, slug normalizado (há duplicatas antigas com sufixo `-2`, como `edital-agenda-rio-2030-2`).
9. **Cadência:** diária (a Comuá publica em lotes), mais uma revisão semanal dos abertos no site oficial.
10. **Rotas diretas dos fundos (motor derivado):** criar ou alimentar leitores de `casa.org.br/chamadas` e `fundobrasil.org.br/editais`, que publicam antes e atualizam o status; a Comuá chega com semanas de atraso.

## 8. O que não foi confirmado e por quê

- **61 posts de 24/10/2023 a 24/09/2025:** não abri as páginas por causa do limite de cerca de 40 chamadas. Ficam sem prazo, valor e link oficial, e o encerramento é **inferido**: todos foram publicados há mais de 12 meses, e as chamadas observadas duram de 3 a 7 semanas. Ação: `aguardar_fonte`.
- **Total exato da API:** não consegui ler o cabeçalho `X-WP-Total` (WebFetch não mostra cabeçalhos e curl foi bloqueado pelo proxy). A contagem de 86 vem das 4 fatias por data; a primeira leitura sem filtro pareceu truncada pelo resumo da ferramenta.
- **ICOM:** o link `conjunta.org/…` não respondeu (timeout no robots.txt), então não se confirmou se é site do ICOM.
- **Agenda Rio 2030 (Casa Fluminense):** a página oficial abre, mas o prazo só está no PDF, que não foi lido. O prazo vem do agregador.
- **Belém (Procomum):** a página traz "08 de Outubro" sem ano; usei 2025 pela data de publicação.
- **Fundo Ecos 2026 (territórios conservados):** o agregador aponta só a home `fundoecos.org.br`; a página específica não foi localizada.
- **Nossa Cidade, Fundo Casa (juventudes, Amazônia, territoriais, Bem Viver, Mata Atlântica, crédito), iCS adaptação, Fundo Brasil (justiça criminal, Geral 2026, LGBTQIA+, Informais):** link oficial extraído da página do agregador, com domínio do próprio fundo, mas a página oficial não foi aberta. Amostra de 10 links oficiais tentados: 8 abriram e eram do financiador (Fundo Brasil, iCS, Hub Economia e Clima, Fundo Casa, Fundo Ecos, Procomum, Casa Fluminense, Baobá), 1 estava errado (ngosource) e 1 caiu (conjunta.org).
- **Feed RSS e sitemap:** não testados.
- Nenhum dado pessoal foi registrado; pessoas físicas premiadas ou selecionadas não entram.
