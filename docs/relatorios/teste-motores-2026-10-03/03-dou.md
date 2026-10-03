# Motor 03 — Diário Oficial da União (`dou`)

**Veredito:** workflow FUNCIONANDO · coleta FUNCIONANDO · resultado FUNCIONANDO na v2, mas a base guarda ruído das
versões antigas · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** todos os dias, às 06:23, 12:53 e 20:23. Só roda na nuvem. O disparo é `agenda-motores` →
  `monitoramento-diario` (fontes=dou) → `src.sensores` → `src/diario_uniao.py` (motor-03 v2, 01/10).
- **Testes:** o motor tem teste próprio (`tests/test_motor03_diario_uniao.py`) e aparece em mais 24 arquivos.
- **Leituras:** 50; a última foi em 02/10, às 14:34. Luz **verde**.
- **Calendário:** 01/10 aparece em azul (com oportunidade) e 02/10 como "parcial".

## Onde coleta

| Rota | Endereço | 02/10 |
|---|---|---|
| A — Leitura do Jornal (JSON da edição) | `in.gov.br/leiturajornal?data={data}&secao=do1` e `do3`, além das extras | 8 seções e 8.366 matérias (30/09 a 02/10) |
| B — busca da semana | `in.gov.br/consulta/-/buscar/dou?q={termo}&exactDate=semana` | 6 consultas |

- A leitura das 08h processou as edições do dia: na DO3 de 02/10 foram 2.334 matérias, das quais 105 de interesse.
- A das 14h34 não achou edição nova, e isso está correto (`edicoes_do_dia` vazio). Não houve dia útil sem DOU.
- Na nuvem, as seções responderam HTTP 200.

## Resultado

- **Consolidado do dia:** 73 matérias "abertas", que deram 3 OPORTUNIDADE, 82 ACOMPANHAR e 345 RUÍDO. São 11
  oportunidades únicas em 25 registros.
- **Acertos da v2:**
  - Prefeitura de Corumbá de Goiás — Aviso de Chamamento Público nº 3/2026, com prazo até 15/10/2026 (Goiás);
  - ANATER — Aviso de Seleção Pública, com prazo até 18/11/2026.
- **Ruído antigo na base:** dos 16 registros, 14 não têm data e vêm de versões anteriores à v2.
  - São extratos de termo de fomento e acordos de cooperação, ou seja, parcerias já celebradas.
  - Há também editais de pós-graduação (UFU, IFAL) e um "edital de intimação".
  - A data de publicação desses registros ficou gravada no campo de prazo.
- **Bom sinal:** a v2 manda os extratos para ACOMPANHAR (80 na fila) e não para OPORTUNIDADE.

## Histórico de 3 anos

- **Próprio:** 2 registros datados, de 2026. **Não há carga de 2023 a 2025.**
- **Correlato:** 1 registro do mesmo site, pelo Espião.
- **Recuperação possível:** a Leitura do Jornal aceita qualquer data. A carga de 3 anos é viável: cerca de 750 dias
  úteis × DO1 + DO3, com o mesmo filtro por tipo de matéria e órgão, fracionada mês a mês.
- **Ganho extra:** os extratos de termo de fomento dos 3 anos mostram **quem financiou quais OSCs**. É a melhor base
  para prever os editais recorrentes.

## Correções, por prioridade

1. **Carga histórica de 3 anos** pela Leitura do Jornal, mês a mês. Gravar à parte os avisos de chamamento (encerrados)
   e os extratos de fomento (série de financiadores).
2. **Limpar os 14 registros antigos sem data** (extratos, pós-graduação, intimação) e corrigir o prazo que guarda a
   data de publicação.
3. **Filtro de território:** vale confirmar no teste do navegador quantas das matérias "de interesse" são de Goiás e
   do DF.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | São 8 mil matérias por dia. Um aviso curto de 5 dias pode cair no ruído e nunca ser revisto. |
| Pessimista | O ruído antigo na base (14 de 16) ainda aparece no painel como se fosse do motor atual. |
| Levemente pessimista | 3 oportunidades por dia contra 82 para acompanhar sobrecarrega a revisão. |
| **Neutro** | **O motor v2 lê o DOU inteiro todo dia e acerta (Corumbá-GO, ANATER). Prioridade: limpeza do legado e carga dos 3 anos, que também alimenta a série de financiadores. Meta: nenhuma DO3 de dia útil sem leitura.** |
| Levemente otimista | A rota A não depende de busca: lê a edição como ela é publicada. |
| Otimista | Os extratos de fomento dão, de graça, o mapa de quem financia OSC no Brasil. |
| Extremamente otimista | Com 3 anos de extratos, o sistema antecipa editais federais antes de serem publicados. |
