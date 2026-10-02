# Esteira metódica de selos — fluxograma (02/10/2026)

A rede neural (maestro) conduz cada etapa; os motores são ferramentas da etapa de busca.

```mermaid
flowchart TD
  M0{{0 · MAESTRO — rede neural<br/>planeja o dia: o que ativar e em que ordem}} --> MB[Motores de busca<br/>ferramentas da etapa]
  MB --> COB{Cobertura do dia<br/>100%?}
  COB -- parcial ou pendente --> RD[Dispara de novo<br/>até 3 vezes no dia] --> MB
  COB -- exige IP brasileiro --> CL[Coleta local no<br/>computador do titular] --> RES
  COB -- completa --> RES[1 · RESULTADO<br/>livro existente: completa e atualiza<br/>livro novo: cria]
  RES --> B{2 · BRONZE<br/>site oficial confirmado?}
  B -- não --> IB[Interceptador no computador do titular<br/>Sonnet 5.5 · esforço baixo<br/>busca e confere no IP do titular]
  IB -- confirmou --> P
  IB -- não confirmou: 1ª tentativa --> IB
  IB -- 2 tentativas sem sucesso --> EB[(Estante de Investigação Bronze<br/>selo bronze)]
  B -- sim --> P{3 · PRATA<br/>edital, prazos e 12 dados<br/>ou dispensas validados?}
  P -- não --> AP[Opus 5.5 · esforço baixo<br/>lê o edital no IP do titular<br/>o código valida]
  AP -- validou --> O
  AP -- não validou: 1ª tentativa --> AP
  AP -- 2 tentativas sem validação --> EP[(Estante de Investigação Prata<br/>selo prata)]
  P -- sim --> O[(4 · OURO<br/>pronto para o Farol de Alexandria)]
  EB -. informação nova de um motor reabre .-> B
  EP -. informação nova de um motor reabre .-> P
  IB -. aprendizado gravado no livro .-> L[(Livro da oportunidade)]
  AP -. aprendizado gravado no livro .-> L
  M0 -. nota da rede ordena as filas .-> IB
  M0 -. nota da rede ordena as filas .-> AP
```

| Selo | Significa | Estante quando não avança |
|---|---|---|
| Bronze | oportunidade identificada; site oficial não confirmado | Estante de Investigação Bronze (após 2 tentativas) |
| Prata | site oficial confirmado; edital, prazos ou 12 dados não validados | Estante de Investigação Prata (após 2 tentativas) |
| Ouro | edital, condições e prazos completos | pronto para o Farol de Alexandria |

Site oficial confirmado = o Interceptador confirmou no IP do titular, ou o endereço é de domínio público (.gov.br, .leg.br, .jus.br, .mp.br, PNCP) e não é republicador.
