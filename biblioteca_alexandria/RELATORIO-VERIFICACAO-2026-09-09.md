# Verificação de todas as oportunidades sem verificação — 09/09/2026

## O tamanho real do que faltava

O senhor pediu para analisar **todas** as oportunidades ainda sem verificação. Medi antes de agir, porque
"todas" eram 19.290 registros — e eles não são a mesma coisa:

| Grupo | Qtde | O que é |
|---|---:|---|
| PNCP (API oficial) | **408** | Registro de edital com chave do órgão. Tratável pelo método dos 210. |
| Outras fontes | **59** | Plataformas privadas, sensores, portais de notícia, sites de patrocinador. |
| Diários oficiais municipais | **18.615** | Edições **inteiras** de diário, capturadas do Querido Diário por palavra-chave. |

Fechei os **467 tratáveis** nesta rodada. Os 18.615 têm estratégia própria, no fim deste relatório.

## Resultado dos 467

**468 registros verificados** (um dos 59 continha dois editais distintos na mesma página, e virou dois).
Cada um com objeto integral, início e fim de inscrição e link da página oficial de publicação.

| Situação de prazo | Qtde |
|---|---:|
| Aberto em 09/09/2026 | 54 |
| Encerrado | 283 |
| Sem prazo confirmado (campo nulo, com motivo escrito) | 131 |

| Triagem | Qtde | O que significa |
|---|---:|---|
| Aprovado | 38 | Objeto compatível com fomento a OSC |
| Atenção | 105 | Passa, mas exige conferência humana antes de virar caso |
| Reprovado | 293 | Não é edital de fomento a OSC — com a família e o motivo registrados |
| Pendência | 26 | Falta fonte oficial: registrado como pendência, não como oportunidade |
| Vetor / ruído | 6 | Página índice ou conteúdo institucional, reclassificado |

**Nenhuma data foi inventada ou estimada.** Os 131 registros sem prazo confirmado estão com os dois
campos nulos e o motivo na observação. Um nulo honesto vale mais que uma data plausível.

## As 11 oportunidades ABERTAS que a rodada achou

Duas fecham em quatro dias.

| Fim | Onde | O que é | Página oficial |
|---|---|---|---|
| **13/09** | Nacional | **Editais Sociais 2026 do Banco do Nordeste** — incentivo fiscal (FIA, Pessoa Idosa, Esporte, Pronon/Pronas-PCD), até **R$ 1,5 milhão por projeto**, inscrição pelo Convênios Web | bnb.gov.br |
| **13/09** | POA, RJ Zona Oeste, interior de SP | **Instituto Lojas Renner — Encantando Comunidades**: R$ 10 mil de recurso livre para até 30 organizações | institutolojasrenner.org.br |
| **15/09** | DF | Credenciamento de OSC no MEMP para cadastro de parceiros (empreendedorismo feminino) | pncp.gov.br |
| **22/09** | Curitiba/PR | Chamamento Público Resíduos Sólidos (objeto de três palavras — precisa abrir o edital) | pncp.gov.br |
| **25/09** | Indaiatuba/SP | Parceria com OSC de proteção animal, recurso do Fundo Municipal | pncp.gov.br |
| **25/09** | Litoral do PR | **Funbio, Chamada 07/2026** — planos de manejo de RPPN, para OSC ambiental | chamadas.funbio.org.br |
| **09/10** | Litoral do PR | **Funbio, Chamada 08/2026** — uso público e negócios sustentáveis em RPPN | chamadas.funbio.org.br |
| **09/11** | Montes Claros/MG | Acolhimento de longa permanência para pessoas idosas | pncp.gov.br |
| **04/12** | Nacional | **BNDES Periferias em Rede, 6º ciclo** — apoio a subprojetos de organizações de base em periferias | bndes.gov.br/periferias |
| **10/12** | Guarapuava/PR | Coleta seletiva solidária na UNICENTRO (associações e cooperativas) | pncp.gov.br |
| **31/12/2027** | Canoas/RS | Credenciamento permanente de agremiações carnavalescas sem fins lucrativos | pncp.gov.br |

Fora dessas, uma pendência de prioridade alta: o **Edital FME Transforma 02/2026 da Fundação Maria
Emília** (até R$ 1 milhão em saúde e educação) tem indício de inscrição aberta até 30/10/2026, mas o
domínio `fundacaomariaemilia.org.br` está com certificado SSL inválido e não abre por nenhum caminho.
Não registrei a data porque a única fonte é portal de notícia, que pela sua regra não vale para prazo.
**Vale um telefone para a Fundação.**

## O veto que faltava no sistema

