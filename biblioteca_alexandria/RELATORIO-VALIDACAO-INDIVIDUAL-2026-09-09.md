# Validação individual de tudo que estava sem confirmação — 09/09/2026

O senhor pediu três coisas: um pacote único, a validação **individual** de cada informação suspeita ou
sem confirmação, e que as correções dos motores de busca viessem junto. Este relatório é o que foi feito
e o que sobrou — com o que sobrou nomeado, um por um.

## Onde a base está agora

| | Antes desta etapa | Agora |
|---|---:|---:|
| Registros na base | 468 | 468 |
| Com prazo confirmado em documento oficial | 337 | **339** |
| Validados individualmente e fechados | 0 | **123** |
| Ainda exigindo a leitura do documento do órgão | 231 | **108** |

O número que importa é o terceiro. Antes, 231 registros estavam "sem confirmação" e todos pareciam
igualmente pendentes. Agora 123 têm, cada um, a **rota usada** e o **achado escrito**, e estão fechados.
Os 108 restantes são um conjunto nomeado, não uma nuvem.

## Como cada registro foi fechado

Três rotas, e cada registro diz qual foi a sua.

**Rota 1 — o documento do próprio órgão.** O cronograma real não está na API do PNCP: a API devolve a
janela de proposta, que em credenciamento costuma ser um período de fachada de dez anos. O cronograma
está dentro do edital que o órgão anexou ao registro. Exemplo do que isso revela — Porangatu/GO,
edital 001/2026: inscrições de **05/02 a 05/03/2026**, e na lista de anexos um **TERMO DE REVOGAÇÃO**.
O edital foi revogado, e isso não aparece em nenhum campo da API. Sem abrir a lista de anexos, o sistema
guardaria como oportunidade um edital que não existe mais.

**Rota 2 — a página oficial do órgão ou do patrocinador.** Januária/MG, por exemplo: o edital 80/2024 é
credenciamento permanente, de **22/05/2024 a 22/05/2030**, situação "Em Andamento". Prazo agora
confirmado — e o objeto continua sendo prestação de serviço remunerada por procedimento, então não é
fomento. Prazo confirmado e veredito de não-oportunidade não se contradizem: um é fato, o outro é
enquadramento.

**Rota 3 — decidido pelo próprio objeto.** 21 registros estavam na fila só porque não tinham data. Mas
o objeto já dizia tudo: exploração publicitária de rotatórias, comercialização de bebidas em evento,
clínica para internação psiquiátrica, credenciamento de bancos comerciais, credenciamento de
pareceristas. **Nenhuma data mudaria o veredito.** Ficam na base como reprovados, com o motivo escrito,
e saem da fila de verificação. Isso não é atalho: é reconhecer que buscar o prazo de algo que não é
oportunidade é trabalho que não produz decisão.

## O achado da etapa: o PNAB de Goiás inteiro

Os **14 editais do PNAB 2026 da SECULT Goiás** — Bolsas Teia, Manutenção de Grupos, Manutenção de
Espaços, Infância e Juventude, Formação, Cultura e Social, Teatro, Dança, Circo, Literatura, Música,
Artesanato, Artes Visuais e Audiovisual — tiveram **inscrições de 13/03/2026 a 17/04/2026, todas
encerradas**.

Isso ficou confirmado em dois documentos oficiais: a retificação publicada no Diário Oficial de
**19/08/2026** (editais 12, 13 e 14: "Envio das inscrições 13/03/2026 17/04/2026") e a errata de
**01/09/2026** (editais 04 e 06, mesma janela de inscrição, com a avaliação de mérito prorrogada de
30/06 para 25/08/2026).

O detalhe que importa para o seu escritório: **houve seis retificações de cronograma**, e nenhuma delas
mexeu na inscrição — todas mexeram nas etapas seguintes. O estado hoje é de resultado:

- resultado preliminar em 08/09/2026;
- **prazo recursal de 09 a 11/09/2026** (editais 12, 13 e 14) e de 02 a 04/09 (edital 06);
- resposta aos recursos de 14 a 18/09/2026;
- **resultado final em 14/09/2026** (edital 06) e **21/09/2026** (editais 12, 13 e 14);
- habilitação para pagamento de 21 a 30/09/2026 e depósito de 26 a 30/10/2026.

Não há nada a inscrever no PNAB de Goiás. Há **prazo recursal correndo esta semana** para quem se
inscreveu, e a habilteração para pagamento no fim do mês.

## Correções nos motores de busca, implementadas

Vão no patch, aplicam com um comando, e têm 24 testes novos.

**1. O arquivo do edital do órgão, anexado ao PNCP, voltou a ser fonte.**
`src/fonte_edital.py` tinha uma decisão explícita de nunca baixar nada do PNCP, por entender que o
portal é só divulgação. Sua regra foi afinada em 08/09: o arquivo do **próprio órgão** hospedado lá é
documento oficial e vale, com a origem declarada. Recusar aquele endereço era recusar a fonte mais
produtiva que o sistema tem — **209 registros estão sem prazo por causa dessa recusa**. A função nova
marca cada anexo com `revogacao` e `errata`, porque essas duas palavras no título de um documento valem
mais que o objeto inteiro.

