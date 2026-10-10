# Eldorado · Parte 1 (Goiás): verificação de 100% e melhorias dos motores

Data: 10/10/2026. O documento tem duas etapas: a verificação de que nada ficou sem pesquisa e o relatório de acertos e erros dos motores, com as melhorias para implantar. Nada foi enviado ao GitHub (regra permanente).

---

# ETAPA 1: verificação de 100%

## 1.1 Conferência de completude

A imagem do sistema (`dados/abertas.json`) foi baixada de novo hoje e o recorte da Parte 1 (`uf = GO` e `nivel ≠ internacional`) foi refeito.

| Verificação | Resultado |
|---|---|
| Registros GO no recorte atual | 350 = 71 (lista A) + 267 (lista B) + 12 já marcados como encerrados pelo próprio sistema (fora do escopo pelo prompt) |
| Lista A: ids do sistema × ids pesquisados | 71 × 71. Nenhum id novo e nenhum id saiu (comparação id a id). |
| Lista B: ids do sistema × ids pesquisados | 267 × 267. Conjunto idêntico, conferido por contagem, unicidade e soma dos ids (`0x8569e02c0f3625f802146b` nos dois lados). |
| Ids com veredito e parecer | 338 de 338 |
| Passadas | 1ª passada nos 338; 2ª passada hoje em todos os pendentes, nas pratas, no bronze e nas pistas abertas |
| Derivadas (citadas em documento oficial, fora do sistema) | 2 pesquisadas e registradas como `novo-…` |
| **Remanescentes sem pesquisa** | **0** |

## 1.2 O que mudou na 2ª passada

| id | Antes | Depois | Prova |
|---|---|---|---|
| 64b098a6 · FMAS Senador Canedo, Edital 006/2026 | prata | **ouro** | Edital lido no PNCP (arquivo 3, 68 p.). Propostas de 11/05/2026 a 10/05/2027 (p. 8). Recurso em 5 dias (p. 11). Até R$ 300 mil (item 12.1.2, p. 16). Anexos I a V (p. 18). Termo de Colaboração de 12 meses (p. 17). |
| b5199edf · Pirenópolis, Edital 013/2025 (música) | prata | **encerrada** | O edital (PNCP arquivo 1, p. 6) fixa as propostas "De 17/09/2025 a 17/10/2025". A data 16/09/2027 vinha do registro do PNCP e não é prazo de inscrição. |
| e412e794 · CMDCA Aparecida, Credenciamento 001/2025 | pendente | **encerrada** | Cronograma no próprio edital: "Envio das propostas pelas Instituições 04/11/2025". |
| 31bc5b45 · CMDPI Aparecida, Credenciamento 02/2023 | pendente | **encerrada** | Item 1.1: captação "do exercício 2023". Encerrada pela vinculação ao exercício. |
| novo-piracanjuba-pncv-002-2026 | — | **pendente (nova)** | Premiação PNCV 002/2026 (Cultura Viva) aparece na página oficial "Lei Aldir Blanc – Ciclo II – 2026", mas os 8 anexos estão com link vazio. |
| novo-hidrolina-chamamento-007-2026 | pista | **fora_perfil** | DOE 7376, matéria 746863: credenciamento de prestadores de serviço médico (escleroterapia). Não é fomento a OSC. |
| cdce7341 · Piracanjuba, Aviso 001/2026 PNAB | pendente | pendente | O DOE 7401 só remete ao site. A página oficial e a API do WordPress não têm o PDF (href vazio), e o PNCP não tem registro. |
| 97773a72 · Corumbá, Aviso 3/2026 | bronze | bronze | A API do site exige login (401), por isso não foi usada. O PNCP não tem registro. A inscrição é presencial até 15/10. |

## 1.3 Totais finais

