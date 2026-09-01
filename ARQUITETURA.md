# Arquitetura

## O procedimento em 5 passos

```mermaid
flowchart TD
    subgraph ELD["🔶 ELDORADO — descoberta e verificação"]
        P1["1 · DESCOBRIR<br/><small>mapear oportunidades e fontes de recursos</small>"]
        P2["2 · CONFIRMAR<br/><small>elegibilidade, requisitos, documentos e anexos</small>"]
    end
    subgraph INT["🔷 INTEGRAÇÃO"]
        P3["3 · ENQUADRAR<br/><small>Biblioteca alimentada · IA cruza requisitos<br/>aderência, viabilidade e histórico</small>"]
    end
    subgraph FAR["🔵 FAROL DE ALEXANDRIA — decisão e preparo"]
        P4["4 · DECIDIR<br/><small>entidades com chances reais<br/>pasta do edital e documentos separados</small>"]
        P5["5 · PREPARAR<br/><small>documentos preenchidos, prontos para download<br/>nota técnica do que falta</small>"]
    end

    F["Fontes: diários oficiais, PNCP,<br/>portais, secretarias, ministérios"] --> P1
    P1 -->|identificação registrada<br/>com URL e evidência| C{"campanha de<br/>completude<br/>até 30 dias"}
    C -->|edital integral<br/>+ datas + modelos| P2
    C -->|ainda incompleto| M["monitoramento na Bússola<br/><small>tenta todo dia</small>"] --> C
    C -->|30 dias sem completar| H["expirado —<br/>revisão humana"]
    P2 -->|verificação DUPLA<br/>fonte + conteúdo| P3

    P3 --> B[("BIBLIOTECA DE ALEXANDRIA<br/>leis · oportunidades · associações")]
    B -->|histórico: o que é cobrado,<br/>quem venceu e por quê| IA["IA por tarefa<br/><small>extração → análise → parecer</small>"]
    IA -->|parecer com aderência<br/>e viabilidade| P4

    P4 -->|bloqueio eliminatório| D["descartada<br/><small>motivo registrado</small>"]
    P4 -->|chance real| PA["pasta do edital<br/>dentro da entidade"] --> P5
    P5 --> DL["documentos para download"]
    P5 --> NT["NOTA TÉCNICA<br/><small>o que falta e como obter</small>"]

    style P1 fill:#FFF3E4,stroke:#C05E00
    style P2 fill:#FFF3E4,stroke:#C05E00
    style P3 fill:#F3EEFF,stroke:#7B4BE0
    style P4 fill:#E8F1FB,stroke:#0B4EA2
    style P5 fill:#E8F1FB,stroke:#0B4EA2
    style B fill:#FDF6E3,stroke:#C9A227
    style H fill:#FDECEA,stroke:#B8433A
    style NT fill:#FFFBEA,stroke:#B8860B
```

### O que cada passo faz, e o que ele não faz

| # | Passo | Quem executa | Entrega | Regra dura |
|---|---|---|---|---|
| 1 | **Descobrir** | Eldorado | oportunidade identificada com fonte, URL e evidência hasheada | identificação em diário é começo, não fim |
| 2 | **Confirmar** | Eldorado | edital integral, datas de inscrição, requisitos e anexos-modelo | verificação **dupla** (fonte + conteúdo); sem isso não passa |
| 3 | **Enquadrar** | Eldorado → Farol | dados na Biblioteca; IA cruza requisitos × associações com apoio do histórico | modelo adequado a cada tarefa; pacote mínimo; sem credencial, só a parte determinística |
| 4 | **Decidir** | Farol (automático) | entidades com chance real, pasta do edital criada, documentos separados | **nenhuma informação nova** é criada; o que falta é declarado |
| 5 | **Preparar** | Farol (automático) | modelos preenchidos no próprio PDF, prontos para download | dado ausente vira **nota técnica** com o caminho para obtê-lo |

As etapas 4 e 5 **não dependem de ação do titular** — rodam sozinhas assim que
o edital chega completo e o parecer aponta enquadramento.

## Fluxo completo (visão geral)

