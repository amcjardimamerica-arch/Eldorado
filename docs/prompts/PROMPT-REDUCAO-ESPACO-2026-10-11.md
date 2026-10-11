# Eldorado · Redução de espaço e melhoria de acesso aos dados · 11/10/2026

## Finalidade
Reduzir o espaço ocupado pelo Eldorado e melhorar o acesso aos dados **sem perder nenhuma informação nem funcionalidade**, com **backup verificado antes** de qualquer remoção.

## Regras invioláveis
1. **Backup antes de tudo**, verificado; nenhuma remoção sem o backup confirmado.
2. **Nada que o sistema lê é removido.** Antes de propor a saída de um arquivo, conferir no código (`src/`, `scripts/`, fluxos em `.github/workflows/`, painel `docs/dashboard.html`) se alguém o lê.
3. **Remover = arquivo frio:** o que sai do repositório vai empacotado sem perda (tar.xz, SHA-256 de cada arquivo) para a Release do GitHub (e para o Drive quando ligado) e fica no manifesto, restaurável arquivo a arquivo. Só lixo regenerável (cache, `__pycache__`, logs de execução) é apagado sem pacote.
4. **PDFs:** vão para o Drive e só saem do repositório com o Drive conferido (regra `exige_drive`).
5. **Histórico do Git não é reescrito** sem autorização expressa da titular (é irreversível).
6. **Uma etapa de cada vez**; a próxima só começa quando a anterior estiver concluída e conferida.

## Etapas
1. **Backup** — marca (tag) imutável do estado atual da `main` + pacote verificado dos arquivos que vão sair (arquivo frio). Conferir que a marca existe no GitHub.
2. **Medição** — tamanho no GitHub (com histórico) e dos arquivos atuais; limites aplicáveis (GitHub: repositório recomendado < 1 GB e < 5 GB; arquivo < 100 MB; GitHub Pages: site publicado < 1 GB; disco do executor das Actions ≈ 14 GB livres); volume por pasta, por tipo e os maiores arquivos.
3. **Inventário de uso** — para cada grande volume: o que é, quem lê, com que frequência é regravado, se é regenerável.
4. **Classificação** — (a) sistema em uso: fica; (b) regenerável sem valor (cache, `__pycache__`, logs): apaga e passa a ser ignorado pelo Git; (c) histórico de uso esporádico: arquivo frio; (d) PDFs: Drive.
5. **Execução** — aplicar (b) e configurar (c) e (d) no arquivo frio; rodar o arquivo frio; conferir o manifesto e que nenhum arquivo em uso saiu (testes).
6. **Melhoria de acesso e de crescimento** — medidas para o repositório não voltar a crescer (regravação de arquivos grandes, publicação do painel) e para o painel carregar mais rápido.
7. **Parecer final** — antes/depois, o que saiu, onde está o backup, como restaurar, e o que depende da titular.
