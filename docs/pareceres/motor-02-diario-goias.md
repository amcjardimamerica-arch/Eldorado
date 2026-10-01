# Parecer do conselho — Motor 02 · Diário Oficial do Estado de Goiás

**Data:** 01/10/2026 · **Motor:** `do-goias` (Bússola, posição 02) · **Matéria:** técnica (engenharia de coleta), com reflexo jurídico (MROSC, PNAB, fundos estaduais e municipais)

## 1. Síntese

Em setembro de 2026, o motor 02 não leu o Diário do Estado nenhuma vez. Trouxe ao sistema 10 registros, todos de páginas da SECULT, quase todos de janeiro a abril, com prazo vencido. Repetidos dia após dia, esses registros viraram 111 "achados" no contador.

Nesse mesmo mês, o Diário publicou **16 seleções diferentes abertas a entidades do terceiro setor**. O motor deixou passar todas. Exemplos:

- o **Chamamento Público nº 001/2026 da SEDS** (R$ 4.258.987,15);
- os editais PNAB da **SECULT-GO** (Natal do Bem nº 19/2026 e Ocupa Goiás nº 20/2026);
- o **Chamamento nº 002/2026 da SECTI**;
- **12 editais de prefeituras** que publicam no Diário do Estado: Senador Canedo ×4, Itumbiara ×3, Orizona, Morrinhos, Mozarlândia, Goiatuba e Nova Iguaçu de Goiás.

**Nove delas seguem abertas em 01/10/2026.**

**Decisão do neutro:** aprovar a versão 2. O motor passa a ler o Diário pela estrutura aberta do portal, em três frentes:

- a busca de texto completo;
- o sumário de cada edição, organizado por órgão, com o texto de cada matéria;
- a API pública dos sites das secretarias.

O classificador é comum aos motores 01 e 02 (`src/atos_diario.py`), não usa IA e escreve o motivo de cada decisão.

## 2. Resultado de setembro/2026 (motor antigo)

| Item | Número | Evidência |
|---|---|---|
| Dias com registro de execução | 26 de 30 (faltam 01, 02, 23 e 27/09) | `estado/esquadra_diario.json` › `do-goias` |
| Dias úteis sem execução | 3 (01, 02 e 23/09) | idem |
| Dias em que o Diário foi lido | **0** | 06–20/09: `http: null`, 0 falhas, 0 achados (pulado por "exige Brasil"); 21–30/09: só páginas de secretaria |
| Dias pintados de "azul, funcionou sem oportunidade" sem ter lido nada | 15 (06 a 20/09) | `cor: azul` com `http: null` |
| "Achados" contados | 111 | `estado/esquadra.json` › `achados_total` |
| Registros reais na base | 10, todos de `goias.gov.br/cultura`, coletados em 21/09 | `dados/oportunidades/oportunidades.jsonl` › `fonte_id = do-goias` |
| Achados vindos do próprio Diário | **0** | domínio das URLs |
| Achados repetidos | os mesmos 11 itens em 8 dias (21, 22, 25, 26, 28, 29 e 30/09; 24/09 com 1) | `esquadra_diario.json` › `achados`, `trecho` |
| Oportunidade aberta e válida | 1, o credenciamento em fluxo contínuo do Goiás Social (Auxílio Nutricional), vindo da página da SEDS | `docs/dados/achados_motores.json` › `decisao: valida_aberta` |
| Descartados | 2 duplicatas e 1 reabertura vencida (até 05/02/2026); os demais caem como "fora da janela, mais de 60 dias sem prazo" | `achados_motores.json` › `opressor.estado` |
| Veredito da auditoria antiga | "MANTER — funcionando, 9 de 9 ativos, 0% eliminado" | `docs/dados/relatorio_motores.json`. Contradiz os descartes acima |

## 3. Defeitos encontrados

