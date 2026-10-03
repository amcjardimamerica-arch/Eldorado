# Motor 30 — site-transferegov — Relatório de estudo (02/10/2026)

Escopo: Transferegov, a plataforma federal de transferências. A rota configurada é `siconv_programa.zip`. O leitor é `transferegov_api` (módulo Parcerias) mais `siconv_zip`.
Foram usadas cerca de 37 chamadas WebFetch. WebSearch está desativado para a organização. O `curl` pelo Bash foi recusado pelo proxy de saída (403 de política) para `api-publica.transferegov.gestao.gov.br`.
Nenhuma página trouxe instruções dirigidas a assistentes de IA.

## 1. Rota (teste e conclusão)

| URL testada | Responde? | O que entrega |
|---|---|---|
| `https://api-publica.transferegov.gestao.gov.br/downloads/dadosgov/siconv_programa.zip` (rota configurada) | Sim, mas é binário | O WebFetch não lê ZIP e o curl foi bloqueado pelo proxy. Não deu para contar itens nem conferir campos nesta sessão. É o único arquivo que cobre as **transferências voluntárias/discricionárias** (convênios, termos de fomento e colaboração com OSC), de onde vieram 11 dos 16 indícios. |
| `https://api-publica.transferegov.gestao.gov.br/downloads/dadosgov/siconv_programa.csv` | 404 | Não existe versão CSV solta. |
| `https://api-publica.transferegov.gestao.gov.br/downloads` | Sim (SPA) | Lista de arquivos carregada por JavaScript ("Buscando arquivos disponíveis…"). Não dá para ler sem navegador. |
| `https://api-publica.transferegov.gestao.gov.br/parcerias/programa` | Sim, JSON | Módulo **Gestão de Parcerias**: fundo a fundo da saúde e do SUAS, Pronon/Pronas, Lei de Incentivo à Reciclagem, Multa Ambiental e Contrato de Gestão. Traz `cd_programa`, `nm_programa`, órgão superior e repassador, `tp_instrumento`, `qualificacao_beneficiario`, `situacao_programa`, datas de início e fim por modalidade (espontâneo, emenda, específico), `nr_vlr_global`, `ufs_habilitadas`, `programa_atende_a`, objetivo e público-alvo. **Não traz link oficial nem data de publicação.** |
| `https://api-publica.transferegov.gestao.gov.br/parcerias/openapi.json` | Sim | Documenta filtros: `ano_programa`, `cd_programa`, `nm_programa` (busca parcial), `situacao_programa` (Em Elaboração/Inativo/Disponibilizado), `sg_uf`, `nr_vlr_global`, `pagina` e `tamanho_da_pagina` (1–200, padrão 50). Outros endpoints: /proposta, /parceria, /beneficiario_emenda_parlamentar, /data-atualizacao. |
| `https://api-publica.transferegov.gestao.gov.br/parcerias/data-atualizacao` | Sim | `{"data_ultima_atualizacao":"2026-08-27T00:00:00"}`, ou seja, a base está **36 dias defasada**. |
| `https://discricionarias.transferegov.sistema.gov.br/voluntarias/programa/ConsultarPrograma/ConsultarPrograma.do` (página do titular) | Não, sem login | Devolve "HTTP Post Binding (Request)", um redirecionamento SAML/SSO gov.br. Nenhuma lista pública. Não foi contornado. |
| `https://www.gov.br/transferegov/pt-br` | Sim | Portal institucional. Aponta para o Painel "Transferências Discricionárias e Legais – Visão OSC" (dd-publico.serpro.gov.br, filtro naturezaJuridica=OSC) e para o portal `portal.transferegov.sistema.gov.br` (SPA, sem conteúdo legível). |
| `https://api.convenios.gov.br/siconv/v1/consulta/programas.json` (API antiga) | Não | Domínio não resolve mais. |

**Conclusão da rota:**
- O ZIP continua sendo a rota correta para programas voluntários com OSC, porque é o único caminho público com os programas `ConsultarPrograma`. Ele precisa ser complementado.
- A API Parcerias com `?ano_programa=AAAA&tamanho_da_pagina=50&pagina=N`, ou com `?nm_programa=Pronon|Pronas|Recicla`, é a **melhor rota verificada para o histórico** do módulo Parcerias: tem filtros por ano e paginação.
- O WebFetch trunca respostas acima de cerca de 25 itens. O leitor do sistema deve usar `tamanho_da_pagina=50` e iterar `pagina`.
- O **link oficial** não vem do Transferegov. Precisa vir da página do órgão. Para Pronon e Pronas: `https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/AAAA`.

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**Como ver o histórico.**
- A API Parcerias aceita `ano_programa=2024|2025|2026`. Nenhum programa de 2023 apareceu: o módulo começou em 2024.
- O ZIP siconv traz `DT_PROGRAMA_INI/FIM` e a situação de todos os anos, mas não foi lido nesta sessão.
- Os chamamentos do Ministério da Saúde ficam em páginas anuais (`/chamamentos-publicos/2024`, `/2025` e `/2026`).

