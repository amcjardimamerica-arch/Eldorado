---
name: cronograma
description: Mapear inscrição, resultado e recurso a partir do cronograma do edital (quase sempre tabela em PDF).
---

# interceptador/cronograma

**Quando carrega:** leitura de edital  
**Usa:** skill leitura_pdf (tabelas) + expressões ampliadas pelo aprendizado

## Instrução
As três condições que mais faltam (prazo de recurso, resultado, prazo de inscrição) moram no CRONOGRAMA.
Procure a tabela "[TABELA …]" ou o item "cronograma/calendário". Para cada etapa, a data ao lado: inscrição
(início e fim), resultado preliminar/final, recurso (prazo em dias ou data). Se o edital disser que não há recurso
ou que a inscrição é contínua, isso é DISPENSA — com o trecho.
