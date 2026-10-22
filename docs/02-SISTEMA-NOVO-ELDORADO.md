# 02 — O sistema do novo Eldorado (a base, o workflow e cada arquivo)

**Versão final, revisada antes da criação (22/10/2026).** Este documento reúne a arquitetura, o workflow, as regras vigentes, a ordem de criação, as dependências com as versões fixadas e o esquema de cada arquivo da base. Os motores e o banco de dados estão nos documentos 01 e 03, e cumprem os contratos definidos aqui. Nada foi criado no repositório novo.

## Revisão final (antes da criação, 22/10/2026)

**Entra desde a Fase 5:**
1. **primp** no degrau 2 da escada de acesso (medido: 40% mais rápido que o curl_cffi, com outra assinatura de navegador).
2. **Protego** na escada de acesso: o robots como informação; a espera pedida pelo site alimenta o limite por domínio, sem bloquear.
3. **webtech** na leitura de páginas: detecta o sistema do site (WordPress e outros) para usar a API dele.
4. **Lightpanda 1.0.0** no degrau 3 (medido: 58 ms e 24 MB por página, contra 156 ms e 484 MB do Chromium), **com a espera configurada obrigatória** em cada motor.
5. **O recibo de cada chamada registra o processador e a memória de pico**, além do tempo: a Sala mostra quanto cada arquivo consome, e o governador adia os mais pesados.
6. **Números por extenso** por regra própria na normalização.
7. **O motor de indicadores** (`cerebro/medicao.py`) e o componente **Análise** (história do livro, previsão e calendário) na base.
8. **A análise da rede neural sobre cada livro**, guardada na Biblioteca (`analise_rede`).

**Sai desde a Fase 5:**
1. **Litestream** (as fotografias e os eventos cobrem a recuperação).
2. **A lógica que estava no banco** (história, previsão, calendário), que passou para a Análise.
3. **Os 103 projetos descartados** no estudo do GitHub, cada um com o motivo (arquivo C).

**Preservado:** as telas do Farol (Enquadramento, Documentos, fichas). **No Eldorado0:** o Interceptador foi corrigido e voltou a gerar aprendizado até a parada total, em 30 dias.

**Ordem de criação:** começa pela Fase 1 (Fundação): contratos, configuração, eventos, alarmes, os esquemas dos três bancos, o gravador e os testes.

## A. A arquitetura em três partes

| Parte | O que é | Natureza |
| --- | --- | --- |
| **Base** (o sistema) | O Cérebro (Regência e Pertinência e aprendizado), a organização, o acionamento, o Cartório, as etapas, a missão, a análise, o painel | **Fixa**: a estrutura que recebe as partes modulares |
| **Motores** | Os 45 motores de canal, os 2 pilotos e as ferramentas de acesso, leitura e descoberta | **Modular**: trocáveis e acrescentáveis sem mudar a base |
| **Banco de dados** | A Biblioteca, o Especial e o banco do Cérebro | **Modular**: guarda, impõe as regras, oferece as visões |

O **Farol de Alexandria** é a segunda metade do sistema, a ser desenvolvida; a única comunicação entre as duas metades é a **transferência de livros finalizados**. As telas do Farol são preservadas.

## B. A estrutura do repositório

```
eldorado/
  base/        nucleo · fluxo · cerebro · cartorio · investigacao · verificacao · transferencia · missao · analise · painel · migracao
  motores/     acesso · leitura · descoberta · canal (motor genérico + 45 configurações) · pilotos · skills
  banco/       biblioteca · especial · cerebro_db · originais · fotografia
  testes/
config/eldorado.toml
workflows/                 os workflows da plataforma (formato próprio, conceito do n8n)
.github/workflows/         passagem · pilotos · painel · qualidade
pyproject.toml             as dependências com as versões fixadas (seção E)
```

## C. O workflow, passo a passo

Cada etapa tem **entrada validada pela Regência** e **saída medida pela Pertinência e aprendizado**.

1. **A Regência aciona os motores.** A rede neural decide quais motores regulares rodam e quando o Espião voa, com quanto tempo, e quais alvos (oportunidades previstas) cada um vigia.
2. **Coleta (03).** Os motores e o Espião leem as suas fontes e extraem, para cada achado, os dados necessários, o link de divulgação, o link oficial e a prova.
3. **Pertinência na saída da Coleta.** A rede mede o que foi coletado: o achado é oportunidade do perfil (regras da missão)? Todos os dados do dia foram obtidos? O que não é oportunidade é registrado com o motivo e ensina o motor.
4. **Regência valida a entrada no Cartório.** Os achados aceitos passam ao Cartório.
5. **Certificação (04).** O Cartório separa cada achado para **criar um livro novo ou vincular a um livro existente**; classifica o livro (tema, quantidade de informações validadas, selo); certifica cada item no documento oficial; organiza os dados.
6. **Pertinência na saída do Cartório.** A rede mede o que foi certificado e o que falta.
7. **Regência direciona a Investigação.** Quando as informações trazidas pelos motores se esgotam, o Cartório certifica o que foi obtido e a Regência escolhe quais livros vão ao Interceptador, e em que ordem.
8. **Investigação (05).** O Interceptador pesquisa e valida as informações que faltam, um livro por voo.
9. **Pertinência na saída da Investigação.** A rede mede o que o Interceptador encontrou; o Cartório **agrega ao livro** e certifica.
10. **Regência transfere os incompletos.** Se o livro ainda não tem todas as informações, a Regência o transfere à Verificação externa, e o Cartório o separa no lote do Claude no Chrome.
11. **Verificação externa (06).** O Claude no Chrome faz a validação final: certifica o que encontrar, **justifica como dispensadas** as informações que não puderam ser levantadas, ou **exclui logicamente** o livro ou a oportunidade (com justificativa; nada é apagado).
12. **Pertinência na saída da Verificação externa.** Um **relatório do que faltou** e do que foi certificado é gravado no livro, e a rede aprende com ele.
13. **Transferência ao Farol (08).** O livro finalizado (validado ou com dispensas justificadas) é liberado pela Regência e transferido ao Farol.

**Em todas as passagens:** o livro recebe o relatório da etapa (o que gerou e o que aprendeu); nada é apagado nem sobrescrito; até 3 tentativas por ferramenta, com intervalo medido pela Regência.

## D. A ordem de criação

Cada fase só começa quando a anterior cumpre o critério de pronto, com os testes verdes e os indicadores ligados à Sala.

| Fase | O que é criado | Pronto quando |
| --- | --- | --- |
| **F1 · Fundação** | contratos; config; eventos; alarmes; esquemas dos três bancos; gravador; testes de contrato e dos bancos | o gravador aplica um lote de eventos aos três bancos, sem duplicar, e as regras barram o proibido |
| **F2 · Execução** | definição de workflow; executor durável; fila; agenda; governador; comandos | uma execução interrompida retoma do mesmo passo; o governador segura a carga abaixo de 85% |
| **F3 · Cérebro** | medição (indicadores); regras; Pertinência; Regência; aprendizado; rede; completude | uma passagem de teste é planejada, acionada, medida, e cada arquivo ganha ponto, círculo e linhas |
| **F4 · Cartório e missão** | missão; portão; itens; chave; índice; passaporte; certificação; selos; site oficial; Cartório | um achado aceito vira livro certificado, com selos, movido pela Regência; casos de ouro 100% |
| **F5 · Ferramentas dos motores** | escada de acesso (degraus 1, 2 e 4 primeiro); leitores (página, PDF, OCR, planilha, documento, expurgo, normalização); descoberta; motor genérico; achado; estado | as páginas gravadas dos 23 PDFs e do MPT-18 lidas com todas as palavras-chave; repetir o teste de velocidade com as versões fixadas |
| **F6 · Migração do Eldorado0** | importar livros, certidões, vereditos, empresas e aprendizado; remover CPF desnecessário; conferir contagens | as contagens importadas batem com a origem |
| **F7 · Primeiros motores** | os motores com API (DOU, PNCP, Querido Diário, Transferegov, SALIC, Mapas Culturais, WordPress de Goiás) | 14 dias em paralelo com os motores de origem, resultado igual ou melhor |
| **F8 · Etapas e pilotos** | Investigação e piloto B; Verificação externa; transferência ao Farol; piloto A | um livro percorre as quatro etapas até o Farol, com o relatório de cada uma |
| **F9 · Análise e painel** | história do livro; previsão; calendário; visões; API; páginas (reaproveitando o dashboard); mostrador da máquina; Sala | todas as telas leem as visões; o mostrador mostra a máquina em tempo real |
| **F10 · Demais motores e desligamento** | motores de diário e de páginas, por ordem de rendimento; diagnóstico dos motores sem resultado; desligamento gradual do Eldorado0 (30 dias) | cada motor substitui o de origem só depois de 14 dias iguais ou melhores |

## E. As dependências com as versões fixadas

Regra: **toda versão tem pelo menos 14 dias de publicada** (versões mais novas podem conter código malicioso ainda não detectado). Todas são compatíveis com o **Python 3.12**. O PyMuPDF e o DuckDB ficam nas versões 1.x (as 2.0 saíram há poucos dias); **o teste de velocidade do PDF deve ser repetido com a versão fixada** na Fase 5 da criação.

### E.1 Ferramentas da base e do banco

