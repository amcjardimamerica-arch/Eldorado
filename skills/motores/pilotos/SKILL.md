---
name: pilotos
description: Pilotos (Espião e Interceptador): buscar oportunidades FORA dos canais e confirmar na fonte oficial.
---

# motores/pilotos

**Quando carrega:** a cada leitura de um canal desta família (config/skills_motores.json)  
**Falhas típicas:** falha_parcial (busca bloqueada: Google Notícias como reserva) — plano em config/linha_producao.json › planos_de_correcao

## Instrução
O Espião procura onde nenhum motor olha: use as CHAVES DE ACIONAMENTO dos livros em janela de ativação e as entidades que a rede neural marcou como prováveis e sem corroboração. O Interceptador confirma na fonte oficial: priorize a fila da rede neural (maior nota e maior incerteza primeiro) e os registros da fila de reprocessamento (link de buscador). Tudo o que achar entra na linha como BRONZE — nunca direto no mapa.

**Esteira de selos (02/10):** o Interceptador trabalha no computador do titular (scripts/interceptador_local.py, junto da coleta
local). BRONZE: com Sonnet 5.5 (esforço baixo), achar o site oficial e CONFERIR no IP do titular — abre, não é republicador e fala
do programa; até 2 tentativas. PRATA: com Opus 5.5 (esforço baixo), ler o edital (página e PDF) e extrair prazos, 12 dados e
dispensas; o código valida. Grave sempre o aprendizado: ele fica no livro e orienta a próxima tentativa.

## Lições aprendidas
- 01/10 — ciclo criativo a cada 100 pesquisas.
- 02/10 — a rede neural separa real × descartado com AUC 0,88 (as regras sozinhas, 0,50).
