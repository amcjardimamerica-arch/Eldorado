# Mapa do sistema Eldorado

Gerado pelo comando `eldorado inventario` a partir do código, da passagem e da configuração. É o catálogo da medição e a base do monitoramento em tempo real.

## Situação dos arquivos

| Situação | Arquivos |
|---|---|
| em funcionamento | 85 |
| pacote | 20 |
| a construir | 16 |
| substituído por eldorado/base/cartorio/analise_externa.py | 3 |
| desligado por desenho | 2 |
| desligado (ninguém o usa nem o aciona) | 2 |
| substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) | 1 |
| substituído por .github/workflows/eldorado.yml (funcionamento permanente) | 1 |
| substituído por .github/workflows/eldorado.yml (os pilotos rodam dentro do funcionamento permanente) | 1 |
| substituído por eldorado/base/cerebro/encaminhamento.py e eldorado/motores/pilotos/interceptador.py | 1 |


## 01 Operação: o que acorda o sistema

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 1 | `.github/workflows/eldorado.yml` |  | em funcionamento |  |  | 0 |
| 2 | `eldorado/base/nucleo/comandos.py` | Os comandos da plataforma: os mesmos no GitHub, no computador da titular e (depois) no painel. | em funcionamento | analise_externa, fila, governador, inventario, pilotos, agenda, definicao, executor, fila, nos, importar_eldorado0, config, eventos, expurgo_externo, gravador, visoes, api, escada, leve, fabrica, motor | .github/workflows/eldorado.yml (eldorado permanente) | 2 |
| 3 | `scripts/gravar.sh` |  | em funcionamento |  |  | 0 |

## 02 Núcleo: contratos, eventos e gravação

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 4 | `eldorado/base/nucleo/__init__.py` |  | pacote |  |  | 26 |
| 5 | `eldorado/base/nucleo/config.py` | A configuração da plataforma, validada na carga. | em funcionamento |  | comandos | 1 |
| 6 | `eldorado/base/nucleo/contratos.py` | Os contratos do Eldorado. | em funcionamento |  | cartorio, indice, pertinencia, regencia, oportunidades, eventos, gravador, registro, motor, espiao, interceptador | 10 |
| 7 | `eldorado/base/nucleo/expurgo_externo.py` | O expurgo físico pela análise externa (titular, 22/10/2026): "o sistema não apaga nada, mas o Claude pode apag | em funcionamento |  | comandos | 1 |
| 8 | `eldorado/base/nucleo/ia.py` | O serviço único de IA dos pilotos (do Eldorado0, titular, 26/09 e 02/10/2026). | em funcionamento |  | encaminhamento, interceptador | 1 |
| 9 | `eldorado/base/nucleo/seguranca.py` | A segurança dos textos lidos: os padrões de injeção de instruções (prompt injection). | em funcionamento |  | motor, leitores | 1 |
| 10 | `eldorado/base/nucleo/eventos.py` | Os eventos: a única forma de escrita do Eldorado. | em funcionamento | contratos | analise_externa, auditoria, cartorio, certificacao, indice, passaporte, selos, aprendizado, completude, encaminhamento,  | 14 |
| 11 | `eldorado/base/nucleo/alarmes.py` | Nenhum erro é engolido: todo erro vira um evento de alarme, e o erro continua subindo. | em funcionamento | eventos | executor | 1 |
| 12 | `eldorado/base/nucleo/gravador.py` | O gravador único: o único que escreve nos bancos. | em funcionamento | _sqlite, contratos, eventos | nos, comandos | 2 |
| 13 | `eldorado/base/nucleo/recibo.py` | A medição de uma chamada: tempo, processador e memória de pico, e se deu certo. | em funcionamento | eventos | regencia, executor | 0 |
| 14 | `eldorado/base/nucleo/registro.py` | O registro dos módulos ligados: confere o contrato antes de aceitar, e arquiva em vez de apagar. | em funcionamento | contratos, eventos | cartorio, encaminhamento, pertinencia, regencia | 6 |

