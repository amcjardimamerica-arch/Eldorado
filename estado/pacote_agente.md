# Pacote para o agente Claude — Enquadramento (Farol de Alexandria)

Regras: (1) use SÓ o texto abaixo e o conhecimento do sistema; busque na internet apenas se o texto não trouxer o item; (2) nunca invente — sem base, null; (3) PNCP e diários são vetores: a fonte é o site do órgão publicador — informe-o em `pagina_divulgacao`; (4) escreva UM arquivo JSON por edital em `dados/editais/respostas_agente/<id>.json` com o formato indicado; depois rode `python -m src.enquadramento ingerir`.

Formato: {"itens": {<item>: <valor|null>}, "regras": <texto>, "requisitos": [..], "pontuacao": [{"criterio":..,"peso":..}], "documentos_exigidos": [..], "anexos": [{"nome":..,"url":..}], "pagina_divulgacao": <url do órgão|null>, "mini_parecer": <3-5 frases>, "enquadramento": {<id_associacao>: {"aderencia": 0-100, "chances": 0-100, "pontuacao_estimada": <texto>, "decisao": <texto>, "para_subir": [..], "riscos": [..]}}}

Associações: amc-jardim-america — Associação dos Moradores e Comerciantes do Jardim América — A.M.C. Jardim América · áreas assistencia_social, defesa_direitos, cultura, esporte, educacao, saude, crianca_adolescente, pessoa_idosa, meio_ambiente, cidadania, desenvolvimento_local, voluntariado, comunicacao_comunitaria · atuação GO, GO/Goiânia, GO/Goiânia/Jardim América, GO/Goiânia/Nova Suíça, GO/Goiânia/Conjunto Oasis · 43 anos


---
## janela-rouanet-2026 — Lei Rouanet — Lei 8.313/1991 (PRONAC) — inscrições 2026

Fonte (vetor): Ministério da Cultura — SALIC · UF BR · nível federal · situação aberta · fim 2026-10-31