1. **D1 — O Diário nunca foi lido.** Em 03/09 o motor tentou `/portal/edicoes` e `/portal/visualizacoes/pesquisa`, caminhos que não existem, e recebeu erro HTTP (`estado/bloqueios.json`). A home respondeu 200. Mesmo assim, o host foi marcado "exige Brasil" (`config/sensores.json` › `exige_brasil`) e o motor passou a ser pulado na nuvem.
2. **D2 — "Pulado" virou "funcionou".** De 06 a 20/09, o calendário mostrou azul sem nenhuma página lida (`esquadra_diario.json`: `http: null`).
3. **D3 — Leitura pelo rótulo do link.** O motor lia a home e o "portal", que têm 17 KB e nenhum edital. O ato fica no texto da matéria.
4. **D4 — Contagem inflada.** 111 "achados" para 10 registros: o contador soma a mesma leitura todos os dias.
5. **D5 — Captura sem prazo.** Os 10 registros de setembro são itens de jan–abr/2026, com prazo vencido, capturados como `capturada`.
6. **D6 — Anexo e listagem tratados como oportunidade.** "ANEXO IX – MINUTA DO TERMO DE COLABORAÇÃO" e as páginas "Chamamentos Públicos" entraram como achado.
7. **D7 — As prefeituras do interior ficavam de fora.** A seção MUNICÍPIOS do Diário (1.327 matérias em setembro) nunca foi lida. Doze das 16 oportunidades vieram de lá.
8. **D8 — Rotas mortas.** `/social/cedca/`, `/social/ceas/` e `/social/feas/` dão 404, e `goias.gov.br` teve 53 bloqueios ou tempos esgotados em páginas HTML (`bloqueios.json`). A API WordPress das mesmas pastas responde 200.
9. **D9 — Auditoria otimista.** `relatorio_motores.json` deu "MANTER, 0% eliminado" a um motor que não leu a sua fonte o mês inteiro.

## 4. Rotas (Etapa 2)

Os testes com IP brasileiro foram feitos pelo navegador do titular em 01/10/2026. Na nuvem do GitHub o resultado ainda não está medido: o motor tenta e registra a causa de qualquer falha. Neste ambiente de análise, todos os domínios são barrados pela política de rede.

| Rota | IP brasileiro | O que entrega | Decisão |
|---|---|---|---|
| `diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/AAAA-MM-DD.json` | 200 | edições do dia (normal + suplemento): setembro = 40 edições | **usar** (Fonte B) |
| `…/portal/visualizacoes/view_html_diario/{id}` | 200 | sumário por órgão; setembro = 5.866 matérias | **usar** (Fonte B) |
| `…/apifront/portal/edicoes/publicacoes_ver_conteudo/{materia}/{id}` | 200 | texto integral da matéria | **usar** (Fonte B) |
| `…/busca/busca/buscar/query/{p}/di:…/df:…/?1=1&q=…` | 200 | busca de texto completo, 10 resultados por página | **usar** (Fonte A) |
| `…/portal/edicoes/download/{id}` | 200 | PDF da edição | espelho (último recurso) |
| `…/portal/edicoes` e `…/portal/visualizacoes/pesquisa` | erro HTTP (03/09, GitHub) | não existem | **descartar** |
| `goias.gov.br/{cultura,social,esporte,saude,educacao}/wp-json/wp/v2/posts` | 200 | posts com data, link e conteúdo; setembro = 23 posts com termos de seleção | **usar** (Fonte C) |
| `goias.gov.br/cultura/chamamentos-publicos-2026/` → `…-lei-13-019-14/` | 200 | listagem SECULT | espelho |
| `goias.gov.br/cultura/chamamentos-publicos-secult/` | 200 | listagem SECULT | espelho |
| `goias.gov.br/esporte/chamamento-publico/` | 200 | listagem SEEL | espelho |
| `goias.gov.br/social/` | 200 | notícias SEDS | coberta pela API (Fonte C) |
| `goias.gov.br/social/cedca/`, `/social/ceas/`, `/social/feas/` | **404** | — | **descartar**; o CEDCA está em `/social/conselho-estadual-dos-direitos-da-crianca-e-do-adolescente-ced…` e é coberto pela API |
| PNCP com UF GO | — | já coberto pelo motor `pncp-api` | não duplicar |
| Emendas impositivas ALEGO | — | entram pela Fonte A ("emenda impositiva", "emendas parlamentares": 106 resultados em setembro) | **usar** |

