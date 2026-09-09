# Conselho técnico — sete pareceres sobre a auditoria dos motores

Conselho convocado para auditar as rodadas de 08 e 09/09/2026: 468 registros, 231 validações individuais,
30 parâmetros propostos. Sete conselheiros, do extremamente pessimista ao extremamente otimista, cada um
avaliando **individualmente cada etapa** e **as oportunidades analisadas**, e fechando com parâmetros
nomeados.

As oito etapas submetidas ao conselho:

| | Etapa | Volume |
|---|---|---|
| **E1** | Triagem pelo objeto, antes de qualquer coleta | 468 registros |
| **E2** | Consulta à API oficial do PNCP | 317 consultas |
| **E3** | Busca oficial para os registros sem chave | 74 tentados, 12 recuperados |
| **E4** | Leitura do documento do órgão | 209 na fila, 132 fechamentos |
| **E5** | Validação individual com rota e achado | 231 fichas, 228 fechadas |
| **E6** | Acervo no Drive, uma pasta por edital | 20 UF, 130 pastas |
| **E7** | Correção dos motores e da curadoria | 20 famílias, 9 armadilhas, 30 parâmetros |
| **E8** | Entrega, testes e rastreabilidade | 316 testes, patch aplicável |

---

# 1. Parecer extremamente pessimista

**Dra. Ingrid Sallenave** — CTO de plataforma de dados públicos, pós-doutorado em sistemas distribuídos,
autora de trabalho sobre falha silenciosa em pipelines de ingestão. Trabalha com uma pergunta só, que
repete até irritar: *"como este sistema descobriria que está errado?"*

## O que eu não consigo aceitar

Esta auditoria mede, com rigor invejável, **tudo aquilo que entrou na base**. Precisão do veto: 285/285 e
14/14. Falso positivo zero. Falso negativo zero. Excelente — e irrelevante para a pergunta que importa.

**Não há uma única medida do que o sistema nunca viu.** Nenhuma. Os 468 registros são o universo do que
foi coletado, e a taxa de acerto sobre eles não diz nada sobre a taxa de perda. Se dos editais de fomento
publicados no Brasil em 2026 este sistema capturou 4%, todas as métricas desta auditoria continuariam
exatamente iguais — e o titular estaria perdendo 96% das oportunidades com um painel que se declara
verde. **Métrica de precisão sem métrica de recall é um espelho, não um instrumento.**

E há prova de que a perda é real, dentro do próprio material. Os 18 editais do PNAB Ciclo 2 de Goiás não
entraram na base por rota errada — foram descobertos por acaso, na rodada seguinte, ao ler outra coisa.
Quantos "PNAB Ciclo 2" existem hoje, em 26 estados e cinco mil municípios, invisíveis pelo mesmo motivo?
O sistema não sabe. Pior: **não tem como saber**, com a instrumentação atual.

## Etapa por etapa

**E1 — Triagem pelo objeto: 8/10.** Tecnicamente sólida, e a única etapa que eu não atacaria. Ressalva:
decide 68,1% e chama os outros 31,9% de "atenção", o que é uma forma elegante de dizer "não sei". Aceito,
porque não sei é melhor que sei errado.

**E2 — Consulta ao PNCP: 4/10.** 317 consultas, 2,5 s cada, mais leitura de documento, para produzir
**seis** oportunidades aproveitáveis e abertas. Isso é 1,9% de rendimento. E agora sabemos por quê: 311
dos 317 citam a Lei 14.133. **A etapa foi executada com competência técnica sobre uma premissa errada.**
Executar bem a coisa errada é o modo mais caro de falhar, porque produz números que parecem trabalho.

**E3 — Busca dos sem chave: 3/10.** 74 registros, 12 recuperados, 62 abandonados. O rendimento dos 12
recuperados foi de 50% de aprovados — o melhor de toda a operação. E paramos nos 12 porque "a fila foi
priorizada para os documentos". **Abandonou-se a via de maior retorno medido para seguir a de menor.**
Isso não é priorização, é inércia.

**E4 — Leitura de documento: 5/10.** 132 leituras produziram **12 datas finais**. Nove em cada dez
leituras não entregaram prazo. Reconheço que entregaram enquadramento — 110 reprovações fundamentadas —
mas o objetivo declarado da rodada era prazo. E há um detalhe que me incomoda mais: uma revogação
encontrada em 132 documentos. Se a taxa real de revogação for de 1%, quantos editais revogados estão hoje
na base como oportunidade, entre os 336 registros que **não** foram lidos?

**E5 — Validação individual: 7/10.** Boa disciplina. Mas é trabalho artesanal que não escala e, mais
grave, **não deixa a máquina mais capaz**: os 231 rótulos humanos foram usados para corrigir a base, não
para treinar nem avaliar o classificador de forma sistemática. Fez-se o trabalho duas vezes e guardou-se
uma vez.

**E6 — Acervo no Drive: 4/10.** 130 pastas com dossiê, e **nenhum PDF dentro delas**. O documento que
fundamentou cada prazo não está espelhado. Os links do PNCP e dos portais municipais morrem — mudam de
CMS, migram de plataforma, expiram. No dia em que o titular precisar provar em que documento se baseou um
prazo, o acervo terá o dossiê e não terá a prova. **Acervo sem o documento é índice de biblioteca queimada.**

**E7 — Correção dos motores: 6/10.** A correção da curadoria é boa e o teste é bom. Mas atenção ao que
isso revela: **o defeito existiu por quanto tempo?** O catálogo foi regenerado, silenciosamente, quantas
vezes antes de alguém notar? Se a regeneração apagou a curadoria em 09/09, apagou também em agosto, em
julho. **Não há registro histórico que permita responder.** Sistema sem histórico de estado não permite
auditoria retroativa, e este não tem.

**E8 — Entrega: 5/10.** 316 testes verdes, e três deles estavam quebrados **antes** desta rodada — um
deles impossível de passar por asserção contraditória. Uma suíte que convive com falha permanente treina
a equipe a ignorar vermelho. E o `git push` negado significa que **o código auditado não está em
produção**: está num patch, num RAR, na área de trabalho de um computador. Auditoria de código que não
roda é auditoria de intenção.

## Sobre as oportunidades

