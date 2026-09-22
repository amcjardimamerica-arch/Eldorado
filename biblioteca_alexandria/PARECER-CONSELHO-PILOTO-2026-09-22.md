# Parecer do conselho — o Piloto está cumprindo a finalidade?

**Data:** 22 de setembro de 2026
**Objeto:** auditoria do funcionamento da IA local (Piloto / Llama-3.2-3B) no sistema Eldorado
**Solicitante:** Eduardo Kleber Xavier Lemos — A.M.C. Jardim América

---

## 1. Os números, antes de qualquer opinião

Tudo abaixo foi lido dos arquivos do próprio sistema, não de impressão.

| medida | valor |
|---|---|
| voos no dia 22/09 | 18 |
| missões registradas | 60 |
| **missões que trouxeram algo** | **3 (5%)** |
| empresas no radar de captação | **0** |
| editais resgatados (de 438 incompletos) | **1** |
| abates registrados | 1 — e é `lab-motor`, artefato de teste, não descoberta real |
| buscadores que respondem do servidor | **1 de 6** (html.duckduckgo.com) |

**Por que as 57 missões falharam:**

| causa | ocorrências |
|---|---|
| resgate: página oficial não encontrada | 22 |
| busca voltou vazia (rede ou bloqueio) | 14 |
| nenhum local candidato | 10 |
| resultados vieram, nenhum passou no crivo | 6 |
| sem proposta de melhoria | 5 |

**Veredito factual:** o Piloto voa muito e entrega quase nada. A máquina de voar está
excelente; a de encontrar, não.

---

## 2. O conselho

Composição: dois *chief engineers* de big tech, um *staff engineer* de infraestrutura de
busca, uma CTO de empresa de dados, dois professores de Ciência da Computação e um professor
de Engenharia da Computação — todos com produção em Python e sistemas distribuídos.

### 2.1 Extremamente pessimista — *Prof.ª Ingrid Sarmento (CC, sistemas autônomos)*

> Isto não é um agente de busca: é um gerador de logs. Cinco por cento de aproveitamento em
> 60 tentativas não é "início de curva de aprendizado", é ruído estatístico — com 3 sucessos
> não se distingue acerto de acaso. E há um agravante ético no painel: durante dias ele
> exibiu movimento, hélice girando, estrelas de abate, enquanto o resultado real era zero.
> O sistema estava contando uma história de produtividade que os dados desmentem. Some-se
> que o único "abate" registrado é um artefato de teste chamado `lab-motor`, o que significa
> que **a métrica principal do painel está contaminada por dado de laboratório**. Recomendo
> suspender o ciclo contínuo: 18 voos que produzem zero são 18 oportunidades de o sistema
> gravar lixo por cima de dado bom — e isso já aconteceu três vezes hoje com o painel e uma
> com o `config/piloto.json`.

### 2.2 Pessimista — *Marcos Villela, chief engineer (busca)*

> O defeito é de arquitetura, não de ajuste. Vocês construíram um agente que depende de
> raspar buscadores públicos a partir de um IP de datacenter. Isso não é um obstáculo
> temporário: é o modelo de negócio dos buscadores. Google, Bing e Mojeek não bloqueiam
> por acidente, e o DuckDuckGo que hoje responde vai cortar assim que o volume subir — as
> 14 buscas vazias já são o começo disso, porque 18 voos × 3 consultas em poucas horas é
> exatamente o padrão que dispara o corte. Construir em cima disso é construir em areia.
> Enquanto não houver uma fonte de busca com contrato (API paga ou índice próprio), toda
> melhoria de prompt é decoração.

### 2.3 Levemente pessimista — *Prof. Haruki Tanabe (Eng. Computação)*

> Há um erro de alvo que ninguém notou por dias: **25 das 60 missões foram gastas resgatando
> editais que não servem à entidade** — credenciamento de leiloeiros oficiais, cadastro de
> profissionais de saúde, credenciamento de estabelecimentos médicos. A fila foi construída
> sobre o critério "está incompleto", quando o critério correto é "está incompleto **e nos
> serve**". Dos 438 incompletos, 347 são irrelevantes. Quarenta por cento do esforço do
> Piloto foi para o lixo — e o pior é que ele teria continuado assim indefinidamente,
> porque nada no sistema media pertinência. Métrica ausente é defeito invisível.

