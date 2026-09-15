# Verificação dos 63 editais não verificados — 15/09/2026

Os 63 registros do relatório foram verificados **um por um**, na fonte oficial do órgão ou do
patrocinador. Nenhuma data foi estimada: onde não houve confirmação, o campo foi a nulo com o motivo
escrito. Este documento diz o que foi encontrado, em que fonte, e o que muda a decisão de captação.

## O placar

| | |
|---|---:|
| Registros verificados | **63** |
| Com prazo confirmado | 32 |
| Sem prazo confirmado, com motivo escrito | 31 |
| Com prazo ainda aberto hoje | **12** |
| Abertos e aproveitáveis | **10** |
| Com página oficial identificada | 44 |
| Prazos corrigidos em relação ao que o sistema tinha | 2 |
| Aprovados / em atenção / reprovados | 4 / 17 / 42 |

## O que está aberto, em ordem de urgência

| Fecha | Dias | Veredito | Órgão | UF |
|---|---:|---|---|---|
| **2026-09-21** | 6 | atencao | PNCP — MUNICIPIO DE JARU | RO |
| **2026-09-22** | 7 | atencao | PNCP — MUNICIPIO DE JARU | RO |
| **2026-09-23** | 8 | atencao | PNCP — MUNICIPIO DE IPU | CE |
| **2026-09-30** | 15 | atencao | PNCP — MUNICIPIO DE LAGOA VERMELHA | RS |
| **2026-10-02** | 17 | atencao | PNCP — MUNICIPIO DE ITATINGA | SP |
| **2026-10-07** | 22 | aprovado | PNCP — MUNICIPIO DE OSORIO | RS |
| **2026-10-08** | 23 | atencao | PNCP — MUNICIPIO DE GUAIRA | PR |
| **2026-10-08** | 23 | reprovado | PNCP — CAIXA ECONOMICA FEDERAL | DF |
| **2026-10-09** | 24 | atencao | PNCP — MUNICIPIO DE PORTO FELIZ | SP |
| **2026-10-11** | 26 | aprovado | ABCR — Associação Brasileira de Captadores | BR |
| **2026-10-28** | 43 | reprovado | PNCP — MUNICIPIO DE FARROUPILHA | RS |
| **2026-10-30** | 45 | aprovado | ABCR — Associação Brasileira de Captadores | BR |

## Os seis achados que mudam decisão

### 1. CONANDA/MDHC nº 01/2026 — R$ 6 milhões — o prazo foi prorrogado para 11/10/2026

O sistema tinha este edital como encerrando em **17/09** — dois dias. A página oficial de editais do
Ministério dos Direitos Humanos traz uma **retificação** que diz, literalmente: onde se lia
*"18/08/2026 a 17/09/2026"*, leia-se *"18/08/2026 a 11/10/2026"*. São **26 dias**, não dois.

São R$ 6 milhões no total e até R$ 1 milhão por projeto, seis propostas selecionadas, termo de fomento
pela Lei 13.019/2014, propostas pelo Transferegov.br. A mesma retificação elevou a abrangência
territorial exigida de **três para cinco regiões do país** — o que pesa no enquadramento e precisa ser
lido antes de montar a proposta.

É a armadilha da errata, outra vez: a informação que muda a decisão estava no anexo, não no corpo.

### 2. A Fundação Maria Emília abriu — até R$ 1 milhão, até 30/10/2026

Esta pendência estava aberta desde 09/09, registrada como *"precisa de telefone, não de código"*: o
domínio `fundacaomariaemilia.org.br` tem certificado inválido e não abre por nenhum caminho. **O domínio
vivo é `mariaemilia.org.br`** — e abriu.

O PDF do **Edital FME Transforma nº 02/2026** foi lido na íntegra: objeto é *"selecionar e apoiar
projetos nas áreas de Saúde e Educação"*; inscrições de 24/08 a **"30/10/2026, às 23h59"**; três faixas
de valor, a maior de R$ 500.001,00 a R$ 1.000.000,00; elegíveis OSC, fundação, instituto e instituição
de ensino, exigido *"estar legalmente constituída há pelo menos 2 (dois) anos"*, sem restrição de UF.

