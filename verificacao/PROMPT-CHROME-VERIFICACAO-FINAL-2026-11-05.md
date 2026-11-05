# Verificação final pelo Claude no Chrome — lote-2026-11-05-externa-final

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Finalizar todos os livros que ainda não têm a verificação externa, para o sistema seguir só com as oportunidades novas:

| O que | Livros |
|---|---|
| Na esteira do Cartório | 6 na recepção, 1 na preparação, 3 na verificação externa |
| Chegaram na semana (os 430 da chegada) e foram ao arquivo ou ao Farol pelas regras automáticas, sem o veredito do Chrome | 55 no arquivo, 8 no Farol |
| Documentos para o expurgo | 17 lotes, 1524 grupos (seção própria abaixo) |
| **Total de livros** | **73**, em 2 partes: `verificacao/lotes/lote-2026-11-05-externa-final-parte-1.json` e `-parte-2.json` |

Os demais livros que chegaram na semana já foram decididos (verificados pelo Chrome, expurgados ou unidos) e não
entram. Versão do lote: `gerado_em` = `2026-11-05T14:17:02+00:00`. A planilha `LISTA-LIVROS-VERIFICACAO-FINAL-2026-11-05.xlsx` tem os
73 livros, com as colunas do resultado para o controle.

Atenção: os livros que já estão no Farol ou no arquivo também recebem a decisão. Um `descartar` tira o livro do sistema
(expurgo), mesmo que ele esteja no Farol; um `valido` com prazo aberto o mantém (ou o leva) ao Farol.

## ENTREGA COMPLETA E TOTAL (R41) — obrigatória

1. Trabalhe UMA PARTE de cada vez. Antes de começar, conte os livros da parte (`total_livros`).
2. Entregue UM veredito decisivo para CADA livro da parte, num único arquivo por parte.
3. Copie do arquivo da parte o `lote` (ex.: `lote-2026-11-05-externa-final-parte-7`) e o `gerado_em` (no campo `lote_gerado_em`).
4. É proibido reduzir o escopo, escolher só uma parte dos livros, deixar livro como "pendente" ou "não verificado".
5. Se não conseguir terminar uma parte, não entregue essa parte: o sistema recusa por inteiro o veredito incompleto.

## As quatro decisões (use exatamente estas palavras)

| decisao | Quando | O que o sistema faz |
|---|---|---|
| `valido` | É oportunidade para o terceiro setor (OSC, associação, fundação), aberta, de fluxo contínuo ou permanente por lei | Grava os itens e as dispensas; com prazo aberto vai ao Farol; sem prazo aberto, ao arquivo. Não volta à fila. |
| `encerrada` | Oportunidade do terceiro setor com as inscrições encerradas (habilitação, resultado, edição anterior sem nova) | Fica no banco, no arquivo |
| `arquivar` | Oportunidade real do terceiro setor fora do perfil (edital privado ou federal restrito a outra região) | Fica no banco, no arquivo |
| `descartar` | NÃO é oportunidade para o terceiro setor | Expurgo: o livro sai do sistema |

Descarte (expurgo) é para: página institucional, menu, transparência ou notícia; notícia sem edital; anexo isolado,
áudio, formulário, errata, extrato, lista de classificados ou suplentes (o livro é o edital-mãe); licitação, pregão,
contrato, termo já celebrado, credenciamento de prestador, concurso público, compra do PNAE; chamada só para pessoa
física, empresa ou pesquisador; edital municipal de outro estado que não é capital; link quebrado sem edital-mãe.

## O catálogo das oportunidades conhecidas (R44)

Os livros `captacao-*` são a lista da titular das oportunidades mais conhecidas. Eles NUNCA saem do sistema (se você
decidir `descartar`, o sistema arquiva). Para cada um, use o campo `catalogo` do lote (programa, onde captar, valor de
referência, editais dos últimos 3 anos, fonte de verificação) e:

- ache o edital, a chamada ou a lei vigente e valide os 12 itens; programa permanente por lei (Rouanet, Goyazes, Lei do
  Esporte, fundos da criança e do idoso) é `valido`, com a lei e o chamamento como documento oficial;
- informe as datas de abertura das edições anteriores que achar (últimos 3 anos), no campo `edicoes_anteriores`: o
  sistema calcula com elas a previsão da próxima edição (a análise preditiva).

