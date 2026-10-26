# Mapa do sistema Eldorado

Gerado pelo comando `eldorado inventario` a partir do código, da passagem e da configuração. É o catálogo da medição e a base do monitoramento em tempo real.

## Situação dos arquivos

| Situação | Arquivos |
|---|---|
| em funcionamento | 156 |
| pacote | 24 |
| a construir | 7 |
| substituído por eldorado/base/cartorio/analise_externa.py | 3 |
| substituído por eldorado/banco/biblioteca/esquema.py (as empresas na Biblioteca, regra R08) | 2 |
| desligado por desenho | 2 |
| substituído por eldorado/banco/biblioteca (o Especial unido à Biblioteca, regra R08) | 1 |
| o teste da ponte da HostGator, sob demanda (o ciclo testa a ponte no início) | 1 |
| aguarda a decisão da titular: fica até a decisão da titular: nenhum código a lê (criada na fase 4, 22/10/2026); as dispensas prováveis por regime de recurso: ligar ao checklist do Cartório ou retirar | 1 |
| substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) | 1 |
| substituído por eldorado/base/analise/previsao.py (o calendário das abertas e das previstas) | 1 |
| substituído por eldorado/base/analise/previsao.py (a história do livro) | 1 |
| substituído por eldorado/base/analise/previsao.py (a previsão da próxima abertura e o alerta) | 1 |
| aguarda a decisão da titular: fica (titular, 25/10/2026): a comprovação de cobertura antes de eliminar o Eldorado0 ainda não foi feita | 1 |
| estudo concluído (25/10/2026): uma IA para as três funções; só sob demanda | 1 |
| estudo concluído (25/10/2026): o arranjo das IAs e o contexto; só sob demanda | 1 |
| estudo concluído (25/10/2026): uma IA para as três funções (o resultado no parecer); só sob demanda | 1 |
| estudo concluído (25/10/2026): o arranjo das IAs e o contexto (o resultado no parecer); só sob demanda | 1 |


