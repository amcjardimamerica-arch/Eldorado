# Motor 25 — site-capitaai (CapitaAI)

Estudo feito em 02/10/2026, com 37 chamadas de WebFetch. Tipo de site: AGREGADOR. O CapitaAI divulga editais de terceiros e republica a lista pública do Prosas como "guias de captação".

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| https://capitaai.com.br/robots.txt | sim | `Allow: /`. Bloqueia `/editais$`, `/editais/`, `/api`, `/financiadores`, `/alertas` e áreas logadas. **`/captacao/`, `/editais-abertos/` e `/quem-ganhou/` estão liberados.** Sitemap declarado: `/sitemap.xml` |
| https://capitaai.com.br/sitemap.xml | sim | sitemapindex com 5 filhos: `sitemap-estatico`, `sitemap-blog`, `sitemap-editais`, `sitemap-aprovados` e `sitemap-captacao` |
| **https://capitaai.com.br/sitemap-captacao.xml** (rota configurada) | sim | **400 URLs** `/captacao/...`, todas com `lastmod`. As datas vão de 2026-08-18 a 2026-10-02. O sitemap não traz prazo, valor nem link oficial; esses dados só aparecem nas páginas de detalhe. |
| https://capitaai.com.br/sitemap-editais.xml | sim | 107 URLs: 104 páginas de categoria `/editais-abertos/*` (por área e por perfil, como `para-ong` ou `saude-para-ong`) e 7 páginas `/leis-de-incentivo/*`. Todas têm o mesmo lastmod, então não servem para cadência. |
| https://capitaai.com.br/sitemap-aprovados.xml | sim | 134 URLs `/quem-ganhou/*`, separadas por UF, cultura, OSCs e prefeituras. É o histórico de premiados, mas pode conter pessoas físicas e por isso não foi usado. |
| https://capitaai.com.br/sitemap-blog.xml | sim | 277 posts, de 2026-08-25 a 2026-10-02. São textos editoriais e não servem como fonte primária. |
| https://capitaai.com.br/editais-abertos/para-ong (página que o titular vê) | sim | Anuncia "250 editais abertos" e mostra uma lista longa sem paginação, ordenada por prazo. Cada item traz título, financiador, prazo, às vezes valor e UF, e um link "Ver detalhes" para `/captacao/...`. **A listagem não tem link oficial externo.** Não há JSON-LD de lista. |
| https://capitaai.com.br/editais-abertos | sim | Anuncia "456 editais abertos". O rodapé leva a `/captacao`, `/quem-ganhou`, `/leis-de-incentivo` e `/blog`. |
| **https://capitaai.com.br/captacao** | sim | É a biblioteca completa: **553 guias** em seções Prosas (89), Observatório 3º Setor (16), Capta (10), Ministério da Saúde (7), FAPEMIG, FAPESC, FAPESB e MinC (5 cada), FAPEG, CNPq e FAPERJ (3 cada), FAPITEC e Fundo Casa (2 cada), Outras fontes (203) e **Editais encerrados (195)**. Não tem paginação. |
| Detalhe `/captacao/<slug>` | sim | JSON-LD `Article` (headline, datePublished, dateModified), prazo, data de publicação, público elegível e um "link oficial" externo. Páginas de editais vencidos continuam no ar com aviso de encerrado (exemplo: FAPESC 51/2026). |

**Conclusão sobre a rota.** A rota configurada funciona, mas não é a melhor. Tem três defeitos:
1. Ela tem **400 URLs enquanto a biblioteca tem 553 guias**. Tudo indica que o sitemap corta em 400 e o motor deixa de ver cerca de 150 guias.
2. Ela não distingue aberto de encerrado. O arquivo de indícios tem **0 encerrados** e 144 itens sem prazo.
3. Prazo, valor e link oficial vêm da página de detalhe, e essa extração está ruim (ver seção 8).