## Os 12 itens (os nomes exatos)

Objeto · Prazo de inscrição · Resultado · Prazo de recurso · Valor · Órgão / financiador · Território · Esfera ·
Requisitos · Anexos · Modalidade · Área de atuação

- Cada item comprovado leva o `trecho` copiado do documento oficial, a `pagina` (número inteiro, ou `null`) e a `url`.
- Persiga o edital oficial com todas as regras da oportunidade; no incentivo fiscal por lei, a lei e o chamamento são o
  documento oficial. Os valores e prazos vêm do documento oficial, nunca do replicador (CapitaAI, Observatório).
- O NÚCLEO nunca se dispensa: Objeto, Prazo de inscrição, Território.
- Os outros itens só se dispensam com justificativa de pelo menos 20 caracteres e uma destas expressões: "não se aplica",
  "não aplicável", "inaplicável", "não há recurso", "não há prazo de recurso", "sem seleção competitiva", "fluxo
  contínuo", "cadastro permanente", "não consta nos documentos oficiais lidos", "dispensado pelo …", "regime …".

## O formato do veredito de cada parte (JSON, exatamente assim; `itens` e `dispensas` são LISTAS)

```json
{
  "lote": "lote-2026-11-05-externa-final-parte-1",
  "lote_gerado_em": "2026-11-05T14:17:02+00:00",
  "total_livros": 50,
  "vereditos": [
    {
      "livro_id": "captacao-031",
      "decisao": "valido",
      "motivo": "por que esta decisão, em uma ou duas frases",
      "link_original": "https://… (o edital, a chamada ou a lei oficial)",
      "como_encontrou": "o caminho até o documento oficial",
      "itens": [{"item": "Objeto", "valor": "…", "trecho": "…", "pagina": 1, "url": "https://…"}],
      "dispensas": [{"item": "Prazo de recurso", "justificativa": "não há recurso previsto: cadastro permanente de projetos"}],
      "edicoes_anteriores": ["2024-03-10", "2025-03-15", "2026-03-12"],
      "aprendizado": "o que o motor deve fazer da próxima vez para achar este edital"
    }
  ]
}
```

Grave como `verificacao/vereditos/veredito-lote-2026-11-05-externa-final-parte-N.json` (uma por parte).

## O expurgo dos documentos (obrigatório nesta entrega)

Os 17 lotes de documentos do expurgo ainda não foram feitos em nenhuma entrega anterior. Eles fazem parte desta
verificação final: são 1524 grupos de documentos sem uso, nos arquivos `verificacao/expurgo/lote-chrome-documentos-*.json`.

Para cada arquivo, entregue um veredito completo (todos os grupos do arquivo; o sistema recusa o veredito incompleto),
com o `lote` copiado do arquivo, em `verificacao/expurgo/vereditos/veredito-<nome do arquivo>.json`:

```json
{"lote": "<o nome do arquivo do lote>", "vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar",
 "motivo": "…", "titulo": "…", "orgao": "…", "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD", "trecho": "…", "livro_id": "…"}]}
```

- `oportunidade`: o documento é um edital aberto que ainda não tem livro (o sistema cria o livro).
- `vincular`: o documento pertence a um livro que já existe (informe o `livro_id`).
- `descartar`: não é oportunidade (o documento sai do sistema).

Os arquivos:

- `lote-chrome-documentos-2026-11-02-auto.json` — 5 grupos
- `lote-chrome-documentos-2026-11-02-parte-01.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-02.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-03.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-04.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-05.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-06.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-07.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-08.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-09.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-10.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-11.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-12.json` — 100 grupos
- `lote-chrome-documentos-2026-11-02-parte-13.json` — 80 grupos
- `lote-chrome-documentos-2026-11-03-auto.json` — 28 grupos
- `lote-chrome-documentos-2026-11-04-auto.json` — 107 grupos
- `lote-chrome-documentos-2026-11-05-auto.json` — 104 grupos

## Ao terminar

Uma planilha de controle com o total de cada parte (entregue / não entregue) e os aprendizados que se repetiram. Nada
parcial: a parte que não foi verificada inteira não é entregue.

## A tabela dos 73 livros

