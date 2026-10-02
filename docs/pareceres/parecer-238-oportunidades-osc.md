# Parecer — validação das 238 oportunidades abertas (não confirmadas) para a A.M.C. Jardim América

**Data-base:** 02/10/2026 · **Entidade de referência:** Associação dos Moradores e Comerciantes do Jardim América (OSC, CNPJ ativo desde 1987, Goiânia/GO) · **Universo:** 238 registros do painel (259 oportunidades − 21 já confirmadas).

## 1. Conclusão em uma página

Das 238 "oportunidades abertas" do painel, **apenas 4 são aplicáveis** à associação (2%); **155 são dispensáveis** (65%) e **79 não se aplicam** (33%). O número 238 mede o que os motores *encontraram*, não o que a entidade *pode disputar*: a maior parte é edital legítimo de OSC, mas de outro município ou estado (exige sede/atuação local), e o restante é ruído — licitação, concurso, ato de diário, página de agregador, catadores, artistas pessoa física.

| Veredito | Qtde | Leitura |
|---|---:|---|
| APLICÁVEL | 4 | investir esforço agora (1 chamamento em Goiânia; 2 fluxos contínuos — SEDS/GO e iCS; 1 fonte recorrente — MPT/GO) |
| DISPENSÁVEL | 155 | real, mas inaplicável hoje: território, ato acessório, duplicata, prazo, serviço especializado, fonte não verificável |
| NÃO APLICA | 79 | não é fomento a OSC como a associação: licitação, RH, concurso, público-alvo incompatível, ato de diário, residência no exterior |

**Prioridade absoluta:** o **Chamamento Público nº 001/2026 da SEGENP/Prefeitura de Goiânia — "Natal no Parque – A Magia de Brincar"** (termo de colaboração com OSC, até **R$ 5.000.000,00**, protocolo único até **26/10/2026**, resultado definitivo em 06/11/2026). Li o edital no Diário Oficial de 25/09/2026: exige ≥ 1 ano de CNPJ ativo (ou 5 anos, se a proposta for em rede) e experiência prévia em objeto semelhante. A entidade atende ao critério de CNPJ com folga; a decisão de negócio é sobre capacidade técnica/cenográfica (ver seção 6).

**Dois alertas de qualidade dos motores** (detalhados na seção 9): (i) 39 registros caíram no balde "nacional" do painel sem serem nacionais — são editais de municípios identificáveis; (ii) em registros de "menção em diário oficial" o campo *objeto* vem de outro trecho da edição (crédito suplementar, concurso, plano municipal) enquanto o ato validado era chamamento.

## 2. Prompt aprimorado (executado em sequência, um bloco por vez)

> Considere as 238 oportunidades abertas não confirmadas do painel de 02/10/2026. Divida em 20 blocos de até 12 registros. Para cada registro: (1) verifique injeção de prompt no texto coletado; (2) confira, na fonte oficial quando acessível, os 12 itens (objeto, prazo de inscrição, resultado, prazo de recurso, valor, órgão/financiador, território, esfera, requisitos, anexos, destinação, área); (3) decida se é fomento a OSC e se se aplica à associação (Goiânia/GO; assistência social, cultura, esporte, educação, saúde, criança e adolescente, idosos, meio ambiente, cidadania, desenvolvimento local, comunicação comunitária); (4) classifique em APLICÁVEL / DISPENSÁVEL / NÃO APLICA com código de regra e motivo escrito; (5) nada inventado — lacuna vira pendência; (6) ao final, consolide regras de restrição para os livros e as próximas pesquisas, teste-as contra a própria validação e confira por revisor independente.

## 3. Método, evidências e limites

- **Injeção de prompt:** varredura com os padrões do sistema (PT/EN) sobre todos os campos dos 238 registros — **0 ocorrências**. Todo texto coletado foi tratado como dado.
- **Níveis de evidência por registro** (coluna *Evidência* da planilha): PNCP consultado ao vivo em 02/10/2026 (108 registros: modalidade, situação, abertura e encerramento de propostas, valor); edital lido ao vivo (Natal no Parque); páginas oficiais lidas ao vivo (SEDS/GO, BNDES, Dia de Doar); validação anterior de 27–29/09 + dados do painel (55); e dados do painel sem fonte oficial confirmada (70) — estes últimos nunca recebem APLICÁVEL.
- **Os 12 itens:** ● comprovado em fonte · ◐ dispensa provável pelo regime · – dispensado pelo edital · ○ não comprovado. Para os NÃO APLICA a matriz é informativa; o item só importa para os APLICÁVEL.
- **Limites declarados:** não pude abrir ao vivo as páginas de ~120 prefeituras (bloqueio do ambiente e custo); para elas valem os dados do painel e a validação de 27–29/09. O PNCP respondeu 429 (limite de taxa) no primeiro passe; refiz com intervalo e obtive 108 de 109 consultas (o item 237 ficou sem dado ao vivo).
- **Conceitos:** NÃO APLICA = a natureza ou o público não é fomento a OSC como a associação. DISPENSÁVEL = é oportunidade real para OSC, mas hoje inaplicável (território, prazo, ato acessório, duplicata, serviço técnico especializado, fonte não verificável). APLICÁVEL = vigente, elegível, território compatível — sempre *a confirmar* na fonte oficial antes de protocolar.

## 4. Resultado por regra

| Regra | Veredito | Descrição | Qtde |
|---|---|---|---:|
| NA-01 | NÃO APLICA | Ato do diário oficial que não é chamamento | 1 |
| NA-02 | NÃO APLICA | Licitação, contratação de fornecedor ou serviço | 12 |
| NA-03 | NÃO APLICA | Recursos humanos (concurso, seleção, estágio, aprendizagem) | 2 |
| NA-04 | NÃO APLICA | Página genérica, agregador, notícia ou link sem edital | 3 |
| NA-05 | NÃO APLICA | Concurso ou prêmio sem fomento a OSC | 7 |
| NA-06 | NÃO APLICA | Público-alvo incompatível com a associação | 49 |
| NA-07 | NÃO APLICA | Conselho, eleição ou representação (sem recurso) | 2 |
| NA-08 | NÃO APLICA | Residência artística ou programa de artista individual no exterior | 3 |
| DI-01 | DISPENSÁVEL | Território incompatível (fora de Goiânia/GO e sem abrangência nacional) | 115 |
| DI-02 | DISPENSÁVEL | Região restrita do edital | 1 |
| DI-03 | DISPENSÁVEL | Prazo encerrado, revogado ou suspenso | 2 |
| DI-04 | DISPENSÁVEL | Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado | 13 |
| DI-05 | DISPENSÁVEL | Não verificável — sem fonte oficial confirmada | 13 |
| DI-06 | DISPENSÁVEL | Serviço técnico especializado exige qualificação que o perfil não comprova | 2 |
| DI-08 | DISPENSÁVEL | Duplicata de outro registro da lista | 9 |
| AP-01 | APLICÁVEL | Goiânia/GO, vigente e elegível a OSC | 1 |
| AP-03 | APLICÁVEL | Fluxo contínuo ou recorrente para OSC | 3 |

| Origem geográfica no painel | APLICÁVEL | DISPENSÁVEL | NÃO APLICA |
|---|---:|---:|---:|
| Goiás | 3 | 11 | 12 |
| balde "nacional" do painel | 1 | 28 | 10 |
| outras UFs | 0 | 116 | 57 |

## 5. Os aplicáveis (ordem de ação)

**#184 — Diário Oficial de Goiânia (GO) 2026-09-25 — "edital de chamamento público" associação** · Goiânia/GO · regra AP-01 · prazo: 2026-10-26 · evidência: edital lido ao vivo (Diário Oficial de Goiânia 25/09)

Goiânia/SEGENP — Chamamento Público nº 001/2026 "Natal no Parque – A Magia de Brincar" (Lei 13.019): termo de colaboração com OSC, valor máximo R$ 5.000.000,00; protocolo único até 26/10/2026, resultado definitivo em 06/11/2026. Exige ≥ 1 ano de CNPJ ativo (a entidade tem 39 anos de CNPJ) e experiência prévia em objeto semelhante (eventos culturais). Edital lido no Diário Oficial de 25/09/2026 (págs. 6–17). Pendência: o portal da Prefeitura ainda não publica página própria — conferir com a SEGENP.

**#199 — Goiás Social aumenta repasse do Auxílio Nutricional às entidades filantrópicas** · GO · regra AP-03 · prazo: fluxo contínuo (até 08/2027) · evidência: validação anterior (27–29/09) + dados do painel

SEDS/GO — Credenciamento nº 001/2026 em fluxo contínuo (12 meses a partir de 27/08/2026) para OSC atuantes em Goiás (Auxílio Nutricional e/ou Água e Energia); sem data-limite. Conferir no edital se o público atendido (entidades que acolhem/atendem pessoas em vulnerabilidade) abrange a atividade da associação.

**#187 — Editais de Destinação de Recursos ou Bens** · GO · regra AP-03 · prazo: recorrente (cada edital ≈ 5 dias; 9282.2026 vencido/no limite) · evidência: validação anterior (27–29/09) + dados do painel

MPT/PRT-18 (Goiás) — página permanente de editais de destinação de recursos de TAC (fonte recorrente, validada em 29/09). O edital em curso (9282.2026, R$ 150.000,00, publicado em 25/09, prazo de 5 dias) já está vencido ou vence hoje; o edital anterior (8927.2026) também encerrou. Valor da fonte: monitorar a página e manter projeto social pronto para indicação a cada novo edital.

**#86 — Como Solicitar uma Doação** · nacional · regra AP-03 · prazo: fluxo contínuo · evidência: validação anterior (27–29/09) + dados do painel

Instituto Clima e Sociedade (iCS) — recebe propostas espontâneas o ano todo (fluxo contínuo), nacional. Aderência limitada à agenda de clima/meio ambiente; esforço baixo para enviar consulta.

## 6. Natal no Parque (#184): o que a proposta precisa conter e o que decidir

Tópicos que devem constar na proposta (Proposta + Documentação de Habilitação, protocolo único até 26/10/2026, e-mail com assunto padronizado indicado no edital):

1. Projeto técnico e plano de trabalho alinhados ao objeto — celebração natalina gratuita com lazer, cultura e entretenimento, incluindo produção cenográfica natalina e decoração temática, planejamento técnico/operacional e gestão de riscos.
2. Comprovação de ≥ 1 ano de cadastro ativo no CNPJ (a associação tem CNPJ desde 1987); se houver atuação em rede, o edital exige 5 anos — a associação cumpre.
3. Comprovação de experiência prévia em objeto semelhante (eventos culturais comunitários da entidade; juntar fotos, listas de presença, relatórios, cartas de órgãos parceiros).
4. Capacidade técnica, operacional e cenográfica compatível: ou própria, ou por rede com produtora/parceiros — decisão de negócio.
5. Declarações exigidas (inexistência de impedimentos, CADIN estadual, dirigentes, vedações da Lei 13.019) e regularidade fiscal, trabalhista e contábil. No perfil da entidade constam como pendentes: estatuto atualizado, ata de eleição vigente, certidões e comprovação das utilidades públicas.
6. Orçamento detalhado dentro do teto de R$ 5 milhões, com cronograma, contrapartidas e plano de prestação de contas.
7. Calendário legal para controle: esclarecimentos até 15/10, impugnação até 19/10, protocolo até 26/10, avaliação em 27/10, recursos de 29/10 a 05/11, resultado definitivo em 06/11/2026.

**Perguntas para melhorar as chances (decisão do titular):** (a) a entidade já realizou evento natalino/comunitário de porte e tem comprovação documental? (b) há produtora ou empresa de cenografia disposta a atuar em rede, e com que contrato? (c) o estatuto atual e a ata de eleição estão regulares e registrados? (d) há capacidade de pré-financiar a execução até o repasse? (e) o presidente quer concorrer ao teto de R$ 5 mi ou a proposta de menor escala, se o edital permitir?

## 7. Conselho de 7 lentes

Composição (perfis, sem nomes reais): ministro(a) de tribunal superior com perfil processualista; doutrinador(a) de direito administrativo e parcerias com o terceiro setor (Lei 13.019); advogado(a) pós-doutor(a) em direito do terceiro setor; ministro(a) de corte de contas; doutrinador(a) de direito tributário das entidades sem fins lucrativos; advogado(a) pós-doutor(a) em compliance e integridade; e magistrado(a) de segunda instância com visão prática de execução.

