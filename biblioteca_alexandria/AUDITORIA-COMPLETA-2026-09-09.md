# Auditoria dos motores de busca do Eldorado — 09/09/2026

Auditoria das duas rodadas de verificação (08 e 09/09/2026) sobre **468 registros** e **231 validações
individuais**, feita para extrair aprendizado implantável. Nada aqui é impressão: cada afirmação traz a
medida que a originou, e cada parâmetro traz o teste que o comprova.

O documento tem cinco partes: o histórico do que foi feito; o que foi medido; onde o edital realmente se
publica; o que deu certo e o que falhou; e os 30 parâmetros que saem daqui prontos para implantação.

---

## Parte 1 — Histórico: o que foi feito, em ordem

### Rodada de 07 a 08/09/2026 — os 210 não verificados

Ponto de partida: 210 registros na base que não tinham as três informações mínimas (objeto, prazo de
inscrição, página oficial). O trabalho estabeleceu a regra que governa tudo desde então, e que veio do
titular: **a fonte é o site oficial do órgão público ou do patrocinador.** PNCP, Querido Diário, Diário
Oficial, Observatório do Terceiro Setor, Captadores/ABCR e Bússola Social servem apenas para descobrir o
número do processo e o nome do órgão. Nunca para confirmar prazo.

Nessa rodada nasceram três coisas: o veto de objeto (`src/inconformidade.py`, 9 famílias), a descoberta
de que 18 editais do PNAB de Goiás não estavam entrando na base porque as fontes apontavam para o índice
da secretaria e não para a página dos editais, e a armadilha de `goias.gov.br/cultura/termos-de-fomento`
— lista de termos já celebrados por inexigibilidade, que nunca terá prazo de inscrição.

### Rodada de 09/09/2026 — os 467 sem verificação

Ponto de partida: 467 registros sem verificação nenhuma, divididos em 408 do PNCP e 59 de outras fontes.
Terminou em 468 registros na base (um registro foi desdobrado em dois). As etapas:

**Etapa 1 — triagem pelo objeto.** Todos os 468 passaram pelo veto de objeto antes de qualquer coleta.
Isso decidiu, sem gastar uma requisição, que centenas de registros não eram oportunidade.

**Etapa 2 — consulta à API oficial do PNCP.** 317 registros tinham a chave `cnpj/ano/sequencial` e foram
consultados um por um na API de consulta, que devolve objeto integral, datas de abertura e encerramento
de proposta, número da compra, processo, órgão, unidade, link do sistema de origem, situação e amparo
legal. A consulta só roda no navegador do titular: a nuvem desta sessão não alcança o PNCP — o proxy nega
a conexão com HTTP 403.

**Etapa 3 — busca oficial para os registros sem chave.** 74 registros não tinham chave. A busca oficial
do PNCP (`api/search` com `tipos_documento=edital`) devolveu a chave de **12** deles, que voltaram a ter
página oficial.

**Etapa 4 — leitura do documento do órgão.** 209 registros entraram na fila de leitura de documento.
Aqui foi corrigida uma decisão explícita do código, que se recusava a baixar qualquer coisa do PNCP: o
arquivo do **próprio órgão** hospedado lá é documento oficial e vale, com a origem declarada — regra
afinada pelo titular em 08/09. Os documentos foram lidos com pdf.js no navegador do titular, com detector
de injeção de prompt antes de qualquer extração.

**Etapa 5 — validação individual.** Os 231 registros sem confirmação foram validados um por um, cada um
com a rota usada e o achado escrito. 228 fechados, 3 com próximo passo nomeado.

**Etapa 6 — acervo no Google Drive.** 20 pastas de UF e 130 pastas de edital, uma por edital
independentemente do prazo, com dossiê dentro de cada uma, mais um índice por UF.

**Etapa 7 — correções de motor.** Tabela de rotas de coleta, 20 famílias de veto (eram 9), três sinais de
aprovação, o discriminador da lei, e a correção do defeito que apagava a curadoria de fontes.

