# Parecer — A rede neural como maestro: falhas, resultados errados, condições não cumpridas e melhorias (02/10/2026)

**Conselho técnico** (chief engineer, staff engineer, CTO e professores de computação, Python) · **Associação:** A.M.C. Jardim América

## 1. Método

Testes com **erros artificiais e propositais** (16 casos: leitura truncada do diário, paginação cortada, datas e prazos impossíveis, prazo antes da publicação, página de erro com resposta 200, captcha, injeção de instrução, registro vazio, sem data de publicação, acentos quebrados, PDF sem texto, título genérico de edição, UF divergente, publicação antiga como nova, URL com rastreio), passados pelo contrato da linha, pela rede neural e pela esteira; medição sobre os 17.542 registros reais da base, o modelo treinado e os fluxos de produção.

## 2. O que estava falhando

| # | Falha | Evidência |
|---|---|---|
| 1 | **A rede não sabia quando a leitura estava defeituosa** | 13 de 14 erros passavam pelo contrato; a rede dava nota média a todos (0,28–0,61): diário lido em 12% → 0,57; data em 2099 → 0,61; registro vazio → 0,49 |
| 2 | **Calibração achatada** | temperatura 6,75 divide as saídas por quase 7 — todas as notas ficam perto de 0,5 |
| 3 | **Revocação baixa** | 0,616: no corte de 0,5, a rede deixa passar 38% das oportunidades reais (precisão 0,808; AUC 0,905) |
| 4 | **Publicações antigas como novas** | mediana de 888 dias entre publicação e consulta; só 31 de 17.229 registros consultados no dia ou no dia seguinte |
| 5 | **Horários que nunca disparavam** | motor estadual em 06:47/14:17 e Diário de Goiânia em 07:41 — a agenda só dispara em HH:23 e HH:53 |
| 6 | **104 fontes das 260 sem horário** | sem leitura desde 30/09; ninguém as acionava |
| 7 | **Leitura cortada contada como completa** | o maestro só olhava falha de página; o corte registrado pelo próprio motor não contava |
| 8 | **Armazenamento pesado** | base de 66,4 MB: rótulos repetidos em cada registro (43 de 60 MB em campos derivados) |
| 9 | **Descarte sem aprendizado** | o que se descartava voltava pelo mesmo motor; a rede não aprendia com isso |

## 3. O que foi feito

1. **Condicionais de integridade** (`src/integridade.py`) antes da rede: **bloqueia** → reprocessamento e rede "inconclusiva" (sem nota); **alerta** → "com ressalva" (nota puxada para o meio). Os sinais entram também como entradas da rede. URL canônica (sem rastreio) para a mesma página ser uma só.
2. **Datas em todo registro novo:** data original da publicação (da fonte; senão extraída do texto ou do endereço, com a origem registrada; sem pista fica vazia) e data da consulta.
3. **Itinerário** (`config/itinerario.json`): horários por família, a 1ª passagem fecha o dia anterior (D-1); 17 motores ajustados; maestro às 07h47, 11h47, 16h47 e 22h17; as 104 fontes sem horário lidas pelo maestro em lotes de 40.
4. **Maestro ativo em cada etapa** (`src/maestro.py`): cobertura (com leitura cortada = parcial), D-1 por motor diário, relatório de 9 etapas com alertas e veredito (`docs/dados/relatorio_etapas.json`, `docs/relatorios/maestro/`, 30 dias).
5. **Armazenamento leve:** códigos na base, rótulos na leitura (−21%: 66,4 → 52,4 MB), compactação idempotente a cada varredura.
6. **Descarte pelas estantes** (`src/descartes.py`): só das Estantes de Investigação; cada descarte grava a restrição do motor de origem (endereço canônico e assinatura do título), o motor passa a contar o dado como ruído filtrado, a linha o classifica como RUÍDO e a rede o recebe como exemplo negativo. Proposta de descarte após 30 dias parado; nada é descartado sozinho.

## 4. Conselho de 7 lentes

1. **Extremamente pessimista:** "Uma rede que dá 0,6 a uma data de 2099 é pior que nenhuma rede: dá falsa segurança. E com revocação de 0,62, ela esconde quase 4 em cada 10 oportunidades reais de quem confiar na nota."
2. **Pessimista:** "A assinatura do título pode bloquear um edital legítimo do ano seguinte com o mesmo nome. Restrição precisa ser específica por motor e reversível."
3. **Levemente pessimista:** "O relatório do maestro só vale se chegar à produção — e o catálogo ainda é regravado inteiro por vários fluxos."
4. **Neutro:** pondera abaixo.
5. **Levemente otimista:** "Integridade antes da nota resolve a maior parte do problema: a rede deixa de opinar sobre leitura quebrada."
6. **Otimista:** "Cada descarte agora ensina duas vezes: o motor deixa de trazer o ruído e a rede aprende o padrão."
7. **Extremamente otimista:** "Com D-1 e data original, o sistema passa a medir o próprio atraso — e a agenda pode se otimizar com dados reais."

**Síntese do neutro — parâmetros de qualidade e mitigação:**
- a rede **nunca** é filtro: nota só para leitura íntegra; inconclusiva vai ao reprocessamento;
- restrição de descarte **por motor**, com assinatura de pelo menos 4 palavras, endereço canônico, e o livro DESCARTADO fica no livro-razão (reversível);
- **próximas melhorias recomendadas:** (a) recalibrar a temperatura e fixar o corte pela revocação (meta ≥ 0,80 com precisão ≥ 0,70), em vez de 0,5; (b) separar as cargas históricas (publicação antiga) do treino de "novidade"; (c) fusão campo a campo do catálogo entre fluxos (pendência anterior); (d) medir, após 7 dias, o atraso real publicação → consulta por motor e reajustar o itinerário.

## 5. Condições que ainda não são cumpridas

- **Catálogo regravado inteiro por vários fluxos** (oscilou de 1.389 para 1.079 livros): a correção está recomendada e não foi feita aqui.
- **Calibração e corte da rede:** diagnosticados; o retreino com o corte pela revocação fica para a próxima rodada, com as decisões novas.
- **Registro da esquadra:** a correção está implantada desde o Pull Request 26, mas ainda não foi confirmada por uma varredura completa.
