# Parecer do conselho — Motor do Congresso Nacional (Câmara dos Deputados, Senado Federal e CMO)

**Data:** 02/10/2026 · **Associação de referência:** A.M.C. Jardim América (OSC, Goiânia/GO) · **Par federal dos motores 05 (Câmara de Goiânia) e 06 (ALEGO).**

## 1. Síntese

O Congresso Nacional quase não publica edital para associação. O que ele produz para uma OSC é outra coisa, e o sistema não lia nenhuma delas:

1. **A janela de emendas ao orçamento da União.** O PLOA 2027 (PLN 24/2026) chegou em 31/08/2026 com **R$ 28,5 bilhões em emendas individuais** (cerca de **R$ 43,0 milhões por deputado** e **R$ 79,1 milhões por senador**, 50% obrigatoriamente na saúde) e **R$ 16,3 bilhões de emendas de bancada estadual** (Informativo Conjunto das Consultorias de Orçamento, 04/09/2026). A bancada de Goiás tem **17 deputados e 3 senadores**: na referência do PLOA, perto de **R$ 968 milhões** em emendas individuais só de parlamentares goianos. O termo de fomento ou de colaboração com recurso de emenda é celebrado **sem chamamento público** (Lei 13.019/2014, art. 29, hipótese própria, que não se confunde com a dispensa do art. 30). O que decide é chegar ao gabinete **antes** de a emenda ser apresentada.
2. **As regras que mudam a vida das entidades.** Em quatro meses, a Câmara recebeu 19 proposições com "sem fins lucrativos". Exemplos: IBS/CBS das entidades (PLP 236/2026), REFIS do terceiro setor (PL 3088/2026), cessão de créditos de energia a entidades (PL 2983/2026), tarifa social de água (PL 3505/2026) e alteração da Lei 13.019 (PL 3527/2026). O PL 2465/2026, que prorroga o crédito do FGTS para filantrópicas e instituições sem fins lucrativos, virou a Lei 15.486/2026.
3. **Chamamento, prêmio ou honraria das próprias Casas.** É raro. As 13 convocações públicas do Senado desde 2017 não tiveram nenhuma para OSC.

**Decisão:** criar o motor `congresso-nacional`, com leitor próprio (`src/congresso_nacional.py`), sem IA e sem tokens. Ele tem cinco fontes: a página da LOA e os comunicados da CMO, a API da Câmara, a API do Senado, as notícias das duas Casas e as convocações do Senado. A situação oficial da janela de emendas passa a alimentar a área de emendas.

## 2. Diagnóstico — o que o sistema tinha

| O que existia | Defeito |
|---|---|
| Área de emendas (`src/emendas.py`): levanta os 594 parlamentares pelas APIs (funciona no GitHub) e abre uma linha "Emenda Parlamentar — Câmara e Senado" com janela **fixa de 01/10 a 30/11** | Não lia o prazo oficial da CMO. A janela de 30/11 é de articulação, e o painel a mostra como prazo (corrigido: a linha passa a trazer a situação oficial ao lado). Em 02/10, a apresentação de emendas ao PLOA 2027 **ainda não estava aberta**: etapa "não iniciada", PLN aguardando despacho para a CMO. |
| Fonte "Emenda parlamentar federal individual" do catálogo das 260 (`captacao-200`) | Aponta para as **homes** da Câmara, do Senado, da ALEGO e da Câmara de Goiânia. A home não traz prazo, proposição nem edital. |
| Nenhum motor regular do Congresso | Os motores 05 e 06 cobrem o município e o estado; o federal não tinha par. |
| Serviço antigo do Senado (`/materia/pesquisa/lista`) | Foi **desativado em 01/02/2026**. O serviço novo é `/dadosabertos/processo`. |

## 3. Varredura das rotas (02/10/2026)

O navegador do titular não respondeu nesta sessão. As rotas foram lidas pelo leitor web da Anthropic (fora do Brasil, como o GitHub); o contêiner não tem saída para `.leg.br`.

