# Motor 10 — MPU: MPF, MPDFT, MPM, MPT nacional, CNMP e FDD (`mpu-destinacao`)

**Veredito:** workflow PARCIAL (motor criado em 02/10 às 19:27; ainda não rodou) · coleta FUNCIONANDO (38 fontes
mapeadas: 20 lidas na nuvem, o resto regra ou navegador) · resultado FUNCIONANDO (sinal do FDD a conferir) · histórico
de 3 anos PARCIAL.

## Workflow

- **Agenda:** todos os dias, às 16:23, na nuvem, com a cadência de cada fonte (RSS e estado de página 7 a 30 dias). O
  módulo é `src/ministerios_publicos.py` (`ler_parte("mpu-destinacao")`, tudo o que não é MP-GO nem MPT-GO).
- **Leituras:** nunca rodou com o id novo. A leitura do antecessor `plat-mp-destinacoes-reparacao` (19:10 de 02/10)
  cobriu estas fontes.

## Onde coleta (leitura de 02/10)

| Órgão | Fontes lidas na nuvem | Itens |
|---|---|---|
| MPT nacional | busca RSS "edital cadastramento entidades" e feed geral | 10 + 0 |
| MPF | notícias, bens para doação e transparência da PR-GO; busca nacional; página-modelo da PR-BA | 0, 0, 0, 10, 2 |
| MPDFT | tag "medidas alternativas"; notícias de 2026; TACs | 11, 1, 0 |
| MPM | busca "prestação pecuniária" | 0 |
| MPU | sitemap | 0 |
| FDD/CFDD (Ministério da Justiça) | capa, **seleção em andamento**, seleções anteriores, atas, convênios | ver abaixo |

- **Não acessadas, por regra:**
  - por robots: os PDFs do MPDFT em `/portal/images/`;
  - por exigir login: o Sistema de Destinações do MPT e o MPF Serviços (gov.br);
  - por exigir navegador: o Diário do MPT, o CNMP Aptus e os atos do CNJ.
- A conferência no navegador do titular ficou pendente, porque o Chrome não respondeu.

## Resultado

- **Sinal importante:** *FDD/CFDD — "seleção em andamento"*. A página do Fundo de Defesa de Direitos Difusos **deixou
  de dizer "Não há"**.
  - O motor registrou o sinal como OPORTUNIDADE para conferência.
  - Um edital do FDD é recurso federal relevante para OSC: a proposta vai pelo Transferegov.
  - **É preciso abrir a página e confirmar** número, prazo e áreas.
- **MPF PR-GO:** o chamamento de cadastro de 09/10/2025 tem o link do edital quebrado (404 em 02/10). Fica a pendência
  do presidente de pedir o edital à PR-GO.
- **MPDFT:** Edital PGJ 1/2026 (cadastro de pessoas jurídicas sem fins lucrativos) só para o DF. Fica em acompanhar.

## Histórico de 3 anos

- O inventário traz:
  - MPF: 2024 (1), 2025 (5) e 2026 (2);
  - MPDFT: 2024 (1) e 2026 (6);
  - MPT nacional: 2024 (1), 2025 (9) e 2026 (2);
  - MPM: 2024 (1) e 2026 (1).
- **Lacuna:** 2023 está quase vazio.
- **Melhor rota para completar:** a página "seleções anteriores" do FDD, com PDFs de anos de editais, legíveis na
  nuvem.

## Correções, por prioridade

1. **Conferir hoje o FDD**, na página "seleção em andamento". Se houver edital, levar ao titular com prazo e
   enquadramento.
2. **Carga de 3 anos do FDD** pelas "seleções anteriores": valores, áreas, prazos e mês típico.
3. **Corrigir a quebra dos sensores** e confirmar a leitura diária às 16:23 com o id novo.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Um alerta de "seleção em andamento" sem número nem prazo pode ser falso alarme: a página pode só ter mudado de texto. |
| Pessimista | Metade das fontes não é lida (login, robots, JavaScript). |
| Levemente pessimista | O MPF de Goiás nem tem página de destinação. A rota depende de notícia. |
| **Neutro** | **Mapeamento exemplar e respeitoso (robots e login). O sinal do FDD é a prioridade do dia. Depois, a carga histórica do FDD. Qualidade: todo alerta do FDD confirmado no PDF do edital em 24 horas.** |
| Levemente otimista | O MPT nacional por RSS de busca é leve e estável. |
| Otimista | Um edital do FDD aberto pode valer milhões para projetos de direitos difusos. |
| Extremamente otimista | Com o histórico do FDD, a associação prepara um projeto alinhado às prioridades do Conselho Federal Gestor antes do próximo edital. |