---

## Parte 2 — O que foi medido

### 2.1 A base

| | |
|---|---:|
| Registros | 468 |
| Com data final confirmada | 339 |
| Sem prazo confirmado | 129 |
| Com prazo aberto | 55 |
| Abertos com objeto compatível ou a conferir | 17 |
| Sem página oficial | 93 |
| Validados individualmente | 231 |
| Fechados | 228 |
| Datas estimadas | **0** |

Veredito: 369 reprovados, 70 aprovados, 22 atenção, 4 ruído, 2 vetor, 1 pendência.

### 2.2 O desempenho do veto de objeto, medido contra a validação individual

Este é o número mais importante da auditoria. O veto foi rodado sobre os **439 registros que têm texto de
objeto**, e o resultado comparado com o que a validação individual concluiu, registro por registro:

| O motor disse | Validação: aprovado | Validação: reprovado | Validação: atenção | outros |
|---|---:|---:|---:|---:|
| **reprovado** (285) | 0 | **285** | 0 | 0 |
| **aprovado** (14) | **14** | 0 | 0 | 0 |
| **atenção** (140) | 56 | 59 | 22 | 3 |

- **Falso positivo: zero.** O motor nunca reprovou nada que a validação aprovou.
- **Falso negativo: zero.** O motor nunca aprovou nada que a validação reprovou.
- **Precisão do reprovado: 285/285. Precisão do aprovado: 14/14.**
- **Cobertura de decisão: 68,1%.** A zona de atenção é **31,9%** — 140 registros.

A leitura correta: **o motor não erra, ele decide pouco.** Toda a imprecisão do sistema está concentrada
na zona de atenção, e é lá que está todo o custo — cada registro em atenção exige leitura de documento.
Dentro dos 140, 59 eram contratação e 56 eram fomento: a informação para separá-los estava no texto, e o
motor não a usava.

### 2.3 O achado estrutural: a via do PNCP não carrega parceria

Dos **317 registros consultados no PNCP**:

- **311 declaram amparo na Lei 14.133/2021.** 6 declaram outro amparo. **Zero declaram a Lei 13.019/2014.**
- **313 são da modalidade "Credenciamento".** 3 Concurso, 1 Dispensa.
- 264 dos 317 foram reprovados.

Isso não é coincidência de amostra, é consequência da lei. A Lei 14.133/2021, no art. 6º, XLIII, define
credenciamento como *"processo administrativo de chamamento público em que a Administração Pública convoca
interessados em prestar serviços ou fornecer bens"*. Credenciamento, **por definição legal, é para quem
presta serviço ou fornece bem** — não é fomento. E a Lei 13.019/2014, no art. 26, manda o edital de
chamamento público de parceria ser divulgado *"em página do sítio oficial da administração pública na
internet, com antecedência mínima de trinta dias"* — não no PNCP.

**Consequência para os motores:** varrer o PNCP procurando fomento é pescar no lago errado. O PNCP é o
portal da contratação sob a Lei 14.133; a parceria com OSC sob a Lei 13.019 vive no site do próprio
órgão. O PNCP continua útil — foi ele que revelou Indaiatuba e Curitiba —, mas como varredura de fundo, e
não como via principal.

### 2.4 Rendimento por origem: onde a oportunidade realmente está

| Origem | Registros | Aprovados | Taxa | Aproveitáveis e abertos | Taxa |
|---|---:|---:|---:|---:|---:|
| PNCP relocalizado pela busca | 12 | 6 | **50,0%** | 1 | 8,3% |
| Outras fontes (patrocinador privado, programa federal) | 60 | 23 | **38,3%** | 10 | **16,7%** |
| PNCP consultado | 317 | 37 | 11,7% | 6 | 1,9% |
| PNCP sem chave | 74 | 4 | 5,4% | 0 | 0,0% |
| PNCP barrado no título | 5 | 0 | 0,0% | 0 | 0,0% |

