# Parecer do conselho — o Piloto funciona agora?

**Data:** 23 de setembro de 2026, fim do dia
**Objeto:** o Piloto depois de reconfigurado para as duas missões definidas pelo titular
**Método:** dez voos no banco de provas, com avaliador a bordo. 80 decisões anotadas.

---

## 1. O que mudou desde a última medição

| | antes (hoje de manhã) | agora |
|---|---|---|
| fila do Piloto | 57 alvos, **100% PNCP** | 0 alvos — o que não era dele saiu |
| editais entregues ao Claude | — | **424** com o motivo escrito item a item |
| tentativas por edital | 3 | **1** — depois passa ao Claude |
| missão 2 | prospecção genérica, 0 resultados em 38 voos | reconhecimento do terceiro setor |
| voos que concluíram | 0 de 10 | **10 de 10** |
| financiadores no radar | **0** em 38 voos de produção | **15**, em 10 voos de banco |

---

## 2. Como os dez voos se comportaram

Todos os dez seguiram o mesmo desenho, sem travar em nenhuma etapa:

1. **Briefing** — rumo definido (modelo mudo → sorteio do catálogo, sem repetir)
2. **Missão 1 · triagem** — 424 ao Claude, 0 ao Piloto, e a assertiva de que nenhum PNCP vaza
3. **Missão 1 · resgate** — nada a resgatar, porque o acervo é todo PNCP: **o voo inteiro vai para a missão 2**
4. **Missão 2 · plano** — a partir do voo 2, o alvo vem do que foi descoberto antes
5. **Missão 2 · crivo** — a página passa ou é descartada por já ser coberta por motor
6. **Missão 2 · leitura** — 1 a 4 financiadores por página, com a via de cada um
7. **Missão 2 · catálogo** — o radar cresce e o plano dos próximos voos se altera
8. **Aprendizado** — efetividade medida pelo critério certo

**Resultado:** 30 registros, 15 empresas distintas no radar, 6 aguardando investigação.
Por via: 10 patrocínio, 3 incentivo fiscal, 2 doação. Por frente: 8 imprensa, 3 entidade,
3 evento, 1 prestação de contas.

### Quatro defeitos aparecerem durante o próprio teste, e foram corrigidos

| defeito | como apareceu | conserto |
|---|---|---|
| aprendizado marcava **efetividade 0** num voo com 4 financiadores | o crivo exigia prazo e inscrição, que edital tem e financiador não | ramo próprio: no reconhecimento, serve quem é nomeado com o trecho que o credita |
| via errada por nome por extenso | a matéria escreve "Fundo da Criança e do Adolescente", a lista dizia "FIA" | nomes por extenso entraram na lista |
| via contaminada pela frase vizinha | "apoio da Construtora Meridiano. A quadra foi viabilizada […] com recursos da Lei de Incentivo" fazia a Construtora virar incentivo fiscal | a janela passou a parar no ponto final |
| o ponto entrava no nome | `[\w&.\-]` aceita ponto: "Meridiano. A" virava um nome só e a captura pulava a frase | ponto só dentro de abreviatura ("S.A" sim, "Meridiano. A" não) |

Os dois últimos eram o mesmo defeito em camadas: **quatro empresas estavam classificadas como
incentivo fiscal por contágio do vizinho.** Isso mandaria o pedido pela porta errada — o setor
fiscal em vez do marketing.

---

## 3. O conselho

### 3.1 Extremamente pessimista — *Prof.ª Ingrid Sarmento*
> Não confundam banco de provas com voo. Os 15 financiadores saíram de cinco páginas que **eu
> mesma escreveria para passar no teste**: texto limpo, crédito explícito, português de manual.
> A página real tem menu, rodapé, JavaScript, nome de empresa em imagem e crédito em letra de
> cartaz. Enquanto não houver uma leitura de página real, o que temos é a prova de que o
> extrator lê o que foi feito para ele ler. E o ocupante do cargo continua mudo em 88%.

### 3.2 Pessimista — *Marcos Villela*
> Concordo com a ressalva e acrescento a mais séria: **a missão 1 ficou sem trabalho**. Zero
> alvos. Está correto — PNCP não é dele —, mas significa que metade da finalidade do Piloto
> hoje não tem objeto. Se os motores continuarem trazendo só PNCP, essa missão nunca acorda, e
> o sistema fica com um cargo de duas funções exercendo uma.