**Rota melhor verificada:** `https://capitaai.com.br/captacao`. É uma página única que traz as 553 entradas já separadas por seção, inclusive "Editais encerrados" com 195 itens. O ideal é combiná-la com `https://capitaai.com.br/editais-abertos/para-ong`, que traz o prazo na listagem e já filtra o perfil OSC. O sitemap fica apenas como detector de novidades, pelo `lastmod`.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**O que se descobriu.** O CapitaAI é um site recente. A URL mais antiga do sitemap de captação é de **18/08/2026** e o blog começa em 25/08/2026. **Não existe arquivo anterior a agosto de 2026**: não há paginação por ano, API pública (o caminho `/api` está bloqueado no robots) nem filtro de data. O único histórico disponível é a seção "Editais encerrados" de `/captacao`, com 195 itens, quase todos com prazo entre ago. e set. de 2026. Alguns guias reaproveitam editais antigos que ainda estão em vigor, como Uberaba 002/2024, CELESC 001 a 004/2024, FCCR 2023 e Uberlândia 213/2023. Por isso, o período de três anos só aparece de forma indireta.

A lista pública do Prosas (`prosas.com.br/editais`) foi testada e está **bloqueada pelo robots.txt** do Prosas. O acesso não foi contornado. O CapitaAI republica 89 guias de origem Prosas.

Tabela das oportunidades que eu confirmei ou extraí. Todas também estão em `livros.json`.

| data (publ.) | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| — | FAPEMIG/CNPq/CAPES 17/2026 PROFIX-CB | FAPEMIG | fapemig.br (página aberta) | 2026-11-03 | aberta | não (ICTs de MG) |
| — | Chamada 20/2026 Atlânticas – Beatriz Nascimento | Min. Mulheres/MCTI/CNPq | gov.br/mulheres (aberta) | "" | sem_data | não (pessoa física) |
| — | CRA-RS 004/2026 Pós-Graduação 2027 | CRA-RS | crars.org.br (aberta) | 2026-10-13 | aberta | não |
| — | CRA-RS 003/2026 Pós-Graduação 2027 | CRA-RS | crars.org.br | 2026-10-13 | aberta | não |
| — | CRA-RS 002/2026 Patrocínio II EGAD | CRA-RS | crars.org.br | 2026-09-04 | encerrada | não |
| — | CRA-RS 001/2026 Painéis II EGAD | CRA-RS | crars.org.br | 2026-09-04 | encerrada | não |
| — | Serpro 857/2026 | Serpro | chamamentos.serpro.gov.br (aberta) | 2026-10-13 | aberta | depende |
| — | FAPESP 42/2026 Auxílio à Inovação Regular | FAPESP | fapesp.br (redireciona) | 2026-10-05 | aberta | não |
| — | Chamada PNAE 2026 (merenda) | SEDUC-GO | goias.gov.br/educacao (aberta) | 2026-10-20 | aberta | não (agricultura familiar) |
| 2026-09-14 | FAPEG 17/2026 (CONFAP/WBI) | FAPEG | goias.gov.br/fapeg | 2026-09-30 | encerrada | não |
| 2026-08-20 | FAPESC 51/2026 C&T | FAPESC | fapesc.sc.gov.br | 2026-09-18 | encerrada | não |
| 2026-09-26 | Programa Marielle Franco – lideranças femininas negras | Fundo Baobá | baoba.org.br (aberta) | 2026-10-19 | aberta | depende (liderança de mulheres negras) |
| — | 15º Edital Fundação Aperam Acesita Social 2026 | Fundação Aperam Acesita | brasil.aperam.com (timeout) | 2026-10-04 | aberta | depende (território) |
| — | Edital Rede Memória Viva | Iniciativa Viva Pequena África | só Prosas/Capta | 2026-10-03 | aberta | depende |
| 2026-08-30 | BNDES R$ 35 mi Norte e Nordeste | BNDES | não confirmado | 2026-09-17 | encerrada | não (N/NE) |
| 2026-09-14 | Editais Sociais 2026 Banco do Nordeste | Banco do Nordeste | não confirmado | 2026-09-30 | encerrada | não (NE) |
| 2026-08-13 | Instituto Impactarte – projetos de impacto social | Instituto Impactarte | não confirmado | "" | sem_data | sim |
| 2026-08-17 | Coop – R$ 500 mil projetos sociais | Coop | não confirmado | "" | sem_data | depende |
| 2026-09-16 | PNAB 1/2026 Patrocínio do Muriaé | Prefeitura de Patrocínio do Muriaé | DOU (não é o site da prefeitura) | 2026-10-02 | aberta | não (MG) |
| — | PNAB Ciclo II 1/2026 Nova América | Prefeitura de Nova América | novaamerica.go.gov.br (timeout) | "" | encerrada | não (outro município) |

