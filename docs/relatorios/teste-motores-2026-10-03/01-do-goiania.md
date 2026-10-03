# Motor 01 — Diário Oficial do Município de Goiânia (`do-goiania`)

**Veredito:** workflow FUNCIONANDO · coleta PARCIAL · resultado FUNCIONANDO · histórico de 3 anos FALHA (próprio).
Há passado na base por outro motor.

## Workflow

- **Agenda:** todos os dias, às 06:23, 12:53 e 20:23. O disparo é `agenda-motores.yml` → `monitoramento-diario.yml`
  (fontes=do-goiania) → `src.sensores` → `src/diario_goiania.py` (motor-01 v2, 01/10).
- **Testes:** `tests/test_motor01_diario_goiania.py` passa.
- **Leituras:** 45 registradas; a última foi em 02/10, às 14:31 (Brasília). A luz está **verde**: coletou hoje, com 2
  achados.
- **Calendário:** 01 e 02/10 aparecem como "parcial". Isso é correto, porque uma das duas rotas não roda na nuvem (ver
  abaixo).

## Onde coleta

| Rota | Endereço | Situação |
|---|---|---|
| A — Querido Diário (API) | `api.queridodiario.ok.org.br/gazettes` (município 5208707) | **Lendo**: 10 consultas, 9 edições, de 17/09 a 30/09 |
| B — Portal da Prefeitura | `goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp` | **Não lê na nuvem**: o portal recusa IP estrangeiro e fica para a coleta no computador do titular, que não registrou leitura |

Teste ao vivo: os dois PDFs que o motor abriu na última leitura responderam HTTP 200 (edições de 28/09 e 30/09). A
conferência no navegador do titular ficou pendente, porque o Chrome não respondeu.

## Resultado

- **Atos lidos:** 107. Desses, 2 foram classificados como OPORTUNIDADE, 78 como ACOMPANHAR e 27 como RUÍDO.
- **Acerto:** *SEGENP — Edital nº 001/2026, Termo de Colaboração com OSC (MROSC)*, publicado em 25/09, com inscrições
  até 26/10/2026. É oportunidade real, está no mapa e tem livro (`op-415e2d6da023`).
- **Contagem dobrada:** os "2 achados" são **o mesmo edital** contado duas vezes (o mesmo id aparece duas vezes em
  `estado/diario_goiania.json › atos`). Há 1 oportunidade única.
- **Omissão possível:** o Querido Diário não tem a edição de 29/09 nem as de 01 e 02/10 (atraso de 2 dias). O que saiu
  nessas edições só será visto quando o Querido Diário as publicar, ou pela rota B, no computador do titular.

## Histórico de 3 anos (desde 03/10/2023)

- **Próprio:** 1 registro, de 2026. O motor só processou as edições a partir de 17/09/2026. **Não há carga dos 3
  anos.**
- **Correlato:** a base tem 269 indícios de Goiânia pelo motor Querido Diário. São 56 de 2023, 55 de 2024, 34 de 2025
  e 41 de 2026. Eles **não passaram** pela classificação de atos do motor 01 (MROSC, prazo, órgão).
- **Recuperação possível:** a API do Querido Diário aceita período (`published_since`/`until`). A carga de 3 anos é
  viável, com cerca de 750 edições.

## Correções, por prioridade

1. **Carga histórica de 3 anos pela rota A.** Reprocessar as edições de out/2023 a set/2026 com o classificador de atos,
   mês a mês, gravando as oportunidades passadas como encerradas, com o órgão, o objeto e o mês típico.
2. **Rota B:** ligar a coleta local no computador do titular. Ela fecha o atraso de 2 dias do Querido Diário.
3. **Não contar o mesmo ato duas vezes** (deduplicar `atos` por id antes de contar os achados).

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Na nuvem, o motor vê Goiânia com 2 dias de atraso e sem o portal oficial. Um edital curto pode abrir e fechar sem ser visto. |
| Pessimista | Os "2 achados" são 1, e o painel infla o resultado. |
| Levemente pessimista | 78 atos em ACOMPANHAR em duas semanas é muito para revisar à mão. |
| **Neutro** | **Funciona e acerta (MROSC real, com prazo). Prioridade: carga dos 3 anos pelo Querido Diário e rota local para o atraso. Critério de qualidade: zero edição de dia útil sem leitura em 48 horas.** |
| Levemente otimista | O classificador por ato (tipo, regime, público) separa bem o ruído: 27 descartes corretos. |
| Otimista | Os 269 indícios históricos já estão na base. Basta passá-los pelo classificador para ter o mapa de 3 anos. |
| Extremamente otimista | Com o histórico, o motor prevê o mês em que cada secretaria abre chamamento. |