De 317 objetos lidos na API oficial do PNCP, **116 eram credenciamento para prestar serviço ao órgão** —
consulta médica, exame, serviço funerário, manutenção de frota, hospedagem, transporte — remunerado por
procedimento executado em tabela SUS/SIGTAP. Quase todos dizem *"com ou sem fins lucrativos"* ou
*"preferencialmente entidades filantrópicas"*, e era exatamente essa frase que os fazia passar pelo filtro:
o sistema perguntava "o texto fala de terceiro setor?" e não "isto repassa recurso a uma entidade?".

Onze famílias novas entraram em `src/inconformidade.py`:

| Família | Casos | Por que reprova |
|---|---:|---|
| serviço ao órgão | 128 | A entidade vende serviço, não recebe fomento |
| compra ou fornecimento | 67 | Entra como fornecedora (PNAE, refeições, combustível, medicamentos) |
| imóvel ou mercado | 13 | Prospecção imobiliária, locação, comodato |
| parecerista ou júri | 12 | Pagamento por parecer emitido, destinatário é pessoa física técnica |
| instituição financeira | 10 | Banco, cooperativa de crédito, microcrédito — inclusive "banco de fomento" |
| cachê artístico | 9 | Contratação de artista para evento do órgão |
| busca de patrocinador | 8 | O recurso **entra** no órgão |
| uso de espaço público | 7 | Permissão de uso, barraca, stand — a entidade paga ou vende |
| resultado de habilitação | 7 | A inscrição já fechou e foi julgada |
| conteúdo institucional | 8 | Livro, pesquisa, campanha, curso, desconto |
| destinado a entes públicos / pessoa física | 4 | Adesão de municípios; prêmio para jornalista |

**E o resgate que impede o erro caro.** Nenhuma dessas famílias reprova quando o objeto nomeia um
instrumento de fomento de verdade e menciona entidade sem fins lucrativos — nesse caso o veredito cai
para *atenção*, que é conferência humana, não descarte. É a diferença entre "credenciamento de clínica
para fazer exame" e "credenciamento de OSC para celebrar termo de fomento na área da saúde". Falso
positivo é o erro caro: perde oportunidade e não deixa rastro.

Duas correções de princípio, achadas por testes que já existiam:

- **Objeto pobre não é mais reprovado por ausência de vocabulário.** "CHAMAMENTO PÚBLICO RESÍDUOS
  SÓLIDOS", de Curitiba, tem três palavras e pode ser parceria com cooperativa de catadores. Vai a
  conferência — e está na lista de abertos acima justamente por isso.
- **"Banco de fomento" não passa mais** só por conter a palavra fomento.

Concordância com a classificação que fiz registro por registro: 316 de 317. A única divergência é o
módulo sendo mais rigoroso que eu, e ele está certo.

## Melhorias levadas aos motores de busca

O catálogo conhecia **BNDES Periferias** por nome e mandava o coletor para a busca do Diário Oficial da
União e para a home do BNDES. A chamada aberta está em `bndes.gov.br/periferias`, endereço que não
estava na lista — o motor procurava para sempre onde a informação não está. Corrigido, junto com mais
três fontes.

**Nove fontes novas** entraram confirmadas: Banco do Nordeste (Editais Sociais), Funbio (Litoral do
Paraná), Movimento Bem Maior, Rede do Bem, Fundação Tide Setubal, Instituto Clima e Sociedade, Banrisul
Cultural, Instituto Impactarte e a página de chamamentos da SECULT Goiás.

**Seis armadilhas registradas**, todas medidas nesta rodada:

- **PNCP**: HTTP 429 a partir de cerca de 14 requisições rápidas. Com 2,5 s de intervalo e recuo
  progressivo, 317 consultas passaram sem um único erro. Consultar em fila, nunca em paralelo.
- **Plataformas privadas de licitação**: 86 dos 408 registros tinham o link apontando para elas, sem
  chave do PNCP. A saída é a busca oficial `pncp.gov.br/api/search/`, que devolve a chave — 12 registros
  voltaram a ter página oficial assim.
- **Portais de notícia**: as datas de duas chamadas do Funbio estavam vencidas em relação à página
  oficial, e um edital de Santa Luzia do Paruá/MA descrito como "Diálogo Competitivo 002/2026" não
  existe no portal de licitações do município. Servem para descobrir o nome, nunca o prazo — como a sua
  regra já dizia.
- **BNDES patrocínios**: portal em JavaScript, só abre com navegador. É vetor permanente, não edital.
- **Fundação Maria Emília**: SSL inválido.
- **goias.gov.br/cultura/termos-de-fomento**: lista de termos já celebrados, reposta na lista.

### Um problema do sistema que precisa da sua decisão

