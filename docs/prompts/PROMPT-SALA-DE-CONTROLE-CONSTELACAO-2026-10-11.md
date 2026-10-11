# Eldorado · Sala de controle, versão 3 — "a constelação" · 11/10/2026

## Finalidade
Todos os dados da versão 1 (mesa de usina) e mais detalhe, com a estrutura de fluxo da versão 2, numa página de desktop
que usa a tela inteira (de uma borda à outra, sem coluna central fixa). A rolagem existe, mas cada tela aproveitada.

## Restrições da titular
- Só desktop (sem layout de celular). Largura total.
- O fundo é uma constelação que interage com os dados e os mostradores — **o fundo não tem paralaxe**.
- Paralaxe, 3D e morph **só nas informações** e na abertura de cada uma.
- O detalhe abre numa janela no meio da tela, de forma criativa — **nunca um painel lateral**.
- Fluxo vertical do começo ao fim da rede neural, inspirado no fluxograma da esteira (9 etapas), sem poluição.
- Leve: sem biblioteca externa; canvas único para a constelação; pausa quando a seção não está visível.

## Skills
- frontend-design (lida e aplicada): plano → revisão contra o genérico → execução → crítica com captura de tela.
- Superdesign: instalada, mas o serviço `superdesign.dev` está bloqueado pela rede deste ambiente (não roda aqui).
- design-elevation, interaction-design, design-critique, genart, data-visualization: listadas, mas sem arquivos nesta
  sessão (instaladas depois do início da conversa) — os princípios delas guiam a crítica manual.

## Conceito
O Eldorado como um **observatório de uma mente em órbita**. As estrelas do fundo SÃO os motores (cada motor uma estrela,
brilho e cor pelo estado); as etapas da rede neural são **constelações** desenhadas sobre elas; o sinal viaja de uma
constelação a outra como luz entre estrelas. Ao passar o mouse numa etapa, a constelação dela se acende no céu; ao
passar numa estrela, ela diz qual motor é e como está. Cada etapa é uma **faixa de largura total** que flutua sobre o
céu em vidro escuro, com seus instrumentos em camadas de profundidade (paralaxe pelo ponteiro).

## Plano de design
- **Cor (noite orbital):** índigo profundo `#070C24` → `#151B45` (céu, com nebulosas violeta e verde-água) · estrela
  `#EAF2FF` · aurora `#5EE6C8` (normal e sinal) · violeta `#9B8CFF` (rede neural) · âmbar `#FFB347` (atenção) · coral
  `#FF6B6B` (alarme) · névoa `#8B93B8` (texto secundário). Multicolorido como uma aurora — não o "preto com um neon".
- **Tipo:** Michroma (estendida, só em números e nomes de etapa) + Saira Semi Condensed (rótulos e texto).
- **Estrutura:** (1) Observatório: o índice de saúde num mostrador-anel grande, o painel de alarmes como um mapa estelar
  de janelas, as contagens; (2) nove faixas em sequência — Regência, Coleta, Repositório, Pertinência e aprendizado,
  Biblioteca, Certificação, Investigação, Verificação externa, Farol — cada faixa com número da etapa, o que faz, os
  mostradores agregados (anéis com faixa normal/alarme), contadores e uma lista curta do que importa (ex.: motores em
  falha, itens do Cartório); (3) sistema nervoso: os fluxos automáticos e a linha do tempo.
- **Janela de detalhe:** abre no centro como um holograma que **nasce do elemento clicado** (morph do retângulo de
  origem até a janela), com o céu escurecendo e a constelação da etapa em destaque.
- **Movimento:** números que sobem ao entrar na tela; camadas da faixa que respondem ao ponteiro; o sinal entre as
  constelações. Respeita "reduzir movimento".
