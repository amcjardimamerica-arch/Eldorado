# Validação individual concluída — 09/09/2026

O senhor pediu três coisas: um pacote único, a validação **individual** de cada informação suspeita ou
sem confirmação, e que as correções dos motores de busca viessem junto. Está feito. Dos 231 registros
que estavam sem confirmação, **228 estão fechados** com a rota usada e o achado escrito, e **3** ficaram
com o próximo passo nomeado — não por falta de trabalho, mas porque a informação não existe em fonte que
a sua regra aceite.

## Onde a base está agora

| | Antes desta etapa | Agora |
|---|---:|---:|
| Registros na base | 468 | 468 |
| Sem confirmação, todos parecendo igualmente pendentes | 231 | **0** |
| Validados individualmente | 0 | **231** |
| Fechados, com rota e achado escritos | 0 | **228** |
| Com próximo passo nomeado | — | **3** |
| Datas inventadas ou estimadas | 0 | **0** |

Dos 231, **191 tiveram objeto ou prazo confirmado em documento oficial**. As rotas:

| Rota | Registros |
|---|---:|
| Documento do próprio órgão, anexado ao registro do PNCP, lido por pdf.js no seu navegador | 132 |
| Objeto integral declarado pelo órgão na API oficial de consulta, lido registro por registro | 91 |
| Página oficial do órgão ou do patrocinador | 7 |
| Quatro rotas tentadas, todas fechadas (Fundação Maria Emília) | 1 |

## O que fecha nos próximos dias

| Prazo | Oportunidade | Onde |
|---|---|---|
| **13/09/2026** | Editais Sociais 2026 do Banco do Nordeste — até R$ 1,5 mi por projeto, por incentivo fiscal | bnb.gov.br |
| **13/09/2026** | Instituto Lojas Renner, Encantando Comunidades — R$ 10 mil livres, até 30 organizações | institutolojasrenner.org.br |
| **15/09/2026** | Brasília/DF — credenciamento de OSC na Secretaria da Micro e Pequena Empresa | PNCP 18299670000116/2026/59 |
| **22/09/2026** | **Curitiba/PR — DER-PR, chamamento público para DOAÇÃO DE BENS MÓVEIS inservíveis** | PNCP 76669324000189/2026/128 |
| **25/09/2026** | **Indaiatuba/SP — termo de colaboração com OSC de proteção animal, Fundo Municipal** | PNCP 44733608000109/2026/765 |
| **25/09 e 09/10** | Funbio — chamadas 07/2026 e 08/2026, Biodiversidade Litoral e plano de manejo de RPPN | chamadas.funbio.org.br |
| **09/11/2026** | Montes Claros/MG — acolhimento, aberto até 09/11/2026 (a conferir o instrumento) | PNCP 22678874000135/2024/589 |
| **04/12/2026** | BNDES Periferias em Rede, 6º ciclo | bndes.gov.br/periferias |
| 10/12/2026 | Guarapuava/PR — UNICENTRO, coleta seletiva (a conferir) | PNCP 77902914000172/2026/1 |

**Dois desses eram desconhecidos ou estavam lidos errado até hoje**, e só apareceram porque o documento
do órgão foi lido:

**Indaiatuba/SP.** A API devolvia 25/09/2026 como abertura *e* encerramento da proposta — o padrão de
data de fachada, que eu já tinha aprendido a desconfiar. Fui ao edital de 53 páginas: *"DO OBJETO DO
TERMO DE COLABORAÇÃO — constitui objeto do presente chamamento público a seleção de Organizações da
Sociedade Civil (OSCs) de proteção animal, sem fins lucrativos"*, na Lei 13.019/2014, e
*"Local e Data da Entrega dos Envelopes: Departamento de Protocolo, até às 09:00 horas do dia
25/09/2026"*. Neste caso a data da API **era** o prazo real. Fomento inequívoco, instrumento nomeado,
fonte de recurso nomeada (Fundo Municipal de Proteção aos Animais), conselho nomeado (COMPDA), e
destinatário exclusivo OSC.

