# Parecer do conselho — skills para os Pilotos (descobrir e investigar) · 29/09/2026

## 1. Resposta curta

**Há condição, e vale a pena — desde que "skill" não signifique "instrução maior".** Os Pilotos rodam um modelo local
pequeno (Qwen3-8B, contexto de 16 mil tokens, no servidor do GitHub). Para esse porte, uma skill é um **pacote pequeno
por tarefa**: instrução curta (até ~500 tokens), 3 a 5 exemplos reais (bons e ruins), uma **ferramenta determinística**
quando a tarefa não precisa de IA, e um **teste com gabarito**. A skill só é carregada na missão que precisa dela.
Hoje acontece o oposto: o Espião recebe ~1.100 tokens de constituição em **todo** pedido — e isso já causou estouros
de tempo.

## 2. Diagnóstico medido

| Piloto | resultado hoje | onde perde |
|---|---|---|
| **Interceptador** (314 estudos) | 24 validadas (**8%**), 104 parciais (33%), 141 insuficientes (**45%**); ~10 min por missão; 30 voos com erro | condições que mais faltam: **prazo de recurso (233), resultado (220), prazo de inscrição (174)** — as três vivem na tabela de **cronograma**, quase sempre em PDF; depois valor (171), área (150), requisitos (147) |
| **Espião** (últimas avaliações) | **16 com resultado** em ~3.990 missões (**0,4%**) | **3.659 "nada passou no crivo"**, 233 "fora do objeto"; na validação, 81% das candidatas dele foram descartadas |

**Matéria-prima que já existe e vira skill** (não é preciso começar do zero):
1.165 decisões rotuladas da validação individual (gabarito de "é/não é oportunidade") · 105 financiadores com site
oficial aprendido e a estatística das rotas que funcionam (regulamento 50, site do financiador 23, programa+edital 17)
· 104 republicadores catalogados · 15 regras aprendidas por motor · 39 opressores com duas ou mais edições (padrões de
cronograma do mesmo financiador) · 314 estudos do Interceptador com o que foi e o que não foi comprovado.

## 3. As skills propostas

### Interceptador — investigar
| skill | quando carrega | o que leva | dado que já temos | meta |
|---|---|---|---|---|
| **Cronograma** | toda leitura de edital | ferramenta que lê **tabelas de PDF** (pdfplumber) e datas por extenso; instrução para mapear inscrição, resultado e recurso; exemplos de cronogramas reais | 128 editais validados/parciais | prazo de recurso e resultado comprovados em ≥50% (hoje ~25%) |
| **Site oficial** | antes de ler | rotas na ordem do que funciona (regulamento → site do financiador → programa+edital); memória dos 105 financiadores; lista de republicadores | aprendizado de 28/09 | ≥80% das missões com página oficial validada |
| **Valor e requisitos** | edital com anexos | onde costumam estar (item "dos recursos", "da habilitação"); normalização de valores | trechos comprovados nos 314 estudos | valor comprovado ≥60% |
| **Dispensa justificada** | item não encontrado | quando o edital dispensa (não há recurso, fluxo contínuo) × quando só não foi achado | 10 dispensas reais | zero dispensa sem trecho |
| **Diário oficial** | menção em diário (71 no mapa) | ferramenta que recorta o ato dentro do PDF da edição; extrai órgão, objeto, prazo | índice de diários | metade das menções vira oportunidade com órgão e prazo |
| **Ficha de empresa** | empresa sem edital | os 8 itens; sinais de investimento social | 20 fichas | fonte confirmada ≥50% |

### Espião — descobrir
| skill | quando carrega | o que leva | dado que já temos | meta |
|---|---|---|---|---|
| **Triagem de indício** | antes de entregar qualquer candidata | exemplos positivos e negativos tirados das **1.165 decisões rotuladas**; as 15 regras aprendidas | validação individual | descarte na validação de 81% → ≤40% |
| **Caçador em site de financiador** | catalogar | onde os editais ficam em sites de institutos/empresas (menus, "editais", "chamadas"); o que não é (notícia, vaga, relatório) | 3.659 "nada no crivo" como exemplos negativos | missões com resultado 0,4% → ≥3% |
| **Entidades empresariais** | meta de 27/09 | associações, federações, CDLs; Goiás primeiro; descarte de outros estados | config/entidades_prioritarias.json | ≥1 fonte nova de entidade por semana |
| **Consulta de busca** | apostas do briefing | como montar a consulta (programa entre aspas, financiador, ano, site:); apostas que renderam | apostas_que_renderam.json | apostas com candidata ≥20% |

