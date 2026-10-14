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

## 2 · O que o diagnóstico já confere
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