**Por registro trabalhado, a fonte do patrocinador foi cerca de nove vezes mais produtiva que o PNCP**
(16,7% contra 1,9% de aproveitáveis-abertos). E a relocalização pela busca oficial do PNCP — 12 registros
— rendeu 50% de aprovados, o melhor de todos: recuperar chave perdida é o trabalho de maior retorno por
unidade de esforço em toda a operação.

Os aprovados, por domínio de origem: 43 em `pncp.gov.br`, 6 no `bndes.gov.br`, 5 no
`institutolojasrenner.org.br`, 3 em `climaesociedade.org`, 2 em `goias.gov.br`, e um cada em
`fundacaotidesetubal.org.br`, `banrisulcultural.com.br`, `movimentobemmaior.org.br`, `rededobem.org.br`,
`chamadas.funbio.org.br`, `impactarte.org.br` e `bnb.gov.br`.

### 2.5 As datas: o que a API entrega e o que ela esconde

Distribuição da janela entre abertura e encerramento de proposta, nos registros que têm as duas datas:

| Duração da janela | Registros | O que costuma ser |
|---|---:|---|
| 0 dias (mesma data) | 82 | assinatura de data de publicação, não janela |
| 1 a 30 dias | 93 | janela real de inscrição |
| 31 a 90 dias | 32 | janela real, edital de fomento com prazo folgado |
| 91 a 365 dias | 83 | credenciamento de fluxo contínuo dentro do exercício |
| 1 a 3 anos | 18 | vigência de credenciamento |
| **mais de 3 anos** | **21** | **fachada: 20 dos 21 são contratação** |

Há registro com encerramento declarado em **2099**. Dos 21 com janela superior a três anos, 20 foram
reprovados e 1 ficou em atenção — nenhum é oportunidade.

Sobre os **82 com janela de um dia**: apenas **1 está no futuro** (Indaiatuba/SP), e foi justamente o
único lido no documento — e nele a data era real, o prazo de entrega de envelope às 09h00 de 25/09/2026.
Os outros 81 já venceram. O risco, portanto, é **histórico e não atual** — mas volta inteiro na próxima
rodada se o parâmetro não entrar.

### 2.6 O que a leitura de documento produziu

132 dos 231 registros validados foram fechados pela leitura do documento do órgão:

| O que a leitura produziu | Registros |
|---|---:|
| Confirmou prazo ou objeto | 121 |
| Reprovou depois de ler | 110 |
| Terminou com data final confirmada | 12 |
| Aprovou depois de ler | 11 |
| Edital sem data final por natureza (fluxo contínuo) | 3 |
| **Revogação encontrada na lista de anexos** | **1** |

Duas observações desconfortáveis e verdadeiras. Primeira: **das 132 leituras, só 12 terminaram com data
final** — a leitura de documento é caríssima e entrega pouco *prazo*; o que ela entrega é
**enquadramento** (110 reprovações fundamentadas). Segunda: **1 revogação em 132** parece pouco, até
lembrar que era Porangatu/GO e que nenhum campo da API dizia isso. Uma revogação não vista custa uma
inscrição preparada para um edital que não existe.

### 2.7 O campo de link do sistema de origem é quase inútil

- Preenchido em **51 dos 317** registros (16%).
- Dos 51, **22 traziam apenas um espaço em branco**.
- Dos restantes, a maioria aponta para **plataforma privada de licitação**: `sai.io.org.br`,
  `app2.ammlicita.org.br`, `compras.m2atecnologia.com.br`, `www.sigep.com.br`, `app2.licitardigital.com.br`,
  `gestaopublica.saopatricio.bsit-br.com.br`.

Nenhuma dessas é fonte válida pela regra do titular. **86 dos 408 registros do PNCP tinham o link
capturado apontando para uma plataforma privada, sem a chave do PNCP no endereço** — foi o principal
motivo de registro sem página oficial.

### 2.8 Duplicatas