Volume da API Parcerias:
- 2024: 7 programas.
- 2025: cerca de 30 programas, 27 deles fundo a fundo.
- 2026: cerca de 27 programas, 26 deles fundo a fundo.

A grande maioria é **fundo a fundo para entes públicos** (Ministério da Saúde e FNAS/MDS) e não se aplica a OSC. Esses programas foram contados, mas não listados um a um.

| data (início) | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| 2024-09-04 | Pronas/PCD 2024 – serviços, formação de RH e pesquisas (2024-00001/2/3) | Ministério da Saúde – SE | gov.br/saude/pt-br/se/pronon-e-pronas-pcd | 2024-10-18 | encerrada | depende |
| 2024-09-04 | Pronon 2024 – formação de RH e pesquisas (2024-00005/6) | Ministério da Saúde – SE | idem | 2024-10-18 | encerrada | depende |
| 2024-09-04 | Pronon 2024 – serviços médico-assistenciais (2024-00004) | Ministério da Saúde – SE | idem | 2025-07-15 | encerrada | depende |
| 2024-12-18 | Lei de Incentivo à Reciclagem (2024-00007) | MMA | não localizado | 2024-12-31 | encerrada | depende |
| 2025-01-02 | Lei de Incentivo à Reciclagem 2025 (2025-00001) | MMA | não localizado | 2025-10-31 | encerrada | depende |
| 2025-04-11 | Multa Ambiental – Resíduos Sólidos em Consórcios de MG (2025-00002), R$ 100 mi | MMA | não localizado | 2025-07-10 | encerrada | não (só consórcios públicos de MG) |
| 2025-05-12 | Pronon – serviços (2º ciclo) – revogado (2025-00003) | Ministério da Saúde – SE | gov.br/saude/pt-br/se/pronon-e-pronas-pcd | 2025-06-25 | encerrada | depende |
| 2025-05-26 | Pronon – serviços (2º ciclo) (2025-00004) | Ministério da Saúde – SE | idem | 2025-10-02 | encerrada | depende |
| 2025-10-06 (publ.) | Chamamento nº 3/2025 – Pronon (2025-00089/90/91), de R$ 500 mil a R$ 13 mi | Ministério da Saúde – SE | …/chamamentos-publicos/2025/chamamento-publico-no-03-2025-se-pronon | 2025-11-12 | encerrada | depende |
| 2025-10-06 (publ.) | Chamamento nº 2/2025 – Pronas/PCD (2025-00092/93/94), de R$ 250 mil a R$ 4 mi | Ministério da Saúde – SE | …/chamamentos-publicos/2025/chamamento-publico-no-02-2025-se-pronas | 2025-11-05 | encerrada | depende |
| 2026-01-19 | Lei de Incentivo à Reciclagem 2026 (2026-00001) | MMA | não localizado | 2026-07-31 | encerrada | depende |
| 2026-05-01 | Rede Sarah – Contrato de Gestão (2026-00067) | Ministério da Saúde | não localizado | 2026-06-30 | encerrada | não |
| 2026-05-01 | SUAS – Emendas de Comissão – Custeio GND3 (2026-00065) | MDS/FNAS | não localizado | 2026-12-31 | aberta | não (fundo a fundo) |
| 2026-05-01 | SUAS – Emendas de Comissão – Investimento GND4 (2026-00066) | MDS/FNAS | não localizado | 2026-12-31 | aberta | não |
| 2026-05-01 | SUAS – Emendas de Bancada – Investimento GND4 (2026-00064) | MDS/FNAS | não localizado | 2026-12-31 | aberta | não |
| (2016/2026-02-06*) | SUAS – Emendas Individuais – Investimento GND4 (2026-00006) | MDS/FNAS | não localizado | 2026-12-31 | aberta | não |
| 2026-02-06 | SUAS – Emendas Individuais – Custeio GND3 (2026-00005) | MDS/FNAS | não localizado | 2026-12-31 | aberta | não |

\* Duas leituras da API devolveram `dt_inicio_beneficiario_emenda` = 06/02/2016, provavelmente um erro de digitação na fonte. O campo ficou vazio.

**Financiadores e programas que aparecem no Transferegov, com site oficial:**

