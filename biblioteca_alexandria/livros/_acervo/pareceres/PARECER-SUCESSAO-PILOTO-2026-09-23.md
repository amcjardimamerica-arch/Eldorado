# Parecer do conselho — quem assume o cargo de Piloto?

**Data:** 23 de setembro de 2026, noite
**Pergunta:** o novo Piloto pode assumir?
**Resposta curta:** **não hoje, e não por falta de candidato — por falta de medição.**

---

## 1. O que se tentou, e o que barrou

Tentei medir os candidatos no runner três vezes ao longo do dia. As três esbarraram em
barreiras diferentes, e nenhuma delas tinha a ver com a qualidade dos modelos.

| tentativa | o que aconteceu |
|---|---|
| 13h28 · benchmark dos cinco | **cancelada na fila.** A corrente de voos dispara a cada ~7 min e, com `cancel-in-progress: false`, o GitHub guarda só a corrida pendente mais recente por grupo — o voo seguinte empurrava o benchmark para fora |
| 21h37 · benchmark dos cinco | rodou 30 minutos e foi **cancelada pelo teto do job**. Os 30 minutos foram desenhados para o VOO — uma pesquisa por execução — e o benchmark é outra coisa: cinco modelos contra 120 itens em 4 CPUs |
| 22h10 · avaliação só do Qwen3 | **concluiu**, e devolveu `"modelo não disponível no runner"`: o GGUF não baixou |

Três barreiras operacionais, três dias de suspeita mal dirigida. Eu vinha atribuindo ao
Qwen3 uma nota de 0,820 que saiu de substitutos que **eu mesmo parametrizei** — e ele nunca chegou a ser executado uma única vez.

---

## 2. O que se sabe de verdade sobre cada candidato

| candidato | medido? | o que se tem |
|---|---|---|
| **Llama-3.2-3B** (ocupante) | sim, duas vezes | venceu o benchmark 1 em 21/09 com acerto 0,597, zero prazos inventados, 16 tok/s. Caiu para 0,342 no benchmark 2, em 22/09. Em voo, responde a **12%** dos pedidos em 393 medidos |
| **Qwen3-1.7B** | **não** | o download falhou; nenhum número real existe |
| Llama-3.2-1B | não | nunca executado |
| Gemma-2-2B | parcial | não subiu no benchmark 1; no 2, inventou prazo |
| Phi-3.5-mini | não | nunca executado |

**Uma ressalva que o conselho considera decisiva:** no benchmark 2, todos os candidatos
caíram juntos — o Llama de 0,597 para 0,342, o Qwen2.5 de 0,342 para 0,325, a velocidade de
16 para 11,5 tok/s. Queda uniforme aponta para condição de medição, não para os modelos.

---

## 3. O conselho

### 3.1 Extremamente pessimista — *Prof.ª Ingrid Sarmento*
> Passamos três dias discutindo a substituição de um ocupante com base em números que não
> existem. A trilha do cargo, que eu elogiei como diagnóstico, foi tratada como se fosse
> medição — e não é: são bonecos com comportamento declarado por quem os escreveu. O único
> número real do dia é que o GGUF do Qwen3 não baixou. Dar posse a ele agora seria repetir,
> em pior grau, o erro que se acusou ontem.

### 3.2 Pessimista — *Marcos Villela*
> As três barreiras são da mesma família: **o benchmark é hóspede num workflow desenhado para
> voar**. Divide fila com a corrente, divide teto de tempo com o voo, divide o passo de
> download. Enquanto for hóspede, vai continuar sendo despejado. Isso precisa de workflow
> próprio, não de mais uma tentativa.

### 3.3 Levemente pessimista — *Prof. Haruki Tanabe*
> Chamo atenção para o que quase passou: a avaliação devolveu `"modelo não disponível no
> runner"` e nada mais. Sem código HTTP, sem endereço. Sem acesso ao log do Actions não havia
> como distinguir URL errada de arquivo renomeado na origem ou de falha de rede — e cada
> hipótese custa uma rodada. Um erro que não diz a causa é quase tão ruim quanto nenhum erro.

### 3.4 Neutro — *Cláudia Bernstein (ponderadora)*
> **Voto contra a posse, e não é contra o Qwen3: é contra dar posse sem medir.**
>
> O que está provado hoje: o ocupante atual não cumpre o critério — 12% de resposta em 393
> pedidos, com `deve_sair` já marcando isso no arquivo do cargo. Isso basta para tirá-lo.
> Não basta para pôr outro.
>
> A consequência prática é menos grave do que parece. Nos dez voos observados, com o modelo
> mudo, a rede determinística entregou **cinco rumos distintos em cinco voos** — o mesmo que
> um modelo que respondesse. O que se perde sem modelo é a leitura da página e a formulação
> da consulta, não a direção do voo.
>
> **Recomendo, nesta ordem:** **(a)** declarar o cargo VAGO, com o motivo escrito, em vez de
> manter um ocupante reprovado por inércia — foi exatamente a inércia que custou um dia e meio
> ontem; **(b)** dar ao benchmark workflow próprio, com teto próprio e sem disputar fila com
> a corrente; **(c)** conferir a URL do GGUF do Qwen3 antes da próxima tentativa, agora que a
> falha passa a registrar o código HTTP; **(d)** só então a posse, e com números reais.

### 3.5 Levemente otimista — *Renata Okoye*
> As três barreiras foram encontradas **hoje**, todas, e as três já têm conserto no
> repositório: teto por modo, pausa da corrente durante o benchmark, e o motivo da falha
> gravado com código HTTP e endereço. A próxima tentativa parte de um lugar muito melhor do
> que a de hoje de manhã.

### 3.6 Otimista — *Daniel Furtado*
> Vale lembrar por que o Qwen3 entrou na disputa: até hoje de manhã ele estava no banco de
> reserva desde 21/09 e o benchmark **não sabia que ele existia** — duas listas que não
> conversavam. Isso já foi corrigido. Ele ainda não foi medido, mas pela primeira vez está na
> fila para ser.

### 3.7 Extremamente otimista — *Prof. Élio Mancuso*
> O sistema hoje recusou dar posse a um candidato que ele mesmo vinha apontando como melhor,
> porque o número que o apontava não era real. Essa recusa vale mais que a troca.

---

## 4. Decisão recomendada

1. **O cargo fica VAGO.** O ocupante atual não cumpre o critério que o próprio sistema
   estabeleceu, e não há substituto medido. `cargo_vago()` registra quem saiu, por quê, e
   como o Piloto voa sem modelo.
2. **O Piloto continua voando** com a rede determinística: rumo sorteado do catálogo, sem
   repetir os últimos.
3. **A posse fica condicionada a três números**, por candidato: acerto ≥ 50%, zero prazos
   inventados, e a resposta em voo acima de 50% — os mesmos que o cargo já exige.

---

## 5. O que o conselho NÃO decidiu

Não decidiu que o Qwen3 é pior nem melhor que o ocupante. **Não há dado.** Quem ler este
parecer procurando autorização para trocar não vai encontrá-la, e quem ler procurando
condenação do Qwen3 também não.

---

*Números lidos de `estado/piloto/benchmark-1-2026-09-21.json`, `benchmark.json`,
`avaliacao-qwen3-1.7b-2026-09-23.json` e `config/cargo_piloto.json`.*
