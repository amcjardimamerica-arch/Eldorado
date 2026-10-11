# Eldorado · Sala de controle, versão 2 — "o datacenter vivo" · 11/10/2026

## Finalidade
Refazer a apresentação da sala de controle (os dados e o gerador `src/sala_controle.py` continuam): a página da versão 1
ficou longa (≈5.800 px) e com aspecto antigo. A nova deve contar a rede neural **de cima para baixo, do começo ao fim**,
etapa por etapa, com os mostradores **agregados por etapa**, compacta, elegante, sem poluição visual, e cada informação
abrindo em detalhe ao clique.

## Direção criativa
Um datacenter em órbita no ano de 2200, onde a computação é cultivada e não montada: o processamento cresce como
micélio, os dados correm por um axônio, cada etapa é uma célula com membrana translúcida. Orgânico e tecnológico ao
mesmo tempo — e claro, não escuro: a luz de uma estação orbital de dia, não uma sala escura com neon.

## Plano de design
- **Cor ("nácar orbital"):** pérola `#EEF1F6` (fundo) · grafite azulado `#1D2738` (texto) · micélio `#4F8C88` (veios e
  etapas) · bioluminescência `#7A6AF0` (o sinal que corre) · musgo `#4FA374` (normal) · âmbar `#E2A04A` (atenção) ·
  coral `#DE5A52` (alarme).
- **Tipo:** Unbounded (só nos números grandes e nos nomes das etapas — larga e arredondada, cara de 2200) e Manrope
  (todo o resto).
- **Estrutura (≈1.500 px):** (1) o núcleo — uma célula que respira com o índice de saúde e os alarmes acesos como
  esporos clicáveis; (2) o axônio — uma linha orgânica que desce pela página, com o sinal correndo e o volume de dados
  escrito em cada trecho; (3) sete células em sequência, alternando os lados do axônio: Coleta · Aprendizado ·
  Repositório · Certificação · Investigação · Destino · Manutenção. Cada célula: nome, uma linha do que faz, até quatro
  anéis de medida (valor e faixa) e o estado. Clique na célula abre a etapa inteira (todos os instrumentos, com o que
  faz, quando, efeito, resultado, faixa e tendência).
- **Profundidade:** três camadas de veios ao fundo que andam em velocidades diferentes com a rolagem (paralaxe); as
  células inclinam levemente para o ponteiro (perspectiva 3D, no máximo 5°). Sem bibliotecas; tudo desliga com
  "reduzir movimento".
- **Movimento:** um só gesto contínuo — o sinal descendo pelo axônio; a célula do núcleo respira devagar.
- **Revisão contra o genérico:** não é fundo escuro com neon (é claro, nacarado); não são cartões retangulares
  idênticos (as células têm membrana assimétrica e tamanhos pela importância); números grandes só onde há leitura.
