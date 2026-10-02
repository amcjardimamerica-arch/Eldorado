# Atualização dos livros — regras de restrição para as próximas pesquisas

**Versão:** 2026-10-02.1 · **Origem:** Parecer das 238 oportunidades não confirmadas — validação item a item em 02/10/2026

## O que é

Conjunto de regras que reconhece, *antes* de virar "oportunidade aberta", os registros que não servem à associação. Cada regra tem código (NA = NÃO APLICA, DI = DISPENSÁVEL), padrões de texto sem acento, exceções, a evidência da validação das 238 oportunidades e o que fazer. Fonte única: `config/regras_restricao_livros.json`; leitura e aplicação em `src/regras_restricao.py` (biblioteca-padrão, testada em `tests/test_regras_restricao.py`).

## Como os livros e os motores usam

1. Para cada registro coletado: `avaliar(registro, perfil)` devolve `veredito`, `regra`, `regras`, `motivos`, `pendencias`, `revisao_humana` e `quarentena`. Em lote, `avaliar_lote(lista)` aplica também DI-08 (duplicata por chave PNCP); `links_suspeitos(lista)` acusa o mesmo link usado por municípios diferentes (RC-03).
2. **NÃO APLICA** e **DISPENSÁVEL** saem do funil de abertas; ficam arquivados com o código da regra (nunca apagados), para auditoria e reversão.
3. Se `revisao_humana` for verdadeiro (há veto, mas o território é Goiânia/GO ou nacional), o registro vai para conferência humana antes de arquivar — um veto automático nunca descarta sozinho algo que poderia ser da associação.
4. **APLICÁVEL** significa só "nenhuma restrição disparou": continua exigindo objeto, prazo e página oficial confirmados (campo `pendencias` lista o que falta).
5. `quarentena` verdadeiro = texto com padrão de injeção: vai para a quarentena do sistema, sem ser avaliado como oportunidade.
6. Ganho esperado (base: 238 registros): 234 deixam o radar (98%); as regras reproduzem a classe da validação humana em 92% dos casos e todos os aplicáveis; as divergências são casos de leitura do ato.

## Regras de restrição

| Código | Veredito | Regra | Tipo | Itens na validação |
|---|---|---|---|---:|
| NA-01 | NÃO APLICA | Ato do diário oficial que não é chamamento | padrao | 1 |
| NA-02 | NÃO APLICA | Licitação, contratação de fornecedor ou serviço | padrao | 12 |
| NA-03 | NÃO APLICA | Recursos humanos (concurso, seleção, estágio, aprendizagem) | padrao | 2 |
| NA-04 | NÃO APLICA | Página genérica, agregador, notícia ou link sem edital | padrao | 3 |
| NA-05 | NÃO APLICA | Concurso ou prêmio sem fomento a OSC | padrao | 7 |
| NA-06 | NÃO APLICA | Público-alvo incompatível com a associação | padrao | 49 |
| NA-07 | NÃO APLICA | Conselho, eleição ou representação (sem recurso) | padrao | 2 |
| NA-08 | NÃO APLICA | Residência artística ou programa de artista individual no exterior | padrao | 3 |
| DI-03 | DISPENSÁVEL | Prazo encerrado, revogado ou suspenso | prazo | 2 |
| DI-02 | DISPENSÁVEL | Região restrita do edital | padrao | 1 |
| DI-01 | DISPENSÁVEL | Território incompatível (fora de Goiânia/GO e sem abrangência nacional) | territorio | 115 |
| DI-04 | DISPENSÁVEL | Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado | padrao | 13 |
| DI-06 | DISPENSÁVEL | Serviço técnico especializado exige qualificação que o perfil não comprova | padrao | 2 |
| DI-05 | DISPENSÁVEL | Não verificável — sem fonte oficial confirmada | dominio | 13 |
| DI-08 | DISPENSÁVEL | Duplicata de outro registro da lista | duplicata | 9 |

### Padrões (texto normalizado, sem acento)

**NA-01 — Ato do diário oficial que não é chamamento**