## 03 Bancos

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 15 | `eldorado/banco/__init__.py` |  | pacote |  |  | 2 |
| 16 | `eldorado/banco/_sqlite.py` | Abertura padronizada dos bancos SQLite: configurações medidas, criação do esquema, versão e integridade. | em funcionamento |  | esquema, esquema, esquema, gravador | 1 |
| 17 | `eldorado/banco/biblioteca/__init__.py` |  | pacote |  |  | 2 |
| 18 | `eldorado/banco/biblioteca/leis.py` | leis atualizadas | a construir |  |  | 0 |
| 19 | `eldorado/banco/biblioteca/livro.py` | leituras e acréscimos por livro | a construir |  |  | 0 |
| 20 | `eldorado/banco/biblioteca/texto.py` | taxa de compressão; busca em menos de 1 ms | a construir |  |  | 0 |
| 21 | `eldorado/banco/cerebro_db/__init__.py` |  | pacote |  |  | 0 |
| 22 | `eldorado/banco/especial/__init__.py` |  | pacote |  |  | 0 |
| 23 | `eldorado/banco/especial/empresas.py` | empresas atualizadas | a construir |  |  | 0 |
| 24 | `eldorado/banco/fotografia.py` | última fotografia; reconstrução testada | a construir |  |  | 0 |
| 25 | `eldorado/banco/originais/drive.py` | originais no Drive × documentos citados | a construir |  |  | 0 |
| 26 | `eldorado/banco/biblioteca/esquema.py` | O esquema da Biblioteca (biblioteca.db): os livros e tudo o que se sabe de cada oportunidade. | em funcionamento | _sqlite | nos | 0 |
| 27 | `eldorado/banco/cerebro_db/esquema.py` | O esquema do banco do Cérebro (cerebro.db): a operação e o aprendizado do sistema, sem nenhuma oportunidade. | em funcionamento | _sqlite | nos | 0 |
| 28 | `eldorado/banco/especial/esquema.py` | O esquema do Especial (especial.db): as empresas, os incentivos e as oportunidades nas empresas conhecidas. | em funcionamento | _sqlite | nos | 0 |

## 04 Execução: workflow, executor, fila e governador

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 29 | `eldorado/base/cerebro/governador.py` | O governador de carga: mantém a máquina abaixo do limite (85%). | em funcionamento | eventos | regencia, fila, nos, comandos | 5 |
| 30 | `eldorado/base/fluxo/__init__.py` |  | pacote |  |  | 12 |
| 31 | `eldorado/base/fluxo/agenda.py` | A agenda: quais módulos estão devidos agora. | em funcionamento |  | regencia, comandos | 4 |
| 32 | `eldorado/base/fluxo/definicao.py` | A definição de um workflow (conceito do n8n, reescrito do zero para o Eldorado). | em funcionamento |  | executor, fila, comandos | 5 |
| 33 | `workflows/passagem.toml` |  | em funcionamento |  |  | 0 |
| 34 | `eldorado/base/fluxo/executor.py` | O executor durável dos workflows. | em funcionamento | definicao, alarmes, eventos, recibo | fila, comandos | 4 |
| 35 | `eldorado/base/fluxo/nos.py` | Os nós próprios da plataforma, usados nos workflows de operação (manutenção, aplicação de eventos). | em funcionamento | esquema, esquema, esquema, governador, eventos, gravador | passagem, nó 10 «aplicar_rede»; passagem, nó 12 «aplicar_validacao»; passagem, nó 18 «aplicar_final»; passagem, nó 4 «ap | 7 |
| 36 | `eldorado/base/fluxo/fila.py` | A fila de tarefas (Huey sobre SQLite): executa workflows, sob o governador e a pausa do sistema. | em funcionamento | governador, definicao, executor | comandos | 1 |

## 05 Cérebro decide: fila do sistema e acionamento

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 37 | `config/agenda.toml` |  | em funcionamento |  |  | 0 |
| 38 | `config/modulos.toml` |  | em funcionamento |  |  | 0 |
| 39 | `eldorado/base/cerebro/decisao.py` | A decisão do Cérebro: a cada batimento, quais motores acionar, conforme a necessidade (titular, 22/10/2026). | em funcionamento |  | fila, regencia | 1 |
| 40 | `eldorado/base/cerebro/regencia.py` | A Regência: planeja a passagem, aciona os motores e autoriza cada passagem de livro. | em funcionamento | decisao, governador, rede, registro, agenda, contratos, eventos, recibo, registro, motor | passagem, nó 1 «planejar»; passagem, nó 2 «acionar» | 11 |
| 41 | `eldorado/base/cerebro/fila.py` | A fila do sistema (titular, 22/10/2026): o Eldorado funciona de forma permanente, sem horário de trabalho e de | em funcionamento | decisao, regencia | encaminhamento, comandos | 0 |