Dezessete abertas. Duas fechando em **13/09** — daqui a quatro dias — e ambas de patrocinador privado,
descobertas fora do PNCP. Isso deveria assustar: **as duas oportunidades mais valiosas e mais urgentes da
base vieram da via que recebeu a menor parte do esforço.** Indaiatuba e Curitiba são vitórias reais, e
foram achadas por leitura manual de documento, uma a uma, por um agente que perdeu conexão no meio. Não
existe processo aqui. Existe sorte com método.

E a Fundação Maria Emília: até R$ 1 milhão, inacessível por certificado inválido, pendente de telefone
desde ontem. **A maior oportunidade em aberto da base depende de alguém ligar.** Nenhum sistema cobre isso.

## Meus parâmetros

- **P31 — Auditoria cega de recall, obrigatória por rodada.** Sortear 20 municípios e 5 patrocinadores,
  procurar editais de fomento à mão, e comparar com o que o sistema capturou. Publicar a taxa de perda.
  Sem esse número, todos os outros são decorativos.
- **P32 — "Coberto até" por fonte.** Cada fonte registra a data da última visita bem-sucedida e o que foi
  visto. Silêncio de fonte tem de ser distinguível de ausência de edital. Hoje não é.
- **P34 — Congelar o documento que fundamentou o prazo.** O PDF vai para a pasta do edital no Drive, com
  hash. Link morre; prova não pode morrer.
- **P43 — Histórico de estado dos arquivos de configuração.** Um registro por regeneração, dizendo quantas
  fontes e quantas armadilhas havia antes e depois. Defeito silencioso de meses não pode voltar a ser
  descoberto por acaso.
- **P44 — Suíte sem falha tolerada.** Zero testes vermelhos permanentes. Teste que não pode passar é
  removido ou corrigido no mesmo dia, com o motivo escrito.

---

# 2. Parecer pessimista

**Prof. Hélio Bastianetto** — professor titular de engenharia de software, pós-doutorado em Python e em
verificação de programas. Passou vinte anos ensinando que dado sem procedência é rumor com formatação.
Fala devagar e cita o próprio caderno de erros.

## Onde a construção está frágil

Meu foco é um só: **a procedência de cada dado gravado**. E aqui o sistema é melhor do que a média e
ainda assim insuficiente.

O que está certo: a `observacao` de cada registro carrega a fonte, a rota e o achado em texto corrido.
Isso é mais do que 90% dos sistemas de dados públicos que eu já auditei fazem. Li amostras e são
verificáveis por um humano.

O que está errado: **a procedência é por registro, e o dado é por campo.** Um registro pode ter o objeto
vindo da API, o prazo vindo do documento, a página oficial vinda da busca e o veredito vindo de um módulo
Python — e a `observacao` mistura tudo numa frase. Quando quatro registros perderam a data nesta rodada
(Itacaré, Guaíra, Kaloré, Campo do Tenente), a operação foi correta e **manual**, com uma lista de
exceções escrita à mão dentro do script de aplicação. Isso funcionou porque havia um agente cuidadoso.
Não funciona na décima rodada.

Segundo problema: **não há hash do documento**. O prazo de Indaiatuba está confirmado "no edital de 53
páginas". Qual edital? O arquivo baixado em 09/09/2026 às tantas horas, de um endereço que pode devolver
outro conteúdo amanhã, sem aviso e sem versão. Se o órgão substituir o PDF por uma retificação — o que
aconteceu **seis vezes** só no PNAB de Goiás — o sistema continuará afirmando o prazo antigo com a mesma
confiança.

Terceiro: o campo `prazo_situacao` é derivado, e é recalculado com a data de hoje embutida como constante
no script. `HOJE = datetime.date(2026, 9, 9)`. Amanhã, a base mente.

## Etapa por etapa

**E1: 8/10.** O veto é bem escrito e, o que é raro, **bem comentado com o caso real que originou cada
regra**. Isso é engenharia de manutenção de primeira. A ordem de avaliação está documentada e testada.
Ressalva: 20 famílias de expressão regular numa cadeia de decisão de ordem sensível é uma estrutura que
cresce mal. Na trigésima família alguém vai inverter duas linhas e ninguém vai notar. Precisa de tabela
de decisão declarativa, não de cadeia de `if`.

**E2: 6/10.** Correto no protocolo, disciplinado no ritmo, **e desperdiçou o campo mais informativo que
recebeu**: o `amparo legal` veio em todos os 317 registros e só foi usado na análise *post mortem* desta
auditoria. Estava ali desde o começo. Ler o dado que já se tem antes de sair buscando dado novo é a
primeira regra, e ela foi violada.

**E3: 5/10.** 12 de 74. E o mais importante: **não há registro de qual busca foi tentada para os 62
restantes**. Não sei se foram tentados e falharam, ou se não foram tentados. Isso é o mesmo problema da
Dra. Sallenave, na minha linguagem: ausência de dado registrada como ausência de fato.

**E4: 6/10.** Tecnicamente o melhor trabalho da rodada: o sniff de bytes, o `Promise.race` por item, a
descoberta de que 61 de 66 estouros de tempo tinham concluído em segundo plano. Isso é depuração de alto
nível. **Mas o extrator de cronograma é heurística de pontuação sem conjunto de avaliação.** "Cobertura
subiu de 25 para 89 de 209" — subiu medida contra o quê? Ninguém verificou, documento por documento,
se as 89 datas extraídas estão certas. Aposto que a maioria está. Aposto também que há erro entre elas, e
não sei em quais.

**E5: 8/10.** É o trabalho de que mais gosto, e por um motivo específico: os achados são **citações
literais do documento**, entre aspas, com a página ou a cláusula. *"Local e Data da Entrega dos Envelopes:
Departamento de Protocolo, até às 09:00 horas do dia 25/09/2026"*. Isso é prova, não conclusão. Um
terceiro pode conferir. Nota reduzida apenas porque as 231 fichas não foram convertidas em conjunto de
avaliação versionado.

**E6: 5/10.** Estrutura correta, uma pasta por edital independentemente do prazo — decisão acertada do
titular, porque o valor do acervo é a série histórica. Sem os PDFs, é metade da obra.

**E7: 7/10.** A correção da curadoria está bem feita: arquivo separado, reaplicação no fim, recusa de id
instável, e cinco testes incluindo idempotência. **A escolha de recusar id ausente com exceção em vez de
gerar um id silenciosamente é a decisão de projeto mais madura de toda a rodada.** Errar alto e cedo.

