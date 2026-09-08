# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## 93aa2d9dc209517bd973 — CREDENCIAMENTO PARA OS PROFISSIONAIS DA SAUDE. ATENDENDO AS NECESSIDADES DO FUNDO MUNICIPAL DE SAÚDE DE TROMBAS NO EXERCÍCIO 2024. (CHAMAMEN

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 2× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — FUNDO MUNICIPAL DE SAUDE · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: CREDENCIAMENTO PARA OS PROFISSIONAIS DA SAUDE, ATENDENDO AS NECESSIDADES DO FUND, Órgão / financiador: Fundo Municipal de Saúde (município de Goiás a identificar pelo CNPJ 11.344.805/, Território: GO, Esfera: municipal, Área de atuação: saude, Destinação: serviços de saúde ao SUS municipal (prestadores/OSC de saúde), Requisitos: prestador habilitado em saúde (CNES, alvará sanitário) — não é o perfil de assoc

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Anexos

Anúncio: https://pncp.gov.br/app/editais/11344805000179/2024/3
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## b0ddc9e8dfb55699a392 — CONTRATAÇÃO DE ORGANIZAÇÃO DE SOCIEDADE CIVIL, PARA CELEBRAÇÃO DE TERMO DE COLABORAÇÃO, NOS TERMOS DO EDITAL DE  CHAMAMENTO  PÚBLICO N° 001/

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 1× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — FUNDO MUNICIPAL DE SAUDE · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: Contratacao de organizacao da sociedade civil para celebracao de Termo de Colabo, Órgão / financiador: Fundo Municipal de Saúde (CNPJ 11.337.362/0001-99) — termo de colaboração em saú, Território: GO, Esfera: municipal, Área de atuação: saude, Destinação: serviços de saúde ao SUS municipal (prestadores/OSC de saúde), Requisitos: prestador habilitado em saúde (CNES, alvará sanitário) — não é o perfil de assoc

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Anexos

Anúncio: https://pncp.gov.br/app/editais/11337362000199/2023/58
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