**2. Tabela de rotas de coleta** (`config/rotas_de_coleta.json` + `src/rotas_coleta.py`).
A lição das duas rodadas é que **a rota importa mais que o endereço**: o coletor conclui "não há edital"
quando o que houve foi rota errada. São dez famílias, cada uma com por onde se abre, se alcança da
nuvem, se exige o seu navegador, em que ritmo, qual o erro conhecido e — a mais importante — **o que
aquela família pode alimentar na base**. Portal de notícia e plataforma privada de licitação nunca viram
fonte de prazo, por mais convincente que a página pareça. A tabela substituiu uma lista de sete domínios
escrita à mão dentro do código.

**3. A armadilha eleitoral de Goiás.** Descobri hoje: `goias.gov.br` **suspendeu a divulgação de
notícias** durante o período de restrições eleitorais — a página responde só com o comunicado. As
páginas de **editais** continuam no ar e completas, e foi por elas que li os 14 editais do PNAB. Um
monitor que lê a seção de notícias conclui que não há nada publicado, e conclui errado. Em período
eleitoral, mirar as páginas de editais e chamamentos, nunca as notícias. Registrado no catálogo.

**4. Mais uma armadilha do PNAB:** as datas de inscrição **não estão no corpo do edital**. Estão nos
anexos de cronograma e nas erratas do Diário Oficial. Ler o edital e ignorar as erratas produz prazo
errado — e há seis retificações só nos editais 04 e 06. Alguns anexos de cronograma são PDF digitalizado
e exigem OCR.

## Os 108 que faltam, e por que não terminei agora

**Perdi a conexão com o seu computador** no meio da leitura dos documentos, e ela não voltou. Não é
escolha minha deixar para depois: o PNCP **não responde a requisição vinda de servidor** — testei as
duas rotas possíveis daqui e o gateway nega a conexão. Só o seu navegador alcança aquele endereço.

Os 108 são:

| Situação | Qtde | O que muda quando o documento for lido |
|---|---:|---|
| Atenção, prazo já encerrado | 93 | Decide se era fomento ou contratação, e completa o acervo histórico |
| **Atenção, ABERTO** | **7** | Pode virar caso de captação esta semana |
| Atenção, sem prazo | 4 | Confirma ou nega a existência de prazo |
| Pendência, sem prazo | 4 | Recupera o registro ou o descarta com motivo |

**Os 7 abertos, nomeados:** Indaiatuba/SP (parceria com OSC de proteção animal, fecha 25/09),
Brasília/DF (credenciamento de OSC no MEMP, fecha 15/09), Montes Claros/MG (acolhimento de idosos, fecha
09/11), Peruíbe/SP (ILPI, credenciamento longo), Curitiba/PR (resíduos sólidos, fecha 22/09),
Guarapuava/PR (coleta seletiva na UNICENTRO, fecha 10/12) e Canoas/RS (agremiações carnavalescas,
credenciamento até 2027).

### Como terminar sem depender de mim

No pacote vai o arquivo **`RETOMAR-VALIDACAO-EDITAIS.js`**. É o mesmo programa que eu estava rodando,
com os 209 editais já dentro dele. Basta:

1. abrir `https://pncp.gov.br` em uma aba e deixar aberta;
2. apertar **F12** e clicar em **Console**;
3. colar o arquivo inteiro e apertar Enter;
4. deixar rodando de 40 a 60 minutos (pode minimizar, **não feche a aba**).

Ele baixa sozinho `eldorado-validacao-editais.json` a cada dez editais lidos, e no fim. Me mande esse
arquivo e eu fecho os 108 em uma passada. O programa só **lê** documentos públicos e grava um arquivo no
seu computador: não envia nada, não clica em nada, não preenche formulário.

## Uma pendência que precisa de telefone, não de código

**Edital FME Transforma 02/2026 da Fundação Maria Emília** — até R$ 1 milhão para projetos em saúde e
educação, com indício de inscrições até 30/10/2026. Tentei quatro rotas: `fundacaomariaemilia.org.br`
tem certificado SSL inválido e não abre por nenhum caminho; `www.fundacaomariaemilia.org.br` e
`fmariaemilia.org.br` não resolvem em DNS; `fme.org.br` é de outra instituição. O único canal citado é
um formulário do Google, que não é domínio do patrocinador. **Não registrei a data**, porque a única
fonte é portal de notícia — e a sua regra é clara. Se o prazo se confirmar, é a maior oportunidade em
aberto da base.

## O que está no pacote

| Pasta | Conteúdo |
|---|---|
| `01-relatorios` | Este relatório, o da verificação dos 467, o de 08/09, e os CSV de abertos e de validação individual |
| `02-base-do-sistema` | A base completa dos 468 registros e a dos 210 da rodada anterior |
| `03-lotes-para-colar` | 32 lotes de 15 registros, prontos para colar |
| `04-codigo-e-motores` | Os patches de 08 e 09/09 e o `RETOMAR-VALIDACAO-EDITAIS.js` |
| `05-acervo-drive` | O banco do acervo e os 20 índices por UF |
| `06-validacao-documento-por-documento` | A ficha de cada um dos 231 registros: rota usada, achado e estado |

O patch aplica limpo na `main` de hoje (`62f9737c82`) e passa 71 testes nos módulos tocados. O `git push`
continua negado pelo proxy desta sessão, que autoriza por repositório — por isso a entrega é o patch.
