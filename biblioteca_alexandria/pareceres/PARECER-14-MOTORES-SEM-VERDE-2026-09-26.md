# Parecer do conselho — os 14 motores sem sinalizador verde · 26/09/2026

*Medido no painel, motor a motor, com a situação que cada quadro exibe e o diagnóstico gravado pelo sensor.*

## Antes de tudo: o sinalizador dizia menos do que devia

O verde exigia **resultado** (achado reconhecido). Um motor que lê a fonte corretamente e não encontra edital naquele dia
ficava com a mesma cor de um motor que nunca leu. **Corrigido hoje**: verde = lê e traz resultado; **verde-claro = lê a fonte,
sem resultado ainda**; vermelho = bloqueio; sem cor = sem leitura. É a "verificação individual de funcionamento e de
resultado" pedida pelo titular — e vale também para os dois Pilotos, agora motores separados (23 Espião, 25 Interceptador).

## Os 14, um a um

| nº | motor | o que o painel mostra | causa real | solução distinta |
|---|---|---|---|---|
| 01 | Diário Oficial de Goiânia | aguardando coleta local | o portal **recusa IP de fora do país**; a nuvem lê a página de recusa (14 bloqueios) | **coleta local** (o computador do titular) ou servidor no Brasil (Oracle São Paulo). Nenhuma mudança de código resolve |
| 04 | PNCP — API | ativo, sem achados | lia **um dia, 20 itens, página 1, Brasil inteiro**: o que interessa não cabia na página | **corrigido hoje**: janela de 3 dias, Goiás primeiro (uf=GO), modalidades 12/3/10, 50 por página, 11 consultas; o classificador de finalidade (89% de acerto) filtra o ruído |
| 05 | Câmara de Goiânia — PLs | ativo, sem achados | goiania.go.leg.br e o SAPL **recusam IP estrangeiro** (49 + 64 bloqueios) | coleta local; alternativa parcial: o Diário da Câmara via Querido Diário quando houver |
| 07 | DJ — TRF1 Seção Goiás | ativo, sem achados | lê a página institucional; **o diário é PDF diário** (e-DJF1) e o sensor não abre PDF por data | apontar para o e-DJF1 do dia (URL por data) e ler o PDF; ou ler a lista de entidades cadastradas para prestação pecuniária da SJGO |
| 08 | Prefeituras — 50 maiores de Goiás | lendo, sem editais reconhecidos | 50 portais heterogêneos, muitos em JavaScript; a rota de descoberta pelo PNCP era só "número do processo" | **usar o PNCP como fonte primária**: desde 2024 todo chamamento municipal está lá; o motor 04 com uf=GO já cobre; o 08 passa a ler só os portais que respondem HTML e a confirmar prazo |
| 10 | TJGO — execução penal | ativo, sem achados | **140 bloqueios** em tjgo.jus.br: recusa IP estrangeiro | coleta local ou servidor no Brasil; enquanto isso, a via já aberta: o motor 24 (MP — destinações) está verde |
| 11 | CNJ — destinações | ativo, sem achados | a página do CNJ é **institucional**: lista o programa, não publica editais; o que existe são as listas de entidades cadastradas por tribunal | mudar o alvo: ler as **resoluções e listas de cadastro** (CNJ 154/2012) e apontar para o cadastro do TJGO; medir por "entidade pode se cadastrar", não por edital |
| 14 | FAPEG | lendo, sem editais reconhecidos | FAPEG usa "chamada pública" e o léxico procura "edital"; quase tudo é pesquisa, não extensão | léxico próprio: "chamada", "extensão", "popularização da ciência", "difusão"; aceitar rendimento baixo e cadência semanal |
| 19 | CNPq / MCTI / Setec | lendo, sem editais reconhecidos | a página gov.br do CNPq é institucional; as chamadas vivem em **memoria2.cnpq.br/web/guest/chamadas-publicas** | trocar a URL da rota pela página de chamadas e aplicar o léxico de extensão (igual ao 14) |
| 20 | Empresas — editais incentivados | lendo, sem editais reconhecidos | a rota lê a **lista de empresas**, não páginas de editais; o site institucional da empresa não tem edital | usar as páginas de editais **mapeadas pelo Interceptador** (fontes novas, em quarentena) e as fichas de empresa (canal de pedido) como rotas |
| 21 | GIFE | lendo, sem editais reconhecidos | gife.org.br/agenda é agenda de eventos; os editais estão nos sites dos **associados**, e a rota derivada nunca foi ligada | ligar a rota derivada: lista de associados → site de cada instituto → página de editais (o Espião já cataloga vários) |
| 22 | Mapa OSC | sem leitura ainda | **nunca executou**: o Mapa das OSC (IPEA) não é fonte de editais; é base de dados | trocar a natureza do motor: **carga mensal pela API do Mapa das OSC** para alimentar as associações com site — hoje nenhuma associação do sistema tem site, e o Espião precisa disso como semente |
| 25/26 | Prosas — editais e prêmios | lendo, sem editais reconhecidos | prosas.com.br/editais é **aplicação em JavaScript**: a listagem chega vazia; as páginas individuais (prosas.com.br/editais/NNNN) são legíveis — o Espião achou várias | ler o **sitemap** da Prosas (lista as páginas de edital) em vez da listagem; cada página individual traz prazo e financiador |

