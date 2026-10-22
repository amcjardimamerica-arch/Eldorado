# 01 — Os motores do novo Eldorado (o esquema completo, motor por motor)

**Versão final, revisada antes da criação (22/10/2026).** O esquema da parte modular dos motores, com as versões fixadas das ferramentas, o modelo de configuração de um motor e o manifesto de uma skill, para a criação começar. Cumpre os contratos do documento 02 (o sistema) e escreve no banco só por eventos (documento 03). Nada foi criado no repositório novo.

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

## A. As ferramentas dos motores, com as versões fixadas

| Ferramenta (GitHub) | Pacote | Versão fixada | Publicada em | Licença | Usada em |
| --- | --- | --- | --- | --- | --- |
| [mjpieters/aiolimiter](https://github.com/mjpieters/aiolimiter) | `aiolimiter` | **1.3.0** | 2026-09-07 | MIT | `motores/acesso/escada.py` |
| [daijro/camoufox](https://github.com/daijro/camoufox) | `camoufox` | **0.5.8** | 2026-10-06 | MIT | `motores/acesso/navegador.py` |
| [commoncrawl/cdx_toolkit](https://github.com/commoncrawl/cdx_toolkit) | `cdx_toolkit` | **0.9.39** | 2026-06-01 | Apache 2.0 | `motores/acesso/arquivo_web.py`, `motores/descoberta/arquivos_web.py` |
| [jawah/charset_normalizer](https://github.com/jawah/charset_normalizer) | `charset-normalizer` | **3.5.2** | 2026-09-30 | MIT | `motores/leitura/leitores.py` |
| [Nykakin/chompjs](https://github.com/Nykakin/chompjs) | `chompjs` | **1.4.1** | 2026-05-17 | MIT License | `motores/leitura/pagina.py` |
| [ckan/ckanapi](https://github.com/ckan/ckanapi) | `ckanapi` | **4.11** | 2026-03-20 | MIT | `motores/descoberta/dados_abertos.py` |
| [lexiforest/curl_cffi](https://github.com/lexiforest/curl_cffi) | `curl_cffi` | **0.16.3** | 2026-09-02 | MIT | `motores/acesso/leve.py` |
| [akoumjian/datefinder](https://github.com/akoumjian/datefinder) | `datefinder` | **1.0.0** | 2026-03-25 | MIT | `motores/leitura/normalizar.py` |
| [scrapinghub/dateparser](https://github.com/scrapinghub/dateparser) | `dateparser` | **1.4.3** | 2026-09-03 | BSD-3-Clause | `motores/leitura/normalizar.py` |
| [deedy5/ddgs](https://github.com/deedy5/ddgs) | `ddgs` | **9.16.0** | 2026-08-26 | MIT | `motores/descoberta/metabusca.py` |
| [ShayHill/docx2python](https://github.com/ShayHill/docx2python) | `docx2python` | **3.7.1** | 2026-08-06 | MIT | `motores/leitura/documento.py` |
| [scrapinghub/extruct](https://github.com/scrapinghub/extruct) | `extruct` | **0.18.0** | 2024-11-08 | BSD License | `motores/leitura/pagina.py` |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | `faster-whisper` | **1.2.1** | 2025-10-31 | MIT | `motores/leitura/universal.py` |
| [kurtmckee/feedparser](https://github.com/kurtmckee/feedparser) | `feedparser` | **6.0.14** | 2026-07-30 | BSD-2-Clause | `motores/descoberta/estrutura_site.py` |
| [encode/httpx](https://github.com/encode/httpx) | `httpx` | **0.28.1** | 2024-12-06 | BSD-3-Clause | `motores/acesso/api.py` |
| [jmespath/jmespath.py](https://github.com/jmespath/jmespath.py) | `jmespath` | **1.1.0** | 2026-01-22 | MIT | `motores/acesso/api.py` |
| [lightpanda-io/browser](https://github.com/lightpanda-io/browser) | `lightpanda (binário)` | **1.0.0** (a mais recente é 1.0.1) | 2026-10-02 | AGPL-3.0 | `motores/acesso/navegador.py` |
| [pemistahl/lingua-py](https://github.com/pemistahl/lingua-py) | `lingua-language-detector` | **2.2.0** | 2026-03-09 | Apache Software License | `motores/leitura/normalizar.py` |
| [run-llama/liteparse](https://github.com/run-llama/liteparse) | `liteparse` | **2.15.1** (a mais recente é 2.16.0) | 2026-10-01 | Apache-2.0 | `motores/leitura/pdf.py` |
| [lxml/lxml](https://github.com/lxml/lxml) | `lxml` | **6.1.3** | 2026-09-02 | BSD-3-Clause | `motores/leitura/pagina.py` |
| [eea/odfpy](https://github.com/eea/odfpy) | `odfpy` | **1.4.1** | 2020-01-18 | Apache Software License | `motores/leitura/documento.py` |
| [Kaliiiiiiiiii-Vinyzu/patchright-python](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python) | `patchright` | **1.63.0** (a mais recente é 1.64.1) | 2026-09-20 | Apache-2.0 | `motores/acesso/navegador.py` |
| [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector) | `pdf-inspector` | **1.25.2** | 2026-09-28 | MIT | `motores/leitura/pdf.py` |
| [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | `playwright` | **1.63.0** (a mais recente é 1.64.0) | 2026-09-15 | Apache-2.0 | `motores/acesso/navegador.py` |
| [pola-rs/polars](https://github.com/pola-rs/polars) | `polars` | **2.0.0** | 2026-10-06 | Copyright (c) 2025 Ritchie Vin | `motores/leitura/planilha.py` |
| [scrapinghub/price-parser](https://github.com/scrapinghub/price-parser) | `price-parser` | **0.5.1** | 2026-03-19 | BSD-3-Clause | `motores/leitura/normalizar.py` |
| [deedy5/primp](https://github.com/deedy5/primp) | `primp` | **2.0.1** | 2026-09-13 | MIT License | `motores/acesso/leve.py` |
| [scrapy/protego](https://github.com/scrapy/protego) | `protego` | **0.7.0** | 2026-09-21 | BSD-3-Clause | `motores/acesso/escada.py` |
| [miurahr/py7zr](https://github.com/miurahr/py7zr) | `py7zr` | **1.1.3** (a mais recente é 1.1.4) | 2026-06-19 | LGPL-2.1-or-later | `motores/leitura/compactado.py` |
| [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF) | `pymupdf` | **1.28.2** (a mais recente é 2.0) | 2026-08-06 | Dual Licensed - GNU AFFERO GPL | `motores/leitura/pdf.py` |
| [pypdfium2-team/pypdfium2](https://github.com/pypdfium2-team/pypdfium2) | `pypdfium2` | **5.14.0** | 2026-10-04 | BSD-3-Clause, Apache-2.0, depe | `motores/leitura/pdf.py` |
| [dimastbk/python-calamine](https://github.com/dimastbk/python-calamine) | `python-calamine` | **0.8.2** (a mais recente é 0.9.0) | 2026-07-13 | MIT | `motores/leitura/planilha.py` |
| [python-openxml/python-docx](https://github.com/python-openxml/python-docx) | `python-docx` | **1.2.0** | 2025-06-16 | MIT | `motores/leitura/documento.py` |
| [scanny/python-pptx](https://github.com/scanny/python-pptx) | `python-pptx` | **1.0.2** | 2024-08-07 | MIT | `motores/leitura/documento.py` |
| [RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR) | `rapidocr` | **3.9.2** (a mais recente é 3.10.0) | 2026-07-21 | Apache-2.0 | `motores/leitura/ocr.py` |
| [markokr/rarfile](https://github.com/markokr/rarfile) | `rarfile` | **4.5** | 2026-08-02 | ISC | `motores/leitura/compactado.py` |
| [chatnoir-eu/chatnoir-resiliparse](https://github.com/chatnoir-eu/chatnoir-resiliparse) | `resiliparse` | **1.0.9** | 2026-07-20 | Apache-2.0 | `motores/leitura/pagina.py` |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | `scrapling` | **0.4.15** (a mais recente é 0.5) | 2026-08-23 | BSD 3-Clause License | `motores/leitura/pagina.py` |
| [rushter/selectolax](https://github.com/rushter/selectolax) | `selectolax` | **1.0.0** (a mais recente é 1.0.2) | 2026-10-03 | MIT | `motores/leitura/pagina.py` |
| [torproject/stem](https://github.com/torproject/stem) | `stem` | **1.8.2** | 2023-06-06 | LGPLv3 | `motores/acesso/rotas_alternativas.py` |
| [jd/tenacity](https://github.com/jd/tenacity) | `tenacity` | **9.2.1** | 2026-10-07 | Apache-2.0 | `motores/acesso/escada.py` |
| [sirfz/tesserocr](https://github.com/sirfz/tesserocr) | `tesserocr` | **2.11.0** | 2026-08-04 | MIT | `motores/leitura/ocr.py` |
| [chrismattmann/tika-python](https://github.com/chrismattmann/tika-python) | `tika` | **3.3.2** | 2026-08-01 | Apache-2.0 | `motores/leitura/universal.py` |
| [adbar/trafilatura](https://github.com/adbar/trafilatura) | `trafilatura` | **2.3.1** | 2026-10-06 | Apache-2.0 | `motores/leitura/pagina.py` |
| [GateNLP/ultimate-sitemap-parser](https://github.com/GateNLP/ultimate-sitemap-parser) | `ultimate-sitemap-parser` | **1.8.1** | 2026-06-16 | GPL-3.0-or-later | `motores/descoberta/estrutura_site.py` |
| [alvarofpp/validate-docbr](https://github.com/alvarofpp/validate-docbr) | `validate-docbr` | **2.0.1** | 2026-10-01 | MIT | `motores/leitura/normalizar.py` |
| [akamhy/waybackpy](https://github.com/akamhy/waybackpy) | `waybackpy` | **3.0.6** | 2022-03-15 | MIT | `motores/acesso/arquivo_web.py` |
| [ShielderSec/webtech](https://github.com/ShielderSec/webtech) | `webtech` | **1.3.4** | 2023-10-12 | GPLv3 | `motores/leitura/pagina.py` |
| [martinblech/xmltodict](https://github.com/martinblech/xmltodict) | `xmltodict` | **1.0.4** | 2026-02-22 | MIT | `motores/acesso/api.py` |

## B. O modelo de configuração de um motor (criar um motor = escrever este arquivo)

```toml
# eldorado/motores/canal/config/do-goias.toml
[motor]
id = "do-goias"
nome = "Diário Oficial do Estado de Goiás"
categoria = "Executivo"
finalidade = "encontrar oportunidade aberta para OSC em diário oficial estadual"
canal = "diario"                       # api · diario · paginas · portal (portal entrega pistas)

[agenda]
horarios = ["06:23", "12:53", "20:23"]
dias = ["seg", "ter", "qua", "qui", "sex", "sab"]
cadencia_dias = 1
motivo = "as edições saem de madrugada; depois vêm as extras e as edições da noite"

[[fonte]]
nome = "Diário do Estado — edições do dia"
url = "https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/"
tipo = "api"
exige_brasil = true

[acesso]
degraus = [1, 2, 4, 6, 9]              # api · leve · não detectável · cópia arquivada · computador local
limite_por_dominio = "1 requisição a cada 2 s"

[leitura]
leitores = ["pagina", "pdf", "ocr", "expurgo", "normalizar"]

[descoberta]
formas = ["dados_abertos", "vigilancia"]

[lexico]
termos = ["chamamento público", "edital", "termo de fomento", "organização da sociedade civil"]
vetos = ["extrato de contrato", "homologação", "resultado final"]

[alvos]
ids = ["f260-captacao-034", "f260-captacao-206"]   # vigiados só na janela prevista recebida no plano

[metas]
frescor = "dentro da cadência"
bloqueio_max = 0.10
barrados_max = 0.30
```

## C. O manifesto de uma skill

```yaml
# eldorado/motores/skills/classificador-atos-diario/SKILL.md (cabeçalho)
name: classificador-atos-diario
description: Classifica cada ato de um diário oficial (edital, extrato, homologação, decreto de emenda).
categoria: leitura
origem: aprendida            # base · aprendida · de perfil
criada_por: sistema          # sistema · titular
encaixe: pre-filtro          # antes do acesso · depois do acesso · descoberta · extração · pré-filtro · depois da entrega
usos: 0
resultado: null              # medido pelo Cérebro
estado: desligada            # entra desligada; ligada só depois de vencer a medição
licenca: MIT
relacionadas: [leitura-pdf, normalizar-datas]
```

---


**Versão de 22/10/2026.** Estudo teórico, antes de qualquer criação ou teste; nada foi criado no repositório novo. Este é o esquema da **parte modular dos motores**, no mesmo formato do esquema base, e cumpre os contratos definidos nele (seção 8.1 de `ESQUEMA-BASE-ELDORADO.md`). O banco de dados terá o seu esquema próprio.

## 1. Como ler

A parte dos motores tem dois tipos de peça:

1. **As ferramentas compartilhadas** (29 arquivos, códigos `NE3-…`): a escada de acesso, os leitores, as formas de descoberta, o motor genérico de canal, os dois pilotos e as skills. Cada uma tem a ficha no mesmo padrão dos arquivos da base.
2. **Os 47 motores** (códigos `MT-…`): 45 motores de canal, cada um é **uma configuração** do motor genérico (um arquivo `.toml`, sem código próprio); e os 2 pilotos, que são motores livres com IA.

Cada motor tem: a finalidade e a finalidade da titular que ele atende; o canal; as fontes; a agenda atual; as ferramentas que usa (os degraus de acesso, os leitores e as formas de descoberta, deduzidos do canal e do aprendizado); a herança (os motores agregados e os alvos vigiados); o aprendizado herdado e o **histórico de erros de 01/10 a 22/10**; o indicador com os limiares (verde / amarelo / vermelho); o teste de aceite; e os cuidados.

## 2. O inventário

De **203 motores** no Eldorado0 (45 na Bússola e 158 ocultos) para **47**: 42 mantidos pela titular, 1 pedido por ela (Outros agregadores) e 4 sugestões (Diários municipais de Goiás, Bancos públicos e Sistema S, Fundações e institutos, Organismos internacionais). Os demais foram agregados a um destes motores, viraram **alvos** vigiados dentro deles (114 pontos de captação) ou, em 3 casos, foram eliminados.

| Categoria | Motores |
| --- | --- |
| Executivo — diários e portais do governo | 14 |
| Judiciário e Ministérios Públicos | 6 |
| Legislativo | 3 |
| Portais e fontes do terceiro setor | 22 |
| Pilotos — motores livres com IA | 2 |

## 3. A arquitetura de todo motor

Todo motor segue as mesmas 10 camadas: **plano** (a janela e os alvos recebidos da Regência) → **acesso** (a escada de 9 degraus) → **descoberta** (5 formas, com reservas) → **mudança** (só segue se a página mudou) → **leitura** (o leitor do tipo de conteúdo; o PDF e a imagem são decupados no próprio motor) → **pré-filtro** (o léxico próprio) → **normalização** → **deduplicação** → **entrega** (o achado compacto, com os dois links, o texto literal comprimido e a prova; o original vai ao Drive) → **aprendizado e painel** (o retorno da Pertinência).

**Regras:** o motor não guarda oportunidade (só os seus dados de uso próprio); não decide pertinência (o portão é da base); não lê caminho de arquivo da base (só pelo contrato); só escreve por eventos (`motor.execucao`, `achado.entregue`); e respeita o governador de carga antes dos degraus pesados.

## 4. Os motores por categoria

### Executivo — diários e portais do governo

- `MT-01` **Diário Oficial do Município de Goiânia** (`do-goiania`, mantido, na Bússola) — 0 agregados · 2 alvos
- `MT-02` **Diário Oficial do Estado de Goiás** (`do-goias`, mantido, na Bússola) — 0 agregados · 2 alvos
- `MT-03` **Diário Oficial da União** (`dou`, mantido, na Bússola) — 0 agregados · 2 alvos
- `MT-04` **Prefeituras das 25 maiores cidades de Goiás — portais de editais** (`prefeituras-50-go`, mantido, na Bússola) — 1 agregados · 4 alvos
- `MT-05` **Oportunidade Estaduais Governamentais de Goiás** (`estaduais-go-gov`, mantido, na Bússola) — 7 agregados · 10 alvos
- `MT-06` **PNCP — API de contratações (chamamentos e credenciamentos)** (`pncp-api`, mantido, na Bússola) — 0 agregados · 17 alvos
- `MT-07` **Lei Rouanet — janela de propostas no SALIC e projetos de Goiás (Ministério da Cultura)** (`salic`, mantido, na Bússola) — 2 agregados · 1 alvos
- `MT-08` **Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás)** (`motor-gife`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-09` **Busca de empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas, Pronon e Goyazes** (`empresas-editais-incentivados`, mantido, na Bússola) — 2 agregados · 5 alvos
- `MT-10` **CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC** (`cnpq-extensao`, mantido, na Bússola) — 2 agregados · 0 alvos
- `MT-11` **Funarte — editais da Fundação Nacional de Artes** (`site-funarte`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-12` **Transferegov — programas e parcerias com OSC abertos na plataforma federal (dados abertos)** (`site-transferegov`, mantido, na Bússola) — 0 agregados · 4 alvos
- `MT-13` **Diários oficiais municipais de Goiás (Querido Diário)** (`novo-diarios-municipais-go`, sugestão) — 0 agregados · 1 alvos
- `MT-14` **Bancos públicos e Sistema S (BNDES, BNB, Caixa, Sebrae)** (`novo-bancos-publicos`, sugestão) — 1 agregados · 5 alvos

### Judiciário e Ministérios Públicos

- `MT-15` **TJ-GO — editais das comarcas (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO** (`judiciario-tjgo`, mantido, na Bússola) — 2 agregados · 1 alvos
- `MT-16` **Diário da Justiça Federal — Seção Judiciária de Goiás** (`dj-trf1-go`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-17` **CNJ — destinação de prestações pecuniárias: busca no Portal do CNJ e regra nacional (Res. 558/2024)** (`judiciario-cnj`, mantido, na Bússola) — 1 agregados · 1 alvos
- `MT-18` **MP-GO — Programa Destina (cadastro de entidades para receber bens e valores de acordos)** (`mpgo-destinacao`, mantido, na Bússola) — 0 agregados · 1 alvos
- `MT-19` **MPT-GO — editais de 5 dias para indicação de destinação de recursos ou bens (PRT 18ª Região)** (`mptgo-destinacao`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-20` **MPU — MPF, MPDFT, MPM e MPT nacional: destinação de bens e valores (com CNMP e FDD)** (`mpu-destinacao`, mantido, na Bússola) — 1 agregados · 2 alvos

### Legislativo

- `MT-21` **Câmara Municipal de Goiânia — processos legislativos, utilidade pública e chamamentos** (`camara-goiania-pl`, mantido, na Bússola) — 0 agregados · 4 alvos
- `MT-22` **Assembleia Legislativa de Goiás — proposições** (`alego-pl`, mantido, na Bússola) — 0 agregados · 2 alvos
- `MT-23` **Congresso Nacional — Câmara, Senado e Comissão Mista de Orçamento (emendas, regras e chamamentos)** (`congresso-nacional`, mantido, na Bússola) — 0 agregados · 1 alvos

### Portais e fontes do terceiro setor

- `MT-24` **GIFE — Grupo de Institutos, Fundações e Empresas** (`gife`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-25` **Adaptador Mapas Culturais — oportunidades com inscrição aberta** (`plataforma-mapas-culturais`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-26` **Farol Cultural — editais de cultura de todo o Brasil, pela API pública do portal** (`site-farol-cultural`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-27` **CapitaAI — editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas** (`site-capitaai`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-28` **Observatório do Terceiro Setor — editais publicados na seção temática do portal** (`site-observatorio-terceiro-setor`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-29` **Mapas Culturais — editais das redes estaduais e municipais de cultura que usam a plataforma** (`site-mapas-culturais`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-30` **ABCR — Associação Brasileira de Captadores de Recursos — editais divulgados pela associação dos captadores** (`site-abcr`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-31` **Rede Comuá — editais dos fundos independentes de filantropia** (`site-rede-comua`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-32` **Fundo Baobá — editais para equidade racial** (`site-fundo-baoba`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-33` **IDIS — Instituto para o Desenvolvimento do Investimento Social — chamadas e editais de investimento social** (`site-idis`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-34` **Fundo Casa Socioambiental — chamadas socioambientais** (`site-fundo-casa`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-35` **CESE — Coordenadoria Ecumênica de Serviço — editais de apoio a projetos populares** (`site-cese`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-36` **Rede Filantropia — editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro)** (`site-rede-filantropia`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-37` **Editais Culturais — editais de cultura reunidos no portal** (`site-editais-culturais`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-38` **Mapa das OSC (Ipea) — editais reunidos no portal** (`site-mapa-osc`, mantido, na Bússola) — 1 agregados · 1 alvos
- `MT-39` **Prosas — editais e prêmios para OSCs (três caminhos indiretos: listagem da CapitaAI, ângulo do Piloto e coleta assistida)** (`site-prosas`, mantido, na Bússola) — 3 agregados · 0 alvos
- `MT-40` **Fundo Brasil de Direitos Humanos — editais de direitos humanos** (`site-fundo-brasil`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-41` **UNDEF — Fundo das Nações Unidas para a Democracia — chamadas anuais para a sociedade civil** (`site-undef`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-42` **BrazilFoundation — editais de apoio a organizações brasileiras** (`site-brazilfoundation`, mantido, na Bússola) — 0 agregados · 0 alvos
- `MT-43` **Outros agregadores e motores de busca** (`outros-agregadores`, novo (pedido)) — 9 agregados · 3 alvos
- `MT-44` **Fundações e institutos (sites próprios)** (`novo-fundacoes-institutos`, sugestão) — 2 agregados · 24 alvos
- `MT-45` **Organismos e fundações internacionais** (`novo-internacional`, sugestão) — 3 agregados · 21 alvos

### Pilotos — motores livres com IA

- `MT-46` **Piloto - Espião — busca aberta no terceiro setor** (`piloto-aberto`, mantido, na Bússola) — 1 agregados · 0 alvos
- `MT-47` **Piloto - Interceptador — comprova na fonte oficial** (`piloto-interceptador`, mantido, na Bússola) — 0 agregados · 0 alvos

## 5. As ferramentas compartilhadas, uma por uma


### Ferramentas de acesso (escada de 9 degraus)

#### `NE3-043` · `eldorado/motores/acesso/escada.py`

**Finalidade:** A escada de acesso: tenta do degrau mais leve ao mais forte, aprende por domínio qual degrau funciona, limita por domínio e repete com espera.

**Atende à finalidade da titular:** pelo menos 5 formas de acesso gratuitas; sem travas para robôs.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | escolher o degrau inicial pelo aprendizado do domínio; subir de degrau a cada falha; limitar requisições por domínio; repetir com espera crescente; registrar qual degrau funcionou; pedir permissão ao governador antes dos degraus pesados |
| Recebe | pedido de leitura |
| Entrega | conteúdo bruto |
| Usa | `NE3-044` eldorado/motores/acesso/api.py, `NE3-045` eldorado/motores/acesso/leve.py, `NE3-046` eldorado/motores/acesso/navegador.py, `NE3-047` eldorado/motores/acesso/arquivo_web.py, `NE3-049` eldorado/motores/acesso/local.py, `NE3-021` eldorado/base/cerebro/governador.py |
| É usado por (arquivos) | `NE3-027` eldorado/base/cartorio/site_oficial.py, `NE3-060` eldorado/motores/descoberta/metabusca.py, `NE3-062` eldorado/motores/descoberta/estrutura_site.py, `NE3-065` eldorado/motores/canal/motor.py, `NE3-070` eldorado/motores/pilotos/interceptador.py |
| Usada pelos motores | 47: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | `motor.execucao` |
| Eventos que consome | — |
| Configuração | ordem dos degraus, limite por domínio, tentativas |
| Alarmes | domínio bloqueado em todos os degraus |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | leituras com sucesso por domínio; degrau usado — limiares: ≥ 90% de sucesso / 70 a 90% / < 70% |
| Teste de aceite | um domínio que recusa o degrau 2 é lido no degrau 4 e, na próxima vez, começa no 4 |
| Ferramentas do GitHub | mjpieters/aiolimiter, jd/tenacity, scrapy/protego |
| Existe hoje no Eldorado0 | estado/bloqueios.json (217 domínios); estado/rotas/ponte_aprendida.json |
| Dados herdados | bloqueios por domínio, ponte aprendida |
| Cuidados | robots só como informação; bloqueio do site → computador da titular |

#### `NE3-044` · `eldorado/motores/acesso/api.py`

**Finalidade:** Degrau 1: APIs oficiais (DOU, PNCP, Querido Diário, Transferegov, Câmara, Senado, WordPress, CKAN).

**Atende à finalidade da titular:** API primeiro, onde houver.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | chamar APIs oficiais; ler JSON e XML; paginar; respeitar o limite da API |
| Recebe | pedido |
| Entrega | JSON |
| Usa | — |
| É usado por (arquivos) | `NE3-043` eldorado/motores/acesso/escada.py, `NE3-061` eldorado/motores/descoberta/dados_abertos.py |
| Usada pelos motores | 15: MT-01, MT-02, MT-03, MT-05, MT-06, MT-07, MT-10, MT-12, MT-13, MT-21, MT-22, MT-23, MT-25, MT-26, MT-29 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | endereços das APIs |
| Alarmes | API fora do ar |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | respostas válidas — limiares: respostas válidas ≥ 95% / 80 a 95% / < 80% |
| Teste de aceite | a API do PNCP devolve os chamamentos de um dia gravado |
| Ferramentas do GitHub | encode/httpx, msgspec/msgspec, martinblech/xmltodict, jmespath/jmespath.py |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-045` · `eldorado/motores/acesso/leve.py`

**Finalidade:** Degrau 2: requisição leve com assinatura de navegador real.

**Atende à finalidade da titular:** acesso leve e gratuito.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | requisição com assinatura de navegador real; certificados que os sites não enviam |
| Recebe | pedido |
| Entrega | HTML |
| Usa | — |
| É usado por (arquivos) | `NE3-043` eldorado/motores/acesso/escada.py |
| Usada pelos motores | 47: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | perfil de navegador |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | sucesso por domínio — limiares: ≥ 90% / 70 a 90% / < 70% |
| Teste de aceite | site que recusa o cliente comum abre com o degrau 2 |
| Ferramentas do GitHub | lexiforest/curl_cffi, deedy5/primp |
| Existe hoje no Eldorado0 | src/certificados.py (cadeias de certificado) |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-046` · `eldorado/motores/acesso/navegador.py`

**Finalidade:** Degraus 3 a 5: navegador leve (Lightpanda, a testar), navegador não detectável (Patchright) e anti-detecção (Camoufox), só sob demanda.

**Atende à finalidade da titular:** sem travas; páginas dinâmicas.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | navegador leve (Lightpanda, com a espera configurada obrigatória: seletor ou rede ociosa); navegador não detectável; navegador anti-detecção; fechar o navegador ao terminar |
| Recebe | pedido |
| Entrega | HTML renderizado |
| Usa | `NE3-021` eldorado/base/cerebro/governador.py |
| É usado por (arquivos) | `NE3-043` eldorado/motores/acesso/escada.py |
| Usada pelos motores | 43: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20, MT-21 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | limite de navegadores simultâneos |
| Alarmes | navegador preso |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | sucesso por degrau — limiares: ≥ 80% / 60 a 80% / < 60% |
| Teste de aceite | página que só abre com JavaScript é lida |
| Ferramentas do GitHub | microsoft/playwright-python, lightpanda-io/browser, Kaliiiiiiiiii-Vinyzu/patchright-python, daijro/camoufox |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | pesado: o governador limita |

#### `NE3-047` · `eldorado/motores/acesso/arquivo_web.py`

**Finalidade:** Degrau 6: a cópia arquivada (Wayback Machine e Common Crawl) quando o site está fora do ar ou bloqueou.

**Atende à finalidade da titular:** nenhuma informação pública omitida.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | buscar a última cópia na Wayback Machine; buscar no Common Crawl; marcar o achado como vindo de cópia |
| Recebe | endereço |
| Entrega | cópia arquivada |
| Usa | — |
| É usado por (arquivos) | `NE3-043` eldorado/motores/acesso/escada.py, `NE3-063` eldorado/motores/descoberta/arquivos_web.py |
| Usada pelos motores | 28: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-12, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20, MT-21, MT-22 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | cópias encontradas — limiares: cópias achadas quando pedidas ≥ 50% / 20 a 50% / < 20% |
| Teste de aceite | site fora do ar devolve a última cópia arquivada |
| Ferramentas do GitHub | akamhy/waybackpy, commoncrawl/cdx_toolkit |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | marcar no achado que veio de cópia |

#### `NE3-048` · `eldorado/motores/acesso/rotas_alternativas.py`

**Finalidade:** Degraus 7 e 8: rota pelo Tor e leitor público de páginas, como reservas.

**Atende à finalidade da titular:** formas de acesso de reserva (acionadas pela escada, nunca diretamente pelo motor).

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | rota pelo Tor; leitor público de páginas |
| Recebe | pedido |
| Entrega | conteúdo |
| Usa | — |
| É usado por (arquivos) | — |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | ligadas ou não |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | sucesso das reservas — limiares: usos com sucesso / — / falha total |
| Teste de aceite | a testar com os sites do governo antes de ligar |
| Ferramentas do GitHub | torproject/stem, jina-ai/reader |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | a testar com os sites do governo |

#### `NE3-049` · `eldorado/motores/acesso/local.py`

**Finalidade:** Degrau 9: o computador da titular (IP brasileiro, navegador local, Claude no Chrome) quando o próprio site bloqueia o acesso remoto.

**Atende à finalidade da titular:** quando o site bloqueia, coleta pelo computador da titular.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | enviar ao computador da titular o pedido bloqueado; receber o conteúdo; registrar que o domínio exige acesso local |
| Recebe | pedidos bloqueados |
| Entrega | conteúdo |
| Usa | — |
| É usado por (arquivos) | `NE3-043` eldorado/motores/acesso/escada.py |
| Usada pelos motores | 28: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-12, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20, MT-21, MT-22 … |
| Eventos que emite | `motor.execucao` |
| Eventos que consome | — |
| Configuração | endereço da ponte |
| Alarmes | ponte desligada com pedidos pendentes |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | pedidos resolvidos localmente — limiares: pedidos atendidos ≥ 90% / 50 a 90% / < 50% |
| Teste de aceite | um domínio que bloqueia o GitHub é lido pelo computador local |
| Ferramentas do GitHub | — |
| Existe hoje no Eldorado0 | src/ponte_brasil.py; src/navegador_local.py; scripts/pilotos_brasil.py (corrigir o endereço do repositório) |
| Dados herdados | domínios que exigem o Brasil |
| Cuidados | — |


### Ferramentas de leitura (canivete suíço)

#### `NE3-050` · `eldorado/motores/leitura/leitores.py`

**Finalidade:** O registro dos leitores: escolhe o leitor pelo tipo de conteúdo; um leitor novo entra pelo manifesto, sem mudar o resto.

**Atende à finalidade da titular:** canivete suíço extensível.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | identificar o tipo do conteúdo; escolher o leitor registrado para o tipo; encaminhar arquivos internos de compactados; registrar tipos sem leitor |
| Recebe | conteúdo bruto e tipo |
| Entrega | texto literal e dados estruturados |
| Usa | `NE3-051` eldorado/motores/leitura/pagina.py, `NE3-052` eldorado/motores/leitura/pdf.py, `NE3-053` eldorado/motores/leitura/ocr.py, `NE3-054` eldorado/motores/leitura/planilha.py, `NE3-055` eldorado/motores/leitura/documento.py, `NE3-056` eldorado/motores/leitura/compactado.py, `NE3-057` eldorado/motores/leitura/universal.py, `NE3-058` eldorado/motores/leitura/expurgo.py, `NE3-059` eldorado/motores/leitura/normalizar.py |
| É usado por (arquivos) | `NE3-056` eldorado/motores/leitura/compactado.py, `NE3-065` eldorado/motores/canal/motor.py, `NE3-070` eldorado/motores/pilotos/interceptador.py |
| Usada pelos motores | 47: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | leitores ligados por tipo |
| Alarmes | tipo sem leitor |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | conteúdos lidos por tipo; tipos sem leitor — limiares: 0 tipos sem leitor / 1 / mais |
| Teste de aceite | um leitor novo registrado é usado sem mudar nenhum outro arquivo |
| Ferramentas do GitHub | jawah/charset_normalizer |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | o motor decupa; o sistema nunca recebe binário |

#### `NE3-051` · `eldorado/motores/leitura/pagina.py`

**Finalidade:** Páginas: estrutura e links, texto limpo, texto principal (pontual), dados embutidos (JSON-LD, objetos JavaScript), sistemas de site (WordPress, Joomla, Drupal).

**Atende à finalidade da titular:** leitura de páginas, WordPress e código-fonte.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | estrutura e links; texto limpo; texto principal (pontual); dados embutidos (JSON-LD e objetos JavaScript); detectar o sistema do site e usar a sua API |
| Recebe | HTML |
| Entrega | texto, links e dados |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 47: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | seletores do canal (na configuração do motor) |
| Alarmes | página lida sem texto |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | páginas lidas; links por página — limiares: páginas com texto ≥ 95% / 80 a 95% / < 80% |
| Teste de aceite | uma página real do MPT-18 gera os links e o texto esperados |
| Ferramentas do GitHub | rushter/selectolax, lxml/lxml, chatnoir-eu/chatnoir-resiliparse, adbar/trafilatura, scrapinghub/extruct, Nykakin/chompjs, D4Vinci/Scrapling, ShielderSec/webtech |
| Existe hoje no Eldorado0 | src/atos_diario.py (classificador de atos dos diários) |
| Dados herdados | classificador de atos; léxico dos motores |
| Cuidados | selectolax 183 MB/s, resiliparse 166 MB/s (medidos) |

#### `NE3-052` · `eldorado/motores/leitura/pdf.py`

**Finalidade:** PDF digital: texto por página com posição (para o trecho e a página), tabelas; classifica digital ou digitalizado para decidir o OCR.

**Atende à finalidade da titular:** até 10 mil páginas de PDF, sem guardar o PDF.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | texto por página com posição; tabelas; classificar digital ou digitalizado; encaminhar ao OCR quando necessário |
| Recebe | PDF |
| Entrega | texto literal por página |
| Usa | `NE3-053` eldorado/motores/leitura/ocr.py, `NE3-058` eldorado/motores/leitura/expurgo.py |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 23: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | páginas máximas por documento |
| Alarmes | PDF sem texto e sem OCR |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | páginas por segundo; páginas sem texto — limiares: ≥ 200 páginas/s por processador / 100 a 200 / < 100 |
| Teste de aceite | os 23 PDFs reais do Eldorado0 com todas as palavras-chave preservadas |
| Ferramentas do GitHub | pymupdf/PyMuPDF, pypdfium2-team/pypdfium2, run-llama/liteparse, firecrawl/pdf-inspector |
| Existe hoje no Eldorado0 | src/skills/leitura_pdf.py (lições) |
| Dados herdados | — |
| Cuidados | PyMuPDF 278 páginas/s (medido); 10 mil páginas em 0,6 min |

#### `NE3-053` · `eldorado/motores/leitura/ocr.py`

**Finalidade:** Imagens e PDF digitalizado.

**Atende à finalidade da titular:** leitura de imagens.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | OCR leve; OCR de reserva; confiança por página |
| Recebe | imagem |
| Entrega | texto |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py, `NE3-052` eldorado/motores/leitura/pdf.py |
| Usada pelos motores | 23: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | idioma português |
| Alarmes | confiança baixa |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | páginas com OCR; confiança média — limiares: confiança média ≥ 85% / 70 a 85% / < 70% |
| Teste de aceite | um edital digitalizado vira texto legível |
| Ferramentas do GitHub | RapidAI/RapidOCR, tesseract-ocr/tesseract, sirfz/tesserocr |
| Existe hoje no Eldorado0 | src/skills/leitura_imagens.py |
| Dados herdados | — |
| Cuidados | só quando o PDF é digitalizado |

#### `NE3-054` · `eldorado/motores/leitura/planilha.py`

**Finalidade:** Planilhas XLSX, XLS, XLSB, ODS e CSV.

**Atende à finalidade da titular:** leitura de planilhas.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | ler XLSX, XLS, XLSB, ODS e CSV; entregar tabelas |
| Recebe | planilha |
| Entrega | tabelas |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 4: MT-07, MT-08, MT-09, MT-12 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | planilhas lidas — limiares: lidas / — / falha |
| Teste de aceite | planilha de 20 mil linhas em menos de 1 s |
| Ferramentas do GitHub | dimastbk/python-calamine, tafia/calamine, pola-rs/polars |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | calamine 13× mais rápido (medido) |

#### `NE3-055` · `eldorado/motores/leitura/documento.py`

**Finalidade:** Documentos DOCX, ODT, PPTX.

**Atende à finalidade da titular:** leitura de documentos.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | DOCX com cabeçalhos e notas; ODT; PPTX |
| Recebe | documento |
| Entrega | texto |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 20: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | documentos lidos — limiares: lidos / — / falha |
| Teste de aceite | um termo de referência em DOCX lido por inteiro |
| Ferramentas do GitHub | ShayHill/docx2python, python-openxml/python-docx, eea/odfpy, scanny/python-pptx |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-056` · `eldorado/motores/leitura/compactado.py`

**Finalidade:** Arquivos ZIP, 7Z e RAR: abre e entrega cada arquivo ao leitor do seu tipo.

**Atende à finalidade da titular:** leitura de arquivos disponibilizados nos sites.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | abrir ZIP, 7Z e RAR; limitar tamanho e profundidade; entregar cada arquivo ao seu leitor |
| Recebe | arquivo compactado |
| Entrega | arquivos internos |
| Usa | `NE3-050` eldorado/motores/leitura/leitores.py |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 23: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | tamanho máximo |
| Alarmes | arquivo acima do limite |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | arquivos abertos — limiares: abertos / — / falha |
| Teste de aceite | um ZIP de anexos de edital tem cada arquivo lido |
| Ferramentas do GitHub | miurahr/py7zr, markokr/rarfile |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | limite de tamanho e de profundidade |

#### `NE3-057` · `eldorado/motores/leitura/universal.py`

**Finalidade:** O leitor universal de reserva (mais de mil formatos) e a transcrição de áudio e vídeo publicados, sob demanda.

**Atende à finalidade da titular:** nenhum formato fica sem leitura (acionado pelo registro de leitores, nunca diretamente pelo motor).

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | leitor universal de reserva; transcrição de áudio e vídeo sob demanda |
| Recebe | formato sem leitor |
| Entrega | texto |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | ligado sob demanda |
| Alarmes | uso frequente (deveria ser raro) |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | usos da reserva (deve ser raro) — limiares: uso raro / — / uso frequente |
| Teste de aceite | um formato sem leitor é lido pela reserva |
| Ferramentas do GitHub | chrismattmann/tika-python, apache/tika, SYSTRAN/faster-whisper |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | pesado: só sob demanda |

#### `NE3-058` · `eldorado/motores/leitura/expurgo.py`

**Finalidade:** O expurgo seguro: tira só o que se repete na faixa do cabeçalho e do rodapé (pela posição); nada de recorte nem resumo.

**Atende à finalidade da titular:** texto literal completo, expurgando o desnecessário.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | achar o que se repete na faixa do cabeçalho e do rodapé; remover só isso; conferir que valores, datas, CNPJ e palavras-chave ficaram |
| Recebe | texto por página com posição |
| Entrega | texto literal completo |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py, `NE3-052` eldorado/motores/leitura/pdf.py |
| Usada pelos motores | 23: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | faixa (9% do topo e da base), repetição mínima (60% das páginas) |
| Alarmes | perda de valor ou palavra-chave |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | palavras-chave e valores preservados (teste obrigatório) — limiares: 0 perdas / — / qualquer perda |
| Teste de aceite | os editais reais: 3,2% removido, nenhum valor perdido |
| Ferramentas do GitHub | — |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | teste nos editais reais: 3,2% removido, nenhum valor perdido |
| Cuidados | o expurgo ingênuo apagava valores de tabela |

#### `NE3-059` · `eldorado/motores/leitura/normalizar.py`

**Finalidade:** Datas, valores, CNPJ e outros documentos, idioma e codificação.

**Atende à finalidade da titular:** dados prontos para o sistema.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | datas em português; valores e moeda; números por extenso (regra própria: o number-parser não aceita português); CNPJ e documentos; idioma; codificação |
| Recebe | texto |
| Entrega | campos normalizados |
| Usa | — |
| É usado por (arquivos) | `NE3-050` eldorado/motores/leitura/leitores.py |
| Usada pelos motores | 47: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-08, MT-09, MT-10, MT-11, MT-12, MT-13, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | campos normalizados por achado — limiares: campos válidos ≥ 95% / 80 a 95% / < 80% |
| Teste de aceite | “até 30 de outubro de 2026” vira 2026-10-30 |
| Ferramentas do GitHub | scrapinghub/dateparser, akoumjian/datefinder, scrapinghub/price-parser, alvarofpp/validate-docbr, pemistahl/lingua-py |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | — |


### Ferramentas de descoberta (5 formas)

#### `NE3-060` · `eldorado/motores/descoberta/metabusca.py`

**Finalidade:** Forma 1: metabusca própria (SearXNG) → biblioteca de metabusca (ddgs) → buscador independente (Marginalia).

**Atende à finalidade da titular:** descoberta sem custo, com rotas de reserva.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | consultar a metabusca própria; passar à reserva quando houver limite; descansar o buscador bloqueado |
| Recebe | consultas |
| Entrega | endereços candidatos |
| Usa | `NE3-043` eldorado/motores/acesso/escada.py |
| É usado por (arquivos) | `NE3-069` eldorado/motores/pilotos/espiao.py |
| Usada pelos motores | 3: MT-43, MT-44, MT-45 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | consultas da missão, descanso |
| Alarmes | todas as rotas esgotadas |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | consultas respondidas por rota — limiares: consultas respondidas ≥ 95% / 80 a 95% / < 80% |
| Teste de aceite | com a rota principal fora, a reserva responde |
| Ferramentas do GitHub | searxng/searxng, deedy5/ddgs, MarginaliaSearch/MarginaliaSearch |
| Existe hoje no Eldorado0 | biblioteca_alexandria/livros/especiais/espiao/vias.json (descanso dos buscadores) |
| Dados herdados | vias de busca e descanso após bloqueio |
| Cuidados | rota de reserva quando uma esgota o limite |

#### `NE3-061` · `eldorado/motores/descoberta/dados_abertos.py`

**Finalidade:** Forma 2: APIs oficiais → portais CKAN → Brasil.io.

**Atende à finalidade da titular:** 5 formas de descoberta.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | APIs oficiais; portais CKAN; Brasil.io |
| Recebe | consultas |
| Entrega | registros |
| Usa | `NE3-044` eldorado/motores/acesso/api.py |
| É usado por (arquivos) | — |
| Usada pelos motores | 15: MT-01, MT-02, MT-03, MT-05, MT-06, MT-07, MT-10, MT-12, MT-13, MT-21, MT-22, MT-23, MT-25, MT-26, MT-29 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | portais |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | registros novos por fonte — limiares: registros novos por janela / — / zero com fonte ativa |
| Teste de aceite | um portal CKAN devolve os conjuntos de um órgão |
| Ferramentas do GitHub | ckan/ckanapi, okfn-brasil/querido-diario |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-062` · `eldorado/motores/descoberta/estrutura_site.py`

**Finalidade:** Forma 3: mapa do site → feeds RSS e Atom e API do WordPress → navegação pelos links.

**Atende à finalidade da titular:** 5 formas de descoberta.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | mapa do site; feeds RSS e Atom; API do WordPress; navegação pelos links |
| Recebe | domínio |
| Entrega | endereços |
| Usa | `NE3-043` eldorado/motores/acesso/escada.py |
| É usado por (arquivos) | — |
| Usada pelos motores | 32: MT-04, MT-08, MT-09, MT-11, MT-14, MT-15, MT-16, MT-17, MT-18, MT-19, MT-20, MT-24, MT-27, MT-28, MT-30, MT-31, MT-32, MT-33, MT-34, MT-35 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | profundidade |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | endereços novos por domínio — limiares: endereços novos por domínio / — / zero com o site mudando |
| Teste de aceite | um site WordPress de secretaria lista as publicações pela API |
| Ferramentas do GitHub | GateNLP/ultimate-sitemap-parser, kurtmckee/feedparser |
| Existe hoje no Eldorado0 | abordagens 5 e 6 do Cartório (mídia do WordPress, mapa do site) |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-063` · `eldorado/motores/descoberta/arquivos_web.py`

**Finalidade:** Forma 4: índices da Wayback Machine e do Common Crawl.

**Atende à finalidade da titular:** 5 formas de descoberta.

| Campo | Esboço |
| --- | --- |
| Construção | **ADOTAR** — usa um projeto do GitHub como dependência, sem modificá-lo, dentro de um contrato do Eldorado |
| Funções principais | índice da Wayback; índice do Common Crawl |
| Recebe | domínio |
| Entrega | endereços históricos |
| Usa | `NE3-047` eldorado/motores/acesso/arquivo_web.py |
| É usado por (arquivos) | — |
| Usada pelos motores | 3: MT-43, MT-44, MT-45 |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | — |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | endereços históricos encontrados — limiares: endereços históricos achados / — / falha |
| Teste de aceite | um edital antigo é reencontrado pelo índice |
| Ferramentas do GitHub | commoncrawl/cdx_toolkit |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | — |

#### `NE3-064` · `eldorado/motores/descoberta/vigilancia.py`

**Finalidade:** Forma 5: detecção de mudança nas páginas conhecidas (assinatura do trecho que importa) e vigilância na janela prevista.

**Atende à finalidade da titular:** 5 formas de descoberta; ler só o que mudou.

| Campo | Esboço |
| --- | --- |
| Construção | **COPIAR_PARTE** — copia uma parte pequena de um projeto aberto (com a licença e a origem registradas no arquivo) |
| Funções principais | assinatura do trecho que importa; detectar mudança; vigiar só na janela recebida no plano |
| Recebe | páginas conhecidas e as janelas previstas, recebidas no plano da Regência (planejar) |
| Entrega | mudanças |
| Usa | — |
| É usado por (arquivos) | `NE3-065` eldorado/motores/canal/motor.py |
| Usada pelos motores | 22: MT-01, MT-02, MT-03, MT-04, MT-05, MT-06, MT-07, MT-09, MT-12, MT-13, MT-14, MT-15, MT-17, MT-18, MT-20, MT-21, MT-22, MT-23, MT-38, MT-43 … |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | filtro do trecho por página |
| Alarmes | página mudou sem achado |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | mudanças detectadas que viraram achado — limiares: mudanças que viraram achado ≥ 30% / 10 a 30% / < 10% |
| Teste de aceite | a mudança num edital vigiado gera achado; página sem mudança não gera leitura |
| Ferramentas do GitHub | dgtlmoon/changedetection.io (lógica de filtro e assinatura), adbar/htmldate |
| Existe hoje no Eldorado0 | nada: arquivo novo |
| Dados herdados | — |
| Cuidados | licença Apache registrada no arquivo |


### Motores de canal (45) e o seu motor genérico

#### `NE3-065` · `eldorado/motores/canal/motor.py`

**Finalidade:** O motor genérico de canal: lê a configuração, planeja, usa acesso, leitura e descoberta, entrega achados compactos, aprende e mantém o painel. Os 45 motores são configurações dele.

**Atende à finalidade da titular:** um motor, uma fonte, uma finalidade; motores autônomos.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | descrever; planejar (janela, alvos); buscar com acesso, leitura e descoberta; pré-filtrar pelo léxico próprio; deduplicar; entregar achados compactos; aprender com o retorno; manter o painel |
| Recebe | acionamento e alvos |
| Entrega | achados |
| Usa | `NE3-001` eldorado/base/nucleo/contratos.py, `NE3-043` eldorado/motores/acesso/escada.py, `NE3-050` eldorado/motores/leitura/leitores.py, `NE3-064` eldorado/motores/descoberta/vigilancia.py, `NE3-067` eldorado/motores/canal/estado.py |
| É usado por (arquivos) | `NE3-068` eldorado/motores/canal/config/ |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | `motor.execucao`, `achado.entregue` |
| Eventos que consome | `acionamento.feito`, `pertinencia.decidida (retorno)` |
| Configuração | configuração do canal |
| Alarmes | motor sem leitura além do dobro da cadência |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | as 6 metas de qualidade do dossiê dos motores — limiares: as 6 metas de qualidade |
| Teste de aceite | cada um dos 45 motores roda sobre as suas páginas gravadas com resultado igual ou melhor que o atual |
| Ferramentas do GitHub | online-ml/river (bandit de rotas) |
| Existe hoje no Eldorado0 | 21 motores de código e os adaptadores (só a lógica de cada canal, reescrita como configuração e skill) |
| Dados herdados | aprendizado de 197 motores (rotas, afinador, bloqueios, histórico de erros) |
| Cuidados | nenhum código por canal; só configuração e skill |

#### `NE3-066` · `eldorado/motores/canal/achado.py`

**Finalidade:** O formato único do achado: os dados necessários da oportunidade, o link de divulgação, o link oficial, o texto literal comprimido, a assinatura e o endereço do original no Drive.

**Atende à finalidade da titular:** motor extrai exatamente os dados necessários e os dois links.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | montar o achado com os dados necessários; link de divulgação e link oficial; texto literal comprimido; assinatura do original e endereço no Drive |
| Recebe | extração |
| Entrega | achado |
| Usa | `NE3-004` eldorado/base/nucleo/eventos.py |
| É usado por (arquivos) | `NE3-069` eldorado/motores/pilotos/espiao.py |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | `achado.entregue` |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | achado sem os dois links ou sem prova |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | achados completos — limiares: achados completos ≥ 98% / 90 a 98% / < 90% |
| Teste de aceite | um achado chega à base com todos os campos |
| Ferramentas do GitHub | msgspec/msgspec, indygreg/python-zstandard |
| Existe hoje no Eldorado0 | src/achados_motores.py (lições) |
| Dados herdados | — |
| Cuidados | nenhum binário |

#### `NE3-067` · `eldorado/motores/canal/estado.py`

**Finalidade:** Os dados de uso próprio de cada motor (cursor, assinaturas, rotas, cadência, léxico, alternativas de acesso, histórico do aprendizado); nenhuma oportunidade.

**Atende à finalidade da titular:** motores gravam o seu aprendizado; nenhuma oportunidade fora da Biblioteca.

| Campo | Esboço |
| --- | --- |
| Construção | **CRIAR** — criado do zero para o Eldorado |
| Funções principais | cursor por fonte; assinaturas das páginas; estatísticas das rotas; cadência aprendida; léxico próprio; histórico versionado do aprendizado |
| Recebe | execuções |
| Entrega | aprendizado do motor |
| Usa | — |
| É usado por (arquivos) | `NE3-065` eldorado/motores/canal/motor.py |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | — |
| Alarmes | estado corrompido |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | idade do último aprendizado — limiares: íntegro / — / corrompido |
| Teste de aceite | o estado sobrevive a uma queda no meio da execução |
| Ferramentas do GitHub | — |
| Existe hoje no Eldorado0 | estado/rotas/*; estado/robots_motores.json |
| Dados herdados | aprendizado e histórico de erros de cada motor |
| Cuidados | só o motor escreve |

#### `NE3-068` · `eldorado/motores/canal/config/`

**Finalidade:** As 45 configurações de canal (uma por motor) e os seus 114 alvos, preenchidas a partir do dossiê dos motores.

**Atende à finalidade da titular:** adicionar motor sem mudar a estrutura.

| Campo | Esboço |
| --- | --- |
| Construção | **CONFIGURAR** — só configuração (dados), lida por um arquivo de código existente |
| Funções principais | uma configuração por motor: identidade, finalidade, fontes, agenda, léxico, vetos, critérios, degraus de acesso, leitores, formas de descoberta, alvos, metas |
| Recebe | — |
| Entrega | motores configurados |
| Usa | `NE3-065` eldorado/motores/canal/motor.py |
| É usado por (arquivos) | — |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | — |
| Eventos que consome | — |
| Configuração | 45 configurações |
| Alarmes | configuração inválida |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | configurações válidas — limiares: todas válidas / — / inválida |
| Teste de aceite | adicionar uma configuração faz um motor novo rodar |
| Ferramentas do GitHub | — |
| Existe hoje no Eldorado0 | config/agenda_motores.json; config/rotas_motores.json; config/diario_*.json; config/fontes_captacao_260.json e as demais configurações de família |
| Dados herdados | dossiê dos 47 motores |
| Cuidados | adicionar um motor = adicionar um arquivo |


### Pilotos: motores livres com IA

#### `NE3-069` · `eldorado/motores/pilotos/espiao.py`

**Finalidade:** Piloto A, o Espião: motor livre de descoberta, com IA; escolhe as famílias de busca pelo aprendizado (4 em 5) e explora (1 em 5).

**Atende à finalidade da titular:** Espião busca empresas e oportunidades novas.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | escolher as famílias de busca (4 em 5 pelo aprendizado, 1 em 5 explorando); buscar com metabusca e IA; propor fontes novas aos motores; achar empresas novas |
| Recebe | acionamento |
| Entrega | achados e fontes novas |
| Usa | `NE3-007` eldorado/base/nucleo/ia.py, `NE3-060` eldorado/motores/descoberta/metabusca.py, `NE3-066` eldorado/motores/canal/achado.py |
| É usado por (arquivos) | `NE3-087` .github/workflows/pilotos.yml |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | `motor.execucao`, `achado.entregue` |
| Eventos que consome | `acionamento.feito` |
| Configuração | famílias, cotas, descanso |
| Alarmes | 1 dia sem voo com sucesso |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | achados por voo; fontes novas propostas — limiares: voos com sucesso ≥ 80% / 50 a 80% / < 50% |
| Teste de aceite | um voo de teste entrega achados e uma fonte nova |
| Ferramentas do GitHub | online-ml/river (bandit), pydantic/pydantic-ai |
| Existe hoje no Eldorado0 | src/espiao_foco.py; espiao_cerebro.json; apostas, memória de erros, vias, manual |
| Dados herdados | cérebro do Espião; 472 ciclos de aprendizado |
| Cuidados | devolve aos motores o que aprende |

#### `NE3-070` · `eldorado/motores/pilotos/interceptador.py`

**Finalidade:** Piloto B, o Interceptador: IA que pesquisa e comprova os itens que faltam, um livro por voo, gravando pelo contrato da Biblioteca.

**Atende à finalidade da titular:** Interceptador aprofunda e valida o que falta.

| Campo | Esboço |
| --- | --- |
| Construção | **APROVEITAR** — reaproveita lógica validada do Eldorado0, reescrita no contrato novo (nunca copiada com os defeitos) |
| Funções principais | receber o livro direcionado; pesquisar e comprovar os itens que faltam; gravar pelo contrato da Biblioteca; devolver rotas novas aos motores |
| Recebe | livro direcionado |
| Entrega | itens com prova |
| Usa | `NE3-007` eldorado/base/nucleo/ia.py, `NE3-043` eldorado/motores/acesso/escada.py, `NE3-050` eldorado/motores/leitura/leitores.py, `NE3-073` eldorado/banco/biblioteca/livro.py |
| É usado por (arquivos) | `NE3-028` eldorado/base/investigacao/investigacao.py, `NE3-087` .github/workflows/pilotos.yml |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | `motor.execucao`, `certidao.gravada` |
| Eventos que consome | `acionamento.feito` |
| Configuração | tempo por voo |
| Alarmes | 1 dia sem voo com sucesso |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | livros resolvidos por voo; respostas válidas — limiares: livros com item novo ≥ 60% / 30 a 60% / < 30% |
| Teste de aceite | um livro esgotado recebe itens comprovados e o resultado fica gravado |
| Ferramentas do GitHub | pydantic/pydantic-ai, stanfordnlp/dspy |
| Existe hoje no Eldorado0 | src/interceptador.py e src/investigador.py (corrigidos em 22/10); sites oficiais que funcionam; manual |
| Dados herdados | rotas que funcionam por órgão |
| Cuidados | nunca lê caminho de arquivo |


### Skills dos motores e pilotos

#### `NE3-071` · `eldorado/motores/skills/`

**Finalidade:** As skills dos motores e pilotos, no formato aberto (SKILL.md com metadados de uso e resultado), promovidas ou arquivadas pelo Cérebro.

**Atende à finalidade da titular:** ferramentas e skills acopláveis.

| Campo | Esboço |
| --- | --- |
| Construção | **COPIAR_PARTE** — copia uma parte pequena de um projeto aberto (com a licença e a origem registradas no arquivo) |
| Funções principais | skills no formato aberto; metadados de uso e resultado; promoção e arquivamento pelo Cérebro |
| Recebe | — |
| Entrega | skills (descobertas pelo registro, pelos manifestos) |
| Usa | — |
| É usado por (arquivos) | — |
| Usada pelos motores | reserva ou peça do motor genérico |
| Eventos que emite | — |
| Eventos que consome | `aprendizado.promovido`, `aprendizado.arquivado` |
| Configuração | skills ligadas |
| Alarmes | skill com resultado ruim ligada |
| Indicador · ponto | rodou sem erro quando chamado |
| Indicador · círculo | skills ativas e o seu resultado — limiares: skills úteis / — / ruins ligadas |
| Teste de aceite | uma skill nova entra desligada e é ligada depois de vencer a medição |
| Ferramentas do GitHub | anthropics/skills (formato), NousResearch/hermes-agent (metadados) |
| Existe hoje no Eldorado0 | config/skills_motores.json (155 motores); src/executor_skills.py |
| Dados herdados | — |
| Cuidados | licença de cada skill registrada |

## 6. Os motores, um por um


### Executivo — diários e portais do governo

#### `MT-01` · Diário Oficial do Município de Goiânia

`do-goiania` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/do-goiania.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em diário oficial municipal — a fonte primária de Goiânia

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | Lista oficial das edições do ano (Casa Civil): https://www.goiania.go.gov.br/shtml//portal/casacivil/lista_diarios.asp?ano=2026; Querido Diário — Goiânia (IBGE 5208707), texto integral das edições: https://api.queridodiario.ok.org.br/gazettes?territory_ids=5208707; Secretaria Municipal de Cultura — editais PNAB: https://www.goiania.go.gov.br/secretaria/secretaria-municipal-de-cultura/; Conselhos Municipais (CMDCA, CMAS, CMI) — resoluções e editais dos fundos: https://www.goiania.go.gov.br/conselhos-municipais/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:23,12:53,20:23 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (diario_oficial): as edições saem de madrugada; depois vêm as extras e as edições da noite; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem + local |
| Configuração de família herdada | `config/diario_goiania.json` |
| Skills que usa hoje | `motores/por_motor/do-goiania`, `motores/diario_oficial`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 2: `f260-captacao-001` PNAB Goiânia - Audiovisual; `f260-captacao-039` Editais de ocupação cultural municipal |
| Aprendizado herdado | 220 leituras, 19 com resultado (9%); bloqueios em www.goiania.go.gov.br (58), diariooficial.goiania.go.gov.br (35); rotas que o afinador provou: https://www.goiania.go.gov.br/secult/leipaulogustavo/; https://www.goiania.go.gov.br/secult/pnab-2024/; https://www.goiania.go.gov.br/; https://www.goiania.go.gov.br/secult/leipaulogustavo/; https://www.goiania.go.gov.br/secult/pnab-2024/; https://www.goiania.go.gov.br/; https://www.goiania.go.gov.br; https://www.goiania.go.gov.br/feed |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 19, vermelho 3. Luz em 22 dias (01/10 a 22/10): 19 verdes, 0 amarelos, 3 vermelhos; maior sequência vermelha: 2 dias (2026-10-21 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (3). Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (57 leituras). Outubro: executou 19 de 22 dias esperados (cobertura 86%), 9 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-20; 1 achado(s) acumulado(s); 1 achados no total. Alerta atual (media): 2 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. Qualidade do que entrega: 1 oportunidades abertas, 12.0 itens por oportunidade, 100% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 1 em 1 dias, do primeiro em 2026-10-01 ao último em 2026-10-01. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 2 domínio(s) com bloqueio: começar pelo degrau aprendido; 2 alvos vigiados só na janela prevista |

#### `MT-02` · Diário Oficial do Estado de Goiás

`do-goias` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/do-goias.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em diário oficial estadual — SECULT, SEDS, SES, SEEL e decretos de emenda

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | Diário do Estado — busca de texto completo: https://diariooficial.abc.go.gov.br/busca/busca/buscar/query/0/; Diário do Estado — edições do dia, sumário por órgão e texto da matéria: https://diariooficial.abc.go.gov.br/apifront/portal/edicoes/edicoes_from_data/; SECULT-GO — Chamamentos Públicos 2026 (Lei 13.019): https://goias.gov.br/cultura/chamamentos-publicos-2026-lei-13-019-14/; SECULT-GO — Chamamentos Públicos (geral): https://goias.gov.br/cultura/chamamentos-publicos-secult/; SEDS / Goiás Social — notícias e editais (API): https://goias.gov.br/social/wp-json/wp/v2/posts; SEEL — Chamamento público: https://goias.gov.br/esporte/chamamento-publico/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:23,12:53,20:23 · dias: seg,ter,qua,qui,sex,sab · cadencia dias: 1 · por que esta hora: itinerário 02/10 (diario_oficial): as edições saem de madrugada; depois vêm as extras e as edições da noite; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem + local |
| Configuração de família herdada | `config/diario_goias.json` |
| Skills que usa hoje | `motores/por_motor/do-goias`, `motores/diario_oficial`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 2: `f260-captacao-034` Fundo de Arte e Cultura de Goiás - projeto cultural geral; `f260-captacao-206` Convênio com órgão público estadual |
| Aprendizado herdado | 150 leituras, 66 com resultado (44%); bloqueios em diariooficial.abc.go.gov.br (4), goias.gov.br (97); rotas que o afinador provou: https://diariooficial.abc.go.gov.br/ |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21, cinza 1. Luz em 22 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. Acerto das rotas piorou: 100% na primeira metade do período e 67% na segunda (57 leituras). Outubro: executou 19 de 22 dias esperados (cobertura 86%), 17 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-22; 20 achado(s) acumulado(s); 20 achados no total. Qualidade do que entrega: 3 oportunidades abertas, 10.3 itens por oportunidade, 67% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 2 em 2 dias, do primeiro em 2026-10-01 ao último em 2026-10-09. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 2 domínio(s) com bloqueio: começar pelo degrau aprendido; 2 alvos vigiados só na janela prevista |

#### `MT-03` · Diário Oficial da União

`dou` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/dou.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em diário federal — ministérios, fundos e conselhos nacionais, prefeituras de Goiás que publicam no DOU, doação de bens e coleta solidária em Goiás/DF

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | DOU Seção 1 — Leitura do Jornal (atos normativos, resoluções de conselho): https://www.in.gov.br/leiturajornal?secao=do1; DOU Seção 3 — Leitura do Jornal (avisos, editais, extratos): https://www.in.gov.br/leiturajornal?secao=do3; DOU edições extras (anunciadas no próprio dia): https://www.in.gov.br/leiturajornal?secao=do1e; DOU busca semanal (reserva): https://www.in.gov.br/consulta/-/buscar/dou?q=chamamento&s=todos&exactDate=semana |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:23,12:53,20:23 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (diario_oficial): as edições saem de madrugada; depois vêm as extras e as edições da noite; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/diario_uniao.json` |
| Skills que usa hoje | `motores/por_motor/dou`, `motores/diario_oficial`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 2: `f260-captacao-134` MDHC - editais de direitos humanos; `f260-captacao-207` Acordo de cooperação sem transferência financeira |
| Aprendizado herdado | 180 leituras, 62 com resultado (34%); bloqueios em www.in.gov.br (334); rotas que o afinador provou: https://www.in.gov.br/web/dou/-/aviso-de-selecao-publica-735913080; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publco-n-1/2025-607581050; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-n-24000001/2024-cs-553430032; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-625851399; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-n-2/gap-rf/2024-577954751; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-733071223; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-n-1/2024-587164593; https://www.in.gov.br/web/dou/-/aviso-de-chamamento-publico-n-1/2024-571998038 |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21, vermelho 1. Luz em 22 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-19 a 2026-10-19). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (1). Acerto das rotas ficou estável: 96% na primeira metade do período e 100% na segunda (57 leituras). Outubro: executou 22 de 22 dias esperados (cobertura 100%), 8 dias com achado, 0 falhas; veredito: íntegro. Auditoria: FUNCIONANDO — leu em 2026-10-22; 27 achado(s) acumulado(s); 27 achados no total. Qualidade do que entrega: 3 oportunidades abertas, 11.0 itens por oportunidade, 67% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 3 em 2 dias, do primeiro em 2026-10-05 ao último em 2026-10-13. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 domínio(s) com bloqueio: começar pelo degrau aprendido; 2 alvos vigiados só na janela prevista |

#### `MT-04` · Prefeituras das 25 maiores cidades de Goiás — portais de editais

`prefeituras-50-go` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/prefeituras-50-go.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em 25 maiores prefeituras de Goiás — cada uma publica no portal próprio E no diário/PNCP (finalidade herdada do motor agregado plat-prefeituras-50-go)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | Portal da prefeitura (config/municipios_maiores.json → GO): config/municipios_maiores.json; Diário oficial do município (Querido Diário / próprio): https://queridodiario.ok.org.br/; PNCP como descoberta (número do processo): https://pncp.gov.br/ |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | `config/prefeituras_25_go.json`, `config/portais_federativos.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-prefeituras-50-go` (60/117 leituras com resultado) |
| Alvos vigiados | 4: `f260-captacao-072` Arte e Cultura na Educação Integral; `f260-captacao-149` SMS Goiânia - parceria com entidade de saúde; `f260-espalhado-acessoainformacao-cavalcante-go-gov-br` PNCP — FUNDO MUNICIPAL DE CULTURA - CAVALCANTE — oportunidades (espalhado de edital validado); `f260-espalhado-senadorcanedo-go-gov-br` PNCP — FUNDO MUNICIPAL DE EDUCACAO E CULTURA - FMEC — oportunidades (espalhado de edital validado) |
| Aprendizado herdado | 165 leituras, 62 com resultado (38%); bloqueios em pncp.gov.br (162), queridodiario.ok.org.br (1), www.goiania.go.gov.br (58), saude.goiania.go.gov.br (4), acessoainformacao.cavalcante.go.gov.br (1); rotas que o afinador provou: https://www.goiania.go.gov.br/secult/leipaulogustavo/; https://www.goiania.go.gov.br/secult/pnab-2024/; https://www.goiania.go.gov.br/; https://www.goiania.go.gov.br; https://www.goiania.go.gov.br/feed; https://senadorcanedo.go.gov.br/senador-canedo-abre-inscricoes-para-o-projeto-guardioes-ambientais-2026/; https://senadorcanedo.go.gov.br/senador-canedo-lanca-edital-aldir-blanc-2026-com-r-380-mil-destinado-a-projetos-culturais/; https://senadorcanedo.go.gov.br/senador-canedo-abre-credenciamento-para-artistas-locais-do-canedo-fest-show-2026/ |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 17, vermelho 5. Luz em 22 dias (01/10 a 22/10): 17 verdes, 0 amarelos, 5 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4), erro de código (1). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 6 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 6 domínio(s) com bloqueio: começar pelo degrau aprendido; 4 alvos vigiados só na janela prevista |

#### `MT-05` · Oportunidade Estaduais Governamentais de Goiás

`estaduais-go-gov` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/estaduais-go-gov.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em TODOS os órgãos do Poder Executivo de Goiás (secretarias, autarquias, fundações, empresas estatais, conselhos e fundos), lidos um por vez em camadas: onde publicam, histórico de 5 anos, oportunidades e monitoramento diário (finalidade herdada do motor agregado plat-estaduais-go-gov)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | site oficial 1: https://goias.gov.br/; site oficial 2: https://goias.gov.br/cultura/editais/; site oficial 3: https://goias.gov.br/social/editais/; FAPEG — chamadas públicas: https://goias.gov.br/fapeg/; Diário Oficial do Estado: https://diariooficial.abc.go.gov.br/; CEDCA-GO — FIA estadual (resoluções e editais): https://goias.gov.br/desenvolvimento-social/; Conselho Estadual do Idoso — Fundo do Idoso: https://goias.gov.br/desenvolvimento-social/; SEMAD — FEMA: https://goias.gov.br/meioambiente/; Diário Oficial do Estado (resoluções dos conselhos): https://diariooficial.abc.go.gov.br/; Goiás Social: https://goias.gov.br/social/; SEDS — editais: https://goias.gov.br/desenvolvimento-social/; OVG — portal: https://www.ovg.org.br/ |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | `config/estaduais_go.json`, `config/portais_federativos.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 7: `plat-estaduais-go-gov` (30/86 leituras com resultado); `plat-fapeg` (0/19 leituras com resultado); `plat-fundos-estaduais-go` (0/19 leituras com resultado); `plat-goias-social` (0/19 leituras com resultado); `plat-ovg` (0/19 leituras com resultado); `plat-secult-go` (0/19 leituras com resultado); `plataforma-wordpress` (23/23 leituras com resultado) |
| Alvos vigiados | 10: `f260-captacao-018` PNAB Goiás - Audiovisual; `f260-captacao-025` PNAB Goiás - Artes Visuais; `f260-captacao-038` Editais FICA Goiás - artes visuais/exposição; `f260-captacao-051` Programa estadual de eventos esportivos; `f260-captacao-081` Projeto de educação para o trabalho; `f260-captacao-095` SEDS Goiás - Auxílio Nutricional a entidades; `f260-captacao-098` FEAS-GO - cofinanciamento da assistência social; `f260-captacao-159` Projeto de teleorientação em saúde comunitária; `f260-captacao-177` SEMAD Goiás - banco de projetos de autocomposição ambiental; `f260-curadoria-009` SECULT Goiás — chamamentos públicos da Lei 13.019/2014 |
| Aprendizado herdado | 382 leituras, 85 com resultado (22%); bloqueios em goias.gov.br (97), diariooficial.abc.go.gov.br (4), www.ovg.org.br (21), pnab.cultura.go.gov.br (1), www.goias.gov.br (6); rotas que o afinador provou: https://goias.gov.br/cultura/secult-goias-prorroga-inscricoes-para-os-editais-da-politica-nacional-aldir-blanc/; https://goias.gov.br/cultura/governo-de-goias-abre-inscricoes-para-o-programa-goyazes-2025-com-novas-regras/; https://goias.gov.br/cultura/programa-goyazes-abre-inscricoes-nesta-terca-feira-02-04/; https://goias.gov.br/cultura/secult-goias-prorroga-inscricoes-da-lei-paulo-gustavo/; https://goias.gov.br/cultura/governo-de-goias-abre-inscricoes-para-novos-editais-dos-pontos-de-cultura-com-investimento-de-cerca-de-r-2-milhoes-2/; https://goias.gov.br/esporte/governo-de-goias-prorroga-inscricoes-para-a-4a-edicao-da-copa-quilombola/; https://goias.gov.br/fapeg/editais/inscricoes-abertas/; https://goias.gov.br/social/inscricoes-abertas-para-representantes-da-sociedade-civil-interessados-em-integrar-o-conselho-estadual-de-direitos-humanos-igualdade-racial-e-combate-ao-preconceito-2/ |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, verde 4, vermelho 4. Acerto das rotas ficou estável: 51% na primeira metade do período e 50% na segunda (55 leituras). Outubro: executou 16 de 22 dias esperados (cobertura 73%), 1 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-18; 1 achado(s) acumulado(s); 1 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 18 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 7 domínio(s) com bloqueio: começar pelo degrau aprendido; 10 alvos vigiados só na janela prevista |

#### `MT-06` · PNCP — API de contratações (chamamentos e credenciamentos)

`pncp-api` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/pncp-api.toml`

**Finalidade:** encontrar no PNCP as seleções ABERTAS para OSC em Goiás e nos órgãos federais, com a data oficial de encerramento

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | API do PNCP — propostas abertas (data oficial de encerramento): https://pncp.gov.br/api/consulta/v1/contratacoes/proposta; Busca do portal PNCP — editais recebendo proposta: https://pncp.gov.br/api/search/; Arquivos do edital do órgão hospedados no PNCP (/arquivos/) — documento oficial: https://pncp.gov.br/pncp-api/v1/orgaos/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 08:53,13:53,19:53 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (portal_chamamentos): atualização contínua em horário comercial; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/pncp_osc.json` |
| Skills que usa hoje | `motores/por_motor/pncp-api`, `motores/portal_chamamentos`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 17: `f260-espalhado-carazinho-atende-net` PNCP — MUNICIPIO DE CARAZINHO — oportunidades (espalhado de edital validado); `f260-espalhado-carire-ce-gov-br` PNCP — MUNICIPIO DE CARIRE — oportunidades (espalhado de edital validado); `f260-espalhado-crcgo-org-br` PNCP — CONSELHO REGIONAL DE CONTABILIDADE DO ESTADO DE GOIAS — oportunidades (espalhado de edital validado); `f260-espalhado-sistema-mirassoldoeste-mt-gov-br` PNCP — MUNICIPIO DE MIRASSOL D'OESTE — oportunidades (espalhado de edital validado); `f260-espalhado-transparencia-agilicloud-com-br` PNCP — MUNICIPIO DE PARANATINGA — oportunidades (espalhado de edital validado); `f260-espalhado-transparencia-cacoal-ro-gov-br` PNCP — MUNICIPIO DE CACOAL — oportunidades (espalhado de edital validado); `f260-espalhado-transparencia-nobres-mt-gov-br` PNCP — MUNICIPIO DE NOBRES — oportunidades (espalhado de edital validado); `f260-espalhado-www-bentogoncalves-rs-gov-br` PNCP — MUNICIPIO DE BENTO GONCALVES — oportunidades (espalhado de edital validado); `f260-espalhado-www-detran-rj-gov-br` PNCP — ESTADO DO RIO DE JANEIRO — oportunidades (espalhado de edital validado); `f260-espalhado-www-ipora-pr-gov-br` PNCP — MUNICIPIO DE IPORA — oportunidades (espalhado de edital validado); `f260-espalhado-www-itabaianinha-se-gov-br` PNCP — MUNICIPIO DE ITABAIANINHA — oportunidades (espalhado de edital validado); `f260-espalhado-www-novohamburgo-rs-gov-br` PNCP — MUNICIPIO DE NOVO HAMBURGO — oportunidades (espalhado de edital validado); `f260-espalhado-www-ribeiraodasneves-mg-gov-br` PNCP — MUNICIPIO DE RIBEIRAO DAS NEVES — oportunidades (espalhado de edital validado); `f260-espalhado-www-riopreto-sp-gov-br` PNCP — MUNICIPIO DE SAO JOSE DO RIO PRETO — oportunidades (espalhado de edital validado) … |
| Aprendizado herdado | 165 leituras, 23 com resultado (14%); bloqueios em pncp.gov.br (162), carazinho.atende.net (1), sistema.mirassoldoeste.mt.gov.br (69), transparencia.agilicloud.com.br (4), www.bentogoncalves.rs.gov.br (36); rotas que o afinador provou: https://www.bentogoncalves.rs.gov.br/feed; https://www.bentogoncalves.rs.gov.br/transparencia/editais; https://www.bentogoncalves.rs.gov.br/editais; https://www.detran.rj.gov.br/sitemap.xml; https://www.detran.rj.gov.br/noticias; https://www.ipora.pr.gov.br/; https://www.riopreto.sp.gov.br/transparencia/editais; https://www.vilarica.mt.gov.br/sitemap.xml |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 17, vermelho 5. Luz em 22 dias (01/10 a 22/10): 17 verdes, 0 amarelos, 5 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (5). Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (12 leituras). Outubro: executou 8 de 22 dias esperados (cobertura 36%), 7 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-18; 261 achado(s) acumulado(s); 261 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. Qualidade do que entrega: 6 oportunidades abertas, 11.7 itens por oportunidade, 67% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 19 em 13 dias, do primeiro em 2023-06-13 ao último em 2026-10-17. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 18 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 7 domínio(s) com bloqueio: começar pelo degrau aprendido; 17 alvos vigiados só na janela prevista |

#### `MT-07` · Lei Rouanet — janela de propostas no SALIC e projetos de Goiás (Ministério da Cultura)

`salic` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/salic.toml`

**Finalidade:** acompanhar as edições do programa “Ministério da Cultura — SALIC — oportunidades (espalhado de edital validado)” (cultura, Brasil, None) no site oficial do órgão (finalidade herdada do motor agregado f260-espalhado-rouanet-cultura-gov-br)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | https://rouanet.cultura.gov.br/; MinC — Lei Rouanet (página institucional): https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet; Salic — sistema de propostas: https://salic.cultura.gov.br/; Instrução Normativa vigente (prazos e limites): https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet/legislacao; VerSalic — consulta pública de projetos e editais: https://versalic.cultura.gov.br/ |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | `config/programas.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/planilha.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 2: `f260-espalhado-rouanet-cultura-gov-br` (0/40 leituras com resultado); `plat-salic` (65/117 leituras com resultado) |
| Alvos vigiados | 1: `f260-captacao-035` Lei Rouanet - doação de pessoa física |
| Aprendizado herdado | 194 leituras, 71 com resultado (37%); bloqueios em rouanet.cultura.gov.br (86), salic.cultura.gov.br (1), www.gov.br (223) |
| Histórico de erros (01/10 a 22/10) | Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (24 leituras). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 17 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 4 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 3 domínio(s) com bloqueio: começar pelo degrau aprendido; 1 alvos vigiados só na janela prevista |

#### `MT-08` · Motor Incentivos Fiscais — empresas da base ICMS/RFB/SALIC (Goiás)

`motor-gife` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/motor-gife.toml`

**Finalidade:** empresas da base ICMS/RFB/SALIC de Goiás com potencial de destinação incentivada e os sites das maiores contribuintes do ICMS (editais incentivados)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | maiores contribuintes do ICMS de Goiás: https://goias.gov.br/economia/os-maiores-contribuintes-do-icms/; site institucional de cada empresa (páginas de RSE): ; Salic — projetos que a empresa já incentivou: https://salic.cultura.gov.br/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 03:23 · dias: todos · cadencia dias: 1 · por que esta hora: cadastro de empresas muda devagar; leitura semanal no domingo · coleta: nuvem |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/motor-gife`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/planilha.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `motor-patrocinio` (0/0 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%); bloqueios em goias.gov.br (97), salic.cultura.gov.br (1), html.duckduckgo.com (4) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 16, verde 20, vermelho 8. Luz em 22 dias (01/10 a 22/10): 10 verdes, 0 amarelos, 4 vermelhos; maior sequência vermelha: 4 dias (2026-10-10 a 2026-10-13). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 3 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-09` · Busca de empresas para FIA, Idoso, Lei de Incentivo ao Esporte, Pronas, Pronon e Goyazes

`empresas-editais-incentivados` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/empresas-editais-incentivados.toml`

**Finalidade:** identificar empresa que já financiou o terceiro setor, e por qual via (finalidade herdada do motor agregado empresas-incentivadas)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | Site institucional da empresa (ranking dos 100 maiores contribuintes ICMS-GO): biblioteca_alexandria/livros/especiais/empresas/ranking_destinacao_tributaria.json; Portais do terceiro setor onde a empresa anuncia (Observatório, ABCR, GIFE): https://observatorio3setor.org.br/editais/; Página de editais e home dos institutos/fundações das empresas que já destinam (banco verificado): config/empresas_destinadoras.json; Portais do terceiro setor onde a empresa anuncia: https://captadores.org.br/editais/; Redes sociais institucionais (LinkedIn/Instagram) — pista, nunca fonte:  |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/planilha.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 2: `empresas-incentivadas` (24/32 leituras com resultado); `plat-empresas-editais-incentivados` (77/120 leituras com resultado) |
| Alvos vigiados | 5: `f260-captacao-041` Lei de Incentivo ao Esporte - Esporte para Toda a Vida; `f260-captacao-044` Projetos aptos à captação na LIE; `f260-captacao-118` Destinação de IR pessoa física para FMDCA; `f260-captacao-119` Destinação de IR pessoa jurídica para Fundo da Criança; `f260-captacao-143` Pronas/PCD - assistência à pessoa com deficiência |
| Aprendizado herdado | 312 leituras, 140 com resultado (45%); bloqueios em go.equatorialenergia.com.br (27), paraquemdoar.org (1), www.saneago.com.br (1), captadores.org.br (12), www.gov.br (223); rotas que o afinador provou: https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-centro-oeste/programa-rouanet-centro-oeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/programa-rouanet-da-juventude; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/selecao-petrobras-cultural-2013-novos-eixos-1; https://www.gov.br/iphan/pt-br/unidades-especiais/centro-nacional-de-folclore-e-cultura-popular/noticias-1/cnfcp-lanca-edital-do-premio-mario-de-andrade-de-fotografias-etnograficas-2026; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-em-andamento/rouanet-nordeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/edital-de-eleicao-do-cnpc/edital-de-eleicao-do-cnpc; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/edital-de-credenciamento-de-pareceristas-tecnicos/edital-de-credenciamento-de-pareceristas-tecnicos |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1. Luz em 1 dias (01/10 a 22/10): 0 verdes, 0 amarelos, 0 vermelhos. Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (27 leituras). Outubro: executou 14 de 22 dias esperados (cobertura 64%), 14 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-22; 41 achado(s) acumulado(s); 41 achados no total. Achados: 11 em 6 dias, do primeiro em 2026-09-03 ao último em 2026-10-17. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 16 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 8 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 6 domínio(s) com bloqueio: começar pelo degrau aprendido; 5 alvos vigiados só na janela prevista |

#### `MT-10` · CNPq / MCTI / Setec-MEC — chamadas com componente de extensão e parceria com OSC

`cnpq-extensao` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/cnpq-extensao.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em CNPq / MCTI / Setec-MEC — chamadas com componente de extensão que aceitam OSC como parceira (finalidade herdada do motor agregado plat-cnpq-extensao)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | CNPq — chamadas abertas para submissão: https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao; MCTI — editais e comunicados: https://www.gov.br/mcti/pt-br/centrais-de-conteudo/comunicados-mcti; MCTI — popularização da ciência: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/popciencia; Setec/MEC — educação profissional e tecnológica: https://www.gov.br/mec/pt-br/composicao/setec |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | `config/programas.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 2: `plat-cnpq-extensao` (53/97 leituras com resultado); `site-finep` (0/0 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 97 leituras, 53 com resultado (55%); bloqueios em www.gov.br (223); rotas que o afinador provou: https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-centro-oeste/programa-rouanet-centro-oeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2; https://www.gov.br/iphan/pt-br/unidades-especiais/centro-nacional-de-folclore-e-cultura-popular/noticias-1/cnfcp-lanca-edital-do-premio-mario-de-andrade-de-fotografias-etnograficas-2026; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/programa-rouanet-da-juventude; https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/leilao/pdm/doacoes; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/selecao-petrobras-cultural-2013-novos-eixos-1; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-em-andamento/rouanet-nordeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/edital-de-eleicao-do-cnpc/edital-de-eleicao-do-cnpc |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1. Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (55 leituras). Outubro: executou 20 de 3 dias esperados (cobertura 100%), 11 dias com achado, 0 falhas; veredito: íntegro. Auditoria: FUNCIONANDO — leu em 2026-10-22; 133 achado(s) acumulado(s); 133 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-11` · Funarte — editais da Fundação Nacional de Artes

`site-funarte` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-funarte.toml`

**Finalidade:** editais da Fundação Nacional de Artes

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | Funarte:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13,19:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-funarte`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 19, vermelho 1, cinza 1. Luz em 21 dias (01/10 a 22/10): 19 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-07 a 2026-10-07). Tipos de problema nos dias amarelos ou vermelhos: erro de código (1). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 12 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-12` · Transferegov — programas e parcerias com OSC abertos na plataforma federal (dados abertos)

`site-transferegov` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-transferegov.toml`

**Finalidade:** programas e parcerias com OSC abertos na plataforma federal (dados abertos)

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | Transferegov: https://api-publica.transferegov.gestao.gov.br/downloads/dadosgov/siconv_programa.zip |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | `config/programas.json` |
| Skills que usa hoje | `motores/por_motor/site-transferegov`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/planilha.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 4: `f260-captacao-060` Escolinha de natação/paradesporto adaptado; `f260-captacao-090` MDS - Cozinhas Solidárias 2026; `f260-captacao-180` Projeto de coleta seletiva inclusiva; `f260-curadoria-010` MDHC / CONANDA — Chamamentos publicos de fomento a OSC |
| Aprendizado herdado | 66 leituras, 22 com resultado (33%); bloqueios em www.gov.br (223); rotas que o afinador provou: https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-centro-oeste/programa-rouanet-centro-oeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-abertas/programa-rouanet-nas-favelas-2/programa-rouanet-nas-favelas-2; https://www.gov.br/iphan/pt-br/unidades-especiais/centro-nacional-de-folclore-e-cultura-popular/noticias-1/cnfcp-lanca-edital-do-premio-mario-de-andrade-de-fotografias-etnograficas-2026; https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/leilao/pdm/doacoes; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/programa-rouanet-da-juventude; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-em-andamento/rouanet-nordeste; https://www.gov.br/cultura/pt-br/assuntos/editais/inscricoes-encerradas/selecao-petrobras-cultural-2013-novos-eixos-1; https://www.gov.br/cultura/pt-br/assuntos/acoes-programas-e-politicas/lei-rouanet-1 |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 20, cinza 1. Luz em 21 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 17 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 5 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 domínio(s) com bloqueio: começar pelo degrau aprendido; 4 alvos vigiados só na janela prevista |

#### `MT-13` · Diários oficiais municipais de Goiás (Querido Diário)

`novo-diarios-municipais-go` · sugestão · arquivo: `eldorado/motores/canal/config/novo-diarios-municipais-go.toml`

**Finalidade:** sugestão: um só motor lê, pela API do Querido Diário, os diários de todos os municípios de Goiás, complementando o Diário de Goiânia

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial (motor novo: sugestão: um só motor lê, pela API do Querido Diário, os diários de todos os municípios de Goiás, complementando o Diário de Goiânia).

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | — |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | `config/querido_diario_fontes.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 1: `f260-espalhado-www-arapongas-pr-gov-br` Querido Diário — diários oficiais municipais — oportunidades (espalhado de edital validado) |
| Aprendizado herdado | 1 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | sem registro no período |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 13 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 alvos vigiados só na janela prevista |

#### `MT-14` · Bancos públicos e Sistema S (BNDES, BNB, Caixa, Sebrae)

`novo-bancos-publicos` · sugestão · arquivo: `eldorado/motores/canal/config/novo-bancos-publicos.toml`

**Finalidade:** sugestão: os editais sociais dos bancos públicos e do Sistema S estão hoje espalhados em pontos de captação e não cabem em nenhum motor mantido

**Atende à finalidade da titular:** buscar oportunidades nos diários e portais do governo, com o link oficial (motor novo: sugestão: os editais sociais dos bancos públicos e do Sistema S estão hoje espalhados em pontos de captação e não cabem em nenhum motor mantido).

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | — |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `site-petrobras` (0/0 leituras com resultado) |
| Alvos vigiados | 5: `f260-captacao-175` BNDES Periferias - geração de emprego e renda; `f260-captacao-176` BNDES Corais - meio ambiente; `f260-captacao-220` BNDES Fundo Socioambiental; `f260-captacao-238` Sebrae Goiás - parcerias com OSC para empreendedorismo; `f260-curadoria-001` Banco do Nordeste — Editais Sociais (incentivo fiscal) |
| Aprendizado herdado | 127 leituras, 27 com resultado (21%); bloqueios em www.bndes.gov.br (4), sebraego.com.br (95), www.bnb.gov.br (28) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1. Luz em 1 dias (01/10 a 22/10): 0 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 7 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 3 domínio(s) com bloqueio: começar pelo degrau aprendido; 5 alvos vigiados só na janela prevista |


### Judiciário e Ministérios Públicos

#### `MT-15` · TJ-GO — editais das comarcas (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO

`judiciario-tjgo` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/judiciario-tjgo.toml`

**Finalidade:** editais das comarcas do TJ-GO (prestações pecuniárias) e Banco de Projetos Sociais da CGJ/GO

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | TJGO — Agência de Notícias (RSS paginado): https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss; TJGO — PDF do edital anexado à notícia: https://www.tjgo.jus.br/files/; Corregedoria (CGJ/GO) — Banco de Projetos Sociais (cadastro prévio): https://corregedoria.tjgo.jus.br/basesocial; Portal do CNJ — busca (republica editais dos tribunais) e regra nacional: https://www.cnj.jus.br/?s=presta%C3%A7%C3%A3o+pecuni%C3%A1ria+edital; PNCP — credenciamentos do TJGO e do CNJ (cruzado do motor 04): https://pncp.gov.br/app/editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:53,16:23 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (justica_mp): o expediente forense publica de manhã e no fim da tarde; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem + local |
| Configuração de família herdada | `config/judiciario_go.json` |
| Skills que usa hoje | `motores/por_motor/judiciario-tjgo`, `motores/justica_mp`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 2: `dje-tjgo` (0/40 leituras com resultado); `judiciario-cnj-tjgo` (0/30 leituras com resultado) |
| Alvos vigiados | 1: `f260-captacao-190` TJGO - penas pecuniárias 1ª Vara de Execução Penal de Goiânia |
| Aprendizado herdado | 235 leituras, 0 com resultado (0%); bloqueios em pncp.gov.br (162), www.cnj.jus.br (55), www.tjgo.jus.br (140), www.trt18.jus.br (18) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 9, verde 13. Luz em 21 dias (01/10 a 22/10): 13 verdes, 0 amarelos, 0 vermelhos. Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (70 leituras). Outubro: executou 16 de 22 dias esperados (cobertura 73%), 0 dias com achado, 16 falhas; veredito: lacunas. Auditoria: BLOQUEADO — todas as páginas falharam em 2026-10-18; 0 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 4 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 4 domínio(s) com bloqueio: começar pelo degrau aprendido; nenhum resultado no histórico: diagnosticar antes de ligar; 1 alvos vigiados só na janela prevista |

#### `MT-16` · Diário da Justiça Federal — Seção Judiciária de Goiás

`dj-trf1-go` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/dj-trf1-go.toml`

**Finalidade:** encontrar oportunidade aberta para OSC em destinações de pena federais — raras em Goiás

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | SJGO — Notícias (onde sai o chamamento de entidades): https://www.trf1.jus.br/sjgo/imprensa/noticias; SJGO — Editais e Portarias: https://www.trf1.jus.br/sjgo/processual/editais-e-portarias; Portal do CNJ — busca (republica editais dos tribunais; motor do CNJ): https://www.cnj.jus.br/?s=presta%C3%A7%C3%A3o+pecuni%C3%A1ria+Goi%C3%A1s |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:53 · dias: seg,ter,qua,qui,sex · cadencia dias: 1 · por que esta hora: o diário da Justiça Federal sai durante a noite; coleta local · coleta: nuvem |
| Configuração de família herdada | `config/judiciario_go.json` |
| Skills que usa hoje | `motores/por_motor/dj-trf1-go`, `motores/diario_oficial`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 80 leituras, 0 com resultado (0%); bloqueios em www.cnj.jus.br (55); rotas que o afinador provou: https://www.trf1.jus.br/sjgo/processual/editais-e-portarias; https://www.trf1.jus.br/sjgo/imprensa/noticias |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 4, verde 17, vermelho 1. Luz em 22 dias (01/10 a 22/10): 17 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-11 a 2026-10-11). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (1). Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (36 leituras). Outubro: executou 17 de 1 dias esperados (cobertura 100%), 0 dias com achado, 0 falhas; veredito: íntegro. Auditoria: LENDO SEM ACHAR — leu em 2026-10-22; nunca reconheceu edital; 0 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 14 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 domínio(s) com bloqueio: começar pelo degrau aprendido; nenhum resultado no histórico: diagnosticar antes de ligar |

#### `MT-17` · CNJ — destinação de prestações pecuniárias: busca no Portal do CNJ e regra nacional (Res. 558/2024)

`judiciario-cnj` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/judiciario-cnj.toml`

**Finalidade:** editais e regra nacional de destinação de prestações pecuniárias no Portal do CNJ

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | TJGO — Agência de Notícias (RSS paginado): https://www.tjgo.jus.br/index.php/agencia-de-noticias/noticias-ccs?format=feed&type=rss; TJGO — PDF do edital anexado à notícia: https://www.tjgo.jus.br/files/; Corregedoria (CGJ/GO) — Banco de Projetos Sociais (cadastro prévio): https://corregedoria.tjgo.jus.br/basesocial; Portal do CNJ — busca (republica editais dos tribunais) e regra nacional: https://www.cnj.jus.br/?s=presta%C3%A7%C3%A3o+pecuni%C3%A1ria+edital; PNCP — credenciamentos do TJGO e do CNJ (cruzado do motor 04): https://pncp.gov.br/app/editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:53 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (justica_mp): o expediente forense publica de manhã e no fim da tarde; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/judiciario_go.json` |
| Skills que usa hoje | `motores/por_motor/judiciario-cnj`, `motores/justica_mp`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `cnj-destinacoes` (0/40 leituras com resultado) |
| Alvos vigiados | 1: `f260-captacao-193` CNJ - política de destinação de penas pecuniárias |
| Aprendizado herdado | 113 leituras, 0 com resultado (0%); bloqueios em pncp.gov.br (162), www.cnj.jus.br (55), www.tjgo.jus.br (140), www.trt18.jus.br (18); rotas que o afinador provou: https://www.cnj.jus.br/abertas-inscricoes-para-reuniao-sobre-decente-nas-plataformas-digitais; https://www.cnj.jus.br/arrecadacao-de-penas-pecuniarias-ira-para-projetos-sociais/; https://www.cnj.jus.br/norma-do-cnj-garante-verbas-para-projetos-sociais-em-cangucu-rs/; https://www.cnj.jus.br/edital-seleciona-entidades-sociais-de-goias-para-receber-recursos-de-penas-pecuniarias/; https://www.cnj.jus.br/comarca-de-tutoia-divulga-resultado-de-selecao-para-projetos-sociais/; https://www.cnj.jus.br/projetos-sociais-recebem-r-360-mil-de-verba-pecuniaria-em-pernambuco/; https://www.cnj.jus.br/programas-e-acoes/direitos-humanos/politica-nacional-de-atencao-as-pessoas-em-situacao-de-rua-e-suas-interseccionalidades/premio-de-boas-praticas-na-politica-judiciaria-popruajud; https://www.cnj.jus.br/vara-unica-de-acari-rn-destina-r-153-mil-a-projetos-sociais/ |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 2, verde 18, vermelho 2. Luz em 21 dias (01/10 a 22/10): 18 verdes, 0 amarelos, 2 vermelhos; maior sequência vermelha: 2 dias (2026-10-19 a 2026-10-20). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (2). Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (55 leituras). Outubro: executou 18 de 22 dias esperados (cobertura 82%), 1 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-22; 2 achado(s) acumulado(s); 2 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 4 domínio(s) com bloqueio: começar pelo degrau aprendido; nenhum resultado no histórico: diagnosticar antes de ligar; 1 alvos vigiados só na janela prevista |

#### `MT-18` · MP-GO — Programa Destina (cadastro de entidades para receber bens e valores de acordos)

`mpgo-destinacao` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/mpgo-destinacao.toml`

**Finalidade:** Destina do MP-GO (Edital de Chamamento 02/2024, cadastro contínuo): regra fixa — o site do MP-GO proíbe robôs. Leitura indireta semanal pelo Diário do Estado (quem recebe recurso DAAMP publica lá) e lembrete de conferência manual mensal

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | MPT-GO — PRT 18ª Região (Goiânia e PTM Anápolis): https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens; MPT-GO — PRT 18ª Região: https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais; MPT-GO — PRT 18ª Região (Goiânia/GO): https://www.prt18.mpt.mp.br/informe-se/noticias-do-mpt-go; MPT nacional — PGT - Noticias: https://mpt.mp.br/search_rss?SearchableText=edital+cadastramento+entidades&sort_on=Date&sort_order=reverse; MPT nacional — PGT - Noticias: https://mpt.mp.br/pgt/noticias/RSS; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao; MPF — nacional (busca): https://www.mpf.mp.br/search?SearchableText=edital+chamamento+recebimento+bens+valores; MPF — PR-BA (modelo): https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores; MPF — nacional: https://www.mpf.mp.br/servicos/mpf-servicos |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:53 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (justica_mp): o expediente forense publica de manhã e no fim da tarde; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem (indireta: Diário do Estado) + manual |
| Configuração de família herdada | `config/ministerios_publicos.json` |
| Skills que usa hoje | `motores/por_motor/mpgo-destinacao`, `motores/justica_mp`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 1: `f260-captacao-196` MPGO - TAC com destinação social |
| Aprendizado herdado | 123 leituras, 57 com resultado (46%); bloqueios em mpt.mp.br (1), www.gov.br (223), www.mpgo.mp.br (101); rotas que o afinador provou: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao; https://www.mpf.mp.br/o-mpf/unidades/pr-pb/noticias/mpf-lanca-chamamento-publico-para-cadastro-de-entidades-aptas-a-receber-bens-e-valores-de-processos-judiciais-e-extrajudiciais-na-pb; https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao; https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-divulga-lista-de-instituicoes-selecionadas-para-receber-bens-doados; https://www.mpf.mp.br/o-mpf/unidades/pr-se/destinacao-de-bens-e-valores/edital-prse-1-2025-chamamento-publico-destinacao-de-bens-e-valores-assinado.pdf/view; https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores; https://www.mpf.mp.br/atuacao/ccr4/normas/copy_of_portarias/portarias-2024/Portaria10972024PGRMPF.pdf/view; https://www.mpf.mp.br/o-mpf/unidades/pr-se/destinacao-de-bens-e-valores/portaria-prse-145-2025-autoriza-chamamento-publico-destinacao-de-bens-e-valores-assinada.pdf/view |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, verde 16, vermelho 4. Luz em 21 dias (01/10 a 22/10): 16 verdes, 0 amarelos, 4 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4). Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (49 leituras). Outubro: executou 16 de 22 dias esperados (cobertura 73%), 16 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-18; 1 achado(s) acumulado(s); 1 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 3 domínio(s) com bloqueio: começar pelo degrau aprendido; 1 alvos vigiados só na janela prevista |

#### `MT-19` · MPT-GO — editais de 5 dias para indicação de destinação de recursos ou bens (PRT 18ª Região)

`mptgo-destinacao` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/mptgo-destinacao.toml`

**Finalidade:** editais de 5 dias do MPT-GO (todo dia) e habilitação da A.M.C.

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | MPT-GO — PRT 18ª Região (Goiânia e PTM Anápolis): https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens; MPT-GO — PRT 18ª Região: https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais; MPT-GO — PRT 18ª Região (Goiânia/GO): https://www.prt18.mpt.mp.br/informe-se/noticias-do-mpt-go; MPT nacional — PGT - Noticias: https://mpt.mp.br/search_rss?SearchableText=edital+cadastramento+entidades&sort_on=Date&sort_order=reverse; MPT nacional — PGT - Noticias: https://mpt.mp.br/pgt/noticias/RSS; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao; MPF — nacional (busca): https://www.mpf.mp.br/search?SearchableText=edital+chamamento+recebimento+bens+valores; MPF — PR-BA (modelo): https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores; MPF — nacional: https://www.mpf.mp.br/servicos/mpf-servicos |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:53,16:23 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (justica_mp): o expediente forense publica de manhã e no fim da tarde; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/ministerios_publicos.json` |
| Skills que usa hoje | `motores/por_motor/mptgo-destinacao`, `motores/justica_mp`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 76 leituras, 58 com resultado (76%); bloqueios em mpt.mp.br (1), www.gov.br (223) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, verde 16, vermelho 4. Luz em 21 dias (01/10 a 22/10): 16 verdes, 0 amarelos, 4 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4). Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (50 leituras). Outubro: executou 16 de 22 dias esperados (cobertura 73%), 16 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-18; 1 achado(s) acumulado(s); 1 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 14 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 2 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-20` · MPU — MPF, MPDFT, MPM e MPT nacional: destinação de bens e valores (com CNMP e FDD)

`mpu-destinacao` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/mpu-destinacao.toml`

**Finalidade:** MPF PR-GO, MPDFT, MPM, MPT nacional, FDD e CNMP (pela cadência de cada fonte)

**Atende à finalidade da titular:** achar editais de destinação de penas e de recursos de acordos.

| Campo | Esboço |
| --- | --- |
| Canal | diário ou documento |
| Fontes de busca | MPT-GO — PRT 18ª Região (Goiânia e PTM Anápolis): https://www.prt18.mpt.mp.br/servicos/editais-de-destinacao-de-recursos-bens; MPT-GO — PRT 18ª Região: https://www.prt18.mpt.mp.br/servicos/entidades-assistenciais; MPT-GO — PRT 18ª Região (Goiânia/GO): https://www.prt18.mpt.mp.br/informe-se/noticias-do-mpt-go; MPT nacional — PGT - Noticias: https://mpt.mp.br/search_rss?SearchableText=edital+cadastramento+entidades&sort_on=Date&sort_order=reverse; MPT nacional — PGT - Noticias: https://mpt.mp.br/pgt/noticias/RSS; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia; MPF — PR-GO: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao; MPF — nacional (busca): https://www.mpf.mp.br/search?SearchableText=edital+chamamento+recebimento+bens+valores; MPF — PR-BA (modelo): https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores; MPF — nacional: https://www.mpf.mp.br/servicos/mpf-servicos |
| Agenda atual (a migrar para a configuração) | horarios brt: 16:23 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (justica_mp): o expediente forense publica de manhã e no fim da tarde; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/ministerios_publicos.json` |
| Skills que usa hoje | `motores/por_motor/mpu-destinacao`, `motores/justica_mp`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py, leitura/documento.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-mp-destinacoes-reparacao` (0/20 leituras com resultado) |
| Alvos vigiados | 2: `f260-captacao-169` FDD/Pronasci - cultura e cidadania em territórios vulneráveis; `f260-captacao-208` Cessão de bens móveis apreendidos |
| Aprendizado herdado | 124 leituras, 7 com resultado (6%); bloqueios em mpt.mp.br (1), www.gov.br (223); rotas que o afinador provou: https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-em-goias-cadastra-entidades-e-orgaos-publicos-para-recebimento-bens-e-valores-decorrentes-da-atuacao-da-instituicao; https://www.mpf.mp.br/o-mpf/unidades/pr-pb/noticias/mpf-lanca-chamamento-publico-para-cadastro-de-entidades-aptas-a-receber-bens-e-valores-de-processos-judiciais-e-extrajudiciais-na-pb; https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/bens-para-doacao; https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias/mpf-divulga-lista-de-instituicoes-selecionadas-para-receber-bens-doados; https://www.mpf.mp.br/o-mpf/unidades/pr-ba/destinacao-de-bens-e-valores; https://www.mpf.mp.br/atuacao/ccr4/normas/copy_of_portarias/portarias-2024/Portaria10972024PGRMPF.pdf/view; https://www.mpf.mp.br/o-mpf/unidades/pr-go/noticias; https://www.mpdft.mp.br/portal/index.php/comunicacao-menu/sala-de-imprensa/noticias/noticias-2026/17805-medidas-alternativas-mpdft-apresenta-resultados-e-iniciativas-dos-ultimos-dois-anos |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, verde 16, vermelho 4. Luz em 21 dias (01/10 a 22/10): 16 verdes, 0 amarelos, 4 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4). Acerto das rotas melhorou: 0% na primeira metade do período e 25% na segunda (49 leituras). Outubro: executou 16 de 22 dias esperados (cobertura 73%), 0 dias com achado, 0 falhas; veredito: lacunas. Auditoria: LENDO SEM ACHAR — leu em 2026-10-18; nunca reconheceu edital; 0 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 4 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 2 domínio(s) com bloqueio: começar pelo degrau aprendido; 2 alvos vigiados só na janela prevista |


### Legislativo

#### `MT-21` · Câmara Municipal de Goiânia — processos legislativos, utilidade pública e chamamentos

`camara-goiania-pl` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/camara-goiania-pl.toml`

**Finalidade:** seguir a utilidade pública da própria associação e achar leis de fomento, parceria, isenção e emendas impositivas para entidades, e os chamamentos da Câmara

**Atende à finalidade da titular:** acompanhar proposições e emendas que criam recursos.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | SUAP da Câmara — consulta pública de processos legislativos (por assunto): https://suap.camaragyn.go.gov.br/camara/consulta_publica/; Portal da Câmara (Plone) — busca de notícias em RSS: https://www.goiania.go.leg.br/search_rss |
| Agenda atual (a migrar para a configuração) | horarios brt: 12:53,20:23 · dias: todos · cadencia dias: 1 · por que esta hora: 03/10 (teste do motor 04): o portal da Câmara responde da nuvem (medido) e libera robôs; as pautas saem no dia da sessão — 12:53 pega a pauta do dia e 20:23 fecha o expediente; o SUAP não é lido (robots.txt proíbe) · coleta: nuvem |
| Configuração de família herdada | `config/camara_goiania.json`, `config/emendas.json` |
| Skills que usa hoje | `motores/por_motor/camara-goiania-pl`, `motores/orgao_publico`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 4: `f260-captacao-069` Emenda municipal para projeto educativo em Goiânia; `f260-captacao-107` Emenda municipal para entidade assistencial; `f260-captacao-113` Projeto de apoio a famílias de baixa renda; `f260-captacao-152` Emenda municipal para saúde preventiva |
| Aprendizado herdado | 210 leituras, 60 com resultado (29%); bloqueios em www.goiania.go.leg.br (68), www.goiania.go.gov.br (58), saude.goiania.go.gov.br (4); rotas que o afinador provou: https://www.goiania.go.gov.br/secult/leipaulogustavo/; https://www.goiania.go.gov.br/secult/pnab-2024/; https://www.goiania.go.gov.br/; https://www.goiania.go.leg.br/sala-de-imprensa/agencia-camara-goiania/Agencia-Camara-Goiania_noticias/comeca-a-tramitar-a-lei-orcamentaria-anual-para-2027; https://saude.goiania.go.gov.br/editas-de-chamamento-publico; https://saude.goiania.go.gov.br/editas-de-chamamento-publico/aviso-de-chamamento-publico-3; https://saude.goiania.go.gov.br/editas-de-chamamento-publico/edital-de-chamamento-publico-no-001-2026/; https://saude.goiania.go.gov.br/editas-de-chamamento-publico/edital-de-chamamento-publico-no-001-2026 |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 2, verde 19, vermelho 1. Luz em 22 dias (01/10 a 22/10): 19 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-19 a 2026-10-19). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (1). Acerto das rotas piorou: 78% na primeira metade do período e 45% na segunda (62 leituras). Outubro: executou 19 de 22 dias esperados (cobertura 86%), 0 dias com achado, 0 falhas; veredito: lacunas. Auditoria: LENDO SEM ACHAR — leu em 2026-10-22; nunca reconheceu edital; 0 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 5 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 3 domínio(s) com bloqueio: começar pelo degrau aprendido; 4 alvos vigiados só na janela prevista |

#### `MT-22` · Assembleia Legislativa de Goiás — proposições

`alego-pl` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/alego-pl.toml`

**Finalidade:** alimentar o sistema com emenda parlamentar, a partir de insumo de EMENDA — proposições e emendas impositivas estaduais (janela out-nov); achados são projetos de lei, não editais

**Atende à finalidade da titular:** acompanhar proposições e emendas que criam recursos.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | SPL da ALEGO — índice cronológico das proposições: https://alegodigital.al.go.leg.br/spl/consulta-cronologico.aspx; SPL da ALEGO — consulta por tipo (projeto de lei, emenda, PLOA): https://alegodigital.al.go.leg.br/spl/consulta-tipo.aspx; SPL da ALEGO — sessões, pauta prévia e ordem do dia: https://alegodigital.al.go.leg.br/spl/sessoes.aspx; Proposições da ALEGO: https://portal.al.go.leg.br/; LOA e emendas impositivas — SEFAZ/SEGPLAN: https://www.economia.go.gov.br/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 10:53,20:53 · dias: seg,ter,qua,qui,sex · cadencia dias: 1 · por que esta hora: itinerário 02/10 (legislativo): as sessões e as pautas publicam no fim do dia; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem + local |
| Configuração de família herdada | `config/emendas.json` |
| Skills que usa hoje | `motores/por_motor/alego-pl`, `motores/orgao_publico`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 2: `f260-captacao-068` Emenda estadual para projeto educativo em Goiás; `f260-captacao-151` Emenda estadual para saúde comunitária |
| Aprendizado herdado | 226 leituras, 9 com resultado (4%); bloqueios em portal.al.go.leg.br (138), goias.gov.br (97); rotas que o afinador provou: https://portal.al.go.leg.br/deputados; https://portal.al.go.leg.br/; https://goias.gov.br/cultura/secult-goias-prorroga-inscricoes-para-os-editais-da-politica-nacional-aldir-blanc/; https://goias.gov.br/cultura/governo-de-goias-abre-inscricoes-para-o-programa-goyazes-2025-com-novas-regras/; https://goias.gov.br/cultura/programa-goyazes-abre-inscricoes-nesta-terca-feira-02-04/; https://goias.gov.br/cultura/secult-goias-prorroga-inscricoes-da-lei-paulo-gustavo/; https://goias.gov.br/esporte/governo-de-goias-prorroga-inscricoes-para-a-4a-edicao-da-copa-quilombola/; https://goias.gov.br/cultura/secult-goias-lanca-dois-novos-editais-da-pnab-destinados-a-pontos-e-pontoes-de-cultura/ |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 2, verde 19, vermelho 1. Luz em 22 dias (01/10 a 22/10): 19 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-11 a 2026-10-11). Tipos de problema nos dias amarelos ou vermelhos: erro de código (1). Acerto das rotas ficou estável: 0% na primeira metade do período e 0% na segunda (50 leituras). Outubro: executou 19 de 22 dias esperados (cobertura 86%), 0 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-22; 3 achado(s) acumulado(s); 3 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 15 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 2 domínio(s) com bloqueio: começar pelo degrau aprendido; 2 alvos vigiados só na janela prevista |

#### `MT-23` · Congresso Nacional — Câmara, Senado e Comissão Mista de Orçamento (emendas, regras e chamamentos)

`congresso-nacional` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/congresso-nacional.toml`

**Finalidade:** ler o prazo oficial das emendas ao orçamento da União e as regras e recursos para entidades que tramitam no Congresso

**Atende à finalidade da titular:** acompanhar proposições e emendas que criam recursos.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · diário ou documento |
| Fontes de busca | CMO — LOA do ano seguinte (etapa 'Apresentação de emendas'): https://www.congressonacional.leg.br/web/orcamento/acompanhe/orcamento-anual/-/loa/2027; CMO — comunicados: https://www.congressonacional.leg.br/web/cmo/comunicados; Câmara — API de proposições: https://dadosabertos.camara.leg.br/api/v2/proposicoes; Senado — API /processo: https://legis.senado.leg.br/dadosabertos/processo; Câmara — notícias (RSS): https://www.camara.leg.br/noticias/rss/ultimas-noticias; Senado — notícias (RSS): https://www12.senado.leg.br/noticias/feed/todasnoticias/rss; Senado — convocações públicas: https://www6g.senado.leg.br/transparencia/licitacoes-e-contratos/sadcon/convocacoes-publicas |
| Agenda atual (a migrar para a configuração) | horarios brt: 10:53,20:53 · dias: todos · cadencia dias: 1 · por que esta hora: itinerário 02/10 (legislativo): as sessões e as pautas publicam no fim do dia; a 1ª passagem fecha o dia anterior (D-1) · coleta: nuvem |
| Configuração de família herdada | `config/congresso_nacional.json`, `config/emendas.json` |
| Skills que usa hoje | `motores/por_motor/congresso-nacional`, `motores/orgao_publico`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py, leitura/pdf.py, leitura/ocr.py, leitura/expurgo.py, leitura/compactado.py |
| Descoberta | descoberta/dados_abertos.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | 1: `f260-captacao-200` Emenda parlamentar federal individual |
| Aprendizado herdado | 102 leituras, 69 com resultado (68%); rotas que o afinador provou: https://www.camara.leg.br/; https://www12.senado.leg.br/; https://www12.senado.leg.br/noticias |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 20, vermelho 1. Luz em 21 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-19 a 2026-10-19). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (1). Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (57 leituras). Outubro: executou 20 de 22 dias esperados (cobertura 91%), 0 dias com achado, 0 falhas; veredito: lacunas. Auditoria: LENDO SEM ACHAR — leu em 2026-10-22; nunca reconheceu edital; 0 achados no total. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 12 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 1 alvos vigiados só na janela prevista |


### Portais e fontes do terceiro setor

#### `MT-24` · GIFE — Grupo de Institutos, Fundações e Empresas

`gife` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/gife.toml`

**Finalidade:** encontrar os editais ABERTOS para OSC que o GIFE seleciona todo mês e que a Capta publica com prazo e link oficial (finalidade herdada do motor agregado plat-gife)

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | GIFE — API de posts: categoria Editais (seleção mensal) + busca de notícias de edital: https://gife.org.br/wp-json/wp/v2/posts; Capta — API de posts: categoria Oportunidades (Região, Inscrições até, link do edital): https://capta.org.br/wp-json/wp/v2/posts |
| Agenda atual (a migrar para a configuração) | cadência de 7 dia(s) |
| Configuração de família herdada | `config/gife_editais.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-gife` (58/102 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 102 leituras, 58 com resultado (57%); bloqueios em gife.org.br (26) |
| Histórico de erros (01/10 a 22/10) | Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (54 leituras). Outubro: executou 19 de 22 dias esperados (cobertura 86%), 19 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-21; 5 achado(s) acumulado(s); 5 achados no total. Qualidade do que entrega: 1 oportunidades abertas, 9.0 itens por oportunidade, 0% completas. Achados: 1 em 1 dias, do primeiro em 2026-07-30 ao último em 2026-07-30. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (7 dias) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 14 dias, ou bloqueio > 30% |
| Indicador · linhas | 9 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório; 1 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-25` · Adaptador Mapas Culturais — oportunidades com inscrição aberta

`plataforma-mapas-culturais` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/plataforma-mapas-culturais.toml`

**Finalidade:** ampliar o alcance: fontes que nenhum motor vigiava

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · portal: entrega pistas |
| Fontes de busca | API padrão do Mapas Culturais (/api/opportunity/find), rodízio: https://mapa.cultura.gov.br/api/opportunity/find?@select=id,name,registrationTo; Listagem pública de oportunidades do mapa: https://mapa.cultura.gov.br/oportunidades/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 11:23 · dias: todos · cadencia dias: 1 · por que esta hora: conselho dos motores (10/10/2026): sites oficiais publicam no expediente · coleta: nuvem |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/dados_abertos.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 20 leituras, 20 com resultado (100%); bloqueios em culteditais.cultura.gov.br (7) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, verde 4, vermelho 4. Luz em 9 dias (01/10 a 22/10): 4 verdes, 0 amarelos, 4 vermelhos; maior sequência vermelha: 4 dias (2026-10-19 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (4). Acerto das rotas ficou estável: 100% na primeira metade do período e 100% na segunda (19 leituras). Outubro: executou 4 de 22 dias esperados (cobertura 18%), 0 dias com achado, 4 falhas; veredito: lacunas. Auditoria: BLOQUEADO — todas as páginas falharam em 2026-10-18; 68 achados no total. Alerta atual (alta): 4 dia(s) sem leitura (cadência 1); ação indicada: conferir escala e limite por execução. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 10 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório; 1 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-26` · Farol Cultural — editais de cultura de todo o Brasil, pela API pública do portal

`site-farol-cultural` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-farol-cultural.toml`

**Finalidade:** editais de cultura de todo o Brasil, pela API pública do portal

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · portal: entrega pistas |
| Fontes de busca | Farol Cultural: https://farolcultural.art/api/v1/editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-farol-cultural`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/dados_abertos.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-27` · CapitaAI — editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas

`site-capitaai` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-capitaai.toml`

**Finalidade:** editais e oportunidades de captação, incluindo a lista pública dos editais do Prosas

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | CapitaAI: https://capitaai.com.br/sitemap-captacao.xml |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-capitaai`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-28` · Observatório do Terceiro Setor — editais publicados na seção temática do portal

`site-observatorio-terceiro-setor` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-observatorio-terceiro-setor.toml`

**Finalidade:** editais publicados na seção temática do portal

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | Observatório do Terceiro Setor: https://www.observatorio3setor.org.br/secoes_tematicas/editais/feed/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-observatorio-terceiro-setor`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-observatorio-3setor` (0/26 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 26 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-29` · Mapas Culturais — editais das redes estaduais e municipais de cultura que usam a plataforma

`site-mapas-culturais` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-mapas-culturais.toml`

**Finalidade:** editais das redes estaduais e municipais de cultura que usam a plataforma

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | API oficial · portal: entrega pistas |
| Fontes de busca | Mapas Culturais:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-mapas-culturais`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/api.py, acesso/leve.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/dados_abertos.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-30` · ABCR — Associação Brasileira de Captadores de Recursos — editais divulgados pela associação dos captadores

`site-abcr` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-abcr.toml`

**Finalidade:** editais divulgados pela associação dos captadores

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | ABCR — Associação Brasileira de Captadores de Recursos: https://captadores.org.br/category/editais/feed/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-abcr`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-abcr` (0/26 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 26 leituras, 0 com resultado (0%); bloqueios em captadores.org.br (12) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 9 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório; 1 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-31` · Rede Comuá — editais dos fundos independentes de filantropia

`site-rede-comua` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-rede-comua.toml`

**Finalidade:** editais dos fundos independentes de filantropia

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | Rede Comuá: https://redecomua.org.br/wp-json/wp/v2/_editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-rede-comua`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-32` · Fundo Baobá — editais para equidade racial

`site-fundo-baoba` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-fundo-baoba.toml`

**Finalidade:** editais para equidade racial

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | Fundo Baobá:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13,19:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-fundo-baoba`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-33` · IDIS — Instituto para o Desenvolvimento do Investimento Social — chamadas e editais de investimento social

`site-idis` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-idis.toml`

**Finalidade:** chamadas e editais de investimento social

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | IDIS — Instituto para o Desenvolvimento do Investimento Social: https://www.idis.org.br/feed/ |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-idis`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-34` · Fundo Casa Socioambiental — chamadas socioambientais

`site-fundo-casa` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-fundo-casa.toml`

**Finalidade:** chamadas socioambientais

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | Fundo Casa Socioambiental: https://casa.org.br/wp-json/wp/v2/chamadas |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-fundo-casa`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-35` · CESE — Coordenadoria Ecumênica de Serviço — editais de apoio a projetos populares

`site-cese` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-cese.toml`

**Finalidade:** editais de apoio a projetos populares

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | CESE — Coordenadoria Ecumênica de Serviço: https://cese.org.br/wp-json/wp/v2/edital |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-cese`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 20, cinza 1. Luz em 21 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-36` · Rede Filantropia — editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro)

`site-rede-filantropia` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-rede-filantropia.toml`

**Finalidade:** editais divulgados pela rede (lida pelo computador do titular: recusa IP estrangeiro)

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | Rede Filantropia:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:10,09:10,12:10,15:10,18:10,21:10 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-rede-filantropia`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-rede-filantropia` (0/4 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 4 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 1, vermelho 1, verde 19. Luz em 21 dias (01/10 a 22/10): 19 verdes, 0 amarelos, 1 vermelhos; maior sequência vermelha: 1 dias (2026-10-03 a 2026-10-03). Tipos de problema nos dias amarelos ou vermelhos: erro de código (1). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 2 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-37` · Editais Culturais — editais de cultura reunidos no portal

`site-editais-culturais` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-editais-culturais.toml`

**Finalidade:** editais de cultura reunidos no portal

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | Editais Culturais:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13,19:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-editais-culturais`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 20, cinza 1. Luz em 21 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-38` · Mapa das OSC (Ipea) — editais reunidos no portal

`site-mapa-osc` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-mapa-osc.toml`

**Finalidade:** editais reunidos no portal do Ipea (coleta assistida: o site proíbe robôs)

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | Mapa das OSC (Ipea): https://mapaosc.ipea.gov.br/editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-mapa-osc`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-mapa-osc` (0/8 leituras com resultado) |
| Alvos vigiados | 1: `f260-captacao-216` Mapa das OSC - área de editais |
| Aprendizado herdado | 40 leituras, 6 com resultado (15%); bloqueios em mapaosc.ipea.gov.br (3) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 8, verde 13. Luz em 21 dias (01/10 a 22/10): 13 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 10 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 3 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório; 1 domínio(s) com bloqueio: começar pelo degrau aprendido; 1 alvos vigiados só na janela prevista |

#### `MT-39` · Prosas — editais e prêmios para OSCs (três caminhos indiretos: listagem da CapitaAI, ângulo do Piloto e coleta assistida)

`site-prosas` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-prosas.toml`

**Finalidade:** editais e prêmios para OSCs; o robots.txt proíbe robôs, então só pelos três caminhos indiretos decididos pelo titular

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | Prosas: https://prosas.com.br/selecao/widgets/listagem-editais |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-prosas`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 3: `plat-prosas` (0/19 leituras com resultado); `plat-prosas-oscs` (0/0 leituras com resultado); `plat-prosas-premios` (0/26 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 45 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 8, verde 13. Luz em 21 dias (01/10 a 22/10): 13 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 4 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório |

#### `MT-40` · Fundo Brasil de Direitos Humanos — editais de direitos humanos

`site-fundo-brasil` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-fundo-brasil.toml`

**Finalidade:** editais de direitos humanos

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | Fundo Brasil de Direitos Humanos: https://www.fundobrasil.org.br/wp-json/wp/v2/edital |
| Agenda atual (a migrar para a configuração) | horarios brt: 06:13,09:13,12:13,15:13,18:13,21:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-fundo-brasil`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 21. Luz em 21 dias (01/10 a 22/10): 21 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-41` · UNDEF — Fundo das Nações Unidas para a Democracia — chamadas anuais para a sociedade civil

`site-undef` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-undef.toml`

**Finalidade:** chamadas anuais para a sociedade civil

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | UNDEF — Fundo das Nações Unidas para a Democracia:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13,19:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-undef`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 12, cinza 6, vermelho 3. Luz em 21 dias (01/10 a 22/10): 12 verdes, 0 amarelos, 3 vermelhos; maior sequência vermelha: 3 dias (2026-10-10 a 2026-10-12). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (3). |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-42` · BrazilFoundation — editais de apoio a organizações brasileiras

`site-brazilfoundation` · mantido · na Bússola · arquivo: `eldorado/motores/canal/config/site-brazilfoundation.toml`

**Finalidade:** editais de apoio a organizações brasileiras

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | BrazilFoundation:  |
| Agenda atual (a migrar para a configuração) | horarios brt: 07:13,19:13 · dias: todos · cadencia dias: 1 · por que esta hora: motor por site (desmonte dos indexadores, 02/10): lido pelo fluxo 16 a partir da última leitura, sem lacuna · coleta: fluxo 16 (indexadores) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/site-brazilfoundation`, `motores/terceiro_setor`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 20, cinza 1. Luz em 21 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 1 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | sem cuidado especial registrado |

#### `MT-43` · Outros agregadores e motores de busca

`outros-agregadores` · novo (pedido) · arquivo: `eldorado/motores/canal/config/outros-agregadores.toml`

**Finalidade:** pedido pela titular: reúne agregadores e buscas que não têm motor próprio

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial (motor novo: pedido pela titular: reúne agregadores e buscas que não têm motor próprio).

| Campo | Esboço |
| --- | --- |
| Canal | portal: entrega pistas |
| Fontes de busca | site oficial 1: https://www.boavista.rr.gov.br/; site oficial 2: https://conexoes.bndes.gov.br/chamadas-e-editais; site oficial 3: https://www.institutococacolabrasil.com.br/; site oficial 4: https://chamamentos.itapevi.sp.gov.br/chamamentos; site oficial 5: https://www.maranguape.ce.gov.br/informa/328/edital-de-fomento-n-004-2026-espa-os-culturais; site oficial 6: https://www.institutoacp.org.br/chamadaaberta; site oficial 1: https://www.cnbb.org.br/cnbb-lanca-edital-do-fns-para-apoio-financeiro-a-projetos-relativos-a-campanha-da-fraternidade-2026; site oficial 2: https://institutogenesio.org.br/wp-content/uploads/2026/10/Edital-Nao-Incentivado-Instituto-Genesio-A-Mendes-2026.pdf?utm_source=Link+da+Bio+do+RD+Station&utm_medium=social&utm_campaign=CTA+no+Link+da+Bio; site oficial 3: https://fns.cnbb.org.br/fundo/informativo/index; site oficial 4: https://fase.org.br/pt/acervo/documentos/edital-agitando-pensamentos-2026-roteiro/; site oficial 5: http://www.editalcorredor2025.com.br; site oficial 6: https://banrisulcultural.com.br/editais/ |
| Agenda atual (a migrar para a configuração) | cadência de 7 dia(s) |
| Configuração de família herdada | `config/indexadores.json`, `config/capilaridade.json`, `config/redes_indireta.json`, `config/sites_terceiro_setor.json` |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py, descoberta/metabusca.py, descoberta/arquivos_web.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 9: `outras-oportunidades-1` (38/44 leituras com resultado); `outras-oportunidades-2` (35/38 leituras com resultado); `outras-oportunidades-3` (26/36 leituras com resultado); `outras-oportunidades-4` (22/22 leituras com resultado); `outras-oportunidades-5` (28/35 leituras com resultado); `outras-oportunidades-6` (20/32 leituras com resultado); `outras-oportunidades-7` (22/22 leituras com resultado); `outras-oportunidades-8` (11/18 leituras com resultado); `plat-captamos` (0/4 leituras com resultado) |
| Alvos vigiados | 3: `f260-captacao-217` Bússola Social - Bússola Editais; `f260-captacao-218` Capta - oportunidades e editais; `f260-curadoria-008` Instituto Impactarte — cadastro de proponente em fluxo contínuo |
| Aprendizado herdado | 381 leituras, 208 com resultado (55%); bloqueios em culteditais.cultura.gov.br (7), www.administracao.go.gov.br (1), www.boavista.rr.gov.br (14), www.institutoacp.org.br (7), www.institutococacolabrasil.com.br (84); rotas que o afinador provou: https://www.diariomunicipal.com.br/maceio/; https://comitedeculturasc.org/editais; https://www.diariomunicipal.com.br/feed; https://www.diariomunicipal.com.br/sitemap.xml; https://www.diariomunicipal.com.br/editais; https://www.diariomunicipal.com.br/edital; https://www.diariomunicipal.com.br/noticias; https://www.diariomunicipal.com.br/chamadas-publicas |
| Histórico de erros (01/10 a 22/10) | Acerto das rotas melhorou: 80% na primeira metade do período e 100% na segunda (41 leituras). Outubro: executou 6 de 22 dias esperados (cobertura 27%), 6 dias com achado, 0 falhas; veredito: lacunas. Auditoria: FUNCIONANDO — leu em 2026-10-22; 189 achado(s) acumulado(s); 189 achados no total. Achados: 6 em 2 dias, do primeiro em 2026-10-17 ao último em 2026-10-18. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (7 dias) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 14 dias, ou bloqueio > 30% |
| Indicador · linhas | 12 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 13 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | entrega pistas: a fonte oficial é confirmada no Cartório; 30 domínio(s) com bloqueio: começar pelo degrau aprendido; 3 alvos vigiados só na janela prevista |

#### `MT-44` · Fundações e institutos (sites próprios)

`novo-fundacoes-institutos` · sugestão · arquivo: `eldorado/motores/canal/config/novo-fundacoes-institutos.toml`

**Finalidade:** sugestão: as fundações e institutos que não estão na lista (Itaú, Bradesco, Vale, Boticário, Sabin, Telefônica, Tide Setubal, iCS e outras) ganham um motor de sites próprios

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial (motor novo: sugestão: as fundações e institutos que não estão na lista (Itaú, Bradesco, Vale, Boticário, Sabin, Telefônica, Tide Setubal, iCS e outras) ganham um motor de sites próprios).

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | — |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py, descoberta/metabusca.py, descoberta/arquivos_web.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 2: `site-fundacao-banco-do-brasil` (0/0 leituras com resultado); `site-itau-social` (0/0 leituras com resultado) |
| Alvos vigiados | 24: `f260-captacao-221` Fundação Banco do Brasil; `f260-captacao-222` Fundação Itaú; `f260-captacao-223` Fundação Bradesco; `f260-captacao-224` Fundação Telefônica Vivo; `f260-captacao-225` Instituto Claro; `f260-captacao-226` Instituto Natura; `f260-captacao-227` Instituto Coca-Cola Brasil; `f260-captacao-228` Instituto Localiza; `f260-captacao-229` Instituto Votorantim; `f260-captacao-230` Fundação ArcelorMittal; `f260-captacao-231` Fundação Vale; `f260-captacao-232` Instituto Neoenergia; `f260-captacao-233` Instituto Sicoob; `f260-captacao-234` Instituto Unibanco … |
| Aprendizado herdado | 825 leituras, 49 com resultado (6%); bloqueios em fundacao.bradesco (2), fundacaotelefonicavivo.org.br (130), www.institutonatura.org (120), www.institutococacolabrasil.com.br (84), institutolocaliza.com.br (37); rotas que o afinador provou: https://www.fbb.org.br/feed; https://www.fbb.org.br/; https://www.fbb.org.br/noticias; https://www.institutoclaro.org.br/feed; https://www.institutoclaro.org.br/; https://www.fundacaovale.org/materiais/cursos; https://www.fundacaovale.org/; https://www.fundacaovale.org/feed |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 2. Luz em 1 dias (01/10 a 22/10): 0 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 12 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 27 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 17 domínio(s) com bloqueio: começar pelo degrau aprendido; 24 alvos vigiados só na janela prevista |

#### `MT-45` · Organismos e fundações internacionais

`novo-internacional` · sugestão · arquivo: `eldorado/motores/canal/config/novo-internacional.toml`

**Finalidade:** sugestão: ONU, UNESCO, UNICEF, Banco Mundial, BID, União Europeia, Ford, Open Society e embaixadas; o UNDEF continua separado

**Atende à finalidade da titular:** ler os portais que reúnem editais e entregar pistas, confirmadas na fonte oficial (motor novo: sugestão: ONU, UNESCO, UNICEF, Banco Mundial, BID, União Europeia, Ford, Open Society e embaixadas; o UNDEF continua separado).

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | — |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py, descoberta/vigilancia.py, descoberta/metabusca.py, descoberta/arquivos_web.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 3: `site-embaixada-eua` (0/0 leituras com resultado); `site-embaixada-japao` (0/0 leituras com resultado); `site-iaf` (0/0 leituras com resultado) |
| Alvos vigiados | 21: `f260-captacao-240` UNESCO – Fundo Internacional para Diversidade Cultural; `f260-captacao-241` UNICEF – Programas de parceria com OSC; `f260-captacao-242` PNUD – Small Grants Programme; `f260-captacao-243` Banco Mundial – Social Development Grants; `f260-captacao-244` BID – Laboratório de Inovação; `f260-captacao-245` USAID – Grants Globais; `f260-captacao-246` União Europeia – Erasmus+; `f260-captacao-247` União Europeia – EuropeAid; `f260-captacao-248` Open Society Foundations; `f260-captacao-249` Ford Foundation; `f260-captacao-250` Gates Foundation; `f260-captacao-251` Google.org; `f260-captacao-252` Meta Community Grants; `f260-captacao-253` Microsoft Philanthropies … |
| Aprendizado herdado | 297 leituras, 6 com resultado (2%); bloqueios em www.unesco.org (49), www.undp.org (34), www.facebook.com (5), www.globalfundforwomen.org (4), sgp.undp.org (4); rotas que o afinador provou: https://www.unicef.org/sitemap.xml; https://www.iadb.org/sitemap.xml; https://international-partnerships.ec.europa.eu/sitemap.xml; https://www.gatesfoundation.org/sitemap.xml; https://skoll.org/feed; https://oakfnd.org/sitemap.xml |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): cinza 2, verde 1. Luz em 1 dias (01/10 a 22/10): 0 verdes, 0 amarelos, 0 vermelhos. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 12 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | rodar sobre as páginas gravadas de 25 fonte(s) e alvo(s), com resultado igual ou melhor que os motores de origem; depois, 14 dias em paralelo |
| Cuidados | 5 domínio(s) com bloqueio: começar pelo degrau aprendido; 21 alvos vigiados só na janela prevista |


### Pilotos — motores livres com IA

#### `MT-46` · Piloto - Espião — busca aberta no terceiro setor

`piloto-aberto` · mantido · na Bússola · arquivo: `eldorado/motores/pilotos/espiao.py`

**Finalidade:** encontrar oportunidade aberta para OSC em Procura o que os outros 28 motores NÃO alcançam: empresas, fundações, institutos, plataformas e programas que ninguém catalogou ainda. Não tem rota fixa — tem léxico, territórios e um rodízio de ângulos de ataque. Toda descoberta precisa apontar, no mínimo, o SITE OFICIAL da oportunidade.

**Atende à finalidade da titular:** motor livre que alimenta a Biblioteca.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | busca aberta por ângulo sorteado (sem rota fixa): https://html.duckduckgo.com/html/?q=; site oficial do financiador descoberto (derivado): ; plataformas ainda não catalogadas: https://html.duckduckgo.com/html/?q=plataforma+editais+terceiro+setor+brasil |
| Agenda atual (a migrar para a configuração) | horarios brt: contínuo · dias: com o Piloto · cadencia dias: 0 · por que esta hora: é a missão 2 do Piloto: voa na corrente de voos, não na agenda · coleta: nuvem |
| Configuração de família herdada | — |
| Skills que usa hoje | — |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py, acesso/arquivo_web.py, acesso/local.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | 1: `plat-piloto-aberto` (53/98 leituras com resultado) |
| Alvos vigiados | — |
| Aprendizado herdado | 98 leituras, 53 com resultado (54%); bloqueios em html.duckduckgo.com (4) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): vermelho 2, verde 20. Luz em 22 dias (01/10 a 22/10): 20 verdes, 0 amarelos, 2 vermelhos; maior sequência vermelha: 2 dias (2026-10-01 a 2026-10-02). Tipos de problema nos dias amarelos ou vermelhos: erro de código (2). Qualidade do que entrega: 12 oportunidades abertas, 10.3 itens por oportunidade, 50% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 22 em 7 dias, do primeiro em 2026-09-28 ao último em 2026-10-17. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 9 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | um voo de teste entrega achados e uma fonte nova |
| Cuidados | 1 domínio(s) com bloqueio: começar pelo degrau aprendido |

#### `MT-47` · Piloto - Interceptador — comprova na fonte oficial

`piloto-interceptador` · mantido · na Bússola · arquivo: `eldorado/motores/pilotos/interceptador.py`

**Finalidade:** pesquisar e comprovar na fonte oficial os itens que faltam nos livros que esgotaram os motores, um livro por voo

**Atende à finalidade da titular:** motor livre que alimenta a Biblioteca.

| Campo | Esboço |
| --- | --- |
| Canal | páginas |
| Fontes de busca | os livros direcionados pela Investigação; os sites oficiais que funcionam, por órgão (aprendizado do piloto) |
| Agenda atual (a migrar para a configuração) | cadência de 1 dia(s) |
| Configuração de família herdada | — |
| Skills que usa hoje | `motores/por_motor/piloto-interceptador`, `comum/leitor_documental`, `comum/linha_producao`, `comum/plano_correcao` |
| Degraus de acesso | acesso/escada.py, acesso/leve.py, acesso/navegador.py |
| Leitores | leitura/leitores.py, leitura/normalizar.py, leitura/pagina.py |
| Descoberta | descoberta/estrutura_site.py |
| Eventos | emite `motor.execucao` e `achado.entregue`; recebe o plano (`acionamento.feito`) e o retorno (`pertinencia.decidida`) |
| Motores agregados | — |
| Alvos vigiados | — |
| Aprendizado herdado | 0 leituras, 0 com resultado (0%) |
| Histórico de erros (01/10 a 22/10) | luz somada (próprio, agregados e alvos): verde 17, vermelho 5. Luz em 22 dias (01/10 a 22/10): 17 verdes, 0 amarelos, 5 vermelhos; maior sequência vermelha: 5 dias (2026-10-18 a 2026-10-22). Tipos de problema nos dias amarelos ou vermelhos: sem leitura (5). Qualidade do que entrega: 30 oportunidades abertas, 8.2 itens por oportunidade, 47% completas, 100% válidas nos vereditos, 0% descartadas no Chrome. Achados: 18 em 11 dias, do primeiro em 2026-09-27 ao último em 2026-10-14. |
| Indicador · ponto | rodou sem erro quando acionado |
| Indicador · círculo | as 6 metas de qualidade — limiares: leu dentro da cadência (1 dia) e bloqueio < 10% / leu, mas sem achado aceito em 2 cadências, ou bloqueio de 10 a 30% / sem leitura além de 2 dias, ou bloqueio > 30% |
| Indicador · linhas | 7 ferramentas usadas, confirmadas pelas chamadas reais |
| Teste de aceite | um livro esgotado recebe itens comprovados e o resultado fica gravado |
| Cuidados | sem cuidado especial registrado |

## 7. Os contratos com a base e com o banco

**Com a base** (cumpre a seção 8.1 do esquema base): o motor expõe `descrever`, `planejar(janela, alvos)`, `buscar(contexto)`, `aprender(retorno)`, `painel` e `saude`. Recebe só o plano da Regência (janela, alvos, limites do governador) e o retorno da Pertinência. Entrega só eventos: `motor.execucao` e `achado.entregue` (o Interceptador também `certidao.gravada`, pela Investigação). Usa da base só: os contratos, os eventos, o serviço de IA e o governador.

**Com o banco:** o motor **não escreve** em nenhum banco. Os seus achados chegam à Biblioteca pelo gravador (`biblioteca.achado`); os originais vão ao Drive (só o endereço e a assinatura ficam no banco); os seus dados de uso próprio ficam nos seus arquivos (`eldorado/motores/canal/estado.py`).

## 8. O monitoramento dos motores

| Nível | O que se mede | Onde aparece |
| --- | --- | --- |
| **Ferramenta** | ponto, círculo (a métrica da ficha) e linhas | a estrela da ferramenta na Sala |
| **Motor** | ponto (rodou sem erro), círculo (as 6 metas: frescor, bloqueio, rendimento, precisão da entrega, cobertura dos alvos, prova) e linhas (as ferramentas usadas) | o painel do motor e a Bússola |
| **Categoria** | a pior saúde entre os motores e a proporção de verdes | a Bússola |
| **Parte dos motores** | o conjunto das categorias e das ferramentas | o resumo das três partes na tela inicial |

## 9. A conferência

| Teste | Resultado |
| --- | --- |
| Todas as ferramentas têm esboço completo | aprovado (29 de 29) |
| Todos os motores têm finalidade e fontes | aprovado depois da correção (7 motores tinham o aprendizado sob o identificador da duplicata agregada) |
| Toda ferramenta é usada por algum motor | aprovado; as rotas alternativas e o leitor universal são reservas acionadas pela escada e pelo registro de leitores |
| Os motores só escrevem por eventos | aprovado |
| Nenhum motor depende da lógica da base | aprovado |

## 10. Parecer do conselho

**1. Extremamente pessimista — Dra. Ingrid Valdés.** “Quarenta e cinco motores numa única peça de código: um defeito no motor genérico derruba todos os canais ao mesmo tempo. Ele precisa de isolamento por canal na execução.”

**2. Pessimista — Prof. Kenji Morimoto.** “Os motores do Judiciário têm zero resultado no histórico. Eles não podem ser ligados só porque existem: o diagnóstico vem antes.”

**3. Levemente pessimista — Eng. Rafaela Duarte.** “Os degraus pesados (navegadores) são usados por 43 motores. Sem o governador, a máquina passa de 85% no primeiro dia.”

**5. Levemente otimista — Eng. Mei Tanaka.** “Cada motor nasce com o seu histórico de erros e as rotas que já funcionaram. Ele começa onde o Eldorado0 parou, e não do zero.”

**6. Otimista — Prof. Diego Albuquerque.** “Um motor é um arquivo de configuração: adicionar uma fonte nova é escrever um arquivo, sem mudar nenhuma linha de código.”

**7. Extremamente otimista — Dra. Lucía Ferraz.** “Com 9 degraus de acesso, um canivete suíço de leitura e 5 formas de descoberta, os motores alcançam o que hoje está fora do alcance, inclusive os sites que bloqueiam.”

**Síntese do neutro — Dr. Antônio Brandt.** O esquema dos motores está aprovado como mapa de criação, com cinco parâmetros: (1) **cada motor roda isolado**: a falha de um canal não derruba os outros; (2) **ligar por ordem de rendimento**: primeiro os com API, depois os de diário, por último os de páginas; (3) **diagnóstico antes de ligar** os motores com zero resultado no histórico; (4) **o governador sempre consultado** antes dos degraus pesados; (5) **nenhum motor substitui o de origem** sem 14 dias em paralelo com resultado igual ou melhor.
