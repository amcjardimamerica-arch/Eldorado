# Parecer — Linha de produção de informação, skills dos motores e rede neural (02/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO de big tech e professores de computação, Python) · **Associação de referência:** A.M.C. Jardim América (OSC, Goiânia/GO)

## 1. Diagnóstico em números (dados do próprio sistema, 02/10/2026)

| Etapa | Medida |
|---|---|
| Registros na base (bronze) | **17.603** — 96% de um único canal (Querido Diário, 16.890); 99% sem prazo; todos com o mesmo status ("capturada") |
| Oportunidades distintas (entidades) | **1.950** — o Querido Diário repete cada ato ~12 vezes (16.890 → 1.385) |
| Vistas em 2+ canais | **13** — a premissa dos múltiplos canais quase não se realiza: cada canal traz oportunidades *exclusivas* |
| Validadas como reais, por canal | Querido Diário 108 · PNCP 9 · ABCR 7 · Observatório 6 · Espião 5 |
| Sensores | 127 ativos; **30 de descoberta sem rendimento** e **12 com falha parcial** (planos de correção abaixo) |
| Mapa → confirmadas | 279 → **22** |
| Validação humana | 1.459 decisões — **61% descartes**; 244 pendentes |
| Registros que se perdiam | **62** com link de buscador (sem site oficial), quase todos do Espião |
| Identidade dos canais | fragmentada (`pncp`/`pncp-api`, `abcr`/`plat-abcr`, três nomes do Observatório) |

## 2. Premissas — o que fica e o que muda

| Premissa atual | Vira | Por quê |
|---|---|---|
| Mais canais = mais oportunidades | **Mais canais *complementares*; mede-se a contribuição exclusiva e validada de cada um** | só 13 de 1.950 oportunidades em 2+ canais; o volume engana (QD: 96% dos registros, mas também o canal mais valioso) |
| Cada motor faz tudo (coleta, filtro, registro) | **Motor só coleta; o resto é linha comum** (contrato, entidade, nota, qualificação) | evita 127 implementações diferentes da mesma lógica e a perda de dados entre elas |
| Filtrar na coleta | **Identificar → qualificar** (decisão do titular) — nada vai ao lixo; contrato violado vai à fila de reprocessamento | 62 registros com link de buscador se perdiam |
| Repetição é ruído a apagar | **Repetição em canais diferentes é corroboração** (confiança); no mesmo canal, é a mesma entidade | a entidade resolvida conta os canais |
| Regras fixas decidem | **Regras viram "rotuladores" de uma rede que aprende com a validação** | as regras sozinhas não separam real × descartado (AUC 0,50); a rede, sim (0,905) |
| Validação no fim, em ordem qualquer | **Aprendizado ativo:** a rede ordena a fila (maior nota e incerteza primeiro) e cada decisão vira rótulo | 104 dos 244 pendentes são prováveis reais |
| Motor sem rendimento continua igual | **Plano de correção automático** por diagnóstico (fluxograma) | 30 motores de descoberta nunca renderam |
| Pilotos buscam livremente | **Pilotos atacam as lacunas:** chaves dos livros em janela, prováveis sem corroboração, fila de reprocessamento | amplitude com foco |

## 3. Referências abertas consultadas (API do GitHub, 02/10/2026)