## 06 Coleta: os motores e o canivete suíço

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 42 | `config/motores_previstos.json` |  | em funcionamento |  |  | 0 |
| 43 | `eldorado/motores/acesso/__init__.py` |  | pacote |  |  | 3 |
| 44 | `eldorado/motores/acesso/escada.py` | A escada de acesso: do degrau mais leve ao mais forte, aprendendo por domínio qual degrau funciona. | em funcionamento | eventos | encaminhamento, pilotos, comandos, api, arquivo_web, leve, local, navegador, rotas_alternativas, motor, fonte_oficial, i | 3 |
| 45 | `eldorado/motores/canal/__init__.py` |  | pacote |  |  | 11 |
| 46 | `eldorado/motores/canal/achado.py` | achados completos | a construir |  |  | 0 |
| 47 | `eldorado/motores/canal/estado.py` | O estado de cada motor: o seu aprendizado de uso próprio, num banco só dele (dados/motores/<id>.db, fora do Gi | em funcionamento |  | motor | 1 |
| 48 | `eldorado/motores/descoberta/__init__.py` |  | pacote |  |  | 4 |
| 49 | `eldorado/motores/descoberta/pistas.py` | O formato comum das cinco formas de descoberta: a pista (título, link, data, de onde veio). | em funcionamento |  | motor, arquivos_web, dados_abertos, estrutura_site, mapa_original, metabusca | 2 |
| 50 | `eldorado/motores/descoberta/vigilancia.py` | Forma 5: a vigilância: só segue quando a página mudou. | em funcionamento |  | motor | 0 |
| 51 | `eldorado/motores/leitura/__init__.py` |  | pacote |  |  | 2 |
| 52 | `eldorado/motores/leitura/atos.py` | O recorte dos atos (canivete suíço): a edição inteira de um diário em PDF ou texto → um ato por cabeçalho. | em funcionamento |  | cadeia | 0 |
| 53 | `eldorado/motores/leitura/expurgo.py` | O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição na página). | em funcionamento |  | pdf | 0 |
| 54 | `eldorado/motores/leitura/normalizar.py` | A normalização: datas, valores, números por extenso e CNPJ, a partir do texto literal. | em funcionamento |  | auditoria | 0 |
| 55 | `eldorado/motores/acesso/api.py` | Degrau 1: as APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN) com o ht | em funcionamento | escada | encaminhamento, comandos, motor | 2 |
| 56 | `eldorado/motores/acesso/arquivo_web.py` | Degrau 6: a cópia arquivada (Wayback Machine), quando o site está fora do ar ou bloqueou. | em funcionamento | escada | motor, interceptador | 1 |
| 57 | `eldorado/motores/acesso/leve.py` | Degrau 2: requisição leve com assinatura de navegador real (TLS e cabeçalhos de um Chrome). | em funcionamento | escada | encaminhamento, comandos, rotas_alternativas, motor | 1 |
| 58 | `eldorado/motores/acesso/local.py` | Degrau 9: o computador da titular, quando o próprio site bloqueia o acesso remoto. | em funcionamento | escada | motor | 1 |
| 59 | `eldorado/motores/acesso/navegador.py` | Degraus 3 a 5: os navegadores, para páginas que só existem depois do JavaScript. | em funcionamento | escada | motor | 1 |
| 60 | `eldorado/motores/descoberta/arquivos_web.py` | Forma 4: os arquivos da web: o índice da Wayback Machine lista as URLs já vistas de um domínio (inclusive edit | em funcionamento | pistas | motor | 0 |
| 61 | `eldorado/motores/descoberta/dados_abertos.py` | Forma 2: os dados abertos: as APIs oficiais (pela configuração de cada motor) e os portais CKAN (dados.gov.br  | em funcionamento | pistas | motor | 0 |
| 62 | `eldorado/motores/descoberta/estrutura_site.py` | Forma 3: a estrutura do site: o mapa do site, os feeds (RSS e Atom), a API do WordPress e os links da página. | em funcionamento | pistas | motor, mapa_original, interceptador | 0 |
| 63 | `eldorado/motores/descoberta/fonte_oficial.py` | Seguir até a fonte oficial: na página de DIVULGAÇÃO (notícia, post, agregador), o documento OFICIAL do edital. | em funcionamento | escada | motor, interceptador | 0 |
| 64 | `eldorado/motores/descoberta/metabusca.py` | Forma 1: a metabusca, com rotas de reserva: SearXNG (serviço próprio) → ddgs → Marginalia. | em funcionamento | pistas | pilotos, motor | 1 |
| 65 | `eldorado/motores/acesso/rotas_alternativas.py` | Degraus 7 e 8, reservas desligadas até o teste real na criação: o Tor (IP diferente) e o leitor público de pág | desligado por desenho | escada, leve |  | 1 |
| 66 | `eldorado/motores/descoberta/mapa_original.py` | O mapa do site ORIGINAL (titular, 23/10/2026): com o histórico do livro, ele tem um site de divulgação e um si | em funcionamento | estrutura_site, pistas | motor | 0 |
| 67 | `eldorado/motores/canal/fabrica.py` | A fábrica de motores: executa a orientação de design (eldorado/motores/skills/criar-motor/SKILL.md). | em funcionamento | motor | comandos | 1 |
| 68 | `eldorado/motores/canal/motor.py` | O motor genérico de canal: um motor é uma CONFIGURAÇÃO (um arquivo TOML), sem código próprio. | em funcionamento | contratos, seguranca, api, arquivo_web, escada, leve, local, navegador, estado, arquivos_web, cadeia, dados_abertos, estrutura_site, fonte_oficial, mapa_original, metabusca, pistas, vigilancia, leitores, pdf | config/modulos.toml (cnpq-extensao); config/modulos.toml (do-goiania); config/modulos.toml (do-goias); config/modulos.to | 11 |
| 69 | `eldorado/motores/descoberta/cadeia.py` | A leitura em cadeia (canivete suíço): a lista → cada item → o detalhe → o texto, sem código por fonte. | em funcionamento | atos, leitores | motor | 0 |
| 70 | `eldorado/motores/leitura/compactado.py` | Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo interno ao leitor do seu tipo. | em funcionamento | leitores | leitores | 0 |
| 71 | `eldorado/motores/leitura/documento.py` | Documentos DOCX (com cabeçalhos, rodapés e notas), ODT e PPTX (uma página por slide). | em funcionamento | leitores | leitores | 0 |
| 72 | `eldorado/motores/leitura/leitores.py` | O registro dos leitores: o canivete suíço da leitura. | em funcionamento | seguranca, compactado, documento, pagina, pdf, planilha | pilotos, motor, cadeia, compactado, documento, ocr, pagina, pdf, planilha, universal, interceptador | 2 |
| 73 | `eldorado/motores/leitura/ocr.py` | O OCR (reserva, extra 'ocr'): RapidOCR, leve; só para o PDF digitalizado e as imagens. | desligado (ninguém o usa nem o aciona) | leitores |  | 1 |
| 74 | `eldorado/motores/leitura/pagina.py` | A leitura de páginas: estrutura, links, tabelas, texto limpo, dados embutidos e o sistema do site. | em funcionamento | leitores | leitores | 0 |
| 75 | `eldorado/motores/leitura/pdf.py` | O leitor de PDF: o texto literal por página (com o expurgo seguro), as tabelas e as páginas que precisam de OC | em funcionamento | expurgo, leitores | motor, leitores, interceptador | 1 |
| 76 | `eldorado/motores/leitura/planilha.py` | Planilhas XLSX, XLS, XLSB e ODS (python-calamine, 13× mais rápido que o openpyxl, medido). Uma página por aba. | em funcionamento | leitores | leitores | 0 |
| 77 | `eldorado/motores/leitura/universal.py` | O leitor universal de reserva (Apache Tika, extra 'universal'): mais de mil formatos, quando nenhum outro lê. | desligado por desenho | leitores |  | 0 |

## 07 Pertinência e missão

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 78 | `eldorado/base/cerebro/pertinencia.py` | A Pertinência: decide se cada achado é oportunidade (pelo portão da missão) e mede a saída de cada etapa. | em funcionamento | contratos, eventos, registro | passagem, nó 3 «decidir»; passagem, nó 9 «decidir_rede» | 3 |
| 79 | `eldorado/base/missao/__init__.py` |  | pacote |  |  | 8 |
| 80 | `eldorado/base/missao/chave.py` | A chave do livro nesta missão: o livro é o PROGRAMA, não a edição. | em funcionamento |  | indice, importar_eldorado0, oportunidades | 0 |
| 81 | `eldorado/base/missao/itens.py` | Os 12 itens do livro e o critério único da estrela (titular, 04/10/2026), aproveitado do Eldorado0. | em funcionamento |  | analise_externa, auditoria, cartorio, certificacao, selos, importar_eldorado0, oportunidades, visoes, interceptador | 0 |
| 82 | `eldorado/base/missao/regras_portao.py` | As regras do portão da missão das oportunidades — aproveitadas do Eldorado0, com fidelidade. | em funcionamento |  | auditoria, portao | 0 |
| 83 | `eldorado/base/missao/portao.py` | O portão da missão das oportunidades (titular, 16/10/2026), com as regras aproveitadas do Eldorado0. | em funcionamento | regras_portao | auditoria, oportunidades | 0 |
| 84 | `eldorado/base/missao/oportunidades.py` | A missão das oportunidades, no contrato da plataforma: itens, chave e portão. | em funcionamento | chave, itens, portao, contratos | passagem, nó «cartorio» (parâmetro); passagem, nó «decidir_rede» (parâmetro); passagem, nó «decidir» (parâmetro); passag | 8 |

## 08 Cartório · etapas 1 e 2 (recepção e certificação)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 85 | `eldorado/base/cartorio/certificacao.py` | A certificação: cada item no texto oficial, com o valor, o trecho e a página. | em funcionamento | itens, eventos | auditoria, cartorio | 1 |
| 86 | `eldorado/base/cartorio/indice.py` | O índice: cria o livro ou vincula ao existente pela chave da missão; reconhece o mesmo edital em canais difere | em funcionamento | chave, contratos, eventos | cartorio | 1 |
| 87 | `eldorado/base/cartorio/origem.py` | A origem da oportunidade, decidida POR LIVRO, com evidência (titular, 23/10/2026). | em funcionamento |  | auditoria, cartorio, interceptador | 0 |
| 88 | `eldorado/base/cartorio/passaporte.py` | O passaporte: move o livro entre as fases só com a autorização da Regência, e registra as tentativas (até 3). | em funcionamento | regencia, eventos | analise_externa, auditoria, cartorio, encaminhamento | 1 |
| 89 | `eldorado/base/cartorio/selos.py` | Os dois selos de cada livro, calculados a cada passagem. | em funcionamento | itens, eventos | auditoria, cartorio | 0 |
| 90 | `eldorado/base/cartorio/cartorio.py` | O Cartório (titular, 22/10/2026): o ORGANIZADOR. Ele não busca nada: é onde o livro recebe informação nova, é | em funcionamento | auditoria, certificacao, indice, origem, passaporte, selos, itens, contratos, eventos, registro | passagem, nó 11 «validar»; passagem, nó 5 «cartorio» | 5 |

## 09 Cartório · validação (auditoria e arquivo)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 91 | `eldorado/base/cartorio/auditoria.py` | A auditoria de cada livro: a validação individual e a decupagem dos dados em colunas (livro_dados). | em funcionamento | certificacao, origem, passaporte, selos, itens, portao, regras_portao, eventos, normalizar | passagem, nó 7 «auditar» | 3 |

## 10 Cartório · etapa 3 (a rede neural encaminha)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 92 | `eldorado/motores/pilotos/__init__.py` |  | pacote |  |  | 4 |
| 93 | `eldorado/motores/pilotos/espiao.py` | O PILOTO ESPIÃO (do Eldorado0, titular, 09 e 16/10/2026): caça só o que nenhum motor alcança. | em funcionamento | contratos | pilotos | 1 |
| 94 | `eldorado/motores/pilotos/interceptador.py` | O PILOTO INTERCEPTADOR (do Eldorado0, titular, 26/09/2026): "o Espião descobre; o Interceptador comprova". | em funcionamento | origem, itens, contratos, eventos, ia, arquivo_web, escada, estrutura_site, fonte_oficial, leitores, pdf | encaminhamento | 3 |
| 95 | `eldorado/base/cerebro/encaminhamento.py` | A rede neural na fase 3 do Cartório (titular, 22/10/2026): quem age é a rede, não o Cartório. | em funcionamento | passaporte, fila, originais, pilotos, rede, regencia, eventos, ia, registro, api, escada, leve, motor, interceptador | passagem, nó 8 «encaminhar» | 3 |

## 11 Cartório · etapa 5 (análise externa)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 96 | `eldorado/base/cartorio/analise_externa.py` | A etapa 5 do Cartório: a ANÁLISE EXTERNA pelo Claude no Chrome (titular, 22/10/2026). | em funcionamento | cartorio, passaporte, itens, eventos | passagem, nó 13 «analise_externa» | 1 |
| 97 | `eldorado/base/verificacao/importacao.py` | respostas importadas e recusadas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 98 | `eldorado/base/verificacao/lote.py` | lotes gerados | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 99 | `eldorado/base/verificacao/relatorio_faltas.py` | livros com relatório final | substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) |  |  | 0 |
| 100 | `eldorado/base/verificacao/verificacao.py` | livros em verificação; decisões recebidas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |

## 12 Farol e transferência

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 101 | `eldorado/base/transferencia/farol.py` | livros transferidos; recusados pelo contrato | a construir |  |  | 0 |

## 13 Aprender e medir

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 102 | `eldorado/base/cerebro/aprendizado.py` | O ciclo de aprendizado: temporário (30 dias) → permanente, se funcionou; arquivado, se falhou; vencido, sai. | em funcionamento | eventos | passagem, nó 15 «aprender» | 2 |
| 103 | `eldorado/base/cerebro/completude.py` | A completude do dia: o que estava devido foi lido? O que precisa ser reacionado? | em funcionamento | eventos | passagem, nó 16 «completude» | 2 |
| 104 | `eldorado/base/cerebro/inventario.py` | O inventário do sistema (titular, 22/10/2026): todo arquivo, do primeiro ao último no caminho do funcionamento | em funcionamento |  | comandos | 1 |
| 105 | `eldorado/base/cerebro/medicao.py` | O motor de indicadores: ponto, círculo e linhas de cada arquivo, e a agregação por componente, parte e sistema | em funcionamento | eventos | passagem, nó 17 «medir» | 2 |
| 106 | `eldorado/base/cerebro/rede.py` | A rede neural única, de aprendizado contínuo (River): aprende a cada veredito e dá as notas. | em funcionamento | eventos, motor | passagem, nó 14 «rede» | 2 |
| 107 | `eldorado/base/cerebro/regras.py` | A tabela única de regras e decisões da titular. | desligado (ninguém o usa nem o aciona) | eventos |  | 1 |

## 14 Análise e painel

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 108 | `eldorado/base/analise/calendario.py` | calendário atualizado na passagem | a construir |  |  | 0 |
| 109 | `eldorado/base/analise/historia.py` | livros com história completa | a construir |  |  | 0 |
| 110 | `eldorado/base/analise/preditivo.py` | alertas emitidos antes da abertura | a construir |  |  | 0 |
| 111 | `eldorado/base/painel/__init__.py` |  | pacote |  |  | 1 |
| 112 | `eldorado/base/painel/api.py` | respostas no prazo; erros | a construir |  |  | 0 |
| 113 | `eldorado/base/painel/maquina.py` | mostrador atualizado em tempo real | a construir |  |  | 0 |
| 114 | `eldorado/base/painel/sala.py` | sala publicada no prazo | a construir |  |  | 0 |
| 115 | `eldorado/base/painel/visoes.py` | As visões do painel: o que cada tela mostra, lido dos bancos (só leitura), num único arquivo de dados. | em funcionamento | itens | comandos | 1 |

## 16 Migração do Eldorado0 (temporária)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 116 | `eldorado/base/migracao/__init__.py` |  | pacote |  |  | 1 |
| 117 | `eldorado/base/migracao/importar_eldorado0.py` | A migração do Eldorado0 (temporária, 30 dias): livros, certidões, documentos, vereditos, selos, leis, empresas | em funcionamento | chave, itens, eventos | comandos | 1 |

## 17 Outros

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 118 | `.github/workflows/painel.yml` |  | em funcionamento |  |  | 0 |
| 119 | `.github/workflows/passagem.yml` | passagens no horário | substituído por .github/workflows/eldorado.yml (funcionamento permanente) |  |  | 0 |
| 120 | `.github/workflows/pilotos.yml` | voos com sucesso | substituído por .github/workflows/eldorado.yml (os pilotos rodam dentro do funcionamento permanente) |  |  | 0 |
| 121 | `config/motores_previstos.toml` | o sistema roda sem intervenção | a construir |  |  | 0 |
| 122 | `eldorado/__init__.py` |  | pacote |  |  | 43 |
| 123 | `eldorado/base/__init__.py` |  | pacote |  |  | 34 |
| 124 | `eldorado/base/cartorio/__init__.py` |  | pacote |  |  | 7 |
| 125 | `eldorado/base/cartorio/site_oficial.py` | O site oficial: a oportunidade se encontra NA FONTE (titular, 14/10/2026). | a construir |  |  | 0 |
| 126 | `eldorado/base/cerebro/__init__.py` |  | pacote |  |  | 19 |
| 127 | `eldorado/base/cerebro/originais.py` | A rede neural vigia os sites ORIGINAIS dos livros (titular, 23/10/2026): com o histórico do livro, ele tem um  | em funcionamento | encaminhamento | encaminhamento | 1 |
| 128 | `eldorado/base/cerebro/pilotos.py` | O Cérebro dos pilotos (titular, 22/10/2026): mede a recorrência de cada piloto e manda nova missão sempre que | em funcionamento | escada, metabusca, leitores, espiao | encaminhamento, comandos | 1 |
| 129 | `eldorado/base/especial/__init__.py` |  | pacote |  |  | 1 |
| 130 | `eldorado/base/especial/registro.py` | O registro da base Especial (as empresas e os incentivos): o "cartório" do banco especial.db. | em funcionamento | eventos | regencia | 1 |
| 131 | `eldorado/base/investigacao/investigacao.py` | livros investigados e itens comprovados por livro | substituído por eldorado/base/cerebro/encaminhamento.py e eldorado/motores/pilotos/interceptador.py |  |  | 0 |
| 132 | `eldorado/motores/__init__.py` |  | pacote |  |  | 19 |

## Os 47 motores (o estudo de reorganização da titular: 45 regulares e 2 pilotos)

| # | Categoria | Motor | Nome | Agrega | Alvos | Motor no sistema | Situação | Observação |
|---|---|---|---|---|---|---|---|---|
| 1 | EXE | do-goiania | Diário Oficial do Município de Goiânia | 0 | 2 | do-goiania | conforme | criado pela orientação: a lista oficial → o PDF → os atos; o Querido Diário pelo código do município como alternativa |
| 2 | EXE | do-goias | Diário Oficial do Estado de Goiás | 0 | 2 | do-goias | conforme | criado pela orientação: a cadeia edições → sumário → matéria; páginas gravadas em 23/10 |
| 3 | EXE | dou | Diário Oficial da União | 0 | 2 | dou | conforme |  |
| 4 | EXE | prefeituras-50-go | Prefeituras das 25 maiores cidades de Goiás — portais de editais | 1 | 4 | prefeituras-50-go | conforme | criado pela orientação: 55 rotas das 25 cidades (WordPress e páginas); 23 respondem da nuvem; Luziânia e Mineiros exigem o Brasil |
| 5 | EXE | estaduais-go-gov | Oportunidade Estaduais Governamentais de Goiás | 7 | 10 | estaduais-go-gov | incompleto | Secult, SEDS, FAPEG, PNAB Goiás, FICA e o Goyazes; faltam OVG, SEMAD, Goiás Social, fundos estaduais e Anater (endereços a localizar; a API da Anater recusa) e 5 alvos |
| 6 | EXE | pncp-api | PNCP — API de contratações (chamamentos e credenciamentos) | 0 | 17 | pncp-api | conforme | faltam os 17 alvos |
| 7 | EXE | salic | Lei Rouanet — janela de propostas no SALIC e projetos de Goiás (Ministério da Cultura) | 2 | 1 | salic | conforme |  |
| 8 | EXE | motor-gife | Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) | 1 | 0 | motor-gife | conforme | criado pela orientação, destino especial: os 500 maiores contribuintes do ICMS de Goiás e os 358 incentivadores PJ de Goiás no Salic; empresas e incentivos na base Especial |
| 9 | EXE | empresas-editais-incentivados | Busca de empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas, Pronon e Goyazes | 2 | 5 | empresas-editais-incentivados | conforme | criado pela orientação: os chamamentos do Pronas/PCD e do Pronon, a apresentação de projetos e o credenciamento; a Lei de Incentivo ao Esporte pelo Brasil; os 5 alvos |
| 10 | EXE | cnpq-extensao | CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC | 2 | 0 | cnpq-extensao | conforme | criado pela orientação: as chamadas abertas do CNPq, com o léxico de extensão e OSC; a Finep sem lista reconhecível (registrada) |
| 11 | EXE | site-funarte | Funarte — editais da Fundação Nacional de Artes | 0 | 0 | site-funarte | conforme | criado pela orientação: os editais abertos e os do ano corrente |
| 12 | EXE | site-transferegov | Transferegov — programas e parcerias com OSC abertos na plataforma federal (dados abertos) | 0 | 4 | site-transferegov | conforme | faltam os 4 alvos |
| 13 | EXE | novo-diarios-municipais-go | Diários oficiais municipais de Goiás (Querido Diário) | 0 | 1 | novo-diarios-municipais-go | conforme | refeito pela orientação: a edição diária da AGM (atos de dezenas de municípios, com o município de cada ato) e o Querido Diário de Aparecida; o QD só tem texto completo de Goiânia e Aparecida em Goiás |
| 14 | EXE | novo-bancos-publicos | Bancos públicos e Sistema S (BNDES, BNB, Caixa, Sebrae) | 1 | 5 | novo-bancos-publicos | conforme | criado pela orientação: os editais sociais do Banco do Nordeste, o BNDES Periferias, o Sebrae Goiás pelo Brasil; os 5 alvos |
| 15 | JUD | judiciario-tjgo | TJ-GO — editais das comarcas (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO | 2 | 1 | — | a construir |  |
| 16 | JUD | dj-trf1-go | Diário da Justiça Federal — Seção Judiciária de Goiás | 0 | 0 | — | a construir |  |
| 17 | JUD | judiciario-cnj | CNJ — destinação de prestações pecuniárias: busca no Portal do CNJ e regra nacional (Res. 558/2024) | 1 | 1 | — | a construir |  |
| 18 | JUD | mpgo-destinacao | MP-GO — Programa Destina (cadastro de entidades para receber bens e valores de acordos) | 0 | 1 | — | a construir |  |
| 19 | JUD | mptgo-destinacao | MPT-GO — editais de 5 dias para indicação de destinação de recursos ou bens (PRT 18ª Região) | 0 | 0 | — | a construir |  |
| 20 | JUD | mpu-destinacao | MPU — MPF, MPDFT, MPM e MPT nacional: destinação de bens e valores (com CNMP e FDD) | 1 | 2 | — | a construir |  |
| 21 | LEG | camara-goiania-pl | Câmara Municipal de Goiânia — processos legislativos, utilidade pública e chamamentos | 0 | 4 | — | a construir |  |
| 22 | LEG | alego-pl | Assembleia Legislativa de Goiás — proposições | 0 | 2 | — | a construir |  |
| 23 | LEG | congresso-nacional | Congresso Nacional — Câmara, Senado e Comissão Mista de Orçamento (emendas, regras e chamamentos) | 0 | 1 | — | a construir |  |
| 24 | POR | gife | GIFE — Grupo de Institutos, Fundações e Empresas | 1 | 0 | gife | conforme |  |
| 25 | POR | plataforma-mapas-culturais | Adaptador Mapas Culturais — oportunidades com inscrição aberta | 0 | 0 | plataforma-mapas-culturais | conforme |  |
| 26 | POR | site-farol-cultural | Farol Cultural — editais de cultura de todo o Brasil, pela API pública do portal | 0 | 0 | — | a construir |  |
| 27 | POR | site-capitaai | CapitaAI — editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas | 0 | 0 | — | a construir |  |
| 28 | POR | site-observatorio-terceiro-setor | Observatório do Terceiro Setor — editais publicados na seção temática do portal | 1 | 0 | — | a construir |  |
| 29 | POR | site-mapas-culturais | Mapas Culturais — editais das redes estaduais e municipais de cultura que usam a plataforma | 0 | 0 | — | a construir |  |
| 30 | POR | site-abcr | ABCR — Associação Brasileira de Captadores de Recursos — editais divulgados pela associação dos captadores | 1 | 0 | site-abcr | conforme |  |
| 31 | POR | site-rede-comua | Rede Comuá — editais dos fundos independentes de filantropia | 0 | 0 | — | a construir |  |
| 32 | POR | site-fundo-baoba | Fundo Baobá — editais para equidade racial | 0 | 0 | — | a construir |  |
| 33 | POR | site-idis | IDIS — Instituto para o Desenvolvimento do Investimento Social — chamadas e editais de investimento social | 0 | 0 | — | a construir |  |
| 34 | POR | site-fundo-casa | Fundo Casa Socioambiental — chamadas socioambientais | 0 | 0 | site-fundo-casa | conforme |  |
| 35 | POR | site-cese | CESE — Coordenadoria Ecumênica de Serviço — editais de apoio a projetos populares | 0 | 0 | site-cese | conforme |  |
| 36 | POR | site-rede-filantropia | Rede Filantropia — editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro) | 1 | 0 | — | a construir |  |
| 37 | POR | site-editais-culturais | Editais Culturais — editais de cultura reunidos no portal | 0 | 0 | — | a construir |  |
| 38 | POR | site-mapa-osc | Mapa das OSC (Ipea) — editais reunidos no portal | 1 | 1 | — | a construir |  |
| 39 | POR | site-prosas | Prosas — editais e prêmios para OSCs (três caminhos indiretos: listagem da CapitaAI, ângulo do Piloto e coleta assistida) | 3 | 0 | — | a construir |  |
| 40 | POR | site-fundo-brasil | Fundo Brasil de Direitos Humanos — editais de direitos humanos | 0 | 0 | site-fundo-brasil | conforme |  |
| 41 | POR | site-undef | UNDEF — Fundo das Nações Unidas para a Democracia — chamadas anuais para a sociedade civil | 0 | 0 | — | a construir |  |
| 42 | POR | site-brazilfoundation | BrazilFoundation — editais de apoio a organizações brasileiras | 0 | 0 | — | a construir |  |
| 43 | POR | outros-agregadores | Outros agregadores e motores de busca | 10 | 3 | — | a construir |  |
| 44 | POR | novo-fundacoes-institutos | Fundações e institutos (sites próprios) | 2 | 24 | — | a construir |  |
| 45 | POR | novo-internacional | Organismos e fundações internacionais | 3 | 21 | — | a construir |  |
| 46 | IA | piloto-aberto | Piloto - Espião — busca aberta no terceiro setor | 1 | 0 | espiao | conforme |  |
| 47 | IA | piloto-interceptador | Piloto - Interceptador — comprova na fonte oficial | 0 | 0 | interceptador | conforme |  |