### 2.4 Neutro — *Cláudia Bernstein, CTO (ponderadora)*

> Separo o que funciona do que não funciona, porque tratá-los juntos leva a decisões ruins.
>
> **Funciona, e bem:** a corrente de voos (18 execuções encadeadas sem intervenção, cada uma
> dentro do limite do GitHub); o registro — todo voo deixa rastro do que tentou e por que
> falhou, e é graças a isso que esta auditoria foi possível em vez de especulativa; as
> travas de segurança; e a disciplina antifabricação, que merece destaque: o Piloto recusa
> prazo que não esteja escrito na página e descarta trecho que não exista literalmente no
> texto. **Preferir não achar a inventar é a decisão mais valiosa deste projeto**, e é o que
> separa um sistema utilizável de um perigoso.
>
> **Não funciona:** a captação em si. Zero empresas, 1 edital resgatado, 1 abate falso.
>
> **A causa-raiz é uma só, e é medível:** o Piloto depende de um insumo — resultados de
> busca — que chega quebrado. Dos seis buscadores, um responde. Ele estava em terceiro na
> fila de tentativas, atrás de dois que falham com 20 segundos de espera cada. Cada consulta
> queimava 40 segundos antes de chegar ao único que funciona. Corrigido hoje.
>
> **Meu parecer:** o Piloto não está cumprindo a finalidade, mas não por estar mal
> construído — e sim por estar apoiado num insumo instável. Não recomendo suspendê-lo, como
> pede a conselheira Sarmento, porque o custo é zero (repositório público) e o registro tem
> valor diagnóstico. Recomendo três coisas: **(a)** parar de medir voos e passar a medir
> achados; **(b)** dar 72 horas para as correções de hoje mostrarem efeito, com um número
> objetivo — se em 72 h não houver ao menos 5 empresas no radar e 10 editais resgatados, a
> raspagem de buscadores está condenada e é hora de decidir entre API paga ou coleta pelo
> computador do titular; **(c)** limpar o `lab-motor` do painel hoje, porque métrica
> contaminada corrói a confiança em tudo o mais.

### 2.5 Levemente otimista — *Renata Okoye, staff engineer*

> O diagnóstico desta semana vale mais do que os achados que não vieram. Vocês saíram de
> "não sei por que não funciona" para "sei que 1 de 6 buscadores responde, que 40% das
> missões tinham alvo errado e que o modelo não devolve JSON no briefing". Isso é um sistema
> observável, e observabilidade é o que permite consertar. A propósito do modelo: ele não
> está errando — está calado, e o sistema tem rede de segurança para isso, então degrada em
> vez de quebrar. Com o filtro de pertinência, a fila caiu de 438 para 92 alvos que
> realmente servem: a mesma máquina agora aponta para o lugar certo.

### 2.6 Otimista — *Daniel Furtado, chief engineer (plataforma)*

> O ativo aqui não é o que o Piloto achou; é a infraestrutura que ele construiu enquanto não
> achava. Existe uma corrente de execução autônoma, um sistema de briefing que lê o passado
> antes de decidir o futuro, uma fila de resgate com prioridade, memória de erros e um painel
> que a partir de hoje é auditável. Trocar o insumo de busca é mudar uma lista de seis linhas
> num arquivo. Toda a máquina em volta já está pronta e testada, e é ela que custa meses.

### 2.7 Extremamente otimista — *Prof. Élio Mancuso (CC, recuperação de informação)*

> Quando a fonte de busca estabilizar, este desenho vai render acima da média, e explico por
> quê: a maioria dos agentes de captação procura *editais*. Este procura *a fonte do
> dinheiro* — a empresa que deduz imposto, o instituto que patrocina, o edital do ano passado
> que indica recorrência. É a pergunta certa. Some-se a disciplina de só aceitar o que está
> escrito na página, e vocês terão uma base de dados em que se pode confiar para escrever
> projeto — coisa rara. A escassez de hoje é de matéria-prima, não de método.

