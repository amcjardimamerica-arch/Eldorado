# Mapa do sistema Eldorado

Gerado pelo comando `eldorado inventario` a partir do código, da passagem e da configuração. É o catálogo da medição e a base do monitoramento em tempo real.

## Situação dos arquivos

| Situação | Arquivos |
|---|---|
| em funcionamento | 75 |
| pacote | 19 |
| a construir | 16 |
| desligado (ninguém o usa nem o aciona) | 3 |
| substituído por eldorado/base/cartorio/analise_externa.py | 3 |
| desligado por desenho | 2 |
| substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) | 1 |
| substituído por .github/workflows/eldorado.yml (funcionamento permanente) | 1 |
| substituído por .github/workflows/eldorado.yml (os pilotos rodam dentro do funcionamento permanente) | 1 |
| substituído por eldorado/base/cerebro/encaminhamento.py e eldorado/motores/pilotos/interceptador.py | 1 |


## 01 Operação: o que acorda o sistema

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 1 | `.github/workflows/eldorado.yml` |  | em funcionamento |  |  | 0 |
| 2 | `eldorado/base/nucleo/comandos.py` | Os comandos da plataforma: os mesmos no GitHub, no computador da titular e (depois) no painel. | em funcionamento | analise_externa, fila, governador, inventario, agenda, definicao, executor, fila, nos, importar_eldorado0, config, eventos, expurgo_externo, gravador, visoes, api, escada, leve | .github/workflows/eldorado.yml (eldorado permanente) | 2 |
| 3 | `scripts/gravar.sh` |  | em funcionamento |  |  | 0 |

## 02 Núcleo: contratos, eventos e gravação

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 4 | `eldorado/base/nucleo/__init__.py` |  | pacote |  |  | 22 |
| 5 | `eldorado/base/nucleo/config.py` | A configuração da plataforma, validada na carga. | em funcionamento |  | comandos | 1 |
| 6 | `eldorado/base/nucleo/contratos.py` | Os contratos do Eldorado. | em funcionamento |  | cartorio, indice, pertinencia, regencia, oportunidades, eventos, gravador, registro, motor, interceptador | 9 |
| 7 | `eldorado/base/nucleo/expurgo_externo.py` | O expurgo físico pela análise externa (titular, 22/10/2026): "o sistema não apaga nada, mas o Claude pode apag | em funcionamento |  | comandos | 1 |
| 8 | `eldorado/base/nucleo/ia.py` | respostas válidas (meta 90%); custo e tempo por tarefa | a construir |  |  | 0 |
| 9 | `eldorado/base/nucleo/seguranca.py` | A segurança dos textos lidos: os padrões de injeção de instruções (prompt injection). | em funcionamento |  | leitores | 1 |
| 10 | `eldorado/base/nucleo/eventos.py` | Os eventos: a única forma de escrita do Eldorado. | em funcionamento | contratos | analise_externa, auditoria, cartorio, certificacao, indice, passaporte, selos, aprendizado, completude, encaminhamento,  | 11 |
| 11 | `eldorado/base/nucleo/alarmes.py` | Nenhum erro é engolido: todo erro vira um evento de alarme, e o erro continua subindo. | em funcionamento | eventos | executor | 1 |
| 12 | `eldorado/base/nucleo/gravador.py` | O gravador único: o único que escreve nos bancos. | em funcionamento | _sqlite, contratos, eventos | nos, comandos | 2 |
| 13 | `eldorado/base/nucleo/recibo.py` | A medição de uma chamada: tempo, processador e memória de pico, e se deu certo. | em funcionamento | eventos | regencia, executor | 0 |
| 14 | `eldorado/base/nucleo/registro.py` | O registro dos módulos ligados: confere o contrato antes de aceitar, e arquiva em vez de apagar. | em funcionamento | contratos, eventos | cartorio, encaminhamento, pertinencia, regencia | 3 |

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
| 29 | `eldorado/base/cerebro/governador.py` | O governador de carga: mantém a máquina abaixo do limite (85%). | em funcionamento | eventos | regencia, fila, nos, comandos | 4 |
| 30 | `eldorado/base/fluxo/__init__.py` |  | pacote |  |  | 11 |
| 31 | `eldorado/base/fluxo/agenda.py` | A agenda: quais módulos estão devidos agora. | em funcionamento |  | regencia, comandos | 3 |
| 32 | `eldorado/base/fluxo/definicao.py` | A definição de um workflow (conceito do n8n, reescrito do zero para o Eldorado). | em funcionamento |  | executor, fila, comandos | 5 |
| 33 | `workflows/passagem.toml` |  | em funcionamento |  |  | 0 |
| 34 | `eldorado/base/fluxo/executor.py` | O executor durável dos workflows. | em funcionamento | definicao, alarmes, eventos, recibo | fila, comandos | 4 |
| 35 | `eldorado/base/fluxo/nos.py` | Os nós próprios da plataforma, usados nos workflows de operação (manutenção, aplicação de eventos). | em funcionamento | esquema, esquema, esquema, governador, eventos, gravador | passagem, nó 10 «aplicar_rede»; passagem, nó 12 «aplicar_validacao»; passagem, nó 17 «aplicar_final»; passagem, nó 4 «ap | 7 |
| 36 | `eldorado/base/fluxo/fila.py` | A fila de tarefas (Huey sobre SQLite): executa workflows, sob o governador e a pausa do sistema. | em funcionamento | governador, definicao, executor | comandos | 1 |

