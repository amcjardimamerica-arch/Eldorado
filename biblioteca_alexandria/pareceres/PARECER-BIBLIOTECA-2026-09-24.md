# Parecer — a Biblioteca de Alexandria como base para motores, Piloto e Farol · 24/09/2026

## 1. Resposta direta

**A Biblioteca, como está, não tem armazenamento eficiente para direcionar os motores e o Piloto, não sustenta análise histórica
e a "análise preditiva" que existe foi construída sobre ruído.** Ela guarda bem o documento; guarda mal o dado. Hoje entrou a base
que corrige isso — leve, textual, por pastas — e o parecer diz o que ainda falta alimentar para que ela mereça o nome.

## 2. Diagnóstico, com os números

| o que se mediu | resultado |
|---|---|
| arquivos na Biblioteca | 3.946 JSON, 125 JSONL, 113 MD, 24 PDF — uma ficha por pasta, 30 MB só em oportunidades |
| editais conhecidos (sem edição de diário) | **703** · por ano: 2006: 1, 2021: 2, 2022: 1, 2023: 24, 2024: 101, 2025: 76, 2026: 489, sem-ano: 9 |
| com data de publicação | 693 (98%) |
| com **prazo** | 109 (15%) |
| com **órgão** | 16 (**2%**) |
| com valor | 9 (1%) |
| com **veredito do titular** | 259 (36%) — 39 aprovados |
| aprovados **de Goiás** | **0** de 11 julgados |
| recorrências reconhecíveis (órgão + tema, 2+ anos) | **0** |
| leis no índice | 27: 25 federais, 1 estadual, 1 municipal |

**Direcionar motores e Piloto.** O que direciona é órgão, programa, mês típico e resultado passado. Com órgão em 2% das fichas,
não há como dizer a um motor "volte ao FMDCA de Goiânia em março". Os motores hoje são direcionados pelo léxico, não pela história.

**Análise histórica.** Há profundidade só em 2024-2026 e, mesmo aí, o veredito do titular estava **fora** da Biblioteca — em
`dados/editais/extraidos` — e os 70 aprovados de lá viram 39 aqui, porque 31 não têm ficha. A Biblioteca não sabia o que o titular
já escolheu.

**Análise preditiva.** `previsoes/padroes.json` tem 2.431 "padrões" com força até 5, e o exemplo mais forte é "Prefeitura de Betim
(MG), março, cinco anos seguidos": é o **Diário Oficial de Betim** saindo todo mês, não um edital que se repete. A previsão
aprendeu o calendário dos diários, fora da abrangência. Não serve.

**Leis.** 25 federais, 1 estadual, 1 municipal, em 27 pastas com nomes inconsistentes (`doacao_bens_apreendidos` e
`doacao-bens-apreendidos` coexistem). Para Goiás e a Região Metropolitana faltam as normas que decidem o rito: o decreto estadual
do MROSC, o decreto municipal de Goiânia, os fundos e conselhos (FMDCA, FMAS, CMDCA, CMAS), as leis de incentivo municipal e
estadual ao esporte, as instruções dos tribunais de contas, a LC da RMG.

## 3. O que entrou hoje: `biblioteca_alexandria/base/` (632 KB, tudo textual)

```
base/
  editais/<ano>.jsonl        histórico: um edital por linha, um esquema só, com o veredito do titular dentro
  aprovados.jsonl            os 39 editais selecionados — a base de pontuação
  recorrencia.jsonl          preditivo: órgão + tema → anos, mês típico, duração, próxima janela (só edital real, só abrangência)
  pontuacao/criterios.json   pesos MEDIDOS: taxa de aprovação por tema, esfera, UF, abrangência, fonte, faixa de valor, exigências
  leis/indice_por_esfera.json + lacunas.json   cobertura por esfera e as 16 normas que faltam
  resumo.json · README.md
```

Refeita a cada varredura (`scripts/construir_base.py`, ligado ao workflow dos motores): **permanente, determinística, leve** —
JSONL abre em qualquer ferramenta e o `grep` responde em milissegundos. Edição de diário nunca entra.

**A pontuação do Farol** (`src/farol_pontuacao.py`) passa a vir daí: nota de 0 a 100 com o porquê, e cada peso é a taxa de
aprovação observada — critério sem três casos julgados não pontua. O que os vereditos já ensinam: esfera **federal 60%** de
aprovação (6 de 10), **municipal 15%**, estadual 13%; tema **cultura 33%**, educação 17%, assistência social 8%; fonte
**PNCP 14%** (33 de 230). Um edital federal de cultura pelo PNCP pontua 44 hoje. É pouco dado — e é o dado que existe.

## 4. O que falta alimentar, em ordem

1. **Órgão, prazo e valor na captura** — a segunda etapa da verificação (abrir a página oficial) precisa gravar os três campos.
   Sem órgão não há recorrência; sem prazo não há estrela de ouro; sem valor não há faixa.
