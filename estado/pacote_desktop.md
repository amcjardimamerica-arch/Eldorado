# Pacote para o Claude Desktop — 2026-09-30

Você está no computador do titular, com IP brasileiro, navegador e o repositório Eldorado clonado. Use o modelo mais forte disponível (Opus 5) para validar. Trabalhe nesta ordem, sem pular etapa, e devolva os arquivos no formato indicado. Nunca estime datas; quando não houver base, escreva o motivo.

## Etapa 1 — motores que aguardam coleta local (portais que recusam IP estrangeiro)

Rode uma vez, na raiz do repositório:

```
python scripts/coleta_brasil.py
```

Ele lê com o seu IP e envia ao repositório. Motores atendidos:
- **Diário Oficial do Município de Goiânia** — rotas: Diário Oficial do Município (edição do dia); SEMASDH — Fundo Municipal de Assistência Social e chamamentos; Secretaria Municipal de Cultura — editais

## Etapa 2 — motores em alerta (não leram, falharam ou passaram da cadência)

- **Editais incentivados — sites das maiores contribuintes do ICMS de Goiás (destinação tributária)** — 3 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://observatorio3setor.org.br/editais/ e procurar: edital, seleção de projetos, investimento social, responsabilidade social, patrocínio, incentivo fiscal

Para cada rota aberta, liste os editais publicados nos últimos 30 dias que casem com o léxico e que ainda não estejam em `dados/editais/`. Devolva em `dados/editais/coleta_navegador/<data>-motores.json` no formato `{"<id ou novo>": {"objeto":..., "inicio":..., "fim":..., "pagina_oficial":..., "observacao":...}}`.

## Etapa 3 — oportunidades aguardando ação externa (21)

- `3f4e0f749a5a6e40f2c4` — Edital prevê seleção de 58 apresentações artísticas para o Natal do Bem 2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/edital-preve-selecao-de-58-apresentacoes-artisticas-para-o-natal-do-bem-2026
- `4d519a11c8b5c23bd8d5` — Termo de Fomento nº 01/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/06/SEI_90351764_Termo_de_Fomento_1.pdf
- `ee794628b50b5fde65f0` — Secult Goiás retifica cronograma do edital de apresentações artísticas para o Natal do Bem · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/secult-goias-retifica-cronograma-do-edital-de-apresentacoes-artisticas-para-o-natal-do-bem-2026
- `9e37b9ad76d2ce6ca86c` — Secult Goiás lança edital para levar produção artística goiana ao Rio de Janeiro · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/secult-goias-lanca-edital-para-levar-producao-artistica-goiana-ao-rio-de-janeiro
- `bed7b83e02d2e24a00a5` — Divulgado resultado preliminar do edital de apresentações artísticas para o Natal do Bem 2 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/divulgado-resultado-preliminar-do-edital-de-apresentacoes-artisticas-para-o-natal-do-bem-2026
- `39e8067201494d565881` — EDITAL PPGFIL/IFILO/UFU Nº 1/2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-ppgfil/ifilo/ufu-n-1/2026-733304995
- `0fc96da3bfa4c9659ef3` — Secretaria de Fomento e Incentivo à Cultura · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.gov.br/cultura/pt-br/composicao/secretaria-de-economia-criativa-e-fomento-cultural
- `bdea428602f61e41e70b` — Edital recebe 851 inscrições! · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://climaesociedade.org/ics-lanca-edital-para-projetos-de-comunicacao-com-acoes-de-enfrentamento-as-mudancas-climaticas
- `575706d9ad755cd36a5d` — EXTRATO DE TERMO DE FOMENTO Nº 997181/2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/extrato-de-termo-de-fomento-n-997181/2026-733920831
- `9107398972ccec107a35` — EDITAL DE INTIMAÇÃO · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-de-intimacao-733801219
- `c1d5199dfe1753398903` — Edital nº 7/2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-n-7/2026-723987102
- `ca24a73387bc378e278a` — EXTRATO DE TERMO DE FOMENTO · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/extrato-de-termo-de-fomento-734970912
- `647bacd91908be74d5ff` — EXTRATO DE TERMO DE FOMENTO · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/extrato-de-termo-de-fomento-735327825
- `dad0d1baa214f9ba880a` — EXTRATO DE TERMO DE FOMENTO · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/extrato-de-termo-de-fomento-735200691
- `400d80f3c84332f2aa0c` — EDITAL DE Nº 126/IFAL, DE 18 DE SETEMBRO DE 2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-de-n-126/ifal-de-18-de-setembro-de-2026-733048195
- `645f8bc3798ac55c4cfe` — Celebração de Termo de Colaboração para a consecução de finalidade de interesse público de · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://pncp.gov.br/app/editais/13646005000138/2024/44
- `f733cd0539057acbdcbe` — A referente requisição se faz para abertura de edital de chamamento público , para contrat · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://pncp.gov.br/app/editais/88775390000112/2023/99
- `5b1f86e6fc0993dabf5b` — Edital Natal do Bem · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://goias.gov.br/cultura/pnab/edital-2026-pnab
- `61208c62e6d5fade40d4` — Política Nacional Aldir Blanc de Fomento à Cultura · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://www.gov.br/cultura/pt-br/acesso-a-informacao/perguntas-frequentes/politica-nacional-aldir-blanc
- `8c25b367f7f8300e0b0f` — Política Nacional Aldir Blanc de Fomento à Cultura · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/politica-nacional-aldir-blanc-de-fomento-a-cultura
- `9a3b706226b8076711a1` — 17 Set.   10:30 
       
     
     Nova legislação altera política de fomento à IA para f · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://portal.al.go.leg.br/noticias/167376/nova-legislacao-altera-politica-de-fomento-a-ia-para-fortalecer-gestao-publica-e-pesquisa-alem-de-instituir-premiacao-na-area

