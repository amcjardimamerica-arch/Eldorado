# Contagem semanal dos Pilotos e leitura de PDF pelos motores (09/10/2026)

## Etapa 1: contagem semanal dos Pilotos

### Por que o reset de 08/10 se desfez

Cada voo leva uma cópia do diário de bordo. Ao pousar, o voo grava essa cópia por cima do que está no repositório.
O voo que decolou antes do reset de 08/10 tinha os números antigos. Ele acrescentou a sua missão e gravou tudo de volta.
A proteção que já existia no pouso ("o que o voo não mexeu não volta") não ajudou, porque o voo mexeu, sim, no diário.

### O que foi feito

- **Quem zera é o próprio Piloto, no início do voo.** O código está em `src/reset_pilotos.py`, na função `zerar_se_preciso`.
  O Espião a chama em `src/piloto.py › ciclo` e o Interceptador em `src/interceptador.py › voo`. Isso vale na nuvem, no
  computador do titular e na VM.
- **Quando o Piloto zera:**
  - toda segunda-feira à 0h, horário de Brasília (UTC−3, sem horário de verão);
  - ou a pedido do titular. O pedido fica em `estado/pilotos/zerar_contagem.json`. Pode ser feito de duas formas: pelo
    fluxo **29 · Zerar contagem dos Pilotos** no Actions ou pelo comando `python -m src.reset_pilotos --pedir`.
- **O que é zerado:**
  - missões, abates e total de abates em `estado/piloto/bordo.json` e em `estado/interceptador/bordo.json`;
  - voos por dia em `estado/piloto/voos.json`;
  - números e missões do quadro em `docs/dados/interceptador.json`. A descrição e a fila desse quadro ficam.
- **Os números antigos são guardados antes de zerar.** Ficam em
  `estado/pilotos/historico/contagem_semanal/<piloto>_<início>_ate_<data>.json.xz`, com o conteúdo completo dos arquivos
  e um resumo.
- **O carimbo viaja com os números.** Cada arquivo leva a marca da contagem a que pertence: o campo `contagem` ou, no
  voos.json, o campo `_contagem`. Um voo antigo que pousar depois leva junto o carimbo velho. O voo seguinte percebe e
  zera de novo, guardando também o que o voo tardio gravou. Assim os números não conseguem mais "ressuscitar".
- **Os quadros contam só a semana em vigor:**
  - o quadro do Interceptador conta pelos relatórios a partir do início da contagem;
  - o quadro do Espião conta pelas avaliações a partir do início da contagem.
- **O aprendizado a cada 100 buscas é contado dentro da semana.** Isso vale para a estratégia nova a cada 100 pesquisas
  e para o ciclo de parâmetros a cada 100 erros. Na virada da semana, a estratégia em uso continua e a contagem recomeça
  do zero.
- **A primeira implantação cumpre o pedido de 08/10.** O arquivo de pedido vem com `pedido_em = 2026-10-08T18:21:48Z`.
  A semana atual conta a partir daí e, na segunda 12/10 à 0h, começa a primeira semana cheia.

### Testes

O arquivo `tests/test_contagem_semanal_pilotos.py` tem 8 testes:

- virada de domingo para segunda em Brasília;
- pedido que só vale a partir da hora marcada;
- zeramento que guarda os números e não se repete na mesma semana;
- voo tardio, sem carimbo, que é zerado de novo;
- segunda-feira e pedido;
- voos por dia que preservam o carimbo;
- 100 buscas contadas dentro da semana;
- números reais de hoje copiados inteiros para o histórico, sem tocar nos arquivos de produção.

## Etapa 2: leitura de PDF pelos motores

### Resultado do executor documental (fluxo 27)

- Na fila havia 85 oportunidades de 42 motores. O robô completou 32, das quais 15 com PDF, e leu em média 3,8 dos 12
  pontos.
