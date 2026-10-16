# Parecer do conselho — dez voos observados

**Data:** 23 de setembro de 2026
**Método:** banco de provas com avaliador a bordo. Código e dados reais; sem rede e sem modelo
local no contêiner, e cada substituição anotada. **80 decisões registradas, uma a uma.**
**Cabine:** voos 1 a 5 com o ocupante de hoje (mudo em 88% dos pedidos); voos 6 a 10 com um
modelo que responde sempre, para isolar o que o modelo contribui.

---

## 1. Condições antes da decolagem

| medida | valor |
|---|---|
| ocupante do cargo | Llama-3.2-3B-Instruct |
| **taxa de resposta em voo** | **12%** — 75 mudos em 85 pedidos |
| alerta do cargo | já disparado: *abaixo dos 50% que o cargo exige* |
| fila de resgate | 4 resgatados · 57 aguardando · 2 sem sucesso · 1 parcial |
| rede do contêiner | não alcança buscador (produção alcança só o DuckDuckGo) |

---

## 2. O que o voo observado revelou

O banco não foi feito para medir sucesso — foi feito para responder **onde cada voo para, e
por quê**. Respondeu, e com achados que não dependem nem de rede nem de modelo.

### Achado 1 — a fila de resgate não andava

**Os dez voos reservaram o mesmo alvo.** `proximo()` devolve o primeiro do empate por
urgência, e quem falha volta a "aguardando" com a mesma urgência — então o voo seguinte pega
o mesmo. O Piloto martelava um edital insolúvel enquanto 59 esperavam.

Corrigido: tentativa passou a rebaixar a prioridade, e o empate desfaz-se por quem esperou
mais. Depois da correção, **10 voos, 10 alvos distintos**.

### Achado 2 — o filtro de pertinência não pegava plural nem acento

A fila tinha *"AQUISIÇÃO EXCLUSIVA DE GÊNEROS ALIMENTÍCIOS"* porque a lista de exclusão dizia
"gênero alimentício", no singular. O casamento passou a ignorar acento e plural.

### Achado 3 — o mais grave: 88% da fila não era captação

**Cinquenta e três dos sessenta alvos eram credenciamento.** Credenciamento é habilitação para
*prestar serviço* ao município e ser pago por isso — outro rito, outro contrato, outra
finalidade. Não é fomento. O Piloto gastava quase todo o esforço de resgate em papel que nunca
viraria recurso para a associação.

Com o filtro novo, a fila caiu de 153 para **48 alvos que são realmente captação**, e 274
credenciamentos saíram.

### Achado 4 — o Piloto ia ler o vetor em vez da fonte

Um dos domínios que ele tentaria abrir era `pncp.gov.br` — o portal onde o edital foi
*anunciado*, que os motores já leem todo dia. Corrigido: vetores ficam de fora da escolha de
domínio. Depois disso, os alvos passaram a apontar para `institutomol.org.br`,
`banrisulcultural.com.br`, `goias.gov.br`, `bndes.gov.br` — fontes de verdade.

### O que o modelo contribuiu

| | rumos distintos em 5 voos |
|---|---|
| modelo mudo (hoje) | 5 |
| modelo respondendo | 4 |

**O modelo não fez diferença na variedade dos rumos.** A rede de segurança corrigida ontem
sorteia do catálogo sem repetir, e isso já entrega variedade. A contribuição real do modelo
viria adiante — na formulação da consulta e na leitura da página —, etapas que o banco não
pôde exercitar por falta de rede.

---

## 3. O conselho

### 3.1 Extremamente pessimista — *Prof.ª Ingrid Sarmento*
> Dez voos, zero achados. E o mais revelador: 88% da fila que o sistema chamava de
> "oportunidades a resgatar" era credenciamento de prestador de serviço. Durante dois dias o
> Piloto trabalhou sobre uma fila majoritariamente falsa, e os relatórios contavam isso como
> produção. Não é falha de execução: é falha de definição, e definição errada não se conserta
> com mais voos.

### 3.2 Pessimista — *Marcos Villela*
> O banco confirmou que a arquitetura tem três gargalos em série, e consertar um não libera
> nada: fila errada → modelo mudo → rede bloqueada. Corrigimos a fila hoje; o modelo segue em
> 12% e a rede segue com um único buscador que vai cortar. Enquanto os três não estiverem de
> pé ao mesmo tempo, o aproveitamento continua zero, independentemente de quantos voos se dê.