**Curitiba/DER-PR.** O objeto no PNCP tinha três palavras e o sistema tinha classificado como
`objeto_insuficiente` — quase ruído. O edital de 75 páginas diz: *"1. OBJETO 1.1 CHAMAMENTO PÚBLICO PARA
DOAÇÃO DE BENS MÓVEIS INSERVÍVEIS E/OU DESNECESSÁRIOS"*. É a mesma modalidade de Colombo/PR: **a
entidade recebe bens**, não presta serviço. Passou de `atenção / objeto insuficiente` para **aprovado, e
aberto até 22/09/2026**. É o exemplo mais claro de por que ler o documento não é luxo: um objeto de três
palavras esconderia uma oportunidade com prazo correndo.

## O PNAB de Goiás está inteiro encerrado

Os **14 editais do PNAB 2026 da SECULT Goiás** tiveram **inscrições de 13/03/2026 a 17/04/2026, todas
encerradas** — confirmado na retificação do Diário Oficial de 19/08/2026 (editais 12, 13 e 14: "Envio
das inscrições 13/03/2026 17/04/2026") e na errata de 01/09/2026 (editais 04 e 06). Houve **seis
retificações de cronograma e nenhuma mexeu na inscrição**: todas mexeram nas etapas seguintes.

O estado hoje é de resultado: preliminar em 08/09, **prazo recursal de 09 a 11/09/2026**, resposta aos
recursos de 14 a 18/09, resultado final em 14/09 (edital 06) e 21/09/2026 (editais 12, 13 e 14),
habilitação para pagamento de 21 a 30/09 e depósito de 26 a 30/10/2026. **Não há nada a inscrever. Há
prazo recursal correndo esta semana** para quem se inscreveu.

## O que o documento revelou e nenhum campo de API carregava

**Porangatu/GO.** Cronograma no Anexo IV: inscrições de 05/02 a 05/03/2026. E na lista de anexos do
próprio registro, um **TERMO DE REVOGAÇÃO** — o edital foi revogado, e isso não aparece em nenhum campo
da API. Sem abrir a lista de anexos, o sistema guardaria como oportunidade um edital que não existe mais.

**Goiandira/GO.** Prazo aberto até 31/12/2026 — parecia a melhor pendência de Goiás. O objeto é
*"concessão de INCENTIVO PATRIMONIAL consistente na alienação, por DOAÇÃO COM ENCARGOS, do bem imóvel
público"*: é atração de empresa para o distrito industrial. Reprovado. Fica no acervo de Goiás como a
lição de que **prazo aberto não significa oportunidade**.

**Nísia Floresta/RN.** *"ENTREGA DOS ENVELOPES: DATA: De 06 de junho a 28 de junho de 2024"* — prazo
confirmado e encerrado. O nome do arquivo anexado ("EDITAL CREDENCIAMENTO 01-2024 - OS") aponta
Organização Social e contrato de gestão, o que muda o enquadramento e ficou registrado.

**Um termo de colaboração que não tem inscrição.** *"termo de colaboração DECORRENTE DA INEXIGIBILIDADE
DE CHAMAMENTO PÚBLICO nº 002/2026"* — é o ato final de uma dispensa, com entidade já definida. A data de
31/05/2027 que o registro trazia é **vigência da parceria, não prazo de inscrição**. Reprovado como
parceria já celebrada. Confundir vigência com inscrição é o erro que mais produz falsa oportunidade.

**Navegantes/SC.** Edital de 60 páginas: *"CREDENCIAMENTO VISANDO A CONTRATAÇÃO DE ENTIDADES PRIVADAS,
SEM FINS LUCRATIVOS, OSCIPS E/OU PESSOAS JURÍDICAS PRIVADAS COM FINS LUCRATIVOS"*. A palavra
**contratação** está no objeto e não há instrumento de parceria em lugar nenhum: é compra de vaga de
internação, remunerada por paciente. Os dois campos de data ficam nulos — agora **com o motivo lido no
próprio edital** (fluxo contínuo, sem cronograma), não por falta de verificação. Essa diferença é a
única que interessa numa base que alimenta decisão.

## Onde o nulo foi mantido de propósito

Quatro registros tinham data na API e **perderam a data** depois da leitura do documento. Não é perda: é
correção.

- **Itacaré/BA** — o documento diz *"o período de inscrição será 08/11/2024 até as 1…"* e o trecho
  extraído termina cortado. Registrei o início confirmado e **deixei o fim nulo**, embora a próxima data
  do mesmo bloco seja 28/11/2024. Prefiro o nulo honesto à data provável.
- **Guaíra/PR** — *"o prazo será DURANTE A SUA VIGÊNCIA, a partir do dia 06 de agosto de 2024"*. Não há
  data final no edital: é credenciamento aberto durante a vigência.
- **Kaloré/PR** — o edital fixa a sessão em 20/05/2024 e **não fixa início** (inexigibilidade).
- **Campo do Tenente/PR** — *"poderá A QUALQUER TEMPO novos interessados ingressarem"*.

A regra que o senhor deu vale nos dois sentidos: não inventar data, e não apagar data confirmada por
descuido. As duas coisas foram conferidas registro por registro antes de gravar.

## Correções nos motores de busca, implementadas

Vão no patch, aplicam com um comando, e têm testes novos.

**1. O arquivo do edital do órgão, anexado ao PNCP, voltou a ser fonte.** `src/fonte_edital.py` tinha uma
decisão explícita de nunca baixar nada do PNCP. Sua regra foi afinada em 08/09: o arquivo do **próprio
órgão** hospedado lá é documento oficial e vale, com a origem declarada. A função nova marca cada anexo
com `revogacao` e `errata`, porque essas duas palavras no título valem mais que o objeto inteiro. Foi
essa correção que produziu 132 dos 231 fechamentos.

**2. Tabela de rotas de coleta** (`config/rotas_de_coleta.json` + `src/rotas_coleta.py`). A rota importa
mais que o endereço: o coletor conclui "não há edital" quando o que houve foi rota errada. São dez
famílias, cada uma com por onde se abre, se alcança da nuvem, se exige o seu navegador, em que ritmo,
qual o erro conhecido e o que aquela família pode alimentar na base. Portal de notícia e plataforma
privada de licitação nunca viram fonte de prazo.

**3. A armadilha eleitoral de Goiás.** `goias.gov.br` **suspendeu a divulgação de notícias** durante as
restrições eleitorais — a página responde só com o comunicado. As páginas de **editais** continuam no ar
e completas, e foi por elas que li os 14 editais do PNAB. Um monitor que lê a seção de notícias conclui
que não há nada publicado, e conclui errado.

**4. Vinte famílias novas de inconformidade e três sinais de aprovação.** O veto de objeto passou de 9
para 20 famílias, entre elas `servico_ao_orgao` (128 casos reais), `convenio_desconto`,
`cadastro_fornecedor`, `contrapartida_sem_repasse` e `compra_de_vaga`. Do outro lado, três sinais que
**aprovam**: `doacao_de_bens` (foi o que salvou Curitiba), `coleta_solidaria` e `plano_de_trabalho`.

**5. O discriminador da lei.** Em acolhimento, a lei citada decide: **Lei 13.019/2014 é parceria**
(fomento); **Lei 14.133/2021 é compra de vaga**. O mesmo objeto, com a mesma redação, muda de veredito
pela lei que invoca — e nenhuma outra pista no texto é tão confiável.

**6. Duas correções nascidas de erro meu, e vale registrar.** Eu havia transformado "objeto sem marca de
fomento" em veto duro; o teste `test_aprovados_nunca_sao_barrados` reprovou, e com razão: **falso
positivo é o erro caro — perde oportunidade e não deixa rastro**. Virou atenção. Depois, ao acertar o
singular "organização da sociedade civil" no reconhecedor, criei um falso positivo em Cocalzinho/GO, que
é o *resultado* de um edital de 2021; corrigi com um padrão específico. Os motores foram conferidos
contra os 317 objetos reais e não reprovam nada que a validação individual aprovou.

## Os 3 que ficaram, e o que fazer com eles

| Registro | Enquadramento | Próximo passo |
|---|---|---|
| AMVAPA — Piraju/SP (dois registros) | Fomento pelo objeto | Cadastrar o Consórcio AMVAPA como fonte e buscar as duas parcerias no portal do consórcio, ou pelo CNPJ do AMVAPA na consulta do PNCP |
| Jacareí/SP | Fomento pelo objeto | Contato com a Secretaria de Meio Ambiente (SMAZU) ou busca no PNCP pelo CNPJ do município |

Nos três, o enquadramento está decidido — é fomento — e só a **data** falta. Não há chave do PNCP para
eles, e os links que existem são de plataforma privada de licitação e de sistema geosiap, que pela sua
regra não são fonte. Registrei o passo em vez de registrar uma data plausível.

## Uma pendência que precisa de telefone, não de código

**Edital FME Transforma 02/2026 da Fundação Maria Emília** — até R$ 1 milhão em saúde e educação, com
indício de inscrições até 30/10/2026. Quatro rotas tentadas: `fundacaomariaemilia.org.br` tem
certificado SSL inválido e não abre por nenhum caminho; `www.fundacaomariaemilia.org.br` e
`fmariaemilia.org.br` não resolvem em DNS; `fme.org.br` é de outra instituição. **Não registrei a
data**, porque a única fonte é portal de notícia. Se o prazo se confirmar, é a maior oportunidade em
aberto da base.

## A curadoria que estava sendo apagada: corrigido

Eu havia deixado isto como decisão sua. Não é decisão sua — é defeito, e resolvi.

`src/fontes260.py` reconstrói `config/fontes_captacao_260.json` inteiro a cada regeneração de dados, a
partir das rotas de monitoramento. Toda correção de endereço feita à mão, toda fonte nova confirmada e
toda armadilha registrada moravam nesse mesmo arquivo — e sumiam na regeneração seguinte, sem aviso.
Hoje o catálogo em produção tinha voltado a 260 fontes e **zero** armadilhas, e o motor voltou a procurar
o BNDES Periferias na busca do Diário Oficial da União, onde a chamada não está. **Perder curadoria é
pior que não tê-la**: o sistema volta a errar exatamente onde já havia aprendido, e ninguém percebe,
porque o arquivo continua parecendo certo.

A curadoria passou a morar em `config/curadoria_fontes.json`, que a regeneração **nunca escreve**, e é
reaplicada no fim de cada regeneração. São 7 regras de endereço, 9 fontes novas e 9 armadilhas.
Regenerei três vezes seguidas: o catálogo continua com 269 fontes, 9 armadilhas, e o BNDES Periferias
continua no topo da sua fonte. Há teste guardando cada uma dessas coisas.

Os dois scripts de aprimoramento passaram a gravar na curadoria e a regenerar o catálogo em seguida, em
vez de escrever no arquivo gerado — quem rodar qualquer um deles no futuro não reintroduz o problema.

## Quatro textos de edital que não eram edital

Um teste do sistema reclamava que havia mídia kit guardado no repositório, e estava certo. O texto
guardado para quatro registros — dois do Prêmio MOL, um do Instituto Lojas Renner e um do Impactarte —
não era o edital: era o **mídia kit do Observatório do Terceiro Setor**. O extrator seguiu o link da
notícia e guardou a página institucional do veículo, antes de o veto de veículo existir.

Os quatro arquivos saíram. Os **itens** desses registros vieram da página oficial do patrocinador e
continuam válidos — o que saiu foi o texto de apoio, que não sustentava nada. Cada registro ficou com a
nota do descarte escrita, e o domínio virou armadilha, para que nenhuma rodada futura o traga de volta.

## O que está no pacote

| Pasta | Conteúdo |
|---|---|
| `01-relatorios` | Este relatório, o da verificação dos 467, o de 08/09, e os CSV de abertos e de validação individual |
| `02-base-do-sistema` | A base completa dos 468 registros e a dos 210 da rodada anterior |
| `03-lotes-para-colar` | 32 lotes de 15 registros, prontos para colar |
| `04-codigo-e-motores` | Os patches de 08 e 09/09, a tabela de rotas, a curadoria de fontes e as 9 armadilhas |
| `05-acervo-drive` | O banco do acervo e os 20 índices por UF |
| `06-validacao-documento-por-documento` | A ficha de cada um dos 231 registros: rota usada, achado e estado |

O patch aplica limpo na `main` de hoje (`62f9737c82`) — conferido clonando o repositório, voltando
àquele commit e aplicando — e a suíte inteira passa: **316 testes verdes**, incluindo a falha antiga que
existia antes desta rodada, e `scripts/verificar_privacidade.py` limpo. O `git push` continua negado pelo
proxy desta sessão, que autoriza por repositório — por isso a entrega é o patch.