Totais: **20 oportunidades** (10 abertas, 7 encerradas e 3 sem data), de **17 financiadores**.

**Verificação por amostra de 12 links oficiais do arquivo de indícios:**

| link do indício | abre? | é do financiador? |
|---|---|---|
| fapemig.br/…/profix-cb | sim | sim, e o conteúdo bate |
| gov.br/mulheres/…/atlanticas | sim | sim |
| crars.org.br/chamamentos-publicos | sim | sim |
| chamamentos.serpro.gov.br/editais/13 | sim | sim (portal genérico) |
| goias.gov.br/educacao/licitacoes/ | sim | sim (órgão certo, mas sem a chamada específica) |
| fapesp.br/18364 | responde com redirecionamento | sim |
| fundacaogrupoboticario.org.br/chamada-busca-negocios… | sim | é da fundação, mas é **notícia de 2020** (1º Mapa GRMA). Link desatualizado. |
| capta.org.br/oportunidades/edital-rede-memoria-viva | sim | **não**, é outro agregador (Capta) |
| brasil.aperam.com/…/editaldeprojetos | **timeout** | domínio do financiador, não confirmado |
| novaamerica.go.gov.br/politica-nacional-aldir-blanc-ciclo-ii/ | **timeout** | domínio do órgão, não confirmado |
| rondonia.ro.gov.br/…/edital-no-4-2023-fapero | **timeout** | domínio do órgão, não confirmado |
| transparencia.caupr.gov.br/chamadas-publicas | **DNS falhou** | não confirmado |

Resultado da amostra: 6 links confirmados, 2 desatualizados ou de agregador, 4 fora do ar.

**Financiadores e programas presentes no agregador.** Os sites oficiais marcados com "(v)" foram abertos por mim. Os demais vêm do domínio do indício e não foram abertos.
- Fomento à pesquisa: FAPEMIG fapemig.br (v), FAPESP fapesp.br (v), FAPESC fapesc.sc.gov.br, FAPEG goias.gov.br/fapeg, FAPESB, FAPERJ, FAPITEC/SE, FAPERO rondonia.ro.gov.br, Fapes, CNPq e CAPES.
- Governo federal: Ministério das Mulheres gov.br/mulheres (v), MinC (salic.cultura.gov.br, culteditais.cultura.gov.br), Ministério da Saúde/SGTES, Funarte (Funarte Aberta), ANATER, Ibama, Marinha, Serpro chamamentos.serpro.gov.br (v), Codeba, Trensurb e IFSP (vários campi).
- Estados e municípios: SEDUC-GO goias.gov.br/educacao (v), prefeituras de GO (Goiatuba, Silvânia, Morrinhos, Ceres, Nova América, Aparecida do Rio Doce, Corumbá de Goiás, Nova Iguaçu de Goiás) e prefeituras de CE, MA, BA, MG, SP, SC e RS, quase todas via DOU.
- Conselhos profissionais: CRA-RS crars.org.br (v), CAU/PR, CAU/BR, CRO-BA, CRBM-4 e CREFITO.
- Privados e institutos: Fundo Baobá baoba.org.br (v), Fundação Aperam Acesita, Fundação Grupo Boticário, Instituto EDP, Instituto John Deere, CEMIG, CELESC, CBMM, Santos Brasil, TAG, Zilor, Zurich Seguros, FCC S.A. (Catalisar), Inter-American Foundation, Fundo Casa Socioambiental, Instituto Impactarte, Coop, BNDES e Banco do Nordeste.
- Plataformas e agregadores citados como "fonte": Prosas (inclusive os BIP – Banco de Investimento em Projetos), Observatório 3º Setor, Capta e captadores.org.br.

