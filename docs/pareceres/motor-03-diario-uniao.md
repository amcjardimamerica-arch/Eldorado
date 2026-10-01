# Parecer do conselho — Motor 03 · Diário Oficial da União

**Data:** 01/10/2026 · **Motor:** `dou` (Bússola, posição 03) · **Matéria:** técnica (engenharia de coleta), com reflexo jurídico (MROSC, PNAB, fundos e conselhos nacionais, Decreto 5.940/2006, aprendizagem)

## 1. Síntese

Em setembro de 2026, o DOU publicou **55.567 matérias** em 21 dias de edição. O motor 03 leu, no máximo, **9.600** delas (17,3%):

- a Seção 3 tem de 2,1 a 2,7 MB e o motor cortava toda página em 2,5 MB. Nos dias **02, 04, 11, 25 e 30/09** (e em 01/10) o bloco de matérias chegava pela metade, e o motor lia **zero**, com o servidor respondendo 200;
- nos outros dias, só as **600 primeiras** das cerca de 2.200 matérias da Seção 3;
- a **Seção 1** (resoluções de conselhos nacionais, portarias do MinC, MDS, MDHC) e as **edições extras** nunca foram lidas.

O pouco que entrou foi decidido pelo título, que no DOU é genérico. Os 14 registros que o motor gravou em setembro eram 9 extratos de parceria já celebrada, 4 editais de universidade e 1 edital de intimação. **Nenhum era seleção aberta para OSC.** O "prazo" gravado era a data de publicação.

No mesmo mês, o DOU publicou **23 seleções reais para OSC** que o motor deixou passar. **Catorze seguem abertas em 01/10/2026** (seção 10). Entre elas:

- o **Chamamento nº 3/2026 do IBAMA** (Fundo Rio Doce, até 22/10);
- o **Edital de Seleção nº 3/2026 da ANATER** (até 18/11);
- o **credenciamento de entidades de aprendizagem da Caixa**;
- **nove editais de prefeituras de Goiás que publicam no DOU**: Goiatuba, Itumbiara ×3, Orizona, Nova América, Planaltina, Nova Iguaçu de Goiás e, já em 01/10, Corumbá de Goiás.

**Decisão do neutro:** aprovar a versão 2. O motor passa a ler:

- a "Leitura do Jornal" **inteira** (DO1, DO3 e as extras que o próprio dia anuncia);
- a **íntegra** das matérias de interesse;
- a busca semanal, como reserva.

Cada ato é classificado pelo classificador comum dos motores 01 e 02 (`src/atos_diario.py`), com vetos e regimes próprios da esfera federal, sem IA e com o motivo escrito.

## 2. Resultado de setembro/2026 (motor antigo)

| Item | Número | Evidência |
|---|---|---|
| Dias com registro de execução | 30 de 30 | `estado/esquadra_diario.json` › `dou` |
| Dias pintados de azul ("funcionou sem oportunidade") | 22, incluindo os 5 dias em que a Seção 3 veio cortada | idem: `http: 200`, `achados: 0` |
| Matérias publicadas no DOU | 55.567 (DO1 8.189 · DO3 47.378) | Leitura do Jornal, lida com IP brasileiro em 01/10 |
| Matérias que o motor podia ler | no máximo 9.600 (17,3%) | 600 por dia × 16 dias não cortados |
| Seção 1 e edições extras lidas | 0 | `config/sensores.json` › `dou.urls` (só `secao=do3`) |
| Registros gravados na base | 14 | `dados/oportunidades/oportunidades.jsonl` › `fonte_id = dou` |
| Seleções abertas a OSC entre eles | **0** | 9 extratos, 4 editais de universidade (IFAL, UFU), 1 edital de intimação |
| "Prazo" gravado | a data de publicação, em 12 dos 14 | `prazo_texto` igual ao dia do DOU |
| Bloqueios registrados em `in.gov.br` | 328 (297 HTTPError na busca `exactDate=dia`) | `estado/bloqueios.json` |
| Diagnóstico de 01/10 no painel | "matérias do DOU lidas: 0" com a página respondendo 200 (2.441.707 bytes) | `estado/esquadra.json` › `dou.diagnostico` |

## 3. Defeitos encontrados

