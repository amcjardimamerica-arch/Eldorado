# Verificação das 23 oportunidades abertas e relatório para o filtro dos motores (02/10/2026)

**Pedido do titular:**

- Verificar os 12 itens de cada uma das 23 oportunidades abertas do painel (23/628).
- Atualizar o livro de cada uma, arquivar como encerrada ou excluir o que não se aplica à associação.
- Gerar um relatório para que os motores melhorem o filtro.
- Trabalhar em blocos por estado, começando por Goiás e pelas nacionais.

**Universo:** as 23 "confirmadas com o mínimo" de `docs/dados/fluxo_oportunidades.json`. No dia, a contagem de possíveis já era 651, não 628.

**Fonte:** sempre o site oficial do órgão ou do patrocinador, ou o PDF do edital publicado por ele.

- **Goiás:** lido pelo navegador do titular, porque os sites `.go.gov.br` recusam IP estrangeiro. PDFs foram lidos com pdf.js, e o de Goiatuba, que é digitalizado, por imagem.
- **Demais:** lidos por três pesquisadores em paralelo, com WebFetch.

**Prompt injection:** nenhuma encontrada nas 23 páginas e PDFs.

## 1. Resultado por bloco

| Bloco | Oportunidade | Motor | Decisão | Aplica à A.M.C. | Prazo antes → depois | Itens antes → depois |
|---|---|---|---|---|---|---|
| **Goiás** | SEGENP Goiânia, Edital 001/2026 "Natal no Parque" (termo de colaboração, até R$ 5 mi) | do-goiania | válida aberta | talvez (grande porte) | 26/10 → 26/10 | 7 → 12 |
| Goiás | Secult GO, Ocupa Goiás – Brasilidades & Futuros 2027 | plat-secult-go | válida aberta | talvez (proponente cultural) | 29/10 → 29/10 | 9 → 9 |
| Goiás | Goiás Social (SEDS), Chamamento 001/2026 Socioeducativo | Piloto-Interceptador | válida aberta | não (exige experiência socioeducativa) | 15/10 → **16/10** | 8 → 12 |
| Goiás | TJGO, credenciamento de entidades de reciclagem (fluxo contínuo) | pncp-api | válida aberta | não (estrutura de coleta) | 22/07/2031 → 22/07/2031 | 4 → 10 |
| Goiás | Goiatuba, Edital 004/2026 PNAB Ciclo 2 | capitaai | fora da abrangência | não (só Goiatuba) | 13/10 → 13/10 | 9 → 9 |
| Goiás | Emenda estadual (ALEGO) | calendário legislativo | válida aberta (janela interna) | **sim** (carteira) | 30/11 → 30/11 **rotulado como meta interna** | "12" → 11 |
| Goiás | Emenda municipal (Câmara de Goiânia) | calendário legislativo | válida aberta (janela interna) | **sim** (carteira) | 30/11 → 30/11 **rotulado como meta interna** | "12" → 11 |
| Goiás | Itaberaí, prestação pecuniária (1ª Vara) | judiciario-cnj-tjgo | **arquivada (encerrada)** | não | **18/08/2027 → 18/08/2020** | 7 → 12 |
| Goiás | Nova Iguaçu de Goiás, Edital 001/2026 | do-goias | **descartada** | não (jogos escolares) | 02/10 → — | 5 → 5 |
| **Brasil** | BNDES Periferias, 6º ciclo | abcr | válida aberta | talvez (entrar na rede de outra proponente) | 04/12 → 04/12 | 12 → 12 |
| Brasil | Instituto ACP, Chamada Aberta 2026 | plat-piloto-aberto | válida aberta | talvez | fluxo contínuo | 12 → 12 |
| Brasil | Fundação Maria Emília, FME Transforma | abcr | válida aberta | não (coordenador com doutorado) | 30/10 → 30/10 | 12 → 12 |
| Brasil | Fundo Baobá, Marielle Franco 2ª ed. | plat-gife | válida aberta | não (85% de liderança de mulheres negras) | 19/10 → **sem fonte** | 0 → 9 |
| Brasil | Grupo Equatorial, CPP 001/2026 (Goiás) | observatorio-3setor | válida aberta | não (OSC só com CEBAS) | 09/11 → 09/11 | "12" → 12 (resultado corrigido) |
| Brasil | Zurich, incentivo fiscal 2026 | Piloto-Espião | válida aberta | não (projeto já aprovado em lei de incentivo) | 19/10 → 19/10 | 12 → 12 |
| Brasil | Instituto Impactarte | observatorio-3setor | pendente | talvez | 31/12 → **sem fonte** | "12" → 3 |
| Brasil | Emenda federal (PLOA 2027, PLN 24/2026) | calendário legislativo | válida aberta (janela interna) | talvez | 30/11 → 30/11 **rotulado como meta interna** | "12" → 11 |
| Brasil | Balsas/MA, Chamamento 02/2026 PNAB | capitaai | fora da abrangência | não | 02/10 → 02/10 | 8 → 8 |
| Brasil | Fundação Aperam Acesita Social 2026 (MG) | capitaai | fora da abrangência | não | 04/10 → 04/10 | 9 → 9 |
| **RJ** | Rouanet nas Favelas 2 (8 localidades) | capitaai | fora da abrangência | não (Goiânia não está entre elas) | 13/10 → 13/10 | 12 → 12 |
| RJ | Parque Bondinho, Lei do ISS do Rio | Piloto-Espião | fora da abrangência | não | 09/10 → 09/10 | "12" → 9 |
| **SP** | Penápolis, Chamamento 006/2026 PNAB | querido-diario | fora da abrangência | não | 16/10 → 16/10 | 8 → 8 (checklist misturava outro edital) |
| **RS** | CRA-RS 004/2026 (pós-graduação EAD) | capitaai | **descartada** | não | 13/10 → 13/10 | 12 → 12 |

