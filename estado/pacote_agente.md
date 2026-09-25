# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## db0bf83f4df2fe2c618a — PNAB 2026: Retificado cronograma dos editais nº 12, 13 e 14/2026

MODO: COMPLETO · marcado desde 2026-09-11 · visto pela IA 119× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Editais FICA Goiás - artes visuais/exposição · UF GO · nível estadual · situação possivel · fim None

Itens já obtidos: Objeto: Retificação de cronograma dos Editais PNAB 2026 da Secult-GO nº 12, 13 e 14/2026, Órgão / financiador: Secretaria de Estado da Cultura de Goiás (Secult-GO) — Política Nacional Aldir B, Território: GO, Esfera: estadual, Destinação: agentes culturais, coletivos e organizações da sociedade civil de Goiás, Área de atuação: cultura

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Requisitos, Anexos

Anúncio: https://goias.gov.br/cultura/pnab-2026-retificado-cronograma-dos-editais-no-12-13-e-14-2026
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
### página institucional
 COMUNICADO &#8211; Cumprimento à Legislação Eleitoral &#8211; Portal Goiás Buscar por: GOIAS.GOV.BR Ir para conteúdo 1 Ir para menu 2 Ir para busca 3 Ir para rodapé 4 A- A A+ Alto contraste Acessibilidade Mapa do site Buscar por: Governo Administração Direta Autarquias e Fundações Empresas Públicas SIGA - Sistema de Gestão Administrativa Conheça Goiás Turismo História Geografia Cultura Economia Municípios Símbolos Estaduais Notícias Legislação Governança Portal da Transparência Dados Abertos e-SIC Ouvidoria Denúncias contra Corrupção LGPD Radar da Transparência Código de Ética PCP SIGA Diário Oficial Acesso à Informação Governo Back Administração Direta Autarquias e Fundações Empresas Públicas SIGA - Sistema de Gestão Administrativa Conheça Goiás Back Turismo História Geografia Cultura Economia Municípios Símbolos Estaduais Notícias Legislação Governança Back Portal da Transparência Dados Abertos e-SIC Ouvidoria Denúncias contra Corrupção LGPD Radar da Transparência Código de Ética PCP SIGA Diário Oficial Acesso à Informação Home &nbsp; &nbsp; Institucional &nbsp; &nbsp; COMUNICADO &#8211; Cumprimento à Legislação Eleitoral COMUNICADO &#8211; Cumprimento à Legislação Eleitoral Publicado em 26 junho 2026 Última Atualização em 26 de junho de 2026 Categoria Institucional Em cumprimento à legislação eleitoral, este portal terá a divulgação de notícias temporariamente suspensa durante o período de restrições previsto para as eleições. A medida tem como objetivo assegurar o pleno atendimento às normas que disciplinam a comunicação institucional dos órgãos públicos durante o período eleitoral, garantindo a observância dos princípios da legalidade, da impessoalidade, da moralidade e da igualdade de oportunidades entre os candidatos. As notícias e demais conteúdos institucionais voltarão a ser publicados após o encerramento do período de restrições estabelecido pela legislação eleitoral. Agradecemos a compreensão. Governo na palma da mão Serviços Expresso Goiás Expresso Aplicações Expresso Servidor SEI Governadoria Cadastro de Autoridades Escola de Governo Outros Sites Governo Federal Assembleia Legislativa do Estado de Goiás Tribunal de Justiça do Estado de Goiás Ministério Público do Estado de Goiás Procuradoria-Geral do Estado de Goiás Controladoria-Geral do Estado de Goiás Diário Oficial Transparência e Ouvidoria LGPD Goiás Transparência Dados Abertos Goiás SIC &#8211; Serviço de Informação ao Cidadão e-SIC &#8211; Serviço Eletrônico de Informação ao Cidadão Regulamentação da LAI Relatório Estatístico da Ouvidoria Canal Telefônico Gratuito &#8211; 162 ou 0800 000 0333 Palácio Pedro Ludovico Teixeira, Rua 82, nº 400 – Setor Central Goiânia/ GO 
```


---
## 1b14b89add228be42305 — Convênios e parcerias

MODO: COMPLETO · marcado desde 2026-09-21 · visto pela IA 61× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Programa estadual de eventos esportivos · UF GO · nível estadual · situação possivel · fim None

Itens já obtidos: nenhum

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://goias.gov.br/esporte/dispensa-de-licitacoes
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