- 53 foram para a fila do Claude no Chrome:

  | Motivo | Quantidade |
  |---|---|
  | robots.txt proíbe | 20 |
  | documento sem os pontos legíveis | 14 |
  | conexão derrubada | 11 |
  | HTTP de erro | 6 |
  | sem endereço | 2 |

### Por que os PDFs do MP vieram sem texto

- O número "1 de 142 motores abriu PDFs; 5 sem texto" vem de `estado/esquadra.json`, no sensor
  `plat-mp-destinacoes-reparacao`. A última leitura desse sensor é de **02/10, 22h10**.
- **Não é PDF escaneado nem página de erro.** A conferência foi feita em 09/10 no navegador do titular, com IP do Brasil:
  - o link `?task=baixa&format=raw&arq=…` devolve `application/pdf` (cerca de 56 KB, 2 páginas, Ghostscript/iText);
  - as fontes são Arial com ToUnicode, ou seja, o PDF tem camada de texto;
  - o link funciona com e sem cookie.
- **A causa foi o pypdf ausente no passo dos motores em 02/10.** Isso foi corrigido em 03/10, no teste do motor 09, que
  também passou a gravar o motivo `sem_leitor_pdf`.
- **A leitura de 08/10 do motor MPT-GO já leu 6 editais**, guardados em `estado/mpt_go.json › pdf_cache`, com valor e
  prazo. Um exemplo é o edital 009591.2026: R$ 252.000,00, 5 dias, sem cadastro prévio.
- O quadro mostrava 0 PDFs lidos porque o PDF já lido fica na memória e não é contado de novo. O diagnóstico agora mostra
  também `pdfs_em_memoria`.
- O `pypdf` entrou no `requirements.txt`, para que nenhum fluxo rode sem ele.

### Leitura de PDF ligada aos motores principais

- O novo `src/leitura_pdf_motores.py` é chamado em `src/sensores.py › ler`, depois que o motor devolve as oportunidades.
  Vale para do-goiania, do-goias, dou, pncp-api e plat-prefeituras-50-go.
- **Que documento é aberto em cada oportunidade:**
  - o arquivo anexado no PNCP (`url_documento`, presente em 202 das 214 abertas);
  - o PDF da prefeitura;
  - a edição do diário;
  - os anexos citados no texto do ato. O DOU e o Diário de Goiás passaram a guardar `links_documento`.
- **Os 12 pontos são extraídos com o mesmo extrator do executor documental** (`src/executor_skills.py`). Cada ponto traz
  valor, trecho literal, documento e página.
- **O motor continua dono dos seus campos.** A leitura só preenche `valor_texto` e `prazo_texto` quando vieram vazios.
- **Formatos tratados:**
  - **ZIP do PNCP:** conferido ao vivo, 2 de 12 anexos eram ZIP. O PDF de dentro é lido, começando pelo que se chama
    "edital".
  - **Edição inteira de diário:** só as páginas do ato são lidas. O ato é localizado pelo número do edital ou pelo título.
    Se não for achado, nada é extraído, para não misturar atos.
  - **Visualizador de imagens do Diário de Goiás:** é ignorado, porque não é PDF. O texto da matéria já vem pela API.
- **Quando não há texto, o motivo fica gravado:** `resposta_nao_e_pdf`, `pdf_sem_camada_de_texto` (escaneado),
  `pdf_cortado_no_limite`, `sem_leitor_pdf`, `pdf_ilegivel` ou `zip_sem_pdf`.
- **Orçamento de cada leitura:** até 6 documentos e 150 segundos. Os limites ficam em `config/leitura_pdf_motores.json`.
  A memória por endereço dura 30 dias e fica em `estado/leitura_pdf_motores.json`.
- **Segurança:**
  - o robots.txt é respeitado;
  - conteúdo com instrução dirigida a robô vai para a quarentena e nada é extraído;
  - nada é inventado.
- **No diagnóstico de cada motor:** `leitura_pdf` (documentos, abertos, da memória, com texto, com pontos, sem texto,
  motivos), `pdfs_lidos` e `sem_texto`. A régua é a mesma do motor 12.