**E8: 7/10.** Patch verificado por clone, volta ao commit e aplicação limpa. Correto. Mas concordo com a
crítica: não está em produção.

## Sobre as oportunidades

As 17 são plausíveis e cada uma tem endereço. Confiro duas ao acaso e as duas se sustentam: Indaiatuba
com citação literal do edital e Curitiba com citação do objeto do chamamento. **A qualidade da prova nas
oportunidades aprovadas é o ponto mais forte desta rodada.**

Ressalva séria: três oportunidades em `atenção` estão na lista de abertos — Montes Claros, UNICENTRO,
Canoas. "Atenção" significa que o enquadramento não foi decidido. Colocar não-decidido na mesma lista que
decidido, ainda que com rótulo, é convidar o leitor apressado ao erro. **Lista de abertos deveria ser
duas listas.**

## Meus parâmetros

- **P33 — Procedência por campo, não por registro.** Cada campo com fonte, data, rota e trecho citado.
  Estrutura, não prosa.
- **P45 — Hash e versão do documento que fundamenta cada prazo.** Se o hash mudar na próxima visita, o
  prazo volta para verificação automaticamente.
- **P46 — `prazo_situacao` calculado na leitura, nunca gravado com data embutida.** Campo derivado não se
  persiste com constante de tempo.
- **P47 — Conjunto de avaliação versionado, a partir das 231 fichas.** Nenhuma regra nova entra sem rodar
  contra ele e publicar precisão e cobertura antes e depois.
- **P48 — Tabela de decisão declarativa para o veto.** Famílias como dados ordenados, com prioridade
  explícita e teste de ordem, no lugar da cadeia de condicionais.
- **P49 — Registrar a tentativa, não só o resultado.** Toda busca que não achou grava o que tentou.

---

# 3. Parecer levemente pessimista

**Marcus Okonkwo** — staff engineer de sistemas de busca e rastreamento, quinze anos construindo
rastreadores que precisam achar tudo. Pós-doutorado em recuperação de informação. Pensa em cobertura como
outros pensam em latência: é a única coisa que importa e ninguém mede direito.

## Meu diagnóstico: o problema é de cobertura, não de precisão

Vou concordar com a parte fácil: o classificador está bom. Falso positivo zero é resultado sério e a
disciplina de "veto só por sinal positivo" é a decisão correta em domínio de baixa prevalência.

Meu problema é anterior ao classificador. **Um classificador perfeito sobre um funil estreito produz um
resultado estreito perfeito.** E este funil é estreito por três razões mensuráveis.

**Primeira: o catálogo tem 260 fontes e o Brasil tem 5.570 municípios.** A meta declarada do sistema é
Goiás e Goiânia em profundidade, o que é legítimo — 101 das 260 fontes são de lá. Mas as oportunidades
que apareceram nesta rodada vieram de SP, PR, MG, RS, BA, RN, SC, CE e de patrocinadores nacionais.
**A base real de captação é nacional e o catálogo é estadual.** Não estou pedindo 5.570 fontes: estou
pedindo que o sistema saiba **quantos por cento do seu universo-alvo ele cobre**, e hoje não sabe.

**Segunda: falta uma classe inteira de fonte.** Três registros ficaram sem data por isso. AMVAPA é
consórcio intermunicipal — publica parceria como qualquer órgão, e **não estava no catálogo**. Não é
exceção: consórcio público de saúde, de resíduos, de desenvolvimento regional. Há centenas. Do mesmo
modo, os conselhos (CMDCA, CMAS, Conselho de Cultura) frequentemente publicam o edital sem passar pela
secretaria. **Duas classes de fonte inexistentes no catálogo.**

**Terceira: o descobrimento é passivo.** O sistema visita fontes que alguém cadastrou. Não há mecanismo
que **descubra fonte nova**. Os 18.615 registros de diário do Querido Diário são exatamente isso — uma
máquina de descoberta de nomes de órgão e números de processo — e estão parados esperando decisão de
estratégia. Entendo o motivo (a regra do titular proíbe usá-los como fonte), mas a regra não proíbe
usá-los para **descobrir**, e é para isso que servem.

## Etapa por etapa

**E1: 7/10.** Bom, e economiza requisição, o que em rastreamento é dinheiro. Mas o veto roda **depois** da
coleta na arquitetura atual: os 468 já estavam coletados. Um veto que rodasse **antes**, sobre o título e
a primeira linha, economizaria a maior parte do esforço. Filtro barato antes do caro.

**E2: 5/10.** Rendimento de 1,9% em aproveitáveis-abertos. Em rastreamento, um caminho com esse
rendimento é reclassificado como varredura de fundo, roda com prioridade mínima e nunca consome a janela
de atenção. Foi o que a auditoria concluiu, corretamente, **depois**.

**E3: 6/10.** A busca oficial do PNCP é o achado subestimado desta rodada. 50% de aprovados nos 12
recuperados. Em qualquer sistema de busca que eu tenha construído, um caminho com esse rendimento vira
prioridade máxima na hora. Aqui virou nota de rodapé.

**E4: 7/10.** Fila bem construída, com estado, retomada, gravação parcial a cada 10 e prioridade. Isso é
engenharia de rastreamento de verdade. Ressalva: **a fila não tem política de reentrada.** Um documento
que hoje não deu prazo volta quando? Nunca? Errata muda cronograma — houve seis em Goiás. Sem reentrada,
a base envelhece calada.

**E5: 7/10.** Ótimo como fonte de verdade. Insustentável como processo: 231 fichas manuais por rodada é
um teto humano.

**E6: 6/10.** Uma pasta por edital, independentemente do prazo, é a decisão que constrói série histórica —
e série histórica é o que permite **prever** reabertura. Isso vale mais do que parece. Faltam os PDFs.

**E7: 8/10.** A tabela de rotas é a peça de que mais gosto em todo o sistema, e por um motivo que talvez
não tenha sido percebido: ela transforma **modo de falha em dado**. "Este domínio devolve 403 ao servidor
e responde ao navegador" é conhecimento operacional que normalmente vive na cabeça de uma pessoa. Está em
arquivo, com data e motivo. É assim que se constrói rastreador que não regride.