```mermaid
flowchart TD
  subgraph FASE1[Fase 1 · ELDORADO — amplitude máxima, custo zero]
    S[Sentinela diária 5h30<br/>hash de candidatos] --> Q[Fila de fontes alteradas]
    Q --> C[Varredura profunda seg/qua 6h<br/>62 fontes HTML/RSS · robots.txt · intervalo]
    A1[PNCP — API oficial<br/>credenciamento e concurso] --> M
    A2[Querido Diário — API<br/>diários oficiais municipais] --> M
    C --> M[Base única deduplicada por URL canônica<br/>merge preserva revisão humana]
    I[Camada capilar — imprensa/anúncios RSS<br/>por termo × UF × emissor] --> P[pistas_imprensa.jsonl<br/>NUNCA entra direto na base]
    P -- confirmar_pista.py<br/>URL oficial obrigatória --> M
  end
  M --> VA{Verificação<br/>capturada → verificada}
  VA -- assistida: página primária + termos + sem injeção --> V[verificada_primaria]
  VA -- humana: scripts/promover.py --> V
  subgraph FASE2[Fase 2 · FAROL DE ALEXANDRIA — seleção e enquadramento]
    V --> T[Triagem determinística ≥60<br/>idempotente: caso aberto não reprocessa]
    T --> K[Caso da associação<br/>universo isolado]
    K --> X[IA extração de requisitos<br/>modelo econômico]
    X --> G{Portão eliminatório<br/>com requisitos reais}
    G -- bloqueio objetivo --> N[Decisão fundamentada:<br/>sem chances + o que falta<br/>conselho não convocado]
    G -- elegível --> CO[Conselho: 7 lentes isoladas<br/>modelo intermediário]
    CO --> PF[Parecer final<br/>modelo mais avançado]
    PF --> DOCS[submissao/ — documentos finais<br/>sem referência a IA, sem pendências]
    PF --> PR[07_pacote_presidente.md<br/>decisão, prazos, orientações objetivas]
    N --> PR
  end
  M --> AP[Aprendizado automático<br/>padrões 2+ ocorrências · previsão de janelas]
  AP --> PAINEL[Painel estático + GitHub Pages]
  M --> PAINEL
  PR --> PAINEL
```

## Contrato de dados

Uma oportunidade só atravessa o portão de confirmação quando possui `titulo`, URL primária, `fonte_id`, `coletado_em` e pelo menos um trecho de evidência. Pista social/imprensa reforça, mas nunca substitui, a fonte primária. Dados desconhecidos permanecem `null`; não são estimados.

A base é **deduplicada globalmente pela URL canônica** (`novo_id`): o mesmo edital visto por fontes diferentes é um único registro, com `fontes_observadas` acumulando as origens. A recoleta usa `merge_registro`: **status definidos por humano (ou verificação assistida auditada) nunca regridem** e os campos `requisitos`, `notas`, `verificado_*` são preservados.

O matching tem duas etapas:

1. **Portão eliminatório**: natureza jurídica, território, área, antiguidade, inscrições/certificações e prazo — alimentado pelos `requisitos` extraídos do edital (IA de extração) e validáveis por humano (`requisitos_validados`).
2. **Pontuação explicável**: aderência temática, territorial, experiência, documentação, capacidade financeira e histórico com o financiador.

Cada associação recebe execução independente e diretório exclusivo; o agregador do painel lê apenas resultados finais.

## Ciclo de operação

```mermaid
flowchart LR
  D1[Diária 5h30<br/>sentinela] --> D2[Seg/Qua 6h<br/>executar_diario]
  D2 --> D3[Diária 6h45<br/>publicar painel]
  W[Domingo 6h35<br/>carga histórica mês a mês<br/>até concluir 5 anos] --> D2
  Mo[Mensal dia 1º<br/>revisão normativa por hash<br/>issue de revisão humana] --> D2
```

`executar_diario` roda as etapas em isolamento (falha em uma não derruba as outras) e `resumo_execucao` decide alertas: **>50% de fontes falhando, 3 execuções sem novidade ou etapa quebrada abrem issue** — o sistema não falha em silêncio.

## Economia de tokens e de espaço

- O pipeline de descoberta é 100% biblioteca-padrão: **zero tokens** na coleta, dedupe, triagem, dossiês, aprendizado e painel.
- IA entra **apenas** no Farol (caso aberto) e em três papéis com modelo dimensionado por tarefa (`config/ia.json`): extração (econômico) → conselho (intermediário) → parecer/documentos (mais avançado). Bloqueio eliminatório objetivo **dispensa o conselho**.
- Limites duros por execução: casos com IA, tamanho de edital, tamanho de pacote e tokens de saída são configuráveis; todo uso fica em `estado/ia_uso.jsonl`.
- Espaço: JSONL compacto, dossiês compactos (`eventos.compacto.json`), derivados de documentos em `.gz`, históricos por edital apenas com o diff de campos rastreados.

## Aprendizado com editais anteriores

`src/aprendizado.py` roda a cada execução: requisitos recorrentes viram **padrão só com duas ocorrências validadas** (antes disso, hipótese) e a recorrência mensal de publicação em anos distintos vira **previsão de janela** (`estado/previsoes.json`), sempre rotulada hipótese. É a base para preparar a associação ANTES do edital abrir — documentos e certificações prontos na janela provável.

## Limite honesto de cobertura

“Todo o país” significa: 62 fontes catalogadas (27 portais estaduais na raiz + federais + setoriais + privadas + internacionais), PNCP (todos os entes) e Querido Diário (diários municipais) — cobertura federativa real e expansível, não a promessa impossível de ler toda a internet. Páginas específicas continuam entrando em `config/fontes.json` após validação (`estado/cobertura_catalogo.json` lista a fila dos 260 pontos do acervo ainda descobertos). Portais autenticados (Goodstack, UN Partner Portal) permanecem manuais, sem burlar cadastro.
