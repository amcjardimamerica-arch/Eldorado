# Consolidado — Teste de coleta e desempenho dos motores 01 a 21 (03/10/2026)

O teste foi feito motor por motor, em sequência, com o prompt de `00-PROMPT.md` e a ferramenta
`scripts/teste_motores.py`. Os relatórios individuais estão nesta pasta (`01-…` a `21-…`).

**Teste ao vivo:**

- O navegador do titular não respondeu durante o teste (4 tentativas de 3 minutos).
- O ambiente de execução não alcança os portais (o proxy recusa).
- A prova ao vivo usada foi, portanto, a última leitura de cada motor na nuvem do GitHub, com o código HTTP de cada
  página (`estado/esquadra.json › saude`).
- A conferência no navegador fica para a conversa de implantação.

## Quadro dos 21 motores

| Nº | Motor | Workflow | Coleta | Resultado | Histórico de 3 anos |
|---|---|---|---|---|---|
| 01 | Diário Oficial de Goiânia | ✅ | 🟡 Querido Diário com 2 dias de atraso; portal só no Brasil | ✅ 1 edital real (contado 2×) | ❌ próprio · 269 indícios correlatos |
| 02 | Diário Oficial de Goiás | ✅ | ✅ 3 rotas | 🟡 10 de 16 registros são ruído antigo | ❌ |
| 03 | Diário Oficial da União | ✅ | ✅ 8 mil matérias por dia | ✅ v2 (Corumbá-GO, ANATER) · ruído antigo | ❌ |
| 04 | Câmara de Goiânia | ❌ `coleta: local`, nunca disparado | ❌ desde 30/09 | ❌ | ❌ |
| 05 | Assembleia de Goiás | ✅ | 🟡 lê notícias, não proposições | ❌ 3 notícias | ❌ |
| 06 | Congresso Nacional | ✅ 1 leitura | ✅ 5 fontes | ✅ janela não iniciada, correto | ❌ |
| 07 | TJ-GO | 🟡 novo, não rodou | 🟡 só no Brasil | ✅ Itaberaí (antecessor) | ❌ carga de 150 dias |
| 08 | MP-GO Destina | ✅ manual por regra | ✅ respeita o robots | ✅ cadastro contínuo | 🟡 2 registros |
| 09 | MPT-GO | 🟡 novo, não rodou | ✅ tabela na nuvem | ✅ edital até 05/10 | 🟡 2026 forte, 2024 e 2025 fracos |
| 10 | MPU e FDD | 🟡 novo, não rodou | ✅ 38 fontes | ✅ sinal do FDD a conferir | 🟡 |
| 11 | CNJ | 🟡 novo, não rodou | ✅ busca do CNJ | ✅ Itaberaí | 🟡 vistos, não gravados |
| 12 | Justiça Federal GO | ❌ `local` errado, nunca disparado | 🟡 home institucional | ❌ 0 em 40 | ❌ |
| 13 | Prefeituras 25 maiores | 🟡 v2 fora do registro | 🟡 8 de 25 cidades | ❌ 0 abertas | ✅ 8 cidades · ❌ 17 |
| 14 | Órgãos do Estado de GO | 🟡 v2 fora do registro | ✅ 37 órgãos | ✅ 1 aberta | ✅ 5 anos, 55 históricas |
| 15 | PNCP | ✅ | ✅ API oficial | ✅ 221 · só 16 de GO | 🟡 2023 fraco |
| 16 | Lei Rouanet | ✅ | 🟡 páginas do Ministério, não o SALIC | ❌ 3 páginas de menu | ❌ |
| 17 | CNPq / MCTI | ❌ adiado em 02/10 | 🟡 home do MCTI | ❌ 0 em 19 | ❌ |
| 18 | GIFE / Capta | ✅ | ✅ APIs | ✅ 3 editais reais | ❌ (36 seleções viáveis) |
| 19 | Editais de empresas | ❌ adiado em 02/10 | 🟡 home das empresas | ❌ 0 em 19 | ❌ |
| 20 | Incentivos Fiscais | ✅ semanal | ✅ ranking do ICMS | ✅ 60 empresas | 🟡 2024 e 2025 · 2023 ausente · 2026 com erro |
| 21 | Patrocínio Privado | ✅ semanal | 🟡 agenda de jornal | ❌ 3 falsos positivos | ❌ |

**Totais:**

- **Workflow:** 11 ✅, 6 🟡 e 4 ❌.
- **Resultado:** 12 ✅, 1 🟡 e 8 ❌.
- **Histórico de 3 anos:** 1 completo (14), 7 parciais (08, 09, 10, 11, 13, 15 e 20) e 13 sem histórico.

## Defeitos comuns, por gravidade

1. **A quebra do passo dos sensores (já corrigida neste pacote).**
   - Às 19:10 de 02/10, `src.sensores` parou com `KeyError: 'lido_em'`, porque um leitor devolveu resultado sem a hora.
   - Depois disso, nenhuma leitura de motor foi registrada até o fim do teste (21:37).
   - **Correção:** o resultado de qualquer leitor agora é completado (hora, achados, falhas, saúde) antes do registro.
     Teste: `tests/test_teste_motores_2026_10_03.py`.