## 5. Parametrização antes × depois

| Item | Antes | Agora |
|---|---|---|
| O que lê | rótulo dos links da home e do "portal" | texto de cada matéria (sumário) + página achada pela busca + post das secretarias |
| Diário na nuvem | pulado ("exige Brasil") | tentado; a falha vira causa descrita; coleta local como reforço |
| Busca | nenhuma | 20 consultas dirigidas, janela de 7 dias, até 5 páginas cada |
| Edição do dia | não | normal + suplemento, últimos 3 dias, até 60 matérias de interesse por edição |
| Secretarias | 3 páginas HTML (uma com 404 intermitente) | API WordPress de 5 pastas, janela de 10 dias |
| Prefeituras no Diário do Estado | ignoradas | lidas, com território municipal (`GO/<município>`) |
| Recorte da página | — | pelo carimbo "Protocolo NNNNNN" que fecha cada matéria |
| Classificação | léxico no rótulo | `src/atos_diario.py`: tipo, regime, público, órgão e prazo, com o motivo escrito |
| Ruído vetado | — | PSS e atos de pessoal, licitação/pregão/leilão (inclusive de fundo municipal), PNAE, credenciamento de prestadores, Organização Social (Lei 15.503/2005), FSA para empresas |
| Mesmo edital em fontes diferentes | registros separados | um registro (órgão + número, ou órgão + dia), com todas as fontes observadas |
| Edital com resultado ou prazo vencido em outra publicação | continuava "aberto" | vai para ACOMPANHAR, com o motivo |
| Alarme | nenhum | 3 dias úteis seguidos sem ler o Diário |
| Agenda | 07:23 seg–sex, "coleta local" | 07:23 seg–sex, "nuvem + local"; a busca de 7 dias recupera o dia perdido |

## 6. Calibração com setembro/2026 (Etapa 4)

O código desta versão rodou, sem alteração, sobre o mês inteiro. Isso foi feito no navegador do titular, com IP brasileiro e Python no próprio navegador.

| Medida | Número |
|---|---|
| Edições lidas | 40 (normal + suplemento) |
| Matérias no sumário | 5.866 |
| Matérias abertas (Fonte B) | 232 |
| Páginas achadas pela busca (Fonte A) | 299, recortadas em 486 matérias de interesse |
| Posts das secretarias (Fonte C) | 23 |
| Total classificado | 741 |
| OPORTUNIDADE (como no dia da publicação) | 23 leituras → **18 registros**, 16 seleções diferentes |
| ACOMPANHAR (em 01/10) | 162 leituras → 113 atos únicos (resultados, extratos de termo e convênio, inexigibilidades, vagas em conselho) |
| RUÍDO | 566 |
| Abertas em 01/10/2026 | **10 registros, 9 seleções diferentes** |

**Conferência manual:**

- **OPORTUNIDADE:** as 18 foram abertas e conferidas, e todas são seleções reais para OSC ou agentes culturais. A precisão foi de **18/18**. Há 2 registros duplicados, que contam como acerto mas são ruído de painel: Mozarlândia (aviso e busca) e Ocupa Goiás (extrato e notícia).
- **ACOMPANHAR:** de 10 sorteados, 8 estavam corretos. Os 2 errados eram extratos de publicação da SECULT, que são lançamento de edital, e viraram regra e teste.
- **RUÍDO:** 10 sorteados conferidos, todos corretos. Também foram revistos os 22 itens de RUÍDO com tipo "abertura". Um deles, o credenciamento PNAB de Silvânia, passou para ACOMPANHAR ("conferir se é de pareceristas").

Todo erro achado virou regra e teste em `tests/test_motor02_diario_goias.py`:

- o "Extrato de Publicação" da SECULT é lançamento de edital;
- o pregão de fundo municipal é licitação;
- a "lista de aprovados" é andamento;
- o órgão de prefeitura sem a palavra "municipal" é reconhecido;
- edital com resultado publicado fecha a oportunidade;
- FSA "para empresas" não é edital de associação;
- notícia de "lança edital" é abertura.

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de sistemas de coleta pública, especialista em falhas silenciosas.**
O pior não foi o motor ter falhado. Foi o painel dizer que ele funcionava: 15 dias de "azul" sem uma página lida, e uma auditoria que mandou "MANTER". A versão 2 ainda depende de um portal que pode recusar a nuvem. Se recusar, o alarme de 3 dias úteis tem de chegar ao titular, e não ficar só num JSON.

**2. Pessimista — staff engineer de busca, obcecado por duplicata e falso positivo.**
A deduplicação sem número de edital usa órgão + dia. Isso juntaria dois avisos diferentes da mesma prefeitura no mesmo dia, e não junta notícia com extrato publicados em dias distintos. Os dois duplicados de setembro mostram isso. O recorte por "Protocolo" depende do layout da página: quando duas colunas se misturam, um aviso herda o texto do vizinho (Mozarlândia "nº 062/2026 — Registro de Preços").

**3. Levemente pessimista — professor de engenharia de computação, especialista em extração de texto.**
A busca devolve a página inteira, sem quebra de linha. O prazo é achado por expressão regular e falhou em 10 das 18 oportunidades, que ficaram "sem prazo no trecho". Para estas, a Fonte B (texto da matéria) é a garantia, e ela só lê títulos que passam no filtro. Seis das 16 seleções só foram achadas pela busca.

**4. Neutro — CTO de plataforma pública de dados, mediador.** O voto está na seção 8.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas explicáveis.**
O classificador ficou único para os dois diários e explica cada decisão. O titular, como advogado, consegue auditar "licitação de fundo municipal — não é fomento a OSC" sem ler código. As regras novas nasceram de erros reais de setembro, cada uma com teste.

**6. Otimista — staff engineer de produto, foco em captação.**
A seção MUNICÍPIOS é o achado do mês: prefeituras pequenas publicam ali e em nenhum outro lugar que o sistema lê. Doze das 16 seleções vieram de lá. E os 113 atos ACOMPANHAR mostram quais secretarias fazem parceria com OSC, com termo, valor e prazo de prorrogação. É inteligência para a próxima rodada de captação.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.**
A mesma estrutura (busca + sumário + matéria) serve à carga histórica de 5 anos do Diário do Estado sem custo. Com ela, o sistema aprende a época em que cada fundo abre (só em setembro, 6 municípios abriram editais da PNAB ciclo 2) e avisa a associação antes da publicação.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 02 versão 2 e publicar.

**Metas (medidas a cada 30 dias em `estado/diario_goias.json` › `historico`):**

| Indicador | Meta |
|---|---|
| Edições de dias úteis lidas | ≥ 90% |
| Atraso entre publicação e leitura | ≤ 1 dia |
| Precisão de OPORTUNIDADE (conferida pelo titular) | ≥ 80% (setembro: 18/18) |
| Falhas com causa descrita | 100% |
| CPF gravado | 0 |

**Mitigação de riscos:**