## 3. Onde publica

- **O CapitaAI** publica um guia em `/captacao/<slug>` com JSON-LD Article e um "link oficial". Também mantém listas por área e perfil em `/editais-abertos/*`.
- **Os financiadores** publicam em canais diferentes:
  - entes públicos: Diário Oficial da União (pesquisa.in.gov.br, 42 indícios), portais de transparência e licitações municipais, e Transferegov ou culteditais (PNAB);
  - FAPs: PDF no site oficial, como FAPESC, FAPEG e FAPEMIG;
  - privados e institutos: **Prosas** (inscrição) e página própria;
  - poucos casos: formulário Google (forms.gle).
- **Observação importante.** O "link oficial" do CapitaAI muitas vezes aponta para **outro agregador**: Observatório 3º Setor, Capta ou captadores.org.br. Em outros casos aponta para a raiz genérica de um ministério (www.gov.br/cultura, gov.br/mcti), sem relação com o edital.

## 4. Tipos de oportunidade

- **Edital de projeto**: maioria. Inclui PNAB municipal, FAPs, institutos privados, BNDES e Banco do Nordeste.
- **Chamamento ou credenciamento**: muito frequente e, em geral, **não é captação para OSC**. São merenda e PNAE, credenciamento de saúde, leiloeiros, permuta de imóveis, pareceristas e oficineiros (pessoa física).
- **Cadastro ou banco de projetos incentivados**: CELESC, CEMIG, Instituto EDP, John Deere, Santos Brasil e os BIP do Prosas, em fluxo contínuo ligado a leis de incentivo.
- **Prêmio**: alguns, como o Prêmio ABDE-BID.
- **Bolsa ou pessoa física**: FAPESP no exterior, Atlânticas, pós-graduação do CRA-RS.
- **Internacional**: Inter-American Foundation e FAPEG/CONFAP-WBI.
- **Áreas**: cultura (PNAB), C&T, assistência social (CMDCA/CMDPI), saúde, esporte, meio ambiente e equidade racial.
- **Faixas de valor** vistas em páginas confiáveis: de R$ 25 mil (Aperam) a R$ 300 mil (Baobá) por projeto, R$ 1,5 mi por projeto (Banco do Nordeste) e totais de R$ 4,2 mi (FAPEMIG) a R$ 35 mi (BNDES). O campo valor do indício **não é confiável**: 52 dos 329 registros têm "R$ 97", que é o preço da assinatura anual do CapitaAI.
- **Quem pode participar**: OSC, prefeituras, ICTs, empresas e pessoas físicas, misturados. O perfil "osc" do indício aparece em 243 itens, mas inclui chamamentos sem relação com captação.

## 5. Calendário

Só é possível observar de ago. a out. de 2026, porque não há dados anteriores. Nesse intervalo:
- Os prazos se concentram em out. de 2026 (121 indícios), nov. e dez. de 2026 (38) e 2027 (credenciamentos de 12 meses).
- O ritmo de publicação é diário, com cerca de 5 a 10 guias por dia no `lastmod`, gerados por volta das 05h30 UTC.
- Padrões típicos dos financiadores, só como referência: o 2º semestre concentra PNAB municipal (ciclo II), FAPs e editais privados de responsabilidade social. Os bancos de projetos incentivados fecham em out. ou dez., junto com o ano fiscal.

## 6. Conselho de 7 lentes

