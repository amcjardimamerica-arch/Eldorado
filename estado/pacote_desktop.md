# Pacote para o Claude Desktop — 2026-09-20

Você está no computador do titular, com IP brasileiro, navegador e o repositório Eldorado clonado. Use o modelo mais forte disponível (Opus 5) para validar. Trabalhe nesta ordem, sem pular etapa, e devolva os arquivos no formato indicado. Nunca estime datas; quando não houver base, escreva o motivo.

## Etapa 1 — motores que aguardam coleta local (portais que recusam IP estrangeiro)

Rode uma vez, na raiz do repositório:

```
python scripts/coleta_brasil.py
```

Ele lê com o seu IP e envia ao repositório. Motores atendidos:
- **Diário Oficial do Município de Goiânia** — rotas: Diário Oficial do Município (edição do dia); SEMASDH — Fundo Municipal de Assistência Social e chamamentos; Secretaria Municipal de Cultura — editais
- **Diário Oficial do Estado de Goiás** — rotas: Diário Oficial do Estado (ABC); SECULT-GO — Chamamentos Públicos; SEDS — Goiás Social e cofinanciamento

## Etapa 2 — motores em alerta (não leram, falharam ou passaram da cadência)

- **ABCR — Associação Brasileira de Captadores** — 14 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://captadores.org.br/editais/ e procurar: edital, chamada, seleção, inscrições, até R$, OSCs
- **CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://www.gov.br/cnpq/pt-br/acesso-a-informacao/acoes-e-programas/programas/chamadas-publicas e procurar: chamada pública, extensão, popularização da ciência, inovação social, parceria, organizações da sociedade civil
    - abrir https://www.gov.br/mcti/pt-br e procurar: chamada pública, extensão, popularização da ciência, inovação social, parceria, organizações da sociedade civil
    - abrir https://www.gov.br/mec/pt-br/acesso-a-informacao/institucional/secretarias/secretaria-de-educacao-profissional-e-tecnologica e procurar: chamada pública, extensão, popularização da ciência, inovação social, parceria, organizações da sociedade civil
- **Editais de empresas incentivadoras (modelo Porto Itapoá) — FIA, Idoso, Esporte, Rouanet, PRONAS** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://captadores.org.br/editais/ e procurar: edital, projetos incentivados, seleção de projetos, FIA, Fundo do Idoso, Lei de Incentivo ao Esporte
- **FAPEG — Fundação de Amparo à Pesquisa de Goiás** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://goias.gov.br/fapeg/ e procurar: chamada pública, extensão, inovação social, popularização da ciência, parceria com organizações, edital
    - abrir https://diariooficial.abc.go.gov.br/ e procurar: chamada pública, extensão, inovação social, popularização da ciência, parceria com organizações, edital
- **Fundos estaduais de Goiás com conselho — FIA, Idoso, FUNJUVE, Meio Ambiente** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://goias.gov.br/desenvolvimento-social/ e procurar: FIA, Fundo da Infância, Fundo do Idoso, FUNJUVE, FEMA, resolução
    - abrir https://goias.gov.br/desenvolvimento-social/ e procurar: FIA, Fundo da Infância, Fundo do Idoso, FUNJUVE, FEMA, resolução
    - abrir https://goias.gov.br/meioambiente/ e procurar: FIA, Fundo da Infância, Fundo do Idoso, FUNJUVE, FEMA, resolução
- **GIFE — Grupo de Institutos, Fundações e Empresas** — 14 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://gife.org.br/agenda/ e procurar: edital, chamada, seleção de projetos, inscrições, instituto, fundação
    - abrir https://gife.org.br/associados/ e procurar: edital, chamada, seleção de projetos, inscrições, instituto, fundação
- **Goiás Social — programas e editais para entidades** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://goias.gov.br/social/ e procurar: Auxílio Nutricional, cofinanciamento, edital, chamamento, entidades filantrópicas, assistência social
    - abrir https://goias.gov.br/desenvolvimento-social/ e procurar: Auxílio Nutricional, cofinanciamento, edital, chamamento, entidades filantrópicas, assistência social
- **Ministérios Públicos — editais de destinação de recursos de reparação e bens lesados** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://www.mpgo.mp.br/ e procurar: edital de destinação, destinação de recursos, TAC, termo de ajustamento, reparação, bens lesados
    - abrir https://www.mpf.mp.br/ e procurar: edital de destinação, destinação de recursos, TAC, termo de ajustamento, reparação, bens lesados
    - abrir https://www.prt18.mpt.mp.br/ e procurar: edital de destinação, destinação de recursos, TAC, termo de ajustamento, reparação, bens lesados