| Veredito | Lista A (71) | Lista B (267) | Novas (2) | Total |
|---|---:|---:|---:|---:|
| ouro | 10 | 0 | 0 | 10 |
| prata | 0 | 0 | 0 | 0 |
| bronze | 1 | 0 | 0 | 1 |
| pendente | 1 | 0 | 1 | 2 |
| encerrada | 12 | 32 | 0 | 44 |
| fora_perfil | 6 | 22 | 1 | 29 |
| duplicata | 7 | 1 | 0 | 8 |
| ruido | 34 | 212 | 0 | 246 |

Na lista B, 56 edições ficaram com `ato_identificado` e 211 com `sem_oportunidade`.

## 1.4 Vigentes certificadas, por prazo

| Prazo final | Selo | Oportunidade | Valor | id |
|---|---|---|---|---|
| 15/10/2026 | bronze | Corumbá de Goiás, Aviso 3/2026 PNAB (presencial) | não publicado | 97773a72 |
| 16/10/2026 | ouro | SEDS-GO 001/2026, socioeducativo | R$ 8,64 mi + R$ 4,26 mi | 7a5b6e2e |
| 19/10/2026 17h | ouro | Cachoeira Alta, PNAB 001/2026 | R$ 101.385,68 | 4fd88f08 |
| 26/10/2026 17h | ouro | Rubiataba, PNAB 01/2026 | R$ 200.000,00 | 4a13aa8e |
| 26/10/2026 18h | ouro | SECTI-GO 002/2026, Cidadão Tech 60+ | R$ 1 mi | 448c8e19 |
| 26/10/2026 23h59 | ouro | SEGENP Goiânia, Natal no Parque | R$ 5 mi | 53e16dff |
| 29/10/2026 23h59 | ouro | Secult-GO Edital 20/2026, Ocupa Goiás | R$ 1 mi | c546d1fd |
| 01/11/2026 23h59 | ouro | Colinas do Sul, Premiação PNAB 01/2026 | R$ 43.866,00 | d1083dc9 |
| 06/11/2026 | ouro | Anater 006/2026, ATER Agroecologia (lote GO) | R$ 43 mi (nacional) | b7aa39bf |
| 10/11/2026 17h | ouro | Itaberaí, CMDCA 001/2026 | R$ 80 mil | 90de619c |
| 10/05/2027 | ouro | Senador Canedo FMAS 006/2026 (credenciamento contínuo) | até R$ 300 mil | 64b098a6 |

Alertas que devem aparecer junto do selo:

- **53e16dff**: divergência de prazo dentro do edital.
- **448c8e19**: e-mail de recurso divergente.
- **b7aa39bf**: abrangência nacional.
- **64b098a6**:
  - o valor diverge entre os itens 3.2 (R$ 480 mil) e 12.1.2 (R$ 300 mil);
  - o cronograma diz que o resultado sai em 10/06/2026, mas o credenciamento segue aberto até 2027;
  - o protocolo é feito só pelo 1Doc.

## 1.5 Pendentes restantes (pesquisados nas 2 passadas)

| Oportunidade | Itens certificados | Bloqueio | Próxima ação |
|---|---:|---|---|
| cdce7341 · Piracanjuba, Aviso 001/2026 PNAB | 5/12 | Edital e anexos com link vazio no site oficial | Contato com a Secretaria de Cultura, ou nova leitura da página em 7 dias |
| novo-piracanjuba-pncv-002-2026 · Premiação Cultura Viva | 5/12 | Mesmo bloqueio | Idem. É de alta aderência para OSC que é Ponto de Cultura. |

Pistas sem documento ainda: Portaria SMS Goiânia 708/2026 (futuro edital de saúde). Deve ser monitorada; não é oportunidade.

---

# ETAPA 2: melhorias dos motores que encontraram as oportunidades da Parte 1

Base: as 71 oportunidades da lista A, atribuídas ao motor pelo campo `fonte_nome`, e as 267 edições da lista B, todas do motor Querido Diário. "Útil" = oportunidade vigente certificada (ouro, prata ou bronze). "Precisão" = úteis ÷ registros trazidos.

## 2.1 Resultado em uma linha

