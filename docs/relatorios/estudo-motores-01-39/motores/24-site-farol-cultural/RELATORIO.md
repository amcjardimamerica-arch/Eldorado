# Motor 24 — site-farol-cultural (Farol Cultural)

Estudo feito em 02/10/2026. Tipo de site: AGREGADOR. Usei 35 chamadas de WebFetch. O `curl` direto foi recusado pelo proxy da sessão (CONNECT 403, política da organização), então toda a coleta passou pelo WebFetch.

## 1. Rota (teste e conclusão)

**robots.txt** (`https://farolcultural.art/robots.txt`): `Allow: /`. Os bloqueios são `/admin`, `/dashboard`, `/api/proxy-geo` e `/api/proxy-edital`. A rota `/api/v1/editais` está liberada. O arquivo declara `Sitemap: https://farolcultural.art/sitemap.xml`.

| URL testada | Responde? | O que entrega |
|---|---|---|
| `https://farolcultural.art/api/v1/editais` (rota configurada) | sim, JSON | `{success, data, meta, error}`; 20 itens por página; `meta.total = 1028`, `total_pages = 52`. Campos: `id, slug, titulo, resumo, instituicao_nome, pais, estado, cidade, area_artistica[], tipo, status (Aberto/Encerrado/EmBreve), valor_total, valor_por_projeto, moeda, vagas, data_publicacao, data_inicio_inscricao, data_fim_inscricao, url_original, url_pdf, latitude, longitude, created_at` |
| `https://farolcultural.art/api/v1/editais?per_page=50&page=N` | sim | 50 itens por página e 21 páginas. Com `per_page=100`, a API devolve só 50 (teto). Ordem: prazo crescente; o fim (p. 21) traz os itens sem prazo |
| `https://farolcultural.art/api/v1/editais?status=encerrado&per_page=50&page=2` | **não, HTTP 400** | o parâmetro `status` com esse valor é rejeitado |
| `https://farolcultural.art/editais` (página do titular) | sim | "497 abertos"; filtros por área e status; ordenação por título, prazo, valor e país; sem paginação visível |
| `https://farolcultural.art/arquivo` | sim | encerrados: "518", 26 páginas de 20 itens (`?page=N&per_page=20`). A amostra mostra itens com prazo em 2027 rotulados como encerrados |
| `https://farolcultural.art/sitemap.xml` | sim | cerca de 13 páginas institucionais e cerca de 480 páginas `/e/<slug>`, sem `lastmod` e sem sub-sitemaps. Lista só os abertos |
| `https://farolcultural.art/api` (documentação) | sim | endpoints `/api/v1/editais` e `/api/v1/editais/geo`. A página cita parâmetros `status, page, per_page, estado/uf, area, since/updated_after, order/sort, q` e diz que exige "chave gratuita" (api@farolcultural.art), com atribuição obrigatória. Na prática, a API respondeu **sem chave** |

**Conclusão.** A rota configurada é a melhor que existe: é JSON, traz prazo, data de publicação (com frequência nula) e `url_original`, e cobre abertos e encerrados na mesma lista. Ela também já é o histórico. Há dois ajustes verificados:
- usar `?per_page=50&page=1..total_pages`, em vez da página padrão de 20, que hoje obriga a 52 requisições;
- ler `meta.total_pages` para saber onde parar.

O sitemap e a página `/editais` são piores (só abertos, sem dados estruturados). Os filtros que a documentação cita (`since`, `uf`, `q`) **não foram testados** além de `status`, que deu 400.

**Qualidade dos campos (amostra de cerca de 500 itens):**
- `valor_total` vem preenchido em cerca de 10% dos itens;
- `data_publicacao` vem nula em 42%;
- `estado` vem nulo em quase todos os itens publicados via "Mapa Cultural" e via redes internacionais;
- `instituicao_nome` = "Mapa Cultural" esconde o município real em 148 itens;
- `status` contradiz o prazo em alguns casos: há itens "Encerrado" com prazo em 03, 04, 05 e 07/10/2026 (Res Artis) e "EmBreve" com prazo já vencido (Guggenheim, Ipaporanga);
- há ruído: diários oficiais inteiros do Querido Diário como "Aberto", notícias da Spcine de 2018 como "Aberto" e um item que parece ser de pessoa física (excluído).

## 2. Histórico de 3 anos (02/10/2023 a 02/10/2026)

**Como ver o histórico.** A própria API lista abertos e encerrados juntos, em ordem de prazo. Extraí as páginas 1 a 10 (com `per_page=50`), que vão de 2021 até 08/10/2026, e a página 21 (itens sem prazo). As páginas 11 a 20 contêm só abertos, que já estão nos indícios (493 itens), e não foram reextraídas.

**Limite de profundidade.** O site guarda quase nada antes de 2026. No período, só aparecem 2 itens com prazo em 2024 (Kinoforum) e 1 em 2025 (Iphan). O acervo começa de fato em fevereiro e março de 2026. Os "3 anos" não existem nesta fonte; o histórico real tem cerca de 8 meses.

**Números do período:** 504 oportunidades, sendo 456 encerradas, 30 abertas e 18 sem data. Das 504:
- 36 já estavam nos indícios (marcadas "[já nos indícios]");
- 461 são novas;
- 13 foram verificadas no site oficial.

**Verificação por amostra de links oficiais (17 tentativas, 14 abriram):**

| # | Link | Abre? | É do financiador? | Observação |
|---|---|---|---|---|
| 1 | pncp.gov.br/app/editais/01067941000105/2025/74 (via API PNCP) | sim | sim (Município de Pirenópolis/GO) | termo de colaboração com OSC, R$ 300 mil, até 16/09/2027 |
| 2 | pncp.gov.br/app/editais/05780030000181/2025/76 (via API PNCP) | sim | sim (FAC Goiânia) | Rede Municipal de Pontos de Cultura de Goiânia, encerrado em 30/07/2026 |
| 3 | pncp.gov.br/app/editais/01130277000100/2026/72 (via API PNCP) | sim | sim (Davinópolis/GO) | PNAB, R$ 31,8 mil, encerrado em 29/08/2026 |
| 4 | pncp.gov.br/app/editais/07598634000137/2026/137 (via API PNCP) | sim | sim (Sobral/CE) | R$ 260 mil, prazo 02/10/2026 |
| 5 | mapagoiano.cultura.go.gov.br/oportunidade/957/ | sim | plataforma oficial Secult GO | sem datas nem valor na página |
| 6 | gov.br/cultura/.../programa-rouanet-centro-oeste | sim | sim (MinC) | 16/06 a 13/08/2026; R$ 29 mi; inclui GO |
| 7 | gov.br/cultura/.../edital-de-intercambio-cultural-... | sim | sim (MinC) | até 06/11/2026; só pessoa física |
| 8 | mapa.cultura.gov.br/oportunidade/8012/ | sim | sim (Mapa da Cultura/MinC) | mesmo edital do item 7 |
| 9 | mapa.cultura.gov.br/oportunidade/5843/ (HIP HOP LAB, GO) | parcial | plataforma oficial | Goiânia e Aparecida; sem datas |
| 10 | gulbenkian.pt/bolsas-lista/apoio-a-circulacao-internacional/ | sim | sim | até 31/10/2026; só Portugal |
| 11 | spcine.com.br/... (NFVF) | sim | sim | **prazo era 17/07/2025**; nos indícios está como sem prazo e "Aberto": erro do agregador |
| 12 | prefeitura.poa.br/smc/... Açorianos de Dança | sim | sim | 30/03 a 29/11/2026 |
| 13 | resartis.org/open-call/wolf-studio-jaipur-... | sim | **não**, rede agregadora | residência paga (€ 2.200), não é financiamento |
| 14 | petrobras.com.br/cultural/selecoes-publicas-culturais | sim | sim | R$ 270 mi; prazo não visível na página |
| 15 | dgartes.gov.pt/pt/node/10265 | **não** (timeout ao ler o robots.txt) | — | site caiu; anotado e segui |
| 16 | iberescena.org/Noticias/2387 | página vazia (só marcação) | — | não confirmado |
| 17 | prosas.com.br/editais/16452-edital-ambev-brasilidades-2026 | **bloqueado pelo robots.txt** | — | respeitado; não confirmado |

O PNCP é uma aplicação de página única: o link `/app/editais/...` não mostra conteúdo sem JavaScript. A API `https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}` traz órgão, objeto, datas e valor.

### Financiadores e programas que aparecem (com domínio do link oficial)

Há 190 nomes distintos de financiador ou publicador, mas "Mapa Cultural" agrupa dezenas de municípios do CE, ES, SE e PE e redes nacionais. A lista completa vem a seguir. "—" significa que o link é de rede agregadora (Res Artis, TransArtists, Plataforma 9 etc.), sem site oficial direto.

| financiador / programa | nº no histórico | domínio do link oficial |
|---|---|---|
| Mapa Cultural | 148 | mapa.cultura.es.gov.br, mapa.cultura.gov.br, mapacultural.pe.gov.br, mapacultural.se.gov.br, mapacultural.secult.ce.gov.br |
| Res Artis (rede de residências) | 53 | — |
| DGARTES | 49 | www.dgartes.gov.pt |
| Plataforma 9 | 19 | — |
| TransArtists / DutchCulture | 16 | www.transartists.org |
| Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | 6 | www.cultura.sp.gov.br |
| Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | 5 | www.mapacultural.pe.gov.br |
| MUNICIPIO DE ALAGOINHAS | 5 | pncp.gov.br |
| MUNICIPIO DE OLINDA | 4 | pncp.gov.br |
| Guia Kinoforum | 3 | — |
| MUNICIPIO DE VILA RICA | 2 | pncp.gov.br |
| MUNICIPIO DE AQUIDAUANA | 2 | pncp.gov.br |
| FUNDACAO MUNICIPAL DE CULTURA | 2 | pncp.gov.br |
| Centro Cultural Veras | 2 | centroculturalveras.org, rededasartes.cultura.gov.br |
| MUNICIPIO DE LAGOA VERMELHA | 2 | pncp.gov.br |
| MUNICIPIO DE BELO JARDIM | 2 | pncp.gov.br |
| Prefeitura de Belo Horizonte — Secretaria Municipal de Cultura / Fundo Municipal de Cultura (LMIC) | 2 | prefeitura.pbh.gov.br |
| MUNICIPIO DE UNIAO | 2 | pncp.gov.br |
| MUNICIPIO DE GRAVATAI | 2 | pncp.gov.br |
| Fundação Catarinense de Cultura (FCC) | 2 | www.cultura.sc.gov.br |
| MUNICIPIO DE CATANDUVA | 2 | pncp.gov.br |
| MUNICIPIO DE FAZENDA RIO GRANDE | 2 | pncp.gov.br |
| FUNDO MUNICIPAL DE EDUCACAO DE ALVORADA DO NORTE - FME | 2 | pncp.gov.br |
| Funarte — Fundação Nacional de Artes | 2 | rededasartes.cultura.gov.br |
| Programa Ibermúsicas | 2 | www.ibermusicas.org |
| Ibermúsicas | 2 | www.ibermusicas.org |
| Spcine | 1 | spcine.com.br |
| Iphan — Instituto do Patrimônio Histórico e Artístico Nacional | 1 | www.gov.br |
| Instituto Cultural Vale | 1 | institutoculturalvale.org |
| Secretaria Municipal de Cultura do Rio de Janeiro | 1 | cultura.prefeitura.rio |
| Fundação Catarinense de Cultura — FCC | 1 | www.cultura.sc.gov.br |
| Conservatório de Tatuí — Sustenidos OS | 1 | www.conservatoriodetatui.org.br |
| Governo do Estado do Paraná | 1 | www.parana.pr.gov.br |
| Secretaria Municipal de Cultura — São Paulo | 1 | prefeitura.sp.gov.br |
| Museu da Imagem e do Som — MIS-SP | 1 | — |
| Festival of Future Storytellers | 1 | — |
| MUNICIPIO DE ARARAS | 1 | pncp.gov.br |
| MUNICIPIO DE PARELHAS | 1 | pncp.gov.br |
| Center for Advanced Internet Studies (CAIS) | 1 | cais-research.de |
| Global Vision Access (GVA) | 1 | vitrine.impactospositivos.com |
| IEPHA-MG / SECULT-MG | 1 | — |
| MUNICIPIO DE BENTO GONCALVES | 1 | pncp.gov.br |
| Associação Portuguesa de Museologia (APOM) | 1 | apom.pt |
| MUNICIPIO DE TACAIMBO | 1 | pncp.gov.br |
| MUNICIPIO DE BARRA LONGA | 1 | pncp.gov.br |
| SECULT-PE / CEPE | 1 | www.mapacultural.pe.gov.br |
| FAPESP | 1 | fapesp.br |
| MUNICIPIO DE LAJE | 1 | pncp.gov.br |
| MUNICIPIO DE MATOZINHOS | 1 | pncp.gov.br |
| Fundo de Apoio à Cultura — FAC (Goiânia) | 1 | pncp.gov.br |
| Emsländische Landschaft e.V. | 1 | www.emslaendische-landschaft.de |
| DAAD — Serviço Alemão de Intercâmbio Acadêmico | 1 | www.daad-brasil.org |
| Kometa | 1 | kometarevue.com |
| Les Nuits Magiques | 1 | www.lesnuitsmagiques.fr |
| Cinéopen Festival / CCJB Pontarlier | 1 | — |
| Club Audiovisuel de Vichy | 1 | www.viff.info |
| Imprensa Nacional-Casa da Moeda (INCM) | 1 | incm.pt |
| Elektronmusikstudion (EMS) + Akademie der Künste (AdK) | 1 | elektronmusikstudion.se |
| Lee Ufan Arles / Maison Guerlain | 1 | en.leeufan-arles.org |
| MUNICIPIO DE INDAIATUBA | 1 | pncp.gov.br |
| FUNDACAO MUNICIPAL DE CULTURA DE BOMBINHAS | 1 | pncp.gov.br |
| MUNICIPIO DE PORTEIRINHA | 1 | pncp.gov.br |
| FUNDO DE APOIO A CULTURA-FAC | 1 | pncp.gov.br |
| MUNICIPIO DE LIVRAMENTO DE NOSSA SENHORA | 1 | pncp.gov.br |
| Petrobras | 1 | petrobras.com.br |
| BigCi — Bilpin international ground for Creative initiatives | 1 | bigci.org |
| IBER-RUTAS / SEGIB | 1 | segib.org |
| BBA Gallery | 1 | bba-prizes.com |
| CNPq / FNDCT | 1 | www.gov.br |
| SECULT-PE | 1 | www.mapacultural.pe.gov.br |
| Vital Strategies Brasil / Google.org | 1 | www.vitalstrategies.org |
| Iphan / Centro Nacional de Folclore e Cultura Popular (CNFCP) | 1 | www.gov.br |
| FAPES | 1 | fapes.es.gov.br |
| MUNICIPIO DE CROATA | 1 | pncp.gov.br |
| Sesc/RS — Serviço Social do Comércio do Rio Grande do Sul | 1 | www.sesc-rs.com.br |
| MUNICIPIO DE CARMO DO PARANAIBA | 1 | pncp.gov.br |
| Prague City of Literature / Municipal Library of Prague | 1 | www.prahamestoliteratury.cz |
| MUNICIPIO DE TAQUARITINGA DO NORTE | 1 | pncp.gov.br |
| MUNICIPIO DE CONCEICAO DE IPANEMA | 1 | pncp.gov.br |
| Goethe-Institut Vietnam | 1 | www.goethe.de |
| CONSORCIO INTERMUNICIPAL GRANDE ABC | 1 | pncp.gov.br |
| Ministério da Cultura (MinC) — Economia Criativa | 1 | mapa.cultura.gov.br |
| TaDA – Textile and Design Alliance | 1 | tada-residency.ch |
| K3 – Zentrum für Choreographie / Tanzplan Hamburg | 1 | www.k3-hamburg.de |
| DOK Leipzig | 1 | www.dok-leipzig.de |
| BNDES | 1 | www.bndes.gov.br |
| Ministério da Cultura | 1 | www.gov.br |
| Conselho de Arquitetura e Urbanismo do Rio Grande do Sul (CAU/RS) | 1 | transparencia.caurs.gov.br |
| Hong Kong Baptist University (IWW) | 1 | iww.hkbu.edu.hk |
| Secretaria de Estado da Cultura do Tocantins (Secult-TO) / Fundo Estadual de Cultura | 1 | www.to.gov.br |
| Global Gastronomy Museum | 1 | www.global-gastronomy.com |
| Sedac-RS / Ieacen / Fundação Theatro São Pedro | 1 | cultura.rs.gov.br |
| Fundo de Fomento Cultural / GEPAC — Ministério da Cultura de Portugal | 1 | culturaportugal.gov.pt |
| Cité internationale des arts | 1 | www.citeinternationaledesarts.fr |
| Sesc Paraná | 1 | www.sescpr.com.br |
| MUNICIPIO DE RIBEIRAO DAS NEVES | 1 | pncp.gov.br |
| Fundação Cultural de Curitiba (FCC) / Prefeitura de Curitiba | 1 | www.fundacaoculturaldecuritiba.com.br |
| MUNICIPIO DE CAPAO DA CANOA | 1 | pncp.gov.br |
| MUNICIPIO DE VERDELANDIA | 1 | pncp.gov.br |
| MUNICIPIO DE VIANA | 1 | pncp.gov.br |
| MUNICIPIO DE GUAIRA | 1 | pncp.gov.br |
| MUNICIPIO DE CAMPOS DO JORDAO | 1 | pncp.gov.br |
| MUNICIPIO DE VERA CRUZ | 1 | pncp.gov.br |
| Sesc RN | 1 | sescrn.com.br |
| MUNICIPIO DE MACAE | 1 | pncp.gov.br |
| Amnesty International France | 1 | — |
| MUNICIPIO DE ABREU E LIMA | 1 | pncp.gov.br |
| MUNICIPIO DE BELTERRA | 1 | pncp.gov.br |
| Secretaria da Cultura do Estado do Rio Grande do Sul | 1 | www.procultura.rs.gov.br |
| Secretaria de Estado da Cultura do Rio Grande do Sul | 1 | cultura.rs.gov.br |
| FUNDACAO CULTURAL CARLOS DRUMMOND DE ANDRADE | 1 | pncp.gov.br |
| Município de Davinópolis | 1 | pncp.gov.br |
| Museu da Língua Portuguesa (IDBrasil Cultura, Educação e Esporte) | 1 | www.idbr.org.br |
| IPDJ — Instituto Português do Desporto e Juventude | 1 | ipdj.gov.pt |
| Fundação Bienal MoAC Biss | 1 | — |
| Kunsthalle Rostock / Kulturstiftung Rostock | 1 | www.kunsthallerostock.de |
| Künstlerhaus Otte 1 | 1 | www.otte1.org |
| MUNICIPIO DE BALNEARIO ARROIO DO SILVA | 1 | pncp.gov.br |
| MUNICIPIO DE BALSAS | 1 | pncp.gov.br |
| Fondation Jan Michalski pour l'écriture et la littérature | 1 | fondation-janmichalski.com |
| Secretaria de Estado de Cultura e Economia Criativa do DF | 1 | sufic.cultura.df.gov.br |
| FAAP — Fundação Armando Alvares Penteado | 1 | www.faap.br |
| MINISTERIO DA CULTURA | 1 | pncp.gov.br |
| Kulturbüro der Stadt Duisburg | 1 | www.duisburg.de |
| MUNICIPIO DE TEIXEIRAS | 1 | pncp.gov.br |
| MUNICIPIO DE EUCLIDES DA CUNHA | 1 | pncp.gov.br |
| Senatsverwaltung für Kultur und Gesellschaftlichen Zusammenhalt | 1 | www.berlin.de |
| MUNICIPIO DE ARAPIRACA | 1 | pncp.gov.br |
| MUNICIPIO DE DIAS D'AVILA | 1 | pncp.gov.br |
| Facteur de Ciel | 1 | www.facteurdeciel.com |
| MUNICIPIO DE ABRE CAMPO | 1 | pncp.gov.br |
| MUNICIPIO DE ARCEBURGO | 1 | pncp.gov.br |
| BOM JESUS DO ITABAPOANA PREFEITURA | 1 | pncp.gov.br |
| MUNICIPIO DE ASSIS CHATEAUBRIAND | 1 | pncp.gov.br |
| Fundação Catarinense de Cultura (FCC) / Governo de Santa Catarina | 1 | prosas.com.br |
| MUNICIPIO DE FRAIBURGO | 1 | pncp.gov.br |
| MUNICIPIO DE NEPOMUCENO | 1 | pncp.gov.br |
| MUNICIPIO DE DOIS IRMAOS | 1 | pncp.gov.br |
| Centre Chorégraphique National de Caen en Normandie | 1 | ccncn.eu |
| MUNICIPIO DE BOM JESUS DO NORTE | 1 | pncp.gov.br |
| MacDowell | 1 | www.macdowell.org |
| MUNICIPIO DE SAO BENTO DO SUL | 1 | pncp.gov.br |
| MUNICIPIO DE SANTO ANTONIO DE JESUS | 1 | pncp.gov.br |
| MUNICIPIO DE PALOTINA | 1 | pncp.gov.br |
| MUNICIPIO DE SAO MIGUEL DAS MATAS | 1 | pncp.gov.br |
| Eurazeo Endowment Fund | 1 | en.newsroom.eurazeo.com |
| Ministerio de Educación y Cultura (MEC) — Fondo de Incentivo Cultural | 1 | www.gub.uy |
| MUNICIPIO DE SAO MIGUEL DOS CAMPOS | 1 | pncp.gov.br |
| John Simon Guggenheim Memorial Foundation | 1 | www.gf.org |
| Revista SÁBADO | 1 | concursodefotografia.com |
| DGARTES / Camões, I.P. / OEI | 1 | www.dgartes.gov.pt |
| Prefeitura da Estância Turística de Avaré | 1 | fampop.art |
| MUNICIPIO DE CACHOEIRINHA | 1 | pncp.gov.br |
| VS. Editor (Vasco Santos Editor) | 1 | www.vseditor.net |
| SECRETARIA MUNICIPAL DE ADMINISTRACAO | 1 | pncp.gov.br |
| MUNICIPIO DE FLORIANOPOLIS | 1 | pncp.gov.br |
| Festival du Court Métrage de Clermont-Ferrand | 1 | www.lecourt-clermont.org |
| MUNICIPIO DE CODO | 1 | pncp.gov.br |
| Fundação Conrado Wessel | 1 | www.fcw.org.br |
| MUNICIPIO DE COLINA | 1 | pncp.gov.br |
| Ars Electronica (com České Budějovice 2028) | 1 | ars.electronica.art |
| SECRETARIA MUNICIPAL DE EDUCACAO, ESPORTE E LAZER | 1 | pncp.gov.br |
| MUNICIPIO DE FAGUNDES VARELA | 1 | pncp.gov.br |
| Universidade de Heidelberg — HCIAS | 1 | www.hcias.uni-heidelberg.de |
| Georg-Eckert-Institut | 1 | www.gei.de |
| Ambev | 1 | prosas.com.br |
| MUNICIPIO DE SOBRAL | 1 | pncp.gov.br |
| Instituto do Cinema e do Audiovisual, I.P. (ICA) | 1 | www.ica-ip.pt |
| Câmara Municipal de Montijo | 1 | www.mun-montijo.pt |
| Fondation Camargo | 1 | camargofoundation.org |
| Programa Ibermúsicas / FUNARTE | 1 | www.ibermusicas.org |
| Programa Ibermúsicas (com DGARTES, FUNARTE e CPLP) | 1 | www.ibermusicas.org |
| Município de Sobral | 1 | pncp.gov.br |
| MUNICIPIO DE ITATINGA | 1 | pncp.gov.br |
| MUNICIPIO DE BARAO DE COCAIS | 1 | pncp.gov.br |
| MUNICIPIO DE NOVA MUTUM | 1 | pncp.gov.br |
| ESTADO DA BAHIA | 1 | pncp.gov.br |
| Residency Wolf (Jaipur, Índia) | 1 | — |
| Fundação Calouste Gulbenkian | 1 | gulbenkian.pt |
| Ministério da Cultura — Secretaria do Audiovisual | 1 | www.gov.br |
| Prefeitura de Porto Alegre — Secretaria Municipal da Cultura / Centro Municipal de Dança | 1 | prefeitura.poa.br |
| (sem nome) | 1 | mapa.cultura.gov.br |
| Município de Pirenópolis (Secretaria Municipal de Educação e Cultura) | 1 | pncp.gov.br |
| Mapa Goiano (plataforma da Secult Goiás) | 1 | mapagoiano.cultura.go.gov.br |
| Canada Council for the Arts | 1 | canadacouncil.ca |
| TECNO BARCA | 1 | rededasartes.cultura.gov.br |
| Riofilme | 1 | riofilme.com.br |
| Festival Art'Incluir | 1 | rededasartes.cultura.gov.br |
| Secretaria de Cultura de Pernambuco — SECULT-PE | 1 | www.cultura.pe.gov.br |
| Funarte | 1 | www.gov.br |

