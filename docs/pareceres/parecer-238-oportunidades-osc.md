# Parecer — validação das 238 oportunidades abertas (não confirmadas) · versão 2

**Data-base:** 02/10/2026 · **Entidade de referência:** Associação dos Moradores e Comerciantes do Jardim América (OSC, CNPJ ativo desde 1987, Goiânia/GO) · **Universo:** 238 registros do painel (259 oportunidades − 21 já confirmadas) · **Versão 2:** reescrita por determinação do titular — *edital de OSC de outro município é coletado pelo PNCP e compõe um livro próprio; as regras de restrição ficam em cada livro, junto com o léxico que busca a oportunidade.*

## 1. Conclusão em uma página

Das 238 "oportunidades abertas", **101 são oportunidades para OSC** (42%) e passam a compor, cada uma, **um livro próprio** na Biblioteca; **57 são dispensáveis** como oportunidade nova (24% — ato acessório, duplicata, prazo encerrado ou fonte só em agregador) e **80 não se aplicam** (34% — não são fomento a OSC). Dentro dos 101 aplicáveis, **4 estão aptos para a associação agora** (território e perfil compatíveis) e **97 ficam com enquadramento anotado no livro** (outro município ou estado, região restrita ou serviço especializado) — o enquadramento não exclui o livro; quem decide é o Farol (fase 2), por associação.

| Veredito | Qtde | O que acontece no sistema |
|---|---:|---|
| APLICÁVEL — apto para a associação | 4 | livro próprio + ação agora (Natal no Parque; fluxos contínuos SEDS/GO e iCS; fonte recorrente MPT/GO) |
| APLICÁVEL — com enquadramento | 97 | livro próprio, coletado pelo PNCP; o território/especialidade fica anotado no livro (EN-01/02/03) |
| DISPENSÁVEL | 57 | não é oportunidade nova: edição do livro do edital (ato acessório), junção (duplicata), livro no histórico (prazo) ou aguarda o ato oficial (fonte em agregador ou link de outro município) |
| NÃO APLICA | 80 | veto: licitação, RH, concurso/prêmio sem fomento, público que não é OSC, ato de diário, residência no exterior — não vira livro |

**Livros:** os 101 aplicáveis e 3 dispensáveis com livro já existente formam a semente `dados/oportunidades/livros_parecer_238.json` (104 itens): **34 livros novos** e **70 livros existentes atualizados**. Simulando o ciclo sobre uma cópia do catálogo de hoje, a Biblioteca passa de 1033 para **1067 livros**, todos com o bloco `busca` (léxico + restrições), e nenhum livro do parecer é arquivado pela regra de abrangência.

**PNCP:** 55 dos livros do parecer já têm registro no PNCP (chave cnpj/ano/seq). Os 58 registros sem link PNCP foram procurados no PNCP hoje, por município e tema — **nenhum foi localizado**. Para chamamento de OSC (Lei 13.019/2014, art. 26) e edital PNAB (Lei 14.903/2024) a divulgação exigida é no sítio oficial do órgão; o PNCP é obrigatório para as contratações da Lei 14.133/2021. Por isso esses livros nascem com a fonte oficial do órgão (diário ou site) e a **Fonte C do PNCP** passa a procurá-los com a consulta gravada em cada livro — o PNCP é a porta de entrada preferencial, não a única.

**Prioridade absoluta (inalterada):** **Chamamento Público nº 001/2026 da SEGENP/Prefeitura de Goiânia — "Natal no Parque – A Magia de Brincar"** (termo de colaboração com OSC, até **R$ 5.000.000,00**, protocolo único até **26/10/2026**, resultado definitivo em 06/11/2026). Ver seção 7.

## 2. O que mudou da versão 1 para a versão 2

