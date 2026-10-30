#!/usr/bin/env bash
# Grava o trabalho no repositório: os eventos sempre (texto, pequeno); o banco uma vez por dia, ou quando pedido.
# Uso: scripts/gravar.sh [forcar_banco: true|false]
#
# 29/10/2026 (titular): a gravação SEM CÓPIA DO REPOSITÓRIO. Antes, cada gravação (a cada 5 min) montava uma árvore de
# trabalho separada com o repositório inteiro (mais de 1 GB) e tinha 10 min de prazo: com a máquina ocupada pela IA, não
# cabia mais, e desde 28/10 15:18 nada foi gravado (e a gravação final levava os bancos de ~250 MB, acima do limite de
# 100 MB do GitHub). Agora o commit é montado direto no Git (um índice temporário sobre a versão do repositório, só com
# os arquivos novos): segundos, sem disco. Nenhum arquivo acima de 95 MB vai (o GitHub recusaria a gravação inteira); os
# bancos acima do limite ficam (o ciclo os reconstrói dos eventos ao começar: "eldorado aplicar"). Toda falha vira aviso
# visível (::error::), para nunca mais falhar às cegas.
#
# As regras de antes continuam: só os dados (nunca o código nem as configurações); só o que o ciclo escreveu desde a
# marca .inicio_ciclo; a R09: o arquivo de uma passagem começada e não terminada não é gravado; a R08: as remoções dos
# bancos paralelos.
set -u
RAIZ=$(pwd)
LIMITE=$((95 * 1024 * 1024))
git config user.name "Eldorado"
git config user.email "eldorado@users.noreply.github.com"
banco=false
ultimo=$(git log -1 --format=%ct -- dados/ 2>/dev/null || echo 0)
if [ "${1:-false}" = "true" ] || [ $(( $(date +%s) - ${ultimo:-0} )) -gt 72000 ]; then banco=true; fi
avisar() { echo "::error::gravação: $*"; }

# a lista dos arquivos a gravar (os caminhos relativos à raiz)
# a passagem dividida em partes (o diário abre <execução>-2.jsonl a partir de 60 MB) é vista inteira: todas as partes juntas
completo() { local b="${1%.jsonl}"; b="${b%-[0-9]*}"; local partes=("$b.jsonl" "$b"-[0-9]*.jsonl)
  ! cat "${partes[@]}" 2>/dev/null | grep -q '"execucao.iniciada"' || cat "${partes[@]}" 2>/dev/null | grep -q '"execucao.concluida"'; }
LISTA=$(mktemp)
for pasta in eventos verificacao dados/ia backups; do   # backups: a cópia dos livros (a cada 3 dias)
  [ -d "$RAIZ/$pasta" ] || continue
  if [ -f "$RAIZ/.inicio_ciclo" ]; then
    find "$pasta" -type f -newer .inicio_ciclo
  else
    find "$pasta" -type f
  fi
done | while read -r f; do
  if [ "${f#eventos/}" != "$f" ] && ! completo "$f"; then echo "em andamento (não gravado): $f" >&2; continue; fi
  echo "$f"
done > "$LISTA"
if [ "$banco" = "true" ]; then
  for f in dados/biblioteca.db dados/cerebro.db; do [ -f "$f" ] && echo "$f" >> "$LISTA"; done
fi

for i in 1 2 3 4; do
  if ! saida=$(git fetch -q origin main 2>&1); then avisar "a busca da versão do repositório falhou ($saida)"; sleep $((i * 5)); continue; fi
  base=$(git rev-parse FETCH_HEAD)
  INDICE=$(mktemp); rm -f "$INDICE"
  export GIT_INDEX_FILE="$INDICE"
  git read-tree "$base" || { avisar "não leu a versão $base"; unset GIT_INDEX_FILE; sleep $((i * 5)); continue; }
  pulados=0; n=0
  while read -r f; do
    [ -f "$f" ] || continue
    tam=$(stat -c %s "$f")
    if [ "$tam" -gt "$LIMITE" ]; then
      pulados=$((pulados + 1))
      case "$f" in dados/*.db) echo "banco acima de 95 MB não vai ao repositório (o ciclo o reconstrói dos eventos): $f ($((tam / 1048576)) MB)";;
                   *) avisar "arquivo acima de 95 MB não gravado (o GitHub recusaria a gravação inteira): $f ($((tam / 1048576)) MB)";; esac
      continue
    fi
    blob=$(git hash-object -w "$f") && git update-index --add --cacheinfo "100644,$blob,$f" && n=$((n + 1))
  done < "$LISTA"
  # a consolidação dos bancos (R08): os bancos paralelos que não existem mais saem do repositório
  git ls-files dados/motores dados/especial.db 2>/dev/null | while read -r f; do [ -e "$RAIZ/$f" ] || git update-index --force-remove "$f"; done
  # 29/10/2026: o veredito que o ciclo importou e moveu para importados/ sai da pasta de entrada no repositório (senão o
  # ciclo seguinte o importaria de novo, duplicando as certidões)
  # 30/10/2026: o lote que o sistema apagou (as partes que sobraram, os dias anteriores) sai do repositório; só o sistema
  # gera os lotes, então o arquivo ausente no ciclo é um lote apagado
  git ls-files "verificacao/lotes/*.json" 2>/dev/null | while read -r f; do [ -e "$RAIZ/$f" ] || git update-index --force-remove "$f"; done
  git ls-files "verificacao/vereditos/*.json" 2>/dev/null | grep -v "/importados/" | while read -r f; do
    # 30/10/2026: só sai quando JÁ FOI IMPORTADO (a cópia em importados/ no ciclo); o veredito recém-enviado ainda não está na
    # pasta local (o ciclo o traz na passagem seguinte) e era apagado sem ser importado
    [ -e "$RAIZ/$f" ] || [ ! -e "$RAIZ/verificacao/vereditos/importados/$(basename "$f")" ] || git update-index --force-remove "$f"; done
  arvore=$(git write-tree)
  if [ "$arvore" = "$(git rev-parse "$base^{tree}")" ]; then
    echo "nada a gravar"; unset GIT_INDEX_FILE; rm -f "$INDICE" "$LISTA"; exit 0
  fi
  commit=$(git commit-tree "$arvore" -p "$base" -m "Eldorado: trabalho até $(date '+%d/%m/%Y %H:%M')")
  unset GIT_INDEX_FILE; rm -f "$INDICE"
  if saida=$(git push -q origin "$commit:refs/heads/main" 2>&1); then
    echo "gravado: $n arquivo(s)$([ "$banco" = "true" ] && echo ' · banco incluído quando abaixo do limite')"
    rm -f "$LISTA"
    # o site acompanha o sistema (R09): a gravação automática não aciona outros fluxos, mas o despacho direto aciona
    if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${GITHUB_REPOSITORY:-}" ]; then
      curl -s -o /dev/null -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/actions/workflows/painel.yml/dispatches" -d '{"ref":"main"}' || true
    fi
    exit 0
  fi
  echo "o envio foi recusado na tentativa $i: ${saida:0:300}"; sleep $((i * 10))   # outra gravação entrou antes: refaz sobre a versão nova
done
avisar "não gravou depois de 4 tentativas (o último motivo está acima)"
rm -f "$LISTA"
exit 1