1. **Extremamente pessimista (processualista rigoroso):** "Dos 238 registros, nenhum deveria virar *oportunidade aberta* sem o edital em mãos. O painel mistura o vetor (diário, agregador, notícia) com o ato. O risco é protocolar proposta com base em objeto mal extraído e perder prazo de impugnação. Até o Natal no Parque só está lido num diário, e a Prefeitura ainda não publicou página própria: exija a cópia integral e o recibo de protocolo."
2. **Pessimista (administrativista):** "O MROSC admite exigência de experiência prévia e capacidade técnica (art. 33); a associação tem 39 anos de CNPJ (43 de fundação) mas documentos pendentes (estatuto, ata, certidões). Um chamamento de R$ 5 mi sem estrutura de execução é risco de inadimplemento e de glosa na prestação de contas. O universo restante é, em quase tudo, fora do território: aplicar a regra de sede local é correto."
3. **Levemente pessimista (tributarista do terceiro setor):** "O fluxo contínuo da SEDS e o iCS são mais seguros que o megaedital, mas pedem enquadramento da atividade. A utilidade pública estadual é apenas alegada; sem prova, perde-se pontuação e acesso a algumas fontes."
4. **Neutro (ponderador imparcial):** "A validação reduz 238 para 4 com critério explícito e reprodutível: 92% das decisões são reproduzidas por regra (calibrada no mesmo conjunto — ver seção 11) e as divergências são justamente os casos que só a leitura do ato resolve. Recomendo: (i) Natal no Parque como projeto prioritário, condicionado à confirmação com a SEGENP e à decisão sobre execução em rede; (ii) abrir os fluxos contínuos como trilha de baixo esforço; (iii) tratar #108 (FNMA/incêndios) e #87 (próxima edição do Dia de Doar) como pendências com dono e data; (iv) aplicar as regras de restrição nos livros para que o funil pare de crescer com ruído. Parâmetros de qualidade: nenhum APLICÁVEL sem objeto, prazo e página oficial; revalidar semanalmente; arquivar com o código da regra, nunca apagar."
5. **Levemente otimista (doutrinador de parcerias):** "A capital goiana abriu um termo de colaboração de R$ 5 mi com requisitos que a entidade cumpre no papel (CNPJ de 1987, eventos culturais). O mesmo edital permite proposta em rede — caminho para suprir o que faltar sem descaracterizar a OSC."
6. **Otimista (compliance):** "A limpeza do funil é, por si só, ganho: 234 registros saem do radar sem perda de oportunidade real, e os padrões aprendidos barram o mesmo ruído nas próximas coletas. O MPT/GO e a SEDS são fontes recorrentes de recursos para entidades goianas."
7. **Extremamente otimista (magistrado prático):** "Com a trilha de recorrência (MPT, SEDS, FNMA, iCS, Dia de Doar) mais o Natal no Parque, a entidade pode montar uma carteira diversificada ainda neste trimestre, e o desenho das regras permite que cada novo edital goiano seja reconhecido em minutos."

**Decisão final do ponderador:** adotar a classificação deste parecer; priorizar #184, #199 e #187; confirmar #86 e acompanhar #108 e #87; incorporar as regras de restrição (arquivo de atualização dos livros) e as regras de coleta RC-01 a RC-06.

## 8. Blocos de 12 — item a item

Legenda da matriz: **Obj** objeto · **Pzo** prazo de inscrição · **Res** resultado · **Rec** prazo de recurso · **Val** valor · **Órg** órgão/financiador · **Ter** território · **Esf** esfera · **Req** requisitos · **Anx** anexos · **Dst** destinação · **Áre** área. ● comprovado · ◐ dispensa provável · – dispensado · ○ não comprovado.

### Bloco 01 — itens 1 a 12 (aplicável 0 · dispensável 9 · não aplica 3)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Andradina/SP · Diário Oficial de Andradina (SP) 2026-09-18 — "edital de chama | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 2 | Campinas/SP · Diário Oficial de Campinas (SP) 2026-07-31 — "chamamento públi | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 3 | Campinas/SP · Diário Oficial de Campinas (SP) 2026-09-11 — "chamamento públi | DISPENSÁVEL | DI-01 +DI-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 4 | Iracemápolis/SP · Diário Oficial de Iracemápolis (SP) 2026-08-14 — "edital de ch | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 5 | Itapeva/SP · Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de chamame | DISPENSÁVEL | DI-04 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 6 | Macatuba/SP · Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de chamam | NÃO APLICA | NA-02 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ○ |
| 7 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-17 — "edital de cham | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 8 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-17 — "edital de cham | NÃO APLICA | NA-02 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ | ○ |
| 9 | Mogi Guaçu/SP · Diário Oficial de Mogi Guaçu (SP) 2026-09-25 — "chamamento púb | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 10 | Monteiro Lobato/SP · Diário Oficial de Monteiro Lobato (SP) 2026-09-11 — "edital de | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 11 | Monteiro Lobato/SP · Diário Oficial de Monteiro Lobato (SP) 2026-09-15 — "edital de | NÃO APLICA | NA-06 +DI-08 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 12 | Valinhos/SP · Diário Oficial de Valinhos (SP) 2026-09-25 — "edital de chamam | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |

- **#1** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Andradina/SP — novo edital PNAB com recursos remanescentes (R$ 60.536,52) — Andradina/SP.
- **#2** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Campinas/SP — Diário Oficial de Campinas (SP) 2026-07-31 — "chamamento público" "organizações da sociedade civil" — Prefeitura Municipal de Campinas.
- **#3** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Campinas/SP — edital 02/2026 acolhimento institucional de crianças — OSC (Campinas/SP).
- **#4** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Iracemápolis/SP — PNAB 008/2026 (Iracemápolis/SP).
- **#5** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapeva/SP — PNAB 01/2026 Pontos de Cultura — prorrogação das inscrições (Itapeva/SP).
- **#6** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Macatuba/SP — credenciamento de pessoas jurídicas para prestação de serviços de agenciamento de viagens corporativas.
- **#7** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Mogi Guaçu/SP — edital 28/SECULT/2026 Natal Encantado — seleção de OSC (Mogi Guaçu/SP).
- **#8** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Mogi Guaçu/SP — REGISTRO DE PREÇOS PELO PERÍODO DE 12 (DOZE) MESES, PARA AQUISIÇÕES FUTURAS DE MATERIAIS DE HIGIENE E LIMPEZA PARA ATENDER A DEMANDA DAS SECRETARIAS MUNICIPAIS DA PREFEIT.
- **#9** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Mogi Guaçu/SP — PNAB 33/2026 subsídio a espaços culturais (Mogi Guaçu/SP).
- **#10** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Monteiro Lobato/SP — PNAB 02/SMCT/2026 termo de execução cultural (Monteiro Lobato/SP).
- **#11** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Monteiro Lobato/SP — PNAB 03/SMCT/2026 premiação mestres (Monteiro Lobato/SP) — mesma oportunidade de 23222c6d.
- **#12** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Valinhos/SP — edital de chamamento 03/2026 — Secretaria de Desenvolvimento Social (Valinhos/SP); objeto não visível no trecho.