1. **D1 — Página cortada lida como vazia.** `_abrir` lê no máximo `bytes_por_pagina` = 2.500.000. A Seção 3 de 01/10 tem 2.587.686 bytes. O `<script id="params">` fica sem fechamento, e a expressão de reserva (`"jsonArray":[...]`) acha o `{"jsonArray":[]}` vazio do portlet de busca da mesma página. O resultado é 0 matérias, sem erro (`src/sensores.py`, bloco "DOU (leiturajornal)").
2. **D2 — 27% da Seção 3 nos dias bons.** O laço tem o limite `[:600]` de matérias por página.
3. **D3 — Só a Seção 3.** As resoluções do CONANDA, do CNAS e de outros conselhos, as portarias de edital e as edições extras saem na Seção 1 ou nas extras, que o motor não lia.
4. **D4 — Decisão pelo título.** "EXTRATO DE TERMO DE FOMENTO" passa no léxico da camada 1 ("termo de fomento") e vira candidato. O título nada diz sobre ser seleção aberta.
5. **D5 — Prazo falso.** `_FIM` procura a primeira data do contexto. No DOU, essa data é a de publicação.
6. **D6 — Busca na rota errada.** `exactDate=dia` foi tentada a cada leitura, e da nuvem deu HTTPError 297 vezes. A descoberta seguia links institucionais ("Destaques do DOU", "Leitura do Jornal" sem data).
7. **D7 — Território ignorado.** O DOU publica atos de prefeituras de todo o país: 7.141 matérias de prefeituras e governos de outros estados em setembro. As de Goiás, que são as que interessam, ficavam no mesmo saco.
8. **D8 — Painel e auditoria otimistas.** O cartão dizia "ativo — captando · 28 edital(is)", e a auditoria dizia "manter; validar por 7 dias se o JSON volta a trazer matérias". Em 01/10 o JSON não trouxe nenhuma, porque a página veio cortada, não porque o seletor mudou.

## 4. Rotas (Etapa 2)

Testes feitos com IP brasileiro pelo navegador do titular em 01/10/2026. Na nuvem do GitHub, a Leitura do Jornal já respondia 200 (é a mesma rota da versão antiga). Neste ambiente de análise, `in.gov.br` é barrado pela política de rede.

| Rota | IP brasileiro | O que entrega | Decisão |
|---|---|---|---|
| `in.gov.br/leiturajornal?data=DD-MM-AAAA&secao=do3` | 200 · 2,1–2,7 MB | `<script id="params">` com todas as matérias do dia (tipo, órgão, página, trecho de ~400 caracteres, `urlTitle`) | **usar** (Fonte A), lida inteira |
| `…&secao=do1` | 200 · ~450 KB | atos normativos: resoluções de conselho, portarias | **usar** (Fonte A) |
| `…&secao=do1e`, `do3e` | 200 quando `typeNormDay` anuncia | edições extras do dia | **usar** só quando anunciadas |
| `…&secao=do2` | 200 · ~1,4 MB | atos de pessoal | **descartar** |
| `in.gov.br/web/dou/-/{urlTitle}` | 200 · ~80 KB | íntegra da matéria (`texto-dou`), com órgão, seção e página | **usar** só nas matérias de interesse |
| `in.gov.br/consulta/-/buscar/dou?…&exactDate=semana` | 200 · 20 resultados | busca com o mesmo formato de matéria | **reserva** (Fonte B) |
| `…&exactDate=personalizado&publishFrom=…` | 200, mas vazia | — | **descartar** |
| `gov.br/cultura/…/editais`, `gov.br/mds/…`, `gov.br/participamaisbrasil/` | não testadas como fonte | os editais desses ministérios saem no DOU e são lidos lá | **descartar** |

## 5. Parametrização antes × depois

