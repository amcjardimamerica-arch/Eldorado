# Verificação pelo Claude no Chrome — GRUPO 3 de 3 (lote-2026-11-05-externa-completo)

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Esta é a atualização única do sistema: zerar a esteira do Cartório. Os 1.169 livros sem decisão (764 na verificação
externa, 387 na preparação, 18 na recepção — os chegados) foram divididos em 3 grupos. Este prompt é o GRUPO 3:

| O que | Quantidade | Onde |
|---|---|---|
| Livros deste grupo | 369: 137 na verificação externa, 228 na preparação, 4 na recepção | `verificacao/lotes/lote-2026-11-05-externa-completo-parte-17.json` a `-parte-24.json` (8 partes de até 50) |
| Do catálogo das oportunidades conhecidas (R44) | 16 | marca «catálogo» na tabela e o campo `catalogo` no lote |
| Sem nenhuma estrela, para validar ou expurgar | 298 | marca «expurgo?» e o campo `"verificacao_para_expurgo": true` |

Versão do lote: `gerado_em` = `2026-11-05T11:07:33+00:00`. A planilha deste grupo, `LISTA-LIVROS-VERIFICACAO-2026-11-05-GRUPO-3-de-3.xlsx`, tem os livros
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

<!-- 

Para cada um dos 16 arquivos `verificacao/expurgo/lote-chrome-documentos-*.json`, entregue um veredito completo (todos os
grupos), com o `lote` copiado do arquivo, em `verificacao/expurgo/vereditos/veredito-<nome do arquivo>.json`:

```json
{"lote": "<o nome do arquivo do lote>", "vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar",
 "motivo": "…", "titulo": "…", "orgao": "…", "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD", "trecho": "…", "livro_id": "…"}]}
```

 -->

## Ao terminar

Uma planilha de controle com o total de cada parte (entregue / não entregue) e os aprendizados que se repetiram. Nada
parcial: a parte que não foi verificada inteira não é entregue.

## A tabela dos 369 livros do GRUPO 3

Colunas: a parte do lote, a posição na parte, o livro, o título, a etapa, a UF, o prazo, a estrela, quantos dos 12 itens
faltam e a marca (catálogo = R44, nunca sai; expurgo? = sem nenhuma estrela, validar ou expurgar).