### Tabela do histórico (504 oportunidades, ordenadas por prazo)

| data | título | financiador | site oficial | prazo | estado | aplicável |
|---|---|---|---|---|---|---|
| — | Women's International Film and Arts Festival | Guia Kinoforum | (aguardar_fonte) | 2024-01-07 | encerrado_arquivar | nao |
| — | Pop Corn Festival del Corto | Guia Kinoforum | (aguardar_fonte) | 2024-05-20 | encerrado_arquivar | nao |
| 2025-06-04 | Spcine — edital de Desenvolvimento e Work in Progress em parceria com a NFVF (África do Sul) | Spcine | https://spcine.com.br/spcine-abre-inscricoes-para-edital-de-desenvolvimento-e-work-in-progress-em-parceria-com-a-national-film-and-video-foundation/ | 2025-07-17 | encerrado_arquivar | nao |
| — | Edital de Termo de Execução Cultural referente ao Inventário Participativo | Iphan — Instituto do Patrimônio Histórico e Artístico Nacional | https://www.gov.br/iphan/pt-br/acesso-a-informacao/editais-e-selecoes/abertos/edital-de-termo-de-execucao-cultural-no-1-2025-iphan-df-1 | 2025-12-18 | encerrado_arquivar | depende |
| — | Concurso para Partituras "Intimacy of Creativity – Composers Meet Performers" | DGARTES | (aguardar_fonte) | 2026-01-26 | encerrado_arquivar | nao |
| 2026-02-11 | Programa artístico "Arts on the Edges" está com candidaturas abertas | DGARTES | (aguardar_fonte) | 2026-02-11 | encerrado_arquivar | nao |
| 2026-02-19 | TranziT – Festival Europeu de Práticas Teatrais Contemporâneas | DGARTES | (aguardar_fonte) | 2026-02-19 | encerrado_arquivar | nao |
| 2026-03-05 | Programa FlowCCA 2026 para Jovens Artistas (UE e Tunísia) | DGARTES | (aguardar_fonte) | 2026-03-05 | encerrado_arquivar | nao |
| 2026-03-05 | Programa de residência artística do ARCUS Project | DGARTES | (aguardar_fonte) | 2026-03-05 | encerrado_arquivar | nao |
| 2026-03-10 | Showcase Outdoor Arts Portugal | DGARTES | (aguardar_fonte) | 2026-03-10 | encerrado_arquivar | nao |
| 2026-03-11 | Open Call RESIDÊNCIAS DE ESCRITA aberta a autores nacionais e internacionais | DGARTES | (aguardar_fonte) | 2026-03-11 | encerrado_arquivar | nao |
| 2026-03-12 | Residência artística SVĚTOVA 1 | DGARTES | (aguardar_fonte) | 2026-03-12 | encerrado_arquivar | nao |
| 2026-03-18 | Dummy Book Award Arles 2026 | DGARTES | (aguardar_fonte) | 2026-03-18 | encerrado_arquivar | nao |
| 2026-03-11 | A Ci.CLO abre candidaturas para Apoio à Produção da Bienal Fotografia do Porto | DGARTES | (aguardar_fonte) | 2026-03-18 | encerrado_arquivar | nao |
| 2026-03-19 | DGARTES abre inscrições para Bolsa de Consultores e Especialistas | DGARTES | https://www.dgartes.gov.pt/pt/node/9678 | 2026-03-19 | encerrado_arquivar | nao |
| 2026-03-19 | A Solar – Galeria de Arte Cinemática abriu candidaturas para Laboratório | DGARTES | (aguardar_fonte) | 2026-03-19 | encerrado_arquivar | nao |
| 2026-03-12 | Skopje, Capital Europeia da Cultura 2028 (Macedónia do Norte) convida à apresentação | DGARTES | (aguardar_fonte) | 2026-03-29 | encerrado_arquivar | nao |
| 2026-03-31 | Open Call SARACOTEIO – Dança no Ecrã | DGARTES | (aguardar_fonte) | 2026-03-31 | encerrado_arquivar | nao |
| 2026-04-01 | Residência de Arte em Vidro "Interior/Exterior" | DGARTES | (aguardar_fonte) | 2026-04-01 | encerrado_arquivar | nao |
| 2026-03-18 | Open Call: Künstlerhaus Marktoberdorf - Exposição e Programa Experimental | DGARTES | (aguardar_fonte) | 2026-04-08 | encerrado_arquivar | nao |
| 2026-04-09 | Programa de Residências da Pim Spazio Scenico | DGARTES | (aguardar_fonte) | 2026-04-09 | encerrado_arquivar | nao |
| 2026-04-09 | Al-Tiba9 Art Magazine (edição 21) convida à apresentação de candidaturas | DGARTES | (aguardar_fonte) | 2026-04-09 | encerrado_arquivar | nao |
| 2026-04-02 | Residências Rauschenberg 2026 em Tecnologia e Media Art | DGARTES | (aguardar_fonte) | 2026-04-12 | encerrado_arquivar | nao |
| — | Residência em Graz para Fotógrafos Internacionais | DGARTES | (aguardar_fonte) | 2026-04-15 | encerrado_arquivar | nao |
| 2026-04-15 | 12ª edição da Academia Europeia de Teatro | DGARTES | (aguardar_fonte) | 2026-04-15 | encerrado_arquivar | nao |
| 2026-04-15 | Programa Bolsas Jovens Criadores 2026 | DGARTES | (aguardar_fonte) | 2026-04-15 | encerrado_arquivar | nao |
| 2026-04-23 | "Obra Abierta. Premio Internacional de Artes Visuales" | DGARTES | (aguardar_fonte) | 2026-04-23 | encerrado_arquivar | nao |
| 2026-04-23 | Feira internacional de arte contemporânea do Luxemburgo abriu candidaturas | DGARTES | (aguardar_fonte) | 2026-04-23 | encerrado_arquivar | nao |
| 2026-04-24 | Bolsa Mariana Nobre Vieira | DGARTES | (aguardar_fonte) | 2026-04-24 | encerrado_arquivar | nao |
| 2026-04-17 | Projeto ERC CATCH recruta investigadores em Humanidades Ambientais | Plataforma 9 | (aguardar_fonte) | 2026-04-25 | encerrado_arquivar | nao |
| 2026-04-30 | Projeto de cooperação europeia "Shared Futures" | DGARTES | (aguardar_fonte) | 2026-04-30 | encerrado_arquivar | nao |
| 2026-04-30 | Programa de Residências Artísticas OASis Lisboa | DGARTES | (aguardar_fonte) | 2026-04-30 | encerrado_arquivar | nao |
| 2026-04-27 | Fundação Gulbenkian abre candidaturas aos Estágios de Verão 2026 | Plataforma 9 | (aguardar_fonte) | 2026-05-03 | encerrado_arquivar | nao |
| 2026-04-14 | OPEN CALL AiR 351 / 2016-2026: UNDER THE LOQUAT TREE | DGARTES | (aguardar_fonte) | 2026-05-03 | encerrado_arquivar | nao |
| 2026-04-29 | Casa Guilherme de Almeida abre inscrições para bolsa de pesquisa sobre acervo | Plataforma 9 | (aguardar_fonte) | 2026-05-06 | encerrado_arquivar | nao |
| 2026-04-23 | Casa Mário de Andrade abre seleção para o Programa de Incentivo à Pesquisa | Plataforma 9 | (aguardar_fonte) | 2026-05-06 | encerrado_arquivar | nao |
| 2026-04-23 | Casa das Rosas abre seleção para a Bolsa Ramos de Azevedo | Plataforma 9 | (aguardar_fonte) | 2026-05-06 | encerrado_arquivar | nao |
| 2026-04-23 | Casa das Rosas abre seleção para a Bolsa Haroldo de Campos | Plataforma 9 | (aguardar_fonte) | 2026-05-06 | encerrado_arquivar | nao |
| 2026-04-23 | Camões – Centro Cultural Português em Maputo abre concurso para Técnico Superior | Plataforma 9 | (aguardar_fonte) | 2026-05-06 | encerrado_arquivar | nao |
| 2026-04-22 | CPLP recruta Diretor/a de Ação Cultural e Língua Portuguesa | Plataforma 9 | (aguardar_fonte) | 2026-05-07 | encerrado_arquivar | nao |
| — | Festival Internacional de Teatro, Arte e Novas Tecnologias [Cagliari, Itália] | DGARTES | (aguardar_fonte) | 2026-05-07 | encerrado_arquivar | nao |
| 2026-04-23 | ARTEMIS: Residências para Jovens Instrumentistas | DGARTES | (aguardar_fonte) | 2026-05-07 | encerrado_arquivar | nao |
| — | EDITAL - CENTENÁRIO DE DARCY PENTEADO | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/7110/ | 2026-05-13 | encerrado_arquivar | depende |
| 2026-04-16 | Chamada Instituto Cultural Vale 2026 | Instituto Cultural Vale | https://institutoculturalvale.org/wp-content/uploads/2026/04/Regulamento-Chamada-Instituto-Cultural-Vale-2026-16-Abr-2026-14h50.pdf | 2026-05-15 | encerrado_arquivar | depende |
| 2026-04-15 | Edital Ações Continuadas — Rio de Janeiro 2026 | Secretaria Municipal de Cultura do Rio de Janeiro | https://cultura.prefeitura.rio/ | 2026-05-18 | encerrado_arquivar | nao |
| 2026-04-17 | Edital SC Cultura Viva 2026 (PNAB) | Fundação Catarinense de Cultura — FCC | https://www.cultura.sc.gov.br/editais-e-acoes/editais | 2026-05-18 | encerrado_arquivar | nao |
| 2026-04-30 | Prêmio Nacional Vozes Periféricas | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8010/ | 2026-05-18 | encerrado_arquivar | depende |
| 2026-04-30 | Bolsa Ofício 2026 — 2º Processo Seletivo (Conservatório de Tatuí) | Conservatório de Tatuí — Sustenidos OS | https://www.conservatoriodetatui.org.br/bolsa-oficio-inscricoes-abertas-2o-processo-seletivo-para-bolsa-oficio/ | 2026-05-20 | encerrado_arquivar | nao |
| 2026-04-20 | Bolsa Cultura Viva — Mestras e Mestres das Culturas Tradicionais (Paraná) | Governo do Estado do Paraná | https://www.parana.pr.gov.br/aen/Noticia/Estado-lanca-edital-de-bolsas-para-mestras-e-mestres-de-culturas-tradicionais-e | 2026-05-22 | encerrado_arquivar | nao |
| — | Elaboração e Gestão de Projetos Culturais | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/7253/ | 2026-05-23 | encerrado_arquivar | depende |
| 2026-05-06 | Nodus 2026: Programa de Residência Artística de Dança Contemporânea | DGARTES | (aguardar_fonte) | 2026-05-25 | encerrado_arquivar | nao |
| 2026-03-15 | Promac 2026 — Programa Municipal de Apoio a Projetos Culturais (SP) | Secretaria Municipal de Cultura — São Paulo | https://prefeitura.sp.gov.br/web/se/w/prefeitura-de-s%C3%A3o-paulo-abre-inscri%C3%A7%C3%B5es-para-edital-do-programa-municipal-de-apoio-a-projetos-culturais-promac-2026 | 2026-05-26 | encerrado_arquivar | nao |
| — | 2 Escuta Zona Oeste | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/6978/ | 2026-05-30 | encerrado_arquivar | depende |
| 2026-04-28 | Projeto FRONTESPO recruta responsável pela recolha e tratamento de corpus | Plataforma 9 | (aguardar_fonte) | 2026-05-31 | encerrado_arquivar | nao |
| — | Pausa Cotidiana - Parque Glória Maria (RJ) | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8122/ | 2026-05-31 | encerrado_arquivar | depende |
| — | Shortway International Short Film Festival | Guia Kinoforum | (aguardar_fonte) | 2026-05-31 | encerrado_arquivar | nao |
| — | 2ª Mapeamento Nacional de Trancistas Negras | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8133/ | 2026-06-01 | encerrado_arquivar | depende |
| — | OFICINA PARA FORMAÇÃO DE PARECERISTAS DE EDITAIS NA ÁREA DA CULTURA | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/9090/ | 2026-06-03 | encerrado_arquivar | depende |
| — | Consulta Pública Preliminar - Edital de Seleção SCDC/MinC/2026 | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8699/ | 2026-06-05 | encerrado_arquivar | depende |
| — | Certificação de Escolas Livres de Formação em Arte e Cultura | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8204/ | 2026-06-08 | encerrado_arquivar | depende |
| 2026-04-25 | Residência Pontos MIS 2026 — Imersão Audiovisual | Museu da Imagem e do Som — MIS-SP | (aguardar_fonte) | 2026-06-10 | encerrado_arquivar | nao |
| — | Festival Itinerância O cinema é Rio - 2º edição | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/9142/ | 2026-06-10 | encerrado_arquivar | depende |
| 2026-05-29 | Universidade Paul-Valéry Montpellier 3 recruta leitor de Português Europeu | Plataforma 9 | (aguardar_fonte) | 2026-06-15 | encerrado_arquivar | nao |
| 2026-06-02 | Bolsa de Investigação para Estudante de Mestrado do CET | Plataforma 9 | (aguardar_fonte) | 2026-06-16 | encerrado_arquivar | nao |
| — | Residência coletiva internacional Low-Tech Projection Lab [França] | DGARTES | (aguardar_fonte) | 2026-06-16 | encerrado_arquivar | nao |
| 2026-06-01 | 1.ª edição do Prêmio de Filosofia do Brasil — Filosofia Maravilhosa | Plataforma 9 | (aguardar_fonte) | 2026-06-21 | encerrado_arquivar | nao |
| 2026-06-03 | Programa de mobilidade CAPES/AUGM 2026 | Plataforma 9 | (aguardar_fonte) | 2026-07-02 | encerrado_arquivar | nao |
| 2026-04-30 | Prémio CEI-IIT-Investigação, Inovação e Território 2026 | Plataforma 9 | (aguardar_fonte) | 2026-07-08 | encerrado_arquivar | nao |
| — | Concurso para seleção de obras para compor o 25º Encontro de Artes Plásticas | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8900/ | 2026-07-13 | encerrado_arquivar | depende |
| — | Chamamento Público 01/26 - PNAB Camaquã - Seleção de Projetos Culturais | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/8879/ | 2026-07-13 | encerrado_arquivar | nao |
| — | Chamamento Público 2/26 Camaquã - Premiação de Pontos e Pontões de Cultura | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/9337/ | 2026-07-13 | encerrado_arquivar | nao |
| 2026-07-07 | Revista internacional Al-Tiba9 lança concurso para Edição 22 | DGARTES | (aguardar_fonte) | 2026-07-15 | encerrado_arquivar | nao |
| — | LUIZ ALVES - PNAB - EDITAL DE CHAMAMENTO PÚBLICO 01/2026 - SEMEC | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/7960/ | 2026-07-15 | encerrado_arquivar | nao |
| 2026-07-16 | Festival of Future Storytellers 2026 — competição internacional | Festival of Future Storytellers | (aguardar_fonte) | 2026-07-20 | encerrado_arquivar | nao |
| 2026-07-03 | SELEÇÃO E HABILITAÇÃO DE GRUPOS DE CAPOEIRA TRADICIONAL MUNICIPAL | MUNICIPIO DE VILA RICA | https://pncp.gov.br/app/editais/03238862000145/2026/62 | 2026-07-20 | encerrado_arquivar | nao |
| 2026-07-08 | Cirkus Kolektiv promove Residência em Circo Contemporâneo | DGARTES | (aguardar_fonte) | 2026-07-20 | encerrado_arquivar | nao |
| — | Intensive Collaborative Residency for Cross-Arts Practice Development | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-21 | encerrado_arquivar | nao |
| 2026-07-06 | Credenciamento para Artistas e Fazedores da Cultura, para o ano de 2026 | MUNICIPIO DE ARARAS | https://pncp.gov.br/app/editais/44215846000114/2026/141 | 2026-07-21 | encerrado_arquivar | nao |
| — | 1º Edital João Celeste Alencar de Fomento à Cultura Vaqueira de Aiuaba | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8116/ | 2026-07-22 | encerrado_arquivar | nao |
| — | Caucasus All Frequency Composer's Workshop | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | nao |
| — | Tushetian Rug Weaving, Wool Processing and Natural Dyeing | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | nao |
| — | Moonlighter Film Camp – Women's Outdoor Filmmaking Intensives | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | nao |
| 2026-07-01 | Projetos inovadores de ópera e dança podem candidatar-se aos Prémios FEDORA | DGARTES | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | nao |
| 2025-07-30 | Contratação de serviços de apresentações musicais, envolvendo artistas | MUNICIPIO DE PARELHAS | https://pncp.gov.br/app/editais/08087561000181/2025/177 | 2026-07-22 | encerrado_arquivar | nao |
| — | Georgian Traditional Polyphonic Singing Workshop at AqTushetii | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-22 | encerrado_arquivar | nao |
| 2026-07-16 | CAIS Fellowships — pesquisa sobre transformação digital (Bochum, Alemanha) | Center for Advanced Internet Studies (CAIS) | https://cais-research.de/en/cais-college/fellowships/ | 2026-07-23 | encerrado_arquivar | nao |
| 2026-07-19 | Prêmio Impactos Positivos 2026 — reconhecimento a negócios e iniciativas | Global Vision Access (GVA) | https://vitrine.impactospositivos.com | 2026-07-24 | encerrado_arquivar | nao |
| 2026-07-19 | Edital Restaura Minas (FEC 07/2026) — R$ 6 milhões para restauro do patrimônio | IEPHA-MG / SECULT-MG | (aguardar_fonte) | 2026-07-24 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO A AÇÕES ARTÍSTICAS E CULTURAIS - POLÍTICA NACIONAL ALDIR BLANC | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8062/ | 2026-07-24 | encerrado_arquivar | nao |
| 2026-06-22 | seleção de pessoas físicas para concessão de prêmios culturais | MUNICIPIO DE AQUIDAUANA | https://pncp.gov.br/app/editais/03452299000103/2026/82 | 2026-07-24 | encerrado_arquivar | nao |
| 2026-06-04 | CONCURSO PARA SELECAO DE DUAS PROPOSTAS DE MONTAGEM TEATRAL | FUNDACAO MUNICIPAL DE CULTURA | https://pncp.gov.br/app/editais/07252975000156/2026/20 | 2026-07-24 | encerrado_arquivar | nao |
| 2026-06-22 | Seleção de até 20 (vinte) artesãos(ãs), pessoas físicas, jurídicas (MEI) | MUNICIPIO DE AQUIDAUANA | https://pncp.gov.br/app/editais/03452299000103/2026/84 | 2026-07-24 | encerrado_arquivar | nao |
| 2026-07-07 | ABERTURA DE CHAMAMENTO PÚBLICO PARA SELEÇÃO E PREMIAÇÃO DE PROPOSTAS | MUNICIPIO DE BENTO GONCALVES | https://pncp.gov.br/app/editais/87849923000109/2026/440 | 2026-07-24 | encerrado_arquivar | nao |
| — | Last Minute Open Call – September 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-24 | encerrado_arquivar | nao |
| 2026-07-19 | Residência Online com Efe Godoy 2026 — Centro Cultural Veras | Centro Cultural Veras | https://rededasartes.cultura.gov.br/oportunidade/9832/ | 2026-07-25 | encerrado_arquivar | nao |
| — | Aviário Studio Furniture Making Residency 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-25 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026-PNAB MARCO - EDITAL PADROEIRA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8093/ | 2026-07-26 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO PARA FOMENTO À PROGRAMAÇÃO DE ESPAÇOS CULTURAIS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8063/ | 2026-07-26 | encerrado_arquivar | nao |
| — | Advent Residencies | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-26 | encerrado_arquivar | nao |
| — | ATHENS AUGUST RESIDENCY & CULTURAL PROGRAM | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-26 | encerrado_arquivar | nao |
| — | Land Art Residency | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-26 | encerrado_arquivar | nao |
| — | Rest in Motion – Embodied Awareness, Somatic Movement | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-26 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 "SIMP... | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8139/ | 2026-07-26 | encerrado_arquivar | nao |
| 2026-07-03 | Prémios da Associação Portuguesa de Museologia | Associação Portuguesa de Museologia (APOM) | https://apom.pt/2026/06/premios-apom-2026-candidaturas-a-decorre/ | 2026-07-27 | encerrado_arquivar | nao |
| 2026-07-06 | Seleção de 6 projetos culturais de agentes residentes | MUNICIPIO DE LAGOA VERMELHA | https://pncp.gov.br/app/editais/87613626000151/2026/286 | 2026-07-27 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO MESTRA DONA BAIA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8064/ | 2026-07-27 | encerrado_arquivar | nao |
| 2025-07-29 | CREDENCIAMENTO DE ARTISTAS, GRUPOS ARTÍSTICOS | MUNICIPIO DE TACAIMBO | https://pncp.gov.br/app/editais/10091601000100/2025/103 | 2026-07-28 | encerrado_arquivar | nao |
| 2025-07-28 | Credenciamento de BANDAS, ARTISTAS MUSICAIS | MUNICIPIO DE BARRA LONGA | https://pncp.gov.br/app/editais/18316182000170/2025/52 | 2026-07-28 | encerrado_arquivar | nao |
| 2026-07-19 | XII Prêmio Hermilo Borba Filho de Literatura | SECULT-PE / CEPE | https://www.mapacultural.pe.gov.br/oportunidade/3284/ | 2026-07-29 | encerrado_arquivar | nao |
| 2026-07-19 | FAPESP PIPE Jornada Tecnológica — até R$ 500 mil | FAPESP | https://fapesp.br/18243/ | 2026-07-29 | encerrado_arquivar | nao |
| — | Microresidencias August 2026 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-29 | encerrado_arquivar | nao |
| — | Audio Recording Engineer: BMiR 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-29 | encerrado_arquivar | nao |
| — | Banff Musicians In Residence 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-29 | encerrado_arquivar | nao |
| 2025-04-28 | Credenciamento de interessados em prestar serviços | MUNICIPIO DE LAJE | https://pncp.gov.br/app/editais/13825492000104/2025/33 | 2026-07-29 | encerrado_arquivar | nao |
| 2025-07-30 | CREDENCIAMENTO DE PROPOSTA ARTISTICA | MUNICIPIO DE MATOZINHOS | https://pncp.gov.br/app/editais/18771238000186/2025/104 | 2026-07-29 | encerrado_arquivar | nao |
| — | Convocatória PRIS - Programa de Residências e Intercâmbio | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/7868/ | 2026-07-29 | encerrado_arquivar | nao |
| — | Silence Awareness Existence – Thematic residency | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-30 | encerrado_arquivar | nao |
| 2026-05-01 | Bolsa de Mobilidade AIL para Jovens Investigadores | Plataforma 9 | (aguardar_fonte) | 2026-07-30 | encerrado_arquivar | nao |
| 2026-07-13 | Rede Municipal de Pontos de Cultura de Goiânia — Política Nacional Cultura Viva | Fundo de Apoio à Cultura — FAC (Goiânia) | https://pncp.gov.br/app/editais/05780030000181/2025/76 | 2026-07-30 | encerrado_arquivar | sim |
| — | EDITAL Nº 001/2026 DE FOMENTO PARA LINGUAGENS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8015/ | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-19 | Bolsa-residência Emsländische Landschaft | Emsländische Landschaft e.V. | https://www.emslaendische-landschaft.de/news/ausschreibung-kunstlerstipendium-der-emslandischen-landschaft-e-v.html | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | Bolsas DAAD — Programa Helmut Schmidt de mestrado | DAAD — Serviço Alemão de Intercâmbio Acadêmico | https://www.daad-brasil.org/pt/2026/05/05/programa-helmut-schmidt-oferece-bolsas-de-pos-graduacao-em-politicas-publicas/ | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | Kometa Fellows — bolsa de €10 mil para jornalismo | Kometa | https://kometarevue.com/page/fellows | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | Les Nuits Magiques — Festival Internacional de Animação | Les Nuits Magiques | https://www.lesnuitsmagiques.fr/inscription.html | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | Cinéopen Festival — competição de curtas de animação | Cinéopen Festival / CCJB Pontarlier | (aguardar_fonte) | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | VIFF — Un Brin de Court: festival de microcurtas | Club Audiovisuel de Vichy | https://www.viff.info/ | 2026-07-31 | encerrado_arquivar | nao |
| — | Funcultura - Edital 01/2026 - Circulação e intercâmbio | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2546/ | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-21 | Prémio Imprensa Nacional / Ferreira de Castro 2026 | Imprensa Nacional-Casa da Moeda (INCM) | https://incm.pt/site/abertas-as-candidaturas-aos-premios-incm-para-a-lingua-portuguesa-2026/ | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-21 | EMS × AdK Residency — música eletroacústica | Elektronmusikstudion (EMS) + Akademie der Künste (AdK) | https://elektronmusikstudion.se/en/aktuellt/call-for-applications-ems-x-adk-residency/ | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-16 | Art & Environment Prize — Lee Ufan Arles + Maison Guerlain | Lee Ufan Arles / Maison Guerlain | https://en.leeufan-arles.org/evenements/art-environment-prize | 2026-07-31 | encerrado_arquivar | nao |
| 2025-04-03 | Contratação de músicos através de credenciamento | MUNICIPIO DE INDAIATUBA | https://pncp.gov.br/app/editais/44733608000109/2025/251 | 2026-07-31 | encerrado_arquivar | nao |
| — | Funded residencies for Artists, writers and researchers (Veneza) | Res Artis (rede de residências) | (aguardar_fonte) | 2026-07-31 | encerrado_arquivar | nao |
| 2026-06-17 | EDITAL 08.FMCB.2026 - MESTRE CANTALÍCIO ROCHA | FUNDACAO MUNICIPAL DE CULTURA DE BOMBINHAS | https://pncp.gov.br/app/editais/09362501000192/2026/24 | 2026-07-31 | encerrado_arquivar | nao |
| — | Territórios da Escrita | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/9276/ | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-13 | Credenciamento de artistas regionais pessoa jurídica | MUNICIPIO DE PORTEIRINHA | https://pncp.gov.br/app/editais/18013326000119/2026/79 | 2026-07-31 | encerrado_arquivar | nao |
| 2026-07-03 | Contratação da prestação de serviços musicais | FUNDO DE APOIO A CULTURA-FAC | https://pncp.gov.br/app/editais/05780030000181/2025/31 | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-13 | EDITAL DE FOMENTO A AÇÕES ARTÍSTICAS E CULTURAIS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8109/ | 2026-07-31 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO ÀS ARTES DE IPAPORANGA - 2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8133/ | 2026-07-31 | encerrado_arquivar | nao |
| — | TED and POSCA Residency | TransArtists / DutchCulture | (aguardar_fonte) | 2026-07-31 | encerrado_arquivar | nao |
| 2026-05-28 | Chamamento Público para o credenciamento de pessoas | MUNICIPIO DE LIVRAMENTO DE NOSSA SENHORA | https://pncp.gov.br/app/editais/13674817000197/2026/72 | 2026-07-31 | encerrado_arquivar | nao |
| — | Seleção Petrobras Cultural 2026 | Petrobras | https://petrobras.com.br/cultural/selecoes-publicas-culturais | 2026-07-31 | encerrado_arquivar | depende |
| 2026-07-19 | Movimentos à Beira — Residência Artística no (en)Veras | Centro Cultural Veras | https://centroculturalveras.org/residencia-artistica-no-en-veras-2026/ | 2026-08-01 | encerrado_arquivar | nao |
| 2026-07-27 | BigCi Environmental Awards 2026 | BigCi — Bilpin international ground for Creative initiatives | https://bigci.org/awards/ | 2026-08-02 | encerrado_arquivar | nao |
| — | CENA OCUPA: Convocatória de Ocupação Artística | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8122/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-21 | Maleta Abierta 2026 — apoio a projetos de arte migrante | IBER-RUTAS / SEGIB | https://segib.org/es/convocatoria-maleta-abierta-2026-para-proyectos-de-arte-migrante-en-iberoamerica/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-16 | BBA 360 Exhibition — competição digital de artes | BBA Gallery | https://bba-prizes.com/360 | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-21 | Fomento CultSP – ProAC nº 01/2026 — Apoio à Produção de Longa-metragem | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/apoio_a_producao_de_longa_metragem_2026/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-21 | Fomento CultSP – ProAC nº 05/2026 — Desenvolvimento de jogos eletrônicos | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/desenvolvimento_ou_finalizacao_e_publicacao_de_jogos_eletronicos_2026/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-19 | Chamada CNPq Universal 2026 — R$ 300 milhões | CNPq / FNDCT | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-06-2026/ChamadaUniversal062026.pdf | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-21 | Fomento CultSP – ProAC nº 09/2026 — Projetos Culturais em municípios de até 50 mil habitantes | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/realizacao_de_projetos_culturais_em_municipios_de_ate_50_mil_habitantes_2026 | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-21 | Fomento CultSP – ProAC nº 08/2026 — Mostras, Festivais e Eventos | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/economia_criativa_fomento_a_mostras_festivais_e_eventos_2026/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-06-10 | Fomento CultSP – ProAC nº 03/2026 — Plano de Trabalho para Cinemas de Rua | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/plano_de_trabalho_para_cinemas_de_rua/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-19 | Edital PNAB PE — R$ 110 mil por projeto para Pontos de Cultura | SECULT-PE | https://www.mapacultural.pe.gov.br/oportunidade/2831/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-07-19 | Desafio Dados e IA para Saúde Mental de Crianças e Adolescentes | Vital Strategies Brasil / Google.org | https://www.vitalstrategies.org/resources/dados-e-ia-para-promocao-da-saude-mental-de-criancas-e-adolescentes/ | 2026-08-03 | encerrado_arquivar | nao |
| 2026-06-10 | Fomento CultSP – ProAC nº 04/2026 — Adaptação de obra literária para roteiro | Secretaria da Cultura, Economia e Indústria Criativas de São Paulo | https://www.cultura.sp.gov.br/sec_cultura/Arquivo_de_Editais/Editais_Fomento_Cultsp/Fomento_CultSP_2026/adaptacao_de_obra_literaria_para_roteiro_cinematografico_2026/ | 2026-08-03 | encerrado_arquivar | nao |
| 2025-08-01 | CREDENCIAMENTO DE INTERESSADOS (PESSOA FÍSICA OU JURÍDICA) | MUNICIPIO DE BELO JARDIM | https://pncp.gov.br/app/editais/10260222000105/2026/1 | 2026-08-04 | encerrado_arquivar | nao |
| 2026-07-21 | Prêmio Mário de Andrade de Fotografias Etnográficas 2026 | Iphan / Centro Nacional de Folclore e Cultura Popular (CNFCP) | https://www.gov.br/iphan/pt-br/unidades-especiais/centro-nacional-de-folclore-e-cultura-popular/noticias-1/cnfcp-lanca-edital-do-premio-mario-de-andrade-de-fotografias-etnograficas-2026 | 2026-08-04 | encerrado_arquivar | nao |
| 2026-07-19 | Edital FAPES 18/2026 — R$ 9,8 milhões para parcerias entre startups | FAPES | https://fapes.es.gov.br/Media/fapes/Editais/EDITAL_FAPES_18-2026_-_PARCERIAS_ENTRE_STARTUPS%20(1).pdf | 2026-08-04 | encerrado_arquivar | nao |
| 2025-08-04 | CREDENCIAMENTO DE INTERESSADOS (PESSOA FÍSICA OU JURÍDICA) | MUNICIPIO DE BELO JARDIM | https://pncp.gov.br/app/editais/10260222000105/2025/283 | 2026-08-04 | encerrado_arquivar | nao |
| 2026-07-15 | 3º Prêmio Pernambuco de Artesanato | Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | https://www.mapacultural.pe.gov.br/oportunidade/3278/ | 2026-08-05 | encerrado_arquivar | nao |
| 2026-07-15 | 3º Prêmio Euclides da Fonseca de Ópera | Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | https://www.mapacultural.pe.gov.br/oportunidade/3276/ | 2026-08-05 | encerrado_arquivar | nao |
| 2026-07-15 | 3º Prêmio Trajetórias em Dança Mestra Nice Teles | Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | https://www.mapacultural.pe.gov.br/oportunidade/3287/ | 2026-08-05 | encerrado_arquivar | nao |
| 2026-07-15 | 3ª edição do Prêmio Bastidores em Cena | Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | https://www.mapacultural.pe.gov.br/oportunidade/3289/ | 2026-08-05 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 - SELEÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8175/ | 2026-08-06 | encerrado_arquivar | nao |
| — | Edital n° 17/2026 - Apoio a Ações Continuadas | Mapa Cultural | https://mapacultural.se.gov.br/oportunidade/46/ | 2026-08-06 | encerrado_arquivar | nao |
| — | CHAMADA DE PROGRAMAÇÃO ARTÍSTICAS DE DIFUSÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8084/ | 2026-08-06 | encerrado_arquivar | nao |
| — | PNAB n° 18/2026 - Subsídio para Manutenção de Espaços | Mapa Cultural | https://mapacultural.se.gov.br/oportunidade/49/ | 2026-08-06 | encerrado_arquivar | nao |
| 2026-07-03 | Chamamento Público destinado a selecionar Organizações | MUNICIPIO DE CROATA | https://pncp.gov.br/app/editais/10462349000107/2026/35 | 2026-08-06 | encerrado_arquivar | nao |
| 2026-07-08 | 15º Festival Internacional Sesc de Música: bolsas | Sesc/RS — Serviço Social do Comércio do Rio Grande do Sul | https://www.sesc-rs.com.br/festival/alunos/ | 2026-08-06 | encerrado_arquivar | nao |
| — | EDITAL DE PREMIAÇÃO DE PONTOS E PONTÕES DE CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/7718/ | 2026-08-07 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/7731/ | 2026-08-07 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO A PROJETOS CONTINUADOS DE PONTOS DE CULTURA (2) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/7620/ | 2026-08-07 | encerrado_arquivar | nao |
| — | Edital 012/2026 - Economia Criativa - PNAB Pacajus | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8192/ | 2026-08-07 | encerrado_arquivar | nao |
| — | EDITAL DE SELEÇÃO PÚBLICA Nº 005/2026 – PROJETOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8195/ | 2026-08-07 | encerrado_arquivar | nao |
| 2026-07-10 | Credenciamento de pessoas físicas ou jurídicas | MUNICIPIO DE CARMO DO PARANAIBA | https://pncp.gov.br/app/editais/18602029000109/2026/45 | 2026-08-07 | encerrado_arquivar | nao |
| 2026-07-21 | Prague City of Literature — Creative Residency 2027 | Prague City of Literature / Municipal Library of Prague | https://www.prahamestoliteratury.cz/2027-prague-creative-residency/ | 2026-08-07 | encerrado_arquivar | nao |
| 2025-08-06 | CREDENCIAMENTO de Microempreendedor Individual | MUNICIPIO DE TAQUARITINGA DO NORTE | https://pncp.gov.br/app/editais/10091593000100/2025/64 | 2026-08-07 | encerrado_arquivar | nao |
| — | SECULTFOR - EDITAL DE SELEÇÃO DE ARTISTAS/GRUPOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8159/ | 2026-08-07 | encerrado_arquivar | nao |
| — | Art, Nature and Community — All in One Week | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-08 | encerrado_arquivar | nao |
| — | From Canvas to Wall: Create Your First Mural in Portugal | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-08 | encerrado_arquivar | nao |
| 2025-08-08 | Credenciamento para a contratação de artistas regionais | MUNICIPIO DE CONCEICAO DE IPANEMA | https://pncp.gov.br/app/editais/18334300000172/2025/56 | 2026-08-08 | encerrado_arquivar | nao |
| 2026-07-21 | Confluence of Myths Residency 2026 — Goethe-Institut | Goethe-Institut Vietnam | https://www.goethe.de/ins/vn/en/kul/aus/tvr.html | 2026-08-09 | encerrado_arquivar | nao |
| 2026-07-24 | Credenciamento de artistas, grupos, coletivos, produtores | CONSORCIO INTERMUNICIPAL GRANDE ABC | https://pncp.gov.br/app/editais/58151580000106/2026/35 | 2026-08-10 | encerrado_arquivar | nao |
| 2026-07-23 | EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 PRÊMIO | Mapa Cultural | https://mapacultural.pe.gov.br/oportunidade/3314/ | 2026-08-10 | encerrado_arquivar | nao |
| 2026-07-17 | Edital BH nas Telas 2026 (Belo Horizonte) | Prefeitura de Belo Horizonte — Secretaria Municipal de Cultura / Fundo Municipal de Cultura (LMIC) | https://prefeitura.pbh.gov.br/cultura/edital-bh-nas-telas-2026 | 2026-08-10 | encerrado_arquivar | nao |
| 2026-07-29 | MICSUL 2026: MinC seleciona 65 empreendedores culturais | Ministério da Cultura (MinC) — Economia Criativa | https://mapa.cultura.gov.br/oportunidade/9881/ | 2026-08-12 | encerrado_arquivar | depende |
| — | Audio Recording Engineer: Indigenous Music 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-12 | encerrado_arquivar | nao |
| 2026-07-14 | PNAB Pernambuco — Premiação aos Pontos e Pontões de Cultura | Secretaria de Cultura do Estado de Pernambuco (SECULT-PE) | https://www.mapacultural.pe.gov.br/oportunidade/3263/ | 2026-08-12 | encerrado_arquivar | nao |
| 2026-07-21 | TaDA — Textile and Design Alliance, Residência 2027 | TaDA – Textile and Design Alliance | https://tada-residency.ch/en/residence | 2026-08-12 | encerrado_arquivar | nao |
| 2026-07-21 | K3 Tanzplan Hamburg — Residência para Coreógrafos | K3 – Zentrum für Choreographie / Tanzplan Hamburg | https://www.k3-hamburg.de/en/residency/application/ | 2026-08-12 | encerrado_arquivar | nao |
| 2026-07-21 | DOK Short n' Sweet — pitch de curtas no DOK Leipzig | DOK Leipzig | https://www.dok-leipzig.de/en/ | 2026-08-12 | encerrado_arquivar | nao |
| 2026-06-29 | BNDES — Edital de Cinema 2026 (Seleção Pública de Patrocínio Cultural 01/2026) | BNDES | https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios/selecao-publica-patrocinio-cultural-01-2026 | 2026-08-13 | encerrado_arquivar | depende |
| — | EDITAL 002/2026 - II FESTIVAL DAS ARTES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8136/ | 2026-08-13 | encerrado_arquivar | nao |
| — | Programa Rouanet Centro-Oeste | Ministério da Cultura | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-centro-oeste/programa-rouanet-centro-oeste | 2026-08-13 | encerrado_arquivar | sim |
| 2026-06-15 | 5º Concurso de Fotografias do CAU/RS 2026 | Conselho de Arquitetura e Urbanismo do Rio Grande do Sul (CAU/RS) | https://transparencia.caurs.gov.br/chamada-publica-005-2026/ | 2026-08-14 | encerrado_arquivar | nao |
| — | Call for Artists & Writers: Open Residency Fall 2026 (San Miguel de Allende) | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-14 | encerrado_arquivar | nao |
| — | Residency Available – SEPTEMBER 2026 – Colombia | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-14 | encerrado_arquivar | nao |
| 2026-07-21 | HKBU International Writers' Workshop 2027 | Hong Kong Baptist University (IWW) | https://iww.hkbu.edu.hk/ | 2026-08-14 | encerrado_arquivar | nao |
| 2026-07-15 | Edital Maximiano da Mata Teixeira — Aquisição | Secretaria de Estado da Cultura do Tocantins (Secult-TO) / Fundo Estadual de Cultura | https://www.to.gov.br/secult/editais-fundo-cultural/30k0lktxt9lk | 2026-08-15 | encerrado_arquivar | nao |
| — | International Contemporary Dance Residency (Skopje) | TransArtists / DutchCulture | (aguardar_fonte) | 2026-08-15 | encerrado_arquivar | nao |
| — | Residency for Glassmakers and Artists | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-15 | encerrado_arquivar | nao |
| 2026-07-21 | Global Gastronomy Museum — "Foodstay" Artist Residency | Global Gastronomy Museum | https://www.global-gastronomy.com/foodstay-en.html | 2026-08-15 | encerrado_arquivar | nao |
| 2026-07-29 | Ocupa LabMultipalco: nove residências | Sedac-RS / Ieacen / Fundação Theatro São Pedro | https://cultura.rs.gov.br/edital-ocupa-labmultipalco-esta-com-inscricoes-abertas-ate-15-de-agosto | 2026-08-15 | encerrado_arquivar | nao |
| 2026-08-05 | Companhias de teatro são convidadas a participar | DGARTES | (aguardar_fonte) | 2026-08-15 | encerrado_arquivar | nao |
| 2026-06-12 | Fundo de Fomento Cultural (Portugal) — Projetos de cruzamento entre cultura e tecnologia | Fundo de Fomento Cultural / GEPAC — Ministério da Cultura de Portugal | https://culturaportugal.gov.pt/pt/saber/2026/06/candidaturas-ao-programa-de-apoio-a-projetos-de-cruzamento-entre-cultura-e-tecnologia/ | 2026-08-15 | encerrado_arquivar | nao |
| — | SELEÇÃO DE PROJETOS CULTURAIS PARA RECEBER APOIO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8085/ | 2026-08-16 | encerrado_arquivar | nao |
| 2026-07-09 | Cité internationale des arts × AFOC | Cité internationale des arts | https://www.citeinternationaledesarts.fr/appels-a-candidature/association-francoise-pour-loeuvre-contemporaine-x-cite-internationale-des-arts/ | 2026-08-16 | encerrado_arquivar | nao |
| 2026-08-03 | Residência de pesquisa e criação no cruzamento | DGARTES | (aguardar_fonte) | 2026-08-16 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8172/ | 2026-08-17 | encerrado_arquivar | nao |
| 2026-06-23 | Edital Sesc Artes da Cena 04/26 | Sesc Paraná | https://www.sescpr.com.br/edital/edital-sesc-artes-da-cena/ | 2026-08-17 | encerrado_arquivar | nao |
| 2026-06-18 | Seleção de 07 projetos de Pontos de Cultura | MUNICIPIO DE RIBEIRAO DAS NEVES | https://pncp.gov.br/app/editais/18314609000109/2026/43 | 2026-08-17 | encerrado_arquivar | nao |
| 2026-07-17 | Edital LMIC Multilinguagens 2026 (Belo Horizonte) | Prefeitura de Belo Horizonte — Secretaria Municipal de Cultura / Fundo Municipal de Cultura (LMIC) | https://prefeitura.pbh.gov.br/cultura/edital-multilinguagens-2026 | 2026-08-17 | encerrado_arquivar | nao |
| 2026-07-17 | Fundação Cultural de Curitiba — Edital Lei de Incentivo | Fundação Cultural de Curitiba (FCC) / Prefeitura de Curitiba | http://www.fundacaoculturaldecuritiba.com.br/leideincentivo/avisos/ | 2026-08-17 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 007/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8178/ | 2026-08-17 | encerrado_arquivar | nao |
| 2026-07-31 | SELEÇÃO DE PROJETOS PARA FIRMAR TERMO DE EXECUÇÃO CULTURAL | MUNICIPIO DE CAPAO DA CANOA | https://pncp.gov.br/app/editais/90836693000140/2026/650 | 2026-08-18 | encerrado_arquivar | nao |
| 2025-08-18 | CREDENCIAMENTO DE PESSOAS FÍSICA OU JURÍDICA | MUNICIPIO DE VERDELANDIA | https://pncp.gov.br/app/editais/01612505000170/2025/76 | 2026-08-18 | encerrado_arquivar | nao |
| 2026-08-03 | CREDENCIAMENTO DE ARTISTAS DA ÁREA DE ENTRETENIMENTO | MUNICIPIO DE UNIAO | https://pncp.gov.br/app/editais/06553606000130/2026/112 | 2026-08-18 | encerrado_arquivar | nao |
| — | Residency at Casa Figueira 2026 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-18 | encerrado_arquivar | nao |
| 2026-07-15 | Credenciamento de pessoas jurídicas residentes | MUNICIPIO DE VIANA | https://pncp.gov.br/app/editais/27165547000101/2026/42 | 2026-08-18 | encerrado_arquivar | nao |
| — | 5th Edition Micro-Residency A Isla R.A.R.O. Bogotá | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-18 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO 011/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8146/ | 2026-08-18 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 01/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8196/ | 2026-08-18 | encerrado_arquivar | nao |
| 2026-06-29 | Seleção de projetos culturais para receber apoio | MUNICIPIO DE GUAIRA | https://pncp.gov.br/app/editais/77857183000190/2026/204 | 2026-08-18 | encerrado_arquivar | nao |
| 2026-08-04 | CADASTRO E EXPORTAÇÃO DE INFORMAÇÕES | MUNICIPIO DE CAMPOS DO JORDAO | https://pncp.gov.br/app/editais/45699626000176/2026/370 | 2026-08-19 | encerrado_arquivar | nao |
| — | SECRETARIA DE CULTURA DE SÃO JOÃO DO JAGUARIBE | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8199/ | 2026-08-19 | encerrado_arquivar | nao |
| 2026-08-05 | SELEÇÃO DE PROJETOS ARTÍSTICO CULTURAIS | MUNICIPIO DE VILA RICA | https://pncp.gov.br/app/editais/03238862000145/2026/66 | 2026-08-19 | encerrado_arquivar | nao |
| — | WILD techniques – Intensive Dance Training Program | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-20 | encerrado_arquivar | nao |
| 2026-07-31 | CHAMAMENTO PÚBLICO 006/2026 PARA SELEÇÃO | MUNICIPIO DE VERA CRUZ | https://pncp.gov.br/app/editais/98661366000106/2026/417 | 2026-08-21 | encerrado_arquivar | nao |
| 2026-07-07 | Festival Sesc de Música 2026 | Sesc RN | https://sescrn.com.br/festival-sesc-de-musica-entra-na-fase-final-de-inscricoes/ | 2026-08-23 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 02/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8173/ | 2026-08-23 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8144/ | 2026-08-24 | encerrado_arquivar | nao |
| 2026-08-05 | EDITAL DE CHAMAMENTO PÚBLICO Nº 01/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8201/ | 2026-08-24 | encerrado_arquivar | nao |
| 2026-07-08 | Celebração de parceria com Organização da Sociedade Civil | MUNICIPIO DE MACAE | https://pncp.gov.br/app/editais/29115474000160/2026/407 | 2026-08-24 | encerrado_arquivar | nao |
| — | Vancouver Island Plein Air Workshop | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-25 | encerrado_arquivar | nao |
| 2026-07-16 | Amnesty International — Au Cinéma pour les Droits Humains | Amnesty International France | (aguardar_fonte) | 2026-08-25 | encerrado_arquivar | nao |
| 2026-07-23 | Seleção de projetos culturais de proponentes | MUNICIPIO DE OLINDA | https://pncp.gov.br/app/editais/10404184000109/2026/492 | 2026-08-26 | encerrado_arquivar | nao |
| 2026-07-23 | Premiação de 14 iniciativas | MUNICIPIO DE OLINDA | https://pncp.gov.br/app/editais/10404184000109/2026/494 | 2026-08-26 | encerrado_arquivar | nao |
| — | EDITAL AGENTES TERRITORIAIS DE CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8231/ | 2026-08-26 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8153/ | 2026-08-26 | encerrado_arquivar | nao |
| 2026-07-23 | Premiação de agentes culturais | MUNICIPIO DE OLINDA | https://pncp.gov.br/app/editais/10404184000109/2026/491 | 2026-08-26 | encerrado_arquivar | nao |
| 2026-08-13 | CREDENCIAMENTO de interessados para apresentações | MUNICIPIO DE ABREU E LIMA | https://pncp.gov.br/app/editais/08637373000180/2026/252 | 2026-08-27 | encerrado_arquivar | nao |
| — | Edital de Chamamento Público nº 004/2026 – Subsídio | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8176/ | 2026-08-27 | encerrado_arquivar | nao |
| — | VIANA/ES - EDITAL 001/2026 - PNAB SELEÇÃO DE PROJETOS | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2370/ | 2026-08-28 | encerrado_arquivar | nao |
| — | VIANA/ES - EDITAL 005/2026 - PNAB/PNCV PREMIAÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2478/ | 2026-08-28 | encerrado_arquivar | nao |
| — | Sacatar 2027-28 Open Call | TransArtists / DutchCulture | (aguardar_fonte) | 2026-08-28 | encerrado_arquivar | nao |
| — | Residency Available – NOVEMBER 2026 – Colombia | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-28 | encerrado_arquivar | nao |
| 2026-08-27 | SELEÇÃO DE PROJETOS PARA FIRMAR TERMO DE EXECUÇÃO CULTURAL | MUNICIPIO DE BELTERRA | https://pncp.gov.br/app/editais/01614112000103/2026/45 | 2026-08-28 | encerrado_arquivar | nao |
| 2026-07-27 | Prêmio Iecine de Suporte por Desempenho Artístico | Secretaria da Cultura do Estado do Rio Grande do Sul | https://www.procultura.rs.gov.br/index.php?menu=facinf | 2026-08-28 | encerrado_arquivar | nao |
| 2026-07-23 | Seleção de projetos de Pontos de Cultura | MUNICIPIO DE OLINDA | https://pncp.gov.br/app/editais/10404184000109/2026/493 | 2026-08-28 | encerrado_arquivar | nao |
| — | VIANA/ES - EDITAL 002/2026 - PNAB AQUISIÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2452/ | 2026-08-28 | encerrado_arquivar | nao |
| — | VIANA/ES - EDITAL 004/2026 - PNAB SELEÇÃO DE ESPAÇOS | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2460/ | 2026-08-28 | encerrado_arquivar | nao |
| 2026-07-14 | Edital Sedac 24/2026 — Artista na Escola em Tempo Integral | Secretaria de Estado da Cultura do Rio Grande do Sul | https://cultura.rs.gov.br/edital-para-projetos-culturais-em-escolas-de-tempo-integral-esta-com-inscricoes-abertas | 2026-08-28 | encerrado_arquivar | nao |
| — | VIANA/ES - EDITAL 003/2026 - PNAB CIRCULAÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2457/ | 2026-08-28 | encerrado_arquivar | nao |
| 2025-09-16 | Credenciamento para eventual contratação de serviços | FUNDACAO CULTURAL CARLOS DRUMMOND DE ANDRADE | https://pncp.gov.br/app/editais/21611579000107/2025/44 | 2026-08-29 | encerrado_arquivar | nao |
| 2026-06-22 | Execução de ações culturais (apoio direto a projetos) — seleção para Termo de Execução Cultural PNAB | Município de Davinópolis | https://pncp.gov.br/app/editais/01130277000100/2026/72 | 2026-08-29 | encerrado_arquivar | depende |
| 2026-06-30 | Residências Cruzadas Museu da Língua Portuguesa e Cité | Museu da Língua Portuguesa (IDBrasil Cultura, Educação e Esporte) | https://www.idbr.org.br/edital-do-programa-de-residencias-cruzadas-linguas-e-conhecimentos-indigenas-alem-das-fronteiras/ | 2026-08-30 | encerrado_arquivar | nao |
| — | Last minute spots September 16 - October 30: Vancouver Island | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-30 | encerrado_arquivar | nao |
| 2026-06-25 | Mostra Nacional Jovens Criadores 2026 (IPDJ/Gerador) | IPDJ — Instituto Português do Desporto e Juventude | https://ipdj.gov.pt/noticias/mostra-nacional-jovens-criadores-2026-candidaturas-abertas | 2026-08-30 | encerrado_arquivar | nao |
| 2026-07-21 | Programa de residência BRIDGES | DGARTES | (aguardar_fonte) | 2026-08-30 | encerrado_arquivar | nao |
| — | Pottery Farm Residency | Res Artis (rede de residências) | (aguardar_fonte) | 2026-08-30 | encerrado_arquivar | nao |
| 2026-06-03 | 2ª Bienal MoAC Biss 2027 (Guiné-Bissau) — Chamada | Fundação Bienal MoAC Biss | (aguardar_fonte) | 2026-08-30 | encerrado_arquivar | nao |
| 2026-07-16 | Rostocker Kunstpreis 2026 | Kunsthalle Rostock / Kulturstiftung Rostock | https://www.kunsthallerostock.de/de/aktuelles/news/ausschreibung-rostocker-kunstpreis-2026 | 2026-08-31 | encerrado_arquivar | nao |
| 2026-07-16 | Otte 1 — residência artística de 4 meses com bolsa | Künstlerhaus Otte 1 | https://www.otte1.org/de/bewerbung/ | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-19 | Credenciamento de atividades, artistas, grupos e coletivos | MUNICIPIO DE BALNEARIO ARROIO DO SILVA | https://pncp.gov.br/app/editais/01605479000152/2026/78 | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-10 | Premiação dos Agentes Culturais Balsenses – Mestres | MUNICIPIO DE BALSAS | https://pncp.gov.br/app/editais/06441430000125/2026/104 | 2026-08-31 | encerrado_arquivar | nao |
| 2026-07-21 | Fondation Jan Michalski — Residência para Escritores | Fondation Jan Michalski pour l'écriture et la littérature | https://fondation-janmichalski.com/en/residences | 2026-08-31 | encerrado_arquivar | nao |
| — | EDITAL DE CREDENCIAMENTO CIRCULA CANINDÉ - 06/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8222/ | 2026-08-31 | encerrado_arquivar | nao |
| 2026-07-16 | Coreógrafos em meio de carreira podem candidatar-se | DGARTES | (aguardar_fonte) | 2026-08-31 | encerrado_arquivar | nao |
| 2026-03-23 | LIC-DF 2026: R$ 16,27 milhões em incentivo fiscal | Secretaria de Estado de Cultura e Economia Criativa do DF | https://sufic.cultura.df.gov.br/como-inscrever-seu-projeto-2 | 2026-08-31 | encerrado_arquivar | nao |
| 2026-07-19 | Residência Artística FAAP | FAAP — Fundação Armando Alvares Penteado | https://www.faap.br/residencia-artistica/ | 2026-08-31 | encerrado_arquivar | nao |
| 2026-08-10 | Continuidade da prestação de serviços por meio do credenciamento | MINISTERIO DA CULTURA | https://pncp.gov.br/app/editais/01264142000129/2027/1 | 2026-08-31 | encerrado_arquivar | depende |
| — | SÍM Residency 2027 | TransArtists / DutchCulture | (aguardar_fonte) | 2026-08-31 | encerrado_arquivar | nao |
| — | Funcultura - Edital 01/2026 - Circulação e intercâmbio (2) | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2564/ | 2026-08-31 | encerrado_arquivar | nao |
| — | SELEÇÃO DE PARECERISTAS PARA AVALIAÇÃO DO MÉRITO CULTURAL | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8220/ | 2026-08-31 | encerrado_arquivar | nao |
| 2026-07-16 | Duisburg — bolsa-residência de 1 ano | Kulturbüro der Stadt Duisburg | https://www.duisburg.de/microsites/kulturbuero-duisburg/foerderung/ausschreibung-aufenthaltsstipendium | 2026-08-31 | encerrado_arquivar | nao |
| 2025-08-29 | CREDENCIAMENTO DE ARTISTAS NAS CATEGORIAS DE CANTOR | MUNICIPIO DE TEIXEIRAS | https://pncp.gov.br/app/editais/18134056000102/2025/67 | 2026-09-01 | encerrado_arquivar | nao |
| — | Le Garage Moderne Residencies | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-01 | encerrado_arquivar | nao |
| — | EDITAL Nº 011/2026 - REDE MUNICIPAL DE PONTOS E PONTÕES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8218/ | 2026-09-01 | encerrado_arquivar | nao |
| 2025-10-07 | Chamamento Público para fins de credenciamento de artistas | MUNICIPIO DE EUCLIDES DA CUNHA | https://pncp.gov.br/app/editais/13698774000180/2025/158 | 2026-09-01 | encerrado_arquivar | nao |
| 2026-07-10 | Bolsa de Trabalho para Artistas Visuais de Berlim 2027 | Senatsverwaltung für Kultur und Gesellschaftlichen Zusammenhalt | https://www.berlin.de/sen/kultgz/aktuelles/pressemitteilungen/2026/pressemitteilung.1690417.php | 2026-09-02 | encerrado_arquivar | nao |
| — | EDITAL CHAMAMENTO PÚBLICO 007/2026 FOMENTO A PROJETOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8253/ | 2026-09-02 | encerrado_arquivar | nao |
| — | Chamamento público para concessão de bolsas Cultura Viva | MUNICIPIO DE GRAVATAI | https://pncp.gov.br/app/editais/87890992000158/2026/910 | 2026-09-03 | encerrado_arquivar | nao |
| 2026-08-03 | Credenciamento de Artistas, Grupos e Profissionais da Cultura | MUNICIPIO DE ARAPIRACA | https://pncp.gov.br/app/editais/12198693000158/2026/182 | 2026-09-03 | encerrado_arquivar | nao |
| 2026-08-03 | Chamamento Público 01/2026 - ARTE E CULTURA NA EDUCAÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2566/ | 2026-09-03 | encerrado_arquivar | nao |
| 2026-08-17 | Chamamento público para Premiações por Trajetória | MUNICIPIO DE GRAVATAI | https://pncp.gov.br/app/editais/87890992000158/2026/911 | 2026-09-03 | encerrado_arquivar | nao |
| 2026-07-24 | Premiação de 14 iniciativas | MUNICIPIO DE DIAS D'AVILA | https://pncp.gov.br/app/editais/13394044000195/2026/73 | 2026-09-04 | encerrado_arquivar | nao |
| — | EDITAL Nº 003/2026 – PNAB AMONTADA – APOIO A GRUPOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8291/ | 2026-09-04 | encerrado_arquivar | nao |
| — | EDITAL 009 - CULTURA INFANCIA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8282/ | 2026-09-04 | encerrado_arquivar | nao |
| 2026-07-21 | Prêmio Elisabete Anderle de Estímulo à Cultura 2026 | Fundação Catarinense de Cultura (FCC) | https://www.cultura.sc.gov.br/editais-e-acoes/editais/26552-edital-premio-elisabete-anderle-de-estimulo-a-cultura-2026 | 2026-09-04 | encerrado_arquivar | nao |
| — | EDITAL PRÊMIO CULTURA VIVA CANINDÉ - 07/2026 - PNAB | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8223/ | 2026-09-04 | encerrado_arquivar | nao |
| — | Culinary residency at DAS MINSK Kunsthaus | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-05 | encerrado_arquivar | nao |
| 2026-07-28 | Teatro IDRA convida artistas, coletivos e companhias | DGARTES | (aguardar_fonte) | 2026-09-05 | encerrado_arquivar | nao |
| — | International Granada Writers in Residence Programme | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-06 | encerrado_arquivar | nao |
| — | "Ecosystems as Living Communities" vol. III UniCredit | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-06 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO DE OSCs PARA ELABORAÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8065/ | 2026-09-06 | encerrado_arquivar | nao |
| 2026-07-15 | Prêmio Adriano Moreira — Academia Internacional da Cultura Portuguesa | Plataforma 9 | (aguardar_fonte) | 2026-09-06 | encerrado_arquivar | nao |
| 2026-07-16 | Facteur de Ciel — residências de escrita e criação | Facteur de Ciel | https://www.facteurdeciel.com/les-r%C3%A9sidences | 2026-09-06 | encerrado_arquivar | nao |
| — | EDITAL DE FORMAÇÃO E CREDENCIAMENTO DOS CICLOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8123/ | 2026-09-07 | encerrado_arquivar | nao |
| 2025-09-08 | CREDENCIAMENTO PARA CONTRATAÇÃO DE ARTISTAS LOCAIS | MUNICIPIO DE ABRE CAMPO | https://pncp.gov.br/app/editais/18837278000183/2025/40 | 2026-09-07 | encerrado_arquivar | nao |
| 2025-08-11 | CREDENCIAMENTO ELETRÔNICO PARA RECEBER PROPOSTAS | MUNICIPIO DE ARCEBURGO | https://pncp.gov.br/app/editais/17899717000110/2025/74 | 2026-09-07 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 002/2026-PNAB | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8167/ | 2026-09-07 | encerrado_arquivar | nao |
| — | ON::View Artist Residency Program | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-07 | encerrado_arquivar | nao |
| 2026-09-04 | Termo de Referência — fundo/ação cultural | BOM JESUS DO ITABAPOANA PREFEITURA | https://pncp.gov.br/app/editais/29112760000172/2026/251 | 2026-09-08 | encerrado_arquivar | nao |
| 2026-08-17 | Credenciamento de artistas e cantores locais | MUNICIPIO DE ASSIS CHATEAUBRIAND | https://pncp.gov.br/app/editais/76208479000118/2026/157 | 2026-09-08 | encerrado_arquivar | nao |
| — | Convocatória para as Artes Cênicas - Teatro Carlos Câmara | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8216/ | 2026-09-08 | encerrado_arquivar | nao |
| 2026-07-20 | Edital de Aquisição de Livros 2026 — FCC (Prosas) | Fundação Catarinense de Cultura (FCC) / Governo de Santa Catarina | https://prosas.com.br/editais/18428-edital-de-concurso-no-65-2026-aquisicao-de-livros | 2026-09-08 | encerrado_arquivar | nao |
| 2025-08-26 | CREDENCIAMENTO de artistas e bandas da terra | MUNICIPIO DE FRAIBURGO | https://pncp.gov.br/app/editais/82947979000174/2025/222 | 2026-09-08 | encerrado_arquivar | nao |
| 2026-08-19 | Credenciamento de pessoas jurídicas capacitadas | MUNICIPIO DE NEPOMUCENO | https://pncp.gov.br/app/editais/18244350000169/2026/73 | 2026-09-09 | encerrado_arquivar | nao |
| — | 2ª EDIÇÃO EDITAL DONA SANTA DE FOMENTO A PROJETOS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8269/ | 2026-09-09 | encerrado_arquivar | nao |
| — | EDITAL GRUPOS CICLO CEARÁ NATALINO - 2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8181/ | 2026-09-09 | encerrado_arquivar | nao |
| — | EDITAL PARA MOSTRAS DO CICLO CEARÁ NATALINO - 2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8182/ | 2026-09-09 | encerrado_arquivar | nao |
| 2026-07-27 | Chamamento Público para seleção de projetos culturais | MUNICIPIO DE DOIS IRMAOS | https://pncp.gov.br/app/editais/88254891000153/2026/207 | 2026-09-09 | encerrado_arquivar | nao |
| — | II EDITAL DE FOMENTO ÀS ARTES LUZANITE CUNHA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8232/ | 2026-09-10 | encerrado_arquivar | nao |
| 2026-07-16 | Accueils Studio — residência de criação em dança | Centre Chorégraphique National de Caen en Normandie | https://ccncn.eu/artistes-accompagnes/accueils-studio/ | 2026-09-10 | encerrado_arquivar | nao |
| — | EDITAL CICLO CEARÁ CARNAVALESCO - 2027 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8183/ | 2026-09-10 | encerrado_arquivar | nao |
| 2026-08-14 | CREDENCIAMENTO DE INSTRUTORES E OFICINEIROS | MUNICIPIO DE BOM JESUS DO NORTE | https://pncp.gov.br/app/editais/27167360000139/2026/32 | 2026-09-10 | encerrado_arquivar | nao |
| 2026-07-23 | MacDowell Fellowship — residência artística multidisciplinar | MacDowell | https://www.macdowell.org/apply/apply-for-fellowship | 2026-09-10 | encerrado_arquivar | nao |
| — | Copa Aéreo Dance Brasil 2026 | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/7130/ | 2026-09-10 | encerrado_arquivar | depende |
| 2025-09-10 | CREDENCIAMENTO VIA CHAMAMENTO PÚBLICO PARA CONTRATAÇÃO | MUNICIPIO DE SAO BENTO DO SUL | https://pncp.gov.br/app/editais/86051398000100/2025/170 | 2026-09-10 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 009/2026 - SEMCULT | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2575/ | 2026-09-11 | encerrado_arquivar | nao |
| 2026-09-05 | EDITAL DE AGENTES TERRITORIAIS CULTURAIS DE FORTALEZA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8228/ | 2026-09-11 | encerrado_arquivar | nao |
| 2025-09-11 | Credenciamento de bandas acima de 03 integrantes | MUNICIPIO DE SANTO ANTONIO DE JESUS | https://pncp.gov.br/app/editais/13825476000103/2025/96 | 2026-09-11 | encerrado_arquivar | nao |
| 2026-06-01 | PREMIAÇÃO AOS CANDIDATOS CLASSIFICADOS NO CONCURSO | MUNICIPIO DE PALOTINA | https://pncp.gov.br/app/editais/76208487000164/2026/164 | 2026-09-11 | encerrado_arquivar | nao |
| 2026-09-02 | Seleção de projetos culturais para receberem apoio | MUNICIPIO DE SAO MIGUEL DAS MATAS | https://pncp.gov.br/app/editais/13825500000104/2026/119 | 2026-09-11 | encerrado_arquivar | nao |
| — | Mountain Hut in Greece | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-11 | encerrado_arquivar | nao |
| — | Residency Available – OCTOBER 2026 – Colombia | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-12 | encerrado_arquivar | nao |
| — | Residency for performing arts professionals from Ukraine, Moldova and Sakartvelo | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-12 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 02/2026 SELEÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8337/ | 2026-09-12 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 05/2026 – ALDIR BLANC | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8260/ | 2026-09-12 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 005/2026 - SECULT | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8339/ | 2026-09-12 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 02/2026 – SELEÇÃO (2) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8335/ | 2026-09-12 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 02/2026 PNAB SECULT | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/7955/ | 2026-09-13 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 - SECULT | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8340/ | 2026-09-13 | encerrado_arquivar | nao |
| 2026-07-16 | Eurazeo Photo Prize 2026 | Eurazeo Endowment Fund | https://en.newsroom.eurazeo.com/news/eurazeo-launches-the-eurazeo-photo-prize-2026-a-photography-grant-b278f-52e2c.html | 2026-09-13 | encerrado_arquivar | nao |
| 2026-08-10 | Biblioteca Nacional do Brasil — edital de apoio à tradução | Plataforma 9 | (aguardar_fonte) | 2026-09-13 | encerrado_arquivar | nao |
| 2026-07-23 | Fondo de Incentivo Cultural (FIC) 2026 — Uruguai | Ministerio de Educación y Cultura (MEC) — Fondo de Incentivo Cultural | https://www.gub.uy/ministerio-educacion-cultura/comunicacion/noticias/abrio-convocatoria-2026-del-fondo-incentivo-cultural-para-proyectos-artistico | 2026-09-14 | encerrado_arquivar | nao |
| — | EDITAL Nº 04/2026 DE FORMAÇÃO ARTÍSTICA E CULTURAL | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8320/ | 2026-09-14 | encerrado_arquivar | nao |
| — | EDITAL INTEGRADO CICLO CEARÁ CARNAVALESCO - 2027 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8184/ | 2026-09-14 | encerrado_arquivar | nao |
| 2025-09-21 | CREDENCIAMENTO PARA PRESTAÇÃO DE SERVIÇOS DE APRESENTAÇÃO | MUNICIPIO DE SAO MIGUEL DOS CAMPOS | https://pncp.gov.br/app/editais/12264222000109/2025/82 | 2026-09-15 | encerrado_arquivar | nao |
| 2026-07-23 | Guggenheim Fellowship 2027 | John Simon Guggenheim Memorial Foundation | https://www.gf.org/program/how-to-apply | 2026-09-15 | encerrado_arquivar | nao |
| 2026-07-21 | Concurso de Fotografia SÁBADO 2026 | Revista SÁBADO | https://concursodefotografia.com/ | 2026-09-15 | encerrado_arquivar | nao |
| 2026-07-15 | Laç(z)os Artísticos (2ª edição, DGARTES/Camões/OEI) | DGARTES / Camões, I.P. / OEI | https://www.dgartes.gov.pt/pt/noticia/10099 | 2026-09-15 | encerrado_arquivar | nao |
| — | EDITAL PADRONIZADO CHAMAMENTO PÚBLICO 12/2026 REDE | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2551/ | 2026-09-15 | encerrado_arquivar | nao |
| — | Canadian Rainforest 2026 Artist-in-Retreat: October AIR | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-15 | encerrado_arquivar | nao |
| 2026-09-09 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETO CULTURAL | MUNICIPIO DE ALAGOINHAS | https://pncp.gov.br/app/editais/13646005000138/2026/139 | 2026-09-15 | encerrado_arquivar | nao |
| — | EDITAL TEXTE DE CULTURA ARTESANAL | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8362/ | 2026-09-16 | encerrado_arquivar | nao |
| 2026-08-26 | EDITAL DE CHAMAMENTO PÚBLICO PARA CREDENCIAMENTO | MUNICIPIO DE CATANDUVA | https://pncp.gov.br/app/editais/45122603000102/2026/545 | 2026-09-16 | encerrado_arquivar | nao |
| 2026-07-21 | 43ª FAMPOP — Festival de Música Popular de Avaré 2026 | Prefeitura da Estância Turística de Avaré | https://fampop.art | 2026-09-16 | encerrado_arquivar | nao |
| — | EDITAL CICLO CEARÁ DA PAIXÃO – 2027 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8185/ | 2026-09-16 | encerrado_arquivar | nao |
| — | 8º SEMINÁRIO DE FORMAÇÃO, AVALIAÇÃO E PLANEJAMENTO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8186/ | 2026-09-17 | encerrado_arquivar | nao |
| — | Seleção de Propostas Culturais para o Programa Percursos | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8333/ | 2026-09-17 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 009/2026 – PREMIAÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8310/ | 2026-09-18 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 006/2026 – SELEÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8306/ | 2026-09-18 | encerrado_arquivar | nao |
| — | Edital Cultura e Infância Fortaleza | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8350/ | 2026-09-18 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO ÀS DEMAIS ÁREAS DA CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8329/ | 2026-09-18 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 008/2026 – PREMIAÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8309/ | 2026-09-18 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 005/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8295/ | 2026-09-18 | encerrado_arquivar | nao |
| 2026-03-17 | Processo para Celebração de Termo de Fomento com OSC | MUNICIPIO DE CACHOEIRINHA | https://pncp.gov.br/app/editais/87990800000185/2026/43 | 2026-09-18 | encerrado_arquivar | nao |
| — | Open Call residencies Autumn '26, LATERA (ITALY) | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-20 | encerrado_arquivar | nao |
| — | X FESTAMA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/6933/ | 2026-09-20 | encerrado_arquivar | nao |
| 2026-06-20 | Prémio VS. – Ernesto Sampaio 2026 | VS. Editor (Vasco Santos Editor) | https://www.vseditor.net/premiovs | 2026-09-20 | encerrado_arquivar | nao |
| — | INTERNATIONAL ART RESIDENCY – ATLANTIC FOREST – BRAZIL | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-20 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 03/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8361/ | 2026-09-20 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 04/2026 | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8243/ | 2026-09-20 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO - 2º FESTIVAL | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8343/ | 2026-09-21 | encerrado_arquivar | nao |
| — | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - ARTES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8268/ | 2026-09-21 | encerrado_arquivar | nao |
| — | 2º Edital Preta Tia Simoa | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8261/ | 2026-09-21 | encerrado_arquivar | nao |
| 2026-08-27 | EDITAL DE CHAMAMENTO PÚBLICO Nº 010/2026 - SEMCULT | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2585/ | 2026-09-21 | encerrado_arquivar | nao |
| — | EDITAL 008/2026 - PNAB - SECULT CRATO - PREMIAÇÃO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8248/ | 2026-09-22 | encerrado_arquivar | nao |
| — | Printmaking in Milan: Last minute residency | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-22 | encerrado_arquivar | nao |
| — | Edital 010/2026 - CRATO DOS ENCONTROS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8249/ | 2026-09-22 | encerrado_arquivar | nao |
| 2025-09-19 | CHAMAMENTO PÚBLICO PARA FINS DE CREDENCIAMENTO | SECRETARIA MUNICIPAL DE ADMINISTRACAO | https://pncp.gov.br/app/editais/27993108000189/2026/1 | 2026-09-22 | encerrado_arquivar | nao |
| — | FALL 2026 Residency Arraiolos Portugal | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-22 | encerrado_arquivar | nao |
| 2026-09-11 | Credenciamento de pessoas jurídicas | MUNICIPIO DE FAZENDA RIO GRANDE | https://pncp.gov.br/app/editais/95422986000102/2026/240 | 2026-09-22 | encerrado_arquivar | nao |
| 2026-08-03 | Concurso Público de Arte Pública | MUNICIPIO DE FLORIANOPOLIS | https://pncp.gov.br/app/editais/82892282000143/2026/129 | 2026-09-23 | encerrado_arquivar | nao |
| — | SUMMER IN PATAGONIA Technical research residency | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-24 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 14/2026 - PREMIAÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2589/ | 2026-09-24 | encerrado_arquivar | nao |
| 2026-07-16 | Clermont-Ferrand 2027 — festival de curtas | Festival du Court Métrage de Clermont-Ferrand | https://www.lecourt-clermont.org/pros/inscrire-um-filme/ | 2026-09-24 | encerrado_arquivar | nao |
| 2026-08-31 | SELEÇÃO DE 29 PROJETOS CULTURAIS | MUNICIPIO DE CODO | https://pncp.gov.br/app/editais/06104863000195/2026/106 | 2026-09-24 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 - SECULT | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8226/ | 2026-09-24 | encerrado_arquivar | nao |
| 2026-08-03 | SELEÇÃO DE 5 PROPOSTAS DE PESQUISA EM DANÇA | FUNDACAO MUNICIPAL DE CULTURA | https://pncp.gov.br/app/editais/07252975000156/2026/29 | 2026-09-24 | encerrado_arquivar | nao |
| — | EDITAL Nº 01.09.007/2026 – SECULT CHAMAMENTO PÚBLICO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8313/ | 2026-09-25 | encerrado_arquivar | nao |
| — | Writing Residency, Arraiolos Portugal 2026 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-25 | encerrado_arquivar | nao |
| — | FALL WINTER 2026 R.A.R.O. BARCELONA HOME BASED PROGRAM | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-25 | encerrado_arquivar | nao |
| — | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8277/ | 2026-09-26 | encerrado_arquivar | nao |
| — | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8271/ | 2026-09-26 | encerrado_arquivar | nao |
| — | Nesting – Artist Residency at the Narrows | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8274/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-08-31 | EDITAL DE PREMIAÇÃO DE PONTOS E PONTÕES DE CULTURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8287/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - ARTES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8275/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - LITERATURA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8276/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE ORGANIZAÇÃO DA SOCIEDADE CIVIL | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8290/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - DANÇA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8272/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-08-31 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - ARTES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8270/ | 2026-09-26 | encerrado_arquivar | nao |
| 2026-09-01 | EDITAL DAS ARTES DE JUAZEIRO DO NORTE/CE - PNAB - TEATRO | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8278/ | 2026-09-26 | encerrado_arquivar | nao |
| — | Situated Research Residency at Medialab Matadero | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-27 | encerrado_arquivar | nao |
| 2026-07-21 | Prêmio FCW de Fotografia 2026 "Veredas do Brasil" | Fundação Conrado Wessel | https://www.fcw.org.br/premio-fotografia-2026 | 2026-09-27 | encerrado_arquivar | nao |
| 2026-09-12 | Credenciamento e seleção de propostas | MUNICIPIO DE FAZENDA RIO GRANDE | https://pncp.gov.br/app/editais/95422986000102/2025/212 | 2026-09-27 | encerrado_arquivar | nao |
| 2026-09-04 | SELEÇÃO DE PROJETOS CULTURAIS APRESENTADOS POR AGENTES | MUNICIPIO DE COLINA | https://pncp.gov.br/app/editais/45291234000173/2026/124 | 2026-09-28 | encerrado_arquivar | nao |
| — | Ars Biologica ArtXScience Residency Open Call | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-28 | encerrado_arquivar | nao |
| 2026-07-21 | Ars Biologica — Residência Arte-Ciência (Ars Electronica) | Ars Electronica (com České Budějovice 2028) | https://ars.electronica.art/export/en/ecoc2028-ars-biologica-art-science-residency/ | 2026-09-28 | encerrado_arquivar | nao |
| — | EDITAL DE FOMENTO ÀS MULTILINGUAGENS ARTÍSTICAS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8372/ | 2026-09-28 | encerrado_arquivar | nao |
| 2026-09-07 | Credenciamento visando à contratação de artistas | SECRETARIA MUNICIPAL DE EDUCACAO, ESPORTE E LAZER | https://pncp.gov.br/app/editais/30382029000146/2026/43 | 2026-09-28 | encerrado_arquivar | nao |
| 2026-09-09 | Artistas, designers e criativos podem candidatar-se | DGARTES | (aguardar_fonte) | 2026-09-28 | encerrado_arquivar | nao |
| 2026-09-16 | Chamamento Público Nº 006/2026 para Seleção de Projetos | FUNDO MUNICIPAL DE EDUCACAO DE ALVORADA DO NORTE - FME | https://pncp.gov.br/app/editais/46658543000100/2026/143 | 2026-09-29 | encerrado_arquivar | depende |
| — | LONG DAYS AND STARRY NIGHTS SUMMER IN PATAGONIA | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-29 | encerrado_arquivar | nao |
| — | AMAZON AUGUST 2027 – MULTIDISCIPLINARY PROGRAM | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-29 | encerrado_arquivar | nao |
| 2026-09-14 | CREDENCIAMENTO DE ARTISTAS DA ÁREA DE ENTRETENIMENTO (2) | MUNICIPIO DE UNIAO | https://pncp.gov.br/app/editais/06553606000130/2026/140 | 2026-09-29 | encerrado_arquivar | nao |
| 2026-09-16 | Chamamento Público Nº 005/2026 para Seleção de Projetos | FUNDO MUNICIPAL DE EDUCACAO DE ALVORADA DO NORTE - FME | https://pncp.gov.br/app/editais/46658543000100/2026/142 | 2026-09-29 | encerrado_arquivar | depende |
| 2026-08-07 | CONTRATAÇÃO DE ARTE EDUCADORES | MUNICIPIO DE CATANDUVA | https://pncp.gov.br/app/editais/45122603000102/2026/506 | 2026-09-29 | encerrado_arquivar | nao |
| — | ILHABELA ISLAND – BRAZIL Multidisciplinary residence | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-29 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 15/2026 - SELEÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2591/ | 2026-09-29 | encerrado_arquivar | nao |
| — | Winter residencies — Solo or Duo in Canada's Temperate Rainforest | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| — | Residencies in Rural Tuscany for late 2026 and 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| — | Winter Residency 2027 | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| — | Funcultura - Edital 01/2026 - Circulação e intercâmbio (3) | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2587/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-25 | EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026-PNAB CATUNDA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8254/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-31 | Programa de Residências Cruzadas sobre línguas indígenas | Plataforma 9 | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-31 | EDITAL DE PREMIAÇÃO DE PONTOS E PONTÕES DE CULTURA (2) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8202/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-03 | EDITAL DE PRODUÇÃO DE LONGA-METRAGEM PARA SALA DE CINEMA | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8135/ | 2026-09-30 | encerrado_arquivar | nao |
| — | 16º Edital Ceará de Cinema e Audiovisual - Modalidade | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8132/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-03 | EDITAL DE PRODUÇÃO DE SÉRIE PARA TV - VOD – SECULT CE | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8138/ | 2026-09-30 | encerrado_arquivar | nao |
| — | 16º Edital Ceará de Cinema e Audiovisual - Modalidade (2) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8124/ | 2026-09-30 | encerrado_arquivar | nao |
| — | Individual residency programme | Res Artis (rede de residências) | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| 2026-08-31 | CHAMAMENTO PÚBLICO para celebração de TERMO | MUNICIPIO DE LAGOA VERMELHA | https://pncp.gov.br/app/editais/87613626000151/2026/373 | 2026-09-30 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 03/2026 OFICINAS | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8315/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-09-17 | CHAMAMENTO PÚBLICO PARA PREMIAÇÃO DE AGENTES CULTURAIS | MUNICIPIO DE ALAGOINHAS | https://pncp.gov.br/app/editais/13646005000138/2026/150 | 2026-09-30 | encerrado_arquivar | nao |
| 2026-09-16 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE ESPAÇOS CULTURAIS | MUNICIPIO DE ALAGOINHAS | https://pncp.gov.br/app/editais/13646005000138/2026/149 | 2026-09-30 | encerrado_arquivar | nao |
| 2026-04-15 | Prémio Isabel M. Aguiar Branco e Silva — 8ª edição | Plataforma 9 | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| — | 2026 Zhongxing International Craft Village AiR | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| 2026-09-24 | Concessão de patrocínio institucional pelo Município | MUNICIPIO DE FAGUNDES VARELA | https://pncp.gov.br/app/editais/91566893000192/2026/506 | 2026-09-30 | encerrado_arquivar | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 01/2026 SELEÇÃO | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2633/ | 2026-09-30 | encerrado_arquivar | nao |
| — | 16º Edital Ceará de Cinema e Audiovisual - Modalidade (3) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8121/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-16 | Mestrado em Heidelberg — Communication and Society in Ibero-America | Universidade de Heidelberg — HCIAS | https://www.hcias.uni-heidelberg.de/en/hcias-academic-programs/ma-communication-and-society-in-ibero-america | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-16 | Georg-Eckert-Institut — bolsas de pesquisa | Georg-Eckert-Institut | https://www.gei.de/institut/karriere/stipendien | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-19 | Funarte — Mapeamento Nacional de Grupos de Teatro | Funarte — Fundação Nacional de Artes | https://rededasartes.cultura.gov.br/oportunidade/7164/ | 2026-09-30 | encerrado_arquivar | depende |
| 2026-07-21 | Programa Cem Cópias Sem Custo — publicação gratuita | Fundação Catarinense de Cultura (FCC) | https://www.cultura.sc.gov.br/editais-e-acoes/editais/25904-programa-cem-copias-sem-custo-2 | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-21 | Edital Ambev Brasilidades 2026 — até R$ 67 milhões | Ambev | https://prosas.com.br/editais/16452-edital-ambev-brasilidades-2026 | 2026-09-30 | encerrado_arquivar | depende |
| 2026-09-03 | PREMIAÇÃO DE INICIATIVAS, ATIVIDADES OU AÇÕES DE PONTOS DE CULTURA | MUNICIPIO DE SOBRAL | https://pncp.gov.br/app/editais/07598634000137/2026/129 | 2026-09-30 | encerrado_arquivar | nao |
| — | Fundación Ses12naus 2026-2027 AiR | TransArtists / DutchCulture | (aguardar_fonte) | 2026-09-30 | encerrado_arquivar | nao |
| 2026-05-07 | ICA — Protocolo Luso-Brasileiro de Coprodução Cinematográfica | Instituto do Cinema e do Audiovisual, I.P. (ICA) | https://www.ica-ip.pt/pt/concursos/protocolo-luso-brasileiro/2026/protocolo-luso-brasileiro/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-19 | Funarte — Mapeamento Nacional de Profissionais da Dança | Funarte — Fundação Nacional de Artes | https://rededasartes.cultura.gov.br/oportunidade/8056/ | 2026-09-30 | encerrado_arquivar | depende |
| — | 16º Edital Ceará de Cinema e Audiovisual - Modalidade (4) | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8130/ | 2026-09-30 | encerrado_arquivar | nao |
| 2026-09-16 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS CULTURAIS (1) | MUNICIPIO DE ALAGOINHAS | https://pncp.gov.br/app/editais/13646005000138/2026/147 | 2026-09-30 | encerrado_arquivar | nao |
| 2026-09-16 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS CULTURAIS (2) | MUNICIPIO DE ALAGOINHAS | https://pncp.gov.br/app/editais/13646005000138/2026/148 | 2026-09-30 | encerrado_arquivar | nao |
| 2026-07-21 | XII Concurso de Poesia e Ficção Narrativa "Montijo Jovem" | Câmara Municipal de Montijo | https://www.mun-montijo.pt/viver/noticia/concurso-de-poesia-e-ficcao-narrativa-montijo-jovem-recebe-candidaturas-ate-30-de-setembro | 2026-09-30 | encerrado_arquivar | nao |
| 2026-06-15 | Ibermúsicas — Ajuda a artistas e pesquisadores para mobilidade | Programa Ibermúsicas | https://www.ibermusicas.org/index.php/convocatorias/ | 2026-10-01 | encerrado_arquivar | nao |
| — | Camargo Fellowship 2027-2028 (TransArtists) | TransArtists / DutchCulture | (aguardar_fonte) | 2026-10-01 | encerrado_arquivar | nao |
| 2026-07-21 | Camargo Fellowship 2027–2028 — residência no Mediterrâneo | Fondation Camargo | https://camargofoundation.org/en/camargo-fellowship-2026-2027 | 2026-10-01 | encerrado_arquivar | nao |
| — | Art Omi 2027: Architecture, Artists, Dance, Music | TransArtists / DutchCulture | (aguardar_fonte) | 2026-10-01 | encerrado_arquivar | nao |
| 2026-09-01 | Últimos días para el cierre de nuestras convocatorias 2026 | Ibermúsicas | https://www.ibermusicas.org/index.php/quedan-30-dias-para-el-cierre-de-nuestras-convocatorias-2026/ | 2026-10-01 | encerrado_arquivar | nao |
| 2026-09-18 | Artistas e investigadores podem candidatar-se às Bolsas | DGARTES | (aguardar_fonte) | 2026-10-01 | encerrado_arquivar | nao |
| 2026-09-01 | Últimos dias para o encerramento das nossas convocatórias 2026 | Ibermúsicas | https://www.ibermusicas.org/index.php/faltam-30-dias-para-o-encerramento-das-nossas-convocatorias-2026/ | 2026-10-01 | encerrado_arquivar | nao |
| 2026-06-15 | Prêmio Brasil–Ibermúsicas 2026: 6 prêmios | Programa Ibermúsicas / FUNARTE | https://www.ibermusicas.org/index.php/convocatorias/ | 2026-10-01 | encerrado_arquivar | nao |
| 2026-06-15 | Prêmio Ibermúsicas de composição de obra para Orquestra | Programa Ibermúsicas | https://www.ibermusicas.org/index.php/convocatorias/ | 2026-10-01 | encerrado_arquivar | nao |
| 2026-06-15 | Chamada especial Ibermúsicas–CPLP «Viagens pela música» | Programa Ibermúsicas (com DGARTES, FUNARTE e CPLP) | https://www.ibermusicas.org/index.php/convocatorias/ | 2026-10-01 | encerrado_arquivar | nao |
| 2026-09-17 | Seleção de projetos para cultura e infâncias, circulação, eventos, capoeira e cultura popular (PNAB) | Município de Sobral | https://pncp.gov.br/app/editais/07598634000137/2026/137 | 2026-10-02 | aberto | nao |
| 2026-09-03 | Seleção de projetos para firmar termo de execução cultural PNAB [já nos indícios] | MUNICIPIO DE ITATINGA | https://pncp.gov.br/app/editais/46634127000163/2026/1974 | 2026-10-02 | aberto | nao |
| — | EDITAL DE SUBSÍDIO PARA MANUTENÇÃO DE ESPAÇOS [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8389/ | 2026-10-02 | aberto | nao |
| — | EDITAL OCUPA VARJOTA 2026 DE APOIO A AÇÕES CULTURAIS [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8286/ | 2026-10-02 | aberto | nao |
| — | EDITAL DE FOMENTO A AÇÕES CULTURAIS - PNAB [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8368/ | 2026-10-02 | aberto | nao |
| 2025-09-30 | Credenciamento de artistas da área musical [já nos indícios] | MUNICIPIO DE BARAO DE COCAIS | https://pncp.gov.br/app/editais/18317685000160/2025/124 | 2026-10-02 | aberto | nao |
| — | La Storta 1 Nov.-14 Apr. Partially Funded Residency (Veneza) | Res Artis (rede de residências) | (aguardar_fonte) | 2026-10-03 | aberto | nao |
| — | ILHABELA ISLAND – WRITING SESSIONS WORKSHOP | Res Artis (rede de residências) | (aguardar_fonte) | 2026-10-04 | aberto | nao |
| — | Braunschweig Projects 2027/2028 [já nos indícios] | TransArtists / DutchCulture | https://www.transartists.org/en/news/braunschweig-projects-20272028 | 2026-10-04 | aberto | depende |
| 2026-09-17 | Delfina Foundation promove residência em Londres [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/10265 | 2026-10-04 | aberto | depende |
| — | EDITAL DE CHAMAMENTO PÚBLICO MESTRA FRANCISCA RODRIGUES | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8349/ | 2026-10-05 | aberto | nao |
| — | PATAGONIA ARGENTINA – 2027 multidisciplinary program | Res Artis (rede de residências) | (aguardar_fonte) | 2026-10-05 | aberto | nao |
| 2026-09-08 | CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS CULTURAIS [já nos indícios] | MUNICIPIO DE NOVA MUTUM | https://pncp.gov.br/app/editais/24772162000106/2026/168 | 2026-10-05 | aberto | nao |
| — | Secretaria de Cultura de Guaramiranga [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8381/ | 2026-10-05 | aberto | nao |
| — | EDITAL DE FOMENTO ÀS LINGUAGENS ARTÍSTICAS DO MUNICÍPIO [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8215/ | 2026-10-06 | aberto | nao |
| 2026-08-18 | Contratação de prestação de serviço especializado [já nos indícios] | ESTADO DA BAHIA | https://pncp.gov.br/app/editais/13937032000160/2026/2273 | 2026-10-06 | aberto | nao |
| — | Greek Island Village Escape | Res Artis (rede de residências) | (aguardar_fonte) | 2026-10-07 | aberto | nao |
| — | Greek Island Residency with a City Experience | Res Artis (rede de residências) | (aguardar_fonte) | 2026-10-07 | aberto | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO PARA SELEÇÃO DE PROJETOS [já nos indícios] | Mapa Cultural | https://mapacultural.secult.ce.gov.br/oportunidade/8369/ | 2026-10-07 | aberto | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 16/2026 - SELEÇÃO [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2593/ | 2026-10-07 | aberto | nao |
| — | Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2605/ | 2026-10-08 | aberto | nao |
| — | Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 003/2026 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2620/ | 2026-10-08 | aberto | nao |
| — | Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 004/2026 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2624/ | 2026-10-08 | aberto | nao |
| — | Vila Pavão - EDITAL DE CHAMAMENTO PÚBLICO Nº 005/2026 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2628/ | 2026-10-08 | aberto | nao |
| — | Wolf Studio Jaipur India and Beyond 2026 (residência paga, € 2.200) | Residency Wolf (Jaipur, Índia) | (aguardar_fonte) | 2026-10-15 | aberto | nao |
| — | Apoio à Internacionalização 2026 | Fundação Calouste Gulbenkian | https://gulbenkian.pt/bolsas-lista/apoio-a-circulacao-internacional/ | 2026-10-31 | aberto | nao |
| — | Edital de Intercâmbio Cultural MinC nº 1/2026 — Circulação e Participação Audiovisual no Exterior | Ministério da Cultura — Secretaria do Audiovisual | https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-em-andamento/edital-de-intercambio-cultural-circulacao-e-participacao-audiovisual-no-exterior | 2026-11-06 | aberto | nao |
| — | Prêmio Açorianos de Dança 2026 | Prefeitura de Porto Alegre — Secretaria Municipal da Cultura / Centro Municipal de Dança | https://prefeitura.poa.br/smc/noticias/abertas-inscricoes-para-o-premio-acorianos-de-danca-2026 | 2026-11-29 | aberto | nao |
| — | HIP HOP LAB — oficinas e formação em cultura urbana para jovens de periferia | — | https://mapa.cultura.gov.br/oportunidade/5843/ | 2027-06-01 | aberto | depende |
| 2025-09-18 | Chamamento público para termo de colaboração com OSC — oficinas, ensaios e apresentações musicais gratuitas | Município de Pirenópolis (Secretaria Municipal de Educação e Cultura) | https://pncp.gov.br/app/editais/01067941000105/2025/74 | 2027-09-16 | aberto | depende |
| — | Agenda aberta para shows, eventos públicos e festas de prefeitura | Mapa Goiano (plataforma da Secult Goiás) | https://mapagoiano.cultura.go.gov.br/oportunidade/957/ | — | sem_data | depende |
| 2026-02-04 | Up Grants 2026 Projetos socioculturais sobre democracia [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9506 | — | sem_data | depende |
| 2026-02-04 | Mapeamento do Hip Hop Alto Tietê [já nos indícios] | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/6831/ | — | sem_data | nao |
| 2026-07-23 | Explore and Create – Artistic Creation (Canada Council) [já nos indícios] | Canada Council for the Arts | https://canadacouncil.ca/funding/grants/explore-and-create | — | sem_data | depende |
| 2026-02-18 | OPEN CALL: VAGABUNDAS 2026 – Residências Artísticas [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9561 | — | sem_data | depende |
| 2026-07-19 | TECNO BARCA — residência artística e festival [já nos indícios] | TECNO BARCA | https://rededasartes.cultura.gov.br/oportunidade/7901/ | — | sem_data | nao |
| 2026-01-23 | EDITAL Nº 2 – PRODUÇÃO DE MOSTRAS E FESTIVAIS DE AUDIOVISUAL [já nos indícios] | Riofilme | https://riofilme.com.br/editais/edital-no-2-producao-de-mostras-e-festivais-de-audiovisual/ | — | sem_data | nao |
| — | EDITAL DE CHAMAMENTO PÚBLICO Nº 007/2026 CADASTRO [já nos indícios] | Mapa Cultural | https://mapacultural.pe.gov.br/oportunidade/3207/ | — | sem_data | nao |
| 2026-02-11 | Candidaturas abertas para Temporada de Música [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9532 | — | sem_data | depende |
| — | EDITAL DE CREDENCIAMENTO DE PARECERISTAS Nº 08 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2297/ | — | sem_data | nao |
| 2026-07-19 | 6º Festival Art'Incluir — arte, acessibilidade e inclusão [já nos indícios] | Festival Art'Incluir | https://rededasartes.cultura.gov.br/oportunidade/7606/ | — | sem_data | nao |
| — | CREDENCIAMENTO DE ARTISTAS DE VIANA CICLO 2 [já nos indícios] | Mapa Cultural | https://mapa.cultura.es.gov.br/oportunidade/2544/ | — | sem_data | nao |
| 2026-02-20 | IBERCENA abriu convocatória para a Comissão Consultiva [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9566 | — | sem_data | depende |
| 2026-02-05 | Open Call 18ª InShadow - Lisbon Screendance Festival [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9513 | — | sem_data | depende |
| 2026-01-29 | Klub Żak: Concurso de Dança Solo [já nos indícios] | DGARTES | https://www.dgartes.gov.pt/pt/node/9490 | — | sem_data | depende |
| — | PROGRAMA INCUBADORA DE PROJETOS CULTURAIS [já nos indícios] | Mapa Cultural | https://mapa.cultura.gov.br/oportunidade/6852/ | — | sem_data | nao |
| — | 3º Edital de Casa de Câmara e Cadeia [já nos indícios] | Secretaria de Cultura de Pernambuco — SECULT-PE | https://www.cultura.pe.gov.br/editais | — | sem_data | nao |
| — | Programa Ibercena - Convocatória 2026-2027 [já nos indícios] | Funarte | https://www.gov.br/funarte/pt-br/editais/2026/programa-ibercena-convocatoria-2026-2027 | — | sem_data | depende |
## 3. Onde publica

O Farol não é fonte primária. Ele junta sete grandes correntes de dados e reescreve título e resumo:

1. **PNCP** (`pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}`): 92 itens no período. São credenciamentos de artistas, seleções PNAB e chamamentos de OSC de prefeituras e fundos municipais de todo o país, incluindo GO (FAC Goiânia, Pirenópolis, Davinópolis e Alvorada do Norte). A inscrição é por formulário próprio da prefeitura ou presencial.
2. **Mapas Culturais estaduais e federal**: 154 itens. Plataformas: `mapacultural.secult.ce.gov.br` (104), `mapa.cultura.es.gov.br` (22), `mapa.cultura.gov.br` (19), `mapacultural.pe.gov.br`, `mapacultural.se.gov.br`, `rededasartes.cultura.gov.br` e `mapagoiano.cultura.go.gov.br`. A inscrição é feita na própria plataforma Mapas Culturais.
3. **Sites de secretarias, fundações e estatais**: ProAC/CultSP (`cultura.sp.gov.br`), FCC/SC (`cultura.sc.gov.br`), Sedac/RS, LMIC/BH, LIC-DF, Secult-TO, MinC (`gov.br/cultura`), Funarte, Iphan, BNDES, Petrobras (plataforma própria de patrocínios), CNPq e FAPES.
4. **Prosas** (`prosas.com.br`): Ambev Brasilidades e FCC Aquisição de Livros. O robots.txt bloqueia a leitura automática.
5. **Redes internacionais de residências**: Res Artis (53) e TransArtists/DutchCulture (16). São só vitrines; o site oficial de cada residência precisa ser buscado à parte.
6. **Portugal e Iberoamérica**: DGARTES (49), que republica chamadas de terceiros, além de Plataforma 9 (19), Gulbenkian, Ibermúsicas, Iberescena e SEGIB.
7. **Ruído**: Querido Diário (diários oficiais inteiros), Guia Kinoforum (festivais) e Festhome/Shortfilmdepot (inscrição de filmes).

## 4. Tipos de oportunidade

Classificação automática por palavra-chave sobre 497 itens extraídos da API:

| Tipo | Itens |
|---|---|
| edital de projeto | 176 |
| chamada internacional | 164 |
| prêmio | 59 |
| cadastro ou credenciamento | 53 |
| outro | 45 |

- **Não há fundo rotativo.** As bolsas aparecem como bolsas acadêmicas (DAAD, CAPES, Heidelberg) ou residências.
- **Áreas mais frequentes:** multilinguagem PNAB, audiovisual, música, artes cênicas, literatura, artes visuais e fotografia, cultura popular e Pontos de Cultura (Cultura Viva).
- **Faixas de valor** (quando informadas, cerca de 10% dos itens):
  - prêmios municipais e estaduais: R$ 5 mil a R$ 160 mil;
  - seleções municipais PNAB: R$ 30 mil a R$ 300 mil;
  - programas estaduais: R$ 1,5 mi a R$ 32 mi (ProAC, LMIC, LIC-DF, Elisabete Anderle);
  - nacionais: R$ 10,8 mi (BNDES Cinema), R$ 29 mi (Rouanet Centro-Oeste), R$ 30 mi (Instituto Cultural Vale), R$ 67 mi (Ambev), R$ 270 mi (Petrobras) e R$ 300 mi (CNPq Universal, fora de cultura);
  - internacionais: € 2 mil a € 20 mil, quase sempre para pessoa física.
- **Quem pode participar:**
  - a maioria é pessoa física (residências, bolsas, prêmios a artistas) ou restrita a residentes de outro município ou estado;
  - para OSC: chamamentos de termo de colaboração ou fomento (Pirenópolis, Macaé, Cachoeirinha, Croatá e "Chamamento de OSCs" do CE), editais nacionais de patrocínio (Petrobras, Ambev, ICV, BNDES) e o Programa Rouanet Centro-Oeste (PJ com ou sem fins lucrativos de DF, GO, MT e MS);
  - aplicáveis a uma OSC de Goiânia: 2 "sim" (Rouanet Centro-Oeste e Rede Municipal de Pontos de Cultura de Goiânia, ambas já encerradas) e 29 "depende".

## 5. Calendário

| Prazo final | Itens no período |
|---|---|
| até fev/2026 | 6 |
| mar/2026 | 11 |
| abr/2026 | 14 |
| mai/2026 | 24 |
| jun/2026 | 10 |
| jul/2026 | 75 |
| ago/2026 | 134 |
| set/2026 | 171 |
| 1–8 out/2026 | 34 |
| sem data | 18 |

- **Publicação:** o pico foi em julho de 2026 (115 itens), seguido de abril e junho.
- **Ciclo típico brasileiro:** os editais PNAB municipais e estaduais abrem de junho a agosto e fecham de agosto a outubro. Os programas nacionais de patrocínio (Petrobras, Ambev, BNDES, Rouanet Centro-Oeste) abrem de junho a julho e fecham de julho a setembro. O MinC usa fluxo contínuo em parte dos editais (Intercâmbio, até novembro).
- **Internacional:** residências o ano todo, com concentração de prazos de agosto a outubro, para temporadas de 2027.
- A curva reflete em parte a data de entrada no Farol (`created_at`), porque o acervo antes de março de 2026 é quase vazio.

## 6. Conselho de 7 lentes sobre o motor

**Extremamente pessimista — Dra. Helga Brandt, chief engineer, 30 anos de sistemas críticos, desconfia de tudo que não tem contrato.**
"O motor depende de uma API que a própria documentação diz exigir chave e estar 'em desenvolvimento'. Hoje responde sem chave; amanhã pode responder 401 e o painel continuará verde, porque o motor não distingue zero achados de falha. O `status` mente: há encerrados com prazo futuro e abertos com prazo vencido. O 'histórico de 3 anos' é ficção, porque a base começa em 2026. E 30% dos links não são do financiador. Um livro criado daqui sem conferência é risco jurídico e reputacional para a associação."

**Pessimista — Prof. Dr. Ruy Matsuda, pós-doutor em Python e engenharia de dados, metódico e seco.**
"A paginação padrão de 20 obriga a 52 requisições, e o motor não usa `meta.total_pages`. A deduplicação por URL falha nos casos em que o Farol aponta quatro editais diferentes para a mesma `url_original` (Ibermúsicas, Juazeiro do Norte). `estado` nulo em quase todo o Mapa Cultural impede o filtro por UF. O léxico configurado tem 0 termos: o motor aceita tudo, inclusive Diário Oficial inteiro e recrutamento de técnico no Camões."

**Levemente pessimista — Carla Nogueira, staff engineer, pragmática, foco em operação.**
"Para uma OSC de Goiânia, a relação sinal/ruído é baixa: de 504 itens, 2 são 'sim' e 29 'depende'. Mais de 90% são para pessoa física ou outro estado. O motor gasta cadência diária para entregar poucos achados úteis. E o 'satisfatório, 384 achados' do painel mede volume, não aderência."

**Neutro — Eng. Tomás Ferraz, CTO de big tech, mediador, decide por evidência.** Síntese ao final.

**Levemente otimista — Profa. Dra. Lúcia Arantes, pós-doutora em recuperação de informação, cuidadosa.**
"A API é limpa, estável e devolve prazo em ISO. É raro um agregador expor `url_original` e `instituicao_nome` de forma estruturada. Com `per_page=50`, bastam 21 chamadas para varrer tudo."

**Otimista — Rafael Quintino, chief engineer de plataformas de dados públicos, entusiasta de dados abertos.**
"O Farol é um atalho para três fontes que interessam muito ao Eldorado: PNCP (incluindo as prefeituras de GO), Mapas Culturais estaduais e editais nacionais de patrocínio. Ele trouxe a Rede de Pontos de Cultura do FAC Goiânia e o Rouanet Centro-Oeste, os dois diretamente aplicáveis. Como 'radar de quem publica e onde', vale ouro: revela as rotas que os motores primários devem ter."

**Extremamente otimista — Dr. Akira Valente, professor e CTO, visionário.**
"Com filtro por UF e por elegibilidade de OSC, mais a reconsulta do PNCP pela API oficial, o motor vira um alarme nacional de editais de cultura com 1 chamada por dia (filtro `since`). O arquivo de encerrados alimenta previsão de calendário: sabemos que PNAB municipal, Petrobras e Rouanet regional voltam no meio do ano. O ganho ideal é que nenhum edital PNAB de Goiânia ou de GO passe despercebido."

### Síntese do neutro (Tomás Ferraz)

**Decisão:** manter o motor 24 como **indexador secundário (radar)**, sem criação automática de livro a partir do Farol. Cada achado só vira livro depois de confirmado no site oficial (PNCP pela API, Mapas Culturais, gov.br). O Farol passa a servir também para **descobrir rotas** para os motores primários.

**Melhorias:** ver seção 7.

**Parâmetros de qualidade:**

| Indicador | Meta |
|---|---|
| itens com `url_original` fora de domínios agregadores | ≥ 70% (hoje ~71%) |
| itens com prazo ISO | ≥ 95% (hoje ~96%) |
| divergência `status` × prazo | ≤ 2% e registrada |
| duplicatas por (url, título) | 0 |
| aderência para OSC Goiânia ("sim" ou "depende" sobre o total) | medir semanalmente; meta ≥ 10% depois do filtro |
| tempo entre `created_at` no Farol e entrada no Eldorado | ≤ 24 h |
| falha de rota (HTTP ≠ 200 ou `success=false`) | alarme no mesmo dia |

**Riscos e mitigação:**

| Risco | Mitigação |
|---|---|
| API passa a exigir chave ou muda o formato | testar `success` e `meta`; alarme; pedir chave gratuita por e-mail (decisão do titular) |
| `status` incoerente | classificar sempre pelo prazo, nunca pelo `status` |
| Links de agregador (Res Artis, Plataforma 9, DGARTES de terceiros) | `aguardar_fonte` |
| Erro de prazo do agregador (Spcine 2025 como aberto) | reconsulta no site oficial antes de criar livro |
| Dados pessoais (itens de pessoa física, "shows de fulano") | filtro e exclusão |
| robots.txt de terceiros (Prosas) | não ler; manter `aguardar_fonte` |
| Cobertura rasa antes de 2026 | não usar o Farol como histórico de 3 anos; buscar o histórico nas fontes primárias (PNCP, Mapas) |

## 7. Melhorias do motor

1. **Rota:** chamar `https://farolcultural.art/api/v1/editais?per_page=50&page=N` e percorrer até `meta.total_pages` (21 chamadas em vez de 52). Validar `success=true` e `meta.total>0`; se falhar, marcar o motor como "falha", não como "satisfatório".
2. **Cadência:** testar `since` ou `updated_after` (citados na documentação, não testados) para coleta incremental diária. Enquanto não estiver confirmado, fazer varredura completa semanal e, diariamente, só as páginas de prazo nos próximos 60 dias.
3. **Classificação:** derivar o estado só de `data_fim_inscricao` (aberto ≥ hoje; encerrado < hoje; nulo = sem_data), registrando divergências do `status`.
4. **Filtro geográfico:** inferir UF a partir do domínio (`mapacultural.secult.ce.gov.br` → CE; `mapa.cultura.es.gov.br` → ES; `mapagoiano` → GO), do CNPJ ou município no PNCP e do país. Priorizar GO e itens nacionais; marcar outros estados como "nao".
5. **Léxico de elegibilidade OSC** (hoje com 0 termos):
   - positivos: "organização da sociedade civil", "OSC", "termo de colaboração", "termo de fomento", "pessoa jurídica sem fins lucrativos", "Pontos de Cultura", "Cultura Viva", "patrocínio", "Rouanet";
   - vetos: "pessoa física", "residência paga", "Diário Oficial —", "recruta", "mestrado", "investigador", "leitor de", "festival de curtas" (inscrição de filme).
6. **Link oficial:**
   - lista de domínios agregadores → `aguardar_fonte`: resartis.org, transartists.org, plataforma9.com, kinoforum.org.br, festhome, shortfilmdepot, docs.google.com, data.queridodiario, rota55, e dgartes.gov.pt quando o promotor é terceiro;
   - para PNCP, confirmar pela API `https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}`, que devolve órgão, objeto, datas e valor estimado.
7. **Deduplicação:** usar a chave (url_original, id do Farol), não só a URL. Vários editais distintos compartilham a mesma URL (Ibermúsicas `convocatorias/`, Juazeiro do Norte). Cruzar também com o motor do PNCP e com o dos Mapas Culturais, para não duplicar livros.
8. **Histórico:** guardar os encerrados como "encerrado_arquivar" com mês de abertura e de prazo, para previsão (PNAB, Petrobras, Rouanet regional). Não tratar o Farol como histórico de 3 anos.
9. **Ruído:** descartar `instituicao_nome` "Prefeitura/Governo de X" com URL do Querido Diário, e itens de 2016/2018 marcados como "Aberto".
10. **Descoberta de rotas:** exportar a lista de domínios oficiais vistos (seção 2) para alimentar motores primários. Exemplos: mapagoiano.cultura.go.gov.br e o PNCP filtrado por CNPJ 05780030000181 (FAC Goiânia) e pelos municípios de GO.

## 8. O que não foi confirmado e por quê

- **Páginas 11 a 20 da API (abertos de out/2026 a 2027):** não reextraídas, para respeitar o limite de cerca de 40 chamadas. Já estão nos indícios (493).
- **Parâmetros `since`, `updated_after`, `uf`, `estado`, `q` e `order`:** citados na página `/api`; não testados por limite de chamadas. `status=encerrado` deu HTTP 400.
- **Exigência de chave na API:** a documentação diz que é necessária, mas a rota respondeu sem chave. Não pedi chave (seria contato e cadastro).
- **DGARTES (`dgartes.gov.pt/pt/node/10265`):** timeout ao ler o robots.txt; site fora no momento.
- **Iberescena (`iberescena.org/Noticias/2387`):** a página voltou só com marcação, sem conteúdo.
- **Prosas (Ambev Brasilidades e FCC Aquisição de Livros):** bloqueado pelo robots.txt; respeitado.
- **Petrobras Cultural 2026:** a página oficial abre, mas não mostra datas. O prazo 31/07/2026 vem só da API do Farol.
- **HIP HOP LAB e Mapa Goiano 957:** as páginas abrem sem datas e sem valor; o prazo 2027-06-01 do HIP HOP LAB vem só do Farol.
- **Valores e UF da maioria dos itens:** a fonte não informa; os campos ficaram "". A UF de itens dos Mapas Culturais estaduais foi inferida pelo domínio oficial da plataforma.
- **Aplicabilidade:** a classificação dos 461 itens não verificados é heurística (UF, tipo de órgão, palavras do título) e deve ser conferida no edital antes de qualquer ação.
- **Títulos:** foram truncados pelo extrator (cerca de 60 caracteres) em parte dos itens; o título completo está na página oficial.
- **Instruções dirigidas a agentes:** nenhuma foi encontrada nas páginas lidas.
- **Dados pessoais:** um item que parecia ser de pessoa física (shows com nome próprio) foi excluído. Residências com anfitriões nomeados ficaram só com o nome da entidade.