| Item | Antes | Agora |
|---|---|---|
| Seções | DO3 | DO1 + DO3 + extras anunciadas no dia |
| Limite da página | 2,5 MB (corta em silêncio) | 12 MB, com erro descrito acima disso |
| Matérias por página | 600 | todas |
| O que decide | rótulo (título) no léxico | tipo da matéria, órgão e território → íntegra → classificador comum |
| Filtro de leitura | — | 28.643 cortadas pelo tipo (licitação, contrato, aditivo, intimação…), 7.141 por território, 641 de conselhos profissionais |
| Íntegra | nunca | matérias de interesse que não são extrato (até 160 por dia) |
| Ato dentro da matéria | — | uma matéria com dois avisos vira dois atos (Mozarlândia, 18/09: aviso PNAB + aviso de licitação) |
| Vetos federais | — | seleção acadêmica e militar, bolsas, órgão pedindo apoio, imóvel, intimação, empresas e prestadores, pesquisa contratada, seleção de famílias, consulta pública, incubação de empresas |
| Regimes federais | — | doação de bens, coleta seletiva solidária (Decreto 5.940), aprendizagem com entidade sem fins lucrativos, clubes esportivos, patrocínio de estatal, cultura, esporte e saúde incentivados, fundos nacionais (FNCA, FNI, FDD, FNMA, FNAS) |
| Território | BR para tudo | prefeituras de Goiás = `GO/<município>`; outros estados ficam fora; unidade regional federal de outro estado vira ruído; doação e coleta só valem em Goiás ou no DF |
| Prazo | primeira data do contexto | período de inscrição, "até", "data final", "sessão de abertura", e o "leia-se" da retificação |
| Mesmo edital em várias matérias | registros separados | chave pela hierarquia do órgão + número; retificação atualiza o prazo; resultado fecha |
| Dia útil sem edição lida | azul | falha (vermelho) e alarme com 2 dias úteis seguidos; antes das 8h não conta |
| Agenda | 05:53, 06:23 e 19:23 | mantida; a janela de 3 dias recupera um dia perdido e a passagem das 19:23 pega as extras |

## 6. Calibração com setembro/2026 (Etapa 4)

O código desta versão rodou, sem alteração, sobre o mês inteiro. Isso foi feito no navegador do titular, com IP brasileiro e Python no próprio navegador. Em seguida houve uma leitura de ponta a ponta, real, do dia 30/09 (um dos dias em que a Seção 3 vinha cortada).

| Medida | Número |
|---|---|
| Matérias no jornal (DO1 + DO3 + extras) | 55.567 |
| Cortadas pelo tipo da matéria | 28.643 |
| Prefeituras ou governos de outros estados | 7.141 |
| Conselhos profissionais | 641 |
| Sem termo de interesse | 16.496 |
| De interesse | 2.646, que viraram 2.674 atos depois do recorte |
| Atos lidos pela íntegra | 489 (os extratos se resolvem pelo trecho) |
| OPORTUNIDADE (como no dia da publicação) | **23** |
| ACOMPANHAR | 770 leituras, que dão 776 atos únicos. Desses, 726 são parcerias celebradas; 294 trazem valor, somando **R$ 123,1 milhões** |
| RUÍDO | 1.881 |
| Abertas em 01/10/2026 | **14 seleções** (mais Corumbá de Goiás, publicada em 01/10) |
| Ponta a ponta em 30/09 | 3 seções, 2.889 matérias e 27 íntegras. Achou ANATER 3/2026 e Corumbá de Goiás 3/2026, esta pela busca de reserva |

**Conferência manual:**

- **OPORTUNIDADE:** as 23 foram abertas e conferidas, e todas são seleções reais com OSC ou entidade sem fins lucrativos como público. Precisão de **23/23**. Ressalva: quatro são de coleta seletiva solidária (Correios ×2, Gráfica do Exército, ambos no DF) e só servem a associação de catadores.
- **ACOMPANHAR:** na primeira rodada, 8 de 12 sorteados estavam corretos. Os erros viraram regra, e na segunda rodada foram 10 de 12. Os 2 restantes são duvidosos, não errados: um resultado de "Edital nº 90004" de gerência de aquisições e uma portaria do MAPA. São itens de inteligência, de custo baixo.
- **RUÍDO:** 12 de 12 sorteados corretos, nas duas rodadas.

Todo erro achado virou regra e teste em `tests/test_motor03_diario_uniao.py` (33 testes):

- recomendação ou portaria que só menciona a seleção não é o edital;
- "atrair apoio de pessoas jurídicas" para evento de instituto federal é o órgão pedindo patrocínio, não oferecendo;
- doação de bens dos Correios da Paraíba é local e fica fora;
- credenciamento de serviços funerários pago por fundo municipal não é fomento;
- bolsa do IPEA sobre financiamento de OSC é bolsa, não edital;
- "alteração de representante de contemplado" é andamento;
- retificação "onde se lê 29/10, leia-se 22/10" muda o prazo do edital do IBAMA;
- unidades diferentes do Exército com "Chamamento nº 1/2026" não se fundem;
- o título da busca vem com marcação de destaque, que precisa ser limpa;
- "a partir do dia 01/10 ao dia 15/10 de 2026" é prazo.