Os motores de Goiás trouxeram 338 registros, e 11 viraram oportunidade vigente certificada (3,3%). Contando só a lista A, foram 11 de 71 (15,5%), mais que o dobro da Parte 3 (6,7%). As 267 edições de diário renderam **zero** oportunidade vigente nova: 228 delas são de 2021 a 2025.

## 2.2 Indicadores por motor

| Motor (fonte) | Trouxe | Úteis | Precisão | Pend. | Encerr. | Ruído | Dupl. | Fora | Erros de campo |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| Diário Oficial da União | 3 | 2 (1 ouro, 1 bronze) | **67%** | 0 | 0 | 0 | 0 | 1 | 1 "validada" que era fora do perfil |
| PNCP (8 fontes, por órgão) | 9 | 2 ouros | 22% | 0 | 6 | 0 | 0 | 1 | `fim` vazio em 6 (o PNCP tem a data); 4 "validadas" que estavam encerradas ou fora do perfil; 1 link para outro processo; 1 prazo do registro ≠ prazo do edital |
| Diário Oficial do Estado de Goiás | 12 | 2 ouros | 17% | 1 | 1 | 3 | 4 | 1 | Anexo, alteração de cronograma e minuta gravados como oportunidade (4 duplicatas) |
| Fontes estaduais de 1 registro (Site oficial Gov GO, Estaduais Governamentais, DOM Goiânia) | 4 | 3 ouros | **75%** | 0 | 0 | 1 | 0 | 0 | 1 notícia de evento |
| Oportunidades das 25 maiores Prefeituras | 11 | 1 ouro | 9% | 0 | 1 | 7 | 2 | 0 | **8 edições de diário gravadas como edital**; 1 coletada 8 dias depois de encerrada |
| Editais incentivados (contribuintes do ICMS) | 14 | 1 ouro (Anater) | 7% | 0 | 2 | 8 | 1 | 2 | **7 com UF errada** (MG, RJ, SC, BR gravadas como GO); 14 sem `fim` e sem valor |
| Programa estadual de eventos esportivos | 6 | 0 | 0% | 0 | 0 | 5 | 0 | 1 | Home, "transporte", "dispensa" e índices da Seel |
| Assembleia Legislativa — proposições | 3 | 0 | 0% | 0 | 0 | 3 | 0 | 0 | Notícias legislativas |
| Emenda municipal para saúde preventiva | 3 | 0 | 0% | 0 | 1 | 2 | 0 | 0 | Ouvidoria, sorologia, aviso de 2020 |
| FEAS-GO, Emenda estadual, FICA, Ocupação cultural municipal | 6 | 0 | 0% | 0 | 1 | 5 | 0 | 0 | BNDES Data e YouTube num motor "municipal de GO" |
| **Querido Diário (lista B)** | 267 | 0 novas | **0%** | 0 | 32 | 212 | 1 | 22 | Só 2 municípios (Goiânia 233, Aparecida 34); 228 edições de 2021–2025; `fim` vazio em 266 |

## 2.3 Pontos de acerto (manter)

| Motor | O que acertou | Evidência |
|---|---|---|
| DOU | Melhor precisão. Os avisos municipais de PNAB publicados no DOU levam direto ao edital. | Rubiataba (ouro), Corumbá (bronze), Goiatuba (lido, fora do perfil por prova) |
| DOE-GO | Capta avisos de prefeituras do interior que não estão em nenhum outro motor. | Cachoeira Alta (ouro), SECTI 002/2026 (ouro), Piracanjuba (pendente) |
| PNCP por órgão | A API oficial entrega objeto, valor e datas, e os arquivos trazem o edital íntegro. | Colinas do Sul (ouro), Senador Canedo (ouro na 2ª passada) |
| Fontes estaduais oficiais (goias.gov.br) | Poucos registros e quase todos certos. | SEDS 001/2026 (R$ 12,9 mi), Secult Edital 20/2026, Natal no Parque |
| 25 maiores Prefeituras | Quando grava a página do edital, e não a edição, acerta. | Itaberaí CMDCA (ouro) |
| Editais incentivados | Achou a maior oportunidade em valor do recorte, apesar do roteamento errado. | Anater R$ 43 mi |

