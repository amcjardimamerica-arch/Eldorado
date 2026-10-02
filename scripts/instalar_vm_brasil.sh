#!/usr/bin/env bash
# INSTALA O ELDORADO NUMA MÁQUINA VIRTUAL NO BRASIL (Ubuntu/Debian) — a "ponte" que roda o próprio repositório.
# Uso, dentro da VM:  bash instalar_vm_brasil.sh
# Pede, na própria VM (nunca no chat), um token do GitHub com permissão de escrita só neste repositório:
#   GitHub → Settings → Developer settings → Fine-grained tokens → Repository access: Eldorado → Contents: Read and write.
# Depois roda scripts/coleta_brasil.py pelo cron a cada 3 horas, 24 horas por dia, com o IP brasileiro da VM.
set -euo pipefail
REPO="amcjardimamerica-arch/Eldorado"
DIR="$HOME/Eldorado"
sudo apt-get update -qq && sudo apt-get install -y -qq git python3 python3-pip cron >/dev/null
if [ ! -d "$DIR/.git" ]; then
  read -r -s -p "Token do GitHub (não aparece na tela): " TOKEN; echo
  git clone -q "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$DIR"
  unset TOKEN
fi
cd "$DIR"
git config user.name "coleta-brasil-vm" && git config user.email "coleta-brasil-vm@eldorado"
pip3 install -q --break-system-packages -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt || true
LINHA="17 */3 * * * cd $DIR && ELDORADO_LOCAL_BR=1 timeout 3000 python3 scripts/coleta_brasil.py >> $HOME/eldorado-coleta.log 2>&1"
( crontab -l 2>/dev/null | grep -v "scripts/coleta_brasil.py" ; echo "$LINHA" ) | crontab -
sudo systemctl enable --now cron >/dev/null 2>&1 || true
echo "Pronto: a VM roda a coleta no Brasil a cada 3 horas (registro em ~/eldorado-coleta.log)."
echo "Teste agora: cd $DIR && ELDORADO_LOCAL_BR=1 python3 scripts/coleta_brasil.py"
