# Auditoria dos bancos de dados paralelos — 16/10/2026

**Regra da titular:** o único banco de dados do Eldorado são os LIVROS. Todo dado de oportunidade (abertas, prazos, dados do edital, links, checklist, marcações de IA, análises de cada etapa, coleta histórica de 3 anos, complementos dos pilotos) vive no livro da oportunidade. Oportunidade aberta com livro acrescenta as informações do edital atual às anteriores — o edital atual sempre vale. Oportunidade sem livro ganha um livro com todas as informações levantadas. É proibido criar dados fora dos livros.

## Resultado

- 35.279 arquivos e 378 MB fora do catálogo de livros, em 1.064 grupos.
- A · dado de oportunidade: 15.794 arquivos, 243 MB → levar para os livros e apagar.
- ? · a revisar (sobretudo 18.475 aprendizados dos pilotos): 19.047 arquivos, 29,5 MB.
- C · vitrine do site (docs/dados): 89 arquivos, 61 MB → gerada SÓ a partir dos livros, nunca lida de volta.
- D · dados da própria associação (documentos da AMC): 298 arquivos, 9 MB → decisão da titular.
- B · controle operacional (cursores, filas que apontam para livros): 50 arquivos, 5 MB → fica, mínimo.

## Desenho

Um arquivo por livro (biblioteca_alexandria/livros/<livro>.json); o catálogo vira só o índice. Absorver 243 MB num arquivo único o tornaria inutilizável.

## Grupos (maiores)