**22 grupos de objeto idêntico, envolvendo 62 registros.** Os maiores: 9 registros do Consórcio
Intermunicipal de Saúde Costa Oeste com o mesmo objeto, 5 do Instituto Lojas Renner (o mesmo edital
Encantando Comunidades), 4+4+3 de credenciamentos idênticos, 3 do BNDES Periferias, 3 do Instituto MOL.

Isso tem dois efeitos ruins: a estatística de rendimento fica torta, e o vocabulário aprendido decora um
edital repetido em vez de aprender um padrão. Boa parte das expressões que aparecem como "sinal de
aprovação" nesta rodada — *zona oeste*, *Cabreúva Itu*, *Porto Feliz Sorocaba* — são apenas o texto do
edital do Renner contado cinco vezes.

### 2.9 O vocabulário que separa fomento de contratação, dentro da zona de atenção

Medido nos 140 registros da zona de atenção (59 reprovados e 56 aprovados na validação):

**Marcas de contratação — aparecem nos reprovados e quase nunca nos aprovados:**

| Expressão | Reprovados | Aprovados |
|---|---:|---:|
| `credenciamento de pessoas jurídicas` | 12 | 0 |
| `pessoas jurídicas para realização` | 8 | 0 |
| `com ou sem fins lucrativos` | 7 | 0 |
| `chamamento público para credenciamento` | 7 | 0 |
| `fundo municipal de saúde` | 6 | 0 |
| `prestadoras` | 6 | 0 |
| `profissionais` / `especializados` | 6 / 7 | 0 / 0 |

**Marcas de fomento — aparecem nos aprovados e quase nunca nos reprovados:**

| Expressão | Aprovados | Reprovados |
|---|---:|---:|
| `organizações da sociedade civil` | 18 | 1 |
| `apoio financeiro` | 8 | 0 |
| `necessidades institucionais` / `fortalecendo sua atuação` | 6 | 0 |
| `fomento` | 7 | 0 |
| `seleção` | 9 | 0 |

E uma descoberta contra-intuitiva que vale registrar: **`chamamento público` não é sinal de fomento.**
Aparece 8 vezes nos reprovados e nenhuma nos aprovados desta zona, porque credenciamento também é
chamamento público. Do mesmo modo, **`Aldir Blanc` não aprova nada por si**: dos 9 objetos que citam a
lei, 3 são credenciamento de parecerista — serviço técnico sob a roupa do PNAB.

E a mais útil de todas: **`com ou sem fins lucrativos` é marca de contratação, não de OSC.** A frase
contém "sem fins lucrativos" e engana o leitor apressado — humano ou máquina. Quem escreve isso está
dizendo que admite empresa.

---

## Parte 3 — Onde o edital realmente se publica

Ver `MAPA-DE-PUBLICACAO-OFICIAL.md` para o mapa completo. O resumo dos parâmetros confirmados:

**Confirmado como fonte de prazo** (326 dos 339 prazos confirmados vieram de `.gov.br`):

1. **Página de editais/chamamentos do próprio órgão**, em `.gov.br`, `.leg.br`, `.jus.br` ou `.mp.br`.
   É o que a Lei 13.019/2014, art. 26, exige para parceria: sítio oficial, 30 dias de antecedência.
2. **Página do programa no site do patrocinador**, em `.org.br` ou `.com.br` do próprio instituto,
   fundação ou banco. Rendeu 9 dos 339 prazos e a maior parte das oportunidades aproveitáveis.
3. **Arquivo do edital anexado pelo próprio órgão ao registro do PNCP** — documento oficial do órgão,
   aceito com a origem declarada. Produziu 132 dos 231 fechamentos.
4. **Errata e retificação no Diário Oficial**, *quando referenciada pelo próprio órgão* — no PNAB de
   Goiás o cronograma real estava na errata, não no corpo do edital.

**Recusado como fonte de prazo, e registrado como armadilha** (9 armadilhas no catálogo):