| Parte | Nº | Livro | Título | Etapa | UF | Prazo | Estrela | Faltam | Por que está na lista |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | `L-58b97cfc36c67eb5` | DOE - PADRE BERNARDO - AVISO 002 - CHAMADA PÚBLICA- ALDIR BLANC | verificação externa | GO | sem prazo | sem | 7 | na esteira do Cartório |
| 1 | 2 | `L-a456d9bccbfc1a33` | DOE - PADRE BERNRDO - AVISO 003 - CHAMADA PÚBLICA- | verificação externa | GO | sem prazo | sem | 7 | na esteira do Cartório |
| 1 | 3 | `L-bd018693e6c2d79a` | DOE - BONOPOLIS - CREDENCIAMENTO 006-2026 | verificação externa | GO | sem prazo | sem | 9 | na esteira do Cartório |
| 1 | 4 | `L-97988670a73d9d1c` | Edital FAPESPA 2026: Mapeamento Turístico Ilha do CombuR$ 544 mil | recepção | PA | aberta | ouro | 1 | na esteira do Cartório |
| 1 | 5 | `op-583de98c37cc` | 2º Edital Social Instituto Porto 2026: até R$ 200 mil por OSC (2 vagas, Grande SP e Grande | recepção | MG | aberta | ouro | 0 | na esteira do Cartório |
| 1 | 6 | `op-cc360a72c619` | Projetos sustentáveis no Cerrado e na Caatinga — Brasil | recepção | MA | aberta | bronze | 1 | na esteira do Cartório |
| 1 | 7 | `op-2f2e856a2474` | Programa Nutrir+ — Brasil | recepção | MS | aberta | bronze | 2 | na esteira do Cartório |
| 1 | 8 | `op-bdda6f400ec9` | IFood Chega Junto – 2ª edição — Brasil | recepção | BA | aberta | bronze | 2 | na esteira do Cartório |
| 1 | 9 | `L-20ad275e2117b5d6` | Seleção de empreendimentos de saneamento 2026 – PCJ SPR$ 12,0 mi·até 16 de mai. de 2027 | recepção | SP | aberta | bronze | 3 | na esteira do Cartório |
| 1 | 10 | `L-27ce64e8a5a06860` | Amazonia Comunitaria (2026) / Granted AI | preparação | — | sem prazo | sem | 11 | na esteira do Cartório |
| 1 | 11 | `L-7c0a3321677b82f3` | AVISO DE PUBLICAÇÃO CHAMADA PUBLICA 03 -2026.docxDOE | Farol | GO | aberta | bronze | 1 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 12 | `L-3eec9433b1907a0c` | Plataforma Conjunta / Equatorial Goiás abre chamada de eficiência energética para OSCs com | Farol | GO | aberta | ouro | 0 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 13 | `L-71d7c6bc7446ed9d` | DOE - NOVA GLORIA - CHAMAMENTO_007-2026 | Farol | GO | aberta | bronze | 0 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 14 | `L-967c8afb34d4ab75` | Edital Comercialização de Longa‑Metragem – Goiás 2026R$ 250 mil·até 02 de dez. de 2026 | Farol | GO | aberta | prata | 1 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 15 | `L-418b736d9b4a4684` | Prêmio Melhores Práticas em Equilíbrio Trabalho-Família | arquivo | GO | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 16 | `L-4f841f73c83befdb` | Confira os selecionados pelo edital Fundos da Infância e da Adolescência | arquivo | GO | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 17 | `L-d82ce960cce2acf5` | W.K. Kellogg Foundation (2026) / Granted AI | arquivo | GO | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 18 | `L-734e8562eb9103ea` | Aava Santiago abre 4º edital participativo de emendas parlamentares com R$ 2,5 milhões par | arquivo | GO | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 19 | `L-af8eb6719e0da13d` | Instituto Porto lança 2º Edital de Verba Direta - Rede Filantropia | Farol | BR | aberta | bronze | 2 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 20 | `L-37806c421a6ae105` | Taquara abre chamamento público para projetos de esporte e cultura ... | Farol | BR | aberta | bronze | 1 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 21 | `L-3ae69a389aff8dcf` | Edital Chamamento Público Mogi Guaçu 01/SAS/2026R$ 477 mil·até 18 de nov. de 2026 | Farol | BR | aberta | bronze | 0 | chegou na semana e foi ao farol sem veredito do Chrome |
| 1 | 22 | `L-0e9e600a00d486d5` | Coca-Cola Femsa Brasil lança edital para fomentar ... | arquivo | BR | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 23 | `L-27eb17b403f46323` | Prosas / Edital - Chamada Pública para Projetos da Sociedade Civil de | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 24 | `L-a47457607ace2e17` | Projetos aptos à captação na LIE | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 25 | `L-dfee9b47629da8c4` | Guia de captação de recursos para organizações de catadores/as | arquivo | RS | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 26 | `L-5aeede4e12ea1dab` | Bolsa CAPES-Humboldt 2026: Guia Completo do Editalaté 01 de dez. de 2026 | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 27 | `L-2d47d8ab7a77f62e` | PDF De Organizações Da Sociedade Civil, Chamamento Público Para O Seleção ... | arquivo | BR | encerrada | sem | 1 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 28 | `L-68b29d68a79e37f5` | Fundo Brasil lança edital para fortalecer a proteção de defensores ... | arquivo | BR | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 29 | `L-c5240359ed3a9737` | Prêmio Educação para Gentileza e Generosidade 2026 Escolas | arquivo | BR | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 30 | `L-9d50bd2572982731` | Edital para parceria com OSC que atende crianças e adolescentes ... | arquivo | DF | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 31 | `L-a279cfc5066b0270` | Chamada Semeia Fundação Cargill 2026 | arquivo | BR | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 32 | `L-7c171b4ba1aceb02` | Instituto Lojas Renner abre edital de R$ 1 milhão para impulsionar ... | arquivo | BR | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 33 | `L-c165ffa512b7bdd7` | Fundo de Empoderamento Comunitário do Brasil apoia projetos locais de sustentabilidade e N | arquivo | BR | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 34 | `L-750cff5410ffeb7f` | PDF REGRAS DA CONVOCAÇÃO 2026 - fundacionmapfre.com.br | arquivo | BR | encerrada | sem | 0 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 35 | `L-f5424de9985fcf01` | Plataforma MROSC lança edital que apoia projetos de fortalecimento da ... | arquivo | BR | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 36 | `L-355e2bd2324ed15c` | Edital De Chamamento Público Minc Nº 2, De 30 De Abril De 2026 | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 37 | `L-1f656d6f636fe064` | TJ CE abre inscrições para níveis médio e superior - Rede ... | arquivo | CE | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 38 | `L-7077dcfb646d5762` | ArcelorMittal Investe: novo edital de apoio a ONGs é lançado | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 39 | `L-77d9ca7e25fd8023` | Call for Letters of Inquiry: Cerrado / CEPF | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 40 | `L-80a9fdc442737a8f` | Edital Social Porto seleciona iniciativas sociais incentivadas | arquivo | RS | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 41 | `L-9c4cee8e375f917f` | Cerrado +Cooperativo: Governo Federal lança edital de R$ 50 milhões para agricultura famil | arquivo | — | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 42 | `L-ff9199517ea95f6c` | Edital seleciona ONGs para projetos de IA e saúde mental ... | arquivo | BR | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 43 | `L-5ea1f1a5c3cd4c48` | Edital De Seleção Pública Nº 2026/006 - Reflorestar | arquivo | BR | encerrada | sem | 0 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 44 | `L-d87b1dd225047164` | Fundação lança edital para ampliar acesso à saúde mental em São ... | arquivo | SP | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 45 | `L-c8392402675d3a67` | Edital De Chamamento Público Nº 02/2026 - Seleção De Organização Da ... | arquivo | BR | encerrada | sem | 7 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 46 | `L-e9bfa6f76865367a` | Edital do Instituto Lojas Renner fortalecerá OSCs em SP, RJ e RS | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 47 | `L-a4ebc9679c35cc16` | Edital Alimento no Prato oferece até R$ 800 mil para projetos de ... | arquivo | BR | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 48 | `L-15af23fd4fe647cf` | FIFE 2026 anuncia virada de lote de inscrições no fim de setembro | arquivo | BR | encerrada | sem | 8 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 49 | `L-6467d26626fce7c4` | Chamada Pública FAPESPA 007/2026 – Como captar recursos | arquivo | BR | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 1 | 50 | `L-29ea85ea6606bffa` | Edital Zurich de Leis de Incentivo 2026 | arquivo | BR | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 1 | `L-57c8158280da05ce` | CMDCA lança edital para projetos sociais voltados a crianças ... | arquivo | BR | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 2 | `L-355ea4606c7514ef` | "A SME publicou o Edital de Chamamento Público nº 5/SME/2026 ... | arquivo | SP | encerrada | sem | 0 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 3 | `L-8defc1b2d773e58f` | SME publica Edital de Chamamento Público para ações de ... | arquivo | BR | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 4 | `L-6bfbd8ebc2563e22` | EDITAL DE CHAMAMENTO PÚBLICO Nº 011/2026/FCMS - Prosas | arquivo | MS | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 5 | `L-a3538cfbcdf3af02` | XXI CBPM 2026 / Goiânia | Farol | — | aberta | bronze | 1 | chegou na semana e foi ao farol sem veredito do Chrome |
| 2 | 6 | `L-08c3ba86f82f7b2c` | TETO Brasil, através de doação do Fundo Comunitário do Airbnb, entrega duas moradias na fa | arquivo | SP | encerrada | sem | 1 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 7 | `L-686a5b6780d4a0d1` | Trump Jr. diz que corte em ONG faz esquerda perder eleição - 05/10/2026 - Mundo - Folha | arquivo | — | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 8 | `L-12b7ddb872b0b827` | Edital Fortalecendo Direitos e Gestando um Mundo Novo 2026 / Casa Projetos Sociais - Proex | arquivo | MA | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 9 | `L-43ca411bfb09063a` | PDF EDITAL DE SELEÇÃO DAS ENTIDADES EXECUTORAS PARA A 9a EDIÇÃO DO CURSO ... | arquivo | — | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 10 | `L-3b91b9a65829ca3e` | Prêmio pagará R$ 230 mil por melhor iniciativa agropecuária | arquivo | SP | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 11 | `L-625370bc07740a09` | Azul 2026 | arquivo | SC | encerrada | sem | 0 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 12 | `L-dfa36a614ee10e71` | Projetos Sociais: Fundação Volkswagen abre inscrições para projetos incentivados | arquivo | — | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 13 | `L-ef0e8d4a73d83366` | Home - Fundação Grupo Volkswagen | arquivo | — | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 14 | `L-fd2a3ead66bfae35` | Edital que destina até R$100 mil para entidades tem inscrições abertas / G1 | arquivo | BA | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 15 | `L-351eaca736f3414d` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 / Agência Brasil | arquivo | — | encerrada | sem | 3 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 16 | `L-53e34a53d0134aab` | PDF EDITAL DE CHAMAMENTO PÚBLICO No 014/2026 | arquivo | AM | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 17 | `L-5b02881843bd0d7a` | EDITAL AMBEV BRASILIDADES 2026 – PROJETOS DE CULTURA E ESPORTE - Instituto INAD | arquivo | — | encerrada | sem | 6 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 18 | `L-a2ff34c46de70e98` | Brasilcap | arquivo | — | encerrada | sem | 5 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 19 | `L-7bd168836fe01b1c` | Instituto Genésio A. Mendes lança Edital 2026 | arquivo | SC | encerrada | sem | 0 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 20 | `L-24d4fa860070e0e6` | Banco do Brasil recebe projetos sociais e de reciclagem até 31 de outubro para apoio finan | arquivo | RJ | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 21 | `L-3bdc0f235659efb1` | Chamamento Engaja Brasil 2026: capte recursos sem comissão (inscrições até 31/10/2026) | arquivo | — | encerrada | sem | 4 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 22 | `L-67afcf15049a8c51` | Regulamento / Chamamento Engaja Brasil 2026 | arquivo | — | encerrada | sem | 8 | chegou na semana e foi ao arquivo sem veredito do Chrome |
| 2 | 23 | `L-a41225aaa17c6599` | Edital PADI Foundation 2026: Guia de Captação em DólarR$ 77 mil·até 16 de jan. de 2027 | arquivo | SC | encerrada | sem | 2 | chegou na semana e foi ao arquivo sem veredito do Chrome |