### 3.3 Levemente pessimista — *Prof. Haruki Tanabe*
> Chamo atenção para o que os quatro defeitos de hoje têm em comum: **todos eram de leitura de
> texto, e todos passariam despercebidos em produção**, porque produziriam um radar com nomes
> certos e vias erradas. Ninguém olharia. Isso sugere que a extração precisa de um teste de
> regressão com frases adversariais — não só as bem-comportadas.

### 3.4 Neutro — *Cláudia Bernstein (ponderadora)*
> Separo o que está provado do que está apenas indicado.
>
> **Provado:** o encadeamento das duas missões funciona de ponta a ponta; o PNCP saiu e não
> vaza; a regra de uma única análise está ativa; o plano de voo se altera com o que foi
> descoberto, e o voo seguinte investiga; a efetividade passou a ser medida pelo critério certo.
> Dez voos, dez conclusões, zero travamentos.
>
> **Apenas indicado:** que o extrator funcione em página real. As cinco páginas do banco são
> verossímeis, mas foram escritas por quem conhece o extrator, e a professora Sarmento tem
> razão em não aceitar isso como prova.
>
> **Não resolvido:** o ocupante do cargo, em 12% de resposta. Nos dez voos o modelo não fez
> diferença — 5 rumos distintos com ele mudo, 4 com ele falando —, mas isso é porque o banco
> não exercita as duas etapas onde ele importaria: formular a consulta que acha a página e
> julgar se a página serve.
>
> **Meu voto: o Piloto está adequado na arquitetura e não provado na prática.** Três
> providências: **(a)** um voo real com rede, lendo três páginas verdadeiras, antes de declarar
> qualquer coisa; **(b)** o modo `avaliar` do cargo, cujo prazo vence em 25/09; **(c)** um teste
> de regressão da extração com frases difíceis — crédito em caixa alta, nome em sigla, dois
> patrocinadores na mesma frase.

### 3.5 Levemente otimista — *Renata Okoye*
> O que me convence não é o número: é que os quatro defeitos apareceram **dentro do teste**,
> enquanto ele rodava, e foram corrigidos na mesma sessão. Um sistema em que o erro se mostra
> depressa vale mais que um sistema que acerta por sorte. E a separação das duas missões deixou
> o desenho legível pela primeira vez: dá para dizer, em uma frase, o que o Piloto faz.

### 3.6 Otimista — *Daniel Furtado*
> A missão 2 é a primeira coisa que o Piloto faz que nenhum motor faz. Motor lê edital
> publicado; ele lê o que já aconteceu e pergunta quem pagou. São 15 empresas que não estavam
> em lugar nenhum do sistema, cada uma com a via pela qual o dinheiro saiu — e a via é o que
> diz por qual porta pedir. Isso é matéria-prima nova, não reorganização da antiga.

### 3.7 Extremamente otimista — *Prof. Élio Mancuso*
> Reparem no voo 2 em diante: o Piloto passou a investigar o que ele mesmo tinha descoberto no
> voo anterior. O plano de voo deixou de ser dado por nós e passou a ser consequência do
> trabalho dele. É a diferença entre uma rotina e um agente.

---

## 4. Resposta à pergunta

**O Piloto funciona de forma adequada?**

Na arquitetura, **sim**: as duas missões estão separadas, o PNCP saiu da mão dele, cada edital
é analisado uma única vez, a missão 2 faz o que nenhum motor faz, o plano de voo se realimenta
e a efetividade é medida pelo critério certo. Dez voos, dez conclusões.

Na prática, **ainda não provado**: as páginas do teste foram escritas para o teste, a missão 1
está sem objeto, e o ocupante do cargo responde a 12% dos pedidos.

**O que falta para responder sim sem ressalva:** um voo real com rede lendo três páginas
verdadeiras, a troca do ocupante do cargo — prazo em 25/09 — e um teste de regressão da
extração com frases difíceis.

---

*80 decisões em `estado/piloto/voo_observado_2026-09-23.json`.
Reproduzível: `python3 scripts/voo_observado.py`.*