- PNCP como portal (a página de divulgação, distinta do arquivo do órgão)
- Querido Diário, Diário Oficial agregado, portais de diário municipal terceirizados
- Observatório do Terceiro Setor — e há prova: **quatro textos de edital guardados no sistema eram o
  mídia kit desse site**, não o edital
- Captadores/ABCR — nesta rodada trazia duas chamadas do Funbio com data vencida em relação à página
  oficial, e um edital de Santa Luzia do Paruá/MA que não existe no portal do município
- Plataformas privadas de licitação (`portaldecompraspublicas`, `bllcompras`, `licitamaisbrasil`,
  `bnccompras`, `licitanet`, `licitardigital`, `sai.io.org.br`, `ammlicita`, `m2atecnologia`, `sigep`)
- `goias.gov.br/cultura/termos-de-fomento` — lista de termos já celebrados, sem fase de inscrição
- A **seção de notícias** de portal de órgão em período eleitoral

---

## Parte 4 — O que deu certo e o que falhou

### Deu certo, com número

| O que | Prova |
|---|---|
| Veto de objeto antes da coleta | decidiu 68,1% dos registros sem gastar requisição, com falso positivo zero |
| Ritmo de 2,5 s com recuo progressivo no PNCP | 317 consultas, zero HTTP 429 |
| Arquivo do órgão anexado ao PNCP como fonte | 132 dos 231 fechamentos |
| Extrator de cronograma por pontuação de janela | cobertura subiu de 25 para 89 de 209 documentos |
| Sniff de bytes antes do parser | recuperou ~30 documentos que falhavam por tipo |
| Fila dispara-e-consulta | 61 de 66 "estouros de tempo" tinham concluído em segundo plano |
| Validação individual com rota e achado escritos | 228 fechamentos auditáveis, um por um |
| Nulo honesto | 0 datas estimadas em 468 registros; 4 datas erradas removidas |
| Curadoria fora do arquivo gerado | sobrevive a três regenerações seguidas, com teste |

### Falhou, e o que a falha ensinou

**1. A curadoria era apagada em silêncio pela regeneração.** O catálogo em produção havia voltado a 260
fontes e **zero armadilhas**, e o motor voltou a procurar o BNDES Periferias na busca do Diário Oficial da
União. Perder curadoria é pior que não tê-la: o sistema volta a errar exatamente onde já havia aprendido,
e ninguém percebe porque o arquivo continua parecendo certo. **Corrigido nesta rodada.**

**2. O código recusava a fonte mais produtiva que tinha.** `src/fonte_edital.py` tinha uma decisão
explícita de nunca baixar nada do PNCP. Essa decisão deixou **209 registros sem prazo**. A lição não é
sobre o PNCP: é que **regra de fonte escrita dentro do código, sem data e sem medida, envelhece sem
aviso**. Agora o que decide se um endereço serve é uma tabela de dados, com o motivo e a data de
verificação em cada linha.

**3. O extrator pegava a primeira ocorrência.** Buscar "cronograma" e usar a primeira ocorrência achou
data em 25 de 209 documentos, porque a primeira ocorrência costuma ser modelo de declaração em anexo ou
cláusula de desembolso. **Em documento jurídico, a primeira ocorrência de um rótulo quase nunca é a
principal.**

**4. Um objeto de quatro palavras quase custou uma oportunidade aberta.** Curitiba/DER-PR estava marcado
como `objeto_insuficiente`. Era doação de bens móveis, aberta até 22/09/2026. **Campo curto é ausência de
informação, não informação de ausência.**

**5. Quatro textos de edital no repositório eram mídia kit de portal de notícia.** O extrator seguiu o
link da notícia e guardou a página institucional do veículo. Havia teste reclamando disso, e o teste
estava certo. **Descartados nesta rodada**, com a nota do descarte escrita em cada registro.

**6. Eu mesmo transformei ausência de vocabulário em veto duro, e o teste me impediu.**
`test_aprovados_nunca_sao_barrados` quebrou com a mensagem certa: *falso positivo é o erro caro — perde
oportunidade e não deixa rastro*. Virou atenção. **O teste que protege contra o erro invisível é o ativo
mais valioso do repositório.**

