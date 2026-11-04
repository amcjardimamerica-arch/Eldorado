# Verificação completa pelo Claude no Chrome — lote-2026-11-04-externa-completo

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Decidir TODOS os livros sem decisão no Eldorado e fazer, junto, o expurgo dos documentos. Depois desta verificação não
pode sobrar nenhuma pendência: o sistema fica livre para as oportunidades novas.

| O que | Quantidade | Onde |
|---|---|---|
| Livros sem decisão | 1147: 746 na verificação externa, 386 na preparação, 15 na recepção | `verificacao/lotes/lote-2026-11-04-externa-completo-parte-1.json` a `-parte-23.json` (50 por parte) |
| Do catálogo das oportunidades conhecidas (R44) | 205 (PNAB, Rouanet, Goyazes, leis de incentivo, fundos, fundações, internacionais) | marcados na tabela e com o campo `catalogo` no lote |
| Sem nenhuma estrela, para validar ou expurgar | 818 | campo `"verificacao_para_expurgo": true` |
| Documentos para o expurgo junto | 16 lotes | `verificacao/expurgo/lote-chrome-documentos-*.json` |

Versão do lote: `gerado_em` = `2026-11-04T22:35:38+00:00`. Os livros já vêm na ordem do Comandante: Goiás → Brasil →
internacional → outras capitais e estados; dentro de cada um, as abertas que fecham antes.

## ENTREGA COMPLETA E TOTAL (R41) — obrigatória

1. Trabalhe UMA PARTE de cada vez. Antes de começar, conte os livros da parte (`total_livros`).
2. Entregue UM veredito decisivo para CADA livro da parte, num único arquivo por parte.
3. Copie do arquivo da parte o `lote` (ex.: `lote-2026-11-04-externa-completo-parte-7`) e o `gerado_em` (no campo `lote_gerado_em`).
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
  "lote": "lote-2026-11-04-externa-completo-parte-1",
  "lote_gerado_em": "2026-11-04T22:35:38+00:00",
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

Grave como `verificacao/vereditos/veredito-lote-2026-11-04-externa-completo-parte-N.json` (uma por parte).

## O expurgo dos documentos (junto)

Para cada um dos 16 arquivos `verificacao/expurgo/lote-chrome-documentos-*.json`, entregue um veredito completo (todos os
grupos), com o `lote` copiado do arquivo, em `verificacao/expurgo/vereditos/veredito-<nome do arquivo>.json`:

```json
{"lote": "<o nome do arquivo do lote>", "vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar",
 "motivo": "…", "titulo": "…", "orgao": "…", "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD", "trecho": "…", "livro_id": "…"}]}
```

## Ao terminar

Uma planilha de controle com o total de cada parte (entregue / não entregue) e os aprendizados que se repetiram. Nada
parcial: a parte que não foi verificada inteira não é entregue.

## A tabela dos 1147 livros pendentes (parte por parte)

Colunas: a parte do lote, a posição na parte, o livro, o título, a etapa, a UF, o prazo, a estrela, quantos dos 12 itens
faltam e a marca (catálogo = R44, nunca sai; expurgo? = sem nenhuma estrela, validar ou expurgar).