## Padrões que atravessam os 14

- **Cinco são IP** (01, 05, 10 e, em parte, 07 e 08): nenhuma correção de código resolve; é a **coleta local** já prevista ou o servidor no Brasil. Enquanto isso, esses cinco devem mostrar "aguardando coleta local", não "sem achados".
- **Quatro são alvo errado** (11, 19, 20, 21): a rota aponta para uma página institucional ou uma lista, não para onde os editais estão. Correção de configuração, sem código novo.
- **Dois são JavaScript** (25, 26): a fonte existe, a listagem não é legível; o sitemap resolve.
- **Um era parâmetro** (04): corrigido hoje.
- **Um é natureza** (22): não é motor de editais; vira carga de dados.
- **Um é léxico** (14): vocabulário da fonte diferente do nosso.

## O conselho

**Extremamente pessimista — chief engineer.** Catorze motores em trinta sem resultado é quase metade da esquadrilha parada; e cinco deles só voltam com máquina no Brasil, que ainda não existe.

**Pessimista — staff engineer.** Quatro motores apontavam para páginas institucionais há semanas sem ninguém notar — porque o sinalizador não distinguia "lendo e vazio" de "quebrado". O painel escondia o problema.

**Levemente pessimista — professor.** A correção do PNCP é a mais promissora e a menos testada: 11 consultas por dia contra uma; medir amanhã se o ruído não voltou junto.

**Neutro — CTO (ponderador).** Separar funcionamento de resultado no sinalizador foi a mudança certa: agora cada motor mostra onde falha. Ordem: (1) configuração — 19 (URL do CNPq), 21 (rota derivada do GIFE), 20 (fontes do Interceptador), 14 (léxico); (2) Prosas pelo sitemap; (3) Mapa OSC como carga mensal, que destrava as sementes do Espião; (4) TRF1 pelo PDF do dia; (5) os cinco de IP esperam a coleta local — e ficam marcados como tal. Motor 04, já corrigido, é o que mais rende se der certo: o PNCP é a fonte obrigatória de todo chamamento público desde 2024.

**Levemente otimista — professor.** Onze dos catorze estão lendo a fonte todos os dias, sem bloqueio: o aparelho funciona; o que falta é apontá-lo para o lugar certo.

**Otimista — staff engineer.** O Interceptador como motor próprio já mostra 2 validadas e 6 parciais no primeiro dia — a comprovação está funcionando, e dá ao painel um verde que é prova, não impressão.

**Extremamente otimista — CTO.** Com o PNCP por Goiás e a Prosas pelo sitemap, os dois maiores repositórios de chamamentos e editais do país passam a alimentar o sistema diariamente — e o Espião fica livre para procurar o que nenhum deles publica.
