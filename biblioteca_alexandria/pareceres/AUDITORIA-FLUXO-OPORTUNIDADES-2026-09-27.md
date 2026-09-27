# Auditoria dos motores e o fluxo das oportunidades · 27/09/2026

## 1. O que a auditoria encontrou

| ponto | situação antes |
|---|---|
| onde fica o **prazo** | nunca no arquivo mestre: só nos registros de verificação (titular, validação, Interceptador) — o mapa e o calendário dependiam de junções parciais |
| oportunidades dos **Pilotos** (54 candidatas do Espião, ~500 registros do Interceptador) | fora do mestre, logo **fora do mapa e do calendário** |
| **calendário** | só editais com início e fim confirmados do conjunto principal; nada do que os Pilotos acharam |
| **mapa** | contava no navegador, preso aos filtros de situação e período; 1º número sem exigir objeto |
| oportunidade nova → **opressor** | 92 criados até 22/09 e nenhum depois; nenhum leu a própria página; duplicados no nascimento |
| **cadastro para previsão** | não existia |

## 2. O fluxo, em seis etapas (src/fluxo_oportunidades.py)

1. **Encontradas** — mestre (motores) + candidatas do Espião + registros estudados pelo Interceptador.
2. **Únicas** — a mesma oportunidade conta uma vez (endereço e título normalizados).
3. **Possíveis abertas** — prazo não vencido, ou sem prazo e publicada nos últimos 60 dias, mesmo sem informação
   nenhuma (menção recente em diário oficial conta): **1019**.
4. **Confirmadas com o mínimo** — objeto + data-limite de inscrição ainda aberta + link do site oficial, de empresa,
   instituto ou ente público: **11**.
5. **Motor opressor** — oportunidade nova com cara de oportunidade (edital, chamada, seleção, prêmio, fundo; não
   notícia, não dispensa) e não coberta por opressor existente ganha opressor próprio, ligado 30 dias, com a página
   dela; o Interceptador a lê na 5ª fila. Criados hoje: **84** (acúmulo de semanas).
6. **Cadastro preditivo** — `biblioteca_alexandria/base/preditivo/oportunidades.jsonl`: órgão, UF, tipo, ciclo
   (pontual/recorrente/indefinido), publicação, prazo e próxima janela estimada: **186** cadastradas
   ({'indefinido': 83, 'pontual': 86, 'recorrente': 17}).

Roda no monitoramento diário e **ao pouso de cada voo do Interceptador**; o painel lê direto do ramo principal, então
o mapa e o calendário mudam assim que algo é gravado.

Origem das possíveis: {'motor': 968, 'Piloto - Espião': 46, 'Piloto - Interceptador': 5} · tipo: {'ente público': 74, 'empresa/instituto': 112, 'menção em diário oficial': 833}.

## 3. Mapa — os dois números

**1º** = confirmadas com o mínimo; **2º** = todas as possíveis abertas. Brasil: **11/1019**.

| UF | 1º | 2º |
|---|---|---|
| SP | 1 | 241 |
| __nac__ | 5 | 135 |
| PR | 0 | 116 |
| BA | 0 | 102 |
| MG | 0 | 95 |
| RJ | 2 | 64 |
| MS | 0 | 45 |
| RS | 2 | 41 |
| GO | 0 | 32 |
| AL | 0 | 31 |
| SE | 0 | 29 |
| SC | 1 | 24 |
| PE | 0 | 13 |
| ES | 0 | 11 |

As **menções em diários oficiais** pesam no 2º número (são possíveis editais sem nenhuma informação ainda) — por
isso São Paulo, Paraná e Bahia aparecem altos: o Querido Diário cobre muitos municípios desses estados.

## 4. As 11 confirmadas (entram no calendário pelo prazo)

| oportunidade | UF | inscrições até | origem |
|---|---|---|---|
| BNDES abre chamada para apoiar projetos de organizações periféricas em | nacional | 2026-12-04 | motor abcr |
| CHAMAMENTO PÚBLICO, objetivando a celebração de TERMO DE COLABORAÇÃO c | RS | 2026-09-30 | motor pncp |
| Fundação Maria Emília abre edital com apoio de até R$ 1 milhão para pr | nacional | 2026-10-30 | motor abcr |
| 2º Prêmio MOL de Jornalismo para Solidariedade reconhecerá reportagens | nacional | 2026-12-28 | motor observatorio-ter |
| Dispensa de Chamamento Público, com vistas à celebração de parceria, a | SC | 2026-12-31 | motor pncp |
| O presente Chamamento Público se destina a selecionar Organizações da  | RS | 2026-10-07 | motor pncp |
| Seleção de projetos para firmar termo de execução cultural com recurso | SP | 2026-10-02 | motor pncp |
| Prêmio MOL reconhece reportagens que inspiram solidariedade e a cultur | nacional | 2026-12-28 | motor observatorio-ter |
| Parque bondinho pao de acucar abre inscricoes para o edital 2026 de se | RJ | 2026-10-09 | Piloto - Espião |
| As inscrições são gratuitas e permanecem abertas até 19 de outubro, às | nacional | 2026-10-19 | Piloto - Espião |
| BeForms – EDITAL 2026 DE SELEÇÃO DE PROJETOS CULTURAIS DO PARQUE BONDI | RJ | 2026-10-09 | Piloto - Espião |

## 5. O conselho

**Extremamente pessimista.** 11 confirmadas em 1.019 possíveis: 1%. O funil mostra, sem disfarce, que quase nada do
que se encontra chega ao mínimo.

**Pessimista.** O 2º número é dominado por menções em diários fora de Goiás; Goiás tem 32 possíveis e nenhuma
confirmada. A régua está certa, a colheita de Goiás é fraca.

**Levemente pessimista.** 84 opressores de uma vez é recuperação de atraso; se o criador não comparar bem, repete o
erro dos duplicados. A comparação por endereço e título está no código; medir amanhã.

**Neutro (ponderador).** O fluxo agora existe e é único: encontra → deduplica → classifica → cria opressor →
cadastra → mostra no mapa e no calendário. O gargalo é a etapa 4 (o mínimo), e ela depende da leitura: o
Interceptador lendo os opressores novos é o que transforma possíveis em confirmadas. Parâmetro de qualidade: a
proporção confirmadas/possíveis, medida a cada pouso.

**Levemente otimista.** A Fundação Maria Emília já aparece no calendário de outubro, vinda do fluxo — o caminho do
achado à tela está aberto.

**Otimista.** 186 oportunidades cadastradas para previsão, cada uma com ciclo e próxima janela estimada: é a base
que faltava para o Farol pontuar e antecipar.

**Extremamente otimista.** A cada pouso do Interceptador, um possível pode virar confirmado — e o mapa muda na
hora.