| Rota | Resultado | Uso no motor |
|---|---|---|
| `congressonacional.leg.br/web/orcamento/acompanhe/orcamento-anual/-/loa/2027` | PLN 24/2026, Mensagem 731/2026 de 31/08, aguardando despacho. Etapas: "Apresentação de emendas" **não iniciada** | **Fonte A**: situação e datas da etapa de emendas |
| `…/web/cmo/comunicados` | LOA 2027 – Instruções do Lexor (30/09); Matérias novas e prazo de emendas (22/09); Informativo Conjunto (08/09); Ofício de Apoio à Emenda – LexEdit (07/09); Proposta do Executivo (01/09) | **Fonte A**: comunicados |
| Informativo Conjunto (PDF) | Valores do PLOA 2027 conferidos por citação literal | Referência fixa em `config/congresso_nacional.json` |
| `dadosabertos.camara.leg.br/api/v2/proposicoes?keywords=…` | JSON válido. A busca casa a expressão e aceita acento. "sem fins lucrativos": 19 desde 01/06; "sociedade civil": 5 desde 01/07; "terceiro setor": PL 3088/2026; "associação de moradores": 4 desde 2025; "13.019" e "filantropicas" vêm vazios | **Fonte B** |
| `legis.senado.leg.br/dadosabertos/processo?termo=…` | JSON válido, com situação e norma gerada | **Fonte C** |
| RSS da Câmara (`/noticias/rss/ultimas-noticias`) e do Senado (`/noticias/feed/todasnoticias/rss`) | RSS 2.0 válido | **Fonte D** |
| Convocações públicas do Senado (`www6g.senado.leg.br/…/convocacoes-publicas`) | 13 desde 2017: concessão de espaço, TI, exposições e audiências técnicas; nenhuma para OSC | **Fonte E** (vigia) |
| Licitações da Câmara (`camara.leg.br/licitacoes-e-contratos`) | Licitações, contratos e cessão de espaços, sem chamamento para entidades. A página de notícias respondeu 429 | Fora do motor: o PNCP (motor 04) já cobre as licitações |
| Comissão de Legislação Participativa e e-Cidadania | Sugestão legislativa por entidades: é participação, não captação | Fora do motor (anotado para o Farol) |

## 4. O que é oportunidade para a associação — leitura jurídica

| Tipo | Natureza | Classificação |
|---|---|---|
| Emenda individual (RP6) e de bancada (RP7) ao PLOA | Recurso. Execução obrigatória, salvo impedimento de ordem técnica (CF, art. 166, §§ 9º a 13; LC 210/2024). À OSC chega por termo de fomento ou de colaboração **sem chamamento** (Lei 13.019, art. 29), pelo órgão executor; a "transferência especial" (CF, art. 166-A) vai ao ente federado, não à OSC | **OPORTUNIDADE** quando a etapa de apresentação está aberta; **ACOMPANHAR** antes e depois |
| Comunicado da CMO (prazo, cronograma, LOA/LDO) | Insumo de prazo | ACOMPANHAR |
| Proposição que muda regra, tributação, programa ou recurso das entidades | Insumo de habilitação e planejamento | ACOMPANHAR (nunca edital) |
| Chamamento ou prêmio das Casas com entidades como público e com prazo | Recurso ou reconhecimento | OPORTUNIDADE |
| Honraria (prêmio, comenda, diploma com indicação de entidades) | Reputação, não recurso | OPORTUNIDADE se tiver prazo; senão ACOMPANHAR |
| Convocação para empresas, TI ou concessão de espaço comercial | Contratação | RUÍDO |
| Dia nacional, homenagem, denominação, concurso | — | RUÍDO |

**Requisitos:** a própria Lei 13.019 exige tempo mínimo de CNPJ ativo — 1, 2 ou 3 anos para parceria com Município, Estado ou União, respectivamente, com redução possível por ato do ente (art. 33, V, "a"). Para recurso federal, são **3 anos**; a associação tem CNPJ desde 1987. Os demais requisitos para entidade privada receber transferência (cadastro, vedações, contrapartida) vêm da **LDO do exercício**. Em 02/10, a LDO 2027 (PLN 2/2026) ainda aguardava despacho. O motor acompanha o tema pelos comunicados da CMO; a regra só entra no Farol quando a lei for publicada.