| Ferramenta (GitHub) | Pacote | Versão fixada | Publicada em | Licença | Usada em |
| --- | --- | --- | --- | --- | --- |
| [simonw/datasette](https://github.com/simonw/datasette) | `datasette` | **0.65.5** | 2026-09-17 | Apache License, Version 2.0 | `base/painel/visoes.py` |
| [ekzhu/datasketch](https://github.com/ekzhu/datasketch) | `datasketch` | **2.0.0** | 2026-07-05 | MIT | `base/cartorio/indice.py` |
| [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | `dspy` | **3.4.0** (a mais recente é 3.4.1) | 2026-09-25 | MIT License | `base/nucleo/ia.py`, `motores/pilotos/interceptador.py` |
| [duckdb/duckdb](https://github.com/duckdb/duckdb) | `duckdb` | **1.5.6** (a mais recente é 2.0.0) | 2026-09-28 | MIT License | `base/painel/visoes.py` |
| [fastapi/fastapi](https://github.com/fastapi/fastapi) | `fastapi` | **0.142.4** (a mais recente é 0.159.1) | 2026-10-07 | MIT | `base/painel/api.py` |
| [googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client) | `google-api-python-client` | **2.201.0** | 2026-09-30 | Apache 2.0 | `banco/originais/drive.py` |
| [adbar/htmldate](https://github.com/adbar/htmldate) | `htmldate` | **1.11.0** | 2026-10-02 | Apache-2.0 | `motores/descoberta/vigilancia.py` |
| [coleifer/huey](https://github.com/coleifer/huey) | `huey` | **3.4.0** | 2026-09-04 | — | `base/fluxo/fila.py` |
| [Delgan/loguru](https://github.com/Delgan/loguru) | `loguru` | **0.7.3** | 2024-12-06 | MIT License | `base/nucleo/alarmes.py` |
| [msgspec/msgspec](https://github.com/msgspec/msgspec) | `msgspec` | **0.22.0** | 2026-09-29 | BSD-3-Clause | `base/nucleo/eventos.py`, `base/transferencia/farol.py`, `base/painel/visoes.py` |
| [ijl/orjson](https://github.com/ijl/orjson) | `orjson` | **3.13.0** | 2026-10-07 | MPL-2.0 AND (Apache-2.0 OR MIT | `base/nucleo/eventos.py` |
| [giampaolo/psutil](https://github.com/giampaolo/psutil) | `psutil` | **7.2.2** | 2026-01-28 | BSD-3-Clause | `base/cerebro/governador.py`, `base/painel/maquina.py` |
| [pydantic/pydantic](https://github.com/pydantic/pydantic) | `pydantic` | **2.13.5** (a mais recente é 2.14.1) | 2026-08-28 | MIT | `base/nucleo/contratos.py`, `base/nucleo/config.py` |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | `pydantic-ai-slim` | **2.54.0** (a mais recente é 2.59.0) | 2026-10-03 | MIT | `base/nucleo/ia.py`, `motores/pilotos/espiao.py`, `motores/pilotos/interceptador.py` |
| [online-ml/river](https://github.com/online-ml/river) | `river` | **0.26.1** | 2026-08-21 | BSD-3-Clause | `base/cerebro/rede.py`, `motores/canal/motor.py`, `motores/pilotos/espiao.py` |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | `ruff` | **0.16.10** (a mais recente é 0.17.1) | 2026-10-01 | MIT | `.github/workflows/qualidade.yml` |
| [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | `scikit-learn` | **1.9.1** | 2026-09-10 | BSD-3-Clause | `base/cerebro/rede.py`, `base/analise/preditivo.py` |
| [simonw/sqlite-utils](https://github.com/simonw/sqlite-utils) | `sqlite-utils` | **4.2.1** | 2026-08-13 | Apache-2.0 | `base/nucleo/gravador.py`, `banco/biblioteca/esquema.py`, `banco/especial/esquema.py` |
| [fastapi/typer](https://github.com/fastapi/typer) | `typer` | **0.27.3** | 2026-10-06 | MIT | `base/nucleo/comandos.py` |
| [astral-sh/uv](https://github.com/astral-sh/uv) | `uv` | **0.12.23** (a mais recente é 0.13.5) | 2026-10-03 | MIT OR Apache-2.0 | `.github/workflows/qualidade.yml` |
| [kevin1024/vcrpy](https://github.com/kevin1024/vcrpy) | `vcrpy` | **8.3.0** | 2026-07-04 | MIT | `testes/` |
| [indygreg/python-zstandard](https://github.com/indygreg/python-zstandard) | `zstandard` | **0.25.0** | 2025-09-14 | BSD-3-Clause | `motores/canal/achado.py`, `banco/biblioteca/texto.py`, `banco/fotografia.py` |

### E.2 Ferramentas que não são pacotes Python

| Ferramenta | Forma de instalação ou uso | Usada em |
| --- | --- | --- |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | binário do servidor llama.cpp (release do GitHub), modelo Qwen3-8B em GGUF | `base/nucleo/ia.py` |
| [searxng/searxng](https://github.com/searxng/searxng) | serviço em contêiner Docker (imagem oficial searxng/searxng) | `motores/descoberta/metabusca.py` |
| [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) | pacote do sistema (apt: tesseract-ocr, tesseract-ocr-por) | `motores/leitura/ocr.py` |
| [tafia/calamine](https://github.com/tafia/calamine) | vem dentro do python-calamine (Rust) | `motores/leitura/planilha.py` |
| [apache/tika](https://github.com/apache/tika) | servidor Java baixado pelo pacote tika na primeira execução | `motores/leitura/universal.py` |
| [lightpanda-io/browser](https://github.com/lightpanda-io/browser) | binário do GitHub, versão 1.0.0 (medido: 58 ms e 24 MB por página) | `motores/acesso/navegador.py` |
| [rclone/rclone](https://github.com/rclone/rclone) | binário do GitHub (release oficial) | `banco/originais/drive.py` |
| [okfn-brasil/querido-diario](https://github.com/okfn-brasil/querido-diario) | API pública (sem instalação); o repositório é referência | `motores/descoberta/dados_abertos.py` |
| [MarginaliaSearch/MarginaliaSearch](https://github.com/MarginaliaSearch/MarginaliaSearch) | API pública gratuita (sem instalação) | `motores/descoberta/metabusca.py` |
| [jina-ai/reader](https://github.com/jina-ai/reader) | serviço público (sem instalação) | `motores/acesso/rotas_alternativas.py` |
| [anthropics/skills](https://github.com/anthropics/skills) | formato das skills (sem instalação) | `motores/skills/` |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | referência de desenho (sem instalação) | `base/nucleo/registro.py`, `base/cerebro/regencia.py`, `base/cerebro/aprendizado.py` |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | referência de desenho (sem instalação) | `base/fluxo/definicao.py`, `base/fluxo/executor.py` |
| [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet) | referência de desenho (sem instalação) | `base/fluxo/executor.py` |
| [dgtlmoon/changedetection.io](https://github.com/dgtlmoon/changedetection.io) | trecho copiado com licença registrada (sem instalação) | `motores/descoberta/vigilancia.py` |
| [nicolargo/glances](https://github.com/nicolargo/glances) | referência de interface (sem instalação) | `base/painel/maquina.py` |

### E.3 A lista para o arquivo de instalação (todas as partes)

```
aiolimiter==1.3.0
camoufox==0.5.8
cdx_toolkit==0.9.39
charset-normalizer==3.5.2
chompjs==1.4.1
ckanapi==4.11
curl_cffi==0.16.3
datasette==0.65.5
datasketch==2.0.0
datefinder==1.0.0
dateparser==1.4.3
ddgs==9.16.0
docx2python==3.7.1
dspy==3.4.0
duckdb==1.5.6
extruct==0.18.0
fastapi==0.142.4
faster-whisper==1.2.1
feedparser==6.0.14
google-api-python-client==2.201.0
htmldate==1.11.0
httpx==0.28.1
huey==3.4.0
jmespath==1.1.0
lightpanda (binário)==1.0.0
lingua-language-detector==2.2.0
liteparse==2.15.1
loguru==0.7.3
lxml==6.1.3
msgspec==0.22.0
odfpy==1.4.1
orjson==3.13.0
patchright==1.63.0
pdf-inspector==1.25.2
playwright==1.63.0
polars==2.0.0
price-parser==0.5.1
primp==2.0.1
protego==0.7.0
psutil==7.2.2
py7zr==1.1.3
pydantic==2.13.5
pydantic-ai-slim==2.54.0
pymupdf==1.28.2
pypdfium2==5.14.0
python-calamine==0.8.2
python-docx==1.2.0
python-pptx==1.0.2
rapidocr==3.9.2
rarfile==4.5
resiliparse==1.0.9
river==0.26.1
ruff==0.16.10
scikit-learn==1.9.1
scrapling==0.4.15
selectolax==1.0.0
sqlite-utils==4.2.1
stem==1.8.2
tenacity==9.2.1
tesserocr==2.11.0
tika==3.3.2
trafilatura==2.3.1
typer==0.27.3
ultimate-sitemap-parser==1.8.1
uv==0.12.23
validate-docbr==2.0.1
vcrpy==8.3.0
waybackpy==3.0.6
webtech==1.3.4
xmltodict==1.0.4
zstandard==0.25.0
```

## F. Conformidade com as regras da titular

| Regra definida pela titular | Onde é cumprida |
| --- | --- |
| Regência e Pertinência com vínculo direto com todo o sistema e todas as etapas | Seções 3, 4 e 5: entrada de toda etapa pela Regência, saída pela Pertinência |
| Uma rede neural que evolui a cada funcionamento | Seção 2 (princípio 2); cérebro com aprendizado temporário e permanente (8.2) |
| A modularidade é dos motores; cada etapa especializada | Seções 2 e 3 |
| Coleta = motores regulares (e o Espião) | Seções 3 e 9 |
| Certificação = Cartório, parte do sistema | Seções 3 e 5 |
| Investigação = piloto Interceptador | Seções 3, 4 (passos 7 a 9) e 9 |
| Verificação externa = Claude no Chrome, validação final ou descarte | Seção 4 (passos 10 a 12) |
| O Cartório como base de passagem entre as fases | Seção 5 |
| Cartório cria ou vincula livro; temas e informações validadas; classifica e organiza | Seção 4 (passo 5) e seção 6 |
| Investigação depois de esgotar os motores, direcionada pela Regência | Seção 4 (passo 7) |
| Dados do Interceptador agregados ao livro | Seção 4 (passo 9) |
| Livros incompletos transferidos pela Regência à Verificação externa | Seção 4 (passo 10) |
| Exclusão ou dispensa justificada na Verificação externa | Seção 4 (passo 11); exclusão lógica (princípio 5) |
| Relatório do que faltou ao final | Seção 4 (passo 12) |
| Nenhuma etapa exclui ou sobrescreve o livro | Princípio 5; regras do banco (8.1) |
| Relatório por etapa em cada livro | Seção 6 (item 5) |
| Relatório preditivo, com motores, datas e alerta | Seção 6 (item 6) |
| Calendário de abertas e previstas | Seção 6 |
| Banco relacional SQLite | Seção 8 |
| Motores com arquivos próprios; livros só na Biblioteca | Seções 8.1 e 8.3 |
| Motores independentes, acionados pela Regência, entregando à Pertinência | Seções 2 e 4 |
| Uma rede neural única para acionar e medir; todos os dados do dia | Seção 4 (passo 3) e o arquivo `completude_do_dia` |
| Motor extrai os dados necessários, o link de divulgação e o link oficial | Princípio 8 |
| Banco próprio da rede neural, sem oportunidades; temporários de 30 dias e permanentes | Seção 8.2 |
| Adicionar motor não muda a estrutura | Seção 9 |
| Prestação de contas: o motor funciona e o sistema valida e certifica | Seção 9 |
| O Farol como segunda metade, comunicação só na transferência | Seções 1 e 7 |

**Uma tensão resolvida:** “nenhuma etapa exclui o livro” e “a Verificação externa permite a exclusão” convivem pela **exclusão lógica**.

Acrescentam-se as diretrizes de 22/10: sem travas para robôs (o bloqueio só existe quando o próprio site bloqueia; aí a coleta vai ao computador da titular); nenhum PDF ou imagem no sistema (originais no Drive); texto literal completo com expurgo seguro; ferramentas leves para até 10 mil páginas; governador de carga de 85% e mostrador da máquina; uso aberto e não comercial; Eldorado0 desligado em 30 dias; CPF removido onde não for necessário; telas do Farol preservadas.

---


**Versão de 22/10/2026.** Estudo teórico, antes de qualquer criação ou teste. Nada foi criado no repositório novo. Este é o esquema da **base** (a parte fixa do sistema). Os **motores** e o **banco de dados** terão os seus próprios esquemas, conforme a modularidade; aqui ficam definidos os **contratos de integração** com eles, para que a integração seja plena.

## 1. Como ler

Cada arquivo tem um código permanente (`NE3-…`) e uma ficha com: finalidade; forma de construção; funções principais; o que recebe e entrega; as ligações nos dois sentidos; os eventos que emite e consome; as tabelas que lê (a escrita é sempre por eventos); as chaves de configuração; os alarmes; **o indicador na Sala com os limiares** (verde / amarelo / vermelho); o teste de aceite; o que existe hoje no Eldorado0 (com o estado medido); as ferramentas novas; os dados herdados; e **a finalidade da titular que ele atende**.

O indicador de cada arquivo segue o padrão já validado no Eldorado0: **ponto** (o arquivo funciona: rodou sem erro quando chamado), **círculo** (atinge a finalidade: a métrica da ficha) e **linhas** (as ligações declaradas, confirmadas pelas chamadas reais).

## 2. O que mudou nesta etapa

Duas correções na especificação da Etapa 4, encontradas ao detalhar a base:

1. **Lógica que estava no banco passou para a base.** A previsão, o calendário e a história do livro são cálculos; formam agora o componente **Análise** da base. O banco só guarda, impõe as regras e oferece as visões.
2. **O motor de indicadores** (`eldorado/base/cerebro/medicao.py`) passou a existir: ele calcula o ponto, o círculo e as linhas de cada arquivo e agrega pelos quatro níveis.

Uma dependência proibida apareceu com a correção e foi removida: a vigilância (um motor) consultava a previsão diretamente; agora recebe as janelas previstas no plano da Regência.

**A especificação tem 89 arquivos:** 51 na base (este esquema), 29 nos motores e 9 no banco.

## 3. A mecânica única

1. A **Regência planeja** e **aciona** pelo executor.
2. Cada módulo trabalha e **só grava eventos**.
3. O **gravador único** aplica os eventos aos bancos.
4. A **Pertinência mede** a saída de cada etapa; o **Cérebro aprende**; o retorno volta aos módulos.
5. As **visões** são geradas dos bancos, e o painel as mostra.
6. O **motor de indicadores** mede cada arquivo, e a Sala mostra do sistema até o arquivo.

## 4. As etapas e os arquivos de cada uma

### 01 Regência

Aciona a entrada de todas as etapas.

- `NE3-015` `eldorado/base/cerebro/regencia.py` (base) — A Regência: monta o plano de cada passagem, aciona os motores e os pilotos, valida a entrada de cada etapa e autoriza cada passagem de livro.
- `NE3-013` `eldorado/base/fluxo/agenda.py` (base) — A agenda de cada motor e alvo (horários, dias, janelas previstas), consultada pela Regência; uma passagem por janela.
- `NE3-021` `eldorado/base/cerebro/governador.py` (base) — O governador de carga: mede a máquina e mantém o uso abaixo de 85% (processador, memória, disco), reduzindo o paralelismo ou adiando tarefas.
- `NE3-019` `eldorado/base/cerebro/completude.py` (base) — Confere se todos os dados do dia foram obtidos: motores devidos que leram, alvos na janela, livros que avançaram.

### 02 Pertinência e aprendizado

Mede a saída de todas as etapas e aprende.

- `NE3-016` `eldorado/base/cerebro/pertinencia.py` (base) — A Pertinência e aprendizado: mede a saída de cada etapa; na saída dos motores, decide se o achado é oportunidade, pelas regras da missão.
- `NE3-017` `eldorado/base/cerebro/aprendizado.py` (base) — O ciclo de aprendizado: guarda como temporário (30 dias), promove a permanente o que provou funcionar, arquiva o que falhou e devolve o retorno a cada
- `NE3-014` `eldorado/base/cerebro/rede.py` (base) — A rede neural única: aprende a cada passagem (incremental) e dá as notas usadas pela Regência e pela Pertinência.
- `NE3-018` `eldorado/base/cerebro/regras.py` (base) — A tabela única de regras e decisões da titular, com data, alcance e precedência; a regra mais recente da titular prevalece.
- `NE3-020` `eldorado/base/cerebro/medicao.py` (base) — O motor de indicadores: calcula, a cada passagem, o ponto (funciona), o círculo (atinge a finalidade) e as linhas (ligações confirmadas) de cada arqui

### 03 Coleta

Parte modular: motores de canal e piloto A; a base só aciona e recebe.

- `NE3-065` `eldorado/motores/canal/motor.py` (motores) — O motor genérico de canal: lê a configuração, planeja, usa acesso, leitura e descoberta, entrega achados compactos, aprende e mantém o painel. Os 45 m
- `NE3-069` `eldorado/motores/pilotos/espiao.py` (motores) — Piloto A, o Espião: motor livre de descoberta, com IA; escolhe as famílias de busca pelo aprendizado (4 em 5) e explora (1 em 5).

### 04 Certificação (Cartório)

Base de passagem: cria ou vincula livro, certifica, classifica, move.

- `NE3-022` `eldorado/base/cartorio/cartorio.py` (base) — O Cartório, base de passagem: recebe os achados aceitos, separa para criar ou vincular livro, aciona a certificação e a classificação e move os livros
- `NE3-023` `eldorado/base/cartorio/passaporte.py` (base) — Move o livro entre as fases com a autorização da Regência; registra cada passagem e as até 3 tentativas por ferramenta.
- `NE3-024` `eldorado/base/cartorio/indice.py` (base) — Cria livro novo ou vincula a um existente pela chave da missão; reconhece o mesmo edital achado em canais diferentes; une duplicados sem apagar.
- `NE3-025` `eldorado/base/cartorio/certificacao.py` (base) — Certifica cada item no texto oficial, com trecho e página; agrega o que vem da Investigação e do Chrome; dispensa só com justificativa.
- `NE3-026` `eldorado/base/cartorio/selos.py` (base) — Calcula os dois selos de cada livro a cada passagem: a estrela (completude dos 12 itens) e o selo do livro (previsibilidade pelo histórico).
- `NE3-027` `eldorado/base/cartorio/site_oficial.py` (base) — Acha o link oficial (o órgão, não o republicador) e aplica a régua do vetor; o que veio de portal é pista.

### 05 Investigação

A base direciona; o piloto B (parte modular) busca.

- `NE3-028` `eldorado/base/investigacao/investigacao.py` (base) — A etapa de Investigação: recebe do Cartório os livros que esgotaram os motores, na ordem escolhida pela Regência, aciona o piloto B e devolve o result
- `NE3-070` `eldorado/motores/pilotos/interceptador.py` (motores) — Piloto B, o Interceptador: IA que pesquisa e comprova os itens que faltam, um livro por voo, gravando pelo contrato da Biblioteca.

### 06 Verificação externa

Decisão final pelo Claude no Chrome.

- `NE3-029` `eldorado/base/verificacao/verificacao.py` (base) — A etapa de Verificação externa: separa os livros transferidos pela Regência, gera o lote, recebe a decisão final (validação, dispensa justificada ou e
- `NE3-030` `eldorado/base/verificacao/lote.py` (base) — Monta o lote do Claude no Chrome por grupo, com o que falta em cada livro.
- `NE3-031` `eldorado/base/verificacao/importacao.py` (base) — Importa a resposta do Chrome como eventos; só documento oficial; aplica as decisões da titular.
- `NE3-032` `eldorado/base/verificacao/relatorio_faltas.py` (base) — Grava em cada livro o relatório do que faltou e do que foi certificado ao fim da Verificação externa.

### 07 Biblioteca

Parte modular do banco; a base lê pelas visões e escreve só por eventos.

- `NE3-072` `eldorado/banco/biblioteca/esquema.py` (banco) — O esquema relacional da Biblioteca, as regras do banco (nada se apaga nem se sobrescreve), a busca de texto (FTS5) e as versões do esquema.
- `NE3-073` `eldorado/banco/biblioteca/livro.py` (banco) — A interface do livro (contrato da Biblioteca): ler, acrescentar, registrar relatório; nunca apagar nem sobrescrever.

### 08 Transferência ao Farol

O único ponto de comunicação com a segunda metade.

- `NE3-033` `eldorado/base/transferencia/farol.py` (base) — O único ponto de comunicação com o Farol: entrega os livros finalizados num formato de exportação estável e registra a transferência.

### Transversal: núcleo, fluxo, análise, missão, painel, qualidade

O que sustenta todas as etapas.

- `NE3-001` `eldorado/base/nucleo/contratos.py` (base) — Os contratos de todo módulo: Motor, Piloto, Ferramenta (acesso, leitura, descoberta), Skill, Etapa, Missão e Banco. A base só conversa por eles.
- `NE3-002` `eldorado/base/nucleo/registro.py` (base) — Registra motores, pilotos, ferramentas, skills e a missão ativa a partir dos seus manifestos; recarrega sem parar o sistema (mecanismo do Hermes).
- `NE3-003` `eldorado/base/nucleo/config.py` (base) — Carrega e valida `config/eldorado.toml` (missão ativa, limites, horários, provedores de IA, armazenamento) com valores padrão seguros.
- `NE3-004` `eldorado/base/nucleo/eventos.py` (base) — O formato único do evento e a gravação em arquivos que só se acrescentam (um por execução); cada evento carrega a linhagem (livro e achado de origem).
- `NE3-005` `eldorado/base/nucleo/gravador.py` (base) — O gravador único: aplica os eventos aos três bancos (Biblioteca, Especial, Cérebro) em ordem, sem duplicar; publica as fotografias e as visões.
- `NE3-006` `eldorado/base/nucleo/alarmes.py` (base) — Nenhum erro é engolido: todo erro vira evento de alarme com gravidade, módulo, mensagem e rastro, e aparece na sala.
- `NE3-007` `eldorado/base/nucleo/ia.py` (base) — O serviço de IA compartilhado: provedores trocáveis (IA externa e modelo local), fila de pedidos, limite por motor e por passagem, resposta sempre no 
- `NE3-008` `eldorado/base/nucleo/comandos.py` (base) — Os comandos da plataforma: rodar uma passagem, um motor, um piloto, a bateria, a importação, a fotografia; pausar e retomar; tudo também acionável pel
- `NE3-009` `eldorado/base/nucleo/seguranca.py` (base) — Senha do painel e bloqueio de publicação de credenciais e de dados pessoais (CPF removido onde não for necessário).
- `NE3-010` `eldorado/base/fluxo/definicao.py` (base) — O formato do workflow (conceito do n8n): nós, conexões, saída de erro, retentativas por nó, dados fixos de teste, versão.
- `NE3-011` `eldorado/base/fluxo/executor.py` (base) — O executor durável: percorre os nós, aplica retentativas, segue pela saída de erro, grava o estado a cada passo e retoma de onde parou depois de uma q
- `NE3-012` `eldorado/base/fluxo/fila.py` (base) — A fila de tarefas e o agendamento em SQLite: tarefas imediatas, periódicas e reagendadas (as esperas de 6 h e 24 h das tentativas).
- `NE3-013` `eldorado/base/fluxo/agenda.py` (base) — A agenda de cada motor e alvo (horários, dias, janelas previstas), consultada pela Regência; uma passagem por janela.
- `NE3-034` `eldorado/base/missao/oportunidades.toml` (base) — A declaração da missão ativa: o que é um livro, as etapas, o destino; trocar a finalidade é trocar este arquivo e os três seguintes.
- `NE3-035` `eldorado/base/missao/portao.py` (base) — As regras do portão desta missão (terceiro setor, território, Goiás restrito, emendas, extratos), lidas da tabela de regras.
- `NE3-036` `eldorado/base/missao/itens.py` (base) — Os 12 itens do livro, como cada um se prova e as dispensas por tipo de recurso.
- `NE3-037` `eldorado/base/missao/chave.py` (base) — A chave do livro nesta missão (programa, órgão, local, objeto).
- `NE3-038` `eldorado/base/painel/api.py` (base) — A API local de controle e de dados: o painel consulta as visões; a titular aciona, pausa e decide.
- `NE3-039` `eldorado/base/painel/visoes.py` (base) — Gera, a cada passagem, as visões que alimentam as telas: toda tela de oportunidade lê a Biblioteca; toda tela de operação lê o Cérebro.
- `NE3-040` `eldorado/base/painel/maquina.py` (base) — O mostrador da máquina na tela inicial: configuração, uso em tempo real (processador, memória, disco, rede), tamanho de cada parte e o limite de 85%.
- `NE3-041` `eldorado/base/painel/sala.py` (base) — A Sala de controle: cada arquivo do sistema como estrela (ponto, círculo, linhas), os indicadores por nível, os alarmes e o Cérebro.
- `NE3-042` `eldorado/base/painel/paginas/` (base) — As páginas do painel, reaproveitadas do dashboard validado: início (com o mostrador da máquina), calendário, oportunidades abertas, Bússola (47 motore
- `NE3-075` `eldorado/base/analise/historia.py` (base) — A história inteira de cada livro: motores e datas, informações obtidas, links, tentativas, passagens, relatórios por etapa, análises internas e extern
- `NE3-076` `eldorado/base/analise/preditivo.py` (base) — A análise preditiva de cada livro e o alerta antes de abrir.
- `NE3-077` `eldorado/base/analise/calendario.py` (base) — O calendário de oportunidades abertas e previstas.
- `NE3-084` `eldorado/base/migracao/importar_eldorado0.py` (base) — Importa do Eldorado0 os livros, as certidões, os vereditos, as empresas e o aprendizado, com CPF removido onde não for necessário; temporário, desliga
- `NE3-085` `eldorado/testes/` (base) — Testes de contrato, casos de ouro das regras, testes dos motores com páginas gravadas, teste do expurgo e testes dos bancos; rodam numa cópia isolada.
- `NE3-086` `.github/workflows/passagem.yml` (base) — A passagem: aciona a Regência; grava eventos; o gravador aplica; publica.
- `NE3-087` `.github/workflows/pilotos.yml` (base) — Os voos dos dois pilotos, acionados pela Regência.
- `NE3-088` `.github/workflows/painel.yml` (base) — Publicação do painel, das visões e da sala.
- `NE3-089` `.github/workflows/qualidade.yml` (base) — A bateria de testes a cada mudança e o teste de contrato.

## 5. Os tipos de ação

| Ação | O que é | Arquivos responsáveis | Eventos |
| --- | --- | --- | --- |
| **PLANEJAR** | decidir o que roda na passagem, com quanto tempo e em que ordem | `base/cerebro/regencia.py`, `base/fluxo/agenda.py`, `base/cerebro/governador.py` | `plano.criado` |
| **ACIONAR** | disparar motores, pilotos e etapas pelo executor | `base/cerebro/regencia.py`, `base/fluxo/executor.py`, `base/fluxo/fila.py` | `acionamento.feito`, `execucao.passo` |
| **COLETAR** | ler fontes e entregar achados (parte modular) | `motores/canal/motor.py`, `motores/pilotos/espiao.py` | `motor.execucao`, `achado.entregue` |
| **MEDIR** | medir a saída de cada etapa e de cada arquivo | `base/cerebro/pertinencia.py`, `base/cerebro/medicao.py`, `base/cerebro/completude.py` | `medicao.registrada` |
| **DECIDIR** | aplicar o portão da missão a cada achado | `base/cerebro/pertinencia.py`, `base/missao/portao.py`, `base/cerebro/regras.py` | `pertinencia.decidida` |
| **GRAVAR** | aplicar eventos aos bancos (só o gravador) | `base/nucleo/gravador.py` | `(todos)` |
| **CRIAR OU VINCULAR LIVRO** | livro novo ou vínculo, com a chave da missão | `base/cartorio/indice.py`, `base/missao/chave.py` | `livro.criado`, `livro.vinculado`, `livro.unido` |
| **MOVER** | passar o livro de fase, com autorização | `base/cartorio/passaporte.py`, `base/cartorio/cartorio.py` | `livro.passagem`, `tentativa.registrada` |
| **CERTIFICAR** | provar cada item no texto oficial | `base/cartorio/certificacao.py`, `base/cartorio/site_oficial.py`, `base/missao/itens.py` | `certidao.gravada` |
| **CLASSIFICAR** | calcular a estrela e o selo do livro | `base/cartorio/selos.py` | `selo.calculado` |
| **INVESTIGAR** | acionar o piloto B nos livros que esgotaram os motores | `base/investigacao/investigacao.py` | `acionamento.feito`, `relatorio.etapa` |
| **VERIFICAR** | decisão final pelo Claude no Chrome | `base/verificacao/verificacao.py`, `base/verificacao/lote.py`, `base/verificacao/importacao.py` | `veredito.gravado`, `livro.excluido_logicamente` |
| **RELATAR** | registrar no livro o que cada etapa gerou e aprendeu | `base/analise/historia.py`, `base/verificacao/relatorio_faltas.py` | `relatorio.etapa` |
| **PREVER** | prever a próxima edição e alertar antes de abrir | `base/analise/preditivo.py`, `base/analise/calendario.py` | `previsao.calculada`, `alerta.preditivo` |
| **TRANSFERIR** | entregar o livro finalizado ao Farol | `base/transferencia/farol.py` | `transferencia.feita` |
| **APRENDER** | consolidar, promover e arquivar o aprendizado | `base/cerebro/aprendizado.py`, `base/cerebro/rede.py` | `aprendizado.registrado`, `aprendizado.promovido`, `modelo.treinado` |
| **PUBLICAR** | gerar as visões e as telas | `base/painel/visoes.py`, `base/painel/sala.py`, `base/painel/paginas/` | `(lê os bancos)` |
| **GOVERNAR** | manter a máquina abaixo de 85% | `base/cerebro/governador.py`, `base/painel/maquina.py` | `maquina.leitura` |
| **ALARMAR** | nenhum erro engolido | `base/nucleo/alarmes.py` | `alarme.aberto`, `alarme.fechado` |
| **TESTAR** | provar antes de ligar | `testes/`, `.github/workflows/qualidade.yml` | `(resultado da bateria)` |
| **MIGRAR** | trazer o Eldorado0 (30 dias) | `base/migracao/importar_eldorado0.py` | `importacao.lote` |

## 6. Os eventos (a única forma de escrita)

| Evento | Quem emite | Quem consome | Efeito no banco |
| --- | --- | --- | --- |
| `plano.criado` | cerebro/regencia | fluxo/executor, painel | cerebro.plano |
| `acionamento.feito` | cerebro/regencia | fluxo/fila, cerebro/medicao | cerebro.acionamento |
| `execucao.passo` | fluxo/executor | cerebro/medicao | cerebro.execucao_passo |
| `chamada.recibo` | fluxo/executor (envolve toda chamada de módulo) | cerebro/medicao | cerebro.recibo |
| `motor.execucao` | motores (contrato Motor) | cerebro/pertinencia, cerebro/medicao | cerebro.execucao_motor |
| `achado.entregue` | motores e piloto A | cerebro/pertinencia | biblioteca.achado (pendente) |
| `pertinencia.decidida` | cerebro/pertinencia | cartorio/cartorio, cerebro/aprendizado | cerebro.decisao_pertinencia; biblioteca.achado (decisão) |
| `livro.criado` | cartorio/indice | cartorio/cartorio | biblioteca.livro |
| `livro.vinculado` | cartorio/indice | cartorio/cartorio | biblioteca.achado (livro) |
| `livro.unido` | cartorio/indice | analise/historia | biblioteca.uniao |
| `livro.passagem` | cartorio/passaporte (com autorização da Regência) | cerebro/medicao, analise/historia | biblioteca.passagem, biblioteca.passaporte |
| `tentativa.registrada` | cartorio/passaporte | cerebro/regencia | biblioteca.tentativa |
| `certidao.gravada` | cartorio/certificacao, verificacao/importacao | cartorio/selos | biblioteca.certidao |
| `selo.calculado` | cartorio/selos | painel/visoes | biblioteca.livro (estrela, selo do livro) |
| `relatorio.etapa` | toda etapa | analise/historia | biblioteca.relatorio_etapa |
| `veredito.gravado` | verificacao/importacao | cerebro/rede, cerebro/aprendizado | biblioteca.veredito; cerebro.rotulo |
| `livro.excluido_logicamente` | verificacao/verificacao | analise/historia, cerebro/aprendizado | biblioteca.livro (situação e justificativa) |
| `previsao.calculada` | analise/preditivo | fluxo/agenda, analise/calendario | biblioteca.previsao |
| `alerta.preditivo` | analise/preditivo | painel/visoes, cerebro/regencia | biblioteca.previsao (alerta) |
| `transferencia.feita` | transferencia/farol | analise/historia | biblioteca.transferencia |
| `aprendizado.registrado` | cerebro/aprendizado | nucleo/registro, módulos | cerebro.aprendizado_temporario |
| `aprendizado.promovido` | cerebro/aprendizado | nucleo/registro | cerebro.aprendizado_permanente |
| `aprendizado.arquivado` | cerebro/aprendizado | nucleo/registro | cerebro.aprendizado_permanente (arquivado) |
| `modelo.treinado` | cerebro/rede | cerebro/regencia, cerebro/pertinencia | cerebro.modelo |
| `regra.registrada` | cerebro/regras | cerebro/pertinencia, missao/portao | cerebro.regra |
| `medicao.registrada` | cerebro/medicao | painel/sala | cerebro.medicao |
| `maquina.leitura` | cerebro/governador | painel/maquina | cerebro.maquina |
| `alarme.aberto` | nucleo/alarmes | painel/sala | cerebro.alarme |
| `alarme.fechado` | nucleo/alarmes | painel/sala | cerebro.alarme |
| `modulo.registrado` | nucleo/registro | cerebro/medicao | cerebro.modulo |
| `workflow.versao` | fluxo/definicao | fluxo/executor | cerebro.workflow |
| `importacao.lote` | migracao/importar_eldorado0 | nucleo/gravador | todas (temporário) |

## 7. Os arquivos da base, um por um


### Núcleo da plataforma

#### `NE3-001` · `eldorado/base/nucleo/contratos.py`

**Finalidade:** Os contratos de todo módulo: Motor, Piloto, Ferramenta (acesso, leitura, descoberta), Skill, Etapa, Missão e Banco. A base só conversa por eles.

**Atende à finalidade da titular:** modularidade: trocar um motor, o banco ou a missão sem mudar a base.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | Motor: descrever, planejar, buscar, aprender, painel, saude; Piloto: os mesmos, mais o provedor de IA; Ferramenta: tipo (acesso, leitura, descoberta), resolve, aplicar; Skill: manifesto (nome, origem, uso, resultado, estado); Etapa: entrada, executar, saída; Banco: Livro, Especial e Cérebro (leitura e acréscimo; escrita só por eventos); Missão: livro, itens, portão, chave, validação, destino |
| Recebe | — |
| Entrega | as interfaces (classes abstratas tipadas) |
| Usa | — |
| É usado por | `NE3-002` eldorado/base/nucleo/registro.py, `NE3-004` eldorado/base/nucleo/eventos.py, `NE3-010` eldorado/base/fluxo/definicao.py, `NE3-065` eldorado/motores/canal/motor.py, `NE3-085` eldorado/testes/ |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | módulo que não cumpre o contrato |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | todo módulo registrado passa no teste de contrato — limiares: 100% dos módulos passam / qualquer recusa é investigada / módulo ligado sem passar |
| Indicador · linhas | 5 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | teste de contrato roda todos os módulos registrados |
| Existe hoje no Eldorado0 | manual de criação do motor, do piloto e da ferramenta (APRENDIZADO-ELDORADO.json) · itens atuais herdados: 3 (⚪ 2 · 🟢 1) |
| Ferramentas novas | pydantic/pydantic |
| Dados herdados | — |
| Cuidados | nenhum módulo importa outro módulo diretamente; só contratos |

#### `NE3-002` · `eldorado/base/nucleo/registro.py`

**Finalidade:** Registra motores, pilotos, ferramentas, skills e a missão ativa a partir dos seus manifestos; recarrega sem parar o sistema (mecanismo do Hermes).

**Atende à finalidade da titular:** adicionar um motor não muda a estrutura.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | descobrir manifestos; validar contra o contrato; ligar e desligar; recarregar sem parar (delta); arquivar e restaurar |
| Recebe | manifestos e configurações |
| Entrega | o catálogo de módulos ligados |
| Usa | `NE3-001` eldorado/base/nucleo/contratos.py, `NE3-003` eldorado/base/nucleo/config.py |
| É usado por | `NE3-017` eldorado/base/cerebro/aprendizado.py, `NE3-020` eldorado/base/cerebro/medicao.py |
| Eventos que emite | `modulo.registrado` |
| Eventos que consome | `aprendizado.promovido`, `aprendizado.arquivado` |
| Tabelas que lê | cerebro.modulo |
| Dados | cerebro.db: modulo |
| Configuração | caminhos dos módulos |
| Alarmes | manifesto inválido, módulo sumiu |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | módulos ligados × módulos com contrato válido; módulo recusado gera alarme — limiares: todos válidos / 1 recusado / módulo ativo recusado |
| Indicador · linhas | 4 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | registrar, recarregar e arquivar um motor de teste sem parar a passagem |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 3 (🟢 2 · ⚪ 1) |
| Ferramentas novas | NousResearch/hermes-agent (desenho: skills_index_delta, learning_mutations) |
| Dados herdados | — |
| Cuidados | excluir é arquivar (restaurável) |

#### `NE3-003` · `eldorado/base/nucleo/config.py`

**Finalidade:** Carrega e valida `config/eldorado.toml` (missão ativa, limites, horários, provedores de IA, armazenamento) com valores padrão seguros.

**Atende à finalidade da titular:** nenhum endereço fixo no código.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | carregar; validar com valores padrão; expor por seção |
| Recebe | config/eldorado.toml |
| Entrega | configuração validada |
| Usa | — |
| É usado por | `NE3-002` eldorado/base/nucleo/registro.py, `NE3-007` eldorado/base/nucleo/ia.py, `NE3-008` eldorado/base/nucleo/comandos.py |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | config/eldorado.toml |
| Dados | — |
| Configuração | missao_ativa, limites, horarios, ia, armazenamento, drive |
| Alarmes | configuração inválida impede a passagem |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | configuração válida na carga — limiares: válida / chave obsoleta / inválida |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | configuração inválida para a passagem com alarme |
| Existe hoje no Eldorado0 | config/horarios.json; config/relatorios.json; config/ia.json; config/ia_local.json · itens atuais herdados: 17 (🟢 16 · ⚪ 1) |
| Ferramentas novas | pydantic/pydantic |
| Dados herdados | horários e cadências validados no Eldorado0 |
| Cuidados | nenhum endereço fixo no código (lição da troca de nome) |

#### `NE3-004` · `eldorado/base/nucleo/eventos.py`

**Finalidade:** O formato único do evento e a gravação em arquivos que só se acrescentam (um por execução); cada evento carrega a linhagem (livro e achado de origem).

**Atende à finalidade da titular:** escrita única; o histórico do livro pela linhagem.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | criar evento (tipo, módulo, linhagem, dados); gravar no arquivo da execução; validar o formato |
| Recebe | eventos de todos os módulos |
| Entrega | eventos/AAAA/MM/DD/<execução>.jsonl |
| Usa | `NE3-001` eldorado/base/nucleo/contratos.py |
| É usado por | `NE3-005` eldorado/base/nucleo/gravador.py, `NE3-006` eldorado/base/nucleo/alarmes.py, `NE3-011` eldorado/base/fluxo/executor.py, `NE3-020` eldorado/base/cerebro/medicao.py, `NE3-031` eldorado/base/verificacao/importacao.py, `NE3-066` eldorado/motores/canal/achado.py, `NE3-084` eldorado/base/migracao/importar_eldorado0.py |
| Eventos que emite | `(todos, em nome dos módulos)` |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | pasta de eventos |
| Alarmes | evento inválido |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | eventos gravados por execução; eventos inválidos (devem ser zero) — limiares: 0 inválidos / até 0,1% / acima |
| Indicador · linhas | 8 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | 10 mil eventos gravados e lidos sem perda |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 1 (⚪ 1) |
| Ferramentas novas | msgspec/msgspec, ijl/orjson |
| Dados herdados | — |
| Cuidados | msgspec (1.482 MB/s medido) |

#### `NE3-005` · `eldorado/base/nucleo/gravador.py`

**Finalidade:** O gravador único: aplica os eventos aos três bancos (Biblioteca, Especial, Cérebro) em ordem, sem duplicar; publica as fotografias e as visões.

**Atende à finalidade da titular:** nada se apaga nem se sobrescreve; um banco relacional.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | ler eventos pendentes em ordem; aplicar por tipo (catálogo de eventos); marcar aplicado (idempotente); gerar fotografia; acionar as visões |
| Recebe | eventos |
| Entrega | bancos atualizados, fotografias, visões |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py, `NE3-072` eldorado/banco/biblioteca/esquema.py, `NE3-079` eldorado/banco/especial/esquema.py, `NE3-081` eldorado/banco/cerebro_db/esquema.py, `NE3-039` eldorado/base/painel/visoes.py |
| É usado por | `NE3-086` .github/workflows/passagem.yml |
| Eventos que emite | `alarme.aberto` |
| Eventos que consome | `(todos)` |
| Tabelas que lê | três bancos |
| Dados | todas |
| Configuração | ordem de aplicação, lote |
| Alarmes | violação de regra do banco, atraso acima de uma passagem |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | atraso entre evento e banco; violações barradas pelas regras do banco — limiares: atraso < 1 passagem / 1 a 2 / > 2 |
| Indicador · linhas | 6 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | aplicar duas vezes o mesmo lote não duplica nada |
| Existe hoje no Eldorado0 | scripts/gravar_somente_alterados.py (só a lição: gravar só o que mudou) · itens atuais herdados: 2 (⚪ 1 · 🟢 1) |
| Ferramentas novas | simonw/sqlite-utils |
| Dados herdados | — |
| Cuidados | é o único que escreve nos bancos |

#### `NE3-006` · `eldorado/base/nucleo/alarmes.py`

**Finalidade:** Nenhum erro é engolido: todo erro vira evento de alarme com gravidade, módulo, mensagem e rastro, e aparece na sala.

**Atende à finalidade da titular:** lições do painel congelado e do Interceptador parado.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | abrir alarme com gravidade; agrupar repetições; fechar ao resolver; notificar a sala |
| Recebe | exceções de qualquer módulo |
| Entrega | eventos de alarme |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py |
| É usado por | — |
| Eventos que emite | `alarme.aberto`, `alarme.fechado` |
| Eventos que consome | — |
| Tabelas que lê | cerebro.alarme |
| Dados | cerebro.db: alarme |
| Configuração | gravidades, prazo por gravidade |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | alarmes abertos por gravidade; tempo até o alarme ser visto — limiares: nenhum crítico aberto / crítico aberto < 1 dia / > 1 dia |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um erro provocado aparece na sala em até uma passagem |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | Delgan/loguru |
| Dados herdados | lição do painel congelado por 4 horas (27/09) e do Interceptador parado 5 dias (17/10) |
| Cuidados | erro silencioso é falha de projeto |

#### `NE3-007` · `eldorado/base/nucleo/ia.py`

**Finalidade:** O serviço de IA compartilhado: provedores trocáveis (IA externa e modelo local), fila de pedidos, limite por motor e por passagem, resposta sempre no formato declarado.

**Atende à finalidade da titular:** pilotos com IA trocável; IA leve e sem custo.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | receber pedido com o formato esperado; escolher o provedor (custo e acerto); respeitar a fila e o limite por motor; validar a resposta; otimizar instruções com o gabarito (DSPy) |
| Recebe | pedidos de IA de pilotos, Pertinência e copiloto dos motores |
| Entrega | respostas validadas |
| Usa | `NE3-003` eldorado/base/nucleo/config.py, `NE3-021` eldorado/base/cerebro/governador.py |
| É usado por | `NE3-069` eldorado/motores/pilotos/espiao.py, `NE3-070` eldorado/motores/pilotos/interceptador.py |
| Eventos que emite | `medicao.registrada` |
| Eventos que consome | — |
| Tabelas que lê | cerebro.medicao |
| Dados | cerebro.db: medicao |
| Configuração | provedores, limites, modelo local |
| Alarmes | respostas inválidas acima do limite, provedor fora |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | respostas válidas (meta 90%); custo e tempo por tarefa — limiares: ≥ 90% válidas / 75 a 90% / < 75% |
| Indicador · linhas | 4 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | mesmo pedido com dois provedores dá respostas no mesmo formato |
| Existe hoje no Eldorado0 | src/ia.py; src/ia_local.py (servidor local, espelhos do modelo) · itens atuais herdados: 4 (🟢 3 · ⚪ 1) |
| Ferramentas novas | pydantic/pydantic-ai, ggml-org/llama.cpp, stanfordnlp/dspy |
| Dados herdados | decisão de 26/09: Qwen3-8B local único; testes de modelos contra o gabarito de 120 vereditos |
| Cuidados | nenhum motor chama a IA por fora do serviço |

#### `NE3-008` · `eldorado/base/nucleo/comandos.py`

**Finalidade:** Os comandos da plataforma: rodar uma passagem, um motor, um piloto, a bateria, a importação, a fotografia; pausar e retomar; tudo também acionável pelo painel.

**Atende à finalidade da titular:** coleta local no computador da titular.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | passagem; motor <id>; piloto <A/B>; bateria; importar; fotografia; pausar; retomar |
| Recebe | comandos da titular ou dos fluxos |
| Entrega | execuções |
| Usa | `NE3-011` eldorado/base/fluxo/executor.py, `NE3-003` eldorado/base/nucleo/config.py |
| É usado por | — |
| Eventos que emite | `acionamento.feito` |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | comando com erro |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | comandos executados sem erro — limiares: sem erro / erro recuperado / erro |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | os mesmos comandos funcionam no GitHub, no computador local e pelo painel |
| Existe hoje no Eldorado0 | scripts/pausa_analise.py (pausar e retomar) |
| Ferramentas novas | fastapi/typer |
| Dados herdados | — |
| Cuidados | o mesmo comando para o fluxo do GitHub, o computador local e o painel |

#### `NE3-009` · `eldorado/base/nucleo/seguranca.py`

**Finalidade:** Senha do painel e bloqueio de publicação de credenciais e de dados pessoais (CPF removido onde não for necessário).

**Atende à finalidade da titular:** CPF removido; segurança dos dados.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | senha do painel; varrer credenciais; varrer CPF e removê-lo onde não for necessário |
| Recebe | arquivos a publicar |
| Entrega | permitido ou barrado |
| Usa | `NE3-038` eldorado/base/painel/api.py |
| É usado por | `NE3-038` eldorado/base/painel/api.py |
| Eventos que emite | `alarme.aberto` |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | padrões de credencial e CPF |
| Alarmes | credencial ou CPF numa publicação |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | nenhuma credencial ou CPF desnecessário publicado — limiares: 0 / — / qualquer ocorrência |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | publicação com credencial falsa é barrada |
| Existe hoje no Eldorado0 | scripts/acesso.py; scripts/verificar_privacidade.py · itens atuais herdados: 2 (⚪ 2) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | varredura antes de toda publicação |


### Workflow, fila e agenda

#### `NE3-010` · `eldorado/base/fluxo/definicao.py`

**Finalidade:** O formato do workflow (conceito do n8n): nós, conexões, saída de erro, retentativas por nó, dados fixos de teste, versão.

**Atende à finalidade da titular:** workflow próprio pelo conceito do n8n.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | ler o workflow (nós, conexões, saída de erro, retentativas); validar; versionar |
| Recebe | workflows em TOML |
| Entrega | workflow validado |
| Usa | `NE3-001` eldorado/base/nucleo/contratos.py |
| É usado por | `NE3-011` eldorado/base/fluxo/executor.py |
| Eventos que emite | `workflow.versao` |
| Eventos que consome | — |
| Tabelas que lê | cerebro.workflow |
| Dados | cerebro.db: workflow |
| Configuração | workflows/*.toml |
| Alarmes | workflow inválido |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | workflows válidos e versionados — limiares: todos válidos / versão antiga em uso / inválido |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | workflow com saída de erro leva o livro à devolução |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | n8n-io/n8n (desenho: interfaces.ts) |
| Dados herdados | — |
| Cuidados | a saída de erro é a devolução do livro |

#### `NE3-011` · `eldorado/base/fluxo/executor.py`

**Finalidade:** O executor durável: percorre os nós, aplica retentativas, segue pela saída de erro, grava o estado a cada passo e retoma de onde parou depois de uma queda.

**Atende à finalidade da titular:** robusto, não quebra.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | percorrer os nós; envolver cada chamada com recibo; retentar por nó; seguir pela saída de erro; gravar o estado a cada passo; retomar após queda |
| Recebe | workflow e entradas |
| Entrega | execução com estado gravado |
| Usa | `NE3-010` eldorado/base/fluxo/definicao.py, `NE3-012` eldorado/base/fluxo/fila.py, `NE3-004` eldorado/base/nucleo/eventos.py |
| É usado por | `NE3-008` eldorado/base/nucleo/comandos.py, `NE3-015` eldorado/base/cerebro/regencia.py |
| Eventos que emite | `execucao.passo`, `chamada.recibo` |
| Eventos que consome | `acionamento.feito` |
| Tabelas que lê | cerebro.execucao |
| Dados | cerebro.db: execucao, execucao_passo |
| Configuração | tentativas por nó |
| Alarmes | execução interrompida sem retomada |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | execuções retomadas sem perda; passos com falha — limiares: 100% retomadas / alguma refeita do início / perda de estado |
| Indicador · linhas | 5 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | interromper no meio e retomar do mesmo passo |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | n8n-io/n8n (desenho: workflow-execute.ts), hatchet-dev/hatchet (conceito de execução durável) |
| Dados herdados | lição da carga histórica de 5 anos que falhou sem retomada |
| Cuidados | nada roda fora do executor |

#### `NE3-012` · `eldorado/base/fluxo/fila.py`

**Finalidade:** A fila de tarefas e o agendamento em SQLite: tarefas imediatas, periódicas e reagendadas (as esperas de 6 h e 24 h das tentativas).

**Atende à finalidade da titular:** até 3 tentativas com intervalo.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | enfileirar; agendar (6 h, 24 h); periódicas; consultar o governador antes de iniciar |
| Recebe | tarefas |
| Entrega | tarefas executadas |
| Usa | `NE3-021` eldorado/base/cerebro/governador.py |
| É usado por | `NE3-011` eldorado/base/fluxo/executor.py, `NE3-013` eldorado/base/fluxo/agenda.py, `NE3-021` eldorado/base/cerebro/governador.py |
| Eventos que emite | — |
| Eventos que consome | `acionamento.feito` |
| Tabelas que lê | fila.db |
| Dados | fila.db (Huey) |
| Configuração | trabalhadores, prioridades |
| Alarmes | tarefa atrasada além da janela |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | tarefas atrasadas; tarefas com erro — limiares: 0 atrasadas / até 5% / acima |
| Indicador · linhas | 4 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | tarefa reagendada roda na hora certa |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | coleifer/huey |
| Dados herdados | — |
| Cuidados | Huey medido: 4,3 mil tarefas/s |

#### `NE3-013` · `eldorado/base/fluxo/agenda.py`

**Finalidade:** A agenda de cada motor e alvo (horários, dias, janelas previstas), consultada pela Regência; uma passagem por janela.

**Atende à finalidade da titular:** lição das 425 execuções em 7 horas.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | montar a janela de cada motor e alvo; aplicar as previsões; uma passagem por janela |
| Recebe | configuração dos motores e previsões |
| Entrega | o que está devido em cada janela |
| Usa | `NE3-012` eldorado/base/fluxo/fila.py, `NE3-076` eldorado/base/analise/preditivo.py |
| É usado por | `NE3-015` eldorado/base/cerebro/regencia.py |
| Eventos que emite | — |
| Eventos que consome | `previsao.calculada` |
| Tabelas que lê | cerebro.agenda |
| Dados | cerebro.db: agenda |
| Configuração | agenda dos motores |
| Alarmes | disparos excessivos |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | motores devidos e acionados no horário — limiares: disparos = devidos / até 20% a mais / mais |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um motor de cadência diária roda uma vez por dia |
| Existe hoje no Eldorado0 | scripts/agenda_motores.py; config/agenda_motores.json |
| Ferramentas novas | — |
| Dados herdados | agenda de 76 motores, com o motivo de cada horário |
| Cuidados | lição: 425 execuções em 7 h (uma por minuto) |


### Cérebro: Regência e Pertinência e aprendizado

#### `NE3-014` · `eldorado/base/cerebro/rede.py`

**Finalidade:** A rede neural única: aprende a cada passagem (incremental) e dá as notas usadas pela Regência e pela Pertinência.

**Atende à finalidade da titular:** rede neural única que evolui a cada funcionamento.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | aprender de forma incremental a cada passagem; dar notas aos motores e livros; avaliar com os rótulos (veredito efetivo) |
| Recebe | medições, rótulos, retornos |
| Entrega | modelo e notas |
| Usa | `NE3-081` eldorado/banco/cerebro_db/esquema.py |
| É usado por | `NE3-015` eldorado/base/cerebro/regencia.py, `NE3-016` eldorado/base/cerebro/pertinencia.py |
| Eventos que emite | `modelo.treinado` |
| Eventos que consome | `veredito.gravado`, `medicao.registrada` |
| Tabelas que lê | cerebro.rotulo, cerebro.medicao |
| Dados | cerebro.db: modelo, rotulo |
| Configuração | características, limiares |
| Alarmes | queda de precisão |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | discernimento, precisão, revocação; idade do modelo — limiares: precisão ≥ 0,8 / 0,6 a 0,8 / < 0,6 |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um rótulo novo muda a nota na passagem seguinte |
| Existe hoje no Eldorado0 | src/rede_neural.py (lições), estado/rede_neural/modelo.json.gz · itens atuais herdados: 4 (🟢 3 · ⚪ 1) |
| Ferramentas novas | online-ml/river, scikit-learn/scikit-learn |
| Dados herdados | 1.531 vereditos como rótulos; medidas da rede (discernimento, precisão, revocação) |
| Cuidados | rótulos pelo veredito efetivo (a decisão da titular prevalece) |

#### `NE3-015` · `eldorado/base/cerebro/regencia.py`

**Finalidade:** A Regência: monta o plano de cada passagem, aciona os motores e os pilotos, valida a entrada de cada etapa e autoriza cada passagem de livro.

**Atende à finalidade da titular:** Regência aciona a entrada de todas as etapas.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | planejar a passagem; acionar motores e pilotos; validar a entrada de cada etapa; autorizar cada passagem de livro; transferir os incompletos à Verificação externa; liberar os finalizados ao Farol |
| Recebe | notas da rede, agenda, estado das etapas |
| Entrega | plano, acionamentos, autorizações |
| Usa | `NE3-014` eldorado/base/cerebro/rede.py, `NE3-011` eldorado/base/fluxo/executor.py, `NE3-013` eldorado/base/fluxo/agenda.py, `NE3-021` eldorado/base/cerebro/governador.py, `NE3-022` eldorado/base/cartorio/cartorio.py |
| É usado por | `NE3-019` eldorado/base/cerebro/completude.py, `NE3-086` .github/workflows/passagem.yml |
| Eventos que emite | `plano.criado`, `acionamento.feito` |
| Eventos que consome | `modelo.treinado`, `alerta.preditivo`, `tentativa.registrada` |
| Tabelas que lê | cerebro.plano, biblioteca.passaporte (visão) |
| Dados | cerebro.db: plano, acionamento |
| Configuração | ordem de resolução, tempo por etapa |
| Alarmes | plano não cumprido |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | acionamentos no horário; passagens autorizadas — limiares: plano cumprido ≥ 95% / 80 a 95% / < 80% |
| Indicador · linhas | 7 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | uma passagem de teste aciona as quatro etapas na ordem |
| Existe hoje no Eldorado0 | src/comando.py e src/maestro.py (só as lições) · itens atuais herdados: 7 (🟢 6 · ⚪ 1) |
| Ferramentas novas | NousResearch/hermes-agent (desenho: subagentes em paralelo) |
| Dados herdados | ordem de resolução: Goiás → Brasil → internacional → demais estados |
| Cuidados | poucas responsabilidades; tudo por contrato |

#### `NE3-016` · `eldorado/base/cerebro/pertinencia.py`

**Finalidade:** A Pertinência e aprendizado: mede a saída de cada etapa; na saída dos motores, decide se o achado é oportunidade, pelas regras da missão.

**Atende à finalidade da titular:** Pertinência mede a saída de todas as etapas.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | decidir se o achado é oportunidade (portão); medir a saída de cada etapa; registrar o motivo de toda recusa; devolver o retorno ao motor |
| Recebe | saídas das etapas |
| Entrega | decisões e medições |
| Usa | `NE3-014` eldorado/base/cerebro/rede.py, `NE3-035` eldorado/base/missao/portao.py, `NE3-018` eldorado/base/cerebro/regras.py |
| É usado por | — |
| Eventos que emite | `pertinencia.decidida`, `medicao.registrada` |
| Eventos que consome | `achado.entregue`, `relatorio.etapa` |
| Tabelas que lê | cerebro.regra |
| Dados | cerebro.db: decisao_pertinencia, medicao |
| Configuração | missão ativa |
| Alarmes | decisão contrariada por veredito |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | achados aceitos e barrados com motivo; decisões contrariadas por veredito — limiares: 0 contrariadas / 1 a 2% / mais |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | os casos de ouro dão 100% de acerto |
| Existe hoje no Eldorado0 | src/porta_oportunidade.py e src/regra_abrangencia.py (lógica validada, reescrita) · itens atuais herdados: 24 (🟢 14 · ⚪ 9 · 🔴 1) |
| Ferramentas novas | — |
| Dados herdados | regras do portão e decisões da titular |
| Cuidados | o motor não decide pertinência |

#### `NE3-017` · `eldorado/base/cerebro/aprendizado.py`

**Finalidade:** O ciclo de aprendizado: guarda como temporário (30 dias), promove a permanente o que provou funcionar, arquiva o que falhou e devolve o retorno a cada módulo.

**Atende à finalidade da titular:** Cérebro com temporários de 30 dias e permanentes.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | registrar como temporário (30 dias); promover pelo uso e pelo resultado; arquivar o que falhou; apagar do Cérebro o temporário vencido; devolver aos módulos |
| Recebe | medições e retornos |
| Entrega | aprendizados e retornos |
| Usa | `NE3-081` eldorado/banco/cerebro_db/esquema.py, `NE3-002` eldorado/base/nucleo/registro.py |
| É usado por | — |
| Eventos que emite | `aprendizado.registrado`, `aprendizado.promovido`, `aprendizado.arquivado` |
| Eventos que consome | `pertinencia.decidida`, `veredito.gravado` |
| Tabelas que lê | cerebro.aprendizado_* |
| Dados | cerebro.db: aprendizado_temporario, aprendizado_permanente |
| Configuração | critério de promoção |
| Alarmes | temporário vencido não apagado |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | aprendizados promovidos e arquivados — limiares: retenção cumprida / atraso < 1 dia / maior |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um aprendizado vencido some do Cérebro e nada some da Biblioteca |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 26 (🟢 17 · ⚪ 8 · 🔴 1) |
| Ferramentas novas | NousResearch/hermes-agent (desenho: learning_graph, learning_mutations) |
| Dados herdados | histórico de erros de 186 motores (01/10 a 22/10) |
| Cuidados | uso e resultado decidem a promoção |

#### `NE3-018` · `eldorado/base/cerebro/regras.py`

**Finalidade:** A tabela única de regras e decisões da titular, com data, alcance e precedência; a regra mais recente da titular prevalece.

**Atende à finalidade da titular:** decisões da titular prevalecem.

| Campo | Esboço |
| --- | --- |
| Construção | **CONFIGURAR** — só configuração (dados), lida por um arquivo de código existente |
| Funções principais | registrar regra com data, alcance e precedência; dar a regra vigente de cada tema; listar contradições |
| Recebe | decisões |
| Entrega | regra vigente para cada tema |
| Usa | `NE3-081` eldorado/banco/cerebro_db/esquema.py |
| É usado por | `NE3-016` eldorado/base/cerebro/pertinencia.py, `NE3-035` eldorado/base/missao/portao.py |
| Eventos que emite | `regra.registrada` |
| Eventos que consome | — |
| Tabelas que lê | cerebro.regra |
| Dados | cerebro.db: regra |
| Configuração | regras.toml |
| Alarmes | contradição aberta |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | decisões aplicadas; contradições abertas (devem ser zero) — limiares: 0 contradições / 1 / mais |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | a regra mais recente da titular prevalece |
| Existe hoje no Eldorado0 | MAPA-REGRAS-E-FUNCIONALIDADES-ELDORADO.md (540 decisões, 9 temas de precedência) |
| Ferramentas novas | — |
| Dados herdados | 2.988 regras mapeadas |
| Cuidados | nenhuma regra fica só no código |

#### `NE3-019` · `eldorado/base/cerebro/completude.py`

**Finalidade:** Confere se todos os dados do dia foram obtidos: motores devidos que leram, alvos na janela, livros que avançaram.

**Atende à finalidade da titular:** todos os dados do dia obtidos.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | comparar o plano com o feito; listar o que reacionar |
| Recebe | plano e execuções |
| Entrega | cobertura do dia e o que reacionar |
| Usa | `NE3-015` eldorado/base/cerebro/regencia.py |
| É usado por | — |
| Eventos que emite | `medicao.registrada` |
| Eventos que consome | `motor.execucao`, `plano.criado` |
| Tabelas que lê | cerebro.cobertura_dia |
| Dados | cerebro.db: cobertura_dia |
| Configuração | — |
| Alarmes | dia incompleto |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | cobertura do dia (meta 100%) — limiares: 100% / 90 a 99% / < 90% |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um motor que não rodou aparece como reacionar |
| Existe hoje no Eldorado0 | src/cobertura.py (lição); docs/dados/validacao_motores_mes.json (o formato dia a dia) · itens atuais herdados: 5 (🟢 3 · ⚪ 2) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | uma única medida por indicador (lição das medidas que discordavam) |

#### `NE3-020` · `eldorado/base/cerebro/medicao.py`

**Finalidade:** O motor de indicadores: calcula, a cada passagem, o ponto (funciona), o círculo (atinge a finalidade) e as linhas (ligações confirmadas) de cada arquivo, e agrega por componente, parte e sistema.

**Atende à finalidade da titular:** monitoramento individual de cada arquivo.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | calcular ponto, círculo e linhas de cada arquivo; agregar por componente, parte e sistema; comparar ligações declaradas com as usadas |
| Recebe | recibos das chamadas, métricas declaradas, ligações declaradas |
| Entrega | medições em quatro níveis |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py, `NE3-002` eldorado/base/nucleo/registro.py |
| É usado por | — |
| Eventos que emite | `medicao.registrada` |
| Eventos que consome | `chamada.recibo`, `execucao.passo`, `modulo.registrado` |
| Tabelas que lê | cerebro.recibo |
| Dados | cerebro.db: medicao |
| Configuração | métrica de cada arquivo (desta especificação) |
| Alarmes | arquivo sem medição |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | arquivos com as três medições na passagem (meta 100%) — limiares: 100% medidos / 95 a 99% / < 95% |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um arquivo que falha fica vermelho na mesma passagem |
| Existe hoje no Eldorado0 | MARCADORES-ELDORADO-FINAL.csv (o padrão ponto, círculo e linha de 735 itens) |
| Ferramentas novas | — |
| Dados herdados | métricas declaradas de cada item atual |
| Cuidados | uma única medida por indicador, definida por escrito |

#### `NE3-021` · `eldorado/base/cerebro/governador.py`

**Finalidade:** O governador de carga: mede a máquina e mantém o uso abaixo de 85% (processador, memória, disco), reduzindo o paralelismo ou adiando tarefas.

**Atende à finalidade da titular:** até 85% da capacidade da máquina.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | medir processador, memória e disco; dar a permissão de paralelismo; adiar as tarefas pesadas |
| Recebe | medições da máquina |
| Entrega | permissão de paralelismo |
| Usa | `NE3-012` eldorado/base/fluxo/fila.py |
| É usado por | `NE3-007` eldorado/base/nucleo/ia.py, `NE3-012` eldorado/base/fluxo/fila.py, `NE3-015` eldorado/base/cerebro/regencia.py, `NE3-040` eldorado/base/painel/maquina.py, `NE3-043` eldorado/motores/acesso/escada.py, `NE3-046` eldorado/motores/acesso/navegador.py |
| Eventos que emite | `maquina.leitura` |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | cerebro.db: maquina |
| Configuração | limite 85% |
| Alarmes | acima de 85% por mais de 1 minuto |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | tempo acima de 85% (meta zero) — limiares: 0 min acima / < 5 min por passagem / mais |
| Indicador · linhas | 7 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | uma carga artificial reduz o paralelismo antes de passar de 85% |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | giampaolo/psutil |
| Dados herdados | — |
| Cuidados | decide antes de iniciar, não depois de travar |


### Cartório: base de passagem

#### `NE3-022` · `eldorado/base/cartorio/cartorio.py`

**Finalidade:** O Cartório, base de passagem: recebe os achados aceitos, separa para criar ou vincular livro, aciona a certificação e a classificação e move os livros entre as fases.

**Atende à finalidade da titular:** o Cartório como base de passagem.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | receber os achados aceitos; acionar o índice, a certificação e os selos; mover os livros entre as fases; balcões das 10 abordagens |
| Recebe | achados aceitos e retornos |
| Entrega | livros movidos |
| Usa | `NE3-023` eldorado/base/cartorio/passaporte.py, `NE3-024` eldorado/base/cartorio/indice.py, `NE3-025` eldorado/base/cartorio/certificacao.py, `NE3-026` eldorado/base/cartorio/selos.py, `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-015` eldorado/base/cerebro/regencia.py, `NE3-028` eldorado/base/investigacao/investigacao.py, `NE3-029` eldorado/base/verificacao/verificacao.py |
| Eventos que emite | `relatorio.etapa` |
| Eventos que consome | `pertinencia.decidida`, `certidao.gravada` |
| Tabelas que lê | biblioteca (visões) |
| Dados | biblioteca.db: livro, passaporte, passagem |
| Configuração | abordagens |
| Alarmes | livro parado além do previsto |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros movidos por passagem; livros parados além do previsto — limiares: 0 parados / até 5% / mais |
| Indicador · linhas | 8 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um achado aceito vira livro certificado e movido |
| Existe hoje no Eldorado0 | src/cartorio.py; src/cartorio_linha.py (linha de produção e as 10 abordagens) · itens atuais herdados: 24 (🟢 15 · ⚪ 9) |
| Ferramentas novas | — |
| Dados herdados | as 10 abordagens, por balcão; eficiência por item dos 12 |
| Cuidados | só o Cartório move livros |

#### `NE3-023` · `eldorado/base/cartorio/passaporte.py`

**Finalidade:** Move o livro entre as fases com a autorização da Regência; registra cada passagem e as até 3 tentativas por ferramenta.

**Atende à finalidade da titular:** cada livro movido com base na Regência e na Pertinência.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | pedir autorização à Regência; mover; registrar a tentativa |
| Recebe | decisões |
| Entrega | passaporte atualizado |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-022` eldorado/base/cartorio/cartorio.py |
| Eventos que emite | `livro.passagem`, `tentativa.registrada` |
| Eventos que consome | `acionamento.feito` |
| Tabelas que lê | biblioteca.passaporte |
| Dados | biblioteca.db: passaporte, passagem, tentativa |
| Configuração | — |
| Alarmes | passagem recusada |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros sem passaporte (zero) — limiares: 0 livros sem passaporte / — / qualquer |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | passagem sem autorização é recusada pelo banco |
| Existe hoje no Eldorado0 | src/fila_livros.py (lição) · itens atuais herdados: 2 (🟢 2) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | passagem sem a Regência é recusada pelo banco |

#### `NE3-024` · `eldorado/base/cartorio/indice.py`

**Finalidade:** Cria livro novo ou vincula a um existente pela chave da missão; reconhece o mesmo edital achado em canais diferentes; une duplicados sem apagar.

**Atende à finalidade da titular:** redundância entre canais unida num livro.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | calcular a chave; achar livro igual ou quase igual; criar, vincular ou unir |
| Recebe | achado aceito |
| Entrega | livro criado ou vinculado |
| Usa | `NE3-037` eldorado/base/missao/chave.py, `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-022` eldorado/base/cartorio/cartorio.py |
| Eventos que emite | `livro.criado`, `livro.vinculado`, `livro.unido` |
| Eventos que consome | `pertinencia.decidida` |
| Tabelas que lê | biblioteca.livro |
| Dados | biblioteca.db: livro, uniao |
| Configuração | limiar de semelhança |
| Alarmes | duplicado detectado depois |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | duplicados unidos; livros criados e vinculados — limiares: 0 duplicados novos / até 1% / mais |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | o mesmo edital achado em dois canais vira um só livro |
| Existe hoje no Eldorado0 | src/indice_livros.py; src/chaves_livros.py; src/unificar_livros.py · itens atuais herdados: 6 (🟢 5 · ⚫ 1) |
| Ferramentas novas | ekzhu/datasketch |
| Dados herdados | — |
| Cuidados | MinHash para quase duplicatas entre canais |

#### `NE3-025` · `eldorado/base/cartorio/certificacao.py`

**Finalidade:** Certifica cada item no texto oficial, com trecho e página; agrega o que vem da Investigação e do Chrome; dispensa só com justificativa.

**Atende à finalidade da titular:** texto literal completo como prova.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | localizar cada item no texto; registrar trecho e página; dispensar com justificativa; agregar o que veio da Investigação e do Chrome |
| Recebe | livro e textos |
| Entrega | certidões |
| Usa | `NE3-036` eldorado/base/missao/itens.py, `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-022` eldorado/base/cartorio/cartorio.py |
| Eventos que emite | `certidao.gravada` |
| Eventos que consome | `relatorio.etapa` |
| Tabelas que lê | biblioteca.pagina, biblioteca.item |
| Dados | biblioteca.db: certidao |
| Configuração | padrões de edital, dispensas |
| Alarmes | item sem prova marcado como provado |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | itens certificados por livro; livros 12 de 12 — limiares: itens com prova / — / item sem prova |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | os 12 itens de um edital real certificados com trecho e página |
| Existe hoje no Eldorado0 | src/completude.py; src/dispensas_itens.py; config/padroes_edital.json; config/dispensas_por_regime.json · itens atuais herdados: 16 (🟢 11 · ⚪ 3 · 🔴 1 · ⚫ 1) |
| Ferramentas novas | — |
| Dados herdados | padrões de edital; gabaritos do Cartório; dispensas por regime |
| Cuidados | lê o texto já extraído pelos motores; não abre PDF |

#### `NE3-026` · `eldorado/base/cartorio/selos.py`

**Finalidade:** Calcula os dois selos de cada livro a cada passagem: a estrela (completude dos 12 itens) e o selo do livro (previsibilidade pelo histórico).

**Atende à finalidade da titular:** livros e estrelas de ouro, prata e bronze.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | calcular a estrela (completude); calcular o selo do livro (previsibilidade) |
| Recebe | livro |
| Entrega | estrela e selo do livro |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py, `NE3-076` eldorado/base/analise/preditivo.py |
| É usado por | `NE3-022` eldorado/base/cartorio/cartorio.py |
| Eventos que emite | `selo.calculado` |
| Eventos que consome | `certidao.gravada`, `previsao.calculada` |
| Tabelas que lê | biblioteca.livro |
| Dados | biblioteca.db: livro (selos) |
| Configuração | critérios |
| Alarmes | livro sem selo |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros sem selo (zero; hoje 70%) — limiares: 0 sem selo / até 5% / mais (hoje 70%) |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | livro com 12 de 12 recebe a estrela de ouro |
| Existe hoje no Eldorado0 | src/criterio_selos.py (04/10); src/selo_livros.py (03/10) · itens atuais herdados: 8 (🟢 6 · 🔴 2) |
| Ferramentas novas | — |
| Dados herdados | critério único e critério histórico |
| Cuidados | “não informado” não é dispensa |

#### `NE3-027` · `eldorado/base/cartorio/site_oficial.py`

**Finalidade:** Acha o link oficial (o órgão, não o republicador) e aplica a régua do vetor; o que veio de portal é pista.

**Atende à finalidade da titular:** link de divulgação e link oficial.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | achar o órgão que publicou; aplicar a régua do vetor; marcar pista |
| Recebe | link de divulgação |
| Entrega | link oficial |
| Usa | `NE3-043` eldorado/motores/acesso/escada.py, `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | — |
| Eventos que emite | `certidao.gravada` |
| Eventos que consome | `livro.criado` |
| Tabelas que lê | cerebro.dominio |
| Dados | biblioteca.db: livro (links) |
| Configuração | republicadores |
| Alarmes | link de vetor como oficial |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros com link oficial aprovado — limiares: 0 / — / qualquer |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um edital achado num portal ganha o link do órgão |
| Existe hoje no Eldorado0 | src/fonte_oficial.py; src/sites_oficiais.py; config/republicadores.json; estado/interceptador/sites_oficiais.json · itens atuais herdados: 8 (🟢 7 · ⚪ 1) |
| Ferramentas novas | — |
| Dados herdados | rotas que funcionam por órgão; lista de republicadores |
| Cuidados | vetor nunca é fonte |


### Etapa de Investigação

#### `NE3-028` · `eldorado/base/investigacao/investigacao.py`

**Finalidade:** A etapa de Investigação: recebe do Cartório os livros que esgotaram os motores, na ordem escolhida pela Regência, aciona o piloto B e devolve o resultado ao Cartório.

**Atende à finalidade da titular:** Investigação com o Interceptador depois dos motores.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | receber os livros esgotados; ordenar pela Regência; acionar o piloto B; devolver ao Cartório |
| Recebe | livros direcionados |
| Entrega | itens comprovados |
| Usa | `NE3-070` eldorado/motores/pilotos/interceptador.py, `NE3-022` eldorado/base/cartorio/cartorio.py |
| É usado por | — |
| Eventos que emite | `acionamento.feito`, `relatorio.etapa` |
| Eventos que consome | `tentativa.registrada` |
| Tabelas que lê | biblioteca (visão dos esgotados) |
| Dados | cerebro.db: acionamento |
| Configuração | — |
| Alarmes | piloto 1 dia sem sucesso |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros investigados e itens comprovados por livro — limiares: voos com sucesso ≥ 80% / 50 a 80% / < 50% |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um livro esgotado recebe itens novos do piloto |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 2 (🟢 1 · ⚪ 1) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | o piloto lê e grava pelo contrato da Biblioteca (lição do Interceptador parado) |


### Etapa de Verificação externa

#### `NE3-029` · `eldorado/base/verificacao/verificacao.py`

**Finalidade:** A etapa de Verificação externa: separa os livros transferidos pela Regência, gera o lote, recebe a decisão final (validação, dispensa justificada ou exclusão lógica).

**Atende à finalidade da titular:** validação final ou descarte pelo Chrome.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | separar os transferidos; gerar o lote; receber a decisão final |
| Recebe | livros transferidos |
| Entrega | decisões finais |
| Usa | `NE3-030` eldorado/base/verificacao/lote.py, `NE3-031` eldorado/base/verificacao/importacao.py, `NE3-022` eldorado/base/cartorio/cartorio.py |
| É usado por | — |
| Eventos que emite | `livro.excluido_logicamente`, `relatorio.etapa` |
| Eventos que consome | `veredito.gravado` |
| Tabelas que lê | biblioteca (visão dos incompletos) |
| Dados | biblioteca.db: veredito |
| Configuração | — |
| Alarmes | livro em verificação além do prazo |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros em verificação; decisões recebidas — limiares: decididos no prazo / atrasados < 10% / mais |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um livro termina validado, dispensado ou excluído logicamente |
| Existe hoje no Eldorado0 | src/pesquisa_externa.py · itens atuais herdados: 5 (⚪ 3 · 🟢 1 · 🔴 1) |
| Ferramentas novas | — |
| Dados herdados | aprendizado do Chrome (onde estava, busca que funcionou) |
| Cuidados | exclusão só lógica |

#### `NE3-030` · `eldorado/base/verificacao/lote.py`

**Finalidade:** Monta o lote do Claude no Chrome por grupo, com o que falta em cada livro.

**Atende à finalidade da titular:** Chrome com lotes claros.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | agrupar; descrever o que falta |
| Recebe | livros separados |
| Entrega | lote |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-029` eldorado/base/verificacao/verificacao.py |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | biblioteca |
| Dados | — |
| Configuração | tamanho do lote |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | lotes gerados — limiares: lotes gerados / — / falha |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | lote com o que falta em cada livro |
| Existe hoje no Eldorado0 | scripts/gerar_lote_chrome.py · itens atuais herdados: 3 (⚪ 2 · 🟢 1) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | lote pequeno e bem formulado |

#### `NE3-031` · `eldorado/base/verificacao/importacao.py`

**Finalidade:** Importa a resposta do Chrome como eventos; só documento oficial; aplica as decisões da titular.

**Atende à finalidade da titular:** validação pelo Chrome com prova.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | ler a resposta; exigir documento oficial; gerar eventos |
| Recebe | resposta do Chrome |
| Entrega | eventos |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py |
| É usado por | `NE3-029` eldorado/base/verificacao/verificacao.py |
| Eventos que emite | `certidao.gravada`, `veredito.gravado` |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | biblioteca.db: certidao, veredito |
| Configuração | — |
| Alarmes | resposta sem documento oficial |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | respostas importadas e recusadas — limiares: importadas / recusadas < 10% / mais |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | resposta sem documento oficial é recusada |
| Existe hoje no Eldorado0 | scripts/importar_verificacao_livros.py · itens atuais herdados: 13 (⚪ 11 · 🟢 2) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-032` · `eldorado/base/verificacao/relatorio_faltas.py`

**Finalidade:** Grava em cada livro o relatório do que faltou e do que foi certificado ao fim da Verificação externa.

**Atende à finalidade da titular:** relatório do que faltou ao final.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | listar o que faltou; listar o que foi certificado |
| Recebe | livro após a decisão |
| Entrega | relatório no livro |
| Usa | `NE3-075` eldorado/base/analise/historia.py |
| É usado por | — |
| Eventos que emite | `relatorio.etapa` |
| Eventos que consome | `veredito.gravado` |
| Tabelas que lê | biblioteca.certidao |
| Dados | biblioteca.db: relatorio_etapa |
| Configuração | — |
| Alarmes | livro finalizado sem relatório |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros com relatório final — limiares: 0 sem relatório / — / qualquer |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | todo livro finalizado tem o relatório do que faltou |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |


### Transferência ao Farol

#### `NE3-033` · `eldorado/base/transferencia/farol.py`

**Finalidade:** O único ponto de comunicação com o Farol: entrega os livros finalizados num formato de exportação estável e registra a transferência.

**Atende à finalidade da titular:** único ponto de comunicação com o Farol.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | conferir que o livro está finalizado; exportar no formato estável; registrar |
| Recebe | livros liberados pela Regência |
| Entrega | pacote ao Farol |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | — |
| Eventos que emite | `transferencia.feita` |
| Eventos que consome | `acionamento.feito` |
| Tabelas que lê | biblioteca (livro completo) |
| Dados | biblioteca.db: transferencia |
| Configuração | versão do formato |
| Alarmes | transferência recusada |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros transferidos; recusados pelo contrato — limiares: todas aceitas / — / recusa |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um livro finalizado chega ao Farol completo |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 18 (🟢 16 · ⚪ 2) |
| Ferramentas novas | msgspec/msgspec |
| Dados herdados | — |
| Cuidados | o Farol nunca escreve no Eldorado |


### Missão (finalidade trocável)

#### `NE3-034` · `eldorado/base/missao/oportunidades.toml`

**Finalidade:** A declaração da missão ativa: o que é um livro, as etapas, o destino; trocar a finalidade é trocar este arquivo e os três seguintes.

**Atende à finalidade da titular:** finalidade trocável.

| Campo | Esboço |
| --- | --- |
| Construção | **CONFIGURAR** — só configuração (dados), lida por um arquivo de código existente |
| Funções principais | declarar a missão |
| Recebe | — |
| Entrega | missão |
| Usa | — |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | livro, itens, etapas, destino |
| Alarmes | missão inválida |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | missão válida — limiares: válida / — / inválida |
| Indicador · linhas | 0 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | trocar por uma missão de teste muda o portão sem mudar a base |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-035` · `eldorado/base/missao/portao.py`

**Finalidade:** As regras do portão desta missão (terceiro setor, território, Goiás restrito, emendas, extratos), lidas da tabela de regras.

**Atende à finalidade da titular:** regras do portão da titular.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | aplicar as regras vigentes ao achado |
| Recebe | achado |
| Entrega | decisão e motivo |
| Usa | `NE3-018` eldorado/base/cerebro/regras.py |
| É usado por | `NE3-016` eldorado/base/cerebro/pertinencia.py |
| Eventos que emite | — |
| Eventos que consome | `regra.registrada` |
| Tabelas que lê | cerebro.regra |
| Dados | cerebro.db: regra |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | decisões contrariadas por veredito (zero) — limiares: casos de ouro 100% / — / abaixo |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | os casos de ouro dos vereditos |
| Existe hoje no Eldorado0 | src/porta_oportunidade.py; src/regra_abrangencia.py; config/escopo.json; config/territorio_goias.json · itens atuais herdados: 7 (🟢 7) |
| Ferramentas novas | — |
| Dados herdados | casos de ouro dos vereditos |
| Cuidados | testado com casos de ouro |

#### `NE3-036` · `eldorado/base/missao/itens.py`

**Finalidade:** Os 12 itens do livro, como cada um se prova e as dispensas por tipo de recurso.

**Atende à finalidade da titular:** validada só com 12 de 12.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | listar os 12 itens; como cada um se prova; dispensas |
| Recebe | — |
| Entrega | itens |
| Usa | — |
| É usado por | `NE3-025` eldorado/base/cartorio/certificacao.py |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | biblioteca.db: item |
| Configuração | itens.toml |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | itens definidos — limiares: definidos / — / faltando |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | os 12 itens carregados |
| Existe hoje no Eldorado0 | src/criterio_selos.py (os 12 itens); config/dispensas_por_regime.json |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-037` · `eldorado/base/missao/chave.py`

**Finalidade:** A chave do livro nesta missão (programa, órgão, local, objeto).

**Atende à finalidade da titular:** um livro por oportunidade.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | montar a chave |
| Recebe | achado |
| Entrega | chave |
| Usa | — |
| É usado por | `NE3-024` eldorado/base/cartorio/indice.py |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | chaves que geraram duplicado — limiares: sem duplicado / — / duplicado |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | duas grafias do mesmo programa dão a mesma chave |
| Existe hoje no Eldorado0 | src/chaves_livros.py |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |


### Painel, API e Sala de controle

#### `NE3-038` · `eldorado/base/painel/api.py`

**Finalidade:** A API local de controle e de dados: o painel consulta as visões; a titular aciona, pausa e decide.

**Atende à finalidade da titular:** controle do sistema pelo painel.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | servir as visões; receber comandos da titular; senha |
| Recebe | pedidos do painel |
| Entrega | dados e comandos |
| Usa | `NE3-039` eldorado/base/painel/visoes.py, `NE3-009` eldorado/base/nucleo/seguranca.py |
| É usado por | `NE3-009` eldorado/base/nucleo/seguranca.py |
| Eventos que emite | `acionamento.feito` |
| Eventos que consome | — |
| Tabelas que lê | visões |
| Dados | leitura dos três bancos |
| Configuração | porta, senha |
| Alarmes | API fora |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | respostas no prazo; erros — limiares: disponível / lenta / fora |
| Indicador · linhas | 3 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | o painel abre lendo só a API |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | fastapi/fastapi |
| Dados herdados | — |
| Cuidados | leitura só por visões |

#### `NE3-039` · `eldorado/base/painel/visoes.py`

**Finalidade:** Gera, a cada passagem, as visões que alimentam as telas: toda tela de oportunidade lê a Biblioteca; toda tela de operação lê o Cérebro.

**Atende à finalidade da titular:** todas as telas de oportunidade vêm da Biblioteca.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | gerar as visões da Biblioteca e do Cérebro; conferir que a visão é igual à consulta |
| Recebe | bancos |
| Entrega | visões (JSON) publicadas |
| Usa | `NE3-072` eldorado/banco/biblioteca/esquema.py, `NE3-081` eldorado/banco/cerebro_db/esquema.py |
| É usado por | `NE3-005` eldorado/base/nucleo/gravador.py, `NE3-038` eldorado/base/painel/api.py, `NE3-042` eldorado/base/painel/paginas/, `NE3-088` .github/workflows/painel.yml |
| Eventos que emite | — |
| Eventos que consome | `selo.calculado`, `medicao.registrada` |
| Tabelas que lê | três bancos (leitura) |
| Dados | visões |
| Configuração | visões |
| Alarmes | visão diferente do banco |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | visões iguais à consulta ao banco — limiares: iguais / — / diferente |
| Indicador · linhas | 6 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | o número da tela é igual à consulta ao banco |
| Existe hoje no Eldorado0 | src/dashboard_dados.py (lições: uma única fonte por tela) |
| Ferramentas novas | simonw/datasette, duckdb/duckdb, msgspec/msgspec |
| Dados herdados | decisões da titular sobre o calendário e a Bússola |
| Cuidados | uma única fonte de verdade por tela |

#### `NE3-040` · `eldorado/base/painel/maquina.py`

**Finalidade:** O mostrador da máquina na tela inicial: configuração, uso em tempo real (processador, memória, disco, rede), tamanho de cada parte e o limite de 85%.

**Atende à finalidade da titular:** mostrador da máquina na tela inicial.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | mostrar a configuração; mostrar o uso em tempo real; mostrar o tamanho de cada parte; linha dos 85% |
| Recebe | medições do governador |
| Entrega | mostrador |
| Usa | `NE3-021` eldorado/base/cerebro/governador.py |
| É usado por | `NE3-042` eldorado/base/painel/paginas/ |
| Eventos que emite | — |
| Eventos que consome | `maquina.leitura` |
| Tabelas que lê | cerebro.maquina |
| Dados | cerebro.db: maquina |
| Configuração | intervalo de atualização |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | mostrador atualizado em tempo real — limiares: atualizado / atraso / parado |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | o mostrador muda quando a carga muda |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | giampaolo/psutil, nicolargo/glances (referência de interface) |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-041` · `eldorado/base/painel/sala.py`

**Finalidade:** A Sala de controle: cada arquivo do sistema como estrela (ponto, círculo, linhas), os indicadores por nível, os alarmes e o Cérebro.

**Atende à finalidade da titular:** monitoramento de funcionamento, finalidade e ligações.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | estrelas por arquivo; indicadores por nível; alarmes |
| Recebe | medições e alarmes |
| Entrega | tela da sala |
| Usa | `NE3-081` eldorado/banco/cerebro_db/esquema.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | `medicao.registrada`, `alarme.aberto` |
| Tabelas que lê | cerebro.medicao, cerebro.alarme |
| Dados | cerebro.db: medicao, alarme |
| Configuração | — |
| Alarmes | sala desatualizada |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | sala publicada no prazo — limiares: atualizada na passagem / atraso de 1 / mais |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um alarme provocado aparece na sala |
| Existe hoje no Eldorado0 | src/sala_controle.py; vista v-neural do painel · itens atuais herdados: 25 (🟢 12 · ⚪ 11 · 🔴 2) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-042` · `eldorado/base/painel/paginas/`

**Finalidade:** As páginas do painel, reaproveitadas do dashboard validado: início (com o mostrador da máquina), calendário, oportunidades abertas, Bússola (47 motores), Cartório, Sala, Biblioteca (página do livro), postos dos pilotos e as telas do Farol preservadas.

**Atende à finalidade da titular:** painel reaproveitado; telas do Farol preservadas.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | início com o mostrador; calendário (abertas e previstas); oportunidades abertas; Bússola (47 motores); Cartório; Sala; página do livro (história); postos dos pilotos; telas do Farol preservadas |
| Recebe | visões |
| Entrega | páginas |
| Usa | `NE3-039` eldorado/base/painel/visoes.py, `NE3-040` eldorado/base/painel/maquina.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | visões |
| Dados | — |
| Configuração | — |
| Alarmes | página com erro de carga |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | páginas sem erro de carga — limiares: 0 erros / — / erro |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | todas as páginas abrem sem erro e sem endereço fixo |
| Existe hoje no Eldorado0 | docs/dashboard.html (11 vistas); docs/mapa-brasil.js; docs/mapa-arte.js · itens atuais herdados: 1 (🟢 1) |
| Ferramentas novas | — |
| Dados herdados | identidade visual validada |
| Cuidados | nenhum endereço fixo de repositório |


### Migração do Eldorado0 (operação temporária, 30 dias)

#### `NE3-084` · `eldorado/base/migracao/importar_eldorado0.py`

**Finalidade:** Importa do Eldorado0 os livros, as certidões, os vereditos, as empresas e o aprendizado, com CPF removido onde não for necessário; temporário, desligado em 30 dias.

**Atende à finalidade da titular:** aprendizado do Eldorado0 extraído antes do desligamento.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | ler o Eldorado0; remover CPF desnecessário; gerar eventos de importação; conferir as contagens |
| Recebe | Eldorado0 |
| Entrega | eventos de importação |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py |
| É usado por | — |
| Eventos que emite | `importacao.lote` |
| Eventos que consome | — |
| Tabelas que lê | Eldorado0 |
| Dados | todos |
| Configuração | origem |
| Alarmes | contagem diferente |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | contagens importadas iguais às de origem — limiares: iguais / — / diferente |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | as contagens importadas batem com a origem |
| Existe hoje no Eldorado0 | 3.668 livros, 2.706 certidões, 1.531 vereditos, APRENDIZADO-ELDORADO.json |
| Ferramentas novas | simonw/sqlite-utils |
| Dados herdados | todo o aprendizado |
| Cuidados | temporário |


### Análise: história do livro, previsão e calendário

#### `NE3-075` · `eldorado/base/analise/historia.py`

**Finalidade:** A história inteira de cada livro: motores e datas, informações obtidas, links, tentativas, passagens, relatórios por etapa, análises internas e externas.

**Atende à finalidade da titular:** cada livro com a sua história contada por inteiro.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | montar a história do livro (achados, motores, datas, links, tentativas, passagens, relatórios, análises) |
| Recebe | livro |
| Entrega | relatório do livro |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-032` eldorado/base/verificacao/relatorio_faltas.py |
| Eventos que emite | — |
| Eventos que consome | `relatorio.etapa`, `livro.passagem`, `transferencia.feita` |
| Tabelas que lê | biblioteca (tudo do livro) |
| Dados | biblioteca.db: relatorio_etapa |
| Configuração | modelo da página do livro |
| Alarmes | livro sem história |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | livros com história completa — limiares: todos completos / — / incompleto |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | a história de um livro conta todas as passagens |
| Existe hoje no Eldorado0 | src/historico_parecer.py (lição) · itens atuais herdados: 1 (🟢 1) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-076` · `eldorado/base/analise/preditivo.py`

**Finalidade:** A análise preditiva de cada livro e o alerta antes de abrir.

**Atende à finalidade da titular:** análise preditiva com alerta antes de abrir.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | prever a próxima edição; emitir o alerta antes de abrir |
| Recebe | histórico |
| Entrega | previsão |
| Usa | `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por | `NE3-013` eldorado/base/fluxo/agenda.py, `NE3-026` eldorado/base/cartorio/selos.py, `NE3-077` eldorado/base/analise/calendario.py |
| Eventos que emite | `previsao.calculada`, `alerta.preditivo` |
| Eventos que consome | `livro.criado`, `relatorio.etapa` |
| Tabelas que lê | biblioteca.achado, biblioteca.livro |
| Dados | biblioteca.db: previsao |
| Configuração | antecedência do alerta (30 dias) |
| Alarmes | previsão vencida sem alerta |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | alertas emitidos antes da abertura — limiares: alertas no prazo / — / perdido |
| Indicador · linhas | 4 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um livro com 3 edições anuais ganha previsão e alerta |
| Existe hoje no Eldorado0 | src/previsao.py; src/janelas.py; config/previsoes_especiais.json · itens atuais herdados: 14 (🟢 12 · ⚪ 2) |
| Ferramentas novas | scikit-learn/scikit-learn |
| Dados herdados | padrões de previsão e janelas confirmadas |
| Cuidados | — |

#### `NE3-077` · `eldorado/base/analise/calendario.py`

**Finalidade:** O calendário de oportunidades abertas e previstas.

**Atende à finalidade da titular:** calendário de abertas e previstas.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | compor as abertas e as previstas |
| Recebe | livros e previsões |
| Entrega | visão do calendário |
| Usa | `NE3-076` eldorado/base/analise/preditivo.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | `previsao.calculada` |
| Tabelas que lê | biblioteca.calendario (visão) |
| Dados | biblioteca.db: calendario (visão) |
| Configuração | regras do calendário |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | calendário atualizado na passagem — limiares: atualizado / — / parado |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | a oportunidade aparece na primeira data em que foi encontrada |
| Existe hoje no Eldorado0 | regras do calendário (06/09 e 20/09) · itens atuais herdados: 11 (🟢 8 · ⚪ 3) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |


### Qualidade e testes

#### `NE3-085` · `eldorado/testes/`

**Finalidade:** Testes de contrato, casos de ouro das regras, testes dos motores com páginas gravadas, teste do expurgo e testes dos bancos; rodam numa cópia isolada.

**Atende à finalidade da titular:** sistema que não quebra.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | contrato; casos de ouro; motores com páginas gravadas; expurgo; bancos; retomada do executor |
| Recebe | — |
| Entrega | bateria |
| Usa | `NE3-001` eldorado/base/nucleo/contratos.py |
| É usado por | `NE3-089` .github/workflows/qualidade.yml |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | bateria vermelha |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | bateria verde; casos de ouro 100% — limiares: verde / — / vermelha |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | a bateria inteira roda na cópia isolada |
| Existe hoje no Eldorado0 | scripts/testar.py (o isolamento, que funcionou) · itens atuais herdados: 12 (⚪ 10 · 🟢 2) |
| Ferramentas novas | kevin1024/vcrpy |
| Dados herdados | páginas reais gravadas; vereditos como casos de ouro |
| Cuidados | nenhuma mudança sem teste |


### Fluxos do GitHub e operação

#### `NE3-086` · `.github/workflows/passagem.yml`

**Finalidade:** A passagem: aciona a Regência; grava eventos; o gravador aplica; publica.

**Atende à finalidade da titular:** operação automática.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | rodar a passagem |
| Recebe | agenda |
| Entrega | eventos |
| Usa | `NE3-015` eldorado/base/cerebro/regencia.py, `NE3-005` eldorado/base/nucleo/gravador.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | janelas |
| Alarmes | passagem falhou |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | passagens no horário — limiares: sucesso / — / falha |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | uma passagem completa sem erro |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 23 (🟢 23) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | uma por janela |

#### `NE3-087` · `.github/workflows/pilotos.yml`

**Finalidade:** Os voos dos dois pilotos, acionados pela Regência.

**Atende à finalidade da titular:** pilotos ativos.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | voos dos pilotos |
| Recebe | acionamento |
| Entrega | eventos |
| Usa | `NE3-069` eldorado/motores/pilotos/espiao.py, `NE3-070` eldorado/motores/pilotos/interceptador.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | 1 dia sem voo com sucesso |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | voos com sucesso — limiares: ≥ 80% / 50 a 80% / < 50% |
| Indicador · linhas | 2 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | um voo de cada piloto |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 5 (🟢 5) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | alarme se um piloto passar 1 dia sem sucesso |

#### `NE3-088` · `.github/workflows/painel.yml`

**Finalidade:** Publicação do painel, das visões e da sala.

**Atende à finalidade da titular:** painel atualizado.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | publicar |
| Recebe | — |
| Entrega | páginas |
| Usa | `NE3-039` eldorado/base/painel/visoes.py |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | publicação falhou |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | publicações no prazo — limiares: no prazo / atraso / falha |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | o painel publicado |
| Existe hoje no Eldorado0 | nada: arquivo novo · itens atuais herdados: 16 (🟢 16) |
| Ferramentas novas | — |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-089` · `.github/workflows/qualidade.yml`

**Finalidade:** A bateria de testes a cada mudança e o teste de contrato.

**Atende à finalidade da titular:** nada entra sem teste.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | bateria a cada mudança |
| Recebe | mudanças |
| Entrega | resultado |
| Usa | `NE3-085` eldorado/testes/ |
| É usado por | — |
| Eventos que emite | — |
| Eventos que consome | — |
| Tabelas que lê | — |
| Dados | — |
| Configuração | — |
| Alarmes | mudança sem bateria |
| Indicador · ponto | rodou sem erro quando chamado (recibo do executor) |
| Indicador · círculo | mudanças aprovadas — limiares: aprovadas / — / reprovada |
| Indicador · linhas | 1 ligações declaradas, confirmadas pelas chamadas reais |
| Teste de aceite | uma mudança quebrada é barrada |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Ferramentas novas | astral-sh/ruff, astral-sh/uv |
| Dados herdados | — |
| Cuidados | — |

## 8. Os contratos de integração com as partes modulares

### 8.1 Com os motores (esquema próprio a seguir)

A base enxerga cada motor e cada piloto **só pelo contrato**: `descrever`, `planejar(janela, alvos)`, `buscar(contexto)`, `aprender(retorno)`, `painel`, `saude`. O motor recebe da base apenas o plano (janela, alvos, limites do governador) e o retorno da Pertinência; entrega apenas eventos (`motor.execucao`, `achado.entregue`). Os motores podem usar da base só: os contratos, os eventos, o serviço de IA e o governador.

- `NE3-043` `eldorado/motores/acesso/escada.py` — A escada de acesso: tenta do degrau mais leve ao mais forte, aprende por domínio qual degrau funciona, limita por domínio e repete com esper
- `NE3-044` `eldorado/motores/acesso/api.py` — Degrau 1: APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN).
- `NE3-045` `eldorado/motores/acesso/leve.py` — Degrau 2: requisição leve com assinatura de navegador real.
- `NE3-046` `eldorado/motores/acesso/navegador.py` — Degraus 3 a 5: navegador leve (Lightpanda, a testar), navegador não detectável (Patchright) e anti-detecção (Camoufox), só sob demanda.
- `NE3-047` `eldorado/motores/acesso/arquivo_web.py` — Degrau 6: a cópia arquivada (Wayback Machine e Common Crawl) quando o site está fora do ar ou bloqueou.
- `NE3-048` `eldorado/motores/acesso/rotas_alternativas.py` — Degraus 7 e 8: rota pelo Tor e leitor público de páginas, como reservas.
- `NE3-049` `eldorado/motores/acesso/local.py` — Degrau 9: o computador da titular (IP brasileiro, navegador local, Claude no Chrome) quando o próprio site bloqueia o acesso remoto.
- `NE3-050` `eldorado/motores/leitura/leitores.py` — O registro dos leitores: escolhe o leitor pelo tipo de conteúdo; um leitor novo entra pelo manifesto, sem mudar o resto.
- `NE3-051` `eldorado/motores/leitura/pagina.py` — Páginas: estrutura e links, texto limpo, texto principal (pontual), dados embutidos (JSON-LD, objetos JavaScript), sistemas de site (WordPre
- `NE3-052` `eldorado/motores/leitura/pdf.py` — PDF digital: texto por página com posição (para o trecho e a página), tabelas; classifica digital ou digitalizado para decidir o OCR.
- `NE3-053` `eldorado/motores/leitura/ocr.py` — Imagens e PDF digitalizado.
- `NE3-054` `eldorado/motores/leitura/planilha.py` — Planilhas XLSX, XLS, XLSB, ODS e CSV.
- `NE3-055` `eldorado/motores/leitura/documento.py` — Documentos DOCX, ODT, PPTX.
- `NE3-056` `eldorado/motores/leitura/compactado.py` — Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo ao leitor do seu tipo.
- `NE3-057` `eldorado/motores/leitura/universal.py` — O leitor universal de reserva (mais de mil formatos) e a transcrição de áudio e vídeo publicados, sob demanda.
- `NE3-058` `eldorado/motores/leitura/expurgo.py` — O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição); nada de recorte nem resumo.
- `NE3-059` `eldorado/motores/leitura/normalizar.py` — Datas, valores, CNPJ e outros documentos, idioma e codificação.
- `NE3-060` `eldorado/motores/descoberta/metabusca.py` — Forma 1: metabusca própria (SearXNG) → biblioteca de metabusca (ddgs) → buscador independente (Marginalia).
- `NE3-061` `eldorado/motores/descoberta/dados_abertos.py` — Forma 2: APIs oficiais → portais CKAN → Brasil.io.
- `NE3-062` `eldorado/motores/descoberta/estrutura_site.py` — Forma 3: mapa do site → feeds RSS e Atom e API do WordPress → navegação pelos links.
- `NE3-063` `eldorado/motores/descoberta/arquivos_web.py` — Forma 4: índices da Wayback Machine e do Common Crawl.
- `NE3-064` `eldorado/motores/descoberta/vigilancia.py` — Forma 5: detecção de mudança nas páginas conhecidas (assinatura do trecho que importa) e vigilância na janela prevista.
- `NE3-065` `eldorado/motores/canal/motor.py` — O motor genérico de canal: lê a configuração, planeja, usa acesso, leitura e descoberta, entrega achados compactos, aprende e mantém o paine
- `NE3-066` `eldorado/motores/canal/achado.py` — O formato único do achado: os dados necessários da oportunidade, o link de divulgação, o link oficial, o texto literal comprimido, a assinat
- `NE3-067` `eldorado/motores/canal/estado.py` — Os dados de uso próprio de cada motor (cursor, assinaturas, rotas, cadência, léxico, alternativas de acesso, histórico do aprendizado); nenh
- `NE3-068` `eldorado/motores/canal/config/` — As 45 configurações de canal (uma por motor) e os seus 114 alvos, preenchidas a partir do dossiê dos motores.
- `NE3-069` `eldorado/motores/pilotos/espiao.py` — Piloto A, o Espião: motor livre de descoberta, com IA; escolhe as famílias de busca pelo aprendizado (4 em 5) e explora (1 em 5).
- `NE3-070` `eldorado/motores/pilotos/interceptador.py` — Piloto B, o Interceptador: IA que pesquisa e comprova os itens que faltam, um livro por voo, gravando pelo contrato da Biblioteca.
- `NE3-071` `eldorado/motores/skills/` — As skills dos motores e pilotos, no formato aberto (SKILL.md com metadados de uso e resultado), promovidas ou arquivadas pelo Cérebro.

### 8.2 Com o banco (esquema próprio a seguir)

A base lê o banco **pelas visões e pela interface do livro**, e escreve **só por eventos**, aplicados pelo gravador. O banco não depende de nenhuma outra parte. As tabelas que este esquema exige do banco são:

- **cerebro:** `acionamento`, `agenda`, `alarme`, `aprendizado_*`, `aprendizado_permanente`, `aprendizado_temporario`, `cobertura_dia`, `decisao_pertinencia`, `dominio`, `execucao`, `execucao_motor`, `execucao_passo`, `maquina`, `medicao`, `modelo`, `modulo`, `plano`, `recibo`, `regra`, `rotulo`, `workflow`
- **biblioteca:** `achado`, `busca`, `calendario`, `certidao`, `documento`, `item`, `lei`, `livro`, `pagina`, `passagem`, `passaporte`, `previsao`, `relatorio_etapa`, `tentativa`, `transferencia`, `uniao`, `veredito`
- **especial:** `empresa`, `incentivo`, `ranking`, `oportunidade_empresa`, `vinculo_livro`

- `NE3-072` `eldorado/banco/biblioteca/esquema.py` — O esquema relacional da Biblioteca, as regras do banco (nada se apaga nem se sobrescreve), a busca de texto (FTS5) e as versões do esquema.
- `NE3-073` `eldorado/banco/biblioteca/livro.py` — A interface do livro (contrato da Biblioteca): ler, acrescentar, registrar relatório; nunca apagar nem sobrescrever.
- `NE3-074` `eldorado/banco/biblioteca/texto.py` — O texto literal de cada página, comprimido com zstd e dicionário treinado; índice de busca.
- `NE3-078` `eldorado/banco/biblioteca/leis.py` — Os livros de leis e o regramento de cada fonte.
- `NE3-079` `eldorado/banco/especial/esquema.py` — O banco Especial: empresas, incentivos, rankings e o vínculo com os livros e com os pilotos (o Espião encontra, o Interceptador aprofunda).
- `NE3-080` `eldorado/banco/especial/empresas.py` — A interface das empresas: fichas, incentivos comprovados, potencial, oportunidades nas empresas conhecidas.
- `NE3-081` `eldorado/banco/cerebro_db/esquema.py` — O banco do Cérebro: sem nenhuma oportunidade; medições, plano, decisões, modelo, regras, aprendizado temporário (30 dias) e permanente, alar
- `NE3-082` `eldorado/banco/originais/drive.py` — Envia os originais (PDF, imagens, planilhas) ao Drive e guarda só o endereço e a assinatura; o sistema nunca guarda binário.
- `NE3-083` `eldorado/banco/fotografia.py` — As fotografias comprimidas dos três bancos, fora do Git, e a reconstrução a partir dos eventos.

## 9. O monitoramento em quatro níveis

| Nível | Quem calcula | Como | Onde aparece |
| --- | --- | --- | --- |
| **Arquivo** | `eldorado/base/cerebro/medicao.py` | ponto pelo recibo de cada chamada; círculo pela métrica e pelos limiares da ficha; linhas pelas chamadas reais contra as declaradas | a estrela do arquivo na Sala |
| **Componente** | o mesmo | vermelho se um arquivo crítico está vermelho; amarelo se 20% ou mais estão sem medição; verde nos demais casos; o círculo é a métrica de saída do componente | o grupo na Sala |
| **Parte** (base, motores, banco) | o mesmo | a pior saúde entre os componentes críticos e a proporção de componentes verdes | o resumo das três partes na tela inicial |
| **Sistema** | o mesmo | as três partes, a cobertura do dia, os alarmes por gravidade e o governador de carga | o topo da tela inicial, junto do mostrador da máquina |

Cada nível é gravado na tabela `medicao` do Cérebro a cada passagem. Um arquivo sem medição na passagem acende o alarme.

## 10. A conferência

| Teste | Resultado |
| --- | --- |
| Todo arquivo da base tem esboço completo | aprovado (51 de 51) |
| Todo evento consumido é emitido por alguém | aprovado (32 tipos de evento) |
| Toda ação e todo evento citam arquivos existentes | aprovado |
| Nenhuma dependência proibida entre as partes | aprovado, depois de remover a da vigilância |
| Nenhuma lógica no banco | aprovado, depois de mover a Análise para a base |
| As tabelas exigidas do banco estão listadas | aprovado (o contrato da seção 8.2) |

## 11. Parecer do conselho

**1. Extremamente pessimista — Dra. Ingrid Valdés, chief engineer.** “Trinta e dois tipos de evento são o sistema nervoso do Eldorado. Um evento mal definido corrompe três bancos de uma vez. O catálogo precisa de versão e de teste para cada tipo.”

**2. Pessimista — Prof. Kenji Morimoto.** “O executor durável e o gravador são pontos únicos. Se um deles parar, tudo para. Eles precisam ser os primeiros a nascer e os mais testados.”

**3. Levemente pessimista — Eng. Rafaela Duarte.** “Limiares escritos antes de medir são palpites. Eles devem começar como estão aqui e ser recalibrados pela medição real nas primeiras semanas.”

**5. Levemente otimista — Eng. Mei Tanaka.** “Cada arquivo nasce com o seu teste de aceite e o seu indicador. Isso é o oposto do Eldorado0, em que a medição veio depois.”

**6. Otimista — Prof. Diego Albuquerque.** “A base enxerga motores e banco só por contratos. É o que permite trocar uma peça específica quando quebrar, como a titular pediu.”

**7. Extremamente otimista — Dra. Lucía Ferraz.** “Com a missão em quatro arquivos e o resto genérico, a mesma base serve a contas públicas ou a qualquer acompanhamento diário de dados.”

**Síntese do neutro — Dr. Antônio Brandt.** O esquema base está aprovado como mapa de criação, com cinco parâmetros: (1) **ordem de criação**: contratos → eventos → gravador → executor → alarmes → medição, cada um com o seu teste, antes de qualquer etapa; (2) **catálogo de eventos versionado**, com um teste por tipo; (3) **limiares recalibrados** pela medição real nas primeiras semanas; (4) **nenhum arquivo entra sem o seu teste de aceite e o seu indicador ligados**; (5) os esquemas dos motores e do banco devem **cumprir exatamente os contratos da seção 8**.
