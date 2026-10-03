# Motor 13 — Prefeituras das 25 maiores cidades de Goiás (`prefeituras-50-go`)

**Veredito:** workflow PARCIAL (a v2 rodou fora do registro da esquadra) · coleta PARCIAL (8 de 25 cidades lidas, 17
aguardando o Brasil) · resultado FALHA hoje (0 oportunidades abertas) · histórico de 3 anos **FUNCIONANDO para 8
cidades** e FALHA para 17.

## Workflow

- **Agenda (`plat-prefeituras-50-go`):** todos os dias, às 09:23 e 15:23, na nuvem. O módulo é
  `src/prefeituras_25_go.py` (motor 08 v2, de 02/10), e o teste `tests/test_motor_prefeituras_25_go.py` passa.
- **Contradição no painel:**
  - a esquadra mostra a última leitura em **01/10, às 12:03, com o leitor antigo**: homes do Querido Diário e do PNCP,
    19 leituras e 0 achados. A luz está **vermelha**;
  - o estado da v2 (`estado/prefeituras_25_go.json`) mostra uma leitura em **02/10, às 20:18 (Brasília)**, que não
    entrou no registro da esquadra nem no calendário do painel.
- Ou seja: o painel ainda mostra o motor antigo.

## Onde coleta (v2)

| Situação | Cidades |
|---|---|
| **Parcial** (camada 4, lidas pelo Querido Diário e pelo site municipal) | Aparecida de Goiânia, Águas Lindas, Trindade, Formosa, Senador Canedo, Cristalina, Inhumas e Goiânia (Goiânia com o portal pendente) |
| **Aguardando coleta local (Brasil)**, camada 1 | Anápolis, Rio Verde, Luziânia, Valparaíso, Novo Gama, Itumbiara, Catalão, Jataí, Planaltina, Caldas Novas, Santo Antônio do Descoberto, Goianésia, Cidade Ocidental, Mineiros, Itaberaí, Jaraguá e Quirinópolis (17) |

## Resultado

- Em 02/10 (v2): 0 oportunidades abertas e 0 históricas novas.
- Não há registros na base com o id do motor.
- **Omissão provável:** os portais das 17 cidades que recusam a nuvem. O Interceptador achou, por outro caminho:
  - Anápolis, Fundo Municipal de Cultura;
  - Goianésia, credenciamento 001/2026;
  - Goiatuba, PNAB.

## Histórico de 3 anos (o mais completo até aqui)

- **Inventário-base embutido:** 357 publicações das 25 cidades, de 2023 (43), 2024 (91), 2025 (109) e 2026 (111).
- **Janela configurada:** 1.096 dias, ou seja, 3 anos.
- **Lido pela v2, por ano:**

| Cidade | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Trindade | 70 | 153 | 124 | 103 |
| Aparecida | 20 | 90 | 46 | 66 |
| Inhumas | 2 | 64 | 72 | 114 |
| Goiânia | 5 | 42 | 22 | 50 |
| Senador Canedo | 41 | 140 | — | — |

  Águas Lindas, Formosa e Cristalina também foram lidas.
- **Lacunas:**
  - as 17 cidades em camada 1 não têm histórico próprio;
  - Senador Canedo para em 2024;
  - Formosa começa em 2025.

## Correções, por prioridade

1. **Ligar a esquadra à v2:** o registro de leitura e o calendário do painel devem refletir a v2, não o leitor antigo.
   A luz vermelha atual é do motor antigo.
2. **Coleta no Brasil** (computador do titular ou VM Oracle) para as 17 cidades em camada 1, com a mesma janela de 3
   anos.
3. Completar Senador Canedo (2025–2026) e Formosa (2023–2024), que podem ter mudado de diário.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | 17 das 25 maiores cidades estão cegas, inclusive Anápolis, Rio Verde e Catalão. |
| Pessimista | O painel mostra luz vermelha do motor antigo e esconde o que a v2 fez. |
| Levemente pessimista | 0 oportunidades abertas hoje em 8 cidades lidas pede conferência dos filtros. |
| **Neutro** | **A v2 tem o melhor desenho de histórico (3 anos por cidade). Faltam execução no Brasil e o registro certo no painel. Prioridade: ligar a v2 à esquadra e rodar as 17 cidades localmente. Meta: 25 de 25 cidades com camada 4.** |
| Levemente otimista | 357 publicações de 3 anos já catalogadas formam a base de recorrência por cidade. |
| Otimista | Trindade e Inhumas têm centenas de publicações por ano: são fontes ricas e próximas. |
| Extremamente otimista | Com as 25 cidades, a associação sabe o mês em que cada prefeitura abre edital de cultura, assistência ou esporte. |