2. **Falta de tempo no passo dos sensores.**
   - Em 02/10 foram **6 rodadas e 12 execuções de motor**, para mais de 100 agendados.
   - Na rodada das 14:49, os diários (cerca de 6 minutos cada), o PNCP e o Congresso consumiram os 1.452 segundos, e
     **49 motores foram adiados** (entre eles 13, 16, 17, 18 e 19).
   - **Recomendação:** dar aos diários (01, 02 e 03) e ao PNCP um passo ou job próprio, em paralelo com os demais, ou
     subir o limite do passo para os motores leves. A decisão de custo de execução do GitHub fica com a próxima
     conversa.
3. **Motores marcados `coleta: local` nunca são disparados pelo GitHub.**
   - O 04 (Câmara) depende do Brasil de fato.
   - O 12 (Justiça Federal) **responde da nuvem**: o rótulo foi corrigido para `nuvem` neste pacote.
   - O 04, o 07 e as 17 cidades do 13 dependem da coleta no computador do titular ou na VM Oracle (pacote dos pilotos).
4. **Leitores v2 que gravam estado próprio e não atualizam o painel** (13 e 14). O painel mostra cinza ou vermelho
   num motor que roda e rende. Os leitores precisam registrar a leitura na esquadra.
5. **Agendador lia `estado/sensores.json`, que não existe.** A cadência longa (7 ou 30 dias) nunca era respeitada.
   Corrigido para `estado/esquadra.json`.
6. **Leitores genéricos em páginas institucionais** (05, 12, 16, 17, 19 e 21): leem home e menu, contam a mesma página
   a cada leitura (o 16 mostra "105 achados" que são 3 páginas) e gravam ruído.
7. **Ruído antigo na base:** registros sem data das versões anteriores à v2 (02: 10, 03: 14; títulos de página no
   09 e no 16).
8. **Histórico de 3 anos:** só o 14 (5 anos) e o 13 (8 cidades) cumprem. Nos demais, a fonte permite a carga:
   - 01: Querido Diário por período;
   - 02: busca de texto completo;
   - 03: Leitura do Jornal por data;
   - 15: API por período;
   - 18: seleções mensais pela API;
   - 20: anexos do ICMS;
   - 07 e 11: arquivo de notícias;
   - 16: dados abertos do SALIC.

## Ordem de correção recomendada

| Prioridade | O quê | Motores |
|---|---|---|
| 1 (feito) | Passo dos sensores não quebra mais; agenda lê a esquadra; o 12 volta à nuvem | todos · 12 |
| 2 | Tempo do passo: diários e PNCP em job próprio | 13, 16, 17, 18 e 19 (adiados) |
| 3 | Coleta no Brasil (computador do titular ou VM) | 01 (portal), 04, 07 e 13 (17 cidades) |
| 4 | v2 registrando na esquadra | 13 e 14 |
| 5 | Leitores próprios no lugar dos genéricos | 05 (processo legislativo), 16 (SALIC), 17 (chamadas do CNPq), 19 (rotas das empresas), 21 (patrocinadores dos eventos) |
| 6 | Carga de 3 anos, fonte por fonte | 01, 02, 03, 07, 11, 15, 18 e 20 |
| 7 | Limpeza do ruído antigo e vetos (extrato, minuta, título de página) | 02, 03, 09 e 16 |

## Ações do titular (decisões e cadastros)

1. **Hoje:** cadastrar a A.M.C. no Sistema de Destinações do MPT (Edital PRT18 24/2025). Há um edital do PTM Anápolis
   aberto até **05/10**.
2. **Hoje:** conferir a página do **FDD (seleção em andamento)**. Ela deixou de dizer "não há".
3. **Até 31/10:** confirmar a janela de propostas da Lei Rouanet 2026. A configuração registra 1º/02 a 31/10, com a
   ressalva de conferir a norma vigente.
4. Pedir o cadastro no **Destina do MP-GO**, pelo COMPOR, telefone (62) 3243-8116.
5. Acompanhar o **PL 288/2026** da Câmara de Goiânia (utilidade pública da A.M.C.). O motor 04 está parado.
6. Rede Memória Viva (GIFE) vence hoje; o programa Marielle Franco do Fundo Baobá, em 19/10.

## Conselho de 7 lentes (conjunto)

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Em 02/10, o sistema registrou 12 execuções para mais de 100 motores e depois quebrou. O painel mostra luzes que não correspondem ao que os motores fazem. |
| Pessimista | 8 de 21 motores não entregam resultado, e 13 não têm o histórico pedido. |
| Levemente pessimista | Leitores genéricos geram números inflados (105 achados que são 3) e ruído. |
| **Neutro** | **O núcleo é bom: 12 motores dão resultado real com fonte oficial (diários, PNCP, MPT, GIFE, Estado). Os defeitos são de execução (quebra, tempo, local) e de registro, mais que de desenho. Ordem: (1) não quebrar, já feito; (2) tempo do passo; (3) Brasil; (4) registro da v2; (5) leitores próprios; (6) carga de 3 anos. Meta de qualidade: nenhum motor agendado sem leitura registrada em 24 horas, e todo número do painel igual a oportunidades únicas.** |
| Levemente otimista | Os motores v2 (01, 02, 03, 09, 14, 15 e 18) já mostram o padrão certo: fonte estruturada, veredito com motivo e prazo oficial. |
| Otimista | O histórico do Estado (5 anos) e das prefeituras (357 publicações) prova que a carga de 3 anos funciona quando é desenhada. |
| Extremamente otimista | Com as 6 correções, o painel passa a prever o calendário de editais de Goiás, e não só a reagir. |
