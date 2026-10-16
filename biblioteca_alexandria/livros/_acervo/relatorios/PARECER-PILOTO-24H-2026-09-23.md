# Parecer do conselho — o Piloto nas últimas 24 horas

**Período:** 22/09 (22 voos) e 23/09 (16 voos até o fechamento) · **38 voos**
**Objeto:** funcionamento da IA local após as correções de ontem
**Método:** números lidos dos arquivos do próprio sistema

---

## 1. O que aconteceu, em números

| medida | 22/09 | hoje | leitura |
|---|---|---|---|
| voos | 22 | 16 | a corrente contínua funciona |
| missões registradas | — | **60** | 32 de resgate, 9 de caça, 9 de local novo, 10 de afiar |
| **missões que trouxeram algo** | — | **3 (5%)** | mesmo índice de antes das correções |
| editais resgatados | 1 | **4** | de 88 relevantes na fila |
| fontes novas descobertas | — | **0** | a missão de expansão não produziu nada |
| abates | 1 (falso) | **0** | o dado de laboratório saiu; não entrou nada real |
| último voo | — | 22,8 min, encerrou por tarefa concluída | o orçamento de tempo está sendo usado |

**Por que as 57 missões não renderam:**

| causa | ocorrências |
|---|---|
| resgate: página oficial não encontrada | 30 |
| nenhum local candidato | 9 |
| resultados vieram, nada passou no crivo | 6 |
| expansão sem resultado | 5 |
| sem proposta de melhoria | 4 |
| busca vazia | 3 |

---

## 2. A descoberta que muda o diagnóstico

**Dos 12 briefings gravados, 9 registram "o modelo não respondeu".** Em 12 voos houve
apenas **2 apostas distintas** — quando deveria haver 12, uma por voo.

Isso reordena tudo o que se poderia dizer sobre o Piloto. Ele não está escolhendo mal onde
procurar: **ele não está escolhendo**. O Llama-3.2-3B não devolve o JSON pedido no briefing,
a rede de segurança entra com o rumo genérico, e o voo sai sem direção própria. O sistema de
prompt único, o crivo de similaridade, os 14 ângulos, o mapa de cobertura — nada disso opera,
porque o passo que os aciona está mudo.

As buscas confirmam: a via DuckDuckGo registra **2 usos em 38 voos**. Um agente que buscasse
de verdade teria centenas.

---

## 3. O conselho

### 3.1 Extremamente pessimista — *Prof.ª Ingrid Sarmento*

> Vinte e quatro horas depois do parecer anterior, o aproveitamento continua em 5%. Não houve
> aprendizado: houve repetição mais bem instrumentada. E há agora uma prova documental de que
> o ocupante do cargo não cumpre a função: 75% dos briefings saem mudos. Um modelo que não
> responde não é um modelo lento nem impreciso — é um modelo ausente. Mantê-lo no posto
> porque passou num benchmark de 21/09 é apego à decisão, não à evidência. Acrescento um
> achado grave: as estatísticas de aprendizado estão contaminadas por motores inexistentes
> chamados `m-teste`, `m-seco` e `m-repete`, com 26 missões somadas. São os testes unitários
> escrevendo na base de produção. Qualquer número que se leia dessa base hoje está errado.

### 3.2 Pessimista — *Marcos Villela, chief engineer*

> Trinta dos trinta e dois resgates falharam por não achar a página oficial. Isso não é
> problema de busca: é problema de método. Procurar a página de um chamamento municipal de
> 2024 por consulta genérica em buscador é a pior estratégia possível — o documento está no
> portal do município, não no índice do buscador. O Piloto deveria ir direto ao domínio do
> órgão, que ele já conhece pelo campo `orgao`, e varrer o site por dentro. A função para isso
> existe desde ontem (`buscar_na_fonte`, leitura de sitemap) e **não está sendo usada no
> resgate**. Construímos a ferramenta certa e continuamos usando a errada.

### 3.3 Levemente pessimista — *Prof. Haruki Tanabe*

> A missão de expansão entregou zero fontes em 24 horas. Ela depende de achar páginas de
> "nossos apoiadores" em sites de outras entidades — o que depende de busca, que depende do
> modelo formular consultas, que está mudo. É uma cadeia de três elos em que o primeiro está
> partido. Enquanto isso, 16 achados foram descartados como "já coberto por motor": o filtro
> funcionou, mas o fato de ele ter disparado 16 vezes mostra que o Piloto continua indo onde
> os motores já vão. A instrução de cobertura está no prompt — e o prompt não é lido.

### 3.4 Neutro — *Cláudia Bernstein, CTO (ponderadora)*