Até ontem essa data só existia em portal de notícia, e por isso não estava registrada. Agora está
confirmada na fonte.

### 3. Ipu/CE fecha um dia antes do que o sistema registrava

O sistema tinha 24/09; o órgão declara encerramento em **23/09/2026 às 17h**. Um dia a menos.

### 4. Jaru/RO — o registro apontava para o edital errado

Dois registros do sistema apontavam para o mesmo edital, e um deles estava trocado. São **dois
chamamentos diferentes** do mesmo município: o de nº 196 (distribuição de calcário e vagão forrageiro,
fecha 21/09) e o de nº 197 (plantadeira de mudas de café, fecha 22/09).

### 5. Porto Feliz/SP — cinco editais dentro de um registro só

Um único registro carrega **cinco editais PNAB distintos** (nº 10 a 14: formação cultural, iniciativas
periféricas, inéditas, continuadas e trajetória artística), com janela de 09/09 a 09/10/2026. Cada um
pode ter cronograma e valor próprios. Precisa ser desdobrado em cinco registros antes de qualquer
inscrição.

### 6. Revogação e prorrogação escondidas nos anexos

**Quixeramobim/CE** está com *"Situação: REVOGADA"* no portal do próprio município. **Ipojuca/PE** tem
um anexo chamado *"05___PRORROGADO_EDITAL_DE_CREDENCIAMENTO..."* — prazo prorrogado que nenhum campo da
API reflete. Nos dois casos, a informação decisiva estava no anexo.

## Por que 31 ficaram sem prazo confirmado

Não por falta de trabalho. Os motivos, medidos:

- **O PDF do edital não é legível da nuvem.** A ferramenta de leitura devolve conteúdo binário, e a
  maior parte dos cronogramas reais mora dentro do PDF. Onde a API do órgão declarava data, ela foi
  registrada com a ressalva escrita; onde não havia, o campo ficou nulo.
- **Sites municipais bloqueiam.** Jaru, Agrolândia, Porto Feliz, Bento Gonçalves, Xanxerê e o CNJ
  responderam 403. Gravataí, São Bento do Sul e Osório têm certificado inválido. Campo Mourão,
  Carazinho, Rondonópolis e Nova Ubiratã servem apenas a casca JavaScript.
- **Datas impossíveis na origem.** Sete registros trazem encerramento anterior à própria publicação —
  Crateús foi divulgado seis horas depois de fechar; Araquari entrou no PNCP três meses e meio depois.
  Nesses casos a data foi anulada: a fonte se contradiz.

## O que os 42 reprovados ensinam

Nenhum deles é edital de fomento a organização da sociedade civil, e a reprovação **não depende de**
**prazo**. Os motivos que mais apareceram: credenciamento de prestador remunerado por procedimento,
vaga ou paciente; locação e prospecção de imóvel; credenciamento de parecerista para subcomissão
técnica de julgamento; busca de patrocinador pelo próprio órgão — em que a entidade pagaria, não
receberia; edital já homologado e adjudicado; e página de atos já celebrados por inexigibilidade.

Um caso merece registro: a **CAIXA** tem chamamento aberto até 08/10 para entidades sem fins
lucrativos, mas é credenciamento de executor do Programa de Aprendizagem da própria CAIXA, remunerado
por vaga de aprendiz, sob regulamento de estatal e não sob o MROSC. Parece fomento e não é.

## Os arquivos para atualizar o sistema

| Arquivo | Para que serve |
|---|---|
| `RESPOSTA-VERIFICACAO-2026-09-15.json` | formato exato do MODELO que veio no relatório — é o que o sistema consome |
| `VERIFICACAO-COMPLETA-2026-09-15.json` | o mesmo, com veredito, família de reprovação, anexos, rota usada e o prazo anterior |
| `VERIFICACAO-63-2026-09-15.csv` | a planilha, ordenada por urgência |

Cada observação diz em que fonte a informação foi lida, o que não abriu e por quê, e por que a data
ficou nula quando ficou.
