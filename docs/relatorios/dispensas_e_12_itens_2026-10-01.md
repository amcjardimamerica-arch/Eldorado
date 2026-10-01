# Biblioteca: os 12 itens de cada livro e a análise de dispensa (01/10/2026)

Refeito sobre o main de 01/10 (commit `ffd910a0b2`), com o vocabulário atual: **Biblioteca**, **livro de oportunidade** (o que antes era o "motor opressor") e **livro de leis**. Nomes internos de arquivos e campos (`estado/opressores.json`, `src/parametros_opressores.py`, `opressor` no fluxo) seguem como no glossário do `AGENTS.md`.

## O que foi pedido

Preencher os 12 itens de cada livro com o que ainda faltava e analisar se cada oportunidade pode ter dispensa de algum deles.

## O que foi feito

**1. Diagnóstico.** Dos livros com edital (vigente, histórico ou programa permanente), 58 tinham 211 itens "não localizado". Outros 79 livros não tinham parâmetro nenhum. No mapa de oportunidades, 136 oportunidades somavam 735 itens "em falta", em parte por defeito do código: o checklist ignorava os 12 itens que a validação individual já gravava e os parâmetros do livro.

**2. Coleta na fonte oficial.** Oito pesquisadores em paralelo: cinco para os 79 livros novos e três para completar 57 livros com itens faltando. Só site oficial do órgão ou do patrocinador, nenhuma data ou valor estimado, PDF checado contra prompt injection (nenhuma injeção encontrada).

**3. Virada de prazo.** 15 inscrições que venceram em 29 e 30/09 saíram de "vigente" e foram para o histórico do livro. Dos registros desta rodada, 33 seguem vigentes (V) em 01/10 e 19 deles encerram em até uma semana, até 07/10.

**4. Matriz de dispensa por tipo de recurso** (`config/dispensas_por_regime.json` e `src/dispensas_itens.py`). Sete regimes: edital com seleção, fluxo contínuo, emenda parlamentar, incentivo fiscal, destinação judicial, doação de bens e patrocínio privado.

**5. Correção do checklist** (`src/fluxo_oportunidades.py`) e dois estados novos no painel (`prov` e `ref`). Os livros que já tinham os 12 itens por outra verificação também ganham a análise de dispensa.

**6. Dados corrigidos para o formato atual.** O arquivo `parametros_2026-10-01.json` foi conferido contra o catálogo de hoje: todos os 142 registros apontam para livros existentes. Um registro ainda trazia o identificador antigo (`nova-786876e1f612`) e passou ao atual (`op-0d2ab7638fd7`), mantendo o antigo em `id_pesquisado`. A fila para o navegador do computador foi refeita com os livros de hoje.

## Resultado

| | Antes | Depois |
|---|---:|---:|
| Itens "em falta" no mapa de oportunidades | 735 | 571 |
| Itens confirmados na validação individual | 56 | 125 |
| Itens dispensados pelo próprio edital | 29 | 46 |
| Itens ainda sem leitura | 132 | 109 |
| Oportunidades com 12 de 12 itens | 3 | 18 |
| Oportunidades com 9 ou mais de 12 | 25 | 36 |
| Livros ligados | 324 | 298 (26 desligados: não são recurso para OSC) |
| Livros sem nenhum parâmetro | 90 | 11 (criados pelos robôs depois da pesquisa) |
| Livros com os 12 itens fechados | 97 | 117 |

Parâmetros dos livros hoje: 1.672 confirmados, 109 dispensados pelo edital, 90 "não informado no edital" e 205 "não localizado".

**Os 79 livros novos:** 17 vigentes (V), 1 histórico (A), 26 não são recurso para OSC (D) e 35 pendentes (P). Entre os D estão 11 do BNDES (linhas de crédito e programas que não são chamada para OSC), notícias, bolsas para pessoa física e páginas de agregador. **Os 57 completados:** 25 vigentes, 29 históricos e 3 permanentes.

