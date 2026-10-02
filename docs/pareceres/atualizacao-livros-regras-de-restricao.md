# Atualização dos livros — léxico e regras de restrição em cada livro

**Versão:** 2026-10-02.2 · **Origem:** Parecer das 238 oportunidades não confirmadas — validação item a item em 02/10/2026 (v2: território vira enquadramento; léxico e restrições em cada livro)

## A regra do livro (alterada pelo titular em 02/10/2026)

Cada livro da Biblioteca carrega, junto com o LÉXICO que busca a sua oportunidade, as RESTRIÇÕES que se aplicam a ela (bloco `busca` gravado no livro a cada ciclo por src/livros_regra.aplicar_motores). Este arquivo é o catálogo-mãe: os livros e os motores atualizam o JSON, não o código. Uma regra nunca se volta contra o próprio livro (fica em `suspensas` e vai à curadoria).

Antes (versão 2026-10-02.1) as restrições eram um filtro único, aplicado de fora, e o território descartava: edital de OSC de outro município virava DISPENSÁVEL. Agora:

1. **Território não descarta.** Edital de OSC de outro município ou estado é oportunidade para OSC, é coletado pelo PNCP (motor 04, Brasil inteiro desde 02/10) e **compõe um livro próprio**. O território vai para o livro como *enquadramento* (EN-01) — quem decide se a associação pode concorrer é o Farol (fase 2), por associação.
2. **Cada livro carrega o seu bloco `busca`**, gravado e atualizado a cada ciclo dos livros (`src/livros_regra.aplicar_motores` → `src/regras_restricao.aplicar_aos_livros`):
   - `lexico` — termos distintivos da oportunidade, frases (nome e número do edital), município, UF e a **consulta ao PNCP** (`pncp.consulta`) com a chave PNCP quando já localizada (`pncp.chave`);
   - `restricoes` — os códigos que valem para aquele livro, cada um com o seu **efeito** (abaixo); os padrões de texto de cada código ficam no catálogo-mãe `config/regras_restricao_livros.json`, na versão gravada no livro (`versao_regras`) — assim o livro diz *o que vale para ele* e o catálogo guarda *como reconhecer*, sem repetir os mesmos padrões em mil livros;
   - `suspensas` e `revisao_curadoria` — regra que se voltaria contra o próprio livro (ex.: livro de prêmio não veta "prêmio"); fica suspensa e vai à curadoria;
   - `aptidao` — situação da associação de referência (apta / restrita, com os motivos). Não exclui o livro.
3. **O achado é julgado pelas restrições do livro a que pertence** (`julgar_no_livro`): veto (não entra), edição (errata, retificação, prorrogação, resultado), junção (mesma chave PNCP) ou aceita (informação nova do livro). Achado novo com veto não vira livro e fica anotado em `vetados_pelas_restricoes` do catálogo — nada se perde.
4. **O léxico do livro trabalha na busca:** o sensor usa o léxico do livro (`sensores.lexico_especifico`), o prompt da IA do livro leva léxico, vetos e enquadramento (`opressores.prompt_para_fonte`) e a **Fonte C do PNCP** procura, com a consulta de cada livro, o ato no PNCP dos livros que ainda não têm chave (`config/pncp_osc.json › fonte_c`).

## Efeitos de cada restrição no livro

| Efeito | O que acontece |
|---|---|
| `veto` | não vira livro nem edição (NÃO APLICA) |
| `estado` | o livro continua, no histórico, com o prazo encerrado |
| `edicao` | ato acessório (errata, retificação, prorrogação, resultado) entra como edição do livro do edital |
| `juntar` | mesma chave PNCP = mesmo livro |
| `pendente` | fonte espelho/agregador: o livro aguarda o ato oficial (PNCP/site do órgão) |
| `enquadramento` | anotado no livro, NÃO descarta: território, região ou serviço especializado — quem decide é o Farol (fase 2), por associação |

