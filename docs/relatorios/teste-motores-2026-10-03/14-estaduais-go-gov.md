# Motor 14 — Oportunidades Estaduais Governamentais de Goiás (`estaduais-go-gov`)

**Veredito:** workflow PARCIAL (roda, mas o painel não vê) · coleta FUNCIONANDO (37 órgãos, todos com HTTP 200 na
nuvem) · resultado FUNCIONANDO (1 aberta, da Secult) · histórico **FUNCIONANDO: 5 anos lidos, 55 oportunidades
históricas**.

## Workflow

- **Agenda (`plat-estaduais-go-gov`):** todos os dias, às 09:23 e 15:23, na nuvem. O módulo é `src/estaduais_go.py`,
  e o teste `tests/test_motor_estaduais_go.py` passa.
- **Leitura real:** 02/10, às 17:57 (Brasília), registrada em `estado/estaduais_go.json`.
- **O painel não vê:** a esquadra **não tem registro** deste motor. O status mostra "não rodou hoje" (cinza) e o
  calendário fica cinza.
- É a mesma desconexão do motor 13: o leitor v2 grava o estado próprio, mas o registro do painel não é atualizado.

## Onde coleta

- **37 órgãos do Poder Executivo de Goiás:** secretarias, autarquias, fundações, estatais, conselhos e fundos. Cada um
  é lido em camadas: onde publica, histórico, oportunidades e monitoramento diário.
- Todos os sites estão no WordPress de `goias.gov.br/<órgão>` e **responderam HTTP 200 da nuvem**. Todos estão na
  camada 4, a completa.
- Exemplo: Secult (`goias.gov.br/cultura`), com 25 pontos de publicação e os termos "chamamento público", "edital",
  "seleção de projetos", "termo de fomento" e "termo de colaboração".

## Resultado

- **Aberta hoje:** 1, na Secult. É a mesma que o motor 02 registrou: o edital para levar a produção goiana ao Rio de
  Janeiro.
- **Na base:** 0 registros com o id do motor. As oportunidades vão para os livros da Biblioteca (`pendentes_livros:
  0`).

## Histórico (o mais longo do conjunto)

- **Publicações lidas por ano (37 órgãos):** 2021 (312), 2022 (1.071), 2023 (1.550), 2024 (2.141), 2025 (2.926) e
  2026 (1.196).
- **Oportunidades históricas registradas:** 55. A Secult sozinha tem 26.
- A janela configurada é de **5 anos**, acima dos 3 pedidos.

## Correções, por prioridade

1. **Registrar a leitura da v2 na esquadra** (última leitura, achados, calendário), para o painel deixar de mostrar
   cinza num motor que roda e rende.
2. **Mostrar no painel o histórico por órgão** (oportunidades por ano e mês típico): o dado já existe.
3. **Conferir a deduplicação** com o motor 02: o mesmo edital da Secult chega pelo diário e pelo site.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | O titular olha o painel, vê cinza e conclui que o motor não funciona. A confiança no sistema cai. |
| Pessimista | 1 oportunidade aberta em 37 órgãos é pouco: falta conferir se o léxico final (126 → 56) ficou restritivo demais. |
| Levemente pessimista | O histórico vai para os livros, mas não aparece no painel do motor. |
| **Neutro** | **É o motor estadual mais completo: 37 órgãos, 5 anos e leitura na nuvem. O defeito é só de registro no painel. Prioridade: ligar o registro da v2 à esquadra. Meta: luz e calendário iguais ao que o motor de fato faz.** |
| Levemente otimista | Todos os sites respondem da nuvem: não depende do computador do titular. |
| Otimista | 55 oportunidades históricas dão o calendário de editais do Estado. |
| Extremamente otimista | Com 5 anos por órgão, o sistema prevê a próxima rodada de cada secretaria e prepara a associação antes. |
