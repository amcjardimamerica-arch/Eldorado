# Parecer do conselho — Motor 04 · PNCP (Portal Nacional de Contratações Públicas)

**Data:** 01/10/2026 · **Motor:** `pncp-api` (Bússola, posição 04) · **Matéria:** técnica (engenharia de coleta), com reflexo jurídico (Lei 14.133/2021 × Lei 13.019/2014, PNAB, Decreto 10.936/2022, aprendizagem)

## 1. Síntese

Em setembro de 2026 o motor 04 rodou **52 vezes e não achou nada**. As causas:

- só lia **3 das 11 URLs** configuradas;
- barrava no rótulo exatamente as palavras dos chamamentos de OSC ("com ou sem fins lucrativos", "prestação de serviços");
- não tratava o limite de requisições do PNCP (HTTP 429).

Ao mesmo tempo, um coletor paralelo (`src/coletores_api.py`) gravou **215 registros do PNCP** na base:

- nenhum com data de encerramento;
- 206 de fora de Goiás;
- vários publicados em 2024.

O painel somava esses 215 ao motor, como "190 oportunidades".

O PNCP tem o que o motor precisava e não usava:

- a lista de **propostas abertas**, com a **data oficial de encerramento**;
- a **busca do portal**, que filtra "recebendo proposta" por UF e por esfera.

Os municípios de Goiás publicam ali, como **credenciamento**, chamamentos MROSC de verdade. Em 01/10/2026 estavam **abertas 8 seleções** para OSC no PNCP. Três delas valem para qualquer associação do perfil:

- **Pirenópolis**: termo de colaboração com OSC, até 16/09/2027;
- **Senador Canedo / FMAS**: OSCs de assistência inscritas no CMAS, até 11/05/2027;
- **Silvânia**: PNAB ciclo 2, até **09/10/2026**.

As outras cinco servem a perfis específicos: coleta seletiva solidária (TJGO, DNIT, TST ×2) e aprendizagem (CONAB).

**Decisão do neutro:** aprovar a versão 2. O motor passa a ler as propostas abertas e a busca do portal. Classifica cada edital pelo classificador de finalidade do PNCP, somado aos vetos e regimes do motor 03, e grava o PDF do edital anexado pelo órgão como documento oficial. O coletor paralelo foi desligado.

## 2. Resultado de setembro/2026 (motor antigo)

| Item | Número | Evidência |
|---|---|---|
| Leituras do sensor | 52, todas com 0 achados | `estado/esquadra.json` › `pncp-api` |
| URLs lidas por execução | 3 de 11 (`paginas_por_sensor` = 3) | `config/sensores.json` › `limites`; `diagnostico.paginas_lidas` = 7 (3 + 4 "descobertas") |
| "Descobertas" seguidas | 4 páginas /app/editais/… por execução | são páginas de aplicação, sem conteúdo no HTML |
| Dias vermelhos sem causa | 8 (07, 09, 14–17, 21 e 22/09) | `estado/esquadra_diario.json`; o PNCP responde 429 em sequência rápida, medido em 01/10 |
| Vetos da camada 1 | "com ou sem fins lucrativos", "prestação de serviços", "aquisição", "Lei 14.133" | `config/rotas_motores.json` › `pncp-api` |
| Registros "pncp" do coletor paralelo | 215: 0 com prazo, 206 fora de Goiás, 167 sem finalidade, 91 publicados em 2024 | `dados/oportunidades/oportunidades.jsonl` |
| Cartão do painel | "190 oportunidades (218 registros)" com o motor em 0 achados | `src/achados_motores.py` › `ALIAS` |

## 3. Defeitos encontrados

