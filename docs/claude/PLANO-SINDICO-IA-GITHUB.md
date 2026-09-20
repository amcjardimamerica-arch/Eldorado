# O SÍNDICO — IA local rodando no próprio GitHub (plano de implantação)

**Decisão do titular (20/09/2026):** a IA não roda no computador dele. Roda no repositório, via
GitHub Actions, como **síndico/curador da Biblioteca de Alexandria**: pensa em otimizar as buscas,
organiza a informação, orienta os motores, expande as rotas a cada dia. Meta: **o máximo de
informação útil no menor espaço** — não é só reduzir tamanho.

## O que o GitHub Actions oferece (limites reais)
- runner `ubuntu-latest`: 4 vCPU, 16 GB RAM, ~14 GB de disco livre, até 6 h por job
- repositório público: minutos ilimitados; privado: 2.000 min/mês no plano gratuito
- **cache do Actions: 10 GB por repositório** → o modelo (2–5 GB) é baixado UMA vez e reaproveitado
- sem GPU → inferência no CPU: modelo de 3B ≈ 10–20 tokens/s; 7B ≈ 4–8 tokens/s

Conclusão: **cabe**. Um ciclo diário de 120 registros × ~300 tokens leva 30–60 min com o 3B.

## Escolha do modelo — decidida por MEDIÇÃO, não por opinião
Temos o que quase ninguém tem: **231 editais validados um a um pelo titular** (aprovado / atenção /
reprovado, com prazo e página). É o gabarito. A primeira execução do síndico roda os candidatos
contra esse gabarito e escolhe o vencedor por (1) acerto na classificação, (2) zero prazos
inventados (P24), (3) tokens/s no runner.

| candidato | Q4 | RAM | por que está na disputa |
|---|---|---|---|
| Qwen2.5-3B-Instruct | 2,0 GB | 4 GB | equilíbrio; português muito bom; Apache 2.0 |
| Qwen2.5-7B-Instruct | 4,7 GB | 8 GB | melhor entendimento; cabe nos 16 GB do runner; mais lento |
| Gemma-2-2B-it | 1,6 GB | 3 GB | alternativa rápida |
| Llama-3.2-3B-Instruct | 2,0 GB | 4 GB | referência; licença mais restrita |

Regra: o que errar prazo (inventar data) **uma vez** no gabarito está fora, por melhor que classifique.

## As tarefas do síndico (o que ele faz todo dia, sozinho)
1. **Curadoria do acervo** — classifica os registros em análise incompleta; extrai objeto/prazo com
   trecho literal; marca duplicatas por semelhança; propõe o que arquivar e o que subir.
2. **Orientação dos motores** — lê a auditoria do dia (quem leu sem achar, quem falhou), lê o texto
   do que cada rota devolveu, e propõe: nova URL, novo termo de camada 1, mudança de cadência,
   rota a desligar. Cada proposta com justificativa e confiança.
3. **Expansão das rotas** — a partir de cada edital validado: quem é o financiador, onde mais ele
   publica, que órgão vizinho faz o mesmo (a prefeitura ao lado, a secretaria irmã, o instituto da
   mesma empresa). Vira fonte candidata no catálogo.
4. **Léxico vivo** — propõe termos e vetos a partir dos títulos do dia; a promoção segue a
   estatística (≥3 aprovados/0 reprovados), o síndico só acelera a descoberta.
5. **Compactação inteligente** — decide o que guardar em texto integral, o que guardar como ficha,
   o que virar só índice: prioriza o que tem valor para a A.M.C. (Goiás, nacional, área compatível)
   e reduz o resto. Relata o ganho em MB e o que foi preservado.
6. **Relatório do síndico** — uma página por dia: o que mudou, o que propôs, o que foi aplicado,
   o que ficou para o titular. Publicado no painel.

## Regra que nunca muda
O síndico **propõe**; a validação determinística **decide**; tudo leva `origem: sindico`, modelo e
trecho. Prazo, valor, objeto e página só entram com trecho literal presente no texto. Nada
sobrescreve o que o titular ou o robô confirmou. Tudo reversível em bloco.

## Passos de implantação (ordem de execução na próxima sessão)
1. **Workflow `sindico.yml`** — roda 1×/dia (04h, depois da coleta) e por disparo manual; instala
   llama.cpp (17 MB, release fixa) e restaura o modelo do cache do Actions (baixa do Hugging Face só
   se o cache estiver vazio); sobe `llama-server`; roda `python -m src.sindico ciclo`; aplica; commita
   `estado/sindico/` e as propostas; publica o painel.
2. **`src/sindico.py`** — evolução do `src/ia_local.py` já existente (mesmas tarefas, mesma
   validação) + as tarefas 3, 5 e 6 acima + o **benchmark contra o gabarito** dos 231.
3. **Primeira execução = benchmark** — roda os 4 candidatos, grava `estado/sindico/benchmark.json`
   (acerto, prazos inventados, tok/s, RAM, minutos gastos) e fixa o vencedor em `config/sindico.json`.
4. **Cache do modelo** — chave `modelo-<nome>-<hash>`; renovação só quando a chave mudar.
5. **Orçamento** — `config/sindico.json` limita minutos por dia e registros por ciclo; se estourar,
   para e relata (nunca corta pela metade sem dizer).
6. **Painel** — quadro "Síndico" na Bússola: último ciclo, propostas válidas/descartadas, rotas
   sugeridas, MB poupados, relatório do dia.
7. **Testes** — servidor simulado (já existe em `tests/test_ia_local.py`) + teste do workflow + teste
   de que nenhuma proposta inválida chega ao banco.

## Prompt de arranque para a próxima sessão
> Leia `docs/claude/PLANO-SINDICO-IA-GITHUB.md` e execute os 7 passos em ordem, um por vez, testando
> cada um antes do seguinte. Comece pelo workflow `sindico.yml` com cache do modelo; depois
> `src/sindico.py` a partir de `src/ia_local.py`; dispare a primeira execução como benchmark dos 4
> candidatos contra as 231 validações do titular (`docs/dados/verificacao_467_2026-09-09.json` e
> `verificacao_63_2026-09-15.json`) e fixe o vencedor. Regra inegociável: o síndico propõe, a validação
> decide; prazo só com trecho literal. Ao final, publique o quadro no painel e me traga o benchmark.
