# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## 2dd2d9b5ffa96b7bbc90 — CHAMAMENTO PÚBLICO DESTINADO AO CREDENCIAMENTO DE ESTABELECIMENTOS DE SAÚDE E PRESTADORES DE SERVIÇOS DE SAÚDE, PESSOAS FÍSICAS OU JURÍDICAS

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 2× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — FUNDO MUNICIPAL DA SAUDE IPAMERI · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: CHAMAMENTO PUBLICO DESTINADO AO CREDENCIAMENTO DE ESTABELECIMENTOS DE SAUDE E PR, Órgão / financiador: Fundo Municipal de Saúde de Ipameri, Território: Ipameri/GO, Esfera: municipal, Área de atuação: saude, Destinação: serviços de saúde ao SUS municipal (prestadores/OSC de saúde), Requisitos: prestador habilitado em saúde (CNES, alvará sanitário) — não é o perfil de assoc

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Anexos

Anúncio: https://pncp.gov.br/app/editais/07777639000127/2026/58
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## 6db359795600d65dd60c — O presente Edital destina-se cadastrar Profissionais de saúde/ Pessoas Físicas e/ ou Jurídicas para posterior Credenciamento, mediante docum

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 1× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — FUNDO MUNICIPAL DE SAUDE · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: Edital destinado a cadastrar Profissionais de saude, pessoas fisicas e/ou juridi, Órgão / financiador: Fundo Municipal de Saúde de Jataí, Território: Jataí/GO, Esfera: municipal, Área de atuação: saude, Destinação: serviços de saúde ao SUS municipal (prestadores/OSC de saúde), Requisitos: prestador habilitado em saúde (CNES, alvará sanitário) — não é o perfil de assoc

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Anexos

Anúncio: https://intranet.jatai.go.gov.br/intranet/sistemas/diario-oficial/diario-site.php
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
