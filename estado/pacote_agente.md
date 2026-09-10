# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## 71f1af059c45f010339a — A PREFEITURA MUNICIPAL DE NOVO GAMA - GO TORNA PÚBLICO QUE REALIZARÁ CHAMAMENTO PÚBLICO, POR CREDENCIAMENTO, PARA SELECIONAR EMPRESA DO RAMO DA CONSTRUÇÃO CIVIL, COM COMPROVADA CAPACIDADE TÉCNICA, INTERESSADA EM APRESENTAR PROJETOS E CONSTRUIR UNIDADES HABITACIONAIS EM LOTES E ÁREA DE PROPRIEDADE DO

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 41× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — MUNICIPIO DE NOVO GAMA · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: Chamamento publico, por credenciamento, da PREFEITURA MUNICIPAL DE NOVO GAMA/GO , Órgão / financiador: Município de Novo Gama (GO), Território: Novo Gama/GO, Esfera: municipal, Destinação: organizações da sociedade civil do município, Área de atuação: outros

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Requisitos, Anexos

Anúncio: https://pncp.gov.br/app/editais/01629276000104/2024/3
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
### página institucional
 Licitações - Prefeitura de Novo Gama - GO Habilite o JavaScript para utilizar o NúcleoGov. Menu Início Atos Norm. Portarias Decretos Leis Resoluções Instrução Normativa Conselhos Municipais Atas de Reunião Receitas Receitas Receitas 2018 até 2012 Inscritos em Dívida Ativa Despesas Despesas Rec. Humanos Folha de Pagamento Padrão Remuneratório Lista de Estagiários Lista de Terceirizados Concursos Públicos Processos Seletivos Eleição de Conselhos Municipais Licitações Licitações Licitações Fracassadas e Desertas Dispensas e Inexigibilidades Plano de Contratações Anual (PCA) Sanções Administrativas Avisos de Dispensas Contratos Contratos Fiscais de Contratos Atas de Registro de Preço Ordem Cronológica de Pagamentos Prest. Contas Prestação de Contas (Balanço Anual) Relatório de Gestão ou Atividades Parecer do Tribunal de Contas Julgamento de Contas pelo legislativo Relatórios de Gestão Fiscal Relatórios Resumido de Execução Orçamentária Plano Estratégico Planejamento Orçamentário SIC SIC - Serviço de Informação ao Cidadão Regulamentação da LAI Relatório Estatístico do e-SIC Informações Classificadas como Sigilosas Informações Desclassificadas como Sigilosas Ouvidoria Início Solicitação Elogios Sugestões Reclamações Denúncias Carta de Serviços aos Usuários Ver mais ACESSIBILIDADE A+ A A- Licitações VOCÊ ESTÁ AQUI: &nbsp; PÁGINA INICIAL &nbsp; > &nbsp; Licitações &nbsp; > &nbsp; Licitações . . Portal do Cidadão da Prefeitura de Novo Gama - GO A+ A A- Acessibilidade Alto Contraste Mapa do Site --> Portal do Cidadão Licitações FILTRO Licitações Licitações Fracassadas e Desertas Dispensas e Inexigibilidades Plano de Contratações Anual (PCA) Sanções Administrativas Avisos de Dispensas Declaração de Não Adesão SRP --> --> --> FILTRAR --> --> --> --> Atualizado em 08/09/2026 --> 
```


---
## 5b991f651a1905c579de — Realização de Chamamento Público visando a Seleção de Agentes Culturais de Audiovisual que tenham prestado relevante contribuição ao desenvo

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 38× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — MUNICIPIO DE ALVORADA DO NORTE · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: Objeto: Edital de Chamamento Publico no 003/2023 do Municipio de Alvorada do Norte/GO - , Órgão / financiador: Município de Alvorada do Norte (GO), Território: Alvorada do Norte/GO, Esfera: municipal, Destinação: organizações da sociedade civil do município, Área de atuação: outros

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Valor, Requisitos, Anexos

Anúncio: https://pncp.gov.br/app/editais/02367597000132/2023/423
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
