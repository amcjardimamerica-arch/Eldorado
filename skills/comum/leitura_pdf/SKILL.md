---
name: leitura_pdf
description: Abrir e ler PDF (texto e tabelas) e buscar expressões com o contexto em volta — a identificação mais importante.
---

# comum/leitura_pdf

**Quando carrega:** toda leitura de edital (Interceptador) e todo PDF de anexo ou diário  
**Usa:** src/skills/leitura_pdf.py (pdfplumber; sem ele, pypdf)

## Instrução
Antes do texto do edital você recebe TRECHOS-CHAVE: cada um traz a condição ([Prazo de inscrição], [Resultado],
[Prazo de recurso], [Cronograma], [Valor], [Requisitos]…) e o contexto em volta da expressão encontrada.
1. Comece pelos trechos-chave; só depois leia o resto.
2. Linhas "[TABELA da página N]" são tabelas do PDF (cronograma, valores): cada linha é "etapa | data".
3. Uma data só vale para a condição se o trecho disser qual etapa ela é (inscrição, resultado, recurso).
4. Copie o trecho exato que comprova; nunca deduza data que não esteja escrita.