## 4. Como construir (arquitetura)

```
skills/
  interceptador/cronograma/   SKILL.md (≤500 tokens) · exemplos.jsonl · ferramentas.py · avaliacao.jsonl
  interceptador/site_oficial/ …
  espiao/triagem/             …
```
- **Carregador por missão**: no máximo 1–2 skills por pedido; a constituição do Espião encolhe para ~300 tokens.
- **Ferramenta antes de instrução**: o que é mecânico (tabela de PDF, datas, recorte de diário) vira código — o
  modelo decide, não garimpa.
- **Bancada de avaliação** (workflow próprio): cada skill roda com e sem ela sobre o gabarito; **só entra em produção
  se melhora** — % validadas, condições comprovadas por missão, falsos positivos, tempo.
- **Revisão periódica**: a cada análise do Claude (3 dias), os exemplos das skills são revistos com os novos casos.
- A ferramenta **skill-creator** disponível nesta conversa pode ajudar a redigir e testar cada skill; o formato segue a
  convenção de pasta com instrução + recursos, adaptado ao modelo local.

## 5. Riscos

- **Porte do modelo**: um 8B segue instrução curta e exemplo concreto; instrução longa ele ignora ou estoura o tempo.
- **Tempo**: a missão já leva ~10 min; skill não pode aumentar isso — ferramentas determinísticas tendem a reduzir.
- **Exemplos viciados**: poucos exemplos de um só financiador ensinam o padrão errado; rodízio e avaliação resolvem.
- **Manutenção**: 10 skills são 10 coisas a manter; por isso a ordem por retorno e a bancada.
- **Skill errada carregada**: o carregador precisa de regra explícita por tipo de missão (não por adivinhação).

## 6. Plano

1. **Fase 1 (maior retorno)**: skill **Cronograma** (com leitura de tabela de PDF) e skill **Site oficial**, mais a
   **bancada de avaliação**. São elas que atacam as três condições que mais faltam e a página oficial.
2. **Fase 2**: **Triagem de indício** do Espião (corta o desperdício de 81%) e **Diário oficial** (71 menções paradas).
3. **Fase 3**: as demais, e a constituição enxuta do Espião.

Parâmetros de qualidade: validadas 8% → 20%; insuficientes 45% → 25%; Espião com resultado 0,4% → 3%; tempo por
missão ≤10 min; nenhuma skill acima de 500 tokens; nenhuma skill em produção sem ganho medido na bancada.

## 7. O conselho

**Extremamente pessimista — chief engineer.** Um modelo de 8B não vira especialista por receber mais texto. Se a
skill for prompt, ela vai engordar o pedido, estourar o tempo e o resultado piora — já vimos isso com a constituição.

**Pessimista — staff engineer.** O maior gargalo (cronograma em tabela de PDF) não é de inteligência, é de leitura.
Chamar isso de skill de IA seria esconder um problema de extração.

**Levemente pessimista — professor.** Sem bancada com gabarito, cada skill vira opinião. A primeira entrega tem de ser
a medição, não a skill.

**Neutro — CTO (ponderador).** A condição existe e os ingredientes já estão no sistema: 1.165 decisões rotuladas, 105
financiadores aprendidos, 314 estudos com o que falta. O desenho certo é skill = instrução curta + exemplos reais +
ferramenta determinística + teste, carregada por missão. Começar pelas duas de maior retorno (cronograma e site
oficial) com bancada; só promover o que melhorar os números.

**Levemente otimista — professor.** As rotas que funcionam já estão medidas: a skill de site oficial nasce com dados,
não com palpite.

**Otimista — staff engineer.** A triagem do Espião usando o gabarito da validação pode transformar 3.659 missões vazias
em aprendizado: cada descarte vira exemplo negativo.

**Extremamente otimista — CTO.** Com skills por tarefa, os Pilotos passam a melhorar a cada análise: o que o Claude
valida vira exemplo, o que falha vira regra — um sistema que se especializa sozinho.