| Tema | Versão 1 (02/10, manhã) | Versão 2 (titular, 02/10) |
|---|---|---|
| Edital de OSC de outro município/estado | DISPENSÁVEL (DI-01: território incompatível) | **APLICÁVEL — livro próprio**, coletado pelo PNCP; território = enquadramento EN-01 |
| Região restrita e serviço especializado | DISPENSÁVEL (DI-02, DI-06) | APLICÁVEL com enquadramento (EN-02, EN-03) |
| Catadores, ILPI, associações estudantis | NÃO APLICA (NA-06) | **mantido NÃO APLICA** — requisito de natureza jurídica e, em vários casos, contratação pela Lei 14.133; vai como proposta ao titular (decisão 3) |
| Onde ficam as regras | um arquivo central aplicado de fora | **em cada livro**, no bloco `busca`, junto com o léxico; o arquivo vira catálogo-mãe |
| Fonte só em agregador (guia CapitaAí, buscarlicitacao, prefeituras.org) | escondida sob DI-01 | DI-05: o livro aguarda o ato oficial (a Fonte C procura no PNCP) |
| Querido Diário | tratado como fonte indireta | texto extraído por terceiro, com link ao arquivo do diário oficial: fonte indicativa aceita para o livro, a confirmar no arquivo oficial |
| Link oficial de outro município (RC-03) | escondido sob DI-01 | DI-05: não vira livro até achar o ato certo (#1, #15, #33, #35, #61, #154, #183) |
| Totais | 4 aplicáveis · 155 dispensáveis · 79 não aplica | **101 aplicáveis (4 aptos)** · 57 dispensáveis · 80 não aplica |

## 3. Prompt aprimorado (executado em sequência)

> Reclassifique as 238 oportunidades com a regra do titular de 02/10: (1) edital de OSC de outro município ou estado é oportunidade para OSC — não é descartado; é coletado pelo PNCP e compõe um livro próprio; o território vira enquadramento anotado no livro; (2) aplique o mesmo raciocínio às restrições de perfil que uma OSC pode cumprir (região, serviço especializado), sem estender a requisitos de natureza jurídica; (3) para os registros sem link PNCP, procure o ato no PNCP; (4) ligue cada registro ao livro existente ou gere a semente de livro novo; (5) grave em CADA livro o seu léxico e as restrições que se aplicam a ele, com o efeito de cada uma (veto, edição, junção, estado, aguardar fonte, enquadramento), sem que uma regra se volte contra o próprio livro; (6) faça o motor do PNCP procurar, com o léxico de cada livro, o ato dos livros sem chave; (7) refaça o parecer e o arquivo de atualização dos livros; teste, simule sobre cópia do catálogo e verifique.

## 4. Método, evidências e limites

- **Injeção de prompt:** varredura com os padrões do sistema (PT/EN) sobre todos os campos dos 238 registros — **0 ocorrências**. Todo texto coletado foi tratado como dado.
- **Níveis de evidência por registro** (coluna *Evidência*): PNCP consultado ao vivo em 02/10/2026 (108); dados do painel (sem fonte oficial confirmada) (70); validação anterior (27–29/09) + dados do painel (55); página oficial lida ao vivo (4); edital lido ao vivo (Diário Oficial de Goiânia 25/09) (1). **Apto** para a associação só com fonte oficial lida; dado só do painel nunca dá aptidão.
- **Busca no PNCP (02/10):** os 58 registros sem link PNCP (54 de outros estados e 4 de outros municípios goianos) foram consultados na busca do portal (`/api/search/`, tipo edital, por município + tema, e pelo número do edital quando havia) — **0 de 58 localizados**. Na conferência dos candidatos devolvidos, os do mesmo município eram credenciamentos ou compras de outro objeto (ex.: leiloeiro, monitores de oficina, instituições financeiras, doação de bens); a lista de candidatos por item não foi guardada, só o resultado. **Leitura jurídica:** o chamamento MROSC é divulgado no sítio oficial do órgão (Lei 13.019/2014, art. 26) e os editais PNAB seguem o regime do fomento cultural (Lei 14.903/2024 e Decreto 11.453/2023, termo de execução cultural) — em nenhum dos dois o PNCP é obrigatório; o PNCP é obrigatório para as contratações da Lei 14.133/2021 (arts. 54 e 174). Por isso credenciamentos regidos pela Lei 14.133 que não apareceram na busca (ex.: #30 Artur Nogueira, #112 Quatá) são lacuna a conferir, não prova de ausência. A restrição territorial, quando existe, vem do edital (a Lei 13.019, art. 24, §2º, I, admite limitar a seleção a OSC sediada ou atuante na unidade da Federação) — por isso o território é anotado como enquadramento, e não presumido como impedimento.
- **Os 12 itens:** ● comprovado em fonte · ◐ dispensa provável pelo regime · – dispensado pelo edital · ○ não comprovado.
- **Limites declarados:** as páginas de ~120 prefeituras não foram abertas ao vivo (para elas valem o painel e a validação de 27–29/09). O enquadramento calculado pelo livro é mais grosseiro que a leitura humana: 8 livros do parecer saem "aptos" no cálculo do livro contra 4 na validação — 2 com prazo encerrado que o livro guarda no histórico (#87 Dia de Doar 2024, #192 SEDS Aprendiz do Futuro), 1 serviço especializado que só a leitura humana enquadra (#193 SEDS socioeducativo) e 1 geografia larga demais no livro (#116 Sonhar o Mundo, só São Paulo).
- **Conceitos (v2):** NÃO APLICA = a natureza ou o público não é fomento a OSC (veto). DISPENSÁVEL = não é oportunidade nova agora (ato acessório, duplicata, prazo, fonte só em agregador ou link de outro município). APLICÁVEL = oportunidade para OSC, em qualquer território → livro próprio; **apto** quando o território e o perfil servem à associação; **enquadramento** quando há restrição de território, região ou especialidade.

## 5. Resultado por regra

| Regra | Veredito | Descrição | Qtde |
|---|---|---|---:|
| NA-01 | NÃO APLICA | Ato do diário oficial que não é chamamento | 1 |
| NA-02 | NÃO APLICA | Licitação, contratação de fornecedor ou serviço | 13 |
| NA-03 | NÃO APLICA | Recursos humanos (concurso, seleção, estágio, aprendizagem) | 2 |
| NA-04 | NÃO APLICA | Página genérica, agregador, notícia ou link sem edital | 3 |
| NA-05 | NÃO APLICA | Concurso ou prêmio sem fomento a OSC | 7 |
| NA-06 | NÃO APLICA | Público-alvo incompatível com a associação | 49 |
| NA-07 | NÃO APLICA | Conselho, eleição ou representação (sem recurso) | 2 |
| NA-08 | NÃO APLICA | Residência artística ou programa de artista individual no exterior | 3 |
| EN-01 | APLICÁVEL | Edital de OSC de outro município/estado — livro próprio (enquadramento territorial) | 94 |
| EN-02 | APLICÁVEL | Edital de OSC com região restrita — livro próprio (enquadramento regional) | 1 |
| DI-03 | DISPENSÁVEL | Prazo encerrado, revogado ou suspenso | 3 |
| DI-04 | DISPENSÁVEL | Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado | 13 |
| DI-05 | DISPENSÁVEL | Não verificável — sem fonte oficial confirmada | 32 |
| EN-03 | APLICÁVEL | Edital de OSC para serviço ou público especializado — livro próprio (enquadramento técnico) | 2 |
| DI-08 | DISPENSÁVEL | Duplicata de outro registro da lista | 9 |
| AP-01 | APLICÁVEL | Goiânia/GO, vigente e elegível a OSC | 1 |
| AP-03 | APLICÁVEL | Fluxo contínuo ou recorrente para OSC | 3 |

| Origem geográfica no painel | APLICÁVEL | DISPENSÁVEL | NÃO APLICA |
|---|---:|---:|---:|
| Goiás | 7 | 7 | 12 |
| balde "nacional" do painel | 14 | 15 | 10 |
| outras UFs | 80 | 35 | 58 |

## 6. Livros — um para cada oportunidade

| Destino no livro | Qtde | Registros |
|---|---:|---|
| livro novo | 34 | #2, #3, #4, #7, #10, #12, #34, #37, #38, #42, #48, #57, #58, #59, #60, #63, #90, #103, #107, #112, #129, #131, #133, #144, #153, #162, #163, #165, #167, #207 e mais 4 |
| livro existente atualizado (léxico, restrições, checklist, edição) | 70 | #18, #19, #22, #23, #24, #25, #26, #28, #32, #45, #46, #49, #50, #51, #52, #54, #64, #66, #67, #71, #86, #87, #99, #105, #106, #115, #116, #117, #118, #119 e mais 40 |
| não vira livro agora: ato acessório sem o livro do edital identificado — entra como edição quando o livro existir (achado novo desse tipo vai a `pendentes_das_restricoes`) | 13 | #5, #31, #36, #40, #41, #56, #62, #122, #124, #125, #130, #177, #223 |
| nada a criar: a oportunidade já está no livro do registro original (duplicata) | 9 | #43, #55, #78, #88, #89, #102, #134, #181, #217 |
| não vira livro: sem fonte oficial confirmada; os que têm município ficam na semente (`aguardar`) e a Fonte C do PNCP os procura | 32 | #1, #9, #13, #15, #16, #29, #30, #33, #35, #61, #85, #91, #92, #93, #94, #95, #96, #98, #101, #108, #111, #141, #154, #183, #189, #202, #203, #205, #208, #214 e mais 2 |
| NÃO APLICA com livro já existente — vai à curadoria (não é apagado) | 68 | #14, #17, #20, #21, #27, #44, #47, #53, #68, #69, #70, #72, #73, #74, #75, #76, #77, #79, #81, #82, #83, #84, #97, #100, #104, #109, #110, #113, #114, #121 e mais 38 |
| NÃO APLICA sem livro — veto, não vira livro | 12 | #6, #8, #11, #39, #65, #80, #123, #126, #132, #164, #174, #201 |

Dos 32 que aguardam a fonte, 22 têm município e estão na fila da Fonte C; os demais dependem de leitura humana.

Fonte dos livros do parecer: PNCP 55 · diário/página oficial, não localizado no PNCP em 02/10: 40 · página oficial (estadual, nacional, privado): 9.

**Como cada livro passa a ser (regra alterada):** o livro guarda o bloco `busca` — *léxico* (termos, número do edital, município, UF, consulta e chave PNCP) e *restrições* (código e efeito de cada regra que vale para ele: vetos NA-01…08, prazo DI-03 = estado, ato acessório DI-04 = edição, duplicata DI-08 = junção, e os enquadramentos EN-01/02/03 com o motivo). Uma regra que casaria com o próprio livro fica *suspensa* e vai à curadoria. O achado de um livro é julgado pelas restrições **dele**; o vetado fica registrado no catálogo, nada se perde. Detalhes, efeitos e um exemplo real no arquivo de atualização dos livros.

## 7. Os aptos para a associação (ordem de ação)

**#184 — Diário Oficial de Goiânia (GO) 2026-09-25 — "edital de chamamento público" associação** · Goiânia/GO · regra AP-01 · prazo: 2026-10-26 · livro: existe · evidência: edital lido ao vivo (Diário Oficial de Goiânia 25/09)

Goiânia/SEGENP — Chamamento Público nº 001/2026 "Natal no Parque – A Magia de Brincar" (Lei 13.019): termo de colaboração com OSC, valor máximo R$ 5.000.000,00; protocolo único até 26/10/2026, resultado definitivo em 06/11/2026. Exige ≥ 1 ano de CNPJ ativo (a entidade tem 39 anos de CNPJ) e experiência prévia em objeto semelhante (eventos culturais). Edital lido no Diário Oficial de 25/09/2026 (págs. 6–17). Pendência: o portal da Prefeitura ainda não publica página própria — conferir com a SEGENP.

**#199 — Goiás Social aumenta repasse do Auxílio Nutricional às entidades filantrópicas** · GO · regra AP-03 · prazo: fluxo contínuo (até 08/2027) · livro: existe · evidência: validação anterior (27–29/09) + dados do painel

SEDS/GO — Credenciamento nº 001/2026 em fluxo contínuo (12 meses a partir de 27/08/2026) para OSC atuantes em Goiás (Auxílio Nutricional e/ou Água e Energia); sem data-limite. Conferir no edital se o público atendido (entidades que acolhem/atendem pessoas em vulnerabilidade) abrange a atividade da associação.

**#187 — Editais de Destinação de Recursos ou Bens** · GO · regra AP-03 · prazo: recorrente (cada edital ≈ 5 dias; 9282.2026 vencido/no limite) · livro: existe · evidência: validação anterior (27–29/09) + dados do painel

MPT/PRT-18 (Goiás) — página permanente de editais de destinação de recursos de TAC (fonte recorrente, validada em 29/09). O edital em curso (9282.2026, R$ 150.000,00, publicado em 25/09, prazo de 5 dias) já está vencido ou vence hoje; o edital anterior (8927.2026) também encerrou. Valor da fonte: monitorar a página e manter projeto social pronto para indicação a cada novo edital.

**#86 — Como Solicitar uma Doação** · nacional · regra AP-03 · prazo: fluxo contínuo · livro: existe · evidência: validação anterior (27–29/09) + dados do painel

Instituto Clima e Sociedade (iCS) — recebe propostas espontâneas o ano todo (fluxo contínuo), nacional. Aderência limitada à agenda de clima/meio ambiente; esforço baixo para enviar consulta.

### Natal no Parque (#184): o que a proposta precisa conter e o que decidir

1. Projeto técnico e plano de trabalho alinhados ao objeto — celebração natalina gratuita com lazer, cultura e entretenimento, produção cenográfica e decoração temática, planejamento técnico/operacional e gestão de riscos.
2. Comprovação de ≥ 1 ano de CNPJ ativo (a associação tem CNPJ desde 1987); em rede, o edital exige 5 anos — a associação cumpre.
3. Comprovação de experiência prévia em objeto semelhante (eventos culturais comunitários: fotos, listas de presença, relatórios, cartas de órgãos parceiros).
4. Capacidade técnica, operacional e cenográfica: própria ou por rede com produtora/parceiros — decisão de negócio.
5. Declarações (impedimentos, CADIN estadual, dirigentes, vedações da Lei 13.019) e regularidade fiscal, trabalhista e contábil. Pendentes no perfil: estatuto atualizado, ata de eleição vigente, certidões e comprovação das utilidades públicas.
6. Orçamento detalhado dentro do teto de R$ 5 milhões, com cronograma e plano de prestação de contas.
7. Calendário legal: esclarecimentos até 15/10, impugnação até 19/10, protocolo até 26/10, avaliação 27/10, recursos 29/10 a 05/11, resultado definitivo 06/11/2026.

**Perguntas para melhorar as chances:** (a) a entidade já realizou evento natalino/comunitário de porte, com comprovação? (b) há produtora ou cenografia disposta a atuar em rede, e com que contrato? (c) estatuto e ata estão regulares e registrados? (d) há capacidade de pré-financiar a execução até o repasse? (e) concorrer ao teto de R$ 5 mi ou a proposta de menor escala?

## 8. Conselho de 7 lentes

Composição (perfis, sem nomes reais): ministro(a) de tribunal superior processualista; doutrinador(a) de direito administrativo e parcerias (Lei 13.019); advogado(a) pós-doutor(a) em direito do terceiro setor; ministro(a) de corte de contas; doutrinador(a) de direito tributário das entidades sem fins lucrativos; advogado(a) pós-doutor(a) em compliance; magistrado(a) de segunda instância com visão de execução.

1. **Extremamente pessimista (processualista):** "Transformar 101 registros em livros sem ler cada edital multiplica livros com objeto mal extraído (RC-02) e link trocado (RC-03). O livro não pode herdar o erro da coleta: sem o ato lido, o livro nasce com pendência, não com certeza. E 58 de 58 buscas no PNCP sem resultado mostram que o 'agregador único' não existe para MROSC."
2. **Pessimista (administrativista):** "O art. 26 da Lei 13.019 manda divulgar no sítio oficial; o PNCP é da Lei 14.133. Depender só do PNCP perde a maioria dos chamamentos municipais. A regra certa é: PNCP primeiro, diário oficial como fonte do livro quando o PNCP não tiver — é o que a Fonte C e a exceção de abrangência fazem, mas só para os livros do parecer; para o resto do país continua valendo a regra antiga."
3. **Levemente pessimista (tributarista):** "Livro com enquadramento 'restrito' não pode virar ruído no painel da associação. A separação apto × enquadramento precisa chegar ao painel, senão o titular volta a ver 238 'abertas'. E o catálogo cresce cerca de 0,6 MB — aceitável, mas a ser vigiado."
4. **Neutro (ponderador):** "A mudança é correta e coerente com a arquitetura: a fase 1 (Eldorado) mapeia todas as oportunidades para OSC; a fase 2 (Farol) enquadra por associação. Território passa a ser enquadramento, e a mesma lógica vale para região e especialidade que uma OSC pode cumprir — não para requisito de natureza jurídica (catadores, ILPI), que fica como proposta ao titular. Parâmetros de qualidade: (i) livro novo só para oportunidade para OSC com fonte oficial ou diário; agregador e link de outro município esperam o ato; (ii) cada livro com léxico e restrições, versionados; (iii) regra nunca se volta contra o próprio livro — vai à curadoria; (iv) aptidão só com fonte oficial lida; (v) Fonte C semanal no PNCP. Mitigação: os 68 livros existentes que caíram em veto vão à curadoria, não são apagados."
5. **Levemente otimista (doutrinador de parcerias):** "Os livros de outros municípios são a melhor escola de editais: mostram valores, critérios e calendários de PNAB, CMDCA e assistência em centenas de municípios — matéria-prima para a previsão e para o projeto-base da associação."
6. **Otimista (compliance):** "Cada livro passa a explicar por que aceita ou recusa um achado — rastreabilidade que um filtro central não dava. E a correção de território nos livros do PNCP (de 103 para 62 livros municipais marcados como 'nacional') melhora o painel de todos."
7. **Extremamente otimista (magistrado prático):** "Com o léxico em cada livro, o sistema aprende a reencontrar cada oportunidade na próxima edição — no PNCP, no diário ou no site. A associação ganha um mapa nacional sem perder o foco local: Natal no Parque agora, carteira de editais goianos e nacionais em seguida."

**Decisão final do ponderador:** adotar a classificação v2; priorizar #184, #199 e #187; confirmar #86; criar/atualizar os livros pela semente; gravar léxico e restrições em cada livro; ligar a Fonte C do PNCP; levar à curadoria os livros com veto ou regra suspensa; e decidir (titular) se a exceção de abrangência vale para todo edital de OSC de outro município achado em diário oficial, e não só para os do parecer.

## 9. Blocos de 12 — item a item

Legenda: **Obj** objeto · **Pzo** prazo · **Res** resultado · **Rec** recurso · **Val** valor · **Órg** órgão · **Ter** território · **Esf** esfera · **Req** requisitos · **Anx** anexos · **Dst** destinação · **Áre** área. ● comprovado · ◐ dispensa provável · – dispensado · ○ não comprovado. **Livro:** novo · existe · edição · junta · aguarda · veto · revisar.

### Bloco 01 — itens 1 a 12 (aplicável 6 · dispensável 3 · não aplica 3)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Andradina/SP · Diário Oficial de Andradina (SP) 2026-09-18 — "edital de c | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 2 | Campinas/SP · Diário Oficial de Campinas (SP) 2026-07-31 — "chamamento p | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 3 | Campinas/SP · Diário Oficial de Campinas (SP) 2026-09-11 — "chamamento p | APLICÁVEL | EN-01 +EN-03 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 4 | Iracemápolis/SP · Diário Oficial de Iracemápolis (SP) 2026-08-14 — "edital d | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 5 | Itapeva/SP · Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de cha | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 6 | Macatuba/SP · Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de ch | NÃO APLICA | NA-02 | veto | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ○ |
| 7 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-17 — "edital de  | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 8 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-17 — "edital de  | NÃO APLICA | NA-02 | veto | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ | ○ |
| 9 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-25 — "chamamento | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 10 | Monteiro Lobato/SP · Diário Oficial de Monteiro Lobato (SP) 2026-09-11 — "edita | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 11 | Monteiro Lobato/SP · Diário Oficial de Monteiro Lobato (SP) 2026-09-15 — "edita | NÃO APLICA | NA-06 +DI-08 | veto | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 12 | Valinhos/SP · Diário Oficial de Valinhos (SP) 2026-09-25 — "edital de ch | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |

- **#1** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Andradina/SP — novo edital PNAB com recursos remanescentes (R$ 60.536,52) — Andradina/SP. Buscado no PNCP em 02/10: não localizado.
- **#2** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Campinas/SP — Diário Oficial de Campinas (SP) 2026-07-31 — "chamamento público" "organizações da sociedade civil" — Prefeitura Municipal de Campinas. Buscado no PNCP em 02/10: não localizado.
- **#3** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Campinas/SP — edital 02/2026 acolhimento institucional de crianças — OSC (Campinas/SP). Buscado no PNCP em 02/10: não localizado.
- **#4** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Iracemápolis/SP — PNAB 008/2026 (Iracemápolis/SP). Buscado no PNCP em 02/10: não localizado.
- **#5** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapeva/SP — PNAB 01/2026 Pontos de Cultura — prorrogação das inscrições (Itapeva/SP).
- **#6** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Macatuba/SP — credenciamento de pessoas jurídicas para prestação de serviços de agenciamento de viagens corporativas.
- **#7** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Mogi Guaçu/SP — edital 28/SECULT/2026 Natal Encantado — seleção de OSC (Mogi Guaçu/SP). Buscado no PNCP em 02/10: não localizado.
- **#8** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Mogi Guaçu/SP — REGISTRO DE PREÇOS PELO PERÍODO DE 12 (DOZE) MESES, PARA AQUISIÇÕES FUTURAS DE MATERIAIS DE HIGIENE E LIMPEZA PARA ATENDER A DEMANDA DAS SECRETARIAS MUNICIPAIS DA PREFEIT.
- **#9** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Mogi Guaçu/SP — PNAB 33/2026 subsídio a espaços culturais (Mogi Guaçu/SP). Buscado no PNCP em 02/10: não localizado.
- **#10** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Monteiro Lobato/SP — PNAB 02/SMCT/2026 termo de execução cultural (Monteiro Lobato/SP). Buscado no PNCP em 02/10: não localizado.
- **#11** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Monteiro Lobato/SP — PNAB 03/SMCT/2026 premiação mestres (Monteiro Lobato/SP) — mesma oportunidade de 23222c6d.
- **#12** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Valinhos/SP — edital de chamamento 03/2026 — Secretaria de Desenvolvimento Social (Valinhos/SP); objeto não visível no trecho. Buscado no PNCP em 02/10: não localizado.

### Bloco 02 — itens 13 a 24 (aplicável 5 · dispensável 3 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 13 | Valinhos/SP · Diário Oficial de Valinhos (SP) 2026-09-25 — "edital de ch | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ● |
| 14 | Valparaíso/SP · Diário Oficial de Valparaíso (SP) 2026-08-27 — "edital de  | NÃO APLICA | NA-06 +EN-01 | revisar | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 15 | Valparaíso/SP · Diário Oficial de Valparaíso (SP) 2026-09-16 — "edital de  | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 16 | Ourinhos/SP · Edital Prefeitura de Ourinhos 2026: Saúde | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 17 | SP · Seleção de propostas para a celebração de parceria entre o | NÃO APLICA | NA-02 +DI-03 | revisar | 2026-09-25 (encerrado) | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 18 | Itatinga/SP · MUNICIPIO DE ITATINGA — Seleção de projetos para firmar te | APLICÁVEL | EN-01 | existe | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 19 | Sao Jose Do Rio Preto/SP · MUNICIPIO DE SAO JOSE DO RIO PRETO — O PRESENTE CHAMAMENTO | APLICÁVEL | EN-01 | existe | 2026-10-05 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 20 | Porto Feliz/SP · MUNICIPIO DE PORTO FELIZ — PREMIO CULTURAL COM RECURSOS DA | NÃO APLICA | NA-06 +EN-01 | revisar | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 21 | SP · SECRETARIA MUNICIPAL DE EDUCACAO — Contratação, pelo PODER | NÃO APLICA | NA-02 | revisar | 2026-10-16 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 22 | Ibate/SP · MUNICIPIO DE IBATE — ABERTURA DE EDITAL PARA SELEÇÃO DE PR | APLICÁVEL | EN-01 | existe | 2026-10-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 23 | Jacarei/SP · MUNICIPIO DE JACAREI — CHAMADA PÚBLICA Nº 03/2026 - SEMAPL | APLICÁVEL | EN-01 +EN-03 | existe | 2026-10-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 24 | Barretos/SP · MUNICIPIO DE BARRETOS — contratação de pessoa jurídica (or | APLICÁVEL | EN-01 | existe | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#13** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Valinhos/SP — Atendimento ambulatorial e hospitalar da rede municipal de saúde.
- **#14** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Valparaíso/SP — extrato do edital 002/2026 de premiação (Valparaíso/SP).
- **#15** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Valparaíso/SP — edital CMDCA 001/2026 seleção de propostas de OSC (Valparaíso/SP). Buscado no PNCP em 02/10: não localizado.
- **#16** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Ourinhos/SP — Edital Prefeitura de Ourinhos 2026: Saúde.
- **#17** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SP — Estudo de Impacto da Pandemia COVID-19 em empresas de Indaiatuba.
- **#18** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Itatinga/SP — Seleção de projetos para firmar termo de execução cultural com recursos da política nacional Aldir Blanc de fomento à cultura – PNAB (lei nº 14.399/2022) - Proc. Administ. PNCP: 46634127000163/2026/1974.
- **#19** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Sao Jose Do Rio Preto/SP — O PRESENTE CHAMAMENTO TEM POR OBJETO SELECIONAR 1 (UMA) PESSOA JURÍDICA DE DIREITO PRIVADO, COM OU SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COOPERAÇÃO CULTURAL DE. PNCP: 46588950000180/2026/895.
- **#20** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Porto Feliz/SP — PREMIO CULTURAL COM RECURSOS DA POLITICA NACIONAL ALDIR BLANC DE FOMENTO A CULTURA NO MUNICIPIO DE PORTO FELIZ SP LEI N 14.399 2022. PNCP: 46634481000198/2026/203.
- **#21** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SP — Contratação, pelo PODER CONCEDENTE, representado pela SECRETARIA MUNICIPAL DE EDUCAÇÃO (“CONTRATANTE”), de pessoa jurídica para atuar como VERIFICADOR INDEPENDENTE (“CONT. PNCP: 46392114000125/2026/941.
- **#22** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Ibate/SP — ABERTURA DE EDITAL PARA SELEÇÃO DE PROJETOS CULTURAIS DE ACORDO COM A POLÍTICA NACIONAL ALDIR BLANC.. PNCP: 45355575000165/2026/125.
- **#23** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Jacarei/SP — CHAMADA PÚBLICA Nº 03/2026 - SEMAPLAN- SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL (OSC) PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO VISANDO A ATUAÇÃO VOLTADA A PROTEÇÃO E BEM-. PNCP: 46694139000183/2026/852.
- **#24** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Barretos/SP — contratação de pessoa jurídica (organizações da sociedade civil sem fins lucrativos) para prestação de serviços culturais de produção técnica, sonorização, contratação de. PNCP: 44780609000104/2026/334.

### Bloco 03 — itens 25 a 36 (aplicável 4 · dispensável 7 · não aplica 1)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 25 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO DE SELEÇÃO DE | APLICÁVEL | EN-01 | existe | 2026-12-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 26 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO (OSC’S) DE EX | APLICÁVEL | EN-01 | existe | 2027-03-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 27 | SP · (UO) ESP-CIA.PTA DE TRENS METROPS-CPTM — Credenciamento de | NÃO APLICA | NA-06 | revisar | 2027-05-04 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 28 | Pindorama/SP · MUNICIPIO DE PINDORAMA — CREDENCIAMENTO DE ORGANIZACOES DA | APLICÁVEL | EN-01 | existe | 2027-05-12 | ● | ● | ○ | ○ | ◐ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 29 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO PAR | DISPENSÁVEL | DI-05 +EN-01 | aguarda | 2030-11-25 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 30 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO DE  | DISPENSÁVEL | DI-05 +EN-01 | aguarda | 2030-12-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 31 | Arataca/BA · Diário Oficial de Arataca (BA) 2026-09-23 — "edital de cha | DISPENSÁVEL | DI-04 +EN-01 | edição | 2027-03-12 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 32 | BA · Chamamento Público Nº 005/2026 para Seleção de Projetos pa | DISPENSÁVEL | DI-03 +EN-01 | existe | 2026-09-29 (encerrado) | ● | ● | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 33 | Adustina/BA · Diário Oficial de Adustina (BA) 2026-09-18 — "chamamento p | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ○ |
| 34 | Alcobaça/BA · Diário Oficial de Alcobaça (BA) 2026-08-28 — "edital de ch | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 35 | Canudos/BA · Diário Oficial de Canudos (BA) 2026-08-05 — "edital de cha | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 36 | Canudos/BA · Diário Oficial de Canudos (BA) 2026-09-23 — "edital de cha | DISPENSÁVEL | DI-04 +EN-01,DI-08 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |

- **#25** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Artur Nogueira/SP — CREDENCIAMENTO DE SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSC) PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO PARA A PRESTAÇÃO DE SERVIÇOS PARA ATENDIMENTO A ANIMAIS DE PEQU. PNCP: 45735552000186/2026/3.
- **#26** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Artur Nogueira/SP — CREDENCIAMENTO (OSC’S) DE EXECUÇÃO DE PROJETO ESPORTIVO VOLTADO Á DIFUSÃO DO ESPORTE E LAZER POR MEIO DA MODALIDADE VOLEIBOL, INCLUINDO AÇÕES DE CONTRATURNO ESCOLAR, LAZE. PNCP: 45735552000186/2027/1.
- **#27** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: SP — Credenciamento de associações e/ou cooperativas de catadores de materiais recicláveis para coleta, transporte, fragmentação/trituração e destinação/desfazimento de caixas. PNCP: 71832679000123/2026/64.
- **#28** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Pindorama/SP — CREDENCIAMENTO DE ORGANIZACOES DA SOCIEDADE CIVIL DE PINDORAMA INTERESSADA EM RECEBER DOACAO DE BENS MOVEIS CONSIDERADOS INSERVIVEIS PERTENCENTES AO MUNICIPIO CONSTANTES . PNCP: 45122942000180/2026/248.
- **#29** (PNCP consultado ao vivo em 02/10/2026): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Artur Nogueira/SP — EDITAL DE CREDENCIAMENTO PARA PARCERIA EM REGIME DE COLABORAÇÃO ENTRE A SECRETARIA DE EDUCAÇÃO E ORGANIZAÇÃO DA SOCIEDADE CIVIL. A PARCERIA CONSISTIRÁ NA OFERTA DE ATENDI. PNCP: 45735552000186/2030/4.
- **#30** (PNCP consultado ao vivo em 02/10/2026): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Artur Nogueira/SP — EDITAL DE CREDENCIAMENTO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL (OSC´S) PARA PRESTAÇÃO DE SERVIÇOS EM ATENDIMENTO À DEMANDA DESTA SECRETARIA DE CULTURA NO MUNICÍPIO DE ARTUR N. PNCP: 45735552000186/2030/5.
- **#31** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Arataca/BA — PNAB 02/2026 — prorrogação do cronograma (Arataca/BA).
- **#32** (PNCP consultado ao vivo em 02/10/2026): Fase encerrada/sem inscrições vigentes: BA — seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), com recursos da Política Nacional Aldir Blanc . Buscado no PNCP em 02/10: não localizado.
- **#33** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Adustina/BA — chamamento para credenciar OSC — Programa Integrado (Adustina/BA). Buscado no PNCP em 02/10: não localizado.
- **#34** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Alcobaça/BA — PNAB 002 e 0003/2026 criação de projetos culturais (Alcobaça/BA). Buscado no PNCP em 02/10: não localizado.
- **#35** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Canudos/BA — PNAB 02/2026 termo de execução cultural (Canudos/BA) — mesma oportunidade de b5525976. Buscado no PNCP em 02/10: não localizado.
- **#36** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Canudos/BA — PNAB 02/2026 — alteração de cronograma (Canudos/BA).

### Bloco 04 — itens 37 a 48 (aplicável 6 · dispensável 3 · não aplica 3)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 37 | Inhambupe/BA · Diário Oficial de Inhambupe (BA) 2026-08-12 — "edital de c | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 38 | Ipiaú/BA · Diário Oficial de Ipiaú (BA) 2026-09-17 — "edital de chama | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 39 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-08-21 — "edital de  | NÃO APLICA | NA-06 +EN-01 | veto | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 40 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-09-16 — "edital de  | DISPENSÁVEL | DI-04 +EN-01,NA-02 | edição | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ | ○ |
| 41 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-09-21 — "chamamento | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 42 | Ituaçu/BA · Diário Oficial de Ituaçu (BA) 2026-08-20 — "chamamento púb | APLICÁVEL | EN-01 | novo | — | ● | – | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 43 | Olindina/BA · o Chamamento Público nº 002/2026, destinado à seleção de p | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 44 | BA · COMPANHIA DE PESQUISA DE RECURSOS MINERAIS — Programa de A | NÃO APLICA | NA-03 +DI-03 | revisar | 2026-10-08 (revogado) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 45 | Jaguaripe/BA · MUNICIPIO DE JAGUARIPE — Constitui objeto do presente Edit | APLICÁVEL | EN-01 | existe | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 46 | Olindina/BA · MUNICIPIO DE OLINDINA — o Chamamento Público nº 002/2026,  | APLICÁVEL | EN-01 | existe | 2026-10-13 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 47 | Itagiba/BA · MUNICIPIO DE ITAGIBA — Chamamento Público a seleção de ass | NÃO APLICA | NA-06 | revisar | 2026-10-14 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 48 | Lauro De Freitas/BA · MUNICIPIO DE LAURO DE FREITAS — Concessão de apoio finance | APLICÁVEL | EN-01 | novo | 2026-10-15 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#37** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Inhambupe/BA — edital PNAB de subsídio a culturas populares (Inhambupe/BA). Buscado no PNCP em 02/10: não localizado.
- **#38** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Ipiaú/BA — edital PNAB 01/2026 Virada Cultural (repetição publicada por Mutuípe/BA). Buscado no PNCP em 02/10: não localizado.
- **#39** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Itapetinga/BA — edital 07/2026 apresentação musical MPB — agentes culturais (Itapetinga/BA).
- **#40** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapetinga/BA — retificação de edital de chamamento (educação/cultura, Itapetinga/BA).
- **#41** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapetinga/BA — errata do aviso de chamamento 006/2026 (Itapetinga/BA) — objeto não visível.
- **#42** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Ituaçu/BA — PNAB 003/2026 festividade cultural e religiosa (Ituaçu/BA). Buscado no PNCP em 02/10: não localizado.
- **#43** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #46: Olindina/BA — seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), com recursos da Política Nacional Aldir Blanc 
- **#44** (PNCP consultado ao vivo em 02/10/2026): É seleção de pessoas (estágio/aprendizagem/processo seletivo), não de entidade: BA — Programa de Aprendizagem, com dois Jovens Aprendizes, para atuação junto à Companhia de Pesquisa de Recursos Minerais - CPRM / na Unidade Regional de Salvador, por até se. PNCP: 00091652000189/2026/333.
- **#45** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Jaguaripe/BA — Constitui objeto do presente Edital a seleção de Organização da Sociedade Civil (OSC), regularmente constituída, para celebração de TERMO DE COLABORAÇÃO, em regime de mút. PNCP: 13796289000149/2026/37.
- **#46** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Olindina/BA — o Chamamento Público nº 002/2026, destinado à seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), . PNCP: 13647854000106/2026/74.
- **#47** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Itagiba/BA — Chamamento Público a seleção de associação ou cooperativa de catadores de materiais recicláveis para a CONTRATAÇÃO REMUNERADA da prestação continuada e integrada dos serv. PNCP: 13701966000106/2026/141.
- **#48** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Lauro De Freitas/BA — Concessão de apoio financeiro para execução de projetos culturais, no âmbito da Política Nacional Aldir Blanc de Fomento à Cultura – PNAB, instituída pela Lei Federal nº . PNCP: 13927819000140/2026/143.

### Bloco 05 — itens 49 a 60 (aplicável 9 · dispensável 2 · não aplica 1)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 49 | Santo Antonio De Jesus/BA · MUNICIPIO DE SANTO ANTONIO DE JESUS — Seleção de Organizaç | APLICÁVEL | EN-01 | existe | 2026-11-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 50 | Rio Real/BA · MUNICIPIO DE RIO REAL — EDITAL DE CREDENCIAMENTO Nº 012/20 | APLICÁVEL | EN-01 | existe | 2026-11-28 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 51 | Feira De Santana/BA · MUNICIPIO DE FEIRA DE SANTANA — CHAMAMENTO PÚBLICO QUE TEM | APLICÁVEL | EN-01 | existe | 2026-12-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 52 | Feira De Santana/BA · MUNICIPIO DE FEIRA DE SANTANA — TERMO DE FOMENTO QUE ENTRE | APLICÁVEL | EN-01 | existe | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 53 | Olindina/BA · MUNICIPIO DE OLINDINA — Chamamento Público é o credenciame | NÃO APLICA | NA-06 +EN-01 | revisar | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 54 | BA · FUNDO MUNICIPAL DE SAUDE DE JEQUIE — 1.1. Contratação de O | APLICÁVEL | EN-01 +EN-03 | existe | 2027-09-14 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 55 | PR · Chamamento Público para firmar Termo de Colaboração com Or | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 56 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-11 — "edital de c | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 57 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-16 — "edital de c | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 58 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-17 — "edital de c | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ○ |
| 59 | Londrina/PR · Diário Oficial de Londrina (PR) 2026-09-18 — "edital de ch | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 60 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-08-21 — "edital de cha | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |

- **#49** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Santo Antonio De Jesus/BA — Seleção de Organização da Sociedade Civil – OSC para a celebração de TERMO DE COLABORAÇÃO, em regime de mútua cooperação, na forma e nas condições estabelecidas neste Edi. PNCP: 13825476000103/2026/139.
- **#50** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Rio Real/BA — EDITAL DE CREDENCIAMENTO Nº 012/2026, PARA FINS DE CREDENCIAR ORGANIZAÇÕES DA SOCIEDADE CIVIL PARA EVENTUAL CELEBRAÇÃO DE TERMO DE COLABORAÇÃO OU TERMO DE FOMENTO, DE ACO. PNCP: 15088800000183/2026/109.
- **#51** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Feira De Santana/BA — CHAMAMENTO PÚBLICO QUE TEM POR FINALIDADE A SELEÇÃO DE PROPOSTAS DE INSTITUIÇÃO DE LONGA PERMANENCIA PARA IDOSOS E ORGANIZAÇÕES DA SOCIEDADE CIVIL DE ATENDIMENTO, PARA EX. PNCP: 14043574000151/2026/139.
- **#52** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Feira De Santana/BA — TERMO DE FOMENTO QUE ENTRE SI CELEBRAM A SECRETARIA MUNICIPAL DA EDUCAÇÃO DE FEIRA DE SANTANA E A ORGANIZAÇÃO DA SOCIEDADE CIVIL SELECIONADA POR MEIO DE CHAMAMENTO PÚBLIC. PNCP: 14043574000151/2026/327.
- **#53** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Olindina/BA — Chamamento Público é o credenciamento de artistas, grupos e coletivos culturais para compor a programação dos eventos realizados pela SECELT no exercício de 2026, nas seg. PNCP: 13647854000106/2026/33.
- **#54** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): BA — 1.1. Contratação de Organização da Sociedade Civil (OSC) para prestação de serviços de reabilitação intelectual, para crianças, jovens e adultos com deficiência intelectu. PNCP: 09436466000109/2026/38.
- **#55** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #66: PR — concessão de apoio da administração pública municipal para a execução de atividade tipificada como Serviço de Educação Básica de Atendimento Educacionais Especializado pa
- **#56** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Arapongas/PR — Programa Jovens Araponguenses pelo Clima (YCAF) — retificação de cronograma.
- **#57** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Arapongas/PR — edital 050/2026 vagas remanescentes "João de Barro" — ações formativas (Arapongas/PR). Buscado no PNCP em 02/10: não localizado.
- **#58** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Arapongas/PR — edital 052/2026 vagas remanescentes "Som do Rouxinol" — retificação (Arapongas/PR). Buscado no PNCP em 02/10: não localizado.
- **#59** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Londrina/PR — edital 004/2026 termo de execução cultural (Londrina/PR). Buscado no PNCP em 02/10: não localizado.
- **#60** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Pinhais/PR — PNAB 050/2026 apoio a projetos de fomento (Pinhais/PR). Buscado no PNCP em 02/10: não localizado.

### Bloco 06 — itens 61 a 72 (aplicável 5 · dispensável 2 · não aplica 5)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 61 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-08-28 — "chamamento pú | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 62 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-09-23 — "edital de cha | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 63 | Primeiro de Maio/PR · Diário Oficial de Primeiro de Maio (PR) 2026-08-28 — "edit | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 64 | Cafelandia/PR · MUNICIPIO DE CAFELANDIA — CONSTITUI OBJETO DO PRESENTE CHA | APLICÁVEL | EN-01 | existe | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 65 | PR · FUNDACAO ESTATAL DE ATENCAO EM SAUDE DO ESTADO DO PARANA - | NÃO APLICA | NA-02 | veto | 2026-10-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 66 | Guaira/PR · MUNICIPIO DE GUAIRA — Chamamento Público para firmar Termo | APLICÁVEL | EN-01 | existe | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 67 | Cafelandia/PR · MUNICIPIO DE CAFELANDIA — SELEÇÃO DE ORGANIZAÇÕES DA SOCIE | APLICÁVEL | EN-01 | existe | 2026-10-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 68 | Ivaipora/PR · MUNICIPIO DE IVAIPORA — PREMIAÇÃO POR TRAJETÓRIA, PREVISTO | NÃO APLICA | NA-06 +EN-01 | revisar | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 69 | PR · DEFENSORIA PUBLICA DO ESTADO DO PARANA — O objeto do prese | NÃO APLICA | NA-06 | revisar | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 70 | Campina Da Lagoa/PR · MUNICIPIO DE CAMPINA DA LAGOA — Chamamento Público de Inst | NÃO APLICA | NA-06 | revisar | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 71 | Clevelandia/PR · MUNICIPIO DE CLEVELANDIA — Chamamento Público destinado à  | APLICÁVEL | EN-01 | existe | 2027-02-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 72 | Quatigua/PR · MUNICIPIO DE QUATIGUA — Credenciamento para seleção de ass | NÃO APLICA | NA-06 | revisar | 2027-04-22 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#61** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Pinhais/PR — PNAB 051/2026 subsídio a espaços (Pinhais/PR). Buscado no PNCP em 02/10: não localizado.
- **#62** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Pinhais/PR — PNAB 51/2026 — reabertura do prazo de inscrições (Pinhais/PR).
- **#63** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Primeiro de Maio/PR — PNAB 001/2026 ciclo II fomento direto PF/PJ (Primeiro de Maio/PR). Buscado no PNCP em 02/10: não localizado.
- **#64** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Cafelandia/PR — CONSTITUI OBJETO DO PRESENTE CHAMAMENTO PÚBLICO A SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL – OSC, SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO COM O MUNI. PNCP: 78121878000172/2026/196.
- **#65** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): PR — Contratação de entidade qualificada em formação técnico-profissional metódica, habilitada junto ao Ministério do Trabalho e Emprego, para prestação de serviços de aprendi. PNCP: 24039073000155/2026/1160.
- **#66** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Guaira/PR — Chamamento Público para firmar Termo de Colaboração com Organização da Sociedade Civil, sem fins lucrativos, que execute Serviço de Educação Básica e de Atendimento Educa. PNCP: 77857183000190/2026/288.
- **#67** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Cafelandia/PR — SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL - OSCS, SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO, NOS TERMOS DA LEI FEDERAL Nº 13.019/2014, VISANDO À EXECU. PNCP: 78121878000172/2026/205.
- **#68** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Ivaipora/PR — PREMIAÇÃO POR TRAJETÓRIA, PREVISTO EM PLANO DE AÇÃO DA PNAB, EM ATENDIMENTO ÀS NECESSIDADES DA SECRETARIA MUNICIPAL DE CULTURA. PNCP: 75741330000137/2026/334.
- **#69** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PR — O objeto do presente credenciamento selecionar associações e/ou cooperativas de catadores de materiais recicláveis para o recolhimento e a destinação de resíduos recicláv. PNCP: 13950733000139/2026/2.
- **#70** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Campina Da Lagoa/PR — Chamamento Público de Instituições/Associações Estudantis e de Acadêmicos, sem ?ns lucrativos, regularmente constituídas, localizadas no Município de Campina da Lagoa, e . PNCP: 76950070000172/2026/25.
- **#71** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Clevelandia/PR — Chamamento Público destinado à seleção de projetos de Organizações da Sociedade Civil - OSCs, regularmente registradas e atualizadas junto ao Conselho Municipal dos Direi. PNCP: 76161199000100/2026/8.
- **#72** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Quatigua/PR — Credenciamento para seleção de associação de estudantes regularmente constituída, sem fins lucrativos, para a cessão de uso, a título gratuito e precário, de 01 (um) veíc. PNCP: 76966852000108/2026/17.

### Bloco 07 — itens 73 a 84 (aplicável 0 · dispensável 1 · não aplica 11)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 73 | Castro/PR · MUNICIPIO DE CASTRO — CHAMAMENTO PÚBLICO PARA FINS DE CRED | NÃO APLICA | NA-06 | revisar | 2027-06-11 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 74 | Ceu Azul/PR · MUNICIPIO DE CEU AZUL — CREDENCIAMENTO de Instituições de  | NÃO APLICA | NA-06 | revisar | 2027-06-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 75 | Guaira/PR · MUNICIPIO DE GUAIRA — Credenciamento de cooperativas de cr | NÃO APLICA | NA-06 | revisar | 2027-07-21 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 76 | Rio Branco Do Sul/PR · MUNICIPIO DE RIO BRANCO DO SUL — Credenciamento de associa | NÃO APLICA | NA-06 | revisar | 2028-03-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 77 | Telemaco Borba/PR · MUNICIPIO DE TELEMACO BORBA — Credenciamento de cooperativ | NÃO APLICA | NA-06 | revisar | 2030-08-16 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 78 | Simão Dias/SE · Diário Oficial de Simão Dias (SE) 2026-08-17 — "edital de  | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ● | ○ | ● | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 79 | DF · COMPANHIA NACIONAL DE ABASTECIMENTO — Contratação de entid | NÃO APLICA | NA-02 | revisar | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 80 | DF · SERVICO DE LIMPEZA URBANA — Credenciamento de Cooperativas | NÃO APLICA | NA-06 | veto | 2027-03-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 81 | DF · DNIT-DEPARTAMENTO NACIONAL DE INFRAEST DE TRANSPORTES — Se | NÃO APLICA | NA-06 | revisar | 2028-09-22 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 82 | DF · TRIBUNAL SUPERIOR DO TRABALHO — Seleção de associações e c | NÃO APLICA | NA-06 | revisar | 2028-12-04 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 83 | nacional · Delfina Foundation promove residência em Londres para arti | NÃO APLICA | NA-08 | revisar | 2026-10-04 | ● | ● | ○ | ◐ | – | ● | ● | ● | ● | ● | ● | ○ |
| 84 | nacional · Braunschweig Projects 2027/2028 | NÃO APLICA | NA-08 | revisar | — | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |

- **#73** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Castro/PR — CHAMAMENTO PÚBLICO PARA FINS DE CREDENCIAMENTO DE COOPERATIVA OU ASSOCIAÇÃO OU DA INICI­ATIVA PRIVADA DE MATERIAIS RECICLÁVEIS ESPECIALIZADA NA EXECUÇÃO DE SERVIÇOS DE RE. PNCP: 77001311000108/2026/307.
- **#74** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Ceu Azul/PR — CREDENCIAMENTO de Instituições de Longa Permanência para Idosos (ILPIs), que tenham interesse em prestar serviços de acolhimento institucional continuado para pessoas ido. PNCP: 76206473000101/2026/130.
- **#75** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Guaira/PR — Credenciamento de cooperativas de crédito autorizadas a funcionar pelo Banco Central do Brasil e legalmente aptas à captação de recursos municipais, com dependência insta. PNCP: 77857183000190/2026/233.
- **#76** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Rio Branco Do Sul/PR — Credenciamento de associações e/ou cooperativas de catadores de materiais recicláveis para a prestação de serviços de processamento e destinação adequada de resíduos sóli. PNCP: 76105576000185/2026/39.
- **#77** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Telemaco Borba/PR — Credenciamento de cooperativas e associações de catadores de materiais recicláveis, bem como organizações não governamentais (ongs) sem fins lucrativos, para a coleta, re. PNCP: 76170240000104/2027/3.
- **#78** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #224: Simão Dias/SE — Apoio à realização de projetos culturais em âmbito nacional.
- **#79** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): DF — Contratação de entidade sem fins lucrativos, inscrita e aprovada no Cadastro Nacional de Aprendizagem, com capacidade técnica e administrativa e que tenha por objetivo a . PNCP: 26461699000180/2026/323.
- **#80** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Credenciamento de Cooperativas/Associações de Catadores, constituídas exclusivamente por pessoas físicas de baixa renda, para a prestação de serviços de manejo de resíduo. PNCP: 01567525000176/2026/3.
- **#81** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Seleção de associações e/ou cooperativas de catadores de materiais recicláveis, cadastradas e habilitadas no Sistema Nacional de Informações sobre a Gestão de Resíduos Só. PNCP: 04892707000100/2026/136.
- **#82** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Seleção de associações e cooperativas de catadores de materiais recicláveis aptas a recolherem os resíduos destinados à reciclagem produzidos pelo TST.. PNCP: 00509968000148/2026/83.
- **#83** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — residência em Londres para artistas visuais de Portugal e de Países Africanos de Língua Portuguesa.
- **#84** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — Residências artísticas em Alemanha.

### Bloco 08 — itens 85 a 96 (aplicável 2 · dispensável 10 · não aplica 0)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 85 | Cajuru (SP/MG) · Chamamento Público 1/2026: Prefeitura de Cajuru (Educação) | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ● |
| 86 | nacional · Como Solicitar uma Doação | APLICÁVEL (apto) | AP-03 | existe | fluxo contínuo | ● | ● | – | – | – | ● | ● | ● | ● | ● | ● | ● |
| 87 | nacional · Dia de Doar abre inscrições para edital que oferece R$ 2,4 | DISPENSÁVEL | DI-03 | existe | edição 2024 (encerrada) (encer | ● | – | ● | ○ | ● | ● | ● | ● | ○ | ● | ● | – |
| 88 | Itapeva/SP · Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de cha | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 89 | Macatuba/SP · Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de ch | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 90 | Potengi/CE · EDITAL DE SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS, AMBIENTES E | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 91 | nacional · Edital Ambev 2026: R$ 67M para Cultura e Esporte — Ambev | DISPENSÁVEL | DI-05 +EN-03 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 92 | Balsas/MA · Edital Balsas 2026: Guia de Captação e Inscrição — Prefeit | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 93 | CAU/PR (Paraná) · Edital CAU/PR 2026: Captação e Regras da Chamada Pública | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ○ |
| 94 | Curitiba/PR · Edital ContraFluxo 2026: Filme para ONGs de Curitiba | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 95 | Itagibá/BA · Edital Itagibá 2026: Guia de Captação e Inscrições | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 96 | Tauá/CE · Edital Tauá 2026: Guia de Captação e Inscrição | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |

- **#85** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Cajuru (SP/MG) — Chamamento Público 1/2026: Prefeitura de Cajuru (Educação).
- **#86** (validação anterior (27–29/09) + dados do painel): Instituto Clima e Sociedade (iCS) — recebe propostas espontâneas o ano todo (fluxo contínuo), nacional. Aderência limitada à agenda de clima/meio ambiente; esforço baixo para enviar consulta.
- **#87** (página oficial lida ao vivo): Dia de Doar/ABCR — edital de Apoio à Filantropia Comunitária (R$ 40 mil para 40 campanhas, R$ 1.000 cada); o painel registra resultado em 24/10/2024, ou seja, é a edição de 2024 (a notícia diz "4º edital" e o painel intitula "R$ 2,4 mil"). Edital da edição anterior = prazo encerrado. Acompanhar a abertura da próxima edição (a ação é anual, em torno de outubro/dezembro).
- **#88** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #5: Itapeva/SP — Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de chamamento público" associação — Prefeitura Municipal de Itapeva
- **#89** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #6: Macatuba/SP — Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de chamamento público" associação — Prefeitura Municipal de Macatuba/SP
- **#90** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Potengi/CE — EDITAL DE SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS, AMBIENTES E INICIATIVAS ARTÍSTICO-CULTURAIS. Buscado no PNCP em 02/10: não localizado.
- **#91** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — Edital Ambev 2026: R$ 67M para Cultura e Esporte — Ambev.
- **#92** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Balsas/MA — Edital Balsas 2026: Guia de Captação e Inscrição — Prefeitura Municipal de Balsas. Buscado no PNCP em 02/10: não localizado.
- **#93** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: CAU/PR (Paraná) — Edital CAU/PR 2026: Captação e Regras da Chamada Pública. Buscado no PNCP em 02/10: não localizado.
- **#94** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Curitiba/PR — Edital ContraFluxo 2026: Filme para ONGs de Curitiba. Buscado no PNCP em 02/10: não localizado.
- **#95** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Itagibá/BA — Edital Itagibá 2026: Guia de Captação e Inscrições. Buscado no PNCP em 02/10: não localizado.
- **#96** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Tauá/CE — Edital Tauá 2026: Guia de Captação e Inscrição. Buscado no PNCP em 02/10: não localizado.

### Bloco 09 — itens 97 a 108 (aplicável 5 · dispensável 4 · não aplica 3)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 97 | nacional · Gife cria fundo para incentivar doacoes | NÃO APLICA | NA-04 | revisar | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 98 | nacional · Mover se na web lanca chamada para projetos de inovacao te | DISPENSÁVEL | DI-05 | aguarda | — | ● | – | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 99 | Norte e Nordeste · ONGs e coletivos periféricos do Nordeste podem se inscreve | APLICÁVEL | EN-02 +EN-01 | existe | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ● | ○ |
| 100 | nacional · Prêmio nacional da Enap oferece até R$ 20 mil para iniciat | NÃO APLICA | NA-05 | revisar | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ● | ○ |
| 101 | nacional · Seleção de organização da sociedade civil – osc, sem fins  | DISPENSÁVEL | DI-05 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 102 | Itatinga/SP · Seleção de projetos para firmar termo de execução cultural | DISPENSÁVEL | DI-08 +EN-01 | junta | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 103 | ICISMEP (consórcio, MG) · 1.1. Constitui objeto do presente edital o credenciamento  | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 104 | nacional · Contratação de prestação de serviço especializado de Produ | NÃO APLICA | NA-02 | revisar | 2026-10-06 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 105 | Espírito Santo (mapa cultural ES) · EDITAL DE CHAMAMENTO PÚBLICO Nº 16 /2026 - SELEÇÃO DE PROJ | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 106 | Ceará (mapa cultural CE) · EDITAL DE CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS - PN | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 107 | Sobral/CE · EDITAL DE FOMENTO AS LINGUAGENS ARTISTICAS DO MUNICIPIO DE | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 108 | nacional · Editais de Fomento a Ações de Prevenção e Combate de Incên | DISPENSÁVEL | DI-05 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

- **#97** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: nacional — apoiar soluções inovadoras que criem condições favoráveis tanto para facilitar a conexão entre doadores e donatários, como para estreitar e aprofundar as relações de conf.
- **#98** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — projetos de inovação tecnológica que tenham potencial para impactar positivamente problemas sociais no Brasil.
- **#99** (página oficial lida ao vivo): BNDES Periferias Fortes — seleção de parceiro executor para territórios do Norte e Nordeste (investimento de até R$ 17,5 mi por parceiro; repasse de R$ 100–300 mil às OSPs capacitadas). Página lida ao vivo. Livro próprio (programa nacional do BNDES, útil para a previsão de novas chamadas); enquadramento: Goiás fora da área desta chamada.
- **#100** (dados do painel (sem fonte oficial confirmada)): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: nacional — Prêmio nacional da Enap oferece até R$ 20 mil para iniciativas que protegem crianças e adolescentes em situação de rua —.
- **#101** (dados do painel (sem fonte oficial confirmada)): Registro cujo link oficial é um placeholder (x.gov.br/edital): não há como comprovar o edital; vai para quarentena (RC-05) e só volta se a fonte real for localizada.
- **#102** (PNCP consultado ao vivo em 02/10/2026): Mesma oportunidade do registro #18: Itatinga/SP — Seleção de projetos para firmar termo de execução cultural com recursos da política nacional Aldir Blanc de fomento à cultura
- **#103** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): ICISMEP (consórcio, MG) — 1.1. Constitui objeto do presente edital o credenciamento de Instituições reconhecidas como Organizações da Sociedade Civil (OSC), nos moldes definidos pela Lei Federal n. Buscado no PNCP em 02/10: não localizado.
- **#104** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): nacional — Contratação de prestação de serviço especializado de Produtor Cultural para a Implementação e Curadoria… — ESTADO DA BAHIA. PNCP: 13937032000160/2026/2273.
- **#105** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Espírito Santo (mapa cultural ES) — EDITAL DE CHAMAMENTO PÚBLICO Nº 16 /2026 - SELEÇÃO DE PROJETOS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS - PNAB. Buscado no PNCP em 02/10: não localizado.
- **#106** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Ceará (mapa cultural CE) — EDITAL DE CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS - PNAB. Buscado no PNCP em 02/10: não localizado.
- **#107** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Sobral/CE — EDITAL DE FOMENTO AS LINGUAGENS ARTISTICAS DO MUNICIPIO DE SOBRAL – POLÍTICA NACIONAL ALDIR BLANC DE FOMENTO À CULTURA – PNAB. Buscado no PNCP em 02/10: não localizado.
- **#108** (dados do painel (sem fonte oficial confirmada)): MMA/FNMA — notícia sobre editais de R$ 34,5 mi para prevenção e combate a incêndios florestais. Não há objeto, prazo, público-alvo nem edital confirmados (a página do MMA não abriu para leitura): sem fonte oficial do edital não pode ser aplicável. PENDÊNCIA PRIORITÁRIA: localizar o edital do FNMA (OSC é público típico do fundo; o Cerrado é bioma goiano — hipótese a confirmar, não dado).

### Bloco 10 — itens 109 a 120 (aplicável 7 · dispensável 1 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 109 | litoral SP/PR/SC · Edital Fundação Grupo Boticário Litoral SP PR SC 2026 | NÃO APLICA | NA-06 | revisar | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 110 | nacional · Edital Marinha 2026: Guia de Permuta e Imóveis Ociosos | NÃO APLICA | NA-02 | revisar | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 111 | nacional · Edital Zurich Seguros 2026: Captação via Incentivo | DISPENSÁVEL | DI-05 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 112 | Quatá/SP · Edital de Credenciamento de Organizações da Sociedade Civi | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 113 | nacional · Edital nº. 4/2026 - Processo de chamamento público para el | NÃO APLICA | NA-07 | revisar | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 114 | nacional · Residência Institut français × Cité internationale des art | NÃO APLICA | NA-08 | revisar | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 115 | Guaramiranga/CE · Secretaria de Cultura de Guaramiranga | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 116 | São Paulo (instituições culturais de SP) · Sonhar o Mundo 2026 abre inscrições para instituições cult | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 117 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Ci | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 118 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - Ap | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 119 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 - Ar | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 120 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - Of | APLICÁVEL | EN-01 | existe | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

- **#109** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: litoral SP/PR/SC — Edital Fundação Grupo Boticário Litoral SP PR SC 2026.
- **#110** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): nacional — Edital Marinha 2026: Guia de Permuta e Imóveis Ociosos.
- **#111** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — Edital Zurich Seguros 2026: Captação via Incentivo.
- **#112** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Quatá/SP — Edital de Credenciamento de Organizações da Sociedade Civil - OSC Nº. 02/ 2026. Buscado no PNCP em 02/10: não localizado.
- **#113** (dados do painel (sem fonte oficial confirmada)): MDH — chamamento para eleição de organizações de conselho nacional: vaga em colegiado, não fomento.
- **#114** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — Residência Institut français × Cité internationale des arts 2027 — Paris, aberta a qualquer nacionalidade.
- **#115** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Guaramiranga/CE — Secretaria de Cultura de Guaramiranga. Buscado no PNCP em 02/10: não localizado.
- **#116** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): São Paulo (instituições culturais de SP) — Sonhar o Mundo 2026 abre inscrições para instituições culturais de São Paulo. Buscado no PNCP em 02/10: não localizado.
- **#117** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Circulação e Intercâmbio de Grupos. Buscado no PNCP em 02/10: não localizado.
- **#118** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - Apoio a Projetos Contínuos. Buscado no PNCP em 02/10: não localizado.
- **#119** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 - Artistas da Terra e Tocadores de Concertina. Buscado no PNCP em 02/10: não localizado.
- **#120** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - Oficinas de Artesanato. Buscado no PNCP em 02/10: não localizado.

### Bloco 11 — itens 121 a 132 (aplicável 4 · dispensável 4 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 121 | local/regional (município não identificado) · “CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ARTISTAS LOCAIS | NÃO APLICA | NA-06 +EN-01 | revisar | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 122 | Campo Alegre/AL · Diário Oficial de Campo Alegre (AL) 2026-08-13 — "edital d | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 123 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-08-24 — "edital de cham | NÃO APLICA | NA-06 +EN-01 | veto | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 124 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-09-16 — "edital de cham | DISPENSÁVEL | DI-04 +EN-01,NA-06 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ○ |
| 125 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-09-25 — "edital de cham | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 126 | Viçosa/AL · Diário Oficial de Viçosa (AL) 2026-08-26 — "edital de cham | NÃO APLICA | NA-06 +EN-01 | veto | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 127 | AL · AGENCIA MUNICIPAL DE REGULACAO DE SERVICOS DELEGADOS- ARSE | APLICÁVEL | EN-01 +EN-03 | existe | 2026-12-30 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 128 | Joaquim Gomes/AL · MUNICIPIO DE JOAQUIM GOMES — CREDENCIAMENTO SAÚDE, PARA FI | APLICÁVEL | EN-01 +EN-03 | existe | 2027-08-20 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 129 | Igaci/AL · Diário Oficial de Igaci (AL) 2026-09-22 — "chamamento públ | APLICÁVEL | EN-01 +EN-03 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ |
| 130 | Igaci/AL · Diário Oficial de Igaci (AL) 2026-09-23 — "chamamento públ | DISPENSÁVEL | DI-04 +EN-01,DI-08 | edição | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ |
| 131 | CE · EDITAL OCUPA VARJOTA 2026 DE APOIO A AÇÕES CULTURAIS E FOR | APLICÁVEL | EN-01 | novo | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 132 | CE · Chamamento Público PMI/SMS Iguatu 2026: Guia Completo | NÃO APLICA | NA-02 | veto | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |

- **#121** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: local/regional (município não identificado) — “CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ARTISTAS LOCAIS/REGIONAIS”, mediante pagamento de cachê, com base… — MUNICIPIO DE ALMIRANTE TAMANDARE. PNCP: 76105659000174/2026/227.
- **#122** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Campo Alegre/AL — PNAB 02/2026 ciclo 2 — errata (Campo Alegre/AL).
- **#123** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Satuba/AL — PNAB 03/2026 premiação cultural (Satuba/AL) — mesma oportunidade de c6941930.
- **#124** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Satuba/AL — PNAB 03/2026 premiação cultural — despacho (Satuba/AL).
- **#125** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Satuba/AL — PNAB 03/2026 — 2ª retificação de cronograma (Satuba/AL) — mesma oportunidade de c6941930.
- **#126** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Viçosa/AL — PNAB 003/2026 premiação de agentes culturais — alteração de cronograma (Viçosa/AL).
- **#127** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): AL — CHAMAMENTO PÚBLICO PARA A SELEÇÃO DE UMA ORGANIZAÇÃO DA SOCIEDADE CIVIL - OSC INTERESSADA EM FIRMAR TERMO DE COLABORAÇÃO COM A PREFEITURA MUNICIPAL DE MACEIÓ PARA A IMPLA. PNCP: 26981455000129/2026/51.
- **#128** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Joaquim Gomes/AL — CREDENCIAMENTO SAÚDE, PARA FINS DE SELECIONAR ORGANIZAÇÕES DA SOCIEDADE CIVIL PARA EVENTUAL CELEBRAÇÃO DE TERMO DE COLABORAÇÃO OU TERMO DE FOMENTO, DE ACORDO COM A LEI FE. PNCP: 12262739000150/2026/43.
- **#129** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Igaci/AL — aviso de credenciamento de OSC da área da saúde (Igaci/AL). Buscado no PNCP em 02/10: não localizado.
- **#130** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Igaci/AL — comissão do credenciamento de OSC da saúde (Igaci/AL) — mesma oportunidade de 512dd2f6.
- **#131** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): CE — SELEÇÃO DE PROJETOS DE MANUTENÇÃO DE ATIVIDADES DE FORMAÇÃO ARTÍSTICOS-CULTURIAS E NOVAS INICIATIVAS ARTÍSTICAS, PESQUISAS, ESTREIAS E LANÇAMENTOS DE PRODUTOS CULTURAIS. Buscado no PNCP em 02/10: não localizado.
- **#132** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): CE — aquisição de gêneros alimentícios diretamente da agricultura familiar e do empreendedor familiar rural ou de suas organizações. Buscado no PNCP em 02/10: não localizado.

### Bloco 12 — itens 133 a 144 (aplicável 9 · dispensável 2 · não aplica 1)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 133 | CE · EDITAL DE FOMENTO A AÇÕES CULTURAIS - POLÍTICA NACIONAL AL | APLICÁVEL | EN-01 | novo | — | ● | – | ○ | ○ | – | ● | ● | ● | ● | ● | ● | ● |
| 134 | Sobral/CE · Edital Sobral 2026: Projetos Culturais e PNAB | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 135 | Sobral/CE · MUNICIPIO DE SOBRAL — [LICITANET] - SELEÇÃO DE PROJETOS PA | APLICÁVEL | EN-01 | existe | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 136 | Iguatu/CE · MUNICIPIO DE IGUATU — Seleção de Organização da Sociedade  | APLICÁVEL | EN-01 | existe | 2026-10-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 137 | Senador Pompeu/CE · MUNICIPIO DE SENADOR POMPEU — Constitui objeto desta chama | APLICÁVEL | EN-01 | existe | 2026-10-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 138 | Maracanau/CE · MUNICIPIO DE MARACANAU — HAMAMENTO PÚBLICO PARA CREDENCIAM | APLICÁVEL | EN-01 +EN-03 | existe | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 139 | Eusebio/CE · MUNICIPIO DE EUSEBIO — Chamamento Público para credenciame | APLICÁVEL | EN-01 +EN-03 | existe | 2027-03-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 140 | Itaitinga/CE · MUNICIPIO DE ITAITINGA — CREDENCIAMENTO DE ORGANIZAÇÕES DA | APLICÁVEL | EN-01 | existe | 2027-07-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 141 | RS · Edital Prefeitura de Encantado 2026: Guia de Captação | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 142 | Minas do Leão/RS (FNMA) · Edital de Apoio a Projetos para a Melhoria de Resíduos Sól | NÃO APLICA | NA-06 | revisar | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 143 | Osorio/RS · MUNICIPIO DE OSORIO — O presente Chamamento Público se des | APLICÁVEL | EN-01 +EN-03 | existe | 2026-10-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 144 | Parobe/RS · MUNICIPIO DE PAROBE — Formalização de parceria estabelecid | APLICÁVEL | EN-01 +EN-03 | novo | 2026-10-13 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#133** (dados do painel (sem fonte oficial confirmada)): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): CE — seleção de propostas culturais destinadas ao fomento à manutenção e programação de espaços, ambientes e iniciativas culturais de Maranguape/CE. Buscado no PNCP em 02/10: não localizado.
- **#134** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #107: Sobral/CE — Seleciona projetos culturais de Sobral nas áreas de cultura e infâncias, circulação de obras, eventos artístico-culturais, cultura popular e capoeira para receber apoio f
- **#135** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Sobral/CE — [LICITANET] - SELEÇÃO DE PROJETOS PARA CULTURA E INFÂNCIAS; OBRAS ARTÍSTICAS PARA CIRCULAÇÃO; EVENTOS ARTÍSTICO-CULTURAIS; CAPOEIRA E CULTURA POPULAR DO MUNICÍPIO DE SOBR. PNCP: 07598634000137/2026/137.
- **#136** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Iguatu/CE — Seleção de Organização da Sociedade Civil – OSC para execução, em regime de colaboração com o Município, de serviços educacionais destinados ao atendimento de crianças da. PNCP: 07810468000190/2026/119.
- **#137** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Senador Pompeu/CE — Constitui objeto desta chamada pública a seleção e apoio a realização de iniciativa destinada à promoção, preservação e difusão das tradições regionais do município de Se. PNCP: 07728421000182/2026/93.
- **#138** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Maracanau/CE — HAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ENTIDADES COMUNITÁRIAS, SEM FINS LUCRATIVOS/ECONÔMICOS, REGULARMENTE CONSTITUÍDAS, MANTENEDORAS DE EDUCAÇÃO, CONTEMPLANDO BERÇÁRI. PNCP: 07605850000162/2026/5.
- **#139** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Eusebio/CE — Chamamento Público para credenciamento de entidades privadas, sem fins lucrativos, que realizem acolhimento exclusivamente voluntário, em regime residencial transitório, . PNCP: 23563067000130/2026/29.
- **#140** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Itaitinga/CE — CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL – OSCS PARA EXECUÇÃO DE ESCOLINHAS ESPORTIVAS E PROJETOS SOCIOESPORTIVOS VOLTADOS AO ATENDIMENTO DE CRIANÇAS E ADOLESCEN. PNCP: 41563628000182/2026/47.
- **#141** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: RS — Edital Prefeitura de Encantado 2026: Guia de Captação. Buscado no PNCP em 02/10: não localizado.
- **#142** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Minas do Leão/RS (FNMA) — seleção de propostas que receberão recursos financeiros.
- **#143** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Osorio/RS — O presente Chamamento Público se destina a selecionar Organizações da Sociedade Civil (OSC) sem fins lucrativos, para firmar parceria através de Termo de Colaboração, em . PNCP: 88814181000130/2026/450.
- **#144** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Parobe/RS — Formalização de parceria estabelecida pela administração pública com Organização de Sociedade Civil (OSC) para a consecução de projetos que tenham por foco atuação dentro. PNCP: 88372883000101/2026/270.

### Bloco 13 — itens 145 a 156 (aplicável 10 · dispensável 1 · não aplica 1)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 145 | Vera Cruz/RS · MUNICIPIO DE VERA CRUZ — Seleção de proposta/Plano de trab | APLICÁVEL | EN-01 +EN-03 | existe | 2026-10-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 146 | Vera Cruz/RS · MUNICIPIO DE VERA CRUZ — Formalização de parceria através  | APLICÁVEL | EN-01 +EN-03 | existe | 2026-11-12 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 147 | Santa Cruz Do Sul/RS · MUNICIPIO DE SANTA CRUZ DO SUL — Edital de Chamamento Públ | APLICÁVEL | EN-01 | existe | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 148 | Novo Hamburgo/RS · MUNICIPIO DE NOVO HAMBURGO — CHAMAMENTO PÚBLICO PARA CREDE | APLICÁVEL | EN-01 +EN-03 | existe | 2027-02-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 149 | Restinga Seca/RS · MUNICIPIO DE RESTINGA SECA — O objeto deste Termo de Refer | APLICÁVEL | EN-01 | existe | 2027-03-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 150 | Gravatai/RS · MUNICIPIO DE GRAVATAI — Credenciamento para seleção de pon | APLICÁVEL | EN-01 | existe | 2027-06-18 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 151 | Canoas/RS · MUNICIPIO DE CANOAS — Credenciamento de Agremiações Carnav | APLICÁVEL | EN-01 | existe | 2027-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 152 | Sao Pedro Do Sul/RS · MUNICIPIO DE SAO PEDRO DO SUL — 1.1.O PRESENTE EDITAL TEM  | APLICÁVEL | EN-01 +EN-03 | existe | 2031-03-26 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 153 | Florianópolis/SC · Diário Oficial de Florianópolis (SC) 2026-09-18 — "chamame | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 154 | Florianópolis/SC · Diário Oficial de Florianópolis (SC) 2026-09-23 — "chamame | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ● | ○ | ○ |
| 155 | SC · FUNDACAO MUNICIPAL DE CULTURA DE BOMBINHAS — EDITAL DE CRE | NÃO APLICA | NA-02 | revisar | 2026-12-21 | ● | ● | ○ | ◐ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 156 | Peritiba/SC · MUNICIPIO DE PERITIBA — O objeto deste Edital é a seleção  | APLICÁVEL | EN-01 | existe | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#145** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vera Cruz/RS — Seleção de proposta/Plano de trabalho para a formalização de parceria através de Termo de Colaboração, com Organizações da Sociedade Civil (OSC), para atender até 50 (cin. PNCP: 98661366000106/2026/563.
- **#146** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Vera Cruz/RS — Formalização de parceria através de Termo de Colaboração, com Organizações da Sociedade Civil (OSC), para atender até 30 (trinta) crianças na faixa etária de 0 (zero) a 4. PNCP: 98661366000106/2026/575.
- **#147** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Santa Cruz Do Sul/RS — Edital de Chamamento Público para seleção de propostas para Patrocínio a Eventos nº 001/2026. PNCP: 95440517000108/2026/24.
- **#148** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Novo Hamburgo/RS — CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE OSCS APTAS A EXECUÇÃO DO SERVIÇO DE ACOLHIMENTO INSTITUCIONAL (SAI), NA MODALIDADE ABRIGO INSTITUCIONAL, PARA CRIANÇAS E ADOLESC. PNCP: 88254875000160/2026/25.
- **#149** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Restinga Seca/RS — O objeto deste Termo de Referencia e o credenciamento de Organizacoes da Sociedade Civil com ou sem fins lucrativos para a prestacao do Servico de Acolhimento Institucion. PNCP: 87490306000151/2026/59.
- **#150** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Gravatai/RS — Credenciamento para seleção de pontos de cultura.. PNCP: 87890992000158/2026/620.
- **#151** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Canoas/RS — Credenciamento de Agremiações Carnavalescas, Agremiações de Samba com personalidade jurídica, sem fins lucrativos, com razão social carnaval, sediadas em canoas, para par. PNCP: 88577416000118/2026/44.
- **#152** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Sao Pedro Do Sul/RS — 1.1.O PRESENTE EDITAL TEM POR OBJETO O CREDENCIAMENTO PERMANENTE DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSCS), SEM FINS LUCRATIVOS, QUE ATUEM NA ÁREA DA EDUCAÇÃO, PARA COMPO. PNCP: 87489910000168/2026/43.
- **#153** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Florianópolis/SC — chamamento de OSC — até 35 núcleos de iniciação esportiva, Florianópolis. Buscado no PNCP em 02/10: não localizado.
- **#154** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Florianópolis/SC — chamamento de OSC — Programa Talentos Mané (esporte e lazer), Florianópolis. Buscado no PNCP em 02/10: não localizado.
- **#155** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SC — EDITAL DE CREDENCIAMENTO ELETRÔNICO DE PESSOAS JURÍDICAS PARA A PRESTAÇÃO DE SERVIÇOS DE CAPTAÇÃO DE RECURSOS ATRAVÉS DE INCENTIVOS FISCAIS VIA LEI Nº 8.313/91 - LEI DE I. PNCP: 09362501000192/2026/14.
- **#156** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Peritiba/SC — O objeto deste Edital é a seleção de projetos culturais para receberem apoio financeiro nas categorias descritas no Anexo I, com o objetivo de incentivar as diversas form. PNCP: 82815085000120/2026/165.

### Bloco 14 — itens 157 a 168 (aplicável 8 · dispensável 0 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 157 | Peritiba/SC · MUNICIPIO DE PERITIBA — [Portal de Compras Públicas] - O o | APLICÁVEL | EN-01 | existe | 2027-04-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 158 | SC · CONSORCIO INTERMUNICIPAL MULTIFINALITARIO DA REGIAO DA AMF | NÃO APLICA | NA-02 | revisar | 2027-07-20 | ● | ● | ○ | ◐ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 159 | Brusque/SC · MUNICIPIO DE BRUSQUE — [Portal de Compras Públicas] - CRED | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-09-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 160 | Balneario Camboriu/SC · MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entida | APLICÁVEL | EN-01 +EN-03 | existe | 2028-01-18 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 161 | Balneario Camboriu/SC · MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entida | APLICÁVEL | EN-01 +EN-03 | existe | 2028-04-15 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 162 | Nova Serrana/MG · Diário Oficial de Nova Serrana (MG) 2026-09-24 — "edital d | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 163 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-14 — "edital de cha | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 164 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-15 — "edital de cha | NÃO APLICA | NA-06 +EN-01 | veto | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 165 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-22 — "edital de cha | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 166 | Pirapetinga/MG · SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE A | APLICÁVEL | EN-01 | existe | 2026-10-16 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ● | ● |
| 167 | Pirapetinga/MG · MUNICIPIO DE PIRAPETINGA — Seleção e concessão de fomento  | APLICÁVEL | EN-01 | novo | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 168 | MG · CONSELHO DE ARQUITETURA E URBANISMO DO ESTADO DE MINAS GER | NÃO APLICA | NA-05 | revisar | 2026-10-21 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#157** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Peritiba/SC — [Portal de Compras Públicas] - O objeto deste edital é o credenciamento de associações sem fins lucrativos, sediadas no município de Peritiba, para realizar a comercializ. PNCP: 82815085000120/2026/121.
- **#158** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SC — CHAMAMENTO PÚBLICO, para CREDENCIAMENTO ELETRÔNICO de pessoas jurídicas para a prestação de serviços de captação de recursos através de incentivos fiscais via Lei n.º 8.3. PNCP: 32980376000104/2026/29.
- **#159** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Brusque/SC — [Portal de Compras Públicas] - CREDENCIAMENTO DE ARTISTAS, GRUPOS ARTÍSTICOS, PROFISSIONAIS DA CULTURA, OFICINEIROS, RECREADORES, INTÉRPRETES DE LIBRAS E DEMAIS AGENTES C. PNCP: 83102343000194/2026/220.
- **#160** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Balneario Camboriu/SC — Credenciamento de entidades privadas ou públicas, com ou sem fins lucrativos, para acolhimento institucional em residência inclusiva de jovens e adultos com deficiência, . PNCP: 83102285000107/2026/1.
- **#161** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Balneario Camboriu/SC — Credenciamento de entidades privadas, com ou sem fins lucrativos, para acolhimento institucional na modalidade Casa de Passagem para adultos, 18 a 59 anos, de ambos os se. PNCP: 83102285000107/2026/184.
- **#162** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Nova Serrana/MG — edital 07/2026 seleção de OSC — termo de fomento para evento de cultura afro-brasileira (Nova Serrana/MG). Buscado no PNCP em 02/10: não localizado.
- **#163** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Uberaba/MG — PNAB 002/2026 bolsas (Uberaba/MG) — mesma oportunidade de 35053888. Buscado no PNCP em 02/10: não localizado.
- **#164** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Uberaba/MG — PNAB 002/2026 bolsas de intercâmbio e residência (Uberaba/MG).
- **#165** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Uberaba/MG — PNAB 004/2026 projetos de música (Uberaba/MG). Buscado no PNCP em 02/10: não localizado.
- **#166** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Pirapetinga/MG — SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS COM RECURSOS DA POLÍTICA NACIONAL ALDIR BLANC DE FOMENTO À CULTURA-PNAB LEI N 14.3992022. PNCP: 01006232000110/2026/72.
- **#167** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Pirapetinga/MG — Seleção e concessão de fomento à execução de ações culturais por meio de projetos, com recursos da Política Nacional Aldir Blanc de Fomento à Cultura (Lei Federal nº 14.3. PNCP: 18092825000149/2026/65.
- **#168** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — O concurso PRÊMIO DE BOAS PRÁTICAS URBANAS: AMBIENTAL, SANEAMENTO E SOCIAL - 2026, visa a seleção e premiação de 05 (cinco) projetos, obras ou instalações arquitetônicas . PNCP: 14951451000119/2026/45.

### Bloco 15 — itens 169 a 180 (aplicável 2 · dispensável 1 · não aplica 9)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 169 | MG · PONTE NOVA CAMARA MUNICIPAL — Concurso Parlamento em Ação, | NÃO APLICA | NA-05 | revisar | 2026-11-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 170 | MG · PONTE NOVA CAMARA MUNICIPAL — Concurso, referente a 5a edi | NÃO APLICA | NA-05 | revisar | 2026-12-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 171 | Lagoa Santa/MG · MUNICIPIO DE LAGOA SANTA — CREDENCIAMENTO DE PROPOSTAS ART | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-04-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 172 | Confins/MG · MUNICIPIO DE CONFINS — CHAMADA PÚBLICA PARA CREDENCIAMENTO | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-06-01 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 173 | MG · MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO — Reabertura | APLICÁVEL | EN-01 +EN-03 | existe | 2027-07-30 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 174 | Juruaia/MG · MUNICIPIO DE JURUAIA — CREDENCIAMENTO ELETRÔNICO PARA RECE | NÃO APLICA | NA-06 +EN-01 | veto | 2027-08-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 175 | MG · FUNDACAO UBERLANDENSE DO TURISMO ESPORTE E LAZER — Credenc | NÃO APLICA | NA-02 | revisar | 2030-12-11 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 176 | Passos/MG · MUNICIPIO DE PASSOS — Credenciamento de Instituições de Lo | NÃO APLICA | NA-06 | revisar | 2031-06-25 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 177 | Vitória/ES · Diário Oficial de Vitória (ES) 2026-08-20 — "edital de cha | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 178 | Castelo/ES · MUNICIPIO DE CASTELO — Credenciamento de cooperativas e as | NÃO APLICA | NA-06 | revisar | 2027-07-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 179 | AC · ESTADO DO ACRE — 4º PRÊMIO DE COMUNICAÇÃO DO GOVERNO DO ES | NÃO APLICA | NA-05 | revisar | 2026-10-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 180 | Silvania/GO · MUNICIPIO DE SILVANIA — REALIZAÇÃO E PUBLICAÇÃO DO EDITAL  | APLICÁVEL | EN-01 | existe | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#169** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — Concurso Parlamento em Ação, projeto desenvolvido e gerenciado pela Escola do Legislativo da Câmara Municipal de Ponte Nova, integrante do conjunto de ações voltadas à ed. PNCP: 21087648000117/2026/24.
- **#170** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — Concurso, referente a 5a edição da gincana “Sua casa, nossa Câmara!", que premiará cidadãos e moradores de Ponte Nova participantes de atividades interativas promovidas p. PNCP: 21087648000117/2026/23.
- **#171** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Lagoa Santa/MG — CREDENCIAMENTO DE PROPOSTAS ARTÍSTICAS, INDIVIDUAIS, E/OU COLETIVOS, E PROFISSIONAIS DE SEGUIMENTOS ARTÍSTICOCULTURAIS, PARA A RESTAÇÃO EVENTUAL DE SERVIÇO, PARA COMPOR A. PNCP: 73357469000156/2026/55.
- **#172** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Confins/MG — CHAMADA PÚBLICA PARA CREDENCIAMENTO DE ARTISTAS, BANDAS, GRUPOS CULTURAIS, COLETIVOS ARTÍSTICOS, PROFISSIONAIS DO AUDIOVISUAL E DEMAIS AGENTES CULTURAIS PARA FUTURA E EVE. PNCP: 01006232000110/2026/40.
- **#173** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): MG — Reabertura do Edital de Credenciamento SEE nº 02/2025 - Credenciamento de instituições públicas ou privadas, com ou sem fins lucrativos, que poderão ofertar formação prof. PNCP: 18715599000105/2026/622.
- **#174** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Juruaia/MG — CREDENCIAMENTO ELETRÔNICO PARA RECEBIMENTO DE PROPOSTAS DE PESSOAS FÍSICAS E JURÍDICAS INTERESSADAS NA PRESTAÇÃO DE SERVIÇOS ARTÍSTICOS E CULTURAIS, ABRANGENDO ARTISTAS, . PNCP: 18668368000198/2026/186.
- **#175** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): MG — Credenciamento de interessados (terceiro facilitador) na captação de recursos vinculados à lei estadual de incentivo ao esporte de minas gerais nº 20.824/2013, ao decreto. PNCP: 20260121000180/2026/1.
- **#176** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Passos/MG — Credenciamento de Instituições de Longa Permanência para Idosos – ILPI, pessoas jurídicas de direito privado, com ou sem fins lucrativos, de Passos e/ou outra cidade da r. PNCP: 18241745000108/2026/37.
- **#177** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Vitória/ES — edital FIA 001/2026 CONCAV — errata (Vitória/ES).
- **#178** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Castelo/ES — Credenciamento de cooperativas e associações que estejam legalmente habilitadas para Coleta Seletiva de resíduos recicláveis, classificados pela NBR 10004 como de origem . PNCP: 27165638000139/2026/241.
- **#179** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: AC — 4º PRÊMIO DE COMUNICAÇÃO DO GOVERNO DO ESTADO DO ACRE “MOISÉS ALENCASTRO". PNCP: 63606479000124/2026/123.
- **#180** (PNCP consultado ao vivo em 02/10/2026): Silvânia/GO — PNAB Ciclo 2 (agentes culturais do município); prazo 09/10/2026 no PNCP; de outro município goiano. PNCP: 01068030000100/2026/355.

### Bloco 16 — itens 181 a 192 (aplicável 4 · dispensável 4 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 181 | GO · Chamamento público publicado no Diário Oficial em 25/09/20 | DISPENSÁVEL | DI-08 | junta | — | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 182 | GO · Chamamento público publicado no Diário Oficial em 25/09/20 | NÃO APLICA | NA-01 | revisar | — | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ○ | ● | ○ | ○ |
| 183 | Catalão/GO (título cita Pinhais) · Chamamento público publicado no Diário Oficial em 28/08/20 | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ● | ● | ● |
| 184 | Goiânia/GO · Diário Oficial de Goiânia (GO) 2026-09-25 — "edital de cha | APLICÁVEL (apto) | AP-01 | existe | 2026-10-26 | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 185 | GO · Editais - FAPEG — Goiás — Goiás — Goiás | NÃO APLICA | NA-06 | revisar | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 186 | GO · Editais de Chamamento — Goiás / Goiânia | NÃO APLICA | NA-04 | revisar | — | ● | – | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 187 | GO · Editais de Destinação de Recursos ou Bens | APLICÁVEL (apto) | AP-03 | existe | recorrente (cada edital ≈ 5 di | ● | ● | – | – | ● | ● | ● | ● | ● | ● | ● | ● |
| 188 | GO · Edital Arranjos Regionais FSA | NÃO APLICA | NA-06 | revisar | — | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 189 | Goiatuba/GO · Edital Cultura Goiatuba 2026: PNAB Ciclo 2 — Goiás / Goiat | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 190 | Planaltina/GO · Edital Prefeitura Municipal de Planaltina 2026 | APLICÁVEL | EN-01 +EN-03 | existe | — | ● | – | – | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 191 | Goiânia/GO · Edital chamamento público nº 001/2026 (oss) — Goiás / Goiâ | APLICÁVEL | EN-03 | existe | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 192 | GO · Edital de Chamamento Público de Instituições sem Fins Lucr | DISPENSÁVEL | DI-03 | existe | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |

- **#181** (dados do painel (sem fonte oficial confirmada)): Registro duplicado do #184 (Natal no Parque): a URL deste registro é o Diário Oficial de Goiânia de 25/09/2026 (o mesmo do #184). Os dados do painel (valor R$ 4.638.055,74) vieram de outro documento, o link oficial de 07/08, que é o crédito suplementar do #182.
- **#182** (dados do painel (sem fonte oficial confirmada)): Diário de Goiânia de 07/08/2026 — abertura de crédito suplementar de R$ 4.638.055,74 para a Secretaria de Administração/Guarda Civil: ato orçamentário, não chamamento (título cita 25/09, mas o documento lido é de 07/08).
- **#183** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Catalão/GO (título cita Pinhais) — O presente edital possui valor total de R$591.740,18 (quinhentos e noventa e um mil setecentos e quarenta reais e dezoito centavos).. Buscado no PNCP em 02/10: não localizado.
- **#184** (edital lido ao vivo (Diário Oficial de Goiânia 25/09)): Goiânia/SEGENP — Chamamento Público nº 001/2026 "Natal no Parque – A Magia de Brincar" (Lei 13.019): termo de colaboração com OSC, valor máximo R$ 5.000.000,00; protocolo único até 26/10/2026, resultado definitivo em 06/11/2026. Exige ≥ 1 ano de CNPJ ativo (a entidade tem 39 anos de CNPJ) e experiência prévia em objeto semelhante (eventos culturais). Edital lido no Diário Oficial de 25/09/2026 (pá
- **#185** (dados do painel (sem fonte oficial confirmada)): FAPEG — página de chamadas de pesquisa/inovação (ICT, pesquisadores, bolsistas): associação não é proponente típico.
- **#186** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: GO — credenciamento de profissionais ESPECIALISTAS, TÉCNICOS E AUXILIARES EM SAÚDE.
- **#187** (validação anterior (27–29/09) + dados do painel): MPT/PRT-18 (Goiás) — página permanente de editais de destinação de recursos de TAC (fonte recorrente, validada em 29/09). O edital em curso (9282.2026, R$ 150.000,00, publicado em 25/09, prazo de 5 dias) já está vencido ou vence hoje; o edital anterior (8927.2026) também encerrou. Valor da fonte: monitorar a página e manter projeto social pronto para indicação a cada novo edital.
- **#188** (dados do painel (sem fonte oficial confirmada)): FSA Arranjos Regionais (Goiás) — exige produtora brasileira independente com fins lucrativos registrada na ANCINE; associação não é público.
- **#189** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Goiatuba/GO — Edital Cultura Goiatuba 2026: PNAB Ciclo 2 — Goiás / Goiatuba. Buscado no PNCP em 02/10: não localizado.
- **#190** (validação anterior (27–29/09) + dados do painel): Planaltina/GO — Chamamento nº 06/2026 (Esporte e Lazer, R$ 30 mil, campeonatos): livro próprio; enquadramento: é de outro município goiano e exige OSC local; data-limite não consta do edital. Buscado no PNCP em 02/10: não localizado.
- **#191** (dados do painel (sem fonte oficial confirmada)): SMS Goiânia — edital de chamamento nº 001/2026 (organização social de saúde): livro próprio; enquadramento: exige qualificação como OS e gestão de serviços de saúde, incompatível com o perfil atual da associação.
- **#192** (página oficial lida ao vivo): SEDS/GO — chamamento "Aprendiz do Futuro" já em fase de recursos administrativos e julgamento: inscrições encerradas.

### Bloco 17 — itens 193 a 204 (aplicável 2 · dispensável 2 · não aplica 8)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 193 | GO (SEDS, estadual) · Edital de chamamento público - 001/2026 - Socioeducativo — | APLICÁVEL | EN-03 | existe | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 194 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — | NÃO APLICA | NA-04 | revisar | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 195 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — | NÃO APLICA | NA-06 | revisar | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 196 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — | NÃO APLICA | NA-06 | revisar | — | ● | ○ | ● | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 197 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — | NÃO APLICA | NA-06 | revisar | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 198 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — | NÃO APLICA | NA-06 | revisar | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 199 | GO · Goiás Social aumenta repasse do Auxílio Nutricional às ent | APLICÁVEL (apto) | AP-03 | existe | fluxo contínuo (até 08/2027) | ● | ● | ● | ● | – | ● | ● | ● | ● | ● | ● | ● |
| 200 | GO · Goiás Social — Conselho Estadual dos Direitos da Criança e | NÃO APLICA | NA-07 | revisar | — | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ● |
| 201 | GO · Prefeitura de Cachoeira Alta — Edital nº 001/2026 | NÃO APLICA | NA-03 | veto | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 202 | Goiatuba/GO · Prefeitura de Goiatuba — Edital nº 004/2026 | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 203 | Nova Iguaçu de Goiás/GO · Prefeitura de Nova Iguaçu de Goiás — Edital nº 001/2026 —  | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 204 | GO · Prorrogado prazo para submissão de propostas ao edital de  | NÃO APLICA | NA-06 | revisar | — | ● | ○ | ● | ○ | ○ | ● | ○ | ● | ○ | ● | ○ | ● |

- **#193** (página oficial lida ao vivo): SEDS/GO — Chamamento nº 001/2026 Socioeducativo: termo de colaboração para ações complementares ao atendimento socioeducativo (página atualizada em 24/09/2026; o texto do edital está em anexo que não consegui ler e o prazo não consta da página). Livro próprio; enquadramento presumido: exigência de experiência técnica especializada, que o perfil da associação não comprova — PRESUNÇÃO a confirmar co
- **#194** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: GO — Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Edital da Fapeg fomenta novas pesquisas sobre os be… — Goiás.
- **#195** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Fapeg lança chamada para apoio financeiro a periódi… — Goiás.
- **#196** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — apoio à pesquisa e inovação em educação especial inclusiva.
- **#197** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — apoiar financeiramente propostas que, para além de diagnósticos, promovam implementação de soluções práticas, sustentáveis e inovadoras, com participação direta das mulhe.
- **#198** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — seleção de bolsistas para projetos de desenvolvimento tecnológico e industrial.
- **#199** (validação anterior (27–29/09) + dados do painel): SEDS/GO — Credenciamento nº 001/2026 em fluxo contínuo (12 meses a partir de 27/08/2026) para OSC atuantes em Goiás (Auxílio Nutricional e/ou Água e Energia); sem data-limite. Conferir no edital se o público atendido (entidades que acolhem/atendem pessoas em vulnerabilidade) abrange a atividade da associação.
- **#200** (dados do painel (sem fonte oficial confirmada)): CEDCA/GO — convocação de representantes da sociedade civil para o conselho: é vaga de conselheiro (influência), não repasse de recursos. Vale acompanhar como oportunidade de articulação, fora do funil de captação.
- **#201** (dados do painel (sem fonte oficial confirmada)): É seleção de pessoas (estágio/aprendizagem/processo seletivo), não de entidade: GO — formação de cadastro reserva para estágio.
- **#202** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Goiatuba/GO — Prefeitura de Goiatuba — Edital nº 004/2026.
- **#203** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Nova Iguaçu de Goiás/GO — Promover os Jogos Educacionais no contexto virtual e/ou presencial, a fim de possibilitar o acesso às práticas corporais, de forma a contribuir com o processo de aprendiz. Buscado no PNCP em 02/10: não localizado.
- **#204** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — Conservação da Biodiversidade Legado Verdes do Cerrado.

### Bloco 18 — itens 205 a 216 (aplicável 4 · dispensável 4 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 205 | GO · SECTI-GO (ciência e tecnologia) — Edital nº 002/2026 | DISPENSÁVEL | DI-05 +EN-03 | aguarda | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 206 | PA · UNIVERSIDADE FEDERAL RURAL DA AMAZONIA — PROCEDIMENTO DE H | NÃO APLICA | NA-06 +DI-03 | revisar | 2026-10-13 (revogado) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 207 | Mossoró/RN · Diário Oficial de Mossoró (RN) 2026-09-15 — "edital de cha | APLICÁVEL | EN-01 | novo | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 208 | Mossoró/RN · Diário Oficial de Mossoró (RN) 2026-09-16 — "chamamento pú | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 209 | Alexandria/RN · MUNICIPIO DE ALEXANDRIA — SELEÇÃO DE ORGANIZAÇÃO DA SOCIED | APLICÁVEL | EN-01 | existe | 2026-10-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 210 | Santa Cruz/RN · MUNICIPIO DE SANTA CRUZ — Credenciamento de artistas indiv | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-06-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 211 | Jandaira/RN · MUNICIPIO DE JANDAIRA — CREDENCIAMENTO DE ARTISTAS, GRUPOS | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-08-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 212 | Portalegre/RN · MUNICIPIO DE PORTALEGRE — Contratação de artistas, grupos  | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-10-01 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 213 | Rio Grande do Norte · Seleção de Organização da Sociedade Civil – OSC, em regime | APLICÁVEL | EN-01 | existe | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 214 | São José do Vale do Rio Preto/RJ · Diário Oficial de São José do Vale do Rio Preto (RJ) 2026- | DISPENSÁVEL | DI-05 +EN-01 | aguarda | 2027-05-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 215 | Macaé/RJ · Diário Oficial de Macaé (RJ) 2026-09-22 — "chamamento públ | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 216 | Niterói/RJ · Diário Oficial de Niterói (RJ) 2026-09-16 — "edital de cha | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |

- **#205** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: GO — SECTI-GO (ciência e tecnologia) — Edital nº 002/2026.
- **#206** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PA — PROCEDIMENTO DE HABILITAÇÃO DAS ASSOCIAÇÕES E/OU COOPERATIVASDECATADORES DE MATERIAIS RECICLÁVEIS E REUTILIZÁVEIS, no intuito de firmar TERMODECOMPROMISSO para fins de co. PNCP: 05200001000101/2027/1.
- **#207** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Mossoró/RN — edital de repasse a projetos artísticos (Mossoró/RN). Buscado no PNCP em 02/10: não localizado.
- **#208** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Mossoró/RN — O presente Termo Aditivo 001 ao contrato que fazem entre si a Câmara Municipal Mossoró/RN, GRID COMUNICAÇÃO VISUAL, SINALIZAÇÃO E EVENTOS LTDA com o objeto de prestação d.
- **#209** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Alexandria/RN — SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL - OSC PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO DESTINADO À EXECUÇÃO DE AÇÕES DE ACOLHIMENTO E HOSPEDAGEM TEMPORÁRIA DE CÃES E GAT. PNCP: 08148462000162/2026/72.
- **#210** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Santa Cruz/RN — Credenciamento de artistas individuais, grupos ou coletivos para a pintura de painéis, tipificados como “intervenções artísticas”, utilizando a técnica do graffiti, mural. PNCP: 08358889000195/2026/102.
- **#211** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Jandaira/RN — CREDENCIAMENTO DE ARTISTAS, GRUPOS, COLETIVOS E AGENTES CULTURAIS, NOS TERMOS DA LEI FEDERAL Nº 14.399/2022 (POLÍTICA NACIONAL ALDIR BLANC – PNAB), PARA PRESTAÇÃO DE SERV. PNCP: 08309239000150/2026/91.
- **#212** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Portalegre/RN — Contratação de artistas, grupos artísticos e agentes culturais para os eventos e demais programações do município de Portalegre/RN, abrangendo apresentações musicais, lit. PNCP: 08358053000190/2026/163.
- **#213** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Rio Grande do Norte — Seleção de Organização da Sociedade Civil – OSC, em regime de mútua cooperação, para celebração de parceria com a administração pública municipal, objetivando a consecuçã. PNCP: 08004525000107/2026/90.
- **#214** (validação anterior (27–29/09) + dados do painel): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: São José do Vale do Rio Preto/RJ — edital 05/2026 seleção de OSC — assistência social (São José do Vale do Rio Preto/RJ). Buscado no PNCP em 02/10: não localizado.
- **#215** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Macaé/RJ — fomento a parcerias com governo federal e estadual.
- **#216** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Niterói/RJ — extrato do edital SMC 02/2026 Cultura Geek (Niterói/RJ). Buscado no PNCP em 02/10: não localizado.

### Bloco 19 — itens 217 a 228 (aplicável 4 · dispensável 2 · não aplica 6)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 217 | São José do Vale do Rio Preto/RJ · Diário Oficial de São José do Vale do Rio Preto (RJ) 2026- | DISPENSÁVEL | DI-08 +EN-01 | junta | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 218 | Arraial Do Cabo/RJ · MUNICIPIO DE ARRAIAL DO CABO — O presente Chamamento Públi | APLICÁVEL | EN-01 | existe | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 219 | RJ · SECRETARIA MUNICIPAL DE EDUCACAO — Credenciamento de Organ | APLICÁVEL | EN-01 +EN-03 | existe | 2027-05-27 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 220 | Angra Dos Reis/RJ · MUNICIPIO DE ANGRA DOS REIS — Credenciamento de Cooperativ | NÃO APLICA | NA-06 | revisar | 2027-06-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 221 | Itacoatiara/AM · MUNICIPIO DE ITACOATIARA — [LICITANET] - Seleção de Projet | APLICÁVEL | EN-01 | novo | 2026-10-16 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 222 | AM · TRIBUNAL REGIONAL ELEITORAL DO AMAZONAS — O presente proce | NÃO APLICA | NA-06 | revisar | 2028-01-31 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 223 | Muribeca/SE · Diário Oficial de Muribeca (SE) 2026-08-04 — "edital de ch | DISPENSÁVEL | DI-04 +EN-01 | edição | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 224 | Simão Dias/SE · Diário Oficial de Simão Dias (SE) 2026-08-17 — "edital de  | APLICÁVEL | EN-01 | novo | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ● | ● |
| 225 | SE · ARACAJU CAMARA MUNICIPAL — ESTE EDITAL DISPÕE SOBRE AS NOR | NÃO APLICA | NA-05 | revisar | 2026-10-13 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 226 | Nova Palmeira/PB · MUNICIPIO DE NOVA PALMEIRA — Credenciamento de facilitador | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-01-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 227 | Nova Palmeira/PB · MUNICIPIO DE NOVA PALMEIRA — credenciamento de articulador | NÃO APLICA | NA-06 +EN-01 | revisar | 2027-01-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 228 | Boa Hora/PI · MUNICIPIO DE BOA HORA — CONTRATAÇÃO DE PRESTADOR DE SERVIÇ | NÃO APLICA | NA-02 | revisar | 2027-07-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#217** (validação anterior (27–29/09) + dados do painel): Mesma oportunidade do registro #214: São José do Vale do Rio Preto/RJ — edital 05/2026 seleção de OSC — republicado (São José do Vale do Rio Preto/RJ) — mesma oportunidade de 332e8f67
- **#218** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Arraial Do Cabo/RJ — O presente Chamamento Público tem por objeto a seleção de Organização da Sociedade Civil (OSC) para celebração de Termo de Colaboração com o Município de Arraial do Cabo,. PNCP: 27792373000107/2026/150.
- **#219** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): RJ — Credenciamento de Organizações da Sociedade Civil (OSC), com vistas a possíveis e futuras parcerias na área educacional, com fundamento na Lei Federal nº 13.019/2014, alt. PNCP: 06072751000108/2026/4.
- **#220** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Angra Dos Reis/RJ — Credenciamento de Cooperativas e Associações interessadas em receber Remuneração Complementar pela prestação de serviços de coleta e reciclagem de óleo vegetal comestível. PNCP: 29172467000109/2027/92.
- **#221** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Itacoatiara/AM — [LICITANET] - Seleção de Projetos Culturais para Concessão de Apoio Financeiro e Celebração de Termo de Execução Cultural, com a Finalidade de Fomentar, Fortalecer e Valo. PNCP: 04241980000175/2026/67.
- **#222** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: AM — O presente procedimento tem por objeto selecionar as associações e/ou cooperativas de catadores de materiais recicláveis e reutilizáveis, que estejam cadastradas no SINIR. PNCP: 05959999000114/2026/52.
- **#223** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Muribeca/SE — comunicado do edital PNAB 001/2026 ciclo 2 (Muribeca/SE).
- **#224** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Simão Dias/SE — editais culturais 003 e 004/2026 SEMCULT (Simão Dias/SE). Buscado no PNCP em 02/10: não localizado.
- **#225** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: SE — ESTE EDITAL DISPÕE SOBRE AS NORMAS, PROCEDIMENTOS E PRAZOS PARA PARTICIPAÇÃO NA 9ª EDIÇÃO DO PRÊMIO DE POESIA GOVERNADOR MARCELO DÉDA, ORGANIZADO PELO SETOR DE PROMOÇÃO S. PNCP: 13167804000121/2026/22.
- **#226** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Nova Palmeira/PB — Credenciamento de facilitadores, profissionais e assessoria técnica para atuar no projeto "DE TODOS PARA TODOS" centro de inclusão social, através de termo de adesão entr. PNCP: 08739930000173/2026/42.
- **#227** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Nova Palmeira/PB — credenciamento de articuladores, profissionais e assessoria técnica para atuar no projeto “TENDA ITINERANTE - ESPAÇO DAS HISTÓRIAS VIVAS, através de termo de adesão entre. PNCP: 08739930000173/2026/41.
- **#228** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Boa Hora/PI — CONTRATAÇÃO DE PRESTADOR DE SERVIÇOS PARA EXECUÇÃO DE CAPACITAÇÃO, QUALIFICAÇÃO E FORMAÇÃO DE AGENTES CULTURAIS (AUDIOVISUAL, TEATRO), NOS TERMOS DA LEI Nº 14.399, DE 8 D. PNCP: 01612568000126/2026/33.

### Bloco 20 — itens 229 a 238 (aplicável 5 · dispensável 1 · não aplica 4)

| # | Local · registro | Veredito | Regra | Livro | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 229 | Palmas/TO · MUNICIPIO DE PALMAS — Selecao de Organizacao da Sociedade  | APLICÁVEL | EN-01 +EN-03 | existe | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 230 | TO · TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciament | NÃO APLICA | NA-06 +DI-03,EN-01 | revisar | 2030-04-01 (suspenso) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 231 | PE · FUNDACAO MUNICIPAL DE SAUDE DE TAQUARITINGA DO NORTE — CRE | APLICÁVEL | EN-01 +EN-03 | existe | 2027-05-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 232 | PE · FUNDO MUNICIPAL DE SAUDE DE TAQUARITINGA DO NORTE — CREDEN | APLICÁVEL | EN-01 +EN-03 | existe | 2027-05-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 233 | PE · UNIVERSIDADE FEDERAL DE PERNAMBUCO — Selecionar e habilita | NÃO APLICA | NA-06 | revisar | 2028-02-08 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 234 | Costa Rica/MS · Diário Oficial de Costa Rica (MS) 2026-08-11 — "edital de  | DISPENSÁVEL | DI-05 +EN-01 | aguarda | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 235 | AP · DEFENSORIA PUBLICA DO ESTADO — Concurso de artigos para pu | NÃO APLICA | NA-05 | revisar | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 236 | Nova Mutum/MT · MUNICIPIO DE NOVA MUTUM — CHAMAMENTO PÚBLICO PARA SELEÇÃO  | APLICÁVEL | EN-01 | existe | 2026-10-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 237 | MT · TRIBUNAL SUPERIOR DO TRABALHO — CHAMAMENTO PÚBLICO DE INST | NÃO APLICA | NA-06 | revisar | 2030-02-13 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 238 | Boa Vista/RR · Diário Oficial de Boa Vista (RR) 2026-08-05 — "edital de c | APLICÁVEL | EN-01 +EN-03 | novo | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |

- **#229** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Palmas/TO — Selecao de Organizacao da Sociedade Civil - OSC para celebracao de Termo de Colaboracao destinado a gestao, a operacionalizacao e a execucao das acoes e servicos de saude. PNCP: 24851511000185/2026/527.
- **#230** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: TO — Credenciamento de associação e/ou cooperativa de catadores de materiais recicláveis por meio do Projeto Coleta Seletiva Solidária para prestarem serviços gratuitos de col. PNCP: 25053190000136/2026/1.
- **#231** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): PE — CREDENCIAMENTO DE PESSOA(S) JURÍDICA(S) DE DIREITO PRIVADO, PREFERENCIALMENTE AS ENTIDADES FILANTRÓPICAS E AS SEM FINS LUCRATIVOS (previsão do Art. 199, § 1º, da CF), INT. PNCP: 01683480000103/2026/5.
- **#232** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): PE — CREDENCIAMENTO DE PESSOA(S) JURÍDICA(S) DE DIREITO PRIVADO, PREFERENCIALMENTE AS ENTIDADES FILANTRÓPICAS E AS SEM FINS LUCRATIVOS (previsão do Art. 199, § 1º, da CF), INT. PNCP: 08677960000100/2026/4.
- **#233** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PE — Selecionar e habilitar as associações e/ou cooperativas de catadores de materiais recicláveis aptas a firmar Termo de Compromisso, visando à coleta de resíduos sólidos re. PNCP: 24134488000108/2027/3.
- **#234** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Costa Rica/MS — Seleção de profissionais para o cargo efetivo de Guarda Civil no Município de Costa Rica/MS.
- **#235** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: AP — Concurso de artigos para publicação na 2ª edição da Revista da Defensoria Pública do Amapá.. PNCP: 11762144000100/2026/16.
- **#236** (PNCP consultado ao vivo em 02/10/2026): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Nova Mutum/MT — CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS CULTURAIS, VISANDO À CELEBRAÇÃO DE TERMO DE EXECUÇÃO CULTURAL COM AGENTES CULTURAIS DO MUNICÍPIO DE NOVA MUTUM-MT – CICLO 2, P. PNCP: 24772162000106/2026/168.
- **#237** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: MT — CHAMAMENTO PÚBLICO DE INSTITUIÇÕES DE ENSINO SUPERIOR (IES) INTERESSADAS EM CELEBRAR ACORDO DE COOPERAÇÃO TÉCNICA E ACORDO DE COOPERAÇÃO PARA DESENVOLVIMENTO DE SERVIÇOS . PNCP: 00509968000148/2026/8.
- **#238** (validação anterior (27–29/09) + dados do painel): Oportunidade para OSC de outro território: ganha livro próprio, coletado pelo PNCP; o território fica anotado no livro como enquadramento (o chamamento costuma exigir sede/atuação local): Boa Vista/RR — resultado final com REABERTURA DE PRAZO de chamamento de OSC — saúde (Boa Vista/RR); prazo não confirmado. Buscado no PNCP em 02/10: não localizado.

## 10. Defeitos de coleta encontrados (regras RC dos livros)

1. **RC-01 — falso "nacional":** 39 registros no balde `__nac__` sem serem nacionais (só 3 são). O mesmo defeito aparece nos livros: 103 livros municipais do PNCP estão marcados como "BR"; o ciclo passa a levar a UF do PNCP ao livro (simulação: 62 restantes).
2. **RC-02 — objeto do diário:** em "menção em diário oficial" o objeto vem de trecho vizinho (crédito, concurso, plano); só vale após ler o ato.
3. **RC-03 — link oficial errado:** Itapeva/SP → itapeva.mg.gov.br; Pinhais/PR → catalao.go.gov.br; Valparaíso/SP → campoflorido.mg.gov.br; Canudos/BA → joaopinheiro.mg.gov.br; PNAB → edital de concurso público; Andradina → PDF de concurso da Educação.
4. **RC-04 — vigência não é prazo:** credenciamentos com encerramento em 2030/2031 são vigência do cadastro.
5. **RC-05 — link fictício:** #101 aponta para `x.gov.br/edital`; quarentena.
6. **RC-06 — duplicatas:** #102=#18, #43=#46, #55=#66, #78=#224, #88=#5, #89=#6, #134=#107, #181=#184, #217=#214 — todas achadas na leitura humana; o código só junta por chave PNCP (título+município exige leitura, porque o mesmo diário traz editais diferentes).
7. **RC-07 — território não descarta (nova):** edital de OSC de outro município/estado compõe livro próprio; o território vai ao livro como enquadramento.
8. **RC-08 — PNCP como agregador, diário como fonte (nova):** livro sem chave PNCP é procurado no PNCP com a consulta do próprio livro; não achado, segue com a fonte do órgão e é procurado de novo em 7 dias.

## 11. Decisões do titular e próximos passos

1. **Natal no Parque:** concorrer sozinha, em rede ou não concorrer? (prazo 26/10).
2. **Alcance da exceção de abrangência:** hoje a regra antiga (livro público municipal só de Goiás) continua valendo para o resto do país, com duas exceções — o que vem do PNCP e os livros deste parecer. Estender a exceção a **todo** edital de OSC de outro município achado em diário oficial (Querido Diário) — mais cobertura, mais livros — ou manter o PNCP como porta de entrada?
3. **Catadores, ILPI e associações estudantis (proposta, não aplicada):** hoje NÃO APLICA. Podem virar livro com enquadramento se o titular quiser o mapa completo — com a ressalva de que ser organização de catadores ou ILPI é requisito de natureza jurídica (a associação nunca o cumpre) e de que vários desses atos são contratação ou credenciamento pela Lei 14.133 (coleta remunerada, SUS complementar), não fomento MROSC.
4. **Fluxos contínuos (#199 SEDS, #86 iCS) e recorrência (#187 MPT):** autorizar a preparação de projeto-base.
5. **Curadoria:** conferir os 68 livros existentes que caíram em veto e os 123 livros com regra suspensa.
6. Aplicar o patch (código, catálogo-mãe das regras, semente e testes) — os livros são criados e recebem léxico e restrições no primeiro ciclo depois da integração.

## 12. Verificação

- Regras contra esta validação: **84.0%** de concordância de classe (v2). Ressalva: calibradas no mesmo conjunto — ajuste, não validação independente. As divergências são casos de leitura do ato (vigência tomada por prazo, link de outro município, objeto mal extraído).
- `tests/test_regras_restricao.py`: 32 testes (regras v2, bloco do livro, regra que não se volta contra o livro, julgamento no livro, idempotência, sensor e prompt com o léxico do livro, achado vetado e em quarentena, errata sem livro em pendência, outro número PNCP = outro livro, livro de outro município criado e não arquivado, semente, Fonte C do PNCP com e sem localização e recusando ato de outro objeto).
- **Revisão independente** (subagente sem contexto): conferiu as 238 linhas do parecer contra a validação (0 divergências), as contagens e o backtest; apontou 11 riscos de lógica, 5 de coerência e 4 de afirmações — aplicados: Fonte C exige ato de OSC, mesmo número ou dois termos do livro e aprovação do classificador; item da semente com livro não é barrado pela validação antiga; editais distintos não se juntam; errata sem livro vai a pendência; modalidade cede às exceções; `oscs?`; datas não viram número de edital; injeção não vira livro; vetos sem repetição; catadores/ILPI revertidos a NÃO APLICA (proposta ao titular); links de outro município (RC-03) em DI-05; textos e contagens corrigidos.
- Simulação do ciclo dos livros sobre cópia do catálogo de 02/10 (nada gravado): 1033 → 1067 livros; 1067 blocos `busca`; 104 livros do parecer, nenhum arquivado; catálogo 4.31 → 4.86 MB.
- Busca no PNCP feita ao vivo em 02/10 (Chrome do titular) para os 58 registros sem link PNCP; resultado registrado por item (coluna *busca_pncp_02_10*).
