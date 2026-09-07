# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## c5c7e37e2e275d2e69fe — Instituto Lojas Renner abre edital com até R$ 10 mil para fortalecer organizações sociais

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 6× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Observatório do Terceiro Setor — editais · UF BR · nível federal · situação aberta · fim 2026-09-13

Itens já obtidos: Objeto: Edital Encantando Comunidades: Recursos Flexiveis - 2a edicao, do Instituto Loja, Órgão / financiador: Instituto Lojas Renner, Esfera: privada (investimento social empresarial), Valor: até R$ 10.000,00 por organização (anúncio), Território: Brasil, Área de atuação: assistencia_social, Destinação: fortalecimento institucional de organizações sociais, Prazo de inscrição: 2026-09-13, Início das inscrições: 2026-08-12

Itens que FALTAM: Resultado, Prazo de recurso, Requisitos, Anexos

Anúncio: https://observatorio3setor.org.br/instituto-lojas-renner-abre-edital-com-ate-r-10-mil-para-fortalecer-organizacoes-sociais
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## ba62bfc2d3ecc4281773 — Termos de Fomento

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 14× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Editais FICA Goiás - artes visuais/exposição · UF GO · nível estadual · situação possivel · fim None

Itens já obtidos: Objeto: Pagina de transparencia 'Termos de Fomento' da Secretaria de Estado da Cultura d

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://goias.gov.br/cultura/termos-de-fomento
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