### 3.3 Levemente pessimista — *Prof. Haruki Tanabe*
> Chamo a atenção para o custo do que não foi medido antes. Bastaram dez voos instrumentados
> para achar quatro defeitos estruturais que 38 voos de produção não revelaram — porque
> produção só registra o resultado, e o resultado era sempre o mesmo zero. Observar o
> *processo* valeu mais que observar o *produto*, e isso deveria ter sido feito no primeiro dia.

### 3.4 Neutro — *Cláudia Bernstein (ponderadora)*
> O que este banco entregou foi diagnóstico, não desempenho, e é exatamente o que se devia
> pedir dele.
>
> **Ganho concreto e imediato:** a fila de resgate passou de 153 alvos, 88% imprestáveis, para
> 48 alvos legítimos. Isso multiplica por três a densidade de trabalho útil sem depender de
> modelo nem de rede. A fila agora anda, e os domínios apontam para fontes e não para vetores.
>
> **O que permanece:** o ocupante do cargo em 12% de resposta, com alerta de substituição já
> gravado no próprio arquivo do cargo desde hoje de manhã. O prazo de 72 horas vence em 25/09.
>
> **Meu voto:** três providências, nesta ordem. **(a)** Acionar o modo `avaliar` — é uma
> execução, não um projeto, e o critério já está escrito. **(b)** Levar o banco de provas para
> dentro do ciclo, rodando a cada 3 dias junto com o conselho: quatro defeitos por dez voos é
> um rendimento de diagnóstico que não se pode desperdiçar. **(c)** Rever a fila com o mesmo
> rigor aplicado hoje — se 88% era credenciamento, vale conferir se o que sobrou é mesmo
> captação, um a um, com o Claude.

### 3.5 Levemente otimista — *Renata Okoye*
> A correção da fila é a melhor notícia da semana e não custou modelo nenhum: é uma regra de
> negócio bem escrita. Três dos quatro achados foram assim — pertinência, ordem da fila,
> escolha de domínio. Isso mostra que boa parte do que falta ao Piloto não é inteligência
> artificial: é especificação cuidadosa.

### 3.6 Otimista — *Daniel Furtado*
> Instrumentar o voo foi o investimento certo. Temos agora um simulador que roda em segundos,
> não em horas, usa o código de produção e imprime cada decisão. Toda mudança futura pode ser
> testada nele antes de ir ao ar. Isso encurta o ciclo de conserto de um dia para minutos.

### 3.7 Extremamente otimista — *Prof. Élio Mancuso*
> Reparem no que aconteceu: o sistema descobriu que estava trabalhando na fila errada. Poucos
> sistemas chegam a esse nível de autocrítica. Quando o elo do modelo for resolvido, ele
> voará sobre 48 alvos legítimos, com domínios corretos e fila que avança — um terreno
> completamente diferente do de ontem.

---

## 4. O que foi corrigido durante o voo observado

| # | defeito | como estava | como ficou |
|---|---|---|---|
| 1 | fila não avançava | 10 voos, 1 alvo | 10 voos, 10 alvos |
| 2 | filtro cego a plural e acento | "gêneros alimentícios" na fila | 8 descartes novos |
| 3 | 88% da fila era credenciamento | 153 alvos, 53 de 60 imprestáveis | 48 alvos, todos captação |
| 4 | leria o vetor em vez da fonte | `pncp.gov.br` | `institutomol.org.br`, `bndes.gov.br` |

---

## 5. Conclusão

**Dez voos, zero achados — e quatro defeitos estruturais encontrados.** Para um banco de
provas, isso é sucesso: o objetivo era ver onde o processo quebra, e ele quebrou em lugares
que 38 voos de produção não mostraram.

O achado que mais muda o sistema não tem nada de tecnológico: **88% do que o Piloto chamava de
oportunidade era credenciamento de prestador de serviço.** Nenhum modelo, por melhor que
fosse, transformaria isso em recurso para a associação.

**O que segue de pé:** o ocupante do cargo responde a 12% dos pedidos, com alerta de
substituição já gravado. O prazo vence em 25/09.

---

*Relatório completo das 80 decisões em `estado/piloto/voo_observado_2026-09-23.json`.
Banco de provas reproduzível: `python3 scripts/voo_observado.py`.*