## 01 Operação: o que acorda, implanta e confere o sistema

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 1 | `.github/workflows/implantar.yml` | name: Implantar (parar, implantar e religar) A regra R09 da titular (25/10/2026, a segunda forma): nunca o mei | em funcionamento | passagem |  | 0 |
| 2 | `config/arquivos.json` | O catálogo dos arquivos do sistema (o inventário). | em funcionamento |  | inventario, mapa_arquivos, medicao, comandos | 0 |
| 3 | `config/eldorado.toml` | Configuração do Eldorado. Validada na carga: chave desconhecida ou valor fora do limite impede a passagem. | em funcionamento |  | comandos, config | 0 |
| 4 | `eldorado/__init__.py` |  | pacote |  |  | 82 |
| 5 | `eldorado/base/__init__.py` |  | pacote |  |  | 64 |
| 6 | `eldorado/base/nucleo/comandos.py` | Os comandos da plataforma: os mesmos no GitHub, no computador da titular e (depois) no painel. | em funcionamento | analise, consolidar, consulta, drive, manutencao, memoria, analise_externa, releitura, fila, governador, inventario, pilotos, pilotos_permanentes, importar_e0, agenda, definicao, executor, fila, nos, importar_eldorado0, config, eventos, expurgo_externo, gravador, ia, api, dados, visoes, api, escada, leve, navegador, ponte_br, fabrica, motor, otimizacao | .github/workflows/eldorado.yml (eldorado permanente) | 2 |
| 7 | `scripts/gravar.sh` | !/usr/bin/env bash Grava o trabalho no repositório: os eventos sempre (texto, pequeno); o banco uma vez por di | em funcionamento |  | eldorado | 0 |
| 8 | `scripts/instalar_bibliotecas.py` | As bibliotecas do plano, em camadas independentes (scripts/instalar.sh): o núcleo é obrigatório; cada grupo do | em funcionamento |  | qualidade, instalar | 0 |
| 9 | `scripts/visualizar_sala.py` | Abre a sala de controle num navegador, fotografa em três alturas de rolagem e mede os quadros ao rolar (o flux | em funcionamento |  | visualizar | 0 |
| 10 | `.github/workflows/painel.yml` | O painel (titular, 23/10/2026): a imagem atual do sistema. A página é a do Eldorado0 (o HTML, os scripts e as  | em funcionamento | comandos, passagem |  | 0 |
| 11 | `.github/workflows/qualidade.yml` | Qualidade: a cada gravação, instala as dependências fixadas, roda o verificador e a bateria inteira. name: Qua | em funcionamento | comandos, instalar_bibliotecas |  | 0 |
| 12 | `.github/workflows/visualizar.yml` | name: Visualizar a sala de controle | em funcionamento | comandos, visualizar_sala |  | 0 |
| 13 | `scripts/instalar.sh` | !/usr/bin/env bash A instalação completa do Eldorado (plano C: as ferramentas adotadas), usada por todos os fl | em funcionamento | settings, instalar_bibliotecas | diagnostico, eldorado, experimentar-motor, gravar-paginas, ia-teste | 0 |
| 14 | `.github/workflows/diagnostico.yml` | Diagnóstico (análise externa): sonda endereços a partir do GitHub, que alcança a internet, e publica o resulta | em funcionamento | comandos, instalar |  | 0 |
| 15 | `.github/workflows/eldorado.yml` | O Eldorado em FUNCIONAMENTO PERMANENTE (titular, 22/10/2026): sem horário fixo, sem trabalho e descanso. Cada  | em funcionamento | ia_local, comandos, gravar, instalar, passagem |  | 0 |

## 02 Núcleo: contratos, eventos e gravação

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 16 | `eldorado/base/nucleo/__init__.py` |  | pacote |  |  | 44 |
| 17 | `eldorado/base/nucleo/config.py` | A configuração da plataforma, validada na carga. | em funcionamento |  | comandos | 1 |
| 18 | `eldorado/base/nucleo/contratos.py` | Os contratos do Eldorado. | em funcionamento |  | cartorio, indice, pertinencia, regencia, oportunidades, eventos, gravador, registro, motor, espiao, interceptador | 14 |
| 19 | `eldorado/base/nucleo/expurgo_externo.py` | O expurgo físico pela análise externa (titular, 22/10/2026): "o sistema não apaga nada, mas o Claude pode apag | em funcionamento |  | comandos | 1 |
| 20 | `eldorado/base/nucleo/seguranca.py` | A segurança dos textos lidos: os padrões de injeção de instruções (prompt injection). | em funcionamento |  | motor, leitores | 1 |
| 21 | `eldorado/base/nucleo/eventos.py` | Os eventos: a única forma de escrita do Eldorado. | em funcionamento | contratos | analise_externa, auditoria, cartorio, certificacao, indice, passaporte, selos, aprendizado, completude, encaminhamento,  | 29 |
| 22 | `eldorado/base/nucleo/alarmes.py` | Nenhum erro é engolido: todo erro vira um evento de alarme, e o erro continua subindo. | em funcionamento | eventos | executor | 1 |
| 23 | `eldorado/base/nucleo/gravador.py` | O gravador único: o único que escreve nos bancos. | em funcionamento | _sqlite, contratos, eventos | nos, comandos, estado | 3 |
| 24 | `eldorado/base/nucleo/recibo.py` | A medição de uma chamada: tempo, processador e memória de pico, e se deu certo. | em funcionamento | eventos | regencia, executor | 0 |
| 25 | `eldorado/base/nucleo/registro.py` | O registro dos módulos ligados: confere o contrato antes de aceitar, e arquiva em vez de apagar. | em funcionamento | contratos, eventos | cartorio, encaminhamento, pertinencia, regencia | 7 |

## 03 Bancos

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 26 | `eldorado/banco/__init__.py` |  | pacote |  |  | 6 |
| 27 | `eldorado/banco/_sqlite.py` | Abertura padronizada dos bancos SQLite: configurações medidas, criação do esquema, versão e integridade. | em funcionamento |  | esquema, esquema, gravador | 1 |
| 28 | `eldorado/banco/analise.py` | As análises sobre os bancos (plano C: DuckDB): o rendimento de cada motor, o funil do Cartório, os achados por | em funcionamento |  | comandos, api | 0 |
| 29 | `eldorado/banco/biblioteca/__init__.py` |  | pacote |  |  | 5 |
| 30 | `eldorado/banco/biblioteca/leis.py` | leis atualizadas | a construir |  |  | 0 |
| 31 | `eldorado/banco/biblioteca/livro.py` | leituras e acréscimos por livro | a construir |  |  | 0 |
| 32 | `eldorado/banco/biblioteca/texto.py` | taxa de compressão; busca em menos de 1 ms | a construir |  |  | 0 |
| 33 | `eldorado/banco/cerebro_db/__init__.py` |  | pacote |  |  | 1 |
| 34 | `eldorado/banco/consulta.py` | A consulta da Biblioteca (plano C: Datasette), só leitura, com consultas prontas. | em funcionamento |  | comandos | 1 |
| 35 | `eldorado/banco/drive.py` | A cópia dos bancos e dos eventos no Drive (plano C: a API do Google; o rclone de alternativa). | em funcionamento |  | comandos | 0 |
| 36 | `eldorado/banco/especial/__init__.py` | testes verdes e uso registrado | substituído por eldorado/banco/biblioteca (o Especial unido à Biblioteca, regra R08) |  |  | 0 |
| 37 | `eldorado/banco/especial/empresas.py` | empresas atualizadas | substituído por eldorado/banco/biblioteca/esquema.py (as empresas na Biblioteca, regra R08) |  |  | 0 |
| 38 | `eldorado/banco/especial/esquema.py` | O esquema do Especial (especial.db): as empresas, os incentivos e as oportunidades nas empresas conhecidas. | substituído por eldorado/banco/biblioteca/esquema.py (as empresas na Biblioteca, regra R08) |  |  | 0 |
| 39 | `eldorado/banco/fotografia.py` | última fotografia; reconstrução testada | a construir |  |  | 0 |
| 40 | `eldorado/banco/manutencao.py` | A manutenção dos bancos e a busca por texto (plano C: sqlite-utils). | em funcionamento |  | comandos, api | 0 |
| 41 | `eldorado/banco/originais/drive.py` | originais no Drive × documentos citados | a construir |  |  | 0 |
| 42 | `eldorado/base/especial/__init__.py` |  | pacote |  |  | 2 |
| 43 | `eldorado/base/especial/importar_e0.py` | A importação das empresas do Eldorado0 (titular, 25/10/2026: 22.174 empresas com os programas validados deveri | em funcionamento |  | comandos | 1 |
| 44 | `eldorado/base/especial/registro.py` | O registro das empresas e dos incentivos (na Biblioteca: os livros e as empresas no mesmo banco, titular 24/10 | em funcionamento | eventos | regencia | 1 |
| 45 | `eldorado/banco/biblioteca/esquema.py` | O esquema da Biblioteca (biblioteca.db): os livros e tudo o que se sabe de cada oportunidade. | em funcionamento | _sqlite | consolidar, nos | 3 |
| 46 | `eldorado/banco/cerebro_db/esquema.py` | O esquema do banco do Cérebro (cerebro.db): a operação e o aprendizado do sistema, sem nenhuma oportunidade. | em funcionamento | _sqlite | nos, estado, espiao | 1 |
| 47 | `eldorado/banco/consolidar.py` | A consolidação dos bancos (titular, 24/10/2026): só o Cérebro tem um banco paralelo, o de aprendizado; os livr | em funcionamento | esquema, estado, espiao | comandos | 0 |

## 04 Execução: workflow, executor e fila (a engenharia do n8n)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 48 | `eldorado/base/fluxo/__init__.py` |  | pacote |  |  | 19 |
| 49 | `eldorado/base/fluxo/agenda.py` | A agenda: quais módulos estão devidos agora. | em funcionamento |  | regencia, comandos | 4 |
| 50 | `eldorado/base/fluxo/definicao.py` | A definição de um workflow (conceito do n8n, reescrito do zero para o Eldorado). | em funcionamento |  | executor, fila, comandos | 6 |
| 51 | `eldorado/base/fluxo/nos.py` | Os nós próprios da plataforma, usados nos workflows de operação (manutenção, aplicação de eventos). | em funcionamento | esquema, esquema, governador, eventos, gravador | passagem, nó 16 «aplicar_rede»; passagem, nó 18 «aplicar_validacao»; passagem, nó 26 «maquina»; passagem, nó 37 «aplicar | 13 |
| 52 | `workflows/passagem.toml` | A passagem: planejar, acionar, decidir, aplicar, certificar no Cartório, aprender, conferir a completude e med | em funcionamento | previsao, avaliar, curador, memoria, analise_externa, auditoria, cartorio, identidade, releitura, aprendizado, completude, encaminhamento | eldorado, ia-teste, implantar, painel, inventario, mapa_arquivos, comandos | 0 |
| 53 | `eldorado/base/fluxo/executor.py` | O executor durável dos workflows. | em funcionamento | definicao, alarmes, eventos, recibo | fila, comandos | 5 |
| 54 | `eldorado/base/fluxo/fila.py` | A fila de tarefas (Huey sobre SQLite): executa workflows, sob o governador e a pausa do sistema. | em funcionamento | governador, definicao, executor | comandos | 1 |

## 05 Comandante: percebe, decide, organiza as filas, comanda os pilotos, parametriza e apresenta

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 55 | `config/agenda.toml` | O PONTO DE PARTIDA do aprendizado (titular, 22/10/2026: o Eldorado não tem horário fixo). Quem decide é o Cére | em funcionamento |  | regencia, comandos, dados | 0 |
| 56 | `config/cargos.toml` | Os cargos da IA (titular, 25/10/2026): uma única Qwen3-8B para o Comandante e os dois pilotos, cada um na SUA  | em funcionamento |  | ia | 0 |
| 57 | `config/ia_local.toml` | A IA local dos pilotos (do Eldorado0, titular, 26/09/2026): um único modelo no sistema, o Qwen3-8B, servido pe | em funcionamento |  | bench-ia, bench-ia2, eldorado, ia-teste | 0 |
| 58 | `config/modulos.toml` | Os módulos ligados. Cada motor é um arquivo de configuração do motor genérico (eldorado/motores/canal/config/) | em funcionamento | registro, alego-pl, camara-goiania-pl, cnpq-extensao, congresso-nacional, dj-trf1-go, do-goiania, do-goias, dou, empresas-editais-incentivados, estaduais-go-gov, gife | encaminhamento, inventario, mapa_arquivos, pilotos_permanentes, regencia, dados, sala | 0 |
| 59 | `eldorado/base/cerebro/__init__.py` |  | pacote |  |  | 29 |
| 60 | `eldorado/base/cerebro/decisao.py` | A decisão do Cérebro: a cada batimento, quais motores acionar, conforme a necessidade (titular, 22/10/2026). | em funcionamento |  | fila, regencia | 1 |
| 61 | `eldorado/base/cerebro/governador.py` | O governador de carga: mantém a máquina abaixo do limite (85%). | em funcionamento | eventos | regencia, fila, nos, comandos | 6 |
| 62 | `eldorado/base/cerebro/livros_motores.py` | Os motores de cada livro e as pesquisas já feitas (comum ao encaminhamento e à vigilância dos sites originais; | em funcionamento | motor | encaminhamento, originais | 0 |
| 63 | `eldorado/base/cerebro/pilotos.py` | O Cérebro dos pilotos (titular, 22/10/2026): mede a recorrência de cada piloto e manda nova missão sempre que | em funcionamento | escada, metabusca, leitores, espiao | encaminhamento, pilotos_permanentes, comandos | 2 |
| 64 | `eldorado/base/comandante/__init__.py` | O Comandante (titular, 25/10/2026): o responsável por executar e coordenar todo o sistema — perceber o estado, | pacote |  |  | 6 |
| 65 | `eldorado/base/comandante/organizar.py` | O Comandante organiza os livros do Cartório (a etapa C6; titular, 25/10/2026: "não existem 5 mil livros e nem  | em funcionamento | auditoria, identidade | passagem, nó 29 «organizar_livros» | 1 |
| 66 | `eldorado/base/comandante/parametros.py` | Os parâmetros do Comandante (as etapas C7 e C9; titular, 25/10/2026). Cada parâmetro de cada etapa vive no Arq | em funcionamento |  | passagem, nó 34 «conferir» | 0 |
| 67 | `eldorado/base/comandante/politica.py` | A política de decisão do Comandante: o Vowpal Wabbit (o bandido contextual SquareCB), eleito no estudo (92% a  | em funcionamento |  | decidir, pilotos | 0 |
| 68 | `eldorado/base/nucleo/ia.py` | O serviço único de IA dos pilotos (do Eldorado0, titular, 26/09 e 02/10/2026). | em funcionamento | memoria, otimizacao | encaminhamento, pilotos_permanentes, apresentar, comandos, interceptador, otimizacao | 3 |
| 69 | `.github/workflows/ia-teste.yml` | Teste dos pilotos no GitHub: uma missão real do Espião e a IA local (análise externa): os mesmos passos do fun | em funcionamento | ia_local, __init__, comandos, ia, instalar, passagem |  | 0 |
| 70 | `eldorado/base/cerebro/originais.py` | A rede neural vigia os sites ORIGINAIS dos livros (titular, 23/10/2026): com o histórico do livro, ele tem um  | em funcionamento | livros_motores | encaminhamento | 2 |
| 71 | `eldorado/base/cerebro/regencia.py` | A Regência: planeja a passagem, aciona os motores e autoriza cada passagem de livro. | em funcionamento | decisao, governador, rede, registro, agenda, contratos, eventos, recibo, registro, sala, motor | passagem, nó 4 «planejar»; passagem, nó 5 «acionar» | 12 |
| 72 | `eldorado/base/comandante/apresentar.py` | O Comandante apresenta à titular (a etapa C10; a fase 6 do desenho, titular, 25/10/2026): o que foi encontrado | em funcionamento | ia | passagem, nó 36 «apresentar» | 1 |
| 73 | `eldorado/base/comandante/decidir.py` | O Comandante decide (a etapa C2), em PARALELO com a ordem fixa (a fase 2 do desenho): ordena todos os motores  | em funcionamento | politica | passagem, nó 31 «comandante_decidir» | 1 |
| 74 | `eldorado/base/comandante/escolher.py` | O nó de agente do Comandante (a fase 3 do desenho; a engenharia do n8n, titular, 25/10/2026): no início de cad | em funcionamento | parametros | passagem, nó 30 «comandante_escolher» | 0 |
| 75 | `eldorado/base/cerebro/fila.py` | A fila do sistema (titular, 22/10/2026): o Eldorado funciona de forma permanente, sem horário de trabalho e de | em funcionamento | decisao, regencia | encaminhamento, comandos | 0 |
| 76 | `eldorado/base/comandante/pilotos.py` | O Comandante comanda os pilotos (a etapa C5; a fase 4 do desenho, titular, 25/10/2026). Cada missão do Espião  | em funcionamento | decidir, parametros, politica | pilotos_permanentes | 0 |
| 77 | `eldorado/base/cerebro/encaminhamento.py` | A rede neural na fase 3 do Cartório (titular, 22/10/2026): quem age é a rede, não o Cartório. | em funcionamento | passaporte, fila, livros_motores, originais, pilotos, pilotos_permanentes, rede, regencia, eventos, ia, registro, completa, metabusca, enriquecer, interceptador | passagem, nó 12 «encaminhar»; passagem, nó 13 «espiao»; passagem, nó 14 «originais» | 5 |
| 78 | `eldorado/base/cerebro/pilotos_permanentes.py` | Os pilotos de forma permanente (titular, 25/10/2026: "execute eles de forma permanente, da forma que foram des | em funcionamento | encaminhamento, pilotos, rede, parametros, pilotos, eventos, ia, metabusca, interceptador | encaminhamento, comandos | 0 |

## 06 Coleta: os motores, o canivete suíço e a ponte BR

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 79 | `.github/workflows/experimentar-motor.yml` | Experimentar motor (orientação de criação, passo 8): roda o motor inteiro no GitHub, com a internet de verdade | em funcionamento | comandos, instalar |  | 0 |
| 80 | `.github/workflows/gravar-paginas.yml` | Gravar páginas (orientação de criação de motores, passo 3 e 8): grava as respostas reais inteiras das rotas de | em funcionamento | comandos, instalar |  | 0 |
| 81 | `config/motores_previstos.json` | O estudo da titular: os 47 motores, os alvos e o aprendizado do Eldorado0. | em funcionamento |  | inventario, mapa_arquivos, dados, fabrica | 0 |
| 82 | `config/ponte_dominios.txt` | Os domínios lidos pela ponte da HostGator (o IP brasileiro): a mesma lista que o ponte.php aceita (do Eldorado | em funcionamento |  | ponte_br | 0 |
| 83 | `config/searxng/settings.yml` | O SearXNG do próprio fluxo (plano C: a metabusca própria, sem custo): só local, sem limitador, com a saída em  | em funcionamento |  | mapa_arquivos, instalar | 0 |
| 84 | `eldorado/base/motor_modelo/__init__.py` |  | pacote |  |  | 0 |
| 85 | `eldorado/motores/__init__.py` |  | pacote |  |  | 32 |
| 86 | `eldorado/motores/acesso/__init__.py` |  | pacote |  |  | 8 |
| 87 | `eldorado/motores/acesso/escada.py` | A escada de acesso: do degrau mais leve ao mais forte, aprendendo por domínio qual degrau funciona. | em funcionamento | eventos | releitura, pilotos, comandos, api, arquivo_web, completa, leve, local, navegador, ponte_br, rotas_alternativas, motor, f | 7 |
| 88 | `eldorado/motores/canal/__init__.py` |  | pacote |  |  | 16 |
| 89 | `eldorado/motores/canal/achado.py` | achados completos | a construir |  |  | 0 |
| 90 | `eldorado/motores/canal/estado.py` | O aprendizado de cada motor, entregue ao Cérebro (titular, 24/10/2026): NENHUM motor tem banco de dados. O mot | em funcionamento | esquema, eventos, gravador | consolidar, dados, visoes, motor | 2 |
| 91 | `eldorado/motores/descoberta/__init__.py` |  | pacote |  |  | 6 |
| 92 | `eldorado/motores/descoberta/pistas.py` | O formato comum das cinco formas de descoberta: a pista (título, link, data, de onde veio). | em funcionamento |  | motor, arquivos_web, dados_abertos, estrutura_site, mapa_original, metabusca | 3 |
| 93 | `eldorado/motores/descoberta/vigilancia.py` | Forma 5: a vigilância: só segue quando a página mudou. | em funcionamento |  | motor | 0 |
| 94 | `eldorado/motores/leitura/__init__.py` |  | pacote |  |  | 4 |
| 95 | `eldorado/motores/leitura/atos.py` | O recorte dos atos (canivete suíço): a edição inteira de um diário em PDF ou texto → um ato por cabeçalho. | em funcionamento |  | cadeia | 0 |
| 96 | `eldorado/motores/leitura/enriquecer.py` | O enriquecimento de cada achado (o canivete do motor padrão; plano C, as ferramentas adotadas): o que o texto  | em funcionamento |  | encaminhamento, motor | 1 |
| 97 | `eldorado/motores/leitura/expurgo.py` | O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição na página). | em funcionamento |  | pdf | 0 |
| 98 | `eldorado/motores/leitura/normalizar.py` | A normalização: datas, valores, números por extenso e CNPJ, a partir do texto literal. | em funcionamento |  | auditoria | 0 |
| 99 | `ponte/ponte.php` | PONTE BRASIL do Eldorado (25/10/2026): a mesma ponte do Eldorado0, com os domínios de TODOS os motores do sist | em funcionamento |  | ponte_br | 0 |
| 100 | `.github/workflows/ponte-teste.yml` | name: Ponte BR (teste) Testa a ponte da HostGator (o IP brasileiro) com os sites que recusam a nuvem (25/10/20 | o teste da ponte da HostGator, sob demanda (o ciclo testa a ponte no início) | __init__ |  | 0 |
| 101 | `eldorado/motores/acesso/arquivo_web.py` | Degrau 6: a cópia arquivada (Wayback Machine), quando o site está fora do ar ou bloqueou. | em funcionamento | escada | completa, motor, interceptador | 1 |
| 102 | `eldorado/motores/acesso/local.py` | Degrau 9: o computador da titular, quando o próprio site bloqueia o acesso remoto. | em funcionamento | escada | completa, motor | 1 |
| 103 | `eldorado/motores/acesso/navegador.py` | Degraus 3 a 5: os navegadores, para páginas que só existem depois do JavaScript. | em funcionamento | escada | comandos, completa, motor | 1 |
| 104 | `eldorado/motores/acesso/ponte_br.py` | A ponte da HostGator (titular, 25/10/2026): o IP brasileiro para os sites que recusam a nuvem (a CESE, o TJ-GO | em funcionamento | escada | comandos, api, completa, leve, motor | 0 |
| 105 | `eldorado/motores/descoberta/arquivos_web.py` | Forma 4: os arquivos da web: o índice da Wayback Machine lista as URLs já vistas de um domínio (inclusive edit | em funcionamento | pistas | motor | 0 |
| 106 | `eldorado/motores/descoberta/dados_abertos.py` | Forma 2: os dados abertos: as APIs oficiais (pela configuração de cada motor) e os portais CKAN (dados.gov.br  | em funcionamento | pistas | motor | 0 |
| 107 | `eldorado/motores/descoberta/estrutura_site.py` | Forma 3: a estrutura do site: o mapa do site, os feeds (RSS e Atom), a API do WordPress e os links da página. | em funcionamento | pistas | motor, mapa_original, interceptador | 2 |
| 108 | `eldorado/motores/descoberta/fonte_oficial.py` | Seguir até a fonte oficial: na página de DIVULGAÇÃO (notícia, post, agregador), o documento OFICIAL do edital. | em funcionamento | escada | motor, interceptador | 0 |
| 109 | `eldorado/motores/descoberta/metabusca.py` | Forma 1: a metabusca, o canivete de busca: SearXNG (serviço próprio), o DDGS por seis motores (Bing, Brave, Mo | em funcionamento | pistas | encaminhamento, pilotos, pilotos_permanentes, motor | 2 |
| 110 | `eldorado/motores/acesso/api.py` | Degrau 1: as APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN) com o ht | em funcionamento | escada, ponte_br | releitura, comandos, completa, motor | 4 |
| 111 | `eldorado/motores/acesso/leve.py` | Degrau 2: requisição leve com assinatura de navegador real (TLS e cabeçalhos de um Chrome). | em funcionamento | escada, ponte_br | releitura, comandos, completa, rotas_alternativas, motor | 1 |
| 112 | `eldorado/motores/descoberta/mapa_original.py` | O mapa do site ORIGINAL (titular, 23/10/2026): com o histórico do livro, ele tem um site de divulgação e um si | em funcionamento | estrutura_site, pistas | motor | 0 |
| 113 | `eldorado/motores/acesso/completa.py` | A escada completa (os 7 degraus) para quem não é motor: os pilotos e a releitura (o parecer do conselho, 24/10 | em funcionamento | api, arquivo_web, escada, leve, local, navegador, ponte_br | encaminhamento | 1 |
| 114 | `eldorado/motores/acesso/rotas_alternativas.py` | Degraus 7 e 8, reservas desligadas até o teste real na criação: o Tor (IP diferente) e o leitor público de pág | desligado por desenho | escada, leve |  | 1 |
| 115 | `eldorado/motores/canal/fabrica.py` | A fábrica de motores: executa a orientação de design (eldorado/motores/skills/criar-motor/SKILL.md). | em funcionamento | motor | comandos | 2 |
| 116 | `eldorado/motores/canal/motor.py` | O motor genérico de canal: um motor é uma CONFIGURAÇÃO (um arquivo TOML), sem código próprio. | em funcionamento | contratos, seguranca, api, arquivo_web, escada, leve, local, navegador, ponte_br, estado, arquivos_web, cadeia, dados_abertos, estrutura_site, fonte_oficial, mapa_original, metabusca, pistas, vigilancia, enriquecer, leitores, ocr, pdf | config/modulos.toml (alego-pl); config/modulos.toml (camara-goiania-pl); config/modulos.toml (cnpq-extensao); config/mod | 13 |
| 117 | `eldorado/motores/descoberta/cadeia.py` | A leitura em cadeia (canivete suíço): a lista → cada item → o detalhe → o texto, sem código por fonte. | em funcionamento | atos, leitores | motor | 0 |
| 118 | `eldorado/motores/leitura/audio.py` | O leitor de áudio e vídeo (plano C: faster-whisper): transcreve em português as transmissões e os vídeos que a | em funcionamento | leitores | leitores | 0 |
| 119 | `eldorado/motores/leitura/compactado.py` | Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo interno ao leitor do seu tipo. | em funcionamento | leitores | leitores | 0 |
| 120 | `eldorado/motores/leitura/documento.py` | Documentos DOCX (com cabeçalhos, rodapés e notas), ODT e PPTX (uma página por slide). | em funcionamento | leitores | leitores | 0 |
| 121 | `eldorado/motores/leitura/leitores.py` | O registro dos leitores: o canivete suíço da leitura. | em funcionamento | seguranca, audio, compactado, documento, ocr, pagina, pdf, planilha, universal | releitura, pilotos, motor, cadeia, audio, compactado, documento, ocr, pagina, pdf, planilha, universal, interceptador | 3 |
| 122 | `eldorado/motores/leitura/ocr.py` | O OCR (reserva, extra 'ocr'): RapidOCR, leve; só para o PDF digitalizado e as imagens. | em funcionamento | leitores | motor, leitores | 1 |
| 123 | `eldorado/motores/leitura/pagina.py` | A leitura de páginas: estrutura, links, tabelas, texto limpo, dados embutidos e o sistema do site. | em funcionamento | leitores | leitores | 0 |
| 124 | `eldorado/motores/leitura/pdf.py` | O leitor de PDF: o texto literal por página (com o expurgo seguro), as tabelas e as páginas que precisam de OC | em funcionamento | expurgo, leitores | motor, leitores, interceptador | 1 |
| 125 | `eldorado/motores/leitura/planilha.py` | Planilhas XLSX, XLS, XLSB e ODS (python-calamine, 13× mais rápido que o openpyxl, medido). Uma página por aba. | em funcionamento | leitores | leitores | 0 |
| 126 | `eldorado/motores/leitura/universal.py` | O leitor universal de reserva (Apache Tika, extra 'universal'): mais de mil formatos, quando nenhum outro lê. | desligado por desenho | leitores | leitores | 0 |

## 07 Missão: o perfil do que se procura

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 127 | `config/missao/dispensas_por_regime.json` | Nem todo recurso tem os 12 parâmetros de um edital. Esta matriz diz, para cada TIPO de recurso (regime), quais | aguarda a decisão da titular: fica até a decisão da titular: nenhum código a lê (criada na fase 4, 22/10/2026); as dispensas prováveis por regime de recurso: ligar ao checklist do Cartório ou retirar |  | mapa_arquivos | 0 |
| 128 | `config/missao/municipios_brasil.json` | Os 5.291 municípios do Brasil (IBGE), para localizar o órgão de cada oportunidade. | em funcionamento |  | auditoria, mapa_arquivos, regras_portao | 0 |
| 129 | `config/missao/republicadores.json` | Sites que REPUBLICAM oportunidades para divulgação: são INDÍCIO e insumo de busca do Piloto - Interceptador, n | em funcionamento |  | origem, organizar | 0 |
| 130 | `config/missao/territorio_goias.json` | O território de Goiás: os 246 municípios (IBGE, código UF 52), para a regra de abrangência. | em funcionamento |  | auditoria, mapa_arquivos, regras_portao | 0 |
| 131 | `eldorado/base/missao/__init__.py` |  | pacote |  |  | 10 |
| 132 | `eldorado/base/missao/chave.py` | A chave do livro nesta missão: o livro é o PROGRAMA, não a edição. | em funcionamento |  | indice, importar_eldorado0, oportunidades | 0 |
| 133 | `eldorado/base/missao/itens.py` | Os 12 itens do livro e o critério único da estrela (titular, 04/10/2026), aproveitado do Eldorado0. | em funcionamento |  | analise_externa, auditoria, cartorio, certificacao, selos, importar_eldorado0, oportunidades, cartorio, dados, pilotos,  | 0 |
| 134 | `eldorado/base/missao/regras_portao.py` | As regras do portão da missão das oportunidades — aproveitadas do Eldorado0, com fidelidade. | em funcionamento |  | auditoria, portao | 0 |
| 135 | `eldorado/base/missao/portao.py` | O portão da missão das oportunidades (titular, 16/10/2026), com as regras aproveitadas do Eldorado0. | em funcionamento | regras_portao | auditoria, oportunidades | 0 |
| 136 | `eldorado/base/missao/oportunidades.py` | A missão das oportunidades, no contrato da plataforma: itens, chave e portão. | em funcionamento | chave, itens, portao, contratos | passagem, nó «cartorio» (parâmetro); passagem, nó «decidir_rede» (parâmetro); passagem, nó «decidir» (parâmetro); passag | 9 |

## 08 Cartório · recepção e certificação

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 137 | `eldorado/base/cartorio/__init__.py` |  | pacote |  |  | 10 |
| 138 | `eldorado/base/cartorio/certificacao.py` | A certificação: cada item no texto oficial, com o valor, o trecho e a página. | em funcionamento | itens, eventos | auditoria, cartorio | 1 |
| 139 | `eldorado/base/cartorio/identidade.py` | A identidade das oportunidades (titular, 24/10/2026): a mesma oportunidade não pode ter mais de um livro. O qu | em funcionamento |  | passagem, nó 10 «unir_repetidos» | 0 |
| 140 | `eldorado/base/cartorio/origem.py` | A origem da oportunidade, decidida POR LIVRO, com evidência (titular, 23/10/2026). | em funcionamento |  | auditoria, cartorio, interceptador | 0 |
| 141 | `eldorado/base/cartorio/passaporte.py` | O passaporte: move o livro entre as fases só com a autorização da Regência, e registra as tentativas (até 3). | em funcionamento | regencia, eventos | analise_externa, auditoria, cartorio, encaminhamento | 1 |
| 142 | `eldorado/base/cartorio/releitura.py` | A releitura dos documentos herdados sem texto (24/10/2026): a migração do Eldorado0 registrou 4.873 documentos | em funcionamento | sala, api, escada, leve, leitores | passagem, nó 27 «reler_documentos» | 1 |
| 143 | `eldorado/base/cartorio/selos.py` | Os dois selos de cada livro, calculados a cada passagem. | em funcionamento | itens, eventos | auditoria, cartorio | 0 |
| 144 | `eldorado/base/cartorio/indice.py` | O índice: cria o livro ou vincula ao existente pela chave da missão; reconhece o mesmo edital em canais difere | em funcionamento | identidade, chave, contratos, eventos | cartorio | 2 |
| 145 | `eldorado/base/cartorio/cartorio.py` | O Cartório (titular, 22/10/2026): o ORGANIZADOR. Ele não busca nada: é onde o livro recebe informação nova, é | em funcionamento | auditoria, certificacao, indice, origem, passaporte, selos, itens, contratos, eventos, registro | passagem, nó 17 «validar»; passagem, nó 8 «cartorio» | 5 |

## 10 Pilotos: o Espião e o Interceptador (comandados pelo Comandante)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 146 | `eldorado/motores/pilotos/__init__.py` |  | pacote |  |  | 6 |
| 147 | `eldorado/motores/pilotos/espiao.py` | O PILOTO ESPIÃO (do Eldorado0, titular, 09 e 16/10/2026): caça só o que nenhum motor alcança. | em funcionamento | esquema, contratos | consolidar, pilotos | 1 |
| 148 | `eldorado/motores/pilotos/interceptador.py` | O PILOTO INTERCEPTADOR (do Eldorado0, titular, 26/09/2026): "o Espião descobre; o Interceptador comprova". | em funcionamento | origem, itens, contratos, eventos, ia, arquivo_web, escada, estrutura_site, fonte_oficial, leitores, pdf | encaminhamento, pilotos_permanentes | 4 |
| 149 | `eldorado/motores/pilotos/otimizacao.py` | A otimização das instruções dos pilotos (plano C: DSPy): a partir das certidões já validadas no banco (o item, | em funcionamento | ia | comandos, ia | 0 |

## 11 Verificação externa (o Claude no Chrome)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 150 | `eldorado/base/cartorio/analise_externa.py` | A etapa 5 do Cartório: a ANÁLISE EXTERNA pelo Claude no Chrome (titular, 22/10/2026). | em funcionamento | cartorio, passaporte, itens, eventos | passagem, nó 19 «analise_externa» | 1 |
| 151 | `eldorado/base/verificacao/importacao.py` | respostas importadas e recusadas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 152 | `eldorado/base/verificacao/lote.py` | lotes gerados | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |
| 153 | `eldorado/base/verificacao/relatorio_faltas.py` | livros com relatório final | substituído por eldorado/base/cartorio/analise_externa.py (o que falta vai no lote) |  |  | 0 |
| 154 | `eldorado/base/verificacao/verificacao.py` | livros em verificação; decisões recebidas | substituído por eldorado/base/cartorio/analise_externa.py |  |  | 0 |

## 12 Farol e transferência

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 155 | `eldorado/base/transferencia/__init__.py` |  | pacote |  |  | 1 |
| 156 | `eldorado/base/transferencia/farol.py` | A transferência ao Farol (etapa 08 do plano): o único ponto de comunicação com a segunda metade do sistema. | em funcionamento |  | passagem, nó 20 «farol» | 0 |

## 13 Aprendizado: pertinência, auditoria, completude, avaliação, curador, memória e skills

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 157 | `config/regras.toml` | A tabela única de regras e decisões da titular. Para cada tema, vale a decisão da titular mais recente. As sub | em funcionamento |  | regras | 0 |
| 158 | `config/regras_titular.json` | As regras da titular para o sistema. Cada regra tem as travas (testes) que a defendem: se alguém quebrar a reg | em funcionamento |  | regras, comandos | 0 |
| 159 | `eldorado/base/aprendizado/__init__.py` | O Aprendizado (titular, 25/10/2026): o responsável por toda análise e melhoria do sistema — a pertinência, a a | pacote |  |  | 3 |
| 160 | `eldorado/base/aprendizado/avaliar.py` | O Aprendizado avalia as decisões do Comandante (a etapa A4): quando o resultado aparece, cada decisão recebe a | em funcionamento | escolher | passagem, nó 32 «avaliar» | 1 |
| 161 | `eldorado/base/aprendizado/curador.py` | O curador do Aprendizado (a etapa A5; o conceito do curador do Hermes Agent, titular, 25/10/2026). | em funcionamento |  | passagem, nó 33 «curar» | 1 |
| 162 | `eldorado/base/aprendizado/memoria.py` | A memória do Aprendizado (a etapa A6): tudo o que o sistema viveu, pesquisável no Arquivo do Cérebro (titular, | em funcionamento |  | passagem, nó 35 «memorizar» | 2 |
| 163 | `eldorado/base/cartorio/auditoria.py` | A auditoria de cada livro: a validação individual e a decupagem dos dados em colunas (livro_dados). | em funcionamento | certificacao, origem, passaporte, selos, itens, portao, regras_portao, eventos, normalizar | passagem, nó 11 «auditar» | 4 |
| 164 | `eldorado/base/cerebro/aprendizado.py` | O ciclo de aprendizado: temporário (30 dias) → permanente, se funcionou; arquivado, se falhou; vencido, sai. | em funcionamento | eventos | passagem, nó 23 «aprender» | 2 |
| 165 | `eldorado/base/cerebro/completude.py` | A completude do dia: o que estava devido foi lido? O que precisa ser reacionado? | em funcionamento | eventos | passagem, nó 24 «completude» | 2 |
| 166 | `eldorado/base/cerebro/lote.py` | Os modelos em lote do Cérebro (plano C: scikit-learn): para cada pergunta da rede, um modelo treinado com o hi | em funcionamento |  | rede | 0 |
| 167 | `eldorado/base/cerebro/mapa_arquivos.py` | O mapa REAL dos arquivos do sistema (titular, 24/10/2026: nada decorativo nem exemplificativo). | em funcionamento | eventos | passagem, nó 28 «medir_arquivos» | 2 |
| 168 | `eldorado/base/cerebro/medicao.py` | O motor de indicadores: ponto, círculo e linhas de cada arquivo, e a agregação por componente, parte e sistema | em funcionamento | eventos | passagem, nó 25 «medir» | 2 |
| 169 | `eldorado/base/cerebro/pertinencia.py` | A Pertinência: decide se cada achado é oportunidade (pelo portão da missão) e mede a saída de cada etapa. | em funcionamento | contratos, eventos, registro | passagem, nó 15 «decidir_rede»; passagem, nó 6 «decidir» | 3 |
| 170 | `eldorado/base/cerebro/regras.py` | A tabela única de regras e decisões da titular (reativada em 25/10/2026: estava inativa, sem nó que a chamasse | em funcionamento | eventos | passagem, nó 1 «regras» | 2 |
| 171 | `eldorado/base/cerebro/revisao_alarmes.py` | O ciclo de vida dos alarmes (titular, 25/10/2026: a sala mostrava alarmes antigos, de causas já corrigidas, po | em funcionamento |  | passagem, nó 2 «revisar_alarmes» | 1 |
| 172 | `skills/aprendizado-avaliar-decisoes/SKILL.md` | A skill aprendizado-avaliar-decisoes: Avalia cada decisão do Comandante quando o resultado aparece (o motor tr | em funcionamento |  | curador | 0 |
| 173 | `skills/aprendizado-curador/SKILL.md` | A skill aprendizado-curador: Mantém as skills pelo uso e pelo resultado (ativa, parada, arquivada; nunca apaga | em funcionamento |  | curador | 0 |
| 174 | `skills/aprendizado-memoria/SKILL.md` | A skill aprendizado-memoria: Registra na memória pesquisável (FTS5) tudo o que é novo no Arquivo do Cérebro; o | em funcionamento |  | curador | 0 |
| 175 | `skills/aprendizado-pertinencia/SKILL.md` | A skill aprendizado-pertinencia: Decide se cada achado é uma oportunidade do perfil, pelas regras da missão e  | em funcionamento |  | curador | 0 |
| 176 | `skills/comandante-autorizar-espiao/SKILL.md` | A skill comandante-autorizar-espiao: Autoriza cada missão do Espião pelas quatro regras (3 segundos, a janela  | em funcionamento |  | curador | 0 |
| 177 | `skills/comandante-autorizar-interceptador/SKILL.md` | A skill comandante-autorizar-interceptador: Autoriza cada voo do Interceptador pelas quatro regras e registra  | em funcionamento |  | curador | 0 |
| 178 | `skills/comandante-conferir-20-minutos/SKILL.md` | A skill comandante-conferir-20-minutos: Confere, 20 minutos depois, cada mudança feita em funcionamento: se fo | em funcionamento |  | curador | 0 |
| 179 | `skills/comandante-decidir-coleta/SKILL.md` | A skill comandante-decidir-coleta: Decide quais motores reacionar, pela política aprendida no Arquivo do Céreb | em funcionamento |  | curador | 0 |
| 180 | `skills/comandante-parametrizar/SKILL.md` | A skill comandante-parametrizar: Ajusta os parâmetros de cada etapa no Arquivo do Cérebro, com a versão e a có | em funcionamento |  | curador | 0 |
| 181 | `skills/espiao-missao/SKILL.md` | A skill espiao-missao: Uma missão de busca de oportunidades novas na web, na família de consultas escolhida pe | em funcionamento |  | curador | 0 |
| 182 | `skills/interceptador-plano-de-voo/SKILL.md` | A skill interceptador-plano-de-voo: Um voo pelo plano de voo de um livro: as abordagens em ordem, até comprova | em funcionamento |  | curador | 0 |
| 183 | `eldorado/base/cerebro/inventario.py` | O inventário do sistema (titular, 22/10/2026): todo arquivo, do primeiro ao último no caminho do funcionamento | em funcionamento | mapa_arquivos | comandos | 1 |
| 184 | `eldorado/base/cerebro/rede.py` | A rede neural única, de aprendizado contínuo (River): aprende a cada veredito e dá as notas. | em funcionamento | lote, eventos, motor | passagem, nó 22 «rede» | 4 |

## 14 Análise e painel

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 185 | `eldorado/base/analise/__init__.py` |  | pacote |  |  | 1 |
| 186 | `eldorado/base/analise/calendario.py` | calendário atualizado na passagem | substituído por eldorado/base/analise/previsao.py (o calendário das abertas e das previstas) |  |  | 0 |
| 187 | `eldorado/base/analise/historia.py` | livros com história completa | substituído por eldorado/base/analise/previsao.py (a história do livro) |  |  | 0 |
| 188 | `eldorado/base/analise/preditivo.py` | alertas emitidos antes da abertura | substituído por eldorado/base/analise/previsao.py (a previsão da próxima abertura e o alerta) |  |  | 0 |
| 189 | `eldorado/base/analise/previsao.py` | A análise (fase F9 do plano): a previsão da próxima abertura, o calendário e a história de cada livro. | em funcionamento |  | passagem, nó 21 «analise» | 0 |
| 190 | `eldorado/base/painel/__init__.py` |  | pacote |  |  | 8 |
| 191 | `eldorado/base/painel/cartorio.py` | O Cartório no site, ligado aos dados (titular, 25/10/2026: a página estava estática). | em funcionamento | itens | dados | 1 |
| 192 | `eldorado/base/painel/legado.py` | Os arquivos do painel que o gerador nunca preenchia (titular, 25/10/2026: "pedi para consertar diversas vezes  | em funcionamento |  | dados | 1 |
| 193 | `eldorado/base/painel/maquina.py` | mostrador atualizado em tempo real | a construir |  |  | 0 |
| 194 | `eldorado/base/painel/pilotos.py` | Os pilotos no site, ligados aos dados (titular, 25/10/2026: sem leitura na página inicial e na sala de control | em funcionamento | itens | dados | 1 |
| 195 | `eldorado/base/painel/ranking.py` | O ranking de empresas (titular, 25/10/2026: a aba "Ranking de empresas" estava zerada: o arquivo ranking_apoia | em funcionamento |  | dados | 1 |
| 196 | `eldorado/base/painel/sala.py` | A sala de controle (o plano: base/painel/sala.py): cada mostrador ligado ao dado MEDIDO pelo sistema (titular, | em funcionamento | avaliar, mapa_arquivos | passagem, nó 3 «medir_sala» | 1 |
| 197 | `eldorado/base/painel/visoes.py` | As visões do painel: o que cada tela mostra, lido dos bancos (só leitura), num único arquivo de dados. | em funcionamento | itens, estado | comandos | 1 |
| 198 | `eldorado/base/painel/dados.py` | Os dados do painel, gerados do sistema novo (titular, 23/10/2026): o site é a imagem atual do sistema. | em funcionamento | mapa_arquivos, rede, itens, cartorio, legado, pilotos, ranking, sala, estado | comandos, api | 4 |
| 199 | `eldorado/base/painel/api.py` | A API do sistema (plano C: FastAPI, com respostas em orjson): a leitura do sistema para o painel novo e para q | em funcionamento | analise, manutencao, previsao, dados | comandos | 1 |

## 16 Migração do Eldorado0 (temporária)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 200 | `config/comparacao.toml` | Os 14 dias de comparação (critério da Fase 7 e da Fase 10): cada motor novo roda em paralelo com o de origem n | aguarda a decisão da titular: fica (titular, 25/10/2026): a comprovação de cobertura antes de eliminar o Eldorado0 ainda não foi feita |  | mapa_arquivos | 0 |
| 201 | `eldorado/base/migracao/__init__.py` |  | pacote |  |  | 1 |
| 202 | `eldorado/base/migracao/importar_eldorado0.py` | A migração do Eldorado0 (temporária, 30 dias): livros, certidões, documentos, vereditos, selos, leis, empresas | em funcionamento | chave, itens, eventos | comandos | 1 |

## 17 Estudos (sob demanda)

| Ordem | Arquivo | Finalidade | Situação | Depende de | Acionado por / usado por | Testes |
|---|---|---|---|---|---|---|
| 203 | `estudos/bench_ia.py` | O estudo das IAs (titular, 25/10/2026): uma Qwen3-8B para as três funções (o Interceptador, o Espião e o Coman | estudo concluído (25/10/2026): uma IA para as três funções; só sob demanda |  | bench-ia | 0 |
| 204 | `estudos/bench_ia2.py` | O estudo das IAs, parte 2 (titular, 25/10/2026): uma IA exclusiva do Comandante e uma dos pilotos (os dois pil | estudo concluído (25/10/2026): o arranjo das IAs e o contexto; só sob demanda |  | bench-ia2 | 0 |
| 205 | `.github/workflows/bench-ia.yml` | name: Estudo das IAs (uma ou três Qwen3-8B) O estudo da titular (25/10/2026): mede, na máquina da produção, as | estudo concluído (25/10/2026): uma IA para as três funções (o resultado no parecer); só sob demanda | ia_local, bench_ia |  | 0 |
| 206 | `.github/workflows/bench-ia2.yml` | name: Estudo das IAs (parte 2) O arranjo decidido pela titular (uma IA do Comandante e uma dos pilotos, em par | estudo concluído (25/10/2026): o arranjo das IAs e o contexto (o resultado no parecer); só sob demanda | ia_local, bench_ia2 |  | 0 |

## Os 47 motores (o estudo de reorganização da titular: 45 regulares e 2 pilotos)

| # | Categoria | Motor | Nome | Agrega | Alvos | Motor no sistema | Situação | Observação |
|---|---|---|---|---|---|---|---|---|
| 1 | EXE | do-goiania | Diário Oficial do Município de Goiânia | 0 | 2 | do-goiania | conforme | criado pela orientação: a lista oficial → o PDF → os atos; o Querido Diário pelo código do município como alternativa |
| 2 | EXE | do-goias | Diário Oficial do Estado de Goiás | 0 | 2 | do-goias | conforme | criado pela orientação: a cadeia edições → sumário → matéria; páginas gravadas em 23/10 |
| 3 | EXE | dou | Diário Oficial da União | 0 | 2 | dou | conforme |  |
| 4 | EXE | prefeituras-50-go | Prefeituras das 25 maiores cidades de Goiás — portais de editais | 1 | 4 | prefeituras-50-go | conforme | criado pela orientação: 55 rotas das 25 cidades (WordPress e páginas); 23 respondem da nuvem; Luziânia e Mineiros exigem o Brasil |
| 5 | EXE | estaduais-go-gov | Oportunidade Estaduais Governamentais de Goiás | 7 | 10 | estaduais-go-gov | conforme | Secult, SEDS, FAPEG, PNAB Goiás, FICA e o Goyazes; faltam OVG, SEMAD, Goiás Social, fundos estaduais e Anater (endereços a localizar; a API da Anater recusa) e 5 alvos |
| 6 | EXE | pncp-api | PNCP — API de contratações (chamamentos e credenciamentos) | 0 | 17 | pncp-api | conforme | faltam os 17 alvos |
| 7 | EXE | salic | Lei Rouanet — janela de propostas no SALIC e projetos de Goiás (Ministério da Cultura) | 2 | 1 | salic | conforme |  |
| 8 | EXE | motor-gife | Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás) | 1 | 0 | motor-gife | conforme | criado pela orientação, destino especial: os 500 maiores contribuintes do ICMS de Goiás e os 358 incentivadores PJ de Goiás no Salic; empresas e incentivos na base Especial |
| 9 | EXE | empresas-editais-incentivados | Busca de empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas, Pronon e Goyazes | 2 | 5 | empresas-editais-incentivados | conforme | criado pela orientação: os chamamentos do Pronas/PCD e do Pronon, a apresentação de projetos e o credenciamento; a Lei de Incentivo ao Esporte pelo Brasil; os 5 alvos |
| 10 | EXE | cnpq-extensao | CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC | 2 | 0 | cnpq-extensao | conforme | criado pela orientação: as chamadas abertas do CNPq, com o léxico de extensão e OSC; a Finep sem lista reconhecível (registrada) |
| 11 | EXE | site-funarte | Funarte — editais da Fundação Nacional de Artes | 0 | 0 | site-funarte | conforme | criado pela orientação: os editais abertos e os do ano corrente |
| 12 | EXE | site-transferegov | Transferegov — programas e parcerias com OSC abertos na plataforma federal (dados abertos) | 0 | 4 | site-transferegov | conforme | faltam os 4 alvos |
| 13 | EXE | novo-diarios-municipais-go | Diários oficiais municipais de Goiás (Querido Diário) | 0 | 1 | novo-diarios-municipais-go | conforme | refeito pela orientação: a edição diária da AGM (atos de dezenas de municípios, com o município de cada ato) e o Querido Diário de Aparecida; o QD só tem texto completo de Goiânia e Aparecida em Goiás |
| 14 | EXE | novo-bancos-publicos | Bancos públicos e Sistema S (BNDES, BNB, Caixa, Sebrae) | 1 | 5 | novo-bancos-publicos | conforme | criado pela orientação: os editais sociais do Banco do Nordeste, o BNDES Periferias, o Sebrae Goiás pelo Brasil; os 5 alvos |
| 15 | JUD | judiciario-tjgo | TJ-GO — editais das comarcas (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO | 2 | 1 | judiciario-tjgo | conforme | criado pelo diagnóstico: o Banco de Projetos Sociais da CGJ-GO (na nuvem) e o portal do TJ-GO pelo computador local (o zero do Eldorado0 era bloqueio); alvo corrigido |
| 16 | JUD | dj-trf1-go | Diário da Justiça Federal — Seção Judiciária de Goiás | 0 | 0 | dj-trf1-go | conforme | criado pelo diagnóstico: notícias e editais da SJGO; experimento real: 2 editais de cadastramento de entidades para projetos sociais (Goiás e Jataí) |
| 17 | JUD | judiciario-cnj | CNJ — destinação de prestações pecuniárias: busca no Portal do CNJ e regra nacional (Res. 558/2024) | 1 | 1 | judiciario-cnj | conforme | criado pelo diagnóstico: a busca do CNJ (divulga os editais das comarcas, como Itaberaí-GO) e a API do WordPress; alvo da Resolução 558 |
| 18 | JUD | mpgo-destinacao | MP-GO — Programa Destina (cadastro de entidades para receber bens e valores de acordos) | 0 | 1 | mpgo-destinacao | conforme | criado pela orientação: o portal pelo computador local (a nuvem recebe tempo esgotado); o Diário do Estado filtrado pelo MP, destinação e TAC; o alvo corrigido |
| 19 | JUD | mptgo-destinacao | MPT-GO — editais de 5 dias para indicação de destinação de recursos ou bens (PRT 18ª Região) | 0 | 0 | mptgo-destinacao | conforme | criado pela orientação: a tabela dos editais da PRT 18 por POST na sessão da página; experimento real em 23/10: 30 editais com documento e 6 do RSS do MPT |
| 20 | JUD | mpu-destinacao | MPU — MPF, MPDFT, MPM e MPT nacional: destinação de bens e valores (com CNMP e FDD) | 1 | 2 | mpu-destinacao | conforme | os editais de doação de bens do MPF em Goiás, as seleções do FDD e o alvo da Receita pela busca do site |
| 21 | LEG | camara-goiania-pl | Câmara Municipal de Goiânia — processos legislativos, utilidade pública e chamamentos | 0 | 4 | camara-goiania-pl | conforme | todo ato do terceiro setor: o Querido Diário recortado em atos com o léxico estrito; experimento: edital de chamamento, termo de fomento, utilidade pública, PL 288/2026 |
| 22 | LEG | alego-pl | Assembleia Legislativa de Goiás — proposições | 0 | 2 | alego-pl | conforme | todo ato do terceiro setor: o portal, o Diário do Estado filtrado e o sistema de consulta pelo computador local; experimento: destinação de emendas, Frente do Terceiro Setor |
| 23 | LEG | congresso-nacional | Congresso Nacional — Câmara, Senado e Comissão Mista de Orçamento (emendas, regras e chamamentos) | 0 | 1 | congresso-nacional | conforme | todo ato do terceiro setor: 11 rotas (CMO, orçamento, RSS e 8 de projetos de lei por termo nas duas casas); experimento: 17 projetos de lei, 4 alterando a Lei 13.019 |
| 24 | POR | gife | GIFE — Grupo de Institutos, Fundações e Empresas | 1 | 0 | gife | conforme |  |
| 25 | POR | plataforma-mapas-culturais | Adaptador Mapas Culturais — oportunidades com inscrição aberta | 0 | 0 | plataforma-mapas-culturais | conforme | a API do Mapa da Cultura e os editais do Ministério da Cultura; experimento: Cultura Viva, PNAB |
| 26 | POR | site-farol-cultural | Farol Cultural — editais de cultura de todo o Brasil, pela API pública do portal | 0 | 0 | site-farol-cultural | conforme | a API dos abertos com o link original; experimento: 15 (chamamentos e credenciamentos de cultura) |
| 27 | POR | site-capitaai | CapitaAI — editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas | 0 | 0 | site-capitaai | conforme | a captação e o mapa do site; experimento: 666 na primeira leitura (o histórico; o Cartório arquiva pelo prazo) |
| 28 | POR | site-observatorio-terceiro-setor | Observatório do Terceiro Setor — editais publicados na seção temática do portal | 1 | 0 | site-observatorio-terceiro-setor | conforme | RSS e página de editais; experimento: 19 (Pague Menos, Smart Fit, Brasilcap, Pretas Potências) |
| 29 | POR | site-mapas-culturais | Mapas Culturais — editais das redes estaduais e municipais de cultura que usam a plataforma | 0 | 0 | site-mapas-culturais | conforme | o Mapa Cultural do Ceará pela API; experimento: 43 chamamentos; o de Goiás a localizar |
| 30 | POR | site-abcr | ABCR — Associação Brasileira de Captadores de Recursos — editais divulgados pela associação dos captadores | 1 | 0 | site-abcr | conforme |  |
| 31 | POR | site-rede-comua | Rede Comuá — editais dos fundos independentes de filantropia | 0 | 0 | site-rede-comua | conforme | o tipo editais do WordPress; experimento: 45 (iCS-ANPEC, Agenda Rio 2030, editais climáticos) |
| 32 | POR | site-fundo-baoba | Fundo Baobá — editais para equidade racial | 0 | 0 | site-fundo-baoba | conforme | editais abertos e WordPress; experimento: 23 |
| 33 | POR | site-idis | IDIS — Instituto para o Desenvolvimento do Investimento Social — chamadas e editais de investimento social | 0 | 0 | site-idis | conforme | RSS e página inicial; experimento: 11 (o edital da Zurich via leis de incentivo, Territórios em Rede) |
| 34 | POR | site-fundo-casa | Fundo Casa Socioambiental — chamadas socioambientais | 0 | 0 | site-fundo-casa | conforme |  |
| 35 | POR | site-cese | CESE — Coordenadoria Ecumênica de Serviço — editais de apoio a projetos populares | 0 | 0 | site-cese | conforme |  |
| 36 | POR | site-rede-filantropia | Rede Filantropia — editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro) | 1 | 0 | site-rede-filantropia | incompleto | o domínio novo (filantropia.ong) responde, mas a página inicial vem com 8 links e nenhuma oportunidade; falta a página de editais |
| 37 | POR | site-editais-culturais | Editais Culturais — editais de cultura reunidos no portal | 0 | 0 | — | conforme |  |
| 38 | POR | site-mapa-osc | Mapa das OSC (Ipea) — editais reunidos no portal | 1 | 1 | site-mapa-osc | conforme | a lista de editais carrega por script (precisa do degrau de navegador); o robots proíbe robôs (informação) |
| 39 | POR | site-prosas | Prosas — editais e prêmios para OSCs (três caminhos indiretos: listagem da CapitaAI, ângulo do Piloto e coleta assistida) | 3 | 0 | site-prosas | conforme | os editais carregam por script: precisa do degrau de navegador (extra navegador) no funcionamento; a lista pública chega pelo CapitaAI e pelo Observatório |
| 40 | POR | site-fundo-brasil | Fundo Brasil de Direitos Humanos — editais de direitos humanos | 0 | 0 | site-fundo-brasil | conforme |  |
| 41 | POR | site-undef | UNDEF — Fundo das Nações Unidas para a Democracia — chamadas anuais para a sociedade civil | 0 | 0 | site-undef | conforme | a página e a chamada anual (Apply for Funding) |
| 42 | POR | site-brazilfoundation | BrazilFoundation — editais de apoio a organizações brasileiras | 0 | 0 | — | conforme |  |
| 43 | POR | outros-agregadores | Outros agregadores e motores de busca | 10 | 3 | outros-agregadores | conforme | criado pela orientação: a área de oportunidades do Editais do Brasil, a Jornada Social e a busca aberta (metabusca); experimento: 41 achados (Cultura Viva, Biblioteca Comunitária, MinC) |
| 44 | POR | novo-fundacoes-institutos | Fundações e institutos (sites próprios) | 2 | 24 | — | conforme |  |
| 45 | POR | novo-internacional | Organismos e fundações internacionais | 3 | 21 | — | conforme |  |
| 46 | IA | piloto-aberto | Piloto - Espião — busca aberta no terceiro setor | 1 | 0 | espiao | conforme | corrigido em 23/10/2026: o Espião nunca recebia missão (a ociosidade não chegava com 45 motores); agora há o mínimo garantido (uma missão a cada 6 h) |
| 47 | IA | piloto-interceptador | Piloto - Interceptador — comprova na fonte oficial | 0 | 0 | interceptador | conforme |  |