## 5. Parametrização (`config/congresso_nacional.json`)

| Fonte | O que lê | Janela |
|---|---|---|
| A — CMO | página da LOA do ano seguinte (situação e datas da apresentação de emendas, PLN e situação do projeto) e comunicados | comunicados dos últimos 60 dias |
| B — Câmara | `/proposicoes?keywords=` com 7 expressões: sem fins lucrativos, sociedade civil, terceiro setor, termo de fomento, emendas parlamentares, entidades beneficentes, associação de moradores | 60 dias |
| C — Senado | `/processo?termo=` com 5 expressões | 60 dias |
| D — notícias | RSS da Câmara e do Senado | 15 dias |
| E — convocações | lista do Senado (só a linha de cada convocação) | 400 dias |

A "utilidade pública" ficou fora da busca: a utilidade pública federal foi extinta pela Lei 13.204/2015. A agenda é diária às 20:53 na nuvem (o agendador dispara nos minutos :23 e :53); na janela de emendas a leitura diária não pode falhar. Os léxicos do painel e do livro estão em `config/rotas_motores.json` › `congresso-nacional` (camada 1, camada 2 e vetos).

## 6. Calibração com dados reais

| Conjunto | Resultado do motor | Conferência humana |
|---|---|---|
| 19 proposições da Câmara ("sem fins lucrativos", 01/06–02/10) | 13 ACOMPANHAR: 6 tributárias (IBS/CBS, REFIS, imunidade, PEC 15), 4 de recurso ou apoio (energia, água, FGTS, Rede Fé Solidária), 2 programas, 1 regra; 6 RUÍDO | 16 de 19 concordam. As divergências são mutualistas (PL 5086, PLP 230) e recuperação judicial (PL 2925): casos de fronteira |
| 4 proposições do Senado | PL 2465/2026 → "virou lei (Lei nº 15.486)"; PLP 263 → tributária; PL 5019 (dia nacional) e PLP 114 → ruído | 4 de 4 |
| 16 manchetes do RSS das duas Casas (01/10) | 16 RUÍDO | 16 de 16 |
| 6 comunicados da CMO | 5 ACOMPANHAR; 1 ruído (apresentações de audiência) | 6 de 6 |
| 5 convocações recentes do Senado | 5 RUÍDO | 5 de 5 |
| Página da LOA 2027 | `nao_iniciada`, PLN 24/2026, aguardando despacho → ACOMPANHAR "emendas a abrir", com a referência de valores | confere |

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — ministro(a) de corte superior, processualista.** Emenda não é direito da entidade. É ato político do parlamentar, executado pelo órgão, com impedimento técnico possível (CF, art. 166, § 13). O motor não pode dizer "oportunidade" para algo que depende de articulação. Tem razão a classificação: a OPORTUNIDADE só acende quando a CMO abre o prazo, e o motivo manda levar projeto e ofício ao gabinete. Não promete recurso.

**2. Pessimista — staff engineer de integração com sistemas de governo.** A página da LOA é HTML de portal (Liferay). A leitura de hoje foi por extrator, não pelo HTML bruto. Se a tabela de etapas mudar, o leitor devolve `desconhecido`. Defesa: `alerta_formato` e a categoria "emendas_formato", nunca o silêncio. A busca da Câmara também é frágil: "13.019" volta vazio, então expressões novas devem ser testadas antes de entrar no config.

**3. Levemente pessimista — doutrinador(a) de direito financeiro.** O valor de R$ 43 milhões por deputado é referência do projeto, não da lei, e metade vai obrigatoriamente para a saúde. A associação de bairro concorre com Santas Casas, APAEs e prefeituras. A LDO 2027 nem foi votada. Mostrar o valor é útil para dimensionar, não para prometer.

**4. Neutro — CTO de plataforma de dados legislativos, mediador.** O voto está na seção 8.

**5. Levemente otimista — advogado(a) pós-doutor(a) em terceiro setor.** O art. 29 da Lei 13.019 dispensa o chamamento quando o recurso vem de emenda. É a porta mais curta entre a associação e o recurso federal, e o motor passa a dizer **quando** ela abre. As regras tributárias (IBS/CBS, REFIS social) afetam o caixa da entidade já no próximo ano.

