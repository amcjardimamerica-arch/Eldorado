# Plano de compactação dos eventos (C-23, manutenção de 16/11/2026)

**Situação em 17/11/2026:** `eventos/` com 1,2 GB em 10.932 arquivos `.jsonl`, nenhum compactado; cresce cerca de 33 MB
por dia. O limite de 5 GB do repositório chega em cerca de 115 dias. `operacao/` tem mais 129 MB.

**O cuidado:** o aplicador registra os arquivos já aplicados pelo NOME. Compactar ou renomear um arquivo antigo sem tratar
isso pode fazê-lo ser reaplicado (os eventos são idempotentes na maior parte, mas não todos: `incentivo` não se regrava,
`execucao.iniciada` insere).

**O plano, em três passos (cada um com trava):**
1. O aplicador passa a ler também `.jsonl.gz` e a reconhecer o arquivo compactado pelo mesmo nome-base do original
   (`x.jsonl.gz` = `x.jsonl`), de modo que um arquivo já aplicado continue pulado depois de compactado.
   Trava: «o arquivo compactado de um já aplicado não é reaplicado».
2. Um passo semanal compacta, por dia, os arquivos de eventos com mais de 30 dias e já aplicados (um `.jsonl.gz` por dia,
   com o índice dos nomes originais), e os arquivos de `operacao/` com mais de 14 dias.
   Trava: «nenhum evento se perde na compactação» (a contagem e o conteúdo antes e depois).
3. O mostrador do tamanho do repositório na Sala (faixa: verde até 3 GB, atenção até 4 GB, alarme acima).

**Ganho esperado:** o JSON de eventos compacta de 8 a 12 vezes — de 1,2 GB para cerca de 120 MB, e o crescimento diário de
33 MB para cerca de 4 MB depois de 30 dias.
