# Pacote para o Claude Desktop — 2026-09-21

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
- **PNCP — API de contratações (chamamentos e credenciamentos)** — todas as páginas falharam em 2026-09-21. Ação: conferir bloqueio/mudança de formato; o Claude Desktop abre a rota no navegador.
    - abrir https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao e procurar: chamamento público, termo de fomento, termo de colaboração, organização da sociedade civil, Lei 13.019, seleção de OSC
    - abrir https://pncp.gov.br/pncp-api/v1/orgaos/ e procurar: chamamento público, termo de fomento, termo de colaboração, organização da sociedade civil, Lei 13.019, seleção de OSC

Para cada rota aberta, liste os editais publicados nos últimos 30 dias que casem com o léxico e que ainda não estejam em `dados/editais/`. Devolva em `dados/editais/coleta_navegador/<data>-motores.json` no formato `{"<id ou novo>": {"objeto":..., "inicio":..., "fim":..., "pagina_oficial":..., "observacao":...}}`.

## Etapa 3 — oportunidades aguardando ação externa (19)

- `3f4e0f749a5a6e40f2c4` — Edital prevê seleção de 58 apresentações artísticas para o Natal do Bem 2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/edital-preve-selecao-de-58-apresentacoes-artisticas-para-o-natal-do-bem-2026
- `4d519a11c8b5c23bd8d5` — Termo de Fomento nº 01/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/06/SEI_90351764_Termo_de_Fomento_1.pdf
- `35720136b64a9f474504` — Aviso de Chamamento Público – Complexo Serra Dourada · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/esporte/aviso-de-chamamento-publico-complexo-serra-dourada
- `3a3514f67ea7f8d2403a` — Aviso de Chamamento Público Nº 02/2006 – DOE · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/02/chamamento022026secultgo.pdf
- `70e84d931e674539af05` — Extrato do Termo de Colaboração Nº 01/2026 – SECULT · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/02/ExtratoCineLeituraBem.pdf
- `89da6af5827f908a3b7c` — ANEXO IX – MINUTA DO TERMO DE COLABORAÇÃO · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/02/SEI_86406084_ANEXO.pdf
- `a6b497cab7db6ab3d0c5` — Aviso de Chamamento Público N° 01/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/01/diario_oficial_2026-01-16_suplemento_pag_3.pdf
- `b3e0dbe3eb4ae0ec3800` — Edital de Chamamento Público Nº 01/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/01/1768591320_SEI_85022756_Edital.pdf
- `bb02bb2ef5d866c021b4` — Chamamento público · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/esporte/chamamento-publico
- `d5a20d71c4aebe0a2b06` — Aviso de Chamamento Público 02/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/02/SEI_86425409_Aviso_de_Chamamento_Publico_02.pdf
- `fa6210416fca8e60c5dd` — 3ª Alteração do Cronograma, “Tabela 2”, item “11.1” referente ao EDITAL DE CHAMAMENTO PÚBL · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/04/diario_oficial_2026_04_07_completo.pdf
- `0fc96da3bfa4c9659ef3` — Secretaria de Fomento e Incentivo à Cultura · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.gov.br/cultura/pt-br/composicao/secretaria-de-economia-criativa-e-fomento-cultural
- `bdea428602f61e41e70b` — Edital recebe 851 inscrições! · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://climaesociedade.org/ics-lanca-edital-para-projetos-de-comunicacao-com-acoes-de-enfrentamento-as-mudancas-climaticas
- `400d80f3c84332f2aa0c` — EDITAL DE Nº 126/IFAL, DE 18 DE SETEMBRO DE 2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-de-n-126/ifal-de-18-de-setembro-de-2026-733048195
- `f733cd0539057acbdcbe` — A referente requisição se faz para abertura de edital de chamamento público , para contrat · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://pncp.gov.br/app/editais/88775390000112/2023/99
- `5b1f86e6fc0993dabf5b` — Edital Natal do Bem · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://goias.gov.br/cultura/pnab/edital-2026-pnab
- `61208c62e6d5fade40d4` — Política Nacional Aldir Blanc de Fomento à Cultura · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://www.gov.br/cultura/pt-br/acesso-a-informacao/perguntas-frequentes/politica-nacional-aldir-blanc
- `8c25b367f7f8300e0b0f` — Política Nacional Aldir Blanc de Fomento à Cultura · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/politica-nacional-aldir-blanc-de-fomento-a-cultura
- `9a3b706226b8076711a1` — 17 Set.   10:30 
       
     
     Nova legislação altera política de fomento à IA para f · **o PDF anexado é digitalização sem camada de texto** → rodar OCR no navegador (tesseract + pdf.js) ou pedir o arquivo ao órgão · link: https://portal.al.go.leg.br/noticias/167376/nova-legislacao-altera-politica-de-fomento-a-ia-para-fortalecer-gestao-publica-e-pesquisa-alem-de-instituir-premiacao-na-area

## Etapa 4 — oportunidades parciais do modo completo, para validar com Opus 5 (40)

Para cada uma, abra a página oficial (nunca PNCP, diário ou portal de notícia; exceção: o arquivo do edital do órgão hospedado no PNCP, em `/arquivos/`), extraia OBJETO, PRAZO (início e fim) e URL oficial, e dê o veredito: aprovado (chamada aberta de fomento a OSC), atenção (serve, mas o enquadramento exige conferência) ou reprovado (com a família: resultado de edital, seleção de empresa, serviço ao órgão, qualificação como OS, órgão buscando patrocinador, parceria já celebrada).