| Financiador | Programas | Site oficial |
|---|---|---|
| Ministério da Saúde – SE/CPRON | Pronon, Pronas/PCD | https://www.gov.br/saude/pt-br/se/pronon-e-pronas-pcd (confirmado) |
| Ministério da Saúde | Fundo a fundo e Rede Sarah | Página não localizada |
| MMA | Reciclagem e Multa Ambiental | Página não localizada; dois caminhos testados deram 404 |
| MDS/FNAS | SUAS fundo a fundo | Não localizado |
| Indícios do ZIP (voluntárias) | MAPA, MDA, MIDR, MEC/Capes, MS, MCTI, MinC, Esporte, MDS, MDHC, MMA | Não verificados nos sites dos ministérios, por falta de busca e de orçamento de chamadas |

**Verificação por amostra dos 16 indícios.** Todos os 16 têm `link_oficial = null`, então não havia nenhum link oficial a abrir.

- **11 páginas `ConsultarPrograma.do#programa-NNNNN`**
  - Testado: a URL base cai no SSO gov.br. O fragmento `#` não chega ao servidor, então os 11 links equivalem a uma única página fechada. **Não abrem publicamente** e não identificam o financiador.
  - **Defeito grave:** os números "programa 22000, 49000, 53000, 26000, 36000, 24000, 42000, 51000, 55000, 81000, 44000" são **códigos de órgão superior** (22000 = MAPA, 26000 = MEC, 36000 = MS, 44000 = MMA etc.), não códigos de programa.
  - O motor usa a coluna errada como identificador. Com isso ele gera uma URL inválida e provavelmente **colapsa todos os programas de cada ministério em um só registro** na deduplicação: 11 indícios, 11 ministérios diferentes.
- **5 links da API (`?cd_programa=2026+-+000xx`)**
  - Abrem (3 testados diretamente e 2 conferidos na listagem de 2026) e confirmam o programa.
  - Porém os 5 estão marcados como `perfil: "osc"` e na verdade são **Transferências Fundo a Fundo para fundos de assistência social de entes federados**, por emenda parlamentar. **Falso positivo de perfil OSC**: o filtro provavelmente se baseou em palavras do texto ("famílias", "vulnerabilidade").

**Oportunidades novas, fora dos indícios, com site oficial:**
- Pronon nº 3/2025.
- Pronas/PCD nº 2/2025.
- Pronon 2º ciclo 2025.
- Pronon 2024 (2 lotes).
- Pronas/PCD 2024.

São 6 livros com `criar_livro`. Reciclagem, Multa e Rede Sarah ficaram em `aguardar_fonte`.

## 3. Onde publica

- **Transferegov.br (voluntárias):** cadastro do programa, envio de proposta e plano de trabalho, tudo com login gov.br. Fora do login, o programa só aparece no ZIP de dados abertos, que é atualizado diariamente segundo o portal, e no Painel Visão OSC (Serpro).
- **Transferegov.br (Parcerias):** API pública em JSON. A inscrição também é no Transferegov, com perfil "Beneficiário Espontâneo" (OSC proponente), "Beneficiário de Emenda Parlamentar" ou "Específico".
- **Órgãos concedentes:** o **edital** (chamamento público com prazos, valores e requisitos) sai na página do ministério e no DOU (in.gov.br). Exemplos: `gov.br/saude/.../chamamentos-publicos/AAAA/...` e o edital Pronon no DOU. O Transferegov é só a plataforma de inscrição.
- Os chamamentos MROSC de cada ministério (termos de fomento) seguem o mesmo padrão: página do ministério mais Transferegov.

## 4. Tipos de oportunidade

- **Edital de projeto (chamamento público MROSC ou incentivo fiscal):** Pronon e Pronas/PCD, apoiados por renúncia fiscal de doadores. OSC de saúde com CEBAS, OS, OSCIP ou CNES.
- **Cadastro:** Lei de Incentivo à Reciclagem, com Declaração de Responsabilidade para projetos incentivados.
- **Programas de emenda parlamentar:** a OSC só entra se for indicada por parlamentar, no tipo "Beneficiário de Emenda". É a principal porta para a A.M.C. em programas voluntários e exige articulação política.
- **Proponente específico:** programa já destinado a uma entidade nomeada (por exemplo, o indício MAPA "Proponente Específico" e o SBPC vai à Escola). Não se aplica a terceiros.
- **Fundo a fundo:** só para entes públicos. Não se aplica.
- Não há prêmios, bolsas nem chamadas internacionais.

**Áreas:** saúde (oncologia, deficiência), assistência social, meio ambiente/reciclagem, além de esporte, cultura, direitos humanos, educação e desenvolvimento rural nos indícios do ZIP.

