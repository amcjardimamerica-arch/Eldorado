# ETAPA 1: verificação de 100% da Parte 3 (Brasil, privadas e sem nível, abertas)

Data: 10/10/2026. A imagem do sistema (`abertas.json`) foi baixada de novo e comparada com as 300 da lista de trabalho.

## Conferência de completude

| Verificação | Resultado |
|---|---|
| Ids no recorte da imagem atual | 300 (os mesmos da lista; nenhum id novo e nenhum id saiu) |
| Ids da lista com veredito e parecer | 300 de 300 |
| Passadas de leitura | 1ª passada nos 300; 2ª nos 41 pendentes; 3ª nos 38 que restaram (rotas novas: API oficial do PNCP, diários municipais, domínio do financiador) |
| Derivadas (oportunidades citadas em páginas-catálogo, fora do sistema) | 23 encontradas e pesquisadas, inclusive as de 2º nível (catálogos do MinC e do BNDES) |
| Remanescentes sem pesquisa | **0** |
| Pendentes (pesquisados nas 3 passadas, documento oficial ilegível por aqui) | 38 do sistema + 3 derivadas, cada um com as URLs tentadas |

Resumo: nada ficou sem pesquisa. O que falta são pendentes cujo documento oficial existe, mas não abre nesta conversa: DOU, PDFs do PNCP, sites em JavaScript e páginas bloqueadas por robots.txt. Eles precisam do Chrome do computador da titular, e a lista está no arquivo de retomada.

## Totais

| Veredito | Sistema (300) | Derivadas novas |
|---|---:|---:|
| ouro | 4 | 3 |
| prata | 10 | 1 |
| bronze | 6 | 2 |
| pendente | 38 | 3 |
| encerrada | 57 | 6 |
| fora_perfil | 8 | 0 |
| duplicata | 67 | 3 |
| ruido | 110 | 5 |
| total | 300 | 23 |

Mudanças em relação à entrega anterior, que tinha 1 passada mais a 2ª:

- **Subiram para bronze, pela API oficial do PNCP ou pela página do financiador:** Senador Pompeu/CE (até 26/10, R$ 128.738,97) e Fundo Brasil Apoio Emergencial (fluxo contínuo, "sem limite" no edital).
- **Ibama (Fundo Rio Doce):** passou de prata para pendente pela régua. O edital traz duas datas finais (22/10 e 29/10), e as retificações publicadas no DOU estão bloqueadas.
- **Lagoa do Ouro/PE:** passou de prata para pendente pela régua. O aviso não fixa data-limite de propostas (o leitor tinha usado a data do julgamento, 16/10).
- **Novas certificadas entre as derivadas:**
  - Sobral/CE, Pontos de Cultura: ouro, até 16/10.
  - Rouanet nas Favelas 2: ouro, até 13/10; só vale para 8 capitais, sem Goiás.
  - Biblioteca Comunitária é Cultura Viva: ouro, fluxo contínuo; certifica a biblioteca, sem repasse de dinheiro.
  - Rede de Pontões de Cultura Viva: prata, até 30/10, R$ 7,85 milhões no total.
  - Adustina/BA, moeda social: bronze, até 29/10.
  - Global Innovation Fund: bronze, fluxo contínuo, baixa aderência ao Brasil.

## Vigentes certificadas (sistema + derivadas), por prazo