## Catálogo-mãe das regras

| Código | Antes | Veredito | Efeito no livro | Regra | Itens na validação |
|---|---|---|---|---|---:|
| NA-01 |  | NÃO APLICA | veto | Ato do diário oficial que não é chamamento | 1 |
| NA-02 |  | NÃO APLICA | veto | Licitação, contratação de fornecedor ou serviço | 13 |
| NA-03 |  | NÃO APLICA | veto | Recursos humanos (concurso, seleção, estágio, aprendizagem) | 2 |
| NA-04 |  | NÃO APLICA | veto | Página genérica, agregador, notícia ou link sem edital | 3 |
| NA-05 |  | NÃO APLICA | veto | Concurso ou prêmio sem fomento a OSC | 7 |
| NA-06 |  | NÃO APLICA | veto | Público-alvo incompatível com a associação | 49 |
| NA-07 |  | NÃO APLICA | veto | Conselho, eleição ou representação (sem recurso) | 2 |
| NA-08 |  | NÃO APLICA | veto | Residência artística ou programa de artista individual no exterior | 3 |
| DI-03 |  | DISPENSÁVEL | estado | Prazo encerrado, revogado ou suspenso | 3 |
| DI-04 |  | DISPENSÁVEL | edicao | Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado | 13 |
| DI-05 |  | DISPENSÁVEL | pendente | Não verificável — sem fonte oficial confirmada | 32 |
| DI-08 |  | DISPENSÁVEL | juntar | Duplicata de outro registro da lista | 9 |
| EN-01 | DI-01 | APLICÁVEL | enquadramento | Edital de OSC de outro município/estado — livro próprio (enquadramento territorial) | 94 |
| EN-02 | DI-02 | APLICÁVEL | enquadramento | Edital de OSC com região restrita — livro próprio (enquadramento regional) | 1 |
| EN-03 | DI-06 | APLICÁVEL | enquadramento | Edital de OSC para serviço ou público especializado — livro próprio (enquadramento técnico) | 2 |

### Padrões (texto normalizado, sem acento)

**NA-01 — Ato do diário oficial que não é chamamento**

- Padrões: `credito (adicional|suplementar)`; `abertura de credito`; `dotacao orcamentaria`; `projeto de lei`; `prorrogacao do plano municipal`; `provimento de empregos`; `vencimentos e vantagens`
- Exceções (anulam o padrão comum): `^diario oficial de`; `termo de (colaboracao|fomento)`; `chamamento publico n`

**NA-02 — Licitação, contratação de fornecedor ou serviço**

- Padrões: `pregao`; `registro de precos`; `contratacao de empresa`; `aquisicao de`; `fornecimento de`; `prestacao de servicos de captacao`; `servicos de captacao de recursos`; `terceiro facilitador`; `captacao de recursos vinculados`; `contratacao de prestador`; `prestador de servicos`; `produtor(a)? (executivo|cultural)`; `estudo de impacto`; `permuta`; `imoveis ociosos`; `recrutar .*aprendiz`; `poder concedente`
- Exceções (anulam o padrão comum): `termo de (colaboracao|fomento)`; `organizacoes? da sociedade civil`; `\boscs?\b`; `entidades? sem fins`; `associacoes?`; `fundacoes?`
- Modalidade PNCP: `pregao|dispensa|inexigibilidade|concorrencia`

**NA-03 — Recursos humanos (concurso, seleção, estágio, aprendizagem)**

- Padrões: `estagi`; `jovens? aprendiz`; `programa de aprendizagem`; `processo seletivo`; `concurso publico`; `selecao de diretores`
- Exceções (anulam o padrão comum): `^diario oficial de`; `organizacoes? da sociedade civil`; `\boscs?\b`; `propostas`; `projetos`

**NA-04 — Página genérica, agregador, notícia ou link sem edital**

- Padrões: `cria fundo para`

**NA-05 — Concurso ou prêmio sem fomento a OSC**