## Dispensa: o que é confirmado e o que é só provável

**Dispensa confirmada** (estado `disp`): o próprio edital ou o regramento oficial diz que o item não existe ou não traz o dado. Conta como item feito.

**Dispensa provável** (estado `prov`, ponto de interrogação âmbar no painel): hipótese pelo tipo de recurso. **Não conta como item feito**, traz motivo, base e grau de confiança e só aparece em item que ainda falta.

| Tipo de recurso | Itens que podem ser dispensados | Confiança | Base |
|---|---|---|---|
| Edital com seleção | nenhum | n/a | em edital cultural, a Lei 14.903/2024, art. 9º, exige inscrição (mín. 5 dias úteis) e recurso (mín. 3 dias úteis): item faltando é falha do edital |
| Fluxo contínuo | Prazo de inscrição | média | Lei 14.903/2024, art. 6º (chamamento de fluxo contínuo, na cultura); credenciamento permanente em geral |
| Emenda parlamentar | Valor, Destinação, Resultado, Prazo de recurso, Anexos | alta | mapa já adotado em 28/09 (não há edital) |
| Incentivo fiscal | Prazo de recurso | baixa | o rito de recurso fica na norma do programa; texto da norma ainda por baixar |
| Destinação judicial / TAC | Valor, Prazo de recurso | baixa / média | ato do juízo ou do MP; Resolução CNJ 154/2012 e Ato PGJ 58/2025 ainda por baixar |
| Doação de bens | Valor | média | Portaria RFB 200/2022 |
| Patrocínio privado ou internacional | Prazo de recurso | média | regulamento privado não é obrigado a ter recurso |

Na prática, a pesquisa já fechou quase tudo que a matriz dispensaria: hoje há **10 dispensas prováveis no mapa de oportunidades e 10 nos livros**. O que ainda falta de verdade são **195 itens em 54 livros** e **571 itens no mapa**, concentrados em Resultado, Prazo de recurso, Prazo de inscrição, Requisitos e Valor. Esses itens existem no edital e só dependem de ler o PDF.

**Base legal verificada em 01/10 no Planalto:** Lei 14.903/2024, arts. 6º e 9º (vale só para fomento cultural, não para o MROSC em geral), e Lei 13.019/2014, art. 26 (edital com 30 dias de antecedência). **Não confirmei** o prazo de recurso da Lei 13.019 (arts. 58 a 60 não apareceram na leitura); por isso ele não entra como regra.

## Dois estados novos no checklist

- `prov`: dispensa provável (não conta como feito).
- `ref`: dado da edição de referência do livro que **não** foi confirmado como sendo o edital desta oportunidade (não conta como feito). Se o link da oportunidade for o mesmo edital do livro, o dado vira `val`. Hoje são 91 itens `ref`.

## O que não deu para fechar

A nuvem só abre páginas com WebFetch; a busca está desligada, o PNCP bloqueia e muitos PDFs de prefeitura voltam ilegíveis ou barrados por robots.txt. O navegador do computador está desconectado. Ficou pronta a **fila para o navegador local** (`dados/opressores/parametros/fila_navegador_local_2026-10-01.json`): 54 livros com itens exigidos faltando, 114 livros pendentes (44 deles por bloqueio de leitura) e 11 livros sem nenhum parâmetro.

## Pontos para o titular decidir

1. **Dois vigentes sem inscrição aberta de fato:** Arranjos Regionais FSA e Confins. Convém decidir se continuam como V ou passam a A.
2. **Livros duplicados** (o mesmo edital de Sobral aparece três vezes) e **páginas de livro erradas** (por exemplo, o livro de Itapeva/SP apontando para Itapeva/MG). As recomendações estão no campo `recomendacao` de cada registro.
3. **Dado suspeito já existente:** o Grupo Equatorial aparece com "Resultado 23/12/2025" em uma chamada de 2026. É anterior a esta rodada e veio do Interceptador; foi mantido, mas deve ser revisado.
4. **Ibermúsicas:** a notícia no site do programa diz que as convocatórias de 2026 fecham hoje, 01/10, às 23h59, sem listar edital específico. O livro foi marcado como D; a data não foi gravada por não ter edital como fonte.

