# Parecer do conselho — motores de busca, oportunidades novas e motores opressores · 27/09/2026

## 1. Os motores de busca estão achando oportunidades novas?

Sim, com volume desigual. Contagem de oportunidades **diferentes** (sem repetição) por motor, publicada hoje em
`docs/dados/achados_motores.json`: PNCP 211 (de 244 registros), ABCR 27 (de 33), Piloto 24 (de 85), Observatório do
3º Setor 17, Diário de Goiás 10, Secult-GO 9, Recorrência 8, DOU 6. A repetição que aparecia nos quadros (motores 02,
12, 13, 15, 16, 17) era a mesma oportunidade chegando por duas listas e em registros levemente diferentes — agora
conta uma vez, e cada quadro mostra as 5 mais recentes com a data de publicação original.

## 2. As oportunidades novas estão criando motores opressores?

**Sim, mas o ciclo não fecha.**

| etapa | situação medida |
|---|---|
| oportunidade nova vira opressor | **92 opressores `nova-*`** criados desde 07/09; último lote em 22/09 |
| opressor é ligado por 30 dias | **76** ligados |
| opressor lê a própria página (a "fonte monitorada") | **0** — todos "não lida ainda", sem última leitura, sem achados |
| fase de IA a cada 3 dias | **873 tentativas, 0 itens**: 815 "a IA não roda no GitHub", 58 "aguardando credencial FAROL_AI_API_KEY" |
| duplicados | "Convênios e parcerias" criado 4 vezes; "Lei Rouanet" 2 |
| época, ciclo ou regime de prazo registrados | **0** — por isso nenhuma previsão é possível hoje |
| fontes monitoradas dos motores regulares | `config/fontes.json`: 85 (2 novas em quarentena, vindas dos Pilotos) — o catálogo de opressores (366) é outra lista e não alimenta o monitoramento diário |

**Correção feita hoje:** o Piloto - Interceptador passa a ter uma 5ª fila — *opressor que nunca leu a própria página*
(40 únicos, sem os duplicados). Ele lê a página com o modelo local (sem chave externa), comprova as condições e
devolve ao catálogo do opressor: validação, última leitura, camadas, e prazo/regime quando comprovado. É isso que
torna a previsão possível.

## 3. Os opressores novos — parâmetros e análise preditiva

Distribuição: famílias {'Outros programas': 73, 'Fundações e institutos privados': 9, 'PNAB / Aldir Blanc': 3, 'BNDES': 2, 'Destinação judicial': 2, 'Lei Rouanet': 2}; esfera/UF {'Brasil/BR': 54, 'Estado/BR': 28, 'Estado/GO': 10}.

Leitura da coluna "previsão": com os dados que existem hoje (título, órgão, família e menções), só é possível dizer
se a oportunidade é **pontual** (um edital com número/ano: vale o prazo dele, e uma nova edição é provável em ~12
meses se o órgão repetir) ou **recorrente** (fundo, programa, convênio, lei: publica em ciclos, cujo calendário ainda
não está registrado). A data da próxima janela só aparece depois da leitura pelo Interceptador.