Contagem das 23:

| Decisão | Quantidade |
|---|---:|
| Válida aberta | 13 (3 delas são as janelas de emenda) |
| Fora da abrangência | 6 |
| Pendente | 1 (Impactarte) |
| Arquivada (encerrada) | 1 |
| Descartada | 2 |

**Painel depois da aplicação** (rotina completa `fluxo_oportunidades --completo`): **19 confirmadas**, e não mais 23. Saíram as 2 descartadas, a encerrada e a pendente (Impactarte, cujo prazo só aparece no agregador).

## 2. O que mudou no sistema

| Onde | O quê |
|---|---|
| `dados/oportunidades/validacao_mapa/validacao_2026-10-02.json` | As 23 decisões, com os 12 itens, a fonte oficial e a aplicabilidade à A.M.C. |
| `dados/opressores/parametros/parametros_2026-10-02.json` | 21 livros: 14 V, 3 R (emendas: programa permanente), 1 A, 2 D e 1 P. Balsas e Penápolis não tinham livro: a validação criou o deles |
| `estado/opressores.json` | itens dos 12 gravados em 19 livros; **2 livros desligados** (Nova Iguaçu de Goiás e CRA-RS) |
| `dados/editais/arquivados.json` | Itaberaí encerrada; Nova Iguaçu e CRA-RS descartadas |
| `biblioteca_alexandria/base/preditivo/oportunidades.jsonl` | 17 estudos novos na previsão (Itaberaí entra como edição de 2020 para prever a próxima) |
| `dados/associacoes/amc-jardim-america/decisoes_editais.json` | 15 oportunidades marcadas "dispensado": saem da carteira da A.M.C., e **o livro continua** para outras entidades e para a previsão |
| `dados/associacoes/amc-jardim-america/triagem_oportunidades_2026-10-02.json` | Motivo de aplicabilidade de cada uma das 23 |
| `config/filtros_motores.json` | 2 regras novas de descarte (item 4) |
| `docs/dados/validacao_motores.json` e `docs/dados/fluxo_oportunidades.json` | Recalculados |

**Ficam na carteira da A.M.C. (8):**

- SEGENP "Natal no Parque" (até 26/10).
- Secult Ocupa Goiás (até 29/10).
- BNDES Periferias (até 04/12).
- Instituto ACP (fluxo contínuo).
- Instituto Impactarte (pendente).
- As três janelas de emenda: federal, estadual e municipal, com prazo de 30/11 como meta interna do titular, até sair o calendário oficial da LOA 2027.

## 3. Relatório para o filtro: os 7 defeitos que a verificação encontrou