## Etapa 4 — oportunidades parciais do modo completo, para validar com Opus 5 (40)

Para cada uma, abra a página oficial (nunca PNCP, diário ou portal de notícia; exceção: o arquivo do edital do órgão hospedado no PNCP, em `/arquivos/`), extraia OBJETO, PRAZO (início e fim) e URL oficial, e dê o veredito: aprovado (chamada aberta de fomento a OSC), atenção (serve, mas o enquadramento exige conferência) ou reprovado (com a família: resultado de edital, seleção de empresa, serviço ao órgão, qualificação como OS, órgão buscando patrocinador, parceria já celebrada).

- `8dfec58a3ca3a2ebe273` — Redion abre seleção para projetos sociais e culturais com captação via leis de incentivo · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/redion-abre-selecao-para-projetos-sociais-e-culturais-com-captacao-via-leis-de-incentivo
- `16bc790ac60fa10b46cd` — Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão em premiação · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/premio-led-globo-2027-abre-inscricoes-com-r-12-milhao-em-premiacao
- `571ef6c46c40aa0bd4f7` — Edital Alimento no Prato oferece até R$ 800 mil para projetos de agricultura urbana · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/edital-alimento-no-prato-oferece-ate-r-800-mil-para-projetos-de-agricultura-urbana
- `9029f6fd301f56924784` — Continue lendo Fundação Maria Emília abre edital com apoio de até R$ 1 milhão para projeto · falta: Objeto, Prazo de inscrição · https://captadores.org.br/editais/fundacao-maria-emilia-abre-edital-com-apoio-de-ate-r-1-milhao-para-projetos-em-saude-e-educacao
- `36052154d2c76c2ace4d` — EDITAL  001/ 2026  - FUNDO SEMENTE PARA RESILIÊNCIA - PARCEIROS VOLUNTÁRIOS SELEÇÃO DE PRO · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fparceirosvoluntarios.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F04%2FEdital%2D001%2D2026.pdf&rut=1cfe90e819e5c912f0a330beec5f4074b788278c1f28e9fee854bde88a861b51
- `550cbdfbd19f8fd24255` — parceirosvoluntarios.org.br/wp-content/uploads/2026/01/Edital-Programa-Impulsionar-2026.pd · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fparceirosvoluntarios.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F01%2FEdital%2DPrograma%2DImpulsionar%2D2026.pdf&rut=852f790f09b78e7e1aa15028160c0809e9fef6b21a7c3b7e4344ba80b48baa7f
- `5c160659318718cf372c` — O UNAIDS publicou  edital  para seleção de  Organizações   da   Sociedade   Civil  para de · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fbrasil.un.org%2Fpt%2Dbr%2F308564%2Dunaids%2De%2Dminist%25C3%25A9rio%2Dda%2Dsa%25C3%25BAde%2Dabrem%2Dsele%25C3%25A7%25C3%25A3o%2Dde%2Dorganiza%25C3%25A7%25C3%25B5es%2Dda%2Dsociedade%2Dcivil%2Dvoltadas%2Da%25C3%25A7%25C3%25B5es&rut=f376926901a1143983b9c627e63707827d4de7dc37bb70ceb0cda3c12b0de420
- `96b662e92919f9080d77` — Explore  editais  públicos e privados abertos para ONGs, projetos sociais, cultura, educaç · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Falteditais.com.br%2Foportunidades&rut=43ad733171887d6d32987d39ba0382c32a1be397b4c0bf559a3431bef529cd04
- `cb12fd7ab9600a4cec12` — Edital  para Seleção de  Organizações   da   Sociedade   Civil  para o Desenvolvimento de  · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Funaids.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F01%2F2026_Edital_UNAIDS_DATHI_Sociedade_Civil.pdf&rut=72de7c14c56224031c1bfffe6714e1c30cd81007daf1a909b5dd17abf9c1e0e6
- `e0372d60014c5c6d46be` — O  Edital  nº 7/2026 tem como objetivo selecionar  organizações   da   sociedade   civil   · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fwww.gov.br%2Fmulheres%2Fpt%2Dbr%2Facesso%2Da%2Dinformacao%2Feditais%2F2026%2Fedital%2Dno%2D7%2D2026%2Dselecao%2Dde%2Dorganizacoes%2Dda%2Dsociedade%2Dcivil%2Dpara%2Dcomposicao%2Ddo%2Dforum%2Dnacional%2Dpelo%2Dprotagonismo%2Ddas%2Dmulheres%2Didosas&rut=a2b32931f929949207cc0d25c6d1f32b815f187877fe8988906708bce9601b87
- `f2a7f6ce188bcc297d5c` — Os  editais  aqui disponibilizados são oportunidades voltadas ao desenvolvimento instituci · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fwww.itausocial.org.br%2Feditais%2F&rut=178675466b10ac3a74943b9cd2117d86099f5bbc5e0471269afd1890a45a6b10
- `3186c66b3eea66113826` — Parque Bondinho Pão de Açúcar abre edital para projetos culturais incentivados Iniciativas · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fobservatorio3setor.org.br%2Fsecoes_tematicas%2Feditais%2F&rut=71e76025cf29251e29b331a6fd2f94e7215aff028875a7f549e64f491361f1f3
- `50a1c1b837c01e854607` — Explore  editais  públicos e privados abertos para ONGs, projetos sociais, cultura, educaç · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Falteditais.com.br%2Foportunidades&rut=354178836f862682b94f171188dede4fcfb28bf24338f564e67873af2327a698
- `8993bf97c9f30b0693b8` — Edital  para Seleção de  Organizações   da   Sociedade   Civil  para o Desenvolvimento de  · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Funaids.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F01%2F2026_Edital_UNAIDS_DATHI_Sociedade_Civil.pdf&rut=0c3d849f487e52ade729eccb3e795d1c962c3111ccdeae0fa58e486dd8f888f1
- `8a6b25cb0d7024bad623` — O UNAIDS publicou  edital  para seleção de  Organizações   da   Sociedade   Civil  para de · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fbrasil.un.org%2Fpt%2Dbr%2F308564%2Dunaids%2De%2Dminist%25C3%25A9rio%2Dda%2Dsa%25C3%25BAde%2Dabrem%2Dsele%25C3%25A7%25C3%25A3o%2Dde%2Dorganiza%25C3%25A7%25C3%25B5es%2Dda%2Dsociedade%2Dcivil%2Dvoltadas%2Da%25C3%25A7%25C3%25B5es&rut=89173c11252d4918b33561b96a3a2cff1ea3644f7114677d14a8be37a203d3d9
- `e8978d129f2f0e1aaa8e` — O  Edital  nº 7/2026 tem como objetivo selecionar  organizações   da   sociedade   civil   · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fwww.gov.br%2Fmulheres%2Fpt%2Dbr%2Facesso%2Da%2Dinformacao%2Feditais%2F2026%2Fedital%2Dno%2D7%2D2026%2Dselecao%2Dde%2Dorganizacoes%2Dda%2Dsociedade%2Dcivil%2Dpara%2Dcomposicao%2Ddo%2Dforum%2Dnacional%2Dpelo%2Dprotagonismo%2Ddas%2Dmulheres%2Didosas&rut=b344638a7913779ead02f3b7baf2d15fc7867709341dc505efe63441381a5b12
- `2a2723c82124d864056f` — EDITAL  001/ 2026  - FUNDO SEMENTE PARA RESILIÊNCIA - PARCEIROS VOLUNTÁRIOS SELEÇÃO DE PRO · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fparceirosvoluntarios.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F04%2FEdital%2D001%2D2026.pdf&rut=9f8dc4d175cc76dfd812fc5d4cdb8a704b49ac4ba23be048793d36ef34d3093f
- `2df87928ba6acc971bd6` — Explore  editais  públicos e privados abertos para ONGs, projetos sociais, cultura, educaç · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Falteditais.com.br%2Foportunidades&rut=a069c4469af36c24615b3612103395a0bb8b66e183c977ae0e55ac6a30f7576b
- `3d574c9d2f1a4fc94f58` — Edital  para Seleção de  Organizações   da   Sociedade   Civil  para o Desenvolvimento de  · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Funaids.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F01%2F2026_Edital_UNAIDS_DATHI_Sociedade_Civil.pdf&rut=9a127a288a095dd335564a77dd360d044756408638eb2505a37a52ccf9c59569
- `575706d9ad755cd36a5d` — EXTRATO DE TERMO DE FOMENTO Nº 997181/2026 · falta: Objeto, Prazo de inscrição, Página oficial do edital
- `7865f403fa2643571d52` — Edital Conta que soma oferece formação gratuita em educação financeira para jovens Co.liga · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fobservatorio3setor.org.br%2Fsecoes_tematicas%2Feditais%2F&rut=eebcd1002a59143e482e3f14690c6d8ab3b35713f1479e9e052b6e891f40de9d
- `8b30dc287d0d7fd64f11` — O UNAIDS publicou  edital  para seleção de  Organizações   da   Sociedade   Civil  para de · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fbrasil.un.org%2Fpt%2Dbr%2F308564%2Dunaids%2De%2Dminist%25C3%25A9rio%2Dda%2Dsa%25C3%25BAde%2Dabrem%2Dsele%25C3%25A7%25C3%25A3o%2Dde%2Dorganiza%25C3%25A7%25C3%25B5es%2Dda%2Dsociedade%2Dcivil%2Dvoltadas%2Da%25C3%25A7%25C3%25B5es&rut=8dfb580804c8cdaeb796de8e54e49ee673b29666479d19272d62d881f397a725
- `8b92b32544c0c751693e` — Chamada Pública Nº  2026 .08.14.01 - Execução compartilhada de ações e serviços de apoio e · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fcapitaai.com.br%2Feditais%2Dabertos%2Fassistencia%2Dsocial%2Dpara%2Dong&rut=3710f7ce81fa053c63c96a6f113899e2f81cc3f2a05ad0bda0f6a529219f5064
- `a3480fa251b601ff3acc` — Edital  de Seleção Pública de Projetos  2026  do Fundo Positivo - O Fundo Positivo, em par · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fgife.org.br%2Fconfira%2Da%2Dselecao%2Dde%2Deditais%2Dcom%2Dinscricoes%2Dabertas%2Dneste%2Dinicio%2Dde%2Dano%2F&rut=ba06a35c3c324786627a851f5adae9dcf3bba62ced2a860561915b567e319960
- `afcede931887dff01827` — O  Edital  nº 7/2026 tem como objetivo selecionar  organizações   da   sociedade   civil   · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fwww.gov.br%2Fmulheres%2Fpt%2Dbr%2Facesso%2Da%2Dinformacao%2Feditais%2F2026%2Fedital%2Dno%2D7%2D2026%2Dselecao%2Dde%2Dorganizacoes%2Dda%2Dsociedade%2Dcivil%2Dpara%2Dcomposicao%2Ddo%2Dforum%2Dnacional%2Dpelo%2Dprotagonismo%2Ddas%2Dmulheres%2Didosas&rut=f6218d317ae4271294cf735463967dc351151cf41a3ea3c73a2a156499caa7cd
- `b9a2bf6d5d2277c9d3f7` — sfo3.digitaloceanspaces.com/iweventos/imagens/ccm/2026-06/EDITAL_ONGS_CONGRESSO_SBOC_2026. · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fsfo3.digitaloceanspaces.com%2Fiweventos%2Fimagens%2Fccm%2F2026%2D06%2FEDITAL_ONGS_CONGRESSO_SBOC_2026.pdf&rut=67a92b9c048b72fbcea6a5080e35fc9a4af33186f6d33b6e7b7dc58f86be791c
- `cf0decbc589a29f50925` — Edital  nº. 4/2026 - Processo de chamamento público para eleição de  organizações   da   s · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fwww.gov.br%2Fmdh%2Fpt%2Dbr%2Fnavegue%2Dpor%2Dtemas%2Fparticipacao%2Dsocial%2Feditais&rut=5c647477f5cae553c847b300371447d660d3172f4262cb90c97c14e6630155c6
- `d299704ec5532fe201b9` — Parque Bondinho Pão de Açúcar abre edital para projetos culturais incentivados · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/parque-bondinho-pao-de-acucar-abre-edital-para-projetos-culturais-incentivados
- `affe8468951e01850caa` — Pnab 2026: Resultado da 2ª Fase de Heteroidentificação dos Editais · falta: Objeto, Prazo de inscrição · https://goias.gov.br/cultura/pnab-2026-resultado-da-2a-fase-de-heteroidentificacao-dos-editais
- `0fe1b4e2ffca86971609` — Chamamento Público nº 0001/2026-5688 Centralizadora Nacional Contratações Aceita:   organi · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/chamamento-publico-000120265688-centralizadora-nacional-contratacoes-vribf3
- `26e43476f2b0bf81352e` — O  edital  estabelece critérios para a seleção de projetos de  organizações   da   socieda · falta: Objeto, Prazo de inscrição · https://www.gov.br/mulheres/pt-br/acesso-a-informacao/editais/2026/edital-justica-climatica
- `66463f6465f409b34cea` — Edital de Projetos Fundação APERAM ACESITA – Social 15ª Edição Fundação APERAM ACESITA R$  · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/edital-projetos-fundacao-aperam-acesita-social-edicao-fundacao-p5hvyn
- `82ebd33966b7ae1de389` — Ambev abre edital de até R$ 67 milhões para projetos culturais e esportivos em todo o Bras · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/ambev-abre-edital-ate-milhoes-projetos-culturais-esportivos-biwuta
- `8792456759c9dda764ef` — Aviso de Chamada Pública Nº CH26002 - SEJUC Prefeitura Municipal de Sobral Aceita:   organ · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/aviso-chamada-publica-ch26002-sejuc-prefeitura-municipal-sobral-1uck7c
- `c9cef45043042a48d03c` — ContraFluxo – Chamada para organizações sociais de Curitiba (PR) que queiram transformar u · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/contrafluxo-abre-chamada-organizacoes-sociais-curitiba-que-queiram-1kt0lj
- `ca24a73387bc378e278a` — EXTRATO DE TERMO DE FOMENTO · falta: Objeto, Prazo de inscrição, Página oficial do edital
- `d8a4963b33b40f02f011` — Chamada Pública Nº 2026.08.14.01 - Execução compartilhada de ações e serviços de apoio e m · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/chamada-publica-2026081401-execucao-compartilhada-acoes-servicos-apoio-txuoet
- `d94cd9a3d245f2393f2f` — Apoio Emergencial: Defensores de Direitos Humanos Fundo Brasil de Direitos Humanos Aceita: · falta: Objeto, Prazo de inscrição · https://capitaai.com.br/captacao/apoio-emergencial-defensores-direitos-humanos-fundo-brasil-direitos-ppj1gw
- `647bacd91908be74d5ff` — EXTRATO DE TERMO DE FOMENTO · falta: Objeto, Prazo de inscrição, Página oficial do edital
- `dad0d1baa214f9ba880a` — EXTRATO DE TERMO DE FOMENTO · falta: Objeto, Prazo de inscrição, Página oficial do edital

