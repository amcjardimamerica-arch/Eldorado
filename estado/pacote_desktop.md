# Pacote para o Claude Desktop — 2026-09-23

Você está no computador do titular, com IP brasileiro, navegador e o repositório Eldorado clonado. Use o modelo mais forte disponível (Opus 5) para validar. Trabalhe nesta ordem, sem pular etapa, e devolva os arquivos no formato indicado. Nunca estime datas; quando não houver base, escreva o motivo.

## Etapa 1 — motores que aguardam coleta local (portais que recusam IP estrangeiro)

Rode uma vez, na raiz do repositório:

```
python scripts/coleta_brasil.py
```

Ele lê com o seu IP e envia ao repositório. Motores atendidos:
- **Diário Oficial do Município de Goiânia** — rotas: Diário Oficial do Município (edição do dia); SEMASDH — Fundo Municipal de Assistência Social e chamamentos; Secretaria Municipal de Cultura — editais

## Etapa 2 — motores em alerta (não leram, falharam ou passaram da cadência)

- **TJGO — varas de execução penal e prestações pecuniárias (substitui o Diário da Justiça)** — todas as páginas falharam em 2026-09-23. Ação: conferir bloqueio/mudança de formato; o Claude Desktop abre a rota no navegador.
    - abrir https://www.tjgo.jus.br/ e procurar: prestação pecuniária, edital de cadastramento, entidades, vara de execução penal, VEP, destinação
    - abrir https://www.tjgo.jus.br/index.php/dje e procurar: prestação pecuniária, edital de cadastramento, entidades, vara de execução penal, VEP, destinação
    - abrir https://corregedoria.tjgo.jus.br/ e procurar: prestação pecuniária, edital de cadastramento, entidades, vara de execução penal, VEP, destinação
- **Editais incentivados — sites das maiores contribuintes do ICMS de Goiás (destinação tributária)** — 5 dia(s) sem leitura (cadência 1). Ação: conferir escala e limite por execução.
    - abrir https://observatorio3setor.org.br/editais/ e procurar: edital, seleção de projetos, investimento social, responsabilidade social, patrocínio, incentivo fiscal

Para cada rota aberta, liste os editais publicados nos últimos 30 dias que casem com o léxico e que ainda não estejam em `dados/editais/`. Devolva em `dados/editais/coleta_navegador/<data>-motores.json` no formato `{"<id ou novo>": {"objeto":..., "inicio":..., "fim":..., "pagina_oficial":..., "observacao":...}}`.

## Etapa 3 — oportunidades aguardando ação externa (11)

- `3f4e0f749a5a6e40f2c4` — Edital prevê seleção de 58 apresentações artísticas para o Natal do Bem 2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/edital-preve-selecao-de-58-apresentacoes-artisticas-para-o-natal-do-bem-2026
- `4d519a11c8b5c23bd8d5` — Termo de Fomento nº 01/2026 · **o portal recusa o robô do GitHub (IP fora do Brasil)** → abrir no navegador do titular, com IP brasileiro · link: https://goias.gov.br/cultura/wp-content/uploads/sites/25/2026/06/SEI_90351764_Termo_de_Fomento_1.pdf
- `0fc96da3bfa4c9659ef3` — Secretaria de Fomento e Incentivo à Cultura · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.gov.br/cultura/pt-br/composicao/secretaria-de-economia-criativa-e-fomento-cultural
- `bdea428602f61e41e70b` — Edital recebe 851 inscrições! · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://climaesociedade.org/ics-lanca-edital-para-projetos-de-comunicacao-com-acoes-de-enfrentamento-as-mudancas-climaticas
- `400d80f3c84332f2aa0c` — EDITAL DE Nº 126/IFAL, DE 18 DE SETEMBRO DE 2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-de-n-126/ifal-de-18-de-setembro-de-2026-733048195
- `39e8067201494d565881` — EDITAL PPGFIL/IFILO/UFU Nº 1/2026 · **só existe o anúncio no PNCP/diário; o site do órgão não foi localizado** → procurar o site oficial do órgão e localizar o edital · link: https://www.in.gov.br/web/dou/-/edital-ppgfil/ifilo/ufu-n-1/2026-733304995
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
- `2f2bbd52c9f4ae6855d8` — Parque Bondinho Pão de Açúcar abre edital para projetos culturais incentivados · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/parque-bondinho-pao-de-acucar-abre-edital-para-projetos-culturais-incentivados
- `36052154d2c76c2ace4d` — EDITAL  001/ 2026  - FUNDO SEMENTE PARA RESILIÊNCIA - PARCEIROS VOLUNTÁRIOS SELEÇÃO DE PRO · falta: Objeto, Prazo de inscrição · https://duckduckgo.com/l?uddg=https%3A%2F%2Fparceirosvoluntarios.org.br%2Fwp%2Dcontent%2Fuploads%2F2026%2F04%2FEdital%2D001%2D2026.pdf&rut=1cfe90e819e5c912f0a330beec5f4074b788278c1f28e9fee854bde88a861b51
- `4c6094e4db7a4c019e94` — Parque Bondinho Pão de Açúcar abre edital para projetos culturais incentivados · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/parque-bondinho-pao-de-acucar-abre-edital-para-projetos-culturais-incentivados
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
- `fdade18228dbd15fb9fb` — Edital Conta que soma oferece formação gratuita em educação financeira para jovens · falta: Objeto, Prazo de inscrição · https://observatorio3setor.org.br/edital-conta-que-soma-oferece-formacao-gratuita-em-educacao-financeira-para-jovens
- `0b74c8f7131e75e09a15` — Captação de Recursos · falta: Objeto, Prazo de inscrição · https://captadores.org.br/captacao-de-recursos
- `1a298f0b5d7cbe0b2d76` — Certificadora Social · falta: Objeto, Prazo de inscrição · https://captadores.org.br/certificadora-social
- `2df7efe2328e78c1df66` — Bússola Investimento Social · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/investidores-sociais
- `5b0575f3f6f5ab2aea82` — Bússola Gestão · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/bussola-gestao
- `6ace1b0d40a5cca52c51` — Bússola Financeiro · falta: Objeto, Prazo de inscrição · https://www.bussolasocial.com.br/bussola-financeiro

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