**Faixas de valor confirmadas:**
- Pronon: de R$ 500 mil a R$ 13 mi por projeto.
- Pronas/PCD: de R$ 250 mil a R$ 4 mi.
- Os demais programas não informam valor (`nr_vlr_global` nulo ou 0).

**Quem pode participar:**
- Pronon e Pronas: pessoa jurídica privada sem fins lucrativos (associação ou fundação) com CEBAS, OS, OSCIP ou CNES.
- Emendas: OSC indicada por parlamentar.
- Fundo a fundo: entes públicos.

## 5. Calendário

- **Pronon e Pronas/PCD:** abrem no início de setembro ou de outubro. Em 2024, de 04/09 a 18/10. Em 2025, publicação em 06/10 e inscrições de 07/10 a 05/11 (Pronas) ou 12/11 (Pronon). Em 2025 houve ainda um 2º ciclo Pronon de serviços, de 26/05 a 02/10. Em 02/10/2026 **ainda não há chamamento 2026** publicado na página do Ministério da Saúde, que foi atualizada em 23/02/2026. Pelo padrão, a **janela provável é outubro e novembro de 2026**, então é preciso vigiar agora.
- **Lei de Incentivo à Reciclagem:** abre em janeiro e fecha em julho ou outubro (2025: de 02/01 a 31/10; 2026: de 19/01 a 31/07).
- **Programas de emenda (voluntárias e SUAS):** abrem entre fevereiro e maio e fecham entre junho e dezembro. Seguem o cronograma anual de emendas parlamentares.

## 6. Conselho de 7 lentes

1. **Extremamente pessimista — Dra. Helga Matsuda, chief engineer, cética por ofício.** "O motor marca o painel como 'satisfatório' e entrega 16 achados sem um único link oficial. Onze deles apontam para uma página atrás do SSO, com um fragmento `#programa-36000` que é código de **órgão**, não de programa. A chave de deduplicação está errada: há um registro por ministério. Os 5 'OSC' são fundo a fundo para prefeituras. Na prática o motor está cego e se acha produtivo."
2. **Pessimista — Prof. Rodrigo Albuquerque, pós-doutor em Python, rigor de revisor.** "O leitor depende de um ZIP que não valida esquema. A API Parcerias ignora a paginação: com 50 por página, o motor perde itens quando o ano tem mais de 50. A data de atualização da base é 27/08. Sem conferir `/data-atualizacao`, o motor não sabe que o dado está velho. E a data 2016 dentro de um programa 2026 mostra que falta sanidade de datas."
3. **Levemente pessimista — Camila Ferraz, staff engineer, pragmática.** "O filtro de perfil precisa usar campos estruturados: `tp_instrumento` (excluir 'Fundo a Fundo'), `qualificacao_beneficiario` e `programa_atende_a`. Hoje ele usa palavras soltas. É uma correção barata."
4. **Neutro — Eng. Marcos Teixeira, CTO de big tech, árbitro.** Fecha abaixo.
5. **Levemente otimista — Prof. Yara Nakamura, pós-doutora em Python, didática.** "A API Parcerias é limpa, tem OpenAPI, filtro por ano e por nome e paginação. Com 3 consultas fixas (Pronon, Pronas, Recicla) o motor recupera todo o histórico de incentivo fiscal que interessa a OSC."
6. **Otimista — Diego Valadares, chief engineer, construtor.** "O Transferegov é a fonte primária de onde o dinheiro federal realmente sai. Cruzar o programa (Transferegov) com o edital (página do ministério e DOU) dá prazo, valor e link oficial com alta confiança. É a fonte mais 'à prova de boato' do sistema."
7. **Extremamente otimista — Profa. Lúcia Brandão, CTO, visionária.** "Com o ZIP lido direito, o motor enxerga *todos* os programas voluntários abertos a OSC no Brasil, por UF e por órgão, antes de qualquer agregador. Somando a vigia sazonal de Pronon e Pronas e um alerta de emendas, a A.M.C. passa a antecipar janelas de R$ 250 mil a R$ 13 mi."

**Síntese do neutro (Marcos Teixeira).**

*Decisão:* **manter o motor, rebaixá-lo de "satisfatório" para "parcial com defeito de chave"** e corrigir antes do próximo ciclo. Os 16 indícios atuais não viram livros. Os 5 SUAS são arquivados como "não aplicável". Os 11 do ZIP ficam em reprocessamento após a correção da chave.