## Conselho de 7 lentes

**Extremamente pessimista (staff engineer de infraestrutura).** Qualquer rótulo "provável" vira "confirmado" na cabeça de quem lê o painel, e a entidade deixa de pedir um documento que o edital exigia. Basta uma dispensa errada para custar um projeto. Além disso, 15 prazos mudaram em 48 horas: o dado envelhece mais rápido que a rotina.

**Pessimista (professora de engenharia de software).** A classificação do regime depende de campos do catálogo que já erram (o campo "nível" classificava prefeituras como privadas). Corrigi usando a esfera comprovada, mas o catálogo continua sendo ponto frágil. O estado `ref` pode gerar falsa sensação de cobertura.

**Levemente pessimista (CTO de plataforma de dados).** O painel só contava 5 estados e agora tem 7; quem exporta o checklist em outro formato pode contar errado. A pesquisa de nuvem rendeu pouco (36 de cerca de 211 itens), e a fila do navegador local é o que realmente fecha o ciclo.

**Neutro (conselheiro ponderador).** A mudança tem dois ganhos independentes: o checklist passou a usar dados que já existiam e estavam sendo jogados fora, e a dispensa passou a ser explícita, com base e confiança. O risco central é a leitura do "provável" como "confirmado". A salvaguarda estrutural já existe: `prov` e `ref` não entram na contagem de itens feitos, a matriz só age sobre item que falta, e o edital lido sempre prevalece. Parâmetros de qualidade: (a) dispensa de confiança "baixa" serve só de orientação, nunca para deixar de entregar documento; (b) toda dispensa provável precisa ser confirmada na leitura do edital antes da inscrição; (c) rodar a fila do navegador local na próxima reconexão.

**Levemente otimista (diretor de engenharia).** Os itens "em falta" caíram 22% sem nenhuma coleta nova, só por ler direito o que já havia, e as oportunidades com os 12 itens fechados foram de 3 para 18. O sistema agora explica por que um item não existe, em vez de marcá-lo como falha.

**Otimista (arquiteta de sistemas).** A matriz é um arquivo de configuração: cada regime novo (prêmio, bolsa, operação de crédito) entra sem mexer em código, e cada dispensa traz base e confiança auditáveis. Com a fila do navegador, o ciclo "ler PDF, fechar item" pode rodar sozinho nas próximas semanas.

**Extremamente otimista (pesquisador de ciência da computação).** O desenho separa dado, hipótese e referência, que é a base para o sistema aprender a prever a próxima edição: com os 12 itens da última edição e as dispensas do regime, a Biblioteca pode dizer, antes de o edital sair, quais documentos a entidade deve preparar.

**Decisão final do conselho:** aplicar. Manter `prov` e `ref` fora da contagem de itens feitos, tratar dispensa de confiança "baixa" apenas como orientação e priorizar a fila do navegador local.

## Arquivos

- `config/dispensas_por_regime.json`: matriz de dispensa por regime.
- `src/dispensas_itens.py`: classificação do regime e aplicação ao checklist e aos livros.
- `src/fluxo_oportunidades.py` e `src/parametros_opressores.py`: ligação ao fluxo.
- `docs/dashboard.html`: estados `prov` e `ref` e o tipo de recurso na ficha da oportunidade.
- `dados/opressores/parametros/parametros_2026-10-01.json`: 79 livros novos, 57 completados e 6 virados para histórico.
- `dados/opressores/parametros/fila_navegador_local_2026-10-01.json`: fila para o navegador do computador.
- `tests/test_dispensas_itens.py`: 18 testes novos.