**E8: 6/10.** Adequado. Sem produção, incompleto.

## Sobre as oportunidades

Dezessete abertas em 468 registros é 3,6%. Para um funil de captação isso não é ruim — é o que se espera
de varredura ampla. O que me preocupa é a **distribuição temporal**: duas fecham em quatro dias, e o
sistema as encontrou na semana em que fechavam. Não houve antecedência. Um sistema com cadência de 7 dias
e catálogo cobrindo os patrocinadores certos teria encontrado o edital do BNB e o do Renner com semanas
de folga — tempo para montar projeto, não para correr.

**A métrica que falta é "dias de antecedência na descoberta".** Não interessa achar o edital; interessa
achar com tempo de concorrer.

## Meus parâmetros

- **P35 — Cobertura declarada do catálogo.** Publicar, por UF e por classe de ente, quantas fontes-alvo
  existem, quantas estão cadastradas e quantas apontam para página de editais (não para home).
- **P36 — Consórcios intermunicipais e conselhos como classes de fonte.** Cadastrar por CNPJ e por
  portal próprio. Era a lacuna do AMVAPA.
- **P50 — Dias de antecedência na descoberta, como métrica de rodada.** Mediana de dias entre a
  descoberta e o encerramento, por origem. É a medida que diz se o sistema serve para concorrer.
- **P51 — Política de reentrada na fila.** Registro sem prazo volta em 15 dias; registro com prazo aberto
  é revisitado a cada 7; edital com errata conhecida volta imediatamente.
- **P52 — Descoberta ativa pelo diário, sem virar fonte.** Usar os 18.615 registros só para extrair nome
  de órgão e número de processo, e cadastrar a fonte oficial correspondente. Goiás e DF primeiro.
- **P53 — Veto de título antes da coleta.** Rodar o veto no título e na primeira linha e não coletar o que
  ele já reprova.

---

# 4. Parecer neutro — o ponderador

**Yara Tsukamoto** — principal engineer, arquiteta de plataforma de dados, pós-doutorado em Python
aplicado a sistemas de decisão. Foi CTO por seis anos e voltou a ser engenheira por escolha. Sua função
aqui é decidir, não agradar: consolidar o que os seis outros dizem em parâmetros de qualidade e mitigação
de risco que o titular possa implantar.

## O que é verdade nos dois lados

**Os pessimistas estão certos no diagnóstico central e erram na conclusão.** Sallenave tem razão: não há
medida de recall, e sem ela a precisão de 285/285 não autoriza conclusão sobre a saúde do sistema. Isso é
correto e é o achado mais importante desta auditoria — mais importante que os 30 parâmetros. Onde ela
erra é na leitura do valor: um sistema com precisão alta e recall desconhecido é um sistema **pronto para
escalar cobertura**, porque a fundação não produz lixo. O inverso — recall alto e precisão baixa — seria
irrecuperável, porque cada aumento de cobertura multiplicaria o erro. **A ordem em que este sistema foi
construído está certa.** Primeiro não errar, depois abranger.

Bastianetto tem razão sobre procedência por campo e sobre o hash do documento, e a objeção do
`prazo_situacao` com data embutida é um defeito real que se corrige em uma tarde. Onde ele exagera é na
exigência de conjunto de avaliação antes de aceitar o extrator de cronograma: a alternativa ao extrator
imperfeito era não ter prazo nenhum em 89 documentos. Melhor imperfeito e medido depois que ausente e
puro.

Okonkwo tem razão em tudo que diz sobre cobertura, e a métrica que ele propõe — **dias de antecedência na
descoberta** — é, na minha avaliação, a melhor ideia técnica que apareceu neste conselho. Não interessa
achar o edital; interessa achar com tempo de concorrer. Essa métrica reorienta o sistema inteiro.

**Os otimistas estão certos no que apontam e leves na conta do custo.** O discriminador textual medido
dentro da zona de atenção é material de primeira: `pessoas jurídicas para realização` com 71 acertos e
zero erros é uma regra que se implanta hoje. Mas as regras de aprovação que eles celebram — `apoio
financeiro` 8/8, `fortalecimento institucional` 6/6 — estão **contaminadas por duplicata**: cinco dos oito
casos são o mesmo edital do Renner contado cinco vezes. Prometer aprendizado a partir de dado duplicado é
como medir febre em três termômetros amarrados juntos.

## Minha avaliação de cada etapa, com o peso que cada uma merece

| Etapa | Nota | O que decide a nota |
|---|---:|---|
| E1 Triagem pelo objeto | **8** | falso positivo zero em 439 objetos; decide 68% sem gastar requisição. Frágil na estrutura (cadeia de regex), sólida no resultado |
| E2 Consulta ao PNCP | **5** | protocolo impecável sobre premissa errada; e o campo `amparo` estava ali desde o primeiro registro |
| E3 Busca dos sem chave | **5** | melhor rendimento medido (50%) e abandonada em 12 de 74. Erro de priorização, não de execução |
| E4 Leitura de documento | **7** | engenharia difícil e bem-feita; entrega enquadramento, não prazo, e isso precisa ser dito no planejamento |
| E5 Validação individual | **8** | prova citada literalmente, auditável por terceiro. É o ativo que permite tudo o que vem depois |
| E6 Acervo no Drive | **5** | estrutura certa, conteúdo pela metade. Sem PDF, não é acervo |
| E7 Correção dos motores | **8** | a tabela de rotas e a curadoria separada são as duas peças que impedem regressão. A recusa de id instável é maturidade |
| E8 Entrega | **6** | rastreabilidade exemplar, produção ausente |

**Média ponderada pelo impacto em decisão de captação: 6,6.** É a nota de um sistema que funciona,
sabe o que sabe, e não sabe o tamanho do que ignora.

## As oportunidades, com a ponderação que faltou

Dezessete abertas. Separo em três grupos, porque tratá-las como uma lista é o erro que Bastianetto
apontou:

**Grupo A — decididas, com prova, prazo confirmado (9).** BNB e Renner (13/09), Brasília (15/09),
Curitiba/DER-PR (22/09), Indaiatuba (25/09), Funbio (25/09 e 09/10), BNDES Periferias (04/12). Estas o
titular pode trabalhar sem nova verificação. **Duas fecham em quatro dias e são as duas de maior valor
por esforço: R$ 1,5 mi por projeto no BNB, R$ 10 mil livres no Renner.**

