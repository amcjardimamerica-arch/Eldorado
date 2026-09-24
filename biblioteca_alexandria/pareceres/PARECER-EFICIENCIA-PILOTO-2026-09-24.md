# Parecer — o motor do Piloto está funcionando de forma eficiente? · 24/09/2026, 14h30

**Resposta curta: não.** Ele cumpre a **forma** do que foi planejado — decola, faz o briefing, monta o plano, voa sete
missões, anuncia onde está, pousa e passa o bastão — e não cumpre a **substância**: em 60 missões hoje, **nenhum achado
útil**; o modelo responde a **19%** dos pedidos; e a única coisa que ele "descobre" é o mesmo par de artigos, a cada voo.

## 1. O que foi planejado e o que ele faz

| atividade planejada | o que acontece de fato (24/09) |
|---|---|
| Decolar a cada ~7 min, voar até 26 min | Decola e voa — mas pousa em **2 a 3 min**: as missões acabam no primeiro passo. 88% do orçamento de voo não é usado |
| Briefing pelo modelo (entender a Biblioteca, apostar um rumo) | Feito; aposta "apoiador no rodapé", confiança **baixa**. O modelo mudo cai na rede determinística |
| Missão especial (resgate) antes da exploração | Fila com 3 alvos; **nenhuma missão de resgate voou hoje** |
| Caçar oportunidade por um motor (26 missões) | A busca volta 8 a 15 resultados e **nenhum passa no crivo** — 0 de 26 |
| Descobrir fonte local (26 missões) | **0 candidatos em 26 de 26**. É a missão mais frequente e a que nunca rende |
| Afiar motor → reconhecimento do terceiro setor (8 missões) | Lê **as mesmas 4 páginas** e "encontra" **os mesmos 2 financiadores** (Globo, FGV) em todos os voos |
| Anunciar a posição para o painel | Feito, HTTP 200 em todas as missões. O avião aparece onde ele está |
| Aprender com o voo (lições, memória de erros) | 40 missões gravadas em 4 motores: **0 úteis, efetividade 0,0** em todos |
| Pousar e passar o bastão | Desde as 10h UTC: **45 voos, 40 com sucesso, 0 falhas**. As 45 falhas do dia foram todas do defeito do pouso, corrigido às 09h56 |

**Modelo (Qwen3-1.7B, empossado às 08h37): 26 pedidos, 5 respostas — 19%.** O alerta do cargo já disparou. É a mesma
mudez do Llama, o que aponta para o **formato** (o JSON exigido, o prompt, o tempo) e não para o modelo.

## 2. Onde a eficiência se perde

1. **Modelo mudo em 4 de 5 pedidos.** Sem resposta, briefing e crivo caem na regra fixa, e a regra fixa não lê página.
2. **Reconhecimento em círculo.** O plano de leitura não gira: as mesmas 4 páginas, os mesmos 2 achados, contados de novo. Hoje
   isso rendeu 62 "abates" que eram 2 — já corrigido (um abate por URL, ouro para edital aberto, prata para empresa).
3. **Descobrir fonte local nunca rendeu** — 43% das missões do dia produzindo zero. Ocupa o lugar de missões que rendem.
4. **O crivo rejeita tudo que a busca traz.** Ou a busca traz o irrelevante, ou o crivo está calibrado para nada passar. Sem
   guardar os 13 resultados e o motivo da recusa de cada um, não há como saber qual.
5. **Contaminação por execução antiga.** Uma execução iniciada antes da limpeza da manhã devolveu o radar velho, e os voos passaram
   a investigar 27 empresas fictícias do banco de provas — e a integração levou lixo ("GGFM&") à lista de empresas. Corrigido com
   barreira por domínio de ensaio (`config/dominios_de_ensaio.json`): o que só foi visto em site de teste não entra, por onde quer
   que venha. Radar hoje: 4 empresas reais.

## 3. O que está bom

- A corrente de voos é estável desde a correção do pouso: 40 de 40 voos válidos.
- A busca voltou: DuckDuckGo entregou em 57 de 59 usos hoje (ontem, 1 em 9).
- A posição ao vivo chega ao painel em toda missão.
- Os links gravados agora apontam para o site real, não para o buscador.

## 4. O conselho

**Extremamente pessimista.** Um motor que voa 100 vezes e não encontra nada útil não é um motor de busca: é um relógio.
**Pessimista.** Os "achados" do dia eram uma repetição; a métrica que o painel exibia estava inflada trinta vezes.
**Levemente pessimista.** A contaminação voltou por um caminho que ninguém previu — execução antiga devolvendo arquivo velho.
Barreira por domínio resolve o sintoma; o vetor (o commit de árvore antiga) continua aberto.
**Neutro (ponderador).** Ordem de execução, sem trocar o modelo antes de medir: (1) gravar a resposta bruta do modelo em cada
pedido mudo, para saber se ele responde fora do formato ou não responde; (2) girar as páginas do reconhecimento — página lida
hoje só volta em 7 dias; (3) suspender "descobrir fonte local" até ter uma regra que renda, e dar as vagas ao resgate e à caça;
(4) guardar os resultados recusados pelo crivo com o motivo, por 3 dias, e ler. Só depois disso faz sentido falar de modelo.
**Levemente otimista.** A infraestrutura toda funciona — voo, agenda, posição, pouso, links. O que falta é o miolo.
**Otimista.** Com a busca de volta e um abate por URL, o próximo relatório vai medir o Piloto de verdade pela primeira vez.
**Extremamente otimista.** Quatro correções de uma tarde separaram o que era ruído do que era trabalho; a partir de agora cada
estrela que aparecer terá sido ganha.
