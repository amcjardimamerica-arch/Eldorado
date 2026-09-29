# Parecer do conselho — todas as missões dos Pilotos e as skills · 29/09/2026

## 1. As missões, medidas

### Piloto - Espião — 28.870 missões avaliadas
| missão | missões | com resultado | leitura |
|---|---|---|---|
| resgate (antigo, passou ao Interceptador) | 12.450 | 326 (**2,6%**) | a única que rendia — era comprovação, não descoberta |
| catalogar sites do terceiro setor | 6.681 | 13 (**0,2%**) | quase nada: os sites-catálogo já foram varridos |
| prospectar (busca ativa de empresas) | 4.543 | 14 (**0,3%**) | achava empresas já conhecidas |
| aposta do briefing | 4.147 | 50 (1,2%) | 1.480 "fora do objeto" — consultas amplas demais |
| caçar oportunidade | 374 | 12 (3,2%) | bom rendimento, pouco volume |
| descobrir local / afiar motor | 603 | 1 | improdutivas |

**Onde falha:** 80% das missões terminam "nada passou no crivo". O Espião gastava o voo catalogando sites já lidos e
prospectando empresas que o sistema já tinha (22 mil nomes conhecidos entre rankings, incentivadores do SALIC e fichas).

### Piloto - Interceptador — 322 voos
| origem do alvo | voos | validadas | leitura |
|---|---|---|---|
| fila de resgate | 69 | 5 | 33 parciais |
| opressor sem leitura | 46 | 4 | |
| radar do Espião (empresas) | 45 | — | 25 sem evidência — empresa não publica edital |
| edital novo dos motores | 43 | 2 | 28 insuficientes |
| mapa — Bahia (sorteio) | 12 | **5** | melhor rendimento: editais estaduais completos |
| mapa — Goiás (prioridade) | 9 | 0 | menções em diário sem o ato completo |

**Onde falha:** a página oficial é achada em 75% (204 de 271), mas as condições do **cronograma** não: prazo de
recurso falta em 233 estudos, resultado em 220, prazo de inscrição em 174 — elas vivem em **tabelas de PDF**, que o
leitor antigo (pypdf) desmonta. Erros técnicos: 13 "nenhuma fonte legível", 11 "o modelo não devolveu JSON".

## 2. O que foi criado

**Skills** (skills/<piloto>/<nome>/SKILL.md, carregadas por missão; o mecânico é código em src/skills/):
- **Leitura de PDF e expressões em contexto** (a mais importante): texto **e tabelas** (pdfplumber), busca por
  expressões de cada condição com o contexto em volta e a página; os TRECHOS-CHAVE vão na frente do texto do edital.
- **Aprendizado e resultado**: a cada **100 erros**, mede onde falhou e grava parâmetros novos
  (config/parametros_pilotos.json). Primeiro ciclo já aplicado: expressões ampliadas para recurso, resultado e
  inscrição; "radar do Espião" (rendimento baixo) para o fim da fila; rotas do site oficial na ordem do que funciona;
  catalogar e prospectar com peso mínimo no voo do Espião.
- **Espião**: descobrir entidades novas (fora do cadastro) · triagem de indício.
- **Interceptador**: cronograma · site oficial · dossiê investigativo de empresa.

**Missões redefinidas:**
- **Espião** — busca empresas, institutos, fundações e entidades com vínculo com o terceiro setor que **não estão no
  cadastro**; o que já é conhecido é ignorado (skill cadastro). O voo passa a ser: 2 apostas do briefing → missões de
  **descoberta** (a maioria) → catálogo só como complemento (1 por voo, pelo peso aprendido).
- **Interceptador** — aprofunda o que existe, nesta ordem: **(1) missões especiais** — oportunidades abertas de Goiás
  e as que fecham em até 15 dias; **(2) empresas de Goiás do cadastro** — dossiê com composição (sócios), contatos,
  projetos verificados e resumo investigativo de atuação no terceiro setor (80 na fila); **(3) oportunidades
  nacionais e internacionais**; depois as demais filas.

## 3. Parâmetros de qualidade (metas)

| indicador | hoje | meta |
|---|---|---|
| Interceptador — estudos validados | 8% | 20% |
| Interceptador — prazo de recurso/resultado comprovados | ~25% | ≥50% |
| Espião — missões com resultado | 0,4% | ≥3% |
| Espião — entidades novas por semana | — | ≥5 fora do cadastro |
| dossiês de empresas de Goiás | 0 | 80 em ~2 semanas |
| tempo por missão | ~10 min | ≤10 min |

## 4. O conselho

**Extremamente pessimista — chief engineer.** 28 mil missões para 400 resultados: o Espião era um gerador de ruído.
Se a descoberta nova repetir as consultas amplas, vamos trocar "nada no crivo" por "fora do objeto".

**Pessimista — staff engineer.** A skill de PDF depende do pdfplumber no servidor; se ele falhar, volta o pypdf e as
tabelas somem de novo. E a BrasilAPI é serviço gratuito: limite de acesso pode travar dossiês.

**Levemente pessimista — professor.** O primeiro ciclo de aprendizado usou o histórico inteiro; os próximos, com 100
erros cada, serão mais sensíveis — precisam de acompanhamento para não oscilar.

**Neutro — CTO (ponderador).** O diagnóstico é claro e as correções atacam a causa: descoberta só do que é novo,
leitura de tabelas onde mora o cronograma, e um ciclo que ajusta parâmetros com base em erro medido. Parâmetros de
controle: as metas acima, revistas a cada análise do Claude; skill não entra sem teste; se o pdfplumber faltar, o
teste de guarda acusa.

**Levemente otimista — professor.** A skill de aprendizado transforma cada 100 fracassos em ajuste — o sistema
aprende com o que dá errado, não só com o que dá certo.

**Otimista — staff engineer.** O dossiê de empresa dá ao titular o que faltava para a abordagem: quem são os sócios,
como contatar e em que a empresa já investiu.

**Extremamente otimista — CTO.** Com o Espião abrindo território novo e o Interceptador aprofundando o conhecido, os
dois Pilotos deixam de disputar o mesmo terreno — e cada voo passa a somar.