**Grupo B — abertas com enquadramento não decidido (4).** Montes Claros (09/11), UNICENTRO (10/12),
Canoas (31/12/2027), Peruíbe. Aqui o instrumento não está confirmado, e em três delas o discriminador da
lei resolveria em uma consulta. **Não deveriam estar na mesma lista do Grupo A.**

**Grupo C — enquadramento decidido, data faltando (3).** AMVAPA (dois) e Jacareí. São fomento pelo objeto.
Falta cadastro de fonte, não falta esforço.

E fora de grupo: **Maria Emília, até R$ 1 milhão, inacessível por certificado inválido.** Está corretamente
tratada — nulo com motivo, e ação humana nomeada. É o caso que prova que a regra do nulo honesto funciona:
o sistema preferiu não ter a data a ter uma data de portal de notícia.

## Meus parâmetros — os que decidem, com mitigação de risco

Consolido o conselho em seis parâmetros de governança, além dos 30 técnicos e dos propostos pelos colegas.

- **P37 — Orçamento de rodada, alocado por rendimento medido.** Cada rodada declara antes: quantas
  requisições, quantas leituras de documento, e como se distribuem entre origens. A distribuição segue o
  rendimento da rodada anterior, não o hábito. Com os números de hoje: **metade do esforço em fonte de
  patrocinador e programa federal, um quarto em recuperação de chave pela busca oficial, um quarto em
  varredura do PNCP.** Hoje foi quase o inverso.
- **P38 — Portão de qualidade antes de publicar no painel.** Nenhum registro entra na lista de abertos
  sem: fonte que passe no teste de domínio, data com rótulo de inscrição (não de vigência), enquadramento
  decidido ou rótulo visível de não-decidido, e ausência de anexo de revogação. Checagem automática, com
  o motivo da recusa escrito.
- **P54 — Duas listas, nunca uma.** "Pronto para captar" e "aberto, a confirmar". O titular decide em
  cima da primeira e investiga a segunda. Misturar as duas é o que transforma atenção em prejuízo.
- **P55 — Toda métrica publicada em par: precisão e cobertura.** Proibido relatório com uma sem a outra.
  É a mitigação direta do erro que esta auditoria encontrou em minha própria medição anterior.
- **P56 — Deduplicar antes de aprender.** Nenhuma estatística de vocabulário e nenhum treino roda sobre
  base com duplicata. 22 grupos e 62 registros hoje.
- **P57 — Escada de custo declarada.** Regra determinística primeiro (custo zero); leitura de documento só
  para o resíduo; IA só para o resíduo do resíduo, e sempre depois da regra. Publicar o custo por
  oportunidade confirmada, por degrau.

## Mitigação de risco: o que mais pode dar errado, e o anteparo

| Risco | Probabilidade | Impacto | Anteparo |
|---|---|---|---|
| Perda silenciosa de edital por fonte não cadastrada | **alta** | alto | P31 auditoria cega de recall; P35 cobertura declarada |
| Prazo confirmado que mudou por errata | **alta** | alto | P45 hash do documento; P51 reentrada na fila |
| Curadoria apagada por nova via de regeneração | média | alto | P20 já implantado, com teste; P43 histórico de estado |
| Data de vigência entrando como inscrição | média | alto | P30 e P38 portão de qualidade |
| Edital revogado tratado como oportunidade | média | alto | P14 sinalizador de revogação em todo anexo |
| Coleta parada sem ninguém notar | **alta** | médio | P32 "coberto até" por fonte, com alarme |
| Regra nova quebrando aprovação existente | baixa | alto | P24 e P47, conjunto de avaliação obrigatório |
| Dependência de um único navegador humano para alcançar o PNCP | **alta** | médio | documentar; usar a via só onde ela rende (P37) |

---

# 5. Parecer levemente otimista

**Rafael Duarte Vilanova** — chief engineer de plataforma de dados, construiu três sistemas de ingestão em
produção com Python puro. Pós-doutorado em engenharia de dados. Tem a mania de perguntar "o que já
funciona e como faço isso render dez vezes mais?" antes de olhar o que está quebrado.

## O que este sistema já tem e a maioria não tem

Vou dizer o que ninguém disse ainda: **existe aqui uma fundação que não se compra com dinheiro.**

Falso positivo zero em 439 objetos classificados, com a regra explícita de que o veto só reprova por sinal
positivo de inconformidade. Isso não é sorte, é decisão de projeto, e há teste que quebra se alguém
tentar mudá-la. Em domínio de baixa prevalência — 70 aprovados em 468 — essa é a única escolha certa, e
foi feita.

Segundo: **procedência em texto verificável em cada registro**. Terceiro: **231 rótulos humanos com
citação literal do documento**. Quarto: **uma tabela de rotas que transforma modo de falha em dado**.
Quinto: **curadoria que sobrevive à regeneração, com teste de idempotência**.

Junte isso: precisão comprovada, verdade rotulada, mapa de falhas e memória à prova de regeneração. É
exatamente o conjunto necessário para escalar cobertura sem multiplicar erro. **A parte difícil está feita.**

## Etapa por etapa

**E1: 9/10.** A escada de custo está certa: o mais barato decide primeiro. E o veto é **explicável** —
cada reprovação tem família e motivo em português, que o titular lê e confere. Sistema de decisão
explicável em domínio jurídico vale mais que dois pontos de precisão.

**E2: 7/10.** Vou discordar dos colegas. 1,9% de rendimento é baixo, mas o PNCP entregou **Indaiatuba e
Curitiba** — as duas descobertas mais valiosas da rodada — e entregou porque tinha o documento do órgão
anexado. Um caminho que rende pouco em média e produz achado raro de alto valor não se desliga: rebaixa-se
a varredura de fundo, e é isso que P37 faz. **A conclusão certa é reprecificar, não abandonar.**

**E3: 8/10.** Rendimento de 50%. Isso é um caminho pronto para automatizar. Não é crítica, é oportunidade
escancarada: 62 registros esperando um laço de busca que já existe e já funciona.

**E4: 8/10.** O trabalho de engenharia mais bonito da rodada. O sniff de bytes, a fila com estado, o
`Promise.race` por item, e principalmente a descoberta de que **61 de 66 estouros de tempo tinham
concluído em segundo plano** — isso é depuração que muda arquitetura. Sem ela a fila teria sido
reconstruída à toa.