## 7. Conselho de 7 lentes

Os conselheiros são arquétipos sorteados para esta análise, não pessoas reais.

**1. Extremamente pessimista — chief engineer de ingestão de dados públicos, especialista em truncamento silencioso.**
O defeito central não estava no léxico. Estava num número mágico: `read(2_500_000)`. Ele valia para todos os 31 motores, e nenhum diagnóstico avisava que a página tinha sido cortada. Quantos outros motores leem meia página e dizem "sem achados"? A versão 2 corrige o DOU, mas o limite geral continua em `config/sensores.json` › `limites`. Exijo que o corte vire erro descrito em `sensores._abrir` para todos os motores, não só neste.

**2. Pessimista — staff engineer de relevância, obcecado por falso positivo e falso negativo.**
A calibração é de um mês. As regras de veto nasceram de exemplos de setembro, e o DOU de outubro terá outros formatos. Riscos concretos:

- o veto "PROCESSO SELETIVO" cede quando o texto fala de OSC, mas "MESTRADO" e "DOCENTE" não cedem. Um edital de OSC para formação de professores pode cair como ruído;
- 8 das 23 oportunidades não tinham prazo no aviso ("conferir no edital"), e a regra dos 60 dias dá cobertura a elas, não garantia;
- "conferir se é em Goiás" fica no ACOMPANHAR quando o aviso não diz o local.

**3. Levemente pessimista — professor de engenharia de computação, especialista em sistemas distribuídos.**
São 160 íntegras por dia, com 0,3 s de pausa: até 50 s de leitura, mais 3 seções de até 2,7 MB. Está dentro do tempo do workflow, mas o `in.gov.br` já derrubou conexão de robô em 04/09 (`RemoteDisconnected`). Se a Imprensa Nacional endurecer o limite de taxa, o motor volta a ficar cego. O alarme de 2 dias úteis cobre a detecção, não a causa. O INLABS (XML oficial, cadastro gratuito) deve ser a segunda via.

**4. Neutro — CTO de plataforma pública de dados, mediador.** O voto está na seção 8.

**5. Levemente otimista — professor de ciência da computação, especialista em sistemas explicáveis.**
O DOU entrega metadados que os diários estadual e municipal não têm: tipo da matéria, hierarquia do órgão e página. O filtro usa isso antes de qualquer texto: só 489 das 55.567 matérias precisaram da íntegra. O classificador continua único para os três motores e explica cada decisão com uma frase que o titular, como advogado, audita sem ler código.

**6. Otimista — staff engineer de produto, foco em captação.**
O achado do mês: **prefeituras de Goiás publicam no DOU**. Goiatuba, Itumbiara, Orizona, Nova América, Planaltina, Nova Iguaçu de Goiás e Corumbá de Goiás apareceram aqui, várias delas também no Diário do Estado. É uma segunda fonte para os mesmos editais, e o motor 02 ganha confirmação cruzada. Os 726 extratos de parceria (R$ 123 milhões) mostram quais ministérios celebram com OSC e quanto: Esporte (407 extratos), MinC (116) e MDS (43). É o mapa de onde bater na próxima rodada.

**7. Extremamente otimista — CTO de big tech, pós-doutor em Python.**
A Leitura do Jornal aceita qualquer data. A mesma leitura serve à carga histórica de 5 anos do DOU, sem custo, dia a dia. Com ela, o sistema aprende o calendário federal (quando o CONANDA, o FNI e o FDD abrem) e avisa a associação antes da publicação. E a família "coleta seletiva solidária" (Decreto 5.940) revelou uma oportunidade permanente para associações de catadores em Goiás e no DF, que nenhuma plataforma agregadora lista.

## 8. Voto do neutro (vinculante)

**Decisão:** aprovar o motor 03 versão 2 e publicar, depois do PR do motor 02, porque o classificador comum mora lá.

**Metas (medidas a cada 30 dias em `estado/diario_uniao.json` › `historico`):**