## 2.4 Pontos de erro (corrigir)

### 2.4.1 Erros comuns

| Código | Erro | Tamanho na Parte 1 | Consequência |
|---|---|---|---|
| G1 | Prazo e valor vazios na coleta | `fim` vazio em 62 de 71; `valor_texto` vazio em 65 de 71; na lista B, `fim` vazio em 266 de 267 | Tudo vira "possível" e depende de leitura manual. |
| G2 | Coleta de oportunidade já encerrada | Todas as 12 encerradas da lista A já estavam vencidas no dia da coleta (a mais antiga, de dez/2023). Na lista B, 228 edições de 2021–2025. | Leitura gasta em histórico. |
| G3 | Selo "validada" sem conferir o prazo | 8 registros validados: 3 encerrados, 2 fora do perfil, 2 ruídos e só 1 ouro | O selo "validada" não é confiável hoje. |
| G4 | Página que não é oportunidade gravada como oportunidade | 34 ruídos na A: home, índices, ouvidoria, notícias, prêmios recebidos por empresas, YouTube | Ruído no painel. |
| G5 | Peças do mesmo edital gravadas separadamente | 7 duplicatas na A: anexo IX, alteração de cronograma, minuta, 2ª notícia, aviso DOE × DOU, URL com parâmetro de rastreio | Contagem inflada. |
| G6 | `tipo_registro` errado | 8 edições inteiras de diário gravadas como "edital" pelo motor das 25 maiores Prefeituras | Edições caem na lista A e escapam do tratamento de diário. |
| G7 | UF forçada para GO | 7 registros de empresas de fora (Aperam MG, Bondinho RJ, ArcelorMittal SC, Banco da Amazônia) mais 1 federal (Anater) | Oportunidade nacional some da Parte 2 ou 3, e oportunidade de outro estado polui Goiás. |
| G8 | Prazo do PNCP tomado como prazo do edital | Pirenópolis: o registro dizia 16/09/2027, e o edital fechou em 17/10/2025 | Uma encerrada aparecia como aberta até 2027. |
| G9 | Cobertura municipal mínima no Querido Diário | 2 de 246 municípios goianos | O motor relê sempre as mesmas capitais e não chega ao interior. |
| G10 | Termo de busca amplo demais no diário | "chamamento público" captura credenciamento de saúde, licitação e extratos (22 fora do perfil, 212 sem oportunidade) | 267 edições lidas para 0 oportunidade nova. |

### 2.4.2 Erros e correções por motor

**Querido Diário (267 edições, 0 úteis novas).**

- Erros: grava a edição inteira, sem filtro de data; cobre só Goiânia e Aparecida; usa termo genérico.
- Correções:
  - janela de data de no máximo 60 dias;
  - expandir para os 246 municípios de GO que o Querido Diário indexa;
  - buscar por expressão composta, por exemplo `("chamamento público" OR "edital de seleção" OR premiação) AND (OSC OR "organização da sociedade civil" OR "termo de fomento" OR "termo de colaboração" OR "termo de execução cultural")`;
  - gravar o **ato**, não a edição, com o trecho e a data-limite extraídos (M4 e M11).

**25 maiores Prefeituras (11, 1 útil).**

- Erro: as edições do DOM de Goiânia e Aparecida são gravadas como "edital".
- Correção: se a URL for de `data.queridodiario` ou de um diário oficial, gravar `tipo_registro = edicao_diario` (M12). Gravar só a página de edital do site da prefeitura (padrão Itaberaí).

**Editais incentivados (14, 1 útil).**

- Erros: UF fixa GO para sites nacionais de empresas; grava páginas institucionais e de prêmios recebidos.
- Correções: UF pelo território do edital (M5); a página institucional da empresa vira "fonte monitorada" (M10).

**PNCP por órgão (9, 2 úteis).**