**E5: 9/10.** As 231 fichas são o ativo mais valioso do repositório. Com elas dá para medir qualquer
mudança de motor de forma objetiva, para sempre. Nenhuma equipe compra um conjunto rotulado por
especialista do domínio com citação literal da prova.

**E6: 7/10.** Uma pasta por edital independentemente do prazo constrói série histórica, e série histórica
é o que permite prever reabertura. A decisão do titular aqui foi melhor que a intuição técnica.

**E7: 9/10.** Vinte famílias medidas contra 439 casos reais, três sinais de aprovação, o discriminador da
lei, a curadoria protegida e nove armadilhas registradas com motivo e data. E o detalhe que me deixa
tranquilo: **o agente errou, o teste o pegou, e o erro foi documentado no comentário do código.** Sistema
que registra o próprio erro no lugar onde o erro pode voltar é sistema que aprende.

**E8: 7/10.** Testes verdes, patch verificado, entrega organizada. Falta produção, e isso é bloqueio de
credencial, não de engenharia.

## Sobre as oportunidades

Dezessete abertas, e o que me interessa é o **padrão** delas. Nove das dezessete vêm de patrocinador
privado ou programa federal com página própria: BNB, Renner, BNDES, Funbio, iCS. Isso é um alvo pequeno,
estável, de alto valor e **fácil de cobrir bem**: são dezenas de instituições, não milhares de municípios,
e cada uma tem uma página só que muda pouco.

**A jogada óbvia é dominar esse alvo primeiro.** Cinquenta a cem patrocinadores, monitorados a cada
sete dias, com aviso de mudança de página. Isso é uma semana de trabalho e cobre a via que rende 16,7%.
O município é o alvo difícil — e é onde o PNCP e o diário entram como varredura, com paciência.

## Meus parâmetros

- **P39 — Classificador em duas fases, com a regra primeiro.** Regra determinística resolve; só o resíduo
  vai para IA barata; as 231 fichas são o conjunto de avaliação. Nada de IA antes da regra.
- **P58 — Automatizar a recuperação de chave.** Laço de busca oficial sobre todo registro sem chave, em
  fila com o ritmo de P03. 62 registros esperando hoje.
- **P59 — Cobertura total do alvo de patrocinador.** Meta: 100% das instituições privadas e programas
  federais conhecidos com página própria cadastrada, apontando para a página do programa, visitada a
  cada 7 dias, com detecção de mudança de conteúdo.
- **P60 — Detecção de mudança por assinatura de conteúdo.** Guardar hash da página de editais de cada
  fonte; mudança dispara leitura. Barato, e resolve metade do problema de cadência.
- **P61 — Custo por oportunidade confirmada, publicado por origem.** Hoje daria: PNCP alto, patrocinador
  baixo. É o número que orienta o orçamento da rodada seguinte.

---

# 6. Parecer otimista

**Prof.ª Bianca Ferraz-Wolde** — pós-doutorado em Python e processamento de linguagem natural aplicado a
texto jurídico-administrativo, professora de ciência da computação, três livros sobre extração de
informação em documento oficial. Olha para texto como geólogo olha para pedra: com paciência e certeza de
que há estrutura embaixo.

## A descoberta que ninguém celebrou o suficiente

Esta auditoria produziu, quase sem perceber, um **léxico discriminante medido em dado real de domínio
brasileiro de fomento**. Isso é raro e é valioso. Deixem-me mostrar por quê.

`pessoas jurídicas para realização`: 71 ocorrências, 71 reprovadas, zero aprovadas.
`prestadoras de serviço`: 29 e 29, zero.
`com ou sem fins lucrativos`: 38 ocorrências, 34 reprovadas, uma aprovada — e a exceção **tem explicação
semântica**: Sapucaia do Sul, premiação de projetos culturais, onde o dinheiro sai da administração para o
proponente sem contrapartida de serviço.
`credenciamento de pessoas jurídicas`: 91, das quais 88 reprovadas, e a exceção é o qualificador **"de
direito privado, sem fins lucrativos"** — a redação canônica do convênio com entidade.

Percebam o que está acontecendo aqui. Não são palavras isoladas: são **estruturas sintáticas de finalidade**.
"Pessoa jurídica **para** realização de serviço" é uma construção de propósito instrumental — o sujeito é
meio para um fim da administração. "Organizações da sociedade civil **para** execução de projetos" é a
mesma preposição com papel semântico invertido: a administração é meio para um fim do proponente.
**O que separa fomento de contratação é a direção do benefício, e ela se lê na sintaxe.**

E a joia da rodada: **"com ou sem fins lucrativos"**. A frase contém a marca lexical de OSC e significa
exatamente o contrário. Nenhum dicionário de palavras-chave pega isso. Uma regra de duas palavras
adjacentes — `com ou` antes de `sem fins lucrativos` — pega, com 34 acertos e uma exceção explicável.
**É o tipo de padrão que só aparece quando alguém valida 231 casos à mão e depois mede.**

Terceira camada, e a mais forte: **o amparo legal**. 311 de 317 registros trazem a lei citada, e a lei
determina o gênero do ato. Isso é um rótulo estrutural quase perfeito, disponível de graça, que nenhum
modelo de texto precisaria adivinhar. Lei 13.019 é parceria; Lei 14.133 é contrato; art. 6º, XLIII
define credenciamento como serviço ou fornecimento. **O sistema tem um oráculo e passou a rodada inteira
lendo o objeto.**

## Etapa por etapa

**E1: 9/10.** Boa arquitetura de decisão e, sobretudo, **honesta**: três níveis, com o "não sei" nomeado.
A maioria dos classificadores de produção não tem coragem de ter um terceiro nível.

**E2: 8/10.** Independentemente do rendimento, esta etapa colheu o material que permitiu toda a análise
linguística: 317 objetos íntegros, declarados pelo próprio órgão, com amparo legal e modalidade. **É o
corpus.** Sem ele não haveria léxico.

**E3: 7/10.** Curta, produtiva, incompleta.