1. **Extremamente pessimista — Dra. Helga Wernicke, chief engineer, rabugenta e literal.** "O motor lê um sitemap cortado em 400 e perde cerca de 150 guias. Grava 'R$ 97' como valor em 52 registros, o que é o preço da assinatura do site. No item de Patrocínio do Muriaé, gravou 'Fundo Baobá', 'PR' e gov.br/cultura: três campos errados de uma vez. 182 registros não têm link oficial. O painel diz 'satisfatório' para isso."
2. **Pessimista — Prof. Otávio Brandão, pós-doutor em Python, metódico.** "Zero encerrados no indício. A rota não tem histórico, então o motor não alimenta a previsão. Além disso, o 'link oficial' aponta para outros agregadores, como Observatório 3º Setor, Capta e captadores. É agregador citando agregador, e o livro não pode nascer disso."
3. **Levemente pessimista — Rafael Ishikawa, staff engineer, pragmático.** "O filtro de perfil não segura merenda, leiloeiro, residência médica e permuta da Marinha. Uns 40% do volume é ruído para uma OSC de Goiânia."
4. **Neutro — Profa. Lúcia Arantes, pós-doutora em computação, mediadora.** Fecha abaixo.
5. **Levemente otimista — Bruno Tavares, staff engineer, construtor.** "Robots liberal em `/captacao`, JSON-LD com datePublished, páginas de encerrados mantidas e prazo na listagem. É uma fonte fácil e estável de raspar."
6. **Otimista — Carla Mendonça, CTO de big tech, visão de produto.** "O CapitaAI já faz a triagem diária do DOU e do Prosas, inclusive dos 89 guias Prosas que não podemos ler direto por causa do robots. Usado como **descobridor de financiadores**, rende muito: dele saem FAPEG, SEDUC-GO e prefeituras de GO que valem motores próprios."
7. **Extremamente otimista — Dr. Ítalo Ferraz, chief engineer, entusiasta.** "Com deduplicação e resolução de link oficial, isto vira o radar nacional de chamadas do Eldorado: cerca de 450 abertas por dia, com histórico próprio a partir de agora."

**Síntese do neutro (Profa. Lúcia Arantes)**

- **Decisão:** **manter o motor, rebaixado a "descobridor"**, e não como fonte de livro. Os livros só nascem depois que o link oficial é resolvido no financiador. Trocar a rota principal para `/captacao` e `/editais-abertos/para-ong`. O status no painel passa de "satisfatório" para "com ressalvas" até que as melhorias 1 a 5 da seção 7 entrem.
- **Parâmetros de qualidade:**
  - cobertura de pelo menos 95% das entradas de `/captacao` contra o contador da página (553);
  - 0 valores iguais a "R$ 97";
  - pelo menos 80% de links oficiais em domínio do financiador (.gov.br do órgão ou domínio da entidade) e 0 em agregadores conhecidos;
  - estado preenchido em 100% (aberto, encerrado ou sem_data);
  - financiador coerente com o título e com a página de detalhe em 100% de uma amostra semanal de 10;
  - ruído (credenciamento, merenda, leiloeiro ou pessoa física) abaixo de 10% no perfil OSC.
- **Riscos e mitigação:**
  1. Mudança de layout ou slug: monitorar o contador de `/captacao` e alertar se a extração divergir em mais de 5%.
  2. Robots passar a bloquear `/captacao`: reler o robots a cada execução e suspender o motor se houver bloqueio.
  3. Link oficial errado ou de agregador gerar livro falso: lista negra de domínios agregadores e `acao="aguardar_fonte"` automática.
  4. Conteúdo gerado por IA no agregador (títulos e resumos inventados, como "Guia de Captação"): usar sempre o título oficial do órgão e o detalhe só como pista.
  5. Duplicatas com o motor do DOU, os motores das FAPs e o Prosas: deduplicar por (órgão, número do edital, ano) e pela URL oficial normalizada.
  6. Paywall, porque anexos e valores ficam atrás da assinatura de R$ 97: não contornar e buscar o anexo no site oficial.

## 7. Melhorias do motor