| Indicador | Meta |
|---|---|
| Seções de dia útil lidas (DO1 e DO3) | ≥ 95% |
| Atraso entre publicação e leitura | ≤ 1 dia |
| Precisão de OPORTUNIDADE (conferida pelo titular) | ≥ 80% (setembro: 23/23) |
| Falhas com causa descrita | 100% |
| CPF gravado | 0 |

**Mitigação de riscos:**

1. **Página cortada:** limite próprio de 12 MB. Acima dele, erro descrito; nunca leitura pela metade.
2. **Taxa e bloqueio:** 3 tentativas com espera crescente. A busca é só reserva, e o alarme dispara com 2 dias úteis sem edição. A segunda via (INLABS) fica como pendência.
3. **Falso negativo dos vetos:** os vetos fortes (bolsa, concurso, imóvel, empresa) não cedem. Os fracos ("processo seletivo", consulta pública) cedem quando o texto fala de OSC. Cada RUÍDO traz o motivo, e o titular pode contestar.
4. **Prazo ausente:** sem prazo no aviso e com mais de 60 dias, o edital vai para ACOMPANHAR com o aviso de conferir. Trecho sem íntegra nunca vira OPORTUNIDADE.
5. **Território:** prefeitura de outro estado fica fora. Unidade regional federal de outro estado vira ruído. Doação e coleta só valem em Goiás ou no DF.
6. **Dado pessoal:** CPF vira `[CPF]` antes de gravar.
7. **Instrução escondida no texto:** a matéria suspeita vai para a quarentena.

## 9. Melhorias aplicadas

| Arquivo | O que mudou |
|---|---|
| `src/diario_uniao.py` (novo) | leitor do motor 03: Leitura do Jornal (DO1, DO3 e extras), filtro por tipo, órgão e território, íntegra, recorte de atos, vetos e regimes federais, prazo, deduplicação pela hierarquia, retificação, fechamento por resultado, alarme e diagnóstico por fonte |
| `src/atos_diario.py` | ganchos opcionais `vetos`, `regimes_extra` e `fundos`. Sem eles, o comportamento dos motores 01 e 02 não muda (os testes deles seguem verdes) |
| `src/sensores.py` | o `dou` passa ao novo leitor antes do laço genérico |
| `config/diario_uniao.json` (novo) | seções, extras, janela, limites, consultas da busca e a calibração de setembro |
| `config/sensores.json`, `config/rotas_motores.json`, `config/agenda_motores.json` | URLs DO1 e DO3, as rotas que o leitor de fato lê, a verificação nova e o texto da agenda |
| `src/auditoria_motores.py`, `scripts/descricao_motores.py` | textos do conselho e da evolução gratuita |
| `tests/test_motor03_diario_uniao.py` (novo) | 33 testes com trechos reais de setembro, jornal simulado, dia útil sem edição, segunda passagem do dia e quarentena |
| `tests/test_system.py` | o teste antigo do DOU (que baixava a edição real sem saber) passa a testar o leitor novo, sem rede |

**Testes:** a suíte completa tem as mesmas 40 falhas e 3 erros antes e depois da mudança, todos já existentes. São 927 testes; os 33 novos e o teste antigo reescrito estão verdes. `scripts/verificar_privacidade.py` não encontrou nenhuma credencial publicada.

**Revisão independente:** um revisor separado leu o código antes da entrega e achou 7 defeitos. Todos foram corrigidos, e cada um ganhou teste:

- o "leia-se" pegava a primeira data, não o prazo;
- o resultado não fechava o edital quando havia retificação no meio;
- duas aberturas sem número da mesma unidade, no mesmo dia, se fundiam;
- uma portaria com cabeçalho curto virava edital ao ser recortada;
- o histórico do dia zerava na segunda passagem;
- a Seção 3 com erro em dia útil pintava o dia de azul;
- a preposição "para" era lida como o estado do Pará.

## 10. Seleções abertas em 01/10/2026, para o titular decidir

