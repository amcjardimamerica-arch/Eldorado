# Verificação pelo Claude no Chrome — GRUPO 2 de 3 (lote-2026-11-05-externa-completo)

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Esta é a atualização única do sistema: zerar a esteira do Cartório. Os 1.169 livros sem decisão (764 na verificação
externa, 387 na preparação, 18 na recepção — os chegados) foram divididos em 3 grupos. Este prompt é o GRUPO 2:

| O que | Quantidade | Onde |
|---|---|---|
| Livros deste grupo | 400: 370 na verificação externa, 30 na preparação, 0 na recepção | `verificacao/lotes/lote-2026-11-05-externa-completo-parte-9.json` a `-parte-16.json` (8 partes de até 50) |
| Do catálogo das oportunidades conhecidas (R44) | 22 | marca «catálogo» na tabela e o campo `catalogo` no lote |
| Sem nenhuma estrela, para validar ou expurgar | 378 | marca «expurgo?» e o campo `"verificacao_para_expurgo": true` |

Versão do lote: `gerado_em` = `2026-11-05T11:07:33+00:00`. A planilha deste grupo, `LISTA-LIVROS-VERIFICACAO-2026-11-05-GRUPO-2-de-3.xlsx`, tem os livros
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

## A tabela dos 400 livros do GRUPO 2

Colunas: a parte do lote, a posição na parte, o livro, o título, a etapa, a UF, o prazo, a estrela, quantos dos 12 itens
faltam e a marca (catálogo = R44, nunca sai; expurgo? = sem nenhuma estrela, validar ou expurgar).