- Padrões: `gincana`; `concurso de artigos`; `premio de boas praticas`; `premio de comunicacao`; `concurso parlamento`; `premio mdhc|premio .*servidor|concurso premio`
- Modalidade PNCP: `^concurso`

**NA-06 — Público-alvo incompatível com a associação**

- Fortes (sem exceção): `catadores?`; `coleta seletiva`; `materiais reciclaveis`; `oleo vegetal`; `longa permanencia`; `\bilpis?\b`; `cooperativas? de credito`; `associacoes? estudantis`; `associacao de estudantes`; `fapeg`; `instituicoes de ensino superior`; `produtora brasileira independente`; `fundo setorial do audiovisual|longa metragem`
- Padrões: `pesquisador`; `negocios de impacto`; `credenciamento de artistas`; `contratacao de artistas`; `propostas artisticas`; `artistas,? grupos`; `premiacao`; `premio cultural`; `\bmestres?\b`; `bolsas? (culturais|de intercambio)`; `apresentacao musical`; `facilitadores?,? profissionais`; `articuladores`
- Exceções (anulam o padrão comum): `organizacoes? da sociedade civil`; `\boscs?\b`; `entidades? sem fins`; `associacoes?`

**NA-07 — Conselho, eleição ou representação (sem recurso)**

- Padrões: `representantes da sociedade civil`; `eleicao de organiza`; `eleicao de entidades`

**NA-08 — Residência artística ou programa de artista individual no exterior**

- Padrões: `residencia (artistica|em|institut)`; `residency`; `delfina|braunschweig|institut francais|transartists`

**DI-04 — Ato acessório (errata, retificação, prorrogação, resultado) de edital já registrado**

- Padrões: `\berrata\b`; `retificacao`; `prorrogacao (das|do|de) (inscri|prazo|cronograma)`; `alteracao de cronograma`; `comunicado do edital`; `\bdespacho\b`; `reabertura de prazo`; `republicad`
- Exceções (anulam o padrão comum): `fluxo continuo`

**DI-05 — Não verificável — sem fonte oficial confirmada**

- Padrões: `guia de (captacao|permuta)`; `guia completo`; `captacao e regras`; `captacao e inscri`; `^edital [^:]{3,80} 20\d\d: `
- Domínios espelho/agregador: licitario.com.br, buscarlicitacao.com.br, capitaai.com.br, prefeituras.org, farolcultural.art, x.gov.br

**EN-02 — Edital de OSC com região restrita — livro próprio (enquadramento regional)**

- Padrões: `norte e nordeste`; `nordeste do brasil`; `do nordeste\b`; `periferias fortes`
- Exceções (anulam o padrão comum): `centro-oeste`; `goias`

**EN-03 — Edital de OSC para serviço ou público especializado — livro próprio (enquadramento técnico)**

- Padrões: `acolhimento institucional`; `organizacao social de saude|\boss\b`; `sistema socioeducativo`; `medidas? socioeducativ`; `atendimento socioeducativo`; `pronto atendimento`; `ambulatorial|hospitalar`; `reabilitacao intelectual`; `comunidade terapeutica`; `assistencia a saude`; `escola de musica`; `abrigo transitorio`

EN-01 (território) usa o perfil da entidade: municípios `goiania`, `jardim america`; UF `GO`. Município citado no título nunca é "nacional". DI-03 (prazo): situação revogada/suspensa/cancelada ou prazo anterior à data-base — o livro continua, no histórico. DI-08 (duplicata): chave PNCP cnpj/ano/seq. **Mudanças de 02/10 (v2):** DI-01 → EN-01, DI-02 → EN-02, DI-06 → EN-03 (enquadramento); catadores, ILPI e associações estudantis continuam NA-06 (requisito de natureza jurídica; proposta ao titular); Querido Diário deixou de ser "fonte indireta" (texto extraído por terceiro com link ao arquivo oficial do diário: fonte indicativa, a confirmar no arquivo oficial); a modalidade do PNCP cede às exceções de OSC; `oscs?` nas exceções.