**7. Minha própria validação anterior foi de um lado só.** Eu havia declarado o motor "validado contra os
317 objetos reais" medindo apenas falso positivo. Esta auditoria mediu os dois lados — e o resultado
continuou bom (falso negativo também zero), mas **a medida anterior não autorizava a conclusão que eu
tirei dela**. Métrica de um lado só é métrica que engana quem a produz.

**8. Três registros ficaram sem data, e a razão é catálogo, não esforço.** AMVAPA (dois registros) e
Jacareí/SP: sem chave do PNCP, e os únicos links existentes são plataforma privada e sistema geosiap. O
consórcio intermunicipal **não estava no catálogo de fontes** — e consórcio publica parceria como
qualquer órgão. **A lacuna era de cadastro.**

### O que ainda pode ser analisado e não foi

| Dado disponível | O que renderia | Por que não foi feito |
|---|---|---|
| 18.615 registros de diário do Querido Diário | descoberta de nome de órgão e número de processo em massa, para depois buscar no site oficial | precisa de decisão de estratégia do titular; recomendação: Goiás e DF primeiro |
| Os 129 registros sem prazo confirmado | 93 já venceram e servem ao acervo histórico; 36 podem render prazo | exige leitura de documento, e o custo por prazo obtido é alto (12 prazos em 132 leituras) |
| Campo `pub` e `incl` do PNCP (data de publicação e de inclusão) | permitiria medir a antecedência real de cada edital e validar a cadência de 7 dias contra dado, não só contra a lei | não foi cruzado nesta rodada |
| Os 74 registros que ficaram sem chave | 12 foram recuperados pela busca oficial; os outros 62 não foram tentados um a um | a busca oficial exige o navegador do titular e a fila foi priorizada para os documentos |
| Texto integral dos 89 documentos com cronograma extraído | requisitos de habilitação, critérios de pontuação e documentos exigidos — matéria-prima do Farol de Alexandria | fora do escopo desta rodada, que era prazo e enquadramento |
| Histórico de 5 anos de cada fonte | previsão de quando cada edital reabre, o que transforma o sistema de reativo em antecipatório | precisa de série histórica que o acervo começou a formar agora |

---

## Parte 5 — Os 30 parâmetros

Estão em `../02-parametros/PARAMETROS-MOTORES-2026-09-09.json`, cada um com: onde implantar, a regra, a
medida que o originou, o valor, o teste de aceite, o risco se for ignorado e a prioridade.

**13 críticos, 12 de prioridade alta, 5 de prioridade média.**

Os cinco que mudam mais o sistema:

- **P04 e P05 — o amparo legal decide antes do texto.** 311 de 317 registros do PNCP citam a Lei
  14.133/2021 e nenhum cita a 13.019/2014. Credenciamento sob a 14.133 é, por definição legal,
  contratação. Isso reordena a fila de prioridade de coleta inteira.
- **P21 — cadência de 7 dias, derivada do art. 26 da Lei 13.019/2014.** O edital de parceria tem de ser
  divulgado com 30 dias de antecedência. Visita semanal dá quatro chances de ver cada edital válido. É a
  única garantia real contra a perda silenciosa.
- **P25 — a zona de atenção é orçamento, com meta.** Hoje 31,9%; meta 15%, sem introduzir um único falso
  positivo. Os 59 registros de contratação que hoje ficam na zona são o material de treino, e P06 a P09
  são as regras medidas que os retiram.
- **P26 — o rendimento por origem orienta o investimento.** A fonte do patrocinador é nove vezes mais
  produtiva que o PNCP por registro trabalhado. O catálogo tem de crescer para esse lado.
- **P24 — falso positivo é o erro caro.** Nenhuma regra nova entra sem que
  `test_aprovados_nunca_sao_barrados` continue verde. É o que separa evolução de regressão.