| Problema | Repositório | Estrelas | Último push | Licença |
|---|---|---|---|---|
| coleta | [okfn-brasil/querido-diario](https://github.com/okfn-brasil/querido-diario) | ★ 1.398 | 2026-09-23 | MIT |
| coleta | [scrapy/scrapy](https://github.com/scrapy/scrapy) | ★ 64.546 | 2026-10-02 | BSD-3-Clause |
| coleta | [adbar/trafilatura](https://github.com/adbar/trafilatura) | ★ 6.903 | 2026-09-30 | Apache-2.0 |
| coleta | [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | ★ 84.642 | 2026-09-25 | Apache-2.0 |
| deduplicacao entre canais | [dedupeio/dedupe](https://github.com/dedupeio/dedupe) | ★ 4.517 | 2025-07-29 | MIT |
| deduplicacao entre canais | [moj-analytical-services/splink](https://github.com/moj-analytical-services/splink) | ★ 2.453 | 2026-09-30 | MIT |
| deduplicacao entre canais | [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers) | ★ 19.144 | 2026-10-01 | Apache-2.0 |
| deduplicacao entre canais | [facebookresearch/faiss](https://github.com/facebookresearch/faiss) | ★ 41.011 | 2026-10-02 | MIT |
| supervisao fraca e rotulos | [snorkel-team/snorkel](https://github.com/snorkel-team/snorkel) | ★ 6.012 | 2026-09-14 | Apache-2.0 |
| supervisao fraca e rotulos | [cleanlab/cleanlab](https://github.com/cleanlab/cleanlab) | ★ 11.684 | 2026-01-13 | Apache-2.0 |
| supervisao fraca e rotulos | [argilla-io/argilla](https://github.com/argilla-io/argilla) | ★ 5.135 | 2026-09-28 | Apache-2.0 |
| aprendizado continuo e decisao | [online-ml/river](https://github.com/online-ml/river) | ★ 6.119 | 2026-09-30 | BSD-3-Clause |
| aprendizado continuo e decisao | [VowpalWabbit/vowpal_wabbit](https://github.com/VowpalWabbit/vowpal_wabbit) | ★ 8.727 | 2026-09-28 | NOASSERTION |
| portugues | [neuralmind-ai/portuguese-bert](https://github.com/neuralmind-ai/portuguese-bert) | ★ 886 | 2024-06-17 | NOASSERTION |
| portugues | [explosion/spaCy](https://github.com/explosion/spaCy) | ★ 33.935 | 2026-09-30 | MIT |
| qualidade e orquestracao | [great-expectations/great_expectations](https://github.com/great-expectations/great_expectations) | ★ 11.854 | 2026-10-02 | Apache-2.0 |
| qualidade e orquestracao | [unionai-oss/pandera](https://github.com/unionai-oss/pandera) | ★ 4.472 | 2026-09-26 | MIT |
| qualidade e orquestracao | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | ★ 23.964 | 2026-10-02 | Apache-2.0 |
| qualidade e orquestracao | [dagster-io/dagster](https://github.com/dagster-io/dagster) | ★ 16.232 | 2026-10-02 | Apache-2.0 |
| qualidade e orquestracao | [dlt-hub/dlt](https://github.com/dlt-hub/dlt) | ★ 5.924 | 2026-10-02 | Apache-2.0 |

**Escolha de engenharia:** o Eldorado roda no GitHub gratuito, sem GPU, com núcleo só na biblioteca-padrão do Python. As **técnicas** foram aplicadas de forma enxuta, sem trazer as bibliotecas: blocagem e semelhança de conjunto de termos para entidades (dedupe/Splink, com `rapidfuzz`, já no projeto); regras como rotuladores (Snorkel); rótulos suspeitos por *confident learning* (Cleanlab); fila por incerteza (Argilla); contratos de dados e fila de reprocessamento (Great Expectations, Pandera, dlt); planos de reexecução (Prefect, Dagster). BERTimbau e embeddings (sentence-transformers, FAISS) ficam como evolução quando houver orçamento de máquina.

## 4. O que foi construído

- **`src/linha_producao.py`** + `config/linha_producao.json` — canal canônico, famílias de fonte, contrato de dados, fila de reprocessamento, resolução de entidades entre canais (corroboração), funil, contribuição exclusiva e validada de cada canal e **livro-razão** só de acréscimos. 17.603 registros em 4 s.
- **`src/rede_neural.py`** — rede de 1 camada oculta (16 neurônios, ReLU) sobre entradas esparsas (*feature hashing* 2^13), Adam, pesos por classe, regularização L2 e **calibração por temperatura**; treina por semana (≈35 s), pontua a cada ciclo; nota de cada livro; fila de validação por incerteza; rótulos suspeitos.
- **`src/planos_correcao.py`** — diagnóstico de cada canal a cada ciclo e o plano previsto no fluxograma.
- **Skills:** 8 por família de fonte + 2 comuns (`skills/motores/*`, `skills/comum/linha_producao`, `skills/comum/plano_correcao`); vínculo motor → skill em `config/skills_motores.json` (127 sensores).
- **Fluxograma:** `docs/arquitetura/linha-de-producao.md`.

## 5. Resultados medidos

| | Regras sozinhas | Rede neural (validação cruzada, 5 partes) |
|---|---:|---:|
| AUC (separar real × descartado) | 0,497 | **0,905** |
| Precisão (nota ≥ 0,5) | 0,266 | **0,808** |
| Revocação (nota ≥ 0,5) | 0,989 | 0,616 |
| Perda logarítmica | — | 1,11 → **0,34** com a calibração |

**Correção feita no caminho:** a 1ª versão deu 0,2% ao Goyazes e 100% ao Zurich. Causa: descartes por *cópia/duplicata/encerramento* (oportunidades reais repetidas) estavam como negativos, e a rede estava superconfiante. Esses descartes passaram a positivos e a nota foi calibrada: Goyazes 56%, Zurich 70%, Mapfre 68%, residência artística no exterior 29%.

## 6. Conselho de 7 lentes

1. **Extremamente pessimista (chief engineer):** "1.042 rótulos é pouco e enviesado pelo que a validação já viu; a rede vai premiar o que se parece com o passado e punir o novo. Livros de programas que nunca passaram pela validação (Goyazes, Mapfre) ficam com nota de extrapolação."
2. **Pessimista (staff engineer):** "O livro-razão e o índice crescem a cada ciclo num repositório que já tem 1,5 GB. A resolução de entidades por blocagem perde pares cujos termos raros diferem (sinônimos, siglas)."
3. **Levemente pessimista (professor de computação):** "A temperatura de 6,75 mostra que a rede crua era muito confiante; com mais dados, regularização e calibração devem ser refeitas, não fixadas."
4. **Neutro (CTO):** pondera abaixo.
5. **Levemente otimista (professor):** "Transformar as regras em rotuladores aproveita meses de conhecimento do sistema sem descartá-lo; a rede só aprende o que as regras não conseguem separar."
6. **Otimista (staff engineer):** "A linha comum acaba com a perda silenciosa: o que falha vai à fila, o que muda de etapa vai ao razão, o que se repete vira corroboração."
7. **Extremamente otimista (chief engineer):** "Com aprendizado ativo, cada decisão sua melhora a rede, que reordena a fila, que gera decisões melhores — o sistema passa a aprender sozinho com o titular."

**Síntese do neutro — parâmetros de qualidade e mitigação de riscos:**
- A nota da rede é **apoio, nunca filtro** (coerente com identificar → qualificar). Nenhum livro é excluído por nota.
- **Treino semanal** com validação cruzada; a nota só é usada se a AUC fora da amostra ficar ≥ 0,80 (abaixo disso, o relatório avisa).
- **Rótulos suspeitos** (a rede contradiz a decisão com > 90%) vão à revisão — corrige o ruído dos rótulos.
- **Armazenamento:** índice compactado (gzip); livro-razão mensal compactado; reavaliar a reescrita do histórico do Git (pendência antiga).
- **Entidades:** a blocagem é conservadora (não junta errado); a evolução natural é embeddings (sentence-transformers) quando houver máquina.
- **Medida de sucesso da linha:** oportunidades validadas como reais por canal e por semana — não o volume de registros.

## 7. Próximos passos recomendados

1. Validar primeiro os 104 pendentes que a rede aponta como prováveis reais (fila em `docs/dados/rede_neural.json`).
2. Aplicar os planos aos 30 canais sem rendimento — começar pelos de maior custo (fontes 260 com 20+ leituras).
3. Ligar o Interceptador à fila de reprocessamento (62 registros com link de buscador).
4. Unificar os dois léxicos dos livros (bloco `busca` e chave de acionamento).