| Publicação no DOU | Órgão | Edital | Prazo no texto | Matéria |
|---|---|---|---|---|
| 28/09 | Prefeitura de Nova Iguaçu de Goiás | Chamamento nº 1/2026: OSC para termo de fomento, crianças e adolescentes com TEA/TDAH | **02/10/2026** | `aviso-de-chamamento-publico-n-1/2026-734979095` |
| 09/09 | Prefeitura de Planaltina (GO) | Chamamento nº 6/2026: OSC para termo de colaboração, campeonatos municipais de futsal e society | **sessão em 09/10/2026** | `aviso-de-chamamento-publico-n-6/2026-730658650` |
| 25/09 | Prefeitura de Goiatuba | Chamamento nº 4/2026: PNAB ciclo 2, projetos culturais | **13/10/2026** | `aviso-de-chamamento-publico-n-4/2026-734365925` |
| 01/10 | Prefeitura de Corumbá de Goiás (Fundo Municipal de Cultura) | Chamamento nº 3/2026: PNAB, premiação de agentes culturais | **15/10/2026** | `aviso-de-chamamento-publico-n-3/2026-736008019` |
| 23/09 e 25/09 | IBAMA (MMA) | Chamamento nº 3/2026: OSC executora de recursos do Fundo Rio Doce | **22/10/2026** (retificado) | `aviso-do-chamamento-publico-n-3/2026-733656174` |
| 29/09 | Gráfica do Exército (Brasília-DF) | Chamamento nº 1/2026: associações de catadores (coleta seletiva solidária) | 09/11/2026 | `aviso-de-chamamento-publico-n-1/2026-735271941` |
| 30/09 | ANATER | Edital de Seleção Pública nº 3/2026: OSC para o projeto Coopera Rio + Doce | **18/11/2026** | `edital-de-selecao-publica-n-3/2026-735620989` |
| 11/09 | Prefeitura de Itumbiara | Chamadas nº 11, 12 e 13/2026: Pontos e Pontões de Cultura, projetos PNAB, ponto de cultura continuado | conferir no edital | `aviso-de-chamada-publica-n-11/2026-731158750` (e 12, 13) |
| 04/09 | Prefeitura de Orizona | Chamamento nº 1/2026: PNAB, projetos culturais | conferir no edital | `aviso-de-chamamento-publico-n-1/2026-730131834` |
| 21/09 | Prefeitura de Nova América | Chamamento nº 1/2026: PNAB, termo de execução cultural | conferir no edital | `aviso-de-chamamento-publico-n-1/2026-733091392` |
| 09/09 | Caixa Econômica Federal | Credenciamento nº 0001/2026: entidade sem fins lucrativos para o Programa de Aprendizagem | conferir no edital | `aviso-de-chamamento-publico-730557757` |
| 14 e 15/09 | Correios (Brasília-DF) | Seleção de associações de catadores (coleta seletiva solidária) | conferir no edital | `edital-de-chamamento-publico-731554631`, `edital-n-cp-01/2026-731661657` |

Endereço de cada matéria: `https://www.in.gov.br/web/dou/-/` + o identificador da última coluna.

Encerradas em setembro, que o motor antigo perdeu:

- **Aragarças** PNAB 1/2026 (até 10/09);
- **Campestre de Goiás** 1/2026 (até 15/09, retificado);
- **Morrinhos** PNAB (até 15/09);
- **Inhumas** PAA, seleção de entidades socioassistenciais para receber alimentos (14 a 18/09);
- **CBCP**, uniformes para clubes paralímpicos (até 16/09);
- **Senador Canedo** PNAB 1/2026 (até 25/09);
- **Mozarlândia** PNAB ciclo 2 (até 28/09);
- **Alvorada do Norte** 5 e 6/2026 (até 29/09).

## 11. Pendências

1. **Ordem de implantação:** o PR do motor 02 (nº 12) precisa ser mesclado antes, porque traz `src/atos_diario.py`.
2. **Primeira execução na nuvem:** confirmar no diagnóstico que as três seções chegam inteiras ao servidor do GitHub (`fontes.A.secoes_lidas` e `materias_no_jornal`).
3. **Limite de página dos outros motores** (lente 1): fazer o corte em `sensores._abrir` virar erro descrito para todos os motores. Muda a régua da esquadra inteira e precisa de decisão própria.
4. **Segunda via oficial:** o INLABS da Imprensa Nacional (XML integral, cadastro gratuito, com senha em GitHub Secrets).
5. **Transferegov como motor próprio:** programas federais abertos a propostas de OSC (discricionárias e emendas) não saem no DOU como edital.
6. **Registros antigos:** os 14 itens de setembro continuam na base. A revisão humana decide arquivá-los (`merge_registro` preserva o status).
7. **Painel:** mostrar os atos ACOMPANHAR e a contagem por seção no cartão do motor. Depende da identidade visual definitiva.