| opressor | programa | órgão | família | esfera/UF | menções | ligado desde | tem página | previsão |
|---|---|---|---|---|---|---|---|---|
| nova-5639af059d87 | Fundação Maria Emília abre edital de até R$ 1 milhão para pr | Observatório do Terceiro Setor — editais | Fundações e institutos privados | Brasil/BR | 3 | 2026-09-12 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-09243dc7dff2 | Instituto Clima e Sociedade abre edital de até R$ 500 mil pa | Observatório do Terceiro Setor — editais | Fundações e institutos privados | Estado/BR | 3 | 2026-09-07 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-becc193fd64c | Aviso de Chamamento Público 02/2026 | Diário Oficial do Estado de Goiás | Outros programas | Estado/GO | 3 | 2026-09-21 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-2b6b7baee206 | Convênios e parcerias | Programa estadual de eventos esportivos | Outros programas | Estado/GO | 3 | 2026-09-22 | sim | recorrente: publica em ciclos; próxima janela depende do calendário do órgão (não registrado) |
| nova-b9a705760266 | Apoio a projetos incentivados | SALIC — Lei Rouanet (Ministério da Cultu | Outros programas | Brasil/BR | 3 | 2026-09-10 | sim | indefinido: sem histórico nem ciclo |
| nova-137bf6a88373 | Aviso de Chamamento Público | SMS Goiânia - parceria com entidade de s | Outros programas | Brasil/BR | 3 | 2026-09-08 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-dbf022617003 | Chamamentos Públicos | Secult Goiás — Goyazes e Aldir Blanc | Outros programas | Brasil/BR | 3 | 2026-09-09 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-09e7716ec5d5 | EDITAL DE Nº 126/IFAL, DE 18 DE SETEMBRO DE 2026 | Diário Oficial da União | Outros programas | Brasil/BR | 3 | 2026-09-21 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-47d6fafae93e | EXTRATO DE TERMO DE FOMENTO | Diário Oficial da União | Outros programas | Brasil/BR | 3 | 2026-09-18 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-44786ad1bb03 | Edital Natal do Bem | Secult Goiás — Goyazes e Aldir Blanc | Outros programas | Brasil/BR | 3 | 2026-09-15 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-2e3527f96184 | Parque Bondinho Pão de Açúcar abre edital para projetos cult | Observatório do Terceiro Setor — editais | Outros programas | Brasil/BR | 3 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-798c91115fc0 | Premiações | Editais de empresas incentivadoras (mode | Outros programas | Brasil/BR | 3 | 2026-09-22 | sim | indefinido: sem histórico nem ciclo |
| nova-86a89ba66dfd | Termos de Fomento | Secult Goiás — Goyazes e Aldir Blanc | Outros programas | Brasil/BR | 3 | 2026-09-07 | sim | indefinido: sem histórico nem ciclo |
| nova-bf43805abcd9 | APOIO FINANCEIRO O  edital  destinou apoio financeiro a prop | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 3 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-2b357be3c852 | Bússola Investimento Social | Bússola Social - Bússola Editais | Outros programas | Estado/BR | 3 | 2026-09-07 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-4702c95f604e | EDITAL  001/ 2026  - FUNDO SEMENTE PARA RESILIÊNCIA - PARCEI | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 3 | 2026-09-22 | sim | recorrente: publica em ciclos; próxima janela depende do calendário do órgão (não registrado) |
| nova-b90aeeaa24be | O UNAIDS publica, nesta quinta-feira (23), o  Edital  para s | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 3 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-962fbc0ba13a | ONGs e coletivos periféricos do Nordeste podem se inscrever  | ABCR — Associação Brasileira de Captador | Outros programas | Estado/BR | 3 | 2026-09-07 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-5295a689e8f3 | parceirosvoluntarios.org.br/wp-content/uploads/2026/01/Edita | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 3 | 2026-09-22 | sim | recorrente: publica em ciclos; próxima janela depende do calendário do órgão (não registrado) |
| nova-2109bafc97e3 | Entidades Assistenciais | Ministérios Públicos — editais de destin | Assistência social (FMAS/FEAS) | Estado/BR | 2 | 2026-09-21 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-34330f93d960 | Instituto Impactarte abre edital para projetos de impacto so | Observatório do Terceiro Setor — editais | Fundações e institutos privados | Estado/BR | 2 | 2026-09-07 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-add1f4c8737f | Lei Rouanet | Lei Rouanet - doação de pessoa física | Lei Rouanet | Brasil/BR | 2 | 2026-09-07 | sim | recorrente: publica em ciclos; próxima janela depende do calendário do órgão (não registrado) |
| nova-036e39c1f345 | Aviso de Chamamento Público – Complexo Serra Dourada | Programa estadual de eventos esportivos | Outros programas | Brasil/BR | 2 | 2026-09-10 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-a3ee60594556 | Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão em p | Observatório do Terceiro Setor — editais | Outros programas | Brasil/BR | 2 | 2026-09-17 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-3919592882f0 | Redion abre seleção para projetos sociais e culturais com ca | Observatório do Terceiro Setor — editais | Outros programas | Brasil/BR | 2 | 2026-09-10 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-bf7dd018241c | 231 editais abertos voltados a ONGs e OSCs somando mais de R | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 2 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-01619b77b6f8 | Como Solicitar uma Doação | Motor de Recorrência — revisita as oport | Outros programas | Estado/BR | 2 | 2026-09-22 | sim | indefinido: sem histórico nem ciclo |
| nova-ccaa100a25a4 | Engajamento, agentes de mudança e governança climática | Motor de Recorrência — revisita as oport | Outros programas | Estado/BR | 2 | 2026-09-22 | sim | indefinido: sem histórico nem ciclo |
| nova-5683dde2381a | Quatro iniciativas vencem premiação do CNJ em gestão de pess | TJGO - penas pecuniárias 1ª Vara de Exec | Destinação judicial | Brasil/BR | 1 | 2026-09-16 | sim | indefinido: sem histórico nem ciclo |
| nova-11c258992c72 | Webinar gratuito vai orientar OSCs sobre prestação de contas | ABCR — Associação Brasileira de Captador | Destinação judicial | Estado/BR | 1 | 2026-09-21 | sim | indefinido: sem histórico nem ciclo |
| nova-ec0435172214 | Grupo Equatorial abre chamada com mais de R$ 61 milhões para | Observatório do Terceiro Setor — editais | Fundações e institutos privados | Brasil/BR | 1 | 2026-09-12 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-8a1dc698eac9 | Instituto de Engenharia contrata profissional de Captação de | ABCR — Associação Brasileira de Captador | Fundações e institutos privados | Estado/BR | 1 | 2026-09-25 | sim | indefinido: sem histórico nem ciclo |
| nova-fec270c47329 | 15:19 
                   
                   Votações conju | Assembleia Legislativa de Goiás — propos | Outros programas | Estado/GO | 1 | 2026-09-16 | sim | indefinido: sem histórico nem ciclo |
| nova-e1762a1c28f7 | 15:32 
                   
                   Requerimentos, | Assembleia Legislativa de Goiás — propos | Outros programas | Estado/GO | 1 | 2026-09-17 | sim | indefinido: sem histórico nem ciclo |
| nova-ff7c62ae5fc0 | Eventos e Prêmios | FEAS-GO - cofinanciamento da assistência | Outros programas | Estado/GO | 1 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-b0eb760d0092 | Edital Alimento no Prato oferece até R$ 800 mil para projeto | Observatório do Terceiro Setor — editais | Outros programas | Brasil/BR | 1 | 2026-09-08 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-d371274db1a0 | Edital prevê seleção de 58 apresentações artísticas para o N | Secult Goiás — Goyazes e Aldir Blanc | Outros programas | Brasil/BR | 1 | 2026-09-15 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-e5fb908f6b88 | Rede Memória Viva abre inscrições para organizações que pres | Observatório do Terceiro Setor — editais | Outros programas | Brasil/BR | 1 | 2026-09-08 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-12fac90504c2 | CNPJ das propostas aprovadas no Edital 1 | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 1 | 2026-09-26 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-4796008ed022 | Dia de Doar vai acontecer em 2 de dezembro e mobilizar milha | ABCR — Associação Brasileira de Captador | Outros programas | Estado/BR | 1 | 2026-09-24 | sim | indefinido: sem histórico nem ciclo |
| nova-d499ba03877e | Editais  Oportunidades de financiamento para organizações da | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 1 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-aa428dd4ec58 | Edital nº 001/2026 - Chamamento público para  registro de ca | Motor de Recorrência — revisita as oport | Outros programas | Estado/BR | 1 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-833a5b50d985 | Os  editais  aqui disponibilizados são oportunidades voltada | Motor do Piloto — busca aberta no tercei | Outros programas | Estado/BR | 1 | 2026-09-22 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |
| nova-a258b361bb1d | Patrocínios | Motor de Recorrência — revisita as oport | Outros programas | Estado/BR | 1 | 2026-09-25 | sim | indefinido: sem histórico nem ciclo |
| nova-73526e946e17 | Santa Luzia do Paruá abre edital para impulsionar projetos s | ABCR — Associação Brasileira de Captador | Outros programas | Estado/BR | 1 | 2026-09-07 | sim | pontual: vale o prazo do próprio edital; nova edição provável em ~12 meses se o órgão repetir |

## 4. O conselho

**Extremamente pessimista.** 170 opressores ligados, 873 tentativas de IA, zero item. Um motor que "pesquisa todos
os dias" e nunca abriu a própria página não é motor: é lembrete.

**Pessimista.** O catálogo de opressores e as fontes monitoradas são listas separadas: oportunidade nova vira
opressor, mas não vira fonte do monitoramento diário. A promessa "aumentar as fontes monitoradas" não se cumpre.

**Levemente pessimista.** Duplicados no nascimento (4× "Convênios e parcerias") mostram que o criador de opressores
não compara com o que já existe.

**Neutro (ponderador).** O desenho está certo — oportunidade nova → opressor por 30 dias → leitura e IA → previsão —
e o elo que faltava agora existe: o Interceptador lê a página com o modelo local. Ordem: (1) os 40 opressores sem
leitura passam pelo Interceptador (em curso); (2) opressor com página lida vira fonte monitorada (quarentena de
`config/fontes.json`), fechando o ciclo; (3) deduplicar no nascimento por programa + órgão; (4) aposentar a fase de
IA por chave externa e usar o Interceptador também nos dias 3, 6 e 9; (5) registrar ciclo/época pelo histórico do
órgão (base de recorrência) para a previsão.

**Levemente otimista.** 92 oportunidades novas já se transformaram em opressores com página conhecida: a matéria-
prima da previsão está lá.

**Otimista.** Com o Interceptador lendo os opressores, cada um passa a ter prazo e condições comprovados — e o
quadro de cada motor já mostra as oportunidades únicas com data de publicação.

**Extremamente otimista.** Quando a página lida virar fonte monitorada, cada oportunidade descoberta vira uma
busca permanente — a próxima edição chega sozinha, com data prevista.
