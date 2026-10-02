---
name: terceiro_setor
description: Ler sites especializados no terceiro setor (ABCR, Observatório, agregadores, GIFE, recorrência).
---

# motores/terceiro_setor

**Quando carrega:** a cada leitura de um canal desta família (config/skills_motores.json)  
**Falhas típicas:** contrato_violado / falha_parcial — plano em config/linha_producao.json › planos_de_correcao

## Instrução
Agregador NÃO é fonte oficial: extraia o financiador e mande ao Interceptador o site oficial (o registro com link de agregador ou de buscador vai à fila de reprocessamento, não ao lixo). Respeite o robots.txt: site que proíbe robôs é pausado com o motivo registrado (ex.: Prosas). O mesmo edital aparece em vários agregadores: isso é CORROBORAÇÃO, não duplicata a apagar.

## Lições aprendidas
- 02/10 — Prosas: robots.txt proíbe robôs; motor pausado.
- 02/10 — 62 registros com link de buscador estavam se perdendo; agora vão à fila de reprocessamento.
