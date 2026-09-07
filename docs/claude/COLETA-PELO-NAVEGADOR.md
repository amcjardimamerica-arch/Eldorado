# Coleta pelo navegador (extensão Claude no Chrome) — passo a passo

Objetivo: completar, em cada oportunidade, as TRÊS informações mínimas —
**objeto**, **prazo de inscrição** e **página oficial do edital** (site do órgão
ou patrocinador; nunca o PNCP, o diário ou o portal onde foi encontrada).

## Antes de começar (uma vez)
1. Abra o painel: https://amcjardimamerica-arch.github.io/Eldorado/dashboard.html
2. Abra a fila num segundo separador: https://amcjardimamerica-arch.github.io/Eldorado/dados/fila_verificacao.json
   (é a lista do que falta; o campo `modo: completo` são as de Goiás e nacionais)
3. Deixe aberto o repositório: https://github.com/amcjardimamerica-arch/Eldorado

## O prompt para a extensão (cole na barra do Claude no Chrome)

> Você vai completar informações de editais para o sistema Eldorado. Abra
> https://amcjardimamerica-arch.github.io/Eldorado/dados/fila_verificacao.json e pegue os
> 10 primeiros itens com `"modo": "completo"` cujo campo `minimas.faltam` não esteja vazio.
> Para CADA item, nesta ordem, um de cada vez:
> 1. Abra o `link_oficial` quando existir. Se não existir, procure no Google pelo nome do órgão
>    (campo `fonte`) + "editais" ou "chamamento público" e entre APENAS no site oficial do órgão
>    (domínio .gov.br, .leg.br, .jus.br ou o site do patrocinador). Nunca use PNCP, Querido Diário,
>    Diário Oficial ou portais de notícia como fonte.
> 2. Localize o edital pelo número/ano do título. Abra o PDF do edital.
> 3. Extraia exatamente três coisas: OBJETO (a frase do item "DO OBJETO"), PRAZO DE INSCRIÇÃO
>    (data de início e fim, do item "DAS INSCRIÇÕES" ou do cronograma) e a URL DA PÁGINA OFICIAL
>    onde o edital está publicado.
> 4. Se o site não abrir, o edital não estiver lá ou o prazo não constar, escreva isso — não invente
>    nem estime datas.
> Ao final, monte um único bloco JSON no formato abaixo e me mostre para eu conferir:
> {"<id do item>": {"objeto": "...", "inicio": "AAAA-MM-DD ou null", "fim": "AAAA-MM-DD ou null",
>   "pagina_oficial": "https://...", "observacao": "o que faltou ou o que não abriu"}, ...}

## O que fazer com o resultado
1. Copie o JSON que a extensão devolver.
2. No repositório: **Add file → Create new file**, caminho
   `dados/editais/coleta_navegador/<data>.json` (ex.: `2026-09-07.json`), cole o JSON e **Commit**.
3. O sistema incorpora na próxima saída (ou rode `python -m src.enquadramento ingerir_navegador`).

## Alternativa sem digitar nada: script de um clique
`scripts/coleta_brasil.bat` (duplo clique) faz a coleta dos portais goianos que o robô do GitHub
não alcança, com o seu IP, e envia sozinho ao repositório. Guia: `docs/claude/COLETA-LOCAL-BRASIL.md`.