*Parâmetros de qualidade:*
- 100% dos itens com `cd_programa` no formato `AAAA - NNNNN` ou com o código siconv do programa, nunca com o código de órgão.
- 0 itens fundo a fundo com perfil OSC.
- Pelo menos 80% dos livros com link oficial do órgão.
- Base com no máximo 7 dias de defasagem, conforme `/data-atualizacao`.
- 100% das datas dentro do ano do programa ±1.
- Contagem paginada igual ao total da API.

*Riscos e mitigação:*
1. SSO e mudança de portal (já houve migração de API). Mitigar com teste diário das 3 rotas e alarme se o status for diferente de 200 ou se a resposta não for JSON ou ZIP.
2. ZIP grande ou com esquema alterado. Mitigar validando colunas esperadas e falhando de forma ruidosa.
3. Base defasada. Mitigar marcando "dado de AAAA-MM-DD" no livro e alertando acima de 7 dias.
4. Falsos positivos de OSC. Mitigar com filtro estruturado mais revisão humana de "depende".
5. Edital fora do Transferegov (ministério e DOU). Mitigar com a sementeira de páginas anuais de chamamentos por ministério.
6. Emendas que dependem de indicação parlamentar. Mitigar marcando "depende – emenda" e não contando como oportunidade aberta.

## 7. Melhorias do motor

1. **Chave (deduplicação):** usar `ID_PROGRAMA`/`COD_PROGRAMA` do ZIP, ou `id_programa`/`cd_programa` da API. **Nunca** `COD_ORGAO_SUP`. Reprocessar os 11 indícios.
2. **Rota (histórico):** adicionar `parcerias/programa?ano_programa={2024,2025,2026}&tamanho_da_pagina=50&pagina=N`, com iteração até a página vir vazia, e as consultas fixas `nm_programa=Pronon|Pronas|Recicla`.
3. **Filtro OSC estruturado:** excluir `tp_instrumento` que contenha "Fundo a Fundo" e "Contrato de Gestão". Aceitar "Beneficiário Espontâneo" e programas cujo `programa_atende_a` inclua entidade privada sem fins lucrativos. No ZIP, usar a natureza jurídica habilitada e descartar "Proponente Específico".
4. **Link oficial:** mapear o órgão para a sua página de chamamentos (por exemplo, MS: `gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/AAAA`, e o DOU). Sem esse casamento, usar `aguardar_fonte`. Nunca gravar `ConsultarPrograma.do#…` como link.
5. **Cadência:** diária para o ZIP e a API. Vigia reforçada de setembro a novembro (Pronon e Pronas) e de janeiro a maio (Reciclagem e emendas). Ler `/parcerias/data-atualizacao` e registrar a defasagem.
6. **Prazo correto:** usar a data fim da modalidade aplicável (espontâneo, emenda ou específico) e não a data máxima. Validar o ano.
7. **Léxico:** separar "emenda parlamentar" (depende de indicação) de "chamamento público" (concorrência aberta). Incluir "Pronon", "Pronas", "termo de fomento" e "chamamento público MROSC".
8. **Leitor do ZIP:** rodar fora do WebFetch, com download direto pelo leitor do sistema, e validar o esquema. Gravar a contagem total, a contagem com OSC elegível e a contagem com situação disponibilizada.

## 8. O que não foi confirmado e por quê

- **Conteúdo do ZIP `siconv_programa.zip`:** é binário, o WebFetch não lê e o curl foi bloqueado pelo proxy. Ficaram sem confirmação a quantidade de programas, quais aceitam OSC e as datas dos 11 indícios voluntários (MAPA, MDA, MIDR, MEC/Capes, MS, MCTI, MinC, Esporte, MDS, MDHC, MMA).
- **Página `ConsultarPrograma.do`:** exige SSO gov.br. Não houve login, por regra.
- **Sites oficiais do MMA (Reciclagem e Multa), da Rede Sarah e do MDS/FNAS:** WebSearch indisponível, e as URLs testadas no gov.br/mma deram 404. Esses itens ficaram em `aguardar_fonte`.
- **Chamamentos Pronon e Pronas de 2024:** a página anual de 2024 do Ministério da Saúde é paginada e a primeira página não os listava. As datas vêm só da API Parcerias. A URL usada é a página oficial do programa.
- **Contagem exata de programas fundo a fundo de 2025 e 2026:** o WebFetch truncou as respostas. Os totais são aproximados (cerca de 30 e cerca de 27).
- **Chamamento 2026 de Pronon e Pronas:** não publicado até a última atualização da página (23/02/2026).
- Fora do escopo do motor, apenas registrado: o Chamamento nº 14/2026-GM/MS seleciona entidade privada sem fins lucrativos para qualificação como Organização Social. É aberto, mas não pertence ao Transferegov.
