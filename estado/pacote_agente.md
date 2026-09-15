# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## db0bf83f4df2fe2c618a — PNAB 2026: Retificado cronograma dos editais nº 12, 13 e 14/2026

MODO: COMPLETO · marcado desde 2026-09-11 · visto pela IA 5× · motivo: sem prazo de inscrição confirmado

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
## ea14b1b3f360d2dc8637 — Instituto Impactarte abre edital para projetos de impacto social com apoio de até R$ 150 mil

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 12× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Observatório do Terceiro Setor — editais · UF BR · nível federal · situação possivel · fim None

Itens já obtidos: Objeto: Edital Continuo de Apoio do Instituto Impactarte: selecionar e apoiar organizaco, Órgão / financiador: Instituto Impactarte, Esfera: privada (filantropia), Valor: Até R$ 150.000,00 por iniciativa, em aporte direto, sem uso de mecanismo de ince, Território: Brasil, Área de atuação: assistencia_social, Destinação: projetos de impacto social por OSCs, Prazo de inscrição: Fluxo contínuo — inscrições abertas durante todo o ano, sem data de encerramento, Requisitos: CNPJ ativo; no mínimo três anos de existência comprovada; constituição como asso

Itens que FALTAM: Resultado, Prazo de recurso, Anexos

Anúncio: https://observatorio3setor.org.br/instituto-impactarte-abre-edital-para-projetos-de-impacto-social-com-apoio-de-ate-r-150-mil
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
### Midia Kit (site institucional)
Com seu apoio, podemos apresentar com
abrangência o que fazem as ONGs do Brasil.
Uma sociedade mais vibrante e participativa
passa pela conexão entre pessoas e causas.
O OBSERVATÓRIO DO 3º SETOR
ESTÁ EVOLUINDO! 
Quem somos Por que fazemos Valores 
Somos o único veículo jornalístico
brasileiro totalmente dedicado à
cobertura do Terceiro Setor. 
Produzimos e divulgamos conteúdo
jornalístico sobre o Terceiro Setor. 
Mantemos um portal multimídia,
atualizado diariamente, com
reportagens, programas de rádio,
artigos, vídeos e podcasts. 
Acreditamos que não existe
democracia sem uma sociedade civil
organizada. 
Queremos fortalecer as ONGs
conscientizando a sociedade sobre a
atuação e a importância do Terceiro
Setor 
Buscamos fortalecer a cultura de
doação brasileira dando espaço para
que organizações possam falar sobre
suas ações 
Compromisso com o bem comum
Paixão pelo social
Diversidade
Imparcialidade
Credibilidade acima de tudo
Há 12 anos fazendo a cobertura
e divulgando os direitos
humanos e iniciativas sociais.
E AGORA ESTAMOS DE CARA NOVA!
ANTES DEPOIS
+ 2.9 milhões
DE ACESSOS POR MÊS EM
TODAS AS REDES SOCIAIS 
 8 MIL
42 MIL
514 MIL
91 MIL
32 MIL
SEGUIDORES
SEGUIDORES
SEGUIDORES
SEGUIDORES
INSCRITOS
A VOZ DAS ONGS E O
RETRATO DO 3º SETOR
BRASILEIRO 
REDES SOCIAIS
RÁDIO E PODCASTS:
+ 250 MIL
650 
OUVINTES
ENTREVISTADOS
Quem dá voz ao nosso rádio atua há mais
de 40 anos defendendo Direitos Humanos
JOEL SCALA E
FRANKLIN VALVERDERADIO E PODCAST
O podcast Conexão 3 é apresentado por
Maria Fernanda Garcia e Gabriel Higute.
Trazendo convidados, que através de
discussões profundas e inspiradoras com
uma linguagem coloquial, falam sobre
direitos humanos, o papel vital dos jovens
na sociedade e o trabalho do terceiro setor. 
CONEXÃO 3
O QUE FAZEMOS
Cobertura jornalística qualificada e confiável de temas do setor 
Acompanhamento de eventos e entrevistas 
Produção de conteúdo para redes sociais 
Promoção de campanhas temáticas de conscientização 
Divulgação de eventos, artigos, cursos e descobertas do setor 
Fortalecimento da sociedade civil sustentando pontes entre os poderes públicos,
privados e sem fins lucrativos
1
2
3
4
5
6
PROJETOS
Observatório em
Movimento 
Produção de mini-
documentários e
e-books para
memória do
terceiro setor
brasileiro de
forma acessível 
Canal oficial de
divulgação de
editais via
Prosas 
Articulação e reflexão sobre
diferentes perspectivas e
causas que englobam a vida
para criar uma ponte entre
terceiro setor e a sociedade.
COMO VOCÊ PODE APOIAR A CONSTRUÇÃO DE
PONTES ENTRE A SOCIEDADE E AS AÇÕES SOCIAIS?
Suporte para desenvolvimento da equipe:
Hoje trabalhamos com uma equipe de profissionais iniciantes e
estagiários, mas sabemos que profissionais. E acreditamos que
profissionais bem treinados são essenciais para o nosso
desenvolvimento.
Aprimoramento na estrutura para cobertura das pautas:
Apurar conteúdo e conferir dados demandam tempo e conhecimento
específico. Para isso, nossos jornalistas precisam se locomover e estar
presente onde os fatos acontecem.
Aperfeiçoamento dos projetos em andamento:
Temos diversos produtos de comunicação que tratam de temas
extremamente relevantes para proteção dos direitos humanos,
promoção das ODS e fortalecimento da cultura de doação no Brasil.
Precisamos traduzir esse conteúdo para as diversas mídias digitais que
hoje representam a principal forma de consumo de informações. 
Precisamos do seu apoio
para produção de conteúdo
para redes socias. 
Animais 
Idosos 
Cultura 
Infância 
Direitos
Humanos 
Meio
ambiente 
Educação 
Povos
originários 
Esporte Saúde 
Você pode escolher as pautas que sua marca será apoiadora
SUA MARCA PATROCINA UMA
SESSÃO TEMÁTICA
SEU LOGO INSERIDO NA
SESSÃO TEMÁTICA
LOGO
DEPOIMENTOS
Diego Henrique Scala
diego@observatorio3setor.org.br
+55 11 97337-1911
CONTATO PARA PARCERIA

```
