# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}, "conformidade": true|false (true = aproveitável em Goiás/Brasil pelas associações; false = sem aproveitamento → vai para Arquivados), "motivo_conformidade": <frase>}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


MARCAÇÕES: os editais abaixo marcados como LEVE pertencem a outros estados — devolva SÓ objeto, início/fim das inscrições e a página oficial (`itens` com essas chaves e `pagina_divulgacao`); não faça parecer nem enquadramento. Os COMPLETOS (Goiás e nacionais) recebem tudo.


---
## 443dfeed2a9493ab123d — Termos de Fomento

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 2× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): Programa Goyazes — incentivo à cultura de Goiás · UF GO · nível estadual · situação possivel · fim None

Itens já obtidos: Objeto: Termos de Fomento, Órgão / financiador: Programa Goyazes — incentivo à cultura de Goiás, Território: GO, Esfera: estadual, Valor: R$ 2.400.000,00, Destinação: O valor total deste instrumento será de, Área de atuação: cultura

Itens que FALTAM: Prazo de inscrição, Resultado, Prazo de recurso, Requisitos, Anexos

Anúncio: https://goias.gov.br/cultura/termos-de-fomento
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
### Termo de Fomento nº 01/2026 (site institucional)
ESTADO DE GOIÁS
SECRETARIA DE ESTADO DA CULTURA
 
 
 
Termo de Fomento nº 1/2026 - SECULT
Processo nº 202600042005523
 
 
 
 TERMO DE FOMENTO
 
 
Termo de Fomento nº 1/2026
Processo nº 
202600042005523
 
 
 
 
TERMO DE FOMENTO Nº 1/2026, 
QUE ENTRE SI CELEBRAM O ESTADO DE GOIÁS, POR
INTERMÉDIO DA SECRETARIA DE ESTADO DA CULTURA, E O 
INSTITUTO BRASIL
CRIATIVO
, CONFORME DISPOSTO A SEGUIR.
 
O 
ESTADO DE GOIÁS
, pessoa jurídica de direito público interno, por intermédio da
SECRETARIA DE ESTADO DA CULTURA - SECULT
, inscrita no CNPJ nº
32.746.693/0001-52, com sede administrativa situada na Praça Dr. Pedro Ludovico
Teixeira, nº 26, St. Central, CEP: 74.003-010, Goiânia – GO, ora representada por sua
titular Sra. YARA NUNES DOS SANTOS, brasileira, solteira, inscrita no CPF sob o nº
XXX.301.821-XX, residente e domiciliada em Goiânia - GO, neste instrumento
denominada
 
ADMINISTRAÇÃO PÚBLICA
, e o 
INSTITUTO BRASIL
CRIATIVO
,
 
inscrita no CNPJ sob o nº 
12.350.038/0001-73
, pessoa jurídica de direito
privado, sem ﬁns lucrativos, com a sede na 
Av Deputado Jamel Cecílio Quadra C-9
Lote 2/15 Edifício Flamboyant Sala 708
, representada por seu presidente,
 
DOUGLAS
RIBEIRO DE CARVALHO
, brasileiro, 
Empresário/Produtor, 
inscrito no CPF sob o nº
XXX.
669.841
-XX, doravante denominada 
ORGANIZAÇÃO DA SOCIEDADE CIVIL
,
nos termos do processo nº 202600042005523
 
e
 
da Lei Federal nº 13.019/2014,
resolvem, de mútuo acordo, celebrar o presente 
TERMO DE FOMENTO,
 mediante
as cláusulas e condições seguintes:
 
CLÁUSULA PRIMEIRA
 – DO OBJETO 
– 
Realização da 8ª FARGO – Feira de Arte
Goiás, evento de artes visuais a ser realizado, entre os dias 13 a 17 de maio de 2026
no Centro Cultural Oscar Niemeyer, em Goiânia – GO, 
enquanto a vigência da
Termo de Fomento 1 /2026 (90351764) SEI 202600042005523 / pg. 1
parceria será de 120 (cento e vinte) dias, conforme previsto no Plano de Trabalho,
abrangendo as etapas preparatórias, administrativas, ﬁnanceiras e de prestação de
contas necessárias à execução integral do objeto.
 