| Parte | Nº | Livro | Título | Etapa | UF | Prazo | Estrela | Faltam | Marca |
|---|---|---|---|---|---|---|---|---|---|
| 17 | 1 | `L-39a09e0e553acd09` | Call for Proposals: Small Grants Programme for Civil Society ... | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 2 | `L-934c20ad7ab817f7` | copa-de-futebol-feminino-2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 3 | `L-2d0d511e499cbed8` | Relatório Semestral | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 4 | `L-416d9cc814fbc2b0` | Operação Acolhida | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 5 | `L-47f74bc000e00d6d` | Operação Rio Grande do Sul | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 6 | `L-2801c01f40c20ed0` | Calendário 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 7 | `L-887ce50272f846ae` | Qualidade Ambiental e Meio Ambiente Urbano | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 8 | `L-631dcfb904a02204` | Últimas notícias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 9 | `L-dd5980032f620770` | Prêmio de 25 Anos do Cadastro Único | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 10 | `L-05902c3624c84c6f` | Agricultura e Pecuária | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 11 | `L-97b78eaf198e548a` | Cultura e Esporte | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 12 | `L-fbc5e6f898c712d3` | Cidadania Marajó | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 13 | `L-249a3c601eee5658` | Fórum Permanente da Sociedade Civil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 14 | `L-fc767efe8a606715` | Infraestrutura Esportiva | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 15 | `L-3f4e21b72338484b` | Arena Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 16 | `L-8e7e15128007d627` | Programa Segundo Tempo (PST) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 17 | `L-a989107b52793954` | Academia e Futebol | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 18 | `L-32554043d885ea7e` | Programa Integra | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 19 | `L-5b864445aa666d18` | Quero Emprego | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 20 | `L-40c7858ac0f64ffd` | Plano de Ação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 21 | `L-271ad50055c0fe96` | Repositório Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 22 | `L-12814fa1f3283604` | Procedimentos de Nomeação, Posse e Exercício | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 23 | `L-752878f12e8f5aeb` | Departamento de Benefícios Assistenciais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 24 | `L-656fe9fed011c89e` | Departamento de Proteção Social Básica | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 25 | `L-25938a389c51110b` | Educação e Pesquisa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 26 | `L-6f47710f7fa4c24d` | Justiça e Segurança | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 27 | `L-a84933292951c006` | Direitos do Trabalhador | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 28 | `L-a19f987129986562` | Wellington Dias conhece tecnologia que identifica áreas para construção de cisternas e hor | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 29 | `L-0c4d49ed3f9af341` | Informações Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 30 | `L-dc9c884d829c7f48` | Mapas Interativos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 31 | `L-0cfa35035f698f4f` | Histórico dos ODS no MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 32 | `L-748612544403a1d6` | Comitê Nacional de Prevenção e Combate à Tortura (CNPCT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 33 | `L-5bc04b7b733d0ea7` | População em Situação de Rua | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 34 | `L-ff7589318a906fb1` | O Jardim Botânico do Rio de Janeiro lançou dois editais de ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 35 | `L-eb42adf5dabf817c` | Projeto Paisagens Sustentáveis da Amazônia - ASL Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 36 | `L-6ec775bf09714f34` | Marcos Normativos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 37 | `L-a6173b6dbd2c855a` | Guia Lilás - Assédio moral, sexual e discriminação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 38 | `L-5ebe00abafd87eb1` | Liberdade Religiosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 39 | `L-3465552b51d76f41` | Acervo Histórico | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 40 | `L-f72d97bb1d3dbc29` | Plano Nacional dos Direitos da Pessoa Idosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 41 | `L-fc5e494ea24dc1b8` | Promoção e Defesa dos Direitos Humanos - PRÓ-DH | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 42 | `L-d8c318dbd5e30fd4` | Emenda parlamentar federal individual | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 43 | `L-5309792d585ac69f` | MDS esclarece regras dos programas sociais e alerta para notícias falsas durante as eleiçõ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 44 | `L-836ed337f16b5b33` | Cadastro de usuários externos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 45 | `L-714a589431dae219` | Conflito de Interesse | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 46 | `L-c32a5af57f8ae855` | Impacto Regulatório | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 47 | `L-26e4546f66a65efc` | Plano de Integridade: Integra+ MDHC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 48 | `L-54e2c41506b290a0` | Caravana Federativa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 49 | `L-c37c714156c62512` | Sentenças da Corte Interamericana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 17 | 50 | `L-f8b57cdefa973090` | Publicações e Referências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 1 | `L-e4a3d532e4057351` | COMIGRAR-MDHC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 2 | `L-20413e5e58893499` | Lista de Serviços | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 3 | `L-e3fb906129cada31` | Tire suas dúvidas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 4 | `L-a4ffa381cca054c1` | Pessoas em situação de rua | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 5 | `L-4f69ce8c67ebc1b9` | Acesso à Área de Trabalho | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 6 | `L-0592e2fc63b3224b` | Nº 10/26 - Manutenção preventiva na API de consulta do PNCP no ambiente de produção entre  | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 7 | `L-e2e998f3c2621e3e` | Nº 07/26 - Indisponibilidade programada do PNCP no dia 17/6/202615/6/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 8 | `L-149f854acd94778a` | Atas de Reunião do CGRNCP | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 9 | `L-4bf029fd699ae4a9` | Catálogo Eletrônico de Padronização | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 10 | `L-449a258a09e73e48` | Central de Conteúdo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 11 | `L-e38522cca1262f53` | Contrata+Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 12 | `L-63881ff6c33ecf20` | Painel para consulta de preços em dados abertos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 13 | `L-c7b9e44a1da06476` | Cadastro Nacional de Empresas Inidôneas e Suspensas (CEIS) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 14 | `L-6722c54a288926bc` | Transparência | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 15 | `L-ed236090519897da` | Onde atuamos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 16 | `L-f3a523a34749f835` | Instituições financeiras credenciadas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 17 | `L-497f3915265652da` | Plano Brasil Soberano 2026Conheça as novas medidas de apoio às empresas afetadas pela inst | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 18 | `L-d09485aa0bcb2b67` | Serviços online | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 19 | `L-e17110f6285fc760` | Consulta a financiamentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 20 | `L-959feb20065a13b1` | Moedas contratuais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 21 | `L-1a969dc86a2e0100` | 6Obter passaporte e outros documentos de viagem | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 22 | `L-c211eab258ce2446` | 4th Call for Proposals: Brazil – gpsa | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 23 | `L-8218fddf08e9e8cd` | Materiais e Publicações | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 24 | `L-6b7d14577f5bb994` | Manual de Gestão de TEDs do MDS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 25 | `L-fa38d2fe57d51405` | Saiba mais sobre os programas vigentes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 26 | `L-0cc3b768478357db` | Programa União com Municípios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 27 | `L-7a95333e6f3eaca6` | Campanha de Prevenção aos Incêndios Florestais 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 28 | `L-ab2d55d18657079d` | Saiba mais sobre MMA abre inscrições para representantes da sociedade civil na Comissão Na | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 29 | `L-a6433823aaadfdf1` | O Instituto Impactarte está com inscrições abertas para o ciclo 2026 ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 30 | `L-2dae61b2e5b80b7c` | Saiba mais sobre MMA atualiza lista nacional de plantas ameaçadas de extinção | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 31 | `L-13ff6591c6d68b39` | Call for Proposals / UNEP - UN Environment Programme | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 32 | `L-13a66337fad770fa` | Open grant — Call for Projects Promoting ... - DevelopmentAid | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 33 | `L-ea2dcadf3eb0b967` | EDITAL Nº009/2026-EJs/DEX/PROEC/ UEMS EDITAL DE FLUXO CONTÍNUO PARA PROJETOS DE EXTENSÃO V | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 34 | `L-2a158e5f4944f50e` | Search for grants in Brazil — DevelopmentAid | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 35 | `L-730d08e3bf38f9bb` | The Path of Grantmaking: How Brazil Fund gets resources to those ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 36 | `L-98599d1056fd7e23` | edital n° 54/2026/sei-inpa (fluxo contínuo) - GOV.BR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 37 | `L-4268cee9bd5177fa` | Edital de Abertura de Inscrições – SAEB nº 04/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 38 | `L-44261059b2360c26` | PROGRAMA FUNARTE MEMÓRIA DAS ARTES | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 39 | `L-c8d5edbc6edb484b` | Edital de Fluxo Contínuo Nº 02/2026 DEX/PROEC/UEMS (Programas, Projetos e Cursos) | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 40 | `L-5122868b5323b845` | GT discute cooperação entre assistência social e Sistema de Justiça | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 41 | `L-c29b3f393b72667e` | EDITAL Nº 003/2026 - RELATÓRIOS/EVENTOS-DEX/PROEC/UEMS | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 42 | `L-a32cc23448866a0a` | Sisan promove Encontro Regional para fortalecer a governança participativa e intersetorial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 43 | `L-2c540e9e12d76a3a` | @vanessaeobicho SEBRAE ABRE EDITAL DE R$ 7,4 MILHÕES ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 44 | `L-0c56e42ece5c3d8b` | EDITAL DE CHAMAMENTO PÚBLICO Nº 14/2026 - PREMIAÇÃO DE PONTOS E PONTÕES DE CULTURA | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 45 | `L-1431232a219af3a0` | EDITAL DE CHAMAMENTO PÚBLICO 13/2026 - FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 46 | `L-d212a3de6b2de37a` | Resultado Definitivo do Edital de Chamamento Público nº 01/2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 47 | `L-30ed7ff62719905b` | Aviso de Credenciamento — AVISO DE CREDENCIAMENTO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 48 | `L-bf5ce760538b1837` | Aviso de Chamamento Público — AVISO DE LICITAÇÃO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 18 | 49 | `L-4fce280f65fec5b9` | Ministério do Esporte aprova 32 projetos para captar recursos via Lei ... | preparação | — | sem prazo | sem | 12 | expurgo? |
| 18 | 50 | `L-40ec576676f5c197` | Criança Esperança - Edital - UNESCO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 1 | `L-1180fcb520026cc9` | Chamada Aberta 2026 - Instituto ACP - Plataforma Conjunta | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 2 | `L-7adafd9f5cf784f2` | Notícias e Conteúdo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 3 | `L-99596629e238a756` | Marcas e Manuais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 4 | `L-8ca3c7315a94f6d9` | Coleção de Notícias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 5 | `L-3d1b7b54e5cd3d79` | Boletins | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 6 | `L-b8abbb6db7d287d7` | MDS Informa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 7 | `L-871c0e6ae30919b5` | Boletins Anteriores | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 8 | `L-3a7b977284ddacd1` | Condutas Vedadas Aos Agentes Públicos Federais Em Eleições | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 9 | `L-6df300e34c7ae5b1` | III Encontro do Programa Cozinha Solidária debate soberania e segurança alimentar no Brasi | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 10 | `L-6a1f09fed9e6a85e` | Adaptação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 11 | `L-024413416cefb98a` | ReCAATINGAR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 12 | `L-b5007188c1d0a855` | Plano Nacional de Desenvolvimento Sustentável de Povos e Comunidades Tradicionais (PDPCT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 13 | `L-7858087d4818d5e3` | Saiba mais sobre MMA contribui para capítulo brasileiro do relatório global sobre o estado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 14 | `L-b8ff5a9baf9506ab` | Na Frequência dos Nossos Direitos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 15 | `L-b21286bd9fc74c43` | SECOND PUBLIC CALL FOR CIVIL SOCIETY ORGANIZATIONS TO ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 16 | `L-ef64ea06fd41c7c3` | Open grant — Call for Projects to Support Kaiowá ... - DevelopmentAid | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 17 | `L-aa6778ddcc24aff8` | O Instituto EDP está com inscrições abertas para a Chamada EDP ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 18 | `L-d54f311c90882223` | Saiba mais sobre MMA disponibiliza guia para apoiar comunidades no enfrentamento de evento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 19 | `L-b7b2412fc99cd4c5` | Resultado de Habilitação — RESULTADO DE HABILITAÇÃO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 20 | `L-25bebfec1ddd39ce` | Edital de Concurso Público — EDITAL, DE 29 DE OUTUBRO DE 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 19 | 21 | `L-53facee2c2ef37c4` | Instituto Ronald inicia obra da 1ª Casa Ronald McDonald verde do sistema global - Diário P | preparação | — | sem prazo | sem | 6 | expurgo? |
| 19 | 22 | `L-079fc16ca2d44163` | Convocatoria de Proyectos Sociales Cooperación internacional 2026 | preparação | — | sem prazo | sem | 9 | expurgo? |
| 19 | 23 | `L-1ed918f727a5d53a` | Subvenciones 2026 para ONGs: financiamiento internacional del GFCF - Noticias con Causa | preparação | — | sem prazo | sem | 9 | expurgo? |
| 19 | 24 | `captacao-242` | PNUD – Small Grants Programme — Internacional | verificação externa | IN | sem prazo | sem | 10 | catálogo |
| 19 | 25 | `captacao-248` | Open Society Foundations — Internacional | verificação externa | IN | sem prazo | sem | 10 | catálogo |
| 19 | 26 | `captacao-250` | Gates Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 27 | `captacao-253` | Microsoft Philanthropies — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 28 | `captacao-258` | Skoll Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 29 | `captacao-260` | Oak Foundation — Internacional | verificação externa | IN | sem prazo | sem | 11 | catálogo |
| 19 | 30 | `captacao-240` | UNESCO – Fundo Internacional para Diversidade Cultural — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 31 | `captacao-243` | Banco Mundial – Social Development Grants — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 32 | `captacao-244` | BID – Laboratório de Inovação — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 33 | `captacao-245` | USAID – Grants Globais — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 34 | `captacao-246` | União Europeia – Erasmus+ — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 35 | `captacao-247` | União Europeia – EuropeAid — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 36 | `captacao-249` | Ford Foundation — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 37 | `captacao-252` | Meta Community Grants — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 38 | `captacao-254` | Global Fund for Women — Internacional | verificação externa | IN | sem prazo | sem | 12 | catálogo |
| 19 | 39 | `L-18a73cab13e388ed` | International Foundation Grant 2026: Complete Application Guide, Timeline, and Funding Opp | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 40 | `L-876c833a355a72f4` | Top Grant Opportunities for NGOs in 2026: Global Calls, Tips &amp; Funding Trends / Grants | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 41 | `L-23d6ecb1933088b6` | Homepage - Global Fund for Children | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 42 | `L-f35d772f5f05fcc8` | Grants for NGOs: Global Database of Funding Opportunities / GrantsDatabase | preparação | — | sem prazo | sem | 12 | expurgo? |
| 19 | 43 | `L-97988670a73d9d1c` | Edital FAPESPA 2026: Mapeamento Turístico Ilha do CombuR$ 544 mil | preparação | PA | aberta | prata | 3 |  |
| 19 | 44 | `L-40ba051fb8149a8e` | Chamamento Público Bálsamo SP 2026: Edital OSCIPaté 05 de nov. de 2026 | verificação externa | SP | aberta | prata | 3 |  |
| 19 | 45 | `L-11dc0e0f3a777a2a` | CHAMADA PÚBLICA 019/2026 – Diagnóstico da População IdosaR$ 543 mil·até 07 de nov. de 2026 | preparação | PA | aberta | bronze | 1 |  |
| 19 | 46 | `L-9c499faba441537f` | Edital Guaraí 2026: R$ 656 mil para Assistência SocialR$ 656 mil·até 06 de nov. de 2026 | verificação externa | TO | aberta | prata | 2 |  |
| 19 | 47 | `op-583de98c37cc` | 2º Edital Social Instituto Porto 2026: até R$ 200 mil por OSC (2 vagas, Grande SP e Grande | verificação externa | MG | aberta | ouro | 0 |  |
| 19 | 48 | `op-83594f2b678d` | Gráfica do Exército — AVISO DE CHAMAMENTO PÚBLICO Nº 1/2026 — é selecionar as associações  | recepção | DF | aberta | bronze | 1 |  |
| 19 | 49 | `L-49d853c2cd4c4a55` | chamada publica 0202026 projeto reciclagem economia circular diagnosti 0dduyb | preparação | PA | aberta | bronze | 2 |  |
| 19 | 50 | `op-863b91d555e7` | Chamamento SEJUS-PI 02/2026 (APEC em Parnaíba, Picos e Floriano; R$ 700,9 mil por parceria | recepção | PI | aberta | bronze | 1 |  |
| 20 | 1 | `L-3a84848a5c807132` | BiodivFuture 2026 – Edital FAPESB para Novos EcossistemasR$ 255 mil·até 11 de nov. de 2026 | preparação | BA | aberta | bronze | 2 |  |
| 20 | 2 | `L-e6c95a125ceb6d1a` | Edital Fundação Araucária Biodiversa+ 2026R$ 300 mil·até 16 de abr. de 2027 | preparação | PR | aberta | bronze | 2 |  |
| 20 | 3 | `op-dd4903d7e5ec` | Chamamento SEJUS-PI 03/2026 (CIAP de Altos/PI, R$ 803 mil) com prazo até 20/10/2026 confir | recepção | PI | aberta | bronze | 4 |  |
| 20 | 4 | `op-cc360a72c619` | Projetos sustentáveis no Cerrado e na Caatinga — Brasil | preparação | MA | aberta | bronze | 1 |  |
| 20 | 5 | `op-a17291a54c03` | OURO (sem repasse, nicho museológico). Edital de credenciamento do Sonhar o Mundo 2026 (SI | preparação | SP | aberta | prata | 1 |  |
| 20 | 6 | `nova-63ac222433cf` | Sonhar o Mundo 2026 abre inscrições para instituições culturais de São Paulo — Brasil | preparação | SP | aberta | prata | 2 |  |
| 20 | 7 | `L-50c619d159861208` | Edital de Chamamento Público destinado projetos sociais voltados à promoção e à garantia d | verificação externa | — | aberta | prata | 1 |  |
| 20 | 8 | `L-9714c53d1fae6b2a` | Edital 4ª Chamada Economia Azul 2026 – Fundação AraucáriaR$ 495 mil·até 14 de jun. de 2027 | preparação | PR | aberta | bronze | 2 |  |
| 20 | 9 | `L-66d5fa8939b32fff` | IFSP - Portal Institucional - IFSP - Portal Institucional | preparação | SP | aberta | bronze | 1 |  |
| 20 | 10 | `L-573e7ff053c0b798` | Edital 03/2026-DRI/UEMS. Edital de fluxo contínuo para propostas de ações de internacional | preparação | MS | aberta | bronze | 4 |  |
| 20 | 11 | `L-075b7ba9539c89c2` | Quintais Produtivos para Mulheres – Edital 04/2026 Anateraté 20 de nov. de 2026 | verificação externa | MG | aberta | ouro | 0 |  |
| 20 | 12 | `op-983526e6e043` | SUP. EST. DE LICITACAO — O presente Chamamento Público tem por objeto selecionar Organizaç | preparação | RO | aberta | bronze | 1 |  |
| 20 | 13 | `L-2dfe5adaa7808b72` | Expoagro Afubra 2027 abre inscrições para o Pavilhão da Agricultura Familiar | preparação | RS | aberta | bronze | 2 |  |
| 20 | 14 | `L-2529e074a2454eac` | Diário oficial de Mogi Guaçu (2026-10-27) | preparação | — | aberta | bronze | 2 |  |
| 20 | 15 | `L-e6b9b1a5607c82d4` | POLÍTICAS DE FOMENTORio Preto abre editais com R$ 756 mil para Pontos de Cultura | preparação | SP | aberta | bronze | 3 |  |
| 20 | 16 | `L-48e828b7e3dc4ec4` | Edital CMDCA Tubarão 003/2026 – Captação de R$200 milR$ 200 mil·até 24 de nov. de 2026 | preparação | SC | aberta | bronze | 2 |  |
| 20 | 17 | `op-ce08d2d6b36e` | MUNICIPIO DE RIO DE JANEIRO — Credenciamento de instituições privadas, sem fins lucrativos | preparação | RJ | aberta | bronze | 1 |  |
| 20 | 18 | `L-1b197365c9a028d0` | Edital SMADS 2026: Abrigo 24h em São Pauloaté 27 de nov. de 2026 | preparação | SP | aberta | bronze | 1 |  |
| 20 | 19 | `op-2f2e856a2474` | Programa Nutrir+ — Brasil | preparação | MS | aberta | bronze | 2 |  |
| 20 | 20 | `op-7eaa1477335f` | DEFENSORIA PUBLICA DO ESTADO DO PARANA — O objeto do presente credenciamento selecionar as | preparação | PR | aberta | bronze | 1 |  |
| 20 | 21 | `op-bdda6f400ec9` | IFood Chega Junto – 2ª edição — Brasil | preparação | BA | aberta | bronze | 2 |  |
| 20 | 22 | `L-fd5c67612e5c6c88` | Edital CAPES 11/2026 – Cátedra Jorge Amado 2026até 31 de dez. de 2026 | preparação | SP | aberta | bronze | 2 |  |
| 20 | 23 | `op-ccab18422744` | Edital 001/2026 de Cadastro de Projetos do Programa de Incentivo ao Esporte - PIE — Brasil | preparação | SC | aberta | bronze | 3 |  |
| 20 | 24 | `op-1bf6c28ac27d` | OURO (sem repasse). CP00126 da CPTM (São Paulo/SP): credenciamento de associações e cooper | preparação | SP | aberta | bronze | 2 |  |
| 20 | 25 | `op-4d6ae06a4182` | (UO) ESP-CIA.PTA DE TRENS METROPS-CPTM — Credenciamento de associações e/ou cooperativas d | preparação | SP | aberta | bronze | 2 |  |
| 20 | 26 | `L-20ad275e2117b5d6` | Seleção de empreendimentos de saneamento 2026 – PCJ SPR$ 12,0 mi·até 16 de mai. de 2027 | preparação | SP | aberta | bronze | 3 |  |
| 20 | 27 | `op-b69ca4f1c758` | MINAS GERAIS SECRETARIA DE ESTADO DA EDUCACAO — Reabertura do Edital de Credenciamento SEE | preparação | MG | aberta | bronze | 2 |  |
| 20 | 28 | `op-e2c38bc30cbe` | MUNICIPIO DE BOA VISTA — credenciamento de Instituições de Longa Permanência para Idosos – | preparação | RR | aberta | bronze | 1 |  |
| 20 | 29 | `op-4c282607bda1` | TRIBUNAL REGIONAL ELEITORAL DO AMAZONAS — O presente procedimento tem por objeto seleciona | preparação | AM | aberta | bronze | 3 |  |
| 20 | 30 | `op-9150ca832311` | Seleção pelo TRE-AM de associações/cooperativas de catadores para Acordo de Cooperação Téc | preparação | AM | aberta | bronze | 3 |  |
| 20 | 31 | `op-185651c7ce6e` | UNIVERSIDADE FEDERAL DE PERNAMBUCO — Selecionar e habilitar as associações e/ou cooperativ | preparação | PE | aberta | bronze | 3 |  |
| 20 | 32 | `op-10a5e444491f` | DNIT-DEPARTAMENTO NACIONAL DE INFRAEST DE TRANSPORTES — Seleção de associações e/ou cooper | preparação | DF | aberta | bronze | 2 |  |
| 20 | 33 | `op-282b8b176c85` | TRIBUNAL SUPERIOR DO TRABALHO — Seleção de associações e cooperativas de catadores de mate | preparação | DF | aberta | bronze | 1 |  |
| 20 | 34 | `op-66ca048d7db5` | TRIBUNAL DE JUSTICA DO ESTADO DO TOCANTINS — Credenciamento de associação e/ou cooperativa | preparação | TO | aberta | bronze | 2 |  |
| 20 | 35 | `op-9c790ce7af74` | OURO (sem repasse). Credenciamento do TJTO (Projeto Coleta Seletiva Solidária) para associ | preparação | TO | aberta | bronze | 2 |  |
| 20 | 36 | `op-628b281e0b9e` | TRIBUNAL DE JUSTICA DO ESTADO DE ALAGOAS — [LICITANET] - Chamamento público na forma de cr | preparação | AL | aberta | bronze | 2 |  |
| 20 | 37 | `op-e0f66703f6ec` | OURO (sem repasse). Credenciamento 002/2024 do TJAL para associações/cooperativas de catad | preparação | AL | aberta | bronze | 2 |  |
| 20 | 38 | `op-03c70c51481b` | FUNDACAO UBERLANDENSE DO TURISMO ESPORTE E LAZER — Credenciamento de interessados (terceir | preparação | MG | aberta | bronze | 3 |  |
| 20 | 39 | `op-6b8887bef5bb` | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento TRT4 n° 01/2023 Credenciamento de associaçõ | preparação | RS | aberta | bronze | 1 |  |
| 20 | 40 | `op-f1f571748e91` | OURO (sem repasse). Credenciamento 001/2023 do TRT4 (republicado no PNCP em 2024) para ass | preparação | RS | aberta | bronze | 2 |  |
| 20 | 41 | `op-8b2f0d2c3ce4` | Edital 1/2025 do IFSULDEMINAS Campus Inconfidentes: credenciamento contínuo (desde 14/01/2 | preparação | MG | aberta | bronze | 2 |  |
| 20 | 42 | `op-07dfbfa866be` | TRIBUNAL SUPERIOR DO TRABALHO — Credenciamento de Cooperativas ou Associações de catadores | preparação | MA | aberta | bronze | 2 |  |
| 20 | 43 | `op-9c8606e47e7b` | OURO (sem repasse). Credenciamento 01/2025 do TRT16 (São Luís/MA) para cooperativas/associ | preparação | MA | aberta | bronze | 2 |  |
| 20 | 44 | `op-cc39b07683ca` | TRIBUNAL SUPERIOR ELEITORAL — Credenciamento de associações e/ou cooperativas de catadores | preparação | RN | aberta | bronze | 2 |  |
| 20 | 45 | `op-f1ca705ce530` | MINISTERIO PUBLICO DO ESTADO DO PARANA — Selecionar associação e/ou cooperativa de catador | preparação | PR | aberta | bronze | 2 |  |
| 20 | 46 | `L-795796b7b9b5e89f` | Sâmia lança edital de emendas para 2026 com foco em participação popular e transparência / | recepção | SP | encerrada | bronze | 8 |  |
| 20 | 47 | `op-4ff34a354f68` | Assistência para Projetos Comunitários e de Segurança do Ser Humano (APC) Consulado Geral  | verificação externa | IN | aberta | prata | 2 |  |
| 20 | 48 | `L-660f394c44569035` | Junte-se à Causa - ONG Banco de Alimentos | preparação | — | sem prazo | sem | 2 | expurgo? |
| 20 | 49 | `L-ba3abbbfa2d0541b` | Banrisul Instituto Cultural e Social — Edital Merece! | preparação | RS | sem prazo | sem | 3 | expurgo? |
| 20 | 50 | `L-a517e18d1a45e03a` | edital chamada publica fapesc 392026 nucleo catarinense mobilidade rh8huo | preparação | SC | sem prazo | sem | 3 | expurgo? |
| 21 | 1 | `L-cd1c83b681badd00` | edital fapesbsecticnpqcapes 112026 profix fapesb fqh8qr | preparação | BA | sem prazo | sem | 3 | expurgo? |
| 21 | 2 | `L-a3f35daeb64685e7` | Receba Doações de Alimentos para sua ONG / Optima ESG | preparação | — | sem prazo | sem | 3 | expurgo? |
| 21 | 3 | `L-63588cc5032d65e6` | 2025: Gestão e Destinação de Valores e Bens Oriundos de Prestações Pecuniárias, da Pena de | preparação | BA | sem prazo | sem | 4 | expurgo? |
| 21 | 4 | `L-55c8ba27edde2f80` | Campanha de Doação de Alimentos: sua empresa pode fazer a diferença! - ONG Banco de Alimen | preparação | — | sem prazo | sem | 4 | expurgo? |
| 21 | 5 | `L-ff0c957845fa0e39` | Hasta el 1 de marzo: convocatorias abiertas para fondos en apoyo a organizaciones de la so | preparação | — | sem prazo | sem | 4 | expurgo? |
| 21 | 6 | `L-cc504de968ded6c2` | PDF Chamada Pública Nº 2026/011 - fbb.org.br | preparação | — | sem prazo | sem | 4 | expurgo? |
| 21 | 7 | `captacao-037` | Programa Rouanet Juventude — Brasil | verificação externa | AC | sem prazo | sem | 5 | catálogo |
| 21 | 8 | `L-f514965d7a8ed4f5` | chamada publica fapespa 0112026 fapespadiepsac fapespa clgedv | verificação externa | PA | sem prazo | sem | 5 | expurgo? |
| 21 | 9 | `L-d6c95c4c8153bb5e` | Convocatoria de manifestación de interés de proyectos de 2026 para las OSC | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 10 | `L-d26f1b33cc343f81` | Annual Report: The Brazil Fund has granted R$ 32 million (circa ... | preparação | RJ | sem prazo | sem | 5 | expurgo? |
| 21 | 11 | `L-37fc4ba798db9f75` | Funai doa R$ 15,6 mil em equipamentos de informática para inclusão digital | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 12 | `L-570b4d9c30337943` | INSTRUÇÃO SOBRE DOAÇÕES DEDUTÍVEIS E RESPONSABILIDADE SOCIAL CORPORATIVA NO REGIME TRIBUTÁ | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 13 | `L-c63ad1020681af8a` | Edital abre inscrições para ONGs e coletivos de periferias no Acre / G1 | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 14 | `L-9ad0609b81817dc5` | Capta: Guia de elaboração de projetos socioambientais | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 15 | `L-4bfbc950302fb835` | Sesc Mesa Brasil RJ - Portal Sesc RJ | preparação | RJ | sem prazo | sem | 5 | expurgo? |
| 21 | 16 | `L-f6fa018898a60f1b` | Empresa apoiando ONG em Goiânia / Parcerias com o Anjos | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 17 | `L-33d2d68328987b08` | Educação afrocentrada impacta alunos de escola quilombola em ... | preparação | — | sem prazo | sem | 5 | expurgo? |
| 21 | 18 | `L-8bc89b8bf7cf8ce7` | premiacao ira reconhecer aplicativos sobre saude e adolescencia | verificação externa | SP | sem prazo | sem | 6 | expurgo? |
| 21 | 19 | `L-f2f712236237ed4e` | Entre as 100 Melhores ONGs do Brasil e a Melhor do Piauí 2026! | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 20 | `L-8ddabb10bd5bd2f6` | Home / Melhores ONGs 2026 | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 21 | `L-f6655472345a0c42` | Home - Solidaridad Southamerica | preparação | PA | sem prazo | sem | 6 | expurgo? |
| 21 | 22 | `L-c945c2ed03c82a83` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 &#8211; GS Notícias | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 23 | `L-12a0367ea70a629f` | FUNDO VERDE DO CLIMA - Organização credenciada junto ao Fundo Verde do Clima. | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 24 | `L-7cc1b0f2372bd58a` | Casa do Pequeno Cidadão Nossa Senhora Aparecida: ONG SAICA ... | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 25 | `L-bcc53ffeab547f08` | Fundação Ford &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 26 | `L-ffcd3d9da3aa896c` | Patrocínios Instituto Claro &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 27 | `L-f8334e1e5f147a02` | Subsídio de Desenvolvimento Comunitário &raquo; Capta | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 28 | `L-fed0b22b22b75cfb` | CONVOCATORIA A PROYECTOS 2026 &#8211; MAR Fund &#8211; Protecting the Mesoamerican Reef | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 29 | `L-d1c185917a73f263` | Funai doa equipamentos de informática para programa de inclusão digital | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 30 | `L-c666dec7c68e386b` | PDF Edital OIJ Digilendo - Projeto Juventudes entre Páginas | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 31 | `L-fc54028dc3c36386` | Funai oficializa doação de equipamentos de informática para programa de inclusão digital | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 32 | `L-2ca4245a6409ad89` | Sicredi UniEstados e Icatu Seguros se unem para apoiar o Cricket Brasil na temporada 2026 | preparação | MG | sem prazo | sem | 6 | expurgo? |
| 21 | 33 | `L-64517a5e9ce64fcc` | Campanha &#8211; ONG AJUDI | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 34 | `L-b4dae80037c9aa60` | CONTRATO DE PATROCÍNIO 2026-2032 PREÂMBULO - agse.pt | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 35 | `L-b0e6e042cb3db10d` | Projeto de reciclagem de aparelhos eletrônicos ajuda moradores da periferia de Teresina /  | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 36 | `L-1da85134248f32d1` | Doação de alimentos por supermercados e estabelecimentos similares - Agenda do Comércio | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 37 | `L-8617d8e7718c68ea` | Mercado imobiliário goianiense se mobiliza para natal solidário / AutImob | preparação | — | sem prazo | sem | 6 | expurgo? |
| 21 | 38 | `L-2df363053b2b5734` | 21/10/2026 09:30Matérias Novas/Relatórios Entregues e prazo de emendas | verificação externa | BA | sem prazo | sem | 7 | expurgo? |
| 21 | 39 | `L-7373afbbea9266b8` | Captação de Recursos para ONGs: Guia Completo 2026 / COREGOV | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 40 | `L-0ec44d941104e289` | Associações e Credenciamentos - Fundación Avina | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 41 | `L-5d7e80665ffb8e16` | Dana doa novo lote de computadores para ONGs por meio da Fundação Pensamento Digital - Dan | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 42 | `L-1911e5f17a5b7e87` | PDF e-book CMVC_VoluntariadoCorporativonasOSCS | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 43 | `L-673efc4b9d04a53f` | 20 lugares para prestar serviços voluntários em Goiânia | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 44 | `L-1970a4dcbd973801` | Doação de Móveis: 9 ONGs para Doar [INFOGRÁFICO] - LBV | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 45 | `L-3b1bcef37839edd9` | ADFEGO &#8211; Associação dos Deficientes Físicos do Estado de Goiás | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 46 | `L-77be7bc5cbd5a504` | Fundo Brasil abre editais para doação milionária a organizações sociais / VEJA | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 47 | `L-f925b7f259a3c575` | UNAIDS divulga lista final de ONGs com projetos aprovados no Edital para ações nos territó | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 48 | `L-405b48dbdb8fb4fa` | Fazer o Bem Faz Bem - JBS | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 49 | `L-49b9f3233d996e64` | Cenário da Infância e Adolescência no Brasil 2026 | preparação | — | sem prazo | sem | 7 | expurgo? |
| 21 | 50 | `L-c1b952a9515669c8` | Captar recursos é o principal desafio para 74% das ONGs - 03/09/2026 - Folha Social+ - Fol | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 1 | `L-9a8137d12285a656` | Troco solidário - Havan | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 2 | `L-4a7e8597605d946b` | Financiamento de OSCs no Brasil: desafios e caminhos | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 3 | `L-a7a7a9b1e4fd0223` | GoodTruck / Comida para a alma / Faça parte | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 4 | `L-cb724e87f462e7b6` | Conheça ONGs que ajudam no combate à fome no Brasil e saiba como colaborar / CNN Brasil V& | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 5 | `L-c7e99c7f3b1f78b4` | O Projeto &#8211; ONG AJUDI | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 6 | `L-04bc431438550011` | ¿Dónde buscar fondos filantrópicos en 2026? - Propel | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 7 | `L-55d5920e90ff984f` | Ato — AVISO DE CHAMAMENTO PÚBLICO - FAR Nº 8/2026 | verificação externa | PE | sem prazo | sem | 7 | expurgo? |
| 22 | 8 | `L-836dda4a33f9eabb` | 7Minutos - Ações sociais em Goiânia resultam na entrega de alimentos e agasalhos para enti | preparação | — | sem prazo | sem | 7 | expurgo? |
| 22 | 9 | `L-6d637c8a87ee06e3` | ONG Banco de Alimentos - Combate à fome e ao desperdício de alimentos | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 10 | `L-e950023e1a174790` | Servizio Civile 2026: Tante opportunità in Italia e all’estero con le ONG - Info-Cooperazi | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 11 | `L-13429cf05482d5c1` | ¿Dónde encontrar fondos para tu ONG en América Latina? - Propel | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 12 | `L-dd0a76bd31180d24` | AIDS 2026: Guía completa para la sociedad civil | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 13 | `L-ac35f7c8dd0109e5` | Como doar computadores usados? &#8211; Blog do Exército de Salvação | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 14 | `L-aee206446c017faf` | Matching de doações: por que esse modelo está crescendo nas empresas - GiftAid | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 15 | `L-e97609e8454afaa8` | DOAÇÃO EQUIPAMENTOS - Ecodigital | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 16 | `L-c23e12381bd62040` | Plataforma Conjunta / Apoios de Resposta Rápida (ARRs) para Movimentos Feministas da Améri | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 17 | `L-153c9ed2532240f4` | Premia��o, limite de atletas e times participantes: veja o regulamento da Libertadores Fem | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 18 | `L-6ebf6db4a9c8ea71` | Comunidade de Mulheres na Tecnologia - WoMakersCode | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 19 | `L-b5d2df33b966c0c9` | Patrocínios da Havan: saiba como inscrever seu projeto - Blog Havan | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 20 | `L-fe3f62d26e5f4699` | Seleção da Havan para patrocínios, projetos e doações — prazo não ... | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 21 | `L-a634ec5d484827df` | Trackmob - Tudo para você captar mais e melhor! | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 22 | `L-bc197c2c1f0c5c97` | 10 instituições que precisam de voluntários e doações em Goiânia e Aparecida - Jornal Opçã | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 23 | `L-6d2b28ebc4b8e555` | WILDLIFE CONSERVATION SOCIETY PROYECTO GEF MANEJO ... | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 24 | `L-a87e6d37de583756` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 25 | `L-08849379c561c598` | Inscrições para delegação do Brasil na COP31 vão até domingo | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 26 | `L-0a64b27e80ec0dbd` | Não queremos apenas dar um cheque, diz VP da Rockefeller - 17/07/2026 - Folha Social+ - Fo | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 27 | `L-07bc668fb81f67b7` | ¡La convocatoria de solicitudes para las pre-sesiones 53 está abierta! / UPR Info | preparação | — | sem prazo | sem | 8 | expurgo? |
| 22 | 28 | `L-95bc21a2a83d82cc` | InstitutoMoveisParaTodos - Doação | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 29 | `L-839abb68d3820339` | ACNUDH / Convocatoria para aportar información para la visita del Relator Especial sobre l | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 30 | `L-4d8eab0bee9bdc3e` | Fundo Canadá para Iniciativas Locais - Repórter Brasil | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 31 | `L-8357148fc31cd8c6` | Financiamento para o Bem: Inovação e Impacto Social 2025-... — Líder Social | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 32 | `L-5b2d20365b991906` | ONGs, Fundaciones y Cooperación en Latinoamérica / Consultorías, Formación y Grants | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 33 | `L-52b050b893115bf3` | Fondo Casa Brasil: 100 iniciativas comunitarias reciben R$ 20 mil cada una / LideraFest | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 34 | `L-b33df43e668c8d28` | Reforma Tributária no Terceiro Setor: O Limite entre Doação e Patrocínio | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 35 | `L-fb990014a66298d9` | Programa de Doação Microsoft / TechSoup Brazil | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 36 | `L-60f978bc06727426` | Schneider Electric reúne empresas para doação de 70 equipamentos solares com o objetivo de | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 37 | `L-5b6039574f554786` | Dedução do IR para Pronon e Pronas/PCD é prorrogada até 2031 | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 38 | `L-552fa963d68d16e4` | Programa auxilia indústrias com móveis e equipamentos de informática para doar / FIESC | preparação | SC | sem prazo | sem | 9 | expurgo? |
| 22 | 39 | `L-0ce0980e42a7eaf2` | Aiuti all’Africa in cambio di rimpatri: la clausola che svuota la cooperazione Ue &#8211;  | preparação | — | sem prazo | sem | 9 | expurgo? |
| 22 | 40 | `L-28f1f34b1bb2b4b5` | Subvenciones / EEAS | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 41 | `L-357b243716706f71` | FEDDAi / Espace de Partage pour la Société Civile et les Partenaires en Mauritanie | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 42 | `L-837204dfcb47bd94` | Festival ABCR 2026 – Captação de Recursos e Filantropia | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 43 | `L-382acc04fb9fbf57` | Convocatoria de proyectos de reflexión sobre retos sociales / Palau Macaya | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 44 | `L-182a578567c039ce` | Convocatoria de propuestas para 2026 | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 45 | `L-817e8b9220796a1a` | Setpar Solidária / Quando nos unimos, nos fortalecemos! - Setpar Empreendimentos | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 46 | `L-db069a0458f8fffa` | Legislação Ambiental 2026: ONGs, Conformidade e Financiamento - projetosocialbrasil.com.br | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 47 | `L-ddeda00a5f6149d4` | Kellogg Foundation Grants 2026 / How to Apply | preparação | — | sem prazo | sem | 10 | expurgo? |
| 22 | 48 | `L-c2d86d00fa66d9fe` | Renforcement des organisations de la société civile en Amérique Latine &#8211; Fondation N | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 49 | `L-467d9bbb630653f8` | Nexans - Appel à Projets | preparação | — | sem prazo | sem | 11 | expurgo? |
| 22 | 50 | `L-4ac0195dea79f9be` | Organisation de la société civile (OSC) / AFD - Agence Française de Développement | preparação | — | sem prazo | sem | 11 | expurgo? |
| 23 | 1 | `L-3badc1fa169d77e6` | Appels d’offres, grants et subventions en Afrique 2026 / VueRadar | preparação | — | sem prazo | sem | 11 | expurgo? |
| 23 | 2 | `L-723211919c9daaf5` | Costa Rica (MS): ......................................................................... | preparação | MS | sem prazo | sem | 12 | expurgo? |
| 23 | 3 | `L-97f88d42e0091dec` | Curitiba (PR): • • •     Licitações    SECRETARIA DO GOVERNO MUNICIPAL - SGM  SECRETARIA M | preparação | PR | sem prazo | sem | 12 | expurgo? |
| 23 | 4 | `L-b6d8e3e0168925b3` | Maragogipe (BA): Ladeira da Laje Maragojipe – Bahia – CEP – 44420-000  Tel. – (75) 3526 29 | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 5 | `L-af8db3e1ea4420b3` | Uberaba (MG): ............................................................................ | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 23 | 6 | `L-0c5af32cda2c3fb4` | Uberaba (MG): ............................................................................ | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 23 | 7 | `L-d1cc925b553d99e6` | Marechal Deodoro (AL): Pecuária, Pesca e Aquicultura.      Prazo para envio das propostas: | preparação | AL | sem prazo | sem | 12 | expurgo? |
| 23 | 8 | `L-c5439a10a22259e4` | Florianópolis (SC): Edição Nº. 4287  Controladoria Geral do Município                NUP/I | preparação | SC | sem prazo | sem | 12 | expurgo? |
| 23 | 9 | `L-934d349f4bef73e8` | Florianópolis (SC):  22/10/2026 Edição Nº. 4288  Sumário Secretaria Municipal da Casa Civi | preparação | SC | sem prazo | sem | 12 | expurgo? |
| 23 | 10 | `L-59b91bbf350473d9` | Niterói (RJ): Ribeiro Monteiro Junior, publicadas em 17/10/2026, onde  se lê: 1397 e 1398/ | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 23 | 11 | `L-3fdea4997a1af232` | Palmas (TO): Palmas, para  responder interina e cumulativamente pela Pasta, pelo período d | preparação | TO | sem prazo | sem | 12 | expurgo? |
| 23 | 12 | `L-97b2b6a16e8b8ff8` | Taubaté (SP): Educação - SEED ......................................... 28  Portaria SEED  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 13 | `L-07ebe6569a211a38` | Santos (SP): �������������������������������������������������������������� 2  FINANÇAS E  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 14 | `L-761baf0dc4c61694` | Campo Grande (MS): Lopes Vice-Prefeita.................................................... | preparação | MS | sem prazo | sem | 12 | expurgo? |
| 23 | 15 | `L-647ab88f3e33f985` | Itaguaí (RJ): R$850,00   1.501.0000.0000 Outros Recursos não Vinculados 850,00   Art. 2º - | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 23 | 16 | `L-7dc99e212338085e` | Feira de Santana (BA): cooperação ou parceria com órgãos e entidades federais, estaduais o | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 17 | `L-e4ad1f2bf47ac8af` | Salvador (BA): que lhe são conferidas pela legislação em vigor, e   CONSIDERANDO que, nos  | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 18 | `L-e2dfbd1e42ca6180` | Campo Mourão (PR): II - incentivar a adoção de soluções tecnológicas abertas, interoperáve | preparação | PR | sem prazo | sem | 12 | expurgo? |
| 23 | 19 | `L-0fcef0383709aeca` | Lavínia (SP):  da Lei 4.320, de 17 de março de 1.964 e Lei Complementar   101, de 04 e mai | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 20 | `L-f01c8a91df65ba5f` | Taiobeiras (MG): diálogo, consulta, acompanhamento e avaliação, considerando as caracterís | preparação | MG | sem prazo | sem | 12 | expurgo? |
| 23 | 21 | `L-970c9f95c102710e` | Osasco (SP): Orçamentária;    2.3. Seção de Almoxarifado e Manutenção;    3. Divisão de Pa | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 22 | `L-8afe83b2f4ed4f9d` | São Domingos (SE): reduzir a sobrecarga dos serviços públicos, abrigos, canis, organizaçõe | preparação | SE | sem prazo | sem | 12 | expurgo? |
| 23 | 23 | `L-935482668632cbc9` | Monte Alto (SP): concessão dos Benefícios Eventuais poderá   ocorrer em quaisquer serviços | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 24 | `L-c3b38ef5ae675fbf` | Avaré (SP): oportunidades disponibilizados por: I – órgãos públicos; II – instituições de  | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 25 | `L-3084013c21e9de1a` | Cordeiro (RJ): relevantes para garantir   experiência segura e acolhedora.      Art. 11. O | preparação | RJ | sem prazo | sem | 12 | expurgo? |
| 23 | 26 | `L-5534901ffc6f4d08` | Salvador (BA): 250116 ELEMENTO DE DESPESA 33903012. - FONTE: TESOURO DATA DA ASSINATURA: 1 | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 27 | `L-b9835b3d189bd42b` | Ipiaú (BA): desenvolvimento da linguagem oral, da consciência   fonológica, da leitura, da | preparação | BA | sem prazo | sem | 12 | expurgo? |
| 23 | 28 | `L-9426b7dd66e3d268` | Sertãozinho (SP): 1058, 1081, 1082, 1083, 1102, 1108, 1124 e 1135/2026. Ofícios diversos n | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 29 | `L-23cdea1a5e59e3e2` | Tapiraí (SP): Desenvolvimento Social: Ana Cláudia dos Santos Toledano    Diretoria de Dep | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 30 | `L-d78f92d5fc92da9f` | Boa Vista (RR): 569743/2026,    DECRETA:   Art. 1º Fica nomeada a senhora Ana Paula de Aze | preparação | RR | sem prazo | sem | 12 | expurgo? |
| 23 | 31 | `L-11806092c4082232` | Junqueirópolis (SP): administrativas mais gravosas em caso de novo descumprimento, mediant | preparação | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 32 | `L-23eb58ba44d21530` | The Next Move Grant 2026: Up to €250,000 in Multi-Year Funding for Sport-Based Nonprofits  | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 33 | `L-fc1cac28a55c69c7` | Mata Atlântica Viva – Conservation and Regeneration Grants 2026 (Brazil) - fundsforNGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 34 | `L-492ad4d27382181f` | Social enterprise opportunities - October 2026 - SEWF | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 35 | `L-c0785f69173e8dc6` | Open Call – Cultural Heritage Fund 2026 (Brazil) - fundsforNGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 36 | `L-ea5bf8441f837443` | Convocatoria de Propuestas: Apoyo de Luena Scholars para proyectos comunitarios en Sudamér | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 37 | `L-38ee67f5e3d9d0dd` | Our Rights, Our Future! – Call for proposal | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 38 | `L-eb3d05c4113dea46` | Erasmus+ 2026 call for proposals published / European School Education Platform | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 39 | `L-58c0e448dd8feff7` | Appels à projets 2026 / France Diplomatie | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 40 | `L-08676ae0e07743cc` | Multilingual and Contextual AI Evaluation call for proposals - Fall 2026 - Amazon Science | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 41 | `L-efbb1d23cea0147d` | Segunda convocatoria para acompañar proyectos de organizaciones de la sociedad civil / Bue | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 42 | `L-429c24a2ff8c8c9c` | 2026/2027 Grants for NGOs and Organizations: Directory of Funding Opportunities - TuiFund | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 43 | `L-3886d7912924d9f4` | Bando “Our Rights, Our Future!” per reti e coalizioni della società civile - Info-Cooperaz | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 44 | `L-bd31f50841b072ca` | chamamento público - PORTAL DE PARCERIAS COM OSC | verificação externa | SP | sem prazo | sem | 12 | expurgo? |
| 23 | 45 | `L-ed7cbe67190c3760` | W.K. Kellogg Foundation Grants 2026: Open Funding Opportunities for Organizations Advancin | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 46 | `L-4c11b76138060386` | Adidas Foundation Grant 2026: Eligibility &amp; How to Apply | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 47 | `L-bca91527b25ecbc5` | Latin America Medical Education Grants / NBME | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 48 | `L-a3bc5c03e0ccb332` | Doação de Computadores &#8211; Projeto de Extensão Centro de Recondicionamento de Computad | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 49 | `L-ef9dc5bc68a022d8` | UNDP GEF Small Grants Programme 2026: Call for Environmental and Climate Project Proposals | preparação | — | sem prazo | sem | 12 | expurgo? |
| 23 | 50 | `L-f2d6784f3e0c3db6` | GEF Small Grants Programme 2026 / Up to US$100,000 | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 1 | `L-a8dc52050bcb219b` | UNDP GEF Small Grants Programme 2026: Funding of Up to $50,000 for Conservation Projects - | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 2 | `L-40aec034af9fa23c` | CONVOCATORIA A ORGANIZACIONES DE LA SOCIEDAD CIVIL INTERESADAS EN PARTICIPAR EN EXPOINCLUS | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 3 | `L-bdc58f9b1c35fb22` | PDF Selecionados 2026 - Edital IVM | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 4 | `L-2215cdfcbf6cd7d7` | PDF Guia 2025 - Edital IVM - portaldoenvelhecimento.com.br | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 5 | `L-5f79bb39b0ff3538` | WK Kellogg Foundation Grants 2026: Fund &amp; Apply | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 6 | `L-c8d97b84b064e7c6` | Call for Proposals-Civil Society Organizations (CSOs) or NGOs | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 7 | `L-bd3a2050c8453fa8` | Embraer Foundation opens applications for 2026 (e)NVEST in Community grant program | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 8 | `L-04a424a960c29c38` | PDF 21189.000536/2026-91 - Embrapa | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 9 | `L-f583cd4f1e567cf6` | Lei regulamenta patrocínio público ao esporte em Goiânia | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 10 | `L-60c6fa067e1d493f` | Governo Municipal amplia apoio às entidades rurais com subvenções, conectividade e investi | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 11 | `L-0bbdbb71adda9d93` | Governo Municipal fortalece o desenvolvimento rural com investimentos em infraestrutura, a | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 12 | `L-7f34b8bfec3302b9` | Edital Roche | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 13 | `L-863fa7af8e46becd` | Banco de Projetos para Associação de Pacientes 2026 | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 14 | `L-06f1dd38fb1b7cff` | Bolsas de Cidadania Roche 2026: Candidaturas Abertas | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 15 | `L-49ba666d61adf2fe` | Home / R4V | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 16 | `L-ca8e26fdccdd3f9a` | Sociedade pode se inscrever para integrar delegação do Brasil na COP31 - eJornais | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 17 | `L-572fffa39932a1e1` | MDA prorroga prazo de edital para agricultura familiar | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 18 | `L-ca16096ad47c1fdf` | Programa Patrulha Agrícola fortalece agricultura familiar e amplia apoio às associações ru | preparação | — | sem prazo | sem | 12 | expurgo? |
| 24 | 19 | `L-36e6594b0adf90f8` | Embassy small grants for NGOs in Brazil · FundingCalls | preparação | — | sem prazo | sem | 12 | expurgo? |
