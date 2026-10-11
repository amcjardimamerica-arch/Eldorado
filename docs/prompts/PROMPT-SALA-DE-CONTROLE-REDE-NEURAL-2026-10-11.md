# Eldorado · Sala de Controle da Rede Neural · 11/10/2026

## Finalidade
Uma página nova no Eldorado (como o Cartório) que mostre a rede neural e o maestro **por inteiro**: cada função que
executam, quando foi acionada pela última vez, o efeito e o resultado, com indicadores de funcionamento e de falha —
o controle do sistema "da visão do maestro", como a sala de controle de uma usina, onde cada instrumento tem o seu
mostrador.

## Regras
1. **Só dado real.** Cada mostrador lê um registro do sistema (rede neural, maestro, status dos motores, linha de
   produção, repositório único, Cartório, Pilotos, Biblioteca, empresas, uso dos arquivos). Sem dado, o mostrador diz
   "sem leitura" — nunca um número inventado.
2. **Cada instrumento responde a quatro perguntas:** o que faz · quando foi acionado · o que mudou (efeito) · como está
   (resultado, com faixa normal e faixa de alarme).
3. **Falha visível:** instrumento parado além da cadência (registro velho) ou fora da faixa acende o painel de alarmes.
4. **Histórico:** cada passagem guarda um retrato dos indicadores (as últimas 96), para mostrar tendência.
5. **Geração automática:** `src/sala_controle.py` roda em toda passagem do fluxo 22 (agenda + maestro + rede neural),
   logo depois do maestro, e grava `docs/dados/sala_controle.json`; a página lê direto do repositório (dado do momento).

## Plano de design (revisado contra os padrões genéricos)
- **Conceito:** a mesa de controle de uma usina dos anos 70–80 — painéis de chapa verde-acinzentada, mostradores de
  ponteiro com mostrador claro, janelas de alarme (anunciador) que acendem âmbar e vermelho, um diagrama mímico do
  processo com o fluxo correndo pelas tubulações. Não é o "fundo preto com verde neon" nem o "creme com serifa".
- **Cor:** chapa do painel `#6E857A` · moldura escura `#2B3530` · mostrador `#E9EBE2` · âmbar de alarme `#E8A33C` ·
  vermelho de desarme `#C2392F` · lâmpada verde `#4FAE5C`.
- **Tipo:** Barlow Condensed (rótulos e números, com algarismos tabulares) — a tipografia estreita das placas de
  identificação de painel; corpo em Barlow.
- **Estrutura:** (1) faixa de anunciadores no alto; (2) o núcleo: mostrador grande do índice de saúde do sistema, com os
  subsistemas em volta; (3) o diagrama mímico da esteira (coleta → repositório → livro → Cartório/Interceptador →
  verificação externa → Farol) com os números em cada trecho; (4) a mesa de instrumentos por subsistema, cada um com
  ponteiro, lâmpada, último acionamento e tendência; (5) a linha do tempo dos acionamentos. Clicar num instrumento abre
  a ficha: o que faz, quando, efeito, resultado, histórico.
- **Movimento:** um só momento orquestrado — ao abrir, os ponteiros sobem do zero até o valor; o fluxo no diagrama
  mímico corre devagar; respeita "reduzir movimento".
- **Lugar da ousadia:** o mostrador do núcleo e o anunciador. O resto, disciplinado.
