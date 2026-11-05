# Verificação pelo Claude no Chrome — GRUPO 1 de 3 (lote-2026-11-05-externa-completo)

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Esta é a atualização única do sistema: zerar a esteira do Cartório. Os 1.169 livros sem decisão (764 na verificação
externa, 387 na preparação, 18 na recepção — os chegados) foram divididos em 3 grupos. Este prompt é o GRUPO 1:

| O que | Quantidade | Onde |
|---|---|---|
| Livros deste grupo | 400: 257 na verificação externa, 129 na preparação, 14 na recepção | `verificacao/lotes/lote-2026-11-05-externa-completo-parte-1.json` a `-parte-8.json` (8 partes de até 50) |
| Do catálogo das oportunidades conhecidas (R44) | 162 | marca «catálogo» na tabela e o campo `catalogo` no lote |
| Sem nenhuma estrela, para validar ou expurgar | 166 | marca «expurgo?» e o campo `"verificacao_para_expurgo": true` |

Versão do lote: `gerado_em` = `2026-11-05T11:07:33+00:00`. A planilha deste grupo, `LISTA-LIVROS-VERIFICACAO-2026-11-05-GRUPO-1-de-3.xlsx`, tem os livros
deste prompt, parte por parte, com as colunas do resultado para o controle.

## ENTREGA COMPLETA E TOTAL (R41) — obrigatória

1. Trabalhe UMA PARTE de cada vez. Antes de começar, conte os livros da parte (`total_livros`).
2. Entregue UM veredito decisivo para CADA livro da parte, num único arquivo por parte.
3. Copie do arquivo da parte o `lote` (ex.: `lote-2026-11-05-externa-completo-parte-7`) e o `gerado_em` (no campo `lote_gerado_em`).
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
  "lote": "lote-2026-11-05-externa-completo-parte-1",
  "lote_gerado_em": "2026-11-05T11:07:33+00:00",
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

Grave como `verificacao/vereditos/veredito-lote-2026-11-05-externa-completo-parte-N.json` (uma por parte).

## O expurgo dos documentos

O expurgo dos 16 lotes de documentos fica no GRUPO 3; neste grupo, só os livros.

## Ao terminar

Uma planilha de controle com o total de cada parte (entregue / não entregue) e os aprendizados que se repetiram. Nada
parcial: a parte que não foi verificada inteira não é entregue.

## A tabela dos 400 livros do GRUPO 1

Colunas: a parte do lote, a posição na parte, o livro, o título, a etapa, a UF, o prazo, a estrela, quantos dos 12 itens
faltam e a marca (catálogo = R44, nunca sai; expurgo? = sem nenhuma estrela, validar ou expurgar).