**6. Otimista — staff engineer de produto, foco em captação.** A janela oficial vira dado: a linha de emenda federal ganha a situação e o prazo da CMO no resumo e, quando há data, o marco "prazo de emendas na CMO". A janela de 01/10 a 30/11 continua como calendário de articulação com os gabinetes. A API do Senado diz quando o projeto **vira lei**: aviso antecipado do programa que vai existir.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.** Com as APIs abertas das duas Casas, o mesmo motor pode cruzar autoria × UF: quem da bancada de Goiás propõe o quê para entidades. Esse é o mapa de padrinhos para o ofício da associação. Com o SIGA Brasil, dá para ver as emendas já indicadas a entidades goianas.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor do Congresso v1, como motor regular de **insumo** ("emenda parlamentar federal e regras para entidades").

**Metas** (medidas a cada 30 dias em `estado/congresso_nacional.json` › `historico`):

| Indicador | Meta |
|---|---|
| Leituras com resposta da CMO e das duas APIs | ≥ 95% dos dias |
| Situação da etapa de emendas reconhecida | 100% das leituras (0 dias com `alerta_formato` sem tratamento) |
| Abertura da apresentação de emendas avisada | no dia da primeira leitura com a etapa "em andamento" |
| Concordância com a conferência humana nas proposições | ≥ 80% (calibração: 16 de 19 na Câmara, 4 de 4 no Senado) |
| Notícias, comunicados e convocações classificados corretamente | ≥ 95% (calibração: 27 de 27) |

**Mitigação de riscos:**