## Exemplo — o bloco `busca` de um livro (simulação no catálogo de 02/10)

Livro `op-785cd7b1785d` — Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Circulação e Intercâmbio de Grupos (rótulo ES - Geral · Chamamento público):

```json
{
 "versao_regras": "2026-10-02.2",
 "atualizado_em": "2026-10-02",
 "lexico": {
  "termos": [
   "pavao",
   "circulacao",
   "intercambio",
   "grupos"
  ],
  "frases": [
   "Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - Circulação e Intercâmbio de Grupos",
   "edital 1/2026"
  ],
  "numeros": [
   "1/2026"
  ],
  "municipio": "vila pavao",
  "uf": "ES",
  "proprio": [],
  "pncp": {
   "chave": null,
   "consulta": "vila pavao circulacao",
   "ufs": "ES"
  }
 },
 "restricoes": [
  {
   "id": "NA-01",
   "efeito": "veto"
  },
  {
   "id": "NA-02",
   "efeito": "veto"
  },
  {
   "id": "NA-03",
   "efeito": "veto"
  },
  {
   "id": "NA-04",
   "efeito": "veto"
  },
  {
   "id": "NA-05",
   "efeito": "veto"
  },
  {
   "id": "NA-06",
   "efeito": "veto"
  },
  {
   "id": "NA-07",
   "efeito": "veto"
  },
  {
   "id": "NA-08",
   "efeito": "veto"
  },
  {
   "id": "DI-03",
   "efeito": "estado",
   "ultimo_fim": null
  },
  {
   "id": "DI-04",
   "efeito": "edicao"
  },
  {
   "id": "DI-08",
   "efeito": "juntar",
   "chave": null,
   "pagina": "https://mapa.cultura.es.gov.br/oportunidade/2605/"
  },
  {
   "id": "EN-01",
   "efeito": "enquadramento",
   "motivo": "livro do município Vila Pavao/ES: costuma exigir sede ou atuação local"
  }
 ],
 "suspensas": [],
 "revisao_curadoria": [],
 "aptidao": {
  "associacao": "amc-jardim-america",
  "situacao": "restrita",
  "motivos": [
   "livro do município Vila Pavao/ES: costuma exigir sede ou atuação local"
  ],
  "nota": "enquadramento não exclui o livro: a fase 2 (Farol) decide por associação"
 }
}
```

## Regras de coleta (defeitos dos motores)

- **RC-01** — Registro com município no título não pode receber 'sem restrição geográfica — vale para todo o Brasil'; o território é o do município. _(Por quê: 39 registros caíram no balde 'nacional' do painel (__nac__) sem serem nacionais.)_
- **RC-02** — Em registros de 'menção em diário oficial', o campo objeto não é confiável (vem de outro trecho da edição): só valer após ler o ato que cita o chamamento. _(Por quê: Valinhos, Iracemápolis, Andradina, Arapongas e outros: objeto = crédito, concurso ou plano, enquanto o ato validado era chamamento.)_
- **RC-03** — link_oficial não pode ser agregador, home, diário de outra cidade ou documento de outro município; quando for, o registro fica sem fonte oficial (DI-05). _(Por quê: Itapeva/SP→itapeva.mg.gov.br; Pinhais/PR→catalao.go.gov.br; Valparaíso/SP→campoflorido.mg.gov.br; PNAB→concurso público.)_
- **RC-04** — Data de vigência de credenciamento (ex.: 2030, 2031) não é prazo de inscrição; usar a abertura/encerramento de propostas do PNCP e marcar 'credenciamento permanente' quando for o caso. _(Por quê: Artur Nogueira/SP 2030, Telêmaco Borba/PR 2030, São Pedro do Sul/RS 2031.)_
- **RC-05** — Registro cuja fonte é um link fictício ou placeholder (ex.: x.gov.br/edital) vai para quarentena, não para a lista de abertas. _(Por quê: Item 101 'Seleção de OSC' sem edital real.)_
- **RC-06** — Mesma oportunidade em mais de um registro (PNCP + diário + Interceptador) conta uma vez: o código junta pela chave PNCP cnpj/ano/seq; título+município só com leitura humana (o mesmo diário traz editais diferentes). _(Por quê: 9 duplicatas entre as 238.)_
- **RC-07** — Edital de OSC de outro município ou estado NÃO é descartado: o PNCP o agrega e ele compõe um livro próprio; o território vai ao livro como enquadramento (EN-01). _(Por quê: Titular, 02/10/2026: 115 editais de OSC de outros territórios estavam como DISPENSÁVEL.)_
- **RC-08** — Livro sem chave PNCP é procurado no PNCP com a consulta do próprio livro (Fonte C); não achado, o livro continua com a fonte oficial do órgão (diário/site) e é procurado de novo em 7 dias. _(Por quê: 02/10: 58 registros sem link PNCP buscados no PNCP por município e tema — nenhum localizado (a Lei 13.019/2014 manda publicar o chamamento no sítio do órgão; o PNCP não é obrigatório para MROSC).)_

