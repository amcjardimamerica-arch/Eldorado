# Arquitetura de busca — decisão de 20/09/2026

## O que o titular pediu
Motores que evoluam a cada busca, aumentem a biblioteca e o léxico, com finalidades separadas
(descoberta × recorrência), empresas dos motores 27/28 virando rotas, e um sistema de código
aberto, leve em disco, eficiente e automatizável para operar a busca e guardar tudo compacto.

## Opções avaliadas (código aberto, pouco disco)
| opção | disco | serviço? | veredito |
|---|---|---|---|
| **SQLite FTS5** | 0 (embutido no Python) | não | **escolhido** — BM25, prefixo, frase, um arquivo |
| Tantivy (Rust) | ~10 MB wheel | não | mais rápido, sem ganho real em 70 mil fichas; compilação frágil no CI |
| Whoosh | ~1 MB | não | puro Python, ~10× mais lento que FTS5 |
| Meilisearch / Typesense | 100–300 MB | sim | processo servidor — descartados |
| Elasticsearch / OpenSearch | >500 MB + JVM | sim | descartados |
| **zstd** (compressão) | 5 MB | não | **escolhido** — 2–4× melhor que gzip em JSON/texto, dicionário treinado no acervo |
| **rapidfuzz** (dedup) | 3 MB | não | **escolhido** — similaridade de título para colapsar reapresentações |
| trafilatura (extração de texto) | 150 KB + lxml 6 MB | não | opcional para a próxima fase (leitura de páginas HTML) |

## O que foi implantado
- `src/empresas_rotas.py` — 52 empresas dos motores 27/28 → 310 rotas (site, páginas de RSE,
  instituto próprio, portais do terceiro setor, Salic, descoberta de domínio). Alimentam o motor
  `plat-empresas-editais-incentivados`.
- `src/finalidade_motores.py` — 22 motores de DESCOBERTA, 3 de INSUMO, 1 de RECORRÊNCIA com 135
  rotas (cadência por estado: aberta 2 d, encerrada 30 d, época de reabertura 1 d). ESPALHAMENTO:
  21 financiadores de editais validados entraram no catálogo pela curadoria.
- `src/aprendizado_lexico.py` — léxico que aprende: 80 termos positivos e 80 vetos promovidos por
  estatística (positivo: ≥3 aprovados e 0 reprovados; veto: ≥5 reprovados e 0 aprovados), com poda de
  artefatos de portal e ids que sustentam cada termo. Soma-se à camada 1 de todo motor de descoberta.
- `src/acervo_compacto.py` — `biblioteca_alexandria/acervo.sqlite`: 17.088 documentos em 12,8 MB,
  busca em ~3 ms, fichas e textos comprimidos com zstd (dicionário treinado). Regenerado no CI a cada
  saída; não versionado (evita 12 MB por commit no histórico).

## O que "inteligência generativa" significa aqui, honestamente
Não há modelo de linguagem rodando dentro do pipeline — isso exigiria GPU ou centenas de MB, contra o
critério de disco. A inteligência do sistema é estatística e auditável (léxico que aprende, dedup,
recorrência por estado) e a leitura semântica pesada fica com o agente Claude (rotina de domingo e
o pacote do Desktop com Opus 5), que devolve o resultado pelo mesmo canal de sempre.
