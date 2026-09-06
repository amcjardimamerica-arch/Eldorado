# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


---
## 2dd2d9b5ffa96b7bbc90 — CHAMAMENTO PÚBLICO DESTINADO AO CREDENCIAMENTO DE ESTABELECIMENTOS DE SAÚDE E PRESTADORES DE SERVIÇOS DE SAÚDE, PESSOAS FÍSICAS OU JURÍDICAS

Fonte (vetor): PNCP — FUNDO MUNICIPAL DA SAUDE IPAMERI · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Valor: R$ 10.000,00

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://pncp.gov.br/app/editais/07777639000127/2026/58
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## 07b47f80913927a4c8d8 — Diário Oficial de Goiânia (GO) 2025-02-26 — "chamamento público" "organizações da sociedade civil"

Fonte (vetor): Querido Diário — diários oficiais municipais · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: nenhum

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://data.queridodiario.ok.org.br/5208707/2025-02-26/d92062f98d128ee3292847aa0203912df42076dc.pdf
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