1. **D1 — Leitura de 27% das rotas.** O laço genérico corta em `paginas_por_sensor` = 3. As modalidades 10 e 3 do Brasil, as páginas seguintes e o país inteiro nunca eram lidos.
2. **D2 — Veto no lugar errado.** "Com ou sem fins lucrativos" e "prestação de serviços" aparecem nos editais de OSC ("pessoa jurídica de direito privado, com ou sem fins lucrativos") e barravam a leitura antes de qualquer análise.
3. **D3 — Prazo inexistente.** A API entrega `dataEncerramentoProposta`. O coletor gravava `prazo_texto: null` em 215 de 215, e o sensor punha a data num texto livre.
4. **D4 — Rota errada.** `/contratacoes/publicacao` traz o que foi **publicado** na janela. O que interessa à associação é o que está **aberto** (`/contratacoes/proposta`), que inclui credenciamentos publicados meses antes e ainda recebendo propostas.
5. **D5 — Limite de requisições.** 429 depois de cerca de 25 chamadas seguidas. O motor não esperava, e o dia ficava vermelho com "falha" genérica.
6. **D6 — Território.** O coletor tinha escopo de 27 UFs e gravava chamamentos municipais de RS, PR e SC, que só servem a OSCs daqueles municípios.
7. **D7 — Painel inflado.** O cartão do motor contava os 215 registros do coletor paralelo.
8. **D8 — Classificador de finalidade com falso positivo.** `" fia"` (Fundo da Infância) casava dentro de "ultrasson**ografia** " e marcava credenciamento de ultrassom como "fundo de direitos".

## 4. Rotas (Etapa 2)

Testes feitos com IP brasileiro pelo navegador do titular em 01/10/2026. O GitHub já recebia 200 da API (`estado/esquadra.json` › `saude`).

| Rota | Resposta | O que entrega | Decisão |
|---|---|---|---|
| `/api/consulta/v1/contratacoes/proposta?dataFinal=…&codigoModalidadeContratacao=…&uf=GO` | 200 · 50 por página | contratações **recebendo proposta**, com `dataEncerramentoProposta`. `dataFinal` limita o encerramento: 407 até 2027 e 465 até 2036 (credenciamento 12, GO) | **usar** (Fonte A), com horizonte de 10 anos |
| `/api/search/?q=…&tipos_documento=edital&status=recebendo_proposta&ufs=GO` ou `&esferas=F` | 200 · até 100 por página | busca no título e na descrição, com UF, município, esfera e modalidade | **usar** (Fonte B), Goiás e órgãos federais |
| `/pncp-api/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos` | 200 | PDFs anexados pelo órgão. A URL vem com a porta interna `:50439`, que é retirada | **usar** como documento oficial |
| `/api/consulta/v1/contratacoes/publicacao` | 200 / 204 | o que foi publicado na janela | **descartar** como via principal |
| `/app/editais/{cnpj}/{ano}/{seq}` | página de aplicação | — | link do registro (vetor), nunca lido como listagem |
| Busca com aspas (`"termo de fomento"`) | 0 resultados | — | aspas não funcionam como frase exata |

Modalidades com propostas abertas em Goiás em 01/10: credenciamento 465, dispensa 278, inexigibilidade 7, manifestação de interesse 5, pré-qualificação 1 e concurso 0. Os chamamentos MROSC de Goiás vêm como **credenciamento (12)**. Dispensa e inexigibilidade são contratação direta e só entram com instrumento MROSC explícito.

## 5. Parametrização antes × depois

| Item | Antes | Agora |
|---|---|---|
| Rota | `/publicacao` (janela de 3 dias), 3 URLs lidas | `/proposta` (tudo o que está aberto) + `/api/search/` |
| Território | GO no sensor; 27 UFs no coletor | Goiás + órgãos federais. Órgão federal sediado fora de GO e DF vira ACOMPANHAR ("conferir se é nacional") |
| Prazo | nenhum | `dataEncerramentoProposta` oficial |
| Classificação | léxico no rótulo + vetos que barravam OSC | território → vetos (empresa, prestador, SUS, OS, serviço ao órgão, conselho profissional, inovação, modalidade de contratação) → finalidade do PNCP + regimes do motor 03 → prazo |
| Documento oficial | — | PDF do edital em `/arquivos`, até 25 por execução; se falhar, tenta de novo |
| Ritmo | sem pausa | 1,5 s entre chamadas; 429 espera 20 s, 40 s e 60 s; prazo total de 7 min; fonte abortada após 3 falhas seguidas |
| Retroativo | relia "um dia de setembro" com os editais de hoje | o motor não relê dia passado (`src/retroativo.py`) |
| Coletor paralelo | ativo, 27 UFs, sem prazo | desligado (`config/coletores_api.json` › `pncp.ativa = false`), também na carga de 5 anos |
| Cartão do painel | somava os registros "pncp" | conta só o que o motor 04 grava (`fonte_id = pncp-api`) |