1. **Rota:** trocar `sitemap-captacao.xml` (limitado a 400) por `https://capitaai.com.br/captacao`, que tem 553 entradas e seções. Usar `https://capitaai.com.br/editais-abertos/para-ong` para pegar o prazo na listagem. Manter o sitemap só para detectar novidades pelo `lastmod`.
2. **Histórico:** ler a seção "Editais encerrados" de `/captacao` (195 itens) e gravar como `encerrado_arquivar`. Guardar uma fotografia diária própria, já que o site não tem arquivo anterior a 18/08/2026.
3. **Link oficial:** criar lista negra de agregadores (observatorio3setor.org.br, capta.org.br, captadores.org.br, prosas.com.br como "plataforma", forms.gle) e de raízes genéricas (`gov.br/<órgão>/pt-br` sem caminho de edital). Nesses casos, `aguardar_fonte`. Para links do DOU, extrair o órgão e buscar o site do órgão.
4. **Valor:** descartar valores do bloco comercial ("R$ 97") e qualquer valor menor que R$ 1.000 sem contexto. Ler o valor só do corpo do edital.
5. **Coerência de campos:** validar financiador e UF do indício contra o JSON-LD headline e o texto de detalhe, e rejeitar o registro se divergirem (caso Patrocínio do Muriaé, gravado como "Fundo Baobá/PR").
6. **Filtro e léxico:** excluir quando o título ou objeto contiver "credenciamento de leiloeiro", "gêneros alimentícios", "agricultura familiar", "residência médica", "permuta", "pareceristas", "oficineiros" ou "bolsa" sem OSC. Marcar como ok "OSC", "organização da sociedade civil", "termo de fomento", "termo de colaboração", "PNAB" e "banco de projetos".
7. **Regra Goiás:** dar prioridade a GO, Goiânia e editais nacionais. Os itens de PNAB municipal de outro município ficam `aplicavel="nao"`.
8. **Deduplicação:** chave (órgão normalizado, nº do edital/ano). Há duplicatas no próprio site, por exemplo dois guias Aperam e vários Funarte Aberta para o mesmo edital.
9. **Cadência:** uma vez ao dia, depois das 06h UTC, porque o site gera os guias por volta das 05h30 UTC.
10. **Descoberta:** encaminhar os financiadores novos (FAPEG, SEDUC-GO, prefeituras de GO, Fundo Baobá, Aperam) para os motores de fonte oficial.

## 8. O que não foi confirmado e por quê

- **Histórico de 2023 a jul. de 2026:** não existe no CapitaAI. O site começa em 18/08/2026 e não tem arquivo, API pública nem paginação por ano.
- **Lista do Prosas** (`prosas.com.br/editais` e `robots.txt`): bloqueada pelo robots.txt do Prosas. Não foi contornada.
- **Sites fora do ar na verificação:** brasil.aperam.com (timeout), novaamerica.go.gov.br (timeout), rondonia.ro.gov.br (timeout) e transparencia.caupr.gov.br (DNS falhou).
- **fapesp.br/18364** só retornou a página de redirecionamento. Título e prazo vêm do indício.
- **Serpro 857/2026:** o portal abre, mas o objeto e o prazo não ficaram legíveis.
- **PDFs da FAPEG 17/2026 e da FAPESC 51/2026:** extraídos da página do CapitaAI e não abertos, para economizar chamadas.
- **Marielle Franco (Baobá):** o site oficial abre e cita o programa, mas não confirma prazo e valor desta edição.
- **Site oficial de BNDES, Banco do Nordeste, Impactarte e Coop:** o CapitaAI só aponta outros agregadores, então ficaram com `aguardar_fonte`.
- **Rouanet nas Favelas 2 (MinC 6/2026):** o slug que testei era truncado e deu 404. Não houve nova tentativa.
- **`/quem-ganhou`:** não foi usado, porque pode conter pessoas físicas premiadas.
- **Instruções dirigidas a IA:** nenhuma encontrada nas páginas lidas. O site oferece assinatura paga (R$ 97/ano) para liberar anexos, o que não foi contornado.