| Parte | Nº | Livro | Título | Etapa | UF | Prazo | Estrela | Faltam | Marca |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | `op-7610b88fd1fc` | Quem exatamente pode aplicar neste edital? — Brasil | recepção | GO | aberta | bronze | 2 |  |
| 1 | 2 | `L-93e4a17ea664cf72` | Prefeitura de Quirinópolis abre inscrições para quatro editais da Política Nacional Aldir  | verificação externa | GO | aberta | bronze | 2 |  |
| 1 | 3 | `L-d6f2af76c1fd022b` | CHAMAMENTO PÚBLICO 001/2026 – FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA | verificação externa | GO | aberta | bronze | 2 |  |
| 1 | 4 | `L-a767fde3d29ee056` | Inscrições para edital Ocupa Goiás – MITsp 2027 começam nesta quarta-feira (4/11) | verificação externa | GO | aberta | bronze | 5 |  |
| 1 | 5 | `L-1fce376bd4f690be` | INSCRIÇÕES ABERTAS PARA O CAMPEONATO MUNICIPAL DE ARTES MARCIAIS (CAMAM) 2026 | preparação | GO | aberta | bronze | 2 |  |
| 1 | 6 | `L-7fa11e1354faab25` | EDITAL AGROINDÚSTRIAS MERCADOS COOPERATIVOS RIO DOCE – SELEÇÃO PÚBLICA 03/2026 – Coopera R | verificação externa | GO | aberta | bronze | 1 |  |
| 1 | 7 | `L-9a312c76f4aa724b` | EDITAL DE SELEÇÃO PÚBLICA Nº 04_2026_QUINTAIS PRODUTIVOS RIO DOCE | verificação externa | GO | aberta | bronze | 2 |  |
| 1 | 8 | `L-8474edbfca7245fe` | Secretaria de Esporte e Lazer abre edital para credenciamento de patrocinadores das compet | verificação externa | GO | aberta | prata | 2 |  |
| 1 | 9 | `op-457280912c7f` | Chamamento público para fins de credenciamento de pessoas físicas e jurídicas, com atuação | verificação externa | GO | aberta | prata | 1 |  |
| 1 | 10 | `L-f34962ed027a9579` | FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL — EDITAL DE CHAMAMENTO PÚBLICO VISANDO À SELEÇÃO DE  | preparação | GO | aberta | bronze | 1 |  |
| 1 | 11 | `op-2cf1888b82c9` | Fundo municipal de assistencia social — edital de chamamento público visando à seleção de  | verificação externa | GO | aberta | prata | 2 |  |
| 1 | 12 | `L-4231397535f30ea9` | SEMASC abre Chamamento Público para seleção de projetos voltados à proteção de crianças e  | verificação externa | GO | aberta | prata | 3 |  |
| 1 | 13 | `op-0dc389eec43b` | Municipio de trindade — credenciamento de instituições de assistência social para acolhime | preparação | GO | aberta | bronze | 1 |  |
| 1 | 14 | `captacao-095` | SEDS Goiás - Auxílio Nutricional a entidades — Goiás | verificação externa | GO | sem prazo | sem | 2 | catálogo |
| 1 | 15 | `L-f73edbb222358e9c` | Credenciamento para atuação nos Residenciais Santa Edwiges I e II avança | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 16 | `L-b7e8c6cb8f6c0057` | Doacao de bens.PDF | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 17 | `L-1fd8d68f56b7da82` | Semad vai financiar projetos da sociobiodiversidade em Goiás; veja o edital | preparação | GO | sem prazo | sem | 2 | expurgo? |
| 1 | 18 | `L-040c3fed85393914` | RESOLUÇÃO Nº 15 DE 2026 | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 19 | `L-70e8fcbdb678d319` | Senador Canedo abre credenciamento para ampliar oferta de oficinas esportivas, culturais e | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 20 | `L-dd5da6a7022c4e57` | AVISO DE PUBLICAÇÃO | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 21 | `L-c84e26957106c18c` | Emenda municipal para entidade assistencial | preparação | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 22 | `L-490b53079346a74c` | Edital Ocupa Goiás – MITsp 2027 | verificação externa | GO | sem prazo | sem | 3 | expurgo? |
| 1 | 23 | `L-4b2357e9611b17a7` | Publicada nova Instrução Normativa do Programa Goyazes | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 24 | `L-7bd91fd4c3e5f390` | Programa Goyazes divulga nova forma de envio para Cartas de Intenção de Patrocínio | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 25 | `L-a797302669cc1f0c` | Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação pecuniária | preparação | GO | sem prazo | sem | 4 | expurgo? |
| 1 | 26 | `captacao-063` | Equipagem esportiva comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 27 | `captacao-096` | SEDS Goiás - Água, energia e esgoto para entidades — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 28 | `captacao-097` | Protege Goiás - financiamento indireto de programas sociais — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 29 | `captacao-104` | Termo de Fomento estadual para entidade social — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 30 | `captacao-109` | Projeto de inclusão produtiva de famílias — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 31 | `captacao-112` | Projeto de apoio a mulheres em vulnerabilidade — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 32 | `captacao-126` | Fundo Estadual dos Direitos da Pessoa Idosa Goiás — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 33 | `captacao-154` | Projeto de saúde mental comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 34 | `captacao-158` | Projeto de reabilitação comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 35 | `captacao-159` | Projeto de teleorientação em saúde comunitária — Goiás | verificação externa | GO | sem prazo | sem | 5 | catálogo |
| 1 | 36 | `L-3227e43b5edcde45` | Pedidos de inscrição de projetos em caráter excepcional no Programa Goyazes devem ser envi | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 37 | `L-df444e6fcee25a18` | Exposição “Ichi-go Ichi-e” é prorrogada até 7 de fevereiro no Museu da Imagem e do Som de  | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 38 | `L-e2d72959753623db` | Política Nacional Aldir Blanc - PNAB | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 39 | `L-fde0a18dfd449d02` | TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 40 | `L-f92d47c67976ed40` | docs-bens-para-doacao | preparação | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 41 | `L-301c4f104c07b061` | Aviso de Alteração — AVISO DE ALTERAÇÃO DE EDITAL | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 42 | `L-a48fdd94a1dede55` | EDITAL DE MANUTENÇÃO CONTINUADA DE ESPAÇOS DE CULTURA | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 43 | `L-d491fd0842b76692` | EXTRATO DO 1º TERMO ADITIVO AO TERMO DE COLABORAÇÃO EMERGENCIAL Nº 046/2026 | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 44 | `L-939509d64f531285` | DESPACHO Nº 13882/2026 | verificação externa | GO | sem prazo | sem | 5 | expurgo? |
| 1 | 45 | `captacao-026` | PNAB Goiás - Manutenção Continuada de Grupos/Companhias — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 46 | `captacao-050` | Pró-Goiás Atleta - atletas e treinadores vinculados a entidades — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 47 | `captacao-054` | Projeto de esporte e contraturno escolar — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 48 | `captacao-057` | Núcleo de artes marciais educativas — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 49 | `captacao-064` | Reforma de espaço esportivo social — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 1 | 50 | `captacao-074` | Projeto de reforço escolar e recomposição de aprendizagem — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 1 | `captacao-077` | Projeto de educação ambiental escolar — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 2 | `captacao-113` | Projeto de apoio a famílias de baixa renda — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 3 | `captacao-155` | Projeto de prevenção ao uso de álcool e drogas — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 4 | `captacao-163` | Projeto de saúde da mulher — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 5 | `captacao-178` | TAC ambiental via Ministério Público — Brasil | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 6 | `captacao-196` | MPGO - TAC com destinação social — Goiás | verificação externa | GO | sem prazo | sem | 6 | catálogo |
| 2 | 7 | `L-3951470189011001` | DESPACHO N.º 3178/2026 - SEMAD/GAB - Cuidam-se os autos sobre o 3º Termo | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 8 | `L-417ae8d2e9f5d965` | EXTRATO DO 5º TERMO ADITIVO AO TERMO DE COLABORAÇÃO EMERGENCIAL Nº 041/2025 | verificação externa | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 9 | `L-bd31527690a94e48` | Terras raras: um passo pequeno demais - Outras Palavras | preparação | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 10 | `L-a18f3537362ab8f1` | Edital de Teatro | verificação externa | GO | sem prazo | sem | 6 | expurgo? |
| 2 | 11 | `captacao-118` | Destinação de IR pessoa física para FMDCA — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 12 | `captacao-147` | SES-GO - atuação em rede com OSC celebrante — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 13 | `captacao-148` | SES-GO - termo de fomento em saúde — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 14 | `captacao-149` | SMS Goiânia - parceria com entidade de saúde — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 15 | `captacao-151` | Emenda estadual para saúde comunitária — Goiás | verificação externa | GO | sem prazo | sem | 7 | catálogo |
| 2 | 16 | `L-96e0e7e0f8cebe7d` | Fundo de Arte e Cultura | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 17 | `L-e8d2b7589e1e8334` | Comunicado de Revogação do Edital do Conselho da Juventude | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 18 | `L-d0643cb995773f5c` | Associações poderão receber material da Prefeitura | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 19 | `L-ef46e9cfdaa9e9e7` | COMFAPE | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 20 | `L-83c645026c1dddd8` | Instituto Reerguer / Acolhimento, Doações e Ações Sociais em Goiânia | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 21 | `L-42f876fb8ac84999` | Goiás convoca suplentes de sete editais da PNAB e destina R$ 1,98 milhão a 33 projetos | preparação | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 22 | `L-9c9ab5df92c89249` | DOE - AP DO RIO DOCE - EXT ADJ HOMOL -  CHAMADA PUBLICA N° 018-2026 | verificação externa | GO | sem prazo | sem | 7 | expurgo? |
| 2 | 23 | `captacao-098` | FEAS-GO - cofinanciamento da assistência social — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 24 | `captacao-099` | FMAS Goiânia - parceria socioassistencial — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 25 | `captacao-101` | SEMASDH Goiânia - República para jovens — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 26 | `captacao-102` | SEMASDH Goiânia - serviço de acolhimento para adolescentes — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 27 | `captacao-125` | Fundo Municipal do Idoso de Goiânia — Goiás / Goiânia | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 28 | `captacao-138` | Projeto de prevenção ao trabalho infantil — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 29 | `captacao-192` | Justiça Federal em Goiás - prestações pecuniárias — Goiás | verificação externa | GO | sem prazo | sem | 8 | catálogo |
| 2 | 30 | `L-096417eff0737f19` | Convênio com órgão público estadual | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 31 | `L-f6d290b1c8331b00` | Manual de Identidade Visual | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 32 | `L-f981ba0888c7d9f0` | Anápolis lança editais com mais de R$ 1,5 milhão para fortalecer a cultura e ampliar oport | preparação | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 33 | `L-a9f7bdd04b4b79bf` | -> EDITAL DE CULTURA NO SOCIAL – PNAB 2026 – CATEGORIA CATEGORIA E – CULTURA E MULHERES EM | verificação externa | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 34 | `L-7f3bcb4dff43bf34` | Edital de Convocação AGE 192 versão editada | verificação externa | GO | sem prazo | sem | 8 | expurgo? |
| 2 | 35 | `L-792e383a380a0b8e` | PRÊMIO A SERVIDOR QUE MENCIONA E DÁ | verificação externa | GO | sem prazo | sem | 8 | expurgo? |
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
| 4 | 23 | `L-bbf6a1bf8fff4611` | EDITAL PULSA FRANCO - ANIVERSÁRIO DE FRANCO DA ROCHA (82 ANOS) | preparação | BR | aberta | bronze | 1 |  |
| 4 | 24 | `L-0059dea383da1a71` | instituto impactarte abre edital projetos impacto social apoio ky3h8l | preparação | BR | aberta | prata | 2 |  |
| 4 | 25 | `L-1bdd24cbf29b642b` | Instituto Impactarte abre edital contínuo de apoio a OSCs - Escola ... | preparação | BR | aberta | prata | 4 |  |
| 4 | 26 | `L-2cd13d0b28654fdf` | Edital SVS 2026 – Captação de R$1,1 mi para vigilânciaR$ 1,1 mi·até 13 de nov. de 2026 | verificação externa | AP | aberta | prata | 2 |  |
| 4 | 27 | `L-9c15ec76c4bb0880` | apoio financeiro / Núcleo de Relações Internacionais | preparação | BR | aberta | bronze | 2 |  |
| 4 | 28 | `L-15843f8d3c824066` | Edital Saúde Branquinha 2026: Como OSCs Podem Captaraté 16 de nov. de 2026 | preparação | BR | aberta | bronze | 1 |  |
| 4 | 29 | `L-0d09458a7d146360` | EDITAL DE RECONHECIMENTO E PREMIAÇÃO DOS MESTRES E MESTRAS DA CULTURA POPULAR DE ARATUBA – | preparação | BR | aberta | bronze | 2 |  |
| 4 | 30 | `L-763c190b30482bb2` | Edital ANATER 3/2026: quem pode aplicar e captar recursosaté 18 de nov. de 2026 | preparação | MG | aberta | bronze | 2 |  |
| 4 | 31 | `L-a2c10bb8c67f0d12` | Aviso — EDITAL DE CONVOCAÇÃO CONJUVE/SNJ/SG/PR Nº 1/2026 | verificação externa | BR | aberta | bronze | 3 |  |
| 4 | 32 | `L-065193c2149b25c2` | Inscrições abertas para o edital Quintais Produtivos para Mulheres ... | preparação | BR | aberta | bronze | 2 |  |
| 4 | 33 | `L-11c34b5394cbc54c` | Edital 03/2026 – Coopera Rio + Doce (Anater/BNDES)até 19 de nov. de 2026 | preparação | MG | aberta | bronze | 4 |  |
| 4 | 34 | `L-be75e8f5923c10ce` | Extrato — EDITAL Nº 2/2026 | verificação externa | BR | aberta | bronze | 6 |  |
| 4 | 35 | `L-20177886a1c4009b` | Edital — EDITAL Nº 41, DE 4 DE NOVEMBRO DE 2026 | verificação externa | BR | aberta | bronze | 5 |  |
| 4 | 36 | `L-50693714a9bf17e8` | Edital CBMM 2026: Guia Completo de Captaçãoaté 30 de nov. de 2026 | preparação | MG | aberta | bronze | 1 |  |
| 4 | 37 | `L-aba76de122cd39fe` | Chamamento Engaja Brasil 2026 / Inscreva sua OSC | preparação | BR | aberta | prata | 2 |  |
| 4 | 38 | `L-30b0c9d6efacdd7f` | Instituto GOL abre edital para doar passagens aéreas a OSCs | recepção | BR | aberta | bronze | 2 |  |
| 4 | 39 | `L-1a5e53224be242d2` | Edital FIA Sarandi 2026: Guia para OSCs captarem recursosaté 01 de dez. de 2026 | preparação | BR | aberta | bronze | 4 |  |
| 4 | 40 | `L-84dc89cf76baa817` | edital-seleciona-redes-para-implementacao-de-nucleos-de-desenvolvimento-da-sociobioeconomi | preparação | BR | aberta | bronze | 3 |  |
| 4 | 41 | `L-feddacd29aefaf0c` | Fundación Mapfre abre inscrições para a 10ª edição dos Prêmios à Inovação Social e vencedo | verificação externa | BR | aberta | bronze | 6 |  |
| 4 | 42 | `op-424cf54854a5` | BNDES abre chamada para apoiar projetos de organizações periféricas em todo o país — BNDES | preparação | BR | aberta | prata | 1 |  |
| 4 | 43 | `op-9b1d2dfcbd4e` | BNDES abre chamada para apoiar projetos de organizações periféricas em todo o país — Brasi | preparação | BR | aberta | prata | 1 |  |
| 4 | 44 | `L-8e00fb51f461c33b` | Edital BNDES Periferias em Rede: Como Captar até 2M em 2026R$ 2,0 mi·até 04 de dez. de 202 | preparação | BR | aberta | prata | 2 |  |
| 4 | 45 | `L-623834cf4a9f402c` | Chamada abre apoio a organizações de base periférica - Nossa Causa | preparação | BR | aberta | bronze | 2 |  |
| 4 | 46 | `L-0d00a9db100f2324` | BNDES lança 6º ciclo de chamada para apoio a projetos nas periferias urbanas do país | preparação | RJ | aberta | bronze | 2 |  |
| 4 | 47 | `L-a0054f7ffe554794` | BNDES, BNB e Ministério do Meio Ambiente abrem 2º ciclo de apoio a projetos para recuperar | recepção | BR | aberta | ouro | 0 |  |
| 4 | 48 | `L-959b8cb42a5bdfb1` | Edital Recaatingar 2026 – Recuperação na CaatingaR$ 55,2 mi·até 14 de dez. de 2026 | preparação | BR | aberta | bronze | 2 |  |
| 4 | 49 | `op-677f1cf40da5` | Primeiro Ciclo Edital Reecatingar: divulgação prorrogada — Brasil | recepção | BR | aberta | prata | 10 |  |
| 4 | 50 | `op-167829dfd75a` | Mapfre abre seleção de projetos incentivados com foco em cultura, esporte e inclusão socia | recepção | BR | aberta | bronze | 4 |  |
| 5 | 1 | `op-2c0b8a816195` | Edital Mapfre 2026 de patrocínio incentivado: só a janela de PRONAS/PCD e PRONON segue abe | recepção | BR | aberta | prata | 4 |  |
| 5 | 2 | `L-7ad6e1d62f398963` | Edital Mapfre 2026: Projetos de Cultura e Esporteaté 15 de dez. de 2026 | preparação | BR | aberta | bronze | 4 |  |
| 5 | 3 | `L-ef49a22f4c2beb9c` | Áudio: Eduardo Braga propõe cronograma para votar Orçamento até 17 de dezembro | verificação externa | BR | aberta | bronze | 10 |  |
| 5 | 4 | `L-31700784edd49869` | 3º Edital Frei Tito | preparação | CE | aberta | bronze | 2 |  |
| 5 | 5 | `L-b567222a27246a8e` | Chamada Rio Doce ParticipativoConheça as regras do edital de apoio a projetos estruturante | preparação | BR | aberta | bronze | 2 |  |
| 5 | 6 | `op-aa70ccf9ba8b` | Chamada Rio Doce Participativo — Projetos Estruturantes para o Desenvolvimento Territorial | preparação | BR | aberta | prata | 3 |  |
| 5 | 7 | `L-9bfc983ec1355812` | Edital CELESC PIE 2026: Captar até R$ 300 milaté 31 de dez. de 2026 | preparação | SC | aberta | bronze | 4 |  |
| 5 | 8 | `L-545b918cd28ff66b` | Chamada PRONINC 2026 – Finep Financiamento até R$5 miR$ 5,0 mi·até 14 de jan. de 2027 | preparação | BR | aberta | bronze | 2 |  |
| 5 | 9 | `L-8a4492b60258e8e2` | Chamada Pública 3/2026 Reitoria: Guia para Catadoresaté 19 de jan. de 2027 | preparação | RJ | aberta | bronze | 2 |  |
| 5 | 10 | `L-ef3608dc03b6cef5` | Abertas inscrições para o 6° Ciclo de Aceleração de OSCs da Glocal | recepção | BR | aberta | bronze | 2 |  |
| 5 | 11 | `op-e96e36b220b6` | Lei Rouanet (mecanismo Incentivo a Projetos Culturais do Pronac), MinC. Programa permanent | recepção | BR | aberta | ouro | 0 |  |
| 5 | 12 | `L-65c48b1fe7662342` | Chamada de Propostas FAPESP/MCTI/MCom/CGI.br 2026 para ... | preparação | SP | aberta | bronze | 2 |  |
| 5 | 13 | `L-00651d67a3de7bdb` | Fortalece Cursinhos Populares lança edital para apoiar iniciativas de educação popular | preparação | BR | aberta | bronze | 2 |  |
| 5 | 14 | `L-a8d0efee35c9a1f7` | edital mobilizacao em defesa dos espacos civicos e da democracia inscreva seu grupo | recepção | BR | aberta | ouro | 0 |  |
| 5 | 15 | `nova-29bca7738ad2` | Chamada Pública MCTI/CNPq/ANR N° 32/2026 — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 16 | `op-4471eceed259` | Inscrições abertas para Programa de capacitação para entidades socioambientais — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 17 | `op-c0289af6330d` | Black STEM – 1ª edição — Brasil | preparação | BR | aberta | prata | 2 |  |
| 5 | 18 | `op-48b6d473759b` | Programa Funarte Aberta 2026 — Ocupação da Sala Multiuso do Centro Técnico de Artes (Rio d | preparação | BR | aberta | prata | 1 |  |
| 5 | 19 | `L-d5f7ae07244c79d6` | Edital Funarte Aberta 2026 - Centro de Teatroaté 30 de abr. de 2027 | verificação externa | BR | aberta | prata | 2 |  |
| 5 | 20 | `L-78874945ef50d4db` | Edital CEMIG 2026: Banco de Projetos Culturais e Saúde | preparação | BR | aberta | bronze | 4 |  |
| 5 | 21 | `op-24ac6bab9536` | Edital 01/2026 do FNS/CNBB (Campanha da Fraternidade 'Fraternidade e Moradia'): auxílio de | recepção | BR | encerrada | bronze | 0 |  |
| 5 | 22 | `op-c95f8c5d7a9c` | Selecionar projetos de Pontões de Cultura para celebrar Termo de Compromisso Cultural (TCC | recepção | BR | encerrada | prata | 1 |  |
| 5 | 23 | `op-d0da321a9cec` | Edital 2026 do Fundo Nacional de Solidariedade (CNBB) para projetos de moradia ligados à C | recepção | BR | encerrada | bronze | 1 |  |
| 5 | 24 | `op-5bdd0bd521e4` | Edital SCDC/MinC nº 11/2026 (2º Edital Cultura Viva — Rede de Pontões) seleciona Pontões d | recepção | BR | encerrada | prata | 2 |  |
| 5 | 25 | `L-1709cea91427c960` | Lei Rouanet - doação de pessoa física | preparação | BR | sem prazo | sem | 1 | expurgo? |
| 5 | 26 | `captacao-036` | Lei Rouanet - patrocínio pessoa jurídica — Brasil | verificação externa | BR | sem prazo | sem | 2 | catálogo |
| 5 | 27 | `captacao-090` | MDS - Cozinhas Solidárias 2026 — Brasil | verificação externa | BR | sem prazo | sem | 2 | catálogo |
| 5 | 28 | `L-d5aa75c011ebfa08` | EDITAL DE CHAMAMENTO PÚBLICO Nº 008/2026 POLÍTICA NACIONAL ALDIR BLANC (PNAB) - SECULT CHO | preparação | BR | sem prazo | sem | 2 | expurgo? |
| 5 | 29 | `L-21d4907988607765` | Edital Recupera Cerrado 2026 – Guia do Banco do BrasilR$ 1,0 mi | preparação | BR | sem prazo | sem | 2 | expurgo? |
| 5 | 30 | `L-45ee431cbdf27937` | Edital CMDPI Riacho dos Machados 2026: Guia de Captação | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 31 | `L-274d0251602f77df` | Edital com inscrições permanentemente abertas incentiva ... | preparação | SP | sem prazo | sem | 3 | expurgo? |
| 5 | 32 | `L-d1c89227e9c4670b` | Convocatoria Consejo de la Sociedad Civil 2026 – 2028 &#8211; Comisión Nacional de Riego | preparação | RS | sem prazo | sem | 3 | expurgo? |
| 5 | 33 | `L-1ecb0900ac49b0ea` | XVIII Seleção Funarte Marc Ferrez de Fotografia | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 34 | `L-013a6acc53cdfdf3` | Fundo OSC apoia 40 projetos de organizações da sociedade civil em todo o Brasil - NIDDE DI | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 35 | `L-cd847ed07b71f074` | EDITAL DE CHAMAMENTO PÚBLICO Nº 03/2026 - PRÊMIO CULTURA NEGRA E CULTURA INCLUSIVA | preparação | BR | sem prazo | sem | 3 | expurgo? |
| 5 | 36 | `L-a28273823f0adb77` | Edital SEDAC 35/2026 – Patrimônio Cultural – 2026 RSR$ 1,4 mi | preparação | BR | aberta | bronze | 4 |  |
| 5 | 37 | `captacao-139` | Projeto de fortalecimento de conselhos e controle social — Brasil | verificação externa | BR | sem prazo | sem | 4 | catálogo |
| 5 | 38 | `captacao-167` | FDD - patrimônio cultural brasileiro — Brasil | verificação externa | BR | sem prazo | sem | 4 | catálogo |
| 5 | 39 | `L-b9390caf143e8993` | chamada publica articuladores locais edital 012018 | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 40 | `L-a9058a24cd25ed90` | Edital seleciona projetos para fortalecer proteção de crianças e ... | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 41 | `L-6793c71b032d65ed` | Edital CMDPI Santaluz 2026: Guia de Chancela de Projetos | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 42 | `L-74402b14b173797a` | Edital CMDPI Godofredo Viana 2026: Guia de Inscrição | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 43 | `L-ee8524847a1d548e` | Edital Instituto EDP 2026: Banco de Projetos | verificação externa | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 44 | `L-ce7087f6ac9f3577` | Dia Nacional da Construção Social reúne trabalhadores e famílias em Aparecida de Goiânia - | preparação | — | sem prazo | sem | 4 | expurgo? |
| 5 | 45 | `L-e12da8c338781518` | 10 ONGs ambientais brasileiras para doar em 2026 | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 46 | `L-a3529382127b06df` | Fies 2: inscrições gratuitas para vagas remanescentes estão abertas / Agência Brasil | preparação | BR | sem prazo | sem | 4 | expurgo? |
| 5 | 47 | `L-0636672456b526c7` | instituto lojas renner seleciona projetos de empreendedorismo feminino | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 48 | `L-d8c0579e2e2b24bc` | chamada publica 0222026 projeto perfil censitario juventude bairro pt25ux | verificação externa | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 49 | `L-b61d39393f78e396` | Fundo Regenerativo PcD lança chamada aberta para projetos de inclusão em Belo Horizonte e  | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 5 | 50 | `L-666604fbe5770427` | Ação da Cidadania Contra a Fome a Miséria e Pela Vida: Doe Agora | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 6 | 1 | `L-726a23675b65b5b3` | Nova Lei de Doação de Alimentos: incentivos fiscais para redução do desperdício - Moore | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 6 | 2 | `L-70b99a72d09d413c` | Programa conserta e doa computadores a escolas e bibliotecas / Agência Brasil | preparação | BR | sem prazo | sem | 5 | expurgo? |
| 6 | 3 | `L-6cc08a827f1546d2` | Chamada Pública CNPq/MMULHERES 2026 – Asas para o Futuro | verificação externa | BR | sem prazo | sem | 5 | expurgo? |
| 6 | 4 | `L-a39813af7d64d700` | PDF Chamada Para Apresentação De Projetos | verificação externa | BR | sem prazo | sem | 5 | expurgo? |
| 6 | 5 | `captacao-041` | Lei de Incentivo ao Esporte - Esporte para Toda a Vida — Brasil | verificação externa | BR | sem prazo | sem | 6 | catálogo |
| 6 | 6 | `L-e75cb9a0fae269e3` | Fundação Maria Emília lança chamada aberta para viabilizar soluções em Saúde e Educação | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 7 | `L-e2c5f8416837e526` | Instituto Cactus lança edital para apoiar projetos de saúde mental voltados às mulheres | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 8 | `L-b2a0292854f18825` | rj lei municipal de cultura abre edital de incentivo | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 9 | `L-afd2e1a5f1ef2bee` | Fundação Telefônica Vivo | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 10 | `L-262c6ca4479191ea` | Fundação Vale | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 11 | `L-553ab50737df52c1` | Instituto Neoenergia | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 12 | `L-a97855804cde9350` | Instituto Lojas Renner | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 13 | `L-c3bb8ee801a083d9` | Edital Instituto John Deere 2026: Guia de Captação | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 14 | `L-64d7b4159c458f36` | Edital FCCR 2024: Arte e Longevidade em São José 2026 | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 15 | `L-6779f8b084960a24` | Edital AlimentaLAB 2026: Guia de Captação e Inovação | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 16 | `L-d1fc1080460201e7` | chamada publica 0212026 projeto radiografia censitaria economia criati e8kuab | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 17 | `L-ed734dd58af49e47` | Edital Carreiras em Movimento aproxima estudante de engenharia da profissional que a inspi | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 18 | `L-9b249a83dda7abfc` | Lei autoriza que empresas e organizações doem alimentos Raquel Montero - Advogada | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 19 | `L-e949ae2748e0a162` | Edital apoia ONGs com foco em saúde e inclusão - Nossa Causa | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 20 | `L-fe871273592eee2b` | Carreiras Santander: venha fazer parte do nosso time | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 21 | `L-537671d9c19d35d0` | Conexão Coloplast - Coloplast Brasil | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 22 | `L-e56c9f0b396fcd14` | Prosas Editais » Capta | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 23 | `L-c11c27e9053ec925` | Edital Impactarte » Capta | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 24 | `L-119eb3c43f8ec210` | ONGs baianas buscam título nacional | preparação | — | sem prazo | sem | 6 | expurgo? |
| 6 | 25 | `L-42ec7db59b6eff68` | Our Rights, Our Future! – Call for proposal - CCPR-Centre | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 26 | `L-c1454109f3f472af` | Conheça a parceria entre o TCU e a organização Programando o Futuro - Programando o Futuro | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 27 | `L-0ae30db9b442d961` | Projetos maranhenses irão receber recursos para apoiar crianças, adolescentes e pessoas id | preparação | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 28 | `L-1ee7a71bc730213c` | Prosas / Listagem de editais | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 29 | `L-b7b56892167df6bd` | Como captar R$200 mil no edital CNPq 2026 – Guia práticoR$ 200 mil·até 12 de fev. de 2027 | verificação externa | BR | sem prazo | sem | 6 | expurgo? |
| 6 | 30 | `L-208b9c4917ce4854` | Edital SJC 01/2026 PPCAAM - Crianças e Adolescentes | verificação externa | SP | sem prazo | sem | 6 | expurgo? |
| 6 | 31 | `captacao-119` | Destinação de IR pessoa jurídica para Fundo da Criança — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 32 | `captacao-169` | FDD/Pronasci - cultura e cidadania em territórios vulneráveis — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 33 | `captacao-193` | CNJ - política de destinação de penas pecuniárias — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 34 | `captacao-215` | Prosas - Central de Editais — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 35 | `captacao-217` | Bússola Social - Bússola Editais — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 36 | `captacao-219` | GIFE Mosaico - base de projetos — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 37 | `captacao-226` | Instituto Natura — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 38 | `captacao-234` | Instituto Unibanco — Brasil | verificação externa | BR | sem prazo | sem | 7 | catálogo |
| 6 | 39 | `L-d2dc513f4abddc06` | prazo prorrogado edital de intercambio para projetos apoiados pelo programa casa cidades | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 40 | `L-d8904b3f21a28a5a` | PL 153/2026 — Altera a Lei nº 9.610, de 19 de fevereiro de 1998, para dispor sobre a desti | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 41 | `L-75e197636d0a60b7` | MPV 1336/2026 — Altera a Lei nº 8.036, de 11 de maio de 1990, que dispõe sobre o Fundo de  | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 42 | `L-b6e9044b7df66a86` | Instituto Grupo Boticário | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 43 | `L-fbe001df9037a548` | Edital Orquestra Joseense FCCR 2026: Guia de CaptaçãoR$ 4 mil | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 44 | `L-f2f5524e139a08d7` | Edital Programa de Recuperação Econômica de Pequenos Negócios de Empreendedores (as) Negro | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 45 | `L-8e0b34b3b8579bed` | Juizado do Torcedor de Pernambuco financia projetos sociais com recursos de prestações pec | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 46 | `L-bb112d2b0a7c4f9c` | Civil Society Microgrant 2025: COP30 Call for Proposal | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 47 | `L-9bc6001a85385bb1` | Mina Cultural / Marketing de causa | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 48 | `L-f3c196b2343fcbdf` | Prêmio Impacta Mais 2026: Inscrições Abertas para Iniciativas Sociais e Ambientais | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 49 | `L-f2596f99b591d72e` | chamada publica mctifinepfndct cooperamais tecnologia ict parceria coo 3oyz1t | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 6 | 50 | `L-7df240257f7de5ea` | Após eleições, empresas anunciam nas redes sociais fim de doações / G1 | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 1 | `L-3bff05968828fcb4` | Todos à Mesa &#8211; Unidos para Alimentar | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 2 | `L-ac1faeb41421a42a` | SoMar Azul: inscrições abertas para o edital que busca soluções ... | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 3 | `L-ebb92f44d65c520e` | Edital CMDCA 001/2026 – Pedra Azul MG: Captação via FMDCA | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 4 | `L-ae0676ca0464063f` | O cenário das ONGs no Brasil em 2026 - INCAvoluntário | preparação | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 5 | `L-08d6664a9600e1f3` | FMDCA 2026 abre chamamento público e destina R$ 240 mil a projetos ... | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 6 | `L-4a02866821bb93d2` | Floresta Viva – Águas do São Francisco 2026: edital FUNBIOR$ 17,8 mi·até 02 de dez. de 202 | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 7 | `L-f8fcf24f66297dcd` | Edital de Projetos Sociais 2027 Cerbranorte – R$40 mil 2026R$ 40 mil·até 15 de dez. de 202 | verificação externa | BR | sem prazo | sem | 7 | expurgo? |
| 7 | 8 | `captacao-128` | Destinação de IR pessoa física para Fundo do Idoso — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 9 | `captacao-129` | Destinação de IR pessoa jurídica para Fundo do Idoso — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 10 | `captacao-136` | Conselho de Igualdade Racial - projetos de promoção da igualdade — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 11 | `captacao-137` | Conselho da Mulher - projetos de autonomia e proteção — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 12 | `captacao-182` | Projeto de compostagem comunitária — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 13 | `captacao-198` | MPT - TAC para inclusão profissional — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 14 | `captacao-208` | Cessão de bens móveis apreendidos — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 15 | `captacao-210` | Tribunal de Contas - capacitação e controle para OSC — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 16 | `captacao-211` | TCE-GO - exigências de certidão para captação — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 17 | `captacao-216` | Mapa das OSC - área de editais — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 18 | `captacao-218` | Capta - oportunidades e editais — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 19 | `captacao-225` | Instituto Claro — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 20 | `captacao-227` | Instituto Coca-Cola Brasil — Brasil | verificação externa | BR | sem prazo | sem | 8 | catálogo |
| 7 | 21 | `L-b08e5bedca000adc` | Fundação Banco do Brasil lança o Edital Rio Doce Participativo e Comunitário – Chamada Púb | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 22 | `L-e99fd3814d087eae` | projetos aprovados chamada publica 0012018 articuladores locais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 23 | `L-4ce84e6cc535deef` | RQS 366/2026 — Requer a realização de Sessão de Debates Temáticos destinada a discutir os  | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 24 | `L-72ce3c531c8db250` | Bússola EditaisEncontre editais de financiamento e gerencie candidaturas com eficiência.Ba | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 25 | `L-c6122d2efb404197` | Lideranças Negras e Oportunidades de Acesso | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 26 | `L-8caf7af533483667` | Fundação Itaú | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 27 | `L-e3d53c5efd260a49` | Cultura de Doação | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 28 | `L-eba16fcc7a79ecb3` | Saberes 2025: Financiamento de Soluções Climáticas Locais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 29 | `L-bd50a3171b5395a6` | • Cadastros e Registros Especiais | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 30 | `L-0d9e86d1d715087e` | Leilão e Doação | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 31 | `L-af8182f136d77bad` | DoaMais - Encontre ONGs e Faça a Diferença | preparação | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 32 | `L-a8352815889fb704` | Faculdade de Medicina de Uberlândia abre inscrições | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 33 | `L-111b49d5bf16972d` | #FazAXepa: Campanha nacional é lançada em evento que prega união contra o desperdício de a | preparação | — | sem prazo | sem | 8 | expurgo? |
| 7 | 34 | `L-f43676458aa0d096` | Edital de segurança alimentar abre inscrições para projetos | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 35 | `L-8cf9d76496dbd49f` | Áudio: CCJ analisa criação de fundo de amparo às crianças órfãs | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 36 | `L-9d526a1b43f82ba9` | Chamada Aberta 2026 Instituto Impactarte - ssir.com.br | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 37 | `L-0570699307acd4fb` | Uso de organizações sociais em contratos na saúde é questionado em audiência no Senado | verificação externa | BR | sem prazo | sem | 8 | expurgo? |
| 7 | 38 | `captacao-062` | Festival esportivo intergeracional — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 39 | `captacao-072` | Arte e Cultura na Educação Integral — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 40 | `captacao-086` | Projeto de educação para direitos humanos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 41 | `captacao-108` | Projeto de convivência e fortalecimento de vínculos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 42 | `captacao-130` | Projeto de convivência para idosos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 43 | `captacao-132` | Projeto de cuidadores e apoio familiar — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 44 | `captacao-134` | MDHC - editais de direitos humanos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 45 | `captacao-156` | Projeto de formação de cuidadores — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 46 | `captacao-165` | FDD - meio ambiente — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 47 | `captacao-166` | FDD - defesa do consumidor — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 48 | `captacao-168` | FDD - outros direitos difusos e coletivos — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 49 | `captacao-173` | Fundo Clima - projetos socioambientais — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 7 | 50 | `captacao-176` | BNDES Corais - meio ambiente — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 1 | `captacao-180` | Projeto de coleta seletiva inclusiva — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 2 | `captacao-184` | Projeto de recuperação de nascente urbana — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 3 | `captacao-186` | Projeto de educação para defesa do consumidor — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 4 | `captacao-187` | Projeto de acessibilidade cultural/patrimonial — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 5 | `captacao-189` | Projeto de economia circular com mulheres e jovens — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 6 | `captacao-194` | MPF - cadastro de entidades para bens e valores de autocomposição coletiva — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 7 | `captacao-195` | CNJ/CNMP - bens e valores de ações coletivas — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 8 | `captacao-197` | MPT - TAC para projetos de combate ao trabalho infantil — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 9 | `captacao-209` | Receita Federal - doação de mercadorias apreendidas — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 10 | `captacao-233` | Instituto Sicoob — Brasil | verificação externa | BR | sem prazo | sem | 9 | catálogo |
| 8 | 11 | `L-dab3e164150143be` | embaixada da australia abre edital para projetos de pequeno e medio porte | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 12 | `L-6b5e48152ff75848` | Apresentação de emendas | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 13 | `L-4e9a47f6002e9e71` | REQ 5/2026 - CCJ — Requer, nos termos dos arts. 336, II, e 338, IV, do Regimento Interno d | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 14 | `L-c730436c2df4b59c` | Edital Biblioteca Comunitária é Cultura Viva | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 15 | `L-654053a13c1e3d7d` | PEC 6/2026 — Altera o art. 156-A, § 6°, IV da Constituição Federal para incluir as entidad | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 16 | `L-7c39565d46943088` | 2026Um ano sem celular nas escolas: o que mudou?Entrevista: Flora Ariza, consultora da Une | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 17 | `L-beab74b3c9814bac` | Concurso de Teatro e Prêmio 2025 | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 18 | `L-f1d429444543408b` | Edital 2025 do Fundo de Impacto para Justiça Social (ICOM): “Justiça Climática Começa nos  | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 19 | `L-661029b0cc856333` | Natal Sem Fome 2026 | preparação | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 20 | `L-bd0b9f49de015351` | Instituto Impactarte abre seleção permanente para apoiar projetos ... | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 21 | `L-941753fd218962cc` | Chamada Pública CNPq/MCTI N° 36/2026 - Apoio a cursos de curta duração em biodiversidade,  | verificação externa | BR | sem prazo | sem | 9 | expurgo? |
| 8 | 22 | `captacao-040` | Lei de Incentivo ao Esporte - Formação Esportiva — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 23 | `captacao-052` | Projeto de inclusão pelo paradesporto — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 24 | `captacao-060` | Escolinha de natação/paradesporto adaptado — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 25 | `captacao-061` | Formação de árbitros e monitores esportivos — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 26 | `captacao-065` | Transferegov - termo de fomento para projeto educacional — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 27 | `captacao-066` | Transferegov - termo de colaboração para educação comunitária — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 28 | `captacao-091` | MDS - Segurança alimentar e nutricional — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 29 | `captacao-092` | MDS - Programa Cisternas / tecnologias sociais de água — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 30 | `captacao-093` | MDS - Sistemas alimentares circulares — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 31 | `captacao-094` | Plano Nacional de Cuidados - participação/arranjos com OSC — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 32 | `captacao-170` | FNMA - redução de vulnerabilidade climática — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 33 | `captacao-171` | FNMA - catadores e reciclagem — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 34 | `captacao-172` | FNMA - educação ambiental — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 35 | `captacao-199` | Defensoria Pública - parcerias de educação em direitos — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 36 | `captacao-207` | Acordo de cooperação sem transferência financeira — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 37 | `captacao-213` | Universidade pública - projeto de extensão com OSC — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 38 | `captacao-214` | Órgão público - chamamento para execução de política pública — Brasil | verificação externa | BR | sem prazo | sem | 10 | catálogo |
| 8 | 39 | `L-87316d7a66e04839` | Prospera Amazônia (programa 44000) | preparação | — | sem prazo | sem | 10 | expurgo? |
| 8 | 40 | `L-b34679d6e44a74a3` | Estudo de Ingressantes das Licenciaturas - Edital CAPES/INEP nº 26/2026 | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 41 | `L-ca58e967440020b4` | Além do financiamento: estudo global revela demandas das ONGs para ampliar sua resiliência | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 42 | `L-03722b231fb461ba` | Penas pecuniárias: tribunal fluminense repassa R$ 4,4 mi a 51 entidades | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 43 | `L-94711ef6f9176229` | Arquivo de Editais - Observatório do 3° Setor | preparação | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 44 | `L-75686f21585e8b1d` | Grantmaking in Brazil – iCS - Instituto Clima e Sociedade | verificação externa | BR | sem prazo | sem | 10 | expurgo? |
| 8 | 45 | `L-80c32cd482a4a857` | Edital de Convocação — EDITAL DE CONVOCAÇÃO | verificação externa | PE | sem prazo | sem | 10 | expurgo? |
| 8 | 46 | `L-329dca61fa8d537d` | Rede multidisciplinar de atenção a mães e familiares vítimas de desaparecimentos forçados  | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 47 | `L-0f21ea3b8bb0ee39` | Ação 214S - Rotas de Integração Nacional - RP2 (programa 53000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 48 | `L-52028b124d35ceb4` | ATENÇÃO INTEGRAL À SAÚDE DA CRIANÇA - POLÍTICAS DE ATENÇÃO A SAÚDE DA CRIANÇA / ACAO 5119. | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 49 | `L-d39c77d6d41a0dd1` | Programa Selo Verde Brasil (programa 28000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 8 | 50 | `L-5b9e28cf67a1612e` | NOVO PAC PATRIMÔNIO CULTURAL - OBRAS 2026 (programa 42000) | preparação | — | sem prazo | sem | 11 | expurgo? |
