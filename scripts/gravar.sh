#!/usr/bin/env bash
# Grava o trabalho no repositório: os eventos sempre (texto, pequeno); o banco uma vez por dia, ou quando pedido
# (o Git guarda uma cópia inteira do binário a cada gravação). Usado pelo fluxo e pelo funcionamento permanente.
# Uso: scripts/gravar.sh [forcar_banco: true|false]
set -u
git config user.name "Eldorado"
git config user.email "eldorado@users.noreply.github.com"
git add eventos/
[ -d verificacao ] && git add verificacao/      # os lotes ao Chrome e os vereditos importados
ultimo=$(git log -1 --format=%ct -- dados/ 2>/dev/null || echo 0)
if [ "${1:-false}" = "true" ] || [ $(( $(date +%s) - ${ultimo:-0} )) -gt 72000 ]; then
  git add dados/
  echo "banco incluído (instantâneo)"
fi
if git diff --cached --quiet; then echo "nada a gravar"; exit 0; fi
git commit -q -m "Eldorado: trabalho até $(date '+%d/%m/%Y %H:%M')"
# O banco é binário e não se mescla: num conflito (outra gravação mexeu nele), vale a versão local (-X theirs: no rebase,
# "theirs" é o commit local reaplicado). É seguro: o banco converge pelos eventos (nomes únicos, nunca conflitam), e a
# próxima execução aplica, de forma idempotente, os eventos das outras gravações. Os eventos nunca se perdem (23/10/2026).
for i in 1 2 3; do
  if git pull -q --rebase -X theirs --autostash origin main && git push -q origin main; then exit 0; fi
  git rebase --abort 2>/dev/null
  sleep $((i * 10))
done
exit 1