## Efeito medido (simulação sobre uma cópia do catálogo de 02/10, sem gravar no repositório)

- Achado novo vetado fica em `vetados_pelas_restricoes` (uma vez por endereço e regra); errata/resultado sem o livro do edital fica em `pendentes_das_restricoes`; texto com injeção vai a `vetados` como `quarentena` e nunca chega ao prompt.
- A Fonte C só grava a chave PNCP no livro quando o ato do mesmo município é de OSC/fomento, tem o mesmo número do edital do livro (ou, sem número, dois termos distintivos do livro) e passa no classificador do motor 04.
- Livros: 1033 → **1067** (34 novos do parecer; os demais do parecer já existiam e receberam léxico, restrições e checklist). Livros do parecer marcados com a exceção de abrangência: 104 (nenhum arquivado pela curadoria).
- Todos os 1067 livros receberam o bloco `busca`; 420 ficam *restritos* para a associação (enquadramento), sem sair da Biblioteca; 123 têm regra suspensa (o próprio livro casa um veto) e vão à curadoria.
- RC-01 também nos livros: livros municipais do PNCP marcados como "BR" (nacional) caíram de 103 para 62 — a UF do PNCP passa ao livro no ciclo.
- Tamanho do catálogo: 4.31 MB → 4.86 MB.

## Validação das regras

- Concordância de classe com a validação humana (v2): **84.0%** — APLICÁVEL->APLICÁVEL: 97; APLICÁVEL->DISPENSÁVEL: 2; APLICÁVEL->NÃO APLICA: 2; DISPENSÁVEL->APLICÁVEL: 28; DISPENSÁVEL->DISPENSÁVEL: 27; DISPENSÁVEL->NÃO APLICA: 2; NÃO APLICA->APLICÁVEL: 3; NÃO APLICA->DISPENSÁVEL: 1; NÃO APLICA->NÃO APLICA: 76.
- As regras reproduzem a classe do veredito humano em 84% dos 238 registros (v2: território e especialidade viram enquadramento; a fonte só em agregador aguarda o ato oficial). As divergências são registros que só a leitura do ato/da página resolve (objeto mal extraído, link de outro município, vigência tomada por prazo) — a regra reduz o funil e organiza o livro, mas não substitui a verificação dos 12 itens.
- **Ressalva:** calibradas no mesmo conjunto de 238 — ajuste, não validação independente; a generalização será medida no próximo ciclo.
- Testes: `tests/test_regras_restricao.py` (32 testes: regras, bloco do livro, regra que não se volta contra o livro, julgamento no livro, idempotência, sensor e prompt com o léxico do livro, achado vetado, livro de outro município não arquivado, semente, Fonte C do PNCP).