> Separo o que melhorou, o que piorou e o que não se mexeu.
>
> **Melhorou, e é real:** os resgates saíram de 1 para 4; a fila passou a ter só editais
> pertinentes (88, não 438); o acervo foi limpo de 334 registros inúteis; o painel deixou de
> mentir sobre o estado do voo; cada missão agora é avaliada e o motivo do insucesso fica
> registrado — é por causa disso que este parecer existe com números em vez de impressões.
>
> **Não se mexeu:** o aproveitamento, em 5%. E a razão agora está identificada com precisão,
> o que é mais valioso do que uma melhora acidental seria.
>
> **Piorou:** a base de aprendizados foi contaminada pelos testes. É defeito de quem escreveu
> os testes, não do Piloto, e precisa ser corrigido antes que qualquer decisão se apoie nesses
> números.
>
> **Meu voto:** o problema não é mais a busca — é o ocupante do cargo. Recomendo, nesta ordem:
> **(a)** limpar a contaminação dos testes hoje; **(b)** usar a leitura direta do site do órgão
> no resgate, que resolve os 30 fracassos de uma vez e não depende de modelo nenhum; **(c)** dar
> ao briefing uma rede de segurança determinística de verdade — um rumo sorteado do catálogo
> de ângulos, em vez de um genérico repetido; **(d)** acionar o modo `avaliar` do cargo, que
> existe desde 21/09 e nunca foi usado: se um reserva bater o ocupante, a troca é uma escrita
> em arquivo. O critério do cargo exige ≥50% de acerto e um modelo mudo entrega 25%.

### 3.5 Levemente otimista — *Renata Okoye, staff engineer*

> Ontem não sabíamos por que o Piloto não achava nada. Hoje sabemos que ele não decide, e
> temos a linha exata onde isso acontece. Foi a instrumentação criada ontem — briefings
> gravados, avaliação por missão, motivo do insucesso, placar por via — que tornou esse
> diagnóstico possível em um dia. Um sistema que se explica sozinho conserta-se rápido. E vale
> registrar o que funcionou sem ninguém olhar: 38 voos encadeados, nenhum estouro de limite,
> nenhum voo duplicado, o último encerrando por tarefa concluída em 22,8 minutos.

### 3.6 Otimista — *Daniel Furtado, chief engineer*

> O trabalho de 24 horas não aparece no aproveitamento porque foi todo em fundação: filtro de
> pertinência, aprendizados com quarentena, prospecção com promoção a motor, duas listas de
> empresas com critérios próprios, catálogo de leis. Quando o elo do modelo for consertado —
> e é uma troca de ocupante, não uma reengenharia —, essa máquina passa a render sobre uma
> base muito melhor do que a de ontem. Os 4 resgates já são prova de conceito: quando o
> caminho não depende do modelo, o sistema entrega.

### 3.7 Extremamente otimista — *Prof. Élio Mancuso*

> Há um dado que ninguém comentou e que eu considero o melhor da semana: o Piloto gerou **20
> sugestões de melhoria para os motores**, e nenhuma foi aplicada ainda. É matéria-prima
> parada. Um sistema que propõe como melhorar a si mesmo, ainda que com um modelo fraco, tem
> o mecanismo certo — falta apenas fechar o ciclo entre propor e aplicar.

---

## 4. Erros a corrigir, em ordem de impacto

| # | erro | efeito medido | correção |
|---|---|---|---|
| 1 | Modelo mudo no briefing | 9 de 12 voos sem rumo próprio; 2 apostas em 12 | acionar o modo `avaliar` do cargo e trocar o ocupante se um reserva bater o critério |
| 2 | Resgate busca página por buscador | 30 de 32 falhas | usar `buscar_na_fonte` no domínio do órgão antes de qualquer busca |
| 3 | Testes gravam na base real | `m-teste`, `m-seco`, `m-repete` com 26 missões falsas | isolar a base nos testes e limpar o que entrou |
| 4 | Rede de segurança repete o mesmo rumo | 2 apostas distintas em 12 voos | sortear do catálogo de ângulos quando o modelo não responder |
| 5 | 20 melhorias propostas, 0 aplicadas | ciclo aberto | aplicar no pacote do conselho de 3 dias |
| 6 | Expansão depende do modelo | 0 fontes em 24 h | dar-lhe uma lista inicial de entidades conhecidas para varrer sem depender de consulta gerada |

---

## 5. Conclusão

**O Piloto não está cumprindo a finalidade, e agora sabemos exatamente por quê.** Não é a
busca, que ontem parecia ser o problema: é que o ocupante do cargo não responde em 3 de cada
4 pedidos, e sem a decisão dele o voo sai sem direção.

Isso é uma boa notícia disfarçada: trocar o ocupante é uma escrita em `config/cargo_piloto.json`,
não uma reconstrução. O cargo foi desenhado para isso em 21/09 e o banco de reservas está
pronto — Qwen3-1.7B, Llama-3.2-1B, Gemma-2-2B, Phi-3.5-mini.

**Prazo do conselho:** o de 72 horas fixado ontem vence em 25/09. Mantém-se, com um número
adicional: se o modo `avaliar` não for acionado até lá, o cargo fica vago por definição — um
ocupante que falha 75% das vezes não atende ao critério que o próprio sistema estabeleceu
(≥50% de acerto).

**E uma advertência sobre estes números:** parte das estatísticas de aprendizado está
contaminada por motores de teste. Corrigir isso é pré-requisito para que a próxima avaliação
valha alguma coisa.

---

*Parecer do conselho de sete posições. Números lidos de `estado/piloto/bordo.json`,
`voos.json`, `fila_resgate.json`, `vias.json`, `docs/dados/briefings_piloto.json` e
`docs/dados/aprendizados_piloto.json`.*