As melhorias de fontes de Goiás que entraram em 08/09 **não estão mais** no catálogo em produção: o
`config/fontes_captacao_260.json` do repositório voltou a ter 260 fontes e **zero armadilhas**. A
regeneração automática de dados reescreve esse arquivo e descarta o que foi curado à mão. Reapliquei
tudo agora, mas vai se perder outra vez na próxima regeneração. Duas saídas: separar as curadorias em um
arquivo que a regeneração não toque, ou fazer a regeneração reaplicar os scripts de curadoria no fim.
Precisa de uma decisão sua sobre qual caminho seguir.

## Acervo no Drive: uma pasta por edital

Regra nova aplicada. Em `Eldorado — Farol de Alexandria / Editais Históricos`:

- **20 pastas de UF** (GO, SP, CE, PR, MG, SC, RS, BA, PE, MT, PA, RJ, DF, ES, PB, RN, RO, AL, MA e
  "Nacional e multi-UF");
- **130 pastas de edital**, cada uma com o dossiê dentro — objeto integral, prazo, órgão, página
  oficial, veredito de triagem e observação;
- os **6 documentos de Goiás** que estavam soltos foram para pastas próprias;
- **um índice JSON em cada pasta de UF** e o banco de dados na raiz, com o id de cada pasta.

Entra no acervo todo edital cujo objeto foi obtido de fonte oficial e que a triagem classificou como
aprovado, atenção ou pendência, **mais todo edital de Goiás, inclusive os reprovados** — porque a regra
de Goiás é de busca histórica, não de captação em curso. Ficaram fora os registros que a triagem reprovou
por não serem edital de fomento; estão na base com o motivo, e posso trazê-los se o senhor quiser.

**O PDF ainda não está dentro das pastas.** O script `scripts/espelhar_editais_drive.py` faz esse envio a
partir do GitHub Actions, onde há rede e credencial — os bytes de um PDF não podem passar por mim sem
custo alto e sem risco de corromper. Até ele rodar, cada dossiê traz o endereço de origem do documento.

## Os 18.615 diários municipais

Este grupo não é edital. São PDFs de **edições inteiras** do diário oficial de 484 municípios (Porto
Alegre 639, Curitiba 465, Uberlândia 463, Florianópolis 341, São Luís 331, Manaus 331, Teresina 325),
capturadas porque a palavra "chamamento público" ou "organizações da sociedade civil" apareceu em algum
lugar da edição. Nenhum tem prazo identificado; 11.080 estão classificados como `apenas_indicio` e 7.651
como `insuficiente`.

Para cada um seria preciso localizar o aviso dentro do diário, ler o trecho e decidir. A um minuto por
edição, são semanas de processamento contínuo. **Não vou fingir que isso cabe em uma rodada.**

Três caminhos, em ordem do que eu recomendo:

1. **Só Goiás e o entorno, primeiro.** Filtrar os diários de municípios goianos e do Distrito Federal,
   que é onde o senhor atua, e processar esse recorte por inteiro. É o que dá resultado utilizável mais
   rápido.
2. **Recorte por ano e por qualidade.** Processar só os de 2026 com classe `apenas_indicio`, descartando
   os anteriores, que já venceram — o acervo histórico deles pode esperar.
3. **Automação no GitHub Actions.** Um script que baixa a edição, localiza o trecho por expressão
   regular, extrai as duas páginas em volta e grava só o recorte. Roda sozinho, sem mim, e leva dias —
   mas precisa ser escrito e testado, e a decisão de escrevê-lo é sua.

Se o senhor não escolher, faço o caminho 1 na próxima rodada, porque é o que atende o seu escritório.

## Entregas

| Arquivo | O que é |
|---|---|
| `2026-09-09-eldorado-467-completo.json` | Os 468 registros verificados, com todos os campos |
| `lotes-2026-09-09.zip` | 32 lotes de 15 registros, prontos para colar |
| `ABERTOS-2026-09-09.csv` | Só os abertos, ordenados por prazo, para abrir no Excel |
| `PATCH-eldorado-2026-09-09.patch` | As mudanças de código, aplicam limpo na `main` atual |
| Google Drive | 20 pastas de UF, 130 pastas de edital, índices e banco atualizado |

O patch aplica sobre o commit `62f9737c82` (a `main` de hoje) e passa 53 testes nos módulos tocados. A
suíte completa tem 265 testes com **uma falha pré-existente**
(`test_gerador_dos_motores_roda_rapido_e_aceita_fontes_mapeadas`), que reproduz sem as minhas mudanças
porque o último relatório do monitor é de 03/09/2026 — **o monitor da Bússola está parado desde então**, e
isso continua pendente da rodada anterior.

Não consegui enviar o commit para o GitHub: o proxy desta sessão autoriza por repositório e nega
`amcjardimamerica-arch/Eldorado`. O patch é a entrega, e aplica com um comando.
