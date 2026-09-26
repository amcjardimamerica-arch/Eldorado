# Parecer — o que o Llama e o Qwen3-1.7B ensinaram, o que muda no CARGO, e até onde um modelo maior cabe · 26/09/2026

## 1. Os aprendizados, em ordem de custo

| # | o que aconteceu | o que se aprendeu | vale para |
|---|---|---|---|
| 1 | O Llama "respondia a 25%"; o Qwen "a 16%". Era o **tempo limite de 25 s** cortando a resposta — só ler os ~1.400 tokens da constituição passava disso em 4 núcleos. Com 150 s, o 1.7B foi a **100%** | Antes de julgar o modelo, medir o que o cerca: tempo, formato, contexto. Dois ocupantes foram condenados por um parâmetro | cargo |
| 2 | O Llama venceu um benchmark, caiu no segundo, e ninguém o tirou; o Qwen foi nomeado por uma nota que **não era medição** | O cargo precisa de regra de saída e de posse — e a única medição que conta é em voo real | cargo |
| 3 | 62 abates que eram 2 artigos; empresas fictícias do banco de provas no radar por dois dias | Dado de teste e dado real nunca dividem arquivo; e a limpeza tem de ser na **leitura**, porque o voo grava por cima | sistema |
| 4 | O voo devolvia arquivos apagados e nomes renomeados durante o voo | Cada execução escreve sobre uma cópia antiga: tudo o que a main mudou no meio precisa ser reaplicado no pouso | sistema |
| 5 | O briefing do 1.7B copiava o exemplo do formato ("setor/região/tipo de fonte") — até ter tempo: com 150 s, apostou "instituto empresarial que seleciona por formulário no próprio site" | Modelo pequeno com prompt cortado parece burro; com tempo, pensa. Exemplos no prompt viram resposta se o modelo não tem espaço | piloto |
| 6 | A regra dos 30 dias ficou morta por dias: nenhum motor gravava data de publicação; as 16 oportunidades que o Piloto achou ficaram paradas no catálogo | Regra sem dado é decoração; e o que o Piloto encontra tem de entrar na fila do próprio Piloto | sistema |
| 7 | 7 resgates com achado e **zero ouro**: o achado de resgate nascia "não novo" | O evento que vale (prazo confirmado) precisa ser o evento que conta | cargo |
| 8 | Dois terços de cada execução são preparação (modelo do cache, servidor, commit) | No GitHub, o voo curto custa caro; o único limite deve ser o tempo total do voo, e o voo deve usá-lo | cargo |

## 2. O que muda no cargo (não só no piloto)

1. **Posse e saída só por medição em voo real** — contador que conta apenas dentro do voo; benchmark e banco de provas não existem mais.
2. **O ambiente é parte do cargo**: tempo limite = o que resta do voo; contexto de 8k; template do modelo; prompt fixo em cache. Um candidato é medido no mesmo ambiente do ocupante, nunca em outro.
3. **Resposta bruta gravada** em todo pedido (tempo, erro, começo do texto): mudez passa a ter causa, não adjetivo.
4. **Métricas do cargo** (por voo): taxa de resposta, tempo por pedido, resgates concluídos, ouro e prata, páginas lidas. É contra isso que o titular compara ocupante e candidato.
5. **Sucessão por comparação em dias alternados**, não em paralelo: mesma fila, mesmo ambiente, sem colisão de estado.
6. **Um único limite de tempo** — 30 min de voo — e a obrigação de usá-lo: primeiro a fila de resgate, depois o catálogo e a busca ativa.
7. **Folga só quando compromete**: na mesma máquina dos motores e acima de 85% de uso, o modelo menor da reserva; abaixo disso, voa.

## 3. Modelos maiores: até onde o GitHub aguenta

A máquina do GitHub (pública, gratuita) tem **4 núcleos, 16 GB de memória, ~14 GB de disco** e cache de modelos de 10 GB por
repositório. O tempo por pedido cresce na proporção do tamanho do arquivo (em CPU a velocidade é limitada pela memória).
Medido: 1.7B = ~45 s por pedido (1.736 tokens de prompt, 400 de resposta).

| modelo (Q4_K_M) | arquivo | memória em uso (8k de contexto) | tempo por pedido (estimado) | pedidos por voo de 30 min | restaurar do cache | cabe? |
|---|---|---|---|---|---|---|
| Qwen3-1.7B | 1,1 GB | ~2,5 GB | **45 s (medido)** | ~35 | 80 s | sim |
| Qwen3-4B | 2,5 GB | ~4 GB | ~100–110 s | ~15 | ~3 min | sim |
| Qwen3-8B | 4,9 GB | ~7 GB | ~210–240 s | ~7 | ~6 min | **sim, no limite útil** |
| Qwen3-14B | 9 GB | ~11,5 GB | ~380–420 s | ~4 | ~11 min | tecnicamente sim; na prática, não voa |
| Qwen3-32B | 19 GB | não cabe | — | — | — | não |
| Qwen3-30B-A3B (MoE) | 18 GB | ~20 GB | — | — | — | não (memória) |

**Leitura:** o 8B é o maior que ainda faz sentido — sete pedidos por voo dão para o briefing e uns cinco resgates. O 14B gasta
onze minutos só restaurando o modelo e responde quatro vezes por voo. Acima disso, não cabe na memória. Máquinas maiores do
GitHub existem, mas são pagas, sem plano gratuito para organização sem fins lucrativos.

**Segurança dos motores:** no GitHub não há disputa — motores e Piloto rodam em máquinas separadas, sempre. Nem o 14B
tocaria os motores. A regra dos 85% só entra em jogo no servidor próprio, e já está no código.

**Recomendação:** concluir o teste do 4B (tempo por pedido e aposta do briefing); se ele responder em ~100 s e apostar
melhor que o 1.7B, testar o 8B um dia. Se o 4B não for claramente melhor, o 1.7B com tempo é o melhor custo por resgate.
