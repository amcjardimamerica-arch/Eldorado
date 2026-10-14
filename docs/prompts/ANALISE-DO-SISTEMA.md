# "Analise o sistema" · como o Claude faz (desde 14/10/2026)

Quando a titular pedir **"Analise o sistema"** (ou "análise do sistema", "diagnóstico do sistema"), use o
**diagnóstico único de backend** — não abra sistema por sistema nem crie página, quadro ou apresentação.

## 1 · Rodar a análise com correção (na produção, com os dados do momento)
Dispare o fluxo **36 · Análise do sistema** (`.github/workflows/analise-sistema.yml`) com `corrigir=sim`:
`POST /repos/amcjardimamerica-arch/Eldorado/actions/workflows/analise-sistema.yml/dispatches`
corpo `{"ref":"main","inputs":{"corrigir":"sim"}}`. Espere terminar (5 a 25 min; ele divide o grupo com o ciclo dos
motores e pode aguardar a vez). Depois baixe a `main` e leia:
- `estado/diagnostico_sistema.md` — resumo (antes → depois, etapas da correção, oportunidades, sistemas, integração,
  problemas);
- `estado/diagnostico_sistema.json` — completo (listas com exemplos de cada problema).
Alternativa local (sem gravar na produção): `python -m src.diagnostico_sistema --corrigir` num clone da `main`.

## 2 · O que o diagnóstico confere (2ª versão, 14/10/2026)
- **Cumprimento da finalidade (0–100%) de cada sistema** contra a meta do que foi projetado — motores (todo ativo lê
  na cadência), maestro (cobertura do dia), rede neural (AUC ≥ 0,85), Biblioteca (toda aberta aplicável com livro
  existente), validação, site oficial, prazo, Cartório (12/12), tela e fichas, integração, fluxos automáticos e
  execução sem falha silenciosa — e um **índice geral**.
- **Execução: parâmetros de tudo que roda** — cada fluxo do GitHub com a cadência esperada (lida dos crons), a última
  execução, a taxa de sucesso e o estado (ok, atenção, atrasado, falha); e as **falhas silenciosas** (etapas que rodam
  com "|| echo falhou") lidas nos registros das últimas execuções. Fora do GitHub os registros podem não ser legíveis:
  então o diagnóstico diz "sem dados", nunca "100%".
- **Conferência da sala de controle:** cada indicador recalculado na fonte e comparado ao que a sala mostra
  (divergências), indicadores sem leitura, estados incoerentes com a faixa e **sugestões de apresentação** (sistemas
  que existem e não aparecem na sala).
- **Regra de abrangência (titular, 14/10):** só Goiás tem oportunidades e livros MUNICIPAIS; de outros estados,
  só estaduais (e nacionais/internacionais). O diagnóstico aponta municipal de outro estado ainda aberta (corrige
  refazendo o repositório, que a descarta) e livro municipal de outro estado no catálogo (corrige pela curadoria).
- **Oportunidades, uma a uma:** tem livro? o livro existe no catálogo? (sem livro "por regra" — dispensa registrada —
  não é problema) · validada? · site oficial? · prazo? · prazo vencido ainda aberta? · aparece na tela e na ficha? ·
  decisão da titular aplicada?
- **Sistemas:** motores (funcionando, em falha, leitura parcial), maestro, rede neural (AUC, treino), Cartório,
  Pilotos, saúde (arquivos, frescor, coerência, fluxos do GitHub), auditoria cega, sala de controle.
- **Integração:** repositório × tela × fichas × sala de controle com as mesmas contagens; idade de cada dado;
  decisões aplicadas.
- **Correção automática (em sequência):** decisões → livros → repositório → tela → fichas → sala de controle → saúde.

## 3 · Depois de ler
1. Conselho de 7 (perfil de tecnologia da titular) sobre os problemas que **sobraram** — especialmente os sem
   correção automática (motor em falha, fluxo do GitHub falhando, divergências que persistem após refazer).
2. Investigar a causa de cada um e implantar as melhorias (PR com testes e comparação com a `main`), como de costume.
3. Relatar em linguagem simples: o que estava errado, o que foi corrigido sozinho, o que foi corrigido no código e o
   que fica pendente.