1. **Portal recusa a nuvem:** cada fonte registra o que leu no dia (`fonte_do_dia`), e o alarme dispara com 3 dias úteis sem Diário. A coleta local lê as Fontes A e B, e a Fonte C segue na nuvem todos os dias.
2. **Duplicata:** chave por órgão + número. Sem número, a chave é órgão + dia. Um resultado publicado ou um prazo vencido em outra fonte fecha a oportunidade.
3. **Falso positivo:** vetos estaduais (PSS, licitação, PNAE, OS, pessoal, FSA para empresas) e cabeçalho de licitação vencem o vocabulário de fomento.
4. **Prazo ausente:** sem prazo no texto e com mais de 60 dias de publicação, o edital vai para ACOMPANHAR com o aviso de conferir.
5. **Dado pessoal:** todo CPF vira `[CPF]` antes de gravar.
6. **Instrução escondida no texto:** um ato suspeito vai para a quarentena.

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/atos_diario.py` (novo) | classificador comum (tipo, regime, público, órgão estadual ou municipal, prazo), vetos estaduais, recorte por "Protocolo", chave de deduplicação |
| `src/diario_goias.py` (novo) | leitor do motor 02: Fontes A, B e C, deduplicação, fechamento por resultado ou prazo, alarme, diagnóstico por fonte |
| `src/sensores.py` | `do-goias` passa ao novo leitor antes da trava "exige Brasil" |
| `config/diario_goias.json` (novo) | endpoints, 20 consultas, janelas e limites |
| `config/sensores.json`, `config/rotas_motores.json`, `config/agenda_motores.json` | URLs reais, rotas sem 404, léxico e vetos, "nuvem + local" |
| `src/auditoria_29.py`, `src/auditoria_motores.py`, `scripts/descricao_motores.py` | o motor 02 deixa de ser marcado "bloqueado"; textos do conselho atualizados |
| `tests/test_motor02_diario_goias.py` (novo) | 18 testes com trechos reais de setembro, API simulada e bloqueio da nuvem |

**Testes:** a suíte completa tem as mesmas 46 falhas antes e depois da mudança, todas já existentes no main. São 894 testes, 18 deles novos e todos verdes. `scripts/verificar_privacidade.py` não encontrou nenhuma credencial publicada.

## 10. Seleções abertas em 01/10/2026, para o titular decidir

| Publicação | Órgão | Edital | Prazo no texto | Endereço |
|---|---|---|---|---|
| 28/09 | Prefeitura de Nova Iguaçu de Goiás | Chamamento nº 001/2026: OSC para termo de fomento, atendimento a crianças e adolescentes com TEA/TDAH | **02/10/2026** | DOE ed. 7382, p. 74 |
| 25/09 | Prefeitura de Goiatuba | Chamamento nº 004/2026: PNAB ciclo 2, projetos culturais | **13/10/2026** | DOE ed. 7376 |
| 24/09 | SECTI-GO | Chamamento nº 002/2026: seleção de OSC | conferir no edital | DOE ed. 7374 |
| 29/09 | SECULT-GO | Ocupa Goiás — Brasilidades & Futuros 2027 nº 20/2026 (PNAB) | conferir no edital | DOE ed. 7384 e site da SECULT |
| 18/09 | Prefeitura de Mozarlândia | Chamamento PNAB 2026 ciclo 2 | conferir no edital | DOE ed. 7366 |
| 10/09 | Prefeitura de Itumbiara | Chamadas Públicas nº 011, 012 e 013/2026: Pontos e Pontões de Cultura, projetos Aldir Blanc, Rede Municipal de Pontos | conferir no edital | DOE ed. 7356 |
| 04/09 | Prefeitura de Orizona | Chamamento nº 01/2026: projetos culturais | conferir no edital | DOE ed. 7350 |

Encerradas em setembro, que o motor antigo perdeu:

- **SEDS 001/2026** (R$ 4,26 milhões, até 21/09);
- **Senador Canedo 002, 003, 004 e 005/2026** (até 25/09);
- **Morrinhos** (até 15/09);
- **SECULT Natal do Bem 19/2026** (resultado preliminar em 28/09).

## 11. Pendências

1. **Primeira execução na nuvem:** confirmar se o portal do Diário aceita o servidor do GitHub. Se recusar, a coleta local passa a ser obrigatória para as Fontes A e B. O diagnóstico vai dizer.
2. **Motor 01:** passar a importar o classificador de `src/atos_diario.py`. O PR nº 11 já foi mesclado; isso fica para o próximo ajuste, para não mexer no motor 01 sem nova calibração.
3. **Painel:** mostrar os atos ACOMPANHAR no cartão do motor e acusar "pulado" em vez de "azul". Depende da identidade visual definitiva.
4. **Contador da esquadra:** contar achados únicos em vez de leituras (D4). Muda a régua de todos os motores e precisa de decisão própria.
5. **Registros antigos:** os 10 itens velhos de setembro continuam na base. A revisão humana decide arquivá-los (`merge_registro` preserva o status).
6. **Carga histórica:** levar a busca de 5 anos do Diário do Estado para a previsão de abertura dos fundos.