- Padrões: `credito (adicional|suplementar)`; `abertura de credito`; `dotacao orcamentaria`; `projeto de lei`; `prorrogacao do plano municipal`; `provimento de empregos`; `vencimentos e vantagens`
- Exceções (anulam o padrão fraco): `^diario oficial de`; `termo de (colaboracao|fomento)`; `chamamento publico n`

**NA-02 — Licitação, contratação de fornecedor ou serviço**

- Padrões: `pregao`; `registro de precos`; `contratacao de empresa`; `aquisicao de`; `fornecimento de`; `prestacao de servicos de captacao`; `servicos de captacao de recursos`; `terceiro facilitador`; `captacao de recursos vinculados`; `contratacao de prestador`; `prestador de servicos`; `produtor(a)? (executivo|cultural)`; `estudo de impacto`; `permuta`; `imoveis ociosos`; `recrutar .*aprendiz`; `poder concedente`
- Exceções (anulam o padrão fraco): `termo de (colaboracao|fomento)`; `organizacoes? da sociedade civil`; `\bosc`; `entidades? sem fins`; `associacoes?`; `fundacoes?`
- Modalidade PNCP: `pregao|dispensa|inexigibilidade|concorrencia`

**NA-03 — Recursos humanos (concurso, seleção, estágio, aprendizagem)**

- Padrões: `estagi`; `jovens? aprendiz`; `programa de aprendizagem`; `processo seletivo`; `concurso publico`; `selecao de diretores`
- Exceções (anulam o padrão fraco): `^diario oficial de`; `organizacoes? da sociedade civil`; `\bosc\b`; `propostas`; `projetos`

**NA-04 — Página genérica, agregador, notícia ou link sem edital**

- Padrões: `cria fundo para`

**NA-05 — Concurso ou prêmio sem fomento a OSC**

- Padrões: `gincana`; `concurso de artigos`; `premio de boas praticas`; `premio de comunicacao`; `concurso parlamento`; `premio mdhc|premio .*servidor|concurso premio`
- Modalidade PNCP: `^concurso`

**NA-06 — Público-alvo incompatível com a associação**

- Fortes (sem exceção): `catadores?`; `coleta seletiva`; `materiais reciclaveis`; `oleo vegetal`; `longa permanencia`; `\bilpis?\b`; `cooperativas? de credito`; `associacoes? estudantis`; `associacao de estudantes`; `fapeg`; `pesquisador`; `instituicoes de ensino superior`; `negocios de impacto`; `produtora brasileira independente`; `fundo setorial do audiovisual|longa metragem`
- Padrões: `credenciamento de artistas`; `contratacao de artistas`; `propostas artisticas`; `artistas,? grupos`; `premiacao`; `premio cultural`; `\bmestres?\b`; `bolsas? (culturais|de intercambio)`; `apresentacao musical`; `facilitadores?,? profissionais`; `articuladores`
- Exceções (anulam o padrão fraco): `organizacoes? da sociedade civil`; `\bosc\b`; `entidades? sem fins`; `associacoes?`

**NA-07 — Conselho, eleição ou representação (sem recurso)**

- Padrões: `representantes da sociedade civil`; `eleicao de organiza`; `eleicao de entidades`

**NA-08 — Residência artística ou programa de artista individual no exterior**

- Padrões: `residencia (artistica|em|institut)`; `residency`; `delfina|braunschweig|institut francais|transartists`

**DI-02 — Região restrita do edital**

- Padrões: `norte e nordeste`; `nordeste do brasil`; `periferias fortes`
- Exceções (anulam o padrão fraco): `centro-oeste`; `goias`

**DI-04 — Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado**

- Padrões: `\berrata\b`; `retificacao`; `prorrogacao (das|do|de) (inscri|prazo|cronograma)`; `alteracao de cronograma`; `comunicado do edital`; `\bdespacho\b`; `reabertura de prazo`; `republicad`
- Exceções (anulam o padrão fraco): `fluxo continuo`

**DI-06 — Serviço técnico especializado exige qualificação que o perfil não comprova**

