# Parecer do conselho — a estrutura dos dois Pilotos · 26/09/2026, 20h30

## 1. As premissas, como estão implementadas

| | Piloto - Espião | Piloto - Interceptador |
|---|---|---|
| premissa | **aumenta**: encontra o que os 30 motores não encontram, com criatividade, e cria fontes novas | **aprofunda**: estuda cada possibilidade trazida pelos motores ou pelo Espião |
| entrada | a Biblioteca, a cobertura dos motores, os voos anteriores | edital novo dos motores → indício novo do Espião → aberto atual com falta → empresa nova |
| trabalho de um voo | briefing (aposta) → missões: **aposta**, catálogo do terceiro setor, busca ativa de empresas | **um alvo**: fonte oficial → doze condições com trecho → dispensa → qualidade → parecer "como serve como fonte" |
| saída | candidatas para o Interceptador; empresas para o radar; **fontes novas** para os motores (em quarentena) | ficha comprovada, fila do Claude, fonte nova (página-mãe de editais), ouro no bordo |
| memória | site lido volta em 7 dias; aposta não repete lugares secos | **nunca refaz**: o que estudou não volta |
| ritmo | corrente de 3 s, 30 min por voo | corrente de 3 s, um alvo (~12 min) |
| modelo | Qwen3-8B, ~100 s por pedido | Qwen3-8B, ~3–5 min por alvo no modelo |
| arbitragem | — | — o **Claude**, a cada 3 dias, valida ou descarta pela fila `para_claude.json` (44 itens hoje) |

## 2. O que já foi medido depois da separação

- Espião: voo de **3,5 min dos 30** — o plano tinha duas missões e acabava. O briefing, porém, apostou bem: *"programa de doação de multinacional com inscrição local: a notícia vem antes do edital"*. A aposta não virava missão. **Corrigido hoje**: a pergunta do briefing vira duas buscas no mesmo voo (nacional e Goiás), e o catálogo passa a receber vários sites por voo até preencher o tempo.
- Interceptador: **BNDES 11/12 validada** e um chamamento do PNCP 10/12 parcial — prazo fora da fonte oficial porque o cronograma está em tabela no PDF.
- Fontes novas ativadas sem revisão (IDIS, Rede Filantropia) — **corrigido**: entram em quarentena, desligadas, até a análise do Claude.

## 3. Pontos de falha (por ordem de gravidade)

1. **Tabelas em PDF.** A extração de texto perde a estrutura; o prazo — o dado mais valioso — fica fora da prova. Vale para qualquer modelo. *Correção:* extrair tabelas como tabelas (pdfplumber) e, sem texto, imagem da página com OCR; janelas em torno de "cronograma".
2. **Cérebro e mãos desconectados no Espião.** O briefing pensa, o plano executa sempre as mesmas missões. *Corrigido parcialmente* (aposta vira missão). Falta: o resultado da aposta alimentar a próxima aposta (o que veio seco é registrado; o que veio cheio deve virar semente).
3. **Enquadramento por regra.** As candidatas do Espião são classificadas por expressões regulares, não pelo modelo — "A VERIFICAR" é a classe mais comum. *Correção:* uma pergunta barata ao modelo por candidata (tipo, quem financia, para quem).
4. **Escrita concorrente no repositório.** Dois papéis e os motores gravam nas mesmas pastas; hoje dois registros ficaram corrompidos por fusão automática. *Correção feita* (cada um grava só o que mudou; validação de JSON na leitura pendente); *falta*: fallback à última versão válida quando um arquivo vier corrompido.
5. **"Nunca refaz" sem exceção.** Edital prorrogado ou republicado não é reestudado. *Correção:* o motor que atualizar o registro (novo prazo, novo anexo) reabre o alvo.
6. **Memória do 8B no Espião.** Pedidos de ~100 s com estouros no fim do voo (8 de 29 no dia). *Correção:* cortar a constituição (~1.400 tokens em cada pedido) para ~500; manter o cache do prompt.
7. **Qualidade "validada" quase inalcançável** enquanto (1) não for resolvido — o padrão está certo, a leitura não. Manter o padrão; corrigir a leitura.
8. **A fila do Claude cresce mais rápido que a análise** (44 hoje; +11 novos dos motores por dia). *Correção:* a fila ordena por qualidade e por proximidade do prazo; itens "insuficientes" sem página oficial saem para uma lista separada.
9. **Custo de preparação**: 2–3 min por execução (modelo do cache, servidor) em cada voo dos dois — 15–20% do tempo. Só o servidor próprio resolve.

## 4. Melhorias propostas, em ordem

1. Leitura de tabelas em PDF e OCR de página (o maior ganho de "validadas").
2. Enquadramento das candidatas pelo modelo, no pouso do Espião.
3. Reabertura de alvo quando o registro muda.
4. Constituição enxuta para o Espião.
5. Fallback à última versão válida em `load_json`.
6. Semente automática: aposta que rendeu candidata vira site do catálogo.

## 5. O conselho

**Extremamente pessimista — chief engineer.** Dois modelos de 8B em duas máquinas para, hoje, entregar duas fichas e zero ouro. Sem ler tabela de PDF, o Interceptador vai carimbar "parcial" para sempre.

**Pessimista — staff engineer.** A fila do Claude vira gargalo em uma semana. Se o humano é o arbitro, o sistema tem de entregar a ele *menos* itens e *melhores*; hoje entrega 44 de qualidade desigual.

**Levemente pessimista — professor.** O Espião ganhou criatividade no briefing, mas a criatividade só vale quando muda o que ele faz; a aposta virar missão foi implementada hoje e ainda não voou.

**Neutro — CTO (ponderador).** A arquitetura está certa e finalmente separada: descobrir, comprovar, decidir — três papéis, três memórias, sem colisão. Os pontos de falha são de leitura e de fluxo, não de desenho. Ordem: (1) tabelas e OCR; (2) enquadramento pelo modelo; (3) reabrir alvo quando o registro muda; (4) fila do Claude ordenada por prazo e qualidade; (5) constituição enxuta. Quarentena de fontes e "nunca refaz" são as duas regras que protegem o sistema de si mesmo — manter.

**Levemente otimista — professor.** BNDES 11/12 na primeira tentativa, com prova literal em cada item. O padrão de qualidade funciona; o que falta é dar a ele documentos legíveis.

**Otimista — staff engineer.** Toda descoberta vira fonte monitorada: o Espião não precisa achar o mesmo edital duas vezes — os motores acham a próxima edição. É o mecanismo que faz o sistema crescer sozinho.

**Extremamente otimista — CTO.** Com a aposta virando missão e as fontes em quarentena revisadas a cada 3 dias, o Espião passa a ser o que foi pedido: quem cria as buscas que os motores farão amanhã.