- `8dfec58a3ca3a2ebe273` — Redion abre seleção para projetos sociais e culturais com captação via leis de incentivo · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/redion-abre-selecao-para-projetos-sociais-e-culturais-com-captacao-via-leis-de-incentivo
- `9a766d6157f999488d58` — Clima na Economia: integrando a questão climática à agenda econômica · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/edital/clima-na-economia-integrando-a-questao-climatica-a-agenda-economica
- `e5fe7f2125dac11f0d23` — Comunicação para Ação Climática no Brasil · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/edital/comunicacao-para-acao-climatica-no-brasil
- `4494396747d696db5a9b` — Médicos Sem Fronteiras abre vaga para Pessoa Captadora de Recursos no Rio de Janeiro · falta: Objeto, Prazo de inscrição · https://captadores.org.br/vagas/medicos-sem-fronteiras-abre-vaga-para-pessoa-captadora-de-recursos-no-rio-de-janeiro
- `0fc96da3bfa4c9659ef3` — Secretaria de Fomento e Incentivo à Cultura · falta: Objeto, Prazo de inscrição · https://www.gov.br/cultura/pt-br/composicao/secretaria-de-economia-criativa-e-fomento-cultural
- `1147574ff00c17dc58ef` — Engajamento, agentes de mudança e governança climática · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/eixo/engajamento-agentes-de-mudanca-e-governanca-climatica
- `16bc790ac60fa10b46cd` — Prêmio LED Globo 2027 abre inscrições com R$ 1,2 milhão em premiação · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/premio-led-globo-2027-abre-inscricoes-com-r-12-milhao-em-premiacao
- `3fabd44e16b092f256aa` — Fundação Maria Emília abre edital de até R$ 1 milhão para projetos de Saúde e Educação · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/fundacao-maria-emilia-abre-edital-de-ate-r-1-milhao-para-projetos-de-saude-e-educacao
- `4438f7fa45e9ee2962bb` — Banrisul abre edital para premiar 50 organizações do Rio Grande do Sul · falta: Objeto, Prazo de inscrição · https://captadores.org.br/editais/banrisul-abre-edital-para-premiar-50-organizacoes-do-rio-grande-do-sul
- `46496cc06152690a1735` — ODS 17 – Parcerias · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/ods/ods-17
- `4d519a11c8b5c23bd8d5` — Termo de Fomento nº 01/2026 · falta: Objeto, Prazo de inscrição · https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/06/SEI_90351764_Termo_de_Fomento_1.pdf
- `51a9cbefb74b503f13a0` — Cultura de Doação · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/secoes_tematicas/cultura-de-doacao
- `571ef6c46c40aa0bd4f7` — Edital Alimento no Prato oferece até R$ 800 mil para projetos de agricultura urbana · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/edital-alimento-no-prato-oferece-ate-r-800-mil-para-projetos-de-agricultura-urbana
- `5b1f86e6fc0993dabf5b` — Edital Natal do Bem · falta: Objeto, Prazo de inscrição · https://goias.gov.br/cultura/pnab/edital-2026-pnab
- `61208c62e6d5fade40d4` — Política Nacional Aldir Blanc de Fomento à Cultura · falta: Objeto, Prazo de inscrição · https://www.gov.br/cultura/pt-br/acesso-a-informacao/perguntas-frequentes/politica-nacional-aldir-blanc
- `7fcafdf4008f29aaf5d9` — Prêmio nacional da Enap oferece até R$ 20 mil para iniciativas que protegem crianças e ado · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/premio-nacional-da-enap-oferece-ate-r-20-mil-para-iniciativas-que-protegem-criancas-e-adolescentes-em-situacao-de-rua
- `8c25b367f7f8300e0b0f` — Política Nacional Aldir Blanc de Fomento à Cultura · falta: Objeto, Prazo de inscrição · https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/politica-nacional-aldir-blanc-de-fomento-a-cultura
- `9029f6fd301f56924784` — Continue lendo Fundação Maria Emília abre edital com apoio de até R$ 1 milhão para projeto · falta: Objeto, Prazo de inscrição · https://captadores.org.br/editais/fundacao-maria-emilia-abre-edital-com-apoio-de-ate-r-1-milhao-para-projetos-em-saude-e-educacao
- `bdea428602f61e41e70b` — Edital recebe 851 inscrições! · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/ics-lanca-edital-para-projetos-de-comunicacao-com-acoes-de-enfrentamento-as-mudancas-climaticas
- `fa3aef7dda8713d36dc3` — Política Nacional Aldir Blanc - PNAB · falta: Objeto, Prazo de inscrição · https://goias.gov.br/cultura/pnab
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
- `07b51af34420730537e7` — Cartilhas e Emendas Parlamentares · falta: Objeto, Prazo de inscrição · https://www.gov.br/transferegov/pt-br/manuais/emendas
- `1112ed09bddc4f27cb42` — Terceirizados · falta: Objeto, Prazo de inscrição · https://transparencia.go.gov.br/terceirizados
- `1900448f0bbb4c705705` — Como Solicitar uma Doação · falta: Objeto, Prazo de inscrição · https://climaesociedade.org/como-solicitar-uma-doacao
- `1b259c84aabf58826786` — Grupo Equatorial abre chamada com mais de R$ 61 milhões para projetos de eficiência energé · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/grupo-equatorial-abre-chamada-com-mais-de-r-61-milhoes-para-projetos-de-eficiencia-energetica

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