## 6. Calibração (Etapa 4)

O código desta versão rodou sem alteração no navegador do titular, com IP brasileiro e Python no próprio navegador, sobre dois conjuntos:

- **(a)** todas as publicações de Goiás de setembro/2026 nas modalidades credenciamento, concurso, manifestação de interesse e pré-qualificação: 82 publicações;
- **(b)** o que estava aberto em 01/10: 698 itens da Fonte A, de 6 modalidades, e 320 da Fonte B, de 18 consultas × 2 escopos. São 896 editais únicos.

Depois houve uma leitura de ponta a ponta, real: 49 consultas, 106 s, nenhuma falha.

| Medida | Setembro (a) | Abertos em 01/10 (b) |
|---|---|---|
| OPORTUNIDADE | 8 | **8** |
| ACOMPANHAR | 1 | 3 |
| RUÍDO | 73 | 885 |
| PDF do edital achado | — | 8 de 8 |

**Conferência manual:**

- **OPORTUNIDADE:** todas as 16 foram abertas e conferidas, e todas são seleções reais com OSC ou entidade sem fins lucrativos como público.
  - Setembro: Senador Canedo/FMEC PNAB 001 a 005, Silvânia PNAB e Alvorada do Norte PNAB 005 e 006.
  - Aberto em 01/10: as 8 da seção 10.
  - O hackathon de Rio Verde, que vinha como "premiação", virou regra (competição de participantes) e saiu.
- **RUÍDO:** dois sorteios de 12, com 12 de 12 corretos em cada. Conferi também todos os itens marcados como RUÍDO que tinham palavras de terceiro setor (cultura, OSC, entidade, sem fins lucrativos): todos corretos. São:
  - compra da agricultura familiar (PNAE);
  - credenciamento de médicos e clínicas, transporte escolar, artistas para shows e empresas de equoterapia.
- **ACOMPANHAR:**
  - ILPI de Trindade: credenciamento de entidade para vaga de acolhimento;
  - prêmio do CAU-MG;
  - aprendizagem da CPRM na Bahia.

Os erros achados viraram regra e teste em `tests/test_motor04_pncp.py` (29 testes):

- dispensa de "processamento de dados" de um fundo de assistência;
- dispensa de "materiais esportivos para premiação";
- credenciamento de ultrassom e de "prestadores de serviços em saúde";
- DPU credenciando "empresas e OSC de saúde" para medicina do trabalho;
- sandbox e hackathon de Rio Verde;
- "fia" dentro de "ultrassonografia";
- coleta do TJGO marcada como "doação de bens";
- pregão de aprendizagem da CONAB (vale, porque só entidade sem fins lucrativos concorre).

**Revisão independente:** um revisor separado leu o código antes da entrega e achou 9 defeitos. Todos foram corrigidos e cobertos por teste:

- documento que falhou ficava sem URL para sempre;
- 429 contínuo podia estourar o tempo do passo dos sensores;
- a varredura retroativa relia o PNCP como se fosse edição de um dia passado;
- a carga de 5 anos ainda chamava o coletor desligado;
- PNAB caía por "publicidade", "equipamentos" ou "concurso público de premiação";
- "jovem aprendiz" no singular não casava;
- finalidade "None" no motivo;
- um item malformado derrubava a fonte inteira;
- órgão estadual era rotulado como municipal.

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de integração com APIs públicas, especialista em limites de taxa.**
O PNCP não documenta o limite, e o 429 aparece depois de umas 25 chamadas. A versão 2 faz cerca de 50 chamadas por passagem, 3 vezes ao dia. Se a Serpro apertar o limite, o motor fica cego de novo. O prazo de 7 minutos e o aborto após 3 falhas impedem o pior caso: derrubar o passo de todos os sensores. Mas a métrica a vigiar é `historico.<dia>.falhou`.