| Parte | Nº | Livro | Título | Etapa | UF | Prazo | Estrela | Faltam | Marca |
|---|---|---|---|---|---|---|---|---|---|
| 9 | 1 | `L-b90dfaa181a9b934` | Promoção e Apoio ao Desenvolvimento do Futebol Masculino e Feminino - Convênio (RP 2) - SN | preparação | — | sem prazo | sem | 11 | expurgo? |
| 9 | 2 | `L-609630b61e19251e` | Rede de Acesso e Desenvolvimento Rural (programa 49000) | preparação | — | sem prazo | sem | 11 | expurgo? |
| 9 | 3 | `L-a362cd1eacea7d40` | Transparência das emendas coletivas | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 4 | `L-7c8a15dfd068950c` | Indigenous Peoples Fellowship Initiative | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 5 | `L-7de78bcbb23d33ca` | Rockefeller Foundation | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 6 | `L-7d2bebb6073526b2` | Virada Sustentável, que acontece de 6 a 9 de junho, abre edital ... | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 7 | `L-52299c9194d034f9` | 04/11/2026 09:55LOA 2027 - Cronograma de tramitação | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 8 | `L-826a1780fc967255` | GFF x CIVIC VOICES: Call for proposals - PATH | preparação | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 9 | `L-854e288012205358` | Áudio: Debate aponta precarização do emprego em contratos na saúde entre governo e organiz | verificação externa | BR | sem prazo | sem | 11 | expurgo? |
| 9 | 10 | `captacao-056` | Campeonato comunitário com inclusão social — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 11 | `captacao-058` | Núcleo de futebol de base comunitário — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 12 | `captacao-059` | Núcleo de corrida/caminhada comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 13 | `captacao-073` | Projeto de alfabetização comunitária de jovens — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 14 | `captacao-076` | Projeto de laboratório maker social — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 15 | `captacao-083` | Projeto de robótica educacional comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 16 | `captacao-085` | Projeto de educação financeira comunitária — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 17 | `captacao-117` | Fundo Nacional da Criança e Adolescente — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 18 | `captacao-131` | Projeto de inclusão digital da pessoa idosa — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 19 | `captacao-135` | Conselho da Pessoa com Deficiência - projetos de acessibilidade — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 20 | `captacao-144` | Pronas/PCD - formação de profissionais — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 21 | `captacao-145` | Pronas/PCD - pesquisa sobre deficiência — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 22 | `captacao-157` | Projeto de apoio a familiares de PCD — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 23 | `captacao-161` | Projeto de vacinação/campanhas educativas de apoio — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 24 | `captacao-164` | Projeto de saúde para população em vulnerabilidade — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 25 | `captacao-181` | Projeto de horta comunitária urbana — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 26 | `captacao-183` | Projeto de arborização e educação ambiental — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 27 | `captacao-185` | Projeto de resíduos eletrônicos — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 28 | `captacao-188` | Projeto de prevenção a desastres e clima em bairros — Goiás | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 29 | `captacao-220` | BNDES Fundo Socioambiental — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 30 | `captacao-228` | Instituto Localiza — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 31 | `captacao-230` | Fundação ArcelorMittal — Brasil | verificação externa | BR | sem prazo | sem | 12 | catálogo |
| 9 | 32 | `L-f059e617f62fb339` | fundo brasil recebe propostas preliminares para edital litigancia estrategica ate o dia 23 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 33 | `L-bd2e97ab93257c89` | encerrado o envio de pedidos para o fundo de apoio emergencial covid 19 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 34 | `L-fe9b6ac885b4090d` | sueli carneiro recebe o premio itau cultural 30 anos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 35 | `L-e05d07f104abf825` | edital direitos humanos e justica criminal inscricoes estao abertas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 36 | `L-e52e914f973fd1cc` | labora vai doar r1 milhao em edital para trabalhadores enfrentarem mudancas climaticas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 37 | `L-c69d3b59c4fcab7c` | justica climatica na amazonia e no cerrado novo edital do raizes recebe inscricoes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 38 | `L-65823116651d81b7` | fundacao mauricio sirotsky sobrinho oferece curso online e premiacao para projetos de ince | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 39 | `L-fdf6206e525557f7` | inscricoes abertas para o premio de criacao de valor compartilhado da nestle | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 40 | `L-47be716328ac7216` | onu seleciona iniciativas para empoderamento feminino | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 41 | `L-aa14b47e800d7492` | editora ftd abre edital na area da educacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 42 | `L-f2848ea576a93c8d` | ultima chamada para a votacao do premio rbs de educacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 43 | `L-bf5cde5fc01e2efb` | inscricoes abertas para desafio natura campus | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 44 | `L-5732b0cfe526326d` | fundo de inovacao humanitaria seleciona iniciativas inovadoras ao redor do mundo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 45 | `L-deca98502881d596` | premio visa a incentivar avancos em gestao ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 46 | `L-f039bab366fdf254` | pescar recebe premio de tecnologia social | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 47 | `L-cb957f1ec8061397` | premio empreendedor social recebe inscricoes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 48 | `L-c9c60b4aa16372b0` | premio de fotografia povos conectados com a terra | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 49 | `L-9f29dd1d133b6d06` | funda casa abre chamada de projetos para apoiar a autonomia e resiliencia de comunidades a | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 9 | 50 | `L-dd706e2f0b842710` | fundo casa abre chamada com foco em projetos para fortalecer a autonomia e resiliencia dos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 1 | `L-c4591fe9fc20c1a2` | chamada de projetos apoio a resiliencia climatica e reconstrucao comunitaria no rio grande | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 2 | `L-ce3dacb0554ad189` | fundo casa lanca primeira chamada de projetos de 2025 educacao para o bem viver | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 3 | `L-c8b5d8004b37bea1` | teia da sociobiodiversidade lanca nova chamada de apoio a projetos de desenvolvimento sust | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 4 | `L-ff002c66cbb41c0e` | apoio a iniciativas culturais dos povos indigenas na amazonia brasileira | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 5 | `L-f3550c93b4b4e34d` | edital fundo casa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 6 | `L-e58c870124e0d484` | inscricoes abertas para o 7o congresso hemisferico de captacao de recursos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 7 | `L-ee117aef867eecc9` | membros abcr tem 30 de desconto em curso sobre inscricao para premios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 8 | `L-dc1a5d6afea90ade` | inscricoes abertas para as bolsas da diversidade da conferencia afp | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 9 | `L-fec11ae0278228de` | Editor de emendas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 10 | `L-29a6cf172723d91d` | Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 11 | `L-5f920baf3048171f` | Receitas e Despesas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 12 | `L-c86150656d3d09a0` | Serviço de Informação ao Cidadão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 13 | `L-818ef641c5ff20fc` | Corregedoria | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 14 | `L-430028f9651e96a5` | Sistema Eletrônico de Informações - SEI | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 15 | `L-9c55682ae51a6c75` | Canais de Atendimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 16 | `L-4a3709af175b82f3` | acessoainformacao | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 17 | `L-2ea3803ca7bf4f6a` | Desenrola Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 18 | `L-1a66abf4427168b5` | Competências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 19 | `L-55f24efa6daf9bc8` | Horário de Atendimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 20 | `L-bee362b69f2e66be` | Manual Operativo de Acordo BIRD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 21 | `L-d710b67ad931dd85` | Receita e Despesas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 22 | `L-ebc32952a9dc3016` | Despesa Pública | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 23 | `L-165c530a13d68f93` | Notas Fiscais Eletrônicas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 24 | `L-61334f80f5442ee8` | Cartilha de Integridade para Licitantes e Contratados | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 25 | `L-8cac7545dbab3dcf` | Transparência e Prestação de Contas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 26 | `L-06219e74b5df5cf2` | Calamidades Públicas e Emergências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 27 | `L-8c5a0d15dd882945` | Bolsa Família | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 28 | `L-b35fa3bd6b9d337b` | Regra de Proteção | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 29 | `L-3e15350a0c7543f1` | Termo de uso | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 30 | `L-e7869f13251f4dbe` | Benefícios Assistenciais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 31 | `L-90273f00e97ca70a` | Quero Aprender | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 32 | `L-64e3ba59437e98ec` | Programa de Aquisição de Alimentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 33 | `L-5e4eafc4c6ec92ba` | Programa Nacional de Agricultura Urbana e Periurbana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 34 | `L-5967b6a9d39ec5ef` | Promoção da Alimentação Adequada e Saudável | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 35 | `L-9ae03fab4ac0f9b9` | Segurança Alimentar e Nutricional no SUAS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 36 | `L-aca6f367f67162d5` | Alimenta Cidades | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 37 | `L-9aa4920dff2c80f0` | Cozinha Comunitária | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 38 | `L-b7783c81abc2fbe6` | Restaurante Popular | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 39 | `L-b2bfa0cec2f438fb` | Cadeia de Valor | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 40 | `L-22288ab125ae769b` | Primeira Infância | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 41 | `L-813f1c8ba66c0fdd` | Canal de Denúncias | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 42 | `L-c0ccd2008f61967b` | Denúncia de fraude | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 43 | `L-2233f13ecabe76eb` | Modalidade de Licitação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 44 | `L-3ec6aaa03ef78ad2` | Processo Seletivo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 45 | `L-9b3b89cb4128b49f` | Secretaria de Avaliação, Gestão da Informação e Cadastro Único | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 46 | `L-8881a446f03d770c` | Buscar serviços por | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 47 | `L-dcc51bdfb7f4e331` | Demais segmentos (ONGs, organizações sociais, etc) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 48 | `L-dc36d3b30f2d5a4a` | Orçamento Nacional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 49 | `L-791fd7382768ca6e` | Serviços para Imigrantes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 10 | 50 | `L-3b8ccd27be80c919` | Educação Profissional para Jovens e Adultos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 1 | `L-3b4979deee13e3d6` | Combate à Discriminação Racial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 2 | `L-e6c6555f11fad4bc` | Saúde Reprodutiva da Mulher | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 3 | `L-247aa2dfbd621a0d` | Controle de Poluição e Resíduos Sólidos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 4 | `L-d43e7cd709f2bb1a` | Acessibilidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 5 | `L-713c890cc781394e` | Órgãos do Governo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 6 | `L-f3e12374ca4d39eb` | Ajuda para Navegar o Portal | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 7 | `L-5f5b0deac39472f8` | Governo Digital | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 8 | `L-52ee307017e870dd` | Dados da Administração Pública Federal | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 9 | `L-c16a6a23011fc960` | 1Assinatura Eletrônica | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 10 | `L-03d7acf31566500f` | 4Consultar CPF | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 11 | `L-c4f8a6f84740c4ea` | OutrosTela Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 12 | `L-ffeb101f4f38fde4` | CrimesCelular Seguro | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 13 | `L-118766fab9c97a28` | Curso online Agricultura Urbana e Periurbana está disponível no Portal Capacita MDS | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 14 | `L-6f319c8b9f950429` | OfícioCircularDiretrizes institucionais sobre as condutas vedadas e regras durante o perío | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 15 | `L-61dbc8beb1eacb24` | Aos Integrantesdo MDSOrientações, regras e condutas vedadas para agentes públicos e colabo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 16 | `L-2193cd41304787b7` | Áreas Protegidas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 17 | `L-f8d8db2da0fc3299` | Comissão Nacional de Biodiversidade - Conabio | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 18 | `L-fd71ca4ff74c16fb` | Patrimônio Genético | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 19 | `L-9a1f029c9447638f` | Política Nacional de Pagamento por Serviços Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 20 | `L-fd21904d6fef90d7` | Planos de Prevenção e Combate ao Desmatamento - PPCD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 21 | `L-50a0d83278a75548` | Agenda Ambiental da Administração Pública (A3P) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 22 | `L-10f7b226de0f0ff7` | Cidadania Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 23 | `L-a9281a5cc950b5d1` | Política Nacional de Educação Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 24 | `L-70a3d885e1e25227` | Agricultura Urbana e Periurbana | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 25 | `L-a7c588def161320c` | Cidades Verdes Resilientes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 26 | `L-ed88e603a7e41473` | Emergências Ambientais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 27 | `L-4bb699c906915a73` | AdaptaCidades | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 28 | `L-f7657ba22a5be916` | Estratégia Nacional para a Conservação e o Uso Sustentável dos Recifes de Coral – ProCoral | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 29 | `L-d52d51ad80e08aed` | Gerenciamento Costeiro – GERCO | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 30 | `L-84d0178dd7312c5d` | Povos e Comunidades Tradicionais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 31 | `L-35ae59c0fe55e212` | Petróleo e gás | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 32 | `L-8eccff9b92cb6fa8` | 1.3. Base Jurídica da Estrutura Organizacional e das Competências | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 33 | `L-8a375fc79da4b349` | 1.8 Histórico Institucional | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 34 | `L-b8c855780b2ebbd2` | 2.3. Concessões de Recurso Financeiros ou Renúncias de Receitas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 35 | `L-711b0ace057d61e6` | 3.3 Conselhos e Órgãos Colegiados | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 36 | `L-cd6e062b96c5e465` | 4.3. Relatórios da CGU | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 37 | `L-edf435159b43ec0e` | 4.6. Ações de Supervisão, Controle e Correição | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 38 | `L-ac3c43c0432c8460` | 5.1 Repasses e Transparências de Recursos Financeiros | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 39 | `L-c0e11ecc42555643` | 7.2. Contratos e Outras Avenças | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 40 | `L-37bd754113b87352` | 8.2. Aposentados e Pensionistas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 41 | `L-ac27d0dfcb7e8285` | 8.5. Despesas com Ações de Desenvolvimento de Servidores | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 42 | `L-f49f6c86e05c0dc6` | Lista de Servidores do MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 43 | `L-ef711582fa56512b` | 10. Serviço de Informação ao Cidadão - SIC | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 44 | `L-6d996d144d909a25` | 12.2 Disponibilização das Bases de Dados Programadas para Abertura no PDA do Órgão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 45 | `L-d35df3be7d4b908c` | 14.1. Ferramenta de Pesquisa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 46 | `L-8db88bd10b999f72` | Análise de Impacto Regulatório (AIR) e Avaliação de Resultado Regulatório (ARR) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 47 | `L-d4d31a727e42f1e3` | Relatórios de AIR | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 48 | `L-893cf31b8822c026` | Termos de Execução Descentralizada | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 49 | `L-f26f7c962c704adb` | O que temos para você | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 11 | 50 | `L-f5f4d76bd11b8976` | Acordos de Cooperação MMA | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 1 | `L-904462a8342eae1b` | Assessoria Especial de Assuntos Internacionais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 2 | `L-36d72d0682a10b8e` | Subsecretaria de Planejamento, Orçamento e Administração | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 3 | `L-fa190715043b480f` | Secretaria Nacional de Biodiversidade, Florestas e Direitos Animais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 4 | `L-6b45de054d1a0b8a` | Departamento de Proteção, Defesa e Direitos Animais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 5 | `L-2bab8ad23078cc27` | Departamento de Políticas de Estímulo à Bioeconomia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 6 | `L-f88e2609f7436065` | Departamento de Políticas de Controle do Desmatamento e Incêndios | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 7 | `L-9709fb3b75c0a13f` | Departamento de Qualidade Ambiental | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 8 | `L-f8320e4d0cadca37` | Departamento de Recursos Hídricos e Meio Ambiente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 9 | `L-8cfe3e3230c76cca` | Departamento de Políticas de Mitigação e Instrumentos de Implementação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 10 | `L-7539fb0874ba4a3a` | Departamento de Instrumentos de Mercado e REDD+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 11 | `L-db1fd0c0052f0d12` | Departamento de Políticas de Gestão Ambiental Rural | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 12 | `L-9f94479ee65a1abf` | Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis - Ibama | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 13 | `L-5bbdb56d3c530016` | Fundo Nacional do Meio Ambiente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 14 | `L-73e39d4e63acb246` | Conselho Nacional de Recursos Hídricos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 15 | `L-33000ef36396e3cc` | Comissão Nacional de Combate à Desertificação – CNCD | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 16 | `L-fb45540c06ec9d73` | Painel Resolveu? (CGU) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 17 | `L-2b7c7e9eed3e709a` | mma-apresenta-estudo-do-plano-de-ar-limpo-e-clima-e-debate-governanca-regional-com-mexico- | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 18 | `L-bb9814a8e1534079` | Saiba mais sobre MMA informa mudanças nos canais institucionais durante o período de defes | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 19 | `L-72a470776da833e9` | Saiba mais sobre Aeronaves federais lançam mais de 1 milhão de litros de água no combate a | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 20 | `L-66b178ef60b4d15a` | Ministro do Meio Ambiente e autoridades do Amazonas reforçam ações conjuntas contra incênd | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 21 | `L-5dc7bf02e9c70c84` | 5º leilão do Eco Invest Brasil tem R$ 49,95 bilhões homologados para seis setores produtiv | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 22 | `L-ffda171a012930f2` | Ministério dos Direitos Humanos e da Cidadania | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 23 | `L-57dcf8d3cca5d773` | Renúncia de Receitas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 24 | `L-5a2de51a70c7bd38` | Plano Anual de Atividades de Interna (PAINT) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 25 | `L-99c5c21dfdfc02be` | Dispensas - 2025 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 26 | `L-fc3ecfd8ae0f8ef4` | Painel de Dados da ONDH – Tutoriais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 27 | `L-c26821ad66f983b6` | Ferramentas e Aspectos Tecnológicos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 28 | `L-b82656fa88bb80d0` | Cadastro das Centrais de Intérpretes de Libras (CadCIL) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 29 | `L-f211d666540cbb38` | Comitê Intersetorial de Acompanhamento e Monitoramento da Política Nacional para a Populaç | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 30 | `L-d389bdf4908f0cb7` | Coordenação-Geral da Comissão de Anistia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 31 | `L-a9aa3ebc822c0cb4` | Coordenação-Geral de Políticas de Memória e Verdade (CGPMV) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 32 | `L-1dca670e073bfaf6` | Estatísticas do Registro Civil – Casamentos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 33 | `L-2ad19b12cf02f8d1` | Levantamentos Nacionais do SINASE | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 34 | `L-12d90837278954e0` | Observatório Nacional dos Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 35 | `L-793dce22a4b42dbb` | Painel de Dados da Ouvidoria Nacional de Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 36 | `L-d5015bf8e67131d5` | Pesquisa de Informações Básicas Estaduais (Estadic) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 37 | `L-ce5ba437cf831de8` | Programa de Proteção a Crianças e Adolescentes Ameaçados de Morte (PPCAAM) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 38 | `L-c6f0741d7374ccec` | Registro Civil de Nascimento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 39 | `L-97dae8ff171ec338` | Sistema Nacional de Adoção e Acolhimento (SNA) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 40 | `L-c5bac8b501ea85be` | Tecer Direitos Humanos-Rede Nacional de Educação em Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 41 | `L-ff030c792cac7de2` | Passo a passo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 42 | `L-17e8481e822608d6` | Política de Privacidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 43 | `L-7e51d172a23c403a` | Programa de Privacidade e Segurança da Informação (PPSI) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 44 | `L-b332b6d13cb7d5c3` | Redes Sociais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 45 | `L-34e143d1fe8ac819` | Encarregado pelo Tratamento de Dados Pessoais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 46 | `L-ab484f057e646e83` | Navegue por temas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 47 | `L-e6ab083ac56eca55` | Organização dos Estados Americanos (OEA) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 48 | `L-376d089bb8f2292a` | Comissão de Anistia | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 49 | `L-3862558b8f378141` | Educação em Direitos Humanos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 12 | 50 | `L-1230eac90bb2850d` | Adesão à Política Nacional dos Direitos das Pessoas LGBTQIA+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 1 | `L-51fb65c418f6b60c` | Memória e Verdade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 2 | `L-7ec6211408e99a0d` | Mortos e Desaparecidos Políticos | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 3 | `L-0ad82a9e66884aa8` | Auxílio Emergencial às ILPIs - Lei 14.018/20 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 4 | `L-a4c034268d0011cc` | Rede Nacional de Gestores Estaduais em Direitos Humanos da Pessoa Idosa | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 5 | `L-30a30344149a4c33` | Avaliação Biopsicossocial | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 6 | `L-d0a3b6cca49d5792` | Protocolar documentos junto ao Ministério dos Direitos Humanos e da Cidadania (MDHC) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 7 | `L-92d4d1aac94b134f` | Registrar Ameaça de Morte contra Criança e Adolescente (PPCAAM) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 8 | `L-fb2d642333f39a9a` | Como realizar ajustes na solicitação de Adesão | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 9 | `L-92b7f3e3074a7727` | Tutoriais em vídeo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 10 | `L-7298b4b607228a78` | Pró-DH (Repositório) | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 11 | `L-f515b6f3c41c7cb2` | Parecer 1 - Grupo De Amigos Da Vida | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 12 | `L-b0d5213727cd0b1f` | Parecer 4 - Associação Conecta Natureza Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 13 | `L-b88ba66eacb50f5c` | Recurso e resposta - ELOE Improcedente | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 14 | `L-6ff89a5468f9e5fe` | FAPEMIG — editais de fomento à pesquisa em Minas Gerais | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 15 | `L-b0992118e27c1217` | CNPq — chamadas públicas de pesquisa e bolsas | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 16 | `L-0a9de2eed246c902` | PL 3087/2026 — Altera a Lei nº 13.019, de 31 de julho de 2014 (Marco Regulatório das Organ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 17 | `L-8f18e3e515f0a69f` | PL 1797/2026 — Altera a Lei nº 13.019, de 31 de julho de 2014, para assegurar a transparên | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 18 | `L-f959434eb54fc6d9` | .css-d102py{margin:0;font-family:"Roboto","Helvetica","Arial",sans-serif;font-weight:400;f | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 19 | `L-3dc0987693f9dacf` | Grant Opportunities | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 20 | `L-d96bac1d11593238` | Ford Global Fellowship | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 21 | `L-3a72ceda00f6516b` | These videos break down the essentials of grantmaking | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 22 | `L-e0b249894c3d850f` | Our Grantees | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 23 | `L-0f59c96c08f9b952` | Big Bets Fellowships | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 24 | `L-6d2131c15280f6ee` | Fellowship Application | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 25 | `L-37ff6fc4c21ecd2d` | Recoverable Grants FAQ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 26 | `L-94d0b18f0aca0029` | Grant-making process | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 27 | `L-e35671ad4e839b31` | União Europeia – Erasmus+ | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 28 | `L-9cbf027fdb739206` | Ford Foundation | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 29 | `L-6a3b7134a4f15614` | Global Fund for Women | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 30 | `L-be372d219c06002d` | Skoll Fellowship | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 31 | `L-581976285385c965` | Edital FETEC 2026: Credenciamento para Artistas e GruposR$ 20 mil | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 32 | `L-c9790611977f3b93` | Edital Dança São José dos Campos 2026: Guia Completo | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 33 | `L-829babbc5d5a0a0f` | Edital CMDPI Godofredo Viana 2026: Guia de Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 34 | `L-652b8cbc7b3b7333` | Edital ECAU Uberaba 2026: Credenciamento de Professores | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 35 | `L-57f934ae5dbb8599` | Edital CMDPI Barrocas 2026: Chancela de Projetos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 36 | `L-f05697924ca0bdca` | Edital Cultura Popular FCCR 2026: Guia de CaptaçãoR$ 4 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 37 | `L-65c7a4884dee153a` | Edital CMDPI Santaluz 2026: Guia de Captação e Prazos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 38 | `L-2f84dc7c3844ef17` | Edital CMDCA Santaluz 2026: Guia de Chancela de Projetos | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 39 | `L-42eae0617ce0dd2f` | Edital CMDPI Teofilândia 2026: Guia de Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 40 | `L-5a342cd6e2a834c6` | Edital BIP FIA 2026: Guia de Captação e Financiamento | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 41 | `L-6bccd8c447ef6bb1` | Edital FCCR: Circulação Artística e Audiovisual 2026R$ 4 mil | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 42 | `L-9a1dd0cac552d631` | Edital BIP Esporte 2026: Guia Completo para Captação | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 43 | `L-a92b51c3da50983a` | Edital Catalisar 2026: Guia de Captação da FCC S.A. | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 44 | `L-eda055d55b5425eb` | Edital CELESC 001/2024: Captação Cultura até 2026até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 45 | `L-f53c83da7b790f1e` | Edital UEMS 020/2026 Cultura: Captação Sem Ônusaté 01 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 46 | `L-55702f5f25670b2b` | Edital CMDCA Santaluz/BA 2026 - Registro de Entidades | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 47 | `L-b57deed3cb4569ae` | Edital Intervenção Artística FCCR 2025 / Circulação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 48 | `L-ebbc0a7d6231003f` | Prêmio Liga STEAM 2026: Inscrições ProrrogadasR$ 25 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 49 | `L-c2bac4ba6e1faf53` | Edital PRONAS/PCD 2026: Guia de Captação do Min. SaúdeR$ 4,0 mi·até 26 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 13 | 50 | `L-a28918fa032de6bc` | Edital Ministério da Saúde 2026: Preceptoria SUSaté 11 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 1 | `L-75cc37cc38a22f0e` | Edital FAPEMIG 2026: Cadastramento de Instituições | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 2 | `L-ed5b7c24b06910d6` | Edital Ciclo de Saberes 2026: Guia de Captação MinC/MECR$ 500 mil·até 08 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 3 | `L-7f3db9f28b584ac2` | Edital Biblioteca Comunitária é Cultura Viva 2026 MinC | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 4 | `L-f39af2f40d87ca90` | Captação de R$200 mil no edital CNPq 34/2026 – Guia 2026R$ 200 mil·até 04 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 5 | `L-d361d198215ed76c` | Edital Acelere o Relógio da Igualdade 2026: R$ 30 milR$ 30 mil·até 11 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 6 | `L-b5fcc8326f0ee1ba` | Edital Brigadas Fundo Casa 2026: R$ 20 mil para ONGsR$ 20 mil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 7 | `L-572ddc6ef94c32b4` | NIH RFA-DA-28-013: NExUS Collaboratory Funding 2026até 09 de fev. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 8 | `L-9eb9bf401231b13e` | Chamada de Propostas FAPESP‑Instituto Pasteur 2026 Brasilaté 04 de mar. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 9 | `L-a66dd8b5d0cfef32` | Chamada Pública CISAMSF 003/2026 – Saúde e Social | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 10 | `L-a4e2f6eb6b20bbeb` | Chamamento Público Consirc 2026 – Oportunidades em Saúde | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 11 | `L-e2cdc0b3af88a3a2` | Chamamento Público 31/2026 Novo Horizonte do Oesteaté 13 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 12 | `L-bd3957e2fd4bbdaf` | Edital AVISO DE CHAMADA PÚBLICA 2/2026 – AgriculturaR$ 3,0 mi·até 22 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 13 | `L-fd06000152e5ae52` | Edital Padre Bernardo 2026: Saúde e Credenciamento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 14 | `L-c0f15387994f534c` | Chamamento Público Saúde Grande Sarandi 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 15 | `L-c81f486b9be30036` | Edital Instituto Genésio A. Mendes 2026: Guia de CaptaçãoR$ 30 mil·até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 16 | `L-d1119ece1e545bf6` | Edital Fapesq Embrapii Paraíba 2026: Inovação e R$ 200 milR$ 200 mil·até 07 de nov. de 202 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 17 | `L-d43bc3b440d5ea9c` | Edital 04/2026 Floresta Viva – Águas do São FranciscoR$ 17,8 mi·até 04 de dez. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 18 | `L-4034f171bda33e78` | Chamada Rio Doce 2026: captação de R$ 23 mi do BNDESR$ 23,0 mi·até 30 de dez. de 2026 | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 19 | `L-bdf3dbbeaa1ef94a` | Edital Campus Itaquaquecetuba 2026: Captação Abertaaté 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 20 | `L-daaafc00b81b3db1` | Edital Campo Belo 2026: Credenciamento Saúde | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 21 | `L-fb1cf0c207bbc0d7` | Edital Chuvisca 2026: Guia de Captação e Credenciamento | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 22 | `L-b82dcc8da89ad5dc` | Chamamento Bacias PCJ 1/2026: Guia de Captaçãoaté 28 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 23 | `L-d0b88506098fec28` | Edital de Medicamentos 2026: Guia de Inovaçãoaté 23 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 24 | `L-f6a39eaeaff63574` | Edital SEINFRA SEGEP 2026: Guia de Captação para OSCsR$ 1,5 mi·até 23 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 25 | `L-f75c1cbf7deda416` | Chamamento Público Alcântara 2026: Guia de Inscriçãoaté 30 de set. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 26 | `L-b471f7ca97960b9f` | Edital SESI 2026: Direção de Arte SESI Lab / Capitaai | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 27 | `L-e210ecc20a95c6bd` | Chamamento CRBM 4ª Região 2026: Guia de Captação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 28 | `L-6854fc20488dde53` | FAPESP Young Investigator Grant 2026: Guia de CaptaçãoR$ 2,5 mi·até 19 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 29 | `L-a49b7bb5028f2927` | Chamamento CRBM-4 2026: Guia de Captação e Edital | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 30 | `L-d78de030c4fa6656` | Edital Chamada Pública 6/2026: Guia de Captaçãoaté 06 de nov. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 31 | `L-edef940981ee0243` | Edital FME Transforma 2026: Como Captar R$ 1 Milhão - GuiaR$ 1,0 mi·até 30 de out. de 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 32 | `L-f637b1e0f20b1db2` | Edital Carmo do Rio Verde 2026: Guia de Captaçãoaté 18 de set. de 2027 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 33 | `L-cb75304d818e080c` | Chamada Pública Merenda Escolar 2026: Guia de Aplicação | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 34 | `L-b3ab31e653906af0` | Edital FCCR 006/2024: Coro Sinfônico de SJC 2026 | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 35 | `L-aa84047bfc0fb860` | Edital FUNBIO 2026: Apoio a UCs no Litoral do Paranáencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 36 | `L-2084252d3dc13cc8` | Edital Fapes/CNPq/Capes 22/2026 – Programa PROFIX-CBencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 37 | `L-2622c94c01a321bc` | Edital FAPESPA 2026: Guia Completo para Submissãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 38 | `L-521fb053365ab694` | Edital IX CBUC Fundação Grupo Boticário 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 39 | `L-a1e90bee73584c16` | Edital Aviso de Chamamento Público 1/2026 – Culturaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 40 | `L-af9c71baa3aef7c5` | Edital IPEA/PIPA 33/2026: Bolsa de Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 41 | `L-add30b67272564b1` | Edital APC Consulado do Japão 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 42 | `L-654fa4b9d5727ce5` | Chamamento Público 1/2026: Conselho Federal de Educaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 43 | `L-260cc2a27fafb757` | Edital FAPERO 2026: Iniciação Científica e Tecnológicaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 44 | `L-ad82163e3702f576` | Edital CRO-BA 2026: Imóveis para Locação em Teixeiraencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 45 | `L-a6229e6c345956a0` | Chamada Pública Doutor Pedrinho 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 46 | `L-fe7ce81921877417` | Edital Brejo Santo 2026: Guia de Credenciamento em Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 47 | `L-fd272500cb106222` | Edital First Solar Toledo Community Foundation 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 48 | `L-217ec5ecc81f2c80` | Chamamento Público Saúde Ielmo Marinho 2026: Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 49 | `L-183825263590a6ee` | Chamada Pública Poá 2026: Aluguel para CAPS IIencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 14 | 50 | `L-377c1e15577763bf` | Edital Itapuranga 2026: Guia de Habitação e Inscriçõesencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 1 | `L-4f8100d64495f9ab` | Edital Praia Grande 2026: Guia de Captação Culturalencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 2 | `L-72b57e1532241f9f` | Edital CAU/BR 2026: Credenciamento para Habitaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 3 | `L-e59a7118b57f77ca` | Edital Sobral 2026: Projetos Culturais e PNABencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 4 | `L-bb6fccb00e013bc8` | Edital SEJUS-PI 2026: Guia de Captação para ONGsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 5 | `L-2cc63d6ef611723c` | Edital SERPRO 2026: Chamamento Público para Tecnologiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 6 | `L-95fed914f55cf009` | Chamamento Público Lagoa do Ouro 2026: Edital de Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 7 | `L-b681bc3d86a3bf8c` | Chamada Pública Viçosa 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 8 | `L-da15e241ee64f623` | Edital Silvânia 2026: Guia de Inscrição e Recursosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 9 | `L-c20be6cb58697a10` | Chamada Pública Sulina 2026: Guia para Produtoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 10 | `L-473ddbc6de3c8c00` | Edital Alfenas 2026: Guia para Captação em Habitaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 11 | `L-357a6d475e17ef68` | Chamada Pública Grupo Hospitalar Conceição 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 12 | `L-d9d84cde3796ad72` | Edital Balsas 2026: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 13 | `L-a286020146c3754b` | Edital FAPEG Goiás pelo Mundo 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 14 | `L-4922caa885f3fe26` | Edital Tauá 2026: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 15 | `L-debece7a606f0969` | Edital FAPESP ANR 2027: Pesquisa Bilateral até 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 16 | `L-5da7d260c5a02967` | Edital Agricultura Familiar São Luiz do Norte 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 17 | `L-de9ed5d8a621b2e3` | Chamada Pública Reitoria 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 18 | `L-48b4ea0a302208da` | Edital FAPESP T-AP 2026: R$ 600 mil para Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 19 | `L-e8858ecdba47c0b0` | Edital Chamamento Público 6/2026 4ª Diretoria: Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 20 | `L-7987f3fc4af47f06` | Edital Acelera Campo 2026: R$ 60 mil para Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 21 | `L-950e17c1ceb8b45b` | Edital Marinha 2026: Guia de Permuta e Imóveis Ociososencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 22 | `L-03c2624ac9939daf` | Edital Fapes 20/2026: Bolsa Pós-Doutorado Sêniorencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 23 | `L-ffcd6ac0f7997144` | Edital Acaraú 2026: Chamamento Público para Leiloeirosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 24 | `L-652a7da44f29f6d2` | Chamada Pública Merenda Escolar 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 25 | `L-d53181e9379c2d96` | Edital Pitangueiras 2026: Projetos Musicais PNABencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 26 | `L-1832a115c196ecb0` | Edital FAPESPA 008/2026: Guia de Captação e Prazosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 27 | `L-19396768923f3b16` | Chamamento Público DSEI Cuiabá 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 28 | `L-755859ee90a2d223` | Edital Fundo Ecos 2026: R$ 3,3M para a Amazônia Legalencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 29 | `L-1451b1b4b560464a` | Chamada Pública IFTM 2026: Guia Completo para Editaisencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 30 | `L-3f2008d5cd1dccf2` | Edital DAAD 2026: Auxílio Doutorado Brasil-Alemanhaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 31 | `L-7a302c1590f8354f` | Edital Fapeg 14/2026: Indicações Geográficas em Goiásencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 32 | `L-f4ca070ac332b7ea` | Edital FAPERJ 04/2025: Hub RJ Startup 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 33 | `L-c0eba72aa5c48bab` | Edital Amazônia Legal Tocantins 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 34 | `L-70cc069c6f5191f5` | Edital PROFIX-CB FAPESPA 2026: Fixação de Doutoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 35 | `L-f8aa6df74f942e30` | Edital Okavango National Geographic 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 36 | `L-540d821b401267c3` | Edital FAPERJ Ciências Agrárias 2026: Como Aprovarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 37 | `L-c5bb572ec5f5b28e` | Edital iCS Comunicação Climática 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 38 | `L-4837326b3c4eafff` | Edital Dia de Doar 2026: R$ 2,4 mil para Campanhasencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 39 | `L-0392ec1f05beeeba` | Edital FAPESB/SECTI/IEL 004/2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 40 | `L-4b93f2c39df9fb60` | Edital Vital Strategies Saúde Mental 2026: R$ 800 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 41 | `L-92b0f183dc84e52f` | Edital Patrimônio Cultural Brasil-Holanda 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 42 | `L-42f07d174f1a6670` | Edital Clima e Sociedade 2026: R$ 500 mil para Comunicaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 43 | `L-3547cc4a0b41c4d6` | Edital Fundo Brasil 2026: R$ 60 mil para Amazônia e Cerradoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 44 | `L-8a9db9b874593590` | Edital FAPEG 2026: Mobilidade Internacional em Eventosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 45 | `L-6ccbb3419a0ee039` | Edital FAPEMIG 15/2026: Laboratórios Certificadoresencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 46 | `L-aa46134dd3f77be1` | Edital FAPESC 40/2026: Inovação e Tecnologia em SCencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 47 | `L-a9fcb4a183ad0d27` | Edital Coletivo Periférico 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 48 | `L-6062bdc25c73a470` | Edital FAPITEC/SE 2026: Auxílio para Eventos PRAPECencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 49 | `L-6ef7134d1b6ab2f3` | Bolsas de Filantropia Ford 2026: Guia de Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 15 | 50 | `L-65ba654531b1bd7c` | Edital PEC-PG 2026 CNPq/CAPES/MRE: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 1 | `L-17cb45df0407631f` | Edital Itaú Viver Mais 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 2 | `L-9e62a8a9e4300981` | Edital Fundo Socioambiental CAIXA 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 3 | `L-7d1d9b24bcca3786` | Prêmio Pacto Contra Fome 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 4 | `L-a3a033a05892d142` | Edital Petrobras Reciclagem de Óleo 2026: Como Aplicarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 5 | `L-afa163cee9f19409` | Edital FAPESC/EPAGRI 49/2026: Bolsas em Agropecuáriaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 6 | `L-80edc142f117d83c` | Edital CNPq/ERC 21/2026: Guia Completo e Como Aplicarencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 7 | `L-25ad60da38698839` | Edital Mulheres que Transformam o Futuro 2026encerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 8 | `L-318c9748cd1ea723` | Edital Instituto ACP 2025: Guia de Captação e Inscriçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 9 | `L-aa89dce465ac0afd` | Edital Mães Cientistas Facepe 2026: Guia de Captaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 10 | `L-1379d21714f8e47f` | Edital Ambev 2026: R$ 67M para Cultura e Esporteencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 11 | `L-c1799d97b19a93f7` | Edital MICSUL 2026: Inscrições no Ministério da Culturaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 12 | `L-78b2a429ec04148a` | Edital FAPESC/SEF 48/2026: Pesquisa e Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 13 | `L-eb132e78d56e0a5f` | Chamamento Público DSEI Porto Velho 2026: Guia Completoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 14 | `L-304331cb42bdbe01` | Edital Compet Mulheres Facepe 2026: R$ 200 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 15 | `L-84b932fab4c2497c` | Edital MinC Rouanet Centro-Oeste 2026: R$ 650 milencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 16 | `L-16428b829db29fe8` | Edital FAPERJ Agro do Futuro 2026: R$ 2,5M para Foodtechsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 17 | `L-148954448c0f66f4` | Edital FAPEAP 003/2026: R$ 3,8M para Redes de Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 18 | `L-659b103b585eacbc` | Edital FAPESB/SECTI 2026: R$ 10 Milhões para Pesquisaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 19 | `L-126b0d4a70619d33` | Edital Amazônia+10 2026: Como Captar Recursos de P&Dencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 20 | `L-40a9c50de52aa61a` | Edital FAPESC 37/2026: Apoio a Grupos UDESCencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 21 | `L-63f38638fcbcd620` | Edital FAPESB 009/2026: Apoio a Eventos Científicosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 22 | `L-f4f9d9228f11bf9d` | Edital MDA Agricultura Familiar 2026: R$ 500 mil para OSCsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 23 | `L-5c1eaf8526c44d24` | Edital Bracell Social 2026: R$ 600 mil para ONGsencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 24 | `L-bc490b45a302c4bf` | Fundo Ecos 2026: Edital para Territórios Indígenasencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 25 | `L-2134a33d8355cc3b` | VOA 2026 Ambev: Edital Inclusão Produtivaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 26 | `L-3929ad88ba608d7d` | FAPERJ 2026: Edital Infraestrutura Hospitais Universitáriosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 27 | `L-db17f96150cffb14` | Edital Fapeg Mestrado Internacional 2026 / Guiaencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 28 | `L-18d816ea11019113` | Edital Zilor 2025: Banco de Projetos Incentivadosencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 29 | `L-5380b833ff4e27c0` | FAPESC/CIASC 045/2026: Edital P&D Inovaçãoencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 30 | `L-fa93cd7e0ab2072b` | CNPq 18/2026: Edital de Avaliações em Saúdeencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 31 | `L-d3129baf79e5a572` | Chamada CNPq 07/2026: guia completo de bolsas deencerrado | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 32 | `L-bd146111cabac6c7` | Guias de editais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 33 | `L-eb2dde3fb7a231c2` | instituto equatorial abre inscricoes jornada capacitacao gratuita oscs 6okgyj | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 34 | `L-ecfb766cb3ca9d3b` | Pesquisa Doação Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 35 | `L-e101015f9a56b2ce` | Chamada de Projetos: Fundo Casa apoia fortalecimento de comunidades tradicionais na Amazôn | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 36 | `L-a35da72fc8f763bf` | ProgramaJá É: Fundo Baobá abre inscrições para jovens negros que querem acessar o ensino s | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 37 | `L-d328ecec135b1bbf` | Chamada de Projetos – Teia da Sociobiodiversidade | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 38 | `L-0b520f43fd339c5d` | project proposal guidelines | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 39 | `L-e38ee5c4af046c22` | blank project proposal form | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 40 | `L-f813a22a67bb6608` | How to Apply - Online Project Proposal System | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 41 | `L-a619afa8d4c32af6` | Technical Guidance - Online Project Proposal System | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 42 | `L-edbfa35456279645` | Mapa das OSC - Editais | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 43 | `L-b3f9565a48c3980d` | RoadSafe: Road Safety Grants Programme: Call for Proposals – Safer Road Users and Safer Ve | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 44 | `L-36b7b5365118eb50` | Calls for proposals - Fundo Brasil | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 45 | `L-437013a02568dc66` | Call for Proposals: Communication for Climate Action Grants (Brazil) ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 46 | `L-c54e454642824d47` | Organizações da sociedade civil já podem se inscrever no 2º Edital ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 47 | `L-eda7efdf9e3c38ad` | EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 FOMENTO À EXECUÇÃO DE AÇÕES CULTURAIS  (APOIO DIR | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 48 | `L-e70d80aa8c4d8522` | EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - MAPEAMENTO, DIAGNÓSTICO E PAINEL DE DADOS CULTU | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 49 | `L-f126270a6904147a` | EDITAL DE CHAMAMENTO PÚBLICO Nº 26/2026 SELEÇÃO DE PROJETOS PARA FIRMAR TERMO DE EXECUÇÃO  | preparação | BR | sem prazo | sem | 12 | expurgo? |
| 16 | 50 | `L-f2fbd3483ac8b040` | EDITAL ABERTO A Plan International Brasil está oferecendo R ... | verificação externa | BR | sem prazo | sem | 12 | expurgo? |