| Prazo | Selo | Oportunidade | Itens que faltam | id |
|---|---|---|---|---|
| 2026-10-11 | ouro | Edital vai destinar R$ 6 milhões a projetos de proteção dos direitos de crianças ​e a | — | 97292f2d3c686703e79e |
| 2026-10-11 | prata | ContraFluxo – Chamada para organizações sociais de Curitiba (PR) que queiram transfor | Prazo de recurso | c9cef45043042a48d03c |
| 2026-10-13 | prata | Chamamento Público N° 2026.09.04.01-PMI/SMS Prefeitura Municipal de Iguatu Aceita:    | Prazo de recurso | e490bff881207038aa6e |
| 2026-10-13 17:00 | ouro | Aviso de Chamamento Público Nº 4/2026 - CRA-RS Conselho Regional de Administração do  | — | 1f91fd3af301a67d29aa |
| 2026-10-13 23:59 | ouro | MinC — Programa Rouanet nas Favelas 2 (Edital MinC nº 6/2026; até 13/10/2026 23h59; a | — | der-75df4e4b0ce4344b |
| 2026-10-14 17:00 | bronze | Aviso de Chamamento Público Nº 7/2026 Prefeitura Municipal de Itagibá Aceita:   organ | Resultado, Prazo de recurso, Valor, Requisitos, Anexos, Destinação | 16a3f1b811ac6854a526 |
| 2026-10-16 23:59 | ouro | Sobral/CE — CH26004-SEJUC Pontos de Cultura | — | der-4fc3d80a28b76cc9 |
| 2026-10-19 17:00 | prata | Programa de Aceleração do Desenvolvimento de Lideranças Femininas Negras: Marielle Fr | Resultado, Prazo de recurso | e216d467a84522d2941d |
| 2026-10-19 23:59 | ouro | Zurich Seguros abre edital nacional para apoiar projetos sociais via leis de incentiv | — | 0435170ee369be5229e7 |
| 2026-10-22 14:00 | bronze | Chamamento Público Nº 1/2026 - SMS Prefeitura Municipal de Ielmo Marinho Aceita:   or | Resultado, Prazo de recurso, Requisitos, Anexos | 26f9d179a7684e2912ad |
| 2026-10-26 08:59 | bronze | AVISO DE CHAMAMENTO PÚBLICO Nº SECULT-CP001/2026 Prefeitura Municipal de Senador Pomp | Resultado, Prazo de recurso, Requisitos, Anexos, Destinação | dced04e657964a977cad |
| 2026-10-26 09:00 | bronze | Chamamento Público nº 2/2026 — Prefeitura Municipal de Nova Independência Prefeitura  | Resultado, Prazo de recurso, Valor, Requisitos, Destinação | fda2399672da118244ba |
| 2026-10-29 | bronze | Secult Goiás lança edital para levar produção artística goiana ao Rio de Janeiro | Resultado, Prazo de recurso, Requisitos, Anexos, Destinação | 9e37b9ad76d2ce6ca86c |
| 2026-10-29 10:00 | bronze | Adustina/BA — Edital 007/2026 moeda social Adus e Banco Popular | Resultado, Prazo de recurso, Valor, Requisitos, Anexos, Destinação, Área de atuação | der-53c859108ab24c76 |
| 2026-10-30 | prata | Instituto Genésio A. Mendes abre edital de R$ 1 milhão para projetos de OSCs em Santa | Prazo de recurso | 6d06351ee0a98f70bf95 |
| 2026-10-30 | prata | CNBB lança edital do FNS para apoio financeiro a projetos relativos à Campanha da Fra | Prazo de recurso | 670a8b39181ce331da24 |
| 2026-10-30 23:59 | prata | Fundação Maria Emília abre edital com apoio de até R$ 1 milhão para projetos em saúde | Prazo de recurso | 0c3d1eb59b2a598a0393 |
| 2026-10-30 23:59 | prata | MinC — 2º Edital Cultura Viva: Fomento à Rede de Pontões de Cultura Viva (inscrições  | Resultado | der-b5acac8cc9ed4b9e |
| 2026-11-01 | prata | Karibu Foundation abre inscrições para iniciativas do Sul Global com bolsas de até US | Prazo de recurso | b2da4e4765b6602f89dd |
| 2026-11-09 | ouro | Grupo Equatorial abre chamada com mais de R$ 61 milhões para projetos de eficiência e | — | 1b259c84aabf58826786 |
| 2026-12-04 17:00 | prata | BNDES abre chamada para apoiar projetos de organizações periféricas em todo o país | Resultado, Prazo de recurso, Anexos, Destinação | 09590060f0bad9ff9a05 |
| 2026-12-04 17:00 | prata | BNDES Periferias em Rede — 6º ciclo BNDES R$ 2,0 mi Aceita:   organizações da socieda | Resultado, Prazo de recurso, Anexos, Destinação | 2f556273766464bcdc19 |
| fluxo contínuo | bronze | Apoio Emergencial: Defensores de Direitos Humanos Fundo Brasil de Direitos Humanos Ac | Resultado, Prazo de recurso, Valor, Anexos | d94cd9a3d245f2393f2f |
| fluxo contínuo | prata | ️ A Conjunta considera que este  edital  apoia o desenvolvimento institucional de  or | Prazo de recurso | fd492598a239b416cd63 |
| fluxo contínuo | bronze | Global Innovation Fund — Rolling Applications | Resultado, Prazo de recurso, Valor, Requisitos, Anexos | der-66da2534534f01a3 |
| fluxo contínuo | ouro | MinC — Edital Biblioteca Comunitária é Cultura Viva (fluxo contínuo) | — | der-d2e6bc525fb1b5a2 |

## Pendentes: motivo do bloqueio (todos pesquisados em 3 passadas)

| Oportunidade | Prazo indicado | Itens certificados | Bloqueio | id |
|---|---|---:|---|---|
| Instituto Porto abre edital de R$ 400 mil para OSCs da Grande São Paulo e Grande Belo | 2026-11-08 18:00 | 0/12 | site só em JavaScript | 8ea4ffb43db2ef33cbed |
| Sonhar o Mundo 2026 abre inscrições para instituições culturais de São Paulo | 2026-11-13 | 0/12 | bloqueio robots.txt | ecb846915cbf2b4133a5 |
| Edital Alimento no Prato oferece até R$ 800 mil para projetos de agricultura urbana | — | 11/12 | URL longa demais | 571ef6c46c40aa0bd4f7 |
| Instituto Impactarte abre edital para projetos de impacto social com apoio de até R$  | — | 1/12 | site só em JavaScript | 6e528af364033c54abd9 |
| Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão em premiação | — | 0/12 | documento oficial não localizado | 7e263d70b9cb7e81176a |
| Redion abre seleção para projetos sociais e culturais com captação via leis de incent | — | 0/12 | bloqueio robots.txt | 8dfec58a3ca3a2ebe273 |
| Aviso de Chamamento Público Nº 3/2026 - SVS/AP SUPERINTENDÊNCIA DE VIGILÂNCIA EM SAÚD | — | 0/12 | DOU bloqueado (robots.txt) | 00df21633ea2380c78fd |
| AVISO DE CHAMAMENTO PÚBLICO Nº 12/2026 - PMNF Prefeitura Municipal de Nisia Floresta  | — | 0/12 | bloqueio robots.txt | 06337d5cae56ae687b62 |
| Chamamento Público nº 0001/2026-5688 Centralizadora Nacional Contratações Aceita:   o | — | 0/12 | bloqueio robots.txt | 0fe1b4e2ffca86971609 |
| Aviso de Chamamento Público Nº 3/2026 - Prefeitura Municipal de Piranhas Prefeitura M | — | 0/12 | bloqueio robots.txt | 147b74de0a82dd4e56a0 |
| Aviso do Chamamento Público Nº 3/2026 Instituto Brasileiro do Meio Ambiente e dos Rec | 2026-10-22 23:00 | 11/12 | DOU bloqueado (robots.txt) | 1b6c6ff730a5ee203166 |
| Chamamento Público para Credenciar OSC - Organização da Sociedade Civil Prefeitura Mu | — | 5/12 | PDF do PNCP ilegível (binário) | 275bb41a215db2d707b1 |
| AVISO DE CHAMAMENTO PÚBLICO Nº 7/2026 PREFEITURA MUNICIPAL DE FRANCO DA ROCHA Aceita: | — | 0/12 | bloqueio robots.txt | 2cfccea68f7bce95ddc2 |
| Subsídio de Desenvolvimento Comunitário Inter-American Foundation R$ 2,0 mi Aceita:   | — | 0/12 | bloqueio robots.txt | 3b6fd4f16e9814286990 |
| Aviso de Chamamentos Públicos Nº 006 a 011/2026 - Prefeitura Municipal da Estância Tu | — | 0/12 | site com erro | 4d2c613d151aa95abe54 |
| Chamamento Público Nº 002/2026 - PMJF/PI Prefeitura Municipal de José de Freitas Acei | — | 0/12 | bloqueio robots.txt | 5ca5b1723af98715150b |
| Credenciamento nº 10/2026-PMSAT - Seleção de Projetos Culturais Prefeitura Municipal  | — | 0/12 | site com erro | 64efa7e36bef2f9468d1 |
| Assistência para Projetos Comunitários e de Segurança do Ser Humano (APC) Consulado G | — | 0/12 | documento oficial não localizado | 68fb8ecc9bc448f187f0 |
| Aviso de Chamamento Público nº 2/2026 – CAU/PR CONSELHO DE ARQUITETURA E URBANISMO DO | — | 0/12 | bloqueio robots.txt | 85c562bdcf9117afd466 |
| Aviso de Chamada Pública Nº CH26002 - SEJUC Prefeitura Municipal de Sobral Aceita:    | — | 0/12 | site só em JavaScript | 8792456759c9dda764ef |
| Aviso de Chamada Pública Nº 1/2026 - Prefeitura Municipal de Cajuru PREFEITURA MUNICI | — | 0/12 | DOU bloqueado (robots.txt) | 8c45db42bf2f405c282a |
| Aviso de Chamamento Público Nº 6/2026 — Prefeitura Municipal de Planaltina Prefeitura | — | 6/12 | PDF do PNCP ilegível (binário) | 8f5c1c6b7b20a61471c4 |
| Mapfre abre seleção de projetos incentivados com foco em cultura, esporte e inclusão  | — | 0/12 | site com erro | a98c4d91f7500fe564d2 |
| Aviso de Chamamento Público - Conselho Regional de Fisioterapia e Terapia Ocupacional | — | 0/12 | DOU bloqueado (robots.txt) | b24cea7e537e90571411 |
| AVISO DE CHAMAMENTO PÚBLICO Nº 3/2026 - SEJUS-PI Secretaria de Estado da Justiça R$ 8 | — | 0/12 | site só em JavaScript | c47cd9cc1dca7fbc7d41 |
| Chamamento Público Nº 6/2026 — Prefeitura Municipal de Lagoa do Ouro/PE PREFEITURA MU | 2026-10-16 14:00 | 6/12 | documento oficial não localizado | c4ac492ae88eb72517b5 |
| Aviso de Chamamento Público Nº 1/2026 - FMAS Prefeitura Municipal de Lagarto R$ 66 mi | — | 0/12 | site só em JavaScript | c5d4e471dd0651987385 |
| Aviso de Chamada Pública Nº 1/2026 Prefeitura Municipal de Divinópolis do Tocantins A | — | 0/12 | site com erro | d001939b9a108b67fc1a |
| EDITAL DE CHAMAMENTO PÚBLICO Nº 001/2026 - SEINFRA SECRETARIA MUNICIPAL DE COORDENAÇÃ | — | 0/12 | bloqueio robots.txt | d046510cd9f6ecaebe09 |
| Aviso de Chamamento Público Nº 1/2026 — Gráfica do Exército Gráfica do Exército Aceit | — | 0/12 | DOU bloqueado (robots.txt) | dbef3d06b60c0274e518 |
| Aviso de Chamamento Público Nº 3/2026 - CRA-RS Conselho Regional de Administração do  | — | 0/12 | DOU bloqueado (robots.txt) | ddd443f9ba070d9ea739 |
| Quem exatamente pode aplicar neste edital? | — | 0/12 | DOU bloqueado (robots.txt) | f7ad33f83b1880bb679f |
| Prêmio de Boas Práticas na Política Judiciária PopRuaJud | — | 0/12 | site com erro | 0376042606d6479cc32e |
| Portal Gov.br — MROSC e Parcerias | — | 0/12 | site com erro | 75051b9c0d097270f51a |
| Portal de Projetos | — | 7/12 | documento oficial não localizado | d3c748c2093127c0f2ef |
| Prêmio Academia Assaí | — | 0/12 | site com erro | 3fb88f219963db3a0799 |
| Leis de Incentivo | — | 3/12 | bloqueio robots.txt | 4183ee9e3fcea064e290 |
| Edital nº 7/2026 | — | 0/12 | DOU bloqueado (robots.txt) | c1d5199dfe1753398903 |
| Brasilcap abre edital para projetos sociais, culturais, esportivos e de saúde | — | 0/12 | site com erro | der-f5fcc1345736b991 |
| MDS — Fundo Nacional de Segurança Alimentar (editais) | — | 0/12 | site com erro | der-cbec2fa1aaaef661 |
| Lei de Incentivo ao Esporte — Ministério do Esporte | — | 5/12 | site com erro | der-593680ab049ca144 |

Bloqueios: bloqueio robots.txt: 11; site com erro: 10; DOU bloqueado (robots.txt): 8; site só em JavaScript: 5; documento oficial não localizado: 4; PDF do PNCP ilegível (binário): 2; URL longa demais: 1.