- **Observatório do Terceiro Setor — editais** — 14 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://observatorio3setor.org.br/editais/ e procurar: abre edital, abre inscrições, seleção de projetos, chamada, até R$, para organizações
- **OVG — Organização das Voluntárias de Goiás: editais e chamamentos** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://www.ovg.org.br/ e procurar: edital, chamamento, credenciamento de entidades, entidades parceiras, Mais Social, cofinanciamento
    - abrir https://www.ovg.org.br/editais e procurar: edital, chamamento, credenciamento de entidades, entidades parceiras, Mais Social, cofinanciamento
    - abrir https://goias.gov.br/social/ e procurar: edital, chamamento, credenciamento de entidades, entidades parceiras, Mais Social, cofinanciamento
- **Prefeituras das 50 maiores cidades de Goiás — portais de editais** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://queridodiario.ok.org.br/ e procurar: chamamento público, termo de fomento, termo de colaboração, edital de seleção, organizações da sociedade civil, fundo municipal
    - abrir https://pncp.gov.br/ e procurar: chamamento público, termo de fomento, termo de colaboração, edital de seleção, organizações da sociedade civil, fundo municipal
- **Prosas — editais para o terceiro setor** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://prosas.com.br/editais e procurar: edital, inscrições abertas, seleção, até, R$, organizações
- **Prosas — prêmios, concursos e cursos para OSCs** — 14 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://prosas.com.br/editais?natureza=premio e procurar: prêmio, concurso, reconhecimento, organizações, iniciativas sociais, inscrições
- **SALIC — Lei Rouanet (Ministério da Cultura)** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet e procurar: Lei Rouanet, PRONAC, Salic, proposta cultural, incentivo fiscal, mecenato
    - abrir https://salic.cultura.gov.br/ e procurar: Lei Rouanet, PRONAC, Salic, proposta cultural, incentivo fiscal, mecenato
    - abrir https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet/legislacao e procurar: Lei Rouanet, PRONAC, Salic, proposta cultural, incentivo fiscal, mecenato
- **Secult Goiás — Goyazes e Aldir Blanc** — nunca rodou. Ação: conferir se o sensor está na escala; se for novo, esperar a próxima saída.
    - abrir https://goias.gov.br/cultura/chamamentos-publicos-2026/ e procurar: chamamento público, edital, PNAB, Goyazes, Fundo de Arte e Cultura, Lei Paulo Gustavo
    - abrir https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/ e procurar: chamamento público, edital, PNAB, Goyazes, Fundo de Arte e Cultura, Lei Paulo Gustavo
    - abrir https://pnab.cultura.go.gov.br e procurar: chamamento público, edital, PNAB, Goyazes, Fundo de Arte e Cultura, Lei Paulo Gustavo
- **Editais incentivados — sites das maiores contribuintes do ICMS de Goiás (destinação tributária)** — 2 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://observatorio3setor.org.br/editais/ e procurar: edital, seleção de projetos, investimento social, responsabilidade social, patrocínio, incentivo fiscal

Para cada rota aberta, liste os editais publicados nos últimos 30 dias que casem com o léxico e que ainda não estejam em `dados/editais/`. Devolva em `dados/editais/coleta_navegador/<data>-motores.json` no formato `{"<id ou novo>": {"objeto":..., "inicio":..., "fim":..., "pagina_oficial":..., "observacao":...}}`.

## Etapa 3 — oportunidades aguardando ação externa (2)

- `f733cd0539057acbdcbe` — A referente requisição se faz para abertura de edital de chamamento público , para contrat · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://pncp.gov.br/app/editais/88775390000112/2023/99
- `9a3b706226b8076711a1` — 17 Set.   10:30 
       
     
     Nova legislação altera política de fomento à IA para f · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://portal.al.go.leg.br/noticias/167376/nova-legislacao-altera-politica-de-fomento-a-ia-para-fortalecer-gestao-publica-e-pesquisa-alem-de-instituir-premiacao-na-area

## Etapa 4 — oportunidades parciais do modo completo, para validar com Opus 5 (38)

Para cada uma, abra a página oficial (nunca PNCP, diário ou portal de notícia; exceção: o arquivo do edital do órgão hospedado no PNCP, em `/arquivos/`), extraia OBJETO, PRAZO (início e fim) e URL oficial, e dê o veredito: aprovado (chamada aberta de fomento a OSC), atenção (serve, mas o enquadramento exige conferência) ou reprovado (com a família: resultado de edital, seleção de empresa, serviço ao órgão, qualificação como OS, órgão buscando patrocinador, parceria já celebrada).