| # | Defeito | Casos | Motor | Correção recomendada |
|---|---|---|---|---|
| 1 | **"12 de 12" falso**: dado sem fonte oficial contado como completo | Impactarte (prazo do agregador), 3 emendas (30/11 era regra interna), Bondinho | observatorio-3setor, calendário legislativo, Piloto-Espião | Item copiado de agregador ou de regra interna entra como `ref`/`prov`, nunca como `ok`; só a página oficial vira `ok` |
| 2 | **Ano errado no prazo** | Itaberaí: edital 001/2020 lido como fim em 18/08/2027 | judiciario-cnj-tjgo | Recusar prazo cujo ano difere do ano do número do edital e da data de assinatura; sem data com ano, deixar null |
| 3 | **Link oficial de outro órgão** | Nova Iguaçu de Goiás com link da SME de Goiânia; TJGO com página da Semad; Penápolis com checklist de outro edital | do-goias, pncp-api, querido-diario | Conferir se o domínio do link pertence ao órgão do título; no PNCP usar `linkSistemaOrigem` do próprio registro |
| 4 | **Resultado errado** | BNDES (copiou a data-limite de inscrição); Equatorial (resultado da edição de 2025) | abcr, observatorio-3setor | Resultado nunca pode ser igual ao fim da inscrição nem anterior a ela; descartar datas de edição anterior |
| 5 | **Prazo da notícia, não do cronograma** | Goiás Social: "abre amanhã" → 15/10; o cronograma diz 16/10 | Piloto-Interceptador | Preferir a etapa "envio das propostas" do cronograma do PDF |
| 6 | **Ruído que passou** | Jogos escolares (Nova Iguaçu); pós-graduação de conselho profissional (CRA-RS) | do-goias, capitaai | Duas regras novas no `config/filtros_motores.json` (item 4) |
| 7 | **Leitura bloqueada** | PDF digitalizado (Goiatuba), robots.txt (Baobá, Penápolis), site em JavaScript (Impactarte), Google Drive (Bondinho) | vários | Fila do navegador local com OCR; nunca preencher o dado pelo agregador |

**Aproveitamento por motor nesta amostra:**

| Motor | Itens | Úteis (válidas, fora da abrangência ou encerradas) | Problemas |
|---|---:|---:|---|
| agregadores · capitaai | 5 | 4 | 1 ruído (CRA-RS); 3 fora da abrangência |
| calendário legislativo · emendas | 3 | 0 (3 pendentes) | Prazo sem fonte oficial |
| abcr | 2 | 2 | Resultado copiado do prazo (BNDES) |
| observatorio-3setor | 2 | 1 | Prazo do agregador (Impactarte); resultado de 2025 (Equatorial) |
| Piloto-Espião | 2 | 2 | Blog como fonte (Bondinho) |
| Piloto-Interceptador | 1 | 1 | Prazo da notícia |
| do-goias | 1 | 0 | Ruído e link de outra prefeitura |
| do-goiania | 1 | 1 | — (achou bem) |
| plat-secult-go | 1 | 1 | — |
| judiciario-cnj-tjgo | 1 | 1 (encerrada) | Ano errado |
| pncp-api | 1 | 1 | Link errado |
| plat-gife | 1 | 1 | Prazo só no PDF bloqueado |
| plat-piloto-aberto | 1 | 1 | — |
| querido-diario | 1 | 1 | Checklist misturado com outro edital |

## 4. Regras aplicadas agora (`config/filtros_motores.json`)

1. **`jogos_e_vagas_escolares`** descarta: jogos escolares ou educacionais, chamada pública escolar ou infantil e matrícula. A regra cede quando o título fala em OSC ou em termo de fomento ou de colaboração. Hoje não pega nenhum dos 651 títulos (os títulos do diário são genéricos) e fica para os próximos casos.
2. **`conselho_profissional_contratacao`** descarta chamamentos de conselho profissional (CRA, CRC, CREA, CRM…) para contratar curso ou serviço. Cede quando há OSC, termo ou doação. Hoje pega 1 título entre 651: o CRA-RS, que já foi descartado.

As duas foram testadas contra os 651 títulos atuais: nenhuma derrubou oportunidade válida.

## 5. Filtro de aplicabilidade da A.M.C. (ainda não automatizado)

Estas exigências **não são ruído**: a oportunidade é boa para outras entidades. Elas devem virar filtro **por associação**, comparando com o perfil da entidade:

| Exigência no edital | Exemplos | Como a A.M.C. está hoje |
|---|---|---|
| CEBAS | Equatorial | Não tem |
| Coordenador com doutorado ou vínculo acadêmico | Fundação Maria Emília | Não tem |
| Liderança ou membresia específica (ex.: 85% de mulheres negras) | Fundo Baobá | Não atende |
| Projeto já aprovado em lei de incentivo (Rouanet, Esporte, FIA, Idoso) | Zurich | Não tem projeto aprovado |
| Sede ou atuação em território restrito | Rouanet nas Favelas, Goiatuba, Balsas, Penápolis, Aperam, Bondinho | Goiânia/GO |
| Experiência e capacidade técnica em equipamento público | Goiás Social (socioeducativo), TJGO (reciclagem) | Não tem |

**Recomendação:** acrescentar ao perfil (`dados/associacoes/<slug>/perfil_publico.json`) os campos `certificacoes`, `projetos_aprovados_leis_incentivo`, `perfil_lideranca` e `experiencias` (alguns já existem). O enquadramento (`src/enquadramento.py`) passaria a marcar "não elegível" quando o edital trouxer uma dessas exigências e o perfil não a cumprir. Por enquanto, o efeito foi aplicado à mão: 15 marcações "dispensado" na carteira da A.M.C.

## 6. Pontos para o titular decidir

1. **Emendas:** o 30/11 é regra do titular, não prazo oficial: o calendário de emendas à LOA 2027 não estava publicado em 02/10. Mantive a regra (decisão de negócio), mas o item "Prazo de inscrição" agora diz "meta interna", com status "não informado no edital". Quando o calendário oficial sair, o prazo deve ser trocado pela data oficial.
2. **SEGENP "Natal no Parque" (R$ 5 milhões, até 26/10):** é a única válida em Goiânia com repasse. Pelo porte, só é viável com parceiro técnico (produtora ou OSC de eventos).
3. **BNDES Periferias:** a A.M.C. só entra como organização apoiada dentro da rede de outra proponente, que precisa reunir 10 ou mais organizações e R$ 20 milhões ou mais. Vale buscar a articuladora em Goiânia.

## 7. Conselho de 7 lentes (tecnologia)

**Extremamente pessimista** (*staff engineer* de qualidade de dados): "Doze de 23 pareciam completas, e quatro delas tinham prazo sem fonte. O painel mentia com cara de verdade. Se a entidade tivesse se organizado pelo 30/11 das emendas, poderia perder a janela real ou correr atrás de uma que não existe."

**Pessimista** (professor de engenharia de software): "Três defeitos são de código, não de fonte: ano errado, resultado igual ao prazo, link de outro órgão. Sem teste de regressão por defeito, eles voltam na próxima coleta."

**Levemente pessimista** (CTO de plataforma): "As regras de título são frágeis: a de jogos escolares não pega nada hoje porque o diário dá título genérico. O filtro precisa olhar o trecho, o objeto, e não só o título."

**Neutro** (ponderador): ver a decisão abaixo.

**Levemente otimista** (diretor de engenharia): "A rotina oficial absorveu tudo: arquivo, previsão, livros e carteira, sem código novo. Só com dados, o painel ficou honesto de 23 para 16, e 103 itens entraram nos livros."

**Otimista** (arquiteta de sistemas): "O 'dispensado' por associação separa duas perguntas que estavam juntas: a oportunidade é boa? E é boa para esta entidade? O livro continua servindo a todas as outras."

**Extremamente otimista** (pesquisador): "Com o perfil completo (certificações, projetos aprovados, liderança), o sistema passa a dizer o que falta para a A.M.C. ficar elegível: 'tire o CEBAS e entram mais 6 editais'. O filtro vira plano de desenvolvimento institucional."

**Decisão do neutro:** aplicar as decisões e as 2 regras agora, e não automatizar ainda o filtro de aplicabilidade.

**Parâmetros de qualidade**

- Dado só é `ok` se vier da página oficial.
- Prazo com ano diferente do edital é recusado.
- Resultado nunca é igual ao prazo de inscrição.
- O link precisa ser do domínio do órgão do título.

**Mitigação:** os itens 1 a 5 da seção 3 viram testes de regressão no motor de cada um, na próxima rodada de código. Até lá, a validação individual de cada semana corrige à mão.