CLÁUSULA SEGUNDA
 – DAS OBRIGAÇÕES DAS PARTES
I - DA ORGANIZAÇÃO DA SOCIEDADE CIVIL:
1- Providenciar, imediatamente, a aplicação ﬁnanceira da totalidade dos valores do
fomento - repasse e contrapartida (se houver) - em conta de aplicação do tipo
poupança e/ou investimento, a ﬁm de evitar responsabilidade pelo ressarcimento de
eventuais valores não aplicados no período compreendido entre o crédito e a efetiva
execução do objeto. 
2- Aplicar o recurso de acordo com o Plano de Trabalho aprovado pela Administração
Pública, cumprindo fielmente o objeto pactuado;
3- Observar, na aquisição de produtos e na contratação de serviços com recursos do
Estado, os princípios da impessoalidade, da moralidade, da publicidade e da
economicidade, sendo necessário, no mínimo, a realização de cotação prévia de
preços no mercado antes da formalização da parceria;
4- Gravar com cláusula de inalienabilidade os equipamentos e materiais
permanentes adquiridos com recursos da parceria;
5- Formalizar promessa de transferência da propriedade dos bens adquiridos à
Administração Pública em caso de extinção da parceria;
6- Prestar contas dos recursos recebidos nos termos da Lei Federal nº 13.019/2014;
7- Facilitar os meios necessários para que a Administração Pública e/ou seus
credenciados exerçam, a qualquer tempo, a ﬁscalização quanto aos aspectos
técnicos, ﬁnanceiros e administrativos da presente parceria, sem prejuízo ação
fiscalizadora dos demais órgãos de controle;
8 - Manter arquivados, em boa ordem, os documentos comprobatórios das despesas
realizadas no âmbito desta parceria, no próprio local em que foram contabilizados,
pelo prazo de 10 (dez) anos, contados da aprovação da prestação de contas pelo
Gestor do órgão;
9- Aﬁxar carimbo identiﬁcador contendo o título, número e ano do Termo de
Fomento ou de Colaboração em todas as faturas, notas ﬁscais e demais documentos
de despesa, obrigatoriamente emitidos em nome da Organização da Sociedade Civil;
10- Assumir integralmente todos os encargos que porventura venham a incidir
quando da execução desta parceria, tais como: obrigações civis, ﬁscais,
trabalhistas ou quaisquer outras correlatas;
11- Abrir conta bancária em instituição contratada para centralizar a movimentação
de recursos do Estado;
12- Depositar os recursos recebidos em decorrência da parceria em conta bancária
referida no item antecedente, a qual deverá ser isenta de tarifa bancária. Os
recursos deverão ser mantidos nesta conta especíﬁca e somente poderão ser
utilizados para o pagamento de despesas constantes do Plano de Trabalho ou para a
aplicação no mercado financeiro conforme previsto neste termo;
13- Destinar os rendimentos de ativos ﬁnanceiros ao objeto da parceria, estando
sujeitos às mesmas regras de prestação de contas aplicáveis aos recursos
transferidos;
14- Movimentar os recursos exclusivamente por transferência eletrônica, sujeita à
Termo de Fomento 1 /2026 (90351764) SEI 202600042005523 / pg. 2
identiﬁcação do beneﬁciário ﬁnal e à obrigatoriedade de depósito em sua conta
bancária;
15- Efetuar os pagamentos diretamente na conta bancária de titularidade dos
fornecedores e prestadores de serviços, exceto nos casos em que a transferência
eletrônica seja inviável, situação em que poderá ser admitido o pagamento em
espécie, nos termos do art. 53, §2º, da Lei nº 13.019/2014;
1 6 - 
Restituir à Administração Pública, no prazo improrrogável de 30 (trinta)
dias, eventuais saldos ﬁnanceiros remanescentes, incluindo receitas de aplicações
ﬁnanceiras, por ocasião da conclusão, denúncia, rescisão ou extinção da parceria,
sob pena de imediata instauração de Tomada de Contas Especial. O saldo a ser
devolvido deverá ser restituído via Documento de Arrecadação de Receitas
Estaduais (DARE) e deverá observar a proporcionalidade entre os recursos
transferidos pela Administração Pública e a contrapartida da Organização da
Sociedade Civil. Procedimento similar será adotado em casos de não execução do
objeto ou prestação de contas não realizada ou reprovada
;
17- Apresentar, na prestação de contas, respeitando a ordem cronológica dos fatos,
toda a documentação necessária para a comprovação do cumprimento das metas;
18- Cumprir rigorosamente o cronograma de execução estabelecido no Plano de
Trabalho, sendo que quaisquer alterações só poderão ocorrer mediante anuência
expressa da Administração Pública;
19- Assumir total responsabilidade pelos contratos ﬁrmados para execução dos
serviços e aquisições relacionadas ao objeto da parceria, respondendo por eventuais
danos ou prejuízos decorrentes da execução irregular, arcando integralmente com
custos de serviços ou aquisições que apresentem vícios, defeitos ou
incorreções, tanto durante quanto após a conclusão da prestação ou aquisição;
20- Responsabilizar-se pelo gerenciamento administrativo e ﬁnanceiro dos recursos
recebidos, abrangendo despesas de custeio, investimento e pessoal, sem qualquer
interferência da Administração Pública;
21- Assumir exclusivamente o pagamento dos encargos trabalhistas,
previdenciários, ﬁscais e comerciais relacionados à execução do objeto, sem que
qualquer inadimplência da organização da sociedade civil gere responsabilidade
solidária ou subsidiária para a Administração Pública. Além disso, arcar com todos os
ônus incidentes sobre a parceria e quaisquer prejuízos resultantes de restrições à
sua execução;
22- Indicar um Gestor, que será responsável por fornecer informações sobre o
andamento da execução e encaminhar as demandas à Administração Pública;
23- Divulgar a parceria celebrada com a Administração Pública na internet e em
locais visíveis de sua sede social e dos estabelecimentos onde desenvolve suas
atividades, contendo, no mínimo, as informações exigidas no parágrafo único do art.
11 da Lei Federal nº 13.019/2014;
24- Permitir acesso irrestrito aos processos, documentos e informações relacionadas
ao termo de fomento, bem como aos locais de execução do objeto, para os agentes
da Administração Pública, órgãos de controle interno e Tribunal de Contas
competente;
25 - Apresentar relatório fotográﬁco para comprovar as atividades e a execução do
objeto pactuado;
26 - Por meio deste instrumento, a organização tem ciência e declara, nos termos
da Lei, que:
Em caso de dissolução da entidade, o respectivo patrimônio líquido será transferido
Termo de Fomento 1 /2026 (90351764) SEI 202600042005523 / pg. 3
a outra pessoa jurídica de igual natureza que preencha os requisitos da Lei
nº13.019/2014, e cujo objeto social seja, preferencialmente, o mesmo da entidade
extinta (Art.33, III, da Lei 13.019/14);
Possui objetivos voltados à promoção de atividades e ﬁnalidades de relevância
pública e social (Art.33, inciso I, Lei 13.019/2014);
Cumpre o disposto no Art.7º, inciso XXXIII da Constituição Federal, que versa sobre a
proibição de trabalho noturno, perigoso ou insalubre a menor de 18 (dezoito) anos e
de qualquer trabalho a menores de 16 (dezesseis) anos, salvo na condição de
aprendiz, a partir dos 14 (quatorze) anos, na forma da Lei;
Não tem como dirigente, membro de Poder ou Ministério Público, ou dirigente de
órgão ou autarquia da administração pública da mesma esfera governamental em
que será celebrado o termo de fomento, estendendo-se a vedação aos respectivos
cônjuges ou companheiros, bem como parentes em linha reta, colateral ou por
aﬁnidade, até o segundo grau (
Art. 39, inciso III, Lei n. º 13.019/2014 e Art. 45, §3º,
II, da Lei 22.874/2024 – LDO/25
);
Tem experiência prévia na realização, com efetividade, do objeto da parceria ou de
natureza semelhante (conforme Art.33, V, ‘b’, Lei nº 13.019/14);
Possui instalações, condições materiais e capacidade técnica operacional para o
desenvolvimento das atividades e/ou projetos previstos na parceria e o
cumprimento das metas estabelecidas no ajuste (conforme Art.33, V, ‘c’, da Lei
13.019/14);
De que não há sobreposição de objeto em relação a outro instrumento celebrado. 
 
