#!/usr/bin/env bash
# Grava o trabalho no repositório: os eventos sempre (texto, pequeno); o banco uma vez por dia, ou quando pedido.
# Uso: scripts/gravar.sh [forcar_banco: true|false]
#
# 25/10/2026: a gravação é feita numa ÁRVORE DE TRABALHO SEPARADA. Antes, o "git pull" da gravação trazia para o disco do
# ciclo em andamento o código e as configurações novas: o código antigo, já carregado, lia uma configuração nova e falhava
# (o nó do Espião: "metrica.esporadica: Extra inputs are not permitted"). Agora o ciclo em andamento nunca muda de versão:
# os dados são copiados para a árvore separada, enviados de lá, e a mudança de código entra só pela implantação (R09).
set -u
RAIZ=$(pwd)
ARVORE="${RUNNER_TEMP:-/tmp}/eldorado-gravacao"
git config user.name "Eldorado"
git config user.email "eldorado@users.noreply.github.com"
banco=false
ultimo=$(git log -1 --format=%ct -- dados/ 2>/dev/null || echo 0)
if [ "${1:-false}" = "true" ] || [ $(( $(date +%s) - ${ultimo:-0} )) -gt 72000 ]; then banco=true; fi

for i in 1 2 3 4; do
  git fetch -q origin main || { sleep $((i * 5)); continue; }
  git worktree remove -f "$ARVORE" 2>/dev/null; rm -rf "$ARVORE"
  git worktree add -q -f --detach "$ARVORE" origin/main || { sleep $((i * 5)); continue; }
  # os dados do ciclo (só dados: nunca o código nem as configurações)
  # o que o ciclo escreveu desde que começou (a marca .inicio_ciclo); sem a marca, tudo
  for pasta in eventos verificacao dados/ia; do
    [ -d "$RAIZ/$pasta" ] || continue
    if [ -f "$RAIZ/.inicio_ciclo" ]; then
      ( cd "$RAIZ" && find "$pasta" -type f -newer .inicio_ciclo -print0 | xargs -0 -r cp --parents -a -t "$ARVORE" )
    else
      mkdir -p "$ARVORE/$pasta" && cp -a "$RAIZ/$pasta/." "$ARVORE/$pasta/"
    fi
  done
  if [ "$banco" = "true" ]; then
    for f in biblioteca.db cerebro.db; do [ -f "$RAIZ/dados/$f" ] && cp "$RAIZ/dados/$f" "$ARVORE/dados/$f"; done
    echo "banco incluído (instantâneo)"
  fi
  # a consolidação dos bancos (R08): as remoções dos bancos paralelos
  ( cd "$ARVORE" && git ls-files dados/motores dados/especial.db 2>/dev/null | while read -r f; do [ -e "$RAIZ/$f" ] || git rm -q --cached "$f" 2>/dev/null; done )
  cd "$ARVORE"
  git add eventos/ 2>/dev/null; [ -d verificacao ] && git add verificacao/; [ -d dados/ia ] && git add dados/ia/
  [ "$banco" = "true" ] && for f in dados/biblioteca.db dados/cerebro.db; do [ -f "$f" ] && git add "$f"; done
  if git diff --cached --quiet; then echo "nada a gravar"; cd "$RAIZ"; git worktree remove -f "$ARVORE" 2>/dev/null; exit 0; fi
  git commit -q -m "Eldorado: trabalho até $(date '+%d/%m/%Y %H:%M')"
  if git push -q origin HEAD:main; then
    cd "$RAIZ"; git worktree remove -f "$ARVORE" 2>/dev/null
    # o site acompanha o sistema (R09): a gravação automática não aciona outros fluxos, mas o despacho direto aciona
    if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${GITHUB_REPOSITORY:-}" ]; then
      curl -s -o /dev/null -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/actions/workflows/painel.yml/dispatches" -d '{"ref":"main"}' || true
    fi
    exit 0
  fi
  cd "$RAIZ"; sleep $((i * 10))                     # outra gravação entrou antes: refaz sobre a versão nova
done
cd "$RAIZ"; git worktree remove -f "$ARVORE" 2>/dev/null
exit 1