- `8dfec58a3ca3a2ebe273` — Redion abre seleção para projetos sociais e culturais com captação via leis de incentivo · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/redion-abre-selecao-para-projetos-sociais-e-culturais-com-captacao-via-leis-de-incentivo
- `9a766d6157f999488d58` — Clima na Economia: integrando a questão climática à agenda econômica · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/edital/clima-na-economia-integrando-a-questao-climatica-a-agenda-economica
- `e5fe7f2125dac11f0d23` — Comunicação para Ação Climática no Brasil · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/edital/comunicacao-para-acao-climatica-no-brasil
- `4494396747d696db5a9b` — Médicos Sem Fronteiras abre vaga para Pessoa Captadora de Recursos no Rio de Janeiro · falta: Objeto, Prazo de inscrição · https://captadores.org.br/vagas/medicos-sem-fronteiras-abre-vaga-para-pessoa-captadora-de-recursos-no-rio-de-janeiro
- `0b74c8f7131e75e09a15` — Captação de Recursos · falta: Objeto, Prazo de inscrição · https://captadores.org.br/captacao-de-recursos
- `1a298f0b5d7cbe0b2d76` — Certificadora Social · falta: Objeto, Prazo de inscrição · https://captadores.org.br/certificadora-social
- `2df7efe2328e78c1df66` — Bússola Investimento Social · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/investidores-sociais
- `5b0575f3f6f5ab2aea82` — Bússola Gestão · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/bussola-gestao
- `6ace1b0d40a5cca52c51` — Bússola Financeiro · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/bussola-financeiro
- `616661aee9a7bc91e944` — Doação e projetos sociais · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/doacao-e-projetos-sociais
- `281b8ce0f96a2b9219a9` — Curso gratuito vai apoiar organizações de base na mobilização da generosidade local · falta: Objeto, Prazo de inscrição · https://captadores.org.br/noticias/curso-gratuito-vai-apoiar-organizacoes-de-base-na-mobilizacao-da-generosidade-local
- `d118fef09161e9e8e0c7` — WoMakersCode abre vaga para Captadora de Recursos · falta: Objeto, Prazo de inscrição · https://captadores.org.br/vagas/womakerscode-abre-vaga-para-captadora-de-recursos
- `d89282fe7b230341381a` — Casa dos Curumins abre vaga para Especialista em Captação de Recursos · falta: Objeto, Prazo de inscrição · https://captadores.org.br/vagas/casa-dos-curumins-abre-vaga-para-especialista-em-captacao-de-recursos
- `1f9233fbd12b1abd9cde` — ACTC – Casa do Coração abre vaga para Assistente Pleno de Captação de Recursos · falta: Objeto, Prazo de inscrição · https://captadores.org.br/vagas/actc-casa-do-coracao-abre-vaga-para-assistente-pleno-de-captacao-de-recursos
- `93509f326fb7440b52cd` — FIFE 2027 abre chamada para seleção de palestrantes · falta: Objeto, Prazo de inscrição · https://captadores.org.br/noticias/fife-2027-abre-chamada-para-selecao-de-palestrantes
- `f9cfc877a0b16b7beda9` — Quatro iniciativas vencem premiação do CNJ em gestão de pessoas do Judiciário · falta: Objeto, Prazo de inscrição · https://www.cnj.jus.br/quatro-iniciativas-vencem-premiacao-do-cnj-em-gestao-de-pessoas-do-judiciario
- `0fd16ad50306fbb939f0` — Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão em premiação · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/premio-led-globo-2027-abre-inscricoes-com-r-12-milhao-em-premiacao
- `9a3b706226b8076711a1` — 17 Set.   10:30 
       
     
     Nova legislação altera política de fomento à IA para f · falta: Objeto, Prazo de inscrição · https://portal.al.go.leg.br/noticias/167376/nova-legislacao-altera-politica-de-fomento-a-ia-para-fortalecer-gestao-publica-e-pesquisa-alem-de-instituir-premiacao-na-area
- `07d250556cee3a6b1f93` — ContraFluxo abre chamada para organizações sociais de Curitiba (PR) que queiram transforma · falta: Objeto, Prazo de inscrição · https://captadores.org.br/editais/contrafluxo-abre-chamada-para-organizacoes-sociais-de-curitiba-pr-que-queiram-transformar-uma-causa-em-filme
- `43992592b6d5e37dd9f3` — Associados da ABCR têm 30% de desconto na inscrição para o CAPTA 2026 · falta: Objeto, Prazo de inscrição · https://captadores.org.br/noticias/associados-da-abcr-tem-30-de-desconto-na-inscricao-para-o-capta-2026
- `c5be5b3ffd220f988d84` — 15:32 
                   
                   Requerimentos, títulos de cidadania e utilid · falta: Objeto, Prazo de inscrição · https://portal.al.go.leg.br/noticias/167417/requerimentos-titulos-de-cidadania-e-utilidades-publicas-sao-aprovados-em-bloco