**2. Pessimista — staff engineer de relevância.**
O classificador de finalidade foi calibrado em 768 publicações de 2026 e agora tem mais 20 vetos. Cada veto é uma chance de falso negativo. Exemplo: "aquisição" barra o edital PNAB que fala em "aquisição de equipamentos", e por isso esse veto cede quando há sinal forte de OSC. Mesmo assim, um chamamento MROSC mal redigido, sem "OSC", "termo de colaboração" ou "PNAB", passa como contratação. O objeto no PNCP tem no máximo uns 500 caracteres. O texto do PDF é a garantia, e ainda não é lido.

**3. Levemente pessimista — professor de engenharia de computação, especialista em sistemas de informação públicos.**
O PNCP é vetor, não fonte: a regra do sistema continua. A versão 2 grava o PDF do órgão como documento oficial, mas não confere o texto dele. Os credenciamentos de fluxo contínuo (Pirenópolis até 2027, TJGO até 2031) podem ter sido encerrados de fato sem atualização no portal. O ACOMPANHAR da Trindade (ILPI) é zona cinzenta: contrato de serviço para entidade, não fomento.

**4. Neutro — CTO de plataforma pública de dados, mediador.** O voto está na seção 8.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas explicáveis.**
A data de encerramento passou a ser **oficial** e estruturada. É a primeira fonte da Bússola em que o prazo não depende de expressão regular. Cada veredito traz uma frase que o titular, como advogado, audita: "modalidade de contratação (Dispensa) sem instrumento MROSC", ou "credenciamento de prestador, Lei 14.133 art. 79".

**6. Otimista — staff engineer de produto, foco em captação.**
O PNCP mostrou dois achados que nenhum diário mostra:

- **credenciamentos permanentes de OSC**: Senador Canedo aceita OSCs de assistência até 2027, e Pirenópolis faz termo de colaboração até 2027. São portas abertas o ano todo, não editais de 15 dias;
- **a família da coleta seletiva solidária** (Decreto 10.936/2022): TJGO, DNIT e TST credenciam associações de catadores por anos. É uma oportunidade permanente para associações desse perfil em Goiânia e no DF.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.**
Com o número de controle do PNCP como chave, o sistema cruza o mesmo edital no Diário Oficial (motores 01 a 03) e no PNCP e confirma o prazo pela fonte estruturada. O PDF em `/arquivos` é a ponte para a extração de requisitos do Farol de Alexandria. Daqui a pouco, a ficha do edital nasce pronta: prazo oficial, documento oficial, órgão, município e modalidade.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 04 versão 2 e publicar, depois dos PRs dos motores 02 e 03, porque o classificador e os vetos federais vêm deles.

**Metas (medidas a cada 30 dias em `estado/pncp_osc.json` › `historico`):**

| Indicador | Meta |
|---|---|
| Passagens com resposta da API | ≥ 95% |
| Oportunidades com prazo oficial | 100% das que vêm da Fonte A |
| Oportunidades com PDF do órgão | ≥ 90% |
| Precisão de OPORTUNIDADE (conferida pelo titular) | ≥ 80% (calibração: 16/16) |
| Falhas com causa descrita | 100% (429 = "ritmo", nunca "falha genérica") |

**Mitigação de riscos:**