- Padrões: `acolhimento institucional`; `organizacao social de saude|\boss\b`; `sistema socioeducativo`; `medidas? socioeducativ`; `atendimento socioeducativo`; `pronto atendimento`; `ambulatorial|hospitalar`; `reabilitacao intelectual`; `comunidade terapeutica`; `assistencia a saude`; `escola de musica`; `abrigo transitorio`

**DI-05 — Não verificável — sem fonte oficial confirmada**

- Padrões: `guia de (captacao|permuta)`; `guia completo`; `captacao e regras`; `captacao e inscri`; `^edital [^:]{3,80} 20\d\d: `
- Domínios de fonte indireta: licitario.com.br, buscarlicitacao.com.br, capitaai.com.br, prefeituras.org, farolcultural.art, x.gov.br, queridodiario.ok.org.br

DI-01 (território) usa o perfil da entidade: municípios `goiania`, `jardim america`; UF `GO`. Município citado no título/objeto nunca é "nacional"; chamamento de outro município (inclusive goiano) é dispensável. DI-03 (prazo): situação revogada/suspensa/cancelada ou prazo anterior à data-base. DI-08 (duplicata): chave PNCP cnpj/ano/seq.

## Regras de coleta (defeitos dos motores)

- **RC-01** — Registro com município no título não pode receber 'sem restrição geográfica — vale para todo o Brasil'; o território é o do município. _(Por quê: 39 registros caíram no balde 'nacional' do painel (__nac__) sem serem nacionais.)_
- **RC-02** — Em registros de 'menção em diário oficial', o campo objeto não é confiável (vem de outro trecho da edição): só valer após ler o ato que cita o chamamento. _(Por quê: Valinhos, Iracemápolis, Andradina, Arapongas e outros: objeto = crédito, concurso ou plano, enquanto o ato validado era chamamento.)_
- **RC-03** — link_oficial não pode ser agregador, home, diário de outra cidade ou documento de outro município; quando for, o registro fica sem fonte oficial (DI-05). _(Por quê: Itapeva/SP→itapeva.mg.gov.br; Pinhais/PR→catalao.go.gov.br; Valparaíso/SP→campoflorido.mg.gov.br; PNAB→concurso público.)_
- **RC-04** — Data de vigência de credenciamento (ex.: 2030, 2031) não é prazo de inscrição; usar a abertura/encerramento de propostas do PNCP e marcar 'credenciamento permanente' quando for o caso. _(Por quê: Artur Nogueira/SP 2030, Telêmaco Borba/PR 2030, São Pedro do Sul/RS 2031.)_
- **RC-05** — Registro cuja fonte é um link fictício ou placeholder (ex.: x.gov.br/edital) vai para quarentena, não para a lista de abertas. _(Por quê: Item 101 'Seleção de OSC' sem edital real.)_
- **RC-06** — Mesma oportunidade em mais de um registro (PNCP + diário + Interceptador) conta uma vez: chave pncp cnpj/ano/seq ou título+município. _(Por quê: 9 duplicatas entre as 238.)_

## Validação das regras

- Concordância de classe com a validação humana: **92.0%** (matriz: DISPENSÁVEL->DISPENSÁVEL: 139; NÃO APLICA->DISPENSÁVEL: 1; NÃO APLICA->NÃO APLICA: 76; DISPENSÁVEL->NÃO APLICA: 5; DISPENSÁVEL->APLICÁVEL: 11; APLICÁVEL->APLICÁVEL: 4; NÃO APLICA->APLICÁVEL: 2).
- As regras reproduzem a classe do veredito humano em 92% dos 238 registros e confirmam os 6 aplicáveis; as divergências são registros que só a leitura do ato/da página resolve (objeto mal extraído, link de outro município) — por isso a regra reduz o funil mas não substitui a verificação dos 12 itens.
- **Ressalva:** calibradas no mesmo conjunto de 238; a generalização será medida no próximo ciclo (sugestão: guardar a decisão humana de cada novo registro e recalcular a concordância).

## Integração sugerida (não ligada ainda)

Chamar `avaliar_lote` em `src/fluxo_oportunidades.py` logo após a união das fontes e antes de contar "abertas" no painel; registrar a regra no arquivamento (`dados/editais/arquivados.json`). Não foi ligado nesta entrega para não alterar o painel sem aprovação.