## 05 Cérebro decide: fila do sistema e acionamento

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 37 | `config/agenda.toml` |  | em funcionamento |  |  | 0 |
| 38 | `config/modulos.toml` |  | em funcionamento |  |  | 0 |
| 39 | `eldorado/base/cerebro/decisao.py` | A decisão do Cérebro: a cada batimento, quais motores acionar, conforme a necessidade (titular, 22/10/2026). | em funcionamento |  | fila, regencia | 1 |
| 40 | `eldorado/base/cerebro/regencia.py` | A Regência: planeja a passagem, aciona os motores e autoriza cada passagem de livro. | em funcionamento | decisao, governador, agenda, contratos, eventos, recibo, registro | passagem, nó 1 «planejar»; passagem, nó 2 «acionar» | 9 |
| 41 | `eldorado/base/cerebro/fila.py` | A fila do sistema (titular, 22/10/2026): o Eldorado funciona de forma permanente, sem horário de trabalho e de | em funcionamento | decisao, regencia | comandos | 0 |

## 06 Coleta: os motores e o canivete suíço

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 42 | `config/motores_previstos.toml` |  | em funcionamento |  |  | 0 |
| 43 | `eldorado/motores/acesso/__init__.py` |  | pacote |  |  | 3 |
| 44 | `eldorado/motores/acesso/escada.py` | A escada de acesso: do degrau mais leve ao mais forte, aprendendo por domínio qual degrau funciona. | em funcionamento | eventos | encaminhamento, comandos, api, arquivo_web, leve, local, navegador, rotas_alternativas, motor, fonte_oficial, intercepta | 3 |
| 45 | `eldorado/motores/canal/__init__.py` |  | pacote |  |  | 3 |
| 46 | `eldorado/motores/canal/achado.py` | achados completos | a construir |  |  | 0 |
| 47 | `eldorado/motores/canal/estado.py` | O estado de cada motor: o seu aprendizado de uso próprio, num banco só dele (dados/motores/<id>.db, fora do Gi | em funcionamento |  | motor | 1 |
| 48 | `eldorado/motores/descoberta/__init__.py` |  | pacote |  |  | 2 |
| 49 | `eldorado/motores/descoberta/pistas.py` | O formato comum das cinco formas de descoberta: a pista (título, link, data, de onde veio). | em funcionamento |  | motor, arquivos_web, dados_abertos, estrutura_site, metabusca | 1 |
| 50 | `eldorado/motores/descoberta/vigilancia.py` | Forma 5: a vigilância: só segue quando a página mudou. | em funcionamento |  | motor | 0 |
| 51 | `eldorado/motores/leitura/__init__.py` |  | pacote |  |  | 2 |
| 52 | `eldorado/motores/leitura/expurgo.py` | O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição na página). | em funcionamento |  | pdf | 0 |
| 53 | `eldorado/motores/leitura/normalizar.py` | A normalização: datas, valores, números por extenso e CNPJ, a partir do texto literal. | em funcionamento |  | auditoria | 0 |
| 54 | `eldorado/motores/acesso/api.py` | Degrau 1: as APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN) com o ht | em funcionamento | escada | encaminhamento, comandos, motor | 2 |
| 55 | `eldorado/motores/acesso/arquivo_web.py` | Degrau 6: a cópia arquivada (Wayback Machine), quando o site está fora do ar ou bloqueou. | em funcionamento | escada | motor, interceptador | 1 |
| 56 | `eldorado/motores/acesso/leve.py` | Degrau 2: requisição leve com assinatura de navegador real (TLS e cabeçalhos de um Chrome). | em funcionamento | escada | encaminhamento, comandos, rotas_alternativas, motor | 1 |
| 57 | `eldorado/motores/acesso/local.py` | Degrau 9: o computador da titular, quando o próprio site bloqueia o acesso remoto. | em funcionamento | escada | motor | 1 |
| 58 | `eldorado/motores/acesso/navegador.py` | Degraus 3 a 5: os navegadores, para páginas que só existem depois do JavaScript. | em funcionamento | escada | motor | 1 |
| 59 | `eldorado/motores/descoberta/arquivos_web.py` | Forma 4: os arquivos da web: o índice da Wayback Machine lista as URLs já vistas de um domínio (inclusive edit | em funcionamento | pistas | motor | 0 |
| 60 | `eldorado/motores/descoberta/dados_abertos.py` | Forma 2: os dados abertos: as APIs oficiais (pela configuração de cada motor) e os portais CKAN (dados.gov.br  | em funcionamento | pistas | motor | 0 |
| 61 | `eldorado/motores/descoberta/estrutura_site.py` | Forma 3: a estrutura do site: o mapa do site, os feeds (RSS e Atom), a API do WordPress e os links da página. | em funcionamento | pistas | motor, interceptador | 0 |
| 62 | `eldorado/motores/descoberta/fonte_oficial.py` | Seguir até a fonte oficial: na página de DIVULGAÇÃO (notícia, post, agregador), o documento OFICIAL do edital. | em funcionamento | escada | motor, interceptador | 0 |
| 63 | `eldorado/motores/descoberta/metabusca.py` | Forma 1: a metabusca, com rotas de reserva: SearXNG (serviço próprio) → ddgs → Marginalia. | em funcionamento | pistas | motor | 1 |
| 64 | `eldorado/motores/acesso/rotas_alternativas.py` | Degraus 7 e 8, reservas desligadas até o teste real na criação: o Tor (IP diferente) e o leitor público de pág | desligado por desenho | escada, leve |  | 1 |
| 65 | `eldorado/motores/canal/motor.py` | O motor genérico de canal: um motor é uma CONFIGURAÇÃO (um arquivo TOML), sem código próprio. | em funcionamento | contratos, api, arquivo_web, escada, leve, local, navegador, estado, arquivos_web, dados_abertos, estrutura_site, fonte_oficial, metabusca, pistas, vigilancia, leitores, pdf | config/modulos.toml (dou); config/modulos.toml (goyazes); config/modulos.toml (mapas-culturais); config/modulos.toml (pn | 3 |
| 66 | `eldorado/motores/leitura/compactado.py` | Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo interno ao leitor do seu tipo. | em funcionamento | leitores | leitores | 0 |
| 67 | `eldorado/motores/leitura/documento.py` | Documentos DOCX (com cabeçalhos, rodapés e notas), ODT e PPTX (uma página por slide). | em funcionamento | leitores | leitores | 0 |
| 68 | `eldorado/motores/leitura/leitores.py` | O registro dos leitores: o canivete suíço da leitura. | em funcionamento | seguranca, compactado, documento, pagina, pdf, planilha | motor, compactado, documento, ocr, pagina, pdf, planilha, universal, interceptador | 2 |
| 69 | `eldorado/motores/leitura/ocr.py` | O OCR (reserva, extra 'ocr'): RapidOCR, leve; só para o PDF digitalizado e as imagens. | desligado (ninguém o usa nem o aciona) | leitores |  | 1 |
| 70 | `eldorado/motores/leitura/pagina.py` | A leitura de páginas: estrutura, links, tabelas, texto limpo, dados embutidos e o sistema do site. | em funcionamento | leitores | leitores | 0 |
| 71 | `eldorado/motores/leitura/pdf.py` | O leitor de PDF: o texto literal por página (com o expurgo seguro), as tabelas e as páginas que precisam de OC | em funcionamento | expurgo, leitores | motor, leitores, interceptador | 1 |
| 72 | `eldorado/motores/leitura/planilha.py` | Planilhas XLSX, XLS, XLSB e ODS (python-calamine, 13× mais rápido que o openpyxl, medido). Uma página por aba. | em funcionamento | leitores | leitores | 0 |
| 73 | `eldorado/motores/leitura/universal.py` | O leitor universal de reserva (Apache Tika, extra 'universal'): mais de mil formatos, quando nenhum outro lê. | desligado por desenho | leitores |  | 0 |

## 07 Pertinência e missão

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 74 | `eldorado/base/cerebro/pertinencia.py` | A Pertinência: decide se cada achado é oportunidade (pelo portão da missão) e mede a saída de cada etapa. | em funcionamento | contratos, eventos, registro | passagem, nó 3 «decidir»; passagem, nó 9 «decidir_rede» | 3 |
| 75 | `eldorado/base/missao/__init__.py` |  | pacote |  |  | 6 |
| 76 | `eldorado/base/missao/chave.py` | A chave do livro nesta missão: o livro é o PROGRAMA, não a edição. | em funcionamento |  | indice, importar_eldorado0, oportunidades | 0 |
| 77 | `eldorado/base/missao/itens.py` | Os 12 itens do livro e o critério único da estrela (titular, 04/10/2026), aproveitado do Eldorado0. | em funcionamento |  | analise_externa, auditoria, cartorio, certificacao, selos, importar_eldorado0, oportunidades, visoes, interceptador | 0 |
| 78 | `eldorado/base/missao/regras_portao.py` | As regras do portão da missão das oportunidades — aproveitadas do Eldorado0, com fidelidade. | em funcionamento |  | auditoria, portao | 0 |
| 79 | `eldorado/base/missao/portao.py` | O portão da missão das oportunidades (titular, 16/10/2026), com as regras aproveitadas do Eldorado0. | em funcionamento | regras_portao | auditoria, oportunidades | 0 |
| 80 | `eldorado/base/missao/oportunidades.py` | A missão das oportunidades, no contrato da plataforma: itens, chave e portão. | em funcionamento | chave, itens, portao, contratos | passagem, nó «cartorio» (parâmetro); passagem, nó «decidir_rede» (parâmetro); passagem, nó «decidir» (parâmetro); passag | 6 |

## 08 Cartório · etapas 1 e 2 (recepção e certificação)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 81 | `eldorado/base/cartorio/certificacao.py` | A certificação: cada item no texto oficial, com o valor, o trecho e a página. | em funcionamento | itens, eventos | auditoria, cartorio | 1 |
| 82 | `eldorado/base/cartorio/indice.py` | O índice: cria o livro ou vincula ao existente pela chave da missão; reconhece o mesmo edital em canais difere | em funcionamento | chave, contratos, eventos | cartorio | 1 |
| 83 | `eldorado/base/cartorio/passaporte.py` | O passaporte: move o livro entre as fases só com a autorização da Regência, e registra as tentativas (até 3). | em funcionamento | regencia, eventos | analise_externa, auditoria, cartorio, encaminhamento | 1 |
| 84 | `eldorado/base/cartorio/selos.py` | Os dois selos de cada livro, calculados a cada passagem. | em funcionamento | itens, eventos | auditoria, cartorio | 0 |
| 85 | `eldorado/base/cartorio/site_oficial.py` | O site oficial: a oportunidade se encontra NA FONTE (titular, 14/10/2026). | em funcionamento |  | auditoria, cartorio, interceptador | 0 |
| 86 | `eldorado/base/cartorio/cartorio.py` | O Cartório (titular, 22/10/2026): o ORGANIZADOR. Ele não busca nada: é onde o livro recebe informação nova, é | em funcionamento | auditoria, certificacao, indice, passaporte, selos, site_oficial, itens, contratos, eventos, registro | passagem, nó 11 «validar»; passagem, nó 5 «cartorio» | 3 |

## 09 Cartório · validação (auditoria e arquivo)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 87 | `eldorado/base/cartorio/auditoria.py` | A auditoria de cada livro: a validação individual e a decupagem dos dados em colunas (livro_dados). | em funcionamento | certificacao, passaporte, selos, site_oficial, itens, portao, regras_portao, eventos, normalizar | passagem, nó 7 «auditar» | 3 |

## 10 Cartório · etapa 3 (a rede neural encaminha)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 88 | `eldorado/motores/pilotos/__init__.py` |  | pacote |  |  | 1 |
| 89 | `eldorado/motores/pilotos/espiao.py` | achados por voo; fontes novas propostas | a construir |  |  | 0 |
| 90 | `eldorado/motores/pilotos/interceptador.py` | O PILOTO INTERCEPTADOR (do Eldorado0, titular, 26/09/2026): "o Espião descobre; o Interceptador comprova". | em funcionamento | site_oficial, itens, contratos, eventos, arquivo_web, escada, estrutura_site, fonte_oficial, leitores, pdf | encaminhamento | 1 |
| 91 | `eldorado/base/cerebro/encaminhamento.py` | A rede neural na fase 3 do Cartório (titular, 22/10/2026): quem age é a rede, não o Cartório. | em funcionamento | passaporte, regencia, eventos, registro, api, escada, leve, interceptador | passagem, nó 8 «encaminhar» | 1 |

## 11 Cartório · etapa 5 (análise externa)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 92 | `eldorado/base/cartorio/analise_externa.py` | A etapa 5 do Cartório: a ANÁLISE EXTERNA pelo Claude no Chrome (titular, 22/10/2026). | em funcionamento | cartorio, passaporte, itens, eventos | passagem, nó 13 «analise_externa» | 1 |
| 93 | `eldorado/base/verificacao/importacao.py` | respostas importadas e recusadas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 94 | `eldorado/base/verificacao/lote.py` | lotes gerados | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 95 | `eldorado/base/verificacao/relatorio_faltas.py` | livros com relatório final | substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) |  |  | 0 |
| 96 | `eldorado/base/verificacao/verificacao.py` | livros em verificação; decisões recebidas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |

## 12 Farol e transferência

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 97 | `eldorado/base/transferencia/farol.py` | livros transferidos; recusados pelo contrato | a construir |  |  | 0 |

## 13 Aprender e medir

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 98 | `eldorado/base/cerebro/aprendizado.py` | O ciclo de aprendizado: temporário (30 dias) → permanente, se funcionou; arquivado, se falhou; vencido, sai. | em funcionamento | eventos | passagem, nó 14 «aprender» | 2 |
| 99 | `eldorado/base/cerebro/completude.py` | A completude do dia: o que estava devido foi lido? O que precisa ser reacionado? | em funcionamento | eventos | passagem, nó 15 «completude» | 2 |
| 100 | `eldorado/base/cerebro/inventario.py` | O inventário do sistema (titular, 22/10/2026): todo arquivo, do primeiro ao último no caminho do funcionamento | em funcionamento |  | comandos | 1 |
| 101 | `eldorado/base/cerebro/medicao.py` | O motor de indicadores: ponto, círculo e linhas de cada arquivo, e a agregação por componente, parte e sistema | em funcionamento | eventos | passagem, nó 16 «medir» | 2 |
| 102 | `eldorado/base/cerebro/rede.py` | A rede neural única, de aprendizado contínuo (River): aprende a cada veredito e dá as notas. | desligado (ninguém o usa nem o aciona) | eventos |  | 1 |
| 103 | `eldorado/base/cerebro/regras.py` | A tabela única de regras e decisões da titular. | desligado (ninguém o usa nem o aciona) | eventos |  | 1 |

## 14 Análise e painel

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 104 | `eldorado/base/analise/calendario.py` | calendário atualizado na passagem | a construir |  |  | 0 |
| 105 | `eldorado/base/analise/historia.py` | livros com história completa | a construir |  |  | 0 |
| 106 | `eldorado/base/analise/preditivo.py` | alertas emitidos antes da abertura | a construir |  |  | 0 |
| 107 | `eldorado/base/painel/__init__.py` |  | pacote |  |  | 1 |
| 108 | `eldorado/base/painel/api.py` | respostas no prazo; erros | a construir |  |  | 0 |
| 109 | `eldorado/base/painel/maquina.py` | mostrador atualizado em tempo real | a construir |  |  | 0 |
| 110 | `eldorado/base/painel/sala.py` | sala publicada no prazo | a construir |  |  | 0 |
| 111 | `eldorado/base/painel/visoes.py` | As visões do painel: o que cada tela mostra, lido dos bancos (só leitura), num único arquivo de dados. | em funcionamento | itens | comandos | 1 |

## 16 Migração do Eldorado0 (temporária)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 112 | `eldorado/base/migracao/__init__.py` |  | pacote |  |  | 1 |
| 113 | `eldorado/base/migracao/importar_eldorado0.py` | A migração do Eldorado0 (temporária, 30 dias): livros, certidões, documentos, vereditos, selos, leis, empresas | em funcionamento | chave, itens, eventos | comandos | 1 |

## 17 Outros

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 114 | `.github/workflows/painel.yml` |  | em funcionamento |  |  | 0 |
| 115 | `.github/workflows/passagem.yml` | passagens no horário | substituído por .github/workflows/eldorado.yml (funcionamento permanente) |  |  | 0 |
| 116 | `.github/workflows/pilotos.yml` | voos com sucesso | substituído por .github/workflows/eldorado.yml (os pilotos rodam dentro do funcionamento permanente) |  |  | 0 |
| 117 | `eldorado/__init__.py` |  | pacote |  |  | 32 |
| 118 | `eldorado/base/__init__.py` |  | pacote |  |  | 29 |
| 119 | `eldorado/base/cartorio/__init__.py` |  | pacote |  |  | 5 |
| 120 | `eldorado/base/cerebro/__init__.py` |  | pacote |  |  | 14 |
| 121 | `eldorado/base/investigacao/investigacao.py` | livros investigados e itens comprovados por livro | substituído por eldorado/base/cerebro/encaminhamento.py e eldorado/motores/pilotos/interceptador.py |  |  | 0 |
| 122 | `eldorado/motores/__init__.py` |  | pacote |  |  | 8 |

## Os 47 motores (45 regulares e 2 pilotos)

| # | Tipo | Motor (Eldorado0) | Nome | Motor novo | Situação | Observação |
|---|---|---|---|---|---|---|
| 1 | regular | do-goiania | Diário Oficial do Município de Goiânia | — | a construir |  |
| 2 | regular | do-goias | Diário Oficial do Estado de Goiás | — | a construir |  |
| 3 | regular | dou | Diário Oficial da União | dou | em funcionamento |  |
| 4 | regular | dj-trf1-go | Diário da Justiça Federal — Seção Judiciária de Goiás | — | a construir |  |
| 5 | regular | camara-goiania-pl | Câmara Municipal de Goiânia — processos legislativos | — | a construir |  |
| 6 | regular | alego-pl | Assembleia Legislativa de Goiás — proposições | — | a construir |  |
| 7 | regular | congresso-nacional | Congresso Nacional — Câmara, Senado e Comissões | — | a construir |  |
| 8 | regular | pncp-api | PNCP — API de contratações (chamamentos e credenciamentos) | pncp | em funcionamento |  |
| 9 | regular | judiciario-tjgo | TJ-GO — editais das comarcas (prestações pecuniárias) | — | a construir |  |
| 10 | regular | judiciario-cnj | CNJ — destinação de prestações pecuniárias | — | a construir |  |
| 11 | regular | mpgo-destinacao | MP-GO — Programa Destina | — | a construir |  |
| 12 | regular | mptgo-destinacao | MPT-GO — editais de indicação de entidades | — | a construir |  |
| 13 | regular | mpu-destinacao | MPU — MPF, MPDFT, MPM e MPT nacional: destinações | — | a construir |  |
| 14 | regular | plataforma-wordpress | Adaptador WordPress — sites oficiais pela API | wordpress-goias | em funcionamento | Secult-GO e SEDS-GO; as demais secretarias entram como fontes |
| 15 | regular | plataforma-mapas-culturais | Adaptador Mapas Culturais — oportunidades | mapas-culturais | em funcionamento |  |
| 16 | regular | outras-oportunidades | Outras Oportunidades | — | a construir |  |
| 17 | regular | motor-gife | Motor Incentivos Fiscais — empresas da base | — | a construir | empresas que distribuem renúncia fiscal (especial.db) |
| 18 | regular | motor-patrocinio | Motor Patrocínio Privado — mídia e eventos | — | a construir |  |
| 19 | regular | gife | GIFE — Grupo de Institutos, Fundações e Empresas | wordpress-financiadores | em funcionamento |  |
| 20 | regular | salic | Lei Rouanet — janela de propostas no SALIC | rouanet | em funcionamento | a API do Salic (projetos de Goiás) vai à análise do painel |
| 21 | regular | prefeituras-50-go | Prefeituras das 25 maiores cidades de Goiás | — | a construir | há o catálogo de rotas das 25 prefeituras no projeto |
| 22 | regular | empresas-editais-incentivados | Empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas/Pronon | — | a construir |  |
| 23 | regular | cnpq-extensao | CNPq / MCTI / Setec-MEC — chamadas com componente de extensão | — | a construir |  |
| 24 | regular | estaduais-go-gov | Oportunidades estaduais governamentais de Goiás | — | a construir | Goyazes já cobre o incentivo estadual à cultura |
| 25 | regular | site-farol-cultural | Farol Cultural | — | a construir |  |
| 26 | regular | site-capitaai | CapitaAI | — | a construir |  |
| 27 | regular | site-observatorio-terceiro-setor | Observatório do Terceiro Setor | — | a construir |  |
| 28 | regular | site-mapas-culturais | Mapas Culturais — redes estaduais | mapas-culturais | parcial | só o Mapa da Cultura federal; faltam as redes estaduais |
| 29 | regular | site-abcr | ABCR — Associação Brasileira de Captadores de Recursos | wordpress-financiadores | parcial | fonte Captadores (Capta) |
| 30 | regular | site-funarte | Funarte | — | a construir |  |
| 31 | regular | site-transferegov | Transferegov — programas e parcerias com OSC | transferegov | em funcionamento |  |
| 32 | regular | site-rede-comua | Rede Comuá | — | a construir |  |
| 33 | regular | site-fundo-baoba | Fundo Baobá | — | a construir |  |
| 34 | regular | site-editais-culturais | Editais Culturais | — | a construir |  |
| 35 | regular | site-fundo-brasil | Fundo Brasil de Direitos Humanos | wordpress-financiadores | em funcionamento |  |
| 36 | regular | site-idis | IDIS | — | a construir |  |
| 37 | regular | site-undef | UNDEF — Fundo das Nações Unidas para a Democracia | — | a construir |  |
| 38 | regular | site-fundo-casa | Fundo Casa Socioambiental | wordpress-financiadores | em funcionamento |  |
| 39 | regular | site-cese | CESE — Coordenadoria Ecumênica de Serviço | wordpress-financiadores | em funcionamento |  |
| 40 | regular | site-brazilfoundation | BrazilFoundation | — | a construir |  |
| 41 | regular | site-rede-filantropia | Rede Filantropia | — | a construir |  |
| 42 | regular | site-mapa-osc | Mapa das OSC (Ipea) | — | a construir |  |
| 43 | regular | site-prosas | Prosas | — | a construir |  |
| 44 | regular | (novo) goyazes | Programa Goyazes — incentivo estadual à cultura | goyazes | em funcionamento | fonte nova do sistema novo |
| 45 | regular | (novo) querido-diario | Querido Diário — diários municipais | querido-diario | sem fonte | a API da fonte está fora do ar desde 22/10 |
| 46 | piloto | piloto-aberto | Piloto Espião — busca livre (privado e internacional) | — | a construir | motores/pilotos/espiao.py |
| 47 | piloto | piloto-interceptador | Piloto Interceptador — comprova na fonte oficial | interceptador | parcial | as 10 abordagens funcionam; falta a IA (o trecho literal item a item) |