1. **Limite de taxa:** pausa de 1,5 s, espera crescente no 429, prazo de 7 minutos e aborto após 3 falhas seguidas. O alarme dispara com 2 dias sem resposta.
2. **Falso negativo dos vetos:** os vetos de serviço ao órgão e de SUS cedem ao instrumento MROSC ou ao sinal forte de OSC/PNAB. Todo RUÍDO traz o motivo.
3. **Fluxo contínuo desatualizado:** a OPORTUNIDADE leva o PDF do órgão para conferência. O Farol confirma antes de qualquer candidatura.
4. **Território:** municipal ou estadual fora de Goiás vira ruído. Órgão federal fora de GO e DF vira ACOMPANHAR. Coleta e doação só valem em Goiás ou no DF.
5. **Vetor × fonte:** a URL do registro é a página do PNCP, e `url_documento` é o arquivo do órgão. A regra "PNCP nunca é fonte" continua valendo.

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/pncp_osc.py` (novo) | leitor do motor 04: Fontes A e B, ritmo e prazo, normalização, território, vetos, finalidade e regimes, prazo oficial, deduplicação por número de controle, PDF do órgão, alarme |
| `config/pncp_osc.json` (novo) | modalidades, horizonte, consultas, escopos, ritmo e limites |
| `src/sensores.py` | o `pncp-api` passa ao novo leitor |
| `src/pncp_terceiro_setor.py` | `" fia "` com espaço dos dois lados (não casa mais dentro de "ultrassonografia") |
| `src/diario_uniao.py` | regime de aprendizagem casa "Cadastro Nacional **de** Aprendizagem" e "jovem aprendiz" (vale também para o motor 03) |
| `src/coletores_api.py`, `config/coletores_api.json` | coletor paralelo do PNCP desligado, inclusive na carga de 5 anos; Querido Diário segue ativo |
| `src/retroativo.py` | o `pncp-api` sai da varredura retroativa |
| `src/achados_motores.py` | o cartão do motor 04 conta só o que ele grava |
| `config/sensores.json`, `config/rotas_motores.json`, `config/agenda_motores.json` | rotas reais, verificação nova e notas de 01/10 |
| `src/auditoria_motores.py`, `scripts/descricao_motores.py` | textos do conselho e da evolução gratuita |
| `tests/test_motor04_pncp.py` (novo) | 29 testes com objetos reais, API simulada, 429, item malformado, retroativo e quarentena |

**Testes:** a suíte completa (956 testes) tem as mesmas 40 falhas e 3 erros que já existiam no ramo do motor 03, e nenhuma falha nova. Os 29 testes novos estão verdes, e os dos motores 01 a 03 também. `scripts/verificar_privacidade.py` não encontrou nenhuma credencial publicada.

## 10. Seleções abertas no PNCP em 01/10/2026, para o titular decidir

| Órgão | Edital | Modalidade | Propostas até | Nº de controle PNCP |
|---|---|---|---|---|
| Prefeitura de Silvânia | Chamamento nº 01/2026: PNAB ciclo 2 | Credenciamento | **09/10/2026** | 01068030000100-1-000355/2026 |
| CONAB (DF) | Entidade sem fins lucrativos do Cadastro Nacional de Aprendizagem, para jovens aprendizes | Pregão | **20/10/2026** | 26461699000180-1-000323/2026 |
| FMAS de Senador Canedo | OSCs de assistência social inscritas no CMAS: projetos e serviços | Credenciamento (fluxo contínuo) | 11/05/2027 | 13501444000152-1-000010/2026 |
| Prefeitura de Pirenópolis | Termo de colaboração com OSC (Secretaria de Educação e Cultura) | Credenciamento (fluxo contínuo) | 16/09/2027 | 01067941000105-1-000074/2025 |
| DNIT (DF) | Associações de catadores: eliminação de documentos e recicláveis | Credenciamento | 22/09/2028 | 04892707000100-1-000136/2026 |
| TST (DF) | Associações de catadores: recicláveis do TST | Credenciamento | 04/12/2028 | 00509968000148-1-000083/2026 |
| TST / TRT | Associações de catadores, contratação onerosa (conferir o estado do TRT) | Credenciamento | 05/07/2030 | 00509968000148-1-001992/2025 |
| TJGO | Entidades sem fins lucrativos para coleta e destinação de recicláveis | Credenciamento | 22/07/2031 | 02292266000180-1-000083/2026 |

Endereço de cada edital: `https://pncp.gov.br/app/editais/{CNPJ}/{ano}/{sequencial}`, tirado do número de controle. O PDF do órgão fica em `url_documento`.

## 11. Pendências

1. **Ordem de implantação:** os PRs dos motores 02 e 03 antes deste.
2. **Primeira execução na nuvem:** confirmar `historico.<dia>.falhou = false` e o número de 429 no diagnóstico.
3. **Texto do PDF do edital:** ler o PDF de `/arquivos` para confirmar público, documentos e prazo. Exige leitor de PDF e precisa de decisão sobre dependência, porque o núcleo é só biblioteca-padrão.
4. **Registros antigos:** os 215 registros "pncp" do coletor desligado continuam na base. A revisão humana decide arquivá-los (`merge_registro` preserva o status).
5. **Outras UFs:** se a associação passar a atuar fora de Goiás, basta acrescentar a UF em `config/pncp_osc.json` › `fonte_a.ufs`.