| Parte | Nº | Livro | Título | Etapa | UF | Prazo | Estrela | Faltam | Marca |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | `op-7610b88fd1fc` | Quem exatamente pode aplicar neste edital? — Brasil | recepção | GO | aberta | bronze | 2 |  |
| 1 | 2 | `L-93e4a17ea664cf72` | Prefeitura de Quirinópolis abre inscrições para quatro editais da Política Nacional Aldir  | verificação externa | GO | aberta | bronze | 2 |  |
| 1 | 3 | `L-d6f2af76c1fd022b` | CHAMAMENTO PÚBLICO 001/2026 – FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA | preparação | GO | aberta | bronze | 2 |  |
| 1 | 4 | `L-a767fde3d29ee056` | Inscrições para edital Ocupa Goiás – MITsp 2027 começam nesta quarta-feira (4/11) | verificação externa | GO | aberta | bronze | 5 |  |
| 1 | 5 | `L-1fce376bd4f690be` | INSCRIÇÕES ABERTAS PARA O CAMPEONATO MUNICIPAL DE ARTES MARCIAIS (CAMAM) 2026 | preparação | GO | aberta | bronze | 2 |  |
| 1 | 6 | `L-7fa11e1354faab25` | EDITAL AGROINDÚSTRIAS MERCADOS COOPERATIVOS RIO DOCE – SELEÇÃO PÚBLICA 03/2026 – Coopera R | preparação | GO | aberta | bronze | 1 |  |
| 1 | 7 | `L-9a312c76f4aa724b` | EDITAL DE SELEÇÃO PÚBLICA Nº 04_2026_QUINTAIS PRODUTIVOS RIO DOCE | preparação | GO | aberta | bronze | 2 |  |
| 1 | 8 | `L-1edae0f51deb9ff2` | 16/10/2026 / EDITAL DE CHAMAMENTO PÚBLICOEdital de Chamamento Público - Termo de Fomento N | preparação | GO | aberta | prata | 2 |  |
| 1 | 9 | `L-8474edbfca7245fe` | Secretaria de Esporte e Lazer abre edital para credenciamento de patrocinadores das compet | preparação | GO | aberta | prata | 2 |  |
| 1 | 10 | `op-113d3528836c` | Secretaria de Estado da Cultura (Secult) — Secult lança edital de chamamento público para  | preparação | GO | aberta | bronze | 2 |  |
| 1 | 11 | `op-457280912c7f` | Chamamento público para fins de credenciamento de pessoas físicas e jurídicas, com atuação | preparação | GO | aberta | prata | 1 |  |
| 1 | 12 | `L-f34962ed027a9579` | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL — EDITAL DE CHAMAMENTO PÚBLICO VISANDO À SELEÇÃO DE  | preparação | GO | aberta | bronze | 1 |  |
| 1 | 13 | `op-2cf1888b82c9` | Fundo municipal de assistencia social — edital de chamamento público visando à seleção de  | verificação externa | GO | aberta | prata | 2 |  |
| 1 | 14 | `L-4231397535f30ea9` | SEMASC abre Chamamento Público para seleção de projetos voltados à proteção de crianças e  | preparação | GO | aberta | prata | 3 |  |
| 1 | 15 | `op-0dc389eec43b` | Municipio de trindade — credenciamento de instituições de assistência social para acolhime | preparação | GO | aberta | bronze | 1 |  |
| 1 | 16 | `op-ef064d6345a6` | GOIAS TRIBUNAL DE JUSTICA DO ESTADO DE GOIAS — Credenciamento de entidades sem fins lucrat | preparação | GO | aberta | bronze | 1 |  |
| 1 | 17 | `captacao-095` | SEDS Goiás - Auxílio Nutricional a entidades — Goiás | verificação externa | GO | sem prazo | sem | 2 | catálogo |
| 1 | 18 | `L-f73edbb222358e9c` | Credenciamento para atuação nos Residenciais Santa Edwiges I e II avança | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 19 | `L-b7e8c6cb8f6c0057` | Doacao de bens.PDF | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 20 | `L-1fd8d68f56b7da82` | Semad vai financiar projetos da sociobiodiversidade em Goiás; veja o edital | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 21 | `L-040c3fed85393914` | RESOLUÇÃO Nº 15 DE 2026 | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 22 | `L-70e8fcbdb678d319` | Senador Canedo abre credenciamento para ampliar oferta de oficinas esportivas, culturais e | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 23 | `L-dd5da6a7022c4e57` | AVISO DE PUBLICAÇÃO | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 24 | `L-c84e26957106c18c` | Emenda municipal para entidade assistencial | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 25 | `L-490b53079346a74c` | Edital Ocupa Goiás – MITsp 2027 | verificação externa | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 26 | `captacao-069` | Emenda municipal para projeto educativo em Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 4 | catálogo |
| 1 | 27 | `L-4b2357e9611b17a7` | Publicada nova Instrução Normativa do Programa Goyazes | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 28 | `L-7bd91fd4c3e5f390` | Programa Goyazes divulga nova forma de envio para Cartas de Intenção de Patrocínio | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 29 | `L-a797302669cc1f0c` | Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 30 | `captacao-063` | Equipagem esportiva comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 31 | `captacao-096` | SEDS Goiás - Água, energia e esgoto para entidades — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 32 | `captacao-097` | Protege Goiás - financiamento indireto de programas sociais — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 33 | `captacao-104` | Termo de Fomento estadual para entidade social — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 34 | `captacao-109` | Projeto de inclusão produtiva de famílias — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 35 | `captacao-112` | Projeto de apoio a mulheres em vulnerabilidade — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 36 | `captacao-126` | Fundo Estadual dos Direitos da Pessoa Idosa Goiás — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 37 | `captacao-154` | Projeto de saúde mental comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 38 | `captacao-158` | Projeto de reabilitação comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 39 | `captacao-159` | Projeto de teleorientação em saúde comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 40 | `L-e2d72959753623db` | Política Nacional Aldir Blanc - PNAB | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 41 | `L-fde0a18dfd449d02` | TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 42 | `L-f92d47c67976ed40` | docs-bens-para-doacao | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 43 | `L-301c4f104c07b061` | Aviso de Alteração — AVISO DE ALTERAÇÃO DE EDITAL | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 44 | `L-a48fdd94a1dede55` | EDITAL DE MANUTENÇÃO CONTINUADA DE ESPAÇOS DE CULTURA | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 45 | `L-d491fd0842b76692` | EXTRATO DO 1º TERMO ADITIVO AO TERMO DE COLABORAÇÃO EMERGENCIAL Nº 046/2026 | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 46 | `captacao-026` | PNAB Goiás - Manutenção Continuada de Grupos/Companhias — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 47 | `captacao-050` | Pró-Goiás Atleta - atletas e treinadores vinculados a entidades — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 48 | `captacao-054` | Projeto de esporte e contraturno escolar — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 49 | `captacao-057` | Núcleo de artes marciais educativas — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 50 | `captacao-064` | Reforma de espaço esportivo social — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 1 | `captacao-074` | Projeto de reforço escolar e recomposição de aprendizagem — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 2 | `captacao-113` | Projeto de apoio a famílias de baixa renda — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 3 | `captacao-155` | Projeto de prevenção ao uso de álcool e drogas — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 4 | `captacao-163` | Projeto de saúde da mulher — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 5 | `captacao-196` | MPGO - TAC com destinação social — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 6 | `L-3227e43b5edcde45` | Pedidos de inscrição de projetos em caráter excepcional no Programa Goyazes devem ser envi | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 7 | `L-df444e6fcee25a18` | Exposição “Ichi-go Ichi-e” é prorrogada até 7 de fevereiro no Museu da Imagem e do Som de  | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 8 | `L-3951470189011001` | DESPACHO N.º 3178/2026 - SEMAD/GAB - Cuidam-se os autos sobre o 3º Termo | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 9 | `L-417ae8d2e9f5d965` | EXTRATO DO 5º TERMO ADITIVO AO TERMO DE COLABORAÇÃO EMERGENCIAL Nº 041/2025 | verificação externa | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 10 | `L-bd31527690a94e48` | Terras raras: um passo pequeno demais - Outras Palavras | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 11 | `L-a18f3537362ab8f1` | Edital de Teatro | verificação externa | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 12 | `captacao-118` | Destinação de IR pessoa física para FMDCA — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 13 | `captacao-147` | SES-GO - atuação em rede com OSC celebrante — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 14 | `captacao-148` | SES-GO - termo de fomento em saúde — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 15 | `captacao-149` | SMS Goiânia - parceria com entidade de saúde — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 16 | `captacao-151` | Emenda estadual para saúde comunitária — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 17 | `L-96e0e7e0f8cebe7d` | Fundo de Arte e Cultura | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 18 | `L-e8d2b7589e1e8334` | Comunicado de Revogação do Edital do Conselho da Juventude | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 19 | `L-d0643cb995773f5c` | Associações poderão receber material da Prefeitura | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 20 | `L-ef46e9cfdaa9e9e7` | COMFAPE | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 21 | `L-83c645026c1dddd8` | Instituto Reerguer / Acolhimento, Doações e Ações Sociais em Goiânia | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 22 | `L-42f876fb8ac84999` | Goiás convoca suplentes de sete editais da PNAB e destina R$ 1,98 milhão a 33 projetos | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 23 | `L-9c9ab5df92c89249` | DOE - AP DO RIO DOCE - EXT ADJ HOMOL -  CHAMADA PUBLICA N° 018-2026 | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 24 | `captacao-098` | FEAS-GO - cofinanciamento da assistência social — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 25 | `captacao-099` | FMAS Goiânia - parceria socioassistencial — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 26 | `captacao-101` | SEMASDH Goiânia - República para jovens — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 27 | `captacao-102` | SEMASDH Goiânia - serviço de acolhimento para adolescentes — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 28 | `captacao-125` | Fundo Municipal do Idoso de Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 29 | `captacao-138` | Projeto de prevenção ao trabalho infantil — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 30 | `captacao-192` | Justiça Federal em Goiás - prestações pecuniárias — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 31 | `L-096417eff0737f19` | Convênio com órgão público estadual | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 32 | `L-f6d290b1c8331b00` | Manual de Identidade Visual | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 33 | `L-f981ba0888c7d9f0` | Anápolis lança editais com mais de R$ 1,5 milhão para fortalecer a cultura e ampliar oport | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 34 | `L-a9f7bdd04b4b79bf` | -> EDITAL DE CULTURA NO SOCIAL – PNAB 2026 – CATEGORIA CATEGORIA E – CULTURA E MULHERES EM | verificação externa | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 35 | `L-7f3bcb4dff43bf34` | Edital de Convocação AGE 192 versão editada | verificação externa | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 36 | `captacao-053` | Projeto de esporte e lazer para idosos — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 37 | `captacao-070` | Parceria com SME Goiânia para contraturno/educação integral — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 38 | `captacao-078` | Projeto de biblioteca comunitária — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 39 | `captacao-080` | Projeto de mediação de leitura para crianças — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 40 | `captacao-082` | Projeto de empreendedorismo juvenil — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 41 | `captacao-087` | Projeto de combate à evasão escolar — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 42 | `captacao-115` | FMDCA Goiânia - projeto aprovado pelo CMDCA — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 43 | `captacao-120` | Projeto de convivência de crianças e adolescentes — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 44 | `captacao-121` | Projeto de proteção contra violações de direitos — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 45 | `captacao-122` | Projeto de protagonismo juvenil — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 46 | `captacao-123` | Projeto de cultura para adolescentes — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 47 | `captacao-124` | Projeto de esporte para adolescentes — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 48 | `captacao-133` | Projeto intergeracional criança-idoso — Goiás | verificação externa | GO | sem prazo | sem | 9 | catálogo |
| 2 | 49 | `L-61bff86141eeb58a` | FEAS-GO - cofinanciamento da assistência social | verificação externa | GO | sem prazo | sem | 9 | expurgo? |
| 2 | 50 | `L-f8213c1c5de17785` | EDITAL DE REGULARIZAÇÃO FUNDIÁRIA 009-2026 - Qd. 14 e 46 | verificação externa | GO | sem prazo | sem | 9 | expurgo? |
| 3 | 1 | `L-327818548a1796e7` | EDITAL DE TRANSAÇÃO Nº 03/2026 | preparação | GO | sem prazo | sem | 9 | expurgo? |
| 3 | 2 | `L-b9cfa19c7c4b36f6` | Cadastro de órgãos e entidades para solicitação de bens e recursos oriundos de reversões | preparação | GO | sem prazo | sem | 10 | expurgo? |
| 3 | 3 | `L-3fdeb0640f792f7d` | Comissão de Tributação, Finanças e Orçamento | verificação externa | GO | sem prazo | sem | 10 | expurgo? |
| 3 | 4 | `captacao-075` | Projeto de inclusão digital comunitária — Goiás | verificação externa | GO | sem prazo | sem | 11 | catálogo |
| 3 | 5 | `captacao-179` | Compensação ambiental e projetos de educação ambiental — Goiás | verificação externa | GO | sem prazo | sem | 11 | catálogo |
| 3 | 6 | `L-f9c496cc27aa4fe2` | Frente Parlamentar do Terceiro Setor | verificação externa | GO | sem prazo | sem | 11 | expurgo? |
| 3 | 7 | `captacao-002` | PNAB Goiânia - Artes Visuais — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 8 | `captacao-003` | PNAB Goiânia - Teatro — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 9 | `captacao-004` | PNAB Goiânia - Dança — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 10 | `captacao-005` | PNAB Goiânia - Circo — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 11 | `captacao-006` | PNAB Goiânia - Música — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 12 | `captacao-007` | PNAB Goiânia - Arte e Mídias Interativas — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 13 | `captacao-008` | PNAB Goiânia - Literatura e Mídias Impressas — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 14 | `captacao-009` | PNAB Goiânia - Ações Formativas — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 15 | `captacao-010` | PNAB Goiânia - Patrimônio Cultural Material e Imaterial — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 16 | `captacao-011` | PNAB Goiânia - Obras e Reformas de Espaços Culturais — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 17 | `captacao-012` | PNAB Goiânia - Pontos de Cultura — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 18 | `captacao-013` | PNAB Goiânia - Bolsas Cultura Viva para Mestras e Mestres — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 19 | `captacao-014` | Lei Municipal nº 7.957/2000 — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 20 | `captacao-045` | Emenda federal para esporte educacional — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 21 | `captacao-046` | Emenda estadual para projeto esportivo em Goiás — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 22 | `captacao-047` | Emenda municipal para projeto esportivo em Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 23 | `captacao-048` | Termo de Fomento com Secretaria Municipal dos Esportes — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 24 | `captacao-049` | Termo de Fomento por emenda municipal via SRI Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 25 | `captacao-067` | Emenda federal para educação complementar — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 26 | `captacao-068` | Emenda estadual para projeto educativo em Goiás — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 27 | `captacao-071` | Programa Escola em Tempo Integral - articulação com OSC — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 28 | `captacao-079` | Projeto de clubes de leitura — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 29 | `captacao-084` | Projeto de formação de educadores sociais — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 30 | `captacao-089` | Projeto de formação para famílias e parentalidade — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 31 | `captacao-100` | SEMASDH Goiânia - acolhimento institucional — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 32 | `captacao-103` | Termo de Fomento municipal para entidade social — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 33 | `captacao-105` | Emenda federal para assistência social — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 34 | `captacao-106` | Emenda estadual para entidade assistencial — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 35 | `captacao-107` | Emenda municipal para entidade assistencial — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 36 | `captacao-110` | Projeto de apoio a pessoas em situação de rua — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 37 | `captacao-111` | Projeto de segurança alimentar comunitária — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 38 | `captacao-150` | Emenda federal para entidade de saúde — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 39 | `captacao-152` | Emenda municipal para saúde preventiva — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 40 | `captacao-153` | Projeto de saúde bucal comunitária — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 41 | `captacao-160` | Projeto de prevenção de doenças crônicas — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 42 | `captacao-162` | Projeto de acessibilidade em saúde — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 43 | `captacao-190` | TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 44 | `captacao-191` | TJGO - penas pecuniárias em comarcas do interior — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 45 | `captacao-200` | Emenda parlamentar federal individual — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 46 | `captacao-201` | Emenda parlamentar federal de bancada — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 47 | `captacao-202` | Emenda parlamentar estadual individual — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 48 | `captacao-203` | Emenda parlamentar estadual impositiva para OSC — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 49 | `captacao-204` | Emenda parlamentar municipal individual — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 3 | 50 | `captacao-205` | Termo de fomento sem chamamento por emenda — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 4 | 1 | `captacao-212` | TCM-GO - regularidade municipal e controle — Goiás | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 4 | 2 | `captacao-239` | Empresas locais de Goiânia - patrocínio direto não incentivado — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 12 | catálogo |
| 4 | 3 | `L-a9e7e9c979824069` | Prefeitura de Goiânia abre credenciamento de guias de turismo | preparação | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 4 | `L-ee7929b75508aa49` | Reabertura do prazo de recursos | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 5 | `L-bab1e09e18b0818b` | TERMO DE COLABORAÇÃO – PROCESSO ADMINISTRATIVO N° 2023031278 – PARTIS | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 6 | `L-fcbe8d17d9bc1a63` | Aviso de Chamamento Público — AVISO DE CHAMAMENTO PÚBLICO Nº 1/2026 -FME | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 4 | 7 | `L-0340419e9a670eb1` | Áudio do Edital Infância e Juventude | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 8 | `L-e9ef766c55d0f47d` | Áudio de Edital de Teatro | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 9 | `L-5d63305e1abaaed5` | Áudio do Edital de Circo | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 10 | `L-9742d1f28091263b` | Edital de Música | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 11 | `L-5c0b90de565bb3dc` | Áudio do Edital de Artesanato | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 12 | `L-0fff2725c2875140` | Edital de Audiovisual | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 13 | `L-71d775c57af9844e` | Áudio do Edital Goiás pelo Mundo Afora | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 14 | `L-8ffc549ee11e86ac` | EDITAL NATAL DO BEM 2026 – CATEGORIA Categoria A.2 – Apresentações Artísitcas no Coreto –  | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 15 | `L-03937c7356c0db9d` | >EDITAL NATAL DO BEM 2026 – CATEGORIA Categoria A.5 – Apresentações Artísitcas no Coreto – | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 16 | `L-37695362d4f29b86` | EDITAL NATAL DO BEM 2026 – CATEGORIA Categoria B.3 – Apresentações MÚSICA | verificação externa | GO | sem prazo | sem | 12 | expurgo? |
| 4 | 17 | `L-4713911330cc16f1` | edital-estabelece-chamada-para-candidaturas-de-territorios-da-restauracao | preparação | BR | aberta | bronze | 4 |  |
| 4 | 18 | `op-2ae6b1d4f552` | Pague Menos abre edital para financiar projetos de saúde e inclusão social em todo o Brasi | preparação | BR | aberta | bronze | 2 |  |
| 4 | 19 | `L-36c27897cd76e33c` | Chamamento Quixadá 2026: Edital UPA 10.006/SMS | preparação | BR | aberta | bronze | 1 |  |
| 4 | 20 | `op-b74799841a6d` | TCSA Porto Sul - Chamada 10/2026: Recomposição da Vegetação Nativa e Fortalecimento da Cad | preparação | BR | aberta | bronze | 2 |  |
| 4 | 21 | `nova-98415000038c` | Portal Gov.br — MROSC e Parcerias — Brasil | recepção | BR | aberta | bronze | 2 |  |
| 4 | 22 | `L-bf172347e2eceb17` | Edital 45º (2º/2025) para organizações da sociedade civil e ... | preparação | BR | aberta | bronze | 2 |  |
| 4 | 23 | `L-0059dea383da1a71` | instituto impactarte abre edital projetos impacto social apoio ky3h8l | preparação | BR | aberta | prata | 2 |  |
| 4 | 24 | `L-bbf6a1bf8fff4611` | EDITAL PULSA FRANCO - ANIVERSÁRIO DE FRANCO DA ROCHA (82 ANOS) | preparação | BR | aberta | bronze | 3 |  |
| 4 | 25 | `L-1bdd24cbf29b642b` | Instituto Impactarte abre edital contínuo de apoio a OSCs - Escola ... | preparação | BR | aberta | prata | 4 |  |
| 4 | 26 | `L-2cd13d0b28654fdf` | Edital SVS 2026 – Captação de R$1,1 mi para vigilânciaR$ 1,1 mi·até 13 de nov. de 2026 | verificação externa | AP | aberta | prata | 2 |  |
| 4 | 27 | `L-9c15ec76c4bb0880` | apoio financeiro / Núcleo de Relações Internacionais | preparação | BR | aberta | bronze | 2 |  |
| 4 | 28 | `L-15843f8d3c824066` | Edital Saúde Branquinha 2026: Como OSCs Podem Captaraté 16 de nov. de 2026 | preparação | BR | aberta | bronze | 1 |  |
| 4 | 29 | `L-0d09458a7d146360` | EDITAL DE RECONHECIMENTO E PREMIAÇÃO DOS MESTRES E MESTRAS DA CULTURA POPULAR DE ARATUBA – | preparação | BR | aberta | bronze | 2 |  |
| 4 | 30 | `L-763c190b30482bb2` | Edital ANATER 3/2026: quem pode aplicar e captar recursosaté 18 de nov. de 2026 | preparação | MG | aberta | bronze | 2 |  |
| 4 | 31 | `L-a2c10bb8c67f0d12` | Aviso — EDITAL DE CONVOCAÇÃO CONJUVE/SNJ/SG/PR Nº 1/2026 | verificação externa | BR | aberta | bronze | 3 |  |
| 4 | 32 | `L-66536bfbc7973f99` | Edital ANATER 4/2026: quem pode concorrer e captar recursosR$ 11,3 mi·até 19 de nov. de 20 | preparação | MG | aberta | bronze | 2 |  |
| 4 | 33 | `L-065193c2149b25c2` | Inscrições abertas para o edital Quintais Produtivos para Mulheres ... | preparação | BR | aberta | bronze | 2 |  |
| 4 | 34 | `L-11c34b5394cbc54c` | Edital 03/2026 – Coopera Rio + Doce (Anater/BNDES)até 19 de nov. de 2026 | preparação | MG | aberta | bronze | 4 |  |
| 4 | 35 | `L-50693714a9bf17e8` | Edital CBMM 2026: Guia Completo de Captaçãoaté 30 de nov. de 2026 | preparação | MG | aberta | bronze | 1 |  |
| 4 | 36 | `L-aba76de122cd39fe` | Chamamento Engaja Brasil 2026 / Inscreva sua OSC | preparação | BR | aberta | prata | 2 |  |
| 4 | 37 | `L-30b0c9d6efacdd7f` | Instituto GOL abre edital para doar passagens aéreas a OSCs | recepção | BR | aberta | bronze | 2 |  |
| 4 | 38 | `L-1a5e53224be242d2` | Edital FIA Sarandi 2026: Guia para OSCs captarem recursosaté 01 de dez. de 2026 | preparação | BR | aberta | bronze | 4 |  |
| 4 | 39 | `L-84dc89cf76baa817` | edital-seleciona-redes-para-implementacao-de-nucleos-de-desenvolvimento-da-sociobioeconomi | preparação | BR | aberta | bronze | 3 |  |
| 4 | 40 | `op-424cf54854a5` | BNDES abre chamada para apoiar projetos de organizações periféricas em todo o país — BNDES | preparação | BR | aberta | prata | 1 |  |
| 4 | 41 | `op-9b1d2dfcbd4e` | BNDES abre chamada para apoiar projetos de organizações periféricas em todo o país — Brasi | preparação | BR | aberta | prata | 1 |  |
| 4 | 42 | `L-8e00fb51f461c33b` | Edital BNDES Periferias em Rede: Como Captar até 2M em 2026R$ 2,0 mi·até 04 de dez. de 202 | preparação | BR | aberta | prata | 2 |  |
| 4 | 43 | `L-623834cf4a9f402c` | Chamada abre apoio a organizações de base periférica - Nossa Causa | preparação | BR | aberta | bronze | 2 |  |
| 4 | 44 | `L-0d00a9db100f2324` | BNDES lança 6º ciclo de chamada para apoio a projetos nas periferias urbanas do país | preparação | RJ | aberta | bronze | 2 |  |
| 4 | 45 | `L-959b8cb42a5bdfb1` | Edital Recaatingar 2026 – Recuperação na CaatingaR$ 55,2 mi·até 14 de dez. de 2026 | preparação | BR | aberta | bronze | 2 |  |
| 4 | 46 | `op-677f1cf40da5` | Primeiro Ciclo Edital Reecatingar: divulgação prorrogada — Brasil | recepção | BR | aberta | prata | 10 |  |
| 4 | 47 | `op-167829dfd75a` | Mapfre abre seleção de projetos incentivados com foco em cultura, esporte e inclusão socia | recepção | BR | aberta | bronze | 4 |  |
| 4 | 48 | `op-2c0b8a816195` | Edital Mapfre 2026 de patrocínio incentivado: só a janela de PRONAS/PCD e PRONON segue abe | recepção | BR | aberta | prata | 4 |  |
| 4 | 49 | `L-7ad6e1d62f398963` | Edital Mapfre 2026: Projetos de Cultura e Esporteaté 15 de dez. de 2026 | preparação | BR | aberta | bronze | 4 |  |
| 4 | 50 | `L-31700784edd49869` | 3º Edital Frei Tito | preparação | CE | aberta | bronze | 2 |  |
| 5 | 1 | `L-b567222a27246a8e` | Chamada Rio Doce ParticipativoConheça as regras do edital de apoio a projetos estruturante | preparação | BR | aberta | bronze | 2 |  |
| 5 | 2 | `op-aa70ccf9ba8b` | Chamada Rio Doce Participativo — Projetos Estruturantes para o Desenvolvimento Territorial | preparação | BR | aberta | prata | 3 |  |
| 5 | 3 | `L-9bfc983ec1355812` | Edital CELESC PIE 2026: Captar até R$ 300 milaté 31 de dez. de 2026 | preparação | SC | aberta | bronze | 4 |  |
| 5 | 4 | `L-545b918cd28ff66b` | Chamada PRONINC 2026 – Finep Financiamento até R$5 miR$ 5,0 mi·até 14 de jan. de 2027 | preparação | BR | aberta | bronze | 2 |  |
| 5 | 5 | `L-8a4492b60258e8e2` | Chamada Pública 3/2026 Reitoria: Guia para Catadoresaté 19 de jan. de 2027 | preparação | RJ | aberta | bronze | 2 |  |
| 5 | 6 | `op-e96e36b220b6` | Lei Rouanet (mecanismo Incentivo a Projetos Culturais do Pronac), MinC. Programa permanent | recepção | BR | aberta | ouro | 0 |  |
| 5 | 7 | `L-65c48b1fe7662342` | Chamada de Propostas FAPESP/MCTI/MCom/CGI.br 2026 para ... | preparação | SP | aberta | bronze | 2 |  |
| 5 | 8 | `L-00651d67a3de7bdb` | Fortalece Cursinhos Populares lança edital para apoiar iniciativas de educação popular | preparação | BR | aberta | bronze | 2 |  |
| 5 | 9 | `nova-29bca7738ad2` | Chamada Pública MCTI/CNPq/ANR N° 32/2026 — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 10 | `op-4471eceed259` | Inscrições abertas para Programa de capacitação para entidades socioambientais — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 11 | `op-c0289af6330d` | Black STEM – 1ª edição — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 12 | `op-48b6d473759b` | Programa Funarte Aberta 2026 — Ocupação da Sala Multiuso do Centro Técnico de Artes (Rio d | preparação | BR | aberta | prata | 1 |  |
| 5 | 13 | `L-78874945ef50d4db` | Edital CEMIG 2026: Banco de Projetos Culturais e Saúde | preparação | BR | aberta | bronze | 4 |  |
| 5 | 14 | `op-24ac6bab9536` | Edital 01/2026 do FNS/CNBB (Campanha da Fraternidade 'Fraternidade e Moradia'): auxílio de | recepção | BR | encerrada | bronze | 0 |  |
| 5 | 15 | `op-c95f8c5d7a9c` | Selecionar projetos de Pontões de Cultura para celebrar Termo de Compromisso Cultural (TCC | recepção | BR | encerrada | prata | 1 |  |
| 5 | 16 | `op-d0da321a9cec` | Edital 2026 do Fundo Nacional de Solidariedade (CNBB) para projetos de moradia ligados à C | recepção | BR | encerrada | bronze | 1 |  |
| 5 | 17 | `op-5bdd0bd521e4` | Edital SCDC/MinC nº 11/2026 (2º Edital Cultura Viva — Rede de Pontões) seleciona Pontões d | recepção | BR | encerrada | prata | 2 |  |
| 5 | 18 | `L-1709cea91427c960` | Lei Rouanet - doação de pessoa física | preparação | BR | sem prazo | sem | 1 | expurgo? |
| 5 | 19 | `L-d5f7ae07244c79d6` | Edital Funarte Aberta 2026 - Centro de Teatroaté 30 de abr. de 2027 | verificação externa | BR | sem prazo | bronze | 1 |  |
| 5 | 20 | `captacao-036` | Lei Rouanet - patrocínio pessoa jurídica — Brasil | verificação externa | BR | sem prazo | sem | 2 | catálogo |
| 5 | 21 | `captacao-090` | MDS - Cozinhas Solidárias 2026 — Brasil | verificação externa | BR | sem prazo | sem | 2 | catálogo |
| 5 | 22 | `L-d5aa75c011ebfa08` | EDITAL DE CHAMAMENTO PÚBLICO Nº 008/2026 POLÍTICA NACIONAL ALDIR BLANC (PNAB) - SECULT CHO | preparação | BR | sem prazo | sem | 2 | expurgo? |
| 5 | 23 | `L-21d4907988607765` | Edital Recupera Cerrado 2026 – Guia do Banco do BrasilR$ 1,0 mi | preparação | BR | sem prazo | sem | 2 | expurgo? |
| 5 | 24 | `L-45ee431cbdf27937` | Edital CMDPI Riacho dos Machados 2026: Guia de Captação | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 25 | `L-274d0251602f77df` | Edital com inscrições permanentemente abertas incentiva ... | preparação | SP | sem prazo | sem | 3 | expurgo? |
| 5 | 26 | `L-d1c89227e9c4670b` | Convocatoria Consejo de la Sociedad Civil 2026 – 2028 &#8211; Comisión Nacional de Riego | preparação | RS | sem prazo | sem | 3 | expurgo? |
| 5 | 27 | `L-1ecb0900ac49b0ea` | XVIII Seleção Funarte Marc Ferrez de Fotografia | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 28 | `L-013a6acc53cdfdf3` | Fundo OSC apoia 40 projetos de organizações da sociedade civil em todo o Brasil - NIDDE DI | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 29 | `L-cd847ed07b71f074` | EDITAL DE CHAMAMENTO PÚBLICO Nº 03/2026 - PRÊMIO CULTURA NEGRA E CULTURA INCLUSIVA | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 30 | `L-a28273823f0adb77` | Edital SEDAC 35/2026 – Patrimônio Cultural – 2026 RSR$ 1,4 mi | preparação | BR | aberta | bronze | 4 |  |
| 5 | 31 | `captacao-139` | Projeto de fortalecimento de conselhos e controle social — Brasil | verificação externa | BR | sem prazo | sem | 4 | catálogo |
| 5 | 32 | `captacao-167` | FDD - patrimônio cultural brasileiro — Brasil | verificação externa | BR | sem prazo | sem | 4 | catálogo |
| 5 | 33 | `L-b9390caf143e8993` | chamada publica articuladores locais edital 012018 | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 34 | `L-a9058a24cd25ed90` | Edital seleciona projetos para fortalecer proteção de crianças e ... | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 35 | `L-6793c71b032d65ed` | Edital CMDPI Santaluz 2026: Guia de Chancela de Projetos | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 36 | `L-74402b14b173797a` | Edital CMDPI Godofredo Viana 2026: Guia de Inscrição | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 37 | `L-ee8524847a1d548e` | Edital Instituto EDP 2026: Banco de Projetos | verificação externa | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 38 | `L-ce7087f6ac9f3577` | Dia Nacional da Construção Social reúne trabalhadores e famílias em Aparecida de Goiânia - | preparação | — | sem prazo | sem | 4 | expurgo? |
| 5 | 39 | `L-e12da8c338781518` | 10 ONGs ambientais brasileiras para doar em 2026 | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 40 | `L-a3529382127b06df` | Fies 2: inscrições gratuitas para vagas remanescentes estão abertas / Agência Brasil | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 41 | `captacao-037` | Programa Rouanet Juventude — Brasil | verificação externa | BR | sem prazo | sem | 5 | catálogo |
| 5 | 42 | `L-0636672456b526c7` | instituto lojas renner seleciona projetos de empreendedorismo feminino | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 43 | `L-d8c0579e2e2b24bc` | chamada publica 0222026 projeto perfil censitario juventude bairro pt25ux | verificação externa | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 44 | `L-b61d39393f78e396` | Fundo Regenerativo PcD lança chamada aberta para projetos de inclusão em Belo Horizonte e  | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 45 | `L-666604fbe5770427` | Ação da Cidadania Contra a Fome a Miséria e Pela Vida: Doe Agora | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 46 | `L-726a23675b65b5b3` | Nova Lei de Doação de Alimentos: incentivos fiscais para redução do desperdício - Moore | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 47 | `L-70b99a72d09d413c` | Programa conserta e doa computadores a escolas e bibliotecas / Agência Brasil | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 48 | `L-6cc08a827f1546d2` | Chamada Pública CNPq/MMULHERES 2026 – Asas para o Futuro | verificação externa | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 49 | `captacao-041` | Lei de Incentivo ao Esporte - Esporte para Toda a Vida — Brasil | verificação externa | BR | sem prazo | sem | 6 | catálogo |
| 5 | 50 | `captacao-077` | Projeto de educação ambiental escolar — Goiás | verificação externa | BR | sem prazo | sem | 6 | catálogo |
| 6 | 1 | `captacao-178` | TAC ambiental via Ministério Público — Brasil | verificação externa | BR | sem prazo | sem | 6 | catálogo |
| 6 | 2 | `L-e75cb9a0fae269e3` | Fundação Maria Emília lança chamada aberta para viabilizar soluções em Saúde e Educação | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 3 | `L-e2c5f8416837e526` | Instituto Cactus lança edital para apoiar projetos de saúde mental voltados às mulheres | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 4 | `L-b2a0292854f18825` | rj lei municipal de cultura abre edital de incentivo | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 5 | `L-afd2e1a5f1ef2bee` | Fundação Telefônica Vivo | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 6 | `L-262c6ca4479191ea` | Fundação Vale | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 7 | `L-553ab50737df52c1` | Instituto Neoenergia | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 8 | `L-a97855804cde9350` | Instituto Lojas Renner | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 9 | `L-c3bb8ee801a083d9` | Edital Instituto John Deere 2026: Guia de Captação | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 10 | `L-64d7b4159c458f36` | Edital FCCR 2024: Arte e Longevidade em São José 2026 | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 11 | `L-6779f8b084960a24` | Edital AlimentaLAB 2026: Guia de Captação e Inovação | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 12 | `L-d1fc1080460201e7` | chamada publica 0212026 projeto radiografia censitaria economia criati e8kuab | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 13 | `L-ed734dd58af49e47` | Edital Carreiras em Movimento aproxima estudante de engenharia da profissional que a inspi | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 14 | `L-9b249a83dda7abfc` | Lei autoriza que empresas e organizações doem alimentos Raquel Montero - Advogada | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 15 | `L-e949ae2748e0a162` | Edital apoia ONGs com foco em saúde e inclusão - Nossa Causa | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 16 | `L-fe871273592eee2b` | Carreiras Santander: venha fazer parte do nosso time | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 17 | `L-537671d9c19d35d0` | Conexão Coloplast - Coloplast Brasil | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 18 | `L-e56c9f0b396fcd14` | Prosas Editais » Capta | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 19 | `L-c11c27e9053ec925` | Edital Impactarte » Capta | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 20 | `L-119eb3c43f8ec210` | ONGs baianas buscam título nacional | preparação | — | sem prazo | sem | 6 | expurgo? |
| 6 | 21 | `L-42ec7db59b6eff68` | Our Rights, Our Future! – Call for proposal - CCPR-Centre | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 22 | `L-c1454109f3f472af` | Conheça a parceria entre o TCU e a organização Programando o Futuro - Programando o Futuro | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 23 | `L-0ae30db9b442d961` | Projetos maranhenses irão receber recursos para apoiar crianças, adolescentes e pessoas id | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 24 | `L-1ee7a71bc730213c` | Prosas / Listagem de editais | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 25 | `captacao-119` | Destinação de IR pessoa jurídica para Fundo da Criança — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 26 | `captacao-169` | FDD/Pronasci - cultura e cidadania em territórios vulneráveis — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 27 | `captacao-193` | CNJ - política de destinação de penas pecuniárias — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 28 | `captacao-215` | Prosas - Central de Editais — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 29 | `captacao-217` | Bússola Social - Bússola Editais — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 30 | `captacao-219` | GIFE Mosaico - base de projetos — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 31 | `captacao-226` | Instituto Natura — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 32 | `captacao-234` | Instituto Unibanco — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 33 | `L-d2dc513f4abddc06` | prazo prorrogado edital de intercambio para projetos apoiados pelo programa casa cidades | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 34 | `L-d8904b3f21a28a5a` | PL 153/2026 — Altera a Lei nº 9.610, de 19 de fevereiro de 1998, para dispor sobre a desti | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 35 | `L-75e197636d0a60b7` | MPV 1336/2026 — Altera a Lei nº 8.036, de 11 de maio de 1990, que dispõe sobre o Fundo de  | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 36 | `L-b6e9044b7df66a86` | Instituto Grupo Boticário | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 37 | `L-fbe001df9037a548` | Edital Orquestra Joseense FCCR 2026: Guia de CaptaçãoR$ 4 mil | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 38 | `L-f2f5524e139a08d7` | Edital Programa de Recuperação Econômica de Pequenos Negócios de Empreendedores (as) Negro | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 39 | `L-8e0b34b3b8579bed` | Juizado do Torcedor de Pernambuco financia projetos sociais com recursos de prestações pec | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 40 | `L-bb112d2b0a7c4f9c` | Civil Society Microgrant 2025: COP30 Call for Proposal | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 41 | `L-9bc6001a85385bb1` | Mina Cultural / Marketing de causa | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 42 | `L-f3c196b2343fcbdf` | Prêmio Impacta Mais 2026: Inscrições Abertas para Iniciativas Sociais e Ambientais | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 43 | `L-f2596f99b591d72e` | chamada publica mctifinepfndct cooperamais tecnologia ict parceria coo 3oyz1t | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 44 | `L-7df240257f7de5ea` | Após eleições, empresas anunciam nas redes sociais fim de doações / G1 | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 45 | `L-3bff05968828fcb4` | Todos à Mesa &#8211; Unidos para Alimentar | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 46 | `L-ac1faeb41421a42a` | SoMar Azul: inscrições abertas para o edital que busca soluções ... | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 47 | `L-ebb92f44d65c520e` | Edital CMDCA 001/2026 – Pedra Azul MG: Captação via FMDCA | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 48 | `L-ae0676ca0464063f` | O cenário das ONGs no Brasil em 2026 - INCAvoluntário | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 49 | `captacao-128` | Destinação de IR pessoa física para Fundo do Idoso — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 6 | 50 | `captacao-129` | Destinação de IR pessoa jurídica para Fundo do Idoso — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 1 | `captacao-136` | Conselho de Igualdade Racial - projetos de promoção da igualdade — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 2 | `captacao-137` | Conselho da Mulher - projetos de autonomia e proteção — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 3 | `captacao-182` | Projeto de compostagem comunitária — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 4 | `captacao-198` | MPT - TAC para inclusão profissional — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 5 | `captacao-208` | Cessão de bens móveis apreendidos — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 6 | `captacao-210` | Tribunal de Contas - capacitação e controle para OSC — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 7 | `captacao-211` | TCE-GO - exigências de certidão para captação — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 8 | `captacao-216` | Mapa das OSC - área de editais — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 9 | `captacao-218` | Capta - oportunidades e editais — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 10 | `captacao-225` | Instituto Claro — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 11 | `captacao-227` | Instituto Coca-Cola Brasil — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 12 | `L-b08e5bedca000adc` | Fundação Banco do Brasil lança o Edital Rio Doce Participativo e Comunitário – Chamada Púb | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 13 | `L-e99fd3814d087eae` | projetos aprovados chamada publica 0012018 articuladores locais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 14 | `L-4ce84e6cc535deef` | RQS 366/2026 — Requer a realização de Sessão de Debates Temáticos destinada a discutir os  | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 15 | `L-72ce3c531c8db250` | Bússola EditaisEncontre editais de financiamento e gerencie candidaturas com eficiência.Ba | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 16 | `L-c6122d2efb404197` | Lideranças Negras e Oportunidades de Acesso | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 17 | `L-8caf7af533483667` | Fundação Itaú | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 18 | `L-e3d53c5efd260a49` | Cultura de Doação | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 19 | `L-eba16fcc7a79ecb3` | Saberes 2025: Financiamento de Soluções Climáticas Locais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 20 | `L-bd50a3171b5395a6` | • Cadastros e Registros Especiais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 21 | `L-0d9e86d1d715087e` | Leilão e Doação | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 22 | `L-af8182f136d77bad` | DoaMais - Encontre ONGs e Faça a Diferença | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 23 | `L-a8352815889fb704` | Faculdade de Medicina de Uberlândia abre inscrições | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 24 | `L-111b49d5bf16972d` | #FazAXepa: Campanha nacional é lançada em evento que prega união contra o desperdício de a | preparação | — | sem prazo | sem | 8 | expurgo? |
| 7 | 25 | `L-f43676458aa0d096` | Edital de segurança alimentar abre inscrições para projetos | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 26 | `L-8cf9d76496dbd49f` | Áudio: CCJ analisa criação de fundo de amparo às crianças órfãs | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 27 | `L-9d526a1b43f82ba9` | Chamada Aberta 2026 Instituto Impactarte - ssir.com.br | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 28 | `captacao-062` | Festival esportivo intergeracional — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 29 | `captacao-072` | Arte e Cultura na Educação Integral — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 30 | `captacao-086` | Projeto de educação para direitos humanos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 31 | `captacao-108` | Projeto de convivência e fortalecimento de vínculos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 32 | `captacao-130` | Projeto de convivência para idosos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 33 | `captacao-132` | Projeto de cuidadores e apoio familiar — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 34 | `captacao-134` | MDHC - editais de direitos humanos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 35 | `captacao-156` | Projeto de formação de cuidadores — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 36 | `captacao-165` | FDD - meio ambiente — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 37 | `captacao-166` | FDD - defesa do consumidor — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 38 | `captacao-168` | FDD - outros direitos difusos e coletivos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 39 | `captacao-173` | Fundo Clima - projetos socioambientais — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 40 | `captacao-176` | BNDES Corais - meio ambiente — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 41 | `captacao-180` | Projeto de coleta seletiva inclusiva — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 42 | `captacao-184` | Projeto de recuperação de nascente urbana — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 43 | `captacao-186` | Projeto de educação para defesa do consumidor — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 44 | `captacao-187` | Projeto de acessibilidade cultural/patrimonial — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 45 | `captacao-189` | Projeto de economia circular com mulheres e jovens — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 46 | `captacao-194` | MPF - cadastro de entidades para bens e valores de autocomposição coletiva — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 47 | `captacao-195` | CNJ/CNMP - bens e valores de ações coletivas — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 48 | `captacao-197` | MPT - TAC para projetos de combate ao trabalho infantil — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 49 | `captacao-209` | Receita Federal - doação de mercadorias apreendidas — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 50 | `captacao-233` | Instituto Sicoob — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 1 | `L-dab3e164150143be` | embaixada da australia abre edital para projetos de pequeno e medio porte | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 2 | `L-6b5e48152ff75848` | Apresentação de emendas | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 3 | `L-4e9a47f6002e9e71` | REQ 5/2026 - CCJ — Requer, nos termos dos arts. 336, II, e 338, IV, do Regimento Interno d | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 4 | `L-c730436c2df4b59c` | Edital Biblioteca Comunitária é Cultura Viva | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 5 | `L-654053a13c1e3d7d` | PEC 6/2026 — Altera o art. 156-A, § 6°, IV da Constituição Federal para incluir as entidad | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 6 | `L-7c39565d46943088` | 2026Um ano sem celular nas escolas: o que mudou?Entrevista: Flora Ariza, consultora da Une | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 7 | `L-beab74b3c9814bac` | Concurso de Teatro e Prêmio 2025 | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 8 | `L-f1d429444543408b` | Edital 2025 do Fundo de Impacto para Justiça Social (ICOM): “Justiça Climática Começa nos  | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 9 | `L-661029b0cc856333` | Natal Sem Fome 2026 | preparação | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 10 | `L-bd0b9f49de015351` | Instituto Impactarte abre seleção permanente para apoiar projetos ... | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 11 | `L-ad5da83eedc90264` | Instituto Natura | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 12 | `L-941753fd218962cc` | Chamada Pública CNPq/MCTI N° 36/2026 - Apoio a cursos de curta duração em biodiversidade,  | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 13 | `captacao-040` | Lei de Incentivo ao Esporte - Formação Esportiva — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 14 | `captacao-042` | Lei de Incentivo ao Esporte - Excelência Esportiva — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 15 | `captacao-052` | Projeto de inclusão pelo paradesporto — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 16 | `captacao-060` | Escolinha de natação/paradesporto adaptado — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 17 | `captacao-061` | Formação de árbitros e monitores esportivos — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 18 | `captacao-065` | Transferegov - termo de fomento para projeto educacional — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 19 | `captacao-066` | Transferegov - termo de colaboração para educação comunitária — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 20 | `captacao-091` | MDS - Segurança alimentar e nutricional — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 21 | `captacao-092` | MDS - Programa Cisternas / tecnologias sociais de água — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 22 | `captacao-093` | MDS - Sistemas alimentares circulares — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 23 | `captacao-094` | Plano Nacional de Cuidados - participação/arranjos com OSC — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 24 | `captacao-170` | FNMA - redução de vulnerabilidade climática — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 25 | `captacao-171` | FNMA - catadores e reciclagem — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 26 | `captacao-172` | FNMA - educação ambiental — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 27 | `captacao-199` | Defensoria Pública - parcerias de educação em direitos — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 28 | `captacao-207` | Acordo de cooperação sem transferência financeira — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 29 | `captacao-213` | Universidade pública - projeto de extensão com OSC — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 30 | `captacao-214` | Órgão público - chamamento para execução de política pública — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 31 | `L-87316d7a66e04839` | Prospera Amazônia (programa 44000) | preparação | — | sem prazo | sem | 10 | expurgo? |
| 8 | 32 | `L-b34679d6e44a74a3` | Estudo de Ingressantes das Licenciaturas - Edital CAPES/INEP nº 26/2026 | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 33 | `L-ca58e967440020b4` | Além do financiamento: estudo global revela demandas das ONGs para ampliar sua resiliência | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 34 | `L-03722b231fb461ba` | Penas pecuniárias: tribunal fluminense repassa R$ 4,4 mi a 51 entidades | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 35 | `L-94711ef6f9176229` | Arquivo de Editais - Observatório do 3° Setor | preparação | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 36 | `L-75686f21585e8b1d` | Grantmaking in Brazil – iCS - Instituto Clima e Sociedade | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 37 | `L-329dca61fa8d537d` | Rede multidisciplinar de atenção a mães e familiares vítimas de desaparecimentos forçados  | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 38 | `L-0f21ea3b8bb0ee39` | Ação 214S - Rotas de Integração Nacional - RP2 (programa 53000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 39 | `L-52028b124d35ceb4` | ATENÇÃO INTEGRAL À SAÚDE DA CRIANÇA - POLÍTICAS DE ATENÇÃO A SAÚDE DA CRIANÇA / ACAO 5119. | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 40 | `L-d39c77d6d41a0dd1` | Programa Selo Verde Brasil (programa 28000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 41 | `L-5b9e28cf67a1612e` | NOVO PAC PATRIMÔNIO CULTURAL - OBRAS 2026 (programa 42000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 42 | `L-b90dfaa181a9b934` | Promoção e Apoio ao Desenvolvimento do Futebol Masculino e Feminino - Convênio (RP 2) - SN | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 43 | `L-609630b61e19251e` | Rede de Acesso e Desenvolvimento Rural (programa 49000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 44 | `L-a362cd1eacea7d40` | Transparência das emendas coletivas | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 8 | 45 | `L-7c8a15dfd068950c` | Indigenous Peoples Fellowship Initiative | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 8 | 46 | `L-7de78bcbb23d33ca` | Rockefeller Foundation | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 8 | 47 | `L-7d2bebb6073526b2` | Virada Sustentável, que acontece de 6 a 9 de junho, abre edital ... | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 8 | 48 | `L-52299c9194d034f9` | 04/11/2026 09:55LOA 2027 - Cronograma de tramitação | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 8 | 49 | `captacao-043` | Lei de Incentivo ao Esporte - projeto paradesportivo — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 8 | 50 | `captacao-044` | Projetos aptos à captação na LIE — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 1 | `captacao-056` | Campeonato comunitário com inclusão social — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 2 | `captacao-058` | Núcleo de futebol de base comunitário — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 3 | `captacao-059` | Núcleo de corrida/caminhada comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 4 | `captacao-073` | Projeto de alfabetização comunitária de jovens — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 5 | `captacao-076` | Projeto de laboratório maker social — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 6 | `captacao-083` | Projeto de robótica educacional comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 7 | `captacao-085` | Projeto de educação financeira comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 8 | `captacao-117` | Fundo Nacional da Criança e Adolescente — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 9 | `captacao-131` | Projeto de inclusão digital da pessoa idosa — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 10 | `captacao-135` | Conselho da Pessoa com Deficiência - projetos de acessibilidade — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 11 | `captacao-142` | Pronon - pesquisa clínica/epidemiológica oncológica — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 12 | `captacao-144` | Pronas/PCD - formação de profissionais — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 13 | `captacao-145` | Pronas/PCD - pesquisa sobre deficiência — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 14 | `captacao-157` | Projeto de apoio a familiares de PCD — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 15 | `captacao-161` | Projeto de vacinação/campanhas educativas de apoio — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 16 | `captacao-164` | Projeto de saúde para população em vulnerabilidade — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 17 | `captacao-181` | Projeto de horta comunitária urbana — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 18 | `captacao-183` | Projeto de arborização e educação ambiental — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 19 | `captacao-185` | Projeto de resíduos eletrônicos — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 20 | `captacao-188` | Projeto de prevenção a desastres e clima em bairros — Goiás | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 21 | `captacao-220` | BNDES Fundo Socioambiental — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 22 | `captacao-228` | Instituto Localiza — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 23 | `captacao-230` | Fundação ArcelorMittal — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 24 | `L-f059e617f62fb339` | fundo brasil recebe propostas preliminares para edital litigancia estrategica ate o dia 23 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 25 | `L-bd2e97ab93257c89` | encerrado o envio de pedidos para o fundo de apoio emergencial covid 19 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 26 | `L-fe9b6ac885b4090d` | sueli carneiro recebe o premio itau cultural 30 anos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 27 | `L-e05d07f104abf825` | edital direitos humanos e justica criminal inscricoes estao abertas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 28 | `L-e52e914f973fd1cc` | labora vai doar r1 milhao em edital para trabalhadores enfrentarem mudancas climaticas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 29 | `L-c69d3b59c4fcab7c` | justica climatica na amazonia e no cerrado novo edital do raizes recebe inscricoes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 30 | `L-65823116651d81b7` | fundacao mauricio sirotsky sobrinho oferece curso online e premiacao para projetos de ince | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 31 | `L-fdf6206e525557f7` | inscricoes abertas para o premio de criacao de valor compartilhado da nestle | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 32 | `L-47be716328ac7216` | onu seleciona iniciativas para empoderamento feminino | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 33 | `L-aa14b47e800d7492` | editora ftd abre edital na area da educacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 34 | `L-f2848ea576a93c8d` | ultima chamada para a votacao do premio rbs de educacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 35 | `L-bf5cde5fc01e2efb` | inscricoes abertas para desafio natura campus | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 36 | `L-5732b0cfe526326d` | fundo de inovacao humanitaria seleciona iniciativas inovadoras ao redor do mundo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 37 | `L-deca98502881d596` | premio visa a incentivar avancos em gestao ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 38 | `L-f039bab366fdf254` | pescar recebe premio de tecnologia social | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 39 | `L-cb957f1ec8061397` | premio empreendedor social recebe inscricoes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 40 | `L-c9c60b4aa16372b0` | premio de fotografia povos conectados com a terra | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 41 | `L-9f29dd1d133b6d06` | funda casa abre chamada de projetos para apoiar a autonomia e resiliencia de comunidades a | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 42 | `L-dd706e2f0b842710` | fundo casa abre chamada com foco em projetos para fortalecer a autonomia e resiliencia dos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 43 | `L-c4591fe9fc20c1a2` | chamada de projetos apoio a resiliencia climatica e reconstrucao comunitaria no rio grande | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 44 | `L-ce3dacb0554ad189` | fundo casa lanca primeira chamada de projetos de 2025 educacao para o bem viver | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 45 | `L-c8b5d8004b37bea1` | teia da sociobiodiversidade lanca nova chamada de apoio a projetos de desenvolvimento sust | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 46 | `L-ff002c66cbb41c0e` | apoio a iniciativas culturais dos povos indigenas na amazonia brasileira | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 47 | `L-f3550c93b4b4e34d` | edital fundo casa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 48 | `L-e58c870124e0d484` | inscricoes abertas para o 7o congresso hemisferico de captacao de recursos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 49 | `L-ee117aef867eecc9` | membros abcr tem 30 de desconto em curso sobre inscricao para premios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 50 | `L-dc1a5d6afea90ade` | inscricoes abertas para as bolsas da diversidade da conferencia afp | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 1 | `L-fec11ae0278228de` | Editor de emendas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 2 | `L-29a6cf172723d91d` | Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 3 | `L-5f920baf3048171f` | Receitas e Despesas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 4 | `L-c86150656d3d09a0` | Serviço de Informação ao Cidadão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 5 | `L-818ef641c5ff20fc` | Corregedoria | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 6 | `L-430028f9651e96a5` | Sistema Eletrônico de Informações - SEI | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 7 | `L-9c55682ae51a6c75` | Canais de Atendimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 8 | `L-4a3709af175b82f3` | acessoainformacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 9 | `L-2ea3803ca7bf4f6a` | Desenrola Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 10 | `L-1a66abf4427168b5` | Competências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 11 | `L-55f24efa6daf9bc8` | Horário de Atendimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 12 | `L-bee362b69f2e66be` | Manual Operativo de Acordo BIRD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 13 | `L-d710b67ad931dd85` | Receita e Despesas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 14 | `L-ebc32952a9dc3016` | Despesa Pública | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 15 | `L-165c530a13d68f93` | Notas Fiscais Eletrônicas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 16 | `L-61334f80f5442ee8` | Cartilha de Integridade para Licitantes e Contratados | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 17 | `L-8cac7545dbab3dcf` | Transparência e Prestação de Contas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 18 | `L-06219e74b5df5cf2` | Calamidades Públicas e Emergências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 19 | `L-8c5a0d15dd882945` | Bolsa Família | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 20 | `L-b35fa3bd6b9d337b` | Regra de Proteção | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 21 | `L-3e15350a0c7543f1` | Termo de uso | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 22 | `L-e7869f13251f4dbe` | Benefícios Assistenciais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 23 | `L-90273f00e97ca70a` | Quero Aprender | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 24 | `L-64e3ba59437e98ec` | Programa de Aquisição de Alimentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 25 | `L-5e4eafc4c6ec92ba` | Programa Nacional de Agricultura Urbana e Periurbana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 26 | `L-5967b6a9d39ec5ef` | Promoção da Alimentação Adequada e Saudável | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 27 | `L-9ae03fab4ac0f9b9` | Segurança Alimentar e Nutricional no SUAS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 28 | `L-aca6f367f67162d5` | Alimenta Cidades | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 29 | `L-9aa4920dff2c80f0` | Cozinha Comunitária | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 30 | `L-b7783c81abc2fbe6` | Restaurante Popular | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 31 | `L-b2bfa0cec2f438fb` | Cadeia de Valor | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 32 | `L-22288ab125ae769b` | Primeira Infância | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 33 | `L-813f1c8ba66c0fdd` | Canal de Denúncias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 34 | `L-c0ccd2008f61967b` | Denúncia de fraude | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 35 | `L-2233f13ecabe76eb` | Modalidade de Licitação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 36 | `L-3ec6aaa03ef78ad2` | Processo Seletivo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 37 | `L-9b3b89cb4128b49f` | Secretaria de Avaliação, Gestão da Informação e Cadastro Único | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 38 | `L-8881a446f03d770c` | Buscar serviços por | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 39 | `L-dcc51bdfb7f4e331` | Demais segmentos (ONGs, organizações sociais, etc) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 40 | `L-dc36d3b30f2d5a4a` | Orçamento Nacional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 41 | `L-791fd7382768ca6e` | Serviços para Imigrantes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 42 | `L-3b8ccd27be80c919` | Educação Profissional para Jovens e Adultos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 43 | `L-3b4979deee13e3d6` | Combate à Discriminação Racial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 44 | `L-e6c6555f11fad4bc` | Saúde Reprodutiva da Mulher | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 45 | `L-247aa2dfbd621a0d` | Controle de Poluição e Resíduos Sólidos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 46 | `L-d43e7cd709f2bb1a` | Acessibilidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 47 | `L-713c890cc781394e` | Órgãos do Governo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 48 | `L-f3e12374ca4d39eb` | Ajuda para Navegar o Portal | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 49 | `L-5f5b0deac39472f8` | Governo Digital | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 50 | `L-52ee307017e870dd` | Dados da Administração Pública Federal | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 1 | `L-c16a6a23011fc960` | 1Assinatura Eletrônica | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 2 | `L-03d7acf31566500f` | 4Consultar CPF | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 3 | `L-c4f8a6f84740c4ea` | OutrosTela Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 4 | `L-ffeb101f4f38fde4` | CrimesCelular Seguro | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 5 | `L-118766fab9c97a28` | Curso online Agricultura Urbana e Periurbana está disponível no Portal Capacita MDS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 6 | `L-6f319c8b9f950429` | OfícioCircularDiretrizes institucionais sobre as condutas vedadas e regras durante o perío | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 7 | `L-61dbc8beb1eacb24` | Aos Integrantesdo MDSOrientações, regras e condutas vedadas para agentes públicos e colabo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 8 | `L-2193cd41304787b7` | Áreas Protegidas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 9 | `L-f8d8db2da0fc3299` | Comissão Nacional de Biodiversidade - Conabio | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 10 | `L-fd71ca4ff74c16fb` | Patrimônio Genético | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 11 | `L-9a1f029c9447638f` | Política Nacional de Pagamento por Serviços Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 12 | `L-fd21904d6fef90d7` | Planos de Prevenção e Combate ao Desmatamento - PPCD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 13 | `L-50a0d83278a75548` | Agenda Ambiental da Administração Pública (A3P) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 14 | `L-10f7b226de0f0ff7` | Cidadania Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 15 | `L-a9281a5cc950b5d1` | Política Nacional de Educação Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 16 | `L-70a3d885e1e25227` | Agricultura Urbana e Periurbana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 17 | `L-a7c588def161320c` | Cidades Verdes Resilientes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 18 | `L-ed88e603a7e41473` | Emergências Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 19 | `L-4bb699c906915a73` | AdaptaCidades | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 20 | `L-f7657ba22a5be916` | Estratégia Nacional para a Conservação e o Uso Sustentável dos Recifes de Coral – ProCoral | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 21 | `L-d52d51ad80e08aed` | Gerenciamento Costeiro – GERCO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 22 | `L-84d0178dd7312c5d` | Povos e Comunidades Tradicionais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 23 | `L-35ae59c0fe55e212` | Petróleo e gás | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 24 | `L-8eccff9b92cb6fa8` | 1.3. Base Jurídica da Estrutura Organizacional e das Competências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 25 | `L-8a375fc79da4b349` | 1.8 Histórico Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 26 | `L-b8c855780b2ebbd2` | 2.3. Concessões de Recurso Financeiros ou Renúncias de Receitas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 27 | `L-711b0ace057d61e6` | 3.3 Conselhos e Órgãos Colegiados | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 28 | `L-cd6e062b96c5e465` | 4.3. Relatórios da CGU | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 29 | `L-edf435159b43ec0e` | 4.6. Ações de Supervisão, Controle e Correição | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 30 | `L-ac3c43c0432c8460` | 5.1 Repasses e Transparências de Recursos Financeiros | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 31 | `L-c0e11ecc42555643` | 7.2. Contratos e Outras Avenças | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 32 | `L-37bd754113b87352` | 8.2. Aposentados e Pensionistas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 33 | `L-ac27d0dfcb7e8285` | 8.5. Despesas com Ações de Desenvolvimento de Servidores | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 34 | `L-f49f6c86e05c0dc6` | Lista de Servidores do MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 35 | `L-ef711582fa56512b` | 10. Serviço de Informação ao Cidadão - SIC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 36 | `L-6d996d144d909a25` | 12.2 Disponibilização das Bases de Dados Programadas para Abertura no PDA do Órgão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 37 | `L-d35df3be7d4b908c` | 14.1. Ferramenta de Pesquisa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 38 | `L-8db88bd10b999f72` | Análise de Impacto Regulatório (AIR) e Avaliação de Resultado Regulatório (ARR) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 39 | `L-d4d31a727e42f1e3` | Relatórios de AIR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 40 | `L-893cf31b8822c026` | Termos de Execução Descentralizada | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 41 | `L-f26f7c962c704adb` | O que temos para você | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 42 | `L-f5f4d76bd11b8976` | Acordos de Cooperação MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 43 | `L-904462a8342eae1b` | Assessoria Especial de Assuntos Internacionais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 44 | `L-36d72d0682a10b8e` | Subsecretaria de Planejamento, Orçamento e Administração | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 45 | `L-fa190715043b480f` | Secretaria Nacional de Biodiversidade, Florestas e Direitos Animais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 46 | `L-6b45de054d1a0b8a` | Departamento de Proteção, Defesa e Direitos Animais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 47 | `L-2bab8ad23078cc27` | Departamento de Políticas de Estímulo à Bioeconomia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 48 | `L-f88e2609f7436065` | Departamento de Políticas de Controle do Desmatamento e Incêndios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 49 | `L-9709fb3b75c0a13f` | Departamento de Qualidade Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 50 | `L-f8320e4d0cadca37` | Departamento de Recursos Hídricos e Meio Ambiente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 1 | `L-8cfe3e3230c76cca` | Departamento de Políticas de Mitigação e Instrumentos de Implementação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 2 | `L-7539fb0874ba4a3a` | Departamento de Instrumentos de Mercado e REDD+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 3 | `L-db1fd0c0052f0d12` | Departamento de Políticas de Gestão Ambiental Rural | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 4 | `L-9f94479ee65a1abf` | Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis - Ibama | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 5 | `L-5bbdb56d3c530016` | Fundo Nacional do Meio Ambiente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 6 | `L-73e39d4e63acb246` | Conselho Nacional de Recursos Hídricos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 7 | `L-33000ef36396e3cc` | Comissão Nacional de Combate à Desertificação – CNCD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 8 | `L-fb45540c06ec9d73` | Painel Resolveu? (CGU) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 9 | `L-2b7c7e9eed3e709a` | mma-apresenta-estudo-do-plano-de-ar-limpo-e-clima-e-debate-governanca-regional-com-mexico- | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 10 | `L-bb9814a8e1534079` | Saiba mais sobre MMA informa mudanças nos canais institucionais durante o período de defes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 11 | `L-72a470776da833e9` | Saiba mais sobre Aeronaves federais lançam mais de 1 milhão de litros de água no combate a | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 12 | `L-66b178ef60b4d15a` | Ministro do Meio Ambiente e autoridades do Amazonas reforçam ações conjuntas contra incênd | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 13 | `L-5dc7bf02e9c70c84` | 5º leilão do Eco Invest Brasil tem R$ 49,95 bilhões homologados para seis setores produtiv | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 14 | `L-ffda171a012930f2` | Ministério dos Direitos Humanos e da Cidadania | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 15 | `L-57dcf8d3cca5d773` | Renúncia de Receitas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 16 | `L-5a2de51a70c7bd38` | Plano Anual de Atividades de Interna (PAINT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 17 | `L-99c5c21dfdfc02be` | Dispensas - 2025 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 18 | `L-fc3ecfd8ae0f8ef4` | Painel de Dados da ONDH – Tutoriais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 19 | `L-c26821ad66f983b6` | Ferramentas e Aspectos Tecnológicos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 20 | `L-b82656fa88bb80d0` | Cadastro das Centrais de Intérpretes de Libras (CadCIL) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 21 | `L-f211d666540cbb38` | Comitê Intersetorial de Acompanhamento e Monitoramento da Política Nacional para a Populaç | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 22 | `L-d389bdf4908f0cb7` | Coordenação-Geral da Comissão de Anistia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 23 | `L-a9aa3ebc822c0cb4` | Coordenação-Geral de Políticas de Memória e Verdade (CGPMV) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 24 | `L-1dca670e073bfaf6` | Estatísticas do Registro Civil – Casamentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 25 | `L-2ad19b12cf02f8d1` | Levantamentos Nacionais do SINASE | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 26 | `L-12d90837278954e0` | Observatório Nacional dos Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 27 | `L-793dce22a4b42dbb` | Painel de Dados da Ouvidoria Nacional de Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 28 | `L-d5015bf8e67131d5` | Pesquisa de Informações Básicas Estaduais (Estadic) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 29 | `L-ce5ba437cf831de8` | Programa de Proteção a Crianças e Adolescentes Ameaçados de Morte (PPCAAM) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 30 | `L-c6f0741d7374ccec` | Registro Civil de Nascimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 31 | `L-97dae8ff171ec338` | Sistema Nacional de Adoção e Acolhimento (SNA) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 32 | `L-c5bac8b501ea85be` | Tecer Direitos Humanos-Rede Nacional de Educação em Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 33 | `L-ff030c792cac7de2` | Passo a passo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 34 | `L-17e8481e822608d6` | Política de Privacidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 35 | `L-7e51d172a23c403a` | Programa de Privacidade e Segurança da Informação (PPSI) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 36 | `L-b332b6d13cb7d5c3` | Redes Sociais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 37 | `L-34e143d1fe8ac819` | Encarregado pelo Tratamento de Dados Pessoais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 38 | `L-ab484f057e646e83` | Navegue por temas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 39 | `L-e6ab083ac56eca55` | Organização dos Estados Americanos (OEA) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 40 | `L-376d089bb8f2292a` | Comissão de Anistia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 41 | `L-3862558b8f378141` | Educação em Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 42 | `L-1230eac90bb2850d` | Adesão à Política Nacional dos Direitos das Pessoas LGBTQIA+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 43 | `L-51fb65c418f6b60c` | Memória e Verdade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 44 | `L-7ec6211408e99a0d` | Mortos e Desaparecidos Políticos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 45 | `L-0ad82a9e66884aa8` | Auxílio Emergencial às ILPIs - Lei 14.018/20 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 46 | `L-a4c034268d0011cc` | Rede Nacional de Gestores Estaduais em Direitos Humanos da Pessoa Idosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 47 | `L-30a30344149a4c33` | Avaliação Biopsicossocial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 48 | `L-d0a3b6cca49d5792` | Protocolar documentos junto ao Ministério dos Direitos Humanos e da Cidadania (MDHC) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 49 | `L-92d4d1aac94b134f` | Registrar Ameaça de Morte contra Criança e Adolescente (PPCAAM) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 50 | `L-fb2d642333f39a9a` | Como realizar ajustes na solicitação de Adesão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 1 | `L-92b7f3e3074a7727` | Tutoriais em vídeo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 2 | `L-7298b4b607228a78` | Pró-DH (Repositório) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 3 | `L-f515b6f3c41c7cb2` | Parecer 1 - Grupo De Amigos Da Vida | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 4 | `L-b0d5213727cd0b1f` | Parecer 4 - Associação Conecta Natureza Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 5 | `L-b88ba66eacb50f5c` | Recurso e resposta - ELOE Improcedente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 6 | `L-6ff89a5468f9e5fe` | FAPEMIG — editais de fomento à pesquisa em Minas Gerais | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 7 | `L-b0992118e27c1217` | CNPq — chamadas públicas de pesquisa e bolsas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 8 | `L-0a9de2eed246c902` | PL 3087/2026 — Altera a Lei nº 13.019, de 31 de julho de 2014 (Marco Regulatório das Organ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 9 | `L-8f18e3e515f0a69f` | PL 1797/2026 — Altera a Lei nº 13.019, de 31 de julho de 2014, para assegurar a transparên | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 10 | `L-f959434eb54fc6d9` | .css-d102py{margin:0;font-family:"Roboto","Helvetica","Arial",sans-serif;font-weight:400;f | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 11 | `L-3dc0987693f9dacf` | Grant Opportunities | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 12 | `L-d96bac1d11593238` | Ford Global Fellowship | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 13 | `L-3a72ceda00f6516b` | These videos break down the essentials of grantmaking | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 14 | `L-e0b249894c3d850f` | Our Grantees | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 15 | `L-0f59c96c08f9b952` | Big Bets Fellowships | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 16 | `L-6d2131c15280f6ee` | Fellowship Application | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 17 | `L-37ff6fc4c21ecd2d` | Recoverable Grants FAQ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 18 | `L-94d0b18f0aca0029` | Grant-making process | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 19 | `L-e35671ad4e839b31` | União Europeia – Erasmus+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 20 | `L-9cbf027fdb739206` | Ford Foundation | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 21 | `L-6a3b7134a4f15614` | Global Fund for Women | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 22 | `L-be372d219c06002d` | Skoll Fellowship | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 23 | `L-581976285385c965` | Edital FETEC 2026: Credenciamento para Artistas e GruposR$ 20 mil | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 24 | `L-c9790611977f3b93` | Edital Dança São José dos Campos 2026: Guia Completo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 25 | `L-829babbc5d5a0a0f` | Edital CMDPI Godofredo Viana 2026: Guia de Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 26 | `L-652b8cbc7b3b7333` | Edital ECAU Uberaba 2026: Credenciamento de Professores | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 27 | `L-57f934ae5dbb8599` | Edital CMDPI Barrocas 2026: Chancela de Projetos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 28 | `L-f05697924ca0bdca` | Edital Cultura Popular FCCR 2026: Guia de CaptaçãoR$ 4 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 29 | `L-65c7a4884dee153a` | Edital CMDPI Santaluz 2026: Guia de Captação e Prazos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 30 | `L-2f84dc7c3844ef17` | Edital CMDCA Santaluz 2026: Guia de Chancela de Projetos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 31 | `L-42eae0617ce0dd2f` | Edital CMDPI Teofilândia 2026: Guia de Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 32 | `L-5a342cd6e2a834c6` | Edital BIP FIA 2026: Guia de Captação e Financiamento | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 33 | `L-6bccd8c447ef6bb1` | Edital FCCR: Circulação Artística e Audiovisual 2026R$ 4 mil | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 34 | `L-9a1dd0cac552d631` | Edital BIP Esporte 2026: Guia Completo para Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 35 | `L-a92b51c3da50983a` | Edital Catalisar 2026: Guia de Captação da FCC S.A. | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 36 | `L-eda055d55b5425eb` | Edital CELESC 001/2024: Captação Cultura até 2026até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 37 | `L-f53c83da7b790f1e` | Edital UEMS 020/2026 Cultura: Captação Sem Ônusaté 01 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 38 | `L-55702f5f25670b2b` | Edital CMDCA Santaluz/BA 2026 - Registro de Entidades | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 39 | `L-b57deed3cb4569ae` | Edital Intervenção Artística FCCR 2025 / Circulação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 40 | `L-ebbc0a7d6231003f` | Prêmio Liga STEAM 2026: Inscrições ProrrogadasR$ 25 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 41 | `L-c2bac4ba6e1faf53` | Edital PRONAS/PCD 2026: Guia de Captação do Min. SaúdeR$ 4,0 mi·até 26 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 42 | `L-a28918fa032de6bc` | Edital Ministério da Saúde 2026: Preceptoria SUSaté 11 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 43 | `L-75cc37cc38a22f0e` | Edital FAPEMIG 2026: Cadastramento de Instituições | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 44 | `L-ed5b7c24b06910d6` | Edital Ciclo de Saberes 2026: Guia de Captação MinC/MECR$ 500 mil·até 08 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 45 | `L-7f3db9f28b584ac2` | Edital Biblioteca Comunitária é Cultura Viva 2026 MinC | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 46 | `L-f39af2f40d87ca90` | Captação de R$200 mil no edital CNPq 34/2026 – Guia 2026R$ 200 mil·até 04 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 47 | `L-d361d198215ed76c` | Edital Acelere o Relógio da Igualdade 2026: R$ 30 milR$ 30 mil·até 11 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 48 | `L-b5fcc8326f0ee1ba` | Edital Brigadas Fundo Casa 2026: R$ 20 mil para ONGsR$ 20 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 49 | `L-572ddc6ef94c32b4` | NIH RFA-DA-28-013: NExUS Collaboratory Funding 2026até 09 de fev. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 50 | `L-9eb9bf401231b13e` | Chamada de Propostas FAPESP‑Instituto Pasteur 2026 Brasilaté 04 de mar. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 1 | `L-a66dd8b5d0cfef32` | Chamada Pública CISAMSF 003/2026 – Saúde e Social | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 2 | `L-a4e2f6eb6b20bbeb` | Chamamento Público Consirc 2026 – Oportunidades em Saúde | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 3 | `L-e2cdc0b3af88a3a2` | Chamamento Público 31/2026 Novo Horizonte do Oesteaté 13 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 4 | `L-bd3957e2fd4bbdaf` | Edital AVISO DE CHAMADA PÚBLICA 2/2026 – AgriculturaR$ 3,0 mi·até 22 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 5 | `L-fd06000152e5ae52` | Edital Padre Bernardo 2026: Saúde e Credenciamento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 6 | `L-c0f15387994f534c` | Chamamento Público Saúde Grande Sarandi 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 7 | `L-c81f486b9be30036` | Edital Instituto Genésio A. Mendes 2026: Guia de CaptaçãoR$ 30 mil·até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 8 | `L-d1119ece1e545bf6` | Edital Fapesq Embrapii Paraíba 2026: Inovação e R$ 200 milR$ 200 mil·até 07 de nov. de 202 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 9 | `L-d43bc3b440d5ea9c` | Edital 04/2026 Floresta Viva – Águas do São FranciscoR$ 17,8 mi·até 04 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 10 | `L-4034f171bda33e78` | Chamada Rio Doce 2026: captação de R$ 23 mi do BNDESR$ 23,0 mi·até 30 de dez. de 2026 | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 11 | `L-bdf3dbbeaa1ef94a` | Edital Campus Itaquaquecetuba 2026: Captação Abertaaté 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 12 | `L-daaafc00b81b3db1` | Edital Campo Belo 2026: Credenciamento Saúde | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 13 | `L-fb1cf0c207bbc0d7` | Edital Chuvisca 2026: Guia de Captação e Credenciamento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 14 | `L-b82dcc8da89ad5dc` | Chamamento Bacias PCJ 1/2026: Guia de Captaçãoaté 28 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 15 | `L-d0b88506098fec28` | Edital de Medicamentos 2026: Guia de Inovaçãoaté 23 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 16 | `L-f6a39eaeaff63574` | Edital SEINFRA SEGEP 2026: Guia de Captação para OSCsR$ 1,5 mi·até 23 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 17 | `L-f75c1cbf7deda416` | Chamamento Público Alcântara 2026: Guia de Inscriçãoaté 30 de set. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 18 | `L-b471f7ca97960b9f` | Edital SESI 2026: Direção de Arte SESI Lab / Capitaai | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 19 | `L-e210ecc20a95c6bd` | Chamamento CRBM 4ª Região 2026: Guia de Captação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 20 | `L-6854fc20488dde53` | FAPESP Young Investigator Grant 2026: Guia de CaptaçãoR$ 2,5 mi·até 19 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 21 | `L-a49b7bb5028f2927` | Chamamento CRBM-4 2026: Guia de Captação e Edital | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 22 | `L-d78de030c4fa6656` | Edital Chamada Pública 6/2026: Guia de Captaçãoaté 06 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 23 | `L-edef940981ee0243` | Edital FME Transforma 2026: Como Captar R$ 1 Milhão - GuiaR$ 1,0 mi·até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 24 | `L-f637b1e0f20b1db2` | Edital Carmo do Rio Verde 2026: Guia de Captaçãoaté 18 de set. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 25 | `L-cb75304d818e080c` | Chamada Pública Merenda Escolar 2026: Guia de Aplicação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 26 | `L-b3ab31e653906af0` | Edital FCCR 006/2024: Coro Sinfônico de SJC 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 27 | `L-aa84047bfc0fb860` | Edital FUNBIO 2026: Apoio a UCs no Litoral do Paranáencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 28 | `L-2084252d3dc13cc8` | Edital Fapes/CNPq/Capes 22/2026 – Programa PROFIX-CBencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 29 | `L-2622c94c01a321bc` | Edital FAPESPA 2026: Guia Completo para Submissãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 30 | `L-521fb053365ab694` | Edital IX CBUC Fundação Grupo Boticário 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 31 | `L-a1e90bee73584c16` | Edital Aviso de Chamamento Público 1/2026 – Culturaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 32 | `L-af9c71baa3aef7c5` | Edital IPEA/PIPA 33/2026: Bolsa de Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 33 | `L-add30b67272564b1` | Edital APC Consulado do Japão 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 34 | `L-654fa4b9d5727ce5` | Chamamento Público 1/2026: Conselho Federal de Educaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 35 | `L-260cc2a27fafb757` | Edital FAPERO 2026: Iniciação Científica e Tecnológicaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 36 | `L-ad82163e3702f576` | Edital CRO-BA 2026: Imóveis para Locação em Teixeiraencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 37 | `L-a6229e6c345956a0` | Chamada Pública Doutor Pedrinho 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 38 | `L-fe7ce81921877417` | Edital Brejo Santo 2026: Guia de Credenciamento em Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 39 | `L-fd272500cb106222` | Edital First Solar Toledo Community Foundation 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 40 | `L-217ec5ecc81f2c80` | Chamamento Público Saúde Ielmo Marinho 2026: Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 41 | `L-183825263590a6ee` | Chamada Pública Poá 2026: Aluguel para CAPS IIencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 42 | `L-377c1e15577763bf` | Edital Itapuranga 2026: Guia de Habitação e Inscriçõesencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 43 | `L-4f8100d64495f9ab` | Edital Praia Grande 2026: Guia de Captação Culturalencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 44 | `L-72b57e1532241f9f` | Edital CAU/BR 2026: Credenciamento para Habitaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 45 | `L-e59a7118b57f77ca` | Edital Sobral 2026: Projetos Culturais e PNABencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 46 | `L-bb6fccb00e013bc8` | Edital SEJUS-PI 2026: Guia de Captação para ONGsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 47 | `L-2cc63d6ef611723c` | Edital SERPRO 2026: Chamamento Público para Tecnologiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 48 | `L-95fed914f55cf009` | Chamamento Público Lagoa do Ouro 2026: Edital de Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 49 | `L-b681bc3d86a3bf8c` | Chamada Pública Viçosa 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 50 | `L-da15e241ee64f623` | Edital Silvânia 2026: Guia de Inscrição e Recursosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 1 | `L-c20be6cb58697a10` | Chamada Pública Sulina 2026: Guia para Produtoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 2 | `L-473ddbc6de3c8c00` | Edital Alfenas 2026: Guia para Captação em Habitaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 3 | `L-357a6d475e17ef68` | Chamada Pública Grupo Hospitalar Conceição 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 4 | `L-d9d84cde3796ad72` | Edital Balsas 2026: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 5 | `L-a286020146c3754b` | Edital FAPEG Goiás pelo Mundo 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 6 | `L-4922caa885f3fe26` | Edital Tauá 2026: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 7 | `L-debece7a606f0969` | Edital FAPESP ANR 2027: Pesquisa Bilateral até 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 8 | `L-5da7d260c5a02967` | Edital Agricultura Familiar São Luiz do Norte 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 9 | `L-de9ed5d8a621b2e3` | Chamada Pública Reitoria 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 10 | `L-48b4ea0a302208da` | Edital FAPESP T-AP 2026: R$ 600 mil para Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 11 | `L-e8858ecdba47c0b0` | Edital Chamamento Público 6/2026 4ª Diretoria: Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 12 | `L-7987f3fc4af47f06` | Edital Acelera Campo 2026: R$ 60 mil para Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 13 | `L-950e17c1ceb8b45b` | Edital Marinha 2026: Guia de Permuta e Imóveis Ociososencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 14 | `L-03c2624ac9939daf` | Edital Fapes 20/2026: Bolsa Pós-Doutorado Sêniorencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 15 | `L-ffcd6ac0f7997144` | Edital Acaraú 2026: Chamamento Público para Leiloeirosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 16 | `L-652a7da44f29f6d2` | Chamada Pública Merenda Escolar 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 17 | `L-d53181e9379c2d96` | Edital Pitangueiras 2026: Projetos Musicais PNABencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 18 | `L-1832a115c196ecb0` | Edital FAPESPA 008/2026: Guia de Captação e Prazosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 19 | `L-19396768923f3b16` | Chamamento Público DSEI Cuiabá 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 20 | `L-755859ee90a2d223` | Edital Fundo Ecos 2026: R$ 3,3M para a Amazônia Legalencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 21 | `L-1451b1b4b560464a` | Chamada Pública IFTM 2026: Guia Completo para Editaisencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 22 | `L-3f2008d5cd1dccf2` | Edital DAAD 2026: Auxílio Doutorado Brasil-Alemanhaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 23 | `L-7a302c1590f8354f` | Edital Fapeg 14/2026: Indicações Geográficas em Goiásencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 24 | `L-f4ca070ac332b7ea` | Edital FAPERJ 04/2025: Hub RJ Startup 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 25 | `L-c0eba72aa5c48bab` | Edital Amazônia Legal Tocantins 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 26 | `L-70cc069c6f5191f5` | Edital PROFIX-CB FAPESPA 2026: Fixação de Doutoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 27 | `L-f8aa6df74f942e30` | Edital Okavango National Geographic 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 28 | `L-540d821b401267c3` | Edital FAPERJ Ciências Agrárias 2026: Como Aprovarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 29 | `L-c5bb572ec5f5b28e` | Edital iCS Comunicação Climática 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 30 | `L-4837326b3c4eafff` | Edital Dia de Doar 2026: R$ 2,4 mil para Campanhasencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 31 | `L-0392ec1f05beeeba` | Edital FAPESB/SECTI/IEL 004/2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 32 | `L-4b93f2c39df9fb60` | Edital Vital Strategies Saúde Mental 2026: R$ 800 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 33 | `L-92b0f183dc84e52f` | Edital Patrimônio Cultural Brasil-Holanda 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 34 | `L-42f07d174f1a6670` | Edital Clima e Sociedade 2026: R$ 500 mil para Comunicaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 35 | `L-3547cc4a0b41c4d6` | Edital Fundo Brasil 2026: R$ 60 mil para Amazônia e Cerradoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 36 | `L-8a9db9b874593590` | Edital FAPEG 2026: Mobilidade Internacional em Eventosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 37 | `L-6ccbb3419a0ee039` | Edital FAPEMIG 15/2026: Laboratórios Certificadoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 38 | `L-aa46134dd3f77be1` | Edital FAPESC 40/2026: Inovação e Tecnologia em SCencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 39 | `L-a9fcb4a183ad0d27` | Edital Coletivo Periférico 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 40 | `L-6062bdc25c73a470` | Edital FAPITEC/SE 2026: Auxílio para Eventos PRAPECencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 41 | `L-6ef7134d1b6ab2f3` | Bolsas de Filantropia Ford 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 42 | `L-65ba654531b1bd7c` | Edital PEC-PG 2026 CNPq/CAPES/MRE: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 43 | `L-17cb45df0407631f` | Edital Itaú Viver Mais 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 44 | `L-9e62a8a9e4300981` | Edital Fundo Socioambiental CAIXA 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 45 | `L-7d1d9b24bcca3786` | Prêmio Pacto Contra Fome 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 46 | `L-a3a033a05892d142` | Edital Petrobras Reciclagem de Óleo 2026: Como Aplicarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 47 | `L-afa163cee9f19409` | Edital FAPESC/EPAGRI 49/2026: Bolsas em Agropecuáriaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 48 | `L-80edc142f117d83c` | Edital CNPq/ERC 21/2026: Guia Completo e Como Aplicarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 49 | `L-25ad60da38698839` | Edital Mulheres que Transformam o Futuro 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 50 | `L-318c9748cd1ea723` | Edital Instituto ACP 2025: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 1 | `L-aa89dce465ac0afd` | Edital Mães Cientistas Facepe 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 2 | `L-1379d21714f8e47f` | Edital Ambev 2026: R$ 67M para Cultura e Esporteencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 3 | `L-c1799d97b19a93f7` | Edital MICSUL 2026: Inscrições no Ministério da Culturaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 4 | `L-78b2a429ec04148a` | Edital FAPESC/SEF 48/2026: Pesquisa e Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 5 | `L-eb132e78d56e0a5f` | Chamamento Público DSEI Porto Velho 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 6 | `L-304331cb42bdbe01` | Edital Compet Mulheres Facepe 2026: R$ 200 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 7 | `L-84b932fab4c2497c` | Edital MinC Rouanet Centro-Oeste 2026: R$ 650 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 8 | `L-16428b829db29fe8` | Edital FAPERJ Agro do Futuro 2026: R$ 2,5M para Foodtechsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 9 | `L-148954448c0f66f4` | Edital FAPEAP 003/2026: R$ 3,8M para Redes de Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 10 | `L-659b103b585eacbc` | Edital FAPESB/SECTI 2026: R$ 10 Milhões para Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 11 | `L-126b0d4a70619d33` | Edital Amazônia+10 2026: Como Captar Recursos de P&Dencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 12 | `L-40a9c50de52aa61a` | Edital FAPESC 37/2026: Apoio a Grupos UDESCencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 13 | `L-63f38638fcbcd620` | Edital FAPESB 009/2026: Apoio a Eventos Científicosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 14 | `L-f4f9d9228f11bf9d` | Edital MDA Agricultura Familiar 2026: R$ 500 mil para OSCsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 15 | `L-5c1eaf8526c44d24` | Edital Bracell Social 2026: R$ 600 mil para ONGsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 16 | `L-bc490b45a302c4bf` | Fundo Ecos 2026: Edital para Territórios Indígenasencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 17 | `L-2134a33d8355cc3b` | VOA 2026 Ambev: Edital Inclusão Produtivaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 18 | `L-3929ad88ba608d7d` | FAPERJ 2026: Edital Infraestrutura Hospitais Universitáriosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 19 | `L-db17f96150cffb14` | Edital Fapeg Mestrado Internacional 2026 / Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 20 | `L-18d816ea11019113` | Edital Zilor 2025: Banco de Projetos Incentivadosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 21 | `L-5380b833ff4e27c0` | FAPESC/CIASC 045/2026: Edital P&D Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 22 | `L-fa93cd7e0ab2072b` | CNPq 18/2026: Edital de Avaliações em Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 23 | `L-d3129baf79e5a572` | Chamada CNPq 07/2026: guia completo de bolsas deencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 24 | `L-bd146111cabac6c7` | Guias de editais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 25 | `L-eb2dde3fb7a231c2` | instituto equatorial abre inscricoes jornada capacitacao gratuita oscs 6okgyj | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 26 | `L-ecfb766cb3ca9d3b` | Pesquisa Doação Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 27 | `L-e101015f9a56b2ce` | Chamada de Projetos: Fundo Casa apoia fortalecimento de comunidades tradicionais na Amazôn | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 28 | `L-a35da72fc8f763bf` | ProgramaJá É: Fundo Baobá abre inscrições para jovens negros que querem acessar o ensino s | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 29 | `L-d328ecec135b1bbf` | Chamada de Projetos – Teia da Sociobiodiversidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 30 | `L-0b520f43fd339c5d` | project proposal guidelines | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 31 | `L-e38ee5c4af046c22` | blank project proposal form | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 32 | `L-f813a22a67bb6608` | How to Apply - Online Project Proposal System | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 33 | `L-a619afa8d4c32af6` | Technical Guidance - Online Project Proposal System | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 34 | `L-edbfa35456279645` | Mapa das OSC - Editais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 35 | `L-b3f9565a48c3980d` | RoadSafe: Road Safety Grants Programme: Call for Proposals – Safer Road Users and Safer Ve | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 36 | `L-36b7b5365118eb50` | Calls for proposals - Fundo Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 37 | `L-437013a02568dc66` | Call for Proposals: Communication for Climate Action Grants (Brazil) ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 38 | `L-c54e454642824d47` | Organizações da sociedade civil já podem se inscrever no 2º Edital ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 39 | `L-eda7efdf9e3c38ad` | EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS  (APOIO DIR | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 40 | `L-e70d80aa8c4d8522` | EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - MAPEAMENTO, DIAGNÓSTICO E PAINEL DE DADOS CULTU | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 41 | `L-f126270a6904147a` | EDITAL DE CHAMAMENTO PÚBLICO Nº 26/2026 SELEÇÃO DE PROJETOS PARA FIRMAR TERMO DE EXECUÇÃO  | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 42 | `L-f2fbd3483ac8b040` | EDITAL ABERTO A Plan International Brasil está oferecendo R ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 43 | `L-39a09e0e553acd09` | Call for Proposals: Small Grants Programme for Civil Society ... | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 44 | `L-934c20ad7ab817f7` | copa-de-futebol-feminino-2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 45 | `L-2d0d511e499cbed8` | Relatório Semestral | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 46 | `L-416d9cc814fbc2b0` | Operação Acolhida | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 47 | `L-47f74bc000e00d6d` | Operação Rio Grande do Sul | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 48 | `L-2801c01f40c20ed0` | Calendário 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 49 | `L-887ce50272f846ae` | Qualidade Ambiental e Meio Ambiente Urbano | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 50 | `L-631dcfb904a02204` | Últimas notícias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 1 | `L-dd5980032f620770` | Prêmio de 25 Anos do Cadastro Único | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 2 | `L-05902c3624c84c6f` | Agricultura e Pecuária | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 3 | `L-97b78eaf198e548a` | Cultura e Esporte | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 4 | `L-fbc5e6f898c712d3` | Cidadania Marajó | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 5 | `L-249a3c601eee5658` | Fórum Permanente da Sociedade Civil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 6 | `L-fc767efe8a606715` | Infraestrutura Esportiva | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 7 | `L-3f4e21b72338484b` | Arena Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 8 | `L-8e7e15128007d627` | Programa Segundo Tempo (PST) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 9 | `L-a989107b52793954` | Academia e Futebol | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 10 | `L-32554043d885ea7e` | Programa Integra | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 11 | `L-5b864445aa666d18` | Quero Emprego | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 12 | `L-40c7858ac0f64ffd` | Plano de Ação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 13 | `L-271ad50055c0fe96` | Repositório Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 14 | `L-12814fa1f3283604` | Procedimentos de Nomeação, Posse e Exercício | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 15 | `L-752878f12e8f5aeb` | Departamento de Benefícios Assistenciais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 16 | `L-656fe9fed011c89e` | Departamento de Proteção Social Básica | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 17 | `L-25938a389c51110b` | Educação e Pesquisa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 18 | `L-6f47710f7fa4c24d` | Justiça e Segurança | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 19 | `L-a84933292951c006` | Direitos do Trabalhador | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 20 | `L-a19f987129986562` | Wellington Dias conhece tecnologia que identifica áreas para construção de cisternas e hor | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 21 | `L-0c4d49ed3f9af341` | Informações Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 22 | `L-dc9c884d829c7f48` | Mapas Interativos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 23 | `L-0cfa35035f698f4f` | Histórico dos ODS no MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 24 | `L-748612544403a1d6` | Comitê Nacional de Prevenção e Combate à Tortura (CNPCT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 25 | `L-5bc04b7b733d0ea7` | População em Situação de Rua | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 26 | `L-ff7589318a906fb1` | O Jardim Botânico do Rio de Janeiro lançou dois editais de ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 27 | `L-eb42adf5dabf817c` | Projeto Paisagens Sustentáveis da Amazônia - ASL Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 28 | `L-6ec775bf09714f34` | Marcos Normativos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 29 | `L-a6173b6dbd2c855a` | Guia Lilás - Assédio moral, sexual e discriminação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 30 | `L-5ebe00abafd87eb1` | Liberdade Religiosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 31 | `L-3465552b51d76f41` | Acervo Histórico | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 32 | `L-f72d97bb1d3dbc29` | Plano Nacional dos Direitos da Pessoa Idosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 33 | `L-fc5e494ea24dc1b8` | Promoção e Defesa dos Direitos Humanos - PRÓ-DH | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 34 | `L-d8c318dbd5e30fd4` | Emenda parlamentar federal individual | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 35 | `L-5309792d585ac69f` | MDS esclarece regras dos programas sociais e alerta para notícias falsas durante as eleiçõ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 36 | `L-836ed337f16b5b33` | Cadastro de usuários externos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 37 | `L-714a589431dae219` | Conflito de Interesse | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 38 | `L-c32a5af57f8ae855` | Impacto Regulatório | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 39 | `L-26e4546f66a65efc` | Plano de Integridade: Integra+ MDHC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 40 | `L-54e2c41506b290a0` | Caravana Federativa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 41 | `L-c37c714156c62512` | Sentenças da Corte Interamericana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 42 | `L-f8b57cdefa973090` | Publicações e Referências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 43 | `L-e4a3d532e4057351` | COMIGRAR-MDHC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 44 | `L-20413e5e58893499` | Lista de Serviços | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 45 | `L-e3fb906129cada31` | Tire suas dúvidas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 46 | `L-a4ffa381cca054c1` | Pessoas em situação de rua | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 47 | `L-4f69ce8c67ebc1b9` | Acesso à Área de Trabalho | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 48 | `L-0592e2fc63b3224b` | Nº 10/26 - Manutenção preventiva na API de consulta do PNCP no ambiente de produção entre  | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 49 | `L-e2e998f3c2621e3e` | Nº 07/26 - Indisponibilidade programada do PNCP no dia 17/6/202615/6/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 50 | `L-149f854acd94778a` | Atas de Reunião do CGRNCP | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 1 | `L-4bf029fd699ae4a9` | Catálogo Eletrônico de Padronização | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 2 | `L-449a258a09e73e48` | Central de Conteúdo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 3 | `L-e38522cca1262f53` | Contrata+Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 4 | `L-63881ff6c33ecf20` | Painel para consulta de preços em dados abertos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 5 | `L-c7b9e44a1da06476` | Cadastro Nacional de Empresas Inidôneas e Suspensas (CEIS) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 6 | `L-6722c54a288926bc` | Transparência | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 7 | `L-ed236090519897da` | Onde atuamos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 8 | `L-f3a523a34749f835` | Instituições financeiras credenciadas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 9 | `L-497f3915265652da` | Plano Brasil Soberano 2026Conheça as novas medidas de apoio às empresas afetadas pela inst | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 10 | `L-d09485aa0bcb2b67` | Serviços online | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 11 | `L-e17110f6285fc760` | Consulta a financiamentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 12 | `L-959feb20065a13b1` | Moedas contratuais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 13 | `L-1a969dc86a2e0100` | 6Obter passaporte e outros documentos de viagem | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 14 | `L-c211eab258ce2446` | 4th Call for Proposals: Brazil – gpsa | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 15 | `L-bcc7db9903c83183` | Lei de Incentivo ao Esporte - Esporte para Toda a Vida | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 16 | `L-8218fddf08e9e8cd` | Materiais e Publicações | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 17 | `L-6b7d14577f5bb994` | Manual de Gestão de TEDs do MDS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 18 | `L-fa38d2fe57d51405` | Saiba mais sobre os programas vigentes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 19 | `L-0cc3b768478357db` | Programa União com Municípios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 20 | `L-7a95333e6f3eaca6` | Campanha de Prevenção aos Incêndios Florestais 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 21 | `L-ab2d55d18657079d` | Saiba mais sobre MMA abre inscrições para representantes da sociedade civil na Comissão Na | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 22 | `L-a6433823aaadfdf1` | O Instituto Impactarte está com inscrições abertas para o ciclo 2026 ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 23 | `L-2dae61b2e5b80b7c` | Saiba mais sobre MMA atualiza lista nacional de plantas ameaçadas de extinção | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 24 | `L-13ff6591c6d68b39` | Call for Proposals / UNEP - UN Environment Programme | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 25 | `L-13a66337fad770fa` | Open grant — Call for Projects Promoting ... - DevelopmentAid | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 26 | `L-ea2dcadf3eb0b967` | EDITAL Nº009/2026-EJs/DEX/PROEC/ UEMS EDITAL DE FLUXO CONTÍNUO PARA PROJETOS DE EXTENSÃO V | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 27 | `L-2a158e5f4944f50e` | Search for grants in Brazil — DevelopmentAid | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 28 | `L-730d08e3bf38f9bb` | The Path of Grantmaking: How Brazil Fund gets resources to those ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 29 | `L-98599d1056fd7e23` | edital n° 54/2026/sei-inpa (fluxo contínuo) - GOV.BR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 30 | `L-4268cee9bd5177fa` | Edital de Abertura de Inscrições – SAEB nº 04/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 31 | `L-44261059b2360c26` | PROGRAMA FUNARTE MEMÓRIA DAS ARTES | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 32 | `L-c8d5edbc6edb484b` | Edital de Fluxo Contínuo Nº 02/2026 DEX/PROEC/UEMS (Programas, Projetos e Cursos) | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 33 | `L-5122868b5323b845` | GT discute cooperação entre assistência social e Sistema de Justiça | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 34 | `L-c29b3f393b72667e` | EDITAL Nº 003/2026 - RELATÓRIOS/EVENTOS-DEX/PROEC/UEMS | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 35 | `L-a32cc23448866a0a` | Sisan promove Encontro Regional para fortalecer a governança participativa e intersetorial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 36 | `L-2c540e9e12d76a3a` | @vanessaeobicho SEBRAE ABRE EDITAL DE R$ 7,4 MILHÕES ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 37 | `L-0c56e42ece5c3d8b` | EDITAL DE CHAMAMENTO PÚBLICO Nº 14/2026 - PREMIAÇÃO DE PONTOS E PONTÕES DE CULTURA | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 38 | `L-1431232a219af3a0` | EDITAL DE CHAMAMENTO PÚBLICO 13/2026 - FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 39 | `L-d212a3de6b2de37a` | Resultado Definitivo do Edital de Chamamento Público nº 01/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 40 | `L-30ed7ff62719905b` | Aviso de Credenciamento — AVISO DE CREDENCIAMENTO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 41 | `L-bf5ce760538b1837` | Aviso de Chamamento Público — AVISO DE LICITAÇÃO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 42 | `L-4fce280f65fec5b9` | Ministério do Esporte aprova 32 projetos para captar recursos via Lei ... | preparação | — | sem prazo | sem | 12 | expurgo? |
| 18 | 43 | `L-40ec576676f5c197` | Criança Esperança - Edital - UNESCO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 44 | `L-1180fcb520026cc9` | Chamada Aberta 2026 - Instituto ACP - Plataforma Conjunta | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 45 | `L-7adafd9f5cf784f2` | Notícias e Conteúdo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 46 | `L-99596629e238a756` | Marcas e Manuais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 47 | `L-8ca3c7315a94f6d9` | Coleção de Notícias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 48 | `L-3d1b7b54e5cd3d79` | Boletins | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 49 | `L-b8abbb6db7d287d7` | MDS Informa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 50 | `L-871c0e6ae30919b5` | Boletins Anteriores | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 1 | `L-3a7b977284ddacd1` | Condutas Vedadas Aos Agentes Públicos Federais Em Eleições | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 2 | `L-6df300e34c7ae5b1` | III Encontro do Programa Cozinha Solidária debate soberania e segurança alimentar no Brasi | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 3 | `L-6a1f09fed9e6a85e` | Adaptação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 4 | `L-024413416cefb98a` | ReCAATINGAR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 5 | `L-b5007188c1d0a855` | Plano Nacional de Desenvolvimento Sustentável de Povos e Comunidades Tradicionais (PDPCT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 6 | `L-7858087d4818d5e3` | Saiba mais sobre MMA contribui para capítulo brasileiro do relatório global sobre o estado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 7 | `L-b8ff5a9baf9506ab` | Na Frequência dos Nossos Direitos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 8 | `L-b21286bd9fc74c43` | SECOND PUBLIC CALL FOR CIVIL SOCIETY ORGANIZATIONS TO ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 9 | `L-ef64ea06fd41c7c3` | Open grant — Call for Projects to Support Kaiowá ... - DevelopmentAid | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 10 | `L-53facee2c2ef37c4` | Instituto Ronald inicia obra da 1ª Casa Ronald McDonald verde do sistema global - Diário P | preparação | — | sem prazo | sem | 6 | expurgo? |
| 19 | 11 | `L-079fc16ca2d44163` | Convocatoria de Proyectos Sociales Cooperación internacional 2026 | preparação | — | sem prazo | sem | 9 | expurgo? |
| 19 | 12 | `L-1ed918f727a5d53a` | Subvenciones 2026 para ONGs: financiamiento internacional del GFCF - Noticias con Causa | preparação | — | sem prazo | sem | 9 | expurgo? |
| 19 | 13 | `captacao-242` | PNUD – Small Grants Programme — Internacional | verificação externa | IN | sem prazo | sem | 10 | catálogo |
| 19 | 14 | `captacao-248` | Open Society Foundations — Internacional | verificação externa | IN | sem prazo | sem | 10 | catálogo |
| 19 | 15 | `captacao-250` | Gates Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 16 | `captacao-253` | Microsoft Philanthropies — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 17 | `captacao-258` | Skoll Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 18 | `captacao-260` | Oak Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 19 | `captacao-240` | UNESCO – Fundo Internacional para Diversidade Cultural — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 20 | `captacao-243` | Banco Mundial – Social Development Grants — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 21 | `captacao-244` | BID – Laboratório de Inovação — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 22 | `captacao-245` | USAID – Grants Globais — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 23 | `captacao-246` | União Europeia – Erasmus+ — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 24 | `captacao-247` | União Europeia – EuropeAid — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 25 | `captacao-249` | Ford Foundation — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 26 | `captacao-252` | Meta Community Grants — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 27 | `captacao-254` | Global Fund for Women — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 28 | `L-18a73cab13e388ed` | International Foundation Grant 2026: Complete Application Guide, Timeline, and Funding Opp | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 29 | `L-876c833a355a72f4` | Top Grant Opportunities for NGOs in 2026: Global Calls, Tips &amp; Funding Trends / Grants | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 30 | `L-23d6ecb1933088b6` | Homepage - Global Fund for Children | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 31 | `L-f35d772f5f05fcc8` | Grants for NGOs: Global Database of Funding Opportunities / GrantsDatabase | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 32 | `L-97988670a73d9d1c` | Edital FAPESPA 2026: Mapeamento Turístico Ilha do CombuR$ 544 mil | preparação | PA | aberta | prata | 3 |  |
| 19 | 33 | `L-40ba051fb8149a8e` | Chamamento Público Bálsamo SP 2026: Edital OSCIPaté 05 de nov. de 2026 | verificação externa | SP | aberta | prata | 3 |  |
| 19 | 34 | `L-11dc0e0f3a777a2a` | CHAMADA PÚBLICA 019/2026 – Diagnóstico da População IdosaR$ 543 mil·até 07 de nov. de 2026 | preparação | PA | aberta | bronze | 1 |  |
| 19 | 35 | `L-9c499faba441537f` | Edital Guaraí 2026: R$ 656 mil para Assistência SocialR$ 656 mil·até 06 de nov. de 2026 | verificação externa | TO | aberta | prata | 2 |  |
| 19 | 36 | `op-583de98c37cc` | 2º Edital Social Instituto Porto 2026: até R$ 200 mil por OSC (2 vagas, Grande SP e Grande | verificação externa | MG | aberta | ouro | 0 |  |
| 19 | 37 | `op-83594f2b678d` | Gráfica do Exército — AVISO DE CHAMAMENTO PÚBLICO Nº 1/2026 — é selecionar as associações  | recepção | DF | aberta | bronze | 1 |  |
| 19 | 38 | `L-49d853c2cd4c4a55` | chamada publica 0202026 projeto reciclagem economia circular diagnosti 0dduyb | preparação | PA | aberta | bronze | 2 |  |
| 19 | 39 | `op-863b91d555e7` | Chamamento SEJUS-PI 02/2026 (APEC em Parnaíba, Picos e Floriano; R$ 700,9 mil por parceria | recepção | PI | aberta | bronze | 1 |  |
| 19 | 40 | `L-3a84848a5c807132` | BiodivFuture 2026 – Edital FAPESB para Novos EcossistemasR$ 255 mil·até 11 de nov. de 2026 | preparação | BA | aberta | bronze | 2 |  |
| 19 | 41 | `L-e6c95a125ceb6d1a` | Edital Fundação Araucária Biodiversa+ 2026R$ 300 mil·até 16 de abr. de 2027 | preparação | PR | aberta | bronze | 2 |  |
| 19 | 42 | `op-dd4903d7e5ec` | Chamamento SEJUS-PI 03/2026 (CIAP de Altos/PI, R$ 803 mil) com prazo até 20/10/2026 confir | recepção | PI | aberta | bronze | 4 |  |
| 19 | 43 | `op-cc360a72c619` | Projetos sustentáveis no Cerrado e na Caatinga — Brasil | preparação | MA | aberta | bronze | 1 |  |
| 19 | 44 | `op-a17291a54c03` | OURO (sem repasse, nicho museológico). Edital de credenciamento do Sonhar o Mundo 2026 (SI | preparação | SP | aberta | prata | 1 |  |
| 19 | 45 | `nova-63ac222433cf` | Sonhar o Mundo 2026 abre inscrições para instituições culturais de São Paulo — Brasil | preparação | SP | aberta | prata | 2 |  |
| 19 | 46 | `L-50c619d159861208` | Edital de Chamamento Público destinado projetos sociais voltados à promoção e à garantia d | verificação externa | — | aberta | prata | 1 |  |
| 19 | 47 | `L-9714c53d1fae6b2a` | Edital 4ª Chamada Economia Azul 2026 – Fundação AraucáriaR$ 495 mil·até 14 de jun. de 2027 | preparação | PR | aberta | bronze | 2 |  |
| 19 | 48 | `L-66d5fa8939b32fff` | IFSP - Portal Institucional - IFSP - Portal Institucional | preparação | SP | aberta | bronze | 1 |  |
| 19 | 49 | `L-573e7ff053c0b798` | Edital 03/2026-DRI/UEMS. Edital de fluxo contínuo para propostas de ações de internacional | preparação | MS | aberta | bronze | 4 |  |
| 19 | 50 | `L-075b7ba9539c89c2` | Quintais Produtivos para Mulheres – Edital 04/2026 Anateraté 20 de nov. de 2026 | verificação externa | MG | aberta | ouro | 0 |  |
| 20 | 1 | `op-983526e6e043` | SUP. EST. DE LICITACAO — O presente Chamamento Público tem por objeto selecionar Organizaç | preparação | RO | aberta | bronze | 1 |  |
| 20 | 2 | `L-2dfe5adaa7808b72` | Expoagro Afubra 2027 abre inscrições para o Pavilhão da Agricultura Familiar | preparação | RS | aberta | bronze | 2 |  |
| 20 | 3 | `L-2529e074a2454eac` | Diário oficial de Mogi Guaçu (2026-10-27) | preparação | — | aberta | bronze | 2 |  |
| 20 | 4 | `L-e6b9b1a5607c82d4` | POLÍTICAS DE FOMENTORio Preto abre editais com R$ 756 mil para Pontos de Cultura | preparação | SP | aberta | bronze | 3 |  |
| 20 | 5 | `L-48e828b7e3dc4ec4` | Edital CMDCA Tubarão 003/2026 – Captação de R$200 milR$ 200 mil·até 24 de nov. de 2026 | preparação | SC | aberta | bronze | 2 |  |
| 20 | 6 | `op-ce08d2d6b36e` | MUNICIPIO DE RIO DE JANEIRO — Credenciamento de instituições privadas, sem fins lucrativos | preparação | RJ | aberta | bronze | 1 |  |
| 20 | 7 | `L-1b197365c9a028d0` | Edital SMADS 2026: Abrigo 24h em São Pauloaté 27 de nov. de 2026 | preparação | SP | aberta | bronze | 1 |  |
| 20 | 8 | `op-2f2e856a2474` | Programa Nutrir+ — Brasil | preparação | MS | aberta | bronze | 2 |  |
| 20 | 9 | `op-7eaa1477335f` | DEFENSORIA PUBLICA DO ESTADO DO PARANA — O objeto do presente credenciamento selecionar as | preparação | PR | aberta | bronze | 1 |  |
| 20 | 10 | `op-bdda6f400ec9` | IFood Chega Junto – 2ª edição — Brasil | preparação | BA | aberta | bronze | 2 |  |
| 20 | 11 | `L-fd5c67612e5c6c88` | Edital CAPES 11/2026 – Cátedra Jorge Amado 2026até 31 de dez. de 2026 | preparação | SP | aberta | bronze | 2 |  |
| 20 | 12 | `op-ccab18422744` | Edital 001/2026 de Cadastro de Projetos do Programa de Incentivo ao Esporte - PIE — Brasil | preparação | SC | aberta | bronze | 3 |  |
| 20 | 13 | `op-1bf6c28ac27d` | OURO (sem repasse). CP00126 da CPTM (São Paulo/SP): credenciamento de associações e cooper | preparação | SP | aberta | bronze | 2 |  |
| 20 | 14 | `op-4d6ae06a4182` | (UO) ESP-CIA.PTA DE TRENS METROPS-CPTM — Credenciamento de associações e/ou cooperativas d | preparação | SP | aberta | bronze | 2 |  |
| 20 | 15 | `L-20ad275e2117b5d6` | Seleção de empreendimentos de saneamento 2026 – PCJ SPR$ 12,0 mi·até 16 de mai. de 2027 | preparação | SP | aberta | bronze | 3 |  |
| 20 | 16 | `op-b69ca4f1c758` | MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO — Reabertura do Edital de Credenciamento SEE | preparação | MG | aberta | bronze | 2 |  |
| 20 | 17 | `op-e2c38bc30cbe` | MUNICIPIO DE BOA VISTA — credenciamento de Instituições de Longa Permanência para Idosos – | preparação | RR | aberta | bronze | 1 |  |
| 20 | 18 | `op-4c282607bda1` | TRIBUNAL REGIONAL ELEITORAL DO AMAZONAS — O presente procedimento tem por objeto seleciona | preparação | AM | aberta | bronze | 3 |  |
| 20 | 19 | `op-9150ca832311` | Seleção pelo TRE-AM de associações/cooperativas de catadores para Acordo de Cooperação Téc | preparação | AM | aberta | bronze | 3 |  |
| 20 | 20 | `op-185651c7ce6e` | UNIVERSIDADE FEDERAL DE PERNAMBUCO — Selecionar e habilitar as associações e/ou cooperativ | preparação | PE | aberta | bronze | 3 |  |
| 20 | 21 | `op-10a5e444491f` | DNIT-DEPARTAMENTO NACIONAL DE INFRAEST DE TRANSPORTES — Seleção de associações e/ou cooper | preparação | DF | aberta | bronze | 2 |  |
| 20 | 22 | `op-282b8b176c85` | TRIBUNAL SUPERIOR DO TRABALHO — Seleção de associações e cooperativas de catadores de mate | preparação | DF | aberta | bronze | 1 |  |
| 20 | 23 | `op-66ca048d7db5` | TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciamento de associação e/ou cooperativa | preparação | TO | aberta | bronze | 2 |  |
| 20 | 24 | `op-9c790ce7af74` | OURO (sem repasse). Credenciamento do TJTO (Projeto Coleta Seletiva Solidária) para associ | preparação | TO | aberta | bronze | 2 |  |
| 20 | 25 | `op-628b281e0b9e` | TRIBUNAL DE JUSTICA DO ESTADO DE ALAGOAS — [LICITANET] - Chamamento público na forma de cr | preparação | AL | aberta | bronze | 2 |  |
| 20 | 26 | `op-e0f66703f6ec` | OURO (sem repasse). Credenciamento 002/2024 do TJAL para associações/cooperativas de catad | preparação | AL | aberta | bronze | 2 |  |
| 20 | 27 | `op-03c70c51481b` | FUNDACAO UBERLANDENSE DO TURISMO ESPORTE E LAZER — Credenciamento de interessados (terceir | preparação | MG | aberta | bronze | 3 |  |
| 20 | 28 | `op-6b8887bef5bb` | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento TRT4 n° 01/2023 Credenciamento de associaçõ | preparação | RS | aberta | bronze | 1 |  |
| 20 | 29 | `op-f1f571748e91` | OURO (sem repasse). Credenciamento 001/2023 do TRT4 (republicado no PNCP em 2024) para ass | preparação | RS | aberta | bronze | 2 |  |
| 20 | 30 | `op-8b2f0d2c3ce4` | Edital 1/2025 do IFSULDEMINAS Campus Inconfidentes: credenciamento contínuo (desde 14/01/2 | preparação | MG | aberta | bronze | 2 |  |
| 20 | 31 | `op-07dfbfa866be` | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento de Cooperativas ou Associações de catadores | preparação | MA | aberta | bronze | 2 |  |
| 20 | 32 | `op-9c8606e47e7b` | OURO (sem repasse). Credenciamento 01/2025 do TRT16 (São Luís/MA) para cooperativas/associ | preparação | MA | aberta | bronze | 2 |  |
| 20 | 33 | `op-cc39b07683ca` | TRIBUNAL SUPERIOR ELEITORAL — Credenciamento de associações e/ou cooperativas de catadores | preparação | RN | aberta | bronze | 2 |  |
| 20 | 34 | `op-f1ca705ce530` | MINISTERIO PUBLICO DO ESTADO DO PARANA — Selecionar associação e/ou cooperativa de catador | preparação | PR | aberta | bronze | 2 |  |
| 20 | 35 | `L-795796b7b9b5e89f` | Sâmia lança edital de emendas para 2026 com foco em participação popular e transparência / | recepção | SP | encerrada | bronze | 8 |  |
| 20 | 36 | `op-4ff34a354f68` | Assistência para Projetos Comunitários e de Segurança do Ser Humano (APC) Consulado Geral  | verificação externa | IN | aberta | prata | 2 |  |
| 20 | 37 | `L-660f394c44569035` | Junte-se à Causa - ONG Banco de Alimentos | preparação | — | sem prazo | sem | 2 | expurgo? |
| 20 | 38 | `L-ba3abbbfa2d0541b` | Banrisul Instituto Cultural e Social — Edital Merece! | preparação | RS | sem prazo | sem | 3 | expurgo? |
| 20 | 39 | `L-a517e18d1a45e03a` | edital chamada publica fapesc 392026 nucleo catarinense mobilidade rh8huo | preparação | SC | sem prazo | sem | 3 | expurgo? |
| 20 | 40 | `L-cd1c83b681badd00` | edital fapesbsecticnpqcapes 112026 profix fapesb fqh8qr | preparação | BA | sem prazo | sem | 3 | expurgo? |
| 20 | 41 | `L-a3f35daeb64685e7` | Receba Doações de Alimentos para sua ONG / Optima ESG | preparação | — | sem prazo | sem | 3 | expurgo? |
| 20 | 42 | `L-63588cc5032d65e6` | 2025: Gestão e Destinação de Valores e Bens Oriundos de Prestações Pecuniárias, da Pena de | preparação | BA | sem prazo | sem | 4 | expurgo? |
| 20 | 43 | `L-55c8ba27edde2f80` | Campanha de Doação de Alimentos: sua empresa pode fazer a diferença! - ONG Banco de Alimen | preparação | — | sem prazo | sem | 4 | expurgo? |
| 20 | 44 | `L-ff0c957845fa0e39` | Hasta el 1 de marzo: convocatorias abiertas para fondos en apoyo a organizaciones de la so | preparação | — | sem prazo | sem | 4 | expurgo? |
| 20 | 45 | `L-cc504de968ded6c2` | PDF Chamada Pública Nº 2026/011 - fbb.org.br | preparação | — | sem prazo | sem | 4 | expurgo? |
| 20 | 46 | `L-f514965d7a8ed4f5` | chamada publica fapespa 0112026 fapespadiepsac fapespa clgedv | verificação externa | PA | sem prazo | sem | 5 | expurgo? |
| 20 | 47 | `L-d6c95c4c8153bb5e` | Convocatoria de manifestación de interés de proyectos de 2026 para las OSC | preparação | — | sem prazo | sem | 5 | expurgo? |
| 20 | 48 | `L-d26f1b33cc343f81` | Annual Report: The Brazil Fund has granted R$ 32 million (circa ... | preparação | RJ | sem prazo | sem | 5 | expurgo? |
| 20 | 49 | `L-37fc4ba798db9f75` | Funai doa R$ 15,6 mil em equipamentos de informática para inclusão digital | preparação | — | sem prazo | sem | 5 | expurgo? |
| 20 | 50 | `L-570b4d9c30337943` | INSTRUÇÃO SOBRE DOAÇÕES DEDUTÍVEIS E RESPONSABILIDADE SOCIAL CORPORATIVA NO REGIME TRIBUTÁ | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 1 | `L-c63ad1020681af8a` | Edital abre inscrições para ONGs e coletivos de periferias no Acre / G1 | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 2 | `L-9ad0609b81817dc5` | Capta: Guia de elaboração de projetos socioambientais | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 3 | `L-4bfbc950302fb835` | Sesc Mesa Brasil RJ - Portal Sesc RJ | preparação | RJ | sem prazo | sem | 5 | expurgo? |
| 21 | 4 | `L-f6fa018898a60f1b` | Empresa apoiando ONG em Goiânia / Parcerias com o Anjos | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 5 | `L-33d2d68328987b08` | Educação afrocentrada impacta alunos de escola quilombola em ... | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 6 | `L-8bc89b8bf7cf8ce7` | premiacao ira reconhecer aplicativos sobre saude e adolescencia | verificação externa | SP | sem prazo | sem | 6 | expurgo? |
| 21 | 7 | `L-f2f712236237ed4e` | Entre as 100 Melhores ONGs do Brasil e a Melhor do Piauí 2026! | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 8 | `L-8ddabb10bd5bd2f6` | Home / Melhores ONGs 2026 | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 9 | `L-f6655472345a0c42` | Home - Solidaridad Southamerica | preparação | PA | sem prazo | sem | 6 | expurgo? |
| 21 | 10 | `L-c945c2ed03c82a83` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 &#8211; GS Notícias | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 11 | `L-12a0367ea70a629f` | FUNDO VERDE DO CLIMA - Organização credenciada junto ao Fundo Verde do Clima. | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 12 | `L-7cc1b0f2372bd58a` | Casa do Pequeno Cidadão Nossa Senhora Aparecida: ONG SAICA ... | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 13 | `L-bcc53ffeab547f08` | Fundação Ford &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 14 | `L-ffcd3d9da3aa896c` | Patrocínios Instituto Claro &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 15 | `L-f8334e1e5f147a02` | Subsídio de Desenvolvimento Comunitário &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 16 | `L-fed0b22b22b75cfb` | CONVOCATORIA A PROYECTOS 2026 &#8211; MAR Fund &#8211; Protecting the Mesoamerican Reef | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 17 | `L-d1c185917a73f263` | Funai doa equipamentos de informática para programa de inclusão digital | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 18 | `L-c666dec7c68e386b` | PDF Edital OIJ Digilendo - Projeto Juventudes entre Páginas | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 19 | `L-fc54028dc3c36386` | Funai oficializa doação de equipamentos de informática para programa de inclusão digital | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 20 | `L-2ca4245a6409ad89` | Sicredi UniEstados e Icatu Seguros se unem para apoiar o Cricket Brasil na temporada 2026 | preparação | MG | sem prazo | sem | 6 | expurgo? |
| 21 | 21 | `L-64517a5e9ce64fcc` | Campanha &#8211; ONG AJUDI | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 22 | `L-b4dae80037c9aa60` | CONTRATO DE PATROCÍNIO 2026-2032 PREÂMBULO - agse.pt | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 23 | `L-b0e6e042cb3db10d` | Projeto de reciclagem de aparelhos eletrônicos ajuda moradores da periferia de Teresina /  | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 24 | `L-1da85134248f32d1` | Doação de alimentos por supermercados e estabelecimentos similares - Agenda do Comércio | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 25 | `L-2df363053b2b5734` | 21/10/2026 09:30Matérias Novas/Relatórios Entregues e prazo de emendas | verificação externa | BA | sem prazo | sem | 7 | expurgo? |
| 21 | 26 | `L-7373afbbea9266b8` | Captação de Recursos para ONGs: Guia Completo 2026 / COREGOV | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 27 | `L-0ec44d941104e289` | Associações e Credenciamentos - Fundación Avina | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 28 | `L-5d7e80665ffb8e16` | Dana doa novo lote de computadores para ONGs por meio da Fundação Pensamento Digital - Dan | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 29 | `L-1911e5f17a5b7e87` | PDF e-book CMVC_VoluntariadoCorporativonasOSCS | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 30 | `L-673efc4b9d04a53f` | 20 lugares para prestar serviços voluntários em Goiânia | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 31 | `L-1970a4dcbd973801` | Doação de Móveis: 9 ONGs para Doar [INFOGRÁFICO] - LBV | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 32 | `L-3b1bcef37839edd9` | ADFEGO &#8211; Associação dos Deficientes Físicos do Estado de Goiás | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 33 | `L-77be7bc5cbd5a504` | Fundo Brasil abre editais para doação milionária a organizações sociais / VEJA | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 34 | `L-f925b7f259a3c575` | UNAIDS divulga lista final de ONGs com projetos aprovados no Edital para ações nos territó | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 35 | `L-405b48dbdb8fb4fa` | Fazer o Bem Faz Bem - JBS | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 36 | `L-49b9f3233d996e64` | Cenário da Infância e Adolescência no Brasil 2026 | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 37 | `L-c1b952a9515669c8` | Captar recursos é o principal desafio para 74% das ONGs - 03/09/2026 - Folha Social+ - Fol | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 38 | `L-9a8137d12285a656` | Troco solidário - Havan | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 39 | `L-4a7e8597605d946b` | Financiamento de OSCs no Brasil: desafios e caminhos | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 40 | `L-a7a7a9b1e4fd0223` | GoodTruck / Comida para a alma / Faça parte | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 41 | `L-cb724e87f462e7b6` | Conheça ONGs que ajudam no combate à fome no Brasil e saiba como colaborar / CNN Brasil V& | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 42 | `L-c7e99c7f3b1f78b4` | O Projeto &#8211; ONG AJUDI | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 43 | `L-04bc431438550011` | ¿Dónde buscar fondos filantrópicos en 2026? - Propel | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 44 | `L-55d5920e90ff984f` | Ato — AVISO DE CHAMAMENTO PÚBLICO - FAR Nº 8/2026 | verificação externa | PE | sem prazo | sem | 7 | expurgo? |
| 21 | 45 | `L-6d637c8a87ee06e3` | ONG Banco de Alimentos - Combate à fome e ao desperdício de alimentos | preparação | — | sem prazo | sem | 8 | expurgo? |
| 21 | 46 | `L-e950023e1a174790` | Servizio Civile 2026: Tante opportunità in Italia e all’estero con le ONG - Info-Cooperazi | preparação | — | sem prazo | sem | 8 | expurgo? |
| 21 | 47 | `L-13429cf05482d5c1` | ¿Dónde encontrar fondos para tu ONG en América Latina? - Propel | preparação | — | sem prazo | sem | 8 | expurgo? |
| 21 | 48 | `L-dd0a76bd31180d24` | AIDS 2026: Guía completa para la sociedad civil | preparação | — | sem prazo | sem | 8 | expurgo? |
| 21 | 49 | `L-ac35f7c8dd0109e5` | Como doar computadores usados? &#8211; Blog do Exército de Salvação | preparação | — | sem prazo | sem | 8 | expurgo? |
| 21 | 50 | `L-aee206446c017faf` | Matching de doações: por que esse modelo está crescendo nas empresas - GiftAid | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 1 | `L-e97609e8454afaa8` | DOAÇÃO EQUIPAMENTOS - Ecodigital | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 2 | `L-c23e12381bd62040` | Plataforma Conjunta / Apoios de Resposta Rápida (ARRs) para Movimentos Feministas da Améri | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 3 | `L-153c9ed2532240f4` | Premia��o, limite de atletas e times participantes: veja o regulamento da Libertadores Fem | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 4 | `L-6ebf6db4a9c8ea71` | Comunidade de Mulheres na Tecnologia - WoMakersCode | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 5 | `L-b5d2df33b966c0c9` | Patrocínios da Havan: saiba como inscrever seu projeto - Blog Havan | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 6 | `L-fe3f62d26e5f4699` | Seleção da Havan para patrocínios, projetos e doações — prazo não ... | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 7 | `L-a634ec5d484827df` | Trackmob - Tudo para você captar mais e melhor! | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 8 | `L-bc197c2c1f0c5c97` | 10 instituições que precisam de voluntários e doações em Goiânia e Aparecida - Jornal Opçã | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 9 | `L-6d2b28ebc4b8e555` | WILDLIFE CONSERVATION SOCIETY PROYECTO GEF MANEJO ... | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 10 | `L-a87e6d37de583756` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 11 | `L-08849379c561c598` | Inscrições para delegação do Brasil na COP31 vão até domingo | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 12 | `L-0a64b27e80ec0dbd` | Não queremos apenas dar um cheque, diz VP da Rockefeller - 17/07/2026 - Folha Social+ - Fo | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 13 | `L-95bc21a2a83d82cc` | InstitutoMoveisParaTodos - Doação | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 14 | `L-839abb68d3820339` | ACNUDH / Convocatoria para aportar información para la visita del Relator Especial sobre l | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 15 | `L-4d8eab0bee9bdc3e` | Fundo Canadá para Iniciativas Locais - Repórter Brasil | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 16 | `L-8357148fc31cd8c6` | Financiamento para o Bem: Inovação e Impacto Social 2025-... — Líder Social | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 17 | `L-5b2d20365b991906` | ONGs, Fundaciones y Cooperación en Latinoamérica / Consultorías, Formación y Grants | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 18 | `L-52b050b893115bf3` | Fondo Casa Brasil: 100 iniciativas comunitarias reciben R$ 20 mil cada una / LideraFest | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 19 | `L-b33df43e668c8d28` | Reforma Tributária no Terceiro Setor: O Limite entre Doação e Patrocínio | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 20 | `L-fb990014a66298d9` | Programa de Doação Microsoft / TechSoup Brazil | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 21 | `L-60f978bc06727426` | Schneider Electric reúne empresas para doação de 70 equipamentos solares com o objetivo de | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 22 | `L-5b6039574f554786` | Dedução do IR para Pronon e Pronas/PCD é prorrogada até 2031 | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 23 | `L-552fa963d68d16e4` | Programa auxilia indústrias com móveis e equipamentos de informática para doar / FIESC | preparação | SC | sem prazo | sem | 9 | expurgo? |
| 22 | 24 | `L-0ce0980e42a7eaf2` | Aiuti all’Africa in cambio di rimpatri: la clausola che svuota la cooperazione Ue &#8211;  | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 25 | `L-28f1f34b1bb2b4b5` | Subvenciones / EEAS | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 26 | `L-357b243716706f71` | FEDDAi / Espace de Partage pour la Société Civile et les Partenaires en Mauritanie | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 27 | `L-837204dfcb47bd94` | Festival ABCR 2026 – Captação de Recursos e Filantropia | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 28 | `L-382acc04fb9fbf57` | Convocatoria de proyectos de reflexión sobre retos sociales / Palau Macaya | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 29 | `L-182a578567c039ce` | Convocatoria de propuestas para 2026 | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 30 | `L-817e8b9220796a1a` | Setpar Solidária / Quando nos unimos, nos fortalecemos! - Setpar Empreendimentos | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 31 | `L-db069a0458f8fffa` | Legislação Ambiental 2026: ONGs, Conformidade e Financiamento - projetosocialbrasil.com.br | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 32 | `L-ddeda00a5f6149d4` | Kellogg Foundation Grants 2026 / How to Apply | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 33 | `L-c2d86d00fa66d9fe` | Renforcement des organisations de la société civile en Amérique Latine &#8211; Fondation N | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 34 | `L-467d9bbb630653f8` | Nexans - Appel à Projets | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 35 | `L-4ac0195dea79f9be` | Organisation de la société civile (OSC) / AFD - Agence Française de Développement | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 36 | `L-3badc1fa169d77e6` | Appels d’offres, grants et subventions en Afrique 2026 / VueRadar | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 37 | `L-07bc668fb81f67b7` | ¡La convocatoria de solicitudes para las pre-sesiones 53 está abierta! / UPR Info | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 38 | `L-723211919c9daaf5` | Costa Rica (MS): ......................................................................... | preparação | MS | sem prazo | sem | 12 | expurgo? |
| 22 | 39 | `L-97f88d42e0091dec` | Curitiba (PR): • • •     Licitações    SECRETARIA DO GOVERNO MUNICIPAL - SGM  SECRETARIA M | preparação | PR | sem prazo | sem | 12 | expurgo? |
| 22 | 40 | `L-b6d8e3e0168925b3` | Maragogipe (BA): Ladeira da Laje Maragojipe – Bahia – CEP – 44420-000  Tel. – (75) 3526 29 | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 22 | 41 | `L-af8db3e1ea4420b3` | Uberaba (MG): ............................................................................ | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 22 | 42 | `L-0c5af32cda2c3fb4` | Uberaba (MG): ............................................................................ | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 22 | 43 | `L-d1cc925b553d99e6` | Marechal Deodoro (AL): Pecuária, Pesca e Aquicultura.      Prazo para envio das propostas: | preparação | AL | sem prazo | sem | 12 | expurgo? |
| 22 | 44 | `L-c5439a10a22259e4` | Florianópolis (SC): Edição Nº. 4287  Controladoria Geral do Município                NUP/I | preparação | SC | sem prazo | sem | 12 | expurgo? |
| 22 | 45 | `L-934d349f4bef73e8` | Florianópolis (SC):  22/10/2026 Edição Nº. 4288  Sumário Secretaria Municipal da Casa Civi | preparação | SC | sem prazo | sem | 12 | expurgo? |
| 22 | 46 | `L-59b91bbf350473d9` | Niterói (RJ): Ribeiro Monteiro Junior, publicadas em 17/10/2026, onde  se lê: 1397 e 1398/ | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 22 | 47 | `L-3fdea4997a1af232` | Palmas (TO): Palmas, para  responder interina e cumulativamente pela Pasta, pelo período d | preparação | TO | sem prazo | sem | 12 | expurgo? |
| 22 | 48 | `L-97b2b6a16e8b8ff8` | Taubaté (SP): Educação - SEED ......................................... 28  Portaria SEED  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 22 | 49 | `L-07ebe6569a211a38` | Santos (SP): �������������������������������������������������������������� 2  FINANÇAS E  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 22 | 50 | `L-761baf0dc4c61694` | Campo Grande (MS): Lopes Vice-Prefeita.................................................... | preparação | MS | sem prazo | sem | 12 | expurgo? |
| 23 | 1 | `L-647ab88f3e33f985` | Itaguaí (RJ): R$850,00   1.501.0000.0000 Outros Recursos não Vinculados 850,00   Art. 2º - | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 23 | 2 | `L-7dc99e212338085e` | Feira de Santana (BA): cooperação ou parceria com órgãos e entidades federais, estaduais o | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 3 | `L-e4ad1f2bf47ac8af` | Salvador (BA): que lhe são conferidas pela legislação em vigor, e   CONSIDERANDO que, nos  | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 4 | `L-e2dfbd1e42ca6180` | Campo Mourão (PR): II - incentivar a adoção de soluções tecnológicas abertas, interoperáve | preparação | PR | sem prazo | sem | 12 | expurgo? |
| 23 | 5 | `L-0fcef0383709aeca` | Lavínia (SP):  da Lei 4.320, de 17 de março de 1.964 e Lei Complementar   101, de 04 e mai | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 6 | `L-f01c8a91df65ba5f` | Taiobeiras (MG): diálogo, consulta, acompanhamento e avaliação, considerando as caracterís | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 23 | 7 | `L-970c9f95c102710e` | Osasco (SP): Orçamentária;    2.3. Seção de Almoxarifado e Manutenção;    3. Divisão de Pa | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 8 | `L-8afe83b2f4ed4f9d` | São Domingos (SE): reduzir a sobrecarga dos serviços públicos, abrigos, canis, organizaçõe | preparação | SE | sem prazo | sem | 12 | expurgo? |
| 23 | 9 | `L-935482668632cbc9` | Monte Alto (SP): concessão dos Benefícios Eventuais poderá   ocorrer em quaisquer serviços | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 10 | `L-c3b38ef5ae675fbf` | Avaré (SP): oportunidades disponibilizados por: I – órgãos públicos; II – instituições de  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 11 | `L-3084013c21e9de1a` | Cordeiro (RJ): relevantes para garantir   experiência segura e acolhedora.      Art. 11. O | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 23 | 12 | `L-5534901ffc6f4d08` | Salvador (BA): 250116 ELEMENTO DE DESPESA 33903012. - FONTE: TESOURO DATA DA ASSINATURA: 1 | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 13 | `L-b9835b3d189bd42b` | Ipiaú (BA): desenvolvimento da linguagem oral, da consciência   fonológica, da leitura, da | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 14 | `L-9426b7dd66e3d268` | Sertãozinho (SP): 1058, 1081, 1082, 1083, 1102, 1108, 1124 e 1135/2026. Ofícios diversos n | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 15 | `L-23cdea1a5e59e3e2` | Tapiraí (SP): Desenvolvimento Social: Ana Cláudia dos Santos Toledano    Diretoria de Dep | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 16 | `L-d78f92d5fc92da9f` | Boa Vista (RR): 569743/2026,    DECRETA:   Art. 1º Fica nomeada a senhora Ana Paula de Aze | preparação | RR | sem prazo | sem | 12 | expurgo? |
| 23 | 17 | `L-11806092c4082232` | Junqueirópolis (SP): administrativas mais gravosas em caso de novo descumprimento, mediant | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 18 | `L-23eb58ba44d21530` | The Next Move Grant 2026: Up to €250,000 in Multi-Year Funding for Sport-Based Nonprofits  | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 19 | `L-fc1cac28a55c69c7` | Mata Atlântica Viva – Conservation and Regeneration Grants 2026 (Brazil) - fundsforNGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 20 | `L-492ad4d27382181f` | Social enterprise opportunities - October 2026 - SEWF | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 21 | `L-c0785f69173e8dc6` | Open Call – Cultural Heritage Fund 2026 (Brazil) - fundsforNGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 22 | `L-ea5bf8441f837443` | Convocatoria de Propuestas: Apoyo de Luena Scholars para proyectos comunitarios en Sudamér | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 23 | `L-38ee67f5e3d9d0dd` | Our Rights, Our Future! – Call for proposal | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 24 | `L-eb3d05c4113dea46` | Erasmus+ 2026 call for proposals published / European School Education Platform | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 25 | `L-58c0e448dd8feff7` | Appels à projets 2026 / France Diplomatie | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 26 | `L-08676ae0e07743cc` | Multilingual and Contextual AI Evaluation call for proposals - Fall 2026 - Amazon Science | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 27 | `L-efbb1d23cea0147d` | Segunda convocatoria para acompañar proyectos de organizaciones de la sociedad civil / Bue | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 28 | `L-429c24a2ff8c8c9c` | 2026/2027 Grants for NGOs and Organizations: Directory of Funding Opportunities - TuiFund | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 29 | `L-3886d7912924d9f4` | Bando “Our Rights, Our Future!” per reti e coalizioni della società civile - Info-Cooperaz | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 30 | `L-bd31f50841b072ca` | chamamento público - PORTAL DE PARCERIAS COM OSC | verificação externa | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 31 | `L-ed7cbe67190c3760` | W.K. Kellogg Foundation Grants 2026: Open Funding Opportunities for Organizations Advancin | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 32 | `L-4c11b76138060386` | Adidas Foundation Grant 2026: Eligibility &amp; How to Apply | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 33 | `L-bca91527b25ecbc5` | Latin America Medical Education Grants / NBME | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 34 | `L-a3bc5c03e0ccb332` | Doação de Computadores &#8211; Projeto de Extensão Centro de Recondicionamento de Computad | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 35 | `L-ef9dc5bc68a022d8` | UNDP GEF Small Grants Programme 2026: Call for Environmental and Climate Project Proposals | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 36 | `L-f2d6784f3e0c3db6` | GEF Small Grants Programme 2026 / Up to US$100,000 | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 37 | `L-a8dc52050bcb219b` | UNDP GEF Small Grants Programme 2026: Funding of Up to $50,000 for Conservation Projects - | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 38 | `L-40aec034af9fa23c` | CONVOCATORIA A ORGANIZACIONES DE LA SOCIEDAD CIVIL INTERESADAS EN PARTICIPAR EN EXPOINCLUS | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 39 | `L-bdc58f9b1c35fb22` | PDF Selecionados 2026 - Edital IVM | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 40 | `L-2215cdfcbf6cd7d7` | PDF Guia 2025 - Edital IVM - portaldoenvelhecimento.com.br | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 41 | `L-5f79bb39b0ff3538` | WK Kellogg Foundation Grants 2026: Fund &amp; Apply | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 42 | `L-c8d97b84b064e7c6` | Call for Proposals-Civil Society Organizations (CSOs) or NGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 43 | `L-bd3a2050c8453fa8` | Embraer Foundation opens applications for 2026 (e)NVEST in Community grant program | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 44 | `L-04a424a960c29c38` | PDF 21189.000536/2026-91 - Embrapa | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 45 | `L-f583cd4f1e567cf6` | Lei regulamenta patrocínio público ao esporte em Goiânia | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 46 | `L-60c6fa067e1d493f` | Governo Municipal amplia apoio às entidades rurais com subvenções, conectividade e investi | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 47 | `L-0bbdbb71adda9d93` | Governo Municipal fortalece o desenvolvimento rural com investimentos em infraestrutura, a | preparação | — | sem prazo | sem | 12 | expurgo? |