II - DA ADMINISTRAÇÃO PÚBLICA :
1- Acompanhar e avaliar de forma global os projetos a serem desenvolvidos no
âmbito da parceria.;
2- Designar o gestor responsável pela gestão da parceria, com poderes para exercer
controle e fiscalização;
3- Designar Comissão de Monitoramento e Avaliação para veriﬁcar o cumprimento
do objeto da parceria;
4- Prorrogar, de ofício, a vigência do fomento em caso de atraso na liberação dos
recursos, limitada a prorrogação ao período exato do atraso verificado;
5- Disponibilizar no site da Secretaria de Estado de Relações Institucionais, o Plano
de Trabalho aprovado e o Termo de Fomento assinado até o quinto dia útil após a
sua publicação no Diário Oficial do Estado;
6- Analisar a prestação de contas apresentada pela Organização da Sociedade Civil,
podendo rejeitá-la caso sejam constatadas irregularidades, tais como:
a) Não utilização, total ou parcial, dos recursos ﬁnanceiros no objeto da parceria,
incluindo saldos remanescentes e receitas obtidas com aplicações ﬁnanceiras, sem
o devido recolhimento conforme previsto neste instrumento;
b) Ausência de documentos exigidos na prestação de contas, comprometendo a
verificação da correta e regular aplicação dos recursos;
7- Assumir a responsabilidade pela continuidade da execução do objeto previsto no
Plano de Trabalho em caso de paralisação, garantindo que os serviços não sejam
interrompidos. Nessa hipótese, a prestação de contas deverá considerar a parte
executada pela Organização da Sociedade Civil até o momento da assunção pela
Administração Pública;
Termo de Fomento 1 /2026 (90351764) SEI 202600042005523 / pg. 4
8- Disponibilizar, na internet, canais de comunicação para denúncias e
representações sobre a aplicação irregular dos recursos da parceria.
 
CLÁUSULA TERCEIRA
 – DO GESTOR DO FOMENTO
Subcláusula Primeira - 
Designar Gestor, na qualidade de representante da
Administração Pública, para acompanhar e ﬁscalizar a execução dos recursos
repassados, nos termos do art. 61 da Lei Fed
```


---
## 71f1af059c45f010339a — A PREFEITURA MUNICIPAL DE NOVO GAMA - GO TORNA PÚBLICO QUE REALIZARÁ CHAMAMENTO PÚBLICO, POR CREDENCIAMENTO, PARA SELECIONAR EMPRESA DO RAMO DA CONSTRUÇÃO CIVIL, COM COMPROVADA CAPACIDADE TÉCNICA, INTERESSADA EM APRESENTAR PROJETOS E CONSTRUIR UNIDADES HABITACIONAIS EM LOTES E ÁREA DE PROPRIEDADE DO

MODO: COMPLETO · marcado desde 2026-09-07 · visto pela IA 2× · motivo: sem prazo de inscrição confirmado

Fonte (vetor): PNCP — MUNICIPIO DE NOVO GAMA · UF GO · nível municipal · situação possivel · fim None

Itens já obtidos: nenhum

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://pncp.gov.br/app/editais/01629276000104/2024/3
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```