## Etapa 4½ — IA local (organização automática, sem gastar Claude)

Se a pasta `ia_local/` ainda não existe: `python scripts/ia_local_instalar.py` (uma vez, ~2 GB; `--leve` para 1 GB).
Suba o servidor local (`ia_local/iniciar.bat` ou `.sh`, deixe a janela aberta) e rode:

```
python -m src.ia_local ciclo      # classifica os incompletos, extrai objeto/prazo com trecho literal, propõe léxico, diagnostica motores 'lendo sem achar'
python -m src.ia_local aplicar    # grava só o que passou na validação — como PROPOSTA, nunca sobrescrevendo dado confirmado
```

As sugestões de rota ficam em `estado/rotas_sugeridas_ia.json` com status 'a confirmar pelo titular'; as extrações entram em `proposta_ia` no registro para o Opus 5 validar na Etapa 4.

## Etapa 5 — fechar o ciclo

```
python -m src.enquadramento ingerir_navegador
python -m src.enquadramento
python -m src.enquadramento fila
python -m src.alerta_motores
python -m src.auditoria_motores
python -m src.dashboard_dados
python -m unittest tests.test_system  # só siga com tudo verde
python scripts/verificar_privacidade.py
git add -A && git commit -m "desktop: complementacao <data>" && git pull --rebase origin main && git push
```

## Resumo final que você deve me dar

Quantos motores voltaram a ler, quantas oportunidades foram completadas, quantas não eram editais, quais sites não abriram — e o que ficou para o titular decidir.