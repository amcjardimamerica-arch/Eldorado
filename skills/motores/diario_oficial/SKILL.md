---
name: diario_oficial
description: Ler diário oficial (municipal, estadual, da União, da Justiça) e achar o ato que abre recurso para OSC.
---

# motores/diario_oficial

**Quando carrega:** a cada leitura de um canal desta família (config/skills_motores.json)  
**Falhas típicas:** formato_mudou / exige_brasil — plano em config/linha_producao.json › planos_de_correcao

## Instrução
Diário publica ATOS, não oportunidades: o chamamento vem no meio de nomeações, licitações e créditos. Leia a ÍNTEGRA do ato (não só o título), classifique com o classificador comum (src/atos_diario.py) e guarde o número do edital, o órgão, a data de publicação e o prazo. Errata, retificação, prorrogação e resultado são EDIÇÕES do livro do edital, nunca descarte. O mesmo ato reaparece em várias edições (Querido Diário repete ~12×): a linha de produção junta as repetições numa entidade só.

## Lições aprendidas
- 01/10 — motores 01–03: o corte por tamanho zerava a Seção 3 do DOU; ler inteiro.
- 02/10 — Querido Diário trouxe 108 das oportunidades reais validadas: é o canal mais valioso, apesar do ruído.
