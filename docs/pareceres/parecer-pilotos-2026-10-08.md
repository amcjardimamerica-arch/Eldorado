# Parecer — Pilotos Espião e Interceptador (08/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO e professores de computação, Python) · **A.M.C. Jardim América**

## O que foi obtido (desde 05/10)
| | Espião | Interceptador |
|---|---|---|
| voos | 561 | 320 |
| resultado | 3.665 achados · **0 oportunidades abertas** | **32 validadas (10%)** · 103 parciais (32%) · 185 insuficientes (58%) |
| antes (29/09–03/10) | 3,6% com aberta | 1% validadas |

## Causas
**Sucesso:** a pergunta do voo deixou de ser o eco do modelo (0 casos, eram 396 de 400); o Interceptador subiu de 1% para 10% validadas com a leitura documental e o critério dos 12 itens; não há insistência no mesmo alvo (no máximo 2 voos).
**Insucesso:** (1) **insistência sem aprendizado no Espião** — o sistema REGISTRAVA as 40 consultas ruins mas não deixava de usá-las (a mesma consulta, 137 mil tentativas, sempre "nada no crivo"); (2) o **território** não chegava aos voos (3.515 achados "sem"): o Espião classificava, mas o registro do voo não guardava; (3) Interceptador: 22 voos "nenhuma fonte legível" (páginas que recusam a nuvem ou só abrem com JavaScript) e 6 "o modelo não devolveu JSON".

## Melhorias implantadas (08/10)
1. **O que foi aprendido como ruim deixa de ser tentado:** consultas com 20+ tentativas sem resultado (e as muito parecidas, similaridade ≥ 0,85) são descartadas antes da busca; o voo gera outra a partir do ângulo.
2. **Território e "novo" gravados em cada achado do voo** (GO, BR, INT, fora).
3. **Contagem de missões reiniciada** (histórico em `estado/piloto/contagem_anterior_2026-10-08.json`).

## Melhorias recomendadas
- Espião: medir por **oportunidade aberta em GO/BR/INT**, não por achado; aposentar ângulos com 0 abertas em 30 voos.
- Interceptador: "nenhuma fonte legível" → fila do navegador do titular (já existe o executor e a fila do Chrome); JSON inválido → segunda tentativa com formato reduzido.
- Pilotos no computador da titular (navegador real): ainda não ativados — é o maior ganho disponível.

## Conselho de 7 lentes
1. Extremamente pessimista: "0 abertas em 561 voos: o Espião hoje não entrega valor."
2. Pessimista: "137 mil tentativas da mesma consulta mostram que aprender sem agir é igual a não aprender."
3. Levemente pessimista: "58% insuficientes no Interceptador ainda é muito."
4. Neutro: implantar o bloqueio das ruins e o território já; reavaliar em 7 dias com a contagem zerada; meta: Espião ≥ 1 aberta GO/BR/INT por dia, Interceptador ≥ 20% validadas.
5. Levemente otimista: "O Interceptador decuplicou a validação."
6. Otimista: "Com a contagem zerada, a próxima medição é limpa."
7. Extremamente otimista: "Com o navegador do titular, o Espião sai da porta única de busca."
