---
name: descobrir_entidades_novas
description: Descobrir empresas, institutos, fundações e entidades ligadas ao terceiro setor que NÃO estão no cadastro.
---

# espiao/descobrir_entidades_novas

**Quando carrega:** missões 'descobrir' do Espião (a maioria do voo)  
**Usa:** src/piloto.py missao_descobrir · src/skills/cadastro.py (22 mil nomes conhecidos)

## Instrução
Sua missão é achar o que o sistema ainda NÃO conhece: empresa, instituto, fundação, associação empresarial,
cooperativa ou entidade com vínculo com o terceiro setor (edital próprio, programa social, patrocínio, doação,
leis de incentivo). Goiás primeiro. Quem já está no cadastro (rankings, incentivadores do SALIC, fichas) NÃO é
descoberta — ignore e siga. Sinal forte: página 'instituto', 'responsabilidade social', 'edital', 'chamada',
'investimento social'. Sinal fraco: notícia genérica, vaga de emprego, relatório financeiro.

## Lições aprendidas
- 30/09 — de 43.230 missões, só 1,5% tiveram resultado. Catalogar (0,1%) e prospectar (0,2%) saíram do voo:
  os sites-catálogo já foram varridos e a prospecção achava empresas já conhecidas.
- Busque ENTIDADES e PROGRAMAS novos pelas áreas da associação (assistência social, criança e adolescente, pessoa
  idosa, cultura, saúde, esporte), sempre com "organizações da sociedade civil" na consulta e Goiás primeiro.
- 01/10 — o buscador (DuckDuckGo) corta depois de 2 consultas em sequência: o resultado vazio é BLOQUEIO, não falha
  da consulta. Intervalo de 10 s entre buscas, nova tentativa após 25 s, e a mesma consulta no máximo 3 vezes por dia.
- Termos que rendem (7 dias): conanda, empresarial, saúde, doação, voluntariado, parceiros. Termos que falham: regiões,
  baixa cobertura, mapeados (sobras das perguntas genéricas do briefing).
