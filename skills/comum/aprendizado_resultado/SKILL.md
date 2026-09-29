---
name: aprendizado_resultado
description: A cada 100 erros de um Piloto, mede onde falhou e grava parâmetros de busca melhores.
---

# comum/aprendizado_resultado

**Quando carrega:** a cada pouso (Espião e Interceptador)  
**Usa:** src/skills/aprendizado.py → config/parametros_pilotos.json · estado/aprendizado/ciclos.jsonl

## Instrução
Erro = missão sem resultado. A cada 100 erros novos: (1) condições que mais faltam ganham expressões novas na skill de
PDF; (2) origens com rendimento abaixo de 25% vão para o fim da fila do Interceptador; (3) rotas do site oficial em
ordem do que funciona; (4) no Espião, missões que quase nunca rendem perdem vagas no voo e termos que marcam
'fora do objeto' passam a ser descartados na origem. Os Pilotos leem os parâmetros na missão seguinte.