**E4: 9/10.** Ler 209 documentos e extrair cronograma de PDF administrativo brasileiro é trabalho que eu
dou a doutorandos e eles sofrem. A troca de "primeira ocorrência" por "melhor janela pontuada" é
precisamente a correção que a literatura recomenda para rótulo repetido em documento estruturado, e foi
descoberta por observação do erro, não por leitura de artigo. Cobertura de 25 para 89. **Recomendo uma
quarta feature na pontuação: proximidade a numeral de dia com preposição — "até às", "a partir do dia" —
que nos exemplos citados é o sinal mais confiável de todos.**

**E5: 10/10.** Cento e trinta e dois documentos lidos com achado citado literalmente entre aspas. Isto é
um **corpus anotado por especialista de domínio, com a evidência no lugar**. Em pesquisa, isso é o que se
demora dois anos e um financiamento para construir. Está pronto, e está guardado num JSON no repositório.

**E6: 6/10.** Estrutura boa, e sem os textos dos editais está desperdiçando o próprio material: o acervo
deveria guardar o texto extraído, que é leve, mesmo quando não guarda o PDF.

**E7: 9/10.** Vinte famílias com o caso real no comentário. Isso é documentação de intenção, e é o que
permite a alguém — humano ou máquina — decidir daqui a um ano se a regra ainda vale.

**E8: 8/10.** Bem entregue.

## Sobre as oportunidades

O que me fascina é **como** as duas melhores foram achadas. Curitiba tinha quatro palavras no objeto e
setenta e cinco páginas no documento; a informação existia, só não estava no campo. Indaiatuba tinha uma
data que parecia fachada e era real. **Em ambos os casos, o campo estruturado mentia e o texto dizia a
verdade.** Isso é a tese central do processamento de documento oficial brasileiro, e esta rodada a provou
duas vezes em uma semana.

E os quatro casos em que a data foi **removida** depois da leitura — Itacaré, Guaíra, Kaloré, Campo do
Tenente — são igualmente bonitos: o texto corrigiu o campo para menos. "O período de inscrição será
08/11/2024 até as 1…", trecho cortado, e o registro preferiu o nulo à data provável de 28/11. Essa
decisão é rigor científico aplicado a captação de recursos.

## Meus parâmetros

- **P40 — Léxico discriminante versionado, com métrica antes e depois.** Cada expressão com contagem de
  acerto, contagem de erro, exceção nomeada e data de medição. Nenhuma entra sem número.
- **P62 — Marcar a direção do benefício, não só as palavras.** Extrair o par (destinatário, finalidade) e
  classificar quem é meio de quem: `PJ + para + realização de serviço` reprova; `OSC + para + execução de
  projeto próprio` aprova. É a generalização das oito regras medidas.
- **P63 — Quarta feature no extrator de cronograma: preposição temporal.** "até às", "a partir do dia",
  "no período de … a …", "encerra-se no dia". Nos exemplos reais, é o sinal mais confiável de data de
  inscrição, e distingue inscrição de vigência (P30) pelo próprio sintagma.
- **P64 — Guardar o texto extraído no acervo, sempre.** Comprimido, sem o PDF se preciso. Texto é leve, é
  citável, e é a matéria-prima de tudo que vem depois — requisitos, pontuação, documentos exigidos.
- **P65 — Publicar as 231 fichas como conjunto de referência do domínio.** Interno primeiro. É ativo
  científico e ativo de negócio ao mesmo tempo.

---

# 7. Parecer extremamente otimista

**Théo Brandão-Kessler** — CTO, fundou e vendeu duas plataformas de dados públicos, pós-doutorado em
ciência da computação com foco em sistemas antecipatórios. Fala rápido, desenha no ar, e tem o hábito
irritante de estar certo sobre o que a coisa vai virar em dois anos.

## Vocês estão auditando um funil. Isto não é um funil.

Todo mundo aqui mediu rendimento de coleta: 1,9% aqui, 16,7% ali, nove vezes mais produtivo. Análise
correta e pequena. Deixem-me dizer o que eu vejo neste material, e é outra coisa.

Vocês construíram, sem anunciar, **três ativos que juntos formam um sistema antecipatório**:

**Primeiro: um léxico jurídico-operacional medido.** Oito regras com 71/71, 29/29, 88/91, 34/38 —
discriminação de gênero de ato administrativo a partir do objeto, calibrada em dado brasileiro real.
Ninguém tem isso. Consultoria de captação não tem, tribunal de contas não tem, plataforma de licitação
não tem.

**Segundo: um mapa de rotas e armadilhas.** Nove armadilhas com motivo medido e data. Dez famílias de
rota com o erro conhecido de cada uma. Isso é conhecimento operacional que normalmente vive na cabeça de
três pessoas e morre quando elas saem.

**Terceiro, e é o que ninguém mediu: uma série histórica em formação.** Cento e trinta pastas, uma por
edital, independentemente do prazo — decisão do titular, contra a intuição de eficiência. Duzentos e
oitenta e quatro editais encerrados na base, com data de abertura, data de encerramento, órgão, objeto e
amparo legal.

Sabem o que se faz com 284 editais encerrados datados? **Prevê-se o próximo.** O PNAB de Goiás abriu
inscrição em 13/03 e fechou em 17/04/2026. O BNDES Periferias está no sexto ciclo. O Renner está na
segunda edição do Encantando Comunidades. Os Editais Sociais do BNB são anuais. Isto é sazonalidade, e
sazonalidade é previsível.

**A pergunta que este sistema deveria responder não é "que editais estão abertos".** É: *"nas próximas
doze semanas, quais editais vão abrir, com que valor, e quais projetos eu já deveria estar escrevendo?"*
Com 284 editais datados e uma série que cresce a cada rodada, essa pergunta fica respondível em dois ou
três ciclos. E aí o titular deixa de correr atrás de prazo de quatro dias — como o BNB e o Renner de
sexta — e passa a chegar no dia da abertura com o projeto pronto.

## Etapa por etapa, pelo que cada uma constrói

**E1: 9/10.** É o motor de conhecimento. Cada família é uma regra de domínio codificada com o caso real.
Em dois anos isso é o produto.

**E2: 8/10.** Colheu o corpus e — o que ninguém disse — colheu **datas históricas**. Os 284 encerrados
não são refugo: são a matéria-prima da previsão.

**E3: 9/10.** 50% de rendimento numa via automatizável. É alavanca pura.