Itens já obtidos: Objeto: Janela anual de inscrição de propostas. Modalidades: Mecenato (patrocínio e doaç, Prazo de inscrição: 2026-10-31, Órgão / financiador: Ministério da Cultura — SALIC, Território: Brasil, Esfera: federal, Área de atuação: cultura, Valor: variável e condicionado à aprovação do projeto no Salic: de R$ 0,01 até R$ 1.500, Resultado: análise contínua pelo MinC dentro da janela; publicação da aprovação no DOU e no, Prazo de recurso: recurso administrativo após indeferimento, no prazo fixado na IN vigente (10 dia, Requisitos: proponente PJ sem fins lucrativos com cadastro no Salic, atuação cultural compro, Anexos: formulários do Salic: proposta cultural, orçamento analítico, plano de distribui, Destinação: projetos culturais aprovados; recursos captados por renúncia fiscal (IRPJ/IRPF) 

Itens que FALTAM: Objeto, Prazo de inscrição, Resultado, Prazo de recurso, Valor, Órgão / financiador, Território, Esfera, Requisitos, Anexos, Destinação, Área de atuação

Anúncio: https://salic.cultura.gov.br/
Site institucional conhecido: https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet-1

Texto do edital (compacto):
```
(sem texto — localizar o edital no site do órgão)
```


---
## 0e732756dd062c3ae737 — Seleção Pública de Projetos para Patrocínio Cultural nº 01/2025 - Projetos Audiovisuais de Longa-metragem

Fonte (vetor): BNDES — Área Social · UF BR · nível federal · situação possivel · fim None

Itens já obtidos: Objeto: Seleção Pública de Projetos para Patrocínio Cultural nº 01/2025 - Projetos Audio, Órgão / financiador: BNDES — Área Social, Esfera: federal, Área de atuação: cultura, Prazo de inscrição: 2025-10-27, Resultado: 2025-11-18, Valor: R$ 15.000.000,00, Pontuação (regras): 50, Requisitos: da MP 2.228-1/01, art. 1º, inciso V., Anexos: Anexo I, Anexo II, Anexo III, Anexo IV, Anexo V

Itens que FALTAM: Prazo de recurso, Território, Destinação

Anúncio: https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios?1dmy&urile=wcm%3apath%3a%2Fbndes_institucional%2Fhome%2Ftransparencia%2Fpatrocinios%2Fselecao-publica-patrocinio-cultural-01-2025
Site institucional conhecido: não localizado

Texto do edital (compacto):
```
### Edital&nbsp; (site institucional)
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
1 
 
BANCO NACIONAL DE DESENVOLVIMENTO ECONÔMICO E SOCIAL - 
BNDES 
EDITAL 
Seleção Pública de Projetos para Patrocínio Cultural Nº 01/2025 – BNDES – 
Projetos Audiovisuais de Longa-Metragem 
 
OBJETO: Seleção pública de obras audiovisuais brasileiras de produção 
independente no formato de longa-metragem , para fins de patrocínio por parte do 
Sistema BNDES. O valor global da seleção será de at é R$ 15.000.000,00 (quinze 
milhões de reais). 
 
 
ANEXO I – MINUTA DE CONTRATO 
ANEXO II – CONTRAPARTIDAS 
ANEXO III - DECLARAÇÃO DE NÃO IMPEDIMENTOS E ADIMPL ÊNCIA COM 
PATROCÍNIOS 
ANEXO IV – RECURSOS CAPTADOS E/OU RECURSOS PRÓPRIOS JÁ 
INVESTIDOS 
ANEXO V – MANUAL PARA PRESTAÇÃO DE CONTAS 
 
PERÍODO DE INSCRIÇÃO: 26/09/2025 a 27/10/2025. 
 
DÚVIDAS SOBRE O EDITAL: As dúvidas acerca do presente Edital deverão ser 
encaminhadas ao BNDES , até 2 (dois) dias úteis anteriores à data de encerramento 
das inscrições, através do e-mail editalcultural2025@bndes.gov.br , devendo ser 
informados, no campo “assunto” Seleção Pública de Projetos para Patrocínio 
Cultural Nº 01/2025 – BNDES . As respostas serão divulgadas na página de 
Patrocínios no endereço eletrônico 
https://www.bndes.gov.br/patrocinios/editalcultural2025 . 
 
ACOMPANHAMENTO DOS ATOS DA SELEÇÃO PÚBLICA: Os avisos, as 
respostas a questionamentos e os resultados da presente Seleção serão divulgados 
na página de Patrocínios no endereço eletrônico 
https://www.bndes.gov.br/patrocinios/editalcultural2025 . 
 
CRÍTICAS, RECLAMAÇÕES E DENÚNCIAS: Críticas, reclamações e denúncias 
relativas a irregularidades ou ao descumprimento pe lo BNDES de suas normas 
internas ou da legislação vigente durante a condução deste procedimento de seleção 
pública poderão ser apresentadas à Ouvidoria do BNDES , por meio eletrônico 
(através de preenchimento do formulário disponível no endereço eletrônico 
www.bndes.gov.br/ouvidoria ), por meio postal (Caixa Postal 15054, CEP nº 20.0 31-
120, Rio de Janeiro – RJ) ou pelo telefone 0800-702 -6307. 
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
2 
 
 
LEGISLAÇÃO APLICÁVEL: Lei nº 13.303, de 01/07/2016, Instrução Normativa 
SECOM nº 2, de 23/12/2019, e Regulamento de Patrocí nio do Sistema BNDES, de 
14/08/2023, disponível no endereço eletrônico www.bndes.gov.br . 
 
TRATAMENTO DE DADOS PESSOAIS: A participação neste procedimento de 
seleção pública importa na manifestação de inequívoco consentimento do titular, seja 
ele pessoa física direta ou indiretamente relacionada ao proponente, inclusive sócios, 
empregados, contratados e/ou terceirizados, quando for o caso, dos dados pessoais 
que tenham se tornado públicos como condição para participação na seleção pública 
e para contratação, para tratamento pelo BNDES , na forma da Lei Geral de Proteção 
de Dados, Lei nº 13.709/2018. 
Poderão ser solicitados pelo BNDES dados pessoais adicionais a fim de viabilizar o 
cumprimento de obrigação legal. 
 
 
 
 
 
 
 
 
 
 
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
3 
 
 
 
SELEÇÃO PÚBLICA DE PROJETOS PARA PATROCÍNIO CULTURAL Nº 01/2025 – 
BNDES – PROJETOS AUDIOVISUAIS DE LONGA-METRAGEM 
EDITAL 
 
O BANCO NACIONAL DE DESENVOLVIMENTO ECONÔMICO E SOCIAL – BNDES , 
por intermédio de sua Área de Relacionamento, Marke ting e Cultura (ARMC), nos 
termos do disposto na Lei nº 13.303/2016, na Instru ção Normativa nº 02/2019, da 
Secretaria de Comunicação Social da Presidência da República (SECOM/PR), que 
disciplina o patrocínio dos órgãos e entidades do P oder Executivo Federal, e na 
Resolução CA-BNDES nº 07/2023, de 14/08/2023, que a provou o Regulamento de 
Patrocínio do Sistema BNDES, torna público, para conhecimento dos interessados, que 
está aberto Edital, na modalidade Seleção Pública, para a seleção de obras 
audiovisuais brasileiras de produção independente n o formato de longa-
metragem para fins de patrocínio por parte do BNDES , conforme as especificações 
deste Edital e de seus Anexos. 
 
1 OBJETO 
 
1.1 A presente Seleção Pública visa escolher, para fins de patrocínio, até 25 (vinte 
e cinco) obras audiovisuais brasileiras de produção independente no formato de longa-
metragem (PROJETOS), destinados à exibição em cinem as ou plataformas digitais, 
com as características definidas no item 4 deste Edital. 
 
1.2 Serão apoiados PROJETOS em estágios finais da cadei a produtiva (por 
exemplo, pós-produção, finalização, distribuição, c omercialização, promoção). Os 
PROJETOS inscritos deverão ser lançados até o final de 2026. 
 
1.3 O valor global a ser concedido a título de patrocín io por meio desta Seleção 
Pública será de até R$ 15.000.000,00 (quinze milhõe s de reais) e o valor fixo a ser 
concedido por PROJETO selecionado será de R$ 600.00 0,00 (seiscentos mil reais), 
para complementação de recursos necessários a viabi lização de projetos em estágio 
avançado de captação. 
 
 
2 ETAPAS 
 
O processo de seleção observará as seguintes etapas e cronograma: 
 
 
 
 
 
 
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
4 
 
 CRONOGRAMA DA SELEÇÃO 
 ETAPA DE INSCRIÇÕES Prazos 
 1 PUBLICAÇÃO DO EDITAL 26/09/2025 
 2 ENCERRAMENTO DAS INSCRIÇÕES 27/10/2025 
 3 PUBLICAÇÃO DA LISTA DE INSCRITOS até 29/10/2025 
 ETAPA DE SELEÇÃO 
 4 FASE 1 - PRÉ-QUALIFICAÇÃO POR SEGMENTO até 03/11/2025 
 5 PUBLICAÇÃO DA LISTA DE PRÉ-QUALIFICADOS VÁLIDOS POR 
SEGMENTO 03/11/2025 
 
 6 FASE 2 - CLASSIFICAÇÃO POR SEGMENTO E SELEÇÃO até 14/11/2025 
 7 PUBLICAÇÃO DA LISTA DE CLASSIFICADOS POR SEGMENTO até 18/11/2025 
 8 DIVULGAÇÃO DO RESULTADO FINAL - LISTA DE SELECIONADOS até 18/11/2025 
 ETAPA DE ANÁLISE TÉCNICA E CONTRATAÇÃO 
 9 INÍCIO DA ANÁLISE TÉCNICA E DOS PROCEDIMENTOS PRÉVIOS 
À CONTRATAÇÃO 
a partir de 
18/11/2025 
 
 
3 CONDIÇÕES E VEDAÇÕES PARA PARTICIPAÇÃO 
 
3.1 O proponente deverá ser empresa produtora brasilei ra registrada na ANCINE cuja 
obra audiovisual brasileira de produção independent e satisfaça os requisitos da MP 
2.228-1/01, art. 1º, inciso V. 
 
3.2 Os PROJETOS contratados assumirão a obrigação de iniciar sua exibição pública 
no período de 01/01/2026 a 31/12/2026 , sem prejuízo de poder o BNDES estender o 
referido período, mediante comum acordo com o patrocinado. 
 
3.2.1 Caso o PROJETO contratado não inicie sua exibição p ública no período 
definido no item 3.2, o BNDES notificará o contrata do solicitando a devolução 
total ou proporcional dos valores já pagos, atualizados pela taxa SELIC, pro rata 
tempore, desde a data da efetivação do pagamento pe lo BNDES até a data de 
sua devolução, que deverá ocorrer no prazo de até 10 (dez) dias úteis, contados 
da data da solicitação, sob pena de pagamento de multa de 2% (dois por cento) 
sobre os valores já pagos, por dia de atraso, até o limite de 30% (trinta por cento), 
sem prejuízo de aplicação de outras penalidades cabíveis. 
 
3.3 Além de outras obrigações previstas no Anexo I - Mi nuta de Contrato, os 
proponentes que forem selecionados se obrigarão a: 
 
a) realizar, no Brasil, evento de pré-estreia ou lançamento do PROJETO no 
período de 01/01/2026 a 31/12/2026 ; 
b) executar todas as contrapartidas padrão descrita s no Anexo II deste Edital, além 
daquelas que poderão ser negociadas na Análise Técn ica, descrita no item 7 
deste Edital; 
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
5 
 
c) contar com trabalho de assessoria de imprensa; 
d) apresentar, na prestação de contas ao BNDES , clipagem das menções ao 
PROJETO na internet (incluindo as redes sociais) e na mídia impressa; e 
e) apresentar, na prestação de contas ao BNDES , relatório de valoração da mídia 
espontânea alcançada pelo PROJETO. 
 
3.4 É vedada a participação de proponente que se insira em algu ma das situações 
abaixo: 
a) pessoa física ou MEI; 
b) entidades político-partidárias, religiosas, ou q ue promovam, ainda que de forma 
indireta, personalidades político-partidárias ou religiosas; 
c) associações de empregados ativos ou aposentados das empresas integrantes 
do Sistema BNDES ; 
d) empresa que mantenha contrato de prestação de se rviços de comunicação com 
o Sistema BNDES , tais como serviços de publicidade, de promoção, d e 
comunicação digital, de assessoria de imprensa ou de relações públicas; 
e) que esteja impedido de contratar com o Sistema B NDES; 
f) cuja pessoa jurídica detenha, entre seus sócios, administradores, associados ou 
congêneres com poder de direção, cônjuge, companhei ro ou parente, em linha 
reta ou colateral, por consanguinidade ou afinidade , até o terceiro grau, de 
pessoa que possua cargo em comissão ou função de co nfiança lotado na Área 
de Relacionamento, Marketing e Cultura – ARMC, no D epartamento Jurídico de 
Licitações e Contratos – AJI/JULIC, ou de autoridad e a eles hierarquicamente 
superiores, incluindo Diretorias Executivas do Sist ema BNDES, e empregados 
que possuam poderes para firmar os contratos de patrocínio do Sistema BNDES ; 
g) que não esteja regular nos âmbitos fiscal e prev idenciário, nos termos da lei; 
h) que explore o trabalho infantil, degradante ou escravo e/ou atente contra a ordem 
pública; 
i) que não seja titular ou detentor dos direitos de realização/organização e/ou 
comercialização do PROJETO; 
j) que incorra em qualquer vedação de contratação c ontida na Lei 13.303/2016. 
 
3.5 O proponente deverá observar o Código de Ética do Sistema BNDES vigente ao 
tempo da contratação, o qual deverá ser consultado por intermédio do sítio 
www.bndes.gov.br , assegurando-se de que seus representantes legais e que todos os 
profissionais envolvidos na execução do objeto paut em seu comportamento e sua 
atuação pelos princípios nele constantes. 
 
3.6 É vedada a inscrição de PROJETOS: 
a) que promovam discriminação de qualquer natureza, notadamente quanto a raça, 
Classificação: Documento Controlado até a publicação do Edital (conforme OS PRESI Nº 01/2015- BNDES) 
Restrição de Acesso: Empresas do Sistema BNDES 
Unidade Gestora: ARMC/DECULT 
 
6 
 
etnia, nacionalidade, religião, política, gênero, orientação sexual, condição social 
e condição física; 
b) que promovam a criação e/ou disseminação de notí cias falsas – fake news ; 
c) que causem ou incentivem maus tratos a animais, a exemplo de rodeios e 
vaquejadas; 
d) que estimulem a violência e o uso de drogas; 
e) que violem direitos de terceiros, incluídos os d e propriedade intelectual; 
f) de cunho político-eleitoraI-partidário, cujos in vestimentos captados a título de 
patrocínio tenham como finalidade direta ou indireta o apoio a financiamento de 
campanhas, realização de comícios, discursos, ou qu alquer outra atividade 
vinculada a partidos políticos, candidatos e/ou sua s coligações, bem como 
promoção pessoal de autoridade ou de servidor públi co dos governos Federal, 
Estadual ou Municipal, além de apoio a manifestaçõe s, protestos, passeatas 
e/ou reivindicações de qualquer natureza; 
g) que já tenha sido apoiado, por meio de qualquer instrumento ou forma, pelo 
Sistema BNDES; 
h) cuja captação de recursos, já incluindo o valor do patrocínio do BNDES por meio 
desta Seleção Pública, tenha ultrapassado o valor do seu orçamento global. 
 
3.7 São vedados PROJETOS que, a critério da Comissão Av aliadora, estejam em 
desacordo com o Código de Ética do Sistema BNDES , disponível em 
https://www.bndes.gov.br/wps/portal
```
