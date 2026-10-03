# Prompt de implantação — coleta dos 3 anos INT (para outro chat com acesso de escrita ao GitHub)

1. Crie a branch `claude/coleta-3-anos-int-2026-10-03` a partir da `main` do repositório Eldorado.
2. Copie, preservando caminhos, os arquivos deste pacote:
   - `dados/coleta_3_anos/entrada/int_2026-10-03.json` (8 edições provadas + observações dos 41 livros)
   - `dados/coleta_3_anos/fila_int.json` (fila remontada; se já existir uma fila oficial, mantenha a oficial)
   - `docs/relatorios/COLETA-3-ANOS-INT-2026-10-03.md`
3. Se existir `src/selo_livros.py`, rode `python -m src.selo_livros` (incorpora as edições e recalcula os selos; idempotente).
   O livro `op-89f2538b8946` deve ir a ouro; `op-b945005df31a`, `op-5e28540d3e9d`, `op-0e162fb94284`, `op-a1a803e05f4b` e `op-ee56b31416f1` ficam com 1 edição (2026).
4. Corrija os livros `op-91c2f4f3673b`, `op-7539f8f6dea1`, `op-e7745f20733f` (credenciamentos do PNCP) para a geografia correta (não INT).
5. Junte os duplicados: `op-124d3e34e79a` → `op-ee56b31416f1`; `op-83fd629ad336` → `op-0e162fb94284`.
6. Rode `python -m unittest discover -s tests` e `python scripts/verificar_privacidade.py`; abra o Pull Request e envie o link.

## Atualização final (03/10/2026)
O pacote agora traz: `dados/coleta_3_anos/12_itens_int/*.json` (41 livros, 12 pontos cada), `docs/relatorios/coleta_int/*.md` (relatório preditivo por oportunidade) e `entrada/int_2026-10-03.json` com IFCD e CJRF. Passos: copiar para o repositório, rodar `python -m src.selo_livros`, testes e `scripts/verificar_privacidade.py`, commit em `claude/coleta-3-anos-int-2026-10-03` e PR.