| Classe | MB | Arquivos | Grupo |
|---|---|---|---|
| C vitrine | 57.6 | 88 | `docs/dados` |
| A oportunidade | 32.6 | 2102 | `biblioteca_alexandria/oportunidades` |
| A oportunidade | 20.3 | 89 | `dados/farol/editais` |
| A oportunidade | 15.6 | 76 | `biblioteca_alexandria/base` |
| A oportunidade | 15.1 | 7 | `estado/cartorio` |
| A oportunidade | 14.4 | 4360 | `dados/coleta_3_anos/relatorios` |
| ? revisar | 14.0 | 18475 | `estado/piloto/aprendizados` |
| A oportunidade | 14.0 | 3523 | `estado/piloto/briefings` |
| A oportunidade | 13.9 | 2587 | `dados/editais/extraidos` |
| A oportunidade | 11.5 | 4 | `biblioteca_alexandria/historico` |
| D associação | 9.0 | 206 | `dados/associacoes/amc-jardim-america` |
| A oportunidade | 8.5 | 10 | `dados/editais` |
| A oportunidade | 8.3 | 8 | `dados/oportunidades` |
| ? revisar | 8.0 | 1 | `dados/historico_export.jsonl.gz` |
| A oportunidade | 7.5 | 54 | `estado/piloto` |
| A oportunidade | 6.7 | 269 | `biblioteca_alexandria/empresas` |
| A oportunidade | 6.7 | 2 | `biblioteca_alexandria/previsoes` |
| A oportunidade | 5.2 | 15 | `dados/oportunidades/pareceres_livros` |
| A oportunidade | 5.2 | 10 | `dados/coleta_3_anos` |
| A oportunidade | 5.0 | 3 | `estado/cartorio/avaliacao` |
| A oportunidade | 4.7 | 7 | `dados/oportunidades/validacao_mapa` |
| A oportunidade | 3.9 | 3 | `estado/esteira` |
| C vitrine | 3.2 | 1 | `docs/dados/doadoras` |
| A oportunidade | 3.0 | 16 | `estado/interceptador/relatorios` |
| A oportunidade | 2.7 | 7 | `biblioteca_alexandria/arquivo_frio` |
| B controle | 2.3 | 1 | `estado/achados_vistos.json` |
| A oportunidade | 2.2 | 7 | `estado/indexadores` |
| A oportunidade | 2.1 | 45 | `dados/coleta_3_anos/lotes12_out` |
| ? revisar | 1.9 | 33 | `biblioteca_alexandria/pareceres` |
| ? revisar | 1.7 | 11 | `dados/empresas/destinacoes` |
| A oportunidade | 1.6 | 14 | `dados/coleta_3_anos/ouro` |
| A oportunidade | 1.6 | 1 | `estado/opressores.json` |
| A oportunidade | 1.5 | 35 | `dados/coleta_3_anos/entrada` |
| A oportunidade | 1.5 | 11 | `dados/revisoes/fila_chrome_2026_10_11` |
| A oportunidade | 1.0 | 16 | `dados/revisoes/abertas_p3_br_privadas_2026_10_10` |
| A oportunidade | 0.9 | 5 | `dados/empresas/go` |
| A oportunidade | 0.8 | 7 | `biblioteca_alexandria/fontes` |
| A oportunidade | 0.8 | 2 | `dados/revisoes/abertas_p2_br_publicas_2026_10_10` |
| A oportunidade | 0.8 | 5 | `dados/opressores/parametros` |
| A oportunidade | 0.8 | 5 | `estado/interceptador` |
| A oportunidade | 0.8 | 26 | `dados/coleta_3_anos/lotes12c_out` |
| ? revisar | 0.7 | 2 | `estado/linha` |
| A oportunidade | 0.6 | 1 | `estado/varredura_referencia` |
| A oportunidade | 0.6 | 14 | `dados/coleta_3_anos/lotes12b_out` |
| A oportunidade | 0.6 | 1 | `estado/fila_verificacao.json` |
| A oportunidade | 0.6 | 1 | `estado/curadoria_links.json` |
| ? revisar | 0.6 | 92 | `dados/editais/textos` |
| A oportunidade | 0.5 | 1 | `estado/saneamento_motores.json` |
| A oportunidade | 0.5 | 3 | `dados/financiadores/querido-diario` |
| B controle | 0.5 | 1 | `estado/esquadra_diario.json` |
| A oportunidade | 0.5 | 6 | `estado/emendas` |
| A oportunidade | 0.5 | 1 | `estado/diario_uniao.json` |
| A oportunidade | 0.5 | 2 | `biblioteca_alexandria/emendas/emenda-federal` |
| ? revisar | 0.4 | 1 | `estado/rede_neural` |
| B controle | 0.4 | 5 | `estado/rotas` |
| A oportunidade | 0.4 | 37 | `biblioteca_alexandria/leis` |
| A oportunidade | 0.4 | 16 | `dados/revisoes/abertas_p1_go_2026_10_10` |
| ? revisar | 0.4 | 5 | `estado/amostra_validacao` |
| B controle | 0.4 | 1 | `estado/fila_retentativa.json` |
| A oportunidade | 0.3 | 1 | `estado/agregadores` |
| B controle | 0.3 | 1 | `estado/esquadra.json` |
| A oportunidade | 0.3 | 3 | `estado/pilotos` |
| B controle | 0.3 | 4 | `estado/comando` |
| A oportunidade | 0.3 | 27 | `dados/coleta_3_anos/lotes12c` |
| B controle | 0.3 | 1 | `estado/rotas_monitoramento.json` |
| ? revisar | 0.2 | 2 | `estado/aprendizado` |
| A oportunidade | 0.2 | 58 | `estado/fontes` |
| ? revisar | 0.2 | 9 | `estado/pilotos/historico` |
| ? revisar | 0.2 | 93 | `estado/interceptador/dossies` |
| A oportunidade | 0.2 | 3 | `estado/pncp` |

## Ligação aos livros (amostra)

| Banco | Registros ligados |
|---|---|
| `estado/esteira` | 94% |
| `estado/piloto` | 94% |
| `dados/coleta_3_anos/ouro` | 81% |
| `dados/oportunidades/pareceres_livros` | 77% |
| `estado/cartorio` | 55% |
| `estado/interceptador/relatorios` | 55% |
| `estado/piloto/briefings` | 39% |
| `dados/editais` | 38% |
| `estado/indexadores` | 38% |
| `dados/editais/extraidos` | 29% |
| `biblioteca_alexandria/base` | 28% |
| `dados/farol/editais` | 1% |
| `biblioteca_alexandria/historico` | 0% |
| `biblioteca_alexandria/previsoes` | 0% — dados criados (estimativas sem fonte) |

## Execução (etapas)

1. Livro em arquivo próprio; catálogo vira índice.
2. Absorção: cada registro ligado entra no livro (o edital atual vale); oportunidade sem livro que passa nos portões ganha livro; o que não é oportunidade é descartado.
3. Remoção à força do grupo A e do grupo ? depois de absorvidos.
4. Conserto: cada módulo quebrado passa a ler e gravar só nos livros.
5. Trava permanente: a gravação do comando recusa dado de oportunidade fora dos livros.
