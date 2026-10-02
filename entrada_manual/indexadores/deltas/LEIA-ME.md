# Deltas da coleta no computador do titular

A ponte Brasil escolhida pelo titular (02/10/2026) é o computador dele. A cada 3 horas, das 06:10 às 21:10, o
`scripts/coleta_brasil.py` lê ali os sites que recusam IP estrangeiro e grava aqui um arquivo `brasil-AAAAMMDD-HHMMSS.json`
com o que leu.

O envio dispara o fluxo **16 · Motores indexadores**, que aplica os arquivos em ordem sobre o main mais novo e os apaga
no mesmo commit. Arquivo novo nunca conflita no git: nada do que a nuvem gravou no meio tempo se perde.

Ninguém precisa mexer nesta pasta.