- Erros:
  - não preenche `fim` e `valor`, que a API traz;
  - marca "validada" registros de 2023–2024;
  - confia em `dataEncerramentoProposta` de "Aviso de Contratação Direta".
- Correções:
  - preencher pela API;
  - para chamamento MROSC, ler o cronograma do edital (arquivo tipo "Edital") e preferi-lo à data do registro;
  - nunca validar com `fim` < hoje (M6).

**DOE-GO (12, 2 úteis).**

- Erro: anexo, alteração e minuta viram registros próprios.
- Correção: agrupar pelo número do edital e pelo órgão (M1). Alteração de cronograma atualiza o `fim` do edital-mãe e não cria registro.

**Programa estadual de eventos esportivos, ALEGO, Emendas de saúde, FEAS, FICA, Ocupação cultural (21 registros, 0 úteis).**

- Correção: rebaixar a "fonte monitorada" (avisa quando a página muda, não cria oportunidade).
- Remover BNDES Data e YouTube do motor "Ocupação cultural municipal".

**DOU (3, 2 úteis), fontes estaduais oficiais (4, 3 úteis).** Manter. Ampliar o DOU com o filtro `Goiás` na seção 3 e "aviso de chamamento" OR "edital de premiação".

## 2.5 Melhorias para implantar (em ordem de prioridade)

| # | Melhoria | Onde | Efeito medido na Parte 1 | Critério de aceite |
|---|---|---|---|---|
| M1 | Deduplicar por (órgão, número do edital, ano) e por URL canônica (sem `utm_`, `fbclid`, `#`). Anexo, alteração e minuta se ligam ao edital-mãe. | Gravação, todos os motores | Elimina as 8 duplicatas | Duplicatas abaixo de 5% |
| M3 | Filtro de não-oportunidade por título e URL: home, índice, ouvidoria, notícia de resultado ou evento, "prêmios e reconhecimentos", extrato de termo já celebrado, YouTube e redes, portal de dados | Gravação | Tira cerca de 30 dos 34 ruídos da A | Ruído abaixo de 10% por motor |
| M4 | Prazo obrigatório: extrair `fim` (padrões "de dd/mm/aaaa a dd/mm/aaaa", "até às HHh do dia", cronograma "Envio das propostas"); com `fim` < data da coleta, arquivar como encerrada | Gravação | Evita as 12 encerradas da A e as 32 da B | 0 registros abertos com prazo vencido |
| M5 | UF e nível pelo território do edital, nunca pelo motor: o domínio `.go.gov.br` dá GO; a sede da empresa não define UF; gov.br e autarquias federais dão "federal/BR" | Gravação | Corrige 8 roteamentos (7 empresas e a Anater) | 0 registros de fora de GO na Parte 1 |
| M6 | Rota PNCP completa: preencher `fim`, `valor` e `orgao` pela API; ler o arquivo "Edital" e preferir o cronograma do edital à `dataEncerramentoProposta`; bloquear a validação com `fim` < hoje | Motores PNCP | Teria evitado Pirenópolis aberta até 2027 e as 5 validações erradas; acelera o ouro (Senador Canedo) | Todo registro PNCP sai com objeto, prazo e valor certificados |
| M7 | O selo "validada" exige prazo vigente com trecho e órgão oficial | Validador | 7 de 8 validações estavam erradas | Precisão da validação de 90% ou mais |
| M11 | Querido Diário: janela de 60 dias, 246 municípios de GO, consulta composta (ver 2.4.2) e extração do ATO com o trecho | Motor QD | De 267 edições e 0 achados para poucas dezenas de atos pertinentes | Pelo menos 30% dos atos gravados são oportunidade de OSC |
| M12 | `tipo_registro` pela URL: `data.queridodiario.ok.org.br`, `diariooficial.*`, `dom.*` e `/edicao/` dão `edicao_diario` | Gravação | Corrige as 8 edições gravadas como edital | 0 edições na lista A |
| M8 | Classificador de perfil: "credenciamento de prestadores de serviços de saúde", "pessoa física", "coletivo sem CNPJ", "adesão de municípios", "PMI", "linha de crédito" dão `fora_perfil` com trecho | Depois da leitura | Antecipa os 6 da A e os 22 da B | Nenhum fora do perfil exibido como oportunidade |
| M9 | Ponte com o Chrome da titular e leitura de PDF escaneado por imagem (já testada: Goiatuba, Secult 20/2026); leitor de .docx | Cartório | Resolveu os 4 pendentes desta rodada; restam 2 por link vazio na origem | Pendentes abaixo de 5% |
| M10 | Fonte monitorada: páginas-índice oficiais (Secult "Chamamentos 2026", Seel "Credenciamento", Piracanjuba "Ciclo II") não viram oportunidade; o sistema avisa quando surge link ou PDF novo e cria a derivada | Esteira | Teria achado a Premiação PNCV 002/2026 automaticamente | Toda página-índice oficial monitorada semanalmente |
| M13 | Painel de qualidade por motor (precisão, duplicata, ruído, encerrada na coleta, `fim` vazio, validação errada), com rebaixamento automático abaixo de 5% de precisão por 2 ciclos | Painel | Os 7 motores com 0% passam a fonte monitorada | Indicadores publicados a cada ciclo |