### Bloco 02 — itens 13 a 24 (aplicável 0 · dispensável 8 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 13 | Valinhos/SP · Diário Oficial de Valinhos (SP) 2026-09-25 — "edital de chamam | DISPENSÁVEL | DI-05 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ● |
| 14 | Valparaíso/SP · Diário Oficial de Valparaíso (SP) 2026-08-27 — "edital de cham | NÃO APLICA | NA-06 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 15 | Valparaíso/SP · Diário Oficial de Valparaíso (SP) 2026-09-16 — "edital de cham | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 16 | Ourinhos/SP · Edital Prefeitura de Ourinhos 2026: Saúde | DISPENSÁVEL | DI-05 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 17 | SP · Seleção de propostas para a celebração de parceria entre o Mun | NÃO APLICA | NA-02 +DI-03 | 2026-09-25 (encerrado) | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 18 | Itatinga/SP · MUNICIPIO DE ITATINGA — Seleção de projetos para firmar termo  | DISPENSÁVEL | DI-01 | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 19 | Sao Jose Do Rio Preto/SP · MUNICIPIO DE SAO JOSE DO RIO PRETO — O PRESENTE CHAMAMENTO TEM | DISPENSÁVEL | DI-01 | 2026-10-05 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 20 | Porto Feliz/SP · MUNICIPIO DE PORTO FELIZ — PREMIO CULTURAL COM RECURSOS DA POL | NÃO APLICA | NA-06 +DI-01 | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 21 | SP · SECRETARIA MUNICIPAL DE EDUCACAO — Contratação, pelo PODER CON | NÃO APLICA | NA-02 | 2026-10-16 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 22 | Ibate/SP · MUNICIPIO DE IBATE — ABERTURA DE EDITAL PARA SELEÇÃO DE PROJET | DISPENSÁVEL | DI-01 | 2026-10-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 23 | Jacarei/SP · MUNICIPIO DE JACAREI — CHAMADA PÚBLICA Nº 03/2026 - SEMAPLAN-  | DISPENSÁVEL | DI-01 +DI-06 | 2026-10-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 24 | Barretos/SP · MUNICIPIO DE BARRETOS — contratação de pessoa jurídica (organi | DISPENSÁVEL | DI-01 | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#13** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Valinhos/SP — Atendimento ambulatorial e hospitalar da rede municipal de saúde.
- **#14** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Valparaíso/SP — extrato do edital 002/2026 de premiação (Valparaíso/SP).
- **#15** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Valparaíso/SP — edital CMDCA 001/2026 seleção de propostas de OSC (Valparaíso/SP).
- **#16** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Ourinhos/SP — Edital Prefeitura de Ourinhos 2026: Saúde.
- **#17** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SP — Estudo de Impacto da Pandemia COVID-19 em empresas de Indaiatuba.
- **#18** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Itatinga/SP — Seleção de projetos para firmar termo de execução cultural com recursos da política nacional Aldir Blanc de fomento à cultura – PNAB (lei nº 14.399/2022) - Proc. Administ.
- **#19** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Sao Jose Do Rio Preto/SP — O PRESENTE CHAMAMENTO TEM POR OBJETO SELECIONAR 1 (UMA) PESSOA JURÍDICA DE DIREITO PRIVADO, COM OU SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COOPERAÇÃO CULTURAL DE.
- **#20** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Porto Feliz/SP — PREMIO CULTURAL COM RECURSOS DA POLITICA NACIONAL ALDIR BLANC DE FOMENTO A CULTURA NO MUNICIPIO DE PORTO FELIZ SP LEI N 14.399 2022.
- **#21** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SP — Contratação, pelo PODER CONCEDENTE, representado pela SECRETARIA MUNICIPAL DE EDUCAÇÃO (“CONTRATANTE”), de pessoa jurídica para atuar como VERIFICADOR INDEPENDENTE (“CONT.
- **#22** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Ibate/SP — ABERTURA DE EDITAL PARA SELEÇÃO DE PROJETOS CULTURAIS DE ACORDO COM A POLÍTICA NACIONAL ALDIR BLANC..
- **#23** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Jacarei/SP — CHAMADA PÚBLICA Nº 03/2026 - SEMAPLAN- SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL (OSC) PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO VISANDO A ATUAÇÃO VOLTADA A PROTEÇÃO E BEM-.
- **#24** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Barretos/SP — contratação de pessoa jurídica (organizações da sociedade civil sem fins lucrativos) para prestação de serviços culturais de produção técnica, sonorização, contratação de.

### Bloco 03 — itens 25 a 36 (aplicável 0 · dispensável 11 · não aplica 1)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 25 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO DE SELEÇÃO DE ORG | DISPENSÁVEL | DI-01 | 2026-12-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 26 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — CREDENCIAMENTO (OSC’S) DE EXECUÇ | DISPENSÁVEL | DI-01 | 2027-03-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 27 | SP · (UO) ESP-CIA.PTA DE TRENS METROPS-CPTM — Credenciamento de ass | NÃO APLICA | NA-06 | 2027-05-04 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 28 | Pindorama/SP · MUNICIPIO DE PINDORAMA — CREDENCIAMENTO DE ORGANIZACOES DA SOC | DISPENSÁVEL | DI-01 | 2027-05-12 | ● | ● | ○ | ○ | ◐ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 29 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO PARA PA | DISPENSÁVEL | DI-01 +DI-05 | 2030-11-25 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 30 | Artur Nogueira/SP · MUNICIPIO DE ARTUR NOGUEIRA — EDITAL DE CREDENCIAMENTO DE ORGA | DISPENSÁVEL | DI-01 +DI-05 | 2030-12-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 31 | Arataca/BA · Diário Oficial de Arataca (BA) 2026-09-23 — "edital de chamame | DISPENSÁVEL | DI-04 +DI-01 | 2027-03-12 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 32 | BA · Chamamento Público Nº 005/2026 para Seleção de Projetos para f | DISPENSÁVEL | DI-01 +DI-03 | 2026-09-29 (encerrado) | ● | ● | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 33 | Adustina/BA · Diário Oficial de Adustina (BA) 2026-09-18 — "chamamento públi | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ○ |
| 34 | Alcobaça/BA · Diário Oficial de Alcobaça (BA) 2026-08-28 — "edital de chamam | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 35 | Canudos/BA · Diário Oficial de Canudos (BA) 2026-08-05 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 36 | Canudos/BA · Diário Oficial de Canudos (BA) 2026-09-23 — "edital de chamame | DISPENSÁVEL | DI-04 +DI-01,DI-08 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |

- **#25** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Artur Nogueira/SP — CREDENCIAMENTO DE SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSC) PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO PARA A PRESTAÇÃO DE SERVIÇOS PARA ATENDIMENTO A ANIMAIS DE PEQU.
- **#26** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Artur Nogueira/SP — CREDENCIAMENTO (OSC’S) DE EXECUÇÃO DE PROJETO ESPORTIVO VOLTADO Á DIFUSÃO DO ESPORTE E LAZER POR MEIO DA MODALIDADE VOLEIBOL, INCLUINDO AÇÕES DE CONTRATURNO ESCOLAR, LAZE.
- **#27** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: SP — Credenciamento de associações e/ou cooperativas de catadores de materiais recicláveis para coleta, transporte, fragmentação/trituração e destinação/desfazimento de caixas.
- **#28** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Pindorama/SP — CREDENCIAMENTO DE ORGANIZACOES DA SOCIEDADE CIVIL DE PINDORAMA INTERESSADA EM RECEBER DOACAO DE BENS MOVEIS CONSIDERADOS INSERVIVEIS PERTENCENTES AO MUNICIPIO CONSTANTES .
- **#29** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Artur Nogueira/SP — EDITAL DE CREDENCIAMENTO PARA PARCERIA EM REGIME DE COLABORAÇÃO ENTRE A SECRETARIA DE EDUCAÇÃO E ORGANIZAÇÃO DA SOCIEDADE CIVIL. A PARCERIA CONSISTIRÁ NA OFERTA DE ATENDI.
- **#30** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Artur Nogueira/SP — EDITAL DE CREDENCIAMENTO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL (OSC´S) PARA PRESTAÇÃO DE SERVIÇOS EM ATENDIMENTO À DEMANDA DESTA SECRETARIA DE CULTURA NO MUNICÍPIO DE ARTUR N.
- **#31** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Arataca/BA — PNAB 02/2026 — prorrogação do cronograma (Arataca/BA).
- **#32** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: BA — seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), com recursos da Política Nacional Aldir Blanc .
- **#33** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Adustina/BA — chamamento para credenciar OSC — Programa Integrado (Adustina/BA).
- **#34** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Alcobaça/BA — PNAB 002 e 0003/2026 criação de projetos culturais (Alcobaça/BA).
- **#35** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Canudos/BA — PNAB 02/2026 termo de execução cultural (Canudos/BA) — mesma oportunidade de b5525976.
- **#36** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Canudos/BA — PNAB 02/2026 — alteração de cronograma (Canudos/BA).

### Bloco 04 — itens 37 a 48 (aplicável 0 · dispensável 9 · não aplica 3)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 37 | Inhambupe/BA · Diário Oficial de Inhambupe (BA) 2026-08-12 — "edital de chama | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 38 | Ipiaú/BA · Diário Oficial de Ipiaú (BA) 2026-09-17 — "edital de chamament | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 39 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-08-21 — "edital de cham | NÃO APLICA | NA-06 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 40 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-09-16 — "edital de cham | DISPENSÁVEL | DI-04 +DI-01,NA-02 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ | ○ |
| 41 | Itapetinga/BA · Diário Oficial de Itapetinga (BA) 2026-09-21 — "chamamento púb | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 42 | Ituaçu/BA · Diário Oficial de Ituaçu (BA) 2026-08-20 — "chamamento público | DISPENSÁVEL | DI-01 | — | ● | – | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 43 | Olindina/BA · o Chamamento Público nº 002/2026, destinado à seleção de proje | DISPENSÁVEL | DI-08 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 44 | BA · COMPANHIA DE PESQUISA DE RECURSOS MINERAIS — Programa de Apren | NÃO APLICA | NA-03 +DI-03 | 2026-10-08 (revogado) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 45 | Jaguaripe/BA · MUNICIPIO DE JAGUARIPE — Constitui objeto do presente Edital a | DISPENSÁVEL | DI-01 | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 46 | Olindina/BA · MUNICIPIO DE OLINDINA — o Chamamento Público nº 002/2026, dest | DISPENSÁVEL | DI-01 | 2026-10-13 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 47 | Itagiba/BA · MUNICIPIO DE ITAGIBA — Chamamento Público a seleção de associa | NÃO APLICA | NA-06 | 2026-10-14 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 48 | Lauro De Freitas/BA · MUNICIPIO DE LAURO DE FREITAS — Concessão de apoio financeiro  | DISPENSÁVEL | DI-01 | 2026-10-15 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#37** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Inhambupe/BA — edital PNAB de subsídio a culturas populares (Inhambupe/BA).
- **#38** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Ipiaú/BA — edital PNAB 01/2026 Virada Cultural (repetição publicada por Mutuípe/BA).
- **#39** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Itapetinga/BA — edital 07/2026 apresentação musical MPB — agentes culturais (Itapetinga/BA).
- **#40** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapetinga/BA — retificação de edital de chamamento (educação/cultura, Itapetinga/BA).
- **#41** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Itapetinga/BA — errata do aviso de chamamento 006/2026 (Itapetinga/BA) — objeto não visível.
- **#42** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Ituaçu/BA — PNAB 003/2026 festividade cultural e religiosa (Ituaçu/BA).
- **#43** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #46: Olindina/BA — seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), com recursos da Política Nacional Aldir Blanc 
- **#44** (PNCP consultado ao vivo em 02/10/2026): É seleção de pessoas (estágio/aprendizagem/processo seletivo), não de entidade: BA — Programa de Aprendizagem, com dois Jovens Aprendizes, para atuação junto à Companhia de Pesquisa de Recursos Minerais - CPRM / na Unidade Regional de Salvador, por até se.
- **#45** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Jaguaripe/BA — Constitui objeto do presente Edital a seleção de Organização da Sociedade Civil (OSC), regularmente constituída, para celebração de TERMO DE COLABORAÇÃO, em regime de mút.
- **#46** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Olindina/BA — o Chamamento Público nº 002/2026, destinado à seleção de projetos culturais para execução de oficinas de música, mediante celebração de Termo de Execução Cultural (TEC), .
- **#47** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Itagiba/BA — Chamamento Público a seleção de associação ou cooperativa de catadores de materiais recicláveis para a CONTRATAÇÃO REMUNERADA da prestação continuada e integrada dos serv.
- **#48** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Lauro De Freitas/BA — Concessão de apoio financeiro para execução de projetos culturais, no âmbito da Política Nacional Aldir Blanc de Fomento à Cultura – PNAB, instituída pela Lei Federal nº .

### Bloco 05 — itens 49 a 60 (aplicável 0 · dispensável 11 · não aplica 1)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 49 | Santo Antonio De Jesus/BA · MUNICIPIO DE SANTO ANTONIO DE JESUS — Seleção de Organização d | DISPENSÁVEL | DI-01 | 2026-11-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 50 | Rio Real/BA · MUNICIPIO DE RIO REAL — EDITAL DE CREDENCIAMENTO Nº 012/2026,  | DISPENSÁVEL | DI-01 | 2026-11-28 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 51 | Feira De Santana/BA · MUNICIPIO DE FEIRA DE SANTANA — CHAMAMENTO PÚBLICO QUE TEM POR | DISPENSÁVEL | DI-01 | 2026-12-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 52 | Feira De Santana/BA · MUNICIPIO DE FEIRA DE SANTANA — TERMO DE FOMENTO QUE ENTRE SI  | DISPENSÁVEL | DI-01 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 53 | Olindina/BA · MUNICIPIO DE OLINDINA — Chamamento Público é o credenciamento  | NÃO APLICA | NA-06 +DI-01 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 54 | BA · FUNDO MUNICIPAL DE SAUDE DE JEQUIE — 1.1. Contratação de Organ | DISPENSÁVEL | DI-01 +DI-06 | 2027-09-14 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 55 | PR · Chamamento Público para firmar Termo de Colaboração com Organi | DISPENSÁVEL | DI-08 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 56 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-11 — "edital de chama | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 57 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-16 — "edital de chama | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 58 | Arapongas/PR · Diário Oficial de Arapongas (PR) 2026-09-17 — "edital de chama | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ○ |
| 59 | Londrina/PR · Diário Oficial de Londrina (PR) 2026-09-18 — "edital de chamam | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 60 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-08-21 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |

- **#49** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Santo Antonio De Jesus/BA — Seleção de Organização da Sociedade Civil – OSC para a celebração de TERMO DE COLABORAÇÃO, em regime de mútua cooperação, na forma e nas condições estabelecidas neste Edi.
- **#50** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Rio Real/BA — EDITAL DE CREDENCIAMENTO Nº 012/2026, PARA FINS DE CREDENCIAR ORGANIZAÇÕES DA SOCIEDADE CIVIL PARA EVENTUAL CELEBRAÇÃO DE TERMO DE COLABORAÇÃO OU TERMO DE FOMENTO, DE ACO.
- **#51** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Feira De Santana/BA — CHAMAMENTO PÚBLICO QUE TEM POR FINALIDADE A SELEÇÃO DE PROPOSTAS DE INSTITUIÇÃO DE LONGA PERMANENCIA PARA IDOSOS E ORGANIZAÇÕES DA SOCIEDADE CIVIL DE ATENDIMENTO, PARA EX.
- **#52** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Feira De Santana/BA — TERMO DE FOMENTO QUE ENTRE SI CELEBRAM A SECRETARIA MUNICIPAL DA EDUCAÇÃO DE FEIRA DE SANTANA E A ORGANIZAÇÃO DA SOCIEDADE CIVIL SELECIONADA POR MEIO DE CHAMAMENTO PÚBLIC.
- **#53** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Olindina/BA — Chamamento Público é o credenciamento de artistas, grupos e coletivos culturais para compor a programação dos eventos realizados pela SECELT no exercício de 2026, nas seg.
- **#54** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: BA — 1.1. Contratação de Organização da Sociedade Civil (OSC) para prestação de serviços de reabilitação intelectual, para crianças, jovens e adultos com deficiência intelectu.
- **#55** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #66: PR — concessão de apoio da administração pública municipal para a execução de atividade tipificada como Serviço de Educação Básica de Atendimento Educacionais Especializado pa
- **#56** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Arapongas/PR — Programa Jovens Araponguenses pelo Clima (YCAF) — retificação de cronograma.
- **#57** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Arapongas/PR — edital 050/2026 vagas remanescentes "João de Barro" — ações formativas (Arapongas/PR).
- **#58** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Arapongas/PR — edital 052/2026 vagas remanescentes "Som do Rouxinol" — retificação (Arapongas/PR).
- **#59** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Londrina/PR — edital 004/2026 termo de execução cultural (Londrina/PR).
- **#60** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Pinhais/PR — PNAB 050/2026 apoio a projetos de fomento (Pinhais/PR).

### Bloco 06 — itens 61 a 72 (aplicável 0 · dispensável 7 · não aplica 5)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 61 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-08-28 — "chamamento públic | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 62 | Pinhais/PR · Diário Oficial de Pinhais (PR) 2026-09-23 — "edital de chamame | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 63 | Primeiro de Maio/PR · Diário Oficial de Primeiro de Maio (PR) 2026-08-28 — "edital d | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 64 | Cafelandia/PR · MUNICIPIO DE CAFELANDIA — CONSTITUI OBJETO DO PRESENTE CHAMAME | DISPENSÁVEL | DI-01 | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 65 | PR · FUNDACAO ESTATAL DE ATENCAO EM SAUDE DO ESTADO DO PARANA - FUN | NÃO APLICA | NA-02 | 2026-10-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 66 | Guaira/PR · MUNICIPIO DE GUAIRA — Chamamento Público para firmar Termo de  | DISPENSÁVEL | DI-01 | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 67 | Cafelandia/PR · MUNICIPIO DE CAFELANDIA — SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE | DISPENSÁVEL | DI-01 | 2026-10-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 68 | Ivaipora/PR · MUNICIPIO DE IVAIPORA — PREMIAÇÃO POR TRAJETÓRIA, PREVISTO EM  | NÃO APLICA | NA-06 +DI-01 | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 69 | PR · DEFENSORIA PUBLICA DO ESTADO DO PARANA — O objeto do presente  | NÃO APLICA | NA-06 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 70 | Campina Da Lagoa/PR · MUNICIPIO DE CAMPINA DA LAGOA — Chamamento Público de Institui | NÃO APLICA | NA-06 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 71 | Clevelandia/PR · MUNICIPIO DE CLEVELANDIA — Chamamento Público destinado à sele | DISPENSÁVEL | DI-01 | 2027-02-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 72 | Quatigua/PR · MUNICIPIO DE QUATIGUA — Credenciamento para seleção de associa | NÃO APLICA | NA-06 | 2027-04-22 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#61** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Pinhais/PR — PNAB 051/2026 subsídio a espaços (Pinhais/PR).
- **#62** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Pinhais/PR — PNAB 51/2026 — reabertura do prazo de inscrições (Pinhais/PR).
- **#63** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Primeiro de Maio/PR — PNAB 001/2026 ciclo II fomento direto PF/PJ (Primeiro de Maio/PR).
- **#64** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Cafelandia/PR — CONSTITUI OBJETO DO PRESENTE CHAMAMENTO PÚBLICO A SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL – OSC, SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO COM O MUNI.
- **#65** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): PR — Contratação de entidade qualificada em formação técnico-profissional metódica, habilitada junto ao Ministério do Trabalho e Emprego, para prestação de serviços de aprendi.
- **#66** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Guaira/PR — Chamamento Público para firmar Termo de Colaboração com Organização da Sociedade Civil, sem fins lucrativos, que execute Serviço de Educação Básica e de Atendimento Educa.
- **#67** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Cafelandia/PR — SELEÇÃO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL - OSCS, SEM FINS LUCRATIVOS, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO, NOS TERMOS DA LEI FEDERAL Nº 13.019/2014, VISANDO À EXECU.
- **#68** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Ivaipora/PR — PREMIAÇÃO POR TRAJETÓRIA, PREVISTO EM PLANO DE AÇÃO DA PNAB, EM ATENDIMENTO ÀS NECESSIDADES DA SECRETARIA MUNICIPAL DE CULTURA.
- **#69** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PR — O objeto do presente credenciamento selecionar associações e/ou cooperativas de catadores de materiais recicláveis para o recolhimento e a destinação de resíduos recicláv.
- **#70** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Campina Da Lagoa/PR — Chamamento Público de Instituições/Associações Estudantis e de Acadêmicos, sem ?ns lucrativos, regularmente constituídas, localizadas no Município de Campina da Lagoa, e .
- **#71** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Clevelandia/PR — Chamamento Público destinado à seleção de projetos de Organizações da Sociedade Civil - OSCs, regularmente registradas e atualizadas junto ao Conselho Municipal dos Direi.
- **#72** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Quatigua/PR — Credenciamento para seleção de associação de estudantes regularmente constituída, sem fins lucrativos, para a cessão de uso, a título gratuito e precário, de 01 (um) veíc.

### Bloco 07 — itens 73 a 84 (aplicável 0 · dispensável 1 · não aplica 11)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 73 | Castro/PR · MUNICIPIO DE CASTRO — CHAMAMENTO PÚBLICO PARA FINS DE CREDENCI | NÃO APLICA | NA-06 | 2027-06-11 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 74 | Ceu Azul/PR · MUNICIPIO DE CEU AZUL — CREDENCIAMENTO de Instituições de Long | NÃO APLICA | NA-06 | 2027-06-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 75 | Guaira/PR · MUNICIPIO DE GUAIRA — Credenciamento de cooperativas de crédit | NÃO APLICA | NA-06 | 2027-07-21 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 76 | Rio Branco Do Sul/PR · MUNICIPIO DE RIO BRANCO DO SUL — Credenciamento de associações | NÃO APLICA | NA-06 | 2028-03-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 77 | Telemaco Borba/PR · MUNICIPIO DE TELEMACO BORBA — Credenciamento de cooperativas e | NÃO APLICA | NA-06 | 2030-08-16 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 78 | Simão Dias/SE · Diário Oficial de Simão Dias (SE) 2026-08-17 — "edital de cham | DISPENSÁVEL | DI-08 +DI-01 | — | ● | ○ | ● | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 79 | DF · COMPANHIA NACIONAL DE ABASTECIMENTO — Contratação de entidade  | NÃO APLICA | NA-02 | 2026-10-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 80 | DF · SERVICO DE LIMPEZA URBANA — Credenciamento de Cooperativas/Ass | NÃO APLICA | NA-06 | 2027-03-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 81 | DF · DNIT-DEPARTAMENTO NACIONAL DE INFRAEST DE TRANSPORTES — Seleçã | NÃO APLICA | NA-06 | 2028-09-22 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 82 | DF · TRIBUNAL SUPERIOR DO TRABALHO — Seleção de associações e coope | NÃO APLICA | NA-06 | 2028-12-04 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 83 | nacional · Delfina Foundation promove residência em Londres para artistas | NÃO APLICA | NA-08 | 2026-10-04 | ● | ● | ○ | ◐ | – | ● | ● | ● | ● | ● | ● | ○ |
| 84 | nacional · Braunschweig Projects 2027/2028 | NÃO APLICA | NA-08 | — | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |

- **#73** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Castro/PR — CHAMAMENTO PÚBLICO PARA FINS DE CREDENCIAMENTO DE COOPERATIVA OU ASSOCIAÇÃO OU DA INICI­ATIVA PRIVADA DE MATERIAIS RECICLÁVEIS ESPECIALIZADA NA EXECUÇÃO DE SERVIÇOS DE RE.
- **#74** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Ceu Azul/PR — CREDENCIAMENTO de Instituições de Longa Permanência para Idosos (ILPIs), que tenham interesse em prestar serviços de acolhimento institucional continuado para pessoas ido.
- **#75** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Guaira/PR — Credenciamento de cooperativas de crédito autorizadas a funcionar pelo Banco Central do Brasil e legalmente aptas à captação de recursos municipais, com dependência insta.
- **#76** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Rio Branco Do Sul/PR — Credenciamento de associações e/ou cooperativas de catadores de materiais recicláveis para a prestação de serviços de processamento e destinação adequada de resíduos sóli.
- **#77** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Telemaco Borba/PR — Credenciamento de cooperativas e associações de catadores de materiais recicláveis, bem como organizações não governamentais (ongs) sem fins lucrativos, para a coleta, re.
- **#78** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #224: Simão Dias/SE — Apoio à realização de projetos culturais em âmbito nacional.
- **#79** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): DF — Contratação de entidade sem fins lucrativos, inscrita e aprovada no Cadastro Nacional de Aprendizagem, com capacidade técnica e administrativa e que tenha por objetivo a .
- **#80** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Credenciamento de Cooperativas/Associações de Catadores, constituídas exclusivamente por pessoas físicas de baixa renda, para a prestação de serviços de manejo de resíduo.
- **#81** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Seleção de associações e/ou cooperativas de catadores de materiais recicláveis, cadastradas e habilitadas no Sistema Nacional de Informações sobre a Gestão de Resíduos Só.
- **#82** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: DF — Seleção de associações e cooperativas de catadores de materiais recicláveis aptas a recolherem os resíduos destinados à reciclagem produzidos pelo TST..
- **#83** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — residência em Londres para artistas visuais de Portugal e de Países Africanos de Língua Portuguesa.
- **#84** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — Residências artísticas em Alemanha.

### Bloco 08 — itens 85 a 96 (aplicável 1 · dispensável 11 · não aplica 0)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 85 | Cajuru (SP/MG) · Chamamento Público 1/2026: Prefeitura de Cajuru (Educação) | DISPENSÁVEL | DI-05 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ● |
| 86 | nacional · Como Solicitar uma Doação | APLICÁVEL | AP-03 | fluxo contínuo | ● | ● | – | – | – | ● | ● | ● | ● | ● | ● | ● |
| 87 | nacional · Dia de Doar abre inscrições para edital que oferece R$ 2,4 mil | DISPENSÁVEL | DI-03 | edição 2024 (encerrada) (encerrado | ● | – | ● | ○ | ● | ● | ● | ● | ○ | ● | ● | – |
| 88 | Itapeva/SP · Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de chamame | DISPENSÁVEL | DI-08 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 89 | Macatuba/SP · Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de chamam | DISPENSÁVEL | DI-08 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 90 | Potengi/CE · EDITAL DE SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS, AMBIENTES E INI | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 91 | nacional · Edital Ambev 2026: R$ 67M para Cultura e Esporte — Ambev | DISPENSÁVEL | DI-05 +DI-06 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 92 | Balsas/MA · Edital Balsas 2026: Guia de Captação e Inscrição — Prefeitura  | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 93 | CAU/PR (Paraná) · Edital CAU/PR 2026: Captação e Regras da Chamada Pública | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ○ |
| 94 | Curitiba/PR · Edital ContraFluxo 2026: Filme para ONGs de Curitiba | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 95 | Itagibá/BA · Edital Itagibá 2026: Guia de Captação e Inscrições | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 96 | Tauá/CE · Edital Tauá 2026: Guia de Captação e Inscrição | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |

- **#85** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Cajuru (SP/MG) — Chamamento Público 1/2026: Prefeitura de Cajuru (Educação).
- **#86** (validação anterior (27–29/09) + dados do painel): Instituto Clima e Sociedade (iCS) — recebe propostas espontâneas o ano todo (fluxo contínuo), nacional. Aderência limitada à agenda de clima/meio ambiente; esforço baixo para enviar consulta.
- **#87** (página oficial lida ao vivo): Dia de Doar/ABCR — edital de Apoio à Filantropia Comunitária (R$ 40 mil para 40 campanhas, R$ 1.000 cada); o painel registra resultado em 24/10/2024, ou seja, é a edição de 2024 (a notícia diz "4º edital" e o painel intitula "R$ 2,4 mil"). Edital da edição anterior = prazo encerrado. Acompanhar a abertura da próxima edição (a ação é anual, em torno de outubro/dezembro).
- **#88** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #5: Itapeva/SP — Diário Oficial de Itapeva (SP) 2026-09-23 — "edital de chamamento público" associação — Prefeitura Municipal de Itapeva
- **#89** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #6: Macatuba/SP — Diário Oficial de Macatuba (SP) 2026-09-22 — "edital de chamamento público" associação — Prefeitura Municipal de Macatuba/SP
- **#90** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Potengi/CE — EDITAL DE SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS, AMBIENTES E INICIATIVAS ARTÍSTICO-CULTURAIS.
- **#91** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — Edital Ambev 2026: R$ 67M para Cultura e Esporte — Ambev.
- **#92** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Balsas/MA — Edital Balsas 2026: Guia de Captação e Inscrição — Prefeitura Municipal de Balsas.
- **#93** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: CAU/PR (Paraná) — Edital CAU/PR 2026: Captação e Regras da Chamada Pública.
- **#94** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Curitiba/PR — Edital ContraFluxo 2026: Filme para ONGs de Curitiba.
- **#95** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Itagibá/BA — Edital Itagibá 2026: Guia de Captação e Inscrições.
- **#96** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Tauá/CE — Edital Tauá 2026: Guia de Captação e Inscrição.

### Bloco 09 — itens 97 a 108 (aplicável 0 · dispensável 9 · não aplica 3)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 97 | nacional · Gife cria fundo para incentivar doacoes | NÃO APLICA | NA-04 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 98 | nacional · Mover se na web lanca chamada para projetos de inovacao tecnol | DISPENSÁVEL | DI-05 | — | ● | – | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 99 | Norte e Nordeste · ONGs e coletivos periféricos do Nordeste podem se inscrever em | DISPENSÁVEL | DI-02 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ● | ○ |
| 100 | nacional · Prêmio nacional da Enap oferece até R$ 20 mil para iniciativas | NÃO APLICA | NA-05 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ● | ○ |
| 101 | nacional · Seleção de organização da sociedade civil – osc, sem fins lucr | DISPENSÁVEL | DI-05 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 102 | Itatinga/SP · Seleção de projetos para firmar termo de execução cultural com | DISPENSÁVEL | DI-08 +DI-01 | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 103 | ICISMEP (consórcio, MG) · 1.1. Constitui objeto do presente edital o credenciamento de I | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 104 | nacional · Contratação de prestação de serviço especializado de Produtor  | NÃO APLICA | NA-02 | 2026-10-06 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 105 | Espírito Santo (mapa cultural ES) · EDITAL DE CHAMAMENTO PÚBLICO Nº 16 /2026 - SELEÇÃO DE PROJETOS | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 106 | Ceará (mapa cultural CE) · EDITAL DE CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS - PNAB | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 107 | Sobral/CE · EDITAL DE FOMENTO AS LINGUAGENS ARTISTICAS DO MUNICIPIO DE SOB | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 108 | nacional · Editais de Fomento a Ações de Prevenção e Combate de Incêndios | DISPENSÁVEL | DI-05 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

- **#97** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: nacional — apoiar soluções inovadoras que criem condições favoráveis tanto para facilitar a conexão entre doadores e donatários, como para estreitar e aprofundar as relações de conf.
- **#98** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — projetos de inovação tecnológica que tenham potencial para impactar positivamente problemas sociais no Brasil.
- **#99** (página oficial lida ao vivo): BNDES Periferias Fortes — seleção de parceiro executor para territórios do Norte e Nordeste (investimento de até R$ 17,5 mi por parceiro; repasse de R$ 100–300 mil às OSPs capacitadas). Página lida ao vivo: Goiás fora da área.
- **#100** (dados do painel (sem fonte oficial confirmada)): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: nacional — Prêmio nacional da Enap oferece até R$ 20 mil para iniciativas que protegem crianças e adolescentes em situação de rua —.
- **#101** (dados do painel (sem fonte oficial confirmada)): Registro cujo link oficial é um placeholder (x.gov.br/edital): não há como comprovar o edital; vai para quarentena (RC-05) e só volta se a fonte real for localizada.
- **#102** (PNCP consultado ao vivo em 02/10/2026): Mesma oportunidade do registro #18: Itatinga/SP — Seleção de projetos para firmar termo de execução cultural com recursos da política nacional Aldir Blanc de fomento à cultura
- **#103** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: ICISMEP (consórcio, MG) — 1.1. Constitui objeto do presente edital o credenciamento de Instituições reconhecidas como Organizações da Sociedade Civil (OSC), nos moldes definidos pela Lei Federal n.
- **#104** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): nacional — Contratação de prestação de serviço especializado de Produtor Cultural para a Implementação e Curadoria… — ESTADO DA BAHIA.
- **#105** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Espírito Santo (mapa cultural ES) — EDITAL DE CHAMAMENTO PÚBLICO Nº 16 /2026 - SELEÇÃO DE PROJETOS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS - PNAB.
- **#106** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Ceará (mapa cultural CE) — EDITAL DE CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS - PNAB.
- **#107** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Sobral/CE — EDITAL DE FOMENTO AS LINGUAGENS ARTISTICAS DO MUNICIPIO DE SOBRAL – POLÍTICA NACIONAL ALDIR BLANC DE FOMENTO À CULTURA – PNAB.
- **#108** (dados do painel (sem fonte oficial confirmada)): MMA/FNMA — notícia sobre editais de R$ 34,5 mi para prevenção e combate a incêndios florestais. Não há objeto, prazo, público-alvo nem edital confirmados (a página do MMA não abriu para leitura): sem fonte oficial do edital não pode ser aplicável. PENDÊNCIA PRIORITÁRIA: localizar o edital do FNMA (OSC é público típico do fundo; o Cerrado é bioma goiano — hipótese a confirmar, não dado).

### Bloco 10 — itens 109 a 120 (aplicável 0 · dispensável 8 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 109 | litoral SP/PR/SC · Edital Fundação Grupo Boticário Litoral SP PR SC 2026 | NÃO APLICA | NA-06 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 110 | nacional · Edital Marinha 2026: Guia de Permuta e Imóveis Ociosos | NÃO APLICA | NA-02 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 111 | nacional · Edital Zurich Seguros 2026: Captação via Incentivo | DISPENSÁVEL | DI-05 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 112 | Quatá/SP · Edital de Credenciamento de Organizações da Sociedade Civil -  | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 113 | nacional · Edital nº. 4/2026 - Processo de chamamento público para eleiçã | NÃO APLICA | NA-07 | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 114 | nacional · Residência Institut français × Cité internationale des arts 20 | NÃO APLICA | NA-08 | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 115 | Guaramiranga/CE · Secretaria de Cultura de Guaramiranga | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 116 | São Paulo (instituições culturais de SP) · Sonhar o Mundo 2026 abre inscrições para instituições culturai | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 117 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Circul | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 118 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - Apoio  | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 119 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 - Artist | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 120 | Vila Pavão/ES · Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - Oficin | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

- **#109** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: litoral SP/PR/SC — Edital Fundação Grupo Boticário Litoral SP PR SC 2026.
- **#110** (dados do painel (sem fonte oficial confirmada)): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): nacional — Edital Marinha 2026: Guia de Permuta e Imóveis Ociosos.
- **#111** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: nacional — Edital Zurich Seguros 2026: Captação via Incentivo.
- **#112** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Quatá/SP — Edital de Credenciamento de Organizações da Sociedade Civil - OSC Nº. 02/ 2026.
- **#113** (dados do painel (sem fonte oficial confirmada)): MDH — chamamento para eleição de organizações de conselho nacional: vaga em colegiado, não fomento.
- **#114** (dados do painel (sem fonte oficial confirmada)): Programa para artista individual no exterior: nacional — Residência Institut français × Cité internationale des arts 2027 — Paris, aberta a qualquer nacionalidade.
- **#115** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Guaramiranga/CE — Secretaria de Cultura de Guaramiranga.
- **#116** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: São Paulo (instituições culturais de SP) — Sonhar o Mundo 2026 abre inscrições para instituições culturais de São Paulo.
- **#117** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Circulação e Intercâmbio de Grupos.
- **#118** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - Apoio a Projetos Contínuos.
- **#119** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 - Artistas da Terra e Tocadores de Concertina.
- **#120** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vila Pavão/ES — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - Oficinas de Artesanato.

### Bloco 11 — itens 121 a 132 (aplicável 0 · dispensável 9 · não aplica 3)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 121 | local/regional (município não identificado) · “CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ARTISTAS LOCAIS/REG | NÃO APLICA | NA-06 +DI-01 | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 122 | Campo Alegre/AL · Diário Oficial de Campo Alegre (AL) 2026-08-13 — "edital de ch | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 123 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-08-24 — "edital de chamamen | NÃO APLICA | NA-06 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 124 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-09-16 — "edital de chamamen | DISPENSÁVEL | DI-04 +DI-01,NA-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ○ |
| 125 | Satuba/AL · Diário Oficial de Satuba (AL) 2026-09-25 — "edital de chamamen | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 126 | Viçosa/AL · Diário Oficial de Viçosa (AL) 2026-08-26 — "edital de chamamen | NÃO APLICA | NA-06 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 127 | AL · AGENCIA MUNICIPAL DE REGULACAO DE SERVICOS DELEGADOS- ARSER —  | DISPENSÁVEL | DI-01 +DI-06 | 2026-12-30 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 128 | Joaquim Gomes/AL · MUNICIPIO DE JOAQUIM GOMES — CREDENCIAMENTO SAÚDE, PARA FINS D | DISPENSÁVEL | DI-01 +DI-06 | 2027-08-20 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 129 | Igaci/AL · Diário Oficial de Igaci (AL) 2026-09-22 — "chamamento público" | DISPENSÁVEL | DI-01 +DI-06 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ |
| 130 | Igaci/AL · Diário Oficial de Igaci (AL) 2026-09-23 — "chamamento público" | DISPENSÁVEL | DI-04 +DI-01,DI-08 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ |
| 131 | CE · EDITAL OCUPA VARJOTA 2026 DE APOIO A AÇÕES CULTURAIS E FORMATI | DISPENSÁVEL | DI-01 | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ● |
| 132 | CE · Chamamento Público PMI/SMS Iguatu 2026: Guia Completo | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |

- **#121** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: local/regional (município não identificado) — “CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ARTISTAS LOCAIS/REGIONAIS”, mediante pagamento de cachê, com base… — MUNICIPIO DE ALMIRANTE TAMANDARE.
- **#122** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Campo Alegre/AL — PNAB 02/2026 ciclo 2 — errata (Campo Alegre/AL).
- **#123** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Satuba/AL — PNAB 03/2026 premiação cultural (Satuba/AL) — mesma oportunidade de c6941930.
- **#124** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Satuba/AL — PNAB 03/2026 premiação cultural — despacho (Satuba/AL).
- **#125** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Satuba/AL — PNAB 03/2026 — 2ª retificação de cronograma (Satuba/AL) — mesma oportunidade de c6941930.
- **#126** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Viçosa/AL — PNAB 003/2026 premiação de agentes culturais — alteração de cronograma (Viçosa/AL).
- **#127** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: AL — CHAMAMENTO PÚBLICO PARA A SELEÇÃO DE UMA ORGANIZAÇÃO DA SOCIEDADE CIVIL - OSC INTERESSADA EM FIRMAR TERMO DE COLABORAÇÃO COM A PREFEITURA MUNICIPAL DE MACEIÓ PARA A IMPLA.
- **#128** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Joaquim Gomes/AL — CREDENCIAMENTO SAÚDE, PARA FINS DE SELECIONAR ORGANIZAÇÕES DA SOCIEDADE CIVIL PARA EVENTUAL CELEBRAÇÃO DE TERMO DE COLABORAÇÃO OU TERMO DE FOMENTO, DE ACORDO COM A LEI FE.
- **#129** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Igaci/AL — aviso de credenciamento de OSC da área da saúde (Igaci/AL).
- **#130** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Igaci/AL — comissão do credenciamento de OSC da saúde (Igaci/AL) — mesma oportunidade de 512dd2f6.
- **#131** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: CE — SELEÇÃO DE PROJETOS DE MANUTENÇÃO DE ATIVIDADES DE FORMAÇÃO ARTÍSTICOS-CULTURIAS E NOVAS INICIATIVAS ARTÍSTICAS, PESQUISAS, ESTREIAS E LANÇAMENTOS DE PRODUTOS CULTURAIS.
- **#132** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: CE — aquisição de gêneros alimentícios diretamente da agricultura familiar e do empreendedor familiar rural ou de suas organizações.

### Bloco 12 — itens 133 a 144 (aplicável 0 · dispensável 11 · não aplica 1)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 133 | CE · EDITAL DE FOMENTO A AÇÕES CULTURAIS - POLÍTICA NACIONAL ALDIR  | DISPENSÁVEL | DI-01 | — | ● | – | ○ | ○ | – | ● | ● | ● | ● | ● | ● | ● |
| 134 | Sobral/CE · Edital Sobral 2026: Projetos Culturais e PNAB | DISPENSÁVEL | DI-08 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 135 | Sobral/CE · MUNICIPIO DE SOBRAL — [LICITANET] - SELEÇÃO DE PROJETOS PARA C | DISPENSÁVEL | DI-01 | 2026-10-02 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 136 | Iguatu/CE · MUNICIPIO DE IGUATU — Seleção de Organização da Sociedade Civi | DISPENSÁVEL | DI-01 | 2026-10-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 137 | Senador Pompeu/CE · MUNICIPIO DE SENADOR POMPEU — Constitui objeto desta chamada p | DISPENSÁVEL | DI-01 | 2026-10-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 138 | Maracanau/CE · MUNICIPIO DE MARACANAU — HAMAMENTO PÚBLICO PARA CREDENCIAMENTO | DISPENSÁVEL | DI-01 +DI-06 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 139 | Eusebio/CE · MUNICIPIO DE EUSEBIO — Chamamento Público para credenciamento  | DISPENSÁVEL | DI-01 +DI-06 | 2027-03-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 140 | Itaitinga/CE · MUNICIPIO DE ITAITINGA — CREDENCIAMENTO DE ORGANIZAÇÕES DA SOC | DISPENSÁVEL | DI-01 | 2027-07-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 141 | RS · Edital Prefeitura de Encantado 2026: Guia de Captação | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 142 | Minas do Leão/RS (FNMA) · Edital de Apoio a Projetos para a Melhoria de Resíduos Sólidos | NÃO APLICA | NA-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 143 | Osorio/RS · MUNICIPIO DE OSORIO — O presente Chamamento Público se destina | DISPENSÁVEL | DI-01 +DI-06 | 2026-10-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 144 | Parobe/RS · MUNICIPIO DE PAROBE — Formalização de parceria estabelecida pe | DISPENSÁVEL | DI-01 +DI-06 | 2026-10-13 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#133** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: CE — seleção de propostas culturais destinadas ao fomento à manutenção e programação de espaços, ambientes e iniciativas culturais de Maranguape/CE.
- **#134** (dados do painel (sem fonte oficial confirmada)): Mesma oportunidade do registro #107: Sobral/CE — Seleciona projetos culturais de Sobral nas áreas de cultura e infâncias, circulação de obras, eventos artístico-culturais, cultura popular e capoeira para receber apoio f
- **#135** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Sobral/CE — [LICITANET] - SELEÇÃO DE PROJETOS PARA CULTURA E INFÂNCIAS; OBRAS ARTÍSTICAS PARA CIRCULAÇÃO; EVENTOS ARTÍSTICO-CULTURAIS; CAPOEIRA E CULTURA POPULAR DO MUNICÍPIO DE SOBR.
- **#136** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Iguatu/CE — Seleção de Organização da Sociedade Civil – OSC para execução, em regime de colaboração com o Município, de serviços educacionais destinados ao atendimento de crianças da.
- **#137** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Senador Pompeu/CE — Constitui objeto desta chamada pública a seleção e apoio a realização de iniciativa destinada à promoção, preservação e difusão das tradições regionais do município de Se.
- **#138** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Maracanau/CE — HAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE ENTIDADES COMUNITÁRIAS, SEM FINS LUCRATIVOS/ECONÔMICOS, REGULARMENTE CONSTITUÍDAS, MANTENEDORAS DE EDUCAÇÃO, CONTEMPLANDO BERÇÁRI.
- **#139** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Eusebio/CE — Chamamento Público para credenciamento de entidades privadas, sem fins lucrativos, que realizem acolhimento exclusivamente voluntário, em regime residencial transitório, .
- **#140** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Itaitinga/CE — CREDENCIAMENTO DE ORGANIZAÇÕES DA SOCIEDADE CIVIL – OSCS PARA EXECUÇÃO DE ESCOLINHAS ESPORTIVAS E PROJETOS SOCIOESPORTIVOS VOLTADOS AO ATENDIMENTO DE CRIANÇAS E ADOLESCEN.
- **#141** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: RS — Edital Prefeitura de Encantado 2026: Guia de Captação.
- **#142** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Minas do Leão/RS (FNMA) — seleção de propostas que receberão recursos financeiros.
- **#143** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Osorio/RS — O presente Chamamento Público se destina a selecionar Organizações da Sociedade Civil (OSC) sem fins lucrativos, para firmar parceria através de Termo de Colaboração, em .
- **#144** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Parobe/RS — Formalização de parceria estabelecida pela administração pública com Organização de Sociedade Civil (OSC) para a consecução de projetos que tenham por foco atuação dentro.

### Bloco 13 — itens 145 a 156 (aplicável 0 · dispensável 11 · não aplica 1)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 145 | Vera Cruz/RS · MUNICIPIO DE VERA CRUZ — Seleção de proposta/Plano de trabalho | DISPENSÁVEL | DI-01 +DI-06 | 2026-10-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 146 | Vera Cruz/RS · MUNICIPIO DE VERA CRUZ — Formalização de parceria através de T | DISPENSÁVEL | DI-01 +DI-06 | 2026-11-12 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 147 | Santa Cruz Do Sul/RS · MUNICIPIO DE SANTA CRUZ DO SUL — Edital de Chamamento Público  | DISPENSÁVEL | DI-01 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 148 | Novo Hamburgo/RS · MUNICIPIO DE NOVO HAMBURGO — CHAMAMENTO PÚBLICO PARA CREDENCIA | DISPENSÁVEL | DI-01 +DI-06 | 2027-02-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 149 | Restinga Seca/RS · MUNICIPIO DE RESTINGA SECA — O objeto deste Termo de Referenci | DISPENSÁVEL | DI-01 | 2027-03-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 150 | Gravatai/RS · MUNICIPIO DE GRAVATAI — Credenciamento para seleção de pontos  | DISPENSÁVEL | DI-01 | 2027-06-18 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 151 | Canoas/RS · MUNICIPIO DE CANOAS — Credenciamento de Agremiações Carnavales | DISPENSÁVEL | DI-01 | 2027-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 152 | Sao Pedro Do Sul/RS · MUNICIPIO DE SAO PEDRO DO SUL — 1.1.O PRESENTE EDITAL TEM POR  | DISPENSÁVEL | DI-01 +DI-06 | 2031-03-26 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 153 | Florianópolis/SC · Diário Oficial de Florianópolis (SC) 2026-09-18 — "chamamento  | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 154 | Florianópolis/SC · Diário Oficial de Florianópolis (SC) 2026-09-23 — "chamamento  | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ● | ○ | ○ |
| 155 | SC · FUNDACAO MUNICIPAL DE CULTURA DE BOMBINHAS — EDITAL DE CREDENC | NÃO APLICA | NA-02 | 2026-12-21 | ● | ● | ○ | ◐ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 156 | Peritiba/SC · MUNICIPIO DE PERITIBA — O objeto deste Edital é a seleção de p | DISPENSÁVEL | DI-01 | 2026-12-31 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#145** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vera Cruz/RS — Seleção de proposta/Plano de trabalho para a formalização de parceria através de Termo de Colaboração, com Organizações da Sociedade Civil (OSC), para atender até 50 (cin.
- **#146** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Vera Cruz/RS — Formalização de parceria através de Termo de Colaboração, com Organizações da Sociedade Civil (OSC), para atender até 30 (trinta) crianças na faixa etária de 0 (zero) a 4.
- **#147** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Santa Cruz Do Sul/RS — Edital de Chamamento Público para seleção de propostas para Patrocínio a Eventos nº 001/2026.
- **#148** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Novo Hamburgo/RS — CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO DE OSCS APTAS A EXECUÇÃO DO SERVIÇO DE ACOLHIMENTO INSTITUCIONAL (SAI), NA MODALIDADE ABRIGO INSTITUCIONAL, PARA CRIANÇAS E ADOLESC.
- **#149** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Restinga Seca/RS — O objeto deste Termo de Referencia e o credenciamento de Organizacoes da Sociedade Civil com ou sem fins lucrativos para a prestacao do Servico de Acolhimento Institucion.
- **#150** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Gravatai/RS — Credenciamento para seleção de pontos de cultura..
- **#151** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Canoas/RS — Credenciamento de Agremiações Carnavalescas, Agremiações de Samba com personalidade jurídica, sem fins lucrativos, com razão social carnaval, sediadas em canoas, para par.
- **#152** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Sao Pedro Do Sul/RS — 1.1.O PRESENTE EDITAL TEM POR OBJETO O CREDENCIAMENTO PERMANENTE DE ORGANIZAÇÕES DA SOCIEDADE CIVIL (OSCS), SEM FINS LUCRATIVOS, QUE ATUEM NA ÁREA DA EDUCAÇÃO, PARA COMPO.
- **#153** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Florianópolis/SC — chamamento de OSC — até 35 núcleos de iniciação esportiva, Florianópolis.
- **#154** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Florianópolis/SC — chamamento de OSC — Programa Talentos Mané (esporte e lazer), Florianópolis.
- **#155** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SC — EDITAL DE CREDENCIAMENTO ELETRÔNICO DE PESSOAS JURÍDICAS PARA A PRESTAÇÃO DE SERVIÇOS DE CAPTAÇÃO DE RECURSOS ATRAVÉS DE INCENTIVOS FISCAIS VIA LEI Nº 8.313/91 - LEI DE I.
- **#156** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Peritiba/SC — O objeto deste Edital é a seleção de projetos culturais para receberem apoio financeiro nas categorias descritas no Anexo I, com o objetivo de incentivar as diversas form.

### Bloco 14 — itens 157 a 168 (aplicável 0 · dispensável 8 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 157 | Peritiba/SC · MUNICIPIO DE PERITIBA — [Portal de Compras Públicas] - O objet | DISPENSÁVEL | DI-01 | 2027-04-20 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 158 | SC · CONSORCIO INTERMUNICIPAL MULTIFINALITARIO DA REGIAO DA AMFRI - | NÃO APLICA | NA-02 | 2027-07-20 | ● | ● | ○ | ◐ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 159 | Brusque/SC · MUNICIPIO DE BRUSQUE — [Portal de Compras Públicas] - CREDENCI | NÃO APLICA | NA-06 +DI-01 | 2027-09-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 160 | Balneario Camboriu/SC · MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entidades  | DISPENSÁVEL | DI-01 +DI-06 | 2028-01-18 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 161 | Balneario Camboriu/SC · MUNICIPIO DE BALNEARIO CAMBORIU — Credenciamento de entidades  | DISPENSÁVEL | DI-01 +DI-06 | 2028-04-15 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 162 | Nova Serrana/MG · Diário Oficial de Nova Serrana (MG) 2026-09-24 — "edital de ch | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 163 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-14 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 164 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-15 — "edital de chamame | NÃO APLICA | NA-06 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 165 | Uberaba/MG · Diário Oficial de Uberaba (MG) 2026-09-22 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 166 | Pirapetinga/MG · SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE AÇÕES | DISPENSÁVEL | DI-01 | 2026-10-16 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ● | ● |
| 167 | Pirapetinga/MG · MUNICIPIO DE PIRAPETINGA — Seleção e concessão de fomento à ex | DISPENSÁVEL | DI-01 | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 168 | MG · CONSELHO DE ARQUITETURA E URBANISMO DO ESTADO DE MINAS GERAIS  | NÃO APLICA | NA-05 | 2026-10-21 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#157** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Peritiba/SC — [Portal de Compras Públicas] - O objeto deste edital é o credenciamento de associações sem fins lucrativos, sediadas no município de Peritiba, para realizar a comercializ.
- **#158** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): SC — CHAMAMENTO PÚBLICO, para CREDENCIAMENTO ELETRÔNICO de pessoas jurídicas para a prestação de serviços de captação de recursos através de incentivos fiscais via Lei n.º 8.3.
- **#159** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Brusque/SC — [Portal de Compras Públicas] - CREDENCIAMENTO DE ARTISTAS, GRUPOS ARTÍSTICOS, PROFISSIONAIS DA CULTURA, OFICINEIROS, RECREADORES, INTÉRPRETES DE LIBRAS E DEMAIS AGENTES C.
- **#160** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Balneario Camboriu/SC — Credenciamento de entidades privadas ou públicas, com ou sem fins lucrativos, para acolhimento institucional em residência inclusiva de jovens e adultos com deficiência, .
- **#161** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Balneario Camboriu/SC — Credenciamento de entidades privadas, com ou sem fins lucrativos, para acolhimento institucional na modalidade Casa de Passagem para adultos, 18 a 59 anos, de ambos os se.
- **#162** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Nova Serrana/MG — edital 07/2026 seleção de OSC — termo de fomento para evento de cultura afro-brasileira (Nova Serrana/MG).
- **#163** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Uberaba/MG — PNAB 002/2026 bolsas (Uberaba/MG) — mesma oportunidade de 35053888.
- **#164** (validação anterior (27–29/09) + dados do painel): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Uberaba/MG — PNAB 002/2026 bolsas de intercâmbio e residência (Uberaba/MG).
- **#165** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Uberaba/MG — PNAB 004/2026 projetos de música (Uberaba/MG).
- **#166** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Pirapetinga/MG — SELEÇÃO DE PROJETOS CULTURAIS PARA FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS COM RECURSOS DA POLÍTICA NACIONAL ALDIR BLANC DE FOMENTO À CULTURA-PNAB LEI N 14.3992022.
- **#167** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Pirapetinga/MG — Seleção e concessão de fomento à execução de ações culturais por meio de projetos, com recursos da Política Nacional Aldir Blanc de Fomento à Cultura (Lei Federal nº 14.3.
- **#168** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — O concurso PRÊMIO DE BOAS PRÁTICAS URBANAS: AMBIENTAL, SANEAMENTO E SOCIAL - 2026, visa a seleção e premiação de 05 (cinco) projetos, obras ou instalações arquitetônicas .

### Bloco 15 — itens 169 a 180 (aplicável 0 · dispensável 3 · não aplica 9)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 169 | MG · PONTE NOVA CAMARA MUNICIPAL — Concurso Parlamento em Ação, pro | NÃO APLICA | NA-05 | 2026-11-26 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 170 | MG · PONTE NOVA CAMARA MUNICIPAL — Concurso, referente a 5a edição  | NÃO APLICA | NA-05 | 2026-12-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 171 | Lagoa Santa/MG · MUNICIPIO DE LAGOA SANTA — CREDENCIAMENTO DE PROPOSTAS ARTÍSTI | NÃO APLICA | NA-06 +DI-01 | 2027-04-10 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 172 | Confins/MG · MUNICIPIO DE CONFINS — CHAMADA PÚBLICA PARA CREDENCIAMENTO DE  | NÃO APLICA | NA-06 +DI-01 | 2027-06-01 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 173 | MG · MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO — Reabertura do  | DISPENSÁVEL | DI-01 +DI-06 | 2027-07-30 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 174 | Juruaia/MG · MUNICIPIO DE JURUAIA — CREDENCIAMENTO ELETRÔNICO PARA RECEBIME | NÃO APLICA | NA-06 +DI-01 | 2027-08-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 175 | MG · FUNDACAO UBERLANDENSE DO TURISMO ESPORTE E LAZER — Credenciame | NÃO APLICA | NA-02 | 2030-12-11 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 176 | Passos/MG · MUNICIPIO DE PASSOS — Credenciamento de Instituições de Longa  | NÃO APLICA | NA-06 | 2031-06-25 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 177 | Vitória/ES · Diário Oficial de Vitória (ES) 2026-08-20 — "edital de chamame | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 178 | Castelo/ES · MUNICIPIO DE CASTELO — Credenciamento de cooperativas e associ | NÃO APLICA | NA-06 | 2027-07-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 179 | AC · ESTADO DO ACRE — 4º PRÊMIO DE COMUNICAÇÃO DO GOVERNO DO ESTADO | NÃO APLICA | NA-05 | 2026-10-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 180 | Silvania/GO · MUNICIPIO DE SILVANIA — REALIZAÇÃO E PUBLICAÇÃO DO EDITAL DE C | DISPENSÁVEL | DI-01 | 2026-10-09 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#169** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — Concurso Parlamento em Ação, projeto desenvolvido e gerenciado pela Escola do Legislativo da Câmara Municipal de Ponte Nova, integrante do conjunto de ações voltadas à ed.
- **#170** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: MG — Concurso, referente a 5a edição da gincana “Sua casa, nossa Câmara!", que premiará cidadãos e moradores de Ponte Nova participantes de atividades interativas promovidas p.
- **#171** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Lagoa Santa/MG — CREDENCIAMENTO DE PROPOSTAS ARTÍSTICAS, INDIVIDUAIS, E/OU COLETIVOS, E PROFISSIONAIS DE SEGUIMENTOS ARTÍSTICOCULTURAIS, PARA A RESTAÇÃO EVENTUAL DE SERVIÇO, PARA COMPOR A.
- **#172** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Confins/MG — CHAMADA PÚBLICA PARA CREDENCIAMENTO DE ARTISTAS, BANDAS, GRUPOS CULTURAIS, COLETIVOS ARTÍSTICOS, PROFISSIONAIS DO AUDIOVISUAL E DEMAIS AGENTES CULTURAIS PARA FUTURA E EVE.
- **#173** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: MG — Reabertura do Edital de Credenciamento SEE nº 02/2025 - Credenciamento de instituições públicas ou privadas, com ou sem fins lucrativos, que poderão ofertar formação prof.
- **#174** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Juruaia/MG — CREDENCIAMENTO ELETRÔNICO PARA RECEBIMENTO DE PROPOSTAS DE PESSOAS FÍSICAS E JURÍDICAS INTERESSADAS NA PRESTAÇÃO DE SERVIÇOS ARTÍSTICOS E CULTURAIS, ABRANGENDO ARTISTAS, .
- **#175** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): MG — Credenciamento de interessados (terceiro facilitador) na captação de recursos vinculados à lei estadual de incentivo ao esporte de minas gerais nº 20.824/2013, ao decreto.
- **#176** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Passos/MG — Credenciamento de Instituições de Longa Permanência para Idosos – ILPI, pessoas jurídicas de direito privado, com ou sem fins lucrativos, de Passos e/ou outra cidade da r.
- **#177** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Vitória/ES — edital FIA 001/2026 CONCAV — errata (Vitória/ES).
- **#178** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Castelo/ES — Credenciamento de cooperativas e associações que estejam legalmente habilitadas para Coleta Seletiva de resíduos recicláveis, classificados pela NBR 10004 como de origem .
- **#179** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: AC — 4º PRÊMIO DE COMUNICAÇÃO DO GOVERNO DO ESTADO DO ACRE “MOISÉS ALENCASTRO".
- **#180** (PNCP consultado ao vivo em 02/10/2026): Silvânia/GO — PNAB Ciclo 2 (agentes culturais do município); prazo 09/10/2026 no PNCP; de outro município goiano.

### Bloco 16 — itens 181 a 192 (aplicável 2 · dispensável 6 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 181 | GO · Chamamento público publicado no Diário Oficial em 25/09/2026 — | DISPENSÁVEL | DI-08 | — | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 182 | GO · Chamamento público publicado no Diário Oficial em 25/09/2026 — | NÃO APLICA | NA-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ○ | ● | ○ | ○ |
| 183 | Catalão/GO (título cita Pinhais) · Chamamento público publicado no Diário Oficial em 28/08/2026 — | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ● | ● | ● |
| 184 | Goiânia/GO · Diário Oficial de Goiânia (GO) 2026-09-25 — "edital de chamame | APLICÁVEL | AP-01 | 2026-10-26 | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 185 | GO · Editais - FAPEG — Goiás — Goiás — Goiás | NÃO APLICA | NA-06 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 186 | GO · Editais de Chamamento — Goiás / Goiânia | NÃO APLICA | NA-04 | — | ● | – | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● |
| 187 | GO · Editais de Destinação de Recursos ou Bens | APLICÁVEL | AP-03 | recorrente (cada edital ≈ 5 dias;  | ● | ● | – | – | ● | ● | ● | ● | ● | ● | ● | ● |
| 188 | GO · Edital Arranjos Regionais FSA | NÃO APLICA | NA-06 | — | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 189 | Goiatuba/GO · Edital Cultura Goiatuba 2026: PNAB Ciclo 2 — Goiás / Goiatuba | DISPENSÁVEL | DI-01 +DI-05 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 190 | Planaltina/GO · Edital Prefeitura Municipal de Planaltina 2026 | DISPENSÁVEL | DI-01 +DI-06 | — | ● | – | – | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 191 | GO · Edital chamamento público nº 001/2026 (oss) — Goiás / Goiânia | DISPENSÁVEL | DI-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 192 | GO · Edital de Chamamento Público de Instituições sem Fins Lucrativ | DISPENSÁVEL | DI-03 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |

- **#181** (dados do painel (sem fonte oficial confirmada)): Registro duplicado do #184 (Natal no Parque): a URL deste registro é o Diário Oficial de Goiânia de 25/09/2026 (o mesmo do #184). Os dados do painel (valor R$ 4.638.055,74) vieram de outro documento, o link oficial de 07/08, que é o crédito suplementar do #182.
- **#182** (dados do painel (sem fonte oficial confirmada)): Diário de Goiânia de 07/08/2026 — abertura de crédito suplementar de R$ 4.638.055,74 para a Secretaria de Administração/Guarda Civil: ato orçamentário, não chamamento (título cita 25/09, mas o documento lido é de 07/08).
- **#183** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Catalão/GO (título cita Pinhais) — O presente edital possui valor total de R$591.740,18 (quinhentos e noventa e um mil setecentos e quarenta reais e dezoito centavos)..
- **#184** (edital lido ao vivo (Diário Oficial de Goiânia 25/09)): Goiânia/SEGENP — Chamamento Público nº 001/2026 "Natal no Parque – A Magia de Brincar" (Lei 13.019): termo de colaboração com OSC, valor máximo R$ 5.000.000,00; protocolo único até 26/10/2026, resultado definitivo em 06/11/2026. Exige ≥ 1 ano de CNPJ ativo (a entidade tem 39 anos de CNPJ) e experiência prévia em objeto semelhante (eventos culturais). Edital lido no Diário Oficial de 25/09/2026 (págs. 6–17). Pendência
- **#185** (dados do painel (sem fonte oficial confirmada)): FAPEG — página de chamadas de pesquisa/inovação (ICT, pesquisadores, bolsistas): associação não é proponente típico.
- **#186** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: GO — credenciamento de profissionais ESPECIALISTAS, TÉCNICOS E AUXILIARES EM SAÚDE.
- **#187** (validação anterior (27–29/09) + dados do painel): MPT/PRT-18 (Goiás) — página permanente de editais de destinação de recursos de TAC (fonte recorrente, validada em 29/09). O edital em curso (9282.2026, R$ 150.000,00, publicado em 25/09, prazo de 5 dias) já está vencido ou vence hoje; o edital anterior (8927.2026) também encerrou. Valor da fonte: monitorar a página e manter projeto social pronto para indicação a cada novo edital.
- **#188** (dados do painel (sem fonte oficial confirmada)): FSA Arranjos Regionais (Goiás) — exige produtora brasileira independente com fins lucrativos registrada na ANCINE; associação não é público.
- **#189** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Goiatuba/GO — Edital Cultura Goiatuba 2026: PNAB Ciclo 2 — Goiás / Goiatuba.
- **#190** (validação anterior (27–29/09) + dados do painel): Planaltina/GO — Chamamento nº 06/2026 (Esporte e Lazer, R$ 30 mil, campeonatos): é de outro município goiano, exige OSC local; data-limite não consta do edital.
- **#191** (dados do painel (sem fonte oficial confirmada)): SMS Goiânia — edital de chamamento nº 001/2026 (organização social de saúde): exige qualificação como OS e gestão de serviços de saúde, incompatível com o perfil.
- **#192** (página oficial lida ao vivo): SEDS/GO — chamamento "Aprendiz do Futuro" já em fase de recursos administrativos e julgamento: inscrições encerradas.

### Bloco 17 — itens 193 a 204 (aplicável 1 · dispensável 3 · não aplica 8)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 193 | GO · Edital de chamamento público - 001/2026 - Socioeducativo — Goi | DISPENSÁVEL | DI-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 194 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Edi | NÃO APLICA | NA-04 | — | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ○ | ○ | ○ | ○ |
| 195 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Fap | NÃO APLICA | NA-06 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 196 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Gov | NÃO APLICA | NA-06 | — | ● | ○ | ● | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● |
| 197 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Lan | NÃO APLICA | NA-06 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 198 | GO · Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Pro | NÃO APLICA | NA-06 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ○ |
| 199 | GO · Goiás Social aumenta repasse do Auxílio Nutricional às entidad | APLICÁVEL | AP-03 | fluxo contínuo (até 08/2027) | ● | ● | ● | ● | – | ● | ● | ● | ● | ● | ● | ● |
| 200 | GO · Goiás Social — Conselho Estadual dos Direitos da Criança e do  | NÃO APLICA | NA-07 | — | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● | ○ | ● | ● |
| 201 | GO · Prefeitura de Cachoeira Alta — Edital nº 001/2026 | NÃO APLICA | NA-03 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 202 | Goiatuba/GO · Prefeitura de Goiatuba — Edital nº 004/2026 | DISPENSÁVEL | DI-05 +DI-01 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 203 | Nova Iguaçu de Goiás/GO · Prefeitura de Nova Iguaçu de Goiás — Edital nº 001/2026 — Goiá | DISPENSÁVEL | DI-01 +DI-05 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 204 | GO · Prorrogado prazo para submissão de propostas ao edital de Cons | NÃO APLICA | NA-06 | — | ● | ○ | ● | ○ | ○ | ● | ○ | ● | ○ | ● | ○ | ● |

- **#193** (página oficial lida ao vivo): SEDS/GO — Chamamento nº 001/2026 Socioeducativo: termo de colaboração para ações complementares ao atendimento socioeducativo (página atualizada em 24/09/2026; o texto do edital está em anexo que não consegui ler e o prazo não consta da página). Presume-se exigência de experiência técnica especializada, que o perfil da associação não comprova: PRESUNÇÃO a confirmar com a leitura do edital.
- **#194** (dados do painel (sem fonte oficial confirmada)): Não há edital identificável: GO — Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Edital da Fapeg fomenta novas pesquisas sobre os be… — Goiás.
- **#195** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — Fundação de Amparo à Pesquisa do Estado de Goiás (FAPEG) — Fapeg lança chamada para apoio financeiro a periódi… — Goiás.
- **#196** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — apoio à pesquisa e inovação em educação especial inclusiva.
- **#197** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — apoiar financeiramente propostas que, para além de diagnósticos, promovam implementação de soluções práticas, sustentáveis e inovadoras, com participação direta das mulhe.
- **#198** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — seleção de bolsistas para projetos de desenvolvimento tecnológico e industrial.
- **#199** (validação anterior (27–29/09) + dados do painel): SEDS/GO — Credenciamento nº 001/2026 em fluxo contínuo (12 meses a partir de 27/08/2026) para OSC atuantes em Goiás (Auxílio Nutricional e/ou Água e Energia); sem data-limite. Conferir no edital se o público atendido (entidades que acolhem/atendem pessoas em vulnerabilidade) abrange a atividade da associação.
- **#200** (dados do painel (sem fonte oficial confirmada)): CEDCA/GO — convocação de representantes da sociedade civil para o conselho: é vaga de conselheiro (influência), não repasse de recursos. Vale acompanhar como oportunidade de articulação, fora do funil de captação.
- **#201** (dados do painel (sem fonte oficial confirmada)): É seleção de pessoas (estágio/aprendizagem/processo seletivo), não de entidade: GO — formação de cadastro reserva para estágio.
- **#202** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Goiatuba/GO — Prefeitura de Goiatuba — Edital nº 004/2026.
- **#203** (dados do painel (sem fonte oficial confirmada)): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Nova Iguaçu de Goiás/GO — Promover os Jogos Educacionais no contexto virtual e/ou presencial, a fim de possibilitar o acesso às práticas corporais, de forma a contribuir com o processo de aprendiz.
- **#204** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: GO — Conservação da Biodiversidade Legado Verdes do Cerrado.

### Bloco 18 — itens 205 a 216 (aplicável 0 · dispensável 8 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 205 | GO · SECTI-GO (ciência e tecnologia) — Edital nº 002/2026 | DISPENSÁVEL | DI-05 +DI-06 | — | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 206 | PA · UNIVERSIDADE FEDERAL RURAL DA AMAZONIA — PROCEDIMENTO DE HABIL | NÃO APLICA | NA-06 +DI-03 | 2026-10-13 (revogado) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 207 | Mossoró/RN · Diário Oficial de Mossoró (RN) 2026-09-15 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |
| 208 | Mossoró/RN · Diário Oficial de Mossoró (RN) 2026-09-16 — "chamamento públic | DISPENSÁVEL | DI-05 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 209 | Alexandria/RN · MUNICIPIO DE ALEXANDRIA — SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE  | DISPENSÁVEL | DI-01 | 2026-10-23 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 210 | Santa Cruz/RN · MUNICIPIO DE SANTA CRUZ — Credenciamento de artistas individua | NÃO APLICA | NA-06 +DI-01 | 2027-06-03 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 211 | Jandaira/RN · MUNICIPIO DE JANDAIRA — CREDENCIAMENTO DE ARTISTAS, GRUPOS, CO | NÃO APLICA | NA-06 +DI-01 | 2027-08-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 212 | Portalegre/RN · MUNICIPIO DE PORTALEGRE — Contratação de artistas, grupos artí | NÃO APLICA | NA-06 +DI-01 | 2027-10-01 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 213 | Rio Grande do Norte · Seleção de Organização da Sociedade Civil – OSC, em regime de  | DISPENSÁVEL | DI-01 | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 214 | São José do Vale do Rio Preto/RJ · Diário Oficial de São José do Vale do Rio Preto (RJ) 2026-09-2 | DISPENSÁVEL | DI-01 | 2027-05-07 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ |
| 215 | Macaé/RJ · Diário Oficial de Macaé (RJ) 2026-09-22 — "chamamento público" | DISPENSÁVEL | DI-05 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |
| 216 | Niterói/RJ · Diário Oficial de Niterói (RJ) 2026-09-16 — "edital de chamame | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ |

- **#205** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: GO — SECTI-GO (ciência e tecnologia) — Edital nº 002/2026.
- **#206** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PA — PROCEDIMENTO DE HABILITAÇÃO DAS ASSOCIAÇÕES E/OU COOPERATIVASDECATADORES DE MATERIAIS RECICLÁVEIS E REUTILIZÁVEIS, no intuito de firmar TERMODECOMPROMISSO para fins de co.
- **#207** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Mossoró/RN — edital de repasse a projetos artísticos (Mossoró/RN).
- **#208** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Mossoró/RN — O presente Termo Aditivo 001 ao contrato que fazem entre si a Câmara Municipal Mossoró/RN, GRID COMUNICAÇÃO VISUAL, SINALIZAÇÃO E EVENTOS LTDA com o objeto de prestação d.
- **#209** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Alexandria/RN — SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL - OSC PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO DESTINADO À EXECUÇÃO DE AÇÕES DE ACOLHIMENTO E HOSPEDAGEM TEMPORÁRIA DE CÃES E GAT.
- **#210** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Santa Cruz/RN — Credenciamento de artistas individuais, grupos ou coletivos para a pintura de painéis, tipificados como “intervenções artísticas”, utilizando a técnica do graffiti, mural.
- **#211** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Jandaira/RN — CREDENCIAMENTO DE ARTISTAS, GRUPOS, COLETIVOS E AGENTES CULTURAIS, NOS TERMOS DA LEI FEDERAL Nº 14.399/2022 (POLÍTICA NACIONAL ALDIR BLANC – PNAB), PARA PRESTAÇÃO DE SERV.
- **#212** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Portalegre/RN — Contratação de artistas, grupos artísticos e agentes culturais para os eventos e demais programações do município de Portalegre/RN, abrangendo apresentações musicais, lit.
- **#213** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Rio Grande do Norte — Seleção de Organização da Sociedade Civil – OSC, em regime de mútua cooperação, para celebração de parceria com a administração pública municipal, objetivando a consecuçã.
- **#214** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: São José do Vale do Rio Preto/RJ — edital 05/2026 seleção de OSC — assistência social (São José do Vale do Rio Preto/RJ).
- **#215** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Macaé/RJ — fomento a parcerias com governo federal e estadual.
- **#216** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Niterói/RJ — extrato do edital SMC 02/2026 Cultura Geek (Niterói/RJ).

### Bloco 19 — itens 217 a 228 (aplicável 0 · dispensável 6 · não aplica 6)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 217 | São José do Vale do Rio Preto/RJ · Diário Oficial de São José do Vale do Rio Preto (RJ) 2026-09-2 | DISPENSÁVEL | DI-08 +DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ● | ● |
| 218 | Arraial Do Cabo/RJ · MUNICIPIO DE ARRAIAL DO CABO — O presente Chamamento Público t | DISPENSÁVEL | DI-01 | 2026-10-08 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 219 | RJ · SECRETARIA MUNICIPAL DE EDUCACAO — Credenciamento de Organizaç | DISPENSÁVEL | DI-01 +DI-06 | 2027-05-27 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 220 | Angra Dos Reis/RJ · MUNICIPIO DE ANGRA DOS REIS — Credenciamento de Cooperativas e | NÃO APLICA | NA-06 | 2027-06-17 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 221 | Itacoatiara/AM · MUNICIPIO DE ITACOATIARA — [LICITANET] - Seleção de Projetos C | DISPENSÁVEL | DI-01 | 2026-10-16 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 222 | AM · TRIBUNAL REGIONAL ELEITORAL DO AMAZONAS — O presente procedime | NÃO APLICA | NA-06 | 2028-01-31 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 223 | Muribeca/SE · Diário Oficial de Muribeca (SE) 2026-08-04 — "edital de chamam | DISPENSÁVEL | DI-04 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |
| 224 | Simão Dias/SE · Diário Oficial de Simão Dias (SE) 2026-08-17 — "edital de cham | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● | ○ | ● | ● |
| 225 | SE · ARACAJU CAMARA MUNICIPAL — ESTE EDITAL DISPÕE SOBRE AS NORMAS, | NÃO APLICA | NA-05 | 2026-10-13 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 226 | Nova Palmeira/PB · MUNICIPIO DE NOVA PALMEIRA — Credenciamento de facilitadores,  | NÃO APLICA | NA-06 +DI-01 | 2027-01-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 227 | Nova Palmeira/PB · MUNICIPIO DE NOVA PALMEIRA — credenciamento de articuladores,  | NÃO APLICA | NA-06 +DI-01 | 2027-01-19 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 228 | Boa Hora/PI · MUNICIPIO DE BOA HORA — CONTRATAÇÃO DE PRESTADOR DE SERVIÇOS P | NÃO APLICA | NA-02 | 2027-07-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |

- **#217** (validação anterior (27–29/09) + dados do painel): Mesma oportunidade do registro #214: São José do Vale do Rio Preto/RJ — edital 05/2026 seleção de OSC — republicado (São José do Vale do Rio Preto/RJ) — mesma oportunidade de 332e8f67
- **#218** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Arraial Do Cabo/RJ — O presente Chamamento Público tem por objeto a seleção de Organização da Sociedade Civil (OSC) para celebração de Termo de Colaboração com o Município de Arraial do Cabo,.
- **#219** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: RJ — Credenciamento de Organizações da Sociedade Civil (OSC), com vistas a possíveis e futuras parcerias na área educacional, com fundamento na Lei Federal nº 13.019/2014, alt.
- **#220** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Angra Dos Reis/RJ — Credenciamento de Cooperativas e Associações interessadas em receber Remuneração Complementar pela prestação de serviços de coleta e reciclagem de óleo vegetal comestível.
- **#221** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Itacoatiara/AM — [LICITANET] - Seleção de Projetos Culturais para Concessão de Apoio Financeiro e Celebração de Termo de Execução Cultural, com a Finalidade de Fomentar, Fortalecer e Valo.
- **#222** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: AM — O presente procedimento tem por objeto selecionar as associações e/ou cooperativas de catadores de materiais recicláveis e reutilizáveis, que estejam cadastradas no SINIR.
- **#223** (validação anterior (27–29/09) + dados do painel): Ato acessório de edital de outro registro/território: Muribeca/SE — comunicado do edital PNAB 001/2026 ciclo 2 (Muribeca/SE).
- **#224** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Simão Dias/SE — editais culturais 003 e 004/2026 SEMCULT (Simão Dias/SE).
- **#225** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: SE — ESTE EDITAL DISPÕE SOBRE AS NORMAS, PROCEDIMENTOS E PRAZOS PARA PARTICIPAÇÃO NA 9ª EDIÇÃO DO PRÊMIO DE POESIA GOVERNADOR MARCELO DÉDA, ORGANIZADO PELO SETOR DE PROMOÇÃO S.
- **#226** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Nova Palmeira/PB — Credenciamento de facilitadores, profissionais e assessoria técnica para atuar no projeto "DE TODOS PARA TODOS" centro de inclusão social, através de termo de adesão entr.
- **#227** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: Nova Palmeira/PB — credenciamento de articuladores, profissionais e assessoria técnica para atuar no projeto “TENDA ITINERANTE - ESPAÇO DAS HISTÓRIAS VIVAS, através de termo de adesão entre.
- **#228** (PNCP consultado ao vivo em 02/10/2026): É contratação/licitação de fornecedor ou prestador (não parceria de fomento com OSC): Boa Hora/PI — CONTRATAÇÃO DE PRESTADOR DE SERVIÇOS PARA EXECUÇÃO DE CAPACITAÇÃO, QUALIFICAÇÃO E FORMAÇÃO DE AGENTES CULTURAIS (AUDIOVISUAL, TEATRO), NOS TERMOS DA LEI Nº 14.399, DE 8 D.

### Bloco 20 — itens 229 a 238 (aplicável 0 · dispensável 6 · não aplica 4)

| # | Local · registro | Veredito | Regra | Prazo | Obj | Pzo | Res | Rec | Val | Órg | Ter | Esf | Req | Anx | Dst | Áre |
|--:|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 229 | Palmas/TO · MUNICIPIO DE PALMAS — Selecao de Organizacao da Sociedade Civi | DISPENSÁVEL | DI-01 +DI-06 | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 230 | TO · TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciamento de | NÃO APLICA | NA-06 +DI-03,DI-01 | 2030-04-01 (suspenso) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 231 | PE · FUNDACAO MUNICIPAL DE SAUDE DE TAQUARITINGA DO NORTE — CREDENC | DISPENSÁVEL | DI-01 +DI-06 | 2027-05-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 232 | PE · FUNDO MUNICIPAL DE SAUDE DE TAQUARITINGA DO NORTE — CREDENCIAM | DISPENSÁVEL | DI-01 +DI-06 | 2027-05-11 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 233 | PE · UNIVERSIDADE FEDERAL DE PERNAMBUCO — Selecionar e habilitar as | NÃO APLICA | NA-06 | 2028-02-08 | ● | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ○ | ○ | ○ |
| 234 | Costa Rica/MS · Diário Oficial de Costa Rica (MS) 2026-08-11 — "edital de cham | DISPENSÁVEL | DI-05 +DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ● | ● | ● | ○ |
| 235 | AP · DEFENSORIA PUBLICA DO ESTADO — Concurso de artigos para public | NÃO APLICA | NA-05 | 2026-10-22 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 236 | Nova Mutum/MT · MUNICIPIO DE NOVA MUTUM — CHAMAMENTO PÚBLICO PARA SELEÇÃO DE P | DISPENSÁVEL | DI-01 | 2026-10-05 | ● | ● | ○ | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ○ |
| 237 | MT · TRIBUNAL SUPERIOR DO TRABALHO — CHAMAMENTO PÚBLICO DE INSTITUI | NÃO APLICA | NA-06 | 2030-02-13 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 238 | Boa Vista/RR · Diário Oficial de Boa Vista (RR) 2026-08-05 — "edital de chama | DISPENSÁVEL | DI-01 | — | ● | ○ | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ○ |

- **#229** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Palmas/TO — Selecao de Organizacao da Sociedade Civil - OSC para celebracao de Termo de Colaboracao destinado a gestao, a operacionalizacao e a execucao das acoes e servicos de saude.
- **#230** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: TO — Credenciamento de associação e/ou cooperativa de catadores de materiais recicláveis por meio do Projeto Coleta Seletiva Solidária para prestarem serviços gratuitos de col.
- **#231** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: PE — CREDENCIAMENTO DE PESSOA(S) JURÍDICA(S) DE DIREITO PRIVADO, PREFERENCIALMENTE AS ENTIDADES FILANTRÓPICAS E AS SEM FINS LUCRATIVOS (previsão do Art. 199, § 1º, da CF), INT.
- **#232** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: PE — CREDENCIAMENTO DE PESSOA(S) JURÍDICA(S) DE DIREITO PRIVADO, PREFERENCIALMENTE AS ENTIDADES FILANTRÓPICAS E AS SEM FINS LUCRATIVOS (previsão do Art. 199, § 1º, da CF), INT.
- **#233** (PNCP consultado ao vivo em 02/10/2026): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: PE — Selecionar e habilitar as associações e/ou cooperativas de catadores de materiais recicláveis aptas a firmar Termo de Compromisso, visando à coleta de resíduos sólidos re.
- **#234** (dados do painel (sem fonte oficial confirmada)): Sem fonte oficial que comprove objeto e prazo; reavaliar se a fonte for localizada: Costa Rica/MS — Seleção de profissionais para o cargo efetivo de Guarda Civil no Município de Costa Rica/MS.
- **#235** (PNCP consultado ao vivo em 02/10/2026): Concurso/prêmio de ideias, artigos ou boas práticas, sem repasse de fomento a OSC: AP — Concurso de artigos para publicação na 2ª edição da Revista da Defensoria Pública do Amapá..
- **#236** (PNCP consultado ao vivo em 02/10/2026): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Nova Mutum/MT — CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS CULTURAIS, VISANDO À CELEBRAÇÃO DE TERMO DE EXECUÇÃO CULTURAL COM AGENTES CULTURAIS DO MUNICÍPIO DE NOVA MUTUM-MT – CICLO 2, P.
- **#237** (dados do painel (sem fonte oficial confirmada)): Público-alvo exclusivo que não inclui associação de moradores/comerciantes: MT — CHAMAMENTO PÚBLICO DE INSTITUIÇÕES DE ENSINO SUPERIOR (IES) INTERESSADAS EM CELEBRAR ACORDO DE COOPERAÇÃO TÉCNICA E ACORDO DE COOPERAÇÃO PARA DESENVOLVIMENTO DE SERVIÇOS .
- **#238** (validação anterior (27–29/09) + dados do painel): Oportunidade real, mas de outro município/estado; chamamentos locais exigem sede/atuação no território: Boa Vista/RR — resultado final com REABERTURA DE PRAZO de chamamento de OSC — saúde (Boa Vista/RR); prazo não confirmado.

## 9. Defeitos de coleta encontrados (viram regras RC dos livros)

1. **RC-01 — falso "nacional":** 39 registros ficaram no balde `__nac__` com "sem restrição geográfica declarada — vale para todo o Brasil", mas só 3 são de fato nacionais (iCS, Dia de Doar, FNMA); os demais têm município no título (Vila Pavão/ES, Tauá/CE, Balsas/MA, Sobral/CE etc.).
2. **RC-02 — objeto do diário:** em "menção em diário oficial" o objeto vem de trecho vizinho (Valinhos: crédito adicional; Iracemápolis: Plano Municipal de Educação; Andradina: concurso; Arapongas: vencimentos; Pinhais: servidores). Só vale após ler o ato que cita o chamamento.
3. **RC-03 — link oficial errado:** Itapeva/SP → itapeva.mg.gov.br; Pinhais/PR → catalao.go.gov.br; Valparaíso/SP → campoflorido.mg.gov.br; Canudos/BA → joaopinheiro.mg.gov.br; PNAB → edital de concurso público; Nova Iguaçu de Goiás → processo seletivo de diretores de Goiânia; Satuba/AL e Simão Dias/SE → o mesmo post de notícia.
4. **RC-04 — vigência não é prazo:** credenciamentos com encerramento em 2030/2031 (Artur Nogueira, Telêmaco Borba, São Pedro do Sul) são vigência do cadastro, não janela de inscrição.
5. **RC-05 — link fictício:** #101 aponta para `x.gov.br/edital` (placeholder); vai para quarentena.
6. **RC-06 — duplicatas:** PNCP + diário + Interceptador repetem a mesma oportunidade (#102=#18 Itatinga, #43=#46 Olindina, #55=#66 Guaíra, #78=#224 Simão Dias, #88=#5 Itapeva, #89=#6 Macatuba, #134=#107 Sobral, #181=#184 Natal no Parque, #217=#214 São José do Vale do Rio Preto).
7. **Situação não lida:** edital revogado (#44 CPRM, #206 UFRA) e suspenso (#230 TJTO) continuavam como "abertos"; encerrados (#17 Indaiatuba; #32 Olindina/BA com encerramento em 29/09) também.

## 10. Decisões do titular e próximos passos

1. **Natal no Parque:** concorrer? sozinha, em rede ou não concorrer? (prazo 26/10).
2. **Território:** manter a regra "sede/atuação local" para chamamentos de outros municípios (inclusive goianos), ou abrir exceção para parcerias com entidades locais?
3. **Fluxos contínuos (#199 SEDS, #86 iCS) e recorrência (#187 MPT):** autorizar a preparação de consulta/projeto-base para uso imediato?
4. **Pendências com dono:** localizar o edital do FNMA/incêndios (#108), acompanhar a abertura da próxima edição do Dia de Doar (#87) e confirmar com a SEGENP a publicação oficial do edital (#184).
5. Aplicar o **arquivo de atualização dos livros** (config/regras_restricao_livros.json + src/regras_restricao.py) no próximo ciclo e rodar a rotina de revalidação semanal.

## 11. Verificação

- Teste das regras contra esta validação: **92.0%** de concordância de classe nos 238, e todos os aplicáveis são reproduzidos. **Ressalva:** as regras foram calibradas sobre o mesmo conjunto — é ajuste, não validação independente; a prova de generalização virá do próximo ciclo de coleta. As 19 divergências são casos de leitura humana do ato/da página (objeto mal extraído, link de outro município, território indeterminado). Duplicatas só são detectadas por chave PNCP; as demais exigem leitura.
- Suíte de testes das regras: `tests/test_regras_restricao.py` (16 testes), incluindo os falsos positivos apontados pela revisão independente (atividades socioeducativas, processo seletivo de propostas de OSC, mestres de capoeira, resultado final no cronograma).
- **Revisão independente** (subagente sem contexto prévio): auditou 40+ itens, as contagens e as regras. Resultado: contagens e prazos conferem; apontou 8 correções e 6 riscos de regras, **todos aplicados**: #87 passou a DISPENSÁVEL (edição 2024 encerrada), #108 a DISPENSÁVEL (sem edital/prazo), #187 explicitado como fonte recorrente, #181 reclassificado como duplicata do #184, #43/#166 corrigidos, #101 em DI-05, correção de números e anos, e regras com exceções para OSC, divisão em padrões fortes/fracos, flag de revisão humana, pendências, quarentena de injeção e releitura do JSON.