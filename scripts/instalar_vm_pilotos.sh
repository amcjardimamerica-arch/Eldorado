#!/usr/bin/env bash
# PILOTOS 24 h NUMA VM GRATUITA NO BRASIL (Oracle Cloud Always Free — São Paulo ou Vinhedo; Ubuntu 22.04/24.04).
# Formato sugerido: VM.Standard.A1.Flex com 4 OCPU e 24 GB (gratuito). Uso, dentro da VM:  bash instalar_vm_pilotos.sh
# Pede, na própria VM (nunca no chat), um token do GitHub com permissão de escrita só neste repositório:
#   GitHub → Settings → Developer settings → Fine-grained tokens → Repository access: Eldorado → Contents: Read and write.
# Compila o llama.cpp (ARM ou x86), baixa o Qwen3-8B (5 GB) e agenda os pilotos de hora em hora, 24 h por dia.
set -euo pipefail
REPO="amcjardimamerica-arch/Eldorado"
DIR="$HOME/Eldorado"
sudo apt-get update -qq && sudo apt-get install -y -qq git python3 python3-pip cron build-essential cmake curl >/dev/null
if [ ! -d "$DIR/.git" ]; then
  read -r -s -p "Token do GitHub (não aparece na tela): " TOKEN; echo
  git clone -q "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$DIR"
  git clone -q "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$HOME/Eldorado-pilotos"
  unset TOKEN
fi
cd "$DIR"
git config user.name "pilotos-brasil-vm" && git config user.email "pilotos-brasil-vm@eldorado"
pip3 install -q --break-system-packages -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt || true
mkdir -p ia_local/motor ia_local/modelos
if [ ! -x ia_local/motor/llama-server ]; then
  rm -rf /tmp/llama.cpp && git clone -q --depth 1 https://github.com/ggml-org/llama.cpp /tmp/llama.cpp
  cmake -S /tmp/llama.cpp -B /tmp/llama.cpp/build -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build /tmp/llama.cpp/build --target llama-server -j "$(nproc)" >/dev/null
  cp /tmp/llama.cpp/build/bin/llama-server ia_local/motor/
fi
M=ia_local/modelos/Qwen3-8B-Q4_K_M.gguf
if [ ! -s "$M" ]; then
  for U in $(python3 -c "import json;print(' '.join(json.load(open('config/espelhos_gguf.json'))['espelhos']['qwen3-8b']))"); do
    curl -L --retry 3 --fail -s -o "$M" "$U" && break || rm -f "$M"
  done
fi
[ -s "$M" ] || { echo "não consegui baixar o modelo"; exit 1; }
LINHA="3 * * * * cd $DIR && git pull -q && timeout 3500 python3 scripts/pilotos_brasil.py --minutos 55 --maquina vm >> $HOME/eldorado-pilotos.log 2>&1"
( crontab -l 2>/dev/null | grep -v "scripts/pilotos_brasil.py" ; echo "$LINHA" ) | crontab -
sudo systemctl enable --now cron >/dev/null 2>&1 || true
echo "Pronto: os pilotos voam pela VM de hora em hora, 24 h por dia (registro em ~/eldorado-pilotos.log)."
echo "Teste agora: cd $DIR && python3 scripts/pilotos_brasil.py --minutos 20 --maquina vm"
