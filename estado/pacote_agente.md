# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## ba62bfc2d3ecc4281773 — Termos de Fomento

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 9× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Editais FICA Goiás - artes visuais/exposição · UF GO · nível estadual · situação possivel · fim None

Itens já obtidos: Valor: R$ 10.000,00

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://goias.gov.br/cultura/termos-de-fomento
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## ea14b1b3f360d2dc8637 — Instituto Impactarte abre edital para projetos de impacto social com apoio de até R$ 150 mil

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 7× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Observatório do Terceiro Setor — editais · UF BR · nível federal · situação possivel · fim None

Itens já obtidos: Objeto: Anúncio, no Observatório do Terceiro Setor, de edital do Instituto Impactarte pa, Órgão / financiador: Instituto Impactarte, Esfera: privada (filantropia), Valor: 150, Território: Brasil, Área de atuação: assistencia_social, Destinação: projetos de impacto social por OSCs

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Requisitos, Anexos

Anúncio: https://observatorio3setor.org.br/instituto-impactarte-abre-edital-para-projetos-de-impacto-social-com-apoio-de-ate-r-150-mil
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
