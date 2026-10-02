# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## 2fe3bf6a9fc9b726bab2 — Prefeitura de Nova Iguaçu de Goiás — Edital nº 001/2026

MODO: COMPLETO

Fonte (vetor): Diário Oficial do Estado de Goiás · UF GO · nível municipal · situação aberta · fim 2026-10-02

Itens já obtidos: nenhum

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://diariooficial.abc.go.gov.br/portal/visualizacoes/pdf/7382/#e:7382
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## 53e16dff2aeb300819dd — SEGENP (gestão de negócios e parcerias) — Edital nº 001/2026 — Celebração de Termo de Colaboração com Organização da Sociedade Civil (OSC) v

MODO: COMPLETO · marcado desde 2026-10-01 · visto pela IA 3× · motivo: informações incompletas

Fonte (vetor): Diário Oficial do Município de Goiânia · UF GO · nível municipal · situação aberta · fim 2026-10-26

Itens já obtidos: nenhum

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://data.queridodiario.ok.org.br/5208707/2026-09-25/9952f00ade29d6e71433d17d9591a05498b890bb.pdf
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