---

## 3. Cada erro, com causa e correção

| # | erro | causa-raiz | correção | estado |
|---|---|---|---|---|
| 1 | Busca vazia em 14 missões | 5 dos 6 buscadores recusam IP de datacenter; o único que responde estava em 3º, atrás de dois que gastam 20 s cada | ordem refeita pela medição real; para no primeiro que entregar | **corrigido** |
| 2 | DuckDuckGo começando a cortar | 18 voos × 3 consultas sem intervalo | espera de 4 s entre buscas | **corrigido** |
| 3 | 25 missões em editais inúteis | fila montada por "incompleto", sem critério de pertinência | filtro por objeto da entidade: 438 → 92 alvos; 347 descartados com motivo registrado | **corrigido** |
| 4 | Painel dizia "em terra" com 18 voos feitos | painel lia a chave `missoes`; o arquivo publica `ultimas` | chave corrigida | **corrigido** |
| 5 | Voo saía com 1 resgate em vez de 6 | reserva gravada em memória, não em arquivo | reserva persistida; item não atendido volta à fila | **corrigido** |
| 6 | Caixa do Piloto em todas as páginas | seção fora da lista `VISTAS` que controla as abas | escondida em toda vista que não seja a inicial | **corrigido** |
| 7 | Painel decorativo: movimento sem informação | estado publicado só ao fim do voo, sem carimbo para o painel julgar | bloco ao vivo com carimbo de hora; o painel recalcula pelo relógio de quem olha e mostra SEM SINAL + botão de acionamento | **corrigido** |
| 8 | `config/piloto.json` sobrescrito por um voo | orçamento tratado como estado de execução | protegido no workflow | **corrigido** |
| 9 | `docs/dados/dados/` criado a cada voo | `cp -r` copia para dentro quando o destino existe | copia o conteúdo, não a pasta | **corrigido** |
| 10 | Painel perdido 3× | job de dados e resolução de rebase com `--ours` | proteção nos dois workflows | **corrigido** |
| 11 | Abate falso (`lab-motor`) inflando o painel | dado de teste nunca removido | **pendente** — remover hoje | aberto |
| 12 | Modelo não responde ao briefing | Llama-3.2-3B falha em devolver JSON estruturado | rede de segurança já existe (rumo genérico); avaliar troca pelo banco de reserva | aberto |
| 13 | 6 resultados reprovados no crivo | léxico do Motor 29 pode estar restritivo demais | **pendente** — medir antes de mexer | aberto |

---

## 4. Conclusão

**O Piloto não está cumprindo a finalidade.** Em 18 voos produziu zero empresas para o radar
e um edital resgatado. Isso precisa ser dito sem atenuação.

**Mas o motivo não é o que parecia.** Não é o modelo local, nem a arquitetura do agente: é
que ele dependia de um insumo quebrado (cinco dos seis buscadores mudos) e mirava no alvo
errado (40% do esforço em editais que não servem à entidade). Os dois defeitos foram
medidos e corrigidos hoje.

**O prazo do conselho:** 72 horas. Se até 25/09 o radar não tiver ao menos **5 empresas** e a
fila não tiver ao menos **10 editais resgatados**, a raspagem de buscadores públicos está
condenada como estratégia, e a decisão passa a ser entre contratar uma API de busca ou fazer
a coleta pelo computador do titular — onde o IP é residencial e nenhum buscador bloqueia.

**O que não se deve perder de vista:** a recusa do sistema em inventar prazo ou documento.
Num sistema que vai embasar projeto e prestação de contas, um dado errado custa mais do que
dez dados ausentes.

---

*Parecer emitido pelo conselho de sete posições a pedido do titular. Os números foram lidos
de `estado/piloto/bordo.json`, `estado/piloto/fila_resgate.json`,
`estado/piloto/diagnostico_busca.json` e `dados/editais/2026-09-09-eldorado-467-completo.json`.*