1. **Formato:** o leitor lê a LINHA da tabela cuja primeira célula é exatamente "Apresentação de emendas" (não "emendas ao Parecer Preliminar"), com as negações testadas antes ("não aberta", "não iniciada"). Etapa não reconhecida gera alerta e **não apaga** a última situação reconhecida.
2. **Fonte fora do ar:** uma fonte nunca derruba as outras. Na leitura parcial, o que tem data dentro dos 60 dias continua; oportunidade com prazo futuro continua sempre. Fora do ciclo (página da LOA ainda inexistente, de janeiro a julho), não há falha: o motor lê a LOA do ano corrente.
3. **Promessa indevida:** proposição nunca é OPORTUNIDADE; emenda só é OPORTUNIDADE com o prazo aberto na CMO.
4. **Injeção:** texto com injeção vai para a quarentena.
5. **PII:** o motor não grava dado pessoal além do que as APIs publicam sobre o ato (autoria parlamentar).

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/congresso_nacional.py` (novo) | leitor das Fontes A–E, classificação, estado da janela de emendas, alarmes e preservação do estado |
| `config/congresso_nacional.json` (novo) | rotas, expressões, janelas, referência do PLOA 2027 e ritmo |
| `config/sensores.json`, `src/sensores.py` | sensor `congresso-nacional` e despacho para o leitor |
| `config/rotas_motores.json`, `config/agenda_motores.json`, `config/finalidade_motores.json`, `src/finalidade_motores.py` | rotas verificadas, léxico, agenda diária e finalidade de insumo |
| `src/emendas.py` | a linha de emenda federal ganha `prazo_oficial_cmo` (situação e datas lidas na CMO, com aviso de leitura desatualizada), o texto no resumo e o marco do prazo |
| `src/auditoria_motores.py`, `scripts/descricao_motores.py`, `config/descricao_motores.json`, `docs/dados/descricao_motores.json` | textos do conselho, evolução gratuita e a descrição do motor no painel (só a entrada nova; as demais não foram regeradas) |
| `tests/test_motor_congresso_nacional.py` (novo) | 21 testes: etapa de emendas (não iniciada, não aberta, aberta, encerrada seguida de outra etapa, emendas ao Parecer Preliminar, uma data só, formato novo), comunicados (data de cada um, link com parâmetros), APIs, RSS, convocações (linha a linha), classificação e falsos positivos, quarentena, motor ponta a ponta, falha de uma fonte, formato novo que não apaga a janela, ano da LOA pelo mês e 404 fora do ciclo, retroativo, registro no sensor, prazo oficial na área de emendas |

## 10. Para o titular (02/10/2026)

| O quê | Situação | Por que importa |
|---|---|---|
| **Emendas ao PLOA 2027** (PLN 24/2026) | prazo de apresentação **ainda não aberto** (aguardando despacho para a CMO); votação prevista para 22/12 | Os parlamentares em exercício, inclusive os 17 deputados e os 3 senadores de Goiás, apresentam as emendas de 2027 **neste ano**, mesmo os que não se reelegerem no domingo (04/10). Projeto, plano de trabalho e ofício precisam estar prontos antes da abertura. |
| PLP 236/2026 e PLP 263/2026 — IBS/CBS das entidades sem fins lucrativos | em tramitação | Efeito no caixa da associação com a reforma tributária |
| PL 3088/2026 — REFIS social do terceiro setor | em tramitação | Regularização de débitos, se houver |
| PL 2983/2026 (créditos de energia) e PL 3505/2026 (tarifa social de água) | em tramitação | Redução de custo fixo da sede |
| Lei 15.486/2026 (ex-PL 2465) | sancionada | Crédito do FGTS para filantrópicas e instituições sem fins lucrativos prorrogado |
| PL 3527/2026 — altera a Lei 13.019 | em tramitação | Muda a regra das parcerias |

**Decisão do titular:** a posição do motor no painel. Pela regra de numeração (grupo legislativo, território nacional), ele entra logo depois do CNJ, por volta do nº 11. Para ficar ao lado dos motores 05 e 06, a posição 07 está fixada hoje para o motor estadual de Goiás; mudar exige a sua decisão.

## 11. Pendências e limites

1. A página da LOA e os comunicados foram lidos por extrator, não em HTML bruto (o navegador do titular não respondeu). O leitor é tolerante e avisa se não reconhecer a etapa. A primeira leitura real no GitHub confirma o formato.
2. O cronograma do Informativo traz "1º a 20/10", mas a extração do PDF não permite afirmar se é o período de audiências ou de emendas. Por isso o motor confia só na **etapa oficial** da página da LOA.
3. A página de notícias da Câmara respondeu 429 (limite de requisições). O motor usa o RSS, com pausa entre chamadas.
4. Próximo passo gratuito: ler o inteiro teor das proposições (a ementa não diz tudo) e o SIGA Brasil (emendas já indicadas a entidades de Goiás).

## 12. Revisão independente

Um revisor sem contexto prévio leu o código, os testes e este parecer. Os 17 testes da época estavam verdes; ele apontou 22 pontos. Correções aplicadas:

- **Leitor da etapa de emendas.** Antes, "Não aberta" virava "aberta" (falsa oportunidade); o trecho podia invadir a etapa seguinte; e "emendas ao Parecer Preliminar" era confundida com a etapa. Agora a leitura é pela linha da tabela, com as negações testadas primeiro.
- **Formato novo** não apaga a última situação reconhecida.
- **Ano da LOA** conforme o mês; o 404 fora do ciclo deixa de contar como falha.
- **Agenda** às 20:53: o agendador só dispara nos minutos :23 e :53.
- **Comunicados:** cada um com a sua data; o link com parâmetros do portal é aceito.
- **Convocações** lidas linha a linha: o texto de uma não contamina a seguinte.
- **Falsos positivos corrigidos:**
  - acordo de cooperação internacional;
  - "associação criminosa";
  - honraria para pessoa indicada por entidade.
- **Alertas novos:** formato da API do Senado e cobertura cortada (mais de 100 resultados).
- **Área de emendas:** passa a mostrar o prazo oficial, com aviso de leitura desatualizada.
- **Parecer:** inclusão do art. 33, V, "a", da Lei 13.019; "afasta o chamamento" (art. 29) no lugar de "dispensa"; indicadores refeitos.
- **Testes:** a docstring identifica os exemplos sintéticos.

Ficam para a versão 2:

- paginação da API da Câmara (hoje há alerta);
- feed Atom;
- leitura do inteiro teor;
- SIGA Brasil.
