# Motor 15 — PNCP: chamamentos e credenciamentos (`pncp-api`)

**Veredito:** workflow FUNCIONANDO · coleta FUNCIONANDO (API oficial, sem bloqueio) · resultado FUNCIONANDO (alto
volume; pouco Goiás) · histórico de 3 anos PARCIAL (2024 e 2025 bons, 2023 fraco).

## Workflow

- **Agenda:** todos os dias, às 08:53, 13:53 e 19:53, na nuvem. O módulo é `src/pncp_osc.py` (motor-04 v2, 01/10).
  Tem 16 arquivos de teste, entre eles `tests/test_motor04_pncp.py` e `tests/test_pncp_nacional.py`.
- **Leituras:** 56; a última foi em 02/10, às 14:49. Luz **verde**, com 221 achados.
- **Calendário:** 01/10 em azul e 02/10 como "parcial".

## Onde coleta

| Fonte | Endereço | 02/10 |
|---|---|---|
| A — propostas abertas por UF e modalidade (12, 3, 10, 11) | `pncp.gov.br/api/consulta/v1/contratacoes/proposta?dataFinal=…&uf=…` | 197 consultas, 6.944 itens, rodízio por 18 UFs (GO primeiro) |
| B — busca de editais "recebendo proposta" | `pncp.gov.br/api/search/?q=…&status=recebendo_proposta` (federal e GO) | 47 consultas, 1.717 itens |
| C — arquivos do órgão | — | 10 consultas, 1 localizado |

As duas APIs responderam HTTP 200 da nuvem.

## Resultado

- **Classificação:** 8.320 itens, que deram 221 OPORTUNIDADE, 1 ACOMPANHAR e 8.099 RUÍDO. São 228 oportunidades únicas
  em 243 registros, e a base tem 454 registros do PNCP.
- **Goiás:** só **16 dos 454**. Exemplos:
  - TJGO, credenciamento de entidades para recicláveis;
  - Fundo Municipal de Assistência Social (FMAS) de Inhumas, credenciamento;
  - Silvânia, chamamento 01/2026 da PNAB;
  - Trindade, acolhimento institucional.
- **Fora de Goiás:** a maior parte é municipal de outros estados (RS, SC, BA…). É útil como referência, mas não serve à
  associação.
- **Qualidade de prazo:** 215 registros antigos do id `pncp` estão como "sem prazo identificado". Os da v2
  (`pncp-api`) já vêm com a data oficial de encerramento.

## Histórico de 3 anos

- **Na base, por ano de publicação:** 2023 (7), 2024 (113), 2025 (113) e 2026 (221). São 230 anteriores a 2026.
- **Na Biblioteca** (`biblioteca_alexandria/base/editais/`, fonte PNCP): 2023 (21), 2024 (100), 2025 (74) e 2026 (371).
- **Lacuna:** 2023 está fraco. Parte do que vem de 2023 a 2025 são credenciamentos longos ainda abertos, e não o
  histórico de editais encerrados.
- **Recuperação possível:** a API de consulta do PNCP aceita período de publicação. A carga de 3 anos para Goiás (todas
  as modalidades de chamamento e credenciamento com OSC) é viável e barata.

## Correções, por prioridade

1. **Carga de 3 anos de Goiás** pela API de publicação, por período (out/2023 a set/2026), gravando também os
   encerrados com o mês típico por órgão.
2. **Prioridade territorial no painel:** separar GO e DF do nacional. Hoje o nacional afoga Goiás (16 de 454).
3. Reprocessar os 215 registros antigos "sem prazo identificado" com o leitor v2.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Com 8 mil itens por dia, a pressa pode esconder um credenciamento goiano no meio de 200 de fora. |
| Pessimista | 96% do que o motor grava não é de Goiás. |
| Levemente pessimista | 215 registros antigos sem prazo poluem a base. |
| **Neutro** | **O motor mais produtivo do conjunto, com fonte oficial e API estável. Prioridade: carga de 3 anos de Goiás e separação territorial no painel. Meta: todo chamamento ou credenciamento com OSC de órgão goiano no painel em até 24 horas.** |
| Levemente otimista | A data oficial de encerramento vem da API: o prazo é confiável. |
| Otimista | Credenciamentos longos (até 2031) são oportunidade contínua para a associação. |
| Extremamente otimista | Com 3 anos de PNCP de Goiás, o sistema sabe que órgão credencia o quê e em que mês. |