### 2.5.1 Especificação para implantação

```json
{
  "M1_dedupe": {"chave": ["orgao_normalizado", "numero_edital", "ano"], "url_canonica": {"remover_query": ["utm_*", "fbclid", "gclid"], "remover_fragmento": true, "barra_final": false},
                "filhos": {"padroes_titulo": ["anexo", "minuta", "altera[çc][ãa]o do cronograma", "retifica[çc][ãa]o", "errata"], "acao": "vincular_ao_edital_mae_e_atualizar_fim"}},
  "M3_nao_oportunidade": {"titulo_regex": ["^p[áa]gina inicial", "ouvidoria", "pr[êe]mios e reconhecimentos", "resultado (final|preliminar)", "lista de aprovados", "extrato do termo", "programa[çc][ãa]o", "transporte"],
                          "dominios_bloqueados": ["youtube.com", "bndes.gov.br/wps/portal/site/home/transparencia/dados", "blogspot.com"], "acao": "descartar_com_motivo_ou_virar_pista"},
  "M4_prazo": {"regex": ["de (\\d{2}/\\d{2}/\\d{4}) (a|até) (\\d{2}/\\d{2}/\\d{4})", "at[ée] (às )?\\d{1,2}h\\d{0,2}(min)? do dia (\\d{2}/\\d{2}/\\d{4})", "Envio das propostas[^\\n]{0,60}(\\d{2} ?/\\d{2}/\\d{4})"],
               "se_fim_menor_que_coleta": "situacao=encerrada", "sem_prazo": "situacao=sem_prazo"},
  "M5_territorio": {"dominio_go": "\\.go\\.gov\\.br$|goias\\.gov\\.br$", "federal": ["gov.br", "anater.org", "bndes.gov.br", "in.gov.br(sem município)"], "empresa": "usar território do edital; nunca a UF do motor"},
  "M6_pncp": {"api": "https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}", "arquivos": "https://pncp.gov.br/pncp-api/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos",
              "regra": "para chamamento MROSC, prazo = cronograma do arquivo tipoDocumentoNome=Edital; dataEncerramentoProposta só se o edital não tiver cronograma"},
  "M7_validacao": {"exige": ["fim >= hoje com trecho", "orgao oficial", "link do documento oficial"]},
  "M11_querido_diario": {"janela_dias": 60, "territorios": "todos os IBGE de GO (52xxxxx) indexados",
                         "consulta": "(\"chamamento público\" OR \"edital de seleção\" OR premiação) AND (OSC OR \"organização da sociedade civil\" OR \"termo de fomento\" OR \"termo de colaboração\" OR \"termo de execução cultural\")",
                         "unidade_gravada": "ato (título, trecho, data-limite, página)"},
  "M12_tipo_registro": {"edicao_diario_se_url": ["data.queridodiario.ok.org.br", "diariooficial.", "/edicao", "dom."]},
  "M8_perfil": {"fora_perfil_regex": ["prestadores de servi[çc]os (especializados )?de sa[úu]de", "pessoa f[íi]sica", "coletivo(s)? sem (CNPJ|personalidade)", "ades[ãa]o (institucional )?de munic[íi]pios", "procedimento de manifesta[çc][ãa]o de interesse", "linha de cr[ée]dito|financiamento"]},
  "M13_painel": {"metricas": ["precisao", "duplicatas", "ruido", "encerrada_na_coleta", "fim_vazio", "validacao_errada"], "rebaixar_se": "precisao < 5% por 2 ciclos"}
}
```