### Testes

O arquivo `tests/test_leitura_pdf_motores.py` tem 11 testes:

- PDF com texto;
- os 4 motivos de "sem texto";
- ZIP do PNCP;
- edição com dois atos, em que o valor do outro ato nunca é atribuído;
- quarentena;
- documentos do achado;
- anexo citado no texto;
- orçamento e memória;
- só os motores principais;
- passagem por `sensores.ler`;
- uso do extrator do executor.

## Suíte

A suíte foi rodada módulo a módulo, com teto de 400 segundos por módulo, na `main` (c78be4a9) e no ramo. **Nenhuma falha
nova.** As falhas que já existiam na `main` continuam idênticas, em 23 módulos. `test_pilotos_reset_e_dias` e `test_espiao_ao_vivo`, que estouravam o
tempo na `main`, agora passam: a contagem na janela da semana evita varrer 1,4 milhão de avaliações.

## Conselho de 7 lentes (engenharia)

| Lente | Conselheiro | Leitura |
|---|---|---|
| Extremamente pessimista | Dra. Helena Vasconcelos, ex-CTO de plataforma de pagamentos | Um relógio errado no executor zeraria fora de hora. Mitigação: o fuso é fixo (UTC−3) e o teste cobre domingo 23h59 e segunda 0h. Se o Brasil voltar a ter horário de verão, troque `BRASILIA` em `src/reset_pilotos.py`. |
| Pessimista | Prof. Otávio Rezende, sistemas distribuídos | Os dois Pilotos gravam em pastas diferentes, mas o Espião copia `docs/dados` inteiro. Mitigação: o painel do Interceptador é sempre recalculado na janela da semana, e o carimbo faz o próximo voo corrigir qualquer gravação velha. |
| Levemente pessimista | Eng. Bianca Tolentino, staff engineer de dados | Os 6 documentos por leitura levam cerca de 2 dias para cobrir as 214 abertas do PNCP. É aceitável com a memória de 30 dias. Se faltar tempo no fluxo 22, reduza `segundos_por_leitura`. |
| Neutro (decide) | Dr. Marcelo Antunes, CTO e professor | **Implantar as duas etapas.** Qualidade: zero falha nova, pontos sempre com trecho e página, e motivo explícito em todo PDF sem texto. Riscos: OCR fica fora (escaneado vai para leitura humana ou Chrome) e o voo antigo é corrigido pelo carimbo. Conferir no site após a implantação (lista abaixo). |
| Levemente otimista | Eng. Rafael Ikeda, principal engineer | O PNCP passa a trazer valor, prazo e requisitos lidos no PDF oficial, e não só o rótulo da API. |
| Otimista | Profa. Lívia Barreto, recuperação de informação | Ler só as páginas do ato na edição inteira evita o erro clássico de atribuir o valor de um contrato vizinho ao edital. |
| Extremamente otimista | Dr. André Falcão, ex-chief engineer de busca | Com o carimbo, a contagem semanal vira série histórica confiável. Semana a semana, o aprendizado mede se as estratégias melhoram. |

## Conferência no site depois da implantação

- **`dados/interceptador.json`:**
  - `contagem.desde` = `2026-10-08T18:21:48+00:00`;
  - `acumulado.missoes` na casa de 80 a 100, no lugar de 724.
- **`dados/espiao.json`:**
  - `acumulado.missoes` na casa de 500 a 600, no lugar de 1.406.199;
  - `abates` volta a contar do zero.
- **`dados/esquadrilha.json`:** `total_abates` volta a contar do zero no primeiro voo.
- **Na segunda 12/10, depois das 0h de Brasília:**
  - os números zeram de novo;
  - `estado/pilotos/historico/contagem_semanal/` ganha 2 arquivos.
- **Nos motores** (`estado/esquadra.json › sensores.pncp-api.diagnostico.leitura_pdf`): `abertos` > 0 e `com_pontos` > 0.
