# Parecer do conselho — todos os painéis, a leitura ao vivo e a operação dos motores · 27/09/2026

## 1. O diagnóstico: por que o painel mostrava informação errada

| causa | efeito |
|---|---|
| **Todo leitor lia a cópia publicada do site**, republicada a cada 6 h | o repositório recebia dados novos a cada voo (~30 min) e o painel mostrava os de até 6 h antes |
| **O conjunto principal era carregado uma vez**, ao abrir a página; os demais ficavam guardados na memória da sessão | a tela aberta nunca mudava; só recarregando |
| **Os dados do Espião eram travados por sinalizadores** ("já carregado") | o posto dele e os motores ficavam na primeira leitura |
| **O gerador principal quebrou às 17h51** (um campo de data dos opressores novos, gravado em formato diferente pelo código de hoje) e o erro era **engolido** (`|| true`) | por quase 4 horas nenhuma caixa que depende dos dados principais mudou |
| **Calendário** aceitava edital sem site oficial | prazo sem fonte na tela de trabalho |

## 2. O que mudou — uma camada só, para todos os leitores

- **Leitura ao vivo**: todo pedido a `dados/…` e ao conjunto principal vai **primeiro ao repositório** (onde voos e
  monitoramento gravam) e, se falhar, **à cópia do site** — redundância de fonte dentro de cada caixa, sem tela extra.
- **Ciclo de 4 minutos**: tudo é relido e redesenhado; ao voltar para a aba, relê na hora; com janela aberta, espera
  fechar para não atrapalhar. Há "atualizar agora" no cabeçalho.
- **Selo em cada caixa**: quando o dado foi **gerado**, quando foi **lido** e **de onde** (repositório ou reserva);
  âmbar se o gerador daquela caixa está atrasado; vermelho se as duas fontes falharam — e aí a caixa mantém o último
  dado bom, avisando.
- **Gerador principal**: consertado; se voltar a falhar, o erro aparece no registro do voo.
- **Calendário**: só entra edital com **site oficial e prazo de inscrição** identificados; a lista "abertos sem prazo"
  saiu do calendário.

## 3. Leitor por leitor — teste de atualização

Teste: o valor foi alterado na fonte (simulando o repositório) e verificou-se se a caixa mudou no ciclo, sem recarregar.

| caixa | arquivo | quem gera e quando | resultado do teste |
|---|---|---|---|
| cabeçalho (geração dos dados) | `dashboard-dados.js` | voo do Espião (~30 min) e publicação | **atualizou** |
| oportunidades em andamento, radar, Gantt, fila, biblioteca | `dashboard-dados.js` + fragmentos | idem | atualiza no mesmo ciclo (mesmo conjunto) |
| mapa — números por estado e rosa dos ventos | `fluxo_oportunidades.json` | monitoramento + **cada pouso do Interceptador** | **atualizou** (rosa e Goiás) |
| calendário | `dashboard-dados.js` + fluxo | idem | atualiza no ciclo; regra site + prazo aplicada |
| quadros dos motores (indicador de oportunidades) | `achados_motores.json` | monitoramento diário | **atualizou** |
| posto do Espião | `esquadrilha.json`, radar, briefings, resgates | cada voo do Espião | **atualizou** (depois de soltar os sinalizadores) |
| posto do Interceptador | `interceptador.json` + sinal ao vivo | cada voo; sinal a cada etapa | **atualizou** |
| aviões (Espião e Interceptador) | posição ao vivo (ramo piloto-ao-vivo) | a cada etapa | já era ao vivo (3–15 s) |
| ranking de empresas | `ranking_apoiadores.json` | monitoramento semanal | **atualizou** |
| selos | todos | — | 7 caixas com selo |

**Limites honestos:** a leitura é ao vivo, mas cada caixa só muda quando o **gerador** dela roda — o selo diz a data
de geração justamente para que um dado de ontem nunca pareça de agora. O repositório pode servir um arquivo com até
5 minutos de atraso (cache do GitHub); somado ao ciclo de 4, o pior caso fica em ~9 minutos entre a gravação e a tela.

## 4. Operação atual dos motores

Últimas 10 execuções: monitoramento diário 10/10 com sucesso; agenda por motor 10/10; Espião 8 sucesso, 1 no ar, 1
cancelada; Interceptador 8 sucesso, 1 no ar, 1 cancelada; publicação do painel 10/10. Os 14 motores sem verde seguem
o parecer de 26/09 (5 por bloqueio de IP, 4 por alvo errado, 2 por JavaScript, 1 por natureza, 1 por léxico; o PNCP
corrigido). Oportunidades únicas por motor: PNCP 211, ABCR 27, Piloto 24, Observatório 17, Diário de Goiás 10.

## 5. O conselho

**Extremamente pessimista.** Quatro horas de painel congelado por um erro engolido: foi exatamente a situação que o
titular descreve — o sistema achou, e a tela escondeu.

**Pessimista.** A leitura ao vivo não cria dado; se um gerador parar, a caixa fica parada — agora com selo âmbar,
mas parada. O ponto de falha passou da tela para os geradores.

**Levemente pessimista.** O ranking relê 10 MB a cada ciclo; em conexão fraca, pesa. Vale dividir em páginas.

**Neutro (ponderador).** A arquitetura agora é robusta: uma camada única de leitura, fonte principal e reserva,
ciclo curto, selo de procedência em cada caixa e erro de gerador visível. Parâmetros de qualidade: (1) nenhuma caixa
sem selo; (2) selo âmbar dispara revisão do gerador; (3) falha do gerador aparece no voo; (4) calendário só com site
e prazo. Próximo passo: alerta automático quando qualquer gerador passar do seu prazo.

**Levemente otimista.** Todos os leitores testados atualizaram sem recarregar a página.

**Otimista.** O mapa e o calendário passam a mudar a cada pouso do Interceptador: o que ele comprova aparece em
minutos.

**Extremamente otimista.** O mostruário passa a ser tão vivo quanto os motores: o que o sistema encontra, a tela mostra.