- `0ee697c3bdecafcc0eff` — 15:19 
                   
                   Votações conjuntas validam requerimentos e d · falta: Objeto, Prazo de inscrição · https://portal.al.go.leg.br/noticias/167392/votacoes-conjuntas-validam-requerimentos-e-declaracoes-de-utilidade-publica
- `fde0308aee36cf7d4e68` — 10:30 
                   
                   Nova legislação altera política de fomento à · falta: Objeto, Prazo de inscrição · https://portal.al.go.leg.br/noticias/167376/nova-legislacao-altera-politica-de-fomento-a-ia-para-fortalecer-gestao-publica-e-pesquisa-alem-de-instituir-premiacao-na-area
- `3dc97bcded767d8821fb` — Patrocínio a projetos culturais · falta: Prazo de inscrição · https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios/patrocinio-a-eventos-culturais
- `0376042606d6479cc32e` — Prêmio de Boas Práticas na Política Judiciária PopRuaJud · falta: Prazo de inscrição · https://www.cnj.jus.br/programas-e-acoes/direitos-humanos/politica-nacional-de-atencao-as-pessoas-em-situacao-de-rua-e-suas-interseccionalidades/premio-de-boas-praticas-na-politica-judiciaria-popruajud/ii-premio-da-politica-judiciaria-popruajud/
- `674ef20921aacd611cf1` — Patrocínio a projetos culturais · falta: Prazo de inscrição · https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios/patrocinio-a-eventos-culturais
- `95c61dfd946ec5a96c3f` — Pnab 2026: Divulgada lista de aprovados e suplentes do Edital de Infância e Juventude na C · falta: Prazo de inscrição · https://goias.gov.br/cultura/
- `ad1dc41c5c10b2561626` — Edital Natal do Bem · falta: Prazo de inscrição · https://www.goias.gov.br/cultura/pnab/edital-2026-pnab/
- `0eac700d7cb170ff96b1` — Instituto Impactarte abre edital para projetos de impacto social com apoio de até R$ 150 m · falta: Prazo de inscrição · https://impactarte.com.br
- `6e528af364033c54abd9` — Instituto Impactarte abre edital para projetos de impacto social com apoio de até R$ 150 m · falta: Prazo de inscrição · https://impactarte.com.br
- `305f369c623c92423e86` — Atenção à Saúde · falta: Prazo de inscrição · https://goias.gov.br/saude/atencao-a-saude/
- `6a6c37dcb037c09baa6c` — Pnab 2026: Divulgada lista de aprovados e suplentes do Edital de Infância e Juventude na C · falta: Prazo de inscrição · https://goias.gov.br/cultura/pnab-2026-divulgada-lista-de-aprovados-e-suplentes-do-edital-de-infancia-e-juventude-na-cultura
- `db0bf83f4df2fe2c618a` — PNAB 2026: Retificado cronograma dos editais nº 12, 13 e 14/2026 · falta: Prazo de inscrição · https://goias.gov.br/cultura/pnab-2026-retificado-cronograma-dos-editais-no-12-13-e-14-2026
- `ace2eed82c392c4d36a5` — Termo de Fomento nº 01/2026 · falta: Prazo de inscrição · https://goias.gov.br/cultura/termos-de-fomento/
- `443dfeed2a9493ab123d` — Termos de Fomento · falta: Prazo de inscrição · https://goias.gov.br/cultura/termos-de-fomento/
- `6db359795600d65dd60c` — O presente Edital destina-se cadastrar Profissionais de saúde/ Pessoas Físicas e/ ou Juríd · falta: Prazo de inscrição · https://www.jatai.go.gov.br/licitacoes/
- `93aa2d9dc209517bd973` — CREDENCIAMENTO PARA OS PROFISSIONAIS DA SAUDE. ATENDENDO AS NECESSIDADES DO FUNDO MUNICIPA · falta: Prazo de inscrição · https://trombas.megasofttransparencia.com.br/contratos-convenios-e-licitacoes
- `9d21d4e6a4ccab244aed` — Pnab 2026: Publicada errata e retificação de cronograma dos Editais nº 4 e nº 6 · falta: Prazo de inscrição · https://goias.gov.br/cultura/pnab-2026-publicada-errata-e-retificacao-de-cronograma-dos-editais-no-4-e-no-6

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