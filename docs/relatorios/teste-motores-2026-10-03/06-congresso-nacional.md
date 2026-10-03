# Motor 06 — Congresso Nacional (`congresso-nacional`)

**Veredito:** workflow FUNCIONANDO (motor novo, 1 leitura) · coleta FUNCIONANDO · resultado FUNCIONANDO, sem
oportunidade no momento, e isso está correto · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** todos os dias, às 10:53 e 20:53, na nuvem. O disparo é `agenda-motores` → `monitoramento-diario` →
  `src.sensores` → `src/congresso_nacional.py` (v1, 02/10).
- **Testes:** `tests/test_motor_congresso_nacional.py` passa.
- **Leituras:** **apenas 1**, manual, em 02/10 às 14:34.
  - A das 20:53 de 02/10 ainda não tinha aparecido às 21:37 (Brasília).
  - A última execução registrada dos sensores foi às 19:10 e terminou em **erro** (`KeyError: 'lido_em'` em
    `src/sensores.py`).
  - Ver o consolidado: depois disso não houve leitura registrada de nenhum motor.

## Onde coleta

| Fonte | Endereço | Nuvem |
|---|---|---|
| A — Comissão Mista de Orçamento | `congressonacional.leg.br/web/orcamento/.../loa/2027` | HTTP 200, 1 item |
| B — Câmara, dados abertos | `dadosabertos.camara.leg.br/api/v2/proposicoes` | HTTP 200, 3 itens |
| C — Senado, dados abertos | `legis.senado.leg.br/dadosabertos/processo` | 4 itens |
| D — notícias | — | 35 itens |
| E — convocações | — | 4 itens |

## Resultado

- 47 itens lidos: 0 OPORTUNIDADE, 3 ACOMPANHAR e 44 RUÍDO.
- **Janela de emendas ao PLOA 2027:** "não iniciada". Está correto: o cronograma da CMO ainda não abriu o prazo das
  emendas individuais.
- **Bom sinal:** quando a CMO publicar o prazo, o motor o lê da fonte oficial, e não de janela fixa.

## Histórico de 3 anos

- **Nenhum registro.**
- **Recuperação possível:** as APIs da Câmara e do Senado aceitam ano, e o cronograma da CMO de cada LOA (2024, 2025 e
  2026) é público. A carga das três janelas de emendas e das proposições para entidades é viável.

## Correções, por prioridade

1. **Corrigir a quebra dos sensores** (`KeyError: 'lido_em'`; ver consolidado). Ela impede o registro de qualquer
   leitura.
2. **Carga de 3 anos:** prazos de emendas da LOA 2024 a 2026 (abertura e encerramento) e proposições sobre entidades,
   para prever a janela de 2027 com data.
3. Quando a janela abrir, rodar diariamente até o fim do prazo e alertar o titular no mesmo dia.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Uma única leitura não prova nada. Se a quebra dos sensores continuar, o prazo da CMO abre e ninguém vê. |
| Pessimista | Sem histórico, não há como avisar com antecedência quando a janela costuma abrir. |
| Levemente pessimista | 44 ruídos em 47 itens: a fonte de notícias pesa pouco. |
| **Neutro** | **Motor correto e bem desenhado (fonte oficial da CMO, APIs abertas). O risco é de execução: corrigir a quebra dos sensores e confirmar 2 leituras por dia. Meta: prazo de emendas registrado em até 24 horas da publicação pela CMO.** |
| Levemente otimista | As 5 fontes responderam na nuvem, sem bloqueio. |
| Otimista | O PLOA 2027 prevê cerca de R$ 43 milhões por deputado em emendas individuais: o ganho potencial é alto. |
| Extremamente otimista | Com 3 anos de janelas, o titular prepara o pedido antes de a janela abrir. |