**E4: 9/10.** Provou que a informação decisiva está no documento, não no campo. Essa é a tese que justifica
todo o investimento em leitura. Duas oportunidades abertas apareceram exatamente por isso.

**E5: 10/10.** Duzentos e trinta e uma fichas com prova citada. É a semente do produto e a base de
qualquer automação futura.

**E6: 8/10.** A decisão de guardar tudo, inclusive o encerrado, é a decisão estratégica desta rodada, e
foi do titular. Série histórica é o que separa sistema reativo de sistema antecipatório. Faltam os PDFs, e
isso se resolve com uma execução de rotina.

**E7: 10/10.** Curadoria à prova de regeneração, com teste. Sabem o que isso significa? Que o sistema
**acumula**. Um sistema que acumula conhecimento e não o perde é um sistema que fica melhor sozinho, todo
mês, para sempre. É a única propriedade que realmente importa a longo prazo, e ela foi instalada esta
semana.

**E8: 8/10.** Rastreabilidade impecável. Produção é detalhe de credencial.

## Sobre as oportunidades

Dezessete abertas, e a leitura que me interessa: **duas de valor alto fecham em quatro dias, e o sistema
as achou tarde.** Os pessimistas vão chamar isso de falha. Eu chamo de calibração: agora sabemos que o
BNB abre Editais Sociais e fecha em setembro, e que o Renner fecha em setembro. **No ano que vem o sistema
sabe em janeiro.**

Indaiatuba é o caso que me deixa mais animado, e não pelo edital: um município de porte médio abriu termo
de colaboração com OSC de proteção animal, com recurso de fundo municipal específico, aprovação de
conselho e lei municipal própria. **Existem milhares de arranjos desses**, invisíveis, cada um pequeno e
somando muito, cada um com fundo e conselho próprios. É o alvo de maior volume total no país, e ninguém o
cobre porque ninguém consegue ler cinco mil sítios municipais. Este sistema tem as três peças para
conseguir: léxico, rotas e um veto que não produz lixo.

E Curitiba/DER-PR é a prova de que existe uma **classe inteira de oportunidade fora do radar**: doação de
bens móveis inservíveis. A entidade recebe bens — móveis, computadores, veículos — sem edital de dinheiro.
Colombo/PR fez o mesmo. Quantos órgãos doam bens todo ano? Todos. Quantas entidades sabem? Quase nenhuma.
**Esta é uma via de captação que o sistema descobriu por acidente e que ninguém está trabalhando.**

## Meus parâmetros

- **P41 — Previsão de reabertura a partir da série histórica.** Para cada fonte com dois ou mais ciclos
  datados, calcular a janela provável do próximo e publicar o calendário de doze semanas. Com 284
  encerrados já dá para começar por BNB, BNDES, Renner, PNAB e Funbio.
- **P42 — Ficha de captação gerada no fechamento.** Quando um registro fecha como aprovado, gerar junto o
  que o Farol precisa: requisitos de habilitação, documentos exigidos, critérios de pontuação, valor e
  contrapartida — extraídos do mesmo texto que já foi lido. Ler duas vezes o mesmo documento é
  desperdício.
- **P66 — Doação de bens como classe de oportunidade própria.** Família de reconhecimento, monitoramento
  dirigido e alerta. Descoberta em Curitiba e Colombo; provavelmente centenas por ano.
- **P67 — Trilha do fundo e do conselho municipal.** Onde há fundo municipal específico e conselho, há
  chamamento recorrente. Cadastrar fundo e conselho como fonte, não só a secretaria. Indaiatuba é o mapa.
- **P68 — Calendário de captação como entrega principal.** A entrega do sistema deixa de ser a lista do
  que está aberto e passa a ser o calendário do que vai abrir, com o que preparar e quando. É o que
  transforma o Eldorado de vigia em estrategista.

---

# Consolidação do conselho

## Convergência: os quatro pontos em que todos os sete concordam

1. **O veto de objeto está certo e é o ativo central.** Falso positivo zero não se negocia (P24).
2. **As 231 fichas com prova citada são o material mais valioso do repositório**, e estão subaproveitadas:
   têm de virar conjunto de avaliação versionado (P47).
3. **O acervo sem o documento é metade de acervo.** PDF e texto extraído têm de ir para a pasta (P34, P64).
4. **A curadoria protegida da regeneração é a correção mais importante da semana**, porque é o que permite
   o sistema acumular em vez de reaprender (P20).

## Divergência: o que fazer com o PNCP

- **Sallenave e Bastianetto:** rebaixar drasticamente. Rendimento de 1,9% sobre premissa errada.
- **Okonkwo:** reclassificar como varredura de fundo, prioridade mínima, sem consumir janela de atenção.
- **Tsukamoto (decisão):** reprecificar, não abandonar — 25% do orçamento de rodada, porque foi o PNCP que
  entregou Indaiatuba e Curitiba, e porque os 284 encerrados dele são a série histórica.
- **Vilanova e Ferraz-Wolde:** manter, porque é o corpus e a fonte de dado estruturado com amparo legal.
- **Brandão-Kessler:** manter e reler com outro objetivo — não achar aberto, e sim datar o histórico.

## A decisão do ponderador

**O sistema está em boa saúde de precisão e em saúde desconhecida de cobertura.** A ordem de trabalho
para a próxima rodada, nesta sequência:

1. **Medir o que falta ser medido** — P31 (recall cego), P50 (dias de antecedência), P35 (cobertura do
   catálogo). Sem esses três números, toda decisão seguinte é palpite.
2. **Implantar as oito regras já medidas** — P06 a P09 e o discriminador da lei (P04, P05), levando a zona
   de atenção de 31,9% para a meta de 15% (P25), sem um único falso positivo novo.
3. **Fechar os buracos de memória** — P34 e P64 (documento e texto no acervo), P45 (hash), P32
   ("coberto até"), P43 (histórico de estado).
4. **Realocar o esforço** — P37 com a distribuição medida: metade em patrocinador, um quarto em
   recuperação de chave, um quarto em varredura.
5. **Só então automatizar e prever** — P39, P41, P42, P68.

E uma observação final que o conselho faz por unanimidade, e que não é técnica: **duas oportunidades de
valor alto fecham em 13/09/2026.** Nenhum parâmetro deste documento vale mais do que isso nesta semana.