**Teste de regressão.** Os 338 vereditos desta Parte 1 (lotes `resultado_ABERTAS_P1-GO_*.json`) passam a ser o gabarito de Goiás para validar M1 a M13 antes de cada implantação.

## 2.6 Ordem de implantação

1. **M4, M5, M7 e M12.** São regras determinísticas na gravação. Cortam as encerradas, corrigem a UF e o tipo e tornam o selo "validada" confiável.
2. **M1, M3 e M6.** Tiram duplicata e ruído e fazem do PNCP fonte certificada.
3. **M11.** Refaz o motor do Querido Diário, que hoje responde por 79% do volume e não produz nada.
4. **M8, M9, M10 e M13.** Qualidade de perfil, pendentes, páginas-índice e medição contínua.

## 2.7 Conselho de 7 lentes

- **Extremamente pessimista:** 327 de 338 registros não serviam. O motor do Querido Diário gerou 267 leituras e nenhuma oportunidade nova. O selo "validada" errou 7 de 8 vezes. Se a titular confiar no selo atual, pode se inscrever em edital encerrado, como o de Pirenópolis, que aparecia aberto até 2027.
- **Pessimista:** o prazo vem vazio em 87% da lista A, e as encerradas foram todas coletadas já vencidas. Sem M4 o sistema continua mostrando histórico como oportunidade. A divergência interna de valor em Senador Canedo (R$ 480 mil × R$ 300 mil) mostra que até o documento oficial exige alerta.
- **Levemente pessimista:** as regras M3 e M12 podem descartar uma edição de diário que traga um ato pertinente. Mitigação: o descarte vira "pista" com motivo, nunca exclusão, e o gabarito de 338 mede a perda.
- **Neutro (decide):** implantar M4, M5, M7 e M12 já, com o gabarito de 338 como teste de aceite. Depois M1, M3 e M6, e em seguida M11.

  Parâmetros mínimos por motor:
  - precisão de 15% ou mais (a média atual da lista A);
  - duplicatas abaixo de 5%;
  - ruído abaixo de 10%;
  - `fim` preenchido em 95% ou mais;
  - 0 registros abertos com prazo vencido;
  - validação correta em 90% ou mais.

  Mitigações:
  - todo descarte automático guarda motivo e pode ser revertido;
  - os alertas dos 4 ouros com divergência aparecem junto do selo;
  - os 2 pendentes de Piracanjuba ficam como fonte monitorada semanal.
- **Levemente otimista:** os motores oficiais (DOU, DOE-GO, PNCP e goias.gov.br) já entregam 9 dos 11 úteis com pouquíssimo ruído. O problema está concentrado em poucos motores genéricos.
- **Otimista:** só nesta parte há cerca de R$ 64 milhões em oportunidades vigentes certificadas (R$ 21 mi goianas e R$ 43 mi da Anater). Com M6, o PNCP certifica sozinho os chamamentos municipais, e a 2ª passada provou isso em Senador Canedo.
- **Extremamente otimista:** com M10 e M11 o sistema passa a ver o interior de Goiás (246 municípios) e as páginas-índice oficiais em tempo quase real. Ele vira a primeira carteira certificada de editais para OSC do estado, a ponto de antecipar editais como a Premiação Cultura Viva de Piracanjuba antes de o próprio município publicar os anexos.
