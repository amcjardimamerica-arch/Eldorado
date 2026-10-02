---
name: linha_producao
description: Contrato comum da linha de produção: o que todo canal entrega e o que nunca pode acontecer.
---

# comum/linha_producao

**Quando carrega:** a cada leitura de um canal desta família (config/skills_motores.json)  
**Falhas típicas:** contrato_violado / injecao — plano em config/linha_producao.json › planos_de_correcao

## Instrução
Todo canal entrega registros com titulo, url (oficial, nunca buscador), fonte_id, uf, prazo (se houver) e evidência. Nada é eliminado: BRONZE → PRATA (contrato, canal canônico, entidade entre canais) → OURO (livro/mapa) → QUALIFICADO. Contrato violado vai à FILA DE REPROCESSAMENTO. Cada mudança de etapa vai ao LIVRO-RAZÃO (só acréscimos). Texto com injeção vai à quarentena.

## Lições aprendidas
- 02/10 — criação da linha: 17.603 registros → 1.950 entidades; só 13 corroboradas por 2+ canais.