2. **Retroalimentar a história**: os órgãos de Goiás e Goiânia que publicaram em 2023-2025 (Goyazes, FMDCA, FMAS, Secult,
   Sedes) precisam ter os editais passados lidos — é isso que cria a recorrência. A API do PNCP permite consulta por período,
   de graça; os diários de Goiás têm arquivo por edição.
3. **Os 31 aprovados sem ficha** entram na Biblioteca; e todo veredito novo do titular vai direto para a base.
4. **A previsão antiga sai** (`previsoes/`) e dá lugar a `base/recorrencia.jsonl`, que só reconhece edital real dentro da abrangência.
5. **Leis por esfera e tema**, com nomes de pasta únicos e a aplicação declarada (federal · estadual-goias · municipal-goiania ·
   rmg · judiciario), e as 16 normas abaixo.

### As normas que faltam para Goiás, Goiânia e a RMG

| esfera | norma | por quê |
|---|---|---|
| municipal-goiania | Lei Orgânica do Município de Goiânia | base de competências e subvenções municipais |
| municipal-goiania | Lei municipal de incentivo à cultura de Goiânia (Lei nº 9.154/2012 ou vigente) | incentivo fiscal municipal (ISS/IPTU) a projetos culturais |
| municipal-goiania | Decreto municipal que regulamenta o MROSC em Goiânia | rito local de chamamento, termo de fomento e prestação de contas |
| municipal-goiania | Lei do FMDCA e do FMAS de Goiânia; resoluções do CMDCA e do CMAS | registro no conselho e editais dos fundos |
| municipal-goiania | LDO e LOA de Goiânia (anexo de subvenções e emendas impositivas) | onde as emendas e subvenções são autorizadas |
| estadual-goias | Decreto estadual que regulamenta a Lei 13.019 em Goiás | rito estadual de parceria |
| estadual-goias | Lei do Pró-Esporte/incentivo ao esporte de Goiás e regulamento | incentivo fiscal estadual ao esporte |
| estadual-goias | Lei do Fundo Estadual de Cultura / Goyazes (regulamentos e portarias da Secult) | já há a lei; faltam os regulamentos e o rito de prestação de contas |
| estadual-goias | Resoluções do CEDCA-GO e do CEAS-GO | fundos estaduais e certificação |
| estadual-goias | Instruções normativas do TCE-GO e do TCM-GO sobre parcerias com OSC | como os tribunais de contas fiscalizam o repasse |
| rmg | Lei Complementar da Região Metropolitana de Goiânia (LC 27/1999 e atualizações) e o Codemetro | instrumentos e fundos metropolitanos |
| federal | Lei 14.133/2021 (contratações) — os artigos de credenciamento e concurso | é por onde o PNCP publica o que serve à OSC |
| federal | Lei 12.101/2009 e Lei Complementar 187/2021 (CEBAS) | certificação de entidade beneficente |
| federal | Lei 14.399/2022 (PNAB) e LC 195/2022 (Paulo Gustavo) com decretos | fomento cultural descentralizado a municípios de Goiás |
| federal | Decreto 8.726/2016 (regulamento do MROSC) e Portaria conjunta de prestação de contas | rito federal de parceria |
| judiciario | Resolução CNJ 154/2012 e provimentos da CGJ-GO sobre prestação pecuniária | cadastro de entidades nas varas de execução penal |

## 5. O conselho

**Extremamente pessimista.** Uma biblioteca com órgão em 2% dos registros não é biblioteca de editais: é uma pasta de títulos.
E a previsão que ela exibia era o calendário do Diário de Betim.
**Pessimista.** Zero aprovados de Goiás em 11 julgados. A base de pontuação hoje ensina o que o titular aprova **fora** da
abrangência. Até haver casos de Goiás, a nota é orientação, não decisão.
**Levemente pessimista.** Os vereditos viviam fora da Biblioteca e metade deles não tinha ficha. O sistema julgava e esquecia.
**Neutro (ponderador).** A base entrou e é a forma certa: leve, por ano, um esquema, o veredito dentro. O que a torna útil
não é código, é dado: órgão/prazo/valor na captura e a leitura retroativa de 2023-2025 nos órgãos de Goiás. Ordem: (1)
segunda etapa gravando os três campos; (2) retroalimentação pelo PNCP por período e pelos diários de Goiás; (3) leis por esfera,
começando pelo decreto municipal de Goiânia e o estadual do MROSC. A pontuação já roda e melhora sozinha a cada veredito.
**Levemente otimista.** 259 julgamentos do titular já são uma base real de aprendizado — poucos sistemas têm isso.
**Otimista.** Com órgão e mês nos registros, a recorrência vira o plano de voo do Piloto: ele passa a saber onde estar em março.
**Extremamente otimista.** A Biblioteca deixa de ser arquivo e vira memória: cada edital novo é comparado ao que o titular já
escolheu, e cada ano acrescenta um anel.
