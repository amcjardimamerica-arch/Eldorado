# Linha de produção de informação do Eldorado — fluxograma (02/10/2026)

Princípio: **cada canal só coleta; as etapas seguintes são comuns; nada é eliminado** (identificar → qualificar).
Toda mudança de etapa vai ao livro-razão (`estado/linha/razao-AAAA-MM.jsonl.gz`, só acréscimos).

```mermaid
flowchart TD
  subgraph C["1 · CAPTAÇÃO — canais (motores) e Pilotos"]
    C1[Diários oficiais<br/>Querido Diário, DO Goiânia, DO Goiás, DOU, Justiça]
    C2[Portais de chamamentos<br/>PNCP nacional, SALIC, Mapa das OSC, prefeituras]
    C3[Órgãos públicos<br/>motor estadual de Goiás, Congresso, fontes 260]
    C4[Justiça e MP<br/>destinações, TAC]
    C5[Terceiro setor<br/>ABCR, Observatório, agregadores, GIFE]
    C6[Entidades e empresas<br/>institutos, fundações, incentivadas]
    P1[Piloto Espião<br/>busca fora dos canais]
  end
  SK[[Skill da família + skills comuns<br/>config/skills_motores.json]] -.orienta.-> C
  C --> F{Leitura ok?}
  P1 --> F
  F -- não --> PC[[Plano de correção<br/>sem rendimento · falha parcial · bloqueio<br/>exige Brasil · formato mudou]]
  PC -- backoff, rota alternativa --> C
  PC -- exige IP brasileiro --> CL[Coleta local<br/>scripts/coleta_brasil.py] --> B
  PC -- robots proíbe --> PZ[Canal pausado<br/>motivo registrado]
  F -- sim --> B[(2 · BRONZE<br/>registro como chegou<br/>base de oportunidades)]
  B --> K{Contrato de dados<br/>título · URL oficial · fonte}
  K -- violado --> DLQ[(Fila de reprocessamento<br/>nunca o lixo)]
  DLQ -- Interceptador acha o site oficial --> B
  K -- injeção de instrução --> QZ[(Quarentena<br/>auditoria)]
  K -- ok --> S[3 · PRATA<br/>canal canônico + entidade resolvida entre canais<br/>corroboração = nº de canais]
  S --> RN{{4 · REDE NEURAL<br/>texto + regras como rotuladores + corroboração<br/>nota 0–1, calibrada — apoio, nunca filtro}}
  RN -- maior nota e incerteza primeiro --> FV[Fila de validação<br/>aprendizado ativo]
  RN -- prováveis sem corroboração --> P2[Piloto Interceptador<br/>confirma na fonte oficial]
  P2 --> B
  S --> O[(5 · OURO<br/>livro da Biblioteca + mapa)]
  O --> Q{6 · QUALIFICAÇÃO<br/>regras de restrição do livro}
  Q -- APLICÁVEL --> M[Mapa · Farol de Alexandria<br/>preparação · previsão · chave de acionamento]
  Q -- EM REVISÃO --> CU[Curadoria do titular]
  Q -- NÃO APLICA --> NA[Livro mantido e marcado<br/>arquivamento só manual]
  FV --> V[Decisão humana]
  V -- vira rótulo --> RN
  M -- previsão: 30 dias antes --> LX[Léxico temporário<br/>chave do livro nos motores do índice]
  LX --> C
  M -- empresas sem publicação --> P1
```

## Planos de correção (previstos, aplicados a cada ciclo — `docs/dados/planos_correcao.json`)

| Diagnóstico | Quando | Plano |
|---|---|---|
| sem rendimento | 5+ leituras sem achado (só motores de descoberta) | robots.txt → página em JavaScript (procurar API/JSON) → rotas alternativas → reduzir frequência e mandar o domínio ao Espião |
| falha parcial | falhas em 3+ dos últimos 7 dias | backoff, reordenar rotas, registrar rota morta |
| bloqueio | 403/429/WAF | espaçar (Crawl-Delay), mudar horário; 403 persistente = exige IP brasileiro |
| exige Brasil | o site recusa o IP da nuvem | coleta local; as outras fontes do motor continuam; não conta como falha |
| formato mudou | zero itens hoje depois de dias com itens | comparar o HTML, alerta, atualizar o leitor e a lição da skill |
| contrato violado | sem título, sem URL oficial, URL de buscador | fila de reprocessamento → Interceptador → volta à linha |
| injeção | instrução ao modelo no texto coletado | quarentena (não vira livro nem prompt) |
